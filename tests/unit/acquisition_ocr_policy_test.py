from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.ocr_policy import decide_ocr_prepass_policy
from pipeline.acquisition.routing import AcquisitionSignals


def _signals(
    *,
    text_page_ratio: float,
    avg_text_chars_per_page: float,
    avg_image_coverage: float,
    max_image_coverage: float,
) -> AcquisitionSignals:
    return AcquisitionSignals(
        page_count=4,
        text_page_ratio=text_page_ratio,
        avg_text_chars_per_page=avg_text_chars_per_page,
        avg_image_coverage=avg_image_coverage,
        max_image_coverage=max_image_coverage,
        avg_text_block_count=2.0,
        max_text_block_count=4,
        two_column_ratio=0.0,
        math_token_density=0.0,
        reference_marker_density=0.0,
    )


class AcquisitionOcrPolicyTest(unittest.TestCase):
    def test_scan_route_requires_ocr_prepass(self) -> None:
        decision = decide_ocr_prepass_policy(
            "scan_or_image_heavy",
            signals=_signals(
                text_page_ratio=0.25,
                avg_text_chars_per_page=80.0,
                avg_image_coverage=0.6,
                max_image_coverage=0.95,
            ),
        )

        self.assertTrue(decision.should_run)
        self.assertEqual(decision.policy, "required")
        self.assertEqual(decision.tool, "ocrmypdf")
        self.assertIn("low_text_page_ratio", decision.trigger_signals)

    def test_degraded_route_recommends_ocr_prepass(self) -> None:
        decision = decide_ocr_prepass_policy(
            "degraded_or_garbled",
            signals=_signals(
                text_page_ratio=0.8,
                avg_text_chars_per_page=320.0,
                avg_image_coverage=0.2,
                max_image_coverage=0.32,
            ),
        )

        self.assertTrue(decision.should_run)
        self.assertEqual(decision.policy, "recommended")
        self.assertEqual(decision.output_pdf_kind, "searchable_pdf")

    def test_born_digital_route_skips_ocr_prepass(self) -> None:
        decision = decide_ocr_prepass_policy(
            "born_digital_scholarly",
            signals=_signals(
                text_page_ratio=1.0,
                avg_text_chars_per_page=2200.0,
                avg_image_coverage=0.02,
                max_image_coverage=0.08,
            ),
        )

        self.assertFalse(decision.should_run)
        self.assertEqual(decision.policy, "skip")
        self.assertIsNone(decision.tool)


if __name__ == "__main__":
    unittest.main()
