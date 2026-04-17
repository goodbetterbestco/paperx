from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.layout_records import (
    absorb_figure_caption_continuations as layout_absorb_figure_caption_continuations,
    append_figure_caption_fragment as layout_append_figure_caption_fragment,
    figure_label_token as layout_figure_label_token,
    layout_record as layout_layout_record,
    match_figure_for_caption_record as layout_match_figure_for_caption_record,
    page_one_front_matter_records as layout_page_one_front_matter_records,
    record_bbox as layout_record_bbox,
    rect_x_overlap_ratio as layout_rect_x_overlap_ratio,
    strip_caption_label_prefix as layout_strip_caption_label_prefix,
    synthetic_caption_record as layout_synthetic_caption_record,
)
from pipeline.types import LayoutBlock


figure_label_token = layout_figure_label_token
synthetic_caption_record = layout_synthetic_caption_record
rect_x_overlap_ratio = layout_rect_x_overlap_ratio


def make_layout_record(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[LayoutBlock], dict[str, Any]]:
    def layout_record(block: LayoutBlock) -> dict[str, Any]:
        return layout_layout_record(
            block,
            clean_text=clean_text,
        )

    return layout_record


def make_page_one_front_matter_records(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[LayoutBlock]]],
    layout_record: Callable[[LayoutBlock], dict[str, Any]],
) -> Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]:
    def page_one_front_matter_records(
        records: list[dict[str, Any]],
        mathpix_layout: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return layout_page_one_front_matter_records(
            records,
            mathpix_layout,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
            layout_record=layout_record,
        )

    return page_one_front_matter_records


def make_record_bbox(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def record_bbox(record: dict[str, Any]) -> dict[str, Any]:
        return layout_record_bbox(
            record,
            block_source_spans=block_source_spans,
        )

    return record_bbox


def make_strip_caption_label_prefix(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[str, dict[str, Any] | None], str]:
    def strip_caption_label_prefix(text: str, figure: dict[str, Any] | None = None) -> str:
        return layout_strip_caption_label_prefix(
            text,
            clean_text=clean_text,
            figure=figure,
        )

    return strip_caption_label_prefix


def make_append_figure_caption_fragment(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    normalize_figure_caption_text: Callable[[str], str],
    strip_caption_label_prefix: Callable[[str, dict[str, Any] | None], str],
) -> Callable[[dict[str, Any], str], None]:
    def append_figure_caption_fragment(figure: dict[str, Any], fragment: str) -> None:
        return layout_append_figure_caption_fragment(
            figure,
            fragment,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            normalize_figure_caption_text=normalize_figure_caption_text,
            strip_caption_label_prefix=strip_caption_label_prefix,
        )

    return append_figure_caption_fragment


def make_match_figure_for_caption_record(
    *,
    record_bbox: Callable[[dict[str, Any]], dict[str, Any]],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
    figure_label_token: Callable[[dict[str, Any]], str | None],
) -> Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any] | None]:
    def match_figure_for_caption_record(
        record: dict[str, Any],
        figures_on_page: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        return layout_match_figure_for_caption_record(
            record,
            figures_on_page,
            record_bbox=record_bbox,
            rect_x_overlap_ratio=rect_x_overlap_ratio,
            figure_label_token=figure_label_token,
        )

    return match_figure_for_caption_record


def make_absorb_figure_caption_continuations(
    *,
    match_figure_for_caption_record: Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any] | None],
    append_figure_caption_fragment: Callable[[dict[str, Any], str], None],
) -> Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]]:
    def absorb_figure_caption_continuations(
        records: list[dict[str, Any]],
        figures: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return layout_absorb_figure_caption_continuations(
            records,
            figures,
            match_figure_for_caption_record=match_figure_for_caption_record,
            append_figure_caption_fragment=append_figure_caption_fragment,
        )

    return absorb_figure_caption_continuations
