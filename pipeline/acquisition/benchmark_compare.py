from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_reports import (
    DEFAULT_HISTORY_DIR,
    aggregate_provider_score_map,
    benchmark_capability_score_maps,
    family_capability_score_maps,
    family_provider_score_maps,
    load_benchmark_report,
    resolve_benchmark_report_path,
)


def _delta_table(
    base_scores: dict[str, dict[str, float]],
    candidate_scores: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    providers = sorted(set(base_scores) | set(candidate_scores))
    rows: list[dict[str, Any]] = []
    for provider in providers:
        base = base_scores.get(provider, {})
        candidate = candidate_scores.get(provider, {})
        rows.append(
            {
                "provider": provider,
                "base_overall": round(float(base.get("overall", 0.0)), 3),
                "candidate_overall": round(float(candidate.get("overall", 0.0)), 3),
                "overall_delta": round(float(candidate.get("overall", 0.0)) - float(base.get("overall", 0.0)), 3),
                "content_delta": round(float(candidate.get("content", 0.0)) - float(base.get("content", 0.0)), 3),
                "execution_delta": round(float(candidate.get("execution", 0.0)) - float(base.get("execution", 0.0)), 3),
            }
        )
    rows.sort(key=lambda item: (-float(item["overall_delta"]), item["provider"]))
    return rows


def _score_delta_table(
    base_scores: dict[str, dict[str, float]],
    candidate_scores: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    providers = sorted(set(base_scores) | set(candidate_scores))
    rows: list[dict[str, Any]] = []
    for provider in providers:
        base = base_scores.get(provider, {})
        candidate = candidate_scores.get(provider, {})
        rows.append(
            {
                "provider": provider,
                "base_score": round(float(base.get("score", 0.0)), 3),
                "candidate_score": round(float(candidate.get("score", 0.0)), 3),
                "score_delta": round(float(candidate.get("score", 0.0)) - float(base.get("score", 0.0)), 3),
            }
        )
    rows.sort(key=lambda item: (-float(item["score_delta"]), item["provider"]))
    return rows


def compare_benchmark_reports(base_path: str | Path, candidate_path: str | Path) -> dict[str, Any]:
    base_report = load_benchmark_report(base_path)
    candidate_report = load_benchmark_report(candidate_path)
    family_names = sorted(
        {
            str(item.get("family", "") or "").strip()
            for item in list(base_report.get("families") or []) + list(candidate_report.get("families") or [])
            if str(item.get("family", "") or "").strip()
        }
    )

    base_family_map = family_provider_score_maps(base_report)
    candidate_family_map = family_provider_score_maps(candidate_report)
    base_capability_map = benchmark_capability_score_maps(base_report)
    candidate_capability_map = benchmark_capability_score_maps(candidate_report)
    base_family_capability_map = family_capability_score_maps(base_report)
    candidate_family_capability_map = family_capability_score_maps(candidate_report)

    family_deltas = [
        {
            "family": family,
            "providers": _delta_table(base_family_map.get(family, {}), candidate_family_map.get(family, {})),
            "capabilities": [
                {
                    "capability": capability,
                    "providers": _score_delta_table(
                        base_family_capability_map.get(family, {}).get(capability, {}),
                        candidate_family_capability_map.get(family, {}).get(capability, {}),
                    ),
                }
                for capability in sorted(
                    set(base_family_capability_map.get(family, {})) | set(candidate_family_capability_map.get(family, {}))
                )
            ],
        }
        for family in family_names
    ]
    return {
        "base_report_path": str(Path(base_path).resolve()),
        "candidate_report_path": str(Path(candidate_path).resolve()),
        "base_paper_count": int(base_report.get("paper_count", 0) or 0),
        "candidate_paper_count": int(candidate_report.get("paper_count", 0) or 0),
        "aggregate": _delta_table(
            aggregate_provider_score_map(base_report),
            aggregate_provider_score_map(candidate_report),
        ),
        "capabilities": [
            {
                "capability": capability,
                "providers": _score_delta_table(
                    base_capability_map.get(capability, {}),
                    candidate_capability_map.get(capability, {}),
                ),
            }
            for capability in sorted(set(base_capability_map) | set(candidate_capability_map))
        ],
        "families": family_deltas,
    }


__all__ = ["DEFAULT_HISTORY_DIR", "compare_benchmark_reports", "resolve_benchmark_report_path"]
