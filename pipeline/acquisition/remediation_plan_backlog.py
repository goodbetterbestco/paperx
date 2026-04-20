from __future__ import annotations

from typing import Any


DEFAULT_BACKLOG_STATUSES = ("pending", "planned_only", "failed")


def select_remediation_plan_waves(
    status_report: dict[str, Any],
    *,
    statuses: list[str] | tuple[str, ...] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    selected_statuses = [
        str(status).strip()
        for status in (statuses or DEFAULT_BACKLOG_STATUSES)
        if str(status).strip()
    ]
    selected_status_set = set(selected_statuses)
    waves = [
        dict(wave)
        for wave in list(status_report.get("waves") or [])
        if str(wave.get("execution_status") or "") in selected_status_set
    ]
    if limit is not None:
        waves = waves[: max(0, int(limit))]
    return {
        "plan": dict(status_report.get("plan") or {}),
        "selected_statuses": selected_statuses,
        "selected_count": len(waves),
        "wave_ids": [str(wave.get("wave_id") or "") for wave in waves],
        "waves": waves,
    }


__all__ = ["DEFAULT_BACKLOG_STATUSES", "select_remediation_plan_waves"]
