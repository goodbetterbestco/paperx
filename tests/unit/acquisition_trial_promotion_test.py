from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.trial_promotion import promote_acquisition_trial
from pipeline.corpus_layout import ProjectLayout


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
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


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionTrialPromotionTest(unittest.TestCase):
    def test_promote_acquisition_trial_replaces_live_sidecars_and_records_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            trial_dir = sources_dir / "trials" / "trial-mathpix"

            _write_json(sources_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(sources_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "docling"})
            _write_json(sources_dir / "layout.json", {"engine": "docling", "blocks": [{"id": "d1"}]})
            _write_json(sources_dir / "math.json", {"engine": "docling", "entries": [{"id": "doc-eq-1"}]})
            _write_json(sources_dir / "acquisition-execution.json", {"executed": {"selected_layout_provider": "docling"}})

            _write_json(trial_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(trial_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "mathpix"})
            _write_json(trial_dir / "layout.json", {"engine": "composed", "blocks": [{"id": "m1"}]})
            _write_json(trial_dir / "math.json", {"engine": "mathpix", "entries": [{"id": "mx-eq-1"}]})
            _write_json(
                trial_dir / "acquisition-execution.json",
                {"executed": {"selected_layout_provider": "mathpix", "selected_math_provider": "mathpix"}},
            )

            summary = promote_acquisition_trial(
                paper_id,
                layout=layout,
                label="trial-mathpix",
                now_iso_impl=lambda: "2026-04-19T00:30:00Z",
            )

            self.assertTrue(summary["promoted"])
            live_layout = json.loads((sources_dir / "layout.json").read_text(encoding="utf-8"))
            live_execution = json.loads((sources_dir / "acquisition-execution.json").read_text(encoding="utf-8"))
            backup_layout = json.loads((trial_dir / "previous-live" / "layout.json").read_text(encoding="utf-8"))
            promotion = json.loads((trial_dir / "promotion.json").read_text(encoding="utf-8"))
            self.assertEqual(live_layout["blocks"][0]["id"], "m1")
            self.assertEqual(live_execution["executed"]["selected_layout_provider"], "mathpix")
            self.assertEqual(live_execution["promotion"]["label"], "trial-mathpix")
            self.assertEqual(live_execution["promotion"]["promoted_at"], "2026-04-19T00:30:00Z")
            self.assertEqual(backup_layout["blocks"][0]["id"], "d1")
            self.assertEqual(promotion["label"], "trial-mathpix")
            self.assertIn("layout.json", summary["previous_live_paths"])

    def test_promote_acquisition_trial_requires_complete_trial_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            trial_dir = layout.canonical_sources_dir(paper_id) / "trials" / "trial-missing"
            _write_json(trial_dir / "layout.json", {"engine": "composed", "blocks": []})

            with self.assertRaises(FileNotFoundError):
                promote_acquisition_trial(paper_id, layout=layout, label="trial-missing")


if __name__ == "__main__":
    unittest.main()
