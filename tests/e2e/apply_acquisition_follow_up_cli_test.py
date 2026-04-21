from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ApplyAcquisitionFollowUpCliE2ETest(unittest.TestCase):
    def test_cli_materializes_follow_up_trial_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "follow_up_project"
            sources_dir = project_dir / "1990_synthetic_test_paper" / "canonical_sources"
            sources_dir.mkdir(parents=True, exist_ok=True)

            (sources_dir / "acquisition-route.json").write_text(
                json.dumps(
                    {
                        "primary_route": "born_digital_scholarly",
                        "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "source-scorecard.json").write_text(
                json.dumps(
                    {
                        "recommended_primary_layout_provider": "docling",
                        "recommended_primary_math_provider": "docling",
                        "layout_recommendation_basis": "fallback_unaccepted",
                        "math_recommendation_basis": "fallback_unaccepted",
                        "providers": [
                            {"provider": "docling", "kind": "layout", "accepted": False, "overall_score": 0.25, "block_count": 1},
                            {"provider": "mathpix", "kind": "layout", "accepted": False, "overall_score": 0.2, "block_count": 1},
                            {"provider": "docling", "kind": "math", "accepted": False, "overall_score": 0.12, "math_entry_count": 1},
                            {"provider": "mathpix", "kind": "math", "accepted": False, "overall_score": 0.09, "math_entry_count": 1},
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "acquisition-execution.json").write_text(
                json.dumps(
                    {
                        "follow_up": {
                            "needs_attention": True,
                            "actions": [
                                {
                                    "product": "layout",
                                    "action": "trial_layout_provider",
                                    "target_provider": "mathpix",
                                },
                                {
                                    "product": "math",
                                    "action": "trial_math_provider",
                                    "target_provider": "mathpix",
                                },
                            ],
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "docling-layout.json").write_text(
                json.dumps(
                    {
                        "engine": "docling",
                        "page_count": 1,
                        "page_sizes_pt": [],
                        "blocks": [{"id": "d1", "page": 1, "order": 1, "role": "paragraph", "text": "Weak body.", "bbox": {}, "meta": {}}],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "mathpix-layout.json").write_text(
                json.dumps(
                    {
                        "engine": "mathpix",
                        "page_count": 1,
                        "page_sizes_pt": [],
                        "blocks": [{"id": "m1", "page": 1, "order": 1, "role": "paragraph", "text": "Better body.", "bbox": {}, "meta": {}}],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "docling-math.json").write_text(
                json.dumps({"engine": "docling", "entries": [{"id": "doc-eq-1", "kind": "display", "display_latex": "x"}]}, indent=2)
                + "\n",
                encoding="utf-8",
            )
            (sources_dir / "mathpix-math.json").write_text(
                json.dumps({"engine": "mathpix", "entries": [{"id": "mx-eq-1", "kind": "display", "display_latex": "y"}]}, indent=2)
                + "\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.apply_acquisition_follow_up",
                    "1990_synthetic_test_paper",
                    "--label",
                    "trial-mathpix",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            summary = json.loads(completed.stdout)
            self.assertTrue(summary["applied"])
            trial_dir = sources_dir / "trials" / "trial-mathpix"
            self.assertTrue((trial_dir / "layout.json").exists())
            self.assertTrue((trial_dir / "math.json").exists())
            execution = json.loads((trial_dir / "acquisition-execution.json").read_text(encoding="utf-8"))
            self.assertEqual(execution["executed"]["selected_layout_provider"], "mathpix")
            self.assertEqual(execution["executed"]["selected_math_provider"], "mathpix")


if __name__ == "__main__":
    unittest.main()
