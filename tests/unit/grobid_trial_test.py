import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.grobid_trial import load_grobid_trial_manifest, run_grobid_trial
from pipeline.acquisition.providers import load_metadata_reference_observation
from pipeline.sources.external import load_grobid_metadata_observation


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

    def test_load_grobid_metadata_observation_reads_sidecar_layout_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            corpus_root = root / "corpus" / "synthetic"
            paper_id = "fixture_paper"
            sources_dir = corpus_root / paper_id / "canonical_sources"
            sources_dir.mkdir(parents=True, exist_ok=True)
            target = sources_dir / "grobid.tei.xml"
            target.write_text(
                (FIXTURE_ROOT / "providers" / "fixture_paper" / "grobid.tei.xml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            from pipeline.corpus_layout import ProjectLayout

            layout = ProjectLayout(
                engine_root=root,
                mode="corpus",
                corpus_name="synthetic",
                project_dir=None,
                corpus_root=corpus_root,
                source_root=corpus_root,
                review_root=corpus_root / "_canon",
                runs_root=corpus_root / "_runs",
                tmp_root=root / "tmp",
                figure_expectations_path=corpus_root / "figure_expectations.json",
            )
            observation = load_grobid_metadata_observation(paper_id, layout=layout)

        self.assertIsNotNone(observation)
        self.assertEqual(observation["provider"], "grobid")
        self.assertEqual(observation["title"], "Synthetic Acquisition Benchmark Paper")

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
