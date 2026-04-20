# StepView Corpus

This directory is the canonical-first research corpus for the academic-paper
ingestion work and the StepView white-paper work.

The important shift is that the pipeline is no longer passage-first.
`passages.jsonl` is gone. The paper-owned source of truth is now
`canonical.json`, with every other paper view derived from it.

Today this corpus still lives in `docs/`, but it is being prepared to move to
`~/Projects/paperx/corpus/stepview/`. In that extracted shape, `paperx/` is the engine
repo root and `corpus/stepview/` is just this corpus, so other project corpora can
live alongside it in the future.

## Current Truth

- This corpus is meant to move between exactly two states: `source` and
  `processed`.
- In `source` state, the corpus root contains only the original paper PDFs plus
  repo-owned documentation.
- In `processed` state, each source PDF has been moved into its paper-owned
  folder, the local build artifacts live alongside it, and `_canon/` provides a
  top-level review surface across the whole corpus.
- Corpus quality is tracked through the canonical audit, not by ad hoc notes.

Processed working shape:

`root PDF -> <paper-id>/<paper-id>.pdf + canonical_sources + canonical.json + figures + _canon review output`

Current formula shape inside canonical:

`display_latex -> compiled_targets -> classification(category/policy/role) -> semantic_expr only for semantic formulas`

## What Lives Here

Root files:

- [README.md](./README.md)
  Corpus scope, working method, and paper-map guidance.
  Normalized citation and provenance layer for drafting and source tracking.
- [whitepaper-editorial-standards.md](./whitepaper-editorial-standards.md)
  Drafting standards for tone, notation, and evidence handling.
- `*.pdf`
  The source-state papers that are intended to be checked into Git.

Processed-state root artifacts:

- `_canon/<paper-id>.canonical.review.md`
  Human-readable review view derived from `canonical.json`.
- `figure_expectations.json`
  Corpus-owned figure completeness expectations used during processed-state
  figure regeneration and completeness auditing.
- `corpus_lexicon.json`
  Processed-state lexicon output built from the active canonicals.

Per-paper folders:

- `<paper-id>/<paper-id>.pdf`
  The source PDF after the corpus has been moved into processed state.
- `<paper-id>/canonical.json`
  Paper-owned structured extraction target.
- `<paper-id>/canonical_sources/`
  Engine-specific layout and math evidence.
- `<paper-id>/figures/`
  Processed-state figure assets.

## Where To Start

- [README.md](./README.md)
  Start here for corpus orientation and paper ownership rules.
- [Pipeline](../pipeline/README.md)
  Top-level architectural boundary for the ingestion system as it is prepared
  for extraction into its own repo.
- [pipeline/README.md](../pipeline/README.md)
  Canonical build contract, source adapters, formula policy, and audit seam.

If you are answering a question about one paper:

1. Open that paper's `canonical.json`.
2. Inspect `canonical_sources/` if you need to understand a bad block or
   formula.
3. Open the PDF when canonical output or figure extraction is still doubtful.

## Corpus State

The checked-in repo copy should stay in `source` state. Local processing moves
the corpus into `processed` state, and `python -m pipeline.cli.reset_corpus_to_source`
returns it to the source-only layout for check-in.

What is materially true right now:

- there are `58` source papers in this corpus
- the canonical pipeline is the active ingestion surface once the corpus is in
  processed state
- `_canon/` is the top-level review surface for processed output
- formula work is now policy-gated:
  only a minority of formulas are treated as semantic objects
- the live parser queue should be taken from the audit report, not from stale
  handwritten priority lists

To generate the current corpus-quality report:

```bash
python3 -m pipeline.cli.audit_corpus --top 12
```

This writes:

- `tmp/canonical_corpus_audit/summary.md`
- `tmp/canonical_corpus_audit/summary.json`

The audit is the current queue source for parser work. It measures, among other
things:

- canonical coverage
- conversion coverage for display math
- formula diagnostics
- formula classification and semantic-policy coverage
- semantic IR coverage
- fragmented prose and section-structure issues
- figure/reference completeness

## Formula Policy

Canonical math is no longer treated as one undifferentiated pool.

Every formula may be annotated with:

- `classification.category`
- `classification.semantic_policy`
- `classification.role`
- `semantic_expr` when policy allows it

High-level split:

- `semantic`
  Eligible for machine-usable interpretation.
- `structure_only`
  Preserve shape, ordering, or notation, but do not treat as a reusable
  mathematical fact.
- `graphic_only`
  Render and retain provenance only.

Current important roles:

- semantic roles:
  `assertion`, `definition`, `condition`, `update_step`, `objective`
- structure-only roles:
  `notation_binding`, `derivation_step`, `structural`
- graphic roles:
  `graphic`, `unknown`

This matters because many formulas that look "mathy" are not the right targets
for semantic work:

- inline `\mathbb{R}^{d}` or `C^{1}` is usually `notation_binding`
- `:=` definitions are semantic, but they are not iterative `update_step`s
- chained equalities inside a proof are usually `derivation_step`
- matrices and piecewise displays are `structural`
- most inline notation is `graphic_only`

So the live semantic work is intentionally narrower than "all formulas."

## Program Map

The current program is still the same six-stage mathematical program:

1. topology-preserving AP242 / B-Rep ingestion
2. exact local trimmed-face predicates and intersection queries
3. characteristic-curve generation on owned or explicitly named proxy models
4. event-aware splitting at cusps, trim events, image intersections, and
   visibility changes
5. visibility classification with a stable view graph, region graph, or
   propagation object
6. correct-resolution display or export of the resulting curves

Implementation-first reading order:

1. `2026_topology_first_brep_meshing`
2. `2018_trimming_in_isogeometric_analysis_review`
3. `2026_robust_tessellation_without_self_intersections`
4. `1990_curve_intersection_using_bezier_clipping`
5. `1990_ray_tracing_trimmed_rational_surface_patches`
6. `2000_practical_ray_tracing_trimmed_nurbs_surfaces`
7. `2019_line_drawings_from_3d_models`
8. `1990_hidden_curve_removal_for_free_form_surfaces`
9. `2001_curve_evaluation_and_interrogation_on_surfaces`
10. `2000_partitioning_trimmed_spline_surfaces_visibility`
11. `1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces`
12. `2014_smooth_surface_contours_accurate_topology`
13. `2023_contesse_occluding_contours`
14. `1989_detecting_and_decomposing_self_overlapping_curves`
15. `2014_locally_injective_parametrization_fixed_boundaries`
16. `2009_self_overlapping_curves_revisited`
17. `2023_algebraic_smooth_occluding_contours`
18. `1967_quantitative_invisibility`
19. `2006_computing_contour_generators_of_evolving_implicit_surfaces`
20. `1994_visibility_maps_and_spherical_algorithms`
21. `2015_correct_resolution_trimmed_spline_surfaces`
22. `2010_two_fast_methods_for_high_quality_line_visibility`

Support lanes outside the main build order:

- perspective visibility and contour geometry
- assembly visibility
- CAD validity, repair, naming, and interoperability

Use the actual paper folder ids above when navigating the corpus.

## Working Method

Single-paper loop:

```bash
python3 -m venv .venv-paperx
.venv-paperx/bin/python -m pip install -r requirements.txt
.venv-paperx/bin/python -m pipeline.cli.build_review <paper-id> --use-external-layout --use-external-math
python3 -m pipeline.cli.audit_corpus --top 12
```

Useful paper checks:

- read `<paper-id>/canonical.json`
- read `_canon/<paper-id>.canonical.review.md`
- inspect `<paper-id>/canonical_sources/*`
- open the local PDF when exact source verification matters

Corpus-wide rebuilds and stale-output checks use:

```bash
python3 -m pipeline.cli.run_corpus_rounds
```

That writes live round status to `tmp/canonical_corpus_rounds/status.json` and a
human report to `tmp/canonical_corpus_rounds/final_summary.md`, including
pre-rebuild stale reasons when an existing `canonical.json` no longer matches
its recorded inputs or the active canonical pipeline.

Source-generation helpers now live under `pipeline/` when stronger
evidence is needed.

The remaining corpus-generation seam is now split this way:

- engine-owned generation and repair live under `pipeline/`
- corpus-owned expectations live in `figure_expectations.json`
- legacy script entrypoints remain only as compatibility shims where needed

## Figure Assets

- The checked-in PNGs in each paper's `figures/` directory are the local figure
  assets.
- If a figure needs manual repair, replace or edit that paper-owned PNG
  directly.
- `pipeline.figure_linking` preserves existing checked-in figures and
  fills gaps, so deleting a specific PNG is the explicit way to force
  regeneration.

## Maintenance Rules

- Do not add a parallel passage layer back into the corpus.
- Do not hand-edit review drafts as if they were source documents.
- Treat `canonical.json` as the only durable source of truth for paper
  structure, formulas, and figure references.
- Treat `canonical_sources/` as evidence, not as the final fused document.
- When the architectural center of gravity changes, update this file, the
  canonical builder README, and any affected parser docs together.
