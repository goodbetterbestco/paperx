from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pipeline.corpus_layout import ProjectLayout


PAPER_ID_TOKEN_RE = re.compile(r"[^a-z0-9]+")
PAPER_DIR_RE = re.compile(r"^\d{4}_.+")
PAPER_UID_HEX_LEN = 5


def normalize_paper_id(value: str) -> str:
    normalized = PAPER_ID_TOKEN_RE.sub("_", value.lower()).strip("_")
    return normalized or "paper"


def corpus_paper_id(paper_id: str) -> str:
    return normalize_paper_id(paper_id)


def paper_uid(paper_id: str) -> str:
    canonical_paper_id = corpus_paper_id(paper_id)
    digest_size = max(1, (PAPER_UID_HEX_LEN + 1) // 2)
    digest = hashlib.blake2b(canonical_paper_id.encode("utf-8"), digest_size=digest_size).hexdigest()
    return digest[:PAPER_UID_HEX_LEN]


def canonical_filename(paper_id: str) -> str:
    return f"canonical_{paper_uid(paper_id)}.json"


def figure_manifest_filename(paper_id: str) -> str:
    return f"figure_manifest_{paper_uid(paper_id)}.json"

def configured_corpus_dir(root: Path, corpus_name: str) -> Path:
    configured = os.environ.get("PIPELINE_CORPUS_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return root / "corpus" / corpus_name

def display_path(path: str | Path, *, layout: ProjectLayout, root: Path) -> str:
    resolved = Path(path).expanduser().resolve()
    data_root = layout.resolved_data_root()
    figures_root = layout.resolved_figures_root()
    candidate_bases = [layout.corpus_root.parent, layout.source_root, data_root, figures_root, layout.corpus_root, root]
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
