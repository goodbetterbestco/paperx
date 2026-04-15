from __future__ import annotations

import re
from typing import Any

from paper_pipeline.text_utils import compact_text


FIGURE_REFERENCE_RE = re.compile(r"\b(?:fig(?:ure)?s?\.?|plate)\s*\d+[A-Za-z]?\b", re.IGNORECASE)
INLINE_NUMERIC_CITATION_RE = re.compile(r"\w\(\d{1,2}(?:[-,]\d{1,2})*\)")
BRACKET_CITATION_RE = re.compile(r"\[\s*\d{1,2}(?:\s*[-,]\s*\d{1,2})*\s*\]")
SUPERSCRIPT_CITATION_RE = re.compile(r"\^\{\(\d{1,2}(?:-\d{1,2})*\)\}")


def _paragraph_text(block: dict[str, Any]) -> str:
    spans = block.get("content", {}).get("spans", [])
    if not isinstance(spans, list):
        return ""
    parts: list[str] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        kind = str(span.get("kind", ""))
        if kind == "text":
            value = compact_text(str(span.get("text", "")))
            if value:
                parts.append(value)
        elif kind == "inline_math_ref":
            parts.append("[M]")
    return compact_text(" ".join(part for part in parts if part))


def block_text(block: dict[str, Any]) -> str:
    block_type = str(block.get("type", ""))
    if block_type in {"paragraph", "list_item"}:
        return _paragraph_text(block)
    content = block.get("content", {})
    if isinstance(content, dict):
        for key in ("text", "caption", "raw_text"):
            value = compact_text(str(content.get(key, "")))
            if value:
                return value
        lines = content.get("lines")
        if isinstance(lines, list):
            value = compact_text(" ".join(compact_text(str(line)) for line in lines if compact_text(str(line))))
            if value:
                return value
    return ""


def document_expects_figures(blocks: list[dict[str, Any]]) -> bool:
    for block in blocks:
        if str(block.get("type", "")) == "figure_ref":
            return True
        if FIGURE_REFERENCE_RE.search(block_text(block)):
            return True
    return False


def document_expects_references(document: dict[str, Any]) -> bool:
    if document.get("references"):
        return True

    citation_markers = 0
    for block in document.get("blocks", []):
        spans = block.get("content", {}).get("spans", [])
        if isinstance(spans, list) and any(
            isinstance(span, dict) and str(span.get("kind", "")) == "citation_ref" for span in spans
        ):
            return True

        text = block_text(block)
        if not text:
            continue
        citation_markers += len(INLINE_NUMERIC_CITATION_RE.findall(text))
        citation_markers += len(BRACKET_CITATION_RE.findall(text))
        citation_markers += len(SUPERSCRIPT_CITATION_RE.findall(text))
        if citation_markers >= 1:
            return True

    return False
