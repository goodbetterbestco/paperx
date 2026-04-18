from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pipeline.reconcile.reference_runtime import (
    extract_reference_records_from_tail_section as reference_extract_reference_records_from_tail_section_runtime,
    is_reference_start as reference_is_reference_start_runtime,
    looks_like_reference_text as reference_looks_like_reference_text_runtime,
    make_reference_entry as reference_make_reference_entry_runtime,
    merge_reference_records as reference_merge_reference_records_runtime,
    reference_records_from_mathpix_layout as reference_reference_records_from_mathpix_layout_runtime,
    split_trailing_reference_records as reference_split_trailing_reference_records_runtime,
)


@dataclass(frozen=True)
class BoundReferenceHelpers:
    looks_like_reference_text: Callable[[str], bool]
    is_reference_start: Callable[[dict[str, Any]], bool]
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    split_trailing_reference_records: Callable[
        [list[dict[str, Any]]],
        tuple[list[dict[str, Any]], list[dict[str, Any]]],
    ]
    extract_reference_records_from_tail_section: Callable[
        [list[dict[str, Any]]],
        tuple[list[dict[str, Any]], list[dict[str, Any]]],
    ]
    reference_records_from_mathpix_layout: Callable[[dict[str, Any] | None], list[dict[str, Any]]]


def make_reference_entry(
    *,
    clean_text: Callable[[str], str],
    normalize_reference_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], int], dict[str, Any]]:
    def build_reference_entry(record: dict[str, Any], index: int) -> dict[str, Any]:
        return reference_make_reference_entry_runtime(
            record,
            index,
            clean_text=clean_text,
            normalize_reference_text=normalize_reference_text,
            block_source_spans=block_source_spans,
            default_review=default_review,
        )

    return build_reference_entry


def make_looks_like_reference_text(
    *,
    clean_text: Callable[[str], str],
    reference_year_re: Any,
    reference_venue_re: Any,
    reference_author_re: Any,
    short_word_re: Any,
) -> Callable[[str], bool]:
    def looks_like_reference_text(text: str) -> bool:
        return reference_looks_like_reference_text_runtime(
            text,
            clean_text=clean_text,
            reference_year_re=reference_year_re,
            reference_venue_re=reference_venue_re,
            reference_author_re=reference_author_re,
            short_word_re=short_word_re,
        )

    return looks_like_reference_text


def make_is_reference_start(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    reference_start_re: Any,
    looks_like_reference_text: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def is_reference_start(record: dict[str, Any]) -> bool:
        return reference_is_reference_start_runtime(
            record,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            reference_start_re=reference_start_re,
            looks_like_reference_text=looks_like_reference_text,
        )

    return is_reference_start


def make_merge_reference_records(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    is_reference_start: Callable[[dict[str, Any]], bool],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def merge_reference_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return reference_merge_reference_records_runtime(
            records,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            is_reference_start=is_reference_start,
        )

    return merge_reference_records


def make_split_trailing_reference_records(
    *,
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def split_trailing_reference_records(
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return reference_split_trailing_reference_records_runtime(
            records,
            looks_like_reference_text=looks_like_reference_text,
            merge_reference_records=merge_reference_records,
        )

    return split_trailing_reference_records


def make_extract_reference_records_from_tail_section(
    *,
    clean_text: Callable[[str], str],
    about_author_re: Any,
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def extract_reference_records_from_tail_section(
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return reference_extract_reference_records_from_tail_section_runtime(
            records,
            clean_text=clean_text,
            about_author_re=about_author_re,
            looks_like_reference_text=looks_like_reference_text,
            merge_reference_records=merge_reference_records,
        )

    return extract_reference_records_from_tail_section


def make_reference_records_from_mathpix_layout(
    *,
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    layout_record: Callable[[Any], dict[str, Any]],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any] | None], list[dict[str, Any]]]:
    def reference_records_from_mathpix_layout(
        layout: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return reference_reference_records_from_mathpix_layout_runtime(
            layout,
            mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            layout_record=layout_record,
            merge_reference_records=merge_reference_records,
        )

    return reference_records_from_mathpix_layout


def make_bound_reference_helpers(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    reference_start_re: Any,
    reference_year_re: Any,
    reference_venue_re: Any,
    reference_author_re: Any,
    short_word_re: Any,
    about_author_re: Any,
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    normalize_title_key: Callable[[str], str],
    layout_record: Callable[[Any], dict[str, Any]],
) -> BoundReferenceHelpers:
    looks_like_reference_text = make_looks_like_reference_text(
        clean_text=clean_text,
        reference_year_re=reference_year_re,
        reference_venue_re=reference_venue_re,
        reference_author_re=reference_author_re,
        short_word_re=short_word_re,
    )
    is_reference_start = make_is_reference_start(
        clean_text=clean_text,
        block_source_spans=block_source_spans,
        reference_start_re=reference_start_re,
        looks_like_reference_text=looks_like_reference_text,
    )
    merge_reference_records = make_merge_reference_records(
        clean_text=clean_text,
        block_source_spans=block_source_spans,
        is_reference_start=is_reference_start,
    )
    split_trailing_reference_records = make_split_trailing_reference_records(
        looks_like_reference_text=looks_like_reference_text,
        merge_reference_records=merge_reference_records,
    )
    extract_reference_records_from_tail_section = make_extract_reference_records_from_tail_section(
        clean_text=clean_text,
        about_author_re=about_author_re,
        looks_like_reference_text=looks_like_reference_text,
        merge_reference_records=merge_reference_records,
    )
    reference_records_from_mathpix_layout = make_reference_records_from_mathpix_layout(
        mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
        layout_record=layout_record,
        merge_reference_records=merge_reference_records,
    )
    return BoundReferenceHelpers(
        looks_like_reference_text=looks_like_reference_text,
        is_reference_start=is_reference_start,
        merge_reference_records=merge_reference_records,
        split_trailing_reference_records=split_trailing_reference_records,
        extract_reference_records_from_tail_section=extract_reference_records_from_tail_section,
        reference_records_from_mathpix_layout=reference_records_from_mathpix_layout,
    )
