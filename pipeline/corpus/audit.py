from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from pipeline.corpus.metadata import discover_paper_pdf_paths, paper_id_from_pdf_path
from pipeline.corpus_layout import current_layout, display_path
from pipeline.math.diagnostics import diagnose_formula_entry, summarize_formula_diagnostics
from pipeline.math.review_policy import math_text_looks_suspicious
from pipeline.output.validation import CanonicalValidationError, validate_canonical
from pipeline.policies.abstract_quality import abstract_quality_flags
from pipeline.policies.completeness import (
    block_text as completeness_block_text,
    document_expects_figures,
    document_expects_references,
)
from pipeline.text.headings import clean_heading_title, compact_text


SENTENCE_END_RE = re.compile(r'[.!?]["\')\]]?$')
CLAUSE_END_RE = re.compile(r'[:;]["\')\]]?$')
LETTER_RE = re.compile(r"[A-Za-z]")
WORD_RE = re.compile(r"[A-Za-z0-9]+")
NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")
SINGLE_LETTER_RUN_RE = re.compile(r"(?:\b[A-Za-z]\b(?:\s+|$)){4,}")
LOWERCASE_START_RE = re.compile(r"^[a-z]")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _review_status(value: dict[str, Any]) -> str:
    review = value.get("review")
    if isinstance(review, dict):
        return str(review.get("status", ""))
    return ""


def _review_risk(value: dict[str, Any]) -> str:
    review = value.get("review")
    if isinstance(review, dict):
        return str(review.get("risk", ""))
    return ""


def _conversion_status(value: dict[str, Any]) -> str:
    conversion = value.get("conversion")
    if isinstance(conversion, dict):
        return str(conversion.get("status", "unconverted"))
    return "unconverted"


def _formula_category(value: dict[str, Any]) -> str:
    classification = value.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("category", "unknown"))
    return "unknown"


def _formula_semantic_policy(value: dict[str, Any]) -> str:
    classification = value.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("semantic_policy", "graphic_only"))
    return "graphic_only"


def _formula_role(value: dict[str, Any]) -> str:
    classification = value.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("role", "unknown"))
    return "unknown"


def _has_semantic_expr(value: dict[str, Any]) -> bool:
    return isinstance(value.get("semantic_expr"), dict)


def _formula_units(math_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for entry in math_entries:
        units.append(
            {
                "id": str(entry.get("id", "")),
                "kind": str(entry.get("kind", "")),
                "category": _formula_category(entry),
                "semantic_policy": _formula_semantic_policy(entry),
                "role": _formula_role(entry),
                "has_semantic_expr": _has_semantic_expr(entry),
            }
        )
        if str(entry.get("kind", "")) != "group":
            continue
        for index, item in enumerate(entry.get("items", []), start=1):
            units.append(
                {
                    "id": f"{entry.get('id', '')}#item-{index}",
                    "kind": "display",
                    "category": _formula_category(item),
                    "semantic_policy": _formula_semantic_policy(item),
                    "role": _formula_role(item),
                    "has_semantic_expr": _has_semantic_expr(item),
                }
            )
    return units


def _count_by_key(values: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        name = str(value.get(key, ""))
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1
    return counts


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


def _block_text(block: dict[str, Any]) -> str:
    return completeness_block_text(block)


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _non_ascii_count(text: str) -> int:
    return len(NON_ASCII_RE.findall(text))


def _title_core(text: str) -> str:
    cleaned = clean_heading_title(text)
    match = re.match(r"^(?:\d+|[A-Z])(?:\.(?:\d+|[A-Z]))*(?:\.)?\s+(?P<title>.+)$", cleaned)
    if match:
        return compact_text(match.group("title"))
    return cleaned


def _section_title_looks_bad(title: str) -> bool:
    core = _title_core(title)
    if not core or not LETTER_RE.search(core):
        return True
    if len(core) > 140 or _word_count(core) > 18:
        return True
    if SINGLE_LETTER_RUN_RE.search(core):
        return True
    if sum(1 for char in core if not char.isalnum() and not char.isspace()) >= max(5, len(core) // 4):
        return True
    lowered = f" {core.lower()} "
    if _word_count(core) >= 8 and any(token in lowered for token in (" is ", " are ", " was ", " were ", " defined ")):
        return True
    return False


def _starts_like_paragraph_continuation(text: str) -> bool:
    stripped = compact_text(text)
    if not stripped:
        return False
    if LOWERCASE_START_RE.match(stripped):
        return True
    return bool(re.match(r"^(?:and|but|or|then|thus|therefore|however)\b", stripped, re.IGNORECASE))


def _text_looks_raw_display_latex(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if (
        lowered.startswith(r"\begin{equation")
        or lowered.startswith(r"\[")
        or lowered.startswith(r"\begin{aligned")
    ):
        return True
    latex_signal_count = sum(cleaned.count(token) for token in (r"\mapsto", r"\quad", r"\frac", r"\left", r"\right"))
    if latex_signal_count >= 2 and cleaned.count("\\") >= 3:
        return True
    return False


def _is_display_lead_in(block: dict[str, Any], next_block: dict[str, Any] | None) -> bool:
    if not isinstance(next_block, dict) or str(next_block.get("type", "")) not in {"display_equation_ref", "equation_group_ref"}:
        return False
    text = _paragraph_text(block)
    if not text:
        return False
    if text.endswith((",", ":", ";")):
        return True
    if re.match(r"^(?:and|but|or|then|thus|therefore|however|where|which|with|while|when|since|because|as)\b", text, re.IGNORECASE):
        return True
    if _word_count(text) > 24:
        return False
    return "i.e.," in text or "e.g.," in text


def _text_looks_affiliation_like(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned or _word_count(cleaned) > 24:
        return False
    lowered = f" {cleaned.lower()} "
    if any(token in lowered for token in (" university ", " department ", " institute ", " laboratory ", " laboratories ", " school of ", " usa ")):
        return True
    return bool(re.search(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b", cleaned))


def _text_looks_algorithmic(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if lowered.startswith(("algorithm ", "initialize ", "for every ", "for each ", "remove ", "set ", "store ", "input:", "output:", "return ")):
        return True
    if " input:" in lowered or " output:" in lowered:
        return True
    return bool(re.search(r"\b[A-Z][A-Z0-9_]{2,}\s*\(", cleaned))


def _text_looks_subcase_lead_in(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    lowered = cleaned.lower()
    if lowered.startswith(("the sub-case ", "sub-case ")):
        return _word_count(cleaned) <= 8
    return False


def _text_looks_short_label_lead_in(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    return cleaned.endswith(":") and _word_count(cleaned) <= 3


def _text_looks_short_fragment(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    if SENTENCE_END_RE.search(cleaned) or cleaned.endswith(":"):
        return False
    if _text_looks_heading_like(cleaned) or _text_looks_algorithmic(cleaned):
        return False
    words = WORD_RE.findall(cleaned)
    if not words or len(words) > 4:
        return False
    lowercase_words = sum(1 for word in words if word.islower())
    return lowercase_words >= max(2, len(words) - 1)


def _text_looks_glossary_header(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    lowered = cleaned.lower()
    return "abbreviation" in lowered and _word_count(cleaned) <= 20


def _text_looks_glossary_item(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    words = WORD_RE.findall(cleaned)
    if not words:
        return False
    if len(words) <= 4:
        alpha_words = [word for word in words if word.isalpha()]
        if alpha_words and all(word.islower() for word in alpha_words):
            return True
    if SENTENCE_END_RE.search(cleaned) or CLAUSE_END_RE.search(cleaned):
        return False
    if _word_count(cleaned) > 10:
        return False
    return bool(re.match(r"^(?:[A-Z0-9]{2,}|[A-Z][a-z]*\d)\b", cleaned))


def _text_looks_glossary_entry(text: str, previous_text: str) -> bool:
    return _text_looks_glossary_item(text) and _text_looks_glossary_header(previous_text)


def _text_looks_interstitial_figure_label(
    previous_text: str,
    text: str,
    previous_previous_block: dict[str, Any] | None,
    next_block: dict[str, Any] | None,
) -> bool:
    cleaned = compact_text(previous_text)
    if not cleaned or not _starts_like_paragraph_continuation(text):
        return False
    if _word_count(cleaned) > 3 or SENTENCE_END_RE.search(cleaned) or CLAUSE_END_RE.search(cleaned):
        return False
    if _text_looks_heading_like(cleaned) or _text_looks_algorithmic(cleaned):
        return False
    alpha_words = [word for word in WORD_RE.findall(cleaned) if word.isalpha()]
    if not alpha_words or all(word.islower() for word in alpha_words):
        return False
    figure_adjacent = (
        isinstance(previous_previous_block, dict) and str(previous_previous_block.get("type", "")) == "figure_ref"
    ) or (isinstance(next_block, dict) and str(next_block.get("type", "")) == "figure_ref")
    return figure_adjacent


def _text_looks_heading_like(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    normalized = clean_heading_title(cleaned)
    if normalized != cleaned and _word_count(normalized) <= 10:
        return True
    return bool(re.match(r"^(?:\d+(?:\.\d+)*|[A-Z])(?:\.)?\s+\S", cleaned))


def _text_looks_result_statement(text: str, previous_text: str, next_text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    if not re.match(r"^then\b", cleaned, re.IGNORECASE):
        return False
    if not SENTENCE_END_RE.search(cleaned):
        return False

    previous_cleaned = compact_text(previous_text)
    next_cleaned = compact_text(next_text)
    if previous_cleaned.endswith(("■", "□")):
        return True
    if re.match(r"^(?:proof:|given\b|without loss of generality\b)", next_cleaned, re.IGNORECASE):
        return True
    return False


def _text_looks_noisy(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    if SINGLE_LETTER_RUN_RE.search(cleaned):
        return True
    word_count = _word_count(cleaned)
    if _non_ascii_count(cleaned) >= max(10, word_count // 3) and "\\" not in cleaned:
        return True
    letters = sum(char.isalpha() for char in cleaned)
    symbols = sum(not char.isalnum() and not char.isspace() for char in cleaned)
    if letters and symbols >= max(8, letters // 2):
        return True
    return False


def _caption_looks_noisy(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return False
    word_count = _word_count(cleaned)
    if _non_ascii_count(cleaned) >= max(10, word_count // 3) and "\\" not in cleaned:
        return True
    letters = sum(char.isalpha() for char in cleaned)
    benign_caption_symbols = set("()[]{}.,;:!?-–—/+=<>%'\"`")
    suspicious_symbols = sum(
        not char.isalnum() and not char.isspace() and char not in benign_caption_symbols for char in cleaned
    )
    if letters and suspicious_symbols >= max(4, letters // 3):
        return True
    return False


def _math_text_looks_contaminated(text: str) -> bool:
    return math_text_looks_suspicious(text)


def _snippet(text: str, limit: int = 100) -> str:
    cleaned = compact_text(text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _issue(issue_key: str, label: str, count: int, examples: list[str]) -> dict[str, Any]:
    return {
        "key": issue_key,
        "label": label,
        "count": count,
        "examples": examples[:3],
    }


def _display_path(path: Path) -> str:
    return display_path(path)


def audit_document(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    validation_errors: list[str] = []
    try:
        validate_canonical(document)
    except CanonicalValidationError as exc:
        validation_errors.append(str(exc))

    sections = list(document.get("sections", []))
    blocks = list(document.get("blocks", []))
    math_entries = list(document.get("math", []))
    figures = list(document.get("figures", []))
    references = list(document.get("references", []))
    formula_units = _formula_units(math_entries)

    paragraph_blocks = [block for block in blocks if block.get("type") == "paragraph"]
    display_like_math = [entry for entry in math_entries if str(entry.get("kind")) in {"display", "group"}]
    converted_display_math = [entry for entry in display_like_math if _conversion_status(entry) == "converted"]
    failed_conversion_math = [entry for entry in display_like_math if _conversion_status(entry) == "failed"]
    unconverted_display_math = [entry for entry in display_like_math if _conversion_status(entry) != "converted"]
    high_risk_math = [entry for entry in math_entries if _review_risk(entry) == "high"]
    high_risk_blocks = [block for block in blocks if _review_risk(block) == "high"]
    needs_source_check = [
        value
        for collection in (blocks, math_entries, figures, references)
        for value in collection
        if _review_status(value) == "needs_source_check"
    ]
    flagged_items = [
        value
        for collection in (blocks, math_entries, figures, references)
        for value in collection
        if _review_status(value) == "flagged"
    ]

    block_by_id = {str(block.get("id")): block for block in blocks}
    section_block_ids = {str(block_id) for section in sections for block_id in section.get("block_ids", [])}
    front_matter_block_ids = {
        str(block_id)
        for block_id in (
            document.get("front_matter", {}).get("abstract_block_id"),
            document.get("front_matter", {}).get("funding_block_id"),
        )
        if block_id
    }
    abstract_block_id = str(document.get("front_matter", {}).get("abstract_block_id") or "")
    abstract_text = _block_text(block_by_id.get(abstract_block_id, {})) if abstract_block_id else ""
    abstract_flags = set(abstract_quality_flags(abstract_text))
    body_block_types = {"paragraph", "list_item", "code", "display_equation_ref", "equation_group_ref", "figure_ref", "algorithm"}
    unassigned_body_blocks = [
        block
        for block in blocks
        if str(block.get("type")) in body_block_types and str(block.get("id")) not in section_block_ids
        and str(block.get("id")) not in front_matter_block_ids
    ]

    bad_section_titles: list[str] = []
    for section in sections:
        title = compact_text(str(section.get("title", "")))
        if _section_title_looks_bad(title):
            bad_section_titles.append(title or str(section.get("id", "")))

    fragmented_paragraphs: list[str] = []
    for section in sections:
        previous_text = ""
        section_block_ids = [str(block_id) for block_id in section.get("block_ids", [])]
        glossary_context_active = False
        for index, block_id in enumerate(section_block_ids):
            block = block_by_id.get(str(block_id))
            if not block:
                previous_text = ""
                continue
            if block.get("type") != "paragraph":
                previous_text = ""
                continue
            text = _paragraph_text(block)
            previous_block = block_by_id.get(section_block_ids[index - 1]) if index > 0 else None
            previous_previous_block = block_by_id.get(section_block_ids[index - 2]) if index > 1 else None
            if _text_looks_raw_display_latex(text):
                previous_text = ""
                continue
            next_block = block_by_id.get(section_block_ids[index + 1]) if index + 1 < len(section_block_ids) else None
            if (
                text
                and previous_text
                and _starts_like_paragraph_continuation(text)
                and not SENTENCE_END_RE.search(previous_text)
                and not CLAUSE_END_RE.search(previous_text)
                and not _is_display_lead_in(block, next_block)
                and not _text_looks_affiliation_like(previous_text)
                and not _text_looks_subcase_lead_in(previous_text)
                and not _text_looks_short_label_lead_in(text)
                and not _text_looks_short_label_lead_in(previous_text)
                and not _text_looks_short_fragment(previous_text)
                and not _text_looks_glossary_entry(text, previous_text)
                and not (glossary_context_active and _text_looks_glossary_item(text))
                and not _text_looks_heading_like(previous_text)
                and not _text_looks_interstitial_figure_label(previous_text, text, previous_previous_block, next_block)
                and not _text_looks_algorithmic(text)
                and not _text_looks_algorithmic(previous_text)
                and not _text_looks_result_statement(
                    text,
                    previous_text,
                    _paragraph_text(next_block) if next_block else "",
                )
            ):
                fragmented_paragraphs.append(f"{block['id']}: {_snippet(text)}")
            if _text_looks_glossary_header(text):
                glossary_context_active = True
            elif glossary_context_active and _text_looks_glossary_item(text):
                glossary_context_active = True
            elif glossary_context_active and not _text_looks_short_fragment(text) and not _text_looks_glossary_item(text):
                glossary_context_active = False
            previous_text = text or previous_text

    noisy_captions = [
        f"{figure.get('id')}: {_snippet(str(figure.get('caption', '')))}"
        for figure in figures
        if _caption_looks_noisy(str(figure.get("caption", "")))
    ]

    suspicious_math_entries = [
        f"{entry.get('id')}: {_snippet(str(entry.get('display_latex', '')))}"
        for entry in display_like_math
        if _math_text_looks_contaminated(str(entry.get("display_latex", "")))
    ]

    formula_diagnostic_hits: list[dict[str, Any]] = []
    for entry in display_like_math:
        diagnostics = diagnose_formula_entry(entry)
        if not diagnostics:
            continue
        formula_diagnostic_hits.append(
            {
                "id": str(entry.get("id", "")),
                "diagnostics": diagnostics,
                "summary": summarize_formula_diagnostics(diagnostics),
            }
        )
    high_severity_formula_diagnostics = [
        hit for hit in formula_diagnostic_hits if any(diagnostic.severity == "high" for diagnostic in hit["diagnostics"])
    ]
    semantic_formula_units = [unit for unit in formula_units if unit["semantic_policy"] == "semantic"]
    structure_only_formula_units = [unit for unit in formula_units if unit["semantic_policy"] == "structure_only"]
    graphic_only_formula_units = [unit for unit in formula_units if unit["semantic_policy"] == "graphic_only"]
    semantic_expr_units = [unit for unit in formula_units if unit["has_semantic_expr"]]
    missing_semantic_expr_units = [unit for unit in semantic_formula_units if not unit["has_semantic_expr"]]
    formula_category_counts = _count_by_key(formula_units, "category")
    formula_policy_counts = _count_by_key(formula_units, "semantic_policy")
    formula_role_counts = _count_by_key(formula_units, "role")

    issues: list[dict[str, Any]] = []
    if validation_errors:
        issues.append(_issue("validation_errors", "validation errors", len(validation_errors), validation_errors))
    if not document.get("front_matter", {}).get("authors"):
        issues.append(_issue("missing_authors", "missing authors", 1, ["front_matter.authors is empty"]))
    if not abstract_block_id or "missing" in abstract_flags:
        details = ["front_matter.abstract_block_id is empty"] if not abstract_block_id else ["abstract uses missing placeholder"]
        issues.append(_issue("missing_abstract", "missing abstract", 1, details))
    elif abstract_flags:
        issues.append(
            _issue(
                "bad_abstract",
                "bad abstract",
                1,
                [f"{','.join(sorted(abstract_flags))}: {_snippet(abstract_text)}"],
            )
        )
    if len(sections) <= 1:
        issues.append(_issue("weak_sections", "weak section structure", 1, [f"only {len(sections)} sections"]))
    if not references and document_expects_references(document):
        issues.append(_issue("missing_references", "missing references", 1, ["references list is empty"]))
    if not figures and document_expects_figures(blocks):
        issues.append(_issue("missing_figures", "missing figures", 1, ["figures list is empty"]))
    if high_risk_math:
        issues.append(
            _issue(
                "high_risk_math",
                "high-risk math",
                len(high_risk_math),
                [f"{entry['id']}: {_snippet(str(entry.get('display_latex', '')))}" for entry in high_risk_math],
            )
        )
    if high_risk_blocks:
        issues.append(
            _issue(
                "high_risk_blocks",
                "high-risk blocks",
                len(high_risk_blocks),
                [f"{block['id']}: {_snippet(_block_text(block))}" for block in high_risk_blocks],
            )
        )
    if flagged_items:
        issues.append(_issue("flagged_items", "flagged review items", len(flagged_items), [str(item.get("id", "")) for item in flagged_items]))
    if needs_source_check:
        issues.append(
            _issue(
                "needs_source_check",
                "needs-source-check items",
                len(needs_source_check),
                [str(item.get("id", "")) for item in needs_source_check],
            )
        )
    if bad_section_titles:
        issues.append(_issue("bad_section_titles", "bad section titles", len(bad_section_titles), bad_section_titles))
    if fragmented_paragraphs:
        issues.append(_issue("fragmented_paragraphs", "fragmented paragraphs", len(fragmented_paragraphs), fragmented_paragraphs))
    if noisy_captions:
        issues.append(_issue("noisy_captions", "noisy figure captions", len(noisy_captions), noisy_captions))
    if suspicious_math_entries:
        issues.append(
            _issue(
                "suspicious_math_entries",
                "suspicious math entries",
                len(suspicious_math_entries),
                suspicious_math_entries,
            )
        )
    if formula_diagnostic_hits:
        issues.append(
            _issue(
                "formula_diagnostic_formulas",
                "formula diagnostic hits",
                len(formula_diagnostic_hits),
                [f"{hit['id']}: {hit['summary']}" for hit in formula_diagnostic_hits],
            )
        )
    if missing_semantic_expr_units:
        issues.append(
            _issue(
                "missing_semantic_expr",
                "semantic formulas missing semantic expr",
                len(missing_semantic_expr_units),
                [unit["id"] for unit in missing_semantic_expr_units],
            )
        )
    if unconverted_display_math:
        issues.append(
            _issue(
                "unconverted_display_math",
                "unconverted display math",
                len(unconverted_display_math),
                [f"{entry['id']}: status={_conversion_status(entry)}" for entry in unconverted_display_math[:25]],
            )
        )
    if unassigned_body_blocks:
        issues.append(
            _issue(
                "unassigned_body_blocks",
                "unassigned body blocks",
                len(unassigned_body_blocks),
                [f"{block['id']}: {_snippet(_block_text(block))}" for block in unassigned_body_blocks],
            )
        )

    paragraph_count = max(len(paragraph_blocks), 1)
    math_count = max(len(math_entries), 1)
    display_math_count = max(len(display_like_math), 1)
    section_count = max(len(sections), 1)
    semantic_formula_count = max(len(semantic_formula_units), 1)

    score = 0.0
    score += min(len(high_risk_math) * 1.5, 30.0)
    score += min(len(high_risk_blocks) * 0.5, 15.0)
    score += len(flagged_items) * 4.0
    score += len(needs_source_check) * 3.0
    score += len(bad_section_titles) * 2.0
    score += len(fragmented_paragraphs) * 1.5
    score += len(noisy_captions) * 1.5
    score += len(suspicious_math_entries) * 2.5
    score += min(len(formula_diagnostic_hits) * 2.0, 18.0)
    score += min(len(high_severity_formula_diagnostics) * 1.5, 12.0)
    score += min(len(missing_semantic_expr_units) * 1.5, 12.0)
    score += min(len(failed_conversion_math) * 1.0, 10.0)
    score += min(len(unassigned_body_blocks) * 1.0, 10.0)
    score += (len(high_risk_math) / math_count) * 20.0
    score += (len(fragmented_paragraphs) / paragraph_count) * 20.0
    score += (len(bad_section_titles) / section_count) * 15.0
    score += (len(suspicious_math_entries) / display_math_count) * 15.0
    score += (len(formula_diagnostic_hits) / display_math_count) * 14.0
    score += (len(unconverted_display_math) / display_math_count) * 12.0
    score += (len(missing_semantic_expr_units) / semantic_formula_count) * 12.0
    score += len(validation_errors) * 10.0
    expects_figures = document_expects_figures(blocks)
    expects_references = document_expects_references(document)
    if not document.get("front_matter", {}).get("authors"):
        score += 6.0
    if not abstract_block_id or "missing" in abstract_flags:
        score += 6.0
    elif abstract_flags:
        score += 8.0
    if len(sections) <= 1:
        score += 4.0
    if not references and expects_references:
        score += 4.0
    if not figures and expects_figures:
        score += 4.0

    return {
        "paper_id": str(document.get("paper_id", "")),
        "title": str(document.get("title", "")),
        "year": None,
        "canonical_path": _display_path(path),
        "has_canonical": True,
        "score": round(score, 2),
        "counts": {
            "sections": len(sections),
            "blocks": len(blocks),
            "paragraph_blocks": len(paragraph_blocks),
            "math_entries": len(math_entries),
            "formula_units": len(formula_units),
            "display_math_entries": len(display_like_math),
            "converted_display_math": len(converted_display_math),
            "unconverted_display_math": len(unconverted_display_math),
            "failed_conversion_math": len(failed_conversion_math),
            "semantic_formula_units": len(semantic_formula_units),
            "structure_only_formula_units": len(structure_only_formula_units),
            "graphic_only_formula_units": len(graphic_only_formula_units),
            "semantic_expr_units": len(semantic_expr_units),
            "missing_semantic_expr_units": len(missing_semantic_expr_units),
            "figures": len(figures),
            "references": len(references),
            "high_risk_math": len(high_risk_math),
            "high_risk_blocks": len(high_risk_blocks),
            "flagged_items": len(flagged_items),
            "needs_source_check": len(needs_source_check),
            "bad_section_titles": len(bad_section_titles),
            "fragmented_paragraphs": len(fragmented_paragraphs),
            "noisy_captions": len(noisy_captions),
            "suspicious_math_entries": len(suspicious_math_entries),
            "formula_diagnostic_formulas": len(formula_diagnostic_hits),
            "high_severity_formula_diagnostics": len(high_severity_formula_diagnostics),
            "unassigned_body_blocks": len(unassigned_body_blocks),
            "validation_errors": len(validation_errors),
        },
        "formula_classification": {
            "categories": formula_category_counts,
            "semantic_policies": formula_policy_counts,
            "roles": formula_role_counts,
        },
        "issues": issues,
    }


def audit_missing_canonical(paper_dir: Path) -> dict[str, Any]:
    return {
        "paper_id": paper_dir.name,
        "title": "",
        "year": None,
        "canonical_path": _display_path(paper_dir / "canonical.json"),
        "has_canonical": False,
        "score": 250.0,
        "counts": {
            "sections": 0,
            "blocks": 0,
            "paragraph_blocks": 0,
            "math_entries": 0,
            "formula_units": 0,
            "display_math_entries": 0,
            "converted_display_math": 0,
            "unconverted_display_math": 0,
            "failed_conversion_math": 0,
            "semantic_formula_units": 0,
            "structure_only_formula_units": 0,
            "graphic_only_formula_units": 0,
            "semantic_expr_units": 0,
            "missing_semantic_expr_units": 0,
            "figures": 0,
            "references": 0,
            "high_risk_math": 0,
            "high_risk_blocks": 0,
            "flagged_items": 0,
            "needs_source_check": 0,
            "bad_section_titles": 0,
            "fragmented_paragraphs": 0,
            "noisy_captions": 0,
            "suspicious_math_entries": 0,
            "formula_diagnostic_formulas": 0,
            "high_severity_formula_diagnostics": 0,
            "unassigned_body_blocks": 0,
            "validation_errors": 0,
        },
        "formula_classification": {
            "categories": {},
            "semantic_policies": {},
            "roles": {},
        },
        "issues": [
            _issue(
                "missing_canonical",
                "missing canonical output",
                1,
                [f"{paper_dir.name}/canonical.json has not been generated"],
            )
        ],
    }


def audit_corpus(
    *,
    docs_dir: Path,
    json_report_path: Path,
    markdown_report_path: Path,
) -> dict[str, Any]:
    layout = current_layout()
    papers: list[dict[str, Any]] = []
    canonical_count = 0
    missing_canonical_papers: list[str] = []
    corpus_category_counts: dict[str, int] = {}
    corpus_policy_counts: dict[str, int] = {}
    corpus_role_counts: dict[str, int] = {}
    semantic_expr_units = 0
    semantic_formula_units = 0
    for pdf_path in discover_paper_pdf_paths(layout=layout):
        paper_id = paper_id_from_pdf_path(pdf_path, layout=layout)
        paper_dir = docs_dir / paper_id
        canonical_path = paper_dir / "canonical.json"
        if canonical_path.exists():
            paper_report = audit_document(canonical_path)
            papers.append(paper_report)
            for key, count in paper_report["formula_classification"]["categories"].items():
                corpus_category_counts[key] = corpus_category_counts.get(key, 0) + int(count)
            for key, count in paper_report["formula_classification"]["semantic_policies"].items():
                corpus_policy_counts[key] = corpus_policy_counts.get(key, 0) + int(count)
            for key, count in paper_report["formula_classification"]["roles"].items():
                corpus_role_counts[key] = corpus_role_counts.get(key, 0) + int(count)
            semantic_expr_units += int(paper_report["counts"]["semantic_expr_units"])
            semantic_formula_units += int(paper_report["counts"]["semantic_formula_units"])
            canonical_count += 1
            continue
        papers.append(audit_missing_canonical(paper_dir))
        missing_canonical_papers.append(paper_dir.name)

    ranked = sorted(papers, key=lambda item: (-float(item["score"]), str(item["paper_id"])))
    return {
        "generated_at": _now_iso(),
        "paper_count": len(ranked),
        "canonical_count": canonical_count,
        "missing_canonical_count": len(missing_canonical_papers),
        "missing_canonical_papers": missing_canonical_papers,
        "formula_classification": {
            "categories": corpus_category_counts,
            "semantic_policies": corpus_policy_counts,
            "roles": corpus_role_counts,
            "semantic_expr_units": semantic_expr_units,
            "semantic_formula_units": semantic_formula_units,
        },
        "report_paths": {
            "json": display_path(json_report_path),
            "markdown": display_path(markdown_report_path),
        },
        "papers": ranked,
    }
