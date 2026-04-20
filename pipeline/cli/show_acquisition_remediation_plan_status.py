from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.remediation_plan_artifacts import DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR
from pipeline.acquisition.remediation_plan_status import summarize_remediation_plan_status
from pipeline.acquisition.remediation_reports import DEFAULT_REMEDIATION_HISTORY_DIR
from pipeline.output.acquisition_remediation_plan_status_report import (
    render_acquisition_remediation_plan_status_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show the current acquisition remediation plan execution status.")
    parser.add_argument("--from-plan", help="Saved remediation plan label or path. Defaults to the current plan summary.")
    parser.add_argument(
        "--plan-output-dir",
        default=str(DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR),
        help="Directory for remediation plan artifacts.",
    )
    parser.add_argument(
        "--remediation-history-dir",
        default=str(DEFAULT_REMEDIATION_HISTORY_DIR),
        help="Directory for remediation queue history artifacts.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_show_remediation_plan_status_cli(
    args: argparse.Namespace,
    *,
    summarize_status_fn: Callable[..., dict[str, Any]] = summarize_remediation_plan_status,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_plan_status_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = summarize_status_fn(
        from_plan=getattr(args, "from_plan", None),
        plan_output_dir=Path(getattr(args, "plan_output_dir", DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR)),
        remediation_history_dir=Path(getattr(args, "remediation_history_dir", DEFAULT_REMEDIATION_HISTORY_DIR)),
    )
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_show_remediation_plan_status_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
