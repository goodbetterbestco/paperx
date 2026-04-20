from __future__ import annotations

from typing import Any


def _append_family_leaders(lines: list[str], families: list[dict[str, Any]], *, score_key: str) -> None:
    for family in families:
        family_name = family.get("family")
        leaders = family.get("leaders") or {}
        overall = leaders.get("overall") or {}
        if overall:
            lines.append(
                f"- family `{family_name}` overall leader: `{overall['provider']}` "
                f"at `{overall.get('avg_overall_score', overall.get('overall'))}`"
            )
        for capability in list(leaders.get("capabilities") or []):
            leader = capability.get("leader") or {}
            if leader:
                lines.append(
                    f"- family `{family_name}` capability `{capability['capability']}` leader: "
                    f"`{leader['provider']}` at `{leader.get(score_key, leader.get('score'))}`"
                )


def render_acquisition_benchmark_markdown(report: dict[str, Any]) -> str:
    leaders = report.get("leaders") or {}
    lines = [
        "# Acquisition Benchmark",
        "",
        f"- Manifest: `{report.get('manifest_path')}`",
        f"- Papers benchmarked: `{report.get('paper_count', 0)}`",
        f"- Snapshot label: `{report.get('snapshot_label') or 'not set'}`",
        f"- JSON report: `{((report.get('report_paths') or {}).get('json')) or 'not written'}`",
        f"- Markdown report: `{((report.get('report_paths') or {}).get('markdown')) or 'not written'}`",
        f"- Snapshot JSON report: `{((report.get('report_paths') or {}).get('snapshot_json')) or 'not written'}`",
        f"- Snapshot Markdown report: `{((report.get('report_paths') or {}).get('snapshot_markdown')) or 'not written'}`",
        "",
        "## Current Leaders",
        "",
    ]
    overall = leaders.get("overall") or {}
    content = leaders.get("content") or {}
    execution = leaders.get("execution") or {}
    if overall:
        lines.append(f"- overall: `{overall['provider']}` at `{overall['avg_overall_score']}`")
    if content:
        lines.append(f"- content: `{content['provider']}` at `{content['avg_content_score']}`")
    if execution:
        lines.append(f"- execution: `{execution['provider']}` at `{execution['avg_execution_score']}`")
    for capability in list(leaders.get("capabilities") or []):
        leader = capability.get("leader") or {}
        if leader:
            lines.append(f"- `{capability['capability']}`: `{leader['provider']}` at `{leader['avg_score']}`")
    _append_family_leaders(lines, list(leaders.get("families") or []), score_key="avg_score")

    lines.extend([
        "",
        "## Aggregate Ranking",
        "",
    ])

    for index, provider in enumerate(list(report.get("aggregate") or []), start=1):
        lines.append(
            f"{index}. `{provider['provider']}` — overall `{provider['avg_overall_score']}`, "
            f"content `{provider['avg_content_score']}`, execution `{provider['avg_execution_score']}`"
        )

    lines.extend(["", "## Capability Ranking", ""])
    for capability in list(report.get("capabilities") or []):
        lines.append(f"### `{capability['capability']}`")
        lines.append("")
        for provider in list(capability.get("providers") or []):
            lines.append(f"- `{provider['provider']}`: score `{provider['avg_score']}`")
        lines.append("")

    lines.extend(
        [
            "",
            "## Family Breakdown",
            "",
        ]
    )
    for family in list(report.get("families") or []):
        lines.append(f"### `{family['family']}`")
        lines.append("")
        for provider in list(family.get("providers") or []):
            lines.append(
                f"- `{provider['provider']}`: overall `{provider['avg_overall_score']}`, "
                f"content `{provider['avg_content_score']}`, execution `{provider['avg_execution_score']}`"
            )
        lines.append("")

    lines.append("## Family Capability Breakdown")
    lines.append("")
    for family in list(report.get("family_capabilities") or []):
        lines.append(f"### `{family['family']}`")
        lines.append("")
        for capability in list(family.get("capabilities") or []):
            lines.append(f"#### `{capability['capability']}`")
            lines.append("")
            for provider in list(capability.get("providers") or []):
                lines.append(f"- `{provider['provider']}`: score `{provider['avg_score']}`")
            lines.append("")
        lines.append("")

    lines.append("## Per-Paper Results")
    lines.append("")
    for paper in list(report.get("papers") or []):
        lines.append(
            f"- `{paper['paper_id']}` ({paper.get('family') or 'unclassified'}) — "
            f"route `{paper.get('expected_route') or 'n/a'}`, "
            f"layout target `{paper.get('expected_primary_layout_provider') or 'n/a'}`, "
            f"math target `{paper.get('expected_primary_math_provider') or 'n/a'}`, "
            f"metadata target `{paper.get('expected_primary_metadata_provider') or 'n/a'}`, "
            f"reference target `{paper.get('expected_primary_reference_provider') or 'n/a'}`"
        )
        for provider in list(paper.get("providers") or []):
            lines.append(
                f"  - `{provider['provider']}`: overall `{provider['overall_score']}`, "
                f"content `{provider['content_score']}`, execution `{provider.get('execution_score')}`"
            )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_benchmark_markdown"]
