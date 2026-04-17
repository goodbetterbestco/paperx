#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.cli.external_source_build import build_mathpix_external_sources
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources from Mathpix PDF OCR output.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--page", type=int, action="append", dest="pages", help="Limit to one or more 1-based page numbers.")
    parser.add_argument("--endpoint", default="https://api.mathpix.com/v3/pdf", help="Mathpix PDF OCR endpoint.")
    parser.add_argument("--app-id", help="Override MATHPIX_APP_ID.")
    parser.add_argument("--app-key", help="Override MATHPIX_APP_KEY.")
    parser.add_argument(
        "--mathpix-json",
        action="append",
        help="Use one or more existing Mathpix page response JSON files instead of calling the API.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Summarize extracted sources without writing them.")
    return parser.parse_args()
def main() -> int:
    args = parse_args()
    build = build_mathpix_external_sources(
        args.paper_id,
        pages=args.pages,
        endpoint=args.endpoint,
        app_id=args.app_id,
        app_key=args.app_key,
        mathpix_json=args.mathpix_json,
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
