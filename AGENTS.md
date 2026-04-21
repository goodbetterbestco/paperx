# Repo Instructions

This file applies to the entire repository.
This `AGENTS.md` is the authoritative default for code-generating agents working in `paperx`.

## Default Posture

- Prefer one clear execution path over compatibility layers.
- Prefer an explicit failure over a silent fallback.
- Prefer deleting transitional code over extending it.

## Compatibility And Fallbacks

- Do not add compatibility aliases, migration shims, deprecated env vars, legacy path support, signature adapters, or silent provider fallbacks by default.
- Do not preserve old behavior "just in case" for an unlaunched system.
- If the current contract is wrong, change the contract and update callers. Do not add another translation layer around it.
- If a fallback would change the work product, stop and ask for human approval instead of inventing a degraded path.

## Human Approval Rule

- Any individual compatibility path or fallback requires explicit human approval in the current thread for that exact case.
- Approval must be case-by-case. A general preference for safety does not authorize new fallback logic.
- Every approved exception must name its exit condition and the test that protects its eventual removal.

## Fail Fast

- Crash loudly when required inputs, tools, or layouts are missing or malformed.
- Surface the broken seam directly instead of continuing with guessed inputs.
- Prefer repo-local tooling and the project venv over machine-level PATH fallbacks.

## Refactoring

- When touching code that contains legacy branches, remove dead fallback logic instead of routing around it.
- Keep the hot path readable. If a branch exists only for history, it probably should not exist.
- Add tests for the intended path and for the fail-fast behavior when a legacy path is no longer supported.
