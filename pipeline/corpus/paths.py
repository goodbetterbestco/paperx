from __future__ import annotations

import os
from pathlib import Path
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pipeline.corpus_layout import ProjectLayout


PAPER_ID_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def normalize_paper_id(value: str) -> str:
    normalized = PAPER_ID_TOKEN_RE.sub("_", value.lower()).strip("_")
    return normalized or "paper"


def corpus_paper_id(paper_id: str) -> str:
    return normalize_paper_id(paper_id)


def env_value(name: str, legacy_name: str, default: str = "") -> str:
    return os.environ.get(name, os.environ.get(legacy_name, default)).strip()


def configured_project_dir() -> Path | None:
    configured = env_value("PIPELINE_PROJECT_DIR", "PAPER_PIPELINE_PROJECT_DIR")
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def configured_corpus_dir(root: Path, corpus_name: str) -> Path:
    configured = env_value("PIPELINE_CORPUS_DIR", "PAPER_PIPELINE_CORPUS_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    corpora_dir = root / "corpus"
    extracted_home = corpora_dir / corpus_name
    if extracted_home.exists():
        return extracted_home
    legacy_home = root / corpus_name
    if legacy_home.exists():
        return legacy_home
    # Current in-repo fallback during migration. The intended home is
    # ~/Projects/paperx/corpus/<corpus-name>, beginning with
    # ~/Projects/paperx/corpus/stepview.
    return root / "docs"


def existing_project_paper_ids(layout: ProjectLayout) -> set[str]:
    paper_ids: set[str] = set()
    if layout.source_root.exists():
        paper_ids.update(normalize_paper_id(path.stem) for path in layout.source_root.glob("*.pdf"))
    if layout.corpus_root.exists():
        paper_ids.update(path.name for path in layout.corpus_root.iterdir() if path.is_dir() and path.name != "_runs")
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

    project_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    corpus_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    reserved_ids = existing_project_paper_ids(layout)
    moved_pdfs: list[dict[str, str]] = []
    discovered_ids: set[str] = set()

    for pdf_path in sorted(path for path in project_dir.glob("*.pdf") if path.is_file()):
        base_id = normalize_paper_id(pdf_path.stem)
        paper_id = base_id
        suffix = 2
        while paper_id in reserved_ids:
            paper_id = f"{base_id}_{suffix}"
            suffix += 1
        target_path = source_dir / f"{paper_id}.pdf"
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

    for pdf_path in sorted(path for path in source_dir.glob("*.pdf") if path.is_file()):
        paper_id = normalize_paper_id(pdf_path.stem)
        target_path = source_dir / f"{paper_id}.pdf"
        if pdf_path != target_path:
            if target_path.exists():
                raise FileExistsError(f"Cannot normalize source PDF name {pdf_path.name}; {target_path.name} already exists")
            pdf_path.rename(target_path)
        discovered_ids.add(paper_id)
        layout.paper_dir(paper_id).mkdir(parents=True, exist_ok=True)

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
    candidate_bases = [root]
    if layout.project_dir is not None:
        candidate_bases.extend([layout.project_dir, layout.source_root, layout.corpus_root])
    else:
        candidate_bases.extend([layout.corpus_root.parent, layout.corpus_root])
    for base in candidate_bases:
        try:
            return str(resolved.relative_to(base.resolve()))
        except ValueError:
            continue
    return str(resolved)
