# ROADMAP

Status: active

This is the only live roadmap for `paperx`.

## Objective

Finish the extraction cleanly and make the current architecture boring to
operate:

- one clear path from `_source` PDFs to canonical outputs
- one clear reset path back to source state
- better acquisition instead of heavier downstream recovery
- post-acquisition handling that keeps shrinking over time
- no compatibility scaffolding or silent fallback behavior unless explicitly
  approved case by case
- enough higher-layer evidence that the architecture can be trusted without
  archaeology

## Non-Negotiables

- checked-in corpora stay in source state
- processed artifacts are local only
- fail fast is preferred over degraded work products
- the project venv is the default runtime surface
- acquisition quality beats downstream reconstruction
- post-acquisition logic should normalize, not rebuild
- root prose documentation stays limited to `README.md` and `ROADMAP.md`

## Current State

Already true:

- the engine is package-first under `pipeline/`
- corpora live under `corpus/`
- corpus mode is the only supported layout model and is centered on `_source`
- `reset_corpus_to_source` is the reverse lifecycle command
- provider routing, OCR policy, and scoring live under `pipeline.acquisition`
- source extraction and batch execution live under `pipeline.processor`
- the test tree is split into `unit`, `integration`, `e2e`, and `smoke`

Still incomplete:

- the densest processor, acquisition, assembly, and figure-linking modules
  still need simplification
- too much downstream recovery logic still exists because upstream acquisition
  is not reliable enough yet
- acquisition fixtures and route expectations still need more decision-grade
  coverage
- optional provider surfaces still deserve more real-environment smoke checks
- top-level docs and operator-facing strings still need periodic cleanup so
  they stay aligned with the repo we actually have

## Finish Line

The repo is at the breakpoint when all of the following are true:

- the `_source` workflow is stable and unambiguous
- no new compatibility or fallback layers are being added by habit
- acquisition decisions are reliable enough that downstream repair keeps
  shrinking
- processor and assembly seams are easy to trace end to end
- acquisition decisions are validated by fixtures and audits rather than manual
  memory
- unit, integration, and e2e suites stay green in `.venv-paperx`

## Workstreams

### 1. Source Extraction And Provider Simplification

Primary target:

- keep the extraction path easy to follow from route choice to final source
  payloads
- keep improving acquisition quality so later stages can stay thin

Main files:

- `pipeline/processor/sources.py`
- `pipeline/acquisition/providers.py`
- `pipeline/acquisition/routing.py`
- `pipeline/acquisition/scoring.py`
- `pipeline/acquisition/source_ownership.py`

Definition of done:

- route reasons are explicit and close to the code that uses them
- OCR and provider decisions fail fast instead of disappearing behind fallback
  behavior
- acquisition output quality is high enough that downstream repair is rare
- tracing one paper through extraction no longer requires runtime spelunking

### 2. Post-Acquisition Reduction

Primary target:

- delete or shrink downstream reconstruction logic whenever better acquisition
  makes it unnecessary

Main files:

- `pipeline/assembly/record_block_builder.py`
- `pipeline/assembly/front_matter_builder.py`
- `pipeline/assembly/abstract_recovery.py`
- `pipeline/figures/linking.py`
- `pipeline/text/document_policy.py`
- `pipeline/text/headings.py`

Definition of done:

- helper ownership is obvious
- post-acquisition code is mostly normalization and formatting, not recovery
- each hot-path module has one job instead of acting like a logic sink
- the build path from acquired sources to canonical output is easy to trace

### 3. Lifecycle And Higher-Layer Validation

Primary target:

- keep the whole source-to-processed-to-source loop trustworthy

Main surfaces:

- `pipeline/cli/reset_corpus_to_source.py`
- `pipeline/cli/build_canonical.py`
- `pipeline/cli/build_review.py`
- `tests/e2e/**`
- `tests/integration/**`

Definition of done:

- the strict lifecycle contract is protected by integration tests
- breakage shows up in CI before it becomes operator folklore

### 4. Corpus And Fixture Hygiene

Primary target:

- keep checked-in corpora and fixtures honest and small

Main surfaces:

- `corpus/stepview/`
- `tests/fixtures/render_review_project/`
- `docs/fixed_validation_slice.json`

Definition of done:

- checked-in regression surfaces stay intentionally small
- repeated validation uses scratch slices under `tmp/`
- fixture taxonomy is easy to understand and extend

### 5. Documentation Discipline

Primary target:

- keep the docs set small enough that it can actually stay true

Rules:

- update `README.md` when the operator model changes materially
- update `ROADMAP.md` when the active backlog changes materially
- do not create new prose docs without a concrete reason that survives review

## Near-Term Queue

1. Keep pruning leftover legacy and fallback branches whenever they are touched.
2. Improve acquisition quality before adding any new downstream repair logic.
3. Continue reducing density in `pipeline/processor/sources.py`,
   `pipeline/acquisition/providers.py`, and the heaviest post-acquisition
   modules.
4. Expand acquisition fixtures around OCR routing, provider choice, and failure
   cases.
5. Keep README, ROADMAP, and CLI help text aligned with the live `_source`
   contract.
6. Add smoke checks for optional external providers when the environment is
   available.
7. Keep the fixed validation slice and StepView as the standard regression
   surfaces.
