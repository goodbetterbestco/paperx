from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.orchestrator.pipeline_deps import PaperRecordNormalizationDeps
from pipeline.orchestrator.normalize_records import normalize_paper_records
from pipeline.state import PaperState


def _state(*, layout: dict[str, Any] | None = None) -> PaperState:
    return PaperState(
        paper_id="1990_synthetic_test_paper",
        pdf_path=Path("/tmp/1990_synthetic_test_paper.pdf"),
        started_at="2026-04-19T00:00:00Z",
        merged_layout=layout,
        native_layout=layout,
        external_math={"entries": [{"id": "math-1"}, {"id": "math-2"}]},
        figures=[{"id": "fig-1", "page": 1, "label": "Figure 1"}],
        mathpix_layout={"engine": "mathpix"},
    )


def _record_normalization_deps(**overrides: object) -> PaperRecordNormalizationDeps:
    values: dict[str, object] = {
        "external_math_by_page": lambda entries: {},
        "merge_layout_and_figure_records": lambda blocks, figures: ([], {}),
        "inject_external_math_records": lambda records, layout_blocks, external_math_entries: ([], set()),
        "mark_records_with_external_math_overlap": lambda records, overlap_map: records,
        "repair_record_text_with_mathpix_hints": lambda records, mathpix_layout: records,
        "pdftotext_available": lambda: False,
        "repair_record_text_with_pdftotext": lambda records, pages, heights: records,
        "extract_pdftotext_pages": lambda paper_id: {},
        "page_height_map": lambda layout: {},
        "promote_heading_like_records": lambda records: records,
        "merge_math_fragment_records": lambda records: records,
        "page_one_front_matter_records": lambda records, mathpix_layout: [],
        "is_title_page_metadata_record": lambda record: False,
        "build_section_tree": lambda records: ([], []),
    }
    values.update(overrides)
    return PaperRecordNormalizationDeps(**values)


class NormalizeRecordsOrchestratorTest(unittest.TestCase):
    def test_normalize_paper_records_requires_resolved_layout(self) -> None:
        state = _state(layout=None)
        config = SimpleNamespace(text_engine="native", pdftotext_enabled=False)

        with self.assertRaises(RuntimeError) as ctx:
            normalize_paper_records(
                state,
                config=config,
                deps=_record_normalization_deps(),
            )

        self.assertEqual(str(ctx.exception), "Missing resolved layout for 1990_synthetic_test_paper")

    def test_normalize_paper_records_threads_records_external_math_and_pdftotext(self) -> None:
        layout = {
            "blocks": [{"id": "layout-1", "page": 1}],
            "page_sizes_pt": [{"page": 1, "height": 792.0}],
        }
        state = _state(layout=layout)
        config = SimpleNamespace(text_engine="hybrid", pdftotext_enabled=True)

        page_maps_seen: list[list[str]] = []

        def external_math_by_page(entries: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
            page_maps_seen.append([entry["id"] for entry in entries])
            return {1: list(entries)}

        result = normalize_paper_records(
            state,
            config=config,
            deps=_record_normalization_deps(
                external_math_by_page=external_math_by_page,
                merge_layout_and_figure_records=lambda blocks, figures: (
                    [
                        {"id": "title-meta", "kind": "meta"},
                        {"id": "body-1", "kind": "paragraph"},
                    ],
                    {"layout-1": {"page": 1}},
                ),
                inject_external_math_records=lambda records, layout_blocks, external_math_entries: (
                    [*records, {"id": "math-injected", "kind": "math"}],
                    {"math-1"},
                ),
                mark_records_with_external_math_overlap=lambda records, overlap_map: [
                    {**record, "overlap_pages": sorted(overlap_map)}
                    for record in records
                ],
                repair_record_text_with_mathpix_hints=lambda records, mathpix_layout: [
                    {**record, "mathpix_hint": bool(mathpix_layout)}
                    for record in records
                ],
                pdftotext_available=lambda: True,
                repair_record_text_with_pdftotext=lambda records, pages, heights: [
                    {**record, "pdftotext_pages": sorted(pages), "page_heights": heights}
                    for record in records
                ],
                extract_pdftotext_pages=lambda paper_id: {1: ["Recovered text line"]},
                page_height_map=lambda resolved_layout: {1: 792.0},
                promote_heading_like_records=lambda records: [{**record, "promoted": True} for record in records],
                merge_math_fragment_records=lambda records: [{**record, "merged_math": True} for record in records],
                page_one_front_matter_records=lambda records, mathpix_layout: [record for record in records if record["id"] == "title-meta"],
                is_title_page_metadata_record=lambda record: record["id"] == "title-meta",
                build_section_tree=lambda records: (
                    [{"id": "prelude-1"}],
                    [SimpleNamespace(title="Methods", level=1, heading_id="sec-methods", records=list(records), children=[])],
                ),
            ),
        )

        self.assertIs(result, state)
        self.assertEqual(page_maps_seen, [["math-1", "math-2"], ["math-2"]])
        self.assertEqual(state.layout_by_id, {"layout-1": {"page": 1}})
        self.assertEqual(state.page_one_records[0]["id"], "title-meta")
        self.assertEqual([record["id"] for record in state.records], ["body-1", "math-injected"])
        self.assertEqual(state.records[0]["pdftotext_pages"], [1])
        self.assertEqual(state.records[0]["page_heights"], {1: 792.0})
        self.assertTrue(all(record["promoted"] for record in state.records))
        self.assertTrue(all(record["merged_math"] for record in state.records))
        self.assertEqual(state.prelude_records, [{"id": "prelude-1"}])
        self.assertEqual(state.section_roots[0].title, "Methods")
        self.assertEqual(state.external_math_entries, [{"id": "math-2"}])
        self.assertEqual(state.external_math_overlap_page_map, {1: [{"id": "math-1"}, {"id": "math-2"}]})
        self.assertEqual(state.external_math_page_map, {1: [{"id": "math-2"}]})
        self.assertEqual(state.effective_text_engine, "native_pdf+pdftotext")


if __name__ == "__main__":
    unittest.main()
