from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.audit import audit_acquisition_quality
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


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionAuditTest(unittest.TestCase):
    def test_audit_acquisition_quality_reports_route_provider_and_ocr_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())

            required_dir = layout.canonical_sources_dir("1990_required_ocr")
            recommended_dir = layout.canonical_sources_dir("1991_recommended_ocr")
            missing_dir = layout.canonical_sources_dir("1992_missing_sidecars")
            layout.canonical_path("1990_required_ocr").parent.mkdir(parents=True, exist_ok=True)
            layout.canonical_path("1990_required_ocr").write_text("{}", encoding="utf-8")
            layout.canonical_path("1991_recommended_ocr").parent.mkdir(parents=True, exist_ok=True)
            layout.canonical_path("1991_recommended_ocr").write_text("{}", encoding="utf-8")
            missing_dir.mkdir(parents=True, exist_ok=True)

            _write_json(
                required_dir / "acquisition-route.json",
                {
                    "primary_route": "scan_or_image_heavy",
                    "ocr_prepass": {"policy": "required", "should_run": True, "tool": "ocrmypdf"},
                },
            )
            _write_json(
                required_dir / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "docling",
                    "recommended_primary_math_provider": "mathpix",
                    "layout_recommendation_basis": "fallback_unaccepted",
                    "math_recommendation_basis": "accepted",
                    "providers": [
                        {
                            "provider": "docling",
                            "kind": "layout",
                            "accepted": False,
                            "rejection_reasons": ["score_below_threshold"],
                        },
                        {
                            "provider": "mathpix",
                            "kind": "math",
                            "accepted": True,
                            "rejection_reasons": [],
                        },
                    ],
                },
            )
            _write_json(
                required_dir / "ocr-prepass.json",
                {
                    "ocr_prepass_policy": "required",
                    "ocr_prepass_tool": "ocrmypdf",
                    "ocr_prepass_applied": False,
                    "pdf_source_kind": "original",
                },
            )
            _write_json(
                required_dir / "acquisition-execution.json",
                {
                    "executed": {
                        "selected_layout_provider": "docling",
                        "selected_math_provider": "mathpix",
                    }
                },
            )

            _write_json(
                recommended_dir / "acquisition-route.json",
                {
                    "primary_route": "degraded_or_garbled",
                    "ocr_prepass": {"policy": "recommended", "should_run": True, "tool": "ocrmypdf"},
                },
            )
            _write_json(
                recommended_dir / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "mathpix",
                    "recommended_primary_math_provider": "mathpix",
                    "layout_recommendation_basis": "accepted",
                    "math_recommendation_basis": "accepted",
                    "providers": [
                        {
                            "provider": "mathpix",
                            "kind": "layout",
                            "accepted": True,
                            "rejection_reasons": [],
                        }
                    ],
                },
            )
            _write_json(
                recommended_dir / "ocr-prepass.json",
                {
                    "ocr_prepass_policy": "recommended",
                    "ocr_prepass_tool": "ocrmypdf",
                    "ocr_prepass_applied": True,
                    "pdf_source_kind": "ocr_normalized_generated",
                },
            )
            _write_json(
                recommended_dir / "acquisition-execution.json",
                {
                    "executed": {
                        "selected_layout_provider": "mathpix",
                        "selected_math_provider": "mathpix",
                    }
                },
            )

            report = audit_acquisition_quality(layout=layout)

        self.assertEqual(report["paper_count"], 3)
        self.assertEqual(report["canonical_count"], 2)
        self.assertEqual(report["missing_canonical_count"], 1)
        self.assertEqual(report["route_counts"]["scan_or_image_heavy"], 1)
        self.assertEqual(report["route_counts"]["degraded_or_garbled"], 1)
        self.assertEqual(report["recommended_layout_provider_counts"]["docling"], 1)
        self.assertEqual(report["recommended_layout_provider_counts"]["mathpix"], 1)
        self.assertEqual(report["layout_recommendation_basis_counts"]["fallback_unaccepted"], 1)
        self.assertEqual(report["layout_recommendation_basis_counts"]["accepted"], 1)
        self.assertEqual(report["math_recommendation_basis_counts"]["accepted"], 2)
        self.assertEqual(report["executed_layout_provider_counts"]["docling"], 1)
        self.assertEqual(report["executed_layout_provider_counts"]["mathpix"], 1)
        self.assertEqual(report["ocr_policy_counts"]["required"], 1)
        self.assertEqual(report["ocr_policy_counts"]["recommended"], 1)
        self.assertEqual(report["pdf_source_kind_counts"]["original"], 1)
        self.assertEqual(report["pdf_source_kind_counts"]["ocr_normalized_generated"], 1)
        self.assertEqual(report["provider_rejection_reason_counts"]["score_below_threshold"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["acquisition-route.json"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["source-scorecard.json"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["ocr-prepass.json"], 1)
        self.assertEqual(report["ocr_summary"]["should_run_count"], 2)
        self.assertEqual(report["ocr_summary"]["applied_count"], 1)
        self.assertEqual(report["ocr_summary"]["required_not_applied_count"], 1)
        self.assertEqual(report["ocr_summary"]["recommended_not_applied_count"], 0)

        papers = {paper["paper_id"]: paper for paper in report["papers"]}
        self.assertIn("required_ocr_not_applied", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("fallback_recommendation", papers["1990_required_ocr"]["issue_flags"])
        self.assertEqual(papers["1991_recommended_ocr"]["pdf_source_kind"], "ocr_normalized_generated")
        self.assertEqual(papers["1990_required_ocr"]["executed_layout_provider"], "docling")
        self.assertEqual(papers["1990_required_ocr"]["layout_recommendation_basis"], "fallback_unaccepted")
        self.assertEqual(
            papers["1990_required_ocr"]["rejected_providers"][0]["rejection_reasons"],
            ["score_below_threshold"],
        )
        self.assertTrue(papers["1991_recommended_ocr"]["has_execution_report"])
        self.assertEqual(
            papers["1992_missing_sidecars"]["missing_sidecars"],
            ["acquisition-route.json", "source-scorecard.json", "ocr-prepass.json"],
        )


if __name__ == "__main__":
    unittest.main()
