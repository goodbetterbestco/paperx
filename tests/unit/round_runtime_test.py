from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline.corpus_layout import ProjectLayout
from pipeline.orchestrator import round_runtime


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


class RoundRuntimeTest(unittest.TestCase):
    def test_build_round_runtime_uses_project_report_paths_in_project_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _project_layout(Path(temp_dir).resolve())

            runtime = round_runtime.build_round_runtime(layout)

            self.assertEqual(runtime.batch_dir, layout.project_status_path().parent)
            self.assertEqual(runtime.status_path, layout.project_status_path())
            self.assertEqual(runtime.report_path, layout.project_report_path())
            self.assertEqual(runtime.lexicon_path, layout.corpus_lexicon_path)

    def test_read_env_local_parses_comments_blank_lines_and_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_local = Path(temp_dir) / ".env.local"
            env_local.write_text(
                "# comment\n\nAPI_KEY='secret'\nPLAIN=value\nQUOTED=\"two words\"\nBROKEN_LINE\n",
                encoding="utf-8",
            )

            with patch.object(round_runtime, "ENV_LOCAL_PATH", env_local):
                loaded = round_runtime.read_env_local()

            self.assertEqual(
                loaded,
                {
                    "API_KEY": "secret",
                    "PLAIN": "value",
                    "QUOTED": "two words",
                },
            )

    def test_read_env_local_can_be_disabled_by_env_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_local = Path(temp_dir) / ".env.local"
            env_local.write_text("API_KEY=secret\n", encoding="utf-8")

            with (
                patch.object(round_runtime, "ENV_LOCAL_PATH", env_local),
                patch.dict("os.environ", {"PIPELINE_SKIP_ENV_LOCAL": "1"}, clear=False),
            ):
                loaded = round_runtime.read_env_local()

            self.assertEqual(loaded, {})

    def test_load_status_discovers_papers_when_status_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            paper_dir = layout.paper_dir("1990_synthetic_test_paper")
            paper_dir.mkdir(parents=True, exist_ok=True)
            layout.paper_pdf_path("1990_synthetic_test_paper").write_bytes(b"%PDF-1.4")
            isolated_tmp_dir = Path(temp_dir).resolve() / "tmp"
            with (
                patch.object(round_runtime, "TMP_DIR", isolated_tmp_dir),
                patch.object(round_runtime, "now_iso", return_value="2026-04-19T00:00:00Z"),
            ):
                runtime = round_runtime.build_round_runtime(layout)
                status = round_runtime.load_status(runtime)

            self.assertEqual(status["papers"], ["1990_synthetic_test_paper"])
            self.assertEqual(status["started_at"], "2026-04-19T00:00:00Z")
            self.assertEqual(status["updated_at"], "2026-04-19T00:00:00Z")
            self.assertEqual(status["rounds"], {})
            self.assertEqual(status["notes"], [])

    def test_save_status_writes_updated_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            status = {"papers": [], "rounds": {}, "notes": []}
            isolated_tmp_dir = Path(temp_dir).resolve() / "tmp"

            with (
                patch.object(round_runtime, "TMP_DIR", isolated_tmp_dir),
                patch.object(round_runtime, "now_iso", return_value="2026-04-19T00:30:00Z"),
            ):
                runtime = round_runtime.build_round_runtime(layout)
                round_runtime.save_status(status, runtime)

            written = json.loads(runtime.status_path.read_text(encoding="utf-8"))
            self.assertEqual(written["updated_at"], "2026-04-19T00:30:00Z")

    def test_rebuild_lexicon_writes_built_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = _corpus_layout(Path(temp_dir).resolve())
            runtime = round_runtime.build_round_runtime(layout)

            with patch.object(round_runtime, "_build_lexicon", return_value={"terms": [{"canonical": "trimmedsurface"}]}):
                payload = round_runtime.rebuild_lexicon(runtime)

            self.assertEqual(payload["terms"][0]["canonical"], "trimmedsurface")
            self.assertEqual(
                json.loads(runtime.lexicon_path.read_text(encoding="utf-8"))["terms"][0]["canonical"],
                "trimmedsurface",
            )


if __name__ == "__main__":
    unittest.main()
