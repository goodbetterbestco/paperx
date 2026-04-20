from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_plan_reports import (
    DEFAULT_REMEDIATION_PLAN_HISTORY_DIR,
    list_remediation_plan_history_reports,
)
from pipeline.acquisition.remediation_plan_status import summarize_remediation_plan_status
from pipeline.acquisition.remediation_reports import DEFAULT_REMEDIATION_HISTORY_DIR


def list_remediation_plan_history(
    plan_history_dir: str | Path = DEFAULT_REMEDIATION_PLAN_HISTORY_DIR,
    *,
    remediation_history_dir: str | Path = DEFAULT_REMEDIATION_HISTORY_DIR,
    limit: int | None = None,
    list_history_reports_fn=list_remediation_plan_history_reports,
    summarize_status_fn=summarize_remediation_plan_status,
) -> dict[str, Any]:
    history_paths = list_history_reports_fn(plan_history_dir)
    if limit is not None and limit > 0:
        history_paths = history_paths[-limit:]

    plans: list[dict[str, Any]] = []
    for path in history_paths:
        status = summarize_status_fn(
            from_plan=path,
            plan_output_dir=Path(plan_history_dir).resolve().parent,
            remediation_history_dir=remediation_history_dir,
        )
        plan = dict(status.get("plan") or {})
        overview = dict(status.get("overview") or {})
        plans.append(
            {
                "label": str(plan.get("label") or path.stem),
                "path": str(path.resolve()),
                "generated_at": plan.get("generated_at"),
                "source_kind": str((plan.get("source") or {}).get("kind") or ""),
                "queue_count": int(plan.get("queue_count") or 0),
                "wave_count": int(plan.get("wave_count") or 0),
                "pending_waves": int(overview.get("pending_waves") or 0),
                "planned_only_waves": int(overview.get("planned_only_waves") or 0),
                "succeeded_waves": int(overview.get("succeeded_waves") or 0),
                "failed_waves": int(overview.get("failed_waves") or 0),
                "execute_attempts": int(overview.get("execute_attempts") or 0),
                "dry_run_attempts": int(overview.get("dry_run_attempts") or 0),
                "orphan_run_count": int(overview.get("orphan_run_count") or 0),
            }
        )

    return {
        "history_dir": str(Path(plan_history_dir).resolve()),
        "plan_count": len(plans),
        "plans": plans,
    }


__all__ = ["list_remediation_plan_history"]
