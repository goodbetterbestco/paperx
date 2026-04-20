import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.assembly.front_matter_support import (
    abstract_text_looks_like_metadata,
    front_block_text,
    make_bound_front_matter_support_helpers,
)
from pipeline.policies.abstract_quality import MISSING_ABSTRACT_PLACEHOLDER, abstract_quality_flags
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_text,
)
from pipeline.text.headings import compact_text, normalize_title_key


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
SUPPORT_HELPERS = make_bound_front_matter_support_helpers(
    clean_text=CLEAN_TEXT,
    normalize_title_key=normalize_title_key,
    compact_text=compact_text,
    short_word_re=rsp.SHORT_WORD_RE,
    block_source_spans=block_source_spans,
    abstract_quality_flags=abstract_quality_flags,
)


class FrontMatterSupportTest(unittest.TestCase):
    def test_title_lookup_keys_strip_year_and_article(self) -> None:
        keys = SUPPORT_HELPERS.title_lookup_keys("2001 The Aspect Graph Survey")

        self.assertIn("2001theaspectgraphsurvey", keys)
        self.assertIn("theaspectgraphsurvey", keys)
        self.assertIn("aspectgraphsurvey", keys)

    def test_matches_title_line_accepts_prefix_match(self) -> None:
        self.assertTrue(
            SUPPORT_HELPERS.matches_title_line(
                "Aspect Graph Survey",
                "The Aspect Graph Survey",
            )
        )

    def test_front_block_text_reads_text_spans_only(self) -> None:
        blocks = [
            {
                "id": "blk-front-abstract-1",
                "content": {
                    "spans": [
                        {"kind": "text", "text": "First part"},
                        {"kind": "math", "text": "x+y"},
                        {"kind": "text", "text": "second part"},
                    ]
                },
            }
        ]

        text = front_block_text(blocks, "blk-front-abstract-1", clean_text=CLEAN_TEXT)

        self.assertEqual(text, "First part second part")

    def test_abstract_text_looks_like_metadata_flags_placeholder(self) -> None:
        self.assertTrue(
            abstract_text_looks_like_metadata(
                MISSING_ABSTRACT_PLACEHOLDER,
                abstract_quality_flags=abstract_quality_flags,
            )
        )


if __name__ == "__main__":
    unittest.main()
