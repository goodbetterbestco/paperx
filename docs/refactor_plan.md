# Pipeline Refactor Plan

Date: 2026-04-18

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

Phase 1 root deprecation status:

- the obvious family wrappers in `pipeline/` are now deprecated by architecture and annotated as such in-module
- this phase is documentation-only on purpose: no runtime warnings yet, no import-path breakage yet
- the currently annotated deprecated root wrappers are:
  `corpus_metadata.py`, `lexicon.py`, `build_corpus_lexicon.py`, `extract_math.py`, `math_review_policy.py`, `formula_diagnostics.py`, `formula_semantic_ir.py`, `formula_semantic_policy.py`, `mathml_compiler.py`, `compile_formulas.py`, `extract_layout.py`, `extract_pdftotext.py`, `extract_figures.py`, `external_sources.py`, `docling_adapter.py`, `mathpix_adapter.py`, `document_policy.py`, `figure_labels.py`, `figure_linking.py`, and `validate_canonical.py`
- the same is now true for the thin root command shims that already delegate into `pipeline.cli.*` or `pipeline.output.*` helpers:
  `build_external_layout_from_pdftotext.py`, `build_external_sources_from_docling.py`, `build_external_sources_from_mathpix.py`, `compose_external_sources.py`, `export_titles_and_abstracts.py`, and `render_review_from_canonical.py`
- the next phase is to migrate remaining internal imports off the still-active root bridges before adding runtime deprecation warnings

Phase 2 migration status:

- internal package imports have now started moving off the still-active root bridges
- the first bridge-reduction slice is complete for `pipeline.text_utils`: package modules under `pipeline/sources/`, `pipeline/policies/`, `pipeline/math/`, `pipeline/reconcile/`, and `pipeline/corpus/` now import the owned helpers directly from `pipeline.text.headings` instead of the root `pipeline.text_utils` bridge
- `pipeline.pdftotext_overlay.py` and the old `pipeline.audit_corpus.py` implementation both moved off that bridge, leaving `pipeline.text_utils` as the remaining compatibility surface in that earlier migration slice
- the next bridge slice is now partially complete for `pipeline.output_artifacts`: internal root build scripts now import the owned `pipeline.output.artifacts` module directly, while `pipeline/run_corpus_rounds.py` intentionally remains on the root bridge because its tests patch that compatibility surface directly
- the normalization bridge seam is now resolved too: `pipeline.text.prose` owns the `zipf_frequency` patch seam directly, `pipeline.text.references` depends on that owner module directly, and `pipeline/reconcile_blocks.py` plus the remaining tests now import the owned text modules instead of the root `normalize_*` facades

Phase 3 removal status:

- the first actual root facade removals are now complete for wrappers that had no remaining runtime or test imports inside the repo:
  `mathml_compiler.py`, `extract_layout.py`, `extract_pdftotext.py`, `extract_figures.py`, `figure_labels.py`, and `validate_canonical.py`
- the next removal batch is complete for wrappers that had become test-only import facades and no longer carried distinct patch behavior:
  `document_policy.py`, `extract_math.py`, `math_review_policy.py`, `formula_diagnostics.py`, `formula_semantic_ir.py`, `formula_semantic_policy.py`, and `compile_formulas.py`
- the next library-facade batch is complete for root modules that no longer carried runtime behavior and whose callers now import the owned packages directly:
  `corpus_metadata.py`, `lexicon.py`, `external_sources.py`, and `build_corpus_lexicon.py`
- the figure-linking compatibility shim is now removed as well: tests and docs point directly at `pipeline.figures.linking`, and the root `figure_linking.py` facade is gone
- the next entrypoint cleanup batch is complete for root command shims whose supported surface now lives under `pipeline.cli.*` instead:
  `build_external_layout_from_pdftotext.py`, `build_external_sources_from_docling.py`, `build_external_sources_from_mathpix.py`, `compose_external_sources.py`, `export_titles_and_abstracts.py`, and `render_review_from_canonical.py`
- the output-artifact compatibility seam is now reduced into the owned module itself: `pipeline.output.artifacts` exposes the patch points that tests and `run_corpus_rounds.py` need, so the root `output_artifacts.py` wrapper is no longer necessary
- the text-heading compatibility shim is now removed as well: `pipeline.reconcile_blocks.py` and the remaining tests import directly from `pipeline.text.headings`, so `text_utils.py` is no longer needed
- the source-adapter compatibility wrappers are now removed as well: the adapter patch seams live on `pipeline.sources.docling` and `pipeline.sources.mathpix`, so `docling_adapter.py` and `mathpix_adapter.py` are no longer needed
- the pdftotext overlay implementation now lives under `pipeline.sources.pdftotext_overlay`, and the old root `pdftotext_overlay.py` file is removed because no test or runtime patch seam still depends on it
- the normalization compatibility wrappers are now removed as well: the test/runtime patch seam lives on `pipeline.text.prose.zipf_frequency`, so `normalize_prose.py` and `normalize_references.py` are no longer needed
- `pipeline.output.identity` now keeps the historical logical component ids for removed wrapper surfaces while fingerprinting the owned implementation files directly, so canonical metadata stays stable without keeping a root `pipeline_identity.py` helper around
- the same identity strategy now covers the removed math-family wrappers as well, so old logical component ids still resolve to the packaged implementations for fingerprinting

Current verification baseline:

- full integration suite passes
- latest result: `python3 -m unittest discover -s tests/integration/pipeline -p '*_test.py'`
- result: `Ran 352 tests in 2.100s OK`

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
- `pipeline/cli/build_external_layout_from_pdftotext.py`
- `pipeline/cli/build_external_sources_from_docling.py`
- `pipeline/cli/build_external_sources_from_mathpix.py`
- `pipeline/cli/compose_external_sources.py`
- `pipeline/cli/render_review_from_canonical.py`
- `pipeline/cli/export_titles_and_abstracts.py`
- `pipeline/cli/run_corpus_rounds.py`
- `pipeline/cli/run_project.py`
- other thin command wrappers

### Corpus

- `pipeline/corpus/metadata.py`
- `pipeline/corpus/lexicon.py`
- `pipeline/corpus/lexicon_builder.py`

### Math

- `pipeline/math/extract.py`
- `pipeline/math/review_policy.py`
- `pipeline/math/diagnostics.py`
- `pipeline/math/semantic_ir.py`
- `pipeline/math/semantic_policy.py`
- `pipeline/math/mathml.py`
- `pipeline/math/compile.py`

### Sources

- `pipeline/sources/layout.py`
- `pipeline/sources/pdftotext.py`
- `pipeline/sources/figures.py`
- `pipeline/sources/external.py`
- `pipeline/sources/docling.py`
- `pipeline/sources/mathpix.py`

Root wrappers still exist for compatibility:

- no adapter-specific root wrappers remain in this family; patch seams now live on the owned source modules directly

### Text

- `pipeline/text/prose.py`
- `pipeline/text/references.py`
- `pipeline/text/document_policy.py`

### Figures

- `pipeline/figures/labels.py`
- `pipeline/figures/linking.py`

Root wrappers still exist for compatibility:


### Orchestrator

Already extracted:

- `pipeline/orchestrator/resolve_sources.py`
- `pipeline/orchestrator/normalize_records.py`
- `pipeline/orchestrator/assemble_document.py`
- `pipeline/orchestrator/paper_reconciler.py`
- `pipeline/orchestrator/layout_merge.py`
- `pipeline/orchestrator/round_build.py`
- `pipeline/orchestrator/round_document.py`
- `pipeline/orchestrator/round_execution.py`
- `pipeline/orchestrator/round_mathpix.py`
- `pipeline/orchestrator/round_paper.py`
- `pipeline/orchestrator/round_reporting.py`
- `pipeline/orchestrator/round_runtime.py`
- `pipeline/orchestrator/round_settings.py`
- `pipeline/orchestrator/round_sources.py`
- `pipeline/orchestrator/source_composition.py`

Important current boundary:

- `pipeline/run_corpus_rounds.py` is still the stable patch/import surface for the round runner
- pure helper logic has now been split across runtime, paper-build, source-build, job-execution, Mathpix coordination, and reporting owner modules, while patch-sensitive coordination remains at the root intentionally

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

There is now a distinct `pipeline/output/` family and the root output wrapper layer has been removed; `pipeline.output.artifacts` is now the owned import and patch surface.

### 5. The refactor has stayed behavior-safe

The working pattern so far has been:

- move pure implementation first
- preserve root import paths as wrappers where patch seams matter
- only switch internal imports directly to packaged modules when test seams are not relying on the root names

That pattern has worked and should continue.

## Remaining Root-Level Hotspots

Largest remaining root files at the time of this update:

- `pipeline/run_corpus_rounds.py` — now a 172-line coordinator boundary
- `pipeline/corpus_layout.py` — now a 169-line boundary object module

Recently reduced:

- extracted audit implementation now lives in `pipeline/corpus/audit.py`
- extracted audit markdown rendering now lives in `pipeline/output/audit_report.py`
- extracted audit command flow now lives in `pipeline/cli/audit_corpus.py`, and the old root `pipeline/audit_corpus.py` shim is now removed after moving the integration coverage onto the owner module
- removed the now-unused root `pipeline/build_canonical.py` and `pipeline/build_review.py` shims after moving the remaining script-layout integration coverage onto `pipeline.cli.build_canonical` and `pipeline.cli.build_review`
- the remaining top-level helper-bundle assembly in `pipeline/reconcile_blocks.py` now routes through a single runtime-owned builder in `pipeline/reconcile/runtime_deps.py`, replacing several root-only bundle globals with one grouped handoff
- the next dependency-packaging seam is now moved too: `pipeline/reconcile/runtime_deps.py` owns the loader/binding/assembly bundle construction for `reconcile_paper_state`, so the root file no longer needs private `_make_reconcile_*deps()` helpers at all
- the remaining regex/token constants are owned by `pipeline/reconcile/runtime_constants.py`, and the integration suites now bind to those owner modules directly instead of reading them through `pipeline/reconcile_blocks.py`
- `pipeline/text_utils.py` — now a 34-line compatibility wrapper
- extracted heading/section helpers now live in `pipeline/text/headings.py`
- `pipeline/corpus_layout.py` — now a 169-line boundary object module
- extracted path/config-prep helpers now live in `pipeline/corpus/paths.py`
- `pipeline.corpus` now uses lazy exports so submodules can be reused without package-init cycles
- removed the root `pipeline/staleness_policy.py` compatibility shim after moving the remaining runtime/test imports onto `pipeline.output.fingerprints` and `pipeline.output.staleness`
- fingerprinting/build metadata helpers now live in `pipeline/output/fingerprints.py`
- staleness decision logic now lives in `pipeline/output/staleness.py`
- removed the unused root `pipeline/pdftotext_overlay.py`; its implementation now lives at `pipeline/sources/pdftotext_overlay.py`
- `pipeline/run_corpus_rounds.py` — now a 172-line coordinator/compatibility surface
- extracted runtime/status/env helpers now live in `pipeline/orchestrator/round_runtime.py`
- extracted paper-build/output helpers now live in `pipeline/orchestrator/round_paper.py`
- `pipeline/orchestrator/round_paper.py` now carries first-class defaults for source composition, output writing, existing-source inspection, and generated-abstract preservation, so those helper tests no longer need the root coordinator as an indirection layer
- extracted Docling/Mathpix source-building helpers now live in `pipeline/orchestrator/round_sources.py`
- `pipeline/orchestrator/round_sources.py` now carries first-class defaults for Docling source generation, Mathpix source generation, and per-paper extraction concurrency, so the root coordinator no longer needs its own source-builder wrapper stack
- extracted job/round execution helpers now live in `pipeline/orchestrator/round_execution.py`
- `pipeline/orchestrator/round_execution.py` now carries first-class defaults for staleness checks, source composition, paper building, status persistence, and queue scheduling, so round-queue behavior can be tested directly on the owner module instead of through the root coordinator
- extracted Mathpix round coordination now lives in `pipeline/orchestrator/round_mathpix.py`
- `pipeline/orchestrator/round_mathpix.py` now carries first-class defaults for its runtime clock and Mathpix API hooks, so the coordinator can be tested directly without a root subclass wrapper
- removed the root `pipeline/reconcile_blocks.py` facade after promoting the default `run_paper_pipeline` seam into `pipeline/reconcile/entrypoint.py`
- extracted record/text cleaning helpers now live in `pipeline/reconcile/text_cleaning.py`
- extracted reference-runtime helper composition now lives in `pipeline/reconcile/reference_runtime.py`
- extracted front-matter candidate/recovery helpers now live in `pipeline/reconcile/front_matter_runtime.py`
- extracted text normalization/reference runtime helper composition now lives in `pipeline/reconcile/text_runtime.py`
- extracted math policy/demotion runtime helper composition now lives in `pipeline/reconcile/math_runtime.py`
- extracted record/postprocess runtime helper composition now lives in `pipeline/reconcile/record_runtime.py`
- extracted runtime dependency bundle assembly now lives in `pipeline/reconcile/runtime_deps.py`
- extracted reconcile entrypoint composition now lives in `pipeline/reconcile/entrypoint.py`
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
- `audit_corpus.py` no longer needs to exist at the root; the supported surfaces are now `pipeline.corpus.audit` for implementation and `pipeline.cli.audit_corpus` for the command entrypoint
- `text_utils.py` has also been converted into the intended wrapper shape
- `corpus_layout.py` now better matches the intended boundary-object role
- the old `staleness_policy.py` bridge is now gone; runtime code and tests import the owned `pipeline.output.*` modules directly
- `run_corpus_rounds.py` now looks much more like an intentional coordinator after peeling off runtime/status/env helpers, paper-build/output helpers, source-build helpers, job execution, and Mathpix round coordination
- the remaining `run_corpus_rounds.py` helper names are increasingly true orchestration seams rather than test-only helper homes; the run-round integration coverage now exercises several owner modules directly instead of reaching through the root coordinator
- the round-execution queue tests now bind to `pipeline.orchestrator.round_execution` directly, which removed the last root-only coverage pressure around `_process_round(...)`
- the root `run_corpus_rounds.py` file is now mostly startup, round-loop orchestration, and CLI argument handling; the former source-builder and paper-job wrapper layers are gone
- the first coordinator-stage split is now in place: front-matter build, abstract recovery, and block-assembly binding moved behind `pipeline/reconcile/stage_runtime.py`
- that coordinator-stage extraction has now expanded to absorb normalization/postprocess binding closures as well, further reducing the inline orchestration burden inside `reconcile_paper_state`
- `reconcile_paper_state` no longer carries nested helper `def`s; it is now primarily factory composition plus the final `run_paper_pipeline(...)` orchestration call
- `reconcile_paper_state` now also carries zero inline lambdas; the root entrypoint is effectively a declarative coordinator over stage-runtime factories and `run_paper_pipeline(...)`
- `reconcile_paper_state` is now a minimal facade over `pipeline/reconcile/stage_runtime.py`, and `pipeline/reconcile/entrypoint.py` now owns the default `run_paper_pipeline` seam directly
- the old `pipeline/reconcile_blocks.py` wrapper is now gone; CLI/runtime callers and the remaining layout-binding integration coverage import `pipeline.reconcile.entrypoint` directly
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
- compatibility-facade removal has started in `pipeline/reconcile_blocks.py`: the dead root aliases for `_split_code_lines`, `_page_height_map`, `_match_external_math_entry`, `_rect_area`, and `_rect_intersection_area` were removed first because tests and runtime assembly no longer depend on those names directly
- a second dead-facade batch is gone too: `_record_bbox`, `_rect_x_overlap_ratio`, `_match_figure_for_caption_record`, `_record_union_bbox`, `_inline_tex_signal_count`, and `_token_subsequence_index` were removed from the root shell and replaced with direct runtime wiring at their remaining call sites
- the next internal-only facade batch is gone as well: `_strip_caption_label_prefix`, `_mathpix_hint_alignment_text`, `_mathpix_hint_tokens`, `_mathpix_text_candidate_score`, `_matching_mathpix_text_blocks`, and `_looks_like_truncated_prose_lead` were removed from the root shell because only local Mathpix/text-repair assembly still needed them
- the screening helper aliases `_looks_like_vertical_label_cloud`, `_looks_like_table_marker_cloud`, `_looks_like_browser_ui_scrap`, `_looks_like_quoted_identifier_fragment`, and `_looks_like_glyph_noise_cloud` were removed too, with `_is_short_ocr_fragment` now wiring those runtime builders directly at the call site
- another internal-only facade batch is gone: `_starts_like_strong_paragraph_continuation`, `_ends_like_short_lead_in`, `_ends_like_clause_lead_in`, `_is_paragraph_like_record`, `_merge_anchor_spans`, `_looks_like_same_page_column_continuation`, `_merge_native_and_external_layout`, and `_first_root_indicates_missing_intro` were removed from the root shell and replaced with direct inline wiring where still needed
- another shell-pruning batch is now gone too: `_normalize_figure_caption_text`, `_repair_record_text_with_pdftotext`, `_page_one_front_matter_records`, `_should_demote_prose_math_entry_to_paragraph`, `_merge_math_fragment_records`, `_is_title_page_metadata_record`, `_abstract_text_looks_like_metadata`, and `_split_trailing_reference_records` were removed from the root file because only adjacent constructor wiring or final runtime assembly still depended on them
- the remaining reference-only shell facades `_looks_like_reference_text` and `_merge_reference_records` are gone too; the reference-start, tail-section, Mathpix-reference, and final assembly bindings now compose those helpers directly instead of routing through extra root aliases
- the next step after facade removal has started too: the reference helper graph is now bound once in `pipeline/reconcile/reference_binding_runtime.py` and exposed back through the root test-facing names, which removes the duplicated inline reference wiring that the last facade-pruning pass temporarily created
- the same semantic cleanup has now started for front matter as well: the parsing/policy helper graph is bound once in `pipeline/reconcile/front_matter_parsing_runtime.py` and the root `_normalize_author_line`, `_looks_like_*`, `_parse_authors*`, `_normalize_affiliation_line`, `_dedupe_authors`, `_filter_front_matter_authors`, `_build_affiliations_for_authors`, and related test-facing names are now exported from that shared bundle instead of being assembled one closure at a time in `pipeline/reconcile_blocks.py`
- the front-matter support/recovery layer is now following the same pattern: `pipeline/reconcile/front_matter_runtime.py` now binds the title-line, record-support, abstract-recovery, and missing-intro helper graphs once, and `pipeline/reconcile_blocks.py` re-exports those stable `_title_lookup_keys`, `_matches_title_line`, `_record_*`, `_leading_abstract_text`, `_opening_abstract_candidate_records`, `_abstract_text_is_recoverable`, `_replace_front_matter_abstract_text`, and `_split_late_prelude_for_missing_intro` names from shared bundles instead of hand-partialing them inline
- the text-repair cluster now follows the same bundle pattern too: `pipeline/reconcile/text_repairs_runtime.py` now binds the pdftotext-skip/repair path plus the Mathpix hint-selection helpers once, and `pipeline/reconcile_blocks.py` re-exports `_should_skip_pdftotext_repair`, `_mathpix_text_blocks_by_page`, `_mathpix_text_hint_candidate`, `_mathpix_prose_lead_repair_candidate`, and `_is_mathpix_text_hint_better` from that shared bundle while loader assembly consumes the same bound pdftotext repair helper directly
- the remaining composition-root density in `pipeline/reconcile_blocks.py` is now reduced as well: `_make_reconcile_runtime_deps()` no longer spells out every loader, binding, and assembly dependency family inline, and instead delegates to `_make_reconcile_loader_deps()`, `_make_reconcile_binding_deps()`, and `_make_reconcile_assembly_deps()` so the stage boundary is easier to scan without freezing any patch-sensitive symbols at import time
- a follow-up dead-import sweep trimmed the stale runtime/factory aliases left behind by those extractions; the only root-level compatibility imports that had to stay despite looking unused locally were `reconcile_split_leading_front_matter_records` and `reconcile_looks_like_leading_display_math_echo`, which are still referenced directly by integration tests
- the root compatibility boundary is now explicit instead of accidental: `pipeline/reconcile_blocks.py` defines `__all__` from the currently exercised compatibility surface, which makes future cleanup safer because we can distinguish intended exports from incidental module leakage before removing or renaming anything
- the specialized front-matter support/parsing/policies integration tests no longer need to reach through `pipeline.reconcile_blocks` for most helper behavior; they now build the owning runtime helper bundles directly, leaving `reconcile_blocks_test.py` and the broader end-to-end integration suite as the main places that intentionally validate the root compatibility shell itself
- the same test-decoupling pattern now covers text repairs too: `tests/integration/pipeline/text_repairs_test.py` now builds the owning text-repair runtime bundle directly for Mathpix/pdftotext helper wiring instead of depending on `pipeline.reconcile_blocks` for that assembly logic
- the layout-records integration test now follows the same model: `tests/integration/pipeline/layout_records_test.py` builds the owning layout-record runtime helpers directly for page-one Mathpix/front-matter composition and figure-caption continuation absorption, instead of borrowing that helper wiring from `pipeline.reconcile_blocks`
- the heading-promotion integration test now does the same: `tests/integration/pipeline/heading_promotion_test.py` builds the owning heading-promotion runtime helpers directly for decoded-heading normalization and embedded-heading splitting, instead of relying on `pipeline.reconcile_blocks` to assemble those helper closures
- the math/postprocess-oriented integration suites are now starting to peel off the compatibility shell too: `external_math_test.py`, `math_fragments_test.py`, `reconcile_postprocess_test.py`, `math_entry_policies_test.py`, and `display_math_suppression_test.py` now assemble their own owner-module/runtime helpers for echo suppression, math-fragment grouping, paragraph-merge policy, and display-math demotion instead of reaching through `pipeline.reconcile_blocks` for those bound facades
- the `block_builder_test.py` harness now follows that same owner-runtime pattern: it binds its own cleaning, screening, reference-entry, external-math, and display-math suppression helpers locally before calling the assembly builder, so it no longer keeps the root `_clean/_record/_is_short/_make_reference_entry/_list_item_marker/_normalize_formula_display_text` facades alive just to exercise block assembly behavior
- the remaining smaller stragglers are shrinking too: `text_repairs_test.py` now binds its own OCR-fragment screening helper locally, and `layout_records_test.py` now imports Mathpix text-block grouping from `pipeline/reconcile/text_repairs_runtime.py` instead of borrowing those helpers from the root compatibility shell
- the front-matter selector/recovery seam is now following the same pattern: `front_matter_selector_test.py` and `front_matter_recovery_test.py` build the support/parsing/recovery helper bundles locally and route the assembly/selector calls through those owner-runtime bindings, which removes another large block of `_clean/_record/_matches/_parse/_leading_abstract/...` dependency traffic from the root compatibility shell
- `section_support_test.py` no longer needs the root-bound `_clean_text` or other simple support helpers either; it now binds clean-text locally and calls the section-support helpers with direct owner-module utilities, leaving `reconcile_blocks_test.py` as the main remaining integration suite that intentionally exercises the root compatibility helper surface
- `reconcile_blocks_test.py` now follows that owner-runtime pattern for most of its helper plumbing too: paragraph merge/suppression, heading promotion, layout/caption merging, text repair, front-matter recovery, reference extraction, OCR screening, and figure-debris checks are now bound locally from the owning runtime modules instead of importing the broad helper facade list from `pipeline.reconcile_blocks`
- with that suite narrowed, compatibility-facade deletion has resumed in `pipeline/reconcile_blocks.py`: the dead `_strip_trailing_abstract_boilerplate` and `_is_reference_start` aliases were removed because runtime assembly and the integration suite no longer depend on those root names directly
- a second dead-facade sweep then removed more root-only compatibility leftovers that were no longer consumed by tests or runtime deps: `_title_lookup_keys`, `_looks_like_page_one_front_matter_tail`, `_normalize_affiliation_line`, `_split_affiliation_fields`, and `_dedupe_authors` are gone from `pipeline/reconcile_blocks.py`, and `_append_figure_caption_fragment` was inlined into the caption-continuation binding instead of being kept as a standalone root helper export
- the root front-matter facade has now shrunk another step: support and recovery fields such as `_matches_title_line`, `_dedupe_text_lines`, `_clone_record_with_text`, `_record_word_count`, `_record_width`, `_should_replace_front_matter_abstract`, `_leading_abstract_text`, `_opening_abstract_candidate_records`, `_abstract_text_is_recoverable`, `_replace_front_matter_abstract_text`, and `_split_late_prelude_for_missing_intro` were removed in favor of wiring `_make_reconcile_*deps()` straight to the bound support/recovery helper bundles
- the same direct-bundle pattern now applies to most front-matter parsing helpers too: `_looks_like_author_line`, `_looks_like_contact_name`, `_looks_like_front_matter_metadata`, `_looks_like_intro_marker`, `_looks_like_body_section_marker`, `_normalize_abstract_candidate_text`, `_parse_authors`, `_parse_authors_from_citation_line`, `_normalize_author_line`, `_filter_front_matter_authors`, `_build_affiliations_for_authors`, `_strip_author_prefix_from_affiliation_line`, and `_looks_like_affiliation_continuation` are no longer exported from `pipeline/reconcile_blocks.py` because the reconcile deps now read them directly from `_front_matter_helpers`
- the reference helper layer has been reduced in the same style: `_make_reference_entry`, `_extract_reference_records_from_tail_section`, and `_reference_records_from_mathpix_layout` are no longer separate root aliases in `pipeline/reconcile_blocks.py`; the assembly/runtime deps now read those behaviors directly from the reference runtime/bound helper layer instead
- the section-filter/screening shell has started collapsing too: `_inject_external_math_records`, `_is_figure_debris`, `_is_short_ocr_fragment`, `_looks_like_running_header_record`, `_looks_like_table_body_debris`, `_suppress_embedded_table_headings`, and `_should_merge_paragraph_records` were removed as standalone root aliases, with `_make_reconcile_*deps()` now constructing those behaviors directly at the dep wiring sites instead of exporting another compatibility layer from `pipeline/reconcile_blocks.py`
- the remaining layout-helper alias layer has now followed that same pattern: `_layout_record`, `_figure_label_token`, `_synthetic_caption_record`, and `_absorb_figure_caption_continuations` are no longer root exports in `pipeline/reconcile_blocks.py`; the reference, layout-heading, and assembly dep constructors now call the layout runtime builders directly where those helpers are needed
- the heading/math-policy alias layer has started collapsing as well: `_decode_control_heading_label`, `_normalize_decoded_heading_title`, `_split_embedded_heading_paragraph`, `_starts_like_sentence`, `_group_entry_items_are_graphic_only`, `_math_entry_semantic_policy`, `_math_entry_category`, and the related math-policy helper aliases are no longer carried as standalone root exports when the deps can call the underlying runtime/binding constructors directly
- a fixed-string export audit then exposed a few root symbols that were not actually needed anymore despite earlier caution: the stale `reconcile_split_leading_front_matter_records` and `reconcile_looks_like_leading_display_math_echo` imports were removed, along with the dead `_normalize_paragraph_text` and `_should_skip_pdftotext_repair` compatibility globals
- the root compatibility surface has now tightened another step without changing runtime assembly: `pipeline/reconcile_blocks.py` no longer advertises internal-only helpers such as `_clean_text`, `_block_source_spans`, `_clean_record`, `_list_item_marker`, `_mathpix_*`, `_missing_front_matter_*`, `_normalize_formula_display_text`, `_record_analysis_text`, `_strong_operator_count`, or the internal math-suppression/external-math helpers through `__all__`; those names still exist where the runtime wiring needs them, but they are no longer part of the intended root export contract
- the last non-regex test-only compat hooks have now moved to their owner modules too: `front_matter_recovery_test.py` imports `default_review` from `pipeline.types`, and `reconcile_blocks_test.py` imports `collapse_ocr_split_caps` / `looks_like_bad_heading` from `pipeline.text.headings` plus `default_review` from `pipeline.types`, instead of reading those through `pipeline.reconcile_blocks`
- the front-matter regex bundle now has an owner module too: `pipeline/reconcile/front_matter_patterns.py` now holds the author/metadata/abstract/preprint/citation/funding pattern set, `pipeline/reconcile_blocks.py` imports those definitions instead of owning them inline, and the front-matter integration tests now bind against that owner module directly
- the remaining shared fixture bundle now has an owner too: `pipeline/reconcile/shared_patterns.py` holds the short-word, running-header, Procedia header, table-caption, display-math, and embedded-heading patterns, and the integration suites now bind against that module directly instead of borrowing those constants from `pipeline.reconcile_blocks`
- the last root fixture alias is now gone too: the remaining tests use `pipeline.policies.abstract_quality.MISSING_ABSTRACT_PLACEHOLDER` directly, so `pipeline/reconcile_blocks.py` no longer exports the placeholder either
- the root export contract is now fully orchestration-only in practice and in `__all__`: the import-aware audit shows only `reconcile_paper` and `reconcile_paper_state` as live external exports from `pipeline/reconcile_blocks.py`
- the first post-export density cleanup is now in too: `pipeline/reconcile_blocks.py` no longer keeps a leftover internal alias layer for front-matter missing-placeholder partials, text-repair helper fields, list-item/code-record helpers, or split-leading-front-matter forwarding; those values are now read directly from the owning helper bundles or constructed inline at the dep-wiring sites, which makes the composition block shorter and less wrapper-heavy
- the next internal-density seam is now starting to move behind an owner helper as well: `pipeline/reconcile/screening_runtime.py` now exposes `build_reconcile_screening_helpers(...)`, which binds the short-OCR, figure-debris, running-header, table-body, embedded-table-heading, and paragraph-merge screening family once; `pipeline/reconcile_blocks.py` now consumes that bundle instead of hand-constructing the same cluster inline across both binding and assembly dep builders
- the block-builder binding cluster now follows the same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_binding_block_builder_deps(...)`, which assembles the screening helper handoff plus the list-item and real-code-record binding helpers in one place; `pipeline/reconcile_blocks.py` now delegates that whole `block_builder_deps` tree to the owner builder instead of constructing those closures inline
- the math-policy binding cluster now follows that same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_binding_math_deps(...)`, which assembles the math-entry semantic policy/category wiring and `group_entry_items_are_graphic_only` helper in one place; `pipeline/reconcile_blocks.py` now delegates that whole `math_deps` tree to the owner builder instead of constructing those math-policy closures inline
- the layout/heading binding cluster now follows the same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_binding_layout_heading_deps(...)`, which assembles the nested layout-record, caption-continuation, external-math-injection, and heading-promotion binding helpers in one place; `pipeline/reconcile_blocks.py` now delegates that whole `layout_heading_deps` tree to the owner builder instead of spelling out every nested constructor inline
- the front-matter binding cluster now follows that same owner-side pattern: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_binding_front_matter_deps(...)`, which assembles the support/parsing/recovery helper bundle wiring plus the missing-author/missing-affiliation placeholder partials in one place; `pipeline/reconcile_blocks.py` now delegates the whole `front_matter_deps` tree to that owner builder instead of manually threading each front-matter field inline
- the shared bootstrap helper layer is now bundled owner-side too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_base_helpers(...)`, which binds the low-level clean-text, clean-record, running-header, formula-normalization, record-analysis, word-count, pdftotext-comparison, and math-signal helpers once; `pipeline/reconcile_blocks.py` now seeds the downstream screening, text-repair, front-matter, reference, binding, and assembly wiring from that explicit base-helper bundle instead of keeping a long list of separate module-scope helper globals
- the remaining screening helper cluster now follows that same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_screening_helper_bundle(...)`, which binds the short-OCR, figure-debris, running-header, table-body, embedded-table-heading, and paragraph-merge screening family from the shared base-helper bundle and screening patterns in one place; `pipeline/reconcile_blocks.py` now consumes that prepared screening bundle instead of constructing `_screening_helpers` directly, and the dead `_starts_like_paragraph_continuation` bootstrap leftover is gone
- the text-repair helper cluster now follows that same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_text_repair_helpers(...)`, which binds the pdftotext-repair and Mathpix-hint helper family from the shared base-helper bundle in one place; `pipeline/reconcile_blocks.py` now consumes that prepared text-repair bundle instead of constructing the `_text_repair_helpers` recipe inline
- the reference helper cluster now follows that same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_reference_helpers(...)`, which binds the reference-start, merge, trailing-tail extraction, and Mathpix-reference helper family from the shared base/text-repair inputs in one place; `pipeline/reconcile_blocks.py` now consumes that prepared reference bundle instead of constructing `_reference_helpers` directly
- the remaining front-matter helper cluster now follows that same owner-side pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_front_matter_helper_bundles(...)`, which binds the support, parsing, and recovery helper trio from the shared base-helper bundle and front-matter pattern inputs in one place; `pipeline/reconcile_blocks.py` now consumes that prepared front-matter helper bundle instead of constructing `_front_matter_support_helpers`, `_front_matter_helpers`, and `_front_matter_recovery_helpers` directly
- the first assembly-side constructor island is now behind an owner helper too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_assembly_record_prep_deps(...)`, which assembles the math-fragment merge helper and the page-one front-matter record builder together; `pipeline/reconcile_blocks.py` now consumes that prepared bundle instead of constructing those two nested assembly callables inline
- the adjacent assembly structure handoff is now behind an owner helper too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_assembly_structure_deps(...)`, which lifts the title-page metadata check, missing-intro/front-matter replacement hooks, and reference-tail extraction/merge helpers out of the shell; `pipeline/reconcile_blocks.py` now reads that whole front-matter/reference assembly cluster from one prepared bundle instead of addressing each bound helper field inline
- the remaining assembly-side screening/postprocess cluster now follows the same pattern too: `pipeline/reconcile/runtime_deps.py` now exposes `build_reconcile_assembly_postprocess_deps(...)`, which lifts the screening-helper handoff plus the paragraph/code merge and suppression/postprocess operations into one prepared bundle; `pipeline/reconcile_blocks.py` now reads that whole postprocess cluster from owner-side assembly deps instead of enumerating each screening and merge helper inline
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
- the old `pipeline/staleness_policy.py` bridge has now been removed after internal callers and tests moved to `pipeline.output.fingerprints` and `pipeline.output.staleness`

Next likely targets after `corpus_layout.py`:

- keep shrinking the remaining intentional root boundary files (`run_corpus_rounds.py` and `corpus_layout.py`) only when a clear owner-module seam appears
- otherwise focus on package-level cleanup and documentation alignment rather than inventing new compatibility layers

Plan:

- keep root adapters as compatibility surfaces while continuing to move implementation into `pipeline/sources/`

Success criteria:

- fewer medium-sized general-purpose root files
- cleaner separation between boundary objects and helper logic
- after this pass, the remaining prep work is considered sufficient to keep polishing the package-level boundaries without relying on new root facades

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
