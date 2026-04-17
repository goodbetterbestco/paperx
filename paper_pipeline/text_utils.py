from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from paper_pipeline.corpus_layout import BIBLIOGRAPHY_PATH, CORPUS_DIR

DOCS_DIR = CORPUS_DIR

HEADING_LABEL_RE = re.compile(r"^(?P<label>(?:\d+|[A-Z])(?:\.(?:\d+|[A-Z]))*)(?:\.)?\s+(?P<title>.+?)\s*$")
TRAILING_PAGE_RE = re.compile(r"^(?P<title>.+?)\s+\d{1,4}$")
WHITESPACE_RE = re.compile(r"\s+")
MATHY_HEADING_RE = re.compile(r"[=<>]|(?:^|\s)[+−-]\s*[A-Za-z0-9(]")
SYMBOL_HEAVY_RE = re.compile(r"[(){}\[\]<>_=+−~/*-]")
SINGLE_UPPER_TOKEN_RE = re.compile(r"^[A-Z]$")
CONTENTS_ITEM_RE = re.compile(r"\b\d+(?:\.\d+){0,2}\b")
STRUCTURAL_HEADINGS = {
    "abstract",
    "acknowledgement",
    "acknowledgements",
    "acknowledgment",
    "acknowledgments",
    "appendix",
    "appendices",
    "background",
    "conclusion",
    "conclusions",
    "discussion",
    "introduction",
    "preliminaries",
    "preliminary",
    "references",
    "summary",
}
CONTENTS_MARKER_KEYS = {
    "contents",
    "tableofcontents",
}


@dataclass
class SectionNode:
    title: str
    level: int
    heading_id: str
    label: tuple[str, ...] | None = None
    records: list[dict[str, Any]] = field(default_factory=list)
    children: list["SectionNode"] = field(default_factory=list)


@dataclass(frozen=True)
class HeadingInfo:
    title: str
    label: tuple[str, ...] | None
    key: str
    repeated_header_candidate: bool


def compact_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.replace("\n", " ")).strip()


def normalize_title_key(text: str) -> str:
    lowered = compact_text(text).lower()
    return re.sub(r"[^a-z0-9]+", "", lowered)


def bibliography_entries() -> list[dict[str, Any]]:
    if not BIBLIOGRAPHY_PATH.exists():
        return []
    obj = json.loads(BIBLIOGRAPHY_PATH.read_text(encoding="utf-8"))
    return list(obj.get("entries", []))


def paper_metadata(paper_id: str) -> dict[str, Any] | None:
    for entry in bibliography_entries():
        if str(entry.get("id", "")) == paper_id:
            return entry
    return None


def collapse_ocr_split_caps(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return text

    merged: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if SINGLE_UPPER_TOKEN_RE.fullmatch(token):
            combined = token
            next_index = index + 1
            while next_index < len(tokens):
                next_token = tokens[next_index]
                letters_only = re.sub(r"[^A-Za-z]", "", next_token)
                if not letters_only or not next_token[0].isupper():
                    break
                if len(next_token) > 1 and not letters_only.isupper():
                    break
                combined += next_token
                next_index += 1
            if len(combined) > len(token):
                merged.append(combined)
                index = next_index
                continue
        merged.append(token)
        index += 1
    return " ".join(merged)


def clean_heading_title(text: str) -> str:
    stripped = compact_text(text)
    trailing_page_match = TRAILING_PAGE_RE.match(stripped)
    if trailing_page_match and re.search(r"[A-Za-z]", trailing_page_match.group("title")):
        stripped = trailing_page_match.group("title").strip()
    stripped = collapse_ocr_split_caps(stripped)
    return compact_text(stripped)


def parse_heading_label(text: str) -> tuple[tuple[str, ...], str] | None:
    match = HEADING_LABEL_RE.match(text)
    if not match:
        return None
    parts = tuple(part for part in match.group("label").split(".") if part)
    title = compact_text(match.group("title"))
    if not parts or not title:
        return None
    return parts, title


def looks_like_structural_title(text: str) -> bool:
    return normalize_title_key(text) in {normalize_title_key(value) for value in STRUCTURAL_HEADINGS}


def looks_like_bad_heading(text: str) -> bool:
    if not text or not re.search(r"[A-Za-z]", text):
        return True

    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        return True

    if len(words) > 18 or len(text) > 140:
        return True

    if len(SYMBOL_HEAVY_RE.findall(text)) >= max(4, len(text) // 4):
        return True

    if MATHY_HEADING_RE.search(text) and len(words) <= 5:
        return True

    lowered = f" {text.lower()} "
    if len(words) >= 8 and any(token in lowered for token in (" is ", " are ", " was ", " were ", " called ", " defined ")):
        return True

    letter_words = [word for word in words if re.search(r"[A-Za-z]", word)]
    if letter_words and sum(1 for word in letter_words if len(word) == 1) >= len(letter_words) // 2 + 1:
        return True

    return False


def is_probable_running_header(cleaned: str, original_text: str) -> bool:
    if TRAILING_PAGE_RE.match(compact_text(original_text)) is None:
        return False
    words = re.findall(r"[A-Za-z]+", cleaned)
    if not words:
        return False
    has_split_caps = bool(re.search(r"\b[A-Z]\s+[A-Z]{2,}", original_text))
    all_upperish = all(word.isupper() or (len(word) == 1 and word.isalpha()) for word in words)
    return has_split_caps or all_upperish


def heading_info(record: dict[str, Any]) -> HeadingInfo | None:
    original_text = compact_text(str(record.get("text", "")))
    cleaned = clean_heading_title(original_text)
    if not cleaned:
        return None

    parsed = parse_heading_label(cleaned)
    if parsed:
        label, title = parsed
        title = collapse_ocr_split_caps(title)
        if looks_like_bad_heading(title):
            return None
        rendered_title = f"{'.'.join(label)} {title}"
        return HeadingInfo(
            title=rendered_title,
            label=label,
            key=normalize_title_key(rendered_title),
            repeated_header_candidate=False,
        )

    if looks_like_bad_heading(cleaned):
        return None

    repeated_header_candidate = is_probable_running_header(cleaned, original_text)
    if repeated_header_candidate or looks_like_structural_title(cleaned):
        normalized_title = cleaned.title() if cleaned.isupper() else cleaned
        return HeadingInfo(
            title=normalized_title,
            label=None,
            key=normalize_title_key(normalized_title),
            repeated_header_candidate=repeated_header_candidate,
        )

    return None


def sort_key(record: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(record.get("page", 0)),
        int(record.get("group_index", 0)),
        int(record.get("split_index", 0)),
    )


def looks_like_contents_block(text: str) -> bool:
    lowered = compact_text(text).lower()
    if "contents" not in lowered:
        return False
    return len(CONTENTS_ITEM_RE.findall(lowered)) >= 5


def looks_like_contents_marker(text: str) -> bool:
    key = normalize_title_key(text)
    if key in CONTENTS_MARKER_KEYS:
        return True
    return bool(re.fullmatch(r"contents\d{1,4}", key))


def looks_like_body_paragraph(record: dict[str, Any]) -> bool:
    if record.get("type") != "paragraph":
        return False
    text = compact_text(str(record.get("text", "")))
    if len(re.findall(r"[A-Za-z0-9]+", text)) < 40:
        return False
    return not looks_like_contents_block(text)


def infer_heading_level(text: str) -> int:
    stripped = clean_heading_title(text)
    parsed = parse_heading_label(stripped)
    if parsed:
        label, _ = parsed
        return len(label)
    return 1


def build_section_tree(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[SectionNode]]:
    ordered = sorted(records, key=sort_key)
    prelude: list[dict[str, Any]] = []
    roots: list[SectionNode] = []
    stack: list[SectionNode] = []
    label_index: dict[tuple[str, ...], SectionNode] = {}
    seen_running_headers: set[str] = set()
    skipping_contents_headings = False

    for record in ordered:
        text = compact_text(str(record.get("text", "")))
        if looks_like_contents_block(text) or looks_like_contents_marker(text):
            skipping_contents_headings = True
            continue

        if skipping_contents_headings:
            if looks_like_body_paragraph(record):
                skipping_contents_headings = False
            else:
                continue

        if record.get("type") == "heading":
            if skipping_contents_headings:
                continue
            info = heading_info(record)
            if info is not None:
                if info.repeated_header_candidate and info.key in seen_running_headers:
                    continue

                node = SectionNode(
                    title=info.title,
                    level=len(info.label) if info.label else infer_heading_level(str(record.get("text", ""))),
                    heading_id=str(record.get("id", "")),
                    label=info.label,
                )

                if info.label:
                    while stack and stack[-1].label and len(stack[-1].label) >= len(info.label):
                        stack.pop()

                    parent = label_index.get(info.label[:-1]) if len(info.label) > 1 else None
                    if parent is not None:
                        parent.children.append(node)
                    else:
                        roots.append(node)

                    stack = [section for section in stack if section.label and len(section.label) < len(info.label)]
                    stack.append(node)
                    label_index[info.label] = node
                else:
                    while stack and stack[-1].level >= node.level:
                        stack.pop()
                    if stack:
                        stack[-1].children.append(node)
                    else:
                        roots.append(node)
                    stack.append(node)

                if info.repeated_header_candidate:
                    seen_running_headers.add(info.key)
                continue

        if stack:
            stack[-1].records.append(record)
        else:
            prelude.append(record)

    return prelude, roots
