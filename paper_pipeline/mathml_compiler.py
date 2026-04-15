from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable

from paper_pipeline.types import default_formula_conversion

MAX_CONVERSION_NOTE_LENGTH = 160


@lru_cache(maxsize=1)
def _load_latex_to_mathml_converter() -> tuple[str | None, Callable[[str], str] | None]:
    try:
        from latex2mathml.converter import convert as latex_to_mathml  # type: ignore
    except ModuleNotFoundError:
        return None, None
    return "latex2mathml", latex_to_mathml


def _normalize_note(note: str) -> str:
    compact = " ".join(note.split())
    if len(compact) <= MAX_CONVERSION_NOTE_LENGTH:
        return compact
    return compact[: MAX_CONVERSION_NOTE_LENGTH - 1].rstrip() + "…"


def compile_latex_targets(latex: str) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized_latex = str(latex or "").strip()
    if not normalized_latex:
        return {}, default_formula_conversion(notes="empty display_latex")

    backend_name, converter = _load_latex_to_mathml_converter()
    if converter is None or backend_name is None:
        return {}, default_formula_conversion(notes="latex2mathml unavailable")

    try:
        mathml = str(converter(normalized_latex)).strip()
    except Exception as exc:  # pragma: no cover - exercised through seam tests
        return {}, default_formula_conversion(status="failed", notes=_normalize_note(f"{backend_name}: {exc}"))

    if not mathml:
        return {}, default_formula_conversion(status="failed", notes=f"{backend_name}: empty MathML output")

    return {"mathml": mathml}, default_formula_conversion(status="converted", notes=f"backend={backend_name}")
