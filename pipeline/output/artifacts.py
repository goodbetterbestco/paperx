from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from pipeline.corpus_layout import ProjectLayout, canonical_path, review_draft_path
from pipeline.output.review_renderer import render_document
from pipeline.output.validation import validate_canonical


def build_summary(document: dict[str, Any]) -> dict[str, int]:
    return {
        "sections": len(document.get("sections", [])),
        "blocks": len(document.get("blocks", [])),
        "math": len(document.get("math", [])),
        "figures": len(document.get("figures", [])),
        "references": len(document.get("references", [])),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    write_json(path, payload)


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


def write_canonical_outputs_impl(
    paper_id: str,
    document: dict[str, Any],
    *,
    include_review: bool = True,
    layout: ProjectLayout | None = None,
    build_summary: Callable[[dict[str, Any]], dict[str, int]],
    write_json: Callable[[Path, Any], None],
    validate_canonical: Callable[[dict[str, Any]], None],
    render_document: Callable[[dict[str, Any]], str],
) -> dict[str, Any]:
    validate_canonical(document)
    review_markdown = render_document(document) if include_review else ""
    canonical_target = canonical_path(paper_id, layout=layout)
    review_target = review_draft_path(paper_id, layout=layout)
    canonical_target.parent.mkdir(parents=True, exist_ok=True)
    canonical_target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if include_review:
        review_target.parent.mkdir(parents=True, exist_ok=True)
        review_target.write_text(review_markdown, encoding="utf-8")
    return {
        "canonical_path": str(canonical_target),
        "review_path": str(review_target),
        "review_chars": len(review_markdown),
        **build_summary(document),
    }


__all__ = [
    "_write_json",
    "build_summary",
    "render_document",
    "validate_canonical",
    "write_canonical_outputs",
    "write_canonical_outputs_impl",
    "write_json",
]
