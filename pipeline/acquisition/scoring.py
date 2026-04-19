from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pipeline.orchestrator.source_composition import page_one_layout_score


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
    marker_score = page_one_layout_score(
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
            {
                "provider": str(external_math.get("engine", "external_math")),
                "kind": "math",
                "block_count": 0,
                "math_entry_count": external_math_entries,
                "page_count": 0,
                "heading_count": 0,
                "front_matter_count": 0,
                "paragraph_count": 0,
                "reference_count": 0,
                "caption_count": 0,
                "avg_text_chars_per_block": 0.0,
                "page_one_marker_score": 0,
                "overall_score": round(min(external_math_entries, 40) * 0.05, 3),
            }
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
                if str(item.get("math_entry_count", 0)) != "0" and int(item.get("math_entry_count", 0) or 0) > 0
            ),
            None,
        ),
    }


__all__ = [
    "build_source_scorecard",
    "score_layout_provider",
]
