from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.assembly.canonical_builder import build_canonical_document


class CanonicalBuilderTest(unittest.TestCase):
    def test_build_canonical_document_builds_metadata_applies_policy_and_reannotates_math(self) -> None:
        compile_inputs: list[list[dict[str, object]]] = []
        classify_inputs: list[list[dict[str, object]]] = []
        semantic_inputs: list[list[dict[str, object]]] = []

        def fake_compile(entries):
            compile_inputs.append(list(entries))
            return [{**entry, "compiled": True} for entry in entries]

        def fake_classify(entries):
            classify_inputs.append(list(entries))
            return [{**entry, "classified": True} for entry in entries]

        def fake_semantic(entries):
            semantic_inputs.append(list(entries))
            return [{**entry, "semantic": True} for entry in entries]

        def fake_apply_policy(document):
            updated = dict(document)
            updated["blocks"] = [*document["blocks"], {"id": "blk-policy"}]
            updated["math"] = [*document["math"], {"id": "math-policy"}]
            return updated

        with (
            patch("pipeline.assembly.canonical_builder.compile_formulas", side_effect=fake_compile),
            patch("pipeline.assembly.canonical_builder.annotate_formula_classifications", side_effect=fake_classify),
            patch("pipeline.assembly.canonical_builder.annotate_formula_semantic_expr", side_effect=fake_semantic),
            patch(
                "pipeline.assembly.canonical_builder.build_metadata_for_paper",
                return_value={"fingerprint": "fp-123", "layout_engine": "docling"},
            ) as build_metadata,
            patch("pipeline.assembly.canonical_builder.apply_document_policy", side_effect=fake_apply_policy),
        ):
            document = build_canonical_document(
                paper_id="1990_synthetic_test_paper",
                title="Synthetic Test Paper",
                source={"pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf", "page_count": 1, "page_sizes_pt": []},
                timestamp="2026-04-19T00:00:00Z",
                layout_engine_name="docling",
                math_engine_name="mathpix",
                effective_text_engine="native_pdf+pdftotext",
                front_matter={"title": "Synthetic Test Paper"},
                sections=[{"id": "sec-1"}],
                blocks=[{"id": "blk-1"}],
                math_entries=[{"id": "math-1"}],
                figures=[{"id": "fig-1"}],
                references=[{"id": "ref-1"}],
                decision_artifacts={"abstract": {"source": "leading_abstract_section_created"}},
            )

        self.assertEqual(len(compile_inputs), 2)
        self.assertEqual(compile_inputs[0], [{"id": "math-1"}])
        self.assertEqual(document["build"], {"fingerprint": "fp-123", "layout_engine": "docling"})
        self.assertEqual(document["schema_version"], "1.0")
        self.assertEqual(document["_decision_artifacts"]["abstract"]["source"], "leading_abstract_section_created")
        self.assertEqual(document["blocks"][-1]["id"], "blk-policy")
        self.assertEqual(document["math"][-1]["id"], "math-policy")
        self.assertTrue(all(entry.get("semantic") for entry in document["math"]))
        build_metadata.assert_called_once_with(
            "1990_synthetic_test_paper",
            pdf_path="1990_synthetic_test_paper/1990_synthetic_test_paper.pdf",
            timestamp="2026-04-19T00:00:00Z",
            layout_engine="docling",
            math_engine="mathpix",
            figure_engine="local",
            text_engine="native_pdf+pdftotext",
        )

    def test_build_canonical_document_omits_decision_artifacts_when_not_present(self) -> None:
        with (
            patch("pipeline.assembly.canonical_builder.compile_formulas", side_effect=lambda entries: list(entries)),
            patch("pipeline.assembly.canonical_builder.annotate_formula_classifications", side_effect=lambda entries: list(entries)),
            patch("pipeline.assembly.canonical_builder.annotate_formula_semantic_expr", side_effect=lambda entries: list(entries)),
            patch("pipeline.assembly.canonical_builder.build_metadata_for_paper", return_value={"fingerprint": "fp-456"}),
            patch("pipeline.assembly.canonical_builder.apply_document_policy", side_effect=lambda document: document),
        ):
            document = build_canonical_document(
                paper_id="1990_synthetic_test_paper",
                title="Synthetic Test Paper",
                source={"pdf_path": "1990_synthetic_test_paper/1990_synthetic_test_paper.pdf", "page_count": 1, "page_sizes_pt": []},
                timestamp="2026-04-19T00:00:00Z",
                layout_engine_name="native_pdf",
                math_engine_name="heuristic",
                effective_text_engine="native_pdf",
                front_matter={"title": "Synthetic Test Paper"},
                sections=[],
                blocks=[],
                math_entries=[],
                figures=[],
                references=[],
                decision_artifacts=None,
            )

        self.assertNotIn("_decision_artifacts", document)
        self.assertEqual(document["math"], [])


if __name__ == "__main__":
    unittest.main()
