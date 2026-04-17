from __future__ import annotations

from typing import Any, Callable


def make_normalize_text_for_layout(
    *,
    normalize_text_impl: Callable[..., tuple[str, Any]],
    layout: Any,
) -> Callable[[str], tuple[str, Any]]:
    def normalize_text_for_layout(text: str) -> tuple[str, Any]:
        return normalize_text_impl(text, layout=layout)

    return normalize_text_for_layout


def make_layout_bound_loader(
    *,
    loader: Callable[..., Any],
    layout: Any,
) -> Callable[[str], Any]:
    def load(target_paper_id: str) -> Any:
        return loader(target_paper_id, layout=layout)

    return load


def make_normalize_paragraph_text(
    *,
    normalize_paragraph_text_impl: Callable[..., str],
    strip_known_running_header_text: Callable[[str], str],
    leading_negationslash_artifact_re: Any,
    leading_ocr_marker_re: Any,
    leading_punct_artifact_re: Any,
    leading_var_artifact_re: Any,
    trailing_numeric_artifact_re: Any,
    normalize_prose_text: Callable[[str], tuple[str, Any]],
    clean_text: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_paragraph_text(text: str) -> str:
        return normalize_paragraph_text_impl(
            text,
            strip_known_running_header_text=strip_known_running_header_text,
            leading_negationslash_artifact_re=leading_negationslash_artifact_re,
            leading_ocr_marker_re=leading_ocr_marker_re,
            leading_punct_artifact_re=leading_punct_artifact_re,
            leading_var_artifact_re=leading_var_artifact_re,
            trailing_numeric_artifact_re=trailing_numeric_artifact_re,
            normalize_prose_text=normalize_prose_text,
            clean_text=clean_text,
        )

    return normalize_paragraph_text


def make_normalize_section_title(
    *,
    normalize_section_title_impl: Callable[..., str],
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_section_title(title: str) -> str:
        return normalize_section_title_impl(
            title,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            parse_heading_label=parse_heading_label,
            normalize_title_key=normalize_title_key,
        )

    return normalize_section_title


def make_front_block_text(
    *,
    front_block_text_impl: Callable[..., str],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], str | None], str]:
    def front_block_text(blocks: list[dict[str, Any]], block_id: str | None) -> str:
        return front_block_text_impl(blocks, block_id, clean_text=clean_text)

    return front_block_text


def make_normalize_figure_caption_text(
    *,
    normalize_figure_caption_text_impl: Callable[..., str],
    clean_text: Callable[[str], str],
    normalize_prose_text: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def normalize_figure_caption_text(text: str) -> str:
        return normalize_figure_caption_text_impl(
            text,
            clean_text=clean_text,
            normalize_prose_text=normalize_prose_text,
        )

    return normalize_figure_caption_text


def make_reference_entry_builder(
    *,
    make_reference_entry_impl: Callable[..., dict[str, Any]],
    clean_text: Callable[[str], str],
    normalize_reference_text: Callable[[str], tuple[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], int], dict[str, Any]]:
    def make_reference_entry(record: dict[str, Any], index: int) -> dict[str, Any]:
        return make_reference_entry_impl(
            record,
            index,
            clean_text=clean_text,
            normalize_reference_text=normalize_reference_text,
            block_source_spans=block_source_spans,
            default_review=default_review,
        )

    return make_reference_entry


def make_match_external_math_entry(
    *,
    match_external_math_entry_impl: Callable[..., dict[str, Any] | None],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], dict[str, Any] | None]:
    def match_external_math_entry(
        record_item: dict[str, Any],
        external_math_map: dict[int, list[dict[str, Any]]],
    ) -> dict[str, Any] | None:
        return match_external_math_entry_impl(
            record_item,
            external_math_map,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
        )

    return match_external_math_entry


def make_overlapping_external_math_entries(
    *,
    overlapping_external_math_entries_impl: Callable[..., list[dict[str, Any]]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]]:
    def overlapping_external_math_entries(
        record_item: dict[str, Any],
        overlap_map: dict[int, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        return overlapping_external_math_entries_impl(
            record_item,
            overlap_map,
            block_source_spans=block_source_spans,
        )

    return overlapping_external_math_entries


def make_trim_embedded_display_math_from_paragraph(
    *,
    trim_embedded_display_math_from_paragraph_impl: Callable[..., str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Any,
    display_math_resume_re: Any,
    display_math_start_re: Any,
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
) -> Callable[[str, dict[str, Any], list[dict[str, Any]]], str]:
    def trim_embedded_display_math_from_paragraph(
        text_value: str,
        record_item: dict[str, Any],
        overlapping_math: list[dict[str, Any]],
    ) -> str:
        return trim_embedded_display_math_from_paragraph_impl(
            text_value,
            record_item,
            overlapping_math,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
            display_math_prose_cue_re=display_math_prose_cue_re,
            display_math_resume_re=display_math_resume_re,
            display_math_start_re=display_math_start_re,
            mathish_ratio=mathish_ratio,
            strong_operator_count=strong_operator_count,
        )

    return trim_embedded_display_math_from_paragraph


def make_looks_like_display_math_echo(
    *,
    looks_like_display_math_echo_impl: Callable[..., bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
    short_word_re: Any,
) -> Callable[[dict[str, Any], str, list[dict[str, Any]]], bool]:
    def looks_like_display_math_echo(
        record_item: dict[str, Any],
        text_value: str,
        overlapping_math: list[dict[str, Any]],
    ) -> bool:
        return looks_like_display_math_echo_impl(
            record_item,
            text_value,
            overlapping_math,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
            mathish_ratio=mathish_ratio,
            strong_operator_count=strong_operator_count,
            short_word_re=short_word_re,
        )

    return looks_like_display_math_echo


def make_math_entry_looks_like_prose(
    *,
    math_entry_looks_like_prose_impl: Callable[..., bool],
    normalize_paragraph_text: Callable[[str], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
) -> Callable[[dict[str, Any]], bool]:
    def math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
        return math_entry_looks_like_prose_impl(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            word_count=word_count,
        )

    return math_entry_looks_like_prose


def make_should_demote_prose_math_entry_to_paragraph(
    *,
    should_demote_prose_math_entry_to_paragraph_impl: Callable[..., bool],
    normalize_paragraph_text: Callable[[str], str],
    word_count: Callable[[str], int],
    strong_operator_count: Callable[[str], int],
    mathish_ratio: Callable[[str], float],
    math_entry_looks_like_prose: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_prose_math_entry_to_paragraph_impl(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            word_count=word_count,
            strong_operator_count=strong_operator_count,
            mathish_ratio=mathish_ratio,
            math_entry_looks_like_prose=math_entry_looks_like_prose,
            math_entry_semantic_policy=math_entry_semantic_policy,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
        )

    return should_demote_prose_math_entry_to_paragraph


def make_should_demote_graphic_math_entry_to_paragraph(
    *,
    should_demote_graphic_math_entry_to_paragraph_impl: Callable[..., bool],
    should_demote_prose_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_graphic_math_entry_to_paragraph_impl(
            entry,
            should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
        )

    return should_demote_graphic_math_entry_to_paragraph


def make_should_drop_display_math_artifact(
    *,
    should_drop_display_math_artifact_impl: Callable[..., bool],
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
        return should_drop_display_math_artifact_impl(
            entry,
            should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
            group_entry_items_are_graphic_only=group_entry_items_are_graphic_only,
            math_entry_semantic_policy=math_entry_semantic_policy,
            math_entry_category=math_entry_category,
        )

    return should_drop_display_math_artifact


def make_paragraph_block_from_graphic_math_entry(
    *,
    paragraph_block_from_graphic_math_entry_impl: Callable[..., tuple[dict[str, Any] | None, list[dict[str, Any]]]],
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[..., Any],
    repair_symbolic_ocr_spans: Callable[..., Any],
    extract_general_inline_math_spans: Callable[..., Any],
    merge_inline_math_relation_suffixes: Callable[..., Any],
    normalize_inline_math_spans: Callable[..., Any],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], dict[str, Any], dict[str, int]], tuple[dict[str, Any] | None, list[dict[str, Any]]]]:
    def paragraph_block_from_graphic_math_entry(
        block: dict[str, Any],
        math_entry: dict[str, Any],
        counters: dict[str, int],
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        return paragraph_block_from_graphic_math_entry_impl(
            block,
            math_entry,
            counters,
            normalize_paragraph_text=normalize_paragraph_text,
            split_inline_math=split_inline_math,
            repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=normalize_inline_math_spans,
            default_review=default_review,
        )

    return paragraph_block_from_graphic_math_entry


def make_build_front_matter(
    *,
    build_front_matter_impl: Callable[..., tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]],
    split_leading_front_matter_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    clean_text: Callable[[str], str],
    record_word_count: Callable[[dict[str, Any]], int],
    record_width: Callable[[dict[str, Any]], float],
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Any,
    looks_like_affiliation: Callable[[str], bool],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    matches_title_line: Callable[[str, str], bool],
    looks_like_affiliation_continuation: Callable[[str], bool],
    funding_re: Any,
    dedupe_text_lines: Callable[[list[str]], list[str]],
    filter_front_matter_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    parse_authors: Callable[[str], list[dict[str, Any]]],
    parse_authors_from_citation_line: Callable[[str, str], list[dict[str, Any]]],
    normalize_author_line: Callable[[str], str],
    missing_front_matter_author: Callable[[], dict[str, Any]],
    build_affiliations_for_authors: Callable[[int, list[str]], tuple[list[dict[str, Any]], list[list[str]]]],
    missing_front_matter_affiliation: Callable[[], dict[str, Any]],
    strip_author_prefix_from_affiliation_line: Callable[[str, list[dict[str, Any]]], str],
    normalize_title_key: Callable[[str], str],
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]],
    looks_like_body_section_marker: Callable[[str], bool],
    preprint_marker_re: Any,
    keywords_lead_re: Any,
    abstract_text_is_usable: Callable[[str], bool],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
    default_review: Callable[..., dict[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    front_matter_missing_placeholder: str,
) -> Callable[[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int], tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]]:
    def build_front_matter(
        paper_id: str,
        prelude: list[dict[str, Any]],
        page_one_records: list[dict[str, Any]],
        blocks: list[dict[str, Any]],
        next_block_index: int,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]:
        return build_front_matter_impl(
            paper_id,
            prelude,
            page_one_records,
            blocks,
            next_block_index,
            split_leading_front_matter_records=split_leading_front_matter_records,
            clean_record=clean_record,
            clean_text=clean_text,
            record_word_count=record_word_count,
            record_width=record_width,
            abstract_marker_only_re=abstract_marker_only_re,
            abstract_lead_re=abstract_lead_re,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            author_note_re=author_note_re,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_intro_marker=looks_like_intro_marker,
            looks_like_author_line=looks_like_author_line,
            looks_like_contact_name=looks_like_contact_name,
            matches_title_line=matches_title_line,
            looks_like_affiliation_continuation=looks_like_affiliation_continuation,
            funding_re=funding_re,
            dedupe_text_lines=dedupe_text_lines,
            filter_front_matter_authors=filter_front_matter_authors,
            parse_authors=parse_authors,
            parse_authors_from_citation_line=parse_authors_from_citation_line,
            normalize_author_line=normalize_author_line,
            missing_front_matter_author=missing_front_matter_author,
            build_affiliations_for_authors=build_affiliations_for_authors,
            missing_front_matter_affiliation=missing_front_matter_affiliation,
            strip_author_prefix_from_affiliation_line=strip_author_prefix_from_affiliation_line,
            normalize_title_key=normalize_title_key,
            clone_record_with_text=clone_record_with_text,
            looks_like_body_section_marker=looks_like_body_section_marker,
            preprint_marker_re=preprint_marker_re,
            keywords_lead_re=keywords_lead_re,
            abstract_text_is_usable=abstract_text_is_usable,
            normalize_abstract_candidate_text=normalize_abstract_candidate_text,
            default_review=default_review,
            block_source_spans=block_source_spans,
            front_matter_missing_placeholder=front_matter_missing_placeholder,
        )

    return build_front_matter


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


def run_reconcile_pipeline(
    paper_id: str,
    *,
    text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
    layout_output: dict[str, Any] | None,
    figures: list[dict[str, Any]] | None,
    runtime_layout: Any,
    run_paper_pipeline_impl: Callable[..., Any],
    extract_layout: Callable[..., Any],
    load_external_layout: Callable[..., Any],
    merge_native_and_external_layout: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    load_external_math: Callable[..., Any],
    external_math_by_page: Callable[[list[dict[str, Any]]], dict[int, list[dict[str, Any]]]],
    load_mathpix_layout: Callable[..., Any],
    extract_figures: Callable[..., Any],
    normalize_prose_text_impl: Callable[..., tuple[str, Any]],
    normalize_reference_text_impl: Callable[..., tuple[str, Any]],
    normalize_paragraph_text_impl: Callable[..., str],
    normalize_figure_caption_text_impl: Callable[..., str],
    strip_known_running_header_text: Callable[[str], str],
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
    make_reference_entry_impl: Callable[..., dict[str, Any]],
    leading_negationslash_artifact_re: Any,
    leading_ocr_marker_re: Any,
    leading_punct_artifact_re: Any,
    leading_var_artifact_re: Any,
    trailing_numeric_artifact_re: Any,
    math_entry_looks_like_prose_impl: Callable[..., bool],
    should_demote_prose_math_entry_to_paragraph_impl: Callable[..., bool],
    should_demote_graphic_math_entry_to_paragraph_impl: Callable[..., bool],
    should_drop_display_math_artifact_impl: Callable[..., bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
    strong_operator_count: Callable[[str], int],
    mathish_ratio: Callable[[str], float],
    paragraph_block_from_graphic_math_entry_impl: Callable[..., tuple[dict[str, Any] | None, list[dict[str, Any]]]],
    split_inline_math: Callable[..., Any],
    repair_symbolic_ocr_spans: Callable[..., Any],
    extract_general_inline_math_spans: Callable[..., Any],
    merge_inline_math_relation_suffixes: Callable[..., Any],
    normalize_inline_math_spans: Callable[..., Any],
    build_front_matter_impl: Callable[..., Any],
    split_leading_front_matter_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    record_word_count: Callable[[dict[str, Any]], int],
    record_width: Callable[[dict[str, Any]], float],
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Any,
    looks_like_affiliation: Callable[[str], bool],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    matches_title_line: Callable[[str, str], bool],
    looks_like_affiliation_continuation: Callable[[str], bool],
    funding_re: Any,
    dedupe_text_lines: Callable[[list[str]], list[str]],
    filter_front_matter_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    parse_authors: Callable[[str], list[dict[str, Any]]],
    parse_authors_from_citation_line: Callable[[str, str], list[dict[str, Any]]],
    normalize_author_line: Callable[[str], str],
    missing_front_matter_author: Callable[[], dict[str, Any]],
    build_affiliations_for_authors: Callable[[int, list[str]], tuple[list[dict[str, Any]], list[list[str]]]],
    missing_front_matter_affiliation: Callable[[], dict[str, Any]],
    strip_author_prefix_from_affiliation_line: Callable[[str, list[dict[str, Any]]], str],
    normalize_title_key: Callable[[str], str],
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]],
    looks_like_body_section_marker: Callable[[str], bool],
    preprint_marker_re: Any,
    keywords_lead_re: Any,
    abstract_text_is_usable: Callable[[str], bool],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
    front_matter_missing_placeholder: str,
    normalize_section_title_impl: Callable[..., str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    front_block_text_impl: Callable[..., str],
    recover_missing_front_matter_abstract_impl: Callable[..., bool],
    abstract_quality_flags: Callable[[str], list[str]],
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]],
    abstract_text_is_recoverable: Callable[[str], bool],
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool],
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    build_blocks_for_record_impl: Callable[..., Any],
    record_analysis_text: Callable[[dict[str, Any]], str],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    caption_label: Callable[[str], str | None],
    looks_like_real_code_record: Callable[[str], bool],
    split_code_lines: Callable[[str], list[str]],
    list_item_marker: Callable[[str], tuple[str | None, bool, str]],
    review_for_math_entry: Callable[..., dict[str, Any]],
    review_for_math_ref_block: Callable[..., dict[str, Any]],
    match_external_math_entry_impl: Callable[..., dict[str, Any] | None],
    build_block_math_entry: Callable[..., dict[str, Any]],
    normalize_formula_display_text: Callable[[str], str],
    classify_math_block: Callable[..., str],
    review_for_algorithm_block_text: Callable[..., dict[str, Any]],
    overlapping_external_math_entries_impl: Callable[..., list[dict[str, Any]]],
    trim_embedded_display_math_from_paragraph_impl: Callable[..., str],
    display_math_prose_cue_re: Any,
    display_math_resume_re: Any,
    display_math_start_re: Any,
    looks_like_display_math_echo_impl: Callable[..., bool],
    short_word_re: Any,
    merge_layout_and_figure_records_impl: Callable[..., tuple[list[dict[str, Any]], dict[str, Any]]],
    layout_record: Callable[[Any], dict[str, Any]],
    absorb_figure_caption_continuations: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]],
    figure_label_token: Callable[[dict[str, Any]], str | None],
    synthetic_caption_record: Callable[[dict[str, Any], list[Any]], dict[str, Any]],
    inject_external_math_records: Callable[[list[dict[str, Any]], list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]],
    mark_records_with_external_math_overlap_impl: Callable[..., list[dict[str, Any]]],
    repair_record_text_with_mathpix_hints_impl: Callable[..., list[dict[str, Any]]],
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    mathpix_text_hint_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str],
    is_mathpix_text_hint_better: Callable[[str, str], bool],
    mathpix_prose_lead_repair_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str],
    pdftotext_available: Callable[[], bool],
    repair_record_text_with_pdftotext: Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]],
    extract_pdftotext_pages: Callable[..., Any],
    page_height_map: Callable[[dict[str, Any]], dict[int, float]],
    promote_heading_like_records_impl: Callable[..., list[dict[str, Any]]],
    looks_like_bad_heading: Callable[[str], bool],
    collapse_ocr_split_caps: Callable[[str], str],
    decode_control_heading_label: Callable[[str], tuple[str | None, str]],
    normalize_decoded_heading_title: Callable[[str], str],
    split_embedded_heading_paragraph: Callable[[dict[str, Any]], tuple[str, str] | None],
    merge_math_fragment_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    page_one_front_matter_records: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]],
    is_title_page_metadata_record: Callable[[dict[str, Any]], bool],
    build_section_tree: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[Any]]],
    attach_orphan_numbered_roots: Callable[[list[Any]], list[Any]],
    split_late_prelude_for_missing_intro: Callable[[list[dict[str, Any]], list[Any]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    build_abstract_decision: Callable[..., dict[str, Any]],
    should_replace_front_matter_abstract: Callable[[str], bool],
    section_node_type: Any,
    prepare_section_nodes: Callable[..., list[Any]],
    split_trailing_reference_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    extract_reference_records_from_tail_section: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    reference_records_from_mathpix_layout: Callable[[dict[str, Any] | None], list[dict[str, Any]]],
    materialize_sections: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    section_id_impl: Callable[..., str],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    is_figure_debris: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], bool],
    looks_like_running_header_record: Callable[[dict[str, Any]], bool],
    looks_like_table_body_debris: Callable[[dict[str, Any]], bool],
    suppress_embedded_table_headings: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    table_caption_re: Any,
    merge_code_records_impl: Callable[..., list[dict[str, Any]]],
    merge_paragraph_records_impl: Callable[..., list[dict[str, Any]]],
    compile_formulas: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    annotate_formula_classifications: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    annotate_formula_semantic_expr: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    suppress_graphic_display_math_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    suppress_running_header_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    compact_text: Callable[[str], str],
    running_header_text_re: Any,
    normalize_footnote_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    starts_like_sentence: Callable[[str], bool],
    merge_paragraph_blocks_impl: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    now_iso: Callable[[], str],
    build_canonical_document: Callable[..., dict[str, Any]],
    config: Any,
    state: Any,
) -> Any:
    normalize_prose_text_for_layout = make_normalize_text_for_layout(
        normalize_text_impl=normalize_prose_text_impl,
        layout=runtime_layout,
    )
    normalize_reference_text_for_layout = make_normalize_text_for_layout(
        normalize_text_impl=normalize_reference_text_impl,
        layout=runtime_layout,
    )
    normalize_paragraph_text = make_normalize_paragraph_text(
        normalize_paragraph_text_impl=normalize_paragraph_text_impl,
        strip_known_running_header_text=strip_known_running_header_text,
        leading_negationslash_artifact_re=leading_negationslash_artifact_re,
        leading_ocr_marker_re=leading_ocr_marker_re,
        leading_punct_artifact_re=leading_punct_artifact_re,
        leading_var_artifact_re=leading_var_artifact_re,
        trailing_numeric_artifact_re=trailing_numeric_artifact_re,
        normalize_prose_text=normalize_prose_text_for_layout,
        clean_text=clean_text,
    )
    normalize_figure_caption_text = make_normalize_figure_caption_text(
        normalize_figure_caption_text_impl=normalize_figure_caption_text_impl,
        clean_text=clean_text,
        normalize_prose_text=normalize_prose_text_for_layout,
    )
    make_reference_entry = make_reference_entry_builder(
        make_reference_entry_impl=make_reference_entry_impl,
        clean_text=clean_text,
        normalize_reference_text=normalize_reference_text_for_layout,
        block_source_spans=block_source_spans,
        default_review=default_review,
    )
    math_entry_looks_like_prose = make_math_entry_looks_like_prose(
        math_entry_looks_like_prose_impl=math_entry_looks_like_prose_impl,
        normalize_paragraph_text=normalize_paragraph_text,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
        looks_like_prose_math_fragment=looks_like_prose_math_fragment,
        word_count=word_count,
    )
    should_demote_prose_math_entry_to_paragraph = make_should_demote_prose_math_entry_to_paragraph(
        should_demote_prose_math_entry_to_paragraph_impl=should_demote_prose_math_entry_to_paragraph_impl,
        normalize_paragraph_text=normalize_paragraph_text,
        word_count=word_count,
        strong_operator_count=strong_operator_count,
        mathish_ratio=mathish_ratio,
        math_entry_looks_like_prose=math_entry_looks_like_prose,
        math_entry_semantic_policy=math_entry_semantic_policy,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
    )
    should_demote_graphic_math_entry_to_paragraph = make_should_demote_graphic_math_entry_to_paragraph(
        should_demote_graphic_math_entry_to_paragraph_impl=should_demote_graphic_math_entry_to_paragraph_impl,
        should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
    )
    should_drop_display_math_artifact = make_should_drop_display_math_artifact(
        should_drop_display_math_artifact_impl=should_drop_display_math_artifact_impl,
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        group_entry_items_are_graphic_only=group_entry_items_are_graphic_only,
        math_entry_semantic_policy=math_entry_semantic_policy,
        math_entry_category=math_entry_category,
    )
    paragraph_block_from_graphic_math_entry = make_paragraph_block_from_graphic_math_entry(
        paragraph_block_from_graphic_math_entry_impl=paragraph_block_from_graphic_math_entry_impl,
        normalize_paragraph_text=normalize_paragraph_text,
        split_inline_math=split_inline_math,
        repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=normalize_inline_math_spans,
        default_review=default_review,
    )
    build_front_matter = make_build_front_matter(
        build_front_matter_impl=build_front_matter_impl,
        split_leading_front_matter_records=split_leading_front_matter_records,
        clean_record=clean_record,
        clean_text=clean_text,
        record_word_count=record_word_count,
        record_width=record_width,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        author_note_re=author_note_re,
        looks_like_affiliation=looks_like_affiliation,
        looks_like_intro_marker=looks_like_intro_marker,
        looks_like_author_line=looks_like_author_line,
        looks_like_contact_name=looks_like_contact_name,
        matches_title_line=matches_title_line,
        looks_like_affiliation_continuation=looks_like_affiliation_continuation,
        funding_re=funding_re,
        dedupe_text_lines=dedupe_text_lines,
        filter_front_matter_authors=filter_front_matter_authors,
        parse_authors=parse_authors,
        parse_authors_from_citation_line=parse_authors_from_citation_line,
        normalize_author_line=normalize_author_line,
        missing_front_matter_author=missing_front_matter_author,
        build_affiliations_for_authors=build_affiliations_for_authors,
        missing_front_matter_affiliation=missing_front_matter_affiliation,
        strip_author_prefix_from_affiliation_line=strip_author_prefix_from_affiliation_line,
        normalize_title_key=normalize_title_key,
        clone_record_with_text=clone_record_with_text,
        looks_like_body_section_marker=looks_like_body_section_marker,
        preprint_marker_re=preprint_marker_re,
        keywords_lead_re=keywords_lead_re,
        abstract_text_is_usable=abstract_text_is_usable,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
        default_review=default_review,
        block_source_spans=block_source_spans,
        front_matter_missing_placeholder=front_matter_missing_placeholder,
    )
    normalize_section_title = make_normalize_section_title(
        normalize_section_title_impl=normalize_section_title_impl,
        clean_text=clean_text,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        normalize_title_key=normalize_title_key,
    )
    front_block_text = make_front_block_text(
        front_block_text_impl=front_block_text_impl,
        clean_text=clean_text,
    )
    match_external_math_entry = make_match_external_math_entry(
        match_external_math_entry_impl=match_external_math_entry_impl,
        block_source_spans=block_source_spans,
        clean_text=clean_text,
    )
    overlapping_external_math_entries = make_overlapping_external_math_entries(
        overlapping_external_math_entries_impl=overlapping_external_math_entries_impl,
        block_source_spans=block_source_spans,
    )
    trim_embedded_display_math_from_paragraph = make_trim_embedded_display_math_from_paragraph(
        trim_embedded_display_math_from_paragraph_impl=trim_embedded_display_math_from_paragraph_impl,
        block_source_spans=block_source_spans,
        clean_text=clean_text,
        display_math_prose_cue_re=display_math_prose_cue_re,
        display_math_resume_re=display_math_resume_re,
        display_math_start_re=display_math_start_re,
        mathish_ratio=mathish_ratio,
        strong_operator_count=strong_operator_count,
    )
    looks_like_display_math_echo = make_looks_like_display_math_echo(
        looks_like_display_math_echo_impl=looks_like_display_math_echo_impl,
        block_source_spans=block_source_spans,
        clean_text=clean_text,
        mathish_ratio=mathish_ratio,
        strong_operator_count=strong_operator_count,
        short_word_re=short_word_re,
    )
    recover_missing_front_matter_abstract = make_recover_missing_front_matter_abstract(
        recover_missing_front_matter_abstract_impl=recover_missing_front_matter_abstract_impl,
        front_block_text=front_block_text,
        abstract_quality_flags=abstract_quality_flags,
        normalize_section_title=normalize_section_title,
        leading_abstract_text=leading_abstract_text,
        abstract_text_is_recoverable=abstract_text_is_recoverable,
        replace_front_matter_abstract_text=replace_front_matter_abstract_text,
        opening_abstract_candidate_records=opening_abstract_candidate_records,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
    )
    build_blocks_for_record = make_build_blocks_for_record(
        build_blocks_for_record_impl=build_blocks_for_record_impl,
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
    merge_layout_and_figure_records = make_merge_layout_and_figure_records(
        merge_layout_and_figure_records_impl=merge_layout_and_figure_records_impl,
        layout_record=layout_record,
        absorb_figure_caption_continuations=absorb_figure_caption_continuations,
        figure_label_token=figure_label_token,
        synthetic_caption_record=synthetic_caption_record,
    )
    mark_records_with_external_math_overlap = make_mark_records_with_external_math_overlap(
        mark_records_with_external_math_overlap_impl=mark_records_with_external_math_overlap_impl,
        block_source_spans=block_source_spans,
    )
    repair_record_text_with_mathpix_hints = make_repair_record_text_with_mathpix_hints(
        repair_record_text_with_mathpix_hints_impl=repair_record_text_with_mathpix_hints_impl,
        mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
        is_short_ocr_fragment=is_short_ocr_fragment,
        mathpix_text_hint_candidate=mathpix_text_hint_candidate,
        is_mathpix_text_hint_better=is_mathpix_text_hint_better,
        mathpix_prose_lead_repair_candidate=mathpix_prose_lead_repair_candidate,
        clean_text=clean_text,
    )
    promote_heading_like_records = make_promote_heading_like_records(
        promote_heading_like_records_impl=promote_heading_like_records_impl,
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
    merge_code_records = make_merge_code_records(
        merge_code_records_impl=merge_code_records_impl,
        block_source_spans=block_source_spans,
        clean_text=clean_text,
    )
    merge_paragraph_records = make_merge_paragraph_records(
        merge_paragraph_records_impl=merge_paragraph_records_impl,
        clean_text=clean_text,
        block_source_spans=block_source_spans,
        should_merge_paragraph_records=should_merge_paragraph_records,
        table_caption_re=table_caption_re,
    )
    suppress_graphic_display_math_blocks = make_suppress_graphic_display_math_blocks(
        suppress_graphic_display_math_blocks_impl=suppress_graphic_display_math_blocks_impl,
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        paragraph_block_from_graphic_math_entry=paragraph_block_from_graphic_math_entry,
        should_drop_display_math_artifact=should_drop_display_math_artifact,
    )
    suppress_running_header_blocks = make_suppress_running_header_blocks(
        suppress_running_header_blocks_impl=suppress_running_header_blocks_impl,
        block_source_spans=block_source_spans,
        compact_text=compact_text,
        running_header_text_re=running_header_text_re,
        short_word_re=short_word_re,
        strip_known_running_header_text=strip_known_running_header_text,
    )
    normalize_footnote_blocks = make_normalize_footnote_blocks(
        normalize_footnote_blocks_impl=normalize_footnote_blocks_impl,
        block_source_spans=block_source_spans,
        short_word_re=short_word_re,
        starts_like_sentence=starts_like_sentence,
        strip_known_running_header_text=strip_known_running_header_text,
    )
    merge_paragraph_blocks = make_merge_paragraph_blocks(
        merge_paragraph_blocks_impl=merge_paragraph_blocks_impl,
        block_source_spans=block_source_spans,
        should_merge_paragraph_records=should_merge_paragraph_records,
        strip_known_running_header_text=strip_known_running_header_text,
    )
    extract_layout_for_runtime = make_layout_bound_loader(loader=extract_layout, layout=runtime_layout)
    load_external_layout_for_runtime = make_layout_bound_loader(loader=load_external_layout, layout=runtime_layout)
    load_external_math_for_runtime = make_layout_bound_loader(loader=load_external_math, layout=runtime_layout)
    load_mathpix_layout_for_runtime = make_layout_bound_loader(loader=load_mathpix_layout, layout=runtime_layout)
    extract_figures_for_runtime = make_layout_bound_loader(loader=extract_figures, layout=runtime_layout)
    extract_pdftotext_pages_for_runtime = make_layout_bound_loader(loader=extract_pdftotext_pages, layout=runtime_layout)
    section_id_for = make_section_id_for(
        section_id_impl=section_id_impl,
        normalize_title_key=normalize_title_key,
    )
    return run_paper_pipeline_impl(
        paper_id,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        layout_output=layout_output,
        figures=figures,
        extract_layout=extract_layout_for_runtime,
        load_external_layout=load_external_layout_for_runtime,
        merge_native_and_external_layout=merge_native_and_external_layout,
        load_external_math=load_external_math_for_runtime,
        external_math_by_page=external_math_by_page,
        load_mathpix_layout=load_mathpix_layout_for_runtime,
        extract_figures=extract_figures_for_runtime,
        normalize_figure_caption_text=normalize_figure_caption_text,
        merge_layout_and_figure_records=merge_layout_and_figure_records,
        inject_external_math_records=inject_external_math_records,
        mark_records_with_external_math_overlap=mark_records_with_external_math_overlap,
        repair_record_text_with_mathpix_hints=repair_record_text_with_mathpix_hints,
        pdftotext_available=pdftotext_available,
        repair_record_text_with_pdftotext=repair_record_text_with_pdftotext,
        extract_pdftotext_pages=extract_pdftotext_pages_for_runtime,
        page_height_map=page_height_map,
        promote_heading_like_records=promote_heading_like_records,
        merge_math_fragment_records=merge_math_fragment_records,
        page_one_front_matter_records=page_one_front_matter_records,
        is_title_page_metadata_record=is_title_page_metadata_record,
        build_section_tree=build_section_tree,
        build_front_matter=build_front_matter,
        attach_orphan_numbered_roots=attach_orphan_numbered_roots,
        split_late_prelude_for_missing_intro=split_late_prelude_for_missing_intro,
        normalize_section_title=normalize_section_title,
        leading_abstract_text=leading_abstract_text,
        front_block_text=front_block_text,
        default_review=default_review,
        block_source_spans=block_source_spans,
        build_abstract_decision=build_abstract_decision,
        should_replace_front_matter_abstract=should_replace_front_matter_abstract,
        recover_missing_front_matter_abstract=recover_missing_front_matter_abstract,
        section_node_type=section_node_type,
        figure_label_token=figure_label_token,
        prepare_section_nodes=prepare_section_nodes,
        split_trailing_reference_records=split_trailing_reference_records,
        extract_reference_records_from_tail_section=extract_reference_records_from_tail_section,
        reference_records_from_mathpix_layout=reference_records_from_mathpix_layout,
        materialize_sections=materialize_sections,
        section_id_for=section_id_for,
        merge_reference_records=merge_reference_records,
        is_figure_debris=is_figure_debris,
        looks_like_running_header_record=looks_like_running_header_record,
        looks_like_table_body_debris=looks_like_table_body_debris,
        is_short_ocr_fragment=is_short_ocr_fragment,
        suppress_embedded_table_headings=suppress_embedded_table_headings,
        merge_code_records=merge_code_records,
        merge_paragraph_records=merge_paragraph_records,
        build_blocks_for_record=build_blocks_for_record,
        clean_text=clean_text,
        compile_formulas=compile_formulas,
        annotate_formula_classifications=annotate_formula_classifications,
        annotate_formula_semantic_expr=annotate_formula_semantic_expr,
        suppress_graphic_display_math_blocks=suppress_graphic_display_math_blocks,
        suppress_running_header_blocks=suppress_running_header_blocks,
        normalize_footnote_blocks=normalize_footnote_blocks,
        merge_paragraph_blocks=merge_paragraph_blocks,
        now_iso=now_iso,
        build_canonical_document=build_canonical_document,
        config=config,
        state=state,
    )


def make_recover_missing_front_matter_abstract(
    *,
    recover_missing_front_matter_abstract_impl: Callable[..., bool],
    front_block_text: Callable[[list[dict[str, Any]], str | None], str],
    abstract_quality_flags: Callable[[str], list[str]],
    normalize_section_title: Callable[[str], str],
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]],
    abstract_text_is_recoverable: Callable[[str], bool],
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool],
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
) -> Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[Any]], bool]:
    def recover_missing_front_matter_abstract(
        front_matter: dict[str, Any],
        blocks: list[dict[str, Any]],
        prelude: list[dict[str, Any]],
        ordered_roots: list[Any],
    ) -> bool:
        return recover_missing_front_matter_abstract_impl(
            front_matter,
            blocks,
            prelude,
            ordered_roots,
            front_block_text=front_block_text,
            abstract_quality_flags=abstract_quality_flags,
            normalize_section_title=normalize_section_title,
            leading_abstract_text=leading_abstract_text,
            abstract_text_is_recoverable=abstract_text_is_recoverable,
            replace_front_matter_abstract_text=replace_front_matter_abstract_text,
            opening_abstract_candidate_records=opening_abstract_candidate_records,
            normalize_abstract_candidate_text=normalize_abstract_candidate_text,
        )

    return recover_missing_front_matter_abstract


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
