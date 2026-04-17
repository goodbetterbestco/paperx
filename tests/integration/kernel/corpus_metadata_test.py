import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import paper_pipeline.corpus_layout as corpus_layout
import paper_pipeline.corpus_metadata as corpus_metadata
import paper_pipeline.text_utils as text_utils


class CorpusMetadataTest(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("PAPER_PIPELINE_CORPUS_DIR", None)
        importlib.reload(corpus_layout)
        importlib.reload(corpus_metadata)
        importlib.reload(text_utils)

    def test_corpus_discovers_unprefixed_ids_and_keeps_legacy_metadata_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir).resolve() / "stepview"
            paper_dir = corpus_dir / "1967_quantitative_invisibility"
            paper_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = paper_dir / "1967_quantitative_invisibility.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nsynthetic\n")
            (corpus_dir / "bibliography.json").write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "id": "kernel_1967_quantitative_invisibility",
                                "title": "Quantitative Invisibility",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            os.environ["PAPER_PIPELINE_CORPUS_DIR"] = str(corpus_dir)
            importlib.reload(corpus_layout)
            importlib.reload(corpus_metadata)
            importlib.reload(text_utils)

            discovered = corpus_metadata.discover_paper_pdf_paths()

            self.assertEqual(discovered, [pdf_path])
            self.assertEqual(
                corpus_metadata.paper_id_from_pdf_path(pdf_path),
                "1967_quantitative_invisibility",
            )
            self.assertEqual(
                corpus_layout.paper_pdf_path("kernel_1967_quantitative_invisibility"),
                pdf_path,
            )
            self.assertEqual(
                text_utils.paper_metadata("1967_quantitative_invisibility"),
                {
                    "id": "kernel_1967_quantitative_invisibility",
                    "title": "Quantitative Invisibility",
                },
            )


if __name__ == "__main__":
    unittest.main()
