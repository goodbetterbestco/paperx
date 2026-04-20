import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import ProjectLayout
from pipeline.output.review_renderer import write_review_from_canonical
from pipeline.output.title_abstract_export import export_titles_and_abstracts


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        mode="corpus",
        corpus_name="synthetic",
        project_dir=None,
        corpus_root=corpus_root,
        source_root=corpus_root,
        review_root=corpus_root / "_canon",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


def _minimal_document(paper_id: str, pdf_path: Path) -> dict:
    return {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "title": "Synthetic Test Paper",
        "source": {"pdf_path": str(pdf_path), "page_count": 1, "page_sizes_pt": []},
        "build": {},
        "front_matter": {
            "title": "Synthetic Test Paper",
            "authors": [],
            "affiliations": [],
            "abstract_block_id": "blk-front-abstract-1",
            "funding_block_id": None,
        },
        "styles": {"document_style": {}, "category_styles": {}, "block_styles": {}},
        "sections": [],
        "blocks": [
            {
                "id": "blk-front-abstract-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "Synthetic abstract."}]},
                "source_spans": [],
                "alternates": [],
                "review": {"risk": "low", "status": "unreviewed", "notes": ""},
            }
        ],
        "math": [],
        "figures": [],
        "references": [],
    }


class OutputHelperTest(unittest.TestCase):
    def test_write_review_from_canonical_uses_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            canonical_target = layout.canonical_path(paper_id)
            canonical_target.parent.mkdir(parents=True, exist_ok=True)
            canonical_target.write_text(
                json.dumps(_minimal_document(paper_id, layout.paper_pdf_path(paper_id))),
                encoding="utf-8",
            )

            destination = write_review_from_canonical(paper_id, layout=layout)

            self.assertEqual(destination, layout.review_draft_path(paper_id))
            self.assertTrue(destination.exists())
            self.assertIn("Synthetic Test Paper", destination.read_text(encoding="utf-8"))

    def test_export_titles_and_abstracts_uses_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            paper_dir = layout.paper_dir(paper_id)
            paper_dir.mkdir(parents=True, exist_ok=True)
            layout.paper_pdf_path(paper_id).write_bytes(b"%PDF-1.4\nsynthetic\n")
            layout.canonical_path(paper_id).write_text(
                json.dumps(_minimal_document(paper_id, layout.paper_pdf_path(paper_id))),
                encoding="utf-8",
            )
            output_path = layout.tmp_root / "titles_and_abstracts.md"

            summary = export_titles_and_abstracts(output_path, layout=layout)

            self.assertEqual(summary["path"], str(output_path.resolve()))
            self.assertEqual(summary["papers"], 1)
            self.assertIn("Synthetic Test Paper", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
