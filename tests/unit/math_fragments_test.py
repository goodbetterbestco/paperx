import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.math import looks_like_prose_paragraph
from pipeline.reconcile.math_fragments_runtime import (
    make_looks_like_math_fragment,
    make_math_signal_count,
    make_merge_math_fragment_records,
)
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE, MATH_TOKEN_RE
from pipeline.reconcile.runtime_support import block_source_spans
from pipeline.reconcile.text_cleaning import make_clean_text, make_record_analysis_text
from pipeline.text.headings import compact_text


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
RECORD_ANALYSIS_TEXT = make_record_analysis_text(clean_text=CLEAN_TEXT)
MATH_SIGNAL_COUNT = make_math_signal_count(math_token_re=MATH_TOKEN_RE)
LOOKS_LIKE_MATH_FRAGMENT = make_looks_like_math_fragment(
    record_analysis_text=RECORD_ANALYSIS_TEXT,
    looks_like_prose_paragraph=looks_like_prose_paragraph,
    short_word_re=rsp.SHORT_WORD_RE,
    math_token_re=MATH_TOKEN_RE,
)
MERGE_MATH_FRAGMENT_RECORDS = make_merge_math_fragment_records(
    looks_like_math_fragment=LOOKS_LIKE_MATH_FRAGMENT,
    clean_text=CLEAN_TEXT,
    record_analysis_text=RECORD_ANALYSIS_TEXT,
    math_signal_count=MATH_SIGNAL_COUNT,
    block_source_spans=block_source_spans,
)


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

        merged = MERGE_MATH_FRAGMENT_RECORDS(records)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["meta"]["forced_math_kind"], "display")


if __name__ == "__main__":
    unittest.main()
