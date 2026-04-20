from __future__ import annotations

from typing import Any


GENERIC_LAYOUT_PROVIDER_NAMES = {"composed", "external_layout", "merged_layout"}
GENERIC_MATH_PROVIDER_NAMES = {"external_math"}


def canonical_provider_name(provider: str | None) -> str | None:
    normalized = str(provider or "").strip()
    if not normalized:
        return None
    lowered = normalized.lower()
    if lowered in {"mathpix", "mathpix_layout"} or lowered.startswith("mathpix"):
        return "mathpix"
    if lowered == "docling" or lowered.startswith("docling"):
        return "docling"
    if lowered == "grobid" or lowered.startswith("grobid"):
        return "grobid"
    if lowered == "native_pdf":
        return "native_pdf"
    return normalized


def normalize_scorecard_recommendations(source_scorecard: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(source_scorecard or {})
    for key in (
        "recommended_primary_layout_provider",
        "recommended_primary_math_provider",
        "recommended_primary_metadata_provider",
        "recommended_primary_reference_provider",
    ):
        payload[key] = canonical_provider_name(payload.get(key))
    return payload


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


def select_math_payload(
    *,
    source_scorecard: dict[str, Any] | None,
    docling_math: dict[str, Any] | None,
    mathpix_math: dict[str, Any] | None,
) -> dict[str, Any]:
    preferred_provider = canonical_provider_name((source_scorecard or {}).get("recommended_primary_math_provider"))
    docling_entries = list((docling_math or {}).get("entries", []))
    mathpix_entries = list((mathpix_math or {}).get("entries", []))
    if preferred_provider == "mathpix" and mathpix_entries:
        return dict(mathpix_math or {})
    if preferred_provider == "docling" and docling_entries:
        return dict(docling_math or {})
    if mathpix_entries:
        return dict(mathpix_math or {})
    if docling_entries:
        return dict(docling_math or {})
    return {"engine": "none", "entries": []}


def select_metadata_observation(
    *,
    source_scorecard: dict[str, Any] | None,
    metadata_candidates: dict[str, dict[str, Any] | None] | None,
) -> dict[str, Any]:
    candidates = {
        canonical_provider_name(provider) or str(provider): dict(payload or {})
        for provider, payload in (metadata_candidates or {}).items()
        if payload
    }
    preferred_provider = canonical_provider_name((source_scorecard or {}).get("recommended_primary_metadata_provider"))
    if preferred_provider:
        preferred_payload = candidates.get(preferred_provider)
        if preferred_payload:
            return preferred_payload
    for provider in sorted(candidates):
        payload = candidates[provider]
        if (
            str(payload.get("title", "")).strip()
            or str(payload.get("abstract", "")).strip()
            or any(str(item).strip() for item in payload.get("references", []))
        ):
            return payload
    return {}


__all__ = [
    "canonical_provider_name",
    "normalize_scorecard_recommendations",
    "reported_layout_provider",
    "reported_math_provider",
    "select_metadata_observation",
    "select_math_payload",
]
