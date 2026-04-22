from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from pipeline.policies.abstract_quality import abstract_quality_flags


ABSTRACT_PAGE_MARKER_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)
INTRO_PAGE_MARKER_RE = re.compile(r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s*introduction\b", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b)\b",
    re.IGNORECASE,
)

@dataclass(frozen=True)
class ProviderScore:
    provider: str
    kind: str
    block_count: int
    math_entry_count: int
    page_count: int
    heading_count: int
    front_matter_count: int
    paragraph_count: int
    reference_count: int
    caption_count: int
    avg_text_chars_per_block: float
    page_one_marker_score: int
    overall_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _block_attr(block: Any, name: str, default: Any = None) -> Any:
    if hasattr(block, name):
        return getattr(block, name)
    if isinstance(block, dict):
        return block.get(name, default)
    return default


def _layout_blocks(layout: dict[str, Any] | None) -> list[Any]:
    if not layout:
        return []
    return list(layout.get("blocks", []))


def _page_count(layout: dict[str, Any] | None) -> int:
    if not layout:
        return 0
    count = int(layout.get("page_count", 0) or 0)
    if count > 0:
        return count
    pages = {
        int(_block_attr(block, "page", 0) or 0)
        for block in _layout_blocks(layout)
        if int(_block_attr(block, "page", 0) or 0) > 0
    }
    return len(pages)


def _dict_layout_for_page_score(layout: dict[str, Any] | None) -> dict[str, Any]:
    blocks = []
    for block in _layout_blocks(layout):
        blocks.append(
            {
                "page": int(_block_attr(block, "page", 0) or 0),
                "order": int(_block_attr(block, "order", 0) or 0),
                "text": str(_block_attr(block, "text", "") or ""),
                "id": str(_block_attr(block, "id", "") or ""),
            }
        )
    return {"blocks": blocks}


def _page_one_layout_score(blocks: list[dict[str, Any]]) -> int:
    if not blocks:
        return -10
    texts = [str(block.get("text", "")).strip() for block in blocks if str(block.get("text", "")).strip()]
    marker_score = 0
    if any(ABSTRACT_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 8
    if any(INTRO_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 4
    marker_score -= sum(3 for text in texts if LAYOUT_METADATA_RE.search(text))
    return marker_score


def acceptance_threshold(kind: str) -> float:
    normalized_kind = str(kind or "").strip()
    if normalized_kind == "layout":
        return 0.3
    if normalized_kind == "math":
        return 0.05
    if normalized_kind == "metadata":
        return 0.45
    return 0.0


def annotate_provider_acceptance(
    provider_score: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(provider_score)
    kind = str(payload.get("kind", "") or "")
    threshold = acceptance_threshold(kind)
    rejection_reasons: list[str] = []
    overall_score = float(payload.get("overall_score", 0.0) or 0.0)

    if kind == "layout":
        if int(payload.get("block_count", 0) or 0) <= 0:
            rejection_reasons.append("no_blocks")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")
    elif kind == "math":
        if int(payload.get("math_entry_count", 0) or 0) <= 0:
            rejection_reasons.append("no_math_entries")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")
    elif kind == "metadata":
        has_structured_fields = (
            bool(payload.get("title_present"))
            or bool(payload.get("abstract_present"))
            or int(payload.get("reference_count", 0) or 0) > 0
        )
        if not has_structured_fields:
            rejection_reasons.append("no_structured_fields")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")

    payload["acceptance_threshold"] = threshold
    payload["accepted"] = not rejection_reasons
    payload["rejection_reasons"] = rejection_reasons
    return payload


def score_layout_provider(
    provider: str,
    layout: dict[str, Any] | None,
    *,
    kind: str,
    math_entry_count: int = 0,
) -> dict[str, Any]:
    blocks = _layout_blocks(layout)
    headings = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "heading")
    front_matter = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "front_matter")
    paragraphs = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "paragraph")
    references = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "reference")
    captions = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "caption")
    text_lengths = [len(str(_block_attr(block, "text", "") or "").strip()) for block in blocks if str(_block_attr(block, "text", "") or "").strip()]
    avg_text_chars_per_block = round(sum(text_lengths) / max(len(text_lengths), 1), 2) if text_lengths else 0.0
    marker_score = _page_one_layout_score(
        [block for block in _dict_layout_for_page_score(layout).get("blocks", []) if int(block.get("page", 0) or 0) == 1]
    )
    overall_score = round(
        (
            min(len(blocks), 80) * 0.01
            + min(headings, 12) * 0.08
            + min(front_matter, 8) * 0.08
            + min(paragraphs, 80) * 0.015
            + min(references, 40) * 0.02
            + min(captions, 20) * 0.015
            + max(marker_score, -10) * 0.05
            + min(math_entry_count, 40) * 0.02
        ),
        3,
    )
    return ProviderScore(
        provider=provider,
        kind=kind,
        block_count=len(blocks),
        math_entry_count=math_entry_count,
        page_count=_page_count(layout),
        heading_count=headings,
        front_matter_count=front_matter,
        paragraph_count=paragraphs,
        reference_count=references,
        caption_count=captions,
        avg_text_chars_per_block=avg_text_chars_per_block,
        page_one_marker_score=marker_score,
        overall_score=overall_score,
    ).to_dict()


def score_math_provider(
    provider: str,
    math_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    entries = list((math_payload or {}).get("entries", []))
    entry_count = len(entries)
    display_like_count = sum(1 for entry in entries if str(entry.get("kind", "display")) in {"display", "group"})
    overall_score = round(min(entry_count, 40) * 0.05 + min(display_like_count, 40) * 0.02, 3)
    return {
        "provider": provider,
        "kind": "math",
        "block_count": 0,
        "math_entry_count": entry_count,
        "page_count": 0,
        "heading_count": 0,
        "front_matter_count": 0,
        "paragraph_count": 0,
        "reference_count": 0,
        "caption_count": 0,
        "avg_text_chars_per_block": 0.0,
        "page_one_marker_score": 0,
        "overall_score": overall_score,
    }


def score_metadata_provider(
    provider: str,
    observation: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = dict(observation or {})
    title = str(payload.get("title", "") or "").strip()
    abstract = str(payload.get("abstract", "") or "").strip()
    references = [str(item).strip() for item in payload.get("references", []) if str(item).strip()]
    clean_abstract = bool(abstract) and not abstract_quality_flags(abstract)
    overall_score = round(
        (0.35 if title else 0.0)
        + (0.35 if clean_abstract else 0.15 if abstract else 0.0)
        + min(len(references), 40) * 0.02
        ,
        3,
    )
    return {
        "provider": provider,
        "kind": "metadata",
        "block_count": 0,
        "math_entry_count": 0,
        "page_count": 0,
        "heading_count": 0,
        "front_matter_count": 0,
        "paragraph_count": 0,
        "reference_count": len(references),
        "caption_count": 0,
        "avg_text_chars_per_block": 0.0,
        "page_one_marker_score": 0,
        "title_present": bool(title),
        "abstract_present": bool(abstract),
        "abstract_clean": clean_abstract,
        "overall_score": overall_score,
    }


def evaluate_layout_candidate(
    provider: str,
    layout: dict[str, Any] | None,
    *,
    math_entry_count: int = 0,
) -> dict[str, Any]:
    return annotate_provider_acceptance(
        score_layout_provider(
            provider,
            layout,
            kind="layout",
            math_entry_count=math_entry_count,
        ),
    )


def evaluate_math_candidate(
    provider: str,
    math_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    return annotate_provider_acceptance(
        score_math_provider(
            provider,
            math_payload,
        ),
    )


def evaluate_metadata_candidate(
    provider: str,
    observation: dict[str, Any] | None,
) -> dict[str, Any]:
    return annotate_provider_acceptance(
        score_metadata_provider(
            provider,
            observation,
        ),
    )


__all__ = [
    "acceptance_threshold",
    "annotate_provider_acceptance",
    "evaluate_layout_candidate",
    "evaluate_math_candidate",
    "evaluate_metadata_candidate",
    "score_metadata_provider",
    "score_math_provider",
    "score_layout_provider",
]
