import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
from pipeline.reconcile.math_suppression import suppress_graphic_display_math_blocks
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


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 640.0,
    height: float = 10.0,
    width: float = 240.0,
) -> dict[str, object]:
    return {
        "id": f"{record_type}-{page}-{y0}-{height}-{width}-{len(text)}",
        "page": page,
        "type": record_type,
        "text": text,
        "source_spans": [
            {
                "page": page,
                "bbox": {
                    "x0": 90.0,
                    "y0": y0,
                    "x1": 90.0 + width,
                    "y1": y0 + height,
                    "width": width,
                    "height": height,
                },
                "engine": "docling",
            }
        ],
        "meta": {},
    }


def _suppress_graphic_display_math_blocks(
    blocks: list[dict[str, object]],
    math_entries: list[dict[str, object]],
    sections: list[dict[str, object]],
    counters: dict[str, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    return suppress_graphic_display_math_blocks(
        blocks,
        math_entries,
        sections,
        counters,
        should_demote_graphic_math_entry_to_paragraph=SHOULD_DEMOTE_GRAPHIC_MATH_ENTRY_TO_PARAGRAPH,
        paragraph_block_from_graphic_math_entry=PARAGRAPH_BLOCK_FROM_GRAPHIC_MATH_ENTRY,
        should_drop_display_math_artifact=SHOULD_DROP_DISPLAY_MATH_ARTIFACT,
    )


class DisplayMathSuppressionTest(unittest.TestCase):
    def test_suppress_graphic_display_math_demotes_figure_prose_to_paragraph(self) -> None:
        blocks = [
            {
                "id": "blk-display_equation_ref-0001",
                "type": "display_equation_ref",
                "content": {"math_id": "eq-1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "alternates": [],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        math_entries = [
            {
                "id": "eq-1",
                "kind": "display",
                "display_latex": r"Geometry. The topological entities embed in \( \mathbb{R}^{3} \) (Figure 7).",
                "classification": {
                    "category": "figure_embedded_math",
                    "semantic_policy": "graphic_only",
                    "role": "graphic",
                    "confidence": "medium",
                    "signals": ["figure_embedded_terms"],
                },
                "compiled_targets": {"mathml": "<math />"},
                "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "1 Test",
                "level": 1,
                "block_ids": ["blk-display_equation_ref-0001"],
                "children": [],
                "source_spans": [],
            }
        ]

        rewritten_blocks, rewritten_math, rewritten_sections = _suppress_graphic_display_math_blocks(
            blocks,
            math_entries,
            sections,
            {"block": 2, "math": 2, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(rewritten_blocks[0]["type"], "paragraph")
        self.assertEqual(rewritten_sections[0]["block_ids"], ["blk-display_equation_ref-0001"])
        self.assertEqual({entry["id"] for entry in rewritten_math}, {"math-inline-1"})
        self.assertTrue(any(span.get("kind") == "inline_math_ref" for span in rewritten_blocks[0]["content"]["spans"]))

    def test_suppress_display_math_demotes_low_signal_prose_relation_to_paragraph(self) -> None:
        blocks = [
            {
                "id": "blk-display_equation_ref-0001",
                "type": "display_equation_ref",
                "content": {"math_id": "eq-1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "alternates": [],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        math_entries = [
            {
                "id": "eq-1",
                "kind": "display",
                "display_latex": "The frames are defined so that instantaneously, at time t = 0, they coincide.",
                "classification": {
                    "category": "relation",
                    "semantic_policy": "semantic",
                    "role": "assertion",
                    "confidence": "medium",
                    "signals": ["single_relation"],
                },
                "compiled_targets": {"mathml": "<math />"},
                "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "1 Test",
                "level": 1,
                "block_ids": ["blk-display_equation_ref-0001"],
                "children": [],
                "source_spans": [],
            }
        ]

        rewritten_blocks, rewritten_math, rewritten_sections = _suppress_graphic_display_math_blocks(
            blocks,
            math_entries,
            sections,
            {"block": 2, "math": 2, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(rewritten_blocks[0]["type"], "paragraph")
        paragraph_text = "".join(span.get("text", "") for span in rewritten_blocks[0]["content"]["spans"])
        self.assertIn("The frames are defined so that instantaneously", paragraph_text)
        self.assertEqual(rewritten_sections[0]["block_ids"], ["blk-display_equation_ref-0001"])
        self.assertNotIn("eq-1", {entry["id"] for entry in rewritten_math})

    def test_suppress_display_math_demotes_prose_lead_in_with_trailing_colon(self) -> None:
        blocks = [
            {
                "id": "blk-display_equation_ref-0001",
                "type": "display_equation_ref",
                "content": {"math_id": "eq-1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "alternates": [],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        math_entries = [
            {
                "id": "eq-1",
                "kind": "display",
                "display_latex": r"An abstract \( n \)-polytope is a poset \( (P, \preceq) \), with elements called faces, which satisfies the following properties:",
                "classification": {
                    "category": "unknown",
                    "semantic_policy": "graphic_only",
                    "role": "unknown",
                    "confidence": "low",
                    "signals": ["fallback_unknown"],
                },
                "compiled_targets": {"mathml": "<math />"},
                "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "1 Test",
                "level": 1,
                "block_ids": ["blk-display_equation_ref-0001"],
                "children": [],
                "source_spans": [],
            }
        ]

        rewritten_blocks, rewritten_math, rewritten_sections = _suppress_graphic_display_math_blocks(
            blocks,
            math_entries,
            sections,
            {"block": 2, "math": 2, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(rewritten_blocks[0]["type"], "paragraph")
        paragraph_text = "".join(span.get("text", "") for span in rewritten_blocks[0]["content"]["spans"])
        self.assertIn("An abstract", paragraph_text)
        self.assertTrue(paragraph_text.endswith("properties:"))
        self.assertEqual(rewritten_sections[0]["block_ids"], ["blk-display_equation_ref-0001"])
        self.assertNotIn("eq-1", {entry["id"] for entry in rewritten_math})

    def test_suppress_display_math_demotes_control_flow_prose_with_inline_math(self) -> None:
        blocks = [
            {
                "id": "blk-display_equation_ref-0001",
                "type": "display_equation_ref",
                "content": {"math_id": "eq-1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "alternates": [],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        math_entries = [
            {
                "id": "eq-1",
                "kind": "display",
                "display_latex": r"Else if \( d_{s} \geq d_{t} \), perform Bézier clipping against \( \mathbf{L}=",
                "classification": {
                    "category": "system",
                    "semantic_policy": "semantic",
                    "role": "condition",
                    "confidence": "medium",
                    "signals": ["multiple_relations"],
                },
                "compiled_targets": {"mathml": "<math />"},
                "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "review": {"status": "unreviewed", "risk": "high", "notes": ""},
            }
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "1 Test",
                "level": 1,
                "block_ids": ["blk-display_equation_ref-0001"],
                "children": [],
                "source_spans": [],
            }
        ]

        rewritten_blocks, rewritten_math, rewritten_sections = _suppress_graphic_display_math_blocks(
            blocks,
            math_entries,
            sections,
            {"block": 2, "math": 2, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(rewritten_blocks[0]["type"], "paragraph")
        paragraph_text = "".join(span.get("text", "") for span in rewritten_blocks[0]["content"]["spans"])
        self.assertIn("Else if", paragraph_text)
        self.assertIn("perform B", paragraph_text)
        self.assertEqual(rewritten_sections[0]["block_ids"], ["blk-display_equation_ref-0001"])
        self.assertNotIn("eq-1", {entry["id"] for entry in rewritten_math})

    def test_suppress_graphic_group_math_drops_label_cloud_artifact(self) -> None:
        blocks = [
            {
                "id": "blk-equation_group_ref-0001",
                "type": "equation_group_ref",
                "content": {"math_id": "eq-group-1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "alternates": [],
                "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
            }
        ]
        math_entries = [
            {
                "id": "eq-group-1",
                "kind": "group",
                "display_latex": "Irretrievable Unusable (Errors in model tree) - Incomplete Missing elements",
                "classification": {
                    "category": "derivation_chain",
                    "semantic_policy": "structure_only",
                    "role": "derivation_step",
                    "confidence": "high",
                    "signals": ["group_kind"],
                },
                "compiled_targets": {},
                "conversion": {"status": "failed", "notes": "group items failed=1/1"},
                "source_spans": _record(record_type="paragraph", text="stub")["source_spans"],
                "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                "items": [
                    {
                        "display_latex": "Irretrievable Unusable (Errors in model tree) - Incomplete Missing elements",
                        "classification": {
                            "category": "malformed_math",
                            "semantic_policy": "graphic_only",
                            "role": "graphic",
                            "confidence": "high",
                            "signals": ["conversion_failed"],
                        },
                        "compiled_targets": {},
                        "conversion": {"status": "failed", "notes": "latex2mathml:"},
                        "semantic_expr": None,
                    }
                ],
            }
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "1 Test",
                "level": 1,
                "block_ids": ["blk-equation_group_ref-0001"],
                "children": [],
                "source_spans": [],
            }
        ]

        rewritten_blocks, rewritten_math, rewritten_sections = _suppress_graphic_display_math_blocks(
            blocks,
            math_entries,
            sections,
            {"block": 2, "math": 2, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(rewritten_blocks, [])
        self.assertEqual(rewritten_math, [])
        self.assertEqual(rewritten_sections[0]["block_ids"], [])


if __name__ == "__main__":
    unittest.main()
