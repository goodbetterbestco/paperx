from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.cli.run_grobid_trial import run_grobid_trial_cli


class GrobidTrialCliTest(unittest.TestCase):
    def test_grobid_trial_cli_prints_json_report(self) -> None:
        printed: list[str] = []

        exit_code = run_grobid_trial_cli(
            argparse.Namespace(manifest=str(Path("tests/fixtures/grobid_trial/manifest.json"))),
            run_trial_fn=lambda manifest: {
                "manifest_path": manifest,
                "policy": {"status": "live_metadata_reference_only"},
                "paper_count": 1,
                "aggregate": {"provider": "grobid", "avg_overall_score": 0.99},
            },
            print_fn=printed.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(printed[0])["aggregate"]["provider"], "grobid")


if __name__ == "__main__":
    unittest.main()
