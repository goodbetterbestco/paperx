from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pipeline.assembly.canonical_builder import build_canonical_document
from pipeline.assembly.abstract_recovery import (
    recover_missing_front_matter_abstract as assemble_recover_missing_front_matter_abstract,
)
from pipeline.assembly.front_matter_builder import build_front_matter as assemble_front_matter
from pipeline.assembly.front_matter_support import (
    front_block_text as assemble_front_block_text,
    missing_front_matter_affiliation as assemble_missing_front_matter_affiliation,
    missing_front_matter_author as assemble_missing_front_matter_author,
)
from pipeline.assembly.record_block_builder import (
    build_blocks_for_record as assemble_blocks_for_record,
    list_item_marker as assemble_list_item_marker,
    looks_like_real_code_record as assemble_looks_like_real_code_record,
    split_code_lines as assemble_split_code_lines,
)
from pipeline.assembly.section_builder import materialize_sections
from pipeline.assembly.section_support import (
    normalize_section_title as assemble_normalize_section_title,
    section_id as assemble_section_id,
)
from pipeline.config import PipelineConfig, build_pipeline_config
from pipeline.corpus_layout import CORPUS_DIR
from pipeline.math.compile import compile_formulas
from pipeline.sources.external import load_external_layout, load_external_math, load_mathpix_layout
from pipeline.figures.labels import caption_label
from pipeline.math.semantic_policy import annotate_formula_classifications
from pipeline.math.semantic_ir import annotate_formula_semantic_expr
from pipeline.math.review_policy import (
    review_for_algorithm_block_text,
    review_for_math_entry,
    review_for_math_ref_block,
)
from pipeline.normalize_prose import decode_ocr_codepoint_tokens, normalize_prose_text
from pipeline.normalize_references import normalize_reference_text
from pipeline.orchestrator.paper_reconciler import run_paper_pipeline
from pipeline.orchestrator.layout_merge import merge_native_and_external_layout as orchestrate_merge_native_and_external_layout
from pipeline.policies.abstract_quality import MISSING_ABSTRACT_PLACEHOLDER, abstract_quality_flags
from pipeline.reconcile.block_merging import (
    merge_code_records as reconcile_merge_code_records,
    merge_paragraph_blocks as reconcile_merge_paragraph_blocks,
    merge_paragraph_records as reconcile_merge_paragraph_records,
    normalize_footnote_blocks as reconcile_normalize_footnote_blocks,
    suppress_running_header_blocks as reconcile_suppress_running_header_blocks,
)
from pipeline.reconcile.math_suppression import (
    external_math_by_page as reconcile_external_math_by_page,
    looks_like_display_math_echo as reconcile_looks_like_display_math_echo,
    looks_like_leading_display_math_echo as reconcile_looks_like_leading_display_math_echo,
    mark_records_with_external_math_overlap as reconcile_mark_records_with_external_math_overlap,
    overlapping_external_math_entries as reconcile_overlapping_external_math_entries,
    suppress_graphic_display_math_blocks as reconcile_suppress_graphic_display_math_blocks,
    trim_embedded_display_math_from_paragraph as reconcile_trim_embedded_display_math_from_paragraph,
)
from pipeline.reconcile.external_math import (
    inject_external_math_records as reconcile_inject_external_math_records,
    match_external_math_entry as reconcile_match_external_math_entry,
    rect_area as reconcile_rect_area,
    rect_intersection_area as reconcile_rect_intersection_area,
)
from pipeline.reconcile.section_filters import (
    ends_like_clause_lead_in as reconcile_ends_like_clause_lead_in,
    ends_like_short_lead_in as reconcile_ends_like_short_lead_in,
    is_paragraph_like_record as reconcile_is_paragraph_like_record,
    looks_like_running_header_record as reconcile_looks_like_running_header_record,
    looks_like_same_page_column_continuation as reconcile_looks_like_same_page_column_continuation,
    looks_like_table_body_debris as reconcile_looks_like_table_body_debris,
    merge_anchor_spans as reconcile_merge_anchor_spans,
    should_merge_paragraph_records as reconcile_should_merge_paragraph_records,
    starts_like_paragraph_continuation as reconcile_starts_like_paragraph_continuation,
    starts_like_sentence as reconcile_starts_like_sentence,
    starts_like_strong_paragraph_continuation as reconcile_starts_like_strong_paragraph_continuation,
    suppress_embedded_table_headings as reconcile_suppress_embedded_table_headings,
)
from pipeline.reconcile.screening import (
    is_figure_debris as reconcile_is_figure_debris,
    is_short_ocr_fragment as reconcile_is_short_ocr_fragment,
    looks_like_browser_ui_scrap as reconcile_looks_like_browser_ui_scrap,
    looks_like_glyph_noise_cloud as reconcile_looks_like_glyph_noise_cloud,
    looks_like_quoted_identifier_fragment as reconcile_looks_like_quoted_identifier_fragment,
    looks_like_table_marker_cloud as reconcile_looks_like_table_marker_cloud,
    looks_like_vertical_label_cloud as reconcile_looks_like_vertical_label_cloud,
)
from pipeline.reconcile.reference_runtime import (
    extract_reference_records_from_tail_section as reconcile_extract_reference_records_from_tail_section_runtime,
    is_reference_start as reconcile_is_reference_start_runtime,
    looks_like_reference_text as reconcile_looks_like_reference_text_runtime,
    make_reference_entry as reconcile_make_reference_entry_runtime,
    merge_reference_records as reconcile_merge_reference_records_runtime,
    reference_records_from_mathpix_layout as reconcile_reference_records_from_mathpix_layout_runtime,
    split_trailing_reference_records as reconcile_split_trailing_reference_records_runtime,
)
from pipeline.reconcile.front_matter_runtime import (
    abstract_text_is_recoverable as reconcile_abstract_text_is_recoverable_runtime,
    abstract_text_looks_like_metadata as reconcile_abstract_text_looks_like_metadata_runtime,
    clone_record_with_text as reconcile_clone_record_with_text_runtime,
    dedupe_text_lines as reconcile_dedupe_text_lines_runtime,
    first_root_indicates_missing_intro as reconcile_first_root_indicates_missing_intro_runtime,
    leading_abstract_text as reconcile_leading_abstract_text_runtime,
    matches_title_line as reconcile_matches_title_line_runtime,
    opening_abstract_candidate_records as reconcile_opening_abstract_candidate_records_runtime,
    record_width as reconcile_record_width_runtime,
    record_word_count as reconcile_record_word_count_runtime,
    replace_front_matter_abstract_text as reconcile_replace_front_matter_abstract_text_runtime,
    should_replace_front_matter_abstract as reconcile_should_replace_front_matter_abstract_runtime,
    split_late_prelude_for_missing_intro as reconcile_split_late_prelude_for_missing_intro_runtime,
    title_lookup_keys as reconcile_title_lookup_keys_runtime,
)
from pipeline.reconcile.runtime_support import (
    block_source_spans as reconcile_block_source_spans_runtime,
    mathish_ratio as reconcile_mathish_ratio_runtime,
    normalize_formula_display_text as reconcile_normalize_formula_display_text_runtime,
    now_iso as reconcile_now_iso_runtime,
    page_height_map as reconcile_page_height_map_runtime,
)
from pipeline.reconcile.stage_runtime import (
    run_reconcile_pipeline as reconcile_run_reconcile_pipeline_runtime,
)
from pipeline.reconcile.layout_records import (
    absorb_figure_caption_continuations as reconcile_absorb_figure_caption_continuations,
    append_figure_caption_fragment as reconcile_append_figure_caption_fragment,
    figure_label_token as reconcile_figure_label_token,
    layout_record as reconcile_layout_record,
    match_figure_for_caption_record as reconcile_match_figure_for_caption_record,
    merge_layout_and_figure_records as reconcile_merge_layout_and_figure_records,
    normalize_figure_caption_text as reconcile_normalize_figure_caption_text,
    page_one_front_matter_records as reconcile_page_one_front_matter_records,
    record_bbox as reconcile_record_bbox,
    rect_x_overlap_ratio as reconcile_rect_x_overlap_ratio,
    strip_caption_label_prefix as reconcile_strip_caption_label_prefix,
    synthetic_caption_record as reconcile_synthetic_caption_record,
)
from pipeline.reconcile.text_repairs import (
    inline_tex_signal_count as reconcile_inline_tex_signal_count,
    is_mathpix_text_hint_better as reconcile_is_mathpix_text_hint_better,
    looks_like_truncated_prose_lead as reconcile_looks_like_truncated_prose_lead,
    matching_mathpix_text_blocks as reconcile_matching_mathpix_text_blocks,
    mathpix_hint_alignment_text as reconcile_mathpix_hint_alignment_text,
    mathpix_hint_tokens as reconcile_mathpix_hint_tokens,
    mathpix_prose_lead_repair_candidate as reconcile_mathpix_prose_lead_repair_candidate,
    mathpix_text_blocks_by_page as reconcile_mathpix_text_blocks_by_page,
    mathpix_text_candidate_score as reconcile_mathpix_text_candidate_score,
    mathpix_text_hint_candidate as reconcile_mathpix_text_hint_candidate,
    record_union_bbox as reconcile_record_union_bbox,
    repair_record_text_with_mathpix_hints as reconcile_repair_record_text_with_mathpix_hints,
    repair_record_text_with_pdftotext as reconcile_repair_record_text_with_pdftotext,
    should_skip_pdftotext_repair as reconcile_should_skip_pdftotext_repair,
    token_subsequence_index as reconcile_token_subsequence_index,
)
from pipeline.reconcile.text_cleaning import (
    clean_record as reconcile_clean_record,
    clean_text as reconcile_clean_text,
    is_pdftotext_candidate_better as reconcile_is_pdftotext_candidate_better,
    normalize_paragraph_text as reconcile_normalize_paragraph_text,
    record_analysis_text as reconcile_record_analysis_text,
    strip_known_running_header_text as reconcile_strip_known_running_header_text,
    word_count as reconcile_word_count,
)
from pipeline.reconcile.heading_promotion import (
    decode_control_heading_label as reconcile_decode_control_heading_label,
    normalize_decoded_heading_title as reconcile_normalize_decoded_heading_title,
    promote_heading_like_records as reconcile_promote_heading_like_records,
    split_embedded_heading_paragraph as reconcile_split_embedded_heading_paragraph,
)
from pipeline.reconcile.math_fragments import (
    looks_like_math_fragment as reconcile_looks_like_math_fragment,
    math_signal_count as reconcile_math_signal_count,
    merge_math_fragment_records as reconcile_merge_math_fragment_records,
    strong_operator_count as reconcile_strong_operator_count,
)
from pipeline.reconcile.math_entry_policies import (
    group_entry_items_are_graphic_only as reconcile_group_entry_items_are_graphic_only,
    math_entry_category as reconcile_math_entry_category,
    math_entry_looks_like_prose as reconcile_math_entry_looks_like_prose,
    math_entry_semantic_policy as reconcile_math_entry_semantic_policy,
    paragraph_block_from_graphic_math_entry as reconcile_paragraph_block_from_graphic_math_entry,
    should_demote_graphic_math_entry_to_paragraph as reconcile_should_demote_graphic_math_entry_to_paragraph,
    should_demote_prose_math_entry_to_paragraph as reconcile_should_demote_prose_math_entry_to_paragraph,
    should_drop_display_math_artifact as reconcile_should_drop_display_math_artifact,
)
from pipeline.reconcile.front_matter_parsing import (
    build_affiliations_for_authors as reconcile_build_affiliations_for_authors,
    dedupe_authors as reconcile_dedupe_authors,
    filter_front_matter_authors as reconcile_filter_front_matter_authors,
    looks_like_affiliation as reconcile_looks_like_affiliation,
    looks_like_affiliation_continuation as reconcile_looks_like_affiliation_continuation,
    looks_like_author_line as reconcile_looks_like_author_line,
    looks_like_contact_name as reconcile_looks_like_contact_name,
    looks_like_front_matter_metadata as reconcile_looks_like_front_matter_metadata,
    normalize_affiliation_line as reconcile_normalize_affiliation_line,
    normalize_author_line as reconcile_normalize_author_line,
    parse_authors as reconcile_parse_authors,
    parse_authors_from_citation_line as reconcile_parse_authors_from_citation_line,
    split_affiliation_fields as reconcile_split_affiliation_fields,
    strip_author_prefix_from_affiliation_line as reconcile_strip_author_prefix_from_affiliation_line,
)
from pipeline.reconcile.front_matter_policies import (
    abstract_text_is_usable as reconcile_abstract_text_is_usable,
    is_title_page_metadata_record as reconcile_is_title_page_metadata_record,
    looks_like_body_section_marker as reconcile_looks_like_body_section_marker,
    looks_like_intro_marker as reconcile_looks_like_intro_marker,
    looks_like_page_one_front_matter_tail as reconcile_looks_like_page_one_front_matter_tail,
    normalize_abstract_candidate_text as reconcile_normalize_abstract_candidate_text,
    split_leading_front_matter_records as reconcile_split_leading_front_matter_records,
    strip_trailing_abstract_boilerplate as reconcile_strip_trailing_abstract_boilerplate,
)
from pipeline.reconcile.section_preparation import (
    attach_orphan_numbered_roots,
    prepare_section_nodes,
)
from pipeline.selectors.abstract_selector import build_abstract_decision
from pipeline.text_utils import (
    SectionNode,
    build_section_tree,
    clean_heading_title,
    collapse_ocr_split_caps,
    compact_text,
    looks_like_bad_heading,
    normalize_title_key,
    parse_heading_label,
)
from pipeline.state import PaperState
from pipeline.types import LayoutBlock, default_review
from pipeline.sources.figures import extract_figures
from pipeline.sources.layout import extract_layout
from pipeline.sources.pdftotext import (
    bbox_to_line_window,
    extract_pdftotext_pages,
    pdftotext_available,
    slice_page_text,
)
from pipeline.math.extract import (
    INLINE_MATH_RE,
    build_block_math_entry,
    classify_math_block,
    extract_general_inline_math_spans,
    looks_like_prose_paragraph,
    looks_like_prose_math_fragment,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    repair_symbolic_ocr_spans,
    split_inline_math,
)


ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = CORPUS_DIR
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
FUNDING_RE = re.compile(r"supp\s*orted\s+in\s+part|supported\s+in\s+part", re.IGNORECASE)
NAME_TOKEN_RE = re.compile(r"[A-Z][a-z]+")
AUTHOR_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'`-]*")
SHORT_WORD_RE = re.compile(r"[A-Za-z0-9]+")
MATHPIX_HINT_TOKEN_RE = re.compile(r"[A-Za-z]{1,}")
MATH_TOKEN_RE = re.compile(r"\b(?:Det|Diag|X|Y|Z|W|N|M|D|u|v|s|t|q|A)\b")
DIAGRAM_DECISION_RE = re.compile(r"^(?:start|stop|yes|no|yes yes|yes no|no yes)\b", re.IGNORECASE)
DIAGRAM_QUERY_RE = re.compile(r"^(?:is there|are there|whether)\b", re.IGNORECASE)
DIAGRAM_ACTION_RE = re.compile(r"^(?:search entity|extract\b|label\b|define\b|set\b|filter out\b)", re.IGNORECASE)
LABEL_CLOUD_TOKEN_RE = re.compile(r"^(?:\([A-Za-z]\)|[A-Za-z]{1,2}\d{1,3}|\d+[A-Za-z]{0,2}|[A-Za-z]{1,3}|\d{1,3})$")
QUOTED_IDENTIFIER_FRAGMENT_RE = re.compile(r'^"?[A-Za-z]+(?:_[A-Za-z]+){1,8}"?\s*[?;:]?$')
RUNNING_HEADER_TEXT_RE = re.compile(r"^[A-Z][A-Z\s.-]{2,}$")
PROCEDIA_RUNNING_HEADER_RE = re.compile(
    r"\b(?:Author name\s+Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000|"
    r"Procedia\s+CIRP\s+00\s+\(\d{4}\)\s+000-000\s+Procedia\s+CIRP\s+\d+\s+\(\d{4}\)\s+\d+-\d+)\b",
    re.IGNORECASE,
)
REFERENCE_START_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{0,12}\b")
REFERENCE_AUTHOR_RE = re.compile(r"^(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+(?:\s+(?:[A-Z]\.\s*)?[A-Z][A-Za-z'`-]+)*[.,]")
REFERENCE_YEAR_RE = re.compile(r"\b(?:18|19|20)\d{2}[a-z]?\b", re.IGNORECASE)
REFERENCE_VENUE_RE = re.compile(
    r"\b(?:press|springer|elsevier|journal|transactions|conference|proceedings|proc\.|siggraph|eurographics|ieee|acm|forum|doi|isbn|issn|pages?|vol\.|volume|technical report|workshop)\b",
    re.IGNORECASE,
)
ABOUT_AUTHOR_RE = re.compile(r"^\s*about the author\b", re.IGNORECASE)
TABLE_CAPTION_RE = re.compile(r"^\s*table\b", re.IGNORECASE)
TERMINAL_PUNCTUATION_RE = re.compile(r"[.!?:]\)?[\"']?$")
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
LEADING_OCR_MARKER_RE = re.compile(r"^(?:;\s*1|1)\s+(?=[A-Z])")
LEADING_PUNCT_ARTIFACT_RE = re.compile(r"^[;,:]\s+(?=[A-Za-z])")
LEADING_VAR_ARTIFACT_RE = re.compile(r"^[a-z]\s+(?=(?:On|The|Since|where)\b)")
TRAILING_NUMERIC_ARTIFACT_RE = re.compile(r"(?<=\.)\s+\d+(?:\s+\d+)+\s*$")
LEADING_NEGATIONSLASH_ARTIFACT_RE = re.compile(r"^(?:negationslash\s+)+", re.IGNORECASE)
SHORT_OCR_NOISE_RE = re.compile(
    r"^(?:[;:.,\-\s0-9]+|[a-z]\s+[a-z]|[a-z]{1,3}-[a-z]{1,3}|[\d\sA-Za-z]*[^\x00-\x7f][\d\sA-Za-z]*)$"
)
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
TRUNCATED_PROSE_LEAD_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "these",
    "this",
    "those",
    "to",
    "we",
    "where",
    "with",
}


def _now_iso() -> str:
    return reconcile_now_iso_runtime()


def _clean_text(text: str) -> str:
    return reconcile_clean_text(
        text,
        control_char_re=CONTROL_CHAR_RE,
        compact_text=compact_text,
    )


def _strip_known_running_header_text(text: str) -> str:
    return reconcile_strip_known_running_header_text(
        text,
        procedia_running_header_re=PROCEDIA_RUNNING_HEADER_RE,
        clean_text=_clean_text,
    )


def _block_source_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
    return reconcile_block_source_spans_runtime(record)


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    return reconcile_clean_record(
        record,
        strip_known_running_header_text=_strip_known_running_header_text,
    )


def _normalize_paragraph_text(text: str) -> str:
    return reconcile_normalize_paragraph_text(
        text,
        strip_known_running_header_text=_strip_known_running_header_text,
        leading_negationslash_artifact_re=LEADING_NEGATIONSLASH_ARTIFACT_RE,
        leading_ocr_marker_re=LEADING_OCR_MARKER_RE,
        leading_punct_artifact_re=LEADING_PUNCT_ARTIFACT_RE,
        leading_var_artifact_re=LEADING_VAR_ARTIFACT_RE,
        trailing_numeric_artifact_re=TRAILING_NUMERIC_ARTIFACT_RE,
        normalize_prose_text=normalize_prose_text,
        clean_text=_clean_text,
    )


def _math_entry_semantic_policy(entry: dict[str, Any]) -> str:
    return reconcile_math_entry_semantic_policy(entry)


def _math_entry_category(entry: dict[str, Any]) -> str:
    return reconcile_math_entry_category(entry)


def _group_entry_items_are_graphic_only(entry: dict[str, Any]) -> bool:
    return reconcile_group_entry_items_are_graphic_only(
        entry,
        math_entry_semantic_policy=_math_entry_semantic_policy,
    )


def _math_entry_looks_like_prose(entry: dict[str, Any]) -> bool:
    return reconcile_math_entry_looks_like_prose(
        entry,
        normalize_paragraph_text=_normalize_paragraph_text,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
        looks_like_prose_math_fragment=looks_like_prose_math_fragment,
        word_count=_word_count,
    )


def _should_demote_prose_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
    return reconcile_should_demote_prose_math_entry_to_paragraph(
        entry,
        normalize_paragraph_text=_normalize_paragraph_text,
        word_count=_word_count,
        strong_operator_count=_strong_operator_count,
        mathish_ratio=_mathish_ratio,
        math_entry_looks_like_prose=_math_entry_looks_like_prose,
        math_entry_semantic_policy=_math_entry_semantic_policy,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
    )


def _should_demote_graphic_math_entry_to_paragraph(entry: dict[str, Any]) -> bool:
    return reconcile_should_demote_graphic_math_entry_to_paragraph(
        entry,
        should_demote_prose_math_entry_to_paragraph=_should_demote_prose_math_entry_to_paragraph,
    )


def _should_drop_display_math_artifact(entry: dict[str, Any]) -> bool:
    return reconcile_should_drop_display_math_artifact(
        entry,
        should_demote_graphic_math_entry_to_paragraph=_should_demote_graphic_math_entry_to_paragraph,
        group_entry_items_are_graphic_only=_group_entry_items_are_graphic_only,
        math_entry_semantic_policy=_math_entry_semantic_policy,
        math_entry_category=_math_entry_category,
    )


def _paragraph_block_from_graphic_math_entry(
    block: dict[str, Any],
    math_entry: dict[str, Any],
    counters: dict[str, int],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    return reconcile_paragraph_block_from_graphic_math_entry(
        block,
        math_entry,
        counters,
        normalize_paragraph_text=_normalize_paragraph_text,
        split_inline_math=split_inline_math,
        repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=normalize_inline_math_spans,
        default_review=default_review,
    )


def _normalize_formula_display_text(text: str) -> str:
    return reconcile_normalize_formula_display_text_runtime(
        text,
        clean_text=_clean_text,
        decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
    )


def _normalize_figure_caption_text(text: str) -> str:
    return reconcile_normalize_figure_caption_text(
        text,
        clean_text=_clean_text,
        normalize_prose_text=normalize_prose_text,
    )


def _mathish_ratio(text: str) -> float:
    return reconcile_mathish_ratio_runtime(
        text,
        word_count=_word_count,
        math_signal_count=_math_signal_count,
    )


def _record_analysis_text(record: dict[str, Any]) -> str:
    return reconcile_record_analysis_text(
        record,
        clean_text=_clean_text,
    )


def _word_count(text: str) -> int:
    return reconcile_word_count(text, short_word_re=SHORT_WORD_RE)


def _page_height_map(layout: dict[str, Any]) -> dict[int, float]:
    return reconcile_page_height_map_runtime(layout)


def _is_pdftotext_candidate_better(original_text: str, candidate_text: str, record_type: str) -> bool:
    return reconcile_is_pdftotext_candidate_better(
        original_text,
        candidate_text,
        record_type,
        clean_text=_clean_text,
        word_count=_word_count,
    )


def _should_skip_pdftotext_repair(record: dict[str, Any]) -> bool:
    return reconcile_should_skip_pdftotext_repair(
        record,
        clean_text=_clean_text,
        word_count=_word_count,
        inline_math_re=INLINE_MATH_RE,
    )


def _repair_record_text_with_pdftotext(
    records: list[dict[str, Any]],
    pdftotext_pages: dict[int, list[str]],
    page_heights: dict[int, float],
) -> list[dict[str, Any]]:
    return reconcile_repair_record_text_with_pdftotext(
        records,
        pdftotext_pages,
        page_heights,
        should_skip_pdftotext_repair=_should_skip_pdftotext_repair,
        block_source_spans=_block_source_spans,
        bbox_to_line_window=bbox_to_line_window,
        slice_page_text=slice_page_text,
        clean_text=_clean_text,
        is_pdftotext_candidate_better=_is_pdftotext_candidate_better,
    )


def _mathpix_text_blocks_by_page(layout: dict[str, Any]) -> dict[int, list[LayoutBlock]]:
    return reconcile_mathpix_text_blocks_by_page(layout)


def _record_union_bbox(record: dict[str, Any]) -> tuple[int, dict[str, float]] | None:
    return reconcile_record_union_bbox(record, block_source_spans=_block_source_spans)


def _inline_tex_signal_count(text: str) -> int:
    return reconcile_inline_tex_signal_count(text)


def _mathpix_hint_alignment_text(text: str) -> str:
    return reconcile_mathpix_hint_alignment_text(
        text,
        clean_text=_clean_text,
        display_math_prose_cue_re=DISPLAY_MATH_PROSE_CUE_RE,
        display_math_start_re=DISPLAY_MATH_START_RE,
        math_signal_count=_math_signal_count,
        word_count=_word_count,
    )


def _mathpix_hint_tokens(text: str) -> list[str]:
    return reconcile_mathpix_hint_tokens(text, hint_token_re=MATHPIX_HINT_TOKEN_RE)


def _mathpix_text_candidate_score(original_text: str, candidate_text: str) -> tuple[int, int, int, int]:
    return reconcile_mathpix_text_candidate_score(
        original_text,
        candidate_text,
        mathpix_hint_alignment_text=_mathpix_hint_alignment_text,
        mathpix_hint_tokens=_mathpix_hint_tokens,
        inline_tex_signal_count=_inline_tex_signal_count,
    )


def _matching_mathpix_text_blocks(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
) -> list[LayoutBlock]:
    return reconcile_matching_mathpix_text_blocks(
        record,
        mathpix_blocks_by_page,
        record_union_bbox=_record_union_bbox,
        rect_x_overlap_ratio=_rect_x_overlap_ratio,
    )


def _mathpix_text_hint_candidate(record: dict[str, Any], mathpix_blocks_by_page: dict[int, list[LayoutBlock]]) -> str:
    return reconcile_mathpix_text_hint_candidate(
        record,
        mathpix_blocks_by_page,
        matching_mathpix_text_blocks=_matching_mathpix_text_blocks,
        word_count=_word_count,
        mathpix_hint_alignment_text=_mathpix_hint_alignment_text,
        clean_text=_clean_text,
        mathpix_text_candidate_score=_mathpix_text_candidate_score,
    )


def _looks_like_truncated_prose_lead(text: str) -> bool:
    return reconcile_looks_like_truncated_prose_lead(
        text,
        clean_text=_clean_text,
        short_word_re=SHORT_WORD_RE,
        truncated_prose_lead_stopwords=TRUNCATED_PROSE_LEAD_STOPWORDS,
    )


def _token_subsequence_index(tokens: list[str], needle: list[str]) -> int | None:
    return reconcile_token_subsequence_index(tokens, needle)


def _mathpix_prose_lead_repair_candidate(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
) -> str:
    return reconcile_mathpix_prose_lead_repair_candidate(
        record,
        mathpix_blocks_by_page,
        clean_text=_clean_text,
        looks_like_truncated_prose_lead=_looks_like_truncated_prose_lead,
        matching_mathpix_text_blocks=_matching_mathpix_text_blocks,
        short_word_re=SHORT_WORD_RE,
        word_count=_word_count,
        parse_heading_label=parse_heading_label,
        token_subsequence_index=_token_subsequence_index,
    )


def _is_mathpix_text_hint_better(original_text: str, candidate_text: str) -> bool:
    return reconcile_is_mathpix_text_hint_better(
        original_text,
        candidate_text,
        clean_text=_clean_text,
        word_count=_word_count,
        inline_tex_signal_count=_inline_tex_signal_count,
    )


def _page_one_front_matter_records(
    records: list[dict[str, Any]],
    mathpix_layout: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    return reconcile_page_one_front_matter_records(
        records,
        mathpix_layout,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
        mathpix_text_blocks_by_page=_mathpix_text_blocks_by_page,
        layout_record=_layout_record,
    )


def _layout_record(block: LayoutBlock) -> dict[str, Any]:
    return reconcile_layout_record(
        block,
        clean_text=_clean_text,
    )


def _figure_label_token(figure: dict[str, Any]) -> str | None:
    return reconcile_figure_label_token(figure)


def _synthetic_caption_record(figure: dict[str, Any], page_blocks: list[LayoutBlock]) -> dict[str, Any]:
    return reconcile_synthetic_caption_record(figure, page_blocks)


def _record_bbox(record: dict[str, Any]) -> dict[str, Any]:
    return reconcile_record_bbox(record, block_source_spans=_block_source_spans)


def _rect_x_overlap_ratio(a: dict[str, Any], b: dict[str, Any]) -> float:
    return reconcile_rect_x_overlap_ratio(a, b)


def _strip_caption_label_prefix(text: str, figure: dict[str, Any] | None = None) -> str:
    return reconcile_strip_caption_label_prefix(
        text,
        clean_text=_clean_text,
        figure=figure,
    )


def _append_figure_caption_fragment(figure: dict[str, Any], fragment: str) -> None:
    return reconcile_append_figure_caption_fragment(
        figure,
        fragment,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
        normalize_figure_caption_text=_normalize_figure_caption_text,
        strip_caption_label_prefix=_strip_caption_label_prefix,
    )


def _match_figure_for_caption_record(record: dict[str, Any], figures_on_page: list[dict[str, Any]]) -> dict[str, Any] | None:
    return reconcile_match_figure_for_caption_record(
        record,
        figures_on_page,
        record_bbox=_record_bbox,
        rect_x_overlap_ratio=_rect_x_overlap_ratio,
        figure_label_token=_figure_label_token,
    )


def _absorb_figure_caption_continuations(
    records: list[dict[str, Any]],
    figures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return reconcile_absorb_figure_caption_continuations(
        records,
        figures,
        match_figure_for_caption_record=_match_figure_for_caption_record,
        append_figure_caption_fragment=_append_figure_caption_fragment,
    )


def _inject_external_math_records(
    records: list[dict[str, Any]],
    layout_blocks: list[LayoutBlock],
    external_math_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[str]]:
    return reconcile_inject_external_math_records(
        records,
        layout_blocks,
        external_math_entries,
        clean_text=_clean_text,
        looks_like_leading_display_math_echo=lambda text: reconcile_looks_like_leading_display_math_echo(
            text,
            clean_text=_clean_text,
            display_math_prose_cue_re=DISPLAY_MATH_PROSE_CUE_RE,
            mathish_ratio=_mathish_ratio,
            strong_operator_count=_strong_operator_count,
        ),
    )


def _decode_control_heading_label(text: str) -> tuple[str | None, str]:
    return reconcile_decode_control_heading_label(text)


def _normalize_decoded_heading_title(title: str) -> str:
    return reconcile_normalize_decoded_heading_title(
        title,
        clean_text=_clean_text,
        clean_heading_title=clean_heading_title,
    )


def _split_embedded_heading_paragraph(record: dict[str, Any]) -> tuple[str, str] | None:
    return reconcile_split_embedded_heading_paragraph(
        record,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        embedded_heading_prefix_re=EMBEDDED_HEADING_PREFIX_RE,
        normalize_decoded_heading_title=_normalize_decoded_heading_title,
        collapse_ocr_split_caps=collapse_ocr_split_caps,
        looks_like_bad_heading=looks_like_bad_heading,
        short_word_re=SHORT_WORD_RE,
    )


def _looks_like_math_fragment(record: dict[str, Any]) -> bool:
    return reconcile_looks_like_math_fragment(
        record,
        record_analysis_text=_record_analysis_text,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
        short_word_re=SHORT_WORD_RE,
        math_token_re=MATH_TOKEN_RE,
    )


def _math_signal_count(text: str) -> int:
    return reconcile_math_signal_count(text, math_token_re=MATH_TOKEN_RE)


def _strong_operator_count(text: str) -> int:
    return reconcile_strong_operator_count(text)


def _looks_like_vertical_label_cloud(text: str, spans: list[dict[str, Any]]) -> bool:
    return reconcile_looks_like_vertical_label_cloud(
        text,
        spans,
        strong_operator_count=_strong_operator_count,
    )


def _looks_like_table_marker_cloud(text: str, spans: list[dict[str, Any]]) -> bool:
    return reconcile_looks_like_table_marker_cloud(
        text,
        spans,
        strong_operator_count=_strong_operator_count,
    )


def _looks_like_browser_ui_scrap(text: str) -> bool:
    return reconcile_looks_like_browser_ui_scrap(text, short_word_re=SHORT_WORD_RE)


def _looks_like_quoted_identifier_fragment(text: str) -> bool:
    return reconcile_looks_like_quoted_identifier_fragment(
        text,
        short_word_re=SHORT_WORD_RE,
        quoted_identifier_fragment_re=QUOTED_IDENTIFIER_FRAGMENT_RE,
    )


def _looks_like_glyph_noise_cloud(text: str) -> bool:
    return reconcile_looks_like_glyph_noise_cloud(text, short_word_re=SHORT_WORD_RE)


def _merge_math_fragment_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_merge_math_fragment_records(
        records,
        looks_like_math_fragment=_looks_like_math_fragment,
        clean_text=_clean_text,
        record_analysis_text=_record_analysis_text,
        math_signal_count=_math_signal_count,
        block_source_spans=_block_source_spans,
    )


def _looks_like_affiliation(text: str) -> bool:
    return reconcile_looks_like_affiliation(text)


def _looks_like_author_line(text: str) -> bool:
    return reconcile_looks_like_author_line(
        text,
        looks_like_affiliation=_looks_like_affiliation,
        normalize_author_line=_normalize_author_line,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        reference_venue_re=REFERENCE_VENUE_RE,
        author_token_re=AUTHOR_TOKEN_RE,
    )


def _normalize_author_line(text: str) -> str:
    return reconcile_normalize_author_line(
        text,
        clean_text=_clean_text,
        author_marker_re=AUTHOR_MARKER_RE,
        author_affiliation_index_re=AUTHOR_AFFILIATION_INDEX_RE,
        compact_text=compact_text,
    )


def _looks_like_contact_name(text: str) -> bool:
    return reconcile_looks_like_contact_name(
        text,
        clean_text=_clean_text,
        name_token_re=NAME_TOKEN_RE,
    )


def _looks_like_front_matter_metadata(text: str) -> bool:
    return reconcile_looks_like_front_matter_metadata(
        text,
        clean_text=_clean_text,
        abbreviated_venue_line_re=ABBREVIATED_VENUE_LINE_RE,
        title_page_metadata_re=TITLE_PAGE_METADATA_RE,
        front_matter_metadata_re=FRONT_MATTER_METADATA_RE,
    )


def _looks_like_intro_marker(text: str) -> bool:
    return reconcile_looks_like_intro_marker(
        text,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
        intro_marker_re=INTRO_MARKER_RE,
    )


def _looks_like_body_section_marker(text: str) -> bool:
    return reconcile_looks_like_body_section_marker(
        text,
        clean_text=_clean_text,
        clean_heading_title=clean_heading_title,
        abstract_marker_only_re=ABSTRACT_MARKER_ONLY_RE,
        abstract_lead_re=ABSTRACT_LEAD_RE,
        looks_like_intro_marker=_looks_like_intro_marker,
        normalize_title_key=normalize_title_key,
        parse_heading_label=parse_heading_label,
    )


def _strip_trailing_abstract_boilerplate(text: str) -> str:
    return reconcile_strip_trailing_abstract_boilerplate(
        text,
        clean_text=_clean_text,
        compact_text=compact_text,
        trailing_abstract_boilerplate_re=TRAILING_ABSTRACT_BOILERPLATE_RE,
        trailing_abstract_tail_re=TRAILING_ABSTRACT_TAIL_RE,
    )


def _normalize_abstract_candidate_text(records: list[dict[str, Any]]) -> str:
    return reconcile_normalize_abstract_candidate_text(
        records,
        clean_text=_clean_text,
        preprint_marker_re=PREPRINT_MARKER_RE,
        abstract_lead_re=ABSTRACT_LEAD_RE,
        strip_trailing_abstract_boilerplate=_strip_trailing_abstract_boilerplate,
    )


def _abstract_text_is_usable(text: str) -> bool:
    return reconcile_abstract_text_is_usable(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def _looks_like_page_one_front_matter_tail(record: dict[str, Any]) -> bool:
    return reconcile_looks_like_page_one_front_matter_tail(
        record,
        clean_text=_clean_text,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        looks_like_author_line=_looks_like_author_line,
        looks_like_affiliation=_looks_like_affiliation,
        looks_like_contact_name=_looks_like_contact_name,
        short_word_re=SHORT_WORD_RE,
    )


def _split_leading_front_matter_records(prelude: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_split_leading_front_matter_records(
        prelude,
        clean_text=_clean_text,
        looks_like_intro_marker=_looks_like_intro_marker,
        looks_like_page_one_front_matter_tail=_looks_like_page_one_front_matter_tail,
    )


def _parse_authors(text: str) -> list[dict[str, Any]]:
    return reconcile_parse_authors(
        text,
        clean_text=_clean_text,
        normalize_author_line=_normalize_author_line,
    )


def _parse_authors_from_citation_line(text: str, title: str) -> list[dict[str, Any]]:
    return reconcile_parse_authors_from_citation_line(
        text,
        title,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
        title_lookup_keys=_title_lookup_keys,
        citation_year_re=CITATION_YEAR_RE,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        citation_author_split_re=CITATION_AUTHOR_SPLIT_RE,
        normalize_author_line=_normalize_author_line,
        short_word_re=SHORT_WORD_RE,
        looks_like_affiliation=_looks_like_affiliation,
    )


def _is_title_page_metadata_record(record: dict[str, Any]) -> bool:
    return reconcile_is_title_page_metadata_record(
        record,
        clean_text=_clean_text,
        preprint_marker_re=PREPRINT_MARKER_RE,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        author_note_re=AUTHOR_NOTE_RE,
        block_source_spans=_block_source_spans,
        looks_like_affiliation=_looks_like_affiliation,
        looks_like_contact_name=_looks_like_contact_name,
    )


def _normalize_affiliation_line(text: str) -> str:
    return reconcile_normalize_affiliation_line(
        text,
        clean_text=_clean_text,
        author_note_re=AUTHOR_NOTE_RE,
        compact_text=compact_text,
    )


def _looks_like_affiliation_continuation(text: str) -> bool:
    return reconcile_looks_like_affiliation_continuation(
        text,
        clean_text=_clean_text,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        short_word_re=SHORT_WORD_RE,
    )


def _split_affiliation_fields(affiliation_lines: list[str]) -> tuple[str, str, str]:
    return reconcile_split_affiliation_fields(
        affiliation_lines,
        normalize_affiliation_line=_normalize_affiliation_line,
    )


def _dedupe_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_dedupe_authors(
        authors,
        normalize_author_line=_normalize_author_line,
        normalize_title_key=normalize_title_key,
    )


def _filter_front_matter_authors(authors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_filter_front_matter_authors(
        authors,
        normalize_author_line=_normalize_author_line,
        short_word_re=SHORT_WORD_RE,
        looks_like_affiliation=_looks_like_affiliation,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        dedupe_authors=_dedupe_authors,
    )


def _build_affiliations_for_authors(author_count: int, affiliation_lines: list[str]) -> tuple[list[dict[str, Any]], list[list[str]]]:
    return reconcile_build_affiliations_for_authors(
        author_count,
        affiliation_lines,
        normalize_affiliation_line=_normalize_affiliation_line,
        split_affiliation_fields=_split_affiliation_fields,
    )


FRONT_MATTER_MISSING_PLACEHOLDER = MISSING_ABSTRACT_PLACEHOLDER


def _missing_front_matter_author() -> dict[str, Any]:
    return assemble_missing_front_matter_author(FRONT_MATTER_MISSING_PLACEHOLDER)


def _missing_front_matter_affiliation() -> dict[str, Any]:
    return assemble_missing_front_matter_affiliation(FRONT_MATTER_MISSING_PLACEHOLDER)


def _strip_author_prefix_from_affiliation_line(text: str, authors: list[dict[str, Any]]) -> str:
    return reconcile_strip_author_prefix_from_affiliation_line(
        text,
        authors,
        clean_text=_clean_text,
        normalize_author_line=_normalize_author_line,
    )


def _title_lookup_keys(title: str) -> list[str]:
    return reconcile_title_lookup_keys_runtime(
        title,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
    )


def _matches_title_line(text: str, title: str) -> bool:
    return reconcile_matches_title_line_runtime(
        text,
        title,
        clean_text=_clean_text,
        compact_text=compact_text,
        short_word_re=SHORT_WORD_RE,
        normalize_title_key=normalize_title_key,
        title_lookup_keys=_title_lookup_keys,
    )


def _dedupe_text_lines(lines: list[str]) -> list[str]:
    return reconcile_dedupe_text_lines_runtime(
        lines,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
    )


def _clone_record_with_text(record: dict[str, Any], text: str) -> dict[str, Any]:
    return reconcile_clone_record_with_text_runtime(record, text, clean_text=_clean_text)


def _record_word_count(record: dict[str, Any]) -> int:
    return reconcile_record_word_count_runtime(
        record,
        clean_text=_clean_text,
        short_word_re=SHORT_WORD_RE,
    )


def _record_width(record: dict[str, Any]) -> float:
    return reconcile_record_width_runtime(record, block_source_spans=_block_source_spans)


def _abstract_text_looks_like_metadata(text: str) -> bool:
    return reconcile_abstract_text_looks_like_metadata_runtime(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def _should_replace_front_matter_abstract(text: str) -> bool:
    return reconcile_should_replace_front_matter_abstract_runtime(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def _leading_abstract_text(node: SectionNode) -> tuple[str, list[dict[str, Any]]]:
    return reconcile_leading_abstract_text_runtime(
        node,
        clean_text=_clean_text,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        keywords_lead_re=KEYWORDS_LEAD_RE,
        author_note_re=AUTHOR_NOTE_RE,
        abstract_body_break_re=ABSTRACT_BODY_BREAK_RE,
        figure_ref_re=FIGURE_REF_RE,
        abstract_continuation_re=ABSTRACT_CONTINUATION_RE,
        record_word_count=_record_word_count,
        normalize_abstract_candidate_text=_normalize_abstract_candidate_text,
    )


def _opening_abstract_candidate_records(prelude: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_opening_abstract_candidate_records_runtime(
        prelude,
        clean_text=_clean_text,
        abstract_lead_re=ABSTRACT_LEAD_RE,
        looks_like_body_section_marker=_looks_like_body_section_marker,
        keywords_lead_re=KEYWORDS_LEAD_RE,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        record_word_count=_record_word_count,
    )


def _abstract_text_is_recoverable(text: str) -> bool:
    return reconcile_abstract_text_is_recoverable_runtime(
        text,
        abstract_quality_flags=abstract_quality_flags,
    )


def _replace_front_matter_abstract_text(
    front_matter: dict[str, Any],
    blocks: list[dict[str, Any]],
    abstract_text: str,
    abstract_records: list[dict[str, Any]],
) -> bool:
    return reconcile_replace_front_matter_abstract_text_runtime(
        front_matter,
        blocks,
        abstract_text,
        abstract_records,
        block_source_spans=_block_source_spans,
    )


def _first_root_indicates_missing_intro(roots: list[Any]) -> bool:
    return reconcile_first_root_indicates_missing_intro_runtime(
        roots,
        clean_text=_clean_text,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        normalize_title_key=normalize_title_key,
    )


def _split_late_prelude_for_missing_intro(
    prelude: list[dict[str, Any]],
    roots: list[Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_split_late_prelude_for_missing_intro_runtime(
        prelude,
        roots,
        first_root_indicates_missing_intro=_first_root_indicates_missing_intro,
    )


def _make_reference_entry(record: dict[str, Any], index: int) -> dict[str, Any]:
    return reconcile_make_reference_entry_runtime(
        record,
        index,
        clean_text=_clean_text,
        normalize_reference_text=normalize_reference_text,
        block_source_spans=_block_source_spans,
        default_review=default_review,
    )


def _is_reference_start(record: dict[str, Any]) -> bool:
    return reconcile_is_reference_start_runtime(
        record,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        reference_start_re=REFERENCE_START_RE,
        looks_like_reference_text=_looks_like_reference_text,
    )


def _merge_reference_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_merge_reference_records_runtime(
        records,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        is_reference_start=_is_reference_start,
    )


def _looks_like_reference_text(text: str) -> bool:
    return reconcile_looks_like_reference_text_runtime(
        text,
        clean_text=_clean_text,
        reference_year_re=REFERENCE_YEAR_RE,
        reference_venue_re=REFERENCE_VENUE_RE,
        reference_author_re=REFERENCE_AUTHOR_RE,
        short_word_re=SHORT_WORD_RE,
    )


def _split_trailing_reference_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_split_trailing_reference_records_runtime(
        records,
        looks_like_reference_text=_looks_like_reference_text,
        merge_reference_records=_merge_reference_records,
    )


def _extract_reference_records_from_tail_section(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return reconcile_extract_reference_records_from_tail_section_runtime(
        records,
        clean_text=_clean_text,
        about_author_re=ABOUT_AUTHOR_RE,
        looks_like_reference_text=_looks_like_reference_text,
        merge_reference_records=_merge_reference_records,
    )


def _reference_records_from_mathpix_layout(layout: dict[str, Any] | None) -> list[dict[str, Any]]:
    return reconcile_reference_records_from_mathpix_layout_runtime(
        layout,
        mathpix_text_blocks_by_page=_mathpix_text_blocks_by_page,
        clean_text=_clean_text,
        normalize_title_key=normalize_title_key,
        layout_record=_layout_record,
        merge_reference_records=_merge_reference_records,
    )


def _starts_like_sentence(text: str) -> bool:
    return reconcile_starts_like_sentence(text)


def _starts_like_paragraph_continuation(text: str) -> bool:
    return reconcile_starts_like_paragraph_continuation(text, clean_text=_clean_text)


def _starts_like_strong_paragraph_continuation(text: str) -> bool:
    return reconcile_starts_like_strong_paragraph_continuation(text, clean_text=_clean_text)


def _ends_like_short_lead_in(text: str) -> bool:
    return reconcile_ends_like_short_lead_in(text, clean_text=_clean_text)


def _ends_like_clause_lead_in(text: str) -> bool:
    return reconcile_ends_like_clause_lead_in(text, clean_text=_clean_text)


def _is_paragraph_like_record(record: dict[str, Any]) -> bool:
    return reconcile_is_paragraph_like_record(record)


def _merge_anchor_spans(record: dict[str, Any]) -> list[dict[str, Any]]:
    return reconcile_merge_anchor_spans(record, block_source_spans=_block_source_spans)


def _looks_like_running_header_record(record: dict[str, Any]) -> bool:
    return reconcile_looks_like_running_header_record(
        record,
        clean_text=_clean_text,
        running_header_text_re=RUNNING_HEADER_TEXT_RE,
        short_word_re=SHORT_WORD_RE,
        block_source_spans=_block_source_spans,
    )


def _looks_like_table_body_debris(record: dict[str, Any]) -> bool:
    return reconcile_looks_like_table_body_debris(
        record,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
    )


def _suppress_embedded_table_headings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return reconcile_suppress_embedded_table_headings(
        records,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        table_caption_re=TABLE_CAPTION_RE,
        parse_heading_label=parse_heading_label,
        clean_heading_title=clean_heading_title,
    )


def _looks_like_same_page_column_continuation(
    previous_x0: float,
    previous_y0: float,
    previous_y1: float,
    current_x0: float,
    current_y0: float,
) -> bool:
    return reconcile_looks_like_same_page_column_continuation(
        previous_x0,
        previous_y0,
        previous_y1,
        current_x0,
        current_y0,
    )


def _should_merge_paragraph_records(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    return reconcile_should_merge_paragraph_records(
        previous,
        current,
        clean_text=_clean_text,
        short_word_re=SHORT_WORD_RE,
        block_source_spans=_block_source_spans,
        terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    )


def _list_item_marker(text: str) -> tuple[str | None, bool, str]:
    return assemble_list_item_marker(text, clean_text=_clean_text)


def _split_code_lines(text: str) -> list[str]:
    return assemble_split_code_lines(text)


def _looks_like_real_code_record(text: str) -> bool:
    return assemble_looks_like_real_code_record(text, clean_text=_clean_text)


def _rect_intersection_area(a: dict[str, Any], b: dict[str, Any]) -> float:
    return reconcile_rect_intersection_area(a, b)


def _rect_area(rect: dict[str, Any]) -> float:
    return reconcile_rect_area(rect)


def _match_external_math_entry(
    record: dict[str, Any],
    external_math_by_page: dict[int, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    return reconcile_match_external_math_entry(
        record,
        external_math_by_page,
        block_source_spans=_block_source_spans,
        clean_text=_clean_text,
    )


def _merge_native_and_external_layout(native_layout: dict[str, Any], external_layout: dict[str, Any]) -> dict[str, Any]:
    return orchestrate_merge_native_and_external_layout(native_layout, external_layout)


def _is_figure_debris(record: dict[str, Any], figures_by_page: dict[int, list[dict[str, Any]]]) -> bool:
    return reconcile_is_figure_debris(
        record,
        figures_by_page,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        diagram_decision_re=DIAGRAM_DECISION_RE,
        diagram_query_re=DIAGRAM_QUERY_RE,
        diagram_action_re=DIAGRAM_ACTION_RE,
        terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
        short_word_re=SHORT_WORD_RE,
        rect_intersection_area=_rect_intersection_area,
    )


def _is_short_ocr_fragment(record: dict[str, Any]) -> bool:
    return reconcile_is_short_ocr_fragment(
        record,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        looks_like_browser_ui_scrap=_looks_like_browser_ui_scrap,
        looks_like_quoted_identifier_fragment=_looks_like_quoted_identifier_fragment,
        looks_like_glyph_noise_cloud=_looks_like_glyph_noise_cloud,
        looks_like_vertical_label_cloud=_looks_like_vertical_label_cloud,
        looks_like_table_marker_cloud=_looks_like_table_marker_cloud,
        short_word_re=SHORT_WORD_RE,
        label_cloud_token_re=LABEL_CLOUD_TOKEN_RE,
        short_ocr_noise_re=SHORT_OCR_NOISE_RE,
        terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
        strong_operator_count=_strong_operator_count,
    )


def reconcile_paper_state(
    paper_id: str,
    *,
    text_engine: str = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    layout_output: dict[str, Any] | None = None,
    figures: list[dict[str, Any]] | None = None,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> PaperState:
    runtime_config = config or build_pipeline_config(
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        include_review=False,
    )
    return reconcile_run_reconcile_pipeline_runtime(
        paper_id,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        layout_output=layout_output,
        figures=figures,
        runtime_layout=runtime_config.layout,
        run_paper_pipeline_impl=run_paper_pipeline,
        extract_layout=extract_layout,
        load_external_layout=load_external_layout,
        merge_native_and_external_layout=_merge_native_and_external_layout,
        load_external_math=load_external_math,
        external_math_by_page=reconcile_external_math_by_page,
        load_mathpix_layout=load_mathpix_layout,
        extract_figures=extract_figures,
        normalize_prose_text_impl=normalize_prose_text,
        normalize_reference_text_impl=normalize_reference_text,
        normalize_paragraph_text_impl=reconcile_normalize_paragraph_text,
        normalize_figure_caption_text_impl=reconcile_normalize_figure_caption_text,
        strip_known_running_header_text=_strip_known_running_header_text,
        clean_text=_clean_text,
        block_source_spans=_block_source_spans,
        default_review=default_review,
        make_reference_entry_impl=reconcile_make_reference_entry_runtime,
        leading_negationslash_artifact_re=LEADING_NEGATIONSLASH_ARTIFACT_RE,
        leading_ocr_marker_re=LEADING_OCR_MARKER_RE,
        leading_punct_artifact_re=LEADING_PUNCT_ARTIFACT_RE,
        leading_var_artifact_re=LEADING_VAR_ARTIFACT_RE,
        trailing_numeric_artifact_re=TRAILING_NUMERIC_ARTIFACT_RE,
        math_entry_looks_like_prose_impl=reconcile_math_entry_looks_like_prose,
        should_demote_prose_math_entry_to_paragraph_impl=reconcile_should_demote_prose_math_entry_to_paragraph,
        should_demote_graphic_math_entry_to_paragraph_impl=reconcile_should_demote_graphic_math_entry_to_paragraph,
        should_drop_display_math_artifact_impl=reconcile_should_drop_display_math_artifact,
        group_entry_items_are_graphic_only=_group_entry_items_are_graphic_only,
        math_entry_semantic_policy=_math_entry_semantic_policy,
        math_entry_category=_math_entry_category,
        looks_like_prose_paragraph=looks_like_prose_paragraph,
        looks_like_prose_math_fragment=looks_like_prose_math_fragment,
        word_count=_word_count,
        strong_operator_count=_strong_operator_count,
        mathish_ratio=_mathish_ratio,
        paragraph_block_from_graphic_math_entry_impl=reconcile_paragraph_block_from_graphic_math_entry,
        split_inline_math=split_inline_math,
        repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
        extract_general_inline_math_spans=extract_general_inline_math_spans,
        merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
        normalize_inline_math_spans=normalize_inline_math_spans,
        build_front_matter_impl=assemble_front_matter,
        split_leading_front_matter_records=_split_leading_front_matter_records,
        clean_record=_clean_record,
        record_word_count=_record_word_count,
        record_width=_record_width,
        abstract_marker_only_re=ABSTRACT_MARKER_ONLY_RE,
        abstract_lead_re=ABSTRACT_LEAD_RE,
        looks_like_front_matter_metadata=_looks_like_front_matter_metadata,
        author_note_re=AUTHOR_NOTE_RE,
        looks_like_affiliation=_looks_like_affiliation,
        looks_like_intro_marker=_looks_like_intro_marker,
        looks_like_author_line=_looks_like_author_line,
        looks_like_contact_name=_looks_like_contact_name,
        matches_title_line=_matches_title_line,
        looks_like_affiliation_continuation=_looks_like_affiliation_continuation,
        funding_re=FUNDING_RE,
        dedupe_text_lines=_dedupe_text_lines,
        filter_front_matter_authors=_filter_front_matter_authors,
        parse_authors=_parse_authors,
        parse_authors_from_citation_line=_parse_authors_from_citation_line,
        normalize_author_line=_normalize_author_line,
        missing_front_matter_author=_missing_front_matter_author,
        build_affiliations_for_authors=_build_affiliations_for_authors,
        missing_front_matter_affiliation=_missing_front_matter_affiliation,
        strip_author_prefix_from_affiliation_line=_strip_author_prefix_from_affiliation_line,
        normalize_title_key=normalize_title_key,
        clone_record_with_text=_clone_record_with_text,
        looks_like_body_section_marker=_looks_like_body_section_marker,
        preprint_marker_re=PREPRINT_MARKER_RE,
        keywords_lead_re=KEYWORDS_LEAD_RE,
        abstract_text_is_usable=_abstract_text_is_usable,
        normalize_abstract_candidate_text=_normalize_abstract_candidate_text,
        front_matter_missing_placeholder=FRONT_MATTER_MISSING_PLACEHOLDER,
        normalize_section_title_impl=assemble_normalize_section_title,
        clean_heading_title=clean_heading_title,
        parse_heading_label=parse_heading_label,
        front_block_text_impl=assemble_front_block_text,
        recover_missing_front_matter_abstract_impl=assemble_recover_missing_front_matter_abstract,
        abstract_quality_flags=abstract_quality_flags,
        leading_abstract_text=_leading_abstract_text,
        abstract_text_is_recoverable=_abstract_text_is_recoverable,
        replace_front_matter_abstract_text=_replace_front_matter_abstract_text,
        opening_abstract_candidate_records=_opening_abstract_candidate_records,
        build_blocks_for_record_impl=assemble_blocks_for_record,
        record_analysis_text=_record_analysis_text,
        is_short_ocr_fragment=_is_short_ocr_fragment,
        caption_label=caption_label,
        looks_like_real_code_record=_looks_like_real_code_record,
        split_code_lines=_split_code_lines,
        list_item_marker=_list_item_marker,
        review_for_math_entry=review_for_math_entry,
        review_for_math_ref_block=review_for_math_ref_block,
        match_external_math_entry_impl=reconcile_match_external_math_entry,
        build_block_math_entry=build_block_math_entry,
        normalize_formula_display_text=_normalize_formula_display_text,
        classify_math_block=classify_math_block,
        review_for_algorithm_block_text=review_for_algorithm_block_text,
        overlapping_external_math_entries_impl=reconcile_overlapping_external_math_entries,
        trim_embedded_display_math_from_paragraph_impl=reconcile_trim_embedded_display_math_from_paragraph,
        display_math_prose_cue_re=DISPLAY_MATH_PROSE_CUE_RE,
        display_math_resume_re=DISPLAY_MATH_RESUME_RE,
        display_math_start_re=DISPLAY_MATH_START_RE,
        looks_like_display_math_echo_impl=reconcile_looks_like_display_math_echo,
        short_word_re=SHORT_WORD_RE,
        merge_layout_and_figure_records_impl=reconcile_merge_layout_and_figure_records,
        layout_record=_layout_record,
        absorb_figure_caption_continuations=_absorb_figure_caption_continuations,
        figure_label_token=_figure_label_token,
        synthetic_caption_record=_synthetic_caption_record,
        inject_external_math_records=_inject_external_math_records,
        mark_records_with_external_math_overlap_impl=reconcile_mark_records_with_external_math_overlap,
        repair_record_text_with_mathpix_hints_impl=reconcile_repair_record_text_with_mathpix_hints,
        mathpix_text_blocks_by_page=_mathpix_text_blocks_by_page,
        mathpix_text_hint_candidate=_mathpix_text_hint_candidate,
        is_mathpix_text_hint_better=_is_mathpix_text_hint_better,
        mathpix_prose_lead_repair_candidate=_mathpix_prose_lead_repair_candidate,
        pdftotext_available=pdftotext_available,
        repair_record_text_with_pdftotext=_repair_record_text_with_pdftotext,
        extract_pdftotext_pages=extract_pdftotext_pages,
        page_height_map=_page_height_map,
        promote_heading_like_records_impl=reconcile_promote_heading_like_records,
        looks_like_bad_heading=looks_like_bad_heading,
        collapse_ocr_split_caps=collapse_ocr_split_caps,
        decode_control_heading_label=_decode_control_heading_label,
        normalize_decoded_heading_title=_normalize_decoded_heading_title,
        split_embedded_heading_paragraph=_split_embedded_heading_paragraph,
        merge_math_fragment_records=_merge_math_fragment_records,
        page_one_front_matter_records=_page_one_front_matter_records,
        is_title_page_metadata_record=_is_title_page_metadata_record,
        build_section_tree=build_section_tree,
        attach_orphan_numbered_roots=attach_orphan_numbered_roots,
        split_late_prelude_for_missing_intro=_split_late_prelude_for_missing_intro,
        build_abstract_decision=build_abstract_decision,
        should_replace_front_matter_abstract=_should_replace_front_matter_abstract,
        section_node_type=SectionNode,
        prepare_section_nodes=prepare_section_nodes,
        split_trailing_reference_records=_split_trailing_reference_records,
        extract_reference_records_from_tail_section=_extract_reference_records_from_tail_section,
        reference_records_from_mathpix_layout=_reference_records_from_mathpix_layout,
        materialize_sections=materialize_sections,
        section_id_impl=assemble_section_id,
        merge_reference_records=_merge_reference_records,
        is_figure_debris=_is_figure_debris,
        looks_like_running_header_record=_looks_like_running_header_record,
        looks_like_table_body_debris=_looks_like_table_body_debris,
        suppress_embedded_table_headings=_suppress_embedded_table_headings,
        should_merge_paragraph_records=_should_merge_paragraph_records,
        table_caption_re=TABLE_CAPTION_RE,
        merge_code_records_impl=reconcile_merge_code_records,
        merge_paragraph_records_impl=reconcile_merge_paragraph_records,
        compile_formulas=compile_formulas,
        annotate_formula_classifications=annotate_formula_classifications,
        annotate_formula_semantic_expr=annotate_formula_semantic_expr,
        suppress_graphic_display_math_blocks_impl=reconcile_suppress_graphic_display_math_blocks,
        suppress_running_header_blocks_impl=reconcile_suppress_running_header_blocks,
        compact_text=compact_text,
        running_header_text_re=RUNNING_HEADER_TEXT_RE,
        normalize_footnote_blocks_impl=reconcile_normalize_footnote_blocks,
        starts_like_sentence=_starts_like_sentence,
        merge_paragraph_blocks_impl=reconcile_merge_paragraph_blocks,
        now_iso=_now_iso,
        build_canonical_document=build_canonical_document,
        config=runtime_config,
        state=state,
    )


def reconcile_paper(
    paper_id: str,
    *,
    text_engine: str = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    layout_output: dict[str, Any] | None = None,
    figures: list[dict[str, Any]] | None = None,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> dict[str, Any]:
    paper_state = reconcile_paper_state(
        paper_id,
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        layout_output=layout_output,
        figures=figures,
        config=config,
        state=state,
    )
    if paper_state.document is None:
        raise RuntimeError(f"Pipeline did not materialize a canonical document for {paper_id}")
    return paper_state.document
