# Smoke Tests

This layer is reserved for opt-in real-environment checks of optional
integrations such as Docling, Mathpix, PyMuPDF-based figure paths, and the
macOS Vision OCR helper.

Current coverage:

- `pipeline.sources.layout.extract_layout` has a gated PyMuPDF smoke skeleton in
  [`layout_extraction_smoke_test.py`](./layout_extraction_smoke_test.py)

Run smoke tests explicitly with:

```bash
PAPERX_RUN_SMOKE=1 python3 -m unittest discover -s tests/smoke -t . -p '*_test.py'
```

See [`docs/testing_audit.md`](../../docs/testing_audit.md) for the current
baseline and recommended next additions.
