from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.remediation_plan_backlog import select_remediation_plan_waves
from pipeline.cli.run_acquisition_remediation_plan_backlog import run_remediation_plan_backlog_cli


class AcquisitionRemediationPlanBacklogTest(unittest.TestCase):
    def test_select_remediation_plan_waves_defaults_to_actionable_statuses(self) -> None:
        report = select_remediation_plan_waves(
            {
                "plan": {"label": "fixture-plan"},
                "waves": [
                    {"wave_id": "wave-pending", "execution_status": "pending"},
                    {"wave_id": "wave-dry", "execution_status": "planned_only"},
                    {"wave_id": "wave-failed", "execution_status": "failed"},
                    {"wave_id": "wave-done", "execution_status": "succeeded"},
                ],
            }
        )

        self.assertEqual(report["selected_statuses"], ["pending", "planned_only", "failed"])
        self.assertEqual(report["wave_ids"], ["wave-pending", "wave-dry", "wave-failed"])

    def test_run_remediation_plan_backlog_cli_dry_run_prints_selected_commands(self) -> None:
        printed: list[str] = []
        exit_code = run_remediation_plan_backlog_cli(
            argparse.Namespace(
                from_plan="latest",
                plan_output_dir="/tmp/plans",
                remediation_history_dir="/tmp/remediation/history",
                queue_output_dir="/tmp/remediation",
                status=[],
                limit=None,
                label_prefix="batch-a",
                dry_run=True,
                fail_fast=False,
                format="json",
            ),
            summarize_status_fn=lambda **_: {
                "plan": {"label": "fixture-plan"},
                "waves": [
                    {"wave_id": "wave-pending", "execution_status": "pending"},
                    {"wave_id": "wave-done", "execution_status": "succeeded"},
                ],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["plan_label"], "fixture-plan")
        self.assertEqual(payload["selected_count"], 1)
        self.assertEqual(payload["waves"][0]["queue_label"], "batch-a-wave-pending")
        self.assertIn("run_acquisition_remediation_wave wave-pending", payload["waves"][0]["command"])

    def test_run_remediation_plan_backlog_cli_executes_selected_waves(self) -> None:
        printed: list[str] = []
        invocations: list[str] = []

        def _run_wave(args, *, print_fn=print, **_kwargs):
            invocations.append(args.wave_id)
            print_fn(
                json.dumps(
                    {
                        "wave_id": args.wave_id,
                        "queue_label": args.label or args.wave_id,
                        "status": "succeeded" if args.wave_id == "wave-a" else "failed",
                    }
                )
            )
            return 0 if args.wave_id == "wave-a" else 1

        exit_code = run_remediation_plan_backlog_cli(
            argparse.Namespace(
                from_plan=None,
                plan_output_dir="/tmp/plans",
                remediation_history_dir="/tmp/remediation/history",
                queue_output_dir="/tmp/remediation",
                status=["failed", "pending"],
                limit=None,
                label_prefix=None,
                dry_run=False,
                fail_fast=True,
                format="json",
            ),
            summarize_status_fn=lambda **_: {
                "plan": {"label": "fixture-plan"},
                "waves": [
                    {"wave_id": "wave-a", "execution_status": "pending"},
                    {"wave_id": "wave-b", "execution_status": "failed"},
                    {"wave_id": "wave-c", "execution_status": "pending"},
                ],
            },
            run_wave_fn=_run_wave,
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(invocations, ["wave-a", "wave-b"])
        payload = json.loads(printed[0])
        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(payload["results"][1]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
