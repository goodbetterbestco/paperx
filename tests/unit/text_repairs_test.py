import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.math.extract import INLINE_MATH_RE
from pipeline.reconcile.runtime_constants import (
    CONTROL_CHAR_RE,
    LABEL_CLOUD_TOKEN_RE,
    MATHPIX_HINT_TOKEN_RE,
    MATH_TOKEN_RE,
    QUOTED_IDENTIFIER_FRAGMENT_RE,
    SHORT_OCR_NOISE_RE,
    TERMINAL_PUNCTUATION_RE,
    TRUNCATED_PROSE_LEAD_STOPWORDS,
)
from pipeline.reconcile.text_repairs import repair_record_text_with_mathpix_hints, repair_record_text_with_pdftotext
from pipeline.reconcile.layout_records import rect_x_overlap_ratio
from pipeline.reconcile.math_fragments_runtime import make_math_signal_count, strong_operator_count
from pipeline.reconcile.screening import (
    make_is_short_ocr_fragment,
    make_looks_like_browser_ui_scrap,
    make_looks_like_glyph_noise_cloud,
    make_looks_like_quoted_identifier_fragment,
    make_looks_like_table_marker_cloud,
    make_looks_like_vertical_label_cloud,
)
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_text,
    make_is_pdftotext_candidate_better,
    make_word_count,
)
from pipeline.reconcile.text_repairs import make_bound_text_repair_helpers
from pipeline.text.headings import compact_text, parse_heading_label
from pipeline.types import LayoutBlock


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
WORD_COUNT = make_word_count(short_word_re=rsp.SHORT_WORD_RE)
IS_PDFTOTEXT_CANDIDATE_BETTER = make_is_pdftotext_candidate_better(
    clean_text=CLEAN_TEXT,
    word_count=WORD_COUNT,
)
LOOKS_LIKE_BROWSER_UI_SCRAP = make_looks_like_browser_ui_scrap(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT = make_looks_like_quoted_identifier_fragment(
    short_word_re=rsp.SHORT_WORD_RE,
    quoted_identifier_fragment_re=QUOTED_IDENTIFIER_FRAGMENT_RE,
)
LOOKS_LIKE_GLYPH_NOISE_CLOUD = make_looks_like_glyph_noise_cloud(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_VERTICAL_LABEL_CLOUD = make_looks_like_vertical_label_cloud(
    strong_operator_count=strong_operator_count,
)
LOOKS_LIKE_TABLE_MARKER_CLOUD = make_looks_like_table_marker_cloud(
    strong_operator_count=strong_operator_count,
)
IS_SHORT_OCR_FRAGMENT = make_is_short_ocr_fragment(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    looks_like_browser_ui_scrap=LOOKS_LIKE_BROWSER_UI_SCRAP,
    looks_like_quoted_identifier_fragment=LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT,
    looks_like_glyph_noise_cloud=LOOKS_LIKE_GLYPH_NOISE_CLOUD,
    looks_like_vertical_label_cloud=LOOKS_LIKE_VERTICAL_LABEL_CLOUD,
    looks_like_table_marker_cloud=LOOKS_LIKE_TABLE_MARKER_CLOUD,
    short_word_re=rsp.SHORT_WORD_RE,
    label_cloud_token_re=LABEL_CLOUD_TOKEN_RE,
    short_ocr_noise_re=SHORT_OCR_NOISE_RE,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    strong_operator_count=strong_operator_count,
)
TEXT_REPAIR_HELPERS = make_bound_text_repair_helpers(
    clean_text=CLEAN_TEXT,
    word_count=WORD_COUNT,
    inline_math_re=INLINE_MATH_RE,
    block_source_spans=block_source_spans,
    bbox_to_line_window=lambda bbox, *, page_height, line_count: (0, 0),
    slice_page_text=lambda lines, *, start_line, end_line: "This OCR text is bad",
    is_pdftotext_candidate_better=IS_PDFTOTEXT_CANDIDATE_BETTER,
    rect_x_overlap_ratio=rect_x_overlap_ratio,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    display_math_start_re=rsp.DISPLAY_MATH_START_RE,
    math_signal_count=make_math_signal_count(math_token_re=MATH_TOKEN_RE),
    hint_token_re=MATHPIX_HINT_TOKEN_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    truncated_prose_lead_stopwords=TRUNCATED_PROSE_LEAD_STOPWORDS,
    parse_heading_label=parse_heading_label,
)


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
            should_skip_pdftotext_repair=TEXT_REPAIR_HELPERS.should_skip_pdftotext_repair,
            block_source_spans=block_source_spans,
            bbox_to_line_window=lambda bbox, *, page_height, line_count: (0, 0),
            slice_page_text=lambda lines, *, start_line, end_line: "This OCR text is bad",
            clean_text=CLEAN_TEXT,
            is_pdftotext_candidate_better=IS_PDFTOTEXT_CANDIDATE_BETTER,
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
            mathpix_text_blocks_by_page=TEXT_REPAIR_HELPERS.mathpix_text_blocks_by_page,
            is_short_ocr_fragment=IS_SHORT_OCR_FRAGMENT,
            mathpix_text_hint_candidate=TEXT_REPAIR_HELPERS.mathpix_text_hint_candidate,
            is_mathpix_text_hint_better=TEXT_REPAIR_HELPERS.is_mathpix_text_hint_better,
            mathpix_prose_lead_repair_candidate=TEXT_REPAIR_HELPERS.mathpix_prose_lead_repair_candidate,
            clean_text=CLEAN_TEXT,
        )

        self.assertEqual(repaired[0]["text"], r"A \mathbf{1} ( B ) \frac{x}{y}")
        self.assertEqual(repaired[0]["meta"]["text_engine"], "mathpix_text_hint")


if __name__ == "__main__":
    unittest.main()
