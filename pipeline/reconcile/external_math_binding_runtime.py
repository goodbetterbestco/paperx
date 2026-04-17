from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.external_math import (
    inject_external_math_records as external_inject_external_math_records,
)
from pipeline.reconcile.math_suppression import (
    looks_like_leading_display_math_echo as suppression_looks_like_leading_display_math_echo,
)
from pipeline.types import LayoutBlock


def make_inject_external_math_records(
    *,
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Any,
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
) -> Callable[[list[dict[str, Any]], list[LayoutBlock], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]]:
    def inject_external_math_records(
        records: list[dict[str, Any]],
        layout_blocks: list[LayoutBlock],
        external_math_entries: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], set[str]]:
        return external_inject_external_math_records(
            records,
            layout_blocks,
            external_math_entries,
            clean_text=clean_text,
            looks_like_leading_display_math_echo=lambda text: suppression_looks_like_leading_display_math_echo(
                text,
                clean_text=clean_text,
                display_math_prose_cue_re=display_math_prose_cue_re,
                mathish_ratio=mathish_ratio,
                strong_operator_count=strong_operator_count,
            ),
        )

    return inject_external_math_records
