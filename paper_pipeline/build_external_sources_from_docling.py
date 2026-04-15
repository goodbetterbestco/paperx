#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.docling_adapter import docling_json_to_external_sources, run_docling, write_external_sources


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources from Docling output.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--docling-json", help="Use an existing Docling JSON file instead of running Docling.")
    parser.add_argument("--device", choices=("auto", "cpu", "mps"), help="Docling device override.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize extracted sources without writing them.")
    return parser.parse_args()


def _load_docling_document(paper_id: str, docling_json: str | None, device: str | None) -> tuple[dict, str]:
    docling_path = Path(docling_json) if docling_json else run_docling(paper_id, device=device)
    document = json.loads(docling_path.read_text(encoding="utf-8"))
    return document, str(docling_path)


def _build_summary(layout: dict, math: dict, source_path: str) -> dict[str, object]:
    return {
        "docling_json": source_path,
        "layout_engine": layout.get("engine"),
        "layout_blocks": len(layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
    }


def main() -> int:
    args = parse_args()
    document, source_path = _load_docling_document(args.paper_id, args.docling_json, args.device)
    external_layout, external_math = docling_json_to_external_sources(document, args.paper_id)
    summary = _build_summary(external_layout, external_math, source_path)

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    layout_path, math_path = write_external_sources(args.paper_id, external_layout, external_math)
    print(
        json.dumps(
            {
                **summary,
                "layout_path": str(layout_path),
                "math_path": str(math_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
