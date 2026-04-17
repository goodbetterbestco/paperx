# Abstract Error Scope Summary

Date: 2026-04-16

Scope: review of the current canonical abstract text for eight papers that were previously flagged as suspect. This document is for scoping only; no fixes are proposed here.

Global note:

- None of these eight papers currently has a `canonical_sources/generated-abstract.txt` override file.
- The failures cluster into four buckets: wrong block selected entirely, figure-caption contamination, partial/truncated abstract capture, and abstract text polluted by non-abstract boilerplate or numbering.

## 1. Arbitrarily Precise Computation of Gauss Maps and Visibility Sets for Freeform Surfaces

Paper id: `1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces`

Current canonical abstract:

> `PDF Download 218013.218073.pdf 07 April 2026 Total Citations: 22 Total Downloads: 497`

Observed errors:

- The extracted abstract is not from the paper at all.
- It is ACM landing-page / portal metadata, not paper content.
- The real abstract appears to have been missed completely.

Scope assessment:

- Severity: critical.
- This is a total abstract-selection failure, likely caused by the PDF beginning with a cover or download wrapper page and the pipeline accepting that page as front matter.

## 2. Partitioning Trimmed Spline Surfaces into NonSelf-Occluding Regions for Visibility Computation

Paper id: `2000_partitioning_trimmed_spline_surfaces_visibility`

Current canonical abstract:

> `Computing the visible portions of curved surfaces from a given viewpoint is of great interest in many applications. It is closely related to the hidden surface re-`

Observed errors:

- The abstract is truncated after the opening lines.
- The capture stops mid-word at `re-`.
- The main contribution text is missing: the decomposition method, visibility curves, trimmed-surface representation, and implementation/results summary do not appear in the canonical abstract.

Scope assessment:

- Severity: major.
- This looks like a partial first-line capture with no continuation merge.

## 3. 2001 a face based mechanism for naming recording and retrieving topological entities

Paper id: `2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities`

Current canonical abstract:

> `some related entities cannot be retrieved or identified from the information in the part model.`

Observed errors:

- The extracted abstract is a single tail sentence from the introduction/problem list, not the abstract.
- The real abstract is present in source layouts and is substantially longer.
- The canonical title is also still polluted with a leading year: `2001 a face based ...`.

Scope assessment:

- Severity: critical.
- This is a wrong-region selection failure, not just truncation.

## 4. Locally Injective Parametrization with Arbitrary Fixed Boundaries

Paper id: `2014_locally_injective_parametrization_fixed_boundaries`

Current canonical abstract:

> `image are positive (i.e. no flipped triangles) and (2) the boundary does not intersect itself. However, in contrast to the smooth setting, (1) alone is not sufficient for local injectivity. A counter example is shown in Figure 1a. A piecewise-linear map is locally injective only if the sum of (unsigned) triangle angles around each internal vertex is precisely 2 p .`

Observed errors:

- The abstract begins mid-sentence and is clearly not the paper abstract.
- The captured text comes from the introduction/discussion of injectivity conditions.
- The real abstract is present in source layouts and starts with `We present an algorithm for mapping a triangle mesh...`.

Scope assessment:

- Severity: critical.
- This is another wrong-region selection failure where the pipeline skipped the actual abstract and latched onto later body text.

## 5. Detecting Weakly Simple Polygons

Paper id: `2015_detecting_weakly_simple_polygons`

Current canonical abstract:

> Correct opening abstract text, followed by a trailing sequence `1 2 3 ... 44`.

Observed errors:

- The abstract body is mostly correct.
- A long run of page or line numbers has been appended to the end of the abstract.
- The contamination appears to come from layout noise rather than from selecting the wrong text block.

Scope assessment:

- Severity: moderate.
- This is a post-processing / noise-filtering issue, not a total extraction failure.

## 6. Algebraic Smooth Occluding Contours

Paper id: `2023_algebraic_smooth_occluding_contours`

Current canonical abstract:

> Mostly correct abstract text, but with broken hyphenation such as `visi- bility`, `pa- per`, `construc- tion`, `state-of- the-art`, and with ACM subject taxonomy appended at the end.

Observed errors:

- The abstract content is largely correct.
- OCR/layout hyphenation artifacts remain inside several words.
- ACM CCS taxonomy text was appended even though it is not part of the abstract.
- The trailing taxonomy clause degrades readability and precision.

Scope assessment:

- Severity: moderate.
- This is primarily a cleanup/boundary problem, not a selection problem.

## 7. ConTesse: Accurate Occluding Contours for Subdivision Surfaces

Paper id: `2023_contesse_occluding_contours`

Current canonical abstract:

> Begins with `Fig. 1. Given (a) a smooth 3D surface...` and panel labels `(a) (b)`, before reaching actual abstract prose.

Observed errors:

- The canonical abstract begins with a figure caption instead of the abstract.
- Panel labels and caption prose are prepended to the real abstract.
- The real abstract text does seem to follow, but the abstract boundary is wrong from the very first sentence.

Scope assessment:

- Severity: major.
- This is figure-caption contamination of the abstract region.

## 8. Topology-First B-Rep Meshing

Paper id: `2026_topology_first_brep_meshing`

Current canonical abstract:

> Begins with `Fig. 1. Selection of models...` and then transitions into actual abstract prose, but ends mid-sentence at `the output mesh is topologically`.

Observed errors:

- The abstract begins with a figure caption rather than the abstract itself.
- The actual abstract prose is present after the caption contamination.
- The capture then truncates before the abstract finishes, ending mid-sentence.

Scope assessment:

- Severity: major.
- This combines two failure modes: figure-caption contamination and truncation.

## Cross-Cutting Patterns

- Wrong block chosen entirely:
  `1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces`
  `2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities`
  `2014_locally_injective_parametrization_fixed_boundaries`
- Figure caption included as abstract lead-in:
  `2023_contesse_occluding_contours`
  `2026_topology_first_brep_meshing`
- Partial/truncated abstract:
  `2000_partitioning_trimmed_spline_surfaces_visibility`
  `2026_topology_first_brep_meshing`
- Mostly correct abstract with cleanup noise:
  `2015_detecting_weakly_simple_polygons`
  `2023_algebraic_smooth_occluding_contours`

## Suggested Fix Buckets For Later

- Front-matter page selection / wrapper-page rejection
- Better abstract boundary detection against figure captions and ACM/venue metadata
- Continuation merging for multi-line or multi-block abstracts
- Noise stripping for page-number streams, taxonomy labels, and OCR hyphenation leftovers
