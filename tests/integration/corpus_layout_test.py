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
from pipeline.corpus_layout import paper_uid


class CorpusLayoutTest(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("PIPELINE_CORPUS_DIR", None)
        os.environ.pop("PIPELINE_CORPUS_NAME", None)
        importlib.reload(corpus_layout)

    def test_corpus_layout_uses_configured_source_and_artifact_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "synthetic"
            source_dir = corpus_dir / "_source"
            source_dir.mkdir(parents=True, exist_ok=True)
            (source_dir / "alpha_paper.pdf").write_bytes(b"%PDF-1.4\nalpha\n")
            (source_dir / "beta_paper.pdf").write_bytes(b"%PDF-1.4\nbeta\n")

            os.environ["PIPELINE_CORPUS_DIR"] = str(corpus_dir)
            os.environ["PIPELINE_CORPUS_NAME"] = "synthetic"
            importlib.reload(corpus_layout)

            layout = corpus_layout.current_layout()

            self.assertEqual(corpus_layout.SOURCE_DIR, source_dir)
            self.assertEqual(corpus_layout.CORPUS_DIR, corpus_dir)
            self.assertEqual(layout.source_root, source_dir)
            self.assertEqual(layout.corpus_root, corpus_dir)
            self.assertEqual(
                layout.discover_source_pdfs(),
                [source_dir / "alpha_paper.pdf", source_dir / "beta_paper.pdf"],
            )
            self.assertEqual(
                corpus_layout.paper_pdf_path("alpha_paper"),
                source_dir / "alpha_paper.pdf",
            )
            self.assertEqual(
                corpus_layout.paper_pdf_path("alpha_paper", layout=layout),
                source_dir / "alpha_paper.pdf",
            )
            self.assertEqual(
                corpus_layout.review_draft_path("alpha_paper"),
                corpus_dir / "_canon" / "alpha_paper.canonical.review.md",
            )
            self.assertEqual(
                corpus_layout.canonical_path("alpha_paper"),
                corpus_dir / "_data" / f"canonical_{paper_uid('alpha_paper')}.json",
            )
            self.assertEqual(
                corpus_layout.figures_dir("alpha_paper"),
                corpus_dir / "_figures",
            )
            self.assertEqual(
                corpus_layout.review_draft_path("alpha_paper", layout=layout),
                corpus_dir / "_canon" / "alpha_paper.canonical.review.md",
            )
            self.assertEqual(
                layout.review_draft_path("alpha_paper"),
                corpus_dir / "_canon" / "alpha_paper.canonical.review.md",
            )

    def test_corpus_layout_rejects_root_level_pdf_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "synthetic"
            corpus_dir.mkdir(parents=True, exist_ok=True)
            (corpus_dir / "alpha_paper.pdf").write_bytes(b"%PDF-1.4\nalpha\n")

            os.environ["PIPELINE_CORPUS_DIR"] = str(corpus_dir)
            os.environ["PIPELINE_CORPUS_NAME"] = "synthetic"
            importlib.reload(corpus_layout)

            with self.assertRaises(RuntimeError):
                corpus_layout.current_layout().discover_source_pdfs()


if __name__ == "__main__":
    unittest.main()
