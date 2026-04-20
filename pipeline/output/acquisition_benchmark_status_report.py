from __future__ import annotations

from typing import Any


def render_acquisition_benchmark_status_markdown(report: dict[str, Any]) -> str:
    latest = report.get("latest_run") or {}
    trend = report.get("trend") or {}
    lines = [
        "# Acquisition Benchmark Status",
        "",
        f"- History directory: `{report.get('history_dir')}`",
        f"- Latest label: `{latest.get('label') or 'none'}`",
        f"- Latest report: `{latest.get('path') or 'not available'}`",
        f"- Papers benchmarked: `{latest.get('paper_count', 0)}`",
        "",
        "## Latest Aggregate Scores",
        "",
    ]

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
