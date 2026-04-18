import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.math import (
    extract_general_inline_math_spans,
    looks_like_prose_math_fragment,
    looks_like_prose_paragraph,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    split_inline_math,
)
from pipeline.math.extract import repair_symbolic_ocr_spans
from pipeline.reconcile.math_entry_binding_runtime import (
    make_group_entry_items_are_graphic_only,
    make_math_entry_looks_like_prose,
    make_paragraph_block_from_graphic_math_entry,
    make_should_demote_graphic_math_entry_to_paragraph,
    make_should_demote_prose_math_entry_to_paragraph,
    make_should_drop_display_math_artifact,
    math_entry_category,
    math_entry_semantic_policy,
)
from pipeline.reconcile.math_fragments_runtime import make_math_signal_count, strong_operator_count
from pipeline.reconcile.runtime_constants import (
    CONTROL_CHAR_RE,
    LEADING_NEGATIONSLASH_ARTIFACT_RE,
    LEADING_OCR_MARKER_RE,
    LEADING_PUNCT_ARTIFACT_RE,
    LEADING_VAR_ARTIFACT_RE,
    MATH_TOKEN_RE,
    TRAILING_NUMERIC_ARTIFACT_RE,
)
from pipeline.reconcile.support_binding_runtime import (
    make_clean_text,
    make_mathish_ratio,
    make_normalize_paragraph_text,
    make_strip_known_running_header_text,
    make_word_count,
)
from pipeline.text.headings import compact_text
from pipeline.text.prose import normalize_prose_text
from pipeline.types import default_review


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
STRIP_KNOWN_RUNNING_HEADER_TEXT = make_strip_known_running_header_text(
    procedia_running_header_re=rsp.PROCEDIA_RUNNING_HEADER_RE,
    clean_text=CLEAN_TEXT,
)
NORMALIZE_PARAGRAPH_TEXT = make_normalize_paragraph_text(
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
    leading_negationslash_artifact_re=LEADING_NEGATIONSLASH_ARTIFACT_RE,
    leading_ocr_marker_re=LEADING_OCR_MARKER_RE,
    leading_punct_artifact_re=LEADING_PUNCT_ARTIFACT_RE,
    leading_var_artifact_re=LEADING_VAR_ARTIFACT_RE,
    trailing_numeric_artifact_re=TRAILING_NUMERIC_ARTIFACT_RE,
    normalize_prose_text=lambda text: normalize_prose_text(text, layout=None),
    clean_text=CLEAN_TEXT,
)
WORD_COUNT = make_word_count(short_word_re=rsp.SHORT_WORD_RE)
MATHISH_RATIO = make_mathish_ratio(
    word_count=WORD_COUNT,
    math_signal_count=make_math_signal_count(math_token_re=MATH_TOKEN_RE),
)
MATH_ENTRY_LOOKS_LIKE_PROSE = make_math_entry_looks_like_prose(
    normalize_paragraph_text=NORMALIZE_PARAGRAPH_TEXT,
    looks_like_prose_paragraph=looks_like_prose_paragraph,
    looks_like_prose_math_fragment=looks_like_prose_math_fragment,
    word_count=WORD_COUNT,
)
SHOULD_DEMOTE_PROSE_MATH_ENTRY_TO_PARAGRAPH = make_should_demote_prose_math_entry_to_paragraph(
    normalize_paragraph_text=NORMALIZE_PARAGRAPH_TEXT,
    word_count=WORD_COUNT,
    strong_operator_count=strong_operator_count,
    mathish_ratio=MATHISH_RATIO,
    math_entry_looks_like_prose=MATH_ENTRY_LOOKS_LIKE_PROSE,
    math_entry_semantic_policy=math_entry_semantic_policy,
    looks_like_prose_paragraph=looks_like_prose_paragraph,
)
GROUP_ENTRY_ITEMS_ARE_GRAPHIC_ONLY = make_group_entry_items_are_graphic_only(
    math_entry_semantic_policy=math_entry_semantic_policy,
)
SHOULD_DEMOTE_GRAPHIC_MATH_ENTRY_TO_PARAGRAPH = make_should_demote_graphic_math_entry_to_paragraph(
    should_demote_prose_math_entry_to_paragraph=SHOULD_DEMOTE_PROSE_MATH_ENTRY_TO_PARAGRAPH,
)
SHOULD_DROP_DISPLAY_MATH_ARTIFACT = make_should_drop_display_math_artifact(
    should_demote_graphic_math_entry_to_paragraph=SHOULD_DEMOTE_GRAPHIC_MATH_ENTRY_TO_PARAGRAPH,
    group_entry_items_are_graphic_only=GROUP_ENTRY_ITEMS_ARE_GRAPHIC_ONLY,
    math_entry_semantic_policy=math_entry_semantic_policy,
    math_entry_category=math_entry_category,
)
PARAGRAPH_BLOCK_FROM_GRAPHIC_MATH_ENTRY = make_paragraph_block_from_graphic_math_entry(
    normalize_paragraph_text=NORMALIZE_PARAGRAPH_TEXT,
    split_inline_math=split_inline_math,
    repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
    extract_general_inline_math_spans=extract_general_inline_math_spans,
    merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
    normalize_inline_math_spans=normalize_inline_math_spans,
    default_review=default_review,
)


class MathEntryPoliciesTest(unittest.TestCase):
    def test_should_demote_prose_math_entry_to_paragraph_for_control_flow_prose(self) -> None:
        entry = {
            "kind": "display",
            "display_latex": "Else if d_s >= d_t, perform Bezier clipping against L =",
            "classification": {"semantic_policy": "semantic", "category": "system"},
        }

        self.assertTrue(SHOULD_DEMOTE_PROSE_MATH_ENTRY_TO_PARAGRAPH(entry))

    def test_should_drop_display_math_artifact_for_graphic_group(self) -> None:
        entry = {
            "kind": "group",
            "classification": {"semantic_policy": "structure_only", "category": "derivation_chain"},
            "items": [
                {"classification": {"semantic_policy": "graphic_only", "category": "malformed_math"}},
            ],
        }

        self.assertTrue(SHOULD_DROP_DISPLAY_MATH_ARTIFACT(entry))

    def test_paragraph_block_from_graphic_math_entry_creates_paragraph_block(self) -> None:
        block = {
            "id": "blk-display_equation_ref-0001",
            "source_spans": [{"page": 1, "bbox": {"x0": 90.0, "y0": 100.0, "x1": 200.0, "y1": 120.0}}],
            "alternates": [],
        }
        entry = {"display_latex": "The frames coincide at time t = 0 and x = y."}
        paragraph_block, inline_math_entries = PARAGRAPH_BLOCK_FROM_GRAPHIC_MATH_ENTRY(
            block,
            entry,
            {"inline_math": 1},
        )

        self.assertEqual(paragraph_block["type"], "paragraph")
        self.assertEqual(paragraph_block["source_spans"], block["source_spans"])
        self.assertIsInstance(paragraph_block["content"]["spans"], list)
        self.assertIsInstance(inline_math_entries, list)


if __name__ == "__main__":
    unittest.main()
