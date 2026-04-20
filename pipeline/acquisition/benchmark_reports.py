from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.runtime_paths import ensure_repo_tmp_dir


DEFAULT_HISTORY_DIR = ensure_repo_tmp_dir() / "acquisition_benchmark" / "history"


def load_benchmark_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def list_history_reports(history_dir: str | Path = DEFAULT_HISTORY_DIR) -> list[Path]:
    root = Path(history_dir)
    if not root.exists():
        return []
    return sorted(
        (path for path in root.glob("*.json") if path.is_file()),
        key=lambda path: (path.stat().st_mtime, path.name),
    )


def resolve_benchmark_report_path(path_or_label: str | Path, *, history_dir: str | Path = DEFAULT_HISTORY_DIR) -> Path:
    candidate = Path(path_or_label)
    if candidate.exists():
        return candidate.resolve()

    value = str(path_or_label).strip()
    reports = list_history_reports(history_dir)
    if value == "latest":
        if not reports:
            raise FileNotFoundError(f"No benchmark history reports found under {Path(history_dir).resolve()}")
        return reports[-1].resolve()
    if value == "previous":
        if len(reports) < 2:
            raise FileNotFoundError(
                f"Need at least two benchmark history reports under {Path(history_dir).resolve()} for 'previous'"
            )
        return reports[-2].resolve()

    if value:
        label_candidate = Path(history_dir) / f"{value.removesuffix('.json')}.json"
        if label_candidate.exists():
            return label_candidate.resolve()

    raise FileNotFoundError(
        f"Could not resolve benchmark report '{path_or_label}' as a path, snapshot label, or latest/previous alias"
    )


def provider_score_map(items: list[dict[str, Any]], *, round_values: bool = False) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for item in items:
        provider = str(item.get("provider", "") or "").strip()
        if not provider:
            continue
        row = {
            "overall": float(item.get("avg_overall_score", item.get("overall_score", 0.0)) or 0.0),
            "content": float(item.get("avg_content_score", item.get("content_score", 0.0)) or 0.0),
            "execution": float(item.get("avg_execution_score", item.get("execution_score", 0.0)) or 0.0),
        }
        if round_values:
            row = {key: round(value, 3) for key, value in row.items()}
        scores[provider] = row
    return scores


def capability_score_map(items: list[dict[str, Any]], *, round_values: bool = False) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for item in items:
        provider = str(item.get("provider", "") or "").strip()
        if not provider:
            continue
        row = {"score": float(item.get("avg_score", item.get("score", 0.0)) or 0.0)}
        if round_values:
            row = {key: round(value, 3) for key, value in row.items()}
        scores[provider] = row
    return scores


def aggregate_provider_score_map(report: dict[str, Any], *, round_values: bool = False) -> dict[str, dict[str, float]]:
    return provider_score_map(list(report.get("aggregate") or []), round_values=round_values)


def family_provider_score_maps(report: dict[str, Any], *, round_values: bool = False) -> dict[str, dict[str, dict[str, float]]]:
    return {
        str(item.get("family", "") or ""): provider_score_map(list(item.get("providers") or []), round_values=round_values)
        for item in list(report.get("families") or [])
    }


def benchmark_capability_score_maps(
    report: dict[str, Any],
    *,
    round_values: bool = False,
) -> dict[str, dict[str, dict[str, float]]]:
    return {
        str(item.get("capability", "") or ""): capability_score_map(
            list(item.get("providers") or []),
            round_values=round_values,
        )
        for item in list(report.get("capabilities") or [])
        if str(item.get("capability", "") or "").strip()
    }


def family_capability_score_maps(
    report: dict[str, Any],
    *,
    round_values: bool = False,
) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    family_maps: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for item in list(report.get("family_capabilities") or []):
        family = str(item.get("family", "") or "").strip()
        if not family:
            continue
        family_maps[family] = {
            str(capability.get("capability", "") or ""): capability_score_map(
                list(capability.get("providers") or []),
                round_values=round_values,
            )
            for capability in list(item.get("capabilities") or [])
            if str(capability.get("capability", "") or "").strip()
        }
    return family_maps


def benchmark_report_label(report: dict[str, Any], *, fallback_path: str | Path | None = None) -> str:
    label = str(report.get("snapshot_label", "") or "").strip()
    if label:
        return label
    if fallback_path is not None:
        return Path(fallback_path).stem
    return "unknown"


__all__ = [
    "DEFAULT_HISTORY_DIR",
    "aggregate_provider_score_map",
    "benchmark_report_label",
    "benchmark_capability_score_maps",
    "capability_score_map",
    "family_capability_score_maps",
    "family_provider_score_maps",
    "list_history_reports",
    "load_benchmark_report",
    "provider_score_map",
    "resolve_benchmark_report_path",
]
