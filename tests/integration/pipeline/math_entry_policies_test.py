import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.math_entry_policies import (
    paragraph_block_from_graphic_math_entry,
    should_demote_prose_math_entry_to_paragraph,
    should_drop_display_math_artifact,
)


class MathEntryPoliciesTest(unittest.TestCase):
    def test_should_demote_prose_math_entry_to_paragraph_for_control_flow_prose(self) -> None:
        entry = {
            "kind": "display",
            "display_latex": "Else if d_s >= d_t, perform Bezier clipping against L =",
            "classification": {"semantic_policy": "semantic", "category": "system"},
        }

        self.assertTrue(
            should_demote_prose_math_entry_to_paragraph(
                entry,
                normalize_paragraph_text=rb._normalize_paragraph_text,
                word_count=rb._word_count,
                strong_operator_count=rb._strong_operator_count,
                mathish_ratio=rb._mathish_ratio,
                math_entry_looks_like_prose=rb._math_entry_looks_like_prose,
                math_entry_semantic_policy=rb._math_entry_semantic_policy,
                looks_like_prose_paragraph=rb.looks_like_prose_paragraph,
            )
        )

    def test_should_drop_display_math_artifact_for_graphic_group(self) -> None:
        entry = {
            "kind": "group",
            "classification": {"semantic_policy": "structure_only", "category": "derivation_chain"},
            "items": [
                {"classification": {"semantic_policy": "graphic_only", "category": "malformed_math"}},
            ],
        }

        self.assertTrue(
            should_drop_display_math_artifact(
                entry,
                should_demote_graphic_math_entry_to_paragraph=rb._should_demote_graphic_math_entry_to_paragraph,
                group_entry_items_are_graphic_only=rb._group_entry_items_are_graphic_only,
                math_entry_semantic_policy=rb._math_entry_semantic_policy,
                math_entry_category=rb._math_entry_category,
            )
        )

    def test_paragraph_block_from_graphic_math_entry_creates_paragraph_block(self) -> None:
        block = {
            "id": "blk-display_equation_ref-0001",
            "source_spans": [{"page": 1, "bbox": {"x0": 90.0, "y0": 100.0, "x1": 200.0, "y1": 120.0}}],
            "alternates": [],
        }
        entry = {"display_latex": "The frames coincide at time t = 0 and x = y."}
        paragraph_block, inline_math_entries = paragraph_block_from_graphic_math_entry(
            block,
            entry,
            {"inline_math": 1},
            normalize_paragraph_text=rb._normalize_paragraph_text,
            split_inline_math=rb.split_inline_math,
            repair_symbolic_ocr_spans=rb.repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=rb.extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=rb.merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=rb.normalize_inline_math_spans,
            default_review=rb.default_review,
        )

        self.assertEqual(paragraph_block["type"], "paragraph")
        self.assertEqual(paragraph_block["source_spans"], block["source_spans"])
        self.assertIsInstance(paragraph_block["content"]["spans"], list)
        self.assertIsInstance(inline_math_entries, list)


if __name__ == "__main__":
    unittest.main()
