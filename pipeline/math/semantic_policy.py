from __future__ import annotations

import re
from typing import Any

from pipeline.math.diagnostics import FormulaDiagnostic, diagnose_formula_entry
from pipeline.types import default_formula_classification


MATRIX_OR_ARRAY_RE = re.compile(
    r"\\begin\{(?:array|matrix|bmatrix|pmatrix|vmatrix|Vmatrix)\}|\\left\[|\\right\]|\\vdots|\\ldots|\\operatorname\{Diag\}|&"
)
PIECEWISE_RE = re.compile(r"\\begin\{cases\}|\\left\{")
SET_LOGIC_RE = re.compile(r"\\in\b|\\subset|\\cup|\\cap|\\forall|\\exists|\\partial\s*\\wp|\\wp\b|\\mid\b")
COMPLEXITY_OR_CLASS_RE = re.compile(r"\bO\(|C\^\{|\\mathbb\{R\}|\\Re\b|\\infty|\bNP\b")
MAPPING_RE = re.compile(r"\\phi_|\\mathbf\{F\}|\\mathbf\{M\}|[A-Za-z](?:_\{[^}]+\})?\([^)]{0,40}\)")
FIGURE_EMBEDDED_MATH_RE = re.compile(
    r"\b(?:figure|fig\.|table|chart|plot|axis|legend|pixel|screen)\b",
    re.IGNORECASE,
)
LAYOUT_FRAGMENT_RE = re.compile(r"^\s*(?:\(?\d+\)?|[:;,\-–—]+|\\tag\{[^}]+\})\s*$")
RELATION_RE = re.compile(r"(=|<|>|\\leq|\\geq|\\neq)")
DERIVATION_OPERATOR_RE = re.compile(r"\\(?:Longrightarrow|Rightarrow|Leftrightarrow|implies|iff)|\\sim\b|\\approx\b")
ITERATION_STATE_RE = re.compile(r"(?:^|[^A-Za-z])(?:q|z|s|x|u|v|p|r)_\{?k(?:[+\-][0-9]+)?\}?")
ITERATION_TRANSITION_RE = re.compile(r"(?:^|[^A-Za-z])(?:q|z|s|x|u|v|p|r)_\{?k(?:[+\-]1)\}?")
DEFINITION_ASSIGNMENT_RE = re.compile(r":=|\\coloneqq|\\triangleq|\\stackrel\{(?:def|\\mathrm\{def\})\}\{=\}")
ASSIGNMENT_RE = re.compile(r"\\gets|:=|\\coloneqq|\\triangleq")
SOLVE_RE = re.compile(r"\\text\s*\{\s*Solve|(?:^|[ ;])Solve\s*\(", re.IGNORECASE)
ITERATION_RE = re.compile(r"\biterate|iteration\b", re.IGNORECASE)
OPTIMIZATION_INLINE_RE = re.compile(r"arg\\min|arg\\max|\bsubject to\b|\bs\.t\.\b", re.IGNORECASE)
OPTIMIZATION_DISPLAY_RE = re.compile(r"(?<![_{])\\min\b|(?<![_{])\\max\b")
NON_EQUAL_RELATION_RE = re.compile(r"<|>|\\leq|\\geq|\\neq")
ARROW_TOKEN_RE = re.compile(r"\\rightarrow|\\to\b|\\mapsto|->")
OPERATION_RULE_RE = re.compile(r"O\^\{\\text\s*\{[^}]+\}\}\s*\(|\\operatorname\{(?:insert|delete|join|split|extract|copy)\}", re.IGNORECASE)


FORMULA_CATEGORIES = {
    "relation",
    "system",
    "mapping",
    "update_rule",
    "optimization",
    "set_logic",
    "complexity_or_class",
    "matrix_or_array",
    "piecewise",
    "derivation_chain",
    "symbolic_reference",
    "figure_embedded_math",
    "layout_fragment",
    "malformed_math",
    "unknown",
}
FORMULA_SEMANTIC_POLICIES = {"semantic", "structure_only", "graphic_only"}
FORMULA_CLASSIFICATION_ROLES = {
    "assertion",
    "definition",
    "condition",
    "update_step",
    "objective",
    "notation_binding",
    "derivation_step",
    "structural",
    "graphic",
    "unknown",
}
FORMULA_CLASSIFICATION_CONFIDENCE = {"low", "medium", "high"}
ROLE_POLICY = {
    "assertion": "semantic",
    "definition": "semantic",
    "condition": "semantic",
    "update_step": "semantic",
    "objective": "semantic",
    "notation_binding": "structure_only",
    "derivation_step": "structure_only",
    "structural": "structure_only",
    "graphic": "graphic_only",
    "unknown": "graphic_only",
}


def _relation_tokens(text: str) -> list[str]:
    return [match.group(0) for match in RELATION_RE.finditer(text)]


def _high_severity_diagnostics(diagnostics: list[FormulaDiagnostic]) -> list[FormulaDiagnostic]:
    return [diagnostic for diagnostic in diagnostics if diagnostic.severity == "high"]


def _has_actual_optimization(text: str, *, kind: str) -> bool:
    if OPTIMIZATION_INLINE_RE.search(text):
        return True
    if kind != "display":
        return False
    return bool(OPTIMIZATION_DISPLAY_RE.search(text))


def _definition_token_count(text: str) -> int:
    return len(DEFINITION_ASSIGNMENT_RE.findall(text))


def _looks_like_definition(text: str, *, relation_tokens: list[str]) -> bool:
    if _definition_token_count(text) == 0:
        return False
    if SOLVE_RE.search(text) or ITERATION_RE.search(text):
        return False
    if OPERATION_RULE_RE.search(text):
        return False
    if ITERATION_TRANSITION_RE.search(text):
        return False
    if ";" in text and ITERATION_STATE_RE.search(text) and len(relation_tokens) >= 2:
        return False
    return True


def _looks_like_update_rule(text: str, *, relation_tokens: list[str]) -> bool:
    if SOLVE_RE.search(text) or ITERATION_RE.search(text):
        return True
    if OPERATION_RULE_RE.search(text):
        return True
    if ASSIGNMENT_RE.search(text) and ITERATION_TRANSITION_RE.search(text):
        return True
    if ";" in text and ITERATION_STATE_RE.search(text) and len(relation_tokens) >= 2:
        return True
    if relation_tokens and ITERATION_TRANSITION_RE.search(text):
        return True
    return False


def _looks_like_derivation_step(text: str, *, relation_tokens: list[str]) -> bool:
    if DERIVATION_OPERATOR_RE.search(text):
        return True
    if len(relation_tokens) < 2:
        return False
    return all(token == "=" for token in relation_tokens) and ";" not in text


def _definition_category(text: str, *, kind: str, relation_tokens: list[str]) -> str:
    definition_count = _definition_token_count(text)
    if definition_count > 1:
        return "system"
    if ";" in text and (definition_count > 0 or len(relation_tokens) > 0):
        return "system"
    if ARROW_TOKEN_RE.search(text) or MAPPING_RE.search(text):
        return "mapping"
    if SET_LOGIC_RE.search(text):
        return "set_logic"
    if COMPLEXITY_OR_CLASS_RE.search(text):
        return "complexity_or_class"
    if len(relation_tokens) >= 2:
        return "system"
    return "relation"


def _role_for_category(
    category: str,
    *,
    kind: str,
    normalized: str,
    relation_tokens: list[str],
    is_definition: bool,
) -> str:
    if category == "derivation_chain":
        return "derivation_step"
    if category in {"matrix_or_array", "piecewise"}:
        return "structural"
    if category in {"symbolic_reference", "figure_embedded_math", "layout_fragment", "malformed_math"}:
        return "graphic"
    if is_definition:
        return "definition"
    if category == "update_rule":
        return "update_step"
    if category == "optimization":
        return "objective"
    if category == "complexity_or_class":
        if kind == "inline" or not relation_tokens:
            return "notation_binding"
        return "assertion"
    if category == "set_logic":
        if kind == "inline" and not relation_tokens:
            return "notation_binding"
        return "condition"
    if category in {"relation", "mapping", "system"} and _looks_like_derivation_step(normalized, relation_tokens=relation_tokens):
        return "derivation_step"
    if category == "relation":
        if NON_EQUAL_RELATION_RE.search(normalized):
            return "condition"
        return "assertion"
    if category == "system":
        return "condition"
    if category == "mapping":
        return "assertion"
    return "unknown"


def _classification(category: str, role: str, confidence: str, signals: list[str]) -> dict[str, Any]:
    enriched_signals = list(signals)
    if role == "notation_binding" and "notation_binding_role" not in enriched_signals:
        enriched_signals.append("notation_binding_role")
    if role == "derivation_step" and "derivation_step_role" not in enriched_signals:
        enriched_signals.append("derivation_step_role")
    return default_formula_classification(
        category=category,
        semantic_policy=ROLE_POLICY[role],
        role=role,
        confidence=confidence,
        signals=enriched_signals,
    )


def _classify_formula_text(
    latex: str,
    *,
    kind: str,
    diagnostics: list[FormulaDiagnostic],
) -> dict[str, Any]:
    normalized = str(latex or "").strip()
    relation_tokens = _relation_tokens(normalized)
    if kind == "group":
        if PIECEWISE_RE.search(normalized):
            return _classification("piecewise", "structural", "high", ["cases_environment"])
        return _classification("derivation_chain", "derivation_step", "high", ["group_kind"])

    high_diagnostics = _high_severity_diagnostics(diagnostics)
    if high_diagnostics:
        return _classification(
            "malformed_math",
            "graphic",
            "high",
            [diagnostic.code for diagnostic in high_diagnostics],
        )

    if not normalized:
        return _classification("unknown", "unknown", "low", ["empty_formula"])

    if FIGURE_EMBEDDED_MATH_RE.search(normalized):
        return _classification("figure_embedded_math", "graphic", "medium", ["figure_embedded_terms"])

    if LAYOUT_FRAGMENT_RE.match(normalized):
        return _classification("layout_fragment", "graphic", "high", ["layout_fragment_shape"])

    if MATRIX_OR_ARRAY_RE.search(normalized):
        return _classification("matrix_or_array", "structural", "high", ["matrix_or_array_shape"])

    if _has_actual_optimization(normalized, kind=kind):
        return _classification("optimization", "objective", "high", ["optimization_tokens"])

    if _looks_like_definition(normalized, relation_tokens=relation_tokens):
        category = _definition_category(normalized, kind=kind, relation_tokens=relation_tokens)
        role = _role_for_category(
            category,
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=True,
        )
        return _classification(category, role, "high", ["definition_tokens"])

    if _looks_like_update_rule(normalized, relation_tokens=relation_tokens):
        return _classification("update_rule", "update_step", "high", ["update_rule_tokens"])

    if SET_LOGIC_RE.search(normalized):
        role = _role_for_category(
            "set_logic",
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=False,
        )
        return _classification("set_logic", role, "high", ["set_logic_tokens"])

    if COMPLEXITY_OR_CLASS_RE.search(normalized):
        role = _role_for_category(
            "complexity_or_class",
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=False,
        )
        return _classification("complexity_or_class", role, "high", ["complexity_or_class_tokens"])

    if MAPPING_RE.search(normalized):
        if not relation_tokens and not ARROW_TOKEN_RE.search(normalized):
            signal = "inline_mapping_reference" if kind == "inline" else "bare_mapping_reference"
            return _classification("symbolic_reference", "graphic", "high", [signal])
        role = _role_for_category(
            "mapping",
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=False,
        )
        return _classification("mapping", role, "medium", ["mapping_tokens"])

    if len(relation_tokens) >= 2:
        role = _role_for_category(
            "system",
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=False,
        )
        return _classification("system", role, "medium", ["multiple_relations"])

    if len(relation_tokens) == 1:
        role = _role_for_category(
            "relation",
            kind=kind,
            normalized=normalized,
            relation_tokens=relation_tokens,
            is_definition=False,
        )
        return _classification("relation", role, "medium", ["single_relation"])

    if kind == "inline":
        return _classification("symbolic_reference", "graphic", "high", ["inline_symbol_reference"])

    return _classification("unknown", "unknown", "low", ["fallback_unknown"])


def _classify_formula_entry(entry: dict[str, Any]) -> dict[str, Any]:
    item = dict(entry)
    diagnostics = diagnose_formula_entry(item)
    item["classification"] = _classify_formula_text(
        str(item.get("display_latex", "")),
        kind=str(item.get("kind", "")),
        diagnostics=diagnostics,
    )

    if str(item.get("kind", "")) != "group":
        return item

    classified_items: list[dict[str, Any]] = []
    for group_item in item.get("items", []):
        next_item = dict(group_item)
        item_diagnostics = diagnose_formula_entry(
            {
                "id": item.get("id", ""),
                "kind": "display",
                "display_latex": str(next_item.get("display_latex", "")),
                "conversion": dict(next_item.get("conversion", {})),
            }
        )
        next_item["classification"] = _classify_formula_text(
            str(next_item.get("display_latex", "")),
            kind="display",
            diagnostics=item_diagnostics,
        )
        classified_items.append(next_item)
    item["items"] = classified_items
    return item


def annotate_formula_classifications(math_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_classify_formula_entry(entry) for entry in math_entries]
