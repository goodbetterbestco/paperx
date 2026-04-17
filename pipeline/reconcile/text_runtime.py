from __future__ import annotations

from typing import Any, Callable


def make_normalize_text_for_layout(
    *,
    normalize_text_impl: Callable[..., tuple[str, Any]],
    layout: Any,
) -> Callable[[str], tuple[str, Any]]:
    def normalize_text_for_layout(text: str) -> tuple[str, Any]:
        return normalize_text_impl(text, layout=layout)

    return normalize_text_for_layout


def make_normalize_paragraph_text(
    *,
    normalize_paragraph_text_impl: Callable[..., str],
    strip_known_running_header_text: Callable[[str], str],
    leading_negationslash_artifact_re: Any,
    leading_ocr_marker_re: Any,
    leading_punct_artifact_re: Any,
    leading_var_artifact_re: Any,
    trailing_numeric_artifact_re: Any,
    normalize_prose_text: Callable[[str], tuple[str, Any]],
    clean_text: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_paragraph_text(text: str) -> str:
        return normalize_paragraph_text_impl(
            text,
            strip_known_running_header_text=strip_known_running_header_text,
            leading_negationslash_artifact_re=leading_negationslash_artifact_re,
            leading_ocr_marker_re=leading_ocr_marker_re,
            leading_punct_artifact_re=leading_punct_artifact_re,
            leading_var_artifact_re=leading_var_artifact_re,
            trailing_numeric_artifact_re=trailing_numeric_artifact_re,
            normalize_prose_text=normalize_prose_text,
            clean_text=clean_text,
        )

    return normalize_paragraph_text


def make_normalize_figure_caption_text(
    *,
    normalize_figure_caption_text_impl: Callable[..., str],
    clean_text: Callable[[str], str],
    normalize_prose_text: Callable[[str], tuple[str, Any]],
) -> Callable[[str], str]:
    def normalize_figure_caption_text(text: str) -> str:
        return normalize_figure_caption_text_impl(
            text,
            clean_text=clean_text,
            normalize_prose_text=normalize_prose_text,
        )

    return normalize_figure_caption_text


def make_reference_entry_builder(
    *,
    make_reference_entry_impl: Callable[..., dict[str, Any]],
    clean_text: Callable[[str], str],
    normalize_reference_text: Callable[[str], tuple[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    default_review: Callable[..., dict[str, Any]],
) -> Callable[[dict[str, Any], int], dict[str, Any]]:
    def make_reference_entry(record: dict[str, Any], index: int) -> dict[str, Any]:
        return make_reference_entry_impl(
            record,
            index,
            clean_text=clean_text,
            normalize_reference_text=normalize_reference_text,
            block_source_spans=block_source_spans,
            default_review=default_review,
        )

    return make_reference_entry


def build_reconcile_text_runtime_helpers(
    *,
    runtime_layout: Any,
    bindings: Any,
) -> dict[str, Any]:
    clean_text = bindings.clean_text
    block_source_spans = bindings.block_source_spans
    default_review = bindings.default_review
    normalize_title_key = bindings.normalize_title_key
    parse_heading_label = bindings.parse_heading_label
    strip_known_running_header_text = bindings.strip_known_running_header_text
    short_word_re = bindings.short_word_re

    normalize_prose_text_for_layout = make_normalize_text_for_layout(
        normalize_text_impl=bindings.normalize_prose_text_impl,
        layout=runtime_layout,
    )
    normalize_reference_text_for_layout = make_normalize_text_for_layout(
        normalize_text_impl=bindings.normalize_reference_text_impl,
        layout=runtime_layout,
    )
    normalize_paragraph_text = make_normalize_paragraph_text(
        normalize_paragraph_text_impl=bindings.normalize_paragraph_text_impl,
        strip_known_running_header_text=strip_known_running_header_text,
        leading_negationslash_artifact_re=bindings.leading_negationslash_artifact_re,
        leading_ocr_marker_re=bindings.leading_ocr_marker_re,
        leading_punct_artifact_re=bindings.leading_punct_artifact_re,
        leading_var_artifact_re=bindings.leading_var_artifact_re,
        trailing_numeric_artifact_re=bindings.trailing_numeric_artifact_re,
        normalize_prose_text=normalize_prose_text_for_layout,
        clean_text=clean_text,
    )
    return {
        "clean_text": clean_text,
        "block_source_spans": block_source_spans,
        "default_review": default_review,
        "normalize_title_key": normalize_title_key,
        "parse_heading_label": parse_heading_label,
        "strip_known_running_header_text": strip_known_running_header_text,
        "short_word_re": short_word_re,
        "normalize_paragraph_text": normalize_paragraph_text,
        "normalize_figure_caption_text": make_normalize_figure_caption_text(
            normalize_figure_caption_text_impl=bindings.normalize_figure_caption_text_impl,
            clean_text=clean_text,
            normalize_prose_text=normalize_prose_text_for_layout,
        ),
        "make_reference_entry": make_reference_entry_builder(
            make_reference_entry_impl=bindings.make_reference_entry_impl,
            clean_text=clean_text,
            normalize_reference_text=normalize_reference_text_for_layout,
            block_source_spans=block_source_spans,
            default_review=default_review,
        ),
    }
