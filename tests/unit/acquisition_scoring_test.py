from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.scoring import (
    build_source_scorecard,
    score_layout_provider,
    score_math_provider,
    score_metadata_provider,
)


class AcquisitionScoringTest(unittest.TestCase):
    def test_score_layout_provider_counts_structural_roles(self) -> None:
        score = score_layout_provider(
            "docling",
            {
                "page_count": 1,
                "blocks": [
                    {"id": "b1", "page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Acquisition Benchmark Paper"},
                    {"id": "b2", "page": 1, "order": 2, "role": "heading", "text": "Abstract"},
                    {"id": "b3", "page": 1, "order": 3, "role": "paragraph", "text": "A paragraph of text."},
                    {"id": "b4", "page": 1, "order": 4, "role": "reference", "text": "[1] Reference"},
                ],
            },
            kind="layout",
            math_entry_count=2,
        )

        self.assertEqual(score["heading_count"], 1)
        self.assertEqual(score["front_matter_count"], 1)
        self.assertEqual(score["paragraph_count"], 1)
        self.assertEqual(score["reference_count"], 1)
        self.assertEqual(score["math_entry_count"], 2)
        self.assertGreater(score["overall_score"], 0.0)

    def test_build_source_scorecard_sorts_best_provider_first(self) -> None:
        scorecard = build_source_scorecard(
            native_layout={"page_count": 1, "blocks": [{"page": 1, "order": 1, "role": "paragraph", "text": "Body text."}]},
            external_layout={
                "engine": "docling",
                "page_count": 1,
                "blocks": [
                    {"page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Title"},
                    {"page": 1, "order": 2, "role": "heading", "text": "Abstract"},
                    {"page": 1, "order": 3, "role": "paragraph", "text": "Body text."},
                    {"page": 1, "order": 4, "role": "reference", "text": "[1] Reference"},
                ],
            },
            mathpix_layout=None,
            external_math={"engine": "mathpix", "entries": [{"id": "eq-1"}, {"id": "eq-2"}]},
        )

        self.assertEqual(scorecard["providers"][0]["provider"], "docling")
        self.assertEqual(scorecard["recommended_primary_layout_provider"], "docling")
        self.assertEqual(scorecard["recommended_primary_math_provider"], "mathpix")

    def test_score_math_provider_biases_mathpix_for_math_dense_routes(self) -> None:
        docling = score_math_provider(
            "docling",
            {"entries": [{"id": "eq-1", "kind": "display"}]},
            route_bias="math_dense",
        )
        mathpix = score_math_provider(
            "mathpix",
            {"entries": [{"id": "eq-1", "kind": "display"}]},
            route_bias="math_dense",
        )

        self.assertGreater(mathpix["overall_score"], docling["overall_score"])

    def test_score_metadata_provider_rewards_clean_abstract_and_references(self) -> None:
        grobid = score_metadata_provider(
            "grobid",
            {
                "title": "Synthetic Acquisition Benchmark Paper",
                "abstract": "We evaluate structured document extraction for synthetic papers.",
                "references": ["Author. Journal of Tests. 2024."],
            },
            route_bias="born_digital_scholarly",
        )

        self.assertTrue(grobid["title_present"])
        self.assertTrue(grobid["abstract_clean"])
        self.assertEqual(grobid["reference_count"], 1)
        self.assertGreater(grobid["overall_score"], 0.8)

    def test_build_source_scorecard_includes_metadata_and_reference_recommendations(self) -> None:
        scorecard = build_source_scorecard(
            native_layout={"page_count": 1, "blocks": [{"page": 1, "order": 1, "role": "paragraph", "text": "Body text."}]},
            external_layout=None,
            mathpix_layout=None,
            external_math=None,
            route_bias="born_digital_scholarly",
            metadata_observations={
                "grobid": {
                    "title": "Synthetic Acquisition Benchmark Paper",
                    "abstract": "We evaluate structured document extraction for synthetic papers.",
                    "references": ["Author. Journal of Tests. 2024."],
                }
            },
        )

        self.assertEqual(scorecard["recommended_primary_metadata_provider"], "grobid")
        self.assertEqual(scorecard["recommended_primary_reference_provider"], "grobid")

    def test_build_source_scorecard_can_score_multiple_explicit_candidates(self) -> None:
        scorecard = build_source_scorecard(
            native_layout=None,
            external_layout=None,
            mathpix_layout=None,
            external_math=None,
            layout_candidates={
                "docling": {
                    "engine": "docling",
                    "page_count": 1,
                    "blocks": [{"page": 1, "order": 1, "role": "paragraph", "text": "Body text."}],
                },
                "mathpix": {
                    "engine": "mathpix",
                    "page_count": 1,
                    "blocks": [
                        {"page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Title"},
                        {"page": 1, "order": 2, "role": "heading", "text": "Abstract"},
                        {"page": 1, "order": 3, "role": "paragraph", "text": "Body text."},
                    ],
                },
            },
            math_candidates={
                "docling": {"engine": "docling", "entries": [{"id": "doc-eq-1", "kind": "display"}]},
                "mathpix": {"engine": "mathpix", "entries": [{"id": "mx-eq-1", "kind": "display"}, {"id": "mx-eq-2", "kind": "display"}]},
            },
            route_bias="math_dense",
        )

        self.assertEqual(scorecard["recommended_primary_layout_provider"], "mathpix")
        self.assertEqual(scorecard["recommended_primary_math_provider"], "mathpix")


if __name__ == "__main__":
    unittest.main()
