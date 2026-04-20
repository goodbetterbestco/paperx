from __future__ import annotations

from pathlib import Path
import re
import shlex
from typing import Any

from pipeline.acquisition.remediation_artifacts import current_remediation_output_dir
from pipeline.acquisition.remediation_status import summarize_latest_remediation_status
from pipeline.acquisition.remediation_trend import summarize_remediation_trend

REMEDIATION_PRIORITY_RANK = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}


def _priority_rank(label: str | None) -> int:
    return int(REMEDIATION_PRIORITY_RANK.get(str(label or "").strip().lower(), -1))


def _target_providers(queue_item: dict[str, Any]) -> list[str]:
    providers = sorted(
        {
            str(item.get("target_provider") or "").strip()
            for item in list(queue_item.get("follow_up_actions") or [])
            if str(item.get("target_provider") or "").strip()
        }
    )
    return providers


def _provider_focus(queue_item: dict[str, Any]) -> str:
    providers = _target_providers(queue_item)
    if not providers:
        return "manual"
    if len(providers) == 1:
        return providers[0]
    return "mixed"


def _wave_kind(*, provider_focus: str, planning_tags: list[str]) -> str:
    if any(tag in {"still_failing", "introduced_failure", "latest_failure"} for tag in planning_tags):
        return "recovery"
    if provider_focus == "manual":
        return "manual"
    return "remediation"


def _chunk(items: list[dict[str, Any]], *, size: int) -> list[list[dict[str, Any]]]:
    if size <= 0:
        return [items]
    return [items[index : index + size] for index in range(0, len(items), size)]


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return cleaned.strip("-") or "wave"


def _wave_command(
    paper_ids: list[str],
    *,
    from_report_path: str | None,
    fail_fast: bool,
) -> str:
    parts = ["python3", "-m", "pipeline.cli.run_acquisition_remediation_queue"]
    if from_report_path:
        parts.extend(["--from-report", from_report_path])
    if fail_fast:
        parts.append("--fail-fast")
    for paper_id in paper_ids:
        parts.extend(["--paper-id", paper_id])
    return " ".join(shlex.quote(part) for part in parts)


def _latest_failure_context(*, history_dir: str | Path | None) -> dict[str, set[str]]:
    output_dir = current_remediation_output_dir(history_dir=history_dir) if history_dir is not None else current_remediation_output_dir()
    latest_failures: set[str] = set()
    still_failing: set[str] = set()
    introduced_failures: set[str] = set()
    try:
        status = summarize_latest_remediation_status(output_dir=output_dir)
        latest_failures = {
            str(item.get("paper_id") or "").strip()
            for item in list(status.get("failures") or [])
            if str(item.get("paper_id") or "").strip()
        }
    except FileNotFoundError:
        pass
    try:
        trend = summarize_remediation_trend(history_dir=history_dir)
        still_failing = {
            str(item.get("paper_id") or "").strip()
            for item in list(trend.get("still_failing") or [])
            if str(item.get("paper_id") or "").strip()
        }
        introduced_failures = {
            str(item.get("paper_id") or "").strip()
            for item in list(trend.get("introduced_failures") or [])
            if str(item.get("paper_id") or "").strip()
        }
    except FileNotFoundError:
        pass
    return {
        "latest_failures": latest_failures,
        "still_failing": still_failing,
        "introduced_failures": introduced_failures,
    }


def plan_remediation_waves(
    report: dict[str, Any],
    *,
    from_report_path: str | None = None,
    history_dir: str | Path | None = None,
    max_wave_size: int = 5,
) -> dict[str, Any]:
    failure_context = _latest_failure_context(history_dir=history_dir)
    latest_failures = set(failure_context["latest_failures"])
    still_failing = set(failure_context["still_failing"])
    introduced_failures = set(failure_context["introduced_failures"])

    paper_rows: list[dict[str, Any]] = []
    for queue_item in list(report.get("remediation_queue") or []):
        paper_id = str(queue_item.get("paper_id") or "").strip()
        if not paper_id:
            continue
        provider_focus = _provider_focus(queue_item)
        target_providers = _target_providers(queue_item)
        planning_tags = list(queue_item.get("remediation_priority_reasons") or [])
        if paper_id in still_failing:
            planning_tags.append("still_failing")
        elif paper_id in introduced_failures:
            planning_tags.append("introduced_failure")
        elif paper_id in latest_failures:
            planning_tags.append("latest_failure")
        if provider_focus == "manual":
            planning_tags.append("manual_provider")
        elif provider_focus == "mixed":
            planning_tags.append("multi_provider")
        paper_rows.append(
            {
                "paper_id": paper_id,
                "priority_label": str(queue_item.get("remediation_priority_label") or ""),
                "priority_score": int(queue_item.get("remediation_priority_score") or 0),
                "provider_focus": provider_focus,
                "target_providers": target_providers,
                "planning_tags": sorted(set(planning_tags)),
                "remediation_command": str(queue_item.get("remediation_command") or ""),
            }
        )

    paper_rows.sort(
        key=lambda item: (
            -_priority_rank(item["priority_label"]),
            -int(item["priority_score"]),
            item["provider_focus"],
            item["paper_id"],
        )
    )
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in paper_rows:
        wave_kind = _wave_kind(provider_focus=row["provider_focus"], planning_tags=row["planning_tags"])
        key = (wave_kind, row["priority_label"], row["provider_focus"])
        grouped.setdefault(key, []).append(row)

    ordered_keys = sorted(
        grouped,
        key=lambda key: (
            0 if key[0] == "recovery" else 1 if key[0] == "remediation" else 2,
            -_priority_rank(key[1]),
            key[2],
        ),
    )

    waves: list[dict[str, Any]] = []
    for wave_kind, priority_label, provider_focus in ordered_keys:
        for index, chunk in enumerate(_chunk(grouped[(wave_kind, priority_label, provider_focus)], size=max_wave_size), start=1):
            paper_ids = [str(item["paper_id"]) for item in chunk]
            selected_priorities = sorted({str(item["priority_label"]) for item in chunk if str(item["priority_label"]).strip()}, key=lambda value: (-_priority_rank(value), value))
            target_providers = sorted({provider for item in chunk for provider in list(item.get("target_providers") or [])})
            execution_command = _wave_command(
                paper_ids,
                from_report_path=from_report_path,
                fail_fast=wave_kind == "recovery",
            )
            waves.append(
                {
                    "wave_id": f"{_slug(wave_kind)}-{_slug(priority_label)}-{_slug(provider_focus)}-{index}",
                    "wave_kind": wave_kind,
                    "priority_label": priority_label,
                    "priority_rank": _priority_rank(priority_label),
                    "provider_focus": provider_focus,
                    "paper_count": len(chunk),
                    "paper_ids": paper_ids,
                    "selected_priorities": selected_priorities,
                    "target_providers": target_providers,
                    "planning_tags": sorted({tag for item in chunk for tag in list(item.get("planning_tags") or [])}),
                    "fail_fast_recommended": wave_kind == "recovery",
                    "execution_command": execution_command,
                    "papers": chunk,
                }
            )

    wave_kind_counts: dict[str, int] = {}
    provider_focus_counts: dict[str, int] = {}
    for wave in waves:
        wave_kind_counts[wave["wave_kind"]] = wave_kind_counts.get(wave["wave_kind"], 0) + 1
        provider_focus_counts[wave["provider_focus"]] = provider_focus_counts.get(wave["provider_focus"], 0) + 1

    return {
        "source": {
            "kind": "report" if from_report_path else "live_audit",
            "path": from_report_path,
        },
        "history_dir": str(Path(history_dir).resolve()) if history_dir is not None else None,
        "queue_count": len(paper_rows),
        "wave_count": len(waves),
        "max_wave_size": max_wave_size,
        "wave_kind_counts": wave_kind_counts,
        "provider_focus_counts": provider_focus_counts,
        "context": {
            "latest_failures": sorted(latest_failures),
            "still_failing": sorted(still_failing),
            "introduced_failures": sorted(introduced_failures),
        },
        "waves": waves,
    }


__all__ = ["plan_remediation_waves"]
