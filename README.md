# paperx

`paperx` is the extracted home for the academic paper ingestion pipeline and its
checked-in corpora.

Right now this repo contains two things:

- `paper_pipeline/`: the reusable engine for canonical extraction, review
  rendering, auditing, and corpus-wide rebuilds
- `stepview/`: the first project corpus migrated into this repo, including
  source PDFs, `canonical.json` outputs, figure assets, and review drafts

## Repository Layout

- `paper_pipeline/`
  Core pipeline code, CLI entrypoints, policies, and adapters.
- `stepview/`
  Current research corpus for StepView and related source papers.
- `tests/`
  Integration tests for the pipeline.
- `tmp/`
  Generated local audit and round-run output. This is ignored by Git.

See [paper_pipeline/README.md](./paper_pipeline/README.md) for engine details
and [stepview/README.md](./stepview/README.md) for corpus structure and working
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
python -m paper_pipeline.cli.audit_corpus --top 12
```

Build a review draft for one paper from the configured corpus:

```bash
python -m paper_pipeline.cli.build_review 1990_hidden_curve_removal_for_free_form_surfaces --use-external-layout --use-external-math
```

Rebuild corpus rounds:

```bash
python -m paper_pipeline.cli.run_corpus_rounds --max-workers 1
```

Normalize and process a project folder:

```bash
python -m paper_pipeline.cli.run_project ./stepview
```

`run_project` is the forward-looking entrypoint for new corpora. It prepares a
project folder, discovers PDFs from the project root or `source/`, and runs the
pipeline rounds against that project.

## New Project Flow

The intended shape for future corpora is:

1. Create a new folder under the repo, such as `paperx/<project>/`.
2. Drop PDFs into that project root or `source/`.
3. Run `python -m paper_pipeline.cli.run_project <project-dir>`.
4. Let the engine normalize the project into project-owned corpus outputs and
   review artifacts.

## Credentials

Repo-local credentials should live in `.env.local`, which is ignored by Git.
Current environment keys used around this repo include:

- `MATHPIX_NAME`
- `MATHPIX_APP_ID`
- `MATHPIX_APP_KEY`
- `GITHUB_PAT`

When using env-backed commands for this repo, prefer sourcing
`/Users/evanthayer/Projects/paperx/.env.local` explicitly so work here does not
accidentally pick up credentials from other sibling projects.
