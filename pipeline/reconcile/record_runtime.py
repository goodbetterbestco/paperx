from __future__ import annotations

from pipeline.assembly.record_block_builder import make_build_blocks_for_record
from pipeline.reconcile.block_merging import (
    make_merge_code_records,
    make_merge_paragraph_blocks,
    make_merge_paragraph_records,
    make_normalize_footnote_blocks,
    make_suppress_running_header_blocks,
)
from pipeline.reconcile.heading_promotion import make_promote_heading_like_records
from pipeline.reconcile.layout_records import make_merge_layout_and_figure_records
from pipeline.reconcile.math_suppression import (
    make_mark_records_with_external_math_overlap,
    make_suppress_graphic_display_math_blocks,
)
from pipeline.reconcile.text_repairs import make_repair_record_text_with_mathpix_hints


def build_reconcile_record_runtime_helpers(
    *,
    bindings: object,
    assembly: object,
    text_helpers: dict[str, object],
    math_helpers: dict[str, object],
) -> dict[str, object]:
    return {
        "build_blocks_for_record": make_build_blocks_for_record(
            clean_record=bindings.clean_record,
            record_analysis_text=bindings.record_analysis_text,
            is_short_ocr_fragment=bindings.is_short_ocr_fragment,
            block_source_spans=text_helpers["block_source_spans"],
            caption_label=bindings.caption_label,
            default_review=text_helpers["default_review"],
            make_reference_entry=text_helpers["make_reference_entry"],
            looks_like_real_code_record=bindings.looks_like_real_code_record,
            split_code_lines=bindings.split_code_lines,
            list_item_marker=bindings.list_item_marker,
            normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
            split_inline_math=bindings.split_inline_math,
            repair_symbolic_ocr_spans=bindings.repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=bindings.extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=bindings.merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=bindings.normalize_inline_math_spans,
            review_for_math_entry=bindings.review_for_math_entry,
            review_for_math_ref_block=bindings.review_for_math_ref_block,
            looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
            looks_like_prose_math_fragment=bindings.looks_like_prose_math_fragment,
            match_external_math_entry=math_helpers["match_external_math_entry"],
            build_block_math_entry=bindings.build_block_math_entry,
            normalize_formula_display_text=bindings.normalize_formula_display_text,
            classify_math_block=bindings.classify_math_block,
            review_for_algorithm_block_text=bindings.review_for_algorithm_block_text,
            overlapping_external_math_entries=math_helpers["overlapping_external_math_entries"],
            trim_embedded_display_math_from_paragraph=math_helpers["trim_embedded_display_math_from_paragraph"],
            looks_like_display_math_echo=math_helpers["looks_like_display_math_echo"],
        ),
        "merge_layout_and_figure_records": make_merge_layout_and_figure_records(
            layout_record=bindings.layout_record,
            absorb_figure_caption_continuations=bindings.absorb_figure_caption_continuations,
            figure_label_token=bindings.figure_label_token,
            synthetic_caption_record=bindings.synthetic_caption_record,
        ),
        "mark_records_with_external_math_overlap": make_mark_records_with_external_math_overlap(
            block_source_spans=text_helpers["block_source_spans"],
        ),
        "repair_record_text_with_mathpix_hints": make_repair_record_text_with_mathpix_hints(
            mathpix_text_blocks_by_page=bindings.mathpix_text_blocks_by_page,
            is_short_ocr_fragment=bindings.is_short_ocr_fragment,
            mathpix_text_hint_candidate=bindings.mathpix_text_hint_candidate,
            is_mathpix_text_hint_better=bindings.is_mathpix_text_hint_better,
            mathpix_prose_lead_repair_candidate=bindings.mathpix_prose_lead_repair_candidate,
            clean_text=text_helpers["clean_text"],
        ),
        "promote_heading_like_records": make_promote_heading_like_records(
            clean_text=text_helpers["clean_text"],
            block_source_spans=text_helpers["block_source_spans"],
            abstract_marker_only_re=bindings.abstract_marker_only_re,
            parse_heading_label=text_helpers["parse_heading_label"],
            clean_heading_title=bindings.clean_heading_title,
            looks_like_bad_heading=bindings.looks_like_bad_heading,
            collapse_ocr_split_caps=bindings.collapse_ocr_split_caps,
            decode_control_heading_label=bindings.decode_control_heading_label,
            normalize_decoded_heading_title=bindings.normalize_decoded_heading_title,
            split_embedded_heading_paragraph=bindings.split_embedded_heading_paragraph,
            short_word_re=text_helpers["short_word_re"],
        ),
        "merge_code_records": make_merge_code_records(
            block_source_spans=text_helpers["block_source_spans"],
            clean_text=text_helpers["clean_text"],
        ),
        "merge_paragraph_records": make_merge_paragraph_records(
            clean_text=text_helpers["clean_text"],
            block_source_spans=text_helpers["block_source_spans"],
            should_merge_paragraph_records=assembly.should_merge_paragraph_records,
            table_caption_re=assembly.table_caption_re,
        ),
        "suppress_graphic_display_math_blocks": make_suppress_graphic_display_math_blocks(
            should_demote_graphic_math_entry_to_paragraph=math_helpers["should_demote_graphic_math_entry_to_paragraph"],
            paragraph_block_from_graphic_math_entry=math_helpers["paragraph_block_from_graphic_math_entry"],
            should_drop_display_math_artifact=math_helpers["should_drop_display_math_artifact"],
        ),
        "suppress_running_header_blocks": make_suppress_running_header_blocks(
            block_source_spans=text_helpers["block_source_spans"],
            compact_text=assembly.compact_text,
            running_header_text_re=assembly.running_header_text_re,
            short_word_re=text_helpers["short_word_re"],
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
        "normalize_footnote_blocks": make_normalize_footnote_blocks(
            block_source_spans=text_helpers["block_source_spans"],
            short_word_re=text_helpers["short_word_re"],
            starts_like_sentence=assembly.starts_like_sentence,
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
        "merge_paragraph_blocks": make_merge_paragraph_blocks(
            block_source_spans=text_helpers["block_source_spans"],
            should_merge_paragraph_records=assembly.should_merge_paragraph_records,
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
    }


__all__ = [
    "build_reconcile_record_runtime_helpers",
    "make_build_blocks_for_record",
    "make_mark_records_with_external_math_overlap",
    "make_merge_code_records",
    "make_merge_layout_and_figure_records",
    "make_merge_paragraph_blocks",
    "make_merge_paragraph_records",
    "make_normalize_footnote_blocks",
    "make_promote_heading_like_records",
    "make_repair_record_text_with_mathpix_hints",
    "make_suppress_graphic_display_math_blocks",
    "make_suppress_running_header_blocks",
]
