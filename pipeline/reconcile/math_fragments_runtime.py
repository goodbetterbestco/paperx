from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.math_fragments import (
    looks_like_math_fragment as fragments_looks_like_math_fragment,
    math_signal_count as fragments_math_signal_count,
    merge_math_fragment_records as fragments_merge_math_fragment_records,
    strong_operator_count as fragments_strong_operator_count,
)


strong_operator_count = fragments_strong_operator_count


def make_math_signal_count(
    *,
    math_token_re: Any,
) -> Callable[[str], int]:
    def math_signal_count(text: str) -> int:
        return fragments_math_signal_count(
            text,
            math_token_re=math_token_re,
        )

    return math_signal_count


def make_looks_like_math_fragment(
    *,
    record_analysis_text: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    short_word_re: Any,
    math_token_re: Any,
) -> Callable[[dict[str, Any]], bool]:
    def looks_like_math_fragment(record: dict[str, Any]) -> bool:
        return fragments_looks_like_math_fragment(
            record,
            record_analysis_text=record_analysis_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            short_word_re=short_word_re,
            math_token_re=math_token_re,
        )

    return looks_like_math_fragment


def make_merge_math_fragment_records(
    *,
    looks_like_math_fragment: Callable[[dict[str, Any]], bool],
    clean_text: Callable[[str], str],
    record_analysis_text: Callable[[dict[str, Any]], str],
    math_signal_count: Callable[[str], int],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def merge_math_fragment_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return fragments_merge_math_fragment_records(
            records,
            looks_like_math_fragment=looks_like_math_fragment,
            clean_text=clean_text,
            record_analysis_text=record_analysis_text,
            math_signal_count=math_signal_count,
            block_source_spans=block_source_spans,
        )

    return merge_math_fragment_records
