# Testing Standards

Date: 2026-04-18

Status: active

## Purpose

This document defines the testing standard for `paperx`.

The goal is not to maximize test count. The goal is to make failures legible
and trustworthy:

- pure logic should be protected by fast, real behavior tests
- cross-module wiring should be exercised with real filesystem and artifact flow
- end-to-end user commands should have a small number of true CLI tests
- optional external integrations should have narrow smoke coverage instead of
  being silently assumed

## Core Principles

1. Prefer real behavior over mocked behavior.
2. Prefer asserting user-visible outcomes over asserting implementation trivia.
3. Use seams intentionally.
4. Keep the test pyramid honest: most tests should be fast hermetic behavior
   tests, with fewer integration tests, and only a small number of e2e and
   smoke checks.
5. A test's directory and name should describe what it really is, not what we
   wish it were.

## Test Layers

### Unit

Definition:

- exercises one production module or one tight cluster of pure helpers
- runs real production logic
- uses synthetic in-memory inputs freely
- may use simple temp files when the module's behavior is fundamentally file
  oriented, but should avoid broad cross-module setup

Allowed:

- plain Python data fixtures
- tiny helper builders inside the test file
- temp directories for narrowly file-oriented code
- patching slow or nondeterministic leaf dependencies only when the test is
  explicitly about the caller's contract with that dependency

Not allowed:

- patching the main collaborators of the behavior under test and then claiming
  the test proves integration
- verifying only that one function called another with a particular keyword
  unless the test is explicitly marked as a contract test

### Integration

Definition:

- exercises multiple production modules together
- uses real filesystem layout, serialization, and artifact paths
- proves that a real boundary works across module ownership lines

Allowed:

- temp project/corpus roots
- real JSON or Markdown artifacts written to disk
- patching only hard external boundaries or expensive optional tools

Not allowed:

- replacing the core collaborators of the path under test
- patching nearly every step and then calling the result an integration test

### End-To-End

Definition:

- runs the actual CLI entrypoint through `python -m ...` or equivalent
- uses a minimal fixture project or corpus
- asserts user-visible outputs and exit status

Allowed:

- fixture projects under `tests/fixtures/`
- subprocess execution
- real artifact assertions

Not allowed:

- patching internal helper functions
- importing `main()` directly and substituting most collaborators

### Smoke

Definition:

- very small real-environment checks for optional dependencies or external
  integrations
- intended to answer "does this actually run here?" rather than "is every
  branch correct?"

Examples:

- PyMuPDF-based figure extraction can open a tiny fixture PDF
- Docling CLI can be discovered and invoked on a tiny fixture when enabled
- Mathpix transport can perform a live request only when credentials are
  explicitly present
- macOS Vision OCR bridge can run on one small image when enabled

Rules:

- smoke tests must be explicitly gated
- they should be skippable in normal local and CI runs unless the environment
  opts in
- they should fail loudly and specifically when opted in

## Contract Tests

Contract tests are a style, not a layer.

A contract test is appropriate when we need to lock:

- argument threading across a boundary
- request or subprocess payload shape
- file naming and location conventions
- stable architecture invariants

Contract tests must be labeled honestly:

- `unit` if they mostly validate one module's boundary contract
- `integration` if they validate a real cross-module contract with real files

Contract tests do not replace real behavior tests.

## Mocking And Faking Policy

### Good Uses

- network calls
- subprocess calls to optional external tools
- time, sleep, randomness, and other nondeterministic leaf dependencies
- expensive or unavailable platform services

### Bad Uses

- patching the function that contains the real logic we claim to be testing
- patching every collaborator in an orchestration path and treating it as
  equivalent to e2e coverage
- using mocks to avoid building minimal real fixtures when the real fixture
  would be cheap

## Fixture Policy

- prefer the smallest fixture that preserves the real behavior
- prefer checked-in fixtures for e2e and smoke tests
- prefer temp directories for integration tests that write artifacts
- avoid giant synthetic dictionaries when a tiny real artifact would be clearer

## Assertion Policy

Every test should primarily answer one of these:

- what behavior does the user or downstream module observe?
- what artifact gets written?
- what stable contract is guaranteed?
- what regression is prevented?

Avoid tests whose only value is:

- "a helper was called"
- "a mock received a parameter"
- "the implementation still has the same call graph"

unless the contract itself is the thing we need to freeze.

## Layout And Naming

The intended suite layout is:

- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`
- `tests/smoke/`

Recommended naming:

- `*_test.py` remains acceptable
- if a test file is mostly contract-focused, the filename or class docstring
  should say so

## Coverage Policy

Coverage is a planning signal, not a substitute for judgment.

Rules:

- line coverage is tracked on `pipeline/*`
- no change should reduce coverage in touched modules without an explicit reason
- if a touched module is below `60%` line coverage, the change should usually
  add tests there unless the change is documentation-only
- new logic-heavy modules should ship with unit coverage
- new CLI or orchestration entrypoints should ship with either real integration
  coverage or e2e coverage, depending on scope
- external integrations should have at least one contract test and one smoke
  test when practical

Current baseline guidance, taken from the 2026-04-18 test audit:

- weighted `pipeline/*` line coverage baseline: `64.1%`
- lowest-covered families are currently `pipeline.figures`, `pipeline.orchestrator`,
  `pipeline.sources`, and `pipeline.assembly`

Near-term target:

- raise weighted `pipeline/*` line coverage above `70%`
- reduce the count of sub-`50%` modules, especially in orchestration and source
  acquisition

## Review Checklist

When reviewing tests, ask:

1. Is this file in the correct layer?
2. Does it run real behavior, or is it mostly a contract test?
3. Is mocking limited to true boundaries?
4. Does it assert observable outcomes?
5. If this path matters to users, do we also have higher-level coverage?

## Migration Rule

When a test is discovered to be mislabeled:

- do not delete it just because it is not "real enough"
- first relabel or move it to the layer it actually belongs in
- then add the missing real behavior or e2e coverage above it

The objective is an honest suite, not a cosmetically small one.
