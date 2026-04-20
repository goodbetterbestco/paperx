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
REPORT_DIR = ROOT / "tmp" / "acquisition_quality_audit"
JSON_REPORT = REPORT_DIR / "summary.json"
MARKDOWN_REPORT = REPORT_DIR / "summary.md"


class AuditAcquisitionQualityCliE2ETest(unittest.TestCase):
    def test_cli_writes_acquisition_reports_for_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "audit_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            sources_dir = project_dir / "corpus" / "1990_synthetic_test_paper" / "canonical_sources"
            sources_dir.mkdir(parents=True, exist_ok=True)
            (sources_dir / "acquisition-route.json").write_text(
                json.dumps(
                    {
                        "primary_route": "degraded_or_garbled",
                        "ocr_prepass": {"policy": "recommended", "should_run": True, "tool": "ocrmypdf"},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "source-scorecard.json").write_text(
                json.dumps(
                    {
                        "recommended_primary_layout_provider": "docling",
                        "recommended_primary_math_provider": "mathpix",
                        "layout_recommendation_basis": "accepted",
                        "math_recommendation_basis": "accepted",
                        "providers": [
                            {
                                "provider": "docling",
                                "kind": "layout",
                                "accepted": True,
                                "rejection_reasons": [],
                            },
                            {
                                "provider": "mathpix",
                                "kind": "math",
                                "accepted": True,
                                "rejection_reasons": [],
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "ocr-prepass.json").write_text(
                json.dumps(
                    {
                        "ocr_prepass_policy": "recommended",
                        "ocr_prepass_tool": "ocrmypdf",
                        "ocr_prepass_applied": True,
                        "pdf_source_kind": "ocr_normalized_generated",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "acquisition-execution.json").write_text(
                json.dumps(
                    {
                        "executed": {
                            "selected_layout_provider": "docling",
                            "selected_math_provider": "mathpix",
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env["PAPER_PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)
            env.pop("PAPER_PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.audit_acquisition_quality",
                    "--top",
                    "1",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertIn("# Acquisition Quality Audit", completed.stdout)
            self.assertIn("1990_synthetic_test_paper", completed.stdout)
            self.assertTrue(JSON_REPORT.exists())
            self.assertTrue(MARKDOWN_REPORT.exists())

            report = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
            self.assertEqual(report["paper_count"], 1)
            self.assertEqual(report["canonical_count"], 1)
            self.assertEqual(report["route_counts"]["degraded_or_garbled"], 1)
            self.assertEqual(report["ocr_summary"]["applied_count"], 1)
            self.assertEqual(report["executed_layout_provider_counts"]["docling"], 1)
            self.assertEqual(report["layout_recommendation_basis_counts"]["accepted"], 1)

            markdown = MARKDOWN_REPORT.read_text(encoding="utf-8")
            self.assertIn("# Acquisition Quality Audit", markdown)
            self.assertIn("1990_synthetic_test_paper", markdown)
            self.assertIn("Executed: layout `docling`", markdown)
            self.assertIn("recommended layout `docling` (accepted)", markdown)


if __name__ == "__main__":
    unittest.main()
