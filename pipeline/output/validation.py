from __future__ import annotations

from typing import Any


REVIEW_STATUSES = {"unreviewed", "approved", "edited", "flagged", "needs_source_check"}
REVIEW_RISKS = {"low", "medium", "high"}
FORMULA_CONVERSION_STATUSES = {"unconverted", "converted", "skipped", "failed", "partial"}
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
BLOCK_TYPES = {
    "paragraph",
    "list_item",
    "code",
    "display_equation_ref",
    "equation_group_ref",
    "figure_ref",
    "algorithm",
    "reference",
    "footnote",
    "front_matter",
}
MATH_KINDS = {"inline", "display", "group"}


class CanonicalValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CanonicalValidationError(message)


def _validate_review(review: dict[str, Any], context: str) -> None:
    _require(isinstance(review, dict), f"{context}: review must be an object")
    _require(review.get("status") in REVIEW_STATUSES, f"{context}: invalid review status")
    _require(review.get("risk") in REVIEW_RISKS, f"{context}: invalid review risk")
    _require(isinstance(review.get("notes", ""), str), f"{context}: review notes must be text")


def _validate_formula_conversion(conversion: dict[str, Any], context: str) -> None:
    _require(isinstance(conversion, dict), f"{context}: conversion must be an object")
    _require(conversion.get("status") in FORMULA_CONVERSION_STATUSES, f"{context}: invalid conversion status")
    _require(isinstance(conversion.get("notes", ""), str), f"{context}: conversion notes must be text")


def _validate_formula_classification(classification: dict[str, Any], context: str) -> None:
    _require(isinstance(classification, dict), f"{context}: classification must be an object")
    _require(classification.get("category") in FORMULA_CATEGORIES, f"{context}: invalid formula category")
    _require(
        classification.get("semantic_policy") in FORMULA_SEMANTIC_POLICIES,
        f"{context}: invalid semantic policy",
    )
    _require(
        classification.get("role") in FORMULA_CLASSIFICATION_ROLES,
        f"{context}: invalid semantic role",
    )
    _require(
        classification.get("confidence") in FORMULA_CLASSIFICATION_CONFIDENCE,
        f"{context}: invalid formula classification confidence",
    )
    signals = classification.get("signals", [])
    _require(isinstance(signals, list), f"{context}: classification signals must be a list")
    _require(all(isinstance(signal, str) for signal in signals), f"{context}: classification signals must be text")


def validate_build(document: dict[str, Any]) -> None:
    build = document["build"]
    _require(isinstance(build, dict), "build must be an object")
    for key in ("created_at", "updated_at", "builder_version", "sources"):
        _require(key in build, f"build missing key: {key}")
    _require(isinstance(build.get("created_at"), str), "build.created_at must be text")
    _require(isinstance(build.get("updated_at"), str), "build.updated_at must be text")
    _require(isinstance(build.get("builder_version"), str), "build.builder_version must be text")
    _require(isinstance(build.get("sources"), dict), "build.sources must be an object")

    for key in ("native_pdf", "layout_engine", "math_engine", "figure_engine"):
        _require(key in build["sources"], f"build.sources missing key: {key}")
    _require(isinstance(build["sources"].get("native_pdf"), bool), "build.sources.native_pdf must be boolean")
    for key in ("layout_engine", "math_engine", "figure_engine"):
        _require(isinstance(build["sources"].get(key), str), f"build.sources.{key} must be text")

    if "inputs" in build:
        inputs = build["inputs"]
        _require(isinstance(inputs, dict), "build.inputs must be an object")
        for key, fingerprint in inputs.items():
            _require(isinstance(key, str), "build.inputs keys must be text")
            _require(isinstance(fingerprint, dict), f"build.inputs.{key} must be an object")
            _require(isinstance(fingerprint.get("path"), str), f"build.inputs.{key}.path must be text")
            _require(isinstance(fingerprint.get("exists"), bool), f"build.inputs.{key}.exists must be boolean")
            if fingerprint.get("exists"):
                _require(isinstance(fingerprint.get("sha256"), str), f"build.inputs.{key}.sha256 must be text")
                _require(isinstance(fingerprint.get("size_bytes"), int), f"build.inputs.{key}.size_bytes must be integer")
                _require(isinstance(fingerprint.get("modified_at"), str), f"build.inputs.{key}.modified_at must be text")

    if "pipeline" in build:
        pipeline = build["pipeline"]
        _require(isinstance(pipeline, dict), "build.pipeline must be an object")
        _require(isinstance(pipeline.get("builder_version"), str), "build.pipeline.builder_version must be text")
        _require(isinstance(pipeline.get("fingerprint"), str), "build.pipeline.fingerprint must be text")
        modules = pipeline.get("modules")
        _require(isinstance(modules, dict), "build.pipeline.modules must be an object")
        _require(
            all(isinstance(path, str) and isinstance(value, str) for path, value in modules.items()),
            "build.pipeline.modules entries must be text",
        )


def validate_top_level(document: dict[str, Any]) -> None:
    for key in ("schema_version", "paper_id", "paper_uid", "title", "source", "build", "front_matter", "sections", "blocks", "math", "figures", "references", "styles"):
        _require(key in document, f"missing top-level key: {key}")
    _require(isinstance(document.get("paper_uid"), str) and document["paper_uid"], "paper_uid must be non-empty text")


def validate_styles(document: dict[str, Any]) -> None:
    styles = document["styles"]
    _require(isinstance(styles, dict), "styles must be an object")
    for key in ("document_style", "category_styles", "block_styles"):
        _require(key in styles, f"styles missing key: {key}")
        _require(isinstance(styles[key], dict), f"styles.{key} must be an object")


def validate_sections(document: dict[str, Any]) -> None:
    sections = document["sections"]
    _require(isinstance(sections, list), "sections must be a list")
    section_ids = {section["id"] for section in sections}
    for section in sections:
        _require(isinstance(section.get("id"), str) and section["id"], "section id missing")
        _require(isinstance(section.get("title"), str), f"section {section['id']}: title missing")
        _require(isinstance(section.get("level"), int), f"section {section['id']}: level missing")
        _require(isinstance(section.get("block_ids"), list), f"section {section['id']}: block_ids must be a list")
        _require(isinstance(section.get("children"), list), f"section {section['id']}: children must be a list")
        for child_id in section["children"]:
            _require(child_id in section_ids, f"section {section['id']}: unknown child section {child_id}")


def validate_blocks(document: dict[str, Any]) -> None:
    blocks = document["blocks"]
    _require(isinstance(blocks, list), "blocks must be a list")
    ids = set()
    math_ids = {entry["id"] for entry in document["math"]}
    figure_ids = {entry["id"] for entry in document["figures"]}
    reference_ids = {entry["id"] for entry in document["references"]}

    for block in blocks:
        block_id = block.get("id")
        _require(isinstance(block_id, str) and block_id, "block id missing")
        _require(block_id not in ids, f"duplicate block id: {block_id}")
        ids.add(block_id)
        _require(block.get("type") in BLOCK_TYPES, f"block {block_id}: invalid type {block.get('type')}")
        _require(isinstance(block.get("content"), dict), f"block {block_id}: content must be an object")
        _require(isinstance(block.get("source_spans"), list), f"block {block_id}: source_spans must be a list")
        _validate_review(block.get("review", {}), f"block {block_id}")

        if block["type"] in {"paragraph", "list_item"}:
            spans = block["content"].get("spans")
            _require(isinstance(spans, list), f"block {block_id}: spans missing")
            for span in spans:
                kind = span.get("kind")
                _require(kind in {"text", "inline_math_ref", "citation_ref"}, f"block {block_id}: invalid span kind {kind}")
                if kind == "inline_math_ref":
                    _require(span.get("target_id") in math_ids, f"block {block_id}: unknown inline math ref {span.get('target_id')}")
                if kind == "citation_ref":
                    _require(span.get("target_id") in reference_ids, f"block {block_id}: unknown citation ref {span.get('target_id')}")
            if block["type"] == "list_item":
                marker = block["content"].get("marker")
                ordered = block["content"].get("ordered")
                depth = block["content"].get("depth", 1)
                _require(marker is None or isinstance(marker, str), f"block {block_id}: marker must be text or null")
                _require(isinstance(ordered, bool), f"block {block_id}: ordered must be boolean")
                _require(isinstance(depth, int) and depth >= 1, f"block {block_id}: depth must be positive integer")

        if block["type"] == "code":
            lines = block["content"].get("lines")
            language = block["content"].get("language", "text")
            _require(isinstance(lines, list) and all(isinstance(line, str) for line in lines), f"block {block_id}: code lines missing")
            _require(isinstance(language, str), f"block {block_id}: code language must be text")

        if block["type"] in {"display_equation_ref", "equation_group_ref"}:
            _require(block["content"].get("math_id") in math_ids, f"block {block_id}: unknown math ref")
        if block["type"] == "figure_ref":
            _require(block["content"].get("figure_id") in figure_ids, f"block {block_id}: unknown figure ref")
        if block["type"] == "reference":
            _require(block["content"].get("reference_id") in reference_ids, f"block {block_id}: unknown reference ref")

    section_block_ids = {block_id for section in document["sections"] for block_id in section["block_ids"]}
    for block_id in section_block_ids:
        _require(block_id in ids, f"section references unknown block {block_id}")


def validate_math(document: dict[str, Any]) -> None:
    seen: set[str] = set()
    for entry in document["math"]:
        math_id = entry.get("id")
        _require(isinstance(math_id, str) and math_id, "math id missing")
        _require(math_id not in seen, f"duplicate math id: {math_id}")
        seen.add(math_id)
        _require(entry.get("kind") in MATH_KINDS, f"math {math_id}: invalid kind")
        _require(isinstance(entry.get("display_latex"), str), f"math {math_id}: display_latex missing")
        _require(entry.get("semantic_expr") is None or isinstance(entry.get("semantic_expr"), dict), f"math {math_id}: semantic_expr must be object or null")
        _require(isinstance(entry.get("compiled_targets"), dict), f"math {math_id}: compiled_targets must be object")
        _validate_formula_conversion(entry.get("conversion", {}), f"math {math_id}")
        if entry.get("classification") is not None:
            _validate_formula_classification(entry.get("classification", {}), f"math {math_id}")
        _require(isinstance(entry.get("source_spans"), list), f"math {math_id}: source_spans must be list")
        _validate_review(entry.get("review", {}), f"math {math_id}")
        if entry["kind"] == "group":
            items = entry.get("items")
            _require(isinstance(items, list) and items, f"math {math_id}: group items missing")
            for item in items:
                _require(isinstance(item.get("display_latex"), str), f"math {math_id}: group item latex missing")
                _require(item.get("semantic_expr") is None or isinstance(item.get("semantic_expr"), dict), f"math {math_id}: group item semantic_expr must be object or null")
                _require(isinstance(item.get("compiled_targets"), dict), f"math {math_id}: group item compiled_targets missing")
                _validate_formula_conversion(item.get("conversion", {}), f"math {math_id}: group item")
                if item.get("classification") is not None:
                    _validate_formula_classification(item.get("classification", {}), f"math {math_id}: group item")


def validate_figures(document: dict[str, Any]) -> None:
    seen: set[str] = set()
    for figure in document["figures"]:
        figure_id = figure.get("id")
        _require(isinstance(figure_id, str) and figure_id, "figure id missing")
        _require(figure_id not in seen, f"duplicate figure id: {figure_id}")
        seen.add(figure_id)
        _require(isinstance(figure.get("image_path"), str) and figure["image_path"], f"figure {figure_id}: image_path missing")
        _require(isinstance(figure.get("bbox"), dict), f"figure {figure_id}: bbox missing")
        _require(isinstance(figure.get("display_size_in"), dict), f"figure {figure_id}: display_size_in missing")
        _validate_review(figure.get("review", {}), f"figure {figure_id}")


def validate_references(document: dict[str, Any]) -> None:
    seen: set[str] = set()
    for reference in document["references"]:
        ref_id = reference.get("id")
        _require(isinstance(ref_id, str) and ref_id, "reference id missing")
        _require(ref_id not in seen, f"duplicate reference id: {ref_id}")
        seen.add(ref_id)
        _require(isinstance(reference.get("raw_text"), str), f"reference {ref_id}: raw_text missing")
        _require(isinstance(reference.get("text"), str), f"reference {ref_id}: text missing")
        _validate_review(reference.get("review", {}), f"reference {ref_id}")


def validate_canonical(document: dict[str, Any]) -> None:
    validate_top_level(document)
    validate_build(document)
    validate_styles(document)
    validate_sections(document)
    validate_math(document)
    validate_figures(document)
    validate_references(document)
    validate_blocks(document)
