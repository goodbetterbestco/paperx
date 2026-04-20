from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Pattern


@dataclass(frozen=True)
class BoundFrontMatterSupportHelpers:
    title_lookup_keys: Callable[[str], list[str]]
    matches_title_line: Callable[[str, str], bool]
    dedupe_text_lines: Callable[[list[str]], list[str]]
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]]
    record_word_count: Callable[[dict[str, Any]], int]
    record_width: Callable[[dict[str, Any]], float]
    should_replace_front_matter_abstract: Callable[[str], bool]


def missing_front_matter_author(placeholder: str) -> dict[str, Any]:
    return {"name": placeholder, "affiliation_ids": ["aff-1"]}


def missing_front_matter_affiliation(placeholder: str) -> dict[str, Any]:
    return {
        "id": "aff-1",
        "department": placeholder,
        "institution": "",
        "address": "",
    }


def title_lookup_keys(
    title: str,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> list[str]:
    cleaned = clean_text(title)
    candidates = [cleaned]
    without_year = re.sub(r"^\s*\d{4}\s+", "", cleaned)
    if without_year != cleaned:
        candidates.append(without_year)

    for candidate in list(candidates):
        stripped = re.sub(r"^\s*(?:a|an|the)\s+", "", candidate, flags=re.IGNORECASE)
        if stripped != candidate:
            candidates.append(stripped)

    keys: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = normalize_title_key(candidate)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def matches_title_line(
    text: str,
    title: str,
    *,
    clean_text: Callable[[str], str],
    compact_text: Callable[[str], str],
    short_word_re: Pattern[str],
    normalize_title_key: Callable[[str], str],
    title_lookup_keys: Callable[[str], list[str]],
) -> bool:
    cleaned_key = normalize_title_key(clean_text(text))
    target_keys = title_lookup_keys(title)
    if cleaned_key and target_keys:
        for title_key in target_keys:
            if cleaned_key == title_key:
                return True
            if len(cleaned_key) >= 16 and title_key.startswith(cleaned_key):
                return True
            if len(title_key) >= 16 and cleaned_key.startswith(title_key):
                return True

    record_words = [token.lower() for token in short_word_re.findall(compact_text(text))]
    title_words = [token.lower() for token in short_word_re.findall(compact_text(title))]
    if not record_words or not title_words:
        return False
    if record_words == title_words:
        return True
    if len(record_words) >= len(title_words) and record_words[: len(title_words)] == title_words:
        return True
    if len(record_words) >= 4 and len(record_words) < len(title_words) and title_words[: len(record_words)] == record_words:
        return True
    return False


def dedupe_text_lines(
    lines: list[str],
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for line in lines:
        cleaned = clean_text(line)
        key = normalize_title_key(cleaned)
        if not cleaned or not key or key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


def clone_record_with_text(
    record: dict[str, Any],
    text: str,
    *,
    clean_text: Callable[[str], str],
) -> dict[str, Any]:
    cloned = dict(record)
    cloned["text"] = clean_text(text)
    return cloned


def record_word_count(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    short_word_re: Pattern[str],
) -> int:
    return len(short_word_re.findall(clean_text(str(record.get("text", "")))))


def record_width(
    record: dict[str, Any],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> float:
    spans = block_source_spans(record)
    if not spans:
        return 0.0
    bbox = spans[0].get("bbox")
    if not isinstance(bbox, dict):
        return 0.0
    try:
        return float(bbox.get("width", 0.0) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def front_block_text(
    blocks: list[dict[str, Any]],
    block_id: str | None,
    *,
    clean_text: Callable[[str], str],
) -> str:
    if not block_id:
        return ""
    for block in blocks:
        if str(block.get("id", "")) != str(block_id):
            continue
        spans = block.get("content", {}).get("spans", [])
        parts = [
            clean_text(str(span.get("text", "")))
            for span in spans
            if isinstance(span, dict) and span.get("kind") == "text"
        ]
        return clean_text(" ".join(part for part in parts if part))
    return ""


def abstract_text_looks_like_metadata(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    return bool(abstract_quality_flags(text))


def make_bound_front_matter_support_helpers(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    compact_text: Callable[[str], str],
    short_word_re: Pattern[str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    abstract_quality_flags: Callable[[str], list[str]],
) -> BoundFrontMatterSupportHelpers:
    bound_title_lookup_keys = lambda title: title_lookup_keys(
        title,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
    )
    return BoundFrontMatterSupportHelpers(
        title_lookup_keys=bound_title_lookup_keys,
        matches_title_line=lambda text, title: matches_title_line(
            text,
            title,
            clean_text=clean_text,
            compact_text=compact_text,
            short_word_re=short_word_re,
            normalize_title_key=normalize_title_key,
            title_lookup_keys=bound_title_lookup_keys,
        ),
        dedupe_text_lines=lambda lines: dedupe_text_lines(
            lines,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
        ),
        clone_record_with_text=lambda record, text: clone_record_with_text(
            record,
            text,
            clean_text=clean_text,
        ),
        record_word_count=lambda record: record_word_count(
            record,
            clean_text=clean_text,
            short_word_re=short_word_re,
        ),
        record_width=lambda record: record_width(
            record,
            block_source_spans=block_source_spans,
        ),
        should_replace_front_matter_abstract=lambda text: abstract_text_looks_like_metadata(
            text,
            abstract_quality_flags=abstract_quality_flags,
        ),
    )


def make_front_block_text(
    *,
    front_block_text_impl: Callable[..., str],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], str | None], str]:
    def bound_front_block_text(blocks: list[dict[str, Any]], block_id: str | None) -> str:
        return front_block_text_impl(blocks, block_id, clean_text=clean_text)

    return bound_front_block_text


__all__ = [
    "BoundFrontMatterSupportHelpers",
    "abstract_text_looks_like_metadata",
    "clone_record_with_text",
    "dedupe_text_lines",
    "front_block_text",
    "make_bound_front_matter_support_helpers",
    "make_front_block_text",
    "matches_title_line",
    "missing_front_matter_affiliation",
    "missing_front_matter_author",
    "record_width",
    "record_word_count",
    "title_lookup_keys",
]
