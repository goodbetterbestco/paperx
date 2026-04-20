from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.math_entry_policies import (
    make_math_entry_looks_like_prose,
    make_paragraph_block_from_graphic_math_entry,
    make_should_demote_graphic_math_entry_to_paragraph,
    make_should_demote_prose_math_entry_to_paragraph,
    make_should_drop_display_math_artifact,
)


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


def build_reconcile_math_runtime_helpers(
    *,
    bindings: Any,
    text_helpers: dict[str, Any],
) -> dict[str, Any]:
    math_entry_looks_like_prose = make_math_entry_looks_like_prose(
        normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
        looks_like_prose_math_fragment=bindings.looks_like_prose_math_fragment,
        word_count=bindings.word_count,
    )
    should_demote_prose_math_entry_to_paragraph = make_should_demote_prose_math_entry_to_paragraph(
        normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
        word_count=bindings.word_count,
        strong_operator_count=bindings.strong_operator_count,
        mathish_ratio=bindings.mathish_ratio,
        math_entry_looks_like_prose=math_entry_looks_like_prose,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
    )
    should_demote_graphic_math_entry_to_paragraph = make_should_demote_graphic_math_entry_to_paragraph(
        should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
    )
    should_drop_display_math_artifact = make_should_drop_display_math_artifact(
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        group_entry_items_are_graphic_only=bindings.group_entry_items_are_graphic_only,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        math_entry_category=bindings.math_entry_category,
    )
    paragraph_block_from_graphic_math_entry = make_paragraph_block_from_graphic_math_entry(
        normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
        split_inline_math=bindings.split_inline_math,
        repair_symbolic_ocr_spans=bindings.repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=bindings.extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=bindings.merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=bindings.normalize_inline_math_spans,
        default_review=text_helpers["default_review"],
    )
    return {
        "paragraph_block_from_graphic_math_entry": paragraph_block_from_graphic_math_entry,
        "should_demote_graphic_math_entry_to_paragraph": should_demote_graphic_math_entry_to_paragraph,
        "should_drop_display_math_artifact": should_drop_display_math_artifact,
        "match_external_math_entry": make_match_external_math_entry(
            match_external_math_entry_impl=bindings.match_external_math_entry_impl,
            block_source_spans=text_helpers["block_source_spans"],
            clean_text=text_helpers["clean_text"],
        ),
        "overlapping_external_math_entries": make_overlapping_external_math_entries(
            overlapping_external_math_entries_impl=bindings.overlapping_external_math_entries_impl,
            block_source_spans=text_helpers["block_source_spans"],
        ),
        "trim_embedded_display_math_from_paragraph": make_trim_embedded_display_math_from_paragraph(
            trim_embedded_display_math_from_paragraph_impl=bindings.trim_embedded_display_math_from_paragraph_impl,
            block_source_spans=text_helpers["block_source_spans"],
            clean_text=text_helpers["clean_text"],
            display_math_prose_cue_re=bindings.display_math_prose_cue_re,
            display_math_resume_re=bindings.display_math_resume_re,
            display_math_start_re=bindings.display_math_start_re,
            mathish_ratio=bindings.mathish_ratio,
            strong_operator_count=bindings.strong_operator_count,
        ),
        "looks_like_display_math_echo": make_looks_like_display_math_echo(
            looks_like_display_math_echo_impl=bindings.looks_like_display_math_echo_impl,
            block_source_spans=text_helpers["block_source_spans"],
            clean_text=text_helpers["clean_text"],
            mathish_ratio=bindings.mathish_ratio,
            strong_operator_count=bindings.strong_operator_count,
            short_word_re=text_helpers["short_word_re"],
        ),
    }
