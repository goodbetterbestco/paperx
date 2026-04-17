import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile_blocks as rb
from pipeline.reconcile.layout_records import merge_layout_and_figure_records, page_one_front_matter_records
from pipeline.types import LayoutBlock


class LayoutRecordsTest(unittest.TestCase):
    def test_page_one_front_matter_records_dedupes_mathpix_duplicates(self) -> None:
        records = [
            {
                "id": "native-title",
                "page": 1,
                "group_index": 10,
                "split_index": 1,
                "type": "paragraph",
                "text": "A Good Paper",
                "source_spans": [],
                "meta": {},
            }
        ]
        mathpix_layout = {
            "blocks": [
                LayoutBlock(
                    id="mx-title",
                    page=1,
                    order=1,
                    text="A Good Paper",
                    role="paragraph",
                    meta={"mathpix_type": "text"},
                    bbox={"x0": 10.0, "y0": 10.0, "x1": 50.0, "y1": 20.0, "width": 40.0, "height": 10.0},
                ),
                LayoutBlock(
                    id="mx-author",
                    page=1,
                    order=2,
                    text="Jane Doe",
                    role="paragraph",
                    meta={"mathpix_type": "text"},
                    bbox={"x0": 10.0, "y0": 22.0, "x1": 50.0, "y1": 32.0, "width": 40.0, "height": 10.0},
                ),
            ]
        }

        combined = page_one_front_matter_records(
            records,
            mathpix_layout,
            clean_text=rb._clean_text,
            normalize_title_key=rb.normalize_title_key,
            mathpix_text_blocks_by_page=rb._mathpix_text_blocks_by_page,
            layout_record=rb._layout_record,
        )

        self.assertEqual([record["text"] for record in combined], ["A Good Paper", "Jane Doe"])

    def test_merge_layout_and_figure_records_absorbs_caption_continuation(self) -> None:
        layout_blocks = [
            LayoutBlock(
                id="caption-1",
                page=1,
                order=1,
                text="Figure 2: Base caption",
                role="caption",
                bbox={"x0": 40.0, "y0": 80.0, "x1": 200.0, "y1": 95.0, "width": 160.0, "height": 15.0},
            ),
            LayoutBlock(
                id="caption-2",
                page=1,
                order=2,
                text="continued description of the model",
                role="caption",
                bbox={"x0": 40.0, "y0": 97.0, "x1": 220.0, "y1": 112.0, "width": 180.0, "height": 15.0},
            ),
        ]
        figures = [
            {
                "id": "figure-2",
                "page": 1,
                "label": "Figure 2",
                "caption": "Base caption",
                "bbox": {"x0": 35.0, "y0": 40.0, "x1": 230.0, "y1": 78.0, "width": 195.0, "height": 38.0},
                "provenance": {
                    "caption_bbox": {"x0": 40.0, "y0": 80.0, "x1": 220.0, "y1": 112.0, "width": 180.0, "height": 32.0}
                },
            }
        ]

        records, _ = merge_layout_and_figure_records(
            layout_blocks,
            figures,
            layout_record=rb._layout_record,
            absorb_figure_caption_continuations=rb._absorb_figure_caption_continuations,
            figure_label_token=rb._figure_label_token,
            synthetic_caption_record=rb._synthetic_caption_record,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["text"], "Figure 2: Base caption")
        self.assertEqual(figures[0]["caption"], "Base caption continued description of the model")


if __name__ == "__main__":
    unittest.main()
