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


from tests.e2e.fixture_helpers import (
    CANONICAL_FILENAME,
    PAPER_ID,
    PAPER_UID,
    TITLE,
    corpus_env,
    cli_python,
    create_processed_corpus_fixture,
)


class BuildCanonicalCliE2ETest(unittest.TestCase):
    def test_build_canonical_cli_writes_canonical_for_processed_corpus_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir) / "build_canonical_corpus"
            pdf_path = create_processed_corpus_fixture(corpus_dir)

            completed = subprocess.run(
                [
                    cli_python(),
                    "-m",
                    "pipeline.cli.build_canonical",
                    PAPER_ID,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=corpus_env(corpus_dir),
            )

            payload = json.loads(completed.stdout)
            canonical_path = corpus_dir / "_data" / CANONICAL_FILENAME

            self.assertEqual(Path(payload["path"]).resolve(), canonical_path.resolve())
            self.assertGreaterEqual(payload["sections"], 2)
            self.assertGreaterEqual(payload["blocks"], 2)
            self.assertTrue(canonical_path.exists())
            self.assertTrue(pdf_path.exists())

            document = json.loads(canonical_path.read_text(encoding="utf-8"))
            self.assertEqual(document["paper_id"], PAPER_ID)
            self.assertEqual(document["paper_uid"], PAPER_UID)
            self.assertEqual(document["title"], TITLE)
            self.assertEqual(document["build"]["sources"]["layout_engine"], "docling")
            self.assertEqual(document["_decision_artifacts"]["acquisition"]["owners"]["layout"], "docling")
            self.assertFalse(document["_decision_artifacts"]["acquisition"]["recovery"]["layout_composed"])
            self.assertIn("pdf", document["build"]["inputs"])


if __name__ == "__main__":
    unittest.main()
