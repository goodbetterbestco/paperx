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


from pipeline.acquisition.benchmark_dashboard import summarize_benchmark_dashboard
from pipeline.cli.show_acquisition_benchmark_dashboard import run_show_benchmark_dashboard_cli


class AcquisitionBenchmarkDashboardTest(unittest.TestCase):
    def test_summarize_benchmark_dashboard_combines_status_comparison_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            (history_dir / "baseline.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "baseline",
                        "paper_count": 2,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8},
                            {"provider": "mathpix", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6},
                        ],
                        "capabilities": [
                            {"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]},
                            {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.9}]},
                        ],
                        "families": [
                            {
                                "family": "math_dense",
                                "providers": [
                                    {"provider": "docling", "avg_overall_score": 0.3, "avg_content_score": 0.2, "avg_execution_score": 0.4},
                                    {"provider": "mathpix", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9},
                                ],
                            }
                        ],
                        "family_capabilities": [
                            {
                                "family": "math_dense",
                                "capabilities": [
                                    {"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]},
                                    {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.9}]},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (history_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "candidate",
                        "paper_count": 2,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.82, "avg_content_score": 0.72, "avg_execution_score": 0.92},
                            {"provider": "mathpix", "avg_overall_score": 0.42, "avg_content_score": 0.32, "avg_execution_score": 0.52},
                        ],
                        "capabilities": [
                            {"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.85}]},
                            {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.7}]},
                        ],
                        "families": [
                            {
                                "family": "math_dense",
                                "providers": [
                                    {"provider": "docling", "avg_overall_score": 0.55, "avg_content_score": 0.45, "avg_execution_score": 0.65},
                                    {"provider": "mathpix", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8},
                                ],
                            }
                        ],
                        "family_capabilities": [
                            {
                                "family": "math_dense",
                                "capabilities": [
                                    {"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.85}]},
                                    {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.7}]},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = summarize_benchmark_dashboard(history_dir=history_dir, history_limit=5, trend_limit=3)

        self.assertEqual(report["overview"]["run_count"], 2)
        self.assertEqual(report["overview"]["latest_label"], "candidate")
        self.assertEqual(report["overview"]["previous_label"], "baseline")
        self.assertTrue(report["overview"]["comparison_available"])
        self.assertEqual(report["leaders"]["overall"]["provider"], "docling")
        self.assertEqual(report["comparison"]["aggregate"][0]["provider"], "docling")
        self.assertEqual(report["alerts"]["provider_regressions"][0]["provider"], "mathpix")
        self.assertEqual(report["alerts"]["capability_regressions"][0]["capability"], "math")
        self.assertEqual(report["recent_history"][-1]["label"], "candidate")

    def test_dashboard_cli_prints_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "snapshot_label": "baseline",
                "paper_count": 1,
                "aggregate": [{"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6}],
                "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]}],
                "families": [{"family": "born_digital_scholarly", "providers": [{"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6}]}],
                "family_capabilities": [{"family": "born_digital_scholarly", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]}]}],
            }
            (history_dir / "baseline.json").write_text(json.dumps(payload), encoding="utf-8")
            (history_dir / "candidate.json").write_text(json.dumps(payload), encoding="utf-8")
            printed: list[str] = []

            exit_code = run_show_benchmark_dashboard_cli(
                argparse.Namespace(history_dir=str(history_dir), history_limit=5, trend_limit=3, format="markdown"),
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark Dashboard", printed[0])
        self.assertIn("Comparison available", printed[0])
        self.assertIn("Current Leaders", printed[0])
        self.assertIn("Regression Watch", printed[0])
        self.assertIn("Recent Runs", printed[0])

    def test_dashboard_cli_can_load_saved_artifact(self) -> None:
        printed: list[str] = []
        exit_code = run_show_benchmark_dashboard_cli(
            argparse.Namespace(history_dir=None, history_limit=5, trend_limit=3, format="markdown", from_artifacts=True),
            load_dashboard_fn=lambda **_: {
                "overview": {"history_dir": "/tmp/history", "run_count": 1, "latest_label": "candidate"},
                "leaders": {"overall": {"provider": "docling", "overall": 0.8}},
                "latest_run": {"providers": []},
                "alerts": {},
                "recent_history": [],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark Dashboard", printed[0])
        self.assertIn("candidate", printed[0])


if __name__ == "__main__":
    unittest.main()
