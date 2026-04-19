from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.backfill import backfill_acquisition_sidecars
from pipeline.corpus_layout import ProjectLayout


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        mode="corpus",
        corpus_name="synthetic",
        project_dir=None,
        corpus_root=corpus_root,
        source_root=corpus_root,
        review_root=corpus_root / "review_drafts",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


class AcquisitionBackfillTest(unittest.TestCase):
    def test_backfill_writes_missing_sidecars_without_overwriting_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            sources_dir = layout.canonical_sources_dir(paper_id)
            sources_dir.mkdir(parents=True, exist_ok=True)
            existing_route = sources_dir / "acquisition-route.json"
            existing_route.write_text(json.dumps({"primary_route": "existing"}) + "\n", encoding="utf-8")

            report = backfill_acquisition_sidecars(
                layout=layout,
                overwrite=False,
                paper_ids=[paper_id],
                build_acquisition_route_report_impl=lambda current_paper_id, *, layout=None: {
                    "paper_id": current_paper_id,
                    "primary_route": "math_dense",
                    "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
                },
                load_docling_layout_impl=lambda current_paper_id, *, layout=None: {
                    "engine": "docling",
                    "page_count": 1,
                    "blocks": [
                        {"page": 1, "order": 1, "role": "front_matter", "text": "Title"},
                        {"page": 1, "order": 2, "role": "reference", "text": "[1] Ref"},
                    ],
                },
                load_mathpix_layout_impl=lambda current_paper_id, *, layout=None: None,
                load_external_layout_impl=lambda current_paper_id, *, layout=None: None,
                load_docling_math_impl=lambda current_paper_id, *, layout=None: {
                    "engine": "docling",
                    "entries": [{"id": "eq-1", "kind": "display"}],
                },
                load_mathpix_math_impl=lambda current_paper_id, *, layout=None: None,
                load_external_math_impl=lambda current_paper_id, *, layout=None: None,
                load_grobid_metadata_observation_impl=lambda current_paper_id, *, layout=None: {
                    "provider": "grobid",
                    "title": "Title",
                    "abstract": "A clean abstract.",
                    "references": ["Author. Journal of Tests. 2024."],
                },
                ocr_normalized_pdf_path_impl=lambda current_paper_id, *, layout=None: sources_dir / "ocr-normalized.pdf",
            )

            self.assertEqual(report["paper_count"], 1)
            self.assertFalse(report["papers"][0]["route_written"])
            self.assertTrue(report["papers"][0]["scorecard_written"])
            self.assertTrue(report["papers"][0]["ocr_report_written"])
            self.assertEqual(report["updated"]["acquisition-route.json"], 0)
            self.assertEqual(report["updated"]["source-scorecard.json"], 1)
            self.assertEqual(report["updated"]["ocr-prepass.json"], 1)

            scorecard = json.loads((sources_dir / "source-scorecard.json").read_text(encoding="utf-8"))
            self.assertEqual(scorecard["recommended_primary_layout_provider"], "docling")
            self.assertEqual(scorecard["recommended_primary_math_provider"], "docling")
            self.assertEqual(scorecard["recommended_primary_metadata_provider"], "grobid")
            self.assertEqual(scorecard["recommended_primary_reference_provider"], "grobid")

            ocr_report = json.loads((sources_dir / "ocr-prepass.json").read_text(encoding="utf-8"))
            self.assertEqual(ocr_report["ocr_prepass_policy"], "skip")
            self.assertFalse(ocr_report["ocr_prepass_applied"])
            self.assertEqual(json.loads(existing_route.read_text(encoding="utf-8"))["primary_route"], "existing")

    def test_backfill_reports_failures_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            layout.canonical_sources_dir("ok-paper").mkdir(parents=True, exist_ok=True)
            layout.canonical_sources_dir("bad-paper").mkdir(parents=True, exist_ok=True)

            report = backfill_acquisition_sidecars(
                layout=layout,
                overwrite=False,
                paper_ids=["ok-paper", "bad-paper"],
                build_acquisition_route_report_impl=lambda current_paper_id, *, layout=None: (
                    {"paper_id": current_paper_id, "primary_route": "born_digital_scholarly", "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None}}
                    if current_paper_id != "bad-paper"
                    else (_ for _ in ()).throw(FileNotFoundError("missing pdf"))
                ),
                load_docling_layout_impl=lambda current_paper_id, *, layout=None: None,
                load_mathpix_layout_impl=lambda current_paper_id, *, layout=None: None,
                load_external_layout_impl=lambda current_paper_id, *, layout=None: None,
                load_docling_math_impl=lambda current_paper_id, *, layout=None: None,
                load_mathpix_math_impl=lambda current_paper_id, *, layout=None: None,
                load_external_math_impl=lambda current_paper_id, *, layout=None: None,
                load_grobid_metadata_observation_impl=lambda current_paper_id, *, layout=None: None,
                ocr_normalized_pdf_path_impl=lambda current_paper_id, *, layout=None: layout.canonical_sources_dir(current_paper_id) / "ocr-normalized.pdf",
            )

            self.assertEqual(report["failure_count"], 1)
            self.assertEqual(report["failures"][0]["paper_id"], "bad-paper")
            self.assertTrue((layout.canonical_sources_dir("ok-paper") / "acquisition-route.json").exists())
            self.assertFalse((layout.canonical_sources_dir("bad-paper") / "acquisition-route.json").exists())


if __name__ == "__main__":
    unittest.main()
