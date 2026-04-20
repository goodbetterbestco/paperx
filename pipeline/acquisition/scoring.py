from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from pipeline.policies.abstract_quality import abstract_quality_flags
from pipeline.acquisition.source_ownership import normalize_scorecard_recommendations


ABSTRACT_PAGE_MARKER_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)
INTRO_PAGE_MARKER_RE = re.compile(r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s*introduction\b", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b)\b",
    re.IGNORECASE,
)

LAYOUT_ACCEPTANCE_THRESHOLD_BY_ROUTE = {
    "born_digital_scholarly": 0.3,
    "layout_complex": 0.3,
    "math_dense": 0.28,
    "scan_or_image_heavy": 0.18,
    "degraded_or_garbled": 0.18,
}
MATH_ACCEPTANCE_THRESHOLD_BY_ROUTE = {
    "born_digital_scholarly": 0.05,
    "layout_complex": 0.05,
    "math_dense": 0.08,
    "scan_or_image_heavy": 0.05,
    "degraded_or_garbled": 0.05,
}
METADATA_ACCEPTANCE_THRESHOLD_BY_ROUTE = {
    "born_digital_scholarly": 0.45,
    "layout_complex": 0.45,
    "math_dense": 0.45,
    "scan_or_image_heavy": 0.35,
    "degraded_or_garbled": 0.35,
}


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


def acceptance_threshold(kind: str, *, route_bias: str | None = None) -> float:
    normalized_kind = str(kind or "").strip()
    route = str(route_bias or "").strip()
    if normalized_kind == "layout":
        return LAYOUT_ACCEPTANCE_THRESHOLD_BY_ROUTE.get(route, 0.22)
    if normalized_kind == "math":
        return MATH_ACCEPTANCE_THRESHOLD_BY_ROUTE.get(route, 0.05)
    if normalized_kind == "metadata":
        return METADATA_ACCEPTANCE_THRESHOLD_BY_ROUTE.get(route, 0.4)
    return 0.0


def annotate_provider_acceptance(
    provider_score: dict[str, Any],
    *,
    route_bias: str | None = None,
) -> dict[str, Any]:
    payload = dict(provider_score)
    kind = str(payload.get("kind", "") or "")
    threshold = acceptance_threshold(kind, route_bias=route_bias)
    rejection_reasons: list[str] = []
    overall_score = float(payload.get("overall_score", 0.0) or 0.0)

    if kind == "layout":
        if int(payload.get("block_count", 0) or 0) <= 0:
            rejection_reasons.append("no_blocks")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")
    elif kind == "math":
        if int(payload.get("math_entry_count", 0) or 0) <= 0:
            rejection_reasons.append("no_math_entries")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")
    elif kind == "metadata":
        has_structured_fields = (
            bool(payload.get("title_present"))
            or bool(payload.get("abstract_present"))
            or int(payload.get("reference_count", 0) or 0) > 0
        )
        if not has_structured_fields:
            rejection_reasons.append("no_structured_fields")
        elif overall_score < threshold:
            rejection_reasons.append("score_below_threshold")

    payload["acceptance_threshold"] = threshold
    payload["accepted"] = not rejection_reasons
    payload["rejection_reasons"] = rejection_reasons
    return payload


def _recommended_provider(
    providers: list[dict[str, Any]],
    *,
    matches: Any,
) -> tuple[str | None, str | None]:
    accepted = next((item for item in providers if matches(item) and bool(item.get("accepted"))), None)
    if accepted is not None:
        return str(accepted.get("provider") or ""), "accepted"
    fallback = next((item for item in providers if matches(item)), None)
    if fallback is not None:
        return str(fallback.get("provider") or ""), "fallback_unaccepted"
    return None, None


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


def score_metadata_provider(
    provider: str,
    observation: dict[str, Any] | None,
    *,
    route_bias: str | None = None,
) -> dict[str, Any]:
    payload = dict(observation or {})
    title = str(payload.get("title", "") or "").strip()
    abstract = str(payload.get("abstract", "") or "").strip()
    references = [str(item).strip() for item in payload.get("references", []) if str(item).strip()]
    clean_abstract = bool(abstract) and not abstract_quality_flags(abstract)
    route_bonus = 0.0
    if provider == "grobid" and route_bias in {
        "born_digital_scholarly",
        "layout_complex",
        "math_dense",
        "degraded_or_garbled",
    }:
        route_bonus = 0.15
    overall_score = round(
        (0.35 if title else 0.0)
        + (0.35 if clean_abstract else 0.15 if abstract else 0.0)
        + min(len(references), 40) * 0.02
        + route_bonus,
        3,
    )
    return {
        "provider": provider,
        "kind": "metadata",
        "block_count": 0,
        "math_entry_count": 0,
        "page_count": 0,
        "heading_count": 0,
        "front_matter_count": 0,
        "paragraph_count": 0,
        "reference_count": len(references),
        "caption_count": 0,
        "avg_text_chars_per_block": 0.0,
        "page_one_marker_score": 0,
        "title_present": bool(title),
        "abstract_present": bool(abstract),
        "abstract_clean": clean_abstract,
        "overall_score": overall_score,
    }


def build_source_scorecard(
    *,
    native_layout: dict[str, Any] | None,
    external_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
    external_math: dict[str, Any] | None,
    layout_candidates: dict[str, dict[str, Any] | None] | None = None,
    math_candidates: dict[str, dict[str, Any] | None] | None = None,
    route_bias: str | None = None,
    metadata_observations: dict[str, dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    external_math_entries = len((external_math or {}).get("entries", []))
    providers = []
    if layout_candidates is not None:
        for provider, payload in layout_candidates.items():
            if payload:
                math_entry_count = len(list((math_candidates or {}).get(provider, {}).get("entries", [])))
                providers.append(
                    score_layout_provider(
                        provider,
                        payload,
                        kind="layout",
                        math_entry_count=math_entry_count,
                    )
                )
    else:
        providers.append(
            score_layout_provider("native_pdf", native_layout, kind="layout"),
        )
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
    if math_candidates is not None:
        for provider, payload in math_candidates.items():
            if payload:
                providers.append(score_math_provider(provider, payload, route_bias=route_bias))
    elif external_math:
        providers.append(
            score_math_provider(
                str(external_math.get("engine", "external_math")),
                external_math,
                route_bias=route_bias,
            )
        )
    for provider, observation in sorted((metadata_observations or {}).items()):
        if observation:
            providers.append(score_metadata_provider(provider, observation, route_bias=route_bias))

    providers = [annotate_provider_acceptance(item, route_bias=route_bias) for item in providers]
    providers.sort(
        key=lambda item: (
            -int(bool(item.get("accepted"))),
            -float(item["overall_score"]),
            str(item["provider"]),
            str(item["kind"]),
        )
    )
    recommended_layout_provider, layout_basis = _recommended_provider(
        providers,
        matches=lambda item: str(item.get("kind")) == "layout",
    )
    recommended_math_provider, math_basis = _recommended_provider(
        providers,
        matches=lambda item: str(item.get("kind")) == "math" and int(item.get("math_entry_count", 0) or 0) > 0,
    )
    recommended_metadata_provider, metadata_basis = _recommended_provider(
        providers,
        matches=lambda item: str(item.get("kind")) == "metadata"
        and (
            bool(item.get("title_present"))
            or bool(item.get("abstract_present"))
            or int(item.get("reference_count", 0) or 0) > 0
        ),
    )
    recommended_reference_provider, reference_basis = _recommended_provider(
        providers,
        matches=lambda item: (
            (str(item.get("kind")) == "metadata" and int(item.get("reference_count", 0) or 0) > 0)
            or (str(item.get("kind")) == "layout" and int(item.get("reference_count", 0) or 0) > 0)
        ),
    )
    scorecard = {
        "providers": providers,
        "recommended_primary_layout_provider": recommended_layout_provider,
        "recommended_primary_math_provider": recommended_math_provider,
        "recommended_primary_metadata_provider": recommended_metadata_provider,
        "recommended_primary_reference_provider": recommended_reference_provider,
        "layout_recommendation_basis": layout_basis,
        "math_recommendation_basis": math_basis,
        "metadata_recommendation_basis": metadata_basis,
        "reference_recommendation_basis": reference_basis,
    }
    return normalize_scorecard_recommendations(scorecard)


__all__ = [
    "acceptance_threshold",
    "annotate_provider_acceptance",
    "build_source_scorecard",
    "score_metadata_provider",
    "score_math_provider",
    "score_layout_provider",
]
