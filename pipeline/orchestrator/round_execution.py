from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import time
import traceback
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.corpus_layout import ProjectLayout, canonical_path
from pipeline.orchestrator.round_document import (
    anomaly_flags,
    desired_flags_for_existing_paper,
    preserve_existing_generated_abstract,
)
from pipeline.orchestrator.round_mathpix import MathpixRoundCoordinator
from pipeline.orchestrator.round_paper import (
    build_best_round_paper,
    compose_external_sources,
    existing_composed_sources,
    load_json_if_exists,
    preserve_existing_generated_abstract_file,
    write_round_canonical_outputs,
)
from pipeline.orchestrator.round_runtime import now_iso, save_status
from pipeline.orchestrator.round_settings import (
    mathpix_credentials_available,
    mathpix_round_poll_seconds,
    mathpix_submit_workers,
)
from pipeline.orchestrator.round_sources import build_extraction_sources_for_paper, mathpix_prefetch_allowed
from pipeline.output.staleness import detect_canonical_staleness


def run_paper_job(
    paper_id: str,
    *,
    force_rebuild: bool,
    layout: ProjectLayout,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
    now_iso_impl: Callable[[], str] | None = None,
    load_json_if_exists_impl: Callable[[Any], dict[str, Any] | None] | None = None,
    canonical_path_impl: Callable[..., Any] | None = None,
    existing_composed_sources_impl: Callable[..., dict[str, Any]] | None = None,
    desired_flags_for_existing_paper_impl: Callable[[dict[str, Any] | None, dict[str, Any]], dict[str, bool]] | None = None,
    detect_canonical_staleness_impl: Callable[..., dict[str, Any]] | None = None,
    write_canonical_outputs_impl: Callable[..., dict[str, Any]] | None = None,
    anomaly_flags_impl: Callable[[dict[str, Any]], list[str]] | None = None,
    build_extraction_sources_for_paper_impl: Callable[..., tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]] | None = None,
    compose_external_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_paper_impl: Callable[..., dict[str, Any]] | None = None,
    preserve_existing_generated_abstract_impl: Callable[[dict[str, Any] | None, dict[str, Any]], bool] | None = None,
    preserve_existing_generated_abstract_file_impl: Callable[..., bool] | None = None,
) -> dict[str, Any]:
    now_iso_impl = now_iso_impl or now_iso
    load_json_if_exists_impl = load_json_if_exists_impl or load_json_if_exists
    canonical_path_impl = canonical_path_impl or canonical_path
    existing_composed_sources_impl = existing_composed_sources_impl or existing_composed_sources
    desired_flags_for_existing_paper_impl = desired_flags_for_existing_paper_impl or desired_flags_for_existing_paper
    detect_canonical_staleness_impl = detect_canonical_staleness_impl or detect_canonical_staleness
    write_canonical_outputs_impl = write_canonical_outputs_impl or write_round_canonical_outputs
    anomaly_flags_impl = anomaly_flags_impl or anomaly_flags
    build_extraction_sources_for_paper_impl = build_extraction_sources_for_paper_impl or build_extraction_sources_for_paper
    compose_external_sources_impl = compose_external_sources_impl or compose_external_sources
    build_paper_impl = build_paper_impl or build_best_round_paper
    preserve_existing_generated_abstract_impl = preserve_existing_generated_abstract_impl or preserve_existing_generated_abstract
    preserve_existing_generated_abstract_file_impl = (
        preserve_existing_generated_abstract_file_impl or preserve_existing_generated_abstract_file
    )
    canonical_target = canonical_path_impl(paper_id, layout=layout)
    paper_status: dict[str, Any] = {}
    timings: dict[str, float] = {}
    overall_started = time.perf_counter()
    try:
        existing_document = load_json_if_exists_impl(canonical_target)
        existing_composed = existing_composed_sources_impl(paper_id, layout=layout)
        desired_flags = desired_flags_for_existing_paper_impl(existing_document, existing_composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness_impl(
            canonical_target,
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        if not force_rebuild and not prebuild_staleness.get("stale") and existing_document is not None:
            refresh_started = time.perf_counter()
            outputs = write_canonical_outputs_impl(paper_id, existing_document, layout=layout)
            timings["refresh_outputs_seconds"] = round(time.perf_counter() - refresh_started, 3)
            anomalies = anomaly_flags_impl(existing_document)
            timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
            paper_status.update(
                {
                    "status": "completed",
                    "completed_at": now_iso_impl(),
                    "mode": "fresh_canonical",
                    "metrics": outputs,
                    "build_sources": existing_document.get("build", {}).get("sources", {}),
                    "anomalies": anomalies,
                    "docling": {
                        "layout_blocks": 0,
                        "math_entries": 0,
                    },
                    "mathpix": {
                        "present": False,
                        "math_entries": 0,
                    },
                    "composed_sources": existing_composed,
                    "attempts": [],
                    "prebuild_staleness": prebuild_staleness,
                    "skipped_fresh": True,
                    "forced_rebuild": False,
                    "timings": timings,
                }
            )
            return paper_status

        docling_sources, mathpix_sources, extraction_timings = build_extraction_sources_for_paper_impl(
            paper_id,
            prefetched_mathpix_future=prefetched_mathpix_future,
            layout=layout,
        )
        timings.update(extraction_timings)

        compose_started = time.perf_counter()
        composed = compose_external_sources_impl(
            paper_id,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
            layout=layout,
        )
        timings["compose_sources_seconds"] = round(time.perf_counter() - compose_started, 3)

        desired_flags = desired_flags_for_existing_paper_impl(existing_document, composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness_impl(
            canonical_target,
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        build_started = time.perf_counter()
        build_result = build_paper_impl(paper_id, layout=layout)
        timings["build_seconds"] = round(time.perf_counter() - build_started, 3)
        document = build_result["document"]
        preserved_generated_abstract = preserve_existing_generated_abstract_impl(existing_document, document)
        preserved_generated_abstract_file = preserve_existing_generated_abstract_file_impl(
            paper_id,
            existing_document,
            document,
            layout=layout,
        )
        outputs = write_canonical_outputs_impl(paper_id, document, layout=layout)
        anomalies = anomaly_flags_impl(document)
        timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
        paper_status.update(
            {
                "status": "completed",
                "completed_at": now_iso_impl(),
                "mode": build_result["mode"],
                "metrics": outputs,
                "build_sources": document.get("build", {}).get("sources", {}),
                "anomalies": anomalies,
                "docling": {
                    "layout_blocks": len(docling_sources["layout"].get("blocks", [])),
                    "math_entries": len(docling_sources["math"].get("entries", [])),
                },
                "mathpix": {
                    "present": bool(mathpix_sources),
                    "math_entries": int((mathpix_sources or {}).get("math_entries", 0)),
                },
                "composed_sources": composed,
                "attempts": build_result["attempts"],
                "prebuild_staleness": prebuild_staleness,
                "skipped_fresh": False,
                "forced_rebuild": bool(force_rebuild),
                "preserved_generated_abstract": preserved_generated_abstract,
                "preserved_generated_abstract_file": preserved_generated_abstract_file,
                "timings": timings,
            }
        )
    except Exception as exc:  # pragma: no cover - batch resilience
        timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
        paper_status.update(
            {
                "status": "failed",
                "completed_at": now_iso_impl(),
                "error": str(exc),
                "traceback": traceback.format_exc(limit=20),
                "timings": timings,
            }
        )
    return paper_status


__all__ = ["run_paper_job"]


def process_round(
    status: dict[str, Any],
    round_index: int,
    *,
    max_workers: int,
    force_rebuild: bool,
    layout: ProjectLayout | None,
    runtime: Any | None = None,
    now_iso_impl: Callable[[], str] | None = None,
    save_status_impl: Callable[[dict[str, Any], Any], None] | None = None,
    mathpix_credentials_available_impl: Callable[[], bool] | None = None,
    mathpix_submit_workers_impl: Callable[[], int] | None = None,
    mathpix_round_poll_seconds_impl: Callable[[], float] | None = None,
    build_acquisition_route_report_impl: Callable[..., dict[str, Any]] | None = None,
    mathpix_round_coordinator_cls: type[Any] | None = None,
    run_paper_job_impl: Callable[..., dict[str, Any]] | None = None,
) -> None:
    now_iso_impl = now_iso_impl or now_iso
    save_status_impl = save_status_impl or save_status
    mathpix_credentials_available_impl = mathpix_credentials_available_impl or mathpix_credentials_available
    mathpix_submit_workers_impl = mathpix_submit_workers_impl or mathpix_submit_workers
    mathpix_round_poll_seconds_impl = mathpix_round_poll_seconds_impl or mathpix_round_poll_seconds
    build_acquisition_route_report_impl = build_acquisition_route_report_impl or build_acquisition_route_report
    mathpix_round_coordinator_cls = mathpix_round_coordinator_cls or MathpixRoundCoordinator
    run_paper_job_impl = run_paper_job_impl or run_paper_job
    round_name = f"round_{round_index}"
    if force_rebuild:
        round_status = {
            "started_at": now_iso_impl(),
            "completed_at": None,
            "papers": {},
            "force_rebuild": True,
        }
        status.setdefault("rounds", {})[round_name] = round_status
    else:
        round_status = status.setdefault("rounds", {}).setdefault(
            round_name,
            {"started_at": now_iso_impl(), "completed_at": None, "papers": {}},
        )
    papers = status.get("papers", [])

    def update_paper_status(paper_id: str, payload: dict[str, Any]) -> None:
        paper_status = round_status.setdefault("papers", {}).setdefault(paper_id, {"status": "queued"})
        for key, value in payload.items():
            if key == "mathpix" and isinstance(value, dict):
                existing = paper_status.setdefault("mathpix", {})
                if isinstance(existing, dict):
                    existing.update(value)
                else:
                    paper_status["mathpix"] = dict(value)
            else:
                paper_status[key] = value
        save_status_impl(status, runtime)

    if force_rebuild:
        pending_papers = list(papers)
    else:
        pending_papers = [
            paper_id for paper_id in papers if round_status["papers"].get(paper_id, {}).get("status") != "completed"
        ]
    next_index = 0
    active_jobs: dict[Future[dict[str, Any]], str] = {}
    mathpix_prefetch_papers: set[str] = set()
    use_round_mathpix = bool(mathpix_credentials_available_impl() and len(pending_papers) > 1)
    mathpix_coordinator: Any | None = None

    if use_round_mathpix:
        mathpix_prefetch_papers = {
            paper_id
            for paper_id in pending_papers
            if mathpix_prefetch_allowed(build_acquisition_route_report_impl(paper_id, layout=layout))
        }
        use_round_mathpix = bool(mathpix_prefetch_papers)

    if use_round_mathpix:
        mathpix_coordinator = mathpix_round_coordinator_cls(
            sorted(mathpix_prefetch_papers),
            submit_workers=mathpix_submit_workers_impl(),
            poll_seconds=mathpix_round_poll_seconds_impl(),
            status_callback=update_paper_status,
            layout=layout,
        )
        mathpix_coordinator.start()

    def schedule_ready_papers(executor: ThreadPoolExecutor) -> None:
        nonlocal next_index
        while next_index < len(pending_papers) and len(active_jobs) < max_workers:
            paper_id = pending_papers[next_index]
            next_index += 1
            paper_status = round_status["papers"].setdefault(paper_id, {})
            paper_status.update(
                {
                    "started_at": now_iso_impl(),
                    "status": "running",
                }
            )
            submit_kwargs: dict[str, Any] = {"force_rebuild": force_rebuild}
            if mathpix_coordinator is not None and paper_id in mathpix_prefetch_papers:
                submit_kwargs["prefetched_mathpix_future"] = mathpix_coordinator.future_for(paper_id)
            if layout is not None:
                submit_kwargs["layout"] = layout
            active_jobs[executor.submit(run_paper_job_impl, paper_id, **submit_kwargs)] = paper_id
            save_status_impl(status, runtime)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            schedule_ready_papers(executor)
            while active_jobs:
                done, _ = wait(tuple(active_jobs.keys()), return_when=FIRST_COMPLETED)
                for future in done:
                    paper_id = active_jobs.pop(future)
                    paper_status = round_status["papers"].setdefault(paper_id, {})
                    try:
                        result = future.result()
                    except Exception as exc:  # pragma: no cover - defensive
                        result = {
                            "status": "failed",
                            "completed_at": now_iso_impl(),
                            "error": str(exc),
                            "traceback": traceback.format_exc(limit=20),
                        }
                    paper_status.update(result)
                    save_status_impl(status, runtime)
                schedule_ready_papers(executor)
    finally:
        if mathpix_coordinator is not None:
            mathpix_coordinator.close()

    round_status["completed_at"] = now_iso_impl()
    save_status_impl(status, runtime)


__all__ = [
    "process_round",
    "run_paper_job",
]
