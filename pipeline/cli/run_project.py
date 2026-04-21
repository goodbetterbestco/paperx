#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a project folder from source state into processed state, then run the processor."
    )
    parser.add_argument("project_dir", help="Path to the paperx project folder.")
    parser.add_argument(
        "--max-workers",
        type=int,
        default=20,
        help="Maximum number of papers to process concurrently. Defaults to 20.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    os.environ["PIPELINE_PROJECT_DIR"] = str(project_dir)
    os.environ.pop("PIPELINE_CORPUS_DIR", None)

    from pipeline.corpus_layout import prepare_project_inputs

    preparation = prepare_project_inputs()
    paper_ids = preparation.get("paper_ids", [])
    if not paper_ids:
        print(
            json.dumps(
                {
                    "project_dir": str(project_dir),
                    "error": "No PDF inputs were found in the project root.",
                    **preparation,
                },
                indent=2,
            )
        )
        return 2

    from pipeline.processor.corpus import process_corpus

    run_result = process_corpus(max_workers=args.max_workers)
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
