# Acquisition Benchmark Fixture Checklist

This checklist defines the minimum bar for benchmark fixtures under
`tests/fixtures/acquisition_benchmark/`.

The goal is to make each fixture useful for engineering decisions, not only to
exercise a happy-path parser.

## Taxonomy

Each fixture should belong to a manifest section that explains what family of
failure or behavior it covers.

Current preferred sections:

- `routing`
- `ocr`
- `metadata`
- `references`
- `layout`
- `math`
- `mixed`

If a fixture touches several categories, choose the one that best explains why
it exists.

## Gold Expectations

Each gold JSON should declare, when applicable:

- `family`
- `expected_route`
- `expected_route_reason_codes`
- `ocr_should_run`
- `expected_ocr_policy`
- `expected_primary_layout_provider`
- `expected_primary_math_provider`
- `expected_primary_metadata_provider`
- `expected_primary_reference_provider`
- `acceptable_selected_*_providers` when more than one selected-provider
  outcome is valid
- realistic title, abstract, headings, paragraphs, equations, and references

Use `acceptable_selected_*_providers` only for genuinely valid alternate live
selections, not to hide indecision about the policy.

## Execution Fixture Expectations

Each execution fixture should preserve the same operator vocabulary used by the
live pipeline whenever possible.

Prefer including:

- `route_primary`
- `route_traits`
- `recommended.*`
- `executed.*`
- `ocr.policy`
- `ocr.applied`
- `follow_up.needs_attention` if follow-up behavior is part of the case

## Quality Rules

Before adding or editing a fixture, confirm:

- the fixture teaches us something about provider choice, OCR policy, or a real
  failure mode
- the route expectation is explicit
- the OCR expectation is explicit
- the provider-selection expectation is explicit
- the fixture would catch a realistic regression, not only a formatting change
- the manifest path makes the fixture family obvious

## Expansion Priority

When adding the next fixtures, prefer this order:

1. routing cases with explicit route-reason coverage
2. OCR-required and OCR-forbidden cases
3. metadata/reference ownership edge cases
4. layout-complex and math-heavy cases
5. mixed or real-corpus gold cases
