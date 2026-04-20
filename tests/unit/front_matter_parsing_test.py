import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.front_matter_patterns as fmp
import pipeline.reconcile.shared_patterns as rsp
from pipeline.assembly.front_matter_support import make_bound_front_matter_support_helpers
from pipeline.policies.abstract_quality import abstract_quality_flags
from pipeline.reconcile.front_matter_parsing import (
    looks_like_affiliation,
    make_bound_front_matter_parsing_helpers,
)
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


class FrontMatterParsingTest(unittest.TestCase):
    def test_looks_like_affiliation_matches_institutional_line(self) -> None:
        self.assertTrue(looks_like_affiliation("Department of Computer Science, Example University"))

    def test_looks_like_author_line_rejects_affiliation(self) -> None:
        self.assertFalse(PARSING_HELPERS.looks_like_author_line("Department of Computer Science, Example University"))

    def test_parse_authors_splits_joined_names(self) -> None:
        authors = PARSING_HELPERS.parse_authors("Alice Example and Bob Example")
        self.assertEqual([author["name"] for author in authors], ["Alice Example", "Bob Example"])

    def test_parse_authors_from_citation_line_recovers_multiple_names(self) -> None:
        authors = PARSING_HELPERS.parse_authors_from_citation_line(
            "Smith, J., Jones, B., A Survey of Aspect Graphs (2001).",
            "A Survey of Aspect Graphs",
        )
        names = [author["name"] for author in authors]
        self.assertIn("Smith J.", names)
        self.assertIn("Jones B.", names)

    def test_filter_front_matter_authors_rejects_institutional_noise(self) -> None:
        filtered = PARSING_HELPERS.filter_front_matter_authors(
            [
                {"name": "Alice Example", "affiliation_ids": ["aff-1"]},
                {"name": "Example University", "affiliation_ids": ["aff-1"]},
            ],
        )
        self.assertEqual([author["name"] for author in filtered], ["Alice Example"])

    def test_build_affiliations_for_authors_assigns_per_author_when_counts_match(self) -> None:
        affiliations, author_affiliation_ids = PARSING_HELPERS.build_affiliations_for_authors(
            2,
            ["Department A, University A, City A", "Department B, University B, City B"],
        )
        self.assertEqual(len(affiliations), 2)
        self.assertEqual(author_affiliation_ids, [["aff-1"], ["aff-2"]])


if __name__ == "__main__":
    unittest.main()
