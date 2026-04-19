from __future__ import annotations

from typing import Any


GENERIC_LAYOUT_PROVIDER_NAMES = {"composed", "external_layout", "merged_layout"}
GENERIC_MATH_PROVIDER_NAMES = {"external_math"}


def reported_layout_provider(
    layout_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
    fallback: str = "native_pdf",
) -> str:
    if not layout_engine:
        return fallback
    preferred_provider = str((source_scorecard or {}).get("recommended_primary_layout_provider", "") or "")
    if layout_engine in GENERIC_LAYOUT_PROVIDER_NAMES and preferred_provider:
        return preferred_provider
    return layout_engine


def reported_math_provider(
    math_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
    math_payload: dict[str, Any] | None,
    fallback: str = "heuristic",
) -> str:
    math_entries = list((math_payload or {}).get("entries", []))
    preferred_provider = str((source_scorecard or {}).get("recommended_primary_math_provider", "") or "")
    if preferred_provider and math_entries:
        return preferred_provider
    if math_engine and math_entries and math_engine not in GENERIC_MATH_PROVIDER_NAMES:
        return math_engine
    return fallback


__all__ = [
    "reported_layout_provider",
    "reported_math_provider",
]
