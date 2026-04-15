from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
from threading import BoundedSemaphore, Lock
from typing import Any
from urllib import request

from paper_pipeline.corpus_layout import CORPUS_DIR, canonical_sources_dir, display_path, paper_pdf_path
from paper_pipeline.math_review_policy import review_for_math_entry
from paper_pipeline.types import default_formula_conversion, default_review

DOCS_DIR = CORPUS_DIR
MATHPIX_TEXT_ENDPOINT = "https://api.mathpix.com/v3/text"
_MATHPIX_REQUEST_SEMAPHORE: BoundedSemaphore | None = None
_MATHPIX_REQUEST_LIMIT: int | None = None
_MATHPIX_REQUEST_LOCK = Lock()


def _load_fitz() -> Any:
    try:
        import fitz  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyMuPDF is required for live Mathpix page rendering.") from exc
    return fitz


def _paper_pdf_path(paper_id: str) -> Path:
    return paper_pdf_path(paper_id)


def _output_dir(paper_id: str) -> Path:
    return canonical_sources_dir(paper_id)


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def _mathpix_request_semaphore() -> BoundedSemaphore:
    global _MATHPIX_REQUEST_SEMAPHORE, _MATHPIX_REQUEST_LIMIT
    limit = _int_env("STEPVIEW_MATHPIX_REQUEST_LIMIT", 12)
    with _MATHPIX_REQUEST_LOCK:
        if _MATHPIX_REQUEST_SEMAPHORE is None or _MATHPIX_REQUEST_LIMIT != limit:
            _MATHPIX_REQUEST_SEMAPHORE = BoundedSemaphore(limit)
            _MATHPIX_REQUEST_LIMIT = limit
    return _MATHPIX_REQUEST_SEMAPHORE


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
    text = _clean_latex(str(line.get("text", "")))
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


def mathpix_pages_to_external_sources(page_payloads: list[dict[str, Any]], paper_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    pdf_path = _paper_pdf_path(paper_id)
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

    layout = {
        "engine": "mathpix",
        "pdf_path": display_path(pdf_path),
        "page_count": page_count,
        "page_sizes_pt": page_sizes_pt,
        "blocks": blocks,
    }
    math = {
        "engine": "mathpix",
        "entries": entries,
    }
    return layout, math


def _render_page_png_bytes(pdf_path: Path, page_number: int, *, scale: float) -> tuple[bytes, int, int, float, float]:
    fitz = _load_fitz()
    with fitz.open(pdf_path) as document:
        page = document[page_number - 1]
        matrix = fitz.Matrix(scale, scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pixmap.tobytes("png")
        return png_bytes, int(pixmap.width), int(pixmap.height), float(page.rect.width), float(page.rect.height)


def _mathpix_headers(app_id: str, app_key: str) -> dict[str, str]:
    return {
        "app_id": app_id,
        "app_key": app_key,
        "Content-Type": "application/json",
    }


def call_mathpix_on_page_image(
    image_bytes: bytes,
    *,
    app_id: str,
    app_key: str,
    endpoint: str = MATHPIX_TEXT_ENDPOINT,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    payload = {
        "src": "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii"),
        "formats": ["text", "data"],
        "data_options": {"include_latex": True},
        "include_line_data": True,
        "include_equation_tags": True,
    }
    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=_mathpix_headers(app_id, app_key),
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _mathpix_page_payload(
    pdf_path: Path,
    *,
    page_number: int,
    scale: float,
    endpoint: str,
    app_id: str,
    app_key: str,
) -> dict[str, Any]:
    image_bytes, image_width, image_height, page_width_pt, page_height_pt = _render_page_png_bytes(
        pdf_path, page_number, scale=scale
    )
    with _mathpix_request_semaphore():
        response = call_mathpix_on_page_image(
            image_bytes,
            app_id=app_id,
            app_key=app_key,
            endpoint=endpoint,
        )
    return {
        "page": page_number,
        "page_width_pt": page_width_pt,
        "page_height_pt": page_height_pt,
        "image_width": image_width,
        "image_height": image_height,
        "response": response,
    }


def run_mathpix(
    paper_id: str,
    *,
    pages: list[int] | None = None,
    scale: float = 2.0,
    endpoint: str = MATHPIX_TEXT_ENDPOINT,
    app_id: str | None = None,
    app_key: str | None = None,
    page_workers: int = 1,
) -> list[dict[str, Any]]:
    resolved_app_id = app_id or os.environ.get("MATHPIX_APP_ID")
    resolved_app_key = app_key or os.environ.get("MATHPIX_APP_KEY")
    if not resolved_app_id or not resolved_app_key:
        raise RuntimeError("Mathpix credentials not found. Set MATHPIX_APP_ID and MATHPIX_APP_KEY.")

    pdf_path = _paper_pdf_path(paper_id)
    fitz = _load_fitz()
    with fitz.open(pdf_path) as document:
        page_numbers = pages or list(range(1, document.page_count + 1))

    payloads: list[dict[str, Any]] = []
    worker_count = max(1, min(int(page_workers), len(page_numbers)))
    if worker_count == 1:
        for page_number in page_numbers:
            payloads.append(
                _mathpix_page_payload(
                    pdf_path,
                    page_number=page_number,
                    scale=scale,
                    endpoint=endpoint,
                    app_id=resolved_app_id,
                    app_key=resolved_app_key,
                )
            )
        return payloads

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_page = {
            executor.submit(
                _mathpix_page_payload,
                pdf_path,
                page_number=page_number,
                scale=scale,
                endpoint=endpoint,
                app_id=resolved_app_id,
                app_key=resolved_app_key,
            ): page_number
            for page_number in page_numbers
        }
        for future in as_completed(future_to_page):
            payloads.append(future.result())
    payloads.sort(key=lambda payload: int(payload["page"]))
    return payloads


def write_external_sources(paper_id: str, layout: dict[str, Any], math: dict[str, Any]) -> tuple[Path, Path]:
    destination = _output_dir(paper_id)
    destination.mkdir(parents=True, exist_ok=True)
    layout_path = destination / "layout.json"
    math_path = destination / "math.json"
    layout_path.write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    math_path.write_text(json.dumps(math, indent=2) + "\n", encoding="utf-8")
    return layout_path, math_path
