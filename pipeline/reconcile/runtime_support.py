from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def block_source_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
    spans = record.get("source_spans")
    if isinstance(spans, list):
        return spans
    return []


def normalize_formula_display_text(
    text: str,
    *,
    clean_text: Callable[[str], str],
    decode_ocr_codepoint_tokens: Callable[[str], tuple[str, Any]],
) -> str:
    normalized = clean_text(text)
    normalized, _ = decode_ocr_codepoint_tokens(normalized)
    return clean_text(normalized)


def mathish_ratio(
    text: str,
    *,
    word_count: Callable[[str], int],
    math_signal_count: Callable[[str], int],
) -> float:
    if not text:
        return 0.0
    normalized_word_count = max(word_count(text), 1)
    symbol_count = math_signal_count(text)
    return symbol_count / normalized_word_count


def page_height_map(layout: dict[str, Any]) -> dict[int, float]:
    return {
        int(page_info["page"]): float(page_info["height"])
        for page_info in layout.get("page_sizes_pt", [])
    }


def make_normalize_formula_display_text(
    *,
    clean_text: Callable[[str], str],
    decode_ocr_codepoint_tokens: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def bound_normalize_formula_display_text(text: str) -> str:
        return normalize_formula_display_text(
            text,
            clean_text=clean_text,
            decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
        )

    return bound_normalize_formula_display_text


def make_mathish_ratio(
    *,
    word_count: Callable[[str], int],
    math_signal_count: Callable[[str], int],
) -> Callable[[str], float]:
    def bound_mathish_ratio(text: str) -> float:
        return mathish_ratio(
            text,
            word_count=word_count,
            math_signal_count=math_signal_count,
        )

    return bound_mathish_ratio


__all__ = [
    "block_source_spans",
    "make_mathish_ratio",
    "make_normalize_formula_display_text",
    "mathish_ratio",
    "normalize_formula_display_text",
    "now_iso",
    "page_height_map",
]
