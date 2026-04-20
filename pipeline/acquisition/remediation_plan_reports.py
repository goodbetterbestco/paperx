from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.acquisition.remediation_plan_artifacts import DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR


DEFAULT_REMEDIATION_PLAN_HISTORY_DIR = DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR / "history"


def list_remediation_plan_history_reports(
    history_dir: str | Path = DEFAULT_REMEDIATION_PLAN_HISTORY_DIR,
) -> list[Path]:
    root = Path(history_dir)
    if not root.exists():
        return []
    return sorted((path.resolve() for path in root.glob("*.json") if path.is_file()), key=lambda path: path.name)


def resolve_remediation_plan_report_path(
    path_or_label: str | Path,
    *,
    history_dir: str | Path = DEFAULT_REMEDIATION_PLAN_HISTORY_DIR,
) -> Path:
    candidate = Path(path_or_label)
    if candidate.exists():
        return candidate.resolve()

    value = str(path_or_label).strip()
    reports = list_remediation_plan_history_reports(history_dir)
    if value == "latest":
        if not reports:
            raise FileNotFoundError(f"No remediation plan history reports found under {Path(history_dir).resolve()}")
        return reports[-1]
    if value == "previous":
        if len(reports) < 2:
            raise FileNotFoundError(
                f"Need at least two remediation plan history reports under {Path(history_dir).resolve()} for 'previous'"
            )
        return reports[-2]

    label_candidate = Path(history_dir) / f"{value.removesuffix('.json')}.json"
    if label_candidate.exists():
        return label_candidate.resolve()
    raise FileNotFoundError(
        f"Could not resolve remediation plan report '{path_or_label}' under {Path(history_dir).resolve()}"
    )


def load_remediation_plan_report(
    path_or_label: str | Path,
    *,
    history_dir: str | Path = DEFAULT_REMEDIATION_PLAN_HISTORY_DIR,
) -> dict[str, Any]:
    path = resolve_remediation_plan_report_path(path_or_label, history_dir=history_dir)
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "DEFAULT_REMEDIATION_PLAN_HISTORY_DIR",
    "list_remediation_plan_history_reports",
    "load_remediation_plan_report",
    "resolve_remediation_plan_report_path",
]
