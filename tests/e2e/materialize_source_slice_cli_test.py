from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


MINIMAL_PDF = b"%PDF-1.4\nsynthetic\n"


class MaterializeSourceSliceCliE2ETest(unittest.TestCase):
    def test_cli_copies_requested_manifest_papers_into_target_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            source_corpus = root / "corpus" / "stepview"
            target_project = root / "tmp" / "validation_slice"
            manifest_path = root / "fixed_validation_slice.json"
            source_corpus.mkdir(parents=True, exist_ok=True)
            (source_corpus / "1990_synthetic_test_paper.pdf").write_bytes(MINIMAL_PDF)
            (source_corpus / "2001_another_test_paper.pdf").write_bytes(MINIMAL_PDF)
            manifest_path.write_text(
                json.dumps(
                    {
                        "label": "validation",
                        "papers": [
                            "1990_synthetic_test_paper",
                            "2001_another_test_paper",
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pipeline.cli.materialize_source_slice",
                    str(target_project),
                    "--source-corpus-dir",
                    str(source_corpus),
                    "--manifest",
                    str(manifest_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(completed.stdout)
            self.assertEqual(payload["state"], "source")
            self.assertEqual(payload["manifest"]["label"], "validation")
            self.assertTrue((target_project / "1990_synthetic_test_paper.pdf").exists())
            self.assertTrue((target_project / "2001_another_test_paper.pdf").exists())


if __name__ == "__main__":
    unittest.main()
