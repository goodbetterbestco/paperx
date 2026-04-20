from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

from pipeline.acquisition.audit import audit_acquisition_quality as audit_acquisition_quality_impl
from pipeline.corpus_layout import current_layout
from pipeline.output.acquisition_audit_report import render_acquisition_audit_markdown
from pipeline.runtime_paths import ensure_repo_tmp_dir


OUTPUT_DIR = ensure_repo_tmp_dir() / "acquisition_quality_audit"
JSON_REPORT_PATH = OUTPUT_DIR / "summary.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit acquisition routing, scoring, and OCR execution quality.")
    parser.add_argument("--top", type=int, default=12, help="Number of papers to include in the markdown summary.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "commands"),
        default="markdown",
        help="Console output format. Reports are still written to disk in both JSON and markdown.",
    )
    return parser.parse_args()


def audit_acquisition_quality() -> dict[str, object]:
    return audit_acquisition_quality_impl(layout=current_layout())


def run_audit_acquisition_quality(
    args: argparse.Namespace,
    *,
    audit_acquisition_quality_fn: Callable[[], dict[str, object]] = audit_acquisition_quality,
    render_markdown_fn: Callable[..., str] = render_acquisition_audit_markdown,
    output_dir: Path = OUTPUT_DIR,
    json_report_path: Path = JSON_REPORT_PATH,
    markdown_report_path: Path = MARKDOWN_REPORT_PATH,
    print_fn: Callable[[str], None] = print,
) -> int:
    report = audit_acquisition_quality_fn()
    report["report_paths"] = {
        "json": str(json_report_path),
        "markdown": str(markdown_report_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown_fn(report, top_n=max(1, args.top))
    markdown_report_path.write_text(markdown, encoding="utf-8")
    if args.format == "json":
        print_fn(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.format == "commands":
        commands = [
            str(item.get("remediation_command") or "").strip()
            for item in list(report.get("remediation_queue") or [])
            if str(item.get("remediation_command") or "").strip()
        ]
        print_fn("\n".join(commands))
    else:
        print_fn(markdown)
    return 0


def main() -> int:
    return run_audit_acquisition_quality(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
