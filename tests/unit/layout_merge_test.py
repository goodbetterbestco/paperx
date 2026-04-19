import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.orchestrator.layout_merge import merge_native_and_external_layout
from pipeline.types import LayoutBlock


class LayoutMergeTest(unittest.TestCase):
    def test_merge_native_and_external_layout_replaces_external_pages(self) -> None:
        native_layout = {
            "pdf_path": "native.pdf",
            "page_count": 2,
            "page_sizes_pt": [{"page": 1, "width": 100.0, "height": 100.0}],
            "blocks": [
                LayoutBlock(id="n1", page=1, order=1, text="native p1", role="paragraph", bbox={}),
                LayoutBlock(id="n2", page=2, order=1, text="native p2", role="paragraph", bbox={}),
            ],
        }
        external_layout = {
            "pdf_path": "external.pdf",
            "page_count": 2,
            "page_sizes_pt": [{"page": 1, "width": 100.0, "height": 100.0}],
            "blocks": [
                LayoutBlock(id="e1", page=2, order=1, text="external p2", role="paragraph", bbox={}),
            ],
        }

        merged = merge_native_and_external_layout(native_layout, external_layout)

        self.assertEqual(merged["pdf_path"], "external.pdf")
        self.assertEqual([block.id for block in merged["blocks"]], ["n1", "e1"])


if __name__ == "__main__":
    unittest.main()
