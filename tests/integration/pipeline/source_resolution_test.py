import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.resolve_sources import resolve_paper_sources
from pipeline.state import PaperState


class SourceResolutionTest(unittest.TestCase):
    def test_resolve_paper_sources_populates_state(self) -> None:
        engine_root = Path("/tmp/paperx-source-resolution").resolve()
        corpus_root = engine_root / "corpus" / "synthetic"
        layout = ProjectLayout(
            engine_root=engine_root,
            mode="corpus",
            corpus_name="synthetic",
            project_dir=None,
            corpus_root=corpus_root,
            source_root=corpus_root,
            review_root=corpus_root / "review_drafts",
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
            "engine": "mathpix",
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
        )

        self.assertEqual(resolved.native_layout, native_layout)
        self.assertEqual(resolved.external_layout, external_layout)
        self.assertEqual(resolved.merged_layout["engine"], "merged_layout")
        self.assertEqual(resolved.mathpix_layout, mathpix_layout)
        self.assertEqual(resolved.external_math, external_math)
        self.assertEqual(resolved.figures[0]["caption"], "CAPTION TEXT")
        self.assertEqual(resolved.layout_engine_name, "mathpix")
        self.assertEqual(resolved.math_engine_name, "mathpix+heuristic")
        self.assertIn("pdf", resolved.input_fingerprints)


if __name__ == "__main__":
    unittest.main()
