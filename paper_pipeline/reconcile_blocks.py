from __future__ import annotations

import re
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from paper_pipeline.corpus_layout import CORPUS_DIR
from paper_pipeline.compile_formulas import compile_formulas
from paper_pipeline.external_sources import load_external_layout, load_external_math, load_mathpix_layout
from paper_pipeline.figure_labels import caption_label
from paper_pipeline.formula_semantic_policy import annotate_formula_classifications
from paper_pipeline.formula_semantic_ir import annotate_formula_semantic_expr
from paper_pipeline.math_review_policy import (
    review_for_algorithm_block_text,
    review_for_math_entry,
    review_for_math_ref_block,
)
from paper_pipeline.normalize_prose import decode_ocr_codepoint_tokens, normalize_prose_text
from paper_pipeline.normalize_references import normalize_reference_text
from paper_pipeline.policies.abstract_quality import MISSING_ABSTRACT_PLACEHOLDER, abstract_quality_flags
from paper_pipeline.staleness_policy import build_metadata_for_paper
from paper_pipeline.text_utils import (
    SectionNode,
    build_section_tree,
    clean_heading_title,
    collapse_ocr_split_caps,
    compact_text,
    looks_like_bad_heading,
    normalize_title_key,
    paper_metadata,
    parse_heading_label,
)
from paper_pipeline.types import LayoutBlock, default_review
from paper_pipeline.document_policy import apply_document_policy
from paper_pipeline.extract_figures import extract_figures
from paper_pipeline.extract_layout import extract_layout
from paper_pipeline.extract_pdftotext import (
    bbox_to_line_window,
    extract_pdftotext_pages,
    pdftotext_available,
    slice_page_text,
)
from paper_pipeline.extract_math import (
    INLINE_MATH_RE,
    build_block_math_entry,
    classify_math_block,
    extract_general_inline_math_spans,
    looks_like_prose_paragraph,
    looks_like_prose_math_fragment,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    repair_symbolic_ocr_spans,
    split_inline_math,
)


ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = CORPUS_DIR
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
FUNDING_RE = re.compile(r"supp\s*orted\s+in\s+part|supported\s+in\s+part", re.IGNORECASE)
NAME_TOKEN_RE = re.compile(r"[A-Z][a-z]+")
AUTHOR_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'`-]*")
SHORT_WORD_RE = re.compile(r"[A-Za-z0-9]+")
MATHPIX_HINT_TOKEN_RE = re.compile(r"[A-Za-z]{1,}")
MATH_TOKEN_RE = re.compile(r"\b(?:Det|Diag|X|Y|Z|W|N|M|D|u|v|s|t|q|A)\b")
DIAGRAM_DECISION_RE = re.compile(r"^(?:start|stop|yes|no|yes yes|yes no|no yes)\b", re.IGNORECASE)
DIAGRAM_QUERY_RE = re.compile(r"^(?:is there|are there|whether)\b", re.IGNORECASE)
DIAGRAM_ACTION_RE = re.compile(r"^(?:search entity|extract\b|label\b|define\b|set\b|filter out\b)", re.IGNORECASE)
LABEL_CLOUD_TOKEN_RE = re.compile(r"^(?:\([A-Za-z]\)|[A-Za-z]{1,2}\d{1,3}|\d+[A-Za-z]{0,2}|[A-Za-z]{1,3}|\d{1,3})$")
QUOTED_IDENTIFIER_FRAGMENT_RE = re.compile(r'^"?[A-Za-z]+(?:_[A-Za-z]+){1,8}"?\s*[?;:]?$')
RUNNING_HEADER_TEXT_RE = re.compile(r"^[A-Z][A-Z\s.-]{2,}$")
PROCEDIA_RUNNING_HEADER_RE = re.compile(
    r"\b(?:Author name\s+Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000|"
    r"Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000-000\s+Procedia\s+CIRP\s+\d+\s+\(\d{4}\)\s+\d+-\d+)\b",
    re.IGNORECASE,
)
REFERENCE_START_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{0,12}\b")
REFERENCE_AUTHOR_RE = re.compile(r"^(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+(?:\s+(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+)*[.,]")
REFERENCE_YEAR_RE = re.compile(r"\b(?:18|19|20)\d{2}[a-z]?\b", re.IGNORECASE)
REFERENCE_VENUE_RE = re.compile(
    r"\b(?:press|springer|elsevier|journal|transactions|conference|proceedings|proc\.|siggraph|eurographics|ieee|acm|forum|doi|isbn|issn|pages?|vol\.|volume|technical report|workshop)\b",
    re.IGNORECASE,
)
ABOUT_AUTHOR_RE = re.compile(r"^\s*about the author\b", re.IGNORECASE)
TABLE_CAPTION_RE = re.compile(r"^\s*table\b", re.IGNORECASE)
TERMINAL_PUNCTUATION_RE = re.compile(r"[.!?:]\)?[\"']?$")
AUTHOR_MARKER_RE = re.compile(r"(?:\\\(|\\\)|\\mathbf|\\mathrm|©|\{|\}|\^)")
AUTHOR_AFFILIATION_INDEX_RE = re.compile(r"\b\d+\b")
ABSTRACT_LEAD_RE = re.compile(r"^\s*abstract\b[\s:.-]*", re.IGNORECASE)
ABSTRACT_MARKER_ONLY_RE = re.compile(r"^\s*abstract\b[\s:.-]*$", re.IGNORECASE)
TITLE_PAGE_METADATA_RE = re.compile(
    r"\b(?:received:|accepted:|published online:|open access publication|open access order|"
    r"the original version of this article was revised|the author\(s\)|accepted manuscript|"
    r"manuscript version|archive ouverte)\b",
    re.IGNORECASE,
)
AUTHOR_NOTE_RE = re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE)
PREPRINT_MARKER_RE = re.compile(r"^\s*preprint\b[\s:.-]*", re.IGNORECASE)
INTRO_MARKER_RE = re.compile(r"^(?:[0-9O](?:\.[0-9O]+)*)?\.?\s*introduction\b", re.IGNORECASE)
FRONT_MATTER_METADATA_RE = re.compile(
    r"\b(?:technical report|deliverable|available online|article history|published online|"
    r"project funded|information society technologies|revised\b|accepted\b|idealibrary|doi\b|dol:|"
    r"ecg-tr-|ist-\d{2,}|effective computational geometry|keywords?:|corresponding author|"
    r"current address|creativecommons|creative commons|licensed under|this manuscript version is made available|"
    r"numdam|cedram|archive ouverte)\b",
    re.IGNORECASE,
)
ABBREVIATED_VENUE_LINE_RE = re.compile(r"(?:\b[A-Za-z]{2,}\.\s*){3,}")
KEYWORDS_LEAD_RE = re.compile(r"^\s*keywords?:\s", re.IGNORECASE)
TRAILING_ABSTRACT_BOILERPLATE_RE = re.compile(
    r"\s+©\s*\d{4}.*?\ball rights reserved\.?$",
    re.IGNORECASE,
)
CITATION_YEAR_RE = re.compile(r"\(\s*(?:18|19|20)\d{2}[a-z]?\s*\)\.")
CITATION_AUTHOR_SPLIT_RE = re.compile(
    r"(?<=\.)\s*,\s+(?=[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'`.-]*(?:[- ][A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'`.-]*)*(?:\s+[A-Z](?:\.[A-Z])*\.?|,\s*[A-Z](?:\.[A-Z])*\.?))"
)
LEADING_OCR_MARKER_RE = re.compile(r"^(?:;\s*1|1)\s+(?=[A-Z])")
LEADING_PUNCT_ARTIFACT_RE = re.compile(r"^[;,:]\s+(?=[A-Za-z])")
LEADING_VAR_ARTIFACT_RE = re.compile(r"^[a-z]\s+(?=(?:On|The|Since|where)\b)")
TRAILING_NUMERIC_ARTIFACT_RE = re.compile(r"(?<=\.)\s+\d+(?:\s+\d+)+\s*$")
LEADING_NEGATIONSLASH_ARTIFACT_RE = re.compile(r"^(?:negationslash\s+)+", re.IGNORECASE)
SHORT_OCR_NOISE_RE = re.compile(
    r"^(?:[;:.,\-\s0-9]+|[a-z]\s+[a-z]|[a-z]{1,3}-[a-z]{1,3}|[\d\sA-Za-z]*[^\x00-\x7f][\d\sA-Za-z]*)$"
)
DISPLAY_MATH_START_RE = re.compile(r"\b(?:Solve\s*\(|[A-Za-z](?:\s+[A-Za-z0-9]){0,3}\s*=\s*)")
DISPLAY_MATH_RESUME_RE = re.compile(r"\b(?:However|Therefore|Once|Since|After|Using|Thus|On the|The second case|Eliminating)\b")
DISPLAY_MATH_PROSE_CUE_RE = re.compile(
    r"\b(?:where|however|furthermore|therefore|thus|in case|algorithms?|"
    r"they\s+(?:are|yield|give|obtain|show)|"
    r"we\s+(?:obtain|get|have|find|derive|see))\b",
    re.IGNORECASE,
)
EMBEDDED_HEADING_PREFIX_RE = re.compile(
    r"^\s*(?P<label>(?:\d+|[A-Z])(?:\s*\.\s*(?:\d+|[A-Z]))*)(?:\.)?\s+(?P<rest>.+)$"
)
TRUNCATED_PROSE_LEAD_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "those",
    "to",
    "we",
    "where",
    "with",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_text(text: str) -> str:
    return compact_text(CONTROL_CHAR_RE.sub(" ", text.replace("\u0000", " ")))


def _strip_known_running_header_text(text: str) -> str:
    return _clean_text(PROCEDIA_RUNNING_HEADER_RE.sub(" ", text))


def _block_source_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
    spans = record.get("source_spans")
    if isinstance(spans, list):
        return spans
    return []


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(record)
    cleaned["text"] = _strip_known_running_header_text(str(record.get("text", "")))
    return cleaned


def _normalize_paragraph_text(text: str) -> str:
    normalized = _strip_known_running_header_text(text)
    if not normalized:
        return normalized
    normalized = LEADING_NEGATIONSLASH_ARTIFACT_RE.sub("", normalized)
    normalized = LEADING_OCR_MARKER_RE.sub("", normalized)
    normalized = LEADING_PUNCT_ARTIFACT_RE.sub("", normalized)
    normalized = LEADING_VAR_ARTIFACT_RE.sub("", normalized)
    normalized = TRAILING_NUMERIC_ARTIFACT_RE.sub(".", normalized)
    normalized, _ = normalize_prose_text(normalized)
    return _clean_text(normalized)


def _math_entry_semantic_policy(entry: dict[str, Any]) -> str:
    classification = entry.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("semantic_policy", "graphic_only"))
    return "graphic_only"


def _math_entry_category(entry: dict[str, Any]) -> str:
    classification = entry.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("category", "unknown"))
    return "unknown"


def _group_entry_items_are_graphic_only(entry: dict[str, Any]) -> bool:
    if str(entry.get("kind", "")) != "group":
        return False
    items = entry.get("items")
    if not isinstance(items, list) or not items:
        return False
    return all(
        isinstance(item, dict) and _math_entry_semantic_policy(item) == "graphic_only"
        for item in items
    )


def _math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
    text = _normalize_paragraph_text(str(entry.get("display_latex", "")))
    if not text:
        return False
    if looks_like_prose_paragraph(text) or looks_like_prose_math_fragment(text):
        return True
    lowered = text.lower()
    if _word_count(text) >= 8 and lowered.startswith(
        ("if ", "else ", "else if ", "then ", "where ", "let ", "assume ", "suppose ")
    ):
        if text.endswith((".", ":", "=")) or "," in text:
            return True
    return _word_count(text) >= 8 and (text.endswith((".", ":")) or text.count(".") >= 1)


def _should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
    if str(entry.get("kind", "")) == "group":
        return False

    text = _normalize_paragraph_text(str(entry.get("display_latex", "")))
    if not text:
        return False

    word_count = _word_count(text)
    strong_operator_count = _strong_operator_count(text)
    mathish_ratio = _mathish_ratio(text)
    prose_like = _math_entry_looks_like_prose(entry)

    if not prose_like:
        starts_sentence = bool(text[:1]) and text[:1].isupper()
        if not (word_count >= 8 and starts_sentence and strong_operator_count <= 1 and mathish_ratio <= 0.2):
            return False

    if _math_entry_semantic_policy(entry) == "graphic_only":
        return True

    if word_count < 8:
        return False
    lowered = text.lower()
    if lowered.startswith(("if ", "else ", "else if ", "then ", "where ", "let ", "assume ", "suppose ")):
        return True
    if looks_like_prose_paragraph(text) and strong_operator_count == 0:
        return True
    if looks_like_prose_paragraph(text) and strong_operator_count <= 1 and mathish_ratio <= 0.35:
        return True
    if strong_operator_count <= 1 and mathish_ratio <= 0.2:
        return True
    return False


def _should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
    return _should_demote_prose_math_entry_to_paragraph(entry)


def _should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
    if _should_demote_graphic_math_entry_to_paragraph(entry):
        return False
    if _group_entry_items_are_graphic_only(entry):
        return True
    if _math_entry_semantic_policy(entry) != "graphic_only":
        return False
    return _math_entry_category(entry) in {"figure_embedded_math", "layout_fragment", "malformed_math"}


def _paragraph_block_from_graphic_math_entry(
    block: dict[str, Any],
    math_entry: dict[str, Any],
    counters: dict[str, int],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    text = _normalize_paragraph_text(str(math_entry.get("display_latex", "")))
    if not text:
        return None, []

    spans, inline_math_entries, next_index = split_inline_math(text, counters["inline_math"])
    spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
    spans = normalize_inline_math_spans(spans)
    counters["inline_math"] = next_index

    source_spans = list(block.get("source_spans") or math_entry.get("source_spans") or [])
    for entry in inline_math_entries:
        entry["source_spans"] = source_spans

    return (
        {
            "id": str(block.get("id", "")),
            "type": "paragraph",
            "content": {"spans": spans},
            "source_spans": source_spans,
            "alternates": list(block.get("alternates") or []),
            "review": default_review(risk="medium"),
        },
        inline_math_entries,
    )


def _suppress_graphic_display_math_blocks(
    blocks: list[dict[str, Any]],
    math_entries: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    counters: dict[str, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    math_by_id = {
        str(entry.get("id", "")): entry
        for entry in math_entries
        if isinstance(entry, dict) and str(entry.get("id", ""))
    }

    rewritten_blocks: list[dict[str, Any]] = []
    removed_block_ids: set[str] = set()
    removed_math_ids: set[str] = set()
    added_math_entries: list[dict[str, Any]] = []

    for block in blocks:
        block_type = str(block.get("type", ""))
        if block_type not in {"display_equation_ref", "equation_group_ref"}:
            rewritten_blocks.append(block)
            continue

        content = block.get("content")
        math_id = str(content.get("math_id", "")) if isinstance(content, dict) else ""
        math_entry = math_by_id.get(math_id)
        if math_entry is None:
            rewritten_blocks.append(block)
            continue

        if _should_demote_graphic_math_entry_to_paragraph(math_entry):
            paragraph_block, inline_math_entries = _paragraph_block_from_graphic_math_entry(block, math_entry, counters)
            removed_math_ids.add(math_id)
            if paragraph_block is None:
                removed_block_ids.add(str(block.get("id", "")))
                continue
            rewritten_blocks.append(paragraph_block)
            added_math_entries.extend(inline_math_entries)
            continue

        if _should_drop_display_math_artifact(math_entry):
            removed_block_ids.add(str(block.get("id", "")))
            removed_math_ids.add(math_id)
            continue

        rewritten_blocks.append(block)

    rewritten_sections: list[dict[str, Any]] = []
    for section in sections:
        updated_section = dict(section)
        updated_section["block_ids"] = [
            block_id
            for block_id in section.get("block_ids", [])
            if str(block_id) not in removed_block_ids
        ]
        rewritten_sections.append(updated_section)

    kept_math_entries = [
        entry for entry in math_entries if str(entry.get("id", "")) not in removed_math_ids
    ]
    kept_math_entries.extend(added_math_entries)
    return rewritten_blocks, kept_math_entries, rewritten_sections


def _normalize_formula_display_text(text: str) -> str:
    normalized = _clean_text(text)
    normalized, _ = decode_ocr_codepoint_tokens(normalized)
    return _clean_text(normalized)


def _normalize_figure_caption_text(text: str) -> str:
    normalized = _clean_text(text)
    normalized = re.sub(r"^\s*Fig\.\s*\d+\s*", "", normalized, flags=re.IGNORECASE)
    normalized, _ = normalize_prose_text(normalized)
    normalized = normalized.lstrip(" .:;-—")
    return _clean_text(normalized)


def _mathish_ratio(text: str) -> float:
    if not text:
        return 0.0
    word_count = max(_word_count(text), 1)
    symbol_count = _math_signal_count(text)
    return symbol_count / word_count


def _record_analysis_text(record: dict[str, Any]) -> str:
    meta = record.get("meta", {})
    if isinstance(meta, dict):
        native_text = _clean_text(str(meta.get("native_text", "")))
        if native_text:
            return native_text
    return _clean_text(str(record.get("text", "")))


def _word_count(text: str) -> int:
    return len(SHORT_WORD_RE.findall(text))


def _page_height_map(layout: dict[str, Any]) -> dict[int, float]:
    return {
        int(page_info["page"]): float(page_info["height"])
        for page_info in layout.get("page_sizes_pt", [])
    }


def _is_pdftotext_candidate_better(original_text: str, candidate_text: str, record_type: str) -> bool:
    original = _clean_text(original_text)
    candidate = _clean_text(candidate_text)
    if not candidate or candidate == original:
        return False
    if record_type in {"heading", "caption", "page_number"}:
        return False

    candidate_words = _word_count(candidate)
    original_words = _word_count(original)
    if candidate_words == 0:
        return False
    if record_type in {"front_matter", "paragraph", "reference", "footnote"} and candidate_words < 4:
        return False
    if "Figure " in candidate and record_type == "paragraph":
        return False
    if candidate.strip().isdigit():
        return False

    if original_words == 0:
        return True
    if candidate_words < max(3, int(original_words * 0.5)):
        return False
    if candidate_words > max(12, int(original_words * 2.25)):
        return False
    return True


def _should_skip_pdftotext_repair(record: dict[str, Any]) -> bool:
    if record.get("type") != "paragraph":
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and (meta.get("forced_math_kind") or meta.get("forced_algorithm")):
        return True
    text = _clean_text(str(record.get("text", "")))
    operator_count = sum(text.count(token) for token in ("=", "<", ">", "+", "-", "(", ")"))
    if text.count("=") >= 1:
        return True
    if operator_count >= 6 and _word_count(text) <= 30:
        return True
    if INLINE_MATH_RE.search(text):
        return True
    return False


def _repair_record_text_with_pdftotext(
    records: list[dict[str, Any]],
    pdftotext_pages: dict[int, list[str]],
    page_heights: dict[int, float],
) -> list[dict[str, Any]]:
    repaired: list[dict[str, Any]] = []
    for record in records:
        record_type = str(record.get("type", ""))
        if record_type not in {"front_matter", "paragraph", "reference", "footnote"}:
            repaired.append(record)
            continue
        if _should_skip_pdftotext_repair(record):
            repaired.append(record)
            continue

        spans = _block_source_spans(record)
        if not spans:
            repaired.append(record)
            continue

        slices: list[str] = []
        for span in spans:
            page = int(span.get("page", 0) or 0)
            page_lines = pdftotext_pages.get(page)
            page_height = page_heights.get(page)
            bbox = span.get("bbox", {})
            if not page_lines or not page_height or not bbox:
                continue
            start_line, end_line = bbox_to_line_window(bbox, page_height=page_height, line_count=len(page_lines))
            text = slice_page_text(page_lines, start_line=start_line, end_line=end_line)
            if text:
                slices.append(text)

        candidate_text = _clean_text(" ".join(slices))
        original_text = str(record.get("text", ""))
        if not _is_pdftotext_candidate_better(original_text, candidate_text, record_type):
            repaired.append(record)
            continue

        updated = dict(record)
        updated["text"] = candidate_text
        meta = dict(updated.get("meta", {}))
        meta["native_text"] = _clean_text(original_text)
        meta["text_engine"] = "native_pdf+pdftotext"
        updated["meta"] = meta
        repaired.append(updated)
    return repaired


def _mathpix_text_blocks_by_page(layout: dict[str, Any]) -> dict[int, list[LayoutBlock]]:
    grouped: dict[int, list[LayoutBlock]] = {}
    for block in layout.get("blocks", []):
        if str(block.role) != "paragraph":
            continue
        if str(block.meta.get("mathpix_type", "")) != "text":
            continue
        grouped.setdefault(int(block.page), []).append(block)
    for blocks in grouped.values():
        blocks.sort(key=lambda block: (float(block.bbox.get("y0", 0.0)), int(block.order), str(block.id)))
    return grouped


def _record_union_bbox(record: dict[str, Any]) -> tuple[int, dict[str, float]] | None:
    spans = _block_source_spans(record)
    if not spans:
        return None
    page = int(spans[0].get("page", record.get("page", 0)) or 0)
    page_spans = [span for span in spans if int(span.get("page", page) or page) == page]
    if not page_spans:
        return None
    x0 = min(float(span.get("bbox", {}).get("x0", 0.0)) for span in page_spans)
    y0 = min(float(span.get("bbox", {}).get("y0", 0.0)) for span in page_spans)
    x1 = max(float(span.get("bbox", {}).get("x1", 0.0)) for span in page_spans)
    y1 = max(float(span.get("bbox", {}).get("y1", 0.0)) for span in page_spans)
    return page, {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "width": max(x1 - x0, 0.0), "height": max(y1 - y0, 0.0)}


def _inline_tex_signal_count(text: str) -> int:
    return (
        text.count(r"\(")
        + text.count(r"\)")
        + text.count(r"\mathbf")
        + text.count(r"\bar")
        + text.count(r"\frac")
        + text.count("_{")
        + text.count("^{")
    )


def _mathpix_hint_alignment_text(text: str) -> str:
    aligned = _clean_text(text)
    prose_cue_match = DISPLAY_MATH_PROSE_CUE_RE.search(aligned)
    if prose_cue_match:
        prefix = aligned[: prose_cue_match.start()]
        if prefix.lstrip().startswith((";", ":")) or (
            _math_signal_count(prefix) >= 4 and _word_count(prefix) <= 24
        ):
            aligned = aligned[prose_cue_match.start() :]

    display_math_match = DISPLAY_MATH_START_RE.search(aligned)
    if display_math_match:
        prefix = aligned[: display_math_match.start()].rstrip()
        suffix = aligned[display_math_match.start() :]
        if _word_count(prefix) >= 6 and _math_signal_count(suffix) >= 4:
            aligned = prefix
    return _clean_text(aligned)


def _mathpix_hint_tokens(text: str) -> list[str]:
    normalized = (
        text.replace(r"\(", " ")
        .replace(r"\)", " ")
        .replace("\\", " ")
        .replace("{", " ")
        .replace("}", " ")
    )
    return [token.lower() for token in MATHPIX_HINT_TOKEN_RE.findall(normalized)]


def _mathpix_text_candidate_score(original_text: str, candidate_text: str) -> tuple[int, int, int, int]:
    aligned_original = _mathpix_hint_alignment_text(original_text)
    original_tokens = _mathpix_hint_tokens(aligned_original)
    candidate_tokens = _mathpix_hint_tokens(candidate_text)
    if not original_tokens or not candidate_tokens:
        return (-10_000, -10_000, -10_000, -10_000)

    prefix_score = 0
    if candidate_tokens[0] == original_tokens[0]:
        prefix_score += 4
    elif candidate_tokens[0] in original_tokens[:4]:
        prefix_score += 1
    else:
        prefix_score -= 2
    if len(candidate_tokens) > 1 and len(original_tokens) > 1 and candidate_tokens[1] == original_tokens[1]:
        prefix_score += 1

    suffix_score = 0
    if candidate_tokens[-1] == original_tokens[-1]:
        suffix_score += 2
    elif candidate_tokens[-1] in original_tokens[-4:]:
        suffix_score += 1
    else:
        suffix_score -= 1

    shared_token_count = len(set(original_tokens) & set(candidate_tokens))
    length_delta = abs(len(candidate_tokens) - len(original_tokens))
    return (
        prefix_score + suffix_score,
        shared_token_count,
        -length_delta,
        _inline_tex_signal_count(candidate_text),
    )


def _matching_mathpix_text_blocks(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
) -> list[LayoutBlock]:
    record_bounds = _record_union_bbox(record)
    if record_bounds is None:
        return []
    page, record_bbox = record_bounds

    matching_blocks: list[LayoutBlock] = []
    for block in mathpix_blocks_by_page.get(page, []):
        block_bbox = dict(block.bbox)
        x_overlap_ratio = _rect_x_overlap_ratio(record_bbox, block_bbox)
        block_x0 = float(block_bbox.get("x0", 0.0))
        block_x1 = float(block_bbox.get("x1", 0.0))
        block_width = float(block_bbox.get("width", max(block_x1 - block_x0, 0.0)))
        left_continuation = (
            x_overlap_ratio <= 0.0
            and block_x1 <= float(record_bbox.get("x0", 0.0))
            and float(record_bbox.get("x0", 0.0)) - block_x1 <= 8.0
            and block_width <= 24.0
        )
        if x_overlap_ratio < 0.7 and not left_continuation:
            continue
        block_y0 = float(block_bbox.get("y0", 0.0))
        block_y1 = float(block_bbox.get("y1", 0.0))
        record_y0 = float(record_bbox.get("y0", 0.0))
        record_y1 = float(record_bbox.get("y1", 0.0))
        if block_y1 < record_y0 - 6.0 or block_y0 > record_y1 + 6.0:
            continue
        matching_blocks.append(block)
    return matching_blocks


def _mathpix_text_hint_candidate(record: dict[str, Any], mathpix_blocks_by_page: dict[int, list[LayoutBlock]]) -> str:
    matching_blocks = _matching_mathpix_text_blocks(record, mathpix_blocks_by_page)

    if not matching_blocks:
        return ""

    original_text = str(record.get("text", ""))
    original_words = max(_word_count(_mathpix_hint_alignment_text(original_text)), 1)
    best_text = ""
    best_score: tuple[int, int, int, int] | None = None

    for start in range(len(matching_blocks)):
        candidate_parts: list[str] = []
        for end in range(start, len(matching_blocks)):
            part = matching_blocks[end].text.strip()
            if not part:
                continue
            candidate_parts.append(part)
            candidate_text = _clean_text(" ".join(candidate_parts))
            candidate_words = _word_count(candidate_text)
            if candidate_words > max(48, int(original_words * 2.0)):
                break
            score = _mathpix_text_candidate_score(original_text, candidate_text)
            if best_score is None or score > best_score:
                best_score = score
                best_text = candidate_text
    return best_text


def _looks_like_truncated_prose_lead(text: str) -> bool:
    cleaned = _clean_text(text)
    if not cleaned or not cleaned[:1].islower():
        return False
    words = SHORT_WORD_RE.findall(cleaned)
    if len(words) < 12:
        return False
    first_word = words[0].lower()
    if first_word in TRUNCATED_PROSE_LEAD_STOPWORDS:
        return False
    return 3 <= len(first_word) <= 10 and first_word.isalpha()


def _token_subsequence_index(tokens: list[str], needle: list[str]) -> int | None:
    if not tokens or not needle or len(tokens) < len(needle):
        return None
    limit = len(tokens) - len(needle) + 1
    for index in range(limit):
        if tokens[index : index + len(needle)] == needle:
            return index
    return None


def _mathpix_prose_lead_repair_candidate(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
) -> str:
    original_text = _clean_text(str(record.get("text", "")))
    if not _looks_like_truncated_prose_lead(original_text):
        return ""

    matching_blocks = _matching_mathpix_text_blocks(record, mathpix_blocks_by_page)
    if not matching_blocks:
        return ""

    original_tokens = [token.lower() for token in SHORT_WORD_RE.findall(original_text)]
    if len(original_tokens) < 12:
        return ""
    overlap_tokens = original_tokens[1 : 1 + min(8, max(len(original_tokens) - 1, 0))]
    if len(overlap_tokens) < 6:
        return ""

    best_text = ""
    best_score: tuple[int, int, int] | None = None
    original_word_count = len(original_tokens)
    for start in range(len(matching_blocks)):
        candidate_parts: list[str] = []
        for end in range(start, len(matching_blocks)):
            part = matching_blocks[end].text.strip()
            if not part:
                continue
            candidate_parts.append(part)
            candidate_text = _clean_text(" ".join(candidate_parts))
            candidate_word_count = _word_count(candidate_text)
            if candidate_word_count > max(64, int(original_word_count * 2.4)):
                break
            if not candidate_text or not candidate_text[:1].isupper():
                continue
            if parse_heading_label(candidate_text) is not None:
                continue
            candidate_tokens = [token.lower() for token in SHORT_WORD_RE.findall(candidate_text)]
            if len(candidate_tokens) <= original_word_count + 4:
                continue
            if candidate_word_count - original_word_count > 36:
                continue
            overlap_index = _token_subsequence_index(candidate_tokens, overlap_tokens)
            if overlap_index is None or overlap_index <= 0 or overlap_index > 36:
                continue
            score = (overlap_index, -start, -abs(candidate_word_count - original_word_count - overlap_index))
            if best_score is None or score > best_score:
                best_score = score
                best_text = candidate_text
    return best_text


def _is_mathpix_text_hint_better(original_text: str, candidate_text: str) -> bool:
    original = _clean_text(original_text)
    candidate = _clean_text(candidate_text)
    if not candidate or candidate == original:
        return False

    original_words = _word_count(original)
    candidate_words = _word_count(candidate)
    if candidate_words < max(4, int(original_words * 0.4)):
        return False
    if candidate_words > max(40, int(original_words * 1.75)):
        return False

    candidate_signal_count = _inline_tex_signal_count(candidate)
    original_signal_count = _inline_tex_signal_count(original)
    if candidate_signal_count < max(2, original_signal_count + 2):
        return False

    degraded_original = (
        ";;" in original
        or " : : :" in original
        or bool(re.search(r"\b[A-Za-z]\s+\d\b", original))
        or bool(re.search(r"\b[A-Za-z]\s*;\s*\d\b", original))
        or bool(re.search(r"\b[A-Za-z]\s+\(", original))
    )
    if not degraded_original and candidate_signal_count < original_signal_count + 3:
        return False
    return True


def _repair_record_text_with_mathpix_hints(
    records: list[dict[str, Any]],
    mathpix_layout: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not mathpix_layout:
        return records

    mathpix_blocks_by_page = _mathpix_text_blocks_by_page(mathpix_layout)
    if not mathpix_blocks_by_page:
        return records

    repaired: list[dict[str, Any]] = []
    for record in records:
        if record.get("type") != "paragraph":
            repaired.append(record)
            continue
        if _is_short_ocr_fragment(record):
            repaired.append(record)
            continue
        original_text = str(record.get("text", ""))
        candidate_text = _mathpix_text_hint_candidate(record, mathpix_blocks_by_page)
        text_engine = ""
        if _is_mathpix_text_hint_better(original_text, candidate_text):
            text_engine = "mathpix_text_hint"
        else:
            candidate_text = _mathpix_prose_lead_repair_candidate(record, mathpix_blocks_by_page)
            if candidate_text:
                text_engine = "mathpix_prose_hint"
        if not text_engine:
            repaired.append(record)
            continue

        updated = dict(record)
        updated["text"] = candidate_text
        meta = dict(updated.get("meta", {}))
        meta["original_text"] = _clean_text(original_text)
        meta["text_engine"] = text_engine
        updated["meta"] = meta
        repaired.append(updated)
    return repaired


def _page_one_front_matter_records(
    records: list[dict[str, Any]],
    mathpix_layout: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    page_one_records = [record for record in records if int(record.get("page", 0) or 0) == 1]
    if not mathpix_layout:
        return page_one_records

    seen: set[str] = set()
    combined: list[dict[str, Any]] = []
    for record in page_one_records:
        key = normalize_title_key(_clean_text(str(record.get("text", ""))))
        if key:
            seen.add(key)
        combined.append(record)

    for block in _mathpix_text_blocks_by_page(mathpix_layout).get(1, []):
        record = _layout_record(block)
        key = normalize_title_key(_clean_text(str(record.get("text", ""))))
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        combined.append(record)

    combined.sort(
        key=lambda record: (
            int(record.get("page", 0) or 0),
            int(record.get("group_index", 0) or 0),
            int(record.get("split_index", 0) or 0),
        )
    )
    return combined


def _layout_record(block: LayoutBlock) -> dict[str, Any]:
    record_type = str(block.role)
    if record_type == "paragraph":
        docling_label = str(block.meta.get("docling_label", "") or "")
        mathpix_type = str(block.meta.get("mathpix_type", "") or "")
        mathpix_subtype = str(block.meta.get("mathpix_subtype", "") or "")
        if docling_label == "list_item":
            record_type = "list_item"
        elif docling_label == "code":
            record_type = "code"
        elif mathpix_type in {"code", "pseudocode"} or mathpix_subtype in {"algorithm", "pseudocode"}:
            record_type = "code"
    record = block.as_record()
    record["type"] = record_type
    record["group_index"] = block.order * 10
    record["text"] = _clean_text(block.text)
    record.setdefault("meta", {})
    record["meta"] = {**record["meta"], "raw_text": block.text}
    return record


def _figure_label_token(figure: dict[str, Any]) -> str | None:
    return caption_label(str(figure.get("label", "")))


def _synthetic_caption_record(figure: dict[str, Any], page_blocks: list[LayoutBlock]) -> dict[str, Any]:
    caption_bbox = figure.get("provenance", {}).get("caption_bbox") or figure.get("bbox", {})
    caption_y = float(caption_bbox.get("y0", 0.0))
    preceding = sum(1 for block in page_blocks if float(block.bbox.get("y0", 0.0)) <= caption_y)
    return {
        "id": f"synthetic-caption-{figure['id']}",
        "page": int(figure["page"]),
        "group_index": preceding * 10 + 5,
        "split_index": 1,
        "type": "caption",
        "text": f"{figure['label']}: {figure['caption']}",
        "source_spans": [
            {
                "page": int(figure["page"]),
                "bbox": caption_bbox,
                "engine": "local_figure_linker",
            }
        ],
        "meta": {
            "figure_id": figure["id"],
            "synthetic": True,
        },
    }


def _record_bbox(record: dict[str, Any]) -> dict[str, Any]:
    return (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})


def _rect_x_overlap_ratio(a: dict[str, Any], b: dict[str, Any]) -> float:
    x0 = max(float(a.get("x0", 0.0)), float(b.get("x0", 0.0)))
    x1 = min(float(a.get("x1", 0.0)), float(b.get("x1", 0.0)))
    if x1 <= x0:
        return 0.0
    width_a = max(float(a.get("width", 0.0)), float(a.get("x1", 0.0)) - float(a.get("x0", 0.0)), 1.0)
    width_b = max(float(b.get("width", 0.0)), float(b.get("x1", 0.0)) - float(b.get("x0", 0.0)), 1.0)
    return (x1 - x0) / min(width_a, width_b)


def _strip_caption_label_prefix(text: str, figure: dict[str, Any] | None = None) -> str:
    cleaned = _clean_text(text)
    if ":" in cleaned:
        leading, remainder = cleaned.split(":", 1)
        if caption_label(leading) or re.match(r"^\s*fig(?:ure)?\.?\s*\d+\b", leading, re.IGNORECASE):
            return _clean_text(remainder)
    prefixes: list[str] = []
    if figure is not None:
        prefixes.append(_clean_text(str(figure.get("label", ""))))
    label = caption_label(cleaned)
    if label:
        prefixes.append(label)
    for prefix in prefixes:
        if prefix and cleaned.lower().startswith(prefix.lower()):
            stripped = cleaned[len(prefix) :].lstrip(" :.-")
            return _clean_text(stripped)
    return cleaned


def _append_figure_caption_fragment(figure: dict[str, Any], fragment: str) -> None:
    normalized_fragment = _normalize_figure_caption_text(_strip_caption_label_prefix(fragment, figure))
    if not normalized_fragment:
        return
    current = _clean_text(str(figure.get("caption", "")))
    if current:
        current_words = current.split()
        fragment_words = normalized_fragment.split()
        max_overlap = min(len(current_words), len(fragment_words))
        for overlap in range(max_overlap, 5, -1):
            prefix = _clean_text(" ".join(fragment_words[:overlap]))
            if prefix and normalize_title_key(prefix) in normalize_title_key(current):
                normalized_fragment = _clean_text(" ".join(fragment_words[overlap:]))
                break
        if not normalized_fragment:
            return
    current_key = normalize_title_key(current)
    fragment_key = normalize_title_key(normalized_fragment)
    if fragment_key and current_key and fragment_key in current_key:
        return
    figure["caption"] = _clean_text(f"{current} {normalized_fragment}" if current else normalized_fragment)


def _match_figure_for_caption_record(record: dict[str, Any], figures_on_page: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not figures_on_page:
        return None
    label = caption_label(str(record.get("text", "")))
    if label:
        for figure in figures_on_page:
            if _figure_label_token(figure) == label:
                return figure

    bbox = _record_bbox(record)
    if not bbox:
        return None
    record_y0 = float(bbox.get("y0", 0.0))
    best_figure: dict[str, Any] | None = None
    best_score = float("-inf")
    for figure in figures_on_page:
        figure_bbox = figure.get("bbox", {})
        if not figure_bbox:
            continue
        x_overlap = _rect_x_overlap_ratio(bbox, figure_bbox)
        if x_overlap <= 0.0:
            continue
        figure_y1 = float(figure_bbox.get("y1", 0.0))
        vertical_gap = max(record_y0 - figure_y1, 0.0)
        if vertical_gap > 120.0:
            continue
        score = x_overlap - (vertical_gap / 120.0)
        if score > best_score:
            best_score = score
            best_figure = figure
    return best_figure


def _absorb_figure_caption_continuations(
    records: list[dict[str, Any]],
    figures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    figures_by_page: dict[int, list[dict[str, Any]]] = {}
    for figure in figures:
        figures_by_page.setdefault(int(figure.get("page", 0) or 0), []).append(figure)

    adjusted: list[dict[str, Any]] = []

    for record in records:
        record_type = str(record.get("type", ""))
        page = int(record.get("page", 0) or 0)

        if record_type == "caption":
            figure = _match_figure_for_caption_record(record, figures_by_page.get(page, []))
            if figure is not None:
                _append_figure_caption_fragment(figure, str(record.get("text", "")))
                if not caption_label(str(record.get("text", ""))):
                    continue
            adjusted.append(record)
            continue

        adjusted.append(record)

    return adjusted


def _merge_layout_and_figure_records(
    layout_blocks: list[LayoutBlock], figures: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, LayoutBlock]]:
    records = [_layout_record(block) for block in layout_blocks]
    layout_by_id = {block.id: block for block in layout_blocks}
    page_blocks: dict[int, list[LayoutBlock]] = {}
    for block in layout_blocks:
        page_blocks.setdefault(block.page, []).append(block)

    records = _absorb_figure_caption_continuations(records, figures)

    existing_labels = {
        (record["page"], caption_label(str(record.get("text", ""))))
        for record in records
        if record.get("type") == "caption"
    }
    for figure in figures:
        label = _figure_label_token(figure)
        key = (int(figure["page"]), label)
        if label and key in existing_labels:
            continue
        records.append(_synthetic_caption_record(figure, page_blocks.get(int(figure["page"]), [])))

    return records, layout_by_id


def _inject_external_math_records(
    records: list[dict[str, Any]],
    layout_blocks: list[LayoutBlock],
    external_math_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[str]]:
    page_orders: dict[int, list[tuple[int, float]]] = {}
    page_blocks: dict[int, list[LayoutBlock]] = {}
    for block in layout_blocks:
        page_orders.setdefault(int(block.page), []).append((int(block.order), float(block.bbox.get("y0", 0.0))))
        page_blocks.setdefault(int(block.page), []).append(block)
    for values in page_orders.values():
        values.sort(key=lambda item: (item[1], item[0]))

    per_anchor_counts: dict[tuple[int, int], int] = {}
    injected_ids: set[str] = set()
    injected_records: list[dict[str, Any]] = []

    for entry in external_math_entries:
        if str(entry.get("kind", "")) not in {"display", "group"}:
            continue
        spans = list(entry.get("source_spans") or [])
        if not spans:
            continue
        span = spans[0]
        page = int(span.get("page", 0) or 0)
        bbox = dict(span.get("bbox", {}))
        if page <= 0 or not bbox:
            continue
        y0 = float(bbox.get("y0", 0.0))
        prior_orders = [order for order, block_y0 in page_orders.get(page, []) if block_y0 <= y0]
        anchor_order = prior_orders[-1] if prior_orders else 0
        anchor_before_order: int | None = None
        entry_area = _rect_area(bbox)
        for block in page_blocks.get(page, []):
            if block.role not in {"paragraph", "code"}:
                continue
            block_bbox = dict(block.bbox)
            overlap = _rect_intersection_area(bbox, block_bbox)
            if overlap <= 0.0:
                continue
            overlap_score = overlap / min(entry_area, _rect_area(block_bbox))
            if overlap_score < 0.2:
                continue
            top_gap = y0 - float(block_bbox.get("y0", 0.0))
            if top_gap < -8.0 or top_gap > 24.0:
                continue
            if not _looks_like_leading_display_math_echo(block.text):
                continue
            candidate_order = int(block.order)
            if anchor_before_order is None or candidate_order < anchor_before_order:
                anchor_before_order = candidate_order
        if anchor_before_order is not None:
            prior_anchor_orders = [order for order, _ in page_orders.get(page, []) if order < anchor_before_order]
            anchor_order = prior_anchor_orders[-1] if prior_anchor_orders else 0
        anchor_key = (page, anchor_order)
        per_anchor_counts[anchor_key] = per_anchor_counts.get(anchor_key, 0) + 1
        split_index = per_anchor_counts[anchor_key]
        injected_records.append(
            {
                "id": f"external-math-record-{entry['id']}",
                "page": page,
                "group_index": anchor_order * 10 + 5,
                "split_index": split_index,
                "type": "paragraph",
                "text": _clean_text(str(entry.get("display_latex", ""))),
                "source_spans": spans,
                "meta": (
                    {"source_math_entry_id": str(entry.get("id", ""))}
                    if looks_like_prose_math_fragment(_clean_text(str(entry.get("display_latex", ""))))
                    else {
                        "external_math_entry": dict(entry),
                        "forced_math_kind": "group" if str(entry.get("kind", "")) == "group" else "display",
                    }
                ),
            }
        )
        injected_ids.add(str(entry["id"]))

    if not injected_records:
        return records, injected_ids

    combined = list(records)
    combined.extend(injected_records)
    combined.sort(key=lambda record: (int(record.get("page", 0)), int(record.get("group_index", 0)), int(record.get("split_index", 0))))
    return combined, injected_ids


def _decode_control_heading_label(text: str) -> tuple[str | None, str]:
    raw = str(text)
    prefix: list[int] = []
    index = 0
    while index < len(raw):
        char = raw[index]
        code = ord(char)
        if char.isspace():
            index += 1
            continue
        if 1 <= code <= 9:
            prefix.append(code)
            index += 1
            continue
        break

    title = _clean_text(raw[index:])
    if not prefix or not title:
        return None, title

    if len(prefix) >= 3 and prefix[1] == 2:
        suffix = "".join(str(code) for code in prefix[2:])
        if suffix:
            return f"{prefix[0]}.{suffix}", title

    label_parts: list[str] = []
    current = str(prefix[0])
    for code in prefix[1:]:
        if code == 2:
            if current:
                label_parts.append(current)
                current = ""
            continue
        current += str(code)
    if current:
        label_parts.append(current)
    if not label_parts:
        return None, title
    return ".".join(label_parts), title


def _normalize_decoded_heading_title(title: str) -> str:
    tokens = title.split()
    normalized: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token and token[0].isupper() and token.isalpha() and len(token) <= 4:
            combined = token
            next_index = index + 1
            while next_index < len(tokens):
                next_token = tokens[next_index]
                if not next_token.isalpha() or (next_token and next_token[0].isupper()) or len(combined) >= 8:
                    break
                combined += next_token
                next_index += 1
            normalized.append(combined)
            index = next_index
            continue
        normalized.append(token)
        index += 1
    return compact_text(" ".join(normalized))


def _split_embedded_heading_paragraph(record: dict[str, Any]) -> tuple[str, str] | None:
    if record.get("type") != "paragraph":
        return None

    source_bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    x0 = float(source_bbox.get("x0", 999.0))
    if x0 > 120.0:
        return None

    raw_text = _clean_text(str(record.get("meta", {}).get("raw_text", record.get("text", ""))))
    if not raw_text:
        return None

    match = EMBEDDED_HEADING_PREFIX_RE.match(raw_text)
    if match is None:
        return None

    label = re.sub(r"\s*\.\s*", ".", match.group("label")).rstrip(".")
    rest = _clean_text(match.group("rest"))
    tokens = rest.split()
    if len(tokens) < 4:
        return None

    title_connector_tokens = {
        "a",
        "an",
        "and",
        "as",
        "at",
        "based",
        "between",
        "by",
        "for",
        "from",
        "in",
        "into",
        "of",
        "on",
        "or",
        "the",
        "to",
        "under",
        "using",
        "via",
        "with",
    }
    sentence_start_tokens = {
        "A",
        "An",
        "After",
        "Assuming",
        "Before",
        "But",
        "Else",
        "For",
        "However",
        "If",
        "In",
        "Moreover",
        "Once",
        "Our",
        "Since",
        "The",
        "Then",
        "There",
        "These",
        "They",
        "This",
        "Thus",
        "To",
        "We",
        "When",
        "While",
    }

    title_tokens: list[str] = []
    for index, token in enumerate(tokens):
        bare = token.strip(" ,;:()[]{}")
        if not bare:
            break

        next_bare = tokens[index + 1].strip(" ,;:()[]{}") if index + 1 < len(tokens) else ""
        if index == 0 and bare in sentence_start_tokens and next_bare[:1].islower():
            return None
        if index > 0 and bare in sentence_start_tokens and next_bare[:1].islower():
            break

        bare_lower = bare.lower()
        if index > 0 and bare_lower not in title_connector_tokens and not bare[:1].isupper() and not bare.isupper():
            break

        title_tokens.append(token)
        if len(title_tokens) >= 10:
            break

    if not title_tokens:
        return None

    title = _normalize_decoded_heading_title(collapse_ocr_split_caps(" ".join(title_tokens).strip(" ,;:")))
    if not title or looks_like_bad_heading(title):
        return None

    remainder_tokens = tokens[len(title_tokens) :]
    remainder = _clean_text(" ".join(remainder_tokens))
    if len(SHORT_WORD_RE.findall(remainder)) < 4:
        return None
    if not remainder_tokens or not remainder_tokens[0][:1].isupper():
        return None

    return f"{label} {title}", remainder


def _promote_heading_like_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for record in records:
        if record.get("type") == "paragraph":
            raw_text = str(record.get("meta", {}).get("raw_text", record.get("text", "")))
            label, title = _decode_control_heading_label(raw_text)
            if not label:
                parsed_heading = parse_heading_label(clean_heading_title(raw_text))
                if parsed_heading is not None:
                    parsed_label, parsed_title = parsed_heading
                    if not looks_like_bad_heading(parsed_title):
                        label = ".".join(parsed_label)
                        title = parsed_title
            word_count = len(SHORT_WORD_RE.findall(title))
            source_bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
            x0 = float(source_bbox.get("x0", 999.0))
            token_lengths = [len(token) for token in SHORT_WORD_RE.findall(title)]
            max_token_length = max(token_lengths) if token_lengths else 0
            if label and title and 1 <= word_count <= 8 and x0 <= 80 and max_token_length >= 4:
                normalized_title = _normalize_decoded_heading_title(collapse_ocr_split_caps(title))
                candidate = dict(record)
                candidate["type"] = "heading"
                candidate["text"] = f"{label} {normalized_title}"
                candidate.setdefault("meta", {})
                candidate["meta"] = {
                    **candidate["meta"],
                    "synthetic_heading": True,
                    "decoded_label": label,
                    "decoded_title": normalized_title,
                }
                promoted.append(candidate)
                continue
            split_heading = _split_embedded_heading_paragraph(record)
            if split_heading is not None:
                heading_text, remainder_text = split_heading
                heading_record = dict(record)
                heading_record["type"] = "heading"
                heading_record["text"] = heading_text
                heading_record.setdefault("meta", {})
                heading_record["meta"] = {
                    **heading_record["meta"],
                    "raw_text": heading_text,
                    "synthetic_heading": True,
                    "synthetic_heading_split": True,
                }
                promoted.append(heading_record)

                paragraph_record = dict(record)
                paragraph_record["text"] = remainder_text
                paragraph_record.setdefault("meta", {})
                paragraph_record["meta"] = {
                    **paragraph_record["meta"],
                    "raw_text": remainder_text,
                    "original_text": _clean_text(str(record.get("text", ""))),
                }
                promoted.append(paragraph_record)
                continue
        promoted.append(record)
    return promoted


def _looks_like_math_fragment(record: dict[str, Any]) -> bool:
    if record.get("type") != "paragraph":
        return False
    text = _record_analysis_text(record)
    if not text:
        return False
    if looks_like_prose_paragraph(text):
        return False
    words = SHORT_WORD_RE.findall(text)
    if len(words) <= 3 and len(text) <= 24:
        return True
    if MATH_TOKEN_RE.search(text) and len(words) <= 8:
        return True
    if any(token in text for token in ("(", ")", "=", "<", ">", "+", "−", "-", "", "", "")) and len(words) <= 10:
        return True
    return False


def _math_signal_count(text: str) -> int:
    return len(MATH_TOKEN_RE.findall(text)) + sum(text.count(token) for token in ("(", ")", "=", "<", ">", "+", "−", "-"))


def _strong_operator_count(text: str) -> int:
    return sum(text.count(token) for token in ("=", "<", ">", "+", "/", "^", "_", "{", "}")) + len(
        re.findall(r"(?<![A-Za-z0-9])[-−](?![A-Za-z0-9])", text)
    )


def _looks_like_vertical_label_cloud(text: str, spans: list[dict[str, Any]]) -> bool:
    raw_tokens = text.split()
    if len(raw_tokens) < 8 or len(spans) < 3:
        return False
    strong_operator_count = _strong_operator_count(text)
    if strong_operator_count > 1 or text.count(".") >= 1 or text.count(":") >= 1:
        return False
    tall_narrow_span_count = sum(
        1
        for span in spans
        if (
            float(span.get("bbox", {}).get("height", 0.0)) >= 24.0
            and float(span.get("bbox", {}).get("width", 0.0)) <= 20.0
        )
        or (
            float(span.get("bbox", {}).get("height", 0.0))
            >= float(span.get("bbox", {}).get("width", 0.0)) * 2.5
            and float(span.get("bbox", {}).get("height", 0.0)) >= 24.0
        )
    )
    return tall_narrow_span_count >= max(3, len(spans) // 8)


def _looks_like_table_marker_cloud(text: str, spans: list[dict[str, Any]]) -> bool:
    raw_tokens = text.split()
    if len(raw_tokens) < 8 or len(spans) < 6:
        return False
    strong_operator_count = _strong_operator_count(text)
    if strong_operator_count > 1 or text.count(".") >= 1 or text.count(":") >= 1:
        return False
    marker_token_count = sum(
        1
        for token in raw_tokens
        if token in {"Y", "N", "X"} or re.fullmatch(r"\(\d+\)", token)
    )
    tiny_span_count = sum(
        1
        for span in spans
        if float(span.get("bbox", {}).get("height", 0.0)) <= 12.0 and float(span.get("bbox", {}).get("width", 0.0)) <= 16.0
    )
    return marker_token_count >= max(4, len(raw_tokens) // 3) and tiny_span_count >= max(4, len(spans) // 3)


def _looks_like_browser_ui_scrap(text: str) -> bool:
    lowered = text.lower()
    if "localhost" not in lowered and "http://" not in lowered and "https://" not in lowered and "www." not in lowered:
        return False
    word_count = len(SHORT_WORD_RE.findall(text))
    if word_count > 24:
        return False
    symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
    return symbol_count >= 3 or any(token in text for token in ("?", "&", "="))


def _looks_like_quoted_identifier_fragment(text: str) -> bool:
    words = SHORT_WORD_RE.findall(text)
    if len(words) > 6:
        return False
    return bool(QUOTED_IDENTIFIER_FRAGMENT_RE.fullmatch(text))


def _looks_like_glyph_noise_cloud(text: str) -> bool:
    letters_only = re.sub(r"[^A-Za-z]", "", text).lower()
    if 4 <= len(letters_only) <= 64 and len(set(letters_only)) <= 3:
        dominant_count = max(letters_only.count(char) for char in set(letters_only))
        if dominant_count / len(letters_only) >= 0.7 and (text.count("~") >= 1 or text.count("!") >= 1):
            return True
    tokens = SHORT_WORD_RE.findall(text)
    if len(tokens) < 8:
        return False
    alpha_tokens = [token.lower() for token in tokens if token.isalpha()]
    if len(alpha_tokens) < 6:
        return False
    single_letter_count = sum(len(token) == 1 for token in alpha_tokens)
    if single_letter_count < max(6, int(len(alpha_tokens) * 0.7)):
        return False
    if len({token for token in alpha_tokens if len(token) == 1}) > 4:
        return False
    symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
    return symbol_count >= 6 or text.count("~") >= 3 or text.count("!") >= 2


def _merge_math_fragment_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(records, key=lambda record: (int(record.get("page", 0)), int(record.get("group_index", 0)), int(record.get("split_index", 0))))
    merged: list[dict[str, Any]] = []
    index = 0

    while index < len(ordered):
        record = ordered[index]
        if not _looks_like_math_fragment(record):
            merged.append(record)
            index += 1
            continue

        cluster = [record]
        next_index = index + 1
        page = int(record.get("page", 0))
        while next_index < len(ordered):
            candidate = ordered[next_index]
            if int(candidate.get("page", 0)) != page or not _looks_like_math_fragment(candidate):
                break
            cluster.append(candidate)
            next_index += 1

        combined_text = _clean_text(" ".join(_record_analysis_text(item) for item in cluster))
        if len(cluster) >= 3 and _math_signal_count(combined_text) >= 5:
            merged.append(
                {
                    "id": f"synthetic-math-{page:03d}-{int(cluster[0].get('group_index', 0)):04d}",
                    "page": page,
                    "group_index": int(cluster[0].get("group_index", 0)),
                    "split_index": 1,
                    "type": "paragraph",
                    "text": combined_text,
                    "source_spans": [span for item in cluster for span in _block_source_spans(item)],
                    "meta": {
                        "forced_math_kind": "group" if len(cluster) >= 5 else "display",
                        "source_record_ids": [str(item.get("id", "")) for item in cluster],
                    },
                }
            )
            index = next_index
            continue

        merged.append(record)
        index += 1

    return merged


def _looks_like_affiliation(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:department|departament|university|universitat|univ\.|college|school|institute|faculty|sciences|informatics|inform[aà]tics?|polytechnic|polit[eè]cnica|laborator(?:y|ies)|research labs?|center|centre|cnrs|inria|labri|e-?mail|email|austin|usa|hill|carolina|inc\.?|corp(?:oration)?\.?|ltd\.?|llc|gmbh|parkway|street|st\.|road|rd\.|avenue|ave\.|boulevard|blvd\.|drive|dr\.|suite)\b",
            text,
            re.IGNORECASE,
        )
    )


def _looks_like_author_line(text: str) -> bool:
    if _looks_like_affiliation(text):
        return False
    normalized = _normalize_author_line(text)
    if not normalized or len(normalized) > 140 or normalized.endswith("."):
        return False
    if normalized.startswith("(") and normalized.endswith(")"):
        return False
    if _looks_like_front_matter_metadata(normalized):
        return False
    if ":" in normalized:
        return False
    lowered = normalized.lower()
    if "system" in lowered and normalized.startswith("("):
        return False
    if any(token in lowered for token in ("www.", "sciencedirect", "elsevier")):
        return False
    if re.match(r"^(?:using|integrating|analysis|handling|with|for|of|the)\b", lowered):
        return False
    if any(token in normalized.lower() for token in (" abstract ", " contents ", " figure ", " chapter ", " section ")):
        return False
    if len(re.findall(r"\b[A-Za-z]{2,}\.", normalized)) >= 3:
        return False
    if REFERENCE_VENUE_RE.search(normalized) and "." in normalized:
        return False
    tokens = AUTHOR_TOKEN_RE.findall(normalized)
    max_tokens = 18 if ("," in normalized or " and " in normalized.lower()) else 12
    if not 2 <= len(tokens) <= max_tokens:
        return False
    if normalized.isupper() and len(tokens) > 3:
        return False
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    lowercase_tokens = sum(1 for token in tokens if token.islower())
    return titlecase_like / len(tokens) >= 0.6 and lowercase_tokens <= max(2, len(tokens) // 3)


def _normalize_author_line(text: str) -> str:
    normalized = _clean_text(text)
    normalized = re.sub(r"^\s*by\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\\\([^)]*\\\)", " ", normalized)
    normalized = AUTHOR_MARKER_RE.sub(" ", normalized)
    normalized = normalized.replace("∗", " ")
    normalized = normalized.replace("·", " ")
    normalized = normalized.replace("⋅", " ")
    normalized = re.sub(r"(?<=\s)[*'`\"]+(?=\s|$)", " ", normalized)
    normalized = AUTHOR_AFFILIATION_INDEX_RE.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return compact_text(normalized.strip(" ,;:"))


def _looks_like_contact_name(text: str) -> bool:
    cleaned = _clean_text(text)
    if any(char in cleaned for char in "@:;,[]()"):
        return False
    tokens = NAME_TOKEN_RE.findall(cleaned)
    return 2 <= len(tokens) <= 4


def _looks_like_front_matter_metadata(text: str) -> bool:
    cleaned = _clean_text(text)
    if not cleaned:
        return False
    if cleaned.lower() == "received":
        return True
    if ABBREVIATED_VENUE_LINE_RE.search(cleaned):
        return True
    if TITLE_PAGE_METADATA_RE.search(cleaned) or FRONT_MATTER_METADATA_RE.search(cleaned):
        return True
    return False


def _looks_like_intro_marker(text: str) -> bool:
    cleaned = _clean_text(text)
    if not cleaned:
        return False
    if INTRO_MARKER_RE.match(cleaned):
        return True
    return normalize_title_key(cleaned) in {"introduction", "1introduction"}


def _looks_like_body_section_marker(text: str) -> bool:
    cleaned = clean_heading_title(_clean_text(text))
    if not cleaned or ABSTRACT_MARKER_ONLY_RE.fullmatch(cleaned) or ABSTRACT_LEAD_RE.match(cleaned):
        return False
    if _looks_like_intro_marker(cleaned):
        return True
    title_key = normalize_title_key(cleaned)
    if title_key in {
        "background",
        "preliminaries",
        "methods",
        "results",
        "discussion",
        "conclusion",
        "conclusions",
        "references",
    }:
        return True
    parsed = parse_heading_label(cleaned)
    if parsed is None:
        return False
    _, title = parsed
    normalized_title = normalize_title_key(title)
    return bool(normalized_title and normalized_title not in {"abstract", "keywords"})


def _strip_trailing_abstract_boilerplate(text: str) -> str:
    return compact_text(TRAILING_ABSTRACT_BOILERPLATE_RE.sub("", _clean_text(text)))


def _normalize_abstract_candidate_text(records: list[dict[str, Any]]) -> str:
    text = _clean_text(" ".join(str(record.get("text", "")) for record in records))
    text = PREPRINT_MARKER_RE.sub("", ABSTRACT_LEAD_RE.sub("", text)).strip()
    return _strip_trailing_abstract_boilerplate(text)


def _abstract_text_is_usable(text: str) -> bool:
    return not abstract_quality_flags(text)


def _looks_like_page_one_front_matter_tail(record: dict[str, Any]) -> bool:
    if int(record.get("page", 0) or 0) != 1:
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text:
        return False
    lowered = text.lower()
    if _looks_like_front_matter_metadata(text) or _looks_like_author_line(text) or _looks_like_affiliation(text) or _looks_like_contact_name(text):
        return True
    if any(token in lowered for token in ("www.", "available online", "sciencedirect", "elsevier", "contents lists available")):
        return True
    tokens = SHORT_WORD_RE.findall(text)
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    return len(tokens) <= 6 and bool(tokens) and titlecase_like >= max(1, len(tokens) - 1)


def _split_leading_front_matter_records(prelude: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    front_records: list[dict[str, Any]] = []
    remainder: list[dict[str, Any]] = []
    intro_seen = False

    for record in prelude:
        text = _clean_text(str(record.get("text", "")))
        if not intro_seen and _looks_like_intro_marker(text):
            intro_seen = True
            continue
        if intro_seen:
            if _looks_like_page_one_front_matter_tail(record):
                front_records.append(record)
                continue
            remainder.append(record)
        else:
            front_records.append(record)

    return front_records, remainder


def _parse_authors(text: str) -> list[dict[str, Any]]:
    raw_text = _clean_text(text)
    separated_parts = [
        part.strip(" ,;:")
        for part in re.split(r"\s*[·⋅]\s*|\s+\band\b\s+|\s*,\s*(?=(?:[A-Z]\.\s*)?[A-Z])", raw_text)
        if part.strip(" ,;:")
    ]
    if len(separated_parts) >= 2:
        authors = []
        for part in separated_parts:
            normalized_part = _normalize_author_line(part)
            if normalized_part:
                authors.append({"name": normalized_part, "affiliation_ids": ["aff-1"]})
        if authors:
            return authors

    normalized = _normalize_author_line(text)
    raw_tokens = normalized.split()
    tokens: list[str] = []
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        if token and token[0].isupper() and token.isalpha() and len(token) <= 5:
            combined = token
            next_index = index + 1
            while next_index < len(raw_tokens):
                next_token = raw_tokens[next_index]
                if not next_token.isalpha() or (next_token and next_token[0].isupper()) or len(combined) >= 7:
                    break
                combined += next_token
                next_index += 1
            tokens.append(combined)
            index = next_index
            continue
        tokens.append(token)
        index += 1
    normalized = " ".join(tokens)
    parts = [part.strip() for part in re.split(r"\s{2,}", normalized) if part.strip()]
    if len(parts) >= 2:
        return [{"name": part, "affiliation_ids": ["aff-1"]} for part in parts]

    tokens = normalized.split()
    if len(tokens) >= 4 and len(tokens) % 2 == 0:
        half = len(tokens) // 2
        return [
            {"name": " ".join(tokens[:half]), "affiliation_ids": ["aff-1"]},
            {"name": " ".join(tokens[half:]), "affiliation_ids": ["aff-1"]},
        ]

    return [{"name": normalized, "affiliation_ids": ["aff-1"]}] if normalized else []


def _parse_authors_from_citation_line(text: str, title: str) -> list[dict[str, Any]]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []
    cleaned_key = normalize_title_key(cleaned)
    title_keys = _title_lookup_keys(title)
    if not title_keys or not any(title_key in cleaned_key for title_key in title_keys):
        return []
    year_match = CITATION_YEAR_RE.search(cleaned)
    if year_match is None:
        return []

    citation_prefix = cleaned[: year_match.start()].strip(" ,;:")
    if not citation_prefix or _looks_like_front_matter_metadata(citation_prefix):
        return []

    citation_prefix = re.sub(r"\s*,\s*&\s*", ", ", citation_prefix)
    citation_prefix = re.sub(r"\s*&\s*", ", ", citation_prefix)
    separated_parts = [
        part.strip(" ,;:")
        for part in CITATION_AUTHOR_SPLIT_RE.split(citation_prefix)
        if part.strip(" ,;:")
    ]
    if len(separated_parts) < 2:
        return []

    authors: list[dict[str, Any]] = []
    for part in separated_parts:
        normalized_part = re.sub(r",\s*(?=[A-Z](?:\.[A-Z])*\.?$)", " ", part)
        normalized_part = _normalize_author_line(normalized_part)
        tokens = SHORT_WORD_RE.findall(normalized_part)
        if len(tokens) < 2 or len(tokens) > 6:
            continue
        if _looks_like_affiliation(normalized_part) or _looks_like_front_matter_metadata(normalized_part):
            continue
        authors.append({"name": normalized_part, "affiliation_ids": ["aff-1"]})
    return authors if len(authors) >= 2 else []


def _is_title_page_metadata_record(record: dict[str, Any]) -> bool:
    page = int(record.get("page", 0) or 0)
    if page != 1:
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text:
        return False
    if PREPRINT_MARKER_RE.fullmatch(text):
        return True
    if _looks_like_front_matter_metadata(text) or AUTHOR_NOTE_RE.search(text):
        return True
    bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 0.0))
    if y0 >= 620.0 and (_looks_like_affiliation(text) or _looks_like_contact_name(text)):
        return True
    return False


def _normalize_affiliation_line(text: str) -> str:
    normalized = _clean_text(text)
    lowered_original = normalized.lower()
    if lowered_original.startswith("email") or lowered_original.startswith("e-mail"):
        return ""
    normalized = re.sub(r"\bE-?mail\s*:\s*[^\s,;]+", " ", normalized, flags=re.IGNORECASE)
    normalized = AUTHOR_NOTE_RE.sub(" ", normalized)
    normalized = re.sub(r"^[*†‡]?\s*\d+\s+", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = compact_text(normalized).strip(" ,;:")
    lowered = normalized.lower()
    if lowered.startswith("e-mail addresses") or lowered.startswith("email") or lowered.startswith("e-mail"):
        return ""
    if lowered in {"com", "edu", "org", "net"}:
        return ""
    return normalized


def _looks_like_affiliation_continuation(text: str) -> bool:
    cleaned = _clean_text(text).strip(" ,;:")
    if not cleaned or _looks_like_front_matter_metadata(cleaned):
        return False
    if re.search(r"\d", cleaned):
        return False
    tokens = SHORT_WORD_RE.findall(cleaned)
    if not 1 <= len(tokens) <= 4:
        return False
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    return titlecase_like >= max(1, len(tokens) - 1)


def _split_affiliation_fields(affiliation_lines: list[str]) -> tuple[str, str, str]:
    cleaned_lines = [_normalize_affiliation_line(line) for line in affiliation_lines if _normalize_affiliation_line(line)]
    if not cleaned_lines:
        return "", "", ""
    if len(cleaned_lines) == 1:
        parts = [part.strip() for part in cleaned_lines[0].split(",") if part.strip()]
        if len(parts) >= 3:
            return parts[0], parts[1], ", ".join(parts[2:])
        return cleaned_lines[0], "", ""
    department = cleaned_lines[0]
    institution = cleaned_lines[1] if len(cleaned_lines) > 1 else ""
    address = " ".join(cleaned_lines[2:]) if len(cleaned_lines) > 2 else ""
    return department, institution, address


def _dedupe_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for author in authors:
        name = _normalize_author_line(str(author.get("name", "")))
        if not name:
            continue
        key = normalize_title_key(name)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append({"name": name, "affiliation_ids": list(author.get("affiliation_ids", [])) or ["aff-1"]})
    return deduped


def _filter_front_matter_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for author in authors:
        name = _normalize_author_line(str(author.get("name", "")))
        if not name:
            continue
        if len(SHORT_WORD_RE.findall(name)) < 2:
            continue
        lowered = name.lower()
        if _looks_like_affiliation(name) or _looks_like_front_matter_metadata(name):
            continue
        if any(
            token in lowered
            for token in (" university", " institute", " department", " research", " corporate", " laboratory")
        ):
            continue
        filtered.append({"name": name, "affiliation_ids": list(author.get("affiliation_ids", [])) or ["aff-1"]})
    return _dedupe_authors(filtered)


def _build_affiliations_for_authors(author_count: int, affiliation_lines: list[str]) -> tuple[list[dict[str, Any]], list[list[str]]]:
    cleaned_lines = [_normalize_affiliation_line(line) for line in affiliation_lines if _normalize_affiliation_line(line)]
    if not cleaned_lines:
        return [], [[] for _ in range(author_count)]

    if author_count > 1 and len(cleaned_lines) == author_count:
        affiliations: list[dict[str, Any]] = []
        author_affiliation_ids: list[list[str]] = []
        for index, line in enumerate(cleaned_lines, start=1):
            department, institution, address = _split_affiliation_fields([line])
            affiliation_id = f"aff-{index}"
            affiliations.append(
                {
                    "id": affiliation_id,
                    "department": department,
                    "institution": institution,
                    "address": address,
                }
            )
            author_affiliation_ids.append([affiliation_id])
        return affiliations, author_affiliation_ids

    department, institution, address = _split_affiliation_fields(cleaned_lines)
    affiliations = [
        {
            "id": "aff-1",
            "department": department,
            "institution": institution,
            "address": address,
        }
    ]
    return affiliations, [["aff-1"] for _ in range(author_count)]


FRONT_MATTER_MISSING_PLACEHOLDER = MISSING_ABSTRACT_PLACEHOLDER


def _missing_front_matter_author() -> dict[str, Any]:
    return {"name": FRONT_MATTER_MISSING_PLACEHOLDER, "affiliation_ids": ["aff-1"]}


def _missing_front_matter_affiliation() -> dict[str, Any]:
    return {
        "id": "aff-1",
        "department": FRONT_MATTER_MISSING_PLACEHOLDER,
        "institution": "",
        "address": "",
    }


def _strip_author_prefix_from_affiliation_line(text: str, authors: list[dict[str, Any]]) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""
    for author in authors:
        author_name = _normalize_author_line(str(author.get("name", "")))
        if not author_name:
            continue
        for prefix in (author_name, f"by {author_name}"):
            if cleaned.lower().startswith(prefix.lower() + " "):
                return _clean_text(cleaned[len(prefix) :])
    return cleaned


def _title_lookup_keys(title: str) -> list[str]:
    cleaned = _clean_text(title)
    candidates = [cleaned]
    without_year = re.sub(r"^\s*\d{4}\s+", "", cleaned)
    if without_year != cleaned:
        candidates.append(without_year)

    for candidate in list(candidates):
        stripped = re.sub(r"^\s*(?:a|an|the)\s+", "", candidate, flags=re.IGNORECASE)
        if stripped != candidate:
            candidates.append(stripped)

    keys: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = normalize_title_key(candidate)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def _matches_title_line(text: str, title: str) -> bool:
    cleaned_key = normalize_title_key(_clean_text(text))
    title_keys = _title_lookup_keys(title)
    if cleaned_key and title_keys:
        for title_key in title_keys:
            if cleaned_key == title_key:
                return True
            if len(cleaned_key) >= 16 and title_key.startswith(cleaned_key):
                return True
            if len(title_key) >= 16 and cleaned_key.startswith(title_key):
                return True

    record_words = [token.lower() for token in SHORT_WORD_RE.findall(compact_text(text))]
    title_words = [token.lower() for token in SHORT_WORD_RE.findall(compact_text(title))]
    if not record_words or not title_words:
        return False
    if record_words == title_words:
        return True
    if len(record_words) >= len(title_words) and record_words[: len(title_words)] == title_words:
        return True
    if len(record_words) >= 4 and len(record_words) < len(title_words) and title_words[: len(record_words)] == record_words:
        return True
    return False


def _dedupe_text_lines(lines: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for line in lines:
        cleaned = _clean_text(line)
        key = normalize_title_key(cleaned)
        if not cleaned or not key or key in seen:
            continue
        seen.add(key)
        deduped.append(cleaned)
    return deduped


def _clone_record_with_text(record: dict[str, Any], text: str) -> dict[str, Any]:
    cloned = dict(record)
    cloned["text"] = _clean_text(text)
    return cloned


def _record_word_count(record: dict[str, Any]) -> int:
    return len(SHORT_WORD_RE.findall(_clean_text(str(record.get("text", "")))))


def _build_front_matter(
    paper_id: str,
    prelude: list[dict[str, Any]],
    page_one_records: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    next_block_index: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]:
    def collect_abstract_and_funding_records(
        candidate_records: list[dict[str, Any]],
        *,
        allow_fallback: bool,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if any(normalize_title_key(str(record.get("text", ""))) == "participants" for record in candidate_records[:12]):
            return [], []
        abstract_records: list[dict[str, Any]] = []
        funding_records: list[dict[str, Any]] = []
        abstract_anchor_index: int | None = None
        inline_abstract_record: dict[str, Any] | None = None
        for index, record in enumerate(candidate_records):
            text = _clean_text(str(record.get("text", "")))
            if not text:
                continue
            if ABSTRACT_MARKER_ONLY_RE.fullmatch(text):
                abstract_anchor_index = index
                break
            if ABSTRACT_LEAD_RE.match(text):
                abstract_anchor_index = index
                stripped_text = PREPRINT_MARKER_RE.sub("", ABSTRACT_LEAD_RE.sub("", text)).strip()
                if stripped_text:
                    inline_abstract_record = _clone_record_with_text(record, stripped_text)
                break
            if _looks_like_body_section_marker(text):
                break

        if abstract_anchor_index is not None:
            if inline_abstract_record is not None:
                abstract_records.append(inline_abstract_record)
            total_words = _record_word_count(inline_abstract_record or {})
            for record in candidate_records[abstract_anchor_index + 1 :]:
                text = _clean_text(str(record.get("text", "")))
                if not text or _looks_like_body_section_marker(text):
                    break
                if KEYWORDS_LEAD_RE.match(text):
                    if abstract_records:
                        break
                    continue
                if _looks_like_author_line(text) or _looks_like_affiliation(text):
                    continue
                if _looks_like_front_matter_metadata(text) or AUTHOR_NOTE_RE.search(text):
                    continue
                if FUNDING_RE.search(text):
                    funding_records.append(record)
                    continue
                abstract_records.append(record)
                total_words += _record_word_count(record)
                if len(abstract_records) >= 6 or total_words >= 360:
                    break
            if abstract_records and not _abstract_text_is_usable(_normalize_abstract_candidate_text(abstract_records)):
                return [], funding_records
            return abstract_records, funding_records

        if not allow_fallback:
            return [], funding_records
        body_boundary_seen = any(_looks_like_body_section_marker(str(record.get("text", ""))) for record in candidate_records)

        started_abstract = False
        start_page: int | None = None
        total_words = 0
        for record in candidate_records:
            text = _clean_text(str(record.get("text", "")))
            if not text or _looks_like_body_section_marker(text):
                break
            if KEYWORDS_LEAD_RE.match(text):
                if started_abstract:
                    break
                continue
            if _looks_like_front_matter_metadata(text) or AUTHOR_NOTE_RE.search(text):
                if started_abstract:
                    break
                continue
            if FUNDING_RE.search(text):
                funding_records.append(record)
                if started_abstract:
                    break
                continue
            if _matches_title_line(text, title) or text.lower() == "and":
                continue
            if _looks_like_author_line(text) or _looks_like_affiliation(text):
                continue
            if not started_abstract and _record_word_count(record) < 14:
                continue
            if started_abstract and not body_boundary_seen:
                break
            record_page = int(record.get("page", 0) or 0)
            started_abstract = True
            if start_page is None:
                start_page = record_page
            elif start_page and record_page and record_page != start_page:
                break
            abstract_records.append(record)
            total_words += _record_word_count(record)
            if len(abstract_records) >= 3 or total_words >= 260:
                break
        if abstract_records and not _abstract_text_is_usable(_normalize_abstract_candidate_text(abstract_records)):
            return [], funding_records
        return abstract_records, funding_records

    leading_front_records, remainder = _split_leading_front_matter_records(prelude)
    front_records = [_clean_record(record) for record in leading_front_records]

    metadata = paper_metadata(paper_id) or {}
    title = str(metadata.get("title") or paper_id.replace("_", " "))

    title_indices = [
        index
        for index, record in enumerate(front_records)
        if _matches_title_line(str(record.get("text", "")), title)
    ]
    boundary_candidates = [
        index
        for index, record in enumerate(front_records)
        if ABSTRACT_MARKER_ONLY_RE.fullmatch(_clean_text(str(record.get("text", ""))))
        or ABSTRACT_LEAD_RE.match(_clean_text(str(record.get("text", ""))))
        or _looks_like_intro_marker(str(record.get("text", "")))
    ]
    first_boundary_index = min(boundary_candidates) if boundary_candidates else None
    content_start_index = 0
    if title_indices:
        tentative_start_index = title_indices[-1] + 1
        if first_boundary_index is None or tentative_start_index <= first_boundary_index:
            content_start_index = tentative_start_index
    content_records = front_records[content_start_index:]

    leading_boundary_index = len(content_records)
    for index, record in enumerate(content_records):
        text = _clean_text(str(record.get("text", "")))
        if ABSTRACT_MARKER_ONLY_RE.fullmatch(text) or ABSTRACT_LEAD_RE.match(text) or _looks_like_intro_marker(text):
            leading_boundary_index = index
            break

    author_candidates: list[dict[str, Any]] = []
    affiliation_lines: list[str] = []
    affiliation_continuation_open = False
    for record in content_records[:leading_boundary_index]:
        text = _clean_text(str(record.get("text", "")))
        if not text or _matches_title_line(text, title):
            affiliation_continuation_open = False
            continue
        if _looks_like_front_matter_metadata(text) or AUTHOR_NOTE_RE.search(text):
            affiliation_continuation_open = False
            continue
        if text.lower() == "and":
            affiliation_continuation_open = False
            continue
        if _looks_like_affiliation(text):
            affiliation_lines.append(text)
            continue
        if (
            affiliation_lines
            and _looks_like_affiliation_continuation(text)
            and (affiliation_continuation_open or text.rstrip().endswith(","))
        ):
            affiliation_lines.append(text)
            affiliation_continuation_open = True
            continue
        affiliation_continuation_open = False
        if _looks_like_author_line(text):
            author_candidates.append(record)

    page_one_clean_records = [
        _clean_record(record)
        for record in page_one_records
        if int(record.get("page", 0) or 0) == 1
    ]
    page_one_title_indices = [
        index
        for index, record in enumerate(page_one_clean_records)
        if _matches_title_line(str(record.get("text", "")), title)
    ]
    page_one_content_start_index = page_one_title_indices[0] + 1 if page_one_title_indices else 0
    while page_one_content_start_index < len(page_one_clean_records) and _matches_title_line(
        str(page_one_clean_records[page_one_content_start_index].get("text", "")),
        title,
    ):
        page_one_content_start_index += 1

    page_one_boundary_index = len(page_one_clean_records)
    for index, record in enumerate(page_one_clean_records[page_one_content_start_index:], start=page_one_content_start_index):
        text = _clean_text(str(record.get("text", "")))
        if ABSTRACT_MARKER_ONLY_RE.fullmatch(text) or ABSTRACT_LEAD_RE.match(text) or _looks_like_intro_marker(text):
            page_one_boundary_index = index
            break

    page_one_author_candidates: list[dict[str, Any]] = []
    page_one_affiliation_lines: list[str] = []
    affiliation_continuation_open = False
    for record in page_one_clean_records[page_one_content_start_index:page_one_boundary_index]:
        text = _clean_text(str(record.get("text", "")))
        if not text or _matches_title_line(text, title):
            affiliation_continuation_open = False
            continue
        if ABSTRACT_MARKER_ONLY_RE.fullmatch(text) or ABSTRACT_LEAD_RE.match(text):
            affiliation_continuation_open = False
            continue
        if _looks_like_front_matter_metadata(text) or FUNDING_RE.search(text) or text.lower() == "and":
            affiliation_continuation_open = False
            continue
        if _looks_like_affiliation(text):
            page_one_affiliation_lines.append(text)
            continue
        if (
            page_one_affiliation_lines
            and _looks_like_affiliation_continuation(text)
            and (affiliation_continuation_open or text.rstrip().endswith(","))
        ):
            page_one_affiliation_lines.append(text)
            affiliation_continuation_open = True
            continue
        affiliation_continuation_open = False
        if _looks_like_author_line(text):
            page_one_author_candidates.append(record)

    author_candidates.extend(page_one_author_candidates)
    affiliation_lines.extend(page_one_affiliation_lines)
    affiliation_lines = _dedupe_text_lines(affiliation_lines)

    page_one_authors = _filter_front_matter_authors(
        [
            author
            for record in page_one_author_candidates
            for author in _parse_authors(str(record.get("text", "")))
        ]
    )
    authors = _filter_front_matter_authors(
        [
            author
            for record in author_candidates
            for author in _parse_authors(str(record.get("text", "")))
        ]
    )
    if len(page_one_authors) >= 2:
        authors = page_one_authors
        deduped_page_one_affiliations = _dedupe_text_lines(page_one_affiliation_lines)
        if deduped_page_one_affiliations:
            mathpix_affiliation_lines = [line for line in deduped_page_one_affiliations if r"\(" in line]
            affiliation_lines = mathpix_affiliation_lines or deduped_page_one_affiliations

    if not authors:
        citation_authors = _filter_front_matter_authors(
            [
                author
                for record in content_records[:leading_boundary_index]
                + page_one_clean_records[page_one_content_start_index:]
                for author in _parse_authors_from_citation_line(str(record.get("text", "")), title)
            ]
        )
        if citation_authors:
            authors = citation_authors
    if not authors:
        for record in content_records[:leading_boundary_index]:
            text = _clean_text(str(record.get("text", "")))
            if not text or _matches_title_line(text, title):
                continue
            if _looks_like_front_matter_metadata(text) or AUTHOR_NOTE_RE.search(text) or _looks_like_affiliation(text):
                continue
            if _looks_like_contact_name(text):
                authors = [{"name": _normalize_author_line(text), "affiliation_ids": ["aff-1"]}]
                break
    if not authors:
        authors = [_missing_front_matter_author()]

    affiliation_lines = [
        stripped
        for line in affiliation_lines
        if (stripped := _strip_author_prefix_from_affiliation_line(line, authors))
    ]
    affiliations, author_affiliation_ids = _build_affiliations_for_authors(len(authors), affiliation_lines)
    if not affiliations:
        affiliations = [_missing_front_matter_affiliation()]
        author_affiliation_ids = [["aff-1"] for _ in range(len(authors))]
    for author, affiliation_ids in zip(authors, author_affiliation_ids):
        author["affiliation_ids"] = affiliation_ids or author.get("affiliation_ids", ["aff-1"])

    abstract_records, funding_records = collect_abstract_and_funding_records(content_records, allow_fallback=False)
    if not abstract_records:
        page_one_content_records = page_one_clean_records[page_one_content_start_index:]
        page_one_abstract_records, page_one_funding_records = collect_abstract_and_funding_records(
            page_one_content_records,
            allow_fallback=True,
        )
        if page_one_abstract_records:
            abstract_records = page_one_abstract_records
        if page_one_funding_records:
            funding_records = page_one_funding_records

    abstract_block_id: str | None = None
    if abstract_records:
        abstract_text = _normalize_abstract_candidate_text(abstract_records)
        if abstract_text and _abstract_text_is_usable(abstract_text):
            abstract_block_id = f"blk-front-abstract-{next_block_index}"
            blocks.append(
                {
                    "id": abstract_block_id,
                    "type": "paragraph",
                    "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                    "source_spans": [span for record in abstract_records for span in _block_source_spans(record)],
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
            next_block_index += 1
    if abstract_block_id is None:
        abstract_block_id = f"blk-front-abstract-{next_block_index}"
        blocks.append(
            {
                "id": abstract_block_id,
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": FRONT_MATTER_MISSING_PLACEHOLDER}]},
                "source_spans": [],
                "alternates": [],
                "review": default_review(risk="low", status="edited", notes=FRONT_MATTER_MISSING_PLACEHOLDER),
            }
        )
        next_block_index += 1

    funding_block_id: str | None = None
    if funding_records:
        funding_text = _clean_text(" ".join(str(record["text"]) for record in funding_records))
        if funding_text:
            funding_block_id = f"blk-front-funding-{next_block_index}"
            blocks.append(
                {
                    "id": funding_block_id,
                    "type": "footnote",
                    "content": {"text": funding_text},
                    "source_spans": [span for record in funding_records for span in _block_source_spans(record)],
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
            next_block_index += 1

    front_matter = {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "abstract_block_id": abstract_block_id,
        "funding_block_id": funding_block_id,
    }
    cleaned_remainder = [
        record
        for record in remainder
        if not (
            int(record.get("page", 0) or 0) == 1
            and (
                _matches_title_line(str(record.get("text", "")), title)
                or _looks_like_front_matter_metadata(str(record.get("text", "")))
                or AUTHOR_NOTE_RE.search(_clean_text(str(record.get("text", ""))))
                or _looks_like_affiliation(str(record.get("text", "")))
                or _looks_like_author_line(str(record.get("text", "")))
                or _looks_like_contact_name(str(record.get("text", "")))
            )
        )
    ]
    return front_matter, blocks, next_block_index, cleaned_remainder


def _section_id(node: Any, fallback_index: int) -> str:
    label = getattr(node, "label", None)
    if label:
        return f"sec-{'-'.join(label)}"
    title = normalize_title_key(str(getattr(node, 'title', '')))
    return f"sec-{title or f'u-{fallback_index}'}"


def _front_block_text(blocks: list[dict[str, Any]], block_id: str | None) -> str:
    if not block_id:
        return ""
    for block in blocks:
        if str(block.get("id", "")) != str(block_id):
            continue
        spans = block.get("content", {}).get("spans", [])
        parts = [
            _clean_text(str(span.get("text", "")))
            for span in spans
            if isinstance(span, dict) and span.get("kind") == "text"
        ]
        return _clean_text(" ".join(part for part in parts if part))
    return ""


def _abstract_text_looks_like_metadata(text: str) -> bool:
    return bool(abstract_quality_flags(text))


def _leading_abstract_text(node: SectionNode) -> tuple[str, list[dict[str, Any]]]:
    records = [
        record
        for record in node.records
        if record.get("type") in {"paragraph", "front_matter", "footnote"}
        and not _looks_like_front_matter_metadata(str(record.get("text", "")))
        and not AUTHOR_NOTE_RE.search(str(record.get("text", "")))
    ]
    text = _normalize_abstract_candidate_text(records)
    return text, records


def _first_root_indicates_missing_intro(roots: list[Any]) -> bool:
    if not roots:
        return False
    first_root = roots[0]
    title_key = _normalize_section_title(str(first_root.title))
    if title_key in {"abstract", "introduction"}:
        return False
    label = getattr(first_root, "label", None)
    if not label:
        return False
    return label[0] != "1" or len(label) > 1


def _split_late_prelude_for_missing_intro(
    prelude: list[dict[str, Any]],
    roots: list[Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not prelude or not _first_root_indicates_missing_intro(roots):
        return prelude, []

    first_page = int(prelude[0].get("page", 0) or 0)
    leading: list[dict[str, Any]] = []
    overflow: list[dict[str, Any]] = []
    overflow_started = False
    for record in prelude:
        page = int(record.get("page", first_page) or first_page)
        if page != first_page:
            overflow_started = True
        if overflow_started:
            overflow.append(record)
        else:
            leading.append(record)

    if not overflow:
        return prelude, []
    return leading, overflow


def _flatten_sections(roots: list[Any]) -> list[Any]:
    ordered: list[Any] = []

    def visit(node: Any) -> None:
        ordered.append(node)
        for child in node.children:
            visit(child)

    for root in roots:
        visit(root)
    return ordered


def _attach_orphan_numbered_roots(roots: list[Any]) -> list[Any]:
    adjusted: list[Any] = []
    index = 0
    while index < len(roots):
        node = roots[index]
        title_key = _normalize_section_title(str(node.title))
        if getattr(node, "label", None) is None and title_key in {"background", "introduction"}:
            expected_prefix = "2" if title_key == "background" else "1"
            children: list[Any] = list(node.children)
            next_index = index + 1
            while next_index < len(roots):
                candidate = roots[next_index]
                label = getattr(candidate, "label", None)
                if not label:
                    break
                if label[0] != expected_prefix or len(label) <= 1:
                    break
                children.append(candidate)
                next_index += 1
            node.children = children
            if title_key == "background":
                node.label = ("2",)
            elif title_key == "introduction":
                node.label = ("1",)
            adjusted.append(node)
            index = next_index
            continue
        adjusted.append(node)
        index += 1
    return adjusted


def _normalize_section_title(title: str) -> str:
    cleaned = clean_heading_title(_clean_text(title))
    parsed = parse_heading_label(cleaned)
    if parsed is not None:
        _, cleaned = parsed
    return normalize_title_key(cleaned)


def _make_reference_entry(record: dict[str, Any], index: int) -> dict[str, Any]:
    raw_text = _clean_text(str(record.get("text", "")))
    text, _ = normalize_reference_text(raw_text)
    return {
        "id": f"ref-{index:03d}",
        "raw_text": raw_text,
        "text": text,
        "source_spans": _block_source_spans(record),
        "alternates": [],
        "review": default_review(risk="medium"),
    }


def _is_reference_start(record: dict[str, Any]) -> bool:
    text = _clean_text(str(record.get("text", "")))
    if not text or not re.search(r"[A-Za-z]", text):
        return False
    if str(record.get("type", "")) == "list_item" and _looks_like_reference_text(text):
        return True
    bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    x0 = float(bbox.get("x0", 0.0))
    if x0 > 90:
        return False
    return bool(REFERENCE_START_RE.match(text))


def _merge_reference_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for record in records:
        text = _clean_text(str(record.get("text", "")))
        if not text or not re.search(r"[A-Za-z]", text):
            continue
        bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
        x0 = float(bbox.get("x0", 0.0))
        if current is None or _is_reference_start(record):
            if current is not None:
                merged.append(current)
            current = {
                "id": f"merged-{record.get('id', '')}",
                "type": "reference",
                "page": int(record.get("page", 0)),
                "group_index": int(record.get("group_index", 0)),
                "split_index": 1,
                "text": text,
                "source_spans": list(_block_source_spans(record)),
                "meta": {"source_record_ids": [str(record.get("id", ""))]},
            }
            continue

        if current is not None and x0 >= 100:
            current["text"] = _clean_text(f"{current['text']} {text}")
            current["source_spans"].extend(_block_source_spans(record))
            current["meta"]["source_record_ids"].append(str(record.get("id", "")))
            continue

        if current is not None:
            merged.append(current)
        current = {
            "id": f"merged-{record.get('id', '')}",
            "type": "reference",
            "page": int(record.get("page", 0)),
            "group_index": int(record.get("group_index", 0)),
            "split_index": 1,
            "text": text,
            "source_spans": list(_block_source_spans(record)),
            "meta": {"source_record_ids": [str(record.get("id", ""))]},
        }

    if current is not None:
        merged.append(current)
    return merged


def _looks_like_reference_text(text: str) -> bool:
    cleaned = _clean_text(text)
    if len(cleaned) < 20 or not re.search(r"[A-Za-z]", cleaned):
        return False
    has_year = bool(REFERENCE_YEAR_RE.search(cleaned))
    has_venue = bool(REFERENCE_VENUE_RE.search(cleaned))
    if has_year and has_venue:
        return True
    if has_year and REFERENCE_AUTHOR_RE.match(cleaned):
        return True
    if has_year and "," in cleaned and len(SHORT_WORD_RE.findall(cleaned)) >= 6:
        return True
    if has_venue and REFERENCE_AUTHOR_RE.match(cleaned):
        return True
    if has_venue and "," in cleaned and len(SHORT_WORD_RE.findall(cleaned)) >= 6:
        return True
    return False


def _split_trailing_reference_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    split_index = len(records)
    while split_index > 0 and _looks_like_reference_text(str(records[split_index - 1].get("text", ""))):
        split_index -= 1

    trailing = records[split_index:]
    if len(trailing) < 5:
        return records, []

    return records[:split_index], _merge_reference_records(trailing)


def _extract_reference_records_from_tail_section(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(records) < 8:
        return records, []

    reference_records: list[dict[str, Any]] = []
    body_records: list[dict[str, Any]] = []
    for record in records:
        text = _clean_text(str(record.get("text", "")))
        if not text:
            body_records.append(record)
            continue
        if ABOUT_AUTHOR_RE.match(text):
            body_records.append(record)
            continue
        if _looks_like_reference_text(text):
            reference_records.append(record)
            continue
        body_records.append(record)

    if len(reference_records) < 5:
        return records, []

    return body_records, _merge_reference_records(reference_records)


def _reference_records_from_mathpix_layout(layout: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not layout:
        return []

    reference_records: list[dict[str, Any]] = []
    references_started = False
    for page in sorted(_mathpix_text_blocks_by_page(layout)):
        for block in _mathpix_text_blocks_by_page(layout)[page]:
            text = _clean_text(str(block.text))
            if not text:
                continue
            if not references_started:
                if normalize_title_key(text) == "references":
                    references_started = True
                continue
            if re.match(r"^\[\s*\d+\s*\]", text):
                reference_records.append(_layout_record(block))
                continue
            if reference_records:
                reference_records.append(_layout_record(block))

    if len(reference_records) < 3:
        return []
    return _merge_reference_records(reference_records)


def _starts_like_sentence(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped:
        return False
    first = stripped[0]
    return first.isupper() or first.isdigit() or stripped.startswith(("(", '"', "'"))


def _starts_like_paragraph_continuation(text: str) -> bool:
    stripped = _clean_text(text)
    if not stripped:
        return False
    if stripped[:1].islower():
        return True
    return bool(re.match(r"^(?:and|but|or|then|thus|therefore|however|where|which|with|while|when|since|because|as)\b", stripped, re.IGNORECASE))


def _starts_like_strong_paragraph_continuation(text: str) -> bool:
    stripped = _clean_text(text)
    if not stripped:
        return False
    return bool(re.match(r"^(?:then|with|where|representing|is|are)\b", stripped, re.IGNORECASE))


def _ends_like_short_lead_in(text: str) -> bool:
    cleaned = _clean_text(text).lower()
    if not cleaned:
        return False
    if cleaned.endswith(("consists of", "defined as", "given by", "represented as")):
        return True
    return cleaned.endswith((" of", " by", " as", " with", " from", " to", " that"))


def _ends_like_clause_lead_in(text: str) -> bool:
    cleaned = _clean_text(text).lower()
    if not cleaned:
        return False
    return bool(re.search(r"\b(?:which|that|where|when|while|whose|because|since|as)$", cleaned))


def _is_paragraph_like_record(record: dict[str, Any]) -> bool:
    return str(record.get("type", "")) in {"paragraph", "front_matter"}


def _merge_anchor_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
    spans = list(_block_source_spans(record))
    if len(spans) <= 1:
        return spans
    body_like_spans: list[dict[str, Any]] = []
    wide_body_like_spans: list[dict[str, Any]] = []
    for span in spans:
        bbox = span.get("bbox", {}) if isinstance(span, dict) else {}
        y0 = float(bbox.get("y0", 0.0))
        height = float(bbox.get("height", 0.0))
        width = float(bbox.get("width", 0.0))
        if y0 > 80.0 or height > 10.0:
            body_like_spans.append(span)
            if width >= 100.0:
                wide_body_like_spans.append(span)
    return wide_body_like_spans or body_like_spans or spans


def _looks_like_running_header_record(record: dict[str, Any]) -> bool:
    if str(record.get("type", "")) not in {"paragraph", "heading"}:
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text or RUNNING_HEADER_TEXT_RE.fullmatch(text) is None:
        return False
    words = SHORT_WORD_RE.findall(text)
    if not words or len(words) > 6:
        return False
    bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 0.0))
    width = float(bbox.get("width", 0.0))
    return y0 <= 100.0 and 80.0 <= width <= 320.0


def _looks_like_table_body_debris(record: dict[str, Any]) -> bool:
    if str(record.get("type", "")) != "paragraph":
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text:
        return False
    spans = _block_source_spans(record)
    if len(spans) < 12:
        return False
    words = text.split()
    if len(words) < 20:
        return False
    span_widths = [float(span.get("bbox", {}).get("width", 0.0)) for span in spans]
    if not span_widths:
        return False
    narrow_span_count = sum(1 for width in span_widths if 0.0 < width <= 40.0)
    if narrow_span_count < len(span_widths) * 0.65:
        return False
    short_or_numeric_token_count = 0
    for token in words:
        compact = token.strip(".,;:()[]{}")
        letters_only = re.sub(r"[^A-Za-z]", "", compact)
        if any(char.isdigit() for char in compact) or len(letters_only) <= 3:
            short_or_numeric_token_count += 1
    return short_or_numeric_token_count / max(len(words), 1) >= 0.55


def _suppress_embedded_table_headings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for record in records:
        if str(record.get("type", "")) == "heading":
            text = _clean_text(str(record.get("text", "")))
            bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
            y0 = float(bbox.get("y0", 0.0))
            previous = kept[-1] if kept else None
            previous_bbox = (_block_source_spans(previous)[:1] or [{}])[0].get("bbox", {}) if previous else {}
            previous_page = int(((_block_source_spans(previous)[:1] or [{}])[0].get("page", previous.get("page", 0)) if previous else 0) or 0)
            current_page = int(((_block_source_spans(record)[:1] or [{}])[0].get("page", record.get("page", 0))) or 0)
            previous_text = _clean_text(str(previous.get("text", ""))) if previous else ""
            if (
                previous is not None
                and str(previous.get("type", "")) == "caption"
                and previous_page == current_page
                and TABLE_CAPTION_RE.match(previous_text)
                and parse_heading_label(clean_heading_title(text)) is None
                and 0.0 <= y0 - float(previous_bbox.get("y1", 0.0)) <= 80.0
            ):
                continue
        kept.append(record)
    return kept


def _looks_like_same_page_column_continuation(
    previous_x0: float,
    previous_y0: float,
    previous_y1: float,
    current_x0: float,
    current_y0: float,
) -> bool:
    return current_x0 >= previous_x0 + 80 and current_y0 + 30 < previous_y1 and current_y0 <= previous_y0 + 24


def _should_merge_paragraph_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    if not _is_paragraph_like_record(previous) or not _is_paragraph_like_record(current):
        return False
    if previous.get("meta", {}).get("forced_math_kind") or current.get("meta", {}).get("forced_math_kind"):
        return False
    if previous.get("meta", {}).get("external_display_math_overlap_count") or current.get("meta", {}).get("external_display_math_overlap_count"):
        return False

    previous_text = _clean_text(str(previous.get("text", "")))
    current_text = _clean_text(str(current.get("text", "")))
    if not previous_text or not current_text:
        return False
    previous_word_count = len(SHORT_WORD_RE.findall(previous_text))
    current_word_count = len(SHORT_WORD_RE.findall(current_text))

    previous_span = (_merge_anchor_spans(previous)[-1:] or [{}])[0]
    current_span = (_merge_anchor_spans(current)[:1] or [{}])[0]
    previous_bbox = previous_span.get("bbox", {})
    current_bbox = current_span.get("bbox", {})
    previous_page = int(previous_span.get("page", previous.get("page", 0)) or 0)
    current_page = int(current_span.get("page", current.get("page", 0)) or 0)
    previous_x0 = float(previous_bbox.get("x0", 0.0))
    current_x0 = float(current_bbox.get("x0", 0.0))
    previous_y0 = float(previous_bbox.get("y0", 0.0))
    previous_y1 = float(previous_bbox.get("y1", 0.0))
    previous_width = float(previous_bbox.get("width", 0.0))
    current_y0 = float(current_bbox.get("y0", 0.0))
    current_width = float(current_bbox.get("width", 0.0))
    vertical_gap = current_y0 - previous_y1
    previous_has_terminal = TERMINAL_PUNCTUATION_RE.search(previous_text) is not None
    current_continues = _starts_like_paragraph_continuation(current_text)

    if current_page == previous_page:
        if not previous_has_terminal and current_continues and current_width <= 1.0 and 0.0 <= vertical_gap <= 24.0:
            return True
        if not previous_has_terminal and current_continues and 0.0 <= vertical_gap <= 14.0:
            return True
        if (
            not previous_has_terminal
            and current_continues
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 48.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and _starts_like_strong_paragraph_continuation(current_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and 0.0 <= vertical_gap <= 180.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and previous_text.strip().lower() in {"where", "where:"}
            and _starts_like_strong_paragraph_continuation(current_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 120.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and _starts_like_strong_paragraph_continuation(current_text)
            and previous_word_count <= 6
            and _ends_like_short_lead_in(previous_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and 0.0 <= vertical_gap <= 120.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and current_text[:1].islower()
            and previous_word_count >= 12
            and _ends_like_short_lead_in(previous_text)
            and abs(current_x0 - previous_x0) <= 32.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and previous_y0 <= 120.0
            and 120.0 < vertical_gap <= 420.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_word_count >= 12
            and current_word_count >= 5
            and _ends_like_clause_lead_in(previous_text)
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 200.0
            and current_width >= 200.0
            and 0.0 <= vertical_gap <= 140.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_text.rstrip().endswith(",")
            and previous_word_count <= 20
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 240.0
            and current_width >= 240.0
            and 0.0 <= vertical_gap <= 220.0
            and current_y0 >= previous_y0
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_x0 - current_x0 >= 120.0
            and previous_width >= 220.0
            and current_width <= 180.0
            and 0.0 <= vertical_gap <= 64.0
            and current_y0 >= previous_y1
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_y0 - 24.0 <= current_y0 <= previous_y1 + 4.0
        ):
            return True
        if not previous_has_terminal and current_continues and _looks_like_same_page_column_continuation(
            previous_x0,
            previous_y0,
            previous_y1,
            current_x0,
            current_y0,
        ):
            return True
        if (
            not previous_has_terminal
            and current_continues
            and previous_text.rstrip().endswith("-")
            and current_x0 >= previous_x0 + 80.0
            and current_y0 + 24.0 < previous_y1
            and current_y0 <= previous_y0 + 16.0
        ):
            return True
        if current_y0 < previous_y0 - 24.0:
            return False
        if vertical_gap > 18:
            return False
        if current_y0 <= previous_y1 + 2 and current_y0 >= previous_y0 - 2:
            return True
        if (previous_word_count <= 3 or current_word_count <= 3) and 0.0 <= vertical_gap <= 14.0:
            return True
    elif current_page == previous_page + 1:
        if previous_has_terminal:
            return False
        if current_continues and current_y0 <= 140:
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_word_count >= 20
            and current_word_count >= 8
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 500.0
            and current_width >= 500.0
        ):
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_word_count >= 12
            and current_word_count <= 16
            and previous_width >= 220.0
            and current_width >= 220.0
            and current_x0 + 80.0 <= previous_x0
        ):
            return True
        if (
            current_continues
            and previous_word_count >= 20
            and previous_width >= 220.0
            and current_width >= 220.0
            and current_y0 <= 240.0
        ):
            return True
        if (
            current_continues
            and current_text[:1].islower()
            and previous_text.rstrip().endswith("and")
            and previous_word_count >= 20
            and current_word_count >= 8
            and abs(current_x0 - previous_x0) <= 24.0
            and previous_width >= 400.0
            and current_width >= 400.0
            and current_y0 <= 360.0
        ):
            return True
        if current_y0 > 120:
            return False
    else:
        return False

    if current_page == previous_page and abs(current_x0 - previous_x0) > 24:
        return False

    current_starts_sentence = _starts_like_sentence(current_text)
    if previous_has_terminal and current_starts_sentence and current_x0 >= previous_x0 - 2:
        return False
    return True


def _merge_paragraph_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def _copy_record(source: dict[str, Any]) -> dict[str, Any]:
        copied = dict(source)
        copied["source_spans"] = list(_block_source_spans(source))
        copied["meta"] = dict(source.get("meta", {}))
        return copied

    def _is_paragraph_merge_interruption(record: dict[str, Any]) -> bool:
        if str(record.get("type", "")) != "caption":
            return False
        text = _clean_text(str(record.get("text", "")))
        return bool(text) and (
            TABLE_CAPTION_RE.match(text) is not None
            or text.lower().startswith("figure ")
        )

    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    pending_interruptions: list[dict[str, Any]] = []

    index = 0
    while index < len(records):
        record = records[index]
        if current is None:
            current = _copy_record(record)
            index += 1
            continue

        if _should_merge_paragraph_records(current, record):
            current["text"] = _clean_text(f"{current.get('text', '')} {record.get('text', '')}")
            current["source_spans"].extend(_block_source_spans(record))
            current["meta"]["source_record_ids"] = [
                *current["meta"].get("source_record_ids", [str(current.get("id", ""))]),
                str(record.get("id", "")),
            ]
            index += 1
            continue

        if (
            _is_paragraph_merge_interruption(record)
            and index + 1 < len(records)
            and _should_merge_paragraph_records(current, records[index + 1])
        ):
            pending_interruptions.append(_copy_record(record))
            index += 1
            continue

        merged.append(current)
        merged.extend(pending_interruptions)
        pending_interruptions = []
        current = _copy_record(record)
        index += 1

    if current is not None:
        merged.append(current)
    merged.extend(pending_interruptions)
    return merged


def _paragraph_block_text(block: dict[str, Any]) -> str:
    if str(block.get("type", "")) != "paragraph":
        return ""
    spans = block.get("content", {}).get("spans", [])
    parts: list[str] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        kind = str(span.get("kind", ""))
        if kind == "text":
            parts.append(str(span.get("text", "")))
        elif kind == "inline_math_ref":
            parts.append("[M]")
    return _strip_known_running_header_text("".join(parts))


def _paragraph_block_record(block: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": str(block.get("type", "")),
        "text": _paragraph_block_text(block),
        "source_spans": list(block.get("source_spans", [])),
        "meta": {},
    }


def _merge_paragraph_block_spans(
    previous_spans: list[dict[str, Any]],
    current_spans: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = [dict(span) for span in previous_spans]
    if merged and current_spans:
        last = merged[-1]
        needs_space = True
        if isinstance(last, dict) and last.get("kind") == "text" and str(last.get("text", "")).endswith((" ", "\n", "\t")):
            needs_space = False
        if needs_space:
            merged.append({"kind": "text", "text": " "})
    merged.extend(dict(span) for span in current_spans)
    return merged


def _merge_paragraph_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    merged_away_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        merged_block_ids: list[str] = []
        previous_block_id: str | None = None
        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in merged_away_ids:
                continue
            if previous_block_id is not None:
                previous_block = block_by_id.get(previous_block_id)
                if previous_block and _should_merge_paragraph_records(
                    _paragraph_block_record(previous_block),
                    _paragraph_block_record(block),
                ):
                    previous_spans = list(previous_block.get("content", {}).get("spans", []))
                    current_spans = list(block.get("content", {}).get("spans", []))
                    previous_block["content"] = {
                        "spans": _merge_paragraph_block_spans(previous_spans, current_spans)
                    }
                    previous_block["source_spans"] = [
                        *list(previous_block.get("source_spans", [])),
                        *list(block.get("source_spans", [])),
                    ]
                    previous_block["alternates"] = [
                        *list(previous_block.get("alternates", [])),
                        *list(block.get("alternates", [])),
                    ]
                    merged_away_ids.add(block_key)
                    continue

            merged_block_ids.append(block_key)
            block_type = str(block.get("type", ""))
            if block_type == "paragraph":
                previous_block_id = block_key
            elif block_type != "footnote":
                previous_block_id = None

        updated_section["block_ids"] = merged_block_ids
        updated_sections.append(updated_section)

    merged_blocks = [block for block in blocks if str(block.get("id", "")) not in merged_away_ids]
    return merged_blocks, updated_sections


def _is_footnote_like_paragraph_block(block: dict[str, Any]) -> bool:
    if str(block.get("type", "")) != "paragraph":
        return False
    text = _paragraph_block_text(block)
    if not text:
        return False
    bbox = (_block_source_spans(block)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 0.0))
    height = float(bbox.get("height", 0.0))
    if text.startswith(("*", "†", "‡")) and y0 >= 620.0 and 0.0 < height <= 120.0:
        return True
    return False


def _looks_like_footnote_continuation_block(
    footnote_block: dict[str, Any],
    block: dict[str, Any],
) -> bool:
    if str(block.get("type", "")) != "paragraph":
        return False
    text = _paragraph_block_text(block)
    if not text:
        return False
    footnote_spans = list(_block_source_spans(footnote_block))
    footnote_span = (footnote_spans[:1] or [{}])[0]
    current_span = (_block_source_spans(block)[:1] or [{}])[0]
    footnote_page = int(footnote_span.get("page", footnote_block.get("page", 0)) or 0)
    current_page = int(current_span.get("page", block.get("page", 0)) or 0)
    if current_page != footnote_page:
        return False
    footnote_bboxes = [span.get("bbox", {}) for span in footnote_spans if span.get("bbox")]
    footnote_bbox = footnote_span.get("bbox", {})
    current_bbox = current_span.get("bbox", {})
    footnote_x0 = min(float(bbox.get("x0", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("x0", 0.0))
    footnote_y0 = min(float(bbox.get("y0", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("y0", 0.0))
    footnote_y1 = max(float(bbox.get("y1", 0.0)) for bbox in footnote_bboxes) if footnote_bboxes else float(footnote_bbox.get("y1", 0.0))
    current_x0 = float(current_bbox.get("x0", 0.0))
    current_y0 = float(current_bbox.get("y0", 0.0))
    current_width = float(current_bbox.get("width", 0.0))
    current_height = float(current_bbox.get("height", 0.0))
    words = SHORT_WORD_RE.findall(text)
    if abs(current_x0 - footnote_x0) > 40.0:
        return False
    if current_y0 + 4.0 < footnote_y0:
        return False
    if current_y0 > footnote_y1 + 32.0:
        return False
    if len(words) <= 6:
        return True
    if current_width <= 140.0 and current_height <= 14.0:
        return True
    return not _starts_like_sentence(text)


def _merge_footnote_block_spans(
    previous_spans: list[dict[str, Any]],
    current_spans: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = [dict(span) for span in previous_spans]
    if merged and current_spans:
        last = merged[-1]
        needs_space = True
        if isinstance(last, dict) and last.get("kind") == "text" and str(last.get("text", "")).endswith((" ", "\n", "\t")):
            needs_space = False
        if needs_space:
            merged.append({"kind": "text", "text": " "})
    merged.extend(dict(span) for span in current_spans)
    return merged


def _normalize_footnote_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    merged_away_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        normalized_block_ids: list[str] = []
        active_footnote_id: str | None = None

        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in merged_away_ids:
                continue

            if _is_footnote_like_paragraph_block(block):
                block["type"] = "footnote"
            elif active_footnote_id is not None:
                active_footnote = block_by_id.get(active_footnote_id)
                if active_footnote and _looks_like_footnote_continuation_block(active_footnote, block):
                    block["type"] = "footnote"

            if str(block.get("type", "")) == "footnote":
                if active_footnote_id is not None:
                    active_footnote = block_by_id.get(active_footnote_id)
                    if active_footnote:
                        previous_spans = list(active_footnote.get("content", {}).get("spans", []))
                        current_spans = list(block.get("content", {}).get("spans", []))
                        active_footnote["content"] = {
                            "spans": _merge_footnote_block_spans(previous_spans, current_spans)
                        }
                        active_footnote["source_spans"] = [
                            *list(active_footnote.get("source_spans", [])),
                            *list(block.get("source_spans", [])),
                        ]
                        active_footnote["alternates"] = [
                            *list(active_footnote.get("alternates", [])),
                            *list(block.get("alternates", [])),
                        ]
                        merged_away_ids.add(block_key)
                        continue
                normalized_block_ids.append(block_key)
                active_footnote_id = block_key
                continue

            normalized_block_ids.append(block_key)
            active_footnote_id = None

        updated_section["block_ids"] = normalized_block_ids
        updated_sections.append(updated_section)

    normalized_blocks = [block for block in blocks if str(block.get("id", "")) not in merged_away_ids]
    return normalized_blocks, updated_sections


def _is_running_header_candidate_block(block: dict[str, Any]) -> bool:
    if str(block.get("type", "")) != "paragraph":
        return False
    text = _paragraph_block_text(block)
    if not text or not RUNNING_HEADER_TEXT_RE.fullmatch(text):
        return False
    words = SHORT_WORD_RE.findall(text)
    if not (1 <= len(words) <= 3):
        return False
    bbox = (_block_source_spans(block)[:1] or [{}])[0].get("bbox", {})
    y0 = float(bbox.get("y0", 999.0))
    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))
    return y0 <= 50.0 and width <= 120.0 and 0.0 < height <= 18.0


def _trim_trailing_text_suffix(
    spans: list[dict[str, Any]],
    suffix: str,
) -> list[dict[str, Any]]:
    if not suffix:
        return [dict(span) for span in spans]
    updated = [dict(span) for span in spans]
    suffix_pattern = re.compile(rf"(?:\s+)?{re.escape(suffix)}\s*$")
    for index in range(len(updated) - 1, -1, -1):
        span = updated[index]
        if str(span.get("kind", "")) != "text":
            continue
        text = str(span.get("text", ""))
        if not compact_text(text):
            continue
        trimmed = suffix_pattern.sub("", text)
        if trimmed == text:
            continue
        span["text"] = trimmed
        updated[index] = span
        break
    while updated and str(updated[-1].get("kind", "")) == "text" and not compact_text(str(updated[-1].get("text", ""))):
        updated.pop()
    return updated


def _suppress_running_header_blocks(
    blocks: list[dict[str, Any]],
    sections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not blocks or not sections:
        return blocks, sections

    header_counts: dict[str, int] = {}
    for block in blocks:
        if not _is_running_header_candidate_block(block):
            continue
        text = _paragraph_block_text(block)
        header_counts[text] = header_counts.get(text, 0) + 1
    running_headers = {text for text, count in header_counts.items() if count >= 3}
    if not running_headers:
        return blocks, sections

    block_by_id = {str(block.get("id", "")): block for block in blocks}
    removed_ids: set[str] = set()
    updated_sections: list[dict[str, Any]] = []

    for section in sections:
        updated_section = dict(section)
        kept_block_ids: list[str] = []
        for block_id in section.get("block_ids", []):
            block_key = str(block_id)
            block = block_by_id.get(block_key)
            if not block or block_key in removed_ids:
                continue

            if _is_running_header_candidate_block(block) and _paragraph_block_text(block) in running_headers:
                removed_ids.add(block_key)
                continue

            if str(block.get("type", "")) == "paragraph":
                text = _paragraph_block_text(block)
                matched_header = next(
                    (
                        header
                        for header in sorted(running_headers, key=len, reverse=True)
                        if text.endswith(header)
                    ),
                    None,
                )
                if matched_header:
                    source_spans = list(block.get("source_spans", []))
                    header_like_spans = [
                        span
                        for span in source_spans
                        if float(span.get("bbox", {}).get("y0", 999.0)) <= 50.0
                        and float(span.get("bbox", {}).get("width", 0.0)) <= 120.0
                        and float(span.get("bbox", {}).get("height", 0.0)) <= 18.0
                    ]
                    if header_like_spans:
                        updated_block = dict(block)
                        updated_block["content"] = {
                            "spans": _trim_trailing_text_suffix(
                                list(block.get("content", {}).get("spans", [])),
                                matched_header,
                            )
                        }
                        updated_block["source_spans"] = [
                            span
                            for span in source_spans
                            if span not in header_like_spans
                        ]
                        block_by_id[block_key] = updated_block
                        block = updated_block

            kept_block_ids.append(block_key)

        updated_section["block_ids"] = kept_block_ids
        updated_sections.append(updated_section)

    filtered_blocks = [block_by_id[str(block.get("id", ""))] for block in blocks if str(block.get("id", "")) not in removed_ids]
    return filtered_blocks, updated_sections


def _should_merge_code_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    if previous.get("type") != "code" or current.get("type") != "code":
        return False

    previous_span = (_block_source_spans(previous)[-1:] or [{}])[0]
    current_span = (_block_source_spans(current)[:1] or [{}])[0]
    previous_page = int(previous_span.get("page", previous.get("page", 0)) or 0)
    current_page = int(current_span.get("page", current.get("page", 0)) or 0)
    if current_page != previous_page:
        return False

    previous_bbox = previous_span.get("bbox", {})
    current_bbox = current_span.get("bbox", {})
    previous_x0 = float(previous_bbox.get("x0", 0.0))
    current_x0 = float(current_bbox.get("x0", 0.0))
    previous_y1 = float(previous_bbox.get("y1", 0.0))
    current_y0 = float(current_bbox.get("y0", 0.0))
    vertical_gap = current_y0 - previous_y1

    if abs(current_x0 - previous_x0) > 36.0:
        return False
    if vertical_gap < -8.0 or vertical_gap > 36.0:
        return False
    return True


def _merge_code_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for record in records:
        if current is None:
            current = dict(record)
            current["source_spans"] = list(_block_source_spans(record))
            current["meta"] = dict(record.get("meta", {}))
            continue

        if _should_merge_code_records(current, record):
            current_text = _clean_text(str(current.get("text", "")))
            next_text = _clean_text(str(record.get("text", "")))
            joiner = " ;; " if current_text and next_text else ""
            current["text"] = f"{current_text}{joiner}{next_text}".strip()
            current["source_spans"].extend(_block_source_spans(record))
            current["meta"]["source_record_ids"] = [
                *current["meta"].get("source_record_ids", [str(current.get("id", ""))]),
                str(record.get("id", "")),
            ]
            continue

        merged.append(current)
        current = dict(record)
        current["source_spans"] = list(_block_source_spans(record))
        current["meta"] = dict(record.get("meta", {}))

    if current is not None:
        merged.append(current)
    return merged


def _list_item_marker(text: str) -> tuple[str | None, bool, str]:
    cleaned = _clean_text(text)
    marker_match = re.match(r"^(?P<marker>(?:[-*•]+|\d+[.)]|[A-Za-z][.)]))\s+(?P<body>.+)$", cleaned)
    if not marker_match:
        return None, False, cleaned
    marker = marker_match.group("marker")
    body = _clean_text(marker_match.group("body"))
    ordered = bool(re.match(r"^(?:\d+[.)]|[A-Za-z][.)])$", marker))
    return marker, ordered, body


def _split_code_lines(text: str) -> list[str]:
    normalized = text.replace("```", " ")
    pieces = re.split(r";;\s*|\n+", normalized)
    return [line.strip() for line in pieces if line.strip()]


def _looks_like_real_code_record(text: str) -> bool:
    normalized = _clean_text(text)
    lowered = normalized.lower()
    if lowered.startswith(("struct ", "typedef ", "for (", "while (", "if (", "q =", "v 0 =", "output ")):
        return True
    if any(
        token in lowered
        for token in (
            "project boundary curves",
            "project_boundary_curves",
            "partition face",
            "partition_face",
            "ray intersection count",
            "ray_intersection_count",
            "random face",
            "for each face",
            "output v",
        )
    ):
        return True
    if "/*" in normalized and "*/" in normalized:
        return True
    if normalized.count(";;") >= 2:
        code_tokens = sum(
            token in lowered
            for token in (
                "double ",
                "int ",
                "float ",
                "char ",
                " push(",
                " pop(",
                " else ",
                " if (",
                " for (",
                "return ",
            )
        )
        if code_tokens >= 1:
            return True
    if any(token in normalized for token in ("{", "}", "==", "&&", "||", "->")) and ";" in normalized:
        return True
    if re.search(r"\b(?:[A-Za-z_]{3,}[A-Za-z0-9_]*|[A-Za-z_]+_[A-Za-z0-9_]*)\s*\(", normalized) and ";" in normalized:
        return True
    return False


def _rect_intersection_area(a: dict[str, Any], b: dict[str, Any]) -> float:
    x0 = max(float(a.get("x0", 0.0)), float(b.get("x0", 0.0)))
    y0 = max(float(a.get("y0", 0.0)), float(b.get("y0", 0.0)))
    x1 = min(float(a.get("x1", 0.0)), float(b.get("x1", 0.0)))
    y1 = min(float(a.get("y1", 0.0)), float(b.get("y1", 0.0)))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _rect_area(rect: dict[str, Any]) -> float:
    return max(float(rect.get("width", 0.0)) * float(rect.get("height", 0.0)), 1.0)


def _external_math_by_page(entries: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for entry in entries:
        for span in entry.get("source_spans", []):
            page = int(span.get("page", 0) or 0)
            if page <= 0:
                continue
            grouped.setdefault(page, []).append(entry)
            break
    return grouped


def _match_external_math_entry(
    record: dict[str, Any],
    external_math_by_page: dict[int, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    source_span = (_block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    record_bbox = source_span.get("bbox", {})
    record_text = _clean_text(str(record.get("text", "")))
    if not page or not record_bbox:
        return None

    candidates = external_math_by_page.get(page, [])
    if not candidates:
        return None

    record_area = _rect_area(record_bbox)
    best_index: int | None = None
    best_score = 0.0
    for index, entry in enumerate(candidates):
        if entry.get("kind") not in {"display", "group"}:
            continue
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        if not entry_bbox:
            continue
        overlap = _rect_intersection_area(record_bbox, entry_bbox)
        if overlap <= 0.0:
            continue
        entry_area = _rect_area(entry_bbox)
        overlap_score = overlap / min(record_area, entry_area)
        score = overlap_score
        entry_text = _clean_text(str(entry.get("display_latex", "")))
        if entry_text and entry_text == record_text:
            score += 1.0
        elif entry_text and record_text and (entry_text in record_text or record_text in entry_text):
            score += 0.2
        if score > best_score:
            best_score = score
            best_index = index

    if best_index is None or best_score < 0.35:
        return None
    return external_math_by_page[page].pop(best_index)


def _overlapping_external_math_entries(
    record: dict[str, Any],
    external_math_by_page: dict[int, list[dict[str, Any]]],
    *,
    minimum_score: float = 0.75,
) -> list[dict[str, Any]]:
    source_span = (_block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    record_bbox = source_span.get("bbox", {})
    if not page or not record_bbox:
        return []

    record_area = _rect_area(record_bbox)
    matches: list[tuple[float, dict[str, Any]]] = []
    for entry in external_math_by_page.get(page, []):
        if entry.get("kind") not in {"display", "group"}:
            continue
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        if not entry_bbox:
            continue
        overlap = _rect_intersection_area(record_bbox, entry_bbox)
        if overlap <= 0.0:
            continue
        entry_area = _rect_area(entry_bbox)
        score = overlap / min(record_area, entry_area)
        if score >= minimum_score:
            matches.append((score, entry))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in matches]


def _trim_embedded_display_math_from_paragraph(
    text: str,
    record: dict[str, Any],
    overlapping_math: list[dict[str, Any]],
) -> str:
    if overlapping_math:
        cue_match = DISPLAY_MATH_PROSE_CUE_RE.search(text)
        if cue_match:
            prefix = text[: cue_match.start()].strip(" ;:")
            if prefix and len(prefix) <= 240 and (_mathish_ratio(prefix) >= 0.25 or (prefix.count("=") >= 1 and _strong_operator_count(prefix) >= 1)):
                text = text[cue_match.start() :].lstrip(" ;:")

    resume = DISPLAY_MATH_RESUME_RE.search(text)
    if resume and resume.start() > 10:
        prefix = text[: resume.start()].strip()
        if prefix and len(prefix) <= 220 and (_mathish_ratio(prefix) >= 0.1 or prefix.startswith("$") or "=" in prefix or "^" in prefix):
            text = text[resume.start() :].lstrip()

    if not overlapping_math:
        return _clean_text(text)

    trimmed = text
    source_span = (_block_source_spans(record)[:1] or [{}])[0]
    bbox = source_span.get("bbox", {})
    record_height = float(bbox.get("height", 0.0))
    record_y0 = float(bbox.get("y0", 0.0))
    cue_phrases = (
        "as follows:",
        "such that",
        "given by",
        "equations become",
        "equation in this case is",
        "with respect to s and t .",
        "corresponding to the eigendecomposition of",
        "determinant",
    )

    for entry in overlapping_math:
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        entry_y0 = float(entry_bbox.get("y0", 0.0))
        entry_y1 = float(entry_bbox.get("y1", 0.0))
        starts_low = record_height > 0 and entry_y0 >= record_y0 + record_height * 0.45
        starts_high = record_height > 0 and entry_y1 <= record_y0 + record_height * 0.55

        cue_matches = [trimmed.lower().rfind(cue) for cue in cue_phrases]
        cue_index = max(cue_matches)
        if cue_index >= 0:
            matched_cue = max((cue for cue in cue_phrases if trimmed.lower().rfind(cue) == cue_index), key=len)
            cue_end = cue_index + len(matched_cue)
            suffix = trimmed[cue_end:].strip()
            if suffix and (len(suffix) >= 20 and _mathish_ratio(suffix) >= 0.15):
                trimmed = trimmed[:cue_end].rstrip()
                continue

        if starts_low:
            match = DISPLAY_MATH_START_RE.search(trimmed)
            if match and match.start() >= 80 and _mathish_ratio(trimmed[match.start() :]) >= 0.35:
                trimmed = trimmed[: match.start()].rstrip()
                continue

        if starts_high:
            resume = DISPLAY_MATH_RESUME_RE.search(trimmed)
            prefix = trimmed[: resume.start()].strip() if resume else ""
            if (
                resume
                and resume.start() > 10
                and len(prefix) <= 220
                and (_mathish_ratio(prefix) >= 0.1 or "=" in prefix or "^" in prefix)
            ):
                trimmed = trimmed[resume.start() :].lstrip()

    return _clean_text(trimmed)


def _looks_like_display_math_echo(
    record: dict[str, Any],
    text: str,
    overlapping_math: list[dict[str, Any]],
) -> bool:
    if not overlapping_math:
        return False
    cleaned = _clean_text(text)
    if not cleaned:
        return False
    strong_operator_count = _strong_operator_count(cleaned)
    if looks_like_prose_paragraph(cleaned) and not (_mathish_ratio(cleaned) >= 0.3 and strong_operator_count >= 2):
        return False
    if looks_like_prose_math_fragment(cleaned):
        return False
    word_count = _word_count(cleaned)
    if word_count > 40:
        return False
    tokens = [token.strip(".,;:()[]{}") for token in cleaned.split() if token.strip(".,;:()[]{}")]
    prose_token_count = sum(1 for token in tokens if re.fullmatch(r"[A-Za-z]{3,}", token))
    compact_token_count = sum(1 for token in tokens if re.fullmatch(r"[\dA-Za-z∂πΠΣΔΩα-ωΑ-Ω]+", token))
    digit_count = sum(char.isdigit() for char in cleaned)
    source_span = (_block_source_spans(record)[:1] or [{}])[0]
    bbox = source_span.get("bbox", {})
    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))
    if prose_token_count == 0 and compact_token_count >= max(4, len(tokens) - 1):
        if width and width <= 160.0:
            return True
        if height and height <= 8.0 and digit_count >= 6:
            return True
        if any(symbol in cleaned for symbol in ("∂", "π", "Σ", "Δ", "Ω")):
            return True
    if cleaned.count("=") >= 1 and strong_operator_count >= 2:
        return True
    if word_count <= 24 and strong_operator_count >= 1 and (cleaned.count(";;") >= 2 or cleaned.count("(") >= 2):
        return True
    if _mathish_ratio(cleaned) >= 0.22 and strong_operator_count >= 1:
        return True
    return False


def _looks_like_leading_display_math_echo(text: str) -> bool:
    cleaned = _clean_text(text).lstrip(" ;:")
    if not cleaned:
        return False
    cue_match = DISPLAY_MATH_PROSE_CUE_RE.search(cleaned)
    prefix = cleaned[: cue_match.start()].strip() if cue_match else cleaned
    if not prefix or len(prefix) > 240:
        return False
    if prefix.count("=") < 1:
        return False
    return _mathish_ratio(prefix) >= 0.25 or _strong_operator_count(prefix) >= 1


def _mark_records_with_external_math_overlap(
    records: list[dict[str, Any]],
    external_math_overlap_by_page: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if not external_math_overlap_by_page:
        return records

    marked: list[dict[str, Any]] = []
    for record in records:
        overlaps = _overlapping_external_math_entries(record, external_math_overlap_by_page)
        if not overlaps:
            marked.append(record)
            continue
        updated = dict(record)
        meta = dict(updated.get("meta", {}))
        meta["external_display_math_overlap_count"] = len(overlaps)
        updated["meta"] = meta
        marked.append(updated)
    return marked


def _merge_native_and_external_layout(native_layout: dict[str, Any], external_layout: dict[str, Any]) -> dict[str, Any]:
    native_blocks: list[LayoutBlock] = list(native_layout.get("blocks", []))
    external_blocks: list[LayoutBlock] = list(external_layout.get("blocks", []))
    external_pages = {int(block.page) for block in external_blocks}
    merged_blocks = [block for block in native_blocks if int(block.page) not in external_pages]
    merged_blocks.extend(external_blocks)
    merged_blocks.sort(key=lambda block: (int(block.page), int(block.order), str(block.id)))
    return {
        "pdf_path": external_layout.get("pdf_path") or native_layout["pdf_path"],
        "page_count": external_layout.get("page_count") or native_layout["page_count"],
        "page_sizes_pt": external_layout.get("page_sizes_pt") or native_layout["page_sizes_pt"],
        "blocks": merged_blocks,
    }


def _is_figure_debris(record: dict[str, Any], figures_by_page: dict[int, list[dict[str, Any]]]) -> bool:
    if record.get("type") not in {"paragraph", "heading"}:
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text:
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and (
        isinstance(meta.get("external_math_entry"), dict) or meta.get("source_math_entry_id")
    ):
        return False
    source_span = (_block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    bbox = source_span.get("bbox", {})
    figures = figures_by_page.get(page, [])
    if not figures:
        return False

    if text.startswith("Figure"):
        return True
    words = SHORT_WORD_RE.findall(text)
    if DIAGRAM_DECISION_RE.match(text):
        return True
    if (
        text.count("_") >= 2
        and len(words) <= 24
        and not TERMINAL_PUNCTUATION_RE.search(text)
    ):
        return True
    if (
        len(words) <= 28
        and not TERMINAL_PUNCTUATION_RE.search(text)
        and (DIAGRAM_QUERY_RE.match(text) or DIAGRAM_ACTION_RE.match(text))
    ):
        return True

    area = max(float(bbox.get("width", 0.0)) * float(bbox.get("height", 0.0)), 1.0)
    word_count = len(words)
    short_label_like = (
        word_count <= 8
        and float(bbox.get("height", 0.0)) <= 12.0
        and TERMINAL_PUNCTUATION_RE.search(text) is None
    )
    center_x = (float(bbox.get("x0", 0.0)) + float(bbox.get("x1", 0.0))) / 2.0
    center_y = (float(bbox.get("y0", 0.0)) + float(bbox.get("y1", 0.0))) / 2.0
    for figure in figures:
        figure_bbox = figure.get("bbox", {})
        overlap = _rect_intersection_area(bbox, figure_bbox)
        if overlap / area >= 0.7:
            return True
        if word_count <= 4 and overlap / area >= 0.2:
            return True
        if short_label_like and overlap / area >= 0.15:
            return True
        if (
            (word_count <= 4 or short_label_like)
            and float(figure_bbox.get("x0", 0.0)) <= center_x <= float(figure_bbox.get("x1", 0.0))
            and float(figure_bbox.get("y0", 0.0)) <= center_y <= float(figure_bbox.get("y1", 0.0))
        ):
            return True
    return False


def _is_short_ocr_fragment(record: dict[str, Any]) -> bool:
    if record.get("type") != "paragraph":
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and meta.get("external_math_entry"):
        return False
    text = _clean_text(str(record.get("text", "")))
    if not text:
        return True
    spans = _block_source_spans(record)
    lowered = text.lower()
    span_widths = [float(span.get("bbox", {}).get("width", 0.0)) for span in spans]
    if text in {"*", "∗"}:
        return True
    if _looks_like_browser_ui_scrap(text):
        return True
    if _looks_like_quoted_identifier_fragment(text):
        return True
    if _looks_like_glyph_noise_cloud(text):
        return True
    if lowered in {"end if", "end while", "end for", "else"} and len(SHORT_WORD_RE.findall(text)) <= 2:
        return True
    if any(float(span.get("bbox", {}).get("width", 0.0)) <= 1.0 for span in spans) and text.lower().startswith("negationslash"):
        return True
    if (
        len(spans) >= 3
        and span_widths
        and max(span_widths) <= 8.0
        and lowered.count(" are in ") >= 2
        and lowered.count(".") >= 2
    ):
        return True
    if _looks_like_vertical_label_cloud(text, spans) or _looks_like_table_marker_cloud(text, spans):
        return True
    if isinstance(meta, dict) and meta.get("forced_math_kind"):
        raw_tokens = text.split()
        if len(raw_tokens) >= 8:
            label_like_count = 0
            for token in raw_tokens:
                compact = token.strip(".,;:")
                if LABEL_CLOUD_TOKEN_RE.fullmatch(compact):
                    label_like_count += 1
                    continue
                if len(compact) <= 4 and any(ord(char) > 127 for char in compact):
                    label_like_count += 1
            strong_operator_count = _strong_operator_count(text)
            if label_like_count / max(len(raw_tokens), 1) >= 0.7 and strong_operator_count <= 1:
                return True
    if len(text) <= 12 and SHORT_OCR_NOISE_RE.match(text):
        return True
    words = SHORT_WORD_RE.findall(text)
    lowercase_words = sum(1 for word in words if word.islower())
    if lowered in {"where", "where:"}:
        return False
    span_heights = [float(span.get("bbox", {}).get("height", 0.0)) for span in spans]
    tiny_span_count = sum(1 for height in span_heights if 0.0 < height <= 4.5)
    if tiny_span_count >= max(3, len(span_heights) // 2 + len(span_heights) % 2):
        digit_count = sum(char.isdigit() for char in text)
        symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
        non_ascii_count = sum(ord(char) > 127 for char in text)
        titlecase_like = sum(1 for word in words if word[:1].isupper())
        if not any(token in text for token in ("=", "\\", "{", "}", "^", "_")):
            if digit_count >= 2 or text.count(":") >= 1 or non_ascii_count >= 1 or symbol_count >= 4:
                return True
            if titlecase_like >= max(4, lowercase_words + 3):
                return True
    bbox = (_block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))
    x0 = float(bbox.get("x0", 0.0))
    y0 = float(bbox.get("y0", 0.0))
    if y0 <= 40.0 and x0 <= 4.0:
        if text[:1] in {":", ";", ",", ".", "-"} and len(words) <= 40:
            return True
        if len(words) <= 18 and lowercase_words >= max(3, len(words) - 2) and not TERMINAL_PUNCTUATION_RE.search(text):
            return True
    if height and height <= 14.0:
        if len(words) <= 2 and width <= 120.0:
            return True
        if len(words) <= 3 and width <= 120.0 and lowercase_words >= max(2, len(words) - 1):
            return True
        if len(words) <= 4 and width <= 95.0:
            return True
        if len(words) <= 6 and width <= 70.0:
            return True
    if width <= 20.0 and len(words) <= 1 and height <= 28.0:
        return True
    if (
        height
        and height <= 8.0
        and width <= 120.0
        and len(words) <= 8
        and lowercase_words >= 2
        and TERMINAL_PUNCTUATION_RE.search(text) is None
    ):
        return True
    if height and height <= 10.0 and width <= 60.0 and len(words) <= 10 and lowercase_words >= max(3, len(words) - 2):
        return True
    if height and height <= 4.5:
        if len(words) <= 12:
            return True
        digit_count = sum(char.isdigit() for char in text)
        symbol_count = sum(not char.isalnum() and not char.isspace() for char in text)
        non_ascii_count = sum(ord(char) > 127 for char in text)
        titlecase_like = sum(1 for word in words if word[:1].isupper())
        if digit_count >= 2 or symbol_count >= 2 or non_ascii_count >= 1:
            return True
        if titlecase_like >= max(4, lowercase_words + 3):
            return True
    y_positions = [float(span.get("bbox", {}).get("y0", 0.0)) for span in spans if span.get("bbox")]
    if len(words) <= 6 and not TERMINAL_PUNCTUATION_RE.search(text):
        if len(y_positions) >= 2 and max(y_positions) - min(y_positions) >= 24.0 and lowercase_words >= max(2, len(words) - 1):
            return True
        if float(bbox.get("y0", 0.0)) <= 80.0 and lowercase_words >= max(2, len(words) - 1):
            return True
    if height and height <= 6.0 and len(words) <= 12 and lowercase_words >= max(3, len(words) - 2):
        return True
    if len(words) > 3 or len(text) > 24:
        return False
    if re.search(r"[A-Z][a-z]{2,}", text):
        return False
    if width and width > 80 and height < 30:
        return False
    return True


def _build_blocks_for_record(
    record: dict[str, Any],
    layout_by_id: dict[str, LayoutBlock],
    figures_by_label: dict[str, dict[str, Any]],
    external_math_by_page: dict[int, list[dict[str, Any]]],
    external_math_overlap_by_page: dict[int, list[dict[str, Any]]],
    references_section: bool,
    counters: dict[str, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    record = _clean_record(record)
    text = str(record.get("text", ""))
    analysis_text = _record_analysis_text(record)
    if not text:
        return [], [], []
    if _is_short_ocr_fragment(record):
        return [], [], []

    blocks: list[dict[str, Any]] = []
    math_entries: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    source_spans = _block_source_spans(record)

    if record.get("type") == "caption":
        label = caption_label(text)
        figure = figures_by_label.get(label or "")
        if figure is not None:
            block_id = f"blk-figure-{counters['block']:04d}"
            counters["block"] += 1
            blocks.append(
                {
                    "id": block_id,
                    "type": "figure_ref",
                    "content": {"figure_id": figure["id"]},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": default_review(risk="medium"),
                }
            )
        return blocks, math_entries, references

    if references_section or record.get("type") == "reference":
        reference = _make_reference_entry(record, counters["reference"])
        counters["reference"] += 1
        references.append(reference)
        block_id = f"blk-reference-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "reference",
                "content": {"reference_id": reference["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    if record.get("type") == "code" and _looks_like_real_code_record(text):
        code_lines = _split_code_lines(str(record.get("text", "")))
        if not code_lines:
            return blocks, math_entries, references
        block_id = f"blk-code-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "code",
                "content": {"lines": code_lines, "language": "text"},
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    list_marker, list_ordered, list_body = _list_item_marker(text)
    if record.get("type") == "list_item" or list_marker is not None:
        list_text = _normalize_paragraph_text(list_body if list_marker is not None else text)
        spans, inline_math_entries, next_index = split_inline_math(list_text, counters["inline_math"])
        spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
        spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
        spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
        spans = normalize_inline_math_spans(spans)
        counters["inline_math"] = next_index
        for entry in inline_math_entries:
            entry["source_spans"] = source_spans
        math_entries.extend(inline_math_entries)
        block_id = f"blk-list_item-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": "list_item",
                "content": {
                    "spans": spans,
                    "marker": list_marker,
                    "ordered": list_ordered,
                    "depth": 1,
                },
                "source_spans": source_spans,
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        return blocks, math_entries, references

    meta = record.get("meta", {})
    if isinstance(meta, dict) and isinstance(meta.get("external_math_entry"), dict):
        math_entry = dict(meta["external_math_entry"])
        math_entry["display_latex"] = _normalize_formula_display_text(str(math_entry.get("display_latex", "")))
        math_entry["source_spans"] = list(math_entry.get("source_spans") or source_spans)
        math_entry["review"] = review_for_math_entry(math_entry)
        math_kind = str(math_entry.get("kind", "display"))
        block_type = "equation_group_ref" if math_kind == "group" else "display_equation_ref"
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    prose_like_record = looks_like_prose_paragraph(text) or looks_like_prose_math_fragment(text)

    external_math_entry = None if prose_like_record else _match_external_math_entry(record, external_math_by_page)
    if external_math_entry is not None:
        math_entry = dict(external_math_entry)
        math_entry["display_latex"] = _normalize_formula_display_text(str(math_entry.get("display_latex", "")))
        math_entry["source_spans"] = list(math_entry.get("source_spans") or source_spans)
        math_entry["review"] = review_for_math_entry(math_entry)
        math_kind = str(math_entry.get("kind", "display"))
        block_type = "equation_group_ref" if math_kind == "group" else "display_equation_ref"
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    layout_block = layout_by_id.get(str(record.get("id", "")))
    forced_math_kind = str(record.get("meta", {}).get("forced_math_kind", "") or "")
    if forced_math_kind in {"display", "group"} and not prose_like_record:
        math_entry = build_block_math_entry(
            LayoutBlock(
                id=str(record.get("id", "")),
                page=int(record.get("page", 0)),
                order=int(record.get("group_index", 0)),
                text=analysis_text,
                role="paragraph",
                bbox=source_spans[0]["bbox"] if source_spans else {},
                engine=str(source_spans[0].get("engine", "native_pdf")) if source_spans else "native_pdf",
                meta={"line_count": len(source_spans)},
            ),
            forced_math_kind,
            counters["math"],
        )
        math_entry["display_latex"] = _normalize_formula_display_text(text)
        math_entry["source_spans"] = source_spans
        if forced_math_kind == "group":
            for item in math_entry.get("items", []):
                item["display_latex"] = _normalize_formula_display_text(str(item.get("display_latex", "")))
            block_type = "equation_group_ref"
        else:
            block_type = "display_equation_ref"
        math_entry["review"] = review_for_math_entry(math_entry)
        counters["math"] += 1
        math_entries.append(math_entry)
        block_id = f"blk-{block_type}-{counters['block']:04d}"
        counters["block"] += 1
        blocks.append(
            {
                "id": block_id,
                "type": block_type,
                "content": {"math_id": math_entry["id"]},
                "source_spans": source_spans,
                "alternates": [],
                "review": review_for_math_ref_block(math_entry),
            }
        )
        return blocks, math_entries, references

    if layout_block is not None:
        classified_kind = classify_math_block(replace(layout_block, text=analysis_text))
        if classified_kind == "algorithm":
            block_id = f"blk-algorithm-{counters['block']:04d}"
            counters["block"] += 1
            algorithm_lines = [line for line in re.split(r"\s{2,}|(?<=;)\s+", text) if line]
            blocks.append(
                {
                    "id": block_id,
                    "type": "algorithm",
                    "content": {"lines": algorithm_lines},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": review_for_algorithm_block_text(" ".join(algorithm_lines)),
                }
            )
            return blocks, math_entries, references

        math_kind = None if prose_like_record else classified_kind
        if math_kind in {"display", "group"}:
            math_entry = build_block_math_entry(layout_block, math_kind, counters["math"])
            math_entry["display_latex"] = _normalize_formula_display_text(text)
            math_entry["source_spans"] = source_spans
            if math_kind == "group":
                for item in math_entry.get("items", []):
                    item["display_latex"] = _normalize_formula_display_text(str(item.get("display_latex", "")))
                block_type = "equation_group_ref"
            else:
                block_type = "display_equation_ref"
            math_entry["review"] = review_for_math_entry(math_entry)
            counters["math"] += 1
            math_entries.append(math_entry)
            block_id = f"blk-{block_type}-{counters['block']:04d}"
            counters["block"] += 1
            blocks.append(
                {
                    "id": block_id,
                    "type": block_type,
                    "content": {"math_id": math_entry["id"]},
                    "source_spans": source_spans,
                    "alternates": [],
                    "review": review_for_math_ref_block(math_entry),
                }
            )
            return blocks, math_entries, references

    text = _normalize_paragraph_text(text)
    overlapping_math = _overlapping_external_math_entries(record, external_math_overlap_by_page)
    text = _trim_embedded_display_math_from_paragraph(text, record, overlapping_math)
    if _looks_like_display_math_echo(record, text, overlapping_math):
        return [], [], []
    spans, inline_math_entries, next_index = split_inline_math(text, counters["inline_math"])
    spans, inline_math_entries, next_index = repair_symbolic_ocr_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries, next_index = extract_general_inline_math_spans(spans, inline_math_entries, next_index)
    spans, inline_math_entries = merge_inline_math_relation_suffixes(spans, inline_math_entries)
    spans = normalize_inline_math_spans(spans)
    counters["inline_math"] = next_index
    for entry in inline_math_entries:
        entry["source_spans"] = source_spans
    math_entries.extend(inline_math_entries)
    block_id = f"blk-paragraph-{counters['block']:04d}"
    counters["block"] += 1
    blocks.append(
        {
            "id": block_id,
            "type": "paragraph",
            "content": {"spans": spans},
            "source_spans": source_spans,
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    )
    return blocks, math_entries, references


def reconcile_paper(
    paper_id: str,
    *,
    text_engine: str = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    layout_output: dict[str, Any] | None = None,
    figures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    native_layout = layout_output or extract_layout(paper_id)
    layout = native_layout
    external_layout_engine: str | None = None
    if use_external_layout:
        external_layout = load_external_layout(paper_id)
        if external_layout and external_layout.get("blocks"):
            layout = _merge_native_and_external_layout(native_layout, external_layout)
            external_layout_engine = str(external_layout.get("engine", "external_layout"))

    external_math_payload = load_external_math(paper_id) if use_external_math else None
    external_math_entries = list((external_math_payload or {}).get("entries", []))
    external_math_engine = str((external_math_payload or {}).get("engine", "")) or None
    external_math_overlap_page_map = _external_math_by_page(external_math_entries)
    mathpix_layout = load_mathpix_layout(paper_id) if use_external_math else None

    figures = figures or extract_figures(paper_id)
    figures = [
        {
            **figure,
            "caption": _normalize_figure_caption_text(str(figure.get("caption", ""))),
        }
        for figure in figures
    ]
    layout_blocks: list[LayoutBlock] = list(layout["blocks"])
    records, layout_by_id = _merge_layout_and_figure_records(layout_blocks, figures)
    records, injected_external_math_ids = _inject_external_math_records(records, layout_blocks, external_math_entries)
    external_math_entries = [entry for entry in external_math_entries if str(entry.get("id", "")) not in injected_external_math_ids]
    records = _mark_records_with_external_math_overlap(records, external_math_overlap_page_map)
    records = _repair_record_text_with_mathpix_hints(records, mathpix_layout)
    effective_text_engine = "native_pdf"
    if text_engine in {"pdftotext", "hybrid"} and pdftotext_available():
        records = _repair_record_text_with_pdftotext(records, extract_pdftotext_pages(paper_id), _page_height_map(layout))
        effective_text_engine = "native_pdf+pdftotext"
    records = _promote_heading_like_records(records)
    records = _merge_math_fragment_records(records)
    page_one_records = _page_one_front_matter_records(records, mathpix_layout)
    records = [record for record in records if not _is_title_page_metadata_record(record)]
    prelude, roots = build_section_tree(records)

    blocks: list[dict[str, Any]] = []
    front_matter, blocks, next_block_index, remaining_prelude = _build_front_matter(
        paper_id,
        prelude,
        page_one_records,
        blocks,
        1,
    )

    ordered_roots = _attach_orphan_numbered_roots(list(roots))
    if not remaining_prelude and front_matter.get("abstract_block_id"):
        trimmed_prelude, overflow_prelude = _split_late_prelude_for_missing_intro(prelude, ordered_roots)
        if overflow_prelude:
            front_matter, blocks, next_block_index, _ = _build_front_matter(
                paper_id,
                trimmed_prelude,
                page_one_records,
                [],
                1,
            )
            remaining_prelude = overflow_prelude
    if ordered_roots and _normalize_section_title(str(ordered_roots[0].title)) == "abstract":
        abstract_text, abstract_records = _leading_abstract_text(ordered_roots[0])
        if abstract_text:
            current_abstract_text = _front_block_text(blocks, front_matter.get("abstract_block_id"))
            if not front_matter.get("abstract_block_id"):
                abstract_block_id = f"blk-front-abstract-{next_block_index}"
                blocks.append(
                    {
                        "id": abstract_block_id,
                        "type": "paragraph",
                        "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                        "source_spans": [span for record in abstract_records for span in _block_source_spans(record)],
                        "alternates": [],
                        "review": default_review(risk="medium"),
                    }
                )
                front_matter["abstract_block_id"] = abstract_block_id
                next_block_index += 1
            elif _abstract_text_looks_like_metadata(current_abstract_text):
                for block in blocks:
                    if str(block.get("id", "")) != str(front_matter["abstract_block_id"]):
                        continue
                    block["content"] = {"spans": [{"kind": "text", "text": abstract_text}]}
                    block["source_spans"] = [span for record in abstract_records for span in _block_source_spans(record)]
                    break
        if front_matter.get("abstract_block_id"):
            ordered_roots = ordered_roots[1:]
    if remaining_prelude and (not ordered_roots or not str(ordered_roots[0].title).lower().endswith("introduction")):
        intro_node = SectionNode(
            title="Introduction",
            level=1,
            heading_id="synthetic-introduction",
            label=("1",) if ordered_roots and getattr(ordered_roots[0], "label", None) and ordered_roots[0].label[0] != "1" else None,
            records=remaining_prelude,
            children=[],
        )
        ordered_roots = [intro_node, *ordered_roots]

    figures_by_label = {
        (_figure_label_token(figure) or ""): figure
        for figure in figures
    }
    figures_by_page: dict[int, list[dict[str, Any]]] = {}
    for figure in figures:
        figures_by_page.setdefault(int(figure["page"]), []).append(figure)
    counters = {
        "block": next_block_index,
        "math": 1,
        "inline_math": 1,
        "reference": 1,
    }
    external_math_page_map = _external_math_by_page(external_math_entries)

    section_nodes = _flatten_sections(ordered_roots)
    if section_nodes and all(_normalize_section_title(str(node.title)) != "references" for node in section_nodes):
        body_records, trailing_reference_records = _split_trailing_reference_records(section_nodes[-1].records)
        if trailing_reference_records:
            section_nodes[-1].records = body_records
            section_nodes.append(
                SectionNode(
                    title="References",
                    level=1,
                    heading_id="synthetic-references",
                    records=trailing_reference_records,
                    children=[],
                )
            )
        else:
            body_records, harvested_reference_records = _extract_reference_records_from_tail_section(section_nodes[-1].records)
            if harvested_reference_records:
                section_nodes[-1].records = body_records
                section_nodes.append(
                    SectionNode(
                        title="References",
                        level=1,
                        heading_id="synthetic-tail-references",
                        records=harvested_reference_records,
                        children=[],
                    )
                )
            else:
                mathpix_reference_records = _reference_records_from_mathpix_layout(mathpix_layout)
                if mathpix_reference_records:
                    section_nodes.append(
                        SectionNode(
                            title="References",
                            level=1,
                            heading_id="synthetic-mathpix-references",
                            records=mathpix_reference_records,
                            children=[],
                        )
                    )
    sections: list[dict[str, Any]] = []
    all_references: list[dict[str, Any]] = []
    all_math: list[dict[str, Any]] = []

    section_ids = {_section_id(node, index + 1): node for index, node in enumerate(section_nodes)}
    for index, node in enumerate(section_nodes):
        section_id = _section_id(node, index + 1)
        section_title_key = _normalize_section_title(str(node.title))
        references_section = section_title_key == "references"
        section_block_ids: list[str] = []
        if references_section:
            section_records = _merge_reference_records(node.records)
        else:
            section_records = [
                record
                for record in node.records
                if not _is_figure_debris(record, figures_by_page)
                and not _looks_like_running_header_record(record)
                and not _looks_like_table_body_debris(record)
                and not _is_short_ocr_fragment(record)
            ]
            section_records = _suppress_embedded_table_headings(section_records)
            section_records = _merge_code_records(section_records)
            section_records = _merge_paragraph_records(section_records)
        for record in section_records:
            new_blocks, math_entries, references = _build_blocks_for_record(
                record,
                layout_by_id,
                figures_by_label,
                external_math_page_map,
                external_math_overlap_page_map,
                references_section,
                counters,
            )
            blocks.extend(new_blocks)
            all_math.extend(math_entries)
            all_references.extend(references)
            section_block_ids.extend(block["id"] for block in new_blocks)

        heading_record = next((record for record in records if str(record.get("id", "")) == str(node.heading_id)), None)
        sections.append(
            {
                "id": section_id,
                "label": ".".join(node.label) if getattr(node, "label", None) else None,
                "title": _clean_text(str(node.title)),
                "level": int(node.level),
                "block_ids": section_block_ids,
                "children": [_section_id(child, 0) for child in node.children],
                "source_spans": _block_source_spans(heading_record or {}),
            }
        )

    compiled_math = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(all_math))
    )
    blocks, compiled_math, sections = _suppress_graphic_display_math_blocks(
        blocks,
        compiled_math,
        sections,
        counters,
    )
    blocks, sections = _suppress_running_header_blocks(blocks, sections)
    blocks, sections = _normalize_footnote_blocks(blocks, sections)
    blocks, sections = _merge_paragraph_blocks(blocks, sections)
    compiled_math = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(compiled_math))
    )
    title = front_matter["title"]
    timestamp = _now_iso()
    layout_engine_name = external_layout_engine or "native_pdf"
    if external_math_engine:
        math_engine_name = f"{external_math_engine}+heuristic"
    else:
        math_engine_name = "heuristic"
    document = {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "title": title,
        "source": {
            "pdf_path": layout["pdf_path"],
            "page_count": int(layout["page_count"]),
            "page_sizes_pt": list(layout["page_sizes_pt"]),
        },
        "build": build_metadata_for_paper(
            paper_id,
            pdf_path=layout["pdf_path"],
            timestamp=timestamp,
            layout_engine=layout_engine_name,
            math_engine=math_engine_name,
            figure_engine="local",
            text_engine=effective_text_engine,
            use_external_layout=bool(external_layout_engine),
            use_external_math=bool(external_math_engine),
        ),
        "front_matter": front_matter,
        "styles": {
            "document_style": {},
            "category_styles": {},
            "block_styles": {},
        },
        "sections": sections,
        "blocks": blocks,
        "math": compiled_math,
        "figures": figures,
        "references": all_references,
    }
    document = apply_document_policy(document)
    document["math"] = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(list(document.get("math", []))))
    )
    return document
