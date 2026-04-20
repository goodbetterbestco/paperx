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
        self.assertTrue(callable(acquisition.list_remediation_history))
        self.assertTrue(callable(acquisition.list_remediation_plan_history))
        self.assertTrue(callable(acquisition.summarize_benchmark_dashboard))
        self.assertTrue(callable(acquisition.summarize_benchmark_trend))
        self.assertTrue(callable(acquisition.plan_remediation_waves))
        self.assertTrue(callable(acquisition.summarize_remediation_dashboard))
        self.assertTrue(callable(acquisition.summarize_remediation_plan_dashboard))
        self.assertTrue(callable(acquisition.summarize_remediation_plan_status))
        self.assertTrue(callable(acquisition.summarize_remediation_trend))
        self.assertTrue(callable(acquisition.benchmark_status_from_dashboard))
        self.assertTrue(callable(acquisition.aggregate_provider_score_map))
        self.assertTrue(callable(acquisition.benchmark_report_label))
        self.assertTrue(callable(acquisition.build_benchmark_artifact_paths))
        self.assertTrue(callable(acquisition.build_remediation_artifact_paths))
        self.assertTrue(callable(acquisition.current_benchmark_output_dir))
        self.assertTrue(callable(acquisition.current_remediation_output_dir))
        self.assertTrue(callable(acquisition.current_remediation_plan_output_dir))
        self.assertTrue(callable(acquisition.family_provider_score_maps))
        self.assertTrue(callable(acquisition.load_current_benchmark_dashboard))
        self.assertTrue(callable(acquisition.load_current_benchmark_status))
        self.assertTrue(callable(acquisition.load_current_benchmark_summary))
        self.assertTrue(callable(acquisition.load_current_remediation_plan_summary))
        self.assertTrue(callable(acquisition.load_current_remediation_summary))
        self.assertTrue(callable(acquisition.load_benchmark_report))
        self.assertTrue(callable(acquisition.list_history_reports))
        self.assertTrue(callable(acquisition.list_remediation_plan_history_reports))
        self.assertTrue(callable(acquisition.resolve_benchmark_report_path))
        self.assertTrue(callable(acquisition.resolve_remediation_plan_report_path))
        self.assertTrue(callable(acquisition.provider_score_map))
        self.assertTrue(callable(acquisition.select_remediation_plan_waves))
        self.assertTrue(callable(acquisition.write_benchmark_artifact_bundle))
        self.assertTrue(callable(acquisition.write_remediation_plan_artifact_bundle))
        self.assertTrue(callable(acquisition.write_remediation_artifact_bundle))
        self.assertTrue(callable(acquisition.summarize_latest_remediation_status))


if __name__ == "__main__":
    unittest.main()
