from __future__ import annotations

import json
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from paper_pipeline.corpus_layout import CORPUS_DIR, paper_pdf_path
from paper_pipeline.external_sources import external_layout_path, external_math_path
from paper_pipeline.extract_layout import extract_layout
from paper_pipeline.math_review_policy import review_for_math_entry
from paper_pipeline.runtime_paths import ensure_repo_tmp_dir, runtime_env
from paper_pipeline.text_utils import compact_text
from paper_pipeline.types import default_formula_conversion, default_review

DOCS_DIR = CORPUS_DIR
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
SLASH_RUN_RE = re.compile(r"/+")
SPACE_RE = re.compile(r"\s+")
REF_RE = re.compile(r"^[A-Z][A-Za-z0-9.-]{1,16}\]")
TAG_NUMBER_RE = re.compile(r"\((\d+)\)\s*$")


def _paper_pdf_path(paper_id: str) -> Path:
    return paper_pdf_path(paper_id)


def _docling_output_dir(paper_id: str, output_dir: Path | None = None) -> Path:
    return output_dir or Path(tempfile.mkdtemp(prefix=f"{paper_id}-docling-", dir=str(ensure_repo_tmp_dir())))


def run_docling(
    paper_id: str,
    *,
    output_dir: Path | None = None,
    device: str | None = None,
    page_batch_size: int = 4,
    timeout_seconds: int = 1800,
) -> Path:
    output_dir = _docling_output_dir(paper_id, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = _paper_pdf_path(paper_id)
    device_arg = f" --device {shlex.quote(device)}" if device else ""
    command = [
        "/bin/zsh",
        "-lc",
        " ".join(
            [
                "source /tmp/stepview-kernel-venv/bin/activate &&",
                "docling",
                shlex.quote(str(pdf_path)),
                "--from pdf --to json",
                f"--output {shlex.quote(str(output_dir))}",
                device_arg,
                f"--page-batch-size {page_batch_size}",
                f"--document-timeout {timeout_seconds}",
            ]
        ).replace("  ", " "),
    ]
    subprocess.run(command, check=True, env=runtime_env(), capture_output=True, text=True)
    return output_dir / f"{paper_id}.json"


def _page_heights(layout: dict[str, Any]) -> dict[int, float]:
    return {int(item["page"]): float(item["height"]) for item in layout.get("page_sizes_pt", [])}


def _docling_bbox_to_canonical(raw_bbox: dict[str, Any], page_height: float) -> dict[str, float]:
    left = float(raw_bbox.get("l", 0.0))
    right = float(raw_bbox.get("r", 0.0))
    top = float(raw_bbox.get("t", 0.0))
    bottom = float(raw_bbox.get("b", 0.0))
    y0 = round(page_height - top, 2)
    y1 = round(page_height - bottom, 2)
    x0 = round(left, 2)
    x1 = round(right, 2)
    return {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "width": round(x1 - x0, 2),
        "height": round(y1 - y0, 2),
    }


def _clean_docling_text(text: str) -> str:
    cleaned = CONTROL_RE.sub(" ", text)
    cleaned = cleaned.replace("/-", "-")
    cleaned = cleaned.replace("/;", ";")
    cleaned = cleaned.replace("/:", ":")
    cleaned = cleaned.replace("/.", ".")
    cleaned = cleaned.replace("/,", ",")
    cleaned = cleaned.replace("/(", "(")
    cleaned = cleaned.replace("/)", ")")
    cleaned = cleaned.replace("/[", "[")
    cleaned = cleaned.replace("/]", "]")
    cleaned = cleaned.replace("/&", "&")
    cleaned = cleaned.replace("/=", "=")
    cleaned = cleaned.replace("/+", "+")
    cleaned = cleaned.replace("/<", "<")
    cleaned = cleaned.replace("/>", ">")
    cleaned = cleaned.replace("/\"", "\"")
    cleaned = cleaned.replace("/'", "'")
    cleaned = SLASH_RUN_RE.sub(" ", cleaned)
    cleaned = SPACE_RE.sub(" ", cleaned)
    return compact_text(cleaned)


def _page_number_from_item(item: dict[str, Any]) -> int:
    prov = item.get("prov") or []
    if not prov:
        return 0
    return int(prov[0].get("page_no", 0) or 0)


def _bbox_from_item(item: dict[str, Any], page_heights: dict[int, float]) -> dict[str, float] | None:
    prov = item.get("prov") or []
    if not prov:
        return None
    page_no = int(prov[0].get("page_no", 0) or 0)
    raw_bbox = prov[0].get("bbox") or {}
    page_height = page_heights.get(page_no)
    if page_no <= 0 or not raw_bbox or page_height is None:
        return None
    return _docling_bbox_to_canonical(raw_bbox, page_height)


def _is_reference_text(text: str, page: int, page_count: int) -> bool:
    return page >= max(2, page_count - 3) and bool(REF_RE.match(text))


def _looks_like_title_page_front_matter(page: int, label: str, text: str, seen_abstract: bool) -> bool:
    if page != 1:
        return False
    if label in {"page_footer", "page_header", "formula", "caption"}:
        return False
    if seen_abstract:
        return False
    return True


def _layout_role_for_docling_item(page: int, page_count: int, label: str, text: str, seen_abstract: bool) -> str | None:
    if label in {"page_footer", "page_header"}:
        return None
    if label == "footnote":
        return "footnote"
    if label == "caption":
        return "caption"
    if label == "section_header":
        if _looks_like_title_page_front_matter(page, label, text, seen_abstract):
            return "front_matter"
        return "heading"
    if label in {"text", "list_item", "code"}:
        if _looks_like_title_page_front_matter(page, label, text, seen_abstract):
            return "front_matter"
        if _is_reference_text(text, page, page_count):
            return "reference"
        if label == "list_item":
            return "list_item"
        if label == "code":
            return "code"
        return "paragraph"
    return None


def _equation_number(text: str) -> str | None:
    match = TAG_NUMBER_RE.search(text)
    if match:
        return match.group(0)
    return None


def docling_json_to_external_sources(docling_document: dict[str, Any], paper_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    layout = extract_layout(paper_id)
    page_sizes = list(layout["page_sizes_pt"])
    page_heights = _page_heights(layout)
    page_count = int(layout["page_count"])

    layout_blocks: list[dict[str, Any]] = []
    math_entries: list[dict[str, Any]] = []
    order_by_page: dict[int, int] = {}
    math_index = 1
    seen_abstract = False

    for item in docling_document.get("texts", []):
        label = str(item.get("label", ""))
        page = _page_number_from_item(item)
        bbox = _bbox_from_item(item, page_heights)
        if page <= 0 or bbox is None:
            continue

        text = _clean_docling_text(str(item.get("text") or ""))
        orig = _clean_docling_text(str(item.get("orig") or ""))

        if label == "formula":
            formula_text = orig or text
            if not formula_text:
                continue
            entry: dict[str, Any] = {
                "id": f"docling-eq-{math_index:04d}",
                "kind": "display",
                "display_latex": formula_text,
                "semantic_expr": None,
                "compiled_targets": {},
                "conversion": default_formula_conversion(),
                "source_spans": [{"page": page, "bbox": bbox, "engine": "docling"}],
                "alternates": [],
                "review": default_review(risk="medium"),
            }
            equation_number = _equation_number(formula_text)
            if equation_number:
                entry["equation_number"] = equation_number
            entry["review"] = review_for_math_entry(entry)
            math_entries.append(entry)
            math_index += 1
            continue

        text_value = text or orig
        if not text_value:
            continue
        if text_value.lower().startswith("abstract "):
            seen_abstract = True

        role = _layout_role_for_docling_item(page, page_count, label, text_value, seen_abstract)
        if role is None:
            continue
        order_by_page[page] = order_by_page.get(page, 0) + 1
        layout_blocks.append(
            {
                "id": str(item.get("self_ref") or f"docling-p{page:03d}-b{order_by_page[page]:03d}"),
                "page": page,
                "order": order_by_page[page],
                "role": role,
                "text": text_value,
                "bbox": bbox,
                "meta": {
                    "docling_label": label,
                    "docling_orig": orig,
                },
            }
        )

    external_layout = {
        "engine": "docling",
        "pdf_path": layout["pdf_path"],
        "page_count": layout["page_count"],
        "page_sizes_pt": page_sizes,
        "blocks": layout_blocks,
    }
    external_math = {
        "engine": "docling",
        "entries": math_entries,
    }
    return external_layout, external_math


def write_external_sources(
    paper_id: str,
    external_layout: dict[str, Any],
    external_math: dict[str, Any],
) -> tuple[Path, Path]:
    layout_path = external_layout_path(paper_id)
    math_path = external_math_path(paper_id)
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    layout_path.write_text(json.dumps(external_layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    math_path.write_text(json.dumps(external_math, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return layout_path, math_path
