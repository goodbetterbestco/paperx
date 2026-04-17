from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any
from urllib import error, parse, request

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, paper_pdf_path
from pipeline.sources.mathpix import (
    MATHPIX_PDF_ENDPOINT,
    _MATHPIX_REQUEST_LIMIT,
    _MATHPIX_REQUEST_LOCK,
    _MATHPIX_REQUEST_SEMAPHORE,
    _RETRYABLE_SOCKET_ERRNOS,
    _bbox_from_cnt,
    _clean_latex,
    _load_fitz,
    _math_entry_from_line,
    _mathpix_headers,
    _mathpix_http_error_message,
    _mathpix_pdf_page_ranges,
    _mathpix_pdf_poll_seconds,
    _mathpix_pdf_wait_timeout_seconds,
    _mathpix_request_semaphore,
    _mathpix_retry_attempts,
    _mathpix_retry_backoff_seconds,
    _multipart_form_payload,
    _output_dir,
    _pdf_page_sizes_pt,
    _render_page_png_bytes,
    _retryable_socket_error,
    _role_for_line,
    _sleep,
    fetch_mathpix_pdf_status,
    mathpix_pages_to_external_sources,
    write_external_sources,
)

DOCS_DIR = CORPUS_DIR


def _paper_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return paper_pdf_path(paper_id, layout=layout)


def _mathpix_request_bytes(req: request.Request, *, timeout_seconds: int = 180) -> bytes:
    max_attempts = _mathpix_retry_attempts()
    last_error: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with request.urlopen(req, timeout=timeout_seconds) as response:
                return response.read()
        except error.HTTPError as exc:
            raise RuntimeError(_mathpix_http_error_message(exc)) from exc
        except Exception as exc:
            retryable = _retryable_socket_error(exc)
            if not retryable or attempt >= max_attempts:
                if retryable and max_attempts > 1:
                    raise RuntimeError(f"Mathpix request failed after {max_attempts} attempts: {exc}") from exc
                raise
            last_error = exc
            _sleep(_mathpix_retry_backoff_seconds(attempt))
    if last_error is not None:  # pragma: no cover - loop always returns or raises
        raise RuntimeError(f"Mathpix request failed after {max_attempts} attempts: {last_error}") from last_error
    raise RuntimeError("Mathpix request did not produce a response.")  # pragma: no cover


def _mathpix_request_json(req: request.Request, *, timeout_seconds: int = 180) -> dict[str, Any]:
    payload = _mathpix_request_bytes(req, timeout_seconds=timeout_seconds)
    decoded = json.loads(payload.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise RuntimeError("Mathpix returned a non-object JSON payload.")
    return decoded


def call_mathpix_on_page_image(
    image_bytes: bytes,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = "https://api.mathpix.com/v3/text",
) -> dict[str, Any]:
    options = {
        "formats": ["text", "data"],
        "data_options": {"include_latex": True},
        "include_line_data": True,
        "include_equation_tags": True,
    }
    options_json = json.dumps(options, separators=(",", ":"))
    payload, boundary = _multipart_form_payload(
        file_bytes=image_bytes,
        filename="page.png",
        file_content_type="image/png",
        options_json=options_json,
    )
    req = request.Request(
        endpoint,
        data=payload,
        headers=_mathpix_headers(app_id, app_key, content_type=f"multipart/form-data; boundary={boundary}"),
        method="POST",
    )
    return _mathpix_request_json(req)


def _mathpix_pdf_submit(
    pdf_path: Path,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    page_ranges: str | None = None,
) -> str:
    options: dict[str, Any] = {
        "include_equation_tags": True,
        "include_page_info": True,
    }
    if page_ranges:
        options["page_ranges"] = page_ranges
    options_json = json.dumps(options, separators=(",", ":"))
    command = [
        "curl",
        "-sS",
        "-X",
        "POST",
        endpoint.rstrip("/"),
        "-H",
        f"app_id: {app_id}",
        "-H",
        f"app_key: {app_key}",
        "-F",
        f"file=@{pdf_path}",
        "-F",
        f"options_json={options_json}",
    ]
    max_attempts = _mathpix_retry_attempts()
    last_error: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with _mathpix_request_semaphore():
                completed = subprocess.run(command, check=True, capture_output=True, text=True)
            response = json.loads(completed.stdout)
            if not isinstance(response, dict):
                raise RuntimeError("Mathpix PDF submission returned a non-object JSON payload.")
            pdf_id = str(response.get("pdf_id", "")).strip()
            if not pdf_id:
                raise RuntimeError(f"Mathpix PDF submission did not return a pdf_id: {response}")
            return pdf_id
        except subprocess.CalledProcessError as exc:
            message = (exc.stderr or exc.stdout or str(exc)).strip()
            if attempt >= max_attempts:
                raise RuntimeError(f"Mathpix PDF submission failed after {max_attempts} attempts: {message}") from exc
            last_error = exc
            _sleep(_mathpix_retry_backoff_seconds(attempt))
        except FileNotFoundError as exc:
            raise RuntimeError("curl is required for Mathpix PDF submission.") from exc
    if last_error is not None:  # pragma: no cover - loop always returns or raises
        raise RuntimeError(f"Mathpix PDF submission failed after {max_attempts} attempts: {last_error}") from last_error
    raise RuntimeError("Mathpix PDF submission did not produce a response.")  # pragma: no cover


def _mathpix_pdf_status(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    req = request.Request(
        f"{endpoint.rstrip('/')}/{parse.quote(pdf_id, safe='')}",
        headers=_mathpix_headers(app_id, app_key),
        method="GET",
    )
    with _mathpix_request_semaphore():
        return _mathpix_request_json(req)


def _mathpix_pdf_wait_for_completion(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    timeout_seconds = _mathpix_pdf_wait_timeout_seconds()
    deadline = time.monotonic() + timeout_seconds
    last_status = "received"
    while True:
        response = _mathpix_pdf_status(pdf_id, app_id=app_id, app_key=app_key, endpoint=endpoint)
        last_status = str(response.get("status", "")).strip().lower() or "unknown"
        if last_status == "completed":
            return response
        if last_status == "error" or response.get("error"):
            raise RuntimeError(f"Mathpix PDF {pdf_id} failed: {response}")
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Mathpix PDF {pdf_id} did not complete within {timeout_seconds} seconds "
                f"(last status: {last_status})."
            )
        _sleep(_mathpix_pdf_poll_seconds())


def _mathpix_pdf_download_lines(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    req = request.Request(
        f"{endpoint.rstrip('/')}/{parse.quote(pdf_id, safe='')}.lines.json",
        headers=_mathpix_headers(app_id, app_key),
        method="GET",
    )
    with _mathpix_request_semaphore():
        response = _mathpix_request_json(req)
    pages = response.get("pages")
    if not isinstance(pages, list):
        raise RuntimeError(f"Mathpix PDF lines download did not include pages: {response}")
    return response


def _mathpix_pdf_lines_to_page_payloads(
    lines_payload: dict[str, Any],
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
) -> list[dict[str, Any]]:
    pdf_path = _paper_pdf_path(paper_id, layout=layout)
    page_sizes_pt = _pdf_page_sizes_pt(pdf_path)
    payloads: list[dict[str, Any]] = []
    for page_data in list(lines_payload.get("pages") or []):
        page_number = int(page_data.get("page", 0) or 0)
        if page_number < 1 or page_number > len(page_sizes_pt):
            raise RuntimeError(f"Mathpix lines payload referenced out-of-range page {page_number} for {paper_id}.")
        page_width_pt, page_height_pt = page_sizes_pt[page_number - 1]
        payloads.append(
            {
                "page": page_number,
                "page_width_pt": page_width_pt,
                "page_height_pt": page_height_pt,
                "image_width": int(page_data.get("page_width", 0) or 0),
                "image_height": int(page_data.get("page_height", 0) or 0),
                "response": {"line_data": list(page_data.get("lines") or [])},
            }
        )
    payloads.sort(key=lambda payload: int(payload["page"]))
    return payloads


def submit_mathpix_pdf(
    paper_id: str,
    *,
    pages: list[int] | None = None,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    app_id: str | None = None,
    app_key: str | None = None,
    layout: ProjectLayout | None = None,
) -> str:
    resolved_app_id = app_id or os.environ.get("MATHPIX_APP_ID")
    resolved_app_key = app_key or os.environ.get("MATHPIX_APP_KEY")
    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError("Mathpix credentials not found. Set MATHPIX_APP_ID and MATHPIX_APP_KEY.")
    if endpoint.rstrip("/") != MATHPIX_PDF_ENDPOINT:
        raise RuntimeError(f"submit_mathpix_pdf expects the Mathpix PDF endpoint, not {endpoint}.")

    pdf_path = _paper_pdf_path(paper_id, layout=layout)
    page_ranges = _mathpix_pdf_page_ranges(pages)
    return _mathpix_pdf_submit(
        pdf_path,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        endpoint=endpoint,
        page_ranges=page_ranges,
    )


def download_mathpix_pdf(
    paper_id: str,
    pdf_id: str,
    *,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    app_id: str | None = None,
    app_key: str | None = None,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    resolved_app_id = app_id or os.environ.get("MATHPIX_APP_ID")
    resolved_app_key = app_key or os.environ.get("MATHPIX_APP_KEY")
    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError("Mathpix credentials not found. Set MATHPIX_APP_ID and MATHPIX_APP_KEY.")
    if endpoint.rstrip("/") != MATHPIX_PDF_ENDPOINT:
        raise RuntimeError(f"download_mathpix_pdf expects the Mathpix PDF endpoint, not {endpoint}.")

    lines_payload = _mathpix_pdf_download_lines(pdf_id, app_id=resolved_app_id, app_key=resolved_app_key, endpoint=endpoint)
    return {
        "pdf_id": pdf_id,
        "lines": lines_payload,
        "pages": _mathpix_pdf_lines_to_page_payloads(lines_payload, paper_id, layout=layout),
    }


def run_mathpix(
    paper_id: str,
    *,
    pages: list[int] | None = None,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    app_id: str | None = None,
    app_key: str | None = None,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    resolved_app_id = app_id or os.environ.get("MATHPIX_APP_ID")
    resolved_app_key = app_key or os.environ.get("MATHPIX_APP_KEY")
    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError("Mathpix credentials not found. Set MATHPIX_APP_ID and MATHPIX_APP_KEY.")
    if endpoint.rstrip("/") != MATHPIX_PDF_ENDPOINT:
        raise RuntimeError(f"run_mathpix now expects the Mathpix PDF endpoint, not {endpoint}.")

    pdf_id = submit_mathpix_pdf(
        paper_id,
        pages=pages,
        endpoint=endpoint,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        layout=layout,
    )
    _mathpix_pdf_wait_for_completion(pdf_id, app_id=resolved_app_id, app_key=resolved_app_key, endpoint=endpoint)
    return download_mathpix_pdf(
        paper_id,
        pdf_id,
        endpoint=endpoint,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        layout=layout,
    )


__all__ = [
    "DOCS_DIR",
    "MATHPIX_PDF_ENDPOINT",
    "_MATHPIX_REQUEST_LIMIT",
    "_MATHPIX_REQUEST_LOCK",
    "_MATHPIX_REQUEST_SEMAPHORE",
    "_RETRYABLE_SOCKET_ERRNOS",
    "_bbox_from_cnt",
    "_clean_latex",
    "_load_fitz",
    "_math_entry_from_line",
    "_mathpix_headers",
    "_mathpix_http_error_message",
    "_mathpix_pdf_download_lines",
    "_mathpix_pdf_lines_to_page_payloads",
    "_mathpix_pdf_page_ranges",
    "_mathpix_pdf_poll_seconds",
    "_mathpix_pdf_status",
    "_mathpix_pdf_submit",
    "_mathpix_pdf_wait_for_completion",
    "_mathpix_pdf_wait_timeout_seconds",
    "_mathpix_request_bytes",
    "_mathpix_request_json",
    "_mathpix_request_semaphore",
    "_mathpix_retry_attempts",
    "_mathpix_retry_backoff_seconds",
    "_multipart_form_payload",
    "_output_dir",
    "_paper_pdf_path",
    "_pdf_page_sizes_pt",
    "_render_page_png_bytes",
    "_retryable_socket_error",
    "_role_for_line",
    "_sleep",
    "call_mathpix_on_page_image",
    "download_mathpix_pdf",
    "fetch_mathpix_pdf_status",
    "mathpix_pages_to_external_sources",
    "request",
    "run_mathpix",
    "submit_mathpix_pdf",
    "subprocess",
    "write_external_sources",
]
