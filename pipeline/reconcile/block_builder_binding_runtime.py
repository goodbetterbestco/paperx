from __future__ import annotations

from typing import Any, Callable

from pipeline.assembly.record_block_builder import (
    list_item_marker as builder_list_item_marker,
    looks_like_real_code_record as builder_looks_like_real_code_record,
)
from pipeline.reconcile.external_math import (
    match_external_math_entry as external_match_external_math_entry,
    rect_area as external_rect_area,
    rect_intersection_area as external_rect_intersection_area,
)


rect_intersection_area = external_rect_intersection_area
rect_area = external_rect_area


def make_list_item_marker(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], tuple[str | None, bool, str]]:
    def list_item_marker(text: str) -> tuple[str | None, bool, str]:
        return builder_list_item_marker(
            text,
            clean_text=clean_text,
        )

    return list_item_marker


def make_looks_like_real_code_record(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def looks_like_real_code_record(text: str) -> bool:
        return builder_looks_like_real_code_record(
            text,
            clean_text=clean_text,
        )

    return looks_like_real_code_record


def make_match_external_math_entry(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], dict[str, Any] | None]:
    def match_external_math_entry(
        record: dict[str, Any],
        external_math_by_page: dict[int, list[dict[str, Any]]],
    ) -> dict[str, Any] | None:
        return external_match_external_math_entry(
            record,
            external_math_by_page,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
        )

    return match_external_math_entry
