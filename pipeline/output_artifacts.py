from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout
from pipeline.output.artifacts import build_summary as build_summary_impl, write_canonical_outputs_impl
from pipeline.output.review_renderer import render_document
from pipeline.output.validation import validate_canonical


def build_summary(document: dict[str, Any]) -> dict[str, int]:
    return build_summary_impl(document)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_canonical_outputs(
    paper_id: str,
    document: dict[str, Any],
    *,
    include_review: bool = True,
    layout: ProjectLayout | None = None,
) -> dict[str, Any]:
    return write_canonical_outputs_impl(
        paper_id,
        document,
        include_review=include_review,
        layout=layout,
        build_summary=build_summary,
        write_json=_write_json,
        validate_canonical=validate_canonical,
        render_document=render_document,
    )
