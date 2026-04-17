from __future__ import annotations

from typing import Any

from pipeline.types import LayoutBlock


def merge_native_and_external_layout(native_layout: dict[str, Any], external_layout: dict[str, Any]) -> dict[str, Any]:
    native_blocks: list[LayoutBlock] = list(native_layout.get("blocks", []))
    external_blocks: list[LayoutBlock] = list(external_layout.get("blocks", []))
    external_pages = {int(block.page) for block in external_blocks}
    merged_blocks = [block for block in native_blocks if int(block.page) not in external_pages]
    merged_blocks.extend(external_blocks)
    merged_blocks.sort(key=lambda block: (int(block.page), int(block.order), str(block.id)))
    return {
        "pdf_path": external_layout.get("pdf_path") or native_layout["pdf_path"],
        "page_count": external_layout.get("page_count") or native_layout["page_count"],
        "page_sizes_pt": external_layout.get("page_sizes_pt") or native_layout["page_sizes_pt"],
        "blocks": merged_blocks,
    }
