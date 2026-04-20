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


from pipeline.acquisition.remediation_dashboard import summarize_remediation_dashboard
from pipeline.cli.show_acquisition_remediation_dashboard import run_show_remediation_dashboard_cli


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionRemediationDashboardTest(unittest.TestCase):
    def test_summarize_remediation_dashboard_combines_status_history_and_trend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "remediation"
            history_dir = output_dir / "history"
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
                        {"paper_id": "paper-b", "status": "failed", "priority": "high", "priority_score": 5}
                    ],
                    "skipped_papers": [],
                },
            )
            latest_payload = {
                "snapshot_label": "candidate",
                "generated_at": "2026-04-19T01:00:00Z",
                "mode": "execute",
                "source": {"kind": "live_audit"},
                "requested_count": 3,
                "selected_count": 2,
                "skipped_count": 1,
                "selected_papers": ["paper-c", "paper-d"],
                "selected_priorities": ["critical", "medium"],
                "status_counts": {"succeeded": 1, "failed": 1, "skipped_succeeded": 1},
                "report_paths": {
                    "json": str(output_dir / "summary.json"),
                    "snapshot_json": str(history_dir / "candidate.json"),
                },
                "results": [
                    {"paper_id": "paper-c", "status": "failed", "priority": "medium", "priority_score": 3},
                    {"paper_id": "paper-d", "status": "succeeded", "priority": "critical", "priority_score": 9},
                ],
                "skipped_papers": [
                    {"paper_id": "paper-a", "status": "skipped_succeeded", "priority": "critical", "priority_score": 9}
                ],
            }
            _write_report(history_dir / "candidate.json", latest_payload)
            _write_report(output_dir / "summary.json", latest_payload)

            report = summarize_remediation_dashboard(history_dir=history_dir, history_limit=5, trend_limit=2)

        self.assertEqual(report["overview"]["run_count"], 2)
        self.assertEqual(report["overview"]["latest_label"], "candidate")
        self.assertTrue(report["overview"]["comparison_available"])
        self.assertEqual(report["alerts"]["introduced_failures"][0]["paper_id"], "paper-c")

    def test_show_remediation_dashboard_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_show_remediation_dashboard_cli(
            argparse.Namespace(history_dir=None, history_limit=5, trend_limit=3, format="markdown"),
            summarize_dashboard_fn=lambda **_: {
                "overview": {
                    "history_dir": "/tmp/remediation/history",
                    "run_count": 2,
                    "latest_label": "candidate",
                    "previous_label": "baseline",
                    "latest_requested_count": 3,
                    "latest_selected_count": 2,
                    "latest_skipped_count": 1,
                    "latest_failed_count": 1,
                    "comparison_available": True,
                },
                "latest_run": {
                    "mode": "execute",
                    "generated_at": "2026-04-19T01:00:00Z",
                    "status_counts": {"failed": 1, "succeeded": 1},
                },
                "trend": {"status_deltas": [{"status": "failed", "base_count": 1, "candidate_count": 1, "delta": 0}]},
                "recent_history": [{"label": "candidate", "selected_count": 2, "skipped_count": 1, "succeeded_count": 1, "failed_count": 1}],
                "alerts": {
                    "introduced_failures": [{"paper_id": "paper-c", "priority": "medium"}],
                    "still_failing": [],
                    "resolved_failures": [{"paper_id": "paper-b", "resolved_to": "succeeded"}],
                },
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Dashboard", printed[0])
        self.assertIn("paper-c", printed[0])
        self.assertIn("paper-b", printed[0])


if __name__ == "__main__":
    unittest.main()
