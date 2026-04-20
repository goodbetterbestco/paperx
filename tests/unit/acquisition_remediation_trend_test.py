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


from pipeline.acquisition.remediation_trend import summarize_remediation_trend
from pipeline.cli.summarize_acquisition_remediation_trend import run_summarize_remediation_trend_cli


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionRemediationTrendTest(unittest.TestCase):
    def test_summarize_remediation_trend_reports_introduced_and_resolved_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            _write_report(
                history_dir / "baseline.json",
                {
                    "snapshot_label": "baseline",
                    "generated_at": "2026-04-19T00:00:00Z",
                    "requested_count": 2,
                    "selected_count": 2,
                    "skipped_count": 0,
                    "status_counts": {"succeeded": 1, "failed": 1},
                    "results": [
                        {"paper_id": "paper-a", "status": "succeeded", "priority": "critical", "priority_score": 9},
                        {"paper_id": "paper-b", "status": "failed", "priority": "high", "priority_score": 5},
                    ],
                    "skipped_papers": [],
                },
            )
            _write_report(
                history_dir / "candidate.json",
                {
                    "snapshot_label": "candidate",
                    "generated_at": "2026-04-19T01:00:00Z",
                    "requested_count": 3,
                    "selected_count": 2,
                    "skipped_count": 1,
                    "status_counts": {"succeeded": 1, "failed": 1, "skipped_succeeded": 1},
                    "results": [
                        {"paper_id": "paper-c", "status": "failed", "priority": "medium", "priority_score": 3},
                        {"paper_id": "paper-d", "status": "succeeded", "priority": "critical", "priority_score": 9},
                    ],
                    "skipped_papers": [
                        {"paper_id": "paper-a", "status": "skipped_succeeded", "priority": "critical", "priority_score": 9}
                    ],
                },
            )

            report = summarize_remediation_trend(history_dir=history_dir)

        self.assertEqual(report["count_deltas"]["requested_count"], 1)
        self.assertEqual(report["status_deltas"][0]["status"], "failed")
        self.assertEqual(report["introduced_failures"][0]["paper_id"], "paper-c")
        self.assertEqual(report["resolved_failures"][0]["paper_id"], "paper-b")
        self.assertEqual(report["resolved_failures"][0]["resolved_to"], "absent")
        self.assertEqual(report["newly_skipped_successes"][0]["paper_id"], "paper-a")

    def test_summarize_remediation_trend_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_summarize_remediation_trend_cli(
            argparse.Namespace(history_dir=None, base="previous", candidate="latest", format="markdown"),
            summarize_trend_fn=lambda **_: {
                "base_report_path": "/tmp/remediation/history/baseline.json",
                "candidate_report_path": "/tmp/remediation/history/candidate.json",
                "base_label": "baseline",
                "candidate_label": "candidate",
                "status_deltas": [{"status": "failed", "base_count": 1, "candidate_count": 0, "delta": -1}],
                "count_deltas": {"requested_count": 0, "selected_count": -1, "skipped_count": 1},
                "introduced_failures": [],
                "resolved_failures": [{"paper_id": "paper-b", "resolved_to": "succeeded"}],
                "still_failing": [],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Trend", printed[0])
        self.assertIn("paper-b", printed[0])


if __name__ == "__main__":
    unittest.main()
