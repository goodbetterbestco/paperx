from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.providers import build_provider_execution_plan, decide_mathpix_execution


class AcquisitionProviderPolicyTest(unittest.TestCase):
    def test_math_dense_route_requests_primary_mathpix(self) -> None:
        decision = decide_mathpix_execution(
            {
                "primary_route": "math_dense",
                "product_plan": {
                    "layout": ["docling"],
                    "math": ["mathpix", "docling"],
                },
            },
            mathpix_available=True,
        )

        self.assertTrue(decision.requested)
        self.assertTrue(decision.prefetch_eligible)

    def test_born_digital_route_skips_mathpix_when_docling_satisfies_math(self) -> None:
        decision = decide_mathpix_execution(
            {
                "primary_route": "born_digital_scholarly",
                "product_plan": {
                    "layout": ["docling"],
                    "math": ["docling", "mathpix"],
                },
            },
            docling_sources={
                "layout": {
                    "page_count": 1,
                    "blocks": [
                        {"id": "docling-1", "page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Title"},
                        {"id": "docling-2", "page": 1, "order": 2, "role": "heading", "text": "Abstract"},
                        {"id": "docling-3", "page": 1, "order": 3, "role": "paragraph", "text": "A coherent abstract paragraph."},
                        {"id": "docling-4", "page": 1, "order": 4, "role": "paragraph", "text": "1. Introduction"},
                    ],
                },
                "math": {"entries": [{"id": "eq-1", "kind": "display"}]},
            },
            mathpix_available=True,
        )

        self.assertFalse(decision.requested)

    def test_layout_route_requests_layout_fallback_when_docling_layout_is_rejected(self) -> None:
        decision = decide_mathpix_execution(
            {
                "primary_route": "layout_complex",
                "product_plan": {
                    "layout": ["docling", "mathpix"],
                    "math": ["docling"],
                },
            },
            docling_sources={
                "layout": {
                    "page_count": 1,
                    "blocks": [{"id": "docling", "page": 1, "order": 1, "role": "paragraph", "text": "Body"}],
                },
                "math": {"entries": [{"id": "eq-1", "kind": "display"}]},
            },
            mathpix_available=True,
        )

        self.assertTrue(decision.requested)


if __name__ == "__main__":
    unittest.main()
