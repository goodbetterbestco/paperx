from __future__ import annotations

from typing import Any, Callable

from pipeline.config import PipelineConfig
from pipeline.state import PaperState


def normalize_paper_records(
    state: PaperState,
    *,
    config: PipelineConfig,
    external_math_by_page: Callable[[list[dict[str, Any]]], dict[int, list[dict[str, Any]]]],
    merge_layout_and_figure_records: Callable[[list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, Any]]],
    inject_external_math_records: Callable[[list[dict[str, Any]], list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]],
    mark_records_with_external_math_overlap: Callable[[list[dict[str, Any]], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]],
    repair_record_text_with_mathpix_hints: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]],
    pdftotext_available: Callable[[], bool],
    repair_record_text_with_pdftotext: Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]],
    extract_pdftotext_pages: Callable[[str], dict[int, list[str]]],
    page_height_map: Callable[[dict[str, Any]], dict[int, float]],
    promote_heading_like_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    merge_math_fragment_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    page_one_front_matter_records: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]],
    is_title_page_metadata_record: Callable[[dict[str, Any]], bool],
    build_section_tree: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[Any]]],
) -> PaperState:
    layout = state.merged_layout or state.native_layout
    if layout is None:
        raise RuntimeError(f"Missing resolved layout for {state.paper_id}")

    external_math_entries = list((state.external_math or {}).get("entries", []))
    external_math_overlap_page_map = external_math_by_page(external_math_entries)
    layout_blocks = list(layout["blocks"])
    records, layout_by_id = merge_layout_and_figure_records(layout_blocks, state.figures)
    records, injected_external_math_ids = inject_external_math_records(records, layout_blocks, external_math_entries)
    external_math_entries = [
        entry
        for entry in external_math_entries
        if str(entry.get("id", "")) not in injected_external_math_ids
    ]
    records = mark_records_with_external_math_overlap(records, external_math_overlap_page_map)
    records = repair_record_text_with_mathpix_hints(records, state.mathpix_layout)

    effective_text_engine = "native_pdf"
    if config.text_engine in {"pdftotext", "hybrid"} and config.pdftotext_enabled and pdftotext_available():
        records = repair_record_text_with_pdftotext(
            records,
            extract_pdftotext_pages(state.paper_id),
            page_height_map(layout),
        )
        effective_text_engine = "native_pdf+pdftotext"

    records = promote_heading_like_records(records)
    records = merge_math_fragment_records(records)
    page_one_records = page_one_front_matter_records(records, state.mathpix_layout)
    records = [record for record in records if not is_title_page_metadata_record(record)]
    prelude, roots = build_section_tree(records)

    state.records = records
    state.layout_by_id = layout_by_id
    state.page_one_records = page_one_records
    state.prelude_records = prelude
    state.section_roots = list(roots)
    state.external_math_entries = external_math_entries
    state.external_math_overlap_page_map = external_math_overlap_page_map
    state.external_math_page_map = external_math_by_page(external_math_entries)
    state.effective_text_engine = effective_text_engine
    return state
