# Pipeline Refactor Plan

Date: 2026-04-16

Goal: make the ingestion pipeline light, decoupled, and debuggable enough that a broken paper can be diagnosed from stage artifacts instead of from cross-reading large heuristic files.

## Root-Level Repository Structure

The repo should treat the engine and corpora as separate first-class concerns at the root.

Target shape:

- `pipeline/`
  Engine code only.
- `corpus/`
  Root container for corpora.
- `corpus/<name>/`
  One checked-in corpus, such as `corpus/stepview/`.
- `tests/`
  Unit, stage, and replay regression tests.
- `docs/`
  Architecture, refactor plans, operational notes.
- `tmp/`
  Local generated output and replay/debug artifacts.

Implications:

- No corpus should live at the repo root as a special case.
- No engine module should hardcode `stepview/`.
- The engine should default to `corpus/<corpus-name>/`, with environment overrides only as compatibility seams.

## Refactor Objectives

- Split extraction, selection, assembly, and orchestration into separate layers.
- Replace hidden fallback behavior with explicit failure modes.
- Emit debug artifacts at each stage.
- Reduce cross-file and cross-stage coupling.
- Make title and abstract extraction independently testable.
- Shrink `pipeline/reconcile_blocks.py` dramatically by moving policy clusters into dedicated modules.

## Guiding Rules

- Each stage has one job.
- Each stage reads a small number of inputs and writes one explicit output artifact.
- Downstream stages must not silently reinterpret upstream failure.
- Heuristics belong in named policy modules, not interleaved conditionals in orchestration code.
- A paper should fail cleanly rather than succeed with invented metadata.

## Desired Layering

### 1. Inputs

Responsibility:

- discover papers
- resolve corpus paths
- locate PDFs and precomputed source artifacts
- load checked-in manual overrides

Planned modules:

- `pipeline/inputs/paper_locator.py`
- `pipeline/inputs/artifact_store.py`
- `pipeline/inputs/corpus_config.py`

### 2. Raw Extraction

Responsibility:

- run Docling, Mathpix, and pdftotext
- normalize raw tool output into typed extractor payloads
- never decide semantic meaning

Planned modules:

- `pipeline/extractors/docling.py`
- `pipeline/extractors/mathpix.py`
- `pipeline/extractors/pdftotext.py`
- `pipeline/extractors/types.py`

### 3. Structural Reconstruction

Responsibility:

- convert raw extractor output into normalized page/block/span records
- expose candidate structural evidence without semantic commitment

Planned modules:

- `pipeline/structure/layout_records.py`
- `pipeline/structure/page_model.py`
- `pipeline/structure/figure_records.py`
- `pipeline/structure/heading_records.py`

### 4. Semantic Selection

Responsibility:

- choose title, authors, affiliations, abstract, references, and sections
- emit both decisions and evidence

Planned modules:

- `pipeline/selectors/title_selector.py`
- `pipeline/selectors/front_matter_selector.py`
- `pipeline/selectors/abstract_selector.py`
- `pipeline/selectors/reference_selector.py`
- `pipeline/selectors/section_selector.py`

### 5. Assembly

Responsibility:

- build canonical output from already-selected pieces
- validate required fields
- never invent missing identity metadata

Planned modules:

- `pipeline/assembly/canonical_builder.py`
- `pipeline/assembly/validation.py`

### 6. Orchestration

Responsibility:

- scheduling
- concurrency
- retries
- status files
- force rebuild behavior
- stage execution order

Planned modules:

- `pipeline/orchestrator/run_corpus.py`
- `pipeline/orchestrator/status.py`
- `pipeline/orchestrator/work_queue.py`

## High-Risk Hotspots To Dismantle

### `pipeline/reconcile_blocks.py`

Current problem:

- too many responsibilities in one file
- extraction cleanup, front matter recovery, title heuristics, abstract heuristics, math suppression, reference extraction, paragraph merging, and assembly all coexist

Decomposition target:

- `pipeline/reconcile/record_cleanup.py`
- `pipeline/reconcile/front_matter_candidates.py`
- `pipeline/reconcile/title_detection.py`
- `pipeline/reconcile/author_affiliation_detection.py`
- `pipeline/reconcile/abstract_detection.py`
- `pipeline/reconcile/reference_detection.py`
- `pipeline/reconcile/block_merging.py`
- `pipeline/reconcile/math_suppression.py`
- `pipeline/reconcile/document_assembly.py`

### `pipeline/run_corpus_rounds.py`

Current problem:

- orchestration file still knows too much about document quality and preservation details

Decomposition target:

- keep only scheduling and state transitions in `run_corpus.py`
- move paper build execution into a small `paper_job.py`
- move status rendering into `status.py`
- move abstract preservation and reuse policies into selector or assembly code

## Stage Artifacts To Emit

For each paper, persist stage outputs under a debug path, ideally inside `canonical_sources/debug/` or another stable per-paper location:

- `stage-01-raw-docling.json`
- `stage-01-raw-mathpix.json`
- `stage-01-raw-pdftotext.json`
- `stage-02-records.json`
- `stage-03-front-matter-candidates.json`
- `stage-04-title-decision.json`
- `stage-05-abstract-decision.json`
- `stage-06-reference-decision.json`
- `stage-07-canonical-draft.json`

Each decision artifact should include:

- selected candidate
- rejected candidates
- evidence used
- confidence or score
- failure reason when no selection is made

## Immediate Refactor Sequence

### Phase 1. Repository Boundary Cleanup

Tasks:

- make `corpus/` the repo-root home for corpora
- remove root-level corpus special cases
- update docs and path resolution to use `corpus/<name>/`

Success criteria:

- engine code resolves default corpus paths under `corpus/`
- `stepview` is only one corpus, not a structural exception

### Phase 2. Observability First

Tasks:

- add structured title and abstract decision artifacts without changing selection logic too much
- make failed title and abstract selection explicit in artifacts

Success criteria:

- one broken abstract can be diagnosed from one artifact file

### Phase 3. Extract Abstract Selection

Tasks:

- move abstract logic out of `reconcile_blocks.py`
- create `selectors/abstract_selector.py`
- add replay tests for known broken papers

Success criteria:

- abstract fixes do not require editing front matter or reference code

### Phase 4. Extract Title and Front Matter

Tasks:

- move title, author, and affiliation logic into dedicated selector modules
- keep hard failure on missing recoverable title

Success criteria:

- title changes do not affect abstract behavior

### Phase 5. Extract Block Merging and Math Suppression

Tasks:

- separate prose cleanup / block merging from semantic selection
- isolate display-math suppression rules

Success criteria:

- paragraph merge bugs can be debugged without touching title or abstract code

### Phase 6. Simplify Orchestrator

Tasks:

- reduce `run_corpus_rounds.py` to scheduling and stage orchestration
- move stage-specific preservation rules outward to selectors or assembly

Success criteria:

- scheduling changes do not require editing extraction internals

## Testing Strategy

Three layers of tests:

### Policy Tests

- small pure-function tests
- title scoring
- caption contamination rejection
- abstract boundary rejection
- page-number/taxonomy/noise stripping

### Stage Tests

- feed normalized records into selectors
- assert structured decisions

### Replay Regression Tests

- maintain a curated hard-paper set
- verify exact decisions for title, abstract, references, and front matter

Seed replay set:

- the eight currently scoped abstract-failure papers

## Expected End State

- `reconcile_blocks.py` shrinks from a monolith into a thin coordinator or disappears entirely
- a paper can be replayed stage by stage
- a failed paper yields explicit structured reasons
- title and abstract debugging become local tasks, not repo-wide surgery
- new corpora can be added under `corpus/` without code changes
