from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from pipeline.corpus_layout import CORPUS_DIR, CORPUS_LEXICON_PATH

DOCS_DIR = CORPUS_DIR
LEXICON_PATH = CORPUS_LEXICON_PATH
AUTHOR_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*")


def _is_join_candidate(value: str, *, count: int = 0) -> bool:
    if not value or " " in value:
        return False
    if value.isdigit():
        return False
    if "-" in value:
        return True
    if any(ord(char) > 127 for char in value):
        return True
    if len(value) >= 8:
        return True
    return count >= 3 and len(value) >= 5


@lru_cache(maxsize=1)
def load_corpus_lexicon() -> dict[str, Any]:
    if not LEXICON_PATH.exists():
        return {}
    return json.loads(LEXICON_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def corpus_join_terms() -> set[str]:
    lexicon = load_corpus_lexicon()
    join_terms: set[str] = set()

    for entry in lexicon.get("terms", []):
        canonical = str(entry.get("canonical", "")).strip().lower()
        count = int(entry.get("count", 0) or 0)
        if _is_join_candidate(canonical, count=count):
            join_terms.add(canonical)
        for variant in entry.get("variants", []):
            normalized = str(variant).strip().lower().replace(" ", "")
            if _is_join_candidate(normalized, count=count):
                join_terms.add(normalized)

    for value in lexicon.get("acronyms", []):
        normalized = str(value).strip().lower().replace("-", "")
        if normalized:
            join_terms.add(normalized)

    for entry in lexicon.get("authors", []):
        canonical = str(entry.get("canonical", "")).strip()
        count = int(entry.get("count", 0) or 0)
        for token in AUTHOR_TOKEN_RE.findall(canonical):
            normalized = token.lower()
            if _is_join_candidate(normalized, count=count):
                join_terms.add(normalized)

    return join_terms
