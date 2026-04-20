from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_leaders import append_leader_lines, metric_leader_summary_parts

def _render_run_leaders(run: dict[str, Any]) -> list[str]:
    leaders = run.get("leaders") or {}
    summary_parts = metric_leader_summary_parts(leaders)
    lines: list[str] = []
    if summary_parts:
        lines.append(f"- Leaders: {', '.join(summary_parts)}")
    append_leader_lines(lines, {"capabilities": leaders.get("capabilities"), "families": leaders.get("families")}, family_label="Family")
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
