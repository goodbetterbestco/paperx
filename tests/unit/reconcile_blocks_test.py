import sys
import unittest
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pipeline.reconcile.front_matter_patterns as fmp
import pipeline.reconcile.shared_patterns as rsp
from pipeline.assembly.abstract_recovery import (
    make_bound_front_matter_recovery_helpers,
    make_recover_missing_front_matter_abstract,
    recover_missing_front_matter_abstract as _assembly_recover_missing_front_matter_abstract,
)
from pipeline.assembly.front_matter_builder import (
    build_front_matter as _assembly_build_front_matter,
    make_build_front_matter,
)
from pipeline.assembly.front_matter_support import (
    front_block_text as _support_front_block_text,
    make_bound_front_matter_support_helpers,
    make_front_block_text,
    missing_front_matter_affiliation,
    missing_front_matter_author,
)
from pipeline.assembly.section_support import (
    make_normalize_section_title,
    normalize_section_title as _section_normalize_section_title,
)
from pipeline.policies.abstract_quality import (
    MISSING_ABSTRACT_PLACEHOLDER,
    NO_ABSTRACT_IN_BASE_MATERIAL,
    abstract_quality_flags,
)
from pipeline.reconcile.external_math_binding_runtime import make_inject_external_math_records
from pipeline.reconcile.external_math import rect_intersection_area
from pipeline.reconcile.front_matter_parsing import looks_like_affiliation
from pipeline.reconcile.front_matter_parsing_runtime import make_bound_front_matter_parsing_helpers
from pipeline.reconcile.heading_promotion_runtime import (
    decode_control_heading_label,
    make_normalize_decoded_heading_title,
    make_split_embedded_heading_paragraph,
)
from pipeline.reconcile.layout_records import (
    figure_label_token,
    make_absorb_figure_caption_continuations,
    make_append_figure_caption_fragment,
    make_layout_record,
    make_merge_layout_and_figure_records as make_record_merge_layout_and_figure_records,
    make_match_figure_for_caption_record,
    make_record_bbox,
    make_strip_caption_label_prefix,
    rect_x_overlap_ratio,
    synthetic_caption_record,
)
from pipeline.reconcile.math_fragments_runtime import make_math_signal_count, strong_operator_count
from pipeline.reconcile.math_runtime import make_trim_embedded_display_math_from_paragraph
from pipeline.reconcile.math_suppression import trim_embedded_display_math_from_paragraph as _math_trim_embedded_display_math_from_paragraph
from pipeline.reconcile.block_merging import (
    make_merge_paragraph_blocks,
    make_merge_paragraph_records,
    make_normalize_footnote_blocks,
    make_suppress_running_header_blocks,
)
from pipeline.reconcile.heading_promotion import make_promote_heading_like_records
from pipeline.reconcile.text_repairs import make_repair_record_text_with_mathpix_hints
from pipeline.reconcile.reference_binding_runtime import make_bound_reference_helpers
from pipeline.reconcile.runtime_constants import (
    ABOUT_AUTHOR_RE,
    CONTROL_CHAR_RE,
    DIAGRAM_ACTION_RE,
    DIAGRAM_DECISION_RE,
    DIAGRAM_QUERY_RE,
    LABEL_CLOUD_TOKEN_RE,
    MATHPIX_HINT_TOKEN_RE,
    MATH_TOKEN_RE,
    QUOTED_IDENTIFIER_FRAGMENT_RE,
    REFERENCE_AUTHOR_RE,
    REFERENCE_START_RE,
    REFERENCE_YEAR_RE,
    SHORT_OCR_NOISE_RE,
    TERMINAL_PUNCTUATION_RE,
    TRUNCATED_PROSE_LEAD_STOPWORDS,
)
from pipeline.reconcile.screening_runtime import (
    make_is_figure_debris,
    make_is_short_ocr_fragment,
    make_looks_like_browser_ui_scrap,
    make_looks_like_glyph_noise_cloud,
    make_looks_like_quoted_identifier_fragment,
    make_looks_like_table_marker_cloud,
    make_looks_like_vertical_label_cloud,
)
from pipeline.reconcile.section_filter_binding_runtime import (
    make_looks_like_running_header_record,
    make_looks_like_table_body_debris,
    make_should_merge_paragraph_records,
    make_suppress_embedded_table_headings,
    starts_like_sentence,
)
from pipeline.reconcile.support_binding_runtime import (
    block_source_spans,
    make_clean_record,
    make_clean_text,
    make_is_pdftotext_candidate_better,
    make_mathish_ratio,
    make_normalize_figure_caption_text,
    make_strip_known_running_header_text,
    make_word_count,
)
from pipeline.reconcile.text_repairs import make_bound_text_repair_helpers, mathpix_text_blocks_by_page
from pipeline.math.extract import INLINE_MATH_RE
from pipeline.text.headings import collapse_ocr_split_caps, looks_like_bad_heading
from pipeline.text.prose import normalize_prose_text
from pipeline.types import LayoutBlock
from pipeline.types import default_review
from pipeline.text.headings import SectionNode
from pipeline.text.headings import clean_heading_title, compact_text, normalize_title_key, parse_heading_label


def _review(risk: str = "medium", status: str = "unreviewed") -> dict[str, str]:
    return {"risk": risk, "status": status, "notes": ""}


CLEAN_TEXT = make_clean_text(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
)
STRIP_KNOWN_RUNNING_HEADER_TEXT = make_strip_known_running_header_text(
    procedia_running_header_re=rsp.PROCEDIA_RUNNING_HEADER_RE,
    clean_text=CLEAN_TEXT,
)
CLEAN_RECORD = make_clean_record(
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
)
WORD_COUNT = make_word_count(short_word_re=rsp.SHORT_WORD_RE)
MATHISH_RATIO = make_mathish_ratio(
    word_count=WORD_COUNT,
    math_signal_count=make_math_signal_count(math_token_re=MATH_TOKEN_RE),
)
LOOKS_LIKE_BROWSER_UI_SCRAP = make_looks_like_browser_ui_scrap(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT = make_looks_like_quoted_identifier_fragment(
    short_word_re=rsp.SHORT_WORD_RE,
    quoted_identifier_fragment_re=QUOTED_IDENTIFIER_FRAGMENT_RE,
)
LOOKS_LIKE_GLYPH_NOISE_CLOUD = make_looks_like_glyph_noise_cloud(
    short_word_re=rsp.SHORT_WORD_RE,
)
LOOKS_LIKE_VERTICAL_LABEL_CLOUD = make_looks_like_vertical_label_cloud(
    strong_operator_count=strong_operator_count,
)
LOOKS_LIKE_TABLE_MARKER_CLOUD = make_looks_like_table_marker_cloud(
    strong_operator_count=strong_operator_count,
)
IS_SHORT_OCR_FRAGMENT = make_is_short_ocr_fragment(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    looks_like_browser_ui_scrap=LOOKS_LIKE_BROWSER_UI_SCRAP,
    looks_like_quoted_identifier_fragment=LOOKS_LIKE_QUOTED_IDENTIFIER_FRAGMENT,
    looks_like_glyph_noise_cloud=LOOKS_LIKE_GLYPH_NOISE_CLOUD,
    looks_like_vertical_label_cloud=LOOKS_LIKE_VERTICAL_LABEL_CLOUD,
    looks_like_table_marker_cloud=LOOKS_LIKE_TABLE_MARKER_CLOUD,
    short_word_re=rsp.SHORT_WORD_RE,
    label_cloud_token_re=LABEL_CLOUD_TOKEN_RE,
    short_ocr_noise_re=SHORT_OCR_NOISE_RE,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    strong_operator_count=strong_operator_count,
)
LOOKS_LIKE_RUNNING_HEADER_RECORD = make_looks_like_running_header_record(
    clean_text=CLEAN_TEXT,
    running_header_text_re=rsp.RUNNING_HEADER_TEXT_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    block_source_spans=block_source_spans,
)
LOOKS_LIKE_TABLE_BODY_DEBRIS = make_looks_like_table_body_debris(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
)
SHOULD_MERGE_PARAGRAPH_RECORDS = make_should_merge_paragraph_records(
    clean_text=CLEAN_TEXT,
    short_word_re=rsp.SHORT_WORD_RE,
    block_source_spans=block_source_spans,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
)
SUPPRESS_EMBEDDED_TABLE_HEADINGS = make_suppress_embedded_table_headings(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    table_caption_re=rsp.TABLE_CAPTION_RE,
    parse_heading_label=parse_heading_label,
    clean_heading_title=clean_heading_title,
)
LAYOUT_RECORD = make_layout_record(clean_text=CLEAN_TEXT)
APPEND_FIGURE_CAPTION_FRAGMENT = make_append_figure_caption_fragment(
    clean_text=CLEAN_TEXT,
    normalize_title_key=normalize_title_key,
    normalize_figure_caption_text=make_normalize_figure_caption_text(
        clean_text=CLEAN_TEXT,
        normalize_prose_text=normalize_prose_text,
    ),
    strip_caption_label_prefix=make_strip_caption_label_prefix(clean_text=CLEAN_TEXT),
)
ABSORB_FIGURE_CAPTION_CONTINUATIONS = make_absorb_figure_caption_continuations(
    match_figure_for_caption_record=make_match_figure_for_caption_record(
        record_bbox=make_record_bbox(block_source_spans=block_source_spans),
        rect_x_overlap_ratio=rect_x_overlap_ratio,
        figure_label_token=figure_label_token,
    ),
    append_figure_caption_fragment=APPEND_FIGURE_CAPTION_FRAGMENT,
)
MERGE_LAYOUT_AND_FIGURE_RECORDS = make_record_merge_layout_and_figure_records(
    layout_record=LAYOUT_RECORD,
    absorb_figure_caption_continuations=ABSORB_FIGURE_CAPTION_CONTINUATIONS,
    figure_label_token=figure_label_token,
    synthetic_caption_record=synthetic_caption_record,
)
TEXT_REPAIR_HELPERS = make_bound_text_repair_helpers(
    clean_text=CLEAN_TEXT,
    word_count=WORD_COUNT,
    inline_math_re=INLINE_MATH_RE,
    block_source_spans=block_source_spans,
    bbox_to_line_window=lambda bbox, *, page_height, line_count: (0, 0),
    slice_page_text=lambda lines, *, start_line, end_line: "",
    is_pdftotext_candidate_better=make_is_pdftotext_candidate_better(
        clean_text=CLEAN_TEXT,
        word_count=WORD_COUNT,
    ),
    rect_x_overlap_ratio=rect_x_overlap_ratio,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    display_math_start_re=rsp.DISPLAY_MATH_START_RE,
    math_signal_count=make_math_signal_count(math_token_re=MATH_TOKEN_RE),
    hint_token_re=MATHPIX_HINT_TOKEN_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    truncated_prose_lead_stopwords=TRUNCATED_PROSE_LEAD_STOPWORDS,
    parse_heading_label=parse_heading_label,
)
REPAIR_RECORD_TEXT_WITH_MATHPIX_HINTS = make_repair_record_text_with_mathpix_hints(
    mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
    is_short_ocr_fragment=IS_SHORT_OCR_FRAGMENT,
    mathpix_text_hint_candidate=TEXT_REPAIR_HELPERS.mathpix_text_hint_candidate,
    is_mathpix_text_hint_better=TEXT_REPAIR_HELPERS.is_mathpix_text_hint_better,
    mathpix_prose_lead_repair_candidate=TEXT_REPAIR_HELPERS.mathpix_prose_lead_repair_candidate,
    clean_text=CLEAN_TEXT,
)
NORMALIZE_DECODED_HEADING_TITLE = make_normalize_decoded_heading_title(
    clean_text=CLEAN_TEXT,
    clean_heading_title=clean_heading_title,
)
SPLIT_EMBEDDED_HEADING_PARAGRAPH = make_split_embedded_heading_paragraph(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    embedded_heading_prefix_re=rsp.EMBEDDED_HEADING_PREFIX_RE,
    normalize_decoded_heading_title=NORMALIZE_DECODED_HEADING_TITLE,
    collapse_ocr_split_caps=collapse_ocr_split_caps,
    looks_like_bad_heading=looks_like_bad_heading,
    short_word_re=rsp.SHORT_WORD_RE,
)
PROMOTE_HEADING_LIKE_RECORDS = make_promote_heading_like_records(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
    parse_heading_label=parse_heading_label,
    clean_heading_title=clean_heading_title,
    looks_like_bad_heading=looks_like_bad_heading,
    collapse_ocr_split_caps=collapse_ocr_split_caps,
    decode_control_heading_label=decode_control_heading_label,
    normalize_decoded_heading_title=NORMALIZE_DECODED_HEADING_TITLE,
    split_embedded_heading_paragraph=SPLIT_EMBEDDED_HEADING_PARAGRAPH,
    short_word_re=rsp.SHORT_WORD_RE,
)
MERGE_PARAGRAPH_RECORDS = make_merge_paragraph_records(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    should_merge_paragraph_records=SHOULD_MERGE_PARAGRAPH_RECORDS,
    table_caption_re=rsp.TABLE_CAPTION_RE,
)
MERGE_PARAGRAPH_BLOCKS = make_merge_paragraph_blocks(
    block_source_spans=block_source_spans,
    should_merge_paragraph_records=SHOULD_MERGE_PARAGRAPH_RECORDS,
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
)
NORMALIZE_FOOTNOTE_BLOCKS = make_normalize_footnote_blocks(
    block_source_spans=block_source_spans,
    short_word_re=rsp.SHORT_WORD_RE,
    starts_like_sentence=starts_like_sentence,
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
)
SUPPRESS_RUNNING_HEADER_BLOCKS = make_suppress_running_header_blocks(
    block_source_spans=block_source_spans,
    compact_text=compact_text,
    running_header_text_re=rsp.RUNNING_HEADER_TEXT_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    strip_known_running_header_text=STRIP_KNOWN_RUNNING_HEADER_TEXT,
)
SUPPORT_HELPERS = make_bound_front_matter_support_helpers(
    clean_text=CLEAN_TEXT,
    normalize_title_key=normalize_title_key,
    compact_text=compact_text,
    short_word_re=rsp.SHORT_WORD_RE,
    block_source_spans=block_source_spans,
    abstract_quality_flags=abstract_quality_flags,
)
PARSING_HELPERS = make_bound_front_matter_parsing_helpers(
    clean_text=CLEAN_TEXT,
    compact_text=compact_text,
    normalize_title_key=normalize_title_key,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    block_source_spans=block_source_spans,
    title_lookup_keys=SUPPORT_HELPERS.title_lookup_keys,
    abstract_quality_flags=abstract_quality_flags,
    looks_like_affiliation=looks_like_affiliation,
    author_marker_re=fmp.AUTHOR_MARKER_RE,
    author_affiliation_index_re=fmp.AUTHOR_AFFILIATION_INDEX_RE,
    name_token_re=fmp.NAME_TOKEN_RE,
    abbreviated_venue_line_re=fmp.ABBREVIATED_VENUE_LINE_RE,
    title_page_metadata_re=fmp.TITLE_PAGE_METADATA_RE,
    front_matter_metadata_re=fmp.FRONT_MATTER_METADATA_RE,
    reference_venue_re=fmp.REFERENCE_VENUE_RE,
    author_token_re=fmp.AUTHOR_TOKEN_RE,
    intro_marker_re=fmp.INTRO_MARKER_RE,
    abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    trailing_abstract_boilerplate_re=fmp.TRAILING_ABSTRACT_BOILERPLATE_RE,
    trailing_abstract_tail_re=fmp.TRAILING_ABSTRACT_TAIL_RE,
    preprint_marker_re=fmp.PREPRINT_MARKER_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    citation_year_re=fmp.CITATION_YEAR_RE,
    citation_author_split_re=fmp.CITATION_AUTHOR_SPLIT_RE,
)
RECOVERY_HELPERS = make_bound_front_matter_recovery_helpers(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    abstract_quality_flags=abstract_quality_flags,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    normalize_title_key=normalize_title_key,
    looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
    looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
    keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    abstract_body_break_re=fmp.ABSTRACT_BODY_BREAK_RE,
    figure_ref_re=fmp.FIGURE_REF_RE,
    abstract_continuation_re=fmp.ABSTRACT_CONTINUATION_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    record_word_count=SUPPORT_HELPERS.record_word_count,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
)
REFERENCE_HELPERS = make_bound_reference_helpers(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    reference_start_re=REFERENCE_START_RE,
    reference_year_re=REFERENCE_YEAR_RE,
    reference_venue_re=fmp.REFERENCE_VENUE_RE,
    reference_author_re=REFERENCE_AUTHOR_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    about_author_re=ABOUT_AUTHOR_RE,
    mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
    normalize_title_key=normalize_title_key,
    layout_record=LAYOUT_RECORD,
)
MISSING_FRONT_MATTER_AUTHOR = partial(
    missing_front_matter_author,
    MISSING_ABSTRACT_PLACEHOLDER,
)
MISSING_FRONT_MATTER_AFFILIATION = partial(
    missing_front_matter_affiliation,
    MISSING_ABSTRACT_PLACEHOLDER,
)
NORMALIZE_SECTION_TITLE = make_normalize_section_title(
    normalize_section_title_impl=_section_normalize_section_title,
    clean_text=CLEAN_TEXT,
    clean_heading_title=clean_heading_title,
    parse_heading_label=parse_heading_label,
    normalize_title_key=normalize_title_key,
)
FRONT_BLOCK_TEXT = make_front_block_text(
    front_block_text_impl=_support_front_block_text,
    clean_text=CLEAN_TEXT,
)
BUILD_FRONT_MATTER = make_build_front_matter(
    build_front_matter_impl=_assembly_build_front_matter,
    split_leading_front_matter_records=PARSING_HELPERS.split_leading_front_matter_records,
    clean_record=CLEAN_RECORD,
    clean_text=CLEAN_TEXT,
    record_word_count=SUPPORT_HELPERS.record_word_count,
    record_width=SUPPORT_HELPERS.record_width,
    abstract_marker_only_re=fmp.ABSTRACT_MARKER_ONLY_RE,
    abstract_lead_re=fmp.ABSTRACT_LEAD_RE,
    looks_like_front_matter_metadata=PARSING_HELPERS.looks_like_front_matter_metadata,
    author_note_re=fmp.AUTHOR_NOTE_RE,
    looks_like_affiliation=looks_like_affiliation,
    looks_like_intro_marker=PARSING_HELPERS.looks_like_intro_marker,
    looks_like_author_line=PARSING_HELPERS.looks_like_author_line,
    looks_like_contact_name=PARSING_HELPERS.looks_like_contact_name,
    matches_title_line=SUPPORT_HELPERS.matches_title_line,
    looks_like_affiliation_continuation=PARSING_HELPERS.looks_like_affiliation_continuation,
    funding_re=fmp.FUNDING_RE,
    dedupe_text_lines=SUPPORT_HELPERS.dedupe_text_lines,
    filter_front_matter_authors=PARSING_HELPERS.filter_front_matter_authors,
    parse_authors=PARSING_HELPERS.parse_authors,
    parse_authors_from_citation_line=PARSING_HELPERS.parse_authors_from_citation_line,
    normalize_author_line=PARSING_HELPERS.normalize_author_line,
    missing_front_matter_author=MISSING_FRONT_MATTER_AUTHOR,
    build_affiliations_for_authors=PARSING_HELPERS.build_affiliations_for_authors,
    missing_front_matter_affiliation=MISSING_FRONT_MATTER_AFFILIATION,
    strip_author_prefix_from_affiliation_line=PARSING_HELPERS.strip_author_prefix_from_affiliation_line,
    normalize_title_key=normalize_title_key,
    clone_record_with_text=SUPPORT_HELPERS.clone_record_with_text,
    looks_like_body_section_marker=PARSING_HELPERS.looks_like_body_section_marker,
    preprint_marker_re=fmp.PREPRINT_MARKER_RE,
    keywords_lead_re=fmp.KEYWORDS_LEAD_RE,
    abstract_text_is_usable=PARSING_HELPERS.abstract_text_is_usable,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
    default_review=default_review,
    block_source_spans=block_source_spans,
    front_matter_missing_placeholder=NO_ABSTRACT_IN_BASE_MATERIAL,
)
RECOVER_MISSING_FRONT_MATTER_ABSTRACT = make_recover_missing_front_matter_abstract(
    recover_missing_front_matter_abstract_impl=_assembly_recover_missing_front_matter_abstract,
    front_block_text=FRONT_BLOCK_TEXT,
    abstract_quality_flags=abstract_quality_flags,
    normalize_section_title=NORMALIZE_SECTION_TITLE,
    leading_abstract_text=RECOVERY_HELPERS.leading_abstract_text,
    abstract_text_is_recoverable=RECOVERY_HELPERS.abstract_text_is_recoverable,
    replace_front_matter_abstract_text=RECOVERY_HELPERS.replace_front_matter_abstract_text,
    opening_abstract_candidate_records=RECOVERY_HELPERS.opening_abstract_candidate_records,
    normalize_abstract_candidate_text=PARSING_HELPERS.normalize_abstract_candidate_text,
)
TRIM_EMBEDDED_DISPLAY_MATH_FROM_PARAGRAPH = make_trim_embedded_display_math_from_paragraph(
    trim_embedded_display_math_from_paragraph_impl=_math_trim_embedded_display_math_from_paragraph,
    block_source_spans=block_source_spans,
    clean_text=CLEAN_TEXT,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    display_math_resume_re=rsp.DISPLAY_MATH_RESUME_RE,
    display_math_start_re=rsp.DISPLAY_MATH_START_RE,
    mathish_ratio=MATHISH_RATIO,
    strong_operator_count=strong_operator_count,
)
INJECT_EXTERNAL_MATH_RECORDS = make_inject_external_math_records(
    clean_text=CLEAN_TEXT,
    display_math_prose_cue_re=rsp.DISPLAY_MATH_PROSE_CUE_RE,
    mathish_ratio=MATHISH_RATIO,
    strong_operator_count=strong_operator_count,
)
IS_FIGURE_DEBRIS = make_is_figure_debris(
    clean_text=CLEAN_TEXT,
    block_source_spans=block_source_spans,
    diagram_decision_re=DIAGRAM_DECISION_RE,
    diagram_query_re=DIAGRAM_QUERY_RE,
    diagram_action_re=DIAGRAM_ACTION_RE,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    short_word_re=rsp.SHORT_WORD_RE,
    rect_intersection_area=rect_intersection_area,
)

_append_figure_caption_fragment = APPEND_FIGURE_CAPTION_FRAGMENT
_leading_abstract_text = RECOVERY_HELPERS.leading_abstract_text
_should_replace_front_matter_abstract = SUPPORT_HELPERS.should_replace_front_matter_abstract
_strip_trailing_abstract_boilerplate = PARSING_HELPERS.strip_trailing_abstract_boilerplate
_extract_reference_records_from_tail_section = REFERENCE_HELPERS.extract_reference_records_from_tail_section
_inject_external_math_records = INJECT_EXTERNAL_MATH_RECORDS
_is_figure_debris = IS_FIGURE_DEBRIS
_is_reference_start = REFERENCE_HELPERS.is_reference_start
_is_short_ocr_fragment = IS_SHORT_OCR_FRAGMENT
_looks_like_affiliation = looks_like_affiliation
_looks_like_author_line = PARSING_HELPERS.looks_like_author_line
_looks_like_running_header_record = LOOKS_LIKE_RUNNING_HEADER_RECORD
_looks_like_table_body_debris = LOOKS_LIKE_TABLE_BODY_DEBRIS
_reference_records_from_mathpix_layout = REFERENCE_HELPERS.reference_records_from_mathpix_layout
_suppress_embedded_table_headings = SUPPRESS_EMBEDDED_TABLE_HEADINGS
_should_merge_paragraph_records = SHOULD_MERGE_PARAGRAPH_RECORDS
_split_late_prelude_for_missing_intro = RECOVERY_HELPERS.split_late_prelude_for_missing_intro
_strip_known_running_header_text = STRIP_KNOWN_RUNNING_HEADER_TEXT


def _merge_paragraph_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return MERGE_PARAGRAPH_RECORDS(records)


def _merge_paragraph_blocks(
    blocks: list[dict[str, object]],
    sections: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return MERGE_PARAGRAPH_BLOCKS(blocks, sections)


def _normalize_footnote_blocks(
    blocks: list[dict[str, object]],
    sections: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return NORMALIZE_FOOTNOTE_BLOCKS(blocks, sections)


def _suppress_running_header_blocks(
    blocks: list[dict[str, object]],
    sections: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return SUPPRESS_RUNNING_HEADER_BLOCKS(blocks, sections)


def _merge_layout_and_figure_records(
    layout_blocks: list[LayoutBlock],
    figures: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, LayoutBlock]]:
    return MERGE_LAYOUT_AND_FIGURE_RECORDS(layout_blocks, figures)


def _repair_record_text_with_mathpix_hints(
    records: list[dict[str, object]],
    mathpix_layout: dict[str, object] | None,
) -> list[dict[str, object]]:
    return REPAIR_RECORD_TEXT_WITH_MATHPIX_HINTS(records, mathpix_layout)


def _split_embedded_heading_paragraph(record: dict[str, object]) -> tuple[str, str] | None:
    return SPLIT_EMBEDDED_HEADING_PARAGRAPH(record)


def _promote_heading_like_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return PROMOTE_HEADING_LIKE_RECORDS(records)


def _split_leading_front_matter_records(
    prelude: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return PARSING_HELPERS.split_leading_front_matter_records(prelude)


def _normalize_section_title(title: str) -> str:
    return NORMALIZE_SECTION_TITLE(title)


def _front_block_text(blocks: list[dict[str, object]], block_id: str | None) -> str:
    return FRONT_BLOCK_TEXT(blocks, block_id)


def _build_front_matter(
    paper_id: str,
    prelude: list[dict[str, object]],
    page_one_records: list[dict[str, object]],
    blocks: list[dict[str, object]],
    next_block_index: int,
) -> tuple[dict[str, object], list[dict[str, object]], int, list[dict[str, object]]]:
    return BUILD_FRONT_MATTER(
        paper_id,
        prelude,
        page_one_records,
        blocks,
        next_block_index,
    )


def _recover_missing_front_matter_abstract(
    front_matter: dict[str, object],
    blocks: list[dict[str, object]],
    prelude: list[dict[str, object]],
    ordered_roots: list[SectionNode],
) -> bool:
    return RECOVER_MISSING_FRONT_MATTER_ABSTRACT(
        front_matter,
        blocks,
        prelude,
        ordered_roots,
    )


def _trim_embedded_display_math_from_paragraph(
    text: str,
    record: dict[str, object],
    overlapping_math: list[dict[str, object]],
) -> str:
    return TRIM_EMBEDDED_DISPLAY_MATH_FROM_PARAGRAPH(
        text,
        record,
        overlapping_math,
    )


def _record(
    *,
    record_type: str,
    text: str,
    page: int = 1,
    y0: float = 640.0,
    height: float = 10.0,
    width: float = 240.0,
) -> dict[str, object]:
    return {
        "id": f"{record_type}-{page}-{y0}-{height}-{width}-{len(text)}",
        "page": page,
        "type": record_type,
        "text": text,
        "source_spans": [
            {
                "page": page,
                "bbox": {
                    "x0": 90.0,
                    "y0": y0,
                    "x1": 90.0 + width,
                    "y1": y0 + height,
                    "width": width,
                    "height": height,
                },
                "engine": "docling",
            }
        ],
        "meta": {},
    }


class ReconcileBlocksTest(unittest.TestCase):
    def test_numbered_paragraph_heading_is_promoted(self) -> None:
        record = _record(
            record_type="paragraph",
            text="5.3 Thin-plate optimization",
            page=7,
            y0=584.18,
            height=14.64,
            width=143.91,
        )
        record["source_spans"][0]["bbox"]["x0"] = 53.8
        record["source_spans"][0]["bbox"]["x1"] = 197.71

        promoted = _promote_heading_like_records([record])

        self.assertEqual(promoted[0]["type"], "heading")
        self.assertEqual(promoted[0]["text"], "5.3 Thin-plate optimization")

    def test_embedded_numbered_heading_paragraph_is_split(self) -> None:
        record = _record(
            record_type="paragraph",
            text=(
                "3 Net Shape Element Associativity We develop a mechanism by which an association "
                "can be created and maintained between the elements of a net shape."
            ),
            page=5,
            y0=210.0,
            height=14.0,
            width=420.0,
        )
        record["source_spans"][0]["bbox"]["x0"] = 53.8
        record["source_spans"][0]["bbox"]["x1"] = 473.8

        split = _split_embedded_heading_paragraph(record)

        self.assertEqual(
            split,
            (
                "3 Net Shape Element Associativity",
                "We develop a mechanism by which an association can be created and maintained between the elements of a net shape.",
            ),
        )

        promoted = _promote_heading_like_records([record])
        self.assertEqual([entry["type"] for entry in promoted], ["heading", "paragraph"])
        self.assertEqual(promoted[0]["text"], "3 Net Shape Element Associativity")
        self.assertTrue(promoted[0]["meta"]["synthetic_heading_split"])

    def test_embedded_heading_split_rejects_numbered_sentence_openers(self) -> None:
        record = _record(
            record_type="paragraph",
            text="1. The client of the master model does not need to communicate directly with the CAD system.",
            page=5,
            y0=240.0,
            height=12.0,
            width=420.0,
        )
        record["source_spans"][0]["bbox"]["x0"] = 53.8
        record["source_spans"][0]["bbox"]["x1"] = 473.8

        self.assertIsNone(_split_embedded_heading_paragraph(record))
        promoted = _promote_heading_like_records([record])
        self.assertEqual([entry["type"] for entry in promoted], ["paragraph"])

    def test_promotes_marker_only_abstract_paragraph_to_heading(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Abstract",
            page=1,
            y0=120.0,
            height=12.0,
            width=80.0,
        )

        promoted = _promote_heading_like_records([record])

        self.assertEqual([entry["type"] for entry in promoted], ["heading"])
        self.assertEqual(promoted[0]["text"], "Abstract")
        self.assertTrue(promoted[0]["meta"]["synthetic_heading_marker_only"])

    def test_page_one_institution_is_not_treated_as_author(self) -> None:
        self.assertTrue(_looks_like_affiliation("Universitat Politècnica de Catalunya"))
        self.assertFalse(_looks_like_author_line("Universitat Politècnica de Catalunya"))
        self.assertTrue(_looks_like_affiliation("Departament de Llenguatges i Sistemes Informàtics"))
        self.assertFalse(_looks_like_author_line("Departament de Llenguatges i Sistemes Informàtics"))

    def test_reference_records_from_mathpix_layout_recovers_bracketed_entries(self) -> None:
        layout = {
            "blocks": [
                LayoutBlock(
                    id="mp-1",
                    page=30,
                    order=1,
                    role="paragraph",
                    text="References",
                    bbox={"x0": 72.0, "y0": 90.0, "x1": 180.0, "y1": 102.0, "width": 108.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mp-2",
                    page=30,
                    order=2,
                    role="paragraph",
                    text="[1] First reference title.",
                    bbox={"x0": 72.0, "y0": 112.0, "x1": 260.0, "y1": 124.0, "width": 188.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mp-3",
                    page=30,
                    order=3,
                    role="paragraph",
                    text="Journal of Tests, 1998.",
                    bbox={"x0": 112.0, "y0": 126.0, "x1": 300.0, "y1": 138.0, "width": 188.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mp-4",
                    page=30,
                    order=4,
                    role="paragraph",
                    text="[2] Second reference title.",
                    bbox={"x0": 72.0, "y0": 150.0, "x1": 270.0, "y1": 162.0, "width": 198.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mp-5",
                    page=30,
                    order=5,
                    role="paragraph",
                    text="Proceedings of Examples, 1997.",
                    bbox={"x0": 112.0, "y0": 164.0, "x1": 330.0, "y1": 176.0, "width": 218.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mp-6",
                    page=31,
                    order=1,
                    role="paragraph",
                    text="[3] Third reference title.",
                    bbox={"x0": 72.0, "y0": 90.0, "x1": 260.0, "y1": 102.0, "width": 188.0, "height": 12.0},
                    meta={"mathpix_type": "text"},
                ),
            ]
        }

        references = _reference_records_from_mathpix_layout(layout)

        self.assertEqual(len(references), 3)
        self.assertEqual(references[0]["type"], "reference")
        self.assertIn("First reference title.", references[0]["text"])
        self.assertIn("Journal of Tests, 1998.", references[0]["text"])

    def test_extract_reference_records_from_tail_section_harvests_scattered_reference_list_items(self) -> None:
        records = [
            _record(record_type="paragraph", text="We conclude that the method is practical.", page=10, y0=100.0, width=320.0),
            _record(record_type="list_item", text="J.J. Koenderink and A. J. van Doorn, The internal representation of solid shape with respect to vision, Biol. Cybern. 32, 211-216 (1979).", page=10, y0=130.0, width=360.0),
            _record(record_type="paragraph", text="About the Author—Alice Example was born in 1965.", page=10, y0=150.0, width=320.0),
            _record(record_type="list_item", text="R. Korn and C. R. Dyer, 3-D multiview object representations for model-based object recognition, Pattern Recognition 20, 91-103 (1987).", page=10, y0=170.0, width=360.0),
            _record(record_type="list_item", text="H. Stewman and K. W. Bowyer, Creating the perspective projection aspect graph of polyhedral objects, ICCV'88, pp. 494-500 (1988).", page=10, y0=190.0, width=360.0),
            _record(record_type="list_item", text="A. Gaultieri, S. Baugher and M. Werman, The visual potential: one convex polygon, Comput. Vision Graphics Image Process. 46(1), 96-130 (1989).", page=10, y0=210.0, width=360.0),
            _record(record_type="list_item", text="Chakravarty and H. Freeman, Characteristic views as a basis of 3-D object recognition, Robot Vision, SPIE 336, 37-45 (1988).", page=10, y0=230.0, width=360.0),
            _record(record_type="list_item", text="Edelsbrunner, J. O'Rourke and R. Seidel, Constructing arrangements of lines and hyperplanes with applications, SIAM J. Comput. 15(2), 341-363 (1986).", page=10, y0=250.0, width=360.0),
        ]

        body_records, references = _extract_reference_records_from_tail_section(records)

        self.assertEqual(len(references), 6)
        self.assertEqual(len(body_records), 2)
        self.assertTrue(any(record["text"].startswith("About the Author") for record in body_records))

    def test_tail_reference_list_item_starts_new_reference_even_when_indented(self) -> None:
        record = _record(
            record_type="list_item",
            text="J.J. Koenderink and A. J. van Doorn, The internal representation of solid shape with respect to vision, Biol. Cybern. 32, 211-216 (1979).",
            page=10,
            y0=130.0,
            width=360.0,
        )
        record["source_spans"][0]["bbox"]["x0"] = 122.0

        self.assertTrue(_is_reference_start(record))

    def test_numbered_references_heading_normalizes_to_references(self) -> None:
        self.assertEqual(_normalize_section_title("6 References"), "references")

    def test_trim_embedded_display_math_removes_leading_formula_echo_before_prose(self) -> None:
        record = _record(
            record_type="paragraph",
            text="; M ( u ) = u d M d + u d ; 1 M d ; 1 + : : : + uM 1 + M 0 : ( 1) where M i 's are matrices of order 2 mn with numeric entries.",
            page=7,
            y0=333.0,
            height=86.0,
            width=468.0,
        )
        overlapping_math = [
            {
                "id": "mathpix-eq-p007-0019",
                "kind": "display",
                "display_latex": r"\mathbf{M}(\bar{u})=\bar{u}^{d} M_{d}+\bar{u}^{d-1} M_{d-1}+\ldots+\bar{u} M_{1}+M_{0}",
                "source_spans": [
                    {
                        "page": 7,
                        "bbox": {
                            "x0": 200.0,
                            "y0": 345.5,
                            "x1": 411.5,
                            "y1": 365.0,
                            "width": 211.5,
                            "height": 19.5,
                        },
                        "engine": "mathpix",
                    }
                ],
            }
        ]

        trimmed = _trim_embedded_display_math_from_paragraph(record["text"], record, overlapping_math)

        self.assertEqual(trimmed, "where M i 's are matrices of order 2 mn with numeric entries.")

    def test_trim_embedded_display_math_keeps_leading_inline_math_when_no_display_overlap(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Given a surface F ( s;; t ), we compute its implicit representation.",
            page=7,
            y0=264.0,
            height=24.0,
            width=320.0,
        )

        trimmed = _trim_embedded_display_math_from_paragraph(record["text"], record, [])

        self.assertEqual(trimmed, "Given a surface F ( s;; t ), we compute its implicit representation.")

    def test_trim_embedded_display_math_keeps_leading_prose_before_bare_they(self) -> None:
        text = (
            "reproject those samples in the camera of the next frame f i + 1 following the 3D animation "
            "to approximate the contour motion (Figure 9.9d). Then, they locally search in image-space the "
            "location of the closest contour paths in the new view (Figure 9.9e)."
        )
        record = _record(
            record_type="paragraph",
            text=text,
            page=96,
            y0=330.17,
            height=169.37,
            width=433.98,
        )
        overlapping_math = [
            {
                "id": "mathpix-eq-p096-0001",
                "kind": "display",
                "display_latex": r"f_{i+1}",
                "source_spans": [
                    {
                        "page": 96,
                        "bbox": {
                            "x0": 300.0,
                            "y0": 340.0,
                            "x1": 340.0,
                            "y1": 356.0,
                            "width": 40.0,
                            "height": 16.0,
                        },
                        "engine": "mathpix",
                    }
                ],
            }
        ]

        trimmed = _trim_embedded_display_math_from_paragraph(text, record, overlapping_math)

        self.assertTrue(trimmed.startswith("reproject those samples"))

    def test_inject_external_math_anchors_before_formula_echo_block(self) -> None:
        layout_blocks = [
            LayoutBlock(
                id="#/texts/55",
                page=7,
                order=4,
                text="The resulting matrix M ( u ) can be represented as",
                role="paragraph",
                bbox={"x0": 72.0, "y0": 264.97, "x1": 540.24, "y1": 339.86, "width": 468.24, "height": 74.89},
                meta={"docling_label": "text"},
            ),
            LayoutBlock(
                id="#/texts/57",
                page=7,
                order=5,
                text="; M ( u ) = u d M d + u d ; 1 M d ; 1 + : : : + uM 1 + M 0 : ( 1) where M i 's are matrices of order 2 mn with numeric entries.",
                role="paragraph",
                bbox={"x0": 72.0, "y0": 333.38, "x1": 540.0, "y1": 420.01, "width": 468.0, "height": 86.63},
                meta={"docling_label": "text"},
            ),
        ]
        records = []
        for block in layout_blocks:
            record = block.as_record()
            record["type"] = block.role
            record["group_index"] = block.order * 10
            record["text"] = block.text
            record["meta"] = dict(block.meta)
            records.append(record)
        external_math_entries = [
            {
                "id": "mathpix-eq-p007-0019",
                "kind": "display",
                "display_latex": r"\mathbf{M}(\bar{u})=\bar{u}^{d} M_{d}+\bar{u}^{d-1} M_{d-1}+\ldots+\bar{u} M_{1}+M_{0}",
                "source_spans": [
                    {
                        "page": 7,
                        "bbox": {
                            "x0": 200.0,
                            "y0": 345.5,
                            "x1": 411.5,
                            "y1": 365.0,
                            "width": 211.5,
                            "height": 19.5,
                        },
                        "engine": "mathpix",
                    }
                ],
            }
        ]

        injected_records, _ = _inject_external_math_records(records, layout_blocks, external_math_entries)
        ordered_ids = [record["id"] for record in injected_records]

        self.assertLess(ordered_ids.index("external-math-record-mathpix-eq-p007-0019"), ordered_ids.index("#/texts/57"))

    def test_repair_record_text_with_mathpix_hints_prefers_better_inline_math_text(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Given a surface F ( s;; t ), we compute its implicit representation and obtain a matrix formulation M ( x;; y;; z;; w ).",
            page=7,
            y0=264.0,
            height=32.0,
            width=468.0,
        )

        mathpix_layout = {
            "engine": "mathpix",
            "blocks": [
                LayoutBlock(
                    id="mathpix-p007-b0013",
                    page=7,
                    order=1,
                    text=r"Given a surface \( \mathbf{F}(s, t) \), we compute its implicit representation",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 263.0, "x1": 541.5, "y1": 278.0, "width": 471.0, "height": 15.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p007-b0014",
                    page=7,
                    order=2,
                    text=r"and obtain a matrix formulation \( \mathbf{M}(x, y, z, w) \).",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 276.0, "x1": 541.5, "y1": 289.0, "width": 471.0, "height": 13.0},
                    meta={"mathpix_type": "text"},
                ),
            ],
        }

        repaired = _repair_record_text_with_mathpix_hints([record], mathpix_layout)

        self.assertEqual(
            repaired[0]["text"],
            r"Given a surface \( \mathbf{F}(s, t) \), we compute its implicit representation and obtain a matrix formulation \( \mathbf{M}(x, y, z, w) \).",
        )
        self.assertEqual(repaired[0]["meta"]["text_engine"], "mathpix_text_hint")

    def test_repair_record_text_with_mathpix_hints_drops_leading_neighbor_fragment(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Given a surface F ( s;; t ), we compute its implicit representation using resultant methods [Dix 0 8] and obtain a matrix formulation M ( x;; y;; z;; w ).",
            page=7,
            y0=264.97,
            height=74.89,
            width=468.24,
        )

        mathpix_layout = {
            "engine": "mathpix",
            "blocks": [
                LayoutBlock(
                    id="mathpix-p007-b0012",
                    page=7,
                    order=1,
                    text="computations [MD94].",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 245.0, "x1": 180.0, "y1": 259.5, "width": 109.5, "height": 14.5},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p007-b0013",
                    page=7,
                    order=2,
                    text=r"Given a surface \( \mathbf{F}(s, t) \), we compute its implicit representation using resultant methods [Dix08] and",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 263.0, "x1": 541.5, "y1": 278.0, "width": 471.0, "height": 15.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p007-b0014",
                    page=7,
                    order=3,
                    text=r"obtain a matrix formulation \( \mathbf{M}(x, y, z, w) \).",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 276.0, "x1": 541.5, "y1": 289.0, "width": 471.0, "height": 13.0},
                    meta={"mathpix_type": "text"},
                ),
            ],
        }

        repaired = _repair_record_text_with_mathpix_hints([record], mathpix_layout)

        self.assertEqual(
            repaired[0]["text"],
            r"Given a surface \( \mathbf{F}(s, t) \), we compute its implicit representation using resultant methods [Dix08] and obtain a matrix formulation \( \mathbf{M}(x, y, z, w) \).",
        )

    def test_repair_record_text_with_mathpix_hints_skips_short_ocr_fragments(self) -> None:
        record = {
            "id": "frag-1",
            "page": 9,
            "type": "paragraph",
            "text": "o",
            "source_spans": [
                {
                    "page": 9,
                    "bbox": {
                        "x0": 358.56,
                        "y0": 71.35,
                        "x1": 413.17,
                        "y1": 154.02,
                        "width": 54.61,
                        "height": 82.67,
                    },
                    "engine": "docling",
                }
            ],
            "meta": {},
        }

        mathpix_layout = {
            "engine": "mathpix",
            "blocks": [
                LayoutBlock(
                    id="mathpix-p009-b0057",
                    page=9,
                    order=1,
                    text=r"Figure 10. Let \( \sigma_{1} \) be the chain in the boundary of",
                    role="paragraph",
                    bbox={"x0": 320.65, "y0": 68.0, "x1": 548.0, "y1": 81.0, "width": 227.35, "height": 13.0},
                    meta={"mathpix_type": "text"},
                ),
            ],
        }

        repaired = _repair_record_text_with_mathpix_hints([record], mathpix_layout)

        self.assertEqual(repaired[0]["text"], "o")
        self.assertNotIn("text_engine", repaired[0]["meta"])

    def test_repair_record_text_with_mathpix_hints_restores_truncated_prose_lead(self) -> None:
        record = {
            "id": "frag-2",
            "page": 8,
            "type": "paragraph",
            "text": (
                "itory, and the change protocol establishing the connection between the elements "
                "of the old and the new net shape. The master model now calls on each application "
                "client and requests an update of the information that was associated with the old net shape."
            ),
            "source_spans": [
                {
                    "page": 8,
                    "bbox": {
                        "x0": 107.04,
                        "y0": 296.26,
                        "x1": 484.07,
                        "y1": 420.0,
                        "width": 377.03,
                        "height": 123.74,
                    },
                    "engine": "docling",
                }
            ],
            "meta": {},
        }

        mathpix_layout = {
            "engine": "mathpix",
            "blocks": [
                LayoutBlock(
                    id="mathpix-p008-b0021",
                    page=8,
                    order=1,
                    text="After the net shape has been edited in the CAD system, the master model",
                    role="paragraph",
                    bbox={"x0": 105.0, "y0": 300.0, "x1": 485.0, "y1": 313.0, "width": 380.0, "height": 13.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0022",
                    page=8,
                    order=2,
                    text="receives the new net shape, its identification in the CAD system's private repos",
                    role="paragraph",
                    bbox={"x0": 106.0, "y0": 313.0, "x1": 485.0, "y1": 327.0, "width": 379.0, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0023",
                    page=8,
                    order=3,
                    text="itory, and the change protocol establishing the connection between the elements",
                    role="paragraph",
                    bbox={"x0": 105.0, "y0": 327.0, "x1": 485.0, "y1": 340.0, "width": 380.0, "height": 13.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0024",
                    page=8,
                    order=4,
                    text="of the old and the new net shape. The master model now calls on each application",
                    role="paragraph",
                    bbox={"x0": 105.0, "y0": 340.5, "x1": 485.0, "y1": 354.5, "width": 380.0, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0025",
                    page=8,
                    order=5,
                    text="client and requests an update of the information that was associated with the old net shape.",
                    role="paragraph",
                    bbox={"x0": 105.0, "y0": 354.0, "x1": 485.0, "y1": 367.5, "width": 380.0, "height": 13.5},
                    meta={"mathpix_type": "text"},
                ),
            ],
        }

        repaired = _repair_record_text_with_mathpix_hints([record], mathpix_layout)

        self.assertTrue(repaired[0]["text"].startswith("After the net shape has been edited"))
        self.assertIn("private repos itory", repaired[0]["text"])
        self.assertEqual(repaired[0]["meta"]["text_engine"], "mathpix_prose_hint")

    def test_repair_record_text_with_mathpix_hints_keeps_best_contiguous_slice(self) -> None:
        record = _record(
            record_type="paragraph",
            text="1 The basic idea of power iterations can be used and modi ed to obtain the eigenvalue of a matrix A that is closest to a given guess s . It actually corresponds to the largest eigenvalue of the matrix ( A ; s I ) ; 1 . Instead of computing the inverse explicitly (which can be numerically unstable), we use inverse power iterations. Given an initial unit vector q 0 , we generate a sequence of vectors q k as Solve ( A ; s I ) z k = q k 1 ;; q k = z k = k z k k ;; s k = q T k Aq k ;;",
            page=8,
            y0=80.41,
            height=119.04,
            width=468.0,
        )

        mathpix_layout = {
            "engine": "mathpix",
            "blocks": [
                LayoutBlock(
                    id="mathpix-p008-b0001",
                    page=8,
                    order=1,
                    text=r"where \( \left\|\mathbf{z}_{k}\right\|_{\infty} \) refers to the infinity norm of the vector \( \mathbf{z}_{k} \cdot s_{k} \) converges to the largest eigenvalue",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 73.0, "x1": 542.0, "y1": 87.0, "width": 471.5, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0003",
                    page=8,
                    order=2,
                    text="The basic idea of power iterations can be used and modified to obtain the eigenvalue of a matrix",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 106.5, "x1": 541.5, "y1": 120.5, "width": 471.0, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0004",
                    page=8,
                    order=3,
                    text=r"\( A \) that is closest to a given guess \( s \). It actually corresponds to the largest eigenvalue of the matrix",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 120.0, "x1": 541.5, "y1": 134.5, "width": 471.0, "height": 14.5},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0005",
                    page=8,
                    order=4,
                    text=r"\( (\mathbf{A}-s \mathbf{I})^{-1} \). Instead of computing the inverse explicitly (which can be numerically unstable), we",
                    role="paragraph",
                    bbox={"x0": 71.0, "y0": 133.5, "x1": 541.5, "y1": 148.0, "width": 470.5, "height": 14.5},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0006",
                    page=8,
                    order=5,
                    text=r"use inverse power iterations. Given an initial unit vector \( \mathbf{q}_{0} \), we generate a sequence of vectors \( \mathbf{q}_{k} \)",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 147.5, "x1": 541.5, "y1": 161.5, "width": 471.0, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0007",
                    page=8,
                    order=6,
                    text="as",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 162.0, "x1": 87.0, "y1": 174.5, "width": 16.5, "height": 12.5},
                    meta={"mathpix_type": "text"},
                ),
                LayoutBlock(
                    id="mathpix-p008-b0009",
                    page=8,
                    order=7,
                    text="We use inverse power iterations to trace curves. We formulate the curve as the singular set of",
                    role="paragraph",
                    bbox={"x0": 70.5, "y0": 194.5, "x1": 541.5, "y1": 208.5, "width": 471.0, "height": 14.0},
                    meta={"mathpix_type": "text"},
                ),
            ],
        }

        repaired = _repair_record_text_with_mathpix_hints([record], mathpix_layout)

        self.assertEqual(
            repaired[0]["text"],
            r"The basic idea of power iterations can be used and modified to obtain the eigenvalue of a matrix \( A \) that is closest to a given guess \( s \). It actually corresponds to the largest eigenvalue of the matrix \( (\mathbf{A}-s \mathbf{I})^{-1} \). Instead of computing the inverse explicitly (which can be numerically unstable), we use inverse power iterations. Given an initial unit vector \( \mathbf{q}_{0} \), we generate a sequence of vectors \( \mathbf{q}_{k} \) as",
        )

    def test_tiny_ocr_paragraph_with_measurements_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Maximum Speed: 180 mph (290 km h)",
            page=8,
            y0=63.22,
            height=3.99,
            width=63.94,
        )

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_single_asterisk_paragraph_is_filtered(self) -> None:
        record = _record(record_type="paragraph", text="*", page=1, y0=153.59, height=7.45, width=2.73)

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_browser_ui_scrap_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text="10t localhostb3342 modes him modes himi? mauto ossssbukthyacosais& i relond=KElDAD ON SAV",
            page=21,
            y0=247.07,
            height=9.78,
            width=26.84,
        )

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_quoted_identifier_fragment_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text='with_datum_reference" ?',
            page=14,
            y0=235.26,
            height=9.99,
            width=90.45,
        )

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_single_letter_glyph_cloud_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text="i ii i ~ i ~ ! i ! ~ i i i i ~ i ~",
            page=6,
            y0=284.64,
            height=19.12,
            width=221.28,
        )

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_single_letter_glyph_cloud_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text="i ii i ~ i ~ !",
            page=9,
            y0=65.51,
            height=28.21,
            width=35.81,
        )

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_control_flow_stub_is_filtered(self) -> None:
        record = _record(record_type="paragraph", text="end if", page=10, y0=625.04, height=7.45, width=21.85)

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_zero_width_negationslash_scrap_is_filtered(self) -> None:
        record = _record(
            record_type="paragraph",
            text="negationslash are called critical regions for the pair ( S1 , S2 )",
            page=6,
            y0=536.82,
            height=13.65,
            width=0.0,
        )
        record["source_spans"][0]["bbox"]["x0"] = 497.34
        record["source_spans"][0]["bbox"]["x1"] = 497.34

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_tiny_multi_span_synthetic_math_cluster_is_filtered(self) -> None:
        spans = [
            _record(record_type="paragraph", text="Performance", page=8, y0=55.24, height=3.32, width=21.98)["source_spans"][0],
            _record(record_type="paragraph", text="Maximum Speed: 180 mph (290 km h)", page=8, y0=63.22, height=3.99, width=63.94)["source_spans"][0],
            _record(record_type="paragraph", text="Cruise Speed: 130 mph (209 km h)", page=8, y0=67.21, height=4.0, width=61.94)["source_spans"][0],
            _record(record_type="paragraph", text="Range: 3,200 mile (5,150 km)", page=8, y0=71.21, height=3.99, width=54.61)["source_spans"][0],
            _record(record_type="paragraph", text="Service Ceiling: 10,000 ft (3,048 m)", page=8, y0=75.2, height=3.99, width=69.93)["source_spans"][0],
        ]
        record = {
            "id": "synthetic-math-ocr-cluster",
            "page": 8,
            "type": "paragraph",
            "text": "Performance Maximum Speed: 180 mph (290 km h) Cruise Speed: 130 mph (209 km h) Range: 3,200 mile (5,150 km) Service Ceiling: 10,000 ft (3,048 m)",
            "source_spans": spans,
            "meta": {"forced_math_kind": "group"},
        }

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_forced_math_label_cloud_is_filtered(self) -> None:
        spans = [
            _record(record_type="paragraph", text="e2", page=11, y0=812.37, width=16.49)["source_spans"][0],
            _record(record_type="paragraph", text="V3", page=11, y0=815.67, width=14.83)["source_spans"][0],
            _record(record_type="paragraph", text="v2", page=11, y0=822.28, width=18.14)["source_spans"][0],
            _record(record_type="paragraph", text="e1", page=11, y0=830.53, width=14.84)["source_spans"][0],
            _record(record_type="paragraph", text="e3", page=11, y0=830.53, width=14.84)["source_spans"][0],
            _record(record_type="paragraph", text="(a)", page=11, y0=957.67, width=21.44)["source_spans"][0],
            _record(record_type="paragraph", text="(b)", page=11, y0=959.33, width=23.08)["source_spans"][0],
            _record(record_type="paragraph", text="(C)", page=11, y0=959.33, width=21.43)["source_spans"][0],
        ]
        record = {
            "id": "synthetic-math-figure-label-cloud",
            "page": 11,
            "type": "paragraph",
            "text": "e2 V3 v2 e1 e3 (a) (b) (C)",
            "source_spans": spans,
            "meta": {"forced_math_kind": "group"},
        }

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_forced_math_vertical_label_cloud_is_filtered(self) -> None:
        spans = [
            _record(record_type="paragraph", text="Mapping scope", page=20, y0=14.42, height=11.46, width=68.7)["source_spans"][0],
            _record(record_type="paragraph", text="Mapping type", page=20, y0=14.67, height=10.66, width=61.33)["source_spans"][0],
            _record(record_type="paragraph", text="High cost", page=20, y0=42.61, height=43.95, width=11.34)["source_spans"][0],
            _record(record_type="paragraph", text="Commercially protected", page=20, y0=43.28, height=105.86, width=12.0)["source_spans"][0],
            _record(record_type="paragraph", text="Inconsistent", page=20, y0=60.97, height=11.89, width=56.12)["source_spans"][0],
            _record(record_type="paragraph", text="Inflexible", page=20, y0=97.21, height=41.95, width=10.67)["source_spans"][0],
            _record(record_type="paragraph", text="Not", page=20, y0=59.92, height=10.66, width=18.67)["source_spans"][0],
            _record(record_type="paragraph", text="Different", page=20, y0=59.47, height=10.23, width=39.54)["source_spans"][0],
        ]
        record = {
            "id": "synthetic-math-vertical-label-cloud",
            "page": 20,
            "type": "paragraph",
            "text": "Mapping scope Mapping type High cost Commercially protected Inconsistent Inflexible Not Different",
            "source_spans": spans,
            "meta": {"forced_math_kind": "group"},
        }

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_vertical_label_cloud_is_filtered_without_forced_math_hint(self) -> None:
        spans = [
            _record(record_type="paragraph", text="Mapping scope", page=20, y0=14.42, height=11.46, width=68.7)["source_spans"][0],
            _record(record_type="paragraph", text="Mapping type", page=20, y0=14.67, height=10.66, width=61.33)["source_spans"][0],
            _record(record_type="paragraph", text="High cost", page=20, y0=42.61, height=43.95, width=11.34)["source_spans"][0],
            _record(record_type="paragraph", text="Commercially protected", page=20, y0=43.28, height=105.86, width=12.0)["source_spans"][0],
            _record(record_type="paragraph", text="Inconsistent", page=20, y0=60.97, height=11.89, width=56.12)["source_spans"][0],
            _record(record_type="paragraph", text="Inflexible", page=20, y0=97.21, height=41.95, width=10.67)["source_spans"][0],
            _record(record_type="paragraph", text="Not", page=20, y0=59.92, height=10.66, width=18.67)["source_spans"][0],
            _record(record_type="paragraph", text="Different", page=20, y0=59.47, height=10.23, width=39.54)["source_spans"][0],
        ]
        record = {
            "id": "layout-vertical-label-cloud",
            "page": 20,
            "type": "paragraph",
            "text": "Mapping scope Mapping type High cost Commercially protected Inconsistent Inflexible Not Different",
            "source_spans": spans,
            "meta": {},
        }

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_same_page_flowchart_nodes_are_treated_as_figure_debris(self) -> None:
        figures_by_page = {
            14: [
                {
                    "id": "fig-11",
                    "bbox": {"x0": 157.32, "y0": 550.61, "x1": 490.25, "y1": 639.86, "width": 332.92, "height": 89.25},
                }
            ]
        }

        self.assertTrue(_is_figure_debris(_record(record_type="paragraph", text="Start", page=14, y0=78.36, width=20.0), figures_by_page))
        self.assertTrue(
            _is_figure_debris(
                _record(
                    record_type="paragraph",
                    text='Search entity "geometric_tolerance_with_datum_reference"',
                    page=14,
                    y0=213.6,
                    width=150.0,
                ),
                figures_by_page,
            )
        )

    def test_same_page_identifier_labels_are_treated_as_figure_debris(self) -> None:
        figures_by_page = {
            8: [
                {
                    "id": "fig-4",
                    "bbox": {"x0": 164.9, "y0": 491.72, "x1": 561.83, "y1": 653.03, "width": 396.93, "height": 161.31},
                }
            ]
        }

        self.assertTrue(
            _is_figure_debris(
                _record(
                    record_type="paragraph",
                    text="tessellated_annotation_occurrence shape_dimension_representation",
                    page=8,
                    y0=339.21,
                    width=150.0,
                ),
                figures_by_page,
            )
        )

    def test_long_step_data_line_paragraph_is_not_trimmed_to_resume_clause(self) -> None:
        text = (
            "The data line 'ADVANCED_FACE (', #462, #514, F.)' can be used to determine the data lines "
            "'#462=FACE_BOUND(,#410,.T.)' and '#514=PLANE(,#572)'. Identifier '#462' describes the boundary "
            "of the surface, and identifier '#514' shows that the surface type is a plane. Through '#514' "
            "the data line '#572=AXIS2_PLACEMENT_3D('', #816, #657, #658)' can be determined. This data line "
            "specifies the position and orientation of a surface in 3D space based on a point and two coordinate "
            "axes. The data line '#816=CARTESIAN_POINT('', (0, 0, 28))' represents the origin of the local "
            "coordinate system for this plane. The data lines '#657=DIRECTION('', (0, 1, 0))' and "
            "'#658=DIRECTION('', (0, 0, 1))' represent the Z-axis and X-axis directions of this local coordinate "
            "system, respectively. Thus, the position and normal vector of a 3D linear-size-associated surface "
            "can be determined."
        )

        trimmed = _trim_embedded_display_math_from_paragraph(
            text,
            _record(record_type="paragraph", text=text, page=27, y0=514.17, height=134.79, width=395.18),
            [],
        )

        self.assertEqual(trimmed, text)

    def test_same_page_explanatory_prose_is_not_treated_as_figure_debris(self) -> None:
        figures_by_page = {
            8: [
                {
                    "id": "fig-4",
                    "bbox": {"x0": 164.9, "y0": 491.72, "x1": 561.83, "y1": 653.03, "width": 396.93, "height": 161.31},
                }
            ]
        }

        self.assertFalse(
            _is_figure_debris(
                _record(
                    record_type="paragraph",
                    text="For example, using the part depicted in Figure 4, the process of extracting information is as follows.",
                    page=8,
                    y0=430.0,
                    width=320.0,
                ),
                figures_by_page,
            )
        )

    def test_external_math_record_is_not_treated_as_figure_debris(self) -> None:
        figures_by_page = {
            4: [
                {
                    "id": "fig-4",
                    "bbox": {"x0": 40.0, "y0": 280.0, "x1": 290.0, "y1": 360.0, "width": 250.0, "height": 80.0},
                }
            ]
        }
        record = _record(
            record_type="paragraph",
            text=r"\begin{equation*} \sum_{i=0}^{I-1} B_{i, p}(u) c_{i}=0 \tag{5} \end{equation*}",
            page=4,
            y0=316.45,
            height=31.49,
            width=67.47,
        )
        record["source_spans"][0]["bbox"]["x0"] = 49.48
        record["source_spans"][0]["bbox"]["x1"] = 116.96
        record["meta"] = {
            "external_math_entry": {
                "id": "mathpix-eq-p004-0015",
                "kind": "display",
                "display_latex": record["text"],
            },
            "forced_math_kind": "display",
        }

        self.assertFalse(_is_figure_debris(record, figures_by_page))

    def test_short_multiword_in_figure_label_is_treated_as_figure_debris(self) -> None:
        figures_by_page = {
            7: [
                {
                    "id": "fig-7",
                    "bbox": {"x0": 70.0, "y0": 300.0, "x1": 275.0, "y1": 355.0, "width": 205.0, "height": 55.0},
                }
            ]
        }
        record = _record(
            record_type="paragraph",
            text="Cone on a surface Contour generator",
            page=7,
            y0=341.19,
            height=6.7,
            width=108.66,
        )
        record["source_spans"][0]["bbox"]["x0"] = 81.02
        record["source_spans"][0]["bbox"]["x1"] = 189.68

        self.assertTrue(_is_figure_debris(record, figures_by_page))

    def test_prose_like_external_math_entry_is_injected_as_paragraph(self) -> None:
        layout_blocks = [
            LayoutBlock(
                id="anchor",
                page=3,
                order=20,
                text="Definitions continue here.",
                role="paragraph",
                bbox={"x0": 430.0, "y0": 980.0, "x1": 780.0, "y1": 1010.0, "width": 350.0, "height": 30.0},
            )
        ]
        records, _ = _inject_external_math_records(
            [],
            layout_blocks,
            [
                {
                    "id": "ext-eq-1",
                    "kind": "display",
                    "display_latex": "In view of the above, we define an open disk A = Int(M),",
                    "source_spans": [
                        {
                            "page": 3,
                            "bbox": {"x0": 449.83, "y0": 1038.01, "x1": 783.89, "y1": 1054.69, "width": 334.06, "height": 16.68},
                            "engine": "docling",
                        }
                    ],
                }
            ],
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["type"], "paragraph")
        self.assertEqual(records[0]["text"], "In view of the above, we define an open disk A = Int(M),")
        self.assertNotIn("forced_math_kind", records[0]["meta"])
        self.assertNotIn("external_math_entry", records[0]["meta"])

    def test_same_page_column_continuation_paragraphs_are_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Once upon a time, the original vision of CAD was the holistic treatment of the engineering design process and visualization of",
            page=1,
            y0=558.32,
            height=47.26,
            width=240.64,
        )
        current = _record(
            record_type="paragraph",
            text="geometric objects. On the other hand, computational analysis has focused on the problem-solving part of engineering.",
            page=1,
            y0=283.32,
            height=84.76,
            width=240.65,
        )
        current["source_spans"][0]["bbox"]["x0"] = 306.14
        current["source_spans"][0]["bbox"]["x1"] = 546.79

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_short_same_page_tail_fragment_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="There have been varied approaches to the determination of line drawing visibility and all schemes implemented to date have assumed a limited vocabulary of solids or surfaces",
            page=1,
            y0=528.88,
            height=209.3,
            width=282.94,
        )
        current = _record(
            record_type="paragraph",
            text="of a complete line segment, there is no resolution problem.",
            page=1,
            y0=741.44,
            height=8.74,
            width=113.79,
        )
        current["source_spans"][0]["bbox"]["x0"] = 162.71
        current["source_spans"][0]["bbox"]["x1"] = 276.5

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_column_incomplete_sentence_with_moderate_gap_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="B-spline curves can be generalized to represent rational functions such as conic sections. For this purpose, weights are associated with the control points such that",
            page=5,
            y0=370.17,
            height=35.54,
            width=240.0,
        )
        current = _record(
            record_type="paragraph",
            text="where d denotes the spatial dimension of the model space.",
            page=5,
            y0=441.85,
            height=72.31,
            width=240.0,
        )

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_column_comma_ended_continuation_with_large_gap_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="consider whether several seven elements in (3.4) modulo R generate seven elements S,",
            page=21,
            y0=331.85,
            height=40.18,
            width=416.69,
        )
        current = _record(
            record_type="paragraph",
            text="to generate the monomials above.",
            page=21,
            y0=532.33,
            height=35.63,
            width=416.69,
        )

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_zero_width_continuation_fragment_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="A pair of domain partitions",
            page=6,
            y0=483.48,
            height=36.16,
            width=243.63,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 303.9
        previous["source_spans"][0]["bbox"]["x1"] = 547.53

        current = _record(
            record_type="paragraph",
            text="negationslash are called critical regions for the pair ( S1 , S2 )",
            page=6,
            y0=536.82,
            height=13.65,
            width=0.0,
        )
        current["source_spans"][0]["bbox"]["x0"] = 497.34
        current["source_spans"][0]["bbox"]["x1"] = 497.34

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_overlapping_same_column_continuation_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="After obtaining the parameter domain mesh, we map it to R3 space ... shared boundary",
            page=9,
            y0=660.58,
            height=74.62,
            width=243.49,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 309.51
        previous["source_spans"][0]["bbox"]["x1"] = 552.98

        current = _record(
            record_type="paragraph",
            text="points and the consistent cross-mapping of critical points-the resulting R3 mesh is inherently watertight.",
            page=9,
            y0=647.59,
            height=29.45,
            width=243.45,
        )
        current["source_spans"][0]["bbox"]["x0"] = 309.51
        current["source_spans"][0]["bbox"]["x1"] = 552.96

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_cross_page_column_reset_continuation_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="The reduced aspect graph and related approaches reduce the graph size, but a smaller representation remains desirable because the current discussion is re-",
            page=2,
            y0=597.67,
            height=401.33,
            width=351.18,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 453.41
        previous["source_spans"][0]["bbox"]["x1"] = 804.59
        current = _record(
            record_type="paragraph",
            text="duced to a smaller size by carrying the idea onto the next page and back to the left column.",
            page=3,
            y0=79.26,
            height=262.72,
            width=349.53,
        )
        current["source_spans"][0]["bbox"]["x0"] = 70.9
        current["source_spans"][0]["bbox"]["x1"] = 420.43

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_page_hyphenated_cross_column_continuation_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Each arc between a pair of nodes represents the adjacency between the corre-",
            page=1,
            y0=792.56,
            height=110.77,
            width=347.88,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 72.55
        previous["source_spans"][0]["bbox"]["x1"] = 420.43
        current = _record(
            record_type="paragraph",
            text="sponding characteristic view domains.",
            page=1,
            y0=755.21,
            height=134.79,
            width=349.64,
        )
        current["source_spans"][0]["bbox"]["x0"] = 454.95
        current["source_spans"][0]["bbox"]["x1"] = 804.59

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_cross_page_upper_half_continuation_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="The combination algorithm is restricted to combine EAGs where the higher level features such as pockets, or steps, are not interacting with each other",
            page=9,
            y0=635.67,
            height=54.66,
            width=347.89,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 456.7
        previous["source_spans"][0]["bbox"]["x1"] = 804.59
        current = _record(
            record_type="paragraph",
            text="on the new object. For example, if the EAG for a step is available and a new object has two steps intersecting with one another.",
            page=10,
            y0=213.0,
            height=189.88,
            width=349.59,
        )
        current["source_spans"][0]["bbox"]["x0"] = 70.9
        current["source_spans"][0]["bbox"]["x1"] = 420.49

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_column_then_continuation_with_large_gap_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Definition 2 (critical region). Let S1 and S2 be two NURBS surface patches. A pair of domain partitions",
            page=6,
            y0=483.48,
            height=36.16,
            width=243.63,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 303.9
        previous["source_spans"][0]["bbox"]["x1"] = 547.53
        current = _record(
            record_type="paragraph",
            text="Then, any pair of triangle meshes are guaranteed to be disjoint.",
            page=6,
            y0=616.57,
            height=73.45,
            width=243.56,
        )
        current["source_spans"][0]["bbox"]["x0"] = 303.9
        current["source_spans"][0]["bbox"]["x1"] = 547.46

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_page_cross_column_overlap_continuation_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="After obtaining the parameter domain mesh, we map it to R3 space and preserve the one-to-one correspondence of shared boundary",
            page=9,
            y0=660.58,
            height=74.62,
            width=243.49,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 48.26
        previous["source_spans"][0]["bbox"]["x1"] = 291.75
        current = _record(
            record_type="paragraph",
            text="points and the consistent cross-mapping of critical points-the resulting R3 mesh is inherently watertight and topologically consistent.",
            page=9,
            y0=647.59,
            height=29.45,
            width=243.45,
        )
        current["source_spans"][0]["bbox"]["x0"] = 309.51
        current["source_spans"][0]["bbox"]["x1"] = 552.96

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_cross_page_short_lowercase_tail_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Evaluation criteria include mesh generation time, triangle count, number of self-intersections, and Hausdorff",
            page=12,
            y0=636.37,
            height=106.45,
            width=243.81,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 303.9
        previous["source_spans"][0]["bbox"]["x1"] = 547.71
        current = _record(
            record_type="paragraph",
            text="distance computed using Metro tool (Cignoni et al. , 1998), scaled by 100 for readability.",
            page=13,
            y0=556.04,
            height=18.44,
            width=243.51,
        )
        current["source_spans"][0]["bbox"]["x0"] = 48.26
        current["source_spans"][0]["bbox"]["x1"] = 291.77

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_cross_page_full_width_lowercase_continuation_after_table_is_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="The pattern of recursive calls takes the form of a binary tree N levels deep. The leaves of the tree represent valid cell numbers. The number of calls",
            page=11,
            y0=932.06,
            height=139.06,
            width=602.85,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 81.08
        previous["source_spans"][0]["bbox"]["x1"] = 683.93

        current = _record(
            record_type="paragraph",
            text="cannot become exponential because, at certain nodes in the tree, entire subtrees are left undeveloped.",
            page=12,
            y0=874.08,
            height=39.77,
            width=604.39,
        )
        current["source_spans"][0]["bbox"]["x0"] = 77.82
        current["source_spans"][0]["bbox"]["x1"] = 682.21

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_merge_paragraph_blocks_merges_cross_column_sentence_continuation(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "The topology due to the STEP and IGES formats is compared and the provided edge loop data"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=30, y0=675.35, height=22.26, width=240.58)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "is shown in the appendix."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=30, y0=551.9, height=22.26, width=238.11)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        blocks[0]["source_spans"][0]["bbox"]["x0"] = 51.02
        blocks[0]["source_spans"][0]["bbox"]["x1"] = 291.6
        blocks[1]["source_spans"][0]["bbox"]["x0"] = 306.14
        blocks[1]["source_spans"][0]["bbox"]["x1"] = 544.25
        sections = [
            {
                "id": "sec-1",
                "label": "4.2",
                "title": "4.2 Test",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertEqual(
            merged_text,
            "The topology due to the STEP and IGES formats is compared and the provided edge loop data is shown in the appendix.",
        )
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_preserves_inline_math_refs(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "A tensor product patch with control points "}, {"kind": "inline_math_ref", "target_id": "math-inline-1"}, {"kind": "text", "text": " can be converted"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=39, y0=420.26, height=59.76, width=240.65)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "where "}, {"kind": "inline_math_ref", "target_id": "math-inline-2"}, {"kind": "text", "text": " are binomial coefficients."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=39, y0=570.79, height=49.21, width=240.62)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "4.5",
                "title": "4.5 Test",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, _ = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_spans = merged_blocks[0]["content"]["spans"]
        self.assertEqual(
            [span.get("target_id") for span in merged_spans if span.get("kind") == "inline_math_ref"],
            ["math-inline-1", "math-inline-2"],
        )

    def test_merge_paragraph_blocks_merges_short_lead_in_clause(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "This equation consists of"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=44, y0=442.03, height=9.76, width=99.51)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "representing the unknown control points."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=44, y0=519.96, height=97.52, width=240.62)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "5.3",
                "title": "5.3 Test",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertEqual(merged_text, "This equation consists of representing the unknown control points.")
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_standalone_where_with_following_continuation(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "where"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=2, y0=662.12, height=13.21, width=41.26)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "is the number of zones in which a hyperspace is divided by n hyperplanes."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=2, y0=743.0, height=97.0, width=333.43)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Introduction",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertEqual(merged_text, "where is the number of zones in which a hyperspace is divided by n hyperplanes.")
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_clause_lead_in_continuation(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "The prime limitation of this work is that it is applicable only to solids which"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=374.48, height=69.21, width=249.29)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "can be rendered with the current scheme."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=544.4, height=93.69, width=250.78)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Introduction",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertEqual(
            merged_text,
            "The prime limitation of this work is that it is applicable only to solids which can be rendered with the current scheme.",
        )
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_lowercase_wrap_reset(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {
                    "spans": [
                        {
                            "kind": "text",
                            "text": "This approach mimics human vision because we are often able to understand the solid shape of an object from a few image lines laid",
                        }
                    ]
                },
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=678.11, height=13.28, width=253.61)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "out on a plane [13], [16]."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=733.31, height=13.28, width=125.85)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        blocks[0]["source_spans"][0]["bbox"]["x0"] = 288.04
        blocks[0]["source_spans"][0]["bbox"]["x1"] = 541.65
        blocks[1]["source_spans"][0]["bbox"]["x0"] = 56.68
        blocks[1]["source_spans"][0]["bbox"]["x1"] = 182.53
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Introduction",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertEqual(
            merged_text,
            "This approach mimics human vision because we are often able to understand the solid shape of an object from a few image lines laid out on a plane [13], [16].",
        )
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_full_width_page_turn_after_conjunction(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {
                    "spans": [
                        {
                            "kind": "text",
                            "text": (
                                "Parameterization propagation. Another solution to these topological issues is to propagate "
                                "the parameterization of the strokes instead of their geometry. They sample the "
                                "parametrization of the strokes at frame f_i uniformly along their arc-length, and"
                            ),
                        }
                    ]
                },
                "source_spans": _record(record_type="paragraph", text="stub", page=95, y0=668.91, height=55.11, width=434.41)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {
                    "spans": [
                        {
                            "kind": "text",
                            "text": (
                                "reproject those samples in the camera of the next frame following the 3D animation "
                                "to approximate the contour motion."
                            ),
                        }
                    ]
                },
                "source_spans": _record(record_type="paragraph", text="stub", page=96, y0=330.17, height=169.37, width=433.98)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "9.5",
                "title": "9.5 Animation",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertIn("and reproject those samples", merged_text)
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_page_turn_after_embedded_procedia_header(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {
                    "spans": [
                        {
                            "kind": "text",
                            "text": (
                                "Within the MBD philosophy a CAD model is created using nominal values "
                                "and the required tolerances are added as 3D Author name Procedia CIRP 00 (2018) 000"
                            ),
                        }
                    ]
                },
                "source_spans": _record(record_type="paragraph", text="stub", page=5, y0=756.81, height=20.6, width=252.7)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {
                    "spans": [
                        {
                            "kind": "text",
                            "text": "annotations, the so-called PMI data. For typical mechanical parts these tolerances have a range of a few µm.",
                        }
                    ]
                },
                "source_spans": _record(record_type="paragraph", text="stub", page=6, y0=74.58, height=104.64, width=252.98)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "4",
                "title": "4 Discussion",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 1)
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in merged_blocks[0]["content"]["spans"]
        )
        self.assertIn("added as 3D Author name Procedia CIRP 00 (2018) 000 annotations", merged_text)
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_should_merge_paragraph_records_ignores_top_margin_header_anchor_span(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Within the MBD philosophy a CAD model is created using nominal values and the required tolerances are added as 3D",
            page=5,
            y0=756.81,
            height=20.6,
            width=252.7,
        )
        previous["source_spans"].append(
            _record(
                record_type="paragraph",
                text="Author name Procedia CIRP 00 (2018) 000",
                page=6,
                y0=52.33,
                height=6.92,
                width=144.31,
            )["source_spans"][0]
        )
        current = _record(
            record_type="paragraph",
            text="annotations, the so-called PMI data. For typical mechanical parts these tolerances have a range of a few µm.",
            page=6,
            y0=74.58,
            height=104.64,
            width=252.98,
        )

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_should_merge_paragraph_records_merges_same_page_figure_interrupted_lead_in(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="Pass 2 Let sigma_1 be the chain in the boundary of",
            page=9,
            y0=637.19,
            height=42.61,
            width=226.63,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 63.36
        previous["source_spans"][0]["bbox"]["x1"] = 289.99
        previous["source_spans"].insert(
            0,
            _record(
                record_type="paragraph",
                text="stub",
                page=9,
                y0=625.16,
                height=7.99,
                width=35.36,
            )["source_spans"][0],
        )
        previous["source_spans"][0]["bbox"]["x0"] = 63.36
        previous["source_spans"][0]["bbox"]["x1"] = 98.72
        previous["source_spans"].extend(
            [
                _record(
                    record_type="paragraph",
                    text="stub",
                    page=9,
                    y0=41.51,
                    height=30.85,
                    width=229.45,
                )["source_spans"][0],
                _record(
                    record_type="paragraph",
                    text="stub",
                    page=9,
                    y0=71.35,
                    height=82.67,
                    width=54.61,
                )["source_spans"][0],
            ]
        )
        previous["source_spans"][2]["bbox"]["x0"] = 320.65
        previous["source_spans"][2]["bbox"]["x1"] = 550.10
        previous["source_spans"][3]["bbox"]["x0"] = 358.56
        previous["source_spans"][3]["bbox"]["x1"] = 413.17
        current = _record(
            record_type="paragraph",
            text="the region on the other side of s from which s can be seen along horizontal rays arbitrarily near p.",
            page=9,
            y0=420.95,
            height=114.61,
            width=228.57,
        )
        current["source_spans"][0]["bbox"]["x0"] = 319.44
        current["source_spans"][0]["bbox"]["x1"] = 548.01

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_merge_paragraph_records_merges_across_caption_interruption(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="These types of errors,",
            page=3,
            y0=462.32,
            height=92.38,
            width=251.06,
        )
        previous["source_spans"][0]["bbox"]["x0"] = 42.52
        previous["source_spans"][0]["bbox"]["x1"] = 293.58

        caption = _record(
            record_type="caption",
            text="Table 1 Classification and frequency of the six error types",
            page=3,
            y0=564.45,
            height=16.93,
            width=161.46,
        )
        caption["source_spans"][0]["bbox"]["x0"] = 42.52
        caption["source_spans"][0]["bbox"]["x1"] = 203.98

        current = _record(
            record_type="paragraph",
            text="which are caused by mismatches in the numerical inaccuracies of the heterogeneous kernel.",
            page=3,
            y0=70.58,
            height=45.26,
            width=250.99,
        )
        current["source_spans"][0]["bbox"]["x0"] = 311.53
        current["source_spans"][0]["bbox"]["x1"] = 562.52

        merged = _merge_paragraph_records([previous, caption, current])

        self.assertEqual([record["type"] for record in merged], ["paragraph", "caption"])
        self.assertIn("These types of errors, which are caused by mismatches", merged[0]["text"])

    def test_normalize_footnote_blocks_promotes_and_merges_footnote_tail(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "*A good machine independent measure of visibility."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=662.24, height=79.53, width=271.32)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "point 387"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=742.64, height=8.73, width=26.39)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-3",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "for the same object."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=742.64, height=8.73, width=18.1)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Introduction",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-paragraph-2", "blk-paragraph-3"],
                "children": [],
                "source_spans": [],
            }
        ]

        normalized_blocks, normalized_sections = _normalize_footnote_blocks(blocks, sections)

        self.assertEqual(len(normalized_blocks), 1)
        self.assertEqual(normalized_blocks[0]["type"], "footnote")
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in normalized_blocks[0]["content"]["spans"]
        )
        self.assertIn("point 387", merged_text)
        self.assertIn("for the same object.", merged_text)
        self.assertEqual(normalized_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_merge_paragraph_blocks_merges_across_intervening_footnote(self) -> None:
        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "The author has developed a scheme for the perspec-"}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=1, y0=641.6, height=8.73, width=247.69)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-footnote-2",
                "type": "footnote",
                "content": {"spans": [{"kind": "text", "text": "*A footnote."}]},
                "source_spans": _record(record_type="footnote", text="stub", page=1, y0=662.24, height=30.0, width=271.32)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-3",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "tive rendering of assemblies of planes in space."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=2, y0=103.6, height=50.0, width=255.98)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Introduction",
                "level": 1,
                "block_ids": ["blk-paragraph-1", "blk-footnote-2", "blk-paragraph-3"],
                "children": [],
                "source_spans": [],
            }
        ]

        merged_blocks, merged_sections = _merge_paragraph_blocks(blocks, sections)

        self.assertEqual(len(merged_blocks), 2)
        paragraph_block = next(block for block in merged_blocks if block["id"] == "blk-paragraph-1")
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in paragraph_block["content"]["spans"]
        )
        self.assertEqual(
            merged_text,
            "The author has developed a scheme for the perspec- tive rendering of assemblies of planes in space.",
        )
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1", "blk-footnote-2"])

    def test_suppress_running_header_blocks_trims_headers_before_merge(self) -> None:
        trailing_header_span = _record(record_type="paragraph", text="stub", page=6, y0=36.41, height=8.29, width=38.5)["source_spans"][0]
        header_span_page6 = _record(record_type="paragraph", text="stub", page=6, y0=36.41, height=8.29, width=38.31)["source_spans"][0]
        header_span_page7 = _record(record_type="paragraph", text="stub", page=7, y0=36.41, height=8.29, width=38.31)["source_spans"][0]
        header_span_page8 = _record(record_type="paragraph", text="stub", page=8, y0=36.41, height=8.29, width=38.31)["source_spans"][0]

        blocks = [
            {
                "id": "blk-paragraph-1",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "Suppose the jump function is constant on each PIGNONI"}]},
                "source_spans": [
                    _record(record_type="paragraph", text="stub", page=5, y0=579.61, height=22.67, width=345.07)["source_spans"][0],
                    trailing_header_span,
                ],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-2",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "PIGNONI"}]},
                "source_spans": [header_span_page6],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-3",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "PIGNONI"}]},
                "source_spans": [header_span_page7],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-4",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "PIGNONI"}]},
                "source_spans": [header_span_page8],
                "alternates": [],
                "review": _review(),
            },
            {
                "id": "blk-paragraph-5",
                "type": "paragraph",
                "content": {"spans": [{"kind": "text", "text": "convex arc, and its value jumps by two."}]},
                "source_spans": _record(record_type="paragraph", text="stub", page=6, y0=64.25, height=8.29, width=328.55)["source_spans"],
                "alternates": [],
                "review": _review(),
            },
        ]
        sections = [
            {
                "id": "sec-1",
                "label": "1",
                "title": "Test",
                "level": 1,
                "block_ids": [
                    "blk-paragraph-1",
                    "blk-paragraph-2",
                    "blk-paragraph-3",
                    "blk-paragraph-4",
                    "blk-paragraph-5",
                ],
                "children": [],
                "source_spans": [],
            }
        ]

        suppressed_blocks, suppressed_sections = _suppress_running_header_blocks(blocks, sections)
        merged_blocks, merged_sections = _merge_paragraph_blocks(suppressed_blocks, suppressed_sections)

        self.assertEqual([block["id"] for block in merged_blocks], ["blk-paragraph-1"])
        paragraph_block = next(block for block in merged_blocks if block["id"] == "blk-paragraph-1")
        merged_text = "".join(
            span.get("text", "") if span.get("kind") == "text" else "[M]"
            for span in paragraph_block["content"]["spans"]
        )
        self.assertEqual(
            merged_text,
            "Suppose the jump function is constant on each convex arc, and its value jumps by two.",
        )
        self.assertEqual(merged_sections[0]["block_ids"], ["blk-paragraph-1"])

    def test_front_matter_body_fragment_is_treated_as_paragraph_continuation(self) -> None:
        previous = _record(
            record_type="front_matter",
            text="INTRODUCTION Line drawings are the most common type of rendering used to convey geometrical description and enable comparitively high speed calculation and excel",
            page=1,
            y0=288.09,
            height=213.69,
            width=290.13,
        )
        current = _record(
            record_type="paragraph",
            text="lent resolution.",
            page=1,
            y0=505.28,
            height=8.74,
            width=60.44,
        )
        current["source_spans"][0]["bbox"]["x0"] = 50.87
        current["source_spans"][0]["bbox"]["x1"] = 111.31

        self.assertTrue(_should_merge_paragraph_records(previous, current))

    def test_same_page_upward_jump_without_column_change_is_not_merged(self) -> None:
        previous = _record(
            record_type="paragraph",
            text="This paragraph ends without punctuation because the OCR stream is noisy",
            page=4,
            y0=268.56,
            height=284.46,
            width=229.15,
        )
        current = _record(
            record_type="paragraph",
            text="are connected by edges that should not merge when the parser jumps upward in the same column.",
            page=4,
            y0=68.16,
            height=33.9,
            width=226.94,
        )

        self.assertFalse(_should_merge_paragraph_records(previous, current))

    def test_short_ocr_fragment_drops_multispan_lowercase_label_cloud(self) -> None:
        record = _record(
            record_type="paragraph",
            text="image-space intersection surface intersection",
            page=39,
            y0=577.66,
            height=9.37,
            width=108.15,
        )
        record["source_spans"] = [
            {
                "page": 39,
                "bbox": {
                    "x0": 153.32,
                    "y0": 577.66,
                    "x1": 261.47,
                    "y1": 587.03,
                    "width": 108.15,
                    "height": 9.37,
                },
                "engine": "docling",
            },
            {
                "page": 39,
                "bbox": {
                    "x0": 153.32,
                    "y0": 621.68,
                    "x1": 238.33,
                    "y1": 631.04,
                    "width": 85.01,
                    "height": 9.36,
                },
                "engine": "docling",
            },
        ]

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_tiny_top_margin_view_label(self) -> None:
        record = _record(
            record_type="paragraph",
            text="camera view top view",
            page=66,
            y0=46.98,
            height=9.84,
            width=59.2,
        )
        record["source_spans"][0]["bbox"]["x0"] = 111.1
        record["source_spans"][0]["bbox"]["x1"] = 170.3

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_narrow_short_scan_scrap(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Initial measurement",
            page=5,
            y0=673.13,
            height=8.29,
            width=91.28,
        )
        record["source_spans"][0]["bbox"]["x0"] = 53.76
        record["source_spans"][0]["bbox"]["x1"] = 145.04

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_top_margin_caption_spill(self) -> None:
        record = _record(
            record_type="paragraph",
            text=": patch under orthographic projection can be parameterized in one of these five tion 2. Other cases not listed",
            page=5,
            y0=17.33,
            height=10.0,
            width=319.33,
        )
        record["source_spans"][0]["bbox"]["x0"] = 0.0
        record["source_spans"][0]["bbox"]["x1"] = 319.33

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_narrow_lowercase_hyphenated_scrap(self) -> None:
        record = _record(
            record_type="paragraph",
            text="urs. In order to need new algo-",
            page=5,
            y0=165.33,
            height=8.0,
            width=55.33,
        )
        record["source_spans"][0]["bbox"]["x0"] = 0.0
        record["source_spans"][0]["bbox"]["x1"] = 55.33

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_tiny_multiword_label_strip(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Cone on a surface Contour generator",
            page=7,
            y0=341.19,
            height=6.7,
            width=108.66,
        )
        record["source_spans"][0]["bbox"]["x0"] = 81.02
        record["source_spans"][0]["bbox"]["x1"] = 189.68

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_three_word_lowercase_label_strip(self) -> None:
        record = _record(
            record_type="paragraph",
            text="image-space intersection",
            page=39,
            y0=577.66,
            height=9.37,
            width=108.15,
        )
        record["source_spans"][0]["bbox"]["x0"] = 153.32
        record["source_spans"][0]["bbox"]["x1"] = 261.47

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_razor_thin_single_word_axis_label(self) -> None:
        record = _record(
            record_type="paragraph",
            text="Time",
            page=96,
            y0=168.18,
            height=22.65,
            width=9.37,
        )
        record["source_spans"][0]["bbox"]["x0"] = 146.11
        record["source_spans"][0]["bbox"]["x1"] = 155.48

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_drops_tiny_repeated_clause_debris(self) -> None:
        record = {
            "id": "tiny-repeated-clause-debris",
            "page": 12,
            "type": "paragraph",
            "text": "T are in e. pi are in y. A are in B.",
            "source_spans": [
                _record(record_type="paragraph", text="T", page=12, y0=324.07, height=8.7, width=5.82)["source_spans"][0],
                _record(record_type="paragraph", text="e", page=12, y0=327.6, height=6.1, width=3.78)["source_spans"][0],
                _record(record_type="paragraph", text="pi", page=12, y0=324.07, height=8.7, width=5.68)["source_spans"][0],
                _record(record_type="paragraph", text="y", page=12, y0=327.6, height=6.1, width=4.04)["source_spans"][0],
                _record(record_type="paragraph", text="A", page=12, y0=324.07, height=8.7, width=2.77)["source_spans"][0],
            ],
            "meta": {},
        }

        self.assertTrue(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_keeps_normal_width_short_sentence(self) -> None:
        record = _record(
            record_type="paragraph",
            text="This matters in practice.",
            page=5,
            y0=320.0,
            height=11.0,
            width=220.0,
        )

        self.assertFalse(_is_short_ocr_fragment(record))

    def test_short_ocr_fragment_keeps_standalone_where_bridge(self) -> None:
        record = _record(
            record_type="paragraph",
            text="where",
            page=2,
            y0=662.12,
            height=13.21,
            width=41.26,
        )

        self.assertFalse(_is_short_ocr_fragment(record))

    def test_strip_known_running_header_text_removes_procedia_stub(self) -> None:
        cleaned = _strip_known_running_header_text(
            "Within the MBD philosophy Author name Procedia CIRP 00 (2018) 000"
        )

        self.assertEqual(cleaned, "Within the MBD philosophy")

    def test_running_header_record_is_detected_before_block_build(self) -> None:
        record = _record(
            record_type="paragraph",
            text="STEWMAN AND BOWYER",
            page=9,
            y0=71.19,
            height=14.9,
            width=182.14,
        )
        record["source_spans"][0]["bbox"]["x0"] = 288.12
        record["source_spans"][0]["bbox"]["x1"] = 470.26

        self.assertTrue(_looks_like_running_header_record(record))

    def test_table_body_debris_record_is_detected_before_block_build(self) -> None:
        record = {
            "id": "table-cloud",
            "page": 9,
            "type": "paragraph",
            "text": "Points of intersection PI P2 P3 P4 P5 P6 P7 P8 P9 P10 Auxiliary Points Coordinates -1 -1 0 0.25 -0.25 0.25 -1 -1 -1 -1 1 1 0.5 0.5 0.5 1 1 -1 -1 -1 A1+ A1- A2+ A2- A3+ A3- A4+ A4- A5+ A5- A6+ A6- A7+ A7- A8+ A8- A9+ A9- A10+",
            "source_spans": [
                _record(record_type="paragraph", text=f"tok-{index}", page=9, y0=170.0 + index * 10.0, height=12.0, width=24.0)["source_spans"][0]
                for index in range(20)
            ],
            "meta": {},
        }

        self.assertTrue(_looks_like_table_body_debris(record))

    def test_embedded_table_heading_is_suppressed_after_table_caption(self) -> None:
        caption = _record(
            record_type="caption",
            text="TABLE 4 Evaluation Matrix for the Truncated Wedge",
            page=12,
            y0=110.56,
            height=24.0,
            width=300.0,
        )
        heading = _record(
            record_type="heading",
            text="Planes from top of parcellation graph",
            page=12,
            y0=160.59,
            height=15.03,
            width=253.34,
        )
        heading["source_spans"][0]["bbox"]["x0"] = 284.81
        heading["source_spans"][0]["bbox"]["x1"] = 538.15

        kept = _suppress_embedded_table_headings([caption, heading])

        self.assertEqual([record["type"] for record in kept], ["caption"])

    def test_append_figure_caption_fragment_trims_repeated_prefix(self) -> None:
        figure = {
            "id": "fig-5-3",
            "label": "Figure 5.3",
            "caption": "Segment atlas — Each input 3D line p i q i is projected and clipped by a fragment shader.",
        }

        _append_figure_caption_fragment(
            figure,
            "Figure 5.3: Segment atlas — Each input 3D line p i q i is projected and clipped by a fragment shader, which also computes visibility samples.",
        )

        self.assertEqual(
            figure["caption"],
            "Segment atlas — Each input 3D line p i q i is projected and clipped by a fragment shader. which also computes visibility samples.",
        )

    def test_append_figure_caption_fragment_strips_leading_punctuation(self) -> None:
        figure = {
            "id": "fig-8",
            "label": "Figure 8.",
            "caption": "",
        }

        _append_figure_caption_fragment(
            figure,
            ". (1) Type I; (2) type II; (3) type III; (4) type IV.",
        )

        self.assertEqual(
            figure["caption"],
            "(1) Type I; (2) type II; (3) type III; (4) type IV.",
        )

    def test_caption_fragment_is_absorbed_into_figure_caption_without_dropping_body_paragraph(self) -> None:
        layout_blocks = [
            LayoutBlock(
                id="caption-fragment",
                page=1,
                order=10,
                text="and d closeup illustrating the difference of the original inner circle of the torus",
                role="caption",
                bbox={"x0": 306.13, "y0": 358.19, "x1": 546.78, "y1": 386.94, "width": 240.65, "height": 28.75},
            ),
            LayoutBlock(
                id="caption-spill",
                page=1,
                order=11,
                text="some inaccuracies of a model defined by a torus intersected by a plane.",
                role="paragraph",
                bbox={"x0": 306.14, "y0": 420.17, "x1": 546.78, "y1": 504.93, "width": 240.64, "height": 84.76},
            ),
        ]
        figures = [
            {
                "id": "fig-1",
                "label": "Figure 1 Model of a half of a torus",
                "caption": "an initial non-trimmed torus and surface defined in the xy-plane, b resulting trimmed object, c closeup showing the deviation from the visualization mesh",
                "page": 1,
                "bbox": {"x0": 42.09, "y0": 49.85, "x1": 553.18, "y1": 348.45, "width": 511.09, "height": 298.6},
                "provenance": {
                    "caption_bbox": {"x0": 51.02, "y0": 354.96, "x1": 291.28, "y1": 398.06, "width": 240.26, "height": 43.1}
                },
            }
        ]

        records, _ = _merge_layout_and_figure_records(layout_blocks, figures)

        self.assertIn("and d closeup illustrating the difference of the original inner circle of the torus", figures[0]["caption"])
        self.assertNotIn("Model of a half of a torus:", figures[0]["caption"])
        paragraph_texts = [str(record.get("text", "")) for record in records if record.get("type") == "paragraph"]
        self.assertTrue(any("some inaccuracies of a model defined by a torus intersected by a plane." in text for text in paragraph_texts))

    def test_front_matter_strips_preprint_marker_from_abstract(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="PREPRINT", y0=700.0, height=12.0, width=80.0),
            _record(
                record_type="paragraph",
                text="Abstract This tutorial describes line drawings from 3D models.",
                y0=640.0,
                height=18.0,
                width=420.0,
            ),
        ]

        with self.assertRaisesRegex(RuntimeError, "Missing recoverable title"):
            _build_front_matter(
                "synthetic_preprint_paper",
                prelude,
                prelude,
                [],
                1,
            )

    def test_front_matter_extracts_multiple_authors_and_leaves_intro_body(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", y0=80.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="Roberto Cipolla", y0=130.0, height=12.0, width=140.0),
            _record(record_type="front_matter", text="Department of Engineering, University of Cambridge", y0=145.0, height=12.0, width=260.0),
            _record(record_type="front_matter", text="Andrew Blake", y0=160.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Department of Engineering Science, University of Oxford", y0=175.0, height=12.0, width=300.0),
            _record(record_type="front_matter", text="Abstract", y0=220.0, height=12.0, width=80.0),
            _record(
                record_type="front_matter",
                text="Surface patches can be reconstructed in the vicinity of contour generators under known viewer motion.",
                y0=245.0,
                height=24.0,
                width=420.0,
            ),
            _record(record_type="front_matter", text="1 Introduction", y0=320.0, height=12.0, width=100.0),
            _record(
                record_type="front_matter",
                text="This introduction paragraph should remain in the body.",
                y0=340.0,
                height=16.0,
                width=340.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            prelude,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Roberto Cipolla", "Andrew Blake"])
        self.assertEqual(len(front_matter["affiliations"]), 2)
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], "Surface patches can be reconstructed in the vicinity of contour generators under known viewer motion.")
        self.assertEqual(next_block_index, 2)
        self.assertEqual(len(remainder), 1)
        self.assertIn("This introduction paragraph should remain in the body.", remainder[0]["text"])

    def test_front_matter_recovers_authors_from_accepted_manuscript_citation(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="This is the accepted manuscript version of the following article:", page=1, y0=80.0, height=12.0, width=360.0),
            _record(
                record_type="front_matter",
                text="González-Lluch C., Company P., Contero M., Camba J.D., & Plumed, R. (2016). A Survey on 3D CAD Model Quality Assurance and Testing Tools. Computer-Aided Design.",
                page=1,
                y0=120.0,
                height=32.0,
                width=420.0,
            ),
            _record(record_type="front_matter", text="1. Introduction", page=2, y0=120.0, height=12.0, width=120.0),
            _record(
                record_type="front_matter",
                text="The introduction body remains outside front matter.",
                page=2,
                y0=150.0,
                height=16.0,
                width=340.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "2017_survey_on_3d_cad_model_quality_assurance_and_testing_tools",
            prelude,
            prelude,
            [],
            1,
        )

        self.assertEqual(
            [author["name"] for author in front_matter["authors"]],
            ["González-Lluch C.", "Company P.", "Contero M.", "Camba J.D.", "Plumed R."],
        )
        self.assertEqual(
            front_matter["affiliations"],
            [{"id": "aff-1", "department": "[missing from original]", "institution": "", "address": ""}],
        )

    def test_front_matter_recovers_long_comma_separated_author_line(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Robust Tessellation of CAD Models without Self-Intersections", page=1, y0=100.5, height=40.11, width=381.36),
            _record(
                record_type="front_matter",
                text="Gangyi Li, Zhongxuan Luo, Yuhao Feng, Lingfeng Zhang, Yuqiao Gai and Na Lei",
                page=1,
                y0=153.59,
                height=7.45,
                width=300.06,
            ),
            _record(
                record_type="front_matter",
                text="School of Software, Dalian University of Technology, Dalian, Liaoning 116024, China ∗ Correspondence: nalei@dlut.edu.cn",
                page=1,
                y0=171.45,
                height=15.58,
                width=260.9,
            ),
            _record(record_type="front_matter", text="Abstract", page=1, y0=220.0, height=12.0, width=80.0),
            _record(record_type="front_matter", text="We present a robust tessellation pipeline.", page=1, y0=245.0, height=24.0, width=320.0),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "2026_robust_tessellation_without_self_intersections",
            prelude,
            prelude,
            [],
            1,
        )

        self.assertEqual(
            [author["name"] for author in front_matter["authors"]],
            ["Gangyi Li", "Zhongxuan Luo", "Yuhao Feng", "Lingfeng Zhang", "Yuqiao Gai", "Na Lei"],
        )
        self.assertEqual(len(front_matter["affiliations"]), 1)
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_front_matter_recovers_abstract_when_title_arrives_after_intro_in_page_order(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="ELSEVIER", y0=60.0, height=12.0, width=90.0),
            _record(record_type="front_matter", text="Abstract", y0=90.0, height=12.0, width=80.0),
            _record(
                record_type="front_matter",
                text="This paper proposes a new entity-based aspect graph for polyhedral solids.",
                y0=110.0,
                height=28.0,
                width=420.0,
            ),
        ]
        page_one_records = [
            *prelude,
            _record(record_type="front_matter", text="1. Introduction", y0=160.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Synthetic Test Paper", y0=210.0, height=16.0, width=300.0),
            _record(
                record_type="front_matter",
                text="Christopher C. Yang, Michael M. Marefat, Erik J. Johnson",
                y0=240.0,
                height=16.0,
                width=360.0,
            ),
            _record(
                record_type="front_matter",
                text="Department of Electrical and Computer Engineering, The University of Arizona, Tucson, AZ 85721, USA",
                y0=265.0,
                height=16.0,
                width=420.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Christopher C. Yang", "Michael M. Marefat", "Erik J. Johnson"])
        self.assertEqual(len(front_matter["affiliations"]), 1)
        self.assertEqual(
            blocks[0]["content"]["spans"][0]["text"],
            "This paper proposes a new entity-based aspect graph for polyhedral solids.",
        )
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_split_leading_front_matter_keeps_page_one_metadata_tail_after_intro_marker(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Abstract", page=1, y0=80.0, height=12.0, width=80.0),
            _record(record_type="front_matter", text="A short abstract.", page=1, y0=95.0, height=24.0, width=260.0),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=120.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="ScienceDirect", page=1, y0=140.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=160.0, height=16.0, width=300.0),
            _record(record_type="front_matter", text="Alice Example, Bob Example", page=1, y0=180.0, height=16.0, width=260.0),
            _record(record_type="front_matter", text="First body paragraph.", page=2, y0=100.0, height=16.0, width=320.0),
        ]

        front_records, remainder = _split_leading_front_matter_records(prelude)

        self.assertIn("ScienceDirect", [record["text"] for record in front_records])
        self.assertIn("Synthetic Test Paper", [record["text"] for record in front_records])
        self.assertEqual([record["text"] for record in remainder], ["First body paragraph."])

    def test_front_matter_prefers_page_one_records_after_title_for_author_recovery(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="ELSEVIER", page=1, y0=60.0, height=12.0, width=90.0),
            _record(record_type="front_matter", text="Abstract", page=1, y0=90.0, height=12.0, width=80.0),
            _record(record_type="front_matter", text="A short abstract.", page=1, y0=105.0, height=24.0, width=260.0),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=130.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Cneck Tol", page=1, y0=150.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="ScienceDirect", page=1, y0=165.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Comput. Methods Appl. Mech. Engrg. 351 (2019) 808-835", page=1, y0=180.0, height=12.0, width=320.0),
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=210.0, height=16.0, width=300.0),
        ]
        page_one_records = [
            *prelude,
            _record(record_type="paragraph", text="Synthetic Test Paper", page=1, y0=210.0, height=16.0, width=300.0),
            _record(record_type="paragraph", text="Alice Example, Bob Example", page=1, y0=235.0, height=16.0, width=260.0),
            _record(record_type="paragraph", text="Department of Engineering, Test University", page=1, y0=255.0, height=14.0, width=280.0),
            _record(record_type="paragraph", text="Abstract", page=1, y0=280.0, height=12.0, width=80.0),
            _record(record_type="paragraph", text="A short abstract.", page=1, y0=295.0, height=24.0, width=260.0),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Alice Example", "Bob Example"])
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_front_matter_page_one_scan_stops_before_abstract_and_drops_permission_tail(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="ELSEVIER", page=1, y0=60.0, height=12.0, width=90.0),
            _record(record_type="front_matter", text="Abstract", page=1, y0=90.0, height=12.0, width=80.0),
            _record(record_type="front_matter", text="A short abstract.", page=1, y0=105.0, height=24.0, width=260.0),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=130.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Body paragraph.", page=2, y0=100.0, height=24.0, width=320.0),
        ]
        page_one_records = [
            _record(
                record_type="front_matter",
                text="A MECHANISM FOR PERSISTENTLY NAMING TOPOLOGICAL ENTITIES",
                page=1,
                y0=180.0,
                height=18.0,
                width=360.0,
            ),
            _record(
                record_type="front_matter",
                text="IN HISTORY-BASED PARAMETRIC SOLID MODELS",
                page=1,
                y0=200.0,
                height=18.0,
                width=360.0,
            ),
            _record(record_type="front_matter", text="(TopologicalID System)", page=1, y0=225.0, height=12.0, width=180.0),
            _record(record_type="front_matter", text="Jiri Kripac", page=1, y0=240.0, height=12.0, width=140.0),
            _record(
                record_type="front_matter",
                text="Autodesk Inc. 111 McInnis Parkway, San Rafael, CA 94903",
                page=1,
                y0=255.0,
                height=12.0,
                width=320.0,
            ),
            _record(record_type="front_matter", text="Email: jkripac@autodesk.com", page=1, y0=270.0, height=12.0, width=220.0),
            _record(record_type="front_matter", text="ABSTRACT", page=1, y0=300.0, height=12.0, width=90.0),
            _record(
                record_type="front_matter",
                text="Permission to copy without fee all or part of this material is granted.",
                page=1,
                y0=320.0,
                height=24.0,
                width=340.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "1997_a_mechanism_for_persistently_naming_topological_entities_in_history_based_parametric_solid_models",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Jiri Kripac"])
        self.assertEqual(len(front_matter["affiliations"]), 1)
        self.assertIn("Autodesk Inc.", front_matter["affiliations"][0]["department"])
        self.assertNotIn("Permission to copy", front_matter["affiliations"][0]["department"])
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(next_block_index, 2)
        self.assertEqual([record["text"] for record in remainder], ["Body paragraph."])

    def test_front_matter_normalizes_byline_and_location_affiliation_continuations(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="The Notion of Quantitative Invisibility", page=1, y0=60.0, height=18.0, width=320.0),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=140.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="Body paragraph.", page=1, y0=160.0, height=24.0, width=320.0),
        ]
        page_one_records = [
            _record(record_type="front_matter", text="The Notion of Quantitative Invisibility", page=1, y0=60.0, height=18.0, width=320.0),
            _record(record_type="front_matter", text="by ARTHUR APPEL", page=1, y0=90.0, height=12.0, width=140.0),
            _record(
                record_type="front_matter",
                text="by ARTHUR APPEL International Business Machines Corporation",
                page=1,
                y0=105.0,
                height=12.0,
                width=340.0,
            ),
            _record(record_type="front_matter", text="Yorktown Heights,", page=1, y0=120.0, height=12.0, width=140.0),
            _record(record_type="front_matter", text="New York", page=1, y0=132.0, height=12.0, width=100.0),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=140.0, height=12.0, width=120.0),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "1967_quantitative_invisibility",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["ARTHUR APPEL"])
        self.assertEqual(len(front_matter["affiliations"]), 1)
        self.assertEqual(front_matter["affiliations"][0]["department"], "International Business Machines Corporation")
        self.assertEqual(front_matter["affiliations"][0]["institution"], "Yorktown Heights")
        self.assertEqual(front_matter["affiliations"][0]["address"], "New York")
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(blocks[0]["review"]["status"], "edited")
        self.assertEqual(remainder, [])

    def test_front_matter_creates_placeholders_for_missing_author_affiliation_and_abstract(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", y0=80.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="1. Introduction", y0=140.0, height=12.0, width=120.0),
            _record(record_type="paragraph", text="Body paragraph.", y0=160.0, height=24.0, width=320.0),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            prelude,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["[missing from original]"])
        self.assertEqual(front_matter["authors"][0]["affiliation_ids"], ["aff-1"])
        self.assertEqual(
            front_matter["affiliations"],
            [{"id": "aff-1", "department": "[missing from original]", "institution": "", "address": ""}],
        )
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(blocks[0]["review"]["notes"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_front_matter_does_not_infer_abstract_from_metadata_filtered_body_text(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", y0=80.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="Shankar Krishnan", y0=140.0, height=12.0, width=140.0),
            _record(record_type="front_matter", text="AT&T Research Labs, Florham Park, New Jersey", y0=155.0, height=12.0, width=260.0),
            _record(record_type="front_matter", text="Received February 22, 1999; revised March 31, 2000", y0=180.0, height=12.0, width=300.0),
            _record(record_type="front_matter", text="dol: 10.1006 gmod.2000.0526, available online at http: example.com", y0=195.0, height=12.0, width=320.0),
            _record(
                record_type="front_matter",
                text="Computing the visible portions of curved surfaces from a given viewpoint is of great interest in many applications.",
                y0=225.0,
                height=28.0,
                width=420.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            prelude,
            [],
            1,
        )

        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(blocks[0]["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_front_matter_does_not_infer_abstract_from_page_two_body_without_anchor(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=80.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="Alice Example", page=1, y0=115.0, height=12.0, width=160.0),
            _record(record_type="front_matter", text="Example Institute", page=1, y0=130.0, height=12.0, width=180.0),
            _record(record_type="heading", text="1. Introduction", page=2, y0=90.0, height=12.0, width=120.0),
            _record(
                record_type="paragraph",
                text="This introductory paragraph should remain body text instead of becoming a synthetic abstract.",
                page=2,
                y0=115.0,
                height=24.0,
                width=420.0,
            ),
        ]
        page_one_records = prelude[:3]

        front_matter, blocks, _, remaining = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            page_one_records,
            [],
            1,
        )

        abstract_block = next(block for block in blocks if block["id"] == front_matter["abstract_block_id"])
        self.assertEqual(abstract_block["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(len(remaining), 1)
        self.assertIn("introductory paragraph", remaining[0]["text"])

    def test_front_matter_discards_accepted_manuscript_boilerplate_without_anchor(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", page=1, y0=70.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="This is the accepted manuscript version of the following article:", page=1, y0=95.0, height=12.0, width=420.0),
            _record(
                record_type="front_matter",
                text="This manuscript version is made available under the CC-BY-NC-ND 4.0 license.",
                page=1,
                y0=110.0,
                height=12.0,
                width=420.0,
            ),
            _record(record_type="front_matter", text="1. Introduction", page=1, y0=150.0, height=12.0, width=120.0),
            _record(record_type="paragraph", text="Body paragraph.", page=2, y0=100.0, height=20.0, width=320.0),
        ]

        front_matter, blocks, _, remaining = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            prelude,
            [],
            1,
        )

        abstract_block = next(block for block in blocks if block["id"] == front_matter["abstract_block_id"])
        self.assertEqual(abstract_block["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(len(remaining), 1)

    def test_front_matter_participants_page_uses_missing_abstract_placeholder(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Workshop Panel Report", page=1, y0=60.0, height=14.0, width=180.0),
            _record(record_type="front_matter", text="Synthetic Panel Paper", page=1, y0=80.0, height=16.0, width=260.0),
            _record(record_type="front_matter", text="Participants", page=1, y0=110.0, height=12.0, width=90.0),
            _record(record_type="front_matter", text="ALICE EXAMPLE Example University", page=1, y0=130.0, height=12.0, width=220.0),
            _record(record_type="front_matter", text="Organizer:", page=1, y0=150.0, height=12.0, width=80.0),
            _record(record_type="front_matter", text="BOB EXAMPLE", page=1, y0=165.0, height=12.0, width=120.0),
            _record(record_type="front_matter", text="1. INTRODUCTION", page=1, y0=220.0, height=12.0, width=120.0),
            _record(record_type="paragraph", text="Body paragraph.", page=2, y0=100.0, height=20.0, width=320.0),
        ]

        front_matter, blocks, _, remaining = _build_front_matter(
            "1992_why_aspect_graphs_are_not_yet_practical_for_computer_vision",
            prelude,
            prelude,
            [],
            1,
        )

        abstract_block = next(block for block in blocks if block["id"] == front_matter["abstract_block_id"])
        self.assertEqual(abstract_block["content"]["spans"][0]["text"], NO_ABSTRACT_IN_BASE_MATERIAL)
        self.assertEqual(abstract_block["review"]["status"], "edited")
        self.assertEqual(len(remaining), 1)

    def test_front_matter_recovers_page_one_authors_and_affiliations(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Synthetic Test Paper", y0=80.0, height=16.0, width=320.0),
            _record(record_type="front_matter", text="Shankar Krishnan", y0=140.0, height=12.0, width=140.0),
            _record(record_type="front_matter", text="and", y0=160.0, height=12.0, width=40.0),
            _record(
                record_type="front_matter",
                text="Computing the visible portions of curved surfaces from a given viewpoint is of great interest in many applications.",
                y0=225.0,
                height=28.0,
                width=420.0,
            ),
        ]
        page_one_records = [
            *prelude,
            _record(
                record_type="front_matter",
                text="AT&T Research Labs, 180 Park Avenue, Room E-201, Florham Park, New Jersey 07932 E-mail: krishnas@research.att.com",
                y0=603.59,
                height=22.0,
                width=360.0,
            ),
            _record(record_type="front_matter", text="Dinesh Manocha", y0=789.8, height=14.0, width=180.0),
            _record(
                record_type="front_matter",
                text="Department of Computer Science, University of North Carolina, Chapel Hill, North Carolina 27599-3175 E-mail: dm@cs.unc.edu",
                y0=844.51,
                height=22.0,
                width=420.0,
            ),
        ]

        front_matter, blocks, next_block_index, remainder = _build_front_matter(
            "synthetic_test_paper",
            prelude,
            page_one_records,
            [],
            1,
        )

        self.assertEqual([author["name"] for author in front_matter["authors"]], ["Shankar Krishnan", "Dinesh Manocha"])
        self.assertEqual(len(front_matter["affiliations"]), 2)
        self.assertEqual(front_matter["affiliations"][0]["department"], "AT&T Research Labs")
        self.assertEqual(front_matter["affiliations"][1]["institution"], "University of North Carolina")
        self.assertEqual(front_matter["abstract_block_id"], "blk-front-abstract-1")
        self.assertEqual(next_block_index, 2)
        self.assertEqual(remainder, [])

    def test_late_prelude_pages_become_intro_when_first_root_skips_it(self) -> None:
        prelude = [
            _record(record_type="front_matter", text="Abstract", page=1, y0=120.0, height=12.0, width=80.0),
            _record(
                record_type="front_matter",
                text="A short abstract lives on the first page.",
                page=1,
                y0=145.0,
                height=18.0,
                width=320.0,
            ),
            _record(
                record_type="front_matter",
                text="This later-page paragraph should be promoted back into the introduction body.",
                page=2,
                y0=90.0,
                height=18.0,
                width=360.0,
            ),
        ]
        roots = [SectionNode(title="2 Preliminary", level=1, heading_id="sec-2", label=("2",))]

        trimmed, overflow = _split_late_prelude_for_missing_intro(prelude, roots)

        self.assertEqual([record["page"] for record in trimmed], [1, 1])
        self.assertEqual([record["page"] for record in overflow], [2])
        self.assertIn("promoted back into the introduction body", overflow[0]["text"])


if __name__ == "__main__":
    unittest.main()
