import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.staleness_policy import (
    build_input_fingerprints,
    build_metadata_for_paper,
    detect_canonical_staleness,
    detect_document_staleness,
    fingerprint_path,
    pipeline_fingerprint,
)


class StalenessPolicyTest(unittest.TestCase):
    def test_pipeline_fingerprint_uses_stable_component_ids(self) -> None:
        fingerprint = pipeline_fingerprint()

        self.assertIn("pipeline/reconcile_blocks.py", fingerprint["modules"])
        self.assertIn("pipeline/formula_semantic_ir.py", fingerprint["modules"])
        self.assertIn("legacy_path_fingerprint", fingerprint["compatibility"])
        self.assertIn("paper_pipeline_fingerprint", fingerprint["compatibility"])

    def test_document_with_matching_inputs_and_pipeline_is_not_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            metadata = build_metadata_for_paper(
                "test_paper",
                pdf_path=pdf_path,
                timestamp="2026-04-14T00:00:00Z",
                layout_engine="native_pdf",
                math_engine="heuristic",
                figure_engine="local",
                text_engine="native_pdf",
                use_external_layout=False,
                use_external_math=False,
            )
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": metadata,
            }

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": False},
                current_inputs=build_input_fingerprints(
                    "test_paper",
                    pdf_path=pdf_path,
                    use_external_layout=False,
                    use_external_math=False,
                ),
                current_pipeline=pipeline_fingerprint(),
            )

            self.assertFalse(result["stale"])
            self.assertEqual(result["reasons"], [])

    def test_legacy_pipeline_fingerprint_is_still_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            current_pipeline = pipeline_fingerprint()
            metadata = build_metadata_for_paper(
                "test_paper",
                pdf_path=pdf_path,
                timestamp="2026-04-15T00:00:00Z",
                layout_engine="native_pdf",
                math_engine="heuristic",
                figure_engine="local",
                text_engine="native_pdf",
                use_external_layout=False,
                use_external_math=False,
            )
            metadata["pipeline"]["fingerprint"] = current_pipeline["compatibility"]["legacy_path_fingerprint"]
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": metadata,
            }

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": False},
                current_inputs=build_input_fingerprints(
                    "test_paper",
                    pdf_path=pdf_path,
                    use_external_layout=False,
                    use_external_math=False,
                ),
                current_pipeline=current_pipeline,
            )

            self.assertFalse(result["stale"])
            self.assertEqual(result["reasons"], [])

    def test_paper_pipeline_component_fingerprint_is_still_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            current_pipeline = pipeline_fingerprint()
            metadata = build_metadata_for_paper(
                "test_paper",
                pdf_path=pdf_path,
                timestamp="2026-04-15T00:00:00Z",
                layout_engine="native_pdf",
                math_engine="heuristic",
                figure_engine="local",
                text_engine="native_pdf",
                use_external_layout=False,
                use_external_math=False,
            )
            metadata["pipeline"]["fingerprint"] = current_pipeline["compatibility"]["paper_pipeline_fingerprint"]
            metadata["pipeline"]["modules"] = {
                module_id.replace("pipeline/", "paper_pipeline/", 1): module_hash
                for module_id, module_hash in metadata["pipeline"]["modules"].items()
            }
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": metadata,
            }

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": False},
                current_inputs=build_input_fingerprints(
                    "test_paper",
                    pdf_path=pdf_path,
                    use_external_layout=False,
                    use_external_math=False,
                ),
                current_pipeline=current_pipeline,
            )

            self.assertFalse(result["stale"])
            self.assertEqual(result["reasons"], [])

    def test_document_without_stale_metadata_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": {
                    "created_at": "2026-04-14T00:00:00Z",
                    "updated_at": "2026-04-14T00:00:00Z",
                    "builder_version": "0.1.0",
                    "sources": {
                        "native_pdf": True,
                        "layout_engine": "native_pdf",
                        "math_engine": "heuristic",
                        "figure_engine": "local",
                        "text_engine": "native_pdf",
                    },
                    "flags": {
                        "use_external_layout": False,
                        "use_external_math": False,
                        "rebuild": False,
                    },
                },
            }

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": False},
                current_inputs=build_input_fingerprints(
                    "test_paper",
                    pdf_path=pdf_path,
                    use_external_layout=False,
                    use_external_math=False,
                ),
                current_pipeline=pipeline_fingerprint(),
            )

            self.assertTrue(result["stale"])
            self.assertIn("builder_version_changed", result["reasons"])
            self.assertIn("missing_input_fingerprints", result["reasons"])
            self.assertIn("missing_pipeline_fingerprint", result["reasons"])
            self.assertIn("missing_pdf_fingerprint", result["reasons"])

    def test_document_is_stale_when_pdf_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            metadata = build_metadata_for_paper(
                "test_paper",
                pdf_path=pdf_path,
                timestamp="2026-04-14T00:00:00Z",
                layout_engine="native_pdf",
                math_engine="heuristic",
                figure_engine="local",
                text_engine="native_pdf",
                use_external_layout=False,
                use_external_math=False,
            )
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": metadata,
            }
            pdf_path.write_text("pdf-v2", encoding="utf-8")

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": False},
                current_inputs=build_input_fingerprints(
                    "test_paper",
                    pdf_path=pdf_path,
                    use_external_layout=False,
                    use_external_math=False,
                ),
                current_pipeline=pipeline_fingerprint(),
            )

            self.assertTrue(result["stale"])
            self.assertIn("pdf_input_changed", result["reasons"])

    def test_document_is_stale_when_target_build_flags_expand(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "paper.pdf"
            pdf_path.write_text("pdf-v1", encoding="utf-8")
            external_math_path = Path(temp_dir) / "math.json"
            external_math_path.write_text("{}", encoding="utf-8")
            metadata = build_metadata_for_paper(
                "test_paper",
                pdf_path=pdf_path,
                timestamp="2026-04-14T00:00:00Z",
                layout_engine="native_pdf",
                math_engine="heuristic",
                figure_engine="local",
                text_engine="native_pdf",
                use_external_layout=False,
                use_external_math=False,
            )
            document = {
                "paper_id": "test_paper",
                "source": {"pdf_path": str(pdf_path)},
                "build": metadata,
            }

            result = detect_document_staleness(
                document,
                desired_flags={"use_external_layout": False, "use_external_math": True},
                current_inputs={
                    "pdf": fingerprint_path(pdf_path),
                    "external_math": fingerprint_path(external_math_path),
                },
                current_pipeline=pipeline_fingerprint(),
            )

            self.assertTrue(result["stale"])
            self.assertIn("build_flags_changed", result["reasons"])
            self.assertIn("missing_external_math_fingerprint", result["reasons"])

    def test_missing_canonical_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = detect_canonical_staleness(Path(temp_dir) / "missing" / "canonical.json")

            self.assertTrue(result["stale"])
            self.assertEqual(result["reasons"], ["canonical_missing"])


if __name__ == "__main__":
    unittest.main()
