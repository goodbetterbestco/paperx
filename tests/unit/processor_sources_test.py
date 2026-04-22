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
        acquisition_route = {
            "traits": [],
            "layout_priority": ["docling"],
            "math_priority": ["docling", "mathpix"],
        }
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
            "execution_plan": {"provider_order": ["docling"], "mathpix_requested": False, "mathpix_reason": "route_prefers_docling"},
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
        composed = compose_external_sources(
            "1990_synthetic_test_paper",
            acquisition_route=acquisition_route,
            docling_sources=docling_sources,
            mathpix_sources=mathpix_sources,
        )

        self.assertEqual(composed["layout_owner"], "docling")
        self.assertEqual(composed["final_layout"]["engine"], "docling")
        self.assertNotEqual(composed["final_layout"]["engine"], "composed")
        self.assertEqual(composed["metadata_owner"], "docling")
        self.assertEqual(composed["acquisition_execution"]["owners"]["layout"], "docling")
        self.assertFalse(composed["acquisition_execution"]["recovery"]["layout_composed"])

    def test_compose_external_sources_raises_when_no_accepted_layout_owner_exists(self) -> None:
        acquisition_route = {
            "traits": [],
            "layout_priority": ["docling", "mathpix"],
            "math_priority": ["mathpix", "docling"],
        }
        docling_sources = {
            "layout": {
                "engine": "docling",
                "page_count": 1,
                "blocks": [{"id": "docling-1", "page": 1, "order": 1, "role": "paragraph", "text": "Unaccepted docling layout"}],
            },
            "math": {"engine": "docling", "entries": []},
            "execution_plan": {"provider_order": ["docling"], "mathpix_requested": False, "mathpix_reason": "route_prefers_docling"},
        }
        mathpix_sources = {
            "layout": {
                "engine": "mathpix",
                "page_count": 1,
                "blocks": [{"id": "mathpix-1", "page": 1, "order": 1, "role": "paragraph", "text": "Unaccepted mathpix layout"}],
            },
            "math": {"engine": "mathpix", "entries": []},
        }
        with self.assertRaises(RuntimeError):
            compose_external_sources(
                "1990_synthetic_test_paper",
                acquisition_route=acquisition_route,
                docling_sources=docling_sources,
                mathpix_sources=mathpix_sources,
            )


if __name__ == "__main__":
    unittest.main()
