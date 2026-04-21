from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI_PYTHON = ROOT / ".venv-paperx" / "bin" / "python"
PAPER_ID = "1990_synthetic_test_paper"
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
    return str(CLI_PYTHON if CLI_PYTHON.exists() else Path(sys.executable))


def project_env(project_dir: Path, *, skip_env_local: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    env["PIPELINE_PROJECT_DIR"] = str(project_dir)
    env.pop("PIPELINE_CORPUS_DIR", None)
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


def _processed_layout_payload() -> dict[str, object]:
    return {
        "engine": "docling",
        "pdf_path": f"{PAPER_ID}/{PAPER_ID}.pdf",
        "page_count": 1,
        "page_sizes_pt": [{"page": 1, "width": 612.0, "height": 792.0}],
        "blocks": [
            {
                "id": "b1",
                "page": 1,
                "order": 1,
                "text": TITLE,
                "role": "front_matter",
                "bbox": {"x0": 72, "y0": 72, "x1": 420, "y1": 90},
                "meta": {},
            },
            {
                "id": "b2",
                "page": 1,
                "order": 2,
                "text": AUTHORS,
                "role": "front_matter",
                "bbox": {"x0": 72, "y0": 110, "x1": 350, "y1": 126},
                "meta": {},
            },
            {
                "id": "b3",
                "page": 1,
                "order": 3,
                "text": AFFILIATION,
                "role": "front_matter",
                "bbox": {"x0": 72, "y0": 140, "x1": 460, "y1": 156},
                "meta": {},
            },
            {
                "id": "b4",
                "page": 1,
                "order": 4,
                "text": "Abstract",
                "role": "front_matter",
                "bbox": {"x0": 72, "y0": 180, "x1": 130, "y1": 196},
                "meta": {},
            },
            {
                "id": "b5",
                "page": 1,
                "order": 5,
                "text": ABSTRACT,
                "role": "front_matter",
                "bbox": {"x0": 72, "y0": 200, "x1": 500, "y1": 216},
                "meta": {},
            },
            {
                "id": "b6",
                "page": 1,
                "order": 6,
                "text": "1. Introduction",
                "role": "heading",
                "bbox": {"x0": 72, "y0": 240, "x1": 220, "y1": 256},
                "meta": {},
            },
            {
                "id": "b7",
                "page": 1,
                "order": 7,
                "text": BODY,
                "role": "paragraph",
                "bbox": {"x0": 72, "y0": 270, "x1": 520, "y1": 286},
                "meta": {},
            },
        ],
    }


def create_processed_project_fixture(project_dir: Path) -> Path:
    paper_dir = project_dir / PAPER_ID
    sources_dir = paper_dir / "canonical_sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / f"{PAPER_ID}.pdf").write_bytes(build_single_page_text_pdf())
    (sources_dir / "layout.json").write_text(
        json.dumps(_processed_layout_payload(), indent=2) + "\n",
        encoding="utf-8",
    )
    return paper_dir


def create_source_project_fixture(project_dir: Path) -> Path:
    project_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = project_dir / f"{PAPER_ID}.pdf"
    pdf_path.write_bytes(build_single_page_text_pdf())
    return pdf_path
