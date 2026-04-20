from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pipeline.reconcile.runtime_builders import build_reconcile_paper_pipeline_deps


@dataclass(frozen=True)
class ReconcileRuntimeInputs:
    paper_id: str
    text_engine: str
    use_external_layout: bool
    use_external_math: bool
    layout_output: dict[str, Any] | None
    figures: list[dict[str, Any]] | None
    runtime_layout: Any
    config: Any
    state: Any


@dataclass(frozen=True)
class ReconcileLoaderDeps:
    run_paper_pipeline_impl: Callable[..., Any]
    extract_layout: Callable[..., Any]
    load_external_layout: Callable[..., Any]
    merge_native_and_external_layout: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
    load_external_math: Callable[..., Any]
    external_math_by_page: Callable[[list[dict[str, Any]]], dict[int, list[dict[str, Any]]]]
    load_mathpix_layout: Callable[..., Any]
    extract_figures: Callable[..., Any]
    pdftotext_available: Callable[[], bool]
    repair_record_text_with_pdftotext: Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]]
    extract_pdftotext_pages: Callable[..., Any]
    page_height_map: Callable[[dict[str, Any]], dict[int, float]]


@dataclass(frozen=True)
class ReconcileBindingDeps:
    strip_known_running_header_text: Callable[[str], str]
    clean_text: Callable[[str], str]
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]]
    default_review: Callable[..., dict[str, Any]]
    leading_negationslash_artifact_re: Any
    leading_ocr_marker_re: Any
    leading_punct_artifact_re: Any
    leading_var_artifact_re: Any
    trailing_numeric_artifact_re: Any
    group_entry_items_are_graphic_only: Callable[[dict[str, Any]], bool]
    math_entry_semantic_policy: Callable[[dict[str, Any]], str]
    math_entry_category: Callable[[dict[str, Any]], str]
    looks_like_prose_paragraph: Callable[[str], bool]
    looks_like_prose_math_fragment: Callable[[str], bool]
    word_count: Callable[[str], int]
    strong_operator_count: Callable[[str], int]
    mathish_ratio: Callable[[str], float]
    split_inline_math: Callable[..., Any]
    repair_symbolic_ocr_spans: Callable[..., Any]
    extract_general_inline_math_spans: Callable[..., Any]
    merge_inline_math_relation_suffixes: Callable[..., Any]
    normalize_inline_math_spans: Callable[..., Any]
    split_leading_front_matter_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    clean_record: Callable[[dict[str, Any]], dict[str, Any]]
    record_word_count: Callable[[dict[str, Any]], int]
    record_width: Callable[[dict[str, Any]], float]
    abstract_marker_only_re: Any
    abstract_lead_re: Any
    looks_like_front_matter_metadata: Callable[[str], bool]
    author_note_re: Any
    looks_like_affiliation: Callable[[str], bool]
    looks_like_intro_marker: Callable[[str], bool]
    looks_like_author_line: Callable[[str], bool]
    looks_like_contact_name: Callable[[str], bool]
    matches_title_line: Callable[[str, str], bool]
    looks_like_affiliation_continuation: Callable[[str], bool]
    funding_re: Any
    dedupe_text_lines: Callable[[list[str]], list[str]]
    filter_front_matter_authors: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    parse_authors: Callable[[str], list[dict[str, Any]]]
    parse_authors_from_citation_line: Callable[[str, str], list[dict[str, Any]]]
    normalize_author_line: Callable[[str], str]
    missing_front_matter_author: Callable[[], dict[str, Any]]
    build_affiliations_for_authors: Callable[[int, list[str]], tuple[list[dict[str, Any]], list[list[str]]]]
    missing_front_matter_affiliation: Callable[[], dict[str, Any]]
    strip_author_prefix_from_affiliation_line: Callable[[str, list[dict[str, Any]]], str]
    normalize_title_key: Callable[[str], str]
    clone_record_with_text: Callable[[dict[str, Any], str], dict[str, Any]]
    looks_like_body_section_marker: Callable[[str], bool]
    preprint_marker_re: Any
    keywords_lead_re: Any
    abstract_text_is_usable: Callable[[str], bool]
    normalize_abstract_candidate_text: Callable[[list[dict[str, Any]]], str]
    front_matter_missing_placeholder: str
    clean_heading_title: Callable[[str], str]
    parse_heading_label: Callable[[str], Any]
    abstract_quality_flags: Callable[[str], list[str]]
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]]
    abstract_text_is_recoverable: Callable[[str], bool]
    replace_front_matter_abstract_text: Callable[[dict[str, Any], list[dict[str, Any]], str, list[dict[str, Any]]], bool]
    opening_abstract_candidate_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    record_analysis_text: Callable[[dict[str, Any]], str]
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool]
    caption_label: Callable[[str], str | None]
    looks_like_real_code_record: Callable[[str], bool]
    split_code_lines: Callable[[str], list[str]]
    list_item_marker: Callable[[str], tuple[str | None, bool, str]]
    review_for_math_entry: Callable[..., dict[str, Any]]
    review_for_math_ref_block: Callable[..., dict[str, Any]]
    build_block_math_entry: Callable[..., dict[str, Any]]
    normalize_formula_display_text: Callable[[str], str]
    classify_math_block: Callable[..., str]
    review_for_algorithm_block_text: Callable[..., dict[str, Any]]
    display_math_prose_cue_re: Any
    display_math_resume_re: Any
    display_math_start_re: Any
    short_word_re: Any
    layout_record: Callable[[Any], dict[str, Any]]
    absorb_figure_caption_continuations: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]]
    figure_label_token: Callable[[dict[str, Any]], str | None]
    synthetic_caption_record: Callable[[dict[str, Any], list[Any]], dict[str, Any]]
    inject_external_math_records: Callable[[list[dict[str, Any]], list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]]
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[Any]]]
    mathpix_text_hint_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str]
    is_mathpix_text_hint_better: Callable[[str, str], bool]
    mathpix_prose_lead_repair_candidate: Callable[[dict[str, Any], dict[int, list[Any]]], str]
    looks_like_bad_heading: Callable[[str], bool]
    collapse_ocr_split_caps: Callable[[str], str]
    decode_control_heading_label: Callable[[str], tuple[str | None, str]]
    normalize_decoded_heading_title: Callable[[str], str]
    split_embedded_heading_paragraph: Callable[[dict[str, Any]], tuple[str, str] | None]


@dataclass(frozen=True)
class ReconcileAssemblyDeps:
    merge_math_fragment_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    page_one_front_matter_records: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]]
    is_title_page_metadata_record: Callable[[dict[str, Any]], bool]
    build_section_tree: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[Any]]]
    attach_orphan_numbered_roots: Callable[[list[Any]], list[Any]]
    split_late_prelude_for_missing_intro: Callable[[list[dict[str, Any]], list[Any]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    build_abstract_decision: Callable[..., dict[str, Any]]
    should_replace_front_matter_abstract: Callable[[str], bool]
    section_node_type: Any
    prepare_section_nodes: Callable[..., list[Any]]
    split_trailing_reference_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    extract_reference_records_from_tail_section: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]]
    reference_records_from_mathpix_layout: Callable[[dict[str, Any] | None], list[dict[str, Any]]]
    materialize_sections: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]]
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    is_figure_debris: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], bool]
    looks_like_running_header_record: Callable[[dict[str, Any]], bool]
    looks_like_table_body_debris: Callable[[dict[str, Any]], bool]
    suppress_embedded_table_headings: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    should_merge_paragraph_records: Callable[[dict[str, Any], dict[str, Any]], bool]
    table_caption_re: Any
    compile_formulas: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    annotate_formula_classifications: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    annotate_formula_semantic_expr: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    compact_text: Callable[[str], str]
    running_header_text_re: Any
    starts_like_sentence: Callable[[str], bool]
    now_iso: Callable[[], str]
    build_canonical_document: Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ReconcileRuntimeDeps:
    loaders: ReconcileLoaderDeps
    bindings: ReconcileBindingDeps
    assembly: ReconcileAssemblyDeps


def run_reconcile_pipeline(
    inputs: ReconcileRuntimeInputs,
    deps: ReconcileRuntimeDeps,
) -> Any:
    pipeline_deps = build_reconcile_paper_pipeline_deps(
        runtime_layout=inputs.runtime_layout,
        loaders=deps.loaders,
        bindings=deps.bindings,
        assembly=deps.assembly,
    )
    return deps.loaders.run_paper_pipeline_impl(
        inputs.paper_id,
        text_engine=inputs.text_engine,
        use_external_layout=inputs.use_external_layout,
        use_external_math=inputs.use_external_math,
        layout_output=inputs.layout_output,
        figures=inputs.figures,
        deps=pipeline_deps,
        config=inputs.config,
        state=inputs.state,
    )
