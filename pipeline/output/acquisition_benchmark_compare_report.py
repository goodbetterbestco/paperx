from __future__ import annotations

from typing import Any


def render_acquisition_benchmark_comparison_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Benchmark Comparison",
        "",
        f"- Base report: `{report.get('base_report_path')}`",
        f"- Candidate report: `{report.get('candidate_report_path')}`",
        f"- Base paper count: `{report.get('base_paper_count', 0)}`",
        f"- Candidate paper count: `{report.get('candidate_paper_count', 0)}`",
        "",
        "## Aggregate Deltas",
        "",
    ]
    for item in list(report.get("aggregate") or []):
        lines.append(
            f"- `{item['provider']}`: overall delta `{item['overall_delta']}`, "
            f"content delta `{item['content_delta']}`, execution delta `{item['execution_delta']}`"
        )

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
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_comparison_markdown"]
