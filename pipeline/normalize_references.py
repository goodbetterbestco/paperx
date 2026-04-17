from __future__ import annotations

import re
from collections import Counter

from pipeline.normalize_prose import normalize_prose_text


LABEL_PREFIX_RE = re.compile(r"^(\[[^\]]+\]\s*)(.*)$")
SPACED_DIGITS_RE = re.compile(r"(?<![A-Za-z])(?:\d\s+){1,5}\d(?![A-Za-z])")
PAGE_RANGE_RE = re.compile(r"\s*\{\s*")
PUNCT_SPACE_BEFORE_RE = re.compile(r"\s+([,.:;)\]])")
PUNCT_SPACE_AFTER_OPEN_RE = re.compile(r"([(\[])\s+")
MULTISPACE_RE = re.compile(r"\s{2,}")
HYPHEN_GAP_RE = re.compile(r"(?<=[A-Za-z0-9])-\s+(?=[A-Za-z0-9])")

REFERENCE_REPLACEMENTS: list[tuple[str, re.Pattern[str], str]] = [
    ("graphics_join", re.compile(r"\bGraph\s+ics\b", re.IGNORECASE), "Graphics"),
    ("freeform_join", re.compile(r"\bfreefrom\b", re.IGNORECASE), "freeform"),
    ("five_axis", re.compile(r"\bve axis\b", re.IGNORECASE), "five axis"),
    ("perspective_join", re.compile(r"\bper\s*spective\b", re.IGNORECASE), "perspective"),
    ("parallelepipeds_join", re.compile(r"\bpar\s*allelepipeds\b", re.IGNORECASE), "parallelepipeds"),
    ("decompositions_join", re.compile(r"\bdecompo\s*sitions\b", re.IGNORECASE), "decompositions"),
    ("sons_titlecase", re.compile(r"& sons\b"), "& Sons"),
    ("title_algorithms", re.compile(r"(?<=\.\s)algorithms for\b"), "Algorithms for"),
    ("title_curves", re.compile(r"(?<=\.\s)curves and Surfaces\b"), "Curves and Surfaces"),
    ("title_visibility", re.compile(r"(?<=\.\s)visibility maps\b"), "Visibility maps"),
    ("roman_one", re.compile(r"\bcurves i:\b", re.IGNORECASE), "curves I:"),
    ("roman_two", re.compile(r"\bhidden surface removal,\s*ii\b", re.IGNORECASE), "hidden surface removal, II"),
    ("ordinal_23rd", re.compile(r"\b2\s*3rd\b", re.IGNORECASE), "23rd"),
    ("guting_name", re.compile(r"\bG uting\b"), "Güting"),
]


def _compact_spaced_digits(text: str, counts: Counter[str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        counts["digit_compaction"] += 1
        return re.sub(r"\s+", "", match.group(0))

    return SPACED_DIGITS_RE.sub(replacement, text)


def normalize_reference_text(text: str) -> tuple[str, Counter[str]]:
    updated = text.strip()
    counts: Counter[str] = Counter()

    label_prefix = ""
    body = updated
    match = LABEL_PREFIX_RE.match(updated)
    if match:
        label_prefix = match.group(1)
        body = match.group(2)

    body, prose_counts = normalize_prose_text(body)
    counts.update(prose_counts)

    body = _compact_spaced_digits(body, counts)

    for label, pattern, replacement in REFERENCE_REPLACEMENTS:
        body, replacement_count = pattern.subn(replacement, body)
        if replacement_count:
            counts[label] += replacement_count

    body, page_range_count = PAGE_RANGE_RE.subn("-", body)
    if page_range_count:
        counts["page_range"] += page_range_count

    body, hyphen_gap_count = HYPHEN_GAP_RE.subn("-", body)
    if hyphen_gap_count:
        counts["hyphen_gap"] += hyphen_gap_count

    body, before_count = PUNCT_SPACE_BEFORE_RE.subn(r"\1", body)
    if before_count:
        counts["punct_space_before"] += before_count

    body, after_count = PUNCT_SPACE_AFTER_OPEN_RE.subn(r"\1", body)
    if after_count:
        counts["punct_space_after_open"] += after_count

    body, multispace_count = MULTISPACE_RE.subn(" ", body)
    if multispace_count:
        counts["multispace"] += multispace_count

    normalized = f"{label_prefix}{body}".strip()
    return normalized, counts
