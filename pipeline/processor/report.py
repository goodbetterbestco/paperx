from __future__ import annotations

from typing import Any


def summarize_run(run_status: dict[str, Any]) -> dict[str, Any]:
    paper_results = run_status.get("papers", {})
    success_results = [item for item in paper_results.values() if item.get("status") == "completed"]
    failed_results = [item for item in paper_results.values() if item.get("status") == "failed"]
    running_results = [item for item in paper_results.values() if item.get("status") == "running"]
    queued_results = [item for item in paper_results.values() if item.get("status") == "queued"]
    anomalies: dict[str, int] = {}
    for item in success_results:
        for flag in item.get("anomalies", []):
            anomalies[flag] = anomalies.get(flag, 0) + 1
    return {
        "success_count": len(success_results),
        "failure_count": len(failed_results),
        "running_count": len(running_results),
        "queued_count": len(queued_results),
        "anomalies": anomalies,
    }


def render_report(status: dict[str, Any]) -> str:
    runs = list(status.get("runs", []))
    lines = [
        "# Canonical Corpus Report",
        "",
        f"- Started: {status.get('started_at', '')}",
        f"- Updated: {status.get('updated_at', '')}",
        f"- Papers targeted: {len(status.get('papers', []))}",
        "",
    ]
    for index, run_status in enumerate(runs, start=1):
        summary = summarize_run(run_status)
        lines.extend(
            [
                f"## Run {index}",
                "",
                f"- Started: {run_status.get('started_at', '')}",
                f"- Completed: {run_status.get('completed_at', '')}",
                f"- Successes: {summary['success_count']}",
                f"- Queued: {summary['queued_count']}",
                f"- Running: {summary['running_count']}",
                f"- Failures: {summary['failure_count']}",
            ]
        )
        if summary["anomalies"]:
            lines.append("- Common anomalies:")
            for key, value in sorted(summary["anomalies"].items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - `{key}`: {value}")
        lines.append("")

    lines.append("## Paper Status")
    lines.append("")
    if runs:
        header = ["Paper", *[f"Run {index}" for index in range(1, len(runs) + 1)]]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    else:
        lines.append("| Paper | Status |")
        lines.append("| --- | --- |")
    for paper_id in status.get("papers", []):
        row = [paper_id]
        for run_status in runs:
            paper_status = run_status.get("papers", {}).get(paper_id, {})
            if paper_status.get("status") == "completed":
                metrics = paper_status.get("metrics", {})
                cell = f"completed ({metrics.get('sections', 0)} s / {metrics.get('references', 0)} r / {metrics.get('figures', 0)} f)"
                anomalies = paper_status.get("anomalies", [])
                if anomalies:
                    cell += f" {';'.join(anomalies[:3])}"
            elif paper_status.get("status") == "running":
                cell = f"running (started {paper_status.get('started_at', '')})"
            elif paper_status.get("status") == "queued":
                phase = str(((paper_status.get("mathpix") or {}).get("phase") or "")).strip()
                cell = f"queued (mathpix {phase})" if phase else "queued"
            elif paper_status:
                cell = "failed"
            else:
                cell = "not-run"
            row.append(cell)
        if len(row) == 1:
            row.append("not-run")
        lines.append("| " + " | ".join(row) + " |")
    lines.extend(["", "## Notes", ""])
    for note in status.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


__all__ = ["render_report", "summarize_run"]
