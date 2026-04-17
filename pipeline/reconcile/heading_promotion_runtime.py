from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.heading_promotion import (
    decode_control_heading_label as heading_decode_control_heading_label,
    normalize_decoded_heading_title as heading_normalize_decoded_heading_title,
    split_embedded_heading_paragraph as heading_split_embedded_heading_paragraph,
)


decode_control_heading_label = heading_decode_control_heading_label


def make_normalize_decoded_heading_title(
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_decoded_heading_title(title: str) -> str:
        return heading_normalize_decoded_heading_title(
            title,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
        )

    return normalize_decoded_heading_title


def make_split_embedded_heading_paragraph(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    embedded_heading_prefix_re: Any,
    normalize_decoded_heading_title: Callable[[str], str],
    collapse_ocr_split_caps: Callable[[str], str],
    looks_like_bad_heading: Callable[[str], bool],
    short_word_re: Any,
) -> Callable[[dict[str, Any]], tuple[str, str] | None]:
    def split_embedded_heading_paragraph(record: dict[str, Any]) -> tuple[str, str] | None:
        return heading_split_embedded_heading_paragraph(
            record,
            clean_text=clean_text,
            block_source_spans=block_source_spans,
            embedded_heading_prefix_re=embedded_heading_prefix_re,
            normalize_decoded_heading_title=normalize_decoded_heading_title,
            collapse_ocr_split_caps=collapse_ocr_split_caps,
            looks_like_bad_heading=looks_like_bad_heading,
            short_word_re=short_word_re,
        )

    return split_embedded_heading_paragraph
