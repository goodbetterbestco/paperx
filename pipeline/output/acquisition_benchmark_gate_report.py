from __future__ import annotations

from typing import Any


def render_acquisition_benchmark_gate_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Acquisition Benchmark Gates",
        "",
        f"- Base report: `{report.get('base_report_path')}`",
        f"- Candidate report: `{report.get('candidate_report_path')}`",
        f"- Base paper count: `{report.get('base_paper_count', 0)}`",
        f"- Candidate paper count: `{report.get('candidate_paper_count', 0)}`",
        f"- Gate status: `{report.get('status', 'unknown')}`",
        f"- Checked families: `{report.get('gate_count', 0)}`",
        f"- Violations: `{report.get('violation_count', 0)}`",
        "",
        "## Family Gates",
        "",
    ]
    for rule in list(report.get("family_rules") or []):
        observed = rule.get("observed_overall_delta")
        observed_label = "missing" if observed is None else str(observed)
        lines.append(
            f"- family `{rule['family']}`: provider `{rule['expected_provider']}`, "
            f"min overall delta `{rule['min_overall_delta']}`, "
            f"observed `{observed_label}`, "
            f"candidate leader `{rule.get('candidate_leader') or 'none'}`, "
            f"leader required `{str(bool(rule.get('require_leader'))).lower()}`, "
            f"status `{rule['status']}`"
        )

    lines.extend(["", "## Violations", ""])
    violations = list(report.get("violations") or [])
    if not violations:
        lines.append("- none")
    else:
        for violation in violations:
            reasons = ", ".join(f"`{item}`" for item in list(violation.get("violations") or [])) or "`none`"
            lines.append(
                f"- family `{violation['family']}` provider `{violation['expected_provider']}` "
                f"failed checks {reasons}; observed delta "
                f"`{violation.get('observed_overall_delta') if violation.get('observed_overall_delta') is not None else 'missing'}`; "
                f"candidate leader `{violation.get('candidate_leader') or 'none'}`"
            )
    lines.append("")
    return "\n".join(lines)


__all__ = ["render_acquisition_benchmark_gate_markdown"]
