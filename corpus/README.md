# Corpora

This directory is the repo-root home for checked-in corpora.

Rules:

- Each corpus lives under `corpus/<name>/`.
- Corpus data is not engine code.
- The pipeline should treat every corpus here through the same root-level seam.
- `stepview/` is the first migrated corpus, not a structural special case.

Current corpus:

- [stepview](./stepview/README.md)

Intended long-term shape:

- `corpus/<name>/source/*.pdf`
- `corpus/<name>/corpus/<paper-id>/...` for project-mode corpora
- or checked-in single-corpus layouts like `corpus/stepview/<paper-id>/...` during migration
