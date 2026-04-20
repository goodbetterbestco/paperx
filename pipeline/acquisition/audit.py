from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout


SIDECARE_ROUTE = "acquisition-route.json"
SIDECARE_SCORECARD = "source-scorecard.json"
SIDECARE_OCR = "ocr-prepass.json"
SIDECAR_EXECUTION = "acquisition-execution.json"
SIDECAR_METADATA_DECISION = "metadata-decision.json"
REMEDIATION_PRIORITY_RANK = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def _increment(counter: dict[str, int], key: str | None) -> None:
    normalized = str(key or "").strip()
    if not normalized:
        return
    counter[normalized] = counter.get(normalized, 0) + 1


def _discover_paper_ids(layout: ProjectLayout) -> list[str]:
    paper_ids: set[str] = set()
    if layout.corpus_root.exists():
        for child in layout.corpus_root.iterdir():
            if not child.is_dir():
                continue
            if child.name.startswith("_") or child.name == "review_drafts":
                continue
            paper_ids.add(child.name)
    if layout.project_mode:
        for pdf_path in layout.discover_source_pdfs():
            paper_ids.add(pdf_path.stem)
    return sorted(paper_ids)


def _missing_sidecars(
    route: dict[str, Any] | None,
    scorecard: dict[str, Any] | None,
    ocr_report: dict[str, Any] | None,
) -> list[str]:
    missing: list[str] = []
    if route is None:
        missing.append(SIDECARE_ROUTE)
    if scorecard is None:
        missing.append(SIDECARE_SCORECARD)
    if ocr_report is None:
        missing.append(SIDECARE_OCR)
    return missing


def _latest_trial_info(sources_dir: Path) -> dict[str, str | None]:
    trials_dir = sources_dir / "trials"
    latest_label: str | None = None
    latest_applied_at: str | None = None
    if not trials_dir.exists():
        return {
            "latest_applied_trial_label": None,
            "latest_applied_trial_at": None,
        }
    for trial_dir in sorted(path for path in trials_dir.iterdir() if path.is_dir()):
        execution_path = trial_dir / SIDECAR_EXECUTION
        if not execution_path.exists():
            continue
        payload = _load_json_dict(execution_path) or {}
        trial = dict(payload.get("trial") or {})
        applied_at = str(trial.get("applied_at") or "").strip() or None
        label = str(trial.get("label") or trial_dir.name).strip() or trial_dir.name
        if applied_at and (latest_applied_at is None or applied_at > latest_applied_at):
            latest_applied_at = applied_at
            latest_label = label
    return {
        "latest_applied_trial_label": latest_label,
        "latest_applied_trial_at": latest_applied_at,
    }


def _default_trial_label(follow_up_actions: list[dict[str, Any]]) -> str:
    providers = [
        str(item.get("target_provider") or "").strip()
        for item in follow_up_actions
        if str(item.get("target_provider") or "").strip()
    ]
    if providers:
        return f"trial-{'-'.join(sorted(set(providers)))}"
    return "follow-up"


def _remediation_command(
    paper_id: str,
    *,
    follow_up_needed: bool,
    follow_up_actions: list[dict[str, Any]],
    active_promoted_trial_label: str | None,
) -> str | None:
    if not follow_up_needed or active_promoted_trial_label:
        return None
    label = _default_trial_label(follow_up_actions)
    return f"python3 -m pipeline.cli.remediate_acquisition_follow_up {paper_id} --label {label}"


def _remediation_priority_rank(label: str | None) -> int:
    return int(REMEDIATION_PRIORITY_RANK.get(str(label or "").strip().lower(), -1))


def _remediation_priority(
    *,
    primary_route: str | None,
    missing_sidecars: list[str],
    ocr_policy: str | None,
    ocr_should_run: bool,
    ocr_applied: bool,
    follow_up_actions: list[dict[str, Any]],
    layout_recommendation_basis: str | None,
    math_recommendation_basis: str | None,
    metadata_suppressed_reason: str | None,
    reference_suppressed_reason: str | None,
) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []
    if missing_sidecars:
        score += 6
        reasons.append("missing_sidecars")
    if ocr_policy == "required" and ocr_should_run and not ocr_applied:
        score += 8
        reasons.append("required_ocr_not_applied")
    elif ocr_policy == "recommended" and ocr_should_run and not ocr_applied:
        score += 2
        reasons.append("recommended_ocr_not_applied")
    if layout_recommendation_basis == "fallback_unaccepted" or math_recommendation_basis == "fallback_unaccepted":
        score += 3
        reasons.append("fallback_recommendation")
    if metadata_suppressed_reason:
        score += 2
        reasons.append("metadata_application_suppressed")
    if reference_suppressed_reason:
        score += 2
        reasons.append("reference_application_suppressed")
    if follow_up_actions:
        score += min(len(follow_up_actions), 3)
        reasons.append("follow_up_actions")
    if primary_route in {"scan_or_image_heavy", "degraded_or_garbled"}:
        score += 1
        reasons.append("route_complexity")

    if score >= 8:
        label = "critical"
    elif score >= 5:
        label = "high"
    elif score >= 3:
        label = "medium"
    else:
        label = "low"
    return {
        "label": label,
        "score": score,
        "reasons": reasons,
    }


def audit_acquisition_quality(*, layout: ProjectLayout) -> dict[str, Any]:
    route_counts: dict[str, int] = {}
    recommended_layout_provider_counts: dict[str, int] = {}
    recommended_math_provider_counts: dict[str, int] = {}
    recommended_metadata_provider_counts: dict[str, int] = {}
    recommended_reference_provider_counts: dict[str, int] = {}
    layout_recommendation_basis_counts: dict[str, int] = {}
    math_recommendation_basis_counts: dict[str, int] = {}
    metadata_recommendation_basis_counts: dict[str, int] = {}
    reference_recommendation_basis_counts: dict[str, int] = {}
    executed_layout_provider_counts: dict[str, int] = {}
    executed_math_provider_counts: dict[str, int] = {}
    executed_metadata_provider_counts: dict[str, int] = {}
    executed_reference_provider_counts: dict[str, int] = {}
    follow_up_needed_counts: dict[str, int] = {}
    follow_up_action_counts: dict[str, int] = {}
    follow_up_target_provider_counts: dict[str, int] = {}
    active_promoted_trial_counts: dict[str, int] = {}
    latest_applied_trial_counts: dict[str, int] = {}
    metadata_application_counts: dict[str, int] = {}
    reference_application_counts: dict[str, int] = {}
    metadata_suppressed_reason_counts: dict[str, int] = {}
    reference_suppressed_reason_counts: dict[str, int] = {}
    ocr_policy_counts: dict[str, int] = {}
    pdf_source_kind_counts: dict[str, int] = {}
    sidecar_missing_counts: dict[str, int] = {}
    provider_rejection_reason_counts: dict[str, int] = {}
    remediation_priority_counts: dict[str, int] = {}
    papers: list[dict[str, Any]] = []
    ocr_should_run_count = 0
    ocr_applied_count = 0
    required_not_applied_count = 0
    recommended_not_applied_count = 0
    canonical_count = 0

    for paper_id in _discover_paper_ids(layout):
        canonical_path = layout.canonical_path(paper_id)
        sources_dir = layout.canonical_sources_dir(paper_id)
        route = _load_json_dict(sources_dir / SIDECARE_ROUTE)
        scorecard = _load_json_dict(sources_dir / SIDECARE_SCORECARD)
        ocr_report = _load_json_dict(sources_dir / SIDECARE_OCR)
        execution_report = _load_json_dict(sources_dir / SIDECAR_EXECUTION)
        metadata_decision = _load_json_dict(sources_dir / SIDECAR_METADATA_DECISION)
        route_ocr = dict((route or {}).get("ocr_prepass") or {})
        executed = dict((execution_report or {}).get("executed") or {})
        follow_up = dict((execution_report or {}).get("follow_up") or {})
        promotion = dict((execution_report or {}).get("promotion") or {})
        latest_trial = _latest_trial_info(sources_dir)

        primary_route = str((route or {}).get("primary_route") or "").strip() or None
        recommended_layout_provider = str((scorecard or {}).get("recommended_primary_layout_provider") or "").strip() or None
        recommended_math_provider = str((scorecard or {}).get("recommended_primary_math_provider") or "").strip() or None
        recommended_metadata_provider = str((scorecard or {}).get("recommended_primary_metadata_provider") or "").strip() or None
        recommended_reference_provider = str((scorecard or {}).get("recommended_primary_reference_provider") or "").strip() or None
        layout_recommendation_basis = str((scorecard or {}).get("layout_recommendation_basis") or "").strip() or None
        math_recommendation_basis = str((scorecard or {}).get("math_recommendation_basis") or "").strip() or None
        metadata_recommendation_basis = str((scorecard or {}).get("metadata_recommendation_basis") or "").strip() or None
        reference_recommendation_basis = str((scorecard or {}).get("reference_recommendation_basis") or "").strip() or None
        executed_layout_provider = str(executed.get("selected_layout_provider") or "").strip() or None
        executed_math_provider = str(executed.get("selected_math_provider") or "").strip() or None
        executed_metadata_provider = str(executed.get("metadata_provider") or "").strip() or None
        executed_reference_provider = str(executed.get("reference_provider") or "").strip() or None
        follow_up_needed = bool(follow_up.get("needs_attention"))
        active_promoted_trial_label = str(promotion.get("label") or "").strip() or None
        active_promoted_trial_at = str(promotion.get("promoted_at") or "").strip() or None
        latest_applied_trial_label = str(latest_trial.get("latest_applied_trial_label") or "").strip() or None
        latest_applied_trial_at = str(latest_trial.get("latest_applied_trial_at") or "").strip() or None
        follow_up_actions = [
            {
                "product": str(item.get("product") or "").strip() or None,
                "reason": str(item.get("reason") or "").strip() or None,
                "action": str(item.get("action") or "").strip() or None,
                "target_provider": str(item.get("target_provider") or "").strip() or None,
            }
            for item in list(follow_up.get("actions") or [])
            if isinstance(item, dict)
        ]
        remediation_command = _remediation_command(
            paper_id,
            follow_up_needed=follow_up_needed,
            follow_up_actions=follow_up_actions,
            active_promoted_trial_label=active_promoted_trial_label,
        )
        metadata_applied = bool((metadata_decision or {}).get("title_applied")) or bool((metadata_decision or {}).get("abstract_applied"))
        references_applied = bool((metadata_decision or {}).get("references_applied"))
        metadata_suppressed_reason = (
            str((metadata_decision or {}).get("title_suppressed_reason") or (metadata_decision or {}).get("abstract_suppressed_reason") or "").strip()
            or None
        )
        reference_suppressed_reason = str((metadata_decision or {}).get("references_suppressed_reason") or "").strip() or None
        ocr_policy = str((ocr_report or {}).get("ocr_prepass_policy") or route_ocr.get("policy") or "").strip() or None
        ocr_tool = str((ocr_report or {}).get("ocr_prepass_tool") or route_ocr.get("tool") or "").strip() or None
        ocr_should_run = bool(route_ocr.get("should_run"))
        ocr_applied = bool((ocr_report or {}).get("ocr_prepass_applied"))
        pdf_source_kind = str((ocr_report or {}).get("pdf_source_kind") or "").strip() or None
        rejected_providers = [
            {
                "provider": str(item.get("provider") or ""),
                "kind": str(item.get("kind") or ""),
                "rejection_reasons": [str(reason) for reason in list(item.get("rejection_reasons") or []) if str(reason)],
            }
            for item in list((scorecard or {}).get("providers") or [])
            if item and not bool(item.get("accepted"))
        ]
        missing_sidecars = _missing_sidecars(route, scorecard, ocr_report)
        issue_flags: list[str] = []

        if canonical_path.exists():
            canonical_count += 1

        _increment(route_counts, primary_route)
        _increment(recommended_layout_provider_counts, recommended_layout_provider)
        _increment(recommended_math_provider_counts, recommended_math_provider)
        _increment(recommended_metadata_provider_counts, recommended_metadata_provider)
        _increment(recommended_reference_provider_counts, recommended_reference_provider)
        _increment(layout_recommendation_basis_counts, layout_recommendation_basis)
        _increment(math_recommendation_basis_counts, math_recommendation_basis)
        _increment(metadata_recommendation_basis_counts, metadata_recommendation_basis)
        _increment(reference_recommendation_basis_counts, reference_recommendation_basis)
        _increment(executed_layout_provider_counts, executed_layout_provider)
        _increment(executed_math_provider_counts, executed_math_provider)
        _increment(executed_metadata_provider_counts, executed_metadata_provider)
        _increment(executed_reference_provider_counts, executed_reference_provider)
        _increment(follow_up_needed_counts, "needs_attention" if follow_up_needed else "no_follow_up")
        for item in follow_up_actions:
            _increment(follow_up_action_counts, item["action"])
            _increment(follow_up_target_provider_counts, item["target_provider"])
        _increment(active_promoted_trial_counts, active_promoted_trial_label)
        _increment(latest_applied_trial_counts, latest_applied_trial_label)
        _increment(metadata_application_counts, "applied" if metadata_applied else "not_applied")
        _increment(reference_application_counts, "applied" if references_applied else "not_applied")
        _increment(metadata_suppressed_reason_counts, metadata_suppressed_reason)
        _increment(reference_suppressed_reason_counts, reference_suppressed_reason)
        _increment(ocr_policy_counts, ocr_policy)
        _increment(pdf_source_kind_counts, pdf_source_kind)
        for item in rejected_providers:
            for reason in item["rejection_reasons"]:
                _increment(provider_rejection_reason_counts, reason)

        for sidecar_name in missing_sidecars:
            sidecar_missing_counts[sidecar_name] = sidecar_missing_counts.get(sidecar_name, 0) + 1

        if ocr_should_run:
            ocr_should_run_count += 1
        if ocr_applied:
            ocr_applied_count += 1

        if ocr_policy == "required" and not ocr_applied:
            required_not_applied_count += 1
            issue_flags.append("required_ocr_not_applied")
        elif ocr_policy == "recommended" and ocr_should_run and not ocr_applied:
            recommended_not_applied_count += 1
            issue_flags.append("recommended_ocr_not_applied")

        if ocr_should_run and not ocr_tool:
            issue_flags.append("missing_ocr_tool")
        if ocr_policy == "skip" and ocr_applied:
            issue_flags.append("unexpected_ocr_application")
        if missing_sidecars:
            issue_flags.append("missing_sidecars")
        if layout_recommendation_basis == "fallback_unaccepted" or math_recommendation_basis == "fallback_unaccepted":
            issue_flags.append("fallback_recommendation")
        if metadata_suppressed_reason:
            issue_flags.append("metadata_application_suppressed")
        if reference_suppressed_reason:
            issue_flags.append("reference_application_suppressed")
        if follow_up_needed:
            issue_flags.append("follow_up_recommended")
        if active_promoted_trial_label:
            issue_flags.append("trial_promoted")

        issue_count = len(missing_sidecars) + len([flag for flag in issue_flags if flag != "missing_sidecars"])
        remediation_priority: dict[str, Any] | None = None
        if remediation_command:
            remediation_priority = _remediation_priority(
                primary_route=primary_route,
                missing_sidecars=missing_sidecars,
                ocr_policy=ocr_policy,
                ocr_should_run=ocr_should_run,
                ocr_applied=ocr_applied,
                follow_up_actions=follow_up_actions,
                layout_recommendation_basis=layout_recommendation_basis,
                math_recommendation_basis=math_recommendation_basis,
                metadata_suppressed_reason=metadata_suppressed_reason,
                reference_suppressed_reason=reference_suppressed_reason,
            )
            _increment(remediation_priority_counts, str(remediation_priority.get("label") or "").strip() or None)

        papers.append(
            {
                "paper_id": paper_id,
                "has_canonical": canonical_path.exists(),
                "canonical_path": str(canonical_path),
                "sources_dir": str(sources_dir),
                "primary_route": primary_route,
                "recommended_primary_layout_provider": recommended_layout_provider,
                "recommended_primary_math_provider": recommended_math_provider,
                "recommended_primary_metadata_provider": recommended_metadata_provider,
                "recommended_primary_reference_provider": recommended_reference_provider,
                "layout_recommendation_basis": layout_recommendation_basis,
                "math_recommendation_basis": math_recommendation_basis,
                "metadata_recommendation_basis": metadata_recommendation_basis,
                "reference_recommendation_basis": reference_recommendation_basis,
                "executed_layout_provider": executed_layout_provider,
                "executed_math_provider": executed_math_provider,
                "executed_metadata_provider": executed_metadata_provider,
                "executed_reference_provider": executed_reference_provider,
                "follow_up_needed": follow_up_needed,
                "follow_up_actions": follow_up_actions,
                "active_promoted_trial_label": active_promoted_trial_label,
                "active_promoted_trial_at": active_promoted_trial_at,
                "latest_applied_trial_label": latest_applied_trial_label,
                "latest_applied_trial_at": latest_applied_trial_at,
                "remediation_command": remediation_command,
                "remediation_priority_label": (
                    str(remediation_priority.get("label") or "").strip() or None if remediation_priority else None
                ),
                "remediation_priority_score": (
                    int(remediation_priority.get("score") or 0) if remediation_priority else None
                ),
                "remediation_priority_reasons": list(remediation_priority.get("reasons") or []) if remediation_priority else [],
                "metadata_applied": metadata_applied,
                "references_applied": references_applied,
                "metadata_suppressed_reason": metadata_suppressed_reason,
                "reference_suppressed_reason": reference_suppressed_reason,
                "has_execution_report": execution_report is not None,
                "ocr_policy": ocr_policy,
                "ocr_should_run": ocr_should_run,
                "ocr_tool": ocr_tool,
                "ocr_applied": ocr_applied,
                "pdf_source_kind": pdf_source_kind,
                "rejected_providers": rejected_providers,
                "missing_sidecars": missing_sidecars,
                "issue_flags": issue_flags,
                "issue_count": issue_count,
            }
        )

    papers.sort(key=lambda item: (-int(item["issue_count"]), str(item["paper_id"])))
    remediation_queue = [
        {
            "paper_id": str(paper["paper_id"]),
            "issue_count": int(paper["issue_count"]),
            "primary_route": paper["primary_route"],
            "follow_up_actions": list(paper["follow_up_actions"]),
            "remediation_priority_label": paper["remediation_priority_label"],
            "remediation_priority_score": paper["remediation_priority_score"],
            "remediation_priority_reasons": list(paper["remediation_priority_reasons"]),
            "latest_applied_trial_label": paper["latest_applied_trial_label"],
            "latest_applied_trial_at": paper["latest_applied_trial_at"],
            "active_promoted_trial_label": paper["active_promoted_trial_label"],
            "active_promoted_trial_at": paper["active_promoted_trial_at"],
            "remediation_command": paper["remediation_command"],
        }
        for paper in papers
        if str(paper.get("remediation_command") or "").strip()
    ]
    remediation_queue.sort(
        key=lambda item: (
            -_remediation_priority_rank(str(item.get("remediation_priority_label") or None)),
            -int(item.get("remediation_priority_score") or 0),
            -int(item.get("issue_count") or 0),
            str(item.get("paper_id") or ""),
        )
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_count": len(papers),
        "canonical_count": canonical_count,
        "missing_canonical_count": len(papers) - canonical_count,
        "route_counts": route_counts,
        "recommended_layout_provider_counts": recommended_layout_provider_counts,
        "recommended_math_provider_counts": recommended_math_provider_counts,
        "recommended_metadata_provider_counts": recommended_metadata_provider_counts,
        "recommended_reference_provider_counts": recommended_reference_provider_counts,
        "layout_recommendation_basis_counts": layout_recommendation_basis_counts,
        "math_recommendation_basis_counts": math_recommendation_basis_counts,
        "metadata_recommendation_basis_counts": metadata_recommendation_basis_counts,
        "reference_recommendation_basis_counts": reference_recommendation_basis_counts,
        "executed_layout_provider_counts": executed_layout_provider_counts,
        "executed_math_provider_counts": executed_math_provider_counts,
        "executed_metadata_provider_counts": executed_metadata_provider_counts,
        "executed_reference_provider_counts": executed_reference_provider_counts,
        "follow_up_needed_counts": follow_up_needed_counts,
        "follow_up_action_counts": follow_up_action_counts,
        "follow_up_target_provider_counts": follow_up_target_provider_counts,
        "active_promoted_trial_counts": active_promoted_trial_counts,
        "latest_applied_trial_counts": latest_applied_trial_counts,
        "metadata_application_counts": metadata_application_counts,
        "reference_application_counts": reference_application_counts,
        "metadata_suppressed_reason_counts": metadata_suppressed_reason_counts,
        "reference_suppressed_reason_counts": reference_suppressed_reason_counts,
        "ocr_policy_counts": ocr_policy_counts,
        "pdf_source_kind_counts": pdf_source_kind_counts,
        "sidecar_missing_counts": sidecar_missing_counts,
        "provider_rejection_reason_counts": provider_rejection_reason_counts,
        "remediation_priority_counts": remediation_priority_counts,
        "ocr_summary": {
            "should_run_count": ocr_should_run_count,
            "applied_count": ocr_applied_count,
            "required_not_applied_count": required_not_applied_count,
            "recommended_not_applied_count": recommended_not_applied_count,
        },
        "remediation_queue": remediation_queue,
        "papers": papers,
    }


__all__ = [
    "audit_acquisition_quality",
]
