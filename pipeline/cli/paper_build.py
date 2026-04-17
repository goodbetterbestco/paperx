from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipeline.config import PipelineConfig, TextEngine, build_pipeline_config
from pipeline.corpus_layout import ProjectLayout, current_layout
from pipeline.reconcile_blocks import reconcile_paper_state
from pipeline.state import PaperState


@dataclass(frozen=True)
class PaperBuildResult:
    layout: ProjectLayout
    config: PipelineConfig
    state: PaperState

    @property
    def document(self) -> dict[str, Any]:
        if self.state.document is None:
            raise RuntimeError(f"Pipeline did not materialize a canonical document for {self.state.paper_id}")
        return self.state.document


def build_paper(
    paper_id: str,
    *,
    text_engine: TextEngine = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    include_review: bool = False,
    layout: ProjectLayout | None = None,
    state: PaperState | None = None,
) -> PaperBuildResult:
    active_layout = layout or current_layout()
    config = build_pipeline_config(
        layout=active_layout,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        include_review=include_review,
    )
    paper_state = reconcile_paper_state(
        paper_id,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        config=config,
        state=state,
    )
    return PaperBuildResult(
        layout=active_layout,
        config=config,
        state=paper_state,
    )
