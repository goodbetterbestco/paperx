from __future__ import annotations

import re
from typing import Any

from pipeline.acquisition.scoring import score_layout_provider
from pipeline.acquisition.source_ownership import canonical_provider_name


ABSTRACT_PAGE_MARKER_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)
INTRO_PAGE_MARKER_RE = re.compile(r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s*introduction\b", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b)\b",
    re.IGNORECASE,
)


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


def page_one_layout_score(blocks: list[dict[str, Any]]) -> int:
    if not blocks:
        return -10
    texts = [str(block.get("text", "")).strip() for block in blocks if str(block.get("text", "")).strip()]
    marker_score = 0
    if any(ABSTRACT_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 8
    if any(INTRO_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 4
    marker_score -= sum(3 for text in texts if LAYOUT_METADATA_RE.search(text))
    return marker_score


def preferred_layout_provider(
    docling_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
    *,
    acquisition_route: dict[str, Any] | None = None,
    source_scorecard: dict[str, Any] | None = None,
) -> str:
    if docling_layout and not mathpix_layout:
        return "docling"
    if mathpix_layout and not docling_layout:
        return "mathpix"

    provider_scores: dict[str, float] = {}
    for item in list((source_scorecard or {}).get("providers", [])):
        provider = str(item.get("provider", "") or "")
        if not provider:
            continue
        provider_scores[provider] = float(item.get("overall_score", 0.0) or 0.0)

    docling_engine = str((docling_layout or {}).get("engine", "docling") or "docling")
    mathpix_engine = str((mathpix_layout or {}).get("engine", "mathpix") or "mathpix")
    docling_score = provider_scores.get(docling_engine)
    mathpix_score = provider_scores.get(mathpix_engine)
    recommended_provider = canonical_provider_name((source_scorecard or {}).get("recommended_primary_layout_provider"))
    if docling_score is None:
        docling_score = float(score_layout_provider(docling_engine, docling_layout, kind="layout")["overall_score"])
    if mathpix_score is None:
        mathpix_score = float(score_layout_provider(mathpix_engine, mathpix_layout, kind="layout")["overall_score"])

    if abs(docling_score - mathpix_score) >= 0.15:
        return "docling" if docling_score > mathpix_score else "mathpix"
    if recommended_provider in {"docling", "mathpix"}:
        return recommended_provider

    primary_route = str((acquisition_route or {}).get("primary_route", "") or "")
    if primary_route in {"scan_or_image_heavy", "degraded_or_garbled"}:
        return "mathpix"
    if primary_route in {"born_digital_scholarly", "layout_complex", "math_dense"}:
        return "docling"
    return "docling" if docling_score >= mathpix_score else "mathpix"


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

    docling_pages = layout_blocks_by_page(docling_layout)
    mathpix_pages = layout_blocks_by_page(mathpix_layout)
    preferred_provider = preferred_layout_provider(
        docling_layout,
        mathpix_layout,
        acquisition_route=acquisition_route,
        source_scorecard=source_scorecard,
    )
    blocks: list[dict[str, Any]] = []
    page_sources: dict[str, str] = {}
    for page in sorted(set(docling_pages) | set(mathpix_pages)):
        docling_blocks = docling_pages.get(page, [])
        mathpix_blocks = mathpix_pages.get(page, [])
        if preferred_provider == "mathpix":
            chosen_blocks = mathpix_blocks or docling_blocks
            chosen_engine = str((mathpix_layout if mathpix_blocks else docling_layout).get("engine", "mathpix"))
        else:
            chosen_blocks = docling_blocks or mathpix_blocks
            chosen_engine = str((docling_layout if docling_blocks else mathpix_layout).get("engine", "docling"))
        if preferred_provider == "docling" and page == 1 and mathpix_blocks:
            if page_one_layout_score(mathpix_blocks) > page_one_layout_score(docling_blocks):
                chosen_blocks = mathpix_blocks
                chosen_engine = str(mathpix_layout.get("engine", "mathpix"))
        blocks.extend(chosen_blocks)
        page_sources[str(page)] = chosen_engine

    return {
        "engine": "composed",
        "pdf_path": docling_layout.get("pdf_path") or mathpix_layout.get("pdf_path"),
        "page_count": docling_layout.get("page_count") or mathpix_layout.get("page_count"),
        "page_sizes_pt": docling_layout.get("page_sizes_pt") or mathpix_layout.get("page_sizes_pt"),
        "blocks": blocks,
        "page_sources": page_sources,
    }


__all__ = [
    "compose_layout_sources",
    "layout_blocks_by_page",
    "page_one_layout_score",
    "preferred_layout_provider",
]
