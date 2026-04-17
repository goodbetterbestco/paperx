from __future__ import annotations

import traceback
from typing import Any, Callable

from pipeline.config import PipelineConfig
from pipeline.corpus_layout import ProjectLayout


QualityKey = tuple[int, int, int, int, int, int]


def build_best_paper(
    paper_id: str,
    *,
    layout: ProjectLayout,
    mode_configs: tuple[dict[str, Any], ...],
    build_pipeline_config: Callable[..., PipelineConfig],
    reconcile_paper: Callable[..., dict[str, Any]],
    validate_canonical: Callable[[dict[str, Any]], None],
    anomaly_flags: Callable[[dict[str, Any]], list[str]],
    document_quality_key: Callable[[dict[str, Any], int], QualityKey],
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for mode_index, config in enumerate(mode_configs):
        try:
            pipeline_config = build_pipeline_config(
                layout=layout,
                text_engine=str(config["text_engine"]),
                use_external_layout=bool(config["use_external_layout"]),
                use_external_math=bool(config["use_external_math"]),
                include_review=False,
            )
            document = reconcile_paper(
                paper_id,
                text_engine=str(config["text_engine"]),
                use_external_layout=bool(config["use_external_layout"]),
                use_external_math=bool(config["use_external_math"]),
                config=pipeline_config,
            )
            validate_canonical(document)
            anomalies = anomaly_flags(document)
            quality_key = document_quality_key(document, mode_index)
            candidates.append(
                {
                    "mode": config["label"],
                    "document": document,
                    "anomalies": anomalies,
                    "quality_key": quality_key,
                }
            )
            attempts.append(
                {
                    "mode": config["label"],
                    "anomalies": anomalies,
                    "quality_key": list(quality_key),
                }
            )
            if not anomalies:
                break
        except Exception as exc:  # pragma: no cover - batch resilience
            attempts.append(
                {
                    "mode": config["label"],
                    "error": str(exc),
                    "traceback": traceback.format_exc(limit=12),
                }
            )

    if not candidates:
        raise RuntimeError(f"All build attempts failed for {paper_id}")

    best_candidate = min(candidates, key=lambda candidate: candidate["quality_key"])
    return {
        "mode": best_candidate["mode"],
        "document": best_candidate["document"],
        "attempts": attempts,
        "anomalies": list(best_candidate["anomalies"]),
    }


__all__ = [
    "build_best_paper",
]
