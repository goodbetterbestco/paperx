from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_reports import (
    DEFAULT_HISTORY_DIR,
    aggregate_provider_score_map,
    benchmark_capability_score_maps,
    benchmark_report_label,
    list_history_reports,
    load_benchmark_report,
)


def list_benchmark_history(history_dir: str | Path = DEFAULT_HISTORY_DIR, *, limit: int | None = None) -> dict[str, Any]:
    history_paths = list_history_reports(history_dir)
    if limit is not None and limit > 0:
        history_paths = history_paths[-limit:]

    runs: list[dict[str, Any]] = []
    previous_provider_map: dict[str, dict[str, float]] = {}
    previous_capability_map: dict[str, dict[str, dict[str, float]]] = {}
    for path in history_paths:
        report = load_benchmark_report(path)
        provider_map = aggregate_provider_score_map(report, round_values=True)
        capability_map = benchmark_capability_score_maps(report, round_values=True)
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
        capability_rows: list[dict[str, Any]] = []
        for capability in sorted(capability_map):
            provider_rows_for_capability: list[dict[str, Any]] = []
            for provider in sorted(capability_map[capability]):
                current = capability_map[capability][provider]
                previous = previous_capability_map.get(capability, {}).get(provider, {})
                provider_rows_for_capability.append(
                    {
                        "provider": provider,
                        "score": current["score"],
                        "score_delta_vs_previous": round(
                            current["score"] - float(previous.get("score", current["score"])),
                            3,
                        ),
                    }
                )
            capability_rows.append(
                {
                    "capability": capability,
                    "provider_count": len(provider_rows_for_capability),
                    "providers": provider_rows_for_capability,
                }
            )

        runs.append(
            {
                "label": benchmark_report_label(report, fallback_path=path),
                "path": str(path.resolve()),
                "paper_count": int(report.get("paper_count", 0) or 0),
                "provider_count": len(provider_rows),
                "providers": provider_rows,
                "capabilities": capability_rows,
            }
        )
        previous_provider_map = provider_map
        previous_capability_map = capability_map

    return {
        "history_dir": str(Path(history_dir).resolve()),
        "run_count": len(runs),
        "runs": runs,
    }


__all__ = ["list_benchmark_history"]
