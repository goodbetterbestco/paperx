from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import canonical_path, canonical_sources_dir, review_draft_path
from pipeline.render_review_from_canonical import render_document
from pipeline.validate_canonical import validate_canonical


def build_summary(document: dict[str, Any]) -> dict[str, int]:
    return {
        "sections": len(document.get("sections", [])),
        "blocks": len(document.get("blocks", [])),
        "math": len(document.get("math", [])),
        "figures": len(document.get("figures", [])),
        "references": len(document.get("references", [])),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_canonical_outputs(
    paper_id: str,
    document: dict[str, Any],
    *,
    include_review: bool = True,
) -> dict[str, Any]:
    decision_artifacts = document.pop("_decision_artifacts", None)
    validate_canonical(document)
    review_markdown = render_document(document) if include_review else ""
    canonical_target = canonical_path(paper_id)
    review_target = review_draft_path(paper_id)
    sources_target = canonical_sources_dir(paper_id)
    canonical_target.parent.mkdir(parents=True, exist_ok=True)
    canonical_target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if include_review:
        review_target.parent.mkdir(parents=True, exist_ok=True)
        review_target.write_text(review_markdown, encoding="utf-8")
    if isinstance(decision_artifacts, dict):
        sources_target.mkdir(parents=True, exist_ok=True)
        title_decision = decision_artifacts.get("title")
        if isinstance(title_decision, dict):
            _write_json(sources_target / "title-decision.json", title_decision)
        abstract_decision = decision_artifacts.get("abstract")
        if isinstance(abstract_decision, dict):
            _write_json(sources_target / "abstract-decision.json", abstract_decision)
    return {
        "canonical_path": str(canonical_target),
        "review_path": str(review_target),
        "review_chars": len(review_markdown),
        **build_summary(document),
    }
