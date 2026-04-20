from __future__ import annotations

from typing import Any


def _render_top_counts(counts: dict[str, int], *, limit: int = 8) -> str:
    ranked = sorted(counts.items(), key=lambda item: (-int(item[1]), item[0]))[:limit]
    if not ranked:
        return "none"
    return ", ".join(f"`{name}`={count}" for name, count in ranked)


def _render_rejections(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in items:
        provider = str(item.get("provider") or "unknown")
        kind = str(item.get("kind") or "unknown")
        reasons = [str(reason) for reason in list(item.get("rejection_reasons") or []) if str(reason)]
        if reasons:
            rendered_reasons = "/".join(f"`{reason}`" for reason in reasons)
            parts.append(f"`{provider}`/{kind}:{rendered_reasons}")
    if not parts:
        return "none"
    return ", ".join(parts)


def _render_follow_up(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in items:
        product = str(item.get("product") or "unknown")
        action = str(item.get("action") or "unknown")
        target_provider = str(item.get("target_provider") or "").strip()
        if target_provider:
            parts.append(f"`{product}` -> `{action}` via `{target_provider}`")
        else:
            parts.append(f"`{product}` -> `{action}`")
    if not parts:
        return "none"
    return ", ".join(parts)


def _render_priority_reasons(items: list[str]) -> str:
    reasons = [str(item).strip() for item in items if str(item).strip()]
    if not reasons:
        return "none"
    return ", ".join(f"`{reason}`" for reason in reasons)


def render_acquisition_audit_markdown(report: dict[str, Any], *, top_n: int) -> str:
    ocr_summary = dict(report.get("ocr_summary") or {})
    actionable_papers = list(report.get("remediation_queue") or [])
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
        f"- Metadata recommendations: {_render_top_counts(report.get('recommended_metadata_provider_counts', {}))}",
        f"- Reference recommendations: {_render_top_counts(report.get('recommended_reference_provider_counts', {}))}",
        f"- Layout recommendation basis: {_render_top_counts(report.get('layout_recommendation_basis_counts', {}))}",
        f"- Math recommendation basis: {_render_top_counts(report.get('math_recommendation_basis_counts', {}))}",
        f"- Metadata recommendation basis: {_render_top_counts(report.get('metadata_recommendation_basis_counts', {}))}",
        f"- Reference recommendation basis: {_render_top_counts(report.get('reference_recommendation_basis_counts', {}))}",
        f"- Executed layout providers: {_render_top_counts(report.get('executed_layout_provider_counts', {}))}",
        f"- Executed math providers: {_render_top_counts(report.get('executed_math_provider_counts', {}))}",
        f"- Executed metadata providers: {_render_top_counts(report.get('executed_metadata_provider_counts', {}))}",
        f"- Executed reference providers: {_render_top_counts(report.get('executed_reference_provider_counts', {}))}",
        f"- Follow-up needed: {_render_top_counts(report.get('follow_up_needed_counts', {}))}",
        f"- Follow-up actions: {_render_top_counts(report.get('follow_up_action_counts', {}))}",
        f"- Follow-up targets: {_render_top_counts(report.get('follow_up_target_provider_counts', {}))}",
        f"- Active promoted trials: {_render_top_counts(report.get('active_promoted_trial_counts', {}))}",
        f"- Latest applied trials: {_render_top_counts(report.get('latest_applied_trial_counts', {}))}",
        f"- Metadata application: {_render_top_counts(report.get('metadata_application_counts', {}))}",
        f"- Reference application: {_render_top_counts(report.get('reference_application_counts', {}))}",
        f"- Metadata suppressed reasons: {_render_top_counts(report.get('metadata_suppressed_reason_counts', {}))}",
        f"- Reference suppressed reasons: {_render_top_counts(report.get('reference_suppressed_reason_counts', {}))}",
        f"- Rejection reasons: {_render_top_counts(report.get('provider_rejection_reason_counts', {}))}",
        f"- Remediation priorities: {_render_top_counts(report.get('remediation_priority_counts', {}))}",
        "",
        "## OCR Summary",
        "",
        f"- OCR policies: {_render_top_counts(report.get('ocr_policy_counts', {}))}",
        f"- Selected PDF kinds: {_render_top_counts(report.get('pdf_source_kind_counts', {}))}",
        f"- Missing sidecars: {_render_top_counts(report.get('sidecar_missing_counts', {}))}",
        "",
        "## Remediation Queue",
        "",
    ]

    if actionable_papers:
        for index, paper in enumerate(actionable_papers[:top_n], start=1):
            lines.extend(
                [
                    f"{index}. `{paper['paper_id']}` — priority `{paper.get('remediation_priority_label') or 'unknown'}` score `{paper.get('remediation_priority_score') or 0}` | issues `{paper['issue_count']}`",
                    f"   Why: {_render_priority_reasons(list(paper.get('remediation_priority_reasons') or []))}",
                    f"   Follow-up: {_render_follow_up(list(paper.get('follow_up_actions') or []))}",
                    f"   Command: `{paper.get('remediation_command')}`",
                ]
            )
    else:
        lines.append("- No actionable remediation commands.")

    lines.extend(
        [
            "",
        "## Highest-Risk Papers",
        "",
        ]
    )

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
                f"   Route: `{paper.get('primary_route') or 'unknown'}` | recommended layout `{paper.get('recommended_primary_layout_provider') or 'unknown'}` ({paper.get('layout_recommendation_basis') or 'unknown'}) | recommended math `{paper.get('recommended_primary_math_provider') or 'unknown'}` ({paper.get('math_recommendation_basis') or 'unknown'})",
                f"   Ownership: metadata `{paper.get('recommended_primary_metadata_provider') or 'unknown'}` ({paper.get('metadata_recommendation_basis') or 'unknown'}) | references `{paper.get('recommended_primary_reference_provider') or 'unknown'}` ({paper.get('reference_recommendation_basis') or 'unknown'})",
                f"   Executed: layout `{paper.get('executed_layout_provider') or 'unknown'}` | math `{paper.get('executed_math_provider') or 'unknown'}` | metadata `{paper.get('executed_metadata_provider') or 'unknown'}` | references `{paper.get('executed_reference_provider') or 'unknown'}` | execution report `{paper.get('has_execution_report')}`",
                f"   Follow-up: needed `{paper.get('follow_up_needed')}` | {_render_follow_up(list(paper.get('follow_up_actions') or []))}",
                f"   Trials: latest applied `{paper.get('latest_applied_trial_label') or 'none'}` at `{paper.get('latest_applied_trial_at') or 'none'}` | active promoted `{paper.get('active_promoted_trial_label') or 'none'}` at `{paper.get('active_promoted_trial_at') or 'none'}`",
                f"   Remediation: `{paper.get('remediation_command') or 'none'}` | priority `{paper.get('remediation_priority_label') or 'none'}` score `{paper.get('remediation_priority_score') or 0}`",
                f"   Applied: metadata `{paper.get('metadata_applied')}` | references `{paper.get('references_applied')}` | suppressed metadata `{paper.get('metadata_suppressed_reason') or 'none'}` | suppressed references `{paper.get('reference_suppressed_reason') or 'none'}`",
                f"   OCR: policy `{paper.get('ocr_policy') or 'unknown'}`, should-run `{paper.get('ocr_should_run')}`, applied `{paper.get('ocr_applied')}`, source `{paper.get('pdf_source_kind') or 'unknown'}`",
                f"   Rejections: {_render_rejections(list(paper.get('rejected_providers') or []))}",
                f"   Findings: {issue_summary}",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "render_acquisition_audit_markdown",
]
