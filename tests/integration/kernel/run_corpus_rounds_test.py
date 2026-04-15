import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.run_corpus_rounds import (
    _anomaly_flags,
    _desired_flags_for_existing_paper,
    _render_final_report,
    _summarize_round,
)


class RunCorpusRoundsTest(unittest.TestCase):
    def test_anomaly_flags_require_reference_and_figure_expectation(self) -> None:
        document = {
            "front_matter": {
                "title": "Synthetic Panel Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [{"id": "sec-1"}],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "A short discussion article."}]},
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "This panel report discusses indexing and scale without figures or a formal bibliography.",
                            }
                        ]
                    },
                },
            ],
            "references": [],
            "figures": [],
        }

        self.assertEqual(_anomaly_flags(document), ["weak_sections"])

    def test_round_summary_counts_prebuild_staleness(self) -> None:
        round_status = {
            "papers": {
                "paper-a": {
                    "status": "ok",
                    "anomalies": ["missing_figures"],
                    "skipped_fresh": True,
                    "prebuild_staleness": {
                        "stale": True,
                        "reasons": ["pipeline_fingerprint_changed", "pdf_input_changed"],
                    },
                },
                "paper-b": {
                    "status": "ok",
                    "anomalies": [],
                    "prebuild_staleness": {
                        "stale": False,
                        "reasons": [],
                    },
                },
            }
        }

        summary = _summarize_round(round_status)

        self.assertEqual(summary["success_count"], 2)
        self.assertEqual(summary["stale_before_build_count"], 1)
        self.assertEqual(summary["fresh_skip_count"], 1)
        self.assertEqual(summary["stale_reasons"]["pipeline_fingerprint_changed"], 1)
        self.assertEqual(summary["stale_reasons"]["pdf_input_changed"], 1)

    def test_final_report_mentions_stale_reasons(self) -> None:
        status = {
            "started_at": "2026-04-14T00:00:00Z",
            "updated_at": "2026-04-14T00:05:00Z",
            "papers": ["paper-a"],
            "rounds": {
                "round_1": {
                    "started_at": "2026-04-14T00:00:00Z",
                    "completed_at": "2026-04-14T00:05:00Z",
                    "papers": {
                        "paper-a": {
                            "status": "ok",
                            "metrics": {"sections": 4, "references": 3, "figures": 2},
                            "anomalies": [],
                            "skipped_fresh": True,
                            "prebuild_staleness": {
                                "stale": True,
                                "reasons": ["pipeline_fingerprint_changed"],
                            },
                        }
                    },
                }
            },
            "notes": [],
        }

        report = _render_final_report(status)

        self.assertIn("Stale before rebuild: 1", report)
        self.assertIn("Fresh canonical skips: 1", report)
        self.assertIn("Common stale reasons:", report)
        self.assertIn("`pipeline_fingerprint_changed`: 1", report)
        self.assertIn("stale-before-build", report)
        self.assertIn("fresh-skip", report)

    def test_existing_paper_flags_keep_required_external_sources(self) -> None:
        document = {
            "build": {
                "flags": {
                    "use_external_layout": True,
                    "use_external_math": False,
                }
            }
        }
        composed_sources = {
            "layout_blocks": 0,
            "math_entries": 7,
        }

        flags = _desired_flags_for_existing_paper(document, composed_sources)

        self.assertEqual(
            flags,
            {
                "use_external_layout": True,
                "use_external_math": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
