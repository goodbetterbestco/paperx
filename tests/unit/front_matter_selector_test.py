import re
import sys
import unittest
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.front_matter_patterns as fmp  # noqa: E402
import pipeline.reconcile.shared_patterns as rsp  # noqa: E402
from pipeline.assembly.front_matter_support import (  # noqa: E402
    missing_front_matter_affiliation,
    missing_front_matter_author,
)
from pipeline.policies.abstract_quality import (  # noqa: E402
    MISSING_ABSTRACT_PLACEHOLDER,
    NO_ABSTRACT_IN_BASE_MATERIAL,
    abstract_quality_flags,
)
from pipeline.reconcile.front_matter_parsing import looks_like_affiliation  # noqa: E402
from pipeline.reconcile.front_matter_parsing_runtime import make_bound_front_matter_parsing_helpers  # noqa: E402
from pipeline.reconcile.front_matter_runtime import make_bound_front_matter_support_helpers  # noqa: E402
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE  # noqa: E402
from pipeline.reconcile.support_binding_runtime import (  # noqa: E402
    block_source_spans,
    make_clean_text,
)
from pipeline.selectors.abstract_selector import collect_abstract_and_funding_records  # noqa: E402
from pipeline.selectors.front_matter_selector import resolve_front_matter_resolution  # noqa: E402
from pipeline.selectors.title_selector import recover_title  # noqa: E402
from pipeline.text.headings import (  # noqa: E402
    clean_heading_title,
    compact_text,
    normalize_title_key,
    parse_heading_label,
)


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
MISSING_FRONT_MATTER_AUTHOR = partial(
    missing_front_matter_author,
    MISSING_ABSTRACT_PLACEHOLDER,
)
MISSING_FRONT_MATTER_AFFILIATION = partial(
    missing_front_matter_affiliation,
    MISSING_ABSTRACT_PLACEHOLDER,
)


class FrontMatterSelectorTest(unittest.TestCase):
    def test_recover_title_selects_front_matter_title(self) -> None:
        title, source = recover_title(
            [
                _record(record_type="front_matter", text="Synthetic Test Paper", width=340.0),
                _record(record_type="front_matter", text="Alice Example", y0=130.0, width=180.0),
            ],
            clean_text=CLEAN_TEXT,
            record_word_count=SUPPORT_HELPERS.record_word_count,
            record_width=SUPPORT_HELPERS.record_width,
            abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
            looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
            author_note_re=fmp.AUTHOR_NOTE_RE,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_intro_marker=lambda text: bool(re.match(r"^\s*1\.?\s*introduction\b", text, re.IGNORECASE)),
            looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
            looks_like_contact_name=PARSING_HELPERS.looks_like_contact_name,
        )

        self.assertEqual(title, "Synthetic Test Paper")
        self.assertEqual(source, "front_matter_records")

    def test_recover_title_extracts_title_from_combined_title_and_byline(self) -> None:
        title, source = recover_title(
            [
                _record(
                    record_type="front_matter",
                    text=(
                        "Geometry -Completeness of Reidemeister-type moves for surfaces "
                        "embedded in three-dimensional space , by Giovanni Bellettini , "
                        "Valentina Beorchia and Maurizio Paolini ."
                    ),
                    width=410.0,
                ),
                _record(record_type="front_matter", text="Abstract.", y0=130.0, width=90.0),
            ],
            clean_text=CLEAN_TEXT,
            record_word_count=SUPPORT_HELPERS.record_word_count,
            record_width=SUPPORT_HELPERS.record_width,
            abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
            looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
            author_note_re=fmp.AUTHOR_NOTE_RE,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_intro_marker=lambda text: bool(re.match(r"^\s*1\.?\s*introduction\b", text, re.IGNORECASE)),
            looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
            looks_like_contact_name=PARSING_HELPERS.looks_like_contact_name,
        )

        self.assertEqual(title, "Completeness of Reidemeister-type moves for surfaces embedded in three-dimensional space")
        self.assertEqual(source, "front_matter_combined_byline")

    def test_collect_abstract_and_funding_records_extracts_inline_abstract(self) -> None:
        abstract_records, funding_records = collect_abstract_and_funding_records(
            [
                _record(record_type="front_matter", text="Abstract: This paper presents a compact summary of a synthetic test."),
                _record(record_type="front_matter", text="Supported in part by Test Funding.", y0=130.0),
                _record(record_type="heading", text="1 Introduction", y0=170.0),
            ],
            allow_fallback=False,
            title="Synthetic Test Paper",
            clean_text=CLEAN_TEXT,
            normalize_title_key=normalize_title_key,
            clone_record_with_text=SUPPORT_HELPERS.clone_record_with_text,
            record_word_count=SUPPORT_HELPERS.record_word_count,
            matches_title_line=SUPPORT_HELPERS.matches_title_line,
            looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
            abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
            preprint_marker_re=fmp.PREPRINT_MARKER_RE,
            keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
            looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
            author_note_re=fmp.AUTHOR_NOTE_RE,
            funding_re=fmp.FUNDING_RE,
            abstract_text_is_usable=PARSING_HELPERS.abstract_text_is_usable,
            normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
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
            clean_text=CLEAN_TEXT,
            matches_title_line=SUPPORT_HELPERS.matches_title_line,
            looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
            author_note_re=fmp.AUTHOR_NOTE_RE,
            looks_like_affiliation=looks_like_affiliation,
            looks_like_affiliation_continuation=PARSING_HELPERS.looks_like_affiliation_continuation,
            looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
            looks_like_contact_name=PARSING_HELPERS.looks_like_contact_name,
            funding_re=fmp.FUNDING_RE,
            dedupe_text_lines=SUPPORT_HELPERS.dedupe_text_lines,
            filter_front_matter_authors=PARSING_HELPERS.filter_front_matter_authors,
            parse_authors=PARSING_HELPERS.parse_authors,
            parse_authors_from_citation_line=PARSING_HELPERS.parse_authors_from_citation_line,
            normalize_author_line=PARSING_HELPERS.normalize_author_line,
            missing_front_matter_author=MISSING_FRONT_MATTER_AUTHOR,
            build_affiliations_for_authors=lambda author_count, affiliation_lines: (
                [{"id": "aff-1", "department": affiliation_lines[0] if affiliation_lines else "", "institution": "", "address": ""}],
                [["aff-1"] for _ in range(author_count)],
            ),
            missing_front_matter_affiliation=MISSING_FRONT_MATTER_AFFILIATION,
            strip_author_prefix_from_affiliation_line=PARSING_HELPERS.strip_author_prefix_from_affiliation_line,
            normalize_title_key=normalize_title_key,
            clone_record_with_text=SUPPORT_HELPERS.clone_record_with_text,
            record_word_count=SUPPORT_HELPERS.record_word_count,
            looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
            abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
            preprint_marker_re=fmp.PREPRINT_MARKER_RE,
            keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
            abstract_text_is_usable=PARSING_HELPERS.abstract_text_is_usable,
            normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
        )

        self.assertEqual([author["name"] for author in resolution.authors], ["Alice Example", "Bob Example"])
        self.assertEqual(resolution.abstract_source, "front_matter_records")
        self.assertEqual(len(resolution.abstract_records), 1)


if __name__ == "__main__":
    unittest.main()
