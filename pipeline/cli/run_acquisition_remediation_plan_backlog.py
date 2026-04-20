from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.remediation_plan_artifacts import DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR
from pipeline.acquisition.remediation_plan_backlog import select_remediation_plan_waves
from pipeline.acquisition.remediation_plan_status import summarize_remediation_plan_status
from pipeline.acquisition.remediation_reports import DEFAULT_REMEDIATION_HISTORY_DIR
from pipeline.acquisition.remediation_artifacts import DEFAULT_REMEDIATION_OUTPUT_DIR
from pipeline.cli.run_acquisition_remediation_wave import run_remediation_wave_cli
from pipeline.output.acquisition_remediation_plan_backlog_report import (
    render_acquisition_remediation_plan_backlog_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the actionable backlog from a saved acquisition remediation plan.")
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
    parser.add_argument(
        "--queue-output-dir",
        default=str(DEFAULT_REMEDIATION_OUTPUT_DIR),
        help="Directory for remediation queue run artifacts.",
    )
    parser.add_argument(
        "--status",
        action="append",
        choices=("pending", "planned_only", "failed", "succeeded"),
        default=[],
        help="Wave execution status to include. Repeat the flag to select multiple statuses.",
    )
    parser.add_argument("--limit", type=int, help="Only include the first N selected waves.")
    parser.add_argument("--label-prefix", help="Optional prefix for emitted queue labels.")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected backlog waves without executing them.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed wave execution.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    return parser.parse_args()


def _wave_command(
    wave: dict[str, Any],
    *,
    from_plan: str | None,
    plan_output_dir: Path,
    queue_output_dir: Path,
    label_prefix: str | None,
) -> str:
    wave_id = str(wave.get("wave_id") or "")
    parts = ["python3", "-m", "pipeline.cli.run_acquisition_remediation_wave", wave_id]
    if from_plan:
        parts.extend(["--from-plan", from_plan])
    parts.extend(["--plan-output-dir", str(plan_output_dir)])
    parts.extend(["--queue-output-dir", str(queue_output_dir)])
    if label_prefix:
        parts.extend(["--label", f"{label_prefix}-{wave_id}"])
    return " ".join(parts)


def run_remediation_plan_backlog_cli(
    args: argparse.Namespace,
    *,
    summarize_status_fn: Callable[..., dict[str, Any]] = summarize_remediation_plan_status,
    select_waves_fn: Callable[..., dict[str, Any]] = select_remediation_plan_waves,
    run_wave_fn: Callable[..., int] = run_remediation_wave_cli,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_remediation_plan_backlog_markdown,
    print_fn: Callable[[str], None] = print,
) -> int:
    plan_output_dir = Path(getattr(args, "plan_output_dir", DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR))
    remediation_history_dir = Path(getattr(args, "remediation_history_dir", DEFAULT_REMEDIATION_HISTORY_DIR))
    queue_output_dir = Path(getattr(args, "queue_output_dir", DEFAULT_REMEDIATION_OUTPUT_DIR))
    status_report = summarize_status_fn(
        from_plan=getattr(args, "from_plan", None),
        plan_output_dir=plan_output_dir,
        remediation_history_dir=remediation_history_dir,
    )
    selection = select_waves_fn(
        status_report,
        statuses=list(getattr(args, "status", []) or []),
        limit=getattr(args, "limit", None),
    )
    waves: list[dict[str, Any]] = []
    for wave in list(selection.get("waves") or []):
        queue_label = None
        if getattr(args, "label_prefix", None):
            queue_label = f"{args.label_prefix}-{wave.get('wave_id')}"
        waves.append(
            {
                **wave,
                "queue_label": queue_label or str(wave.get("wave_id") or ""),
                "command": _wave_command(
                    wave,
                    from_plan=getattr(args, "from_plan", None),
                    plan_output_dir=plan_output_dir,
                    queue_output_dir=queue_output_dir,
                    label_prefix=getattr(args, "label_prefix", None),
                ),
            }
        )

    payload: dict[str, Any] = {
        "plan_label": str((selection.get("plan") or {}).get("label") or ""),
        "mode": "dry_run" if getattr(args, "dry_run", False) else "execute",
        "selected_statuses": list(selection.get("selected_statuses") or []),
        "selected_count": len(waves),
        "waves": waves,
        "results": [],
    }
    if getattr(args, "dry_run", False):
        if args.format == "json":
            print_fn(json.dumps(payload, indent=2))
        else:
            print_fn(render_markdown_fn(payload))
        return 0

    exit_code = 0
    for wave in waves:
        printed: list[str] = []
        run_exit_code = run_wave_fn(
            argparse.Namespace(
                wave_id=wave["wave_id"],
                from_plan=getattr(args, "from_plan", None),
                plan_output_dir=str(plan_output_dir),
                queue_output_dir=str(queue_output_dir),
                label=wave["queue_label"] if getattr(args, "label_prefix", None) else None,
                dry_run=False,
            ),
            print_fn=printed.append,
        )
        result = json.loads(printed[0]) if printed else {}
        result.setdefault("wave_id", wave["wave_id"])
        result.setdefault("queue_label", wave["queue_label"])
        payload["results"].append(result)
        if run_exit_code != 0:
            exit_code = 1
            if getattr(args, "fail_fast", False):
                break

    if args.format == "json":
        print_fn(json.dumps(payload, indent=2))
    else:
        print_fn(render_markdown_fn(payload))
    return exit_code


def main() -> int:
    return run_remediation_plan_backlog_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
