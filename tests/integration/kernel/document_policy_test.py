import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.document_policy import apply_document_policy


class DocumentPolicyTest(unittest.TestCase):
    def test_hidden_surface_policy_repairs_known_problem_blocks(self) -> None:
        document = {
            "paper_id": "1990_hidden_curve_removal_for_free_form_surfaces",
            "front_matter": {
                "abstract_block_id": "blk-front-abstract-1",
                "affiliations": [
                    {
                        "id": "aff-1",
                        "department": "Department of Computer Science",
                        "institution": "University of North Carolina",
                        "address": "Chapel Hill, NC 2 7 5 9 9- 3 1 7 5",
                    }
                ]
            },
            "blocks": [
                {
                    "id": "blk-front-abstract-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": 'We introduce a notion of \\visibility curves" obtained by projection.',
                            }
                        ]
                    },
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {"kind": "text", "text": r"\begin{gathered} \mathbf{F}(s, t)=\langle "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-a"},
                            {"kind": "text", "text": r", "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-b"},
                            {"kind": "text", "text": r", "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-c"},
                            {"kind": "text", "text": r", "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-d"},
                            {"kind": "text", "text": r"\rangle \\ \phi_{1}(s,)=\frac{"},
                            {"kind": "inline_math_ref", "target_id": "math-inline-e"},
                            {"kind": "text", "text": r"}{"},
                            {"kind": "inline_math_ref", "target_id": "math-inline-f"},
                            {"kind": "text", "text": r"} \end{gathered}"},
                        ]
                    },
                    "source_spans": [{"page": 8, "bbox": {"x0": 1, "y0": 2, "x1": 3, "y1": 4}}],
                },
                {
                    "id": "blk-code-1",
                    "type": "code",
                    "content": {"lines": ["if ( q .type = p .type) push( q )"], "language": "text"},
                },
                {
                    "id": "blk-code-2",
                    "type": "code",
                    "content": {"lines": ["struct start point f double xval, yval"], "language": "text"},
                },
                {
                    "id": "blk-code-3",
                    "type": "code",
                    "content": {"lines": ["Q ="], "language": "text"},
                },
                {
                    "id": "blk-list-1",
                    "type": "list_item",
                    "content": {"spans": [{"kind": "text", "text": "(h u ;;h v) goes out of the region, or"}], "marker": None, "ordered": False, "depth": 1},
                },
                {
                    "id": "blk-list-2",
                    "type": "list_item",
                    "content": {"spans": [{"kind": "text", "text": "(h u ;;h v) = (g u ;; g v)."}], "marker": None, "ordered": False, "depth": 1},
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {"kind": "text", "text": "The input to the algorithm is a set of "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-292"},
                            {"kind": "text", "text": " faces. Let "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-294"},
                            {"kind": "text", "text": " denote the collection of with the face "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-295"},
                        ]
                    },
                },
            ],
            "math": [
                {"id": "math-inline-a", "kind": "inline", "display_latex": "X(s,t)"},
                {"id": "math-inline-b", "kind": "inline", "display_latex": "Y(s,t)"},
                {"id": "math-inline-c", "kind": "inline", "display_latex": "Z(s,t)"},
                {"id": "math-inline-d", "kind": "inline", "display_latex": "W(s,t)"},
                {"id": "math-inline-e", "kind": "inline", "display_latex": "X(s,t)"},
                {"id": "math-inline-f", "kind": "inline", "display_latex": "W(s,t)"},
                {"id": "math-inline-292", "kind": "inline", "display_latex": "n"},
                {"id": "math-inline-293", "kind": "inline", "display_latex": "H=\\{h_1,\\ldots,h_n\\}"},
                {"id": "math-inline-294", "kind": "inline", "display_latex": "V^i"},
                {"id": "math-inline-295", "kind": "inline", "display_latex": "h_{i+1}"},
                {"id": "math-inline-296", "kind": "inline", "display_latex": "p,q"},
                {"id": "math-inline-297", "kind": "inline", "display_latex": "p"},
                {"id": "math-inline-298", "kind": "inline", "display_latex": "V^i"},
                {"id": "math-inline-299", "kind": "inline", "display_latex": "q"},
                {"id": "math-inline-300", "kind": "inline", "display_latex": "h_{i+1}"},
                {"id": "math-inline-301", "kind": "inline", "display_latex": "z"},
                {"id": "math-inline-302", "kind": "inline", "display_latex": "p"},
                {"id": "math-inline-303", "kind": "inline", "display_latex": "q"},
                {"id": "math-inline-304", "kind": "inline", "display_latex": "p"},
                {"id": "math-inline-305", "kind": "inline", "display_latex": "q"},
                {"id": "math-inline-306", "kind": "inline", "display_latex": "p"},
                {"id": "math-inline-307", "kind": "inline", "display_latex": "h_{i+1}"},
                {"id": "math-inline-308", "kind": "inline", "display_latex": "r"},
                {"id": "math-inline-309", "kind": "inline", "display_latex": "r"},
                {"id": "math-inline-310", "kind": "inline", "display_latex": "-\\infty"},
                {"id": "math-inline-311", "kind": "inline", "display_latex": "z"},
                {"id": "math-inline-312", "kind": "inline", "display_latex": "V^i \\cup \\{h_{i+1}\\}"},
                {"id": "math-inline-313", "kind": "inline", "display_latex": "i+1"},
                {"id": "math-inline-314", "kind": "inline", "display_latex": "V^{i+1}"},
                {"id": "math-inline-315", "kind": "inline", "display_latex": "n"},
                {"id": "math-inline-316", "kind": "inline", "display_latex": "V^n"},
            ],
            "figures": [
                {
                    "id": "fig-4",
                    "bbox": {"x0": 74.82, "y0": 99.35, "x1": 435.69, "y1": 236.41, "width": 360.87, "height": 137.06},
                    "display_size_in": {"width": 5.0121, "height": 1.9036},
                }
            ],
        }

        repaired = apply_document_policy(document)

        self.assertEqual(repaired["front_matter"]["affiliations"][0]["address"], "Chapel Hill, NC 27599-3175")
        self.assertEqual(
            repaired["blocks"][0]["content"]["spans"][0]["text"],
            "We introduce a notion of visibility curves obtained by projection.",
        )
        repaired_block = repaired["blocks"][1]
        self.assertEqual(repaired_block["type"], "display_equation_ref")
        self.assertEqual(repaired_block["content"]["math_id"], "paper-policy-eq-1990-3-1-mapping")
        self.assertTrue(any(entry["id"] == "paper-policy-eq-1990-3-1-mapping" for entry in repaired["math"]))
        self.assertFalse(any(entry["id"] == "math-inline-a" for entry in repaired["math"]))
        self.assertEqual(repaired["blocks"][2]["content"]["lines"][0], "if (q.type == p.type) push(q);")
        self.assertEqual(repaired["blocks"][3]["content"]["lines"][0], "struct start_point {")
        self.assertEqual(repaired["blocks"][4]["content"]["lines"][0], "Q = {};")
        self.assertEqual(repaired["blocks"][5]["content"]["spans"][0]["target_id"], "paper-policy-inline-1990-hu-hv")
        paragraph_text = " ".join(
            span["text"]
            for span in repaired["blocks"][7]["content"]["spans"]
            if span.get("kind") == "text"
        )
        self.assertIn("visible regions after adding i faces at random", paragraph_text)
        self.assertTrue(
            any(
                span.get("kind") == "inline_math_ref"
                and span.get("target_id") == "paper-policy-inline-1990-h-minus-q"
                for span in repaired["blocks"][7]["content"]["spans"]
            )
        )
        self.assertEqual(repaired["figures"][0]["bbox"]["x0"], 14.82)


if __name__ == "__main__":
    unittest.main()
