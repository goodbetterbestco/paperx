from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


POLICY_ACTION_RULES: tuple[dict[str, Any], ...] = (
    {
        "action": "tighten_ocr_execution_defaults",
        "category": "ocr",
        "summary": "OCR-required or OCR-recommended papers are still escaping without the intended OCR pre-pass.",
        "recommended_modules": [
            "pipeline/acquisition/ocr_policy.py",
            "pipeline/orchestrator/round_sources.py",
            "pipeline/sources/ocrmypdf.py",
        ],
        "evidence_rules": (
            {
                "source": "issue_flag_counts",
                "key": "required_ocr_not_applied",
                "weight": 6,
                "label": "required OCR missed",
            },
            {
                "source": "issue_flag_counts",
                "key": "recommended_ocr_not_applied",
                "weight": 3,
                "label": "recommended OCR missed",
            },
            {
                "source": "remediation_priority_reason_counts",
                "key": "required_ocr_not_applied",
                "weight": 4,
                "label": "required OCR drove remediation priority",
            },
            {
                "source": "remediation_priority_reason_counts",
                "key": "recommended_ocr_not_applied",
                "weight": 2,
                "label": "recommended OCR drove remediation priority",
            },
        ),
    },
    {
        "action": "tighten_provider_acceptance_thresholds",
        "category": "routing_scoring",
        "summary": "Fallback recommendations and provider trials suggest the current scoring thresholds or route plans are too permissive.",
        "recommended_modules": [
            "pipeline/acquisition/scoring.py",
            "pipeline/acquisition/providers.py",
            "pipeline/acquisition/routing.py",
        ],
        "evidence_rules": (
            {
                "source": "issue_flag_counts",
                "key": "fallback_recommendation",
                "weight": 4,
                "label": "fallback recommendations accumulating",
            },
            {
                "source": "follow_up_action_counts",
                "key": "trial_layout_provider",
                "weight": 4,
                "label": "layout provider trials requested",
            },
            {
                "source": "follow_up_action_counts",
                "key": "trial_math_provider",
                "weight": 4,
                "label": "math provider trials requested",
            },
            {
                "source": "provider_rejection_reason_counts",
                "key": "score_below_threshold",
                "weight": 2,
                "label": "providers rejected on threshold",
            },
        ),
    },
    {
        "action": "stabilize_metadata_ownership",
        "category": "metadata",
        "summary": "Metadata application is being suppressed or escalated instead of landing on a stable ownership decision.",
        "recommended_modules": [
            "pipeline/acquisition/source_ownership.py",
            "pipeline/orchestrator/round_paper.py",
            "pipeline/acquisition/grobid_policy.py",
        ],
        "evidence_rules": (
            {
                "source": "issue_flag_counts",
                "key": "metadata_application_suppressed",
                "weight": 4,
                "label": "metadata application suppressed",
            },
            {
                "source": "metadata_suppressed_reason_counts",
                "key": "metadata_provider_not_accepted",
                "weight": 4,
                "label": "metadata provider not accepted",
            },
            {
                "source": "follow_up_action_counts",
                "key": "escalate_grobid_metadata",
                "weight": 4,
                "label": "GROBID metadata escalation requested",
            },
        ),
    },
    {
        "action": "stabilize_reference_ownership",
        "category": "references",
        "summary": "Reference ownership is falling back to manual handling or suppressed application too often.",
        "recommended_modules": [
            "pipeline/acquisition/source_ownership.py",
            "pipeline/orchestrator/round_paper.py",
            "pipeline/acquisition/grobid_policy.py",
        ],
        "evidence_rules": (
            {
                "source": "issue_flag_counts",
                "key": "reference_application_suppressed",
                "weight": 4,
                "label": "reference application suppressed",
            },
            {
                "source": "reference_suppressed_reason_counts",
                "key": "reference_provider_not_accepted",
                "weight": 4,
                "label": "reference provider not accepted",
            },
            {
                "source": "follow_up_action_counts",
                "key": "escalate_grobid_references",
                "weight": 4,
                "label": "GROBID reference escalation requested",
            },
            {
                "source": "follow_up_action_counts",
                "key": "manual_review_references",
                "weight": 3,
                "label": "manual reference review requested",
            },
        ),
    },
    {
        "action": "enforce_acquisition_sidecar_generation",
        "category": "operator",
        "summary": "Missing acquisition sidecars are blocking policy evaluation and hiding real routing or OCR drift.",
        "recommended_modules": [
            "pipeline/acquisition/backfill.py",
            "pipeline/cli/backfill_acquisition_sidecars.py",
            "pipeline/cli/audit_acquisition_quality.py",
        ],
        "evidence_rules": (
            {
                "source": "sidecar_missing_counts",
                "key": "acquisition-route.json",
                "weight": 3,
                "label": "route sidecars missing",
            },
            {
                "source": "sidecar_missing_counts",
                "key": "source-scorecard.json",
                "weight": 3,
                "label": "scorecard sidecars missing",
            },
            {
                "source": "sidecar_missing_counts",
                "key": "ocr-prepass.json",
                "weight": 3,
                "label": "OCR sidecars missing",
            },
        ),
    },
)


def _increment(counts: dict[str, int], key: str | None) -> None:
    normalized = str(key or "").strip()
    if not normalized:
        return
    counts[normalized] = counts.get(normalized, 0) + 1


def _derive_issue_flag_counts(report: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for paper in list(report.get("papers") or []):
        for flag in list(paper.get("issue_flags") or []):
            _increment(counts, str(flag))
    return counts


def _derive_remediation_priority_reason_counts(report: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for paper in list(report.get("papers") or []):
        for reason in list(paper.get("remediation_priority_reasons") or []):
            _increment(counts, str(reason))
    return counts


def _count_papers_with_follow_up(report: dict[str, Any]) -> int:
    return sum(1 for paper in list(report.get("papers") or []) if list(paper.get("follow_up_actions") or []))


def _count_papers_with_suppressed_application(report: dict[str, Any]) -> int:
    count = 0
    for paper in list(report.get("papers") or []):
        if str(paper.get("metadata_suppressed_reason") or "").strip() or str(paper.get("reference_suppressed_reason") or "").strip():
            count += 1
    return count


def _count_papers_with_ocr_gap(report: dict[str, Any]) -> int:
    count = 0
    for paper in list(report.get("papers") or []):
        issue_flags = {str(flag).strip() for flag in list(paper.get("issue_flags") or []) if str(flag).strip()}
        if "required_ocr_not_applied" in issue_flags or "recommended_ocr_not_applied" in issue_flags:
            count += 1
    return count


def _signal_counts(report: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {
        "issue_flag_counts": _derive_issue_flag_counts(report),
        "remediation_priority_reason_counts": _derive_remediation_priority_reason_counts(report),
        "follow_up_action_counts": dict(report.get("follow_up_action_counts") or {}),
        "provider_rejection_reason_counts": dict(report.get("provider_rejection_reason_counts") or {}),
        "metadata_suppressed_reason_counts": dict(report.get("metadata_suppressed_reason_counts") or {}),
        "reference_suppressed_reason_counts": dict(report.get("reference_suppressed_reason_counts") or {}),
        "sidecar_missing_counts": dict(report.get("sidecar_missing_counts") or {}),
    }


def _policy_action_rows(report: dict[str, Any], signal_counts: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rule in POLICY_ACTION_RULES:
        evidence_rows: list[dict[str, Any]] = []
        evidence_count = 0
        priority_score = 0
        for evidence_rule in list(rule.get("evidence_rules") or []):
            source_name = str(evidence_rule.get("source") or "").strip()
            key = str(evidence_rule.get("key") or "").strip()
            weight = int(evidence_rule.get("weight") or 0)
            count = int((signal_counts.get(source_name) or {}).get(key, 0) or 0)
            if count <= 0:
                continue
            weighted_score = count * weight
            evidence_rows.append(
                {
                    "source": source_name,
                    "key": key,
                    "label": str(evidence_rule.get("label") or key),
                    "count": count,
                    "weight": weight,
                    "weighted_score": weighted_score,
                }
            )
            evidence_count += count
            priority_score += weighted_score
        if not evidence_rows:
            continue
        evidence_rows.sort(key=lambda item: (-int(item["weighted_score"]), -int(item["count"]), str(item["key"])))
        rows.append(
            {
                "action": str(rule.get("action") or ""),
                "category": str(rule.get("category") or ""),
                "summary": str(rule.get("summary") or ""),
                "recommended_modules": list(rule.get("recommended_modules") or []),
                "priority_score": priority_score,
                "evidence_count": evidence_count,
                "evidence": evidence_rows,
            }
        )
    rows.sort(
        key=lambda item: (
            -int(item["priority_score"]),
            -int(item["evidence_count"]),
            str(item["action"]),
        )
    )
    return rows


def summarize_acquisition_policy_feedback(
    report: dict[str, Any],
    *,
    source_path: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    signal_counts = _signal_counts(report)
    policy_actions = _policy_action_rows(report, signal_counts)
    return {
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source_generated_at": report.get("generated_at"),
        "source_report_path": source_path,
        "paper_count": int(report.get("paper_count", 0) or 0),
        "remediation_queue_count": len(list(report.get("remediation_queue") or [])),
        "follow_up_paper_count": _count_papers_with_follow_up(report),
        "suppressed_application_paper_count": _count_papers_with_suppressed_application(report),
        "ocr_gap_paper_count": _count_papers_with_ocr_gap(report),
        "signal_counts": signal_counts,
        "policy_actions": policy_actions,
    }


__all__ = [
    "POLICY_ACTION_RULES",
    "summarize_acquisition_policy_feedback",
]
