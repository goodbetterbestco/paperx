from __future__ import annotations

from pipeline.corpus_layout import CORPUS_DIR
from pipeline.text.headings import (
    CONTENTS_ITEM_RE,
    CONTENTS_MARKER_KEYS,
    HEADING_LABEL_RE,
    HeadingInfo,
    MATHY_HEADING_RE,
    SectionNode,
    SINGLE_UPPER_TOKEN_RE,
    STRUCTURAL_HEADINGS,
    SYMBOL_HEAVY_RE,
    TRAILING_PAGE_RE,
    WHITESPACE_RE,
    build_section_tree,
    clean_heading_title,
    collapse_ocr_split_caps,
    compact_text,
    heading_info,
    infer_heading_level,
    is_probable_running_header,
    looks_like_bad_heading,
    looks_like_body_paragraph,
    looks_like_contents_block,
    looks_like_contents_marker,
    looks_like_structural_title,
    normalize_title_key,
    parse_heading_label,
    sort_key,
)


DOCS_DIR = CORPUS_DIR
