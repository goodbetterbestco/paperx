import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.assembly.abstract_recovery import recover_missing_front_matter_abstract as _assembly_recover_missing_front_matter_abstract
from pipeline.assembly.front_matter_builder import build_front_matter as _assembly_build_front_matter
from pipeline.assembly.front_matter_support import front_block_text as _support_front_block_text
from pipeline.assembly.section_support import normalize_section_title as _section_normalize_section_title
from pipeline.text_utils import SectionNode


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


def _split_leading_front_matter_records(
    prelude: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return rb.reconcile_split_leading_front_matter_records(
        prelude,
        clean_text=rb._clean_text,
        looks_like_intro_marker=rb._looks_like_intro_marker,
        looks_like_page_one_front_matter_tail=rb._looks_like_page_one_front_matter_tail,
    )


def _normalize_section_title(title: str) -> str:
    return _section_normalize_section_title(
        title,
        clean_text=rb._clean_text,
        clean_heading_title=rb.clean_heading_title,
        parse_heading_label=rb.parse_heading_label,
        normalize_title_key=rb.normalize_title_key,
    )


def _front_block_text(blocks: list[dict[str, object]], block_id: str | None) -> str:
    return _support_front_block_text(blocks, block_id, clean_text=rb._clean_text)


def _build_front_matter(
    paper_id: str,
    prelude: list[dict[str, object]],
    page_one_records: list[dict[str, object]],
    blocks: list[dict[str, object]],
    next_block_index: int,
) -> tuple[dict[str, object], list[dict[str, object]], int, list[dict[str, object]]]:
    return _assembly_build_front_matter(
        paper_id,
        prelude,
        page_one_records,
        blocks,
        next_block_index,
        split_leading_front_matter_records=_split_leading_front_matter_records,
        clean_record=rb._clean_record,
        clean_text=rb._clean_text,
        record_word_count=rb._record_word_count,
        record_width=rb._record_width,
        abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
        abstract_lead_re=rb.ABSTRACT_LEAD_RE,
        looks_like_front_matter_metadata=rb._looks_like_front_matter_metadata,
        author_note_re=rb.AUTHOR_NOTE_RE,
        looks_like_affiliation=rb._looks_like_affiliation,
        looks_like_intro_marker=rb._looks_like_intro_marker,
        looks_like_author_line=rb._looks_like_author_line,
        looks_like_contact_name=rb._looks_like_contact_name,
        matches_title_line=rb._matches_title_line,
        looks_like_affiliation_continuation=rb._looks_like_affiliation_continuation,
        funding_re=rb.FUNDING_RE,
        dedupe_text_lines=rb._dedupe_text_lines,
        filter_front_matter_authors=rb._filter_front_matter_authors,
        parse_authors=rb._parse_authors,
        parse_authors_from_citation_line=rb._parse_authors_from_citation_line,
        normalize_author_line=rb._normalize_author_line,
        missing_front_matter_author=rb._missing_front_matter_author,
        build_affiliations_for_authors=rb._build_affiliations_for_authors,
        missing_front_matter_affiliation=rb._missing_front_matter_affiliation,
        strip_author_prefix_from_affiliation_line=rb._strip_author_prefix_from_affiliation_line,
        normalize_title_key=rb.normalize_title_key,
        clone_record_with_text=rb._clone_record_with_text,
        looks_like_body_section_marker=rb._looks_like_body_section_marker,
        preprint_marker_re=rb.PREPRINT_MARKER_RE,
        keywords_lead_re=rb.KEYWORDS_LEAD_RE,
        abstract_text_is_usable=rb._abstract_text_is_usable,
        normalize_abstract_candidate_text=rb._normalize_abstract_candidate_text,
        default_review=rb.default_review,
        block_source_spans=rb._block_source_spans,
        front_matter_missing_placeholder=rb.MISSING_ABSTRACT_PLACEHOLDER,
    )


def _recover_missing_front_matter_abstract(
    front_matter: dict[str, object],
    blocks: list[dict[str, object]],
    prelude: list[dict[str, object]],
    ordered_roots: list[SectionNode],
) -> bool:
    return _assembly_recover_missing_front_matter_abstract(
        front_matter,
        blocks,
        prelude,
        ordered_roots,
        front_block_text=_front_block_text,
        abstract_quality_flags=rb.abstract_quality_flags,
        normalize_section_title=_normalize_section_title,
        leading_abstract_text=rb._leading_abstract_text,
        abstract_text_is_recoverable=rb._abstract_text_is_recoverable,
        replace_front_matter_abstract_text=rb._replace_front_matter_abstract_text,
        opening_abstract_candidate_records=rb._opening_abstract_candidate_records,
        normalize_abstract_candidate_text=rb._normalize_abstract_candidate_text,
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
        self.assertTrue(rb._should_replace_front_matter_abstract("[missing from original]"))

    def test_should_replace_front_matter_abstract_for_metadata_noise(self) -> None:
        self.assertTrue(
            rb._should_replace_front_matter_abstract(
                "This manuscript version is made available under the CC-BY-NC-ND 4.0 license."
            )
        )

    def test_should_not_replace_front_matter_abstract_for_valid_text(self) -> None:
        self.assertFalse(
            rb._should_replace_front_matter_abstract(
                "This paper gives a concise abstract that should be preserved."
            )
        )

    def test_strip_trailing_abstract_boilerplate_removes_keywords_and_copyright(self) -> None:
        cleaned = rb._strip_trailing_abstract_boilerplate(
            "A concise abstract. © 2000 Elsevier Science Ltd. All rights reserved. Keywords: one; two"
        )
        self.assertEqual(cleaned, "A concise abstract.")

    def test_strip_trailing_abstract_boilerplate_removes_subject_classification_and_intro(self) -> None:
        cleaned = rb._strip_trailing_abstract_boilerplate(
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

        text, records = rb._leading_abstract_text(node)

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

        text, records = rb._leading_abstract_text(node)

        self.assertIn("viewpoint partitions", text)
        self.assertNotIn("A number of researchers", text)
        self.assertEqual(len(records), 2)

    def test_recovers_missing_abstract_from_inline_prelude_and_keywords(self) -> None:
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
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=60.0, height=16.0, width=240.0),
            _record(record_type="front_matter", text="This paper studies model repair for invalid boundary representations, focusing on practical recovery strategies for defective CAD data exchange pipelines.", page=1, y0=120.0, height=18.0, width=360.0),
            _record(record_type="front_matter", text="Keywords: boundary representation; model repair", page=1, y0=145.0, height=12.0, width=260.0),
        ]

        replaced = _recover_missing_front_matter_abstract(front_matter, blocks, prelude, [])

        self.assertTrue(replaced)
        self.assertIn("This paper studies model repair", blocks[0]["content"]["spans"][0]["text"])

    def test_build_front_matter_uses_page_one_records_for_missing_abstract(self) -> None:
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
