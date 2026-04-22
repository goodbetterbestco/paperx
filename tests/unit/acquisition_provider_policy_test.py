from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.providers import decide_mathpix_execution


class AcquisitionProviderPolicyTest(unittest.TestCase):
    def test_math_heavy_priority_requests_primary_mathpix(self) -> None:
        decision = decide_mathpix_execution(
            {
                "layout_priority": ["docling"],
                "math_priority": ["mathpix", "docling"],
            },
            mathpix_available=True,
        )

        self.assertTrue(decision.requested)
        self.assertEqual(decision.reason, "route_requests_mathpix")

    def test_born_digital_route_skips_mathpix_when_docling_is_primary(self) -> None:
        decision = decide_mathpix_execution(
            {
                "layout_priority": ["docling"],
                "math_priority": ["docling", "mathpix"],
            },
            mathpix_available=True,
        )

        self.assertFalse(decision.requested)
        self.assertEqual(decision.reason, "route_prefers_docling")

    def test_route_request_is_disabled_when_mathpix_is_unavailable(self) -> None:
        decision = decide_mathpix_execution(
            {
                "layout_priority": ["mathpix", "docling"],
                "math_priority": ["docling", "mathpix"],
            },
            mathpix_available=False,
        )

        self.assertFalse(decision.requested)
        self.assertEqual(decision.reason, "mathpix_unavailable")


if __name__ == "__main__":
    unittest.main()
