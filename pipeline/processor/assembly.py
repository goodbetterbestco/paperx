from __future__ import annotations

import re
from typing import Any

from pipeline.assembly.canonical_builder import build_canonical_document
from pipeline.config import PipelineConfig, build_pipeline_config
from pipeline.output.fingerprints import build_input_fingerprints
from pipeline.processor.status import now_iso
from pipeline.sources.figures import extract_figures
from pipeline.state import PaperState
from pipeline.text.references import normalize_reference_text
from pipeline.types import default_review

_AFFILIATION_HINT_RE = re.compile(
    r"\b(department|school|college|institute|university|laboratory|centre|center|faculty|city)\b",
    re.IGNORECASE,
)
_ABSTRACT_MARKER_RE = re.compile(r"^\s*abstract\b[\s:.-]*", re.IGNORECASE)
_HEADING_NUMBER_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]?\s*(.+?)\s*$")


def _block_attr(block: object, name: str, default: object = None) -> object:
    if hasattr(block, name):
        return getattr(block, name)
    if isinstance(block, dict):
        return block.get(name, default)
    return default


def _block_text(block: object) -> str:
    return " ".join(str(_block_attr(block, "text", "") or "").split()).strip()


def _sorted_blocks(layout: dict[str, Any] | None) -> list[object]:
    return sorted(
        list((layout or {}).get("blocks", []) or []),
        key=lambda block: (
            int(_block_attr(block, "page", 0) or 0),
            int(_block_attr(block, "order", 0) or 0),
            _block_text(block),
        ),
    )


def _block_source_spans(block: object) -> list[dict[str, Any]]:
    if hasattr(block, "source_span"):
        return [block.source_span().as_dict()]
    return [
        {
            "page": int(_block_attr(block, "page", 0) or 0),
            "bbox": dict(_block_attr(block, "bbox", {}) or {}),
            "engine": str(_block_attr(block, "engine", "layout") or "layout"),
        }
    ]


def _normalize_heading_title(text: str) -> str:
    match = _HEADING_NUMBER_RE.match(text)
    if not match:
        return text
    return f"{match.group(1)} {match.group(2)}".strip()


def _split_people(line: str) -> list[str]:
    normalized = line.replace(" and ", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _parse_affiliation(line: str, index: int) -> dict[str, Any]:
    parts = [part.strip() for part in line.split(",") if part.strip()]
    department = parts[0] if parts else ""
    institution = parts[1] if len(parts) > 1 else ""
    address = ", ".join(parts[2:]) if len(parts) > 2 else ""
    return {
        "id": f"aff-{index}",
        "department": department,
        "institution": institution,
        "address": address,
    }


def _front_matter_from_layout(layout: dict[str, Any], observation: dict[str, Any] | None) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], str]:
    title = ""
    abstract = str((observation or {}).get("abstract", "")).strip()
    page_one_blocks = [
        block
        for block in _sorted_blocks(layout)
        if int(_block_attr(block, "page", 0) or 0) == 1 and _block_text(block)
    ]
    page_one_front_matter = [
        block
        for block in page_one_blocks
        if str(_block_attr(block, "role", "") or "") == "front_matter"
    ]
    lines = [_block_text(block) for block in page_one_front_matter if _block_text(block)]
    if lines:
        title = lines[0]
    if not title:
        title = str((observation or {}).get("title", "")).strip()

    author_line = ""
    affiliation_lines: list[str] = []
    for line in lines[1:]:
        if _ABSTRACT_MARKER_RE.match(line):
            break
        if not author_line and not _AFFILIATION_HINT_RE.search(line):
            author_line = line
            continue
        affiliation_lines.append(line)

    authors: list[dict[str, Any]] = []
    affiliations = [_parse_affiliation(line, index) for index, line in enumerate(affiliation_lines, start=1)]
    affiliation_ids = [affiliation["id"] for affiliation in affiliations] or []
    if author_line:
        for name in _split_people(author_line):
            authors.append({"name": name, "affiliation_ids": list(affiliation_ids)})
    return title, authors, affiliations, abstract


def _reference_entry(text: str, *, index: int) -> dict[str, Any]:
    normalized_text, _ = normalize_reference_text(text)
    return {
        "id": f"ref-{index:03d}",
        "raw_text": text,
        "text": normalized_text,
        "source_spans": [],
        "alternates": [],
        "review": default_review(risk="medium"),
    }


def _body_block(block: object, *, block_id: str) -> dict[str, Any] | None:
    text = _block_text(block)
    if not text:
        return None
    role = str(_block_attr(block, "role", "paragraph") or "paragraph")
    source_spans = _block_source_spans(block)
    if role == "list_item":
        return {
            "id": block_id,
            "type": "list_item",
            "content": {
                "marker": None,
                "ordered": False,
                "depth": 1,
                "spans": [{"kind": "text", "text": text}],
            },
            "source_spans": source_spans,
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    if role == "code":
        return {
            "id": block_id,
            "type": "code",
            "content": {"lines": [line for line in str(text).splitlines() if line.strip()], "language": "text"},
            "source_spans": source_spans,
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    return {
        "id": block_id,
        "type": "paragraph",
        "content": {"spans": [{"kind": "text", "text": text}]},
        "source_spans": source_spans,
        "alternates": [],
        "review": default_review(risk="medium"),
    }


def _sections_and_blocks(layout: dict[str, Any], abstract_text: str, references: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    sections: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    abstract_block_id: str | None = None
    next_block_index = 1
    next_section_index = 1

    if abstract_text:
        abstract_block_id = f"blk-front-abstract-{next_block_index}"
        blocks.append(
            {
                "id": abstract_block_id,
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                "source_spans": [],
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        next_block_index += 1

    current_section: dict[str, Any] | None = None
    for layout_block in _sorted_blocks(layout):
        role = str(_block_attr(layout_block, "role", "") or "")
        text = _block_text(layout_block)
        if role == "front_matter" or role == "reference" or not text:
            continue
        if role == "heading":
            current_section = {
                "id": f"sec-{next_section_index}",
                "title": _normalize_heading_title(text),
                "level": 1,
                "block_ids": [],
                "children": [],
            }
            next_section_index += 1
            sections.append(current_section)
            continue
        if current_section is None:
            current_section = {
                "id": "sec-1",
                "title": "1 Introduction",
                "level": 1,
                "block_ids": [],
                "children": [],
            }
            next_section_index = max(next_section_index, 2)
            sections.append(current_section)
        block = _body_block(layout_block, block_id=f"blk-{next_block_index}")
        if block is None:
            continue
        next_block_index += 1
        blocks.append(block)
        current_section["block_ids"].append(block["id"])

    if references:
        reference_section = {
            "id": "sec-references",
            "title": "References",
            "level": 1,
            "block_ids": [],
            "children": [],
        }
        for reference in references:
            block_id = f"blk-ref-{reference['id']}"
            blocks.append(
                {
                    "id": block_id,
                    "type": "reference",
                    "content": {"reference_id": reference["id"]},
                    "source_spans": [],
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
            reference_section["block_ids"].append(block_id)
        sections.append(reference_section)

    return sections, blocks, abstract_block_id


def build_paper_state(
    paper_id: str,
    *,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
    prepared_sources: dict[str, Any] | None = None,
) -> PaperState:
    runtime_config = config or build_pipeline_config(include_review=False)
    paper_state = state or PaperState.begin(
        paper_id,
        config=runtime_config,
        started_at=now_iso(),
    )

    if prepared_sources is None:
        from pipeline.acquisition.routing import build_acquisition_route_report
        from pipeline.processor.sources import build_extraction_sources_for_paper, compose_external_sources

        acquisition_route = build_acquisition_route_report(
            paper_id,
            layout=runtime_config.layout,
        )

        docling_sources, mathpix_sources, _ = build_extraction_sources_for_paper(
            paper_id,
            acquisition_route=acquisition_route,
            layout=runtime_config.layout,
        )
        prepared_sources = compose_external_sources(
            paper_id,
            acquisition_route=acquisition_route,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
        )

    acquired_layout = dict(prepared_sources.get("final_layout") or {})
    external_math = dict(prepared_sources.get("final_math") or {})
    mathpix_layout = dict(prepared_sources.get("mathpix_layout") or {})
    metadata_candidates = dict(prepared_sources.get("metadata_candidates") or {})
    metadata_observation = dict(prepared_sources.get("metadata_observation") or {}) or None
    reference_observation = dict(prepared_sources.get("reference_observation") or {}) or None
    acquisition_route = dict(prepared_sources.get("acquisition_route_payload") or {})
    acquisition_execution = dict(prepared_sources.get("acquisition_execution") or {})
    layout_owner = str(prepared_sources.get("layout_owner", "") or "") or None
    math_owner = str(prepared_sources.get("math_owner", "") or "") or None
    metadata_owner = str(prepared_sources.get("metadata_owner", "") or "") or None
    reference_owner = str(prepared_sources.get("reference_owner", "") or "") or None
    figures = extract_figures(paper_id, layout=runtime_config.layout)
    title, authors, affiliations, abstract = _front_matter_from_layout(acquired_layout, metadata_observation)
    title = str(title or str((metadata_observation or {}).get("title", "") or "")).strip()
    if not title:
        raise RuntimeError(
            f"Missing trustworthy acquired title for {paper_id}. Refusing to fall back to the paper id."
        )
    observed_references = [
        str(item).strip()
        for item in list((reference_observation or {}).get("references", []))
        if str(item).strip()
    ]
    references = [_reference_entry(text, index=index) for index, text in enumerate(observed_references, start=1)]
    sections, blocks, abstract_block_id = _sections_and_blocks(acquired_layout, abstract, references)
    front_matter = {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "abstract_block_id": abstract_block_id,
        "funding_block_id": None,
    }
    decision_artifacts = {
        "acquisition": {
            "traits": list(acquisition_route.get("traits", [])),
            "layout_priority": list(acquisition_route.get("layout_priority", [])),
            "math_priority": list(acquisition_route.get("math_priority", [])),
            "owners": {
                "layout": layout_owner,
                "math": math_owner,
                "metadata": metadata_owner,
                "references": reference_owner,
            },
            "ownership": dict(acquisition_execution.get("ownership") or {}),
            "recovery": dict(acquisition_execution.get("recovery") or {}),
        },
    }

    paper_state.native_layout = acquired_layout
    paper_state.external_layout = acquired_layout
    paper_state.merged_layout = acquired_layout
    paper_state.external_math = external_math
    paper_state.mathpix_layout = mathpix_layout
    paper_state.metadata_candidates = metadata_candidates
    paper_state.metadata_observation = metadata_observation
    paper_state.reference_observation = reference_observation
    paper_state.figures = figures
    paper_state.acquisition_route = acquisition_route
    paper_state.front_matter = front_matter
    paper_state.blocks = blocks
    paper_state.sections = sections
    paper_state.math_entries = list((external_math or {}).get("entries", []))
    paper_state.references = references
    paper_state.decision_artifacts = decision_artifacts
    paper_state.layout_engine_name = layout_owner or "none"
    paper_state.math_engine_name = math_owner or "none"
    paper_state.input_fingerprints = build_input_fingerprints(
        paper_id,
        pdf_path=paper_state.pdf_path,
    )
    source = {
        "pdf_path": str(paper_state.pdf_path),
        "page_count": int(acquired_layout.get("page_count", 0) or 0),
        "page_sizes_pt": list(acquired_layout.get("page_sizes_pt", [])),
    }
    paper_state.document = build_canonical_document(
        paper_id=paper_id,
        title=front_matter["title"],
        source=source,
        timestamp=paper_state.started_at,
        layout_engine_name=paper_state.layout_engine_name,
        math_engine_name=paper_state.math_engine_name,
        front_matter=front_matter,
        sections=sections,
        blocks=blocks,
        math_entries=paper_state.math_entries,
        figures=figures,
        references=references,
        decision_artifacts=decision_artifacts,
    )
    return paper_state


__all__ = ["build_paper_state"]
