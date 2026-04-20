import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.corpus.metadata as corpus_metadata
import pipeline.corpus_layout as corpus_layout


class CorpusMetadataTest(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("PIPELINE_CORPUS_DIR", None)
        os.environ.pop("PAPER_PIPELINE_CORPUS_DIR", None)
        importlib.reload(corpus_layout)
        importlib.reload(corpus_metadata)
    def test_corpus_discovers_unprefixed_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "stepview"
            corpus_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = corpus_dir / "1967_quantitative_invisibility.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nsynthetic\n")

            os.environ["PIPELINE_CORPUS_DIR"] = str(corpus_dir)
            importlib.reload(corpus_layout)
            importlib.reload(corpus_metadata)

            discovered = corpus_metadata.discover_paper_pdf_paths()

            self.assertEqual(discovered, [pdf_path])
            self.assertEqual(
                corpus_metadata.paper_id_from_pdf_path(pdf_path),
                "1967_quantitative_invisibility",
            )
            self.assertEqual(
                corpus_layout.paper_pdf_path("1967_quantitative_invisibility"),
                pdf_path,
            )


if __name__ == "__main__":
    unittest.main()
