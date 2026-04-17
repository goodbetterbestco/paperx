import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.build_canonical as build_canonical
import pipeline.build_external_layout_from_pdftotext as build_external_layout_from_pdftotext
import pipeline.build_external_sources_from_docling as build_external_sources_from_docling
import pipeline.build_external_sources_from_mathpix as build_external_sources_from_mathpix
import pipeline.build_review as build_review
import pipeline.compose_external_sources as compose_external_sources
import pipeline.export_titles_and_abstracts as export_titles_and_abstracts
import pipeline.render_review_from_canonical as render_review_from_canonical
from pipeline.corpus_layout import ProjectLayout


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


class ScriptLayoutTest(unittest.TestCase):
    def test_render_review_main_uses_explicit_layout_paths(self) -> None:
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

            with (
                patch.object(render_review_from_canonical, "parse_args", return_value=Namespace(paper_id=paper_id)),
                patch.object(render_review_from_canonical, "current_layout", return_value=layout),
                patch("builtins.print"),
            ):
                result = render_review_from_canonical.main()

            self.assertEqual(result, 0)
            review_target = layout.review_draft_path(paper_id)
            self.assertTrue(review_target.exists())
            self.assertIn("Synthetic Test Paper", review_target.read_text(encoding="utf-8"))

    def test_build_export_text_uses_explicit_layout(self) -> None:
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

            exported = export_titles_and_abstracts.build_export_text(layout=layout)

            self.assertIn("Synthetic Test Paper", exported)
            self.assertIn("Synthetic abstract.", exported)

    def test_build_canonical_main_threads_layout_to_config_and_writer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            captured: dict[str, object] = {}
            document = _minimal_document(paper_id, layout.paper_pdf_path(paper_id))

            class FakeBuild:
                def __init__(self) -> None:
                    self.layout = layout
                    self.document = document

            def fake_write_outputs(_paper_id: str, _document: dict, *, include_review: bool, layout=None) -> dict:
                captured["write_layout"] = layout
                return {"canonical_path": str(layout.canonical_path(paper_id))}

            with (
                patch.object(
                    build_canonical,
                    "parse_args",
                    return_value=Namespace(
                        paper_id=paper_id,
                        text_engine="native",
                        use_external_layout=False,
                        use_external_math=False,
                        dry_run=False,
                        validate=False,
                    ),
                ),
                patch.object(build_canonical, "current_layout", return_value=layout),
                patch.object(build_canonical, "build_paper", return_value=FakeBuild()) as build_paper,
                patch.object(build_canonical, "validate_canonical"),
                patch.object(build_canonical, "write_canonical_outputs", side_effect=fake_write_outputs),
                patch("builtins.print"),
            ):
                result = build_canonical.main()

            self.assertEqual(result, 0)
            self.assertIs(build_paper.call_args.kwargs["layout"], layout)
            self.assertIs(captured["write_layout"], layout)

    def test_build_review_main_threads_layout_to_config_and_writer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            captured: dict[str, object] = {}
            document = _minimal_document(paper_id, layout.paper_pdf_path(paper_id))

            class FakeBuild:
                def __init__(self) -> None:
                    self.layout = layout
                    self.document = document

            def fake_write_outputs(_paper_id: str, _document: dict, *, include_review: bool, layout=None) -> dict:
                captured["write_layout"] = layout
                return {
                    "canonical_path": str(layout.canonical_path(paper_id)),
                    "review_path": str(layout.review_draft_path(paper_id)),
                }

            with (
                patch.object(
                    build_review,
                    "parse_args",
                    return_value=Namespace(
                        paper_id=paper_id,
                        text_engine="native",
                        use_external_layout=False,
                        use_external_math=False,
                        dry_run=False,
                    ),
                ),
                patch.object(build_review, "current_layout", return_value=layout),
                patch.object(build_review, "build_paper", return_value=FakeBuild()) as build_paper,
                patch.object(build_review, "validate_canonical"),
                patch.object(build_review, "write_canonical_outputs", side_effect=fake_write_outputs),
                patch("builtins.print"),
            ):
                result = build_review.main()

            self.assertEqual(result, 0)
            self.assertIs(build_paper.call_args.kwargs["layout"], layout)
            self.assertIs(captured["write_layout"], layout)

    def test_build_external_layout_from_pdftotext_main_uses_helper_with_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"

            class FakeBuild:
                summary = {"changed_blocks": 1, "skipped_blocks": 0, "total_blocks": 1}

                def write(self) -> dict[str, str]:
                    return {"layout_path": str(layout.canonical_sources_dir(paper_id) / "layout.json")}

            with (
                patch.object(
                    build_external_layout_from_pdftotext,
                    "parse_args",
                    return_value=Namespace(paper_id=paper_id, dry_run=False),
                ),
                patch.object(build_external_layout_from_pdftotext, "current_layout", return_value=layout),
                patch.object(build_external_layout_from_pdftotext, "build_pdftotext_external_layout", return_value=FakeBuild()) as helper,
                patch("builtins.print"),
            ):
                result = build_external_layout_from_pdftotext.main()

            self.assertEqual(result, 0)
            self.assertIs(helper.call_args.kwargs["layout"], layout)

    def test_build_external_sources_from_docling_main_uses_helper_with_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"

            class FakeBuild:
                summary = {"docling_json": "synthetic.json", "layout_engine": "docling", "layout_blocks": 0, "math_engine": "docling", "math_entries": 0}

                def write(self) -> dict[str, str]:
                    return {
                        "layout_path": str(layout.canonical_sources_dir(paper_id) / "layout.json"),
                        "math_path": str(layout.canonical_sources_dir(paper_id) / "math.json"),
                    }

            with (
                patch.object(
                    build_external_sources_from_docling,
                    "parse_args",
                    return_value=Namespace(paper_id=paper_id, docling_json=None, device="cpu", dry_run=False),
                ),
                patch.object(build_external_sources_from_docling, "current_layout", return_value=layout),
                patch.object(build_external_sources_from_docling, "build_docling_external_sources", return_value=FakeBuild()) as helper,
                patch("builtins.print"),
            ):
                result = build_external_sources_from_docling.main()

            self.assertEqual(result, 0)
            self.assertIs(helper.call_args.kwargs["layout"], layout)

    def test_build_external_sources_from_mathpix_main_uses_helper_with_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"

            class FakeBuild:
                summary = {"source": "mathpix_api", "layout_engine": "mathpix", "layout_blocks": 0, "math_engine": "mathpix", "math_entries": 0}

                def write(self) -> dict[str, str]:
                    return {
                        "layout_path": str(layout.canonical_sources_dir(paper_id) / "layout.json"),
                        "math_path": str(layout.canonical_sources_dir(paper_id) / "math.json"),
                    }

            with (
                patch.object(
                    build_external_sources_from_mathpix,
                    "parse_args",
                    return_value=Namespace(
                        paper_id=paper_id,
                        pages=None,
                        endpoint="https://api.mathpix.com/v3/pdf",
                        app_id=None,
                        app_key=None,
                        mathpix_json=None,
                        dry_run=False,
                    ),
                ),
                patch.object(build_external_sources_from_mathpix, "current_layout", return_value=layout),
                patch.object(build_external_sources_from_mathpix, "build_mathpix_external_sources", return_value=FakeBuild()) as helper,
                patch("builtins.print"),
            ):
                result = build_external_sources_from_mathpix.main()

            self.assertEqual(result, 0)
            self.assertIs(helper.call_args.kwargs["layout"], layout)

    def test_compose_external_sources_main_uses_helper_with_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"

            class FakeBuild:
                summary = {"layout_engine": "docling", "layout_blocks": 0, "math_engine": "mathpix", "math_entries": 0}

                def write(self) -> dict[str, str]:
                    return {
                        "layout_path": str(layout.canonical_sources_dir(paper_id) / "layout.json"),
                        "math_path": str(layout.canonical_sources_dir(paper_id) / "math.json"),
                    }

            with (
                patch.object(
                    compose_external_sources,
                    "parse_args",
                    return_value=Namespace(
                        paper_id=paper_id,
                        layout_json="layout.json",
                        math_json="math.json",
                        dry_run=False,
                    ),
                ),
                patch.object(compose_external_sources, "current_layout", return_value=layout),
                patch.object(compose_external_sources, "build_composed_external_sources", return_value=FakeBuild()) as helper,
                patch("builtins.print"),
            ):
                result = compose_external_sources.main()

            self.assertEqual(result, 0)
            self.assertIs(helper.call_args.kwargs["layout"], layout)


if __name__ == "__main__":
    unittest.main()
