import io
import os
import sys
import unittest
from unittest.mock import patch

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.native_stderr import run_with_stderr_label


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


if __name__ == "__main__":
    unittest.main()
