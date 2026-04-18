from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pipeline.assembly.abstract_recovery import (
    abstract_text_is_recoverable as assemble_abstract_text_is_recoverable,
    first_root_indicates_missing_intro as assemble_first_root_indicates_missing_intro,
    leading_abstract_text as assemble_leading_abstract_text,
    opening_abstract_candidate_records as assemble_opening_abstract_candidate_records,
    replace_front_matter_abstract_text as assemble_replace_front_matter_abstract_text,
    should_replace_front_matter_abstract as assemble_should_replace_front_matter_abstract,
    split_late_prelude_for_missing_intro as assemble_split_late_prelude_for_missing_intro,
)
from pipeline.assembly.front_matter_support import (
    abstract_text_looks_like_metadata as assemble_abstract_text_looks_like_metadata,
    clone_record_with_text as assemble_clone_record_with_text,
    dedupe_text_lines as assemble_dedupe_text_lines,
    matches_title_line as assemble_matches_title_line,
    record_width as assemble_record_width,
    record_word_count as assemble_record_word_count,
    title_lookup_keys as assemble_title_lookup_keys,
)
from pipeline.assembly.section_support import normalize_section_title as assemble_normalize_section_title


@dataclass(frozen=True)
class BoundFrontMatterSupportHelpers:
    title_lookup_keys: Callable[[str], list[str]]
    matches_title_line: Callable[[str, str], bool]
    dedupe_text_lines: Callable[[list[str]], list[str]]
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]]
    record_word_count: Callable[[dict[str, Any]], int]
    record_width: Callable[[dict[str, Any]], float]
    should_replace_front_matter_abstract: Callable[[str], bool]


@dataclass(frozen=True)
class BoundFrontMatterRecoveryHelpers:
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]]
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    abstract_text_is_recoverable: Callable[[str], bool]
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool]
    split_late_prelude_for_missing_intro: Callable[
        [list[dict[str, Any]], list[Any]],
        tuple[list[dict[str, Any]], list[dict[str, Any]]],
    ]


def title_lookup_keys(
    title: str,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> list[str]:
    return assemble_title_lookup_keys(
        title,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
    )


def matches_title_line(
    text: str,
    title: str,
    *,
    clean_text: Callable[[str], str],
    compact_text: Callable[[str], str],
    short_word_re: Any,
    normalize_title_key: Callable[[str], str],
    title_lookup_keys: Callable[[str], list[str]],
) -> bool:
    return assemble_matches_title_line(
        text,
        title,
        clean_text=clean_text,
        compact_text=compact_text,
        short_word_re=short_word_re,
        normalize_title_key=normalize_title_key,
        title_lookup_keys=title_lookup_keys,
    )


def dedupe_text_lines(
    lines: list[str],
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> list[str]:
    return assemble_dedupe_text_lines(
        lines,
        clean_text=clean_text,
        normalize_title_key=normalize_title_key,
    )


def clone_record_with_text(
    record: dict[str, Any],
    text: str,
    *,
    clean_text: Callable[[str], str],
) -> dict[str, Any]:
    return assemble_clone_record_with_text(record, text, clean_text=clean_text)


def record_word_count(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    short_word_re: Any,
) -> int:
    return assemble_record_word_count(
        record,
        clean_text=clean_text,
        short_word_re=short_word_re,
    )


def record_width(
    record: dict[str, Any],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> float:
    return assemble_record_width(record, block_source_spans=block_source_spans)


def abstract_text_looks_like_metadata(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    return assemble_abstract_text_looks_like_metadata(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def should_replace_front_matter_abstract(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    return assemble_should_replace_front_matter_abstract(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def leading_abstract_text(
    node: Any,
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    keywords_lead_re: Any,
    author_note_re: Any,
    abstract_body_break_re: Any,
    figure_ref_re: Any,
    abstract_continuation_re: Any,
    record_word_count: Callable[[dict[str, Any]], int],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
) -> tuple[str, list[dict[str, Any]]]:
    return assemble_leading_abstract_text(
        node,
        clean_text=clean_text,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        keywords_lead_re=keywords_lead_re,
        author_note_re=author_note_re,
        abstract_body_break_re=abstract_body_break_re,
        figure_ref_re=figure_ref_re,
        abstract_continuation_re=abstract_continuation_re,
        record_word_count=record_word_count,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
    )


def opening_abstract_candidate_records(
    prelude: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    abstract_lead_re: Any,
    looks_like_body_section_marker: Callable[[str], bool],
    keywords_lead_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    record_word_count: Callable[[dict[str, Any]], int],
) -> list[dict[str, Any]]:
    return assemble_opening_abstract_candidate_records(
        prelude,
        clean_text=clean_text,
        abstract_lead_re=abstract_lead_re,
        looks_like_body_section_marker=looks_like_body_section_marker,
        keywords_lead_re=keywords_lead_re,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        record_word_count=record_word_count,
    )


def abstract_text_is_recoverable(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    return assemble_abstract_text_is_recoverable(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def replace_front_matter_abstract_text(
    front_matter: dict[str, Any],
    blocks: list[dict[str, Any]],
    abstract_text: str,
    abstract_records: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> bool:
    return assemble_replace_front_matter_abstract_text(
        front_matter,
        blocks,
        abstract_text,
        abstract_records,
        block_source_spans=block_source_spans,
    )


def first_root_indicates_missing_intro(
    roots: list[Any],
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
) -> bool:
    return assemble_first_root_indicates_missing_intro(
        roots,
        normalize_section_title=lambda title: assemble_normalize_section_title(
            title,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            parse_heading_label=parse_heading_label,
            normalize_title_key=normalize_title_key,
        ),
    )


def split_late_prelude_for_missing_intro(
    prelude: list[dict[str, Any]],
    roots: list[Any],
    *,
    first_root_indicates_missing_intro: Callable[[list[Any]], bool],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return assemble_split_late_prelude_for_missing_intro(
        prelude,
        roots,
        first_root_indicates_missing_intro=first_root_indicates_missing_intro,
    )


def make_bound_front_matter_support_helpers(
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    compact_text: Callable[[str], str],
    short_word_re: Any,
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
        should_replace_front_matter_abstract=lambda text: should_replace_front_matter_abstract(
            text,
            abstract_quality_flags=abstract_quality_flags,
        ),
    )


def make_bound_front_matter_recovery_helpers(
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    abstract_quality_flags: Callable[[str], list[str]],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    looks_like_body_section_marker: Callable[[str], bool],
    keywords_lead_re: Any,
    author_note_re: Any,
    abstract_body_break_re: Any,
    figure_ref_re: Any,
    abstract_continuation_re: Any,
    abstract_lead_re: Any,
    record_word_count: Callable[[dict[str, Any]], int],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
) -> BoundFrontMatterRecoveryHelpers:
    bound_leading_abstract_text = lambda node: leading_abstract_text(
        node,
        clean_text=clean_text,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        keywords_lead_re=keywords_lead_re,
        author_note_re=author_note_re,
        abstract_body_break_re=abstract_body_break_re,
        figure_ref_re=figure_ref_re,
        abstract_continuation_re=abstract_continuation_re,
        record_word_count=record_word_count,
        normalize_abstract_candidate_text=normalize_abstract_candidate_text,
    )
    bound_opening_abstract_candidate_records = lambda prelude: opening_abstract_candidate_records(
        prelude,
        clean_text=clean_text,
        abstract_lead_re=abstract_lead_re,
        looks_like_body_section_marker=looks_like_body_section_marker,
        keywords_lead_re=keywords_lead_re,
        looks_like_front_matter_metadata=looks_like_front_matter_metadata,
        record_word_count=record_word_count,
    )
    bound_abstract_text_is_recoverable = lambda text: abstract_text_is_recoverable(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )
    bound_replace_front_matter_abstract_text = (
        lambda front_matter, blocks, abstract_text, abstract_records: replace_front_matter_abstract_text(
            front_matter,
            blocks,
            abstract_text,
            abstract_records,
            block_source_spans=block_source_spans,
        )
    )
    bound_first_root_indicates_missing_intro = lambda roots: first_root_indicates_missing_intro(
        roots,
        clean_text=clean_text,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        normalize_title_key=normalize_title_key,
    )
    return BoundFrontMatterRecoveryHelpers(
        leading_abstract_text=bound_leading_abstract_text,
        opening_abstract_candidate_records=bound_opening_abstract_candidate_records,
        abstract_text_is_recoverable=bound_abstract_text_is_recoverable,
        replace_front_matter_abstract_text=bound_replace_front_matter_abstract_text,
        split_late_prelude_for_missing_intro=lambda prelude, roots: split_late_prelude_for_missing_intro(
            prelude,
            roots,
            first_root_indicates_missing_intro=bound_first_root_indicates_missing_intro,
        ),
    )


def make_normalize_section_title(
    *,
    normalize_section_title_impl: Callable[..., str],
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
    parse_heading_label: Callable[[str], Any],
    normalize_title_key: Callable[[str], str],
) -> Callable[[str], str]:
    def normalize_section_title(title: str) -> str:
        return normalize_section_title_impl(
            title,
            clean_text=clean_text,
            clean_heading_title=clean_heading_title,
            parse_heading_label=parse_heading_label,
            normalize_title_key=normalize_title_key,
        )

    return normalize_section_title


def make_front_block_text(
    *,
    front_block_text_impl: Callable[..., str],
    clean_text: Callable[[str], str],
) -> Callable[[list[dict[str, Any]], str | None], str]:
    def front_block_text(blocks: list[dict[str, Any]], block_id: str | None) -> str:
        return front_block_text_impl(blocks, block_id, clean_text=clean_text)

    return front_block_text


def make_build_front_matter(
    *,
    build_front_matter_impl: Callable[..., tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]],
    split_leading_front_matter_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    clean_record: Callable[[dict[str, Any]], dict[str, Any]],
    clean_text: Callable[[str], str],
    record_word_count: Callable[[dict[str, Any]], int],
    record_width: Callable[[dict[str, Any]], float],
    abstract_marker_only_re: Any,
    abstract_lead_re: Any,
    looks_like_front_matter_metadata: Callable[[str], bool],
    author_note_re: Any,
    looks_like_affiliation: Callable[[str], bool],
    looks_like_intro_marker: Callable[[str], bool],
    looks_like_author_line: Callable[[str], bool],
    looks_like_contact_name: Callable[[str], bool],
    matches_title_line: Callable[[str, str], bool],
    looks_like_affiliation_continuation: Callable[[str], bool],
    funding_re: Any,
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
    preprint_marker_re: Any,
    keywords_lead_re: Any,
    abstract_text_is_usable: Callable[[str], bool],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
    default_review: Callable[..., dict[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    front_matter_missing_placeholder: str,
) -> Callable[[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int], tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]]:
    def build_front_matter(
        paper_id: str,
        prelude: list[dict[str, Any]],
        page_one_records: list[dict[str, Any]],
        blocks: list[dict[str, Any]],
        next_block_index: int,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]:
        return build_front_matter_impl(
            paper_id,
            prelude,
            page_one_records,
            blocks,
            next_block_index,
            split_leading_front_matter_records=split_leading_front_matter_records,
            clean_record=clean_record,
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
            matches_title_line=matches_title_line,
            looks_like_affiliation_continuation=looks_like_affiliation_continuation,
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
            looks_like_body_section_marker=looks_like_body_section_marker,
            preprint_marker_re=preprint_marker_re,
            keywords_lead_re=keywords_lead_re,
            abstract_text_is_usable=abstract_text_is_usable,
            normalize_abstract_candidate_text=normalize_abstract_candidate_text,
            default_review=default_review,
            block_source_spans=block_source_spans,
            front_matter_missing_placeholder=front_matter_missing_placeholder,
        )

    return build_front_matter


def make_recover_missing_front_matter_abstract(
    *,
    recover_missing_front_matter_abstract_impl: Callable[..., bool],
    front_block_text: Callable[[list[dict[str, Any]], str | None], str],
    abstract_quality_flags: Callable[[str], list[str]],
    normalize_section_title: Callable[[str], str],
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]],
    abstract_text_is_recoverable: Callable[[str], bool],
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool],
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
) -> Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[Any]], bool]:
    def recover_missing_front_matter_abstract(
        front_matter: dict[str, Any],
        blocks: list[dict[str, Any]],
        prelude: list[dict[str, Any]],
        ordered_roots: list[Any],
    ) -> bool:
        return recover_missing_front_matter_abstract_impl(
            front_matter,
            blocks,
            prelude,
            ordered_roots,
            front_block_text=front_block_text,
            abstract_quality_flags=abstract_quality_flags,
            normalize_section_title=normalize_section_title,
            leading_abstract_text=leading_abstract_text,
            abstract_text_is_recoverable=abstract_text_is_recoverable,
            replace_front_matter_abstract_text=replace_front_matter_abstract_text,
            opening_abstract_candidate_records=opening_abstract_candidate_records,
            normalize_abstract_candidate_text=normalize_abstract_candidate_text,
        )

    return recover_missing_front_matter_abstract


def build_reconcile_front_matter_runtime_helpers(
    *,
    bindings: Any,
    text_helpers: dict[str, Any],
) -> dict[str, Any]:
    build_front_matter = make_build_front_matter(
        build_front_matter_impl=bindings.build_front_matter_impl,
        split_leading_front_matter_records=bindings.split_leading_front_matter_records,
        clean_record=bindings.clean_record,
        clean_text=text_helpers["clean_text"],
        record_word_count=bindings.record_word_count,
        record_width=bindings.record_width,
        abstract_marker_only_re=bindings.abstract_marker_only_re,
        abstract_lead_re=bindings.abstract_lead_re,
        looks_like_front_matter_metadata=bindings.looks_like_front_matter_metadata,
        author_note_re=bindings.author_note_re,
        looks_like_affiliation=bindings.looks_like_affiliation,
        looks_like_intro_marker=bindings.looks_like_intro_marker,
        looks_like_author_line=bindings.looks_like_author_line,
        looks_like_contact_name=bindings.looks_like_contact_name,
        matches_title_line=bindings.matches_title_line,
        looks_like_affiliation_continuation=bindings.looks_like_affiliation_continuation,
        funding_re=bindings.funding_re,
        dedupe_text_lines=bindings.dedupe_text_lines,
        filter_front_matter_authors=bindings.filter_front_matter_authors,
        parse_authors=bindings.parse_authors,
        parse_authors_from_citation_line=bindings.parse_authors_from_citation_line,
        normalize_author_line=bindings.normalize_author_line,
        missing_front_matter_author=bindings.missing_front_matter_author,
        build_affiliations_for_authors=bindings.build_affiliations_for_authors,
        missing_front_matter_affiliation=bindings.missing_front_matter_affiliation,
        strip_author_prefix_from_affiliation_line=bindings.strip_author_prefix_from_affiliation_line,
        normalize_title_key=text_helpers["normalize_title_key"],
        clone_record_with_text=bindings.clone_record_with_text,
        looks_like_body_section_marker=bindings.looks_like_body_section_marker,
        preprint_marker_re=bindings.preprint_marker_re,
        keywords_lead_re=bindings.keywords_lead_re,
        abstract_text_is_usable=bindings.abstract_text_is_usable,
        normalize_abstract_candidate_text=bindings.normalize_abstract_candidate_text,
        default_review=text_helpers["default_review"],
        block_source_spans=text_helpers["block_source_spans"],
        front_matter_missing_placeholder=bindings.front_matter_missing_placeholder,
    )
    normalize_section_title = make_normalize_section_title(
        normalize_section_title_impl=bindings.normalize_section_title_impl,
        clean_text=text_helpers["clean_text"],
        clean_heading_title=bindings.clean_heading_title,
        parse_heading_label=text_helpers["parse_heading_label"],
        normalize_title_key=text_helpers["normalize_title_key"],
    )
    front_block_text = make_front_block_text(
        front_block_text_impl=bindings.front_block_text_impl,
        clean_text=text_helpers["clean_text"],
    )
    return {
        "build_front_matter": build_front_matter,
        "normalize_section_title": normalize_section_title,
        "front_block_text": front_block_text,
        "recover_missing_front_matter_abstract": make_recover_missing_front_matter_abstract(
            recover_missing_front_matter_abstract_impl=bindings.recover_missing_front_matter_abstract_impl,
            front_block_text=front_block_text,
            abstract_quality_flags=bindings.abstract_quality_flags,
            normalize_section_title=normalize_section_title,
            leading_abstract_text=bindings.leading_abstract_text,
            abstract_text_is_recoverable=bindings.abstract_text_is_recoverable,
            replace_front_matter_abstract_text=bindings.replace_front_matter_abstract_text,
            opening_abstract_candidate_records=bindings.opening_abstract_candidate_records,
            normalize_abstract_candidate_text=bindings.normalize_abstract_candidate_text,
        ),
    }
