from __future__ import annotations

from typing import Any, Callable

from pipeline.policies.abstract_quality import abstract_quality_flags, abstract_quality_rank
from pipeline.policies.completeness import (
    block_text as completeness_block_text,
    document_expects_figures,
    document_expects_references,
)


ANOMALY_WEIGHTS = {
    "bad_abstract": 5,
    "missing_authors": 4,
    "missing_abstract": 2,
    "weak_sections": 2,
    "missing_references": 1,
    "missing_figures": 1,
}
GENERATED_ABSTRACT_NOTE_PREFIX = "Generated abstract from "


def document_abstract_text(document: dict[str, Any]) -> str:
    abstract_id = str(document.get("front_matter", {}).get("abstract_block_id") or "")
    if not abstract_id:
        return ""
    for block in document.get("blocks", []):
        if str(block.get("id", "")) == abstract_id:
            return completeness_block_text(block)
    return ""


def document_abstract_block(document: dict[str, Any]) -> dict[str, Any] | None:
    abstract_id = str(document.get("front_matter", {}).get("abstract_block_id") or "")
    if not abstract_id:
        return None
    for block in document.get("blocks", []):
        if str(block.get("id", "")) == abstract_id:
            return block
    return None


def document_has_generated_abstract(document: dict[str, Any] | None) -> bool:
    if not isinstance(document, dict):
        return False
    abstract_block = document_abstract_block(document)
    if not abstract_block:
        return False
    review = abstract_block.get("review", {})
    notes = str(review.get("notes", "")) if isinstance(review, dict) else ""
    text = completeness_block_text(abstract_block)
    return notes.startswith(GENERATED_ABSTRACT_NOTE_PREFIX) or text.startswith("[Generated abstract from ")


def copy_existing_abstract_block(existing_document: dict[str, Any] | None, new_document: dict[str, Any]) -> bool:
    existing_block = document_abstract_block(existing_document or {})
    if not existing_block:
        return False

    target_id = str(new_document.get("front_matter", {}).get("abstract_block_id") or "")
    if not target_id:
        return False

    blocks = list(new_document.get("blocks", []))
    for block in blocks:
        if str(block.get("id", "")) != target_id:
            continue
        block["type"] = str(existing_block.get("type", block.get("type", "paragraph")))
        block["content"] = dict(existing_block.get("content", {}))
        block["source_spans"] = list(existing_block.get("source_spans", []))
        block["alternates"] = list(existing_block.get("alternates", []))
        block["review"] = dict(existing_block.get("review", {}))
        new_document["blocks"] = blocks
        return True

    preserved_block = {
        **existing_block,
        "id": target_id,
    }
    blocks.append(preserved_block)
    new_document["blocks"] = blocks
    return True


def preserve_existing_generated_abstract(
    existing_document: dict[str, Any] | None,
    new_document: dict[str, Any],
) -> bool:
    if not document_has_generated_abstract(existing_document):
        return False
    return copy_existing_abstract_block(existing_document, new_document)


def preserve_existing_generated_abstract_file(
    paper_id: str,
    existing_document: dict[str, Any] | None,
    new_document: dict[str, Any],
    *,
    abstract_file_exists: Callable[[str], bool],
) -> bool:
    if not abstract_file_exists(paper_id):
        return False
    existing_text = document_abstract_text(existing_document or {})
    if not existing_text or "missing" in abstract_quality_flags(existing_text):
        return False
    return copy_existing_abstract_block(existing_document, new_document)


def anomaly_flags(document: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    front_matter = document.get("front_matter", {})
    if not front_matter.get("authors"):
        flags.append("missing_authors")
    abstract_flags = set(abstract_quality_flags(document_abstract_text(document)))
    if not front_matter.get("abstract_block_id") or "missing" in abstract_flags:
        flags.append("missing_abstract")
    elif abstract_flags:
        flags.append("bad_abstract")
    if len(document.get("sections", [])) <= 1:
        flags.append("weak_sections")
    if len(document.get("references", [])) == 0 and document_expects_references(document):
        flags.append("missing_references")
    if len(document.get("figures", [])) == 0 and document_expects_figures(document.get("blocks", [])):
        flags.append("missing_figures")
    return flags


def document_quality_key(document: dict[str, Any], mode_index: int) -> tuple[int, int, int, int, int, int]:
    anomalies = anomaly_flags(document)
    weighted = sum(ANOMALY_WEIGHTS.get(flag, 1) for flag in anomalies)
    abstract_rank = abstract_quality_rank(document_abstract_text(document))
    return (
        weighted,
        abstract_rank,
        len(anomalies),
        -len(document.get("sections", [])),
        -len(document.get("references", [])),
        mode_index,
    )


def desired_flags_from_composed_sources(composed_sources: dict[str, Any]) -> dict[str, bool]:
    return {
        "use_external_layout": int(composed_sources.get("layout_blocks", 0) or 0) > 0,
        "use_external_math": int(composed_sources.get("math_entries", 0) or 0) > 0,
    }


def desired_flags_for_existing_paper(
    document: dict[str, Any] | None,
    composed_sources: dict[str, Any],
) -> dict[str, bool]:
    composed_flags = desired_flags_from_composed_sources(composed_sources)
    build_flags = ((document or {}).get("build", {}) or {}).get("flags", {})
    return {
        "use_external_layout": bool(build_flags.get("use_external_layout")) or composed_flags["use_external_layout"],
        "use_external_math": bool(build_flags.get("use_external_math")) or composed_flags["use_external_math"],
    }


__all__ = [
    "ANOMALY_WEIGHTS",
    "GENERATED_ABSTRACT_NOTE_PREFIX",
    "anomaly_flags",
    "copy_existing_abstract_block",
    "desired_flags_for_existing_paper",
    "desired_flags_from_composed_sources",
    "document_abstract_block",
    "document_abstract_text",
    "document_has_generated_abstract",
    "document_quality_key",
    "preserve_existing_generated_abstract",
    "preserve_existing_generated_abstract_file",
]
