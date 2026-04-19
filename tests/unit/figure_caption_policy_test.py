import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.policies.figure_caption import apply_figure_caption_policy


class FigureCaptionPolicyTest(unittest.TestCase):
    def test_caption_policy_applies_known_caption_correction(self) -> None:
        self.assertEqual(
            apply_figure_caption_policy(
                "2001_survey_of_aspect_graphs",
                "fig-18",
                (
                    "Fig 18. (a) A portion of the lower bound construction for ¶ k) convex polyhedra "
                    "with · (n) total edges. (b) The same construction as viewed from the plane "
                    "z = + ¸ ¹ º¼»v½¿¾ÁÀ º z-axis. (From [4])"
                ),
            ),
            (
                "Fig 18. (a) A portion of the lower bound construction for Θ(k) convex polyhedra "
                "with Θ(n) total edges. (b) The same construction as viewed from the plane "
                "z = +∞ near the z-axis. (From [4])"
            ),
        )

    def test_caption_policy_keeps_unknown_caption_unchanged(self) -> None:
        self.assertEqual(
            apply_figure_caption_policy("example_paper", "fig-1", "Fig 1. Example caption."),
            "Fig 1. Example caption.",
        )


if __name__ == "__main__":
    unittest.main()
