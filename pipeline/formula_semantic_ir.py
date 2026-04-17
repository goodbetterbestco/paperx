from __future__ import annotations

import re
from typing import Any


IR_SCHEMA_VERSION = "formula_semantic_expr/v1"

PRESENTATION_ENV_RE = re.compile(r"\\begin\{(?:equation\*?|align\*?|aligned|gather\*?|split)\}|\\end\{(?:equation\*?|align\*?|aligned|gather\*?|split)\}")
PRESENTATION_TOKEN_RE = re.compile(r"\\(?:left|right|quad|qquad|,|;|:|!|displaystyle|textstyle|medskip|smallskip|bigskip)\b")
TAG_RE = re.compile(r"\\tag\{[^}]*\}")
TEXT_MACRO_RE = re.compile(r"\\text\s*\{([^{}]*)\}")
UNWRAP_MACRO_NAMES = (
    "mathbf",
    "mathrm",
    "mathit",
    "mathsf",
    "mathcal",
    "mathbb",
    "bar",
    "hat",
    "tilde",
    "vec",
    "overline",
    "underline",
    "operatorname",
    "textbf",
    "textrm",
    "mbox",
)
SYMBOL_TOKEN_RE = re.compile(
    r"\\[A-Za-z]+(?:_\{[^}]+\}|_[A-Za-z0-9]+)?(?:\^\{[^}]+\}|\^[A-Za-z0-9]+)?"
    r"|[A-Za-z](?:[A-Za-z0-9]*)(?:_\{[^}]+\}|_[A-Za-z0-9]+)?(?:\^\{[^}]+\}|\^[A-Za-z0-9]+)?"
)
FUNCTION_HEAD_RE = re.compile(
    r"(?P<head>(?:\\[A-Za-z]+|[A-Za-z])(?:_\{[^}]+\}|_[A-Za-z0-9]+)?)(?:\s*)\((?P<args>[^()]*)\)"
)
BIG_O_RE = re.compile(r"\bO\([^)]*\)")
CLASS_NOTATION_RE = re.compile(r"(?:C\^\{[^}]+\}|C\^[A-Za-z0-9]+|\\mathbb\{R\}(?:\^\{[^}]+\}|\^[A-Za-z0-9]+)?)")
OBJECTIVE_RE = re.compile(r"arg\\min|arg\\max|\\min\b|\\max\b")
CONSTRAINT_SPLIT_RE = re.compile(r"\b(?:subject to|s\.t\.)\b", re.IGNORECASE)
SET_OPERATOR_MAP = {
    r"\\in\b": "in",
    r"\\subseteq\b": "subseteq",
    r"\\subset\b": "subset",
    r"\\cup\b": "union",
    r"\\cap\b": "intersection",
    r"\\forall\b": "forall",
    r"\\exists\b": "exists",
}
OPERATOR_PATTERNS = (
    (re.compile(r"arg\\min"), "argmin"),
    (re.compile(r"arg\\max"), "argmax"),
    (re.compile(r"\\min\b"), "min"),
    (re.compile(r"\\max\b"), "max"),
    (re.compile(r"\\sum\b"), "sum"),
    (re.compile(r"\\prod\b"), "product"),
    (re.compile(r"\\int\b"), "integral"),
    (re.compile(r"\\forall\b"), "forall"),
    (re.compile(r"\\exists\b"), "exists"),
    (re.compile(r"\\subseteq\b"), "subseteq"),
    (re.compile(r"\\subset\b"), "subset"),
    (re.compile(r"\\in\b"), "membership"),
    (re.compile(r"\\cup\b"), "union"),
    (re.compile(r"\\cap\b"), "intersection"),
    (re.compile(r"\\leq"), "leq"),
    (re.compile(r"\\geq"), "geq"),
    (re.compile(r"\\neq"), "neq"),
    (re.compile(r"\\gets"), "assign"),
    (re.compile(r":="), "assign"),
    (re.compile(r"="), "eq"),
    (re.compile(r"<"), "lt"),
    (re.compile(r">"), "gt"),
    (re.compile(r"/"), "divide"),
    (re.compile(r"\+"), "add"),
    (re.compile(r"-"), "subtract"),
    (re.compile(r"\^"), "power"),
)
RELATION_PATTERNS = (
    (re.compile(r":="), "assign"),
    (re.compile(r"\\gets"), "assign"),
    (re.compile(r"\\leq"), "leq"),
    (re.compile(r"\\geq"), "geq"),
    (re.compile(r"\\neq"), "neq"),
    (re.compile(r"\\subseteq\b"), "subseteq"),
    (re.compile(r"\\subset\b"), "subset"),
    (re.compile(r"\\in\b"), "in"),
    (re.compile(r"="), "eq"),
    (re.compile(r"<"), "lt"),
    (re.compile(r">"), "gt"),
)
STEP_SPLIT_RE = re.compile(r"\s*;\s*")
COMMANDS_TO_IGNORE = {
    "begin",
    "end",
    "left",
    "right",
    "tag",
    "text",
    "quad",
    "qquad",
    "displaystyle",
    "textstyle",
    "frac",
    "sum",
    "prod",
    "int",
    "leq",
    "geq",
    "neq",
    "subset",
    "subseteq",
    "in",
    "cup",
    "cap",
    "forall",
    "exists",
    "min",
    "max",
    "arg",
    "cdots",
    "ldots",
    "vdots",
    "cdot",
    "times",
    "quad",
    "qquad",
    "infty",
    "solve",
    "subject",
    "to",
}


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _unwrap_latex_macros(text: str) -> str:
    normalized = text
    for macro_name in UNWRAP_MACRO_NAMES:
        pattern = re.compile(rf"\\{macro_name}\s*\{{([^{{}}]*)\}}")
        previous = None
        while previous != normalized:
            previous = normalized
            normalized = pattern.sub(r"\1", normalized)
    return normalized


def _normalize_latex_for_ir(latex: str) -> str:
    normalized = str(latex or "").strip()
    if not normalized:
        return ""
    normalized = PRESENTATION_ENV_RE.sub(" ", normalized)
    normalized = TAG_RE.sub(" ", normalized)
    normalized = TEXT_MACRO_RE.sub(r" \1 ", normalized)
    normalized = _unwrap_latex_macros(normalized)
    normalized = PRESENTATION_TOKEN_RE.sub(" ", normalized)
    normalized = normalized.replace("\\,", " ").replace("\\;", " ").replace("\\:", " ")
    normalized = normalized.replace("\\!", " ").replace("~", " ").replace("\n", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip(" ;")


def _normalize_symbol_token(token: str) -> str:
    normalized = token.strip()
    if normalized.startswith("\\"):
        normalized = normalized[1:]
    normalized = normalized.strip()
    return normalized


def _symbol_inventory(latex: str) -> list[str]:
    normalized = _normalize_latex_for_ir(latex)
    symbols: list[str] = []
    for match in SYMBOL_TOKEN_RE.finditer(normalized):
        token = _normalize_symbol_token(match.group(0))
        if not token:
            continue
        head = token.split("_", 1)[0].split("^", 1)[0]
        if head.lower() in COMMANDS_TO_IGNORE:
            continue
        symbols.append(token)
    return _ordered_unique(symbols)


def _operator_inventory(latex: str) -> list[str]:
    normalized = _normalize_latex_for_ir(latex)
    operators = [label for pattern, label in OPERATOR_PATTERNS if pattern.search(normalized)]
    return _ordered_unique(operators)


def _parse_relation(expression: str) -> dict[str, str] | None:
    normalized = expression.strip().strip(";")
    if not normalized:
        return None
    for pattern, operator in RELATION_PATTERNS:
        match = pattern.search(normalized)
        if not match:
            continue
        lhs = normalized[: match.start()].strip()
        rhs = normalized[match.end() :].strip()
        if not lhs or not rhs:
            return None
        return {
            "lhs": lhs,
            "operator": operator,
            "operator_token": match.group(0),
            "rhs": rhs,
        }
    return None


def _extract_mapping_term(expression: str) -> dict[str, Any] | None:
    match = FUNCTION_HEAD_RE.search(expression)
    if not match:
        return None
    raw_args = [arg.strip() for arg in match.group("args").split(",")]
    args = [arg for arg in raw_args if arg]
    return {
        "head": _normalize_symbol_token(match.group("head")),
        "arguments": args,
    }


def _base_ir(entry: dict[str, Any], *, category: str) -> dict[str, Any]:
    latex = str(entry.get("display_latex", ""))
    classification = entry.get("classification")
    role = None
    if isinstance(classification, dict):
        role = classification.get("role")
    return {
        "schema_version": IR_SCHEMA_VERSION,
        "category": category,
        "role": role,
        "kind": str(entry.get("kind", "")),
        "normalized_latex": _normalize_latex_for_ir(latex),
        "symbols": _symbol_inventory(latex),
        "operators": _operator_inventory(latex),
    }


def _build_relation_like_ir(entry: dict[str, Any], *, category: str) -> dict[str, Any]:
    expression = _normalize_latex_for_ir(str(entry.get("display_latex", "")))
    relation = _parse_relation(expression)
    payload = _base_ir(entry, category=category)
    if relation:
        payload["relations"] = [relation]
        mapping = _extract_mapping_term(relation["lhs"])
        if mapping is not None:
            payload["mapping"] = mapping
        return payload
    mapping = _extract_mapping_term(expression)
    if mapping is not None:
        payload["mapping"] = mapping
    return payload


def _build_update_rule_ir(entry: dict[str, Any]) -> dict[str, Any]:
    expression = _normalize_latex_for_ir(str(entry.get("display_latex", "")))
    payload = _base_ir(entry, category="update_rule")
    steps: list[dict[str, Any]] = []
    for raw_step in STEP_SPLIT_RE.split(expression):
        step_text = raw_step.strip()
        if not step_text:
            continue
        step_payload: dict[str, Any] = {"text": step_text}
        relation = _parse_relation(step_text)
        if relation is not None:
            step_payload["relation"] = relation
        leading_text = re.match(r"^(?P<action>[A-Za-z ]+)\(", step_text)
        if leading_text:
            step_payload["action"] = leading_text.group("action").strip().lower().replace(" ", "_")
        steps.append(step_payload)
    payload["steps"] = steps or [{"text": expression}]
    return payload


def _build_optimization_ir(entry: dict[str, Any]) -> dict[str, Any]:
    expression = _normalize_latex_for_ir(str(entry.get("display_latex", "")))
    payload = _base_ir(entry, category="optimization")
    objective_match = OBJECTIVE_RE.search(expression)
    constraints: list[dict[str, str]] = []
    if objective_match:
        payload["objective"] = {
            "operator": objective_match.group(0).replace("\\", ""),
            "expression": expression[objective_match.end() :].strip(),
        }
    parts = CONSTRAINT_SPLIT_RE.split(expression, maxsplit=1)
    if len(parts) == 2:
        for clause in STEP_SPLIT_RE.split(parts[1]):
            relation = _parse_relation(clause)
            if relation is not None:
                constraints.append(relation)
    if constraints:
        payload["constraints"] = constraints
    return payload


def _build_set_logic_ir(entry: dict[str, Any]) -> dict[str, Any]:
    expression = _normalize_latex_for_ir(str(entry.get("display_latex", "")))
    payload = _base_ir(entry, category="set_logic")
    predicates: list[dict[str, str]] = []
    relation = _parse_relation(expression)
    if relation is not None:
        predicates.append(relation)
    payload["set_operators"] = [label for pattern, label in ((re.compile(pattern), label) for pattern, label in SET_OPERATOR_MAP.items()) if pattern.search(expression)]
    if predicates:
        payload["predicates"] = predicates
    return payload


def _build_complexity_ir(entry: dict[str, Any]) -> dict[str, Any]:
    expression = _normalize_latex_for_ir(str(entry.get("display_latex", "")))
    payload = _base_ir(entry, category="complexity_or_class")
    notations: list[dict[str, str]] = []
    for match in BIG_O_RE.finditer(expression):
        notations.append({"kind": "big_o", "value": match.group(0)})
    for match in CLASS_NOTATION_RE.finditer(expression):
        value = match.group(0)
        notation_kind = "space_or_class"
        if value.startswith("C^"):
            notation_kind = "smoothness_class"
        notations.append({"kind": notation_kind, "value": value})
    payload["notations"] = notations or [{"kind": "notation", "value": expression}]
    return payload


def _build_semantic_expr(entry: dict[str, Any]) -> dict[str, Any] | None:
    classification = entry.get("classification")
    if not isinstance(classification, dict):
        return None
    if str(classification.get("semantic_policy", "")) != "semantic":
        return None

    category = str(classification.get("category", "unknown"))
    if category in {"relation", "system", "mapping"}:
        return _build_relation_like_ir(entry, category=category)
    if category == "update_rule":
        return _build_update_rule_ir(entry)
    if category == "optimization":
        return _build_optimization_ir(entry)
    if category == "set_logic":
        return _build_set_logic_ir(entry)
    if category == "complexity_or_class":
        return _build_complexity_ir(entry)
    return None


def annotate_formula_semantic_expr(math_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for entry in math_entries:
        item = dict(entry)
        item["semantic_expr"] = _build_semantic_expr(item)
        if str(item.get("kind", "")) == "group":
            next_items: list[dict[str, Any]] = []
            for group_item in item.get("items", []):
                next_item = dict(group_item)
                next_item["semantic_expr"] = _build_semantic_expr(next_item)
                next_items.append(next_item)
            item["items"] = next_items
        annotated.append(item)
    return annotated
