from __future__ import annotations

import argparse
import json
from collections.abc import Callable

from pipeline.corpus_layout import CORPUS_DIR, current_layout
from pipeline.output.artifacts import build_summary, write_canonical_outputs
from pipeline.output.validation import CanonicalValidationError, validate_canonical
from pipeline.processor.paper import build_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical.json for a paper.")
    parser.add_argument("paper_id", help=f"Paper id in the configured layout ({CORPUS_DIR}).")
    parser.add_argument(
        "--text-engine",
        choices=("native", "pdftotext", "hybrid"),
        default="native",
        help="Text extraction source for prose blocks.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing the file.")
    parser.add_argument("--validate", action="store_true", help="Validate the output and exit.")
    return parser.parse_args()


def run_build_canonical(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    build_paper_fn: Callable[..., object] = build_paper,
    validate_canonical_fn: Callable[[dict[str, object]], None] = validate_canonical,
    build_summary_fn: Callable[[dict[str, object]], dict[str, object]] = build_summary,
    write_canonical_outputs_fn: Callable[..., dict[str, str]] = write_canonical_outputs,
    print_fn: Callable[..., None] = print,
) -> int:
    layout = current_layout_fn()
    try:
        build = build_paper_fn(
            args.paper_id,
            text_engine=args.text_engine,
            include_review=False,
            layout=layout,
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
    if args.dry_run or args.validate:
        print_fn(json.dumps(summary, indent=2))
        return 0

    outputs = write_canonical_outputs_fn(args.paper_id, document, include_review=False, layout=build.layout)
    print_fn(json.dumps({"path": outputs["canonical_path"], **summary}, indent=2))
    return 0


def main() -> int:
    return run_build_canonical(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
