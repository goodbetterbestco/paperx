from __future__ import annotations

from typing import Any


def summarize_round(round_status: dict[str, Any]) -> dict[str, Any]:
    paper_results = round_status.get("papers", {})
    success_results = [item for item in paper_results.values() if item.get("status") == "completed"]
    failed_results = [item for item in paper_results.values() if item.get("status") == "failed"]
    running_results = [item for item in paper_results.values() if item.get("status") == "running"]
    queued_results = [item for item in paper_results.values() if item.get("status") == "queued"]
    anomalies: dict[str, int] = {}
    stale_reasons: dict[str, int] = {}
    stale_before_build_count = 0
    fresh_skip_count = 0
    for item in success_results:
        if item.get("skipped_fresh"):
            fresh_skip_count += 1
        for flag in item.get("anomalies", []):
            anomalies[flag] = anomalies.get(flag, 0) + 1
    for item in paper_results.values():
        staleness = item.get("prebuild_staleness", {})
        if staleness.get("stale"):
            stale_before_build_count += 1
            for reason in staleness.get("reasons", []):
                stale_reasons[str(reason)] = stale_reasons.get(str(reason), 0) + 1
    return {
        "success_count": len(success_results),
        "failure_count": len(failed_results),
        "running_count": len(running_results),
        "queued_count": len(queued_results),
        "anomalies": anomalies,
        "stale_before_build_count": stale_before_build_count,
        "stale_reasons": stale_reasons,
        "fresh_skip_count": fresh_skip_count,
    }


def render_final_report(status: dict[str, Any]) -> str:
    round_names = sorted(status.get("rounds", {}).keys())
    lines = [
        "# Canonical Corpus Report",
        "",
        f"- Started: {status.get('started_at', '')}",
        f"- Updated: {status.get('updated_at', '')}",
        f"- Papers targeted: {len(status.get('papers', []))}",
        "",
    ]
    for round_name in round_names:
        round_status = status["rounds"][round_name]
        summary = summarize_round(round_status)
        lines.extend(
            [
                f"## {round_name.title()}",
                "",
                f"- Started: {round_status.get('started_at', '')}",
                f"- Completed: {round_status.get('completed_at', '')}",
                f"- Successes: {summary['success_count']}",
                f"- Queued: {summary['queued_count']}",
                f"- Running: {summary['running_count']}",
                f"- Failures: {summary['failure_count']}",
                f"- Stale before rebuild: {summary['stale_before_build_count']}",
                f"- Fresh canonical skips: {summary['fresh_skip_count']}",
            ]
        )
        if summary["anomalies"]:
            lines.append("- Common anomalies:")
            for key, value in sorted(summary["anomalies"].items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - `{key}`: {value}")
        if summary["stale_reasons"]:
            lines.append("- Common stale reasons:")
            for key, value in sorted(summary["stale_reasons"].items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - `{key}`: {value}")
        lines.append("")

    lines.append("## Paper Status")
    lines.append("")
    if round_names:
        header = ["Paper", *[round_name.replace("_", " ").title() for round_name in round_names]]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    else:
        lines.append("| Paper | Status |")
        lines.append("| --- | --- |")
    for paper_id in status.get("papers", []):
        row = [paper_id]
        for round_name in round_names:
            paper_status = status.get("rounds", {}).get(round_name, {}).get("papers", {}).get(paper_id, {})
            if paper_status.get("status") == "completed":
                metrics = paper_status.get("metrics", {})
                cell = f"completed ({metrics.get('sections', 0)} s / {metrics.get('references', 0)} r / {metrics.get('figures', 0)} f)"
                anomalies = paper_status.get("anomalies", [])
                if anomalies:
                    cell += f" {';'.join(anomalies[:3])}"
                if paper_status.get("prebuild_staleness", {}).get("stale"):
                    cell += " stale-before-build"
                if paper_status.get("skipped_fresh"):
                    cell += " fresh-skip"
            elif paper_status.get("status") == "running":
                cell = f"running (started {paper_status.get('started_at', '')})"
            elif paper_status.get("status") == "queued":
                mathpix_phase = str(((paper_status.get("mathpix") or {}).get("phase") or "")).strip()
                if mathpix_phase:
                    cell = f"queued (mathpix {mathpix_phase})"
                else:
                    cell = "queued"
            elif paper_status:
                cell = "failed"
            else:
                cell = "not-run"
            row.append(cell)
        if len(row) == 1:
            row.append("not-run")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    for note in status.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "render_final_report",
    "summarize_round",
]
