from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.benchmark import load_benchmark_manifest, run_acquisition_benchmark
from pipeline.cli.run_acquisition_benchmark import run_benchmark_cli


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "acquisition_benchmark"


class AcquisitionBenchmarkTest(unittest.TestCase):
    def test_load_benchmark_manifest_resolves_provider_paths(self) -> None:
        papers = load_benchmark_manifest(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(len(papers), 4)
        self.assertEqual(
            {paper.paper_id for paper in papers},
            {"fixture_paper", "math_dense_fixture", "scan_image_heavy_fixture", "layout_complex_fixture"},
        )
        self.assertEqual(
            {paper.family for paper in papers},
            {"born_digital_scholarly", "math_dense", "scan_or_image_heavy", "layout_complex"},
        )
        for paper in papers:
            self.assertEqual({provider.name for provider in paper.providers}, {"docling", "mathpix"})
            for provider in paper.providers:
                self.assertTrue(provider.layout_path.is_absolute())
                self.assertTrue(provider.execution_path is None or provider.execution_path.is_absolute())

    def test_benchmark_scores_docling_above_mathpix_for_fixture(self) -> None:
        report = run_acquisition_benchmark(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(report["paper_count"], 4)
        papers = {paper["paper_id"]: paper for paper in report["papers"]}

        born_digital = {entry["provider"]: entry for entry in papers["fixture_paper"]["providers"]}
        self.assertGreater(born_digital["docling"]["overall_score"], born_digital["mathpix"]["overall_score"])
        self.assertEqual(born_digital["docling"]["metrics"]["title_match"], 1.0)
        self.assertGreaterEqual(born_digital["docling"]["metrics"]["equation_hit_rate"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_layout_provider_match"], 1.0)
        self.assertEqual(born_digital["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)

        math_dense = {entry["provider"]: entry for entry in papers["math_dense_fixture"]["providers"]}
        self.assertGreater(math_dense["mathpix"]["overall_score"], math_dense["docling"]["overall_score"])
        self.assertEqual(math_dense["mathpix"]["metrics"]["route_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["selected_math_provider_match"], 1.0)
        self.assertEqual(math_dense["docling"]["metrics"]["selected_math_provider_match"], 0.0)

        scan_heavy = {entry["provider"]: entry for entry in papers["scan_image_heavy_fixture"]["providers"]}
        self.assertGreater(scan_heavy["docling"]["overall_score"], scan_heavy["mathpix"]["overall_score"])
        self.assertEqual(scan_heavy["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(scan_heavy["mathpix"]["metrics"]["ocr_should_run_match"], 0.0)

        layout_complex = {entry["provider"]: entry for entry in papers["layout_complex_fixture"]["providers"]}
        self.assertGreater(layout_complex["docling"]["overall_score"], layout_complex["mathpix"]["overall_score"])
        self.assertEqual(layout_complex["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(layout_complex["docling"]["metrics"]["selected_layout_provider_match"], 1.0)
        self.assertEqual(layout_complex["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)
        self.assertEqual(
            {entry["family"] for entry in report["families"]},
            {"born_digital_scholarly", "math_dense", "scan_or_image_heavy", "layout_complex"},
        )

    def test_benchmark_cli_prints_json_report(self) -> None:
        printed: list[str] = []
        exit_code = run_benchmark_cli(
            argparse.Namespace(manifest=str(FIXTURE_ROOT / "manifest.json"), format="json"),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["paper_count"], 4)
        self.assertEqual(
            {paper["paper_id"] for paper in payload["papers"]},
            {"fixture_paper", "math_dense_fixture", "scan_image_heavy_fixture", "layout_complex_fixture"},
        )

    def test_benchmark_cli_prints_markdown_report(self) -> None:
        printed: list[str] = []
        exit_code = run_benchmark_cli(
            argparse.Namespace(manifest=str(FIXTURE_ROOT / "manifest.json"), format="markdown"),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("# Acquisition Benchmark", printed[0])
        self.assertIn("fixture_paper", printed[0])
        self.assertIn("math_dense_fixture", printed[0])
        self.assertIn("scan_image_heavy_fixture", printed[0])
        self.assertIn("layout_complex_fixture", printed[0])


if __name__ == "__main__":
    unittest.main()
