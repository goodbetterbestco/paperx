import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.assembly.section_support import normalize_section_title, section_id
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE
from pipeline.reconcile.support_binding_runtime import make_clean_text
from pipeline.text.headings import SectionNode, compact_text, normalize_title_key, parse_heading_label, clean_heading_title


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)


class SectionSupportTest(unittest.TestCase):
    def test_normalize_section_title_strips_numeric_label(self) -> None:
        self.assertEqual(
            normalize_section_title(
                "6 References",
                clean_text=CLEAN_TEXT,
                clean_heading_title=clean_heading_title,
                parse_heading_label=parse_heading_label,
                normalize_title_key=normalize_title_key,
            ),
            "references",
        )

    def test_section_id_uses_label_when_present(self) -> None:
        node = SectionNode(title="Methods", level=1, heading_id="sec-2", label=("2", "3"), records=[], children=[])
        self.assertEqual(section_id(node, 4, normalize_title_key=normalize_title_key), "sec-2-3")


if __name__ == "__main__":
    unittest.main()
