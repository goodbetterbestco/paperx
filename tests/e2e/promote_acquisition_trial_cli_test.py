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


class PromoteAcquisitionTrialCliE2ETest(unittest.TestCase):
    def test_cli_promotes_trial_bundle_into_live_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "promotion_project"
            sources_dir = project_dir / "1990_synthetic_test_paper" / "canonical_sources"
            trial_dir = sources_dir / "trials" / "trial-mathpix"
            trial_dir.mkdir(parents=True, exist_ok=True)

            (sources_dir / "acquisition-route.json").write_text(
                json.dumps({"primary_route": "born_digital_scholarly"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (sources_dir / "source-scorecard.json").write_text(
                json.dumps({"recommended_primary_layout_provider": "docling"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (sources_dir / "layout.json").write_text(
                json.dumps({"engine": "docling", "blocks": [{"id": "d1"}]}, indent=2) + "\n",
                encoding="utf-8",
            )
            (sources_dir / "math.json").write_text(
                json.dumps({"engine": "docling", "entries": [{"id": "doc-eq-1"}]}, indent=2) + "\n",
                encoding="utf-8",
            )
            (sources_dir / "acquisition-execution.json").write_text(
                json.dumps({"executed": {"selected_layout_provider": "docling"}}, indent=2) + "\n",
                encoding="utf-8",
            )

            (trial_dir / "acquisition-route.json").write_text(
                json.dumps({"primary_route": "born_digital_scholarly"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (trial_dir / "source-scorecard.json").write_text(
                json.dumps({"recommended_primary_layout_provider": "mathpix"}, indent=2) + "\n",
                encoding="utf-8",
            )
            (trial_dir / "layout.json").write_text(
                json.dumps({"engine": "composed", "blocks": [{"id": "m1"}]}, indent=2) + "\n",
                encoding="utf-8",
            )
            (trial_dir / "math.json").write_text(
                json.dumps({"engine": "mathpix", "entries": [{"id": "mx-eq-1"}]}, indent=2) + "\n",
                encoding="utf-8",
            )
            (trial_dir / "acquisition-execution.json").write_text(
                json.dumps({"executed": {"selected_layout_provider": "mathpix"}}, indent=2) + "\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.promote_acquisition_trial",
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
            self.assertTrue(summary["promoted"])
            live_layout = json.loads((sources_dir / "layout.json").read_text(encoding="utf-8"))
            live_execution = json.loads((sources_dir / "acquisition-execution.json").read_text(encoding="utf-8"))
            self.assertEqual(live_layout["blocks"][0]["id"], "m1")
            self.assertEqual(live_execution["promotion"]["label"], "trial-mathpix")
            self.assertTrue((trial_dir / "previous-live" / "layout.json").exists())


if __name__ == "__main__":
    unittest.main()
