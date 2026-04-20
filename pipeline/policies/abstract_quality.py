from __future__ import annotations

import re

from pipeline.text.headings import compact_text


MISSING_ABSTRACT_PLACEHOLDER = "[missing from original]"
NO_ABSTRACT_IN_BASE_MATERIAL = "No abstract in base material."
WORD_RE = re.compile(r"[A-Za-z0-9]+")
ABSTRACT_ONLY_RE = re.compile(r"^\s*abstract\b[\s:.-]*$", re.IGNORECASE)
KEYWORDS_RE = re.compile(r"(?:^|\s)key\s*words?:\s", re.IGNORECASE)
SECTION_MARKER_RE = re.compile(
    r"^\s*(?:\d+|[IVX]+)(?:\.\d+)*\.?\s+"
    r"(?:introduction|background|preliminaries|methods?|results?|discussion|conclusions?|references)\b",
    re.IGNORECASE,
)
ABSTRACT_METADATA_RE = re.compile(
    r"\b(?:accepted manuscript|manuscript version|creative commons|creativecommons|"
    r"cc-by(?:-nc(?:-nd)?)?|available online|article history|published online|"
    r"open access|licensed under|this manuscript version is made available|"
    r"the following article|archive ouverte|numdam|cedram|sciencedirect|"
    r"corresponding author|doi\b|license)\b",
    re.IGNORECASE,
)


def clean_abstract_text(text: str) -> str:
    return compact_text(str(text))


def abstract_word_count(text: str) -> int:
    return len(WORD_RE.findall(clean_abstract_text(text)))


def abstract_quality_flags(text: str) -> list[str]:
    cleaned = clean_abstract_text(text)
    if not cleaned or cleaned in {MISSING_ABSTRACT_PLACEHOLDER, NO_ABSTRACT_IN_BASE_MATERIAL}:
        return ["missing"]

    flags: list[str] = []
    if ABSTRACT_ONLY_RE.fullmatch(cleaned):
        flags.append("marker_only")
    if KEYWORDS_RE.search(cleaned):
        flags.append("keywords")
    if ABSTRACT_METADATA_RE.search(cleaned) or cleaned.startswith("@"):
        flags.append("metadata")
    if SECTION_MARKER_RE.search(cleaned):
        flags.append("section_marker")
    if abstract_word_count(cleaned) > 320:
        flags.append("too_long")
    return list(dict.fromkeys(flags))


def abstract_quality_rank(text: str) -> int:
    flags = set(abstract_quality_flags(text))
    if "missing" in flags:
        return 1
    if flags:
        return 2
    return 0
