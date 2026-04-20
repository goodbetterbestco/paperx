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
        self.assertEqual(decision.phase, "primary")
        self.assertTrue(decision.prefetch_eligible)
        self.assertEqual(decision.reason, "route_requested_primary_mathpix")

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
        self.assertEqual(decision.phase, "skip")
        self.assertEqual(decision.reason, "route_sufficient_without_mathpix")

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
        self.assertEqual(decision.phase, "fallback")
        self.assertEqual(decision.reason, "layout_fallback_docling_rejected")

    def test_execution_plan_keeps_ocr_then_docling_then_mathpix_order(self) -> None:
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

        plan = build_provider_execution_plan(
            {
                "primary_route": "math_dense",
                "ocr_prepass": {"policy": "required", "should_run": True, "tool": "ocrmypdf"},
            },
            mathpix_decision=decision,
            mathpix_strategy="prefetched_primary",
            ocr_prepass_applied=True,
        )

        self.assertEqual(plan["provider_order"], ["ocrmypdf", "docling", "mathpix"])
        self.assertTrue(plan["mathpix_requested"])
        self.assertTrue(plan["mathpix_prefetch_eligible"])
        self.assertEqual(plan["mathpix_reason"], "route_requested_primary_mathpix")


if __name__ == "__main__":
    unittest.main()
