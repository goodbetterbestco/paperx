from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.text_repairs import (
    inline_tex_signal_count as repair_inline_tex_signal_count,
    is_mathpix_text_hint_better as repair_is_mathpix_text_hint_better,
    looks_like_truncated_prose_lead as repair_looks_like_truncated_prose_lead,
    matching_mathpix_text_blocks as repair_matching_mathpix_text_blocks,
    mathpix_hint_alignment_text as repair_mathpix_hint_alignment_text,
    mathpix_hint_tokens as repair_mathpix_hint_tokens,
    mathpix_prose_lead_repair_candidate as repair_mathpix_prose_lead_repair_candidate,
    mathpix_text_blocks_by_page as repair_mathpix_text_blocks_by_page,
    mathpix_text_candidate_score as repair_mathpix_text_candidate_score,
    mathpix_text_hint_candidate as repair_mathpix_text_hint_candidate,
    record_union_bbox as repair_record_union_bbox,
    repair_record_text_with_pdftotext as repair_repair_record_text_with_pdftotext,
    should_skip_pdftotext_repair as repair_should_skip_pdftotext_repair,
    token_subsequence_index as repair_token_subsequence_index,
)


def make_should_skip_pdftotext_repair(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_math_re: Any,
) -> Callable[[dict[str, Any]], bool]:
    def should_skip_pdftotext_repair(record: dict[str, Any]) -> bool:
        return repair_should_skip_pdftotext_repair(
            record,
            clean_text=clean_text,
            word_count=word_count,
            inline_math_re=inline_math_re,
        )

    return should_skip_pdftotext_repair


def make_repair_record_text_with_pdftotext(
    *,
    should_skip_pdftotext_repair: Callable[[dict[str, Any]], bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    bbox_to_line_window: Callable[..., tuple[int, int]],
    slice_page_text: Callable[..., str],
    clean_text: Callable[[str], str],
    is_pdftotext_candidate_better: Callable[[str, str, str], bool],
) -> Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]]:
    def repair_record_text_with_pdftotext(
        records: list[dict[str, Any]],
        pdftotext_pages: dict[int, list[str]],
        page_heights: dict[int, float],
    ) -> list[dict[str, Any]]:
        return repair_repair_record_text_with_pdftotext(
            records,
            pdftotext_pages,
            page_heights,
            should_skip_pdftotext_repair=should_skip_pdftotext_repair,
            block_source_spans=block_source_spans,
            bbox_to_line_window=bbox_to_line_window,
            slice_page_text=slice_page_text,
            clean_text=clean_text,
            is_pdftotext_candidate_better=is_pdftotext_candidate_better,
        )

    return repair_record_text_with_pdftotext


def make_record_union_bbox(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], tuple[int, dict[str, float]] | None]:
    def record_union_bbox(record: dict[str, Any]) -> tuple[int, dict[str, float]] | None:
        return repair_record_union_bbox(
            record,
            block_source_spans=block_source_spans,
        )

    return record_union_bbox


def make_mathpix_hint_alignment_text(
    *,
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Any,
    display_math_start_re: Any,
    math_signal_count: Callable[[str], int],
    word_count: Callable[[str], int],
) -> Callable[[str], str]:
    def mathpix_hint_alignment_text(text: str) -> str:
        return repair_mathpix_hint_alignment_text(
            text,
            clean_text=clean_text,
            display_math_prose_cue_re=display_math_prose_cue_re,
            display_math_start_re=display_math_start_re,
            math_signal_count=math_signal_count,
            word_count=word_count,
        )

    return mathpix_hint_alignment_text


def make_mathpix_hint_tokens(
    *,
    hint_token_re: Any,
) -> Callable[[str], list[str]]:
    def mathpix_hint_tokens(text: str) -> list[str]:
        return repair_mathpix_hint_tokens(
            text,
            hint_token_re=hint_token_re,
        )

    return mathpix_hint_tokens


def make_mathpix_text_candidate_score(
    *,
    mathpix_hint_alignment_text: Callable[[str], str],
    mathpix_hint_tokens: Callable[[str], list[str]],
    inline_tex_signal_count: Callable[[str], int],
) -> Callable[[str, str], tuple[int, int, int, int]]:
    def mathpix_text_candidate_score(
        original_text: str,
        candidate_text: str,
    ) -> tuple[int, int, int, int]:
        return repair_mathpix_text_candidate_score(
            original_text,
            candidate_text,
            mathpix_hint_alignment_text=mathpix_hint_alignment_text,
            mathpix_hint_tokens=mathpix_hint_tokens,
            inline_tex_signal_count=inline_tex_signal_count,
        )

    return mathpix_text_candidate_score


def make_matching_mathpix_text_blocks(
    *,
    record_union_bbox: Callable[[dict[str, Any]], tuple[int, dict[str, float]] | None],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
) -> Callable[[dict[str, Any], dict[int, list[Any]]], list[Any]]:
    def matching_mathpix_text_blocks(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[Any]],
    ) -> list[Any]:
        return repair_matching_mathpix_text_blocks(
            record,
            mathpix_blocks_by_page,
            record_union_bbox=record_union_bbox,
            rect_x_overlap_ratio=rect_x_overlap_ratio,
        )

    return matching_mathpix_text_blocks


def make_mathpix_text_hint_candidate(
    *,
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[Any]]], list[Any]],
    word_count: Callable[[str], int],
    mathpix_hint_alignment_text: Callable[[str], str],
    clean_text: Callable[[str], str],
    mathpix_text_candidate_score: Callable[[str, str], tuple[int, int, int, int]],
) -> Callable[[dict[str, Any], dict[int, list[Any]]], str]:
    def mathpix_text_hint_candidate(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[Any]],
    ) -> str:
        return repair_mathpix_text_hint_candidate(
            record,
            mathpix_blocks_by_page,
            matching_mathpix_text_blocks=matching_mathpix_text_blocks,
            word_count=word_count,
            mathpix_hint_alignment_text=mathpix_hint_alignment_text,
            clean_text=clean_text,
            mathpix_text_candidate_score=mathpix_text_candidate_score,
        )

    return mathpix_text_hint_candidate


def make_looks_like_truncated_prose_lead(
    *,
    clean_text: Callable[[str], str],
    short_word_re: Any,
    truncated_prose_lead_stopwords: set[str],
) -> Callable[[str], bool]:
    def looks_like_truncated_prose_lead(text: str) -> bool:
        return repair_looks_like_truncated_prose_lead(
            text,
            clean_text=clean_text,
            short_word_re=short_word_re,
            truncated_prose_lead_stopwords=truncated_prose_lead_stopwords,
        )

    return looks_like_truncated_prose_lead


def make_mathpix_prose_lead_repair_candidate(
    *,
    clean_text: Callable[[str], str],
    looks_like_truncated_prose_lead: Callable[[str], bool],
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[Any]]], list[Any]],
    short_word_re: Any,
    word_count: Callable[[str], int],
    parse_heading_label: Callable[[str], Any],
    token_subsequence_index: Callable[[list[str], list[str]], int | None],
) -> Callable[[dict[str, Any], dict[int, list[Any]]], str]:
    def mathpix_prose_lead_repair_candidate(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[Any]],
    ) -> str:
        return repair_mathpix_prose_lead_repair_candidate(
            record,
            mathpix_blocks_by_page,
            clean_text=clean_text,
            looks_like_truncated_prose_lead=looks_like_truncated_prose_lead,
            matching_mathpix_text_blocks=matching_mathpix_text_blocks,
            short_word_re=short_word_re,
            word_count=word_count,
            parse_heading_label=parse_heading_label,
            token_subsequence_index=token_subsequence_index,
        )

    return mathpix_prose_lead_repair_candidate


def make_is_mathpix_text_hint_better(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_tex_signal_count: Callable[[str], int],
) -> Callable[[str, str], bool]:
    def is_mathpix_text_hint_better(original_text: str, candidate_text: str) -> bool:
        return repair_is_mathpix_text_hint_better(
            original_text,
            candidate_text,
            clean_text=clean_text,
            word_count=word_count,
            inline_tex_signal_count=inline_tex_signal_count,
        )

    return is_mathpix_text_hint_better


mathpix_text_blocks_by_page = repair_mathpix_text_blocks_by_page
inline_tex_signal_count = repair_inline_tex_signal_count
token_subsequence_index = repair_token_subsequence_index
