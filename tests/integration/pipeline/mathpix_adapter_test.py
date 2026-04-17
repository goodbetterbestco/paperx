import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.mathpix_adapter import (
    _mathpix_pdf_submit,
    _mathpix_pdf_wait_for_completion,
    _mathpix_request_semaphore,
    call_mathpix_on_page_image,
    run_mathpix,
)


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
    def test_mathpix_request_limit_defaults_to_six(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            semaphore = _mathpix_request_semaphore()

        self.assertEqual(semaphore._value, 6)

    def test_run_mathpix_downloads_pdf_lines_preserves_page_order(self) -> None:
        lines_payload = {
            "pages": [
                {"page": 2, "page_width": 200, "page_height": 400, "lines": [{"type": "math", "text": r"\[y\]"}]},
                {"page": 1, "page_width": 100, "page_height": 200, "lines": [{"type": "text", "text": "alpha"}]},
            ]
        }

        with (
            patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False),
            patch("pipeline.mathpix_adapter._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
            patch("pipeline.mathpix_adapter._mathpix_pdf_submit", return_value="pdf-123") as submit_mock,
            patch("pipeline.mathpix_adapter._mathpix_pdf_wait_for_completion", return_value={"status": "completed"}),
            patch("pipeline.mathpix_adapter._mathpix_pdf_download_lines", return_value=lines_payload),
            patch(
                "pipeline.mathpix_adapter._pdf_page_sizes_pt",
                return_value=[(612.0, 792.0), (612.0, 792.0)],
            ),
        ):
            result = run_mathpix("test-paper")

        self.assertEqual(result["pdf_id"], "pdf-123")
        self.assertEqual([payload["page"] for payload in result["pages"]], [1, 2])
        self.assertEqual(result["pages"][0]["response"]["line_data"][0]["text"], "alpha")
        self.assertEqual(result["pages"][1]["response"]["line_data"][0]["text"], r"\[y\]")
        self.assertEqual(submit_mock.call_args.kwargs["page_ranges"], None)

    def test_run_mathpix_passes_page_ranges_to_pdf_submit(self) -> None:
        with (
            patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False),
            patch("pipeline.mathpix_adapter._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
            patch("pipeline.mathpix_adapter._mathpix_pdf_submit", return_value="pdf-123") as submit_mock,
            patch("pipeline.mathpix_adapter._mathpix_pdf_wait_for_completion", return_value={"status": "completed"}),
            patch("pipeline.mathpix_adapter._mathpix_pdf_download_lines", return_value={"pages": []}),
            patch(
                "pipeline.mathpix_adapter._pdf_page_sizes_pt",
                return_value=[(612.0, 792.0), (612.0, 792.0), (612.0, 792.0)],
            ),
        ):
            run_mathpix("test-paper", pages=[3, 1, 3])

        self.assertEqual(submit_mock.call_args.kwargs["page_ranges"], "1,3")

    def test_mathpix_pdf_wait_for_completion_retries_until_completed(self) -> None:
        with (
            patch(
                "pipeline.mathpix_adapter._mathpix_pdf_status",
                side_effect=[
                    {"status": "received"},
                    {"status": "split"},
                    {"status": "completed", "num_pages": 2},
                ],
            ) as status_mock,
            patch("pipeline.mathpix_adapter._mathpix_pdf_wait_timeout_seconds", return_value=60),
            patch("pipeline.mathpix_adapter._mathpix_pdf_poll_seconds", return_value=0.25),
            patch("pipeline.mathpix_adapter._sleep") as sleep_mock,
        ):
            result = _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(status_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_args.args[0], 0.25)

    def test_mathpix_pdf_submit_uses_multipart_pdf_upload_shape(self) -> None:
        captured: dict[str, object] = {}

        class _Completed:
            def __init__(self, stdout: str) -> None:
                self.stdout = stdout

        def fake_run(command, check, capture_output, text):
            captured["command"] = command
            self.assertTrue(check)
            self.assertTrue(capture_output)
            self.assertTrue(text)
            return _Completed('{"pdf_id":"pdf-123"}')

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "fake.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 test")
            with patch("pipeline.mathpix_adapter.subprocess.run", side_effect=fake_run):
                pdf_id = _mathpix_pdf_submit(pdf_path, app_id="id", app_key="key", page_ranges="1,3")

        self.assertEqual(pdf_id, "pdf-123")
        command = list(captured["command"])
        self.assertEqual(command[:4], ["curl", "-sS", "-X", "POST"])
        self.assertIn("app_id: id", command)
        self.assertIn("app_key: key", command)
        self.assertIn(f"file=@{pdf_path}", command)
        self.assertIn('options_json={"include_equation_tags":true,"include_page_info":true,"page_ranges":"1,3"}', command)

    def test_call_mathpix_retries_connection_reset_then_succeeds(self) -> None:
        with (
            patch("pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "pipeline.mathpix_adapter.request.urlopen",
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

        with patch("pipeline.mathpix_adapter.request.urlopen", side_effect=fake_urlopen):
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
            patch("pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "pipeline.mathpix_adapter.request.urlopen",
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
            patch("pipeline.mathpix_adapter._mathpix_retry_attempts", return_value=3),
            patch("pipeline.mathpix_adapter._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.mathpix_adapter._sleep") as sleep_mock,
            patch(
                "pipeline.mathpix_adapter.request.urlopen",
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
