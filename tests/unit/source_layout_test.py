from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import pipeline.sources.layout as source_layout


class _Rect:
    def __init__(self, *args: object) -> None:
        if len(args) == 1 and isinstance(args[0], _Rect):
            other = args[0]
            self.x0, self.y0, self.x1, self.y1 = other.x0, other.y0, other.x1, other.y1
            return
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            x0, y0, x1, y1 = args[0]
            self.x0, self.y0, self.x1, self.y1 = map(float, (x0, y0, x1, y1))
            return
        x0, y0, x1, y1 = args
        self.x0, self.y0, self.x1, self.y1 = map(float, (x0, y0, x1, y1))

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


class _FakePage:
    def __init__(self, rect: _Rect, blocks: list[dict[str, object]]) -> None:
        self.rect = rect
        self._blocks = blocks

    def get_text(self, mode: str) -> dict[str, object]:
        return {"blocks": self._blocks}


class _FakeDoc:
    def __init__(self, pages: list[_FakePage]) -> None:
        self._pages = pages
        self.page_count = len(pages)
        self.closed = False

    def load_page(self, index: int) -> _FakePage:
        return self._pages[index]

    def close(self) -> None:
        self.closed = True


class SourceLayoutTest(unittest.TestCase):
    def test_extract_layout_classifies_front_matter_heading_paragraph_caption_and_reference(self) -> None:
        fake_fitz = types.SimpleNamespace(
            Rect=_Rect,
            open=lambda path: _FakeDoc(
                [
                    _FakePage(
                        _Rect(0, 0, 600, 800),
                        [
                            {
                                "type": 0,
                                "bbox": (40, 40, 560, 120),
                                "lines": [{"spans": [{"text": "Synthetic Paper Title", "size": 18.0}]}],
                            },
                            {
                                "type": 0,
                                "bbox": (40, 320, 300, 350),
                                "lines": [{"spans": [{"text": "1 Introduction", "size": 14.0}]}],
                            },
                            {
                                "type": 0,
                                "bbox": (40, 260, 560, 320),
                                "lines": [{"spans": [{"text": "This paragraph contains the body text.", "size": 11.0}]}],
                            },
                            {
                                "type": 0,
                                "bbox": (40, 620, 560, 650),
                                "lines": [{"spans": [{"text": "Figure 2: A stable silhouette.", "size": 10.0}]}],
                            },
                        ],
                    ),
                    _FakePage(
                        _Rect(0, 0, 600, 800),
                        [
                            {
                                "type": 0,
                                "bbox": (50, 700, 500, 730),
                                "lines": [{"spans": [{"text": "Smith2024] A cited work.", "size": 10.0}]}],
                            }
                        ],
                    ),
                ]
            ),
        )
        original_fitz = source_layout.fitz
        try:
            source_layout.fitz = fake_fitz
            with (
                unittest.mock.patch("pipeline.sources.layout.paper_pdf_path", return_value=Path("/tmp/synthetic.pdf")),
                unittest.mock.patch("pipeline.sources.layout.display_path", return_value="1990_synthetic_test_paper/1990_synthetic_test_paper.pdf"),
            ):
                extracted = source_layout.extract_layout(
                    "1990_synthetic_test_paper",
                    layout=types.SimpleNamespace(),
                )
        finally:
            source_layout.fitz = original_fitz

        self.assertEqual(extracted["page_count"], 2)
        self.assertEqual(extracted["page_sizes_pt"][0], {"page": 1, "width": 600.0, "height": 800.0})
        self.assertEqual([block.role for block in extracted["blocks"]], ["front_matter", "heading", "paragraph", "caption", "reference"])
        self.assertEqual(extracted["blocks"][2].bbox["width"], 520.0)


if __name__ == "__main__":
    unittest.main()
