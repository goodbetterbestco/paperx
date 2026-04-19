# Testing Audit

Date: 2026-04-18

Status: active baseline

Related:

- [`docs/testing_standards.md`](./testing_standards.md)

## Scope

This audit reviews the current repository test suite and classifies each test
file by what it actually does today.

Important current-state note:

- the repo now has `tests/unit/`, `tests/integration/`, `tests/e2e/`, and
  `tests/smoke/`
- this audit drove the first taxonomy pass that split former
  `tests/integration/` files into honest `unit` and `integration` locations
- `tests/e2e/` now has its first true subprocess-driven CLI test
- `tests/smoke/` still exists as a placeholder only

The suite is more honestly labeled now, but higher-layer coverage is still
thin.

## Coverage Baseline

Coverage was measured on 2026-04-18 with Python's stdlib `trace` tool because
`coverage.py` is not installed in this repo and there is no existing coverage
config file.

Command used:

```bash
python3 -m trace --count --summary --missing \
  --coverdir tmp/tracecov \
  --ignore-dir '/opt/homebrew,/Library/Frameworks' \
  --ignore-module unittest,argparse,tempfile,json,urllib,http,ssl,subprocess,multiprocessing,concurrent,threading,logging,tokenize,linecache,inspect,dataclasses,pathlib,typing,traceback,contextlib,collections,enum,re,pprint,shlex,base64,binascii,hashlib,math,statistics,random,email,importlib,_pytest \
  --module unittest discover -s tests/integration/pipeline -p '*_test.py'
```

Result:

- `353` tests passed
- weighted `pipeline/*` line coverage: `64.1%`
- simple average across traced `pipeline/*` modules: `69.7%`
- traced pipeline modules: `128`
- modules under `50%`: `23`
- modules under `60%`: `34`

Family-level coverage:

- `pipeline.figures`: `16.9%`
- `pipeline.orchestrator`: `43.8%`
- `pipeline.sources`: `46.9%`
- `pipeline.assembly`: `52.4%`
- `pipeline.reconcile`: `67.7%`
- `pipeline.cli`: `71.5%`
- `pipeline.output`: `71.6%`
- `pipeline.text`: `76.7%`
- `pipeline.corpus`: `78.7%`
- `pipeline.math`: `79.3%`

Lowest-covered modules:

- `pipeline.orchestrator.assemble_document`: `2.0%`
- `pipeline.assembly.section_builder`: `4.3%`
- `pipeline.orchestrator.paper_reconciler`: `4.4%`
- `pipeline.output.audit_report`: `5.2%`
- `pipeline.orchestrator.normalize_records`: `8.6%`
- `pipeline.figures.linking`: `12.9%`
- `pipeline.sources.pdftotext_overlay`: `16.4%`
- `pipeline.sources.layout`: `17.6%`
- `pipeline.sources.figures`: `24.6%`
- `pipeline.sources.mathpix`: `45.1%`

## Current Suite Summary

Current inventory:

- `45` test files
- `353` test cases

Current file-level classification:

- `28` files / `272` tests are real hermetic behavior tests
- `6` files / `18` tests are real filesystem integration tests
- `11` files / `63` tests are contract or seam-heavy tests

Interpretation:

- the core logic layer is in better shape than the directory names imply
- the top of the pyramid is missing
- several tests currently called "integration" are better understood as unit or
  contract tests

## File Classification

Legend:

- `unit/behavior`: real production logic, mostly hermetic
- `unit/contract`: boundary or payload shape test with intentional seams
- `integration/behavior`: multiple real modules with real filesystem or
  artifact flow
- `integration/contract`: cross-module contract test that still uses seam
  patching

| File | Actual type | Proposed destination | Notes |
|---|---|---|---|
| `audit_corpus_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real heuristic behavior with minimal seams |
| `block_builder_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Large real behavior surface |
| `cli_helper_test.py` | `unit/contract` | `tests/unit/pipeline/` | Mostly argument threading and file-target contracts |
| `compile_formulas_test.py` | `unit/contract` | `tests/unit/pipeline/` | Backend seam contract, not real compilation integration |
| `config_test.py` | `unit/contract` | `tests/unit/pipeline/` | Env/runtime capability contract |
| `corpus_layout_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real project filesystem normalization |
| `corpus_metadata_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real corpus discovery behavior |
| `display_math_suppression_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real logic tests |
| `docling_adapter_test.py` | `unit/contract` | `tests/unit/pipeline/` | Docling seam and transformation contract, not live Docling |
| `document_policy_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real renderer/policy behavior |
| `external_math_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real matching and geometry behavior |
| `extract_math_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real math extraction behavior |
| `figure_caption_policy_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure policy tests |
| `formula_diagnostics_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure behavior |
| `formula_semantic_ir_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure behavior |
| `formula_semantic_policy_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure behavior |
| `front_matter_parsing_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure logic |
| `front_matter_policies_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure policy |
| `front_matter_recovery_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real behavior across recovery helpers |
| `front_matter_selector_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure selector logic |
| `front_matter_support_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure helper behavior |
| `heading_promotion_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure promotion logic |
| `helper_layout_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real filesystem/layout, but figure path uses stubbed `fitz` |
| `layout_io_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real file targets; output rendering/validation still patched |
| `layout_merge_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure merge logic |
| `layout_records_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real record behavior |
| `link_figures_test.py` | `unit/contract` | `tests/unit/pipeline/` | Not true figure-linking integration; `fitz` is stubbed |
| `math_entry_policies_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure policy logic |
| `math_fragments_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure helper logic |
| `math_review_policy_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure policy logic |
| `mathpix_adapter_test.py` | `unit/contract` | `tests/unit/pipeline/` | Transport and payload shape; no live Mathpix |
| `normalize_layout_test.py` | `unit/contract` | `tests/unit/pipeline/` | Layout-binding contract with patched seams |
| `output_helper_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real files and outputs |
| `reconcile_blocks_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Main logic safety net |
| `reconcile_postprocess_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure behavior |
| `render_review_from_canonical_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real render behavior |
| `root_boundary_test.py` | `integration/contract` | `tests/integration/pipeline/` | Architectural invariant, not behavioral integration |
| `run_corpus_rounds_test.py` | `integration/contract` | `tests/integration/pipeline/` | Important orchestration contract, but seam-heavy |
| `runtime_paths_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure helper behavior |
| `script_layout_test.py` | `integration/contract` | `tests/integration/pipeline/` | CLI wrapper contract, not true e2e |
| `section_preparation_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure behavior |
| `section_support_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Pure helper behavior |
| `source_resolution_test.py` | `unit/contract` | `tests/unit/pipeline/` | State-population contract via injected collaborators |
| `staleness_policy_test.py` | `integration/behavior` | `tests/integration/pipeline/` | Real metadata and file fingerprints |
| `text_repairs_test.py` | `unit/behavior` | `tests/unit/pipeline/` | Real repair behavior |

## Gaps Against The Standard

### Missing Real Higher-Layer Coverage

Current higher-layer status:

- `tests/e2e/` has one true subprocess-driven CLI test for
  `pipeline.cli.render_review_from_canonical`
- `tests/smoke/` has no real coverage yet

The biggest remaining structural gap is the lack of breadth in e2e coverage
and the absence of any real smoke coverage.

### Mislabeling

Most seam-heavy tests currently live under `tests/integration/` even when they
are better understood as:

- unit contract tests
- integration contract tests

That mislabeling makes the suite sound more realistic than it currently is.

### External Reality Gaps

These paths do not yet have real-environment coverage:

- Docling execution
- PyMuPDF-backed figure extraction and figure linking
- macOS Vision OCR bridge
- live Mathpix integration
- actual CLI subprocess execution for user-facing commands

## Recommended Pass Order

### Pass 1: Honest Taxonomy

Status:

- completed on 2026-04-18

Goal:

- create `tests/unit/`, `tests/integration/`, `tests/e2e/`, and `tests/smoke/`
- move the current files into the layer they actually belong in
- do not weaken or rewrite the tests yet

Outcome:

- the suite becomes honest immediately
- future gaps are easier to see

### Pass 2: Add True E2E

Status:

- started on 2026-04-19 with a real subprocess-driven test for
  `pipeline.cli.render_review_from_canonical`

Add subprocess-based e2e tests for a tiny fixture project covering:

- `python -m pipeline.cli.run_project`
- `python -m pipeline.cli.build_review`
- `python -m pipeline.cli.build_canonical`

At least one test should assert real artifact paths and exit status without
patching internal helpers.

### Pass 3: Add Smoke Coverage For Optional Integrations

Add gated smoke tests for:

- PyMuPDF figure path
- Docling CLI
- macOS Vision OCR helper
- live Mathpix when credentials are present

These should be opt-in and tiny.

### Pass 4: Raise Coverage In Low-Coverage Families

Priority order:

1. `pipeline.orchestrator`
2. `pipeline.figures`
3. `pipeline.sources`
4. `pipeline.assembly`

Suggested targets for the first improvement wave:

- cover real document assembly flow
- cover more real figure-linking behavior
- cover `pdftotext` and source-composition paths
- cover assembly helpers that are barely exercised today

## Immediate Next Actions

The next concrete repository changes should be:

1. add a second true e2e around `pipeline.cli.build_review` or `pipeline.cli.build_canonical`
2. add one gated smoke test skeleton for an optional real integration
3. attack the lowest-covered orchestrator and figures modules with real tests
4. rerun traced coverage after the next e2e and first smoke addition
