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


from tests.e2e.fixture_helpers import CANONICAL_FILENAME, cli_python, corpus_env


FIXTURE_PROJECT = ROOT / "tests" / "fixtures" / "render_review_project"
PAPER_ID = "1990_synthetic_test_paper"


class RenderReviewCliE2ETest(unittest.TestCase):
    def test_render_review_cli_writes_review_for_corpus_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir) / "render_review_corpus"
            shutil.copytree(FIXTURE_PROJECT, corpus_dir)
            (corpus_dir / "_source").mkdir(parents=True, exist_ok=True)
            (corpus_dir / "_data").mkdir(parents=True, exist_ok=True)
            shutil.move(
                str(corpus_dir / PAPER_ID / f"{PAPER_ID}.pdf"),
                str(corpus_dir / "_source" / f"{PAPER_ID}.pdf"),
            )
            shutil.move(
                str(corpus_dir / PAPER_ID / "canonical.json"),
                str(corpus_dir / "_data" / CANONICAL_FILENAME),
            )
            shutil.rmtree(corpus_dir / PAPER_ID)
            completed = subprocess.run(
                [
                    cli_python(),
                    "-m",
                    "pipeline.cli.render_review_from_canonical",
                    PAPER_ID,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=corpus_env(corpus_dir),
            )

            payload = json.loads(completed.stdout)
            review_path = (corpus_dir / "_canon" / f"{PAPER_ID}.canonical.review.md").resolve()

            self.assertEqual(Path(payload["path"]).resolve(), review_path)
            self.assertTrue(review_path.exists())

            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn("Synthetic Test Paper", review_text)
            self.assertIn("Synthetic abstract for the end-to-end review rendering test.", review_text)
            self.assertIn(r"\(O(N \log N)\)", review_text)
            self.assertIn("# Introduction", review_text)


if __name__ == "__main__":
    unittest.main()
