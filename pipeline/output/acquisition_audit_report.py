from __future__ import annotations

from typing import Any


def _render_top_counts(counts: dict[str, int], *, limit: int = 8) -> str:
    ranked = sorted(counts.items(), key=lambda item: (-int(item[1]), item[0]))[:limit]
    if not ranked:
        return "none"
    return ", ".join(f"`{name}`={count}" for name, count in ranked)


def render_acquisition_audit_markdown(report: dict[str, Any], *, top_n: int) -> str:
    ocr_summary = dict(report.get("ocr_summary") or {})
    lines = [
        "# Acquisition Quality Audit",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Papers audited: `{report['paper_count']}`",
        f"- Canonical outputs present: `{report['canonical_count']} / {report['paper_count']}`",
        f"- OCR should-run count: `{ocr_summary.get('should_run_count', 0)}`",
        f"- OCR applied count: `{ocr_summary.get('applied_count', 0)}`",
        f"- Required OCR not applied: `{ocr_summary.get('required_not_applied_count', 0)}`",
        f"- Recommended OCR not applied: `{ocr_summary.get('recommended_not_applied_count', 0)}`",
        f"- JSON report: `{report['report_paths']['json']}`",
        f"- Markdown report: `{report['report_paths']['markdown']}`",
        "",
        "## Route Distribution",
        "",
        f"- Routes: {_render_top_counts(report.get('route_counts', {}))}",
        f"- Layout recommendations: {_render_top_counts(report.get('recommended_layout_provider_counts', {}))}",
        f"- Math recommendations: {_render_top_counts(report.get('recommended_math_provider_counts', {}))}",
        "",
        "## OCR Summary",
        "",
        f"- OCR policies: {_render_top_counts(report.get('ocr_policy_counts', {}))}",
        f"- Selected PDF kinds: {_render_top_counts(report.get('pdf_source_kind_counts', {}))}",
        f"- Missing sidecars: {_render_top_counts(report.get('sidecar_missing_counts', {}))}",
        "",
        "## Highest-Risk Papers",
        "",
    ]

    for index, paper in enumerate(list(report.get("papers") or [])[:top_n], start=1):
        missing_sidecars = list(paper.get("missing_sidecars") or [])
        issue_flags = list(paper.get("issue_flags") or [])
        issue_summary_parts: list[str] = []
        if issue_flags:
            issue_summary_parts.append(", ".join(f"`{flag}`" for flag in issue_flags))
        if missing_sidecars:
            issue_summary_parts.append("missing " + ", ".join(f"`{name}`" for name in missing_sidecars))
        issue_summary = "; ".join(issue_summary_parts) if issue_summary_parts else "no audit issues"
        lines.extend(
            [
                f"{index}. `{paper['paper_id']}` — issues `{paper['issue_count']}`",
                f"   Route: `{paper.get('primary_route') or 'unknown'}` | layout `{paper.get('recommended_primary_layout_provider') or 'unknown'}` | math `{paper.get('recommended_primary_math_provider') or 'unknown'}`",
                f"   OCR: policy `{paper.get('ocr_policy') or 'unknown'}`, should-run `{paper.get('ocr_should_run')}`, applied `{paper.get('ocr_applied')}`, source `{paper.get('pdf_source_kind') or 'unknown'}`",
                f"   Findings: {issue_summary}",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "render_acquisition_audit_markdown",
]
