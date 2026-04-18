from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, paper_pdf_path
from pipeline.text.headings import compact_text

DOCS_DIR = CORPUS_DIR
PAGE_SPLIT_RE = "\f"


def pdftotext_available() -> bool:
    return shutil.which("pdftotext") is not None


def _pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return paper_pdf_path(paper_id, layout=layout)


def _run_pdftotext(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def extract_pdftotext_pages(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[int, list[str]]:
    pdf_path = _pdf_path(paper_id, layout=layout)
    text = _run_pdftotext(pdf_path)
    pages = [page for page in text.split(PAGE_SPLIT_RE) if page.strip()]
    return {
        page_index + 1: page_text.splitlines()
        for page_index, page_text in enumerate(pages)
    }


def slice_page_text(lines: list[str], *, start_line: int, end_line: int) -> str:
    start = max(0, start_line)
    end = min(len(lines) - 1, end_line)
    if end < start or not lines:
        return ""
    return compact_text(" ".join(line.strip() for line in lines[start : end + 1] if line.strip()))


def bbox_to_line_window(bbox: dict[str, float], *, page_height: float, line_count: int, pad_lines: int = 1) -> tuple[int, int]:
    if page_height <= 0 or line_count <= 0:
        return 0, -1
    y0 = float(bbox.get("y0", 0.0))
    y1 = float(bbox.get("y1", y0))
    start = math.floor((y0 / page_height) * line_count) - pad_lines
    end = math.ceil((y1 / page_height) * line_count) + pad_lines
    return max(0, start), min(line_count - 1, end)
