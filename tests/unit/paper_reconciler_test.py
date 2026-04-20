from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.paper_reconciler import (
    reconcile_paper_document,
    run_paper_pipeline,
)
from pipeline.orchestrator.pipeline_deps import (
    PaperDocumentAssemblyDeps,
    PaperPipelineDeps,
    PaperRecordNormalizationDeps,
    PaperSourceResolutionDeps,
)
from pipeline.state import PaperState


def _layout() -> ProjectLayout:
    root = Path("/tmp/paperx-paper-reconciler").resolve()
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


def _pipeline_deps() -> PaperPipelineDeps:
    return PaperPipelineDeps(
        source_resolution=PaperSourceResolutionDeps(
            extract_layout=lambda paper_id: {"engine": "native_pdf"},
            load_external_layout=lambda paper_id: None,
            merge_native_and_external_layout=lambda native_layout, external_layout: native_layout,
            load_external_math=lambda paper_id: None,
            load_mathpix_layout=lambda paper_id: None,
            extract_figures=lambda paper_id: [],
            normalize_figure_caption_text=lambda text: text,
        ),
        record_normalization=PaperRecordNormalizationDeps(
            external_math_by_page=lambda entries: {},
            merge_layout_and_figure_records=lambda blocks, figures: ([], {}),
            inject_external_math_records=lambda records, layout_blocks, external_math_entries: ([], set()),
            mark_records_with_external_math_overlap=lambda records, overlap_map: records,
            repair_record_text_with_mathpix_hints=lambda records, mathpix_layout: records,
            pdftotext_available=lambda: False,
            repair_record_text_with_pdftotext=lambda records, pages, heights: records,
            extract_pdftotext_pages=lambda paper_id: {},
            page_height_map=lambda layout: {},
            promote_heading_like_records=lambda records: records,
            merge_math_fragment_records=lambda records: records,
            page_one_front_matter_records=lambda records, mathpix_layout: [],
            is_title_page_metadata_record=lambda record: False,
            build_section_tree=lambda records: ([], []),
        ),
        document_assembly=PaperDocumentAssemblyDeps(
            build_front_matter=lambda paper_id, prelude, page_one_records, blocks, next_index: ({"title": "Synthetic Test Paper"}, [], next_index, []),
            attach_orphan_numbered_roots=lambda roots: roots,
            split_late_prelude_for_missing_intro=lambda prelude, roots: (prelude, []),
            normalize_section_title=lambda title: title,
            leading_abstract_text=lambda node: ("", []),
            front_block_text=lambda blocks, block_id: "",
            default_review=lambda **kwargs: {"status": "unreviewed", "risk": "medium", "notes": ""},
            block_source_spans=lambda record: [],
            build_abstract_decision=lambda **kwargs: kwargs,
            should_replace_front_matter_abstract=lambda text: False,
            recover_missing_front_matter_abstract=lambda front_matter, blocks, prelude, ordered_roots: False,
            section_node_type=SimpleNamespace,
            figure_label_token=lambda figure: None,
            prepare_section_nodes=lambda **kwargs: [],
            split_trailing_reference_records=lambda records: (records, []),
            extract_reference_records_from_tail_section=lambda records: (records, []),
            reference_records_from_mathpix_layout=lambda mathpix_layout: [],
            materialize_sections=lambda **kwargs: ([], [], [], []),
            section_id_for=lambda node, index: f"sec-{index}",
            merge_reference_records=lambda records: records,
            is_figure_debris=lambda record, figures_by_page: False,
            looks_like_running_header_record=lambda record: False,
            looks_like_table_body_debris=lambda record: False,
            is_short_ocr_fragment=lambda record: False,
            suppress_embedded_table_headings=lambda records: records,
            merge_code_records=lambda records: records,
            merge_paragraph_records=lambda records: records,
            build_blocks_for_record=lambda record, layout_by_id, figures_by_label, external_math_page_map, external_math_overlap_page_map, allow_math, counters: ([], [], []),
            clean_text=lambda text: text,
            compile_formulas=lambda entries: entries,
            annotate_formula_classifications=lambda entries: entries,
            annotate_formula_semantic_expr=lambda entries: entries,
            suppress_graphic_display_math_blocks=lambda blocks, compiled_math, sections, counters: (blocks, compiled_math, sections),
            suppress_running_header_blocks=lambda blocks, sections: (blocks, sections),
            normalize_footnote_blocks=lambda blocks, sections: (blocks, sections),
            merge_paragraph_blocks=lambda blocks, sections: (blocks, sections),
            now_iso=lambda: "2026-04-19T00:00:00Z",
            build_canonical_document=lambda **kwargs: kwargs,
        ),
    )


def _pipeline_kwargs() -> dict[str, object]:
    return {
        "text_engine": "hybrid",
        "use_external_layout": True,
        "use_external_math": False,
        "layout_output": {"engine": "native_pdf"},
        "figures": [],
        "deps": _pipeline_deps(),
    }


class PaperReconcilerTest(unittest.TestCase):
    def test_run_paper_pipeline_builds_config_and_threads_state_through_stages(self) -> None:
        layout = _layout()
        config = SimpleNamespace(layout=layout)
        calls: list[str] = []

        def fake_resolve_sources(state: PaperState, *, config, **kwargs) -> PaperState:
            calls.append("resolve")
            self.assertEqual(state.started_at, "2026-04-19T00:00:00Z")
            self.assertIs(config.layout, layout)
            state.native_layout = {"pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf", "page_count": 1, "page_sizes_pt": [], "blocks": []}
            return state

        def fake_normalize_records(state: PaperState, *, config, **kwargs) -> PaperState:
            calls.append("normalize")
            self.assertIs(config.layout, layout)
            state.merged_layout = {"pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf", "page_count": 1, "page_sizes_pt": [], "blocks": []}
            return state

        def fake_assemble_document(state: PaperState, **kwargs) -> PaperState:
            calls.append("assemble")
            state.document = {"paper_id": state.paper_id, "title": "Synthetic Test Paper"}
            return state

        with (
            patch("pipeline.orchestrator.paper_reconciler.build_pipeline_config", return_value=config) as build_config,
            patch("pipeline.orchestrator.paper_reconciler.resolve_paper_sources", side_effect=fake_resolve_sources),
            patch("pipeline.orchestrator.paper_reconciler.normalize_paper_records", side_effect=fake_normalize_records),
            patch("pipeline.orchestrator.paper_reconciler.assemble_paper_document", side_effect=fake_assemble_document),
        ):
            result = run_paper_pipeline(
                "1990_synthetic_test_paper",
                **_pipeline_kwargs(),
                config=None,
                state=None,
            )

        self.assertEqual(calls, ["resolve", "normalize", "assemble"])
        self.assertEqual(result.document, {"paper_id": "1990_synthetic_test_paper", "title": "Synthetic Test Paper"})
        build_config.assert_called_once_with(
            text_engine="hybrid",
            use_external_layout=True,
            use_external_math=False,
            include_review=False,
        )

    def test_reconcile_paper_document_returns_document_from_pipeline_state(self) -> None:
        with patch(
            "pipeline.orchestrator.paper_reconciler.run_paper_pipeline",
            return_value=PaperState(
                paper_id="1990_synthetic_test_paper",
                pdf_path=Path("/tmp/1990_synthetic_test_paper.pdf"),
                started_at="2026-04-19T00:00:00Z",
                document={"paper_id": "1990_synthetic_test_paper", "title": "Synthetic Test Paper"},
            ),
        ):
            document = reconcile_paper_document("1990_synthetic_test_paper", **_pipeline_kwargs())

        self.assertEqual(document["title"], "Synthetic Test Paper")

    def test_reconcile_paper_document_raises_when_pipeline_state_has_no_document(self) -> None:
        with patch(
            "pipeline.orchestrator.paper_reconciler.run_paper_pipeline",
            return_value=PaperState(
                paper_id="1990_synthetic_test_paper",
                pdf_path=Path("/tmp/1990_synthetic_test_paper.pdf"),
                started_at="2026-04-19T00:00:00Z",
                document=None,
            ),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                reconcile_paper_document("1990_synthetic_test_paper", **_pipeline_kwargs())

        self.assertEqual(str(ctx.exception), "Pipeline did not produce a document for 1990_synthetic_test_paper")


if __name__ == "__main__":
    unittest.main()
