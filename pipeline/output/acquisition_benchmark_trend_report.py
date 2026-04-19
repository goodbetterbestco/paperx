from __future__ import annotations

from typing import Any


def _render_changes(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [title, ""]
    if not rows:
        lines.append("- none")
        lines.append("")
        return lines
    for row in rows:
        lines.append(
            f"- `{row['provider']}`: overall delta `{row['overall_delta']}`, "
            f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
        )
    lines.append("")
    return lines


def render_acquisition_benchmark_trend_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Benchmark Trend",
        "",
        f"- Base report: `{report.get('base_report_path')}`",
        f"- Candidate report: `{report.get('candidate_report_path')}`",
        f"- Base paper count: `{report.get('base_paper_count', 0)}`",
        f"- Candidate paper count: `{report.get('candidate_paper_count', 0)}`",
        "",
    ]
    lines.extend(_render_changes("## Top Improvements", list(report.get("top_improvements") or [])))
    lines.extend(_render_changes("## Top Regressions", list(report.get("top_regressions") or [])))
    lines.append("## Family Watchlist")
    lines.append("")
    for family in list(report.get("families") or []):
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
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_trend_markdown"]
