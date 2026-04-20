from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.benchmark_gates import evaluate_latest_benchmark_gates
from pipeline.output.acquisition_benchmark_gate_report import render_acquisition_benchmark_gate_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check soft regression gates for acquisition benchmark snapshots.")
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional benchmark history directory. Defaults to the repo acquisition benchmark history path.",
    )
    parser.add_argument(
        "--base",
        default="previous",
        help="Baseline report path, snapshot label, or alias. Defaults to 'previous'.",
    )
    parser.add_argument(
        "--candidate",
        default="latest",
        help="Candidate report path, snapshot label, or alias. Defaults to 'latest'.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_check_benchmark_gates_cli(
    args: argparse.Namespace,
    *,
    evaluate_gates_fn: Callable[..., dict[str, Any]] = evaluate_latest_benchmark_gates,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_gate_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = evaluate_gates_fn(
        history_dir=args.history_dir,
        base=args.base,
        candidate=args.candidate,
    )
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0 if report.get("status") == "pass" else 1


def main() -> int:
    return run_check_benchmark_gates_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
