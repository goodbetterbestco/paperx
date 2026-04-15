# Kernel Corpus

This directory is the canonical-first research corpus for the academic-paper
ingestion work and the StepView kernel white-paper work.

The important shift is that the paper pipeline is no longer passage-first.
`passages.jsonl` is gone. The paper-owned source of truth is now
`canonical.json`, with every other paper view derived from it.

Today this corpus still lives in `docs/`, but it is being prepared to move to
`~/Projects/paperx/stepview/`. In that extracted shape, `paperx/` is the engine
repo root and `stepview/` is just this corpus, so other project corpora can
live alongside it in the future.

## Current Truth

- There are `58` paper-owned folders directly under `docs/<paper-id>/`.
- Each paper folder is the authoritative local home for that paper's PDF,
  canonical extraction, source-evidence files, and checked-in figures.
- `docs/review_drafts/*.canonical.review.md` are derived review views for human
  QA. They are useful, but they are not the source of truth.
- Corpus quality is tracked through the canonical audit, not by ad hoc notes.

Current working shape:

`PDF + canonical_sources -> canonical.json -> review draft / audit / later retrieval products`

Current formula shape inside canonical:

`display_latex -> compiled_targets -> classification(category/policy/role) -> semantic_expr only for semantic formulas`

## What Lives Here

Root files:

- [README.md](./README.md)
  Corpus scope, working method, and paper-map guidance.
- [bibliography.json](./bibliography.json)
  Normalized citation and provenance layer for drafting and source tracking.
- [figure_expectations.json](./figure_expectations.json)
  Corpus-owned figure completeness expectations used by figure regeneration and
  completeness auditing.
- [stepview-kernel-whitepaper-skeleton.md](./stepview-kernel-whitepaper-skeleton.md)
  Working scaffold for the kernel white paper.
- [whitepaper-editorial-standards.md](./whitepaper-editorial-standards.md)
  Drafting standards for tone, notation, and evidence handling.

Per-paper folders:

- `docs/<paper-id>/<paper-id>.pdf`
  Normalized local paper PDF.
- `docs/<paper-id>/canonical.json`
  Paper-owned structured extraction target.
- `docs/<paper-id>/canonical_sources/`
  Engine-specific layout and math evidence.
- `docs/<paper-id>/figures/`
  Checked-in figure assets.

Derived review output:

- `docs/review_drafts/<paper-id>.canonical.review.md`
  Human-readable review draft derived from `canonical.json`.

## Where To Start

- [docs/README.md](./README.md)
  Start here for corpus orientation and paper ownership rules.
- [Paper Pipeline](../paper_pipeline/README.md)
  Top-level architectural boundary for the ingestion system as it is prepared
  for extraction into its own repo.
- [Canonical Builder README](../scripts/kernel/canonical/README.md)
  Canonical build contract, source adapters, formula policy, and audit seam.
- [parser/README.md](../parser/README.md)
  Parser architecture and the current engineering center of gravity.
- [parser/ROADMAP.md](../parser/ROADMAP.md)
  Active StepView implementation plan and phase progress.

If you are answering a question about one paper:

1. Open that paper's `canonical.json`.
2. Inspect `canonical_sources/` if you need to understand a bad block or
   formula.
3. Open the PDF when canonical output or figure extraction is still doubtful.

## Corpus State

The corpus is complete enough that implementation is now the bottleneck, not
paper acquisition.

What is materially true right now:

- all `58` papers have paper-owned homes under `docs/`
- the canonical pipeline is the active ingestion surface
- review drafts are derived from canonical and used for QA only
- formula work is now policy-gated:
  only a minority of formulas are treated as semantic objects
- the live parser queue should be taken from the audit report, not from stale
  handwritten priority lists

To generate the current corpus-quality report:

```bash
python3 -m paper_pipeline.cli.audit_corpus --top 12
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

## Kernel Program Map

The kernel program is still the same six-stage mathematical program:

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

Use the actual paper folder ids above when navigating the corpus. The old
`kernel_*` path naming is no longer the filesystem shape.

## Working Method

Single-paper loop:

```bash
python3 -m venv .venv-kernel-tools
.venv-kernel-tools/bin/python -m pip install -r requirements.txt
.venv-kernel-tools/bin/python -m paper_pipeline.cli.build_review <paper-id> --use-external-layout --use-external-math
python3 -m paper_pipeline.cli.audit_corpus --top 12
```

Useful paper checks:

- read `docs/<paper-id>/canonical.json`
- read `docs/review_drafts/<paper-id>.canonical.review.md`
- inspect `docs/<paper-id>/canonical_sources/*`
- open the local PDF when exact source verification matters

Corpus-wide rebuilds and stale-output checks use:

```bash
python3 -m paper_pipeline.cli.run_corpus_rounds
```

That writes live round status to `tmp/canonical_corpus_rounds/status.json` and a
human report to `tmp/canonical_corpus_rounds/final_summary.md`, including
pre-rebuild stale reasons when an existing `canonical.json` no longer matches
its recorded inputs or the active canonical pipeline.

Source-generation helpers still exist when stronger evidence is needed:

- `scripts/kernel/ingest_pdfs.py`
- `scripts/kernel/canonical/build_external_sources_from_docling.py`
- `scripts/kernel/canonical/build_external_sources_from_mathpix.py`
- `scripts/kernel/canonical/build_external_sources_from_marker.py`
- `scripts/kernel/canonical/build_external_sources_from_grobid.py`

The remaining corpus-generation seam is now split this way:

- engine-owned generation and repair live under `paper_pipeline/`
- corpus-owned expectations live in `figure_expectations.json`
- legacy script entrypoints remain only as compatibility shims where needed

## Figure Assets

- The checked-in PNGs in each paper's `figures/` directory are the local figure
  assets.
- If a figure needs manual repair, replace or edit that paper-owned PNG
  directly.
- `scripts/kernel/link_figures.py` preserves existing checked-in figures and
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
