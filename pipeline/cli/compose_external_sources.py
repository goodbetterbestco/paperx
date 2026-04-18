from __future__ import annotations

import argparse
import json

from pipeline.cli.external_source_build import compose_external_sources as build_composed_external_sources
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose canonical external sources from separate layout and math providers.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--layout-json", required=True, help="Path to a layout.json-style source file.")
    parser.add_argument("--math-json", required=True, help="Path to a math.json-style source file.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize the composed sources without writing them.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build = build_composed_external_sources(
        args.paper_id,
        layout_json=args.layout_json,
        math_json=args.math_json,
        layout=current_layout(),
    )

    if args.dry_run:
        print(json.dumps(build.summary, indent=2))
        return 0

    outputs = build.write()
    print(json.dumps({**build.summary, **outputs}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
