import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.corpus_layout as corpus_layout


class CorpusLayoutTest(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("PIPELINE_PROJECT_DIR", None)
        importlib.reload(corpus_layout)

    def test_project_layout_moves_root_pdfs_into_processed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir).resolve()
            (project_dir / "Alpha Paper.pdf").write_bytes(b"%PDF-1.4\nalpha\n")
            (project_dir / "Beta-Paper.pdf").write_bytes(b"%PDF-1.4\nbeta\n")

            os.environ["PIPELINE_PROJECT_DIR"] = str(project_dir)
            importlib.reload(corpus_layout)

            preparation = corpus_layout.prepare_project_inputs()
            layout = corpus_layout.current_layout()

            self.assertTrue(corpus_layout.PROJECT_MODE)
            self.assertEqual(corpus_layout.SOURCE_DIR, project_dir / "_source")
            self.assertEqual(corpus_layout.CORPUS_DIR, project_dir)
            self.assertEqual(layout.mode, "project")
            self.assertEqual(layout.project_dir, project_dir)
            self.assertEqual(layout.source_root, project_dir / "_source")
            self.assertEqual(layout.corpus_root, project_dir)
            self.assertEqual(
                preparation["paper_ids"],
                ["alpha_paper", "beta_paper"],
            )
            self.assertTrue((project_dir / "_source" / "alpha_paper.pdf").exists())
            self.assertTrue((project_dir / "_source" / "beta_paper.pdf").exists())
            self.assertFalse((project_dir / "Alpha Paper.pdf").exists())
            self.assertFalse((project_dir / "Beta-Paper.pdf").exists())
            self.assertEqual(
                corpus_layout.paper_pdf_path("alpha_paper"),
                project_dir / "_source" / "alpha_paper.pdf",
            )
            self.assertEqual(
                corpus_layout.paper_pdf_path("alpha_paper", layout=layout),
                project_dir / "_source" / "alpha_paper.pdf",
            )
            self.assertEqual(
                corpus_layout.review_draft_path("alpha_paper"),
                project_dir / "_canon" / "alpha_paper.canonical.review.md",
            )
            self.assertEqual(
                corpus_layout.canonical_path("alpha_paper"),
                project_dir / "_data" / "alpha_paper.json",
            )
            self.assertEqual(
                corpus_layout.figures_dir("alpha_paper"),
                project_dir / "_figures" / "alpha_paper",
            )
            self.assertEqual(
                corpus_layout.review_draft_path("alpha_paper", layout=layout),
                project_dir / "_canon" / "alpha_paper.canonical.review.md",
            )
            self.assertEqual(
                layout.review_draft_path("alpha_paper"),
                project_dir / "_canon" / "alpha_paper.canonical.review.md",
            )

    def test_project_layout_rejects_legacy_source_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir).resolve()
            legacy_source = project_dir / "source"
            legacy_source.mkdir(parents=True, exist_ok=True)
            (legacy_source / "Alpha Paper.pdf").write_bytes(b"%PDF-1.4\nalpha\n")

            os.environ["PIPELINE_PROJECT_DIR"] = str(project_dir)
            importlib.reload(corpus_layout)

            with self.assertRaisesRegex(RuntimeError, "Legacy project input directory is no longer supported"):
                corpus_layout.prepare_project_inputs()


if __name__ == "__main__":
    unittest.main()
