from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_deltas import append_provider_delta_lines, append_score_delta_lines
from pipeline.output.acquisition_benchmark_leaders import render_labeled_leader_snapshot


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
    lines.extend(render_labeled_leader_snapshot("Base", leaders.get("base") or {}))
    lines.extend(render_labeled_leader_snapshot("Candidate", leaders.get("candidate") or {}))
    lines.extend([
        "## Aggregate Deltas",
        "",
    ])
    append_provider_delta_lines(lines, list(report.get("aggregate") or []))

    lines.extend(["", "## Capability Deltas", ""])
    for capability in list(report.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        append_score_delta_lines(lines, list(capability.get("providers") or []))
        lines.append("")

    lines.extend(["", "## Family Deltas", ""])
    for family in list(report.get("families") or []):
        lines.append(f"### `{family['family']}`")
        lines.append("")
        append_provider_delta_lines(lines, list(family.get("providers") or []))
        lines.append("")
        for capability in list(family.get("capabilities") or []):
            lines.append(f"#### `{capability['capability']}`")
            lines.append("")
            append_score_delta_lines(lines, list(capability.get("providers") or []))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_comparison_markdown"]
