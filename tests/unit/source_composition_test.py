from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.orchestrator.source_composition import compose_layout_sources, preferred_layout_provider


def _layout(engine: str, blocks: list[dict[str, object]]) -> dict[str, object]:
    return {
        "engine": engine,
        "pdf_path": "fixture.pdf",
        "page_count": 2,
        "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
        "blocks": blocks,
    }


class SourceCompositionTest(unittest.TestCase):
    def test_preferred_layout_provider_uses_route_tiebreak_for_scan_like_documents(self) -> None:
        provider = preferred_layout_provider(
            _layout("docling", [{"page": 1, "order": 1, "role": "paragraph", "text": "Body"}]),
            _layout("mathpix", [{"page": 1, "order": 1, "role": "paragraph", "text": "Body"}]),
            acquisition_route={"primary_route": "scan_or_image_heavy"},
            source_scorecard={
                "providers": [
                    {"provider": "docling", "overall_score": 0.5},
                    {"provider": "mathpix", "overall_score": 0.48},
                ]
            },
        )

        self.assertEqual(provider, "mathpix")

    def test_compose_layout_sources_prefers_mathpix_globally_when_scorecard_is_stronger(self) -> None:
        docling_sources = {
            "layout": _layout(
                "docling",
                [
                    {"id": "d1", "page": 1, "order": 1, "text": "Docling front matter", "role": "paragraph"},
                    {"id": "d2", "page": 2, "order": 1, "text": "Docling body", "role": "paragraph"},
                ],
            )
        }
        mathpix_sources = {
            "layout": _layout(
                "mathpix",
                [
                    {"id": "m1", "page": 1, "order": 1, "text": "Mathpix front matter", "role": "paragraph"},
                    {"id": "m2", "page": 2, "order": 1, "text": "Mathpix body", "role": "paragraph"},
                ],
            )
        }

        composed = compose_layout_sources(
            docling_sources,
            mathpix_sources,
            source_scorecard={
                "providers": [
                    {"provider": "docling", "overall_score": 0.4},
                    {"provider": "mathpix", "overall_score": 0.8},
                ]
            },
        )

        self.assertEqual([block["id"] for block in composed["blocks"]], ["m1", "m2"])
        self.assertEqual(composed["page_sources"], {"1": "mathpix", "2": "mathpix"})

    def test_compose_layout_sources_keeps_page_one_override_for_docling_preference(self) -> None:
        docling_sources = {
            "layout": _layout(
                "docling",
                [
                    {"id": "d1", "page": 1, "order": 1, "text": "Creative Commons accepted manuscript", "role": "paragraph"},
                    {"id": "d2", "page": 2, "order": 1, "text": "Docling body", "role": "paragraph"},
                ],
            )
        }
        mathpix_sources = {
            "layout": _layout(
                "mathpix",
                [
                    {"id": "m1", "page": 1, "order": 1, "text": "Abstract", "role": "paragraph"},
                    {"id": "m2", "page": 2, "order": 1, "text": "Mathpix body", "role": "paragraph"},
                ],
            )
        }

        composed = compose_layout_sources(
            docling_sources,
            mathpix_sources,
            source_scorecard={
                "providers": [
                    {"provider": "docling", "overall_score": 0.9},
                    {"provider": "mathpix", "overall_score": 0.6},
                ]
            },
        )

        self.assertEqual([block["id"] for block in composed["blocks"]], ["m1", "d2"])
        self.assertEqual(composed["page_sources"], {"1": "mathpix", "2": "docling"})


if __name__ == "__main__":
    unittest.main()
