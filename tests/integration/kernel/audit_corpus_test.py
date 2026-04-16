import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.audit_corpus import (
    _block_text,
    _caption_looks_noisy,
    _is_display_lead_in,
    _math_text_looks_contaminated,
    _section_title_looks_bad,
    _starts_like_paragraph_continuation,
    _text_looks_affiliation_like,
    _text_looks_algorithmic,
    _text_looks_heading_like,
    _text_looks_noisy,
    _text_looks_short_label_lead_in,
    audit_document,
)


def _review(risk: str = "medium", status: str = "unreviewed") -> dict[str, str]:
    return {"risk": risk, "status": status, "notes": ""}


class AuditCorpusTest(unittest.TestCase):
    def test_math_contamination_heuristic_distinguishes_prose_from_formula(self) -> None:
        self.assertTrue(_math_text_looks_contaminated("Figure 3 shows the result of the experiment"))
        self.assertFalse(_math_text_looks_contaminated(r"\frac{u-u_i}{u_{i+p}-u_i}"))

    def test_section_title_heuristic_rejects_sentence_like_headings(self) -> None:
        self.assertTrue(_section_title_looks_bad("2 This section is defined by a full sentence"))
        self.assertFalse(_section_title_looks_bad("2 Basis Functions"))

    def test_paragraph_continuation_heuristic_catches_lowercase_fragments(self) -> None:
        self.assertTrue(_starts_like_paragraph_continuation("geometric objects continue here"))
        self.assertFalse(_starts_like_paragraph_continuation("Geometric objects continue here"))

    def test_heading_like_text_heuristic_accepts_spaced_scan_heading(self) -> None:
        self.assertTrue(_text_looks_heading_like("2.3 T o l e r a n c e-B a s e d representation"))

    def test_short_label_lead_in_heuristic_accepts_where_colon(self) -> None:
        self.assertTrue(_text_looks_short_label_lead_in("where:"))

    def test_caption_noise_heuristic_allows_rich_typography(self) -> None:
        caption = (
            'Occluding contours — The 3D model “Origins of the Pig” © Keenan Crane is shown '
            'with diffuse shading; contour extraction remains stable.'
        )
        self.assertFalse(_text_looks_noisy(caption))

    def test_caption_noise_heuristic_allows_clean_subfigure_enumeration(self) -> None:
        caption = "(1) Type I; (2) type II; (3) type III; (4) type IV."

        self.assertFalse(_caption_looks_noisy(caption))

    def test_caption_noise_heuristic_allows_coordinate_caption(self) -> None:
        caption = "Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space."

        self.assertFalse(_caption_looks_noisy(caption))

    def test_caption_noise_heuristic_rejects_corrupted_glyph_caption(self) -> None:
        caption = (
            "Fig 18. (a) A portion of the lower bound construction for \u00b6 k) convex "
            "polyhedra with \u00b7 (n) total edges. (b) The same construction as viewed "
            "from the plane z = + \u00b8 \u00b9 \u00ba\u00bc\u00bbv\u00bd\u00bf\u00be\u00c1\u00c0 \u00ba z-axis."
        )

        self.assertTrue(_caption_looks_noisy(caption))

    def test_display_lead_in_heuristic_accepts_short_math_bridge(self) -> None:
        block = {
            "id": "blk-paragraph-1",
            "type": "paragraph",
            "content": {"spans": [{"kind": "text", "text": "and they are linearly independent, i.e.,"}]},
        }
        next_block = {"id": "blk-equation-1", "type": "display_equation_ref"}

        self.assertTrue(_is_display_lead_in(block, next_block))

    def test_display_lead_in_heuristic_accepts_long_colon_ended_bridge(self) -> None:
        block = {
            "id": "blk-paragraph-1",
            "type": "paragraph",
            "content": {
                "spans": [
                    {
                        "kind": "text",
                        "text": (
                            'giving the following sequence of "right-left" equivalent maps '
                            'because we compose the germ with diffeomorphisms on the right and left:'
                        ),
                    }
                ]
            },
        }
        next_block = {"id": "blk-equation-1", "type": "display_equation_ref"}

        self.assertTrue(_is_display_lead_in(block, next_block))

    def test_display_lead_in_heuristic_accepts_long_continuation_bridge(self) -> None:
        block = {
            "id": "blk-paragraph-1",
            "type": "paragraph",
            "content": {
                "spans": [
                    {
                        "kind": "text",
                        "text": (
                            "which are not independent, because clearly A 2 + B 2 + C 2 + D 2 = 1. "
                            "A rigid rotation of the surface is then given by"
                        ),
                    }
                ]
            },
        }
        next_block = {"id": "blk-equation-1", "type": "display_equation_ref"}

        self.assertTrue(_is_display_lead_in(block, next_block))

    def test_affiliation_and_algorithm_heuristics_catch_non_prose_neighbors(self) -> None:
        self.assertTrue(
            _text_looks_affiliation_like("Department of Electrical and Computer Engineering, The University of Arizona, Tucson, AZ 85721, USA")
        )
        self.assertTrue(_text_looks_algorithmic("Algorithm for contraction of entity-based aspect graph CONTRACT_EAG(EAG')"))
        self.assertTrue(_text_looks_algorithmic("return the one with minimal genus change"))
        self.assertTrue(_text_looks_algorithmic("for each Trim t in TrimList tl do if t contains newtrim then Insert(newtrim, t.trimlist)"))
        self.assertTrue(_text_looks_algorithmic("store it into the array"))

    def test_block_text_reads_algorithm_lines(self) -> None:
        block = {
            "id": "blk-algorithm-1",
            "type": "algorithm",
            "content": {"lines": ["Initialize EAG", "Remove Vi from V"]},
        }

        self.assertEqual(_block_text(block), "Initialize EAG Remove Vi from V")

    def test_audit_document_reports_core_canonical_failures(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [],
                "affiliations": [],
                "abstract_block_id": None,
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 This section is defined by a full sentence",
                    "level": 1,
                    "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This paragraph does not end cleanly"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "continues in the next block after Fig. 1 and cites Koenderink and van Doorn(1)",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(risk="high"),
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": "Figure 3 shows the result of the experiment",
                    "semantic_expr": None,
                    "compiled_targets": {},
                    "conversion": {"status": "unconverted", "notes": ""},
                    "source_spans": [],
                    "review": _review(risk="high"),
                }
            ],
            "figures": [],
            "references": [],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertGreater(result["score"], 0)
        self.assertEqual(issue_counts["missing_authors"], 1)
        self.assertEqual(issue_counts["missing_abstract"], 1)
        self.assertEqual(issue_counts["missing_figures"], 1)
        self.assertEqual(issue_counts["missing_references"], 1)
        self.assertEqual(issue_counts["bad_section_titles"], 1)
        self.assertEqual(issue_counts["fragmented_paragraphs"], 1)
        self.assertEqual(issue_counts["suspicious_math_entries"], 1)
        self.assertEqual(issue_counts["unconverted_display_math"], 1)
        self.assertEqual(result["counts"]["unconverted_display_math"], 1)

    def test_audit_document_does_not_flag_missing_figures_without_figure_cues(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {
                "created_at": "2026-04-15T00:00:00Z",
                "updated_at": "2026-04-15T00:00:00Z",
                "builder_version": "test",
                "sources": {
                    "native_pdf": True,
                    "layout_engine": "native",
                    "math_engine": "native",
                    "figure_engine": "native",
                    "text_engine": "native",
                },
                "flags": {
                    "use_external_layout": False,
                    "use_external_math": False,
                    "rebuild": False,
                },
            },
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                },
                {
                    "id": "sec-2",
                    "label": "2",
                    "title": "2 Discussion",
                    "level": 1,
                    "block_ids": ["blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This paper is purely mathematical exposition without figure references."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The discussion continues without any figure callouts."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference", "raw_text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("missing_figures", issue_counts)

    def test_audit_document_treats_placeholder_abstract_as_missing(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "Introduction",
                    "level": 1,
                    "block_ids": ["blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "[missing from original]"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Body paragraph."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [],
            "references": [],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertEqual(issue_counts["missing_abstract"], 1)

    def test_audit_document_flags_boilerplate_abstract_text(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "Introduction",
                    "level": 1,
                    "block_ids": ["blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "This is the accepted manuscript version of the following article: available online at example.com.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Body paragraph."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [],
            "references": [],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertEqual(issue_counts["bad_abstract"], 1)

    def test_audit_document_does_not_flag_missing_references_without_citation_cues(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Panel Paper",
            "source": {},
            "build": {
                "created_at": "2026-04-15T00:00:00Z",
                "updated_at": "2026-04-15T00:00:00Z",
                "builder_version": "test",
                "sources": {
                    "native_pdf": True,
                    "layout_engine": "native",
                    "math_engine": "native",
                    "figure_engine": "native",
                    "text_engine": "native",
                },
                "flags": {
                    "use_external_layout": False,
                    "use_external_math": False,
                    "rebuild": False,
                },
            },
            "front_matter": {
                "title": "Synthetic Panel Paper",
                "authors": [{"name": "Alice Example", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "A short discussion article."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "This panel report discusses indexing and scale, but it does not cite a formal bibliography.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [],
            "references": [],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("missing_references", issue_counts)

    def test_audit_document_ignores_raw_display_latex_paragraph_when_counting_fragments(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "4",
                    "title": "4 Criteria",
                    "level": 1,
                    "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": r"\begin{equation*} A C_{6}-70 a_{40} A C_{5} \tag{4.6} \end{equation*}"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "is equal to the non degenerate condition of ugly gulls singularity."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_ignores_mapsto_heavy_raw_display_latex_paragraph(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "2",
                    "title": "2 Normal Forms",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": r"y \mapsto y-\frac{1}{2}xy, \quad Z \mapsto 3Z, \quad x \mapsto \frac{1}{6}x",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": 'giving the following sequence of "right-left" equivalent maps because we compose on both sides:',
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_counts_converted_display_math(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-equation-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-equation-1",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"\frac{u-u_i}{u_{i+p}-u_i}",
                    "semantic_expr": None,
                    "compiled_targets": {"mathml": "<math />"},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "source_spans": [],
                    "review": _review(),
                }
            ],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertEqual(result["counts"]["converted_display_math"], 1)
        self.assertEqual(result["counts"]["unconverted_display_math"], 0)
        self.assertNotIn("unconverted_display_math", issue_counts)

    def test_audit_document_reports_formula_diagnostic_hits(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-equation-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-equation-1",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"\phi_{1}(s,)=\frac{X(s, t)}{W(s, t}",
                    "semantic_expr": None,
                    "compiled_targets": {},
                    "conversion": {"status": "failed", "notes": "latex2mathml: unexpected EOF"},
                    "source_spans": [],
                    "review": _review(risk="medium"),
                }
            ],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertEqual(issue_counts["formula_diagnostic_formulas"], 1)
        self.assertEqual(result["counts"]["formula_diagnostic_formulas"], 1)
        self.assertEqual(result["counts"]["high_severity_formula_diagnostics"], 1)

    def test_audit_document_tracks_formula_policies_and_semantic_ir(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-equation-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-equation-1",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"M(u)=u^d M_d + M_0",
                    "semantic_expr": {
                        "schema_version": "formula_semantic_expr/v1",
                        "category": "mapping",
                        "kind": "display",
                        "normalized_latex": r"M(u)=u^d M_d + M_0",
                        "symbols": ["M", "u", "d", "M_d", "M_0"],
                        "operators": ["eq", "add", "power"],
                    },
                    "compiled_targets": {"mathml": "<math />"},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "classification": {
                        "category": "mapping",
                        "semantic_policy": "semantic",
                        "role": "assertion",
                        "confidence": "medium",
                        "signals": ["mapping_tokens"],
                    },
                    "source_spans": [],
                    "review": _review(),
                }
            ],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure.", "image_path": "figures/fig-1.png", "bbox": {}, "display_size_in": {}, "review": _review()}],
            "references": [{"id": "ref-1", "label": "[1]", "raw_text": "Example reference", "text": "Example reference", "review": _review()}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        self.assertEqual(result["counts"]["semantic_formula_units"], 1)
        self.assertEqual(result["counts"]["semantic_expr_units"], 1)
        self.assertEqual(result["counts"]["missing_semantic_expr_units"], 0)
        self.assertEqual(result["formula_classification"]["categories"]["mapping"], 1)
        self.assertEqual(result["formula_classification"]["semantic_policies"]["semantic"], 1)

    def test_audit_document_flags_missing_semantic_ir_for_semantic_formula(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-equation-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-equation-1",
                    "type": "display_equation_ref",
                    "content": {"math_id": "math-1"},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [
                {
                    "id": "math-1",
                    "kind": "display",
                    "display_latex": r"s_k=q_k^T A q_k",
                    "semantic_expr": None,
                    "compiled_targets": {"mathml": "<math />"},
                    "conversion": {"status": "converted", "notes": "backend=latex2mathml"},
                    "classification": {
                        "category": "update_rule",
                        "semantic_policy": "semantic",
                        "role": "update_step",
                        "confidence": "medium",
                        "signals": ["update_rule_tokens"],
                    },
                    "source_spans": [],
                    "review": _review(),
                }
            ],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure.", "image_path": "figures/fig-1.png", "bbox": {}, "display_size_in": {}, "review": _review()}],
            "references": [{"id": "ref-1", "label": "[1]", "raw_text": "Example reference", "text": "Example reference", "review": _review()}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertEqual(result["counts"]["missing_semantic_expr_units"], 1)
        self.assertEqual(issue_counts["missing_semantic_expr"], 1)

    def test_audit_document_does_not_flag_figure_interrupted_prose_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-figure-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Artists frequently use line drawings to depict complex objects"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-figure-1",
                    "type": "figure_ref",
                    "content": {"text": ""},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "and the surrounding figure is referenced inline rather than splitting the prose badly."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_section_opener_after_heading_like_block(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "2.3",
                    "title": "2.3 Tolerance-Based Representation",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-heading-1", "blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-heading-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "2.3 T o l e r a n c e-B a s e d representation"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "define the epsilon region of an object as the subset of space."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_short_where_lead_in_as_fragment(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "4",
                    "title": "4 Test",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-signature-1", "blk-where-1", "blk-paragraph-1"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-signature-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "mapId() -> Status"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-where-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "where:"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The oldId has been mapped to more than one new ID."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Example figure."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_clause_and_display_lead_ins_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": [
                        "blk-abstract-1",
                        "blk-paragraph-1",
                        "blk-paragraph-2",
                        "blk-paragraph-3",
                        "blk-equation-1",
                    ],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Our main result is the following theorem:"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Then, the criteria are listed below."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-3",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "and they are linearly independent, i.e.,"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-equation-1",
                    "type": "display_equation_ref",
                    "content": {"text": ""},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_leading_inline_math_paragraph_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "3.2",
                    "title": "3.2 Test",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The relation between cells is described below"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {"kind": "inline_math_ref", "target_id": "math-inline-1"},
                            {"kind": "text", "text": " events. In Fig. 22, regions A and C comprise the viewing cell."},
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_affiliation_or_algorithm_spill_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "1",
                    "title": "1 Introduction",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2", "blk-paragraph-3", "blk-paragraph-4"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "Department of Electrical and Computer Engineering, The University of Arizona, Tucson, AZ 85721, USA",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "Therefore, an efficient viewer-centered representation of objects is desired.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-3",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "Algorithm for contraction of entity-based aspect graph CONTRACT_EAG(EAG')",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-4",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "determine the visibility of the entities in E for each element in V2",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_subcase_lead_in_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "3.1.1",
                    "title": "3.1.1 Test",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The sub-case hyperbolic-hyperbolic"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Thus also in this case the internal segment is locally active."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_standalone_result_statement_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "3",
                    "title": "3 Results",
                    "level": 1,
                    "block_ids": [
                        "blk-abstract-1",
                        "blk-paragraph-1",
                        "blk-paragraph-2",
                        "blk-paragraph-3",
                        "blk-paragraph-4",
                        "blk-paragraph-5",
                        "blk-paragraph-6",
                    ],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The visibility set is centrally convex. ■"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Then, the Gauss image is a great circle segment."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-3",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Proof: Without loss of generality, choose a cylindrical chart."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-4",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Since the two hemispheres provide the extreme locations"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-5",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Then, the visibility set is the same as the connecting arc."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-6",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Given the arc endpoints, the proof follows by monotonicity."}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_blame_long_continuation_after_short_fragment(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "3.1",
                    "title": "3.1 Test",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2", "blk-paragraph-3"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "The figure shows a mislabeled edge."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "curve of node eik"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-3",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "close to their original erroneous positions in order to reflect the design intent.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_glossary_entry_as_fragmented(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "6",
                    "title": "6 Discussion",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "The following abbreviations are used in this manuscript: 2D two-dimensional 3D three-dimensional CMM",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "coordinate measuring machine"}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_keeps_glossary_context_across_abbreviation_run(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "6",
                    "title": "6 Discussion",
                    "level": 1,
                    "block_ids": ["blk-abstract-1", "blk-paragraph-1", "blk-paragraph-2", "blk-paragraph-3"],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "Abbreviations The following abbreviations are used in this manuscript:",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "3DAP 3D annotation plane"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-3",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "coordinate measuring machine"}]},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [{"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."}],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)

    def test_audit_document_does_not_flag_figure_axis_label_as_fragmented_context(self) -> None:
        document = {
            "schema_version": "1.0",
            "paper_id": "test_kernel_paper",
            "title": "Synthetic Test Paper",
            "source": {},
            "build": {},
            "front_matter": {
                "title": "Synthetic Test Paper",
                "authors": [{"name": "Test Author", "affiliation_ids": ["aff-1"]}],
                "affiliations": [{"id": "aff-1", "department": "", "institution": "Test Lab", "address": ""}],
                "abstract_block_id": "blk-abstract-1",
                "funding_block_id": None,
            },
            "sections": [
                {
                    "id": "sec-1",
                    "label": "5.1",
                    "title": "5.1 Example",
                    "level": 1,
                    "block_ids": [
                        "blk-abstract-1",
                        "blk-figure-1",
                        "blk-paragraph-1",
                        "blk-paragraph-2",
                        "blk-figure-2",
                    ],
                    "children": [],
                    "source_spans": [],
                }
            ],
            "blocks": [
                {
                    "id": "blk-abstract-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "This abstract is present."}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-figure-1",
                    "type": "figure_ref",
                    "content": {"figure_id": "fig-1"},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-1",
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": "Polynomial degree"}]},
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-paragraph-2",
                    "type": "paragraph",
                    "content": {
                        "spans": [
                            {
                                "kind": "text",
                                "text": "the integration of the system matrices requires many quadrature points.",
                            }
                        ]
                    },
                    "source_spans": [],
                    "review": _review(),
                },
                {
                    "id": "blk-figure-2",
                    "type": "figure_ref",
                    "content": {"figure_id": "fig-2"},
                    "source_spans": [],
                    "review": _review(),
                },
            ],
            "math": [],
            "figures": [
                {"id": "fig-1", "label": "Figure 1", "caption": "Line drawing example."},
                {"id": "fig-2", "label": "Figure 2", "caption": "Quadrature plot."},
            ],
            "references": [{"id": "ref-1", "label": "[1]", "text": "Example reference"}],
            "styles": {
                "document_style": {},
                "category_styles": {},
                "block_styles": {},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "canonical.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            result = audit_document(path)

        issue_counts = {issue["key"]: issue["count"] for issue in result["issues"]}
        self.assertNotIn("fragmented_paragraphs", issue_counts)


if __name__ == "__main__":
    unittest.main()
