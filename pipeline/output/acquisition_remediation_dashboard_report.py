from __future__ import annotations

from typing import Any


def render_acquisition_remediation_dashboard_markdown(report: dict[str, Any]) -> str:
    overview = dict(report.get("overview") or {})
    latest = dict(report.get("latest_run") or {})
    alerts = dict(report.get("alerts") or {})
    trend = report.get("trend") or {}
    lines = [
        "# Acquisition Remediation Dashboard",
        "",
        f"- History directory: `{overview.get('history_dir')}`",
        f"- Saved runs: `{overview.get('run_count', 0)}`",
        f"- Latest run: `{overview.get('latest_label') or 'none'}`",
        f"- Previous run: `{overview.get('previous_label') or 'none'}`",
        f"- Latest requested count: `{overview.get('latest_requested_count', 0)}`",
        f"- Latest selected count: `{overview.get('latest_selected_count', 0)}`",
        f"- Latest skipped count: `{overview.get('latest_skipped_count', 0)}`",
        f"- Latest failed count: `{overview.get('latest_failed_count', 0)}`",
        f"- Comparison available: `{str(bool(overview.get('comparison_available'))).lower()}`",
        "",
        "## Latest Run",
        "",
        f"- Mode: `{latest.get('mode') or 'unknown'}`",
        f"- Generated at: `{latest.get('generated_at') or 'none'}`",
        f"- Status counts: {', '.join(f'`{key}`={value}' for key, value in sorted(dict(latest.get('status_counts') or {}).items())) or 'none'}",
        "",
        "## Alerts",
        "",
    ]

    introduced = list(alerts.get("introduced_failures") or [])
    still_failing = list(alerts.get("still_failing") or [])
    resolved = list(alerts.get("resolved_failures") or [])
    if not introduced and not still_failing and not resolved:
        lines.append("- none")
    else:
        for item in introduced:
            lines.append(f"- introduced failure `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}`")
        for item in still_failing:
            lines.append(f"- still failing `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}`")
        for item in resolved:
            lines.append(f"- resolved failure `{item.get('paper_id')}` -> `{item.get('resolved_to') or 'unknown'}`")

    lines.extend(["", "## Latest vs Previous", ""])
    if not trend:
        lines.append("- Not enough history for a latest-vs-previous remediation comparison yet.")
    else:
        for row in list(trend.get("status_deltas") or []):
            lines.append(
                f"- `{row.get('status')}`: base `{row.get('base_count', 0)}`, candidate `{row.get('candidate_count', 0)}`, delta `{row.get('delta', 0)}`"
            )

    lines.extend(["", "## Recent Runs", ""])
    for run in reversed(list(report.get("recent_history") or [])):
        lines.append(
            f"- `{run['label']}`: selected `{run.get('selected_count', 0)}`, skipped `{run.get('skipped_count', 0)}`, "
            f"succeeded `{run.get('succeeded_count', 0)}`, failed `{run.get('failed_count', 0)}`"
        )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_dashboard_markdown"]
