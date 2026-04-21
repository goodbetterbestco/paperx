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


def provider_score_rows(
    source_scorecard: dict[str, Any] | None,
    *,
    kind: str,
) -> list[dict[str, Any]]:
    normalized_kind = str(kind or "").strip()
    rows = []
    for item in list((source_scorecard or {}).get("providers") or []):
        if str(item.get("kind", "") or "").strip() != normalized_kind:
            continue
        payload = dict(item)
        payload["provider"] = canonical_provider_name(payload.get("provider")) or str(payload.get("provider", "") or "")
        rows.append(payload)
    rows.sort(
        key=lambda item: (
            -int(bool(item.get("accepted"))),
            -float(item.get("overall_score", 0.0) or 0.0),
            str(item.get("provider", "")),
        )
    )
    return rows


def provider_score_row(
    source_scorecard: dict[str, Any] | None,
    *,
    kind: str,
    provider: str | None,
) -> dict[str, Any] | None:
    normalized_provider = canonical_provider_name(provider)
    if not normalized_provider:
        return None
    for item in provider_score_rows(source_scorecard, kind=kind):
        if canonical_provider_name(item.get("provider")) == normalized_provider:
            return item
    return None


def _fallback_unaccepted(source_scorecard: dict[str, Any] | None, key: str) -> bool:
    return str((source_scorecard or {}).get(key, "") or "").strip() == "fallback_unaccepted"


def _has_metadata_fields(payload: dict[str, Any] | None) -> bool:
    candidate = dict(payload or {})
    return bool(str(candidate.get("title", "")).strip() or str(candidate.get("abstract", "")).strip())


def _has_reference_fields(payload: dict[str, Any] | None) -> bool:
    candidate = dict(payload or {})
    return any(str(item).strip() for item in list(candidate.get("references", [])))


def reported_layout_provider(
    layout_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
    fallback: str = "native_pdf",
) -> str:
    reported = canonical_provider_name(layout_engine)
    return reported or fallback


def reported_math_provider(
    math_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
    math_payload: dict[str, Any] | None,
    fallback: str = "heuristic",
) -> str:
    math_entries = list((math_payload or {}).get("entries", []))
    reported = canonical_provider_name(math_engine)
    if reported and math_entries and reported not in GENERIC_MATH_PROVIDER_NAMES:
        return reported
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


def select_follow_up_provider(
    *,
    source_scorecard: dict[str, Any] | None,
    kind: str,
    selected_provider: str | None,
) -> str | None:
    normalized_kind = str(kind or "").strip()
    normalized_selected = canonical_provider_name(selected_provider)
    candidates: list[tuple[int, float, str]] = []
    for item in list((source_scorecard or {}).get("providers") or []):
        if str(item.get("kind", "") or "").strip() != normalized_kind:
            continue
        provider = canonical_provider_name(item.get("provider"))
        if not provider or provider == normalized_selected:
            continue
        if normalized_kind == "layout" and int(item.get("block_count", 0) or 0) <= 0:
            continue
        if normalized_kind == "math" and int(item.get("math_entry_count", 0) or 0) <= 0:
            continue
        accepted_rank = 1 if bool(item.get("accepted")) else 0
        overall_score = float(item.get("overall_score", 0.0) or 0.0)
        candidates.append((accepted_rank, overall_score, provider))
    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return candidates[0][2] if candidates else None


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
    grobid_payload = candidates.get("grobid")
    if _fallback_unaccepted(source_scorecard, "metadata_recommendation_basis") and _has_metadata_fields(grobid_payload):
        return dict(grobid_payload or {})
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


def select_reference_observation(
    *,
    source_scorecard: dict[str, Any] | None,
    metadata_candidates: dict[str, dict[str, Any] | None] | None,
) -> dict[str, Any]:
    candidates = {
        canonical_provider_name(provider) or str(provider): dict(payload or {})
        for provider, payload in (metadata_candidates or {}).items()
        if payload
    }
    grobid_payload = candidates.get("grobid")
    if _fallback_unaccepted(source_scorecard, "reference_recommendation_basis") and _has_reference_fields(grobid_payload):
        return dict(grobid_payload or {})
    preferred_provider = canonical_provider_name((source_scorecard or {}).get("recommended_primary_reference_provider"))
    if preferred_provider:
        preferred_payload = candidates.get(preferred_provider)
        preferred_references = [str(item).strip() for item in list((preferred_payload or {}).get("references", [])) if str(item).strip()]
        if preferred_payload and preferred_references:
            return preferred_payload
    for provider in sorted(candidates):
        payload = candidates[provider]
        if any(str(item).strip() for item in payload.get("references", [])):
            return payload
    return {}


__all__ = [
    "canonical_provider_name",
    "normalize_scorecard_recommendations",
    "provider_score_row",
    "provider_score_rows",
    "reported_layout_provider",
    "reported_math_provider",
    "select_follow_up_provider",
    "select_metadata_observation",
    "select_reference_observation",
    "select_math_payload",
]
