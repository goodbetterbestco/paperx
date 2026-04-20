import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.acquisition.providers import derive_metadata_reference_observation_from_layout


class AcquisitionProvidersTest(unittest.TestCase):
    def test_derive_metadata_reference_observation_from_docling_layout_extracts_front_matter_and_references(self) -> None:
        observation = derive_metadata_reference_observation_from_layout(
            "docling",
            {
                "engine": "docling",
                "page_count": 3,
                "blocks": [
                    {"page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Acquisition Benchmark Paper"},
                    {"page": 1, "order": 2, "role": "front_matter", "text": "Alice Example, Bob Example"},
                    {"page": 1, "order": 3, "role": "front_matter", "text": "Abstract"},
                    {
                        "page": 1,
                        "order": 4,
                        "role": "front_matter",
                        "text": "We evaluate structured document extraction across multiple synthetic fixtures.",
                    },
                    {"page": 3, "order": 1, "role": "reference", "text": "[1] A. Author. Journal of Tests. 2024."},
                    {"page": 3, "order": 2, "role": "reference", "text": "[2] B. Author. Proceedings of Examples. 2023."},
                ],
            },
        )

        self.assertEqual(observation.provider, "docling")
        self.assertEqual(observation.title, "Synthetic Acquisition Benchmark Paper")
        self.assertIn("structured document extraction", observation.abstract.lower())
        self.assertEqual(len(observation.references), 2)

    def test_derive_metadata_reference_observation_from_mathpix_layout_uses_explicit_types_and_reference_section(self) -> None:
        observation = derive_metadata_reference_observation_from_layout(
            "mathpix",
            {
                "engine": "mathpix",
                "page_count": 2,
                "blocks": [
                    {
                        "page": 1,
                        "order": 1,
                        "role": "front_matter",
                        "text": "A Mathpix Exported Title",
                        "meta": {"mathpix_type": "title"},
                    },
                    {
                        "page": 1,
                        "order": 2,
                        "role": "front_matter",
                        "text": "Abstract: A compact abstract from Mathpix.",
                        "meta": {"mathpix_type": "abstract"},
                    },
                    {"page": 2, "order": 1, "role": "heading", "text": "References"},
                    {"page": 2, "order": 2, "role": "paragraph", "text": "[1] A. Author. Journal of Tests. 2024."},
                    {"page": 2, "order": 3, "role": "paragraph", "text": "[2] B. Author. Proceedings of Examples. 2023."},
                ],
            },
        )

        self.assertEqual(observation.provider, "mathpix")
        self.assertEqual(observation.title, "A Mathpix Exported Title")
        self.assertEqual(observation.abstract, "A compact abstract from Mathpix.")
        self.assertEqual(len(observation.references), 2)


if __name__ == "__main__":
    unittest.main()
