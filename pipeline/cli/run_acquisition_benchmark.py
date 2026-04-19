from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark import run_acquisition_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-backed acquisition benchmark.")
    parser.add_argument("--manifest", required=True, help="Path to an acquisition benchmark manifest JSON file.")
    return parser.parse_args()


def run_benchmark_cli(
    args: argparse.Namespace,
    *,
    run_benchmark_fn: Callable[[str], dict[str, Any]] = run_acquisition_benchmark,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = run_benchmark_fn(args.manifest)
    print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
