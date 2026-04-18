from __future__ import annotations

import argparse
import json

from pipeline.cli.external_source_build import build_pdftotext_external_layout
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources/layout.json from native layout + pdftotext.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize without writing the file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build = build_pdftotext_external_layout(args.paper_id, layout=current_layout())
    if args.dry_run:
        print(json.dumps(build.summary, indent=2))
        return 0
    outputs = build.write()
    print(json.dumps({"path": outputs["layout_path"], **build.summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
