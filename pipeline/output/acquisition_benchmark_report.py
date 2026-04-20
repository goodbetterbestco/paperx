from __future__ import annotations

from typing import Any

from pipeline.output.acquisition_benchmark_leaders import append_leader_lines


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
        f"- Status JSON report: `{((report.get('report_paths') or {}).get('status_json')) or 'not written'}`",
        f"- Status Markdown report: `{((report.get('report_paths') or {}).get('status_markdown')) or 'not written'}`",
        f"- Snapshot JSON report: `{((report.get('report_paths') or {}).get('snapshot_json')) or 'not written'}`",
        f"- Snapshot Markdown report: `{((report.get('report_paths') or {}).get('snapshot_markdown')) or 'not written'}`",
        f"- Dashboard JSON report: `{((report.get('report_paths') or {}).get('dashboard_json')) or 'not written'}`",
        f"- Dashboard Markdown report: `{((report.get('report_paths') or {}).get('dashboard_markdown')) or 'not written'}`",
        "",
        "## Current Leaders",
        "",
    ]
    append_leader_lines(lines, leaders)

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
        route_reason_codes = ", ".join(f"`{item}`" for item in list(paper.get("expected_route_reason_codes") or [])) or "`n/a`"
        ocr_policy = paper.get("expected_ocr_policy") or "n/a"
        lines.append(
            f"- `{paper['paper_id']}` "
            f"[section `{paper.get('section') or 'unsectioned'}`] "
            f"({paper.get('family') or 'unclassified'}) — "
            f"route `{paper.get('expected_route') or 'n/a'}`, "
            f"route reasons {route_reason_codes}, "
            f"OCR policy `{ocr_policy}`, "
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
