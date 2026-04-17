from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, paper_pdf_path
from pipeline.sources.docling import (
    ABSTRACT_LEAD_RE,
    CONTROL_RE,
    DOCS_DIR as _DOCS_DIR_IMPL,
    ENGINE_ROOT,
    REF_RE,
    SLASH_RUN_RE,
    SPACE_RE,
    TAG_NUMBER_RE,
    _bbox_from_item,
    _clean_docling_text,
    _docling_bbox_to_canonical,
    _docling_output_dir,
    _equation_number,
    _is_reference_text,
    _layout_role_for_docling_item,
    _looks_like_abstract_marker,
    _looks_like_page_one_body_heading,
    _looks_like_title_page_front_matter,
    _page_heights,
    _page_number_from_item,
    _resolve_docling_command as _resolve_docling_command_impl,
    docling_json_to_external_sources as docling_json_to_external_sources_impl,
    run_docling as run_docling_impl,
    write_external_sources,
)
from pipeline.sources.layout import extract_layout

DOCS_DIR = CORPUS_DIR if _DOCS_DIR_IMPL == CORPUS_DIR else _DOCS_DIR_IMPL


def _paper_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return paper_pdf_path(paper_id, layout=layout)


def _resolve_docling_command() -> list[str]:
    return _resolve_docling_command_impl()


def run_docling(
    paper_id: str,
    *,
    output_dir: Path | None = None,
    device: str | None = None,
    page_batch_size: int = 4,
    timeout_seconds: int = 1800,
    layout: ProjectLayout | None = None,
) -> Path:
    return run_docling_impl(
        paper_id,
        output_dir=output_dir,
        device=device,
        page_batch_size=page_batch_size,
        timeout_seconds=timeout_seconds,
        layout=layout,
        paper_pdf_path_fn=_paper_pdf_path,
        resolve_docling_command_fn=_resolve_docling_command,
    )


def docling_json_to_external_sources(
    docling_document: dict[str, Any],
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return docling_json_to_external_sources_impl(
        docling_document,
        paper_id,
        layout=layout,
        extract_layout_fn=extract_layout,
    )


__all__ = [
    "ABSTRACT_LEAD_RE",
    "CONTROL_RE",
    "DOCS_DIR",
    "ENGINE_ROOT",
    "REF_RE",
    "SLASH_RUN_RE",
    "SPACE_RE",
    "TAG_NUMBER_RE",
    "_bbox_from_item",
    "_clean_docling_text",
    "_docling_bbox_to_canonical",
    "_docling_output_dir",
    "_equation_number",
    "_is_reference_text",
    "_layout_role_for_docling_item",
    "_looks_like_abstract_marker",
    "_looks_like_page_one_body_heading",
    "_looks_like_title_page_front_matter",
    "_page_heights",
    "_page_number_from_item",
    "_paper_pdf_path",
    "_resolve_docling_command",
    "docling_json_to_external_sources",
    "run_docling",
    "write_external_sources",
]
