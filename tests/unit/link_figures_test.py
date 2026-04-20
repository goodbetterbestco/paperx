import json
import tempfile
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.modules.setdefault("fitz", types.SimpleNamespace(Document=object, Matrix=object, Page=object, Rect=object))

import pipeline.figures.linking as linking
from pipeline.figures.linking import (
    build_manifest_from_pdf_path,
    choose_visual_region,
    caption_label,
    collect_references,
    extract_ocr_caption_lines,
    extract_reference_labels,
    group_ocr_lines,
    load_or_generate_ocr_records,
    merge_missing_caption_blocks,
    render_crop_if_missing,
    resolve_manifest_figures_dir,
    resolve_manifest_pdf_path,
    summarize_figure_expectations,
)


class _Rect:
    def __init__(self, *args: object) -> None:
        if len(args) == 1 and isinstance(args[0], _Rect):
            other = args[0]
            self.x0 = other.x0
            self.y0 = other.y0
            self.x1 = other.x1
            self.y1 = other.y1
            return
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            values = args[0]
            self.x0 = float(values[0])
            self.y0 = float(values[1])
            self.x1 = float(values[2])
            self.y1 = float(values[3])
            return
        x0, y0, x1, y1 = args
        self.x0 = float(x0)
        self.y0 = float(y0)
        self.x1 = float(x1)
        self.y1 = float(y1)

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def include_rect(self, other: "_Rect") -> None:
        self.x0 = min(self.x0, other.x0)
        self.y0 = min(self.y0, other.y0)
        self.x1 = max(self.x1, other.x1)
        self.y1 = max(self.y1, other.y1)

    def get_area(self) -> float:
        if self.is_empty:
            return 0.0
        return self.width * self.height

    def __and__(self, other: "_Rect") -> "_Rect":
        return _Rect(
            max(self.x0, other.x0),
            max(self.y0, other.y0),
            min(self.x1, other.x1),
            min(self.y1, other.y1),
        )


linking.fitz = types.SimpleNamespace(Rect=_Rect)


class _FakePage:
    def __init__(self, rect: _Rect) -> None:
        self.rect = rect

    def get_pixmap(self, matrix=None, alpha=False):
        return types.SimpleNamespace(save=lambda path: None)


class _FakeDocument:
    def __init__(self, page: _FakePage) -> None:
        self.page_count = 1
        self._page = page
        self.closed = False

    def load_page(self, index: int) -> _FakePage:
        return self._page

    def close(self) -> None:
        self.closed = True


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
        root = Path(__file__).resolve().parents[2]
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

    def test_extract_reference_labels_normalizes_mixed_reference_sequences(self) -> None:
        labels = extract_reference_labels("See Figs. 2, 3a and B4.1 for the construction, then compare with Figure 7.")

        self.assertEqual(labels, {"2", "3a", "b4.1", "7"})

    def test_merge_missing_caption_blocks_adds_only_new_caption_labels(self) -> None:
        text_blocks = [
            {"rect": _Rect(0, 10, 50, 20), "text": "Figure 1: Existing caption"},
            {"rect": _Rect(0, 40, 50, 50), "text": "Body text that remains in place."},
        ]
        extra_caption_blocks = [
            {"rect": _Rect(0, 5, 50, 15), "text": "Figure 1: OCR duplicate"},
            {"rect": _Rect(0, 25, 50, 35), "text": "Figure 2: OCR-only caption"},
        ]

        merged = merge_missing_caption_blocks(text_blocks, extra_caption_blocks)

        self.assertEqual([block["text"] for block in merged], [
            "Figure 1: Existing caption",
            "Figure 2: OCR-only caption",
            "Body text that remains in place.",
        ])

    def test_collect_references_returns_same_and_cross_page_mentions_without_duplicates(self) -> None:
        page_states = [
            {
                "page": 2,
                "text_blocks": [
                    {"text": "Figure 3: The semantic figure caption", "rect": _Rect(0, 10, 100, 20)},
                    {"text": "As shown in Fig. 3, the silhouette remains stable.", "rect": _Rect(0, 30, 120, 45)},
                    {"text": "As shown in Fig. 3, the silhouette remains stable.", "rect": _Rect(0, 50, 120, 65)},
                ],
            },
            {
                "page": 4,
                "text_blocks": [
                    {"text": "We revisit Figure 3 in the comparison study.", "rect": _Rect(0, 12, 120, 28)},
                ],
            },
        ]

        references = collect_references("3", 2, page_states)

        self.assertEqual(len(references), 2)
        self.assertEqual([reference["relation"] for reference in references], ["same_page", "cross_page"])
        self.assertEqual(references[0]["bbox"]["width"], 120)

    def test_summarize_figure_expectations_reports_matched_underlinked_and_expected_none(self) -> None:
        matched = summarize_figure_expectations({"expected_semantic_figure_count": 2}, 2)
        underlinked = summarize_figure_expectations({"expected_semantic_figure_count": 3}, 1)
        expected_none = summarize_figure_expectations({"expected_no_semantic_figures": True}, 0)

        self.assertEqual(matched["semantic_figure_expectation_status"], "matched")
        self.assertEqual(matched["semantic_figure_count_gap"], 0)
        self.assertEqual(underlinked["semantic_figure_expectation_status"], "underlinked")
        self.assertEqual(underlinked["semantic_figure_count_gap"], -2)
        self.assertEqual(expected_none["semantic_figure_expectation_status"], "expected_none")
        self.assertEqual(expected_none["semantic_figure_count_gap"], 0)

    def test_process_paper_builds_records_manifest_and_reference_stats(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            paper_id = "1990_synthetic_test_paper"
            corpus_root = root / "corpus" / "synthetic"
            paper_dir = corpus_root / paper_id
            figures_dir = paper_dir / "figures"
            pdf_path = paper_dir / f"{paper_id}.pdf"
            figures_dir.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(b"%PDF-1.4")
            layout = linking.ProjectLayout(
                engine_root=root,
                mode="corpus",
                corpus_name="synthetic",
                project_dir=None,
                corpus_root=corpus_root,
                source_root=corpus_root,
                review_root=corpus_root / "_canon",
                runs_root=corpus_root / "_runs",
                tmp_root=root / "tmp",
                figure_expectations_path=corpus_root / "figure_expectations.json",
            )
            manifest = {
                "id": paper_id,
                "source_pdf": str(pdf_path),
                "artifacts": {
                    "pdf": str(pdf_path),
                    "figures_dir": str(figures_dir),
                },
                "figure_expectations": {"expected_semantic_figure_count": 1},
                "stats": {},
            }
            page = _FakePage(_Rect(0, 0, 200, 300))
            document = _FakeDocument(page)
            text_blocks = [
                {"rect": _Rect(30, 180, 170, 198), "text": "Figure 2: Linked semantic figure caption", "source": "pdf_text"},
                {"rect": _Rect(24, 220, 180, 240), "text": "As shown in Fig. 2, the boundary remains stable.", "source": "pdf_text"},
            ]
            visual_blocks = [{"rect": _Rect(35, 70, 165, 150), "source": "image_xref_7"}]
            rendered: list[Path] = []

            with (
                patch.object(linking.fitz, "open", return_value=document, create=True),
                patch.object(linking, "extract_pdf_text_blocks", return_value=text_blocks),
                patch.object(linking, "extract_pdf_visual_blocks", return_value=visual_blocks),
                patch.object(linking, "extract_drawing_rects", return_value=[]),
                patch.object(linking, "render_crop_if_missing", side_effect=lambda page, rect, output_path: rendered.append(output_path) or True),
            ):
                updated_manifest, count = linking.process_paper(manifest, layout=layout)

            self.assertEqual(count, 1)
            self.assertTrue(document.closed)
            self.assertEqual(rendered, [figures_dir / "figure-2-p001.png"])
            self.assertEqual(updated_manifest["stats"]["semantic_figure_count"], 1)
            self.assertEqual(updated_manifest["stats"]["semantic_figure_link_modes"], {"visual_blocks": 1})
            self.assertEqual(updated_manifest["stats"]["semantic_figure_reference_count"], 1)
            self.assertEqual(updated_manifest["stats"]["semantic_figure_expectation_status"], "matched")

            manifest_path = figures_dir / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["records"]), 1)
            self.assertEqual(payload["records"][0]["figure_id"], "figure-2")
            self.assertEqual(payload["records"][0]["label"], "2")
            self.assertEqual(payload["records"][0]["link_mode"], "visual_blocks")
            self.assertEqual(payload["records"][0]["sources"], ["image_xref_7"])

    def test_resolve_manifest_paths_prefer_explicit_project_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            project_pdf = root / "1990_synthetic_test_paper" / "1990_synthetic_test_paper.pdf"
            project_figures_dir = root / "artifacts" / "figures"
            project_pdf.parent.mkdir(parents=True, exist_ok=True)
            project_figures_dir.mkdir(parents=True, exist_ok=True)
            project_pdf.write_bytes(b"%PDF-1.4")
            layout = linking.ProjectLayout(
                engine_root=root,
                mode="project",
                corpus_name="fixture",
                project_dir=root,
                corpus_root=root,
                source_root=root,
                review_root=root / "_canon",
                runs_root=root / "_runs",
                tmp_root=root / "tmp",
                figure_expectations_path=root / "figure_expectations.json",
            )
            manifest = {
                "id": "1990_synthetic_test_paper",
                "source_pdf": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
                "artifacts": {
                    "pdf": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
                    "figures_dir": "artifacts/figures",
                },
            }

            self.assertEqual(resolve_manifest_pdf_path(manifest, layout=layout), project_pdf)
            self.assertEqual(resolve_manifest_figures_dir(manifest, layout=layout), project_figures_dir)

    def test_group_ocr_lines_merges_column_lines_and_extracts_unique_caption_lines(self) -> None:
        page_rect = _Rect(0, 0, 200, 300)
        grouped_lines = [
            {"text": "Figure 2:", "bbox": {"x0": 0.10, "y0": 0.60, "x1": 0.40, "y1": 0.65}},
            {"text": "Stable silhouette", "bbox": {"x0": 0.10, "y0": 0.66, "x1": 0.45, "y1": 0.71}},
            {"text": "Body line one", "bbox": {"x0": 0.55, "y0": 0.20, "x1": 0.85, "y1": 0.24}},
            {"text": "Body line two", "bbox": {"x0": 0.55, "y0": 0.25, "x1": 0.85, "y1": 0.29}},
        ]
        caption_lines = [*grouped_lines, {"text": "Figure 2:", "bbox": {"x0": 0.10, "y0": 0.60, "x1": 0.40, "y1": 0.65}}]

        grouped = group_ocr_lines(grouped_lines, page_rect)
        captions = extract_ocr_caption_lines(caption_lines, page_rect)

        self.assertEqual(len(grouped), 2)
        self.assertEqual(grouped[0]["text"], "Body line one Body line two")
        self.assertEqual(grouped[1]["text"], "Figure 2: Stable silhouette")
        self.assertEqual(len(captions), 1)
        self.assertEqual(captions[0]["source"], "ocr_caption")
        self.assertEqual(captions[0]["text"], "Figure 2:")

    def test_choose_visual_region_returns_column_gap_fallback_when_visuals_are_missing(self) -> None:
        page_rect = _Rect(0, 0, 200, 300)
        caption_block = {"rect": _Rect(20, 150, 80, 168), "text": "Figure 2: Caption"}
        text_blocks = [
            {
                "rect": _Rect(12, 20, 92, 60),
                "text": "This body paragraph is intentionally long enough to establish a body-text scope for the fallback region.",
            },
            caption_block,
        ]

        rect, link_mode, sources = choose_visual_region(page_rect, caption_block, text_blocks, [], [])

        self.assertIsNotNone(rect)
        self.assertEqual(link_mode, "column_gap_fallback")
        self.assertEqual(sources, ["heuristic_scope"])
        self.assertGreaterEqual(rect.width, 40)
        self.assertGreaterEqual(rect.height, 40)

    def test_choose_visual_region_returns_drawing_fallback_when_drawings_match_caption_side(self) -> None:
        page_rect = _Rect(0, 0, 200, 300)
        caption_block = {"rect": _Rect(25, 170, 90, 190), "text": "Figure 2: Caption"}
        drawing_rect = _Rect(30, 80, 100, 140)

        rect, link_mode, sources = choose_visual_region(
            page_rect,
            caption_block,
            [caption_block],
            [],
            [drawing_rect],
        )

        self.assertIsNotNone(rect)
        self.assertEqual(link_mode, "drawing_fallback")
        self.assertEqual(sources, ["drawing_rects"])
        self.assertGreaterEqual(rect.width, drawing_rect.width)
        self.assertGreaterEqual(rect.height, drawing_rect.height)

    def test_load_or_generate_ocr_records_renders_pages_and_invokes_vision_ocr(self) -> None:
        doc = _FakeDocument(_FakePage(_Rect(0, 0, 200, 300)))
        manifest = {"id": "1990_synthetic_test_paper", "source_pdf": "ignored.pdf"}

        with (
            patch.object(linking, "render_pages_for_ocr", return_value=[Path("/tmp/page-001.png")]),
            patch.object(linking, "run_vision_ocr", return_value=[{"lines": [{"text": "Figure 2"}]}]),
        ):
            records = load_or_generate_ocr_records(manifest, doc)

        self.assertEqual(records, [{"lines": [{"text": "Figure 2"}]}])


if __name__ == "__main__":
    unittest.main()
