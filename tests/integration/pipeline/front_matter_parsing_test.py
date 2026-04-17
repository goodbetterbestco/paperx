import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.front_matter_parsing import (
    build_affiliations_for_authors,
    filter_front_matter_authors,
    looks_like_affiliation,
    looks_like_author_line,
    parse_authors,
    parse_authors_from_citation_line,
)


class FrontMatterParsingTest(unittest.TestCase):
    def test_looks_like_affiliation_matches_institutional_line(self) -> None:
        self.assertTrue(looks_like_affiliation("Department of Computer Science, Example University"))

    def test_looks_like_author_line_rejects_affiliation(self) -> None:
        self.assertFalse(
            looks_like_author_line(
                "Department of Computer Science, Example University",
                looks_like_affiliation=looks_like_affiliation,
                normalize_author_line=lambda text: rb._normalize_author_line(text),
                looks_like_front_matter_metadata=lambda text: rb._looks_like_front_matter_metadata(text),
                reference_venue_re=rb.REFERENCE_VENUE_RE,
                author_token_re=rb.AUTHOR_TOKEN_RE,
            )
        )

    def test_parse_authors_splits_joined_names(self) -> None:
        authors = parse_authors(
            "Alice Example and Bob Example",
            clean_text=rb._clean_text,
            normalize_author_line=rb._normalize_author_line,
        )
        self.assertEqual([author["name"] for author in authors], ["Alice Example", "Bob Example"])

    def test_parse_authors_from_citation_line_recovers_multiple_names(self) -> None:
        authors = parse_authors_from_citation_line(
            "Smith, J., Jones, B., A Survey of Aspect Graphs (2001).",
            "A Survey of Aspect Graphs",
            clean_text=rb._clean_text,
            normalize_title_key=rb.normalize_title_key,
            title_lookup_keys=rb._title_lookup_keys,
            citation_year_re=rb.CITATION_YEAR_RE,
            looks_like_front_matter_metadata=rb._looks_like_front_matter_metadata,
            citation_author_split_re=rb.CITATION_AUTHOR_SPLIT_RE,
            normalize_author_line=rb._normalize_author_line,
            short_word_re=rb.SHORT_WORD_RE,
            looks_like_affiliation=rb._looks_like_affiliation,
        )
        names = [author["name"] for author in authors]
        self.assertIn("Smith J.", names)
        self.assertIn("Jones B.", names)

    def test_filter_front_matter_authors_rejects_institutional_noise(self) -> None:
        filtered = filter_front_matter_authors(
            [
                {"name": "Alice Example", "affiliation_ids": ["aff-1"]},
                {"name": "Example University", "affiliation_ids": ["aff-1"]},
            ],
            normalize_author_line=rb._normalize_author_line,
            short_word_re=rb.SHORT_WORD_RE,
            looks_like_affiliation=rb._looks_like_affiliation,
            looks_like_front_matter_metadata=rb._looks_like_front_matter_metadata,
            dedupe_authors=rb._dedupe_authors,
        )
        self.assertEqual([author["name"] for author in filtered], ["Alice Example"])

    def test_build_affiliations_for_authors_assigns_per_author_when_counts_match(self) -> None:
        affiliations, author_affiliation_ids = build_affiliations_for_authors(
            2,
            ["Department A, University A, City A", "Department B, University B, City B"],
            normalize_affiliation_line=rb._normalize_affiliation_line,
            split_affiliation_fields=rb._split_affiliation_fields,
        )
        self.assertEqual(len(affiliations), 2)
        self.assertEqual(author_affiliation_ids, [["aff-1"], ["aff-2"]])


if __name__ == "__main__":
    unittest.main()
