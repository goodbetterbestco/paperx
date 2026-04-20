import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.pipeline_deps import PaperSourceResolutionDeps
from pipeline.orchestrator.resolve_sources import resolve_paper_sources
from pipeline.state import PaperState


def _source_resolution_deps(**overrides: object) -> PaperSourceResolutionDeps:
    values: dict[str, object] = {
        "extract_layout": lambda paper_id: {"engine": "native_pdf"},
        "load_external_layout": lambda paper_id: None,
        "merge_native_and_external_layout": lambda native_layout, external_layout: native_layout,
        "load_external_math": lambda paper_id: None,
        "load_mathpix_layout": lambda paper_id: None,
        "extract_figures": lambda paper_id: [],
        "normalize_figure_caption_text": lambda text: text,
    }
    values.update(overrides)
    return PaperSourceResolutionDeps(**values)


class SourceResolutionTest(unittest.TestCase):
    def test_resolve_paper_sources_reports_primary_provider_for_generic_engines(self) -> None:
        engine_root = Path("/tmp/paperx-source-resolution").resolve()
        corpus_root = engine_root / "corpus" / "synthetic"
        layout = ProjectLayout(
            engine_root=engine_root,
            mode="corpus",
            corpus_name="synthetic",
            project_dir=None,
            corpus_root=corpus_root,
            source_root=corpus_root,
            review_root=corpus_root / "_canon",
            runs_root=corpus_root / "_runs",
            tmp_root=engine_root / "tmp",
            figure_expectations_path=corpus_root / "figure_expectations.json",
        )
        config = build_pipeline_config(
            layout=layout,
            text_engine="native",
            use_external_layout=True,
            use_external_math=True,
            include_review=False,
        )
        state = PaperState.begin(
            "1990_synthetic_test_paper",
            config=config,
            started_at="2026-04-17T00:00:00Z",
        )

        native_layout = {
            "engine": "native_pdf",
            "pdf_path": str(state.pdf_path),
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [{"id": "native-1", "page": 1, "order": 1, "text": "Native text", "role": "paragraph", "bbox": {}}],
        }
        external_layout = {
            "engine": "composed",
            "pdf_path": str(state.pdf_path),
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [{"id": "external-1", "page": 1, "order": 1, "text": "External text", "role": "paragraph", "bbox": {}}],
        }
        external_math = {
            "engine": "mathpix",
            "entries": [{"id": "ext-math-1"}],
        }
        mathpix_layout = {"engine": "mathpix_layout", "blocks": []}

        resolved = resolve_paper_sources(
            state,
            config=config,
            layout_output=native_layout,
            figures=[{"id": "fig-1", "page": 1, "caption": "caption text"}],
            deps=_source_resolution_deps(
                extract_layout=lambda paper_id: native_layout,
                load_external_layout=lambda paper_id: external_layout,
                merge_native_and_external_layout=lambda native, external: {
                    **external,
                    "engine": "merged_layout",
                    "pdf_path": native["pdf_path"],
                    "page_count": native["page_count"],
                    "page_sizes_pt": native["page_sizes_pt"],
                },
                load_external_math=lambda paper_id: external_math,
                load_mathpix_layout=lambda paper_id: mathpix_layout,
                extract_figures=lambda paper_id: [],
                normalize_figure_caption_text=lambda text: text.upper(),
            ),
            build_acquisition_route_report_impl=lambda paper_id, *, layout=None: {
                "paper_id": paper_id,
                "primary_route": "math_dense",
            },
            build_source_scorecard_impl=lambda **kwargs: {
                "providers": [{"provider": "mathpix", "overall_score": 1.2}],
                "recommended_primary_layout_provider": "mathpix",
                "recommended_primary_math_provider": "mathpix",
                "recommended_primary_metadata_provider": "docling",
                "recommended_primary_reference_provider": "grobid",
            },
            load_docling_metadata_observation_impl=lambda paper_id, *, layout=None: {
                "provider": "docling",
                "title": "Docling Title",
                "abstract": "Docling abstract.",
                "references": ["D. Ref"],
            },
            load_grobid_metadata_observation_impl=lambda paper_id, *, layout=None: {
                "provider": "grobid",
                "title": "Synthetic Title",
                "abstract": "Synthetic abstract.",
                "references": ["A. Ref"],
            },
            load_mathpix_metadata_observation_impl=lambda paper_id, *, layout=None: {
                "provider": "mathpix",
                "title": "Mathpix Title",
                "abstract": "",
                "references": [],
            },
        )

        self.assertEqual(resolved.native_layout, native_layout)
        self.assertEqual(resolved.external_layout, external_layout)
        self.assertEqual(resolved.merged_layout["engine"], "merged_layout")
        self.assertEqual(resolved.mathpix_layout, mathpix_layout)
        self.assertEqual(resolved.external_math, external_math)
        self.assertEqual(resolved.metadata_candidates["docling"]["provider"], "docling")
        self.assertEqual(resolved.metadata_candidates["grobid"]["provider"], "grobid")
        self.assertEqual(resolved.metadata_candidates["mathpix"]["provider"], "mathpix")
        self.assertEqual(resolved.figures[0]["caption"], "CAPTION TEXT")
        self.assertEqual(resolved.acquisition_route, {"paper_id": "1990_synthetic_test_paper", "primary_route": "math_dense"})
        self.assertEqual(resolved.source_scorecard["recommended_primary_layout_provider"], "mathpix")
        self.assertEqual(resolved.layout_engine_name, "mathpix")
        self.assertEqual(resolved.math_engine_name, "mathpix")
        self.assertEqual(resolved.metadata_observation["provider"], "docling")
        self.assertEqual(resolved.reference_observation["provider"], "grobid")
        self.assertIn("pdf", resolved.input_fingerprints)

    def test_resolve_paper_sources_preserves_concrete_external_layout_engine(self) -> None:
        engine_root = Path("/tmp/paperx-source-resolution").resolve()
        corpus_root = engine_root / "corpus" / "synthetic"
        layout = ProjectLayout(
            engine_root=engine_root,
            mode="corpus",
            corpus_name="synthetic",
            project_dir=None,
            corpus_root=corpus_root,
            source_root=corpus_root,
            review_root=corpus_root / "_canon",
            runs_root=corpus_root / "_runs",
            tmp_root=engine_root / "tmp",
            figure_expectations_path=corpus_root / "figure_expectations.json",
        )
        config = build_pipeline_config(
            layout=layout,
            text_engine="native",
            use_external_layout=True,
            use_external_math=True,
            include_review=False,
        )
        state = PaperState.begin(
            "1990_synthetic_test_paper",
            config=config,
            started_at="2026-04-17T00:00:00Z",
        )

        native_layout = {
            "engine": "native_pdf",
            "pdf_path": str(state.pdf_path),
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [{"id": "native-1", "page": 1, "order": 1, "text": "Native text", "role": "paragraph", "bbox": {}}],
        }
        external_layout = {
            "engine": "docling",
            "pdf_path": str(state.pdf_path),
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [{"id": "external-1", "page": 1, "order": 1, "text": "External text", "role": "paragraph", "bbox": {}}],
        }
        external_math = {
            "engine": "mathpix",
            "entries": [],
        }

        resolved = resolve_paper_sources(
            state,
            config=config,
            layout_output=native_layout,
            figures=[],
            deps=_source_resolution_deps(
                extract_layout=lambda paper_id: native_layout,
                load_external_layout=lambda paper_id: external_layout,
                merge_native_and_external_layout=lambda native, external: external,
                load_external_math=lambda paper_id: external_math,
            ),
            build_acquisition_route_report_impl=lambda paper_id, *, layout=None: {
                "paper_id": paper_id,
                "primary_route": "born_digital_scholarly",
            },
            build_source_scorecard_impl=lambda **kwargs: {
                "providers": [
                    {"provider": "mathpix_layout", "kind": "layout", "overall_score": 1.4},
                    {"provider": "docling", "kind": "layout", "overall_score": 1.2},
                ],
                "recommended_primary_layout_provider": "mathpix_layout",
                "recommended_primary_math_provider": None,
            },
        )

        self.assertEqual(resolved.layout_engine_name, "docling")
        self.assertEqual(resolved.math_engine_name, "heuristic")

    def test_resolve_paper_sources_escalates_metadata_and_references_to_grobid_when_fallback_is_unaccepted(self) -> None:
        engine_root = Path("/tmp/paperx-source-resolution").resolve()
        corpus_root = engine_root / "corpus" / "synthetic"
        layout = ProjectLayout(
            engine_root=engine_root,
            mode="corpus",
            corpus_name="synthetic",
            project_dir=None,
            corpus_root=corpus_root,
            source_root=corpus_root,
            review_root=corpus_root / "_canon",
            runs_root=corpus_root / "_runs",
            tmp_root=engine_root / "tmp",
            figure_expectations_path=corpus_root / "figure_expectations.json",
        )
        config = build_pipeline_config(
            layout=layout,
            text_engine="native",
            use_external_layout=True,
            use_external_math=True,
            include_review=False,
        )
        state = PaperState.begin(
            "1990_synthetic_test_paper",
            config=config,
            started_at="2026-04-17T00:00:00Z",
        )

        native_layout = {
            "engine": "native_pdf",
            "pdf_path": str(state.pdf_path),
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
            "blocks": [{"id": "native-1", "page": 1, "order": 1, "text": "Native text", "role": "paragraph", "bbox": {}}],
        }

        resolved = resolve_paper_sources(
            state,
            config=config,
            layout_output=native_layout,
            figures=[],
            deps=_source_resolution_deps(
                extract_layout=lambda paper_id: native_layout,
            ),
            build_acquisition_route_report_impl=lambda paper_id, *, layout=None: {
                "paper_id": paper_id,
                "primary_route": "born_digital_scholarly",
            },
            build_source_scorecard_impl=lambda **kwargs: {
                "providers": [],
                "recommended_primary_layout_provider": "native_pdf",
                "recommended_primary_math_provider": None,
                "recommended_primary_metadata_provider": "docling",
                "recommended_primary_reference_provider": "docling",
                "metadata_recommendation_basis": "fallback_unaccepted",
                "reference_recommendation_basis": "fallback_unaccepted",
            },
            load_docling_metadata_observation_impl=lambda paper_id, *, layout=None: {
                "provider": "docling",
                "title": "Weak title",
                "abstract": "",
                "references": ["D. Ref"],
            },
            load_grobid_metadata_observation_impl=lambda paper_id, *, layout=None: {
                "provider": "grobid",
                "title": "Strong title",
                "abstract": "Strong abstract.",
                "references": ["G. Ref"],
            },
            load_mathpix_metadata_observation_impl=lambda paper_id, *, layout=None: None,
        )

        self.assertEqual(resolved.metadata_observation["provider"], "grobid")
        self.assertEqual(resolved.reference_observation["provider"], "grobid")


if __name__ == "__main__":
    unittest.main()
