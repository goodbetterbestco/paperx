from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipeline.runtime_paths import ensure_repo_tmp_dir


DEFAULT_BENCHMARK_OUTPUT_DIR = ensure_repo_tmp_dir() / "acquisition_benchmark"


@dataclass(frozen=True)
class BenchmarkArtifactPaths:
    output_dir: Path
    history_dir: Path
    summary_json: Path
    summary_markdown: Path
    status_json: Path
    status_markdown: Path
    dashboard_json: Path
    dashboard_markdown: Path
    snapshot_json: Path
    snapshot_markdown: Path

    def report_paths(self) -> dict[str, str]:
        return {
            "json": str(self.summary_json),
            "markdown": str(self.summary_markdown),
            "status_json": str(self.status_json),
            "status_markdown": str(self.status_markdown),
            "snapshot_json": str(self.snapshot_json),
            "snapshot_markdown": str(self.snapshot_markdown),
            "dashboard_json": str(self.dashboard_json),
            "dashboard_markdown": str(self.dashboard_markdown),
        }


def build_benchmark_artifact_paths(
    snapshot_label: str,
    *,
    output_dir: str | Path = DEFAULT_BENCHMARK_OUTPUT_DIR,
) -> BenchmarkArtifactPaths:
    root = Path(output_dir)
    history_dir = root / "history"
    return BenchmarkArtifactPaths(
        output_dir=root,
        history_dir=history_dir,
        summary_json=root / "summary.json",
        summary_markdown=root / "summary.md",
        status_json=root / "status.json",
        status_markdown=root / "status.md",
        dashboard_json=root / "dashboard.json",
        dashboard_markdown=root / "dashboard.md",
        snapshot_json=history_dir / f"{snapshot_label}.json",
        snapshot_markdown=history_dir / f"{snapshot_label}.md",
    )


def current_benchmark_output_dir(*, history_dir: str | Path | None = None) -> Path:
    if history_dir is not None:
        return Path(history_dir).resolve().parent
    return DEFAULT_BENCHMARK_OUTPUT_DIR.resolve()


def ensure_benchmark_artifact_dirs(paths: BenchmarkArtifactPaths) -> None:
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.history_dir.mkdir(parents=True, exist_ok=True)


def write_benchmark_artifact_bundle(
    report: dict[str, Any],
    status: dict[str, Any],
    dashboard: dict[str, Any],
    *,
    paths: BenchmarkArtifactPaths,
    benchmark_markdown: str,
    status_markdown: str,
    dashboard_markdown: str,
) -> dict[str, Any]:
    ensure_benchmark_artifact_dirs(paths)
    report["report_paths"] = paths.report_paths()
    paths.summary_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.summary_markdown.write_text(benchmark_markdown, encoding="utf-8")
    paths.status_json.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.status_markdown.write_text(status_markdown, encoding="utf-8")
    paths.snapshot_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.snapshot_markdown.write_text(benchmark_markdown, encoding="utf-8")
    paths.dashboard_json.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.dashboard_markdown.write_text(dashboard_markdown, encoding="utf-8")
    return report


def load_current_benchmark_dashboard(*, output_dir: str | Path = DEFAULT_BENCHMARK_OUTPUT_DIR) -> dict[str, Any]:
    path = Path(output_dir) / "dashboard.json"
    if not path.exists():
        raise FileNotFoundError(f"No benchmark dashboard artifact found at {path.resolve()}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_current_benchmark_status(*, output_dir: str | Path = DEFAULT_BENCHMARK_OUTPUT_DIR) -> dict[str, Any]:
    path = Path(output_dir) / "status.json"
    if not path.exists():
        raise FileNotFoundError(f"No benchmark status artifact found at {path.resolve()}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_current_benchmark_summary(*, output_dir: str | Path = DEFAULT_BENCHMARK_OUTPUT_DIR) -> dict[str, Any]:
    path = Path(output_dir) / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"No benchmark summary artifact found at {path.resolve()}")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "BenchmarkArtifactPaths",
    "DEFAULT_BENCHMARK_OUTPUT_DIR",
    "build_benchmark_artifact_paths",
    "current_benchmark_output_dir",
    "ensure_benchmark_artifact_dirs",
    "load_current_benchmark_dashboard",
    "load_current_benchmark_status",
    "load_current_benchmark_summary",
    "write_benchmark_artifact_bundle",
]
