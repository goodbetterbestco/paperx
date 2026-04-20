from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.acquisition.benchmark_history import list_benchmark_history
from pipeline.acquisition.benchmark_status import summarize_latest_benchmark_status


def _capability_regressions(trend: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for capability in list(trend.get("capabilities") or []):
        for row in list(capability.get("regressions") or []):
            rows.append(
                {
                    "capability": capability.get("capability"),
                    "provider": row.get("provider"),
                    "score_delta": row.get("score_delta"),
                }
            )
    rows.sort(key=lambda item: (float(item.get("score_delta", 0.0)), str(item.get("provider", ""))))
    return rows[:limit]


def _family_regressions(trend: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in list(trend.get("families") or []):
        for row in list(family.get("regressions") or []):
            rows.append(
                {
                    "family": family.get("family"),
                    "provider": row.get("provider"),
                    "overall_delta": row.get("overall_delta"),
                    "content_delta": row.get("content_delta"),
                    "execution_delta": row.get("execution_delta"),
                }
            )
    rows.sort(key=lambda item: (float(item.get("overall_delta", 0.0)), str(item.get("provider", ""))))
    return rows[:limit]


def summarize_benchmark_dashboard(
    *,
    history_dir: str | Path | None = None,
    history_limit: int = 5,
    trend_limit: int = 3,
) -> dict[str, Any]:
    history_kwargs = {"history_dir": history_dir} if history_dir is not None else {}
    full_history = list_benchmark_history(**history_kwargs)
    recent_history = list_benchmark_history(limit=history_limit, **history_kwargs)
    status = summarize_latest_benchmark_status(limit=trend_limit, **history_kwargs)

    runs = list(full_history.get("runs") or [])
    latest_run = status.get("latest_run")
    previous_run = runs[-2] if len(runs) >= 2 else None
    comparison = None
    if latest_run is not None and previous_run is not None:
        comparison = compare_benchmark_reports(previous_run["path"], latest_run["path"])

    trend = status.get("trend") or {}
    overview = {
        "history_dir": full_history.get("history_dir"),
        "run_count": int(full_history.get("run_count", 0) or 0),
        "latest_label": (latest_run or {}).get("label"),
        "previous_label": (previous_run or {}).get("label"),
        "latest_paper_count": int((latest_run or {}).get("paper_count", 0) or 0),
        "latest_provider_count": int((latest_run or {}).get("provider_count", 0) or 0),
        "comparison_available": comparison is not None,
    }

    return {
        "overview": overview,
        "latest_run": latest_run,
        "previous_run": previous_run,
        "leaders": status.get("leaders") or {},
        "trend": trend,
        "comparison": comparison,
        "recent_history": list(recent_history.get("runs") or []),
        "alerts": {
            "provider_regressions": list(trend.get("top_regressions") or [])[:trend_limit],
            "capability_regressions": _capability_regressions(trend, limit=trend_limit),
            "family_regressions": _family_regressions(trend, limit=trend_limit),
        },
    }


__all__ = ["summarize_benchmark_dashboard"]
