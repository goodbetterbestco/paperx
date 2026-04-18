import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class RootBoundaryTest(unittest.TestCase):
    def test_pipeline_root_contains_only_boundary_modules(self) -> None:
        pipeline_root = ROOT / "pipeline"
        actual = {path.name for path in pipeline_root.glob("*.py")}
        expected = {
            "__init__.py",
            "config.py",
            "corpus_layout.py",
            "run_corpus_rounds.py",
            "runtime_paths.py",
            "state.py",
            "types.py",
        }

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
