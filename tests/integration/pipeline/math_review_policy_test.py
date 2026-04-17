import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.math_review_policy import (
    review_for_algorithm_block_text,
    review_for_math_entry,
    review_for_math_ref_block,
)


class MathReviewPolicyTest(unittest.TestCase):
    def test_clean_external_formula_defaults_to_medium(self) -> None:
        entry = {
            "id": "mathpix-eq-1",
            "kind": "display",
            "display_latex": r"\frac{u-u_i}{u_{i+p}-u_i}",
            "source_spans": [{"page": 1, "bbox": {}, "engine": "mathpix"}],
            "review": {"status": "unreviewed", "risk": "high", "notes": ""},
        }

        self.assertEqual(review_for_math_entry(entry)["risk"], "medium")
        self.assertEqual(review_for_math_ref_block(entry)["risk"], "medium")

    def test_prose_contaminated_formula_stays_high(self) -> None:
        entry = {
            "id": "eq-1",
            "kind": "display",
            "display_latex": "Nonsingular parametrized surfaces: case n = 1 of II. Nonsingular surface of revolution with algebraic generating curve.",
            "source_spans": [{"page": 2, "bbox": {}, "engine": "mathpix"}],
            "review": {"status": "unreviewed", "risk": "high", "notes": ""},
        }

        self.assertEqual(review_for_math_entry(entry)["risk"], "high")
        self.assertEqual(review_for_math_ref_block(entry)["risk"], "high")

    def test_truncated_formula_stays_high(self) -> None:
        entry = {
            "id": "mathpix-eq-2",
            "kind": "display",
            "display_latex": r"\begin{equation*} f(x) = x^2 \tag{1.",
            "source_spans": [{"page": 3, "bbox": {}, "engine": "mathpix"}],
            "review": {"status": "unreviewed", "risk": "high", "notes": ""},
        }

        self.assertEqual(review_for_math_entry(entry)["risk"], "high")

    def test_formula_can_end_with_comma_without_becoming_high_risk(self) -> None:
        entry = {
            "id": "mathpix-eq-4",
            "kind": "display",
            "display_latex": r"\mathbf{n}(\mathbf{u})=\mathbf{t}_{u}(\mathbf{u}) \times \mathbf{t}_{v}(\mathbf{u}),",
            "source_spans": [{"page": 5, "bbox": {}, "engine": "mathpix"}],
            "review": {"status": "unreviewed", "risk": "high", "notes": ""},
        }

        self.assertEqual(review_for_math_entry(entry)["risk"], "medium")

    def test_manual_review_is_preserved(self) -> None:
        entry = {
            "id": "mathpix-eq-3",
            "kind": "display",
            "display_latex": r"\int_0^1 x^2\,dx",
            "source_spans": [{"page": 4, "bbox": {}, "engine": "mathpix"}],
            "review": {"status": "reviewed", "risk": "low", "notes": "checked against source PDF"},
        }

        self.assertEqual(review_for_math_entry(entry), entry["review"])

    def test_clean_algorithm_block_defaults_to_medium(self) -> None:
        text = "Algorithm for contraction of entity-based aspect graph EAG' to construct EAG' CONTRACT_EAG(EAG')"

        self.assertEqual(review_for_algorithm_block_text(text)["risk"], "medium")

    def test_empty_algorithm_block_stays_high(self) -> None:
        self.assertEqual(review_for_algorithm_block_text("")["risk"], "high")


if __name__ == "__main__":
    unittest.main()
