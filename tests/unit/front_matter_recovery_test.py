import sys
import unittest
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.front_matter_patterns as fmp
import pipeline.reconcile.shared_patterns as rsp
from pipeline.assembly.abstract_recovery import (
    make_bound_front_matter_recovery_helpers,
    make_recover_missing_front_matter_abstract,
    recover_missing_front_matter_abstract as _assembly_recover_missing_front_matter_abstract,
)
from pipeline.assembly.front_matter_builder import (
    build_front_matter as _assembly_build_front_matter,
    make_build_front_matter,
)
from pipeline.assembly.front_matter_support import (
    front_block_text as _support_front_block_text,
    make_bound_front_matter_support_helpers,
    make_front_block_text,
    missing_front_matter_affiliation,
    missing_front_matter_author,
)
from pipeline.assembly.section_support import (
    make_normalize_section_title,
    normalize_section_title as _section_normalize_section_title,
)
from pipeline.policies.abstract_quality import (
    MISSING_ABSTRACT_PLACEHOLDER,
    NO_ABSTRACT_IN_BASE_MATERIAL,
    abstract_quality_flags,
)
from pipeline.reconcile.front_matter_parsing import (
    looks_like_affiliation,
    make_bound_front_matter_parsing_helpers,
)
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_record,
    make_clean_text,
    make_strip_known_running_header_text,
)
from pipeline.types import default_review
from pipeline.text.headings import SectionNode
from pipeline.text.headings import clean_heading_title, compact_text, normalize_title_key, parse_heading_label


def _review(risk: str = "medium", status: str = "unreviewed") -> dict[str, str]:
    return {"risk": risk, "status": status, "notes": ""}


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 640.0,
    height: float = 10.0,
    width: float = 240.0,
) -> dict[str, object]:
    return {
        "id": f"{record_type}-{page}-{y0}-{height}-{width}-{len(text)}",
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
                "engine": "docling",
            }
        ],
        "meta": {},
    }


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
STRIP_KNOWN_RUNNING_HEADER_TEXT = make_strip_known_running_header_text(
    procedia_running_header_re=rsp.PROCEDIA_RUNNING_HEADER_RE,
    clean_text=CLEAN_TEXT,
)
CLEAN_RECORD = make_clean_record(
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
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
RECOVERY_HELPERS = make_bound_front_matter_recovery_helpers(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    abstract_quality_flags=abstract_quality_flags,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    normalize_title_key=normalize_title_key,
    looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
    looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
    keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    abstract_body_break_re=fmp.ABSTRACT_BODY_BREAK_RE,
    figure_ref_re=fmp.FIGURE_REF_RE,
    abstract_continuation_re=fmp.ABSTRACT_CONTINUATION_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    record_word_count=SUPPORT_HELPERS.record_word_count,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
)
MISSING_FRONT_MATTER_AUTHOR = partial(
    missing_front_matter_author,
    MISSING_ABSTRACT_PLACEHOLDER,
)
MISSING_FRONT_MATTER_AFFILIATION = partial(
    missing_front_matter_affiliation,
    MISSING_ABSTRACT_PLACEHOLDER,
)
SPLIT_LEADING_FRONT_MATTER_RECORDS = PARSING_HELPERS.split_leading_front_matter_records
NORMALIZE_SECTION_TITLE = make_normalize_section_title(
    normalize_section_title_impl=_section_normalize_section_title,
    clean_text=CLEAN_TEXT,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    normalize_title_key=normalize_title_key,
)
FRONT_BLOCK_TEXT = make_front_block_text(
    front_block_text_impl=_support_front_block_text,
    clean_text=CLEAN_TEXT,
)
BUILD_FRONT_MATTER = make_build_front_matter(
    build_front_matter_impl=_assembly_build_front_matter,
    split_leading_front_matter_records=SPLIT_LEADING_FRONT_MATTER_RECORDS,
    clean_record=CLEAN_RECORD,
    clean_text=CLEAN_TEXT,
    record_word_count=SUPPORT_HELPERS.record_word_count,
    record_width=SUPPORT_HELPERS.record_width,
    abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    looks_like_affiliation=looks_like_affiliation,
    looks_like_intro_marker=PARSING_HELPERS.looks_like_intro_marker,
    looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
    looks_like_contact_name=PARSING_HELPERS.looks_like_contact_name,
    matches_title_line=SUPPORT_HELPERS.matches_title_line,
    looks_like_affiliation_continuation=PARSING_HELPERS.looks_like_affiliation_continuation,
    funding_re=fmp.FUNDING_RE,
    dedupe_text_lines=SUPPORT_HELPERS.dedupe_text_lines,
    filter_front_matter_authors=PARSING_HELPERS.filter_front_matter_authors,
    parse_authors=PARSING_HELPERS.parse_authors,
    parse_authors_from_citation_line=PARSING_HELPERS.parse_authors_from_citation_line,
    normalize_author_line=PARSING_HELPERS.normalize_author_line,
    missing_front_matter_author=MISSING_FRONT_MATTER_AUTHOR,
    build_affiliations_for_authors=PARSING_HELPERS.build_affiliations_for_authors,
    missing_front_matter_affiliation=MISSING_FRONT_MATTER_AFFILIATION,
    strip_author_prefix_from_affiliation_line=PARSING_HELPERS.strip_author_prefix_from_affiliation_line,
    normalize_title_key=normalize_title_key,
    clone_record_with_text=SUPPORT_HELPERS.clone_record_with_text,
    looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
    preprint_marker_re=fmp.PREPRINT_MARKER_RE,
    keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
    abstract_text_is_usable=PARSING_HELPERS.abstract_text_is_usable,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
    default_review=default_review,
    block_source_spans=block_source_spans,
    front_matter_missing_placeholder=NO_ABSTRACT_IN_BASE_MATERIAL,
)
RECOVER_MISSING_FRONT_MATTER_ABSTRACT = make_recover_missing_front_matter_abstract(
    recover_missing_front_matter_abstract_impl=_assembly_recover_missing_front_matter_abstract,
    front_block_text=FRONT_BLOCK_TEXT,
    abstract_quality_flags=abstract_quality_flags,
    normalize_section_title=NORMALIZE_SECTION_TITLE,
    leading_abstract_text=RECOVERY_HELPERS.leading_abstract_text,
    abstract_text_is_recoverable=RECOVERY_HELPERS.abstract_text_is_recoverable,
    replace_front_matter_abstract_text=RECOVERY_HELPERS.replace_front_matter_abstract_text,
    opening_abstract_candidate_records=RECOVERY_HELPERS.opening_abstract_candidate_records,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
)


def _split_leading_front_matter_records(
    prelude: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return SPLIT_LEADING_FRONT_MATTER_RECORDS(prelude)


def _normalize_section_title(title: str) -> str:
    return NORMALIZE_SECTION_TITLE(title)


def _front_block_text(blocks: list[dict[str, object]], block_id: str | None) -> str:
    return FRONT_BLOCK_TEXT(blocks, block_id)


def _build_front_matter(
    paper_id: str,
    prelude: list[dict[str, object]],
    page_one_records: list[dict[str, object]],
    blocks: list[dict[str, object]],
    next_block_index: int,
) -> tuple[dict[str, object], list[dict[str, object]], int, list[dict[str, object]]]:
    return BUILD_FRONT_MATTER(
        paper_id,
        prelude,
        page_one_records,
        blocks,
        next_block_index,
    )


def _recover_missing_front_matter_abstract(
    front_matter: dict[str, object],
    blocks: list[dict[str, object]],
    prelude: list[dict[str, object]],
    ordered_roots: list[SectionNode],
) -> bool:
    return RECOVER_MISSING_FRONT_MATTER_ABSTRACT(
        front_matter,
        blocks,
        prelude,
        ordered_roots,
    )


class FrontMatterRecoveryTest(unittest.TestCase):
    def test_build_front_matter_requires_title_metadata(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Missing recoverable title"):
            _build_front_matter(
                "2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities",
                [],
                [],
                [],
                1,
            )

    def test_build_front_matter_emits_debug_decisions(self) -> None:
        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_title_and_abstract_paper",
            [
                _record(record_type="front_matter", text="Synthetic Test Paper", width=320.0, y0=60.0),
                _record(record_type="front_matter", text="Alice Example", width=180.0, y0=95.0),
                _record(record_type="front_matter", text="Abstract", width=90.0, y0=130.0),
                _record(
                    record_type="front_matter",
                    text="This paper presents a compact abstract for a synthetic regression test.",
                    width=360.0,
                    y0=150.0,
                ),
            ],
            [],
            [],
            1,
        )

        self.assertEqual(front_matter["title"], "Synthetic Test Paper")
        self.assertEqual(front_matter["_debug_title_decision"]["selected_text"], "Synthetic Test Paper")
        self.assertEqual(front_matter["_debug_abstract_decision"]["source"], "front_matter_records")
        self.assertFalse(front_matter["_debug_abstract_decision"]["placeholder"])
        self.assertEqual(len(blocks), 1)
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_should_replace_front_matter_abstract_for_missing_placeholder(self) -> None:
        self.assertTrue(SUPPORT_HELPERS.should_replace_front_matter_abstract("[missing from original]"))

    def test_should_replace_front_matter_abstract_for_metadata_noise(self) -> None:
        self.assertTrue(
            SUPPORT_HELPERS.should_replace_front_matter_abstract(
                "This manuscript version is made available under the CC-BY-NC-ND 4.0 license."
            )
        )

    def test_should_not_replace_front_matter_abstract_for_valid_text(self) -> None:
        self.assertFalse(
            SUPPORT_HELPERS.should_replace_front_matter_abstract(
                "This paper gives a concise abstract that should be preserved."
            )
        )

    def test_strip_trailing_abstract_boilerplate_removes_keywords_and_copyright(self) -> None:
        cleaned = PARSING_HELPERS.strip_trailing_abstract_boilerplate(
            "A concise abstract. © 2000 Elsevier Science Ltd. All rights reserved. Keywords: one; two"
        )
        self.assertEqual(cleaned, "A concise abstract.")

    def test_strip_trailing_abstract_boilerplate_removes_subject_classification_and_intro(self) -> None:
        cleaned = PARSING_HELPERS.strip_trailing_abstract_boilerplate(
            "A concise abstract. ACM Subject Classification I.3.5 Computational Geometry 1 Introduction Body text"
        )
        self.assertEqual(cleaned, "A concise abstract.")

    def test_recovers_missing_abstract_from_nonfirst_abstract_root(self) -> None:
        front_matter = {"abstract_block_id": "blk-front-abstract-1"}
        blocks = [
            {
                "id": "blk-front-abstract-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                "source_spans": [],
                "alternates": [],
                "review": _review(risk="low", status="edited"),
            }
        ]
        abstract_record = _record(
            record_type="paragraph",
            text="A proper abstract appears under the abstract heading.",
            page=1,
            y0=140.0,
            height=18.0,
            width=320.0,
        )
        roots = [
            SectionNode(title="J.H Rieger*", level=1, heading_id="sec-author", records=[]),
            SectionNode(title="Abstract", level=1, heading_id="sec-abstract", records=[abstract_record]),
        ]

        replaced = _recover_missing_front_matter_abstract(front_matter, blocks, [], roots)

        self.assertTrue(replaced)
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], "A proper abstract appears under the abstract heading.")

    def test_leading_abstract_text_stops_at_next_heading(self) -> None:
        node = SectionNode(
            title="Abstract",
            level=1,
            heading_id="sec-abstract",
            records=[
                _record(record_type="paragraph", text="This paper presents a concise abstract that should be preserved as the abstract text.", page=2, y0=120.0, height=18.0, width=340.0),
                _record(record_type="paragraph", text="Some non-simple curves are more non-simple than others.", page=2, y0=150.0, height=18.0, width=340.0),
                _record(record_type="heading", text="DEFINITIONS", page=2, y0=190.0, height=12.0, width=120.0),
            ],
        )

        text, records = RECOVERY_HELPERS.leading_abstract_text(node)

        self.assertIn("concise abstract", text)
        self.assertNotIn("Some non-simple curves", text)
        self.assertEqual(len(records), 1)

    def test_leading_abstract_text_stops_before_later_page_jump(self) -> None:
        node = SectionNode(
            title="Abstract",
            level=1,
            heading_id="sec-abstract",
            records=[
                _record(record_type="paragraph", text="This paper studies viewpoint partitions and aspect graphs for polyhedra under changing viewpoint.", page=3, y0=120.0, height=18.0, width=340.0),
                _record(record_type="footnote", text="* This work was supported in part by the NSF.", page=3, y0=160.0, height=12.0, width=320.0),
                _record(record_type="paragraph", text="A number of researchers in computer vision have suggested a characteristic-view approach.", page=7, y0=120.0, height=18.0, width=360.0),
            ],
        )

        text, records = RECOVERY_HELPERS.leading_abstract_text(node)

        self.assertIn("viewpoint partitions", text)
        self.assertNotIn("A number of researchers", text)
        self.assertEqual(len(records), 2)

    def test_does_not_recover_missing_abstract_from_inline_prelude_and_keywords(self) -> None:
        front_matter = {"abstract_block_id": "blk-front-abstract-1"}
        blocks = [
            {
                "id": "blk-front-abstract-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": MISSING_ABSTRACT_PLACEHOLDER}]},
                "source_spans": [],
                "alternates": [],
                "review": _review(risk="low", status="edited"),
            }
        ]
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=60.0, height=16.0, width=240.0),
            _record(record_type="front_matter", text="This paper studies model repair for invalid boundary representations, focusing on practical recovery strategies for defective CAD data exchange pipelines.", page=1, y0=120.0, height=18.0, width=360.0),
            _record(record_type="front_matter", text="Keywords: boundary representation; model repair", page=1, y0=145.0, height=12.0, width=260.0),
        ]

        replaced = _recover_missing_front_matter_abstract(front_matter, blocks, prelude, [])

        self.assertFalse(replaced)
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], MISSING_ABSTRACT_PLACEHOLDER)

    def test_build_front_matter_uses_page_one_abstract_anchor_for_missing_abstract(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="CAD and the Product Master Model", page=1, y0=40.0, width=300.0),
            _record(record_type="paragraph", text="1 Introduction", page=2, y0=90.0, width=160.0),
            _record(record_type="paragraph", text="There is a long-standing interest in product data bases.", page=2, y0=110.0, width=320.0),
        ]
        page_one_records = [
            _record(record_type="paragraph", text="CAD and the Product Master Model", page=1, y0=40.0, width=300.0),
            _record(record_type="paragraph", text="Christoph M. Hoffmann", page=1, y0=70.0, width=180.0),
            _record(record_type="paragraph", text="Department of Computer Sciences", page=1, y0=88.0, width=220.0),
            _record(record_type="paragraph", text="Purdue University", page=1, y0=102.0, width=180.0),
            _record(record_type="paragraph", text="Abstract", page=1, y0=124.0, width=70.0),
            _record(record_type="paragraph", text="We develop an architecture for a product master model that federates CAD systems.", page=1, y0=140.0, width=360.0),
        ]

        front_matter, blocks, _, remaining = _build_front_matter(
            "1998_cad_and_the_product_master_model",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Christoph M. Hoffmann"])
        self.assertEqual(front_matter["affiliations"][0]["department"], "Department of Computer Sciences")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["text"], "There is a long-standing interest in product data bases.")
        abstract_block = next(block for block in blocks if block["id"] == front_matter["abstract_block_id"])
        self.assertIn("We develop an architecture", abstract_block["content"]["spans"][0]["text"])


if __name__ == "__main__":
    unittest.main()
