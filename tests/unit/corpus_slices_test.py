from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus.slices import load_source_slice_manifest, materialize_source_slice


MINIMAL_PDF = b"%PDF-1.4\nsynthetic\n"


class CorpusSlicesTest(unittest.TestCase):
    def test_load_source_slice_manifest_normalizes_and_dedupes_paper_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "slice.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "label": "validation",
                        "papers": [
                            "1990_Synthetic_Test_Paper",
                            "1990_synthetic_test_paper.pdf",
                            "2001 Another Paper",
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            payload = load_source_slice_manifest(manifest_path)

            self.assertEqual(payload["label"], "validation")
            self.assertEqual(
                payload["paper_ids"],
                ["1990_synthetic_test_paper", "2001_another_paper"],
            )

    def test_materialize_source_slice_copies_requested_root_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            source_corpus = root / "corpus" / "stepview"
            target_project = root / "tmp" / "validation_slice"
            source_corpus.mkdir(parents=True, exist_ok=True)
            (source_corpus / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)
            (source_corpus / "2001_another_test_paper.pdf").write_bytes(MINIMAL_PDF)

            payload = materialize_source_slice(
                source_corpus,
                target_project,
                paper_ids=["2001_another_test_paper", "1990_synthetic_test_paper"],
            )

            self.assertEqual(payload["state"], "source")
            self.assertEqual(
                payload["paper_ids"],
                ["2001_another_test_paper", "1990_synthetic_test_paper"],
            )
            self.assertTrue((target_project / "1990_synthetic_test_paper.pdf").exists())
            self.assertTrue((target_project / "2001_another_test_paper.pdf").exists())

    def test_materialize_source_slice_requires_source_state_root_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            source_corpus = root / "corpus" / "stepview"
            processed_paper_dir = source_corpus / "1990_synthetic_test_paper"
            processed_paper_dir.mkdir(parents=True, exist_ok=True)
            (processed_paper_dir / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)

            with self.assertRaises(FileNotFoundError) as ctx:
                materialize_source_slice(
                    source_corpus,
                    root / "tmp" / "validation_slice",
                    paper_ids=["1990_synthetic_test_paper"],
                )

            self.assertIn("processed state", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
