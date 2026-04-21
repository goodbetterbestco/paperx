from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.processor.sources import compose_external_sources


class ProcessorSourcesTest(unittest.TestCase):
    def test_compose_external_sources_selects_single_accepted_owner_without_composition(self) -> None:
        docling_sources = {
            "layout": {
                "engine": "docling",
                "page_count": 1,
                "blocks": [
                    {"id": "docling-1", "page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Test Paper"},
                    {"id": "docling-2", "page": 1, "order": 2, "role": "heading", "text": "Abstract"},
                    {"id": "docling-3", "page": 1, "order": 3, "role": "paragraph", "text": "Synthetic abstract."},
                ],
            },
            "math": {"engine": "docling", "entries": []},
            "pdf_selection": {"ocr_prepass_policy": "skip", "ocr_prepass_tool": None, "ocr_prepass_applied": False, "pdf_source_kind": "original", "selected_pdf_path": Path("/tmp/synthetic.pdf")},
            "execution_plan": {"provider_order": ["docling"], "mathpix_strategy": "skipped", "mathpix_reason": "route_sufficient_without_mathpix", "mathpix_prefetch_eligible": False},
        }
        mathpix_sources = {
            "layout": {
                "engine": "mathpix",
                "page_count": 1,
                "blocks": [
                    {"id": "mathpix-1", "page": 1, "order": 1, "role": "paragraph", "text": "Low quality layout"},
                ],
            },
            "math": {"engine": "mathpix", "entries": []},
        }
        source_scorecard = {
            "providers": [
                {"provider": "docling", "kind": "layout", "accepted": True, "overall_score": 0.8, "acceptance_threshold": 0.3, "rejection_reasons": []},
                {"provider": "mathpix", "kind": "layout", "accepted": False, "overall_score": 0.1, "acceptance_threshold": 0.3, "rejection_reasons": ["score_below_threshold"]},
                {"provider": "docling", "kind": "metadata", "accepted": True, "overall_score": 0.7, "acceptance_threshold": 0.45, "rejection_reasons": [], "title_present": True, "abstract_present": True, "reference_count": 0},
            ],
            "recommended_primary_layout_provider": "docling",
            "recommended_primary_math_provider": None,
            "recommended_primary_metadata_provider": "docling",
            "recommended_primary_reference_provider": None,
        }

        composed = compose_external_sources(
            "1990_synthetic_test_paper",
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
            build_acquisition_route_report_impl=lambda *args, **kwargs: {"primary_route": "born_digital_scholarly", "traits": [], "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None}},
            build_source_scorecard_impl=lambda **kwargs: source_scorecard,
        )

        self.assertEqual(composed["layout_owner"], "docling")
        self.assertEqual(composed["final_layout"]["engine"], "docling")
        self.assertNotEqual(composed["final_layout"]["engine"], "composed")
        self.assertEqual(composed["metadata_owner"], "docling")
        self.assertEqual(composed["acquisition_execution"]["owners"]["layout"], "docling")
        self.assertFalse(composed["acquisition_execution"]["recovery"]["layout_composed"])

    def test_compose_external_sources_raises_when_no_accepted_layout_owner_exists(self) -> None:
        docling_sources = {
            "layout": {
                "engine": "docling",
                "page_count": 1,
                "blocks": [{"id": "docling-1", "page": 1, "order": 1, "role": "paragraph", "text": "Unaccepted docling layout"}],
            },
            "math": {"engine": "docling", "entries": []},
            "pdf_selection": {"ocr_prepass_policy": "skip", "ocr_prepass_tool": None, "ocr_prepass_applied": False, "pdf_source_kind": "original", "selected_pdf_path": Path("/tmp/synthetic.pdf")},
            "execution_plan": {"provider_order": ["docling"], "mathpix_strategy": "skipped", "mathpix_reason": "route_sufficient_without_mathpix", "mathpix_prefetch_eligible": False},
        }
        mathpix_sources = {
            "layout": {
                "engine": "mathpix",
                "page_count": 1,
                "blocks": [{"id": "mathpix-1", "page": 1, "order": 1, "role": "paragraph", "text": "Unaccepted mathpix layout"}],
            },
            "math": {"engine": "mathpix", "entries": []},
        }
        source_scorecard = {
            "providers": [
                {"provider": "docling", "kind": "layout", "accepted": False, "overall_score": 0.2, "acceptance_threshold": 0.3, "rejection_reasons": ["score_below_threshold"]},
                {"provider": "mathpix", "kind": "layout", "accepted": False, "overall_score": 0.1, "acceptance_threshold": 0.3, "rejection_reasons": ["score_below_threshold"]},
            ],
            "recommended_primary_layout_provider": "docling",
            "recommended_primary_math_provider": None,
            "recommended_primary_metadata_provider": None,
            "recommended_primary_reference_provider": None,
        }

        with self.assertRaises(RuntimeError):
            compose_external_sources(
                "1990_synthetic_test_paper",
                docling_sources=docling_sources,
                mathpix_sources=mathpix_sources,
                build_acquisition_route_report_impl=lambda *args, **kwargs: {"primary_route": "layout_complex", "traits": [], "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None}},
                build_source_scorecard_impl=lambda **kwargs: source_scorecard,
            )


if __name__ == "__main__":
    unittest.main()
