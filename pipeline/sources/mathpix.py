from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
from threading import BoundedSemaphore, Lock
import time
from typing import Any
from urllib import error, parse, request
import uuid

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, canonical_sources_dir, display_path, paper_pdf_path
from pipeline.math.review_policy import review_for_math_entry
from pipeline.types import default_formula_conversion, default_review

DOCS_DIR = CORPUS_DIR
MATHPIX_PDF_ENDPOINT = "https://api.mathpix.com/v3/pdf"
_MATHPIX_REQUEST_SEMAPHORE: BoundedSemaphore | None = None
_MATHPIX_REQUEST_LIMIT: int | None = None
_MATHPIX_REQUEST_LOCK = Lock()
_RETRYABLE_SOCKET_ERRNOS = {32, 54, 60, 104, 110}


def _load_fitz() -> Any:
    try:
        import fitz  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyMuPDF is required for Mathpix PDF page sizing.") from exc
    return fitz


def _paper_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return paper_pdf_path(paper_id, layout=layout)


def _output_dir(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return canonical_sources_dir(paper_id, layout=layout)


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


def _mathpix_request_semaphore() -> BoundedSemaphore:
    global _MATHPIX_REQUEST_SEMAPHORE, _MATHPIX_REQUEST_LIMIT
    # Cap concurrent Mathpix network work across paper workers.
    limit = _int_env("STEPVIEW_MATHPIX_REQUEST_LIMIT", 20)
    with _MATHPIX_REQUEST_LOCK:
        if _MATHPIX_REQUEST_SEMAPHORE is None or _MATHPIX_REQUEST_LIMIT != limit:
            _MATHPIX_REQUEST_SEMAPHORE = BoundedSemaphore(limit)
            _MATHPIX_REQUEST_LIMIT = limit
    return _MATHPIX_REQUEST_SEMAPHORE


def _mathpix_retry_attempts() -> int:
    return _int_env("STEPVIEW_MATHPIX_RETRY_ATTEMPTS", 4)


def _mathpix_retry_backoff_seconds(retry_index: int) -> float:
    base_seconds = _float_env("STEPVIEW_MATHPIX_RETRY_BASE_SECONDS", 1.0)
    max_seconds = _float_env("STEPVIEW_MATHPIX_RETRY_MAX_SECONDS", 8.0)
    return min(max_seconds, base_seconds * (2 ** max(0, retry_index - 1)))


def _mathpix_pdf_poll_seconds() -> float:
    return _float_env("STEPVIEW_MATHPIX_PDF_POLL_SECONDS", 2.0)


def _mathpix_pdf_wait_timeout_seconds() -> int:
    return _int_env("STEPVIEW_MATHPIX_PDF_WAIT_TIMEOUT_SECONDS", 1800)


def _retryable_socket_error(exc: BaseException) -> bool:
    if isinstance(exc, error.URLError) and isinstance(exc.reason, BaseException):
        return _retryable_socket_error(exc.reason)
    if isinstance(exc, (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, socket.timeout, TimeoutError)):
        return True
    if isinstance(exc, OSError):
        return exc.errno in _RETRYABLE_SOCKET_ERRNOS
    if isinstance(exc, http.client.RemoteDisconnected):
        return True
    return False


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _bbox_from_cnt(cnt: list[list[float]], *, page_width_pt: float, page_height_pt: float, image_width: int, image_height: int) -> dict[str, float]:
    xs = [float(point[0]) for point in cnt]
    ys = [float(point[1]) for point in cnt]
    if not xs or not ys:
        return {}
    x_scale = page_width_pt / max(image_width, 1)
    y_scale = page_height_pt / max(image_height, 1)
    x0 = min(xs) * x_scale
    y0 = min(ys) * y_scale
    x1 = max(xs) * x_scale
    y1 = max(ys) * y_scale
    return {
        "x0": round(x0, 2),
        "y0": round(y0, 2),
        "x1": round(x1, 2),
        "y1": round(y1, 2),
        "width": round(x1 - x0, 2),
        "height": round(y1 - y0, 2),
    }


def _clean_latex(text: str) -> str:
    stripped = text.strip()
    for prefix, suffix in (("\\[", "\\]"), ("\\(", "\\)"), ("$$", "$$"), ("$", "$")):
        if stripped.startswith(prefix) and stripped.endswith(suffix) and len(stripped) > len(prefix) + len(suffix):
            return stripped[len(prefix) : -len(suffix)].strip()
    return stripped


def _role_for_line(line: dict[str, Any]) -> str | None:
    line_type = str(line.get("type", ""))
    subtype = str(line.get("subtype", ""))

    if line_type in {"page_info", "equation_number"}:
        return None
    if line_type in {"title", "authors", "abstract"}:
        return "front_matter"
    if line_type == "section_header":
        return "heading"
    if line_type == "figure_label":
        return "caption"
    if line_type == "footnote":
        return "footnote"
    if line_type in {"code", "pseudocode"} or subtype in {"algorithm", "pseudocode"}:
        return "code"
    return "paragraph"


def _layout_block_from_line(
    line: dict[str, Any],
    *,
    paper_id: str,
    page: int,
    order: int,
    page_width_pt: float,
    page_height_pt: float,
    image_width: int,
    image_height: int,
) -> dict[str, Any] | None:
    role = _role_for_line(line)
    if role is None:
        return None
    text = str(line.get("text", "")).strip()
    if not text:
        return None
    bbox = _bbox_from_cnt(
        list(line.get("cnt") or []),
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        image_width=image_width,
        image_height=image_height,
    )
    return {
        "id": f"mathpix-p{page:03d}-b{order:04d}",
        "page": page,
        "order": order,
        "role": role,
        "text": text,
        "bbox": bbox,
        "meta": {
            "mathpix_type": str(line.get("type", "")),
            "mathpix_subtype": str(line.get("subtype", "")),
            "confidence": line.get("confidence"),
            "confidence_rate": line.get("confidence_rate"),
            "parent_id": line.get("parent_id"),
            "children_ids": line.get("children_ids"),
        },
    }


def _math_entry_from_line(
    line: dict[str, Any],
    *,
    page: int,
    order: int,
    page_width_pt: float,
    page_height_pt: float,
    image_width: int,
    image_height: int,
) -> dict[str, Any] | None:
    line_type = str(line.get("type", ""))
    if line_type != "math":
        return None
    text = _clean_latex(str(line.get("text") or line.get("text_display") or ""))
    if not text:
        return None
    bbox = _bbox_from_cnt(
        list(line.get("cnt") or []),
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        image_width=image_width,
        image_height=image_height,
    )
    source_span = {"page": page, "bbox": bbox, "engine": "mathpix"}
    return {
        "id": f"mathpix-eq-p{page:03d}-{order:04d}",
        "kind": "display",
        "display_latex": text,
        "semantic_expr": None,
        "compiled_targets": {},
        "conversion": default_formula_conversion(),
        "source_spans": [source_span],
        "alternates": [],
        "review": review_for_math_entry(
            {
                "display_latex": text,
                "source_spans": [source_span],
                "review": default_review(risk="medium"),
            }
        ),
    }


def mathpix_pages_to_external_sources(
    page_payloads: list[dict[str, Any]],
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    pdf_path: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pdf_path = pdf_path or _paper_pdf_path(paper_id, layout=layout)
    page_count = len(page_payloads)
    page_sizes_pt = [
        {"page": payload["page"], "width": payload["page_width_pt"], "height": payload["page_height_pt"]}
        for payload in page_payloads
    ]
    blocks: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []

    for payload in page_payloads:
        page = int(payload["page"])
        page_width_pt = float(payload["page_width_pt"])
        page_height_pt = float(payload["page_height_pt"])
        image_width = int(payload["image_width"])
        image_height = int(payload["image_height"])
        response = dict(payload["response"])
        line_data = list(response.get("line_data") or [])
        for order, line in enumerate(line_data, start=1):
            block = _layout_block_from_line(
                line,
                paper_id=paper_id,
                page=page,
                order=order,
                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
                image_width=image_width,
                image_height=image_height,
            )
            if block is not None:
                blocks.append(block)
            math_entry = _math_entry_from_line(
                line,
                page=page,
                order=order,
                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
                image_width=image_width,
                image_height=image_height,
            )
            if math_entry is not None:
                entries.append(math_entry)

    layout_payload = {
        "engine": "mathpix",
        "pdf_path": display_path(pdf_path, layout=layout),
        "page_count": page_count,
        "page_sizes_pt": page_sizes_pt,
        "blocks": blocks,
    }
    math = {
        "engine": "mathpix",
        "entries": entries,
    }
    return layout_payload, math


def _render_page_png_bytes(pdf_path: Path, page_number: int, *, scale: float) -> tuple[bytes, int, int, float, float]:
    fitz = _load_fitz()
    with fitz.open(pdf_path) as document:
        page = document[page_number - 1]
        matrix = fitz.Matrix(scale, scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pixmap.tobytes("png")
        return png_bytes, int(pixmap.width), int(pixmap.height), float(page.rect.width), float(page.rect.height)


def _mathpix_headers(
    app_id: str,
    app_key: str,
    *,
    accept: str = "application/json",
    content_type: str | None = None,
) -> dict[str, str]:
    headers = {
        "app_id": app_id,
        "app_key": app_key,
        "Accept": accept,
        # Fresh connections reduce the chance of carrying a bad socket across requests.
        "Connection": "close",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _multipart_form_payload(
    *,
    file_bytes: bytes,
    filename: str,
    file_content_type: str,
    options_json: str,
) -> tuple[bytes, str]:
    boundary = f"----MathpixBoundary{uuid.uuid4().hex}"
    boundary_bytes = boundary.encode("ascii")
    chunks = [
        b"--" + boundary_bytes + b"\r\n",
        b'Content-Disposition: form-data; name="file"; filename="' + filename.encode("utf-8") + b'"\r\n',
        b"Content-Type: " + file_content_type.encode("ascii") + b"\r\n\r\n",
        file_bytes,
        b"\r\n",
        b"--" + boundary_bytes + b"\r\n",
        b'Content-Disposition: form-data; name="options_json"\r\n\r\n',
        options_json.encode("utf-8"),
        b"\r\n",
        b"--" + boundary_bytes + b"--\r\n",
    ]
    return b"".join(chunks), boundary


def _mathpix_http_error_message(exc: error.HTTPError) -> str:
    body_text = exc.read().decode("utf-8", errors="replace").strip()
    if body_text:
        try:
            payload = json.loads(body_text)
        except json.JSONDecodeError:
            return f"Mathpix HTTP {exc.code}: {body_text}"
        summary = str(payload.get("error") or payload.get("message") or body_text)
        error_info = payload.get("error_info")
        if isinstance(error_info, dict):
            detail = str(error_info.get("id") or error_info.get("message") or "").strip()
            if detail and detail not in summary:
                summary = f"{summary} ({detail})"
        return f"Mathpix HTTP {exc.code}: {summary}"
    return f"Mathpix HTTP {exc.code}: {exc.reason}"


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
            if not _retryable_socket_error(exc) or attempt >= max_attempts:
                if _retryable_socket_error(exc) and max_attempts > 1:
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


def _pdf_page_sizes_pt(pdf_path: Path) -> list[tuple[float, float]]:
    fitz = _load_fitz()
    with fitz.open(pdf_path) as document:
        return [(float(page.rect.width), float(page.rect.height)) for page in document]


def _mathpix_pdf_page_ranges(pages: list[int] | None) -> str | None:
    if not pages:
        return None
    normalized = sorted({int(page) for page in pages if int(page) > 0})
    if not normalized:
        return None
    return ",".join(str(page) for page in normalized)


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
    deadline = time.monotonic() + _mathpix_pdf_wait_timeout_seconds()
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
                f"Mathpix PDF {pdf_id} did not complete within {_mathpix_pdf_wait_timeout_seconds()} seconds "
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
    pdf_path: Path | None = None,
) -> list[dict[str, Any]]:
    pdf_path = pdf_path or _paper_pdf_path(paper_id, layout=layout)
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
    pdf_path: Path | None = None,
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

    pdf_path = pdf_path or _paper_pdf_path(paper_id, layout=layout)
    page_ranges = _mathpix_pdf_page_ranges(pages)
    return _mathpix_pdf_submit(
        pdf_path,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        endpoint=endpoint,
        page_ranges=page_ranges,
    )


def fetch_mathpix_pdf_status(
    pdf_id: str,
    *,
    endpoint: str = MATHPIX_PDF_ENDPOINT,
    app_id: str | None = None,
    app_key: str | None = None,
) -> dict[str, Any]:
    resolved_app_id = app_id or os.environ.get("MATHPIX_APP_ID")
    resolved_app_key = app_key or os.environ.get("MATHPIX_APP_KEY")
    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError("Mathpix credentials not found. Set MATHPIX_APP_ID and MATHPIX_APP_KEY.")
    if endpoint.rstrip("/") != MATHPIX_PDF_ENDPOINT:
        raise RuntimeError(f"fetch_mathpix_pdf_status expects the Mathpix PDF endpoint, not {endpoint}.")
    return _mathpix_pdf_status(pdf_id, app_id=resolved_app_id, app_key=resolved_app_key, endpoint=endpoint)


def download_mathpix_pdf(
    paper_id: str,
    pdf_id: str,
    *,
    pdf_path: Path | None = None,
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
        "pages": _mathpix_pdf_lines_to_page_payloads(lines_payload, paper_id, layout=layout, pdf_path=pdf_path),
    }


def run_mathpix(
    paper_id: str,
    *,
    pages: list[int] | None = None,
    pdf_path: Path | None = None,
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
        pdf_path=pdf_path,
        endpoint=endpoint,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        layout=layout,
    )
    _mathpix_pdf_wait_for_completion(pdf_id, app_id=resolved_app_id, app_key=resolved_app_key, endpoint=endpoint)
    return download_mathpix_pdf(
        paper_id,
        pdf_id,
        pdf_path=pdf_path,
        endpoint=endpoint,
        app_id=resolved_app_id,
        app_key=resolved_app_key,
        layout=layout,
    )


def write_external_sources(
    paper_id: str,
    layout: dict[str, Any],
    math: dict[str, Any],
    *,
    project_layout: ProjectLayout | None = None,
) -> tuple[Path, Path]:
    destination = _output_dir(paper_id, layout=project_layout)
    destination.mkdir(parents=True, exist_ok=True)
    layout_path = destination / "layout.json"
    math_path = destination / "math.json"
    layout_path.write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    math_path.write_text(json.dumps(math, indent=2) + "\n", encoding="utf-8")
    return layout_path, math_path
