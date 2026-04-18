from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

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
) -> dict[str, Any]:
    compose_layout_sources_impl = compose_layout_sources_impl or compose_layout_sources
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    external_math_path_impl = external_math_path_impl or external_math_path
    write_json_impl = write_json_impl or write_json
    final_layout = compose_layout_sources_impl(docling_sources, mathpix_sources)
    if mathpix_sources and mathpix_sources.get("math", {}).get("entries"):
        final_math = mathpix_sources["math"]
    elif docling_sources:
        final_math = docling_sources["math"]
    else:
        final_math = {"engine": "none", "entries": []}
    layout_path = external_layout_path_impl(paper_id, layout=layout)
    math_path = external_math_path_impl(paper_id, layout=layout)
    write_json_impl(layout_path, final_layout)
    write_json_impl(math_path, final_math)
    return {
        "layout_path": str(layout_path),
        "math_path": str(math_path),
        "layout_engine": final_layout.get("engine"),
        "layout_blocks": len(final_layout.get("blocks", [])),
        "math_engine": final_math.get("engine"),
        "math_entries": len(final_math.get("entries", [])),
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
    return {
        "layout_path": str(external_layout_path_impl(paper_id, layout=layout)),
        "math_path": str(external_math_path_impl(paper_id, layout=layout)),
        "layout_engine": external_layout.get("engine"),
        "layout_blocks": len(external_layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
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
) -> dict[str, Any]:
    build_best_paper_impl = build_best_paper_impl or build_best_paper
    build_pipeline_config_impl = build_pipeline_config_impl or build_pipeline_config
    reconcile_paper_impl = reconcile_paper_impl or reconcile_paper
    validate_canonical_impl = validate_canonical_impl or validate_canonical
    anomaly_flags_impl = anomaly_flags_impl or anomaly_flags
    document_quality_key_impl = document_quality_key_impl or document_quality_key
    return build_best_paper_impl(
        paper_id,
        layout=layout,
        mode_configs=(
            {"use_external_layout": True, "use_external_math": True, "text_engine": "native", "label": "hybrid"},
            {"use_external_layout": True, "use_external_math": False, "text_engine": "native", "label": "layout_only"},
            {"use_external_layout": False, "use_external_math": False, "text_engine": "native", "label": "native"},
        ),
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
