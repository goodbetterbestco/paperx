from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.providers import derive_metadata_reference_observation_from_layout
from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.acquisition.source_ownership import normalize_scorecard_recommendations
from pipeline.corpus_layout import ProjectLayout, canonical_sources_dir, display_path, paper_pdf_path
from pipeline.orchestrator.round_runtime import write_json


def _discover_paper_ids(layout: ProjectLayout) -> list[str]:
    paper_ids: set[str] = set()
    if layout.corpus_root.exists():
        for child in layout.corpus_root.iterdir():
            if not child.is_dir():
                continue
            if child.name.startswith("_") or child.name == "review_drafts":
                continue
            paper_ids.add(child.name)
    if layout.project_mode:
        for pdf_path in layout.discover_source_pdfs():
            paper_ids.add(pdf_path.stem)
    return sorted(paper_ids)


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


def build_backfill_source_scorecard(
    paper_id: str,
    *,
    layout: ProjectLayout,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] = build_acquisition_route_report,
    build_source_scorecard_impl: Callable[..., dict[str, Any]] = build_source_scorecard,
    load_docling_layout_impl: Callable[..., dict[str, Any] | None],
    load_mathpix_layout_impl: Callable[..., dict[str, Any] | None],
    load_external_layout_impl: Callable[..., dict[str, Any] | None],
    load_docling_math_impl: Callable[..., dict[str, Any] | None],
    load_mathpix_math_impl: Callable[..., dict[str, Any] | None],
    load_external_math_impl: Callable[..., dict[str, Any] | None],
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None],
) -> dict[str, Any]:
    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    primary_route = str(acquisition_route.get("primary_route", "") or "")
    docling_layout = load_docling_layout_impl(paper_id, layout=layout) or {}
    mathpix_layout = load_mathpix_layout_impl(paper_id, layout=layout) or {}
    composed_layout = load_external_layout_impl(paper_id, layout=layout) or {}
    docling_math = load_docling_math_impl(paper_id, layout=layout) or {}
    mathpix_math = load_mathpix_math_impl(paper_id, layout=layout) or {}
    composed_math = load_external_math_impl(paper_id, layout=layout) or {}
    metadata_observations = {
        "docling": _nonempty_metadata_observation("docling", docling_layout),
        "grobid": load_grobid_metadata_observation_impl(paper_id, layout=layout) or {},
        "mathpix": _nonempty_metadata_observation("mathpix", mathpix_layout),
    }

    scorecard = build_source_scorecard_impl(
        native_layout=None,
        external_layout=None,
        mathpix_layout=None,
        external_math=None,
        layout_candidates={
            "docling": docling_layout,
            "mathpix": mathpix_layout,
            "composed": composed_layout if not docling_layout and not mathpix_layout else None,
        },
        math_candidates={
            "docling": docling_math,
            "mathpix": mathpix_math,
            "composed": composed_math if not docling_math and not mathpix_math else None,
        },
        route_bias=primary_route,
        metadata_observations=metadata_observations,
    )
    return normalize_scorecard_recommendations(scorecard)


def build_backfill_ocr_prepass_report(
    paper_id: str,
    *,
    layout: ProjectLayout,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] = build_acquisition_route_report,
    paper_pdf_path_impl: Callable[..., Path] = paper_pdf_path,
    ocr_normalized_pdf_path_impl: Callable[..., Path],
) -> dict[str, Any]:
    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    route_ocr_prepass = dict(acquisition_route.get("ocr_prepass") or {})
    original_pdf_path = paper_pdf_path_impl(paper_id, layout=layout)
    normalized_pdf_path = ocr_normalized_pdf_path_impl(paper_id, layout=layout)
    selected_pdf_path = normalized_pdf_path if normalized_pdf_path.exists() else original_pdf_path
    pdf_source_kind = "ocr_normalized_existing" if normalized_pdf_path.exists() else "original"
    return {
        "selected_pdf_path": display_path(selected_pdf_path, layout=layout),
        "original_pdf_path": display_path(original_pdf_path, layout=layout),
        "ocr_normalized_pdf_path": display_path(normalized_pdf_path, layout=layout),
        "pdf_source_kind": pdf_source_kind,
        "ocr_prepass_policy": str(route_ocr_prepass.get("policy", "skip") or "skip"),
        "ocr_prepass_tool": route_ocr_prepass.get("tool"),
        "ocr_prepass_applied": normalized_pdf_path.exists(),
    }


def backfill_acquisition_sidecars(
    *,
    layout: ProjectLayout,
    overwrite: bool = False,
    paper_ids: list[str] | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] = build_acquisition_route_report,
    load_docling_layout_impl: Callable[..., dict[str, Any] | None],
    load_mathpix_layout_impl: Callable[..., dict[str, Any] | None],
    load_external_layout_impl: Callable[..., dict[str, Any] | None],
    load_docling_math_impl: Callable[..., dict[str, Any] | None],
    load_mathpix_math_impl: Callable[..., dict[str, Any] | None],
    load_external_math_impl: Callable[..., dict[str, Any] | None],
    load_grobid_metadata_observation_impl: Callable[..., dict[str, Any] | None],
    ocr_normalized_pdf_path_impl: Callable[..., Path],
    write_json_impl: Callable[[Path, Any], None] = write_json,
) -> dict[str, Any]:
    target_papers = sorted(set(paper_ids or _discover_paper_ids(layout)))
    updated = {"acquisition-route.json": 0, "source-scorecard.json": 0, "ocr-prepass.json": 0}
    paper_results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for paper_id in target_papers:
        sources_dir = canonical_sources_dir(paper_id, layout=layout)
        sources_dir.mkdir(parents=True, exist_ok=True)
        route_path = sources_dir / "acquisition-route.json"
        scorecard_path = sources_dir / "source-scorecard.json"
        ocr_report_path = sources_dir / "ocr-prepass.json"
        try:
            if overwrite or not route_path.exists():
                route_payload = build_acquisition_route_report_impl(paper_id, layout=layout)
                write_json_impl(route_path, route_payload)
                updated["acquisition-route.json"] += 1
            else:
                route_payload = None

            if overwrite or not scorecard_path.exists():
                scorecard_payload = build_backfill_source_scorecard(
                    paper_id,
                    layout=layout,
                    build_acquisition_route_report_impl=build_acquisition_route_report_impl,
                    load_docling_layout_impl=load_docling_layout_impl,
                    load_mathpix_layout_impl=load_mathpix_layout_impl,
                    load_external_layout_impl=load_external_layout_impl,
                    load_docling_math_impl=load_docling_math_impl,
                    load_mathpix_math_impl=load_mathpix_math_impl,
                    load_external_math_impl=load_external_math_impl,
                    load_grobid_metadata_observation_impl=load_grobid_metadata_observation_impl,
                )
                write_json_impl(scorecard_path, scorecard_payload)
                updated["source-scorecard.json"] += 1
            else:
                scorecard_payload = None

            if overwrite or not ocr_report_path.exists():
                ocr_payload = build_backfill_ocr_prepass_report(
                    paper_id,
                    layout=layout,
                    build_acquisition_route_report_impl=build_acquisition_route_report_impl,
                    ocr_normalized_pdf_path_impl=ocr_normalized_pdf_path_impl,
                )
                write_json_impl(ocr_report_path, ocr_payload)
                updated["ocr-prepass.json"] += 1
            else:
                ocr_payload = None

            paper_results.append(
                {
                    "paper_id": paper_id,
                    "route_written": route_payload is not None,
                    "scorecard_written": scorecard_payload is not None,
                    "ocr_report_written": ocr_payload is not None,
                    "status": "updated",
                }
            )
        except Exception as exc:
            failures.append({"paper_id": paper_id, "error": str(exc)})
            paper_results.append(
                {
                    "paper_id": paper_id,
                    "route_written": False,
                    "scorecard_written": False,
                    "ocr_report_written": False,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    return {
        "paper_count": len(target_papers),
        "updated": updated,
        "failure_count": len(failures),
        "failures": failures,
        "papers": paper_results,
    }


__all__ = [
    "backfill_acquisition_sidecars",
    "build_backfill_ocr_prepass_report",
    "build_backfill_source_scorecard",
]
