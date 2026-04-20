from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_artifacts import DEFAULT_REMEDIATION_OUTPUT_DIR
from pipeline.acquisition.remediation_plan_artifacts import (
    DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
    load_current_remediation_plan_summary,
)
from pipeline.acquisition.remediation_plan_reports import (
    load_remediation_plan_report,
    resolve_remediation_plan_report_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a saved acquisition remediation wave by wave id.")
    parser.add_argument("wave_id", help="Wave identifier from a saved remediation plan.")
    parser.add_argument(
        "--from-plan",
        help="Saved remediation plan snapshot label or path. Defaults to the current remediation plan summary artifact.",
    )
    parser.add_argument(
        "--plan-output-dir",
        default=str(DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR),
        help="Directory for remediation plan artifacts when resolving current or historical plans.",
    )
    parser.add_argument(
        "--queue-output-dir",
        default=str(DEFAULT_REMEDIATION_OUTPUT_DIR),
        help="Directory for remediation queue run artifacts written by the queue runner.",
    )
    parser.add_argument(
        "--label",
        help="Optional remediation queue run label. Defaults to the selected wave id.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved queue command without executing it.")
    return parser.parse_args()


def _run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(command),
        check=False,
        capture_output=True,
        text=True,
    )


def _build_wave_command(wave: dict[str, Any], *, queue_output_dir: str | Path, label: str) -> str:
    tokens = shlex.split(str(wave.get("execution_command") or ""))
    if not tokens:
        return ""
    plan_label = str(wave.get("plan_label") or "").strip()
    wave_id = str(wave.get("wave_id") or "").strip()
    if "--label" not in tokens:
        tokens.extend(["--label", str(label)])
    if "--output-dir" not in tokens:
        tokens.extend(["--output-dir", str(queue_output_dir)])
    if plan_label and "--plan-label" not in tokens:
        tokens.extend(["--plan-label", plan_label])
    if wave_id and "--plan-wave-id" not in tokens:
        tokens.extend(["--plan-wave-id", wave_id])
    return " ".join(shlex.quote(token) for token in tokens)


def run_remediation_wave_cli(
    args: argparse.Namespace,
    *,
    load_current_plan_fn: Callable[..., dict[str, Any]] = load_current_remediation_plan_summary,
    load_plan_report_fn: Callable[..., dict[str, Any]] = load_remediation_plan_report,
    resolve_plan_path_fn: Callable[..., Path] = resolve_remediation_plan_report_path,
    run_command_fn: Callable[[str], Any] = _run_command,
    print_fn: Callable[[str], None] = print,
) -> int:
    plan_output_dir = Path(getattr(args, "plan_output_dir", DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR))
    history_dir = plan_output_dir / "history"
    if getattr(args, "from_plan", None):
        plan = load_plan_report_fn(getattr(args, "from_plan"), history_dir=history_dir)
        plan_path = resolve_plan_path_fn(getattr(args, "from_plan"), history_dir=history_dir)
    else:
        plan = load_current_plan_fn(output_dir=plan_output_dir)
        plan_path = plan_output_dir / "summary.json"

    wave_id = str(args.wave_id)
    wave = next((dict(item) for item in list(plan.get("waves") or []) if str(item.get("wave_id") or "") == wave_id), None)
    if wave is None:
        print_fn(
            json.dumps(
                {
                    "wave_id": wave_id,
                    "plan_path": str(plan_path),
                    "error": "wave_not_found",
                },
                indent=2,
            )
        )
        return 3

    label = str(getattr(args, "label", None) or wave_id)
    wave = {**wave, "plan_label": str(plan.get("snapshot_label") or "").strip() or None}
    command = _build_wave_command(
        wave,
        queue_output_dir=Path(getattr(args, "queue_output_dir", DEFAULT_REMEDIATION_OUTPUT_DIR)),
        label=label,
    )
    payload: dict[str, Any] = {
        "wave_id": wave_id,
        "plan_path": str(plan_path),
        "plan_label": plan.get("snapshot_label"),
        "wave_kind": wave.get("wave_kind"),
        "provider_focus": wave.get("provider_focus"),
        "paper_ids": list(wave.get("paper_ids") or []),
        "queue_label": label,
        "queue_output_dir": str(Path(getattr(args, "queue_output_dir", DEFAULT_REMEDIATION_OUTPUT_DIR))),
        "command": command,
    }
    if args.dry_run:
        payload["status"] = "planned"
        print_fn(json.dumps(payload, indent=2))
        return 0

    completed = run_command_fn(command)
    payload["returncode"] = int(getattr(completed, "returncode", 1))
    payload["stdout"] = str(getattr(completed, "stdout", "") or "")
    payload["stderr"] = str(getattr(completed, "stderr", "") or "")
    payload["status"] = "succeeded" if int(payload["returncode"]) == 0 else "failed"
    print_fn(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "succeeded" else 1


def main() -> int:
    return run_remediation_wave_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
