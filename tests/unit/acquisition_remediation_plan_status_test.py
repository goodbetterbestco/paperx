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


from pipeline.acquisition.remediation_plan_status import summarize_remediation_plan_status
from pipeline.cli.show_acquisition_remediation_plan_status import run_show_remediation_plan_status_cli


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionRemediationPlanStatusTest(unittest.TestCase):
    def test_summarize_remediation_plan_status_reconciles_wave_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            plan_output_dir = temp_root / "plans"
            remediation_history_dir = temp_root / "remediation" / "history"
            _write_report(
                plan_output_dir / "summary.json",
                {
                    "snapshot_label": "fixture-plan",
                    "generated_at": "2026-04-19T02:00:00Z",
                    "source": {"kind": "report"},
                    "queue_count": 3,
                    "wave_count": 3,
                    "waves": [
                        {
                            "wave_id": "recovery-critical-mathpix-1",
                            "wave_kind": "recovery",
                            "priority_label": "critical",
                            "provider_focus": "mathpix",
                            "paper_count": 1,
                            "paper_ids": ["paper-a"],
                        },
                        {
                            "wave_id": "remediation-high-grobid-1",
                            "wave_kind": "remediation",
                            "priority_label": "high",
                            "provider_focus": "grobid",
                            "paper_count": 1,
                            "paper_ids": ["paper-b"],
                        },
                        {
                            "wave_id": "manual-medium-manual-1",
                            "wave_kind": "manual",
                            "priority_label": "medium",
                            "provider_focus": "manual",
                            "paper_count": 1,
                            "paper_ids": ["paper-c"],
                        },
                    ],
                },
            )
            _write_report(
                remediation_history_dir / "20260419T020500Z.json",
                {
                    "snapshot_label": "20260419T020500Z",
                    "generated_at": "2026-04-19T02:05:00Z",
                    "mode": "dry_run",
                    "plan": {"label": "fixture-plan", "wave_id": "remediation-high-grobid-1"},
                    "status_counts": {"planned": 1},
                    "selected_count": 1,
                },
            )
            _write_report(
                remediation_history_dir / "20260419T021000Z.json",
                {
                    "snapshot_label": "20260419T021000Z",
                    "generated_at": "2026-04-19T02:10:00Z",
                    "mode": "execute",
                    "plan": {"label": "fixture-plan", "wave_id": "recovery-critical-mathpix-1"},
                    "status_counts": {"succeeded": 1},
                    "selected_count": 1,
                },
            )
            _write_report(
                remediation_history_dir / "20260419T021500Z.json",
                {
                    "snapshot_label": "20260419T021500Z",
                    "generated_at": "2026-04-19T02:15:00Z",
                    "mode": "execute",
                    "plan": {"label": "fixture-plan", "wave_id": "orphan-wave"},
                    "status_counts": {"failed": 1},
                    "selected_count": 1,
                },
            )

            report = summarize_remediation_plan_status(
                plan_output_dir=plan_output_dir,
                remediation_history_dir=remediation_history_dir,
            )

        self.assertEqual(report["plan"]["label"], "fixture-plan")
        self.assertEqual(report["overview"]["planned_waves"], 3)
        self.assertEqual(report["overview"]["succeeded_waves"], 1)
        self.assertEqual(report["overview"]["planned_only_waves"], 1)
        self.assertEqual(report["overview"]["pending_waves"], 1)
        self.assertEqual(report["overview"]["orphan_run_count"], 1)
        self.assertEqual(report["pending_waves"][0]["wave_id"], "manual-medium-manual-1")
        self.assertEqual(report["planned_only_waves"][0]["wave_id"], "remediation-high-grobid-1")

    def test_show_remediation_plan_status_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_show_remediation_plan_status_cli(
            argparse.Namespace(
                from_plan=None,
                plan_output_dir="/tmp/plans",
                remediation_history_dir="/tmp/remediation/history",
                format="markdown",
            ),
            summarize_status_fn=lambda **_: {
                "plan": {
                    "label": "fixture-plan",
                    "path": "/tmp/plans/summary.json",
                    "generated_at": "2026-04-19T02:00:00Z",
                    "source": {"kind": "report"},
                    "queue_count": 3,
                },
                "overview": {
                    "planned_waves": 3,
                    "execute_attempts": 1,
                    "dry_run_attempts": 1,
                    "orphan_run_count": 0,
                    "wave_status_counts": {"pending": 1, "planned_only": 1, "succeeded": 1, "failed": 0},
                },
                "failed_waves": [],
                "pending_waves": [{"wave_id": "manual-medium-manual-1", "wave_kind": "manual", "provider_focus": "manual", "paper_count": 1}],
                "planned_only_waves": [{"wave_id": "remediation-high-grobid-1", "attempt_count": 1, "latest_run": {"label": "20260419T020500Z"}}],
                "orphan_runs": [],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation Plan Status", printed[0])
        self.assertIn("fixture-plan", printed[0])
        self.assertIn("manual-medium-manual-1", printed[0])


if __name__ == "__main__":
    unittest.main()
