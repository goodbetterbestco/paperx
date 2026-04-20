from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipeline.runtime_paths import ensure_repo_tmp_dir


DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR = ensure_repo_tmp_dir() / "acquisition_remediation_plans"


@dataclass(frozen=True)
class RemediationPlanArtifactPaths:
    output_dir: Path
    history_dir: Path
    summary_json: Path
    snapshot_json: Path

    def report_paths(self) -> dict[str, str]:
        return {
            "json": str(self.summary_json),
            "snapshot_json": str(self.snapshot_json),
        }


def build_remediation_plan_artifact_paths(
    snapshot_label: str,
    *,
    output_dir: str | Path = DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
) -> RemediationPlanArtifactPaths:
    root = Path(output_dir)
    history_dir = root / "history"
    return RemediationPlanArtifactPaths(
        output_dir=root,
        history_dir=history_dir,
        summary_json=root / "summary.json",
        snapshot_json=history_dir / f"{snapshot_label}.json",
    )


def ensure_remediation_plan_artifact_dirs(paths: RemediationPlanArtifactPaths) -> None:
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.history_dir.mkdir(parents=True, exist_ok=True)


def current_remediation_plan_output_dir(*, history_dir: str | Path | None = None) -> Path:
    if history_dir is not None:
        return Path(history_dir).resolve().parent
    return DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR.resolve()


def write_remediation_plan_artifact_bundle(report: dict[str, Any], *, paths: RemediationPlanArtifactPaths) -> dict[str, Any]:
    ensure_remediation_plan_artifact_dirs(paths)
    report["report_paths"] = paths.report_paths()
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    paths.summary_json.write_text(payload, encoding="utf-8")
    paths.snapshot_json.write_text(payload, encoding="utf-8")
    return report


def load_current_remediation_plan_summary(
    *,
    output_dir: str | Path = DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR,
) -> dict[str, Any]:
    path = Path(output_dir) / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"No remediation plan summary artifact found at {path.resolve()}")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "DEFAULT_REMEDIATION_PLAN_OUTPUT_DIR",
    "RemediationPlanArtifactPaths",
    "build_remediation_plan_artifact_paths",
    "current_remediation_plan_output_dir",
    "ensure_remediation_plan_artifact_dirs",
    "load_current_remediation_plan_summary",
    "write_remediation_plan_artifact_bundle",
]
