import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.assembly.record_block_builder import build_blocks_for_record, split_code_lines
from pipeline.reconcile.block_merging import merge_code_records


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 640.0,
    height: float = 10.0,
    width: float = 240.0,
) -> dict[str, object]:
    return {
        "id": f"{record_type}-{page}-{y0}-{height}-{width}-{len(text)}",
        "page": page,
        "type": record_type,
        "text": text,
        "source_spans": [
            {
                "page": page,
                "bbox": {
                    "x0": 90.0,
                    "y0": y0,
                    "x1": 90.0 + width,
                    "y1": y0 + height,
                    "width": width,
                    "height": height,
                },
                "engine": "docling",
            }
        ],
        "meta": {},
    }


def _merge_code_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return merge_code_records(
        records,
        block_source_spans=rb._block_source_spans,
        clean_text=rb._clean_text,
    )


def _build_blocks_for_record(
    record: dict[str, object],
    layout_by_id: dict[str, object],
    figures_by_label: dict[str, dict[str, object]],
    external_math_by_page: dict[int, list[dict[str, object]]],
    external_math_overlap_by_page: dict[int, list[dict[str, object]]],
    references_section: bool,
    counters: dict[str, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    return build_blocks_for_record(
        record,
        layout_by_id,
        figures_by_label,
        external_math_by_page,
        external_math_overlap_by_page,
        references_section,
        counters,
        clean_record=rb._clean_record,
        record_analysis_text=rb._record_analysis_text,
        is_short_ocr_fragment=rb._is_short_ocr_fragment,
        block_source_spans=rb._block_source_spans,
        caption_label=rb.caption_label,
        default_review=rb.default_review,
        make_reference_entry=rb._make_reference_entry,
        looks_like_real_code_record=lambda text: rb._looks_like_real_code_record(text),
        split_code_lines=split_code_lines,
        list_item_marker=lambda text: rb._list_item_marker(text),
        normalize_paragraph_text=rb._normalize_paragraph_text,
        split_inline_math=rb.split_inline_math,
        repair_symbolic_ocr_spans=rb.repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=rb.extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=rb.merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=rb.normalize_inline_math_spans,
        review_for_math_entry=rb.review_for_math_entry,
        review_for_math_ref_block=rb.review_for_math_ref_block,
        looks_like_prose_paragraph=rb.looks_like_prose_paragraph,
        looks_like_prose_math_fragment=rb.looks_like_prose_math_fragment,
        match_external_math_entry=lambda record_item, external_math_map: rb.reconcile_match_external_math_entry(
            record_item,
            external_math_map,
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
        ),
        build_block_math_entry=rb.build_block_math_entry,
        normalize_formula_display_text=rb._normalize_formula_display_text,
        classify_math_block=rb.classify_math_block,
        review_for_algorithm_block_text=rb.review_for_algorithm_block_text,
        overlapping_external_math_entries=lambda record_item, overlap_map: rb.reconcile_overlapping_external_math_entries(
            record_item,
            overlap_map,
            block_source_spans=rb._block_source_spans,
        ),
        trim_embedded_display_math_from_paragraph=lambda text_value, record_item, overlapping_math: rb.reconcile_trim_embedded_display_math_from_paragraph(
            text_value,
            record_item,
            overlapping_math,
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
            display_math_prose_cue_re=rb.DISPLAY_MATH_PROSE_CUE_RE,
            display_math_resume_re=rb.DISPLAY_MATH_RESUME_RE,
            display_math_start_re=rb.DISPLAY_MATH_START_RE,
            mathish_ratio=rb._mathish_ratio,
            strong_operator_count=rb._strong_operator_count,
        ),
        looks_like_display_math_echo=lambda record_item, text_value, overlapping_math: rb.reconcile_looks_like_display_math_echo(
            record_item,
            text_value,
            overlapping_math,
            block_source_spans=rb._block_source_spans,
            clean_text=rb._clean_text,
            mathish_ratio=rb._mathish_ratio,
            strong_operator_count=rb._strong_operator_count,
            short_word_re=rb.SHORT_WORD_RE,
        ),
    )


class BlockBuilderTest(unittest.TestCase):
    def test_build_blocks_preserves_list_item_structure_and_inline_math(self) -> None:
        record = _record(
            record_type="list_item",
            text="Decompose the polygon in O(NlogN) time",
            page=5,
            y0=320.0,
            height=11.0,
            width=260.0,
        )
        record["meta"] = {"docling_label": "list_item"}

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual([block["type"] for block in blocks], ["list_item"])
        self.assertEqual(references, [])
        self.assertEqual(len(math_entries), 1)
        spans = blocks[0]["content"]["spans"]
        self.assertTrue(any(span.get("kind") == "inline_math_ref" for span in spans))
        self.assertFalse(blocks[0]["content"]["ordered"])

    def test_build_blocks_promotes_numbered_paragraph_to_list_item(self) -> None:
        record = _record(
            record_type="paragraph",
            text="1. intersection between two boundary curves: Let f and g be plane curves.",
            page=16,
            y0=420.0,
            height=12.0,
            width=320.0,
        )

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual([block["type"] for block in blocks], ["list_item"])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])
        self.assertEqual(blocks[0]["content"]["marker"], "1.")
        self.assertTrue(blocks[0]["content"]["ordered"])
        item_text = "".join(span.get("text", "") for span in blocks[0]["content"]["spans"])
        self.assertEqual(item_text, "intersection between two boundary curves: Let f and g be plane curves.")

    def test_merge_code_records_combines_adjacent_code_lines(self) -> None:
        first = _record(
            record_type="code",
            text="if (q.type != p.type)",
            page=6,
            y0=420.0,
            height=10.0,
            width=180.0,
        )
        second = _record(
            record_type="code",
            text="push(q);",
            page=6,
            y0=432.0,
            height=10.0,
            width=120.0,
        )

        merged = _merge_code_records([first, second])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["type"], "code")
        self.assertIn("if (q.type != p.type) ;; push(q);", merged[0]["text"])

    def test_build_blocks_emits_code_block_for_code_record(self) -> None:
        record = _record(
            record_type="code",
            text="struct start point ;; double xval, yval;;",
            page=17,
            y0=510.0,
            height=12.0,
            width=260.0,
        )

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual([block["type"] for block in blocks], ["code"])
        self.assertEqual(blocks[0]["content"]["lines"], ["struct start point", "double xval, yval"])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])

    def test_build_blocks_allows_math_path_for_formula_like_code_record(self) -> None:
        record = _record(
            record_type="code",
            text="E ( u;; s;; t ) = D 2 ( s;; t ) + ( X ( s;; t ) W f ( u ) ) 2 .",
            page=18,
            y0=255.0,
            height=40.0,
            width=220.0,
        )

        external_math_entry = {
            "id": "mathpix-eq-p018-0001",
            "kind": "display",
            "display_latex": r"E(u,s,t)=D^2(s,t)+(X(s,t)W_f(u))^2.",
            "source_spans": [
                {
                    "page": 18,
                    "bbox": {
                        "x0": 97.0,
                        "y0": 253.0,
                        "x1": 321.0,
                        "y1": 299.0,
                        "width": 224.0,
                        "height": 46.0,
                    },
                    "engine": "mathpix",
                }
            ],
            "compiled_targets": {},
            "conversion": {"status": "source_only"},
            "alternates": [],
            "review": {"status": "needs_review", "risk": "medium", "notes": []},
        }

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {18: [external_math_entry]},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual([block["type"] for block in blocks], ["display_equation_ref"])
        self.assertEqual(math_entries[0]["id"], "mathpix-eq-p018-0001")
        self.assertEqual(references, [])

    def test_build_blocks_drops_duplicate_formula_echo_paragraph(self) -> None:
        record = _record(
            record_type="paragraph",
            text="E ( u;; s;; t ) = D 2 ( s;; t )+ ( X ( s;; t ) W f ( u ) ; X f ( u ) W ( s;; t )) 2 .",
            page=18,
            y0=255.0,
            height=40.0,
            width=220.0,
        )

        overlapping_math_entry = {
            "id": "mathpix-eq-p018-0003",
            "kind": "display",
            "display_latex": r"\begin{aligned} E(u,s,t)&=D^2(s,t)+\left(X(s,t)W_f(u)-X_f(u)W(s,t)\right)^2 . \end{aligned}",
            "source_spans": [
                {
                    "page": 18,
                    "bbox": {
                        "x0": 96.5,
                        "y0": 253.0,
                        "x1": 320.5,
                        "y1": 299.0,
                        "width": 224.0,
                        "height": 46.0,
                    },
                    "engine": "mathpix",
                }
            ],
        }

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {18: [overlapping_math_entry]},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(blocks, [])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])

    def test_build_blocks_drops_short_overlapping_display_math_token_echo(self) -> None:
        record = _record(
            record_type="paragraph",
            text="x 2 1 x 2 ∂πy ∂x 1",
            page=25,
            y0=318.14,
            height=12.73,
            width=29.94,
        )
        record["source_spans"][0]["bbox"]["x0"] = 96.87
        record["source_spans"][0]["bbox"]["x1"] = 126.81

        overlapping_math_entry = {
            "id": "mathpix-eq-p025-0173",
            "kind": "display",
            "display_latex": r"x_{1}^{2} x_{2} \frac{\partial \pi_{y}}{\partial x_{1}}",
            "source_spans": [
                {
                    "page": 25,
                    "bbox": {
                        "x0": 96.46,
                        "y0": 318.46,
                        "x1": 127.95,
                        "y1": 330.96,
                        "width": 31.49,
                        "height": 12.5,
                    },
                    "engine": "mathpix",
                }
            ],
        }

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {25: [overlapping_math_entry]},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(blocks, [])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])

    def test_block_builder_drops_merged_table_marker_cloud(self) -> None:
        spans = [
            _record(record_type="paragraph", text="CADfix (ITI)", page=24, y0=403.78, height=8.07, width=49.54)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.53)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=401.4, height=10.45, width=13.27)["source_spans"][0],
            _record(record_type="paragraph", text="(3)", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
            _record(record_type="paragraph", text="Y", page=24, y0=403.78, height=8.07, width=8.5)["source_spans"][0],
        ]
        record = {
            "id": "merged-table-marker-cloud",
            "page": 24,
            "type": "paragraph",
            "text": "CADfix (ITI) Y Y (3) Y Y Y Y Y Y",
            "source_spans": spans,
            "meta": {},
        }

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual(blocks, [])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])

    def test_block_builder_keeps_forced_prose_math_fragment_as_paragraph(self) -> None:
        record = {
            "id": "forced-prose-math-fragment",
            "page": 11,
            "type": "paragraph",
            "text": "glyph[negationslash] glyph[negationslash] glyph[negationslash] We also assume that π y (0 , 0) = (0 , 0).",
            "source_spans": [
                _record(record_type="paragraph", text="glyph[negationslash]", page=11, y0=462.29, height=15.23, width=12.0)["source_spans"][0],
                _record(record_type="paragraph", text="glyph[negationslash]", page=11, y0=486.2, height=15.23, width=12.0)["source_spans"][0],
                _record(record_type="paragraph", text="glyph[negationslash]", page=11, y0=524.82, height=15.24, width=12.0)["source_spans"][0],
                _record(record_type="paragraph", text="We also assume that π y (0 , 0) = (0 , 0).", page=11, y0=548.73, height=9.63, width=164.78)["source_spans"][0],
            ],
            "meta": {"forced_math_kind": "display"},
        }

        blocks, math_entries, references = _build_blocks_for_record(
            record,
            {},
            {},
            {},
            {},
            False,
            {"block": 1, "math": 1, "reference": 1, "inline_math": 1},
        )

        self.assertEqual([block["type"] for block in blocks], ["paragraph"])
        self.assertEqual(math_entries, [])
        self.assertEqual(references, [])


if __name__ == "__main__":
    unittest.main()
