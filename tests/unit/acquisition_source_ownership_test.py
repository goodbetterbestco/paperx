import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.source_ownership import (
    canonical_provider_name,
    normalize_scorecard_recommendations,
    reported_layout_provider,
    reported_math_provider,
    select_math_payload,
)


class AcquisitionSourceOwnershipTest(unittest.TestCase):
    def test_canonical_provider_name_normalizes_layout_aliases(self) -> None:
        self.assertEqual(canonical_provider_name("mathpix_layout"), "mathpix")
        self.assertEqual(canonical_provider_name("docling-layout"), "docling")
        self.assertEqual(canonical_provider_name("native_pdf"), "native_pdf")

    def test_normalize_scorecard_recommendations_canonicalizes_primary_providers(self) -> None:
        normalized = normalize_scorecard_recommendations(
            {
                "recommended_primary_layout_provider": "mathpix_layout",
                "recommended_primary_math_provider": "docling",
                "recommended_primary_metadata_provider": "grobid",
                "recommended_primary_reference_provider": "mathpix_layout",
            }
        )

        self.assertEqual(normalized["recommended_primary_layout_provider"], "mathpix")
        self.assertEqual(normalized["recommended_primary_reference_provider"], "mathpix")

    def test_reported_layout_provider_uses_primary_provider_for_generic_engine(self) -> None:
        self.assertEqual(
            reported_layout_provider(
                "composed",
                source_scorecard={"recommended_primary_layout_provider": "mathpix"},
                fallback="none",
            ),
            "mathpix",
        )

    def test_reported_layout_provider_preserves_concrete_engine(self) -> None:
        self.assertEqual(
            reported_layout_provider(
                "docling",
                source_scorecard={"recommended_primary_layout_provider": "mathpix_layout"},
            ),
            "docling",
        )

    def test_reported_math_provider_requires_real_entries(self) -> None:
        self.assertEqual(
            reported_math_provider(
                "mathpix",
                source_scorecard={"recommended_primary_math_provider": "mathpix"},
                math_payload={"engine": "mathpix", "entries": []},
                fallback="none",
            ),
            "none",
        )

    def test_reported_math_provider_uses_primary_provider_when_entries_exist(self) -> None:
        self.assertEqual(
            reported_math_provider(
                "external_math",
                source_scorecard={"recommended_primary_math_provider": "docling"},
                math_payload={"engine": "docling", "entries": [{"id": "eq-1"}]},
            ),
            "docling",
        )

    def test_select_math_payload_prefers_recommended_provider_when_entries_exist(self) -> None:
        selected = select_math_payload(
            source_scorecard={"recommended_primary_math_provider": "docling"},
            docling_math={"engine": "docling", "entries": [{"id": "doc-eq-1"}]},
            mathpix_math={"engine": "mathpix", "entries": [{"id": "mx-eq-1"}]},
        )

        self.assertEqual(selected["engine"], "docling")

    def test_select_math_payload_falls_back_to_available_provider(self) -> None:
        selected = select_math_payload(
            source_scorecard={"recommended_primary_math_provider": "docling"},
            docling_math={"engine": "docling", "entries": []},
            mathpix_math={"engine": "mathpix", "entries": [{"id": "mx-eq-1"}]},
        )

        self.assertEqual(selected["engine"], "mathpix")


if __name__ == "__main__":
    unittest.main()
