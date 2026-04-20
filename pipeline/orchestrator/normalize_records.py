from __future__ import annotations

from typing import Any

from pipeline.config import PipelineConfig
from pipeline.orchestrator.pipeline_deps import PaperRecordNormalizationDeps
from pipeline.state import PaperState


def normalize_paper_records(
    state: PaperState,
    *,
    config: PipelineConfig,
    deps: PaperRecordNormalizationDeps,
) -> PaperState:
    layout = state.merged_layout or state.native_layout
    if layout is None:
        raise RuntimeError(f"Missing resolved layout for {state.paper_id}")

    external_math_entries = list((state.external_math or {}).get("entries", []))
    external_math_overlap_page_map = deps.external_math_by_page(external_math_entries)
    layout_blocks = list(layout["blocks"])
    records, layout_by_id = deps.merge_layout_and_figure_records(layout_blocks, state.figures)
    records, injected_external_math_ids = deps.inject_external_math_records(records, layout_blocks, external_math_entries)
    external_math_entries = [
        entry
        for entry in external_math_entries
        if str(entry.get("id", "")) not in injected_external_math_ids
    ]
    records = deps.mark_records_with_external_math_overlap(records, external_math_overlap_page_map)
    records = deps.repair_record_text_with_mathpix_hints(records, state.mathpix_layout)

    effective_text_engine = "native_pdf"
    if config.text_engine in {"pdftotext", "hybrid"} and config.pdftotext_enabled and deps.pdftotext_available():
        records = deps.repair_record_text_with_pdftotext(
            records,
            deps.extract_pdftotext_pages(state.paper_id),
            deps.page_height_map(layout),
        )
        effective_text_engine = "native_pdf+pdftotext"

    records = deps.promote_heading_like_records(records)
    records = deps.merge_math_fragment_records(records)
    page_one_records = deps.page_one_front_matter_records(records, state.mathpix_layout)
    records = [record for record in records if not deps.is_title_page_metadata_record(record)]
    prelude, roots = deps.build_section_tree(records)

    state.records = records
    state.layout_by_id = layout_by_id
    state.page_one_records = page_one_records
    state.prelude_records = prelude
    state.section_roots = list(roots)
    state.external_math_entries = external_math_entries
    state.external_math_overlap_page_map = external_math_overlap_page_map
    state.external_math_page_map = deps.external_math_by_page(external_math_entries)
    state.effective_text_engine = effective_text_engine
    return state
