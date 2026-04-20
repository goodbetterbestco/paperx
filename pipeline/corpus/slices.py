from __future__ import annotations

import json
import shutil
from pathlib import Path

from pipeline.corpus.paths import PAPER_DIR_RE, normalize_paper_id


def _coerce_paper_id(value: str) -> str:
    raw = value.strip()
    if raw.lower().endswith(".pdf"):
        raw = raw[:-4]
    return normalize_paper_id(raw)


def normalize_requested_paper_ids(values: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        paper_id = _coerce_paper_id(value)
        if not paper_id or paper_id in seen:
            continue
        normalized.append(paper_id)
        seen.add(paper_id)
    return normalized


def load_source_slice_manifest(manifest_path: str | Path) -> dict[str, object]:
    path = Path(manifest_path).expanduser().resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_papers = payload.get("papers")
    if not isinstance(raw_papers, list) or not raw_papers:
        raise ValueError(f"Source slice manifest {path} must define a non-empty 'papers' list.")
    paper_ids = normalize_requested_paper_ids([str(value) for value in raw_papers])
    if not paper_ids:
        raise ValueError(f"Source slice manifest {path} does not contain any usable paper ids.")
    return {
        "manifest_path": str(path),
        "label": str(payload.get("label", "")).strip() or path.stem,
        "description": str(payload.get("description", "")).strip(),
        "paper_ids": paper_ids,
        "paper_count": len(paper_ids),
    }


def _discover_source_pdf_map(source_corpus_dir: Path) -> dict[str, Path]:
    source_pdfs = sorted(path for path in source_corpus_dir.glob("*.pdf") if path.is_file())
    if source_pdfs:
        return {normalize_paper_id(path.stem): path for path in source_pdfs}
    has_processed_dirs = any(path.is_dir() and PAPER_DIR_RE.match(path.name) for path in source_corpus_dir.iterdir())
    if has_processed_dirs:
        raise FileNotFoundError(
            f"No source-state PDFs were found at {source_corpus_dir}. "
            "The corpus appears to be in processed state; reset it before materializing a slice."
        )
    raise FileNotFoundError(f"No source-state PDFs were found at {source_corpus_dir}.")


def materialize_source_slice(
    source_corpus_dir: str | Path,
    target_project_dir: str | Path,
    *,
    paper_ids: list[str],
    clobber: bool = False,
) -> dict[str, object]:
    source_root = Path(source_corpus_dir).expanduser().resolve()
    target_root = Path(target_project_dir).expanduser().resolve()
    requested_paper_ids = normalize_requested_paper_ids(paper_ids)
    if not requested_paper_ids:
        raise ValueError("Provide at least one paper id when materializing a source slice.")
    if target_root == source_root or source_root in target_root.parents:
        raise ValueError("Target project dir must live outside the source corpus.")

    source_pdf_map = _discover_source_pdf_map(source_root)
    missing_paper_ids = [paper_id for paper_id in requested_paper_ids if paper_id not in source_pdf_map]
    if missing_paper_ids:
        missing_display = ", ".join(missing_paper_ids)
        raise FileNotFoundError(f"Missing source PDFs for requested paper ids: {missing_display}")

    removed_existing_target = False
    if target_root.exists():
        if target_root.is_file():
            raise FileExistsError(f"Target project dir {target_root} already exists as a file.")
        if any(target_root.iterdir()):
            if not clobber:
                raise FileExistsError(f"Target project dir {target_root} is not empty. Pass --force to replace it.")
            shutil.rmtree(target_root)
            removed_existing_target = True

    target_root.mkdir(parents=True, exist_ok=True)
    copied_pdfs: list[dict[str, str]] = []
    for paper_id in requested_paper_ids:
        source_path = source_pdf_map[paper_id]
        target_path = target_root / source_path.name
        shutil.copy2(source_path, target_path)
        copied_pdfs.append(
            {
                "paper_id": paper_id,
                "from": str(source_path),
                "to": str(target_path),
            }
        )

    return {
        "source_corpus_dir": str(source_root),
        "target_project_dir": str(target_root),
        "state": "source",
        "paper_ids": requested_paper_ids,
        "paper_count": len(requested_paper_ids),
        "copied_pdfs": copied_pdfs,
        "removed_existing_target": removed_existing_target,
        "run_project_command": f"python3 -m pipeline.cli.run_project {target_root}",
    }
