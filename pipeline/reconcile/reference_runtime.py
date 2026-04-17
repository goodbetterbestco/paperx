from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.references import (
    extract_reference_records_from_tail_section as reconcile_extract_reference_records_from_tail_section,
    is_reference_start as reconcile_is_reference_start,
    looks_like_reference_text as reconcile_looks_like_reference_text,
    make_reference_entry as reconcile_make_reference_entry,
    merge_reference_records as reconcile_merge_reference_records,
    reference_records_from_mathpix_layout as reconcile_reference_records_from_mathpix_layout,
    split_trailing_reference_records as reconcile_split_trailing_reference_records,
)


def make_reference_entry(
    record: dict[str, Any],
    index: int,
    *,
    clean_text: Callable[[str], str],
    normalize_reference_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    return reconcile_make_reference_entry(
        record,
        index,
        clean_text=clean_text,
        normalize_reference_text=normalize_reference_text,
        block_source_spans=block_source_spans,
        default_review=default_review,
    )


def looks_like_reference_text(
    text: str,
    *,
    clean_text: Callable[[str], str],
    reference_year_re: Any,
    reference_venue_re: Any,
    reference_author_re: Any,
    short_word_re: Any,
) -> bool:
    return reconcile_looks_like_reference_text(
        text,
        clean_text=clean_text,
        reference_year_re=reference_year_re,
        reference_venue_re=reference_venue_re,
        reference_author_re=reference_author_re,
        short_word_re=short_word_re,
    )


def is_reference_start(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    reference_start_re: Any,
    looks_like_reference_text: Callable[[str], bool],
) -> bool:
    return reconcile_is_reference_start(
        record,
        clean_text=clean_text,
        block_source_spans=block_source_spans,
        reference_start_re=reference_start_re,
        looks_like_reference_text=looks_like_reference_text,
    )


def merge_reference_records(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    is_reference_start: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    return reconcile_merge_reference_records(
        records,
        clean_text=clean_text,
        block_source_spans=block_source_spans,
        is_reference_start=is_reference_start,
    )


def split_trailing_reference_records(
    records: list[dict[str, Any]],
    *,
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_split_trailing_reference_records(
        records,
        looks_like_reference_text=looks_like_reference_text,
        merge_reference_records=merge_reference_records,
    )


def extract_reference_records_from_tail_section(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    about_author_re: Any,
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_extract_reference_records_from_tail_section(
        records,
        clean_text=clean_text,
        about_author_re=about_author_re,
        looks_like_reference_text=looks_like_reference_text,
        merge_reference_records=merge_reference_records,
    )


def reference_records_from_mathpix_layout(
    layout: dict[str, Any] | None,
    *,
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    layout_record: Callable[[Any], dict[str, Any]],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return reconcile_reference_records_from_mathpix_layout(
        layout,
        mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
        layout_record=layout_record,
        merge_reference_records=merge_reference_records,
    )
