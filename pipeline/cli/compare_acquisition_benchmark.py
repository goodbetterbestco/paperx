from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.benchmark_compare import compare_benchmark_reports, resolve_benchmark_report_path
from pipeline.output.acquisition_benchmark_compare_report import (
    render_acquisition_benchmark_comparison_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two acquisition benchmark summary reports.")
    parser.add_argument(
        "--base",
        required=True,
        help="Baseline report path, snapshot label, or 'latest'/'previous' alias resolved from history.",
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help="Candidate report path, snapshot label, or 'latest'/'previous' alias resolved from history.",
    )
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional benchmark history directory used for snapshot labels and latest/previous aliases.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_compare_benchmark_cli(
    args: argparse.Namespace,
    *,
    compare_reports_fn: Callable[[str, str], dict[str, Any]] = compare_benchmark_reports,
    resolve_report_path_fn: Callable[..., Path] = resolve_benchmark_report_path,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_comparison_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    history_dir = getattr(args, "history_dir", None)
    resolve_kwargs = {"history_dir": history_dir} if history_dir else {}
    base_path = resolve_report_path_fn(args.base, **resolve_kwargs)
    candidate_path = resolve_report_path_fn(args.candidate, **resolve_kwargs)
    report = compare_reports_fn(str(base_path), str(candidate_path))
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_compare_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
