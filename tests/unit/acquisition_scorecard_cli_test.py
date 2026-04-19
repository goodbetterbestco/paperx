from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.inspect_acquisition_scorecard import run_inspect_acquisition_scorecard


class AcquisitionScorecardCliTest(unittest.TestCase):
    def test_scorecard_cli_prints_provider_report(self) -> None:
        printed: list[str] = []
        exit_code = run_inspect_acquisition_scorecard(
            argparse.Namespace(paper_id="fixture"),
            current_layout_fn=lambda: object(),
            extract_layout_fn=lambda paper_id, *, layout=None: {"page_count": 1, "blocks": []},
            load_external_layout_fn=lambda paper_id, *, layout=None: None,
            load_mathpix_layout_fn=lambda paper_id, *, layout=None: None,
            load_external_math_fn=lambda paper_id, *, layout=None: None,
            build_source_scorecard_fn=lambda **kwargs: {
                "providers": [{"provider": "native_pdf", "overall_score": 0.5}],
                "recommended_primary_layout_provider": "native_pdf",
                "recommended_primary_math_provider": None,
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["paper_id"], "fixture")
        self.assertEqual(payload["recommended_primary_layout_provider"], "native_pdf")


if __name__ == "__main__":
    unittest.main()
