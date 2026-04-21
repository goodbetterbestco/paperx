from __future__ import annotations

import argparse
import json

from pipeline.corpus_layout import CORPUS_DIR, current_layout
from pipeline.output.review_renderer import write_review_from_canonical


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a markdown review draft from canonical.json.")
    parser.add_argument("paper_id", help=f"Paper id in the configured layout ({CORPUS_DIR}).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    destination = write_review_from_canonical(args.paper_id, layout=current_layout())
    print(json.dumps({"path": str(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
