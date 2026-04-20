from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.policy_feedback import summarize_acquisition_policy_feedback
from pipeline.cli.summarize_acquisition_policy_feedback import (
    run_summarize_acquisition_policy_feedback_cli,
)


def _sample_audit_report() -> dict[str, object]:
    return {
        "generated_at": "2026-04-20T12:00:00Z",
        "paper_count": 4,
        "remediation_queue": [
            {"paper_id": "paper-a"},
            {"paper_id": "paper-b"},
        ],
        "follow_up_action_counts": {
            "trial_layout_provider": 2,
            "trial_math_provider": 1,
            "escalate_grobid_metadata": 1,
            "manual_review_references": 1,
        },
        "provider_rejection_reason_counts": {
            "score_below_threshold": 3,
        },
        "metadata_suppressed_reason_counts": {
            "metadata_provider_not_accepted": 1,
        },
        "reference_suppressed_reason_counts": {
            "reference_provider_not_accepted": 1,
        },
        "sidecar_missing_counts": {
            "acquisition-route.json": 2,
            "ocr-prepass.json": 1,
        },
        "papers": [
            {
                "paper_id": "paper-a",
                "issue_flags": ["required_ocr_not_applied", "follow_up_recommended"],
                "follow_up_actions": [
                    {"action": "trial_layout_provider", "target_provider": "mathpix"},
                    {"action": "trial_math_provider", "target_provider": "mathpix"},
                ],
                "remediation_priority_reasons": ["required_ocr_not_applied", "follow_up_actions"],
                "metadata_suppressed_reason": "",
                "reference_suppressed_reason": "",
                "rejected_providers": [
                    {"provider": "docling", "kind": "layout", "rejection_reasons": ["score_below_threshold"]}
                ],
            },
            {
                "paper_id": "paper-b",
                "issue_flags": ["fallback_recommendation", "metadata_application_suppressed"],
                "follow_up_actions": [
                    {"action": "trial_layout_provider", "target_provider": "mathpix"},
                    {"action": "escalate_grobid_metadata", "target_provider": "grobid"},
                ],
                "remediation_priority_reasons": ["fallback_recommendation", "follow_up_actions"],
                "metadata_suppressed_reason": "metadata_provider_not_accepted",
                "reference_suppressed_reason": "",
                "rejected_providers": [
                    {"provider": "docling", "kind": "layout", "rejection_reasons": ["score_below_threshold"]}
                ],
            },
            {
                "paper_id": "paper-c",
                "issue_flags": ["reference_application_suppressed"],
                "follow_up_actions": [
                    {"action": "manual_review_references", "target_provider": None},
                ],
                "remediation_priority_reasons": [],
                "metadata_suppressed_reason": "",
                "reference_suppressed_reason": "reference_provider_not_accepted",
                "rejected_providers": [
                    {"provider": "docling", "kind": "layout", "rejection_reasons": ["score_below_threshold"]}
                ],
            },
            {
                "paper_id": "paper-d",
                "issue_flags": [],
                "follow_up_actions": [],
                "remediation_priority_reasons": [],
                "metadata_suppressed_reason": "",
                "reference_suppressed_reason": "",
                "rejected_providers": [],
            },
        ],
    }


class AcquisitionPolicyFeedbackTest(unittest.TestCase):
    def test_summarize_policy_feedback_ranks_actions_from_audit_signals(self) -> None:
        report = summarize_acquisition_policy_feedback(_sample_audit_report(), source_path="/tmp/audit.json")

        self.assertEqual(report["paper_count"], 4)
        self.assertEqual(report["remediation_queue_count"], 2)
        self.assertEqual(report["follow_up_paper_count"], 3)
        self.assertEqual(report["suppressed_application_paper_count"], 2)
        self.assertEqual(report["ocr_gap_paper_count"], 1)
        self.assertEqual(report["signal_counts"]["issue_flag_counts"]["required_ocr_not_applied"], 1)
        self.assertEqual(report["signal_counts"]["remediation_priority_reason_counts"]["follow_up_actions"], 2)
        actions = {item["action"]: item for item in report["policy_actions"]}
        self.assertIn("tighten_ocr_execution_defaults", actions)
        self.assertIn("tighten_provider_acceptance_thresholds", actions)
        self.assertIn("stabilize_metadata_ownership", actions)
        self.assertIn("stabilize_reference_ownership", actions)
        self.assertIn("enforce_acquisition_sidecar_generation", actions)
        self.assertGreater(actions["tighten_provider_acceptance_thresholds"]["priority_score"], 0)
        self.assertEqual(actions["stabilize_metadata_ownership"]["category"], "metadata")
        self.assertTrue(actions["enforce_acquisition_sidecar_generation"]["evidence"])

    def test_ocr_gap_paper_count_counts_unique_papers(self) -> None:
        sample = _sample_audit_report()
        papers = list(sample["papers"])
        papers[0] = {
            **papers[0],
            "issue_flags": [
                "required_ocr_not_applied",
                "recommended_ocr_not_applied",
            ],
        }
        sample["papers"] = papers

        report = summarize_acquisition_policy_feedback(sample)

        self.assertEqual(report["ocr_gap_paper_count"], 1)
        self.assertEqual(report["signal_counts"]["issue_flag_counts"]["required_ocr_not_applied"], 1)
        self.assertEqual(report["signal_counts"]["issue_flag_counts"]["recommended_ocr_not_applied"], 1)

    def test_cli_writes_reports_and_prints_markdown(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "policy_feedback"
            json_path = output_dir / "policy_feedback.json"
            markdown_path = output_dir / "policy_feedback.md"
            exit_code = run_summarize_acquisition_policy_feedback_cli(
                argparse.Namespace(from_report=None, format="markdown"),
                audit_acquisition_quality_fn=lambda **_: _sample_audit_report(),
                current_layout_fn=lambda: object(),
                output_dir=output_dir,
                json_report_path=json_path,
                markdown_report_path=markdown_path,
                print_fn=printed.append,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["paper_count"], 4)
        self.assertIn("# Acquisition Policy Feedback", printed[0])
        self.assertIn("tighten_provider_acceptance_thresholds", printed[0])
        self.assertIn("Signal Summary", printed[0])

    def test_cli_can_load_saved_audit_report(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "audit.json"
            source_path.write_text(json.dumps(_sample_audit_report(), indent=2) + "\n", encoding="utf-8")
            output_dir = root / "policy_feedback"
            exit_code = run_summarize_acquisition_policy_feedback_cli(
                argparse.Namespace(from_report=str(source_path), format="json"),
                output_dir=output_dir,
                json_report_path=output_dir / "policy_feedback.json",
                markdown_report_path=output_dir / "policy_feedback.md",
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(printed[0])
        self.assertEqual(payload["source_report_path"], str(source_path.resolve()))
        self.assertIn("policy_actions", payload)


if __name__ == "__main__":
    unittest.main()
