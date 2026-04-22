from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

from pipeline.corpus_layout import CORPUS_DIR, current_layout
from pipeline.output.artifacts import build_summary, write_canonical_outputs
from pipeline.output.review_renderer import render_document
from pipeline.output.validation import CanonicalValidationError, validate_canonical
from pipeline.processor.paper import build_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build canonical.json and the markdown review draft in one sequential pass."
    )
    parser.add_argument("paper_id", help=f"Paper id in the configured layout ({CORPUS_DIR}).")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing files.")
    return parser.parse_args()


def run_build_review(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    build_paper_fn: Callable[..., object] = build_paper,
    validate_canonical_fn: Callable[[dict[str, object]], None] = validate_canonical,
    build_summary_fn: Callable[[dict[str, object]], dict[str, object]] = build_summary,
    render_document_fn: Callable[[dict[str, object]], str] = render_document,
    write_canonical_outputs_fn: Callable[..., dict[str, str]] = write_canonical_outputs,
    print_fn: Callable[..., None] = print,
) -> int:
    try:
        build = build_paper_fn(
            args.paper_id,
            include_review=True,
            layout=current_layout_fn(),
        )
    except RuntimeError as exc:
        print_fn(f"build_error={exc}")
        return 1
    document = build.document
    try:
        validate_canonical_fn(document)
    except CanonicalValidationError as exc:
        print_fn(f"validation_error={exc}")
        return 2

    summary = build_summary_fn(document)

    if args.dry_run:
        print_fn(
            json.dumps(
                {
                    "paper_id": args.paper_id,
                    **summary,
                    "review_chars": len(render_document_fn(document)),
                },
                indent=2,
            )
        )
        return 0

    outputs = write_canonical_outputs_fn(args.paper_id, document, include_review=True, layout=build.layout)
    canonical_exists = Path(outputs["canonical_path"]).exists()
    review_exists = Path(outputs["review_path"]).exists()
    print_fn(
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


def main() -> int:
    return run_build_review(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
