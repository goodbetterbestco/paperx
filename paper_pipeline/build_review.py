#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from paper_pipeline.build_canonical import build_summary
from paper_pipeline.corpus_layout import CORPUS_DIR, canonical_path
from paper_pipeline.reconcile_blocks import reconcile_paper
from paper_pipeline.render_review_from_canonical import output_path, render_document
from paper_pipeline.validate_canonical import CanonicalValidationError, validate_canonical


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

    review_markdown = render_document(document)
    summary = build_summary(document)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "paper_id": args.paper_id,
                    **summary,
                    "review_chars": len(review_markdown),
                },
                indent=2,
            )
        )
        return 0

    canonical_target = canonical_path(args.paper_id)
    review_target = output_path(args.paper_id)
    canonical_target.parent.mkdir(parents=True, exist_ok=True)
    review_target.parent.mkdir(parents=True, exist_ok=True)

    canonical_target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    review_target.write_text(review_markdown, encoding="utf-8")

    canonical_exists = canonical_target.exists()
    review_exists = review_target.exists()
    print(
        json.dumps(
            {
                "paper_id": args.paper_id,
                "canonical_path": str(canonical_target),
                "canonical_exists": canonical_exists,
                "review_path": str(review_target),
                "review_exists": review_exists,
                **summary,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
