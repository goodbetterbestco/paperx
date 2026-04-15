from __future__ import annotations

from typing import Final


_FIGURE_CAPTION_CORRECTIONS: Final[dict[tuple[str, str], str]] = {
    (
        "2001_survey_of_aspect_graphs",
        "fig-18",
    ): (
        "Fig 18. (a) A portion of the lower bound construction for Θ(k) convex "
        "polyhedra with Θ(n) total edges. (b) The same construction as viewed "
        "from the plane z = +∞ near the z-axis. (From [4])"
    ),
}


def apply_figure_caption_policy(paper_id: str, figure_id: str, caption: str) -> str:
    return _FIGURE_CAPTION_CORRECTIONS.get((paper_id, figure_id), caption)

