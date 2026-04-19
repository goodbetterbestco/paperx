from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import ProjectLayout, canonical_sources_dir
from pipeline.math.review_policy import review_for_math_entry
from pipeline.types import LayoutBlock, default_formula_conversion, default_review


def _paper_sources_dir(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return canonical_sources_dir(paper_id, layout=layout)


def _load_layout_payload(path: Path, *, default_engine: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    blocks: list[LayoutBlock] = []
    for index, block in enumerate(payload.get("blocks", []), start=1):
        blocks.append(
            LayoutBlock(
                id=str(block.get("id") or f"{default_engine}-layout-{index:04d}"),
                page=int(block["page"]),
                order=int(block.get("order", index)),
                text=str(block.get("text", "")),
                role=str(block.get("role", "paragraph")),
                bbox=dict(block.get("bbox", {})),
                engine=str(payload.get("engine", default_engine)),
                meta=dict(block.get("meta", {})),
            )
        )
    return {
        "engine": str(payload.get("engine", default_engine)),
        "pdf_path": payload.get("pdf_path"),
        "page_count": int(payload.get("page_count", 0) or 0),
        "page_sizes_pt": list(payload.get("page_sizes_pt", [])),
        "blocks": blocks,
    }


def external_layout_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return _paper_sources_dir(paper_id, layout=layout) / "layout.json"


def external_math_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return _paper_sources_dir(paper_id, layout=layout) / "math.json"


def ocr_normalized_pdf_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return _paper_sources_dir(paper_id, layout=layout) / "ocr-normalized.pdf"


def ocr_prepass_report_path(paper_id: str, *, layout: ProjectLayout | None = None) -> Path:
    return _paper_sources_dir(paper_id, layout=layout) / "ocr-prepass.json"


def load_external_layout(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any] | None:
    return _load_layout_payload(external_layout_path(paper_id, layout=layout), default_engine="external_layout")


def load_mathpix_layout(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any] | None:
    return _load_layout_payload(
        _paper_sources_dir(paper_id, layout=layout) / "mathpix-layout.json",
        default_engine="mathpix_layout",
    )


def _normalize_external_math_item(
    item: dict[str, Any],
    *,
    default_engine: str,
    index: int,
) -> dict[str, Any]:
    kind = str(item.get("kind", "display"))
    normalized: dict[str, Any] = {
        "id": str(item.get("id") or f"external-math-{index:04d}"),
        "kind": kind,
        "display_latex": str(item.get("display_latex", "")),
        "semantic_expr": item.get("semantic_expr"),
        "compiled_targets": dict(item.get("compiled_targets", {})),
        "conversion": dict(item.get("conversion", default_formula_conversion())),
        "source_spans": list(item.get("source_spans", [])),
        "alternates": list(item.get("alternates", [])),
        "review": dict(item.get("review", default_review(risk="medium"))),
        "external_engine": default_engine,
    }
    if "equation_number" in item:
        normalized["equation_number"] = item.get("equation_number")
    if kind == "group":
        normalized["items"] = [
            {
                "display_latex": str(group_item.get("display_latex", "")),
                "semantic_expr": group_item.get("semantic_expr"),
                "compiled_targets": dict(group_item.get("compiled_targets", {})),
                "conversion": dict(group_item.get("conversion", default_formula_conversion())),
            }
            for group_item in item.get("items", [])
        ]
    normalized["review"] = review_for_math_entry(normalized)
    return normalized


def load_external_math(paper_id: str, *, layout: ProjectLayout | None = None) -> dict[str, Any] | None:
    path = external_math_path(paper_id, layout=layout)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    engine = str(payload.get("engine", "external_math"))
    entries = [
        _normalize_external_math_item(entry, default_engine=engine, index=index)
        for index, entry in enumerate(payload.get("entries", []), start=1)
    ]
    return {
        "engine": engine,
        "entries": entries,
    }
