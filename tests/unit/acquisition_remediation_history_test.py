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


from pipeline.acquisition.remediation_history import list_remediation_history
from pipeline.cli.list_acquisition_remediation_history import run_list_remediation_history_cli


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionRemediationHistoryTest(unittest.TestCase):
    def test_list_remediation_history_reports_saved_runs_with_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            _write_report(
                history_dir / "baseline.json",
                {
                    "snapshot_label": "baseline",
                    "generated_at": "2026-04-19T00:00:00Z",
                    "mode": "execute",
                    "source": {"kind": "live_audit"},
                    "requested_count": 2,
                    "selected_count": 2,
                    "skipped_count": 0,
                    "selected_priorities": ["critical"],
                    "status_counts": {"succeeded": 1, "failed": 1},
                },
            )
            _write_report(
                history_dir / "candidate.json",
                {
                    "snapshot_label": "candidate",
                    "generated_at": "2026-04-19T01:00:00Z",
                    "mode": "execute",
                    "source": {"kind": "report"},
                    "requested_count": 3,
                    "selected_count": 2,
                    "skipped_count": 1,
                    "selected_priorities": ["critical", "high"],
                    "status_counts": {"succeeded": 2, "failed": 0, "skipped_succeeded": 1},
                },
            )

            report = list_remediation_history(history_dir)

        self.assertEqual(report["run_count"], 2)
        self.assertEqual(report["runs"][0]["label"], "baseline")
        self.assertEqual(report["runs"][1]["label"], "candidate")
        self.assertEqual(report["runs"][1]["requested_delta_vs_previous"], 1)
        self.assertEqual(report["runs"][1]["failed_delta_vs_previous"], -1)
        self.assertEqual(report["runs"][1]["skipped_delta_vs_previous"], 1)

    def test_list_remediation_history_cli_prints_markdown(self) -> None:
        printed: list[str] = []
        exit_code = run_list_remediation_history_cli(
            argparse.Namespace(history_dir=None, limit=None, format="markdown"),
            list_history_fn=lambda limit=None: {
                "history_dir": "/tmp/remediation/history",
                "run_count": 1,
                "runs": [
                    {
                        "label": "candidate",
                        "path": "/tmp/remediation/history/candidate.json",
                        "generated_at": "2026-04-19T01:00:00Z",
                        "mode": "execute",
                        "source_kind": "live_audit",
                        "requested_count": 3,
                        "selected_count": 2,
                        "skipped_count": 1,
                        "succeeded_count": 1,
                        "failed_count": 1,
                        "requested_delta_vs_previous": 0,
                        "selected_delta_vs_previous": 0,
                        "skipped_delta_vs_previous": 0,
                        "succeeded_delta_vs_previous": 0,
                        "failed_delta_vs_previous": 0,
                        "selected_priorities": ["critical", "high"],
                    }
                ],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Remediation History", printed[0])
        self.assertIn("candidate", printed[0])


if __name__ == "__main__":
    unittest.main()
