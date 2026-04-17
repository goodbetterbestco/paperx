import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.corpus_layout as corpus_layout


class CorpusLayoutTest(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("PIPELINE_PROJECT_DIR", None)
        os.environ.pop("PAPER_PIPELINE_PROJECT_DIR", None)
        importlib.reload(corpus_layout)

    def test_project_layout_moves_root_pdfs_and_uses_root_review_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir).resolve()
            (project_dir / "Alpha Paper.pdf").write_bytes(b"%PDF-1.4\nalpha\n")
            (project_dir / "Beta-Paper.pdf").write_bytes(b"%PDF-1.4\nbeta\n")

            os.environ["PIPELINE_PROJECT_DIR"] = str(project_dir)
            importlib.reload(corpus_layout)

            preparation = corpus_layout.prepare_project_inputs()

            self.assertTrue(corpus_layout.PROJECT_MODE)
            self.assertEqual(corpus_layout.SOURCE_DIR, project_dir / "source")
            self.assertEqual(corpus_layout.CORPUS_DIR, project_dir / "corpus")
            self.assertEqual(
                preparation["paper_ids"],
                ["alpha_paper", "beta_paper"],
            )
            self.assertTrue((project_dir / "source" / "alpha_paper.pdf").exists())
            self.assertTrue((project_dir / "source" / "beta_paper.pdf").exists())
            self.assertFalse((project_dir / "Alpha Paper.pdf").exists())
            self.assertFalse((project_dir / "Beta-Paper.pdf").exists())
            self.assertTrue((project_dir / "corpus" / "alpha_paper").is_dir())
            self.assertTrue((project_dir / "corpus" / "beta_paper").is_dir())
            self.assertEqual(
                corpus_layout.paper_pdf_path("alpha_paper"),
                project_dir / "source" / "alpha_paper.pdf",
            )
            self.assertEqual(
                corpus_layout.review_draft_path("alpha_paper"),
                project_dir / "alpha_paper.canonical.review.md",
            )


if __name__ == "__main__":
    unittest.main()
