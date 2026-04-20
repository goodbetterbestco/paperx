from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.output.acquisition_benchmark_deltas import (
    append_named_provider_delta_lines,
    append_named_score_delta_lines,
    append_provider_delta_lines,
    append_score_delta_lines,
    render_delta_section,
)


class AcquisitionBenchmarkOutputDeltasTest(unittest.TestCase):
    def test_delta_helpers_render_provider_and_score_sections(self) -> None:
        provider_rows = [
            {"provider": "docling", "overall_delta": 0.1, "content_delta": 0.2, "execution_delta": -0.1}
        ]
        score_rows = [{"provider": "mathpix", "score_delta": -0.05}]

        provider_lines: list[str] = []
        append_provider_delta_lines(provider_lines, provider_rows)
        self.assertEqual(
            provider_lines[0],
            "- `docling`: overall delta `0.1`, content delta `0.2`, execution delta `-0.1`",
        )

        score_lines: list[str] = []
        append_score_delta_lines(score_lines, score_rows)
        self.assertEqual(score_lines[0], "- `mathpix`: score delta `-0.05`")

        named_provider_lines: list[str] = []
        append_named_provider_delta_lines(named_provider_lines, provider_rows, label="improvement")
        self.assertEqual(
            named_provider_lines[0],
            "- improvement `docling`: overall delta `0.1`, content delta `0.2`, execution delta `-0.1`",
        )

        named_score_lines: list[str] = []
        append_named_score_delta_lines(named_score_lines, score_rows, label="regression")
        self.assertEqual(named_score_lines[0], "- regression `mathpix`: score delta `-0.05`")

        provider_section = render_delta_section("## Top Improvements", provider_rows)
        self.assertIn("## Top Improvements", "\n".join(provider_section))
        self.assertIn("`docling`", "\n".join(provider_section))

        empty_section = render_delta_section("## Top Regressions", [], kind="score")
        self.assertEqual(empty_section[2], "- none")


if __name__ == "__main__":
    unittest.main()
