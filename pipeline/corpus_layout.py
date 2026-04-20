from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipeline.corpus.paths import (
    configured_corpus_dir as _configured_corpus_dir,
    configured_project_dir as _configured_project_dir,
    corpus_paper_id,
    display_path as _display_path,
    env_value as _env_value,
    normalize_paper_id,
    prepare_project_inputs as _prepare_project_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_NAME = "stepview"


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
            source_root = project_dir
            corpus_root = project_dir
            review_root = project_dir / "_canon"
            runs_root = project_dir / "_runs"
            mode = "project"
        else:
            corpus_root = _configured_corpus_dir(root, corpus_name)
            source_root = corpus_root
            review_root = corpus_root / "_canon"
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
        converted = self.paper_dir(canonical_paper_id) / f"{canonical_paper_id}.pdf"
        if converted.exists():
            return converted
        source = self.source_root / f"{canonical_paper_id}.pdf"
        if source.exists():
            return source
        legacy_source = self.project_root() / "source" / f"{canonical_paper_id}.pdf"
        if legacy_source.exists():
            return legacy_source
        return converted

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


def prepare_project_inputs(layout: ProjectLayout | None = None) -> dict[str, object]:
    return _prepare_project_inputs(layout or DEFAULT_LAYOUT)


def display_path(path: str | Path, *, layout: ProjectLayout | None = None) -> str:
    return _display_path(path, layout=layout or DEFAULT_LAYOUT, root=ROOT)
