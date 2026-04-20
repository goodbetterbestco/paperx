from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class PaperSourceResolutionDeps:
    extract_layout: Callable[[str], dict[str, Any]]
    load_external_layout: Callable[[str], dict[str, Any] | None]
    merge_native_and_external_layout: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
    load_external_math: Callable[[str], dict[str, Any] | None]
    load_mathpix_layout: Callable[[str], dict[str, Any] | None]
    extract_figures: Callable[[str], list[dict[str, Any]]]
    normalize_figure_caption_text: Callable[[str], str]


@dataclass(frozen=True)
class PaperRecordNormalizationDeps:
    external_math_by_page: Callable[[list[dict[str, Any]]], dict[int, list[dict[str, Any]]]]
    merge_layout_and_figure_records: Callable[[list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, Any]]]
    inject_external_math_records: Callable[[list[dict[str, Any]], list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]]
    mark_records_with_external_math_overlap: Callable[[list[dict[str, Any]], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]]
    repair_record_text_with_mathpix_hints: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]
    pdftotext_available: Callable[[], bool]
    repair_record_text_with_pdftotext: Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]]
    extract_pdftotext_pages: Callable[[str], dict[int, list[str]]]
    page_height_map: Callable[[dict[str, Any]], dict[int, float]]
    promote_heading_like_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    merge_math_fragment_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    page_one_front_matter_records: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]
    is_title_page_metadata_record: Callable[[dict[str, Any]], bool]
    build_section_tree: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[Any]]]


@dataclass(frozen=True)
class PaperDocumentAssemblyDeps:
    build_front_matter: Callable[[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int], tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]]
    attach_orphan_numbered_roots: Callable[[list[Any]], list[Any]]
    split_late_prelude_for_missing_intro: Callable[[list[dict[str, Any]], list[Any]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    normalize_section_title: Callable[[str], str]
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]]
    front_block_text: Callable[[list[dict[str, Any]], str | None], str]
    default_review: Callable[..., dict[str, Any]]
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]]
    build_abstract_decision: Callable[..., dict[str, Any]]
    should_replace_front_matter_abstract: Callable[[str], bool]
    recover_missing_front_matter_abstract: Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[Any]], bool]
    section_node_type: Any
    figure_label_token: Callable[[dict[str, Any]], str | None]
    prepare_section_nodes: Callable[..., list[Any]]
    split_trailing_reference_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    extract_reference_records_from_tail_section: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    reference_records_from_mathpix_layout: Callable[[dict[str, Any] | None], list[dict[str, Any]]]
    materialize_sections: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]]
    section_id_for: Callable[[Any, int], str]
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    is_figure_debris: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], bool]
    looks_like_running_header_record: Callable[[dict[str, Any]], bool]
    looks_like_table_body_debris: Callable[[dict[str, Any]], bool]
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool]
    suppress_embedded_table_headings: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    merge_code_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    merge_paragraph_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    build_blocks_for_record: Callable[[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[int, list[dict[str, Any]]], dict[int, list[dict[str, Any]]], bool, dict[str, int]], tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]]
    clean_text: Callable[[str], str]
    compile_formulas: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    annotate_formula_classifications: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    annotate_formula_semantic_expr: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    suppress_graphic_display_math_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]], tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]]
    suppress_running_header_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    normalize_footnote_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    merge_paragraph_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    now_iso: Callable[[], str]
    build_canonical_document: Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class PaperPipelineDeps:
    source_resolution: PaperSourceResolutionDeps
    record_normalization: PaperRecordNormalizationDeps
    document_assembly: PaperDocumentAssemblyDeps


__all__ = [
    "PaperDocumentAssemblyDeps",
    "PaperPipelineDeps",
    "PaperRecordNormalizationDeps",
    "PaperSourceResolutionDeps",
]
