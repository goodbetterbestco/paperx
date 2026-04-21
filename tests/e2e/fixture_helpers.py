from __future__ import annotations

import json
import os
from pathlib import Path

from pipeline.corpus_layout import paper_uid


ROOT = Path(__file__).resolve().parents[2]
CLI_PYTHON = ROOT / ".venv-paperx" / "bin" / "python"
PAPER_ID = "1990_synthetic_test_paper"
PAPER_UID = paper_uid(PAPER_ID)
CANONICAL_FILENAME = f"canonical_{PAPER_UID}.json"
TITLE = "A Synthetic Study of Stable Figure Recovery"
AUTHORS = "Ada Example and Bob Example"
AFFILIATION = "Department of Geometry, Synthetic Institute, Example City"
ABSTRACT = "Synthetic abstract for build CLI testing and review rendering."
BODY = "This section references a stable synthetic figure and a predictable workflow."

PDF_LINES: tuple[tuple[int, str], ...] = (
    (22, TITLE),
    (14, AUTHORS),
    (12, AFFILIATION),
    (14, "Abstract"),
    (12, ABSTRACT),
    (14, "1. Introduction"),
    (12, BODY),
)


def cli_python() -> str:
    if not CLI_PYTHON.exists():
        raise FileNotFoundError(
            f"Expected repo venv interpreter at {CLI_PYTHON}. Run `make install` before e2e tests."
        )
    return str(CLI_PYTHON)


def corpus_env(corpus_dir: Path, *, corpus_name: str = "synthetic", skip_env_local: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    env["PIPELINE_CORPUS_DIR"] = str(corpus_dir)
    env["PIPELINE_CORPUS_NAME"] = corpus_name
    env["STEPVIEW_DOCLING_DEVICE"] = "cpu"
    if skip_env_local:
        env["PIPELINE_SKIP_ENV_LOCAL"] = "1"
    return env


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_single_page_text_pdf(lines: tuple[tuple[int, str], ...] = PDF_LINES) -> bytes:
    content_lines = ["BT"]
    y_position = 720
    for index, (font_size, text) in enumerate(lines):
        escaped = _escape_pdf_text(text)
        if index == 0:
            content_lines.append(f"/F1 {font_size} Tf")
            content_lines.append(f"72 {y_position} Td")
        else:
            content_lines.append(f"/F1 {font_size} Tf")
            content_lines.append(f"0 {-34 if font_size >= 20 else -24 if font_size >= 14 else -20} Td")
        content_lines.append(f"({_escape_pdf_text(text)}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("utf-8")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    parts: list[bytes] = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(sum(len(part) for part in parts))
        parts.append(f"{index} 0 obj\n".encode("ascii"))
        parts.append(body)
        parts.append(b"\nendobj\n")

    xref_start = sum(len(part) for part in parts)
    parts.append(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    parts.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        parts.append(f"{offset:010d} 00000 n \n".encode("ascii"))
    parts.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    return b"".join(parts)


def create_processed_corpus_fixture(corpus_dir: Path) -> Path:
    source_dir = corpus_dir / "_source"
    source_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = source_dir / f"{PAPER_ID}.pdf"
    pdf_path.write_bytes(build_single_page_text_pdf())
    return pdf_path
