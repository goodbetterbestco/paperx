from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipeline.reconcile.external_math import make_match_external_math_entry
from pipeline.reconcile.math_entry_policies import (
    make_math_entry_looks_like_prose,
    make_paragraph_block_from_graphic_math_entry,
    make_should_demote_graphic_math_entry_to_paragraph,
    make_should_demote_prose_math_entry_to_paragraph,
    make_should_drop_display_math_artifact,
)
from pipeline.reconcile.math_suppression import (
    make_looks_like_display_math_echo,
    make_overlapping_external_math_entries,
    make_trim_embedded_display_math_from_paragraph,
)


@dataclass(frozen=True)
class ReconcileMathRuntimeHelpers:
    paragraph_block_from_graphic_math_entry: Any
    should_demote_graphic_math_entry_to_paragraph: Any
    should_drop_display_math_artifact: Any
    match_external_math_entry: Any
    overlapping_external_math_entries: Any
    trim_embedded_display_math_from_paragraph: Any
    looks_like_display_math_echo: Any


def build_reconcile_math_runtime_helpers(
    *,
    bindings: Any,
    text_helpers: Any,
) -> ReconcileMathRuntimeHelpers:
    math_entry_looks_like_prose = make_math_entry_looks_like_prose(
        normalize_paragraph_text=text_helpers.normalize_paragraph_text,
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
        looks_like_prose_math_fragment=bindings.looks_like_prose_math_fragment,
        word_count=bindings.word_count,
    )
    should_demote_prose_math_entry_to_paragraph = make_should_demote_prose_math_entry_to_paragraph(
        normalize_paragraph_text=text_helpers.normalize_paragraph_text,
        word_count=bindings.word_count,
        strong_operator_count=bindings.strong_operator_count,
        mathish_ratio=bindings.mathish_ratio,
        math_entry_looks_like_prose=math_entry_looks_like_prose,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        looks_like_prose_paragraph=bindings.looks_like_prose_paragraph,
    )
    should_demote_graphic_math_entry_to_paragraph = make_should_demote_graphic_math_entry_to_paragraph(
        should_demote_prose_math_entry_to_paragraph=should_demote_prose_math_entry_to_paragraph,
    )
    should_drop_display_math_artifact = make_should_drop_display_math_artifact(
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        group_entry_items_are_graphic_only=bindings.group_entry_items_are_graphic_only,
        math_entry_semantic_policy=bindings.math_entry_semantic_policy,
        math_entry_category=bindings.math_entry_category,
    )
    paragraph_block_from_graphic_math_entry = make_paragraph_block_from_graphic_math_entry(
        normalize_paragraph_text=text_helpers.normalize_paragraph_text,
        split_inline_math=bindings.split_inline_math,
        repair_symbolic_ocr_spans=bindings.repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=bindings.extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=bindings.merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=bindings.normalize_inline_math_spans,
        default_review=text_helpers.default_review,
    )
    return ReconcileMathRuntimeHelpers(
        paragraph_block_from_graphic_math_entry=paragraph_block_from_graphic_math_entry,
        should_demote_graphic_math_entry_to_paragraph=should_demote_graphic_math_entry_to_paragraph,
        should_drop_display_math_artifact=should_drop_display_math_artifact,
        match_external_math_entry=make_match_external_math_entry(
            block_source_spans=text_helpers.block_source_spans,
            clean_text=text_helpers.clean_text,
        ),
        overlapping_external_math_entries=make_overlapping_external_math_entries(
            block_source_spans=text_helpers.block_source_spans,
        ),
        trim_embedded_display_math_from_paragraph=make_trim_embedded_display_math_from_paragraph(
            block_source_spans=text_helpers.block_source_spans,
            clean_text=text_helpers.clean_text,
            display_math_prose_cue_re=bindings.display_math_prose_cue_re,
            display_math_resume_re=bindings.display_math_resume_re,
            display_math_start_re=bindings.display_math_start_re,
            mathish_ratio=bindings.mathish_ratio,
            strong_operator_count=bindings.strong_operator_count,
        ),
        looks_like_display_math_echo=make_looks_like_display_math_echo(
            block_source_spans=text_helpers.block_source_spans,
            clean_text=text_helpers.clean_text,
            mathish_ratio=bindings.mathish_ratio,
            strong_operator_count=bindings.strong_operator_count,
            short_word_re=text_helpers.short_word_re,
        ),
    )


__all__ = [
    "ReconcileMathRuntimeHelpers",
    "build_reconcile_math_runtime_helpers",
]
