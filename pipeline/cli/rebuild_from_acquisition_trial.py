from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from typing import Any

from pipeline.acquisition.trial_promotion import promote_acquisition_trial
from pipeline.cli.paper_build import build_paper
from pipeline.corpus_layout import current_layout
from pipeline.output.artifacts import build_summary, write_canonical_outputs
from pipeline.output.validation import CanonicalValidationError, validate_canonical


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a named acquisition trial bundle and rebuild the canonical from the promoted sources."
    )
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus or project.")
    parser.add_argument(
        "--label",
        default="follow-up",
        help="Trial bundle label under canonical_sources/trials/. Defaults to follow-up.",
    )
    parser.add_argument(
        "--text-engine",
        choices=("native", "pdftotext", "hybrid"),
        default="native",
        help="Text extraction source for prose blocks.",
    )
    parser.add_argument(
        "--include-review",
        action="store_true",
        help="Also write the markdown review output after rebuilding.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing outputs.")
    return parser.parse_args()


def run_rebuild_from_trial_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    promote_trial_fn: Callable[..., dict[str, Any]] = promote_acquisition_trial,
    build_paper_fn: Callable[..., object] = build_paper,
    validate_canonical_fn: Callable[[dict[str, object]], None] = validate_canonical,
    build_summary_fn: Callable[[dict[str, object]], dict[str, object]] = build_summary,
    write_canonical_outputs_fn: Callable[..., dict[str, str]] = write_canonical_outputs,
    print_fn: Callable[..., None] = print,
) -> int:
    layout = current_layout_fn()
    promotion = promote_trial_fn(
        args.paper_id,
        layout=layout,
        label=args.label,
    )
    if not bool(promotion.get("promoted")):
        print_fn(json.dumps(promotion, indent=2))
        return 3
    try:
        build = build_paper_fn(
            args.paper_id,
            text_engine=args.text_engine,
            use_external_layout=True,
            use_external_math=True,
            include_review=bool(args.include_review),
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
    if args.dry_run:
        print_fn(
            json.dumps(
                {
                    "paper_id": args.paper_id,
                    "promotion": promotion,
                    **summary,
                },
                indent=2,
            )
        )
        return 0

    outputs = write_canonical_outputs_fn(
        args.paper_id,
        document,
        include_review=bool(args.include_review),
        layout=build.layout,
    )
    print_fn(
        json.dumps(
            {
                "paper_id": args.paper_id,
                "promotion": promotion,
                **outputs,
                **summary,
            },
            indent=2,
        )
    )
    return 0


def main() -> int:
    return run_rebuild_from_trial_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
