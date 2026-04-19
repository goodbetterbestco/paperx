import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.grobid_trial import load_grobid_trial_manifest, run_grobid_trial
from pipeline.acquisition.providers import load_metadata_reference_observation


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "grobid_trial"


class GrobidTrialTest(unittest.TestCase):
    def test_load_metadata_reference_observation_parses_grobid_tei(self) -> None:
        observation = load_metadata_reference_observation(
            "grobid",
            FIXTURE_ROOT / "providers" / "fixture_paper" / "grobid.tei.xml",
        )

        self.assertEqual(observation.provider, "grobid")
        self.assertEqual(observation.title, "Synthetic Acquisition Benchmark Paper")
        self.assertIn("structured document extraction", observation.abstract.lower())
        self.assertEqual(len(observation.references), 2)
        self.assertIn("Journal of Tests", observation.references[0])

    def test_load_grobid_trial_manifest_resolves_fixture_paths(self) -> None:
        papers = load_grobid_trial_manifest(FIXTURE_ROOT / "manifest.json")
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].paper_id, "fixture_paper")
        self.assertTrue(papers[0].gold_path.exists())
        self.assertTrue(papers[0].artifact_path.exists())

    def test_run_grobid_trial_reports_per_paper_and_aggregate_scores(self) -> None:
        report = run_grobid_trial(FIXTURE_ROOT / "manifest.json")

        self.assertEqual(report["paper_count"], 1)
        self.assertEqual(report["aggregate"]["provider"], "grobid")
        self.assertGreaterEqual(report["aggregate"]["avg_overall_score"], 0.95)
        paper = report["papers"][0]
        self.assertEqual(paper["provider"], "grobid")
        self.assertEqual(paper["metrics"]["title_match"], 1.0)
        self.assertGreaterEqual(paper["metrics"]["reference_hit_rate"], 0.95)
        self.assertEqual(json.loads(json.dumps(paper["observation"]))["provider"], "grobid")


if __name__ == "__main__":
    unittest.main()
