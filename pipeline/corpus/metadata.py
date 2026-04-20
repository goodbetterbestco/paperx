from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, corpus_paper_id, current_layout


__all__ = [
    "PAPER_DIR_RE",
    "build_figure_expectations",
    "canonical_pdf_filename",
    "discover_paper_pdf_paths",
    "is_paper_dir",
    "load_figure_expectations",
    "paper_dir_name_from_paper_id",
    "paper_figure_metadata",
    "paper_id_from_dir_name",
    "paper_id_from_pdf_path",
]


PAPER_DIR_RE = re.compile(r"^\d{4}_.+")
def paper_dir_name_from_paper_id(paper_id: str) -> str:
    return corpus_paper_id(paper_id)


def paper_id_from_dir_name(dir_name: str) -> str:
    return corpus_paper_id(dir_name)


def is_paper_dir(path: Path) -> bool:
    return path.is_dir() and bool(PAPER_DIR_RE.match(path.name))


def paper_id_from_pdf_path(pdf_path: Path, *, layout: ProjectLayout | None = None) -> str:
    active_layout = layout or current_layout()
    if pdf_path.parent.resolve() == active_layout.source_root.resolve():
        return corpus_paper_id(pdf_path.stem)
    if PAPER_DIR_RE.match(pdf_path.parent.name):
        return paper_id_from_dir_name(pdf_path.parent.name)
    return corpus_paper_id(pdf_path.stem)


def canonical_pdf_filename(paper_id: str) -> str:
    return f"{corpus_paper_id(paper_id)}.pdf"


def discover_paper_pdf_paths(*, layout: ProjectLayout | None = None) -> list[Path]:
    active_layout = layout or current_layout()
    pdf_by_id: dict[str, Path] = {}
    corpus_root = active_layout.corpus_root
    if not corpus_root.exists():
        return []
    for pdf_path in sorted(path for path in active_layout.source_root.glob("*.pdf") if path.is_file()):
        pdf_by_id[paper_id_from_pdf_path(pdf_path, layout=active_layout)] = pdf_path
    for candidate_dir in sorted(path for path in corpus_root.iterdir() if is_paper_dir(path)):
        paper_id = paper_id_from_dir_name(candidate_dir.name)
        if paper_id in pdf_by_id:
            continue
        preferred = active_layout.paper_pdf_path(paper_id)
        legacy = candidate_dir / f"{paper_id}.pdf"
        if preferred.exists():
            pdf_by_id[paper_id] = preferred
            continue
        if legacy.exists():
            pdf_by_id[paper_id] = legacy
            continue
        other_pdfs = sorted(path for path in candidate_dir.glob("*.pdf") if path.is_file())
        if other_pdfs:
            pdf_by_id[paper_id] = other_pdfs[0]
    return [pdf_by_id[paper_id] for paper_id in sorted(pdf_by_id)]


@lru_cache(maxsize=None)
def _load_figure_expectations(expectations_path: str) -> dict[str, dict[str, Any]]:
    path = Path(expectations_path)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
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


def load_figure_expectations(*, layout: ProjectLayout | None = None) -> dict[str, dict[str, Any]]:
    active_layout = layout or current_layout()
    return _load_figure_expectations(str(active_layout.figure_expectations_path.resolve()))


def paper_figure_metadata(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any] | None:
    return load_figure_expectations(layout=layout).get(paper_id)


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
