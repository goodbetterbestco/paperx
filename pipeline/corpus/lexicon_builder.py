#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from wordfreq import zipf_frequency
except Exception:  # pragma: no cover - optional
    zipf_frequency = None

from pipeline.corpus_layout import ProjectLayout, current_layout


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*")
ACRONYM_RE = re.compile(r"\b(?:[A-Z]{2,8}|[A-Z]-[A-Z][A-Za-z]*|[A-Z][A-Z0-9]{1,6})\b")
STOPWORDS = {
    "about", "above", "after", "again", "against", "analysis", "analysiss", "along", "also", "among", "an",
    "and", "another", "any", "are", "around", "as", "at", "be", "because", "been", "before", "being", "between",
    "both", "but", "by", "can", "case", "cases", "chapter", "close", "common", "computing", "context", "curved",
    "data", "defined", "design", "different", "discussion", "due", "each", "element", "elements", "engineering",
    "et", "example", "examples", "field", "fields", "final", "first", "for", "form", "forms", "from", "further",
    "general", "given", "good", "has", "have", "however", "if", "illustrated", "in", "including", "independent",
    "into", "introduction", "is", "it", "its", "later", "line", "lines", "local", "main", "means", "method",
    "methods", "model", "models", "more", "most", "new", "non", "note", "of", "on", "one", "only", "open", "or",
    "other", "our", "out", "over", "paper", "papers", "part", "parts", "point", "points", "problem", "problems",
    "procedure", "process", "provides", "related", "respect", "review", "section", "sections", "set", "sets",
    "shown", "simple", "since", "small", "so", "some", "space", "state", "such", "surface", "surfaces", "system",
    "systems", "than", "that", "the", "their", "them", "there", "these", "this", "those", "through", "thus", "to",
    "two", "under", "using", "various", "via", "visible", "we", "well", "where", "which", "while", "with", "within",
    "work", "works",
}
VENUE_ABBREVIATIONS = {
    "Acad",
    "Acta",
    "Adv",
    "Aided",
    "Algorithmica",
    "AMR",
    "Anal",
    "Ann",
    "Appl",
    "Approx",
    "CAD",
    "CGF",
    "Comput",
    "Des",
    "Eng",
    "Engrg",
    "Geom",
    "Graph",
    "Graphics",
    "IEEE",
    "Int",
    "J",
    "Mach",
    "Math",
    "Mech",
    "Methods",
    "Numer",
    "Proc",
    "Proceedings",
    "Sci",
    "SIAM",
    "Struct",
    "Symp",
    "Tech",
    "Trans",
    "Vis",
}
MANUAL_TERMS = {
    "Bezier",
    "Bézier",
    "B-Rep",
    "Catmull-Clark",
    "Clough-Tocher",
    "Coons",
    "Cox",
    "de Boor",
    "Gauss",
    "Greville",
    "isogeometric",
    "Nitsche",
    "NURBS",
    "Nyström",
    "parametrization",
    "reparameterization",
    "spline",
    "splines",
    "tensor-product",
    "T-spline",
    "T-splines",
    "trimmed",
    "trimming",
    "watertight",
}
MANUAL_ACRONYMS = {"CAD", "CAGD", "CSG", "FEA", "IGA", "IGES", "NURBS", "STEP"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a shared corpus lexicon for OCR normalization.")
    parser.add_argument("--dry-run", action="store_true", help="Summarize the lexicon without writing it.")
    return parser.parse_args()


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _add_text_sources(
    text: str,
    *,
    paper_id: str,
    token_counts: Counter[str],
    token_papers: dict[str, set[str]],
    acronym_counts: Counter[str],
    acronym_papers: dict[str, set[str]],
) -> None:
    normalized = _normalize_whitespace(text)
    if not normalized:
        return

    for token in TOKEN_RE.findall(normalized):
        cleaned = token.strip("'-")
        if len(cleaned) < 4:
            continue
        lowered = cleaned.lower()
        if lowered in STOPWORDS:
            continue
        token_counts[cleaned] += 1
        token_papers[cleaned].add(paper_id)

    for acronym in ACRONYM_RE.findall(normalized):
        cleaned = acronym.strip()
        if len(cleaned) < 2:
            continue
        acronym_counts[cleaned] += 1
        acronym_papers[cleaned].add(paper_id)


def _canonical_document_paths(layout: ProjectLayout) -> list[Path]:
    return sorted(layout.corpus_root.glob("*/canonical.json"))


def _collect_canonical_sources(
    token_counts: Counter[str],
    token_papers: dict[str, set[str]],
    acronym_counts: Counter[str],
    acronym_papers: dict[str, set[str]],
    *,
    layout: ProjectLayout,
) -> tuple[Counter[str], dict[str, set[str]], Counter[str], dict[str, set[str]], Counter[str], dict[str, set[str]]]:
    author_counts: Counter[str] = Counter()
    author_papers: dict[str, set[str]] = defaultdict(set)

    for canonical_path in _canonical_document_paths(layout):
        paper_id = canonical_path.parent.name
        document = json.loads(canonical_path.read_text(encoding="utf-8"))

        _add_text_sources(
            str(document.get("title", "")),
            paper_id=paper_id,
            token_counts=token_counts,
            token_papers=token_papers,
            acronym_counts=acronym_counts,
            acronym_papers=acronym_papers,
        )

        for section in document.get("sections", []):
            _add_text_sources(
                str(section.get("title", "")),
                paper_id=paper_id,
                token_counts=token_counts,
                token_papers=token_papers,
                acronym_counts=acronym_counts,
                acronym_papers=acronym_papers,
            )

        for figure in document.get("figures", []):
            _add_text_sources(
                str(figure.get("caption", "")),
                paper_id=paper_id,
                token_counts=token_counts,
                token_papers=token_papers,
                acronym_counts=acronym_counts,
                acronym_papers=acronym_papers,
            )

        for reference in document.get("references", []):
            _add_text_sources(
                str(reference.get("text", "")),
                paper_id=paper_id,
                token_counts=token_counts,
                token_papers=token_papers,
                acronym_counts=acronym_counts,
                acronym_papers=acronym_papers,
            )

        for author in document.get("front_matter", {}).get("authors", []):
            name = _normalize_whitespace(str(author.get("name", "")))
            if not name:
                continue
            author_counts[name] += 1
            author_papers[name].add(paper_id)
            _add_text_sources(
                name,
                paper_id=paper_id,
                token_counts=token_counts,
                token_papers=token_papers,
                acronym_counts=acronym_counts,
                acronym_papers=acronym_papers,
            )

    return token_counts, token_papers, acronym_counts, acronym_papers, author_counts, author_papers


def _term_priority(token: str, count: int, paper_count: int) -> bool:
    lowered = token.lower()
    if token in MANUAL_TERMS or lowered in {value.lower() for value in MANUAL_TERMS}:
        return True
    if token.isdigit() or token in VENUE_ABBREVIATIONS:
        return False
    if len(token) <= 3:
        return False
    if zipf_frequency is not None and zipf_frequency(lowered, "en") > 4.8 and token.islower():
        return False
    if paper_count >= 2 and count >= 2:
        return True
    if zipf_frequency is not None and zipf_frequency(lowered, "en") <= 3.4 and count >= 2:
        return True
    if ("-" in token or any(ord(char) > 127 for char in token)) and count >= 1:
        return True
    return False


def _build_lexicon(*, layout: ProjectLayout | None = None) -> dict[str, Any]:
    active_layout = layout or current_layout()
    token_counts: Counter[str] = Counter()
    token_papers: dict[str, set[str]] = defaultdict(set)
    acronym_counts: Counter[str] = Counter()
    acronym_papers: dict[str, set[str]] = defaultdict(set)
    (
        token_counts,
        token_papers,
        acronym_counts,
        acronym_papers,
        author_counts,
        author_papers,
    ) = _collect_canonical_sources(
        token_counts,
        token_papers,
        acronym_counts,
        acronym_papers,
        layout=active_layout,
    )

    terms: list[dict[str, Any]] = []
    for token, count in sorted(token_counts.items(), key=lambda item: (-item[1], item[0].lower())):
        papers = sorted(token_papers[token])
        if not _term_priority(token, count, len(papers)):
            continue
        terms.append(
            {
                "canonical": token,
                "count": count,
                "papers": papers,
                "variants": [],
            }
        )

    manual_terms_lower = {value.lower() for value in MANUAL_TERMS}
    known_terms_lower = {str(entry["canonical"]).lower() for entry in terms}
    for value in sorted(MANUAL_TERMS, key=str.lower):
        if value.lower() in known_terms_lower:
            continue
        terms.append({"canonical": value, "count": 0, "papers": [], "variants": []})

    acronyms = sorted(
        {
            *MANUAL_ACRONYMS,
            *{
                token
                for token, count in acronym_counts.items()
                if count >= 2 or token in MANUAL_ACRONYMS
            },
        }
    )

    authors = [
        {
            "canonical": name,
            "count": count,
            "papers": sorted(author_papers[name]),
        }
        for name, count in sorted(author_counts.items(), key=lambda item: (-item[1], item[0].lower()))
    ]

    venues = sorted(VENUE_ABBREVIATIONS)
    return {
        "schema_version": 1,
        "sources": {
            "canonical_papers": len(_canonical_document_paths(active_layout)),
        },
        "terms": terms,
        "authors": authors,
        "venues": venues,
        "acronyms": acronyms,
        "symbols": ["Bézier", "Γ", "Ξ", "γ", "∂", "𝛯", "𝕊", "𝜕"],
        "phrase_patterns": [
            "divide-and-conquer",
            "surface-to-surface",
            "point inversion",
            "boundary representation",
            "tensor product",
            "trimmed surfaces",
            "isogeometric analysis",
            "Greville abscissae",
        ],
    }


def main() -> int:
    args = parse_args()
    layout = current_layout()
    lexicon = _build_lexicon(layout=layout)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "terms": len(lexicon.get("terms", [])),
                    "authors": len(lexicon.get("authors", [])),
                    "acronyms": len(lexicon.get("acronyms", [])),
                    "path": str(layout.corpus_lexicon_path),
                },
                indent=2,
            )
        )
        return 0

    layout.corpus_lexicon_path.write_text(json.dumps(lexicon, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "path": str(layout.corpus_lexicon_path),
                "terms": len(lexicon.get("terms", [])),
                "authors": len(lexicon.get("authors", [])),
                "acronyms": len(lexicon.get("acronyms", [])),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main", "_build_lexicon"]
