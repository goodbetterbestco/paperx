from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.routing import build_acquisition_route_report
from pipeline.corpus_layout import current_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the acquisition route for one paper.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--write", action="store_true", help="Write canonical_sources/acquisition-route.json.")
    return parser.parse_args()


def run_inspect_acquisition_route(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], Any] = current_layout,
    build_report_fn: Callable[..., dict[str, Any]] = build_acquisition_route_report,
    print_fn: Callable[[str], None] = print,
) -> int:
    layout = current_layout_fn()
    report = build_report_fn(args.paper_id, layout=layout)

    if args.write:
        output_path = layout.canonical_sources_dir(args.paper_id) / "acquisition-route.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print_fn(json.dumps({**report, "route_path": str(Path(output_path).resolve())}, indent=2))
        return 0

    print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_inspect_acquisition_route(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
