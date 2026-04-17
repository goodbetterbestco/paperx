from __future__ import annotations

import re
from typing import Any, Callable, Pattern


def make_reference_entry(
    record: dict[str, Any],
    index: int,
    *,
    clean_text: Callable[[str], str],
    normalize_reference_text: Callable[[str], tuple[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    raw_text = clean_text(str(record.get("text", "")))
    text, _ = normalize_reference_text(raw_text)
    return {
        "id": f"ref-{index:03d}",
        "raw_text": raw_text,
        "text": text,
        "source_spans": block_source_spans(record),
        "alternates": [],
        "review": default_review(risk="medium"),
    }


def is_reference_start(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    reference_start_re: Pattern[str],
    looks_like_reference_text: Callable[[str], bool],
) -> bool:
    text = clean_text(str(record.get("text", "")))
    if not text or not re.search(r"[A-Za-z]", text):
        return False
    if str(record.get("type", "")) == "list_item" and looks_like_reference_text(text):
        return True
    bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    x0 = float(bbox.get("x0", 0.0))
    if x0 > 90:
        return False
    return bool(reference_start_re.match(text))


def merge_reference_records(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    is_reference_start: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for record in records:
        text = clean_text(str(record.get("text", "")))
        if not text or not re.search(r"[A-Za-z]", text):
            continue
        bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
        x0 = float(bbox.get("x0", 0.0))
        if current is None or is_reference_start(record):
            if current is not None:
                merged.append(current)
            current = {
                "id": f"merged-{record.get('id', '')}",
                "type": "reference",
                "page": int(record.get("page", 0)),
                "group_index": int(record.get("group_index", 0)),
                "split_index": 1,
                "text": text,
                "source_spans": list(block_source_spans(record)),
                "meta": {"source_record_ids": [str(record.get("id", ""))]},
            }
            continue

        if current is not None and x0 >= 100:
            current["text"] = clean_text(f"{current['text']} {text}")
            current["source_spans"].extend(block_source_spans(record))
            current["meta"]["source_record_ids"].append(str(record.get("id", "")))
            continue

        if current is not None:
            merged.append(current)
        current = {
            "id": f"merged-{record.get('id', '')}",
            "type": "reference",
            "page": int(record.get("page", 0)),
            "group_index": int(record.get("group_index", 0)),
            "split_index": 1,
            "text": text,
            "source_spans": list(block_source_spans(record)),
            "meta": {"source_record_ids": [str(record.get("id", ""))]},
        }

    if current is not None:
        merged.append(current)
    return merged


def looks_like_reference_text(
    text: str,
    *,
    clean_text: Callable[[str], str],
    reference_year_re: Pattern[str],
    reference_venue_re: Pattern[str],
    reference_author_re: Pattern[str],
    short_word_re: Pattern[str],
) -> bool:
    cleaned = clean_text(text)
    if len(cleaned) < 20 or not re.search(r"[A-Za-z]", cleaned):
        return False
    has_year = bool(reference_year_re.search(cleaned))
    has_venue = bool(reference_venue_re.search(cleaned))
    if has_year and has_venue:
        return True
    if has_year and reference_author_re.match(cleaned):
        return True
    if has_year and "," in cleaned and len(short_word_re.findall(cleaned)) >= 6:
        return True
    if has_venue and reference_author_re.match(cleaned):
        return True
    if has_venue and "," in cleaned and len(short_word_re.findall(cleaned)) >= 6:
        return True
    return False


def split_trailing_reference_records(
    records: list[dict[str, Any]],
    *,
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    split_index = len(records)
    while split_index > 0 and looks_like_reference_text(str(records[split_index - 1].get("text", ""))):
        split_index -= 1

    trailing = records[split_index:]
    if len(trailing) < 5:
        return records, []

    return records[:split_index], merge_reference_records(trailing)


def extract_reference_records_from_tail_section(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    about_author_re: Pattern[str],
    looks_like_reference_text: Callable[[str], bool],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(records) < 8:
        return records, []

    reference_records: list[dict[str, Any]] = []
    body_records: list[dict[str, Any]] = []
    for record in records:
        text = clean_text(str(record.get("text", "")))
        if not text:
            body_records.append(record)
            continue
        if about_author_re.match(text):
            body_records.append(record)
            continue
        if looks_like_reference_text(text):
            reference_records.append(record)
            continue
        body_records.append(record)

    if len(reference_records) < 5:
        return records, []

    return body_records, merge_reference_records(reference_records)


def reference_records_from_mathpix_layout(
    layout: dict[str, Any] | None,
    *,
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]],
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    layout_record: Callable[[Any], dict[str, Any]],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if not layout:
        return []

    reference_records: list[dict[str, Any]] = []
    references_started = False
    for page in sorted(mathpix_text_blocks_by_page(layout)):
        for block in mathpix_text_blocks_by_page(layout)[page]:
            text = clean_text(str(block.text))
            if not text:
                continue
            if not references_started:
                if normalize_title_key(text) == "references":
                    references_started = True
                continue
            if re.match(r"^\[\s*\d+\s*\]", text):
                reference_records.append(layout_record(block))
                continue
            if reference_records:
                reference_records.append(layout_record(block))

    if len(reference_records) < 3:
        return []
    return merge_reference_records(reference_records)
