# ROADMAP

Status: active

This is the only live roadmap for `paperx`.

## Objective

Finish the extraction cleanly and make the current architecture boring to
operate:

- one clear path from source PDFs to canonical outputs
- one clear reset path back to source state
- no compatibility scaffolding or silent fallback behavior unless explicitly
  approved case by case
- enough higher-layer evidence that the architecture can be trusted without
  archaeology

## Non-Negotiables

- checked-in corpora stay in source state
- processed artifacts are local only
- fail fast is preferred over degraded work products
- the project venv is the default runtime surface
- root prose documentation stays limited to `README.md` and `ROADMAP.md`

## Current State

Already true:

- the engine is package-first under `pipeline/`
- corpora live under `corpus/`
- project mode and corpus mode share one layout model
- `run_project` is the forward lifecycle command
- `reset_corpus_to_source` is the reverse lifecycle command
- StepView is checked in as source PDFs only
- acquisition policy, audits, benchmarks, and remediation surfaces have first-
  class ownership under `pipeline.acquisition`
- the test tree is split into `unit`, `integration`, `e2e`, and `smoke`

Still incomplete:

- the densest reconcile helper and policy hubs still need simplification
- acquisition fixtures and route expectations still need more decision-grade
  coverage
- optional provider surfaces still deserve more real-environment smoke checks
- the remaining codebase still contains some finish-work cleanup beyond the
  already-pruned compatibility surface

## Finish Line

The repo is at the breakpoint when all of the following are true:

- the source-state corpus workflow is stable and unambiguous
- no new compatibility or fallback layers are being added by habit
- reconcile and orchestration seams are easy to trace end to end
- acquisition decisions are validated by fixtures and audits rather than manual
  memory
- unit, integration, and e2e suites stay green in `.venv-paperx`

## Workstreams

### 1. Reconcile Density Reduction

Primary target:

- keep `pipeline.reconcile.entrypoint` as a public seam, not a logic sink
- continue shrinking the largest pure helper modules when touched

Main files:

- `pipeline/reconcile/front_matter_parsing.py`
- `pipeline/reconcile/text_repairs.py`
- `pipeline/reconcile/section_filters.py`
- `pipeline/reconcile/block_merging.py`
- `pipeline/reconcile/runtime_deps.py`

Definition of done:

- helper ownership is obvious
- wrappers only exist when they bind real state or real dependencies
- tracing one paper through reconcile no longer requires runtime spelunking

### 2. Acquisition Quality And Policy

Primary target:

- make provider choice, OCR policy, and remediation decisions evidence-driven

Main files:

- `pipeline/acquisition/routing.py`
- `pipeline/acquisition/scoring.py`
- `pipeline/acquisition/providers.py`
- `pipeline/acquisition/ocr_policy.py`
- `pipeline/acquisition/audit.py`
- `pipeline/acquisition/policy_feedback.py`

Definition of done:

- route reasons are explicit
- OCR decisions are benchmarked rather than inferred from anecdotes
- remediation is exceptional instead of routine

### 3. Lifecycle And Higher-Layer Validation

Primary target:

- keep the whole source-to-processed-to-source loop trustworthy

Main surfaces:

- `pipeline/cli/run_project.py`
- `pipeline/cli/reset_corpus_to_source.py`
- `pipeline/cli/build_canonical.py`
- `pipeline/cli/build_review.py`
- `tests/e2e/**`
- `tests/integration/**`

Definition of done:

- project mode remains covered by subprocess e2e tests
- the strict lifecycle contract is protected by integration tests
- breakage shows up in CI before it becomes operator folklore

### 4. Corpus And Fixture Hygiene

Primary target:

- keep checked-in corpora and fixtures honest and small

Main surfaces:

- `corpus/stepview/`
- `tests/fixtures/acquisition_benchmark/`
- `tests/fixtures/grobid_trial/`
- `docs/fixed_validation_slice.json`

Definition of done:

- StepView stays source-only in Git
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
2. Continue reducing density in the largest reconcile helper modules.
3. Expand acquisition fixtures around OCR routing, provider choice, and failure
   cases.
4. Add smoke checks for optional external providers when the environment is
   available.
5. Keep the fixed validation slice and StepView as the standard regression
   surfaces.
