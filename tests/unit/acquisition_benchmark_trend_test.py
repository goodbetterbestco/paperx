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


from pipeline.acquisition.benchmark_trend import summarize_benchmark_trend
from pipeline.cli.summarize_acquisition_benchmark_trend import run_summarize_benchmark_trend_cli


class AcquisitionBenchmarkTrendTest(unittest.TestCase):
    def test_summarize_benchmark_trend_highlights_improvements_and_regressions(self) -> None:
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
                                    {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.9}]}
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
                                    {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.75}]}
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = summarize_benchmark_trend(history_dir=history_dir, limit=2)

        self.assertEqual(report["top_improvements"][0]["provider"], "docling")
        self.assertEqual(report["top_regressions"][0]["provider"], "mathpix")
        self.assertEqual(report["leaders"]["candidate"]["overall"]["provider"], "docling")
        self.assertEqual(report["leaders"]["candidate"]["families"][0]["family"], "math_dense")
        family = report["families"][0]
        self.assertEqual(family["family"], "math_dense")
        self.assertEqual(family["improvements"][0]["provider"], "docling")
        self.assertEqual(family["regressions"][0]["provider"], "mathpix")
        capability = {item["capability"]: item for item in report["capabilities"]}
        self.assertEqual(capability["layout"]["improvements"][0]["provider"], "docling")
        self.assertEqual(capability["math"]["regressions"][0]["provider"], "mathpix")
        family_capability = {item["capability"]: item for item in family["capabilities"]}
        self.assertEqual(family_capability["math"]["regressions"][0]["provider"], "mathpix")

    def test_summarize_benchmark_trend_cli_prints_markdown(self) -> None:
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

            exit_code = run_summarize_benchmark_trend_cli(
                argparse.Namespace(history_dir=str(history_dir), base="baseline", candidate="candidate", limit=3, format="markdown"),
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark Trend", printed[0])
        self.assertIn("born_digital_scholarly", printed[0])
        self.assertIn("Leader Shift", printed[0])
        self.assertIn("Family Leader Shift", printed[0])
        self.assertIn("Capability Watchlist", printed[0])


if __name__ == "__main__":
    unittest.main()
