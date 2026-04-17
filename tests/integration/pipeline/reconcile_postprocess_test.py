import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.block_merging import merge_code_records, merge_paragraph_records
from pipeline.reconcile.math_suppression import (
    looks_like_leading_display_math_echo,
    trim_embedded_display_math_from_paragraph,
)


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 120.0,
    height: float = 12.0,
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
            }
        ],
        "meta": {},
    }


class ReconcilePostprocessTest(unittest.TestCase):
    def test_merge_paragraph_records_keeps_caption_interruption_logic(self) -> None:
        previous = _record(record_type="paragraph", text="This paragraph ends with")
        caption = _record(record_type="caption", text="Figure 4", y0=132.0)
        current = _record(record_type="paragraph", text="a continuation after interruption.", y0=144.0)

        merged = merge_paragraph_records(
            [previous, caption, current],
            clean_text=rb._clean_text,
            block_source_spans=rb._block_source_spans,
            should_merge_paragraph_records=rb._should_merge_paragraph_records,
            table_caption_re=rb.TABLE_CAPTION_RE,
        )

        self.assertEqual(len(merged), 2)
        self.assertEqual(
            merged[0]["text"],
            "This paragraph ends with a continuation after interruption.",
        )

    def test_merge_code_records_preserves_code_joiner(self) -> None:
        first = _record(record_type="code", text="for (i = 0; i < n; ++i)")
        second = _record(record_type="code", text="push(item);", y0=132.0)

        merged = merge_code_records(
            [first, second],
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
        )

        self.assertEqual(len(merged), 1)
        self.assertIn(";;", merged[0]["text"])

    def test_trim_embedded_display_math_from_paragraph_drops_math_tail(self) -> None:
        record = _record(
            record_type="paragraph",
            text="The equations become x = y + z + w + q + r + s + t however the proof continues.",
            y0=200.0,
            height=48.0,
            width=360.0,
        )
        overlapping_math = [
            {
                "kind": "display",
                "source_spans": [
                    {
                        "page": 1,
                        "bbox": {"x0": 120.0, "y0": 228.0, "x1": 320.0, "y1": 244.0, "width": 200.0, "height": 16.0},
                    }
                ],
            }
        ]

        trimmed = trim_embedded_display_math_from_paragraph(
            record["text"],
            record,
            overlapping_math,
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
            display_math_prose_cue_re=rb.DISPLAY_MATH_PROSE_CUE_RE,
            display_math_resume_re=rb.DISPLAY_MATH_RESUME_RE,
            display_math_start_re=rb.DISPLAY_MATH_START_RE,
            mathish_ratio=rb._mathish_ratio,
            strong_operator_count=rb._strong_operator_count,
        )

        self.assertEqual(trimmed, "however the proof continues.")

    def test_looks_like_leading_display_math_echo_detects_formula_prefix(self) -> None:
        self.assertTrue(
            looks_like_leading_display_math_echo(
                "x = y + z + w therefore we continue",
                clean_text=rb._clean_text,
                display_math_prose_cue_re=rb.DISPLAY_MATH_PROSE_CUE_RE,
                mathish_ratio=rb._mathish_ratio,
                strong_operator_count=rb._strong_operator_count,
            )
        )


if __name__ == "__main__":
    unittest.main()
