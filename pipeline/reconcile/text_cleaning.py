from __future__ import annotations

from typing import Any, Callable


def clean_text(
    text: str,
    *,
    control_char_re: Any,
    compact_text: Callable[[str], str],
) -> str:
    return compact_text(control_char_re.sub(" ", text.replace("\u0000", " ")))


def strip_known_running_header_text(
    text: str,
    *,
    procedia_running_header_re: Any,
    clean_text: Callable[[str], str],
) -> str:
    return clean_text(procedia_running_header_re.sub(" ", text))


def clean_record(
    record: dict[str, Any],
    *,
    strip_known_running_header_text: Callable[[str], str],
) -> dict[str, Any]:
    cleaned = dict(record)
    cleaned["text"] = strip_known_running_header_text(str(record.get("text", "")))
    return cleaned


def normalize_paragraph_text(
    text: str,
    *,
    strip_known_running_header_text: Callable[[str], str],
    leading_negationslash_artifact_re: Any,
    leading_ocr_marker_re: Any,
    leading_punct_artifact_re: Any,
    leading_var_artifact_re: Any,
    trailing_numeric_artifact_re: Any,
    normalize_prose_text: Callable[[str], tuple[str, Any]],
    clean_text: Callable[[str], str],
) -> str:
    normalized = strip_known_running_header_text(text)
    if not normalized:
        return normalized
    normalized = leading_negationslash_artifact_re.sub("", normalized)
    normalized = leading_ocr_marker_re.sub("", normalized)
    normalized = leading_punct_artifact_re.sub("", normalized)
    normalized = leading_var_artifact_re.sub("", normalized)
    normalized = trailing_numeric_artifact_re.sub(".", normalized)
    normalized, _ = normalize_prose_text(normalized)
    return clean_text(normalized)


def record_analysis_text(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
) -> str:
    meta = record.get("meta", {})
    if isinstance(meta, dict):
        native_text = clean_text(str(meta.get("native_text", "")))
        if native_text:
            return native_text
    return clean_text(str(record.get("text", "")))


def word_count(text: str, *, short_word_re: Any) -> int:
    return len(short_word_re.findall(text))


def is_pdftotext_candidate_better(
    original_text: str,
    candidate_text: str,
    record_type: str,
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
) -> bool:
    original = clean_text(original_text)
    candidate = clean_text(candidate_text)
    if not candidate or candidate == original:
        return False
    if record_type in {"heading", "caption", "page_number"}:
        return False

    candidate_words = word_count(candidate)
    original_words = word_count(original)
    if candidate_words == 0:
        return False
    if record_type in {"front_matter", "paragraph", "reference", "footnote"} and candidate_words < 4:
        return False
    if "Figure " in candidate and record_type == "paragraph":
        return False
    if candidate.strip().isdigit():
        return False

    if original_words == 0:
        return True
    if candidate_words < max(3, int(original_words * 0.5)):
        return False
    if candidate_words > max(12, int(original_words * 2.25)):
        return False
    return True
