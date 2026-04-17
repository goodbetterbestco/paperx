# Pipeline

This directory is the new top-level architectural boundary for the academic
paper ingestion system. In the extracted shape, `paperx/` will be the engine
repo root, and each project corpus will live under `corpus/` as data only.

Planned extraction target:

- local repo: `/Users/evanthayer/Projects/paperx`
- remote repo: `https://github.com/goodbetterbestco/paperx`

Planned project layout inside that repo:

- `/Users/evanthayer/Projects/paperx/pipeline/...`
- `/Users/evanthayer/Projects/paperx/corpus/<project>/source/*.pdf`
- `/Users/evanthayer/Projects/paperx/corpus/<project>/corpus/<paper-id>/...`
- `/Users/evanthayer/Projects/paperx/corpus/<project>/*.canonical.review.md`

`corpus/stepview/` is just the first migrated corpus inside `paperx/`, not an
operational dependency of the StepView app.

Today, the primary checked-in engine/data split is:

- engine implementation under `pipeline/`
- checked-in corpora under `corpus/`
- local generated run state under `tmp/`

The build and orchestration entrypoints now live directly under this package,
and the first extraction-prep slices also live here:

- `pipeline.build_canonical`
- `pipeline.build_review`
- `pipeline.build_corpus_lexicon`
- `pipeline.audit_corpus`
- `pipeline.run_corpus_rounds`
- `pipeline.runtime_paths`
- `pipeline.staleness_policy`
- `pipeline.policies.*`

That is intentional for now. The goal of this boundary is to make a later repo
extraction low-risk by stabilizing:

- the user-facing CLI entrypoints
- the logical identity of the pipeline components
- the documentation center of gravity

Current preferred commands:

- `python3 -m pipeline.cli.run_project /Users/evanthayer/Projects/paperx/<project>`
- `python3 -m pipeline.cli.build_review <paper-id> --use-external-layout --use-external-math`
- `python3 -m pipeline.cli.build_corpus_lexicon`
- `python3 -m pipeline.cli.audit_corpus --top 12`
- `python3 -m pipeline.cli.run_corpus_rounds`

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

Figure regeneration now also lives under this package:

- `pipeline.figures.linking` (with `pipeline.figure_linking` kept as a compatibility shim)
- `pipeline.vision_ocr.js`

Corpus-specific figure expectations now live with the corpus itself at
`<corpus-root>/figure_expectations.json`.

The local extraction target at `/Users/evanthayer/Projects/paperx` now routes
the default checked-in corpus through `/Users/evanthayer/Projects/paperx/corpus/stepview`.
The remaining plain-`python3` gap is dependency bootstrap, not path coupling.

The extraction plan is:

1. keep this package as the stable boundary
2. move the remaining parser/extractor implementation under this boundary in
   smaller slices
3. move the corpus out of the StepView repo only after the contracts are clean

When the extracted repo exists, the preferred user flow is:

1. create `paperx/corpus/<project>/`
2. drop PDFs into that project root
3. run `python3 -m pipeline.cli.run_project <project-path>`
4. let the engine normalize the project into:
   - `source/` for the input PDFs
   - `corpus/` for canonical outputs
   - project-root generated review drafts

For compatibility, `PIPELINE_CORPUS_DIR` can point the code at a single corpus
root, and the older `PAPER_PIPELINE_CORPUS_DIR` still works as a fallback.
Without that override, the package prefers
`<engine-root>/corpus/<corpus-name>/` when it exists, and falls back to the current
in-repo `docs/` layout otherwise.
