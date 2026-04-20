# paperx

`paperx` is the extracted home for the academic paper ingestion pipeline and its
checked-in corpora.

Right now this repo contains three first-class areas:

- `pipeline/`: the reusable engine for canonical extraction, review
  rendering, auditing, and corpus-wide rebuilds
- `corpus/`: checked-in corpora, with `stepview/` as the first migrated corpus
- `corpus/stepview/`: the current StepView corpus, including
  checked-in source PDFs plus local processed-state build artifacts when you
  run the pipeline

## Repository Layout

- `pipeline/`
  Core pipeline code, CLI entrypoints, policies, and adapters.
- `corpus/`
  Root container for checked-in corpora.
- `corpus/stepview/`
  Current research corpus for StepView and related source papers.
- `tests/`
  Integration tests for the pipeline.
- `tmp/`
  Generated local audit and round-run output. This is ignored by Git.

See [pipeline/README.md](./pipeline/README.md) for engine details
and [corpus/stepview/README.md](./corpus/stepview/README.md) for corpus structure and working
method.

## Quick Start

```bash
python3 -m venv .venv-paperx
. .venv-paperx/bin/activate
python -m pip install -r requirements.txt
```

This is enough for audit, review, and most local corpus work.

Full source regeneration may also require:

- `pdftotext` on `PATH`
- Mathpix credentials in `.env.local`
- a working `docling` CLI for external source generation

## Common Commands

Audit the current corpus:

```bash
python -m pipeline.cli.audit_corpus --top 12
```

Build a review draft for one paper from the configured corpus:

```bash
python -m pipeline.cli.build_review 1990_hidden_curve_removal_for_free_form_surfaces --use-external-layout --use-external-math
```

Rebuild corpus rounds:

```bash
python -m pipeline.cli.run_corpus_rounds --max-workers 1
```

Normalize and process a project folder:

```bash
python -m pipeline.cli.run_project ./corpus/stepview
```

`run_project` is the forward-looking entrypoint for corpora in `source` state.
It moves root PDFs into processed per-paper folders, materializes the build
artifacts, writes top-level review outputs into `_canon/`, and runs the
pipeline rounds against that corpus folder.

## New Project Flow

The intended shape for future corpora is:

1. Create a new folder under `paperx/corpus/`, such as `paperx/corpus/<project>/`.
2. Drop source PDFs directly into that corpus root.
3. Run `python -m pipeline.cli.run_project <project-dir>`.
4. Let the engine move the corpus from `source` state into `processed` state.
5. Use `python -m pipeline.cli.reset_corpus_to_source <project-dir>` to return
   the corpus to source-only form for check-in.

## Credentials

Repo-local credentials should live in `.env.local`, which is ignored by Git.
Current environment keys used by the pipeline include:

- `MATHPIX_APP_ID`
- `MATHPIX_APP_KEY`

When using env-backed commands for this repo, prefer sourcing
`/Users/evanthayer/Projects/paperx/.env.local` explicitly so work here does not
accidentally pick up credentials from other sibling projects.
