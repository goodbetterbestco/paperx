# End-To-End Tests

This layer is reserved for true subprocess-driven CLI tests.

Current coverage:

- `pipeline.cli.render_review_from_canonical` has a real subprocess-driven e2e
  test in [`render_review_cli_test.py`](./render_review_cli_test.py)
- `pipeline.cli.export_titles_and_abstracts` has a real subprocess-driven e2e
  test in [`export_titles_cli_test.py`](./export_titles_cli_test.py)
- `pipeline.cli.audit_corpus` has a real subprocess-driven e2e test in
  [`audit_corpus_cli_test.py`](./audit_corpus_cli_test.py)
- `pipeline.cli.build_corpus_lexicon` has a real subprocess-driven e2e test in
  [`build_corpus_lexicon_cli_test.py`](./build_corpus_lexicon_cli_test.py)

See [`docs/testing_audit.md`](../../docs/testing_audit.md) for the current
baseline and recommended next additions.
