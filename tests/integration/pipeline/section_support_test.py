import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.assembly.section_support import normalize_section_title, section_id
from pipeline.text_utils import SectionNode


class SectionSupportTest(unittest.TestCase):
    def test_normalize_section_title_strips_numeric_label(self) -> None:
        self.assertEqual(
            normalize_section_title(
                "6 References",
                clean_text=rb._clean_text,
                clean_heading_title=rb.clean_heading_title,
                parse_heading_label=rb.parse_heading_label,
                normalize_title_key=rb.normalize_title_key,
            ),
            "references",
        )

    def test_section_id_uses_label_when_present(self) -> None:
        node = SectionNode(title="Methods", level=1, heading_id="sec-2", label=("2", "3"), records=[], children=[])
        self.assertEqual(section_id(node, 4, normalize_title_key=rb.normalize_title_key), "sec-2-3")


if __name__ == "__main__":
    unittest.main()
