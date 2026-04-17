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
- `pipeline/audit_corpus.py` — 954 lines
- `pipeline/run_corpus_rounds.py` — 951 lines
- `pipeline/mathpix_adapter.py` — 382 lines
- `pipeline/text_utils.py` — 305 lines
- `pipeline/corpus_layout.py` — 279 lines
- `pipeline/staleness_policy.py` — 261 lines

Interpretation:

- `run_corpus_rounds.py` has already been materially reduced and is no longer the worst root orchestrator
- `reconcile_blocks.py` is still the dominant monolith
- `audit_corpus.py` is now the best next large refactor target before attempting another high-coupling `reconcile_blocks.py` slice

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

Next target:

- `pipeline/audit_corpus.py`

Plan:

- move corpus-audit scanning and report-rendering helpers out of the root file
- keep `pipeline/audit_corpus.py` as the stable entrypoint and compatibility surface
- avoid inventing a one-off top-level category just for one file

Preferred destination:

- use `pipeline/corpus/` and `pipeline/output/` for the extracted helpers rather than adding a brand-new root category unless the audit split clearly grows into a real family

Success criteria:

- `audit_corpus.py` becomes a small coordinator or wrapper
- pure audit/report logic becomes testable without loading the full command path

### Phase B. Keep reducing shared root utilities

Next likely targets after `audit_corpus.py`:

- `pipeline/text_utils.py`
- `pipeline/corpus_layout.py`
- `pipeline/staleness_policy.py`

Plan:

- move pure text/heading helpers into the existing `pipeline/text/` family where appropriate
- keep `ProjectLayout` in `pipeline/corpus_layout.py` for now, but consider pulling pure path helpers into `pipeline/corpus/` if that reduces coupling without hiding the main boundary object
- keep `staleness_policy.py` centralized unless it naturally splits into fingerprinting vs policy helpers

Success criteria:

- fewer medium-sized general-purpose root files
- cleaner separation between boundary objects and helper logic

### Phase C. Continue adapter normalization

Targets:

- `pipeline/mathpix_adapter.py`
- `pipeline/docling_adapter.py`

Plan:

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

- front-matter candidate and recovery logic
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
