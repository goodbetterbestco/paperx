#!/usr/bin/env python3

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import json
import os
import re
import socket
import sys
from threading import Event, Thread
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from pipeline.build_corpus_lexicon import _build_lexicon
from pipeline.corpus_layout import (
    CORPUS_DIR,
    CORPUS_LEXICON_PATH,
    PROJECT_MODE,
    canonical_path,
    canonical_sources_dir,
    project_report_path,
    project_status_path,
)
from pipeline.corpus_metadata import discover_paper_pdf_paths, paper_id_from_pdf_path
from pipeline.docling_adapter import docling_json_to_external_sources, run_docling
from pipeline.external_sources import external_layout_path, external_math_path
from pipeline.mathpix_adapter import (
    MATHPIX_PDF_ENDPOINT,
    download_mathpix_pdf,
    fetch_mathpix_pdf_status,
    mathpix_pages_to_external_sources,
    run_mathpix,
    submit_mathpix_pdf,
)
from pipeline.output_artifacts import build_summary, write_canonical_outputs
from pipeline.policies.abstract_quality import abstract_quality_flags, abstract_quality_rank
from pipeline.policies.completeness import (
    block_text as completeness_block_text,
    document_expects_figures,
    document_expects_references,
)
from pipeline.reconcile_blocks import reconcile_paper
from pipeline.runtime_paths import ENGINE_ROOT, ensure_repo_tmp_dir, runtime_env
from pipeline.staleness_policy import detect_canonical_staleness
from pipeline.validate_canonical import validate_canonical


TMP_DIR = ensure_repo_tmp_dir()
if PROJECT_MODE:
    BATCH_DIR = project_status_path().parent
    STATUS_PATH = project_status_path()
    REPORT_PATH = project_report_path()
else:
    BATCH_DIR = TMP_DIR / "canonical_corpus_rounds"
    STATUS_PATH = BATCH_DIR / "status.json"
    REPORT_PATH = BATCH_DIR / "final_summary.md"
DOCS_DIR = CORPUS_DIR
LEXICON_PATH = CORPUS_LEXICON_PATH
ENV_LOCAL_PATH = ENGINE_ROOT / ".env.local"
PER_PAPER_SOURCE_WORKERS = 2
ABSTRACT_PAGE_MARKER_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)
INTRO_PAGE_MARKER_RE = re.compile(r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s*introduction\b", re.IGNORECASE)
LAYOUT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"this manuscript version is made available|available online|article history|doi\b)\b",
    re.IGNORECASE,
)
ANOMALY_WEIGHTS = {
    "bad_abstract": 5,
    "missing_authors": 4,
    "missing_abstract": 2,
    "weak_sections": 2,
    "missing_references": 1,
    "missing_figures": 1,
}
GENERATED_ABSTRACT_NOTE_PREFIX = "Generated abstract from "


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


def _paper_ids() -> list[str]:
    return [paper_id_from_pdf_path(path) for path in discover_paper_pdf_paths()]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_status() -> dict[str, Any]:
    if STATUS_PATH.exists():
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    return {
        "started_at": _now_iso(),
        "updated_at": _now_iso(),
        "papers": _paper_ids(),
        "rounds": {},
        "notes": [],
    }


def _save_status(status: dict[str, Any]) -> None:
    status["updated_at"] = _now_iso()
    _write_json(STATUS_PATH, status)


def _rebuild_lexicon() -> dict[str, Any]:
    lexicon = _build_lexicon()
    _write_json(LEXICON_PATH, lexicon)
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


def _build_docling_sources(paper_id: str) -> dict[str, Any]:
    docling_json_path = run_docling(paper_id, device=_docling_device())
    docling_document = json.loads(docling_json_path.read_text(encoding="utf-8"))
    layout, math = docling_json_to_external_sources(docling_document, paper_id)
    sources_dir = external_layout_path(paper_id).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    docling_layout_path = sources_dir / "docling-layout.json"
    docling_math_path = sources_dir / "docling-math.json"
    _write_json(docling_layout_path, layout)
    _write_json(docling_math_path, math)
    return {
        "docling_json": str(docling_json_path),
        "layout": layout,
        "math": math,
        "layout_path": str(docling_layout_path),
        "math_path": str(docling_math_path),
    }


def _build_mathpix_sources_from_result(paper_id: str, mathpix_result: dict[str, Any]) -> dict[str, Any]:
    payloads = list(mathpix_result.get("pages") or [])
    layout, math = mathpix_pages_to_external_sources(payloads, paper_id)
    sources_dir = external_layout_path(paper_id).parent
    sources_dir.mkdir(parents=True, exist_ok=True)
    mathpix_layout_path = sources_dir / "mathpix-layout.json"
    mathpix_math_path = sources_dir / "mathpix-math.json"
    _write_json(mathpix_layout_path, layout)
    _write_json(mathpix_math_path, math)
    result = {
        "layout": layout,
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


def _build_mathpix_sources(paper_id: str) -> dict[str, Any] | None:
    if not _mathpix_credentials_available():
        return None
    mathpix_result = run_mathpix(paper_id)
    return _build_mathpix_sources_from_result(paper_id, mathpix_result)


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
    ) -> None:
        self._paper_ids = list(paper_ids)
        self._submit_workers = max(1, submit_workers)
        self._poll_seconds = max(1.0, poll_seconds)
        self._futures = {paper_id: Future() for paper_id in self._paper_ids}
        self._thread = Thread(target=self._run, name="mathpix-round-coordinator", daemon=True)
        self._stop = Event()
        self._status_callback = status_callback

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
                pending_submissions[executor.submit(submit_mathpix_pdf, paper_id)] = paper_id

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
                                result = download_mathpix_pdf(paper_id, pdf_id)
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
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, float]]:
    timings: dict[str, float] = {}
    mathpix_enabled = _mathpix_credentials_available()
    max_workers = 1 if prefetched_mathpix_future is not None else (PER_PAPER_SOURCE_WORKERS if mathpix_enabled else 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        docling_future = executor.submit(_timed_call, "docling", _build_docling_sources, paper_id)
        local_mathpix_future: Future[tuple[str, float, Any]] | None = None
        if mathpix_enabled and prefetched_mathpix_future is None:
            local_mathpix_future = executor.submit(
                _timed_call,
                "mathpix",
                _build_mathpix_sources,
                paper_id,
            )

        _, docling_seconds, docling_sources = docling_future.result()
        timings["docling_seconds"] = docling_seconds
        mathpix_sources = None
        if prefetched_mathpix_future is not None:
            mathpix_result = prefetched_mathpix_future.result()
            mathpix_sources = _build_mathpix_sources_from_result(paper_id, mathpix_result)
            mathpix_seconds = float(mathpix_result.get("elapsed_seconds", 0.0))
            timings["mathpix_seconds"] = mathpix_seconds
        elif local_mathpix_future is not None:
            _, mathpix_seconds, mathpix_sources = local_mathpix_future.result()
            timings["mathpix_seconds"] = mathpix_seconds
        else:
            timings["mathpix_seconds"] = 0.0

    return docling_sources, mathpix_sources, timings


def _layout_blocks_by_page(layout: dict[str, Any] | None) -> dict[int, list[dict[str, Any]]]:
    by_page: dict[int, list[dict[str, Any]]] = {}
    if not layout:
        return by_page
    for block in layout.get("blocks", []):
        page = int(block.get("page", 0) or 0)
        if page <= 0:
            continue
        by_page.setdefault(page, []).append(block)
    for blocks in by_page.values():
        blocks.sort(key=lambda block: (int(block.get("order", 0) or 0), str(block.get("id", ""))))
    return by_page


def _page_one_layout_score(blocks: list[dict[str, Any]]) -> int:
    if not blocks:
        return -10
    texts = [str(block.get("text", "")).strip() for block in blocks if str(block.get("text", "")).strip()]
    marker_score = 0
    if any(ABSTRACT_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 8
    if any(INTRO_PAGE_MARKER_RE.match(text) for text in texts):
        marker_score += 4
    marker_score -= sum(3 for text in texts if LAYOUT_METADATA_RE.search(text))
    return marker_score


def _compose_layout_sources(
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
) -> dict[str, Any]:
    docling_layout = (docling_sources or {}).get("layout") or {}
    mathpix_layout = (mathpix_sources or {}).get("layout") or {}
    if not docling_layout and not mathpix_layout:
        return {"engine": "none", "blocks": []}
    if not docling_layout:
        return dict(mathpix_layout)
    if not mathpix_layout:
        return dict(docling_layout)

    docling_pages = _layout_blocks_by_page(docling_layout)
    mathpix_pages = _layout_blocks_by_page(mathpix_layout)
    blocks: list[dict[str, Any]] = []
    page_sources: dict[str, str] = {}
    for page in sorted(set(docling_pages) | set(mathpix_pages)):
        docling_blocks = docling_pages.get(page, [])
        mathpix_blocks = mathpix_pages.get(page, [])
        chosen_blocks = docling_blocks
        chosen_engine = str(docling_layout.get("engine", "docling"))
        if page == 1 and mathpix_blocks:
            if _page_one_layout_score(mathpix_blocks) > _page_one_layout_score(docling_blocks):
                chosen_blocks = mathpix_blocks
                chosen_engine = str(mathpix_layout.get("engine", "mathpix"))
        elif not chosen_blocks and mathpix_blocks:
            chosen_blocks = mathpix_blocks
            chosen_engine = str(mathpix_layout.get("engine", "mathpix"))
        blocks.extend(chosen_blocks)
        page_sources[str(page)] = chosen_engine

    return {
        "engine": "composed",
        "pdf_path": docling_layout.get("pdf_path") or mathpix_layout.get("pdf_path"),
        "page_count": docling_layout.get("page_count") or mathpix_layout.get("page_count"),
        "page_sizes_pt": docling_layout.get("page_sizes_pt") or mathpix_layout.get("page_sizes_pt"),
        "blocks": blocks,
        "page_sources": page_sources,
    }


def _compose_external_sources(
    paper_id: str,
    *,
    docling_sources: dict[str, Any] | None,
    mathpix_sources: dict[str, Any] | None,
) -> dict[str, Any]:
    final_layout = _compose_layout_sources(docling_sources, mathpix_sources)
    final_math = {}
    if mathpix_sources and mathpix_sources.get("math", {}).get("entries"):
        final_math = mathpix_sources["math"]
    elif docling_sources:
        final_math = docling_sources["math"]
    else:
        final_math = {"engine": "none", "entries": []}
    layout_path = external_layout_path(paper_id)
    math_path = external_math_path(paper_id)
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


def _write_canonical_outputs(paper_id: str, document: dict[str, Any]) -> dict[str, Any]:
    return write_canonical_outputs(paper_id, document, include_review=True)


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return None


def _document_abstract_text(document: dict[str, Any]) -> str:
    abstract_id = str(document.get("front_matter", {}).get("abstract_block_id") or "")
    if not abstract_id:
        return ""
    for block in document.get("blocks", []):
        if str(block.get("id", "")) == abstract_id:
            return completeness_block_text(block)
    return ""


def _document_abstract_block(document: dict[str, Any]) -> dict[str, Any] | None:
    abstract_id = str(document.get("front_matter", {}).get("abstract_block_id") or "")
    if not abstract_id:
        return None
    for block in document.get("blocks", []):
        if str(block.get("id", "")) == abstract_id:
            return block
    return None


def _document_has_generated_abstract(document: dict[str, Any] | None) -> bool:
    if not isinstance(document, dict):
        return False
    abstract_block = _document_abstract_block(document)
    if not abstract_block:
        return False
    review = abstract_block.get("review", {})
    notes = str(review.get("notes", "")) if isinstance(review, dict) else ""
    text = completeness_block_text(abstract_block)
    return notes.startswith(GENERATED_ABSTRACT_NOTE_PREFIX) or text.startswith("[Generated abstract from ")


def _paper_has_generated_abstract_file(paper_id: str) -> bool:
    return (canonical_sources_dir(paper_id) / "generated-abstract.txt").exists()


def _copy_existing_abstract_block(existing_document: dict[str, Any] | None, new_document: dict[str, Any]) -> bool:
    existing_block = _document_abstract_block(existing_document or {})
    if not existing_block:
        return False

    target_id = str(new_document.get("front_matter", {}).get("abstract_block_id") or "")
    if not target_id:
        return False

    blocks = list(new_document.get("blocks", []))
    for block in blocks:
        if str(block.get("id", "")) != target_id:
            continue
        block["type"] = str(existing_block.get("type", block.get("type", "paragraph")))
        block["content"] = dict(existing_block.get("content", {}))
        block["source_spans"] = list(existing_block.get("source_spans", []))
        block["alternates"] = list(existing_block.get("alternates", []))
        block["review"] = dict(existing_block.get("review", {}))
        new_document["blocks"] = blocks
        return True

    preserved_block = {
        **existing_block,
        "id": target_id,
    }
    blocks.append(preserved_block)
    new_document["blocks"] = blocks
    return True


def _preserve_existing_generated_abstract(existing_document: dict[str, Any] | None, new_document: dict[str, Any]) -> bool:
    if not _document_has_generated_abstract(existing_document):
        return False
    return _copy_existing_abstract_block(existing_document, new_document)


def _preserve_existing_generated_abstract_file(
    paper_id: str,
    existing_document: dict[str, Any] | None,
    new_document: dict[str, Any],
) -> bool:
    if not _paper_has_generated_abstract_file(paper_id):
        return False
    existing_text = _document_abstract_text(existing_document or {})
    if not existing_text or "missing" in abstract_quality_flags(existing_text):
        return False
    return _copy_existing_abstract_block(existing_document, new_document)


def _anomaly_flags(document: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    front_matter = document.get("front_matter", {})
    if not front_matter.get("authors"):
        flags.append("missing_authors")
    abstract_flags = set(abstract_quality_flags(_document_abstract_text(document)))
    if not front_matter.get("abstract_block_id") or "missing" in abstract_flags:
        flags.append("missing_abstract")
    elif abstract_flags:
        flags.append("bad_abstract")
    if len(document.get("sections", [])) <= 1:
        flags.append("weak_sections")
    if len(document.get("references", [])) == 0 and document_expects_references(document):
        flags.append("missing_references")
    if len(document.get("figures", [])) == 0 and document_expects_figures(document.get("blocks", [])):
        flags.append("missing_figures")
    return flags


def _document_quality_key(document: dict[str, Any], mode_index: int) -> tuple[int, int, int, int, int, int]:
    anomalies = _anomaly_flags(document)
    weighted = sum(ANOMALY_WEIGHTS.get(flag, 1) for flag in anomalies)
    abstract_rank = abstract_quality_rank(_document_abstract_text(document))
    return (
        weighted,
        abstract_rank,
        len(anomalies),
        -len(document.get("sections", [])),
        -len(document.get("references", [])),
        mode_index,
    )


def _desired_flags_from_composed_sources(composed_sources: dict[str, Any]) -> dict[str, bool]:
    return {
        "use_external_layout": int(composed_sources.get("layout_blocks", 0) or 0) > 0,
        "use_external_math": int(composed_sources.get("math_entries", 0) or 0) > 0,
    }


def _existing_composed_sources(paper_id: str) -> dict[str, Any]:
    layout = _load_json_if_exists(external_layout_path(paper_id)) or {"engine": "none", "blocks": []}
    math = _load_json_if_exists(external_math_path(paper_id)) or {"engine": "none", "entries": []}
    return {
        "layout_path": str(external_layout_path(paper_id)),
        "math_path": str(external_math_path(paper_id)),
        "layout_engine": layout.get("engine"),
        "layout_blocks": len(layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
    }


def _desired_flags_for_existing_paper(
    document: dict[str, Any] | None,
    composed_sources: dict[str, Any],
) -> dict[str, bool]:
    composed_flags = _desired_flags_from_composed_sources(composed_sources)
    build_flags = ((document or {}).get("build", {}) or {}).get("flags", {})
    return {
        "use_external_layout": bool(build_flags.get("use_external_layout")) or composed_flags["use_external_layout"],
        "use_external_math": bool(build_flags.get("use_external_math")) or composed_flags["use_external_math"],
    }


def _build_paper(paper_id: str) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for mode_index, config in enumerate(
        (
        {"use_external_layout": True, "use_external_math": True, "text_engine": "native", "label": "hybrid"},
        {"use_external_layout": True, "use_external_math": False, "text_engine": "native", "label": "layout_only"},
        {"use_external_layout": False, "use_external_math": False, "text_engine": "native", "label": "native"},
        )
    ):
        try:
            document = reconcile_paper(
                paper_id,
                text_engine=str(config["text_engine"]),
                use_external_layout=bool(config["use_external_layout"]),
                use_external_math=bool(config["use_external_math"]),
            )
            validate_canonical(document)
            anomalies = _anomaly_flags(document)
            quality_key = _document_quality_key(document, mode_index)
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


def _run_paper_job(
    paper_id: str,
    *,
    force_rebuild: bool,
    prefetched_mathpix_future: Future[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    paper_status: dict[str, Any] = {}
    timings: dict[str, float] = {}
    overall_started = time.perf_counter()
    try:
        existing_document = _load_json_if_exists(canonical_path(paper_id))
        existing_composed = _existing_composed_sources(paper_id)
        desired_flags = _desired_flags_for_existing_paper(existing_document, existing_composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness(
            canonical_path(paper_id),
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        if not force_rebuild and not prebuild_staleness.get("stale") and existing_document is not None:
            refresh_started = time.perf_counter()
            outputs = _write_canonical_outputs(paper_id, existing_document)
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
        )
        timings.update(extraction_timings)

        compose_started = time.perf_counter()
        composed = _compose_external_sources(
            paper_id,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
        )
        timings["compose_sources_seconds"] = round(time.perf_counter() - compose_started, 3)

        desired_flags = _desired_flags_for_existing_paper(existing_document, composed)
        staleness_started = time.perf_counter()
        prebuild_staleness = detect_canonical_staleness(
            canonical_path(paper_id),
            desired_flags=desired_flags,
        )
        timings["staleness_seconds"] = round(time.perf_counter() - staleness_started, 3)

        build_started = time.perf_counter()
        build_result = _build_paper(paper_id)
        timings["build_seconds"] = round(time.perf_counter() - build_started, 3)
        document = build_result["document"]
        preserved_generated_abstract = _preserve_existing_generated_abstract(existing_document, document)
        preserved_generated_abstract_file = _preserve_existing_generated_abstract_file(paper_id, existing_document, document)
        outputs = _write_canonical_outputs(paper_id, document)
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


def _summarize_round(round_status: dict[str, Any]) -> dict[str, Any]:
    paper_results = round_status.get("papers", {})
    success_results = [item for item in paper_results.values() if item.get("status") == "completed"]
    failed_results = [item for item in paper_results.values() if item.get("status") == "failed"]
    running_results = [item for item in paper_results.values() if item.get("status") == "running"]
    queued_results = [item for item in paper_results.values() if item.get("status") == "queued"]
    anomalies: dict[str, int] = {}
    stale_reasons: dict[str, int] = {}
    stale_before_build_count = 0
    fresh_skip_count = 0
    for item in success_results:
        if item.get("skipped_fresh"):
            fresh_skip_count += 1
        for flag in item.get("anomalies", []):
            anomalies[flag] = anomalies.get(flag, 0) + 1
    for item in paper_results.values():
        staleness = item.get("prebuild_staleness", {})
        if staleness.get("stale"):
            stale_before_build_count += 1
            for reason in staleness.get("reasons", []):
                stale_reasons[str(reason)] = stale_reasons.get(str(reason), 0) + 1
    return {
        "success_count": len(success_results),
        "failure_count": len(failed_results),
        "running_count": len(running_results),
        "queued_count": len(queued_results),
        "anomalies": anomalies,
        "stale_before_build_count": stale_before_build_count,
        "stale_reasons": stale_reasons,
        "fresh_skip_count": fresh_skip_count,
    }


def _render_final_report(status: dict[str, Any]) -> str:
    round_names = sorted(status.get("rounds", {}).keys())
    lines = [
        "# Canonical Corpus Report",
        "",
        f"- Started: {status.get('started_at', '')}",
        f"- Updated: {status.get('updated_at', '')}",
        f"- Papers targeted: {len(status.get('papers', []))}",
        "",
    ]
    for round_name in round_names:
        round_status = status["rounds"][round_name]
        summary = _summarize_round(round_status)
        lines.extend(
            [
                f"## {round_name.title()}",
                "",
                f"- Started: {round_status.get('started_at', '')}",
                f"- Completed: {round_status.get('completed_at', '')}",
                f"- Successes: {summary['success_count']}",
                f"- Queued: {summary['queued_count']}",
                f"- Running: {summary['running_count']}",
                f"- Failures: {summary['failure_count']}",
                f"- Stale before rebuild: {summary['stale_before_build_count']}",
                f"- Fresh canonical skips: {summary['fresh_skip_count']}",
            ]
        )
        if summary["anomalies"]:
            lines.append("- Common anomalies:")
            for key, value in sorted(summary["anomalies"].items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - `{key}`: {value}")
        if summary["stale_reasons"]:
            lines.append("- Common stale reasons:")
            for key, value in sorted(summary["stale_reasons"].items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - `{key}`: {value}")
        lines.append("")

    lines.append("## Paper Status")
    lines.append("")
    if round_names:
        header = ["Paper", *[round_name.replace("_", " ").title() for round_name in round_names]]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    else:
        lines.append("| Paper | Status |")
        lines.append("| --- | --- |")
    for paper_id in status.get("papers", []):
        row = [paper_id]
        for round_name in round_names:
            paper_status = status.get("rounds", {}).get(round_name, {}).get("papers", {}).get(paper_id, {})
            if paper_status.get("status") == "completed":
                metrics = paper_status.get("metrics", {})
                cell = f"completed ({metrics.get('sections', 0)} s / {metrics.get('references', 0)} r / {metrics.get('figures', 0)} f)"
                anomalies = paper_status.get("anomalies", [])
                if anomalies:
                    cell += f" {';'.join(anomalies[:3])}"
                if paper_status.get("prebuild_staleness", {}).get("stale"):
                    cell += " stale-before-build"
                if paper_status.get("skipped_fresh"):
                    cell += " fresh-skip"
            elif paper_status.get("status") == "running":
                cell = f"running (started {paper_status.get('started_at', '')})"
            elif paper_status.get("status") == "queued":
                mathpix_phase = str(((paper_status.get("mathpix") or {}).get("phase") or "")).strip()
                if mathpix_phase:
                    cell = f"queued (mathpix {mathpix_phase})"
                else:
                    cell = "queued"
            elif paper_status:
                cell = "failed"
            else:
                cell = "not-run"
            row.append(cell)
        if len(row) == 1:
            row.append("not-run")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    for note in status.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _process_round(
    status: dict[str, Any],
    round_index: int,
    *,
    max_workers: int,
    force_rebuild: bool,
) -> None:
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
        _save_status(status)

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
            active_jobs[executor.submit(_run_paper_job, paper_id, **submit_kwargs)] = paper_id
            _save_status(status)

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
                    _save_status(status)
                schedule_ready_papers(executor)
    finally:
        if mathpix_coordinator is not None:
            mathpix_coordinator.close()

    round_status["completed_at"] = _now_iso()
    _save_status(status)


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
) -> dict[str, Any]:
    if start_round > end_round:
        raise SystemExit("--start-round cannot be greater than --end-round")
    if max_workers < 1:
        raise SystemExit("--max-workers must be at least 1")

    _configure_runtime_environment()
    if _mathpix_credentials_available():
        _assert_mathpix_dns_available()
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    status = _load_status()
    status["papers"] = _paper_ids()
    status["notes"] = [
        "Round processing uses Docling for layout, Mathpix for math when credentials are available, and lexicon refresh at round boundaries.",
        f"Corpus temp paths are redirected into {TMP_DIR}.",
        f"Configured worker concurrency: {max_workers}.",
        "Fresh canonicals are skipped when source inputs, build flags, and pipeline fingerprints still match.",
        "Mathpix defaults to whole-PDF round coordination when multiple papers are pending and credentials are available.",
    ]
    if PROJECT_MODE:
        status["notes"].append(f"Project reports are written into {BATCH_DIR}.")
    if force_rebuild:
        status["notes"].append("Fresh canonicals are still rebuilt because --force-rebuild was enabled.")
    _save_status(status)

    _rebuild_lexicon()
    for round_index in range(start_round, end_round + 1):
        _process_round(
            status,
            round_index,
            max_workers=max_workers,
            force_rebuild=bool(force_rebuild),
        )
        _rebuild_lexicon()
        if stop_after_round == round_index:
            break

    report = _render_final_report(status)
    REPORT_PATH.write_text(report, encoding="utf-8")
    return {
        "status_path": str(STATUS_PATH),
        "report_path": str(REPORT_PATH),
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
