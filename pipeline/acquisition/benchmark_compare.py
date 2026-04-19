from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _provider_scores(items: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for item in items:
        provider = str(item.get("provider", "") or "").strip()
        if not provider:
            continue
        scores[provider] = {
            "overall": float(item.get("avg_overall_score", item.get("overall_score", 0.0)) or 0.0),
            "content": float(item.get("avg_content_score", item.get("content_score", 0.0)) or 0.0),
            "execution": float(item.get("avg_execution_score", item.get("execution_score", 0.0)) or 0.0),
        }
    return scores


def _delta_table(
    base_scores: dict[str, dict[str, float]],
    candidate_scores: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    providers = sorted(set(base_scores) | set(candidate_scores))
    rows: list[dict[str, Any]] = []
    for provider in providers:
        base = base_scores.get(provider, {})
        candidate = candidate_scores.get(provider, {})
        rows.append(
            {
                "provider": provider,
                "base_overall": round(float(base.get("overall", 0.0)), 3),
                "candidate_overall": round(float(candidate.get("overall", 0.0)), 3),
                "overall_delta": round(float(candidate.get("overall", 0.0)) - float(base.get("overall", 0.0)), 3),
                "content_delta": round(float(candidate.get("content", 0.0)) - float(base.get("content", 0.0)), 3),
                "execution_delta": round(float(candidate.get("execution", 0.0)) - float(base.get("execution", 0.0)), 3),
            }
        )
    rows.sort(key=lambda item: (-float(item["overall_delta"]), item["provider"]))
    return rows


def compare_benchmark_reports(base_path: str | Path, candidate_path: str | Path) -> dict[str, Any]:
    base_report = _load_report(base_path)
    candidate_report = _load_report(candidate_path)
    family_names = sorted(
        {
            str(item.get("family", "") or "").strip()
            for item in list(base_report.get("families") or []) + list(candidate_report.get("families") or [])
            if str(item.get("family", "") or "").strip()
        }
    )

    base_family_map = {
        str(item.get("family", "") or ""): _provider_scores(list(item.get("providers") or []))
        for item in list(base_report.get("families") or [])
    }
    candidate_family_map = {
        str(item.get("family", "") or ""): _provider_scores(list(item.get("providers") or []))
        for item in list(candidate_report.get("families") or [])
    }

    family_deltas = [
        {
            "family": family,
            "providers": _delta_table(base_family_map.get(family, {}), candidate_family_map.get(family, {})),
        }
        for family in family_names
    ]
    return {
        "base_report_path": str(Path(base_path).resolve()),
        "candidate_report_path": str(Path(candidate_path).resolve()),
        "base_paper_count": int(base_report.get("paper_count", 0) or 0),
        "candidate_paper_count": int(candidate_report.get("paper_count", 0) or 0),
        "aggregate": _delta_table(
            _provider_scores(list(base_report.get("aggregate") or [])),
            _provider_scores(list(candidate_report.get("aggregate") or [])),
        ),
        "families": family_deltas,
    }


__all__ = ["compare_benchmark_reports"]
