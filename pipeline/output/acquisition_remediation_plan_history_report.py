from __future__ import annotations

from typing import Any


def render_acquisition_remediation_plan_history_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Remediation Plan History",
        "",
        f"- History directory: `{report.get('history_dir')}`",
        f"- Saved plans: `{report.get('plan_count', 0)}`",
        "",
    ]
    for plan in reversed(list(report.get("plans") or [])):
        lines.append(f"## `{plan.get('label')}`")
        lines.append("")
        lines.append(f"- Report: `{plan.get('path') or 'none'}`")
        lines.append(f"- Generated at: `{plan.get('generated_at') or 'none'}`")
        lines.append(f"- Source: `{plan.get('source_kind') or 'unknown'}`")
        lines.append(f"- Queue items: `{plan.get('queue_count', 0)}` | waves `{plan.get('wave_count', 0)}`")
        lines.append(
            f"- Execution: pending `{plan.get('pending_waves', 0)}`, dry-run only `{plan.get('planned_only_waves', 0)}`, "
            f"succeeded `{plan.get('succeeded_waves', 0)}`, failed `{plan.get('failed_waves', 0)}`"
        )
        lines.append(
            f"- Attempts: execute `{plan.get('execute_attempts', 0)}`, dry-run `{plan.get('dry_run_attempts', 0)}`, "
            f"orphan runs `{plan.get('orphan_run_count', 0)}`"
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_plan_history_markdown"]
