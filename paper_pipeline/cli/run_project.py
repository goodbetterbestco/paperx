#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize a paperx project folder, then run the full paper pipeline against it."
    )
    parser.add_argument("project_dir", help="Path to the paperx project folder.")
    parser.add_argument(
        "--start-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to start from. Defaults to 1.",
    )
    parser.add_argument(
        "--end-round",
        type=int,
        choices=(1, 2),
        default=1,
        help="Round number to end on. Defaults to 1.",
    )
    parser.add_argument(
        "--stop-after-round",
        type=int,
        choices=(1, 2),
        default=None,
        help="Optional round number after which execution should stop.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum number of papers to process concurrently within a round.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Rebuild every targeted paper even when the canonical is already fresh.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    os.environ["PAPER_PIPELINE_PROJECT_DIR"] = str(project_dir)
    os.environ.pop("PAPER_PIPELINE_CORPUS_DIR", None)

    from paper_pipeline.corpus_layout import prepare_project_inputs

    preparation = prepare_project_inputs()
    paper_ids = preparation.get("paper_ids", [])
    if not paper_ids:
        print(
            json.dumps(
                {
                    "project_dir": str(project_dir),
                    "error": "No PDF inputs were found in the project root or source/.",
                    **preparation,
                },
                indent=2,
            )
        )
        return 2

    from paper_pipeline.run_corpus_rounds import run_rounds

    run_result = run_rounds(
        start_round=args.start_round,
        end_round=args.end_round,
        stop_after_round=args.stop_after_round,
        max_workers=args.max_workers,
        force_rebuild=bool(args.force_rebuild),
    )
    print(
        json.dumps(
            {
                "project_dir": str(project_dir),
                **preparation,
                **run_result,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
