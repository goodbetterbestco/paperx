import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.cli.external_source_build import (
    build_docling_external_sources,
    build_mathpix_external_sources,
    build_pdftotext_external_layout,
    compose_external_sources,
)
from pipeline.cli.paper_build import build_paper
from pipeline.corpus_layout import ProjectLayout
from pipeline.state import PaperState


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


class CliHelperTest(unittest.TestCase):
    def test_build_paper_threads_explicit_layout_into_config_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            captured: dict[str, object] = {}

            def fake_reconcile_paper_state(paper_id: str, **kwargs: object) -> PaperState:
                config = kwargs["config"]
                captured["paper_id"] = paper_id
                captured["config"] = config
                state = PaperState.begin(
                    paper_id,
                    config=config,
                    started_at="2026-04-17T00:00:00Z",
                )
                state.document = {
                    "paper_id": paper_id,
                    "title": "Synthetic Test Paper",
                    "sections": [],
                    "blocks": [],
                    "math": [],
                    "figures": [],
                    "references": [],
                }
                return state

            with patch("pipeline.cli.paper_build.reconcile_paper_state", side_effect=fake_reconcile_paper_state):
                build = build_paper(
                    "1990_synthetic_test_paper",
                    text_engine="hybrid",
                    use_external_layout=True,
                    use_external_math=False,
                    include_review=True,
                    layout=layout,
                )

            self.assertEqual(captured["paper_id"], "1990_synthetic_test_paper")
            self.assertIs(build.layout, layout)
            self.assertIs(build.config.layout, layout)
            self.assertEqual(build.config.text_engine, "hybrid")
            self.assertTrue(build.config.use_external_layout)
            self.assertFalse(build.config.use_external_math)
            self.assertTrue(build.config.include_review)
            self.assertEqual(build.document["paper_id"], "1990_synthetic_test_paper")

    def test_build_docling_external_sources_forwards_layout_and_writes_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            docling_json_path = layout.tmp_root / "docling.json"
            docling_json_path.parent.mkdir(parents=True, exist_ok=True)
            docling_json_path.write_text(json.dumps({"texts": []}), encoding="utf-8")
            captured: dict[str, object] = {}

            def fake_docling_to_sources(_document: dict, _paper_id: str, *, layout=None) -> tuple[dict, dict]:
                captured["sources_layout"] = layout
                return (
                    {"engine": "docling", "blocks": [{"id": "blk-1"}]},
                    {"engine": "docling", "entries": [{"id": "eq-1"}]},
                )

            with (
                patch("pipeline.cli.external_source_build.run_docling", return_value=docling_json_path) as run_docling,
                patch(
                    "pipeline.cli.external_source_build.docling_json_to_external_sources",
                    side_effect=fake_docling_to_sources,
                ),
            ):
                build = build_docling_external_sources(
                    paper_id,
                    device="cpu",
                    layout=layout,
                )
                outputs = build.write()

            self.assertEqual(run_docling.call_args.kwargs["layout"], layout)
            self.assertIs(captured["sources_layout"], layout)
            self.assertEqual(build.summary["layout_engine"], "docling")
            self.assertEqual(build.summary["math_entries"], 1)
            self.assertTrue(Path(outputs["layout_path"]).exists())
            self.assertTrue(Path(outputs["math_path"]).exists())

    def test_build_mathpix_external_sources_forwards_layout_and_writes_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            captured: dict[str, object] = {}

            def fake_pages_to_sources(_payloads: list[dict], _paper_id: str, *, layout=None) -> tuple[dict, dict]:
                captured["sources_layout"] = layout
                return (
                    {"engine": "mathpix", "blocks": [{"id": "blk-1"}]},
                    {"engine": "mathpix", "entries": [{"id": "eq-1"}]},
                )

            with (
                patch("pipeline.cli.external_source_build.run_mathpix", return_value={"pages": [{"page": 1}]}) as run_mathpix,
                patch(
                    "pipeline.cli.external_source_build.mathpix_pages_to_external_sources",
                    side_effect=fake_pages_to_sources,
                ),
            ):
                build = build_mathpix_external_sources(
                    paper_id,
                    pages=[1],
                    layout=layout,
                )
                outputs = build.write()

            self.assertEqual(run_mathpix.call_args.kwargs["layout"], layout)
            self.assertIs(captured["sources_layout"], layout)
            self.assertEqual(build.summary["source"], "mathpix_api")
            self.assertTrue(Path(outputs["layout_path"]).exists())
            self.assertTrue(Path(outputs["math_path"]).exists())

    def test_build_pdftotext_external_layout_writes_explicit_layout_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            payload = {"engine": "pdftotext_overlay", "blocks": []}
            summary = {"changed_blocks": 1, "skipped_blocks": 0, "total_blocks": 1}

            with patch(
                "pipeline.cli.external_source_build.overlay_pdftotext_onto_layout",
                return_value=(payload, summary),
            ) as overlay:
                build = build_pdftotext_external_layout(paper_id, layout=layout)
                outputs = build.write()

            self.assertEqual(overlay.call_args.kwargs["layout"], layout)
            self.assertEqual(build.summary["changed_blocks"], 1)
            self.assertEqual(json.loads(Path(outputs["layout_path"]).read_text(encoding="utf-8"))["engine"], "pdftotext_overlay")

    def test_compose_external_sources_reads_inputs_and_writes_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_id = "1990_synthetic_test_paper"
            input_dir = layout.tmp_root / "compose-inputs"
            input_dir.mkdir(parents=True, exist_ok=True)
            layout_input = input_dir / "layout.json"
            math_input = input_dir / "math.json"
            layout_input.write_text(json.dumps({"engine": "docling", "blocks": []}), encoding="utf-8")
            math_input.write_text(json.dumps({"engine": "mathpix", "entries": []}), encoding="utf-8")

            build = compose_external_sources(
                paper_id,
                layout_json=layout_input,
                math_json=math_input,
                layout=layout,
            )
            outputs = build.write()

            self.assertEqual(build.summary["layout_engine"], "docling")
            self.assertEqual(build.summary["math_engine"], "mathpix")
            self.assertTrue(Path(outputs["layout_path"]).exists())
            self.assertTrue(Path(outputs["math_path"]).exists())


if __name__ == "__main__":
    unittest.main()
