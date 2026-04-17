from __future__ import annotations

import re
from dataclasses import replace
from typing import Any, Callable

from pipeline.types import LayoutBlock


def list_item_marker(text: str, *, clean_text: Callable[[str], str]) -> tuple[str | None, bool, str]:
    cleaned = clean_text(text)
    marker_match = re.match(r"^(?P<marker>(?:[-*•]+|\d+[.)]|[A-Za-z][.)]))\s+(?P<body>.+)$", cleaned)
    if not marker_match:
        return None, False, cleaned
    marker = marker_match.group("marker")
    body = clean_text(marker_match.group("body"))
    ordered = bool(re.match(r"^(?:\d+[.)]|[A-Za-z][.)])$", marker))
    return marker, ordered, body


def split_code_lines(text: str) -> list[str]:
    normalized = text.replace("```", " ")
    pieces = re.split(r";;\s*|\n+", normalized)
    return [line.strip() for line in pieces if line.strip()]


def looks_like_real_code_record(text: str, *, clean_text: Callable[[str], str]) -> bool:
    normalized = clean_text(text)
    lowered = normalized.lower()
    if lowered.startswith(("struct ", "typedef ", "for (", "while (", "if (", "q =", "v 0 =", "output ")):
        return True
    if any(
        token in lowered
        for token in (
            "project boundary curves",
            "project_boundary_curves",
            "partition face",
            "partition_face",
            "ray intersection count",
            "ray_intersection_count",
            "random face",
            "for each face",
            "output v",
        )
    ):
        return True
    if "/*" in normalized and "*/" in normalized:
        return True
    if normalized.count(";;") >= 2:
        code_tokens = sum(
            token in lowered
            for token in (
                "double ",
                "int ",
                "float ",
                "char ",
                " push(",
                " pop(",
                " else ",
                " if (",
                " for (",
                "return ",
            )
        )
        if code_tokens >= 1:
            return True
    if any(token in normalized for token in ("{", "}", "==", "&&", "||", "->")) and ";" in normalized:
        return True
    if re.search(r"\b(?:[A-Za-z_]{3,}[A-Za-z0-9_]*|[A-Za-z_]+_[A-Za-z0-9_]*)\s*\(", normalized) and ";" in normalized:
        return True
    return False


def build_blocks_for_record(
    record: dict[str, Any],
    layout_by_id: dict[str, LayoutBlock],
    figures_by_label: dict[str, dict[str, Any]],
    external_math_by_page: dict[int, list[dict[str, Any]]],
    external_math_overlap_by_page: dict[int, list[dict[str, Any]]],
    references_section: bool,
    counters: dict[str, int],
    *,
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    record_analysis_text: Callable[[dict[str, Any]], str],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    caption_label: Callable[[str], str | None],
    default_review: Callable[..., dict[str, Any]],
    make_reference_entry: Callable[[dict[str, Any], int], dict[str, Any]],
    looks_like_real_code_record: Callable[[str], bool],
    split_code_lines: Callable[[str], list[str]],
    list_item_marker: Callable[[str], tuple[str | None, bool, str]],
    normalize_paragraph_text: Callable[[str], str],
    split_inline_math: Callable[[str, int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    repair_symbolic_ocr_spans: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    extract_general_inline_math_spans: Callable[[list[dict[str, Any]], list[dict[str, Any]], int], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    merge_inline_math_relation_suffixes: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    normalize_inline_math_spans: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    review_for_math_entry: Callable[[dict[str, Any]], dict[str, Any]],
    review_for_math_ref_block: Callable[[dict[str, Any]], dict[str, Any]],
    looks_like_prose_paragraph: Callable[[str], bool],
    looks_like_prose_math_fragment: Callable[[str], bool],
    match_external_math_entry: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], dict[str, Any] | None],
    build_block_math_entry: Callable[[LayoutBlock, str, int], dict[str, Any]],
    normalize_formula_display_text: Callable[[str], str],
    classify_math_block: Callable[[LayoutBlock], str | None],
    review_for_algorithm_block_text: Callable[[str], dict[str, Any]],
    overlapping_external_math_entries: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]],
    trim_embedded_display_math_from_paragraph: Callable[[str, dict[str, Any], list[dict[str, Any]]], str],
    looks_like_display_math_echo: Callable[[dict[str, Any], str, list[dict[str, Any]]], bool],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    record = clean_record(record)
    text = str(record.get("text", ""))
    analysis_text = record_analysis_text(record)
    if not text:
        return [], [], []
    if is_short_ocr_fragment(record):
        return [], [], []

    blocks: list[dict[str, Any]] = []
    math_entries: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    source_spans = block_source_spans(record)

    if record.get("type") == "caption":
        label = caption_label(text)
        figure = figures_by_label.get(label or "")
        if figure is not None:
            block_id = f"blk-figure-{counters['block']:04d}"
            counters["block"] += 1
            blocks.append(
                {
                    "id": block_id,
                    "type": "figure_ref",
                    "content": {"figure_id": figure["id"]},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
        return blocks, math_entries, references

    if references_section or record.get("type") == "reference":
        reference = make_reference_entry(record, counters["reference"])
        counters["reference"] += 1
        references.append(reference)
        block_id = f"blk-reference-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "reference",
                "content": {"reference_id": reference["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    if record.get("type") == "code" and looks_like_real_code_record(text):
        code_lines = split_code_lines(str(record.get("text", "")))
        if not code_lines:
            return blocks, math_entries, references
        block_id = f"blk-code-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "code",
                "content": {"lines": code_lines, "language": "text"},
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    marker, ordered, body = list_item_marker(text)
    if record.get("type") == "list_item" or marker is not None:
        list_text = normalize_paragraph_text(body if marker is not None else text)
        spans, inline_math_entries, next_index = split_inline_math(list_text, counters["inline_math"])
        spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
        spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
        spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
        spans = normalize_inline_math_spans(spans)
        counters["inline_math"] = next_index
        for entry in inline_math_entries:
            entry["source_spans"] = source_spans
        math_entries.extend(inline_math_entries)
        block_id = f"blk-list_item-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "list_item",
                "content": {
                    "spans": spans,
                    "marker": marker,
                    "ordered": ordered,
                    "depth": 1,
                },
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    meta = record.get("meta", {})
    if isinstance(meta, dict) and isinstance(meta.get("external_math_entry"), dict):
        math_entry = dict(meta["external_math_entry"])
        math_entry["display_latex"] = normalize_formula_display_text(str(math_entry.get("display_latex", "")))
        math_entry["source_spans"] = list(math_entry.get("source_spans") or source_spans)
        math_entry["review"] = review_for_math_entry(math_entry)
        math_kind = str(math_entry.get("kind", "display"))
        block_type = "equation_group_ref" if math_kind == "group" else "display_equation_ref"
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    prose_like_record = looks_like_prose_paragraph(text) or looks_like_prose_math_fragment(text)

    external_math_entry = None if prose_like_record else match_external_math_entry(record, external_math_by_page)
    if external_math_entry is not None:
        math_entry = dict(external_math_entry)
        math_entry["display_latex"] = normalize_formula_display_text(str(math_entry.get("display_latex", "")))
        math_entry["source_spans"] = list(math_entry.get("source_spans") or source_spans)
        math_entry["review"] = review_for_math_entry(math_entry)
        math_kind = str(math_entry.get("kind", "display"))
        block_type = "equation_group_ref" if math_kind == "group" else "display_equation_ref"
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    layout_block = layout_by_id.get(str(record.get("id", "")))
    forced_math_kind = str(record.get("meta", {}).get("forced_math_kind", "") or "")
    if forced_math_kind in {"display", "group"} and not prose_like_record:
        math_entry = build_block_math_entry(
            LayoutBlock(
                id=str(record.get("id", "")),
                page=int(record.get("page", 0)),
                order=int(record.get("group_index", 0)),
                text=analysis_text,
                role="paragraph",
                bbox=source_spans[0]["bbox"] if source_spans else {},
                engine=str(source_spans[0].get("engine", "native_pdf")) if source_spans else "native_pdf",
                meta={"line_count": len(source_spans)},
            ),
            forced_math_kind,
            counters["math"],
        )
        math_entry["display_latex"] = normalize_formula_display_text(text)
        math_entry["source_spans"] = source_spans
        if forced_math_kind == "group":
            for item in math_entry.get("items", []):
                item["display_latex"] = normalize_formula_display_text(str(item.get("display_latex", "")))
            block_type = "equation_group_ref"
        else:
            block_type = "display_equation_ref"
        math_entry["review"] = review_for_math_entry(math_entry)
        counters["math"] += 1
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    if layout_block is not None:
        classified_kind = classify_math_block(replace(layout_block, text=analysis_text))
        if classified_kind == "algorithm":
            block_id = f"blk-algorithm-{counters['block']:04d}"
            counters["block"] += 1
            algorithm_lines = [line for line in re.split(r"\s{2,}|(?<=;)\s+", text) if line]
            blocks.append(
                {
                    "id": block_id,
                    "type": "algorithm",
                    "content": {"lines": algorithm_lines},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": review_for_algorithm_block_text(" ".join(algorithm_lines)),
                }
            )
            return blocks, math_entries, references

        math_kind = None if prose_like_record else classified_kind
        if math_kind in {"display", "group"}:
            math_entry = build_block_math_entry(layout_block, math_kind, counters["math"])
            math_entry["display_latex"] = normalize_formula_display_text(text)
            math_entry["source_spans"] = source_spans
            if math_kind == "group":
                for item in math_entry.get("items", []):
                    item["display_latex"] = normalize_formula_display_text(str(item.get("display_latex", "")))
                block_type = "equation_group_ref"
            else:
                block_type = "display_equation_ref"
            math_entry["review"] = review_for_math_entry(math_entry)
            counters["math"] += 1
            math_entries.append(math_entry)
            block_id = f"blk-{block_type}-{counters['block']:04d}"
            counters["block"] += 1
            blocks.append(
                {
                    "id": block_id,
                    "type": block_type,
                    "content": {"math_id": math_entry["id"]},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": review_for_math_ref_block(math_entry),
                }
            )
            return blocks, math_entries, references

    text = normalize_paragraph_text(text)
    overlapping_math = overlapping_external_math_entries(record, external_math_overlap_by_page)
    text = trim_embedded_display_math_from_paragraph(text, record, overlapping_math)
    if looks_like_display_math_echo(record, text, overlapping_math):
        return [], [], []
    spans, inline_math_entries, next_index = split_inline_math(text, counters["inline_math"])
    spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
    spans = normalize_inline_math_spans(spans)
    counters["inline_math"] = next_index
    for entry in inline_math_entries:
        entry["source_spans"] = source_spans
    math_entries.extend(inline_math_entries)
    block_id = f"blk-paragraph-{counters['block']:04d}"
    counters["block"] += 1
    blocks.append(
        {
            "id": block_id,
            "type": "paragraph",
            "content": {"spans": spans},
            "source_spans": source_spans,
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    )
    return blocks, math_entries, references
