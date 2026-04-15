#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.external_sources import external_layout_path
from paper_pipeline.pdftotext_overlay import overlay_pdftotext_onto_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources/layout.json from native layout + pdftotext.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize without writing the file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload, summary = overlay_pdftotext_onto_layout(args.paper_id)
    destination = external_layout_path(args.paper_id)
    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(destination), **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
