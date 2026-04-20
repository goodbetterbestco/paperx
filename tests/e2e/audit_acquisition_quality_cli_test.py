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
                        "recommended_primary_metadata_provider": "grobid",
                        "recommended_primary_reference_provider": "docling",
                        "layout_recommendation_basis": "accepted",
                        "math_recommendation_basis": "accepted",
                        "metadata_recommendation_basis": "accepted",
                        "reference_recommendation_basis": "accepted",
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
                            "metadata_provider": "grobid",
                            "reference_provider": "docling",
                        },
                        "follow_up": {
                            "needs_attention": True,
                            "actions": [
                                {
                                    "product": "metadata",
                                    "reason": "metadata_provider_not_accepted",
                                    "action": "escalate_grobid_metadata",
                                    "target_provider": "grobid",
                                }
                            ],
                        },
                        "promotion": {
                            "label": "trial-mathpix",
                            "promoted_at": "2026-04-19T01:00:00Z",
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "trials" / "trial-mathpix").mkdir(parents=True, exist_ok=True)
            (sources_dir / "trials" / "trial-mathpix" / "acquisition-execution.json").write_text(
                json.dumps(
                    {
                        "trial": {
                            "label": "trial-mathpix",
                            "applied_at": "2026-04-19T00:30:00Z",
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "metadata-decision.json").write_text(
                json.dumps(
                    {
                        "provider": "grobid",
                        "reference_provider": "docling",
                        "title_applied": True,
                        "abstract_applied": True,
                        "references_applied": True,
                        "reference_count": 3,
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
            self.assertEqual(report["executed_metadata_provider_counts"]["grobid"], 1)
            self.assertEqual(report["executed_reference_provider_counts"]["docling"], 1)
            self.assertEqual(report["follow_up_needed_counts"]["needs_attention"], 1)
            self.assertEqual(report["follow_up_action_counts"]["escalate_grobid_metadata"], 1)
            self.assertEqual(report["active_promoted_trial_counts"]["trial-mathpix"], 1)
            self.assertEqual(report["latest_applied_trial_counts"]["trial-mathpix"], 1)
            self.assertEqual(report["metadata_application_counts"]["applied"], 1)
            self.assertEqual(report["reference_application_counts"]["applied"], 1)

            markdown = MARKDOWN_REPORT.read_text(encoding="utf-8")
            self.assertIn("# Acquisition Quality Audit", markdown)
            self.assertIn("1990_synthetic_test_paper", markdown)
            self.assertIn("Executed: layout `docling`", markdown)
            self.assertIn("metadata `grobid`", markdown)
            self.assertIn("references `docling`", markdown)
            self.assertIn("Follow-up: needed `True`", markdown)
            self.assertIn("latest applied `trial-mathpix`", markdown)
            self.assertIn("active promoted `trial-mathpix`", markdown)
            self.assertIn("Remediation: `none`", markdown)
            self.assertIn("`metadata` -> `escalate_grobid_metadata` via `grobid`", markdown)
            self.assertIn("Applied: metadata `True` | references `True`", markdown)
            self.assertIn("recommended layout `docling` (accepted)", markdown)

    def test_cli_renders_remediation_queue_for_actionable_paper(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "audit_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            sources_dir = project_dir / "corpus" / "1990_synthetic_test_paper" / "canonical_sources"
            sources_dir.mkdir(parents=True, exist_ok=True)
            (sources_dir / "acquisition-route.json").write_text(
                json.dumps(
                    {
                        "primary_route": "born_digital_scholarly",
                        "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
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
                        "recommended_primary_math_provider": "docling",
                        "layout_recommendation_basis": "fallback_unaccepted",
                        "math_recommendation_basis": "fallback_unaccepted",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "ocr-prepass.json").write_text(
                json.dumps(
                    {
                        "ocr_prepass_policy": "skip",
                        "ocr_prepass_tool": None,
                        "ocr_prepass_applied": False,
                        "pdf_source_kind": "original",
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
                            "selected_math_provider": "docling",
                        },
                        "follow_up": {
                            "needs_attention": True,
                            "actions": [
                                {
                                    "product": "layout",
                                    "action": "trial_layout_provider",
                                    "target_provider": "mathpix",
                                },
                                {
                                    "product": "math",
                                    "action": "trial_math_provider",
                                    "target_provider": "mathpix",
                                },
                            ],
                        },
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

            subprocess.run(
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

            markdown = MARKDOWN_REPORT.read_text(encoding="utf-8")
            self.assertIn("## Remediation Queue", markdown)
            self.assertIn("Command: `python3 -m pipeline.cli.remediate_acquisition_follow_up 1990_synthetic_test_paper --label trial-mathpix`", markdown)


if __name__ == "__main__":
    unittest.main()
