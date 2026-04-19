import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.math.extract import (
    classify_math_block,
    extract_general_inline_math_spans,
    looks_like_prose_math_fragment,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    split_inline_math,
)
from pipeline.types import LayoutBlock


class ExtractMathTest(unittest.TestCase):
    def test_split_inline_math_normalizes_tuple_separators(self) -> None:
        spans, entries, _ = split_inline_math("G(u) = (X(u) ;;Y(u) ;;Z(u) ;;W(u))", 1)
        spans = normalize_inline_math_spans(spans)

        self.assertEqual(entries[0]["display_latex"], "G(u)")
        self.assertEqual(entries[1]["display_latex"], "X(u)")
        self.assertEqual(entries[2]["display_latex"], "Y(u)")
        self.assertEqual(entries[3]["display_latex"], "Z(u)")
        self.assertEqual(entries[4]["display_latex"], "W(u)")
        text_spans = [span.get("text", "") for span in spans if span.get("kind") == "text"]
        self.assertEqual(text_spans, [" = (", ", ", ", ", ", ", ")"])

    def test_split_inline_math_preserves_mathpix_delimited_latex(self) -> None:
        spans, entries, _ = split_inline_math(
            r"Given a surface \( \mathbf{F}(s, t) \) and matrix \( \mathbf{M}(x, y, z, w) \).",
            1,
        )

        self.assertEqual(entries[0]["display_latex"], r"\mathbf{F}(s, t)")
        self.assertEqual(entries[1]["display_latex"], r"\mathbf{M}(x, y, z, w)")
        self.assertEqual(spans[0], {"kind": "text", "text": "Given a surface "})
        self.assertEqual(spans[-1], {"kind": "text", "text": "."})

    def test_split_inline_math_normalizes_spaced_subscripts_inside_delimited_latex(self) -> None:
        spans, entries, _ = split_inline_math(
            r"Regions \( K 2 \) and constraint \( N z = 0 \).",
            1,
        )

        self.assertEqual(entries[0]["display_latex"], r"K_{2}")
        self.assertEqual(entries[1]["display_latex"], r"N_{z}=0")
        self.assertEqual(spans[0], {"kind": "text", "text": "Regions "})
        self.assertEqual(spans[-1], {"kind": "text", "text": "."})

    def test_extract_general_inline_math_spans_recovers_relation_forms(self) -> None:
        spans, entries, _ = extract_general_inline_math_spans(
            [{"kind": "text", "text": "On the silhouette curve, N z = 0. Since W ( s;; t ) > 0, we continue."}],
            [],
            1,
        )

        self.assertEqual(entries[0]["display_latex"], r"N_{z}=0")
        self.assertEqual(entries[1]["display_latex"], r"W(s,t)>0")
        text_spans = [span.get("text", "") for span in spans if span.get("kind") == "text"]
        self.assertEqual(text_spans, ["On the silhouette curve, ", ". Since ", ", we continue."])

    def test_merge_inline_math_relation_suffixes_extends_existing_inline_entry(self) -> None:
        spans, entries, _ = split_inline_math("Since W(s,t) > 0, we continue.", 1)

        merged_spans, merged_entries = merge_inline_math_relation_suffixes(spans, entries)
        merged_spans = normalize_inline_math_spans(merged_spans)

        self.assertEqual(merged_entries[0]["display_latex"], r"W(s,t)>0")
        self.assertEqual(
            merged_spans,
            [
                {"kind": "text", "text": "Since "},
                {"kind": "inline_math_ref", "target_id": "math-inline-1"},
                {"kind": "text", "text": ", we continue."},
            ],
        )

    def test_extract_general_inline_math_spans_recovers_contextual_point_labels(self) -> None:
        spans, entries, _ = extract_general_inline_math_spans(
            [{"kind": "text", "text": "The curve b 2 meets point p 1 near region K 2."}],
            [],
            1,
        )

        self.assertEqual(
            [entry["display_latex"] for entry in entries],
            [r"b_{2}", r"p_{1}", r"K_{2}"],
        )
        text_spans = [span.get("text", "") for span in spans if span.get("kind") == "text"]
        self.assertEqual(text_spans, ["The curve ", " meets point ", " near region ", "."])

    def test_algorithm_heading_line_is_classified_as_algorithm(self) -> None:
        block = LayoutBlock(
            id="algorithm-heading",
            page=7,
            order=1,
            text="Algorithm for contraction of entity-based aspect graph EAG' to construct EAG' (where E' CE) CONTRACT_EAG(EAG')",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 0.0, "x1": 100.0, "y1": 10.0, "width": 100.0, "height": 10.0},
        )

        self.assertEqual(classify_math_block(block), "algorithm")

    def test_viewing_domain_assignment_line_is_classified_as_algorithm(self) -> None:
        block = LayoutBlock(
            id="algorithm-assignment",
            page=7,
            order=2,
            text="The viewing domain formed by V* = V; - Vi nV has a list of observable entities Ovi=",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 10.0, "x1": 100.0, "y1": 20.0, "width": 100.0, "height": 10.0},
        )

        self.assertEqual(classify_math_block(block), "algorithm")

    def test_sentence_fragment_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="prose-fragment",
            page=3,
            order=10,
            text="In view of the above, we define an open disk A = Int(M),",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 0.0, "x1": 200.0, "y1": 20.0, "width": 200.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_lowercase_sentence_fragment_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="prose-fragment-lower",
            page=7,
            order=11,
            text="is a closed disk with boundary. Obviously, Int(D) = N. This proves the claim.",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 20.0, "x1": 240.0, "y1": 40.0, "width": 240.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_assumption_sentence_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="assumption-fragment",
            page=11,
            order=21,
            text="We also assume that π y (0 , 0) = (0 , 0).",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 40.0, "x1": 220.0, "y1": 60.0, "width": 220.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_remark_sentence_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="remark-fragment",
            page=29,
            order=31,
            text="Remark 4.5. Suppose that f (0) is not red subparabolic, that is, a 21 = 0.",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 60.0, "x1": 260.0, "y1": 80.0, "width": 260.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_condition_statement_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="condition-fragment",
            page=28,
            order=27,
            text="The vertex y is contained in the asymptotic straight line of S at x = 0 and",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 80.0, "x1": 280.0, "y1": 100.0, "width": 280.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_leading_glyph_noise_before_assumption_stays_prose(self) -> None:
        block = LayoutBlock(
            id="glyph-assumption-fragment",
            page=11,
            order=41,
            text="glyph[negationslash] glyph[negationslash] glyph[negationslash] We also assume that π y (0 , 0) = (0 , 0).",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 100.0, "x1": 320.0, "y1": 120.0, "width": 320.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_when_clause_with_single_equality_stays_prose(self) -> None:
        block = LayoutBlock(
            id="when-fragment",
            page=19,
            order=51,
            text="When a = 1.5E 6 , ambiguities are created, after r is increased to 3E 3, they are detected coincident.",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 120.0, "x1": 360.0, "y1": 140.0, "width": 360.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_proof_line_with_prose_content_stays_prose(self) -> None:
        block = LayoutBlock(
            id="proof-fragment",
            page=7,
            order=61,
            text="Proof. Lift the three punctured disks of Lemma 1 to distinct heights in R 3 . intersectionsq unionsq",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 140.0, "x1": 360.0, "y1": 160.0, "width": 360.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_satisfy_for_all_fragment_stays_prose(self) -> None:
        block = LayoutBlock(
            id="satisfy-fragment",
            page=7,
            order=71,
            text="satisfy triangle 1 ∩ triangle 2 = ∅ for all triangle 1 ∈ M 1 and triangle 2 ∈ M 2 .",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 160.0, "x1": 360.0, "y1": 180.0, "width": 360.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))

    def test_sentence_about_equations_and_variables_stays_prose(self) -> None:
        block = LayoutBlock(
            id="equations-variables-fragment",
            page=13,
            order=81,
            text="This is a system of five equations in the six variables Xi, Yi, Zi, i = 1,2.",
            role="paragraph",
            bbox={"x0": 0.0, "y0": 180.0, "x1": 360.0, "y1": 200.0, "width": 360.0, "height": 20.0},
        )

        self.assertTrue(looks_like_prose_math_fragment(block.text))
        self.assertIsNone(classify_math_block(block))


if __name__ == "__main__":
    unittest.main()
