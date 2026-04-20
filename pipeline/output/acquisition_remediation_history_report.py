from __future__ import annotations

from typing import Any


def render_acquisition_remediation_history_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Remediation History",
        "",
        f"- History directory: `{report.get('history_dir')}`",
        f"- Saved runs: `{report.get('run_count', 0)}`",
        "",
    ]
    for run in reversed(list(report.get("runs") or [])):
        lines.append(f"## `{run['label']}`")
        lines.append("")
        lines.append(f"- Report: `{run['path']}`")
        lines.append(f"- Generated at: `{run.get('generated_at') or 'none'}`")
        lines.append(f"- Mode: `{run.get('mode') or 'unknown'}`")
        lines.append(f"- Source: `{run.get('source_kind') or 'unknown'}`")
        lines.append(
            f"- Counts: requested `{run.get('requested_count', 0)}`, selected `{run.get('selected_count', 0)}`, "
            f"skipped `{run.get('skipped_count', 0)}`, succeeded `{run.get('succeeded_count', 0)}`, "
            f"failed `{run.get('failed_count', 0)}`"
        )
        lines.append(
            f"- Deltas vs previous: requested `{run.get('requested_delta_vs_previous', 0)}`, "
            f"selected `{run.get('selected_delta_vs_previous', 0)}`, skipped `{run.get('skipped_delta_vs_previous', 0)}`, "
            f"succeeded `{run.get('succeeded_delta_vs_previous', 0)}`, failed `{run.get('failed_delta_vs_previous', 0)}`"
        )
        priorities = list(run.get("selected_priorities") or [])
        lines.append(f"- Priorities: {', '.join(f'`{item}`' for item in priorities) if priorities else 'none'}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_history_markdown"]
