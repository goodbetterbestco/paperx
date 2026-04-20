from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

from pipeline.corpus.paths import PAPER_DIR_RE, normalize_paper_id


def _remove_path(path: Path) -> int:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return 1
    if path.is_dir():
        count = sum(1 for child in path.rglob("*") if child.is_file() or child.is_symlink())
        shutil.rmtree(path)
        return count
    return 0


def _paper_id_for_pdf(pdf_path: Path, *, corpus_dir: Path) -> str:
    if pdf_path.parent == corpus_dir or pdf_path.parent.name == "source":
        return normalize_paper_id(pdf_path.stem)
    if PAPER_DIR_RE.match(pdf_path.parent.name):
        return normalize_paper_id(pdf_path.parent.name)
    if pdf_path.parent.parent == corpus_dir / "corpus" and PAPER_DIR_RE.match(pdf_path.parent.name):
        return normalize_paper_id(pdf_path.parent.name)
    return normalize_paper_id(pdf_path.stem)


def _discover_pdf_candidates(corpus_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    candidates.extend(sorted(path for path in corpus_dir.glob("*.pdf") if path.is_file()))
    legacy_source = corpus_dir / "source"
    if legacy_source.exists():
        candidates.extend(sorted(path for path in legacy_source.glob("*.pdf") if path.is_file()))
    candidates.extend(sorted(path for path in corpus_dir.glob("*/*.pdf") if path.is_file() and PAPER_DIR_RE.match(path.parent.name)))
    legacy_corpus = corpus_dir / "corpus"
    if legacy_corpus.exists():
        candidates.extend(sorted(path for path in legacy_corpus.glob("*/*.pdf") if path.is_file() and PAPER_DIR_RE.match(path.parent.name)))
    return candidates


def reset_corpus_to_source_state(corpus_dir: str | Path) -> dict[str, object]:
    root = Path(corpus_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    moved_pdfs: list[dict[str, str]] = []
    deduped_pdfs: list[str] = []

    for pdf_path in _discover_pdf_candidates(root):
        paper_id = _paper_id_for_pdf(pdf_path, corpus_dir=root)
        target_path = root / f"{paper_id}.pdf"
        if pdf_path == target_path:
            continue
        if target_path.exists():
            if not filecmp.cmp(pdf_path, target_path, shallow=False):
                raise FileExistsError(
                    f"Cannot reset corpus to source state because {target_path} already exists with different contents "
                    f"than {pdf_path}."
                )
            pdf_path.unlink()
            deduped_pdfs.append(str(pdf_path))
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.rename(target_path)
        moved_pdfs.append({"from": str(pdf_path), "to": str(target_path), "paper_id": paper_id})

    removed_files = 0
    removed_paths: list[str] = []
    for artifact_path in [
        root / "_canon",
        root / "review_drafts",
        root / "_runs",
        root / "source",
        root / "corpus",
        root / "corpus_lexicon.json",
        root / "figure_expectations.json",
    ]:
        if not artifact_path.exists():
            continue
        removed_files += _remove_path(artifact_path)
        removed_paths.append(str(artifact_path))

    for review_path in sorted(root.glob("*.canonical.review.md")):
        removed_files += _remove_path(review_path)
        removed_paths.append(str(review_path))

    for paper_dir in sorted(path for path in root.iterdir() if path.is_dir() and PAPER_DIR_RE.match(path.name)):
        removed_files += _remove_path(paper_dir)
        removed_paths.append(str(paper_dir))

    source_pdfs = sorted(path.name for path in root.glob("*.pdf") if path.is_file())
    return {
        "corpus_dir": str(root),
        "state": "source",
        "paper_count": len(source_pdfs),
        "source_pdfs": source_pdfs,
        "moved_pdfs": moved_pdfs,
        "deduped_pdfs": deduped_pdfs,
        "removed_paths": removed_paths,
        "removed_file_count": removed_files,
    }

