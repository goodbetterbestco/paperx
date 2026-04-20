from __future__ import annotations

from typing import Any


def _render_run_leaders(run: dict[str, Any]) -> list[str]:
    leaders = run.get("leaders") or {}
    overall = leaders.get("overall") or {}
    content = leaders.get("content") or {}
    execution = leaders.get("execution") or {}
    summary_parts: list[str] = []
    if overall:
        summary_parts.append(f"overall `{overall['provider']}` at `{overall['overall']}`")
    if content:
        summary_parts.append(f"content `{content['provider']}` at `{content['content']}`")
    if execution:
        summary_parts.append(f"execution `{execution['provider']}` at `{execution['execution']}`")

    lines: list[str] = []
    if summary_parts:
        lines.append(f"- Leaders: {', '.join(summary_parts)}")
    for capability in list(leaders.get("capabilities") or []):
        leader = capability.get("leader") or {}
        if leader:
            lines.append(f"- Capability `{capability['capability']}` leader: `{leader['provider']}` at `{leader['score']}`")
    for family in list(leaders.get("families") or []):
        family_leaders = family.get("leaders") or {}
        overall_leader = family_leaders.get("overall") or {}
        if overall_leader:
            lines.append(
                f"- Family `{family['family']}` overall leader: "
                f"`{overall_leader['provider']}` at `{overall_leader.get('avg_overall_score', overall_leader.get('overall'))}`"
            )
        for capability in list(family_leaders.get("capabilities") or []):
            leader = capability.get("leader") or {}
            if leader:
                lines.append(
                    f"- Family `{family['family']}` capability `{capability['capability']}` leader: "
                    f"`{leader['provider']}` at `{leader.get('avg_score', leader.get('score'))}`"
                )
    return lines


def render_acquisition_benchmark_history_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Benchmark History",
        "",
        f"- History directory: `{report.get('history_dir')}`",
        f"- Saved runs: `{report.get('run_count', 0)}`",
        "",
    ]

    for run in reversed(list(report.get("runs") or [])):
        lines.append(f"## `{run['label']}`")
        lines.append("")
        lines.append(f"- Report: `{run['path']}`")
        lines.append(f"- Papers benchmarked: `{run['paper_count']}`")
        lines.append(f"- Providers scored: `{run['provider_count']}`")
        lines.extend(_render_run_leaders(run))
        lines.append("")
        for provider in list(run.get("providers") or []):
            delta = provider.get("overall_delta_vs_previous", 0.0)
            lines.append(
                f"- `{provider['provider']}`: overall `{provider['overall']}` "
                f"(delta vs previous `{delta}`), content `{provider['content']}`, execution `{provider['execution']}`"
            )
        lines.append("")
        for capability in list(run.get("capabilities") or []):
            lines.append(f"### `{capability['capability']}`")
            lines.append("")
            for provider in list(capability.get("providers") or []):
                lines.append(
                    f"- `{provider['provider']}`: score `{provider['score']}` "
                    f"(delta vs previous `{provider['score_delta_vs_previous']}`)"
                )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_history_markdown"]
