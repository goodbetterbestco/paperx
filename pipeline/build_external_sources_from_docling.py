#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.cli.external_source_build import build_docling_external_sources
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources from Docling output.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--docling-json", help="Use an existing Docling JSON file instead of running Docling.")
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), help="Docling device override.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize extracted sources without writing them.")
    return parser.parse_args()
def main() -> int:
    args = parse_args()
    build = build_docling_external_sources(
        args.paper_id,
        docling_json=args.docling_json,
        device=args.device,
        layout=current_layout(),
    )

    if args.dry_run:
        print(json.dumps(build.summary, indent=2))
        return 0

    outputs = build.write()
    print(
        json.dumps(
            {
                **build.summary,
                **outputs,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
