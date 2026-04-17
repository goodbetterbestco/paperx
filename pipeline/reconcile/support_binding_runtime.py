from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.runtime_support import (
    block_source_spans as support_block_source_spans,
    mathish_ratio as support_mathish_ratio,
    normalize_formula_display_text as support_normalize_formula_display_text,
    now_iso as support_now_iso,
    page_height_map as support_page_height_map,
)
from pipeline.reconcile.layout_records import (
    normalize_figure_caption_text as layout_normalize_figure_caption_text,
)
from pipeline.reconcile.text_cleaning import (
    clean_record as text_clean_record,
    clean_text as text_clean_text,
    is_pdftotext_candidate_better as text_is_pdftotext_candidate_better,
    normalize_paragraph_text as text_normalize_paragraph_text,
    record_analysis_text as text_record_analysis_text,
    strip_known_running_header_text as text_strip_known_running_header_text,
    word_count as text_word_count,
)


now_iso = support_now_iso
block_source_spans = support_block_source_spans
page_height_map = support_page_height_map


def make_clean_text(
    *,
    control_char_re: Any,
    compact_text: Callable[[str], str],
) -> Callable[[str], str]:
    def clean_text(text: str) -> str:
        return text_clean_text(
            text,
            control_char_re=control_char_re,
            compact_text=compact_text,
        )

    return clean_text


def make_strip_known_running_header_text(
    *,
    procedia_running_header_re: Any,
    clean_text: Callable[[str], str],
) -> Callable[[str], str]:
    def strip_known_running_header_text(text: str) -> str:
        return text_strip_known_running_header_text(
            text,
            procedia_running_header_re=procedia_running_header_re,
            clean_text=clean_text,
        )

    return strip_known_running_header_text


def make_clean_record(
    *,
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def clean_record(record: dict[str, Any]) -> dict[str, Any]:
        return text_clean_record(
            record,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return clean_record


def make_normalize_paragraph_text(
    *,
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
        return text_normalize_paragraph_text(
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


def make_normalize_formula_display_text(
    *,
    clean_text: Callable[[str], str],
    decode_ocr_codepoint_tokens: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def normalize_formula_display_text(text: str) -> str:
        return support_normalize_formula_display_text(
            text,
            clean_text=clean_text,
            decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
        )

    return normalize_formula_display_text


def make_normalize_figure_caption_text(
    *,
    clean_text: Callable[[str], str],
    normalize_prose_text: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def normalize_figure_caption_text(text: str) -> str:
        return layout_normalize_figure_caption_text(
            text,
            clean_text=clean_text,
            normalize_prose_text=normalize_prose_text,
        )

    return normalize_figure_caption_text


def make_record_analysis_text(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[dict[str, Any]], str]:
    def record_analysis_text(record: dict[str, Any]) -> str:
        return text_record_analysis_text(
            record,
            clean_text=clean_text,
        )

    return record_analysis_text


def make_word_count(
    *,
    short_word_re: Any,
) -> Callable[[str], int]:
    def word_count(text: str) -> int:
        return text_word_count(
            text,
            short_word_re=short_word_re,
        )

    return word_count


def make_mathish_ratio(
    *,
    word_count: Callable[[str], int],
    math_signal_count: Callable[[str], int],
) -> Callable[[str], float]:
    def mathish_ratio(text: str) -> float:
        return support_mathish_ratio(
            text,
            word_count=word_count,
            math_signal_count=math_signal_count,
        )

    return mathish_ratio


def make_is_pdftotext_candidate_better(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
) -> Callable[[str, str, str], bool]:
    def is_pdftotext_candidate_better(original_text: str, candidate_text: str, record_type: str) -> bool:
        return text_is_pdftotext_candidate_better(
            original_text,
            candidate_text,
            record_type,
            clean_text=clean_text,
            word_count=word_count,
        )

    return is_pdftotext_candidate_better
