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
    select_metadata_observation,
    select_reference_observation,
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

    def test_select_metadata_observation_prefers_recommended_provider(self) -> None:
        selected = select_metadata_observation(
            source_scorecard={"recommended_primary_metadata_provider": "grobid"},
            metadata_candidates={
                "grobid": {"provider": "grobid", "title": "A title", "abstract": "", "references": []},
                "other": {"provider": "other", "title": "B title", "abstract": "", "references": []},
            },
        )

        self.assertEqual(selected["provider"], "grobid")

    def test_select_metadata_observation_escalates_to_grobid_when_fallback_is_unaccepted(self) -> None:
        selected = select_metadata_observation(
            source_scorecard={
                "recommended_primary_metadata_provider": "docling",
                "metadata_recommendation_basis": "fallback_unaccepted",
            },
            metadata_candidates={
                "docling": {"provider": "docling", "title": "Weak title", "abstract": "", "references": []},
                "grobid": {"provider": "grobid", "title": "A title", "abstract": "Abstract", "references": []},
            },
        )

        self.assertEqual(selected["provider"], "grobid")

    def test_select_reference_observation_prefers_recommended_provider(self) -> None:
        selected = select_reference_observation(
            source_scorecard={"recommended_primary_reference_provider": "mathpix"},
            metadata_candidates={
                "grobid": {"provider": "grobid", "title": "A title", "abstract": "", "references": ["G. Ref"]},
                "mathpix": {"provider": "mathpix", "title": "", "abstract": "", "references": ["M. Ref"]},
            },
        )

        self.assertEqual(selected["provider"], "mathpix")

    def test_select_reference_observation_falls_back_to_any_provider_with_references(self) -> None:
        selected = select_reference_observation(
            source_scorecard={"recommended_primary_reference_provider": "mathpix"},
            metadata_candidates={
                "grobid": {"provider": "grobid", "title": "A title", "abstract": "", "references": ["G. Ref"]},
                "mathpix": {"provider": "mathpix", "title": "", "abstract": "", "references": []},
            },
        )

        self.assertEqual(selected["provider"], "grobid")

    def test_select_reference_observation_escalates_to_grobid_when_fallback_is_unaccepted(self) -> None:
        selected = select_reference_observation(
            source_scorecard={
                "recommended_primary_reference_provider": "docling",
                "reference_recommendation_basis": "fallback_unaccepted",
            },
            metadata_candidates={
                "docling": {"provider": "docling", "title": "", "abstract": "", "references": ["D. Ref"]},
                "grobid": {"provider": "grobid", "title": "", "abstract": "", "references": ["G. Ref"]},
            },
        )

        self.assertEqual(selected["provider"], "grobid")


if __name__ == "__main__":
    unittest.main()
