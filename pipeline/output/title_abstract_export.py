from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, canonical_path, current_layout
from pipeline.corpus.metadata import discover_paper_pdf_paths, paper_id_from_pdf_path


def _paper_ids(*, layout: ProjectLayout | None = None) -> list[str]:
    return [paper_id_from_pdf_path(path, layout=layout) for path in discover_paper_pdf_paths(layout=layout)]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _block_text(block: dict[str, Any]) -> str:
    spans = ((block.get("content") or {}).get("spans") or [])
    parts = [
        str(span.get("text", "")).strip()
        for span in spans
        if isinstance(span, dict) and span.get("kind") == "text" and str(span.get("text", "")).strip()
    ]
    return " ".join(parts).strip()


def _title_and_abstract(document: dict[str, Any]) -> tuple[str, str]:
    front_matter = document.get("front_matter") or {}
    title = str(front_matter.get("title") or "").strip()
    abstract_id = str(front_matter.get("abstract_block_id") or "").strip()
    abstract = ""
    if abstract_id:
        for block in document.get("blocks") or []:
            if str(block.get("id", "")).strip() == abstract_id:
                abstract = _block_text(block)
                break
    return title, abstract


def build_export_text(*, layout: ProjectLayout | None = None) -> str:
    sections: list[str] = []
    for paper_id in _paper_ids(layout=layout):
        title, abstract = _title_and_abstract(_load_json(canonical_path(paper_id, layout=layout)))
        sections.append(f"{title}\n\n{abstract}".strip())
    return "\n\n---\n\n".join(sections) + "\n"


def export_titles_and_abstracts(
    output_path: str | Path,
    *,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    active_layout = layout or current_layout()
    resolved_output = Path(output_path).expanduser().resolve()
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(build_export_text(layout=active_layout), encoding="utf-8")
    return {
        "path": str(resolved_output),
        "papers": len(_paper_ids(layout=active_layout)),
    }
