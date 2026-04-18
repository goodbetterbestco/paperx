from __future__ import annotations

import re
from typing import Any

from pipeline.text.headings import compact_text
from pipeline.types import default_review


WORD_RE = re.compile(r"[A-Za-z0-9]+")
NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")
MATH_COMMAND_RE = re.compile(r"\\[A-Za-z]+")
MATH_SYMBOL_RE = re.compile(r"[=<>+\-*/^_{}[\]()|]|[±×·−∑∫√∞≤≥→↦]")
SINGLE_LETTER_RUN_RE = re.compile(r"(?:\b[A-Za-z]\b(?:\s+|$)){4,}")
PROSE_CONTAMINATION_RE = re.compile(
    r"\b(?:figure|table|algorithm|copyright|received|accepted|introduction|references|abstract|elsevier|springer)\b",
    re.IGNORECASE,
)
GLYPH_ARTIFACT_RE = re.compile(r"glyph\[[^\]]+\]", re.IGNORECASE)
TRUNCATED_TAG_RE = re.compile(r"\\tag\{[^}]*$")
TRUNCATED_ENV_RE = re.compile(r"\\begin\{[^}]+\}(?!.*\\end\{[^}]+\})")
TRUNCATED_TAIL_RE = re.compile(r"[=+\-*/([{]\s*$")
ALGORITHM_CALL_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\s*\(")


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _non_ascii_count(text: str) -> int:
    return len(NON_ASCII_RE.findall(text))


def _math_signal_count(text: str) -> int:
    return len(MATH_COMMAND_RE.findall(text)) + len(MATH_SYMBOL_RE.findall(text))


def _has_manual_review(review: Any) -> bool:
    if not isinstance(review, dict):
        return False
    if compact_text(str(review.get("notes", ""))):
        return True
    status = compact_text(str(review.get("status", "")))
    return bool(status and status != "unreviewed")


def math_text_looks_suspicious(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return True
    if GLYPH_ARTIFACT_RE.search(cleaned):
        return True
    if PROSE_CONTAMINATION_RE.search(cleaned):
        return True
    if TRUNCATED_TAG_RE.search(cleaned) or TRUNCATED_ENV_RE.search(cleaned) or TRUNCATED_TAIL_RE.search(cleaned):
        return True
    if _non_ascii_count(cleaned) >= 8 and "\\" not in cleaned:
        return True
    word_count = _word_count(cleaned)
    math_signal_count = _math_signal_count(cleaned)
    if word_count >= 12 and math_signal_count < max(4, word_count // 5):
        return True
    return False


def review_for_math_entry(entry: dict[str, Any]) -> dict[str, str]:
    existing_review = entry.get("review")
    if _has_manual_review(existing_review):
        return {
            "status": str(existing_review.get("status", "unreviewed")),
            "risk": str(existing_review.get("risk", "medium")),
            "notes": str(existing_review.get("notes", "")),
        }

    risk = "high" if math_text_looks_suspicious(str(entry.get("display_latex", ""))) else "medium"
    return default_review(risk=risk)


def review_for_math_ref_block(entry: dict[str, Any]) -> dict[str, str]:
    return default_review(risk=review_for_math_entry(entry)["risk"])


def algorithm_text_looks_suspicious(text: str) -> bool:
    cleaned = compact_text(text)
    if not cleaned:
        return True
    if GLYPH_ARTIFACT_RE.search(cleaned):
        return True
    if SINGLE_LETTER_RUN_RE.search(cleaned):
        return True
    word_count = _word_count(cleaned)
    if word_count <= 2 and not ALGORITHM_CALL_RE.search(cleaned):
        return True
    if _non_ascii_count(cleaned) >= max(8, word_count // 3) and not ALGORITHM_CALL_RE.search(cleaned):
        return True
    return False


def review_for_algorithm_block_text(text: str, existing_review: Any | None = None) -> dict[str, str]:
    if _has_manual_review(existing_review):
        return {
            "status": str(existing_review.get("status", "unreviewed")),
            "risk": str(existing_review.get("risk", "medium")),
            "notes": str(existing_review.get("notes", "")),
        }

    risk = "high" if algorithm_text_looks_suspicious(text) else "medium"
    return default_review(risk=risk)
