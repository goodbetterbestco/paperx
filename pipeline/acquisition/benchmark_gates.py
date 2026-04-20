from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.acquisition.benchmark_reports import resolve_benchmark_report_path


DEFAULT_FAMILY_SOFT_GATES: tuple[dict[str, Any], ...] = (
    {
        "family": "born_digital_scholarly",
        "expected_provider": "docling",
        "min_overall_delta": -0.02,
        "require_leader": True,
    },
    {
        "family": "layout_complex",
        "expected_provider": "docling",
        "min_overall_delta": -0.03,
        "require_leader": True,
    },
    {
        "family": "scan_or_image_heavy",
        "expected_provider": "docling",
        "min_overall_delta": -0.02,
        "require_leader": True,
    },
    {
        "family": "degraded_or_garbled",
        "expected_provider": "grobid",
        "min_overall_delta": -0.03,
        "require_leader": False,
    },
    {
        "family": "math_dense",
        "expected_provider": "mathpix",
        "min_overall_delta": -0.03,
        "require_leader": True,
    },
)


def _candidate_family_leader(comparison: dict[str, Any], family: str) -> str | None:
    families = list((((comparison.get("leaders") or {}).get("candidate") or {}).get("families") or []))
    for entry in families:
        if str(entry.get("family", "") or "").strip() != family:
            continue
        overall = dict((entry.get("leaders") or {}).get("overall") or {})
        provider = str(overall.get("provider", "") or "").strip()
        return provider or None
    return None


def _family_provider_row(comparison: dict[str, Any], family: str, provider: str) -> dict[str, Any] | None:
    families = list(comparison.get("families") or [])
    for entry in families:
        if str(entry.get("family", "") or "").strip() != family:
            continue
        for row in list(entry.get("providers") or []):
            if str(row.get("provider", "") or "").strip() == provider:
                return row
    return None


def _rule_result(comparison: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    family = str(rule.get("family", "") or "").strip()
    expected_provider = str(rule.get("expected_provider", "") or "").strip()
    min_overall_delta = round(float(rule.get("min_overall_delta", 0.0) or 0.0), 3)
    require_leader = bool(rule.get("require_leader"))
    row = _family_provider_row(comparison, family, expected_provider)
    candidate_leader = _candidate_family_leader(comparison, family)
    violations: list[str] = []

    if row is None:
        violations.append("missing_family_provider_row")
        observed_overall_delta = None
    else:
        observed_overall_delta = round(float(row.get("overall_delta", 0.0) or 0.0), 3)
        if observed_overall_delta < min_overall_delta:
            violations.append("overall_delta_below_threshold")

    if require_leader and candidate_leader != expected_provider:
        violations.append("expected_leader_changed")

    return {
        "family": family,
        "expected_provider": expected_provider,
        "min_overall_delta": min_overall_delta,
        "require_leader": require_leader,
        "candidate_leader": candidate_leader,
        "observed_overall_delta": observed_overall_delta,
        "status": "fail" if violations else "pass",
        "violations": violations,
    }


def evaluate_benchmark_gates(
    base_path: str | Path,
    candidate_path: str | Path,
    *,
    family_rules: list[dict[str, Any]] | tuple[dict[str, Any], ...] = DEFAULT_FAMILY_SOFT_GATES,
) -> dict[str, Any]:
    comparison = compare_benchmark_reports(base_path, candidate_path)
    results = [_rule_result(comparison, dict(rule)) for rule in family_rules]
    violations = [result for result in results if result["violations"]]
    return {
        "status": "fail" if violations else "pass",
        "base_report_path": comparison.get("base_report_path"),
        "candidate_report_path": comparison.get("candidate_report_path"),
        "base_paper_count": int(comparison.get("base_paper_count", 0) or 0),
        "candidate_paper_count": int(comparison.get("candidate_paper_count", 0) or 0),
        "gate_count": len(results),
        "violation_count": len(violations),
        "family_rules": results,
        "violations": violations,
        "comparison": comparison,
    }


def evaluate_latest_benchmark_gates(
    *,
    history_dir: str | Path | None = None,
    base: str = "previous",
    candidate: str = "latest",
    family_rules: list[dict[str, Any]] | tuple[dict[str, Any], ...] = DEFAULT_FAMILY_SOFT_GATES,
) -> dict[str, Any]:
    resolve_kwargs = {"history_dir": history_dir} if history_dir is not None else {}
    base_path = resolve_benchmark_report_path(base, **resolve_kwargs)
    candidate_path = resolve_benchmark_report_path(candidate, **resolve_kwargs)
    return evaluate_benchmark_gates(base_path, candidate_path, family_rules=family_rules)


__all__ = [
    "DEFAULT_FAMILY_SOFT_GATES",
    "evaluate_benchmark_gates",
    "evaluate_latest_benchmark_gates",
]
