import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb  # noqa: E402
from pipeline.reconcile.front_matter_parsing import (  # noqa: E402
    filter_front_matter_authors,
    looks_like_affiliation,
    looks_like_affiliation_continuation,
    looks_like_author_line,
    looks_like_contact_name,
    looks_like_front_matter_metadata,
    normalize_author_line,
    parse_authors,
    parse_authors_from_citation_line,
    strip_author_prefix_from_affiliation_line,
)
from pipeline.reconcile.front_matter_policies import (  # noqa: E402
    abstract_text_is_usable,
    looks_like_body_section_marker,
    normalize_abstract_candidate_text,
)
from pipeline.assembly.front_matter_support import (  # noqa: E402
    clone_record_with_text,
    dedupe_text_lines,
    matches_title_line,
    missing_front_matter_affiliation,
    missing_front_matter_author,
    record_width,
    record_word_count,
    title_lookup_keys,
)
from pipeline.selectors.abstract_selector import collect_abstract_and_funding_records  # noqa: E402
from pipeline.selectors.front_matter_selector import resolve_front_matter_resolution  # noqa: E402
from pipeline.selectors.title_selector import recover_title  # noqa: E402
from pipeline.text_utils import normalize_title_key  # noqa: E402


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 100.0,
    width: float = 280.0,
    height: float = 16.0,
) -> dict[str, object]:
    return {
        "id": f"{record_type}-{page}-{y0}-{width}-{len(text)}",
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


class FrontMatterSelectorTest(unittest.TestCase):
    def test_recover_title_selects_front_matter_title(self) -> None:
        title, source = recover_title(
            [
                _record(record_type="front_matter", text="Synthetic Test Paper", width=340.0),
                _record(record_type="front_matter", text="Alice Example", y0=130.0, width=180.0),
            ],
            clean_text=rb._clean_text,
            record_word_count=lambda record: record_word_count(record, clean_text=rb._clean_text, short_word_re=rb.SHORT_WORD_RE),
            record_width=lambda record: record_width(record, block_source_spans=rb._block_source_spans),
            abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=rb.ABSTRACT_LEAD_RE,
            looks_like_front_matter_metadata=lambda text: looks_like_front_matter_metadata(
                text,
                clean_text=rb._clean_text,
                abbreviated_venue_line_re=rb.ABBREVIATED_VENUE_LINE_RE,
                title_page_metadata_re=rb.TITLE_PAGE_METADATA_RE,
                front_matter_metadata_re=rb.FRONT_MATTER_METADATA_RE,
            ),
            author_note_re=rb.AUTHOR_NOTE_RE,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_intro_marker=lambda text: bool(re.match(r"^\s*1\.?\s*introduction\b", text, re.IGNORECASE)),
            looks_like_author_line=lambda text: looks_like_author_line(
                text,
                looks_like_affiliation=looks_like_affiliation,
                normalize_author_line=lambda inner: normalize_author_line(
                    inner,
                    clean_text=rb._clean_text,
                    author_marker_re=rb.AUTHOR_MARKER_RE,
                    author_affiliation_index_re=rb.AUTHOR_AFFILIATION_INDEX_RE,
                    compact_text=rb.compact_text,
                ),
                looks_like_front_matter_metadata=lambda inner: looks_like_front_matter_metadata(
                    inner,
                    clean_text=rb._clean_text,
                    abbreviated_venue_line_re=rb.ABBREVIATED_VENUE_LINE_RE,
                    title_page_metadata_re=rb.TITLE_PAGE_METADATA_RE,
                    front_matter_metadata_re=rb.FRONT_MATTER_METADATA_RE,
                ),
                reference_venue_re=rb.REFERENCE_VENUE_RE,
                author_token_re=rb.AUTHOR_TOKEN_RE,
            ),
            looks_like_contact_name=lambda text: looks_like_contact_name(text, clean_text=rb._clean_text, name_token_re=rb.NAME_TOKEN_RE),
        )

        self.assertEqual(title, "Synthetic Test Paper")
        self.assertEqual(source, "front_matter_records")

    def test_collect_abstract_and_funding_records_extracts_inline_abstract(self) -> None:
        abstract_records, funding_records = collect_abstract_and_funding_records(
            [
                _record(record_type="front_matter", text="Abstract: This paper presents a compact summary of a synthetic test."),
                _record(record_type="front_matter", text="Supported in part by Test Funding.", y0=130.0),
                _record(record_type="heading", text="1 Introduction", y0=170.0),
            ],
            allow_fallback=False,
            title="Synthetic Test Paper",
            clean_text=rb._clean_text,
            normalize_title_key=normalize_title_key,
            clone_record_with_text=lambda record, text: clone_record_with_text(record, text, clean_text=rb._clean_text),
            record_word_count=lambda record: record_word_count(record, clean_text=rb._clean_text, short_word_re=rb.SHORT_WORD_RE),
            matches_title_line=lambda text, title: matches_title_line(
                text, title,
                clean_text=rb._clean_text, compact_text=rb.compact_text, short_word_re=rb.SHORT_WORD_RE,
                normalize_title_key=normalize_title_key,
                title_lookup_keys=lambda item: title_lookup_keys(item, clean_text=rb._clean_text, normalize_title_key=normalize_title_key),
            ),
            looks_like_body_section_marker=lambda text: looks_like_body_section_marker(
                text,
                clean_text=rb._clean_text,
                clean_heading_title=rb.clean_heading_title,
                abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
                abstract_lead_re=rb.ABSTRACT_LEAD_RE,
                looks_like_intro_marker=lambda inner: rb._looks_like_intro_marker(inner),
                normalize_title_key=normalize_title_key,
                parse_heading_label=rb.parse_heading_label,
            ),
            abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=rb.ABSTRACT_LEAD_RE,
            preprint_marker_re=rb.PREPRINT_MARKER_RE,
            keywords_lead_re=rb.KEYWORDS_LEAD_RE,
            looks_like_author_line=lambda text: rb._looks_like_author_line(text),
            looks_like_affiliation=looks_like_affiliation,
            looks_like_front_matter_metadata=lambda text: rb._looks_like_front_matter_metadata(text),
            author_note_re=rb.AUTHOR_NOTE_RE,
            funding_re=rb.FUNDING_RE,
            abstract_text_is_usable=lambda text: abstract_text_is_usable(text, abstract_quality_flags=rb.abstract_quality_flags),
            normalize_abstract_candidate_text=lambda records: normalize_abstract_candidate_text(
                records,
                clean_text=rb._clean_text,
                preprint_marker_re=rb.PREPRINT_MARKER_RE,
                abstract_lead_re=rb.ABSTRACT_LEAD_RE,
                strip_trailing_abstract_boilerplate=rb._strip_trailing_abstract_boilerplate,
            ),
        )

        self.assertEqual(len(abstract_records), 1)
        self.assertIn("compact summary", str(abstract_records[0]["text"]))
        self.assertEqual(len(funding_records), 1)

    def test_resolve_front_matter_resolution_prefers_page_one_authors(self) -> None:
        page_one_clean_records = [
            _record(record_type="front_matter", text="Synthetic Test Paper", width=340.0),
            _record(record_type="front_matter", text="Alice Example", y0=130.0, width=170.0),
            _record(record_type="front_matter", text="Bob Example", y0=150.0, width=170.0),
            _record(record_type="front_matter", text="Department of Computing, Test Lab", y0=170.0, width=260.0),
            _record(record_type="front_matter", text="Abstract", y0=210.0, width=90.0),
            _record(
                record_type="front_matter",
                text="This paper presents a compact abstract for selector-level testing.",
                y0=230.0,
                width=360.0,
            ),
        ]

        resolution = resolve_front_matter_resolution(
            content_records=page_one_clean_records,
            leading_boundary_index=4,
            page_one_clean_records=page_one_clean_records,
            page_one_content_start_index=1,
            page_one_boundary_index=4,
            title="Synthetic Test Paper",
            clean_text=rb._clean_text,
            matches_title_line=lambda text, title: rb._matches_title_line(text, title),
            looks_like_front_matter_metadata=lambda text: rb._looks_like_front_matter_metadata(text),
            author_note_re=rb.AUTHOR_NOTE_RE,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_affiliation_continuation=lambda text: looks_like_affiliation_continuation(
                text,
                clean_text=rb._clean_text,
                looks_like_front_matter_metadata=lambda inner: rb._looks_like_front_matter_metadata(inner),
                short_word_re=rb.SHORT_WORD_RE,
            ),
            looks_like_author_line=lambda text: rb._looks_like_author_line(text),
            looks_like_contact_name=lambda text: looks_like_contact_name(text, clean_text=rb._clean_text, name_token_re=rb.NAME_TOKEN_RE),
            funding_re=rb.FUNDING_RE,
            dedupe_text_lines=lambda lines: dedupe_text_lines(lines, clean_text=rb._clean_text, normalize_title_key=normalize_title_key),
            filter_front_matter_authors=lambda authors: filter_front_matter_authors(
                authors,
                normalize_author_line=lambda text: rb._normalize_author_line(text),
                short_word_re=rb.SHORT_WORD_RE,
                looks_like_affiliation=looks_like_affiliation,
                looks_like_front_matter_metadata=lambda text: rb._looks_like_front_matter_metadata(text),
                dedupe_authors=lambda authors: rb._dedupe_authors(authors),
            ),
            parse_authors=lambda text: parse_authors(text, clean_text=rb._clean_text, normalize_author_line=lambda inner: rb._normalize_author_line(inner)),
            parse_authors_from_citation_line=lambda text, title: parse_authors_from_citation_line(
                text, title,
                clean_text=rb._clean_text,
                normalize_title_key=normalize_title_key,
                title_lookup_keys=lambda item: title_lookup_keys(item, clean_text=rb._clean_text, normalize_title_key=normalize_title_key),
                citation_year_re=rb.CITATION_YEAR_RE,
                looks_like_front_matter_metadata=lambda inner: rb._looks_like_front_matter_metadata(inner),
                citation_author_split_re=rb.CITATION_AUTHOR_SPLIT_RE,
                normalize_author_line=lambda inner: rb._normalize_author_line(inner),
                short_word_re=rb.SHORT_WORD_RE,
                looks_like_affiliation=looks_like_affiliation,
            ),
            normalize_author_line=lambda text: rb._normalize_author_line(text),
            missing_front_matter_author=lambda: missing_front_matter_author(rb.MISSING_ABSTRACT_PLACEHOLDER),
            build_affiliations_for_authors=lambda author_count, affiliation_lines: (
                [{"id": "aff-1", "department": affiliation_lines[0] if affiliation_lines else "", "institution": "", "address": ""}],
                [["aff-1"] for _ in range(author_count)],
            ),
            missing_front_matter_affiliation=lambda: missing_front_matter_affiliation(rb.MISSING_ABSTRACT_PLACEHOLDER),
            strip_author_prefix_from_affiliation_line=lambda text, authors: strip_author_prefix_from_affiliation_line(
                text, authors, clean_text=rb._clean_text, normalize_author_line=lambda inner: rb._normalize_author_line(inner)
            ),
            normalize_title_key=normalize_title_key,
            clone_record_with_text=lambda record, text: clone_record_with_text(record, text, clean_text=rb._clean_text),
            record_word_count=lambda record: record_word_count(record, clean_text=rb._clean_text, short_word_re=rb.SHORT_WORD_RE),
            looks_like_body_section_marker=lambda text: rb._looks_like_body_section_marker(text),
            abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=rb.ABSTRACT_LEAD_RE,
            preprint_marker_re=rb.PREPRINT_MARKER_RE,
            keywords_lead_re=rb.KEYWORDS_LEAD_RE,
            abstract_text_is_usable=lambda text: abstract_text_is_usable(text, abstract_quality_flags=rb.abstract_quality_flags),
            normalize_abstract_candidate_text=lambda records: normalize_abstract_candidate_text(
                records,
                clean_text=rb._clean_text,
                preprint_marker_re=rb.PREPRINT_MARKER_RE,
                abstract_lead_re=rb.ABSTRACT_LEAD_RE,
                strip_trailing_abstract_boilerplate=rb._strip_trailing_abstract_boilerplate,
            ),
        )

        self.assertEqual([author["name"] for author in resolution.authors], ["Alice Example", "Bob Example"])
        self.assertEqual(resolution.abstract_source, "front_matter_records")
        self.assertEqual(len(resolution.abstract_records), 1)


if __name__ == "__main__":
    unittest.main()
