from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.audit_acquisition_quality import run_audit_acquisition_quality


class AcquisitionAuditCliTest(unittest.TestCase):
    def test_run_audit_cli_prints_commands_from_remediation_queue(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "audit"
            json_report_path = output_dir / "summary.json"
            markdown_report_path = output_dir / "summary.md"

            exit_code = run_audit_acquisition_quality(
                argparse.Namespace(top=5, format="commands"),
                audit_acquisition_quality_fn=lambda: {
                    "generated_at": "2026-04-19T00:00:00Z",
                    "paper_count": 2,
                    "canonical_count": 2,
                    "missing_canonical_count": 0,
                    "ocr_summary": {
                        "should_run_count": 0,
                        "applied_count": 0,
                        "required_not_applied_count": 0,
                        "recommended_not_applied_count": 0,
                    },
                    "remediation_queue": [
                        {
                            "paper_id": "paper-a",
                            "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-mathpix",
                        },
                        {
                            "paper_id": "paper-b",
                            "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-grobid",
                        },
                    ],
                    "papers": [],
                },
                render_markdown_fn=lambda report, *, top_n: "# Acquisition Quality Audit\n",
                output_dir=output_dir,
                json_report_path=json_report_path,
                markdown_report_path=markdown_report_path,
                print_fn=printed.append,
            )

            self.assertTrue(json_report_path.exists())
            self.assertTrue(markdown_report_path.exists())
            report = json.loads(json_report_path.read_text(encoding="utf-8"))
            self.assertEqual(len(report["remediation_queue"]), 2)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            printed[0],
            "\n".join(
                [
                    "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-mathpix",
                    "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-grobid",
                ]
            ),
        )

    def test_run_audit_cli_prints_json_when_requested(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "audit"
            exit_code = run_audit_acquisition_quality(
                argparse.Namespace(top=3, format="json"),
                audit_acquisition_quality_fn=lambda: {
                    "generated_at": "2026-04-19T00:00:00Z",
                    "paper_count": 1,
                    "canonical_count": 1,
                    "missing_canonical_count": 0,
                    "ocr_summary": {
                        "should_run_count": 0,
                        "applied_count": 0,
                        "required_not_applied_count": 0,
                        "recommended_not_applied_count": 0,
                    },
                    "remediation_queue": [],
                    "papers": [],
                },
                render_markdown_fn=lambda report, *, top_n: "# Acquisition Quality Audit\n",
                output_dir=output_dir,
                json_report_path=output_dir / "summary.json",
                markdown_report_path=output_dir / "summary.md",
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["paper_count"], 1)


if __name__ == "__main__":
    unittest.main()
