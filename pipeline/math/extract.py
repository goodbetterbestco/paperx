from __future__ import annotations

import re
from typing import Any

from pipeline.math.review_policy import review_for_math_entry
from pipeline.types import LayoutBlock, default_formula_conversion, default_review

INLINE_MATH_RE = re.compile(
    r"\b(?:Det|Diag|int|max|min|O|[A-Z](?:_[A-Za-z0-9]+)?)\s*\([^)]{1,40}\)"
)
INLINE_DELIMITED_TEX_RE = re.compile(r"\\\((.+?)\\\)")
INLINE_BASE_CHARS = "BCRSXJcuvw"
INLINE_ATTACHED_BASIS_RE = re.compile(r"\b([BR])([ijklstuvpqrwgcmIJ])\s*,\s*([pq])\b")
INLINE_SUPERSCRIPT_SUBSCRIPT_RE = re.compile(
    r"\b([cC])\s+(h|w)\s+([ijklstuvpqrwgcmIJ0-9]+)\b"
)
INLINE_MULTIINDEX_RE = re.compile(
    r"\b([cC])\s+([ijklstuvpqrwgcmIJ0-9]+)\s*,\s*([ijklstuvpqrwgcmIJ0-9]+)\b"
)
INLINE_SUPERSCRIPT_CALL_RE = re.compile(rf"\b([{INLINE_BASE_CHARS}])\s+(iso|h|w|r|c|u|v|g)\s*\(([^)]{{1,24}})\)")
INLINE_SUPERSCRIPT_RE = re.compile(rf"\b([{INLINE_BASE_CHARS}])\s+(iso|h|w|r|c|u|v|g)\b")
INLINE_NUMERIC_SUBSCRIPT_CALL_RE = re.compile(rf"\b([{INLINE_BASE_CHARS}])\s+([0-9]+(?:,[0-9]+)?)\s*\(([^)]{{1,24}})\)")
INLINE_SIMPLE_SUBSCRIPT_CALL_RE = re.compile(
    rf"\b([{INLINE_BASE_CHARS}])\s+([ijklstuvpqrwgcmIJ](?:\s*[+-]\s*[ijklstuvpqrwgcmpqIJ0-9])*)\s*\(([^)]{{1,24}})\)"
)
INLINE_NUMERIC_SUBSCRIPT_RE = re.compile(rf"\b([{INLINE_BASE_CHARS}])\s+([0-9]+(?:,[0-9]+)?)\b")
INLINE_SIMPLE_SUBSCRIPT_RE = re.compile(
    rf"\b([{INLINE_BASE_CHARS}])\s+([ijklstuvpqrwgcmIJ](?:\s*[+-]\s*[ijklstuvpqrwgcmpqIJ0-9])*)\b"
)
INLINE_REALSPACE_RE = re.compile(r"ℝ\s+([A-Za-z0-9]+(?:\s*[+-]\s*[A-Za-z0-9]+)*)")
INLINE_CONTINUITY_RE = re.compile(r"\bC\s+∞\b|\bC\s+([pkqmld0-9]+(?:\s*-\s*[pkqmld0-9]+)*)\b")
INLINE_FUNCTION_RELATION_RE = re.compile(r"\b([A-Za-z]\s*\([^)]{1,24}\))\s*(<=|>=|=|<|>)\s*([0-9]+(?:\.[0-9]+)?)\b")
INLINE_SUBSCRIPT_RELATION_RE = re.compile(r"\b([A-Za-z])\s+([A-Za-z0-9])\s*(<=|>=|=|<|>)\s*([0-9]+(?:\.[0-9]+)?)\b")
INLINE_RELATION_SUFFIX_RE = re.compile(r"^\s*(<=|>=|=|<|>)\s*([0-9]+(?:\.[0-9]+)?)\b")
INLINE_LABEL_NUMERIC_RE = re.compile(r"\b([A-Za-z])\s+([0-9]+)\b")
INLINE_LABEL_CONTEXT_RE = re.compile(
    r"\b(?:point|points|curve|curves|region|regions|vertex|vertices|boundary|boundaries|edge|edges|intersection|intersections|polygon|face|faces)\b",
    re.IGNORECASE,
)
SYMBOLIC_OPEN_SET_RE = re.compile(r"open set\s*;\s*@(?:\s*\})?")
SYMBOLIC_BOUNDARY_WP_RE = re.compile(r"@\s*\}")
SYMBOLIC_BOUNDARY_VAR_RE = re.compile(r"@\s*([A-Za-z])\b")
SYMBOLIC_BOUNDARY_RE = re.compile(r"(?<![A-Za-z0-9])@(?![A-Za-z0-9])")
SYMBOLIC_WP_MEMBERSHIP_RE = re.compile(r"\}\s*2\s*([A-Z])\b")
SYMBOLIC_VAR_MEMBERSHIP_RE = re.compile(r"\b([A-Za-z])\s*2\s*([A-Z])\b")
SYMBOLIC_WP_RE = re.compile(r"(?<![A-Za-z0-9])\}(?![A-Za-z0-9])")
WORD_RE = re.compile(r"[A-Za-z0-9]+")
SYMBOLIC_REGION_CONTEXT_RE = re.compile(
    r"\b(?:region|regions|visibility curve|visibility curves|boundary of|interior of|open set|corollary|lemma|partition)\b",
    re.IGNORECASE,
)
PROSE_CUE_RE = re.compile(
    r"\b(?:we|let|given|suppose|consider|therefore|however|proof|lemma|theorem|corollary|in this section|for the sake of)\b",
    re.IGNORECASE,
)
PROSE_LEAD_RE = re.compile(
    r"^\s*(?:let|given|suppose|consider|therefore|however|proof|lemma|theorem|corollary|definition|thus|where|for example|in the rest of the paper)\b",
    re.IGNORECASE,
)
PROSE_MATH_FRAGMENT_LEAD_RE = re.compile(
    r"^\s*(?:\d+\.\s*)?(?:proof\.?|remark(?:\s+\d+(?:\.\d+)*)?\.?\s+suppose that|we also assume that|assume that|suppose that|if|when|satisfy|in view of|we define|we claim|obviously|indeed|this proves|this is a|this is an|is a|then|since|thus|therefore|where|the vertex)\b",
    re.IGNORECASE,
)
DISPLAY_TRIGGER_RE = re.compile(r"(?:\\[a-zA-Z]+|[=<>]|\\tag\{|begin\{|end\{|/\\parallel|frac\{|\\mathbf\{)")
MATHISH_TOKEN_RE = re.compile(r"(?:[A-Z]\([^)]+\)|[A-Za-z]_[A-Za-z0-9]+|[xyzwstu]\s*[=<>]|[+\-*/^]|[(){}\[\]<>])")


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _math_symbol_count(text: str) -> int:
    return len(MATHISH_TOKEN_RE.findall(text))


def _looks_like_display_math(text: str) -> bool:
    words = _word_count(text)
    if words == 0:
        return False
    if DISPLAY_TRIGGER_RE.search(text) and words <= 28:
        return True
    symbol_count = _math_symbol_count(text)
    if symbol_count >= 8 and words <= 28:
        return True
    if text.count("=") >= 2 and words <= 24:
        return True
    return False


def _looks_like_prose_with_inline_math(text: str) -> bool:
    words = _word_count(text)
    if words < 18:
        return False
    if PROSE_CUE_RE.search(text):
        return True
    sentence_punct = text.count(".") + text.count(":")
    return sentence_punct >= 1 and words >= 24


def looks_like_prose_paragraph(text: str) -> bool:
    words = _word_count(text)
    if words >= 5 and PROSE_LEAD_RE.search(text):
        return True
    if words < 12:
        return False
    if _looks_like_prose_with_inline_math(text):
        return True
    comma_count = text.count(",")
    sentence_punct = text.count(".") + text.count(":")
    if words >= 8 and " because " in f" {text.lower()} ":
        return True
    return words >= 20 and (comma_count >= 1 or sentence_punct >= 1)


def looks_like_prose_math_fragment(text: str) -> bool:
    cleaned = re.sub(r"^(?:glyph\[[^\]]+\]\s*)+", "", text.strip(), flags=re.IGNORECASE)
    words = _word_count(cleaned)
    if words < 8:
        return False
    if text.count("=") > 1:
        return False
    strong_operator_count = sum(text.count(token) for token in ("<", ">", "+", "*", "/", "^"))
    if strong_operator_count >= 2:
        return False
    if PROSE_MATH_FRAGMENT_LEAD_RE.match(cleaned):
        return True
    lowered = f" {cleaned.lower()} "
    prose_cues = sum(
        token in lowered
        for token in (
            " if ",
            " then ",
            " define ",
            " claim ",
            " above ",
            " obviously ",
            " proves ",
            " boundary ",
            " disk ",
            " assume ",
            " suppose ",
            " remark ",
            " vertex ",
            " contained ",
            " linearly independent ",
            " equations ",
            " variables ",
        )
    )
    if " for all " in lowered:
        prose_cues += 1
    connective_cues = sum(
        token in lowered
        for token in (" the ", " that ", " this ", " these ", " also ", " and ", " is ", " are ", " in ", " of ", " at ")
    )
    long_prose_words = sum(
        token.isalpha() and len(token) >= 7
        for token in re.findall(r"[A-Za-z]+", cleaned.lower())
    )
    sentence_punct = cleaned.count(".") + cleaned.count(":")
    comma_count = cleaned.count(",")
    if words >= 10 and prose_cues >= 1 and connective_cues >= 4 and long_prose_words >= 1:
        return True
    return words >= 10 and prose_cues >= 2 and (sentence_punct >= 1 or comma_count >= 1)


def classify_math_block(block: LayoutBlock) -> str | None:
    text = block.text
    lowered = text.lower()
    equals_count = text.count("=")
    operator_count = sum(text.count(token) for token in ("=", "<", ">", ";", "&&", "->"))
    line_count = int(block.meta.get("line_count") or 1)
    word_count = _word_count(text)
    stripped = text.lstrip()

    if block.role in {"heading", "caption", "page_number", "front_matter", "footnote"}:
        return None

    algorithm_lead = lowered.startswith(
        (
            "if (",
            "for (",
            "while (",
            "q =",
            "v 0 =",
            "struct ",
            "typedef ",
            "algorithm ",
            "initialize ",
            "input:",
            "output:",
            "remove ",
            "construct ",
            "determine ",
            "for every ",
            "the viewing domain formed by ",
            "if the entities ",
        )
    )
    algorithm_cues = (
        "for each" in lowered
        or "output" in lowered
        or "random face" in lowered
        or "if (" in text
        or "contract_eag" in lowered
        or "eag'" in text
        or ("/*" in text and "*/" in text)
    )
    if algorithm_lead and word_count <= 80:
        return "algorithm"
    if algorithm_cues and word_count <= 120 and (operator_count >= 1 or equals_count >= 1 or text.endswith(":")):
        return "algorithm"

    if looks_like_prose_math_fragment(text):
        return None

    if _looks_like_prose_with_inline_math(text) and (word_count >= 14 or not _looks_like_display_math(text)):
        return None

    if equals_count >= 3 and len(text) > 120 and word_count <= 28:
        return "group"
    if equals_count >= 1 and (line_count >= 2 or len(text) < 140) and word_count <= 18:
        return "display"
    if operator_count >= 5 and len(text) > 180 and word_count <= 24:
        return "group"
    if _looks_like_display_math(text) and word_count <= 28:
        return "display"
    return None


def split_inline_math(text: str, start_index: int) -> tuple[list[dict[str, str]], list[dict[str, Any]], int]:
    spans: list[dict[str, str]] = []
    entries: list[dict[str, Any]] = []
    cursor = 0
    next_index = start_index

    while cursor < len(text):
        delimited_match = INLINE_DELIMITED_TEX_RE.search(text, cursor)
        plain_match = INLINE_MATH_RE.search(text, cursor)

        best_match: re.Match[str] | None = None
        delimited = False
        for candidate, is_delimited in ((delimited_match, True), (plain_match, False)):
            if candidate is None:
                continue
            if best_match is None or candidate.start() < best_match.start():
                best_match = candidate
                delimited = is_delimited

        if best_match is None:
            tail = text[cursor:]
            if tail:
                spans.append({"kind": "text", "text": tail})
            break

        if best_match.start() > cursor:
            spans.append({"kind": "text", "text": text[cursor : best_match.start()]})

        math_id = f"math-inline-{next_index}"
        if delimited:
            latex = _normalize_inline_latex(best_match.group(1).strip())
        else:
            latex = _normalize_inline_latex(best_match.group(0).replace(" ", ""))
        spans.append({"kind": "inline_math_ref", "target_id": math_id})
        entries.append(
            {
                "id": math_id,
                "kind": "inline",
                "display_latex": latex,
                "semantic_expr": None,
                "compiled_targets": {},
                "conversion": default_formula_conversion(),
                "source_spans": [],
                "alternates": [],
                "review": default_review(risk="medium"),
            }
        )
        next_index += 1
        cursor = best_match.end()

    if not spans:
        spans = [{"kind": "text", "text": text}]
    return spans, entries, next_index


def _append_inline_math(
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
    latex: str,
    next_index: int,
) -> int:
    math_id = f"math-inline-{next_index}"
    spans.append({"kind": "inline_math_ref", "target_id": math_id})
    entries.append(
        {
            "id": math_id,
            "kind": "inline",
            "display_latex": latex,
            "semantic_expr": None,
            "compiled_targets": {},
            "conversion": default_formula_conversion(),
            "source_spans": [],
            "alternates": [],
            "review": default_review(risk="medium"),
        }
    )
    return next_index + 1


def _normalize_inline_latex(latex: str) -> str:
    normalized = latex
    normalized = re.sub(r"\b([A-Za-z]+)\(\}\)", r"\1(\\wp)", normalized)
    normalized = normalized.replace(";;", ",")
    normalized = re.sub(r"(?<![A-Za-z\\])([A-Za-z])\s+([0-9]+)\b", r"\1_{\2}", normalized)
    normalized = re.sub(
        r"(?<![A-Za-z\\])([A-Za-z])\s+([ijklmnpqrstuvwxyz])(?=\s*(?:[=,)\]}]|$))",
        r"\1_{\2}",
        normalized,
    )
    normalized = re.sub(r"\s*(<=|>=|=|<|>)\s*", r"\1", normalized)
    return normalized


def _normalize_inline_arg(arg: str) -> str:
    normalized = re.sub(r"\s+", "", arg)
    normalized = normalized.replace("∞", r"\infty")
    return normalized


def _normalize_inline_index(index: str) -> str:
    normalized = re.sub(r"\s+", "", index)
    normalized = normalized.replace("∞", r"\infty")
    return normalized


def _normalize_inline_relation_lhs(lhs: str) -> str:
    cleaned = _normalize_inline_latex(lhs)
    compact = re.sub(r"\s+", "", cleaned)
    return compact


def normalize_inline_math_spans(spans: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, span in enumerate(spans):
        if span.get("kind") != "text":
            normalized.append(span)
            continue

        text = str(span.get("text", ""))
        previous_kind = spans[index - 1].get("kind") if index > 0 else None
        next_kind = spans[index + 1].get("kind") if index + 1 < len(spans) else None
        if previous_kind == "inline_math_ref" and next_kind == "inline_math_ref" and text.strip() == ";;":
            text = ", "
        normalized.append({"kind": "text", "text": text})

    if not normalized:
        return [{"kind": "text", "text": ""}]
    return normalized


def merge_inline_math_relation_suffixes(
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    entry_by_id = {str(entry.get("id", "")): entry for entry in entries}
    merged_spans: list[dict[str, str]] = []
    index = 0

    while index < len(spans):
        span = dict(spans[index])
        if span.get("kind") == "inline_math_ref" and index + 1 < len(spans):
            next_span = spans[index + 1]
            if next_span.get("kind") == "text":
                suffix_match = INLINE_RELATION_SUFFIX_RE.match(str(next_span.get("text", "")))
                if suffix_match:
                    target_id = str(span.get("target_id", ""))
                    entry = entry_by_id.get(target_id)
                    if entry is not None:
                        entry["display_latex"] = (
                            f"{_normalize_inline_latex(str(entry.get('display_latex', '')))}"
                            f"{suffix_match.group(1)}{suffix_match.group(2)}"
                        )
                        remainder = str(next_span.get("text", ""))[suffix_match.end() :]
                        merged_spans.append(span)
                        if remainder:
                            merged_spans.append({"kind": "text", "text": remainder})
                        index += 2
                        continue
        merged_spans.append(span)
        index += 1

    if not merged_spans:
        merged_spans = [{"kind": "text", "text": ""}]
    return merged_spans, entries


def _extract_general_inline_math_from_text(
    text: str,
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
    next_index: int,
) -> int:
    patterns: list[tuple[re.Pattern[str], Any]] = [
        (
            INLINE_FUNCTION_RELATION_RE,
            lambda match: f"{_normalize_inline_relation_lhs(match.group(1))}{match.group(2)}{match.group(3)}",
        ),
        (
            INLINE_SUBSCRIPT_RELATION_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}{match.group(3)}{match.group(4)}",
        ),
    ]

    if INLINE_LABEL_CONTEXT_RE.search(text):
        patterns.append(
            (
                INLINE_LABEL_NUMERIC_RE,
                lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}",
            )
        )

    patterns.extend(
        [
        (
            INLINE_ATTACHED_BASIS_RE,
            lambda match: f"{match.group(1)}_{{{match.group(2)},{match.group(3)}}}",
        ),
        (
            INLINE_SUPERSCRIPT_SUBSCRIPT_RE,
            lambda match: f"{match.group(1)}^{{{match.group(2)}}}_{{{_normalize_inline_index(match.group(3))}}}",
        ),
        (
            INLINE_MULTIINDEX_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))},{_normalize_inline_index(match.group(3))}}}",
        ),
        (
            INLINE_SUPERSCRIPT_CALL_RE,
            lambda match: f"{match.group(1)}^{{{match.group(2)}}}({_normalize_inline_arg(match.group(3))})",
        ),
        (
            INLINE_NUMERIC_SUBSCRIPT_CALL_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}({_normalize_inline_arg(match.group(3))})",
        ),
        (
            INLINE_SIMPLE_SUBSCRIPT_CALL_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}({_normalize_inline_arg(match.group(3))})",
        ),
        (
            INLINE_REALSPACE_RE,
            lambda match: rf"\mathbb{{R}}^{{{_normalize_inline_index(match.group(1))}}}",
        ),
        (
            INLINE_CONTINUITY_RE,
            lambda match: r"C^{\infty}" if match.group(0).endswith("∞") else f"C^{{{_normalize_inline_index(match.group(1))}}}",
        ),
        (
            INLINE_SUPERSCRIPT_RE,
            lambda match: f"{match.group(1)}^{{{match.group(2)}}}",
        ),
        (
            INLINE_NUMERIC_SUBSCRIPT_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}",
        ),
        (
            INLINE_SIMPLE_SUBSCRIPT_RE,
            lambda match: f"{match.group(1)}_{{{_normalize_inline_index(match.group(2))}}}",
        ),
        ]
    )

    cursor = 0
    while cursor < len(text):
        best_match: re.Match[str] | None = None
        best_builder = None
        for pattern, builder in patterns:
            match = pattern.search(text, cursor)
            if match is None:
                continue
            if best_match is None or match.start() < best_match.start():
                best_match = match
                best_builder = builder
        if best_match is None:
            tail = text[cursor:]
            if tail:
                spans.append({"kind": "text", "text": tail})
            break
        if best_match.start() > cursor:
            spans.append({"kind": "text", "text": text[cursor : best_match.start()]})
        latex = str(best_builder(best_match))
        next_index = _append_inline_math(spans, entries, latex, next_index)
        cursor = best_match.end()
    return next_index


def _looks_like_symbolic_region_context(text: str) -> bool:
    return bool(SYMBOLIC_REGION_CONTEXT_RE.search(text))


def _repair_symbolic_text_span(
    text: str,
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
    next_index: int,
) -> int:
    patterns: list[tuple[re.Pattern[str], Any]] = [
        (SYMBOLIC_OPEN_SET_RE, lambda match: "\\wp - \\partial \\wp"),
        (SYMBOLIC_BOUNDARY_WP_RE, lambda match: "\\partial \\wp"),
        (SYMBOLIC_BOUNDARY_VAR_RE, lambda match: f"\\partial {match.group(1)}"),
        (SYMBOLIC_BOUNDARY_RE, lambda match: "\\partial \\wp"),
        (SYMBOLIC_WP_MEMBERSHIP_RE, lambda match: f"\\wp \\in {match.group(1)}"),
        (SYMBOLIC_VAR_MEMBERSHIP_RE, lambda match: f"{match.group(1)} \\in {match.group(2)}"),
        (SYMBOLIC_WP_RE, lambda match: "\\wp"),
    ]

    cursor = 0
    working = text
    while cursor < len(working):
        best_match: re.Match[str] | None = None
        best_builder = None
        for pattern, builder in patterns:
            match = pattern.search(working, cursor)
            if match is None:
                continue
            if best_match is None or match.start() < best_match.start():
                best_match = match
                best_builder = builder
        if best_match is None:
            tail = working[cursor:]
            if tail:
                spans.append({"kind": "text", "text": tail})
            break
        if best_match.start() > cursor:
            spans.append({"kind": "text", "text": working[cursor : best_match.start()]})
        latex = str(best_builder(best_match))
        next_index = _append_inline_math(spans, entries, latex, next_index)
        cursor = best_match.end()
    return next_index


def repair_symbolic_ocr_spans(
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
    start_index: int,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], int]:
    combined_text = "".join(str(span.get("text", "")) for span in spans if span.get("kind") == "text")
    if not _looks_like_symbolic_region_context(combined_text):
        return spans, entries, start_index

    normalized_entries = []
    for entry in entries:
        updated = dict(entry)
        updated["display_latex"] = _normalize_inline_latex(str(entry.get("display_latex", "")))
        normalized_entries.append(updated)

    repaired_spans: list[dict[str, str]] = []
    next_index = start_index
    for span in spans:
        if span.get("kind") != "text":
            repaired_spans.append(span)
            continue
        text = str(span.get("text", ""))
        text = re.sub(r"visibility curves on,\s*$", "visibility curves on ", text)
        text = re.sub(r"interior of,\s*", "interior of ", text)
        next_index = _repair_symbolic_text_span(text, repaired_spans, normalized_entries, next_index)

    if not repaired_spans:
        repaired_spans = [{"kind": "text", "text": ""}]
    return repaired_spans, normalized_entries, next_index


def extract_general_inline_math_spans(
    spans: list[dict[str, str]],
    entries: list[dict[str, Any]],
    start_index: int,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], int]:
    normalized_entries = []
    for entry in entries:
        updated = dict(entry)
        updated["display_latex"] = _normalize_inline_latex(str(entry.get("display_latex", "")))
        normalized_entries.append(updated)

    repaired_spans: list[dict[str, str]] = []
    next_index = start_index
    for span in spans:
        if span.get("kind") != "text":
            repaired_spans.append(span)
            continue
        text = str(span.get("text", ""))
        next_index = _extract_general_inline_math_from_text(text, repaired_spans, normalized_entries, next_index)

    if not repaired_spans:
        repaired_spans = [{"kind": "text", "text": ""}]
    return repaired_spans, normalized_entries, next_index


def build_block_math_entry(block: LayoutBlock, kind: str, index: int) -> dict[str, Any]:
    math_id = f"{'eq-group' if kind == 'group' else 'eq'}-{index}"
    entry: dict[str, Any] = {
        "id": math_id,
        "kind": "group" if kind == "group" else "display",
        "display_latex": block.text,
        "semantic_expr": None,
        "compiled_targets": {},
        "conversion": default_formula_conversion(),
        "source_spans": [block.source_span().as_dict()],
        "alternates": [],
        "review": default_review(risk="medium"),
    }
    if kind == "group":
        pieces = [piece.strip() for piece in re.split(r"(?<=\))\s+(?=[A-Za-z0-9(])|(?<=0)\s+(?=\()", block.text) if piece.strip()]
        entry["items"] = [
            {
                "display_latex": piece,
                "semantic_expr": None,
                "compiled_targets": {},
                "conversion": default_formula_conversion(),
            }
            for piece in (pieces or [block.text])
        ]
    else:
        equation_number_match = re.search(r"\((\d+)\)\s*$", block.text)
        entry["equation_number"] = equation_number_match.group(0) if equation_number_match else None
    entry["review"] = review_for_math_entry(entry)
    return entry
