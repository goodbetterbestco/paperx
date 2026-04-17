import tempfile
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.modules.setdefault("fitz", types.SimpleNamespace(Document=object, Matrix=object, Page=object, Rect=object))

from paper_pipeline.figure_linking import build_manifest_from_pdf_path, caption_label, render_crop_if_missing


class LinkFiguresTest(unittest.TestCase):
    def test_caption_label_accepts_common_caption_formats(self) -> None:
        self.assertEqual(caption_label("Fig.\u202f1\u2002\u2009Model of a half of a torus"), "1")
        self.assertEqual(caption_label("Figure 1 (a) A simple polygon"), "1")
        self.assertEqual(caption_label("(c) FIG. 1"), "1")
        self.assertEqual(caption_label("Fig. I"), "1")
        self.assertEqual(caption_label("Figure & Augmented visibility maps"), "8")
        self.assertEqual(caption_label("FIG.8"), "8")
        self.assertEqual(caption_label("Figure 7 Empey visibility map"), "7")

    def test_caption_label_rejects_body_references(self) -> None:
        self.assertIsNone(caption_label("Figure 3 provides a diagram illustrating such a pipeline."))
        self.assertIsNone(caption_label("As shown in Figure 3, the method changes."))

    def test_build_manifest_from_pdf_path_uses_paper_owned_pdf(self) -> None:
        root = Path(__file__).resolve().parents[3]
        pdf_path = root / "docs" / "2016_recognizing_weakly_simple_polygons" / "2016_recognizing_weakly_simple_polygons.pdf"
        manifest = build_manifest_from_pdf_path(pdf_path)

        self.assertEqual(manifest["id"], "2016_recognizing_weakly_simple_polygons")
        self.assertEqual(
            manifest["source_pdf"],
            "docs/2016_recognizing_weakly_simple_polygons/2016_recognizing_weakly_simple_polygons.pdf",
        )
        self.assertEqual(manifest["figure_expectations"]["expected_semantic_figure_count"], 18)

    def test_render_crop_if_missing_preserves_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "figure-12-p009.png"
            output_path.write_bytes(b"manual")
            written = render_crop_if_missing(object(), object(), output_path)
            preserved = output_path.read_bytes()

        self.assertFalse(written)
        self.assertEqual(preserved, b"manual")


if __name__ == "__main__":
    unittest.main()
