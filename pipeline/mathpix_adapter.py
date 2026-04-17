from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any
from urllib import request

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, paper_pdf_path
from pipeline.sources import mathpix as _mathpix


DOCS_DIR = CORPUS_DIR
MATHPIX_PDF_ENDPOINT = _mathpix.MATHPIX_PDF_ENDPOINT
_MATHPIX_REQUEST_SEMAPHORE = _mathpix._MATHPIX_REQUEST_SEMAPHORE
_MATHPIX_REQUEST_LIMIT = _mathpix._MATHPIX_REQUEST_LIMIT
_MATHPIX_REQUEST_LOCK = _mathpix._MATHPIX_REQUEST_LOCK
_RETRYABLE_SOCKET_ERRNOS = _mathpix._RETRYABLE_SOCKET_ERRNOS
_bbox_from_cnt = _mathpix._bbox_from_cnt
_clean_latex = _mathpix._clean_latex
_load_fitz = _mathpix._load_fitz
_math_entry_from_line = _mathpix._math_entry_from_line
_mathpix_headers = _mathpix._mathpix_headers
_mathpix_http_error_message = _mathpix._mathpix_http_error_message
_mathpix_pdf_page_ranges = _mathpix._mathpix_pdf_page_ranges
_mathpix_pdf_poll_seconds = _mathpix._mathpix_pdf_poll_seconds
_mathpix_pdf_wait_timeout_seconds = _mathpix._mathpix_pdf_wait_timeout_seconds
_mathpix_request_semaphore = _mathpix._mathpix_request_semaphore
_mathpix_retry_attempts = _mathpix._mathpix_retry_attempts
_mathpix_retry_backoff_seconds = _mathpix._mathpix_retry_backoff_seconds
_multipart_form_payload = _mathpix._multipart_form_payload
_output_dir = _mathpix._output_dir
_pdf_page_sizes_pt = _mathpix._pdf_page_sizes_pt
_render_page_png_bytes = _mathpix._render_page_png_bytes
_retryable_socket_error = _mathpix._retryable_socket_error
_role_for_line = _mathpix._role_for_line
_sleep = _mathpix._sleep
fetch_mathpix_pdf_status = _mathpix.fetch_mathpix_pdf_status
mathpix_pages_to_external_sources = _mathpix.mathpix_pages_to_external_sources
write_external_sources = _mathpix.write_external_sources

_SOURCE_MATHPIX_REQUEST_BYTES = _mathpix._mathpix_request_bytes
_SOURCE_MATHPIX_REQUEST_JSON = _mathpix._mathpix_request_json
_SOURCE_CALL_MATHPIX_ON_PAGE_IMAGE = _mathpix.call_mathpix_on_page_image
_SOURCE_MATHPIX_PDF_SUBMIT = _mathpix._mathpix_pdf_submit
_SOURCE_MATHPIX_PDF_STATUS = _mathpix._mathpix_pdf_status
_SOURCE_MATHPIX_PDF_WAIT_FOR_COMPLETION = _mathpix._mathpix_pdf_wait_for_completion
_SOURCE_MATHPIX_PDF_DOWNLOAD_LINES = _mathpix._mathpix_pdf_download_lines
_SOURCE_MATHPIX_PDF_LINES_TO_PAGE_PAYLOADS = _mathpix._mathpix_pdf_lines_to_page_payloads


def _paper_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return paper_pdf_path(paper_id, layout=layout)


def _sync_mathpix_compat() -> None:
    _mathpix.request = request
    _mathpix.subprocess = subprocess
    _mathpix._sleep = _sleep
    _mathpix._paper_pdf_path = _paper_pdf_path
    _mathpix._pdf_page_sizes_pt = _pdf_page_sizes_pt
    _mathpix._mathpix_request_semaphore = _mathpix_request_semaphore
    _mathpix._mathpix_retry_attempts = _mathpix_retry_attempts
    _mathpix._mathpix_retry_backoff_seconds = _mathpix_retry_backoff_seconds
    _mathpix._retryable_socket_error = _retryable_socket_error
    _mathpix._mathpix_headers = _mathpix_headers
    _mathpix._mathpix_http_error_message = _mathpix_http_error_message
    _mathpix._multipart_form_payload = _multipart_form_payload
    _mathpix._mathpix_request_bytes = _mathpix_request_bytes
    _mathpix._mathpix_request_json = _mathpix_request_json
    _mathpix._mathpix_pdf_page_ranges = _mathpix_pdf_page_ranges
    _mathpix._mathpix_pdf_status = _mathpix_pdf_status
    _mathpix._mathpix_pdf_poll_seconds = _mathpix_pdf_poll_seconds
    _mathpix._mathpix_pdf_wait_timeout_seconds = _mathpix_pdf_wait_timeout_seconds


def _mathpix_request_bytes(req: request.Request, *, timeout_seconds: int = 180) -> bytes:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_REQUEST_BYTES(req, timeout_seconds=timeout_seconds)


def _mathpix_request_json(req: request.Request, *, timeout_seconds: int = 180) -> dict[str, Any]:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_REQUEST_JSON(req, timeout_seconds=timeout_seconds)


def call_mathpix_on_page_image(
    image_bytes: bytes,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = "https://api.mathpix.com/v3/text",
) -> dict[str, Any]:
    _sync_mathpix_compat()
    return _SOURCE_CALL_MATHPIX_ON_PAGE_IMAGE(
        image_bytes,
        app_id=app_id,
        app_key=app_key,
        endpoint=endpoint,
    )


def _mathpix_pdf_submit(
    pdf_path: Path,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    page_ranges: str | None = None,
) -> str:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_PDF_SUBMIT(
        pdf_path,
        app_id=app_id,
        app_key=app_key,
        endpoint=endpoint,
        page_ranges=page_ranges,
    )


def _mathpix_pdf_status(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_PDF_STATUS(
        pdf_id,
        app_id=app_id,
        app_key=app_key,
        endpoint=endpoint,
    )


def _mathpix_pdf_wait_for_completion(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_PDF_WAIT_FOR_COMPLETION(
        pdf_id,
        app_id=app_id,
        app_key=app_key,
        endpoint=endpoint,
    )


def _mathpix_pdf_download_lines(
    pdf_id: str,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
) -> dict[str, Any]:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_PDF_DOWNLOAD_LINES(
        pdf_id,
        app_id=app_id,
        app_key=app_key,
        endpoint=endpoint,
    )


def _mathpix_pdf_lines_to_page_payloads(
    lines_payload: dict[str, Any],
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
) -> list[dict[str, Any]]:
    _sync_mathpix_compat()
    return _SOURCE_MATHPIX_PDF_LINES_TO_PAGE_PAYLOADS(lines_payload, paper_id, layout=layout)


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
