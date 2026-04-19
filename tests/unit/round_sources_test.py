from __future__ import annotations

import json
import sys
import tempfile
import unittest
from concurrent.futures import Future
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_sources import (
    build_docling_sources,
    build_extraction_sources_for_paper,
    build_mathpix_sources,
    build_mathpix_sources_from_result,
    resolve_extraction_pdf,
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


class RoundSourcesTest(unittest.TestCase):
    def test_resolve_extraction_pdf_generates_ocr_normalized_pdf_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            original_pdf_path = layout.paper_pdf_path(paper_id)
            original_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            original_pdf_path.write_bytes(b"%PDF-1.4\noriginal\n")
            normalized_pdf_path = layout.canonical_sources_dir(paper_id) / "ocr-normalized.pdf"

            result = resolve_extraction_pdf(
                paper_id,
                layout=layout,
                build_acquisition_route_report_impl=lambda target_paper_id, *, layout=None: {
                    "paper_id": target_paper_id,
                    "primary_route": "scan_or_image_heavy",
                    "ocr_prepass": {"policy": "required", "should_run": True, "tool": "ocrmypdf"},
                },
                run_ocrmypdf_impl=lambda input_path, output_path: (output_path.write_bytes(b"%PDF-1.4\nocr\n"), output_path)[1],
            )

            self.assertEqual(result["selected_pdf_path"], normalized_pdf_path)
            self.assertEqual(result["pdf_source_kind"], "ocr_normalized_generated")
            self.assertTrue(result["ocr_prepass_applied"])
            self.assertTrue(normalized_pdf_path.exists())

    def test_resolve_extraction_pdf_falls_back_for_recommended_ocr_when_tool_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            paper_id = "1990_synthetic_test_paper"
            original_pdf_path = layout.paper_pdf_path(paper_id)
            original_pdf_path.parent.mkdir(parents=True, exist_ok=True)
            original_pdf_path.write_bytes(b"%PDF-1.4\noriginal\n")

            result = resolve_extraction_pdf(
                paper_id,
                layout=layout,
                build_acquisition_route_report_impl=lambda target_paper_id, *, layout=None: {
                    "paper_id": target_paper_id,
                    "primary_route": "degraded_or_garbled",
                    "ocr_prepass": {"policy": "recommended", "should_run": True, "tool": "ocrmypdf"},
                },
                run_ocrmypdf_impl=lambda input_path, output_path: (_ for _ in ()).throw(FileNotFoundError("missing ocrmypdf")),
            )

            self.assertEqual(result["selected_pdf_path"], original_pdf_path)
            self.assertEqual(result["pdf_source_kind"], "original_recommended_ocr_unavailable")
            self.assertFalse(result["ocr_prepass_applied"])

    def test_build_docling_sources_writes_sidecars_and_returns_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            docling_json_path = layout.tmp_root / "docling.json"
            docling_json_path.parent.mkdir(parents=True, exist_ok=True)
            docling_json_path.write_text(json.dumps({"texts": [{"text": "Synthetic"}]}), encoding="utf-8")

            result = build_docling_sources(
                paper_id,
                layout=layout,
                docling_device_impl=lambda: "cpu",
                run_docling_impl=lambda *args, **kwargs: docling_json_path,
                docling_json_to_external_sources_impl=lambda document, target_paper_id, *, layout=None: (
                    {"engine": "docling", "blocks": [{"id": "blk-1"}], "from": target_paper_id},
                    {"engine": "docling", "entries": [{"id": "eq-1"}]},
                ),
                external_layout_path_impl=lambda target_paper_id, *, layout=None: (
                    layout.canonical_sources_dir(target_paper_id) / "layout.json"
                ),
            )

            self.assertEqual(result["docling_json"], str(docling_json_path))
            self.assertEqual(result["layout"]["engine"], "docling")
            self.assertEqual(result["layout"]["from"], paper_id)
            self.assertEqual(result["math"]["entries"][0]["id"], "eq-1")
            self.assertTrue(Path(result["layout_path"]).exists())
            self.assertTrue(Path(result["math_path"]).exists())

    def test_build_mathpix_sources_from_result_writes_sidecars_and_preserves_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"

            result = build_mathpix_sources_from_result(
                paper_id,
                {"pdf_id": "pdf-123", "elapsed_seconds": 4.25, "pages": [{"page": 1}]},
                layout=layout,
                mathpix_pages_to_external_sources_impl=lambda payloads, target_paper_id, *, layout=None: (
                    {"engine": "mathpix", "blocks": [{"id": f"{target_paper_id}-blk"}]},
                    {"engine": "mathpix", "entries": [{"id": "math-1"}, {"id": "math-2"}]},
                ),
                external_layout_path_impl=lambda target_paper_id, *, layout=None: (
                    layout.canonical_sources_dir(target_paper_id) / "layout.json"
                ),
            )

            self.assertEqual(result["pdf_id"], "pdf-123")
            self.assertEqual(result["elapsed_seconds"], 4.25)
            self.assertEqual(result["math_entries"], 2)
            self.assertTrue(Path(result["layout_path"]).exists())
            self.assertTrue(Path(result["math_path"]).exists())

    def test_build_mathpix_sources_returns_none_without_credentials(self) -> None:
        result = build_mathpix_sources(
            "1990_synthetic_test_paper",
            mathpix_credentials_available_impl=lambda: False,
        )

        self.assertIsNone(result)

    def test_build_extraction_sources_uses_prefetched_mathpix_future(self) -> None:
        prefetched: Future[dict[str, object]] = Future()
        prefetched.set_result({"elapsed_seconds": 3.5, "pages": [{"page": 1}], "pdf_id": "prefetched-1"})
        selected_pdf_path = Path("/tmp/selected-prefetched.pdf")
        written_reports: dict[str, dict] = {}

        docling_sources, mathpix_sources, timings = build_extraction_sources_for_paper(
            "1990_synthetic_test_paper",
            prefetched_mathpix_future=prefetched,
            mathpix_credentials_available_impl=lambda: True,
            timed_call_impl=lambda label, fn, /, *args, **kwargs: (label, 1.25, fn(*args, **kwargs)),
            resolve_extraction_pdf_impl=lambda paper_id, *, layout=None: {
                "selected_pdf_path": selected_pdf_path,
                "original_pdf_path": Path("/tmp/original-prefetched.pdf"),
                "ocr_normalized_pdf_path": selected_pdf_path,
                "pdf_source_kind": "ocr_normalized_existing",
                "ocr_prepass_policy": "required",
                "ocr_prepass_tool": "ocrmypdf",
                "ocr_prepass_applied": True,
            },
            write_json_impl=lambda path, payload: written_reports.__setitem__(path.name, payload),
            build_docling_sources_impl=lambda paper_id, *, pdf_path=None, layout=None: {
                "layout": {"blocks": []},
                "math": {"entries": []},
                "source_pdf_path": str(pdf_path),
            },
            build_mathpix_sources_from_result_impl=lambda paper_id, result, *, pdf_path=None, layout=None: {
                "pdf_id": result["pdf_id"],
                "math_entries": len(result["pages"]),
                "source_pdf_path": str(pdf_path),
            },
        )

        self.assertEqual(docling_sources["layout"]["blocks"], [])
        self.assertEqual(mathpix_sources["pdf_id"], "prefetched-1")
        self.assertEqual(mathpix_sources["math_entries"], 1)
        self.assertEqual(docling_sources["source_pdf_path"], str(selected_pdf_path))
        self.assertEqual(mathpix_sources["source_pdf_path"], str(selected_pdf_path))
        self.assertEqual(written_reports["ocr-prepass.json"]["pdf_source_kind"], "ocr_normalized_existing")
        self.assertTrue(written_reports["ocr-prepass.json"]["ocr_prepass_applied"])
        self.assertEqual(timings["docling_seconds"], 1.25)
        self.assertEqual(timings["mathpix_seconds"], 3.5)
        self.assertIn("ocr_prepass_seconds", timings)

    def test_build_extraction_sources_runs_local_mathpix_when_enabled(self) -> None:
        selected_pdf_path = Path("/tmp/selected-local.pdf")
        written_reports: dict[str, dict] = {}
        docling_sources, mathpix_sources, timings = build_extraction_sources_for_paper(
            "1990_synthetic_test_paper",
            mathpix_credentials_available_impl=lambda: True,
            timed_call_impl=lambda label, fn, /, *args, **kwargs: (
                label,
                0.75 if label == "docling" else 2.5,
                fn(*args, **kwargs),
            ),
            resolve_extraction_pdf_impl=lambda paper_id, *, layout=None: {
                "selected_pdf_path": selected_pdf_path,
                "original_pdf_path": selected_pdf_path,
                "ocr_normalized_pdf_path": Path("/tmp/missing-local.pdf"),
                "pdf_source_kind": "original",
                "ocr_prepass_policy": "skip",
                "ocr_prepass_tool": None,
                "ocr_prepass_applied": False,
            },
            write_json_impl=lambda path, payload: written_reports.__setitem__(path.name, payload),
            build_docling_sources_impl=lambda paper_id, *, pdf_path=None, layout=None: {
                "layout": {"blocks": [{"id": "docling"}]},
                "math": {"entries": []},
                "source_pdf_path": str(pdf_path),
            },
            build_mathpix_sources_impl=lambda paper_id, *, pdf_path=None, layout=None: {
                "math_entries": 4,
                "layout": {"blocks": []},
                "math": {"entries": []},
                "source_pdf_path": str(pdf_path),
            },
        )

        self.assertEqual(docling_sources["layout"]["blocks"][0]["id"], "docling")
        self.assertEqual(mathpix_sources["math_entries"], 4)
        self.assertEqual(docling_sources["source_pdf_path"], str(selected_pdf_path))
        self.assertEqual(mathpix_sources["source_pdf_path"], str(selected_pdf_path))
        self.assertEqual(written_reports["ocr-prepass.json"]["pdf_source_kind"], "original")
        self.assertFalse(written_reports["ocr-prepass.json"]["ocr_prepass_applied"])
        self.assertEqual(timings["docling_seconds"], 0.75)
        self.assertEqual(timings["mathpix_seconds"], 2.5)
        self.assertIn("ocr_prepass_seconds", timings)


if __name__ == "__main__":
    unittest.main()
