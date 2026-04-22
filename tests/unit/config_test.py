import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
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
            corpus_name="synthetic",
            corpus_root=corpus_root,
            source_root=corpus_root / "_source",
            review_root=corpus_root / "_canon",
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
            )
        ):
            config = build_pipeline_config(
                layout=layout,
                include_review=False,
            )

        self.assertEqual(config.layout, layout)
        self.assertFalse(config.include_review)
        self.assertEqual(config.docling_bin, Path("/tmp/docling").resolve())
        self.assertEqual(config.docling_device, "cpu")
        self.assertTrue(config.mathpix_enabled)


if __name__ == "__main__":
    unittest.main()
