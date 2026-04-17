import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.config import build_pipeline_config
from pipeline.corpus_layout import ProjectLayout


class PipelineConfigTest(unittest.TestCase):
    def test_build_pipeline_config_captures_runtime_capabilities(self) -> None:
        engine_root = Path("/tmp/paperx-runtime").resolve()
        corpus_root = engine_root / "corpus" / "synthetic"
        layout = ProjectLayout(
            engine_root=engine_root,
            mode="corpus",
            corpus_name="synthetic",
            project_dir=None,
            corpus_root=corpus_root,
            source_root=corpus_root,
            review_root=corpus_root / "review_drafts",
            runs_root=corpus_root / "_runs",
            tmp_root=engine_root / "tmp",
            figure_expectations_path=corpus_root / "figure_expectations.json",
        )

        with (
            patch.dict(
                os.environ,
                {
                    "MATHPIX_APP_ID": "test-app-id",
                    "MATHPIX_APP_KEY": "test-app-key",
                    "PIPELINE_DOCLING_BIN": "/tmp/docling",
                    "STEPVIEW_DOCLING_DEVICE": "cpu",
                },
                clear=False,
            ),
            patch("pipeline.config.shutil.which", return_value="/usr/bin/pdftotext"),
        ):
            config = build_pipeline_config(
                layout=layout,
                text_engine="hybrid",
                use_external_layout=True,
                use_external_math=False,
                include_review=False,
            )

        self.assertEqual(config.layout, layout)
        self.assertEqual(config.text_engine, "hybrid")
        self.assertTrue(config.use_external_layout)
        self.assertFalse(config.use_external_math)
        self.assertFalse(config.include_review)
        self.assertEqual(config.docling_bin, Path("/tmp/docling").resolve())
        self.assertEqual(config.docling_device, "cpu")
        self.assertTrue(config.mathpix_enabled)
        self.assertTrue(config.pdftotext_enabled)


if __name__ == "__main__":
    unittest.main()
