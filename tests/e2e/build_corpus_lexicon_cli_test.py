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


class BuildCorpusLexiconCliE2ETest(unittest.TestCase):
    def test_build_corpus_lexicon_cli_writes_project_lexicon_for_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "lexicon_project"
            shutil.copytree(FIXTURE_PROJECT, project_dir)
            lexicon_path = project_dir / "corpus_lexicon.json"
            env = os.environ.copy()
            env["PIPELINE_PROJECT_DIR"] = str(project_dir)
            env["PAPER_PIPELINE_PROJECT_DIR"] = str(project_dir)
            env.pop("PIPELINE_CORPUS_DIR", None)
            env.pop("PAPER_PIPELINE_CORPUS_DIR", None)

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.build_corpus_lexicon",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            payload = json.loads(completed.stdout)

            self.assertEqual(Path(payload["path"]).resolve(), lexicon_path.resolve())
            self.assertGreater(payload["terms"], 0)
            self.assertEqual(payload["authors"], 1)
            self.assertGreater(payload["acronyms"], 0)
            self.assertTrue(lexicon_path.exists())

            lexicon = json.loads(lexicon_path.read_text(encoding="utf-8"))
            self.assertEqual(lexicon["sources"]["canonical_papers"], 1)
            self.assertEqual(lexicon["authors"][0]["canonical"], "Ada Example")
            self.assertEqual(lexicon["authors"][0]["papers"], ["1990_synthetic_test_paper"])


if __name__ == "__main__":
    unittest.main()
