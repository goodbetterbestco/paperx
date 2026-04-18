from __future__ import annotations

import re

SHORT_WORD_RE = re.compile(r"[A-Za-z0-9]+")
RUNNING_HEADER_TEXT_RE = re.compile(r"^[A-Z][A-Z\s.-]{2,}$")
PROCEDIA_RUNNING_HEADER_RE = re.compile(
    r"\b(?:Author name\s+Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000|"
    r"Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000-000\s+Procedia\s+CIRP\s+\d+\s+\(\d{4}\)\s+\d+-\d+)\b",
    re.IGNORECASE,
)
TABLE_CAPTION_RE = re.compile(r"^\s*table\b", re.IGNORECASE)
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

__all__ = [
    "DISPLAY_MATH_PROSE_CUE_RE",
    "DISPLAY_MATH_RESUME_RE",
    "DISPLAY_MATH_START_RE",
    "EMBEDDED_HEADING_PREFIX_RE",
    "PROCEDIA_RUNNING_HEADER_RE",
    "RUNNING_HEADER_TEXT_RE",
    "SHORT_WORD_RE",
    "TABLE_CAPTION_RE",
]
