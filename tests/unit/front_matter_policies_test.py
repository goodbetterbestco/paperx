import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.front_matter_patterns as fmp
import pipeline.reconcile.shared_patterns as rsp
from pipeline.policies.abstract_quality import abstract_quality_flags
from pipeline.reconcile.front_matter_parsing import looks_like_affiliation
from pipeline.reconcile.front_matter_parsing_runtime import make_bound_front_matter_parsing_helpers
from pipeline.reconcile.front_matter_runtime import make_bound_front_matter_support_helpers
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_text,
)
from pipeline.text.headings import (
    clean_heading_title,
    compact_text,
    normalize_title_key,
    parse_heading_label,
)


def _record(text: str, *, page: int = 1, y0: float = 120.0) -> dict[str, object]:
    return {
        "id": f"r-{page}-{y0}-{len(text)}",
        "page": page,
        "type": "paragraph",
        "text": text,
        "source_spans": [{"page": page, "bbox": {"x0": 90.0, "y0": y0, "x1": 200.0, "y1": y0 + 10.0, "width": 110.0, "height": 10.0}}],
        "meta": {},
    }


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
PARSING_HELPERS = make_bound_front_matter_parsing_helpers(
    clean_text=CLEAN_TEXT,
    compact_text=compact_text,
    normalize_title_key=normalize_title_key,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    block_source_spans=block_source_spans,
    title_lookup_keys=SUPPORT_HELPERS.title_lookup_keys,
    abstract_quality_flags=abstract_quality_flags,
    looks_like_affiliation=looks_like_affiliation,
    author_marker_re=fmp.AUTHOR_MARKER_RE,
    author_affiliation_index_re=fmp.AUTHOR_AFFILIATION_INDEX_RE,
    name_token_re=fmp.NAME_TOKEN_RE,
    abbreviated_venue_line_re=fmp.ABBREVIATED_VENUE_LINE_RE,
    title_page_metadata_re=fmp.TITLE_PAGE_METADATA_RE,
    front_matter_metadata_re=fmp.FRONT_MATTER_METADATA_RE,
    reference_venue_re=fmp.REFERENCE_VENUE_RE,
    author_token_re=fmp.AUTHOR_TOKEN_RE,
    intro_marker_re=fmp.INTRO_MARKER_RE,
    abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    trailing_abstract_boilerplate_re=fmp.TRAILING_ABSTRACT_BOILERPLATE_RE,
    trailing_abstract_tail_re=fmp.TRAILING_ABSTRACT_TAIL_RE,
    preprint_marker_re=fmp.PREPRINT_MARKER_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    citation_year_re=fmp.CITATION_YEAR_RE,
    citation_author_split_re=fmp.CITATION_AUTHOR_SPLIT_RE,
)


class FrontMatterPoliciesTest(unittest.TestCase):
    def test_looks_like_body_section_marker_accepts_numbered_heading(self) -> None:
        self.assertTrue(PARSING_HELPERS.looks_like_body_section_marker("2 Methods"))

    def test_normalize_abstract_candidate_text_strips_lead_and_keywords(self) -> None:
        text = PARSING_HELPERS.normalize_abstract_candidate_text(
            [{"text": "Abstract: A concise summary. Keywords: shape, topology"}]
        )
        self.assertEqual(text, "A concise summary.")

    def test_split_leading_front_matter_records_keeps_page_one_tail_after_intro(self) -> None:
        prelude = [
            _record("Synthetic Title", page=1, y0=50.0),
            _record("1 Introduction", page=2, y0=90.0),
            _record("Alice Example", page=1, y0=620.0),
            _record("Real introduction body", page=2, y0=110.0),
        ]

        front, remainder = PARSING_HELPERS.split_leading_front_matter_records(prelude)

        self.assertEqual([r["text"] for r in front], ["Synthetic Title", "Alice Example"])
        self.assertEqual([r["text"] for r in remainder], ["Real introduction body"])

    def test_is_title_page_metadata_record_flags_footer_affiliation(self) -> None:
        record = _record("Department of Computer Science", page=1, y0=650.0)
        self.assertTrue(PARSING_HELPERS.is_title_page_metadata_record(record))


if __name__ == "__main__":
    unittest.main()
