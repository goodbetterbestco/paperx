#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.corpus.state import reset_corpus_to_source_state
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset a processed corpus back to source state by moving PDFs into _source and removing generated artifacts."
    )
    parser.add_argument(
        "corpus_dir",
        nargs="?",
        help="Corpus directory to reset. Defaults to the configured corpus root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    active_layout = current_layout()
    corpus_dir = Path(args.corpus_dir).expanduser().resolve() if args.corpus_dir else active_layout.corpus_root
    result = reset_corpus_to_source_state(corpus_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
