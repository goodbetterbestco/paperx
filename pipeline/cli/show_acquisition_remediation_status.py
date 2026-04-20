from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.remediation_artifacts import (
    DEFAULT_REMEDIATION_OUTPUT_DIR,
    current_remediation_output_dir,
)
from pipeline.acquisition.remediation_status import summarize_latest_remediation_status
from pipeline.output.acquisition_remediation_status_report import (
    render_acquisition_remediation_status_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show the latest acquisition remediation run status.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_REMEDIATION_OUTPUT_DIR),
        help="Optional remediation output directory. Defaults to the repo remediation artifact path.",
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown", help="Output format.")
    return parser.parse_args()


def run_show_remediation_status_cli(
    args: argparse.Namespace,
    *,
    summarize_status_fn: Callable[..., dict[str, Any]] = summarize_latest_remediation_status,
    resolve_output_dir_fn: Callable[..., Path] = current_remediation_output_dir,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_status_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = summarize_status_fn(output_dir=resolve_output_dir_fn(history_dir=Path(args.output_dir) / "history"))
    if args.format == "json":
        print_fn(json.dumps(report, indent=2))
    else:
        print_fn(render_markdown_fn(report))
    return 0


def main() -> int:
    return run_show_remediation_status_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
