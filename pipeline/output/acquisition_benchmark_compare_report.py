from __future__ import annotations

from typing import Any


def _render_leader_snapshot(label: str, leaders: dict[str, Any]) -> list[str]:
    lines = [f"### {label}", ""]
    overall = leaders.get("overall") or {}
    content = leaders.get("content") or {}
    execution = leaders.get("execution") or {}
    if overall:
        lines.append(f"- overall: `{overall['provider']}` at `{overall.get('avg_overall_score', overall.get('overall'))}`")
    if content:
        lines.append(f"- content: `{content['provider']}` at `{content.get('avg_content_score', content.get('content'))}`")
    if execution:
        lines.append(
            f"- execution: `{execution['provider']}` at `{execution.get('avg_execution_score', execution.get('execution'))}`"
        )
    for capability in list(leaders.get("capabilities") or []):
        leader = capability.get("leader") or {}
        if leader:
            lines.append(
                f"- `{capability['capability']}`: `{leader['provider']}` at `{leader.get('avg_score', leader.get('score'))}`"
            )
    for family in list(leaders.get("families") or []):
        family_leaders = family.get("leaders") or {}
        overall_leader = family_leaders.get("overall") or {}
        if overall_leader:
            lines.append(
                f"- family `{family['family']}` overall leader: `{overall_leader['provider']}` "
                f"at `{overall_leader.get('avg_overall_score', overall_leader.get('overall'))}`"
            )
        for capability in list(family_leaders.get("capabilities") or []):
            leader = capability.get("leader") or {}
            if leader:
                lines.append(
                    f"- family `{family['family']}` capability `{capability['capability']}` leader: "
                    f"`{leader['provider']}` at `{leader.get('avg_score', leader.get('score'))}`"
                )
    lines.append("")
    return lines


def render_acquisition_benchmark_comparison_markdown(report: dict[str, Any]) -> str:
    leaders = report.get("leaders") or {}
    lines = [
        "# Acquisition Benchmark Comparison",
        "",
        f"- Base report: `{report.get('base_report_path')}`",
        f"- Candidate report: `{report.get('candidate_report_path')}`",
        f"- Base paper count: `{report.get('base_paper_count', 0)}`",
        f"- Candidate paper count: `{report.get('candidate_paper_count', 0)}`",
        "",
        "## Leader Snapshot",
        "",
    ]
    lines.extend(_render_leader_snapshot("Base", leaders.get("base") or {}))
    lines.extend(_render_leader_snapshot("Candidate", leaders.get("candidate") or {}))
    lines.extend([
        "## Aggregate Deltas",
        "",
    ])
    for item in list(report.get("aggregate") or []):
        lines.append(
            f"- `{item['provider']}`: overall delta `{item['overall_delta']}`, "
            f"content delta `{item['content_delta']}`, execution delta `{item['execution_delta']}`"
        )

    lines.extend(["", "## Capability Deltas", ""])
    for capability in list(report.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        for item in list(capability.get("providers") or []):
            lines.append(f"- `{item['provider']}`: score delta `{item['score_delta']}`")
        lines.append("")

    lines.extend(["", "## Family Deltas", ""])
    for family in list(report.get("families") or []):
        lines.append(f"### `{family['family']}`")
        lines.append("")
        for item in list(family.get("providers") or []):
            lines.append(
                f"- `{item['provider']}`: overall delta `{item['overall_delta']}`, "
                f"content delta `{item['content_delta']}`, execution delta `{item['execution_delta']}`"
            )
        lines.append("")
        for capability in list(family.get("capabilities") or []):
            lines.append(f"#### `{capability['capability']}`")
            lines.append("")
            for item in list(capability.get("providers") or []):
                lines.append(f"- `{item['provider']}`: score delta `{item['score_delta']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_comparison_markdown"]
