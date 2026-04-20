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


from pipeline.acquisition.benchmark import load_benchmark_manifest, run_acquisition_benchmark
from pipeline.cli.run_acquisition_benchmark import run_benchmark_cli


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "acquisition_benchmark"


class AcquisitionBenchmarkTest(unittest.TestCase):
    def test_load_benchmark_manifest_resolves_provider_paths(self) -> None:
        papers = load_benchmark_manifest(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(len(papers), 5)
        self.assertEqual(
            {paper.paper_id for paper in papers},
            {
                "fixture_paper",
                "math_dense_fixture",
                "scan_image_heavy_fixture",
                "layout_complex_fixture",
                "degraded_garbled_fixture",
            },
        )
        self.assertEqual(
            {paper.family for paper in papers},
            {"born_digital_scholarly", "math_dense", "scan_or_image_heavy", "layout_complex", "degraded_or_garbled"},
        )
        for paper in papers:
            self.assertEqual({provider.name for provider in paper.providers}, {"docling", "grobid", "mathpix"})
            for provider in paper.providers:
                self.assertTrue(
                    (provider.layout_path is not None and provider.layout_path.is_absolute())
                    or (provider.metadata_path is not None and provider.metadata_path.is_absolute())
                )
                if provider.name == "grobid":
                    self.assertIsNone(provider.layout_path)
                    self.assertIsNotNone(provider.metadata_path)
                self.assertTrue(provider.execution_path is None or provider.execution_path.is_absolute())

    def test_benchmark_scores_docling_above_mathpix_for_fixture(self) -> None:
        report = run_acquisition_benchmark(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(report["paper_count"], 5)
        papers = {paper["paper_id"]: paper for paper in report["papers"]}

        born_digital = {entry["provider"]: entry for entry in papers["fixture_paper"]["providers"]}
        self.assertGreater(born_digital["docling"]["overall_score"], born_digital["mathpix"]["overall_score"])
        self.assertGreater(born_digital["grobid"]["overall_score"], born_digital["mathpix"]["overall_score"])
        self.assertEqual(born_digital["docling"]["metrics"]["title_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metadata_observation"]["provider"], "docling")
        self.assertIn("routing and acquisition scoring", born_digital["docling"]["metadata_observation"]["abstract"].lower())
        self.assertGreaterEqual(born_digital["docling"]["metrics"]["equation_hit_rate"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_layout_provider_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_metadata_provider_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_reference_provider_match"], 1.0)
        self.assertEqual(born_digital["grobid"]["metadata_observation"]["provider"], "grobid")
        self.assertEqual(born_digital["grobid"]["metrics"]["title_match"], 1.0)
        self.assertEqual(born_digital["grobid"]["metrics"]["recommended_metadata_provider_match"], 1.0)
        self.assertEqual(born_digital["grobid"]["metrics"]["selected_reference_provider_match"], 1.0)
        self.assertNotIn("selected_layout_provider_match", born_digital["grobid"]["metrics"])
        self.assertEqual(born_digital["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)

        math_dense = {entry["provider"]: entry for entry in papers["math_dense_fixture"]["providers"]}
        self.assertGreater(math_dense["mathpix"]["overall_score"], math_dense["docling"]["overall_score"])
        self.assertEqual(math_dense["mathpix"]["metrics"]["route_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["selected_math_provider_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["recommended_metadata_provider_match"], 1.0)
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

        degraded = {entry["provider"]: entry for entry in papers["degraded_garbled_fixture"]["providers"]}
        self.assertGreater(degraded["docling"]["overall_score"], degraded["mathpix"]["overall_score"])
        self.assertEqual(degraded["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(degraded["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(degraded["mathpix"]["metrics"]["ocr_should_run_match"], 0.0)
        self.assertEqual(
            {entry["family"] for entry in report["families"]},
            {
                "born_digital_scholarly",
                "math_dense",
                "scan_or_image_heavy",
                "layout_complex",
                "degraded_or_garbled",
            },
        )

    def test_benchmark_cli_prints_json_report(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "benchmark"
            json_path = output_dir / "summary.json"
            markdown_path = output_dir / "summary.md"
            history_dir = output_dir / "history"
            snapshot_json_path = history_dir / "fixture-run.json"
            snapshot_markdown_path = history_dir / "fixture-run.md"
            exit_code = run_benchmark_cli(
                argparse.Namespace(manifest=str(FIXTURE_ROOT / "manifest.json"), format="json", label="fixture-run"),
                print_fn=printed.append,
                output_dir=output_dir,
                json_report_path=json_path,
                markdown_report_path=markdown_path,
            )

            self.assertEqual(exit_code, 0)
            payload = json.loads(printed[0])
            self.assertEqual(payload["paper_count"], 5)
            self.assertEqual(
                {paper["paper_id"] for paper in payload["papers"]},
                {
                    "fixture_paper",
                    "math_dense_fixture",
                    "scan_image_heavy_fixture",
                    "layout_complex_fixture",
                    "degraded_garbled_fixture",
                },
            )
            self.assertIn("grobid", {provider["provider"] for provider in payload["aggregate"]})
            self.assertEqual(payload["report_paths"]["json"], str(json_path))
            self.assertEqual(payload["report_paths"]["snapshot_json"], str(snapshot_json_path))
            self.assertEqual(payload["report_paths"]["snapshot_markdown"], str(snapshot_markdown_path))
            self.assertEqual(payload["snapshot_label"], "fixture-run")
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertTrue(snapshot_json_path.exists())
            self.assertTrue(snapshot_markdown_path.exists())

    def test_benchmark_cli_prints_markdown_report(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "benchmark"
            json_path = output_dir / "summary.json"
            markdown_path = output_dir / "summary.md"
            history_dir = output_dir / "history"
            snapshot_json_path = history_dir / "benchmark-markdown.json"
            snapshot_markdown_path = history_dir / "benchmark-markdown.md"
            exit_code = run_benchmark_cli(
                argparse.Namespace(
                    manifest=str(FIXTURE_ROOT / "manifest.json"),
                    format="markdown",
                    label="benchmark-markdown",
                ),
                print_fn=printed.append,
                output_dir=output_dir,
                json_report_path=json_path,
                markdown_report_path=markdown_path,
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("# Acquisition Benchmark", printed[0])
            self.assertIn("fixture_paper", printed[0])
            self.assertIn("math_dense_fixture", printed[0])
            self.assertIn("scan_image_heavy_fixture", printed[0])
            self.assertIn("layout_complex_fixture", printed[0])
            self.assertIn("degraded_garbled_fixture", printed[0])
            self.assertIn("grobid", printed[0])
            self.assertIn("metadata target", printed[0])
            self.assertIn(str(json_path), printed[0])
            self.assertIn(str(snapshot_json_path), printed[0])
            self.assertIn(str(snapshot_markdown_path), printed[0])
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertTrue(snapshot_json_path.exists())
            self.assertTrue(snapshot_markdown_path.exists())


if __name__ == "__main__":
    unittest.main()
