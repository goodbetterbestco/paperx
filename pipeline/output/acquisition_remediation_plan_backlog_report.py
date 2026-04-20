from __future__ import annotations

from typing import Any


def render_acquisition_remediation_plan_backlog_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Remediation Plan Backlog",
        "",
        f"- Plan label: `{report.get('plan_label') or 'none'}`",
        f"- Mode: `{report.get('mode') or 'unknown'}`",
        f"- Selected statuses: {', '.join(f'`{status}`' for status in list(report.get('selected_statuses') or [])) or 'none'}",
        f"- Selected waves: `{report.get('selected_count', 0)}`",
        "",
        "## Waves",
        "",
    ]
    waves = list(report.get("waves") or [])
    if not waves:
        lines.append("- none")
    else:
        for wave in waves:
            lines.append(
                f"- `{wave.get('wave_id')}` status `{wave.get('execution_status') or 'unknown'}` "
                f"command `{wave.get('command') or 'none'}`"
            )

    lines.extend(["", "## Results", ""])
    results = list(report.get("results") or [])
    if not results:
        lines.append("- none")
    else:
        for result in results:
            lines.append(
                f"- `{result.get('wave_id')}` status `{result.get('status') or 'unknown'}` "
                f"queue label `{result.get('queue_label') or 'none'}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_plan_backlog_markdown"]
