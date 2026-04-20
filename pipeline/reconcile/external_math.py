from __future__ import annotations

from typing import Any, Callable

from pipeline.math.extract import looks_like_prose_math_fragment
from pipeline.types import LayoutBlock


def rect_intersection_area(a: dict[str, Any], b: dict[str, Any]) -> float:
    x0 = max(float(a.get("x0", 0.0)), float(b.get("x0", 0.0)))
    y0 = max(float(a.get("y0", 0.0)), float(b.get("y0", 0.0)))
    x1 = min(float(a.get("x1", 0.0)), float(b.get("x1", 0.0)))
    y1 = min(float(a.get("y1", 0.0)), float(b.get("y1", 0.0)))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def rect_area(rect: dict[str, Any]) -> float:
    return max(float(rect.get("width", 0.0)) * float(rect.get("height", 0.0)), 1.0)


def match_external_math_entry(
    record: dict[str, Any],
    external_math_by_page: dict[int, list[dict[str, Any]]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> dict[str, Any] | None:
    source_span = (block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    record_bbox = source_span.get("bbox", {})
    record_text = clean_text(str(record.get("text", "")))
    if not page or not record_bbox:
        return None

    candidates = external_math_by_page.get(page, [])
    if not candidates:
        return None

    record_area = rect_area(record_bbox)
    best_index: int | None = None
    best_score = 0.0
    for index, entry in enumerate(candidates):
        if entry.get("kind") not in {"display", "group"}:
            continue
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        if not entry_bbox:
            continue
        overlap = rect_intersection_area(record_bbox, entry_bbox)
        if overlap <= 0.0:
            continue
        entry_area = rect_area(entry_bbox)
        overlap_score = overlap / min(record_area, entry_area)
        score = overlap_score
        entry_text = clean_text(str(entry.get("display_latex", "")))
        if entry_text and entry_text == record_text:
            score += 1.0
        elif entry_text and record_text and (entry_text in record_text or record_text in entry_text):
            score += 0.2
        if score > best_score:
            best_score = score
            best_index = index

    if best_index is None or best_score < 0.35:
        return None
    return external_math_by_page[page].pop(best_index)


def make_match_external_math_entry(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], dict[str, Any] | None]:
    def bound_match_external_math_entry(
        record: dict[str, Any],
        external_math_by_page: dict[int, list[dict[str, Any]]],
    ) -> dict[str, Any] | None:
        return match_external_math_entry(
            record,
            external_math_by_page,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
        )

    return bound_match_external_math_entry


def inject_external_math_records(
    records: list[dict[str, Any]],
    layout_blocks: list[LayoutBlock],
    external_math_entries: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    looks_like_leading_display_math_echo: Callable[[str], bool],
) -> tuple[list[dict[str, Any]], set[str]]:
    page_orders: dict[int, list[tuple[int, float]]] = {}
    page_blocks: dict[int, list[LayoutBlock]] = {}
    for block in layout_blocks:
        page_orders.setdefault(int(block.page), []).append((int(block.order), float(block.bbox.get("y0", 0.0))))
        page_blocks.setdefault(int(block.page), []).append(block)
    for values in page_orders.values():
        values.sort(key=lambda item: (item[1], item[0]))

    per_anchor_counts: dict[tuple[int, int], int] = {}
    injected_ids: set[str] = set()
    injected_records: list[dict[str, Any]] = []

    for entry in external_math_entries:
        if str(entry.get("kind", "")) not in {"display", "group"}:
            continue
        spans = list(entry.get("source_spans") or [])
        if not spans:
            continue
        span = spans[0]
        page = int(span.get("page", 0) or 0)
        bbox = dict(span.get("bbox", {}))
        if page <= 0 or not bbox:
            continue
        y0 = float(bbox.get("y0", 0.0))
        prior_orders = [order for order, block_y0 in page_orders.get(page, []) if block_y0 <= y0]
        anchor_order = prior_orders[-1] if prior_orders else 0
        anchor_before_order: int | None = None
        entry_area = rect_area(bbox)
        for block in page_blocks.get(page, []):
            if block.role not in {"paragraph", "code"}:
                continue
            block_bbox = dict(block.bbox)
            overlap = rect_intersection_area(bbox, block_bbox)
            if overlap <= 0.0:
                continue
            overlap_score = overlap / min(entry_area, rect_area(block_bbox))
            if overlap_score < 0.2:
                continue
            top_gap = y0 - float(block_bbox.get("y0", 0.0))
            if top_gap < -8.0 or top_gap > 24.0:
                continue
            if not looks_like_leading_display_math_echo(block.text):
                continue
            candidate_order = int(block.order)
            if anchor_before_order is None or candidate_order < anchor_before_order:
                anchor_before_order = candidate_order
        if anchor_before_order is not None:
            prior_anchor_orders = [order for order, _ in page_orders.get(page, []) if order < anchor_before_order]
            anchor_order = prior_anchor_orders[-1] if prior_anchor_orders else 0
        anchor_key = (page, anchor_order)
        per_anchor_counts[anchor_key] = per_anchor_counts.get(anchor_key, 0) + 1
        split_index = per_anchor_counts[anchor_key]
        entry_text = clean_text(str(entry.get("display_latex", "")))
        injected_records.append(
            {
                "id": f"external-math-record-{entry['id']}",
                "page": page,
                "group_index": anchor_order * 10 + 5,
                "split_index": split_index,
                "type": "paragraph",
                "text": entry_text,
                "source_spans": spans,
                "meta": (
                    {"source_math_entry_id": str(entry.get("id", ""))}
                    if looks_like_prose_math_fragment(entry_text)
                    else {
                        "external_math_entry": dict(entry),
                        "forced_math_kind": "group" if str(entry.get("kind", "")) == "group" else "display",
                    }
                ),
            }
        )
        injected_ids.add(str(entry["id"]))

    if not injected_records:
        return records, injected_ids

    combined = list(records)
    combined.extend(injected_records)
    combined.sort(key=lambda record: (int(record.get("page", 0)), int(record.get("group_index", 0)), int(record.get("split_index", 0))))
    return combined, injected_ids


__all__ = [
    "inject_external_math_records",
    "make_match_external_math_entry",
    "match_external_math_entry",
    "rect_area",
    "rect_intersection_area",
]
