import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.mathpix_adapter import run_mathpix


class _FakeDoc:
    def __init__(self, page_count: int) -> None:
        self.page_count = page_count

    def __enter__(self) -> "_FakeDoc":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class _FakeFitz:
    def open(self, path: Path) -> _FakeDoc:
        return _FakeDoc(page_count=3)


class MathpixAdapterTest(unittest.TestCase):
    def test_parallel_run_mathpix_preserves_page_order(self) -> None:
        def fake_render(pdf_path: Path, page_number: int, *, scale: float) -> tuple[bytes, int, int, float, float]:
            return (str(page_number).encode("ascii"), 100, 100, 612.0, 792.0)

        def fake_call(
            image_bytes: bytes,
            *,
            app_id: str,
            app_key: str,
            endpoint: str,
            timeout_seconds: int = 180,
        ) -> dict[str, int]:
            page_number = int(image_bytes.decode("ascii"))
            if page_number == 1:
                time.sleep(0.03)
            elif page_number == 2:
                time.sleep(0.01)
            return {"page_number": page_number}

        with (
            patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False),
            patch("paper_pipeline.mathpix_adapter._load_fitz", return_value=_FakeFitz()),
            patch("paper_pipeline.mathpix_adapter._render_page_png_bytes", side_effect=fake_render),
            patch("paper_pipeline.mathpix_adapter.call_mathpix_on_page_image", side_effect=fake_call),
        ):
            payloads = run_mathpix("test-paper", page_workers=3)

        self.assertEqual([payload["page"] for payload in payloads], [1, 2, 3])
        self.assertEqual(
            [payload["response"]["page_number"] for payload in payloads],
            [1, 2, 3],
        )


if __name__ == "__main__":
    unittest.main()
