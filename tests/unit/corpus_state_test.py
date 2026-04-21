from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus.state import reset_corpus_to_source_state


MINIMAL_PDF = b"%PDF-1.4\nsynthetic\n"


class CorpusStateTest(unittest.TestCase):
    def test_reset_corpus_to_source_state_moves_pdfs_into_source_dir_and_removes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "stepview"
            paper_dir = corpus_dir / "1990_synthetic_test_paper"
            paper_dir.mkdir(parents=True, exist_ok=True)
            (paper_dir / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)
            (paper_dir / "canonical.json").write_text('{"title": "Synthetic"}\n', encoding="utf-8")
            (paper_dir / "canonical_sources").mkdir(parents=True, exist_ok=True)
            (paper_dir / "canonical_sources" / "layout.json").write_text("{}", encoding="utf-8")
            (corpus_dir / "_canon").mkdir(parents=True, exist_ok=True)
            (corpus_dir / "_canon" / "1990_synthetic_test_paper.canonical.review.md").write_text(
                "# Synthetic\n",
                encoding="utf-8",
            )
            (corpus_dir / "_runs").mkdir(parents=True, exist_ok=True)
            (corpus_dir / "_runs" / "status.json").write_text("{}", encoding="utf-8")
            (corpus_dir / "corpus_lexicon.json").write_text("{}", encoding="utf-8")
            (corpus_dir / "figure_expectations.json").write_text("{}", encoding="utf-8")

            result = reset_corpus_to_source_state(corpus_dir)

            self.assertEqual(result["state"], "source")
            self.assertTrue((corpus_dir / "_source" / "1990_synthetic_test_paper.pdf").exists())
            self.assertFalse(paper_dir.exists())
            self.assertFalse((corpus_dir / "_canon").exists())
            self.assertFalse((corpus_dir / "_runs").exists())
            self.assertFalse((corpus_dir / "corpus_lexicon.json").exists())
            self.assertFalse((corpus_dir / "figure_expectations.json").exists())

    def test_reset_corpus_to_source_state_rejects_legacy_layout_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "stepview"
            legacy_source = corpus_dir / "source"
            legacy_source.mkdir(parents=True, exist_ok=True)
            (legacy_source / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)

            with self.assertRaises(RuntimeError):
                reset_corpus_to_source_state(corpus_dir)


if __name__ == "__main__":
    unittest.main()
