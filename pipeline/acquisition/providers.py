from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from pipeline.text.headings import clean_heading_title, normalize_title_key


TEI_NAMESPACE = {"tei": "http://www.tei-c.org/ns/1.0"}
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


def _collapse_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _itertext(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return _collapse_text("".join(element.itertext()))


def _parse_grobid_tei(path: Path) -> MetadataReferenceObservation:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    title = _itertext(root.find(".//tei:titleStmt/tei:title", TEI_NAMESPACE))
    abstract_parts = [
        _itertext(node)
        for node in root.findall(".//tei:profileDesc/tei:abstract//tei:p", TEI_NAMESPACE)
    ]
    if not abstract_parts:
        abstract_parts = [_itertext(root.find(".//tei:profileDesc/tei:abstract", TEI_NAMESPACE))]
    references = []
    for node in root.findall(".//tei:listBibl/tei:biblStruct", TEI_NAMESPACE):
        text = _itertext(node)
        if text:
            references.append(text)
    return MetadataReferenceObservation(
        provider="grobid",
        title=title,
        abstract=_collapse_text(" ".join(part for part in abstract_parts if part)),
        references=references,
    )


def _parse_generic_metadata_json(path: Path) -> MetadataReferenceObservation:
    payload = _load_json(path)
    return MetadataReferenceObservation(
        provider=str(payload.get("provider", "generic")),
        title=_collapse_text(str(payload.get("title", ""))),
        abstract=_collapse_text(str(payload.get("abstract", ""))),
        references=[
            _collapse_text(str(item))
            for item in payload.get("references", [])
            if _collapse_text(str(item))
        ],
    )


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


def load_metadata_reference_observation(
    provider: str,
    artifact_path: str | Path,
) -> MetadataReferenceObservation:
    resolved_path = Path(artifact_path).resolve()
    normalized_provider = provider.strip().lower()
    if normalized_provider == "grobid":
        observation = _parse_grobid_tei(resolved_path)
        return MetadataReferenceObservation(
            provider="grobid",
            title=observation.title,
            abstract=observation.abstract,
            references=observation.references,
        )
    observation = _parse_generic_metadata_json(resolved_path)
    return MetadataReferenceObservation(
        provider=normalized_provider or observation.provider,
        title=observation.title,
        abstract=observation.abstract,
        references=observation.references,
    )


__all__ = [
    "MetadataReferenceObservation",
    "derive_metadata_reference_observation_from_layout",
    "load_metadata_reference_observation",
]
