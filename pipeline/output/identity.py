from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Stable logical component ids for the pipeline. These ids are intended
# to survive a later repo extraction so canonical build metadata does not go
# stale merely because files moved to a different repository.
PIPELINE_COMPONENTS: tuple[tuple[str, Path], ...] = (
    ("pipeline/reconcile_blocks.py", ROOT / "pipeline" / "reconcile" / "entrypoint.py"),
    ("pipeline/extract_math.py", ROOT / "pipeline" / "math" / "extract.py"),
    ("pipeline/normalize_prose.py", ROOT / "pipeline" / "text" / "prose.py"),
    ("pipeline/extract_figures.py", ROOT / "pipeline" / "sources" / "figures.py"),
    ("pipeline/math_review_policy.py", ROOT / "pipeline" / "math" / "review_policy.py"),
    ("pipeline/compile_formulas.py", ROOT / "pipeline" / "math" / "compile.py"),
    ("pipeline/mathml_compiler.py", ROOT / "pipeline" / "math" / "mathml.py"),
    ("pipeline/lexicon.py", ROOT / "pipeline" / "corpus" / "lexicon.py"),
    ("pipeline/formula_diagnostics.py", ROOT / "pipeline" / "math" / "diagnostics.py"),
    ("pipeline/formula_semantic_policy.py", ROOT / "pipeline" / "math" / "semantic_policy.py"),
    ("pipeline/formula_semantic_ir.py", ROOT / "pipeline" / "math" / "semantic_ir.py"),
)

# Compatibility ids for historical canonicals that fingerprinted the same
# files under the old `paper_pipeline/` package name.
LEGACY_PIPELINE_COMPONENTS: tuple[tuple[str, Path], ...] = tuple(
    (component_id.replace("pipeline/", "paper_pipeline/", 1), path)
    for component_id, path in PIPELINE_COMPONENTS
)
