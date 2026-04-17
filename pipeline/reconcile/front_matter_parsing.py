from __future__ import annotations

import re
from typing import Any, Callable, Pattern


def looks_like_affiliation(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:department|departament|university|universitat|univ\.|college|school|institute|faculty|sciences|informatics|inform[aà]tics?|polytechnic|polit[eè]cnica|laborator(?:y|ies)|research labs?|center|centre|cnrs|inria|labri|e-?mail|email|austin|usa|hill|carolina|inc\.?|corp(?:oration)?\.?|ltd\.?|llc|gmbh|parkway|street|st\.|road|rd\.|avenue|ave\.|boulevard|blvd\.|drive|dr\.|suite)\b",
            text,
            re.IGNORECASE,
        )
    )


def normalize_author_line(
    text: str,
    *,
    clean_text: Callable[[str], str],
    author_marker_re: Pattern[str],
    author_affiliation_index_re: Pattern[str],
    compact_text: Callable[[str], str],
) -> str:
    normalized = clean_text(text)
    normalized = re.sub(r"^\s*by\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\\\([^)]*\\\)", " ", normalized)
    normalized = author_marker_re.sub(" ", normalized)
    normalized = normalized.replace("∗", " ")
    normalized = normalized.replace("·", " ")
    normalized = normalized.replace("⋅", " ")
    normalized = re.sub(r"(?<=\s)[*'`\"]+(?=\s|$)", " ", normalized)
    normalized = author_affiliation_index_re.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return compact_text(normalized.strip(" ,;:"))


def looks_like_contact_name(
    text: str,
    *,
    clean_text: Callable[[str], str],
    name_token_re: Pattern[str],
) -> bool:
    cleaned = clean_text(text)
    if any(char in cleaned for char in "@:;,[]()"):
        return False
    tokens = name_token_re.findall(cleaned)
    return 2 <= len(tokens) <= 4


def looks_like_front_matter_metadata(
    text: str,
    *,
    clean_text: Callable[[str], str],
    abbreviated_venue_line_re: Pattern[str],
    title_page_metadata_re: Pattern[str],
    front_matter_metadata_re: Pattern[str],
) -> bool:
    cleaned = clean_text(text)
    if not cleaned:
        return False
    if cleaned.lower() == "received":
        return True
    if abbreviated_venue_line_re.search(cleaned):
        return True
    if title_page_metadata_re.search(cleaned) or front_matter_metadata_re.search(cleaned):
        return True
    return False


def looks_like_author_line(
    text: str,
    *,
    looks_like_affiliation: Callable[[str], bool],
    normalize_author_line: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    reference_venue_re: Pattern[str],
    author_token_re: Pattern[str],
) -> bool:
    if looks_like_affiliation(text):
        return False
    normalized = normalize_author_line(text)
    if not normalized or len(normalized) > 140 or normalized.endswith("."):
        return False
    if normalized.startswith("(") and normalized.endswith(")"):
        return False
    if looks_like_front_matter_metadata(normalized):
        return False
    if ":" in normalized:
        return False
    lowered = normalized.lower()
    if "system" in lowered and normalized.startswith("("):
        return False
    if any(token in lowered for token in ("www.", "sciencedirect", "elsevier")):
        return False
    if re.match(r"^(?:using|integrating|analysis|handling|with|for|of|the)\b", lowered):
        return False
    if any(token in normalized.lower() for token in (" abstract ", " contents ", " figure ", " chapter ", " section ")):
        return False
    if len(re.findall(r"\b[A-Za-z]{2,}\.", normalized)) >= 3:
        return False
    if reference_venue_re.search(normalized) and "." in normalized:
        return False
    tokens = author_token_re.findall(normalized)
    max_tokens = 18 if ("," in normalized or " and " in normalized.lower()) else 12
    if not 2 <= len(tokens) <= max_tokens:
        return False
    if normalized.isupper() and len(tokens) > 3:
        return False
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    lowercase_tokens = sum(1 for token in tokens if token.islower())
    return titlecase_like / len(tokens) >= 0.6 and lowercase_tokens <= max(2, len(tokens) // 3)


def parse_authors(
    text: str,
    *,
    clean_text: Callable[[str], str],
    normalize_author_line: Callable[[str], str],
) -> list[dict[str, Any]]:
    raw_text = clean_text(text)
    separated_parts = [
        part.strip(" ,;:")
        for part in re.split(r"\s*[·⋅]\s*|\s+\band\b\s+|\s*,\s*(?=(?:[A-Z]\.\s*)?[A-Z])", raw_text)
        if part.strip(" ,;:")
    ]
    if len(separated_parts) >= 2:
        authors = []
        for part in separated_parts:
            normalized_part = normalize_author_line(part)
            if normalized_part:
                authors.append({"name": normalized_part, "affiliation_ids": ["aff-1"]})
        if authors:
            return authors

    normalized = normalize_author_line(text)
    raw_tokens = normalized.split()
    tokens: list[str] = []
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        if token and token[0].isupper() and token.isalpha() and len(token) <= 5:
            combined = token
            next_index = index + 1
            while next_index < len(raw_tokens):
                next_token = raw_tokens[next_index]
                if not next_token.isalpha() or (next_token and next_token[0].isupper()) or len(combined) >= 7:
                    break
                combined += next_token
                next_index += 1
            tokens.append(combined)
            index = next_index
            continue
        tokens.append(token)
        index += 1
    normalized = " ".join(tokens)
    parts = [part.strip() for part in re.split(r"\s{2,}", normalized) if part.strip()]
    if len(parts) >= 2:
        return [{"name": part, "affiliation_ids": ["aff-1"]} for part in parts]

    tokens = normalized.split()
    if len(tokens) >= 4 and len(tokens) % 2 == 0:
        half = len(tokens) // 2
        return [
            {"name": " ".join(tokens[:half]), "affiliation_ids": ["aff-1"]},
            {"name": " ".join(tokens[half:]), "affiliation_ids": ["aff-1"]},
        ]

    return [{"name": normalized, "affiliation_ids": ["aff-1"]}] if normalized else []


def parse_authors_from_citation_line(
    text: str,
    title: str,
    *,
    clean_text: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
    title_lookup_keys: Callable[[str], list[str]],
    citation_year_re: Pattern[str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    citation_author_split_re: Pattern[str],
    normalize_author_line: Callable[[str], str],
    short_word_re: Pattern[str],
    looks_like_affiliation: Callable[[str], bool],
) -> list[dict[str, Any]]:
    cleaned = clean_text(text)
    if not cleaned:
        return []
    cleaned_key = normalize_title_key(cleaned)
    title_keys = title_lookup_keys(title)
    if not title_keys or not any(title_key in cleaned_key for title_key in title_keys):
        return []
    year_match = citation_year_re.search(cleaned)
    if year_match is None:
        return []

    citation_prefix = cleaned[: year_match.start()].strip(" ,;:")
    if not citation_prefix or looks_like_front_matter_metadata(citation_prefix):
        return []

    citation_prefix = re.sub(r"\s*,\s*&\s*", ", ", citation_prefix)
    citation_prefix = re.sub(r"\s*&\s*", ", ", citation_prefix)
    separated_parts = [
        part.strip(" ,;:")
        for part in citation_author_split_re.split(citation_prefix)
        if part.strip(" ,;:")
    ]
    if len(separated_parts) < 2:
        return []

    authors: list[dict[str, Any]] = []
    for part in separated_parts:
        normalized_part = re.sub(r",\s*(?=[A-Z](?:\.[A-Z])*\.?$)", " ", part)
        normalized_part = normalize_author_line(normalized_part)
        tokens = short_word_re.findall(normalized_part)
        if len(tokens) < 2 or len(tokens) > 6:
            continue
        if looks_like_affiliation(normalized_part) or looks_like_front_matter_metadata(normalized_part):
            continue
        authors.append({"name": normalized_part, "affiliation_ids": ["aff-1"]})
    return authors if len(authors) >= 2 else []


def normalize_affiliation_line(
    text: str,
    *,
    clean_text: Callable[[str], str],
    author_note_re: Pattern[str],
    compact_text: Callable[[str], str],
) -> str:
    normalized = clean_text(text)
    lowered_original = normalized.lower()
    if lowered_original.startswith("email") or lowered_original.startswith("e-mail"):
        return ""
    normalized = re.sub(r"\bE-?mail\s*:\s*[^\s,;]+", " ", normalized, flags=re.IGNORECASE)
    normalized = author_note_re.sub(" ", normalized)
    normalized = re.sub(r"^[*†‡]?\s*\d+\s+", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = compact_text(normalized).strip(" ,;:")
    lowered = normalized.lower()
    if lowered.startswith("e-mail addresses") or lowered.startswith("email") or lowered.startswith("e-mail"):
        return ""
    if lowered in {"com", "edu", "org", "net"}:
        return ""
    return normalized


def looks_like_affiliation_continuation(
    text: str,
    *,
    clean_text: Callable[[str], str],
    looks_like_front_matter_metadata: Callable[[str], bool],
    short_word_re: Pattern[str],
) -> bool:
    cleaned = clean_text(text).strip(" ,;:")
    if not cleaned or looks_like_front_matter_metadata(cleaned):
        return False
    if re.search(r"\d", cleaned):
        return False
    tokens = short_word_re.findall(cleaned)
    if not 1 <= len(tokens) <= 4:
        return False
    titlecase_like = sum(1 for token in tokens if token[:1].isupper())
    return titlecase_like >= max(1, len(tokens) - 1)


def split_affiliation_fields(
    affiliation_lines: list[str],
    *,
    normalize_affiliation_line: Callable[[str], str],
) -> tuple[str, str, str]:
    cleaned_lines = [normalize_affiliation_line(line) for line in affiliation_lines if normalize_affiliation_line(line)]
    if not cleaned_lines:
        return "", "", ""
    if len(cleaned_lines) == 1:
        parts = [part.strip() for part in cleaned_lines[0].split(",") if part.strip()]
        if len(parts) >= 3:
            return parts[0], parts[1], ", ".join(parts[2:])
        return cleaned_lines[0], "", ""
    department = cleaned_lines[0]
    institution = cleaned_lines[1] if len(cleaned_lines) > 1 else ""
    address = " ".join(cleaned_lines[2:]) if len(cleaned_lines) > 2 else ""
    return department, institution, address


def dedupe_authors(
    authors: list[dict[str, Any]],
    *,
    normalize_author_line: Callable[[str], str],
    normalize_title_key: Callable[[str], str],
) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for author in authors:
        name = normalize_author_line(str(author.get("name", "")))
        if not name:
            continue
        key = normalize_title_key(name)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append({"name": name, "affiliation_ids": list(author.get("affiliation_ids", [])) or ["aff-1"]})
    return deduped


def filter_front_matter_authors(
    authors: list[dict[str, Any]],
    *,
    normalize_author_line: Callable[[str], str],
    short_word_re: Pattern[str],
    looks_like_affiliation: Callable[[str], bool],
    looks_like_front_matter_metadata: Callable[[str], bool],
    dedupe_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for author in authors:
        name = normalize_author_line(str(author.get("name", "")))
        if not name:
            continue
        if len(short_word_re.findall(name)) < 2:
            continue
        lowered = name.lower()
        if looks_like_affiliation(name) or looks_like_front_matter_metadata(name):
            continue
        if any(
            token in lowered
            for token in (" university", " institute", " department", " research", " corporate", " laboratory")
        ):
            continue
        filtered.append({"name": name, "affiliation_ids": list(author.get("affiliation_ids", [])) or ["aff-1"]})
    return dedupe_authors(filtered)


def build_affiliations_for_authors(
    author_count: int,
    affiliation_lines: list[str],
    *,
    normalize_affiliation_line: Callable[[str], str],
    split_affiliation_fields: Callable[[list[str]], tuple[str, str, str]],
) -> tuple[list[dict[str, Any]], list[list[str]]]:
    cleaned_lines = [normalize_affiliation_line(line) for line in affiliation_lines if normalize_affiliation_line(line)]
    if not cleaned_lines:
        return [], [[] for _ in range(author_count)]

    if author_count > 1 and len(cleaned_lines) == author_count:
        affiliations: list[dict[str, Any]] = []
        author_affiliation_ids: list[list[str]] = []
        for index, line in enumerate(cleaned_lines, start=1):
            department, institution, address = split_affiliation_fields([line])
            affiliation_id = f"aff-{index}"
            affiliations.append(
                {
                    "id": affiliation_id,
                    "department": department,
                    "institution": institution,
                    "address": address,
                }
            )
            author_affiliation_ids.append([affiliation_id])
        return affiliations, author_affiliation_ids

    department, institution, address = split_affiliation_fields(cleaned_lines)
    affiliations = [
        {
            "id": "aff-1",
            "department": department,
            "institution": institution,
            "address": address,
        }
    ]
    return affiliations, [["aff-1"] for _ in range(author_count)]


def strip_author_prefix_from_affiliation_line(
    text: str,
    authors: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    normalize_author_line: Callable[[str], str],
) -> str:
    cleaned = clean_text(text)
    if not cleaned:
        return ""
    for author in authors:
        author_name = normalize_author_line(str(author.get("name", "")))
        if not author_name:
            continue
        for prefix in (author_name, f"by {author_name}"):
            if cleaned.lower().startswith(prefix.lower() + " "):
                return clean_text(cleaned[len(prefix) :])
    return cleaned
