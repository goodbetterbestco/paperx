from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Stable logical component ids for the paper pipeline. These ids are intended
# to survive a later repo extraction so canonical build metadata does not go
# stale merely because files moved to a different repository.
PIPELINE_COMPONENTS: tuple[tuple[str, Path], ...] = (
    ("paper_pipeline/reconcile_blocks.py", ROOT / "paper_pipeline" / "reconcile_blocks.py"),
    ("paper_pipeline/extract_math.py", ROOT / "paper_pipeline" / "extract_math.py"),
    ("paper_pipeline/normalize_prose.py", ROOT / "paper_pipeline" / "normalize_prose.py"),
    ("paper_pipeline/extract_figures.py", ROOT / "paper_pipeline" / "extract_figures.py"),
    ("paper_pipeline/math_review_policy.py", ROOT / "paper_pipeline" / "math_review_policy.py"),
    ("paper_pipeline/compile_formulas.py", ROOT / "paper_pipeline" / "compile_formulas.py"),
    ("paper_pipeline/mathml_compiler.py", ROOT / "paper_pipeline" / "mathml_compiler.py"),
    ("paper_pipeline/lexicon.py", ROOT / "paper_pipeline" / "lexicon.py"),
    ("paper_pipeline/formula_diagnostics.py", ROOT / "paper_pipeline" / "formula_diagnostics.py"),
    ("paper_pipeline/formula_semantic_policy.py", ROOT / "paper_pipeline" / "formula_semantic_policy.py"),
    ("paper_pipeline/formula_semantic_ir.py", ROOT / "paper_pipeline" / "formula_semantic_ir.py"),
)
