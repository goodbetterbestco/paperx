from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_artifacts import (
    DEFAULT_REMEDIATION_OUTPUT_DIR,
    RemediationArtifactPaths,
    build_remediation_artifact_paths,
    write_remediation_artifact_bundle,
)
from pipeline.acquisition.remediation_reports import (
    load_remediation_report,
    resolve_remediation_report_path,
)
from pipeline.acquisition.audit import audit_acquisition_quality as audit_acquisition_quality_impl
from pipeline.corpus_layout import current_layout

REMEDIATION_PRIORITY_RANK = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}
OUTPUT_DIR = DEFAULT_REMEDIATION_OUTPUT_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the actionable acquisition remediation queue from a live audit or saved audit report."
    )
    parser.add_argument(
        "--from-report",
        help="Read remediation_queue from an existing acquisition audit JSON report instead of recomputing a live audit.",
    )
    parser.add_argument(
        "--resume-from",
        help="Resume from a prior remediation run report path or saved snapshot label such as latest or previous.",
    )
    parser.add_argument(
        "--label",
        help="Optional snapshot label for the saved remediation run. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directory for current and historical remediation run artifacts.",
    )
    parser.add_argument("--plan-label", help="Optional originating remediation plan label for reconciliation.")
    parser.add_argument("--plan-wave-id", help="Optional originating remediation wave id for reconciliation.")
    parser.add_argument(
        "--paper-id",
        action="append",
        default=[],
        help="Restrict execution to one or more paper ids. Repeat the flag to select multiple papers.",
    )
    parser.add_argument(
        "--priority",
        action="append",
        choices=tuple(REMEDIATION_PRIORITY_RANK),
        default=[],
        help="Restrict execution to one or more exact remediation priority levels. Repeat the flag to select multiple.",
    )
    parser.add_argument(
        "--min-priority",
        choices=tuple(REMEDIATION_PRIORITY_RANK),
        help="Restrict execution to queue items at or above the given remediation priority level.",
    )
    parser.add_argument("--limit", type=int, help="Only process the first N selected queue items.")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected queue commands without executing them.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed remediation command.")
    return parser.parse_args()


def _snapshot_label(value: str | None) -> str:
    if value:
        cleaned = "".join(character if character.isalnum() or character in ("-", "_") else "-" for character in value)
        cleaned = cleaned.strip("-_")
        if cleaned:
            return cleaned
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(command),
        check=False,
        capture_output=True,
        text=True,
    )


def _priority_rank(label: str | None) -> int:
    return int(REMEDIATION_PRIORITY_RANK.get(str(label or "").strip().lower(), -1))


def _select_queue_items(
    report: dict[str, Any],
    *,
    paper_ids: list[str],
    priorities: list[str],
    min_priority: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected_ids = {paper_id.strip() for paper_id in paper_ids if paper_id and paper_id.strip()}
    selected_priorities = {priority.strip() for priority in priorities if priority and priority.strip()}
    min_priority_rank = _priority_rank(min_priority) if min_priority else None
    queue = [
        dict(item)
        for item in list(report.get("remediation_queue") or [])
        if str(item.get("remediation_command") or "").strip()
    ]
    if selected_ids:
        queue = [item for item in queue if str(item.get("paper_id") or "") in selected_ids]
    if selected_priorities:
        queue = [item for item in queue if str(item.get("remediation_priority_label") or "") in selected_priorities]
    if min_priority_rank is not None:
        queue = [
            item
            for item in queue
            if _priority_rank(str(item.get("remediation_priority_label") or None)) >= min_priority_rank
        ]
    if limit is not None:
        queue = queue[: max(0, int(limit))]
    return queue


def _status_counts(results: list[dict[str, Any]], skipped_papers: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in results:
        status = str(item.get("status") or "").strip()
        if not status:
            continue
        counts[status] = counts.get(status, 0) + 1
    for item in skipped_papers:
        status = str(item.get("status") or "").strip()
        if not status:
            continue
        counts[status] = counts.get(status, 0) + 1
    return counts


def run_remediation_queue_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    audit_acquisition_quality_fn: Callable[..., dict[str, Any]] = audit_acquisition_quality_impl,
    load_report_fn: Callable[[Path], dict[str, Any]] = _load_report,
    load_resume_report_fn: Callable[..., dict[str, Any]] = load_remediation_report,
    resolve_resume_path_fn: Callable[..., Path] = resolve_remediation_report_path,
    run_command_fn: Callable[[str], Any] = _run_command,
    build_artifact_paths_fn: Callable[..., RemediationArtifactPaths] = build_remediation_artifact_paths,
    write_artifact_bundle_fn: Callable[..., dict[str, Any]] = write_remediation_artifact_bundle,
    print_fn: Callable[[str], None] = print,
) -> int:
    snapshot_label = _snapshot_label(getattr(args, "label", None))
    paths = build_artifact_paths_fn(snapshot_label, output_dir=getattr(args, "output_dir", OUTPUT_DIR))
    if args.from_report:
        report = load_report_fn(Path(args.from_report))
        source = {"kind": "report", "path": str(Path(args.from_report))}
    else:
        report = audit_acquisition_quality_fn(layout=current_layout_fn())
        source = {"kind": "live_audit"}

    queue = _select_queue_items(
        report,
        paper_ids=list(args.paper_id or []),
        priorities=list(args.priority or []),
        min_priority=args.min_priority,
        limit=args.limit,
    )
    resume_info: dict[str, Any] | None = None
    skipped_papers: list[dict[str, Any]] = []
    if getattr(args, "resume_from", None):
        resume_report = load_resume_report_fn(
            getattr(args, "resume_from"),
            history_dir=Path(getattr(args, "output_dir", OUTPUT_DIR)) / "history",
        )
        resume_path = resolve_resume_path_fn(
            getattr(args, "resume_from"),
            history_dir=Path(getattr(args, "output_dir", OUTPUT_DIR)) / "history",
        )
        succeeded_ids = {
            str(item.get("paper_id") or "").strip()
            for item in list(resume_report.get("results") or [])
            if str(item.get("status") or "").strip() == "succeeded" and str(item.get("paper_id") or "").strip()
        }
        original_queue = list(queue)
        queue = [item for item in original_queue if str(item.get("paper_id") or "").strip() not in succeeded_ids]
        skipped_papers = [
            {
                "paper_id": str(item.get("paper_id") or ""),
                "priority": str(item.get("remediation_priority_label") or ""),
                "priority_score": int(item.get("remediation_priority_score") or 0),
                "command": str(item.get("remediation_command") or ""),
                "status": "skipped_succeeded",
            }
            for item in original_queue
            if str(item.get("paper_id") or "").strip() in succeeded_ids
        ]
        resume_info = {
            "requested": str(getattr(args, "resume_from")),
            "path": str(resume_path),
            "successful_papers": sorted(succeeded_ids),
        }

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_label": snapshot_label,
        "mode": "dry_run" if args.dry_run else "execute",
        "source": source,
        "plan": {
            "label": str(getattr(args, "plan_label", None) or "").strip() or None,
            "wave_id": str(getattr(args, "plan_wave_id", None) or "").strip() or None,
        },
        "resume": resume_info,
        "requested_count": len(queue) + len(skipped_papers),
        "selected_count": len(queue),
        "skipped_count": len(skipped_papers),
        "selected_papers": [str(item.get("paper_id") or "") for item in queue],
        "selected_priorities": sorted({str(item.get("remediation_priority_label") or "") for item in queue if str(item.get("remediation_priority_label") or "").strip()}),
        "skipped_papers": skipped_papers,
        "results": [],
    }

    if args.dry_run:
        payload["results"] = [
            {
                "paper_id": str(item.get("paper_id") or ""),
                "priority": str(item.get("remediation_priority_label") or ""),
                "priority_score": int(item.get("remediation_priority_score") or 0),
                "command": str(item.get("remediation_command") or ""),
                "status": "planned",
            }
            for item in queue
        ]
        payload["status_counts"] = _status_counts(list(payload["results"]), skipped_papers)
        write_artifact_bundle_fn(payload, paths=paths)
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
                "priority": str(item.get("remediation_priority_label") or ""),
                "priority_score": int(item.get("remediation_priority_score") or 0),
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

    payload["status_counts"] = _status_counts(list(payload["results"]), skipped_papers)
    write_artifact_bundle_fn(payload, paths=paths)
    print_fn(json.dumps(payload, indent=2))
    return exit_code


def main() -> int:
    return run_remediation_queue_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
