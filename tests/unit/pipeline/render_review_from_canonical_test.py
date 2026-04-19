import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.output.review_renderer import render_document


class RenderReviewFromCanonicalTest(unittest.TestCase):
    def test_inline_math_renders_with_explicit_math_delimiters(self) -> None:
        document = {
            "title": "Inline Math",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Intro",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {"kind": "text", "text": "The cost is "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-1"},
                            {"kind": "text", "text": " for the full pass."},
                        ]
                    },
                }
            ],
            "math": [
                {
                    "id": "math-inline-1",
                    "kind": "inline",
                    "display_latex": r"O(N \log N)",
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn(r"\(O(N \log N)\)", review)
        self.assertNotIn("$O(N \\log N)$", review)

    def test_display_formula_renders_as_typora_friendly_math_block(self) -> None:
        document = {
            "title": "Test Paper",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Method",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                }
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"x^2 + y^2 = 1",
                    "equation_number": "(1)",
                    "conversion": {"status": "converted"},
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("$$\nx^2 + y^2 = 1\n$$", review)
        self.assertNotIn("```latex", review)
        self.assertNotIn("Formula math-1", review)

    def test_imperative_list_like_paragraph_renders_as_bullets(self) -> None:
        document = {
            "title": "List Recovery",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Method",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": (
                                    "Decompose the polygon into trapezoids in "
                                    r"\(O(N \log N)\) time, "
                                    "Decompose the trapezoids into monotone polygons in linear time, "
                                    "and Triangulate the monotone polygons in linear time. "
                                    "The triangulation is later reused for rendering."
                                ),
                            }
                        ]
                    },
                }
            ],
            "math": [],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("- Decompose the polygon into trapezoids in \\(O(N \\log N)\\) time", review)
        self.assertIn("- Decompose the trapezoids into monotone polygons in linear time", review)
        self.assertIn("- Triangulate the monotone polygons in linear time", review)
        self.assertIn("The triangulation is later reused for rendering.", review)

    def test_list_item_block_renders_with_inline_math(self) -> None:
        document = {
            "title": "Structured List",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Method",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "list_item",
                    "content": {
                        "spans": [
                            {"kind": "text", "text": "Decompose in "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-1"},
                            {"kind": "text", "text": " time"},
                        ],
                        "marker": None,
                        "ordered": False,
                        "depth": 1,
                    },
                    "source_spans": [],
                    "alternates": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ],
            "math": [
                {
                    "id": "math-inline-1",
                    "kind": "inline",
                    "display_latex": r"O(N \log N)",
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn(r"- Decompose in \(O(N \log N)\) time", review)

    def test_code_block_renders_from_structured_code_block(self) -> None:
        document = {
            "title": "Structured Code",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Algorithm",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "code",
                    "content": {"lines": ["if (x)", "push(q);"], "language": "text"},
                    "source_spans": [],
                    "alternates": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ],
            "math": [],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("```text\nif (x)\npush(q);\n```", review)

    def test_numbered_case_paragraph_renders_as_subheading_not_markdown_list_item(self) -> None:
        document = {
            "title": "Case Recovery",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Boundary Intersections",
                    "level": 1,
                    "block_ids": ["blk-1", "blk-2"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": (
                                    "1. intersection between two boundary curves: "
                                    "Let f and g be two plane curves parametrized by u and v respectively."
                                ),
                            }
                        ]
                    },
                },
                {
                    "id": "blk-2",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"\frac{X(u)}{W(u)} = \frac{X(v)}{W(v)}",
                    "conversion": {"status": "converted"},
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("### 1. intersection between two boundary curves", review)
        self.assertNotIn("\n1. intersection between two boundary curves:", review)
        self.assertIn("$$\n\\frac{X(u)}{W(u)} = \\frac{X(v)}{W(v)}\n$$", review)

    def test_codeish_paragraph_renders_lead_lines_as_code_block(self) -> None:
        document = {
            "title": "Code Recovery",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Algorithm",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": (
                                    "if (q.type = p.type) push(q);; "
                                    "if ((q.rank p.rank == 1) && (q.in or out == out) && (p.in or out == in)) pop(p);; "
                                    "if ((p.rank q.rank == 1) && (p.in or out == out) && (q.in or out == in)) pop(p);; "
                                    "push(q);; "
                                    "If p is popped, then p and q form a partition of the polygon."
                                ),
                            }
                        ]
                    },
                }
            ],
            "math": [],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("```text", review)
        self.assertIn("if (q.type = p.type) push(q)", review)
        self.assertIn("push(q)", review)
        self.assertIn("If p is popped, then p and q form a partition of the polygon.", review)

    def test_codeish_paragraph_with_inline_math_renders_as_code_block_using_plain_formula_text(self) -> None:
        document = {
            "title": "Pseudo Code",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Visibility",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {"kind": "text", "text": "Q = ;; for each face "},
                            {"kind": "inline_math_ref", "target_id": "math-inline-1"},
                            {"kind": "text", "text": " do ;; output V n ;;"},
                        ]
                    },
                }
            ],
            "math": [
                {
                    "id": "math-inline-1",
                    "kind": "inline",
                    "display_latex": r"f \in V",
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("```text", review)
        self.assertIn("for each face f \\in V do", review)
        self.assertNotIn(r"\(f \in V\)", review)

    def test_algorithm_block_repairs_comment_lines(self) -> None:
        document = {
            "title": "Struct",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Tracing",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "algorithm",
                    "content": {
                        "lines": [
                            "struct start point f double xval, yval;;",
                            "* x and y value of intersection point * double dom point 1 u, dom point 1 v;;",
                            "* index of the second point in the polygonal region * g",
                        ]
                    },
                }
            ],
            "math": [],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertIn("struct start_point {", review)
        self.assertIn("/* x and y value of intersection point */", review)
        self.assertIn("double dom_point_1_u, dom_point_1_v;", review)
        self.assertIn("}", review)

    def test_equation_group_renders_each_item_as_its_own_math_block(self) -> None:
        document = {
            "title": "Grouped Math",
            "sections": [
                {
                    "id": "sec-1",
                    "title": "Results",
                    "level": 1,
                    "block_ids": ["blk-1"],
                    "children": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-1",
                    "type": "equation_group_ref",
                    "content": {"math_id": "math-group-1"},
                }
            ],
            "math": [
                {
                    "id": "math-group-1",
                    "kind": "group",
                    "conversion": {"status": "partial"},
                    "items": [
                        {"display_latex": r"a=b"},
                        {"display_latex": r"c=d"},
                    ],
                }
            ],
            "figures": [],
            "references": [],
            "front_matter": {},
        }

        review = render_document(document)

        self.assertEqual(review.count("$$"), 4)
        self.assertIn("$$\na=b\n$$", review)
        self.assertIn("$$\nc=d\n$$", review)


if __name__ == "__main__":
    unittest.main()
