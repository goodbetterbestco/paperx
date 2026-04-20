from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator.round_execution import run_paper_job


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


class RoundExecutionTest(unittest.TestCase):
    def test_run_paper_job_refreshes_existing_fresh_canonical_without_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            canonical_target = layout.canonical_path("1990_synthetic_test_paper")
            existing_document = {
                "build": {"sources": {"layout_engine": "docling"}},
                "front_matter": {},
                "sections": [],
                "blocks": [],
                "math": [],
                "figures": [],
                "references": [],
            }

            result = run_paper_job(
                "1990_synthetic_test_paper",
                force_rebuild=False,
                layout=layout,
                now_iso_impl=lambda: "2026-04-19T00:00:00Z",
                canonical_path_impl=lambda paper_id, *, layout=None: canonical_target,
                load_json_if_exists_impl=lambda path: existing_document,
                existing_composed_sources_impl=lambda paper_id, *, layout=None: {"layout_engine": "docling", "ocr_prepass_policy": "skip"},
                desired_flags_for_existing_paper_impl=lambda document, composed: {"needs_refresh": False},
                detect_canonical_staleness_impl=lambda path, *, desired_flags: {"stale": False, "reasons": []},
                write_canonical_outputs_impl=lambda paper_id, document, *, layout=None: {"canonical_path": str(canonical_target)},
                anomaly_flags_impl=lambda document: ["weak_sections"],
                build_extraction_sources_for_paper_impl=lambda *args, **kwargs: (_ for _ in ()).throw(
                    AssertionError("fresh canonical path should not rebuild extraction sources")
                ),
            )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["mode"], "fresh_canonical")
            self.assertTrue(result["skipped_fresh"])
            self.assertFalse(result["forced_rebuild"])
            self.assertEqual(result["build_sources"], {"layout_engine": "docling"})
            self.assertEqual(result["anomalies"], ["weak_sections"])
            self.assertEqual(result["docling"], {"layout_blocks": 0, "math_entries": 0})
            self.assertEqual(result["mathpix"], {"present": False, "math_entries": 0})
            self.assertEqual(result["composed_sources"]["ocr_prepass_policy"], "skip")

    def test_run_paper_job_rebuilds_from_extracted_sources_and_records_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            canonical_target = layout.canonical_path("1990_synthetic_test_paper")
            document = {
                "build": {"sources": {"layout_engine": "composed", "math_engine": "mathpix"}},
                "front_matter": {},
                "sections": [{"id": "sec-1"}],
                "blocks": [],
                "math": [],
                "figures": [],
                "references": [],
            }

            result = run_paper_job(
                "1990_synthetic_test_paper",
                force_rebuild=True,
                layout=layout,
                now_iso_impl=lambda: "2026-04-19T00:10:00Z",
                canonical_path_impl=lambda paper_id, *, layout=None: canonical_target,
                load_json_if_exists_impl=lambda path: {"front_matter": {"generated_abstract": "old"}},
                existing_composed_sources_impl=lambda paper_id, *, layout=None: {"layout_engine": "docling", "ocr_prepass_policy": "recommended"},
                desired_flags_for_existing_paper_impl=lambda document, composed: {"needs_refresh": True},
                detect_canonical_staleness_impl=lambda path, *, desired_flags: {"stale": True, "reasons": ["pipeline_fingerprint_changed"]},
                build_extraction_sources_for_paper_impl=lambda paper_id, *, prefetched_mathpix_future=None, layout=None: (
                    {"layout": {"blocks": [{"id": "docling-1"}]}, "math": {"entries": [{"id": "eq-1"}]}},
                    {"math_entries": 3},
                    {"docling_seconds": 1.2, "mathpix_seconds": 2.4},
                ),
                compose_external_sources_impl=lambda paper_id, *, docling_sources, mathpix_sources, layout=None: {
                    "layout_engine": "composed",
                    "math_engine": "mathpix",
                    "ocr_prepass_policy": "recommended",
                    "ocr_prepass_should_run": True,
                    "ocr_prepass_tool": "ocrmypdf",
                },
                build_paper_impl=lambda paper_id, *, layout=None: {
                    "mode": "layout_plus_mathpix",
                    "attempts": ["layout_only", "layout_plus_mathpix"],
                    "document": document,
                },
                write_canonical_outputs_impl=lambda paper_id, new_document, *, layout=None: {
                    "canonical_path": str(canonical_target),
                    "references": 0,
                    "figures": 0,
                },
                anomaly_flags_impl=lambda new_document: [],
            )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["mode"], "layout_plus_mathpix")
            self.assertFalse(result["skipped_fresh"])
            self.assertTrue(result["forced_rebuild"])
            self.assertEqual(result["docling"], {"layout_blocks": 1, "math_entries": 1})
            self.assertEqual(result["mathpix"], {"present": True, "math_entries": 3})
            self.assertEqual(
                result["composed_sources"],
                {
                    "layout_engine": "composed",
                    "math_engine": "mathpix",
                    "ocr_prepass_policy": "recommended",
                    "ocr_prepass_should_run": True,
                    "ocr_prepass_tool": "ocrmypdf",
                },
            )
            self.assertEqual(result["attempts"], ["layout_only", "layout_plus_mathpix"])
            self.assertEqual(result["prebuild_staleness"]["reasons"], ["pipeline_fingerprint_changed"])
            self.assertEqual(result["build_sources"], {"layout_engine": "composed", "math_engine": "mathpix"})
            self.assertIn("build_seconds", result["timings"])
            self.assertIn("compose_sources_seconds", result["timings"])

    def test_run_paper_job_reports_failures_with_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())

            result = run_paper_job(
                "1990_synthetic_test_paper",
                force_rebuild=True,
                layout=layout,
                now_iso_impl=lambda: "2026-04-19T00:20:00Z",
                canonical_path_impl=lambda paper_id, *, layout=None: layout.canonical_path(paper_id),
                load_json_if_exists_impl=lambda path: None,
                existing_composed_sources_impl=lambda paper_id, *, layout=None: {},
                desired_flags_for_existing_paper_impl=lambda document, composed: {},
                detect_canonical_staleness_impl=lambda path, *, desired_flags: {"stale": True, "reasons": ["forced"]},
                build_extraction_sources_for_paper_impl=lambda *args, **kwargs: (_ for _ in ()).throw(
                    RuntimeError("synthetic extraction failure")
                ),
            )

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["error"], "synthetic extraction failure")
            self.assertIn("RuntimeError: synthetic extraction failure", result["traceback"])


if __name__ == "__main__":
    unittest.main()
