# Acquisition Baseline Note (2026-04-20)

This note captures the shared Phase 0 baseline from
`docs/acquisition_plan.md` after the corpus was reset to the new `source`
layout.

## Commands Run

```bash
.venv-paperx/bin/python -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --label baseline-finalization
.venv-paperx/bin/python -m pipeline.cli.show_acquisition_benchmark_status --from-artifacts
.venv-paperx/bin/python -m pipeline.cli.show_acquisition_benchmark_dashboard --from-artifacts

.venv-paperx/bin/python -m pipeline.cli.audit_acquisition_quality --top 50
.venv-paperx/bin/python -m pipeline.cli.plan_acquisition_remediation_waves --label finalization-baseline
.venv-paperx/bin/python -m pipeline.cli.show_acquisition_remediation_plan_status
```

## Preserved Artifacts

- `tmp/acquisition_benchmark/history/baseline-finalization.json`
- `tmp/acquisition_benchmark/history/baseline-finalization.md`
- `tmp/acquisition_remediation_plans/history/finalization-baseline.json`
- `tmp/acquisition_remediation_plans/summary.json`
- `tmp/acquisition_quality_audit/summary.json`
- `tmp/acquisition_quality_audit/summary.md`

## Benchmark Baseline

The synthetic acquisition benchmark ran cleanly on five fixture papers.

- Overall leader: `docling` at `0.772`
- Content leader: `docling` at `0.725`
- Execution leader: `grobid` at `1.0`
- Layout leader: `docling` at `0.827`
- Math leader: `mathpix` at `0.867`
- Metadata/reference leader: `grobid` at `1.0`

Family leaders from the saved baseline:

- `born_digital_scholarly`: `docling` overall `1.0`
- `scan_or_image_heavy`: `docling` overall `1.0`
- `layout_complex`: `docling` overall `0.88`
- `math_dense`: `mathpix` overall `0.68`
- `degraded_or_garbled`: `grobid` overall `0.68`

Interpretation:

- The current fixture set still supports the broad intended provider split:
  `docling` for layout-first born-digital and scan-heavy cases, `mathpix` for
  math-dense cases, and `grobid` for metadata/reference strength.
- The benchmark remains small and synthetic. It is good enough for a frozen
  baseline, but not yet good enough to trust as a regression gate.

## Live Validation Pressure

The live acquisition audit now sees the real source-state `stepview` corpus.

- Papers audited: `59`
- Canonical outputs present: `0 / 59`
- Missing sidecars reported: `acquisition-route.json`=`59`,
  `source-scorecard.json`=`59`, `ocr-prepass.json`=`59`
- Planned remediation queue items: `0`
- Planned remediation waves: `0`

Interpretation:

- This is the expected baseline for a corpus that has been reset to `source`
  state and not yet locally converted. The audit is now measuring the real
  checked-in corpus, but that corpus intentionally has no acquisition sidecars
  or canonical outputs yet.
- The empty remediation queue is not a sign that the corpus is already healthy.
  It means remediation planning is downstream of acquisition execution and
  follow-up signals. At baseline, the main pressure is still initial conversion
  and sidecar generation, not remediation triage.

## Operator Findings During Phase 0

Two concrete issues showed up immediately:

1. `show_acquisition_benchmark_status --from-artifacts` and
   `show_acquisition_benchmark_dashboard --from-artifacts` reported zero saved
   runs even though `baseline-finalization.json` exists under
   `tmp/acquisition_benchmark/history/`.
2. `audit_acquisition_quality --top 50` did not surface the real source-state
   `stepview` papers after the corpus layout transition, so live validation is
   not yet exercising the new checked-in corpus shape.

Status after this baseline pass:

- The benchmark history-discovery issue is fixed in the benchmark runner, and
  the saved status/dashboard artifacts now see `baseline-finalization`
  correctly.
- The live audit/source-state discovery gap is also fixed. The audit now
  surfaces the real `stepview` source corpus instead of a stray synthetic
  paper.

These are roadmap-relevant findings, not side notes. They mean the first sprint
should include benchmark hardening plus a repeatable processed-state validation
flow for the fixed slice before we trust trend or remediation dashboards.

## Fixed Validation Slice

Use the following `stepview` papers as the fixed real-corpus slice for repeated
validation during the roadmap:

- `corpus/stepview/1967_quantitative_invisibility.pdf`
- `corpus/stepview/1990_curve_intersection_using_bezier_clipping.pdf`
- `corpus/stepview/1990_hidden_curve_removal_for_free_form_surfaces.pdf`
- `corpus/stepview/2001_survey_of_aspect_graphs.pdf`
- `corpus/stepview/2018_trimming_in_isogeometric_analysis_review.pdf`
- `corpus/stepview/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline.pdf`

This slice is intended to cover:

- early or potentially scan-like material
- math-heavy geometry extraction
- figure-heavy core domain material
- survey/reference-heavy structure
- modern review-style layout
- recent born-digital pipeline-oriented PDFs

Until a machine-readable validation manifest is added, treat this list as the
manual source of truth for repeated spot checks.

## What This Means For The Next Sprint

The roadmap is ready to move forward, but the next sprint should start with
Track 2.1 and 2.2 plus one enabling operator workflow:

- expand the acquisition benchmark taxonomy
- add explicit route and OCR expectations
- run the fixed validation slice through the source -> processed path so live
  audit and remediation reports measure provider behavior, not only missing
  sidecars

That will give later routing, OCR, and GROBID work a stable measurement
surface.
