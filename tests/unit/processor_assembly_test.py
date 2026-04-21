from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout
from pipeline.processor.assembly import build_paper_state


def _layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        corpus_name="synthetic",
        corpus_root=corpus_root,
        source_root=corpus_root / "_source",
        review_root=corpus_root / "_canon",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


class ProcessorAssemblyTest(unittest.TestCase):
    def test_build_paper_state_allows_missing_abstract_without_placeholder_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _layout(root)
            paper_id = "1990_synthetic_test_paper"
            pdf_path = layout.source_root / f"{paper_id}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(b"%PDF-1.4\nsynthetic\n")
            prepared_sources = {
                "final_layout": {
                    "engine": "docling",
                    "page_count": 1,
                    "page_sizes_pt": [],
                    "blocks": [
                        {"id": "blk-1", "page": 1, "order": 1, "role": "front_matter", "text": "Synthetic Test Paper"},
                        {"id": "blk-2", "page": 1, "order": 2, "role": "heading", "text": "1 Introduction"},
                        {"id": "blk-3", "page": 1, "order": 3, "role": "paragraph", "text": "A stable paragraph."},
                    ],
                },
                "final_math": {"engine": "none", "entries": []},
                "mathpix_layout": {},
                "metadata_candidates": {},
                "metadata_observation": None,
                "reference_observation": None,
                "acquisition_route_payload": {"primary_route": "born_digital_scholarly", "traits": []},
                "source_scorecard": {"providers": []},
                "acquisition_execution": {"ownership": {}, "recovery": {"abstract_placeholder_used": False}},
                "layout_owner": "docling",
                "math_owner": "none",
                "metadata_owner": None,
                "reference_owner": None,
            }

            with patch("pipeline.processor.assembly.extract_figures", return_value=[]):
                state = build_paper_state(
                    paper_id,
                    config=build_pipeline_config(layout=layout),
                    prepared_sources=prepared_sources,
                )

            self.assertIsNone(state.document["front_matter"]["abstract_block_id"])
            self.assertEqual(state.document["build"]["sources"]["layout_engine"], "docling")
            self.assertEqual(state.document["build"]["sources"]["math_engine"], "none")
            self.assertEqual(state.document["_decision_artifacts"]["acquisition"]["owners"]["layout"], "docling")
            self.assertFalse(
                any(block["id"].startswith("blk-front-abstract-") for block in state.document["blocks"])
            )

    def test_build_paper_state_fails_when_no_trustworthy_title_is_acquired(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _layout(root)
            paper_id = "1990_synthetic_test_paper"
            pdf_path = layout.source_root / f"{paper_id}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(b"%PDF-1.4\nsynthetic\n")
            prepared_sources = {
                "final_layout": {
                    "engine": "docling",
                    "page_count": 1,
                    "page_sizes_pt": [],
                    "blocks": [
                        {"id": "blk-1", "page": 1, "order": 1, "role": "paragraph", "text": "No usable title here."},
                    ],
                },
                "final_math": {"engine": "none", "entries": []},
                "mathpix_layout": {},
                "metadata_candidates": {},
                "metadata_observation": None,
                "reference_observation": None,
                "acquisition_route_payload": {"primary_route": "born_digital_scholarly", "traits": []},
                "source_scorecard": {"providers": []},
                "acquisition_execution": {"ownership": {}, "recovery": {"abstract_placeholder_used": False}},
                "layout_owner": "docling",
                "math_owner": "none",
                "metadata_owner": None,
                "reference_owner": None,
            }

            with patch("pipeline.processor.assembly.extract_figures", return_value=[]):
                with self.assertRaises(RuntimeError):
                    build_paper_state(
                        paper_id,
                        config=build_pipeline_config(layout=layout),
                        prepared_sources=prepared_sources,
                    )


if __name__ == "__main__":
    unittest.main()
