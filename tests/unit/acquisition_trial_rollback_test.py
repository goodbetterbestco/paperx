from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.trial_promotion import rollback_acquisition_trial
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


class AcquisitionTrialRollbackTest(unittest.TestCase):
    def test_rollback_acquisition_trial_restores_previous_live_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            trial_dir = sources_dir / "trials" / "trial-mathpix"
            backup_dir = trial_dir / "previous-live"

            _write_json(sources_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(sources_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "mathpix"})
            _write_json(sources_dir / "layout.json", {"engine": "composed", "blocks": [{"id": "m1"}]})
            _write_json(sources_dir / "math.json", {"engine": "mathpix", "entries": [{"id": "mx-eq-1"}]})
            _write_json(sources_dir / "acquisition-execution.json", {"executed": {"selected_layout_provider": "mathpix"}})

            _write_json(backup_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(backup_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "docling"})
            _write_json(backup_dir / "layout.json", {"engine": "docling", "blocks": [{"id": "d1"}]})
            _write_json(backup_dir / "math.json", {"engine": "docling", "entries": [{"id": "doc-eq-1"}]})
            _write_json(backup_dir / "acquisition-execution.json", {"executed": {"selected_layout_provider": "docling"}})
            _write_json(
                trial_dir / "promotion.json",
                {
                    "label": "trial-mathpix",
                    "previous_live_paths": {
                        "acquisition-route.json": str(backup_dir / "acquisition-route.json"),
                        "source-scorecard.json": str(backup_dir / "source-scorecard.json"),
                        "layout.json": str(backup_dir / "layout.json"),
                        "math.json": str(backup_dir / "math.json"),
                        "acquisition-execution.json": str(backup_dir / "acquisition-execution.json"),
                    },
                },
            )

            summary = rollback_acquisition_trial(
                paper_id,
                layout=layout,
                label="trial-mathpix",
                now_iso_impl=lambda: "2026-04-19T01:00:00Z",
            )

            self.assertTrue(summary["rolled_back"])
            live_layout = json.loads((sources_dir / "layout.json").read_text(encoding="utf-8"))
            live_execution = json.loads((sources_dir / "acquisition-execution.json").read_text(encoding="utf-8"))
            rollback = json.loads((trial_dir / "rollback.json").read_text(encoding="utf-8"))
            self.assertEqual(live_layout["blocks"][0]["id"], "d1")
            self.assertEqual(live_execution["executed"]["selected_layout_provider"], "docling")
            self.assertEqual(live_execution["rollback"]["label"], "trial-mathpix")
            self.assertEqual(live_execution["rollback"]["rolled_back_at"], "2026-04-19T01:00:00Z")
            self.assertEqual(rollback["label"], "trial-mathpix")

    def test_rollback_acquisition_trial_removes_live_files_that_did_not_exist_before_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            trial_dir = sources_dir / "trials" / "trial-mathpix"
            backup_dir = trial_dir / "previous-live"
            backup_dir.mkdir(parents=True, exist_ok=True)

            _write_json(sources_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(sources_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "mathpix"})
            _write_json(sources_dir / "layout.json", {"engine": "composed", "blocks": []})
            _write_json(sources_dir / "math.json", {"engine": "mathpix", "entries": []})
            _write_json(sources_dir / "acquisition-execution.json", {"executed": {"selected_layout_provider": "mathpix"}})

            _write_json(
                trial_dir / "promotion.json",
                {
                    "label": "trial-mathpix",
                    "previous_live_paths": {
                        "acquisition-route.json": str(backup_dir / "acquisition-route.json"),
                    },
                },
            )
            _write_json(backup_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})

            summary = rollback_acquisition_trial(paper_id, layout=layout, label="trial-mathpix")

            self.assertTrue(summary["rolled_back"])
            self.assertFalse((sources_dir / "layout.json").exists())
            self.assertFalse((sources_dir / "math.json").exists())
            self.assertFalse((sources_dir / "acquisition-execution.json").exists())


if __name__ == "__main__":
    unittest.main()
