# Pipeline

This directory is the top-level engine boundary for the academic paper
ingestion system.

Today, the checked-in engine/data split is:

- engine implementation under `pipeline/`
- checked-in corpora under `corpus/`
- local generated run state under `tmp/`

`corpus/stepview/` is just the first migrated corpus inside `paperx/`, not an
runtime dependency of another application.

The current architecture is package-first:

- stable root boundary files live directly under `pipeline/`
- implementation lives in package families under `pipeline/*/`
- user-facing commands prefer `pipeline.cli.*`

The intended stable root boundary is:

- `pipeline.run_corpus_rounds`
- `pipeline.config`
- `pipeline.corpus_layout`
- `pipeline.runtime_paths`
- `pipeline.state`
- `pipeline.types`

The main implementation families are:

- `pipeline.acquisition`
- `pipeline.assembly`
- `pipeline.cli`
- `pipeline.corpus`
- `pipeline.figures`
- `pipeline.math`
- `pipeline.orchestrator`
- `pipeline.output`
- `pipeline.policies`
- `pipeline.reconcile`
- `pipeline.selectors`
- `pipeline.sources`
- `pipeline.text`

This boundary is intentionally stable so that the engine can evolve without
reintroducing large root-level facade modules. Historical logical component ids
for canonical fingerprint compatibility are preserved in
`pipeline.output.identity` even when old root wrappers have been deleted.

The architecture goals are:

- the user-facing CLI entrypoints
- explicit config, state, and path resolution
- thin orchestration
- package-owned implementation by domain
- stable canonical fingerprint identity across file moves

Current preferred commands:

- `python3 -m pipeline.cli.run_project /Users/evanthayer/Projects/paperx/<project>`
- `python3 -m pipeline.cli.build_canonical <paper-id> --use-external-layout --use-external-math`
- `python3 -m pipeline.cli.build_review <paper-id> --use-external-layout --use-external-math`
- `python3 -m pipeline.cli.build_corpus_lexicon`
- `python3 -m pipeline.cli.build_external_layout_from_pdftotext <paper-id>`
- `python3 -m pipeline.cli.build_external_sources_from_docling <paper-id>`
- `python3 -m pipeline.cli.build_external_sources_from_mathpix <paper-id>`
- `python3 -m pipeline.cli.compose_external_sources <paper-id> --layout-json ... --math-json ...`
- `python3 -m pipeline.cli.inspect_acquisition_route <paper-id>`
- `python3 -m pipeline.cli.inspect_acquisition_scorecard <paper-id>`
- `python3 -m pipeline.cli.backfill_acquisition_sidecars`
- `python3 -m pipeline.cli.audit_acquisition_quality --top 12`
- `python3 -m pipeline.cli.audit_acquisition_quality --format commands`
- `python3 -m pipeline.cli.run_acquisition_remediation_queue --dry-run`
- `python3 -m pipeline.cli.run_acquisition_remediation_queue --fail-fast --limit 5`
- `python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json`
- `python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --label baseline-apr19`
- `python3 -m pipeline.cli.run_acquisition_benchmark --manifest tests/fixtures/acquisition_benchmark/manifest.json --format markdown`
- `python3 -m pipeline.cli.show_acquisition_benchmark_status`
- `python3 -m pipeline.cli.show_acquisition_benchmark_status --from-artifacts`
- `python3 -m pipeline.cli.show_acquisition_benchmark_dashboard`
- `python3 -m pipeline.cli.show_acquisition_benchmark_dashboard --from-artifacts`
- `python3 -m pipeline.cli.list_acquisition_benchmark_history --limit 5`
- `python3 -m pipeline.cli.summarize_acquisition_benchmark_trend`
- `python3 -m pipeline.cli.compare_acquisition_benchmark --base tmp/acquisition_benchmark/history/baseline-apr19.json --candidate tmp/acquisition_benchmark/history/candidate-apr20.json`
- `python3 -m pipeline.cli.compare_acquisition_benchmark --base previous --candidate latest`
- `python3 -m pipeline.cli.run_grobid_trial --manifest tests/fixtures/grobid_trial/manifest.json`
- `python3 -m pipeline.cli.render_review_from_canonical <paper-id>`
- `python3 -m pipeline.cli.export_titles_and_abstracts`
- `python3 -m pipeline.cli.audit_corpus --top 12`
- `python3 -m pipeline.cli.run_corpus_rounds`

## Source Of Truth

This README is the current architecture reference for the pipeline package.

## Bootstrap

Minimal Python bootstrap for audit/review work:

- `python3 -m venv .venv-paperx`
- `.venv-paperx/bin/python -m pip install -r requirements.txt`

That is enough for:

- `python3 -m pipeline.cli.audit_corpus`
- `python3 -m pipeline.cli.build_review ... --use-external-layout --use-external-math`
- `python3 -m pipeline.cli.run_project /path/to/project`

Full source regeneration still expects additional tools and credentials:

- `pdftotext` on `PATH`
- Mathpix credentials for live Mathpix calls
- a working `docling` CLI for Docling source generation
- `ocrmypdf` when the acquisition route recommends or requires an OCR pre-pass

When OCR normalization runs, the generated artifact is written to
`<corpus-root>/<paper-id>/canonical_sources/ocr-normalized.pdf`, and the round
source builders will prefer that PDF over the original input for Docling and
Mathpix extraction.
The OCR execution result is also persisted to
`<corpus-root>/<paper-id>/canonical_sources/ocr-prepass.json`.
Acquisition routing and provider recommendation sidecars remain at
`<corpus-root>/<paper-id>/canonical_sources/acquisition-route.json` and
`<corpus-root>/<paper-id>/canonical_sources/source-scorecard.json`, and the
acquisition audit CLI summarizes their coverage and OCR execution drift into
`tmp/acquisition_quality_audit/`.
That audit also writes a structured `remediation_queue` into
`tmp/acquisition_quality_audit/summary.json`; use
`pipeline.cli.audit_acquisition_quality --format commands` to print only the
queued remediation commands, or
`pipeline.cli.run_acquisition_remediation_queue` to batch-run the selected
follow-up remediations from either a live audit or a saved report.
The fixture-backed acquisition benchmark can now also score execution-policy
behavior when provider fixtures include `acquisition-execution.json` sidecars,
including route agreement, OCR application correctness, and selected-provider
agreement against gold expectations. Each benchmark run now writes a current
artifact bundle under `tmp/acquisition_benchmark/`:

- `summary.{json,md}` for the raw benchmark report
- `status.{json,md}` for the latest operator status view
- `dashboard.{json,md}` for the broader operator dashboard
- `history/<label>.{json,md}` for the labeled benchmark snapshot

Use `--label` on `pipeline.cli.run_acquisition_benchmark` to name snapshot
artifacts explicitly. `pipeline.cli.compare_acquisition_benchmark` can diff two
saved summary JSON files by provider and benchmark family, and it also accepts
snapshot labels plus `latest` and `previous` aliases resolved from benchmark
history. `pipeline.cli.list_acquisition_benchmark_history` shows the saved runs
and per-provider aggregate deltas versus the previous snapshot.
`pipeline.cli.summarize_acquisition_benchmark_trend` turns the latest-vs-previous
comparison into a short improvement/regression watchlist overall and by family.
`pipeline.cli.show_acquisition_benchmark_status` combines the latest saved run
with that watchlist into a single “where are we now?” status view, and
`pipeline.cli.show_acquisition_benchmark_dashboard` gives the fuller operator
dashboard across leaders, regressions, latest-vs-previous movement, and recent
runs. Both status and dashboard CLIs accept `--from-artifacts` when you want to
read the saved current bundle directly instead of recomputing from history.

Figure regeneration now also lives under this package:

- `pipeline.figures.linking`
- `pipeline.figures.vision_ocr.js`

Corpus-specific figure expectations now live with the corpus itself at
`<corpus-root>/figure_expectations.json`.

For compatibility, `PIPELINE_CORPUS_DIR` can point the code at a single corpus
root, and the older `PAPER_PIPELINE_CORPUS_DIR` still works as a fallback.
Without that override, the package prefers
`<engine-root>/corpus/<corpus-name>/` when it exists, and falls back to the current
in-repo `docs/` layout otherwise.
