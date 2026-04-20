from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pipeline.assembly.section_support import (
    make_normalize_section_title,
    normalize_section_title,
)


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


def should_replace_front_matter_abstract(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    flags = set(abstract_quality_flags(text))
    return "missing" in flags or bool(flags)


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
    records: list[dict[str, Any]] = []
    word_total = 0
    last_page: int | None = None
    for index, record in enumerate(node.records):
        record_type = str(record.get("type", ""))
        text = clean_text(str(record.get("text", "")))
        if not text:
            continue
        if record_type == "heading" and records:
            break
        if record_type not in {"paragraph", "front_matter", "footnote"}:
            continue
        if looks_like_front_matter_metadata(text) and not keywords_lead_re.match(text):
            if records:
                break
            continue
        if author_note_re.search(text):
            if records:
                break
            continue
        page = int(record.get("page", 0) or 0)
        if records and last_page is not None and page - last_page > 1:
            break
        if records and word_total >= 60 and abstract_body_break_re.match(text):
            break
        if records and word_total >= 12:
            future_heading_exists = any(
                str(follower.get("type", "")) == "heading"
                and clean_text(str(follower.get("text", "")))
                for follower in node.records[index + 1 :]
            )
            if future_heading_exists and (
                figure_ref_re.search(text)
                or abstract_body_break_re.match(text)
                or not abstract_continuation_re.match(text)
            ):
                break
        records.append(record)
        word_total += record_word_count(record)
        last_page = page
    text = normalize_abstract_candidate_text(records)
    return text, records


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
    candidate_records: list[dict[str, Any]] = []
    for index, record in enumerate(prelude):
        text = clean_text(str(record.get("text", "")))
        if not text:
            continue
        if abstract_lead_re.match(text):
            candidate_records.append(record)
            for follower in prelude[index + 1 :]:
                follower_text = clean_text(str(follower.get("text", "")))
                if not follower_text:
                    continue
                if looks_like_body_section_marker(follower_text):
                    break
                if keywords_lead_re.search(follower_text):
                    candidate_records.append(follower)
                    break
                if looks_like_front_matter_metadata(follower_text) and not follower_text.lower().startswith("keywords"):
                    continue
                if follower.get("type") not in {"paragraph", "front_matter", "footnote"}:
                    break
                candidate_records.append(follower)
            return candidate_records

    for index, record in enumerate(prelude[:-1]):
        text = clean_text(str(record.get("text", "")))
        next_text = clean_text(str(prelude[index + 1].get("text", "")))
        if (
            record_word_count(record) >= 20
            and not looks_like_front_matter_metadata(text)
            and keywords_lead_re.search(next_text)
        ):
            return [record, prelude[index + 1]]
    return []


def abstract_text_is_recoverable(
    text: str,
    *,
    abstract_quality_flags: Callable[[str], list[str]],
) -> bool:
    flags = set(abstract_quality_flags(text))
    return bool(text) and "missing" not in flags and "too_long" not in flags and "section_marker" not in flags


def replace_front_matter_abstract_text(
    front_matter: dict[str, Any],
    blocks: list[dict[str, Any]],
    abstract_text: str,
    abstract_records: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> bool:
    target_id = str(front_matter.get("abstract_block_id") or "")
    if not target_id:
        return False
    for block in blocks:
        if str(block.get("id", "")) != target_id:
            continue
        block["content"] = {"spans": [{"kind": "text", "text": abstract_text}]}
        block["source_spans"] = [span for record in abstract_records for span in block_source_spans(record)]
        return True
    return False


def recover_missing_front_matter_abstract(
    front_matter: dict[str, Any],
    blocks: list[dict[str, Any]],
    prelude: list[dict[str, Any]],
    ordered_roots: list[Any],
    *,
    front_block_text: Callable[[list[dict[str, Any]], str | None], str],
    abstract_quality_flags: Callable[[str], list[str]],
    normalize_section_title: Callable[[str], str],
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]],
    abstract_text_is_recoverable: Callable[[str], bool],
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool],
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str],
) -> bool:
    current_text = front_block_text(blocks, front_matter.get("abstract_block_id"))
    if "missing" not in abstract_quality_flags(current_text):
        return False

    for node in ordered_roots[:3]:
        if normalize_section_title(str(node.title)) != "abstract":
            continue
        abstract_text, abstract_records = leading_abstract_text(node)
        if abstract_text_is_recoverable(abstract_text):
            return replace_front_matter_abstract_text(front_matter, blocks, abstract_text, abstract_records)
    return False


def first_root_indicates_missing_intro(
    roots: list[Any],
    *,
    normalize_section_title: Callable[[str], str],
) -> bool:
    if not roots:
        return False
    first_root = roots[0]
    title_key = normalize_section_title(str(first_root.title))
    if title_key in {"abstract", "introduction"}:
        return False
    label = getattr(first_root, "label", None)
    if not label:
        return False
    return label[0] != "1" or len(label) > 1


def split_late_prelude_for_missing_intro(
    prelude: list[dict[str, Any]],
    roots: list[Any],
    *,
    first_root_indicates_missing_intro: Callable[[list[Any]], bool],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not prelude or not first_root_indicates_missing_intro(roots):
        return prelude, []

    first_page = int(prelude[0].get("page", 0) or 0)
    leading: list[dict[str, Any]] = []
    overflow: list[dict[str, Any]] = []
    overflow_started = False
    for record in prelude:
        page = int(record.get("page", first_page) or first_page)
        if page != first_page:
            overflow_started = True
        if overflow_started:
            overflow.append(record)
        else:
            leading.append(record)

    if not overflow:
        return prelude, []
    return leading, overflow


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
    bound_normalize_section_title = make_normalize_section_title(
        normalize_section_title_impl=normalize_section_title,
        clean_text=clean_text,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        normalize_title_key=normalize_title_key,
    )
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
        normalize_section_title=bound_normalize_section_title,
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
    def bound_recover_missing_front_matter_abstract(
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

    return bound_recover_missing_front_matter_abstract


__all__ = [
    "BoundFrontMatterRecoveryHelpers",
    "abstract_text_is_recoverable",
    "first_root_indicates_missing_intro",
    "leading_abstract_text",
    "make_bound_front_matter_recovery_helpers",
    "make_recover_missing_front_matter_abstract",
    "opening_abstract_candidate_records",
    "recover_missing_front_matter_abstract",
    "replace_front_matter_abstract_text",
    "should_replace_front_matter_abstract",
    "split_late_prelude_for_missing_intro",
]
