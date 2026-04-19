from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.sources.pdftotext import bbox_to_line_window, extract_pdftotext_pages, pdftotext_available, slice_page_text


class PdftotextSourceTest(unittest.TestCase):
    def test_pdftotext_available_tracks_binary_presence(self) -> None:
        with patch("pipeline.sources.pdftotext.shutil.which", return_value="/usr/bin/pdftotext"):
            self.assertTrue(pdftotext_available())
        with patch("pipeline.sources.pdftotext.shutil.which", return_value=None):
            self.assertFalse(pdftotext_available())

    def test_extract_pdftotext_pages_splits_formfeed_delimited_output(self) -> None:
        with (
            patch("pipeline.sources.pdftotext._pdf_path", return_value=Path("/tmp/synthetic.pdf")),
            patch(
                "pipeline.sources.pdftotext._run_pdftotext",
                return_value="Title line\nBody line\fSecond page line\nTail\n\f\n",
            ),
        ):
            pages = extract_pdftotext_pages("1990_synthetic_test_paper")

        self.assertEqual(
            pages,
            {
                1: ["Title line", "Body line"],
                2: ["Second page line", "Tail"],
            },
        )

    def test_slice_page_text_compacts_requested_line_window(self) -> None:
        text = slice_page_text(
            [" Title ", "", "Body line", " Tail "],
            start_line=0,
            end_line=2,
        )

        self.assertEqual(text, "Title Body line")

    def test_bbox_to_line_window_bounds_indices(self) -> None:
        self.assertEqual(
            bbox_to_line_window({"y0": 100.0, "y1": 220.0}, page_height=800.0, line_count=20, pad_lines=1),
            (1, 7),
        )
        self.assertEqual(
            bbox_to_line_window({"y0": 0.0, "y1": 0.0}, page_height=0.0, line_count=20, pad_lines=1),
            (0, -1),
        )


if __name__ == "__main__":
    unittest.main()
