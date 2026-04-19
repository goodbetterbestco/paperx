from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus_layout import ProjectLayout
from pipeline.sources.layout import extract_layout


PAPER_ID = "smoke_layout_test"
SMOKE_ENV = "PAPERX_RUN_SMOKE"


def _project_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus"
    return ProjectLayout(
        engine_root=root,
        mode="project",
        corpus_name="fixture",
        project_dir=root,
        corpus_root=corpus_root,
        source_root=root / "source",
        review_root=root,
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


@unittest.skipUnless(os.environ.get(SMOKE_ENV) == "1", f"set {SMOKE_ENV}=1 to run smoke tests")
class LayoutExtractionSmokeTest(unittest.TestCase):
    def test_extract_layout_reads_real_pdf_with_pymupdf(self) -> None:
        try:
            import fitz  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover
            self.fail(f"Smoke test requested via {SMOKE_ENV}=1, but PyMuPDF is not installed: {exc}")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _project_layout(root)
            layout.source_root.mkdir(parents=True, exist_ok=True)
            layout.paper_dir(PAPER_ID).mkdir(parents=True, exist_ok=True)
            pdf_path = layout.paper_pdf_path(PAPER_ID)

            doc = fitz.open()
            page = doc.new_page(width=300, height=200)
            page.insert_text((36, 72), "Synthetic smoke layout text")
            doc.save(pdf_path)
            doc.close()

            extracted = extract_layout(PAPER_ID, layout=layout)

            self.assertEqual(extracted["page_count"], 1)
            self.assertTrue(extracted["blocks"])
            block_texts = [str(block.text) if hasattr(block, "text") else str(block.get("text", "")) for block in extracted["blocks"]]
            self.assertTrue(any("Synthetic smoke layout text" in text for text in block_texts))


if __name__ == "__main__":
    unittest.main()
