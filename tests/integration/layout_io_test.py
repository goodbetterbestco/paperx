import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_paper import existing_composed_sources
from pipeline.output.artifacts import write_canonical_outputs
from pipeline.sources.external import (
    external_layout_path,
    external_math_path,
    load_external_layout,
    load_external_math,
    load_mathpix_layout,
    ocr_prepass_report_path,
)


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


class LayoutIoTest(unittest.TestCase):
    def test_external_source_helpers_resolve_against_explicit_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            sources_dir.mkdir(parents=True, exist_ok=True)

            external_layout_payload = {
                "engine": "mathpix",
                "pdf_path": str(layout.paper_pdf_path(paper_id)),
                "page_count": 1,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [{"id": "mx-1", "page": 1, "order": 1, "text": "Synthetic layout", "role": "paragraph", "bbox": {}}],
            }
            external_math_payload = {
                "engine": "mathpix",
                "entries": [{"id": "eq-1", "display_latex": "x+y", "source_spans": [{"page": 1, "bbox": {}}]}],
            }
            mathpix_layout_payload = {
                "engine": "mathpix_layout",
                "pdf_path": str(layout.paper_pdf_path(paper_id)),
                "page_count": 1,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [{"id": "mxl-1", "page": 1, "order": 1, "text": "Mathpix layout", "role": "paragraph", "bbox": {}}],
            }

            external_layout_path(paper_id, layout=layout).write_text(
                json.dumps(external_layout_payload),
                encoding="utf-8",
            )
            external_math_path(paper_id, layout=layout).write_text(
                json.dumps(external_math_payload),
                encoding="utf-8",
            )
            (sources_dir / "mathpix-layout.json").write_text(
                json.dumps(mathpix_layout_payload),
                encoding="utf-8",
            )

            loaded_layout = load_external_layout(paper_id, layout=layout)
            loaded_math = load_external_math(paper_id, layout=layout)
            loaded_mathpix_layout = load_mathpix_layout(paper_id, layout=layout)

            self.assertEqual(external_layout_path(paper_id, layout=layout), sources_dir / "layout.json")
            self.assertEqual(external_math_path(paper_id, layout=layout), sources_dir / "math.json")
            self.assertEqual(ocr_prepass_report_path(paper_id, layout=layout), sources_dir / "ocr-prepass.json")
            self.assertEqual(loaded_layout["engine"], "mathpix")
            self.assertEqual(loaded_layout["blocks"][0].id, "mx-1")
            self.assertEqual(loaded_layout["blocks"][0].engine, "mathpix")
            self.assertEqual(loaded_math["engine"], "mathpix")
            self.assertEqual(loaded_math["entries"][0]["external_engine"], "mathpix")
            self.assertEqual(loaded_mathpix_layout["engine"], "mathpix_layout")

    def test_existing_composed_sources_prefers_persisted_ocr_prepass_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            sources_dir.mkdir(parents=True, exist_ok=True)

            external_layout_path(paper_id, layout=layout).write_text(
                json.dumps(
                    {
                        "engine": "docling",
                        "pdf_path": str(layout.paper_pdf_path(paper_id)),
                        "page_count": 1,
                        "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                        "blocks": [{"id": "d-1", "page": 1, "order": 1, "text": "Synthetic", "role": "paragraph", "bbox": {}}],
                    }
                ),
                encoding="utf-8",
            )
            external_math_path(paper_id, layout=layout).write_text(
                json.dumps({"engine": "mathpix", "entries": [{"id": "eq-1", "display_latex": "x+y", "source_spans": [{"page": 1, "bbox": {}}]}]}),
                encoding="utf-8",
            )
            (sources_dir / "acquisition-route.json").write_text(
                json.dumps(
                    {
                        "paper_id": paper_id,
                        "primary_route": "scan_or_image_heavy",
                        "ocr_prepass": {"policy": "required", "should_run": True, "tool": "ocrmypdf"},
                    }
                ),
                encoding="utf-8",
            )
            (sources_dir / "source-scorecard.json").write_text(
                json.dumps(
                    {
                        "providers": [{"provider": "docling", "kind": "layout", "overall_score": 1.0}],
                        "recommended_primary_layout_provider": "docling",
                        "recommended_primary_math_provider": "mathpix",
                    }
                ),
                encoding="utf-8",
            )
            ocr_prepass_report_path(paper_id, layout=layout).write_text(
                json.dumps(
                    {
                        "selected_pdf_path": "corpus/synthetic/1990_synthetic_test_paper/canonical_sources/ocr-normalized.pdf",
                        "original_pdf_path": "corpus/synthetic/1990_synthetic_test_paper/paper.pdf",
                        "ocr_normalized_pdf_path": "corpus/synthetic/1990_synthetic_test_paper/canonical_sources/ocr-normalized.pdf",
                        "pdf_source_kind": "ocr_normalized_generated",
                        "ocr_prepass_policy": "required",
                        "ocr_prepass_tool": "ocrmypdf",
                        "ocr_prepass_applied": True,
                    }
                ),
                encoding="utf-8",
            )

            summary = existing_composed_sources(paper_id, layout=layout)

            self.assertEqual(summary["ocr_prepass_policy"], "required")
            self.assertTrue(summary["ocr_prepass_should_run"])
            self.assertEqual(summary["ocr_prepass_tool"], "ocrmypdf")
            self.assertTrue(summary["ocr_prepass_applied"])
            self.assertEqual(summary["pdf_source_kind"], "ocr_normalized_generated")
            self.assertTrue(str(summary["selected_pdf_path"]).endswith("ocr-normalized.pdf"))

    def test_write_canonical_outputs_uses_explicit_layout_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            document = {
                "schema_version": "1.0",
                "paper_id": paper_id,
                "title": "Synthetic Test Paper",
                "source": {"pdf_path": str(layout.paper_pdf_path(paper_id)), "page_count": 1, "page_sizes_pt": []},
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
                "_decision_artifacts": {
                    "acquisition_route": {"paper_id": paper_id, "primary_route": "born_digital_scholarly"},
                    "source_scorecard": {
                        "providers": [{"provider": "native_pdf", "overall_score": 0.8}],
                        "recommended_primary_layout_provider": "native_pdf",
                        "recommended_primary_math_provider": None
                    },
                    "title": {"selected_text": "Synthetic Test Paper", "source": "front_matter_records"},
                    "abstract": {"selected_text": "Synthetic abstract.", "source": "front_matter_records", "placeholder": False},
                },
            }

            with (
                patch("pipeline.output.artifacts.validate_canonical"),
                patch("pipeline.output.artifacts.render_document", return_value="# synthetic\n"),
            ):
                outputs = write_canonical_outputs(paper_id, document, include_review=True, layout=layout)

            canonical_target = layout.canonical_path(paper_id)
            review_target = layout.review_draft_path(paper_id)
            sources_target = layout.canonical_sources_dir(paper_id)

            self.assertEqual(outputs["canonical_path"], str(canonical_target))
            self.assertEqual(outputs["review_path"], str(review_target))
            self.assertTrue(canonical_target.exists())
            self.assertTrue(review_target.exists())
            self.assertTrue((sources_target / "acquisition-route.json").exists())
            self.assertTrue((sources_target / "source-scorecard.json").exists())
            self.assertTrue((sources_target / "title-decision.json").exists())
            self.assertTrue((sources_target / "abstract-decision.json").exists())
            self.assertEqual(
                json.loads((sources_target / "acquisition-route.json").read_text(encoding="utf-8"))["primary_route"],
                "born_digital_scholarly",
            )
            self.assertEqual(
                json.loads((sources_target / "source-scorecard.json").read_text(encoding="utf-8"))["recommended_primary_layout_provider"],
                "native_pdf",
            )
            self.assertEqual(
                json.loads((sources_target / "title-decision.json").read_text(encoding="utf-8"))["selected_text"],
                "Synthetic Test Paper",
            )


if __name__ == "__main__":
    unittest.main()
