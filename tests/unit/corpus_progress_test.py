import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.corpus_layout import ProjectLayout
from pipeline.processor.corpus import run_corpus_once
from pipeline.processor.status import CorpusRuntime


def _corpus_layout(root: Path) -> ProjectLayout:
    corpus_root = root / "corpus" / "synthetic"
    return ProjectLayout(
        engine_root=root,
        corpus_name="synthetic",
        corpus_root=corpus_root,
        source_root=corpus_root / "_source",
        data_root=corpus_root / "_data",
        figures_root=corpus_root / "_figures",
        review_root=corpus_root / "_canon",
        runs_root=corpus_root / "_runs",
        tmp_root=root / "tmp",
        figure_expectations_path=corpus_root / "figure_expectations.json",
    )


class CorpusProgressTest(unittest.TestCase):
    def test_run_corpus_once_reports_initial_and_completion_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            runtime = CorpusRuntime(
                layout=layout,
                batch_dir=layout.runs_root,
                status_path=layout.runs_root / "status.json",
                report_path=layout.runs_root / "final_summary.md",
            )
            status = {
                "started_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "papers": ["paper_a", "paper_b"],
                "runs": [],
                "notes": [],
            }
            progress_updates: list[dict[str, int]] = []

            def fake_run_paper_job(paper_id: str, *, layout: ProjectLayout) -> dict[str, object]:
                if paper_id == "paper_a":
                    return {"status": "completed", "completed_at": "2026-01-01T00:00:01Z"}
                return {"status": "failed", "completed_at": "2026-01-01T00:00:02Z", "error": "boom"}

            run_corpus_once(
                status,
                max_workers=1,
                layout=layout,
                runtime=runtime,
                run_paper_job_impl=fake_run_paper_job,
                progress_callback=progress_updates.append,
            )

            self.assertEqual(len(progress_updates), 3)
            self.assertEqual(
                progress_updates[0],
                {
                    "total": 2,
                    "queued": 1,
                    "processing": 1,
                    "processed": 0,
                    "passed": 0,
                    "failed": 0,
                },
            )
            self.assertEqual(
                progress_updates[1],
                {
                    "total": 2,
                    "queued": 0,
                    "processing": 1,
                    "processed": 1,
                    "passed": 1,
                    "failed": 0,
                },
            )
            self.assertEqual(
                progress_updates[2],
                {
                    "total": 2,
                    "queued": 0,
                    "processing": 0,
                    "processed": 2,
                    "passed": 1,
                    "failed": 1,
                },
            )

    def test_run_corpus_once_does_not_route_the_full_corpus_before_scheduling(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            layout = _corpus_layout(root)
            runtime = CorpusRuntime(
                layout=layout,
                batch_dir=layout.runs_root,
                status_path=layout.runs_root / "status.json",
                report_path=layout.runs_root / "final_summary.md",
            )
            status = {
                "started_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "papers": ["paper_a", "paper_b"],
                "runs": [],
                "notes": [],
            }
            seen: list[str] = []

            def fake_run_paper_job(paper_id: str, *, layout: ProjectLayout) -> dict[str, object]:
                seen.append(paper_id)
                return {"status": "completed", "completed_at": "2026-01-01T00:00:01Z"}

            with patch(
                "pipeline.processor.corpus.build_acquisition_route_report",
                side_effect=AssertionError("unexpected corpus-wide routing"),
            ):
                run_corpus_once(
                    status,
                    max_workers=1,
                    layout=layout,
                    runtime=runtime,
                    run_paper_job_impl=fake_run_paper_job,
                )

            self.assertEqual(seen, ["paper_a", "paper_b"])


if __name__ == "__main__":
    unittest.main()
