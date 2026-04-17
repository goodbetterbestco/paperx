import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_pipeline.runtime_paths import runtime_env


class RuntimePathsTest(unittest.TestCase):
    def test_runtime_env_leaves_xdg_cache_home_unset_by_default(self) -> None:
        original = os.environ.pop("XDG_CACHE_HOME", None)
        try:
            env = runtime_env()
        finally:
            if original is not None:
                os.environ["XDG_CACHE_HOME"] = original

        self.assertNotIn("XDG_CACHE_HOME", env)


if __name__ == "__main__":
    unittest.main()
