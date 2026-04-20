from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.remediation_plan_dashboard import summarize_remediation_plan_dashboard
from pipeline.cli.show_acquisition_remediation_plan_dashboard import run_show_remediation_plan_dashboard_cli


class AcquisitionRemediationPlanDashboardTest(unittest.TestCase):
    def test_summarize_remediation_plan_dashboard_combines_status_and_history(self) -> None:
        report = summarize_remediation_plan_dashboard(
            from_plan=None,
            plan_output_dir="/tmp/plans",
            remediation_history_dir="/tmp/remediation/history",
            history_limit=5,
            wave_limit=2,
            summarize_status_fn=lambda **_: {
                "plan": {
                    "label": "candidate",
                    "generated_at": "2026-04-19T02:00:00Z",
                    "queue_count": 4,
                },
                "overview": {
                    "planned_waves": 4,
                    "pending_waves": 1,
                    "planned_only_waves": 1,
                    "succeeded_waves": 1,
                    "failed_waves": 1,
                    "execute_attempts": 2,
                    "dry_run_attempts": 1,
                    "orphan_run_count": 1,
                },
                "failed_waves": [{"wave_id": "wave-failed", "execution_status": "failed", "latest_run": {"label": "run-2"}}],
                "pending_waves": [{"wave_id": "wave-pending", "execution_status": "pending", "latest_run": None}],
                "planned_only_waves": [{"wave_id": "wave-dry", "execution_status": "planned_only", "latest_run": {"label": "run-1"}}],
                "orphan_runs": [{"label": "run-orphan", "plan_wave_id": "wave-z", "mode": "execute"}],
            },
            list_history_fn=lambda **_: {
                "plan_count": 2,
                "plans": [
                    {"label": "baseline", "wave_count": 3, "succeeded_waves": 1, "failed_waves": 1, "pending_waves": 1},
                    {"label": "candidate", "wave_count": 4, "succeeded_waves": 1, "failed_waves": 1, "pending_waves": 1},
                ],
            },
        )

        self.assertEqual(report["overview"]["plan_label"], "candidate")
        self.assertEqual(report["overview"]["saved_plan_count"], 2)
        self.assertEqual(report["alerts"]["failed_waves"][0]["wave_id"], "wave-failed")
        self.assertEqual(report["alerts"]["orphan_runs"][0]["label"], "run-orphan")

    def test_show_remediation_plan_dashboard_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_show_remediation_plan_dashboard_cli(
            argparse.Namespace(
                from_plan=None,
                plan_output_dir="/tmp/plans",
                remediation_history_dir="/tmp/remediation/history",
                history_limit=5,
                wave_limit=3,
                format="markdown",
            ),
            summarize_dashboard_fn=lambda **_: {
                "overview": {
                    "plan_label": "candidate",
                    "plan_generated_at": "2026-04-19T02:00:00Z",
                    "queue_count": 4,
                    "planned_waves": 4,
                    "pending_waves": 1,
                    "planned_only_waves": 1,
                    "succeeded_waves": 1,
                    "failed_waves": 1,
                    "execute_attempts": 2,
                    "dry_run_attempts": 1,
                    "orphan_run_count": 1,
                },
                "alerts": {
                    "failed_waves": [{"wave_id": "wave-failed", "execution_status": "failed", "latest_run": {"label": "run-2"}}],
                    "pending_waves": [{"wave_id": "wave-pending", "execution_status": "pending", "latest_run": None}],
                    "planned_only_waves": [{"wave_id": "wave-dry", "execution_status": "planned_only", "latest_run": {"label": "run-1"}}],
                    "orphan_runs": [{"label": "run-orphan", "plan_wave_id": "wave-z", "mode": "execute"}],
                },
                "recent_history": [{"label": "candidate", "wave_count": 4, "succeeded_waves": 1, "failed_waves": 1, "pending_waves": 1}],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Plan Dashboard", printed[0])
        self.assertIn("wave-failed", printed[0])
        self.assertIn("run-orphan", printed[0])


if __name__ == "__main__":
    unittest.main()
