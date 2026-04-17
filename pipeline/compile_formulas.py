from __future__ import annotations

from typing import Any

from pipeline.mathml_compiler import compile_latex_targets
from pipeline.types import default_formula_conversion


def _compiled_formula_item(entry: dict[str, Any]) -> dict[str, Any]:
    item = dict(entry)
    item.setdefault("semantic_expr", None)

    existing_targets = dict(item.get("compiled_targets", {}))
    existing_conversion = dict(item.get("conversion", default_formula_conversion()))
    if existing_targets and str(existing_conversion.get("status", "")) == "converted":
        item["compiled_targets"] = existing_targets
        item["conversion"] = existing_conversion
        return item

    compiled_targets, conversion = compile_latex_targets(str(item.get("display_latex", "")))
    item["compiled_targets"] = compiled_targets
    item["conversion"] = conversion
    return item


def _group_conversion_from_items(items: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not items:
        return {}, default_formula_conversion(notes="group has no items")

    mathml_items = [str(item.get("compiled_targets", {}).get("mathml", "")) for item in items]
    statuses = [str(item.get("conversion", {}).get("status", "unconverted")) for item in items]
    compiled_targets = {"mathml_items": mathml_items} if any(mathml_items) else {}

    converted_count = sum(status == "converted" for status in statuses)
    failed_count = sum(status == "failed" for status in statuses)
    total = len(statuses)

    if converted_count == total:
        return compiled_targets, default_formula_conversion(status="converted", notes=f"group items converted={converted_count}/{total}")
    if converted_count > 0:
        return compiled_targets, default_formula_conversion(
            status="partial",
            notes=f"group items converted={converted_count}/{total}; failed={failed_count}",
        )
    if failed_count > 0:
        return compiled_targets, default_formula_conversion(status="failed", notes=f"group items failed={failed_count}/{total}")
    return compiled_targets, default_formula_conversion(notes=f"group items converted=0/{total}")


def compile_formulas(math_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compiled: list[dict[str, Any]] = []
    for entry in math_entries:
        item = dict(entry)
        if item["kind"] == "group":
            items = []
            for group_item in item.get("items", []):
                next_item = _compiled_formula_item(group_item)
                items.append(next_item)
            item["items"] = items
            existing_targets = dict(item.get("compiled_targets", {}))
            existing_conversion = dict(item.get("conversion", default_formula_conversion()))
            if existing_targets and str(existing_conversion.get("status", "")) == "converted":
                item["compiled_targets"] = existing_targets
                item["conversion"] = existing_conversion
            else:
                item["compiled_targets"], item["conversion"] = _group_conversion_from_items(items)
            item.setdefault("semantic_expr", None)
            compiled.append(item)
            continue
        item = _compiled_formula_item(item)
        compiled.append(item)
    return compiled
