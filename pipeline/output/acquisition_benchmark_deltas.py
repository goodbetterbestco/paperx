from __future__ import annotations

from typing import Any


def append_provider_delta_lines(lines: list[str], rows: list[dict[str, Any]], *, prefix: str = "-") -> None:
    for row in rows:
        lines.append(
            f"{prefix} `{row['provider']}`: overall delta `{row['overall_delta']}`, "
            f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
        )


def append_score_delta_lines(lines: list[str], rows: list[dict[str, Any]], *, prefix: str = "-") -> None:
    for row in rows:
        lines.append(f"{prefix} `{row['provider']}`: score delta `{row['score_delta']}`")


def render_delta_section(
    title: str,
    rows: list[dict[str, Any]],
    *,
    kind: str = "provider",
    empty_label: str = "- none",
) -> list[str]:
    lines = [title, ""]
    if not rows:
        lines.append(empty_label)
        lines.append("")
        return lines
    if kind == "score":
        append_score_delta_lines(lines, rows)
    else:
        append_provider_delta_lines(lines, rows)
    lines.append("")
    return lines


def append_named_provider_delta_lines(lines: list[str], rows: list[dict[str, Any]], *, label: str) -> None:
    for row in rows:
        lines.append(
            f"- {label} `{row['provider']}`: overall delta `{row['overall_delta']}`, "
            f"content delta `{row['content_delta']}`, execution delta `{row['execution_delta']}`"
        )


def append_named_score_delta_lines(lines: list[str], rows: list[dict[str, Any]], *, label: str) -> None:
    for row in rows:
        lines.append(f"- {label} `{row['provider']}`: score delta `{row['score_delta']}`")


__all__ = [
    "append_named_provider_delta_lines",
    "append_named_score_delta_lines",
    "append_provider_delta_lines",
    "append_score_delta_lines",
    "render_delta_section",
]
