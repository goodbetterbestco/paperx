from __future__ import annotations

import re
from typing import Any


def _record_preview(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "page": int(record.get("page", 0) or 0),
        "type": str(record.get("type", "")),
        "text": str(record.get("text", "")).strip(),
    }


def build_title_decision(
    *,
    title: str,
    source: str,
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "selected_text": title,
        "source": source,
        "candidate_count": len(candidate_records),
        "candidates": [_record_preview(record) for record in candidate_records[:12]],
    }


def recover_title(
    candidate_records: list[dict[str, Any]],
    *,
    clean_text: Any,
    record_word_count: Any,
    record_width: Any,
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    looks_like_front_matter_metadata: Any,
    author_note_re: Any,
    looks_like_affiliation: Any,
    looks_like_intro_marker: Any,
    looks_like_author_line: Any,
    looks_like_contact_name: Any,
) -> tuple[str, str]:
    def title_from_citation(text: str) -> str:
        match = re.search(r"\(\s*(?:18|19|20)\d{2}[a-z]?\s*\)\.\s*(?P<title>.+?)\.\s+[A-Z]", text)
        if not match:
            return ""
        return clean_text(match.group("title"))

    def title_signal(text: str, record: dict[str, Any], *, allow_author_like: bool) -> bool:
        word_count = record_word_count(record)
        width = record_width(record)
        lowered = text.lower()
        has_connector_word = bool(re.search(r"\b(?:a|an|and|for|from|in|into|of|on|or|the|to|with)\b", lowered))
        titlecase_words = len(re.findall(r"\b[A-Z][a-z]+(?:[-'][A-Za-z]+)?\b", text))
        if text.endswith(".") or word_count > 14:
            return False
        if text.startswith("(") and text.endswith(")") and word_count >= 2:
            return True
        if text.isupper() and word_count >= 4:
            return True
        if has_connector_word and word_count >= 3:
            return True
        if width >= 250.0 and word_count >= 3:
            return True
        if allow_author_like and width >= 300.0 and titlecase_words >= 3:
            return True
        return False

    start_index: int | None = None
    for index, record in enumerate(candidate_records):
        text = clean_text(str(record.get("text", "")))
        if not text or text.lower() == "and":
            continue
        if abstract_marker_only_re.fullmatch(text) or abstract_lead_re.match(text):
            if start_index is None:
                continue
            break
        if not start_index:
            citation_title = title_from_citation(text)
            if citation_title:
                return citation_title, "front_matter_citation"
        if looks_like_front_matter_metadata(text) or author_note_re.search(text):
            continue
        if looks_like_affiliation(text):
            continue
        if title_signal(text, record, allow_author_like=True):
            start_index = index
            break

    if start_index is None:
        return "", "unresolved"

    title_lines: list[str] = []
    for record in candidate_records[start_index:]:
        text = clean_text(str(record.get("text", "")))
        if not text:
            continue
        record_is_title_like = title_signal(text, record, allow_author_like=True)
        if abstract_marker_only_re.fullmatch(text) or abstract_lead_re.match(text):
            break
        if looks_like_front_matter_metadata(text) or author_note_re.search(text):
            if title_lines:
                break
            continue
        if looks_like_intro_marker(text):
            if title_lines:
                break
            continue
        if looks_like_author_line(text) or looks_like_affiliation(text) or looks_like_contact_name(text):
            if title_lines:
                break
            if not record_is_title_like:
                continue
        if text.lower() == "and" or record_word_count(record) < 2:
            continue
        if title_lines and record_width(record) < 140.0 and not (text.startswith("(") and text.endswith(")")):
            break
        title_lines.append(text)
        if len(title_lines) >= 3:
            break
    return clean_text(" ".join(title_lines)), "front_matter_records"
