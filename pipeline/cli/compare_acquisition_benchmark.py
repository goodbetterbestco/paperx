from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.output.acquisition_benchmark_compare_report import (
    render_acquisition_benchmark_comparison_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two acquisition benchmark summary reports.")
    parser.add_argument("--base", required=True, help="Path to the baseline benchmark summary JSON.")
    parser.add_argument("--candidate", required=True, help="Path to the candidate benchmark summary JSON.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_compare_benchmark_cli(
    args: argparse.Namespace,
    *,
    compare_reports_fn: Callable[[str, str], dict[str, Any]] = compare_benchmark_reports,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_comparison_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = compare_reports_fn(args.base, args.candidate)
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_compare_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
