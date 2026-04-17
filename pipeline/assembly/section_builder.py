from __future__ import annotations

from typing import Any


def materialize_sections(
    *,
    section_nodes: list[Any],
    records: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    counters: dict[str, int],
    layout_by_id: dict[str, Any],
    figures_by_label: dict[str, dict[str, Any]],
    figures_by_page: dict[int, list[dict[str, Any]]],
    external_math_page_map: dict[int, list[dict[str, Any]]],
    external_math_overlap_page_map: dict[int, list[dict[str, Any]]],
    section_id_for: Any,
    normalize_section_title: Any,
    merge_reference_records: Any,
    is_figure_debris: Any,
    looks_like_running_header_record: Any,
    looks_like_table_body_debris: Any,
    is_short_ocr_fragment: Any,
    suppress_embedded_table_headings: Any,
    merge_code_records: Any,
    merge_paragraph_records: Any,
    build_blocks_for_record: Any,
    clean_text: Any,
    block_source_spans: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sections: list[dict[str, Any]] = []
    all_references: list[dict[str, Any]] = []
    all_math: list[dict[str, Any]] = []

    for index, node in enumerate(section_nodes):
        section_id = section_id_for(node, index + 1)
        section_title_key = normalize_section_title(str(node.title))
        references_section = section_title_key == "references"
        section_block_ids: list[str] = []
        if references_section:
            section_records = merge_reference_records(node.records)
        else:
            section_records = [
                record
                for record in node.records
                if not is_figure_debris(record, figures_by_page)
                and not looks_like_running_header_record(record)
                and not looks_like_table_body_debris(record)
                and not is_short_ocr_fragment(record)
            ]
            section_records = suppress_embedded_table_headings(section_records)
            section_records = merge_code_records(section_records)
            section_records = merge_paragraph_records(section_records)
        for record in section_records:
            new_blocks, math_entries, references = build_blocks_for_record(
                record,
                layout_by_id,
                figures_by_label,
                external_math_page_map,
                external_math_overlap_page_map,
                references_section,
                counters,
            )
            blocks.extend(new_blocks)
            all_math.extend(math_entries)
            all_references.extend(references)
            section_block_ids.extend(block["id"] for block in new_blocks)

        heading_record = next((record for record in records if str(record.get("id", "")) == str(node.heading_id)), None)
        sections.append(
            {
                "id": section_id,
                "label": ".".join(node.label) if getattr(node, "label", None) else None,
                "title": clean_text(str(node.title)),
                "level": int(node.level),
                "block_ids": section_block_ids,
                "children": [section_id_for(child, 0) for child in node.children],
                "source_spans": block_source_spans(heading_record or {}),
            }
        )

    return blocks, sections, all_math, all_references
