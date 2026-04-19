from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from pipeline.acquisition.backfill import backfill_acquisition_sidecars
from pipeline.corpus_layout import current_layout
from pipeline.sources.external import (
    load_docling_layout,
    load_docling_math,
    load_external_layout,
    load_external_math,
    load_grobid_metadata_observation,
    load_mathpix_layout,
    load_mathpix_math,
    ocr_normalized_pdf_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill acquisition route, scorecard, and OCR sidecars.")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite sidecars even when they already exist.")
    parser.add_argument("--paper-id", action="append", dest="paper_ids", help="Limit the backfill to one or more paper ids.")
    return parser.parse_args()


def run_backfill_acquisition_sidecars(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], Any] = current_layout,
    backfill_acquisition_sidecars_fn: Callable[..., dict[str, Any]] = backfill_acquisition_sidecars,
    print_fn: Callable[[str], None] = print,
) -> int:
    layout = current_layout_fn()
    report = backfill_acquisition_sidecars_fn(
        layout=layout,
        overwrite=bool(args.overwrite),
        paper_ids=list(args.paper_ids or []),
        load_docling_layout_impl=load_docling_layout,
        load_mathpix_layout_impl=load_mathpix_layout,
        load_external_layout_impl=load_external_layout,
        load_docling_math_impl=load_docling_math,
        load_mathpix_math_impl=load_mathpix_math,
        load_external_math_impl=load_external_math,
        load_grobid_metadata_observation_impl=load_grobid_metadata_observation,
        ocr_normalized_pdf_path_impl=ocr_normalized_pdf_path,
    )
    print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_backfill_acquisition_sidecars(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
