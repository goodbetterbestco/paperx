from __future__ import annotations

from typing import Any


def render_acquisition_remediation_plan_dashboard_markdown(report: dict[str, Any]) -> str:
    overview = dict(report.get("overview") or {})
    lines = [
        "# Acquisition Remediation Plan Dashboard",
        "",
        f"- Plan label: `{overview.get('plan_label') or 'none'}`",
        f"- Generated at: `{overview.get('plan_generated_at') or 'none'}`",
        f"- Queue items: `{overview.get('queue_count', 0)}`",
        f"- Planned waves: `{overview.get('planned_waves', 0)}`",
        f"- Pending waves: `{overview.get('pending_waves', 0)}`",
        f"- Dry-run only waves: `{overview.get('planned_only_waves', 0)}`",
        f"- Succeeded waves: `{overview.get('succeeded_waves', 0)}`",
        f"- Failed waves: `{overview.get('failed_waves', 0)}`",
        f"- Execute attempts: `{overview.get('execute_attempts', 0)}`",
        f"- Dry-run attempts: `{overview.get('dry_run_attempts', 0)}`",
        f"- Orphan runs: `{overview.get('orphan_run_count', 0)}`",
        "",
        "## Alerts",
        "",
    ]
    for title, key in (
        ("Failed Waves", "failed_waves"),
        ("Pending Waves", "pending_waves"),
        ("Dry-Run Only Waves", "planned_only_waves"),
        ("Orphan Runs", "orphan_runs"),
    ):
        lines.append(f"### {title}")
        items = list((report.get("alerts") or {}).get(key) or [])
        if not items:
            lines.append("- none")
        else:
            for item in items:
                if key == "orphan_runs":
                    lines.append(
                        f"- run `{item.get('label') or 'unknown'}` wave `{item.get('plan_wave_id') or 'none'}` "
                        f"mode `{item.get('mode') or 'unknown'}`"
                    )
                else:
                    latest = dict(item.get("latest_run") or {})
                    lines.append(
                        f"- `{item.get('wave_id')}` status `{item.get('execution_status') or 'unknown'}` "
                        f"latest `{latest.get('label') or 'none'}`"
                    )
        lines.append("")

    lines.append("## Recent Plan History")
    lines.append("")
    recent_history = list(report.get("recent_history") or [])
    if not recent_history:
        lines.append("- none")
    else:
        for plan in reversed(recent_history):
            lines.append(
                f"- `{plan.get('label')}` waves `{plan.get('wave_count', 0)}` "
                f"succeeded `{plan.get('succeeded_waves', 0)}` failed `{plan.get('failed_waves', 0)}` "
                f"pending `{plan.get('pending_waves', 0)}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_plan_dashboard_markdown"]
