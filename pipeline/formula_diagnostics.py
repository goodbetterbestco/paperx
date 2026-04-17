from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


BEGIN_ENV_RE = re.compile(r"\\begin\{([^}]+)\}")
END_ENV_RE = re.compile(r"\\end\{([^}]+)\}")
LEFT_RIGHT_RE = re.compile(r"\\(left|right)\b")
SPACED_SUBSCRIPT_RE = re.compile(r"(?<![\\A-Za-z])([A-Za-z])\s+([A-Za-z0-9])\b")
OCR_PUNCTUATION_RE = re.compile(r"(?:[:;]\s*){2,}")
DANGLING_FUNCTION_ARG_RE = re.compile(r"(?:\\[A-Za-z]+|[A-Za-z])(?:_\{[^}]+\})?\([^)]*,\)")
DANGLING_OPERATOR_START_RE = re.compile(r"^(?:=|\+|\*|/|\^|\\cdot\b)")
DANGLING_OPERATOR_END_RE = re.compile(r"(?:=|\+|\-|\*|/|\^|\\cdot\b)\s*$")
BRACED_SCRIPT_RE = re.compile(r"(?:_|\^)\{[^{}]*\}")
INTERVAL_RE = re.compile(
    r"(?:\\left)?[\[(][^][)(]{0,120},[^][)(]{0,120}(?:\\right)?[\])]"
)


@dataclass(frozen=True)
class FormulaDiagnostic:
    code: str
    severity: str
    message: str
    target: str = "entry"


def _unescaped_char(text: str, index: int) -> bool:
    return index == 0 or text[index - 1] != "\\"


def _delimiter_imbalance(text: str, open_char: str, close_char: str) -> int:
    balance = 0
    for index, char in enumerate(text):
        if not _unescaped_char(text, index):
            continue
        if char == open_char:
            balance += 1
        elif char == close_char:
            balance -= 1
            if balance < 0:
                return balance
    return balance


def _delimiter_issue(text: str) -> str | None:
    masked = INTERVAL_RE.sub(" ", text)
    issues: list[str] = []
    for open_char, close_char, label in (("{", "}", "braces"), ("(", ")", "parentheses"), ("[", "]", "brackets")):
        if _delimiter_imbalance(masked, open_char, close_char) != 0:
            issues.append(label)
    if not issues:
        return None
    return ", ".join(issues)


def _environment_issue(text: str) -> str | None:
    stack: list[str] = []
    token_re = re.compile(r"\\(?:begin|end)\{([^}]+)\}")
    for match in token_re.finditer(text):
        token = match.group(0)
        env_name = match.group(1)
        if token.startswith(r"\begin"):
            stack.append(env_name)
            continue
        if not stack:
            return f"unexpected end={env_name}"
        expected = stack.pop()
        if expected != env_name:
            return f"expected end={expected} got end={env_name}"
    if not stack:
        return None
    return f"unclosed begin={stack}"


def _left_right_issue(text: str) -> str | None:
    tokens = LEFT_RIGHT_RE.findall(text)
    left_count = sum(token == "left" for token in tokens)
    right_count = sum(token == "right" for token in tokens)
    if left_count == right_count:
        return None
    return f"left={left_count} right={right_count}"


def _spaced_subscript_issue(text: str, *, conversion_status: str) -> str | None:
    if conversion_status == "converted":
        return None
    masked = BRACED_SCRIPT_RE.sub(" ", text)
    match = SPACED_SUBSCRIPT_RE.search(masked)
    if match is None:
        return None
    return f"{match.group(1)} {match.group(2)}"


def _ocr_punctuation_issue(text: str) -> str | None:
    match = OCR_PUNCTUATION_RE.search(text)
    if match is None:
        return None
    return match.group(0)


def _dangling_function_issue(text: str) -> str | None:
    match = DANGLING_FUNCTION_ARG_RE.search(text)
    if match is None:
        return None
    return match.group(0)


def _dangling_operator_issue(text: str, *, conversion_status: str) -> str | None:
    if conversion_status == "converted":
        return None
    stripped = text.strip()
    start_match = DANGLING_OPERATOR_START_RE.search(stripped)
    if start_match is not None:
        return start_match.group(0).strip()
    end_match = DANGLING_OPERATOR_END_RE.search(stripped)
    if end_match is not None:
        return end_match.group(0).strip()
    return None


def _diagnose_formula_text(
    latex: str,
    *,
    target: str,
    conversion_status: str = "",
) -> list[FormulaDiagnostic]:
    normalized = str(latex or "").strip()
    if not normalized:
        return [FormulaDiagnostic(code="empty_formula", severity="high", message="empty display_latex", target=target)]

    diagnostics: list[FormulaDiagnostic] = []
    if conversion_status == "failed":
        diagnostics.append(
            FormulaDiagnostic(code="conversion_failed", severity="high", message="formula conversion failed", target=target)
        )

    delimiter_issue = _delimiter_issue(normalized)
    if delimiter_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="unbalanced_delimiters",
                severity="high",
                message=f"unbalanced {delimiter_issue}",
                target=target,
            )
        )

    environment_issue = _environment_issue(normalized)
    if environment_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="environment_mismatch",
                severity="high",
                message=f"environment mismatch ({environment_issue})",
                target=target,
            )
        )

    left_right_issue = _left_right_issue(normalized)
    if left_right_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="left_right_mismatch",
                severity="medium",
                message=f"\\left/\\right mismatch ({left_right_issue})",
                target=target,
            )
        )

    spaced_subscript_issue = _spaced_subscript_issue(normalized, conversion_status=conversion_status)
    if spaced_subscript_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="spaced_subscript_token",
                severity="medium",
                message=f"spaced subscript-like token `{spaced_subscript_issue}`",
                target=target,
            )
        )

    ocr_punctuation_issue = _ocr_punctuation_issue(normalized)
    if ocr_punctuation_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="ocr_punctuation_noise",
                severity="medium",
                message=f"OCR punctuation noise `{ocr_punctuation_issue}`",
                target=target,
            )
        )

    dangling_function_issue = _dangling_function_issue(normalized)
    if dangling_function_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="dangling_function_argument",
                severity="medium",
                message=f"dangling function argument `{dangling_function_issue}`",
                target=target,
            )
        )

    dangling_operator_issue = _dangling_operator_issue(normalized, conversion_status=conversion_status)
    if dangling_operator_issue:
        diagnostics.append(
            FormulaDiagnostic(
                code="dangling_operator",
                severity="medium",
                message=f"dangling operator `{dangling_operator_issue}`",
                target=target,
            )
        )

    return diagnostics


def diagnose_formula_entry(entry: dict[str, Any]) -> list[FormulaDiagnostic]:
    conversion = entry.get("conversion")
    conversion_status = ""
    if isinstance(conversion, dict):
        conversion_status = str(conversion.get("status", ""))

    diagnostics = _diagnose_formula_text(
        str(entry.get("display_latex", "")),
        target="entry",
        conversion_status=conversion_status,
    )

    if str(entry.get("kind", "")) != "group":
        return diagnostics

    for index, item in enumerate(entry.get("items", []), start=1):
        item_conversion = item.get("conversion")
        item_status = ""
        if isinstance(item_conversion, dict):
            item_status = str(item_conversion.get("status", ""))
        diagnostics.extend(
            _diagnose_formula_text(
                str(item.get("display_latex", "")),
                target=f"item {index}",
                conversion_status=item_status,
            )
        )
    return diagnostics


def summarize_formula_diagnostics(diagnostics: list[FormulaDiagnostic], *, limit: int = 3) -> str:
    parts: list[str] = []
    for diagnostic in diagnostics[:limit]:
        if diagnostic.target == "entry":
            parts.append(diagnostic.message)
            continue
        parts.append(f"{diagnostic.target}: {diagnostic.message}")
    return "; ".join(parts)
