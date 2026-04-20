from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_plan_artifacts import DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR
from pipeline.acquisition.remediation_plan_history import list_remediation_plan_history
from pipeline.acquisition.remediation_plan_status import summarize_remediation_plan_status
from pipeline.acquisition.remediation_reports import DEFAULT_REMEDIATION_HISTORY_DIR


def summarize_remediation_plan_dashboard(
    *,
    from_plan: str | Path | None = None,
    plan_output_dir: str | Path = DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
    remediation_history_dir: str | Path = DEFAULT_REMEDIATION_HISTORY_DIR,
    history_limit: int = 5,
    wave_limit: int = 5,
    summarize_status_fn=summarize_remediation_plan_status,
    list_history_fn=list_remediation_plan_history,
) -> dict[str, Any]:
    status = summarize_status_fn(
        from_plan=from_plan,
        plan_output_dir=plan_output_dir,
        remediation_history_dir=remediation_history_dir,
    )
    history = list_history_fn(
        plan_history_dir=Path(plan_output_dir) / "history",
        remediation_history_dir=remediation_history_dir,
        limit=history_limit,
    )
    plan = dict(status.get("plan") or {})
    overview = dict(status.get("overview") or {})
    return {
        "overview": {
            "plan_label": plan.get("label"),
            "plan_generated_at": plan.get("generated_at"),
            "queue_count": int(plan.get("queue_count") or 0),
            "planned_waves": int(overview.get("planned_waves") or 0),
            "pending_waves": int(overview.get("pending_waves") or 0),
            "planned_only_waves": int(overview.get("planned_only_waves") or 0),
            "succeeded_waves": int(overview.get("succeeded_waves") or 0),
            "failed_waves": int(overview.get("failed_waves") or 0),
            "execute_attempts": int(overview.get("execute_attempts") or 0),
            "dry_run_attempts": int(overview.get("dry_run_attempts") or 0),
            "orphan_run_count": int(overview.get("orphan_run_count") or 0),
            "saved_plan_count": int(history.get("plan_count") or 0),
        },
        "plan": plan,
        "current_status": status,
        "recent_history": list(history.get("plans") or []),
        "alerts": {
            "failed_waves": list(status.get("failed_waves") or [])[:wave_limit],
            "pending_waves": list(status.get("pending_waves") or [])[:wave_limit],
            "planned_only_waves": list(status.get("planned_only_waves") or [])[:wave_limit],
            "orphan_runs": list(status.get("orphan_runs") or [])[:wave_limit],
        },
    }


__all__ = ["summarize_remediation_plan_dashboard"]
