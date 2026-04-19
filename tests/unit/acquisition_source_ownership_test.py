import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.source_ownership import reported_layout_provider, reported_math_provider


class AcquisitionSourceOwnershipTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
