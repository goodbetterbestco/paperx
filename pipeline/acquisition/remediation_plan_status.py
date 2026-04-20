from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_plan_artifacts import (
    DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
    load_current_remediation_plan_summary,
)
from pipeline.acquisition.remediation_plan_reports import (
    load_remediation_plan_report,
    resolve_remediation_plan_report_path,
)
from pipeline.acquisition.remediation_reports import (
    DEFAULT_REMEDIATION_HISTORY_DIR,
    list_remediation_history_reports,
    load_remediation_report,
)


def _normalize_run(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    status_counts = dict(report.get("status_counts") or {})
    return {
        "label": str(report.get("snapshot_label") or path.stem),
        "path": str(path.resolve()),
        "generated_at": report.get("generated_at"),
        "mode": str(report.get("mode") or ""),
        "plan_label": str((report.get("plan") or {}).get("label") or ""),
        "plan_wave_id": str((report.get("plan") or {}).get("wave_id") or ""),
        "selected_count": int(report.get("selected_count") or 0),
        "status_counts": status_counts,
        "succeeded_count": int(status_counts.get("succeeded", 0) or 0),
        "failed_count": int(status_counts.get("failed", 0) or 0),
        "skipped_succeeded_count": int(status_counts.get("skipped_succeeded", 0) or 0),
    }


def _matching_runs(
    *,
    plan_label: str,
    remediation_history_dir: str | Path,
    list_history_reports_fn=list_remediation_history_reports,
    load_report_fn=load_remediation_report,
) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in list_history_reports_fn(remediation_history_dir):
        report = load_report_fn(path)
        run = _normalize_run(path, report)
        if run["plan_label"] != plan_label:
            continue
        runs.append(run)
    runs.sort(key=lambda item: (str(item.get("generated_at") or ""), str(item.get("label") or ""), str(item["path"])))
    return runs


def _wave_status(runs: list[dict[str, Any]]) -> str:
    if not runs:
        return "pending"
    execute_runs = [run for run in runs if run["mode"] == "execute"]
    if not execute_runs:
        return "planned_only"
    latest_execute = execute_runs[-1]
    if int(latest_execute.get("failed_count", 0) or 0) > 0:
        return "failed"
    return "succeeded"


def summarize_remediation_plan_status(
    *,
    from_plan: str | Path | None = None,
    plan_output_dir: str | Path = DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
    remediation_history_dir: str | Path = DEFAULT_REMEDIATION_HISTORY_DIR,
    load_current_plan_fn=load_current_remediation_plan_summary,
    load_plan_report_fn=load_remediation_plan_report,
    resolve_plan_path_fn=resolve_remediation_plan_report_path,
    list_history_reports_fn=list_remediation_history_reports,
    load_remediation_report_fn=load_remediation_report,
) -> dict[str, Any]:
    plan_output_dir = Path(plan_output_dir)
    plan_history_dir = plan_output_dir / "history"
    if from_plan is not None:
        plan = load_plan_report_fn(from_plan, history_dir=plan_history_dir)
        plan_path = resolve_plan_path_fn(from_plan, history_dir=plan_history_dir)
    else:
        plan = load_current_plan_fn(output_dir=plan_output_dir)
        plan_path = plan_output_dir / "summary.json"

    plan_label = str(plan.get("snapshot_label") or plan_path.stem)
    matching_runs = _matching_runs(
        plan_label=plan_label,
        remediation_history_dir=remediation_history_dir,
        list_history_reports_fn=list_history_reports_fn,
        load_report_fn=load_remediation_report_fn,
    )
    runs_by_wave: dict[str, list[dict[str, Any]]] = {}
    for run in matching_runs:
        wave_id = str(run.get("plan_wave_id") or "")
        if not wave_id:
            continue
        runs_by_wave.setdefault(wave_id, []).append(run)

    wave_summaries: list[dict[str, Any]] = []
    status_counts = {"pending": 0, "planned_only": 0, "succeeded": 0, "failed": 0}
    for wave in list(plan.get("waves") or []):
        wave_id = str(wave.get("wave_id") or "")
        wave_runs = list(runs_by_wave.get(wave_id, []))
        execute_runs = [run for run in wave_runs if run["mode"] == "execute"]
        dry_run_runs = [run for run in wave_runs if run["mode"] == "dry_run"]
        latest_run = execute_runs[-1] if execute_runs else (wave_runs[-1] if wave_runs else None)
        execution_status = _wave_status(wave_runs)
        status_counts[execution_status] += 1
        wave_summaries.append(
            {
                "wave_id": wave_id,
                "wave_kind": str(wave.get("wave_kind") or ""),
                "priority_label": str(wave.get("priority_label") or ""),
                "provider_focus": str(wave.get("provider_focus") or ""),
                "paper_count": int(wave.get("paper_count") or len(list(wave.get("paper_ids") or []))),
                "paper_ids": list(wave.get("paper_ids") or []),
                "selected_priorities": list(wave.get("selected_priorities") or []),
                "execution_command": str(wave.get("execution_command") or ""),
                "execution_status": execution_status,
                "attempt_count": len(wave_runs),
                "execute_attempt_count": len(execute_runs),
                "dry_run_attempt_count": len(dry_run_runs),
                "latest_run": latest_run,
                "run_labels": [str(run.get("label") or "") for run in wave_runs],
            }
        )

    wave_ids = {str(wave.get("wave_id") or "") for wave in list(plan.get("waves") or []) if str(wave.get("wave_id") or "")}
    orphan_runs = [run for run in matching_runs if str(run.get("plan_wave_id") or "") not in wave_ids]

    failed_waves = [wave for wave in wave_summaries if wave["execution_status"] == "failed"]
    pending_waves = [wave for wave in wave_summaries if wave["execution_status"] == "pending"]
    planned_only_waves = [wave for wave in wave_summaries if wave["execution_status"] == "planned_only"]

    return {
        "plan": {
            "label": plan_label,
            "path": str(plan_path),
            "generated_at": plan.get("generated_at"),
            "source": dict(plan.get("source") or {}),
            "queue_count": int(plan.get("queue_count") or 0),
            "wave_count": int(plan.get("wave_count") or len(wave_summaries)),
            "wave_kind_counts": dict(plan.get("wave_kind_counts") or {}),
            "provider_focus_counts": dict(plan.get("provider_focus_counts") or {}),
            "report_paths": dict(plan.get("report_paths") or {}),
        },
        "overview": {
            "planned_waves": len(wave_summaries),
            "pending_waves": status_counts["pending"],
            "planned_only_waves": status_counts["planned_only"],
            "executed_waves": status_counts["succeeded"] + status_counts["failed"],
            "succeeded_waves": status_counts["succeeded"],
            "failed_waves": status_counts["failed"],
            "matched_run_count": len(matching_runs),
            "execute_attempts": sum(int(wave["execute_attempt_count"]) for wave in wave_summaries),
            "dry_run_attempts": sum(int(wave["dry_run_attempt_count"]) for wave in wave_summaries),
            "orphan_run_count": len(orphan_runs),
            "wave_status_counts": status_counts,
        },
        "waves": wave_summaries,
        "failed_waves": failed_waves,
        "pending_waves": pending_waves,
        "planned_only_waves": planned_only_waves,
        "orphan_runs": orphan_runs,
    }


__all__ = ["summarize_remediation_plan_status"]
