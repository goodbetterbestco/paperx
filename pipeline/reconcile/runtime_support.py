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
