from __future__ import annotations

import re
from typing import Any, Callable, Pattern


def looks_like_vertical_label_cloud(
    text: str,
    spans: list[dict[str, Any]],
    *,
    strong_operator_count: Callable[[str], int],
) -> bool:
    raw_tokens = text.split()
    if len(raw_tokens) < 8 or len(spans) < 3:
        return False
    operator_count = strong_operator_count(text)
    if operator_count > 1 or text.count(".") >= 1 or text.count(":") >= 1:
        return False
    tall_narrow_span_count = sum(
        1
        for span in spans
        if (
            float(span.get("bbox", {}).get("height", 0.0)) >= 24.0
            and float(span.get("bbox", {}).get("width", 0.0)) <= 20.0
        )
        or (
            float(span.get("bbox", {}).get("height", 0.0))
            >= float(span.get("bbox", {}).get("width", 0.0)) * 2.5
            and float(span.get("bbox", {}).get("height", 0.0)) >= 24.0
        )
    )
    return tall_narrow_span_count >= max(3, len(spans) // 8)


def looks_like_table_marker_cloud(
    text: str,
    spans: list[dict[str, Any]],
    *,
    strong_operator_count: Callable[[str], int],
) -> bool:
    raw_tokens = text.split()
    if len(raw_tokens) < 8 or len(spans) < 6:
        return False
    operator_count = strong_operator_count(text)
    if operator_count > 1 or text.count(".") >= 1 or text.count(":") >= 1:
        return False
    marker_token_count = sum(
        1
        for token in raw_tokens
        if token in {"Y", "N", "X"} or re.fullmatch(r"\(\d+\)", token)
    )
    tiny_span_count = sum(
        1
        for span in spans
        if float(span.get("bbox", {}).get("height", 0.0)) <= 12.0 and float(span.get("bbox", {}).get("width", 0.0)) <= 16.0
    )
    return marker_token_count >= max(4, len(raw_tokens) // 3) and tiny_span_count >= max(4, len(spans) // 3)


def looks_like_browser_ui_scrap(text: str, *, short_word_re: Pattern[str]) -> bool:
    lowered = text.lower()
    if "localhost" not in lowered and "http://" not in lowered and "https://" not in lowered and "www." not in lowered:
        return False
    word_count = len(short_word_re.findall(text))
    if word_count > 24:
        return False
    symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
    return symbol_count >= 3 or any(token in text for token in ("?", "&", "="))


def looks_like_quoted_identifier_fragment(
    text: str,
    *,
    short_word_re: Pattern[str],
    quoted_identifier_fragment_re: Pattern[str],
) -> bool:
    words = short_word_re.findall(text)
    if len(words) > 6:
        return False
    return bool(quoted_identifier_fragment_re.fullmatch(text))


def looks_like_glyph_noise_cloud(text: str, *, short_word_re: Pattern[str]) -> bool:
    letters_only = re.sub(r"[^A-Za-z]", "", text).lower()
    if 4 <= len(letters_only) <= 64 and len(set(letters_only)) <= 3:
        dominant_count = max(letters_only.count(char) for char in set(letters_only))
        if dominant_count / len(letters_only) >= 0.7 and (text.count("~") >= 1 or text.count("!") >= 1):
            return True
    tokens = short_word_re.findall(text)
    if len(tokens) < 8:
        return False
    alpha_tokens = [token.lower() for token in tokens if token.isalpha()]
    if len(alpha_tokens) < 6:
        return False
    single_letter_count = sum(len(token) == 1 for token in alpha_tokens)
    if single_letter_count < max(6, int(len(alpha_tokens) * 0.7)):
        return False
    if len({token for token in alpha_tokens if len(token) == 1}) > 4:
        return False
    symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
    return symbol_count >= 6 or text.count("~") >= 3 or text.count("!") >= 2


def is_figure_debris(
    record: dict[str, Any],
    figures_by_page: dict[int, list[dict[str, Any]]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    diagram_decision_re: Pattern[str],
    diagram_query_re: Pattern[str],
    diagram_action_re: Pattern[str],
    terminal_punctuation_re: Pattern[str],
    short_word_re: Pattern[str],
    rect_intersection_area: Callable[[dict[str, Any], dict[str, Any]], float],
) -> bool:
    if record.get("type") not in {"paragraph", "heading"}:
        return False
    text = clean_text(str(record.get("text", "")))
    if not text:
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and (
        isinstance(meta.get("external_math_entry"), dict) or meta.get("source_math_entry_id")
    ):
        return False
    source_span = (block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    bbox = source_span.get("bbox", {})
    figures = figures_by_page.get(page, [])
    if not figures:
        return False

    if text.startswith("Figure"):
        return True
    words = short_word_re.findall(text)
    if diagram_decision_re.match(text):
        return True
    if (
        text.count("_") >= 2
        and len(words) <= 24
        and not terminal_punctuation_re.search(text)
    ):
        return True
    if (
        len(words) <= 28
        and not terminal_punctuation_re.search(text)
        and (diagram_query_re.match(text) or diagram_action_re.match(text))
    ):
        return True

    area = max(float(bbox.get("width", 0.0)) * float(bbox.get("height", 0.0)), 1.0)
    word_count = len(words)
    short_label_like = (
        word_count <= 8
        and float(bbox.get("height", 0.0)) <= 12.0
        and terminal_punctuation_re.search(text) is None
    )
    center_x = (float(bbox.get("x0", 0.0)) + float(bbox.get("x1", 0.0))) / 2.0
    center_y = (float(bbox.get("y0", 0.0)) + float(bbox.get("y1", 0.0))) / 2.0
    for figure in figures:
        figure_bbox = figure.get("bbox", {})
        overlap = rect_intersection_area(bbox, figure_bbox)
        if overlap / area >= 0.7:
            return True
        if word_count <= 4 and overlap / area >= 0.2:
            return True
        if short_label_like and overlap / area >= 0.15:
            return True
        if (
            (word_count <= 4 or short_label_like)
            and float(figure_bbox.get("x0", 0.0)) <= center_x <= float(figure_bbox.get("x1", 0.0))
            and float(figure_bbox.get("y0", 0.0)) <= center_y <= float(figure_bbox.get("y1", 0.0))
        ):
            return True
    return False


def is_short_ocr_fragment(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    looks_like_browser_ui_scrap: Callable[[str], bool],
    looks_like_quoted_identifier_fragment: Callable[[str], bool],
    looks_like_glyph_noise_cloud: Callable[[str], bool],
    looks_like_vertical_label_cloud: Callable[[str, list[dict[str, Any]]], bool],
    looks_like_table_marker_cloud: Callable[[str, list[dict[str, Any]]], bool],
    short_word_re: Pattern[str],
    label_cloud_token_re: Pattern[str],
    short_ocr_noise_re: Pattern[str],
    terminal_punctuation_re: Pattern[str],
    strong_operator_count: Callable[[str], int],
) -> bool:
    if record.get("type") != "paragraph":
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and meta.get("external_math_entry"):
        return False
    text = clean_text(str(record.get("text", "")))
    if not text:
        return True
    spans = block_source_spans(record)
    lowered = text.lower()
    span_widths = [float(span.get("bbox", {}).get("width", 0.0)) for span in spans]
    if text in {"*", "∗"}:
        return True
    if looks_like_browser_ui_scrap(text):
        return True
    if looks_like_quoted_identifier_fragment(text):
        return True
    if looks_like_glyph_noise_cloud(text):
        return True
    if lowered in {"end if", "end while", "end for", "else"} and len(short_word_re.findall(text)) <= 2:
        return True
    if any(float(span.get("bbox", {}).get("width", 0.0)) <= 1.0 for span in spans) and text.lower().startswith("negationslash"):
        return True
    if (
        len(spans) >= 3
        and span_widths
        and max(span_widths) <= 8.0
        and lowered.count(" are in ") >= 2
        and lowered.count(".") >= 2
    ):
        return True
    if looks_like_vertical_label_cloud(text, spans) or looks_like_table_marker_cloud(text, spans):
        return True
    if isinstance(meta, dict) and meta.get("forced_math_kind"):
        raw_tokens = text.split()
        if len(raw_tokens) >= 8:
            label_like_count = 0
            for token in raw_tokens:
                compact = token.strip(".,;:")
                if label_cloud_token_re.fullmatch(compact):
                    label_like_count += 1
                    continue
                if len(compact) <= 4 and any(ord(char) > 127 for char in compact):
                    label_like_count += 1
            operator_count = strong_operator_count(text)
            if label_like_count / max(len(raw_tokens), 1) >= 0.7 and operator_count <= 1:
                return True
    if len(text) <= 12 and short_ocr_noise_re.match(text):
        return True
    words = short_word_re.findall(text)
    lowercase_words = sum(1 for word in words if word.islower())
    if lowered in {"where", "where:"}:
        return False
    span_heights = [float(span.get("bbox", {}).get("height", 0.0)) for span in spans]
    tiny_span_count = sum(1 for height in span_heights if 0.0 < height <= 4.5)
    if tiny_span_count >= max(3, len(span_heights) // 2 + len(span_heights) % 2):
        digit_count = sum(char.isdigit() for char in text)
        symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
        non_ascii_count = sum(ord(char) > 127 for char in text)
        titlecase_like = sum(1 for word in words if word[:1].isupper())
        if not any(token in text for token in ("=", "\\", "{", "}", "^", "_")):
            if digit_count >= 2 or text.count(":") >= 1 or non_ascii_count >= 1 or symbol_count >= 4:
                return True
            if titlecase_like >= max(4, lowercase_words + 3):
                return True
    bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))
    x0 = float(bbox.get("x0", 0.0))
    y0 = float(bbox.get("y0", 0.0))
    if y0 <= 40.0 and x0 <= 4.0:
        if text[:1] in {":", ";", ",", ".", "-"} and len(words) <= 40:
            return True
        if len(words) <= 18 and lowercase_words >= max(3, len(words) - 2) and not terminal_punctuation_re.search(text):
            return True
    if height and height <= 14.0:
        if len(words) <= 2 and width <= 120.0:
            return True
        if len(words) <= 3 and width <= 120.0 and lowercase_words >= max(2, len(words) - 1):
            return True
        if len(words) <= 4 and width <= 95.0:
            return True
        if len(words) <= 6 and width <= 70.0:
            return True
    if width <= 20.0 and len(words) <= 1 and height <= 28.0:
        return True
    if (
        height
        and height <= 8.0
        and width <= 120.0
        and len(words) <= 8
        and lowercase_words >= 2
        and terminal_punctuation_re.search(text) is None
    ):
        return True
    if height and height <= 10.0 and width <= 60.0 and len(words) <= 10 and lowercase_words >= max(3, len(words) - 2):
        return True
    if height and height <= 4.5:
        if len(words) <= 12:
            return True
        digit_count = sum(char.isdigit() for char in text)
        symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
        non_ascii_count = sum(ord(char) > 127 for char in text)
        titlecase_like = sum(1 for word in words if word[:1].isupper())
        if digit_count >= 2 or symbol_count >= 2 or non_ascii_count >= 1:
            return True
        if titlecase_like >= max(4, lowercase_words + 3):
            return True
    y_positions = [float(span.get("bbox", {}).get("y0", 0.0)) for span in spans if span.get("bbox")]
    if len(words) <= 6 and not terminal_punctuation_re.search(text):
        if len(y_positions) >= 2 and max(y_positions) - min(y_positions) >= 24.0 and lowercase_words >= max(2, len(words) - 1):
            return True
        if float(bbox.get("y0", 0.0)) <= 80.0 and lowercase_words >= max(2, len(words) - 1):
            return True
    if height and height <= 6.0 and len(words) <= 12 and lowercase_words >= max(3, len(words) - 2):
        return True
    if len(words) > 3 or len(text) > 24:
        return False
    if re.search(r"[A-Z][a-z]{2,}", text):
        return False
    if width and width > 80 and height < 30:
        return False
    return True
