import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.math_fragments import merge_math_fragment_records


def _record(text: str, *, group_index: int) -> dict[str, object]:
    return {
        "id": f"r-{group_index}",
        "page": 1,
        "group_index": group_index,
        "split_index": 1,
        "type": "paragraph",
        "text": text,
        "source_spans": [{"page": 1, "bbox": {"x0": 90.0, "y0": float(group_index), "x1": 200.0, "y1": float(group_index) + 10.0}}],
        "meta": {},
    }


class MathFragmentsTest(unittest.TestCase):
    def test_merge_math_fragment_records_groups_adjacent_mathish_fragments(self) -> None:
        records = [
            _record("x = y + z", group_index=10),
            _record("Det A", group_index=20),
            _record("( u )", group_index=30),
        ]

        merged = merge_math_fragment_records(
            records,
            looks_like_math_fragment=rb._looks_like_math_fragment,
            clean_text=rb._clean_text,
            record_analysis_text=rb._record_analysis_text,
            math_signal_count=rb._math_signal_count,
            block_source_spans=rb._block_source_spans,
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["meta"]["forced_math_kind"], "display")


if __name__ == "__main__":
    unittest.main()
