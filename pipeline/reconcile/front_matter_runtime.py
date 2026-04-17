from __future__ import annotations

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
