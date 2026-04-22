from __future__ import annotations

import re
from typing import Any

try:
    import fitz  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    fitz = None  # type: ignore

from pipeline.native_stderr import open_pdf_with_diagnostics
from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, display_path, paper_pdf_path
from pipeline.figures.labels import caption_label
from pipeline.text.headings import compact_text, heading_info, looks_like_structural_title  # noqa: E402
from pipeline.types import LayoutBlock  # noqa: E402

DOCS_DIR = CORPUS_DIR

REFERENCE_RE = re.compile(r"^[A-Z][A-Za-z0-9.-]{1,16}\]")
PAGE_NUMBER_RE = re.compile(r"^\d{1,3}$")


def _require_fitz() -> Any:
    if fitz is None:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required for layout extraction.")
    return fitz


def _rect_dict(rect: fitz.Rect) -> dict[str, float]:
    return {
        "x0": round(float(rect.x0), 2),
        "y0": round(float(rect.y0), 2),
        "x1": round(float(rect.x1), 2),
        "y1": round(float(rect.y1), 2),
        "width": round(float(rect.width), 2),
        "height": round(float(rect.height), 2),
    }


def _classify_role(
    text: str,
    page_num: int,
    page_count: int,
    rect: fitz.Rect,
    page_rect: fitz.Rect,
    meta: dict[str, Any],
) -> str:
    lowered = text.lower()
    center_x = (rect.x0 + rect.x1) / 2
    horizontal_center = abs(center_x - (page_rect.width / 2)) <= page_rect.width * 0.08

    if PAGE_NUMBER_RE.fullmatch(text) and horizontal_center and rect.y0 >= page_rect.height * 0.85:
        return "page_number"
    if caption_label(text):
        return "caption"
    if page_num == 1 and "supported in part" in lowered:
        return "footnote"
    if page_num == 1 and rect.y1 <= page_rect.height * 0.38:
        return "front_matter"

    info = heading_info({"type": "heading", "text": text})
    word_count = len(re.findall(r"[A-Za-z0-9]+", text))
    line_count = int(meta.get("line_count") or 1)
    if (
        info is not None
        and rect.y1 <= page_rect.height * 0.92
        and line_count <= 5
        and (
            (info.label is not None and all(part.isdigit() for part in info.label))
            or looks_like_structural_title(info.title)
        )
        and word_count <= 12
    ):
        return "heading"

    if page_num >= max(2, page_count - 3) and REFERENCE_RE.match(text):
        return "reference"
    return "paragraph"


def _block_text(block: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    texts: list[str] = []
    font_sizes: list[float] = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            span_text = str(span.get("text", ""))
            if span_text:
                texts.append(span_text)
                if span.get("size") is not None:
                    font_sizes.append(float(span["size"]))
    return compact_text(" ".join(texts)), {
        "font_size_max": round(max(font_sizes), 2) if font_sizes else None,
        "font_size_min": round(min(font_sizes), 2) if font_sizes else None,
        "line_count": len(block.get("lines", [])),
    }


def extract_layout(
    paper_id: str,
    *,
    layout: ProjectLayout | None = None,
    pdf_path: str | Any | None = None,
) -> dict[str, Any]:
    fitz_module = _require_fitz()
    resolved_pdf_path = paper_pdf_path(paper_id, layout=layout) if pdf_path is None else pdf_path
    document = open_pdf_with_diagnostics(
        f"{paper_id} stage=layout-open",
        resolved_pdf_path,
        fitz_module=fitz_module,
    )
    blocks: list[LayoutBlock] = []
    page_sizes: list[dict[str, float]] = []
    try:
        for page_index in range(document.page_count):
            page_num = page_index + 1
            page = document.load_page(page_index)
            page_rect = fitz_module.Rect(page.rect)
            page_sizes.append({"page": page_num, "width": round(page_rect.width, 2), "height": round(page_rect.height, 2)})

            order = 0
            for block in page.get_text("dict")["blocks"]:
                if block.get("type") != 0:
                    continue
                rect = fitz_module.Rect(block["bbox"])
                text, meta = _block_text(block)
                if not text:
                    continue
                order += 1
                role = _classify_role(text, page_num, document.page_count, rect, page_rect, meta)
                blocks.append(
                    LayoutBlock(
                        id=f"layout-p{page_num:03d}-b{order:03d}",
                        page=page_num,
                        order=order,
                        text=text,
                        role=role,
                        bbox=_rect_dict(rect),
                        meta=meta,
                    )
                )
        return {
            "pdf_path": display_path(resolved_pdf_path, layout=layout),
            "page_count": len(page_sizes),
            "page_sizes_pt": page_sizes,
            "blocks": blocks,
        }
    finally:
        document.close()
