from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.follow_up import apply_acquisition_follow_up
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
        review_root=corpus_root / "review_drafts",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionFollowUpTest(unittest.TestCase):
    def test_apply_acquisition_follow_up_writes_trial_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)

            _write_json(
                sources_dir / "acquisition-route.json",
                {
                    "primary_route": "born_digital_scholarly",
                    "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
                },
            )
            _write_json(
                sources_dir / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "docling",
                    "recommended_primary_math_provider": "docling",
                    "recommended_primary_metadata_provider": "docling",
                    "recommended_primary_reference_provider": "docling",
                    "layout_recommendation_basis": "fallback_unaccepted",
                    "math_recommendation_basis": "fallback_unaccepted",
                    "metadata_recommendation_basis": "accepted",
                    "reference_recommendation_basis": "accepted",
                    "providers": [
                        {
                            "provider": "docling",
                            "kind": "layout",
                            "accepted": False,
                            "overall_score": 0.25,
                            "block_count": 1,
                        },
                        {
                            "provider": "mathpix",
                            "kind": "layout",
                            "accepted": False,
                            "overall_score": 0.2,
                            "block_count": 1,
                        },
                        {
                            "provider": "docling",
                            "kind": "math",
                            "accepted": False,
                            "overall_score": 0.12,
                            "math_entry_count": 1,
                        },
                        {
                            "provider": "mathpix",
                            "kind": "math",
                            "accepted": False,
                            "overall_score": 0.09,
                            "math_entry_count": 1,
                        },
                    ],
                },
            )
            _write_json(
                sources_dir / "acquisition-execution.json",
                {
                    "follow_up": {
                        "needs_attention": True,
                        "actions": [
                            {
                                "product": "layout",
                                "reason": "layout_provider_not_accepted",
                                "action": "trial_layout_provider",
                                "target_provider": "mathpix",
                            },
                            {
                                "product": "math",
                                "reason": "math_provider_not_accepted",
                                "action": "trial_math_provider",
                                "target_provider": "mathpix",
                            },
                        ],
                    }
                },
            )
            _write_json(
                sources_dir / "docling-layout.json",
                {
                    "engine": "docling",
                    "pdf_path": "docs/synthetic.pdf",
                    "page_count": 1,
                    "page_sizes_pt": [],
                    "blocks": [
                        {"id": "d1", "page": 1, "order": 1, "role": "paragraph", "text": "Weak body text.", "bbox": {}, "meta": {}},
                    ],
                },
            )
            _write_json(
                sources_dir / "mathpix-layout.json",
                {
                    "engine": "mathpix",
                    "pdf_path": "docs/synthetic.pdf",
                    "page_count": 1,
                    "page_sizes_pt": [],
                    "blocks": [
                        {"id": "m1", "page": 1, "order": 1, "role": "heading", "text": "Abstract", "bbox": {}, "meta": {}},
                        {"id": "m2", "page": 1, "order": 2, "role": "paragraph", "text": "Alternative abstract body.", "bbox": {}, "meta": {}},
                    ],
                },
            )
            _write_json(
                sources_dir / "docling-math.json",
                {"engine": "docling", "entries": [{"id": "doc-eq-1", "kind": "display", "display_latex": "x"}]},
            )
            _write_json(
                sources_dir / "mathpix-math.json",
                {"engine": "mathpix", "entries": [{"id": "mx-eq-1", "kind": "display", "display_latex": "y"}]},
            )

            summary = apply_acquisition_follow_up(
                paper_id,
                layout=layout,
                label="trial-mathpix",
                now_iso_impl=lambda: "2026-04-19T00:00:00Z",
            )

            self.assertTrue(summary["applied"])
            trial_dir = sources_dir / "trials" / "trial-mathpix"
            self.assertEqual(summary["trial_dir"], str(trial_dir))
            trial_scorecard = json.loads((trial_dir / "source-scorecard.json").read_text(encoding="utf-8"))
            trial_execution = json.loads((trial_dir / "acquisition-execution.json").read_text(encoding="utf-8"))
            self.assertEqual(trial_scorecard["recommended_primary_layout_provider"], "mathpix")
            self.assertEqual(trial_scorecard["recommended_primary_math_provider"], "mathpix")
            self.assertEqual(trial_scorecard["layout_recommendation_basis"], "trial_override")
            self.assertEqual(trial_scorecard["math_recommendation_basis"], "trial_override")
            self.assertEqual(trial_execution["executed"]["selected_layout_provider"], "mathpix")
            self.assertEqual(trial_execution["executed"]["selected_math_provider"], "mathpix")
            self.assertFalse(trial_execution["follow_up"]["needs_attention"])
            self.assertEqual(trial_execution["trial"]["label"], "trial-mathpix")
            self.assertEqual(
                trial_execution["trial"]["applied_actions"],
                [
                    {"product": "layout", "target_provider": "mathpix"},
                    {"product": "math", "target_provider": "mathpix"},
                ],
            )

    def test_apply_acquisition_follow_up_returns_noop_when_no_trial_actions_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            _write_json(sources_dir / "acquisition-route.json", {"primary_route": "born_digital_scholarly"})
            _write_json(sources_dir / "source-scorecard.json", {"recommended_primary_layout_provider": "docling"})
            _write_json(
                sources_dir / "acquisition-execution.json",
                {"follow_up": {"needs_attention": True, "actions": [{"action": "manual_review_layout"}]}},
            )

            summary = apply_acquisition_follow_up(paper_id, layout=layout)

            self.assertFalse(summary["applied"])
            self.assertEqual(summary["reason"], "no_trial_actions")


if __name__ == "__main__":
    unittest.main()
