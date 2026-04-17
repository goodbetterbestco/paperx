from __future__ import annotations

from typing import Any, Callable, Pattern

from pipeline.selectors.abstract_selector import build_abstract_decision
from pipeline.selectors.front_matter_selector import resolve_front_matter_resolution
from pipeline.selectors.title_selector import build_title_decision, recover_title


def build_front_matter(
    paper_id: str,
    prelude: list[dict[str, Any]],
    page_one_records: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    next_block_index: int,
    *,
    split_leading_front_matter_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    clean_text: Callable[[str], str],
    record_word_count: Callable[[dict[str, Any]], int],
    record_width: Callable[[dict[str, Any]], float],
    abstract_marker_only_re: Pattern[str],
    abstract_lead_re: Pattern[str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Pattern[str],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    matches_title_line: Callable[[str, str], bool],
    looks_like_affiliation_continuation: Callable[[str], bool],
    funding_re: Pattern[str],
    dedupe_text_lines: Callable[[list[str]], list[str]],
    filter_front_matter_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    parse_authors: Callable[[str], list[dict[str, Any]]],
    parse_authors_from_citation_line: Callable[[str, str], list[dict[str, Any]]],
    normalize_author_line: Callable[[str], str],
    missing_front_matter_author: Callable[[], dict[str, Any]],
    build_affiliations_for_authors: Callable[[int, list[str]], tuple[list[dict[str, Any]], list[list[str]]]],
    missing_front_matter_affiliation: Callable[[], dict[str, Any]],
    strip_author_prefix_from_affiliation_line: Callable[[str, list[dict[str, Any]]], str],
    normalize_title_key: Callable[[str], str],
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]],
    looks_like_body_section_marker: Callable[[str], bool],
    preprint_marker_re: Pattern[str],
    keywords_lead_re: Pattern[str],
    abstract_text_is_usable: Callable[[str], bool],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
    default_review: Callable[..., dict[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    front_matter_missing_placeholder: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]:
    leading_front_records, remainder = split_leading_front_matter_records(prelude)
    front_records = [clean_record(record) for record in leading_front_records]

    title_records = front_records
    title, title_source = recover_title(
        title_records,
        clean_text=clean_text,
        record_word_count=record_word_count,
        record_width=record_width,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        author_note_re=author_note_re,
        looks_like_affiliation=looks_like_affiliation,
        looks_like_intro_marker=looks_like_intro_marker,
        looks_like_author_line=looks_like_author_line,
        looks_like_contact_name=looks_like_contact_name,
    )
    if not title:
        title_records = [clean_record(record) for record in page_one_records if int(record.get("page", 0) or 0) == 1]
        title, title_source = recover_title(
            title_records,
            clean_text=clean_text,
            record_word_count=record_word_count,
            record_width=record_width,
            abstract_marker_only_re=abstract_marker_only_re,
            abstract_lead_re=abstract_lead_re,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            author_note_re=author_note_re,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_intro_marker=looks_like_intro_marker,
            looks_like_author_line=looks_like_author_line,
            looks_like_contact_name=looks_like_contact_name,
        )
        if title:
            title_source = "page_one_records"
    if not title:
        raise RuntimeError(
            f"Missing recoverable title for {paper_id}. Refusing to fall back to the paper slug; "
            "fix title extraction inputs or skip the paper."
        )

    title_indices = [
        index
        for index, record in enumerate(front_records)
        if matches_title_line(str(record.get("text", "")), title)
    ]
    boundary_candidates = [
        index
        for index, record in enumerate(front_records)
        if abstract_marker_only_re.fullmatch(clean_text(str(record.get("text", ""))))
        or abstract_lead_re.match(clean_text(str(record.get("text", ""))))
        or looks_like_intro_marker(str(record.get("text", "")))
    ]
    first_boundary_index = min(boundary_candidates) if boundary_candidates else None
    content_start_index = 0
    if title_indices:
        tentative_start_index = title_indices[-1] + 1
        if first_boundary_index is None or tentative_start_index <= first_boundary_index:
            content_start_index = tentative_start_index
    content_records = front_records[content_start_index:]

    leading_boundary_index = len(content_records)
    for index, record in enumerate(content_records):
        text = clean_text(str(record.get("text", "")))
        if abstract_marker_only_re.fullmatch(text) or abstract_lead_re.match(text) or looks_like_intro_marker(text):
            leading_boundary_index = index
            break

    page_one_clean_records = [
        clean_record(record)
        for record in page_one_records
        if int(record.get("page", 0) or 0) == 1
    ]
    page_one_title_indices = [
        index
        for index, record in enumerate(page_one_clean_records)
        if matches_title_line(str(record.get("text", "")), title)
    ]
    page_one_content_start_index = page_one_title_indices[0] + 1 if page_one_title_indices else 0
    while page_one_content_start_index < len(page_one_clean_records) and matches_title_line(
        str(page_one_clean_records[page_one_content_start_index].get("text", "")),
        title,
    ):
        page_one_content_start_index += 1

    page_one_boundary_index = len(page_one_clean_records)
    for index, record in enumerate(page_one_clean_records[page_one_content_start_index:], start=page_one_content_start_index):
        text = clean_text(str(record.get("text", "")))
        if abstract_marker_only_re.fullmatch(text) or abstract_lead_re.match(text) or looks_like_intro_marker(text):
            page_one_boundary_index = index
            break

    front_matter_resolution = resolve_front_matter_resolution(
        content_records=content_records,
        leading_boundary_index=leading_boundary_index,
        page_one_clean_records=page_one_clean_records,
        page_one_content_start_index=page_one_content_start_index,
        page_one_boundary_index=page_one_boundary_index,
        title=title,
        clean_text=clean_text,
        matches_title_line=matches_title_line,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        author_note_re=author_note_re,
        looks_like_affiliation=looks_like_affiliation,
        looks_like_affiliation_continuation=looks_like_affiliation_continuation,
        looks_like_author_line=looks_like_author_line,
        looks_like_contact_name=looks_like_contact_name,
        funding_re=funding_re,
        dedupe_text_lines=dedupe_text_lines,
        filter_front_matter_authors=filter_front_matter_authors,
        parse_authors=parse_authors,
        parse_authors_from_citation_line=parse_authors_from_citation_line,
        normalize_author_line=normalize_author_line,
        missing_front_matter_author=missing_front_matter_author,
        build_affiliations_for_authors=build_affiliations_for_authors,
        missing_front_matter_affiliation=missing_front_matter_affiliation,
        strip_author_prefix_from_affiliation_line=strip_author_prefix_from_affiliation_line,
        normalize_title_key=normalize_title_key,
        clone_record_with_text=clone_record_with_text,
        record_word_count=record_word_count,
        looks_like_body_section_marker=looks_like_body_section_marker,
        abstract_marker_only_re=abstract_marker_only_re,
        abstract_lead_re=abstract_lead_re,
        preprint_marker_re=preprint_marker_re,
        keywords_lead_re=keywords_lead_re,
        abstract_text_is_usable=abstract_text_is_usable,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
    )
    authors = front_matter_resolution.authors
    affiliations = front_matter_resolution.affiliations
    abstract_records = front_matter_resolution.abstract_records
    funding_records = front_matter_resolution.funding_records
    abstract_source = front_matter_resolution.abstract_source

    abstract_block_id: str | None = None
    abstract_decision: dict[str, Any]
    if abstract_records:
        abstract_text = normalize_abstract_candidate_text(abstract_records)
        if abstract_text and abstract_text_is_usable(abstract_text):
            abstract_block_id = f"blk-front-abstract-{next_block_index}"
            blocks.append(
                {
                    "id": abstract_block_id,
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                    "source_spans": [span for record in abstract_records for span in block_source_spans(record)],
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
            next_block_index += 1
            abstract_decision = build_abstract_decision(
                abstract_text=abstract_text,
                source=abstract_source,
                candidate_records=abstract_records,
            )
        else:
            abstract_decision = build_abstract_decision(
                abstract_text=front_matter_missing_placeholder,
                source=f"{abstract_source}_rejected",
                candidate_records=abstract_records,
                placeholder=True,
            )
    if abstract_block_id is None:
        abstract_block_id = f"blk-front-abstract-{next_block_index}"
        blocks.append(
            {
                "id": abstract_block_id,
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": front_matter_missing_placeholder}]},
                "source_spans": [],
                "alternates": [],
                "review": default_review(risk="low", status="edited", notes=front_matter_missing_placeholder),
            }
        )
        next_block_index += 1
        if not abstract_records:
            abstract_decision = build_abstract_decision(
                abstract_text=front_matter_missing_placeholder,
                source="missing_placeholder",
                candidate_records=[],
                placeholder=True,
            )

    funding_block_id: str | None = None
    if funding_records:
        funding_text = clean_text(" ".join(str(record["text"]) for record in funding_records))
        if funding_text:
            funding_block_id = f"blk-front-funding-{next_block_index}"
            blocks.append(
                {
                    "id": funding_block_id,
                    "type": "footnote",
                    "content": {"text": funding_text},
                    "source_spans": [span for record in funding_records for span in block_source_spans(record)],
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
            next_block_index += 1

    front_matter = {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "abstract_block_id": abstract_block_id,
        "funding_block_id": funding_block_id,
        "_debug_title_decision": build_title_decision(
            title=title,
            source=title_source,
            candidate_records=title_records,
        ),
        "_debug_abstract_decision": abstract_decision,
    }
    cleaned_remainder = [
        record
        for record in remainder
        if not (
            int(record.get("page", 0) or 0) == 1
            and (
                matches_title_line(str(record.get("text", "")), title)
                or looks_like_front_matter_metadata(str(record.get("text", "")))
                or author_note_re.search(clean_text(str(record.get("text", ""))))
                or looks_like_affiliation(str(record.get("text", "")))
                or looks_like_author_line(str(record.get("text", "")))
                or looks_like_contact_name(str(record.get("text", "")))
            )
        )
    ]
    return front_matter, blocks, next_block_index, cleaned_remainder
