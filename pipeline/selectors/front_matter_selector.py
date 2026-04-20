from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipeline.selectors.abstract_selector import collect_abstract_and_funding_records


@dataclass(frozen=True)
class FrontMatterResolution:
    authors: list[dict[str, Any]]
    affiliations: list[dict[str, Any]]
    abstract_records: list[dict[str, Any]]
    funding_records: list[dict[str, Any]]
    abstract_source: str


def resolve_front_matter_resolution(
    *,
    content_records: list[dict[str, Any]],
    leading_boundary_index: int,
    page_one_clean_records: list[dict[str, Any]],
    page_one_content_start_index: int,
    page_one_boundary_index: int,
    title: str,
    clean_text: Any,
    matches_title_line: Any,
    looks_like_front_matter_metadata: Any,
    author_note_re: Any,
    looks_like_affiliation: Any,
    looks_like_affiliation_continuation: Any,
    looks_like_author_line: Any,
    looks_like_contact_name: Any,
    funding_re: Any,
    dedupe_text_lines: Any,
    filter_front_matter_authors: Any,
    parse_authors: Any,
    parse_authors_from_citation_line: Any,
    normalize_author_line: Any,
    missing_front_matter_author: Any,
    build_affiliations_for_authors: Any,
    missing_front_matter_affiliation: Any,
    strip_author_prefix_from_affiliation_line: Any,
    normalize_title_key: Any,
    clone_record_with_text: Any,
    record_word_count: Any,
    looks_like_body_section_marker: Any,
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    preprint_marker_re: Any,
    keywords_lead_re: Any,
    abstract_text_is_usable: Any,
    normalize_abstract_candidate_text: Any,
) -> FrontMatterResolution:
    author_candidates: list[dict[str, Any]] = []
    affiliation_lines: list[str] = []
    affiliation_continuation_open = False
    for record in content_records[:leading_boundary_index]:
        text = clean_text(str(record.get("text", "")))
        if not text or matches_title_line(text, title):
            affiliation_continuation_open = False
            continue
        if looks_like_front_matter_metadata(text) or author_note_re.search(text):
            affiliation_continuation_open = False
            continue
        if text.lower() == "and":
            affiliation_continuation_open = False
            continue
        if looks_like_affiliation(text):
            affiliation_lines.append(text)
            continue
        if (
            affiliation_lines
            and looks_like_affiliation_continuation(text)
            and (affiliation_continuation_open or text.rstrip().endswith(","))
        ):
            affiliation_lines.append(text)
            affiliation_continuation_open = True
            continue
        affiliation_continuation_open = False
        if looks_like_author_line(text):
            author_candidates.append(record)

    page_one_author_candidates: list[dict[str, Any]] = []
    page_one_affiliation_lines: list[str] = []
    affiliation_continuation_open = False
    for record in page_one_clean_records[page_one_content_start_index:page_one_boundary_index]:
        text = clean_text(str(record.get("text", "")))
        if not text or matches_title_line(text, title):
            affiliation_continuation_open = False
            continue
        if abstract_marker_only_re.fullmatch(text) or abstract_lead_re.match(text):
            affiliation_continuation_open = False
            continue
        if looks_like_front_matter_metadata(text) or funding_re.search(text) or text.lower() == "and":
            affiliation_continuation_open = False
            continue
        if looks_like_affiliation(text):
            page_one_affiliation_lines.append(text)
            continue
        if (
            page_one_affiliation_lines
            and looks_like_affiliation_continuation(text)
            and (affiliation_continuation_open or text.rstrip().endswith(","))
        ):
            page_one_affiliation_lines.append(text)
            affiliation_continuation_open = True
            continue
        affiliation_continuation_open = False
        if looks_like_author_line(text):
            page_one_author_candidates.append(record)

    author_candidates.extend(page_one_author_candidates)
    affiliation_lines.extend(page_one_affiliation_lines)
    affiliation_lines = dedupe_text_lines(affiliation_lines)

    page_one_authors = filter_front_matter_authors(
        [
            author
            for record in page_one_author_candidates
            for author in parse_authors(str(record.get("text", "")))
        ]
    )
    authors = filter_front_matter_authors(
        [
            author
            for record in author_candidates
            for author in parse_authors(str(record.get("text", "")))
        ]
    )
    if len(page_one_authors) >= 2:
        authors = page_one_authors
        deduped_page_one_affiliations = dedupe_text_lines(page_one_affiliation_lines)
        if deduped_page_one_affiliations:
            mathpix_affiliation_lines = [line for line in deduped_page_one_affiliations if r"\(" in line]
            affiliation_lines = mathpix_affiliation_lines or deduped_page_one_affiliations

    if not authors:
        citation_authors = filter_front_matter_authors(
            [
                author
                for record in content_records[:leading_boundary_index]
                + page_one_clean_records[page_one_content_start_index:]
                for author in parse_authors_from_citation_line(str(record.get("text", "")), title)
            ]
        )
        if citation_authors:
            authors = citation_authors
    if not authors:
        for record in content_records[:leading_boundary_index]:
            text = clean_text(str(record.get("text", "")))
            if not text or matches_title_line(text, title):
                continue
            if looks_like_front_matter_metadata(text) or author_note_re.search(text) or looks_like_affiliation(text):
                continue
            if looks_like_contact_name(text):
                authors = [{"name": normalize_author_line(text), "affiliation_ids": ["aff-1"]}]
                break
    if not authors:
        authors = [missing_front_matter_author()]

    affiliation_lines = [
        stripped
        for line in affiliation_lines
        if (stripped := strip_author_prefix_from_affiliation_line(line, authors))
    ]
    affiliations, author_affiliation_ids = build_affiliations_for_authors(len(authors), affiliation_lines)
    if not affiliations:
        affiliations = [missing_front_matter_affiliation()]
        author_affiliation_ids = [["aff-1"] for _ in range(len(authors))]
    for author, affiliation_ids in zip(authors, author_affiliation_ids):
        author["affiliation_ids"] = affiliation_ids or author.get("affiliation_ids", ["aff-1"])

    abstract_records, funding_records = collect_abstract_and_funding_records(
        content_records,
        allow_fallback=False,
        title=title,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
        clone_record_with_text=clone_record_with_text,
        record_word_count=record_word_count,
        matches_title_line=matches_title_line,
        looks_like_body_section_marker=looks_like_body_section_marker,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        preprint_marker_re=preprint_marker_re,
        keywords_lead_re=keywords_lead_re,
        looks_like_author_line=looks_like_author_line,
        looks_like_affiliation=looks_like_affiliation,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        author_note_re=author_note_re,
        funding_re=funding_re,
        abstract_text_is_usable=abstract_text_is_usable,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
    )
    abstract_source = "front_matter_records"
    if not abstract_records:
        page_one_content_records = page_one_clean_records[page_one_content_start_index:]
        page_one_abstract_records, page_one_funding_records = collect_abstract_and_funding_records(
            page_one_content_records,
            allow_fallback=False,
            title=title,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            clone_record_with_text=clone_record_with_text,
            record_word_count=record_word_count,
            matches_title_line=matches_title_line,
            looks_like_body_section_marker=looks_like_body_section_marker,
            abstract_marker_only_re=abstract_marker_only_re,
            abstract_lead_re=abstract_lead_re,
            preprint_marker_re=preprint_marker_re,
            keywords_lead_re=keywords_lead_re,
            looks_like_author_line=looks_like_author_line,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            author_note_re=author_note_re,
            funding_re=funding_re,
            abstract_text_is_usable=abstract_text_is_usable,
            normalize_abstract_candidate_text=normalize_abstract_candidate_text,
        )
        if page_one_abstract_records:
            abstract_records = page_one_abstract_records
            abstract_source = "page_one_records"
        if page_one_funding_records:
            funding_records = page_one_funding_records

    return FrontMatterResolution(
        authors=authors,
        affiliations=affiliations,
        abstract_records=abstract_records,
        funding_records=funding_records,
        abstract_source=abstract_source,
    )
