from __future__ import annotations

from typing import Any, Callable


def section_id(node: Any, fallback_index: int, *, normalize_title_key: Callable[[str], str]) -> str:
    label = getattr(node, "label", None)
    if label:
        return f"sec-{'-'.join(label)}"
    title = normalize_title_key(str(getattr(node, "title", "")))
    return f"sec-{title or f'u-{fallback_index}'}"


def normalize_section_title(
    title: str,
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
) -> str:
    cleaned = clean_heading_title(clean_text(title))
    parsed = parse_heading_label(cleaned)
    if parsed is not None:
        _, cleaned = parsed
    return normalize_title_key(cleaned)


def make_normalize_section_title(
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
) -> Callable[[str], str]:
    def bound_normalize_section_title(title: str) -> str:
        return normalize_section_title(
            title,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            parse_heading_label=parse_heading_label,
            normalize_title_key=normalize_title_key,
        )

    return bound_normalize_section_title


__all__ = [
    "make_normalize_section_title",
    "normalize_section_title",
    "section_id",
]
