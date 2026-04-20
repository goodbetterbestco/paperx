from __future__ import annotations

from typing import Any


def leader_value(row: dict[str, Any], *keys: str, default: str = "n/a") -> Any:
    for key in keys:
        value = row.get(key)
        if value is not None and value != "":
            return value
    return default


def metric_leader_summary_parts(leaders: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for label, keys in (
        ("overall", ("avg_overall_score", "overall")),
        ("content", ("avg_content_score", "content")),
        ("execution", ("avg_execution_score", "execution")),
    ):
        row = leaders.get(label) or {}
        if row:
            parts.append(f"{label} `{row['provider']}` at `{leader_value(row, *keys)}`")
    return parts


def append_leader_lines(
    lines: list[str],
    leaders: dict[str, Any],
    *,
    family_label: str = "family",
    capability_score_keys: tuple[str, ...] = ("avg_score", "score"),
) -> None:
    for label, keys in (
        ("overall", ("avg_overall_score", "overall")),
        ("content", ("avg_content_score", "content")),
        ("execution", ("avg_execution_score", "execution")),
    ):
        row = leaders.get(label) or {}
        if row:
            lines.append(f"- {label}: `{row['provider']}` at `{leader_value(row, *keys)}`")

    for capability in list(leaders.get("capabilities") or []):
        leader = capability.get("leader") or {}
        if leader:
            lines.append(
                f"- `{capability['capability']}`: `{leader['provider']}` "
                f"at `{leader_value(leader, *capability_score_keys)}`"
            )

    for family in list(leaders.get("families") or []):
        family_leaders = family.get("leaders") or {}
        overall_leader = family_leaders.get("overall") or {}
        if overall_leader:
            lines.append(
                f"- {family_label} `{family['family']}` overall leader: "
                f"`{overall_leader['provider']}` at "
                f"`{leader_value(overall_leader, 'avg_overall_score', 'overall')}`"
            )
        for capability in list(family_leaders.get("capabilities") or []):
            leader = capability.get("leader") or {}
            if leader:
                lines.append(
                    f"- {family_label} `{family['family']}` capability `{capability['capability']}` leader: "
                    f"`{leader['provider']}` at `{leader_value(leader, *capability_score_keys)}`"
                )


def render_labeled_leader_snapshot(label: str, leaders: dict[str, Any]) -> list[str]:
    lines = [f"### {label}", ""]
    append_leader_lines(lines, leaders)
    lines.append("")
    return lines


def capability_leader_map(leaders: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("capability", "") or "").strip(): item.get("leader") or {}
        for item in list(leaders.get("capabilities") or [])
        if str(item.get("capability", "") or "").strip()
    }


def family_leader_map(leaders: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("family", "") or "").strip(): item.get("leaders") or {}
        for item in list(leaders.get("families") or [])
        if str(item.get("family", "") or "").strip()
    }


__all__ = [
    "append_leader_lines",
    "capability_leader_map",
    "family_leader_map",
    "leader_value",
    "metric_leader_summary_parts",
    "render_labeled_leader_snapshot",
]
