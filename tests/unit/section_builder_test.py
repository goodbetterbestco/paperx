from __future__ import annotations

import sys
import unittest
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.assembly.section_builder import materialize_sections


class SectionBuilderTest(unittest.TestCase):
    def test_materialize_sections_filters_non_reference_records_and_tracks_blocks_math_and_references(self) -> None:
        node = SimpleNamespace(
            title="Methods",
            level=2,
            heading_id="heading-1",
            label=("2", "1"),
            records=[
                {"id": "keep-1", "kind": "paragraph"},
                {"id": "drop-figure", "kind": "figure_debris"},
                {"id": "drop-header", "kind": "header"},
                {"id": "drop-table", "kind": "table"},
                {"id": "drop-fragment", "kind": "fragment"},
                {"id": "keep-2", "kind": "paragraph"},
            ],
            children=[SimpleNamespace(id="child", title="Child", level=3, heading_id="child-heading", label=None, records=[], children=[])],
        )
        heading_record = {"id": "heading-1", "source_spans": [{"page": 1, "bbox": {"x0": 1}, "engine": "native_pdf"}]}
        records = [heading_record, *node.records]
        counters = {"block": 1, "math": 1, "reference": 1}

        def build_blocks_for_record(record, layout_by_id, figures_by_label, external_math_page_map, external_math_overlap_page_map, references_section, counters):
            block_id = f"blk-{record['id']}"
            return (
                [{"id": block_id, "type": "paragraph"}],
                [{"id": f"math-{record['id']}"}] if record["id"] == "keep-1" else [],
                [{"id": f"ref-{record['id']}"}] if record["id"] == "keep-2" else [],
            )

        blocks, sections, all_math, all_references = materialize_sections(
            section_nodes=[node],
            records=records,
            blocks=[],
            counters=counters,
            layout_by_id={},
            figures_by_label={},
            figures_by_page={},
            external_math_page_map={},
            external_math_overlap_page_map={},
            section_id_for=lambda current_node, index: f"sec-{index or current_node.title.lower()}",
            normalize_section_title=lambda title: title.strip().lower(),
            merge_reference_records=lambda section_records: list(section_records),
            is_figure_debris=lambda record, figures_by_page: record["kind"] == "figure_debris",
            looks_like_running_header_record=lambda record: record["kind"] == "header",
            looks_like_table_body_debris=lambda record: record["kind"] == "table",
            is_short_ocr_fragment=lambda record: record["kind"] == "fragment",
            suppress_embedded_table_headings=lambda section_records: list(section_records),
            merge_code_records=lambda section_records: list(section_records),
            merge_paragraph_records=lambda section_records: list(section_records),
            build_blocks_for_record=build_blocks_for_record,
            clean_text=lambda text: text.strip(),
            block_source_spans=lambda record: list(record.get("source_spans", [])),
        )

        self.assertEqual([block["id"] for block in blocks], ["blk-keep-1", "blk-keep-2"])
        self.assertEqual(all_math, [{"id": "math-keep-1"}])
        self.assertEqual(all_references, [{"id": "ref-keep-2"}])
        self.assertEqual(
            sections,
            [
                {
                    "id": "sec-1",
                    "label": "2.1",
                    "title": "Methods",
                    "level": 2,
                    "block_ids": ["blk-keep-1", "blk-keep-2"],
                    "children": ["sec-child"],
                    "source_spans": [{"page": 1, "bbox": {"x0": 1}, "engine": "native_pdf"}],
                }
            ],
        )

    def test_materialize_sections_merges_reference_sections_without_record_filters(self) -> None:
        node = SimpleNamespace(
            title="References",
            level=1,
            heading_id="heading-ref",
            label=None,
            records=[
                {"id": "raw-1", "kind": "reference"},
                {"id": "raw-2", "kind": "reference"},
            ],
            children=[],
        )
        seen_records: list[list[str]] = []

        def merge_reference_records(section_records):
            seen_records.append([record["id"] for record in section_records])
            return [{"id": "merged-reference", "kind": "reference"}]

        blocks, sections, all_math, all_references = materialize_sections(
            section_nodes=[node],
            records=[],
            blocks=[],
            counters={"block": 1, "math": 1, "reference": 1},
            layout_by_id={},
            figures_by_label={},
            figures_by_page={},
            external_math_page_map={},
            external_math_overlap_page_map={},
            section_id_for=lambda current_node, index: "sec-references",
            normalize_section_title=lambda title: title.strip().lower(),
            merge_reference_records=merge_reference_records,
            is_figure_debris=lambda record, figures_by_page: (_ for _ in ()).throw(AssertionError("reference sections should not use body filters")),
            looks_like_running_header_record=lambda record: False,
            looks_like_table_body_debris=lambda record: False,
            is_short_ocr_fragment=lambda record: False,
            suppress_embedded_table_headings=lambda section_records: section_records,
            merge_code_records=lambda section_records: section_records,
            merge_paragraph_records=lambda section_records: section_records,
            build_blocks_for_record=lambda record, layout_by_id, figures_by_label, external_math_page_map, external_math_overlap_page_map, references_section, counters: (
                [{"id": "blk-reference-1", "type": "reference"}],
                [],
                [{"id": "ref-1"}],
            ),
            clean_text=lambda text: text.strip(),
            block_source_spans=lambda record: [],
        )

        self.assertEqual(seen_records, [["raw-1", "raw-2"]])
        self.assertEqual([block["id"] for block in blocks], ["blk-reference-1"])
        self.assertEqual(all_math, [])
        self.assertEqual(all_references, [{"id": "ref-1"}])
        self.assertEqual(sections[0]["title"], "References")
        self.assertEqual(sections[0]["block_ids"], ["blk-reference-1"])
        self.assertEqual(sections[0]["source_spans"], [])


if __name__ == "__main__":
    unittest.main()
