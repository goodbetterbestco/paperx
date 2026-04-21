from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


FIXTURE_PROJECT = ROOT / "tests" / "fixtures" / "render_review_project"


class ExportTitlesCliE2ETest(unittest.TestCase):
    def test_export_titles_and_abstracts_cli_writes_markdown_for_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "export_titles_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            output_path = project_dir / "tmp" / "titles_and_abstracts.md"
            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.export_titles_and_abstracts",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(completed.stdout)

            self.assertEqual(Path(payload["path"]).resolve(), output_path.resolve())
            self.assertEqual(payload["papers"], 1)
            self.assertTrue(output_path.exists())

            exported = output_path.read_text(encoding="utf-8")
            self.assertIn("Synthetic Test Paper", exported)
            self.assertIn("Synthetic abstract for the end-to-end review rendering test.", exported)


if __name__ == "__main__":
    unittest.main()
