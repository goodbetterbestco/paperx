from __future__ import annotations

from typing import Any


def render_acquisition_remediation_trend_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Remediation Trend",
        "",
        f"- Base report: `{report.get('base_report_path')}`",
        f"- Candidate report: `{report.get('candidate_report_path')}`",
        f"- Base label: `{report.get('base_label') or 'none'}`",
        f"- Candidate label: `{report.get('candidate_label') or 'none'}`",
        "",
        "## Status Deltas",
        "",
    ]
    for row in list(report.get("status_deltas") or []):
        lines.append(
            f"- `{row['status']}`: base `{row['base_count']}`, candidate `{row['candidate_count']}`, delta `{row['delta']}`"
        )

    lines.extend(["", "## Count Deltas", ""])
    count_deltas = dict(report.get("count_deltas") or {})
    lines.append(f"- requested count delta `{count_deltas.get('requested_count', 0)}`")
    lines.append(f"- selected count delta `{count_deltas.get('selected_count', 0)}`")
    lines.append(f"- skipped count delta `{count_deltas.get('skipped_count', 0)}`")

    lines.extend(["", "## Introduced Failures", ""])
    introduced = list(report.get("introduced_failures") or [])
    if not introduced:
        lines.append("- none")
    else:
        for item in introduced:
            lines.append(
                f"- `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}` "
                f"score `{item.get('priority_score', 0)}`"
            )

    lines.extend(["", "## Resolved Failures", ""])
    resolved = list(report.get("resolved_failures") or [])
    if not resolved:
        lines.append("- none")
    else:
        for item in resolved:
            lines.append(f"- `{item.get('paper_id')}` -> `{item.get('resolved_to') or 'unknown'}`")

    lines.extend(["", "## Still Failing", ""])
    still_failing = list(report.get("still_failing") or [])
    if not still_failing:
        lines.append("- none")
    else:
        for item in still_failing:
            lines.append(
                f"- `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}` "
                f"score `{item.get('priority_score', 0)}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_trend_markdown"]
