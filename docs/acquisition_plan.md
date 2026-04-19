## Acquisition Refactor Plan

This document maps the acquisition-quality refactor onto concrete modules, CLIs,
and fixtures inside `paperx`.

### Goals

- choose an acquisition route before extraction and reconciliation
- measure acquisition quality directly instead of inferring it from downstream
  repairs
- separate acquisition decisions from document assembly
- make provider trials reproducible with fixture-backed benchmarks

### Package Map

Phase 1 and Phase 5 are implemented first.

- `pipeline/acquisition/routing.py`
  - cheap PDF signal inspection
  - route selection
  - recommended provider plans by route
- `pipeline/acquisition/benchmark.py`
  - benchmark manifest loading
  - provider artifact loading
  - gold annotation loading
  - task-level scoring and aggregate reporting
- `pipeline/acquisition/grobid_trial.py`
  - fixture-backed GROBID metadata/reference bakeoff
  - per-paper scoring and aggregate reporting
- `pipeline/acquisition/providers.py`
  - provider artifact adapters
  - GROBID TEI metadata/reference extraction
- `pipeline/acquisition/__init__.py`
  - public boundary for routing and benchmark helpers

Planned follow-on modules:

- `pipeline/acquisition/scoring.py`
  - document-level and page-level source scorecards
  - accept/reject thresholds for provider outputs
- `pipeline/acquisition/ocr_policy.py`
  - pre-pass routing for scanned and degraded PDFs
- `pipeline/acquisition/source_ownership.py`
  - provider ownership by output product such as metadata, layout,
    references, math, and tables

### CLI Map

Phase 1 and Phase 5 CLIs:

- `pipeline.cli.inspect_acquisition_route`
  - inspect one paper
  - optionally write `canonical_sources/acquisition-route.json`
- `pipeline.cli.run_acquisition_benchmark`
  - run a fixture-backed or corpus-backed benchmark manifest
  - emit a JSON report for provider comparison

Planned follow-on CLIs:

- `pipeline.cli.run_acquisition_bakeoff`
  - compare multiple providers over a shared manifest and cost budget
- `pipeline.cli.audit_acquisition_quality`
  - summarize route distributions, score distributions, and rejection causes

### Fixture Map

Phase 5 fixture set:

- `tests/fixtures/acquisition_benchmark/manifest.json`
  - benchmark manifest
- `tests/fixtures/acquisition_benchmark/gold/*.json`
  - task-oriented gold annotations
- `tests/fixtures/acquisition_benchmark/providers/*/*.json`
  - provider artifact samples for deterministic scoring tests

Planned follow-on fixtures:

- `tests/fixtures/acquisition_routing/`
  - small route-specific PDFs or mocked signal bundles
- `tests/fixtures/acquisition_benchmark/corpus_samples/`
  - real corpus excerpts stratified by route type

### Rollout Order

1. Phase 1: route inspection and route sidecars.
2. Phase 5: benchmark harness and provider comparison reports.
3. Phase 2: source scorecards and provider acceptance thresholds.
4. Phase 3: GROBID trial and ownership decision for metadata and references.
5. Phase 4: OCR pre-pass policy.
6. Integration: replace heuristic composition with route-aware source
   ownership.

### Integration Notes

- `pipeline.orchestrator.round_sources` remains the current extraction entrypoint
  during the first pass.
- route inspection is intentionally additive at first so we can study decisions
  before changing runtime behavior.
- the benchmark harness is provider-artifact-based so new tools can be tested
  without wiring them into the main pipeline immediately.
