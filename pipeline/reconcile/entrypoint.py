from __future__ import annotations

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
from pipeline.assembly.record_block_builder import split_code_lines as assemble_split_code_lines
from pipeline.assembly.section_builder import materialize_sections
from pipeline.assembly.section_support import (
    normalize_section_title as assemble_normalize_section_title,
    section_id as assemble_section_id,
)
from pipeline.config import PipelineConfig, build_pipeline_config
from pipeline.figures.labels import caption_label
from pipeline.math.compile import compile_formulas
from pipeline.math.extract import (
    INLINE_MATH_RE,
    build_block_math_entry,
    classify_math_block,
    extract_general_inline_math_spans,
    looks_like_prose_math_fragment,
    looks_like_prose_paragraph,
    merge_inline_math_relation_suffixes,
    normalize_inline_math_spans,
    repair_symbolic_ocr_spans,
    split_inline_math,
)
from pipeline.math.review_policy import (
    review_for_algorithm_block_text,
    review_for_math_entry,
    review_for_math_ref_block,
)
from pipeline.math.semantic_ir import annotate_formula_semantic_expr
from pipeline.math.semantic_policy import annotate_formula_classifications
from pipeline.orchestrator.layout_merge import merge_native_and_external_layout as orchestrate_merge_native_and_external_layout
from pipeline.orchestrator.paper_reconciler import run_paper_pipeline
from pipeline.policies.abstract_quality import (
    MISSING_ABSTRACT_PLACEHOLDER,
    NO_ABSTRACT_IN_BASE_MATERIAL,
    abstract_quality_flags,
)
from pipeline.reconcile.external_math import match_external_math_entry as reconcile_match_external_math_entry
from pipeline.reconcile.front_matter_parsing import looks_like_affiliation as reconcile_looks_like_affiliation_runtime
from pipeline.reconcile.front_matter_patterns import (
    ABBREVIATED_VENUE_LINE_RE,
    ABSTRACT_BODY_BREAK_RE,
    ABSTRACT_CONTINUATION_RE,
    ABSTRACT_LEAD_RE,
    ABSTRACT_MARKER_ONLY_RE,
    AUTHOR_AFFILIATION_INDEX_RE,
    AUTHOR_MARKER_RE,
    AUTHOR_NOTE_RE,
    AUTHOR_TOKEN_RE,
    CITATION_AUTHOR_SPLIT_RE,
    CITATION_YEAR_RE,
    FIGURE_REF_RE,
    FRONT_MATTER_METADATA_RE,
    FUNDING_RE,
    INTRO_MARKER_RE,
    KEYWORDS_LEAD_RE,
    NAME_TOKEN_RE,
    PREPRINT_MARKER_RE,
    REFERENCE_VENUE_RE,
    TITLE_PAGE_METADATA_RE,
    TRAILING_ABSTRACT_BOILERPLATE_RE,
    TRAILING_ABSTRACT_TAIL_RE,
)
from pipeline.reconcile.layout_records import (
    rect_x_overlap_ratio as reconcile_rect_x_overlap_ratio,
)
from pipeline.reconcile.math_suppression import (
    external_math_by_page as reconcile_external_math_by_page,
    looks_like_display_math_echo as reconcile_looks_like_display_math_echo,
    overlapping_external_math_entries as reconcile_overlapping_external_math_entries,
    trim_embedded_display_math_from_paragraph as reconcile_trim_embedded_display_math_from_paragraph,
)
from pipeline.reconcile.runtime_constants import (
    ABOUT_AUTHOR_RE,
    CONTROL_CHAR_RE,
    DIAGRAM_ACTION_RE,
    DIAGRAM_DECISION_RE,
    DIAGRAM_QUERY_RE,
    LABEL_CLOUD_TOKEN_RE,
    LEADING_NEGATIONSLASH_ARTIFACT_RE,
    LEADING_OCR_MARKER_RE,
    LEADING_PUNCT_ARTIFACT_RE,
    LEADING_VAR_ARTIFACT_RE,
    MATHPIX_HINT_TOKEN_RE,
    MATH_TOKEN_RE,
    QUOTED_IDENTIFIER_FRAGMENT_RE,
    REFERENCE_AUTHOR_RE,
    REFERENCE_START_RE,
    REFERENCE_YEAR_RE,
    SHORT_OCR_NOISE_RE,
    TERMINAL_PUNCTUATION_RE,
    TRAILING_NUMERIC_ARTIFACT_RE,
    TRUNCATED_PROSE_LEAD_STOPWORDS,
)
from pipeline.reconcile.runtime_deps import (
    build_reconcile_root_helper_bundles as reconcile_build_reconcile_root_helper_bundles_runtime,
    build_reconcile_runtime_deps as reconcile_build_reconcile_runtime_deps_runtime,
)
from pipeline.reconcile.section_filters import starts_like_sentence as reconcile_starts_like_sentence
from pipeline.reconcile.section_preparation import attach_orphan_numbered_roots, prepare_section_nodes
from pipeline.reconcile.shared_patterns import (
    DISPLAY_MATH_PROSE_CUE_RE,
    DISPLAY_MATH_RESUME_RE,
    DISPLAY_MATH_START_RE,
    EMBEDDED_HEADING_PREFIX_RE,
    PROCEDIA_RUNNING_HEADER_RE,
    RUNNING_HEADER_TEXT_RE,
    SHORT_WORD_RE,
    TABLE_CAPTION_RE,
)
from pipeline.reconcile.stage_runtime import ReconcileRuntimeInputs, run_reconcile_pipeline as reconcile_run_reconcile_pipeline_runtime
from pipeline.reconcile.runtime_support import page_height_map as reconcile_page_height_map_binding_runtime
from pipeline.selectors.abstract_selector import build_abstract_decision
from pipeline.sources.external import load_external_layout, load_external_math, load_mathpix_layout
from pipeline.sources.figures import extract_figures
from pipeline.sources.layout import extract_layout
from pipeline.sources.pdftotext import (
    bbox_to_line_window,
    extract_pdftotext_pages,
    pdftotext_available,
    slice_page_text,
)
from pipeline.state import PaperState
from pipeline.text.headings import (
    SectionNode,
    build_section_tree,
    clean_heading_title,
    collapse_ocr_split_caps,
    compact_text,
    looks_like_bad_heading,
    normalize_title_key,
    parse_heading_label,
)
from pipeline.text.prose import decode_ocr_codepoint_tokens, normalize_prose_text
from pipeline.text.references import normalize_reference_text
from pipeline.types import default_review

_helper_bundles = reconcile_build_reconcile_root_helper_bundles_runtime(
    control_char_re=CONTROL_CHAR_RE,
    compact_text=compact_text,
    procedia_running_header_re=PROCEDIA_RUNNING_HEADER_RE,
    short_word_re=SHORT_WORD_RE,
    decode_ocr_codepoint_tokens=decode_ocr_codepoint_tokens,
    looks_like_prose_paragraph=looks_like_prose_paragraph,
    math_token_re=MATH_TOKEN_RE,
    quoted_identifier_fragment_re=QUOTED_IDENTIFIER_FRAGMENT_RE,
    label_cloud_token_re=LABEL_CLOUD_TOKEN_RE,
    short_ocr_noise_re=SHORT_OCR_NOISE_RE,
    terminal_punctuation_re=TERMINAL_PUNCTUATION_RE,
    diagram_decision_re=DIAGRAM_DECISION_RE,
    diagram_query_re=DIAGRAM_QUERY_RE,
    diagram_action_re=DIAGRAM_ACTION_RE,
    running_header_text_re=RUNNING_HEADER_TEXT_RE,
    table_caption_re=TABLE_CAPTION_RE,
    parse_heading_label=parse_heading_label,
    clean_heading_title=clean_heading_title,
    inline_math_re=INLINE_MATH_RE,
    bbox_to_line_window=bbox_to_line_window,
    slice_page_text=slice_page_text,
    rect_x_overlap_ratio=reconcile_rect_x_overlap_ratio,
    display_math_prose_cue_re=DISPLAY_MATH_PROSE_CUE_RE,
    display_math_start_re=DISPLAY_MATH_START_RE,
    hint_token_re=MATHPIX_HINT_TOKEN_RE,
    truncated_prose_lead_stopwords=TRUNCATED_PROSE_LEAD_STOPWORDS,
    normalize_title_key=normalize_title_key,
    abstract_quality_flags=abstract_quality_flags,
    looks_like_affiliation=reconcile_looks_like_affiliation_runtime,
    author_marker_re=AUTHOR_MARKER_RE,
    author_affiliation_index_re=AUTHOR_AFFILIATION_INDEX_RE,
    name_token_re=NAME_TOKEN_RE,
    abbreviated_venue_line_re=ABBREVIATED_VENUE_LINE_RE,
    title_page_metadata_re=TITLE_PAGE_METADATA_RE,
    front_matter_metadata_re=FRONT_MATTER_METADATA_RE,
    reference_venue_re=REFERENCE_VENUE_RE,
    author_token_re=AUTHOR_TOKEN_RE,
    intro_marker_re=INTRO_MARKER_RE,
    abstract_marker_only_re=ABSTRACT_MARKER_ONLY_RE,
    abstract_lead_re=ABSTRACT_LEAD_RE,
    trailing_abstract_boilerplate_re=TRAILING_ABSTRACT_BOILERPLATE_RE,
    trailing_abstract_tail_re=TRAILING_ABSTRACT_TAIL_RE,
    preprint_marker_re=PREPRINT_MARKER_RE,
    author_note_re=AUTHOR_NOTE_RE,
    citation_year_re=CITATION_YEAR_RE,
    citation_author_split_re=CITATION_AUTHOR_SPLIT_RE,
    keywords_lead_re=KEYWORDS_LEAD_RE,
    abstract_body_break_re=ABSTRACT_BODY_BREAK_RE,
    figure_ref_re=FIGURE_REF_RE,
    abstract_continuation_re=ABSTRACT_CONTINUATION_RE,
    reference_start_re=REFERENCE_START_RE,
    about_author_re=ABOUT_AUTHOR_RE,
    reference_year_re=REFERENCE_YEAR_RE,
    reference_author_re=REFERENCE_AUTHOR_RE,
)


def reconcile_paper_state(
    paper_id: str,
    *,
    run_paper_pipeline_impl: Any | None = None,
    text_engine: str = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    layout_output: dict[str, Any] | None = None,
    figures: list[dict[str, Any]] | None = None,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> PaperState:
    run_paper_pipeline_impl = run_paper_pipeline_impl or run_paper_pipeline
    runtime_config = config or build_pipeline_config(
        text_engine=text_engine,
        use_external_layout=use_external_layout,
        use_external_math=use_external_math,
        include_review=False,
    )
    return reconcile_run_reconcile_pipeline_runtime(
        inputs=ReconcileRuntimeInputs(
            paper_id=paper_id,
            text_engine=text_engine,
            use_external_layout=use_external_layout,
            use_external_math=use_external_math,
            layout_output=layout_output,
            figures=figures,
            runtime_layout=runtime_config.layout,
            config=runtime_config,
            state=state,
        ),
        deps=reconcile_build_reconcile_runtime_deps_runtime(
            helper_bundles=_helper_bundles,
            run_paper_pipeline_impl=run_paper_pipeline_impl,
            extract_layout=extract_layout,
            load_external_layout=load_external_layout,
            merge_native_and_external_layout=orchestrate_merge_native_and_external_layout,
            load_external_math=load_external_math,
            external_math_by_page=reconcile_external_math_by_page,
            load_mathpix_layout=load_mathpix_layout,
            extract_figures=extract_figures,
            pdftotext_available=pdftotext_available,
            extract_pdftotext_pages=extract_pdftotext_pages,
            page_height_map=reconcile_page_height_map_binding_runtime,
            normalize_prose_text_impl=normalize_prose_text,
            normalize_reference_text_impl=normalize_reference_text,
            default_review=default_review,
            leading_negationslash_artifact_re=LEADING_NEGATIONSLASH_ARTIFACT_RE,
            leading_ocr_marker_re=LEADING_OCR_MARKER_RE,
            leading_punct_artifact_re=LEADING_PUNCT_ARTIFACT_RE,
            leading_var_artifact_re=LEADING_VAR_ARTIFACT_RE,
            trailing_numeric_artifact_re=TRAILING_NUMERIC_ARTIFACT_RE,
            looks_like_prose_paragraph=looks_like_prose_paragraph,
            looks_like_prose_math_fragment=looks_like_prose_math_fragment,
            split_inline_math=split_inline_math,
            repair_symbolic_ocr_spans=repair_symbolic_ocr_spans,
            extract_general_inline_math_spans=extract_general_inline_math_spans,
            merge_inline_math_relation_suffixes=merge_inline_math_relation_suffixes,
            normalize_inline_math_spans=normalize_inline_math_spans,
            build_front_matter_impl=assemble_front_matter,
            abstract_marker_only_re=ABSTRACT_MARKER_ONLY_RE,
            abstract_lead_re=ABSTRACT_LEAD_RE,
            author_note_re=AUTHOR_NOTE_RE,
            looks_like_affiliation=reconcile_looks_like_affiliation_runtime,
            funding_re=FUNDING_RE,
            missing_front_matter_placeholder=NO_ABSTRACT_IN_BASE_MATERIAL,
            missing_front_matter_author_impl=assemble_missing_front_matter_author,
            missing_front_matter_affiliation_impl=assemble_missing_front_matter_affiliation,
            normalize_title_key=normalize_title_key,
            preprint_marker_re=PREPRINT_MARKER_RE,
            keywords_lead_re=KEYWORDS_LEAD_RE,
            normalize_section_title_impl=assemble_normalize_section_title,
            clean_heading_title=clean_heading_title,
            parse_heading_label=parse_heading_label,
            front_block_text_impl=assemble_front_block_text,
            recover_missing_front_matter_abstract_impl=assemble_recover_missing_front_matter_abstract,
            abstract_quality_flags=abstract_quality_flags,
            caption_label=caption_label,
            split_code_lines=assemble_split_code_lines,
            review_for_math_entry=review_for_math_entry,
            review_for_math_ref_block=review_for_math_ref_block,
            match_external_math_entry_impl=reconcile_match_external_math_entry,
            build_block_math_entry=build_block_math_entry,
            classify_math_block=classify_math_block,
            review_for_algorithm_block_text=review_for_algorithm_block_text,
            overlapping_external_math_entries_impl=reconcile_overlapping_external_math_entries,
            trim_embedded_display_math_from_paragraph_impl=reconcile_trim_embedded_display_math_from_paragraph,
            display_math_prose_cue_re=DISPLAY_MATH_PROSE_CUE_RE,
            display_math_resume_re=DISPLAY_MATH_RESUME_RE,
            display_math_start_re=DISPLAY_MATH_START_RE,
            looks_like_display_math_echo_impl=reconcile_looks_like_display_math_echo,
            short_word_re=SHORT_WORD_RE,
            looks_like_bad_heading=looks_like_bad_heading,
            collapse_ocr_split_caps=collapse_ocr_split_caps,
            embedded_heading_prefix_re=EMBEDDED_HEADING_PREFIX_RE,
            build_section_tree=build_section_tree,
            attach_orphan_numbered_roots=attach_orphan_numbered_roots,
            build_abstract_decision=build_abstract_decision,
            section_node_type=SectionNode,
            prepare_section_nodes=prepare_section_nodes,
            materialize_sections=materialize_sections,
            section_id_impl=assemble_section_id,
            compile_formulas=compile_formulas,
            annotate_formula_classifications=annotate_formula_classifications,
            annotate_formula_semantic_expr=annotate_formula_semantic_expr,
            table_caption_re=TABLE_CAPTION_RE,
            compact_text=compact_text,
            running_header_text_re=RUNNING_HEADER_TEXT_RE,
            starts_like_sentence=reconcile_starts_like_sentence,
            build_canonical_document=build_canonical_document,
        ),
    )


def reconcile_paper(
    paper_id: str,
    *,
    run_paper_pipeline_impl: Any | None = None,
    text_engine: str = "native",
    use_external_layout: bool = False,
    use_external_math: bool = False,
    layout_output: dict[str, Any] | None = None,
    figures: list[dict[str, Any]] | None = None,
    config: PipelineConfig | None = None,
    state: PaperState | None = None,
) -> dict[str, Any]:
    run_paper_pipeline_impl = run_paper_pipeline_impl or run_paper_pipeline
    paper_state = reconcile_paper_state(
        paper_id,
        run_paper_pipeline_impl=run_paper_pipeline_impl,
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


__all__ = ["reconcile_paper", "reconcile_paper_state"]
