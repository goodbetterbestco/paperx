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


from pipeline.acquisition.benchmark_gates import evaluate_benchmark_gates
from pipeline.cli.check_acquisition_benchmark_gates import run_check_benchmark_gates_cli


def _report_payload(*, label: str, docling_layout_complex: float, docling_scan: float, mathpix_math_dense: float) -> dict[str, object]:
    return {
        "snapshot_label": label,
        "paper_count": 5,
        "aggregate": [
            {"provider": "docling", "avg_overall_score": 0.8, "avg_content_score": 0.7, "avg_execution_score": 0.9},
            {"provider": "grobid", "avg_overall_score": 0.6, "avg_content_score": 0.5, "avg_execution_score": 1.0},
            {"provider": "mathpix", "avg_overall_score": 0.5, "avg_content_score": 0.4, "avg_execution_score": 0.8},
        ],
        "capabilities": [
            {"capability": "layout", "providers": [{"provider": "docling", "avg_score": 0.9}]},
            {"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 0.9}]},
            {"capability": "metadata_reference", "providers": [{"provider": "grobid", "avg_score": 1.0}]},
        ],
        "families": [
            {
                "family": "born_digital_scholarly",
                "providers": [
                    {"provider": "docling", "avg_overall_score": 1.0, "avg_content_score": 1.0, "avg_execution_score": 1.0},
                    {"provider": "grobid", "avg_overall_score": 0.6, "avg_content_score": 0.5, "avg_execution_score": 1.0},
                ],
            },
            {
                "family": "layout_complex",
                "providers": [
                    {"provider": "docling", "avg_overall_score": docling_layout_complex, "avg_content_score": 0.9, "avg_execution_score": 1.0},
                    {"provider": "grobid", "avg_overall_score": 0.6, "avg_content_score": 0.5, "avg_execution_score": 1.0},
                ],
            },
            {
                "family": "scan_or_image_heavy",
                "providers": [
                    {"provider": "docling", "avg_overall_score": docling_scan, "avg_content_score": 1.0, "avg_execution_score": 1.0},
                    {"provider": "grobid", "avg_overall_score": 0.6, "avg_content_score": 0.5, "avg_execution_score": 1.0},
                ],
            },
            {
                "family": "degraded_or_garbled",
                "providers": [
                    {"provider": "grobid", "avg_overall_score": 0.68, "avg_content_score": 0.6, "avg_execution_score": 1.0},
                    {"provider": "docling", "avg_overall_score": 0.56, "avg_content_score": 0.45, "avg_execution_score": 1.0},
                ],
            },
            {
                "family": "math_dense",
                "providers": [
                    {"provider": "mathpix", "avg_overall_score": mathpix_math_dense, "avg_content_score": 0.6, "avg_execution_score": 1.0},
                    {"provider": "docling", "avg_overall_score": 0.42, "avg_content_score": 0.33, "avg_execution_score": 0.83},
                ],
            },
        ],
        "family_capabilities": [
            {"family": "born_digital_scholarly", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 1.0}]}]},
            {"family": "layout_complex", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 1.0}]}]},
            {"family": "scan_or_image_heavy", "capabilities": [{"capability": "layout", "providers": [{"provider": "docling", "avg_score": 1.0}]}]},
            {"family": "degraded_or_garbled", "capabilities": [{"capability": "metadata_reference", "providers": [{"provider": "grobid", "avg_score": 1.0}]}]},
            {"family": "math_dense", "capabilities": [{"capability": "math", "providers": [{"provider": "mathpix", "avg_score": 1.0}]}]},
        ],
    }


class AcquisitionBenchmarkGatesTest(unittest.TestCase):
    def test_evaluate_benchmark_gates_passes_for_stable_family_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = root / "base.json"
            candidate_path = root / "candidate.json"
            base_path.write_text(
                json.dumps(_report_payload(label="base", docling_layout_complex=0.92, docling_scan=1.0, mathpix_math_dense=0.68)),
                encoding="utf-8",
            )
            candidate_path.write_text(
                json.dumps(_report_payload(label="candidate", docling_layout_complex=0.91, docling_scan=0.99, mathpix_math_dense=0.67)),
                encoding="utf-8",
            )

            report = evaluate_benchmark_gates(base_path, candidate_path)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["violation_count"], 0)

    def test_evaluate_benchmark_gates_fails_for_threshold_and_leader_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = root / "base.json"
            candidate_path = root / "candidate.json"
            base_path.write_text(
                json.dumps(_report_payload(label="base", docling_layout_complex=0.92, docling_scan=1.0, mathpix_math_dense=0.68)),
                encoding="utf-8",
            )
            candidate_payload = _report_payload(label="candidate", docling_layout_complex=0.86, docling_scan=0.95, mathpix_math_dense=0.62)
            candidate_families = list(candidate_payload["families"])  # type: ignore[index]
            candidate_families[0] = {
                "family": "born_digital_scholarly",
                "providers": [
                    {"provider": "grobid", "avg_overall_score": 1.01, "avg_content_score": 0.95, "avg_execution_score": 1.0},
                    {"provider": "docling", "avg_overall_score": 1.0, "avg_content_score": 1.0, "avg_execution_score": 1.0},
                ],
            }
            candidate_payload["families"] = candidate_families
            candidate_path.write_text(json.dumps(candidate_payload), encoding="utf-8")

            report = evaluate_benchmark_gates(base_path, candidate_path)

        self.assertEqual(report["status"], "fail")
        self.assertGreaterEqual(report["violation_count"], 2)
        violations = {entry["family"]: entry for entry in report["violations"]}
        self.assertIn("expected_leader_changed", violations["born_digital_scholarly"]["violations"])
        self.assertIn("overall_delta_below_threshold", violations["layout_complex"]["violations"])

    def test_check_benchmark_gates_cli_returns_nonzero_on_violation(self) -> None:
        printed: list[str] = []
        exit_code = run_check_benchmark_gates_cli(
            argparse.Namespace(history_dir=None, base="previous", candidate="latest", format="markdown"),
            evaluate_gates_fn=lambda **_: {
                "status": "fail",
                "base_report_path": "/tmp/base.json",
                "candidate_report_path": "/tmp/candidate.json",
                "base_paper_count": 5,
                "candidate_paper_count": 5,
                "gate_count": 1,
                "violation_count": 1,
                "family_rules": [
                    {
                        "family": "layout_complex",
                        "expected_provider": "docling",
                        "min_overall_delta": -0.03,
                        "observed_overall_delta": -0.05,
                        "candidate_leader": "mathpix",
                        "require_leader": True,
                        "status": "fail",
                        "violations": ["overall_delta_below_threshold", "expected_leader_changed"],
                    }
                ],
                "violations": [
                    {
                        "family": "layout_complex",
                        "expected_provider": "docling",
                        "observed_overall_delta": -0.05,
                        "candidate_leader": "mathpix",
                        "violations": ["overall_delta_below_threshold", "expected_leader_changed"],
                    }
                ],
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertIn("# Acquisition Benchmark Gates", printed[0])
        self.assertIn("layout_complex", printed[0])
        self.assertIn("Violations", printed[0])


if __name__ == "__main__":
    unittest.main()
