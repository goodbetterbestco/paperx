from __future__ import annotations

from typing import Any


def _render_top_counts(counts: dict[str, int], *, limit: int = 6) -> str:
    ranked = sorted(
        (
            (str(key), int(value))
            for key, value in dict(counts or {}).items()
            if str(key).strip() and int(value or 0) > 0
        ),
        key=lambda item: (-item[1], item[0]),
    )[:limit]
    if not ranked:
        return "none"
    return ", ".join(f"`{name}`={count}" for name, count in ranked)


def render_acquisition_policy_feedback_markdown(report: dict[str, Any]) -> str:
    signal_counts = dict(report.get("signal_counts") or {})
    lines = [
        "# Acquisition Policy Feedback",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Source generated at: `{report.get('source_generated_at') or 'unknown'}`",
        f"- Source report: `{report.get('source_report_path') or 'live_audit'}`",
        f"- Papers audited: `{report.get('paper_count', 0)}`",
        f"- Remediation queue size: `{report.get('remediation_queue_count', 0)}`",
        f"- Papers with follow-up actions: `{report.get('follow_up_paper_count', 0)}`",
        f"- Papers with suppressed application: `{report.get('suppressed_application_paper_count', 0)}`",
        f"- OCR gap papers: `{report.get('ocr_gap_paper_count', 0)}`",
        "",
        "## Signal Summary",
        "",
        f"- Issue flags: {_render_top_counts(dict(signal_counts.get('issue_flag_counts') or {}))}",
        f"- Remediation priority reasons: {_render_top_counts(dict(signal_counts.get('remediation_priority_reason_counts') or {}))}",
        f"- Follow-up actions: {_render_top_counts(dict(signal_counts.get('follow_up_action_counts') or {}))}",
        f"- Rejection reasons: {_render_top_counts(dict(signal_counts.get('provider_rejection_reason_counts') or {}))}",
        f"- Metadata suppressed reasons: {_render_top_counts(dict(signal_counts.get('metadata_suppressed_reason_counts') or {}))}",
        f"- Reference suppressed reasons: {_render_top_counts(dict(signal_counts.get('reference_suppressed_reason_counts') or {}))}",
        f"- Missing sidecars: {_render_top_counts(dict(signal_counts.get('sidecar_missing_counts') or {}))}",
        "",
        "## Recommended Actions",
        "",
    ]

    actions = list(report.get("policy_actions") or [])
    if not actions:
        lines.append("- none")
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    for action in actions:
        evidence_summary = ", ".join(
            f"`{item.get('label')}` x{int(item.get('count') or 0)}"
            for item in list(action.get("evidence") or [])
        ) or "none"
        module_summary = ", ".join(f"`{item}`" for item in list(action.get("recommended_modules") or [])) or "`none`"
        lines.extend(
            [
                f"### `{action.get('action')}`",
                "",
                f"- Category: `{action.get('category') or 'unknown'}`",
                f"- Priority score: `{action.get('priority_score', 0)}`",
                f"- Evidence count: `{action.get('evidence_count', 0)}`",
                f"- Why now: {evidence_summary}",
                f"- Recommended modules: {module_summary}",
                f"- Summary: {action.get('summary') or 'none'}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_acquisition_policy_feedback_markdown"]
