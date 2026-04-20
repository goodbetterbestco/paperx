from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.audit import audit_acquisition_quality as audit_acquisition_quality_impl
from pipeline.acquisition.remediation_plan import plan_remediation_waves
from pipeline.corpus_layout import current_layout
from pipeline.output.acquisition_remediation_plan_report import render_acquisition_remediation_plan_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan acquisition remediation waves from the actionable audit queue.")
    parser.add_argument(
        "--from-report",
        help="Read remediation_queue from an existing acquisition audit JSON report instead of recomputing a live audit.",
    )
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Optional remediation history directory used to identify recovery waves.",
    )
    parser.add_argument("--max-wave-size", type=int, default=5, help="Maximum papers to include in each planned wave.")
    parser.add_argument("--format", choices=("json", "markdown", "commands"), default="markdown", help="Output format.")
    return parser.parse_args()


def _load_report(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def run_plan_remediation_waves_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    audit_acquisition_quality_fn: Callable[..., dict[str, Any]] = audit_acquisition_quality_impl,
    load_report_fn: Callable[[str], dict[str, Any]] = _load_report,
    plan_waves_fn: Callable[..., dict[str, Any]] = plan_remediation_waves,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_plan_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    from_report_path = str(args.from_report) if getattr(args, "from_report", None) else None
    if from_report_path:
        report = load_report_fn(from_report_path)
    else:
        report = audit_acquisition_quality_fn(layout=current_layout_fn())
    plan = plan_waves_fn(
        report,
        from_report_path=from_report_path,
        history_dir=args.history_dir,
        max_wave_size=max(1, int(args.max_wave_size)),
    )
    if args.format == "json":
        print_fn(json.dumps(plan, indent=2))
    elif args.format == "commands":
        print_fn("\n".join(str(item.get("execution_command") or "") for item in list(plan.get("waves") or [])))
    else:
        print_fn(render_markdown_fn(plan))
    return 0


def main() -> int:
    return run_plan_remediation_waves_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
