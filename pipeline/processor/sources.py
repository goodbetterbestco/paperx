from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.providers import build_provider_execution_plan, decide_mathpix_execution
from pipeline.acquisition.providers import derive_metadata_reference_observation_from_layout
from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.acquisition.source_ownership import (
    canonical_provider_name,
    normalize_scorecard_recommendations,
    provider_score_row,
    select_follow_up_provider,
)
from pipeline.corpus_layout import ProjectLayout, display_path, paper_pdf_path
from pipeline.processor.settings import docling_device, mathpix_credentials_available
from pipeline.orchestrator.source_composition import compose_layout_sources
from pipeline.output.artifacts import write_canonical_outputs
from pipeline.sources.docling import docling_json_to_external_sources, run_docling
from pipeline.sources.mathpix import mathpix_pages_to_external_sources, run_mathpix
from pipeline.sources.ocrmypdf import run_ocrmypdf

PER_PAPER_SOURCE_WORKERS = 2


def build_docling_sources(
    paper_id: str,
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    docling_device_impl: Callable[[], str | None] | None = None,
    run_docling_impl: Callable[..., Path] | None = None,
    docling_json_to_external_sources_impl: Callable[..., tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    docling_device_impl = docling_device_impl or docling_device
    run_docling_impl = run_docling_impl or run_docling
    docling_json_to_external_sources_impl = docling_json_to_external_sources_impl or docling_json_to_external_sources
    with tempfile.TemporaryDirectory(prefix=f"{paper_id}-docling-") as temp_dir:
        docling_json_path = run_docling_impl(
            paper_id,
            output_dir=Path(temp_dir),
            pdf_path=pdf_path,
            device=docling_device_impl(),
            layout=layout,
        )
        docling_document = json.loads(docling_json_path.read_text(encoding="utf-8"))
    external_layout, math = docling_json_to_external_sources_impl(
        docling_document,
        paper_id,
        layout=layout,
        pdf_path=pdf_path,
    )
    return {
        "docling_json": str(docling_json_path),
        "source_pdf_path": str((pdf_path or Path(external_layout.get("pdf_path", ""))).resolve()) if pdf_path else external_layout.get("pdf_path"),
        "layout": external_layout,
        "math": math,
    }


def build_mathpix_sources_from_result(
    paper_id: str,
    mathpix_result: dict[str, Any],
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    mathpix_pages_to_external_sources_impl: Callable[..., tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    mathpix_pages_to_external_sources_impl = mathpix_pages_to_external_sources_impl or mathpix_pages_to_external_sources
    payloads = list(mathpix_result.get("pages") or [])
    external_layout, math = mathpix_pages_to_external_sources_impl(
        payloads,
        paper_id,
        layout=layout,
        pdf_path=pdf_path,
    )
    result = {
        "source_pdf_path": str(pdf_path.resolve()) if pdf_path is not None else external_layout.get("pdf_path"),
        "layout": external_layout,
        "math": math,
        "math_entries": len(math.get("entries", [])),
    }
    if "pdf_id" in mathpix_result:
        result["pdf_id"] = str(mathpix_result["pdf_id"])
    if "elapsed_seconds" in mathpix_result:
        result["elapsed_seconds"] = float(mathpix_result["elapsed_seconds"])
    return result


def build_mathpix_sources(
    paper_id: str,
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    run_mathpix_impl: Callable[..., dict[str, Any]] | None = None,
    build_mathpix_sources_from_result_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    run_mathpix_impl = run_mathpix_impl or run_mathpix
    build_mathpix_sources_from_result_impl = build_mathpix_sources_from_result_impl or build_mathpix_sources_from_result
    if not mathpix_credentials_available_impl():
        return None
    mathpix_result = run_mathpix_impl(paper_id, pdf_path=pdf_path, layout=layout)
    return build_mathpix_sources_from_result_impl(paper_id, mathpix_result, pdf_path=pdf_path, layout=layout)


def mathpix_prefetch_allowed(acquisition_route: dict[str, Any] | None) -> bool:
    return decide_mathpix_execution(acquisition_route).prefetch_eligible


def resolve_extraction_pdf(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    normalized_pdf_path: Path | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    paper_pdf_path_impl: Callable[..., Path] | None = None,
    run_ocrmypdf_impl: Callable[..., Path] | None = None,
) -> dict[str, Any]:
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    paper_pdf_path_impl = paper_pdf_path_impl or paper_pdf_path
    run_ocrmypdf_impl = run_ocrmypdf_impl or run_ocrmypdf
    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    original_pdf_path = paper_pdf_path_impl(paper_id, layout=layout)
    if normalized_pdf_path is None:
        raise ValueError("normalized_pdf_path is required for extraction and must point to temporary storage.")
    ocr_prepass = dict(acquisition_route.get("ocr_prepass") or {})
    policy = str(ocr_prepass.get("policy", "skip") or "skip")
    tool = str(ocr_prepass.get("tool", "") or "") or None
    should_run = bool(ocr_prepass.get("should_run"))

    selected_pdf_path = original_pdf_path
    pdf_source_kind = "original"
    ocr_prepass_applied = False
    if should_run and tool == "ocrmypdf":
        if normalized_pdf_path.exists():
            selected_pdf_path = normalized_pdf_path
            pdf_source_kind = "ocr_normalized_existing"
            ocr_prepass_applied = True
        elif policy in {"required", "recommended"}:
            normalized_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                generated_pdf_path = run_ocrmypdf_impl(original_pdf_path, normalized_pdf_path)
            except FileNotFoundError:
                if policy == "required":
                    raise
                pdf_source_kind = "original_recommended_ocr_unavailable"
            else:
                selected_pdf_path = generated_pdf_path
                pdf_source_kind = "ocr_normalized_generated"
                ocr_prepass_applied = True

    return {
        "acquisition_route": acquisition_route,
        "selected_pdf_path": selected_pdf_path,
        "original_pdf_path": original_pdf_path,
        "ocr_normalized_pdf_path": normalized_pdf_path,
        "pdf_source_kind": pdf_source_kind,
        "ocr_prepass_policy": policy,
        "ocr_prepass_tool": tool,
        "ocr_prepass_applied": ocr_prepass_applied,
    }


def timed_call(label: str, fn: Any, /, *args: Any, **kwargs: Any) -> tuple[str, float, Any]:
    started = time.perf_counter()
    result = fn(*args, **kwargs)
    return label, round(time.perf_counter() - started, 3), result


def _ocr_prepass_report_payload(pdf_selection: dict[str, Any], *, layout: ProjectLayout | None = None) -> dict[str, Any]:
    return {
        "selected_pdf_path": display_path(pdf_selection["selected_pdf_path"], layout=layout),
        "original_pdf_path": display_path(pdf_selection["original_pdf_path"], layout=layout),
        "ocr_normalized_pdf_path": display_path(pdf_selection["ocr_normalized_pdf_path"], layout=layout),
        "pdf_source_kind": str(pdf_selection["pdf_source_kind"]),
        "ocr_prepass_policy": str(pdf_selection["ocr_prepass_policy"]),
        "ocr_prepass_tool": pdf_selection["ocr_prepass_tool"],
        "ocr_prepass_applied": bool(pdf_selection["ocr_prepass_applied"]),
    }


def build_extraction_sources_for_paper(
    paper_id: str,
    *,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
    layout: ProjectLayout | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    per_paper_source_workers: int = PER_PAPER_SOURCE_WORKERS,
    timed_call_impl: Callable[..., tuple[str, float, Any]] | None = None,
    resolve_extraction_pdf_impl: Callable[..., dict[str, Any]] | None = None,
    build_docling_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_mathpix_sources_impl: Callable[..., dict[str, Any] | None] | None = None,
    build_mathpix_sources_from_result_impl: Callable[..., dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]:
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    timed_call_impl = timed_call_impl or timed_call
    resolve_extraction_pdf_impl = resolve_extraction_pdf_impl or resolve_extraction_pdf
    build_docling_sources_impl = build_docling_sources_impl or build_docling_sources
    build_mathpix_sources_impl = build_mathpix_sources_impl or build_mathpix_sources
    build_mathpix_sources_from_result_impl = build_mathpix_sources_from_result_impl or build_mathpix_sources_from_result

    timings: dict[str, float] = {}
    with tempfile.TemporaryDirectory(prefix=f"{paper_id}-sources-") as temp_dir:
        pdf_selection_started = time.perf_counter()
        pdf_selection = resolve_extraction_pdf_impl(
            paper_id,
            layout=layout,
            normalized_pdf_path=Path(temp_dir) / "ocr-normalized.pdf",
        )
        timings["ocr_prepass_seconds"] = round(time.perf_counter() - pdf_selection_started, 3)
        selected_pdf_path = pdf_selection["selected_pdf_path"]
        acquisition_route = dict(pdf_selection.get("acquisition_route") or {})
        mathpix_enabled = mathpix_credentials_available_impl()
        initial_mathpix_decision = decide_mathpix_execution(
            acquisition_route,
            mathpix_available=mathpix_enabled,
        )
        final_mathpix_decision = initial_mathpix_decision
        eager_mathpix = initial_mathpix_decision.phase == "primary"
        max_workers = 1 if prefetched_mathpix_future is not None else (per_paper_source_workers if eager_mathpix else 1)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            docling_future = executor.submit(
                timed_call_impl,
                "docling",
                build_docling_sources_impl,
                paper_id,
                pdf_path=selected_pdf_path,
                layout=layout,
            )
            local_mathpix_future: Future[tuple[str, float, Any]] | None = None
            if eager_mathpix and prefetched_mathpix_future is None:
                local_mathpix_future = executor.submit(
                    timed_call_impl,
                    "mathpix",
                    build_mathpix_sources_impl,
                    paper_id,
                    pdf_path=selected_pdf_path,
                    layout=layout,
                )

            _, docling_seconds, docling_sources = docling_future.result()
            timings["docling_seconds"] = docling_seconds
            mathpix_sources = None
            mathpix_strategy = "skipped"
            if prefetched_mathpix_future is not None:
                mathpix_strategy = "prefetched_primary"
                mathpix_result = prefetched_mathpix_future.result()
                mathpix_sources = build_mathpix_sources_from_result_impl(
                    paper_id,
                    mathpix_result,
                    pdf_path=selected_pdf_path,
                    layout=layout,
                )
                timings["mathpix_seconds"] = float(mathpix_result.get("elapsed_seconds", 0.0))
            elif local_mathpix_future is not None:
                mathpix_strategy = "parallel_primary"
                _, mathpix_seconds, mathpix_sources = local_mathpix_future.result()
                timings["mathpix_seconds"] = mathpix_seconds
            else:
                final_mathpix_decision = decide_mathpix_execution(
                    acquisition_route,
                    docling_sources=docling_sources,
                    mathpix_available=mathpix_enabled,
                )
                if final_mathpix_decision.phase == "fallback":
                    mathpix_strategy = "fallback_after_docling"
                    _, mathpix_seconds, mathpix_sources = timed_call_impl(
                        "mathpix",
                        build_mathpix_sources_impl,
                        paper_id,
                        pdf_path=selected_pdf_path,
                        layout=layout,
                    )
                    timings["mathpix_seconds"] = mathpix_seconds
                else:
                    timings["mathpix_seconds"] = 0.0

    if initial_mathpix_decision.phase == "primary":
        final_mathpix_decision = initial_mathpix_decision
    execution_plan = build_provider_execution_plan(
        acquisition_route,
        mathpix_decision=final_mathpix_decision,
        mathpix_strategy=mathpix_strategy,
        ocr_prepass_applied=bool(pdf_selection["ocr_prepass_applied"]),
    )
    docling_sources["pdf_selection"] = {
        "selected_pdf_path": str(selected_pdf_path),
        "pdf_source_kind": str(pdf_selection["pdf_source_kind"]),
        "ocr_prepass_policy": str(pdf_selection["ocr_prepass_policy"]),
        "ocr_prepass_tool": pdf_selection["ocr_prepass_tool"],
        "ocr_prepass_applied": bool(pdf_selection["ocr_prepass_applied"]),
    }
    docling_sources["execution_plan"] = execution_plan
    if mathpix_sources is not None:
        mathpix_sources["pdf_selection"] = dict(docling_sources["pdf_selection"])
        mathpix_sources["execution_plan"] = dict(execution_plan)
    return docling_sources, mathpix_sources, timings


def _observation_has_metadata(observation: dict[str, Any] | None) -> bool:
    payload = dict(observation or {})
    return bool(str(payload.get("title", "")).strip() or str(payload.get("abstract", "")).strip())


def _observation_has_references(observation: dict[str, Any] | None) -> bool:
    payload = dict(observation or {})
    return any(str(item).strip() for item in list(payload.get("references", [])))


def _layout_payload_present(payload: dict[str, Any] | None) -> bool:
    candidate = dict(payload or {})
    return bool(list(candidate.get("blocks", [])))


def _math_payload_present(payload: dict[str, Any] | None) -> bool:
    candidate = dict(payload or {})
    return bool(list(candidate.get("entries", [])))


def _selection_candidates(
    *,
    source_scorecard: dict[str, Any],
    kind: str,
    candidates: dict[str, dict[str, Any] | None],
    payload_present: Callable[[dict[str, Any] | None], bool],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_provider, payload in sorted(candidates.items()):
        provider = canonical_provider_name(raw_provider) or str(raw_provider)
        score_row = provider_score_row(source_scorecard, kind=kind, provider=provider) or {}
        rows.append(
            {
                "provider": provider,
                "payload": dict(payload or {}),
                "present": payload_present(payload),
                "accepted": bool(score_row.get("accepted")),
                "overall_score": float(score_row.get("overall_score", 0.0) or 0.0),
                "acceptance_threshold": score_row.get("acceptance_threshold"),
                "rejection_reasons": list(score_row.get("rejection_reasons", [])),
            }
        )
    rows.sort(key=lambda item: (-int(item["accepted"]), -item["overall_score"], item["provider"]))
    return rows


def _selected_candidate(
    candidates: list[dict[str, Any]],
    *,
    preferred_provider: str | None,
) -> dict[str, Any] | None:
    normalized_preferred = canonical_provider_name(preferred_provider)
    if normalized_preferred:
        for candidate in candidates:
            if candidate["provider"] == normalized_preferred:
                return candidate
    return candidates[0] if candidates else None


def _selection_snapshot(
    *,
    owner: str | None,
    status: str,
    basis: str,
    selected: dict[str, Any] | None,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "owner": owner,
        "status": status,
        "basis": basis,
        "accepted": bool((selected or {}).get("accepted")),
        "overall_score": (selected or {}).get("overall_score"),
        "acceptance_threshold": (selected or {}).get("acceptance_threshold"),
        "rejection_reasons": list((selected or {}).get("rejection_reasons", [])),
        "payload": dict((selected or {}).get("payload", {}) or {}),
        "candidates": [
            {
                "provider": candidate["provider"],
                "present": bool(candidate["present"]),
                "accepted": bool(candidate["accepted"]),
                "overall_score": candidate["overall_score"],
                "acceptance_threshold": candidate["acceptance_threshold"],
                "rejection_reasons": list(candidate["rejection_reasons"]),
            }
            for candidate in candidates
        ],
    }


def _select_owned_layout(
    *,
    source_scorecard: dict[str, Any],
    docling_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates = _selection_candidates(
        source_scorecard=source_scorecard,
        kind="layout",
        candidates={"docling": docling_layout, "mathpix": mathpix_layout},
        payload_present=_layout_payload_present,
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        preferred_provider=source_scorecard.get("recommended_primary_layout_provider"),
    )
    if selected is not None:
        basis = "recommended_accepted" if selected["provider"] == canonical_provider_name(source_scorecard.get("recommended_primary_layout_provider")) else "highest_accepted"
        return _selection_snapshot(
            owner=selected["provider"],
            status="selected",
            basis=basis,
            selected=selected,
            candidates=candidates,
        )
    if any(item["present"] for item in candidates):
        return _selection_snapshot(
            owner=None,
            status="rejected",
            basis="no_accepted_layout_owner",
            selected=None,
            candidates=candidates,
        )
    return _selection_snapshot(
        owner=None,
        status="missing",
        basis="no_layout_candidates",
        selected=None,
        candidates=candidates,
    )


def _select_owned_math(
    *,
    source_scorecard: dict[str, Any],
    docling_math: dict[str, Any] | None,
    mathpix_math: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates = _selection_candidates(
        source_scorecard=source_scorecard,
        kind="math",
        candidates={"docling": docling_math, "mathpix": mathpix_math},
        payload_present=_math_payload_present,
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        preferred_provider=source_scorecard.get("recommended_primary_math_provider"),
    )
    if selected is not None:
        basis = "recommended_accepted" if selected["provider"] == canonical_provider_name(source_scorecard.get("recommended_primary_math_provider")) else "highest_accepted"
        return _selection_snapshot(
            owner=selected["provider"],
            status="selected",
            basis=basis,
            selected=selected,
            candidates=candidates,
        )
    if any(item["present"] for item in candidates):
        return _selection_snapshot(
            owner=None,
            status="rejected",
            basis="no_accepted_math_owner",
            selected=None,
            candidates=candidates,
        )
    return {
        **_selection_snapshot(
            owner="none",
            status="missing",
            basis="no_math_candidates",
            selected=None,
            candidates=candidates,
        ),
        "payload": {"engine": "none", "entries": []},
    }


def _select_owned_metadata(
    *,
    source_scorecard: dict[str, Any],
    metadata_candidates: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    candidates = _selection_candidates(
        source_scorecard=source_scorecard,
        kind="metadata",
        candidates=metadata_candidates,
        payload_present=_observation_has_metadata,
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        preferred_provider=source_scorecard.get("recommended_primary_metadata_provider"),
    )
    if selected is not None:
        basis = "recommended_accepted" if selected["provider"] == canonical_provider_name(source_scorecard.get("recommended_primary_metadata_provider")) else "highest_accepted"
        return _selection_snapshot(
            owner=selected["provider"],
            status="selected",
            basis=basis,
            selected=selected,
            candidates=candidates,
        )
    return _selection_snapshot(
        owner=None,
        status="missing" if not any(item["present"] for item in candidates) else "rejected",
        basis="no_accepted_metadata_owner",
        selected=None,
        candidates=candidates,
    )


def _select_owned_references(
    *,
    source_scorecard: dict[str, Any],
    metadata_candidates: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    candidates = _selection_candidates(
        source_scorecard=source_scorecard,
        kind="metadata",
        candidates=metadata_candidates,
        payload_present=_observation_has_references,
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        preferred_provider=source_scorecard.get("recommended_primary_reference_provider"),
    )
    if selected is not None:
        basis = "recommended_accepted" if selected["provider"] == canonical_provider_name(source_scorecard.get("recommended_primary_reference_provider")) else "highest_accepted"
        return _selection_snapshot(
            owner=selected["provider"],
            status="selected",
            basis=basis,
            selected=selected,
            candidates=candidates,
        )
    return _selection_snapshot(
        owner=None,
        status="missing" if not any(item["present"] for item in candidates) else "rejected",
        basis="no_accepted_reference_owner",
        selected=None,
        candidates=candidates,
    )


def _selection_failure_message(kind: str, selection: dict[str, Any]) -> str:
    candidate_summary = ", ".join(
        f"{item['provider']}(accepted={item['accepted']}, present={item['present']}, reasons={item['rejection_reasons']})"
        for item in selection.get("candidates", [])
    )
    return (
        f"No accepted {kind} owner was available. "
        f"basis={selection.get('basis')} candidates=[{candidate_summary}]"
    )


def build_acquisition_follow_up(
    *,
    source_scorecard: dict[str, Any],
    layout_selection: dict[str, Any],
    math_selection: dict[str, Any],
    metadata_selection: dict[str, Any],
    reference_selection: dict[str, Any],
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    selected_layout_provider = str(layout_selection.get("owner", "") or "") or None
    selected_math_provider = str(math_selection.get("owner", "") or "") or None
    selected_metadata_provider = str(metadata_selection.get("owner", "") or "") or None
    selected_reference_provider = str(reference_selection.get("owner", "") or "") or None

    if layout_selection.get("status") == "rejected":
        layout_trial_provider = select_follow_up_provider(
            source_scorecard=source_scorecard,
            kind="layout",
            selected_provider=selected_layout_provider,
        )
        actions.append(
            {"product": "layout", "reason": "layout_provider_not_accepted", "action": "trial_layout_provider" if layout_trial_provider else "manual_review_layout", "target_provider": layout_trial_provider}
        )
    if math_selection.get("status") == "rejected":
        math_trial_provider = select_follow_up_provider(
            source_scorecard=source_scorecard,
            kind="math",
            selected_provider=selected_math_provider,
        )
        actions.append(
            {"product": "math", "reason": "math_provider_not_accepted", "action": "trial_math_provider" if math_trial_provider else "manual_review_math", "target_provider": math_trial_provider}
        )
    if metadata_selection.get("status") == "rejected" and selected_metadata_provider != "grobid":
        actions.append({"product": "metadata", "reason": "metadata_provider_not_accepted", "action": "manual_review_metadata", "target_provider": None})
    if reference_selection.get("status") == "rejected" and selected_reference_provider != "grobid":
        actions.append({"product": "references", "reason": "reference_provider_not_accepted", "action": "manual_review_references", "target_provider": None})
    return {"needs_attention": bool(actions), "actions": actions}


def build_acquisition_execution_summary(
    *,
    acquisition_route: dict[str, Any],
    source_scorecard: dict[str, Any],
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    layout_selection: dict[str, Any],
    math_selection: dict[str, Any],
    metadata_selection: dict[str, Any],
    reference_selection: dict[str, Any],
) -> dict[str, Any]:
    pdf_selection = dict((docling_sources or {}).get("pdf_selection") or (mathpix_sources or {}).get("pdf_selection") or {})
    execution_plan = dict((docling_sources or {}).get("execution_plan") or (mathpix_sources or {}).get("execution_plan") or {})
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    follow_up = build_acquisition_follow_up(
        source_scorecard=source_scorecard,
        layout_selection=layout_selection,
        math_selection=math_selection,
        metadata_selection=metadata_selection,
        reference_selection=reference_selection,
    )
    return {
        "route_primary": acquisition_route.get("primary_route"),
        "route_traits": list(acquisition_route.get("traits", [])),
        "provider_order": list(execution_plan.get("provider_order", [])),
        "available": {
            "layout_candidates": [provider for provider, payload in (("docling", docling_layout), ("mathpix", mathpix_layout)) if payload],
            "math_candidates": [provider for provider, payload in (("docling", docling_math), ("mathpix", mathpix_math)) if payload and list(payload.get("entries", []))],
            "docling_ran": bool(docling_sources),
            "mathpix_ran": bool(mathpix_sources),
            "mathpix_strategy": execution_plan.get("mathpix_strategy"),
            "mathpix_reason": execution_plan.get("mathpix_reason"),
            "mathpix_prefetch_eligible": bool(execution_plan.get("mathpix_prefetch_eligible")),
        },
        "owners": {
            "layout": layout_selection["owner"],
            "math": math_selection["owner"],
            "metadata": metadata_selection["owner"],
            "references": reference_selection["owner"],
        },
        "ownership": {
            "layout": {key: value for key, value in layout_selection.items() if key != "payload"},
            "math": {key: value for key, value in math_selection.items() if key != "payload"},
            "metadata": {key: value for key, value in metadata_selection.items() if key != "payload"},
            "references": {key: value for key, value in reference_selection.items() if key != "payload"},
        },
        "ocr": {
            "policy": pdf_selection.get("ocr_prepass_policy") or (acquisition_route.get("ocr_prepass") or {}).get("policy"),
            "tool": pdf_selection.get("ocr_prepass_tool") or (acquisition_route.get("ocr_prepass") or {}).get("tool"),
            "applied": bool(pdf_selection.get("ocr_prepass_applied")),
            "pdf_source_kind": pdf_selection.get("pdf_source_kind"),
            "selected_pdf_path": pdf_selection.get("selected_pdf_path"),
        },
        "recovery": {
            "layout_composed": False,
            "abstract_placeholder_used": False,
            "page_one_override_used": False,
        },
        "follow_up": follow_up,
    }


def _nonempty_metadata_observation(provider: str, layout_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not layout_payload:
        return None
    observation = derive_metadata_reference_observation_from_layout(provider, layout_payload).to_dict()
    if str(observation.get("title", "")).strip() or str(observation.get("abstract", "")).strip() or any(str(item).strip() for item in observation.get("references", [])):
        return observation
    return None


def compose_external_sources(
    paper_id: str,
    *,
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    layout: ProjectLayout | None = None,
    compose_layout_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    build_source_scorecard_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    compose_layout_sources_impl = compose_layout_sources_impl or compose_layout_sources
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    build_source_scorecard_impl = build_source_scorecard_impl or build_source_scorecard

    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    metadata_candidates = {
        "docling": _nonempty_metadata_observation("docling", docling_layout),
        "grobid": None,
        "mathpix": _nonempty_metadata_observation("mathpix", mathpix_layout),
    }
    source_scorecard = normalize_scorecard_recommendations(
        build_source_scorecard_impl(
            native_layout=None,
            external_layout=None,
            mathpix_layout=None,
            external_math=None,
            layout_candidates={"docling": docling_layout, "mathpix": mathpix_layout},
            math_candidates={"docling": docling_math, "mathpix": mathpix_math},
            route_bias=str(acquisition_route.get("primary_route", "") or ""),
            metadata_observations=metadata_candidates,
        )
    )
    layout_selection = _select_owned_layout(
        source_scorecard=source_scorecard,
        docling_layout=docling_layout,
        mathpix_layout=mathpix_layout,
    )
    if layout_selection["status"] != "selected":
        raise RuntimeError(_selection_failure_message("layout", layout_selection))
    final_layout = compose_layout_sources_impl(
        docling_sources,
        mathpix_sources,
        acquisition_route=acquisition_route,
        source_scorecard=source_scorecard,
    )
    math_selection = _select_owned_math(
        source_scorecard=source_scorecard,
        docling_math=docling_math,
        mathpix_math=mathpix_math,
    )
    if math_selection["status"] == "rejected":
        raise RuntimeError(_selection_failure_message("math", math_selection))
    final_math = dict(math_selection.get("payload") or {"engine": "none", "entries": []})
    metadata_selection = _select_owned_metadata(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    reference_selection = _select_owned_references(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    metadata_observation = dict(metadata_selection.get("payload") or {}) or None
    reference_observation = dict(reference_selection.get("payload") or {}) or None
    acquisition_execution = build_acquisition_execution_summary(
        acquisition_route=acquisition_route,
        source_scorecard=source_scorecard,
        docling_sources=docling_sources,
        mathpix_sources=mathpix_sources,
        layout_selection=layout_selection,
        math_selection=math_selection,
        metadata_selection=metadata_selection,
        reference_selection=reference_selection,
    )
    ocr_prepass = acquisition_route.get("ocr_prepass") or {}
    return {
        "final_layout": final_layout,
        "final_math": final_math,
        "docling_layout": docling_layout,
        "docling_math": docling_math,
        "mathpix_layout": mathpix_layout,
        "mathpix_math": mathpix_math,
        "metadata_candidates": metadata_candidates,
        "metadata_observation": metadata_observation,
        "reference_observation": reference_observation,
        "acquisition_route_payload": acquisition_route,
        "source_scorecard": source_scorecard,
        "acquisition_execution": acquisition_execution,
        "layout_owner": layout_selection["owner"],
        "math_owner": math_selection["owner"],
        "metadata_owner": metadata_selection["owner"],
        "reference_owner": reference_selection["owner"],
        "ownership": acquisition_execution["ownership"],
        "layout_engine": layout_selection["owner"] or "none",
        "layout_blocks": len(final_layout.get("blocks", [])),
        "math_engine": math_selection["owner"] or "none",
        "math_entries": len(final_math.get("entries", [])),
        "recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
        "recommended_primary_math_provider": source_scorecard.get("recommended_primary_math_provider"),
        "recommended_primary_metadata_provider": source_scorecard.get("recommended_primary_metadata_provider"),
        "recommended_primary_reference_provider": source_scorecard.get("recommended_primary_reference_provider"),
        "executed_layout_provider": layout_selection["owner"],
        "executed_math_provider": math_selection["owner"],
        "executed_metadata_provider": metadata_selection["owner"],
        "executed_reference_provider": reference_selection["owner"],
        "follow_up_needed": bool((acquisition_execution.get("follow_up") or {}).get("needs_attention")),
        "follow_up_actions": list((acquisition_execution.get("follow_up") or {}).get("actions") or []),
        "acquisition_route": acquisition_route.get("primary_route"),
        "ocr_prepass_policy": ocr_prepass.get("policy"),
        "ocr_prepass_should_run": bool(ocr_prepass.get("should_run")),
        "ocr_prepass_tool": ocr_prepass.get("tool"),
    }


def write_canonical_outputs_for_run(
    paper_id: str,
    document: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
    write_canonical_outputs_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    write_canonical_outputs_impl = write_canonical_outputs_impl or write_canonical_outputs
    return write_canonical_outputs_impl(paper_id, document, include_review=True, layout=layout)


__all__ = [
    "PER_PAPER_SOURCE_WORKERS",
    "build_docling_sources",
    "build_extraction_sources_for_paper",
    "build_mathpix_sources",
    "build_mathpix_sources_from_result",
    "compose_external_sources",
    "mathpix_prefetch_allowed",
    "resolve_extraction_pdf",
    "timed_call",
    "write_canonical_outputs_for_run",
]
