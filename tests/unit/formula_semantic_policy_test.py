import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.math.semantic_policy import annotate_formula_classifications


class FormulaSemanticPolicyTest(unittest.TestCase):
    def test_inline_symbol_reference_is_graphic_only(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-inline-1",
                    "kind": "inline",
                    "display_latex": r"F(s,t)",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "symbolic_reference")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "graphic_only")
        self.assertEqual(classified[0]["classification"]["role"], "graphic")

    def test_inline_relation_is_semantic(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-inline-2",
                    "kind": "inline",
                    "display_latex": r"N_{z}=0",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "relation")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "semantic")
        self.assertEqual(classified[0]["classification"]["role"], "assertion")

    def test_display_matrix_is_structure_only(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-1",
                    "kind": "display",
                    "display_latex": r"C=\left[\begin{array}{cc} 0 & 1 \\ -M_{0} & -M_{1} \end{array}\right]",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "matrix_or_array")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "structure_only")
        self.assertEqual(classified[0]["classification"]["role"], "structural")

    def test_update_rule_is_semantic(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-2",
                    "kind": "display",
                    "display_latex": r"\text { Solve }(\mathbf{A}-s \mathbf{I}) \mathbf{z}_{k}=\mathbf{q}_{k-1} ; \quad \mathbf{q}_{k}=\mathbf{z}_{k} /\left\|\mathbf{z}_{k}\right\|_{\infty}",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "update_rule")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "semantic")
        self.assertEqual(classified[0]["classification"]["role"], "update_step")

    def test_definition_assignment_is_semantic_definition_not_update(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-definition-1",
                    "kind": "display",
                    "display_latex": r"E := M_{0} + M_{1}",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "relation")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "semantic")
        self.assertEqual(classified[0]["classification"]["role"], "definition")

    def test_mapping_definition_is_semantic_definition_not_update(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-definition-2",
                    "kind": "display",
                    "display_latex": r"\pi_y(x_1, x_2) := (x_1, y, x_2)",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "mapping")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "semantic")
        self.assertEqual(classified[0]["classification"]["role"], "definition")

    def test_display_bare_mapping_reference_is_graphic_only(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-mapping-ref-1",
                    "kind": "display",
                    "display_latex": r"\operatorname{hom} P(01)",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "symbolic_reference")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "graphic_only")
        self.assertEqual(classified[0]["classification"]["role"], "graphic")

    def test_group_defaults_to_derivation_chain(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-group-1",
                    "kind": "group",
                    "display_latex": "",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                    "items": [
                        {
                            "display_latex": r"A=B",
                            "compiled_targets": {},
                            "conversion": {"status": "unconverted", "notes": ""},
                            "semantic_expr": None,
                        },
                        {
                            "display_latex": r"B=C",
                            "compiled_targets": {},
                            "conversion": {"status": "unconverted", "notes": ""},
                            "semantic_expr": None,
                        },
                    ],
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "derivation_chain")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "structure_only")
        self.assertEqual(classified[0]["classification"]["role"], "derivation_step")
        self.assertEqual(classified[0]["items"][0]["classification"]["category"], "relation")

    def test_malformed_formula_is_graphic_only(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-3",
                    "kind": "display",
                    "display_latex": r"\phi_{1}(s,)=\frac{X(s, t)}{W(s, t}",
                    "compiled_targets": {},
                    "conversion": {"status": "failed", "notes": "latex2mathml: unexpected EOF"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "malformed_math")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "graphic_only")
        self.assertEqual(classified[0]["classification"]["role"], "graphic")

    def test_inline_complexity_class_is_notation_binding(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-inline-3",
                    "kind": "inline",
                    "display_latex": r"\mathbb{R}^{d}",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "complexity_or_class")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "structure_only")
        self.assertEqual(classified[0]["classification"]["role"], "notation_binding")

    def test_inline_set_membership_is_notation_binding(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-inline-4",
                    "kind": "inline",
                    "display_latex": r"c_{i} \in C",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "set_logic")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "structure_only")
        self.assertEqual(classified[0]["classification"]["role"], "notation_binding")

    def test_chained_equality_is_derivation_step_not_semantic_system(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-4",
                    "kind": "display",
                    "display_latex": r"K_{\mathrm{app}}=d K_{\mathrm{t}}=\frac{d K}{K_{\mathrm{r}}}",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertEqual(classified[0]["classification"]["category"], "system")
        self.assertEqual(classified[0]["classification"]["semantic_policy"], "structure_only")
        self.assertEqual(classified[0]["classification"]["role"], "derivation_step")

    def test_subscript_min_is_not_false_optimization(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-inline-5",
                    "kind": "inline",
                    "display_latex": r"u=u_{\min }=\frac{1}{6}",
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertNotEqual(classified[0]["classification"]["category"], "optimization")

    def test_z_zero_equation_is_not_false_update_rule(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-5",
                    "kind": "display",
                    "display_latex": r"a\left(x-x_{0}\right)+b\left(y-y_{0}\right)+c\left(z-z_{0}\right)=0",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertNotEqual(classified[0]["classification"]["category"], "update_rule")

    def test_set_logic_with_semicolon_is_not_false_update_rule(self) -> None:
        classified = annotate_formula_classifications(
            [
                {
                    "id": "math-display-6",
                    "kind": "display",
                    "display_latex": r"\{x \in X ; x > 0\}",
                    "compiled_targets": {},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "semantic_expr": None,
                    "source_spans": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ]
        )

        self.assertNotEqual(classified[0]["classification"]["category"], "update_rule")
        self.assertEqual(classified[0]["classification"]["category"], "set_logic")


if __name__ == "__main__":
    unittest.main()
