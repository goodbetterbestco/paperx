from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.benchmark_reports import (
    aggregate_provider_score_map,
    benchmark_report_label,
    benchmark_capability_score_maps,
    family_provider_score_maps,
    family_capability_score_maps,
    capability_leader_rows,
    leader_for_metric,
    list_history_reports,
    provider_leader_summary,
    resolve_benchmark_report_path,
)


class AcquisitionBenchmarkReportsTest(unittest.TestCase):
    def test_resolve_benchmark_report_path_supports_labels_and_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            older_path = history_dir / "older.json"
            newer_path = history_dir / "newer.json"
            older_path.write_text("{}", encoding="utf-8")
            newer_path.write_text("{}", encoding="utf-8")

            self.assertEqual(resolve_benchmark_report_path("older", history_dir=history_dir), older_path.resolve())
            self.assertEqual(resolve_benchmark_report_path("latest", history_dir=history_dir), newer_path.resolve())
            self.assertEqual(resolve_benchmark_report_path("previous", history_dir=history_dir), older_path.resolve())

    def test_list_history_reports_returns_sorted_json_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            older_path = history_dir / "alpha.json"
            newer_path = history_dir / "zeta.json"
            older_path.write_text("{}", encoding="utf-8")
            newer_path.write_text("{}", encoding="utf-8")
            os.utime(older_path, (100, 100))
            os.utime(newer_path, (200, 200))
            (history_dir / "ignore.txt").write_text("{}", encoding="utf-8")

            reports = list_history_reports(history_dir)

        self.assertEqual([path.name for path in reports], ["alpha.json", "zeta.json"])

    def test_report_shape_helpers_extract_label_and_provider_maps(self) -> None:
        report = {
            "snapshot_label": "candidate-run",
            "aggregate": [
                {"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9}
            ],
            "families": [
                {
                    "family": "math_dense",
                    "providers": [
                        {"provider": "mathpix", "avg_overall_score": 0.75, "avg_content_score": 0.65, "avg_execution_score": 0.85}
                    ],
                }
            ],
            "capabilities": [
                {
                    "capability": "metadata_reference",
                    "providers": [{"provider": "grobid", "avg_score": 0.95}],
                }
            ],
            "family_capabilities": [
                {
                    "family": "math_dense",
                    "capabilities": [
                        {
                            "capability": "math",
                            "providers": [{"provider": "mathpix", "avg_score": 0.88}],
                        }
                    ],
                }
            ],
        }

        self.assertEqual(benchmark_report_label(report), "candidate-run")
        self.assertEqual(benchmark_report_label({}, fallback_path="history/fallback.json"), "fallback")
        aggregate_scores = aggregate_provider_score_map(report, round_values=True)
        family_scores = family_provider_score_maps(report, round_values=True)
        capability_scores = benchmark_capability_score_maps(report, round_values=True)
        family_capability_scores = family_capability_score_maps(report, round_values=True)

        self.assertEqual(aggregate_scores["docling"]["overall"], 0.8)
        self.assertEqual(family_scores["math_dense"]["mathpix"]["execution"], 0.85)
        self.assertEqual(capability_scores["metadata_reference"]["grobid"]["score"], 0.95)
        self.assertEqual(family_capability_scores["math_dense"]["math"]["mathpix"]["score"], 0.88)
        self.assertEqual(leader_for_metric(report["aggregate"], value_key="avg_overall_score")["provider"], "docling")
        self.assertEqual(
            provider_leader_summary(
                report["aggregate"],
                overall_key="avg_overall_score",
                content_key="avg_content_score",
                execution_key="avg_execution_score",
            )["overall"]["provider"],
            "docling",
        )
        self.assertEqual(capability_leader_rows(report["capabilities"])[0]["leader"]["provider"], "grobid")


if __name__ == "__main__":
    unittest.main()
