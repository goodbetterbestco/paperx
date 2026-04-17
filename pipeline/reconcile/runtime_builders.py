from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.front_matter_runtime import (
    build_reconcile_front_matter_runtime_helpers,
)
from pipeline.reconcile.math_runtime import (
    build_reconcile_math_runtime_helpers,
)
from pipeline.reconcile.record_runtime import (
    build_reconcile_record_runtime_helpers,
)
from pipeline.reconcile.text_runtime import (
    build_reconcile_text_runtime_helpers,
)


def make_layout_bound_loader(
    *,
    loader: Callable[..., Any],
    layout: Any,
) -> Callable[[str], Any]:
    def load(target_paper_id: str) -> Any:
        return loader(target_paper_id, layout=layout)

    return load


def make_section_id_for(
    *,
    section_id_impl: Callable[..., str],
    normalize_title_key: Callable[[str], str],
) -> Callable[[Any, int], str]:
    def section_id_for(node: Any, fallback_index: int) -> str:
        return section_id_impl(
            node,
            fallback_index,
            normalize_title_key=normalize_title_key,
        )

    return section_id_for


def build_reconcile_loader_runtime_kwargs(
    *,
    runtime_layout: Any,
    loaders: Any,
) -> dict[str, Any]:
    return {
        "extract_layout": make_layout_bound_loader(loader=loaders.extract_layout, layout=runtime_layout),
        "load_external_layout": make_layout_bound_loader(loader=loaders.load_external_layout, layout=runtime_layout),
        "merge_native_and_external_layout": loaders.merge_native_and_external_layout,
        "load_external_math": make_layout_bound_loader(loader=loaders.load_external_math, layout=runtime_layout),
        "external_math_by_page": loaders.external_math_by_page,
        "load_mathpix_layout": make_layout_bound_loader(loader=loaders.load_mathpix_layout, layout=runtime_layout),
        "extract_figures": make_layout_bound_loader(loader=loaders.extract_figures, layout=runtime_layout),
        "pdftotext_available": loaders.pdftotext_available,
        "repair_record_text_with_pdftotext": loaders.repair_record_text_with_pdftotext,
        "extract_pdftotext_pages": make_layout_bound_loader(loader=loaders.extract_pdftotext_pages, layout=runtime_layout),
        "page_height_map": loaders.page_height_map,
    }


def build_reconcile_runtime_kwargs(
    *,
    runtime_layout: Any,
    loaders: Any,
    bindings: Any,
    assembly: Any,
) -> dict[str, Any]:
    text_helpers = build_reconcile_text_runtime_helpers(
        runtime_layout=runtime_layout,
        bindings=bindings,
    )
    math_helpers = build_reconcile_math_runtime_helpers(
        bindings=bindings,
        text_helpers=text_helpers,
    )
    front_matter_helpers = build_reconcile_front_matter_runtime_helpers(
        bindings=bindings,
        text_helpers=text_helpers,
    )
    record_helpers = build_reconcile_record_runtime_helpers(
        bindings=bindings,
        assembly=assembly,
        text_helpers=text_helpers,
        math_helpers=math_helpers,
    )
    return {
        **build_reconcile_loader_runtime_kwargs(
            runtime_layout=runtime_layout,
            loaders=loaders,
        ),
        "normalize_figure_caption_text": text_helpers["normalize_figure_caption_text"],
        "merge_layout_and_figure_records": record_helpers["merge_layout_and_figure_records"],
        "inject_external_math_records": bindings.inject_external_math_records,
        "mark_records_with_external_math_overlap": record_helpers["mark_records_with_external_math_overlap"],
        "repair_record_text_with_mathpix_hints": record_helpers["repair_record_text_with_mathpix_hints"],
        "promote_heading_like_records": record_helpers["promote_heading_like_records"],
        "merge_math_fragment_records": assembly.merge_math_fragment_records,
        "page_one_front_matter_records": assembly.page_one_front_matter_records,
        "is_title_page_metadata_record": assembly.is_title_page_metadata_record,
        "build_section_tree": assembly.build_section_tree,
        "build_front_matter": front_matter_helpers["build_front_matter"],
        "attach_orphan_numbered_roots": assembly.attach_orphan_numbered_roots,
        "split_late_prelude_for_missing_intro": assembly.split_late_prelude_for_missing_intro,
        "normalize_section_title": front_matter_helpers["normalize_section_title"],
        "leading_abstract_text": bindings.leading_abstract_text,
        "front_block_text": front_matter_helpers["front_block_text"],
        "default_review": text_helpers["default_review"],
        "block_source_spans": text_helpers["block_source_spans"],
        "build_abstract_decision": assembly.build_abstract_decision,
        "should_replace_front_matter_abstract": assembly.should_replace_front_matter_abstract,
        "recover_missing_front_matter_abstract": front_matter_helpers["recover_missing_front_matter_abstract"],
        "section_node_type": assembly.section_node_type,
        "figure_label_token": bindings.figure_label_token,
        "prepare_section_nodes": assembly.prepare_section_nodes,
        "split_trailing_reference_records": assembly.split_trailing_reference_records,
        "extract_reference_records_from_tail_section": assembly.extract_reference_records_from_tail_section,
        "reference_records_from_mathpix_layout": assembly.reference_records_from_mathpix_layout,
        "materialize_sections": assembly.materialize_sections,
        "section_id_for": make_section_id_for(
            section_id_impl=assembly.section_id_impl,
            normalize_title_key=text_helpers["normalize_title_key"],
        ),
        "merge_reference_records": assembly.merge_reference_records,
        "is_figure_debris": assembly.is_figure_debris,
        "looks_like_running_header_record": assembly.looks_like_running_header_record,
        "looks_like_table_body_debris": assembly.looks_like_table_body_debris,
        "is_short_ocr_fragment": bindings.is_short_ocr_fragment,
        "suppress_embedded_table_headings": assembly.suppress_embedded_table_headings,
        "merge_code_records": record_helpers["merge_code_records"],
        "merge_paragraph_records": record_helpers["merge_paragraph_records"],
        "build_blocks_for_record": record_helpers["build_blocks_for_record"],
        "clean_text": text_helpers["clean_text"],
        "compile_formulas": assembly.compile_formulas,
        "annotate_formula_classifications": assembly.annotate_formula_classifications,
        "annotate_formula_semantic_expr": assembly.annotate_formula_semantic_expr,
        "suppress_graphic_display_math_blocks": record_helpers["suppress_graphic_display_math_blocks"],
        "suppress_running_header_blocks": record_helpers["suppress_running_header_blocks"],
        "normalize_footnote_blocks": record_helpers["normalize_footnote_blocks"],
        "merge_paragraph_blocks": record_helpers["merge_paragraph_blocks"],
        "now_iso": assembly.now_iso,
        "build_canonical_document": assembly.build_canonical_document,
    }
