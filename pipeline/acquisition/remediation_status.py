from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_artifacts import (
    DEFAULT_REMEDIATION_OUTPUT_DIR,
    load_current_remediation_summary,
)


def summarize_latest_remediation_status(
    *,
    output_dir: str | Path = DEFAULT_REMEDIATION_OUTPUT_DIR,
    load_summary_fn=load_current_remediation_summary,
) -> dict[str, Any]:
    summary = load_summary_fn(output_dir=output_dir)
    results = list(summary.get("results") or [])
    skipped = list(summary.get("skipped_papers") or [])
    failures = [
        {
            "paper_id": str(item.get("paper_id") or ""),
            "priority": str(item.get("priority") or ""),
            "priority_score": int(item.get("priority_score") or 0),
            "returncode": int(item.get("returncode") or 0),
            "stderr": str(item.get("stderr") or ""),
        }
        for item in results
        if str(item.get("status") or "") == "failed"
    ]
    return {
        "output_dir": str(Path(output_dir).resolve()),
        "latest_run": {
            "label": summary.get("snapshot_label"),
            "generated_at": summary.get("generated_at"),
            "mode": summary.get("mode"),
            "source": summary.get("source") or {},
            "plan": summary.get("plan") or {},
            "resume": summary.get("resume"),
            "selected_count": int(summary.get("selected_count") or 0),
            "requested_count": int(summary.get("requested_count") or 0),
            "skipped_count": int(summary.get("skipped_count") or 0),
            "selected_papers": list(summary.get("selected_papers") or []),
            "selected_priorities": list(summary.get("selected_priorities") or []),
            "status_counts": dict(summary.get("status_counts") or {}),
            "report_paths": dict(summary.get("report_paths") or {}),
        },
        "failures": failures,
        "skipped_papers": skipped,
        "results": results,
    }


__all__ = ["summarize_latest_remediation_status"]
