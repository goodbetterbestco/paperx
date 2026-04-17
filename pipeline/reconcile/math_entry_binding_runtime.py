from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.math_entry_policies import (
    group_entry_items_are_graphic_only as policy_group_entry_items_are_graphic_only,
    math_entry_category as policy_math_entry_category,
    math_entry_looks_like_prose as policy_math_entry_looks_like_prose,
    math_entry_semantic_policy as policy_math_entry_semantic_policy,
    paragraph_block_from_graphic_math_entry as policy_paragraph_block_from_graphic_math_entry,
    should_demote_graphic_math_entry_to_paragraph as policy_should_demote_graphic_math_entry_to_paragraph,
    should_demote_prose_math_entry_to_paragraph as policy_should_demote_prose_math_entry_to_paragraph,
    should_drop_display_math_artifact as policy_should_drop_display_math_artifact,
)


math_entry_semantic_policy = policy_math_entry_semantic_policy
math_entry_category = policy_math_entry_category


def make_group_entry_items_are_graphic_only(
    *,
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def group_entry_items_are_graphic_only(entry: dict[str, Any]) -> bool:
        return policy_group_entry_items_are_graphic_only(
            entry,
            math_entry_semantic_policy=math_entry_semantic_policy,
        )

    return group_entry_items_are_graphic_only


def make_math_entry_looks_like_prose(
    *,
    normalize_paragraph_text: Callable[[str], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
) -> Callable[[dict[str, Any]], bool]:
    def math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
        return policy_math_entry_looks_like_prose(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            word_count=word_count,
        )

    return math_entry_looks_like_prose


def make_should_demote_prose_math_entry_to_paragraph(
    *,
    normalize_paragraph_text: Callable[[str], str],
    word_count: Callable[[str], int],
    strong_operator_count: Callable[[str], int],
    mathish_ratio: Callable[[str], float],
    math_entry_looks_like_prose: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return policy_should_demote_prose_math_entry_to_paragraph(
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
    should_demote_prose_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
) -> Callable[[dict[str, Any]], bool]:
    def should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return policy_should_demote_graphic_math_entry_to_paragraph(
            entry,
            should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
        )

    return should_demote_graphic_math_entry_to_paragraph


def make_should_drop_display_math_artifact(
    *,
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
        return policy_should_drop_display_math_artifact(
            entry,
            should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
            group_entry_items_are_graphic_only=group_entry_items_are_graphic_only,
            math_entry_semantic_policy=math_entry_semantic_policy,
            math_entry_category=math_entry_category,
        )

    return should_drop_display_math_artifact


def make_paragraph_block_from_graphic_math_entry(
    *,
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[..., Any],
    repair_symbolic_ocr_spans: Callable[..., Any],
    extract_general_inline_math_spans: Callable[..., Any],
    merge_inline_math_relation_suffixes: Callable[..., Any],
    normalize_inline_math_spans: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], dict[str, Any], dict[str, int]], tuple[dict[str, Any] | None, list[dict[str, Any]]]]:
    def paragraph_block_from_graphic_math_entry(
        block: dict[str, Any],
        math_entry: dict[str, Any],
        counters: dict[str, int],
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        return policy_paragraph_block_from_graphic_math_entry(
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
