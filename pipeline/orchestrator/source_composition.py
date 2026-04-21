from __future__ import annotations

from typing import Any

from pipeline.acquisition.source_ownership import canonical_provider_name, provider_score_row


def layout_blocks_by_page(layout: dict[str, Any] | None) -> dict[int, list[dict[str, Any]]]:
    by_page: dict[int, list[dict[str, Any]]] = {}
    if not layout:
        return by_page
    for block in layout.get("blocks", []):
        page = int(block.get("page", 0) or 0)
        if page <= 0:
            continue
        by_page.setdefault(page, []).append(block)
    for blocks in by_page.values():
        blocks.sort(key=lambda block: (int(block.get("order", 0) or 0), str(block.get("id", ""))))
    return by_page


def select_owned_layout_provider(
    docling_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
    *,
    acquisition_route: dict[str, Any] | None = None,
    source_scorecard: dict[str, Any] | None = None,
) -> str | None:
    if docling_layout and not mathpix_layout:
        return "docling"
    if mathpix_layout and not docling_layout:
        return "mathpix"
    if not docling_layout and not mathpix_layout:
        return None

    recommended_provider = canonical_provider_name((source_scorecard or {}).get("recommended_primary_layout_provider"))
    if recommended_provider in {"docling", "mathpix"}:
        recommended_row = provider_score_row(
            source_scorecard,
            kind="layout",
            provider=recommended_provider,
        )
        if bool((recommended_row or {}).get("accepted")):
            return recommended_provider

    ranked_candidates: list[tuple[float, str]] = []
    for provider in ("docling", "mathpix"):
        payload = docling_layout if provider == "docling" else mathpix_layout
        if not payload:
            continue
        provider_row = provider_score_row(source_scorecard, kind="layout", provider=provider)
        if not bool((provider_row or {}).get("accepted")):
            continue
        ranked_candidates.append((float((provider_row or {}).get("overall_score", 0.0) or 0.0), provider))
    if ranked_candidates:
        ranked_candidates.sort(key=lambda item: (-item[0], item[1]))
        return ranked_candidates[0][1]

    primary_route = str((acquisition_route or {}).get("primary_route", "") or "")
    if primary_route in {"scan_or_image_heavy", "degraded_or_garbled"}:
        return "mathpix"
    if primary_route in {"born_digital_scholarly", "layout_complex", "math_dense"}:
        return "docling"
    return "docling"


def compose_layout_sources(
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    *,
    acquisition_route: dict[str, Any] | None = None,
    source_scorecard: dict[str, Any] | None = None,
) -> dict[str, Any]:
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    if not docling_layout and not mathpix_layout:
        return {"engine": "none", "blocks": []}
    if not docling_layout:
        return dict(mathpix_layout)
    if not mathpix_layout:
        return dict(docling_layout)

    preferred_provider = select_owned_layout_provider(
        docling_layout,
        mathpix_layout,
        acquisition_route=acquisition_route,
        source_scorecard=source_scorecard,
    )
    if preferred_provider == "mathpix":
        return dict(mathpix_layout)
    return dict(docling_layout)


__all__ = [
    "compose_layout_sources",
    "layout_blocks_by_page",
    "select_owned_layout_provider",
]
