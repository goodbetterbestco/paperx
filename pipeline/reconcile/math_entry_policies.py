from __future__ import annotations

from typing import Any, Callable


def math_entry_semantic_policy(entry: dict[str, Any]) -> str:
    classification = entry.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("semantic_policy", "graphic_only"))
    return "graphic_only"


def math_entry_category(entry: dict[str, Any]) -> str:
    classification = entry.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("category", "unknown"))
    return "unknown"


def group_entry_items_are_graphic_only(
    entry: dict[str, Any],
    *,
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
) -> bool:
    if str(entry.get("kind", "")) != "group":
        return False
    items = entry.get("items")
    if not isinstance(items, list) or not items:
        return False
    return all(isinstance(item, dict) and math_entry_semantic_policy(item) == "graphic_only" for item in items)


def math_entry_looks_like_prose(
    entry: dict[str, Any],
    *,
    normalize_paragraph_text: Callable[[str], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
) -> bool:
    text = normalize_paragraph_text(str(entry.get("display_latex", "")))
    if not text:
        return False
    if looks_like_prose_paragraph(text) or looks_like_prose_math_fragment(text):
        return True
    lowered = text.lower()
    if word_count(text) >= 8 and lowered.startswith(("if ", "else ", "else if ", "then ", "where ", "let ", "assume ", "suppose ")):
        if text.endswith((".", ":", "=")) or "," in text:
            return True
    return word_count(text) >= 8 and (text.endswith((".", ":")) or text.count(".") >= 1)


def should_demote_prose_math_entry_to_paragraph(
    entry: dict[str, Any],
    *,
    normalize_paragraph_text: Callable[[str], str],
    word_count: Callable[[str], int],
    strong_operator_count: Callable[[str], int],
    mathish_ratio: Callable[[str], float],
    math_entry_looks_like_prose: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
) -> bool:
    if str(entry.get("kind", "")) == "group":
        return False

    text = normalize_paragraph_text(str(entry.get("display_latex", "")))
    if not text:
        return False

    words = word_count(text)
    operators = strong_operator_count(text)
    ratio = mathish_ratio(text)
    prose_like = math_entry_looks_like_prose(entry)

    if not prose_like:
        starts_sentence = bool(text[:1]) and text[:1].isupper()
        if not (words >= 8 and starts_sentence and operators <= 1 and ratio <= 0.2):
            return False

    if math_entry_semantic_policy(entry) == "graphic_only":
        return True

    if words < 8:
        return False
    lowered = text.lower()
    if lowered.startswith(("if ", "else ", "else if ", "then ", "where ", "let ", "assume ", "suppose ")):
        return True
    if looks_like_prose_paragraph(text) and operators == 0:
        return True
    if looks_like_prose_paragraph(text) and operators <= 1 and ratio <= 0.35:
        return True
    if operators <= 1 and ratio <= 0.2:
        return True
    return False


def should_demote_graphic_math_entry_to_paragraph(
    entry: dict[str, Any],
    *,
    should_demote_prose_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
) -> bool:
    return should_demote_prose_math_entry_to_paragraph(entry)


def should_drop_display_math_artifact(
    entry: dict[str, Any],
    *,
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
) -> bool:
    if should_demote_graphic_math_entry_to_paragraph(entry):
        return False
    if group_entry_items_are_graphic_only(entry):
        return True
    if math_entry_semantic_policy(entry) != "graphic_only":
        return False
    return math_entry_category(entry) in {"figure_embedded_math", "layout_fragment", "malformed_math"}


def paragraph_block_from_graphic_math_entry(
    block: dict[str, Any],
    math_entry: dict[str, Any],
    counters: dict[str, int],
    *,
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[[str, int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    repair_symbolic_ocr_spans: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    extract_general_inline_math_spans: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    merge_inline_math_relation_suffixes: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    normalize_inline_math_spans: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    text = normalize_paragraph_text(str(math_entry.get("display_latex", "")))
    if not text:
        return None, []

    spans, inline_math_entries, next_index = split_inline_math(text, counters["inline_math"])
    spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
    spans = normalize_inline_math_spans(spans)
    counters["inline_math"] = next_index

    source_spans = list(block.get("source_spans") or math_entry.get("source_spans") or [])
    for entry_item in inline_math_entries:
        entry_item["source_spans"] = source_spans

    return (
        {
            "id": str(block.get("id", "")),
            "type": "paragraph",
            "content": {"spans": spans},
            "source_spans": source_spans,
            "alternates": list(block.get("alternates") or []),
            "review": default_review(risk="medium"),
        },
        inline_math_entries,
    )


def make_group_entry_items_are_graphic_only(
    *,
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def bound_group_entry_items_are_graphic_only(entry: dict[str, Any]) -> bool:
        return group_entry_items_are_graphic_only(
            entry,
            math_entry_semantic_policy=math_entry_semantic_policy,
        )

    return bound_group_entry_items_are_graphic_only


def make_math_entry_looks_like_prose(
    *,
    normalize_paragraph_text: Callable[[str], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    word_count: Callable[[str], int],
) -> Callable[[dict[str, Any]], bool]:
    def bound_math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
        return math_entry_looks_like_prose(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            word_count=word_count,
        )

    return bound_math_entry_looks_like_prose


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
    def bound_should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_prose_math_entry_to_paragraph(
            entry,
            normalize_paragraph_text=normalize_paragraph_text,
            word_count=word_count,
            strong_operator_count=strong_operator_count,
            mathish_ratio=mathish_ratio,
            math_entry_looks_like_prose=math_entry_looks_like_prose,
            math_entry_semantic_policy=math_entry_semantic_policy,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
        )

    return bound_should_demote_prose_math_entry_to_paragraph


def make_should_demote_graphic_math_entry_to_paragraph(
    *,
    should_demote_prose_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
) -> Callable[[dict[str, Any]], bool]:
    def bound_should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
        return should_demote_graphic_math_entry_to_paragraph(
            entry,
            should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
        )

    return bound_should_demote_graphic_math_entry_to_paragraph


def make_should_drop_display_math_artifact(
    *,
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool],
    math_entry_semantic_policy: Callable[[dict[str, Any]], str],
    math_entry_category: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], bool]:
    def bound_should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
        return should_drop_display_math_artifact(
            entry,
            should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
            group_entry_items_are_graphic_only=group_entry_items_are_graphic_only,
            math_entry_semantic_policy=math_entry_semantic_policy,
            math_entry_category=math_entry_category,
        )

    return bound_should_drop_display_math_artifact


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
    def bound_paragraph_block_from_graphic_math_entry(
        block: dict[str, Any],
        math_entry: dict[str, Any],
        counters: dict[str, int],
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        return paragraph_block_from_graphic_math_entry(
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

    return bound_paragraph_block_from_graphic_math_entry


__all__ = [
    "group_entry_items_are_graphic_only",
    "make_group_entry_items_are_graphic_only",
    "make_math_entry_looks_like_prose",
    "make_paragraph_block_from_graphic_math_entry",
    "make_should_demote_graphic_math_entry_to_paragraph",
    "make_should_demote_prose_math_entry_to_paragraph",
    "make_should_drop_display_math_artifact",
    "math_entry_category",
    "math_entry_looks_like_prose",
    "math_entry_semantic_policy",
    "paragraph_block_from_graphic_math_entry",
    "should_demote_graphic_math_entry_to_paragraph",
    "should_demote_prose_math_entry_to_paragraph",
    "should_drop_display_math_artifact",
]
