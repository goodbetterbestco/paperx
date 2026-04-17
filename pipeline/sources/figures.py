from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import CORPUS_DIR, ProjectLayout, figure_manifest_path, paper_pdf_path
DOCS_DIR = CORPUS_DIR

from pipeline.policies.figure_caption import apply_figure_caption_policy
from pipeline.types import default_review


def _figure_manifest_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return figure_manifest_path(paper_id, layout=layout)


def ensure_figure_manifest(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    manifest_path = _figure_manifest_path(paper_id, layout=layout)
    if manifest_path.exists():
        return manifest_path

    from pipeline.figures.linking import build_manifest_from_pdf_path, process_paper

    pdf_path = paper_pdf_path(paper_id, layout=layout)
    manifest = build_manifest_from_pdf_path(pdf_path.resolve(), layout=layout)
    process_paper(manifest, layout=layout)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing figure manifest after extraction: {manifest_path}")
    return manifest_path


def _canonical_figure_id(record: dict[str, Any]) -> str:
    manifest_id = str(record.get("figure_id", "")).strip().lower()
    if manifest_id.startswith("figure-"):
        return "fig-" + manifest_id.removeprefix("figure-")
    if manifest_id:
        return manifest_id
    return f"fig-{str(record['label']).lower()}"


def _canonical_figure_label(record: dict[str, Any]) -> str:
    caption_text = str(record.get("caption_text", "")).strip()
    prefix = caption_text.split(":", 1)[0].strip()
    if prefix.lower().startswith(("figure ", "fig.")):
        return prefix.replace("Fig.", "Figure").strip()
    return f"Figure {record['label']}"


def _canonical_figure(paper_id: str, record: dict[str, Any]) -> dict[str, Any]:
    bbox = dict(record["figure_bbox"])
    figure_id = _canonical_figure_id(record)
    raw_caption = str(record["caption_text"]).split(":", 1)[1].strip() if ":" in str(record["caption_text"]) else str(record["caption_text"])
    return {
        "id": figure_id,
        "label": _canonical_figure_label(record),
        "caption": apply_figure_caption_policy(paper_id, figure_id, raw_caption),
        "image_path": str(record["image_path"]),
        "page": int(record["page"]),
        "bbox": bbox,
        "display_size_in": {
            "width": round(float(bbox["width"]) / 72.0, 4),
            "height": round(float(bbox["height"]) / 72.0, 4),
        },
        "provenance": {
            "link_mode": str(record.get("link_mode", "")),
            "sources": list(record.get("sources", [])),
            "caption_bbox": record.get("caption_bbox", {}),
        },
        "review": default_review(risk="medium"),
    }


def extract_figures(paper_id: str, *, layout: ProjectLayout | None = None) -> list[dict[str, Any]]:
    manifest_path = ensure_figure_manifest(paper_id, layout=layout)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [_canonical_figure(paper_id, record) for record in payload.get("records", [])]
