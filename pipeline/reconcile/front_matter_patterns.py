from __future__ import annotations

import re

FUNDING_RE = re.compile(r"supp\s*orted\s+in\s+part|supported\s+in\s+part", re.IGNORECASE)
NAME_TOKEN_RE = re.compile(r"[A-Z][a-z]+")
AUTHOR_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'`-]*")
REFERENCE_VENUE_RE = re.compile(
    r"\b(?:press|springer|elsevier|journal|transactions|conference|proceedings|proc\.|siggraph|eurographics|ieee|acm|forum|doi|isbn|issn|pages?|vol\.|volume|technical report|workshop)\b",
    re.IGNORECASE,
)
AUTHOR_MARKER_RE = re.compile(r"(?:\\\(|\\\)|\\mathbf|\\mathrm|©|\{|\}|\^)")
AUTHOR_AFFILIATION_INDEX_RE = re.compile(r"\b\d+\b")
ABSTRACT_LEAD_RE = re.compile(r"^\s*abstract\b[\s:.-]*", re.IGNORECASE)
ABSTRACT_MARKER_ONLY_RE = re.compile(r"^\s*abstract\b[\s:.-]*$", re.IGNORECASE)
ABSTRACT_BODY_BREAK_RE = re.compile(
    r"^\s*(?:figure|table|definition\b|theorem\b|for any two points|"
    r"we define\b|our goal\b|a number of researchers|these problems\b|"
    r"in this section\b|some non-simple curves\b)",
    re.IGNORECASE,
)
ABSTRACT_CONTINUATION_RE = re.compile(
    r"^\s*(?:we\b|this\b|in this paper\b|our\b|the paper\b|it\b|these\b|"
    r"using\b|by\b|based on\b|results?\b|experiments?\b|findings?\b|"
    r"we (?:show|present|propose|study|derive|develop|analyze|investigate)\b)",
    re.IGNORECASE,
)
FIGURE_REF_RE = re.compile(r"\bfigure\s+\d", re.IGNORECASE)
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
    r"ecg-tr-|ist-\d{2,}|effective computational geometry|key\s*words?:|corresponding author|"
    r"current address|creativecommons|creative commons|licensed under|this manuscript version is made available|"
    r"numdam|cedram|archive ouverte)\b",
    re.IGNORECASE,
)
ABBREVIATED_VENUE_LINE_RE = re.compile(r"(?:\b[A-Za-z]{2,}\.\s*){3,}")
KEYWORDS_LEAD_RE = re.compile(r"^\s*key\s*words?:\s", re.IGNORECASE)
TRAILING_ABSTRACT_BOILERPLATE_RE = re.compile(
    r"\s+©\s*\d{4}.*?\ball rights reserved\.?$",
    re.IGNORECASE,
)
TRAILING_ABSTRACT_TAIL_RE = re.compile(
    r"\s+(?:©\s*\d{4}\b.*|key\s*words?:\s.*|keywords?\s+and\s+phrases\s+.*|"
    r"acm\s+subject\s+classification\s+.*|digital\s+object\s+identifier\s+.*|"
    r"(?:\d+|[IVX]+)\s+introduction\b.*)$",
    re.IGNORECASE,
)
CITATION_YEAR_RE = re.compile(r"\(\s*(?:18|19|20)\d{2}[a-z]?\s*\)\.")
CITATION_AUTHOR_SPLIT_RE = re.compile(
    r"(?<=\.)\s*,\s+(?=[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'`.-]*(?:[- ][A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'`.-]*)*(?:\s+[A-Z](?:\.[A-Z])*\.?|,\s*[A-Z](?:\.[A-Z])*\.?))"
)

__all__ = [
    "ABBREVIATED_VENUE_LINE_RE",
    "ABSTRACT_BODY_BREAK_RE",
    "ABSTRACT_CONTINUATION_RE",
    "ABSTRACT_LEAD_RE",
    "ABSTRACT_MARKER_ONLY_RE",
    "AUTHOR_AFFILIATION_INDEX_RE",
    "AUTHOR_MARKER_RE",
    "AUTHOR_NOTE_RE",
    "AUTHOR_TOKEN_RE",
    "CITATION_AUTHOR_SPLIT_RE",
    "CITATION_YEAR_RE",
    "FIGURE_REF_RE",
    "FRONT_MATTER_METADATA_RE",
    "FUNDING_RE",
    "INTRO_MARKER_RE",
    "KEYWORDS_LEAD_RE",
    "NAME_TOKEN_RE",
    "PREPRINT_MARKER_RE",
    "REFERENCE_VENUE_RE",
    "TITLE_PAGE_METADATA_RE",
    "TRAILING_ABSTRACT_BOILERPLATE_RE",
    "TRAILING_ABSTRACT_TAIL_RE",
]
