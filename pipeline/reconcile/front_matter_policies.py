from __future__ import annotations

from typing import Any, Callable, Pattern


def looks_like_intro_marker(
    text: str,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    intro_marker_re: Pattern[str],
) -> bool:
    cleaned = clean_text(text)
    if not cleaned:
        return False
    if intro_marker_re.match(cleaned):
        return True
    return normalize_title_key(cleaned) in {"introduction", "1introduction"}


def looks_like_body_section_marker(
    text: str,
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    abstract_marker_only_re: Pattern[str],
    abstract_lead_re: Pattern[str],
    looks_like_intro_marker: Callable[[str], bool],
    normalize_title_key: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
) -> bool:
    cleaned = clean_heading_title(clean_text(text))
    if not cleaned or abstract_marker_only_re.fullmatch(cleaned) or abstract_lead_re.match(cleaned):
        return False
    if looks_like_intro_marker(cleaned):
        return True
    title_key = normalize_title_key(cleaned)
    if title_key in {
        "background",
        "preliminaries",
        "methods",
        "results",
        "discussion",
        "conclusion",
        "conclusions",
        "references",
    }:
        return True
    parsed = parse_heading_label(cleaned)
    if parsed is None:
        return False
    _, title = parsed
    normalized_title = normalize_title_key(title)
    return bool(normalized_title and normalized_title not in {"abstract", "keywords"})


def strip_trailing_abstract_boilerplate(
    text: str,
    *,
    clean_text: Callable[[str], str],
    compact_text: Callable[[str], str],
    trailing_abstract_boilerplate_re: Pattern[str],
    trailing_abstract_tail_re: Pattern[str],
) -> str:
    cleaned = clean_text(text)
    cleaned = trailing_abstract_boilerplate_re.sub("", cleaned)
    cleaned = trailing_abstract_tail_re.sub("", cleaned)
    return compact_text(cleaned)


def normalize_abstract_candidate_text(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Pattern[str],
    abstract_lead_re: Pattern[str],
    strip_trailing_abstract_boilerplate: Callable[[str], str],
) -> str:
    text = clean_text(" ".join(str(record.get("text", "")) for record in records))
    text = preprint_marker_re.sub("", abstract_lead_re.sub("", text)).strip()
    return strip_trailing_abstract_boilerplate(text)


def abstract_text_is_usable(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    return not abstract_quality_flags(text)


def looks_like_page_one_front_matter_tail(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    short_word_re: Pattern[str],
) -> bool:
    if int(record.get("page", 0) or 0) != 1:
        return False
    text = clean_text(str(record.get("text", "")))
    if not text:
        return False
    lowered = text.lower()
    if looks_like_front_matter_metadata(text) or looks_like_author_line(text) or looks_like_affiliation(text) or looks_like_contact_name(text):
        return True
    if any(token in lowered for token in ("www.", "available online", "sciencedirect", "elsevier", "contents lists available")):
        return True
    tokens = short_word_re.findall(text)
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    return len(tokens) <= 6 and bool(tokens) and titlecase_like >= max(1, len(tokens) - 1)


def split_leading_front_matter_records(
    prelude: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_page_one_front_matter_tail: Callable[[dict[str, Any]], bool],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    front_records: list[dict[str, Any]] = []
    remainder: list[dict[str, Any]] = []
    intro_seen = False

    for record in prelude:
        text = clean_text(str(record.get("text", "")))
        if not intro_seen and looks_like_intro_marker(text):
            intro_seen = True
            continue
        if intro_seen:
            if looks_like_page_one_front_matter_tail(record):
                front_records.append(record)
                continue
            remainder.append(record)
        else:
            front_records.append(record)

    return front_records, remainder


def is_title_page_metadata_record(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Pattern[str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Pattern[str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
) -> bool:
    page = int(record.get("page", 0) or 0)
    if page != 1:
        return False
    text = clean_text(str(record.get("text", "")))
    if not text:
        return False
    if preprint_marker_re.fullmatch(text):
        return True
    if looks_like_front_matter_metadata(text) or author_note_re.search(text):
        return True
    bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 0.0))
    if y0 >= 620.0 and (looks_like_affiliation(text) or looks_like_contact_name(text)):
        return True
    return False


def make_looks_like_intro_marker(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    intro_marker_re: Pattern[str],
) -> Callable[[str], bool]:
    def bound_looks_like_intro_marker(text: str) -> bool:
        return looks_like_intro_marker(
            text,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            intro_marker_re=intro_marker_re,
        )

    return bound_looks_like_intro_marker


def make_looks_like_body_section_marker(
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    abstract_marker_only_re: Pattern[str],
    abstract_lead_re: Pattern[str],
    looks_like_intro_marker: Callable[[str], bool],
    normalize_title_key: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
) -> Callable[[str], bool]:
    def bound_looks_like_body_section_marker(text: str) -> bool:
        return looks_like_body_section_marker(
            text,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            abstract_marker_only_re=abstract_marker_only_re,
            abstract_lead_re=abstract_lead_re,
            looks_like_intro_marker=looks_like_intro_marker,
            normalize_title_key=normalize_title_key,
            parse_heading_label=parse_heading_label,
        )

    return bound_looks_like_body_section_marker


def make_strip_trailing_abstract_boilerplate(
    *,
    clean_text: Callable[[str], str],
    compact_text: Callable[[str], str],
    trailing_abstract_boilerplate_re: Pattern[str],
    trailing_abstract_tail_re: Pattern[str],
) -> Callable[[str], str]:
    def bound_strip_trailing_abstract_boilerplate(text: str) -> str:
        return strip_trailing_abstract_boilerplate(
            text,
            clean_text=clean_text,
            compact_text=compact_text,
            trailing_abstract_boilerplate_re=trailing_abstract_boilerplate_re,
            trailing_abstract_tail_re=trailing_abstract_tail_re,
        )

    return bound_strip_trailing_abstract_boilerplate


def make_normalize_abstract_candidate_text(
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Pattern[str],
    abstract_lead_re: Pattern[str],
    strip_trailing_abstract_boilerplate: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], str]:
    def bound_normalize_abstract_candidate_text(records: list[dict[str, Any]]) -> str:
        return normalize_abstract_candidate_text(
            records,
            clean_text=clean_text,
            preprint_marker_re=preprint_marker_re,
            abstract_lead_re=abstract_lead_re,
            strip_trailing_abstract_boilerplate=strip_trailing_abstract_boilerplate,
        )

    return bound_normalize_abstract_candidate_text


def make_abstract_text_is_usable(
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> Callable[[str], bool]:
    def bound_abstract_text_is_usable(text: str) -> bool:
        return abstract_text_is_usable(
            text,
            abstract_quality_flags=abstract_quality_flags,
        )

    return bound_abstract_text_is_usable


def make_looks_like_page_one_front_matter_tail(
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    short_word_re: Pattern[str],
) -> Callable[[dict[str, Any]], bool]:
    def bound_looks_like_page_one_front_matter_tail(record: dict[str, Any]) -> bool:
        return looks_like_page_one_front_matter_tail(
            record,
            clean_text=clean_text,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            looks_like_author_line=looks_like_author_line,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_contact_name=looks_like_contact_name,
            short_word_re=short_word_re,
        )

    return bound_looks_like_page_one_front_matter_tail


def make_split_leading_front_matter_records(
    *,
    clean_text: Callable[[str], str],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_page_one_front_matter_tail: Callable[[dict[str, Any]], bool],
) -> Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def bound_split_leading_front_matter_records(
        prelude: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return split_leading_front_matter_records(
            prelude,
            clean_text=clean_text,
            looks_like_intro_marker=looks_like_intro_marker,
            looks_like_page_one_front_matter_tail=looks_like_page_one_front_matter_tail,
        )

    return bound_split_leading_front_matter_records


def make_is_title_page_metadata_record(
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Pattern[str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Pattern[str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def bound_is_title_page_metadata_record(record: dict[str, Any]) -> bool:
        return is_title_page_metadata_record(
            record,
            clean_text=clean_text,
            preprint_marker_re=preprint_marker_re,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            author_note_re=author_note_re,
            block_source_spans=block_source_spans,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_contact_name=looks_like_contact_name,
        )

    return bound_is_title_page_metadata_record


__all__ = [
    "abstract_text_is_usable",
    "is_title_page_metadata_record",
    "looks_like_body_section_marker",
    "looks_like_intro_marker",
    "looks_like_page_one_front_matter_tail",
    "make_abstract_text_is_usable",
    "make_is_title_page_metadata_record",
    "make_looks_like_body_section_marker",
    "make_looks_like_intro_marker",
    "make_looks_like_page_one_front_matter_tail",
    "make_normalize_abstract_candidate_text",
    "make_split_leading_front_matter_records",
    "make_strip_trailing_abstract_boilerplate",
    "normalize_abstract_candidate_text",
    "split_leading_front_matter_records",
    "strip_trailing_abstract_boilerplate",
]
