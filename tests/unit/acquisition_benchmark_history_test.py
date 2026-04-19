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


from pipeline.acquisition.benchmark_history import list_benchmark_history
from pipeline.cli.list_acquisition_benchmark_history import run_list_benchmark_history_cli


class AcquisitionBenchmarkHistoryTest(unittest.TestCase):
    def test_list_benchmark_history_reports_runs_and_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            (history_dir / "baseline.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "baseline",
                        "paper_count": 3,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8},
                            {"provider": "mathpix", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (history_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "candidate",
                        "paper_count": 4,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9},
                            {"provider": "mathpix", "avg_overall_score": 0.45, "avg_content_score": 0.35, "avg_execution_score": 0.55},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = list_benchmark_history(history_dir)

        self.assertEqual(report["run_count"], 2)
        self.assertEqual([run["label"] for run in report["runs"]], ["baseline", "candidate"])
        latest = report["runs"][-1]
        providers = {item["provider"]: item for item in latest["providers"]}
        self.assertEqual(providers["docling"]["overall_delta_vs_previous"], 0.1)
        self.assertEqual(providers["mathpix"]["overall_delta_vs_previous"], -0.05)

    def test_list_benchmark_history_cli_prints_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            (history_dir / "baseline.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "baseline",
                        "paper_count": 1,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            printed: list[str] = []

            exit_code = run_list_benchmark_history_cli(
                argparse.Namespace(history_dir=str(history_dir), limit=None, format="markdown"),
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark History", printed[0])
        self.assertIn("baseline", printed[0])


if __name__ == "__main__":
    unittest.main()
