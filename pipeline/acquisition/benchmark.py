from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from pipeline.acquisition.benchmark_reports import capability_leader_rows, family_leader_rows, provider_leader_summary
from pipeline.acquisition.providers import (
    derive_metadata_reference_observation_from_layout,
    load_metadata_reference_observation,
)


SPACE_RE = re.compile(r"\s+")
NON_WORD_RE = re.compile(r"[^a-z0-9]+")
CAPABILITY_ORDER = ("layout", "math", "metadata_reference")
CAPABILITY_METRIC_NAMES: dict[str, tuple[str, ...]] = {
    "layout": (
        "title_match",
        "heading_hit_rate",
        "paragraph_hit_rate",
        "recommended_layout_provider_match",
        "selected_layout_provider_match",
    ),
    "math": (
        "equation_hit_rate",
        "recommended_math_provider_match",
        "selected_math_provider_match",
    ),
    "metadata_reference": (
        "title_match",
        "abstract_token_recall",
        "reference_hit_rate",
        "recommended_metadata_provider_match",
        "selected_metadata_provider_match",
        "recommended_reference_provider_match",
        "selected_reference_provider_match",
    ),
}


@dataclass(frozen=True)
class AcquisitionGoldRecord:
    paper_id: str
    title: str
    abstract: str
    headings: list[str]
    paragraphs: list[str]
    equations: list[str]
    references: list[str]
    family: str | None
    expected_route: str | None
    expected_route_reason_codes: list[str]
    ocr_should_run: bool | None
    expected_ocr_policy: str | None
    expected_primary_layout_provider: str | None
    expected_primary_math_provider: str | None
    expected_primary_metadata_provider: str | None
    expected_primary_reference_provider: str | None
    acceptable_selected_layout_providers: list[str]
    acceptable_selected_math_providers: list[str]
    acceptable_selected_metadata_providers: list[str]
    acceptable_selected_reference_providers: list[str]


@dataclass(frozen=True)
class ProviderArtifacts:
    name: str
    layout_path: Path | None
    metadata_path: Path | None
    math_path: Path | None
    execution_path: Path | None


@dataclass(frozen=True)
class BenchmarkPaper:
    paper_id: str
    gold_path: Path
    family: str | None
    section: str | None
    providers: list[ProviderArtifacts]


def _normalize_text(text: str) -> str:
    squashed = SPACE_RE.sub(" ", text.lower()).strip()
    return NON_WORD_RE.sub(" ", squashed).strip()


def _normalize_tokens(text: str) -> set[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return set()
    return {token for token in normalized.split(" ") if token}


def _contains_normalized(haystack: str, needle: str) -> bool:
    normalized_haystack = _normalize_text(haystack)
    normalized_needle = _normalize_text(needle)
    return bool(normalized_needle and normalized_needle in normalized_haystack)


def _token_recall(expected: str, observed: str) -> float:
    expected_tokens = _normalize_tokens(expected)
    if not expected_tokens:
        return 1.0
    observed_tokens = _normalize_tokens(observed)
    return round(len(expected_tokens & observed_tokens) / len(expected_tokens), 3)


def _guess_title(blocks: list[dict[str, Any]]) -> str:
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if role == "front_matter" and text:
            return text
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if role == "heading" and text:
            return text
    return ""


def _guess_abstract(blocks: list[dict[str, Any]]) -> str:
    seen_abstract_marker = False
    for block in blocks:
        role = str(block.get("role", ""))
        text = str(block.get("text", "")).strip()
        if not text:
            continue
        normalized = _normalize_text(text)
        if normalized == "abstract":
            seen_abstract_marker = True
            continue
        if seen_abstract_marker and role in {"front_matter", "paragraph"}:
            return text
        if role == "front_matter" and normalized.startswith("abstract "):
            return text.split(" ", 1)[1].strip()
    return ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_provider_observation(
    provider_name: str,
    *,
    layout_path: Path | None,
    metadata_path: Path | None,
    math_path: Path | None,
) -> dict[str, Any]:
    layout_payload = _load_json(layout_path) if layout_path is not None and layout_path.exists() else {}
    math_payload = _load_json(math_path) if math_path is not None and math_path.exists() else {}
    blocks = list(layout_payload.get("blocks", []))
    if metadata_path is not None and metadata_path.exists():
        metadata_observation = load_metadata_reference_observation(provider_name, metadata_path).to_dict()
    else:
        inferred_provider_name = str(
            layout_payload.get("engine", provider_name) or provider_name
        ).strip()
        metadata_observation = derive_metadata_reference_observation_from_layout(
            inferred_provider_name,
            layout_payload,
        ).to_dict()
    headings = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "heading"]
    paragraphs = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "paragraph"]
    layout_references = [str(block.get("text", "")).strip() for block in blocks if str(block.get("role", "")) == "reference"]
    references = list(metadata_observation.get("references", [])) or layout_references
    title = str(metadata_observation.get("title", "")).strip() or _guess_title(blocks)
    abstract = str(metadata_observation.get("abstract", "")).strip() or _guess_abstract(blocks)
    full_text = "\n".join(text for text in [title, abstract, *headings, *paragraphs, *references] if text)
    equations = [
        str(entry.get("display_latex", "") or entry.get("text", "")).strip()
        for entry in math_payload.get("entries", [])
        if str(entry.get("display_latex", "") or entry.get("text", "")).strip()
    ]
    return {
        "title": title,
        "abstract": abstract,
        "headings": headings,
        "paragraphs": paragraphs,
        "references": references,
        "equations": equations,
        "full_text": full_text,
        "metadata_observation": metadata_observation,
    }


def _extract_execution_observation(execution_path: Path | None) -> dict[str, Any]:
    if execution_path is None or not execution_path.exists():
        return {}
    payload = _load_json(execution_path)
    recommended = dict(payload.get("recommended") or {})
    executed = dict(payload.get("executed") or {})
    ocr = dict(payload.get("ocr") or {})
    follow_up = dict(payload.get("follow_up") or {})
    route_reason_codes = [
        str(item).strip()
        for item in list(payload.get("route_reason_codes") or payload.get("route_traits") or [])
        if str(item).strip()
    ]
    return {
        "route_primary": str(payload.get("route_primary", "") or "").strip() or None,
        "route_reason_codes": route_reason_codes,
        "recommended_layout_provider": str(recommended.get("layout_provider", "") or "").strip() or None,
        "recommended_math_provider": str(recommended.get("math_provider", "") or "").strip() or None,
        "recommended_metadata_provider": str(recommended.get("metadata_provider", "") or "").strip() or None,
        "recommended_reference_provider": str(recommended.get("reference_provider", "") or "").strip() or None,
        "selected_layout_provider": str(executed.get("selected_layout_provider", "") or "").strip() or None,
        "selected_math_provider": str(executed.get("selected_math_provider", "") or "").strip() or None,
        "selected_metadata_provider": str(executed.get("metadata_provider", "") or "").strip() or None,
        "selected_reference_provider": str(executed.get("reference_provider", "") or "").strip() or None,
        "ocr_policy": str(ocr.get("policy", "") or "").strip() or None,
        "ocr_applied": bool(ocr.get("applied")) if "applied" in ocr else None,
        "follow_up_needed": bool(follow_up.get("needs_attention")) if "needs_attention" in follow_up else None,
    }


def _list_hit_rate(expected_items: list[str], observed_items: list[str], fallback_text: str) -> float:
    if not expected_items:
        return 1.0
    hits = 0
    for item in expected_items:
        if any(_contains_normalized(candidate, item) for candidate in observed_items):
            hits += 1
            continue
        if _contains_normalized(fallback_text, item):
            hits += 1
    return round(hits / len(expected_items), 3)


def _content_score(metrics: dict[str, float]) -> float:
    weighted_total = (
        metrics["title_match"] * 0.2
        + metrics["abstract_token_recall"] * 0.2
        + metrics["heading_hit_rate"] * 0.2
        + metrics["paragraph_hit_rate"] * 0.15
        + metrics["equation_hit_rate"] * 0.15
        + metrics["reference_hit_rate"] * 0.1
    )
    return round(weighted_total, 3)


def _selected_provider_match(
    selected_provider: str | None,
    *,
    expected_provider: str | None,
    acceptable_providers: list[str],
) -> float | None:
    allowed = [provider for provider in acceptable_providers if provider]
    if not allowed and expected_provider:
        allowed = [expected_provider]
    if not allowed:
        return None
    return float((selected_provider or "") in allowed)


def _execution_metrics(
    gold: AcquisitionGoldRecord,
    execution: dict[str, Any],
    *,
    provider: ProviderArtifacts,
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    if gold.expected_route:
        metrics["route_match"] = float(execution.get("route_primary") == gold.expected_route)
    if gold.expected_route_reason_codes:
        observed_codes = {str(item).strip() for item in list(execution.get("route_reason_codes") or []) if str(item).strip()}
        expected_codes = {str(item).strip() for item in gold.expected_route_reason_codes if str(item).strip()}
        metrics["route_reason_code_recall"] = round(
            len(observed_codes & expected_codes) / max(len(expected_codes), 1),
            3,
        )
    if gold.ocr_should_run is not None:
        metrics["ocr_should_run_match"] = float(execution.get("ocr_applied") == gold.ocr_should_run)
    if gold.expected_ocr_policy:
        metrics["ocr_policy_match"] = float(execution.get("ocr_policy") == gold.expected_ocr_policy)
    if gold.expected_primary_layout_provider and provider.layout_path is not None:
        metrics["recommended_layout_provider_match"] = float(
            execution.get("recommended_layout_provider") == gold.expected_primary_layout_provider
        )
        selected_layout_provider_match = _selected_provider_match(
            execution.get("selected_layout_provider"),
            expected_provider=gold.expected_primary_layout_provider,
            acceptable_providers=gold.acceptable_selected_layout_providers,
        )
        if selected_layout_provider_match is not None:
            metrics["selected_layout_provider_match"] = selected_layout_provider_match
    if gold.expected_primary_math_provider and provider.math_path is not None:
        metrics["recommended_math_provider_match"] = float(
            execution.get("recommended_math_provider") == gold.expected_primary_math_provider
        )
        selected_math_provider_match = _selected_provider_match(
            execution.get("selected_math_provider"),
            expected_provider=gold.expected_primary_math_provider,
            acceptable_providers=gold.acceptable_selected_math_providers,
        )
        if selected_math_provider_match is not None:
            metrics["selected_math_provider_match"] = selected_math_provider_match
    if gold.expected_primary_metadata_provider and (provider.metadata_path is not None or provider.layout_path is not None):
        metrics["recommended_metadata_provider_match"] = float(
            execution.get("recommended_metadata_provider") == gold.expected_primary_metadata_provider
        )
        selected_metadata_provider_match = _selected_provider_match(
            execution.get("selected_metadata_provider"),
            expected_provider=gold.expected_primary_metadata_provider,
            acceptable_providers=gold.acceptable_selected_metadata_providers,
        )
        if selected_metadata_provider_match is not None:
            metrics["selected_metadata_provider_match"] = selected_metadata_provider_match
    if gold.expected_primary_reference_provider and (provider.metadata_path is not None or provider.layout_path is not None):
        metrics["recommended_reference_provider_match"] = float(
            execution.get("recommended_reference_provider") == gold.expected_primary_reference_provider
        )
        selected_reference_provider_match = _selected_provider_match(
            execution.get("selected_reference_provider"),
            expected_provider=gold.expected_primary_reference_provider,
            acceptable_providers=gold.acceptable_selected_reference_providers,
        )
        if selected_reference_provider_match is not None:
            metrics["selected_reference_provider_match"] = selected_reference_provider_match
    return metrics


def _execution_score(metrics: dict[str, float]) -> float | None:
    if not metrics:
        return None
    return round(sum(metrics.values()) / len(metrics), 3)


def _overall_score(content_score: float, execution_score: float | None) -> float:
    if execution_score is None:
        return content_score
    return round(content_score * 0.8 + execution_score * 0.2, 3)


def _capability_scores(metrics: dict[str, float]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for capability in CAPABILITY_ORDER:
        values = [float(metrics[name]) for name in CAPABILITY_METRIC_NAMES[capability] if name in metrics]
        if values:
            scores[capability] = round(sum(values) / len(values), 3)
    return scores


def _aggregate_capability_rankings(
    totals: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, Any]]:
    rankings: list[dict[str, Any]] = []
    for capability in CAPABILITY_ORDER:
        provider_values = totals.get(capability, {})
        providers = [
            {
                "provider": provider_name,
                "papers": int(values["papers"]),
                "avg_score": round(values["score_total"] / max(values["papers"], 1), 3),
            }
            for provider_name, values in provider_values.items()
        ]
        providers.sort(key=lambda item: (-float(item["avg_score"]), str(item["provider"])))
        rankings.append({"capability": capability, "providers": providers})
    return rankings


def _load_gold_record(paper_id: str, gold_path: Path) -> AcquisitionGoldRecord:
    payload = _load_json(gold_path)
    return AcquisitionGoldRecord(
        paper_id=paper_id,
        title=str(payload.get("title", "")),
        abstract=str(payload.get("abstract", "")),
        headings=[str(item) for item in payload.get("headings", [])],
        paragraphs=[str(item) for item in payload.get("paragraphs", [])],
        equations=[str(item) for item in payload.get("equations", [])],
        references=[str(item) for item in payload.get("references", [])],
        family=(str(payload.get("family", "")).strip() or None),
        expected_route=(str(payload.get("expected_route", "")).strip() or None),
        expected_route_reason_codes=[
            str(item).strip()
            for item in list(payload.get("expected_route_reason_codes") or payload.get("route_reason_codes") or [])
            if str(item).strip()
        ],
        ocr_should_run=(bool(payload["ocr_should_run"]) if "ocr_should_run" in payload else None),
        expected_ocr_policy=(str(payload.get("expected_ocr_policy", "")).strip() or None),
        expected_primary_layout_provider=(str(payload.get("expected_primary_layout_provider", "")).strip() or None),
        expected_primary_math_provider=(str(payload.get("expected_primary_math_provider", "")).strip() or None),
        expected_primary_metadata_provider=(str(payload.get("expected_primary_metadata_provider", "")).strip() or None),
        expected_primary_reference_provider=(str(payload.get("expected_primary_reference_provider", "")).strip() or None),
        acceptable_selected_layout_providers=[
            str(item).strip()
            for item in list(payload.get("acceptable_selected_layout_providers") or [])
            if str(item).strip()
        ],
        acceptable_selected_math_providers=[
            str(item).strip()
            for item in list(payload.get("acceptable_selected_math_providers") or [])
            if str(item).strip()
        ],
        acceptable_selected_metadata_providers=[
            str(item).strip()
            for item in list(payload.get("acceptable_selected_metadata_providers") or [])
            if str(item).strip()
        ],
        acceptable_selected_reference_providers=[
            str(item).strip()
            for item in list(payload.get("acceptable_selected_reference_providers") or [])
            if str(item).strip()
        ],
    )


def _iter_manifest_papers(payload: dict[str, Any], *, inherited_section: str | None = None) -> list[tuple[str | None, dict[str, Any]]]:
    rows: list[tuple[str | None, dict[str, Any]]] = []
    for paper_payload in list(payload.get("papers", []) or []):
        if isinstance(paper_payload, dict):
            section = str(paper_payload.get("section", "")).strip() or inherited_section
            rows.append((section, paper_payload))
    for section_payload in list(payload.get("sections", []) or []):
        if not isinstance(section_payload, dict):
            continue
        section_name = str(section_payload.get("name", "") or section_payload.get("section", "")).strip() or inherited_section
        rows.extend(_iter_manifest_papers(section_payload, inherited_section=section_name))
    return rows


def load_benchmark_manifest(manifest_path: str | Path) -> list[BenchmarkPaper]:
    resolved_manifest_path = Path(manifest_path).resolve()
    manifest_dir = resolved_manifest_path.parent
    payload = _load_json(resolved_manifest_path)
    papers: list[BenchmarkPaper] = []
    for section_name, paper_payload in _iter_manifest_papers(payload):
        paper_id = str(paper_payload.get("paper_id", "")).strip()
        if not paper_id:
            continue
        gold_path = (manifest_dir / str(paper_payload["gold"])).resolve()
        providers = [
            ProviderArtifacts(
                name=str(provider_name),
                layout_path=(
                    (manifest_dir / str(provider_payload["layout"])).resolve()
                    if provider_payload.get("layout")
                    else None
                ),
                metadata_path=(
                    (manifest_dir / str(provider_payload["metadata"])).resolve()
                    if provider_payload.get("metadata")
                    else None
                ),
                math_path=((manifest_dir / str(provider_payload["math"])).resolve() if provider_payload.get("math") else None),
                execution_path=(
                    (manifest_dir / str(provider_payload["execution"])).resolve()
                    if provider_payload.get("execution")
                    else None
                ),
            )
            for provider_name, provider_payload in (paper_payload.get("providers", {}) or {}).items()
        ]
        gold_payload = _load_json(gold_path)
        papers.append(
            BenchmarkPaper(
                paper_id=paper_id,
                gold_path=gold_path,
                family=(str(gold_payload.get("family", "")).strip() or None),
                section=section_name,
                providers=providers,
            )
        )
    return papers


def run_acquisition_benchmark(manifest_path: str | Path) -> dict[str, Any]:
    papers = load_benchmark_manifest(manifest_path)
    per_paper_results: list[dict[str, Any]] = []
    aggregate_totals: dict[str, dict[str, float]] = {}
    family_totals: dict[str, dict[str, dict[str, float]]] = {}
    capability_totals: dict[str, dict[str, dict[str, float]]] = {capability: {} for capability in CAPABILITY_ORDER}
    family_capability_totals: dict[str, dict[str, dict[str, dict[str, float]]]] = {}

    for paper in papers:
        gold = _load_gold_record(paper.paper_id, paper.gold_path)
        provider_results: list[dict[str, Any]] = []
        for provider in paper.providers:
            observed = _extract_provider_observation(
                provider.name,
                layout_path=provider.layout_path,
                metadata_path=provider.metadata_path,
                math_path=provider.math_path,
            )
            content_metrics = {
                "title_match": float(_contains_normalized(observed["title"], gold.title)),
                "abstract_token_recall": _token_recall(gold.abstract, observed["abstract"]),
                "heading_hit_rate": _list_hit_rate(gold.headings, observed["headings"], observed["full_text"]),
                "paragraph_hit_rate": _list_hit_rate(gold.paragraphs, observed["paragraphs"], observed["full_text"]),
                "equation_hit_rate": _list_hit_rate(gold.equations, observed["equations"], observed["full_text"]),
                "reference_hit_rate": _list_hit_rate(gold.references, observed["references"], observed["full_text"]),
            }
            execution_observation = _extract_execution_observation(provider.execution_path)
            execution_metrics = _execution_metrics(gold, execution_observation, provider=provider)
            content_score = _content_score(content_metrics)
            execution_score = _execution_score(execution_metrics)
            overall = _overall_score(content_score, execution_score)
            capability_scores = _capability_scores({**content_metrics, **execution_metrics})
            result = {
                "provider": provider.name,
                "layout_path": str(provider.layout_path) if provider.layout_path is not None else None,
                "metadata_path": str(provider.metadata_path) if provider.metadata_path is not None else None,
                "math_path": str(provider.math_path) if provider.math_path is not None else None,
                "execution_path": str(provider.execution_path) if provider.execution_path is not None else None,
                "metrics": {
                    **content_metrics,
                    **execution_metrics,
                },
                "content_score": content_score,
                "execution_score": execution_score,
                "overall_score": overall,
                "capability_scores": capability_scores,
                "metadata_observation": observed["metadata_observation"],
                "execution_observation": execution_observation,
            }
            provider_results.append(result)

            provider_totals = aggregate_totals.setdefault(
                provider.name,
                {"papers": 0, "overall_score_total": 0.0, "content_score_total": 0.0, "execution_score_total": 0.0},
            )
            provider_totals["papers"] += 1
            provider_totals["overall_score_total"] += overall
            provider_totals["content_score_total"] += content_score
            provider_totals["execution_score_total"] += execution_score or 0.0

            family_name = gold.family or "unclassified"
            family_provider_totals = family_totals.setdefault(family_name, {}).setdefault(
                provider.name,
                {"papers": 0, "overall_score_total": 0.0, "content_score_total": 0.0, "execution_score_total": 0.0},
            )
            family_provider_totals["papers"] += 1
            family_provider_totals["overall_score_total"] += overall
            family_provider_totals["content_score_total"] += content_score
            family_provider_totals["execution_score_total"] += execution_score or 0.0

            family_name = gold.family or "unclassified"
            family_capability_map = family_capability_totals.setdefault(
                family_name,
                {capability: {} for capability in CAPABILITY_ORDER},
            )
            for capability, score in capability_scores.items():
                capability_provider_totals = capability_totals.setdefault(capability, {}).setdefault(
                    provider.name,
                    {"papers": 0, "score_total": 0.0},
                )
                capability_provider_totals["papers"] += 1
                capability_provider_totals["score_total"] += score

                family_capability_provider_totals = family_capability_map.setdefault(capability, {}).setdefault(
                    provider.name,
                    {"papers": 0, "score_total": 0.0},
                )
                family_capability_provider_totals["papers"] += 1
                family_capability_provider_totals["score_total"] += score

        provider_results.sort(key=lambda item: (-float(item["overall_score"]), str(item["provider"])))
        per_paper_results.append(
            {
                "paper_id": paper.paper_id,
                "gold_path": str(paper.gold_path),
                "section": paper.section,
                "family": gold.family,
                "expected_route": gold.expected_route,
                "expected_route_reason_codes": list(gold.expected_route_reason_codes),
                "ocr_should_run": gold.ocr_should_run,
                "expected_ocr_policy": gold.expected_ocr_policy,
                "expected_primary_layout_provider": gold.expected_primary_layout_provider,
                "expected_primary_math_provider": gold.expected_primary_math_provider,
                "expected_primary_metadata_provider": gold.expected_primary_metadata_provider,
                "expected_primary_reference_provider": gold.expected_primary_reference_provider,
                "acceptable_selected_layout_providers": list(gold.acceptable_selected_layout_providers),
                "acceptable_selected_math_providers": list(gold.acceptable_selected_math_providers),
                "acceptable_selected_metadata_providers": list(gold.acceptable_selected_metadata_providers),
                "acceptable_selected_reference_providers": list(gold.acceptable_selected_reference_providers),
                "providers": provider_results,
            }
        )

    aggregate = [
        {
            "provider": provider_name,
            "papers": int(values["papers"]),
            "avg_overall_score": round(values["overall_score_total"] / max(values["papers"], 1), 3),
            "avg_content_score": round(values["content_score_total"] / max(values["papers"], 1), 3),
            "avg_execution_score": round(values["execution_score_total"] / max(values["papers"], 1), 3),
        }
        for provider_name, values in aggregate_totals.items()
    ]
    aggregate.sort(key=lambda item: (-float(item["avg_overall_score"]), str(item["provider"])))
    families = []
    for family_name, provider_values in sorted(family_totals.items()):
        rankings = [
            {
                "provider": provider_name,
                "papers": int(values["papers"]),
                "avg_overall_score": round(values["overall_score_total"] / max(values["papers"], 1), 3),
                "avg_content_score": round(values["content_score_total"] / max(values["papers"], 1), 3),
                "avg_execution_score": round(values["execution_score_total"] / max(values["papers"], 1), 3),
            }
            for provider_name, values in provider_values.items()
        ]
        rankings.sort(key=lambda item: (-float(item["avg_overall_score"]), str(item["provider"])))
        families.append(
            {
                "family": family_name,
                "paper_count": sum(int(values["papers"]) for values in provider_values.values()),
                "providers": rankings,
            }
        )
    family_capabilities = [
        {
            "family": family_name,
            "capabilities": _aggregate_capability_rankings(capability_values),
        }
        for family_name, capability_values in sorted(family_capability_totals.items())
    ]
    capabilities = _aggregate_capability_rankings(capability_totals)
    return {
        "manifest_path": str(Path(manifest_path).resolve()),
        "paper_count": len(per_paper_results),
        "papers": per_paper_results,
        "aggregate": aggregate,
        "families": families,
        "capabilities": capabilities,
        "family_capabilities": family_capabilities,
        "leaders": {
            **provider_leader_summary(
                aggregate,
                overall_key="avg_overall_score",
                content_key="avg_content_score",
                execution_key="avg_execution_score",
            ),
            "capabilities": capability_leader_rows(capabilities, value_key="avg_score"),
            "families": family_leader_rows(
                families,
                family_capabilities,
                overall_key="avg_overall_score",
                content_key="avg_content_score",
                execution_key="avg_execution_score",
                capability_value_key="avg_score",
            ),
        },
    }


__all__ = [
    "BenchmarkPaper",
    "ProviderArtifacts",
    "load_benchmark_manifest",
    "run_acquisition_benchmark",
]
