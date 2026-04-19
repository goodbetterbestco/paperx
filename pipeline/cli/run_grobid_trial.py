from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.grobid_trial import run_grobid_trial


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-backed GROBID metadata/reference trial.")
    parser.add_argument("--manifest", required=True, help="Path to a GROBID trial manifest JSON file.")
    return parser.parse_args()


def run_grobid_trial_cli(
    args: argparse.Namespace,
    *,
    run_trial_fn: Callable[[str], dict[str, Any]] = run_grobid_trial,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = run_trial_fn(args.manifest)
    print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_grobid_trial_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
