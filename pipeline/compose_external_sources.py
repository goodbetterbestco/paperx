#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.external_sources import external_layout_path, external_math_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose canonical external sources from separate layout and math providers.")
    parser.add_argument("paper_id", help="Paper directory id under the configured corpus.")
    parser.add_argument("--layout-json", required=True, help="Path to a layout.json-style source file.")
    parser.add_argument("--math-json", required=True, help="Path to a math.json-style source file.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize the composed sources without writing them.")
    return parser.parse_args()


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _summary(layout: dict, math: dict) -> dict[str, object]:
    return {
        "layout_engine": layout.get("engine"),
        "layout_blocks": len(layout.get("blocks", [])),
        "math_engine": math.get("engine"),
        "math_entries": len(math.get("entries", [])),
    }


def main() -> int:
    args = parse_args()
    layout = _load_json(args.layout_json)
    math = _load_json(args.math_json)
    summary = _summary(layout, math)

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    layout_path = external_layout_path(args.paper_id)
    math_path = external_math_path(args.paper_id)
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    layout_path.write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    math_path.write_text(json.dumps(math, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({**summary, "layout_path": str(layout_path), "math_path": str(math_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
