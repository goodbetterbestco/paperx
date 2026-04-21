import os
import subprocess
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib import error, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.sources.mathpix import (
    _mathpix_http_error_message,
    _mathpix_pdf_download_lines,
    _mathpix_pdf_lines_to_page_payloads,
    _mathpix_pdf_page_ranges,
    _mathpix_pdf_submit,
    _mathpix_pdf_wait_for_completion,
    _mathpix_request_json,
    download_mathpix_pdf,
    fetch_mathpix_pdf_status,
    call_mathpix_on_page_image,
    mathpix_pages_to_external_sources,
    run_mathpix,
    submit_mathpix_pdf,
    write_external_sources,
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
    def test_mathpix_pages_to_external_sources_emits_layout_and_math_payloads(self) -> None:
        page_payloads = [
            {
                "page": 1,
                "page_width_pt": 612.0,
                "page_height_pt": 792.0,
                "image_width": 100,
                "image_height": 200,
                "response": {
                    "line_data": [
                        {"type": "title", "text": "Paper Title", "cnt": [[10, 20], [50, 60]]},
                        {"type": "section_header", "text": "1 Introduction", "cnt": [[20, 30], [60, 80]]},
                        {"type": "figure_label", "text": "Figure 1", "cnt": [[15, 70], [45, 90]]},
                        {"type": "footnote", "text": "funded by x", "cnt": [[5, 180], [30, 195]]},
                        {"type": "text", "subtype": "algorithm", "text": "step one", "cnt": [[10, 100], [40, 120]]},
                        {"type": "text", "text": "Main paragraph", "cnt": [[10, 130], [90, 160]]},
                        {"type": "equation_number", "text": "(1)", "cnt": [[80, 20], [95, 30]]},
                        {"type": "math", "text_display": r"\(x + y\)", "cnt": [[20, 40], [80, 70]]},
                    ]
                },
            }
        ]

        with patch("pipeline.sources.mathpix._paper_pdf_path", return_value=Path("/tmp/paper.pdf")):
            layout, math = mathpix_pages_to_external_sources(page_payloads, "paper-1")

        self.assertEqual(layout["engine"], "mathpix")
        self.assertTrue(str(layout["pdf_path"]).endswith("/tmp/paper.pdf"))
        self.assertEqual(layout["page_count"], 1)
        self.assertEqual([block["role"] for block in layout["blocks"]], ["front_matter", "heading", "caption", "footnote", "code", "paragraph"])
        self.assertEqual(math["engine"], "mathpix")
        self.assertEqual(len(math["entries"]), 1)
        self.assertEqual(math["entries"][0]["display_latex"], "x + y")

    def test_mathpix_request_json_and_http_error_message_handle_invalid_payloads(self) -> None:
        http_error = error.HTTPError(
            "https://api.mathpix.com/v3/text",
            400,
            "Bad Request",
            hdrs=None,
            fp=BytesIO(b'{"error":"bad input","error_info":{"id":"req-7"}}'),
        )
        try:
            self.assertEqual(_mathpix_http_error_message(http_error), "Mathpix HTTP 400: bad input (req-7)")
        finally:
            http_error.close()

        with patch("pipeline.sources.mathpix._mathpix_request_bytes", return_value=b"[1,2,3]"):
            with self.assertRaises(RuntimeError):
                _mathpix_request_json(request.Request("https://api.mathpix.com/v3/text"))

    def test_mathpix_pdf_submit_retries_and_reports_missing_curl(self) -> None:
        call_count = 0

        def fake_run(command, check, capture_output, text):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise subprocess.CalledProcessError(56, command, stderr="temporary failure")
            return type("Completed", (), {"stdout": '{"pdf_id":"pdf-123"}'})()

        with (
            patch("pipeline.sources.mathpix._mathpix_retry_attempts", return_value=2),
            patch("pipeline.sources.mathpix._mathpix_retry_backoff_seconds", return_value=0.25),
            patch("pipeline.sources.mathpix._sleep"),
            patch("pipeline.sources.mathpix.subprocess.run", side_effect=fake_run),
        ):
            pdf_id = _mathpix_pdf_submit(Path("/tmp/fake.pdf"), app_id="id", app_key="key")

        self.assertEqual(pdf_id, "pdf-123")

        with patch("pipeline.sources.mathpix.subprocess.run", side_effect=FileNotFoundError()):
            with self.assertRaises(RuntimeError):
                _mathpix_pdf_submit(Path("/tmp/fake.pdf"), app_id="id", app_key="key")

    def test_mathpix_pdf_wait_for_completion_raises_for_error_and_timeout(self) -> None:
        with patch("pipeline.sources.mathpix._mathpix_pdf_status", return_value={"status": "error", "error": "bad pdf"}):
            with self.assertRaises(RuntimeError):
                _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

        monotonic_values = iter([0.0, 61.0])
        with (
            patch("pipeline.sources.mathpix._mathpix_pdf_status", return_value={"status": "processing"}),
            patch("pipeline.sources.mathpix._mathpix_pdf_wait_timeout_seconds", return_value=60),
            patch("pipeline.sources.mathpix.time.monotonic", side_effect=lambda: next(monotonic_values)),
        ):
            with self.assertRaises(RuntimeError):
                _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

    def test_mathpix_pdf_download_and_page_payload_helpers_validate_shapes(self) -> None:
        with patch("pipeline.sources.mathpix._mathpix_request_json", return_value={"status": "ok"}):
            with self.assertRaises(RuntimeError):
                _mathpix_pdf_download_lines("pdf-123", app_id="id", app_key="key")

        with (
            patch("pipeline.sources.mathpix._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
            patch("pipeline.sources.mathpix._pdf_page_sizes_pt", return_value=[(612.0, 792.0)]),
        ):
            payloads = _mathpix_pdf_lines_to_page_payloads(
                {
                    "pages": [
                        {"page": 1, "page_width": 200, "page_height": 400, "lines": [{"text": "alpha"}]},
                    ]
                },
                "paper-1",
            )

            self.assertEqual(payloads[0]["page"], 1)
            self.assertEqual(payloads[0]["response"]["line_data"][0]["text"], "alpha")

            with self.assertRaises(RuntimeError):
                _mathpix_pdf_lines_to_page_payloads(
                    {"pages": [{"page": 2, "page_width": 200, "page_height": 400, "lines": []}]},
                    "paper-1",
                )

    def test_public_pdf_helpers_validate_credentials_endpoints_and_forward_layout(self) -> None:
        self.assertEqual(_mathpix_pdf_page_ranges([3, 1, 3, 0]), "1,3")
        self.assertIsNone(_mathpix_pdf_page_ranges([]))

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                submit_mathpix_pdf("paper-1")
            with self.assertRaises(RuntimeError):
                fetch_mathpix_pdf_status("pdf-123")
            with self.assertRaises(RuntimeError):
                download_mathpix_pdf("paper-1", "pdf-123")

        with patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False):
            with self.assertRaises(RuntimeError):
                submit_mathpix_pdf("paper-1", endpoint="https://example.com")
            with self.assertRaises(RuntimeError):
                fetch_mathpix_pdf_status("pdf-123", endpoint="https://example.com")
            with self.assertRaises(RuntimeError):
                download_mathpix_pdf("paper-1", "pdf-123", endpoint="https://example.com")

            layout = object()
            with (
                patch("pipeline.sources.mathpix._paper_pdf_path", return_value=Path("/tmp/fake.pdf")) as paper_pdf_path_mock,
                patch("pipeline.sources.mathpix._mathpix_pdf_submit", return_value="pdf-123") as submit_mock,
                patch("pipeline.sources.mathpix._mathpix_pdf_status", return_value={"status": "completed"}) as status_mock,
                patch("pipeline.sources.mathpix._mathpix_pdf_download_lines", return_value={"pages": []}) as download_mock,
                patch("pipeline.sources.mathpix._pdf_page_sizes_pt", return_value=[]),
            ):
                self.assertEqual(submit_mathpix_pdf("paper-1", pages=[2, 2, 1], layout=layout), "pdf-123")
                self.assertEqual(fetch_mathpix_pdf_status("pdf-123"), {"status": "completed"})
                downloaded = download_mathpix_pdf("paper-1", "pdf-123", layout=layout)

        self.assertEqual(downloaded, {"pdf_id": "pdf-123", "lines": {"pages": []}, "pages": []})

    def test_write_external_sources_writes_json_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "sources"
            with patch("pipeline.sources.mathpix._output_dir", return_value=destination):
                layout_path, math_path = write_external_sources(
                    "paper-1",
                    {"engine": "mathpix", "blocks": [{"id": "block-1"}]},
                    {"engine": "mathpix", "entries": [{"id": "eq-1"}]},
                )

            self.assertTrue(layout_path.exists())
            self.assertTrue(math_path.exists())
            self.assertIn('"id": "block-1"', layout_path.read_text(encoding="utf-8"))
            self.assertIn('"id": "eq-1"', math_path.read_text(encoding="utf-8"))

    def test_run_mathpix_downloads_pdf_lines_preserves_page_order(self) -> None:
        lines_payload = {
            "pages": [
                {"page": 2, "page_width": 200, "page_height": 400, "lines": [{"type": "math", "text": r"\[y\]"}]},
                {"page": 1, "page_width": 100, "page_height": 200, "lines": [{"type": "text", "text": "alpha"}]},
            ]
        }

        with (
            patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False),
            patch("pipeline.sources.mathpix._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
            patch("pipeline.sources.mathpix._mathpix_pdf_submit", return_value="pdf-123") as submit_mock,
            patch("pipeline.sources.mathpix._mathpix_pdf_wait_for_completion", return_value={"status": "completed"}),
            patch("pipeline.sources.mathpix._mathpix_pdf_download_lines", return_value=lines_payload),
            patch(
                "pipeline.sources.mathpix._pdf_page_sizes_pt",
                return_value=[(612.0, 792.0), (612.0, 792.0)],
            ),
        ):
            result = run_mathpix("test-paper")

        self.assertEqual(result["pdf_id"], "pdf-123")
        self.assertEqual([payload["page"] for payload in result["pages"]], [1, 2])
        self.assertEqual(result["pages"][0]["response"]["line_data"][0]["text"], "alpha")
        self.assertEqual(result["pages"][1]["response"]["line_data"][0]["text"], r"\[y\]")

    def test_mathpix_pdf_wait_for_completion_retries_until_completed(self) -> None:
        with (
            patch(
                "pipeline.sources.mathpix._mathpix_pdf_status",
                side_effect=[
                    {"status": "received"},
                    {"status": "split"},
                    {"status": "completed", "num_pages": 2},
                ],
            ) as status_mock,
            patch("pipeline.sources.mathpix._mathpix_pdf_wait_timeout_seconds", return_value=60),
            patch("pipeline.sources.mathpix._mathpix_pdf_poll_seconds", return_value=0.25),
            patch("pipeline.sources.mathpix._sleep") as sleep_mock,
        ):
            result = _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

        self.assertEqual(result["status"], "completed")

    def test_call_mathpix_retries_connection_reset_then_succeeds(self) -> None:
        with (
            patch("pipeline.sources.mathpix._mathpix_retry_attempts", return_value=3),
            patch("pipeline.sources.mathpix._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.sources.mathpix._sleep") as sleep_mock,
            patch(
                "pipeline.sources.mathpix.request.urlopen",
                side_effect=[
                    ConnectionResetError(54, "Connection reset by peer"),
                    _FakeMathpixResponse({"ok": True}),
                ],
            ) as urlopen_mock,
        ):
            payload = call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(payload, {"ok": True})

    def test_call_mathpix_retries_broken_pipe_urlerror_then_succeeds(self) -> None:
        with (
            patch("pipeline.sources.mathpix._mathpix_retry_attempts", return_value=3),
            patch("pipeline.sources.mathpix._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.sources.mathpix._sleep") as sleep_mock,
            patch(
                "pipeline.sources.mathpix.request.urlopen",
                side_effect=[
                    error.URLError(BrokenPipeError(32, "Broken pipe")),
                    _FakeMathpixResponse({"ok": True}),
                ],
            ) as urlopen_mock,
        ):
            payload = call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(payload, {"ok": True})

    def test_call_mathpix_raises_after_retry_budget_exhausted(self) -> None:
        with (
            patch("pipeline.sources.mathpix._mathpix_retry_attempts", return_value=3),
            patch("pipeline.sources.mathpix._mathpix_retry_backoff_seconds", side_effect=[0.25, 0.5]),
            patch("pipeline.sources.mathpix._sleep") as sleep_mock,
            patch(
                "pipeline.sources.mathpix.request.urlopen",
                side_effect=[
                    ConnectionResetError(54, "Connection reset by peer"),
                    ConnectionResetError(54, "Connection reset by peer"),
                    ConnectionResetError(54, "Connection reset by peer"),
                ],
            ) as urlopen_mock,
        ):
            with self.assertRaises(RuntimeError):
                call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")


if __name__ == "__main__":
    unittest.main()
