from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.output.acquisition_benchmark_leaders import (
    append_leader_lines,
    capability_leader_map,
    family_leader_map,
    leader_value,
    metric_leader_summary_parts,
    render_labeled_leader_snapshot,
)


class AcquisitionBenchmarkOutputLeadersTest(unittest.TestCase):
    def test_leader_helpers_render_and_map_leaders(self) -> None:
        leaders = {
            "overall": {"provider": "docling", "avg_overall_score": 0.91},
            "content": {"provider": "docling", "avg_content_score": 0.92},
            "execution": {"provider": "mathpix", "avg_execution_score": 0.81},
            "capabilities": [
                {"capability": "layout", "leader": {"provider": "docling", "avg_score": 0.95}},
                {"capability": "math", "leader": {"provider": "mathpix", "score": 0.88}},
            ],
            "families": [
                {
                    "family": "math_dense",
                    "leaders": {
                        "overall": {"provider": "mathpix", "avg_overall_score": 0.89},
                        "capabilities": [
                            {"capability": "math", "leader": {"provider": "mathpix", "avg_score": 0.97}}
                        ],
                    },
                }
            ],
        }

        self.assertEqual(leader_value(leaders["overall"], "avg_overall_score", "overall"), 0.91)
        self.assertEqual(leader_value({"score": 0.7}, "avg_score", "score"), 0.7)
        self.assertEqual(metric_leader_summary_parts(leaders)[0], "overall `docling` at `0.91`")
        self.assertEqual(capability_leader_map(leaders)["layout"]["provider"], "docling")
        self.assertEqual(family_leader_map(leaders)["math_dense"]["overall"]["provider"], "mathpix")

        lines: list[str] = []
        append_leader_lines(lines, leaders, family_label="Family")
        rendered = "\n".join(lines)
        self.assertIn("- overall: `docling` at `0.91`", rendered)
        self.assertIn("- `math`: `mathpix` at `0.88`", rendered)
        self.assertIn("- Family `math_dense` overall leader: `mathpix` at `0.89`", rendered)

        snapshot = "\n".join(render_labeled_leader_snapshot("Candidate", leaders))
        self.assertIn("### Candidate", snapshot)
        self.assertIn("family `math_dense` capability `math` leader: `mathpix` at `0.97`", snapshot)


if __name__ == "__main__":
    unittest.main()
