from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.acquisition.benchmark_artifacts import (
    build_benchmark_artifact_paths,
    current_benchmark_output_dir,
    ensure_benchmark_artifact_dirs,
    load_current_benchmark_dashboard,
    load_current_benchmark_summary,
    write_benchmark_artifact_bundle,
)


class AcquisitionBenchmarkArtifactsTest(unittest.TestCase):
    def test_build_benchmark_artifact_paths_returns_expected_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = build_benchmark_artifact_paths("fixture-run", output_dir=Path(temp_dir) / "benchmark")

        self.assertTrue(str(paths.summary_json).endswith("summary.json"))
        self.assertTrue(str(paths.status_json).endswith("status.json"))
        self.assertTrue(str(paths.dashboard_markdown).endswith("dashboard.md"))
        self.assertTrue(str(paths.snapshot_json).endswith("history/fixture-run.json"))
        self.assertEqual(paths.report_paths()["snapshot_markdown"], str(paths.snapshot_markdown))
        self.assertEqual(current_benchmark_output_dir(history_dir=paths.history_dir), paths.output_dir.resolve())

    def test_write_benchmark_artifact_bundle_writes_all_current_and_snapshot_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = build_benchmark_artifact_paths("fixture-run", output_dir=Path(temp_dir) / "benchmark")
            ensure_benchmark_artifact_dirs(paths)
            report = {"snapshot_label": "fixture-run", "paper_count": 1}
            status = {"latest_run": {"label": "fixture-run"}}
            dashboard = {"overview": {"latest_label": "fixture-run"}}

            result = write_benchmark_artifact_bundle(
                report,
                status,
                dashboard,
                paths=paths,
                benchmark_markdown="# benchmark\n",
                status_markdown="# status\n",
                dashboard_markdown="# dashboard\n",
            )

            self.assertEqual(result["report_paths"]["json"], str(paths.summary_json))
            self.assertEqual(json.loads(paths.summary_json.read_text(encoding="utf-8"))["snapshot_label"], "fixture-run")
            self.assertEqual(paths.summary_markdown.read_text(encoding="utf-8"), "# benchmark\n")
            self.assertEqual(json.loads(paths.status_json.read_text(encoding="utf-8"))["latest_run"]["label"], "fixture-run")
            self.assertEqual(paths.status_markdown.read_text(encoding="utf-8"), "# status\n")
            self.assertEqual(paths.snapshot_markdown.read_text(encoding="utf-8"), "# benchmark\n")
            self.assertEqual(json.loads(paths.dashboard_json.read_text(encoding="utf-8"))["overview"]["latest_label"], "fixture-run")
            self.assertEqual(paths.dashboard_markdown.read_text(encoding="utf-8"), "# dashboard\n")
            self.assertEqual(load_current_benchmark_summary(output_dir=paths.output_dir)["snapshot_label"], "fixture-run")
            self.assertEqual(load_current_benchmark_dashboard(output_dir=paths.output_dir)["overview"]["latest_label"], "fixture-run")


if __name__ == "__main__":
    unittest.main()
