from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_history import list_benchmark_history
from pipeline.acquisition.benchmark_reports import capability_leader_rows, provider_leader_summary
from pipeline.acquisition.benchmark_trend import summarize_benchmark_trend


def summarize_latest_benchmark_status(
    *,
    history_dir: str | Path | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    history_kwargs = {"history_dir": history_dir} if history_dir is not None else {}
    history = list_benchmark_history(limit=1, **history_kwargs)
    try:
        trend = summarize_benchmark_trend(limit=limit, **history_kwargs)
    except FileNotFoundError:
        trend = None
    latest_run = list(history.get("runs") or [])
    latest = latest_run[-1] if latest_run else None
    latest_providers = list((latest or {}).get("providers") or [])
    latest_capabilities = list((latest or {}).get("capabilities") or [])
    leaders = dict((latest or {}).get("leaders") or {})
    if not leaders:
        leaders = provider_leader_summary(latest_providers)
        leaders["capabilities"] = capability_leader_rows(latest_capabilities)

    return {
        "history_dir": history.get("history_dir"),
        "latest_run": latest,
        "leaders": leaders,
        "trend": trend,
    }


__all__ = ["summarize_latest_benchmark_status"]
