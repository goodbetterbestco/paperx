from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.acquisition.benchmark_reports import resolve_benchmark_report_path


def _top_changes(rows: list[dict[str, Any]], *, limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    improvements = sorted(
        (row for row in rows if float(row.get("overall_delta", 0.0)) > 0.0),
        key=lambda row: (-float(row.get("overall_delta", 0.0)), str(row.get("provider", ""))),
    )[:limit]
    regressions = sorted(
        (row for row in rows if float(row.get("overall_delta", 0.0)) < 0.0),
        key=lambda row: (float(row.get("overall_delta", 0.0)), str(row.get("provider", ""))),
    )[:limit]
    return improvements, regressions


def _top_score_changes(rows: list[dict[str, Any]], *, limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    improvements = sorted(
        (row for row in rows if float(row.get("score_delta", 0.0)) > 0.0),
        key=lambda row: (-float(row.get("score_delta", 0.0)), str(row.get("provider", ""))),
    )[:limit]
    regressions = sorted(
        (row for row in rows if float(row.get("score_delta", 0.0)) < 0.0),
        key=lambda row: (float(row.get("score_delta", 0.0)), str(row.get("provider", ""))),
    )[:limit]
    return improvements, regressions


def summarize_benchmark_trend(
    *,
    history_dir: str | Path | None = None,
    base: str = "previous",
    candidate: str = "latest",
    limit: int = 3,
) -> dict[str, Any]:
    resolve_kwargs = {"history_dir": history_dir} if history_dir is not None else {}
    base_path = resolve_benchmark_report_path(base, **resolve_kwargs)
    candidate_path = resolve_benchmark_report_path(candidate, **resolve_kwargs)
    comparison = compare_benchmark_reports(base_path, candidate_path)

    aggregate_improvements, aggregate_regressions = _top_changes(list(comparison.get("aggregate") or []), limit=limit)
    capability_summaries: list[dict[str, Any]] = []
    for capability in list(comparison.get("capabilities") or []):
        providers = list(capability.get("providers") or [])
        improvements, regressions = _top_score_changes(providers, limit=limit)
        capability_summaries.append(
            {
                "capability": capability.get("capability"),
                "improvements": improvements,
                "regressions": regressions,
            }
        )
    family_summaries: list[dict[str, Any]] = []
    for family in list(comparison.get("families") or []):
        providers = list(family.get("providers") or [])
        improvements, regressions = _top_changes(providers, limit=limit)
        capability_summaries_for_family: list[dict[str, Any]] = []
        for capability in list(family.get("capabilities") or []):
            capability_rows = list(capability.get("providers") or [])
            capability_improvements, capability_regressions = _top_score_changes(capability_rows, limit=limit)
            capability_summaries_for_family.append(
                {
                    "capability": capability.get("capability"),
                    "improvements": capability_improvements,
                    "regressions": capability_regressions,
                }
            )
        family_summaries.append(
            {
                "family": family.get("family"),
                "improvements": improvements,
                "regressions": regressions,
                "capabilities": capability_summaries_for_family,
            }
        )

    return {
        "base_report_path": str(base_path.resolve()),
        "candidate_report_path": str(candidate_path.resolve()),
        "base_paper_count": int(comparison.get("base_paper_count", 0) or 0),
        "candidate_paper_count": int(comparison.get("candidate_paper_count", 0) or 0),
        "leaders": comparison.get("leaders") or {},
        "aggregate": list(comparison.get("aggregate") or []),
        "top_improvements": aggregate_improvements,
        "top_regressions": aggregate_regressions,
        "capabilities": capability_summaries,
        "families": family_summaries,
    }


__all__ = ["summarize_benchmark_trend"]
