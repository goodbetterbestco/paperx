import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.shared_patterns as rsp
from pipeline.assembly.record_block_builder import (
    make_build_blocks_for_record,
    split_code_lines,
)
from pipeline.figures.labels import caption_label
from pipeline.math import (
    classify_math_block,
    extract_general_inline_math_spans,
    looks_like_prose_math_fragment,
    looks_like_prose_paragraph,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    review_for_algorithm_block_text,
    review_for_math_entry,
    review_for_math_ref_block,
    split_inline_math,
)
from pipeline.math.extract import build_block_math_entry, repair_symbolic_ocr_spans
from pipeline.reconcile.block_builder_binding_runtime import (
    make_list_item_marker,
    make_looks_like_real_code_record,
    make_match_external_math_entry,
)
from pipeline.reconcile.math_fragments_runtime import make_math_signal_count, strong_operator_count
from pipeline.reconcile.math_runtime import (
    make_looks_like_display_math_echo,
    make_overlapping_external_math_entries,
    make_trim_embedded_display_math_from_paragraph,
)
from pipeline.reconcile.math_suppression import (
    looks_like_display_math_echo as suppression_looks_like_display_math_echo,
    overlapping_external_math_entries as suppression_overlapping_external_math_entries,
    trim_embedded_display_math_from_paragraph as suppression_trim_embedded_display_math_from_paragraph,
)
from pipeline.reconcile.block_merging import make_merge_code_records
from pipeline.reconcile.references import make_reference_entry_builder as make_reference_entry
from pipeline.reconcile.runtime_constants import (
    CONTROL_CHAR_RE,
    LABEL_CLOUD_TOKEN_RE,
    LEADING_NEGATIONSLASH_ARTIFACT_RE,
    LEADING_OCR_MARKER_RE,
    LEADING_PUNCT_ARTIFACT_RE,
    LEADING_VAR_ARTIFACT_RE,
    MATH_TOKEN_RE,
    QUOTED_IDENTIFIER_FRAGMENT_RE,
    SHORT_OCR_NOISE_RE,
    TERMINAL_PUNCTUATION_RE,
    TRAILING_NUMERIC_ARTIFACT_RE,
)
from pipeline.reconcile.screening_runtime import (
    make_is_short_ocr_fragment,
    make_looks_like_browser_ui_scrap,
    make_looks_like_glyph_noise_cloud,
    make_looks_like_quoted_identifier_fragment,
    make_looks_like_table_marker_cloud,
    make_looks_like_vertical_label_cloud,
)
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_record,
    make_clean_text,
    make_mathish_ratio,
    make_normalize_formula_display_text,
    make_normalize_paragraph_text,
    make_record_analysis_text,
    make_strip_known_running_header_text,
    make_word_count,
)
from pipeline.text.headings import compact_text
from pipeline.text.prose import decode_ocr_codepoint_tokens, normalize_prose_text
from pipeline.text.references import normalize_reference_text
from pipeline.types import default_review


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
STRIP_KNOWN_RUNNING_HEADER_TEXT = make_strip_known_running_header_text(
    procedia_running_header_re=rsp.PROCEDIA_RUNNING_HEADER_RE,
    clean_text=CLEAN_TEXT,
)
CLEAN_RECORD = make_clean_record(
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
)
NORMALIZE_PARAGRAPH_TEXT = make_normalize_paragraph_text(
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
    leading_negationslash_artifact_re=LEADING_NEGATIONSLASH_ARTIFACT_RE,
    leading_ocr_marker_re=LEADING_OCR_MARKER_RE,
    leading_punct_artifact_re=LEADING_PUNCT_ARTIFACT_RE,
    leading_var_artifact_re=LEADING_VAR_ARTIFACT_RE,
    trailing_numeric_artifact_re=TRAILING_NUMERIC_ARTIFACT_RE,
    normalize_prose_text=normalize_prose_text,
    clean_text=CLEAN_TEXT,
)
NORMALIZE_FORMULA_DISPLAY_TEXT = make_normalize_formula_display_text(
    clean_text=CLEAN_TEXT,
    decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
)
RECORD_ANALYSIS_TEXT = make_record_analysis_text(clean_text=CLEAN_TEXT)
WORD_COUNT = make_word_count(short_word_re=rsp.SHORT_WORD_RE)
MATH_SIGNAL_COUNT = make_math_signal_count(math_token_re=MATH_TOKEN_RE)
MATHISH_RATIO = make_mathish_ratio(
    word_count=WORD_COUNT,
    math_signal_count=MATH_SIGNAL_COUNT,
)
LOOKS_LIKE_BROWSER_UI_SCRAP = make_looks_like_browser_ui_scrap(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT = make_looks_like_quoted_identifier_fragment(
    short_word_re=rsp.SHORT_WORD_RE,
    quoted_identifier_fragment_re=QUOTED_IDENTIFIER_FRAGMENT_RE,
)
LOOKS_LIKE_GLYPH_NOISE_CLOUD = make_looks_like_glyph_noise_cloud(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_VERTICAL_LABEL_CLOUD = make_looks_like_vertical_label_cloud(
    strong_operator_count=strong_operator_count,
)
LOOKS_LIKE_TABLE_MARKER_CLOUD = make_looks_like_table_marker_cloud(
    strong_operator_count=strong_operator_count,
)
IS_SHORT_OCR_FRAGMENT = make_is_short_ocr_fragment(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    looks_like_browser_ui_scrap=LOOKS_LIKE_BROWSER_UI_SCRAP,
    looks_like_quoted_identifier_fragment=LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT,
    looks_like_glyph_noise_cloud=LOOKS_LIKE_GLYPH_NOISE_CLOUD,
    looks_like_vertical_label_cloud=LOOKS_LIKE_VERTICAL_LABEL_CLOUD,
    looks_like_table_marker_cloud=LOOKS_LIKE_TABLE_MARKER_CLOUD,
    short_word_re=rsp.SHORT_WORD_RE,
    label_cloud_token_re=LABEL_CLOUD_TOKEN_RE,
    short_ocr_noise_re=SHORT_OCR_NOISE_RE,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    strong_operator_count=strong_operator_count,
)
MAKE_REFERENCE_ENTRY = make_reference_entry(
    clean_text=CLEAN_TEXT,
    normalize_reference_text=normalize_reference_text,
    block_source_spans=block_source_spans,
    default_review=default_review,
)
LIST_ITEM_MARKER = make_list_item_marker(clean_text=CLEAN_TEXT)
LOOKS_LIKE_REAL_CODE_RECORD = make_looks_like_real_code_record(clean_text=CLEAN_TEXT)
MATCH_EXTERNAL_MATH_ENTRY = make_match_external_math_entry(
    block_source_spans=block_source_spans,
    clean_text=CLEAN_TEXT,
)
OVERLAPPING_EXTERNAL_MATH_ENTRIES = make_overlapping_external_math_entries(
    overlapping_external_math_entries_impl=suppression_overlapping_external_math_entries,
    block_source_spans=block_source_spans,
)
TRIM_EMBEDDED_DISPLAY_MATH_FROM_PARAGRAPH = make_trim_embedded_display_math_from_paragraph(
    trim_embedded_display_math_from_paragraph_impl=suppression_trim_embedded_display_math_from_paragraph,
    block_source_spans=block_source_spans,
    clean_text=CLEAN_TEXT,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    display_math_resume_re=rsp.DISPLAY_MATH_RESUME_RE,
    display_math_start_re=rsp.DISPLAY_MATH_START_RE,
    mathish_ratio=MATHISH_RATIO,
    strong_operator_count=strong_operator_count,
)
LOOKS_LIKE_DISPLAY_MATH_ECHO = make_looks_like_display_math_echo(
    looks_like_display_math_echo_impl=suppression_looks_like_display_math_echo,
    block_source_spans=block_source_spans,
    clean_text=CLEAN_TEXT,
    mathish_ratio=MATHISH_RATIO,
    strong_operator_count=strong_operator_count,
    short_word_re=rsp.SHORT_WORD_RE,
)
MERGE_CODE_RECORDS = make_merge_code_records(
    block_source_spans=block_source_spans,
    clean_text=CLEAN_TEXT,
)
BUILD_BLOCKS_FOR_RECORD = make_build_blocks_for_record(
    clean_record=CLEAN_RECORD,
    record_analysis_text=RECORD_ANALYSIS_TEXT,
    is_short_ocr_fragment=IS_SHORT_OCR_FRAGMENT,
    block_source_spans=block_source_spans,
    caption_label=caption_label,
    default_review=default_review,
    make_reference_entry=MAKE_REFERENCE_ENTRY,
    looks_like_real_code_record=LOOKS_LIKE_REAL_CODE_RECORD,
    split_code_lines=split_code_lines,
    list_item_marker=LIST_ITEM_MARKER,
    normalize_paragraph_text=NORMALIZE_PARAGRAPH_TEXT,
    split_inline_math=split_inline_math,
    repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
    extract_general_inline_math_spans=extract_general_inline_math_spans,
    merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
    normalize_inline_math_spans=normalize_inline_math_spans,
    review_for_math_entry=review_for_math_entry,
    review_for_math_ref_block=review_for_math_ref_block,
    looks_like_prose_paragraph=looks_like_prose_paragraph,
    looks_like_prose_math_fragment=looks_like_prose_math_fragment,
    match_external_math_entry=MATCH_EXTERNAL_MATH_ENTRY,
    build_block_math_entry=build_block_math_entry,
    normalize_formula_display_text=NORMALIZE_FORMULA_DISPLAY_TEXT,
    classify_math_block=classify_math_block,
    review_for_algorithm_block_text=review_for_algorithm_block_text,
    overlapping_external_math_entries=OVERLAPPING_EXTERNAL_MATH_ENTRIES,
    trim_embedded_display_math_from_paragraph=TRIM_EMBEDDED_DISPLAY_MATH_FROM_PARAGRAPH,
    looks_like_display_math_echo=LOOKS_LIKE_DISPLAY_MATH_ECHO,
)


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
    return MERGE_CODE_RECORDS(records)


def _build_blocks_for_record(
    record: dict[str, object],
    layout_by_id: dict[str, object],
    figures_by_label: dict[str, dict[str, object]],
    external_math_by_page: dict[int, list[dict[str, object]]],
    external_math_overlap_by_page: dict[int, list[dict[str, object]]],
    references_section: bool,
    counters: dict[str, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    return BUILD_BLOCKS_FOR_RECORD(
        record,
        layout_by_id,
        figures_by_label,
        external_math_by_page,
        external_math_overlap_by_page,
        references_section,
        counters,
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
