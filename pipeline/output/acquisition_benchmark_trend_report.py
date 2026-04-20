from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_deltas import (
    append_named_provider_delta_lines,
    append_named_score_delta_lines,
    render_delta_section,
)
from pipeline.output.acquisition_benchmark_leaders import capability_leader_map, family_leader_map, leader_value


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
            f"`{base_row.get('provider', 'none')}` `{leader_value(base_row, f'avg_{value_key}_score', value_key)}`"
            f" -> `{candidate_row.get('provider', 'none')}` "
            f"`{leader_value(candidate_row, f'avg_{value_key}_score', value_key)}`"
        )

    base_capabilities = capability_leader_map(base)
    candidate_capabilities = capability_leader_map(candidate)
    for capability in sorted(set(base_capabilities) | set(candidate_capabilities)):
        base_row = base_capabilities.get(capability, {})
        candidate_row = candidate_capabilities.get(capability, {})
        lines.append(
            f"- `{capability}`: "
            f"`{base_row.get('provider', 'none')}` `{leader_value(base_row, 'avg_score', 'score')}`"
            f" -> `{candidate_row.get('provider', 'none')}` "
            f"`{leader_value(candidate_row, 'avg_score', 'score')}`"
        )

    lines.append("")
    return lines


def _render_family_leader_shift(report: dict[str, Any]) -> list[str]:
    leaders = report.get("leaders") or {}
    base = family_leader_map(leaders.get("base") or {})
    candidate = family_leader_map(leaders.get("candidate") or {})
    lines = ["## Family Leader Shift", ""]
    for family in sorted(set(base) | set(candidate)):
        base_leaders = base.get(family, {})
        candidate_leaders = candidate.get(family, {})
        base_overall = base_leaders.get("overall") or {}
        candidate_overall = candidate_leaders.get("overall") or {}
        lines.append(
            f"- family `{family}` overall: "
            f"`{base_overall.get('provider', 'none')}` "
            f"`{leader_value(base_overall, 'avg_overall_score', 'overall')}`"
            f" -> `{candidate_overall.get('provider', 'none')}` "
            f"`{leader_value(candidate_overall, 'avg_overall_score', 'overall')}`"
        )
        base_capabilities = capability_leader_map(base_leaders)
        candidate_capabilities = capability_leader_map(candidate_leaders)
        for capability in sorted(set(base_capabilities) | set(candidate_capabilities)):
            base_row = base_capabilities.get(capability, {})
            candidate_row = candidate_capabilities.get(capability, {})
            lines.append(
                f"- family `{family}` capability `{capability}`: "
                f"`{base_row.get('provider', 'none')}` `{leader_value(base_row, 'avg_score', 'score')}`"
                f" -> `{candidate_row.get('provider', 'none')}` "
                f"`{leader_value(candidate_row, 'avg_score', 'score')}`"
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
    lines.extend(_render_leader_shift(report))
    lines.extend(_render_family_leader_shift(report))
    lines.extend(render_delta_section("## Top Improvements", list(report.get("top_improvements") or [])))
    lines.extend(render_delta_section("## Top Regressions", list(report.get("top_regressions") or [])))
    lines.append("## Capability Watchlist")
    lines.append("")
    for capability in list(report.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        lines.extend(render_delta_section("#### Improvements", list(capability.get("improvements") or []), kind="score"))
        lines.extend(render_delta_section("#### Regressions", list(capability.get("regressions") or []), kind="score"))
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


__all__ = ["render_acquisition_benchmark_trend_markdown"]
