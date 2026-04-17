import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.external_math import inject_external_math_records, match_external_math_entry
from pipeline.types import LayoutBlock


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
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
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

        combined, injected = inject_external_math_records(
            [],
            layout_blocks,
            external_entries,
            clean_text=rb._clean_text,
            looks_like_leading_display_math_echo=lambda text: rb.reconcile_looks_like_leading_display_math_echo(
                text,
                clean_text=rb._clean_text,
                display_math_prose_cue_re=rb.DISPLAY_MATH_PROSE_CUE_RE,
                mathish_ratio=rb._mathish_ratio,
                strong_operator_count=rb._strong_operator_count,
            ),
        )

        self.assertEqual(injected, {"m1"})
        self.assertEqual(len(combined), 1)
        self.assertEqual(combined[0]["meta"]["forced_math_kind"], "display")


if __name__ == "__main__":
    unittest.main()
