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

        self.assertEqual(len(papers), 7)
        self.assertEqual(
            {paper.paper_id for paper in papers},
            {
                "fixture_paper",
                "math_dense_fixture",
                "scan_image_heavy_fixture",
                "layout_complex_fixture",
                "degraded_garbled_fixture",
                "ocr_forbidden_layout_fixture",
                "ocr_required_layout_fixture",
            },
        )
        self.assertEqual(
            {paper.family for paper in papers},
            {"born_digital_scholarly", "math_dense", "scan_or_image_heavy", "layout_complex", "degraded_or_garbled"},
        )
        self.assertEqual(
            {paper.paper_id: paper.section for paper in papers},
            {
                "fixture_paper": "routing",
                "math_dense_fixture": "routing",
                "layout_complex_fixture": "routing",
                "scan_image_heavy_fixture": "ocr",
                "degraded_garbled_fixture": "ocr",
                "ocr_forbidden_layout_fixture": "ocr",
                "ocr_required_layout_fixture": "ocr",
            },
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

        self.assertEqual(report["paper_count"], 7)
        papers = {paper["paper_id"]: paper for paper in report["papers"]}

        born_digital = {entry["provider"]: entry for entry in papers["fixture_paper"]["providers"]}
        self.assertGreater(born_digital["docling"]["overall_score"], born_digital["mathpix"]["overall_score"])
        self.assertGreater(born_digital["grobid"]["overall_score"], born_digital["mathpix"]["overall_score"])
        self.assertEqual(born_digital["docling"]["metrics"]["title_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metadata_observation"]["provider"], "docling")
        self.assertIn("routing and acquisition scoring", born_digital["docling"]["metadata_observation"]["abstract"].lower())
        self.assertGreaterEqual(born_digital["docling"]["metrics"]["equation_hit_rate"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_layout_provider_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_metadata_provider_match"], 1.0)
        self.assertEqual(born_digital["docling"]["metrics"]["selected_reference_provider_match"], 1.0)
        self.assertEqual(born_digital["docling"]["execution_observation"]["selected_reference_provider"], "docling")
        self.assertEqual(born_digital["docling"]["execution_observation"]["route_reason_codes"], ["scholarly_references"])
        self.assertEqual(born_digital["grobid"]["metadata_observation"]["provider"], "grobid")
        self.assertEqual(born_digital["grobid"]["metrics"]["title_match"], 1.0)
        self.assertEqual(born_digital["grobid"]["metrics"]["recommended_metadata_provider_match"], 1.0)
        self.assertEqual(born_digital["grobid"]["metrics"]["selected_reference_provider_match"], 1.0)
        self.assertNotIn("selected_layout_provider_match", born_digital["grobid"]["metrics"])
        self.assertEqual(born_digital["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)

        math_dense = {entry["provider"]: entry for entry in papers["math_dense_fixture"]["providers"]}
        self.assertGreater(math_dense["mathpix"]["overall_score"], math_dense["docling"]["overall_score"])
        self.assertEqual(math_dense["mathpix"]["metrics"]["route_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["selected_math_provider_match"], 1.0)
        self.assertEqual(math_dense["mathpix"]["metrics"]["recommended_metadata_provider_match"], 1.0)
        self.assertEqual(math_dense["docling"]["metrics"]["selected_math_provider_match"], 0.0)

        scan_heavy = {entry["provider"]: entry for entry in papers["scan_image_heavy_fixture"]["providers"]}
        self.assertGreater(scan_heavy["docling"]["overall_score"], scan_heavy["mathpix"]["overall_score"])
        self.assertEqual(scan_heavy["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(scan_heavy["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(scan_heavy["docling"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(scan_heavy["mathpix"]["metrics"]["ocr_should_run_match"], 0.0)

        layout_complex = {entry["provider"]: entry for entry in papers["layout_complex_fixture"]["providers"]}
        self.assertGreater(layout_complex["docling"]["overall_score"], layout_complex["mathpix"]["overall_score"])
        self.assertEqual(layout_complex["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(layout_complex["docling"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(layout_complex["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(layout_complex["docling"]["metrics"]["selected_layout_provider_match"], 1.0)
        self.assertEqual(layout_complex["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)

        degraded = {entry["provider"]: entry for entry in papers["degraded_garbled_fixture"]["providers"]}
        self.assertGreater(degraded["docling"]["overall_score"], degraded["mathpix"]["overall_score"])
        self.assertEqual(degraded["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(degraded["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(degraded["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(degraded["docling"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(degraded["mathpix"]["metrics"]["ocr_should_run_match"], 0.0)

        ocr_forbidden = {entry["provider"]: entry for entry in papers["ocr_forbidden_layout_fixture"]["providers"]}
        self.assertGreater(ocr_forbidden["docling"]["overall_score"], ocr_forbidden["mathpix"]["overall_score"])
        self.assertEqual(ocr_forbidden["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(ocr_forbidden["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(ocr_forbidden["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(ocr_forbidden["docling"]["metrics"]["selected_math_provider_match"], 1.0)
        self.assertEqual(ocr_forbidden["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)
        self.assertEqual(ocr_forbidden["mathpix"]["metrics"]["selected_math_provider_match"], 0.0)

        ocr_required = {entry["provider"]: entry for entry in papers["ocr_required_layout_fixture"]["providers"]}
        self.assertGreater(ocr_required["docling"]["overall_score"], ocr_required["mathpix"]["overall_score"])
        self.assertEqual(ocr_required["docling"]["metrics"]["route_match"], 1.0)
        self.assertEqual(ocr_required["docling"]["metrics"]["ocr_should_run_match"], 1.0)
        self.assertEqual(ocr_required["docling"]["metrics"]["ocr_policy_match"], 1.0)
        self.assertEqual(ocr_required["docling"]["metrics"]["route_reason_code_recall"], 1.0)
        self.assertEqual(ocr_required["mathpix"]["metrics"]["ocr_should_run_match"], 0.0)
        self.assertEqual(ocr_required["mathpix"]["metrics"]["selected_layout_provider_match"], 0.0)

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
        capabilities = {entry["capability"]: entry["providers"] for entry in report["capabilities"]}
        self.assertEqual(capabilities["layout"][0]["provider"], "docling")
        self.assertEqual(capabilities["math"][0]["provider"], "mathpix")
        metadata_leaders = {entry["provider"] for entry in capabilities["metadata_reference"][:2]}
        self.assertIn("grobid", metadata_leaders)
        family_capabilities = {entry["family"]: entry["capabilities"] for entry in report["family_capabilities"]}
        self.assertIn("born_digital_scholarly", family_capabilities)
        self.assertEqual(
            {entry["capability"] for entry in family_capabilities["born_digital_scholarly"]},
            {"layout", "math", "metadata_reference"},
        )
        self.assertEqual(report["leaders"]["overall"]["provider"], "docling")
        family_leaders = {entry["family"]: entry["leaders"] for entry in report["leaders"]["families"]}
        self.assertIn("math_dense", family_leaders)
        self.assertEqual(family_leaders["math_dense"]["overall"]["provider"], "mathpix")

    def test_benchmark_cli_prints_json_report(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "benchmark"
            json_path = output_dir / "summary.json"
            markdown_path = output_dir / "summary.md"
            status_json_path = output_dir / "status.json"
            status_markdown_path = output_dir / "status.md"
            dashboard_json_path = output_dir / "dashboard.json"
            dashboard_markdown_path = output_dir / "dashboard.md"
            history_dir = output_dir / "history"
            snapshot_json_path = history_dir / "fixture-run.json"
            snapshot_markdown_path = history_dir / "fixture-run.md"
            exit_code = run_benchmark_cli(
                argparse.Namespace(
                    manifest=str(FIXTURE_ROOT / "manifest.json"),
                    format="json",
                    label="fixture-run",
                    dashboard_history_limit=5,
                    dashboard_trend_limit=3,
                ),
                print_fn=printed.append,
                output_dir=output_dir,
                json_report_path=json_path,
                markdown_report_path=markdown_path,
                status_json_report_path=status_json_path,
                status_markdown_report_path=status_markdown_path,
                dashboard_json_report_path=dashboard_json_path,
                dashboard_markdown_report_path=dashboard_markdown_path,
            )

            self.assertEqual(exit_code, 0)
            payload = json.loads(printed[0])
            self.assertEqual(payload["paper_count"], 7)
            self.assertEqual(
                {paper["paper_id"] for paper in payload["papers"]},
                {
                    "fixture_paper",
                    "math_dense_fixture",
                    "scan_image_heavy_fixture",
                    "layout_complex_fixture",
                    "degraded_garbled_fixture",
                    "ocr_forbidden_layout_fixture",
                    "ocr_required_layout_fixture",
                },
            )
            self.assertIn("grobid", {provider["provider"] for provider in payload["aggregate"]})
            self.assertEqual(payload["report_paths"]["json"], str(json_path))
            self.assertEqual(payload["report_paths"]["status_json"], str(status_json_path))
            self.assertEqual(payload["report_paths"]["status_markdown"], str(status_markdown_path))
            self.assertEqual(payload["report_paths"]["snapshot_json"], str(snapshot_json_path))
            self.assertEqual(payload["report_paths"]["snapshot_markdown"], str(snapshot_markdown_path))
            self.assertEqual(payload["report_paths"]["dashboard_json"], str(dashboard_json_path))
            self.assertEqual(payload["report_paths"]["dashboard_markdown"], str(dashboard_markdown_path))
            self.assertEqual(payload["snapshot_label"], "fixture-run")
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertTrue(status_json_path.exists())
            self.assertTrue(status_markdown_path.exists())
            self.assertTrue(dashboard_json_path.exists())
            self.assertTrue(dashboard_markdown_path.exists())
            self.assertTrue(snapshot_json_path.exists())
            self.assertTrue(snapshot_markdown_path.exists())
            status_payload = json.loads(status_json_path.read_text(encoding="utf-8"))
            dashboard_payload = json.loads(dashboard_json_path.read_text(encoding="utf-8"))
            self.assertEqual(status_payload["latest_run"]["label"], "fixture-run")
            self.assertEqual(status_payload["latest_run"]["paper_count"], 7)
            self.assertEqual(dashboard_payload["overview"]["run_count"], 1)
            self.assertEqual(dashboard_payload["overview"]["latest_label"], "fixture-run")

    def test_benchmark_cli_prints_markdown_report(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "benchmark"
            json_path = output_dir / "summary.json"
            markdown_path = output_dir / "summary.md"
            status_json_path = output_dir / "status.json"
            status_markdown_path = output_dir / "status.md"
            dashboard_json_path = output_dir / "dashboard.json"
            dashboard_markdown_path = output_dir / "dashboard.md"
            history_dir = output_dir / "history"
            snapshot_json_path = history_dir / "benchmark-markdown.json"
            snapshot_markdown_path = history_dir / "benchmark-markdown.md"
            exit_code = run_benchmark_cli(
                argparse.Namespace(
                    manifest=str(FIXTURE_ROOT / "manifest.json"),
                    format="markdown",
                    label="benchmark-markdown",
                    dashboard_history_limit=5,
                    dashboard_trend_limit=3,
                ),
                print_fn=printed.append,
                output_dir=output_dir,
                json_report_path=json_path,
                markdown_report_path=markdown_path,
                status_json_report_path=status_json_path,
                status_markdown_report_path=status_markdown_path,
                dashboard_json_report_path=dashboard_json_path,
                dashboard_markdown_report_path=dashboard_markdown_path,
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("# Acquisition Benchmark", printed[0])
            self.assertIn("fixture_paper", printed[0])
            self.assertIn("math_dense_fixture", printed[0])
            self.assertIn("scan_image_heavy_fixture", printed[0])
            self.assertIn("layout_complex_fixture", printed[0])
            self.assertIn("degraded_garbled_fixture", printed[0])
            self.assertIn("ocr_forbidden_layout_fixture", printed[0])
            self.assertIn("ocr_required_layout_fixture", printed[0])
            self.assertIn("grobid", printed[0])
            self.assertIn("metadata target", printed[0])
            self.assertIn("section `routing`", printed[0])
            self.assertIn("OCR policy `skip`", printed[0])
            self.assertIn("## Current Leaders", printed[0])
            self.assertIn("## Capability Ranking", printed[0])
            self.assertIn("## Family Capability Breakdown", printed[0])
            self.assertIn("family `math_dense` overall leader", printed[0])
            self.assertIn(str(json_path), printed[0])
            self.assertIn(str(status_json_path), printed[0])
            self.assertIn(str(status_markdown_path), printed[0])
            self.assertIn(str(snapshot_json_path), printed[0])
            self.assertIn(str(snapshot_markdown_path), printed[0])
            self.assertIn(str(dashboard_json_path), printed[0])
            self.assertIn(str(dashboard_markdown_path), printed[0])
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertTrue(status_json_path.exists())
            self.assertTrue(status_markdown_path.exists())
            self.assertTrue(dashboard_json_path.exists())
            self.assertTrue(dashboard_markdown_path.exists())
            self.assertTrue(snapshot_json_path.exists())
            self.assertTrue(snapshot_markdown_path.exists())
            status_payload = json.loads(status_json_path.read_text(encoding="utf-8"))
            dashboard_payload = json.loads(dashboard_json_path.read_text(encoding="utf-8"))
            self.assertEqual(status_payload["latest_run"]["label"], "benchmark-markdown")
            self.assertEqual(dashboard_payload["overview"]["run_count"], 1)
            self.assertEqual(dashboard_payload["overview"]["latest_label"], "benchmark-markdown")


if __name__ == "__main__":
    unittest.main()
