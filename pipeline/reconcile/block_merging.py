from __future__ import annotations

import re
from typing import Any, Callable, Pattern


def merge_paragraph_records(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    table_caption_re: Pattern[str],
) -> list[dict[str, Any]]:
    def copy_record(source: dict[str, Any]) -> dict[str, Any]:
        copied = dict(source)
        copied["source_spans"] = list(block_source_spans(source))
        copied["meta"] = dict(source.get("meta", {}))
        return copied

    def is_paragraph_merge_interruption(record: dict[str, Any]) -> bool:
        if str(record.get("type", "")) != "caption":
            return False
        text = clean_text(str(record.get("text", "")))
        return bool(text) and (
            table_caption_re.match(text) is not None
            or text.lower().startswith("figure ")
        )

    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    pending_interruptions: list[dict[str, Any]] = []

    index = 0
    while index < len(records):
        record = records[index]
        if current is None:
            current = copy_record(record)
            index += 1
            continue

        if should_merge_paragraph_records(current, record):
            current["text"] = clean_text(f"{current.get('text', '')} {record.get('text', '')}")
            current["source_spans"].extend(block_source_spans(record))
            current["meta"]["source_record_ids"] = [
                *current["meta"].get("source_record_ids", [str(current.get("id", ""))]),
                str(record.get("id", "")),
            ]
            index += 1
            continue

        if (
            is_paragraph_merge_interruption(record)
            and index + 1 < len(records)
            and should_merge_paragraph_records(current, records[index + 1])
        ):
            pending_interruptions.append(copy_record(record))
            index += 1
            continue

        merged.append(current)
        merged.extend(pending_interruptions)
        pending_interruptions = []
        current = copy_record(record)
        index += 1

    if current is not None:
        merged.append(current)
    merged.extend(pending_interruptions)
    return merged


def merge_paragraph_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    def paragraph_block_text(block: dict[str, Any]) -> str:
        if str(block.get("type", "")) != "paragraph":
            return ""
        spans = block.get("content", {}).get("spans", [])
        parts: list[str] = []
        for span in spans:
            if not isinstance(span, dict):
                continue
            kind = str(span.get("kind", ""))
            if kind == "text":
                parts.append(str(span.get("text", "")))
            elif kind == "inline_math_ref":
                parts.append("[M]")
        return strip_known_running_header_text("".join(parts))

    def paragraph_block_record(block: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": str(block.get("type", "")),
            "text": paragraph_block_text(block),
            "source_spans": list(block_source_spans(block)),
            "meta": {},
        }

    def merge_paragraph_block_spans(
        previous_spans: list[dict[str, Any]],
        current_spans: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged = [dict(span) for span in previous_spans]
        if merged and current_spans:
            last = merged[-1]
            needs_space = True
            if isinstance(last, dict) and last.get("kind") == "text" and str(last.get("text", "")).endswith((" ", "\n", "\t")):
                needs_space = False
            if needs_space:
                merged.append({"kind": "text", "text": " "})
        merged.extend(dict(span) for span in current_spans)
        return merged

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    merged_away_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        merged_block_ids: list[str] = []
        previous_block_id: str | None = None
        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in merged_away_ids:
                continue
            if previous_block_id is not None:
                previous_block = block_by_id.get(previous_block_id)
                if previous_block and should_merge_paragraph_records(
                    paragraph_block_record(previous_block),
                    paragraph_block_record(block),
                ):
                    previous_spans = list(previous_block.get("content", {}).get("spans", []))
                    current_spans = list(block.get("content", {}).get("spans", []))
                    previous_block["content"] = {
                        "spans": merge_paragraph_block_spans(previous_spans, current_spans)
                    }
                    previous_block["source_spans"] = [
                        *list(previous_block.get("source_spans", [])),
                        *list(block.get("source_spans", [])),
                    ]
                    previous_block["alternates"] = [
                        *list(previous_block.get("alternates", [])),
                        *list(block.get("alternates", [])),
                    ]
                    merged_away_ids.add(block_key)
                    continue

            merged_block_ids.append(block_key)
            block_type = str(block.get("type", ""))
            if block_type == "paragraph":
                previous_block_id = block_key
            elif block_type != "footnote":
                previous_block_id = None

        updated_section["block_ids"] = merged_block_ids
        updated_sections.append(updated_section)

    merged_blocks = [block for block in blocks if str(block.get("id", "")) not in merged_away_ids]
    return merged_blocks, updated_sections


def normalize_footnote_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    short_word_re: Pattern[str],
    starts_like_sentence: Callable[[str], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    def paragraph_block_text(block: dict[str, Any]) -> str:
        if str(block.get("type", "")) != "paragraph":
            return ""
        spans = block.get("content", {}).get("spans", [])
        parts: list[str] = []
        for span in spans:
            if not isinstance(span, dict):
                continue
            kind = str(span.get("kind", ""))
            if kind == "text":
                parts.append(str(span.get("text", "")))
            elif kind == "inline_math_ref":
                parts.append("[M]")
        return strip_known_running_header_text("".join(parts))

    def is_footnote_like_paragraph_block(block: dict[str, Any]) -> bool:
        if str(block.get("type", "")) != "paragraph":
            return False
        text = paragraph_block_text(block)
        if not text:
            return False
        bbox = (block_source_spans(block)[:1] or [{}])[0].get("bbox", {})
        y0 = float(bbox.get("y0", 0.0))
        height = float(bbox.get("height", 0.0))
        if text.startswith(("*", "†", "‡")) and y0 >= 620.0 and 0.0 < height <= 120.0:
            return True
        return False

    def looks_like_footnote_continuation_block(
        footnote_block: dict[str, Any],
        block: dict[str, Any],
    ) -> bool:
        if str(block.get("type", "")) != "paragraph":
            return False
        text = paragraph_block_text(block)
        if not text:
            return False
        footnote_spans = list(block_source_spans(footnote_block))
        footnote_span = (footnote_spans[:1] or [{}])[0]
        current_span = (block_source_spans(block)[:1] or [{}])[0]
        footnote_page = int(footnote_span.get("page", footnote_block.get("page", 0)) or 0)
        current_page = int(current_span.get("page", block.get("page", 0)) or 0)
        if current_page != footnote_page:
            return False
        footnote_bboxes = [span.get("bbox", {}) for span in footnote_spans if span.get("bbox")]
        footnote_bbox = footnote_span.get("bbox", {})
        current_bbox = current_span.get("bbox", {})
        footnote_x0 = min(float(bbox.get("x0", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("x0", 0.0))
        footnote_y0 = min(float(bbox.get("y0", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("y0", 0.0))
        footnote_y1 = max(float(bbox.get("y1", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("y1", 0.0))
        current_x0 = float(current_bbox.get("x0", 0.0))
        current_y0 = float(current_bbox.get("y0", 0.0))
        current_width = float(current_bbox.get("width", 0.0))
        current_height = float(current_bbox.get("height", 0.0))
        words = short_word_re.findall(text)
        if abs(current_x0 - footnote_x0) > 40.0:
            return False
        if current_y0 + 4.0 < footnote_y0:
            return False
        if current_y0 > footnote_y1 + 32.0:
            return False
        if len(words) <= 6:
            return True
        if current_width <= 140.0 and current_height <= 14.0:
            return True
        return not starts_like_sentence(text)

    def merge_footnote_block_spans(
        previous_spans: list[dict[str, Any]],
        current_spans: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged = [dict(span) for span in previous_spans]
        if merged and current_spans:
            last = merged[-1]
            needs_space = True
            if isinstance(last, dict) and last.get("kind") == "text" and str(last.get("text", "")).endswith((" ", "\n", "\t")):
                needs_space = False
            if needs_space:
                merged.append({"kind": "text", "text": " "})
        merged.extend(dict(span) for span in current_spans)
        return merged

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    merged_away_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        normalized_block_ids: list[str] = []
        active_footnote_id: str | None = None

        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in merged_away_ids:
                continue

            if is_footnote_like_paragraph_block(block):
                block["type"] = "footnote"
            elif active_footnote_id is not None:
                active_footnote = block_by_id.get(active_footnote_id)
                if active_footnote and looks_like_footnote_continuation_block(active_footnote, block):
                    block["type"] = "footnote"

            if str(block.get("type", "")) == "footnote":
                if active_footnote_id is not None:
                    active_footnote = block_by_id.get(active_footnote_id)
                    if active_footnote:
                        previous_spans = list(active_footnote.get("content", {}).get("spans", []))
                        current_spans = list(block.get("content", {}).get("spans", []))
                        active_footnote["content"] = {
                            "spans": merge_footnote_block_spans(previous_spans, current_spans)
                        }
                        active_footnote["source_spans"] = [
                            *list(active_footnote.get("source_spans", [])),
                            *list(block.get("source_spans", [])),
                        ]
                        active_footnote["alternates"] = [
                            *list(active_footnote.get("alternates", [])),
                            *list(block.get("alternates", [])),
                        ]
                        merged_away_ids.add(block_key)
                        continue
                normalized_block_ids.append(block_key)
                active_footnote_id = block_key
                continue

            normalized_block_ids.append(block_key)
            active_footnote_id = None

        updated_section["block_ids"] = normalized_block_ids
        updated_sections.append(updated_section)

    normalized_blocks = [block for block in blocks if str(block.get("id", "")) not in merged_away_ids]
    return normalized_blocks, updated_sections


def suppress_running_header_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    compact_text: Callable[[str], str],
    running_header_text_re: Pattern[str],
    short_word_re: Pattern[str],
    strip_known_running_header_text: Callable[[str], str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    def paragraph_block_text(block: dict[str, Any]) -> str:
        if str(block.get("type", "")) != "paragraph":
            return ""
        spans = block.get("content", {}).get("spans", [])
        parts: list[str] = []
        for span in spans:
            if not isinstance(span, dict):
                continue
            kind = str(span.get("kind", ""))
            if kind == "text":
                parts.append(str(span.get("text", "")))
            elif kind == "inline_math_ref":
                parts.append("[M]")
        return strip_known_running_header_text("".join(parts))

    def is_running_header_candidate_block(block: dict[str, Any]) -> bool:
        if str(block.get("type", "")) != "paragraph":
            return False
        text = paragraph_block_text(block)
        if not text or not running_header_text_re.fullmatch(text):
            return False
        words = short_word_re.findall(text)
        if not (1 <= len(words) <= 3):
            return False
        bbox = (block_source_spans(block)[:1] or [{}])[0].get("bbox", {})
        y0 = float(bbox.get("y0", 999.0))
        width = float(bbox.get("width", 0.0))
        height = float(bbox.get("height", 0.0))
        return y0 <= 50.0 and width <= 120.0 and 0.0 < height <= 18.0

    def trim_trailing_text_suffix(
        spans: list[dict[str, Any]],
        suffix: str,
    ) -> list[dict[str, Any]]:
        if not suffix:
            return [dict(span) for span in spans]
        updated = [dict(span) for span in spans]
        suffix_pattern = re.compile(rf"(?:\s+)?{re.escape(suffix)}\s*$")
        for index in range(len(updated) - 1, -1, -1):
            span = updated[index]
            if str(span.get("kind", "")) != "text":
                continue
            text = str(span.get("text", ""))
            if not compact_text(text):
                continue
            trimmed = suffix_pattern.sub("", text)
            if trimmed == text:
                continue
            span["text"] = trimmed
            updated[index] = span
            break
        while updated and str(updated[-1].get("kind", "")) == "text" and not compact_text(str(updated[-1].get("text", ""))):
            updated.pop()
        return updated

    header_counts: dict[str, int] = {}
    for block in blocks:
        if not is_running_header_candidate_block(block):
            continue
        text = paragraph_block_text(block)
        header_counts[text] = header_counts.get(text, 0) + 1
    running_headers = {text for text, count in header_counts.items() if count >= 3}
    if not running_headers:
        return blocks, sections

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    removed_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        kept_block_ids: list[str] = []
        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in removed_ids:
                continue

            if is_running_header_candidate_block(block) and paragraph_block_text(block) in running_headers:
                removed_ids.add(block_key)
                continue

            if str(block.get("type", "")) == "paragraph":
                text = paragraph_block_text(block)
                matched_header = next(
                    (
                        header
                        for header in sorted(running_headers, key=len, reverse=True)
                        if text.endswith(header)
                    ),
                    None,
                )
                if matched_header:
                    source_spans = list(block.get("source_spans", []))
                    header_like_spans = [
                        span
                        for span in source_spans
                        if float(span.get("bbox", {}).get("y0", 999.0)) <= 50.0
                        and float(span.get("bbox", {}).get("width", 0.0)) <= 120.0
                        and float(span.get("bbox", {}).get("height", 0.0)) <= 18.0
                    ]
                    if header_like_spans:
                        updated_block = dict(block)
                        updated_block["content"] = {
                            "spans": trim_trailing_text_suffix(
                                list(block.get("content", {}).get("spans", [])),
                                matched_header,
                            )
                        }
                        updated_block["source_spans"] = [
                            span
                            for span in source_spans
                            if span not in header_like_spans
                        ]
                        block_by_id[block_key] = updated_block

            kept_block_ids.append(block_key)

        updated_section["block_ids"] = kept_block_ids
        updated_sections.append(updated_section)

    filtered_blocks = [block_by_id[str(block.get("id", ""))] for block in blocks if str(block.get("id", "")) not in removed_ids]
    return filtered_blocks, updated_sections


def merge_code_records(
    records: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> list[dict[str, Any]]:
    def should_merge_code_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
        if previous.get("type") != "code" or current.get("type") != "code":
            return False

        previous_span = (block_source_spans(previous)[-1:] or [{}])[0]
        current_span = (block_source_spans(current)[:1] or [{}])[0]
        previous_page = int(previous_span.get("page", previous.get("page", 0)) or 0)
        current_page = int(current_span.get("page", current.get("page", 0)) or 0)
        if current_page != previous_page:
            return False

        previous_bbox = previous_span.get("bbox", {})
        current_bbox = current_span.get("bbox", {})
        previous_x0 = float(previous_bbox.get("x0", 0.0))
        current_x0 = float(current_bbox.get("x0", 0.0))
        previous_y1 = float(previous_bbox.get("y1", 0.0))
        current_y0 = float(current_bbox.get("y0", 0.0))
        vertical_gap = current_y0 - previous_y1

        if abs(current_x0 - previous_x0) > 36.0:
            return False
        if vertical_gap < -8.0 or vertical_gap > 36.0:
            return False
        return True

    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for record in records:
        if current is None:
            current = dict(record)
            current["source_spans"] = list(block_source_spans(record))
            current["meta"] = dict(record.get("meta", {}))
            continue

        if should_merge_code_records(current, record):
            current_text = clean_text(str(current.get("text", "")))
            next_text = clean_text(str(record.get("text", "")))
            joiner = " ;; " if current_text and next_text else ""
            current["text"] = f"{current_text}{joiner}{next_text}".strip()
            current["source_spans"].extend(block_source_spans(record))
            current["meta"]["source_record_ids"] = [
                *current["meta"].get("source_record_ids", [str(current.get("id", ""))]),
                str(record.get("id", "")),
            ]
            continue

        merged.append(current)
        current = dict(record)
        current["source_spans"] = list(block_source_spans(record))
        current["meta"] = dict(record.get("meta", {}))

    if current is not None:
        merged.append(current)
    return merged


def make_merge_code_records(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def build_merge_code_records(record_batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return merge_code_records(
            record_batch,
            block_source_spans=block_source_spans,
            clean_text=clean_text,
        )

    return build_merge_code_records


def make_merge_paragraph_records(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    table_caption_re: Pattern[str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def build_merge_paragraph_records(record_batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return merge_paragraph_records(
            record_batch,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            should_merge_paragraph_records=should_merge_paragraph_records,
            table_caption_re=table_caption_re,
        )

    return build_merge_paragraph_records


def make_suppress_running_header_blocks(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    compact_text: Callable[[str], str],
    running_header_text_re: Pattern[str],
    short_word_re: Pattern[str],
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def build_suppress_running_header_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return suppress_running_header_blocks(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            compact_text=compact_text,
            running_header_text_re=running_header_text_re,
            short_word_re=short_word_re,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return build_suppress_running_header_blocks


def make_normalize_footnote_blocks(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    short_word_re: Pattern[str],
    starts_like_sentence: Callable[[str], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def build_normalize_footnote_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return normalize_footnote_blocks(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            short_word_re=short_word_re,
            starts_like_sentence=starts_like_sentence,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return build_normalize_footnote_blocks


def make_merge_paragraph_blocks(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool],
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def build_merge_paragraph_blocks(
        blocks: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return merge_paragraph_blocks(
            blocks,
            sections,
            block_source_spans=block_source_spans,
            should_merge_paragraph_records=should_merge_paragraph_records,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return build_merge_paragraph_blocks
