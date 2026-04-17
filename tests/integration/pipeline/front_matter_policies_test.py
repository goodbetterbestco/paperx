import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.front_matter_policies import (
    is_title_page_metadata_record,
    looks_like_body_section_marker,
    normalize_abstract_candidate_text,
    split_leading_front_matter_records,
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


class FrontMatterPoliciesTest(unittest.TestCase):
    def test_looks_like_body_section_marker_accepts_numbered_heading(self) -> None:
        self.assertTrue(
            looks_like_body_section_marker(
                "2 Methods",
                clean_text=rb._clean_text,
                clean_heading_title=rb.clean_heading_title,
                abstract_marker_only_re=rb.ABSTRACT_MARKER_ONLY_RE,
                abstract_lead_re=rb.ABSTRACT_LEAD_RE,
                looks_like_intro_marker=rb._looks_like_intro_marker,
                normalize_title_key=rb.normalize_title_key,
                parse_heading_label=rb.parse_heading_label,
            )
        )

    def test_normalize_abstract_candidate_text_strips_lead_and_keywords(self) -> None:
        text = normalize_abstract_candidate_text(
            [{"text": "Abstract: A concise summary. Keywords: shape, topology"}],
            clean_text=rb._clean_text,
            preprint_marker_re=rb.PREPRINT_MARKER_RE,
            abstract_lead_re=rb.ABSTRACT_LEAD_RE,
            strip_trailing_abstract_boilerplate=rb._strip_trailing_abstract_boilerplate,
        )
        self.assertEqual(text, "A concise summary.")

    def test_split_leading_front_matter_records_keeps_page_one_tail_after_intro(self) -> None:
        prelude = [
            _record("Synthetic Title", page=1, y0=50.0),
            _record("1 Introduction", page=2, y0=90.0),
            _record("Alice Example", page=1, y0=620.0),
            _record("Real introduction body", page=2, y0=110.0),
        ]

        front, remainder = split_leading_front_matter_records(
            prelude,
            clean_text=rb._clean_text,
            looks_like_intro_marker=rb._looks_like_intro_marker,
            looks_like_page_one_front_matter_tail=rb._looks_like_page_one_front_matter_tail,
        )

        self.assertEqual([r["text"] for r in front], ["Synthetic Title", "Alice Example"])
        self.assertEqual([r["text"] for r in remainder], ["Real introduction body"])

    def test_is_title_page_metadata_record_flags_footer_affiliation(self) -> None:
        record = _record("Department of Computer Science", page=1, y0=650.0)
        self.assertTrue(
            is_title_page_metadata_record(
                record,
                clean_text=rb._clean_text,
                preprint_marker_re=rb.PREPRINT_MARKER_RE,
                looks_like_front_matter_metadata=rb._looks_like_front_matter_metadata,
                author_note_re=rb.AUTHOR_NOTE_RE,
                block_source_spans=rb._block_source_spans,
                looks_like_affiliation=rb._looks_like_affiliation,
                looks_like_contact_name=rb._looks_like_contact_name,
            )
        )


if __name__ == "__main__":
    unittest.main()
