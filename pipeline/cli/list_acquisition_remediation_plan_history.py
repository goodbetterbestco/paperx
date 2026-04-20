from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.remediation_plan_history import list_remediation_plan_history
from pipeline.acquisition.remediation_plan_reports import DEFAULT_REMEDIATION_PLAN_HISTORY_DIR
from pipeline.acquisition.remediation_reports import DEFAULT_REMEDIATION_HISTORY_DIR
from pipeline.output.acquisition_remediation_plan_history_report import (
    render_acquisition_remediation_plan_history_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List saved acquisition remediation plan snapshots and execution state.")
    parser.add_argument(
        "--plan-history-dir",
        default=str(DEFAULT_REMEDIATION_PLAN_HISTORY_DIR),
        help="Directory for remediation plan history artifacts.",
    )
    parser.add_argument(
        "--remediation-history-dir",
        default=str(DEFAULT_REMEDIATION_HISTORY_DIR),
        help="Directory for remediation queue history artifacts.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of plan snapshots to include.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_list_remediation_plan_history_cli(
    args: argparse.Namespace,
    *,
    list_history_fn: Callable[..., dict[str, Any]] = list_remediation_plan_history,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_plan_history_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = list_history_fn(
        plan_history_dir=Path(getattr(args, "plan_history_dir", DEFAULT_REMEDIATION_PLAN_HISTORY_DIR)),
        remediation_history_dir=Path(getattr(args, "remediation_history_dir", DEFAULT_REMEDIATION_HISTORY_DIR)),
        limit=args.limit,
    )
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_list_remediation_plan_history_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
