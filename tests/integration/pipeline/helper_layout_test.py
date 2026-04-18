import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.modules.setdefault("fitz", types.SimpleNamespace(Document=object, Matrix=object, Page=object, Rect=object))

from pipeline.corpus.lexicon import corpus_join_terms, load_corpus_lexicon
from pipeline.corpus.lexicon_builder import _build_lexicon
from pipeline.corpus_layout import ProjectLayout, display_path
from pipeline.corpus.metadata import load_figure_expectations, paper_figure_metadata
from pipeline.figures.linking import build_manifest_from_pdf_path


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        mode="corpus",
        corpus_name="synthetic",
        project_dir=None,
        corpus_root=corpus_root,
        source_root=corpus_root,
        review_root=corpus_root / "review_drafts",
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
            "authors": [{"name": "Ada Example"}],
            "affiliations": [],
            "abstract_block_id": "blk-front-abstract-1",
            "funding_block_id": None,
        },
        "styles": {"document_style": {}, "category_styles": {}, "block_styles": {}},
        "sections": [{"id": "sec-1", "title": "Results"}],
        "blocks": [
            {
                "id": "blk-front-abstract-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "Synthetic abstract about trimmed surfaces."}]},
                "source_spans": [],
                "alternates": [],
                "review": {"risk": "low", "status": "unreviewed", "notes": ""},
            }
        ],
        "math": [],
        "figures": [{"id": "fig-1", "caption": "Synthetic figure caption"}],
        "references": [{"id": "ref-1", "text": "Trimmed surfaces in CAD."}],
    }


class HelperLayoutTest(unittest.TestCase):
    def test_figure_expectations_use_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            layout.figure_expectations_path.parent.mkdir(parents=True, exist_ok=True)
            layout.figure_expectations_path.write_text(
                json.dumps(
                    {
                        "entries": {
                            "1990_synthetic_test_paper": {
                                "expected_semantic_figure_count": 3,
                                "notes": "synthetic note",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            expectations = load_figure_expectations(layout=layout)
            metadata = paper_figure_metadata("1990_synthetic_test_paper", layout=layout)

            self.assertEqual(expectations["1990_synthetic_test_paper"]["expected_semantic_figure_count"], 3)
            self.assertEqual(metadata["notes"], "synthetic note")

    def test_lexicon_helpers_use_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            layout.corpus_lexicon_path.parent.mkdir(parents=True, exist_ok=True)
            layout.corpus_lexicon_path.write_text(
                json.dumps(
                    {
                        "terms": [{"canonical": "trimmedsurface", "count": 4, "variants": []}],
                        "authors": [{"canonical": "Ada Example", "count": 1}],
                        "acronyms": ["CAD"],
                    }
                ),
                encoding="utf-8",
            )

            lexicon = load_corpus_lexicon(layout=layout)
            join_terms = corpus_join_terms(layout=layout)

            self.assertEqual(lexicon["terms"][0]["canonical"], "trimmedsurface")
            self.assertIn("trimmedsurface", join_terms)
            self.assertIn("cad", join_terms)

    def test_build_lexicon_uses_explicit_layout_canonicals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            paper_dir = layout.paper_dir(paper_id)
            paper_dir.mkdir(parents=True, exist_ok=True)
            canonical_path = layout.canonical_path(paper_id)
            canonical_path.write_text(
                json.dumps(_minimal_document(paper_id, layout.paper_pdf_path(paper_id))),
                encoding="utf-8",
            )

            lexicon = _build_lexicon(layout=layout)

            self.assertEqual(lexicon["sources"]["canonical_papers"], 1)
            self.assertTrue(any(entry["canonical"] == "Ada Example" for entry in lexicon["authors"]))
            self.assertGreaterEqual(len(lexicon["terms"]), 1)

    def test_build_manifest_from_pdf_path_uses_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            paper_dir = layout.paper_dir(paper_id)
            paper_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = layout.paper_pdf_path(paper_id)
            pdf_path.write_bytes(b"%PDF-1.4\nsynthetic\n")
            layout.figure_expectations_path.parent.mkdir(parents=True, exist_ok=True)
            layout.figure_expectations_path.write_text(
                json.dumps({"entries": {paper_id: {"expected_semantic_figure_count": 2}}}),
                encoding="utf-8",
            )

            manifest = build_manifest_from_pdf_path(pdf_path, layout=layout)

            self.assertEqual(manifest["id"], paper_id)
            self.assertEqual(manifest["source_pdf"], display_path(pdf_path, layout=layout))
            self.assertEqual(
                manifest["artifacts"]["figures_dir"],
                display_path(layout.figures_dir(paper_id), layout=layout),
            )
            self.assertEqual(manifest["figure_expectations"]["expected_semantic_figure_count"], 2)


if __name__ == "__main__":
    unittest.main()
