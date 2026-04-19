from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from pipeline import acquisition


class AcquisitionPackageExportsTest(unittest.TestCase):
    def test_benchmark_utilities_are_exported_from_package_boundary(self) -> None:
        self.assertTrue(callable(acquisition.compare_benchmark_reports))
        self.assertTrue(callable(acquisition.list_benchmark_history))
        self.assertTrue(callable(acquisition.summarize_benchmark_trend))
        self.assertTrue(callable(acquisition.aggregate_provider_score_map))
        self.assertTrue(callable(acquisition.benchmark_report_label))
        self.assertTrue(callable(acquisition.family_provider_score_maps))
        self.assertTrue(callable(acquisition.load_benchmark_report))
        self.assertTrue(callable(acquisition.list_history_reports))
        self.assertTrue(callable(acquisition.resolve_benchmark_report_path))
        self.assertTrue(callable(acquisition.provider_score_map))


if __name__ == "__main__":
    unittest.main()
