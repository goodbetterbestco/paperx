from __future__ import annotations

from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.config import PipelineConfig
from pipeline.output.fingerprints import build_input_fingerprints
from pipeline.state import PaperState


GENERIC_LAYOUT_ENGINE_NAMES = {"composed", "external_layout", "merged_layout"}
GENERIC_MATH_ENGINE_NAMES = {"external_math"}


def _reported_layout_engine_name(
    external_layout_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
) -> str:
    if not external_layout_engine:
        return "native_pdf"
    preferred_provider = str((source_scorecard or {}).get("recommended_primary_layout_provider", "") or "")
    if external_layout_engine in GENERIC_LAYOUT_ENGINE_NAMES and preferred_provider:
        return preferred_provider
    return external_layout_engine


def _reported_math_engine_name(
    external_math_engine: str | None,
    *,
    source_scorecard: dict[str, Any] | None,
    external_math: dict[str, Any] | None,
) -> str:
    math_entries = list((external_math or {}).get("entries", []))
    preferred_provider = str((source_scorecard or {}).get("recommended_primary_math_provider", "") or "")
    if preferred_provider and math_entries:
        return preferred_provider
    if external_math_engine and math_entries and external_math_engine not in GENERIC_MATH_ENGINE_NAMES:
        return external_math_engine
    return "heuristic"


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
) -> PaperState:
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    build_source_scorecard_impl = build_source_scorecard_impl or build_source_scorecard
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
    state.figures = resolved_figures
    state.acquisition_route = build_acquisition_route_report_impl(
        paper_id,
        layout=config.layout,
    )
    source_scorecard = build_source_scorecard_impl(
        native_layout=native_layout,
        external_layout=external_layout,
        mathpix_layout=mathpix_layout,
        external_math=external_math,
    )
    state.source_scorecard = source_scorecard
    state.layout_engine_name = _reported_layout_engine_name(
        external_layout_engine,
        source_scorecard=source_scorecard,
    )
    state.math_engine_name = _reported_math_engine_name(
        external_math_engine,
        source_scorecard=source_scorecard,
        external_math=external_math,
    )
    state.input_fingerprints = build_input_fingerprints(
        paper_id,
        pdf_path=state.pdf_path,
        use_external_layout=bool(external_layout_engine),
        use_external_math=bool(external_math_engine),
        layout=config.layout,
    )
    return state
