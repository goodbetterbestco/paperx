from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

from pipeline.corpus.audit import audit_corpus as audit_corpus_impl
from pipeline.corpus_layout import CORPUS_DIR
from pipeline.output.audit_report import render_audit_markdown
from pipeline.runtime_paths import ensure_repo_tmp_dir


OUTPUT_DIR = ensure_repo_tmp_dir() / "canonical_corpus_audit"
JSON_REPORT_PATH = OUTPUT_DIR / "summary.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit canonical corpus quality and rank the most broken papers.")
    parser.add_argument("--top", type=int, default=10, help="Number of papers to include in the markdown summary.")
    return parser.parse_args()


def audit_corpus() -> dict[str, object]:
    return audit_corpus_impl(
        docs_dir=CORPUS_DIR,
        json_report_path=JSON_REPORT_PATH,
        markdown_report_path=MARKDOWN_REPORT_PATH,
    )


def run_audit_corpus(
    args: argparse.Namespace,
    *,
    audit_corpus_fn: Callable[[], dict[str, object]] = audit_corpus,
    render_markdown_fn: Callable[..., str] = render_audit_markdown,
    output_dir: Path = OUTPUT_DIR,
    json_report_path: Path = JSON_REPORT_PATH,
    markdown_report_path: Path = MARKDOWN_REPORT_PATH,
    print_fn: Callable[..., None] = print,
) -> int:
    report = audit_corpus_fn()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown_fn(report, top_n=max(1, args.top))
    markdown_report_path.write_text(markdown, encoding="utf-8")
    print_fn(markdown, end="")
    return 0


def main() -> int:
    return run_audit_corpus(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
