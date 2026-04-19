from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark_status import summarize_latest_benchmark_status
from pipeline.output.acquisition_benchmark_status_report import render_acquisition_benchmark_status_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show the latest acquisition benchmark status and trend.")
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional benchmark history directory. Defaults to the repo acquisition benchmark history path.",
    )
    parser.add_argument("--limit", type=int, default=3, help="Maximum improvements/regressions to highlight.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_show_benchmark_status_cli(
    args: argparse.Namespace,
    *,
    summarize_status_fn: Callable[..., dict[str, Any]] = summarize_latest_benchmark_status,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_status_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = summarize_status_fn(history_dir=args.history_dir, limit=args.limit)
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_show_benchmark_status_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
