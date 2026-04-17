import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.heading_promotion import (
    decode_control_heading_label,
    promote_heading_like_records,
    split_embedded_heading_paragraph,
)


def _record(*, text: str, y0: float = 120.0, x0: float = 53.8, width: float = 240.0) -> dict[str, object]:
    return {
        "id": f"r-{y0}-{len(text)}",
        "page": 1,
        "type": "paragraph",
        "text": text,
        "source_spans": [
            {
                "page": 1,
                "bbox": {"x0": x0, "y0": y0, "x1": x0 + width, "y1": y0 + 12.0, "width": width, "height": 12.0},
            }
        ],
        "meta": {},
    }


class HeadingPromotionTest(unittest.TestCase):
    def test_decode_control_heading_label_decodes_control_prefix(self) -> None:
        text = "\x01\x02\x03 Thin Plates"
        self.assertEqual(decode_control_heading_label(text), ("1.3", "Thin Plates"))

    def test_split_embedded_heading_paragraph_extracts_title_and_remainder(self) -> None:
        record = _record(
            text="3 Net Shape Element Associativity We develop a mechanism by which an association can be created and maintained."
        )
        self.assertEqual(
            split_embedded_heading_paragraph(
                record,
                clean_text=rb._clean_text,
                block_source_spans=rb._block_source_spans,
                embedded_heading_prefix_re=rb.EMBEDDED_HEADING_PREFIX_RE,
                normalize_decoded_heading_title=rb._normalize_decoded_heading_title,
                collapse_ocr_split_caps=rb.collapse_ocr_split_caps,
                looks_like_bad_heading=rb.looks_like_bad_heading,
                short_word_re=rb.SHORT_WORD_RE,
            ),
            (
                "3 Net Shape Element Associativity",
                "We develop a mechanism by which an association can be created and maintained.",
            ),
        )

    def test_promote_heading_like_records_promotes_marker_only_abstract(self) -> None:
        promoted = promote_heading_like_records(
            [_record(text="Abstract", width=80.0)],
            clean_text=rb._clean_text,
            block_source_spans=rb._block_source_spans,
            abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
            parse_heading_label=rb.parse_heading_label,
            clean_heading_title=rb.clean_heading_title,
            looks_like_bad_heading=rb.looks_like_bad_heading,
            collapse_ocr_split_caps=rb.collapse_ocr_split_caps,
            decode_control_heading_label=rb._decode_control_heading_label,
            normalize_decoded_heading_title=rb._normalize_decoded_heading_title,
            split_embedded_heading_paragraph=rb._split_embedded_heading_paragraph,
            short_word_re=rb.SHORT_WORD_RE,
        )
        self.assertEqual(promoted[0]["type"], "heading")
        self.assertEqual(promoted[0]["text"], "Abstract")


if __name__ == "__main__":
    unittest.main()
