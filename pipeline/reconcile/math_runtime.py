from __future__ import annotations

from typing import Any, Callable


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


def make_math_entry_looks_like_prose(
    *,
    math_entry_looks_like_prose_impl: Callable[..., bool],
    normalize_paragraph_text: Callable[[str], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
) -> Callable[[dict[str, Any]], bool]:
    def math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
        return math_entry_looks_like_prose_impl(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            word_count=word_count,
        )

    return math_entry_looks_like_prose


def make_should_demote_prose_math_entry_to_paragraph(
    *,
    should_demote_prose_math_entry_to_paragraph_impl: Callable[..., bool],
    normalize_paragraph_text: Callable[[str], str],
    word_count: Callable[[str], int],
    strong_operator_count: Callable[[str], int],
    mathish_ratio: Callable[[str], float],
    math_entry_looks_like_prose: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_prose_math_entry_to_paragraph_impl(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            word_count=word_count,
            strong_operator_count=strong_operator_count,
            mathish_ratio=mathish_ratio,
            math_entry_looks_like_prose=math_entry_looks_like_prose,
            math_entry_semantic_policy=math_entry_semantic_policy,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
        )

    return should_demote_prose_math_entry_to_paragraph


def make_should_demote_graphic_math_entry_to_paragraph(
    *,
    should_demote_graphic_math_entry_to_paragraph_impl: Callable[..., bool],
    should_demote_prose_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_graphic_math_entry_to_paragraph_impl(
            entry,
            should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
        )

    return should_demote_graphic_math_entry_to_paragraph


def make_should_drop_display_math_artifact(
    *,
    should_drop_display_math_artifact_impl: Callable[..., bool],
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
        return should_drop_display_math_artifact_impl(
            entry,
            should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
            group_entry_items_are_graphic_only=group_entry_items_are_graphic_only,
            math_entry_semantic_policy=math_entry_semantic_policy,
            math_entry_category=math_entry_category,
        )

    return should_drop_display_math_artifact


def make_paragraph_block_from_graphic_math_entry(
    *,
    paragraph_block_from_graphic_math_entry_impl: Callable[..., tuple[dict[str, Any] | None, list[dict[str, Any]]]],
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[..., Any],
    repair_symbolic_ocr_spans: Callable[..., Any],
    extract_general_inline_math_spans: Callable[..., Any],
    merge_inline_math_relation_suffixes: Callable[..., Any],
    normalize_inline_math_spans: Callable[..., Any],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], dict[str, Any], dict[str, int]], tuple[dict[str, Any] | None, list[dict[str, Any]]]]:
    def paragraph_block_from_graphic_math_entry(
        block: dict[str, Any],
        math_entry: dict[str, Any],
        counters: dict[str, int],
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        return paragraph_block_from_graphic_math_entry_impl(
            block,
            math_entry,
            counters,
            normalize_paragraph_text=normalize_paragraph_text,
            split_inline_math=split_inline_math,
            repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=normalize_inline_math_spans,
            default_review=default_review,
        )

    return paragraph_block_from_graphic_math_entry


def build_reconcile_math_runtime_helpers(
    *,
    bindings: Any,
    text_helpers: dict[str, Any],
) -> dict[str, Any]:
    math_entry_looks_like_prose = make_math_entry_looks_like_prose(
        math_entry_looks_like_prose_impl=bindings.math_entry_looks_like_prose_impl,
        normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
        looks_like_prose_math_fragment=bindings.looks_like_prose_math_fragment,
        word_count=bindings.word_count,
    )
    should_demote_prose_math_entry_to_paragraph = make_should_demote_prose_math_entry_to_paragraph(
        should_demote_prose_math_entry_to_paragraph_impl=bindings.should_demote_prose_math_entry_to_paragraph_impl,
        normalize_paragraph_text=text_helpers["normalize_paragraph_text"],
        word_count=bindings.word_count,
        strong_operator_count=bindings.strong_operator_count,
        mathish_ratio=bindings.mathish_ratio,
        math_entry_looks_like_prose=math_entry_looks_like_prose,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
    )
    should_demote_graphic_math_entry_to_paragraph = make_should_demote_graphic_math_entry_to_paragraph(
        should_demote_graphic_math_entry_to_paragraph_impl=bindings.should_demote_graphic_math_entry_to_paragraph_impl,
        should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
    )
    should_drop_display_math_artifact = make_should_drop_display_math_artifact(
        should_drop_display_math_artifact_impl=bindings.should_drop_display_math_artifact_impl,
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        group_entry_items_are_graphic_only=bindings.group_entry_items_are_graphic_only,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        math_entry_category=bindings.math_entry_category,
    )
    paragraph_block_from_graphic_math_entry = make_paragraph_block_from_graphic_math_entry(
        paragraph_block_from_graphic_math_entry_impl=bindings.paragraph_block_from_graphic_math_entry_impl,
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
