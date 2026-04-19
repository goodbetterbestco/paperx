from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import score_layout_provider, score_math_provider
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
from pipeline.sources.external import external_layout_path, external_math_path


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
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    score_layout_provider_impl: Callable[..., dict[str, Any]] | None = None,
    score_math_provider_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    compose_layout_sources_impl = compose_layout_sources_impl or compose_layout_sources
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    external_math_path_impl = external_math_path_impl or external_math_path
    write_json_impl = write_json_impl or write_json
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    score_layout_provider_impl = score_layout_provider_impl or score_layout_provider
    score_math_provider_impl = score_math_provider_impl or score_math_provider
    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    primary_route = str(acquisition_route.get("primary_route", "") or "")
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    docling_math = (docling_sources or {}).get("math") or {}
    mathpix_math = (mathpix_sources or {}).get("math") or {}
    docling_math_entries = len(((docling_sources or {}).get("math") or {}).get("entries", []))
    mathpix_math_entries = len(((mathpix_sources or {}).get("math") or {}).get("entries", []))
    provider_scores = []
    if docling_layout:
        provider_scores.append(
            score_layout_provider_impl(
                str(docling_layout.get("engine", "docling")),
                docling_layout,
                kind="layout",
                math_entry_count=docling_math_entries,
            )
        )
    if mathpix_layout:
        provider_scores.append(
            score_layout_provider_impl(
                str(mathpix_layout.get("engine", "mathpix")),
                mathpix_layout,
                kind="layout",
                math_entry_count=mathpix_math_entries,
            )
        )
    if docling_math:
        provider_scores.append(
            score_math_provider_impl(
                str(docling_math.get("engine", "docling")),
                docling_math,
                route_bias=primary_route,
            )
        )
    if mathpix_math:
        provider_scores.append(
            score_math_provider_impl(
                str(mathpix_math.get("engine", "mathpix")),
                mathpix_math,
                route_bias=primary_route,
            )
        )
    provider_scores.sort(key=lambda item: (-float(item.get("overall_score", 0.0) or 0.0), str(item.get("provider", ""))))
    source_scorecard = {
        "providers": provider_scores,
        "recommended_primary_layout_provider": next(
            (item["provider"] for item in provider_scores if str(item.get("kind")) == "layout"),
            None,
        ),
        "recommended_primary_math_provider": next(
            (item["provider"] for item in provider_scores if str(item.get("kind")) == "math" and int(item.get("math_entry_count", 0) or 0) > 0),
            None,
        ),
    }
    try:
        final_layout = compose_layout_sources_impl(
            docling_sources,
            mathpix_sources,
            acquisition_route=acquisition_route,
            source_scorecard=source_scorecard,
        )
    except TypeError:
        final_layout = compose_layout_sources_impl(docling_sources, mathpix_sources)
    preferred_math_provider = str(source_scorecard.get("recommended_primary_math_provider") or "")
    if preferred_math_provider == str(mathpix_math.get("engine", "mathpix")) and mathpix_math.get("entries"):
        final_math = mathpix_math
    elif preferred_math_provider == str(docling_math.get("engine", "docling")) and docling_math.get("entries"):
        final_math = docling_math
    elif mathpix_math.get("entries"):
        final_math = mathpix_math
    elif docling_math.get("entries"):
        final_math = docling_math
    else:
        final_math = {"engine": "none", "entries": []}
    layout_path = external_layout_path_impl(paper_id, layout=layout)
    math_path = external_math_path_impl(paper_id, layout=layout)
    write_json_impl(layout_path, final_layout)
    write_json_impl(math_path, final_math)
    sources_dir = layout_path.parent
    write_json_impl(sources_dir / "acquisition-route.json", acquisition_route)
    write_json_impl(sources_dir / "source-scorecard.json", source_scorecard)
    return {
        "layout_path": str(layout_path),
        "math_path": str(math_path),
        "layout_engine": final_layout.get("engine"),
        "layout_blocks": len(final_layout.get("blocks", [])),
        "math_engine": final_math.get("engine"),
        "math_entries": len(final_math.get("entries", [])),
        "recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
        "recommended_primary_math_provider": source_scorecard.get("recommended_primary_math_provider"),
        "acquisition_route": acquisition_route.get("primary_route"),
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
) -> dict[str, Any]:
    load_json_if_exists_impl = load_json_if_exists_impl or load_json_if_exists
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    external_math_path_impl = external_math_path_impl or external_math_path
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
    return {
        "layout_path": str(external_layout_path_impl(paper_id, layout=layout)),
        "math_path": str(external_math_path_impl(paper_id, layout=layout)),
        "layout_engine": external_layout.get("engine"),
        "layout_blocks": len(external_layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
        "acquisition_route": acquisition_route.get("primary_route"),
        "recommended_primary_layout_provider": source_scorecard.get("recommended_primary_layout_provider"),
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
