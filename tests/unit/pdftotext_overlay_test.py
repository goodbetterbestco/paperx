from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.sources.pdftotext_overlay import (
    candidate_text_for_block,
    clean_text,
    is_better_candidate,
    overlay_pdftotext_onto_layout,
    should_skip_repair,
)
from pipeline.types import LayoutBlock


class PdftotextOverlayTest(unittest.TestCase):
    def test_should_skip_repair_for_heading_and_inline_math_paragraphs(self) -> None:
        heading = LayoutBlock(id="b1", page=1, order=1, text="1 Introduction", role="heading", bbox={})
        inline_math = LayoutBlock(id="b2", page=1, order=2, text=r"The cost is \(O(n)\).", role="paragraph", bbox={})
        symbolic = LayoutBlock(id="b3", page=1, order=3, text="a = b + c - d", role="paragraph", bbox={})
        plain = LayoutBlock(id="b4", page=1, order=4, text="This paragraph needs cleanup.", role="paragraph", bbox={})

        self.assertTrue(should_skip_repair(heading))
        self.assertTrue(should_skip_repair(inline_math))
        self.assertTrue(should_skip_repair(symbolic))
        self.assertFalse(should_skip_repair(plain))

    def test_candidate_text_for_block_uses_bbox_window_and_cleans_text(self) -> None:
        block = LayoutBlock(
            id="b1",
            page=1,
            order=1,
            text="orig",
            role="paragraph",
            bbox={"y0": 100.0, "y1": 220.0},
        )

        candidate = candidate_text_for_block(
            block,
            page_lines=["Header", "  repaired  text  ", "with tail", "Footer"],
            page_height=800.0,
        )

        self.assertEqual(candidate, "Header repaired text with tail")

    def test_is_better_candidate_rejects_short_or_unrelated_replacements(self) -> None:
        block = LayoutBlock(id="b1", page=1, order=1, text="Stable paragraph with useful tokens", role="paragraph", bbox={})

        self.assertFalse(is_better_candidate(block, ""))
        self.assertFalse(is_better_candidate(block, "12"))
        self.assertFalse(is_better_candidate(block, "totally unrelated glyph cloud"))
        self.assertTrue(is_better_candidate(block, "Stable paragraph with repaired useful tokens"))

    def test_overlay_pdftotext_onto_layout_repairs_only_better_candidates(self) -> None:
        native_layout = {
            "engine": "native_pdf",
            "pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 612.0, "height": 792.0}],
            "blocks": [
                LayoutBlock(
                    id="b1",
                    page=1,
                    order=1,
                    text="This paragraph has br0ken OCR tok3ns",
                    role="paragraph",
                    bbox={"y0": 120.0, "y1": 180.0},
                    meta={},
                ),
                LayoutBlock(
                    id="b2",
                    page=1,
                    order=2,
                    text="1 Introduction",
                    role="heading",
                    bbox={"y0": 200.0, "y1": 230.0},
                    meta={},
                ),
                LayoutBlock(
                    id="b3",
                    page=1,
                    order=3,
                    text="Another stable paragraph",
                    role="paragraph",
                    bbox={"y0": 594.0, "y1": 792.0},
                    meta={},
                ),
            ],
        }
        pages = {
            1: [
                "",
                "This paragraph has broken OCR tokens",
                "",
                "Another stable paragraph",
            ]
        }

        with (
            patch("pipeline.sources.pdftotext_overlay.extract_layout", return_value=native_layout),
            patch("pipeline.sources.pdftotext_overlay.extract_pdftotext_pages", return_value=pages),
        ):
            overlay, summary = overlay_pdftotext_onto_layout("1990_synthetic_test_paper")

        self.assertEqual(summary, {"changed_blocks": 1, "skipped_blocks": 1, "total_blocks": 3})
        self.assertEqual(overlay["engine"], "pdftotext_overlay")
        self.assertEqual(overlay["blocks"][0]["text"], "This paragraph has broken OCR tokens")
        self.assertEqual(overlay["blocks"][0]["meta"]["native_text"], "This paragraph has br0ken OCR tok3ns")
        self.assertEqual(overlay["blocks"][0]["meta"]["text_engine"], "native_pdf+pdftotext")
        self.assertEqual(overlay["blocks"][1]["text"], "1 Introduction")
        self.assertEqual(overlay["blocks"][2]["text"], "Another stable paragraph")

    def test_clean_text_removes_control_characters(self) -> None:
        self.assertEqual(clean_text("A\u0000 noisy\x07 line"), "A noisy line")


if __name__ == "__main__":
    unittest.main()
