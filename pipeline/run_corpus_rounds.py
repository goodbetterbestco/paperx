#!/usr/bin/env python3

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
import json
import os
import socket
import sys
from threading import Event, Thread
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from pipeline.corpus.lexicon_builder import _build_lexicon
from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import (
    CORPUS_DIR,
    ProjectLayout,
    canonical_path,
    canonical_sources_dir,
    current_layout,
)
from pipeline.corpus.metadata import discover_paper_pdf_paths, paper_id_from_pdf_path
from pipeline.orchestrator.round_build import build_best_paper as _build_best_paper_impl
from pipeline.orchestrator.round_document import (
    anomaly_flags as _anomaly_flags,
    copy_existing_abstract_block as _copy_existing_abstract_block,
    desired_flags_for_existing_paper as _desired_flags_for_existing_paper,
    desired_flags_from_composed_sources as _desired_flags_from_composed_sources,
    document_abstract_block as _document_abstract_block,
    document_abstract_text as _document_abstract_text,
    document_has_generated_abstract as _document_has_generated_abstract,
    document_quality_key as _document_quality_key,
    preserve_existing_generated_abstract as _preserve_existing_generated_abstract,
    preserve_existing_generated_abstract_file as _preserve_existing_generated_abstract_file_impl,
)
from pipeline.orchestrator.round_reporting import (
    render_final_report as _render_final_report,
    summarize_round as _summarize_round,
)
from pipeline.orchestrator.source_composition import (
    compose_layout_sources as _compose_layout_sources,
    layout_blocks_by_page as _layout_blocks_by_page,
    page_one_layout_score as _page_one_layout_score,
)
from pipeline.sources.docling import docling_json_to_external_sources, run_docling
from pipeline.sources.external import external_layout_path, external_math_path
from pipeline.sources.mathpix import (
    MATHPIX_PDF_ENDPOINT,
    download_mathpix_pdf,
    fetch_mathpix_pdf_status,
    mathpix_pages_to_external_sources,
    run_mathpix,
    submit_mathpix_pdf,
)
from pipeline.output_artifacts import write_canonical_outputs
from pipeline.output.validation import validate_canonical
from pipeline.reconcile_blocks import reconcile_paper
from pipeline.runtime_paths import ENGINE_ROOT, ensure_repo_tmp_dir, runtime_env
from pipeline.staleness_policy import detect_canonical_staleness


TMP_DIR = ensure_repo_tmp_dir()


@dataclass(frozen=True)
class RoundRuntime:
    layout: ProjectLayout
    batch_dir: Path
    status_path: Path
    report_path: Path
    lexicon_path: Path


def _build_round_runtime(layout: ProjectLayout | None = None) -> RoundRuntime:
    active_layout = layout or current_layout()
    if active_layout.project_mode:
        batch_dir = active_layout.project_status_path().parent
        status_path = active_layout.project_status_path()
        report_path = active_layout.project_report_path()
    else:
        batch_dir = TMP_DIR / "canonical_corpus_rounds"
        status_path = batch_dir / "status.json"
        report_path = batch_dir / "final_summary.md"
    return RoundRuntime(
        layout=active_layout,
        batch_dir=batch_dir,
        status_path=status_path,
        report_path=report_path,
        lexicon_path=active_layout.corpus_lexicon_path,
    )


DEFAULT_RUNTIME = _build_round_runtime()
BATCH_DIR = DEFAULT_RUNTIME.batch_dir
STATUS_PATH = DEFAULT_RUNTIME.status_path
REPORT_PATH = DEFAULT_RUNTIME.report_path
DOCS_DIR = CORPUS_DIR
LEXICON_PATH = DEFAULT_RUNTIME.lexicon_path
ENV_LOCAL_PATH = ENGINE_ROOT / ".env.local"
PER_PAPER_SOURCE_WORKERS = 2


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_env_local() -> dict[str, str]:
    if not ENV_LOCAL_PATH.exists():
        return {}
    loaded: dict[str, str] = {}
    for raw_line in ENV_LOCAL_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        loaded[key] = value
    return loaded


def _configure_runtime_environment() -> None:
    env = runtime_env()
    os.environ.update(env)
    os.environ.update(_read_env_local())


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(0.0, float(raw))
    except ValueError:
        return default


def _paper_ids(*, layout: ProjectLayout | None = None) -> list[str]:
    return [paper_id_from_pdf_path(path, layout=layout) for path in discover_paper_pdf_paths(layout=layout)]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_status(runtime: RoundRuntime | None = None) -> dict[str, Any]:
    active_runtime = runtime or DEFAULT_RUNTIME
    if active_runtime.status_path.exists():
        return json.loads(active_runtime.status_path.read_text(encoding="utf-8"))
    return {
        "started_at": _now_iso(),
        "updated_at": _now_iso(),
        "papers": _paper_ids(layout=active_runtime.layout),
        "rounds": {},
        "notes": [],
    }


def _save_status(status: dict[str, Any], runtime: RoundRuntime | None = None) -> None:
    active_runtime = runtime or DEFAULT_RUNTIME
    status["updated_at"] = _now_iso()
    _write_json(active_runtime.status_path, status)


def _rebuild_lexicon(runtime: RoundRuntime | None = None) -> dict[str, Any]:
    active_runtime = runtime or DEFAULT_RUNTIME
    lexicon = _build_lexicon(layout=active_runtime.layout)
    _write_json(active_runtime.lexicon_path, lexicon)
    return lexicon


def _mathpix_credentials_available() -> bool:
    return bool(os.environ.get("MATHPIX_APP_ID") and os.environ.get("MATHPIX_APP_KEY"))


def _assert_mathpix_dns_available(endpoint: str = MATHPIX_PDF_ENDPOINT) -> None:
    host = urlparse(endpoint).hostname or ""
    if not host:
        raise SystemExit(f"Mathpix DNS preflight failed: could not determine hostname from endpoint {endpoint!r}.")
    try:
        socket.getaddrinfo(host, 443)
    except OSError as exc:
        raise SystemExit(
            "Mathpix DNS preflight failed for "
            f"{host}: {exc}. This usually means the corpus pipeline is running inside a "
            "sandboxed environment without external DNS/network access. Rerun the corpus "
            "outside the sandbox or with escalated network access."
        ) from exc


def _mathpix_submit_workers() -> int:
    return _int_env("STEPVIEW_MATHPIX_SUBMIT_WORKERS", 20)


def _mathpix_round_poll_seconds() -> float:
    return _float_env("STEPVIEW_MATHPIX_ROUND_POLL_SECONDS", 30.0)


def _docling_device() -> str | None:
    configured = os.environ.get("STEPVIEW_DOCLING_DEVICE", "").strip().lower()
    if configured in {"auto", "cpu", "mps", "cuda", "xpu"}:
        return configured
    if sys.platform == "darwin":
        return "mps"
    return None


def _snapshot_external_source(path: Path, snapshot_name: str) -> Path | None:
    if not path.exists():
        return None
    destination = path.parent / snapshot_name
    destination.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return destination


def _build_docling_sources(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any]:
    docling_json_path = run_docling(paper_id, device=_docling_device(), layout=layout)
    docling_document = json.loads(docling_json_path.read_text(encoding="utf-8"))
    external_layout, math = docling_json_to_external_sources(docling_document, paper_id, layout=layout)
    sources_dir = external_layout_path(paper_id, layout=layout).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    docling_layout_path = sources_dir / "docling-layout.json"
    docling_math_path = sources_dir / "docling-math.json"
    _write_json(docling_layout_path, external_layout)
    _write_json(docling_math_path, math)
    return {
        "docling_json": str(docling_json_path),
        "layout": external_layout,
        "math": math,
        "layout_path": str(docling_layout_path),
        "math_path": str(docling_math_path),
    }


def _build_mathpix_sources_from_result(
    paper_id: str,
    mathpix_result: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    payloads = list(mathpix_result.get("pages") or [])
    external_layout, math = mathpix_pages_to_external_sources(payloads, paper_id, layout=layout)
    sources_dir = external_layout_path(paper_id, layout=layout).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    mathpix_layout_path = sources_dir / "mathpix-layout.json"
    mathpix_math_path = sources_dir / "mathpix-math.json"
    _write_json(mathpix_layout_path, external_layout)
    _write_json(mathpix_math_path, math)
    result = {
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


def _build_mathpix_sources(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any] | None:
    if not _mathpix_credentials_available():
        return None
    mathpix_result = run_mathpix(paper_id, layout=layout)
    return _build_mathpix_sources_from_result(paper_id, mathpix_result, layout=layout)


def _timed_call(label: str, fn: Any, /, *args: Any, **kwargs: Any) -> tuple[str, float, Any]:
    started = time.perf_counter()
    result = fn(*args, **kwargs)
    return label, round(time.perf_counter() - started, 3), result


class _MathpixRoundCoordinator:
    def __init__(
        self,
        paper_ids: list[str],
        *,
        submit_workers: int,
        poll_seconds: float,
        status_callback: Callable[[str, dict[str, Any]], None] | None = None,
        layout: ProjectLayout | None = None,
    ) -> None:
        self._paper_ids = list(paper_ids)
        self._submit_workers = max(1, submit_workers)
        self._poll_seconds = max(1.0, poll_seconds)
        self._futures = {paper_id: Future() for paper_id in self._paper_ids}
        self._thread = Thread(target=self._run, name="mathpix-round-coordinator", daemon=True)
        self._stop = Event()
        self._status_callback = status_callback
        self._layout = layout

    def start(self) -> None:
        self._thread.start()

    def future_for(self, paper_id: str) -> Future[dict[str, Any]]:
        return self._futures[paper_id]

    def close(self) -> None:
        self._stop.set()
        self._thread.join()

    def _publish(self, paper_id: str, payload: dict[str, Any]) -> None:
        if self._status_callback is not None:
            self._status_callback(paper_id, payload)

    def _run(self) -> None:
        submit_started: dict[str, float] = {}
        submitted_jobs: dict[str, str] = {}
        pending_submissions: dict[Future[str], str] = {}

        with ThreadPoolExecutor(max_workers=self._submit_workers) as executor:
            for paper_id in self._paper_ids:
                submit_started[paper_id] = time.perf_counter()
                self._publish(
                    paper_id,
                    {
                        "mathpix": {
                            "phase": "submit_queued",
                            "submit_queued_at": _now_iso(),
                        }
                    },
                )
                pending_submissions[executor.submit(submit_mathpix_pdf, paper_id, layout=self._layout)] = paper_id

            next_poll_at = time.monotonic() + self._poll_seconds
            while (pending_submissions or submitted_jobs) and not self._stop.is_set():
                done_submits: set[Future[str]] = set()
                if pending_submissions:
                    done_submits, _ = wait(tuple(pending_submissions.keys()), timeout=0.2, return_when=FIRST_COMPLETED)

                for future in done_submits:
                    paper_id = pending_submissions.pop(future)
                    paper_future = self._futures[paper_id]
                    try:
                        pdf_id = future.result()
                        submitted_jobs[paper_id] = pdf_id
                        self._publish(
                            paper_id,
                            {
                                "mathpix": {
                                    "phase": "submitted",
                                    "submit_completed_at": _now_iso(),
                                    "pdf_id": pdf_id,
                                }
                            },
                        )
                    except Exception as exc:  # pragma: no cover - defensive
                        self._publish(
                            paper_id,
                            {
                                "mathpix": {
                                    "phase": "submit_failed",
                                    "failed_at": _now_iso(),
                                    "error": str(exc),
                                }
                            },
                        )
                        if not paper_future.done():
                            paper_future.set_exception(exc)

                now = time.monotonic()
                if submitted_jobs and now >= next_poll_at:
                    for paper_id, pdf_id in list(submitted_jobs.items()):
                        paper_future = self._futures[paper_id]
                        if paper_future.done():
                            submitted_jobs.pop(paper_id, None)
                            continue
                        try:
                            status = fetch_mathpix_pdf_status(pdf_id)
                            state = str(status.get("status", "")).strip().lower()
                            self._publish(
                                paper_id,
                                {
                                    "mathpix": {
                                        "phase": "polling",
                                        "last_polled_at": _now_iso(),
                                        "pdf_id": pdf_id,
                                        "remote_status": state or "unknown",
                                    }
                                },
                            )
                            if state == "completed":
                                result = download_mathpix_pdf(paper_id, pdf_id, layout=self._layout)
                                result["elapsed_seconds"] = round(time.perf_counter() - submit_started[paper_id], 3)
                                self._publish(
                                    paper_id,
                                    {
                                        "mathpix": {
                                            "phase": "completed",
                                            "completed_at": _now_iso(),
                                            "pdf_id": pdf_id,
                                            "remote_status": state,
                                            "elapsed_seconds": result["elapsed_seconds"],
                                        }
                                    },
                                )
                                paper_future.set_result(result)
                                submitted_jobs.pop(paper_id, None)
                            elif state == "error" or status.get("error"):
                                raise RuntimeError(f"Mathpix PDF {pdf_id} failed: {status}")
                        except Exception as exc:  # pragma: no cover - defensive
                            self._publish(
                                paper_id,
                                {
                                    "mathpix": {
                                        "phase": "failed",
                                        "failed_at": _now_iso(),
                                        "pdf_id": pdf_id,
                                        "error": str(exc),
                                    }
                                },
                            )
                            if not paper_future.done():
                                paper_future.set_exception(exc)
                            submitted_jobs.pop(paper_id, None)
                    next_poll_at = time.monotonic() + self._poll_seconds

            if self._stop.is_set():
                for paper_id, paper_future in self._futures.items():
                    if not paper_future.done():
                        self._publish(
                            paper_id,
                            {
                                "mathpix": {
                                    "phase": "stopped",
                                    "stopped_at": _now_iso(),
                                }
                            },
                        )
                        paper_future.set_exception(RuntimeError(f"Mathpix round coordinator stopped before {paper_id} completed."))


def _build_extraction_sources_for_paper(
    paper_id: str,
    *,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
    layout: ProjectLayout | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]:
    timings: dict[str, float] = {}
    mathpix_enabled = _mathpix_credentials_available()
    max_workers = 1 if prefetched_mathpix_future is not None else (PER_PAPER_SOURCE_WORKERS if mathpix_enabled else 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        docling_future = executor.submit(_timed_call, "docling", _build_docling_sources, paper_id, layout=layout)
        local_mathpix_future: Future[tuple[str, float, Any]] | None = None
        if mathpix_enabled and prefetched_mathpix_future is None:
            local_mathpix_future = executor.submit(
                _timed_call,
                "mathpix",
                _build_mathpix_sources,
                paper_id,
                layout=layout,
            )

        _, docling_seconds, docling_sources = docling_future.result()
        timings["docling_seconds"] = docling_seconds
        mathpix_sources = None
        if prefetched_mathpix_future is not None:
            mathpix_result = prefetched_mathpix_future.result()
            mathpix_sources = _build_mathpix_sources_from_result(paper_id, mathpix_result, layout=layout)
            mathpix_seconds = float(mathpix_result.get("elapsed_seconds", 0.0))
            timings["mathpix_seconds"] = mathpix_seconds
        elif local_mathpix_future is not None:
            _, mathpix_seconds, mathpix_sources = local_mathpix_future.result()
            timings["mathpix_seconds"] = mathpix_seconds
        else:
            timings["mathpix_seconds"] = 0.0

    return docling_sources, mathpix_sources, timings


def _compose_external_sources(
    paper_id: str,
    *,
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    final_layout = _compose_layout_sources(docling_sources, mathpix_sources)
    final_math = {}
    if mathpix_sources and mathpix_sources.get("math", {}).get("entries"):
        final_math = mathpix_sources["math"]
    elif docling_sources:
        final_math = docling_sources["math"]
    else:
        final_math = {"engine": "none", "entries": []}
    layout_path = external_layout_path(paper_id, layout=layout)
    math_path = external_math_path(paper_id, layout=layout)
    _write_json(layout_path, final_layout)
    _write_json(math_path, final_math)
    return {
        "layout_path": str(layout_path),
        "math_path": str(math_path),
        "layout_engine": final_layout.get("engine"),
        "layout_blocks": len(final_layout.get("blocks", [])),
        "math_engine": final_math.get("engine"),
        "math_entries": len(final_math.get("entries", [])),
    }


def _write_canonical_outputs(
    paper_id: str,
    document: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    return write_canonical_outputs(paper_id, document, include_review=True, layout=layout)


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def _paper_has_generated_abstract_file(paper_id: str, *, layout: ProjectLayout | None = None) -> bool:
    return (canonical_sources_dir(paper_id, layout=layout) / "generated-abstract.txt").exists()


def _preserve_existing_generated_abstract_file(
    paper_id: str,
    existing_document: dict[str, Any] | None,
    new_document: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
) -> bool:
    return _preserve_existing_generated_abstract_file_impl(
        paper_id,
        existing_document,
        new_document,
        abstract_file_exists=lambda current_paper_id: _paper_has_generated_abstract_file(
            current_paper_id,
            layout=layout,
        ),
    )


def _existing_composed_sources(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any]:
    external_layout = _load_json_if_exists(external_layout_path(paper_id, layout=layout)) or {"engine": "none", "blocks": []}
    math = _load_json_if_exists(external_math_path(paper_id, layout=layout)) or {"engine": "none", "entries": []}
    return {
        "layout_path": str(external_layout_path(paper_id, layout=layout)),
        "math_path": str(external_math_path(paper_id, layout=layout)),
        "layout_engine": external_layout.get("engine"),
        "layout_blocks": len(external_layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
    }


def _build_paper(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any]:
    active_layout = layout or current_layout()
    return _build_best_paper_impl(
        paper_id,
        layout=active_layout,
        mode_configs=(
            {"use_external_layout": True, "use_external_math": True, "text_engine": "native", "label": "hybrid"},
            {"use_external_layout": True, "use_external_math": False, "text_engine": "native", "label": "layout_only"},
            {"use_external_layout": False, "use_external_math": False, "text_engine": "native", "label": "native"},
        ),
        build_pipeline_config=build_pipeline_config,
        reconcile_paper=reconcile_paper,
        validate_canonical=validate_canonical,
        anomaly_flags=_anomaly_flags,
        document_quality_key=_document_quality_key,
    )


def _run_paper_job(
    paper_id: str,
    *,
    force_rebuild: bool,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    active_layout = layout or current_layout()
    canonical_target = canonical_path(paper_id, layout=active_layout)
    paper_status: dict[str, Any] = {}
    timings: dict[str, float] = {}
    overall_started = time.perf_counter()
    try:
        existing_document = _load_json_if_exists(canonical_target)
        existing_composed = _existing_composed_sources(paper_id, layout=active_layout)
        desired_flags = _desired_flags_for_existing_paper(existing_document, existing_composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness(
            canonical_target,
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        if not force_rebuild and not prebuild_staleness.get("stale") and existing_document is not None:
            refresh_started = time.perf_counter()
            outputs = _write_canonical_outputs(paper_id, existing_document, layout=active_layout)
            timings["refresh_outputs_seconds"] = round(time.perf_counter() - refresh_started, 3)
            anomalies = _anomaly_flags(existing_document)
            timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
            paper_status.update(
                {
                    "status": "completed",
                    "completed_at": _now_iso(),
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

        docling_sources, mathpix_sources, extraction_timings = _build_extraction_sources_for_paper(
            paper_id,
            prefetched_mathpix_future=prefetched_mathpix_future,
            layout=active_layout,
        )
        timings.update(extraction_timings)

        compose_started = time.perf_counter()
        composed = _compose_external_sources(
            paper_id,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
            layout=active_layout,
        )
        timings["compose_sources_seconds"] = round(time.perf_counter() - compose_started, 3)

        desired_flags = _desired_flags_for_existing_paper(existing_document, composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness(
            canonical_target,
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        build_started = time.perf_counter()
        build_result = _build_paper(paper_id, layout=layout)
        timings["build_seconds"] = round(time.perf_counter() - build_started, 3)
        document = build_result["document"]
        preserved_generated_abstract = _preserve_existing_generated_abstract(existing_document, document)
        preserved_generated_abstract_file = _preserve_existing_generated_abstract_file(
            paper_id,
            existing_document,
            document,
            layout=active_layout,
        )
        outputs = _write_canonical_outputs(paper_id, document, layout=active_layout)
        anomalies = _anomaly_flags(document)
        timings["total_seconds"] = round(time.perf_counter() - overall_started, 3)
        paper_status.update(
            {
                "status": "completed",
                "completed_at": _now_iso(),
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
                "completed_at": _now_iso(),
                "error": str(exc),
                "traceback": traceback.format_exc(limit=20),
                "timings": timings,
            }
        )
    return paper_status


def _process_round(
    status: dict[str, Any],
    round_index: int,
    *,
    max_workers: int,
    force_rebuild: bool,
    layout: ProjectLayout | None = None,
    runtime: RoundRuntime | None = None,
) -> None:
    active_runtime = runtime or DEFAULT_RUNTIME
    round_name = f"round_{round_index}"
    if force_rebuild:
        round_status = {
            "started_at": _now_iso(),
            "completed_at": None,
            "papers": {},
            "force_rebuild": True,
        }
        status.setdefault("rounds", {})[round_name] = round_status
    else:
        round_status = status.setdefault("rounds", {}).setdefault(
            round_name,
            {"started_at": _now_iso(), "completed_at": None, "papers": {}},
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
        _save_status(status, active_runtime)

    if force_rebuild:
        pending_papers = list(papers)
    else:
        pending_papers = [
            paper_id for paper_id in papers if round_status["papers"].get(paper_id, {}).get("status") != "completed"
        ]
    next_index = 0
    active_jobs: dict[Future[dict[str, Any]], str] = {}
    use_round_mathpix = bool(_mathpix_credentials_available() and len(pending_papers) > 1)
    mathpix_coordinator: _MathpixRoundCoordinator | None = None

    if use_round_mathpix:
        mathpix_coordinator = _MathpixRoundCoordinator(
            pending_papers,
            submit_workers=_mathpix_submit_workers(),
            poll_seconds=_mathpix_round_poll_seconds(),
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
            paper_status.update({
                "started_at": _now_iso(),
                "status": "running",
            })
            submit_kwargs: dict[str, Any] = {"force_rebuild": force_rebuild}
            if mathpix_coordinator is not None:
                submit_kwargs["prefetched_mathpix_future"] = mathpix_coordinator.future_for(paper_id)
            if layout is not None:
                submit_kwargs["layout"] = layout
            active_jobs[executor.submit(_run_paper_job, paper_id, **submit_kwargs)] = paper_id
            _save_status(status, active_runtime)

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
                            "completed_at": _now_iso(),
                            "error": str(exc),
                            "traceback": traceback.format_exc(limit=20),
                        }
                    paper_status.update(result)
                    _save_status(status, active_runtime)
                schedule_ready_papers(executor)
    finally:
        if mathpix_coordinator is not None:
            mathpix_coordinator.close()

    round_status["completed_at"] = _now_iso()
    _save_status(status, active_runtime)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run canonical extraction across the corpus. By default this runs one round; round 2 is opt-in."
    )
    parser.add_argument(
        "--start-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to start from. Defaults to 1.",
    )
    parser.add_argument(
        "--end-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to end on. Defaults to 1.",
    )
    parser.add_argument(
        "--stop-after-round",
        type=int,
        choices=(1, 2),
        default=None,
        help="Optional round number after which execution should stop even if later rounds are configured.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum number of papers to process concurrently within a round. Defaults to 1.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Rebuild every targeted paper even when the canonical is already fresh.",
    )
    return parser.parse_args()


def run_rounds(
    *,
    start_round: int = 1,
    end_round: int = 1,
    stop_after_round: int | None = None,
    max_workers: int = 1,
    force_rebuild: bool = False,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    if start_round > end_round:
        raise SystemExit("--start-round cannot be greater than --end-round")
    if max_workers < 1:
        raise SystemExit("--max-workers must be at least 1")

    _configure_runtime_environment()
    if _mathpix_credentials_available():
        _assert_mathpix_dns_available()
    runtime = _build_round_runtime(layout)
    runtime.batch_dir.mkdir(parents=True, exist_ok=True)

    status = _load_status(runtime)
    status["papers"] = _paper_ids(layout=runtime.layout)
    status["notes"] = [
        "Round processing uses Docling for layout, Mathpix for math when credentials are available, and lexicon refresh at round boundaries.",
        f"Corpus temp paths are redirected into {TMP_DIR}.",
        f"Configured worker concurrency: {max_workers}.",
        "Fresh canonicals are skipped when source inputs, build flags, and pipeline fingerprints still match.",
        "Mathpix defaults to whole-PDF round coordination when multiple papers are pending and credentials are available.",
    ]
    if runtime.layout.project_mode:
        status["notes"].append(f"Project reports are written into {runtime.batch_dir}.")
    if force_rebuild:
        status["notes"].append("Fresh canonicals are still rebuilt because --force-rebuild was enabled.")
    _save_status(status, runtime)

    _rebuild_lexicon(runtime)
    for round_index in range(start_round, end_round + 1):
        _process_round(
            status,
            round_index,
            max_workers=max_workers,
            force_rebuild=bool(force_rebuild),
            layout=runtime.layout,
            runtime=runtime,
        )
        _rebuild_lexicon(runtime)
        if stop_after_round == round_index:
            break

    report = _render_final_report(status)
    runtime.report_path.write_text(report, encoding="utf-8")
    return {
        "status_path": str(runtime.status_path),
        "report_path": str(runtime.report_path),
        "rounds": list(status.get("rounds", {}).keys()),
        "papers": len(status.get("papers", [])),
    }


def main() -> int:
    args = _parse_args()
    result = run_rounds(
        start_round=args.start_round,
        end_round=args.end_round,
        stop_after_round=args.stop_after_round,
        max_workers=args.max_workers,
        force_rebuild=bool(args.force_rebuild),
    )
    print(
        json.dumps(
            result,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
