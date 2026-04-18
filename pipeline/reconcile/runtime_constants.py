from __future__ import annotations

import re


CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MATHPIX_HINT_TOKEN_RE = re.compile(r"[A-Za-z]{1,}")
MATH_TOKEN_RE = re.compile(r"\b(?:Det|Diag|X|Y|Z|W|N|M|D|u|v|s|t|q|A)\b")
DIAGRAM_DECISION_RE = re.compile(r"^(?:start|stop|yes|no|yes yes|yes no|no yes)\b", re.IGNORECASE)
DIAGRAM_QUERY_RE = re.compile(r"^(?:is there|are there|whether)\b", re.IGNORECASE)
DIAGRAM_ACTION_RE = re.compile(r"^(?:search entity|extract\b|label\b|define\b|set\b|filter out\b)", re.IGNORECASE)
LABEL_CLOUD_TOKEN_RE = re.compile(r"^(?:\([A-Za-z]\)|[A-Za-z]{1,2}\d{1,3}|\d+[A-Za-z]{0,2}|[A-Za-z]{1,3}|\d{1,3})$")
QUOTED_IDENTIFIER_FRAGMENT_RE = re.compile(r'^"?[A-Za-z]+(?:_[A-Za-z]+){1,8}"?\s*[?;:]?$')
REFERENCE_START_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{0,12}\b")
REFERENCE_AUTHOR_RE = re.compile(r"^(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+(?:\s+(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+)*[.,]")
REFERENCE_YEAR_RE = re.compile(r"\b(?:18|19|20)\d{2}[a-z]?\b", re.IGNORECASE)
ABOUT_AUTHOR_RE = re.compile(r"^\s*about the author\b", re.IGNORECASE)
TERMINAL_PUNCTUATION_RE = re.compile(r"[.!?:]\)?[\"']?$")
LEADING_OCR_MARKER_RE = re.compile(r"^(?:;\s*1|1)\s+(?=[A-Z])")
LEADING_PUNCT_ARTIFACT_RE = re.compile(r"^[;,:]\s+(?=[A-Za-z])")
LEADING_VAR_ARTIFACT_RE = re.compile(r"^[a-z]\s+(?=(?:On|The|Since|where)\b)")
TRAILING_NUMERIC_ARTIFACT_RE = re.compile(r"(?<=\.)\s+\d+(?:\s+\d+)+\s*$")
LEADING_NEGATIONSLASH_ARTIFACT_RE = re.compile(r"^(?:negationslash\s+)+", re.IGNORECASE)
SHORT_OCR_NOISE_RE = re.compile(
    r"^(?:[;:.,\-\s0-9]+|[a-z]\s+[a-z]|[a-z]{1,3}-[a-z]{1,3}|[\d\sA-Za-z]*[^\x00-\x7f][\d\sA-Za-z]*)$"
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


__all__ = [
    "ABOUT_AUTHOR_RE",
    "CONTROL_CHAR_RE",
    "DIAGRAM_ACTION_RE",
    "DIAGRAM_DECISION_RE",
    "DIAGRAM_QUERY_RE",
    "LABEL_CLOUD_TOKEN_RE",
    "LEADING_NEGATIONSLASH_ARTIFACT_RE",
    "LEADING_OCR_MARKER_RE",
    "LEADING_PUNCT_ARTIFACT_RE",
    "LEADING_VAR_ARTIFACT_RE",
    "MATHPIX_HINT_TOKEN_RE",
    "MATH_TOKEN_RE",
    "QUOTED_IDENTIFIER_FRAGMENT_RE",
    "REFERENCE_AUTHOR_RE",
    "REFERENCE_START_RE",
    "REFERENCE_YEAR_RE",
    "SHORT_OCR_NOISE_RE",
    "TERMINAL_PUNCTUATION_RE",
    "TRAILING_NUMERIC_ARTIFACT_RE",
    "TRUNCATED_PROSE_LEAD_STOPWORDS",
]
