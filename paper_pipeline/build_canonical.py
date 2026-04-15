#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from paper_pipeline.corpus_layout import CORPUS_DIR, canonical_path
from paper_pipeline.reconcile_blocks import reconcile_paper
from paper_pipeline.validate_canonical import CanonicalValidationError, validate_canonical


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical.json for a paper.")
    parser.add_argument("paper_id", help=f"Paper directory id under the configured corpus ({CORPUS_DIR}).")
    parser.add_argument(
        "--text-engine",
        choices=("native", "pdftotext", "hybrid"),
        default="native",
        help="Text extraction source for prose blocks.",
    )
    parser.add_argument(
        "--use-external-layout",
        action="store_true",
        help="Use <corpus>/<paper>/canonical_sources/layout.json when present.",
    )
    parser.add_argument(
        "--use-external-math",
        action="store_true",
        help="Use <corpus>/<paper>/canonical_sources/math.json when present.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing the file.")
    parser.add_argument("--validate", action="store_true", help="Validate the output and exit.")
    return parser.parse_args()


def build_summary(document: dict) -> dict[str, int]:
    return {
        "sections": len(document.get("sections", [])),
        "blocks": len(document.get("blocks", [])),
        "math": len(document.get("math", [])),
        "figures": len(document.get("figures", [])),
        "references": len(document.get("references", [])),
    }


def main() -> int:
    args = parse_args()
    paper_id = args.paper_id

    document = reconcile_paper(
        paper_id,
        text_engine=args.text_engine,
        use_external_layout=args.use_external_layout,
        use_external_math=args.use_external_math,
    )
    try:
        validate_canonical(document)
    except CanonicalValidationError as exc:
        print(f"validation_error={exc}")
        return 2

    if args.dry_run or args.validate:
        print(json.dumps(build_summary(document), indent=2))
        return 0

    output_path = canonical_path(paper_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(output_path), **build_summary(document)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
