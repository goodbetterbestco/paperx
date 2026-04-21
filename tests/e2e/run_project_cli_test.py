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
    create_source_project_fixture,
    project_env,
)


class RunProjectCliE2ETest(unittest.TestCase):
    def test_run_project_cli_processes_source_project_into_processed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "run_project_fixture"
            source_pdf_path = create_source_project_fixture(project_dir)

            completed = subprocess.run(
                [
                    cli_python(),
                    "-m",
                    "pipeline.cli.run_project",
                    str(project_dir),
                    "--max-workers",
                    "1",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                env=project_env(project_dir, skip_env_local=True),
            )

            payload = json.loads(completed.stdout)
            paper_dir = project_dir / PAPER_ID
            canonical_path = paper_dir / "canonical.json"
            review_path = project_dir / "_runs" / "review_drafts" / f"{PAPER_ID}.canonical.review.md"
            status_path = project_dir / "_runs" / "status.json"
            report_path = project_dir / "_runs" / "final_summary.md"

            self.assertTrue(payload["project_mode"])
            self.assertEqual(payload["paper_ids"], [PAPER_ID])
            self.assertEqual(len(payload["moved_pdfs"]), 1)
            self.assertFalse(source_pdf_path.exists())
            self.assertTrue((paper_dir / f"{PAPER_ID}.pdf").exists())
            self.assertTrue(canonical_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((paper_dir / "canonical_sources").exists())
            self.assertFalse((project_dir / "_canon").exists())
            self.assertEqual(Path(payload["status_path"]).resolve(), status_path.resolve())
            self.assertEqual(Path(payload["report_path"]).resolve(), report_path.resolve())

            document = json.loads(canonical_path.read_text(encoding="utf-8"))
            self.assertEqual(document["title"], TITLE)
            self.assertEqual(document["paper_id"], PAPER_ID)

            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(status["papers"], [PAPER_ID])
            self.assertEqual(status["runs"][0]["papers"][PAPER_ID]["status"], "completed")


if __name__ == "__main__":
    unittest.main()
