import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.formula_semantic_ir import annotate_formula_semantic_expr


class FormulaSemanticIrTest(unittest.TestCase):
    def test_relation_formula_gets_relation_ir(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"M(u)=u^d M_d + M_0",
                    "classification": {
                        "category": "mapping",
                        "semantic_policy": "semantic",
                        "role": "assertion",
                        "confidence": "medium",
                        "signals": ["mapping_tokens"],
                    },
                }
            ]
        )

        semantic_expr = annotated[0]["semantic_expr"]
        self.assertEqual(semantic_expr["schema_version"], "formula_semantic_expr/v1")
        self.assertEqual(semantic_expr["category"], "mapping")
        self.assertEqual(semantic_expr["role"], "assertion")
        self.assertEqual(semantic_expr["mapping"]["head"], "M")
        self.assertEqual(semantic_expr["mapping"]["arguments"], ["u"])
        self.assertEqual(semantic_expr["relations"][0]["operator"], "eq")

    def test_update_rule_formula_gets_step_ir(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-2",
                    "kind": "display",
                    "display_latex": r"\text { Solve }(\mathbf{A}-s \mathbf{I}) \mathbf{z}_{k}=\mathbf{q}_{k-1} ; \quad \mathbf{q}_{k}=\mathbf{z}_{k} /\left\|\mathbf{z}_{k}\right\|_{\infty} ;",
                    "classification": {
                        "category": "update_rule",
                        "semantic_policy": "semantic",
                        "role": "update_step",
                        "confidence": "high",
                        "signals": ["update_rule_tokens"],
                    },
                }
            ]
        )

        steps = annotated[0]["semantic_expr"]["steps"]
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["action"], "solve")
        self.assertEqual(steps[0]["relation"]["operator"], "eq")
        self.assertNotIn("Solve", annotated[0]["semantic_expr"]["symbols"])

    def test_definition_formula_preserves_definition_role_in_ir(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-definition-1",
                    "kind": "display",
                    "display_latex": r"\pi_y(x_1, x_2) := (x_1, y, x_2)",
                    "classification": {
                        "category": "mapping",
                        "semantic_policy": "semantic",
                        "role": "definition",
                        "confidence": "high",
                        "signals": ["definition_tokens"],
                    },
                }
            ]
        )

        semantic_expr = annotated[0]["semantic_expr"]
        self.assertEqual(semantic_expr["category"], "mapping")
        self.assertEqual(semantic_expr["role"], "definition")
        self.assertEqual(semantic_expr["mapping"]["head"], "pi_y")
        self.assertEqual(semantic_expr["mapping"]["arguments"], ["x_1", "x_2"])
        self.assertEqual(semantic_expr["relations"][0]["operator"], "assign")

    def test_graphic_only_formula_keeps_null_semantic_expr(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-3",
                    "kind": "inline",
                    "display_latex": r"K_2",
                    "classification": {
                        "category": "symbolic_reference",
                        "semantic_policy": "graphic_only",
                        "role": "graphic",
                        "confidence": "high",
                        "signals": ["inline_symbol_reference"],
                    },
                }
            ]
        )

        self.assertIsNone(annotated[0]["semantic_expr"])

    def test_group_items_can_carry_semantic_ir_when_parent_is_structure_only(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-group-1",
                    "kind": "group",
                    "display_latex": r"x = y \\ y = z",
                    "classification": {
                        "category": "derivation_chain",
                        "semantic_policy": "structure_only",
                        "role": "derivation_step",
                        "confidence": "high",
                        "signals": ["group_kind"],
                    },
                    "items": [
                        {
                            "display_latex": r"x = y",
                            "classification": {
                                "category": "relation",
                                "semantic_policy": "semantic",
                                "role": "assertion",
                                "confidence": "medium",
                                "signals": ["single_relation"],
                            },
                        }
                    ],
                }
            ]
        )

        self.assertIsNone(annotated[0]["semantic_expr"])
        self.assertEqual(annotated[0]["items"][0]["semantic_expr"]["category"], "relation")

    def test_complexity_formula_collects_notations(self) -> None:
        annotated = annotate_formula_semantic_expr(
            [
                {
                    "id": "math-4",
                    "kind": "inline",
                    "display_latex": r"O(N \log N) \text{ and } C^{1}",
                    "classification": {
                        "category": "complexity_or_class",
                        "semantic_policy": "semantic",
                        "role": "assertion",
                        "confidence": "high",
                        "signals": ["complexity_or_class_tokens"],
                    },
                }
            ]
        )

        notations = annotated[0]["semantic_expr"]["notations"]
        self.assertEqual(len(notations), 2)
        self.assertEqual(notations[0]["kind"], "big_o")


if __name__ == "__main__":
    unittest.main()
