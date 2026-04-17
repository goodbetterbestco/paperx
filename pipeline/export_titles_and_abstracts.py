#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import current_layout
from pipeline.output.title_abstract_export import build_export_text, export_titles_and_abstracts


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
    summary = export_titles_and_abstracts(args.output, layout=current_layout())
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
