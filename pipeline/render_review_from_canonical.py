#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, current_layout, review_draft_path
from pipeline.output.review_renderer import render_document, write_review_from_canonical


DOCS_DIR = CORPUS_DIR
REVIEW_DRAFTS_DIR = DOCS_DIR / "review_drafts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a markdown review draft from canonical.json.")
    parser.add_argument("paper_id", help=f"Paper directory id under the configured corpus ({CORPUS_DIR}).")
    return parser.parse_args()


def output_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return review_draft_path(paper_id, layout=layout)


def main() -> int:
    args = parse_args()
    destination = write_review_from_canonical(args.paper_id, layout=current_layout())
    print(json.dumps({"path": str(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
