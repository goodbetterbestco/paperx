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

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].paper_id, "fixture_paper")
        self.assertEqual({provider.name for provider in papers[0].providers}, {"docling", "mathpix"})
        for provider in papers[0].providers:
            self.assertTrue(provider.layout_path.is_absolute())

    def test_benchmark_scores_docling_above_mathpix_for_fixture(self) -> None:
        report = run_acquisition_benchmark(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(report["paper_count"], 1)
        paper_report = report["papers"][0]
        self.assertEqual(paper_report["paper_id"], "fixture_paper")
        providers = {entry["provider"]: entry for entry in paper_report["providers"]}
        self.assertGreater(providers["docling"]["overall_score"], providers["mathpix"]["overall_score"])
        self.assertEqual(providers["docling"]["metrics"]["title_match"], 1.0)
        self.assertGreaterEqual(providers["docling"]["metrics"]["equation_hit_rate"], 1.0)

    def test_benchmark_cli_prints_json_report(self) -> None:
        printed: list[str] = []
        exit_code = run_benchmark_cli(
            argparse.Namespace(manifest=str(FIXTURE_ROOT / "manifest.json")),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["paper_count"], 1)
        self.assertEqual(payload["aggregate"][0]["provider"], "docling")


if __name__ == "__main__":
    unittest.main()
