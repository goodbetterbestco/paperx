from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pipeline.reconcile.screening import (
    is_figure_debris,
    is_short_ocr_fragment,
    looks_like_browser_ui_scrap,
    looks_like_glyph_noise_cloud,
    looks_like_quoted_identifier_fragment,
    looks_like_table_marker_cloud,
    looks_like_vertical_label_cloud,
    make_is_figure_debris,
    make_is_short_ocr_fragment,
    make_looks_like_browser_ui_scrap,
    make_looks_like_glyph_noise_cloud,
    make_looks_like_quoted_identifier_fragment,
    make_looks_like_table_marker_cloud,
    make_looks_like_vertical_label_cloud,
)
from pipeline.reconcile.section_filters import (
    make_looks_like_running_header_record,
    make_looks_like_table_body_debris,
    make_should_merge_paragraph_records,
    make_suppress_embedded_table_headings,
)


@dataclass(frozen=True)
class BoundReconcileScreeningHelpers:
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool]
    is_figure_debris: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], bool]
    looks_like_running_header_record: Callable[[dict[str, Any]], bool]
    looks_like_table_body_debris: Callable[[dict[str, Any]], bool]
    suppress_embedded_table_headings: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool]


def build_reconcile_screening_helpers(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    short_word_re: Any,
    quoted_identifier_fragment_re: Any,
    label_cloud_token_re: Any,
    short_ocr_noise_re: Any,
    terminal_punctuation_re: Any,
    strong_operator_count: Callable[[str], int],
    diagram_decision_re: Any,
    diagram_query_re: Any,
    diagram_action_re: Any,
    rect_intersection_area: Callable[[dict[str, Any], dict[str, Any]], float],
    running_header_text_re: Any,
    table_caption_re: Any,
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
) -> BoundReconcileScreeningHelpers:
    looks_like_browser_ui_scrap_fn = make_looks_like_browser_ui_scrap(
        short_word_re=short_word_re,
    )
    looks_like_quoted_identifier_fragment_fn = make_looks_like_quoted_identifier_fragment(
        short_word_re=short_word_re,
        quoted_identifier_fragment_re=quoted_identifier_fragment_re,
    )
    looks_like_glyph_noise_cloud_fn = make_looks_like_glyph_noise_cloud(
        short_word_re=short_word_re,
    )
    looks_like_vertical_label_cloud_fn = make_looks_like_vertical_label_cloud(
        strong_operator_count=strong_operator_count,
    )
    looks_like_table_marker_cloud_fn = make_looks_like_table_marker_cloud(
        strong_operator_count=strong_operator_count,
    )
    return BoundReconcileScreeningHelpers(
        is_short_ocr_fragment=make_is_short_ocr_fragment(
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            looks_like_browser_ui_scrap=looks_like_browser_ui_scrap_fn,
            looks_like_quoted_identifier_fragment=looks_like_quoted_identifier_fragment_fn,
            looks_like_glyph_noise_cloud=looks_like_glyph_noise_cloud_fn,
            looks_like_vertical_label_cloud=looks_like_vertical_label_cloud_fn,
            looks_like_table_marker_cloud=looks_like_table_marker_cloud_fn,
            short_word_re=short_word_re,
            label_cloud_token_re=label_cloud_token_re,
            short_ocr_noise_re=short_ocr_noise_re,
            terminal_punctuation_re=terminal_punctuation_re,
            strong_operator_count=strong_operator_count,
        ),
        is_figure_debris=make_is_figure_debris(
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            diagram_decision_re=diagram_decision_re,
            diagram_query_re=diagram_query_re,
            diagram_action_re=diagram_action_re,
            terminal_punctuation_re=terminal_punctuation_re,
            short_word_re=short_word_re,
            rect_intersection_area=rect_intersection_area,
        ),
        looks_like_running_header_record=make_looks_like_running_header_record(
            clean_text=clean_text,
            running_header_text_re=running_header_text_re,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
        ),
        looks_like_table_body_debris=make_looks_like_table_body_debris(
            clean_text=clean_text,
            block_source_spans=block_source_spans,
        ),
        suppress_embedded_table_headings=make_suppress_embedded_table_headings(
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            table_caption_re=table_caption_re,
            parse_heading_label=parse_heading_label,
            clean_heading_title=clean_heading_title,
        ),
        should_merge_paragraph_records=make_should_merge_paragraph_records(
            clean_text=clean_text,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
            terminal_punctuation_re=terminal_punctuation_re,
        ),
    )


__all__ = [
    "BoundReconcileScreeningHelpers",
    "build_reconcile_screening_helpers",
    "is_figure_debris",
    "is_short_ocr_fragment",
    "looks_like_browser_ui_scrap",
    "looks_like_glyph_noise_cloud",
    "looks_like_quoted_identifier_fragment",
    "looks_like_table_marker_cloud",
    "looks_like_vertical_label_cloud",
    "make_is_figure_debris",
    "make_is_short_ocr_fragment",
    "make_looks_like_browser_ui_scrap",
    "make_looks_like_glyph_noise_cloud",
    "make_looks_like_quoted_identifier_fragment",
    "make_looks_like_table_marker_cloud",
    "make_looks_like_vertical_label_cloud",
]
