from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any


ABSTRACT_PAGE_MARKER_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)
INTRO_PAGE_MARKER_RE = re.compile(r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s*introduction\b", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProviderScore:
    provider: str
    kind: str
    block_count: int
    math_entry_count: int
    page_count: int
    heading_count: int
    front_matter_count: int
    paragraph_count: int
    reference_count: int
    caption_count: int
    avg_text_chars_per_block: float
    page_one_marker_score: int
    overall_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _block_attr(block: Any, name: str, default: Any = None) -> Any:
    if hasattr(block, name):
        return getattr(block, name)
    if isinstance(block, dict):
        return block.get(name, default)
    return default


def _layout_blocks(layout: dict[str, Any] | None) -> list[Any]:
    if not layout:
        return []
    return list(layout.get("blocks", []))


def _page_count(layout: dict[str, Any] | None) -> int:
    if not layout:
        return 0
    count = int(layout.get("page_count", 0) or 0)
    if count > 0:
        return count
    pages = {
        int(_block_attr(block, "page", 0) or 0)
        for block in _layout_blocks(layout)
        if int(_block_attr(block, "page", 0) or 0) > 0
    }
    return len(pages)


def _dict_layout_for_page_score(layout: dict[str, Any] | None) -> dict[str, Any]:
    blocks = []
    for block in _layout_blocks(layout):
        blocks.append(
            {
                "page": int(_block_attr(block, "page", 0) or 0),
                "order": int(_block_attr(block, "order", 0) or 0),
                "text": str(_block_attr(block, "text", "") or ""),
                "id": str(_block_attr(block, "id", "") or ""),
            }
        )
    return {"blocks": blocks}


def _page_one_layout_score(blocks: list[dict[str, Any]]) -> int:
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


def score_layout_provider(
    provider: str,
    layout: dict[str, Any] | None,
    *,
    kind: str,
    math_entry_count: int = 0,
) -> dict[str, Any]:
    blocks = _layout_blocks(layout)
    headings = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "heading")
    front_matter = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "front_matter")
    paragraphs = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "paragraph")
    references = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "reference")
    captions = sum(1 for block in blocks if str(_block_attr(block, "role", "")) == "caption")
    text_lengths = [len(str(_block_attr(block, "text", "") or "").strip()) for block in blocks if str(_block_attr(block, "text", "") or "").strip()]
    avg_text_chars_per_block = round(sum(text_lengths) / max(len(text_lengths), 1), 2) if text_lengths else 0.0
    marker_score = _page_one_layout_score(
        [block for block in _dict_layout_for_page_score(layout).get("blocks", []) if int(block.get("page", 0) or 0) == 1]
    )
    overall_score = round(
        (
            min(len(blocks), 80) * 0.01
            + min(headings, 12) * 0.08
            + min(front_matter, 8) * 0.08
            + min(paragraphs, 80) * 0.015
            + min(references, 40) * 0.02
            + min(captions, 20) * 0.015
            + max(marker_score, -10) * 0.05
            + min(math_entry_count, 40) * 0.02
        ),
        3,
    )
    return ProviderScore(
        provider=provider,
        kind=kind,
        block_count=len(blocks),
        math_entry_count=math_entry_count,
        page_count=_page_count(layout),
        heading_count=headings,
        front_matter_count=front_matter,
        paragraph_count=paragraphs,
        reference_count=references,
        caption_count=captions,
        avg_text_chars_per_block=avg_text_chars_per_block,
        page_one_marker_score=marker_score,
        overall_score=overall_score,
    ).to_dict()


def score_math_provider(
    provider: str,
    math_payload: dict[str, Any] | None,
    *,
    route_bias: str | None = None,
) -> dict[str, Any]:
    entries = list((math_payload or {}).get("entries", []))
    entry_count = len(entries)
    display_like_count = sum(1 for entry in entries if str(entry.get("kind", "display")) in {"display", "group"})
    route_bonus = 0.0
    if route_bias in {"math_dense", "scan_or_image_heavy", "degraded_or_garbled"} and provider == "mathpix":
        route_bonus = 0.1
    elif route_bias == "born_digital_scholarly" and provider == "docling":
        route_bonus = 0.05
    overall_score = round(min(entry_count, 40) * 0.05 + min(display_like_count, 40) * 0.02 + route_bonus, 3)
    return {
        "provider": provider,
        "kind": "math",
        "block_count": 0,
        "math_entry_count": entry_count,
        "page_count": 0,
        "heading_count": 0,
        "front_matter_count": 0,
        "paragraph_count": 0,
        "reference_count": 0,
        "caption_count": 0,
        "avg_text_chars_per_block": 0.0,
        "page_one_marker_score": 0,
        "overall_score": overall_score,
    }


def build_source_scorecard(
    *,
    native_layout: dict[str, Any] | None,
    external_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
    external_math: dict[str, Any] | None,
) -> dict[str, Any]:
    external_math_entries = len((external_math or {}).get("entries", []))
    providers = [
        score_layout_provider("native_pdf", native_layout, kind="layout"),
    ]
    if external_layout:
        providers.append(
            score_layout_provider(
                str(external_layout.get("engine", "external_layout")),
                external_layout,
                kind="layout",
                math_entry_count=external_math_entries,
            )
        )
    if mathpix_layout:
        providers.append(
            score_layout_provider("mathpix_layout", mathpix_layout, kind="layout")
        )
    if external_math:
        providers.append(
            score_math_provider(
                str(external_math.get("engine", "external_math")),
                external_math,
            )
        )

    providers.sort(key=lambda item: (-float(item["overall_score"]), str(item["provider"]), str(item["kind"])))
    return {
        "providers": providers,
        "recommended_primary_layout_provider": next(
            (item["provider"] for item in providers if str(item.get("kind")) == "layout"),
            None,
        ),
        "recommended_primary_math_provider": next(
            (
                item["provider"]
                for item in providers
                if str(item.get("kind")) == "math" and int(item.get("math_entry_count", 0) or 0) > 0
            ),
            None,
        ),
    }


__all__ = [
    "build_source_scorecard",
    "score_math_provider",
    "score_layout_provider",
]
