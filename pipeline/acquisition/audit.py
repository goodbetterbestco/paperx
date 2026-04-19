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


def audit_acquisition_quality(*, layout: ProjectLayout) -> dict[str, Any]:
    route_counts: dict[str, int] = {}
    recommended_layout_provider_counts: dict[str, int] = {}
    recommended_math_provider_counts: dict[str, int] = {}
    executed_layout_provider_counts: dict[str, int] = {}
    executed_math_provider_counts: dict[str, int] = {}
    ocr_policy_counts: dict[str, int] = {}
    pdf_source_kind_counts: dict[str, int] = {}
    sidecar_missing_counts: dict[str, int] = {}
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
        route_ocr = dict((route or {}).get("ocr_prepass") or {})
        executed = dict((execution_report or {}).get("executed") or {})

        primary_route = str((route or {}).get("primary_route") or "").strip() or None
        recommended_layout_provider = str((scorecard or {}).get("recommended_primary_layout_provider") or "").strip() or None
        recommended_math_provider = str((scorecard or {}).get("recommended_primary_math_provider") or "").strip() or None
        executed_layout_provider = str(executed.get("selected_layout_provider") or "").strip() or None
        executed_math_provider = str(executed.get("selected_math_provider") or "").strip() or None
        ocr_policy = str((ocr_report or {}).get("ocr_prepass_policy") or route_ocr.get("policy") or "").strip() or None
        ocr_tool = str((ocr_report or {}).get("ocr_prepass_tool") or route_ocr.get("tool") or "").strip() or None
        ocr_should_run = bool(route_ocr.get("should_run"))
        ocr_applied = bool((ocr_report or {}).get("ocr_prepass_applied"))
        pdf_source_kind = str((ocr_report or {}).get("pdf_source_kind") or "").strip() or None
        missing_sidecars = _missing_sidecars(route, scorecard, ocr_report)
        issue_flags: list[str] = []

        if canonical_path.exists():
            canonical_count += 1

        _increment(route_counts, primary_route)
        _increment(recommended_layout_provider_counts, recommended_layout_provider)
        _increment(recommended_math_provider_counts, recommended_math_provider)
        _increment(executed_layout_provider_counts, executed_layout_provider)
        _increment(executed_math_provider_counts, executed_math_provider)
        _increment(ocr_policy_counts, ocr_policy)
        _increment(pdf_source_kind_counts, pdf_source_kind)

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

        papers.append(
            {
                "paper_id": paper_id,
                "has_canonical": canonical_path.exists(),
                "canonical_path": str(canonical_path),
                "sources_dir": str(sources_dir),
                "primary_route": primary_route,
                "recommended_primary_layout_provider": recommended_layout_provider,
                "recommended_primary_math_provider": recommended_math_provider,
                "executed_layout_provider": executed_layout_provider,
                "executed_math_provider": executed_math_provider,
                "has_execution_report": execution_report is not None,
                "ocr_policy": ocr_policy,
                "ocr_should_run": ocr_should_run,
                "ocr_tool": ocr_tool,
                "ocr_applied": ocr_applied,
                "pdf_source_kind": pdf_source_kind,
                "missing_sidecars": missing_sidecars,
                "issue_flags": issue_flags,
                "issue_count": len(missing_sidecars) + len([flag for flag in issue_flags if flag != "missing_sidecars"]),
            }
        )

    papers.sort(key=lambda item: (-int(item["issue_count"]), str(item["paper_id"])))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_count": len(papers),
        "canonical_count": canonical_count,
        "missing_canonical_count": len(papers) - canonical_count,
        "route_counts": route_counts,
        "recommended_layout_provider_counts": recommended_layout_provider_counts,
        "recommended_math_provider_counts": recommended_math_provider_counts,
        "executed_layout_provider_counts": executed_layout_provider_counts,
        "executed_math_provider_counts": executed_math_provider_counts,
        "ocr_policy_counts": ocr_policy_counts,
        "pdf_source_kind_counts": pdf_source_kind_counts,
        "sidecar_missing_counts": sidecar_missing_counts,
        "ocr_summary": {
            "should_run_count": ocr_should_run_count,
            "applied_count": ocr_applied_count,
            "required_not_applied_count": required_not_applied_count,
            "recommended_not_applied_count": recommended_not_applied_count,
        },
        "papers": papers,
    }


__all__ = [
    "audit_acquisition_quality",
]
