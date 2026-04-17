#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import canonical_path
from pipeline.corpus_metadata import discover_paper_pdf_paths, paper_id_from_pdf_path


def _paper_ids() -> list[str]:
    return [paper_id_from_pdf_path(path) for path in discover_paper_pdf_paths()]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _block_text(block: dict) -> str:
    spans = ((block.get("content") or {}).get("spans") or [])
    parts = [
        str(span.get("text", "")).strip()
        for span in spans
        if isinstance(span, dict) and span.get("kind") == "text" and str(span.get("text", "")).strip()
    ]
    return " ".join(parts).strip()


def _title_and_abstract(document: dict) -> tuple[str, str]:
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


def build_export_text() -> str:
    sections: list[str] = []
    for paper_id in _paper_ids():
        title, abstract = _title_and_abstract(_load_json(canonical_path(paper_id)))
        sections.append(f"{title}\n\n{abstract}".strip())
    return "\n\n---\n\n".join(sections) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export paper titles and abstracts from canonical.json files.")
    parser.add_argument(
        "--output",
        default=str(Path.home() / "Downloads" / "stepview_titles_and_abstracts.md"),
        help="Destination markdown path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).expanduser().resolve()
    output_path.write_text(build_export_text(), encoding="utf-8")
    print(json.dumps({"path": str(output_path), "papers": len(_paper_ids())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
