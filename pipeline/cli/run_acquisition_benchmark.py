from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.benchmark import run_acquisition_benchmark
from pipeline.output.acquisition_benchmark_report import render_acquisition_benchmark_markdown
from pipeline.runtime_paths import ensure_repo_tmp_dir


OUTPUT_DIR = ensure_repo_tmp_dir() / "acquisition_benchmark"
JSON_REPORT_PATH = OUTPUT_DIR / "summary.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-backed acquisition benchmark.")
    parser.add_argument("--manifest", required=True, help="Path to an acquisition benchmark manifest JSON file.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    parser.add_argument(
        "--label",
        help="Optional snapshot label. Defaults to a UTC timestamp and is used for history artifact filenames.",
    )
    return parser.parse_args()


def _snapshot_label(value: str | None) -> str:
    if value:
        cleaned = "".join(character if character.isalnum() or character in ("-", "_") else "-" for character in value)
        cleaned = cleaned.strip("-_")
        if cleaned:
            return cleaned
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_benchmark_cli(
    args: argparse.Namespace,
    *,
    run_benchmark_fn: Callable[[str], dict[str, Any]] = run_acquisition_benchmark,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_markdown,
    output_dir: Path = OUTPUT_DIR,
    json_report_path: Path = JSON_REPORT_PATH,
    markdown_report_path: Path = MARKDOWN_REPORT_PATH,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = run_benchmark_fn(args.manifest)
    history_dir = output_dir / "history"
    snapshot_label = _snapshot_label(getattr(args, "label", None))
    snapshot_json_path = history_dir / f"{snapshot_label}.json"
    snapshot_markdown_path = history_dir / f"{snapshot_label}.md"
    report["report_paths"] = {
        "json": str(json_report_path),
        "markdown": str(markdown_report_path),
        "snapshot_json": str(snapshot_json_path),
        "snapshot_markdown": str(snapshot_markdown_path),
    }
    report["snapshot_label"] = snapshot_label
    output_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown_fn(report)
    markdown_report_path.write_text(markdown, encoding="utf-8")
    snapshot_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    snapshot_markdown_path.write_text(markdown, encoding="utf-8")
    if args.format == "markdown":
        print_fn(markdown)
    else:
        print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
