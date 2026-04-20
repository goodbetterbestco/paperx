from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_deltas import append_provider_delta_lines
from pipeline.output.acquisition_benchmark_leaders import append_leader_lines


def _append_score_regression_lines(lines: list[str], rows: list[dict[str, Any]]) -> None:
    for row in rows:
        lines.append(
            f"- capability `{row['capability']}` regression `{row['provider']}`: "
            f"score delta `{row['score_delta']}`"
        )


def _append_family_regression_lines(lines: list[str], rows: list[dict[str, Any]]) -> None:
    for row in rows:
        lines.append(
            f"- family `{row['family']}` regression `{row['provider']}`: "
            f"overall delta `{row['overall_delta']}`, content delta `{row['content_delta']}`, "
            f"execution delta `{row['execution_delta']}`"
        )


def render_acquisition_benchmark_dashboard_markdown(report: dict[str, Any]) -> str:
    overview = report.get("overview") or {}
    latest = report.get("latest_run") or {}
    previous = report.get("previous_run") or {}
    comparison = report.get("comparison") or {}
    alerts = report.get("alerts") or {}
    lines = [
        "# Acquisition Benchmark Dashboard",
        "",
        f"- History directory: `{overview.get('history_dir')}`",
        f"- Saved runs: `{overview.get('run_count', 0)}`",
        f"- Latest run: `{overview.get('latest_label') or 'none'}`",
        f"- Previous run: `{overview.get('previous_label') or 'none'}`",
        f"- Latest papers benchmarked: `{overview.get('latest_paper_count', 0)}`",
        f"- Latest providers scored: `{overview.get('latest_provider_count', 0)}`",
        f"- Comparison available: `{str(bool(overview.get('comparison_available'))).lower()}`",
        "",
        "## Current Leaders",
        "",
    ]
    append_leader_lines(lines, report.get("leaders") or {})

    lines.extend(["", "## Latest Aggregate Scores", ""])
    for provider in list(latest.get("providers") or []):
        lines.append(
            f"- `{provider['provider']}`: overall `{provider['overall']}` "
            f"(delta vs previous `{provider['overall_delta_vs_previous']}`), "
            f"content `{provider['content']}`, execution `{provider['execution']}`"
        )

    lines.extend(["", "## Regression Watch", ""])
    provider_regressions = list(alerts.get("provider_regressions") or [])
    capability_regressions = list(alerts.get("capability_regressions") or [])
    family_regressions = list(alerts.get("family_regressions") or [])
    if not provider_regressions and not capability_regressions and not family_regressions:
        lines.append("- none")
    else:
        append_provider_delta_lines(lines, provider_regressions)
        _append_score_regression_lines(lines, capability_regressions)
        _append_family_regression_lines(lines, family_regressions)

    lines.extend(["", "## Latest vs Previous", ""])
    if not comparison:
        lines.append("- Not enough history for a latest-vs-previous comparison yet.")
    else:
        lines.append(f"- Base report: `{comparison.get('base_report_path')}`")
        lines.append(f"- Candidate report: `{comparison.get('candidate_report_path')}`")
        lines.append("")
        for row in list(comparison.get("aggregate") or []):
            lines.append(
                f"- `{row['provider']}`: base `{row['base_overall']}`, candidate `{row['candidate_overall']}`, "
                f"overall delta `{row['overall_delta']}`"
            )

    lines.extend(["", "## Recent Runs", ""])
    for run in reversed(list(report.get("recent_history") or [])):
        leaders = run.get("leaders") or {}
        overall = leaders.get("overall") or {}
        lines.append(
            f"- `{run['label']}`: papers `{run['paper_count']}`, providers `{run['provider_count']}`, "
            f"overall leader `{overall.get('provider', 'none')}`"
        )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_dashboard_markdown"]
