import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.assembly.front_matter_support import (
    abstract_text_looks_like_metadata,
    front_block_text,
    matches_title_line,
    title_lookup_keys,
)


class FrontMatterSupportTest(unittest.TestCase):
    def test_title_lookup_keys_strip_year_and_article(self) -> None:
        keys = title_lookup_keys(
            "2001 The Aspect Graph Survey",
            clean_text=rb._clean_text,
            normalize_title_key=rb.normalize_title_key,
        )

        self.assertIn("2001theaspectgraphsurvey", keys)
        self.assertIn("theaspectgraphsurvey", keys)
        self.assertIn("aspectgraphsurvey", keys)

    def test_matches_title_line_accepts_prefix_match(self) -> None:
        self.assertTrue(
            matches_title_line(
                "Aspect Graph Survey",
                "The Aspect Graph Survey",
                clean_text=rb._clean_text,
                compact_text=rb.compact_text,
                short_word_re=rb.SHORT_WORD_RE,
                normalize_title_key=rb.normalize_title_key,
                title_lookup_keys=rb._title_lookup_keys,
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

        text = front_block_text(blocks, "blk-front-abstract-1", clean_text=rb._clean_text)

        self.assertEqual(text, "First part second part")

    def test_abstract_text_looks_like_metadata_flags_placeholder(self) -> None:
        self.assertTrue(
            abstract_text_looks_like_metadata(
                rb.MISSING_ABSTRACT_PLACEHOLDER,
                abstract_quality_flags=rb.abstract_quality_flags,
            )
        )


if __name__ == "__main__":
    unittest.main()
