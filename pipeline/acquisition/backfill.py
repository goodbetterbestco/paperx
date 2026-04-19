from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.acquisition.scoring import score_layout_provider, score_math_provider, score_metadata_provider
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


def _recommended_provider(provider_scores: list[dict[str, Any]], kind: str) -> str | None:
    for item in provider_scores:
        if str(item.get("kind")) == kind:
            if kind == "math" and int(item.get("math_entry_count", 0) or 0) <= 0:
                continue
            if kind == "metadata" and not (
                bool(item.get("title_present"))
                or bool(item.get("abstract_present"))
                or int(item.get("reference_count", 0) or 0) > 0
            ):
                continue
            return str(item.get("provider", "") or "") or None
    return None


def build_backfill_source_scorecard(
    paper_id: str,
    *,
    layout: ProjectLayout,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] = build_acquisition_route_report,
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
    metadata_observation = load_grobid_metadata_observation_impl(paper_id, layout=layout) or {}

    provider_scores: list[dict[str, Any]] = []
    if docling_layout:
        provider_scores.append(
            score_layout_provider(
                str(docling_layout.get("engine", "docling")),
                docling_layout,
                kind="layout",
                math_entry_count=len((docling_math.get("entries") or [])),
            )
        )
    if mathpix_layout:
        provider_scores.append(
            score_layout_provider(
                str(mathpix_layout.get("engine", "mathpix")),
                mathpix_layout,
                kind="layout",
                math_entry_count=len((mathpix_math.get("entries") or [])),
            )
        )
    if not provider_scores and composed_layout:
        provider_scores.append(
            score_layout_provider(
                str(composed_layout.get("engine", "composed")),
                composed_layout,
                kind="layout",
                math_entry_count=len((composed_math.get("entries") or [])),
            )
        )

    if docling_math:
        provider_scores.append(
            score_math_provider(
                str(docling_math.get("engine", "docling")),
                docling_math,
                route_bias=primary_route,
            )
        )
    if mathpix_math:
        provider_scores.append(
            score_math_provider(
                str(mathpix_math.get("engine", "mathpix")),
                mathpix_math,
                route_bias=primary_route,
            )
        )
    if not any(str(item.get("kind")) == "math" for item in provider_scores) and composed_math:
        provider_scores.append(
            score_math_provider(
                str(composed_math.get("engine", "external_math")),
                composed_math,
                route_bias=primary_route,
            )
        )
    if metadata_observation:
        provider_scores.append(score_metadata_provider("grobid", metadata_observation, route_bias=primary_route))

    provider_scores.sort(key=lambda item: (-float(item.get("overall_score", 0.0) or 0.0), str(item.get("provider", ""))))
    return {
        "providers": provider_scores,
        "recommended_primary_layout_provider": _recommended_provider(provider_scores, "layout"),
        "recommended_primary_math_provider": _recommended_provider(provider_scores, "math"),
        "recommended_primary_metadata_provider": _recommended_provider(provider_scores, "metadata"),
        "recommended_primary_reference_provider": next(
            (
                str(item.get("provider", "") or "")
                for item in provider_scores
                if (
                    (str(item.get("kind")) == "metadata" and int(item.get("reference_count", 0) or 0) > 0)
                    or (str(item.get("kind")) == "layout" and int(item.get("reference_count", 0) or 0) > 0)
                )
            ),
            None,
        ),
    }


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
