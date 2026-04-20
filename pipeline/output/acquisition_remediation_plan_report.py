from __future__ import annotations

from typing import Any


def render_acquisition_remediation_plan_markdown(report: dict[str, Any]) -> str:
    source = dict(report.get("source") or {})
    context = dict(report.get("context") or {})
    lines = [
        "# Acquisition Remediation Plan",
        "",
        f"- Source: `{source.get('kind') or 'unknown'}`",
        f"- Source path: `{source.get('path') or 'none'}`",
        f"- History directory: `{report.get('history_dir') or 'none'}`",
        f"- Queue items planned: `{report.get('queue_count', 0)}`",
        f"- Waves planned: `{report.get('wave_count', 0)}`",
        f"- Max wave size: `{report.get('max_wave_size', 0)}`",
        f"- Wave kinds: {', '.join(f'`{key}`={value}' for key, value in sorted(dict(report.get('wave_kind_counts') or {}).items())) or 'none'}",
        f"- Provider focus: {', '.join(f'`{key}`={value}' for key, value in sorted(dict(report.get('provider_focus_counts') or {}).items())) or 'none'}",
        "",
        "## Recovery Context",
        "",
        f"- Latest failures: {', '.join(f'`{item}`' for item in list(context.get('latest_failures') or [])) or 'none'}",
        f"- Still failing: {', '.join(f'`{item}`' for item in list(context.get('still_failing') or [])) or 'none'}",
        f"- Introduced failures: {', '.join(f'`{item}`' for item in list(context.get('introduced_failures') or [])) or 'none'}",
        "",
    ]

    for wave in list(report.get("waves") or []):
        lines.append(f"## `{wave['wave_id']}`")
        lines.append("")
        lines.append(
            f"- Kind: `{wave.get('wave_kind')}` | priority `{wave.get('priority_label')}` | provider focus `{wave.get('provider_focus')}` | papers `{wave.get('paper_count', 0)}`"
        )
        lines.append(
            f"- Tags: {', '.join(f'`{item}`' for item in list(wave.get('planning_tags') or [])) if list(wave.get('planning_tags') or []) else 'none'}"
        )
        lines.append(
            f"- Target providers: {', '.join(f'`{item}`' for item in list(wave.get('target_providers') or [])) if list(wave.get('target_providers') or []) else 'none'}"
        )
        lines.append(f"- Fail-fast recommended: `{str(bool(wave.get('fail_fast_recommended'))).lower()}`")
        lines.append(f"- Command: `{wave.get('execution_command')}`")
        lines.append("")
        for paper in list(wave.get("papers") or []):
            lines.append(
                f"- `{paper.get('paper_id')}` priority `{paper.get('priority_label')}` score `{paper.get('priority_score', 0)}` "
                f"provider `{paper.get('provider_focus')}`"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_remediation_plan_markdown"]
