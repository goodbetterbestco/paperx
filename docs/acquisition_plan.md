# Acquisition Finalization Roadmap

This document is the current work-sequenced implementation roadmap for
finalizing the acquisition-quality program and the remaining architecture work
around it.

The plan is organized into three tracks:

- acquisition capability
- benchmark and gold fixtures
- internal reconcile simplification

The operating rule is simple: each work cycle should end in measurable
improvement to real corpus outcomes, not only cleaner internals or better
dashboards.

## Current State

The repository is now in a strong package-first shape:

- stable root boundary files remain directly under `pipeline/`
- implementation lives under package families such as `pipeline.acquisition`,
  `pipeline.orchestrator`, `pipeline.reconcile`, and `pipeline.assembly`
- user-facing entrypoints are centered in `pipeline.cli`

The acquisition-quality operator surface is now implemented end to end:

- routing and scoring live in `pipeline.acquisition.routing` and
  `pipeline.acquisition.scoring`
- OCR pre-pass policy lives in `pipeline.acquisition.ocr_policy`
- GROBID trial support lives in `pipeline.acquisition.grobid_trial`
- acquisition benchmarking, comparison, status, dashboard, history, and trend
  all exist under `pipeline.acquisition` and `pipeline.output`
- remediation queue execution, prioritization, artifacts, status, history,
  dashboard, wave planning, saved-wave execution, plan reconciliation, and
  backlog execution are all implemented

What remains is to convert this strong operator framework into stronger live
acquisition behavior and to simplify the densest remaining internals.

## Phase 0: Baseline Freeze

Before the three tracks branch, capture one shared baseline.

### Commands

```bash
python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --label baseline-finalization
python3 -m pipeline.cli.show_acquisition_benchmark_status --from-artifacts
python3 -m pipeline.cli.show_acquisition_benchmark_dashboard --from-artifacts

python3 -m pipeline.cli.audit_acquisition_quality --top 50
python3 -m pipeline.cli.plan_acquisition_remediation_waves --label finalization-baseline
python3 -m pipeline.cli.show_acquisition_remediation_plan_status
```

### Artifacts To Preserve

- `tmp/acquisition_benchmark/history/baseline-finalization.json`
- `tmp/acquisition_remediation_plans/history/finalization-baseline.json`

### Do This Next

- write a short baseline note under `docs/` summarizing benchmark status and
  remediation pressure
- choose the corpus slice that will be used repeatedly for real validation

## Track 1: Acquisition Capability

Goal: improve live extraction decisions so the system needs less downstream
repair and less remediation.

### Step 1.1: Centralize Provider Decision Policy

Primary modules:

- `pipeline/acquisition/routing.py`
- `pipeline/acquisition/scoring.py`
- `pipeline/acquisition/ocr_policy.py`
- `pipeline/acquisition/providers.py`
- `pipeline/orchestrator/resolve_sources.py`
- `pipeline/orchestrator/round_sources.py`

Deliverable:

- one explicit decision table for route selection, fallback ordering, and OCR
  escalation
- removal of duplicated provider-choice logic from orchestration code

Working commands:

```bash
python3 -m pipeline.cli.inspect_acquisition_route <paper-id>
python3 -m pipeline.cli.inspect_acquisition_scorecard <paper-id>
python3 -m pipeline.cli.audit_acquisition_quality --top 20
```

Fixtures to add:

- `tests/fixtures/acquisition_benchmark/routing/`
- born-digital clean PDF case
- scan-like PDF with sparse embedded text
- bad embedded text but recoverable OCR case
- figure-dense paper case
- math-heavy paper case
- reference-heavy paper case

Do this next:

- add `route_reason_codes` expectations to benchmark fixtures
- add tests that assert why a provider was selected, not only which provider
  was selected
- move hidden provider heuristics out of orchestrator code and into
  acquisition-policy modules

### Step 1.2: Tighten OCR Pre-Pass Policy

Primary modules:

- `pipeline/acquisition/ocr_policy.py`
- `pipeline/sources/ocrmypdf.py`
- `pipeline/acquisition/audit.py`

Deliverable:

- OCR decisions driven by explicit evidence such as text sparsity, scan
  indicators, layout corruption, and known provider failure patterns

Working commands:

```bash
python3 -m pipeline.cli.backfill_acquisition_sidecars
python3 -m pipeline.cli.audit_acquisition_quality --top 25
python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --label ocr-policy-candidate
```

Fixtures to add:

- `acquisition-execution.json` sidecars for OCR-required and OCR-forbidden
  cases
- cases where OCR would be harmful, not only helpful

Do this next:

- add benchmark assertions for false-positive OCR and false-negative OCR
- add remediation reason codes that distinguish "OCR should have been run" from
  "OCR was run unnecessarily"

### Step 1.3: Make GROBID An Intentional Policy Choice

Primary modules:

- `pipeline/acquisition/grobid_trial.py`
- `pipeline/acquisition/providers.py`
- `pipeline/acquisition/routing.py`

Deliverable:

- a clear decision to either integrate GROBID into live policy or keep it
  trial-only with that boundary documented

Working commands:

```bash
python3 -m pipeline.cli.run_grobid_trial --manifest tests/fixtures/grobid_trial/manifest.json
python3 -m pipeline.cli.compare_acquisition_benchmark --base previous --candidate latest
```

Fixtures to add:

- metadata-heavy papers
- bad reference extraction papers
- front-matter-weak papers

Do this next:

- add a benchmark family for "GROBID worth it / not worth it"
- write down the live-routing decision after the trial instead of leaving it
  implicit

### Step 1.4: Close The Loop From Failure To Better Defaults

Primary modules:

- `pipeline/acquisition/remediation_trend.py`
- `pipeline/acquisition/remediation_plan_status.py`
- `pipeline/acquisition/benchmark_trend.py`

Deliverable:

- a clear mapping from repeated remediation failures to recommended policy
  changes

Working commands:

```bash
python3 -m pipeline.cli.summarize_acquisition_remediation_trend
python3 -m pipeline.cli.show_acquisition_remediation_plan_dashboard
python3 -m pipeline.cli.summarize_acquisition_benchmark_trend
```

Do this next:

- add a report grouping recurring remediation failures by recommended policy
  action
- add a "top recurring routing mistakes" section to the benchmark or
  remediation dashboard

## Track 2: Benchmark And Gold Fixtures

Goal: make the benchmark system strong enough to guide real engineering
decisions and eventually gate regressions.

### Step 2.1: Expand Fixture Taxonomy

Primary modules:

- `pipeline/acquisition/benchmark.py`
- `pipeline/acquisition/benchmark_reports.py`
- `pipeline/output/acquisition_benchmark_report.py`

Fixture roots:

- `tests/fixtures/acquisition_benchmark/`
- `tests/fixtures/grobid_trial/`

Subgroups to add or clarify:

- `routing/`
- `ocr/`
- `metadata/`
- `references/`
- `layout/`
- `math/`
- `mixed/`

Do this next:

- normalize fixture naming conventions so the tested family is obvious from the
  path
- add one manifest section per failure class, not only per provider

### Step 2.2: Strengthen Expected Outcomes

Each benchmark fixture should ideally declare:

- expected route or provider
- expected OCR yes or no
- acceptable selected-provider set when more than one outcome is valid
- minimum metadata, reference, layout, or math quality floor
- expected remediation absence or presence for pathological cases

Primary files:

- `tests/fixtures/acquisition_benchmark/manifest.json`
- acquisition fixture JSONs
- `acquisition-execution.json` sidecars

Working commands:

```bash
python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --format markdown
python3 -m pipeline.cli.compare_acquisition_benchmark --base baseline-finalization --candidate latest
```

Do this next:

- audit every existing fixture for whether it tests real behavior or only the
  happy path
- add a fixture quality checklist to `docs/testing_audit.md` or a sibling file

### Step 2.3: Promote Stable Families To Gates

Primary modules:

- `pipeline/acquisition/benchmark_status.py`
- `pipeline/acquisition/benchmark_dashboard.py`
- `pipeline/acquisition/benchmark_compare.py`

Deliverable:

- soft gates first
- hard gates later for the most stable acquisition families

Do this next:

- define soft regression thresholds per family
- add a CLI or CI-facing summary that exits nonzero on gated regressions
- start with routing and OCR families before more semantic families

### Step 2.4: Add Real Corpus-Sampled Gold Cases

Goal:

- complement synthetic fixtures with a small curated set of real corpus papers

Sources:

- selected papers from `corpus/`
- papers already known to be problematic from remediation history

Do this next:

- create a small fixed "gold sample" corpus slice
- add expected acquisition outcome sidecars beside those sample fixtures
- rerun this slice after each major routing or OCR change

## Track 3: Internal Reconcile Simplification

Goal: reduce the cognitive load and density of the normalization core without
losing behavior.

### Step 3.1: Document The Reconcile Stage Map

Primary modules:

- `pipeline/reconcile/entrypoint.py`
- `pipeline/reconcile/stage_runtime.py`
- `pipeline/reconcile/runtime_deps.py`

Deliverable:

- one stage-by-stage map of reconcile flow
- one line per stage describing purpose, primary module, and main outputs

Do this next:

- add a short reconcile design note under `docs/`
- identify the top five densest files by responsibility and import surface

### Step 3.2: Collapse Unnecessary Runtime Indirection

Hotspot modules to inspect first:

- `pipeline/reconcile/runtime_deps.py`
- `pipeline/reconcile/runtime_builders.py`
- `pipeline/reconcile/layout_records.py`
- `pipeline/reconcile/layout_records_runtime.py`
- `pipeline/reconcile/math_fragments.py`
- `pipeline/reconcile/math_fragments_runtime.py`
- `pipeline/reconcile/text_repairs.py`
- `pipeline/reconcile/text_repairs_runtime.py`

Deliverable:

- fewer runtime wrappers that only forward arguments
- explicit justification for the layers that remain

Do this next:

- mark each runtime or policy pair as keep, merge, or rename
- start with a single pair, prove the simplification pattern, then continue

### Step 3.3: Separate Policy From Plumbing

Policy-oriented modules:

- `pipeline/reconcile/front_matter_policies.py`
- `pipeline/reconcile/math_entry_policies.py`
- `pipeline/reconcile/section_filters.py`

Runtime-oriented modules:

- `pipeline/reconcile/stage_runtime.py`
- `pipeline/reconcile/record_runtime.py`
- `pipeline/reconcile/text_runtime.py`

Deliverable:

- heuristics live in policy modules
- orchestration lives in runtime modules
- narrower, more meaningful unit tests

Do this next:

- move embedded heuristics out of runtime files when touched
- add narrow tests for extracted policy functions rather than relying only on
  broad end-to-end tests

### Step 3.4: Re-Audit Ownership Between Reconcile, Assembly, And Orchestrator

Primary seams:

- `pipeline/orchestrator/normalize_records.py`
- `pipeline/orchestrator/paper_reconciler.py`
- `pipeline/orchestrator/assemble_document.py`
- `pipeline/assembly/canonical_builder.py`

Deliverable:

- clean ownership boundaries between normalization, reconciliation, canonical
  assembly, and output rendering

Do this next:

- audit whether orchestrator modules are doing hidden domain policy work
- push content decisions downward into reconcile or assembly where appropriate

## Recommended Cross-Track Sequence

This is the recommended execution order:

1. benchmark hardening sprint
   - Track 2, Steps 2.1 and 2.2
2. routing and OCR sprint
   - Track 1, Steps 1.1 and 1.2
3. GROBID decision sprint
   - Track 1, Step 1.3
4. policy feedback sprint
   - Track 1, Step 1.4
5. reconcile simplification sprint
   - Track 3, Steps 3.1 through 3.3
6. ownership cleanup sprint
   - Track 3, Step 3.4

## Immediate Backlog

If only the next ten highest-value tickets are taken, do them in this order:

1. expand `tests/fixtures/acquisition_benchmark/` with routing and OCR taxonomy
2. add explicit route and OCR expectations to benchmark fixtures
3. centralize provider-choice logic in `pipeline.acquisition`
4. tighten `pipeline/acquisition/ocr_policy.py` using benchmark-driven cases
5. run a new labeled benchmark and compare it with the frozen baseline
6. decide whether GROBID joins live routing or remains trial-only
7. add a remediation-to-policy report grouping recurring failure causes
8. write the reconcile stage map document
9. simplify one reconcile runtime or policy pair end to end
10. rerun the validation corpus slice and compare benchmark deltas, remediation
    queue size, plan backlog size, and operator alerts

## Definition Of Done

The roadmap is considered complete when:

- benchmark fixtures are rich enough to trust
- routing, OCR, and provider selection improve on real corpus behavior
- remediation is more exceptional and less routine
- reconcile is understandable without deep runtime spelunking
- the README and operator commands reflect the final working model rather than
  a transition state
