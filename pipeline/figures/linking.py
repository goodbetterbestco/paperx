#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from pipeline.native_stderr import open_pdf_with_diagnostics
from pipeline.corpus_layout import (
    CORPUS_DIR,
    ProjectLayout,
    current_layout,
    display_path,
    figure_manifest_path,
    figures_dir as corpus_figures_dir,
    paper_uid,
)
from pipeline.corpus.metadata import (
    build_figure_expectations,
    discover_paper_pdf_paths,
    paper_figure_metadata,
    paper_id_from_pdf_path,
)
from pipeline.figures.labels import caption_label

try:
    import fitz  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "PyMuPDF is required. Install it first, for example:\n"
        "python3 -m pip install pymupdf"
    ) from exc


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = CORPUS_DIR

REFERENCE_SEQUENCE_RE = re.compile(
    r"\b(?:Fig(?:ure)?s?\.?)\s*((?:[A-Za-z]?\d+(?:\.\d+)*[A-Za-z]?)(?:\s*(?:,|and|&)\s*[A-Za-z]?\d+(?:\.\d+)*[A-Za-z]?)+|[A-Za-z]?\d+(?:\.\d+)*[A-Za-z]?)",
    re.IGNORECASE,
)
REFERENCE_LABEL_RE = re.compile(r"[A-Za-z]?\d+(?:\.\d+)*[A-Za-z]?")
PAGE_NUMBER_RE = re.compile(r"^[0-9]{1,3}$")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_label_key(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def _resolve_manifest_relative_path(path_value: str, *, layout: ProjectLayout | None = None) -> Path:
    active_layout = layout or current_layout()
    candidate_bases: list[Path] = []
    corpus_parent = active_layout.corpus_root.parent
    corpus_root_from_engine = active_layout.engine_root / "corpus"
    for base in (
        active_layout.source_root,
        active_layout.resolved_data_root(),
        active_layout.resolved_figures_root(),
        corpus_parent,
        corpus_root_from_engine,
        ROOT,
        active_layout.corpus_root,
    ):
        if base not in candidate_bases:
            candidate_bases.append(base)
    for base in candidate_bases:
        candidate = base / path_value
        if candidate.exists():
            return candidate
    return corpus_parent / path_value


def resolve_manifest_pdf_path(manifest: dict[str, Any], *, layout: ProjectLayout | None = None) -> Path:
    artifacts = manifest.get("artifacts") or {}
    pdf_path = artifacts.get("pdf")
    if pdf_path:
        return _resolve_manifest_relative_path(str(pdf_path), layout=layout)
    return _resolve_manifest_relative_path(str(manifest["source_pdf"]), layout=layout)


def resolve_manifest_figures_dir(manifest: dict[str, Any], *, layout: ProjectLayout | None = None) -> Path:
    artifacts = manifest.get("artifacts") or {}
    figures_dir = artifacts.get("figures_dir")
    if figures_dir:
        return _resolve_manifest_relative_path(str(figures_dir), layout=layout)
    return corpus_figures_dir(str(manifest["id"]), layout=layout)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_figure_manifest(
    paper_id: str,
    records: list[dict[str, Any]],
    *,
    paper_uid_value: str,
    layout: ProjectLayout | None = None,
) -> Path:
    manifest_path = figure_manifest_path(paper_id, layout=layout)
    payload = {
        "paper_id": paper_id,
        "paper_uid": paper_uid_value,
        "records": [
            {
                "figure_id": record["figure_id"],
                "label": record["label"],
                "page": record["page"],
                "image_path": record["image_path"],
                "caption_text": record["caption_text"],
                "figure_bbox": record["figure_bbox"],
                "caption_bbox": record["caption_bbox"],
                "link_mode": record["link_mode"],
                "sources": record["sources"],
            }
            for record in records
        ]
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path
def summarize_figure_expectations(figure_expectations: dict[str, Any] | None, actual_count: int) -> dict[str, Any]:
    expectations = figure_expectations or {}
    expected_count = expectations.get("expected_semantic_figure_count")
    expected_no_figures = bool(expectations.get("expected_no_semantic_figures"))

    summary: dict[str, Any] = {
        "expected_semantic_figure_count": expected_count,
        "expected_no_semantic_figures": expected_no_figures,
        "semantic_figure_expectation_status": "unknown",
        "semantic_figure_count_gap": None,
    }

    if expected_no_figures:
        summary["semantic_figure_expectation_status"] = "expected_none" if actual_count == 0 else "unexpected_figures"
        summary["semantic_figure_count_gap"] = actual_count
        return summary

    if expected_count is None:
        return summary

    gap = actual_count - int(expected_count)
    if gap == 0:
        status = "matched"
    elif gap < 0:
        status = "underlinked"
    else:
        status = "overlinked"

    summary["semantic_figure_expectation_status"] = status
    summary["semantic_figure_count_gap"] = gap
    return summary


def rect_to_dict(rect: fitz.Rect) -> dict[str, float]:
    return {
        "x0": round(rect.x0, 2),
        "y0": round(rect.y0, 2),
        "x1": round(rect.x1, 2),
        "y1": round(rect.y1, 2),
        "width": round(rect.width, 2),
        "height": round(rect.height, 2),
    }


def union_rects(rects: list[fitz.Rect]) -> fitz.Rect:
    current = fitz.Rect(rects[0])
    for rect in rects[1:]:
        current.include_rect(rect)
    return current


def overlap_ratio(rect: fitz.Rect, x0: float, x1: float) -> float:
    overlap = max(0.0, min(rect.x1, x1) - max(rect.x0, x0))
    width = max(1.0, min(rect.width, x1 - x0))
    return overlap / width


def is_wide(rect: fitz.Rect, page_rect: fitz.Rect) -> bool:
    return rect.width / max(page_rect.width, 1.0) >= 0.6


def body_text_frame_scope(
    page_rect: fitz.Rect,
    text_blocks: list[dict[str, Any]],
) -> tuple[float, float] | None:
    body_rects = [
        block["rect"]
        for block in text_blocks
        if is_body_text(block["text"])
        and block["rect"].width / max(page_rect.width, 1.0) >= 0.45
    ]
    if not body_rects:
        return None

    x0 = max(page_rect.x0, min(rect.x0 for rect in body_rects))
    x1 = min(page_rect.x1, max(rect.x1 for rect in body_rects))
    if x1 <= x0:
        return None

    scope_width = x1 - x0
    if scope_width / max(page_rect.width, 1.0) < 0.58:
        return None
    return x0, x1


def scope_from_rect(
    page_rect: fitz.Rect,
    rect: fitz.Rect,
    text_blocks: list[dict[str, Any]] | None = None,
) -> tuple[float, float]:
    page_width = page_rect.width
    margin = page_width * 0.04
    gutter = page_width * 0.03
    mid_x = page_rect.x0 + (page_width / 2)
    center_x = (rect.x0 + rect.x1) / 2

    if text_blocks:
        text_frame_scope = body_text_frame_scope(page_rect, text_blocks)
        if text_frame_scope is not None:
            return text_frame_scope

    if is_wide(rect, page_rect):
        return page_rect.x0 + margin, page_rect.x1 - margin
    if center_x <= mid_x:
        return page_rect.x0 + margin, mid_x - gutter
    return mid_x + gutter, page_rect.x1 - margin


def blocks_overlap_scope(rect: fitz.Rect, scope: tuple[float, float]) -> bool:
    x0, x1 = scope
    return overlap_ratio(rect, x0, x1) >= 0.2 or (x0 <= ((rect.x0 + rect.x1) / 2) <= x1)
def is_body_text(text: str) -> bool:
    if caption_label(text):
        return False
    compact = normalize_text(text)
    if len(compact) < 70:
        return False
    if re.match(r"^(?:\(?[a-zA-Z0-9]\)?|[0-9.]+)$", compact):
        return False
    return True


def is_aux_text(text: str) -> bool:
    compact = normalize_text(text)
    return bool(compact) and len(compact) < 90


def extract_reference_labels(text: str) -> set[str]:
    normalized = normalize_text(text)
    labels: set[str] = set()
    for match in REFERENCE_SEQUENCE_RE.finditer(normalized):
        for raw_label in REFERENCE_LABEL_RE.findall(match.group(1)):
            labels.add(normalize_label_key(raw_label))
    return labels


def dedupe_visuals(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    for item in items:
        rect = item["rect"]
        duplicate = False
        for existing in deduped:
            other = existing["rect"]
            intersection = rect & other
            if intersection.is_empty:
                continue
            inter_area = intersection.get_area()
            union_area = rect.get_area() + other.get_area() - inter_area
            if union_area > 0 and inter_area / union_area > 0.95:
                duplicate = True
                break
        if not duplicate:
            deduped.append(item)
    return deduped


def extract_pdf_text_blocks(page: fitz.Page) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        text = normalize_text(" ".join(span["text"] for line in block["lines"] for span in line["spans"]))
        if text:
            blocks.append({"rect": fitz.Rect(block["bbox"]), "text": text, "source": "pdf_text"})
    return sorted(blocks, key=lambda block: (block["rect"].y0, block["rect"].x0))


def extract_pdf_visual_blocks(doc: fitz.Document, page: fitz.Page) -> list[dict[str, Any]]:
    visuals: list[dict[str, Any]] = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] == 0:
            continue
        rect = fitz.Rect(block["bbox"])
        if rect.width >= 12 and rect.height >= 12:
            visuals.append({"rect": rect, "source": f"block_type_{block['type']}"})

    for image_info in page.get_images(full=True):
        xref = int(image_info[0])
        for rect in page.get_image_rects(xref):
            if rect.width >= 12 and rect.height >= 12:
                visuals.append({"rect": fitz.Rect(rect), "source": f"image_xref_{xref}"})

    return dedupe_visuals(visuals)


def extract_drawing_rects(page: fitz.Page) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = fitz.Rect(drawing["rect"])
        if rect.width < 2 or rect.height < 2:
            continue
        if rect.get_area() < 50 and max(rect.width, rect.height) < 20:
            continue
        rects.append(rect)
    return rects


def collect_caption_blocks(text_blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [block for block in text_blocks if caption_label(block["text"])]


def build_manifest_from_pdf_path(pdf_path: Path, *, layout: ProjectLayout | None = None) -> dict[str, Any]:
    active_layout = layout or current_layout()
    paper_id = paper_id_from_pdf_path(pdf_path, layout=active_layout)
    paper_uid_value = paper_uid(paper_id)
    manifest: dict[str, Any] = {
        "id": paper_id,
        "paper_uid": paper_uid_value,
        "source_pdf": display_path(pdf_path, layout=active_layout),
        "artifacts": {
            "pdf": display_path(pdf_path, layout=active_layout),
            "figures_dir": display_path(corpus_figures_dir(paper_id, layout=active_layout), layout=active_layout),
        },
        "stats": {},
    }
    metadata = paper_figure_metadata(paper_id, layout=active_layout)
    if metadata is not None:
        figure_expectations = build_figure_expectations(metadata)
        if figure_expectations:
            manifest["figure_expectations"] = figure_expectations
    return manifest


def discover_manifests(*, layout: ProjectLayout | None = None) -> list[dict[str, Any]]:
    active_layout = layout or current_layout()
    return [build_manifest_from_pdf_path(pdf_path, layout=active_layout) for pdf_path in discover_paper_pdf_paths(layout=active_layout)]


def render_crop_if_missing(page: fitz.Page, rect: fitz.Rect, output_path: Path) -> bool:
    if output_path.exists():
        return False
    render_crop(page, rect, output_path)
    return True


def choose_side(
    caption_rect: fitz.Rect,
    above: list[dict[str, Any]],
    below: list[dict[str, Any]],
) -> str | None:
    if above and not below:
        return "above"
    if below and not above:
        return "below"
    if not above and not below:
        return None

    above_gap = caption_rect.y0 - max(item["rect"].y1 for item in above)
    below_gap = min(item["rect"].y0 for item in below) - caption_rect.y1
    if above_gap <= below_gap:
        return "above"
    return "below"


def build_fallback_rect(
    page_rect: fitz.Rect,
    caption_rect: fitz.Rect,
    scope: tuple[float, float],
    text_blocks: list[dict[str, Any]],
) -> fitz.Rect | None:
    relevant_body = [
        block["rect"]
        for block in text_blocks
        if is_body_text(block["text"]) and blocks_overlap_scope(block["rect"], scope)
    ]
    relevant_captions = [
        block["rect"]
        for block in text_blocks
        if caption_label(block["text"]) and blocks_overlap_scope(block["rect"], scope)
    ]

    top_limit = max(
        [rect.y1 for rect in relevant_body if rect.y1 <= caption_rect.y0]
        + [rect.y1 for rect in relevant_captions if rect.y1 <= caption_rect.y0],
        default=page_rect.y0 + page_rect.height * 0.05,
    )
    bottom_limit = min(
        [rect.y0 for rect in relevant_body if rect.y0 >= caption_rect.y1]
        + [rect.y0 for rect in relevant_captions if rect.y0 >= caption_rect.y1],
        default=page_rect.y1 - page_rect.height * 0.05,
    )

    candidate = fitz.Rect(scope[0], top_limit + 4, scope[1], caption_rect.y0 - 4)
    if candidate.width >= 40 and candidate.height >= 40:
        return candidate & page_rect

    candidate = fitz.Rect(scope[0], caption_rect.y1 + 4, scope[1], bottom_limit - 4)
    if candidate.width >= 40 and candidate.height >= 40:
        return candidate & page_rect
    return None


def is_probable_page_number_text(text: str) -> bool:
    compact = normalize_text(text)
    return bool(PAGE_NUMBER_RE.fullmatch(compact))


def expand_rect(rect: fitz.Rect, page_rect: fitz.Rect, x_pad: float, y_pad: float) -> fitz.Rect:
    expanded = fitz.Rect(rect)
    expanded.x0 = max(page_rect.x0, expanded.x0 - x_pad)
    expanded.y0 = max(page_rect.y0, expanded.y0 - y_pad)
    expanded.x1 = min(page_rect.x1, expanded.x1 + x_pad)
    expanded.y1 = min(page_rect.y1, expanded.y1 + y_pad)
    return expanded


def collect_figure_text_rects(
    page_rect: fitz.Rect,
    caption_block: dict[str, Any],
    text_blocks: list[dict[str, Any]],
    figure_rect: fitz.Rect,
    side: str,
) -> list[fitz.Rect]:
    x_pad = page_rect.width * 0.08
    y_pad = page_rect.height * 0.02
    horizontal_zone = expand_rect(figure_rect, page_rect, x_pad=x_pad, y_pad=0)
    vertical_min = figure_rect.y0 - y_pad if side == "above" else caption_block["rect"].y1 - y_pad
    vertical_max = caption_block["rect"].y0 + y_pad if side == "above" else figure_rect.y1 + y_pad
    footer_guard = caption_block["rect"].y0 - page_rect.height * 0.06
    caption_guard = caption_block["rect"].y0 - page_rect.height * 0.025

    text_rects: list[fitz.Rect] = []
    for block in text_blocks:
        if block is caption_block:
            continue
        text = block["text"]
        rect = block["rect"]
        if caption_label(text) or is_probable_page_number_text(text):
            continue
        alnum_count = sum(char.isalnum() for char in text)
        letter_count = sum(char.isalpha() for char in text)
        if alnum_count < 2:
            continue
        if rect.y0 < vertical_min or rect.y1 > vertical_max:
            continue
        if side == "above" and rect.y0 >= caption_guard:
            continue
        if side == "above" and rect.y0 >= footer_guard and letter_count < 4:
            continue
        if rect.x1 < horizontal_zone.x0 or rect.x0 > horizontal_zone.x1:
            continue
        if is_body_text(text) and rect.width / max(page_rect.width, 1.0) >= 0.62:
            continue
        text_rects.append(rect)

    return text_rects


def finalize_figure_rect(page_rect: fitz.Rect, rects: list[fitz.Rect]) -> fitz.Rect:
    figure_rect = union_rects(rects)
    return expand_rect(
        figure_rect,
        page_rect,
        x_pad=page_rect.width * 0.015,
        y_pad=page_rect.height * 0.01,
    )


def choose_visual_region(
    page_rect: fitz.Rect,
    caption_block: dict[str, Any],
    text_blocks: list[dict[str, Any]],
    visual_blocks: list[dict[str, Any]],
    drawing_rects: list[fitz.Rect],
) -> tuple[fitz.Rect | None, str, list[str]]:
    caption_rect = caption_block["rect"]
    scope = scope_from_rect(page_rect, caption_rect, text_blocks)

    relevant_body = [
        block["rect"]
        for block in text_blocks
        if is_body_text(block["text"]) and blocks_overlap_scope(block["rect"], scope)
    ]
    upper_barrier = max([rect.y1 for rect in relevant_body if rect.y1 <= caption_rect.y0], default=page_rect.y0)
    lower_barrier = min([rect.y0 for rect in relevant_body if rect.y0 >= caption_rect.y1], default=page_rect.y1)

    above = [
        block for block in visual_blocks
        if block["rect"].y1 <= caption_rect.y0 + 8
        and block["rect"].y0 >= upper_barrier - 8
        and blocks_overlap_scope(block["rect"], scope)
    ]
    below = [
        block for block in visual_blocks
        if block["rect"].y0 >= caption_rect.y1 - 8
        and block["rect"].y1 <= lower_barrier + 8
        and blocks_overlap_scope(block["rect"], scope)
    ]

    drawing_candidates_above = [
        rect for rect in drawing_rects
        if rect.y1 <= caption_rect.y0 + 8
        and rect.y0 >= upper_barrier - 8
    ]
    drawing_candidates_below = [
        rect for rect in drawing_rects
        if rect.y0 >= caption_rect.y1 - 8
        and rect.y1 <= lower_barrier + 8
    ]
    drawing_side = choose_side(
        caption_rect,
        [{"rect": rect} for rect in drawing_candidates_above],
        [{"rect": rect} for rect in drawing_candidates_below],
    )
    combined_side = choose_side(
        caption_rect,
        [*above, *[{"rect": rect} for rect in drawing_candidates_above]],
        [*below, *[{"rect": rect} for rect in drawing_candidates_below]],
    )
    selected_visuals = above if combined_side == "above" else below if combined_side == "below" else []
    selected_drawings = (
        drawing_candidates_above
        if combined_side == "above"
        else drawing_candidates_below
        if combined_side == "below"
        else []
    )
    if selected_visuals or selected_drawings:
        figure_rects = [block["rect"] for block in selected_visuals] + list(selected_drawings)
        figure_rect = union_rects(figure_rects)
        text_rects = collect_figure_text_rects(page_rect, caption_block, text_blocks, figure_rect, combined_side)
        sources = sorted(
            {
                *(block["source"] for block in selected_visuals),
                *(["drawing_rects"] if selected_drawings else []),
            }
        )
        return (
            finalize_figure_rect(page_rect, [*figure_rects, *text_rects]) & page_rect,
            "visual_blocks" if selected_visuals else "drawing_fallback",
            sources,
        )

    fallback_rect = build_fallback_rect(page_rect, caption_rect, scope, text_blocks)
    if fallback_rect is not None:
        return (fallback_rect, "column_gap_fallback", ["heuristic_scope"])
    return (None, "none", [])


def render_crop(page: fitz.Page, rect: fitz.Rect, output_path: Path) -> None:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect, alpha=False)
    pixmap.save(output_path)


def _close_document(doc: fitz.Document) -> None:
    doc.close()


def _page_state_from_document(doc: fitz.Document, page_index: int) -> dict[str, Any]:
    page = doc.load_page(page_index)
    page_rect = fitz.Rect(page.rect)
    return {
        "page": page_index + 1,
        "page_rect": page_rect,
        "text_blocks": extract_pdf_text_blocks(page),
        "visual_blocks": extract_pdf_visual_blocks(doc, page),
        "drawing_rects": extract_drawing_rects(page),
    }


def _load_page(doc: fitz.Document, page_index: int) -> fitz.Page:
    return doc.load_page(page_index)


def collect_references(label: str, caption_page: int, page_states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target = normalize_label_key(label)
    references: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()

    for page_state in page_states:
        for block in page_state["text_blocks"]:
            if caption_label(block["text"]):
                continue
            labels = extract_reference_labels(block["text"])
            if target not in labels:
                continue

            dedupe_key = (page_state["page"], block["text"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            references.append(
                {
                    "page": page_state["page"],
                    "text": block["text"],
                    "bbox": rect_to_dict(block["rect"]),
                    "source": block.get("source", "text"),
                    "relation": "same_page" if page_state["page"] == caption_page else "cross_page",
                }
            )

    return references


def process_paper(
    manifest: dict[str, Any],
    *,
    layout: ProjectLayout | None = None,
) -> tuple[dict[str, Any], int]:
    active_layout = layout or current_layout()
    paper_id = str(manifest["id"])
    paper_uid_value = str(manifest.get("paper_uid") or paper_uid(paper_id))
    source_pdf = resolve_manifest_pdf_path(manifest, layout=active_layout)
    figures_dir = resolve_manifest_figures_dir(manifest, layout=active_layout)
    figures_dir.mkdir(parents=True, exist_ok=True)

    doc = open_pdf_with_diagnostics(
        f"{paper_id} stage=figure-linking-open",
        source_pdf,
        fitz_module=fitz,
    )
    try:
        records: list[dict[str, Any]] = []
        used_ids: set[str] = set()
        page_states = [
            _page_state_from_document(doc, page_index)
            for page_index in range(doc.page_count)
        ]

        for page_state in page_states:
            page_index = int(page_state["page"]) - 1
            page = _load_page(doc, page_index)
            page_rect = page_state["page_rect"]
            text_blocks = page_state["text_blocks"]
            visual_blocks = page_state["visual_blocks"]
            captions = collect_caption_blocks(text_blocks)
            drawing_rects = page_state["drawing_rects"]

            for sequence, caption_block in enumerate(captions, start=1):
                label = caption_label(caption_block["text"])
                if not label:
                    continue

                rect, link_mode, sources = choose_visual_region(page_rect, caption_block, text_blocks, visual_blocks, drawing_rects)
                if rect is None or rect.width < 30 or rect.height < 30:
                    continue

                base_id = f"figure-{slugify(label)}"
                figure_id = base_id
                suffix = 2
                while figure_id in used_ids:
                    figure_id = f"{base_id}-{suffix}"
                    suffix += 1
                used_ids.add(figure_id)

                filename = f"figure_{paper_uid_value}_{len(records) + 1:03d}.png"
                output_path = figures_dir / filename
                render_crop_if_missing(page, rect, output_path)

                records.append(
                    {
                        "figure_id": figure_id,
                        "label": label,
                        "page": page_index + 1,
                        "page_size": rect_to_dict(page_rect),
                        "caption_text": caption_block["text"],
                        "caption_bbox": rect_to_dict(caption_block["rect"]),
                        "figure_bbox": rect_to_dict(rect),
                        "image_path": display_path(output_path, layout=active_layout),
                        "link_mode": link_mode,
                        "sources": sources,
                        "sequence_on_page": sequence,
                        "references": [],
                        "reference_count": 0,
                    }
                )

        for record in records:
            references = collect_references(record["label"], int(record["page"]), page_states)
            record["references"] = references
            record["reference_count"] = len(references)

        manifest_path = write_figure_manifest(
            paper_id,
            records,
            paper_uid_value=paper_uid_value,
            layout=active_layout,
        )
        manifest.setdefault("artifacts", {})
        manifest["paper_uid"] = paper_uid_value
        manifest["artifacts"]["figures_dir"] = display_path(figures_dir, layout=active_layout)
        manifest["artifacts"]["figures_manifest"] = display_path(manifest_path, layout=active_layout)
        manifest.setdefault("stats", {})
        manifest["stats"]["semantic_figure_count"] = len(records)
        manifest["stats"]["semantic_figure_link_modes"] = {
            mode: sum(1 for record in records if record["link_mode"] == mode)
            for mode in sorted({record["link_mode"] for record in records})
        }
        manifest["stats"]["semantic_figure_reference_count"] = sum(record["reference_count"] for record in records)
        manifest["stats"].update(summarize_figure_expectations(manifest.get("figure_expectations"), len(records)))
        return manifest, len(records)
    finally:
        _close_document(doc)

def main() -> int:
    layout = current_layout()
    manifests = discover_manifests(layout=layout)
    for manifest in manifests:
        updated_manifest, count = process_paper(manifest, layout=layout)
        print(f"{updated_manifest['id']}: linked {count} semantic figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
