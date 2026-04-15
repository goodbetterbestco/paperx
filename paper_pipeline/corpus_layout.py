from __future__ import annotations

import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_NAME = "stepview"
CORPUS_NAME = os.environ.get("PAPER_PIPELINE_CORPUS_NAME", DEFAULT_CORPUS_NAME).strip() or DEFAULT_CORPUS_NAME
PAPER_ID_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def _configured_project_dir() -> Path | None:
    configured = os.environ.get("PAPER_PIPELINE_PROJECT_DIR", "").strip()
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def _configured_corpus_dir() -> Path:
    configured = os.environ.get("PAPER_PIPELINE_CORPUS_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    extracted_home = ROOT / CORPUS_NAME
    if extracted_home.exists():
        return extracted_home
    # Current in-repo home. The intended extracted home is
    # ~/Projects/paperx/<corpus-name>, beginning with ~/Projects/paperx/stepview.
    return ROOT / "docs"


PROJECT_DIR = _configured_project_dir()
PROJECT_MODE = PROJECT_DIR is not None

if PROJECT_MODE:
    SOURCE_DIR = PROJECT_DIR / "source"
    CORPUS_DIR = PROJECT_DIR / "corpus"
    REVIEW_DRAFTS_DIR = PROJECT_DIR
    CORPUS_RUNS_DIR = CORPUS_DIR / "_runs"
else:
    CORPUS_DIR = _configured_corpus_dir()
    SOURCE_DIR = CORPUS_DIR
    REVIEW_DRAFTS_DIR = CORPUS_DIR / "review_drafts"
    CORPUS_RUNS_DIR = CORPUS_DIR / "_runs"

BIBLIOGRAPHY_PATH = CORPUS_DIR / "bibliography.json"
CORPUS_LEXICON_PATH = CORPUS_DIR / "corpus_lexicon.json"


def normalize_paper_id(value: str) -> str:
    normalized = PAPER_ID_TOKEN_RE.sub("_", value.lower()).strip("_")
    return normalized or "paper"


def project_root() -> Path:
    return PROJECT_DIR if PROJECT_DIR is not None else CORPUS_DIR


def paper_dir(paper_id: str) -> Path:
    return CORPUS_DIR / paper_id


def paper_pdf_path(paper_id: str) -> Path:
    if PROJECT_MODE:
        return SOURCE_DIR / f"{paper_id}.pdf"
    return paper_dir(paper_id) / f"{paper_id}.pdf"


def canonical_path(paper_id: str) -> Path:
    return paper_dir(paper_id) / "canonical.json"


def canonical_sources_dir(paper_id: str) -> Path:
    return paper_dir(paper_id) / "canonical_sources"


def figures_dir(paper_id: str) -> Path:
    return paper_dir(paper_id) / "figures"


def figure_manifest_path(paper_id: str) -> Path:
    return figures_dir(paper_id) / "manifest.json"


def review_draft_path(paper_id: str) -> Path:
    return REVIEW_DRAFTS_DIR / f"{paper_id}.canonical.review.md"


def project_report_path() -> Path:
    return CORPUS_RUNS_DIR / "final_summary.md"


def project_status_path() -> Path:
    return CORPUS_RUNS_DIR / "status.json"


def _existing_project_paper_ids() -> set[str]:
    paper_ids: set[str] = set()
    if SOURCE_DIR.exists():
        paper_ids.update(normalize_paper_id(path.stem) for path in SOURCE_DIR.glob("*.pdf"))
    if CORPUS_DIR.exists():
        paper_ids.update(path.name for path in CORPUS_DIR.iterdir() if path.is_dir() and path.name != "_runs")
    return paper_ids


def prepare_project_inputs() -> dict[str, object]:
    if not PROJECT_MODE or PROJECT_DIR is None:
        return {
            "project_mode": False,
            "project_dir": None,
            "moved_pdfs": [],
            "paper_ids": [],
        }

    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    reserved_ids = _existing_project_paper_ids()
    moved_pdfs: list[dict[str, str]] = []
    discovered_ids: set[str] = set()

    for pdf_path in sorted(path for path in PROJECT_DIR.glob("*.pdf") if path.is_file()):
        base_id = normalize_paper_id(pdf_path.stem)
        paper_id = base_id
        suffix = 2
        while paper_id in reserved_ids:
            paper_id = f"{base_id}_{suffix}"
            suffix += 1
        target_path = SOURCE_DIR / f"{paper_id}.pdf"
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

    for pdf_path in sorted(path for path in SOURCE_DIR.glob("*.pdf") if path.is_file()):
        paper_id = normalize_paper_id(pdf_path.stem)
        target_path = SOURCE_DIR / f"{paper_id}.pdf"
        if pdf_path != target_path:
            if target_path.exists():
                raise FileExistsError(f"Cannot normalize source PDF name {pdf_path.name}; {target_path.name} already exists")
            pdf_path.rename(target_path)
        discovered_ids.add(paper_id)
        paper_dir(paper_id).mkdir(parents=True, exist_ok=True)

    return {
        "project_mode": True,
        "project_dir": str(PROJECT_DIR),
        "source_dir": str(SOURCE_DIR),
        "corpus_dir": str(CORPUS_DIR),
        "moved_pdfs": moved_pdfs,
        "paper_ids": sorted(discovered_ids),
    }


def display_path(path: str | Path) -> str:
    resolved = Path(path).expanduser().resolve()
    candidate_bases = [ROOT]
    if PROJECT_DIR is not None:
        candidate_bases.extend([PROJECT_DIR, SOURCE_DIR, CORPUS_DIR])
    else:
        candidate_bases.extend([CORPUS_DIR.parent, CORPUS_DIR])
    for base in candidate_bases:
        try:
            return str(resolved.relative_to(base.resolve()))
        except ValueError:
            continue
    return str(resolved)
