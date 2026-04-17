from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_NAME = "stepview"
PAPER_ID_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def normalize_paper_id(value: str) -> str:
    normalized = PAPER_ID_TOKEN_RE.sub("_", value.lower()).strip("_")
    return normalized or "paper"


def corpus_paper_id(paper_id: str) -> str:
    return normalize_paper_id(paper_id)


def _env_value(name: str, legacy_name: str, default: str = "") -> str:
    return os.environ.get(name, os.environ.get(legacy_name, default)).strip()


def _configured_project_dir() -> Path | None:
    configured = _env_value("PIPELINE_PROJECT_DIR", "PAPER_PIPELINE_PROJECT_DIR")
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def _configured_corpus_dir(root: Path, corpus_name: str) -> Path:
    configured = _env_value("PIPELINE_CORPUS_DIR", "PAPER_PIPELINE_CORPUS_DIR")
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


@dataclass(frozen=True)
class ProjectLayout:
    engine_root: Path
    mode: str
    corpus_name: str
    project_dir: Path | None
    corpus_root: Path
    source_root: Path
    review_root: Path
    runs_root: Path
    tmp_root: Path
    figure_expectations_path: Path

    @classmethod
    def from_environment(cls, *, engine_root: Path | None = None) -> ProjectLayout:
        root = (engine_root or ROOT).resolve()
        corpus_name = _env_value("PIPELINE_CORPUS_NAME", "PAPER_PIPELINE_CORPUS_NAME", DEFAULT_CORPUS_NAME) or DEFAULT_CORPUS_NAME
        project_dir = _configured_project_dir()
        if project_dir is not None:
            source_root = project_dir / "source"
            corpus_root = project_dir / "corpus"
            review_root = project_dir
            runs_root = corpus_root / "_runs"
            mode = "project"
        else:
            corpus_root = _configured_corpus_dir(root, corpus_name)
            source_root = corpus_root
            review_root = corpus_root / "review_drafts"
            runs_root = corpus_root / "_runs"
            mode = "corpus"
        return cls(
            engine_root=root,
            mode=mode,
            corpus_name=corpus_name,
            project_dir=project_dir,
            corpus_root=corpus_root,
            source_root=source_root,
            review_root=review_root,
            runs_root=runs_root,
            tmp_root=root / "tmp",
            figure_expectations_path=corpus_root / "figure_expectations.json",
        )

    @property
    def project_mode(self) -> bool:
        return self.mode == "project"

    @property
    def corpus_lexicon_path(self) -> Path:
        return self.corpus_root / "corpus_lexicon.json"

    def project_root(self) -> Path:
        return self.project_dir if self.project_dir is not None else self.corpus_root

    def paper_dir(self, paper_id: str) -> Path:
        return self.corpus_root / corpus_paper_id(paper_id)

    def paper_pdf_path(self, paper_id: str) -> Path:
        canonical_paper_id = corpus_paper_id(paper_id)
        if self.project_mode:
            return self.source_root / f"{canonical_paper_id}.pdf"
        return self.paper_dir(canonical_paper_id) / f"{canonical_paper_id}.pdf"

    def canonical_path(self, paper_id: str) -> Path:
        return self.paper_dir(paper_id) / "canonical.json"

    def canonical_sources_dir(self, paper_id: str) -> Path:
        return self.paper_dir(paper_id) / "canonical_sources"

    def figures_dir(self, paper_id: str) -> Path:
        return self.paper_dir(paper_id) / "figures"

    def figure_manifest_path(self, paper_id: str) -> Path:
        return self.figures_dir(paper_id) / "manifest.json"

    def review_draft_path(self, paper_id: str) -> Path:
        return self.review_root / f"{corpus_paper_id(paper_id)}.canonical.review.md"

    def project_report_path(self) -> Path:
        return self.runs_root / "final_summary.md"

    def project_status_path(self) -> Path:
        return self.runs_root / "status.json"

    def discover_source_pdfs(self) -> list[Path]:
        return sorted(path for path in self.source_root.glob("*.pdf") if path.is_file())


DEFAULT_LAYOUT = ProjectLayout.from_environment(engine_root=ROOT)
CORPUS_NAME = DEFAULT_LAYOUT.corpus_name
PROJECT_DIR = DEFAULT_LAYOUT.project_dir
PROJECT_MODE = DEFAULT_LAYOUT.project_mode
CORPUS_DIR = DEFAULT_LAYOUT.corpus_root
SOURCE_DIR = DEFAULT_LAYOUT.source_root
REVIEW_DRAFTS_DIR = DEFAULT_LAYOUT.review_root
CORPUS_RUNS_DIR = DEFAULT_LAYOUT.runs_root
CORPUS_LEXICON_PATH = DEFAULT_LAYOUT.corpus_lexicon_path


def current_layout() -> ProjectLayout:
    return DEFAULT_LAYOUT


def project_root(*, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).project_root()


def paper_dir(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).paper_dir(paper_id)


def paper_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).paper_pdf_path(paper_id)


def canonical_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).canonical_path(paper_id)


def canonical_sources_dir(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).canonical_sources_dir(paper_id)


def figures_dir(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).figures_dir(paper_id)


def figure_manifest_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).figure_manifest_path(paper_id)


def review_draft_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).review_draft_path(paper_id)


def project_report_path(*, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).project_report_path()


def project_status_path(*, layout: ProjectLayout | None = None) -> Path:
    return (layout or DEFAULT_LAYOUT).project_status_path()


def _existing_project_paper_ids(layout: ProjectLayout) -> set[str]:
    paper_ids: set[str] = set()
    if layout.source_root.exists():
        paper_ids.update(normalize_paper_id(path.stem) for path in layout.source_root.glob("*.pdf"))
    if layout.corpus_root.exists():
        paper_ids.update(path.name for path in layout.corpus_root.iterdir() if path.is_dir() and path.name != "_runs")
    return paper_ids


def prepare_project_inputs(layout: ProjectLayout | None = None) -> dict[str, object]:
    active_layout = layout or DEFAULT_LAYOUT
    if not active_layout.project_mode or active_layout.project_dir is None:
        return {
            "project_mode": False,
            "project_dir": None,
            "moved_pdfs": [],
            "paper_ids": [],
        }

    project_dir = active_layout.project_dir
    source_dir = active_layout.source_root
    corpus_dir = active_layout.corpus_root
    runs_dir = active_layout.runs_root

    project_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    corpus_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    reserved_ids = _existing_project_paper_ids(active_layout)
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
        active_layout.paper_dir(paper_id).mkdir(parents=True, exist_ok=True)

    return {
        "project_mode": True,
        "project_dir": str(project_dir),
        "source_dir": str(source_dir),
        "corpus_dir": str(corpus_dir),
        "moved_pdfs": moved_pdfs,
        "paper_ids": sorted(discovered_ids),
    }


def display_path(path: str | Path, *, layout: ProjectLayout | None = None) -> str:
    resolved = Path(path).expanduser().resolve()
    candidate_bases = [ROOT]
    active_layout = layout or DEFAULT_LAYOUT
    if active_layout.project_dir is not None:
        candidate_bases.extend([active_layout.project_dir, active_layout.source_root, active_layout.corpus_root])
    else:
        candidate_bases.extend([active_layout.corpus_root.parent, active_layout.corpus_root])
    for base in candidate_bases:
        try:
            return str(resolved.relative_to(base.resolve()))
        except ValueError:
            continue
    return str(resolved)
