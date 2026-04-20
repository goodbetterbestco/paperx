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


from pipeline.acquisition.remediation_plan_history import list_remediation_plan_history
from pipeline.cli.list_acquisition_remediation_plan_history import run_list_remediation_plan_history_cli


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionRemediationPlanHistoryTest(unittest.TestCase):
    def test_list_remediation_plan_history_reports_saved_plan_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            plan_history_dir = temp_root / "plans" / "history"
            remediation_history_dir = temp_root / "remediation" / "history"
            _write_report(
                plan_history_dir / "baseline.json",
                {
                    "snapshot_label": "baseline",
                    "generated_at": "2026-04-19T01:00:00Z",
                    "source": {"kind": "report"},
                    "queue_count": 2,
                    "wave_count": 2,
                    "waves": [
                        {"wave_id": "wave-a", "paper_ids": ["paper-a"]},
                        {"wave_id": "wave-b", "paper_ids": ["paper-b"]},
                    ],
                },
            )
            _write_report(
                plan_history_dir / "candidate.json",
                {
                    "snapshot_label": "candidate",
                    "generated_at": "2026-04-19T02:00:00Z",
                    "source": {"kind": "report"},
                    "queue_count": 3,
                    "wave_count": 3,
                    "waves": [
                        {"wave_id": "wave-a", "paper_ids": ["paper-a"]},
                        {"wave_id": "wave-b", "paper_ids": ["paper-b"]},
                        {"wave_id": "wave-c", "paper_ids": ["paper-c"]},
                    ],
                },
            )
            _write_report(
                remediation_history_dir / "20260419T020500Z.json",
                {
                    "snapshot_label": "20260419T020500Z",
                    "generated_at": "2026-04-19T02:05:00Z",
                    "mode": "execute",
                    "plan": {"label": "candidate", "wave_id": "wave-a"},
                    "status_counts": {"succeeded": 1},
                },
            )
            _write_report(
                remediation_history_dir / "20260419T021000Z.json",
                {
                    "snapshot_label": "20260419T021000Z",
                    "generated_at": "2026-04-19T02:10:00Z",
                    "mode": "dry_run",
                    "plan": {"label": "candidate", "wave_id": "wave-b"},
                    "status_counts": {"planned": 1},
                },
            )

            report = list_remediation_plan_history(
                plan_history_dir=plan_history_dir,
                remediation_history_dir=remediation_history_dir,
            )

        self.assertEqual(report["plan_count"], 2)
        self.assertEqual(report["plans"][1]["label"], "candidate")
        self.assertEqual(report["plans"][1]["succeeded_waves"], 1)
        self.assertEqual(report["plans"][1]["planned_only_waves"], 1)
        self.assertEqual(report["plans"][1]["pending_waves"], 1)

    def test_list_remediation_plan_history_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_list_remediation_plan_history_cli(
            argparse.Namespace(
                plan_history_dir="/tmp/plans/history",
                remediation_history_dir="/tmp/remediation/history",
                limit=None,
                format="markdown",
            ),
            list_history_fn=lambda **_: {
                "history_dir": "/tmp/plans/history",
                "plan_count": 1,
                "plans": [
                    {
                        "label": "candidate",
                        "path": "/tmp/plans/history/candidate.json",
                        "generated_at": "2026-04-19T02:00:00Z",
                        "source_kind": "report",
                        "queue_count": 3,
                        "wave_count": 3,
                        "pending_waves": 1,
                        "planned_only_waves": 1,
                        "succeeded_waves": 1,
                        "failed_waves": 0,
                        "execute_attempts": 1,
                        "dry_run_attempts": 1,
                        "orphan_run_count": 0,
                    }
                ],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Plan History", printed[0])
        self.assertIn("candidate", printed[0])


if __name__ == "__main__":
    unittest.main()
