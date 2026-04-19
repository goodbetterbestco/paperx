# End-To-End Tests

This layer is reserved for true subprocess-driven CLI tests.

Current coverage:

- `pipeline.cli.render_review_from_canonical` has a real subprocess-driven e2e
  test in [`pipeline/render_review_cli_test.py`](./pipeline/render_review_cli_test.py)

See [`docs/testing_audit.md`](../../docs/testing_audit.md) for the current
baseline and recommended next additions.
