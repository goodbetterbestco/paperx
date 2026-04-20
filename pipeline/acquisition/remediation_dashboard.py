from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_artifacts import current_remediation_output_dir
from pipeline.acquisition.remediation_history import list_remediation_history
from pipeline.acquisition.remediation_status import summarize_latest_remediation_status
from pipeline.acquisition.remediation_trend import summarize_remediation_trend


def summarize_remediation_dashboard(
    *,
    history_dir: str | Path | None = None,
    history_limit: int = 5,
    trend_limit: int = 3,
) -> dict[str, Any]:
    history_kwargs = {"history_dir": history_dir} if history_dir is not None else {}
    full_history = list_remediation_history(**history_kwargs)
    recent_history = list_remediation_history(limit=history_limit, **history_kwargs)
    status = summarize_latest_remediation_status(
        output_dir=current_remediation_output_dir(history_dir=history_dir) if history_dir is not None else current_remediation_output_dir()
    )

    runs = list(full_history.get("runs") or [])
    latest_run = status.get("latest_run") or {}
    previous_run = runs[-2] if len(runs) >= 2 else None
    trend = None
    if previous_run is not None and latest_run:
        trend = summarize_remediation_trend(history_dir=history_dir, base="previous", candidate="latest")

    overview = {
        "history_dir": full_history.get("history_dir"),
        "run_count": int(full_history.get("run_count", 0) or 0),
        "latest_label": latest_run.get("label"),
        "previous_label": (previous_run or {}).get("label"),
        "latest_requested_count": int(latest_run.get("requested_count", 0) or 0),
        "latest_selected_count": int(latest_run.get("selected_count", 0) or 0),
        "latest_skipped_count": int(latest_run.get("skipped_count", 0) or 0),
        "latest_failed_count": int((latest_run.get("status_counts") or {}).get("failed", 0) or 0),
        "comparison_available": trend is not None,
    }
    return {
        "overview": overview,
        "latest_run": latest_run,
        "previous_run": previous_run,
        "trend": trend,
        "recent_history": list(recent_history.get("runs") or []),
        "alerts": {
            "introduced_failures": list((trend or {}).get("introduced_failures") or [])[:trend_limit],
            "still_failing": list((trend or {}).get("still_failing") or [])[:trend_limit],
            "resolved_failures": list((trend or {}).get("resolved_failures") or [])[:trend_limit],
        },
    }


__all__ = ["summarize_remediation_dashboard"]
