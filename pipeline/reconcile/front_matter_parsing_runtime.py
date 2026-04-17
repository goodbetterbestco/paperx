from __future__ import annotations

from typing import Any, Callable

from pipeline.reconcile.front_matter_parsing import (
    build_affiliations_for_authors as parsing_build_affiliations_for_authors,
    dedupe_authors as parsing_dedupe_authors,
    filter_front_matter_authors as parsing_filter_front_matter_authors,
    looks_like_affiliation as parsing_looks_like_affiliation,
    looks_like_affiliation_continuation as parsing_looks_like_affiliation_continuation,
    looks_like_author_line as parsing_looks_like_author_line,
    looks_like_contact_name as parsing_looks_like_contact_name,
    looks_like_front_matter_metadata as parsing_looks_like_front_matter_metadata,
    normalize_affiliation_line as parsing_normalize_affiliation_line,
    normalize_author_line as parsing_normalize_author_line,
    parse_authors as parsing_parse_authors,
    parse_authors_from_citation_line as parsing_parse_authors_from_citation_line,
    split_affiliation_fields as parsing_split_affiliation_fields,
    strip_author_prefix_from_affiliation_line as parsing_strip_author_prefix_from_affiliation_line,
)
from pipeline.reconcile.front_matter_policies import (
    abstract_text_is_usable as policy_abstract_text_is_usable,
    is_title_page_metadata_record as policy_is_title_page_metadata_record,
    looks_like_body_section_marker as policy_looks_like_body_section_marker,
    looks_like_intro_marker as policy_looks_like_intro_marker,
    looks_like_page_one_front_matter_tail as policy_looks_like_page_one_front_matter_tail,
    normalize_abstract_candidate_text as policy_normalize_abstract_candidate_text,
    split_leading_front_matter_records as policy_split_leading_front_matter_records,
    strip_trailing_abstract_boilerplate as policy_strip_trailing_abstract_boilerplate,
)


looks_like_affiliation = parsing_looks_like_affiliation


def make_normalize_author_line(
    *,
    clean_text: Callable[[str], str],
    author_marker_re: Any,
    author_affiliation_index_re: Any,
    compact_text: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_author_line(text: str) -> str:
        return parsing_normalize_author_line(
            text,
            clean_text=clean_text,
            author_marker_re=author_marker_re,
            author_affiliation_index_re=author_affiliation_index_re,
            compact_text=compact_text,
        )

    return normalize_author_line


def make_looks_like_contact_name(
    *,
    clean_text: Callable[[str], str],
    name_token_re: Any,
) -> Callable[[str], bool]:
    def looks_like_contact_name(text: str) -> bool:
        return parsing_looks_like_contact_name(
            text,
            clean_text=clean_text,
            name_token_re=name_token_re,
        )

    return looks_like_contact_name


def make_looks_like_front_matter_metadata(
    *,
    clean_text: Callable[[str], str],
    abbreviated_venue_line_re: Any,
    title_page_metadata_re: Any,
    front_matter_metadata_re: Any,
) -> Callable[[str], bool]:
    def looks_like_front_matter_metadata(text: str) -> bool:
        return parsing_looks_like_front_matter_metadata(
            text,
            clean_text=clean_text,
            abbreviated_venue_line_re=abbreviated_venue_line_re,
            title_page_metadata_re=title_page_metadata_re,
            front_matter_metadata_re=front_matter_metadata_re,
        )

    return looks_like_front_matter_metadata


def make_looks_like_author_line(
    *,
    looks_like_affiliation: Callable[[str], bool],
    normalize_author_line: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    reference_venue_re: Any,
    author_token_re: Any,
) -> Callable[[str], bool]:
    def looks_like_author_line(text: str) -> bool:
        return parsing_looks_like_author_line(
            text,
            looks_like_affiliation=looks_like_affiliation,
            normalize_author_line=normalize_author_line,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            reference_venue_re=reference_venue_re,
            author_token_re=author_token_re,
        )

    return looks_like_author_line


def make_looks_like_intro_marker(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    intro_marker_re: Any,
) -> Callable[[str], bool]:
    def looks_like_intro_marker(text: str) -> bool:
        return policy_looks_like_intro_marker(
            text,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            intro_marker_re=intro_marker_re,
        )

    return looks_like_intro_marker


def make_looks_like_body_section_marker(
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    looks_like_intro_marker: Callable[[str], bool],
    normalize_title_key: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
) -> Callable[[str], bool]:
    def looks_like_body_section_marker(text: str) -> bool:
        return policy_looks_like_body_section_marker(
            text,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            abstract_marker_only_re=abstract_marker_only_re,
            abstract_lead_re=abstract_lead_re,
            looks_like_intro_marker=looks_like_intro_marker,
            normalize_title_key=normalize_title_key,
            parse_heading_label=parse_heading_label,
        )

    return looks_like_body_section_marker


def make_strip_trailing_abstract_boilerplate(
    *,
    clean_text: Callable[[str], str],
    compact_text: Callable[[str], str],
    trailing_abstract_boilerplate_re: Any,
    trailing_abstract_tail_re: Any,
) -> Callable[[str], str]:
    def strip_trailing_abstract_boilerplate(text: str) -> str:
        return policy_strip_trailing_abstract_boilerplate(
            text,
            clean_text=clean_text,
            compact_text=compact_text,
            trailing_abstract_boilerplate_re=trailing_abstract_boilerplate_re,
            trailing_abstract_tail_re=trailing_abstract_tail_re,
        )

    return strip_trailing_abstract_boilerplate


def make_normalize_abstract_candidate_text(
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Any,
    abstract_lead_re: Any,
    strip_trailing_abstract_boilerplate: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], str]:
    def normalize_abstract_candidate_text(records: list[dict[str, Any]]) -> str:
        return policy_normalize_abstract_candidate_text(
            records,
            clean_text=clean_text,
            preprint_marker_re=preprint_marker_re,
            abstract_lead_re=abstract_lead_re,
            strip_trailing_abstract_boilerplate=strip_trailing_abstract_boilerplate,
        )

    return normalize_abstract_candidate_text


def make_abstract_text_is_usable(
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> Callable[[str], bool]:
    def abstract_text_is_usable(text: str) -> bool:
        return policy_abstract_text_is_usable(
            text,
            abstract_quality_flags=abstract_quality_flags,
        )

    return abstract_text_is_usable


def make_looks_like_page_one_front_matter_tail(
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    short_word_re: Any,
) -> Callable[[dict[str, Any]], bool]:
    def looks_like_page_one_front_matter_tail(record: dict[str, Any]) -> bool:
        return policy_looks_like_page_one_front_matter_tail(
            record,
            clean_text=clean_text,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            looks_like_author_line=looks_like_author_line,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_contact_name=looks_like_contact_name,
            short_word_re=short_word_re,
        )

    return looks_like_page_one_front_matter_tail


def make_split_leading_front_matter_records(
    *,
    clean_text: Callable[[str], str],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_page_one_front_matter_tail: Callable[[dict[str, Any]], bool],
) -> Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]:
    def split_leading_front_matter_records(
        prelude: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return policy_split_leading_front_matter_records(
            prelude,
            clean_text=clean_text,
            looks_like_intro_marker=looks_like_intro_marker,
            looks_like_page_one_front_matter_tail=looks_like_page_one_front_matter_tail,
        )

    return split_leading_front_matter_records


def make_parse_authors(
    *,
    clean_text: Callable[[str], str],
    normalize_author_line: Callable[[str], str],
) -> Callable[[str], list[dict[str, Any]]]:
    def parse_authors(text: str) -> list[dict[str, Any]]:
        return parsing_parse_authors(
            text,
            clean_text=clean_text,
            normalize_author_line=normalize_author_line,
        )

    return parse_authors


def make_parse_authors_from_citation_line(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    title_lookup_keys: Callable[[str], list[str]],
    citation_year_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    citation_author_split_re: Any,
    normalize_author_line: Callable[[str], str],
    short_word_re: Any,
    looks_like_affiliation: Callable[[str], bool],
) -> Callable[[str, str], list[dict[str, Any]]]:
    def parse_authors_from_citation_line(text: str, title: str) -> list[dict[str, Any]]:
        return parsing_parse_authors_from_citation_line(
            text,
            title,
            clean_text=clean_text,
            normalize_title_key=normalize_title_key,
            title_lookup_keys=title_lookup_keys,
            citation_year_re=citation_year_re,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            citation_author_split_re=citation_author_split_re,
            normalize_author_line=normalize_author_line,
            short_word_re=short_word_re,
            looks_like_affiliation=looks_like_affiliation,
        )

    return parse_authors_from_citation_line


def make_is_title_page_metadata_record(
    *,
    clean_text: Callable[[str], str],
    preprint_marker_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Any,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
) -> Callable[[dict[str, Any]], bool]:
    def is_title_page_metadata_record(record: dict[str, Any]) -> bool:
        return policy_is_title_page_metadata_record(
            record,
            clean_text=clean_text,
            preprint_marker_re=preprint_marker_re,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            author_note_re=author_note_re,
            block_source_spans=block_source_spans,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_contact_name=looks_like_contact_name,
        )

    return is_title_page_metadata_record


def make_normalize_affiliation_line(
    *,
    clean_text: Callable[[str], str],
    author_note_re: Any,
    compact_text: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_affiliation_line(text: str) -> str:
        return parsing_normalize_affiliation_line(
            text,
            clean_text=clean_text,
            author_note_re=author_note_re,
            compact_text=compact_text,
        )

    return normalize_affiliation_line


def make_looks_like_affiliation_continuation(
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    short_word_re: Any,
) -> Callable[[str], bool]:
    def looks_like_affiliation_continuation(text: str) -> bool:
        return parsing_looks_like_affiliation_continuation(
            text,
            clean_text=clean_text,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            short_word_re=short_word_re,
        )

    return looks_like_affiliation_continuation


def make_split_affiliation_fields(
    *,
    normalize_affiliation_line: Callable[[str], str],
) -> Callable[[list[str]], tuple[str, str, str]]:
    def split_affiliation_fields(affiliation_lines: list[str]) -> tuple[str, str, str]:
        return parsing_split_affiliation_fields(
            affiliation_lines,
            normalize_affiliation_line=normalize_affiliation_line,
        )

    return split_affiliation_fields


def make_dedupe_authors(
    *,
    normalize_author_line: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def dedupe_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return parsing_dedupe_authors(
            authors,
            normalize_author_line=normalize_author_line,
            normalize_title_key=normalize_title_key,
        )

    return dedupe_authors


def make_filter_front_matter_authors(
    *,
    normalize_author_line: Callable[[str], str],
    short_word_re: Any,
    looks_like_affiliation: Callable[[str], bool],
    looks_like_front_matter_metadata: Callable[[str], bool],
    dedupe_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    def filter_front_matter_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return parsing_filter_front_matter_authors(
            authors,
            normalize_author_line=normalize_author_line,
            short_word_re=short_word_re,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_front_matter_metadata=looks_like_front_matter_metadata,
            dedupe_authors=dedupe_authors,
        )

    return filter_front_matter_authors


def make_build_affiliations_for_authors(
    *,
    normalize_affiliation_line: Callable[[str], str],
    split_affiliation_fields: Callable[[list[str]], tuple[str, str, str]],
) -> Callable[[int, list[str]], tuple[list[dict[str, Any]], list[list[str]]]]:
    def build_affiliations_for_authors(
        author_count: int,
        affiliation_lines: list[str],
    ) -> tuple[list[dict[str, Any]], list[list[str]]]:
        return parsing_build_affiliations_for_authors(
            author_count,
            affiliation_lines,
            normalize_affiliation_line=normalize_affiliation_line,
            split_affiliation_fields=split_affiliation_fields,
        )

    return build_affiliations_for_authors


def make_strip_author_prefix_from_affiliation_line(
    *,
    clean_text: Callable[[str], str],
    normalize_author_line: Callable[[str], str],
) -> Callable[[str, list[dict[str, Any]]], str]:
    def strip_author_prefix_from_affiliation_line(
        text: str,
        authors: list[dict[str, Any]],
    ) -> str:
        return parsing_strip_author_prefix_from_affiliation_line(
            text,
            authors,
            clean_text=clean_text,
            normalize_author_line=normalize_author_line,
        )

    return strip_author_prefix_from_affiliation_line
