from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


FIXTURE_PROJECT = ROOT / "tests" / "fixtures" / "render_review_project"
CLI_PYTHON = ROOT / ".venv-paperx" / "bin" / "python"
MINIMAL_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 18 Tf 72 720 Td (Synthetic PDF) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000241 00000 n 
0000000335 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
405
%%EOF
"""


class BackfillAcquisitionSidecarsCliE2ETest(unittest.TestCase):
    def test_cli_writes_missing_sidecars_for_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "audit_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            (project_dir / "1990_synthetic_test_paper" / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)
            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    str(CLI_PYTHON if CLI_PYTHON.exists() else Path(sys.executable)),
                    "-m",
                    "pipeline.cli.backfill_acquisition_sidecars",
                    "--paper-id",
                    "1990_synthetic_test_paper",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["paper_count"], 1)
            self.assertEqual(payload["updated"]["acquisition-route.json"], 1)
            self.assertEqual(payload["updated"]["source-scorecard.json"], 1)
            self.assertEqual(payload["updated"]["ocr-prepass.json"], 1)

            sources_dir = project_dir / "1990_synthetic_test_paper" / "canonical_sources"
            self.assertTrue((sources_dir / "acquisition-route.json").exists())
            self.assertTrue((sources_dir / "source-scorecard.json").exists())
            self.assertTrue((sources_dir / "ocr-prepass.json").exists())


if __name__ == "__main__":
    unittest.main()
