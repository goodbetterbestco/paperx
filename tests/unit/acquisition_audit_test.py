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
        review_root=corpus_root / "_canon",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class AcquisitionAuditTest(unittest.TestCase):
    def test_audit_acquisition_quality_discovers_source_state_root_pdfs_in_corpus_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            layout.corpus_root.mkdir(parents=True, exist_ok=True)
            (layout.corpus_root / "1990_root_pdf_only.pdf").write_bytes(b"%PDF-1.4\n")

            report = audit_acquisition_quality(layout=layout)

        self.assertEqual(report["paper_count"], 1)
        self.assertEqual(report["canonical_count"], 0)
        self.assertEqual(report["missing_canonical_count"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["acquisition-route.json"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["source-scorecard.json"], 1)
        self.assertEqual(report["sidecar_missing_counts"]["ocr-prepass.json"], 1)
        self.assertEqual(report["papers"][0]["paper_id"], "1990_root_pdf_only")
        self.assertEqual(
            report["papers"][0]["missing_sidecars"],
            ["acquisition-route.json", "source-scorecard.json", "ocr-prepass.json"],
        )

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
                    "recommended_primary_metadata_provider": "grobid",
                    "recommended_primary_reference_provider": "docling",
                    "layout_recommendation_basis": "fallback_unaccepted",
                    "math_recommendation_basis": "accepted",
                    "metadata_recommendation_basis": "accepted",
                    "reference_recommendation_basis": "accepted",
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
                        "metadata_provider": "grobid",
                        "reference_provider": "docling",
                    },
                    "follow_up": {
                        "needs_attention": True,
                        "actions": [
                            {
                                "product": "metadata",
                                "reason": "metadata_provider_not_accepted",
                                "action": "escalate_grobid_metadata",
                                "target_provider": "grobid",
                            },
                            {
                                "product": "references",
                                "reason": "reference_provider_not_accepted",
                                "action": "manual_review_references",
                                "target_provider": None,
                            },
                        ],
                    },
                    "promotion": {
                        "label": "trial-mathpix",
                        "promoted_at": "2026-04-19T01:00:00Z",
                    },
                },
            )
            _write_json(
                required_dir / "trials" / "trial-mathpix" / "acquisition-execution.json",
                {
                    "trial": {
                        "label": "trial-mathpix",
                        "applied_at": "2026-04-19T00:30:00Z",
                    }
                },
            )
            _write_json(
                required_dir / "metadata-decision.json",
                {
                    "provider": "grobid",
                    "reference_provider": "docling",
                    "title_applied": False,
                    "abstract_applied": False,
                    "references_applied": False,
                    "title_suppressed_reason": "metadata_provider_not_accepted",
                    "abstract_suppressed_reason": "metadata_provider_not_accepted",
                    "references_suppressed_reason": "reference_provider_not_accepted",
                    "reference_count": 2,
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
                    "recommended_primary_metadata_provider": "grobid",
                    "recommended_primary_reference_provider": "grobid",
                    "layout_recommendation_basis": "accepted",
                    "math_recommendation_basis": "accepted",
                    "metadata_recommendation_basis": "accepted",
                    "reference_recommendation_basis": "accepted",
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
                        "metadata_provider": "grobid",
                        "reference_provider": "grobid",
                    },
                    "follow_up": {
                        "needs_attention": False,
                        "actions": [],
                    },
                },
            )
            _write_json(
                recommended_dir / "metadata-decision.json",
                {
                    "provider": "grobid",
                    "reference_provider": "grobid",
                    "title_applied": True,
                    "abstract_applied": True,
                    "references_applied": True,
                    "reference_count": 5,
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
        self.assertEqual(report["recommended_metadata_provider_counts"]["grobid"], 2)
        self.assertEqual(report["recommended_reference_provider_counts"]["docling"], 1)
        self.assertEqual(report["recommended_reference_provider_counts"]["grobid"], 1)
        self.assertEqual(report["layout_recommendation_basis_counts"]["fallback_unaccepted"], 1)
        self.assertEqual(report["layout_recommendation_basis_counts"]["accepted"], 1)
        self.assertEqual(report["math_recommendation_basis_counts"]["accepted"], 2)
        self.assertEqual(report["metadata_recommendation_basis_counts"]["accepted"], 2)
        self.assertEqual(report["reference_recommendation_basis_counts"]["accepted"], 2)
        self.assertEqual(report["executed_layout_provider_counts"]["docling"], 1)
        self.assertEqual(report["executed_layout_provider_counts"]["mathpix"], 1)
        self.assertEqual(report["executed_metadata_provider_counts"]["grobid"], 2)
        self.assertEqual(report["executed_reference_provider_counts"]["docling"], 1)
        self.assertEqual(report["executed_reference_provider_counts"]["grobid"], 1)
        self.assertEqual(report["follow_up_needed_counts"]["needs_attention"], 1)
        self.assertEqual(report["follow_up_needed_counts"]["no_follow_up"], 2)
        self.assertEqual(report["follow_up_action_counts"]["escalate_grobid_metadata"], 1)
        self.assertEqual(report["follow_up_action_counts"]["manual_review_references"], 1)
        self.assertEqual(report["follow_up_target_provider_counts"]["grobid"], 1)
        self.assertEqual(report["active_promoted_trial_counts"]["trial-mathpix"], 1)
        self.assertEqual(report["latest_applied_trial_counts"]["trial-mathpix"], 1)
        self.assertEqual(report["metadata_application_counts"]["applied"], 1)
        self.assertEqual(report["metadata_application_counts"]["not_applied"], 2)
        self.assertEqual(report["reference_application_counts"]["applied"], 1)
        self.assertEqual(report["reference_application_counts"]["not_applied"], 2)
        self.assertEqual(report["metadata_suppressed_reason_counts"]["metadata_provider_not_accepted"], 1)
        self.assertEqual(report["reference_suppressed_reason_counts"]["reference_provider_not_accepted"], 1)
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
        self.assertEqual(report["remediation_priority_counts"], {})
        self.assertEqual(report["remediation_queue"], [])

        papers = {paper["paper_id"]: paper for paper in report["papers"]}
        self.assertIn("required_ocr_not_applied", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("fallback_recommendation", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("metadata_application_suppressed", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("reference_application_suppressed", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("follow_up_recommended", papers["1990_required_ocr"]["issue_flags"])
        self.assertIn("trial_promoted", papers["1990_required_ocr"]["issue_flags"])
        self.assertEqual(papers["1991_recommended_ocr"]["pdf_source_kind"], "ocr_normalized_generated")
        self.assertEqual(papers["1990_required_ocr"]["executed_layout_provider"], "docling")
        self.assertEqual(papers["1990_required_ocr"]["executed_metadata_provider"], "grobid")
        self.assertEqual(papers["1990_required_ocr"]["executed_reference_provider"], "docling")
        self.assertTrue(papers["1990_required_ocr"]["follow_up_needed"])
        self.assertEqual(papers["1990_required_ocr"]["active_promoted_trial_label"], "trial-mathpix")
        self.assertEqual(papers["1990_required_ocr"]["latest_applied_trial_label"], "trial-mathpix")
        self.assertIsNone(papers["1990_required_ocr"]["remediation_command"])
        self.assertIsNone(papers["1990_required_ocr"]["remediation_priority_label"])
        self.assertIsNone(papers["1990_required_ocr"]["remediation_priority_score"])
        self.assertEqual(papers["1990_required_ocr"]["remediation_priority_reasons"], [])
        self.assertEqual(papers["1990_required_ocr"]["follow_up_actions"][0]["action"], "escalate_grobid_metadata")
        self.assertFalse(papers["1990_required_ocr"]["metadata_applied"])
        self.assertFalse(papers["1990_required_ocr"]["references_applied"])
        self.assertEqual(
            papers["1990_required_ocr"]["metadata_suppressed_reason"],
            "metadata_provider_not_accepted",
        )
        self.assertEqual(
            papers["1990_required_ocr"]["reference_suppressed_reason"],
            "reference_provider_not_accepted",
        )
        self.assertEqual(papers["1990_required_ocr"]["layout_recommendation_basis"], "fallback_unaccepted")
        self.assertEqual(
            papers["1990_required_ocr"]["rejected_providers"][0]["rejection_reasons"],
            ["score_below_threshold"],
        )
        self.assertTrue(papers["1991_recommended_ocr"]["has_execution_report"])
        self.assertIsNone(papers["1991_recommended_ocr"]["remediation_command"])
        self.assertEqual(
            papers["1992_missing_sidecars"]["missing_sidecars"],
            ["acquisition-route.json", "source-scorecard.json", "ocr-prepass.json"],
        )

    def test_audit_acquisition_quality_emits_remediation_command_for_actionable_follow_up(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1993_actionable_follow_up"
            sources_dir = layout.canonical_sources_dir(paper_id)
            layout.canonical_path(paper_id).parent.mkdir(parents=True, exist_ok=True)
            layout.canonical_path(paper_id).write_text("{}", encoding="utf-8")

            _write_json(
                sources_dir / "acquisition-route.json",
                {
                    "primary_route": "born_digital_scholarly",
                    "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
                },
            )
            _write_json(
                sources_dir / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "docling",
                    "recommended_primary_math_provider": "docling",
                    "layout_recommendation_basis": "fallback_unaccepted",
                    "math_recommendation_basis": "fallback_unaccepted",
                },
            )
            _write_json(
                sources_dir / "ocr-prepass.json",
                {
                    "ocr_prepass_policy": "skip",
                    "ocr_prepass_tool": None,
                    "ocr_prepass_applied": False,
                    "pdf_source_kind": "original",
                },
            )
            _write_json(
                sources_dir / "acquisition-execution.json",
                {
                    "executed": {
                        "selected_layout_provider": "docling",
                        "selected_math_provider": "docling",
                    },
                    "follow_up": {
                        "needs_attention": True,
                        "actions": [
                            {
                                "product": "layout",
                                "reason": "layout_provider_not_accepted",
                                "action": "trial_layout_provider",
                                "target_provider": "mathpix",
                            },
                            {
                                "product": "math",
                                "reason": "math_provider_not_accepted",
                                "action": "trial_math_provider",
                                "target_provider": "mathpix",
                            },
                        ],
                    },
                },
            )

            report = audit_acquisition_quality(layout=layout)

        papers = {paper["paper_id"]: paper for paper in report["papers"]}
        self.assertEqual(
            papers[paper_id]["remediation_command"],
            f"python3 -m pipeline.cli.remediate_acquisition_follow_up {paper_id} --label trial-mathpix",
        )
        self.assertEqual(len(report["remediation_queue"]), 1)
        self.assertEqual(report["remediation_queue"][0]["paper_id"], paper_id)
        self.assertEqual(report["remediation_queue"][0]["issue_count"], papers[paper_id]["issue_count"])
        self.assertEqual(report["remediation_queue"][0]["primary_route"], "born_digital_scholarly")
        self.assertEqual(
            report["remediation_queue"][0]["remediation_command"],
            papers[paper_id]["remediation_command"],
        )
        self.assertEqual(report["remediation_priority_counts"]["high"], 1)
        self.assertEqual(papers[paper_id]["remediation_priority_label"], "high")
        self.assertEqual(papers[paper_id]["remediation_priority_score"], 5)
        self.assertEqual(
            papers[paper_id]["remediation_priority_reasons"],
            ["fallback_recommendation", "follow_up_actions"],
        )
        self.assertEqual(report["remediation_queue"][0]["remediation_priority_label"], "high")
        self.assertEqual(report["remediation_queue"][0]["remediation_priority_score"], 5)
        self.assertEqual(
            report["remediation_queue"][0]["follow_up_actions"],
            papers[paper_id]["follow_up_actions"],
        )

    def test_audit_acquisition_quality_sorts_remediation_queue_by_priority_then_issue_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())

            critical_id = "1994_critical_follow_up"
            high_id = "1995_high_follow_up"

            critical_sources = layout.canonical_sources_dir(critical_id)
            high_sources = layout.canonical_sources_dir(high_id)
            layout.canonical_path(critical_id).parent.mkdir(parents=True, exist_ok=True)
            layout.canonical_path(critical_id).write_text("{}", encoding="utf-8")
            layout.canonical_path(high_id).parent.mkdir(parents=True, exist_ok=True)
            layout.canonical_path(high_id).write_text("{}", encoding="utf-8")

            _write_json(
                critical_sources / "acquisition-route.json",
                {
                    "primary_route": "scan_or_image_heavy",
                    "ocr_prepass": {"policy": "required", "should_run": True, "tool": "ocrmypdf"},
                },
            )
            _write_json(
                critical_sources / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "docling",
                    "recommended_primary_math_provider": "mathpix",
                    "layout_recommendation_basis": "accepted",
                    "math_recommendation_basis": "accepted",
                },
            )
            _write_json(
                critical_sources / "ocr-prepass.json",
                {
                    "ocr_prepass_policy": "required",
                    "ocr_prepass_tool": "ocrmypdf",
                    "ocr_prepass_applied": False,
                    "pdf_source_kind": "original",
                },
            )
            _write_json(
                critical_sources / "acquisition-execution.json",
                {
                    "executed": {
                        "selected_layout_provider": "docling",
                        "selected_math_provider": "mathpix",
                    },
                    "follow_up": {
                        "needs_attention": True,
                        "actions": [
                            {
                                "product": "layout",
                                "action": "trial_layout_provider",
                                "target_provider": "mathpix",
                            }
                        ],
                    },
                },
            )

            _write_json(
                high_sources / "acquisition-route.json",
                {
                    "primary_route": "born_digital_scholarly",
                    "ocr_prepass": {"policy": "skip", "should_run": False, "tool": None},
                },
            )
            _write_json(
                high_sources / "source-scorecard.json",
                {
                    "recommended_primary_layout_provider": "docling",
                    "recommended_primary_math_provider": "docling",
                    "layout_recommendation_basis": "fallback_unaccepted",
                    "math_recommendation_basis": "fallback_unaccepted",
                },
            )
            _write_json(
                high_sources / "ocr-prepass.json",
                {
                    "ocr_prepass_policy": "skip",
                    "ocr_prepass_tool": None,
                    "ocr_prepass_applied": False,
                    "pdf_source_kind": "original",
                },
            )
            _write_json(
                high_sources / "acquisition-execution.json",
                {
                    "executed": {
                        "selected_layout_provider": "docling",
                        "selected_math_provider": "docling",
                    },
                    "follow_up": {
                        "needs_attention": True,
                        "actions": [
                            {
                                "product": "layout",
                                "action": "trial_layout_provider",
                                "target_provider": "mathpix",
                            },
                            {
                                "product": "math",
                                "action": "trial_math_provider",
                                "target_provider": "mathpix",
                            },
                        ],
                    },
                },
            )

            report = audit_acquisition_quality(layout=layout)

        self.assertEqual(
            [item["paper_id"] for item in report["remediation_queue"]],
            [critical_id, high_id],
        )
        self.assertEqual(report["remediation_queue"][0]["remediation_priority_label"], "critical")
        self.assertEqual(report["remediation_queue"][1]["remediation_priority_label"], "high")
        self.assertEqual(report["remediation_priority_counts"]["critical"], 1)
        self.assertEqual(report["remediation_priority_counts"]["high"], 1)


if __name__ == "__main__":
    unittest.main()
