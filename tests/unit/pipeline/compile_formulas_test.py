import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.math.compile import compile_formulas


class CompileFormulasTest(unittest.TestCase):
    def test_display_formula_stays_unconverted_when_backend_is_unavailable(self) -> None:
        with patch(
            "pipeline.math.compile.compile_latex_targets",
            return_value=({}, {"status": "unconverted", "notes": "latex2mathml unavailable"}),
        ):
            compiled = compile_formulas(
                [
                    {
                        "id": "math-1",
                        "kind": "display",
                        "display_latex": r"\frac{u-u_i}{u_{i+p}-u_i}",
                    }
                ]
            )

        self.assertEqual(compiled[0]["compiled_targets"], {})
        self.assertEqual(compiled[0]["conversion"]["status"], "unconverted")

    def test_display_formula_compiles_to_mathml_when_backend_is_available(self) -> None:
        with patch(
            "pipeline.math.compile.compile_latex_targets",
            return_value=({"mathml": "<math><mi>x</mi></math>"}, {"status": "converted", "notes": "backend=test"}),
        ):
            compiled = compile_formulas(
                [
                    {
                        "id": "math-1",
                        "kind": "display",
                        "display_latex": "x",
                    }
                ]
            )

        self.assertEqual(compiled[0]["compiled_targets"]["mathml"], "<math><mi>x</mi></math>")
        self.assertEqual(compiled[0]["conversion"]["status"], "converted")

    def test_group_formula_summarizes_item_conversion(self) -> None:
        responses = [
            ({"mathml": "<math><mi>a</mi></math>"}, {"status": "converted", "notes": "backend=test"}),
            ({}, {"status": "failed", "notes": "backend=test: parse error"}),
        ]

        with patch("pipeline.math.compile.compile_latex_targets", side_effect=responses):
            compiled = compile_formulas(
                [
                    {
                        "id": "math-group-1",
                        "kind": "group",
                        "display_latex": "a b",
                        "items": [
                            {"display_latex": "a"},
                            {"display_latex": "b"},
                        ],
                    }
                ]
            )

        group = compiled[0]
        self.assertEqual(group["conversion"]["status"], "partial")
        self.assertEqual(group["items"][0]["conversion"]["status"], "converted")
        self.assertEqual(group["items"][1]["conversion"]["status"], "failed")
        self.assertEqual(group["compiled_targets"]["mathml_items"][0], "<math><mi>a</mi></math>")


if __name__ == "__main__":
    unittest.main()
