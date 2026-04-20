from __future__ import annotations

from pipeline.reconcile.math_entry_policies import (
    make_group_entry_items_are_graphic_only,
    make_math_entry_looks_like_prose,
    make_paragraph_block_from_graphic_math_entry,
    make_should_demote_graphic_math_entry_to_paragraph,
    make_should_demote_prose_math_entry_to_paragraph,
    make_should_drop_display_math_artifact,
    math_entry_category,
    math_entry_semantic_policy,
)

__all__ = [
    "make_group_entry_items_are_graphic_only",
    "make_math_entry_looks_like_prose",
    "make_paragraph_block_from_graphic_math_entry",
    "make_should_demote_graphic_math_entry_to_paragraph",
    "make_should_demote_prose_math_entry_to_paragraph",
    "make_should_drop_display_math_artifact",
    "math_entry_category",
    "math_entry_semantic_policy",
]
