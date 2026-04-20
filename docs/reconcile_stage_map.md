# Reconcile Stage Map

This note is the Track 3.1 stage map for the current reconcile flow in
`paperx`.

The important high-level shape is:

- `pipeline.reconcile.entrypoint` owns the static import fan-in and the
  initial helper bundle construction.
- `pipeline.reconcile.runtime_deps` builds frozen dependency bundles for the
  loader, binding, and assembly surfaces.
- `pipeline.reconcile.runtime_builders` binds those bundles into the keyword
  arguments expected by `pipeline.orchestrator.paper_reconciler.run_paper_pipeline`.
- The actual logical stages are then executed inside the orchestrator modules,
  with the final document returned back through `pipeline.reconcile.entrypoint`.

`pipeline.reconcile.stage_runtime` is thin: despite the name, it mostly
provides typed dataclasses plus a single pass-through runner that turns the
dependency bundles into `run_paper_pipeline(...)` kwargs.

## Stage-By-Stage Flow

| Stage | Purpose | Primary modules | Main outputs |
| --- | --- | --- | --- |
| 0. Entrypoint and dependency assembly | Build `PipelineConfig`, root helper bundles, and the frozen loader/binding/assembly dependency graph that the runtime will use. | `pipeline/reconcile/entrypoint.py`, `pipeline/reconcile/runtime_deps.py`, `pipeline/reconcile/runtime_builders.py`, `pipeline/reconcile/stage_runtime.py` | `ReconcileRuntimeInputs`, `ReconcileRuntimeDeps`, runtime kwargs for `run_paper_pipeline(...)` |
| 1. Source resolution | Resolve native and optional external layout/math inputs, normalize figures, compute acquisition route and source scorecard, and choose metadata/reference observations. | `pipeline/orchestrator/resolve_sources.py` | `state.native_layout`, `state.external_layout`, `state.merged_layout`, `state.external_math`, `state.mathpix_layout`, `state.figures`, `state.acquisition_route`, `state.source_scorecard`, `state.metadata_observation`, `state.reference_observation`, engine names, input fingerprints |
| 2. Record normalization | Convert resolved layout into working records, inject external math, apply Mathpix and optional pdftotext text repair, promote headings, merge math fragments, and split records into prelude vs section roots. | `pipeline/orchestrator/normalize_records.py` | `state.records`, `state.layout_by_id`, `state.page_one_records`, `state.prelude_records`, `state.section_roots`, `state.external_math_entries`, page maps, `state.effective_text_engine` |
| 3. Front matter and section preparation | Build title/authors/abstract blocks, recover or replace missing abstracts, create a synthetic introduction when needed, and prepare section nodes for section materialization. | `pipeline/orchestrator/assemble_document.py`, `pipeline/assembly/front_matter_builder.py`, `pipeline/assembly/abstract_recovery.py`, `pipeline/reconcile/section_preparation.py` | `front_matter`, early `blocks`, ordered section roots, `section_nodes`, debug title/abstract decisions |
| 4. Section materialization and document postprocess | Materialize sections and references, compile and annotate math, suppress display-math/header noise, normalize footnotes, merge paragraph blocks, and build the canonical document shell. | `pipeline/orchestrator/assemble_document.py`, `pipeline/assembly/section_builder.py`, `pipeline/assembly/canonical_builder.py`, `pipeline/reconcile/block_merging.py`, `pipeline/reconcile/math_suppression.py` | `state.blocks`, `state.sections`, `state.math_entries`, `state.references`, `state.decision_artifacts`, `state.document` |
| 5. Metadata/reference ownership overlay | Apply the chosen metadata/reference observation after document assembly, replacing low-quality title/abstract/reference content only when the current ownership basis allows it. | `pipeline/orchestrator/metadata_enrichment.py`, `pipeline/acquisition/source_ownership.py` | Updated `state.front_matter`, `state.blocks`, `state.references`, metadata decision artifact, final `state.document` |
| 6. Public return surface | Return the full `PaperState` or unwrap the canonical document for external callers. | `pipeline/reconcile/entrypoint.py` | `reconcile_paper_state(...) -> PaperState`, `reconcile_paper(...) -> dict` |

## Dependency Bundle Map

The code currently separates reconcile dependencies into three frozen bundles in
`pipeline.reconcile.stage_runtime`:

- `ReconcileLoaderDeps`
  Purpose: paper-id based loading and source-repair entrypoints.
  Main examples: layout extraction, external layout/math loading, figure
  extraction, pdftotext access.
- `ReconcileBindingDeps`
  Purpose: policy helpers, regexes, text normalization, front matter parsing,
  math heuristics, record-level transforms.
  Main examples: abstract/title heuristics, heading promotion helpers, text
  repair helpers, record cleaners, math-entry classification.
- `ReconcileAssemblyDeps`
  Purpose: section assembly and final canonical document construction.
  Main examples: section tree materialization, reference extraction/merge,
  block postprocess, formula compilation, canonical document build.

`pipeline.reconcile.runtime_deps` constructs these bundles.
`pipeline.reconcile.runtime_builders` then converts them into four helper maps:

- text helpers
- math helpers
- front matter helpers
- record helpers

That conversion layer is the main bridge between the frozen dependency graph
and the much older `run_paper_pipeline(...)` keyword-argument interface.

## Top Density Hotspots

These are the five files that currently look densest by combined
responsibility and import surface, based on a quick line-count and import-fan-in
scan of `pipeline/reconcile/*.py`.

1. `pipeline/reconcile/runtime_deps.py`
   - About `1541` lines and `49` imported names.
   - Builds most helper bundles and owns a very wide swath of reconcile
     assembly wiring.
2. `pipeline/reconcile/entrypoint.py`
   - About `395` lines and `143` imported names.
   - Acts as the root import concentrator for assembly, math, text, policy,
     runtime, and orchestrator seams.
3. `pipeline/reconcile/front_matter_parsing_runtime.py`
   - About `638` lines and `26` imported names.
   - Mixes front matter parsing, heuristics, and runtime-style binding logic.
4. `pipeline/reconcile/front_matter_runtime.py`
   - About `610` lines and `19` imported names.
   - Owns front matter support and recovery orchestration, which makes it a
     second major concentration point in the same domain.
5. `pipeline/reconcile/text_repairs_runtime.py`
   - About `348` lines and `18` imported names.
   - Couples multiple text-repair decisions and bound helper construction in
     one runtime surface.

Close follow-up candidates:

- `pipeline/reconcile/block_merging.py`
  Why it matters: high behavioral density at about `518` lines, even with a
  smaller import fan-in.
- `pipeline/reconcile/record_runtime.py`
  Why it matters: another mid-sized adapter surface at about `438` lines that
  feeds many section/materialization behaviors.

## Recommended First Simplification Target

The most approachable Step 3.2 starting point appears to be a bounded
runtime/pure-function pair rather than one of the front matter hubs.

Recommended first pair:

- `pipeline/reconcile/layout_records.py`
- `pipeline/reconcile/layout_records_runtime.py`

Why this pair first:

- it is smaller than the front matter runtime cluster
- it is directly on the record-normalization path
- it looks more adapter-heavy than policy-heavy, which makes it a better place
  to prove a merge-or-rename simplification pattern before touching the larger
  front matter seams

## Current Mental Model

When reading reconcile code today, the simplest model is:

1. `entrypoint.py` gathers everything.
2. `runtime_deps.py` freezes the dependency graph.
3. `runtime_builders.py` reshapes that graph for the legacy runner surface.
4. `paper_reconciler.py` executes four real stages:
   source resolution, record normalization, document assembly, and metadata
   overlay.
5. `entrypoint.py` returns either the updated `PaperState` or just the
   assembled document.
