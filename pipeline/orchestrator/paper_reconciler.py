from __future__ import annotations

from typing import Any

from pipeline.config import PipelineConfig, build_pipeline_config
from pipeline.orchestrator.assemble_document import assemble_paper_document
from pipeline.orchestrator.metadata_enrichment import apply_metadata_observation
from pipeline.orchestrator.normalize_records import normalize_paper_records
from pipeline.orchestrator.pipeline_deps import PaperPipelineDeps
from pipeline.orchestrator.resolve_sources import resolve_paper_sources
from pipeline.state import PaperState


def run_paper_pipeline(
    paper_id: str,
    *,
    text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
    layout_output: dict[str, Any] | None,
    figures: list[dict[str, Any]] | None,
    deps: PaperPipelineDeps,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> PaperState:
    runtime_config = config or build_pipeline_config(
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        include_review=False,
    )
    paper_state = state or PaperState.begin(
        paper_id,
        config=runtime_config,
        started_at=deps.document_assembly.now_iso(),
    )
    paper_state = resolve_paper_sources(
        paper_state,
        config=runtime_config,
        layout_output=layout_output,
        figures=figures,
        deps=deps.source_resolution,
    )
    paper_state = normalize_paper_records(
        paper_state,
        config=runtime_config,
        deps=deps.record_normalization,
    )
    paper_state = assemble_paper_document(
        paper_state,
        deps=deps.document_assembly,
    )
    return apply_metadata_observation(paper_state)


def reconcile_paper_document(
    paper_id: str,
    *,
    text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
    layout_output: dict[str, Any] | None,
    figures: list[dict[str, Any]] | None,
    deps: PaperPipelineDeps,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> dict[str, Any]:
    paper_state = run_paper_pipeline(
        paper_id,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        layout_output=layout_output,
        figures=figures,
        deps=deps,
        config=config,
        state=state,
    )
    if paper_state.document is None:
        raise RuntimeError(f"Pipeline did not produce a document for {paper_id}")
    return paper_state.document
