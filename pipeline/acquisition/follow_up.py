from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.source_ownership import (
    normalize_scorecard_recommendations,
    select_metadata_observation,
    select_reference_observation,
    select_math_payload,
)
from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_paper import build_acquisition_execution_summary
from pipeline.orchestrator.round_runtime import now_iso, write_json
from pipeline.orchestrator.source_composition import compose_layout_sources
from pipeline.sources.external import (
    acquisition_execution_report_path,
    acquisition_trial_dir,
    external_layout_path,
    load_docling_metadata_observation,
    load_grobid_metadata_observation,
    load_mathpix_metadata_observation,
)


def _load_json_dict(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return {}


def _trial_override_scorecard(
    source_scorecard: dict[str, Any],
    *,
    layout_target_provider: str | None,
    math_target_provider: str | None,
) -> dict[str, Any]:
    trial_scorecard = dict(source_scorecard)
    trial_scorecard["trial_override"] = {
        "original_recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
        "original_recommended_primary_math_provider": source_scorecard.get("recommended_primary_math_provider"),
        "applied_layout_provider": layout_target_provider,
        "applied_math_provider": math_target_provider,
    }
    if layout_target_provider:
        trial_scorecard["recommended_primary_layout_provider"] = layout_target_provider
        trial_scorecard["layout_recommendation_basis"] = "trial_override"
    if math_target_provider:
        trial_scorecard["recommended_primary_math_provider"] = math_target_provider
        trial_scorecard["math_recommendation_basis"] = "trial_override"
    return normalize_scorecard_recommendations(trial_scorecard)


def apply_acquisition_follow_up(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    label: str = "follow-up",
    load_json_dict_impl: Callable[[Path], dict[str, Any]] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
    now_iso_impl: Callable[[], str] | None = None,
    load_docling_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_mathpix_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    load_json_dict_impl = load_json_dict_impl or _load_json_dict
    write_json_impl = write_json_impl or write_json
    now_iso_impl = now_iso_impl or now_iso
    load_docling_metadata_observation_impl = (
        load_docling_metadata_observation_impl or load_docling_metadata_observation
    )
    load_grobid_metadata_observation_impl = (
        load_grobid_metadata_observation_impl or load_grobid_metadata_observation
    )
    load_mathpix_metadata_observation_impl = (
        load_mathpix_metadata_observation_impl or load_mathpix_metadata_observation
    )

    execution_path = acquisition_execution_report_path(paper_id, layout=layout)
    if not execution_path.exists():
        raise FileNotFoundError(f"Missing acquisition execution sidecar for {paper_id}: {execution_path}")
    sources_dir = external_layout_path(paper_id, layout=layout).parent
    route_path = sources_dir / "acquisition-route.json"
    scorecard_path = sources_dir / "source-scorecard.json"
    if not route_path.exists():
        raise FileNotFoundError(f"Missing acquisition route sidecar for {paper_id}: {route_path}")
    if not scorecard_path.exists():
        raise FileNotFoundError(f"Missing source scorecard sidecar for {paper_id}: {scorecard_path}")

    acquisition_route = load_json_dict_impl(route_path)
    source_scorecard = normalize_scorecard_recommendations(load_json_dict_impl(scorecard_path))
    acquisition_execution = load_json_dict_impl(execution_path)
    follow_up = dict(acquisition_execution.get("follow_up") or {})
    follow_up_actions = [
        dict(item)
        for item in list(follow_up.get("actions") or [])
        if isinstance(item, dict)
    ]

    layout_target_provider = next(
        (
            str(item.get("target_provider", "")).strip() or None
            for item in follow_up_actions
            if str(item.get("action", "")).strip() == "trial_layout_provider"
        ),
        None,
    )
    math_target_provider = next(
        (
            str(item.get("target_provider", "")).strip() or None
            for item in follow_up_actions
            if str(item.get("action", "")).strip() == "trial_math_provider"
        ),
        None,
    )

    if not layout_target_provider and not math_target_provider:
        return {
            "paper_id": paper_id,
            "label": label,
            "trial_dir": str(acquisition_trial_dir(paper_id, layout=layout, label=label)),
            "applied": False,
            "applied_actions": [],
            "reason": "no_trial_actions",
        }

    docling_layout_path = sources_dir / "docling-layout.json"
    mathpix_layout_path = sources_dir / "mathpix-layout.json"
    docling_math_path = sources_dir / "docling-math.json"
    mathpix_math_path = sources_dir / "mathpix-math.json"
    docling_layout = load_json_dict_impl(docling_layout_path) if docling_layout_path.exists() else {}
    mathpix_layout = load_json_dict_impl(mathpix_layout_path) if mathpix_layout_path.exists() else {}
    docling_math = load_json_dict_impl(docling_math_path) if docling_math_path.exists() else {}
    mathpix_math = load_json_dict_impl(mathpix_math_path) if mathpix_math_path.exists() else {}
    docling_sources = {"layout": docling_layout, "math": docling_math} if (docling_layout or docling_math) else None
    mathpix_sources = {"layout": mathpix_layout, "math": mathpix_math} if (mathpix_layout or mathpix_math) else None

    trial_scorecard = _trial_override_scorecard(
        source_scorecard,
        layout_target_provider=layout_target_provider,
        math_target_provider=math_target_provider,
    )
    metadata_candidates = {
        "docling": load_docling_metadata_observation_impl(paper_id, layout=layout),
        "grobid": load_grobid_metadata_observation_impl(paper_id, layout=layout),
        "mathpix": load_mathpix_metadata_observation_impl(paper_id, layout=layout),
    }
    metadata_observation = select_metadata_observation(
        source_scorecard=trial_scorecard,
        metadata_candidates=metadata_candidates,
    )
    reference_observation = select_reference_observation(
        source_scorecard=trial_scorecard,
        metadata_candidates=metadata_candidates,
    )
    final_layout = compose_layout_sources(
        docling_sources,
        mathpix_sources,
        acquisition_route=acquisition_route,
        source_scorecard=trial_scorecard,
    )
    final_math = select_math_payload(
        source_scorecard=trial_scorecard,
        docling_math=docling_math,
        mathpix_math=mathpix_math,
    )
    execution_summary = build_acquisition_execution_summary(
        acquisition_route=acquisition_route,
        source_scorecard=trial_scorecard,
        docling_sources=docling_sources,
        mathpix_sources=mathpix_sources,
        final_layout=final_layout,
        final_math=final_math,
        metadata_candidates=metadata_candidates,
        metadata_observation=metadata_observation,
        reference_observation=reference_observation,
    )

    applied_actions = [
        {
            "product": "layout",
            "target_provider": layout_target_provider,
        }
        for _ in ([layout_target_provider] if layout_target_provider else [])
    ] + [
        {
            "product": "math",
            "target_provider": math_target_provider,
        }
        for _ in ([math_target_provider] if math_target_provider else [])
    ]
    trial_dir = acquisition_trial_dir(paper_id, layout=layout, label=label)
    execution_summary["trial"] = {
        "label": label,
        "applied_at": now_iso_impl(),
        "applied_actions": applied_actions,
        "source_execution_path": str(execution_path),
    }
    write_json_impl(trial_dir / "acquisition-route.json", acquisition_route)
    write_json_impl(trial_dir / "source-scorecard.json", trial_scorecard)
    write_json_impl(trial_dir / "layout.json", final_layout)
    write_json_impl(trial_dir / "math.json", final_math)
    write_json_impl(trial_dir / "acquisition-execution.json", execution_summary)
    return {
        "paper_id": paper_id,
        "label": label,
        "trial_dir": str(trial_dir),
        "applied": True,
        "applied_actions": applied_actions,
        "layout_path": str(trial_dir / "layout.json"),
        "math_path": str(trial_dir / "math.json"),
        "source_scorecard_path": str(trial_dir / "source-scorecard.json"),
        "acquisition_execution_path": str(trial_dir / "acquisition-execution.json"),
    }


__all__ = ["apply_acquisition_follow_up"]
