from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


MINIMAL_PDF = b"%PDF-1.4\nsynthetic\n"


class ResetCorpusToSourceCliE2ETest(unittest.TestCase):
    def test_cli_resets_processed_corpus_back_to_source_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "stepview"
            paper_dir = corpus_dir / "1990_synthetic_test_paper"
            paper_dir.mkdir(parents=True, exist_ok=True)
            (paper_dir / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)
            (paper_dir / "canonical.json").write_text('{"title": "Synthetic"}\n', encoding="utf-8")
            (corpus_dir / "_canon").mkdir(parents=True, exist_ok=True)
            (corpus_dir / "_canon" / "1990_synthetic_test_paper.canonical.review.md").write_text(
                "# Synthetic\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.reset_corpus_to_source",
                    str(corpus_dir),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["state"], "source")
            self.assertTrue((corpus_dir / "_source" / "1990_synthetic_test_paper.pdf").exists())
            self.assertFalse(paper_dir.exists())
            self.assertFalse((corpus_dir / "_canon").exists())


if __name__ == "__main__":
    unittest.main()
