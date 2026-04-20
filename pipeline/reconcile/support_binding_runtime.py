from __future__ import annotations

from pipeline.reconcile.layout_records import make_normalize_figure_caption_text
from pipeline.reconcile.runtime_support import (
    block_source_spans,
    make_mathish_ratio,
    make_normalize_formula_display_text,
    mathish_ratio,
    normalize_formula_display_text,
    now_iso,
    page_height_map,
)
from pipeline.reconcile.text_cleaning import (
    clean_record,
    clean_text,
    is_pdftotext_candidate_better,
    make_clean_record,
    make_clean_text,
    make_is_pdftotext_candidate_better,
    make_normalize_paragraph_text,
    make_record_analysis_text,
    make_strip_known_running_header_text,
    make_word_count,
    normalize_paragraph_text,
    record_analysis_text,
    strip_known_running_header_text,
    word_count,
)


__all__ = [
    "block_source_spans",
    "clean_record",
    "clean_text",
    "is_pdftotext_candidate_better",
    "make_clean_record",
    "make_clean_text",
    "make_is_pdftotext_candidate_better",
    "make_mathish_ratio",
    "make_normalize_figure_caption_text",
    "make_normalize_formula_display_text",
    "make_normalize_paragraph_text",
    "make_record_analysis_text",
    "make_strip_known_running_header_text",
    "make_word_count",
    "mathish_ratio",
    "normalize_formula_display_text",
    "normalize_paragraph_text",
    "now_iso",
    "page_height_map",
    "record_analysis_text",
    "strip_known_running_header_text",
    "word_count",
]
