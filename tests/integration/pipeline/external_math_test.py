import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.reconcile.external_math import match_external_math_entry
from pipeline.reconcile.external_math_binding_runtime import make_inject_external_math_records
from pipeline.reconcile.math_fragments_runtime import make_math_signal_count, strong_operator_count
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE, MATH_TOKEN_RE
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_text,
    make_mathish_ratio,
    make_word_count,
)
from pipeline.text.headings import compact_text
from pipeline.types import LayoutBlock


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
WORD_COUNT = make_word_count(short_word_re=rsp.SHORT_WORD_RE)
MATHISH_RATIO = make_mathish_ratio(
    word_count=WORD_COUNT,
    math_signal_count=make_math_signal_count(math_token_re=MATH_TOKEN_RE),
)
INJECT_EXTERNAL_MATH_RECORDS = make_inject_external_math_records(
    clean_text=CLEAN_TEXT,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    mathish_ratio=MATHISH_RATIO,
    strong_operator_count=strong_operator_count,
)


def _record(text: str) -> dict[str, object]:
    return {
        "id": "rec-1",
        "page": 1,
        "type": "paragraph",
        "text": text,
        "source_spans": [
            {
                "page": 1,
                "bbox": {"x0": 100.0, "y0": 120.0, "x1": 300.0, "y1": 140.0, "width": 200.0, "height": 20.0},
            }
        ],
        "meta": {},
    }


class ExternalMathTest(unittest.TestCase):
    def test_match_external_math_entry_prefers_exact_overlap(self) -> None:
        external_by_page = {
            1: [
                {
                    "id": "m1",
                    "kind": "display",
                    "display_latex": "x = y + z",
                    "source_spans": [
                        {
                            "page": 1,
                            "bbox": {"x0": 100.0, "y0": 120.0, "x1": 300.0, "y1": 140.0, "width": 200.0, "height": 20.0},
                        }
                    ],
                }
            ]
        }

        matched = match_external_math_entry(
            _record("x = y + z"),
            external_by_page,
            block_source_spans=block_source_spans,
            clean_text=CLEAN_TEXT,
        )

        self.assertIsNotNone(matched)
        self.assertEqual(matched["id"], "m1")
        self.assertEqual(external_by_page[1], [])

    def test_inject_external_math_records_forces_display_kind_when_not_prose(self) -> None:
        layout_blocks = [
            LayoutBlock(
                id="blk-1",
                page=1,
                order=1,
                text="x = y + z therefore continue",
                role="paragraph",
                bbox={"x0": 90.0, "y0": 100.0, "x1": 320.0, "y1": 120.0, "width": 230.0, "height": 20.0},
                engine="docling",
                meta={},
            )
        ]
        external_entries = [
            {
                "id": "m1",
                "kind": "display",
                "display_latex": "x = y + z",
                "source_spans": [
                    {
                        "page": 1,
                        "bbox": {"x0": 100.0, "y0": 108.0, "x1": 300.0, "y1": 132.0, "width": 200.0, "height": 24.0},
                    }
                ],
            }
        ]

        combined, injected = INJECT_EXTERNAL_MATH_RECORDS(
            [],
            layout_blocks,
            external_entries,
        )

        self.assertEqual(injected, {"m1"})
        self.assertEqual(len(combined), 1)
        self.assertEqual(combined[0]["meta"]["forced_math_kind"], "display")


if __name__ == "__main__":
    unittest.main()
