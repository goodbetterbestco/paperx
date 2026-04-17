import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.math_suppression import suppress_graphic_display_math_blocks


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
        should_demote_graphic_math_entry_to_paragraph=rb._should_demote_graphic_math_entry_to_paragraph,
        paragraph_block_from_graphic_math_entry=rb._paragraph_block_from_graphic_math_entry,
        should_drop_display_math_artifact=rb._should_drop_display_math_artifact,
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
