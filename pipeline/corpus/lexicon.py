from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from pipeline.corpus_layout import CORPUS_DIR, CORPUS_LEXICON_PATH, ProjectLayout, current_layout

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


@lru_cache(maxsize=None)
def _load_corpus_lexicon(lexicon_path: str) -> dict[str, Any]:
    path = Path(lexicon_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_corpus_lexicon(*, layout: ProjectLayout | None = None) -> dict[str, Any]:
    active_layout = layout or current_layout()
    return _load_corpus_lexicon(str(active_layout.corpus_lexicon_path.resolve()))


@lru_cache(maxsize=None)
def _corpus_join_terms(lexicon_path: str) -> set[str]:
    lexicon = _load_corpus_lexicon(lexicon_path)
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


def corpus_join_terms(*, layout: ProjectLayout | None = None) -> set[str]:
    active_layout = layout or current_layout()
    return _corpus_join_terms(str(active_layout.corpus_lexicon_path.resolve()))


__all__ = [
    "AUTHOR_TOKEN_RE",
    "DOCS_DIR",
    "LEXICON_PATH",
    "corpus_join_terms",
    "load_corpus_lexicon",
]
