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
REPORT_DIR = ROOT / "tmp" / "canonical_corpus_audit"
JSON_REPORT = REPORT_DIR / "summary.json"
MARKDOWN_REPORT = REPORT_DIR / "summary.md"


class AuditCorpusCliE2ETest(unittest.TestCase):
    def test_audit_corpus_cli_writes_reports_for_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "audit_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.audit_corpus",
                    "--top",
                    "1",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertIn("# Canonical Corpus Audit", completed.stdout)
            self.assertIn("1990_synthetic_test_paper", completed.stdout)
            self.assertTrue(JSON_REPORT.exists())
            self.assertTrue(MARKDOWN_REPORT.exists())

            report = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
            self.assertEqual(report["paper_count"], 1)
            self.assertEqual(report["canonical_count"], 1)
            self.assertEqual(report["missing_canonical_count"], 0)
            self.assertEqual(report["papers"][0]["paper_id"], "1990_synthetic_test_paper")

            markdown = MARKDOWN_REPORT.read_text(encoding="utf-8")
            self.assertIn("# Canonical Corpus Audit", markdown)
            self.assertIn("1990_synthetic_test_paper", markdown)


if __name__ == "__main__":
    unittest.main()
