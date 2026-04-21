from __future__ import annotations

from typing import Any

from pipeline.assembly.abstract_recovery import (
    make_bound_front_matter_recovery_helpers as reconcile_make_bound_front_matter_recovery_helpers_runtime,
)
from pipeline.assembly.front_matter_support import (
    make_bound_front_matter_support_helpers as reconcile_make_bound_front_matter_support_helpers_runtime,
)
from pipeline.reconcile.block_builder_binding_runtime import (
    rect_intersection_area as reconcile_rect_intersection_area_binding_runtime,
)
from pipeline.reconcile.front_matter_parsing import (
    make_bound_front_matter_parsing_helpers as reconcile_make_bound_front_matter_parsing_helpers_runtime,
)
from pipeline.reconcile.layout_records import (
    make_layout_record as reconcile_make_layout_record,
    make_page_one_front_matter_records as reconcile_make_page_one_front_matter_records,
)
from pipeline.reconcile.math_fragments_runtime import (
    make_looks_like_math_fragment as reconcile_make_looks_like_math_fragment_runtime,
    make_math_signal_count as reconcile_make_math_signal_count_runtime,
    strong_operator_count as reconcile_strong_operator_count_runtime,
)
from pipeline.reconcile.pipeline_deps import (
    ReconcileBaseHelpers,
    ReconcileFrontMatterHelperBundles,
    ReconcileRootHelperBundles,
)
from pipeline.reconcile.references import (
    make_bound_reference_helpers as reconcile_make_bound_reference_helpers_binding_runtime,
)
from pipeline.reconcile.runtime_support import (
    block_source_spans as reconcile_block_source_spans_binding_runtime,
    make_mathish_ratio as reconcile_make_mathish_ratio_binding_runtime,
    make_normalize_formula_display_text as reconcile_make_normalize_formula_display_text_binding_runtime,
    now_iso as reconcile_now_iso_binding_runtime,
)
from pipeline.reconcile.screening_runtime import (
    build_reconcile_screening_helpers as reconcile_build_reconcile_screening_helpers_runtime,
)
from pipeline.reconcile.text_cleaning import (
    make_clean_record as reconcile_make_clean_record_binding_runtime,
    make_clean_text as reconcile_make_clean_text_binding_runtime,
    make_is_pdftotext_candidate_better as reconcile_make_is_pdftotext_candidate_better_binding_runtime,
    make_record_analysis_text as reconcile_make_record_analysis_text_binding_runtime,
    make_strip_known_running_header_text as reconcile_make_strip_known_running_header_text_binding_runtime,
    make_word_count as reconcile_make_word_count_binding_runtime,
)
from pipeline.reconcile.text_repairs import (
    make_bound_text_repair_helpers as reconcile_make_bound_text_repair_helpers,
)


def build_reconcile_base_helpers(
    *,
    control_char_re: Any,
    compact_text: Any,
    procedia_running_header_re: Any,
    short_word_re: Any,
    decode_ocr_codepoint_tokens: Any,
    looks_like_prose_paragraph: Any,
    math_token_re: Any,
) -> ReconcileBaseHelpers:
    clean_text = reconcile_make_clean_text_binding_runtime(
        control_char_re=control_char_re,
        compact_text=compact_text,
    )
    strip_known_running_header_text = reconcile_make_strip_known_running_header_text_binding_runtime(
        procedia_running_header_re=procedia_running_header_re,
        clean_text=clean_text,
    )
    word_count = reconcile_make_word_count_binding_runtime(
        short_word_re=short_word_re,
    )
    math_signal_count = reconcile_make_math_signal_count_runtime(
        math_token_re=math_token_re,
    )
    record_analysis_text = reconcile_make_record_analysis_text_binding_runtime(
        clean_text=clean_text,
    )
    return ReconcileBaseHelpers(
        now_iso=reconcile_now_iso_binding_runtime,
        block_source_spans=reconcile_block_source_spans_binding_runtime,
        clean_text=clean_text,
        strip_known_running_header_text=strip_known_running_header_text,
        clean_record=reconcile_make_clean_record_binding_runtime(
            strip_known_running_header_text=strip_known_running_header_text,
        ),
        normalize_formula_display_text=reconcile_make_normalize_formula_display_text_binding_runtime(
            clean_text=clean_text,
            decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
        ),
        record_analysis_text=record_analysis_text,
        word_count=word_count,
        is_pdftotext_candidate_better=reconcile_make_is_pdftotext_candidate_better_binding_runtime(
            clean_text=clean_text,
            word_count=word_count,
        ),
        looks_like_math_fragment=reconcile_make_looks_like_math_fragment_runtime(
            record_analysis_text=record_analysis_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            short_word_re=short_word_re,
            math_token_re=math_token_re,
        ),
        math_signal_count=math_signal_count,
        strong_operator_count=reconcile_strong_operator_count_runtime,
        mathish_ratio=reconcile_make_mathish_ratio_binding_runtime(
            word_count=word_count,
            math_signal_count=math_signal_count,
        ),
    )


def build_reconcile_front_matter_helper_bundles(
    *,
    base_helpers: ReconcileBaseHelpers,
    normalize_title_key: Any,
    compact_text: Any,
    short_word_re: Any,
    abstract_quality_flags: Any,
    clean_heading_title: Any,
    parse_heading_label: Any,
    looks_like_affiliation: Any,
    author_marker_re: Any,
    author_affiliation_index_re: Any,
    name_token_re: Any,
    abbreviated_venue_line_re: Any,
    title_page_metadata_re: Any,
    front_matter_metadata_re: Any,
    reference_venue_re: Any,
    author_token_re: Any,
    intro_marker_re: Any,
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    trailing_abstract_boilerplate_re: Any,
    trailing_abstract_tail_re: Any,
    preprint_marker_re: Any,
    author_note_re: Any,
    citation_year_re: Any,
    citation_author_split_re: Any,
    keywords_lead_re: Any,
    abstract_body_break_re: Any,
    figure_ref_re: Any,
    abstract_continuation_re: Any,
) -> ReconcileFrontMatterHelperBundles:
    support_helpers = reconcile_make_bound_front_matter_support_helpers_runtime(
        clean_text=base_helpers.clean_text,
        normalize_title_key=normalize_title_key,
        compact_text=compact_text,
        short_word_re=short_word_re,
        block_source_spans=base_helpers.block_source_spans,
        abstract_quality_flags=abstract_quality_flags,
    )
    parsing_helpers = reconcile_make_bound_front_matter_parsing_helpers_runtime(
        clean_text=base_helpers.clean_text,
        compact_text=compact_text,
        normalize_title_key=normalize_title_key,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        block_source_spans=base_helpers.block_source_spans,
        title_lookup_keys=support_helpers.title_lookup_keys,
        abstract_quality_flags=abstract_quality_flags,
        looks_like_affiliation=looks_like_affiliation,
        author_marker_re=author_marker_re,
        author_affiliation_index_re=author_affiliation_index_re,
        name_token_re=name_token_re,
        abbreviated_venue_line_re=abbreviated_venue_line_re,
        title_page_metadata_re=title_page_metadata_re,
        front_matter_metadata_re=front_matter_metadata_re,
        reference_venue_re=reference_venue_re,
        author_token_re=author_token_re,
        intro_marker_re=intro_marker_re,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        trailing_abstract_boilerplate_re=trailing_abstract_boilerplate_re,
        trailing_abstract_tail_re=trailing_abstract_tail_re,
        preprint_marker_re=preprint_marker_re,
        short_word_re=short_word_re,
        author_note_re=author_note_re,
        citation_year_re=citation_year_re,
        citation_author_split_re=citation_author_split_re,
    )
    recovery_helpers = reconcile_make_bound_front_matter_recovery_helpers_runtime(
        clean_text=base_helpers.clean_text,
        block_source_spans=base_helpers.block_source_spans,
        abstract_quality_flags=abstract_quality_flags,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        normalize_title_key=normalize_title_key,
        looks_like_front_matter_metadata=parsing_helpers.looks_like_front_matter_metadata,
        looks_like_body_section_marker=parsing_helpers.looks_like_body_section_marker,
        keywords_lead_re=keywords_lead_re,
        author_note_re=author_note_re,
        abstract_body_break_re=abstract_body_break_re,
        figure_ref_re=figure_ref_re,
        abstract_continuation_re=abstract_continuation_re,
        abstract_lead_re=abstract_lead_re,
        record_word_count=support_helpers.record_word_count,
        normalize_abstract_candidate_text=parsing_helpers.normalize_abstract_candidate_text,
    )
    return ReconcileFrontMatterHelperBundles(
        support_helpers=support_helpers,
        parsing_helpers=parsing_helpers,
        recovery_helpers=recovery_helpers,
    )


def build_reconcile_text_repair_helpers(
    *,
    base_helpers: ReconcileBaseHelpers,
    inline_math_re: Any,
    bbox_to_line_window: Any,
    slice_page_text: Any,
    rect_x_overlap_ratio: Any,
    display_math_prose_cue_re: Any,
    display_math_start_re: Any,
    hint_token_re: Any,
    short_word_re: Any,
    truncated_prose_lead_stopwords: set[str],
    parse_heading_label: Any,
) -> Any:
    return reconcile_make_bound_text_repair_helpers(
        clean_text=base_helpers.clean_text,
        word_count=base_helpers.word_count,
        inline_math_re=inline_math_re,
        block_source_spans=base_helpers.block_source_spans,
        bbox_to_line_window=bbox_to_line_window,
        slice_page_text=slice_page_text,
        is_pdftotext_candidate_better=base_helpers.is_pdftotext_candidate_better,
        rect_x_overlap_ratio=rect_x_overlap_ratio,
        display_math_prose_cue_re=display_math_prose_cue_re,
        display_math_start_re=display_math_start_re,
        math_signal_count=base_helpers.math_signal_count,
        hint_token_re=hint_token_re,
        short_word_re=short_word_re,
        truncated_prose_lead_stopwords=truncated_prose_lead_stopwords,
        parse_heading_label=parse_heading_label,
    )


def build_reconcile_reference_helpers(
    *,
    base_helpers: ReconcileBaseHelpers,
    reference_start_re: Any,
    about_author_re: Any,
    mathpix_text_blocks_by_page: Any,
    reference_year_re: Any,
    reference_venue_re: Any,
    reference_author_re: Any,
    short_word_re: Any,
    normalize_title_key: Any,
) -> Any:
    return reconcile_make_bound_reference_helpers_binding_runtime(
        clean_text=base_helpers.clean_text,
        block_source_spans=base_helpers.block_source_spans,
        reference_start_re=reference_start_re,
        about_author_re=about_author_re,
        mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
        reference_year_re=reference_year_re,
        reference_venue_re=reference_venue_re,
        reference_author_re=reference_author_re,
        short_word_re=short_word_re,
        normalize_title_key=normalize_title_key,
        layout_record=reconcile_make_layout_record(
            clean_text=base_helpers.clean_text,
        ),
    )


def build_reconcile_screening_helper_bundle(
    *,
    base_helpers: ReconcileBaseHelpers,
    short_word_re: Any,
    quoted_identifier_fragment_re: Any,
    label_cloud_token_re: Any,
    short_ocr_noise_re: Any,
    terminal_punctuation_re: Any,
    diagram_decision_re: Any,
    diagram_query_re: Any,
    diagram_action_re: Any,
    running_header_text_re: Any,
    table_caption_re: Any,
    parse_heading_label: Any,
    clean_heading_title: Any,
) -> Any:
    return reconcile_build_reconcile_screening_helpers_runtime(
        clean_text=base_helpers.clean_text,
        block_source_spans=base_helpers.block_source_spans,
        short_word_re=short_word_re,
        quoted_identifier_fragment_re=quoted_identifier_fragment_re,
        label_cloud_token_re=label_cloud_token_re,
        short_ocr_noise_re=short_ocr_noise_re,
        terminal_punctuation_re=terminal_punctuation_re,
        strong_operator_count=base_helpers.strong_operator_count,
        diagram_decision_re=diagram_decision_re,
        diagram_query_re=diagram_query_re,
        diagram_action_re=diagram_action_re,
        rect_intersection_area=reconcile_rect_intersection_area_binding_runtime,
        running_header_text_re=running_header_text_re,
        table_caption_re=table_caption_re,
        parse_heading_label=parse_heading_label,
        clean_heading_title=clean_heading_title,
    )


def build_reconcile_root_helper_bundles(
    *,
    control_char_re: Any,
    compact_text: Any,
    procedia_running_header_re: Any,
    short_word_re: Any,
    decode_ocr_codepoint_tokens: Any,
    looks_like_prose_paragraph: Any,
    math_token_re: Any,
    quoted_identifier_fragment_re: Any,
    label_cloud_token_re: Any,
    short_ocr_noise_re: Any,
    terminal_punctuation_re: Any,
    diagram_decision_re: Any,
    diagram_query_re: Any,
    diagram_action_re: Any,
    running_header_text_re: Any,
    table_caption_re: Any,
    parse_heading_label: Any,
    clean_heading_title: Any,
    inline_math_re: Any,
    bbox_to_line_window: Any,
    slice_page_text: Any,
    rect_x_overlap_ratio: Any,
    display_math_prose_cue_re: Any,
    display_math_start_re: Any,
    hint_token_re: Any,
    truncated_prose_lead_stopwords: set[str],
    normalize_title_key: Any,
    abstract_quality_flags: Any,
    looks_like_affiliation: Any,
    author_marker_re: Any,
    author_affiliation_index_re: Any,
    name_token_re: Any,
    abbreviated_venue_line_re: Any,
    title_page_metadata_re: Any,
    front_matter_metadata_re: Any,
    reference_venue_re: Any,
    author_token_re: Any,
    intro_marker_re: Any,
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    trailing_abstract_boilerplate_re: Any,
    trailing_abstract_tail_re: Any,
    preprint_marker_re: Any,
    author_note_re: Any,
    citation_year_re: Any,
    citation_author_split_re: Any,
    keywords_lead_re: Any,
    abstract_body_break_re: Any,
    figure_ref_re: Any,
    abstract_continuation_re: Any,
    reference_start_re: Any,
    about_author_re: Any,
    reference_year_re: Any,
    reference_author_re: Any,
) -> ReconcileRootHelperBundles:
    base_helpers = build_reconcile_base_helpers(
        control_char_re=control_char_re,
        compact_text=compact_text,
        procedia_running_header_re=procedia_running_header_re,
        short_word_re=short_word_re,
        decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
        math_token_re=math_token_re,
    )
    screening_helpers = build_reconcile_screening_helper_bundle(
        base_helpers=base_helpers,
        short_word_re=short_word_re,
        quoted_identifier_fragment_re=quoted_identifier_fragment_re,
        label_cloud_token_re=label_cloud_token_re,
        short_ocr_noise_re=short_ocr_noise_re,
        terminal_punctuation_re=terminal_punctuation_re,
        diagram_decision_re=diagram_decision_re,
        diagram_query_re=diagram_query_re,
        diagram_action_re=diagram_action_re,
        running_header_text_re=running_header_text_re,
        table_caption_re=table_caption_re,
        parse_heading_label=parse_heading_label,
        clean_heading_title=clean_heading_title,
    )
    text_repair_helpers = build_reconcile_text_repair_helpers(
        base_helpers=base_helpers,
        inline_math_re=inline_math_re,
        bbox_to_line_window=bbox_to_line_window,
        slice_page_text=slice_page_text,
        rect_x_overlap_ratio=rect_x_overlap_ratio,
        display_math_prose_cue_re=display_math_prose_cue_re,
        display_math_start_re=display_math_start_re,
        hint_token_re=hint_token_re,
        short_word_re=short_word_re,
        truncated_prose_lead_stopwords=truncated_prose_lead_stopwords,
        parse_heading_label=parse_heading_label,
    )
    front_matter_helper_bundles = build_reconcile_front_matter_helper_bundles(
        base_helpers=base_helpers,
        normalize_title_key=normalize_title_key,
        compact_text=compact_text,
        short_word_re=short_word_re,
        abstract_quality_flags=abstract_quality_flags,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        looks_like_affiliation=looks_like_affiliation,
        author_marker_re=author_marker_re,
        author_affiliation_index_re=author_affiliation_index_re,
        name_token_re=name_token_re,
        abbreviated_venue_line_re=abbreviated_venue_line_re,
        title_page_metadata_re=title_page_metadata_re,
        front_matter_metadata_re=front_matter_metadata_re,
        reference_venue_re=reference_venue_re,
        author_token_re=author_token_re,
        intro_marker_re=intro_marker_re,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        trailing_abstract_boilerplate_re=trailing_abstract_boilerplate_re,
        trailing_abstract_tail_re=trailing_abstract_tail_re,
        preprint_marker_re=preprint_marker_re,
        author_note_re=author_note_re,
        citation_year_re=citation_year_re,
        citation_author_split_re=citation_author_split_re,
        keywords_lead_re=keywords_lead_re,
        abstract_body_break_re=abstract_body_break_re,
        figure_ref_re=figure_ref_re,
        abstract_continuation_re=abstract_continuation_re,
    )
    reference_helpers = build_reconcile_reference_helpers(
        base_helpers=base_helpers,
        reference_start_re=reference_start_re,
        about_author_re=about_author_re,
        mathpix_text_blocks_by_page=text_repair_helpers.mathpix_text_blocks_by_page,
        reference_year_re=reference_year_re,
        reference_venue_re=reference_venue_re,
        reference_author_re=reference_author_re,
        short_word_re=short_word_re,
        normalize_title_key=normalize_title_key,
    )
    return ReconcileRootHelperBundles(
        base_helpers=base_helpers,
        screening_helpers=screening_helpers,
        text_repair_helpers=text_repair_helpers,
        front_matter_helper_bundles=front_matter_helper_bundles,
        reference_helpers=reference_helpers,
    )


__all__ = [
    "build_reconcile_base_helpers",
    "build_reconcile_front_matter_helper_bundles",
    "build_reconcile_reference_helpers",
    "build_reconcile_root_helper_bundles",
    "build_reconcile_screening_helper_bundle",
    "build_reconcile_text_repair_helpers",
]
