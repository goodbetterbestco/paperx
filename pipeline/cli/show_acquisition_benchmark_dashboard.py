from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.benchmark_artifacts import current_benchmark_output_dir, load_current_benchmark_dashboard
from pipeline.acquisition.benchmark_dashboard import summarize_benchmark_dashboard
from pipeline.output.acquisition_benchmark_dashboard_report import (
    render_acquisition_benchmark_dashboard_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show the acquisition benchmark operator dashboard.")
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional benchmark history directory. Defaults to the repo acquisition benchmark history path.",
    )
    parser.add_argument("--history-limit", type=int, default=5, help="Number of recent runs to include in the dashboard.")
    parser.add_argument("--trend-limit", type=int, default=3, help="Maximum regressions to highlight per watchlist.")
    parser.add_argument(
        "--from-artifacts",
        action="store_true",
        help="Read the current saved dashboard artifact instead of recomputing from history.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_show_benchmark_dashboard_cli(
    args: argparse.Namespace,
    *,
    summarize_dashboard_fn: Callable[..., dict[str, Any]] = summarize_benchmark_dashboard,
    load_dashboard_fn: Callable[..., dict[str, Any]] = load_current_benchmark_dashboard,
    resolve_output_dir_fn: Callable[..., Path] = current_benchmark_output_dir,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_dashboard_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    if getattr(args, "from_artifacts", False):
        report = load_dashboard_fn(output_dir=resolve_output_dir_fn(history_dir=args.history_dir))
    else:
        report = summarize_dashboard_fn(
            history_dir=args.history_dir,
            history_limit=args.history_limit,
            trend_limit=args.trend_limit,
        )
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_show_benchmark_dashboard_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
