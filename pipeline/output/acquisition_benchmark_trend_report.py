from __future__ import annotations

from typing import Any


def _render_leader_shift(report: dict[str, Any]) -> list[str]:
    leaders = report.get("leaders") or {}
    base = leaders.get("base") or {}
    candidate = leaders.get("candidate") or {}
    lines = ["## Leader Shift", ""]

    for label, value_key in (("overall", "overall"), ("content", "content"), ("execution", "execution")):
        base_row = base.get(label) or {}
        candidate_row = candidate.get(label) or {}
        if not base_row and not candidate_row:
            continue
        lines.append(
            f"- {label}: "
            f"`{base_row.get('provider', 'none')}` `{base_row.get(f'avg_{value_key}_score', base_row.get(value_key, 'n/a'))}`"
            f" -> `{candidate_row.get('provider', 'none')}` "
            f"`{candidate_row.get(f'avg_{value_key}_score', candidate_row.get(value_key, 'n/a'))}`"
        )

    base_capabilities = {
        str(item.get("capability", "") or ""): item.get("leader") or {}
        for item in list(base.get("capabilities") or [])
        if str(item.get("capability", "") or "").strip()
    }
    candidate_capabilities = {
        str(item.get("capability", "") or ""): item.get("leader") or {}
        for item in list(candidate.get("capabilities") or [])
        if str(item.get("capability", "") or "").strip()
    }
    for capability in sorted(set(base_capabilities) | set(candidate_capabilities)):
        base_row = base_capabilities.get(capability, {})
        candidate_row = candidate_capabilities.get(capability, {})
        lines.append(
            f"- `{capability}`: "
            f"`{base_row.get('provider', 'none')}` `{base_row.get('avg_score', base_row.get('score', 'n/a'))}`"
            f" -> `{candidate_row.get('provider', 'none')}` "
            f"`{candidate_row.get('avg_score', candidate_row.get('score', 'n/a'))}`"
        )

    lines.append("")
    return lines


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


def _render_score_changes(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [title, ""]
    if not rows:
        lines.append("- none")
        lines.append("")
        return lines
    for row in rows:
        lines.append(f"- `{row['provider']}`: score delta `{row['score_delta']}`")
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
    lines.extend(_render_leader_shift(report))
    lines.extend(_render_changes("## Top Improvements", list(report.get("top_improvements") or [])))
    lines.extend(_render_changes("## Top Regressions", list(report.get("top_regressions") or [])))
    lines.append("## Capability Watchlist")
    lines.append("")
    for capability in list(report.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        lines.extend(_render_score_changes("#### Improvements", list(capability.get("improvements") or [])))
        lines.extend(_render_score_changes("#### Regressions", list(capability.get("regressions") or [])))
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


__all__ = ["render_acquisition_benchmark_trend_markdown"]
