import io
import os
import sys
import unittest
from unittest.mock import patch

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.native_stderr import open_pdf_with_diagnostics, run_with_stderr_label


class NativeStderrTest(unittest.TestCase):
    def test_run_with_stderr_label_prefixes_native_stderr_output(self) -> None:
        captured = io.StringIO()

        def emit_native_stderr() -> str:
            os.write(2, b"MuPDF error: format error: cmsOpenProfileFromMem failed\n")
            return "ok"

        with patch("sys.stderr", captured):
            result = run_with_stderr_label("paper-1 stage=test", emit_native_stderr)

        self.assertEqual(result, "ok")
        self.assertIn("[native-stderr paper=paper-1 stage=test] MuPDF error: format error: cmsOpenProfileFromMem failed", captured.getvalue())

    def test_open_pdf_with_diagnostics_rewrites_cms_profile_open_failure(self) -> None:
        captured = io.StringIO()

        class FakeFitz:
            @staticmethod
            def open(path: Path) -> None:
                os.write(2, b"MuPDF error: format error: cmsOpenProfileFromMem failed\n")
                raise RuntimeError(f"cannot open {path}")

        pdf_path = Path("/tmp/bad-source.pdf")
        with patch("sys.stderr", captured):
            with self.assertRaises(RuntimeError) as raised:
                open_pdf_with_diagnostics("paper-1 stage=layout-open", pdf_path, fitz_module=FakeFitz)

        message = str(raised.exception)
        self.assertIn("Failed to open source PDF for paper-1 stage=layout-open", message)
        self.assertIn(str(pdf_path), message)
        self.assertIn("Inspect or replace the source PDF", message)
        self.assertIn("[native-stderr paper=paper-1 stage=layout-open] MuPDF error: format error: cmsOpenProfileFromMem failed", captured.getvalue())

    def test_open_pdf_with_diagnostics_preserves_other_open_failures(self) -> None:
        class FakeFitz:
            @staticmethod
            def open(path: Path) -> None:
                raise ValueError(f"bad open: {path}")

        pdf_path = Path("/tmp/other-bad-source.pdf")
        with self.assertRaises(ValueError) as raised:
            open_pdf_with_diagnostics("paper-2 stage=layout-open", pdf_path, fitz_module=FakeFitz)

        self.assertEqual(str(raised.exception), f"bad open: {pdf_path}")


if __name__ == "__main__":
    unittest.main()
