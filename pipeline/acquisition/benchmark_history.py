from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_reports import (
    DEFAULT_HISTORY_DIR,
    aggregate_provider_score_map,
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
    for path in history_paths:
        report = load_benchmark_report(path)
        provider_map = aggregate_provider_score_map(report, round_values=True)
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
                "label": benchmark_report_label(report, fallback_path=path),
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
