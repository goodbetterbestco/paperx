from __future__ import annotations

import re
from typing import Any, Callable

from pipeline.figures.labels import caption_label
from pipeline.types import LayoutBlock


def normalize_figure_caption_text(
    text: str,
    *,
    clean_text: Callable[[str], str],
    normalize_prose_text: Callable[[str], tuple[str, Any]],
) -> str:
    normalized = clean_text(text)
    normalized = re.sub(r"^\s*Fig\.\s*\d+\s*", "", normalized, flags=re.IGNORECASE)
    normalized, _ = normalize_prose_text(normalized)
    normalized = normalized.lstrip(" .:;-—")
    return clean_text(normalized)


def make_normalize_figure_caption_text(
    *,
    clean_text: Callable[[str], str],
    normalize_prose_text: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def bound_normalize_figure_caption_text(text: str) -> str:
        return normalize_figure_caption_text(
            text,
            clean_text=clean_text,
            normalize_prose_text=normalize_prose_text,
        )

    return bound_normalize_figure_caption_text


def layout_record(
    block: LayoutBlock,
    *,
    clean_text: Callable[[str], str],
) -> dict[str, Any]:
    record_type = str(block.role)
    if record_type == "paragraph":
        docling_label = str(block.meta.get("docling_label", "") or "")
        mathpix_type = str(block.meta.get("mathpix_type", "") or "")
        mathpix_subtype = str(block.meta.get("mathpix_subtype", "") or "")
        if docling_label == "list_item":
            record_type = "list_item"
        elif docling_label == "code":
            record_type = "code"
        elif mathpix_type in {"code", "pseudocode"} or mathpix_subtype in {"algorithm", "pseudocode"}:
            record_type = "code"
    record = block.as_record()
    record["type"] = record_type
    record["group_index"] = block.order * 10
    record["text"] = clean_text(block.text)
    record.setdefault("meta", {})
    record["meta"] = {**record["meta"], "raw_text": block.text}
    return record


def page_one_front_matter_records(
    records: list[dict[str, Any]],
    mathpix_layout: dict[str, Any] | None,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[LayoutBlock]]],
    layout_record: Callable[[LayoutBlock], dict[str, Any]],
) -> list[dict[str, Any]]:
    page_one_records = [record for record in records if int(record.get("page", 0) or 0) == 1]
    if not mathpix_layout:
        return page_one_records

    seen: set[str] = set()
    combined: list[dict[str, Any]] = []
    for record in page_one_records:
        key = normalize_title_key(clean_text(str(record.get("text", ""))))
        if key:
            seen.add(key)
        combined.append(record)

    for block in mathpix_text_blocks_by_page(mathpix_layout).get(1, []):
        record = layout_record(block)
        key = normalize_title_key(clean_text(str(record.get("text", ""))))
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        combined.append(record)

    combined.sort(
        key=lambda record: (
            int(record.get("page", 0) or 0),
            int(record.get("group_index", 0) or 0),
            int(record.get("split_index", 0) or 0),
        )
    )
    return combined


def figure_label_token(figure: dict[str, Any]) -> str | None:
    return caption_label(str(figure.get("label", "")))


def synthetic_caption_record(figure: dict[str, Any], page_blocks: list[LayoutBlock]) -> dict[str, Any]:
    caption_bbox = figure.get("provenance", {}).get("caption_bbox") or figure.get("bbox", {})
    caption_y = float(caption_bbox.get("y0", 0.0))
    preceding = sum(1 for block in page_blocks if float(block.bbox.get("y0", 0.0)) <= caption_y)
    return {
        "id": f"synthetic-caption-{figure['id']}",
        "page": int(figure["page"]),
        "group_index": preceding * 10 + 5,
        "split_index": 1,
        "type": "caption",
        "text": f"{figure['label']}: {figure['caption']}",
        "source_spans": [
            {
                "page": int(figure["page"]),
                "bbox": caption_bbox,
                "engine": "local_figure_linker",
            }
        ],
        "meta": {
            "figure_id": figure["id"],
            "synthetic": True,
        },
    }


def record_bbox(
    record: dict[str, Any],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> dict[str, Any]:
    return (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})


def rect_x_overlap_ratio(a: dict[str, Any], b: dict[str, Any]) -> float:
    x0 = max(float(a.get("x0", 0.0)), float(b.get("x0", 0.0)))
    x1 = min(float(a.get("x1", 0.0)), float(b.get("x1", 0.0)))
    if x1 <= x0:
        return 0.0
    width_a = max(float(a.get("width", 0.0)), float(a.get("x1", 0.0)) - float(a.get("x0", 0.0)), 1.0)
    width_b = max(float(b.get("width", 0.0)), float(b.get("x1", 0.0)) - float(b.get("x0", 0.0)), 1.0)
    return (x1 - x0) / min(width_a, width_b)


def strip_caption_label_prefix(
    text: str,
    *,
    clean_text: Callable[[str], str],
    figure: dict[str, Any] | None = None,
) -> str:
    cleaned = clean_text(text)
    if ":" in cleaned:
        leading, remainder = cleaned.split(":", 1)
        if caption_label(leading) or re.match(r"^\s*fig(?:ure)?\.?\s*\d+\b", leading, re.IGNORECASE):
            return clean_text(remainder)
    prefixes: list[str] = []
    if figure is not None:
        prefixes.append(clean_text(str(figure.get("label", ""))))
    label = caption_label(cleaned)
    if label:
        prefixes.append(label)
    for prefix in prefixes:
        if prefix and cleaned.lower().startswith(prefix.lower()):
            stripped = cleaned[len(prefix) :].lstrip(" :.-")
            return clean_text(stripped)
    return cleaned


def append_figure_caption_fragment(
    figure: dict[str, Any],
    fragment: str,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    normalize_figure_caption_text: Callable[[str], str],
    strip_caption_label_prefix: Callable[[str, dict[str, Any] | None], str],
) -> None:
    normalized_fragment = normalize_figure_caption_text(strip_caption_label_prefix(fragment, figure))
    if not normalized_fragment:
        return
    current = clean_text(str(figure.get("caption", "")))
    if current:
        current_words = current.split()
        fragment_words = normalized_fragment.split()
        max_overlap = min(len(current_words), len(fragment_words))
        for overlap in range(max_overlap, 5, -1):
            prefix = clean_text(" ".join(fragment_words[:overlap]))
            if prefix and normalize_title_key(prefix) in normalize_title_key(current):
                normalized_fragment = clean_text(" ".join(fragment_words[overlap:]))
                break
        if not normalized_fragment:
            return
    current_key = normalize_title_key(current)
    fragment_key = normalize_title_key(normalized_fragment)
    if fragment_key and current_key and fragment_key in current_key:
        return
    figure["caption"] = clean_text(f"{current} {normalized_fragment}" if current else normalized_fragment)


def match_figure_for_caption_record(
    record: dict[str, Any],
    figures_on_page: list[dict[str, Any]],
    *,
    record_bbox: Callable[[dict[str, Any]], dict[str, Any]],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
    figure_label_token: Callable[[dict[str, Any]], str | None],
) -> dict[str, Any] | None:
    if not figures_on_page:
        return None
    label = caption_label(str(record.get("text", "")))
    if label:
        for figure in figures_on_page:
            if figure_label_token(figure) == label:
                return figure

    bbox = record_bbox(record)
    if not bbox:
        return None
    record_y0 = float(bbox.get("y0", 0.0))
    best_figure: dict[str, Any] | None = None
    best_score = float("-inf")
    for figure in figures_on_page:
        figure_bbox = figure.get("bbox", {})
        if not figure_bbox:
            continue
        x_overlap = rect_x_overlap_ratio(bbox, figure_bbox)
        if x_overlap <= 0.0:
            continue
        figure_y1 = float(figure_bbox.get("y1", 0.0))
        vertical_gap = max(record_y0 - figure_y1, 0.0)
        if vertical_gap > 120.0:
            continue
        score = x_overlap - (vertical_gap / 120.0)
        if score > best_score:
            best_score = score
            best_figure = figure
    return best_figure


def absorb_figure_caption_continuations(
    records: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    *,
    match_figure_for_caption_record: Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any] | None],
    append_figure_caption_fragment: Callable[[dict[str, Any], str], None],
) -> list[dict[str, Any]]:
    figures_by_page: dict[int, list[dict[str, Any]]] = {}
    for figure in figures:
        figures_by_page.setdefault(int(figure.get("page", 0) or 0), []).append(figure)

    adjusted: list[dict[str, Any]] = []
    for record in records:
        record_type = str(record.get("type", ""))
        page = int(record.get("page", 0) or 0)

        if record_type == "caption":
            figure = match_figure_for_caption_record(record, figures_by_page.get(page, []))
            if figure is not None:
                append_figure_caption_fragment(figure, str(record.get("text", "")))
                if not caption_label(str(record.get("text", ""))):
                    continue
            adjusted.append(record)
            continue

        adjusted.append(record)

    return adjusted


def merge_layout_and_figure_records(
    layout_blocks: list[LayoutBlock],
    figures: list[dict[str, Any]],
    *,
    layout_record: Callable[[LayoutBlock], dict[str, Any]],
    absorb_figure_caption_continuations: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]],
    figure_label_token: Callable[[dict[str, Any]], str | None],
    synthetic_caption_record: Callable[[dict[str, Any], list[LayoutBlock]], dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, LayoutBlock]]:
    records = [layout_record(block) for block in layout_blocks]
    layout_by_id = {block.id: block for block in layout_blocks}
    page_blocks: dict[int, list[LayoutBlock]] = {}
    for block in layout_blocks:
        page_blocks.setdefault(block.page, []).append(block)

    records = absorb_figure_caption_continuations(records, figures)

    existing_labels = {
        (record["page"], caption_label(str(record.get("text", ""))))
        for record in records
        if record.get("type") == "caption"
    }
    for figure in figures:
        label = figure_label_token(figure)
        key = (int(figure["page"]), label)
        if label and key in existing_labels:
            continue
        records.append(synthetic_caption_record(figure, page_blocks.get(int(figure["page"]), [])))

    return records, layout_by_id


def make_layout_record(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[LayoutBlock], dict[str, Any]]:
    def build_layout_record(block: LayoutBlock) -> dict[str, Any]:
        return layout_record(
            block,
            clean_text=clean_text,
        )

    return build_layout_record


def make_page_one_front_matter_records(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[LayoutBlock]]],
    layout_record: Callable[[LayoutBlock], dict[str, Any]],
) -> Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]:
    def build_page_one_front_matter_records(
        records: list[dict[str, Any]],
        mathpix_layout: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return page_one_front_matter_records(
            records,
            mathpix_layout,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
            layout_record=layout_record,
        )

    return build_page_one_front_matter_records


def make_record_bbox(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def build_record_bbox(record: dict[str, Any]) -> dict[str, Any]:
        return record_bbox(
            record,
            block_source_spans=block_source_spans,
        )

    return build_record_bbox


def make_strip_caption_label_prefix(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str, dict[str, Any] | None], str]:
    def build_strip_caption_label_prefix(text: str, figure: dict[str, Any] | None = None) -> str:
        return strip_caption_label_prefix(
            text,
            clean_text=clean_text,
            figure=figure,
        )

    return build_strip_caption_label_prefix


def make_append_figure_caption_fragment(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    normalize_figure_caption_text: Callable[[str], str],
    strip_caption_label_prefix: Callable[[str, dict[str, Any] | None], str],
) -> Callable[[dict[str, Any], str], None]:
    def build_append_figure_caption_fragment(figure: dict[str, Any], fragment: str) -> None:
        append_figure_caption_fragment(
            figure,
            fragment,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            normalize_figure_caption_text=normalize_figure_caption_text,
            strip_caption_label_prefix=strip_caption_label_prefix,
        )

    return build_append_figure_caption_fragment


def make_match_figure_for_caption_record(
    *,
    record_bbox: Callable[[dict[str, Any]], dict[str, Any]],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
    figure_label_token: Callable[[dict[str, Any]], str | None],
) -> Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any] | None]:
    def build_match_figure_for_caption_record(
        record: dict[str, Any],
        figures_on_page: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        return match_figure_for_caption_record(
            record,
            figures_on_page,
            record_bbox=record_bbox,
            rect_x_overlap_ratio=rect_x_overlap_ratio,
            figure_label_token=figure_label_token,
        )

    return build_match_figure_for_caption_record


def make_absorb_figure_caption_continuations(
    *,
    match_figure_for_caption_record: Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any] | None],
    append_figure_caption_fragment: Callable[[dict[str, Any], str], None],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]]:
    def build_absorb_figure_caption_continuations(
        records: list[dict[str, Any]],
        figures: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return absorb_figure_caption_continuations(
            records,
            figures,
            match_figure_for_caption_record=match_figure_for_caption_record,
            append_figure_caption_fragment=append_figure_caption_fragment,
        )

    return build_absorb_figure_caption_continuations


def make_merge_layout_and_figure_records(
    *,
    layout_record: Callable[[LayoutBlock], dict[str, Any]],
    absorb_figure_caption_continuations: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]],
    figure_label_token: Callable[[dict[str, Any]], str | None],
    synthetic_caption_record: Callable[[dict[str, Any], list[LayoutBlock]], dict[str, Any]],
) -> Callable[[list[LayoutBlock], list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, LayoutBlock]]]:
    def build_merge_layout_and_figure_records(
        layout_blocks: list[LayoutBlock],
        figures: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, LayoutBlock]]:
        return merge_layout_and_figure_records(
            layout_blocks,
            figures,
            layout_record=layout_record,
            absorb_figure_caption_continuations=absorb_figure_caption_continuations,
            figure_label_token=figure_label_token,
            synthetic_caption_record=synthetic_caption_record,
        )

    return build_merge_layout_and_figure_records


__all__ = [
    "absorb_figure_caption_continuations",
    "append_figure_caption_fragment",
    "figure_label_token",
    "layout_record",
    "make_absorb_figure_caption_continuations",
    "make_append_figure_caption_fragment",
    "make_layout_record",
    "make_merge_layout_and_figure_records",
    "make_match_figure_for_caption_record",
    "make_normalize_figure_caption_text",
    "make_page_one_front_matter_records",
    "make_record_bbox",
    "make_strip_caption_label_prefix",
    "match_figure_for_caption_record",
    "merge_layout_and_figure_records",
    "normalize_figure_caption_text",
    "page_one_front_matter_records",
    "record_bbox",
    "rect_x_overlap_ratio",
    "strip_caption_label_prefix",
    "synthetic_caption_record",
]
