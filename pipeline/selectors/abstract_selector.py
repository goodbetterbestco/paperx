from __future__ import annotations

from typing import Any


def _record_preview(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "page": int(record.get("page", 0) or 0),
        "type": str(record.get("type", "")),
        "text": str(record.get("text", "")).strip(),
    }


def build_abstract_decision(
    *,
    abstract_text: str,
    source: str,
    candidate_records: list[dict[str, Any]],
    placeholder: bool = False,
) -> dict[str, Any]:
    return {
        "selected_text": abstract_text,
        "source": source,
        "placeholder": placeholder,
        "candidate_count": len(candidate_records),
        "candidates": [_record_preview(record) for record in candidate_records[:12]],
    }


def collect_abstract_and_funding_records(
    candidate_records: list[dict[str, Any]],
    *,
    allow_fallback: bool,
    title: str,
    clean_text: Any,
    normalize_title_key: Any,
    clone_record_with_text: Any,
    record_word_count: Any,
    matches_title_line: Any,
    looks_like_body_section_marker: Any,
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    preprint_marker_re: Any,
    keywords_lead_re: Any,
    looks_like_author_line: Any,
    looks_like_affiliation: Any,
    looks_like_front_matter_metadata: Any,
    author_note_re: Any,
    funding_re: Any,
    abstract_text_is_usable: Any,
    normalize_abstract_candidate_text: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if any(normalize_title_key(str(record.get("text", ""))) == "participants" for record in candidate_records[:12]):
        return [], []
    abstract_records: list[dict[str, Any]] = []
    funding_records: list[dict[str, Any]] = []
    abstract_anchor_index: int | None = None
    inline_abstract_record: dict[str, Any] | None = None
    for index, record in enumerate(candidate_records):
        text = clean_text(str(record.get("text", "")))
        if not text:
            continue
        if abstract_marker_only_re.fullmatch(text):
            abstract_anchor_index = index
            break
        if abstract_lead_re.match(text):
            abstract_anchor_index = index
            stripped_text = preprint_marker_re.sub("", abstract_lead_re.sub("", text)).strip()
            if stripped_text:
                inline_abstract_record = clone_record_with_text(record, stripped_text)
            break
        if looks_like_body_section_marker(text):
            break

    if abstract_anchor_index is not None:
        if inline_abstract_record is not None:
            abstract_records.append(inline_abstract_record)
        total_words = record_word_count(inline_abstract_record or {})
        for record in candidate_records[abstract_anchor_index + 1 :]:
            text = clean_text(str(record.get("text", "")))
            if not text or looks_like_body_section_marker(text):
                break
            if keywords_lead_re.match(text):
                if abstract_records:
                    break
                continue
            if looks_like_author_line(text) or looks_like_affiliation(text):
                continue
            if looks_like_front_matter_metadata(text) or author_note_re.search(text):
                continue
            if funding_re.search(text):
                funding_records.append(record)
                continue
            abstract_records.append(record)
            total_words += record_word_count(record)
            if len(abstract_records) >= 6 or total_words >= 360:
                break
        if abstract_records and not abstract_text_is_usable(normalize_abstract_candidate_text(abstract_records)):
            return [], funding_records
        return abstract_records, funding_records

    if not allow_fallback:
        return [], funding_records
    body_boundary_seen = any(looks_like_body_section_marker(str(record.get("text", ""))) for record in candidate_records)

    started_abstract = False
    start_page: int | None = None
    total_words = 0
    for record in candidate_records:
        text = clean_text(str(record.get("text", "")))
        if not text or looks_like_body_section_marker(text):
            break
        if keywords_lead_re.match(text):
            if started_abstract:
                break
            continue
        if looks_like_front_matter_metadata(text) or author_note_re.search(text):
            if started_abstract:
                break
            continue
        if funding_re.search(text):
            funding_records.append(record)
            if started_abstract:
                break
            continue
        if matches_title_line(text, title) or text.lower() == "and":
            continue
        if looks_like_author_line(text) or looks_like_affiliation(text):
            continue
        if not started_abstract and record_word_count(record) < 14:
            continue
        if started_abstract and not body_boundary_seen:
            break
        record_page = int(record.get("page", 0) or 0)
        started_abstract = True
        if start_page is None:
            start_page = record_page
        elif start_page and record_page and record_page != start_page:
            break
        abstract_records.append(record)
        total_words += record_word_count(record)
        if len(abstract_records) >= 3 or total_words >= 260:
            break
    if abstract_records and not abstract_text_is_usable(normalize_abstract_candidate_text(abstract_records)):
        return [], funding_records
    return abstract_records, funding_records
