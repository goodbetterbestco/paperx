from __future__ import annotations

import re
from collections import Counter

from paper_pipeline.lexicon import corpus_join_terms

try:
    from wordfreq import zipf_frequency
except Exception:  # pragma: no cover - optional dependency for stronger OCR repair
    zipf_frequency = None


def _spaced_word_pattern(value: str) -> re.Pattern[str]:
    pieces = [re.escape(char) for char in value]
    return re.compile(rf"\b{r'\s*'.join(pieces)}\b", re.IGNORECASE)


REPLACEMENTS: list[tuple[str, re.Pattern[str], str]] = [
    ("planar_split", _spaced_word_pattern("planar"), "planar"),
    ("removal_split", _spaced_word_pattern("removal"), "removal"),
    ("algorithm_split", _spaced_word_pattern("algorithm"), "algorithm"),
    ("algorithms_split", _spaced_word_pattern("algorithms"), "algorithms"),
    ("analysis_split", _spaced_word_pattern("analysis"), "analysis"),
    ("engineering_split", _spaced_word_pattern("engineering"), "engineering"),
    ("computational_split", _spaced_word_pattern("computational"), "computational"),
    ("conventional_split", _spaced_word_pattern("conventional"), "conventional"),
    ("representation_split", _spaced_word_pattern("representation"), "representation"),
    ("representations_split", _spaced_word_pattern("representations"), "representations"),
    ("decomposition_split", _spaced_word_pattern("decomposition"), "decomposition"),
    ("diagonalizable_split", _spaced_word_pattern("diagonalizable"), "diagonalizable"),
    ("different_split", _spaced_word_pattern("different"), "different"),
    ("differentiable_split", _spaced_word_pattern("differentiable"), "differentiable"),
    ("defined_split", _spaced_word_pattern("defined"), "defined"),
    ("define_split", _spaced_word_pattern("define"), "define"),
    ("definition_split", _spaced_word_pattern("definition"), "definition"),
    ("definitions_split", _spaced_word_pattern("definitions"), "definitions"),
    ("sufficient_split", _spaced_word_pattern("sufficient"), "sufficient"),
    ("efficient_split", _spaced_word_pattern("efficient"), "efficient"),
    ("efficiently_split", _spaced_word_pattern("efficiently"), "efficiently"),
    ("configuration_split", _spaced_word_pattern("configuration"), "configuration"),
    ("floating_split", _spaced_word_pattern("floating"), "floating"),
    ("fixed_split", _spaced_word_pattern("fixed"), "fixed"),
    ("infinity_split", _spaced_word_pattern("infinity"), "infinity"),
    ("first_split", _spaced_word_pattern("first"), "first"),
    ("final_split", _spaced_word_pattern("final"), "final"),
    ("silhouette_split", _spaced_word_pattern("silhouette"), "silhouette"),
    ("silhouettes_split", _spaced_word_pattern("silhouettes"), "silhouettes"),
    ("bezier_split", _spaced_word_pattern("bezier"), "Bezier"),
    ("beziers_split", _spaced_word_pattern("beziers"), "Beziers"),
    ("differentiable_variant", re.compile(r"\bdi\s*eren\s*tiable\b", re.IGNORECASE), "differentiable"),
    ("different_variant", re.compile(r"\bdi\s*erent\b", re.IGNORECASE), "different"),
    ("determine_variant", re.compile(r"\bdeter\s*mine\b", re.IGNORECASE), "determine"),
    ("modified_variant", re.compile(r"\bmodi\s*ed\b", re.IGNORECASE), "modified"),
    ("reflexive_variant", re.compile(r"\bre\s*exive\b", re.IGNORECASE), "reflexive"),
    ("groebner_variant", re.compile(r"\bGr\s*obner\b"), "Groebner"),
    ("suffers_variant", re.compile(r"\bsu\s*ers\b", re.IGNORECASE), "suffers"),
    ("sixtyfour_variant", re.compile(r"\b6\s*4-bit\b", re.IGNORECASE), "64-bit"),
    ("intersection_split", _spaced_word_pattern("intersection"), "intersection"),
    ("intersections_split", _spaced_word_pattern("intersections"), "intersections"),
    ("refined_split", _spaced_word_pattern("refined"), "refined"),
    ("specific_split", _spaced_word_pattern("specific"), "specific"),
    ("implemented_split", _spaced_word_pattern("implemented"), "implemented"),
    ("visibility_split", _spaced_word_pattern("visibility"), "visibility"),
    ("curve_split", _spaced_word_pattern("curve"), "curve"),
    ("curves_split", _spaced_word_pattern("curves"), "curves"),
    ("milliseconds_split", _spaced_word_pattern("milliseconds"), "milliseconds"),
    ("domain_split", re.compile(r"\bdo\s*main\b", re.IGNORECASE), "domain"),
    ("suffixes_split", re.compile(r"\bsu\s*xes\b", re.IGNORECASE), "suffixes"),
    ("defined_variant", re.compile(r"\bde\s*ned\b", re.IGNORECASE), "defined"),
    ("define_variant", re.compile(r"\bde\s*ne\b", re.IGNORECASE), "define"),
    ("definition_variant", re.compile(r"\bde\s*nition\b", re.IGNORECASE), "definition"),
    ("sufficient_variant", re.compile(r"\bsu\s*cient\b", re.IGNORECASE), "sufficient"),
    ("efficient_variant", re.compile(r"\be\s*cient\b", re.IGNORECASE), "efficient"),
    ("efficiently_variant", re.compile(r"\be\s*ciently\b", re.IGNORECASE), "efficiently"),
    ("configuration_variant", re.compile(r"\bcon\s*guration\b", re.IGNORECASE), "configuration"),
    ("specific_variant", re.compile(r"\bspeci\s*c\b", re.IGNORECASE), "specific"),
    ("special_form", re.compile(r"\bspecial from of\b", re.IGNORECASE), "special form of"),
    (
        "an_initial",
        re.compile(r"\ba initial\b", re.IGNORECASE),
        lambda m: "An initial" if m.group(0)[:1].isupper() else "an initial",
    ),
    ("surface_to_surface", re.compile(r"\bsurfaceto-surface\b", re.IGNORECASE), "surface-to-surface"),
    ("curve_to_grid", re.compile(r"\bcurveto-grid\b", re.IGNORECASE), "curve-to-grid"),
    ("highprecision", re.compile(r"\bhighprecision\b", re.IGNORECASE), "high-precision"),
    ("errorprone", re.compile(r"\berrorprone\b", re.IGNORECASE), "error-prone"),
    ("abounded", re.compile(r"\babounded\b", re.IGNORECASE), "a bounded"),
    ("acad_vendor", re.compile(r"\baCAD\b"), "a CAD"),
    ("master_slave", re.compile(r"\bmaster\s*-\s*slave\b", re.IGNORECASE), "master-slave"),
    ("enhanced_by", re.compile(r"\benhance by\b", re.IGNORECASE), "enhanced by"),
    ("model_consists", re.compile(r"\bmodel consist of\b", re.IGNORECASE), "model consists of"),
    ("hardly_affects", re.compile(r"\bhardly effects\b", re.IGNORECASE), "hardly affects"),
    ("depicted", re.compile(r"\bproblem is depict\b", re.IGNORECASE), "problem is depicted"),
    ("associated_with", re.compile(r"\bis associate to\b", re.IGNORECASE), "is associated to"),
    ("curve_consists", re.compile(r"\bcurve consist of\b", re.IGNORECASE), "curve consists of"),
    (
        "in_sect",
        re.compile(r"\binSect\.", re.IGNORECASE),
        lambda m: "In Sect." if m.group(0)[:1].isupper() else "in Sect.",
    ),
    ("and_in_sect", re.compile(r"\bandinSect\.", re.IGNORECASE), "and in Sect."),
    ("divide_and_conquer", re.compile(r"\bdivide-andconquer\b", re.IGNORECASE), "divide-and-conquer"),
    ("establish_variant", re.compile(r"\bis establish\b", re.IGNORECASE), "is established"),
    ("fixed_variant", re.compile(r"\bxed\b", re.IGNORECASE), "fixed"),
    ("floating_variant", re.compile(r"\boating(?:-point)?\b", re.IGNORECASE), lambda m: "floating-point" if "-" in m.group(0) else "floating"),
    ("guarantee_variant", re.compile(r"\bguaranty\b", re.IGNORECASE), "guarantee"),
    ("coefficients_variant", re.compile(r"\bcoe\s*cients\b", re.IGNORECASE), "coefficients"),
    ("fields_variant", re.compile(r"\belds\b", re.IGNORECASE), "fields"),
    ("field_variant", re.compile(r"\beld\b", re.IGNORECASE), "field"),
    ("figure_variant", re.compile(r"\bgure\b", re.IGNORECASE), "figure"),
    ("figures_variant", re.compile(r"\bgures\b", re.IGNORECASE), "figures"),
    ("companion_variant", re.compile(r"\bcom\s*panion\b", re.IGNORECASE), "companion"),
    ("field_phrase_variant", re.compile(r"\bin or out eld\b", re.IGNORECASE), "in or out field"),
    ("point_variant", re.compile(r"\bpo\$?int\b", re.IGNORECASE), "point"),
    ("point_call_variant", re.compile(r"\bpo\$?int(?=\()",
        re.IGNORECASE), "point"),
    ("ruling_variant", re.compile(r"\brulling\b", re.IGNORECASE), "ruling"),
    ("nurbs_enhanced", re.compile(r"\bNURBSenhanced\b"), "NURBS-enhanced"),
    ("infinite_variant", re.compile(r"\bin\s*nite\b", re.IGNORECASE), "infinite"),
    ("infinity_variant", re.compile(r"\bin\s*nity\b", re.IGNORECASE), "infinity"),
    ("finite_variant", re.compile(r"\bnite\b", re.IGNORECASE), "finite"),
    ("find_variant", re.compile(r"\bnd\b", re.IGNORECASE), "find"),
    ("finding_variant", re.compile(r"\bnding\b", re.IGNORECASE), "finding"),
    ("refined_variant", re.compile(r"\bre\s*ned\b", re.IGNORECASE), "refined"),
    ("first_variant", re.compile(r"\brst\b", re.IGNORECASE), "first"),
    ("final_variant", re.compile(r"\bnal\b", re.IGNORECASE), "final"),
    ("figure_abbrev", re.compile(r"(?<![A-Za-z])g\.\s*(\d+)\b", re.IGNORECASE), r"Fig. \1"),
    ("see_figure_abbrev", re.compile(r"\bsee g\.", re.IGNORECASE), "see Fig."),
    ("sentence_algorithms", re.compile(r"(?:(?<=\.\s)|^)(algorithms to compute)\b"), "Algorithms to compute"),
    ("sentence_silhouette", re.compile(r"(?:(?<=\n)|^)(silhouette computation forms)\b"), "Silhouette computation forms"),
    ("sentence_first_of_all", re.compile(r"(?:(?<=[\.:]\s)|^)(first of all,)", re.IGNORECASE), "First of all,"),
    ("definition_label", re.compile(r"(?:(?<=\n)|^)(definition\s+\d+)\b"), lambda m: m.group(1).capitalize()),
    ("duplicate_the_interior", re.compile(r"\bthe the interior\b", re.IGNORECASE), "the interior"),
    ("duplicate_the_same", re.compile(r"\bthe the same\b", re.IGNORECASE), "the same"),
    ("jacobian_case", re.compile(r"\bjacobian\b"), "Jacobian"),
    ("face_period", re.compile(r"\bface\s+\."), "face."),
    ("complexity_semicolon", re.compile(r"complexity;;"), "complexity;"),
]

INTRAWORD_SYMBOL_RE = re.compile(r"(?<=[A-Za-z])[$](?=[A-Za-z])")
OCR_CODEPOINT_RE = re.compile(r"\bu([0-9A-Fa-f]{5,6})\b")
SPLIT_HYPHEN_WORD_RE = re.compile(r"\b([A-Za-z]{2,})-\s+([A-Za-z]{2,})\b")
JOIN_FRAGMENT_RE = re.compile(r"\b([A-Za-z]{1,8})\s+([A-Za-z]{2,12})\b")
FIGURE_NUMBER_RE = re.compile(r"\b(Figs?\.)\s+((?:\d\s+){1,3}\d)(?=(?:\([a-z]\))?\b)")
CITATION_DIGIT_RE = re.compile(r"\[([A-Za-z]{2,6})\s+((?:\d\s+){1,3}\d)\]")
STRAY_BRACE_RE = re.compile(r"\s+\}\s+(?=[.,;:])")
SPLIT_DIGIT_SEQUENCE_RE = re.compile(r"\b(?:\d\s+){1,3}\d\b")
BRACKET_CONTENT_RE = re.compile(r"\[([^\]]+)\]")
SPACE_BEFORE_PUNCTUATION_RE = re.compile(r"(?<=[A-Za-z0-9\)])\s+([.,])")
SPACE_AFTER_OPEN_DELIMITER_RE = re.compile(r"([(\[])\s+(?=[A-Za-z0-9])")
SPACE_BEFORE_CLOSE_DELIMITER_RE = re.compile(r"(?<=[A-Za-z0-9])\s+([)\]])")
HYPHEN_GAP_RE = re.compile(r"(?<=[A-Za-z0-9])(?:\s+-\s*|\s*-\s+)(?=[A-Za-z0-9])")
SKIP_JOIN_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "do",
    "for",
    "if",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "we",
}
SKIP_JOIN_RIGHT_TOKENS = {
    "sect",
    "section",
    "fig",
    "figure",
    "eq",
    "equation",
    "remark",
    "definition",
    "lemma",
    "corollary",
    "theorem",
}


def _preserve_case(template: str, replacement: str) -> str:
    if template.isupper():
        return replacement.upper()
    if template[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _repair_intraword_symbols(text: str, counts: Counter[str]) -> str:
    updated, replacement_count = INTRAWORD_SYMBOL_RE.subn("", text)
    if replacement_count:
        counts["intraword_symbol"] += replacement_count
    return updated


def _apply_replacements(text: str, counts: Counter[str]) -> str:
    updated = text
    for label, pattern, replacement in REPLACEMENTS:
        updated, replacement_count = pattern.subn(replacement, updated)
        if replacement_count:
            counts[label] += replacement_count
    return updated


def decode_ocr_codepoint_tokens(text: str) -> tuple[str, Counter[str]]:
    counts: Counter[str] = Counter()

    def replacement(match: re.Match[str]) -> str:
        codepoint = int(match.group(1), 16)
        try:
            decoded = chr(codepoint)
        except ValueError:
            return match.group(0)
        counts["ocr_codepoint_decode"] += 1
        return decoded

    return OCR_CODEPOINT_RE.sub(replacement, text), counts


def _repair_split_hyphenated_words(text: str, counts: Counter[str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        left = match.group(1)
        right = match.group(2)
        combined = left + right
        if zipf_frequency is not None and zipf_frequency(combined.lower(), "en") < 2.2:
            return match.group(0)
        counts["split_hyphen_join"] += 1
        return _preserve_case(left, combined)

    return SPLIT_HYPHEN_WORD_RE.sub(replacement, text)


def _compact_figure_numbers(text: str, counts: Counter[str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        counts["figure_number_compaction"] += 1
        return f"{match.group(1)} {re.sub(r'\s+', '', match.group(2))}"

    updated = FIGURE_NUMBER_RE.sub(replacement, text)

    def compact_split_digits(match: re.Match[str]) -> str:
        start = match.start()
        prefix = updated[max(0, start - 24) : start]
        if "Fig." not in prefix and "Figs." not in prefix and " and " not in prefix:
            return match.group(0)
        compacted = re.sub(r"\s+", "", match.group(0))
        if len(compacted) > 2:
            return match.group(0)
        counts["figure_number_compaction"] += 1
        return compacted

    return SPLIT_DIGIT_SEQUENCE_RE.sub(compact_split_digits, updated)


def _compact_citation_digits(text: str, counts: Counter[str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        counts["citation_digit_compaction"] += 1
        return f"[{match.group(1)} {re.sub(r'\s+', '', match.group(2))}]"

    return CITATION_DIGIT_RE.sub(replacement, text)


def _remove_stray_braces(text: str, counts: Counter[str]) -> str:
    updated, replacement_count = STRAY_BRACE_RE.subn(" ", text)
    if replacement_count:
        counts["stray_brace"] += replacement_count
    return updated


def _compact_bracket_citations(text: str, counts: Counter[str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        content = match.group(1)
        compacted = re.sub(r"(?<=[A-Za-z])\s+((?:\d\s+){1,3}\d)\b", lambda m: " " + re.sub(r"\s+", "", m.group(1)), content)
        if compacted != content:
            counts["bracket_citation_compaction"] += 1
        return f"[{compacted}]"

    return BRACKET_CONTENT_RE.sub(replacement, text)


def _tighten_punctuation_spacing(text: str, counts: Counter[str]) -> str:
    updated, replacement_count = SPACE_BEFORE_PUNCTUATION_RE.subn(r"\1", text)
    if replacement_count:
        counts["tighten_punctuation_spacing"] += replacement_count
    return updated


def _tighten_delimiter_spacing(text: str, counts: Counter[str]) -> str:
    updated, open_count = SPACE_AFTER_OPEN_DELIMITER_RE.subn(r"\1", text)
    if open_count:
        counts["tighten_open_delimiter_spacing"] += open_count
    updated, close_count = SPACE_BEFORE_CLOSE_DELIMITER_RE.subn(r"\1", updated)
    if close_count:
        counts["tighten_close_delimiter_spacing"] += close_count
    return updated


def _tighten_hyphen_gaps(text: str, counts: Counter[str]) -> str:
    updated, replacement_count = HYPHEN_GAP_RE.subn("-", text)
    if replacement_count:
        counts["tighten_hyphen_gap"] += replacement_count
    return updated


def _should_join_fragments(left: str, right: str) -> bool:
    if zipf_frequency is None:
        return False
    lower_left = left.lower()
    lower_right = right.lower()
    if lower_right in SKIP_JOIN_RIGHT_TOKENS:
        return False
    if right[:1].isupper() and lower_left in SKIP_JOIN_WORDS:
        return False
    if lower_left in SKIP_JOIN_WORDS and lower_right in SKIP_JOIN_WORDS:
        return False

    combined = lower_left + lower_right
    if combined in corpus_join_terms():
        return True
    combined_score = zipf_frequency(combined, "en")
    left_score = zipf_frequency(lower_left, "en")
    right_score = zipf_frequency(lower_right, "en")

    if combined_score < 2.4:
        return False
    if left_score > 4.5 and right_score > 4.5:
        return False
    if lower_left in SKIP_JOIN_WORDS and right_score > 4.0:
        return False
    if lower_right in SKIP_JOIN_WORDS and left_score > 4.0:
        return False
    return left_score <= 2.2 or right_score <= 2.2 or len(left) <= 2 or len(right) <= 2


def _join_fragmented_words(text: str, counts: Counter[str]) -> str:
    if zipf_frequency is None:
        return text

    def replacement(match: re.Match[str]) -> str:
        left = match.group(1)
        right = match.group(2)
        if not _should_join_fragments(left, right):
            return match.group(0)
        counts["frequency_join"] += 1
        return _preserve_case(left + right, left + right)

    updated = text
    for _ in range(2):
        updated = JOIN_FRAGMENT_RE.sub(replacement, updated)
    return updated


def normalize_prose_text(text: str) -> tuple[str, Counter[str]]:
    updated = text
    counts: Counter[str] = Counter()
    updated, codepoint_counts = decode_ocr_codepoint_tokens(updated)
    counts.update(codepoint_counts)
    updated = _repair_intraword_symbols(updated, counts)
    updated = _repair_split_hyphenated_words(updated, counts)
    updated = _apply_replacements(updated, counts)
    updated = _join_fragmented_words(updated, counts)
    updated = _apply_replacements(updated, counts)
    updated = _compact_figure_numbers(updated, counts)
    updated = _compact_citation_digits(updated, counts)
    updated = _compact_bracket_citations(updated, counts)
    updated = _remove_stray_braces(updated, counts)
    updated = _tighten_delimiter_spacing(updated, counts)
    updated = _tighten_hyphen_gaps(updated, counts)
    updated = _tighten_punctuation_spacing(updated, counts)
    return updated, counts
