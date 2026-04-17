from __future__ import annotations

from typing import Any

from pipeline.compile_formulas import compile_formulas
from pipeline.document_policy import apply_document_policy
from pipeline.formula_semantic_ir import annotate_formula_semantic_expr
from pipeline.formula_semantic_policy import annotate_formula_classifications
from pipeline.staleness_policy import build_metadata_for_paper


def build_canonical_document(
    *,
    paper_id: str,
    title: str,
    source: dict[str, Any],
    timestamp: str,
    layout_engine_name: str,
    math_engine_name: str,
    effective_text_engine: str,
    use_external_layout: bool,
    use_external_math: bool,
    front_matter: dict[str, Any],
    sections: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    math_entries: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    references: list[dict[str, Any]],
    decision_artifacts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    compiled_math = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(math_entries))
    )
    document = {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "title": title,
        "source": source,
        "build": build_metadata_for_paper(
            paper_id,
            pdf_path=source["pdf_path"],
            timestamp=timestamp,
            layout_engine=layout_engine_name,
            math_engine=math_engine_name,
            figure_engine="local",
            text_engine=effective_text_engine,
            use_external_layout=use_external_layout,
            use_external_math=use_external_math,
        ),
        "front_matter": front_matter,
        "styles": {
            "document_style": {},
            "category_styles": {},
            "block_styles": {},
        },
        "sections": sections,
        "blocks": blocks,
        "math": compiled_math,
        "figures": figures,
        "references": references,
    }
    if decision_artifacts:
        document["_decision_artifacts"] = decision_artifacts
    document = apply_document_policy(document)
    document["math"] = annotate_formula_semantic_expr(
        annotate_formula_classifications(compile_formulas(list(document.get("math", []))))
    )
    return document
