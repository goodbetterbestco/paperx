from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.providers import derive_metadata_reference_observation_from_layout
from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.acquisition.source_ownership import (
    normalize_scorecard_recommendations,
    reported_layout_provider,
    reported_math_provider,
    select_follow_up_provider,
    select_metadata_observation,
    select_reference_observation,
    select_math_payload,
)
from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout
from pipeline.corpus_layout import canonical_sources_dir
from pipeline.orchestrator.round_build import build_best_paper
from pipeline.orchestrator.round_document import anomaly_flags, document_quality_key
from pipeline.orchestrator.round_runtime import write_json
from pipeline.orchestrator.source_composition import compose_layout_sources
from pipeline.output.artifacts import write_canonical_outputs
from pipeline.output.validation import validate_canonical
from pipeline.reconcile.entrypoint import reconcile_paper
from pipeline.sources.external import (
    acquisition_execution_report_path,
    external_layout_path,
    external_math_path,
    load_docling_metadata_observation,
    load_grobid_metadata_observation,
    load_mathpix_metadata_observation,
    ocr_prepass_report_path,
)


def _observation_has_metadata(observation: dict[str, Any] | None) -> bool:
    payload = dict(observation or {})
    return bool(str(payload.get("title", "")).strip() or str(payload.get("abstract", "")).strip())


def _observation_has_references(observation: dict[str, Any] | None) -> bool:
    payload = dict(observation or {})
    return any(str(item).strip() for item in list(payload.get("references", [])))


def build_acquisition_follow_up(
    *,
    source_scorecard: dict[str, Any],
    selected_layout_provider: str | None,
    selected_math_provider: str | None,
    metadata_candidates: dict[str, dict[str, Any] | None] | None,
    metadata_observation: dict[str, Any] | None,
    reference_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    layout_basis = str(source_scorecard.get("layout_recommendation_basis", "") or "")
    math_basis = str(source_scorecard.get("math_recommendation_basis", "") or "")
    metadata_basis = str(source_scorecard.get("metadata_recommendation_basis", "") or "")
    reference_basis = str(source_scorecard.get("reference_recommendation_basis", "") or "")
    selected_metadata_provider = str((metadata_observation or {}).get("provider", "") or "") or None
    selected_reference_provider = str((reference_observation or {}).get("provider", "") or "") or None
    candidates = {str(key): dict(value or {}) for key, value in (metadata_candidates or {}).items()}
    grobid_candidate = candidates.get("grobid") or {}

    if layout_basis == "fallback_unaccepted":
        layout_trial_provider = select_follow_up_provider(
            source_scorecard=source_scorecard,
            kind="layout",
            selected_provider=selected_layout_provider,
        )
        actions.append(
            {
                "product": "layout",
                "reason": "layout_provider_not_accepted",
                "action": "trial_layout_provider" if layout_trial_provider else "manual_review_layout",
                "target_provider": layout_trial_provider,
            }
        )

    if math_basis == "fallback_unaccepted":
        math_trial_provider = select_follow_up_provider(
            source_scorecard=source_scorecard,
            kind="math",
            selected_provider=selected_math_provider,
        )
        actions.append(
            {
                "product": "math",
                "reason": "math_provider_not_accepted",
                "action": "trial_math_provider" if math_trial_provider else "manual_review_math",
                "target_provider": math_trial_provider,
            }
        )

    if metadata_basis == "fallback_unaccepted":
        if selected_metadata_provider == "grobid":
            pass
        elif _observation_has_metadata(grobid_candidate):
            actions.append(
                {
                    "product": "metadata",
                    "reason": "metadata_provider_not_accepted",
                    "action": "escalate_grobid_metadata",
                    "target_provider": "grobid",
                }
            )
        else:
            actions.append(
                {
                    "product": "metadata",
                    "reason": "metadata_provider_not_accepted",
                    "action": "manual_review_metadata",
                    "target_provider": None,
                }
            )

    if reference_basis == "fallback_unaccepted":
        if selected_reference_provider == "grobid":
            pass
        elif _observation_has_references(grobid_candidate):
            actions.append(
                {
                    "product": "references",
                    "reason": "reference_provider_not_accepted",
                    "action": "escalate_grobid_references",
                    "target_provider": "grobid",
                }
            )
        else:
            actions.append(
                {
                    "product": "references",
                    "reason": "reference_provider_not_accepted",
                    "action": "manual_review_references",
                    "target_provider": None,
                }
            )

    return {
        "needs_attention": bool(actions),
        "actions": actions,
    }


def build_acquisition_execution_summary(
    *,
    acquisition_route: dict[str, Any],
    source_scorecard: dict[str, Any],
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    final_layout: dict[str, Any],
    final_math: dict[str, Any],
    metadata_candidates: dict[str, dict[str, Any] | None] | None,
    metadata_observation: dict[str, Any] | None,
    reference_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    pdf_selection = dict((docling_sources or {}).get("pdf_selection") or (mathpix_sources or {}).get("pdf_selection") or {})
    execution_plan = dict((docling_sources or {}).get("execution_plan") or (mathpix_sources or {}).get("execution_plan") or {})
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    metadata_provider = str((metadata_observation or {}).get("provider", "") or "") or None
    reference_provider = str((reference_observation or {}).get("provider", "") or "") or None
    selected_layout_provider = reported_layout_provider(
        str(final_layout.get("engine", "") or "") or None,
        source_scorecard=source_scorecard,
        fallback="none",
    )
    selected_math_provider = reported_math_provider(
        str(final_math.get("engine", "") or "") or None,
        source_scorecard=source_scorecard,
        math_payload=final_math,
        fallback="none",
    )
    executed_layout_candidates = [
        provider
        for provider, payload in (
            ("docling", docling_layout),
            ("mathpix", mathpix_layout),
        )
        if payload
    ]
    executed_math_candidates = [
        provider
        for provider, payload in (
            ("docling", docling_math),
            ("mathpix", mathpix_math),
        )
        if payload and list(payload.get("entries", []))
    ]
    executed_metadata_candidates = [
        provider
        for provider, payload in sorted((metadata_candidates or {}).items())
        if payload
    ]
    follow_up = build_acquisition_follow_up(
        source_scorecard=source_scorecard,
        selected_layout_provider=selected_layout_provider,
        selected_math_provider=selected_math_provider,
        metadata_candidates=metadata_candidates,
        metadata_observation=metadata_observation,
        reference_observation=reference_observation,
    )
    return {
        "route_primary": acquisition_route.get("primary_route"),
        "route_traits": list(acquisition_route.get("traits", [])),
        "provider_order": list(execution_plan.get("provider_order", [])),
        "recommended": {
            "layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
            "math_provider": source_scorecard.get("recommended_primary_math_provider"),
            "metadata_provider": source_scorecard.get("recommended_primary_metadata_provider"),
            "reference_provider": source_scorecard.get("recommended_primary_reference_provider"),
            "layout_basis": source_scorecard.get("layout_recommendation_basis"),
            "math_basis": source_scorecard.get("math_recommendation_basis"),
            "metadata_basis": source_scorecard.get("metadata_recommendation_basis"),
            "reference_basis": source_scorecard.get("reference_recommendation_basis"),
        },
        "executed": {
            "layout_candidates": executed_layout_candidates,
            "math_candidates": executed_math_candidates,
            "selected_layout_provider": selected_layout_provider,
            "selected_math_provider": selected_math_provider,
            "metadata_provider": metadata_provider,
            "reference_provider": reference_provider,
            "metadata_candidates": executed_metadata_candidates,
            "docling_ran": bool(docling_sources),
            "mathpix_ran": bool(mathpix_sources),
            "mathpix_strategy": execution_plan.get("mathpix_strategy"),
            "mathpix_reason": execution_plan.get("mathpix_reason"),
            "mathpix_prefetch_eligible": bool(execution_plan.get("mathpix_prefetch_eligible")),
        },
        "ocr": {
            "policy": pdf_selection.get("ocr_prepass_policy") or (acquisition_route.get("ocr_prepass") or {}).get("policy"),
            "tool": pdf_selection.get("ocr_prepass_tool") or (acquisition_route.get("ocr_prepass") or {}).get("tool"),
            "applied": bool(pdf_selection.get("ocr_prepass_applied")),
            "pdf_source_kind": pdf_selection.get("pdf_source_kind"),
            "selected_pdf_path": pdf_selection.get("selected_pdf_path"),
        },
        "follow_up": follow_up,
    }


def _nonempty_metadata_observation(
    provider: str,
    layout_payload: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not layout_payload:
        return None
    observation = derive_metadata_reference_observation_from_layout(provider, layout_payload).to_dict()
    if (
        str(observation.get("title", "")).strip()
        or str(observation.get("abstract", "")).strip()
        or any(str(item).strip() for item in observation.get("references", []))
    ):
        return observation
    return None


def compose_external_sources(
    paper_id: str,
    *,
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    layout: ProjectLayout | None = None,
    compose_layout_sources_impl: Callable[[dict[str, Any] | None, dict[str, Any] | None], dict[str, Any]] | None = None,
    external_layout_path_impl: Callable[..., Path] | None = None,
    external_math_path_impl: Callable[..., Path] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
    acquisition_execution_report_path_impl: Callable[..., Path] | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    build_source_scorecard_impl: Callable[..., dict[str, Any]] | None = None,
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    compose_layout_sources_impl = compose_layout_sources_impl or compose_layout_sources
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    external_math_path_impl = external_math_path_impl or external_math_path
    write_json_impl = write_json_impl or write_json
    acquisition_execution_report_path_impl = acquisition_execution_report_path_impl or acquisition_execution_report_path
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    build_source_scorecard_impl = build_source_scorecard_impl or build_source_scorecard
    load_grobid_metadata_observation_impl = (
        load_grobid_metadata_observation_impl or load_grobid_metadata_observation
    )

    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    primary_route = str(acquisition_route.get("primary_route", "") or "")
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    metadata_candidates = {
        "docling": _nonempty_metadata_observation("docling", docling_layout),
        "grobid": load_grobid_metadata_observation_impl(paper_id, layout=layout),
        "mathpix": _nonempty_metadata_observation("mathpix", mathpix_layout),
    }
    try:
        source_scorecard = build_source_scorecard_impl(
            native_layout=None,
            external_layout=None,
            mathpix_layout=None,
            external_math=None,
            layout_candidates={
                "docling": docling_layout,
                "mathpix": mathpix_layout,
            },
            math_candidates={
                "docling": docling_math,
                "mathpix": mathpix_math,
            },
            route_bias=primary_route,
            metadata_observations=metadata_candidates,
        )
    except TypeError:
        source_scorecard = build_source_scorecard_impl(
            native_layout=None,
            external_layout=docling_layout,
            mathpix_layout=mathpix_layout,
            external_math=mathpix_math or docling_math,
            route_bias=primary_route,
            metadata_observations=metadata_candidates,
        )
    source_scorecard = normalize_scorecard_recommendations(source_scorecard)
    metadata_observation = select_metadata_observation(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    reference_observation = select_reference_observation(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    try:
        final_layout = compose_layout_sources_impl(
            docling_sources,
            mathpix_sources,
            acquisition_route=acquisition_route,
            source_scorecard=source_scorecard,
        )
    except TypeError:
        final_layout = compose_layout_sources_impl(docling_sources, mathpix_sources)
    final_math = select_math_payload(
        source_scorecard=source_scorecard,
        docling_math=docling_math,
        mathpix_math=mathpix_math,
    )
    layout_path = external_layout_path_impl(paper_id, layout=layout)
    math_path = external_math_path_impl(paper_id, layout=layout)
    write_json_impl(layout_path, final_layout)
    write_json_impl(math_path, final_math)
    sources_dir = layout_path.parent
    write_json_impl(sources_dir / "acquisition-route.json", acquisition_route)
    write_json_impl(sources_dir / "source-scorecard.json", source_scorecard)
    acquisition_execution = build_acquisition_execution_summary(
        acquisition_route=acquisition_route,
        source_scorecard=source_scorecard,
        docling_sources=docling_sources,
        mathpix_sources=mathpix_sources,
        final_layout=final_layout,
        final_math=final_math,
        metadata_candidates=metadata_candidates,
        metadata_observation=metadata_observation,
        reference_observation=reference_observation,
    )
    write_json_impl(acquisition_execution_report_path_impl(paper_id, layout=layout), acquisition_execution)
    ocr_prepass = acquisition_route.get("ocr_prepass") or {}
    return {
        "layout_path": str(layout_path),
        "math_path": str(math_path),
        "acquisition_execution_path": str(acquisition_execution_report_path_impl(paper_id, layout=layout)),
        "layout_engine": reported_layout_provider(
            str(final_layout.get("engine", "") or "") or None,
            source_scorecard=source_scorecard,
            fallback="none",
        ),
        "layout_blocks": len(final_layout.get("blocks", [])),
        "math_engine": reported_math_provider(
            str(final_math.get("engine", "") or "") or None,
            source_scorecard=source_scorecard,
            math_payload=final_math,
            fallback="none",
        ),
        "math_entries": len(final_math.get("entries", [])),
        "recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
        "recommended_primary_math_provider": source_scorecard.get("recommended_primary_math_provider"),
        "recommended_primary_metadata_provider": source_scorecard.get("recommended_primary_metadata_provider"),
        "recommended_primary_reference_provider": source_scorecard.get("recommended_primary_reference_provider"),
        "executed_layout_provider": acquisition_execution["executed"]["selected_layout_provider"],
        "executed_math_provider": acquisition_execution["executed"]["selected_math_provider"],
        "executed_metadata_provider": acquisition_execution["executed"]["metadata_provider"],
        "executed_reference_provider": acquisition_execution["executed"]["reference_provider"],
        "follow_up_needed": bool((acquisition_execution.get("follow_up") or {}).get("needs_attention")),
        "follow_up_actions": list((acquisition_execution.get("follow_up") or {}).get("actions") or []),
        "acquisition_route": acquisition_route.get("primary_route"),
        "ocr_prepass_policy": ocr_prepass.get("policy"),
        "ocr_prepass_should_run": bool(ocr_prepass.get("should_run")),
        "ocr_prepass_tool": ocr_prepass.get("tool"),
    }


def write_round_canonical_outputs(
    paper_id: str,
    document: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
    write_canonical_outputs_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    write_canonical_outputs_impl = write_canonical_outputs_impl or write_canonical_outputs
    return write_canonical_outputs_impl(paper_id, document, include_review=True, layout=layout)


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def paper_has_generated_abstract_file(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    canonical_sources_dir_impl: Callable[..., Path] | None = None,
) -> bool:
    canonical_sources_dir_impl = canonical_sources_dir_impl or canonical_sources_dir
    return (canonical_sources_dir_impl(paper_id, layout=layout) / "generated-abstract.txt").exists()


def preserve_existing_generated_abstract_file(
    paper_id: str,
    existing_document: dict[str, Any] | None,
    new_document: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
    preserve_existing_generated_abstract_file_impl: Callable[..., bool] | None = None,
    paper_has_generated_abstract_file_impl: Callable[..., bool] | None = None,
) -> bool:
    from pipeline.orchestrator.round_document import preserve_existing_generated_abstract_file as _preserve_generated_abstract_file

    preserve_existing_generated_abstract_file_impl = (
        preserve_existing_generated_abstract_file_impl or _preserve_generated_abstract_file
    )
    paper_has_generated_abstract_file_impl = paper_has_generated_abstract_file_impl or paper_has_generated_abstract_file
    return preserve_existing_generated_abstract_file_impl(
        paper_id,
        existing_document,
        new_document,
        abstract_file_exists=lambda current_paper_id: paper_has_generated_abstract_file_impl(
            current_paper_id,
            layout=layout,
        ),
    )


def existing_composed_sources(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    load_json_if_exists_impl: Callable[[Path], dict[str, Any] | None] | None = None,
    external_layout_path_impl: Callable[..., Path] | None = None,
    external_math_path_impl: Callable[..., Path] | None = None,
    ocr_prepass_report_path_impl: Callable[..., Path] | None = None,
    acquisition_execution_report_path_impl: Callable[..., Path] | None = None,
    load_docling_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_mathpix_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    load_json_if_exists_impl = load_json_if_exists_impl or load_json_if_exists
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    external_math_path_impl = external_math_path_impl or external_math_path
    ocr_prepass_report_path_impl = ocr_prepass_report_path_impl or ocr_prepass_report_path
    acquisition_execution_report_path_impl = acquisition_execution_report_path_impl or acquisition_execution_report_path
    load_docling_metadata_observation_impl = (
        load_docling_metadata_observation_impl or load_docling_metadata_observation
    )
    load_grobid_metadata_observation_impl = (
        load_grobid_metadata_observation_impl or load_grobid_metadata_observation
    )
    load_mathpix_metadata_observation_impl = (
        load_mathpix_metadata_observation_impl or load_mathpix_metadata_observation
    )
    external_layout = load_json_if_exists_impl(external_layout_path_impl(paper_id, layout=layout)) or {
        "engine": "none",
        "blocks": [],
    }
    math = load_json_if_exists_impl(external_math_path_impl(paper_id, layout=layout)) or {
        "engine": "none",
        "entries": [],
    }
    sources_dir = external_layout_path_impl(paper_id, layout=layout).parent
    acquisition_route = load_json_if_exists_impl(sources_dir / "acquisition-route.json") or {}
    source_scorecard = load_json_if_exists_impl(sources_dir / "source-scorecard.json") or {}
    ocr_prepass = load_json_if_exists_impl(ocr_prepass_report_path_impl(paper_id, layout=layout)) or {}
    acquisition_execution = (
        load_json_if_exists_impl(acquisition_execution_report_path_impl(paper_id, layout=layout)) or {}
    )
    metadata_candidates = {
        "docling": load_docling_metadata_observation_impl(paper_id, layout=layout),
        "grobid": load_grobid_metadata_observation_impl(paper_id, layout=layout),
        "mathpix": load_mathpix_metadata_observation_impl(paper_id, layout=layout),
    }
    metadata_observation = select_metadata_observation(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    reference_observation = select_reference_observation(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    route_ocr_prepass = acquisition_route.get("ocr_prepass") or {}
    return {
        "layout_path": str(external_layout_path_impl(paper_id, layout=layout)),
        "math_path": str(external_math_path_impl(paper_id, layout=layout)),
        "layout_engine": reported_layout_provider(
            str(external_layout.get("engine", "") or "") or None,
            source_scorecard=source_scorecard,
            fallback="none",
        ),
        "layout_blocks": len(external_layout.get("blocks", [])),
        "math_engine": reported_math_provider(
            str(math.get("engine", "") or "") or None,
            source_scorecard=source_scorecard,
            math_payload=math,
            fallback="none",
        ),
        "math_entries": len(math.get("entries", [])),
        "acquisition_route": acquisition_route.get("primary_route"),
        "ocr_prepass_policy": ocr_prepass.get("ocr_prepass_policy") or route_ocr_prepass.get("policy"),
        "ocr_prepass_should_run": bool(route_ocr_prepass.get("should_run")),
        "ocr_prepass_tool": ocr_prepass.get("ocr_prepass_tool") or route_ocr_prepass.get("tool"),
        "ocr_prepass_applied": bool(ocr_prepass.get("ocr_prepass_applied")),
        "pdf_source_kind": ocr_prepass.get("pdf_source_kind"),
        "selected_pdf_path": ocr_prepass.get("selected_pdf_path"),
        "recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
        "recommended_primary_math_provider": source_scorecard.get("recommended_primary_math_provider"),
        "recommended_primary_metadata_provider": source_scorecard.get("recommended_primary_metadata_provider"),
        "recommended_primary_reference_provider": source_scorecard.get("recommended_primary_reference_provider"),
        "executed_layout_provider": ((acquisition_execution.get("executed") or {}).get("selected_layout_provider")),
        "executed_math_provider": ((acquisition_execution.get("executed") or {}).get("selected_math_provider")),
        "executed_metadata_provider": ((acquisition_execution.get("executed") or {}).get("metadata_provider")),
        "executed_reference_provider": ((acquisition_execution.get("executed") or {}).get("reference_provider")),
        "follow_up_needed": bool((acquisition_execution.get("follow_up") or {}).get("needs_attention")),
        "follow_up_actions": list((acquisition_execution.get("follow_up") or {}).get("actions") or []),
        "metadata_provider": metadata_observation.get("provider"),
        "reference_provider": reference_observation.get("provider"),
    }


def build_best_round_paper(
    paper_id: str,
    *,
    layout: ProjectLayout,
    build_best_paper_impl: Callable[..., dict[str, Any]] | None = None,
    build_pipeline_config_impl: Callable[..., Any] | None = None,
    reconcile_paper_impl: Callable[..., dict[str, Any]] | None = None,
    validate_canonical_impl: Callable[[dict[str, Any]], None] | None = None,
    anomaly_flags_impl: Callable[[dict[str, Any]], list[str]] | None = None,
    document_quality_key_impl: Callable[[dict[str, Any], int], Any] | None = None,
    existing_composed_sources_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    build_best_paper_impl = build_best_paper_impl or build_best_paper
    build_pipeline_config_impl = build_pipeline_config_impl or build_pipeline_config
    reconcile_paper_impl = reconcile_paper_impl or reconcile_paper
    validate_canonical_impl = validate_canonical_impl or validate_canonical
    anomaly_flags_impl = anomaly_flags_impl or anomaly_flags
    document_quality_key_impl = document_quality_key_impl or document_quality_key
    existing_composed_sources_impl = existing_composed_sources_impl or existing_composed_sources
    composed_sources = existing_composed_sources_impl(paper_id, layout=layout)
    layout_blocks = int(composed_sources.get("layout_blocks", 0) or 0)
    math_entries = int(composed_sources.get("math_entries", 0) or 0)
    primary_route = str(composed_sources.get("acquisition_route", "") or "")
    preferred_text_engine = "hybrid" if primary_route in {"scan_or_image_heavy", "degraded_or_garbled"} else "native"

    if layout_blocks <= 0 and math_entries <= 0:
        mode_configs = (
            {"use_external_layout": True, "use_external_math": True, "text_engine": "native", "label": "hybrid"},
            {"use_external_layout": True, "use_external_math": False, "text_engine": "native", "label": "layout_only"},
            {"use_external_layout": False, "use_external_math": False, "text_engine": "native", "label": "native"},
        )
    else:
        dynamic_mode_configs: list[dict[str, Any]] = []
        if layout_blocks > 0 and math_entries > 0:
            dynamic_mode_configs.append(
                {
                    "use_external_layout": True,
                    "use_external_math": True,
                    "text_engine": preferred_text_engine,
                    "label": "hybrid",
                }
            )
        if layout_blocks > 0:
            dynamic_mode_configs.append(
                {
                    "use_external_layout": True,
                    "use_external_math": False,
                    "text_engine": preferred_text_engine,
                    "label": "layout_only",
                }
            )
        if layout_blocks <= 0 and math_entries > 0:
            dynamic_mode_configs.append(
                {
                    "use_external_layout": False,
                    "use_external_math": True,
                    "text_engine": preferred_text_engine,
                    "label": "math_only",
                }
            )
        dynamic_mode_configs.append(
            {
                "use_external_layout": False,
                "use_external_math": False,
                "text_engine": "native",
                "label": "native",
            }
        )
        mode_configs = tuple(dynamic_mode_configs)
    return build_best_paper_impl(
        paper_id,
        layout=layout,
        mode_configs=mode_configs,
        build_pipeline_config=build_pipeline_config_impl,
        reconcile_paper=reconcile_paper_impl,
        validate_canonical=validate_canonical_impl,
        anomaly_flags=anomaly_flags_impl,
        document_quality_key=document_quality_key_impl,
    )


__all__ = [
    "build_best_round_paper",
    "compose_external_sources",
    "existing_composed_sources",
    "load_json_if_exists",
    "paper_has_generated_abstract_file",
    "preserve_existing_generated_abstract_file",
    "write_round_canonical_outputs",
]
