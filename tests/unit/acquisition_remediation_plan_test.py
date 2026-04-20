from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.remediation_plan import plan_remediation_waves
from pipeline.cli.plan_acquisition_remediation_waves import run_plan_remediation_waves_cli


class AcquisitionRemediationPlanTest(unittest.TestCase):
    def test_plan_remediation_waves_groups_recovery_and_provider_focused_batches(self) -> None:
        report = {
            "remediation_queue": [
                {
                    "paper_id": "paper-a",
                    "remediation_priority_label": "critical",
                    "remediation_priority_score": 9,
                    "remediation_priority_reasons": ["required_ocr_not_applied"],
                    "follow_up_actions": [{"target_provider": "mathpix"}],
                    "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-mathpix",
                },
                {
                    "paper_id": "paper-b",
                    "remediation_priority_label": "high",
                    "remediation_priority_score": 6,
                    "remediation_priority_reasons": ["fallback_recommendation"],
                    "follow_up_actions": [{"target_provider": "mathpix"}],
                    "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-mathpix",
                },
                {
                    "paper_id": "paper-c",
                    "remediation_priority_label": "high",
                    "remediation_priority_score": 5,
                    "remediation_priority_reasons": ["follow_up_actions"],
                    "follow_up_actions": [{"target_provider": "grobid"}],
                    "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-c --label trial-grobid",
                },
                {
                    "paper_id": "paper-d",
                    "remediation_priority_label": "medium",
                    "remediation_priority_score": 3,
                    "remediation_priority_reasons": ["follow_up_actions"],
                    "follow_up_actions": [{"target_provider": None}],
                    "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-d --label follow-up",
                },
            ]
        }

        module = sys.modules["pipeline.acquisition.remediation_plan"]
        original_status = module.summarize_latest_remediation_status
        original_trend = module.summarize_remediation_trend
        try:
            module.summarize_latest_remediation_status = lambda **_: {"failures": [{"paper_id": "paper-a"}]}
            module.summarize_remediation_trend = lambda **_: {
                "still_failing": [{"paper_id": "paper-a"}],
                "introduced_failures": [{"paper_id": "paper-c"}],
            }
            plan = plan_remediation_waves(report, from_report_path="/tmp/audit.json", history_dir="/tmp/remediation/history", max_wave_size=2)
        finally:
            module.summarize_latest_remediation_status = original_status
            module.summarize_remediation_trend = original_trend

        self.assertEqual(plan["queue_count"], 4)
        self.assertEqual(plan["wave_count"], 4)
        self.assertEqual(plan["waves"][0]["wave_kind"], "recovery")
        self.assertEqual(plan["waves"][0]["paper_ids"], ["paper-a"])
        self.assertTrue(plan["waves"][0]["fail_fast_recommended"])
        self.assertIn("--from-report /tmp/audit.json", plan["waves"][0]["execution_command"])
        self.assertEqual(plan["waves"][1]["wave_kind"], "recovery")
        self.assertEqual(plan["waves"][1]["paper_ids"], ["paper-c"])
        self.assertEqual(plan["waves"][2]["provider_focus"], "mathpix")
        self.assertEqual(plan["waves"][2]["paper_ids"], ["paper-b"])
        self.assertEqual(plan["waves"][3]["wave_kind"], "manual")
        self.assertEqual(plan["waves"][3]["paper_ids"], ["paper-d"])

    def test_plan_remediation_waves_cli_prints_commands(self) -> None:
        printed: list[str] = []
        exit_code = run_plan_remediation_waves_cli(
            argparse.Namespace(from_report=None, history_dir=None, max_wave_size=2, format="commands"),
            current_layout_fn=lambda: object(),
            audit_acquisition_quality_fn=lambda *, layout=None: {"remediation_queue": []},
            plan_waves_fn=lambda report, **kwargs: {
                "waves": [
                    {"execution_command": "python3 -m pipeline.cli.run_acquisition_remediation_queue --paper-id paper-a"},
                    {"execution_command": "python3 -m pipeline.cli.run_acquisition_remediation_queue --paper-id paper-b"},
                ]
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            printed[0],
            "\n".join(
                [
                    "python3 -m pipeline.cli.run_acquisition_remediation_queue --paper-id paper-a",
                    "python3 -m pipeline.cli.run_acquisition_remediation_queue --paper-id paper-b",
                ]
            ),
        )

    def test_plan_remediation_waves_cli_prints_json(self) -> None:
        printed: list[str] = []
        exit_code = run_plan_remediation_waves_cli(
            argparse.Namespace(from_report=None, history_dir=None, max_wave_size=3, format="json"),
            current_layout_fn=lambda: object(),
            audit_acquisition_quality_fn=lambda *, layout=None: {"remediation_queue": []},
            plan_waves_fn=lambda report, **kwargs: {"wave_count": 0, "waves": []},
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["wave_count"], 0)


if __name__ == "__main__":
    unittest.main()
