import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.run_corpus_rounds import (
    _MathpixRoundCoordinator,
    _anomaly_flags,
    _assert_mathpix_dns_available,
    _build_paper,
    _compose_external_sources,
    _desired_flags_for_existing_paper,
    _mathpix_submit_workers,
    _process_round,
    _preserve_existing_generated_abstract,
    _preserve_existing_generated_abstract_file,
    _render_final_report,
    _summarize_round,
)


class RunCorpusRoundsTest(unittest.TestCase):
    def test_mathpix_dns_preflight_resolves_host(self) -> None:
        with patch("paper_pipeline.run_corpus_rounds.socket.getaddrinfo", return_value=[object()]):
            _assert_mathpix_dns_available()

    def test_mathpix_dns_preflight_fails_with_sandbox_guidance(self) -> None:
        with patch(
            "paper_pipeline.run_corpus_rounds.socket.getaddrinfo",
            side_effect=socket.gaierror(8, "nodename nor servname provided, or not known"),
        ):
            with self.assertRaises(SystemExit) as ctx:
                _assert_mathpix_dns_available()
        message = str(ctx.exception)
        self.assertIn("Mathpix DNS preflight failed for api.mathpix.com", message)
        self.assertIn("sandboxed environment", message)
        self.assertIn("escalated network access", message)

    def test_mathpix_submit_workers_defaults_to_twenty(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STEPVIEW_MATHPIX_SUBMIT_WORKERS", None)
            self.assertEqual(_mathpix_submit_workers(), 20)

    def test_mathpix_submit_workers_is_not_capped_by_max_workers(self) -> None:
        with patch.dict(os.environ, {"STEPVIEW_MATHPIX_SUBMIT_WORKERS": "12"}, clear=False):
            self.assertEqual(_mathpix_submit_workers(), 12)

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

    def test_anomaly_flags_treat_missing_placeholder_as_missing_abstract(self) -> None:
        document = {
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [{"id": "sec-1"}, {"id": "sec-2"}],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                }
            ],
            "references": [],
            "figures": [],
        }

        self.assertEqual(_anomaly_flags(document), ["missing_abstract"])

    def test_compose_external_sources_prefers_mathpix_page_one_when_it_scores_better(self) -> None:
        captured: dict[str, dict] = {}

        def capture(path: Path, payload: dict) -> None:
            captured[path.name] = payload

        docling_sources = {
            "layout": {
                "engine": "docling",
                "pdf_path": "docs/synthetic.pdf",
                "page_count": 2,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [
                    {"id": "d1", "page": 1, "order": 1, "role": "front_matter", "text": "This is the accepted manuscript version of the following article:", "bbox": {}, "meta": {}},
                    {"id": "d2", "page": 2, "order": 1, "role": "paragraph", "text": "Page two body.", "bbox": {}, "meta": {}},
                ],
            },
            "math": {"engine": "docling", "entries": []},
        }
        mathpix_sources = {
            "layout": {
                "engine": "mathpix",
                "pdf_path": "docs/synthetic.pdf",
                "page_count": 2,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [
                    {"id": "m1", "page": 1, "order": 1, "role": "paragraph", "text": "Abstract", "bbox": {}, "meta": {}},
                    {"id": "m2", "page": 1, "order": 2, "role": "paragraph", "text": "A real abstract paragraph.", "bbox": {}, "meta": {}},
                    {"id": "m3", "page": 1, "order": 3, "role": "paragraph", "text": "1. Introduction", "bbox": {}, "meta": {}},
                ],
            },
            "math": {"engine": "mathpix", "entries": [{"id": "math-1"}]},
        }

        with (
            patch("paper_pipeline.run_corpus_rounds._write_json", side_effect=capture),
            patch("paper_pipeline.run_corpus_rounds.external_layout_path", return_value=Path("/tmp/layout.json")),
            patch("paper_pipeline.run_corpus_rounds.external_math_path", return_value=Path("/tmp/math.json")),
        ):
            summary = _compose_external_sources(
                "synthetic_test_paper",
                docling_sources=docling_sources,
                mathpix_sources=mathpix_sources,
            )

        self.assertEqual(summary["layout_engine"], "composed")
        self.assertEqual(summary["math_engine"], "mathpix")
        layout_blocks = captured["layout.json"]["blocks"]
        page_one_texts = [block["text"] for block in layout_blocks if block["page"] == 1]
        page_two_texts = [block["text"] for block in layout_blocks if block["page"] == 2]
        self.assertEqual(page_one_texts, ["Abstract", "A real abstract paragraph.", "1. Introduction"])
        self.assertEqual(page_two_texts, ["Page two body."])

    def test_compose_external_sources_keeps_docling_page_one_on_score_tie(self) -> None:
        captured: dict[str, dict] = {}

        def capture(path: Path, payload: dict) -> None:
            captured[path.name] = payload

        docling_sources = {
            "layout": {
                "engine": "docling",
                "pdf_path": "docs/synthetic.pdf",
                "page_count": 1,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [
                    {"id": "d1", "page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Title", "bbox": {}, "meta": {}},
                    {"id": "d2", "page": 1, "order": 2, "role": "front_matter", "text": "Alice Example", "bbox": {}, "meta": {}},
                    {"id": "d3", "page": 1, "order": 3, "role": "front_matter", "text": "A coherent abstract paragraph.", "bbox": {}, "meta": {}},
                ],
            },
            "math": {"engine": "docling", "entries": []},
        }
        mathpix_sources = {
            "layout": {
                "engine": "mathpix",
                "pdf_path": "docs/synthetic.pdf",
                "page_count": 1,
                "page_sizes_pt": [{"page": 1, "width": 600.0, "height": 800.0}],
                "blocks": [
                    {"id": "m1", "page": 1, "order": 1, "role": "paragraph", "text": "Synthetic", "bbox": {}, "meta": {}},
                    {"id": "m2", "page": 1, "order": 2, "role": "paragraph", "text": "Title", "bbox": {}, "meta": {}},
                    {"id": "m3", "page": 1, "order": 3, "role": "paragraph", "text": "A coherent", "bbox": {}, "meta": {}},
                    {"id": "m4", "page": 1, "order": 4, "role": "paragraph", "text": "summary paragraph.", "bbox": {}, "meta": {}},
                ],
            },
            "math": {"engine": "mathpix", "entries": []},
        }

        with (
            patch("paper_pipeline.run_corpus_rounds._write_json", side_effect=capture),
            patch("paper_pipeline.run_corpus_rounds.external_layout_path", return_value=Path("/tmp/layout.json")),
            patch("paper_pipeline.run_corpus_rounds.external_math_path", return_value=Path("/tmp/math.json")),
        ):
            _compose_external_sources(
                "synthetic_test_paper",
                docling_sources=docling_sources,
                mathpix_sources=mathpix_sources,
            )

        layout_blocks = captured["layout.json"]["blocks"]
        self.assertEqual([block["id"] for block in layout_blocks], ["d1", "d2", "d3"])

    def test_build_paper_prefers_cleaner_later_candidate(self) -> None:
        bad_document = {
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [{"id": "sec-1"}, {"id": "sec-2"}],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This is the accepted manuscript version of the following article:"}]},
                }
            ],
            "references": [{"id": "ref-1"}],
            "figures": [],
        }
        good_document = {
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [{"id": "sec-1"}, {"id": "sec-2"}],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "A short and valid abstract about the paper."}]},
                }
            ],
            "references": [{"id": "ref-1"}],
            "figures": [],
        }

        with (
            patch("paper_pipeline.run_corpus_rounds.reconcile_paper", side_effect=[bad_document, good_document]),
            patch("paper_pipeline.run_corpus_rounds.validate_canonical"),
        ):
            result = _build_paper("synthetic_test_paper")

        self.assertEqual(result["mode"], "layout_only")
        self.assertEqual(result["document"], good_document)
        self.assertEqual(result["anomalies"], [])

    def test_preserve_existing_generated_abstract_copies_prior_generated_text(self) -> None:
        existing_document = {
            "front_matter": {
                "abstract_block_id": "blk-abstract-old",
            },
            "blocks": [
                {
                    "id": "blk-abstract-old",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "[Generated abstract from paper content.] A preserved generated abstract.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "alternates": [],
                    "review": {
                        "status": "edited",
                        "risk": "low",
                        "notes": "Generated abstract from paper content; original abstract unavailable in source PDF.",
                    },
                }
            ],
        }
        new_document = {
            "front_matter": {
                "abstract_block_id": "blk-abstract-new",
            },
            "blocks": [
                {
                    "id": "blk-abstract-new",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                    "source_spans": [],
                    "alternates": [],
                    "review": {"status": "edited", "risk": "low", "notes": "[missing from original]"},
                }
            ],
        }

        preserved = _preserve_existing_generated_abstract(existing_document, new_document)

        self.assertTrue(preserved)
        self.assertEqual(
            new_document["blocks"][0]["content"]["spans"][0]["text"],
            "[Generated abstract from paper content.] A preserved generated abstract.",
        )
        self.assertEqual(
            new_document["blocks"][0]["review"]["notes"],
            "Generated abstract from paper content; original abstract unavailable in source PDF.",
        )

    def test_preserve_existing_generated_abstract_file_copies_prior_text(self) -> None:
        existing_document = {
            "front_matter": {
                "abstract_block_id": "blk-abstract-old",
            },
            "blocks": [
                {
                    "id": "blk-abstract-old",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "A manually curated abstract that should survive regeneration.",
                            }
                        ]
                    },
                    "source_spans": [{"page": 1, "span_id": "orig"}],
                    "alternates": [],
                    "review": {
                        "status": "edited",
                        "risk": "low",
                        "notes": "Generated abstract from paper content; original abstract unavailable in source PDF.",
                    },
                }
            ],
        }
        new_document = {
            "front_matter": {
                "abstract_block_id": "blk-abstract-new",
            },
            "blocks": [
                {
                    "id": "blk-abstract-new",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "A newly extracted abstract."}]},
                    "source_spans": [],
                    "alternates": [],
                    "review": {"status": "unreviewed", "risk": "medium", "notes": ""},
                }
            ],
        }

        with patch("paper_pipeline.run_corpus_rounds._paper_has_generated_abstract_file", return_value=True):
            preserved = _preserve_existing_generated_abstract_file("synthetic_test_paper", existing_document, new_document)

        self.assertTrue(preserved)
        self.assertEqual(
            new_document["blocks"][0]["content"]["spans"][0]["text"],
            "A manually curated abstract that should survive regeneration.",
        )
        self.assertEqual(
            new_document["blocks"][0]["review"]["notes"],
            "Generated abstract from paper content; original abstract unavailable in source PDF.",
        )

    def test_round_summary_counts_prebuild_staleness(self) -> None:
        round_status = {
            "papers": {
                "paper-a": {
                    "status": "completed",
                    "anomalies": ["missing_figures"],
                    "skipped_fresh": True,
                    "prebuild_staleness": {
                        "stale": True,
                        "reasons": ["pipeline_fingerprint_changed", "pdf_input_changed"],
                    },
                },
                "paper-b": {
                    "status": "completed",
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
        self.assertEqual(summary["queued_count"], 0)
        self.assertEqual(summary["running_count"], 0)
        self.assertEqual(summary["stale_before_build_count"], 1)
        self.assertEqual(summary["fresh_skip_count"], 1)
        self.assertEqual(summary["stale_reasons"]["pipeline_fingerprint_changed"], 1)
        self.assertEqual(summary["stale_reasons"]["pdf_input_changed"], 1)

    def test_process_round_force_rebuild_requeues_ok_papers(self) -> None:
        status = {
            "papers": ["paper-a", "paper-b"],
            "rounds": {
                "round_1": {
                    "started_at": "2026-04-14T00:00:00Z",
                    "completed_at": "2026-04-14T00:05:00Z",
                    "papers": {
                        "paper-a": {"status": "completed", "completed_at": "2026-04-14T00:01:00Z"},
                        "paper-b": {"status": "completed", "completed_at": "2026-04-14T00:02:00Z"},
                    },
                }
            },
        }

        def fake_run_paper_job(paper_id: str, *, force_rebuild: bool, prefetched_mathpix_future=None) -> dict:
            return {
                "status": "completed",
                "completed_at": "2026-04-14T00:10:00Z",
                "forced_rebuild": force_rebuild,
                "paper_id": paper_id,
            }

        with (
            patch("paper_pipeline.run_corpus_rounds._mathpix_credentials_available", return_value=False),
            patch("paper_pipeline.run_corpus_rounds._run_paper_job", side_effect=fake_run_paper_job),
            patch("paper_pipeline.run_corpus_rounds._save_status"),
        ):
            _process_round(status, 1, max_workers=2, force_rebuild=True)

        round_status = status["rounds"]["round_1"]["papers"]
        self.assertTrue(round_status["paper-a"]["forced_rebuild"])
        self.assertTrue(round_status["paper-b"]["forced_rebuild"])
        self.assertEqual(round_status["paper-a"]["paper_id"], "paper-a")
        self.assertEqual(round_status["paper-b"]["paper_id"], "paper-b")
        self.assertNotEqual(status["rounds"]["round_1"]["started_at"], "2026-04-14T00:00:00Z")
        self.assertIsNotNone(status["rounds"]["round_1"]["completed_at"])
        self.assertTrue(status["rounds"]["round_1"]["force_rebuild"])

    def test_final_report_mentions_running_papers(self) -> None:
        status = {
            "started_at": "2026-04-14T00:00:00Z",
            "updated_at": "2026-04-14T00:05:00Z",
            "papers": ["paper-a", "paper-b"],
            "rounds": {
                "round_1": {
                    "started_at": "2026-04-14T00:00:00Z",
                    "completed_at": None,
                    "papers": {
                        "paper-a": {
                            "status": "running",
                            "started_at": "2026-04-14T00:01:00Z",
                        },
                        "paper-b": {
                            "status": "completed",
                            "metrics": {"sections": 4, "references": 3, "figures": 2},
                            "anomalies": [],
                            "prebuild_staleness": {"stale": False, "reasons": []},
                        },
                    },
                }
            },
            "notes": [],
        }

        report = _render_final_report(status)

        self.assertIn("- Running: 1", report)
        self.assertIn("running (started 2026-04-14T00:01:00Z)", report)

    def test_final_report_mentions_queued_mathpix_phase(self) -> None:
        status = {
            "started_at": "2026-04-14T00:00:00Z",
            "updated_at": "2026-04-14T00:05:00Z",
            "papers": ["paper-a"],
            "rounds": {
                "round_1": {
                    "started_at": "2026-04-14T00:00:00Z",
                    "completed_at": None,
                    "papers": {
                        "paper-a": {
                            "status": "queued",
                            "mathpix": {"phase": "submitted"},
                        }
                    },
                }
            },
            "notes": [],
        }

        report = _render_final_report(status)

        self.assertIn("- Queued: 1", report)
        self.assertIn("queued (mathpix submitted)", report)

    def test_mathpix_round_coordinator_publishes_phase_updates(self) -> None:
        events: list[tuple[str, dict[str, object]]] = []

        def callback(paper_id: str, payload: dict[str, object]) -> None:
            events.append((paper_id, payload))

        with (
            patch("paper_pipeline.run_corpus_rounds.submit_mathpix_pdf", return_value="pdf-123"),
            patch("paper_pipeline.run_corpus_rounds.fetch_mathpix_pdf_status", return_value={"status": "completed"}),
            patch("paper_pipeline.run_corpus_rounds.download_mathpix_pdf", return_value={"pdf_id": "pdf-123", "pages": []}),
        ):
            coordinator = _MathpixRoundCoordinator(
                ["paper-a"],
                submit_workers=1,
                poll_seconds=1.0,
                status_callback=callback,
            )
            coordinator.start()
            result = coordinator.future_for("paper-a").result(timeout=3)
            coordinator.close()

        self.assertEqual(result["pdf_id"], "pdf-123")
        phases = [payload["mathpix"]["phase"] for _, payload in events if "mathpix" in payload]
        self.assertIn("submit_queued", phases)
        self.assertIn("submitted", phases)
        self.assertIn("polling", phases)
        self.assertIn("completed", phases)

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
                            "status": "completed",
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

    def test_final_report_uses_only_present_round_columns(self) -> None:
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
                            "status": "completed",
                            "metrics": {"sections": 4, "references": 3, "figures": 2},
                            "anomalies": [],
                            "prebuild_staleness": {"stale": False, "reasons": []},
                        }
                    },
                }
            },
            "notes": [],
        }

        report = _render_final_report(status)

        self.assertIn("# Canonical Corpus Report", report)
        self.assertIn("| Paper | Round 1 |", report)
        self.assertNotIn("| Paper | Round 1 | Round 2 |", report)

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
