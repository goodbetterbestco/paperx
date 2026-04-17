#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.mathpix_adapter import (
    mathpix_pages_to_external_sources,
    run_mathpix,
    write_external_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical_sources from Mathpix PDF OCR output.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--page", type=int, action="append", dest="pages", help="Limit to one or more 1-based page numbers.")
    parser.add_argument("--endpoint", default="https://api.mathpix.com/v3/pdf", help="Mathpix PDF OCR endpoint.")
    parser.add_argument("--app-id", help="Override MATHPIX_APP_ID.")
    parser.add_argument("--app-key", help="Override MATHPIX_APP_KEY.")
    parser.add_argument(
        "--mathpix-json",
        action="append",
        help="Use one or more existing Mathpix page response JSON files instead of calling the API.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Summarize extracted sources without writing them.")
    return parser.parse_args()


def _load_saved_payloads(paths: list[str]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for value in paths:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
        payloads.append(payload)
    payloads.sort(key=lambda item: int(item.get("page", 0)))
    return payloads


def _build_summary(layout: dict[str, Any], math: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "source": source,
        "layout_engine": layout.get("engine"),
        "layout_blocks": len(layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
    }


def main() -> int:
    args = parse_args()
    if args.mathpix_json:
        payloads = _load_saved_payloads(args.mathpix_json)
        source = ",".join(args.mathpix_json)
    else:
        mathpix_result = run_mathpix(
            args.paper_id,
            pages=args.pages,
            endpoint=args.endpoint,
            app_id=args.app_id,
            app_key=args.app_key,
        )
        payloads = list(mathpix_result.get("pages") or [])
        source = "mathpix_api"

    layout, math = mathpix_pages_to_external_sources(payloads, args.paper_id)
    summary = _build_summary(layout, math, source)

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    layout_path, math_path = write_external_sources(args.paper_id, layout, math)
    print(
        json.dumps(
            {
                **summary,
                "layout_path": str(layout_path),
                "math_path": str(math_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
