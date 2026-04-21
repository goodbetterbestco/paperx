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
    ABSTRACT,
    PAPER_ID,
    TITLE,
    cli_python,
    create_processed_project_fixture,
    project_env,
)


class BuildReviewCliE2ETest(unittest.TestCase):
    def test_build_review_cli_writes_canonical_and_review_for_processed_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "build_review_project"
            pdf_path = create_processed_project_fixture(project_dir)

            completed = subprocess.run(
                [
                    cli_python(),
                    "-m",
                    "pipeline.cli.build_review",
                    PAPER_ID,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=project_env(project_dir),
            )

            payload = json.loads(completed.stdout)
            canonical_path = project_dir / "_data" / f"{PAPER_ID}.json"
            review_path = project_dir / "_canon" / f"{PAPER_ID}.canonical.review.md"

            self.assertEqual(Path(payload["canonical_path"]).resolve(), canonical_path.resolve())
            self.assertEqual(Path(payload["review_path"]).resolve(), review_path.resolve())
            self.assertTrue(payload["canonical_exists"])
            self.assertTrue(payload["review_exists"])
            self.assertTrue(canonical_path.exists())
            self.assertTrue(review_path.exists())
            self.assertTrue(pdf_path.exists())

            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn(f"# {TITLE}", review_text)
            self.assertIn(ABSTRACT, review_text)
            self.assertIn("## 1 Introduction", review_text)


if __name__ == "__main__":
    unittest.main()
