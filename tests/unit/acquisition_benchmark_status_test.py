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


from pipeline.acquisition.benchmark_status import summarize_latest_benchmark_status
from pipeline.cli.show_acquisition_benchmark_status import run_show_benchmark_status_cli


class AcquisitionBenchmarkStatusTest(unittest.TestCase):
    def test_summarize_latest_benchmark_status_returns_latest_run_and_trend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            history_dir = Path(temp_dir) / "history"
            history_dir.mkdir(parents=True, exist_ok=True)
            (history_dir / "baseline.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "baseline",
                        "paper_count": 1,
                        "aggregate": [{"provider": "docling", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8}],
                        "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]}],
                        "families": [{"family": "math_dense", "providers": [{"provider": "docling", "avg_overall_score": 0.7, "avg_content_score": 0.6, "avg_execution_score": 0.8}]}],
                        "family_capabilities": [{"family": "math_dense", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.7}]}]}],
                    }
                ),
                encoding="utf-8",
            )
            (history_dir / "candidate.json").write_text(
                json.dumps(
                    {
                        "snapshot_label": "candidate",
                        "paper_count": 1,
                        "aggregate": [{"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9}],
                        "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.85}]}],
                        "families": [{"family": "math_dense", "providers": [{"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9}]}],
                        "family_capabilities": [{"family": "math_dense", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.85}]}]}],
                    }
                ),
                encoding="utf-8",
            )

            report = summarize_latest_benchmark_status(history_dir=history_dir, limit=2)

        self.assertEqual(report["latest_run"]["label"], "candidate")
        self.assertEqual(report["trend"]["top_improvements"][0]["provider"], "docling")
        self.assertEqual(report["latest_run"]["capabilities"][0]["capability"], "layout")
        self.assertEqual(report["trend"]["capabilities"][0]["capability"], "layout")

    def test_show_benchmark_status_cli_prints_markdown(self) -> None:
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

            exit_code = run_show_benchmark_status_cli(
                argparse.Namespace(history_dir=str(history_dir), limit=3, format="markdown"),
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark Status", printed[0])
        self.assertIn("born_digital_scholarly", printed[0])
        self.assertIn("Latest Capability Scores", printed[0])
