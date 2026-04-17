#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.corpus_layout import CORPUS_DIR
from pipeline.output_artifacts import build_summary, write_canonical_outputs
from pipeline.reconcile_blocks import reconcile_paper
from pipeline.render_review_from_canonical import render_document
from pipeline.validate_canonical import CanonicalValidationError, validate_canonical


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build canonical.json and the markdown review draft in one sequential pass."
    )
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
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    document = reconcile_paper(
        args.paper_id,
        text_engine=args.text_engine,
        use_external_layout=args.use_external_layout,
        use_external_math=args.use_external_math,
    )
    try:
        validate_canonical(document)
    except CanonicalValidationError as exc:
        print(f"validation_error={exc}")
        return 2

    summary = build_summary(document)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "paper_id": args.paper_id,
                    **summary,
                    "review_chars": len(render_document(document)),
                },
                indent=2,
            )
        )
        return 0

    outputs = write_canonical_outputs(args.paper_id, document, include_review=True)
    canonical_exists = Path(outputs["canonical_path"]).exists()
    review_exists = Path(outputs["review_path"]).exists()
    print(
        json.dumps(
            {
                "paper_id": args.paper_id,
                "canonical_path": outputs["canonical_path"],
                "canonical_exists": canonical_exists,
                "review_path": outputs["review_path"],
                "review_exists": review_exists,
                **summary,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
