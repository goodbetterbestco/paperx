from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.providers import build_provider_execution_plan, decide_mathpix_execution
from pipeline.acquisition.providers import derive_metadata_reference_observation_from_layout
from pipeline.acquisition.scoring import (
    evaluate_layout_candidate,
    evaluate_math_candidate,
    evaluate_metadata_candidate,
)
from pipeline.corpus_layout import ProjectLayout, paper_pdf_path
from pipeline.processor.settings import docling_device, mathpix_credentials_available
from pipeline.output.artifacts import write_canonical_outputs
from pipeline.sources.docling import docling_json_to_external_sources, run_docling
from pipeline.sources.mathpix import mathpix_pages_to_external_sources, run_mathpix

PER_PAPER_SOURCE_WORKERS = 2


def _canonical_provider_name(provider: str | None) -> str | None:
    normalized = str(provider or "").strip()
    if not normalized:
        return None
    lowered = normalized.lower()
    if lowered in {"mathpix", "mathpix_layout"} or lowered.startswith("mathpix"):
        return "mathpix"
    if lowered == "docling" or lowered.startswith("docling"):
        return "docling"
    if lowered == "native_pdf":
        return "native_pdf"
    return normalized


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


def timed_call(label: str, fn: Any, /, *args: Any, **kwargs: Any) -> tuple[str, float, Any]:
    started = time.perf_counter()
    result = fn(*args, **kwargs)
    return label, round(time.perf_counter() - started, 3), result


def build_extraction_sources_for_paper(
    paper_id: str,
    *,
    acquisition_route: dict[str, Any],
    layout: ProjectLayout | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    per_paper_source_workers: int = PER_PAPER_SOURCE_WORKERS,
    timed_call_impl: Callable[..., tuple[str, float, Any]] | None = None,
    build_docling_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_mathpix_sources_impl: Callable[..., dict[str, Any] | None] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]:
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    timed_call_impl = timed_call_impl or timed_call
    build_docling_sources_impl = build_docling_sources_impl or build_docling_sources
    build_mathpix_sources_impl = build_mathpix_sources_impl or build_mathpix_sources

    timings: dict[str, float] = {}
    selected_pdf_path = paper_pdf_path(paper_id, layout=layout)
    route_payload = dict(acquisition_route or {})
    mathpix_decision = decide_mathpix_execution(
        route_payload,
        mathpix_available=mathpix_credentials_available_impl(),
    )
    max_workers = per_paper_source_workers if mathpix_decision.requested else 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        docling_future = executor.submit(
            timed_call_impl,
            "docling",
            build_docling_sources_impl,
            paper_id,
            pdf_path=selected_pdf_path,
            layout=layout,
        )
        mathpix_future = None
        if mathpix_decision.requested:
            mathpix_future = executor.submit(
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
        if mathpix_future is not None:
            _, mathpix_seconds, mathpix_sources = mathpix_future.result()
            timings["mathpix_seconds"] = mathpix_seconds
        else:
            timings["mathpix_seconds"] = 0.0

    execution_plan = build_provider_execution_plan(
        route_payload,
        mathpix_decision=mathpix_decision,
    )
    docling_sources["execution_plan"] = execution_plan
    if mathpix_sources is not None:
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
    candidates: dict[str, dict[str, Any] | None],
    payload_present: Callable[[dict[str, Any] | None], bool],
    evaluate_candidate: Callable[[str, dict[str, Any] | None], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_provider, payload in sorted(candidates.items()):
        provider = _canonical_provider_name(raw_provider) or str(raw_provider)
        evaluation = evaluate_candidate(provider, payload)
        rows.append(
            {
                "provider": provider,
                "payload": dict(payload or {}),
                "present": payload_present(payload),
                "accepted": bool(evaluation.get("accepted")),
                "overall_score": float(evaluation.get("overall_score", 0.0) or 0.0),
                "acceptance_threshold": evaluation.get("acceptance_threshold"),
                "rejection_reasons": list(evaluation.get("rejection_reasons", [])),
            }
        )
    rows.sort(key=lambda item: (-int(item["accepted"]), -item["overall_score"], item["provider"]))
    return rows


def _route_provider_priority(
    acquisition_route: dict[str, Any],
    *,
    field: str,
) -> list[str]:
    providers: list[str] = []
    for item in list((acquisition_route or {}).get(field) or []):
        provider = _canonical_provider_name(str(item).strip())
        if provider and provider not in providers:
            providers.append(provider)
    return providers


def _fixed_provider_priority(*providers: str) -> list[str]:
    ordered: list[str] = []
    for raw_provider in providers:
        provider = _canonical_provider_name(raw_provider)
        if provider and provider not in ordered:
            ordered.append(provider)
    return ordered


def _selected_candidate(
    candidates: list[dict[str, Any]],
    *,
    provider_priority: list[str],
) -> dict[str, Any] | None:
    if not candidates:
        return None
    if not provider_priority:
        return candidates[0]
    priority_index = {provider: index for index, provider in enumerate(provider_priority)}
    ranked_candidates = sorted(
        candidates,
        key=lambda item: (
            priority_index.get(item["provider"], len(priority_index)),
            -item["overall_score"],
            item["provider"],
        ),
    )
    return ranked_candidates[0]


def _selection_basis(selected: dict[str, Any], *, provider_priority: list[str]) -> str:
    if selected["provider"] in provider_priority:
        return "route_priority_accepted"
    return "highest_accepted"


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
    acquisition_route: dict[str, Any],
    docling_layout: dict[str, Any] | None,
    mathpix_layout: dict[str, Any] | None,
    docling_math: dict[str, Any] | None,
    mathpix_math: dict[str, Any] | None,
) -> dict[str, Any]:
    math_candidates = {
        "docling": docling_math,
        "mathpix": mathpix_math,
    }
    candidates = _selection_candidates(
        candidates={"docling": docling_layout, "mathpix": mathpix_layout},
        payload_present=_layout_payload_present,
        evaluate_candidate=lambda provider, payload: evaluate_layout_candidate(
            provider,
            payload,
            math_entry_count=len(list((math_candidates.get(provider) or {}).get("entries", []))),
        ),
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        provider_priority=_route_provider_priority(acquisition_route, field="layout_priority"),
    )
    if selected is not None:
        basis = _selection_basis(
            selected,
            provider_priority=_route_provider_priority(acquisition_route, field="layout_priority"),
        )
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
    acquisition_route: dict[str, Any],
    docling_math: dict[str, Any] | None,
    mathpix_math: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates = _selection_candidates(
        candidates={"docling": docling_math, "mathpix": mathpix_math},
        payload_present=_math_payload_present,
        evaluate_candidate=lambda provider, payload: evaluate_math_candidate(
            provider,
            payload,
        ),
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    selected = _selected_candidate(
        accepted_candidates,
        provider_priority=_route_provider_priority(acquisition_route, field="math_priority"),
    )
    if selected is not None:
        basis = _selection_basis(
            selected,
            provider_priority=_route_provider_priority(acquisition_route, field="math_priority"),
        )
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
    metadata_candidates: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    candidates = _selection_candidates(
        candidates=metadata_candidates,
        payload_present=_observation_has_metadata,
        evaluate_candidate=lambda provider, payload: evaluate_metadata_candidate(
            provider,
            payload,
        ),
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    provider_priority = _fixed_provider_priority("docling", "mathpix")
    selected = _selected_candidate(
        accepted_candidates,
        provider_priority=provider_priority,
    )
    if selected is not None:
        basis = _selection_basis(
            selected,
            provider_priority=provider_priority,
        )
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
    metadata_candidates: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    candidates = _selection_candidates(
        candidates=metadata_candidates,
        payload_present=_observation_has_references,
        evaluate_candidate=lambda provider, payload: evaluate_metadata_candidate(
            provider,
            payload,
        ),
    )
    accepted_candidates = [item for item in candidates if item["present"] and item["accepted"]]
    provider_priority = _fixed_provider_priority("docling", "mathpix")
    selected = _selected_candidate(
        accepted_candidates,
        provider_priority=provider_priority,
    )
    if selected is not None:
        basis = _selection_basis(
            selected,
            provider_priority=provider_priority,
        )
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


def build_acquisition_execution_summary(
    *,
    acquisition_route: dict[str, Any],
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    layout_selection: dict[str, Any],
    math_selection: dict[str, Any],
    metadata_selection: dict[str, Any],
    reference_selection: dict[str, Any],
) -> dict[str, Any]:
    execution_plan = dict((docling_sources or {}).get("execution_plan") or (mathpix_sources or {}).get("execution_plan") or {})
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    return {
        "route_traits": list(acquisition_route.get("traits", [])),
        "layout_priority": list(acquisition_route.get("layout_priority", [])),
        "math_priority": list(acquisition_route.get("math_priority", [])),
        "provider_order": list(execution_plan.get("provider_order", [])),
        "available": {
            "layout_candidates": [provider for provider, payload in (("docling", docling_layout), ("mathpix", mathpix_layout)) if payload],
            "math_candidates": [provider for provider, payload in (("docling", docling_math), ("mathpix", mathpix_math)) if payload and list(payload.get("entries", []))],
            "docling_ran": bool(docling_sources),
            "mathpix_ran": bool(mathpix_sources),
            "mathpix_requested": bool(execution_plan.get("mathpix_requested")),
            "mathpix_reason": execution_plan.get("mathpix_reason"),
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
        "recovery": {
            "layout_composed": False,
            "abstract_placeholder_used": False,
            "page_one_override_used": False,
        },
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
    acquisition_route: dict[str, Any],
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
) -> dict[str, Any]:
    route_payload = dict(acquisition_route or {})
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    metadata_candidates = {
        "docling": _nonempty_metadata_observation("docling", docling_layout),
        "mathpix": _nonempty_metadata_observation("mathpix", mathpix_layout),
    }
    layout_selection = _select_owned_layout(
        acquisition_route=route_payload,
        docling_layout=docling_layout,
        mathpix_layout=mathpix_layout,
        docling_math=docling_math,
        mathpix_math=mathpix_math,
    )
    if layout_selection["status"] != "selected":
        raise RuntimeError(_selection_failure_message("layout", layout_selection))
    final_layout = dict(layout_selection.get("payload") or {})
    math_selection = _select_owned_math(
        acquisition_route=route_payload,
        docling_math=docling_math,
        mathpix_math=mathpix_math,
    )
    if math_selection["status"] == "rejected":
        raise RuntimeError(_selection_failure_message("math", math_selection))
    final_math = dict(math_selection.get("payload") or {"engine": "none", "entries": []})
    metadata_selection = _select_owned_metadata(
        metadata_candidates=metadata_candidates,
    )
    reference_selection = _select_owned_references(
        metadata_candidates=metadata_candidates,
    )
    metadata_observation = dict(metadata_selection.get("payload") or {}) or None
    reference_observation = dict(reference_selection.get("payload") or {}) or None
    acquisition_execution = build_acquisition_execution_summary(
        acquisition_route=route_payload,
        docling_sources=docling_sources,
        mathpix_sources=mathpix_sources,
        layout_selection=layout_selection,
        math_selection=math_selection,
        metadata_selection=metadata_selection,
        reference_selection=reference_selection,
    )
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
        "acquisition_route_payload": route_payload,
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
    "timed_call",
    "write_canonical_outputs_for_run",
]
