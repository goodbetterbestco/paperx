from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark_history import list_benchmark_history
from pipeline.output.acquisition_benchmark_history_report import render_acquisition_benchmark_history_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List saved acquisition benchmark snapshots.")
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional benchmark history directory. Defaults to the repo acquisition benchmark history path.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional number of most recent runs to include.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_list_benchmark_history_cli(
    args: argparse.Namespace,
    *,
    list_history_fn: Callable[..., dict[str, Any]] = list_benchmark_history,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_history_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = list_history_fn(args.history_dir, limit=args.limit) if args.history_dir else list_history_fn(limit=args.limit)
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_list_benchmark_history_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
