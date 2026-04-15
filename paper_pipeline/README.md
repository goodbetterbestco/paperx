# Paper Pipeline

This directory is the new top-level architectural boundary for the academic
paper ingestion system. In the extracted shape, `paperx/` will be the engine
repo root, and each project corpus will live beside the engine as data only.

Planned extraction target:

- local repo: `/Users/evanthayer/Projects/paperx`
- remote repo: `https://github.com/goodbetterbestco/paperx`

Planned project layout inside that repo:

- `/Users/evanthayer/Projects/paperx/paper_pipeline/...`
- `/Users/evanthayer/Projects/paperx/<project>/source/*.pdf`
- `/Users/evanthayer/Projects/paperx/<project>/corpus/<paper-id>/...`
- `/Users/evanthayer/Projects/paperx/<project>/*.canonical.review.md`

`stepview/` will just be one such project folder inside `paperx/`, not an
operational dependency of the StepView app.

Today, the system has one primary engine home and one remaining legacy helper
surface:

- engine implementation lives primarily under `paper_pipeline/`
- `scripts/kernel/canonical/*.py` now exist mostly as compatibility shims
- a smaller set of source-generation helpers still live under `scripts/kernel/`
- paper corpus and checked-in outputs still live under `docs/`

The code now has an explicit corpus-layout seam so that current `docs/` can be
repointed to `paperx/<project>/source + corpus + root generated papers` later
without another broad hardcoded-path pass.

The build and orchestration entrypoints now live directly under this package,
and the first extraction-prep slices also live here:

- `paper_pipeline.build_canonical`
- `paper_pipeline.build_review`
- `paper_pipeline.build_corpus_lexicon`
- `paper_pipeline.audit_corpus`
- `paper_pipeline.run_corpus_rounds`
- `paper_pipeline.runtime_paths`
- `paper_pipeline.staleness_policy`
- `paper_pipeline.policies.*`

That is intentional for now. The goal of this boundary is to make a later repo
extraction low-risk by stabilizing:

- the user-facing CLI entrypoints
- the logical identity of the pipeline components
- the documentation center of gravity

Current preferred commands:

- `python3 -m paper_pipeline.cli.run_project /Users/evanthayer/Projects/paperx/<project>`
- `python3 -m paper_pipeline.cli.build_review <paper-id> --use-external-layout --use-external-math`
- `python3 -m paper_pipeline.cli.build_corpus_lexicon`
- `python3 -m paper_pipeline.cli.audit_corpus --top 12`
- `python3 -m paper_pipeline.cli.run_corpus_rounds`

The older `scripts/kernel/canonical/*.py` commands still exist, but they are
now compatibility shims rather than the preferred engine boundary.

## Bootstrap

Minimal Python bootstrap for audit/review work:

- `python3 -m venv .venv-paperx`
- `.venv-paperx/bin/python -m pip install -r paper_pipeline/requirements.txt`

That is enough for:

- `python3 -m paper_pipeline.cli.audit_corpus`
- `python3 -m paper_pipeline.cli.build_review ... --use-external-layout --use-external-math`
- `python3 -m paper_pipeline.cli.run_project /path/to/project`

Full source regeneration still expects additional tools and credentials:

- `pdftotext` on `PATH`
- Mathpix credentials for live Mathpix calls
- a working `docling` CLI for Docling source generation

Figure regeneration now also lives under this package:

- `paper_pipeline.figure_linking`
- `paper_pipeline.vision_ocr.js`

Corpus-specific figure expectations are no longer read from
`scripts/kernel/ingest_pdfs.py`. They now live with the corpus itself at
`<corpus-root>/figure_expectations.json`.

The copied local extraction target at `/Users/evanthayer/Projects/paperx`
already passes the audit path directly against `/Users/evanthayer/Projects/paperx/stepview`.
The build path also works there when run with the current kernel-tools Python
environment; the remaining plain-`python3` gap is just dependency bootstrap.

The extraction plan is:

1. keep this package as the stable boundary
2. move the remaining parser/extractor implementation under this boundary in
   smaller slices
3. move the corpus out of the StepView repo only after the contracts are clean

When the extracted repo exists, the preferred user flow is:

1. create `paperx/<project>/`
2. drop PDFs into that project root
3. run `python3 -m paper_pipeline.cli.run_project <project-path>`
4. let the engine normalize the project into:
   - `source/` for the input PDFs
   - `corpus/` for canonical outputs
   - root-level generated paper drafts

For compatibility, `PAPER_PIPELINE_CORPUS_DIR` can still point the code at a
single corpus root. Without that override, the package prefers
`<engine-root>/<corpus-name>/` when it exists, and falls back to the current
in-repo `docs/` layout otherwise.
