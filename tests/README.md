# Test Suite

The test tree is organized by truth of execution, not by historical habit.

Layers:

- `tests/unit/`: fast hermetic behavior tests and narrow contract tests
- `tests/integration/`: real cross-module and filesystem tests
- `tests/e2e/`: true CLI subprocess tests against minimal fixture projects
- `tests/smoke/`: opt-in real-environment checks for optional integrations

Recommended discovery command:

```bash
python3 -m unittest discover -s tests -t . -p '*_test.py'
```

See [`docs/testing_standards.md`](../docs/testing_standards.md) for the active
standard and [`docs/testing_audit.md`](../docs/testing_audit.md) for the
2026-04-18 baseline classification and coverage review.
