from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.scoring import build_source_scorecard
from pipeline.corpus_layout import current_layout
from pipeline.sources.external import load_external_layout, load_external_math, load_mathpix_layout
from pipeline.sources.layout import extract_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect acquisition source scorecards for one paper.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    return parser.parse_args()


def run_inspect_acquisition_scorecard(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], Any] = current_layout,
    extract_layout_fn: Callable[..., dict[str, Any]] = extract_layout,
    load_external_layout_fn: Callable[..., dict[str, Any] | None] = load_external_layout,
    load_mathpix_layout_fn: Callable[..., dict[str, Any] | None] = load_mathpix_layout,
    load_external_math_fn: Callable[..., dict[str, Any] | None] = load_external_math,
    build_source_scorecard_fn: Callable[..., dict[str, Any]] = build_source_scorecard,
    print_fn: Callable[[str], None] = print,
) -> int:
    layout = current_layout_fn()
    report = build_source_scorecard_fn(
        native_layout=extract_layout_fn(args.paper_id, layout=layout),
        external_layout=load_external_layout_fn(args.paper_id, layout=layout),
        mathpix_layout=load_mathpix_layout_fn(args.paper_id, layout=layout),
        external_math=load_external_math_fn(args.paper_id, layout=layout),
    )
    print_fn(json.dumps({"paper_id": args.paper_id, **report}, indent=2))
    return 0


def main() -> int:
    return run_inspect_acquisition_scorecard(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
