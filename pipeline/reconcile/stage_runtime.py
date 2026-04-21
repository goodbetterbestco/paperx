from __future__ import annotations

from typing import Any

from pipeline.reconcile.pipeline_deps import (
    ReconcileAssemblyDeps,
    ReconcileBindingDeps,
    ReconcileLoaderDeps,
    ReconcileRuntimeDeps,
    ReconcileRuntimeInputs,
)
from pipeline.reconcile.runtime_builders import build_reconcile_paper_pipeline_deps


def run_reconcile_pipeline(
    inputs: ReconcileRuntimeInputs,
    deps: ReconcileRuntimeDeps,
) -> Any:
    pipeline_deps = build_reconcile_paper_pipeline_deps(
        runtime_layout=inputs.runtime_layout,
        loaders=deps.loaders,
        bindings=deps.bindings,
        assembly=deps.assembly,
    )
    return deps.loaders.run_paper_pipeline_impl(
        inputs.paper_id,
        text_engine=inputs.text_engine,
        use_external_layout=inputs.use_external_layout,
        use_external_math=inputs.use_external_math,
        layout_output=inputs.layout_output,
        figures=inputs.figures,
        deps=pipeline_deps,
        config=inputs.config,
        state=inputs.state,
    )
