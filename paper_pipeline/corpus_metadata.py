from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from paper_pipeline.corpus_layout import CORPUS_DIR, PROJECT_MODE, SOURCE_DIR, corpus_paper_id, normalize_paper_id, paper_pdf_path


PAPER_DIR_RE = re.compile(r"^(?:kernel_)?\d{4}_.+")
FIGURE_EXPECTATIONS_PATH = CORPUS_DIR / "figure_expectations.json"


def paper_dir_name_from_paper_id(paper_id: str) -> str:
    return corpus_paper_id(paper_id)


def paper_id_from_dir_name(dir_name: str) -> str:
    return corpus_paper_id(dir_name)


def is_paper_dir(path: Path) -> bool:
    return path.is_dir() and bool(PAPER_DIR_RE.match(path.name))


def paper_id_from_pdf_path(pdf_path: Path) -> str:
    if PROJECT_MODE and pdf_path.parent.resolve() == SOURCE_DIR.resolve():
        return corpus_paper_id(pdf_path.stem)
    if PAPER_DIR_RE.match(pdf_path.parent.name):
        return paper_id_from_dir_name(pdf_path.parent.name)
    return corpus_paper_id(pdf_path.stem)


def canonical_pdf_filename(paper_id: str) -> str:
    return f"{corpus_paper_id(paper_id)}.pdf"


def discover_paper_pdf_paths() -> list[Path]:
    if PROJECT_MODE:
        return sorted(path for path in SOURCE_DIR.glob("*.pdf") if path.is_file())

    pdf_paths: list[Path] = []
    for candidate_dir in sorted(path for path in CORPUS_DIR.iterdir() if is_paper_dir(path)):
        paper_id = paper_id_from_dir_name(candidate_dir.name)
        preferred = candidate_dir / canonical_pdf_filename(paper_id)
        legacy = candidate_dir / f"{paper_id}.pdf"
        if preferred.exists():
            pdf_paths.append(preferred)
            continue
        if legacy.exists():
            pdf_paths.append(legacy)
            continue
        other_pdfs = sorted(path for path in candidate_dir.glob("*.pdf") if path.is_file())
        if other_pdfs:
            pdf_paths.append(other_pdfs[0])
    return pdf_paths


@lru_cache(maxsize=1)
def load_figure_expectations() -> dict[str, dict[str, Any]]:
    if not FIGURE_EXPECTATIONS_PATH.exists():
        return {}
    payload = json.loads(FIGURE_EXPECTATIONS_PATH.read_text(encoding="utf-8"))
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in entries.items():
        if not isinstance(value, dict):
            continue
        paper_id = paper_id_from_dir_name(str(key))
        normalized[paper_id] = dict(value)
    return normalized


def paper_figure_metadata(paper_id: str) -> dict[str, Any] | None:
    return load_figure_expectations().get(paper_id)


def build_figure_expectations(metadata: dict[str, Any] | None) -> dict[str, object] | None:
    if not metadata:
        return None
    expected_semantic_figure_count = metadata.get("expected_semantic_figure_count")
    expected_no_semantic_figures = bool(metadata.get("expected_no_semantic_figures", False))
    figure_notes = metadata.get("notes")
    if (
        expected_semantic_figure_count is None
        and not expected_no_semantic_figures
        and figure_notes is None
    ):
        return None
    return {
        "expected_semantic_figure_count": expected_semantic_figure_count,
        "expected_no_semantic_figures": expected_no_semantic_figures,
        "notes": figure_notes,
    }
