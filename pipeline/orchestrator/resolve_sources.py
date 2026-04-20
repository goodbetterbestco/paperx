from __future__ import annotations

from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.acquisition.source_ownership import (
    normalize_scorecard_recommendations,
    reported_layout_provider,
    reported_math_provider,
    select_metadata_observation,
)
from pipeline.config import PipelineConfig
from pipeline.output.fingerprints import build_input_fingerprints
from pipeline.state import PaperState
from pipeline.sources.external import (
    load_docling_metadata_observation,
    load_grobid_metadata_observation,
    load_mathpix_metadata_observation,
)


def resolve_paper_sources(
    state: PaperState,
    *,
    config: PipelineConfig,
    layout_output: dict[str, Any] | None,
    figures: list[dict[str, Any]] | None,
    extract_layout: Callable[[str], dict[str, Any]],
    load_external_layout: Callable[[str], dict[str, Any] | None],
    merge_native_and_external_layout: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    load_external_math: Callable[[str], dict[str, Any] | None],
    load_mathpix_layout: Callable[[str], dict[str, Any] | None],
    extract_figures: Callable[[str], list[dict[str, Any]]],
    normalize_figure_caption_text: Callable[[str], str],
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    build_source_scorecard_impl: Callable[..., dict[str, Any]] | None = None,
    load_docling_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
    load_mathpix_metadata_observation_impl: Callable[..., dict[str, Any] | None] | None = None,
) -> PaperState:
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    build_source_scorecard_impl = build_source_scorecard_impl or build_source_scorecard
    load_docling_metadata_observation_impl = (
        load_docling_metadata_observation_impl or load_docling_metadata_observation
    )
    load_grobid_metadata_observation_impl = (
        load_grobid_metadata_observation_impl or load_grobid_metadata_observation
    )
    load_mathpix_metadata_observation_impl = (
        load_mathpix_metadata_observation_impl or load_mathpix_metadata_observation
    )
    paper_id = state.paper_id
    native_layout = layout_output or extract_layout(paper_id)
    layout = native_layout
    external_layout = None
    external_layout_engine: str | None = None
    if config.use_external_layout:
        external_layout = load_external_layout(paper_id)
        if external_layout and external_layout.get("blocks"):
            layout = merge_native_and_external_layout(native_layout, external_layout)
            external_layout_engine = str(external_layout.get("engine", "external_layout"))

    external_math = load_external_math(paper_id) if config.use_external_math else None
    external_math_engine = str((external_math or {}).get("engine", "")) or None
    mathpix_layout = load_mathpix_layout(paper_id) if config.use_external_math else None
    metadata_candidates = {
        "docling": load_docling_metadata_observation_impl(paper_id, layout=config.layout),
        "grobid": load_grobid_metadata_observation_impl(paper_id, layout=config.layout),
        "mathpix": load_mathpix_metadata_observation_impl(paper_id, layout=config.layout),
    }
    metadata_observation = select_metadata_observation(
        source_scorecard=None,
        metadata_candidates=metadata_candidates,
    )

    resolved_figures = figures or extract_figures(paper_id)
    resolved_figures = [
        {
            **figure,
            "caption": normalize_figure_caption_text(str(figure.get("caption", ""))),
        }
        for figure in resolved_figures
    ]

    state.native_layout = native_layout
    state.external_layout = external_layout
    state.merged_layout = layout
    state.external_math = external_math
    state.mathpix_layout = mathpix_layout
    state.metadata_candidates = metadata_candidates
    state.metadata_observation = metadata_observation
    state.figures = resolved_figures
    state.acquisition_route = build_acquisition_route_report_impl(
        paper_id,
        layout=config.layout,
    )
    primary_route = str((state.acquisition_route or {}).get("primary_route", "") or "")
    try:
        source_scorecard = build_source_scorecard_impl(
            native_layout=native_layout,
            external_layout=external_layout,
            mathpix_layout=mathpix_layout,
            external_math=external_math,
            route_bias=primary_route,
            metadata_observations=metadata_candidates,
        )
    except TypeError:
        source_scorecard = build_source_scorecard_impl(
            native_layout=native_layout,
            external_layout=external_layout,
            mathpix_layout=mathpix_layout,
            external_math=external_math,
        )
    source_scorecard = normalize_scorecard_recommendations(source_scorecard)
    state.source_scorecard = source_scorecard
    state.metadata_observation = select_metadata_observation(
        source_scorecard=source_scorecard,
        metadata_candidates=metadata_candidates,
    )
    state.layout_engine_name = reported_layout_provider(
        external_layout_engine,
        source_scorecard=source_scorecard,
    )
    state.math_engine_name = reported_math_provider(
        external_math_engine,
        source_scorecard=source_scorecard,
        math_payload=external_math,
    )
    state.input_fingerprints = build_input_fingerprints(
        paper_id,
        pdf_path=state.pdf_path,
        use_external_layout=bool(external_layout_engine),
        use_external_math=bool(external_math_engine),
        layout=config.layout,
    )
    return state
