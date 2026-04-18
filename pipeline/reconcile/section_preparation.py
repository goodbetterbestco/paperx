from __future__ import annotations

from typing import Any

from pipeline.text.headings import SectionNode


def flatten_sections(roots: list[Any]) -> list[Any]:
    ordered: list[Any] = []

    def visit(node: Any) -> None:
        ordered.append(node)
        for child in node.children:
            visit(child)

    for root in roots:
        visit(root)
    return ordered


def attach_orphan_numbered_roots(roots: list[Any]) -> list[Any]:
    adjusted: list[Any] = []
    index = 0
    while index < len(roots):
        node = roots[index]
        title_key = str(getattr(node, "title", "")).strip().lower()
        if getattr(node, "label", None) is None and title_key in {"background", "introduction"}:
            expected_prefix = "2" if title_key == "background" else "1"
            children: list[Any] = list(node.children)
            next_index = index + 1
            while next_index < len(roots):
                candidate = roots[next_index]
                label = getattr(candidate, "label", None)
                if not label:
                    break
                if label[0] != expected_prefix or len(label) <= 1:
                    break
                children.append(candidate)
                next_index += 1
            node.children = children
            if title_key == "background":
                node.label = ("2",)
            elif title_key == "introduction":
                node.label = ("1",)
            adjusted.append(node)
            index = next_index
            continue
        adjusted.append(node)
        index += 1
    return adjusted


def prepare_section_nodes(
    *,
    ordered_roots: list[Any],
    normalize_section_title: Any,
    split_trailing_reference_records: Any,
    extract_reference_records_from_tail_section: Any,
    reference_records_from_mathpix_layout: Any,
    mathpix_layout: dict[str, Any] | None,
) -> list[Any]:
    section_nodes = flatten_sections(ordered_roots)
    if section_nodes and all(normalize_section_title(str(node.title)) != "references" for node in section_nodes):
        body_records, trailing_reference_records = split_trailing_reference_records(section_nodes[-1].records)
        if trailing_reference_records:
            section_nodes[-1].records = body_records
            section_nodes.append(
                SectionNode(
                    title="References",
                    level=1,
                    heading_id="synthetic-references",
                    records=trailing_reference_records,
                    children=[],
                )
            )
        else:
            body_records, harvested_reference_records = extract_reference_records_from_tail_section(section_nodes[-1].records)
            if harvested_reference_records:
                section_nodes[-1].records = body_records
                section_nodes.append(
                    SectionNode(
                        title="References",
                        level=1,
                        heading_id="synthetic-tail-references",
                        records=harvested_reference_records,
                        children=[],
                    )
                )
            else:
                mathpix_reference_records = reference_records_from_mathpix_layout(mathpix_layout)
                if mathpix_reference_records:
                    section_nodes.append(
                        SectionNode(
                            title="References",
                            level=1,
                            heading_id="synthetic-mathpix-references",
                            records=mathpix_reference_records,
                            children=[],
                        )
                    )
    return section_nodes
