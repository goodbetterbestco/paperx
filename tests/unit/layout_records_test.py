import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.reconcile.layout_records import (
    merge_layout_and_figure_records,
    page_one_front_matter_records,
    figure_label_token,
    make_absorb_figure_caption_continuations,
    make_append_figure_caption_fragment,
    make_layout_record,
    make_match_figure_for_caption_record,
    make_page_one_front_matter_records,
    make_record_bbox,
    make_strip_caption_label_prefix,
    rect_x_overlap_ratio,
    synthetic_caption_record,
)
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_text,
    make_normalize_figure_caption_text,
)
from pipeline.reconcile.text_repairs_runtime import mathpix_text_blocks_by_page
from pipeline.reconcile.runtime_constants import CONTROL_CHAR_RE
from pipeline.text.headings import compact_text, normalize_title_key
from pipeline.text.prose import normalize_prose_text
from pipeline.types import LayoutBlock


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
LAYOUT_RECORD = make_layout_record(clean_text=CLEAN_TEXT)
PAGE_ONE_FRONT_MATTER_RECORDS = make_page_one_front_matter_records(
    clean_text=CLEAN_TEXT,
    normalize_title_key=normalize_title_key,
    mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
    layout_record=LAYOUT_RECORD,
)
APPEND_FIGURE_CAPTION_FRAGMENT = make_append_figure_caption_fragment(
    clean_text=CLEAN_TEXT,
    normalize_title_key=normalize_title_key,
    normalize_figure_caption_text=make_normalize_figure_caption_text(
        clean_text=CLEAN_TEXT,
        normalize_prose_text=normalize_prose_text,
    ),
    strip_caption_label_prefix=make_strip_caption_label_prefix(clean_text=CLEAN_TEXT),
)
ABSORB_FIGURE_CAPTION_CONTINUATIONS = make_absorb_figure_caption_continuations(
    match_figure_for_caption_record=make_match_figure_for_caption_record(
        record_bbox=make_record_bbox(block_source_spans=block_source_spans),
        rect_x_overlap_ratio=rect_x_overlap_ratio,
        figure_label_token=figure_label_token,
    ),
    append_figure_caption_fragment=APPEND_FIGURE_CAPTION_FRAGMENT,
)


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

        combined = PAGE_ONE_FRONT_MATTER_RECORDS(records, mathpix_layout)

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
            layout_record=LAYOUT_RECORD,
            absorb_figure_caption_continuations=ABSORB_FIGURE_CAPTION_CONTINUATIONS,
            figure_label_token=figure_label_token,
            synthetic_caption_record=synthetic_caption_record,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["text"], "Figure 2: Base caption")
        self.assertEqual(figures[0]["caption"], "Base caption continued description of the model")


if __name__ == "__main__":
    unittest.main()
