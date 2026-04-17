from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.section_filters import (
    ends_like_clause_lead_in as filter_ends_like_clause_lead_in,
    ends_like_short_lead_in as filter_ends_like_short_lead_in,
    is_paragraph_like_record as filter_is_paragraph_like_record,
    looks_like_running_header_record as filter_looks_like_running_header_record,
    looks_like_same_page_column_continuation as filter_looks_like_same_page_column_continuation,
    looks_like_table_body_debris as filter_looks_like_table_body_debris,
    merge_anchor_spans as filter_merge_anchor_spans,
    should_merge_paragraph_records as filter_should_merge_paragraph_records,
    starts_like_paragraph_continuation as filter_starts_like_paragraph_continuation,
    starts_like_sentence as filter_starts_like_sentence,
    starts_like_strong_paragraph_continuation as filter_starts_like_strong_paragraph_continuation,
    suppress_embedded_table_headings as filter_suppress_embedded_table_headings,
)


starts_like_sentence = filter_starts_like_sentence
is_paragraph_like_record = filter_is_paragraph_like_record
looks_like_same_page_column_continuation = filter_looks_like_same_page_column_continuation


def make_starts_like_paragraph_continuation(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def starts_like_paragraph_continuation(text: str) -> bool:
        return filter_starts_like_paragraph_continuation(
            text,
            clean_text=clean_text,
        )

    return starts_like_paragraph_continuation


def make_starts_like_strong_paragraph_continuation(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def starts_like_strong_paragraph_continuation(text: str) -> bool:
        return filter_starts_like_strong_paragraph_continuation(
            text,
            clean_text=clean_text,
        )

    return starts_like_strong_paragraph_continuation


def make_ends_like_short_lead_in(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def ends_like_short_lead_in(text: str) -> bool:
        return filter_ends_like_short_lead_in(
            text,
            clean_text=clean_text,
        )

    return ends_like_short_lead_in


def make_ends_like_clause_lead_in(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def ends_like_clause_lead_in(text: str) -> bool:
        return filter_ends_like_clause_lead_in(
            text,
            clean_text=clean_text,
        )

    return ends_like_clause_lead_in


def make_merge_anchor_spans(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def merge_anchor_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
        return filter_merge_anchor_spans(
            record,
            block_source_spans=block_source_spans,
        )

    return merge_anchor_spans


def make_looks_like_running_header_record(
    *,
    clean_text: Callable[[str], str],
    running_header_text_re: Any,
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], bool]:
    def looks_like_running_header_record(record: dict[str, Any]) -> bool:
        return filter_looks_like_running_header_record(
            record,
            clean_text=clean_text,
            running_header_text_re=running_header_text_re,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
        )

    return looks_like_running_header_record


def make_looks_like_table_body_debris(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], bool]:
    def looks_like_table_body_debris(record: dict[str, Any]) -> bool:
        return filter_looks_like_table_body_debris(
            record,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
        )

    return looks_like_table_body_debris


def make_suppress_embedded_table_headings(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    table_caption_re: Any,
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def suppress_embedded_table_headings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return filter_suppress_embedded_table_headings(
            records,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            table_caption_re=table_caption_re,
            parse_heading_label=parse_heading_label,
            clean_heading_title=clean_heading_title,
        )

    return suppress_embedded_table_headings


def make_should_merge_paragraph_records(
    *,
    clean_text: Callable[[str], str],
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    terminal_punctuation_re: Any,
) -> Callable[[dict[str, Any], dict[str, Any]], bool]:
    def should_merge_paragraph_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
        return filter_should_merge_paragraph_records(
            previous,
            current,
            clean_text=clean_text,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
            terminal_punctuation_re=terminal_punctuation_re,
        )

    return should_merge_paragraph_records
