from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.remediation_trend import summarize_remediation_trend
from pipeline.output.acquisition_remediation_trend_report import render_acquisition_remediation_trend_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the latest acquisition remediation trend.")
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional remediation history directory. Defaults to the repo remediation history path.",
    )
    parser.add_argument("--base", default="previous", help="Baseline report path, snapshot label, or alias.")
    parser.add_argument("--candidate", default="latest", help="Candidate report path, snapshot label, or alias.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_summarize_remediation_trend_cli(
    args: argparse.Namespace,
    *,
    summarize_trend_fn: Callable[..., dict[str, Any]] = summarize_remediation_trend,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_trend_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = summarize_trend_fn(history_dir=args.history_dir, base=args.base, candidate=args.candidate)
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_summarize_remediation_trend_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
