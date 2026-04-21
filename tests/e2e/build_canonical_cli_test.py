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
    PAPER_ID,
    TITLE,
    cli_python,
    create_processed_project_fixture,
    project_env,
)


class BuildCanonicalCliE2ETest(unittest.TestCase):
    def test_build_canonical_cli_writes_canonical_for_processed_project_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "build_canonical_project"
            paper_dir = create_processed_project_fixture(project_dir)

            completed = subprocess.run(
                [
                    cli_python(),
                    "-m",
                    "pipeline.cli.build_canonical",
                    PAPER_ID,
                    "--use-external-layout",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=project_env(project_dir),
            )

            payload = json.loads(completed.stdout)
            canonical_path = paper_dir / "canonical.json"

            self.assertEqual(Path(payload["path"]).resolve(), canonical_path.resolve())
            self.assertEqual(payload["sections"], 1)
            self.assertEqual(payload["blocks"], 2)
            self.assertTrue(canonical_path.exists())

            document = json.loads(canonical_path.read_text(encoding="utf-8"))
            self.assertEqual(document["paper_id"], PAPER_ID)
            self.assertEqual(document["title"], TITLE)
            self.assertEqual(document["build"]["sources"]["layout_engine"], "docling")
            self.assertTrue(document["build"]["flags"]["use_external_layout"])


if __name__ == "__main__":
    unittest.main()
