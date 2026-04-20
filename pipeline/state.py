from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pipeline.config import PipelineConfig


@dataclass
class PaperState:
    paper_id: str
    pdf_path: Path
    started_at: str
    input_fingerprints: dict[str, Any] = field(default_factory=dict)

    native_layout: dict[str, Any] | None = None
    external_layout: dict[str, Any] | None = None
    merged_layout: dict[str, Any] | None = None
    mathpix_layout: dict[str, Any] | None = None
    external_math: dict[str, Any] | None = None
    metadata_candidates: dict[str, dict[str, Any] | None] = field(default_factory=dict)
    metadata_observation: dict[str, Any] | None = None
    reference_observation: dict[str, Any] | None = None
    figures: list[dict[str, Any]] = field(default_factory=list)
    acquisition_route: dict[str, Any] | None = None
    source_scorecard: dict[str, Any] | None = None

    records: list[dict[str, Any]] = field(default_factory=list)
    layout_by_id: dict[str, Any] = field(default_factory=dict)
    page_one_records: list[dict[str, Any]] = field(default_factory=list)
    prelude_records: list[dict[str, Any]] = field(default_factory=list)
    section_roots: list[Any] = field(default_factory=list)

    external_math_entries: list[dict[str, Any]] = field(default_factory=list)
    external_math_overlap_page_map: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    external_math_page_map: dict[int, list[dict[str, Any]]] = field(default_factory=dict)

    front_matter: dict[str, Any] | None = None
    blocks: list[dict[str, Any]] = field(default_factory=list)
    sections: list[dict[str, Any]] = field(default_factory=list)
    math_entries: list[dict[str, Any]] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    decision_artifacts: dict[str, Any] = field(default_factory=dict)

    document: dict[str, Any] | None = None
    effective_text_engine: str = "native_pdf"
    layout_engine_name: str = "native_pdf"
    math_engine_name: str = "heuristic"
    notes: list[str] = field(default_factory=list)

    @classmethod
    def begin(cls, paper_id: str, *, config: PipelineConfig, started_at: str) -> PaperState:
        return cls(
            paper_id=paper_id,
            pdf_path=config.layout.paper_pdf_path(paper_id),
            started_at=started_at,
        )
