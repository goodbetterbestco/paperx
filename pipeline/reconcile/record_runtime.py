from __future__ import annotations

from typing import Any, Callable


def make_build_blocks_for_record(
    *,
    build_blocks_for_record_impl: Callable[..., list[dict[str, Any]]],
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    record_analysis_text: Callable[[dict[str, Any]], str],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    caption_label: Callable[[str], str | None],
    default_review: Callable[..., dict[str, Any]],
    make_reference_entry: Callable[[dict[str, Any], int], dict[str, Any]],
    looks_like_real_code_record: Callable[[str], bool],
    split_code_lines: Callable[[str], list[str]],
    list_item_marker: Callable[[str], tuple[str | None, bool, str]],
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[..., Any],
    repair_symbolic_ocr_spans: Callable[..., Any],
    extract_general_inline_math_spans: Callable[..., Any],
    merge_inline_math_relation_suffixes: Callable[..., Any],
    normalize_inline_math_spans: Callable[..., Any],
    review_for_math_entry: Callable[..., dict[str, Any]],
    review_for_math_ref_block: Callable[..., dict[str, Any]],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    match_external_math_entry: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], dict[str, Any] | None],
    build_block_math_entry: Callable[..., dict[str, Any]],
    normalize_formula_display_text: Callable[[str], str],
    classify_math_block: Callable[..., str],
    review_for_algorithm_block_text: Callable[..., dict[str, Any]],
    overlapping_external_math_entries: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]],
    trim_embedded_display_math_from_paragraph: Callable[[str, dict[str, Any], list[dict[str, Any]]], str],
    looks_like_display_math_echo: Callable[[dict[str, Any], str, list[dict[str, Any]]], bool],
) -> Callable[..., list[dict[str, Any]]]:
    def build_blocks_for_record(
        record: dict[str, Any],
        layout_by_id: dict[str, Any],
        figures_by_label: dict[str, dict[str, Any]],
        external_math_by_page: dict[int, list[dict[str, Any]]],
        external_math_overlap_by_page: dict[int, list[dict[str, Any]]],
        references_section: bool,
        counters: dict[str, int],
    ) -> list[dict[str, Any]]:
        return build_blocks_for_record_impl(
            record,
            layout_by_id,
            figures_by_label,
            external_math_by_page,
            external_math_overlap_by_page,
            references_section,
            counters,
            clean_record=clean_record,
            record_analysis_text=record_analysis_text,
            is_short_ocr_fragment=is_short_ocr_fragment,
            block_source_spans=block_source_spans,
            caption_label=caption_label,
            default_review=default_review,
            make_reference_entry=make_reference_entry,
            looks_like_real_code_record=looks_like_real_code_record,
            split_code_lines=split_code_lines,
            list_item_marker=list_item_marker,
            normalize_paragraph_text=normalize_paragraph_text,
            split_inline_math=split_inline_math,
            repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=normalize_inline_math_spans,
            review_for_math_entry=review_for_math_entry,
            review_for_math_ref_block=review_for_math_ref_block,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            match_external_math_entry=match_external_math_entry,
            build_block_math_entry=build_block_math_entry,
            normalize_formula_display_text=normalize_formula_display_text,
            classify_math_block=classify_math_block,
            review_for_algorithm_block_text=review_for_algorithm_block_text,
            overlapping_external_math_entries=overlapping_external_math_entries,
            trim_embedded_display_math_from_paragraph=trim_embedded_display_math_from_paragraph,
            looks_like_display_math_echo=looks_like_display_math_echo,
        )

    return build_blocks_for_record


def make_merge_layout_and_figure_records(
    *,
    merge_layout_and_figure_records_impl: Callable[..., tuple[list[dict[str, Any]], dict[str, Any]]],
    layout_record: Callable[[Any], dict[str, Any]],
    absorb_figure_caption_continuations: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]],
    figure_label_token: Callable[[dict[str, Any]], str | None],
    synthetic_caption_record: Callable[[dict[str, Any], list[Any]], dict[str, Any]],
) -> Callable[[list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, Any]]]:
    def merge_layout_and_figure_records(
        layout_blocks: list[Any],
        figures: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return merge_layout_and_figure_records_impl(
            layout_blocks,
            figures,
            layout_record=layout_record,
            absorb_figure_caption_continuations=absorb_figure_caption_continuations,
            figure_label_token=figure_label_token,
            synthetic_caption_record=synthetic_caption_record,
        )

    return merge_layout_and_figure_records


def make_mark_records_with_external_math_overlap(
    *,
    mark_records_with_external_math_overlap_impl: Callable[..., list[dict[str, Any]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[list[dict[str, Any]], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]]:
    def mark_records_with_external_math_overlap(
        record_batch: list[dict[str, Any]],
        overlap_map: dict[int, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        return mark_records_with_external_math_overlap_impl(
            record_batch,
            overlap_map,
            block_source_spans=block_source_spans,
        )

    return mark_records_with_external_math_overlap


def make_repair_record_text_with_mathpix_hints(
    *,
    repair_record_text_with_mathpix_hints_impl: Callable[..., list[dict[str, Any]]],
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    mathpix_text_hint_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str],
    is_mathpix_text_hint_better: Callable[[str, str], bool],
    mathpix_prose_lead_repair_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]:
    def repair_record_text_with_mathpix_hints(
        records: list[dict[str, Any]],
        mathpix_layout: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return repair_record_text_with_mathpix_hints_impl(
            records,
            mathpix_layout,
            mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
            is_short_ocr_fragment=is_short_ocr_fragment,
            mathpix_text_hint_candidate=mathpix_text_hint_candidate,
            is_mathpix_text_hint_better=is_mathpix_text_hint_better,
            mathpix_prose_lead_repair_candidate=mathpix_prose_lead_repair_candidate,
            clean_text=clean_text,
        )

    return repair_record_text_with_mathpix_hints


def make_promote_heading_like_records(
    *,
    promote_heading_like_records_impl: Callable[..., list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    abstract_marker_only_re: Any,
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
    looks_like_bad_heading: Callable[[str], bool],
    collapse_ocr_split_caps: Callable[[str], str],
    decode_control_heading_label: Callable[[str], tuple[str | None, str]],
    normalize_decoded_heading_title: Callable[[str], str],
    split_embedded_heading_paragraph: Callable[[dict[str, Any]], tuple[str, str] | None],
    short_word_re: Any,
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def promote_heading_like_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return promote_heading_like_records_impl(
            records,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            abstract_marker_only_re=abstract_marker_only_re,
            parse_heading_label=parse_heading_label,
            clean_heading_title=clean_heading_title,
            looks_like_bad_heading=looks_like_bad_heading,
            collapse_ocr_split_caps=collapse_ocr_split_caps,
            decode_control_heading_label=decode_control_heading_label,
            normalize_decoded_heading_title=normalize_decoded_heading_title,
            split_embedded_heading_paragraph=split_embedded_heading_paragraph,
            short_word_re=short_word_re,
        )

    return promote_heading_like_records


def make_merge_code_records(
    *,
    merge_code_records_impl: Callable[..., list[dict[str, Any]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def merge_code_records(record_batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return merge_code_records_impl(
            record_batch,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
        )

    return merge_code_records


def make_merge_paragraph_records(
    *,
    merge_paragraph_records_impl: Callable[..., list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    table_caption_re: Any,
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def merge_paragraph_records(record_batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return merge_paragraph_records_impl(
            record_batch,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            should_merge_paragraph_records=should_merge_paragraph_records,
            table_caption_re=table_caption_re,
        )

    return merge_paragraph_records


def make_suppress_graphic_display_math_blocks(
    *,
    suppress_graphic_display_math_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    paragraph_block_from_graphic_math_entry: Callable[[dict[str, Any], dict[str, Any], dict[str, int]], tuple[dict[str, Any] | None, list[dict[str, Any]]]],
    should_drop_display_math_artifact: Callable[[dict[str, Any]], bool],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]], tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]]:
    def suppress_graphic_display_math_blocks(
        blocks: list[dict[str, Any]],
        compiled_math: list[dict[str, Any]],
        sections: list[dict[str, Any]],
        counters: dict[str, int],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        return suppress_graphic_display_math_blocks_impl(
            blocks,
            compiled_math,
            sections,
            counters,
            should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
            paragraph_block_from_graphic_math_entry=paragraph_block_from_graphic_math_entry,
            should_drop_display_math_artifact=should_drop_display_math_artifact,
        )

    return suppress_graphic_display_math_blocks


def make_suppress_running_header_blocks(
    *,
    suppress_running_header_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    compact_text: Callable[[str], str],
    running_header_text_re: Any,
    short_word_re: Any,
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def suppress_running_header_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return suppress_running_header_blocks_impl(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            compact_text=compact_text,
            running_header_text_re=running_header_text_re,
            short_word_re=short_word_re,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return suppress_running_header_blocks


def make_normalize_footnote_blocks(
    *,
    normalize_footnote_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    short_word_re: Any,
    starts_like_sentence: Callable[[str], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def normalize_footnote_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return normalize_footnote_blocks_impl(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            short_word_re=short_word_re,
            starts_like_sentence=starts_like_sentence,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return normalize_footnote_blocks


def make_merge_paragraph_blocks(
    *,
    merge_paragraph_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def merge_paragraph_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return merge_paragraph_blocks_impl(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            should_merge_paragraph_records=should_merge_paragraph_records,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return merge_paragraph_blocks


def build_reconcile_record_runtime_helpers(
    *,
    bindings: Any,
    assembly: Any,
    text_helpers: dict[str, Any],
    math_helpers: dict[str, Any],
) -> dict[str, Any]:
    return {
        "build_blocks_for_record": make_build_blocks_for_record(
            build_blocks_for_record_impl=bindings.build_blocks_for_record_impl,
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
            merge_layout_and_figure_records_impl=bindings.merge_layout_and_figure_records_impl,
            layout_record=bindings.layout_record,
            absorb_figure_caption_continuations=bindings.absorb_figure_caption_continuations,
            figure_label_token=bindings.figure_label_token,
            synthetic_caption_record=bindings.synthetic_caption_record,
        ),
        "mark_records_with_external_math_overlap": make_mark_records_with_external_math_overlap(
            mark_records_with_external_math_overlap_impl=bindings.mark_records_with_external_math_overlap_impl,
            block_source_spans=text_helpers["block_source_spans"],
        ),
        "repair_record_text_with_mathpix_hints": make_repair_record_text_with_mathpix_hints(
            repair_record_text_with_mathpix_hints_impl=bindings.repair_record_text_with_mathpix_hints_impl,
            mathpix_text_blocks_by_page=bindings.mathpix_text_blocks_by_page,
            is_short_ocr_fragment=bindings.is_short_ocr_fragment,
            mathpix_text_hint_candidate=bindings.mathpix_text_hint_candidate,
            is_mathpix_text_hint_better=bindings.is_mathpix_text_hint_better,
            mathpix_prose_lead_repair_candidate=bindings.mathpix_prose_lead_repair_candidate,
            clean_text=text_helpers["clean_text"],
        ),
        "promote_heading_like_records": make_promote_heading_like_records(
            promote_heading_like_records_impl=bindings.promote_heading_like_records_impl,
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
            merge_code_records_impl=assembly.merge_code_records_impl,
            block_source_spans=text_helpers["block_source_spans"],
            clean_text=text_helpers["clean_text"],
        ),
        "merge_paragraph_records": make_merge_paragraph_records(
            merge_paragraph_records_impl=assembly.merge_paragraph_records_impl,
            clean_text=text_helpers["clean_text"],
            block_source_spans=text_helpers["block_source_spans"],
            should_merge_paragraph_records=assembly.should_merge_paragraph_records,
            table_caption_re=assembly.table_caption_re,
        ),
        "suppress_graphic_display_math_blocks": make_suppress_graphic_display_math_blocks(
            suppress_graphic_display_math_blocks_impl=assembly.suppress_graphic_display_math_blocks_impl,
            should_demote_graphic_math_entry_to_paragraph=math_helpers["should_demote_graphic_math_entry_to_paragraph"],
            paragraph_block_from_graphic_math_entry=math_helpers["paragraph_block_from_graphic_math_entry"],
            should_drop_display_math_artifact=math_helpers["should_drop_display_math_artifact"],
        ),
        "suppress_running_header_blocks": make_suppress_running_header_blocks(
            suppress_running_header_blocks_impl=assembly.suppress_running_header_blocks_impl,
            block_source_spans=text_helpers["block_source_spans"],
            compact_text=assembly.compact_text,
            running_header_text_re=assembly.running_header_text_re,
            short_word_re=text_helpers["short_word_re"],
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
        "normalize_footnote_blocks": make_normalize_footnote_blocks(
            normalize_footnote_blocks_impl=assembly.normalize_footnote_blocks_impl,
            block_source_spans=text_helpers["block_source_spans"],
            short_word_re=text_helpers["short_word_re"],
            starts_like_sentence=assembly.starts_like_sentence,
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
        "merge_paragraph_blocks": make_merge_paragraph_blocks(
            merge_paragraph_blocks_impl=assembly.merge_paragraph_blocks_impl,
            block_source_spans=text_helpers["block_source_spans"],
            should_merge_paragraph_records=assembly.should_merge_paragraph_records,
            strip_known_running_header_text=text_helpers["strip_known_running_header_text"],
        ),
    }
