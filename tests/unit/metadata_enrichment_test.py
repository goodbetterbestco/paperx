from __future__ import annotations

import sys
import unittest
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.orchestrator.metadata_enrichment import apply_metadata_observation


class MetadataEnrichmentTest(unittest.TestCase):
    def test_apply_metadata_observation_replaces_missing_abstract_and_empty_references(self) -> None:
        state = SimpleNamespace(
            metadata_observation={
                "provider": "grobid",
                "title": "Synthetic Acquisition Benchmark Paper",
                "abstract": "We evaluate structured document extraction for synthetic papers.",
                "references": [],
            },
            reference_observation={
                "provider": "docling",
                "title": "Synthetic Acquisition Benchmark Paper",
                "abstract": "",
                "references": [
                    "A. Author. Journal of Tests. 2024.",
                    "B. Author. Proceedings of Examples. 2023.",
                ],
            },
            front_matter={
                "title": "Synthetic Acquisition Benchmark Paper",
                "authors": [],
                "affiliations": [],
                "abstract_block_id": "blk-front-abstract-1",
                "funding_block_id": None,
            },
            blocks=[
                {
                    "id": "blk-front-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                    "source_spans": [],
                    "alternates": [],
                    "review": {"risk": "low", "status": "edited", "notes": ""},
                }
            ],
            references=[],
            decision_artifacts={},
            source_scorecard={
                "recommended_primary_metadata_provider": "grobid",
                "recommended_primary_reference_provider": "docling",
                "metadata_recommendation_basis": "accepted",
                "reference_recommendation_basis": "accepted",
            },
            document={
                "title": "Synthetic Acquisition Benchmark Paper",
                "front_matter": {
                    "title": "Synthetic Acquisition Benchmark Paper",
                    "authors": [],
                    "affiliations": [],
                    "abstract_block_id": "blk-front-abstract-1",
                    "funding_block_id": None,
                },
                "blocks": [
                    {
                        "id": "blk-front-abstract-1",
                        "type": "paragraph",
                        "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                        "source_spans": [],
                        "alternates": [],
                        "review": {"risk": "low", "status": "edited", "notes": ""},
                    }
                ],
                "references": [],
            },
        )

        enriched = apply_metadata_observation(state)

        abstract_text = enriched.blocks[0]["content"]["spans"][0]["text"]
        self.assertIn("structured document extraction", abstract_text)
        self.assertEqual(len(enriched.references), 2)
        self.assertTrue(enriched.decision_artifacts["metadata"]["abstract_applied"])
        self.assertTrue(enriched.decision_artifacts["metadata"]["references_applied"])
        self.assertEqual(enriched.decision_artifacts["metadata"]["provider"], "grobid")
        self.assertEqual(enriched.decision_artifacts["metadata"]["reference_provider"], "docling")
        self.assertEqual(enriched.decision_artifacts["metadata"]["recommended_metadata_provider"], "grobid")
        self.assertEqual(enriched.decision_artifacts["metadata"]["recommended_reference_provider"], "docling")
        self.assertEqual(enriched.decision_artifacts["metadata"]["metadata_recommendation_basis"], "accepted")
        self.assertEqual(enriched.decision_artifacts["metadata"]["reference_recommendation_basis"], "accepted")
        self.assertEqual(enriched.document["references"][0]["id"], "ref-001")

    def test_apply_metadata_observation_suppresses_fallback_unaccepted_owners(self) -> None:
        state = SimpleNamespace(
            metadata_observation={
                "provider": "grobid",
                "title": "Replacement Title",
                "abstract": "A trusted looking abstract that should not be applied automatically.",
                "references": [],
            },
            reference_observation={
                "provider": "docling",
                "title": "",
                "abstract": "",
                "references": [
                    "A. Author. Journal of Tests. 2024.",
                ],
            },
            front_matter={
                "title": "Bad",
                "authors": [],
                "affiliations": [],
                "abstract_block_id": "blk-front-abstract-1",
                "funding_block_id": None,
            },
            blocks=[
                {
                    "id": "blk-front-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                    "source_spans": [],
                    "alternates": [],
                    "review": {"risk": "low", "status": "edited", "notes": ""},
                }
            ],
            references=[],
            decision_artifacts={},
            source_scorecard={
                "recommended_primary_metadata_provider": "grobid",
                "recommended_primary_reference_provider": "docling",
                "metadata_recommendation_basis": "fallback_unaccepted",
                "reference_recommendation_basis": "fallback_unaccepted",
            },
            document={
                "title": "Bad",
                "front_matter": {
                    "title": "Bad",
                    "authors": [],
                    "affiliations": [],
                    "abstract_block_id": "blk-front-abstract-1",
                    "funding_block_id": None,
                },
                "blocks": [
                    {
                        "id": "blk-front-abstract-1",
                        "type": "paragraph",
                        "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                        "source_spans": [],
                        "alternates": [],
                        "review": {"risk": "low", "status": "edited", "notes": ""},
                    }
                ],
                "references": [],
            },
        )

        enriched = apply_metadata_observation(state)

        self.assertEqual(enriched.front_matter["title"], "Bad")
        self.assertEqual(enriched.blocks[0]["content"]["spans"][0]["text"], "[missing from original]")
        self.assertEqual(enriched.references, [])
        self.assertFalse(enriched.decision_artifacts["metadata"]["title_applied"])
        self.assertFalse(enriched.decision_artifacts["metadata"]["abstract_applied"])
        self.assertFalse(enriched.decision_artifacts["metadata"]["references_applied"])
        self.assertEqual(
            enriched.decision_artifacts["metadata"]["title_suppressed_reason"],
            "metadata_provider_not_accepted",
        )
        self.assertEqual(
            enriched.decision_artifacts["metadata"]["abstract_suppressed_reason"],
            "metadata_provider_not_accepted",
        )
        self.assertEqual(
            enriched.decision_artifacts["metadata"]["references_suppressed_reason"],
            "reference_provider_not_accepted",
        )


if __name__ == "__main__":
    unittest.main()
