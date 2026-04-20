from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_reports import (
    DEFAULT_REMEDIATION_HISTORY_DIR,
    list_remediation_history_reports,
    load_remediation_report,
)


def _status_count(report: dict[str, Any], status: str) -> int:
    return int((report.get("status_counts") or {}).get(status, 0) or 0)


def list_remediation_history(
    history_dir: str | Path = DEFAULT_REMEDIATION_HISTORY_DIR,
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    history_paths = list_remediation_history_reports(history_dir)
    if limit is not None and limit > 0:
        history_paths = history_paths[-limit:]

    runs: list[dict[str, Any]] = []
    previous_counts: dict[str, int] = {}
    for path in history_paths:
        report = load_remediation_report(path)
        current_counts = {
            "requested_count": int(report.get("requested_count", 0) or 0),
            "selected_count": int(report.get("selected_count", 0) or 0),
            "skipped_count": int(report.get("skipped_count", 0) or 0),
            "planned_count": _status_count(report, "planned"),
            "succeeded_count": _status_count(report, "succeeded"),
            "failed_count": _status_count(report, "failed"),
            "skipped_succeeded_count": _status_count(report, "skipped_succeeded"),
        }
        runs.append(
            {
                "label": str(report.get("snapshot_label") or path.stem),
                "path": str(path.resolve()),
                "generated_at": report.get("generated_at"),
                "mode": report.get("mode"),
                "source_kind": str((report.get("source") or {}).get("kind") or ""),
                "requested_count": current_counts["requested_count"],
                "selected_count": current_counts["selected_count"],
                "skipped_count": current_counts["skipped_count"],
                "planned_count": current_counts["planned_count"],
                "succeeded_count": current_counts["succeeded_count"],
                "failed_count": current_counts["failed_count"],
                "skipped_succeeded_count": current_counts["skipped_succeeded_count"],
                "selected_priorities": list(report.get("selected_priorities") or []),
                "status_counts": dict(report.get("status_counts") or {}),
                "requested_delta_vs_previous": current_counts["requested_count"] - int(previous_counts.get("requested_count", current_counts["requested_count"])),
                "selected_delta_vs_previous": current_counts["selected_count"] - int(previous_counts.get("selected_count", current_counts["selected_count"])),
                "skipped_delta_vs_previous": current_counts["skipped_count"] - int(previous_counts.get("skipped_count", current_counts["skipped_count"])),
                "succeeded_delta_vs_previous": current_counts["succeeded_count"] - int(previous_counts.get("succeeded_count", current_counts["succeeded_count"])),
                "failed_delta_vs_previous": current_counts["failed_count"] - int(previous_counts.get("failed_count", current_counts["failed_count"])),
            }
        )
        previous_counts = current_counts

    return {
        "history_dir": str(Path(history_dir).resolve()),
        "run_count": len(runs),
        "runs": runs,
    }


__all__ = ["list_remediation_history"]
