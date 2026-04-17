from __future__ import annotations

from typing import Any

from pipeline.math.compile import (
    _compiled_formula_item as _compiled_formula_item_impl,
    _group_conversion_from_items,
    compile_formulas as compile_formulas_impl,
)
from pipeline.math.mathml import compile_latex_targets


def _compiled_formula_item(entry: dict[str, Any]) -> dict[str, Any]:
    return _compiled_formula_item_impl(
        entry,
        compile_latex_targets=compile_latex_targets,
    )


def compile_formulas(math_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return compile_formulas_impl(
        math_entries,
        compile_latex_targets=compile_latex_targets,
    )


__all__ = [
    "_compiled_formula_item",
    "_group_conversion_from_items",
    "compile_formulas",
    "compile_latex_targets",
]
