from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pipeline.acquisition.audit import audit_acquisition_quality as audit_acquisition_quality_impl
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the actionable acquisition remediation queue from a live audit or saved audit report."
    )
    parser.add_argument(
        "--from-report",
        help="Read remediation_queue from an existing acquisition audit JSON report instead of recomputing a live audit.",
    )
    parser.add_argument(
        "--paper-id",
        action="append",
        default=[],
        help="Restrict execution to one or more paper ids. Repeat the flag to select multiple papers.",
    )
    parser.add_argument("--limit", type=int, help="Only process the first N selected queue items.")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected queue commands without executing them.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed remediation command.")
    return parser.parse_args()


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(command),
        check=False,
        capture_output=True,
        text=True,
    )


def _select_queue_items(report: dict[str, Any], *, paper_ids: list[str], limit: int | None) -> list[dict[str, Any]]:
    selected_ids = {paper_id.strip() for paper_id in paper_ids if paper_id and paper_id.strip()}
    queue = [
        dict(item)
        for item in list(report.get("remediation_queue") or [])
        if str(item.get("remediation_command") or "").strip()
    ]
    if selected_ids:
        queue = [item for item in queue if str(item.get("paper_id") or "") in selected_ids]
    if limit is not None:
        queue = queue[: max(0, int(limit))]
    return queue


def run_remediation_queue_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    audit_acquisition_quality_fn: Callable[..., dict[str, Any]] = audit_acquisition_quality_impl,
    load_report_fn: Callable[[Path], dict[str, Any]] = _load_report,
    run_command_fn: Callable[[str], Any] = _run_command,
    print_fn: Callable[[str], None] = print,
) -> int:
    if args.from_report:
        report = load_report_fn(Path(args.from_report))
        source = {"kind": "report", "path": str(Path(args.from_report))}
    else:
        report = audit_acquisition_quality_fn(layout=current_layout_fn())
        source = {"kind": "live_audit"}

    queue = _select_queue_items(
        report,
        paper_ids=list(args.paper_id or []),
        limit=args.limit,
    )
    payload: dict[str, Any] = {
        "mode": "dry_run" if args.dry_run else "execute",
        "source": source,
        "selected_count": len(queue),
        "selected_papers": [str(item.get("paper_id") or "") for item in queue],
        "results": [],
    }

    if args.dry_run:
        payload["results"] = [
            {
                "paper_id": str(item.get("paper_id") or ""),
                "command": str(item.get("remediation_command") or ""),
                "status": "planned",
            }
            for item in queue
        ]
        print_fn(json.dumps(payload, indent=2))
        return 0

    exit_code = 0
    for item in queue:
        command = str(item.get("remediation_command") or "").strip()
        completed = run_command_fn(command)
        returncode = int(getattr(completed, "returncode", 1))
        ok = returncode == 0
        payload["results"].append(
            {
                "paper_id": str(item.get("paper_id") or ""),
                "command": command,
                "status": "succeeded" if ok else "failed",
                "returncode": returncode,
                "stdout": str(getattr(completed, "stdout", "") or ""),
                "stderr": str(getattr(completed, "stderr", "") or ""),
            }
        )
        if not ok:
            exit_code = 1
            if args.fail_fast:
                break

    print_fn(json.dumps(payload, indent=2))
    return exit_code


def main() -> int:
    return run_remediation_queue_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
