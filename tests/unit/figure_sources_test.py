import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import ProjectLayout
from pipeline.sources.figures import ensure_figure_manifest, extract_figures


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
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


class FigureSourcesTest(unittest.TestCase):
    def test_ensure_figure_manifest_returns_existing_manifest_without_rebuilding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            manifest_path = layout.paper_dir("1990_synthetic_test_paper") / "figures" / "manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text('{"records": []}\n', encoding="utf-8")

            resolved = ensure_figure_manifest("1990_synthetic_test_paper", layout=layout)

            self.assertEqual(resolved, manifest_path)

    def test_extract_figures_converts_manifest_records_into_canonical_figures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            manifest_path = layout.paper_dir(paper_id) / "figures" / "manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "figure_id": "figure-2a",
                                "label": "2A",
                                "page": 7,
                                "image_path": "corpus/synthetic/1990_synthetic_test_paper/figures/figure-2a-p007.png",
                                "caption_text": "Fig. 2A: Boundary silhouette used for evaluation.",
                                "figure_bbox": {
                                    "x0": 10.0,
                                    "y0": 20.0,
                                    "x1": 154.0,
                                    "y1": 236.0,
                                    "width": 144.0,
                                    "height": 216.0,
                                },
                                "caption_bbox": {"x0": 11.0, "y0": 240.0, "x1": 155.0, "y1": 255.0},
                                "link_mode": "visual_blocks",
                                "sources": ["pdf_text", "drawing_rects"],
                            },
                            {
                                "figure_id": "",
                                "label": "4",
                                "page": 9,
                                "image_path": "corpus/synthetic/1990_synthetic_test_paper/figures/figure-4-p009.png",
                                "caption_text": "Unprefixed caption text",
                                "figure_bbox": {
                                    "x0": 0.0,
                                    "y0": 0.0,
                                    "x1": 72.0,
                                    "y1": 36.0,
                                    "width": 72.0,
                                    "height": 36.0,
                                },
                                "caption_bbox": {"x0": 0.0, "y0": 40.0, "x1": 72.0, "y1": 55.0},
                                "link_mode": "column_gap_fallback",
                                "sources": ["heuristic_scope"],
                            },
                        ]
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            figures = extract_figures(paper_id, layout=layout)

            self.assertEqual(len(figures), 2)
            self.assertEqual(figures[0]["id"], "fig-2a")
            self.assertEqual(figures[0]["label"], "Figure 2A")
            self.assertEqual(figures[0]["caption"], "Boundary silhouette used for evaluation.")
            self.assertEqual(figures[0]["display_size_in"], {"width": 2.0, "height": 3.0})
            self.assertEqual(figures[0]["provenance"]["link_mode"], "visual_blocks")
            self.assertEqual(figures[0]["provenance"]["sources"], ["pdf_text", "drawing_rects"])
            self.assertEqual(figures[0]["review"]["status"], "unreviewed")
            self.assertEqual(figures[0]["review"]["risk"], "medium")

            self.assertEqual(figures[1]["id"], "fig-4")
            self.assertEqual(figures[1]["label"], "Figure 4")
            self.assertEqual(figures[1]["caption"], "Unprefixed caption text")
            self.assertEqual(figures[1]["display_size_in"], {"width": 1.0, "height": 0.5})


if __name__ == "__main__":
    unittest.main()
