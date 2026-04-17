import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.text_repairs import repair_record_text_with_mathpix_hints, repair_record_text_with_pdftotext
from pipeline.types import LayoutBlock


class TextRepairsTest(unittest.TestCase):
    def test_repair_record_text_with_pdftotext_replaces_cleaner_slice(self) -> None:
        records = [
            {
                "id": "r1",
                "page": 1,
                "group_index": 10,
                "split_index": 1,
                "type": "paragraph",
                "text": "Th1s OCR text is b4d",
                "source_spans": [{"page": 1, "bbox": {"x0": 0.0, "y0": 0.0, "x1": 100.0, "y1": 20.0}}],
                "meta": {},
            }
        ]
        repaired = repair_record_text_with_pdftotext(
            records,
            {1: ["This OCR text is bad"]},
            {1: 100.0},
            should_skip_pdftotext_repair=rb._should_skip_pdftotext_repair,
            block_source_spans=rb._block_source_spans,
            bbox_to_line_window=lambda bbox, *, page_height, line_count: (0, 0),
            slice_page_text=lambda lines, *, start_line, end_line: "This OCR text is bad",
            clean_text=rb._clean_text,
            is_pdftotext_candidate_better=rb._is_pdftotext_candidate_better,
        )

        self.assertEqual(repaired[0]["text"], "This OCR text is bad")
        self.assertEqual(repaired[0]["meta"]["text_engine"], "native_pdf+pdftotext")

    def test_repair_record_text_with_mathpix_hints_promotes_mathpix_candidate(self) -> None:
        records = [
            {
                "id": "r1",
                "page": 1,
                "group_index": 10,
                "split_index": 1,
                "type": "paragraph",
                "text": "A ; 1 ( B and C )",
                "source_spans": [{"page": 1, "bbox": {"x0": 10.0, "y0": 10.0, "x1": 200.0, "y1": 30.0, "width": 190.0, "height": 20.0}}],
                "meta": {},
            }
        ]
        mathpix_layout = {
            "blocks": [
                LayoutBlock(
                    id="mx1",
                    page=1,
                    order=1,
                    text=r"A \mathbf{1} ( B ) \frac{x}{y}",
                    role="paragraph",
                    bbox={"x0": 10.0, "y0": 10.0, "x1": 200.0, "y1": 30.0, "width": 190.0, "height": 20.0},
                    meta={"mathpix_type": "text"},
                )
            ]
        }

        repaired = repair_record_text_with_mathpix_hints(
            records,
            mathpix_layout,
            mathpix_text_blocks_by_page=rb._mathpix_text_blocks_by_page,
            is_short_ocr_fragment=rb._is_short_ocr_fragment,
            mathpix_text_hint_candidate=rb._mathpix_text_hint_candidate,
            is_mathpix_text_hint_better=rb._is_mathpix_text_hint_better,
            mathpix_prose_lead_repair_candidate=rb._mathpix_prose_lead_repair_candidate,
            clean_text=rb._clean_text,
        )

        self.assertEqual(repaired[0]["text"], r"A \mathbf{1} ( B ) \frac{x}{y}")
        self.assertEqual(repaired[0]["meta"]["text_engine"], "mathpix_text_hint")


if __name__ == "__main__":
    unittest.main()
