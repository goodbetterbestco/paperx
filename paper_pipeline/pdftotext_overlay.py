from __future__ import annotations

import re
from typing import Any

from paper_pipeline.extract_layout import extract_layout
from paper_pipeline.extract_math import INLINE_MATH_RE, classify_math_block
from paper_pipeline.extract_pdftotext import bbox_to_line_window, extract_pdftotext_pages, slice_page_text
from paper_pipeline.text_utils import compact_text
from paper_pipeline.types import LayoutBlock


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WORD_RE = re.compile(r"[A-Za-z0-9]+")


def clean_text(text: str) -> str:
    return compact_text(CONTROL_CHAR_RE.sub(" ", text.replace("\u0000", " ")))


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _meaningful_tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in WORD_RE.findall(text)
        if len(token) >= 4 and not token.isdigit()
    }


def _operator_count(text: str) -> int:
    return sum(text.count(token) for token in ("=", "<", ">", "+", "-", "(", ")"))


def should_skip_repair(block: LayoutBlock) -> bool:
    if block.role in {"front_matter", "heading", "caption", "page_number"}:
        return True
    if block.role == "paragraph":
        math_kind = classify_math_block(block)
        if math_kind in {"display", "group", "algorithm"}:
            return True
        if INLINE_MATH_RE.search(block.text):
            return True
        if block.text.count("=") >= 1:
            return True
        if _operator_count(block.text) >= 6 and _word_count(block.text) <= 30:
            return True
    return False


def candidate_text_for_block(
    block: LayoutBlock,
    *,
    page_lines: list[str],
    page_height: float,
) -> str:
    start_line, end_line = bbox_to_line_window(
        block.bbox,
        page_height=page_height,
        line_count=len(page_lines),
        pad_lines=0,
    )
    return clean_text(slice_page_text(page_lines, start_line=start_line, end_line=end_line))


def is_better_candidate(block: LayoutBlock, candidate_text: str) -> bool:
    original = clean_text(block.text)
    candidate = clean_text(candidate_text)
    if not candidate or candidate == original:
        return False

    candidate_words = _word_count(candidate)
    original_words = _word_count(original)
    if candidate_words == 0:
        return False
    if block.role in {"front_matter", "paragraph", "reference", "footnote"} and candidate_words < 4:
        return False
    if candidate.strip().isdigit():
        return False
    if original_words == 0:
        return True
    if candidate_words < max(3, int(original_words * 0.5)):
        return False
    if candidate_words > max(12, int(original_words * 2.0)):
        return False
    original_tokens = _meaningful_tokens(original)
    candidate_tokens = _meaningful_tokens(candidate)
    if original_tokens and candidate_tokens:
        overlap = original_tokens & candidate_tokens
        overlap_ratio = len(overlap) / max(1, min(len(original_tokens), len(candidate_tokens)))
        if len(overlap) < 2 and overlap_ratio < 0.3:
            return False
    return True


def overlay_pdftotext_onto_layout(paper_id: str) -> tuple[dict[str, Any], dict[str, int]]:
    layout = extract_layout(paper_id)
    page_lines_by_page = extract_pdftotext_pages(paper_id)
    page_heights = {
        int(page_info["page"]): float(page_info["height"])
        for page_info in layout.get("page_sizes_pt", [])
    }

    repaired_blocks: list[LayoutBlock] = []
    changed = 0
    skipped = 0

    for block in layout["blocks"]:
        if should_skip_repair(block):
            repaired_blocks.append(block)
            skipped += 1
            continue

        page_lines = page_lines_by_page.get(block.page, [])
        page_height = page_heights.get(block.page, 0.0)
        candidate = candidate_text_for_block(block, page_lines=page_lines, page_height=page_height) if page_lines and page_height else ""
        if not is_better_candidate(block, candidate):
            repaired_blocks.append(block)
            continue

        next_meta = dict(block.meta)
        next_meta["native_text"] = clean_text(block.text)
        next_meta["text_engine"] = "native_pdf+pdftotext"
        repaired_blocks.append(
            LayoutBlock(
                id=block.id,
                page=block.page,
                order=block.order,
                text=candidate,
                role=block.role,
                bbox=block.bbox,
                engine=block.engine,
                meta=next_meta,
            )
        )
        changed += 1

    overlay = {
        "engine": "pdftotext_overlay",
        "pdf_path": layout["pdf_path"],
        "page_count": layout["page_count"],
        "page_sizes_pt": layout["page_sizes_pt"],
        "blocks": [
            {
                "id": block.id,
                "page": block.page,
                "order": block.order,
                "role": block.role,
                "text": block.text,
                "bbox": block.bbox,
                "meta": block.meta,
            }
            for block in repaired_blocks
        ],
    }
    return overlay, {"changed_blocks": changed, "skipped_blocks": skipped, "total_blocks": len(repaired_blocks)}
