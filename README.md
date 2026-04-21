# paperx

`paperx` is the extracted home for the academic paper ingestion engine and the
checked-in research corpora it operates on.

The project is now organized around one simple truth:

- engine code lives under `pipeline/`
- checked-in corpora live under `corpus/`
- processed outputs are local artifacts only
- the checked-in copy of a corpus stays in source state

The first migrated corpus is `corpus/stepview`, which currently contains `58`
checked-in source PDFs.

## Repository Layout

- `pipeline/`
  Engine code, CLI entrypoints, acquisition policy, orchestration, reconcile
  helpers, assembly, and output writers.
- `corpus/`
  Checked-in corpora. In Git they should remain source-only.
- `tests/`
  `unit`, `integration`, `e2e`, and `smoke` coverage.
- `docs/`
  Machine-readable repo assets such as `fixed_validation_slice.json`, not
  prose documentation.
- `tmp/`
  Local audits, reports, scratch slices, and other generated artifacts.

## Operating Model

Every corpus has exactly two meaningful states.

`source`

- the corpus root contains only the original PDFs
- this is the checked-in Git state

`processed`

- PDFs have been moved into per-paper folders
- the engine may generate `canonical.json`, `canonical_sources/`, `figures/`,
  `_canon/`, `_runs/`, and other local outputs

Rules:

- commit source-state inputs
- do not commit processed-state outputs
- use the CLI to move between states instead of hand-editing the layout

## Pipeline Map

The main engine ownership is:

- `pipeline.acquisition`: provider routing, OCR policy, scorecards, audits,
  benchmarks, and remediation surfaces
- `pipeline.corpus`: layout resolution, corpus-state transitions, metadata, and
  scratch-slice materialization
- `pipeline.orchestrator`: source resolution, record normalization, document
  assembly sequencing, and metadata overlay
- `pipeline.reconcile`: dense helper and dependency-binding layer for layout,
  text, front matter, sections, and math
- `pipeline.assembly`: canonical-document construction
- `pipeline.output`: canonicals, review drafts, staleness, dashboards, and
  reports

The hot path is:

1. CLI entrypoint
2. layout resolution
3. source resolution
4. record normalization
5. document assembly
6. metadata overlay
7. output writing or audit rendering

## Quick Start

Create and use the project venv:

```bash
python3 -m venv .venv-paperx
./.venv-paperx/bin/python -m pip install -r requirements.txt
```

Optional external dependencies:

- `pdftotext` on `PATH`
- `ocrmypdf` on `PATH`
- Mathpix credentials in `.env.local`
- a working Docling CLI in `.venv-paperx` or `PIPELINE_DOCLING_BIN`

## Common Workflows

Inspect the checked-in source-state corpus:

```bash
./.venv-paperx/bin/python -m pipeline.cli.audit_acquisition_quality --top 12
```

Materialize a scratch validation slice:

```bash
./.venv-paperx/bin/python -m pipeline.cli.materialize_source_slice ./tmp/fixed_validation_slice --manifest ./docs/fixed_validation_slice.json --force
```

Convert that slice from source to processed state and run the pipeline:

```bash
./.venv-paperx/bin/python -m pipeline.cli.run_project ./tmp/fixed_validation_slice --max-workers 2
```

Build a canonical or review draft for one paper in a processed corpus:

```bash
./.venv-paperx/bin/python -m pipeline.cli.build_canonical 1990_hidden_curve_removal_for_free_form_surfaces --use-external-layout --use-external-math
./.venv-paperx/bin/python -m pipeline.cli.build_review 1990_hidden_curve_removal_for_free_form_surfaces --use-external-layout --use-external-math
```

Audit processed-state canonicals:

```bash
./.venv-paperx/bin/python -m pipeline.cli.audit_corpus --top 12
```

Return a processed corpus or scratch slice to clean source state:

```bash
./.venv-paperx/bin/python -m pipeline.cli.reset_corpus_to_source ./tmp/fixed_validation_slice
```

## Testing

Current test inventory:

- `tests/unit/`: `94` files
- `tests/integration/`: `9` files
- `tests/e2e/`: `14` files
- `tests/smoke/`: `1` file

Recommended commands:

```bash
./.venv-paperx/bin/python -m unittest discover -s tests/unit -t . -p '*_test.py'
./.venv-paperx/bin/python -m unittest discover -s tests/integration -t . -p '*_test.py'
./.venv-paperx/bin/python -m unittest discover -s tests/e2e -t . -p '*_test.py'
PAPERX_RUN_SMOKE=1 ./.venv-paperx/bin/python -m unittest discover -s tests/smoke -t . -p '*_test.py'
```

## Credentials

Repo-local credentials belong in `.env.local`, which is ignored by Git.
Current live provider keys include:

- `MATHPIX_APP_ID`
- `MATHPIX_APP_KEY`

Prefer explicitly sourcing this repo's `.env.local` when needed so work here
does not accidentally inherit credentials from a sibling project.

## Roadmap

The live backlog and finish-line criteria are in [`ROADMAP.md`](./ROADMAP.md).
