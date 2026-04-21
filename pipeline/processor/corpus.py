from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import traceback
import time
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.corpus.state import cleanup_processed_runtime_artifacts
from pipeline.corpus_layout import ProjectLayout
from pipeline.processor.mathpix import MathpixCoordinator
from pipeline.processor.quality import anomaly_flags as default_anomaly_flags
from pipeline.processor.report import render_report
from pipeline.processor.sources import (
    build_extraction_sources_for_paper,
    compose_external_sources,
    mathpix_prefetch_allowed,
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
    mathpix_round_poll_seconds,
    mathpix_submit_workers,
)
from pipeline.processor.paper import build_paper


def run_paper_job(
    paper_id: str,
    *,
    layout: ProjectLayout,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
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

        build_started = time.perf_counter()
        preferred_text_engine = (
            "hybrid"
            if str(composed.get("acquisition_route") or "") in {"scan_or_image_heavy", "degraded_or_garbled"}
            else "native"
        )
        build_result = build_paper_impl(
            paper_id,
            text_engine=preferred_text_engine,
            include_review=True,
            layout=layout,
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
                "composed_sources": composed,
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

    def update_paper_status(paper_id: str, payload: dict[str, Any]) -> None:
        paper_status = run_status.setdefault("papers", {}).setdefault(paper_id, {"status": "queued"})
        for key, value in payload.items():
            if key == "mathpix" and isinstance(value, dict):
                existing = paper_status.setdefault("mathpix", {})
                if isinstance(existing, dict):
                    existing.update(value)
                else:
                    paper_status["mathpix"] = dict(value)
            else:
                paper_status[key] = value
        save_status(status, runtime)

    mathpix_prefetch_papers: set[str] = set()
    mathpix_coordinator: MathpixCoordinator | None = None
    use_mathpix = bool(mathpix_credentials_available() and len(pending_papers) > 1)
    if use_mathpix:
        mathpix_prefetch_papers = {
            paper_id
            for paper_id in pending_papers
            if mathpix_prefetch_allowed(build_acquisition_route_report(paper_id, layout=layout))
        }
        use_mathpix = bool(mathpix_prefetch_papers)
    if use_mathpix:
        mathpix_coordinator = MathpixCoordinator(
            sorted(mathpix_prefetch_papers),
            submit_workers=mathpix_submit_workers(),
            poll_seconds=mathpix_round_poll_seconds(),
            status_callback=update_paper_status,
            layout=layout,
        )
        mathpix_coordinator.start()

    def schedule_ready(executor: ThreadPoolExecutor) -> None:
        nonlocal next_index
        while next_index < len(pending_papers) and len(active_jobs) < max_workers:
            paper_id = pending_papers[next_index]
            next_index += 1
            run_status["papers"].setdefault(paper_id, {}).update(
                {"started_at": now_iso(), "status": "running"}
            )
            submit_kwargs: dict[str, Any] = {"layout": layout}
            if mathpix_coordinator is not None and paper_id in mathpix_prefetch_papers:
                submit_kwargs["prefetched_mathpix_future"] = mathpix_coordinator.future_for(paper_id)
            active_jobs[executor.submit(run_paper_job_impl, paper_id, **submit_kwargs)] = paper_id
            save_status(status, runtime)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            schedule_ready(executor)
            while active_jobs:
                done, _ = wait(tuple(active_jobs.keys()), return_when=FIRST_COMPLETED)
                for future in done:
                    paper_id = active_jobs.pop(future)
                    run_status["papers"].setdefault(paper_id, {}).update(future.result())
                    save_status(status, runtime)
                schedule_ready(executor)
    finally:
        if mathpix_coordinator is not None:
            mathpix_coordinator.close()

    run_status["completed_at"] = now_iso()
    save_status(status, runtime)


def process_corpus(
    *,
    max_workers: int = 20,
    layout: ProjectLayout | None = None,
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
        "Each paper is processed once from its PDF into canonical output and figures.",
        "Mathpix uses whole-PDF coordination when multiple papers are pending and credentials are available.",
    ]
    if runtime.layout.project_mode:
        status["notes"].append(f"Project reports are written into {runtime.batch_dir}.")
    save_status(status, runtime)

    run_corpus_once(
        status,
        max_workers=max_workers,
        layout=runtime.layout,
        runtime=runtime,
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
