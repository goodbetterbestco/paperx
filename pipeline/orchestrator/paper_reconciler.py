from __future__ import annotations

from typing import Any, Callable


def reconcile_paper_document(
    paper_id: str,
    *,
    text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
    layout_output: dict[str, Any] | None,
    figures: list[dict[str, Any]] | None,
    extract_layout: Callable[[str], dict[str, Any]],
    load_external_layout: Callable[[str], dict[str, Any] | None],
    merge_native_and_external_layout: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    load_external_math: Callable[[str], dict[str, Any] | None],
    external_math_by_page: Callable[[list[dict[str, Any]]], dict[int, list[dict[str, Any]]]],
    load_mathpix_layout: Callable[[str], dict[str, Any] | None],
    extract_figures: Callable[[str], list[dict[str, Any]]],
    normalize_figure_caption_text: Callable[[str], str],
    merge_layout_and_figure_records: Callable[[list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, Any]]],
    inject_external_math_records: Callable[[list[dict[str, Any]], list[Any], list[dict[str, Any]]], tuple[list[dict[str, Any]], set[str]]],
    mark_records_with_external_math_overlap: Callable[[list[dict[str, Any]], dict[int, list[dict[str, Any]]]], list[dict[str, Any]]],
    repair_record_text_with_mathpix_hints: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]],
    pdftotext_available: Callable[[], bool],
    repair_record_text_with_pdftotext: Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]],
    extract_pdftotext_pages: Callable[[str], dict[int, list[str]]],
    page_height_map: Callable[[dict[str, Any]], dict[int, float]],
    promote_heading_like_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    merge_math_fragment_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    page_one_front_matter_records: Callable[[list[dict[str, Any]], dict[str, Any] | None], list[dict[str, Any]]],
    is_title_page_metadata_record: Callable[[dict[str, Any]], bool],
    build_section_tree: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[Any]]],
    build_front_matter: Callable[[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int], tuple[dict[str, Any], list[dict[str, Any]], int, list[dict[str, Any]]]],
    attach_orphan_numbered_roots: Callable[[list[Any]], list[Any]],
    split_late_prelude_for_missing_intro: Callable[[list[dict[str, Any]], list[Any]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    normalize_section_title: Callable[[str], str],
    leading_abstract_text: Callable[[Any], tuple[str, list[dict[str, Any]]]],
    front_block_text: Callable[[list[dict[str, Any]], str | None], str],
    default_review: Callable[..., dict[str, Any]],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    build_abstract_decision: Callable[..., dict[str, Any]],
    should_replace_front_matter_abstract: Callable[[str], bool],
    recover_missing_front_matter_abstract: Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[Any]], bool],
    section_node_type: Any,
    figure_label_token: Callable[[dict[str, Any]], str | None],
    prepare_section_nodes: Callable[..., list[Any]],
    split_trailing_reference_records: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    extract_reference_records_from_tail_section: Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    reference_records_from_mathpix_layout: Callable[[dict[str, Any] | None], list[dict[str, Any]]],
    materialize_sections: Callable[..., tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    section_id_for: Callable[[Any, int], str],
    merge_reference_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    is_figure_debris: Callable[[dict[str, Any], dict[int, list[dict[str, Any]]]], bool],
    looks_like_running_header_record: Callable[[dict[str, Any]], bool],
    looks_like_table_body_debris: Callable[[dict[str, Any]], bool],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    suppress_embedded_table_headings: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    merge_code_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    merge_paragraph_records: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    build_blocks_for_record: Callable[[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[int, list[dict[str, Any]]], dict[int, list[dict[str, Any]]], bool, dict[str, int]], tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    clean_text: Callable[[str], str],
    compile_formulas: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    annotate_formula_classifications: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    annotate_formula_semantic_expr: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
    suppress_graphic_display_math_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]], tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]],
    suppress_running_header_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    normalize_footnote_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    merge_paragraph_blocks: Callable[[list[dict[str, Any]], list[dict[str, Any]]], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    now_iso: Callable[[], str],
    build_canonical_document: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    native_layout = layout_output or extract_layout(paper_id)
    layout = native_layout
    external_layout_engine: str | None = None
    if use_external_layout:
        external_layout = load_external_layout(paper_id)
        if external_layout and external_layout.get("blocks"):
            layout = merge_native_and_external_layout(native_layout, external_layout)
            external_layout_engine = str(external_layout.get("engine", "external_layout"))

    external_math_payload = load_external_math(paper_id) if use_external_math else None
    external_math_entries = list((external_math_payload or {}).get("entries", []))
    external_math_engine = str((external_math_payload or {}).get("engine", "")) or None
    external_math_overlap_page_map = external_math_by_page(external_math_entries)
    mathpix_layout = load_mathpix_layout(paper_id) if use_external_math else None

    figures = figures or extract_figures(paper_id)
    figures = [
        {
            **figure,
            "caption": normalize_figure_caption_text(str(figure.get("caption", ""))),
        }
        for figure in figures
    ]
    layout_blocks = list(layout["blocks"])
    records, layout_by_id = merge_layout_and_figure_records(layout_blocks, figures)
    records, injected_external_math_ids = inject_external_math_records(records, layout_blocks, external_math_entries)
    external_math_entries = [entry for entry in external_math_entries if str(entry.get("id", "")) not in injected_external_math_ids]
    records = mark_records_with_external_math_overlap(records, external_math_overlap_page_map)
    records = repair_record_text_with_mathpix_hints(records, mathpix_layout)
    effective_text_engine = "native_pdf"
    if text_engine in {"pdftotext", "hybrid"} and pdftotext_available():
        records = repair_record_text_with_pdftotext(records, extract_pdftotext_pages(paper_id), page_height_map(layout))
        effective_text_engine = "native_pdf+pdftotext"
    records = promote_heading_like_records(records)
    records = merge_math_fragment_records(records)
    page_one_records = page_one_front_matter_records(records, mathpix_layout)
    records = [record for record in records if not is_title_page_metadata_record(record)]
    prelude, roots = build_section_tree(records)

    blocks: list[dict[str, Any]] = []
    front_matter, blocks, next_block_index, remaining_prelude = build_front_matter(
        paper_id,
        prelude,
        page_one_records,
        blocks,
        1,
    )
    title_decision = front_matter.pop("_debug_title_decision", None)
    abstract_decision = front_matter.pop("_debug_abstract_decision", None)

    ordered_roots = attach_orphan_numbered_roots(list(roots))
    if not remaining_prelude and front_matter.get("abstract_block_id"):
        trimmed_prelude, overflow_prelude = split_late_prelude_for_missing_intro(prelude, ordered_roots)
        if overflow_prelude:
            front_matter, blocks, next_block_index, _ = build_front_matter(
                paper_id,
                trimmed_prelude,
                page_one_records,
                [],
                1,
            )
            title_decision = front_matter.pop("_debug_title_decision", None)
            abstract_decision = front_matter.pop("_debug_abstract_decision", None)
            remaining_prelude = overflow_prelude
    if ordered_roots and normalize_section_title(str(ordered_roots[0].title)) == "abstract":
        abstract_text, abstract_records = leading_abstract_text(ordered_roots[0])
        if abstract_text:
            current_abstract_text = front_block_text(blocks, front_matter.get("abstract_block_id"))
            if not front_matter.get("abstract_block_id"):
                abstract_block_id = f"blk-front-abstract-{next_block_index}"
                blocks.append(
                    {
                        "id": abstract_block_id,
                        "type": "paragraph",
                        "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                        "source_spans": [span for record in abstract_records for span in block_source_spans(record)],
                        "alternates": [],
                        "review": default_review(risk="medium"),
                    }
                )
                front_matter["abstract_block_id"] = abstract_block_id
                next_block_index += 1
                abstract_decision = build_abstract_decision(
                    abstract_text=abstract_text,
                    source="leading_abstract_section_created",
                    candidate_records=abstract_records,
                )
            elif should_replace_front_matter_abstract(current_abstract_text):
                for block in blocks:
                    if str(block.get("id", "")) != str(front_matter["abstract_block_id"]):
                        continue
                    block["content"] = {"spans": [{"kind": "text", "text": abstract_text}]}
                    block["source_spans"] = [span for record in abstract_records for span in block_source_spans(record)]
                    abstract_decision = build_abstract_decision(
                        abstract_text=abstract_text,
                        source="leading_abstract_section_replaced",
                        candidate_records=abstract_records,
                    )
                    break
        if front_matter.get("abstract_block_id"):
            ordered_roots = ordered_roots[1:]
    if recover_missing_front_matter_abstract(front_matter, blocks, prelude, ordered_roots):
        abstract_decision = build_abstract_decision(
            abstract_text=front_block_text(blocks, front_matter.get("abstract_block_id")),
            source="recovered_from_body_or_prelude",
            candidate_records=[],
        )
    if remaining_prelude and (not ordered_roots or not str(ordered_roots[0].title).lower().endswith("introduction")):
        intro_node = section_node_type(
            title="Introduction",
            level=1,
            heading_id="synthetic-introduction",
            label=("1",) if ordered_roots and getattr(ordered_roots[0], "label", None) and ordered_roots[0].label[0] != "1" else None,
            records=remaining_prelude,
            children=[],
        )
        ordered_roots = [intro_node, *ordered_roots]

    figures_by_label = {
        (figure_label_token(figure) or ""): figure
        for figure in figures
    }
    figures_by_page: dict[int, list[dict[str, Any]]] = {}
    for figure in figures:
        figures_by_page.setdefault(int(figure["page"]), []).append(figure)
    counters = {
        "block": next_block_index,
        "math": 1,
        "inline_math": 1,
        "reference": 1,
    }
    external_math_page_map = external_math_by_page(external_math_entries)

    section_nodes = prepare_section_nodes(
        ordered_roots=ordered_roots,
        normalize_section_title=normalize_section_title,
        split_trailing_reference_records=split_trailing_reference_records,
        extract_reference_records_from_tail_section=extract_reference_records_from_tail_section,
        reference_records_from_mathpix_layout=reference_records_from_mathpix_layout,
        mathpix_layout=mathpix_layout,
    )
    blocks, sections, all_math, all_references = materialize_sections(
        section_nodes=section_nodes,
        records=records,
        blocks=blocks,
        counters=counters,
        layout_by_id=layout_by_id,
        figures_by_label=figures_by_label,
        figures_by_page=figures_by_page,
        external_math_page_map=external_math_page_map,
        external_math_overlap_page_map=external_math_overlap_page_map,
        section_id_for=section_id_for,
        normalize_section_title=normalize_section_title,
        merge_reference_records=merge_reference_records,
        is_figure_debris=is_figure_debris,
        looks_like_running_header_record=looks_like_running_header_record,
        looks_like_table_body_debris=looks_like_table_body_debris,
        is_short_ocr_fragment=is_short_ocr_fragment,
        suppress_embedded_table_headings=suppress_embedded_table_headings,
        merge_code_records=merge_code_records,
        merge_paragraph_records=merge_paragraph_records,
        build_blocks_for_record=build_blocks_for_record,
        clean_text=clean_text,
        block_source_spans=block_source_spans,
    )

    compiled_math = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(all_math))
    )
    blocks, compiled_math, sections = suppress_graphic_display_math_blocks(
        blocks,
        compiled_math,
        sections,
        counters,
    )
    blocks, sections = suppress_running_header_blocks(blocks, sections)
    blocks, sections = normalize_footnote_blocks(blocks, sections)
    blocks, sections = merge_paragraph_blocks(blocks, sections)
    compiled_math = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(compiled_math))
    )
    timestamp = now_iso()
    layout_engine_name = external_layout_engine or "native_pdf"
    if external_math_engine:
        math_engine_name = f"{external_math_engine}+heuristic"
    else:
        math_engine_name = "heuristic"
    decision_artifacts: dict[str, Any] | None = None
    if title_decision or abstract_decision:
        decision_artifacts = {}
        if title_decision:
            decision_artifacts["title"] = title_decision
        if abstract_decision:
            decision_artifacts["abstract"] = abstract_decision
    return build_canonical_document(
        paper_id=paper_id,
        title=front_matter["title"],
        source={
            "pdf_path": layout["pdf_path"],
            "page_count": int(layout["page_count"]),
            "page_sizes_pt": list(layout["page_sizes_pt"]),
        },
        timestamp=timestamp,
        layout_engine_name=layout_engine_name,
        math_engine_name=math_engine_name,
        effective_text_engine=effective_text_engine,
        use_external_layout=bool(external_layout_engine),
        use_external_math=bool(external_math_engine),
        front_matter=front_matter,
        sections=sections,
        blocks=blocks,
        math_entries=compiled_math,
        figures=figures,
        references=all_references,
        decision_artifacts=decision_artifacts,
    )
