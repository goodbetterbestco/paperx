from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_deltas import append_named_provider_delta_lines, append_named_score_delta_lines
from pipeline.output.acquisition_benchmark_leaders import append_leader_lines


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
    append_leader_lines(lines, leaders)

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
        append_named_provider_delta_lines(lines, improvements, label="improvement")
    if not regressions:
        lines.append("- regressions: none")
    else:
        append_named_provider_delta_lines(lines, regressions, label="regression")

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
        append_named_score_delta_lines(lines, improvements, label="improvement")
        append_named_score_delta_lines(lines, regressions, label="regression")
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
        append_named_provider_delta_lines(lines, family_improvements, label="improvement")
        append_named_provider_delta_lines(lines, family_regressions, label="regression")
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
            append_named_score_delta_lines(lines, capability_improvements, label="improvement")
            append_named_score_delta_lines(lines, capability_regressions, label="regression")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_status_markdown"]
