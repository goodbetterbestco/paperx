# paperx

`paperx` is a straightforward PDF processor for turning paper PDFs into
canonical JSON plus a markdown review draft.

The repo is organized around one clear contract:

- engine code lives under `pipeline/`
- checked-in corpora live under `corpus/`
- source PDFs live under `_source/`
- processed outputs live under `_data/`, `_canon/`, `_figures/`, and `_runs/`
- `reset_corpus_to_source` is the reverse path back to clean source state

The main architectural bias is acquisition-first:

- prefer better provider choice, OCR policy, and source capture over downstream
  repair
- keep post-acquisition handling structural and minimal
- if a document needs heavy reconstruction after acquisition, treat that as an
  acquisition problem first

## Repository Layout

- `pipeline/`
  Engine code, CLI entrypoints, provider routing, source extraction, assembly,
  and output writers.
- `corpus/`
  Checked-in corpora and local regression surfaces.
- `tests/`
  `unit`, `integration`, `e2e`, and `smoke` coverage.
- `docs/`
  Machine-readable repo assets such as `fixed_validation_slice.json`.
- `tmp/`
  Local audits, reports, scratch slices, and other generated artifacts.

## Layout Contract

There is one supported mode.

`corpus`

- source PDFs live under `corpus/<name>/_source/`
- outputs are written under that corpus directory

Rules:

- use `_source/` as the only supported source-PDF location
- treat `_data/`, `_canon/`, `_figures/`, and `_runs/` as generated artifacts
- use the CLI to move between states instead of hand-editing layout by hand
- fail fast when required tools or expected files are missing

## Pipeline Map

The main engine ownership is:

- `pipeline.acquisition`: provider routing, OCR policy, scorecards, and source
  ownership decisions
- `pipeline.corpus`: corpus paths, metadata, and reset helpers
- `pipeline.processor`: batch execution, source extraction, runtime status, and
  paper-level orchestration
- `pipeline.sources`: Docling, Mathpix, OCRmyPDF, and pdftotext adapters
- `pipeline.assembly`: thin canonical document construction from acquired
  sources
- `pipeline.output`: canonical writing, validation, and review rendering

The hot path is:

1. CLI entrypoint
2. layout resolution
3. source extraction and provider composition
4. minimal paper assembly
5. canonical validation
6. output writing

The reverse path is:

1. `pipeline.cli.reset_corpus_to_source`
2. `pipeline.corpus.state.reset_corpus_to_source_state`
3. `_source/` restored, generated artifacts removed

## Quick Start

Create and use the project venv:

```bash
python3 -m venv .venv-paperx
./.venv-paperx/bin/python -m pip install -r requirements.txt
```

Optional external dependencies:

- Docling CLI in `./.venv-paperx/bin/docling` or `PIPELINE_DOCLING_BIN`
- `ocrmypdf` in `./.venv-paperx/bin/ocrmypdf`, `PIPELINE_OCRMYPDF_BIN`, or
  `PATH`
- `pdftotext` on `PATH`
- Mathpix credentials in `.env.local` when Mathpix is intentionally enabled

## Common Workflows

Run the configured checked-in corpus:

```bash
PIPELINE_CORPUS_NAME=stepview ./.venv-paperx/bin/python -m pipeline.cli.run_corpus_rounds --max-workers 2
```

Build one canonical from the configured corpus:

```bash
PIPELINE_CORPUS_NAME=stepview ./.venv-paperx/bin/python -m pipeline.cli.build_canonical 1990_hidden_curve_removal_for_free_form_surfaces
```

Build canonical plus review draft in one pass:

```bash
PIPELINE_CORPUS_NAME=stepview ./.venv-paperx/bin/python -m pipeline.cli.build_review 1990_hidden_curve_removal_for_free_form_surfaces
```

Render a review draft from an existing canonical:

```bash
PIPELINE_CORPUS_NAME=stepview ./.venv-paperx/bin/python -m pipeline.cli.render_review_from_canonical 1990_hidden_curve_removal_for_free_form_surfaces
```

Reset a processed corpus back to source state:

```bash
./.venv-paperx/bin/python -m pipeline.cli.reset_corpus_to_source ./corpus/stepview
```

## Testing

Recommended commands:

```bash
make test-unit
make test-integration
make test-e2e
make test-smoke

./.venv-paperx/bin/python -m unittest discover -s tests/unit -t . -p '*_test.py'
./.venv-paperx/bin/python -m unittest discover -s tests/integration -t . -p '*_test.py'
./.venv-paperx/bin/python -m unittest discover -s tests/e2e -t . -p '*_test.py'
PAPERX_RUN_SMOKE=1 ./.venv-paperx/bin/python -m unittest discover -s tests/smoke -t . -p '*_test.py'
```

## Credentials

Repo-local credentials belong in `.env.local`, which is ignored by Git.
Current provider keys include:

- `MATHPIX_APP_ID`
- `MATHPIX_APP_KEY`

Prefer explicitly sourcing this repo's `.env.local` when needed so work here
does not accidentally inherit credentials from a sibling project.

## Roadmap

The live backlog and finish-line criteria are in [`ROADMAP.md`](./ROADMAP.md).
