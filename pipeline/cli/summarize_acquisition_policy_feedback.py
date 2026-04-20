from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pipeline.acquisition.audit import audit_acquisition_quality as audit_acquisition_quality_impl
from pipeline.acquisition.policy_feedback import summarize_acquisition_policy_feedback
from pipeline.corpus_layout import current_layout
from pipeline.output.acquisition_policy_feedback_report import render_acquisition_policy_feedback_markdown
from pipeline.runtime_paths import ensure_repo_tmp_dir


OUTPUT_DIR = ensure_repo_tmp_dir() / "acquisition_quality_audit"
JSON_REPORT_PATH = OUTPUT_DIR / "policy_feedback.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "policy_feedback.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize recurring acquisition audit signals into recommended upstream policy actions."
    )
    parser.add_argument(
        "--from-report",
        help="Optional acquisition audit JSON report path. Defaults to running a live audit against the current layout.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Console output format. Reports are still written to disk in both JSON and markdown.",
    )
    return parser.parse_args()


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_summarize_acquisition_policy_feedback_cli(
    args: argparse.Namespace,
    *,
    current_layout_fn: Callable[[], object] = current_layout,
    audit_acquisition_quality_fn: Callable[..., dict[str, Any]] = audit_acquisition_quality_impl,
    load_report_fn: Callable[[Path], dict[str, Any]] = _load_report,
    summarize_feedback_fn: Callable[..., dict[str, Any]] = summarize_acquisition_policy_feedback,
    render_markdown_fn: Callable[[dict[str, Any]], str] = render_acquisition_policy_feedback_markdown,
    output_dir: Path = OUTPUT_DIR,
    json_report_path: Path = JSON_REPORT_PATH,
    markdown_report_path: Path = MARKDOWN_REPORT_PATH,
    print_fn: Callable[[str], None] = print,
) -> int:
    source_path: str | None = None
    if getattr(args, "from_report", None):
        resolved_path = Path(str(args.from_report)).resolve()
        audit_report = load_report_fn(resolved_path)
        source_path = str(resolved_path)
    else:
        audit_report = audit_acquisition_quality_fn(layout=current_layout_fn())

    report = summarize_feedback_fn(audit_report, source_path=source_path)
    report["report_paths"] = {
        "json": str(json_report_path),
        "markdown": str(markdown_report_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown_fn(report)
    markdown_report_path.write_text(markdown, encoding="utf-8")
    if args.format == "json":
        print_fn(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_fn(markdown)
    return 0


def main() -> int:
    return run_summarize_acquisition_policy_feedback_cli(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
