import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.reconcile.section_preparation import (  # noqa: E402
    attach_orphan_numbered_roots,
    flatten_sections,
    prepare_section_nodes,
)
from pipeline.text.headings import SectionNode  # noqa: E402


class SectionPreparationTest(unittest.TestCase):
    def test_attach_orphan_numbered_roots_claims_intro_children(self) -> None:
        roots = [
            SectionNode(title="Introduction", level=1, heading_id="sec-intro", records=[], children=[]),
            SectionNode(title="Motivation", level=2, heading_id="sec-1-1", label=("1", "1"), records=[], children=[]),
        ]

        adjusted = attach_orphan_numbered_roots(roots)

        self.assertEqual(len(adjusted), 1)
        self.assertEqual(adjusted[0].label, ("1",))
        self.assertEqual(len(adjusted[0].children), 1)

    def test_prepare_section_nodes_synthesizes_references_from_tail(self) -> None:
        roots = [
            SectionNode(
                title="Results",
                level=1,
                heading_id="sec-results",
                records=[
                    {"text": "Body text"},
                    {"text": "[1] Alice, Example Journal, 2020."},
                    {"text": "[2] Bob, Example Journal, 2021."},
                    {"text": "[3] Carol, Example Journal, 2022."},
                    {"text": "[4] Dan, Example Journal, 2023."},
                    {"text": "[5] Eve, Example Journal, 2024."},
                ],
                children=[],
            )
        ]

        section_nodes = prepare_section_nodes(
            ordered_roots=roots,
            normalize_section_title=lambda title: title.strip().lower(),
            split_trailing_reference_records=lambda records: (records[:1], records[1:]) if len(records) >= 6 else (records, []),
            extract_reference_records_from_tail_section=lambda records: (records, []),
            reference_records_from_mathpix_layout=lambda layout: [],
            mathpix_layout=None,
        )

        self.assertEqual(len(section_nodes), 2)
        self.assertEqual(section_nodes[-1].title, "References")
        self.assertEqual(section_nodes[-1].heading_id, "synthetic-references")
        self.assertEqual(len(section_nodes[-1].records), 5)

    def test_flatten_sections_visits_children_depth_first(self) -> None:
        roots = [
            SectionNode(
                title="Intro",
                level=1,
                heading_id="sec-1",
                records=[],
                children=[
                    SectionNode(title="Sub", level=2, heading_id="sec-1-1", records=[], children=[]),
                ],
            )
        ]

        ordered = flatten_sections(roots)

        self.assertEqual([node.heading_id for node in ordered], ["sec-1", "sec-1-1"])


if __name__ == "__main__":
    unittest.main()
