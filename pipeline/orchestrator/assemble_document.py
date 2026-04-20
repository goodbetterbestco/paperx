from __future__ import annotations

from typing import Any

from pipeline.orchestrator.pipeline_deps import PaperDocumentAssemblyDeps
from pipeline.state import PaperState


def assemble_paper_document(
    state: PaperState,
    *,
    deps: PaperDocumentAssemblyDeps,
) -> PaperState:
    layout = state.merged_layout or state.native_layout
    if layout is None:
        raise RuntimeError(f"Missing resolved layout for {state.paper_id}")

    blocks: list[dict[str, Any]] = []
    prelude = list(state.prelude_records)
    front_matter, blocks, next_block_index, remaining_prelude = deps.build_front_matter(
        state.paper_id,
        prelude,
        state.page_one_records,
        blocks,
        1,
    )
    title_decision = front_matter.pop("_debug_title_decision", None)
    abstract_decision = front_matter.pop("_debug_abstract_decision", None)

    ordered_roots = deps.attach_orphan_numbered_roots(list(state.section_roots))
    if not remaining_prelude and front_matter.get("abstract_block_id"):
        trimmed_prelude, overflow_prelude = deps.split_late_prelude_for_missing_intro(prelude, ordered_roots)
        if overflow_prelude:
            front_matter, blocks, next_block_index, _ = deps.build_front_matter(
                state.paper_id,
                trimmed_prelude,
                state.page_one_records,
                [],
                1,
            )
            title_decision = front_matter.pop("_debug_title_decision", None)
            abstract_decision = front_matter.pop("_debug_abstract_decision", None)
            remaining_prelude = overflow_prelude
    if ordered_roots and deps.normalize_section_title(str(ordered_roots[0].title)) == "abstract":
        abstract_text, abstract_records = deps.leading_abstract_text(ordered_roots[0])
        if abstract_text:
            current_abstract_text = deps.front_block_text(blocks, front_matter.get("abstract_block_id"))
            if not front_matter.get("abstract_block_id"):
                abstract_block_id = f"blk-front-abstract-{next_block_index}"
                blocks.append(
                    {
                        "id": abstract_block_id,
                        "type": "paragraph",
                        "content": {"spans": [{"kind": "text", "text": abstract_text}]},
                        "source_spans": [span for record in abstract_records for span in deps.block_source_spans(record)],
                        "alternates": [],
                        "review": deps.default_review(risk="medium"),
                    }
                )
                front_matter["abstract_block_id"] = abstract_block_id
                next_block_index += 1
                abstract_decision = deps.build_abstract_decision(
                    abstract_text=abstract_text,
                    source="leading_abstract_section_created",
                    candidate_records=abstract_records,
                )
            elif deps.should_replace_front_matter_abstract(current_abstract_text):
                for block in blocks:
                    if str(block.get("id", "")) != str(front_matter["abstract_block_id"]):
                        continue
                    block["content"] = {"spans": [{"kind": "text", "text": abstract_text}]}
                    block["source_spans"] = [span for record in abstract_records for span in deps.block_source_spans(record)]
                    abstract_decision = deps.build_abstract_decision(
                        abstract_text=abstract_text,
                        source="leading_abstract_section_replaced",
                        candidate_records=abstract_records,
                    )
                    break
        if front_matter.get("abstract_block_id"):
            ordered_roots = ordered_roots[1:]
    if deps.recover_missing_front_matter_abstract(front_matter, blocks, prelude, ordered_roots):
        abstract_decision = deps.build_abstract_decision(
            abstract_text=deps.front_block_text(blocks, front_matter.get("abstract_block_id")),
            source="recovered_from_body_or_prelude",
            candidate_records=[],
        )
    if remaining_prelude and (not ordered_roots or not str(ordered_roots[0].title).lower().endswith("introduction")):
        intro_node = deps.section_node_type(
            title="Introduction",
            level=1,
            heading_id="synthetic-introduction",
            label=("1",) if ordered_roots and getattr(ordered_roots[0], "label", None) and ordered_roots[0].label[0] != "1" else None,
            records=remaining_prelude,
            children=[],
        )
        ordered_roots = [intro_node, *ordered_roots]

    figures_by_label = {
        (deps.figure_label_token(figure) or ""): figure
        for figure in state.figures
    }
    figures_by_page: dict[int, list[dict[str, Any]]] = {}
    for figure in state.figures:
        figures_by_page.setdefault(int(figure["page"]), []).append(figure)
    counters = {
        "block": next_block_index,
        "math": 1,
        "inline_math": 1,
        "reference": 1,
    }

    section_nodes = deps.prepare_section_nodes(
        ordered_roots=ordered_roots,
        normalize_section_title=deps.normalize_section_title,
        split_trailing_reference_records=deps.split_trailing_reference_records,
        extract_reference_records_from_tail_section=deps.extract_reference_records_from_tail_section,
        reference_records_from_mathpix_layout=deps.reference_records_from_mathpix_layout,
        mathpix_layout=state.mathpix_layout,
    )
    blocks, sections, all_math, all_references = deps.materialize_sections(
        section_nodes=section_nodes,
        records=state.records,
        blocks=blocks,
        counters=counters,
        layout_by_id=state.layout_by_id,
        figures_by_label=figures_by_label,
        figures_by_page=figures_by_page,
        external_math_page_map=state.external_math_page_map,
        external_math_overlap_page_map=state.external_math_overlap_page_map,
        section_id_for=deps.section_id_for,
        normalize_section_title=deps.normalize_section_title,
        merge_reference_records=deps.merge_reference_records,
        is_figure_debris=deps.is_figure_debris,
        looks_like_running_header_record=deps.looks_like_running_header_record,
        looks_like_table_body_debris=deps.looks_like_table_body_debris,
        is_short_ocr_fragment=deps.is_short_ocr_fragment,
        suppress_embedded_table_headings=deps.suppress_embedded_table_headings,
        merge_code_records=deps.merge_code_records,
        merge_paragraph_records=deps.merge_paragraph_records,
        build_blocks_for_record=deps.build_blocks_for_record,
        clean_text=deps.clean_text,
        block_source_spans=deps.block_source_spans,
    )

    compiled_math = deps.annotate_formula_semantic_expr(
        deps.annotate_formula_classifications(deps.compile_formulas(all_math))
    )
    blocks, compiled_math, sections = deps.suppress_graphic_display_math_blocks(
        blocks,
        compiled_math,
        sections,
        counters,
    )
    blocks, sections = deps.suppress_running_header_blocks(blocks, sections)
    blocks, sections = deps.normalize_footnote_blocks(blocks, sections)
    blocks, sections = deps.merge_paragraph_blocks(blocks, sections)
    compiled_math = deps.annotate_formula_semantic_expr(
        deps.annotate_formula_classifications(deps.compile_formulas(compiled_math))
    )

    decision_artifacts: dict[str, Any] = {}
    if state.acquisition_route:
        decision_artifacts["acquisition_route"] = state.acquisition_route
    if state.source_scorecard:
        decision_artifacts["source_scorecard"] = state.source_scorecard
    if title_decision:
        decision_artifacts["title"] = title_decision
    if abstract_decision:
        decision_artifacts["abstract"] = abstract_decision

    state.front_matter = front_matter
    state.blocks = blocks
    state.sections = sections
    state.math_entries = compiled_math
    state.references = all_references
    state.decision_artifacts = decision_artifacts
    state.document = deps.build_canonical_document(
        paper_id=state.paper_id,
        title=front_matter["title"],
        source={
            "pdf_path": layout["pdf_path"],
            "page_count": int(layout["page_count"]),
            "page_sizes_pt": list(layout["page_sizes_pt"]),
        },
        timestamp=deps.now_iso(),
        layout_engine_name=state.layout_engine_name,
        math_engine_name=state.math_engine_name,
        effective_text_engine=state.effective_text_engine,
        use_external_layout=state.layout_engine_name != "native_pdf",
        use_external_math=state.math_engine_name != "heuristic",
        front_matter=front_matter,
        sections=sections,
        blocks=blocks,
        math_entries=compiled_math,
        figures=state.figures,
        references=all_references,
        decision_artifacts=decision_artifacts or None,
    )
    return state
