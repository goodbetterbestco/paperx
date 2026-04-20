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


from pipeline.cli.inspect_acquisition_route import run_inspect_acquisition_route
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


class AcquisitionCliTest(unittest.TestCase):
    def test_route_cli_prints_json_without_writing(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            exit_code = run_inspect_acquisition_route(
                argparse.Namespace(paper_id="fixture", write=False),
                current_layout_fn=lambda: layout,
                build_report_fn=lambda paper_id, *, layout=None: {
                    "paper_id": paper_id,
                    "primary_route": "born_digital_scholarly",
                },
                print_fn=printed.append,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["primary_route"], "born_digital_scholarly")

    def test_route_cli_writes_sidecar_when_requested(self) -> None:
        printed: list[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            exit_code = run_inspect_acquisition_route(
                argparse.Namespace(paper_id="fixture", write=True),
                current_layout_fn=lambda: layout,
                build_report_fn=lambda paper_id, *, layout=None: {
                    "paper_id": paper_id,
                    "primary_route": "layout_complex",
                },
                print_fn=printed.append,
            )
            route_path = layout.canonical_sources_dir("fixture") / "acquisition-route.json"

            self.assertTrue(route_path.exists())
            self.assertEqual(json.loads(route_path.read_text(encoding="utf-8"))["primary_route"], "layout_complex")

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["primary_route"], "layout_complex")


if __name__ == "__main__":
    unittest.main()
