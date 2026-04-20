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


def leader_for_metric(
    items: list[dict[str, Any]],
    *,
    value_key: str,
) -> dict[str, Any] | None:
    leader: dict[str, Any] | None = None
    leader_value = float("-inf")
    leader_provider = ""
    for item in items:
        provider = str(item.get("provider", "") or "").strip()
        if not provider:
            continue
        value = float(item.get(value_key, 0.0) or 0.0)
        if value > leader_value or (value == leader_value and provider < leader_provider):
            leader = dict(item)
            leader_value = value
            leader_provider = provider
    return leader


def provider_leader_summary(
    items: list[dict[str, Any]],
    *,
    overall_key: str = "overall",
    content_key: str = "content",
    execution_key: str = "execution",
) -> dict[str, dict[str, Any] | None]:
    return {
        "overall": leader_for_metric(items, value_key=overall_key),
        "content": leader_for_metric(items, value_key=content_key),
        "execution": leader_for_metric(items, value_key=execution_key),
    }


def capability_leader_rows(
    capabilities: list[dict[str, Any]],
    *,
    value_key: str = "score",
) -> list[dict[str, Any]]:
    leaders: list[dict[str, Any]] = []
    for capability in capabilities:
        capability_name = str(capability.get("capability", "") or "").strip()
        if not capability_name:
            continue
        leader = leader_for_metric(list(capability.get("providers") or []), value_key=value_key)
        if leader is None:
            continue
        leaders.append({"capability": capability_name, "leader": leader})
    return leaders


def family_leader_rows(
    families: list[dict[str, Any]],
    family_capabilities: list[dict[str, Any]],
    *,
    overall_key: str = "overall",
    content_key: str = "content",
    execution_key: str = "execution",
    capability_value_key: str = "score",
) -> list[dict[str, Any]]:
    capability_lookup = {
        str(item.get("family", "") or "").strip(): list(item.get("capabilities") or [])
        for item in family_capabilities
        if str(item.get("family", "") or "").strip()
    }
    rows: list[dict[str, Any]] = []
    for family in families:
        family_name = str(family.get("family", "") or "").strip()
        if not family_name:
            continue
        leaders = provider_leader_summary(
            list(family.get("providers") or []),
            overall_key=overall_key,
            content_key=content_key,
            execution_key=execution_key,
        )
        leaders["capabilities"] = capability_leader_rows(
            capability_lookup.get(family_name, []),
            value_key=capability_value_key,
        )
        rows.append({"family": family_name, "leaders": leaders})
    rows.sort(key=lambda item: item["family"])
    return rows


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
    "capability_leader_rows",
    "family_capability_score_maps",
    "family_leader_rows",
    "family_provider_score_maps",
    "leader_for_metric",
    "list_history_reports",
    "load_benchmark_report",
    "provider_leader_summary",
    "provider_score_map",
    "resolve_benchmark_report_path",
]
