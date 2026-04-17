#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from pipeline.corpus.audit import (
    _block_text,
    _caption_looks_noisy,
    _is_display_lead_in,
    _math_text_looks_contaminated,
    _section_title_looks_bad,
    _starts_like_paragraph_continuation,
    _text_looks_affiliation_like,
    _text_looks_algorithmic,
    _text_looks_heading_like,
    _text_looks_noisy,
    _text_looks_short_label_lead_in,
    audit_corpus as _audit_corpus_impl,
    audit_document,
    audit_missing_canonical,
)
from pipeline.output.audit_report import render_audit_markdown
from pipeline.runtime_paths import ensure_repo_tmp_dir
from pipeline.text_utils import DOCS_DIR


OUTPUT_DIR = ensure_repo_tmp_dir() / "canonical_corpus_audit"
JSON_REPORT_PATH = OUTPUT_DIR / "summary.json"
MARKDOWN_REPORT_PATH = OUTPUT_DIR / "summary.md"

render_markdown = render_audit_markdown


def audit_corpus() -> dict[str, object]:
    return _audit_corpus_impl(
        docs_dir=DOCS_DIR,
        json_report_path=JSON_REPORT_PATH,
        markdown_report_path=MARKDOWN_REPORT_PATH,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit canonical corpus quality and rank the most broken papers.")
    parser.add_argument("--top", type=int, default=10, help="Number of papers to include in the markdown summary.")
    args = parser.parse_args()

    report = audit_corpus()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown(report, top_n=max(1, args.top))
    MARKDOWN_REPORT_PATH.write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
