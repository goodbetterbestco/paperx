from __future__ import annotations

from typing import Any


def _render_status_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    ranked = sorted(counts.items(), key=lambda item: (-int(item[1]), item[0]))
    return ", ".join(f"`{name}`={count}" for name, count in ranked)


def render_acquisition_remediation_status_markdown(report: dict[str, Any]) -> str:
    latest = dict(report.get("latest_run") or {})
    source = dict(latest.get("source") or {})
    plan = dict(latest.get("plan") or {})
    resume = latest.get("resume")
    lines = [
        "# Acquisition Remediation Status",
        "",
        f"- Output directory: `{report.get('output_dir')}`",
        f"- Latest label: `{latest.get('label') or 'none'}`",
        f"- Generated at: `{latest.get('generated_at') or 'none'}`",
        f"- Mode: `{latest.get('mode') or 'unknown'}`",
        f"- Source: `{source.get('kind') or 'unknown'}`",
        f"- Plan label: `{plan.get('label') or 'none'}`",
        f"- Plan wave: `{plan.get('wave_id') or 'none'}`",
        f"- Requested papers: `{latest.get('requested_count', 0)}`",
        f"- Selected papers: `{latest.get('selected_count', 0)}`",
        f"- Skipped papers: `{latest.get('skipped_count', 0)}`",
        f"- Priorities: {', '.join(f'`{item}`' for item in list(latest.get('selected_priorities') or [])) or 'none'}",
        f"- Status counts: {_render_status_counts(dict(latest.get('status_counts') or {}))}",
        f"- Current summary: `{dict(latest.get('report_paths') or {}).get('json') or 'not available'}`",
        f"- Snapshot summary: `{dict(latest.get('report_paths') or {}).get('snapshot_json') or 'not available'}`",
    ]
    if resume:
        lines.append(f"- Resumed from: `{dict(resume).get('path') or dict(resume).get('requested') or 'unknown'}`")

    lines.extend(["", "## Failures", ""])
    failures = list(report.get("failures") or [])
    if not failures:
        lines.append("- none")
    else:
        for item in failures:
            lines.append(
                f"- `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}` "
                f"score `{item.get('priority_score', 0)}` returncode `{item.get('returncode', 0)}`"
            )

    lines.extend(["", "## Skipped Successes", ""])
    skipped = list(report.get("skipped_papers") or [])
    if not skipped:
        lines.append("- none")
    else:
        for item in skipped:
            lines.append(
                f"- `{item.get('paper_id')}` priority `{item.get('priority') or 'unknown'}` "
                f"score `{item.get('priority_score', 0)}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_status_markdown"]
