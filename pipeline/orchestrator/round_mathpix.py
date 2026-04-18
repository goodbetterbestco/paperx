from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from threading import Event, Thread
import time
from typing import Any, Callable

from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_runtime import now_iso
from pipeline.sources.mathpix import (
    download_mathpix_pdf,
    fetch_mathpix_pdf_status,
    submit_mathpix_pdf,
)


class MathpixRoundCoordinator:
    def __init__(
        self,
        paper_ids: list[str],
        *,
        submit_workers: int,
        poll_seconds: float,
        status_callback: Callable[[str, dict[str, Any]], None] | None = None,
        layout: ProjectLayout | None = None,
        now_iso_impl: Callable[[], str] | None = None,
        submit_mathpix_pdf_impl: Callable[..., str] | None = None,
        fetch_mathpix_pdf_status_impl: Callable[[str], dict[str, Any]] | None = None,
        download_mathpix_pdf_impl: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self._paper_ids = list(paper_ids)
        self._submit_workers = max(1, submit_workers)
        self._poll_seconds = max(1.0, poll_seconds)
        self._futures = {paper_id: Future() for paper_id in self._paper_ids}
        self._thread = Thread(target=self._run, name="mathpix-round-coordinator", daemon=True)
        self._stop = Event()
        self._status_callback = status_callback
        self._layout = layout
        self._now_iso = now_iso_impl or now_iso
        self._submit_mathpix_pdf = submit_mathpix_pdf_impl or submit_mathpix_pdf
        self._fetch_mathpix_pdf_status = fetch_mathpix_pdf_status_impl or fetch_mathpix_pdf_status
        self._download_mathpix_pdf = download_mathpix_pdf_impl or download_mathpix_pdf

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
                            "submit_queued_at": self._now_iso(),
                        }
                    },
                )
                pending_submissions[executor.submit(self._submit_mathpix_pdf, paper_id, layout=self._layout)] = paper_id

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
                                    "submit_completed_at": self._now_iso(),
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
                                    "failed_at": self._now_iso(),
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
                            status = self._fetch_mathpix_pdf_status(pdf_id)
                            state = str(status.get("status", "")).strip().lower()
                            self._publish(
                                paper_id,
                                {
                                    "mathpix": {
                                        "phase": "polling",
                                        "last_polled_at": self._now_iso(),
                                        "pdf_id": pdf_id,
                                        "remote_status": state or "unknown",
                                    }
                                },
                            )
                            if state == "completed":
                                result = self._download_mathpix_pdf(paper_id, pdf_id, layout=self._layout)
                                result["elapsed_seconds"] = round(time.perf_counter() - submit_started[paper_id], 3)
                                self._publish(
                                    paper_id,
                                    {
                                        "mathpix": {
                                            "phase": "completed",
                                            "completed_at": self._now_iso(),
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
                                        "failed_at": self._now_iso(),
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
                                    "stopped_at": self._now_iso(),
                                }
                            },
                        )
                        paper_future.set_exception(RuntimeError(f"Mathpix round coordinator stopped before {paper_id} completed."))


__all__ = ["MathpixRoundCoordinator"]
