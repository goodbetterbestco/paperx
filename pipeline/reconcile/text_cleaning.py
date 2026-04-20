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


def make_clean_text(
    *,
    control_char_re: Any,
    compact_text: Callable[[str], str],
) -> Callable[[str], str]:
    def bound_clean_text(text: str) -> str:
        return clean_text(
            text,
            control_char_re=control_char_re,
            compact_text=compact_text,
        )

    return bound_clean_text


def make_strip_known_running_header_text(
    *,
    procedia_running_header_re: Any,
    clean_text: Callable[[str], str],
) -> Callable[[str], str]:
    def bound_strip_known_running_header_text(text: str) -> str:
        return strip_known_running_header_text(
            text,
            procedia_running_header_re=procedia_running_header_re,
            clean_text=clean_text,
        )

    return bound_strip_known_running_header_text


def make_clean_record(
    *,
    strip_known_running_header_text: Callable[[str], str],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def bound_clean_record(record: dict[str, Any]) -> dict[str, Any]:
        return clean_record(
            record,
            strip_known_running_header_text=strip_known_running_header_text,
        )

    return bound_clean_record


def make_normalize_paragraph_text(
    *,
    strip_known_running_header_text: Callable[[str], str],
    leading_negationslash_artifact_re: Any,
    leading_ocr_marker_re: Any,
    leading_punct_artifact_re: Any,
    leading_var_artifact_re: Any,
    trailing_numeric_artifact_re: Any,
    normalize_prose_text: Callable[[str], tuple[str, Any]],
    clean_text: Callable[[str], str],
) -> Callable[[str], str]:
    def bound_normalize_paragraph_text(text: str) -> str:
        return normalize_paragraph_text(
            text,
            strip_known_running_header_text=strip_known_running_header_text,
            leading_negationslash_artifact_re=leading_negationslash_artifact_re,
            leading_ocr_marker_re=leading_ocr_marker_re,
            leading_punct_artifact_re=leading_punct_artifact_re,
            leading_var_artifact_re=leading_var_artifact_re,
            trailing_numeric_artifact_re=trailing_numeric_artifact_re,
            normalize_prose_text=normalize_prose_text,
            clean_text=clean_text,
        )

    return bound_normalize_paragraph_text


def make_record_analysis_text(
    *,
    clean_text: Callable[[str], str],
) -> Callable[[dict[str, Any]], str]:
    def bound_record_analysis_text(record: dict[str, Any]) -> str:
        return record_analysis_text(
            record,
            clean_text=clean_text,
        )

    return bound_record_analysis_text


def make_word_count(
    *,
    short_word_re: Any,
) -> Callable[[str], int]:
    def bound_word_count(text: str) -> int:
        return word_count(
            text,
            short_word_re=short_word_re,
        )

    return bound_word_count


def make_is_pdftotext_candidate_better(
    *,
    clean_text: Callable[[str], str],
    word_count: Callable[[str], int],
) -> Callable[[str, str, str], bool]:
    def bound_is_pdftotext_candidate_better(
        original_text: str,
        candidate_text: str,
        record_type: str,
    ) -> bool:
        return is_pdftotext_candidate_better(
            original_text,
            candidate_text,
            record_type,
            clean_text=clean_text,
            word_count=word_count,
        )

    return bound_is_pdftotext_candidate_better


__all__ = [
    "clean_record",
    "clean_text",
    "is_pdftotext_candidate_better",
    "make_clean_record",
    "make_clean_text",
    "make_is_pdftotext_candidate_better",
    "make_normalize_paragraph_text",
    "make_record_analysis_text",
    "make_strip_known_running_header_text",
    "make_word_count",
    "normalize_paragraph_text",
    "record_analysis_text",
    "strip_known_running_header_text",
    "word_count",
]
