from __future__ import annotations

from typing import Any


def render_acquisition_benchmark_status_markdown(report: dict[str, Any]) -> str:
    latest = report.get("latest_run") or {}
    leaders = report.get("leaders") or {}
    trend = report.get("trend") or {}
    lines = [
        "# Acquisition Benchmark Status",
        "",
        f"- History directory: `{report.get('history_dir')}`",
        f"- Latest label: `{latest.get('label') or 'none'}`",
        f"- Latest report: `{latest.get('path') or 'not available'}`",
        f"- Papers benchmarked: `{latest.get('paper_count', 0)}`",
        "",
        "## Current Leaders",
        "",
    ]

    overall_leader = leaders.get("overall") or {}
    content_leader = leaders.get("content") or {}
    execution_leader = leaders.get("execution") or {}
    if overall_leader:
        lines.append(f"- overall: `{overall_leader['provider']}` at `{overall_leader['overall']}`")
    if content_leader:
        lines.append(f"- content: `{content_leader['provider']}` at `{content_leader['content']}`")
    if execution_leader:
        lines.append(f"- execution: `{execution_leader['provider']}` at `{execution_leader['execution']}`")
    for capability in list(leaders.get("capabilities") or []):
        leader = capability.get("leader") or {}
        if leader:
            lines.append(f"- `{capability['capability']}`: `{leader['provider']}` at `{leader['score']}`")
    for family in list(leaders.get("families") or []):
        family_leaders = family.get("leaders") or {}
        overall_family_leader = family_leaders.get("overall") or {}
        if overall_family_leader:
            lines.append(
                f"- family `{family['family']}` overall leader: "
                f"`{overall_family_leader['provider']}` "
                f"at `{overall_family_leader.get('avg_overall_score', overall_family_leader.get('overall'))}`"
            )
        for capability in list(family_leaders.get("capabilities") or []):
            leader = capability.get("leader") or {}
            if leader:
                lines.append(
                    f"- family `{family['family']}` capability `{capability['capability']}` leader: "
                    f"`{leader['provider']}` at `{leader.get('avg_score', leader.get('score'))}`"
                )

    lines.extend([
        "",
        "## Latest Aggregate Scores",
        "",
    ])

    for provider in list(latest.get("providers") or []):
        lines.append(
            f"- `{provider['provider']}`: overall `{provider['overall']}` "
            f"(delta vs previous `{provider['overall_delta_vs_previous']}`), "
            f"content `{provider['content']}`, execution `{provider['execution']}`"
        )

    lines.extend(["", "## Latest Capability Scores", ""])
    for capability in list(latest.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        for provider in list(capability.get("providers") or []):
            lines.append(
                f"- `{provider['provider']}`: score `{provider['score']}` "
                f"(delta vs previous `{provider['score_delta_vs_previous']}`)"
            )
        lines.append("")

    lines.extend(["", "## Trend Watchlist", ""])

    improvements = list(trend.get("top_improvements") or [])
    regressions = list(trend.get("top_regressions") or [])
    if not improvements:
        lines.append("- improvements: none")
    else:
        for row in improvements:
            lines.append(
                f"- improvement `{row['provider']}`: overall delta `{row['overall_delta']}`, "
                f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
            )
    if not regressions:
        lines.append("- regressions: none")
    else:
        for row in regressions:
            lines.append(
                f"- regression `{row['provider']}`: overall delta `{row['overall_delta']}`, "
                f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
            )

    lines.extend(["", "## Capability Watchlist", ""])
    for capability in list(trend.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        improvements = list(capability.get("improvements") or [])
        regressions = list(capability.get("regressions") or [])
        if not improvements and not regressions:
            lines.append("- no capability movement")
            lines.append("")
            continue
        for row in improvements:
            lines.append(f"- improvement `{row['provider']}`: score delta `{row['score_delta']}`")
        for row in regressions:
            lines.append(f"- regression `{row['provider']}`: score delta `{row['score_delta']}`")
        lines.append("")

    lines.extend(["", "## Family Watchlist", ""])
    for family in list(trend.get("families") or []):
        lines.append(f"### `{family['family']}`")
        lines.append("")
        family_improvements = list(family.get("improvements") or [])
        family_regressions = list(family.get("regressions") or [])
        if not family_improvements and not family_regressions:
            lines.append("- no provider movement")
            lines.append("")
            continue
        for row in family_improvements:
            lines.append(
                f"- improvement `{row['provider']}`: overall delta `{row['overall_delta']}`, "
                f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
            )
        for row in family_regressions:
            lines.append(
                f"- regression `{row['provider']}`: overall delta `{row['overall_delta']}`, "
                f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
            )
        lines.append("")
        for capability in list(family.get("capabilities") or []):
            lines.append(f"#### `{capability['capability']}`")
            lines.append("")
            capability_improvements = list(capability.get("improvements") or [])
            capability_regressions = list(capability.get("regressions") or [])
            if not capability_improvements and not capability_regressions:
                lines.append("- no capability movement")
                lines.append("")
                continue
            for row in capability_improvements:
                lines.append(f"- improvement `{row['provider']}`: score delta `{row['score_delta']}`")
            for row in capability_regressions:
                lines.append(f"- regression `{row['provider']}`: score delta `{row['score_delta']}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_status_markdown"]
