from __future__ import annotations

from dataclasses import dataclass

from pipeline.assembly.abstract_recovery import (
    BoundFrontMatterRecoveryHelpers,
    abstract_text_is_recoverable,
    first_root_indicates_missing_intro,
    leading_abstract_text,
    make_bound_front_matter_recovery_helpers,
    make_recover_missing_front_matter_abstract,
    opening_abstract_candidate_records,
    replace_front_matter_abstract_text,
    should_replace_front_matter_abstract,
    split_late_prelude_for_missing_intro,
)
from pipeline.assembly.front_matter_builder import make_build_front_matter
from pipeline.assembly.front_matter_support import (
    BoundFrontMatterSupportHelpers,
    abstract_text_looks_like_metadata,
    clone_record_with_text,
    dedupe_text_lines,
    front_block_text,
    make_bound_front_matter_support_helpers,
    make_front_block_text,
    matches_title_line,
    record_width,
    record_word_count,
    title_lookup_keys,
)
from pipeline.assembly.section_support import make_normalize_section_title


@dataclass(frozen=True)
class ReconcileFrontMatterRuntimeHelpers:
    build_front_matter: object
    normalize_section_title: object
    front_block_text: object
    recover_missing_front_matter_abstract: object


def build_reconcile_front_matter_runtime_helpers(
    *,
    bindings: object,
    text_helpers: object,
) -> ReconcileFrontMatterRuntimeHelpers:
    build_front_matter = make_build_front_matter(
        split_leading_front_matter_records=bindings.split_leading_front_matter_records,
        clean_record=bindings.clean_record,
        clean_text=text_helpers.clean_text,
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
        normalize_title_key=text_helpers.normalize_title_key,
        clone_record_with_text=bindings.clone_record_with_text,
        looks_like_body_section_marker=bindings.looks_like_body_section_marker,
        preprint_marker_re=bindings.preprint_marker_re,
        keywords_lead_re=bindings.keywords_lead_re,
        abstract_text_is_usable=bindings.abstract_text_is_usable,
        normalize_abstract_candidate_text=bindings.normalize_abstract_candidate_text,
        default_review=text_helpers.default_review,
        block_source_spans=text_helpers.block_source_spans,
        front_matter_missing_placeholder=bindings.front_matter_missing_placeholder,
    )
    normalize_section_title = make_normalize_section_title(
        clean_text=text_helpers.clean_text,
        clean_heading_title=bindings.clean_heading_title,
        parse_heading_label=text_helpers.parse_heading_label,
        normalize_title_key=text_helpers.normalize_title_key,
    )
    front_block_text_fn = make_front_block_text(
        clean_text=text_helpers.clean_text,
    )
    return ReconcileFrontMatterRuntimeHelpers(
        build_front_matter=build_front_matter,
        normalize_section_title=normalize_section_title,
        front_block_text=front_block_text_fn,
        recover_missing_front_matter_abstract=make_recover_missing_front_matter_abstract(
            front_block_text=front_block_text_fn,
            abstract_quality_flags=bindings.abstract_quality_flags,
            normalize_section_title=normalize_section_title,
            leading_abstract_text=bindings.leading_abstract_text,
            abstract_text_is_recoverable=bindings.abstract_text_is_recoverable,
            replace_front_matter_abstract_text=bindings.replace_front_matter_abstract_text,
            opening_abstract_candidate_records=bindings.opening_abstract_candidate_records,
            normalize_abstract_candidate_text=bindings.normalize_abstract_candidate_text,
        ),
    )


__all__ = [
    "BoundFrontMatterRecoveryHelpers",
    "BoundFrontMatterSupportHelpers",
    "ReconcileFrontMatterRuntimeHelpers",
    "abstract_text_is_recoverable",
    "abstract_text_looks_like_metadata",
    "build_reconcile_front_matter_runtime_helpers",
    "clone_record_with_text",
    "dedupe_text_lines",
    "first_root_indicates_missing_intro",
    "front_block_text",
    "leading_abstract_text",
    "make_bound_front_matter_recovery_helpers",
    "make_bound_front_matter_support_helpers",
    "make_build_front_matter",
    "make_front_block_text",
    "make_normalize_section_title",
    "make_recover_missing_front_matter_abstract",
    "matches_title_line",
    "opening_abstract_candidate_records",
    "record_width",
    "record_word_count",
    "replace_front_matter_abstract_text",
    "should_replace_front_matter_abstract",
    "split_late_prelude_for_missing_intro",
    "title_lookup_keys",
]
