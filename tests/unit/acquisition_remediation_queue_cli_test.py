from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.run_acquisition_remediation_queue import run_remediation_queue_cli


class AcquisitionRemediationQueueCliTest(unittest.TestCase):
    def test_cli_dry_run_selects_filtered_queue_items(self) -> None:
        printed: list[str] = []

        exit_code = run_remediation_queue_cli(
            argparse.Namespace(
                from_report=None,
                paper_id=["paper-b"],
                priority=[],
                min_priority=None,
                limit=1,
                dry_run=True,
                fail_fast=False,
            ),
            current_layout_fn=lambda: object(),
            audit_acquisition_quality_fn=lambda *, layout=None: {
                "remediation_queue": [
                    {
                        "paper_id": "paper-a",
                        "remediation_priority_label": "critical",
                        "remediation_priority_score": 9,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-a",
                    },
                    {
                        "paper_id": "paper-b",
                        "remediation_priority_label": "high",
                        "remediation_priority_score": 5,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-b",
                    },
                ]
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["mode"], "dry_run")
        self.assertEqual(payload["selected_count"], 1)
        self.assertEqual(payload["selected_papers"], ["paper-b"])
        self.assertEqual(payload["selected_priorities"], ["high"])
        self.assertEqual(payload["results"][0]["status"], "planned")
        self.assertEqual(payload["results"][0]["priority"], "high")
        self.assertIn("paper-b --label trial-b", payload["results"][0]["command"])

    def test_cli_executes_queue_and_stops_after_failure_when_fail_fast(self) -> None:
        printed: list[str] = []
        commands_seen: list[str] = []

        def _run_command(command: str):
            commands_seen.append(command)
            if "paper-b" in command:
                return type("Completed", (), {"returncode": 2, "stdout": "", "stderr": "boom"})()
            return type("Completed", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

        exit_code = run_remediation_queue_cli(
            argparse.Namespace(
                from_report=None,
                paper_id=[],
                priority=[],
                min_priority=None,
                limit=None,
                dry_run=False,
                fail_fast=True,
            ),
            current_layout_fn=lambda: object(),
            audit_acquisition_quality_fn=lambda *, layout=None: {
                "remediation_queue": [
                    {
                        "paper_id": "paper-a",
                        "remediation_priority_label": "critical",
                        "remediation_priority_score": 10,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-a",
                    },
                    {
                        "paper_id": "paper-b",
                        "remediation_priority_label": "high",
                        "remediation_priority_score": 6,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-b",
                    },
                    {
                        "paper_id": "paper-c",
                        "remediation_priority_label": "medium",
                        "remediation_priority_score": 3,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-c --label trial-c",
                    },
                ]
            },
            run_command_fn=_run_command,
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(len(commands_seen), 2)
        payload = json.loads(printed[0])
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["results"][0]["status"], "succeeded")
        self.assertEqual(payload["results"][1]["status"], "failed")
        self.assertEqual(payload["results"][0]["priority"], "critical")
        self.assertEqual(payload["results"][1]["priority"], "high")
        self.assertEqual(payload["results"][1]["returncode"], 2)
        self.assertEqual(payload["results"][1]["stderr"], "boom")

    def test_cli_can_read_saved_report_instead_of_live_audit(self) -> None:
        printed: list[str] = []
        loaded_paths: list[Path] = []

        exit_code = run_remediation_queue_cli(
            argparse.Namespace(
                from_report="/tmp/acquisition-summary.json",
                paper_id=[],
                priority=[],
                min_priority=None,
                limit=None,
                dry_run=True,
                fail_fast=False,
            ),
            load_report_fn=lambda path: (
                loaded_paths.append(path)
                or {
                    "remediation_queue": [
                        {
                            "paper_id": "paper-x",
                            "remediation_priority_label": "medium",
                            "remediation_priority_score": 4,
                            "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-x --label follow-up",
                        }
                    ]
                }
            ),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(loaded_paths, [Path("/tmp/acquisition-summary.json")])
        payload = json.loads(printed[0])
        self.assertEqual(payload["source"]["kind"], "report")
        self.assertEqual(payload["selected_papers"], ["paper-x"])
        self.assertEqual(payload["selected_priorities"], ["medium"])

    def test_cli_filters_queue_by_minimum_priority(self) -> None:
        printed: list[str] = []

        exit_code = run_remediation_queue_cli(
            argparse.Namespace(
                from_report=None,
                paper_id=[],
                priority=[],
                min_priority="high",
                limit=None,
                dry_run=True,
                fail_fast=False,
            ),
            current_layout_fn=lambda: object(),
            audit_acquisition_quality_fn=lambda *, layout=None: {
                "remediation_queue": [
                    {
                        "paper_id": "paper-a",
                        "remediation_priority_label": "critical",
                        "remediation_priority_score": 11,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-a --label trial-a",
                    },
                    {
                        "paper_id": "paper-b",
                        "remediation_priority_label": "high",
                        "remediation_priority_score": 6,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-b --label trial-b",
                    },
                    {
                        "paper_id": "paper-c",
                        "remediation_priority_label": "medium",
                        "remediation_priority_score": 3,
                        "remediation_command": "python3 -m pipeline.cli.remediate_acquisition_follow_up paper-c --label trial-c",
                    },
                ]
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["selected_papers"], ["paper-a", "paper-b"])
        self.assertEqual(payload["selected_priorities"], ["critical", "high"])


if __name__ == "__main__":
    unittest.main()
