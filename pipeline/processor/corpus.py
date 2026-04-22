from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import traceback
import time
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.corpus.state import cleanup_processed_runtime_artifacts
from pipeline.corpus_layout import ProjectLayout
from pipeline.processor.quality import anomaly_flags as default_anomaly_flags
from pipeline.processor.report import render_report
from pipeline.processor.sources import (
    build_extraction_sources_for_paper,
    compose_external_sources,
    write_canonical_outputs_for_run,
)
from pipeline.processor.status import (
    CorpusRuntime,
    build_runtime,
    configure_runtime_environment,
    load_status,
    now_iso,
    paper_ids,
    save_status,
)
from pipeline.processor.settings import (
    assert_mathpix_dns_available,
    mathpix_credentials_available,
)
from pipeline.processor.paper import build_paper


def _progress_snapshot(
    paper_ids: list[str],
    run_status: dict[str, Any],
) -> dict[str, int]:
    passed = 0
    failed = 0
    queued = 0
    processing = 0

    paper_statuses = dict(run_status.get("papers", {}))
    for paper_id in paper_ids:
        payload = dict(paper_statuses.get(paper_id) or {})
        state = str(payload.get("status", "queued") or "queued")
        if state == "completed":
            passed += 1
        elif state == "failed":
            failed += 1
        elif state == "queued":
            queued += 1
        else:
            processing += 1

    return {
        "total": len(paper_ids),
        "queued": queued,
        "processing": processing,
        "processed": passed + failed,
        "passed": passed,
        "failed": failed,
    }


def run_paper_job(
    paper_id: str,
    *,
    layout: ProjectLayout,
    now_iso_impl: Callable[[], str] | None = None,
    build_extraction_sources_for_paper_impl: Callable[..., tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]] | None = None,
    compose_external_sources_impl: Callable[..., dict[str, Any]] | None = None,
    build_paper_impl: Callable[..., Any] | None = None,
    write_canonical_outputs_impl: Callable[..., dict[str, Any]] | None = None,
    anomaly_flags_impl: Callable[[dict[str, Any]], list[str]] | None = None,
) -> dict[str, Any]:
    now_iso_impl = now_iso_impl or now_iso
    build_extraction_sources_for_paper_impl = build_extraction_sources_for_paper_impl or build_extraction_sources_for_paper
    compose_external_sources_impl = compose_external_sources_impl or compose_external_sources
    build_paper_impl = build_paper_impl or build_paper
    write_canonical_outputs_impl = write_canonical_outputs_impl or write_canonical_outputs_for_run
    anomaly_flags_impl = anomaly_flags_impl or default_anomaly_flags

    timings: dict[str, float] = {}
    overall_started = time.perf_counter()
    paper_status: dict[str, Any] = {}
    try:
        route_started = time.perf_counter()
        acquisition_route = build_acquisition_route_report(paper_id, layout=layout)
        timings["route_seconds"] = round(time.perf_counter() - route_started, 3)
        docling_sources, mathpix_sources, extraction_timings = build_extraction_sources_for_paper_impl(
            paper_id,
            acquisition_route=acquisition_route,
            layout=layout,
        )
        timings.update(extraction_timings)

        compose_started = time.perf_counter()
        composed = compose_external_sources_impl(
            paper_id,
            acquisition_route=acquisition_route,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
        )
        timings["compose_sources_seconds"] = round(time.perf_counter() - compose_started, 3)

        build_started = time.perf_counter()
        build_result = build_paper_impl(
            paper_id,
            include_review=True,
            layout=layout,
            prepared_sources=composed,
        )
        timings["build_seconds"] = round(time.perf_counter() - build_started, 3)
        document = build_result.document if hasattr(build_result, "document") else build_result["document"]
        outputs = write_canonical_outputs_impl(paper_id, document, layout=layout)
        anomalies = anomaly_flags_impl(document)
        timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
        paper_status.update(
            {
                "status": "completed",
                "completed_at": now_iso_impl(),
                "mode": "processed",
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
                "acquisition": {
                    "owners": {
                        "layout": composed.get("layout_owner"),
                        "math": composed.get("math_owner"),
                        "metadata": composed.get("metadata_owner"),
                        "references": composed.get("reference_owner"),
                    },
                    "ownership": composed.get("ownership", {}),
                    "execution": composed.get("acquisition_execution", {}),
                },
                "acquisition_sources": composed,
                "attempts": [],
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


def run_corpus_once(
    status: dict[str, Any],
    *,
    max_workers: int,
    layout: ProjectLayout,
    runtime: CorpusRuntime,
    run_paper_job_impl: Callable[..., dict[str, Any]] | None = None,
    progress_callback: Callable[[dict[str, int]], None] | None = None,
) -> None:
    run_paper_job_impl = run_paper_job_impl or run_paper_job
    run_status = {
        "started_at": now_iso(),
        "completed_at": None,
        "papers": {},
    }
    status.setdefault("runs", []).append(run_status)
    pending_papers = list(status.get("papers", []))
    active_jobs: dict[Future[dict[str, Any]], str] = {}
    next_index = 0
    reported_snapshot: dict[str, int] | None = None

    def schedule_ready(executor: ThreadPoolExecutor) -> None:
        nonlocal next_index
        while next_index < len(pending_papers) and len(active_jobs) < max_workers:
            paper_id = pending_papers[next_index]
            next_index += 1
            run_status["papers"].setdefault(paper_id, {}).update(
                {"started_at": now_iso(), "status": "running"}
            )
            active_jobs[executor.submit(run_paper_job_impl, paper_id, layout=layout)] = paper_id
            save_status(status, runtime)

    def maybe_report_progress() -> None:
        nonlocal reported_snapshot
        if progress_callback is None:
            return
        snapshot = _progress_snapshot(pending_papers, run_status)
        if snapshot != reported_snapshot:
            reported_snapshot = dict(snapshot)
            progress_callback(snapshot)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        schedule_ready(executor)
        maybe_report_progress()
        while active_jobs:
            done, _ = wait(tuple(active_jobs.keys()), return_when=FIRST_COMPLETED)
            for future in done:
                paper_id = active_jobs.pop(future)
                run_status["papers"].setdefault(paper_id, {}).update(future.result())
                save_status(status, runtime)
            schedule_ready(executor)
            maybe_report_progress()

    run_status["completed_at"] = now_iso()
    save_status(status, runtime)


def process_corpus(
    *,
    max_workers: int = 20,
    layout: ProjectLayout | None = None,
    progress_callback: Callable[[dict[str, int]], None] | None = None,
) -> dict[str, Any]:
    if max_workers < 1:
        raise SystemExit("--max-workers must be at least 1")
    configure_runtime_environment()
    if mathpix_credentials_available():
        assert_mathpix_dns_available()
    runtime = build_runtime(layout)
    runtime.batch_dir.mkdir(parents=True, exist_ok=True)

    status = load_status(runtime)
    status["papers"] = paper_ids(layout=runtime.layout)
    status["notes"] = [
        "Processing uses Docling for layout and Mathpix for math when credentials are available.",
        "Temporary process files use the system temp area and are not retained as repo artifacts.",
        f"Configured worker concurrency: {max_workers}.",
        "Each paper is routed once, then processed from its PDF into canonical output and figures.",
        "Mathpix runs only within eligible paper jobs; there is no corpus-wide routing barrier before processing starts.",
    ]
    save_status(status, runtime)

    run_corpus_once(
        status,
        max_workers=max_workers,
        layout=runtime.layout,
        runtime=runtime,
        progress_callback=progress_callback,
    )

    cleanup = cleanup_processed_runtime_artifacts(runtime.layout)
    if cleanup.get("removed_paths"):
        status["cleanup"] = cleanup
        status["notes"].append(
            f"Legacy paper-local runtime artifacts were removed after processing ({cleanup['removed_file_count']} files)."
        )
        save_status(status, runtime)

    runtime.report_path.write_text(render_report(status), encoding="utf-8")
    return {
        "status_path": str(runtime.status_path),
        "report_path": str(runtime.report_path),
        "runs": len(status.get("runs", [])),
        "papers": len(status.get("papers", [])),
        "cleanup": cleanup,
    }
