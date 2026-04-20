from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.build_canonical import run_build_canonical
from pipeline.cli.build_review import run_build_review
from pipeline.cli.rebuild_from_acquisition_trial import run_rebuild_from_trial_cli
from pipeline.corpus_layout import ProjectLayout


def _project_layout(root: Path) -> ProjectLayout:
    corpus_root = root
    return ProjectLayout(
        engine_root=root,
        mode="project",
        corpus_name="fixture",
        project_dir=root,
        corpus_root=corpus_root,
        source_root=root,
        review_root=root / "_canon",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


class BuildCliTest(unittest.TestCase):
    def test_build_canonical_reports_runtime_build_errors_without_traceback(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-build-cli").resolve())
        printed: list[str] = []
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            text_engine="native",
            use_external_layout=False,
            use_external_math=False,
            dry_run=False,
            validate=False,
        )

        exit_code = run_build_canonical(
            args,
            current_layout_fn=lambda: layout,
            build_paper_fn=lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("PyMuPDF is required for layout extraction.")
            ),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(printed, ["build_error=PyMuPDF is required for layout extraction."])

    def test_build_review_reports_runtime_build_errors_without_traceback(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-build-cli").resolve())
        printed: list[str] = []
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            text_engine="native",
            use_external_layout=False,
            use_external_math=False,
            dry_run=False,
        )

        exit_code = run_build_review(
            args,
            current_layout_fn=lambda: layout,
            build_paper_fn=lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("PyMuPDF is required for layout extraction.")
            ),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(printed, ["build_error=PyMuPDF is required for layout extraction."])

    def test_rebuild_from_trial_promotes_then_builds_with_external_sources_enabled(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-build-cli").resolve())
        printed: list[str] = []
        captured: dict[str, object] = {}
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            label="trial-mathpix",
            text_engine="native",
            include_review=False,
            dry_run=True,
        )

        exit_code = run_rebuild_from_trial_cli(
            args,
            current_layout_fn=lambda: layout,
            promote_trial_fn=lambda paper_id, *, layout=None, label=None: {
                "paper_id": paper_id,
                "label": label,
                "promoted": True,
                "trial_dir": "/tmp/trial",
            },
            build_paper_fn=lambda paper_id, **kwargs: (
                captured.update({"paper_id": paper_id, **kwargs})
                or type(
                    "Build",
                    (),
                    {
                        "layout": layout,
                        "document": {"paper_id": paper_id, "front_matter": {}, "blocks": [], "sections": [], "references": [], "figures": []},
                    },
                )()
            ),
            validate_canonical_fn=lambda document: None,
            build_summary_fn=lambda document: {"block_count": len(document.get("blocks", []))},
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(captured["paper_id"], "1990_synthetic_test_paper")
        self.assertTrue(captured["use_external_layout"])
        self.assertTrue(captured["use_external_math"])
        payload = json.loads(printed[0])
        self.assertEqual(payload["promotion"]["label"], "trial-mathpix")

    def test_rebuild_from_trial_reports_runtime_build_errors_without_traceback(self) -> None:
        layout = _project_layout(Path("/tmp/paperx-build-cli").resolve())
        printed: list[str] = []
        args = argparse.Namespace(
            paper_id="1990_synthetic_test_paper",
            label="trial-mathpix",
            text_engine="native",
            include_review=False,
            dry_run=False,
        )

        exit_code = run_rebuild_from_trial_cli(
            args,
            current_layout_fn=lambda: layout,
            promote_trial_fn=lambda paper_id, *, layout=None, label=None: {
                "paper_id": paper_id,
                "label": label,
                "promoted": True,
            },
            build_paper_fn=lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("PyMuPDF is required for layout extraction.")
            ),
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(printed, ["build_error=PyMuPDF is required for layout extraction."])


if __name__ == "__main__":
    unittest.main()
