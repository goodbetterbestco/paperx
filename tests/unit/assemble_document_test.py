from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.orchestrator.assemble_document import assemble_paper_document
from pipeline.state import PaperState


@dataclass
class _SectionNode:
    title: str
    level: int
    heading_id: str
    label: tuple[str, ...] | None = None
    records: list[dict[str, Any]] = field(default_factory=list)
    children: list[Any] = field(default_factory=list)


def _state(*, layout: dict[str, Any] | None = None) -> PaperState:
    return PaperState(
        paper_id="1990_synthetic_test_paper",
        pdf_path=Path("/tmp/1990_synthetic_test_paper.pdf"),
        started_at="2026-04-19T00:00:00Z",
        merged_layout=layout,
        native_layout=layout,
    )


def _base_kwargs() -> dict[str, Any]:
    return {
        "build_front_matter": lambda paper_id, prelude, page_one_records, blocks, next_index: (
            {"title": "Synthetic Test Paper"},
            list(blocks),
            next_index,
            list(prelude),
        ),
        "attach_orphan_numbered_roots": lambda roots: list(roots),
        "split_late_prelude_for_missing_intro": lambda prelude, roots: (list(prelude), []),
        "normalize_section_title": lambda title: title.strip().lower(),
        "leading_abstract_text": lambda node: ("", []),
        "front_block_text": lambda blocks, block_id: "",
        "default_review": lambda **kwargs: {"status": "unreviewed", "risk": kwargs.get("risk", "medium"), "notes": ""},
        "block_source_spans": lambda record: list(record.get("source_spans", [])),
        "build_abstract_decision": lambda **kwargs: dict(kwargs),
        "should_replace_front_matter_abstract": lambda text: False,
        "recover_missing_front_matter_abstract": lambda front_matter, blocks, prelude, ordered_roots: False,
        "section_node_type": _SectionNode,
        "figure_label_token": lambda figure: figure.get("label"),
        "prepare_section_nodes": lambda **kwargs: list(kwargs["ordered_roots"]),
        "split_trailing_reference_records": lambda records: (list(records), []),
        "extract_reference_records_from_tail_section": lambda records: (list(records), []),
        "reference_records_from_mathpix_layout": lambda mathpix_layout: [],
        "materialize_sections": lambda **kwargs: (
            list(kwargs["blocks"]),
            [
                {
                    "id": kwargs["section_id_for"](node, index),
                    "title": node.title,
                    "level": node.level,
                    "block_ids": [],
                    "children": [],
                }
                for index, node in enumerate(kwargs["section_nodes"], start=1)
            ],
            [],
            [],
        ),
        "section_id_for": lambda node, index: f"sec-{index}",
        "merge_reference_records": lambda records: list(records),
        "is_figure_debris": lambda record, figures_by_page: False,
        "looks_like_running_header_record": lambda record: False,
        "looks_like_table_body_debris": lambda record: False,
        "is_short_ocr_fragment": lambda record: False,
        "suppress_embedded_table_headings": lambda records: list(records),
        "merge_code_records": lambda records: list(records),
        "merge_paragraph_records": lambda records: list(records),
        "build_blocks_for_record": lambda record, layout_by_id, figures_by_label, external_math_page_map, external_math_overlap_page_map, allow_math, counters: ([], [], []),
        "clean_text": lambda text: text.strip(),
        "compile_formulas": lambda entries: list(entries),
        "annotate_formula_classifications": lambda entries: list(entries),
        "annotate_formula_semantic_expr": lambda entries: list(entries),
        "suppress_graphic_display_math_blocks": lambda blocks, compiled_math, sections, counters: (list(blocks), list(compiled_math), list(sections)),
        "suppress_running_header_blocks": lambda blocks, sections: (list(blocks), list(sections)),
        "normalize_footnote_blocks": lambda blocks, sections: (list(blocks), list(sections)),
        "merge_paragraph_blocks": lambda blocks, sections: (list(blocks), list(sections)),
        "now_iso": lambda: "2026-04-19T00:00:00Z",
        "build_canonical_document": lambda **kwargs: dict(kwargs),
    }


class AssembleDocumentTest(unittest.TestCase):
    def test_assemble_paper_document_requires_resolved_layout(self) -> None:
        state = _state(layout=None)

        with self.assertRaises(RuntimeError) as ctx:
            assemble_paper_document(state, **_base_kwargs())

        self.assertEqual(str(ctx.exception), "Missing resolved layout for 1990_synthetic_test_paper")

    def test_assemble_paper_document_creates_leading_abstract_and_synthetic_intro(self) -> None:
        layout = {
            "pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 612.0, "height": 792.0}],
            "blocks": [],
        }
        state = _state(layout=layout)
        state.page_one_records = [{"id": "page-one"}]
        state.prelude_records = [{"id": "prelude-1", "source_spans": [{"page": 1, "bbox": {}, "engine": "native_pdf"}]}]
        state.section_roots = [
            SimpleNamespace(
                title="Abstract",
                level=1,
                heading_id="sec-abstract",
                label=None,
                records=[{"id": "abs-1", "source_spans": [{"page": 1, "bbox": {"x0": 1}, "engine": "native_pdf"}]}],
                children=[],
            ),
            SimpleNamespace(
                title="Methods",
                level=1,
                heading_id="sec-methods",
                label=("2",),
                records=[{"id": "m-1"}],
                children=[],
            ),
        ]

        captured: dict[str, Any] = {}
        kwargs = _base_kwargs()
        kwargs.update(
            {
                "build_front_matter": lambda paper_id, prelude, page_one_records, blocks, next_index: (
                    {
                        "title": "Synthetic Test Paper",
                        "_debug_title_decision": {"source": "front_matter_records"},
                    },
                    list(blocks),
                    next_index,
                    list(prelude),
                ),
                "leading_abstract_text": lambda node: (
                    "A compact abstract from the leading abstract section.",
                    list(node.records),
                ),
                "prepare_section_nodes": lambda **kwargs: captured.setdefault("ordered_roots", list(kwargs["ordered_roots"])),
                "build_canonical_document": lambda **kwargs: captured.setdefault("document", dict(kwargs)),
            }
        )

        result = assemble_paper_document(state, **kwargs)

        self.assertIs(result, state)
        self.assertEqual(result.front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(result.blocks[0]["content"]["spans"][0]["text"], "A compact abstract from the leading abstract section.")
        self.assertEqual(result.blocks[0]["source_spans"], [{"page": 1, "bbox": {"x0": 1}, "engine": "native_pdf"}])
        self.assertEqual(result.decision_artifacts["title"], {"source": "front_matter_records"})
        self.assertEqual(result.decision_artifacts["abstract"]["source"], "leading_abstract_section_created")
        self.assertEqual([node.title for node in captured["ordered_roots"]], ["Introduction", "Methods"])
        self.assertEqual(captured["ordered_roots"][0].heading_id, "synthetic-introduction")
        self.assertEqual(captured["ordered_roots"][0].label, ("1",))
        self.assertEqual(captured["document"]["source"]["pdf_path"], "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf")
        self.assertEqual(captured["document"]["title"], "Synthetic Test Paper")
        self.assertEqual(captured["document"]["decision_artifacts"]["abstract"]["source"], "leading_abstract_section_created")

    def test_assemble_paper_document_replaces_placeholder_front_matter_abstract(self) -> None:
        layout = {
            "pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
            "page_count": 1,
            "page_sizes_pt": [{"page": 1, "width": 612.0, "height": 792.0}],
            "blocks": [],
        }
        state = _state(layout=layout)
        state.section_roots = [
            SimpleNamespace(
                title="Abstract",
                level=1,
                heading_id="sec-abstract",
                label=None,
                records=[{"id": "abs-1", "source_spans": [{"page": 1, "bbox": {"x0": 7}, "engine": "native_pdf"}]}],
                children=[],
            )
        ]

        kwargs = _base_kwargs()
        kwargs.update(
            {
                "build_front_matter": lambda paper_id, prelude, page_one_records, blocks, next_index: (
                    {
                        "title": "Synthetic Test Paper",
                        "abstract_block_id": "blk-front-abstract-1",
                    },
                    [
                        {
                            "id": "blk-front-abstract-1",
                            "type": "paragraph",
                            "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                            "source_spans": [],
                            "alternates": [],
                            "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                        }
                    ],
                    next_index,
                    [],
                ),
                "leading_abstract_text": lambda node: ("Recovered abstract from body section.", list(node.records)),
                "front_block_text": lambda blocks, block_id: next(
                    (
                        span["text"]
                        for block in blocks
                        if block.get("id") == block_id
                        for span in block.get("content", {}).get("spans", [])
                    ),
                    "",
                ),
                "should_replace_front_matter_abstract": lambda text: text == "[missing from original]",
            }
        )

        result = assemble_paper_document(state, **kwargs)

        self.assertEqual(result.blocks[0]["content"]["spans"][0]["text"], "Recovered abstract from body section.")
        self.assertEqual(result.blocks[0]["source_spans"], [{"page": 1, "bbox": {"x0": 7}, "engine": "native_pdf"}])
        self.assertEqual(result.decision_artifacts["abstract"]["source"], "leading_abstract_section_replaced")


if __name__ == "__main__":
    unittest.main()
