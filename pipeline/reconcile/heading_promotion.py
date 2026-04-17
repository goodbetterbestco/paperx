from __future__ import annotations

import re
from typing import Any, Callable, Pattern


def decode_control_heading_label(text: str) -> tuple[str | None, str]:
    raw = str(text)
    prefix: list[int] = []
    index = 0
    while index < len(raw):
        char = raw[index]
        code = ord(char)
        if char.isspace():
            index += 1
            continue
        if 1 <= code <= 9:
            prefix.append(code)
            index += 1
            continue
        break

    title = raw[index:].strip()
    if not prefix or not title:
        return None, title

    if len(prefix) >= 3 and prefix[1] == 2:
        suffix = "".join(str(code) for code in prefix[2:])
        if suffix:
            return f"{prefix[0]}.{suffix}", title

    label_parts: list[str] = []
    current = str(prefix[0])
    for code in prefix[1:]:
        if code == 2:
            if current:
                label_parts.append(current)
                current = ""
            continue
        current += str(code)
    if current:
        label_parts.append(current)
    if not label_parts:
        return None, title
    return ".".join(label_parts), title


def normalize_decoded_heading_title(
    text: str,
    *,
    clean_text: Callable[[str], str],
    clean_heading_title: Callable[[str], str],
) -> str:
    tokens = text.split()
    normalized: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token and token[0].isupper() and token.isalpha() and len(token) <= 4:
            combined = token
            next_index = index + 1
            while next_index < len(tokens):
                next_token = tokens[next_index]
                if not next_token.isalpha() or (next_token and next_token[0].isupper()) or len(combined) >= 8:
                    break
                combined += next_token
                next_index += 1
            normalized.append(combined)
            index = next_index
            continue
        normalized.append(token)
        index += 1
    return clean_text(" ".join(normalized))


def split_embedded_heading_paragraph(
    record: dict[str, Any],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    embedded_heading_prefix_re: Pattern[str],
    normalize_decoded_heading_title: Callable[[str], str],
    collapse_ocr_split_caps: Callable[[str], str],
    looks_like_bad_heading: Callable[[str], bool],
    short_word_re: Pattern[str],
) -> tuple[str, str] | None:
    if record.get("type") != "paragraph":
        return None

    source_bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
    x0 = float(source_bbox.get("x0", 999.0))
    if x0 > 120.0:
        return None

    raw_text = clean_text(str(record.get("meta", {}).get("raw_text", record.get("text", ""))))
    if not raw_text:
        return None

    match = embedded_heading_prefix_re.match(raw_text)
    if match is None:
        return None

    label = re.sub(r"\s*\.\s*", ".", match.group("label")).rstrip(".")
    rest = clean_text(match.group("rest"))
    tokens = rest.split()
    if len(tokens) < 4:
        return None

    title_connector_tokens = {
        "a", "an", "and", "as", "at", "based", "between", "by", "for", "from", "in", "into", "of", "on",
        "or", "the", "to", "under", "using", "via", "with",
    }
    sentence_start_tokens = {
        "A", "An", "After", "Assuming", "Before", "But", "Else", "For", "However", "If", "In", "Moreover",
        "Once", "Our", "Since", "The", "Then", "There", "These", "They", "This", "Thus", "To", "We", "When", "While",
    }

    title_tokens: list[str] = []
    for index, token in enumerate(tokens):
        bare = token.strip(" ,;:()[]{}")
        if not bare:
            break

        next_bare = tokens[index + 1].strip(" ,;:()[]{}") if index + 1 < len(tokens) else ""
        if index == 0 and bare in sentence_start_tokens and next_bare[:1].islower():
            return None
        if index > 0 and bare in sentence_start_tokens and next_bare[:1].islower():
            break

        bare_lower = bare.lower()
        if index > 0 and bare_lower not in title_connector_tokens and not bare[:1].isupper() and not bare.isupper():
            break

        title_tokens.append(token)
        if len(title_tokens) >= 10:
            break

    if not title_tokens:
        return None

    title = normalize_decoded_heading_title(collapse_ocr_split_caps(" ".join(title_tokens).strip(" ,;:")))
    if not title or looks_like_bad_heading(title):
        return None

    remainder_tokens = tokens[len(title_tokens) :]
    remainder = clean_text(" ".join(remainder_tokens))
    if len(short_word_re.findall(remainder)) < 4:
        return None
    if not remainder_tokens or not remainder_tokens[0][:1].isupper():
        return None

    return f"{label} {title}", remainder


def promote_heading_like_records(
    records: list[dict[str, Any]],
    *,
    clean_text: Callable[[str], str],
    block_source_spans: Callable[[dict[str, Any]], list[dict[str, Any]]],
    abstract_marker_only_re: Pattern[str],
    parse_heading_label: Callable[[str], Any],
    clean_heading_title: Callable[[str], str],
    looks_like_bad_heading: Callable[[str], bool],
    collapse_ocr_split_caps: Callable[[str], str],
    decode_control_heading_label: Callable[[str], tuple[str | None, str]],
    normalize_decoded_heading_title: Callable[[str], str],
    split_embedded_heading_paragraph: Callable[[dict[str, Any]], tuple[str, str] | None],
    short_word_re: Pattern[str],
) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for record in records:
        if record.get("type") == "paragraph":
            raw_text = clean_text(str(record.get("text", "")))
            cleaned_raw_text = clean_heading_title(raw_text)
            if abstract_marker_only_re.fullmatch(cleaned_raw_text):
                candidate = dict(record)
                candidate["type"] = "heading"
                candidate["text"] = "Abstract"
                candidate.setdefault("meta", {})
                candidate["meta"] = {
                    **candidate["meta"],
                    "synthetic_heading": True,
                    "synthetic_heading_marker_only": True,
                }
                promoted.append(candidate)
                continue
            label, title = decode_control_heading_label(raw_text)
            if not label:
                parsed_heading = parse_heading_label(cleaned_raw_text)
                if parsed_heading is not None:
                    parsed_label, parsed_title = parsed_heading
                    if not looks_like_bad_heading(parsed_title):
                        label = ".".join(parsed_label)
                        title = parsed_title
            word_count = len(short_word_re.findall(title))
            source_bbox = (block_source_spans(record)[:1] or [{}])[0].get("bbox", {})
            x0 = float(source_bbox.get("x0", 999.0))
            token_lengths = [len(token) for token in short_word_re.findall(title)]
            max_token_length = max(token_lengths) if token_lengths else 0
            if label and title and 1 <= word_count <= 8 and x0 <= 80 and max_token_length >= 4:
                normalized_title = normalize_decoded_heading_title(collapse_ocr_split_caps(title))
                candidate = dict(record)
                candidate["type"] = "heading"
                candidate["text"] = f"{label} {normalized_title}"
                candidate.setdefault("meta", {})
                candidate["meta"] = {
                    **candidate["meta"],
                    "synthetic_heading": True,
                    "decoded_label": label,
                    "decoded_title": normalized_title,
                }
                promoted.append(candidate)
                continue
            split_heading = split_embedded_heading_paragraph(record)
            if split_heading is not None:
                heading_text, remainder_text = split_heading
                heading_record = dict(record)
                heading_record["type"] = "heading"
                heading_record["text"] = heading_text
                heading_record.setdefault("meta", {})
                heading_record["meta"] = {
                    **heading_record["meta"],
                    "raw_text": heading_text,
                    "synthetic_heading": True,
                    "synthetic_heading_split": True,
                }
                promoted.append(heading_record)

                paragraph_record = dict(record)
                paragraph_record["text"] = remainder_text
                paragraph_record.setdefault("meta", {})
                paragraph_record["meta"] = {
                    **paragraph_record["meta"],
                    "raw_text": remainder_text,
                    "original_text": clean_text(str(record.get("text", ""))),
                }
                promoted.append(paragraph_record)
                continue
        promoted.append(record)
    return promoted
