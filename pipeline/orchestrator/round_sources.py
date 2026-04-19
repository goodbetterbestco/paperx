from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import json
import time
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.corpus_layout import ProjectLayout
from pipeline.corpus_layout import paper_pdf_path
from pipeline.orchestrator.round_runtime import write_json
from pipeline.orchestrator.round_settings import docling_device, mathpix_credentials_available
from pipeline.sources.docling import docling_json_to_external_sources, run_docling
from pipeline.sources.external import external_layout_path, ocr_normalized_pdf_path
from pipeline.sources.mathpix import mathpix_pages_to_external_sources, run_mathpix
from pipeline.sources.ocrmypdf import run_ocrmypdf


PER_PAPER_SOURCE_WORKERS = 2


def build_docling_sources(
    paper_id: str,
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    docling_device_impl: Callable[[], str | None] | None = None,
    run_docling_impl: Callable[..., Path] | None = None,
    docling_json_to_external_sources_impl: Callable[..., tuple[dict[str, Any], dict[str, Any]]] | None = None,
    external_layout_path_impl: Callable[..., Path] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
) -> dict[str, Any]:
    docling_device_impl = docling_device_impl or docling_device
    run_docling_impl = run_docling_impl or run_docling
    docling_json_to_external_sources_impl = docling_json_to_external_sources_impl or docling_json_to_external_sources
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    write_json_impl = write_json_impl or write_json
    docling_json_path = run_docling_impl(paper_id, pdf_path=pdf_path, device=docling_device_impl(), layout=layout)
    docling_document = json.loads(docling_json_path.read_text(encoding="utf-8"))
    try:
        external_layout, math = docling_json_to_external_sources_impl(
            docling_document,
            paper_id,
            layout=layout,
            pdf_path=pdf_path,
        )
    except TypeError:
        external_layout, math = docling_json_to_external_sources_impl(docling_document, paper_id, layout=layout)
    sources_dir = external_layout_path_impl(paper_id, layout=layout).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    docling_layout_path = sources_dir / "docling-layout.json"
    docling_math_path = sources_dir / "docling-math.json"
    write_json_impl(docling_layout_path, external_layout)
    write_json_impl(docling_math_path, math)
    return {
        "docling_json": str(docling_json_path),
        "source_pdf_path": str((pdf_path or Path(external_layout.get("pdf_path", ""))).resolve()) if pdf_path else external_layout.get("pdf_path"),
        "layout": external_layout,
        "math": math,
        "layout_path": str(docling_layout_path),
        "math_path": str(docling_math_path),
    }


def build_mathpix_sources_from_result(
    paper_id: str,
    mathpix_result: dict[str, Any],
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    mathpix_pages_to_external_sources_impl: Callable[..., tuple[dict[str, Any], dict[str, Any]]] | None = None,
    external_layout_path_impl: Callable[..., Path] | None = None,
    write_json_impl: Callable[[Path, Any], None] | None = None,
) -> dict[str, Any]:
    mathpix_pages_to_external_sources_impl = mathpix_pages_to_external_sources_impl or mathpix_pages_to_external_sources
    external_layout_path_impl = external_layout_path_impl or external_layout_path
    write_json_impl = write_json_impl or write_json
    payloads = list(mathpix_result.get("pages") or [])
    try:
        external_layout, math = mathpix_pages_to_external_sources_impl(
            payloads,
            paper_id,
            layout=layout,
            pdf_path=pdf_path,
        )
    except TypeError:
        external_layout, math = mathpix_pages_to_external_sources_impl(payloads, paper_id, layout=layout)
    sources_dir = external_layout_path_impl(paper_id, layout=layout).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    mathpix_layout_path = sources_dir / "mathpix-layout.json"
    mathpix_math_path = sources_dir / "mathpix-math.json"
    write_json_impl(mathpix_layout_path, external_layout)
    write_json_impl(mathpix_math_path, math)
    result = {
        "source_pdf_path": str(pdf_path.resolve()) if pdf_path is not None else external_layout.get("pdf_path"),
        "layout": external_layout,
        "math": math,
        "layout_path": str(mathpix_layout_path),
        "math_path": str(mathpix_math_path),
        "math_entries": len(math.get("entries", [])),
    }
    if "pdf_id" in mathpix_result:
        result["pdf_id"] = str(mathpix_result["pdf_id"])
    if "elapsed_seconds" in mathpix_result:
        result["elapsed_seconds"] = float(mathpix_result["elapsed_seconds"])
    return result


def build_mathpix_sources(
    paper_id: str,
    *,
    pdf_path: Path | None = None,
    layout: ProjectLayout | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    run_mathpix_impl: Callable[..., dict[str, Any]] | None = None,
    build_mathpix_sources_from_result_impl: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    run_mathpix_impl = run_mathpix_impl or run_mathpix
    build_mathpix_sources_from_result_impl = build_mathpix_sources_from_result_impl or build_mathpix_sources_from_result
    if not mathpix_credentials_available_impl():
        return None
    mathpix_result = run_mathpix_impl(paper_id, pdf_path=pdf_path, layout=layout)
    return build_mathpix_sources_from_result_impl(paper_id, mathpix_result, pdf_path=pdf_path, layout=layout)


def resolve_extraction_pdf(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    paper_pdf_path_impl: Callable[..., Path] | None = None,
    ocr_normalized_pdf_path_impl: Callable[..., Path] | None = None,
    run_ocrmypdf_impl: Callable[..., Path] | None = None,
) -> dict[str, Any]:
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    paper_pdf_path_impl = paper_pdf_path_impl or paper_pdf_path
    ocr_normalized_pdf_path_impl = ocr_normalized_pdf_path_impl or ocr_normalized_pdf_path
    run_ocrmypdf_impl = run_ocrmypdf_impl or run_ocrmypdf
    acquisition_route = build_acquisition_route_report_impl(paper_id, layout=layout)
    original_pdf_path = paper_pdf_path_impl(paper_id, layout=layout)
    normalized_pdf_path = ocr_normalized_pdf_path_impl(paper_id, layout=layout)
    ocr_prepass = dict(acquisition_route.get("ocr_prepass") or {})
    policy = str(ocr_prepass.get("policy", "skip") or "skip")
    tool = str(ocr_prepass.get("tool", "") or "") or None
    should_run = bool(ocr_prepass.get("should_run"))

    selected_pdf_path = original_pdf_path
    pdf_source_kind = "original"
    ocr_prepass_applied = False

    if should_run and tool == "ocrmypdf":
        if normalized_pdf_path.exists():
            selected_pdf_path = normalized_pdf_path
            pdf_source_kind = "ocr_normalized_existing"
            ocr_prepass_applied = True
        elif policy in {"required", "recommended"}:
            normalized_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                generated_pdf_path = run_ocrmypdf_impl(original_pdf_path, normalized_pdf_path)
            except FileNotFoundError:
                if policy == "required":
                    raise
                pdf_source_kind = "original_recommended_ocr_unavailable"
            else:
                selected_pdf_path = generated_pdf_path
                pdf_source_kind = "ocr_normalized_generated"
                ocr_prepass_applied = True

    return {
        "acquisition_route": acquisition_route,
        "selected_pdf_path": selected_pdf_path,
        "original_pdf_path": original_pdf_path,
        "ocr_normalized_pdf_path": normalized_pdf_path,
        "pdf_source_kind": pdf_source_kind,
        "ocr_prepass_policy": policy,
        "ocr_prepass_tool": tool,
        "ocr_prepass_applied": ocr_prepass_applied,
    }


def timed_call(label: str, fn: Any, /, *args: Any, **kwargs: Any) -> tuple[str, float, Any]:
    started = time.perf_counter()
    result = fn(*args, **kwargs)
    return label, round(time.perf_counter() - started, 3), result


def build_extraction_sources_for_paper(
    paper_id: str,
    *,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
    layout: ProjectLayout | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    per_paper_source_workers: int = PER_PAPER_SOURCE_WORKERS,
    timed_call_impl: Callable[..., tuple[str, float, Any]] | None = None,
    resolve_extraction_pdf_impl: Callable[..., dict[str, Any]] | None = None,
    build_docling_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_mathpix_sources_impl: Callable[..., dict[str, Any] | None] | None = None,
    build_mathpix_sources_from_result_impl: Callable[..., dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]:
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    timed_call_impl = timed_call_impl or timed_call
    resolve_extraction_pdf_impl = resolve_extraction_pdf_impl or resolve_extraction_pdf
    build_docling_sources_impl = build_docling_sources_impl or build_docling_sources
    build_mathpix_sources_impl = build_mathpix_sources_impl or build_mathpix_sources
    build_mathpix_sources_from_result_impl = (
        build_mathpix_sources_from_result_impl or build_mathpix_sources_from_result
    )
    timings: dict[str, float] = {}
    pdf_selection_started = time.perf_counter()
    pdf_selection = resolve_extraction_pdf_impl(paper_id, layout=layout)
    timings["ocr_prepass_seconds"] = round(time.perf_counter() - pdf_selection_started, 3)
    selected_pdf_path = pdf_selection["selected_pdf_path"]
    mathpix_enabled = mathpix_credentials_available_impl()
    max_workers = 1 if prefetched_mathpix_future is not None else (per_paper_source_workers if mathpix_enabled else 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        docling_future = executor.submit(
            timed_call_impl,
            "docling",
            build_docling_sources_impl,
            paper_id,
            pdf_path=selected_pdf_path,
            layout=layout,
        )
        local_mathpix_future: Future[tuple[str, float, Any]] | None = None
        if mathpix_enabled and prefetched_mathpix_future is None:
            local_mathpix_future = executor.submit(
                timed_call_impl,
                "mathpix",
                build_mathpix_sources_impl,
                paper_id,
                pdf_path=selected_pdf_path,
                layout=layout,
            )

        _, docling_seconds, docling_sources = docling_future.result()
        timings["docling_seconds"] = docling_seconds
        mathpix_sources = None
        if prefetched_mathpix_future is not None:
            mathpix_result = prefetched_mathpix_future.result()
            mathpix_sources = build_mathpix_sources_from_result_impl(
                paper_id,
                mathpix_result,
                pdf_path=selected_pdf_path,
                layout=layout,
            )
            mathpix_seconds = float(mathpix_result.get("elapsed_seconds", 0.0))
            timings["mathpix_seconds"] = mathpix_seconds
        elif local_mathpix_future is not None:
            _, mathpix_seconds, mathpix_sources = local_mathpix_future.result()
            timings["mathpix_seconds"] = mathpix_seconds
        else:
            timings["mathpix_seconds"] = 0.0

    docling_sources["pdf_selection"] = {
        "selected_pdf_path": str(selected_pdf_path),
        "pdf_source_kind": str(pdf_selection["pdf_source_kind"]),
        "ocr_prepass_policy": str(pdf_selection["ocr_prepass_policy"]),
        "ocr_prepass_tool": pdf_selection["ocr_prepass_tool"],
        "ocr_prepass_applied": bool(pdf_selection["ocr_prepass_applied"]),
    }
    if mathpix_sources is not None:
        mathpix_sources["pdf_selection"] = dict(docling_sources["pdf_selection"])
    return docling_sources, mathpix_sources, timings


__all__ = [
    "build_docling_sources",
    "build_extraction_sources_for_paper",
    "build_mathpix_sources",
    "build_mathpix_sources_from_result",
    "resolve_extraction_pdf",
    "timed_call",
]
