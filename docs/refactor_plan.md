# Pipeline Refactor Plan

Date: 2026-04-17

Status: active, mid-refactor

Current naming note:

- `pipeline/` is the current engine package.
- `paper_pipeline` is an older name and is not the target architecture.
- Legacy `PAPER_PIPELINE_*` environment variables are still accepted as compatibility seams during migration.

## Goal

Make the ingestion pipeline light, decoupled, and debuggable enough that a broken paper can be diagnosed from stage artifacts and narrow helper modules instead of by cross-reading large heuristic files.

The practical target is not novelty in architecture. It is a standard, boring shape where:

- config and path resolution are explicit
- source acquisition is grouped by extractor family
- orchestration is thin
- document-quality heuristics are pure and testable
- assembly is separate from selection and cleanup
- root-level files become wrappers or small coordinators instead of implementation homes

## Verified Current Status

The repo is no longer at the "single large pipeline file plus scripts" stage.

Already in place:

- `PipelineConfig` exists in `pipeline/config.py`
- `ProjectLayout` exists in `pipeline/corpus_layout.py`
- `PaperState` exists in `pipeline/state.py`
- slim CLI entrypoints live under `pipeline/cli/`
- real implementation families now live under package directories instead of only at `pipeline/` root
- many former root implementation modules are now compatibility wrappers

Current implementation package families:

- `pipeline/assembly/`
- `pipeline/cli/`
- `pipeline/corpus/`
- `pipeline/figures/`
- `pipeline/math/`
- `pipeline/orchestrator/`
- `pipeline/output/`
- `pipeline/policies/`
- `pipeline/reconcile/`
- `pipeline/selectors/`
- `pipeline/sources/`
- `pipeline/text/`

Current compatibility pattern:

- keep public root import paths stable when tests or scripts patch them
- move real implementation into a package family
- leave a root wrapper or facade in place until downstream usage no longer depends on it

Current verification baseline:

- full integration suite passes
- latest result: `python3 -m unittest discover -s tests/integration/pipeline -p '*_test.py'`
- result: `Ran 352 tests in 2.149s OK`

## Repository Boundary Status

This area is improved but not fully finished.

What is true today:

- `ProjectLayout` resolves corpora under `corpus/<name>/` when that location exists
- project-mode builds are explicit through `PIPELINE_PROJECT_DIR`
- the engine no longer has to assume a single checked-in corpus shape

What is intentionally still present as migration compatibility:

- legacy `PAPER_PIPELINE_*` env var names
- legacy root-level corpus fallback
- temporary fallback to `docs/` when the new corpus home is not present

Implication:

- the repository boundary cleanup is substantially underway, but not complete until the engine no longer needs the legacy root/docs fallbacks

## Current Package Shape

### Core Runtime

- `pipeline/config.py`
  Defines `PipelineConfig`
- `pipeline/corpus_layout.py`
  Defines `ProjectLayout` and current corpus/project path resolution
- `pipeline/state.py`
  Defines `PaperState`

### CLI

- `pipeline/cli/paper_build.py`
- `pipeline/cli/external_source_build.py`
- `pipeline/cli/run_corpus_rounds.py`
- `pipeline/cli/run_project.py`
- other thin command wrappers

### Corpus

- `pipeline/corpus/metadata.py`
- `pipeline/corpus/lexicon.py`
- `pipeline/corpus/lexicon_builder.py`

Root wrappers still exist for compatibility:

- `pipeline/corpus_metadata.py`
- `pipeline/lexicon.py`
- `pipeline/build_corpus_lexicon.py`

### Math

- `pipeline/math/extract.py`
- `pipeline/math/review_policy.py`
- `pipeline/math/diagnostics.py`
- `pipeline/math/semantic_ir.py`
- `pipeline/math/semantic_policy.py`
- `pipeline/math/mathml.py`
- `pipeline/math/compile.py`

Root wrappers still exist for compatibility:

- `pipeline/extract_math.py`
- `pipeline/math_review_policy.py`
- `pipeline/formula_diagnostics.py`
- `pipeline/formula_semantic_ir.py`
- `pipeline/formula_semantic_policy.py`
- `pipeline/mathml_compiler.py`
- `pipeline/compile_formulas.py`

### Sources

- `pipeline/sources/layout.py`
- `pipeline/sources/pdftotext.py`
- `pipeline/sources/figures.py`
- `pipeline/sources/external.py`
- `pipeline/sources/docling.py`
- `pipeline/sources/mathpix.py`

Root wrappers still exist for compatibility:

- `pipeline/extract_layout.py`
- `pipeline/extract_pdftotext.py`
- `pipeline/extract_figures.py`
- `pipeline/external_sources.py`
- `pipeline/docling_adapter.py`
- `pipeline/mathpix_adapter.py`

### Text

- `pipeline/text/prose.py`
- `pipeline/text/references.py`
- `pipeline/text/document_policy.py`

Root wrappers still exist for compatibility:

- `pipeline/normalize_prose.py`
- `pipeline/normalize_references.py`
- `pipeline/document_policy.py`

### Figures

- `pipeline/figures/labels.py`
- `pipeline/figures/linking.py`

Root wrappers still exist for compatibility:

- `pipeline/figure_labels.py`
- `pipeline/figure_linking.py`

### Orchestrator

Already extracted:

- `pipeline/orchestrator/resolve_sources.py`
- `pipeline/orchestrator/normalize_records.py`
- `pipeline/orchestrator/assemble_document.py`
- `pipeline/orchestrator/paper_reconciler.py`
- `pipeline/orchestrator/layout_merge.py`
- `pipeline/orchestrator/round_build.py`
- `pipeline/orchestrator/round_document.py`
- `pipeline/orchestrator/round_reporting.py`
- `pipeline/orchestrator/source_composition.py`

Important current boundary:

- `pipeline/run_corpus_rounds.py` is still the stable patch/import surface for the round runner
- pure helper logic has been moved out, but patch-sensitive coordination remains there intentionally

## What Has Been Completed

### 1. Standard runtime objects exist

This is no longer conceptual work.

- `PipelineConfig` is the explicit runtime config object
- `ProjectLayout` is the explicit path/layout object
- `PaperState` is the explicit per-paper working state object

### 2. CLI entrypoints were slimmed into a standard pattern

The repo now has a usable split between:

- implementation helpers in `pipeline/cli/*_build.py`
- command entrypoints in `pipeline/cli/*.py`
- compatibility scripts at `pipeline/*.py`

### 3. Large root implementation clusters have been relocated

Completed family moves:

- corpus helpers moved under `pipeline/corpus/`
- math helpers moved under `pipeline/math/`
- source adapters and extractors moved under `pipeline/sources/`
- prose/reference/document policy moved under `pipeline/text/`
- figure caption and linking logic moved under `pipeline/figures/`
- round-runner pure logic moved under `pipeline/orchestrator/`

### 4. Output handling is no longer only implicit

There is now a distinct `pipeline/output/` family and more explicit output-side helpers than before, even though some output wrappers still remain at the root.

### 5. The refactor has stayed behavior-safe

The working pattern so far has been:

- move pure implementation first
- preserve root import paths as wrappers where patch seams matter
- only switch internal imports directly to packaged modules when test seams are not relying on the root names

That pattern has worked and should continue.

## Remaining Root-Level Hotspots

Largest remaining root files at the time of this update:

- `pipeline/reconcile_blocks.py` — 1846 lines

Recently reduced:

- `pipeline/audit_corpus.py` — now a 59-line compatibility wrapper
- extracted audit implementation now lives in `pipeline/corpus/audit.py`
- extracted audit markdown rendering now lives in `pipeline/output/audit_report.py`
- `pipeline/text_utils.py` — now a 34-line compatibility wrapper
- extracted heading/section helpers now live in `pipeline/text/headings.py`
- `pipeline/corpus_layout.py` — now a 169-line boundary object module
- extracted path/config-prep helpers now live in `pipeline/corpus/paths.py`
- `pipeline.corpus` now uses lazy exports so submodules can be reused without package-init cycles
- `pipeline/staleness_policy.py` — now a 117-line policy wrapper/coordinator
- extracted fingerprinting/build metadata helpers now live in `pipeline/output/fingerprints.py`
- `pipeline/mathpix_adapter.py` — now a 308-line compatibility adapter over `pipeline/sources/mathpix.py`
- the root Mathpix adapter keeps test-facing patch seams while delegating implementation to `pipeline/sources/mathpix.py`
- `pipeline/run_corpus_rounds.py` — now an 894-line coordinator
- extracted runtime/status/env helpers now live in `pipeline/orchestrator/round_runtime.py`
- `pipeline/reconcile_blocks.py` — first narrow extractions are underway
- extracted record/text cleaning helpers now live in `pipeline/reconcile/text_cleaning.py`
- extracted reference-runtime helper composition now lives in `pipeline/reconcile/reference_runtime.py`
- extracted front-matter candidate/recovery helpers now live in `pipeline/reconcile/front_matter_runtime.py`
- extracted text normalization/reference runtime helper composition now lives in `pipeline/reconcile/text_runtime.py`
- extracted math policy/demotion runtime helper composition now lives in `pipeline/reconcile/math_runtime.py`
- extracted record/postprocess runtime helper composition now lives in `pipeline/reconcile/record_runtime.py`
- extracted runtime dependency bundle assembly now lives in `pipeline/reconcile/runtime_deps.py`
- extracted shared reconcile utility support now lives in `pipeline/reconcile/runtime_support.py`
- extracted coordinator-stage binding factories now live in `pipeline/reconcile/stage_runtime.py`
- `pipeline/reconcile/stage_runtime.py` now also covers record-normalization and postprocess binding factories that were previously inlined inside `reconcile_paper_state`
- `pipeline/reconcile/stage_runtime.py` now also covers layout-bound text normalization and math-entry policy/demotion bindings that were previously local to `reconcile_paper_state`
- `pipeline/reconcile/stage_runtime.py` now also covers the remaining lambda-style binders for layout-bound loaders, section helpers, and block-assembly support wiring
- `pipeline/reconcile/stage_runtime.py` now also owns the binding-and-dispatch executor that composes those factories and calls `run_paper_pipeline(...)`
- the stage-runtime executor now accepts typed runtime objects (`ReconcileRuntimeInputs` and `ReconcileRuntimeDeps`) instead of a giant flat keyword surface, reducing the new refactor debt introduced during extraction
- `ReconcileRuntimeDeps` is now grouped into `ReconcileLoaderDeps`, `ReconcileBindingDeps`, and `ReconcileAssemblyDeps`, which makes the stage-runtime boundary more explicit
- `run_reconcile_pipeline(...)` is now a thin orchestrator over a dedicated `build_reconcile_runtime_kwargs(...)` helper instead of a long local rebinding/unpacking block
- the grouped runtime helper construction has now moved into `pipeline/reconcile/runtime_builders.py`, leaving `pipeline/reconcile/stage_runtime.py` as the typed boundary plus executor entrypoint
- front-matter runtime builder construction has now been pulled back into `pipeline/reconcile/front_matter_runtime.py`, so `runtime_builders.py` is already starting to decompose by domain instead of becoming a new generic monolith

Interpretation:

- `run_corpus_rounds.py` has already been materially reduced and is no longer the worst root orchestrator
- `reconcile_blocks.py` is still the dominant monolith
- `audit_corpus.py` has been converted into the intended wrapper shape without changing the CLI/import surface
- `text_utils.py` has also been converted into the intended wrapper shape
- `corpus_layout.py` now better matches the intended boundary-object role
- `staleness_policy.py` now matches the natural split between fingerprint/build metadata helpers and staleness policy logic
- `mathpix_adapter.py` now better matches the compatibility-adapter role, although its patch-sensitive seams still justify some root-local code
- `run_corpus_rounds.py` now looks much more like an intentional coordinator after peeling off runtime/status/env helpers
- `reconcile_blocks.py` is now the clear next target and the only remaining root monolith that still needs substantive dismantling
- the first `reconcile_blocks.py` seam is now proven: narrow helper extraction with root compatibility wrappers keeps the integration suite stable
- the private helper surface inside `reconcile_blocks.py` is now wrapper-shaped end to end; the next reductions should target larger coordinator-stage boundaries rather than more utility peeling
- the first coordinator-stage split is now in place: front-matter build, abstract recovery, and block-assembly binding moved behind `pipeline/reconcile/stage_runtime.py`
- that coordinator-stage extraction has now expanded to absorb normalization/postprocess binding closures as well, further reducing the inline orchestration burden inside `reconcile_paper_state`
- `reconcile_paper_state` no longer carries nested helper `def`s; it is now primarily factory composition plus the final `run_paper_pipeline(...)` orchestration call
- `reconcile_paper_state` now also carries zero inline lambdas; the root entrypoint is effectively a declarative coordinator over stage-runtime factories and `run_paper_pipeline(...)`
- `reconcile_paper_state` is now a minimal facade: runtime-config selection plus delegation into `pipeline/reconcile/stage_runtime.py`, with the root `run_paper_pipeline` symbol still passed through as the compatibility/patch seam
- `pipeline/reconcile_blocks.py` now imports the stage-runtime executor directly rather than the full factory toolbox, which is a better match for its compatibility-facade role
- stale root-only imports from earlier extraction phases have been trimmed from `pipeline/reconcile_blocks.py`, reducing facade noise without changing the test-facing helper surface
- the patch-sensitive dependency bundle construction in `reconcile_blocks.py` now lives behind dedicated root-local helper builders instead of one giant inline call site
- the root binding dependency seam is now decomposed into smaller concern-grouped helper builders, which keeps the patch surface local while making the remaining debt easier to target
- the stage-runtime kwargs seam is now decomposed into grouped helper builders for text, math, front-matter, record/postprocess, and loader runtime wiring
- the runtime dependency bundle assembly has now also moved into `pipeline/reconcile/runtime_deps.py`, leaving the root file with a single compact runtime-deps handoff instead of multiple local packaging helpers
- the remaining front-matter/reference root helper names are now mostly direct bound facades over extracted runtime helpers rather than hand-written pass-through wrapper defs, which trims facade debt without changing the test-facing symbol surface
- the screening and paragraph/postprocess helper names at the root are now also mostly direct bound facades over extracted helpers, further shrinking facade-only code while keeping the stable test-facing symbol surface intact
- the screening runtime binding layer for OCR/noise and figure-debris heuristics now lives in `pipeline/reconcile/screening_runtime.py`, so those root helper names are no longer responsible for binding that domain-specific dependency set inline
- the text-repair runtime binding layer for pdftotext and Mathpix hint helpers now lives in `pipeline/reconcile/text_repairs_runtime.py`, so the root file no longer owns that dependency wiring inline either
- the front-matter parsing/policy runtime binding layer now lives in `pipeline/reconcile/front_matter_parsing_runtime.py`, leaving the root file with the same test-facing helper names but far less inline front-matter dependency wiring
- the layout-record and figure-caption runtime binding layer now lives in `pipeline/reconcile/layout_records_runtime.py`, so the remaining caption/layout glue at the root is mostly stable helper names rather than inline dependency assembly
- the heading-promotion binding layer now lives in `pipeline/reconcile/heading_promotion_runtime.py`, with `pipeline/reconcile_blocks.py` keeping the same `_decode/_normalize/_split` helper names while shedding their inline dependency wiring
- the reference helper binding layer now lives in `pipeline/reconcile/reference_binding_runtime.py`, moving the root `_make_reference_entry`, `_looks_like_reference_text`, `_is_reference_start`, and related reference closures out without changing their test-facing names
- the math-fragment binding layer now lives in `pipeline/reconcile/math_fragments_runtime.py`, so `_looks_like_math_fragment`, `_math_signal_count`, `_strong_operator_count`, and `_merge_math_fragment_records` stay test-stable while leaving the root file
- the external-math injection binding now lives in `pipeline/reconcile/external_math_binding_runtime.py`, keeping `_inject_external_math_records` stable at the root while moving its leading-display-echo dependency wiring out
- the section-filter binding layer now lives in `pipeline/reconcile/section_filter_binding_runtime.py`, moving the paragraph-merge/running-header/table-heading closure setup out while preserving the same root helper names for tests and remaining compatibility callers
- the remaining block-builder helper binding layer now lives in `pipeline/reconcile/block_builder_binding_runtime.py`, so `_list_item_marker`, `_looks_like_real_code_record`, `_match_external_math_entry`, and the rect helpers no longer need inline root partials
- the shared text/runtime support binding layer now lives in `pipeline/reconcile/support_binding_runtime.py`, moving the root `_clean_text`, `_block_source_spans`, `_normalize_paragraph_text`, `_record_analysis_text`, `_word_count`, `_mathish_ratio`, and related support closures out while keeping the same compatibility names
- the math-entry policy binding layer now lives in `pipeline/reconcile/math_entry_binding_runtime.py`, so the root `_math_entry_*`, `_should_demote_*`, `_should_drop_*`, and `_paragraph_block_from_graphic_math_entry` helpers keep their compatibility names without owning the inline dependency wiring
- `pipeline/reconcile/stage_runtime.py` has now shrunk to a small boundary module while `pipeline/reconcile/runtime_builders.py` absorbs the runtime helper-construction implementation
- `pipeline/reconcile/runtime_builders.py` is no longer absorbing all domains indiscriminately; front-matter builder logic has already moved into the front-matter runtime module, which is the right direction for the next semantic splits
- the remaining runtime-builder helper families have now also been pulled into dedicated domain modules for text, math, and record/postprocess wiring, leaving `pipeline/reconcile/runtime_builders.py` as a small composition-root plus loader helper module
- the main reconcile tech debt is now narrower and clearer: the remaining debt is no longer concentrated in one obvious mechanical block, and the next work should prefer smaller semantic seams over more large-scale coordinator reshaping

## Current Refactor Rules

These rules now reflect what is actually working in the repo.

- Preserve patch seams at the root when tests depend on them.
- Prefer moving pure helpers before moving orchestration.
- Do not create a new top-level package family unless it clearly groups multiple related modules.
- Prefer package families over a flat `pipeline/` root whenever two or more files clearly belong together.
- Keep the `pipeline/` root as a boundary layer, not the long-term home of most implementation.
- Do not force the tests to relearn import paths unless there is a strong reason.

## Immediate Next Plan

### Phase A. Finish the low-risk root cleanup

Completed:

- `pipeline/audit_corpus.py` was reduced to a thin coordinator/wrapper
- audit scanning and heuristics moved to `pipeline/corpus/audit.py`
- audit markdown rendering moved to `pipeline/output/audit_report.py`
- the root CLI/import surface stayed stable for tests and scripts

Result:

- the root now matches the intended boundary-layer shape
- pure audit/report logic is isolated from the command path

### Phase B. Keep reducing shared root utilities

Completed:

- `pipeline/text_utils.py` was reduced to a thin compatibility wrapper
- heading parsing, section-tree construction, and text cleanup helpers moved to `pipeline/text/headings.py`
- root imports for `SectionNode`, `compact_text`, `clean_heading_title`, and related helpers stayed stable
- `pipeline/corpus_layout.py` kept `ProjectLayout` at the root while moving path/config-prep helpers to `pipeline/corpus/paths.py`
- root imports for `prepare_project_inputs`, `display_path`, `normalize_paper_id`, and related helpers stayed stable
- `pipeline.corpus` package exports were made lazy so layout helpers can live under the corpus family without circular imports
- `pipeline/staleness_policy.py` stayed centralized while fingerprint/build metadata helpers moved to `pipeline/output/fingerprints.py`
- root imports for `fingerprint_path`, `pipeline_fingerprint`, `build_input_fingerprints`, and `build_metadata_for_paper` stayed stable

Next likely targets after `corpus_layout.py`:

- `pipeline/reconcile_blocks.py`
- `pipeline/docling_adapter.py` only if a cleaner compatibility seam appears

Plan:

- keep root adapters as compatibility surfaces while continuing to move implementation into `pipeline/sources/`

Success criteria:

- fewer medium-sized general-purpose root files
- cleaner separation between boundary objects and helper logic
- after this pass, the remaining prep work is considered sufficient to begin narrow `reconcile_blocks.py` extractions

### Phase C. Continue adapter normalization

Targets:

- `pipeline/mathpix_adapter.py`
- `pipeline/docling_adapter.py`

Completed so far:

- `pipeline/mathpix_adapter.py` now delegates through `pipeline/sources/mathpix.py` while preserving root-local monkeypatch seams used by tests
- `pipeline/docling_adapter.py` is already essentially wrapper-shaped and does not currently need the same kind of extraction work

Ongoing intent:

- keep the root adapters only as patch-friendly compatibility surfaces
- move any remaining implementation detail that can safely move into `pipeline/sources/mathpix.py` and `pipeline/sources/docling.py`
- preserve current monkeypatch seams where tests rely on root-local symbols

Success criteria:

- root adapters become visibly wrapper-shaped
- implementation stays in `pipeline/sources/`

### Phase D. Resume dismantling `reconcile_blocks.py`

This remains the highest-value but highest-risk refactor area.

Already extracted around it:

- orchestration helpers under `pipeline/orchestrator/`
- assembly helpers under `pipeline/assembly/`
- multiple reconcile helpers under `pipeline/reconcile/`
- text/math/source helpers in their own families

Recommended next extractions from `reconcile_blocks.py`:

- most non-`reconcile_blocks` root modules are now either boundary objects, compatibility wrappers, or intentional coordinators
- `reconcile_blocks.py` helper wrappers are now consistently shaped around `pipeline/reconcile/*` and `pipeline/assembly/*`
- the next high-value work should therefore move coordinator-stage chunks, not more leaf utilities, unless a new patch-sensitive seam appears
- first completed narrow seams:
  - record/text cleaning helpers moved to `pipeline/reconcile/text_cleaning.py`
  - reference-runtime helper composition moved to `pipeline/reconcile/reference_runtime.py`
  - front-matter candidate/recovery helper composition moved to `pipeline/reconcile/front_matter_runtime.py`
  - shared helper utilities moved to `pipeline/reconcile/runtime_support.py`
  - coordinator-stage binding factories moved to `pipeline/reconcile/stage_runtime.py`
  - `stage_runtime.py` now also owns layout-bound normalization and math-entry policy factories
  - `stage_runtime.py` now also owns the former inline lambda binders used by `reconcile_paper_state`
  - `stage_runtime.py` now also owns the former factory-composition and dispatch body of `reconcile_paper_state`
  - `stage_runtime.py` now also owns layout merge, mathpix repair, heading-promotion, and postprocess block-binding factories
  - `stage_runtime.py` now groups runtime deps into loader, binding, and assembly bundles instead of a single flat dependency object
  - `run_reconcile_pipeline(...)` now delegates runtime-prep assembly to `build_reconcile_runtime_kwargs(...)` instead of locally unpacking every grouped dependency
  - grouped runtime helper-construction code now lives in `pipeline/reconcile/runtime_builders.py`, reducing `stage_runtime.py` to the typed surface and executor
  - front-matter runtime builder helpers now live in `pipeline/reconcile/front_matter_runtime.py` instead of the generic runtime-builders module
  - text normalization/reference runtime builder helpers now live in `pipeline/reconcile/text_runtime.py`
  - math policy/demotion runtime builder helpers now live in `pipeline/reconcile/math_runtime.py`
  - record/postprocess runtime builder helpers now live in `pipeline/reconcile/record_runtime.py`
  - runtime dependency bundle assembly now lives in `pipeline/reconcile/runtime_deps.py`
  - `reconcile_blocks.py` now assembles those grouped runtime deps through root-local helper builders rather than one large inline nested constructor
  - root `_clean_text`/`_normalize_paragraph_text`/front-matter/reference helper names remain stable for tests

- title/author/affiliation detection helpers
- reference extraction and cleanup helpers
- additional record cleanup and paragraph/section support that can move without destabilizing the full build path

Preferred destination:

- `pipeline/reconcile/`
- `pipeline/assembly/`
- `pipeline/selectors/` when the logic is truly semantic selection rather than cleanup

Success criteria:

- `reconcile_blocks.py` becomes a thin coordinator over package helpers
- title/front-matter/reference fixes become local edits instead of monolith surgery

## Planned End-State Shape

This is the target shape from here, adjusted to what now already exists.

### Boundary Objects

- `pipeline/config.py`
- `pipeline/corpus_layout.py`
- `pipeline/state.py`

### Source Acquisition

- `pipeline/sources/*`
- `pipeline/figures/*`
- `pipeline/cli/external_source_build.py`

### Record Normalization And Document Build

- `pipeline/orchestrator/*`
- `pipeline/reconcile/*`
- `pipeline/assembly/*`
- `pipeline/text/*`
- `pipeline/math/*`

### Corpus-Level Logic

- `pipeline/corpus/*`

### Output And Reporting

- `pipeline/output/*`
- thin root/report wrappers only where compatibility still matters

## Stage Boundary Intent

The stage boundary we should continue converging toward is:

### 1. Config And Layout

Owned by:

- `PipelineConfig`
- `ProjectLayout`
- `PaperState`

Responsibility:

- resolve what build we are doing
- resolve where inputs and outputs live
- hold explicit per-paper pipeline state

### 2. Source Acquisition And Composition

Owned by:

- `pipeline/sources/*`
- `pipeline/figures/*`
- `pipeline/orchestrator/source_composition.py`

Responsibility:

- acquire source artifacts
- normalize extractor payloads
- compose external layout/math sources without semantic document decisions

### 3. Record Normalization And Selection

Owned by:

- `pipeline/orchestrator/*`
- `pipeline/reconcile/*`
- `pipeline/selectors/*`

Responsibility:

- convert source artifacts into normalized records
- identify front matter, sections, references, math, and figures
- keep policy logic grouped and testable

### 4. Assembly And Outputs

Owned by:

- `pipeline/assembly/*`
- `pipeline/output/*`

Responsibility:

- assemble canonical outputs from already-normalized state
- write stable artifacts, reviews, and reports

## Explicit Non-Goals Right Now

- do not rename everything at once
- do not remove root compatibility wrappers prematurely
- do not force a perfect package taxonomy before the file families are clear
- do not attack `reconcile_blocks.py` and another high-coupling root monolith in the same pass unless the extracted seam is obviously pure

## Expected End State

- the `pipeline/` root mostly contains boundary objects, compatibility wrappers, and a small number of true coordinators
- implementation lives in package families instead of dozens of unrelated root files
- `run_corpus_rounds.py` and similar command files become thin
- `reconcile_blocks.py` shrinks dramatically or disappears behind explicit stage helpers
- the corpus home is cleanly `corpus/<name>/` without special-case fallbacks
- a broken paper can be debugged by stage and helper family instead of by reading monoliths
