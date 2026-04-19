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


from pipeline.acquisition.benchmark_compare import compare_benchmark_reports
from pipeline.cli.compare_acquisition_benchmark import run_compare_benchmark_cli


class AcquisitionBenchmarkCompareTest(unittest.TestCase):
    def test_compare_benchmark_reports_computes_provider_and_family_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = root / "base.json"
            candidate_path = root / "candidate.json"
            base_path.write_text(
                json.dumps(
                    {
                        "paper_count": 2,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8},
                            {"provider": "mathpix", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6},
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
                    }
                ),
                encoding="utf-8",
            )
            candidate_path.write_text(
                json.dumps(
                    {
                        "paper_count": 2,
                        "aggregate": [
                            {"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9},
                            {"provider": "mathpix", "avg_overall_score": 0.45, "avg_content_score": 0.35, "avg_execution_score": 0.55},
                        ],
                        "families": [
                            {
                                "family": "math_dense",
                                "providers": [
                                    {"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6},
                                    {"provider": "mathpix", "avg_overall_score": 0.75, "avg_content_score": 0.65, "avg_execution_score": 0.85},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = compare_benchmark_reports(base_path, candidate_path)

        aggregate = {item["provider"]: item for item in report["aggregate"]}
        self.assertEqual(aggregate["docling"]["overall_delta"], 0.1)
        self.assertEqual(aggregate["mathpix"]["overall_delta"], -0.05)
        family = report["families"][0]
        self.assertEqual(family["family"], "math_dense")
        family_providers = {item["provider"]: item for item in family["providers"]}
        self.assertEqual(family_providers["docling"]["overall_delta"], 0.2)
        self.assertEqual(family_providers["mathpix"]["overall_delta"], -0.05)

    def test_compare_benchmark_cli_prints_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = root / "base.json"
            candidate_path = root / "candidate.json"
            payload = {
                "paper_count": 1,
                "aggregate": [{"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6}],
                "families": [{"family": "born_digital_scholarly", "providers": [{"provider": "docling", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.6}]}],
            }
            base_path.write_text(json.dumps(payload), encoding="utf-8")
            candidate_path.write_text(json.dumps(payload), encoding="utf-8")
            printed: list[str] = []

            exit_code = run_compare_benchmark_cli(
                argparse.Namespace(base=str(base_path), candidate=str(candidate_path), format="markdown"),
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark Comparison", printed[0])
        self.assertIn("born_digital_scholarly", printed[0])


if __name__ == "__main__":
    unittest.main()
