import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.mathpix_adapter import call_mathpix_on_page_image, run_mathpix


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


class _FakeMathpixResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeMathpixResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        import json

        return json.dumps(self._payload).encode("utf-8")


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

    def test_call_mathpix_retries_connection_reset_then_succeeds(self) -> None:
        with (
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("paper_pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "paper_pipeline.mathpix_adapter.request.urlopen",
                side_effect=[
                    ConnectionResetError(54, "Connection reset by peer"),
                    _FakeMathpixResponse({"ok": True}),
                ],
            ) as urlopen_mock,
        ):
            payload = call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(urlopen_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 1)
        self.assertEqual(sleep_mock.call_args.args[0], 0.25)

    def test_call_mathpix_uses_multipart_file_upload_shape(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(req, timeout: int = 180):
            captured["timeout"] = timeout
            captured["headers"] = dict(req.header_items())
            captured["body"] = req.data
            return _FakeMathpixResponse({"ok": True})

        with (
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=1),
            patch("paper_pipeline.mathpix_adapter.request.urlopen", side_effect=fake_urlopen),
        ):
            payload = call_mathpix_on_page_image(b"PNGDATA", app_id="id", app_key="key")

        self.assertEqual(payload, {"ok": True})
        headers = {str(key).lower(): str(value) for key, value in dict(captured["headers"]).items()}
        self.assertIn("multipart/form-data; boundary=", headers["content-type"])
        self.assertEqual(headers["connection"], "close")
        self.assertEqual(headers["accept"], "application/json")
        body_text = bytes(captured["body"]).decode("latin1")
        self.assertIn('name="file"; filename="page.png"', body_text)
        self.assertIn("Content-Type: image/png", body_text)
        self.assertIn('name="options_json"', body_text)
        self.assertIn('"formats":["text","data"]', body_text)
        self.assertIn('"include_line_data":true', body_text)
        self.assertNotIn("data:image/png;base64", body_text)
        self.assertIn("PNGDATA", body_text)

    def test_call_mathpix_retries_broken_pipe_urlerror_then_succeeds(self) -> None:
        with (
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("paper_pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "paper_pipeline.mathpix_adapter.request.urlopen",
                side_effect=[
                    error.URLError(BrokenPipeError(32, "Broken pipe")),
                    _FakeMathpixResponse({"ok": True}),
                ],
            ) as urlopen_mock,
        ):
            payload = call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(urlopen_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 1)
        self.assertEqual(sleep_mock.call_args.args[0], 0.25)

    def test_call_mathpix_raises_after_retry_budget_exhausted(self) -> None:
        with (
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("paper_pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("paper_pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "paper_pipeline.mathpix_adapter.request.urlopen",
                side_effect=[
                    ConnectionResetError(54, "Connection reset by peer"),
                    ConnectionResetError(54, "Connection reset by peer"),
                    ConnectionResetError(54, "Connection reset by peer"),
                ],
            ) as urlopen_mock,
        ):
            with self.assertRaisesRegex(RuntimeError, r"Mathpix request failed after 3 attempts"):
                call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(urlopen_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
