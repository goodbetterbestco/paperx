from __future__ import annotations

from typing import Any, Callable, Pattern


def math_signal_count(text: str, *, math_token_re: Pattern[str]) -> int:
    return len(math_token_re.findall(text)) + sum(text.count(token) for token in ("(", ")", "=", "<", ">", "+", "−", "-"))


def strong_operator_count(text: str) -> int:
    import re

    return sum(text.count(token) for token in ("=", "<", ">", "+", "/", "^", "_", "{", "}")) + len(
        re.findall(r"(?<![A-Za-z0-9])[-−](?![A-Za-z0-9])", text)
    )


def looks_like_math_fragment(
    record: dict[str, Any],
    *,
    record_analysis_text: Callable[[dict[str, Any]], str],
    looks_like_prose_paragraph: Callable[[str], bool],
    short_word_re: Pattern[str],
    math_token_re: Pattern[str],
) -> bool:
    if record.get("type") != "paragraph":
        return False
    text = record_analysis_text(record)
    if not text:
        return False
    if looks_like_prose_paragraph(text):
        return False
    words = short_word_re.findall(text)
    if len(words) <= 3 and len(text) <= 24:
        return True
    if math_token_re.search(text) and len(words) <= 8:
        return True
    if any(token in text for token in ("(", ")", "=", "<", ">", "+", "−", "-", "", "", "")) and len(words) <= 10:
        return True
    return False


def merge_math_fragment_records(
    records: list[dict[str, Any]],
    *,
    looks_like_math_fragment: Callable[[dict[str, Any]], bool],
    clean_text: Callable[[str], str],
    record_analysis_text: Callable[[dict[str, Any]], str],
    math_signal_count: Callable[[str], int],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    ordered = sorted(
        records,
        key=lambda record: (
            int(record.get("page", 0)),
            int(record.get("group_index", 0)),
            int(record.get("split_index", 0)),
        ),
    )
    merged: list[dict[str, Any]] = []
    index = 0

    while index < len(ordered):
        record = ordered[index]
        if not looks_like_math_fragment(record):
            merged.append(record)
            index += 1
            continue

        cluster = [record]
        next_index = index + 1
        page = int(record.get("page", 0))
        while next_index < len(ordered):
            candidate = ordered[next_index]
            if int(candidate.get("page", 0)) != page or not looks_like_math_fragment(candidate):
                break
            cluster.append(candidate)
            next_index += 1

        combined_text = clean_text(" ".join(record_analysis_text(item) for item in cluster))
        if len(cluster) >= 3 and math_signal_count(combined_text) >= 5:
            merged.append(
                {
                    "id": f"synthetic-math-{page:03d}-{int(cluster[0].get('group_index', 0)):04d}",
                    "page": page,
                    "group_index": int(cluster[0].get("group_index", 0)),
                    "split_index": 1,
                    "type": "paragraph",
                    "text": combined_text,
                    "source_spans": [span for item in cluster for span in block_source_spans(item)],
                    "meta": {
                        "forced_math_kind": "group" if len(cluster) >= 5 else "display",
                        "source_record_ids": [str(item.get("id", "")) for item in cluster],
                    },
                }
            )
            index = next_index
            continue

        merged.append(record)
        index += 1

    return merged
