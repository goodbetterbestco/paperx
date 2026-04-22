from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from pipeline.text.headings import clean_heading_title, normalize_title_key


ABSTRACT_LEAD_RE = re.compile(r"^\s*abstract\b[\s:.-]*", re.IGNORECASE)
KEYWORDS_LEAD_RE = re.compile(r"^\s*keywords?\b[\s:.-]*", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b|received\b|published\b)\b",
    re.IGNORECASE,
)
REFERENCE_START_RE = re.compile(r"^(?:\[\s*\d+\s*\]|\d+\.\s+|\(\d+\)\s+)")
REFERENCE_SIGNAL_RE = re.compile(
    r"\b(?:19|20)\d{2}\b|\bdoi\b|\bjournal\b|\bproceedings\b|\bvol\.\b|\bpp\.\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MetadataReferenceObservation:
    provider: str
    title: str
    abstract: str
    references: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MathpixExecutionDecision:
    requested: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _collapse_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def _block_attr(block: object, name: str, default: object = None) -> object:
    if hasattr(block, name):
        return getattr(block, name)
    if isinstance(block, dict):
        return block.get(name, default)
    return default


def _block_text(block: object) -> str:
    return _collapse_text(str(_block_attr(block, "text", "") or ""))


def _block_role(block: object) -> str:
    return str(_block_attr(block, "role", "") or "")


def _block_page(block: object) -> int:
    return int(_block_attr(block, "page", 0) or 0)


def _block_order(block: object) -> int:
    return int(_block_attr(block, "order", 0) or 0)


def _block_meta(block: object) -> dict[str, object]:
    meta = _block_attr(block, "meta", {})
    return dict(meta or {}) if isinstance(meta, dict) else {}


def _sorted_layout_blocks(layout: dict[str, object] | None) -> list[object]:
    return sorted(
        list((layout or {}).get("blocks", []) or []),
        key=lambda block: (_block_page(block), _block_order(block), _block_text(block)),
    )


def _looks_like_layout_metadata_line(text: str) -> bool:
    return bool(LAYOUT_METADATA_RE.search(text))


def _looks_like_title_candidate(text: str) -> bool:
    if ABSTRACT_LEAD_RE.match(text) or KEYWORDS_LEAD_RE.match(text):
        return False
    if _looks_like_layout_metadata_line(text):
        return False
    words = text.split()
    return 3 <= len(words) <= 28 and any(char.isalpha() for char in text)


def _title_from_layout_blocks(blocks: list[object]) -> str:
    page_one_blocks = [block for block in blocks if _block_page(block) == 1]
    explicit_titles = [
        _block_text(block)
        for block in page_one_blocks
        if str(_block_meta(block).get("mathpix_type", "") or "") == "title" and _block_text(block)
    ]
    if explicit_titles:
        return _collapse_text(" ".join(explicit_titles[:3]))

    page_one_candidates: list[tuple[str, str]] = []
    for block in page_one_blocks:
        text = _block_text(block)
        if not text:
            continue
        if ABSTRACT_LEAD_RE.match(text):
            break
        if _looks_like_layout_metadata_line(text):
            continue
        if _looks_like_title_candidate(text):
            page_one_candidates.append((_block_role(block), text))
        elif page_one_candidates:
            break
        if len(page_one_candidates) >= 4:
            break
    heading_candidates = [text for role, text in page_one_candidates if role == "heading"]
    if heading_candidates:
        return heading_candidates[0]
    if page_one_candidates:
        return page_one_candidates[0][1]

    front_matter_blocks = [block for block in page_one_blocks if _block_role(block) == "front_matter"]
    title_candidates: list[str] = []
    for block in front_matter_blocks:
        text = _block_text(block)
        if not text:
            continue
        if ABSTRACT_LEAD_RE.match(text):
            break
        if _looks_like_title_candidate(text):
            title_candidates.append(text)
        if len(title_candidates) >= 4:
            break
    if not title_candidates:
        return ""
    return max(title_candidates, key=lambda value: (len(value), -title_candidates.index(value)))


def _abstract_from_layout_blocks(blocks: list[object]) -> str:
    page_one_blocks = [block for block in blocks if _block_page(block) == 1]
    start_index: int | None = None
    abstract_parts: list[str] = []
    for index, block in enumerate(page_one_blocks):
        text = _block_text(block)
        if not text:
            continue
        if str(_block_meta(block).get("mathpix_type", "") or "") == "abstract" or ABSTRACT_LEAD_RE.match(text):
            start_index = index
            stripped = ABSTRACT_LEAD_RE.sub("", text).strip(" :-")
            if stripped:
                abstract_parts.append(stripped)
            break
    if start_index is None:
        return ""

    for block in page_one_blocks[start_index + 1 :]:
        text = _block_text(block)
        if not text:
            continue
        role = _block_role(block)
        if role == "heading":
            break
        if KEYWORDS_LEAD_RE.match(text):
            break
        if role not in {"front_matter", "paragraph"}:
            continue
        if _looks_like_layout_metadata_line(text) and abstract_parts:
            break
        abstract_parts.append(text)
        if len(abstract_parts) >= 4 or len(" ".join(abstract_parts).split()) >= 260:
            break
    return _collapse_text(" ".join(abstract_parts))


def _dedupe_texts(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        cleaned = _collapse_text(item)
        key = normalize_title_key(cleaned)
        if not cleaned or key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


def _references_from_layout_blocks(blocks: list[object]) -> list[str]:
    explicit_references = _dedupe_texts(
        [_block_text(block) for block in blocks if _block_role(block) == "reference" and _block_text(block)]
    )
    if explicit_references:
        return explicit_references

    references_started = False
    current_reference: str | None = None
    references: list[str] = []
    for block in blocks:
        text = _block_text(block)
        if not text:
            continue
        role = _block_role(block)
        if not references_started:
            if role == "heading" and normalize_title_key(clean_heading_title(text)) == "references":
                references_started = True
            continue
        if role == "heading":
            break
        if role not in {"paragraph", "list_item", "reference"}:
            continue
        if REFERENCE_START_RE.match(text):
            if current_reference:
                references.append(current_reference)
            current_reference = text
            continue
        if current_reference and not REFERENCE_START_RE.match(text):
            current_reference = _collapse_text(f"{current_reference} {text}")
            continue
        if REFERENCE_SIGNAL_RE.search(text):
            current_reference = text
    if current_reference:
        references.append(current_reference)
    return _dedupe_texts(references)


def _route_priority(acquisition_route: dict[str, Any] | None, field: str) -> list[str]:
    return [str(item).strip() for item in list((acquisition_route or {}).get(field) or []) if str(item).strip()]


def _primary_provider(acquisition_route: dict[str, Any] | None, field: str) -> str | None:
    plan = _route_priority(acquisition_route, field)
    return plan[0] if plan else None


def decide_mathpix_execution(
    acquisition_route: dict[str, Any] | None,
    *,
    mathpix_available: bool = True,
) -> MathpixExecutionDecision:
    if not mathpix_available:
        return MathpixExecutionDecision(
            requested=False,
            reason="mathpix_unavailable",
        )
    if _primary_provider(acquisition_route, "layout_priority") == "mathpix" or _primary_provider(acquisition_route, "math_priority") == "mathpix":
        return MathpixExecutionDecision(
            requested=True,
            reason="route_requests_mathpix",
        )
    return MathpixExecutionDecision(
        requested=False,
        reason="route_prefers_docling",
    )


def build_provider_execution_plan(
    acquisition_route: dict[str, Any] | None,
    *,
    mathpix_decision: MathpixExecutionDecision,
) -> dict[str, Any]:
    provider_order: list[str] = ["docling"]
    if mathpix_decision.requested:
        provider_order.append("mathpix")
    return {
        "provider_order": provider_order,
        "mathpix_requested": bool(mathpix_decision.requested),
        "mathpix_reason": mathpix_decision.reason,
    }


def derive_metadata_reference_observation_from_layout(
    provider: str,
    layout: dict[str, object] | None,
) -> MetadataReferenceObservation:
    blocks = _sorted_layout_blocks(layout)
    return MetadataReferenceObservation(
        provider=provider.strip().lower() or "layout",
        title=_title_from_layout_blocks(blocks),
        abstract=_abstract_from_layout_blocks(blocks),
        references=_references_from_layout_blocks(blocks),
    )


__all__ = [
    "MathpixExecutionDecision",
    "build_provider_execution_plan",
    "decide_mathpix_execution",
    "MetadataReferenceObservation",
    "derive_metadata_reference_observation_from_layout",
]
