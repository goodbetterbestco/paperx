from __future__ import annotations

import os
from pathlib import Path
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pipeline.corpus_layout import ProjectLayout


PAPER_ID_TOKEN_RE = re.compile(r"[^a-z0-9]+")
PAPER_DIR_RE = re.compile(r"^\d{4}_.+")


def normalize_paper_id(value: str) -> str:
    normalized = PAPER_ID_TOKEN_RE.sub("_", value.lower()).strip("_")
    return normalized or "paper"


def corpus_paper_id(paper_id: str) -> str:
    return normalize_paper_id(paper_id)


def configured_project_dir() -> Path | None:
    configured = os.environ.get("PIPELINE_PROJECT_DIR", "").strip()
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def configured_corpus_dir(root: Path, corpus_name: str) -> Path:
    configured = os.environ.get("PIPELINE_CORPUS_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return root / "corpus" / corpus_name


def existing_project_paper_ids(layout: ProjectLayout) -> set[str]:
    paper_ids: set[str] = set()
    if layout.corpus_root.exists():
        for path in layout.corpus_root.iterdir():
            if not path.is_dir():
                continue
            if path.name.startswith("_") or path.name in {"source", "corpus"}:
                continue
            if not PAPER_DIR_RE.match(path.name):
                continue
            paper_ids.add(path.name)
    return paper_ids


def prepare_project_inputs(layout: ProjectLayout) -> dict[str, object]:
    if not layout.project_mode or layout.project_dir is None:
        return {
            "project_mode": False,
            "project_dir": None,
            "moved_pdfs": [],
            "paper_ids": [],
        }

    project_dir = layout.project_dir
    source_dir = layout.source_root
    corpus_dir = layout.corpus_root
    runs_dir = layout.runs_root
    legacy_source_dir = project_dir / "source"

    if legacy_source_dir.exists():
        raise RuntimeError(
            f"Legacy project input directory is no longer supported: {legacy_source_dir}. "
            "Move PDFs into the project root and rerun."
        )

    project_dir.mkdir(parents=True, exist_ok=True)
    corpus_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    preexisting_ids = existing_project_paper_ids(layout)
    reserved_ids = set(preexisting_ids)
    moved_pdfs: list[dict[str, str]] = []
    discovered_ids: set[str] = set()

    candidate_pdfs = sorted(path for path in project_dir.glob("*.pdf") if path.is_file())

    for existing_dir in sorted(path for path in corpus_dir.iterdir() if path.is_dir()):
        if existing_dir.name.startswith("_") or existing_dir.name in {"source", "corpus"}:
            continue
        existing_pdf = existing_dir / f"{normalize_paper_id(existing_dir.name)}.pdf"
        if existing_pdf.exists():
            discovered_ids.add(normalize_paper_id(existing_dir.name))
            reserved_ids.add(normalize_paper_id(existing_dir.name))

    for pdf_path in candidate_pdfs:
        base_id = normalize_paper_id(pdf_path.stem)
        paper_id = base_id
        suffix = 2
        while paper_id in reserved_ids:
            if paper_id in preexisting_ids:
                existing_target = corpus_dir / paper_id / f"{paper_id}.pdf"
                raise FileExistsError(
                    f"Cannot move {pdf_path.name} into processed state; {existing_target} already exists. "
                    "Reset the corpus back to source state before rebuilding."
                )
            paper_id = f"{base_id}_{suffix}"
            suffix += 1
        target_path = corpus_dir / paper_id / f"{paper_id}.pdf"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.rename(target_path)
        reserved_ids.add(paper_id)
        discovered_ids.add(paper_id)
        moved_pdfs.append(
            {
                "from": str(pdf_path),
                "to": str(target_path),
                "paper_id": paper_id,
            }
        )

    for paper_id in sorted(existing_project_paper_ids(layout)):
        discovered_ids.add(normalize_paper_id(paper_id))

    return {
        "project_mode": True,
        "project_dir": str(project_dir),
        "source_dir": str(source_dir),
        "corpus_dir": str(corpus_dir),
        "moved_pdfs": moved_pdfs,
        "paper_ids": sorted(discovered_ids),
    }


def display_path(path: str | Path, *, layout: ProjectLayout, root: Path) -> str:
    resolved = Path(path).expanduser().resolve()
    candidate_bases: list[Path] = []
    if layout.project_dir is not None:
        candidate_bases.extend([layout.project_dir, layout.source_root, layout.corpus_root, root])
    else:
        candidate_bases.extend([layout.corpus_root.parent, layout.corpus_root, root])
    deduped_bases: list[Path] = []
    seen_bases: set[Path] = set()
    for base in candidate_bases:
        resolved_base = base.resolve()
        if resolved_base in seen_bases:
            continue
        deduped_bases.append(resolved_base)
        seen_bases.add(resolved_base)
    for base in deduped_bases:
        try:
            return str(resolved.relative_to(base))
        except ValueError:
            continue
    return str(resolved)
