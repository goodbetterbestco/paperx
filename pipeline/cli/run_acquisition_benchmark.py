from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from pipeline.acquisition.benchmark import run_acquisition_benchmark
from pipeline.acquisition.benchmark_artifacts import (
    DEFAULT_BENCHMARK_OUTPUT_DIR,
    BenchmarkArtifactPaths,
    build_benchmark_artifact_paths,
    ensure_benchmark_artifact_dirs,
    write_benchmark_artifact_bundle,
)
from pipeline.acquisition.benchmark_dashboard import summarize_benchmark_dashboard
from pipeline.acquisition.benchmark_status import summarize_latest_benchmark_status
from pipeline.output.acquisition_benchmark_dashboard_report import (
    render_acquisition_benchmark_dashboard_markdown,
)
from pipeline.output.acquisition_benchmark_report import render_acquisition_benchmark_markdown
from pipeline.output.acquisition_benchmark_status_report import render_acquisition_benchmark_status_markdown


OUTPUT_DIR = DEFAULT_BENCHMARK_OUTPUT_DIR
JSON_REPORT_PATH = OUTPUT_DIR / "summary.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "summary.md"
DASHBOARD_JSON_REPORT_PATH = OUTPUT_DIR / "dashboard.json"
DASHBOARD_MARKDOWN_REPORT_PATH = OUTPUT_DIR / "dashboard.md"
STATUS_JSON_REPORT_PATH = OUTPUT_DIR / "status.json"
STATUS_MARKDOWN_REPORT_PATH = OUTPUT_DIR / "status.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-backed acquisition benchmark.")
    parser.add_argument("--manifest", required=True, help="Path to an acquisition benchmark manifest JSON file.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    parser.add_argument(
        "--label",
        help="Optional snapshot label. Defaults to a UTC timestamp and is used for history artifact filenames.",
    )
    parser.add_argument(
        "--dashboard-history-limit",
        type=int,
        default=5,
        help="Number of recent runs to include in the generated dashboard artifact.",
    )
    parser.add_argument(
        "--dashboard-trend-limit",
        type=int,
        default=3,
        help="Maximum regressions to highlight in the generated dashboard artifact.",
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
    dashboard_json_report_path: Path = DASHBOARD_JSON_REPORT_PATH,
    dashboard_markdown_report_path: Path = DASHBOARD_MARKDOWN_REPORT_PATH,
    status_json_report_path: Path = STATUS_JSON_REPORT_PATH,
    status_markdown_report_path: Path = STATUS_MARKDOWN_REPORT_PATH,
    summarize_dashboard_fn: Callable[..., dict[str, Any]] = summarize_benchmark_dashboard,
    summarize_status_fn: Callable[..., dict[str, Any]] = summarize_latest_benchmark_status,
    render_dashboard_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_dashboard_markdown,
    render_status_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_benchmark_status_markdown,
    build_artifact_paths_fn: Callable[..., BenchmarkArtifactPaths] = build_benchmark_artifact_paths,
    write_artifact_bundle_fn: Callable[..., dict[str, Any]] = write_benchmark_artifact_bundle,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = run_benchmark_fn(args.manifest)
    snapshot_label = _snapshot_label(getattr(args, "label", None))
    paths = build_artifact_paths_fn(snapshot_label, output_dir=output_dir)
    if json_report_path != paths.summary_json or markdown_report_path != paths.summary_markdown:
        paths = BenchmarkArtifactPaths(
            output_dir=paths.output_dir,
            history_dir=paths.history_dir,
            summary_json=json_report_path,
            summary_markdown=markdown_report_path,
            status_json=status_json_report_path,
            status_markdown=status_markdown_report_path,
            dashboard_json=dashboard_json_report_path,
            dashboard_markdown=dashboard_markdown_report_path,
            snapshot_json=paths.snapshot_json,
            snapshot_markdown=paths.snapshot_markdown,
        )
    report["snapshot_label"] = snapshot_label
    report["report_paths"] = paths.report_paths()
    markdown = render_markdown_fn(report)
    ensure_benchmark_artifact_dirs(paths)
    snapshot_payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    paths.snapshot_json.write_text(snapshot_payload, encoding="utf-8")
    paths.snapshot_markdown.write_text(markdown, encoding="utf-8")
    dashboard = summarize_dashboard_fn(
        history_dir=paths.history_dir,
        history_limit=getattr(args, "dashboard_history_limit", 5),
        trend_limit=getattr(args, "dashboard_trend_limit", 3),
    )
    status = summarize_status_fn(
        history_dir=paths.history_dir,
        limit=getattr(args, "dashboard_trend_limit", 3),
    )
    write_artifact_bundle_fn(
        report,
        status,
        dashboard,
        paths=paths,
        benchmark_markdown=markdown,
        status_markdown=render_status_markdown_fn(status),
        dashboard_markdown=render_dashboard_markdown_fn(dashboard),
    )
    if args.format == "markdown":
        print_fn(markdown)
    else:
        print_fn(json.dumps(report, indent=2))
    return 0


def main() -> int:
    return run_benchmark_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
