from __future__ import annotations

from typing import Any


def _render_counts(counts: dict[str, int]) -> str:
    ranked = sorted(counts.items(), key=lambda item: (-int(item[1]), item[0]))
    return ", ".join(f"`{name}`={count}" for name, count in ranked) if ranked else "none"


def render_acquisition_remediation_plan_status_markdown(report: dict[str, Any]) -> str:
    plan = dict(report.get("plan") or {})
    overview = dict(report.get("overview") or {})
    lines = [
        "# Acquisition Remediation Plan Status",
        "",
        f"- Plan label: `{plan.get('label') or 'none'}`",
        f"- Plan path: `{plan.get('path') or 'none'}`",
        f"- Generated at: `{plan.get('generated_at') or 'none'}`",
        f"- Source: `{dict(plan.get('source') or {}).get('kind') or 'unknown'}`",
        f"- Queue items: `{plan.get('queue_count', 0)}`",
        f"- Planned waves: `{overview.get('planned_waves', 0)}`",
        f"- Wave status counts: {_render_counts(dict(overview.get('wave_status_counts') or {}))}",
        f"- Execute attempts: `{overview.get('execute_attempts', 0)}`",
        f"- Dry-run attempts: `{overview.get('dry_run_attempts', 0)}`",
        f"- Orphan runs: `{overview.get('orphan_run_count', 0)}`",
        "",
        "## Failed Waves",
        "",
    ]
    failed_waves = list(report.get("failed_waves") or [])
    if not failed_waves:
        lines.append("- none")
    else:
        for wave in failed_waves:
            latest = dict(wave.get("latest_run") or {})
            lines.append(
                f"- `{wave.get('wave_id')}` papers `{wave.get('paper_count', 0)}` latest `{latest.get('label') or 'none'}` "
                f"failed `{latest.get('failed_count', 0)}`"
            )

    lines.extend(["", "## Pending Waves", ""])
    pending_waves = list(report.get("pending_waves") or [])
    if not pending_waves:
        lines.append("- none")
    else:
        for wave in pending_waves:
            lines.append(
                f"- `{wave.get('wave_id')}` kind `{wave.get('wave_kind') or 'unknown'}` "
                f"provider `{wave.get('provider_focus') or 'unknown'}` papers `{wave.get('paper_count', 0)}`"
            )

    lines.extend(["", "## Dry-Run Only Waves", ""])
    planned_only_waves = list(report.get("planned_only_waves") or [])
    if not planned_only_waves:
        lines.append("- none")
    else:
        for wave in planned_only_waves:
            latest = dict(wave.get("latest_run") or {})
            lines.append(
                f"- `{wave.get('wave_id')}` latest dry-run `{latest.get('label') or 'none'}` "
                f"attempts `{wave.get('attempt_count', 0)}`"
            )

    lines.extend(["", "## Orphan Runs", ""])
    orphan_runs = list(report.get("orphan_runs") or [])
    if not orphan_runs:
        lines.append("- none")
    else:
        for run in orphan_runs:
            lines.append(
                f"- run `{run.get('label') or 'unknown'}` references wave `{run.get('plan_wave_id') or 'none'}` "
                f"mode `{run.get('mode') or 'unknown'}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_plan_status_markdown"]
