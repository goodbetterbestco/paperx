from __future__ import annotations

import re
from typing import Any


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


def compose_layout_sources(
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
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
    blocks: list[dict[str, Any]] = []
    page_sources: dict[str, str] = {}
    for page in sorted(set(docling_pages) | set(mathpix_pages)):
        docling_blocks = docling_pages.get(page, [])
        mathpix_blocks = mathpix_pages.get(page, [])
        chosen_blocks = docling_blocks
        chosen_engine = str(docling_layout.get("engine", "docling"))
        if page == 1 and mathpix_blocks:
            if page_one_layout_score(mathpix_blocks) > page_one_layout_score(docling_blocks):
                chosen_blocks = mathpix_blocks
                chosen_engine = str(mathpix_layout.get("engine", "mathpix"))
        elif not chosen_blocks and mathpix_blocks:
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
]
