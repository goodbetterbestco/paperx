from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable, Pattern

from pipeline.types import LayoutBlock


def should_skip_pdftotext_repair(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_math_re: Pattern[str],
) -> bool:
    if record.get("type") != "paragraph":
        return False
    meta = record.get("meta", {})
    if isinstance(meta, dict) and (meta.get("forced_math_kind") or meta.get("forced_algorithm")):
        return True
    text = clean_text(str(record.get("text", "")))
    operator_count = sum(text.count(token) for token in ("=", "<", ">", "+", "-", "(", ")"))
    if text.count("=") >= 1:
        return True
    if operator_count >= 6 and word_count(text) <= 30:
        return True
    if inline_math_re.search(text):
        return True
    return False


def repair_record_text_with_pdftotext(
    records: list[dict[str, Any]],
    pdftotext_pages: dict[int, list[str]],
    page_heights: dict[int, float],
    *,
    should_skip_pdftotext_repair: Callable[[dict[str, Any]], bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    bbox_to_line_window: Callable[..., tuple[int, int]],
    slice_page_text: Callable[..., str],
    clean_text: Callable[[str], str],
    is_pdftotext_candidate_better: Callable[[str, str, str], bool],
) -> list[dict[str, Any]]:
    repaired: list[dict[str, Any]] = []
    for record in records:
        record_type = str(record.get("type", ""))
        if record_type not in {"front_matter", "paragraph", "reference", "footnote"}:
            repaired.append(record)
            continue
        if should_skip_pdftotext_repair(record):
            repaired.append(record)
            continue

        spans = block_source_spans(record)
        if not spans:
            repaired.append(record)
            continue

        slices: list[str] = []
        for span in spans:
            page = int(span.get("page", 0) or 0)
            page_lines = pdftotext_pages.get(page)
            page_height = page_heights.get(page)
            bbox = span.get("bbox", {})
            if not page_lines or not page_height or not bbox:
                continue
            start_line, end_line = bbox_to_line_window(bbox, page_height=page_height, line_count=len(page_lines))
            text = slice_page_text(page_lines, start_line=start_line, end_line=end_line)
            if text:
                slices.append(text)

        candidate_text = clean_text(" ".join(slices))
        original_text = str(record.get("text", ""))
        if not is_pdftotext_candidate_better(original_text, candidate_text, record_type):
            repaired.append(record)
            continue

        updated = dict(record)
        updated["text"] = candidate_text
        meta = dict(updated.get("meta", {}))
        meta["native_text"] = clean_text(original_text)
        meta["text_engine"] = "native_pdf+pdftotext"
        updated["meta"] = meta
        repaired.append(updated)
    return repaired


def mathpix_text_blocks_by_page(layout: dict[str, Any]) -> dict[int, list[LayoutBlock]]:
    grouped: dict[int, list[LayoutBlock]] = {}
    for block in layout.get("blocks", []):
        if str(block.role) != "paragraph":
            continue
        if str(block.meta.get("mathpix_type", "")) != "text":
            continue
        grouped.setdefault(int(block.page), []).append(block)
    for blocks in grouped.values():
        blocks.sort(key=lambda block: (float(block.bbox.get("y0", 0.0)), int(block.order), str(block.id)))
    return grouped


def record_union_bbox(
    record: dict[str, Any],
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> tuple[int, dict[str, float]] | None:
    spans = block_source_spans(record)
    if not spans:
        return None
    page = int(spans[0].get("page", record.get("page", 0)) or 0)
    page_spans = [span for span in spans if int(span.get("page", page) or page) == page]
    if not page_spans:
        return None
    x0 = min(float(span.get("bbox", {}).get("x0", 0.0)) for span in page_spans)
    y0 = min(float(span.get("bbox", {}).get("y0", 0.0)) for span in page_spans)
    x1 = max(float(span.get("bbox", {}).get("x1", 0.0)) for span in page_spans)
    y1 = max(float(span.get("bbox", {}).get("y1", 0.0)) for span in page_spans)
    return page, {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "width": max(x1 - x0, 0.0), "height": max(y1 - y0, 0.0)}


def inline_tex_signal_count(text: str) -> int:
    return (
        text.count(r"\(")
        + text.count(r"\)")
        + text.count(r"\mathbf")
        + text.count(r"\bar")
        + text.count(r"\frac")
        + text.count("_{")
        + text.count("^{")
    )


def mathpix_hint_alignment_text(
    text: str,
    *,
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Pattern[str],
    display_math_start_re: Pattern[str],
    math_signal_count: Callable[[str], int],
    word_count: Callable[[str], int],
) -> str:
    aligned = clean_text(text)
    prose_cue_match = display_math_prose_cue_re.search(aligned)
    if prose_cue_match:
        prefix = aligned[: prose_cue_match.start()]
        if prefix.lstrip().startswith((";", ":")) or (
            math_signal_count(prefix) >= 4 and word_count(prefix) <= 24
        ):
            aligned = aligned[prose_cue_match.start() :]

    display_math_match = display_math_start_re.search(aligned)
    if display_math_match:
        prefix = aligned[: display_math_match.start()].rstrip()
        suffix = aligned[display_math_match.start() :]
        if word_count(prefix) >= 6 and math_signal_count(suffix) >= 4:
            aligned = prefix
    return clean_text(aligned)


def mathpix_hint_tokens(
    text: str,
    *,
    hint_token_re: Pattern[str],
) -> list[str]:
    normalized = (
        text.replace(r"\(", " ")
        .replace(r"\)", " ")
        .replace("\\", " ")
        .replace("{", " ")
        .replace("}", " ")
    )
    return [token.lower() for token in hint_token_re.findall(normalized)]


def mathpix_text_candidate_score(
    original_text: str,
    candidate_text: str,
    *,
    mathpix_hint_alignment_text: Callable[[str], str],
    mathpix_hint_tokens: Callable[[str], list[str]],
    inline_tex_signal_count: Callable[[str], int],
) -> tuple[int, int, int, int]:
    aligned_original = mathpix_hint_alignment_text(original_text)
    original_tokens = mathpix_hint_tokens(aligned_original)
    candidate_tokens = mathpix_hint_tokens(candidate_text)
    if not original_tokens or not candidate_tokens:
        return (-10_000, -10_000, -10_000, -10_000)

    prefix_score = 0
    if candidate_tokens[0] == original_tokens[0]:
        prefix_score += 4
    elif candidate_tokens[0] in original_tokens[:4]:
        prefix_score += 1
    else:
        prefix_score -= 2
    if len(candidate_tokens) > 1 and len(original_tokens) > 1 and candidate_tokens[1] == original_tokens[1]:
        prefix_score += 1

    suffix_score = 0
    if candidate_tokens[-1] == original_tokens[-1]:
        suffix_score += 2
    elif candidate_tokens[-1] in original_tokens[-4:]:
        suffix_score += 1
    else:
        suffix_score -= 1

    shared_token_count = len(set(original_tokens) & set(candidate_tokens))
    length_delta = abs(len(candidate_tokens) - len(original_tokens))
    return (
        prefix_score + suffix_score,
        shared_token_count,
        -length_delta,
        inline_tex_signal_count(candidate_text),
    )


def matching_mathpix_text_blocks(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    *,
    record_union_bbox: Callable[[dict[str, Any]], tuple[int, dict[str, float]] | None],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
) -> list[LayoutBlock]:
    record_bounds = record_union_bbox(record)
    if record_bounds is None:
        return []
    page, record_bbox = record_bounds

    matching_blocks: list[LayoutBlock] = []
    for block in mathpix_blocks_by_page.get(page, []):
        block_bbox = dict(block.bbox)
        x_overlap_ratio = rect_x_overlap_ratio(record_bbox, block_bbox)
        block_x0 = float(block_bbox.get("x0", 0.0))
        block_x1 = float(block_bbox.get("x1", 0.0))
        block_width = float(block_bbox.get("width", max(block_x1 - block_x0, 0.0)))
        left_continuation = (
            x_overlap_ratio <= 0.0
            and block_x1 <= float(record_bbox.get("x0", 0.0))
            and float(record_bbox.get("x0", 0.0)) - block_x1 <= 8.0
            and block_width <= 24.0
        )
        if x_overlap_ratio < 0.7 and not left_continuation:
            continue
        block_y0 = float(block_bbox.get("y0", 0.0))
        block_y1 = float(block_bbox.get("y1", 0.0))
        record_y0 = float(record_bbox.get("y0", 0.0))
        record_y1 = float(record_bbox.get("y1", 0.0))
        if block_y1 < record_y0 - 6.0 or block_y0 > record_y1 + 6.0:
            continue
        matching_blocks.append(block)
    return matching_blocks


def mathpix_text_hint_candidate(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    *,
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], list[LayoutBlock]],
    word_count: Callable[[str], int],
    mathpix_hint_alignment_text: Callable[[str], str],
    clean_text: Callable[[str], str],
    mathpix_text_candidate_score: Callable[[str, str], tuple[int, int, int, int]],
) -> str:
    matching_blocks = matching_mathpix_text_blocks(record, mathpix_blocks_by_page)

    if not matching_blocks:
        return ""

    original_text = str(record.get("text", ""))
    original_words = max(word_count(mathpix_hint_alignment_text(original_text)), 1)
    best_text = ""
    best_score: tuple[int, int, int, int] | None = None

    for start in range(len(matching_blocks)):
        candidate_parts: list[str] = []
        for end in range(start, len(matching_blocks)):
            part = matching_blocks[end].text.strip()
            if not part:
                continue
            candidate_parts.append(part)
            candidate_text = clean_text(" ".join(candidate_parts))
            candidate_words = word_count(candidate_text)
            if candidate_words > max(48, int(original_words * 2.0)):
                break
            score = mathpix_text_candidate_score(original_text, candidate_text)
            if best_score is None or score > best_score:
                best_score = score
                best_text = candidate_text
    return best_text


def looks_like_truncated_prose_lead(
    text: str,
    *,
    clean_text: Callable[[str], str],
    short_word_re: Pattern[str],
    truncated_prose_lead_stopwords: set[str],
) -> bool:
    cleaned = clean_text(text)
    if not cleaned or not cleaned[:1].islower():
        return False
    words = short_word_re.findall(cleaned)
    if len(words) < 12:
        return False
    first_word = words[0].lower()
    if first_word in truncated_prose_lead_stopwords:
        return False
    return 3 <= len(first_word) <= 10 and first_word.isalpha()


def token_subsequence_index(tokens: list[str], needle: list[str]) -> int | None:
    if not tokens or not needle or len(tokens) < len(needle):
        return None
    limit = len(tokens) - len(needle) + 1
    for index in range(limit):
        if tokens[index : index + len(needle)] == needle:
            return index
    return None


def mathpix_prose_lead_repair_candidate(
    record: dict[str, Any],
    mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    *,
    clean_text: Callable[[str], str],
    looks_like_truncated_prose_lead: Callable[[str], bool],
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], list[LayoutBlock]],
    short_word_re: Pattern[str],
    word_count: Callable[[str], int],
    parse_heading_label: Callable[[str], Any],
    token_subsequence_index: Callable[[list[str], list[str]], int | None],
) -> str:
    original_text = clean_text(str(record.get("text", "")))
    if not looks_like_truncated_prose_lead(original_text):
        return ""

    matching_blocks = matching_mathpix_text_blocks(record, mathpix_blocks_by_page)
    if not matching_blocks:
        return ""

    original_tokens = [token.lower() for token in short_word_re.findall(original_text)]
    if len(original_tokens) < 12:
        return ""
    overlap_tokens = original_tokens[1 : 1 + min(8, max(len(original_tokens) - 1, 0))]
    if len(overlap_tokens) < 6:
        return ""

    best_text = ""
    best_score: tuple[int, int, int] | None = None
    original_word_count = len(original_tokens)
    for start in range(len(matching_blocks)):
        candidate_parts: list[str] = []
        for end in range(start, len(matching_blocks)):
            part = matching_blocks[end].text.strip()
            if not part:
                continue
            candidate_parts.append(part)
            candidate_text = clean_text(" ".join(candidate_parts))
            candidate_word_count = word_count(candidate_text)
            if candidate_word_count > max(64, int(original_word_count * 2.4)):
                break
            if not candidate_text or not candidate_text[:1].isupper():
                continue
            if parse_heading_label(candidate_text) is not None:
                continue
            candidate_tokens = [token.lower() for token in short_word_re.findall(candidate_text)]
            if len(candidate_tokens) <= original_word_count + 4:
                continue
            if candidate_word_count - original_word_count > 36:
                continue
            overlap_index = token_subsequence_index(candidate_tokens, overlap_tokens)
            if overlap_index is None or overlap_index <= 0 or overlap_index > 36:
                continue
            score = (overlap_index, -start, -abs(candidate_word_count - original_word_count - overlap_index))
            if best_score is None or score > best_score:
                best_score = score
                best_text = candidate_text
    return best_text


def is_mathpix_text_hint_better(original_text: str, candidate_text: str, *, clean_text: Callable[[str], str], word_count: Callable[[str], int], inline_tex_signal_count: Callable[[str], int]) -> bool:
    original = clean_text(original_text)
    candidate = clean_text(candidate_text)
    if not candidate or candidate == original:
        return False

    original_words = word_count(original)
    candidate_words = word_count(candidate)
    if candidate_words < max(4, int(original_words * 0.4)):
        return False
    if candidate_words > max(40, int(original_words * 1.75)):
        return False

    candidate_signal_count = inline_tex_signal_count(candidate)
    original_signal_count = inline_tex_signal_count(original)
    if candidate_signal_count < max(2, original_signal_count + 2):
        return False

    degraded_original = (
        ";;" in original
        or " : : :" in original
        or bool(re.search(r"\b[A-Za-z]\s+\d\b", original))
        or bool(re.search(r"\b[A-Za-z]\s*;\s*\d\b", original))
        or bool(re.search(r"\b[A-Za-z]\s+\(", original))
    )
    if not degraded_original and candidate_signal_count < original_signal_count + 3:
        return False
    return True


def repair_record_text_with_mathpix_hints(
    records: list[dict[str, Any]],
    mathpix_layout: dict[str, Any] | None,
    *,
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[LayoutBlock]]],
    is_short_ocr_fragment: Callable[[dict[str, Any]], bool],
    mathpix_text_hint_candidate: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str],
    is_mathpix_text_hint_better: Callable[[str, str], bool],
    mathpix_prose_lead_repair_candidate: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str],
    clean_text: Callable[[str], str],
) -> list[dict[str, Any]]:
    if not mathpix_layout:
        return records

    blocks_by_page = mathpix_text_blocks_by_page(mathpix_layout)
    if not blocks_by_page:
        return records

    repaired: list[dict[str, Any]] = []
    for record in records:
        if record.get("type") != "paragraph":
            repaired.append(record)
            continue
        if is_short_ocr_fragment(record):
            repaired.append(record)
            continue
        original_text = str(record.get("text", ""))
        candidate_text = mathpix_text_hint_candidate(record, blocks_by_page)
        text_engine = ""
        if is_mathpix_text_hint_better(original_text, candidate_text):
            text_engine = "mathpix_text_hint"
        else:
            candidate_text = mathpix_prose_lead_repair_candidate(record, blocks_by_page)
            if candidate_text:
                text_engine = "mathpix_prose_hint"
        if not text_engine:
            repaired.append(record)
            continue

        updated = dict(record)
        updated["text"] = candidate_text
        meta = dict(updated.get("meta", {}))
        meta["original_text"] = clean_text(original_text)
        meta["text_engine"] = text_engine
        updated["meta"] = meta
        repaired.append(updated)
    return repaired


@dataclass(frozen=True)
class BoundTextRepairHelpers:
    should_skip_pdftotext_repair: Callable[[dict[str, Any]], bool]
    repair_record_text_with_pdftotext: Callable[
        [list[dict[str, Any]], dict[int, list[str]], dict[int, float]],
        list[dict[str, Any]],
    ]
    mathpix_text_blocks_by_page: Callable[[dict[str, Any]], dict[int, list[LayoutBlock]]]
    mathpix_text_hint_candidate: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str]
    mathpix_prose_lead_repair_candidate: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str]
    is_mathpix_text_hint_better: Callable[[str, str], bool]


def make_should_skip_pdftotext_repair(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_math_re: Pattern[str],
) -> Callable[[dict[str, Any]], bool]:
    def build_should_skip_pdftotext_repair(record: dict[str, Any]) -> bool:
        return should_skip_pdftotext_repair(
            record,
            clean_text=clean_text,
            word_count=word_count,
            inline_math_re=inline_math_re,
        )

    return build_should_skip_pdftotext_repair


def make_repair_record_text_with_pdftotext(
    *,
    should_skip_pdftotext_repair: Callable[[dict[str, Any]], bool],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    bbox_to_line_window: Callable[..., tuple[int, int]],
    slice_page_text: Callable[..., str],
    clean_text: Callable[[str], str],
    is_pdftotext_candidate_better: Callable[[str, str, str], bool],
) -> Callable[[list[dict[str, Any]], dict[int, list[str]], dict[int, float]], list[dict[str, Any]]]:
    def build_repair_record_text_with_pdftotext(
        records: list[dict[str, Any]],
        pdftotext_pages: dict[int, list[str]],
        page_heights: dict[int, float],
    ) -> list[dict[str, Any]]:
        return repair_record_text_with_pdftotext(
            records,
            pdftotext_pages,
            page_heights,
            should_skip_pdftotext_repair=should_skip_pdftotext_repair,
            block_source_spans=block_source_spans,
            bbox_to_line_window=bbox_to_line_window,
            slice_page_text=slice_page_text,
            clean_text=clean_text,
            is_pdftotext_candidate_better=is_pdftotext_candidate_better,
        )

    return build_repair_record_text_with_pdftotext


def make_record_union_bbox(
    *,
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> Callable[[dict[str, Any]], tuple[int, dict[str, float]] | None]:
    def build_record_union_bbox(record: dict[str, Any]) -> tuple[int, dict[str, float]] | None:
        return record_union_bbox(
            record,
            block_source_spans=block_source_spans,
        )

    return build_record_union_bbox


def make_mathpix_hint_alignment_text(
    *,
    clean_text: Callable[[str], str],
    display_math_prose_cue_re: Pattern[str],
    display_math_start_re: Pattern[str],
    math_signal_count: Callable[[str], int],
    word_count: Callable[[str], int],
) -> Callable[[str], str]:
    def build_mathpix_hint_alignment_text(text: str) -> str:
        return mathpix_hint_alignment_text(
            text,
            clean_text=clean_text,
            display_math_prose_cue_re=display_math_prose_cue_re,
            display_math_start_re=display_math_start_re,
            math_signal_count=math_signal_count,
            word_count=word_count,
        )

    return build_mathpix_hint_alignment_text


def make_mathpix_hint_tokens(
    *,
    hint_token_re: Pattern[str],
) -> Callable[[str], list[str]]:
    def build_mathpix_hint_tokens(text: str) -> list[str]:
        return mathpix_hint_tokens(
            text,
            hint_token_re=hint_token_re,
        )

    return build_mathpix_hint_tokens


def make_mathpix_text_candidate_score(
    *,
    mathpix_hint_alignment_text: Callable[[str], str],
    mathpix_hint_tokens: Callable[[str], list[str]],
    inline_tex_signal_count: Callable[[str], int],
) -> Callable[[str, str], tuple[int, int, int, int]]:
    def build_mathpix_text_candidate_score(
        original_text: str,
        candidate_text: str,
    ) -> tuple[int, int, int, int]:
        return mathpix_text_candidate_score(
            original_text,
            candidate_text,
            mathpix_hint_alignment_text=mathpix_hint_alignment_text,
            mathpix_hint_tokens=mathpix_hint_tokens,
            inline_tex_signal_count=inline_tex_signal_count,
        )

    return build_mathpix_text_candidate_score


def make_matching_mathpix_text_blocks(
    *,
    record_union_bbox: Callable[[dict[str, Any]], tuple[int, dict[str, float]] | None],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
) -> Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], list[LayoutBlock]]:
    def build_matching_mathpix_text_blocks(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    ) -> list[LayoutBlock]:
        return matching_mathpix_text_blocks(
            record,
            mathpix_blocks_by_page,
            record_union_bbox=record_union_bbox,
            rect_x_overlap_ratio=rect_x_overlap_ratio,
        )

    return build_matching_mathpix_text_blocks


def make_mathpix_text_hint_candidate(
    *,
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], list[LayoutBlock]],
    word_count: Callable[[str], int],
    mathpix_hint_alignment_text: Callable[[str], str],
    clean_text: Callable[[str], str],
    mathpix_text_candidate_score: Callable[[str, str], tuple[int, int, int, int]],
) -> Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str]:
    def build_mathpix_text_hint_candidate(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    ) -> str:
        return mathpix_text_hint_candidate(
            record,
            mathpix_blocks_by_page,
            matching_mathpix_text_blocks=matching_mathpix_text_blocks,
            word_count=word_count,
            mathpix_hint_alignment_text=mathpix_hint_alignment_text,
            clean_text=clean_text,
            mathpix_text_candidate_score=mathpix_text_candidate_score,
        )

    return build_mathpix_text_hint_candidate


def make_looks_like_truncated_prose_lead(
    *,
    clean_text: Callable[[str], str],
    short_word_re: Pattern[str],
    truncated_prose_lead_stopwords: set[str],
) -> Callable[[str], bool]:
    def build_looks_like_truncated_prose_lead(text: str) -> bool:
        return looks_like_truncated_prose_lead(
            text,
            clean_text=clean_text,
            short_word_re=short_word_re,
            truncated_prose_lead_stopwords=truncated_prose_lead_stopwords,
        )

    return build_looks_like_truncated_prose_lead


def make_mathpix_prose_lead_repair_candidate(
    *,
    clean_text: Callable[[str], str],
    looks_like_truncated_prose_lead: Callable[[str], bool],
    matching_mathpix_text_blocks: Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], list[LayoutBlock]],
    short_word_re: Pattern[str],
    word_count: Callable[[str], int],
    parse_heading_label: Callable[[str], Any],
    token_subsequence_index: Callable[[list[str], list[str]], int | None],
) -> Callable[[dict[str, Any], dict[int, list[LayoutBlock]]], str]:
    def build_mathpix_prose_lead_repair_candidate(
        record: dict[str, Any],
        mathpix_blocks_by_page: dict[int, list[LayoutBlock]],
    ) -> str:
        return mathpix_prose_lead_repair_candidate(
            record,
            mathpix_blocks_by_page,
            clean_text=clean_text,
            looks_like_truncated_prose_lead=looks_like_truncated_prose_lead,
            matching_mathpix_text_blocks=matching_mathpix_text_blocks,
            short_word_re=short_word_re,
            word_count=word_count,
            parse_heading_label=parse_heading_label,
            token_subsequence_index=token_subsequence_index,
        )

    return build_mathpix_prose_lead_repair_candidate


def make_is_mathpix_text_hint_better(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_tex_signal_count: Callable[[str], int],
) -> Callable[[str, str], bool]:
    def build_is_mathpix_text_hint_better(original_text: str, candidate_text: str) -> bool:
        return is_mathpix_text_hint_better(
            original_text,
            candidate_text,
            clean_text=clean_text,
            word_count=word_count,
            inline_tex_signal_count=inline_tex_signal_count,
        )

    return build_is_mathpix_text_hint_better


def make_bound_text_repair_helpers(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
    inline_math_re: Pattern[str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    bbox_to_line_window: Callable[..., tuple[int, int]],
    slice_page_text: Callable[..., str],
    is_pdftotext_candidate_better: Callable[[str, str, str], bool],
    rect_x_overlap_ratio: Callable[[dict[str, Any], dict[str, Any]], float],
    display_math_prose_cue_re: Pattern[str],
    display_math_start_re: Pattern[str],
    math_signal_count: Callable[[str], int],
    hint_token_re: Pattern[str],
    short_word_re: Pattern[str],
    truncated_prose_lead_stopwords: set[str],
    parse_heading_label: Callable[[str], Any],
) -> BoundTextRepairHelpers:
    should_skip = make_should_skip_pdftotext_repair(
        clean_text=clean_text,
        word_count=word_count,
        inline_math_re=inline_math_re,
    )
    repair_pdftotext = make_repair_record_text_with_pdftotext(
        should_skip_pdftotext_repair=should_skip,
        block_source_spans=block_source_spans,
        bbox_to_line_window=bbox_to_line_window,
        slice_page_text=slice_page_text,
        clean_text=clean_text,
        is_pdftotext_candidate_better=is_pdftotext_candidate_better,
    )
    bound_record_union_bbox = make_record_union_bbox(
        block_source_spans=block_source_spans,
    )
    bound_matching_mathpix_text_blocks = make_matching_mathpix_text_blocks(
        record_union_bbox=bound_record_union_bbox,
        rect_x_overlap_ratio=rect_x_overlap_ratio,
    )
    bound_mathpix_hint_alignment_text = make_mathpix_hint_alignment_text(
        clean_text=clean_text,
        display_math_prose_cue_re=display_math_prose_cue_re,
        display_math_start_re=display_math_start_re,
        math_signal_count=math_signal_count,
        word_count=word_count,
    )
    bound_mathpix_text_candidate_score = make_mathpix_text_candidate_score(
        mathpix_hint_alignment_text=bound_mathpix_hint_alignment_text,
        mathpix_hint_tokens=make_mathpix_hint_tokens(
            hint_token_re=hint_token_re,
        ),
        inline_tex_signal_count=inline_tex_signal_count,
    )
    bound_mathpix_text_hint_candidate = make_mathpix_text_hint_candidate(
        matching_mathpix_text_blocks=bound_matching_mathpix_text_blocks,
        word_count=word_count,
        mathpix_hint_alignment_text=bound_mathpix_hint_alignment_text,
        clean_text=clean_text,
        mathpix_text_candidate_score=bound_mathpix_text_candidate_score,
    )
    bound_mathpix_prose_lead_repair_candidate = make_mathpix_prose_lead_repair_candidate(
        clean_text=clean_text,
        looks_like_truncated_prose_lead=make_looks_like_truncated_prose_lead(
            clean_text=clean_text,
            short_word_re=short_word_re,
            truncated_prose_lead_stopwords=truncated_prose_lead_stopwords,
        ),
        matching_mathpix_text_blocks=bound_matching_mathpix_text_blocks,
        short_word_re=short_word_re,
        word_count=word_count,
        parse_heading_label=parse_heading_label,
        token_subsequence_index=token_subsequence_index,
    )
    bound_is_mathpix_text_hint_better = make_is_mathpix_text_hint_better(
        clean_text=clean_text,
        word_count=word_count,
        inline_tex_signal_count=inline_tex_signal_count,
    )
    return BoundTextRepairHelpers(
        should_skip_pdftotext_repair=should_skip,
        repair_record_text_with_pdftotext=repair_pdftotext,
        mathpix_text_blocks_by_page=mathpix_text_blocks_by_page,
        mathpix_text_hint_candidate=bound_mathpix_text_hint_candidate,
        mathpix_prose_lead_repair_candidate=bound_mathpix_prose_lead_repair_candidate,
        is_mathpix_text_hint_better=bound_is_mathpix_text_hint_better,
    )


__all__ = [
    "BoundTextRepairHelpers",
    "inline_tex_signal_count",
    "is_mathpix_text_hint_better",
    "looks_like_truncated_prose_lead",
    "make_bound_text_repair_helpers",
    "make_is_mathpix_text_hint_better",
    "make_looks_like_truncated_prose_lead",
    "make_matching_mathpix_text_blocks",
    "make_mathpix_hint_alignment_text",
    "make_mathpix_hint_tokens",
    "make_mathpix_prose_lead_repair_candidate",
    "make_mathpix_text_candidate_score",
    "make_mathpix_text_hint_candidate",
    "make_record_union_bbox",
    "make_repair_record_text_with_pdftotext",
    "make_should_skip_pdftotext_repair",
    "matching_mathpix_text_blocks",
    "mathpix_hint_alignment_text",
    "mathpix_hint_tokens",
    "mathpix_prose_lead_repair_candidate",
    "mathpix_text_blocks_by_page",
    "mathpix_text_candidate_score",
    "mathpix_text_hint_candidate",
    "record_union_bbox",
    "repair_record_text_with_mathpix_hints",
    "repair_record_text_with_pdftotext",
    "should_skip_pdftotext_repair",
    "token_subsequence_index",
]
