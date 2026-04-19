from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.routing import inspect_pdf_signals, route_pdf_signals


class _FakeRect:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height


class _FakePage:
    def __init__(
        self,
        *,
        text: str,
        blocks: list[tuple[float, float, float, float, str]],
        image_blocks: list[dict[str, object]] | None = None,
        width: float = 600.0,
        height: float = 800.0,
    ) -> None:
        self._text = text
        self._blocks = blocks
        self._image_blocks = image_blocks or []
        self.rect = _FakeRect(width, height)

    def get_text(self, mode: str) -> object:
        if mode == "text":
            return self._text
        if mode == "blocks":
            return [(*block[:4], block[4], 0, 0) for block in self._blocks]
        if mode == "dict":
            return {"blocks": list(self._image_blocks)}
        raise AssertionError(f"unsupported mode: {mode}")


class _FakeDocument:
    def __init__(self, pages: list[_FakePage]) -> None:
        self._pages = pages

    def __len__(self) -> int:
        return len(self._pages)

    def __iter__(self):
        return iter(self._pages)

    def __enter__(self) -> _FakeDocument:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeFitz:
    def __init__(self, document: _FakeDocument) -> None:
        self._document = document

    def open(self, _path: Path) -> _FakeDocument:
        return self._document


class AcquisitionRoutingTest(unittest.TestCase):
    def test_routes_scan_first_for_image_heavy_pdf(self) -> None:
        pages = [
            _FakePage(
                text="scanned page",
                blocks=[],
                image_blocks=[{"type": 1, "bbox": [0, 0, 600, 760]}],
            ),
            _FakePage(
                text="",
                blocks=[],
                image_blocks=[{"type": 1, "bbox": [0, 0, 600, 800]}],
            ),
        ]

        signals = inspect_pdf_signals("/tmp/scan.pdf", load_fitz=lambda: _FakeFitz(_FakeDocument(pages)))
        decision = route_pdf_signals(signals)

        self.assertEqual(decision.primary_route, "scan_or_image_heavy")
        self.assertIn("ocrmypdf", decision.recommended_providers)
        self.assertIn("image_heavy", decision.traits)

    def test_routes_math_dense_for_born_digital_stem_pdf(self) -> None:
        stem_text = (
            "Abstract\n"
            "We prove a theorem about x_{n+1} = x_n + 1 and E = mc^2. "
            "Lemma 1 shows a proof with additional symbolic terms like a^2 + b^2 = c^2.\n"
            "[1] reference"
        )
        pages = [
            _FakePage(
                text=stem_text,
                blocks=[
                    (10, 10, 280, 80, "Synthetic Title"),
                    (20, 120, 280, 200, "Abstract"),
                    (20, 220, 280, 520, stem_text),
                ],
            ),
            _FakePage(
                text=stem_text,
                blocks=[
                    (10, 10, 280, 80, "Introduction"),
                    (20, 120, 280, 520, stem_text),
                ],
            ),
        ]

        signals = inspect_pdf_signals("/tmp/stem.pdf", load_fitz=lambda: _FakeFitz(_FakeDocument(pages)))
        decision = route_pdf_signals(signals)

        self.assertEqual(decision.primary_route, "math_dense")
        self.assertIn("mathpix", decision.recommended_providers)
        self.assertIn("math_heavy", decision.traits)

    def test_routes_layout_complex_for_two_column_pdf(self) -> None:
        pages = [
            _FakePage(
                text="two column content " * 80,
                blocks=[
                    (20, 20, 250, 150, "L" * 120),
                    (320, 20, 560, 150, "R" * 120),
                    (20, 180, 250, 320, "L2" * 70),
                    (320, 180, 560, 320, "R2" * 70),
                ],
            )
        ]

        signals = inspect_pdf_signals("/tmp/two-column.pdf", load_fitz=lambda: _FakeFitz(_FakeDocument(pages)))
        decision = route_pdf_signals(signals)

        self.assertEqual(decision.primary_route, "layout_complex")
        self.assertIn("two_column", decision.traits)
        self.assertIn("llamaparse", decision.recommended_providers)


if __name__ == "__main__":
    unittest.main()
