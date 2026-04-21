from __future__ import annotations

import argparse
import json

from pipeline.processor.corpus import process_corpus


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the corpus processor once across the configured corpus.")
    parser.add_argument(
        "--max-workers",
        type=int,
        default=20,
        help="Maximum number of papers to process concurrently. Defaults to 20.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    print(json.dumps(process_corpus(max_workers=args.max_workers), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
