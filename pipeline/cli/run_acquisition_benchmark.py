from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark import run_acquisition_benchmark
from pipeline.output.acquisition_benchmark_report import render_acquisition_benchmark_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-backed acquisition benchmark.")
    parser.add_argument("--manifest", required=True, help="Path to an acquisition benchmark manifest JSON file.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    return parser.parse_args()


def run_benchmark_cli(
    args: argparse.Namespace,
    *,
    run_benchmark_fn: Callable[[str], dict[str, Any]] = run_acquisition_benchmark,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = run_benchmark_fn(args.manifest)
    if args.format == "markdown":
        print_fn(render_markdown_fn(report))
    else:
        print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
