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
    _bbox_from_cnt,
    _clean_latex,
    _float_env,
    _int_env,
    _layout_block_from_line,
    _math_entry_from_line,
    _mathpix_http_error_message,
    _mathpix_pdf_download_lines,
    _mathpix_pdf_lines_to_page_payloads,
    _mathpix_pdf_page_ranges,
    _mathpix_pdf_submit,
    _mathpix_pdf_wait_for_completion,
    _mathpix_request_json,
    _mathpix_request_semaphore,
    _mathpix_retry_backoff_seconds,
    _render_page_png_bytes,
    _retryable_socket_error,
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
    def test_env_helpers_and_backoff_clamp_invalid_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "STEPVIEW_MATHPIX_REQUEST_LIMIT": "0",
                "STEPVIEW_MATHPIX_RETRY_BASE_SECONDS": "-2",
                "STEPVIEW_MATHPIX_RETRY_MAX_SECONDS": "bogus",
                "STEPVIEW_MATHPIX_PDF_WAIT_TIMEOUT_SECONDS": "bogus",
            },
            clear=False,
        ):
            self.assertEqual(_int_env("STEPVIEW_MATHPIX_REQUEST_LIMIT", 6), 1)
            self.assertEqual(_float_env("STEPVIEW_MATHPIX_RETRY_BASE_SECONDS", 1.0), 0.0)
            self.assertEqual(_float_env("STEPVIEW_MATHPIX_RETRY_MAX_SECONDS", 8.0), 8.0)
            self.assertEqual(_mathpix_retry_backoff_seconds(3), 0.0)
            self.assertEqual(_int_env("STEPVIEW_MATHPIX_PDF_WAIT_TIMEOUT_SECONDS", 1800), 1800)

    def test_mathpix_request_limit_defaults_to_six(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            semaphore = _mathpix_request_semaphore()

        self.assertEqual(semaphore._value, 6)

    def test_retryable_socket_error_handles_nested_and_non_retryable_exceptions(self) -> None:
        self.assertTrue(_retryable_socket_error(error.URLError(BrokenPipeError(32, "Broken pipe"))))
        self.assertTrue(_retryable_socket_error(ConnectionResetError(54, "Connection reset by peer")))
        self.assertTrue(_retryable_socket_error(OSError(104, "Connection reset by peer")))
        self.assertFalse(_retryable_socket_error(RuntimeError("boom")))

    def test_bbox_clean_latex_and_layout_helpers_transform_lines(self) -> None:
        bbox = _bbox_from_cnt(
            [[10, 20], [50, 60]],
            page_width_pt=612.0,
            page_height_pt=792.0,
            image_width=100,
            image_height=200,
        )
        self.assertEqual(
            bbox,
            {
                "x0": 61.2,
                "y0": 79.2,
                "x1": 306.0,
                "y1": 237.6,
                "width": 244.8,
                "height": 158.4,
            },
        )
        self.assertEqual(_bbox_from_cnt([], page_width_pt=10.0, page_height_pt=10.0, image_width=0, image_height=0), {})
        self.assertEqual(_clean_latex(r" \[ x + y \] "), "x + y")
        self.assertEqual(_clean_latex(r"$z$"), "z")
        self.assertEqual(_clean_latex("plain text"), "plain text")

        block = _layout_block_from_line(
            {
                "type": "pseudocode",
                "subtype": "algorithm",
                "text": " for i in range(n) ",
                "cnt": [[10, 20], [50, 60]],
                "confidence": 0.9,
                "confidence_rate": 0.8,
                "parent_id": "parent-1",
                "children_ids": ["child-1"],
            },
            paper_id="paper-1",
            page=2,
            order=3,
            page_width_pt=612.0,
            page_height_pt=792.0,
            image_width=100,
            image_height=200,
        )

        self.assertIsNotNone(block)
        assert block is not None
        self.assertEqual(block["id"], "mathpix-p002-b0003")
        self.assertEqual(block["role"], "code")
        self.assertEqual(block["text"], "for i in range(n)")
        self.assertEqual(block["meta"]["mathpix_subtype"], "algorithm")
        self.assertIsNone(
            _layout_block_from_line(
                {"type": "page_info", "text": "ignored"},
                paper_id="paper-1",
                page=1,
                order=1,
                page_width_pt=612.0,
                page_height_pt=792.0,
                image_width=100,
                image_height=200,
            )
        )

    def test_math_entry_from_line_uses_text_display_and_skips_blank_or_non_math(self) -> None:
        entry = _math_entry_from_line(
            {
                "type": "math",
                "text_display": r"$$E = mc^2$$",
                "cnt": [[10, 20], [50, 60]],
            },
            page=4,
            order=9,
            page_width_pt=612.0,
            page_height_pt=792.0,
            image_width=100,
            image_height=200,
        )

        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry["id"], "mathpix-eq-p004-0009")
        self.assertEqual(entry["display_latex"], "E = mc^2")
        self.assertEqual(entry["source_spans"][0]["engine"], "mathpix")
        self.assertIsNone(
            _math_entry_from_line(
                {"type": "math", "text": "   "},
                page=1,
                order=1,
                page_width_pt=612.0,
                page_height_pt=792.0,
                image_width=100,
                image_height=200,
            )
        )
        self.assertIsNone(
            _math_entry_from_line(
                {"type": "text", "text": "alpha"},
                page=1,
                order=1,
                page_width_pt=612.0,
                page_height_pt=792.0,
                image_width=100,
                image_height=200,
            )
        )

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

    def test_render_page_png_bytes_uses_pymupdf_page_geometry(self) -> None:
        class _FakePixmap:
            width = 320
            height = 640

            def tobytes(self, fmt: str) -> bytes:
                self.format = fmt
                return b"PNGDATA"

        class _FakePage:
            def __init__(self) -> None:
                self.rect = type("Rect", (), {"width": 612.0, "height": 792.0})()
                self.pixmap_calls: list[tuple[object, bool]] = []

            def get_pixmap(self, *, matrix, alpha: bool):
                self.pixmap_calls.append((matrix, alpha))
                return _FakePixmap()

        class _FakeDocument:
            def __init__(self) -> None:
                self.page = _FakePage()

            def __enter__(self) -> "_FakeDocument":
                return self

            def __exit__(self, exc_type, exc, tb) -> bool:
                return False

            def __getitem__(self, index: int) -> _FakePage:
                self.requested_index = index
                return self.page

        fake_document = _FakeDocument()

        class _FakeFitz:
            @staticmethod
            def open(path: Path) -> _FakeDocument:
                self.assertEqual(path, Path("/tmp/fake.pdf"))
                return fake_document

            @staticmethod
            def Matrix(x: float, y: float) -> tuple[float, float]:
                return (x, y)

        with patch("pipeline.sources.mathpix._load_fitz", return_value=_FakeFitz):
            png_bytes, image_width, image_height, page_width, page_height = _render_page_png_bytes(
                Path("/tmp/fake.pdf"),
                2,
                scale=2.0,
            )

        self.assertEqual(png_bytes, b"PNGDATA")
        self.assertEqual((image_width, image_height), (320, 640))
        self.assertEqual((page_width, page_height), (612.0, 792.0))
        self.assertEqual(fake_document.requested_index, 1)
        self.assertEqual(fake_document.page.pixmap_calls, [((2.0, 2.0), False)])

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
            with self.assertRaisesRegex(RuntimeError, "non-object JSON payload"):
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
            patch("pipeline.sources.mathpix._sleep") as sleep_mock,
            patch("pipeline.sources.mathpix.subprocess.run", side_effect=fake_run),
        ):
            pdf_id = _mathpix_pdf_submit(Path("/tmp/fake.pdf"), app_id="id", app_key="key")

        self.assertEqual(pdf_id, "pdf-123")
        self.assertEqual(call_count, 2)
        self.assertEqual(sleep_mock.call_count, 1)

        with patch("pipeline.sources.mathpix.subprocess.run", side_effect=FileNotFoundError()):
            with self.assertRaisesRegex(RuntimeError, "curl is required"):
                _mathpix_pdf_submit(Path("/tmp/fake.pdf"), app_id="id", app_key="key")

    def test_mathpix_pdf_wait_for_completion_raises_for_error_and_timeout(self) -> None:
        with patch("pipeline.sources.mathpix._mathpix_pdf_status", return_value={"status": "error", "error": "bad pdf"}):
            with self.assertRaisesRegex(RuntimeError, "failed"):
                _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

        monotonic_values = iter([0.0, 61.0])
        with (
            patch("pipeline.sources.mathpix._mathpix_pdf_status", return_value={"status": "processing"}),
            patch("pipeline.sources.mathpix._mathpix_pdf_wait_timeout_seconds", return_value=60),
            patch("pipeline.sources.mathpix.time.monotonic", side_effect=lambda: next(monotonic_values)),
        ):
            with self.assertRaisesRegex(RuntimeError, "did not complete within 60 seconds"):
                _mathpix_pdf_wait_for_completion("pdf-123", app_id="id", app_key="key")

    def test_mathpix_pdf_download_and_page_payload_helpers_validate_shapes(self) -> None:
        with patch("pipeline.sources.mathpix._mathpix_request_json", return_value={"status": "ok"}):
            with self.assertRaisesRegex(RuntimeError, "did not include pages"):
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

            with self.assertRaisesRegex(RuntimeError, "out-of-range page 2"):
                _mathpix_pdf_lines_to_page_payloads(
                    {"pages": [{"page": 2, "page_width": 200, "page_height": 400, "lines": []}]},
                    "paper-1",
                )

    def test_public_pdf_helpers_validate_credentials_endpoints_and_forward_layout(self) -> None:
        self.assertEqual(_mathpix_pdf_page_ranges([3, 1, 3, 0]), "1,3")
        self.assertIsNone(_mathpix_pdf_page_ranges([]))

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "credentials not found"):
                submit_mathpix_pdf("paper-1")
            with self.assertRaisesRegex(RuntimeError, "credentials not found"):
                fetch_mathpix_pdf_status("pdf-123")
            with self.assertRaisesRegex(RuntimeError, "credentials not found"):
                download_mathpix_pdf("paper-1", "pdf-123")

        with patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "expects the Mathpix PDF endpoint"):
                submit_mathpix_pdf("paper-1", endpoint="https://example.com")
            with self.assertRaisesRegex(RuntimeError, "expects the Mathpix PDF endpoint"):
                fetch_mathpix_pdf_status("pdf-123", endpoint="https://example.com")
            with self.assertRaisesRegex(RuntimeError, "expects the Mathpix PDF endpoint"):
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

        self.assertEqual(submit_mock.call_args.kwargs["page_ranges"], "1,2")
        self.assertIs(paper_pdf_path_mock.call_args.kwargs["layout"], layout)
        self.assertEqual(status_mock.call_args.args[0], "pdf-123")
        self.assertEqual(download_mock.call_args.args[0], "pdf-123")
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
        self.assertEqual(submit_mock.call_args.kwargs["page_ranges"], None)

    def test_run_mathpix_passes_page_ranges_to_pdf_submit(self) -> None:
        with (
            patch.dict(os.environ, {"MATHPIX_APP_ID": "id", "MATHPIX_APP_KEY": "key"}, clear=False),
            patch("pipeline.sources.mathpix._paper_pdf_path", return_value=Path("/tmp/fake.pdf")),
            patch("pipeline.sources.mathpix._mathpix_pdf_submit", return_value="pdf-123") as submit_mock,
            patch("pipeline.sources.mathpix._mathpix_pdf_wait_for_completion", return_value={"status": "completed"}),
            patch("pipeline.sources.mathpix._mathpix_pdf_download_lines", return_value={"pages": []}),
            patch(
                "pipeline.sources.mathpix._pdf_page_sizes_pt",
                return_value=[(612.0, 792.0), (612.0, 792.0), (612.0, 792.0)],
            ),
        ):
            run_mathpix("test-paper", pages=[3, 1, 3])

        self.assertEqual(submit_mock.call_args.kwargs["page_ranges"], "1,3")

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
            with patch("pipeline.sources.mathpix.subprocess.run", side_effect=fake_run):
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

        with patch("pipeline.sources.mathpix.request.urlopen", side_effect=fake_urlopen):
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
        self.assertEqual(urlopen_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 1)
        self.assertEqual(sleep_mock.call_args.args[0], 0.25)

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
            with self.assertRaisesRegex(RuntimeError, r"Mathpix request failed after 3 attempts"):
                call_mathpix_on_page_image(b"image-bytes", app_id="id", app_key="key")

        self.assertEqual(urlopen_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
