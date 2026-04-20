from __future__ import annotations

import re
from typing import Any, Callable


def starts_like_sentence(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped:
        return False
    first = stripped[0]
    return first.isupper() or first.isdigit() or stripped.startswith(("(", '"', "'"))


def starts_like_paragraph_continuation(text: str, *, clean_text: Callable[[str], str]) -> bool:
    stripped = clean_text(text)
    if not stripped:
        return False
    if stripped[:1].islower():
        return True
    return bool(re.match(r"^(?:and|but|or|then|thus|therefore|however|where|which|with|while|when|since|because|as)\b", stripped, re.IGNORECASE))


def starts_like_strong_paragraph_continuation(text: str, *, clean_text: Callable[[str], str]) -> bool:
    stripped = clean_text(text)
    if not stripped:
        return False
    return bool(re.match(r"^(?:then|with|where|representing|is|are)\b", stripped, re.IGNORECASE))


def ends_like_short_lead_in(text: str, *, clean_text: Callable[[str], str]) -> bool:
    cleaned = clean_text(text).lower()
    if not cleaned:
        return False
    if cleaned.endswith(("consists of", "defined as", "given by", "represented as")):
        return True
    return cleaned.endswith((" of", " by", " as", " with", " from", " to", " that"))


def ends_like_clause_lead_in(text: str, *, clean_text: Callable[[str], str]) -> bool:
    cleaned = clean_text(text).lower()
    if not cleaned:
        return False
    return bool(re.search(r"\b(?:which|that|where|when|while|whose|because|since|as)$", cleaned))


def is_paragraph_like_record(record: dict[str, Any]) -> bool:
    return str(record.get("type", "")) in {"paragraph", "front_matter"}


def merge_anchor_spans(
    record: dict[str, Any],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    spans = list(block_source_spans(record))
    if len(spans) <= 1:
        return spans
    body_like_spans: list[dict[str, Any]] = []
    wide_body_like_spans: list[dict[str, Any]] = []
    for span in spans:
        bbox = span.get("bbox", {}) if isinstance(span, dict) else {}
        y0 = float(bbox.get("y0", 0.0))
        height = float(bbox.get("height", 0.0))
        width = float(bbox.get("width", 0.0))
        if y0 > 80.0 or height > 10.0:
            body_like_spans.append(span)
            if width >= 100.0:
                wide_body_like_spans.append(span)
    return wide_body_like_spans or body_like_spans or spans


def looks_like_running_header_record(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    running_header_text_re: Any,
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> bool:
    if str(record.get("type", "")) not in {"paragraph", "heading"}:
        return False
    text = clean_text(str(record.get("text", "")))
    if not text or running_header_text_re.fullmatch(text) is None:
        return False
    words = short_word_re.findall(text)
    if not words or len(words) > 6:
        return False
    bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 0.0))
    width = float(bbox.get("width", 0.0))
    return y0 <= 100.0 and 80.0 <= width <= 320.0


def looks_like_table_body_debris(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> bool:
    if str(record.get("type", "")) != "paragraph":
        return False
    text = clean_text(str(record.get("text", "")))
    if not text:
        return False
    spans = block_source_spans(record)
    if len(spans) < 12:
        return False
    words = text.split()
    if len(words) < 20:
        return False
    span_widths = [float(span.get("bbox", {}).get("width", 0.0)) for span in spans]
    if not span_widths:
        return False
    narrow_span_count = sum(1 for width in span_widths if 0.0 < width <= 40.0)
    if narrow_span_count < len(span_widths) * 0.65:
        return False
    short_or_numeric_token_count = 0
    for token in words:
        compact = token.strip(".,;:()[]{}")
        letters_only = re.sub(r"[^A-Za-z]", "", compact)
        if any(char.isdigit() for char in compact) or len(letters_only) <= 3:
            short_or_numeric_token_count += 1
    return short_or_numeric_token_count / max(len(words), 1) >= 0.55


def suppress_embedded_table_headings(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    table_caption_re: Any,
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for record in records:
        if str(record.get("type", "")) == "heading":
            text = clean_text(str(record.get("text", "")))
            bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
            y0 = float(bbox.get("y0", 0.0))
            previous = kept[-1] if kept else None
            previous_bbox = (block_source_spans(previous)[:1] or [{}])[0].get("bbox", {}) if previous else {}
            previous_page = int((((block_source_spans(previous)[:1] or [{}])[0].get("page", previous.get("page", 0)) if previous else 0) or 0))
            current_page = int((((block_source_spans(record)[:1] or [{}])[0].get("page", record.get("page", 0))) or 0))
            previous_text = clean_text(str(previous.get("text", ""))) if previous else ""
            if (
                previous is not None
                and str(previous.get("type", "")) == "caption"
                and previous_page == current_page
                and table_caption_re.match(previous_text)
                and parse_heading_label(clean_heading_title(text)) is None
                and 0.0 <= y0 - float(previous_bbox.get("y1", 0.0)) <= 80.0
            ):
                continue
        kept.append(record)
    return kept


def looks_like_same_page_column_continuation(
    previous_x0: float,
    previous_y0: float,
    previous_y1: float,
    current_x0: float,
    current_y0: float,
) -> bool:
    return current_x0 >= previous_x0 + 80 and current_y0 + 30 < previous_y1 and current_y0 <= previous_y0 + 24


def should_merge_paragraph_records(
    previous: dict[str, Any],
    current: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    terminal_punctuation_re: Any,
) -> bool:
    if not is_paragraph_like_record(previous) or not is_paragraph_like_record(current):
        return False
    if previous.get("meta", {}).get("forced_math_kind") or current.get("meta", {}).get("forced_math_kind"):
        return False
    if previous.get("meta", {}).get("external_display_math_overlap_count") or current.get("meta", {}).get("external_display_math_overlap_count"):
        return False

    previous_text = clean_text(str(previous.get("text", "")))
    current_text = clean_text(str(current.get("text", "")))
    if not previous_text or not current_text:
        return False
    previous_word_count = len(short_word_re.findall(previous_text))
    current_word_count = len(short_word_re.findall(current_text))

    previous_span = (merge_anchor_spans(previous, block_source_spans=block_source_spans)[-1:] or [{}])[0]
    current_span = (merge_anchor_spans(current, block_source_spans=block_source_spans)[:1] or [{}])[0]
    previous_bbox = previous_span.get("bbox", {})
    current_bbox = current_span.get("bbox", {})
    previous_page = int(previous_span.get("page", previous.get("page", 0)) or 0)
    current_page = int(current_span.get("page", current.get("page", 0)) or 0)
    previous_x0 = float(previous_bbox.get("x0", 0.0))
    current_x0 = float(current_bbox.get("x0", 0.0))
    previous_y0 = float(previous_bbox.get("y0", 0.0))
    previous_y1 = float(previous_bbox.get("y1", 0.0))
    previous_width = float(previous_bbox.get("width", 0.0))
    current_y0 = float(current_bbox.get("y0", 0.0))
    current_width = float(current_bbox.get("width", 0.0))
    vertical_gap = current_y0 - previous_y1
    previous_has_terminal = terminal_punctuation_re.search(previous_text) is not None
    current_continues = starts_like_paragraph_continuation(current_text, clean_text=clean_text)

    if current_page == previous_page:
        if not previous_has_terminal and current_continues and current_width <= 1.0 and 0.0 <= vertical_gap <= 24.0:
            return True
        if not previous_has_terminal and current_continues and 0.0 <= vertical_gap <= 14.0:
            return True
        if (
            not previous_has_terminal
            and current_continues
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 48.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and starts_like_strong_paragraph_continuation(current_text, clean_text=clean_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and 0.0 <= vertical_gap <= 180.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and previous_text.strip().lower() in {"where", "where:"}
            and starts_like_strong_paragraph_continuation(current_text, clean_text=clean_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 120.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and starts_like_strong_paragraph_continuation(current_text, clean_text=clean_text)
            and previous_word_count <= 6
            and ends_like_short_lead_in(previous_text, clean_text=clean_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 120.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and current_text[:1].islower()
            and previous_word_count >= 12
            and ends_like_short_lead_in(previous_text, clean_text=clean_text)
            and abs(current_x0 - previous_x0) <= 32.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and previous_y0 <= 120.0
            and 120.0 < vertical_gap <= 420.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_word_count >= 12
            and current_word_count >= 5
            and ends_like_clause_lead_in(previous_text, clean_text=clean_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and 0.0 <= vertical_gap <= 140.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_text.rstrip().endswith(",")
            and previous_word_count <= 20
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 240.0
            and current_width >= 240.0
            and 0.0 <= vertical_gap <= 220.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_x0 - current_x0 >= 120.0
            and previous_width >= 220.0
            and current_width <= 180.0
            and 0.0 <= vertical_gap <= 64.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_y0 - 24.0 <= current_y0 <= previous_y1 + 4.0
        ):
            return True
        if not previous_has_terminal and current_continues and looks_like_same_page_column_continuation(
            previous_x0,
            previous_y0,
            previous_y1,
            current_x0,
            current_y0,
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_text.rstrip().endswith("-")
            and current_x0 >= previous_x0 + 80.0
            and current_y0 + 24.0 < previous_y1
            and current_y0 <= previous_y0 + 16.0
        ):
            return True
        if current_y0 < previous_y0 - 24.0:
            return False
        if vertical_gap > 18:
            return False
        if current_y0 <= previous_y1 + 2 and current_y0 >= previous_y0 - 2:
            return True
        if (previous_word_count <= 3 or current_word_count <= 3) and 0.0 <= vertical_gap <= 14.0:
            return True
    elif current_page == previous_page + 1:
        if previous_has_terminal:
            return False
        if current_continues and current_y0 <= 140:
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_word_count >= 20
            and current_word_count >= 8
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 500.0
            and current_width >= 500.0
        ):
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_word_count >= 12
            and current_word_count <= 16
            and previous_width >= 220.0
            and current_width >= 220.0
            and current_x0 + 80.0 <= previous_x0
        ):
            return True
        if (
            current_continues
            and previous_word_count >= 20
            and previous_width >= 220.0
            and current_width >= 220.0
            and current_y0 <= 240.0
        ):
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_text.rstrip().endswith("and")
            and previous_word_count >= 20
            and current_word_count >= 8
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 400.0
            and current_width >= 400.0
            and current_y0 <= 360.0
        ):
            return True
        if current_y0 > 120:
            return False
    else:
        return False

    if current_page == previous_page and abs(current_x0 - previous_x0) > 24:
        return False

    current_starts_sentence = starts_like_sentence(current_text)
    if previous_has_terminal and current_starts_sentence and current_x0 >= previous_x0 - 2:
        return False
    return True


def make_starts_like_paragraph_continuation(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def bound_starts_like_paragraph_continuation(text: str) -> bool:
        return starts_like_paragraph_continuation(
            text,
            clean_text=clean_text,
        )

    return bound_starts_like_paragraph_continuation


def make_starts_like_strong_paragraph_continuation(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def bound_starts_like_strong_paragraph_continuation(text: str) -> bool:
        return starts_like_strong_paragraph_continuation(
            text,
            clean_text=clean_text,
        )

    return bound_starts_like_strong_paragraph_continuation


def make_ends_like_short_lead_in(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def bound_ends_like_short_lead_in(text: str) -> bool:
        return ends_like_short_lead_in(
            text,
            clean_text=clean_text,
        )

    return bound_ends_like_short_lead_in


def make_ends_like_clause_lead_in(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str], bool]:
    def bound_ends_like_clause_lead_in(text: str) -> bool:
        return ends_like_clause_lead_in(
            text,
            clean_text=clean_text,
        )

    return bound_ends_like_clause_lead_in


def make_merge_anchor_spans(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def bound_merge_anchor_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
        return merge_anchor_spans(
            record,
            block_source_spans=block_source_spans,
        )

    return bound_merge_anchor_spans


def make_looks_like_running_header_record(
    *,
    clean_text: Callable[[str], str],
    running_header_text_re: Any,
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], bool]:
    def bound_looks_like_running_header_record(record: dict[str, Any]) -> bool:
        return looks_like_running_header_record(
            record,
            clean_text=clean_text,
            running_header_text_re=running_header_text_re,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
        )

    return bound_looks_like_running_header_record


def make_looks_like_table_body_debris(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], bool]:
    def bound_looks_like_table_body_debris(record: dict[str, Any]) -> bool:
        return looks_like_table_body_debris(
            record,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
        )

    return bound_looks_like_table_body_debris


def make_suppress_embedded_table_headings(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    table_caption_re: Any,
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def bound_suppress_embedded_table_headings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return suppress_embedded_table_headings(
            records,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            table_caption_re=table_caption_re,
            parse_heading_label=parse_heading_label,
            clean_heading_title=clean_heading_title,
        )

    return bound_suppress_embedded_table_headings


def make_should_merge_paragraph_records(
    *,
    clean_text: Callable[[str], str],
    short_word_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    terminal_punctuation_re: Any,
) -> Callable[[dict[str, Any], dict[str, Any]], bool]:
    def bound_should_merge_paragraph_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
        return should_merge_paragraph_records(
            previous,
            current,
            clean_text=clean_text,
            short_word_re=short_word_re,
            block_source_spans=block_source_spans,
            terminal_punctuation_re=terminal_punctuation_re,
        )

    return bound_should_merge_paragraph_records


__all__ = [
    "ends_like_clause_lead_in",
    "ends_like_short_lead_in",
    "is_paragraph_like_record",
    "looks_like_running_header_record",
    "looks_like_same_page_column_continuation",
    "looks_like_table_body_debris",
    "make_ends_like_clause_lead_in",
    "make_ends_like_short_lead_in",
    "make_looks_like_running_header_record",
    "make_looks_like_table_body_debris",
    "make_merge_anchor_spans",
    "make_should_merge_paragraph_records",
    "make_starts_like_paragraph_continuation",
    "make_starts_like_strong_paragraph_continuation",
    "make_suppress_embedded_table_headings",
    "merge_anchor_spans",
    "should_merge_paragraph_records",
    "starts_like_paragraph_continuation",
    "starts_like_sentence",
    "starts_like_strong_paragraph_continuation",
    "suppress_embedded_table_headings",
]
