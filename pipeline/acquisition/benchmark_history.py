from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_compare import DEFAULT_HISTORY_DIR


def _load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _history_reports(history_dir: str | Path) -> list[Path]:
    root = Path(history_dir)
    if not root.exists():
        return []
    return sorted(
        (path for path in root.glob("*.json") if path.is_file()),
        key=lambda path: (path.stat().st_mtime, path.name),
    )


def _provider_map(items: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    providers: dict[str, dict[str, float]] = {}
    for item in items:
        provider = str(item.get("provider", "") or "").strip()
        if not provider:
            continue
        providers[provider] = {
            "overall": round(float(item.get("avg_overall_score", item.get("overall_score", 0.0)) or 0.0), 3),
            "content": round(float(item.get("avg_content_score", item.get("content_score", 0.0)) or 0.0), 3),
            "execution": round(float(item.get("avg_execution_score", item.get("execution_score", 0.0)) or 0.0), 3),
        }
    return providers


def list_benchmark_history(history_dir: str | Path = DEFAULT_HISTORY_DIR, *, limit: int | None = None) -> dict[str, Any]:
    history_paths = _history_reports(history_dir)
    if limit is not None and limit > 0:
        history_paths = history_paths[-limit:]

    runs: list[dict[str, Any]] = []
    previous_provider_map: dict[str, dict[str, float]] = {}
    for path in history_paths:
        report = _load_report(path)
        provider_map = _provider_map(list(report.get("aggregate") or []))
        provider_rows: list[dict[str, Any]] = []
        for provider in sorted(provider_map):
            current = provider_map[provider]
            previous = previous_provider_map.get(provider, {})
            provider_rows.append(
                {
                    "provider": provider,
                    "overall": current["overall"],
                    "content": current["content"],
                    "execution": current["execution"],
                    "overall_delta_vs_previous": round(
                        current["overall"] - float(previous.get("overall", current["overall"])),
                        3,
                    ),
                }
            )

        runs.append(
            {
                "label": str(report.get("snapshot_label") or path.stem),
                "path": str(path.resolve()),
                "paper_count": int(report.get("paper_count", 0) or 0),
                "provider_count": len(provider_rows),
                "providers": provider_rows,
            }
        )
        previous_provider_map = provider_map

    return {
        "history_dir": str(Path(history_dir).resolve()),
        "run_count": len(runs),
        "runs": runs,
    }


__all__ = ["list_benchmark_history"]
