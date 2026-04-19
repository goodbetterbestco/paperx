from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


FIXTURE_PROJECT = ROOT / "tests" / "fixtures" / "render_review_project"
PAPER_ID = "1990_synthetic_test_paper"


class RenderReviewCliE2ETest(unittest.TestCase):
    def test_render_review_cli_writes_review_for_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "render_review_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env["PAPER_PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)
            env.pop("PAPER_PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.render_review_from_canonical",
                    PAPER_ID,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(completed.stdout)
            review_path = (project_dir / f"{PAPER_ID}.canonical.review.md").resolve()

            self.assertEqual(Path(payload["path"]).resolve(), review_path)
            self.assertTrue(review_path.exists())

            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("Synthetic Test Paper", review_text)
            self.assertIn("Synthetic abstract for the end-to-end review rendering test.", review_text)
            self.assertIn(r"\(O(N \log N)\)", review_text)
            self.assertIn("# Introduction", review_text)


if __name__ == "__main__":
    unittest.main()
