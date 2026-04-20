from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_reports import (
    DEFAULT_REMEDIATION_HISTORY_DIR,
    load_remediation_report,
    resolve_remediation_report_path,
)


def _results_by_status(report: dict[str, Any], status: str) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("paper_id") or ""): dict(item)
        for item in list(report.get("results") or [])
        if str(item.get("status") or "") == status and str(item.get("paper_id") or "")
    }


def _skipped_successes(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("paper_id") or ""): dict(item)
        for item in list(report.get("skipped_papers") or [])
        if str(item.get("paper_id") or "")
    }


def summarize_remediation_trend(
    *,
    history_dir: str | Path | None = None,
    base: str = "previous",
    candidate: str = "latest",
) -> dict[str, Any]:
    resolve_kwargs = {"history_dir": history_dir} if history_dir is not None else {"history_dir": DEFAULT_REMEDIATION_HISTORY_DIR}
    base_path = resolve_remediation_report_path(base, **resolve_kwargs)
    candidate_path = resolve_remediation_report_path(candidate, **resolve_kwargs)
    base_report = load_remediation_report(base_path, **resolve_kwargs)
    candidate_report = load_remediation_report(candidate_path, **resolve_kwargs)

    statuses = sorted(set((base_report.get("status_counts") or {}).keys()) | set((candidate_report.get("status_counts") or {}).keys()))
    status_deltas = [
        {
            "status": status,
            "base_count": int((base_report.get("status_counts") or {}).get(status, 0) or 0),
            "candidate_count": int((candidate_report.get("status_counts") or {}).get(status, 0) or 0),
            "delta": int((candidate_report.get("status_counts") or {}).get(status, 0) or 0)
            - int((base_report.get("status_counts") or {}).get(status, 0) or 0),
        }
        for status in statuses
    ]

    base_failures = _results_by_status(base_report, "failed")
    candidate_failures = _results_by_status(candidate_report, "failed")
    base_successes = _results_by_status(base_report, "succeeded")
    candidate_successes = _results_by_status(candidate_report, "succeeded")
    base_skipped = _skipped_successes(base_report)
    candidate_skipped = _skipped_successes(candidate_report)

    introduced_failures = [candidate_failures[paper_id] for paper_id in sorted(set(candidate_failures) - set(base_failures))]
    resolved_failures = [
        {
            "paper_id": paper_id,
            "resolved_to": "succeeded" if paper_id in candidate_successes else "skipped_succeeded" if paper_id in candidate_skipped else "absent",
        }
        for paper_id in sorted(set(base_failures) - set(candidate_failures))
    ]
    still_failing = [candidate_failures[paper_id] for paper_id in sorted(set(candidate_failures) & set(base_failures))]
    newly_skipped_successes = [candidate_skipped[paper_id] for paper_id in sorted(set(candidate_skipped) - set(base_skipped))]

    count_deltas = {
        "requested_count": int(candidate_report.get("requested_count", 0) or 0) - int(base_report.get("requested_count", 0) or 0),
        "selected_count": int(candidate_report.get("selected_count", 0) or 0) - int(base_report.get("selected_count", 0) or 0),
        "skipped_count": int(candidate_report.get("skipped_count", 0) or 0) - int(base_report.get("skipped_count", 0) or 0),
    }

    return {
        "base_report_path": str(base_path.resolve()),
        "candidate_report_path": str(candidate_path.resolve()),
        "base_label": str(base_report.get("snapshot_label") or base_path.stem),
        "candidate_label": str(candidate_report.get("snapshot_label") or candidate_path.stem),
        "base_generated_at": base_report.get("generated_at"),
        "candidate_generated_at": candidate_report.get("generated_at"),
        "base_status_counts": dict(base_report.get("status_counts") or {}),
        "candidate_status_counts": dict(candidate_report.get("status_counts") or {}),
        "status_deltas": status_deltas,
        "count_deltas": count_deltas,
        "introduced_failures": introduced_failures,
        "resolved_failures": resolved_failures,
        "still_failing": still_failing,
        "newly_skipped_successes": newly_skipped_successes,
    }


__all__ = ["summarize_remediation_trend"]
