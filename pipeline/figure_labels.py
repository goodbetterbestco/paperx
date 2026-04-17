from __future__ import annotations

import re


CAPTION_RE = re.compile(
    r"^(?:\([a-z]\)\s*)*(?:Figure|Fig\.?)\s*((?:[A-Za-z]?\d+(?:\.\d+)*[A-Za-z]?)|(?:[IVXLCDM]+)|(?:[A-Za-z])|&)(?:(?:\s*[:.]|\s*[—-])|\s+(?=\(|(?-i:[A-Z]))|\s*$)",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def normalize_caption_token(token: str) -> str:
    compact = re.sub(r"\s+", "", token)
    roman_values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    upper = compact.upper()

    if compact == "&":
        return "8"
    if compact in {"l", "L"}:
        return "1"
    if upper == "T":
        return "7"

    if upper and all(char in roman_values for char in upper):
        total = 0
        previous = 0
        for char in reversed(upper):
            value = roman_values[char]
            if value < previous:
                total -= value
            else:
                total += value
                previous = value
        if total > 0:
            return str(total)

    return compact


def caption_label(text: str) -> str | None:
    match = CAPTION_RE.match(normalize_text(text))
    if not match:
        return None
    return normalize_caption_token(match.group(1))
