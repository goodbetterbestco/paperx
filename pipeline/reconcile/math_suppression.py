from __future__ import annotations

import re
from typing import Any, Callable, Pattern

from pipeline.extract_math import looks_like_prose_math_fragment, looks_like_prose_paragraph


def suppress_graphic_display_math_blocks(
    blocks: list[dict[str, Any]],
    math_entries: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    counters: dict[str, int],
    *,
    should_demote_graphic_math_entry_to_paragraph: Callable[[dict[str, Any]], bool],
    paragraph_block_from_graphic_math_entry: Callable[[dict[str, Any], dict[str, Any], dict[str, int]], tuple[dict[str, Any] | None, list[dict[str, Any]]]],
    should_drop_display_math_artifact: Callable[[dict[str, Any]], bool],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    math_by_id = {
        str(entry.get("id", "")): entry
        for entry in math_entries
        if isinstance(entry, dict) and str(entry.get("id", ""))
    }

    rewritten_blocks: list[dict[str, Any]] = []
    removed_block_ids: set[str] = set()
    removed_math_ids: set[str] = set()
    added_math_entries: list[dict[str, Any]] = []

    for block in blocks:
        block_type = str(block.get("type", ""))
        if block_type not in {"display_equation_ref", "equation_group_ref"}:
            rewritten_blocks.append(block)
            continue

        content = block.get("content")
        math_id = str(content.get("math_id", "")) if isinstance(content, dict) else ""
        math_entry = math_by_id.get(math_id)
        if math_entry is None:
            rewritten_blocks.append(block)
            continue

        if should_demote_graphic_math_entry_to_paragraph(math_entry):
            paragraph_block, inline_math_entries = paragraph_block_from_graphic_math_entry(block, math_entry, counters)
            removed_math_ids.add(math_id)
            if paragraph_block is None:
                removed_block_ids.add(str(block.get("id", "")))
                continue
            rewritten_blocks.append(paragraph_block)
            added_math_entries.extend(inline_math_entries)
            continue

        if should_drop_display_math_artifact(math_entry):
            removed_block_ids.add(str(block.get("id", "")))
            removed_math_ids.add(math_id)
            continue

        rewritten_blocks.append(block)

    rewritten_sections: list[dict[str, Any]] = []
    for section in sections:
        updated_section = dict(section)
        updated_section["block_ids"] = [
            block_id
            for block_id in section.get("block_ids", [])
            if str(block_id) not in removed_block_ids
        ]
        rewritten_sections.append(updated_section)

    kept_math_entries = [
        entry for entry in math_entries if str(entry.get("id", "")) not in removed_math_ids
    ]
    kept_math_entries.extend(added_math_entries)
    return rewritten_blocks, kept_math_entries, rewritten_sections


def external_math_by_page(entries: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for entry in entries:
        for span in entry.get("source_spans", []):
            page = int(span.get("page", 0) or 0)
            if page <= 0:
                continue
            grouped.setdefault(page, []).append(entry)
            break
    return grouped


def overlapping_external_math_entries(
    record: dict[str, Any],
    external_math_by_page_map: dict[int, list[dict[str, Any]]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    minimum_score: float = 0.75,
) -> list[dict[str, Any]]:
    source_span = (block_source_spans(record)[:1] or [{}])[0]
    page = int(source_span.get("page", record.get("page", 0)) or 0)
    record_bbox = source_span.get("bbox", {})
    if not page or not record_bbox:
        return []

    def rect_intersection_area(a: dict[str, Any], b: dict[str, Any]) -> float:
        x0 = max(float(a.get("x0", 0.0)), float(b.get("x0", 0.0)))
        y0 = max(float(a.get("y0", 0.0)), float(b.get("y0", 0.0)))
        x1 = min(float(a.get("x1", 0.0)), float(b.get("x1", 0.0)))
        y1 = min(float(a.get("y1", 0.0)), float(b.get("y1", 0.0)))
        if x1 <= x0 or y1 <= y0:
            return 0.0
        return (x1 - x0) * (y1 - y0)

    def rect_area(rect: dict[str, Any]) -> float:
        return max(float(rect.get("width", 0.0)) * float(rect.get("height", 0.0)), 1.0)

    record_area = rect_area(record_bbox)
    matches: list[tuple[float, dict[str, Any]]] = []
    for entry in external_math_by_page_map.get(page, []):
        if entry.get("kind") not in {"display", "group"}:
            continue
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        if not entry_bbox:
            continue
        overlap = rect_intersection_area(record_bbox, entry_bbox)
        if overlap <= 0.0:
            continue
        entry_area = rect_area(entry_bbox)
        score = overlap / min(record_area, entry_area)
        if score >= minimum_score:
            matches.append((score, entry))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in matches]


def trim_embedded_display_math_from_paragraph(
    text: str,
    record: dict[str, Any],
    overlapping_math: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Pattern[str],
    display_math_resume_re: Pattern[str],
    display_math_start_re: Pattern[str],
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
) -> str:
    if overlapping_math:
        cue_match = display_math_prose_cue_re.search(text)
        if cue_match:
            prefix = text[: cue_match.start()].strip(" ;:")
            if prefix and len(prefix) <= 240 and (mathish_ratio(prefix) >= 0.25 or (prefix.count("=") >= 1 and strong_operator_count(prefix) >= 1)):
                text = text[cue_match.start() :].lstrip(" ;:")

    resume = display_math_resume_re.search(text)
    if resume and resume.start() > 10:
        prefix = text[: resume.start()].strip()
        if prefix and len(prefix) <= 220 and (mathish_ratio(prefix) >= 0.1 or prefix.startswith("$") or "=" in prefix or "^" in prefix):
            text = text[resume.start() :].lstrip()

    if not overlapping_math:
        return clean_text(text)

    trimmed = text
    source_span = (block_source_spans(record)[:1] or [{}])[0]
    bbox = source_span.get("bbox", {})
    record_height = float(bbox.get("height", 0.0))
    record_y0 = float(bbox.get("y0", 0.0))
    cue_phrases = (
        "as follows:",
        "such that",
        "given by",
        "equations become",
        "equation in this case is",
        "with respect to s and t .",
        "corresponding to the eigendecomposition of",
        "determinant",
    )

    for entry in overlapping_math:
        entry_span = (entry.get("source_spans") or [{}])[0]
        entry_bbox = entry_span.get("bbox", {})
        entry_y0 = float(entry_bbox.get("y0", 0.0))
        entry_y1 = float(entry_bbox.get("y1", 0.0))
        starts_low = record_height > 0 and entry_y0 >= record_y0 + record_height * 0.45
        starts_high = record_height > 0 and entry_y1 <= record_y0 + record_height * 0.55

        cue_matches = [trimmed.lower().rfind(cue) for cue in cue_phrases]
        cue_index = max(cue_matches)
        if cue_index >= 0:
            matched_cue = max((cue for cue in cue_phrases if trimmed.lower().rfind(cue) == cue_index), key=len)
            cue_end = cue_index + len(matched_cue)
            suffix = trimmed[cue_end:].strip()
            if suffix and (len(suffix) >= 20 and mathish_ratio(suffix) >= 0.15):
                trimmed = trimmed[:cue_end].rstrip()
                continue

        if starts_low:
            match = display_math_start_re.search(trimmed)
            if match and match.start() >= 80 and mathish_ratio(trimmed[match.start() :]) >= 0.35:
                trimmed = trimmed[: match.start()].rstrip()
                continue

        if starts_high:
            resume = display_math_resume_re.search(trimmed)
            prefix = trimmed[: resume.start()].strip() if resume else ""
            if (
                resume
                and resume.start() > 10
                and len(prefix) <= 220
                and (mathish_ratio(prefix) >= 0.1 or "=" in prefix or "^" in prefix)
            ):
                trimmed = trimmed[resume.start() :].lstrip()

    return clean_text(trimmed)


def looks_like_display_math_echo(
    record: dict[str, Any],
    text: str,
    overlapping_math: list[dict[str, Any]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    clean_text: Callable[[str], str],
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
    short_word_re: Pattern[str],
) -> bool:
    if not overlapping_math:
        return False
    cleaned = clean_text(text)
    if not cleaned:
        return False
    strong_count = strong_operator_count(cleaned)
    if looks_like_prose_paragraph(cleaned) and not (mathish_ratio(cleaned) >= 0.3 and strong_count >= 2):
        return False
    if looks_like_prose_math_fragment(cleaned):
        return False
    word_count = len(short_word_re.findall(cleaned))
    if word_count > 40:
        return False
    tokens = [token.strip(".,;:()[]{}") for token in cleaned.split() if token.strip(".,;:()[]{}")]
    prose_token_count = sum(1 for token in tokens if re.fullmatch(r"[A-Za-z]{3,}", token))
    compact_token_count = sum(1 for token in tokens if re.fullmatch(r"[\dA-Za-z∂πΠΣΔΩα-ωΑ-Ω]+", token))
    digit_count = sum(char.isdigit() for char in cleaned)
    source_span = (block_source_spans(record)[:1] or [{}])[0]
    bbox = source_span.get("bbox", {})
    width = float(bbox.get("width", 0.0))
    height = float(bbox.get("height", 0.0))
    if prose_token_count == 0 and compact_token_count >= max(4, len(tokens) - 1):
        if width and width <= 160.0:
            return True
        if height and height <= 8.0 and digit_count >= 6:
            return True
        if any(symbol in cleaned for symbol in ("∂", "π", "Σ", "Δ", "Ω")):
            return True
    if cleaned.count("=") >= 1 and strong_count >= 2:
        return True
    if word_count <= 24 and strong_count >= 1 and (cleaned.count(";;") >= 2 or cleaned.count("(") >= 2):
        return True
    if mathish_ratio(cleaned) >= 0.22 and strong_count >= 1:
        return True
    return False


def looks_like_leading_display_math_echo(
    text: str,
    *,
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Pattern[str],
    mathish_ratio: Callable[[str], float],
    strong_operator_count: Callable[[str], int],
) -> bool:
    cleaned = clean_text(text).lstrip(" ;:")
    if not cleaned:
        return False
    cue_match = display_math_prose_cue_re.search(cleaned)
    prefix = cleaned[: cue_match.start()].strip() if cue_match else cleaned
    if not prefix or len(prefix) > 240:
        return False
    if prefix.count("=") < 1:
        return False
    return mathish_ratio(prefix) >= 0.25 or strong_operator_count(prefix) >= 1


def mark_records_with_external_math_overlap(
    records: list[dict[str, Any]],
    external_math_overlap_by_page: dict[int, list[dict[str, Any]]],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if not external_math_overlap_by_page:
        return records

    marked: list[dict[str, Any]] = []
    for record in records:
        overlaps = overlapping_external_math_entries(
            record,
            external_math_overlap_by_page,
            block_source_spans=block_source_spans,
        )
        if not overlaps:
            marked.append(record)
            continue
        updated = dict(record)
        meta = dict(updated.get("meta", {}))
        meta["external_display_math_overlap_count"] = len(overlaps)
        updated["meta"] = meta
        marked.append(updated)
    return marked
