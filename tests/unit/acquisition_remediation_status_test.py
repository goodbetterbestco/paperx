from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.remediation_status import summarize_latest_remediation_status
from pipeline.cli.show_acquisition_remediation_status import run_show_remediation_status_cli


class AcquisitionRemediationStatusTest(unittest.TestCase):
    def test_summarize_latest_remediation_status_condenses_failures_and_skips(self) -> None:
        report = summarize_latest_remediation_status(
            output_dir="/tmp/remediation",
            load_summary_fn=lambda *, output_dir=None: {
                "snapshot_label": "queue-run",
                "generated_at": "2026-04-19T00:00:00Z",
                "mode": "execute",
                "source": {"kind": "live_audit"},
                "plan": {"label": "fixture-plan", "wave_id": "wave-2"},
                "resume": {"requested": "latest", "path": "/tmp/remediation/history/latest.json"},
                "requested_count": 3,
                "selected_count": 2,
                "skipped_count": 1,
                "selected_papers": ["paper-b", "paper-c"],
                "selected_priorities": ["critical", "high"],
                "status_counts": {"failed": 1, "skipped_succeeded": 1, "succeeded": 1},
                "report_paths": {
                    "json": "/tmp/remediation/summary.json",
                    "snapshot_json": "/tmp/remediation/history/queue-run.json",
                },
                "skipped_papers": [
                    {"paper_id": "paper-a", "priority": "critical", "priority_score": 9, "status": "skipped_succeeded"}
                ],
                "results": [
                    {"paper_id": "paper-b", "priority": "critical", "priority_score": 9, "status": "succeeded"},
                    {
                        "paper_id": "paper-c",
                        "priority": "high",
                        "priority_score": 5,
                        "status": "failed",
                        "returncode": 2,
                        "stderr": "boom",
                    },
                ],
            },
        )

        self.assertEqual(report["latest_run"]["label"], "queue-run")
        self.assertEqual(report["latest_run"]["plan"]["label"], "fixture-plan")
        self.assertEqual(report["latest_run"]["status_counts"]["failed"], 1)
        self.assertEqual(report["failures"][0]["paper_id"], "paper-c")
        self.assertEqual(report["skipped_papers"][0]["paper_id"], "paper-a")

    def test_show_remediation_status_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_show_remediation_status_cli(
            argparse.Namespace(output_dir="/tmp/remediation", format="markdown"),
            summarize_status_fn=lambda *, output_dir=None: {
                "output_dir": "/tmp/remediation",
                "latest_run": {
                    "label": "queue-run",
                    "generated_at": "2026-04-19T00:00:00Z",
                    "mode": "execute",
                    "source": {"kind": "live_audit"},
                    "plan": {"label": "fixture-plan", "wave_id": "wave-2"},
                    "resume": {"requested": "latest", "path": "/tmp/remediation/history/latest.json"},
                    "requested_count": 3,
                    "selected_count": 2,
                    "skipped_count": 1,
                    "selected_priorities": ["critical", "high"],
                    "status_counts": {"failed": 1, "skipped_succeeded": 1, "succeeded": 1},
                    "report_paths": {
                        "json": "/tmp/remediation/summary.json",
                        "snapshot_json": "/tmp/remediation/history/queue-run.json",
                    },
                },
                "failures": [
                    {"paper_id": "paper-c", "priority": "high", "priority_score": 5, "returncode": 2, "stderr": "boom"}
                ],
                "skipped_papers": [
                    {"paper_id": "paper-a", "priority": "critical", "priority_score": 9, "status": "skipped_succeeded"}
                ],
                "results": [],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Status", printed[0])
        self.assertIn("fixture-plan", printed[0])
        self.assertIn("queue-run", printed[0])
        self.assertIn("paper-c", printed[0])
        self.assertIn("paper-a", printed[0])

    def test_show_remediation_status_cli_prints_json(self) -> None:
        printed: list[str] = []
        exit_code = run_show_remediation_status_cli(
            argparse.Namespace(output_dir="/tmp/remediation", format="json"),
            summarize_status_fn=lambda *, output_dir=None: {
                "output_dir": "/tmp/remediation",
                "latest_run": {"label": "queue-run"},
                "failures": [],
                "skipped_papers": [],
                "results": [],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["latest_run"]["label"], "queue-run")


if __name__ == "__main__":
    unittest.main()
