from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.cli.build_canonical import run_build_canonical
from pipeline.cli.build_review import run_build_review
from pipeline.corpus_layout import ProjectLayout


def _project_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus"
    return ProjectLayout(
        engine_root=root,
        mode="project",
        corpus_name="fixture",
        project_dir=root,
        corpus_root=corpus_root,
        source_root=root / "source",
        review_root=root,
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


if __name__ == "__main__":
    unittest.main()
