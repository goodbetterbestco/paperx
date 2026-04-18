import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.math.diagnostics import diagnose_formula_entry, summarize_formula_diagnostics


class FormulaDiagnosticsTest(unittest.TestCase):
    def test_clean_formula_has_no_diagnostics(self) -> None:
        entry = {
            "id": "math-1",
            "kind": "display",
            "display_latex": r"\frac{u-u_i}{u_{i+p}-u_i}",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)

        self.assertEqual(diagnostics, [])

    def test_converted_formula_with_division_and_negative_terms_is_not_flagged(self) -> None:
        entry = {
            "id": "math-1b",
            "kind": "display",
            "display_latex": r"\mathbf{q}_{k}=\mathbf{z}_{k} /\left\|\mathbf{z}_{k}\right\|_{\infty}",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)

        self.assertEqual(diagnostics, [])

    def test_braced_subscripts_are_not_false_spaced_subscript_diagnostics(self) -> None:
        entry = {
            "id": "math-1c",
            "kind": "display",
            "display_latex": r"F_{z z}(p) \neq 0",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertNotIn("spaced_subscript_token", codes)

    def test_converted_adjacent_identifier_formula_is_not_flagged_as_spaced_subscript(self) -> None:
        entry = {
            "id": "math-1d",
            "kind": "display",
            "display_latex": r"a x+b y+c=0",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertNotIn("spaced_subscript_token", codes)

    def test_nested_aligned_array_environment_is_not_false_mismatch(self) -> None:
        entry = {
            "id": "math-1e",
            "kind": "display",
            "display_latex": r"\begin{aligned} A &= \left(\begin{array}{cc} 1 & 0 \\ 0 & 1 \end{array}\right) \end{aligned}",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertNotIn("environment_mismatch", codes)

    def test_interval_notation_is_not_false_unbalanced_delimiter(self) -> None:
        entry = {
            "id": "math-1f",
            "kind": "inline",
            "display_latex": r"t \in [0.5,1)",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertNotIn("unbalanced_delimiters", codes)

    def test_left_right_interval_notation_is_not_false_unbalanced_delimiter(self) -> None:
        entry = {
            "id": "math-1g",
            "kind": "inline",
            "display_latex": r"\left[u_{i}, u_{i+1}\right)",
            "conversion": {"status": "converted", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertNotIn("unbalanced_delimiters", codes)

    def test_malformed_formula_reports_structural_diagnostics(self) -> None:
        entry = {
            "id": "math-2",
            "kind": "display",
            "display_latex": r"\phi_{1}(s,)=\frac{X(s, t)}{W(s, t}",
            "conversion": {"status": "failed", "notes": "latex2mathml: unexpected EOF"},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertIn("conversion_failed", codes)
        self.assertIn("unbalanced_delimiters", codes)
        self.assertIn("dangling_function_argument", codes)
        summary = summarize_formula_diagnostics(diagnostics)
        self.assertIn("formula conversion failed", summary)

    def test_ocr_style_formula_reports_spacing_and_punctuation_diagnostics(self) -> None:
        entry = {
            "id": "math-3",
            "kind": "display",
            "display_latex": "N z = 0 : : : + M i",
            "conversion": {"status": "source_only", "notes": ""},
        }

        diagnostics = diagnose_formula_entry(entry)
        codes = {diagnostic.code for diagnostic in diagnostics}

        self.assertIn("spaced_subscript_token", codes)
        self.assertIn("ocr_punctuation_noise", codes)


if __name__ == "__main__":
    unittest.main()
