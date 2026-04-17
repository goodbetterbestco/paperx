# Robust Tessellation of CAD Models without Self-Intersections

Gangyi Li, Zhongxuan Luo, Yuhao Feng, Lingfeng Zhang, Yuqiao Gai, Na Lei

School of Software
Dalian University of Technology
Dalian, Liaoning 116024, China ∗ Correspondence

## Abstract

The tessellation of Computer-Aided Design (CAD) models into high-quality triangular meshes is a fundamental preprocessing step for downstream applications in visualization, numerical simulation, and digital manufacturing. While modern boundary representation models are typically geometrically valid and free of self-intersections, their tessellation frequently introduces artificial geometric artifacts-including self-intersections and gaps-particularly in regions containing narrow features or high-curvature surfaces. This paper presents a robust, general framework for watertight B-rep tessellation with three key contributions. First, we introduce math- ematically rigorous definitions of critical points and critical regions that characterize local geometric behavior; our analysis proves that sampling constrained to these regions guarantees intersection-free refinement under arbitrary resolution. Second, we develop an accelerated spatial indexing structure using a novel parallel hexahedron bounding volume hierarchy, which dynamically adapts to ge- ometric complexity while minimizing the number of required critical regions. Third, we propose an improved constrained Delaunay triangulation algorithm that, when guided by critical regions, simultaneously enforces watertightness and optimal element qual- ity across surface patch boundaries. Comprehensive experimental evaluations against state-of-the-art geometric kernels (NetGen, Gmsh, and Open CASCADE) demonstrate our method’s superior performance in generating intersection-free meshes with enhanced geometric fidelity and computational efficiency.

## 1 Introduction

Computer-Aided Design (CAD) systems form the backbone of modern engineering workflows, enabling the creation, analysis, and optimization of complex geometric models. These models – typically represented as boundary representation (B-rep) solids – serve as fundamental inputs for downstream Computer-Aided engineering (CAE) and Manufacturing (CAM) processes (Gong & Feng, 2015 ; Zhang et al. , 2015). The standard processing pipeline involves geometric validation, simplification, and tessellation into meshes suitable for simulations and manufacturing operations. The generation of watertight, intersection-free triangle meshes represents not merely a geometric transformation but a critical prerequisite for reliable digital modeling, with applications spanning structural analysis, biomedical modeling (Cha et al. , 2020), motion capture (Endo et al. , 2014), and performance prediction (Park & Kang, 2024).

Figure 1 illustrates the topological hierarchy of a B-rep model. A body represents a volumetric solid bounded by shells – connected collections of faces. Each face comprises a trimmed parametric surface (typically NURBS) bounded by oriented loops (one outer, potentially multiple inner). These loops consist of edges (curve segments between vertices) with corresponding trims in the parameter domain. The geometric mapping S establishes a bijection between parameter-space trims and \(R_{3}\) edges, forming a watertight manifold representation.

While mesh generation has been extensively studied – including Delaunay refinement (Cheng et al. , 2013), advancingfront methods (Schöberl, 1997), and quad-dominant approaches (Bommes et al. , 2013) – existing techniques primarily focus on element quality metrics (aspect ratios, angle bounds) and feature alignment. Crucially, they often neglect explicit prevention of selfintersections, which can cause catastrophic CAE failures (nonphysical element penetration, stress singularities) and CAM errors (erroneous toolpaths, collisions). These issues frequently originate from challenging geometric features in CAD models (Samareh, 2005), such as knife edges, micro cuts (Gu et al. , 2001), or near intersecting loops.

Although robust methods exist for continuous-level intersection problems (Marussig & Hughes, 2018 ; Patrikalakis, 1993) and spline self-intersections (Li et al. , 2025), the discrete analog, guaranteeing intersection-free piecewise-linear approximations, remains understudied as shown in Figure 2. Our work bridges this gap through four key contributions:

Our contributions are summarized as follows:

(1) Critical region framework: We introduce mathematically rigorous critical points and regions that characterize local geometric behavior, proving that refinement within nonoverlapping critical regions guarantees intersection-free tessellation. (2) Parallel hexahedron BVH: Our novel surface-aware bounding volume hierarchy (BVH), constructed from local

## 240 | Robust tessellation of CAD models

![Figure 1](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-1-p002.png)

*Figure 1: Topological structure of a B-rep model showing the hierarchical relationship between bodies, shells, faces, loops, edges, and vertices. The parameter-space trims map to R 3 edges through the surface parametrization S.*

![Figure 2](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-2-p002.png)

*Figure 2: Continuous, non-intersecting spline geometries (left and middle: curves in R 2 ; right: surfaces in R 3) and their tessellated approximations (polylines and meshes) exhibiting unintended intersections.*

partial derivatives, provides tight geometric approximation while minimizing subdivision requirements and accelerating critical region identification. (3) Enhanced CDT algorithm: We develop a constrained Delaunay triangulation (CDT) method that leverages critical regions to simultaneously enforce watertightness and optimal element quality across patch boundaries, maintaining exact \(R_{2}\)-to-\(R_{3}\) correspondence. (4) Comprehensive validation: Extensive experiments against NetGen, Gmsh, and OpenCASCADE demonstrate our method’s superior performance in generating high-quality, watertight meshes for complex models with challenging geometric features.

The paper proceeds as follows: Section 2 reviews related work; Sections 3 and 4 present our theoretical foundations and algorithms in \(R_{2}\) and \(R_{3}\) ; Section 5 details experimental results; and Section 6 concludes with future directions.

## 2 Related Work 2.1. B-rep self-intersection

Unwanted model self-intersections can significantly degrade the visual fidelity of rendered models and introduce severe complications in downstream CAX (Computer-Aided Technologies) processes such as simulation, manufacturing, and analysis. NURBS surface-surface intersection and self-intersection problems are traditionally addressed using several classes of methods (Marussig & Hughes, 2018). Analytic methods attempt to compute intersection curves exactly by solving systems of equations derived from the parametric representations (Sederberg, 1983 ; Barto ˇn, 2011). Lattice evaluation methods discretize the domains and evaluate proximity at grid points (Lien et al. , 1987 ; Rossignac & Requicha, 1987). Subdivision methods iteratively refine surface patches while tracking potential intersections (Lin et al. , 2013 ; Park et al. , 2020). Marching methods construct approximate intersection curves incrementally based on local surface approximations (Bajaj et al. , 1988). Accurate detection and handling of surface intersections play a critical role in maintaining model quality and reliability throughout the CAD pipeline.

### 2.2 Mesh generation

Mesh generation from CAD B-rep models, particularly for surface triangulations and quadrilateral meshes, has been a significant area of research in computational geometry and CAD. Surface mesh generation encompasses three principal paradigms: direct, parametric, and hybrid methods (Owen, 1998). Direct methods construct meshes entirely in \(R_{3}\), without reference to the underlying surface parametrization. Classical examples include Delaunay triangulation and its refinement variants (Cheng et al. , 2013 ; Ruppert, 1995), advancing-front techniques (Cuillière, 1998 ; Schöberl, 1997), and octree-based subdivision (Shostko et al. , 1999 ; Yerry & Shephard, 1984), all of which excel in automation and robustness. However, these approaches often require excessive refinement to conform to intricate trimming curves and may produce poorly shaped elements in regions of high curvature.

Parametric methods (Cripps & Parwana, 2011 ; Sheng & Hirsch, 1992) leverage the bijective mapping S : ⊂ \(R_{2}\) → \(R_{3}\) of NURBS or spline patches. A high-quality two-dimensional mesh-often Journal of computational Design and engineering, 2026, 13(1), 239–258 | 241

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-3-p003.png)

*Figure 3: OBB calculation for a NURBS curve. The process involves: Construct a rotation system R by connecting the first and last control points; Transform the curve using R ; Calculate axis-aligned bounding box (AABB) of the transformed control points; Transform AABB back using R − 1 to get the OBB.*

![Figure 4](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-4-p003.png)

*Figure 4: If the control-polygon angles relative to the initial tangent at C (0) = CV 0 are increasing, then the angle function θ (t) is also increasing for t ∈ [0, 1] .*

generated by structured quad layouts (Lu et al. , 2022) or planar Delaunay triangulations-is first constructed in the parameter domain. The mesh is then mapped onto the surface via S. To avoid poor-quality meshes resulting from distorted parametric surfaces after mapping, field-based methods (Borouchaki et al. , 1998 ; De Goes et al. , 2016) incorporate local geometric properties into the parameter domain, thereby improving mesh quality.

### 2.3 Mesh repair and quality improvement

Mesh repair and quality improvement aim to detect, correct, and optimize mesh models, ensuring topological correctness, geometric consistency, and mesh regularity (Attene et al. , 2013 ; Ju, 2009). Since mesh self-intersections typically occur within extremely localized regions, detection and correction often involve substantial computational expense.

Metrics such as element aspect ratio, minimum angle, surface fairness, and alignment with underlying geometry are typically used to guide optimization. Guo et al. (2019) proposes a remeshing algorithm to improve the regularity and angle quality. Attene (2010) presents a method to remove local degenerate or intersecting elements. Pekerman et al. (2008) proposes a method for calculating and eliminating model self-intersections. Charton et al. (2020) utilizes topology graphs to repair meshes.

## 3 Tessellation in R

This section addresses the self-intersection-free tessellation of planar loops composed of spline curves. To guarantee geometric consistency and topological correctness in the resulting polygonal representation, we classify and treat three core scenarios encountered during planar curve tessellation:

(1) Inter-curve tessellation. To ensure non-intersecting tessellation between two curves \(C_{1}\) and \(C_{2}\), we introduce the concept of critical points, derived from the convex hulls of curve subsegments. We prove that as long as the tessellation includes these critical points, the resulting polylines are guaranteed to be non-intersecting. (2) Endpoint-adjacent tessellation. When two curve segments share a common endpoint and have nearly identical tangent directions, convex hull-based separation may fail due to local collinearity. To address this, we introduce angular monotonicity and a separation vector condition. The two conditions ensure that the resulting polylines preserve the original relative orientation and avoid intersection. (3) Intra-curve tessellation. We prove that if a curve segment is monotonic in a given coordinate direction, its tessellation yields a self-intersection-free polyline, and we provide an efficient method for selecting such a coordinate direction.

### 3.1 Inter-curve tessellation

Let \(C_{1}\) (s) and \(C_{2}\) (t), with s, t ∈ [0, 1] , be two NURBS curves in \(R_{2}\) that are geometrically close but do not intersect. Our goal is to construct piecewise-linear approximations \(L_{1}\) and \(L_{2}\) such that \(L_{1}\) ∩ \(L_{2}\) = ∅ , even under further refinement.

To achieve this, we first introduce the concept of critical points and then prove their key property in Lemma 1.

Definition 1 (critical point). Let \(C_{1}\) (s) : [0, 1] → \(R_{2}\) and \(C_{2}\) (t) : [0, 1] → \(R_{2}\) be two NURBS curves satisfying \(C_{1}\) (s) ̸ = \(C_{2}\) (t) for all s, t ∈ [0, 1] . A pair of partitions

### 3.2 Endpoint-adjacent tessellation

When two curves share a common endpoint and exhibit similar tangents, naive tessellation may introduce artificial intersections near the junction. This issue arises when the tessellated polylines fail to preserve the original angular ordering of the curves – e.g., reversing their relative orientation, as illustrated in the left of Figure 2. To address this, we introduce the concept of angular monotonicity and separation vector, which guides the placement of the first sampling points on each curve. The separation vector ensures that the piecewise-linear approximations initiate from directions that preserve the original orientation and avoid crossing.

#### 3.2.1 Angular monotonicity

We require that each curve involved satisfy the Angular Monotonicity condition: that is, any straight line through the endpoint intersects the control polygon in at most one location (excluding the endpoint). This condition guarantees that as the curve parameter increases, the angle between the position vector −−−−−→ \(C(0)\) \(C(t)\) and the initial tangent vector T = C ′ (0) increases monotonically. Thus, the curve’s sampled direction evolves in a single rotational direction and avoids reversal, as shown in Figure 4. Importantly, this condition can be efficiently verified via the control polygon alone, without evaluating the spline curve geometry, making it well-suited for engineering applications. If the condition is not satisfied, we recursively subdivide the curve until it holds on each local segment.

#### 3.2.2 Separation vector

Let \(C_{1}\) and \(C_{2}\) be two NURBS curves with shared endpoint \(C_{1}\) (0) = \(C_{2}\) (0), which we denote by \(C(0)\), and initial tangents T 1 = C ′ 1 (0), T 2 = C ′ 2 (0). We define a vector D ∈ \(R_{2}\), the separation vector, such that the vectors from the common endpoint to the first sampling

sign (det (D, \(V_{1}\))) ̸ = sign (det (D, \(V_{2}\))), where det (a, b) = a x b y − a y b x, whose sign indicates their relative orientation. This condition ensures that the first tessellation segments lie on opposite sides of D, thereby preventing intersection and preserving angular separation. The separation vector D is computed according to the local geometry at \(C(0)\), with three cases shown in Figure 5 : r Case 1: Opposing curvature directions. If the two curves bend in opposite directions near \(C(0)\), we define:

D = \(T_{1}\) ∥ \(T_{1}\) ∥ + \(T_{2}\) ∥ \(T_{2}\) ∥ , i.e., the average of the normalized tangents. This vector bisects the angle between the curves and separates their initial sampling directions. r Case 2: Same curvature, distinct tangents. When the curves bend in the same direction but have different tangents, we use the same bisector formulation. The sign of angular deviation between the tangents determines which side each curve samples from. r Case 3: Identical curvature and tangent. When the two curves share both tangent and curvature direction at \(C(0)\), we select the curve \(C_{i}\) with the smaller n th-order derivative (i.e., less curved).We then locate a nearby point \(C_{i}(t)\) on this flatter curve guided by the target maximum mesh edge length from Journal of computational Design and engineering, 2026, 13(1), 239–258 | 243

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-6-p005.png)

*Figure 6: Workflow of our algorithm. Our method ensures the generation of watertight, high-quality mesh without self-intersections through four steps.*

![Figure 7](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-7-p005.png)

*Figure 7: Construction of the parallel hexahedron bounding volume and comparison with alternative bounding volumes. The computation pipeline comprises: construct a non-rigid rotation system R ; transform the surface using R ; calculate AABB of the transformed surface; transform AABB back using R − 1 to get the parallel hexahedron. The right side of the figure provides a visual comparison with two other common bounding volumes.*

the shared endpoint and define:

$$
D = −−−−−→ C (0) C i ( t ) .
$$

This guarantees a divergence direction even in higher-order degenerate cases. The separation vector framework is applied to all endpointadjacent tessellation cases. Combined with the angular monotonicity condition, it ensures that initial sampling segments of the curves respect the original orientation and remain nonintersecting.

### 3.3 Intra-curve tessellation

Consider a planar spline curve \(C(t)\) : [0, 1] → \(R_{2}\) defined by control points { \(P_{0}\), \(P_{1}\), . . . , P n. To ensure the resulting tessellation is free of self-intersections, we examine the monotonicity of the curve in a locally defined coordinate direction.

Specifically, we define a local coordinate axis using the vector V = −−→ \(P_{0}\) P n, connecting the first and last control points. This vector serves as a projection direction. If the projection coordinates of all control points onto V form a strictly increasing sequence:

then the curve is said to be monotonic in direction V.

By the convex hull and variation-diminishing properties of spline curves (Piegl & Tiller, 2012), this condition implies that the entire curve lies within a convex region bounded by a monotonic polygonal chain, and any line orthogonal to V intersects the curve at most once. Consequently, a tessellated polyline generated by uniformly or adaptively sampling the curve in parameter order will be self-intersection-free.

This directional monotonicity condition can be efficiently verified using only control points, making it practical for preprocessing in engineering applications. When the condition is not met, the curve can be subdivided until the property holds locally on each subsegment.

## 242 | Robust tessellation of CAD models

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-5-p004.png)

*Figure 5: Sampling at a shared endpoint C (0) of curves C 1 and C 2 using the separation vector D. (A), (B), and (C) represent the cases of opposite curvature directions, same curvature direction with different tangents, and identical curvature and tangent, respectively. T denotes the common tangent direction (T = T 1 = T 2).*

are called critical points for the pair (\(C_{1}\), \(C_{2}\)) if, for every i ∈ { 0, 1, . . . , n − 1 } and j ∈ { 0, 1, . . . , m − 1, the convex hulls of the corresponding curve subsegments are disjoint:

$$
conv ( C 1 | [ s i , s i + 1 ] ) ∩ conv ( C 2 | [ t j , t j + 1 ] ) = ∅ .
$$

Lemma 1 (Non-intersection via Critical Points). Let \(C_{1}\) and \(C_{2}\) be two non-intersecting NURBS curves. If S and T are critical points for (\(C_{1}\), \(C_{2}\)) as per definition 1, then the polylines obtained by connecting consecutive points in S and T are guaranteed to be nonintersecting. Furthermore, this non-intersection property is preserved under any refinement of the critical points.

Formally, define the polylines:

(1) \(L_{1}\) ∩ \(L_{2}\) = ∅ . (2) For any refinement S ′ ⊇ S and T ′ ⊇ T, the corresponding refined polylines L ′ 1 and L ′ 2 also satisfy L ′ 1 ∩ L ′ 2 = ∅ . The detailed proof of Lemma 1 is presented in Appendix A. To compute critical points for inter-curve tessellation, we first construct oriented bounding boxes (OBBs) for each curve segment as shown in Figure 3. For every pair of non-adjacent curves, we check OBB intersections. If detected, the corresponding segments are subdivided at midpoints. This process iterates recursively: new OBBs are computed for subdivided segments, and intersection checks continue until all OBBs from different curves are disjoint. The resulting subdivision points become the critical points, ensuring the final tessellation avoids artificial intersections.

## 4 Tessellation of B-Rep Models

Given a B-rep model composed of trimmed NURBS surfaces, we propose a robust and watertight tessellation framework that ensures non-self-intersecting and high-quality meshes. The method proceeds in four major steps: (1) boundary tessellation, (2) critical region computation, (3) interior triangulation via CDT, and (4) \(R_{3}\) mapping and optimization. As shown in Figure 6.

### 4.1 Boundary tessellation

To ensure watertightness and topological consistency across adjacent trimmed surfaces, we first perform precise boundary sampling guided by bothparameter-domain topology and geometric intersections in \(R_{3}\). Specifically:

### 4.2 Critical region computation

To prevent mutual intersections between tessellated surfaces, we adopt an adaptive and geometry-aware surface subdivision strategy that identifies non-overlapping surface regions, called critical regions.

Definition 2 (critical region). Let \(S_{1}\) (u, v) : 1 → \(R_{3}\) and \(S_{2}\) (s, t) : 2 → \(R_{3}\) be two NURBS surface patches with \(S_{1}\) (u, v) ̸ = \(S_{2}\) (s, t) for all (u, v) ∈ 1, (s, t) ∈ 2. A pair of domain partitions

\(R_{1}\) = { \(R_{1}\), 1, \(R_{1}\), 2, . . . , \(R_{1}\), n, \(R_{1}\), k ∩ \(R_{1}\), l = ∅ ( ∀ k ̸ = l), \(R_{2}\) = { \(R_{2}\), 1, \(R_{2}\), 2, . . . , \(R_{2}\), m, \(R_{2}\), p ∩ \(R_{2}\), q = ∅ ( ∀ p ̸ = q), are called critical regions for the pair (\(S_{1}\), \(S_{2}\)) if, for every k ∈ { 1, . . . , n \(\wp\) and p ∈ { 1, . . . , m, the convex hulls of the corresponding surface subpatches are disjoint:

Lemma 2 (Non-intersection via Critical Regions). Let \(S_{1}\) and \(S_{2}\) be two \(C_{2}\)-continuous non-intersecting NURBS surface patches with critical regions \(R_{1}\) and \(R_{2}\) as definition 2. Then, any pair of triangle meshes ˆ \(M_{1}\) and ˆ \(M_{2}\), generated by triangulating the parameter domains 1 and 2 such that each triangle lies within a single critical region and then mapping to \(R_{3}\), are guaranteed to be disjoint.

Formally, if M 1 is a triangulation of 1 with △ ⊂ \(R_{1}\), k for some k for every △ ∈ M 1, and M 2 is a triangulation of 2 with △ ⊂ \(R_{2}\), p for some p for every △ ∈ M 2, then the spatial meshes

△ (\(S_{1}(P)\), \(S_{1}(Q)\), \(S_{1}(R)\)) | △ (P, Q, R) ∈ M 1 Journal of computational Design and engineering, 2026, 13(1), 239–258 | 245

![Figure 10](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-10-p007.png)

*Figure 10: Case 1 for R 2 curves tessellation. Self-intersection results are marked with ∗ .*

△ (\(S_{2}(P′)\), \(S_{2}(Q′)\), \(S_{2}(R′)\)) | △ (P ′ , Q ′ , R ′ ) ∈ M 2 satisfy ˆ △ 1 ∩ ˆ △ 2 = ∅ for all ˆ △ 1 ∈ ˆ M 1 and ˆ △ 2 ∈ ˆ M 2.

The detailed proof of Lemma 2 is presented in Appendix B. A fundamental property of NURBS states that refining the knot vectors-the essence of surface subdivision-brings the control net closer to the surface, with the net converging to the surface in the limit (Piegl & Tiller, 2012). Specifically, recursive midpoint subdivision of curves and surfaces exhibits quadratic convergence (Filip et al. , 1986), ensuring that the approximation error decreases rapidly with each refinement step. Consequently, for two initially disjoint surfaces with a positive minimal geometric distance, the convex hulls of their subdivided patches will converge toward the actual surfaces. This guarantees that the convex hulls will eventually become disjoint once their size, under a suitable metric, is reduced below the initial separation distance. This mechanism ensures that the recursive subdivision process terminates after a finite number of refinements.

```text
Algorithm 1 constructs a surface-aware BVH to identify crit- ical regions by initializing root nodes for each surface and it- eratively refining potentially intersecting node pairs through a queue-based process. For each pair, the algorithm computes par- allel hexahedron bounding volumes, checks their intersection sta- tus, and continues subdivision only when volumes intersect, not outside the loop, and exceed the precision threshold l .
```

For engineering implementation, the precision threshold l is adopted to balance efficiency and accuracy. When the diagonal length of the current subregion’s bounding volume falls below this threshold, the region is triangulated, and intersection testing of the resulting triangular meshes is performed to ensure a nonintersecting mesh. This precision-controlled strategy prevents redundant computations caused by excessive subdivision.

In the worst case where all surface pairs intersect and require refinement to depth D ≈ log (d initial / l) (with d initial being the initial bounding volume diagonal), the time complexity is \(O(F2·4D)\) due

```text
Algorithm 1 B-rep BVH Construction Require: A B-rep model M , threshold l Ensure: BVH structure 1: N ← ∅ ▷ Initialize node list 2: for each surface S i in M do
```

6: for each node N i in N do 7: for each node N j in N \ { N i } do 8: Q ← ∅ ▷ Initialize queue with node pairs

9: push (Q, ⟨ N i, N j ⟩ ) 10: while Q ̸ = ∅ do 11: ⟨ N s, N t ⟩ ← pop (Q) 12: PH s ← computeParallelHexahedron (N s) 13: PH t ← computeParallelHexahedron (N t) 14: if not intersect (P H s, P H t) then 16: else if not insideLoop (N s) or not insideLoop (N t) then 18: else if diagonal (PH s) < l and diagonal (PH t) < l then

23: for i, j ∈ { 1, 2 } do

to exponential queue growth, where F denotes the total number of surfaces in the B-rep model. In practical implementations, the

### 4.3 Interior tessellation via CDT

Following boundary and critical region sampling, we perform surface tessellation in the parameter domain using CDT as shown in algorithm 2. This step generates a valid interior mesh while ensuring:

r Watertightness: Tessellated boundary curves (loop samples and mapped intersection points) remain fixed to preserve point-to-point consistency. r intersection freedom: Critical region boundaries derived from BVH are allowed to be adaptively resampled and refined.

The density of the output mesh is governed by the quality metric (e.g., minimal angle and maximal edge length), which directly determines the termination of the refinement process by controlling the insertion of new vertices. The algorithm exhibits a worstcase time complexity of \(O(n2)\), where n is the number of vertices in the final mesh, although its average-case performance is often closer to \(O(nlogn)\) in practice. Furthermore, the computational cost of key operations, such as point location and neighborhood queries during incremental insertion and edge flipping, can be significantly reduced by employing spatial indexing structures like a quadtree, leading to substantial practical acceleration. As shown in Figure 9, the CDT process maintains separation between surface patches and honors boundary fidelity, balancing quality and robustness.

Journal of computational Design and engineering, 2026, 13(1), 239–258 | 247

![Figure 12](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-12-p009.png)

*Figure 12: Case 3 for R 2 loops tessellation.*

![Figure 13](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-13-p009.png)

*Figure 13: Case 4 for R 2 loops tessellation.*

### 4.4 Mesh mapping and optimization

After obtaining the parameter domain mesh, we map it to \(R_{3}\) space by evaluating the NURBS surface function at the vertex coordinates of each triangle. This process transforms the 2D parameter-domain triangles into a set of 3D spatial triangles that piecewise linearly approximate the original surface geometry. Thanks to the constraints in previous stepssuch as the one-to-one correspondence of shared boundary points and the consistent cross-mapping of critical points-the resulting \(R_{3}\) mesh is inherently watertight and topologically consistent.

Although critical regions ensure non-intersection between surface patches, poorly parameterized surfaces still lead to low-quality local meshes, such as degeneration and distortion. To address this, we eliminate mesh degeneration through mesh optimization operations. For specific implementation details, refer

## 244 | Robust tessellation of CAD models

![Figure 8](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-8-p006.png)

*Figure 8: Computation of critical regions between surfaces. For two surfaces with poor parametrization, our method generates uniform critical region subdivisions based on their geometric features.*

![Figure 9](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-9-p006.png)

*Figure 9: One surface’s critical region and its tessellated triangles. The outer, inner boundary edges and critical region edges serve as constraints for CDT, which can be resampled by linear interpolation. The fixed edge points ensure a one-to-one mapping between surfaces and watertightness.*

r Parameter loop critical points: Each loop is tessellated satisfying inter-curve, endpoint-adjacent and intra-curve tessellation conditions, as introduced in Section 3. This ensures the tessellated points from each parameter-domain loop remain non-intersecting, maintaining the topological validity of the trimmed surface representation. r Cross-parametric mapping: For adjacent surfaces sharing a common edge with parameter-domain trimming curves \(C_{1}\) (s) and \(C_{2}\) (t), each tessellated point \(C_{1}\) (s i) is mapped to \(C_{2}\) (t j) by solving \(S_{1}\) (\(C_{1}\) (s i)) = \(S_{2}\) (\(C_{2}\) (t j)), where \(S_{1}\) and \(S_{2}\) are the surface mappings, ensuring the corresponding 3D points coincide exactly on the shared edge. This bidirectional mapping maintains consistent point ordering between trims while preserving geometric watertightness and topological consistency through identical 3D point generation from both parametrizations. r Edge tessellation: For every shared edge E ⊂ \(R_{3}\), we use arc-length parametrization to sample discrete points { \(E(ξi)\). These points are then projected back onto the parameter domains of the intersecting boundary curves to obtain corresponding points \(C_{1}\) (s i) ∈ \(S_{1}\) and \(C_{2}\) (t i) ∈ \(S_{2}\), solving

$$
S 1 ( C 1 ( s i )) = S 2 ( C 2 ( t i )) = E ( ξ i ) , ∀ i .
$$

These steps collectively ensure that the boundary tessellation is watertight across surface patches, enabling consistent mesh construction without introducing cracks or mismatches.

Our method can be generalized to non-manifold edges by extending the bidirectional mapping to a multi-way constraint. For surfaces \(S_{1}\), \(S_{2}\), \(S_{3}\), . . . meeting at an edge E, we solve \(S_{1}\) (\(C_{1}\) (s i)) = \(S_{2}\) (\(C_{2}\) (t j)) = \(S_{3}\) (\(C_{3}\) (\(u_{k}\))) = \(E(ξl)\) for a consistent \(R_{3}\) discretization \(E(ξl)\). This ensures identical vertices across all patches for a watertight mesh. This method, however, requires valid B-rep topology and cannot handle T-junctions, which violate the mapping’s topological assumptions.

## 246 | Robust tessellation of CAD models

![Figure 11](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-11-p008.png)

*Figure 11: Case 2 for R 2 curves tessellation.*

algorithm’s efficiency is enhanced by reusing sub-surface bounding volume computations and employing early BVH pruning for sparse geometries.

We adopt a special type of convex hull, namely the parallel hexahedron, to rapidly compute the critical regions. To compute the parallel hexahedron bounding volume of a NURBS surface patch, we first evaluate the partial derivatives at the patch center (\(u^{c}\), \(v^{c}\)) :

These vectors define two axes of a local, generally non-orthogonal coordinate system:

We then construct a transformation matrix R = [\(e_{1}\) \(e_{2}\) \(e_{3}\)] from the global coordinate system to this local frame. Figure 7 illustrates the construction process: all control points of the patch are transformed into the local frame using R, and the AABB of these transformed points is computed. Applying the inverse transformation R − 1 (provided that R is invertible and well-conditioned) to this AABB yields the parallel hexahedron bounding volume in the original global coordinates. As shown in Figure 7, OBB provides a tighter fit than AABB by better capturing the surface’s orientation. However, our proposed parallel hexahedron further improves upon OBB by explicitly accounting for the strong non-orthogonality often present in the parametric directions of NURBS surfaces. As a result, parallel hexahedron yields a higher approximation fidelity for the same surface geometry, especially in regions with significant distortion or anisotropy. Specifically, we choose to subdivide the surface along the parameter direction with a longer boundary arc length. This directional refinement enhances the resolution along elongated regions of the surface and improves bounding volume accuracy under anisotropic parametrizations. As shown in Figure 8, our method generates well-adapted BVH for slender surface patches. This approach effectively captures the local geometric anisotropy of the surface patch and provides a tighter bounding volume than the standard AABB.

## 248 | Robust tessellation of CAD models

![Figure 14](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-14-p010.png)

*Figure 14: Eight CAD models tessellated with our method, demonstrating its effectiveness and generality across a variety of geometric features and complexities.*

algorithm 2 Constrained Delaunay Triangulation with Critical Regions Require: Outer boundary edge set B out, inner boundary edge set B in, critical region edge set C Ensure: A constrained Delaunay triangular mesh \(M_{1}\): Initialize a large bounding triangle M containing all vertices of B out ∪ B in ∪ \(C_{2}\): Incrementally insert all vertices from B out ∪ B in ∪ C into M to form an initial Delaunay triangulation 3: for each segment b in B out ∪ B in ∪ C do 4: if b is already present as an edge in M then 5: Mark b as frozen

7: Restore b by iteratively flipping edges in M that intersect with it 8: Mark the recovered edge b as frozen

11: Compute a priority queue Q of bad triangles in M sorted by a quality metric 12: while Q is not empty do 13: Pop the worst triangle △ from Q and compute its circumcenter \(c_{14}\): if c encroaches upon any frozen edge e in B out ∪ B in ∪ C then 15: if e ∈ B out ∪ B in then ▷ Encroachment on domain boundary 17: else ▷ Encroachment on internal critical region edge 18: Split e at its midpoint m, insert m into M, and update Q

21: Insert c into M, perform edge flips to restore the Delaunay property locally 22: Update the triangle quality queue Q

25: Delete all triangles from M that lie inside any inner boundary or outside the outer boundary 26: return the final mesh M to the discussions on mesh repair and quality improvement in Section 2.

## 5 Results

All experiments were performed on a workstation equipped with an Intel i7-12750HX CPU, 32 GB of RAM, and an NVIDIA RTX 4060 Ti GPU. To ensure fair comparison, we disabled multi-threading and GPU acceleration across all tools, and performed all computations in single-threaded CPU mode. Our evaluation covers a broad set of models from the GrabCAD (GrabCAD, 2025) and ABC datasets (Koch et al. , 2019). While we tested our method on a large number of cases to verify general robustness (see Appendix C for additional results on 75 models), we specifically selected the following representative examples for detailed comparison due to their high geometric complexity and challenging topological features.

### 5.1 Tessellation of R 2 curves and loops

We evaluate our \(R_{2}\) tessellation framework through a series of experiments on individual curve segments and closed loops. This section presents both the constructed hierarchical bounding volumes in the parametric domain and the resulting tessellated polylines guided by critical points. For comparison, we include three widely used strategies: uniform sampling (20 segments per curve’s parameter domain), curvature-adaptive sampling, and arc-length-based sampling. As shown in Figures 10 – 13, our method consistently produces non-intersecting polylines by leveraging a hierarchy of disjoint bounding regions and carefully selected critical points. In contrast, uniform sampling performs well only when curve lengths are relatively balanced; it tends to oversample short curves and undersample long ones. Arc-length sampling achieves consistent geometric spacing based on cumulative length, while curvaturebased sampling increases density in highly curved regions, capturing shape variation more effectively. However, none of the three conventional methods can guarantee self-intersection-free results in general. Our approach addresses this limitation by enforcing non-overlapping convex hulls during refinement, enabling robust and intersection-free Journal of computational Design and engineering, 2026, 13(1), 239–258 | 249 tessellation even in challenging configurations such as sharp junctions and densely packed loops.

![Figure 15](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-15-p011.png)

*Figure 15: Visual comparison with other methods. Surface self-intersections are highlighted in red, and regions with significant geometric errors are locally magnified for clarity.*

It is important to emphasize that the resulting tessellation represents the minimal number of segments required by our method to guarantee non-intersecting curves. Furthermore, any additional sampling-whether uniform or adaptive-can be safely inserted without introducing intersections.

### 5.2 Bounding volume comparison experiment

In this experiment, we compare two types of bounding volumesAABB and our proposed parallel hexahedron-for constructing critical regions. The comparison is conducted across three key metrics: the number of bounding volumes, total bounding volume, and computation time.

The total volume of all bounding volumes reflects how well the geometry of the surface is approximated: a smaller total volume indicates a tighter and more accurate fit to the B-rep geometry. As shown in Tables 1 and 2, our parallel hexahedron approach achieves much higher approximation accuracy (as measured by total bounding volume’s volume) compared to AABB, while using fewer bounding volumes and incurring lower computation time. This significant reduction in the number of bounding volumes not only speeds up the computation, but also leads to a smaller number of larger critical regions. This coarser yet precise regionalization offers greater flexibility for downstream mesh refinement,

### 5.3 B-rep tessellation using our method

In this section, we present the results and performance of applying our method to tessellation models. We selected a series of representative CAD models covering a wide range of geometric and topological complexities – from simple, smooth surfaces to highly intricate models with interlaced components and hundreds of NURBS patches, as shown in Figure 14. All generated meshes are self-intersection-free. Table 3 lists the time required for each step, including boundary tessellation, critical region, and CDT. It also includes the total computation time and relevant metrics such as the number of faces generated, the Scaled Jacobian, and the skewness of the resulting mesh. As shown in Figure 14 and Table 3, the proposed method demonstrates stable performance across models of varying complexity. The overall runtime increases with the number of surface patches, the target mesh density, and the geometric intricacy of the model. In particular, the critical region detection stage dominates the computation time for models with highly curved or tightly packed surfaces, while boundary tessellation and CDT meshing contribute relatively minor portions. These results indicate that the method scales efficiently with model complexity and maintains consistent mesh quality in terms of scaled Jacobian and skewness metrics.

### 5.4 B-rep tessellation comparison with other methods

We conduct a comprehensive comparison of mesh generation quality using four different methods: NetGen (Schöberl, 1997), Gmsh (Geuzaine & Remacle, 2009), OpenCASCADE(OCC) (Open CASCADE Technology, 2025), and our proposed approach across six CAD B-rep test cases, with challenges such as high curvature, tight gaps, and surface-surface tangency. The visual results are shown in Figure 15, and quantitative metrics are summarized in Table 4. Evaluation criteria include mesh generation time, triangle count, number of self-intersections, Scaled Jacobian and Skew (computed via VTK library; Schroeder et al. , 2000), and Hausdorff Journal of computational Design and engineering, 2026, 13(1), 239–258 | 251 Table 3: Performance comparison of different tessellation methods for B-rep Models. “Surfaces” refers to the number of NURBS surfaces in the B-rep model, and “Faces” refers to the number of generated triangular meshes. We use B.T. to denote boundary tessellation, C.R. to denote critical region, S.J. to denote Scaled Jacobian, and H.D. to represent Hausdorff Distance. Hausdorff distances are scaled by 100 for readability.

Test case Surfaces B.T. C.R. CDT Total Faces(k) S.J. Skewness H.D.

Gear 1 306 0.34 8.01 2.06 11.2 56.7 0.69 0.34 0.03 Gear 2 174 0.24 5.40 3.56 10.18 460.6 0.72 0.37 0.02 Fuel injector 375 0.87 13.12 0.67 15.45 49.5 0.70 0.33 0.10 Shaft 179 0.25 4.75 0.50 6.26 34.2 0.72 0.32 0.06 Wheel hub 649 1.25 40.23 2.13 45.78 140.8 0.71 0.33 0.13 Mobius ring 136 0.18 7.05 1.67 9.58 161.1 0.65 0.38 0.08 Front wing 128 0.41 4.67 0.73 6.7 92.9 0.75 0.38 0.06 Motovario 362 0.69 21.88 7.52 32.84 780.2 0.68 0.34 0.04

Table 4: Comparison of mesh generation results across six test cases and four methods. Self-intersections (SI) are counted, and Hausdorff distances are scaled by 100 for readability. We use S.J. to denote Scaled Jacobian and H.D. to represent Hausdorff Distance. Methods that produce mesh self-intersections or failures are marked with “ ∗ ”.

Test case Method Time (s) Faces(k) SI Num S.J. Skewness H.D.

Turbine Netgen 8.46 98.4 0 0.84 0.21 3.43 Gmsh ∗ 1.62 96.0 8485 0.53 0.51 2.03 OCC ∗ 0.39 186.9 36 0.57 0.49 2.39 Ours 4.13 86.7 0 0.68 0.36 2.48 Lens protector Netgen 4.58 50.2 0 0.89 0.15 2.33 Gmsh ∗ 88.23 809.0 188 0.83 0.20 224.99 OCC 0.49 12.5 0 0.52 0.53 2.57 Ours 3.54 33.6 0 0.76 0.29 2.24 Wheel set Netgen ∗ 18.54 30.8 4 0.83 0.22 1.78 Gmsh ∗ 1.12 27.5 259 0.54 0.52 1.66 OCC 0.10 22.2 0 0.62 0.44 0.35 Ours 3.73 21.5 0 0.74 0.31 0.33 Glass artwork Netgen ∗ Crash – – – – – Gmsh ∗ 5.42 211.4 15410 0.40 0.64 1.85 OCC ∗ 1.58 163.3 36 0.55 0.51 1.31 Ours 9.24 201.8 0 0.71 0.47 0.72 Break disc-1 Netgen 6.56 36.0 0 0.91 0.13 0.07 Gmsh ∗ 2.29 54.9 234 0.69 0.37 0.06 OCC 3.07 65.5 0 0.03 0.98 0.02 Ours 4.87 74.6 0 0.71 0.32 0.05 Break disc-2 Netgen 9.05 56.6 0 0.92 0.12 0.08 Gmsh ∗ 2.08 146.2 2060 0.65 0.41 0.03 OCC 6.73 183.7 0 0.25 0.77 0.03 Ours 4.26 45.8 0 0.72 0.34 0.03 distance [computed using Metro tool (Cignoni et al. , 1998), scaled by 100 for readability]. It is worth noting that the tessellation functionality provided by OCC is primarily designed for visualization purposes, rather than for producing high-quality meshes suitable for CAE/CAM applications. In contrast, both NetGen and Gmsh are specialized mesh generation tools intended for numerical simulations and engineering analysis. In our comparative experiments, we carefully adjusted mesh density parameters across all mesh generation methods to control the resulting number of faces to within a comparable order of magnitude. This calibration helps ensure a fairer basis for evaluating performance metrics. We present detailed visual comparisons for selected test cases (see Figure 16), highlighting boundary behavior and watertightness. As shown in the insets, both NetGen and our proposed method successfully generate watertight meshes along surface boundaries, preserving topological consistency across adjacent patches. In contrast, Gmsh and OCC often introduce gaps or misaligned vertices at patch interfaces, leading to non-watertight meshes in regions where surface stitching is required. Netgen generates uniformly distributed meshes that are close to equilateral triangles, and its output typically exhibits high element quality in terms of metrics like skewness and Scaled Jacobian. It performs local refinement near sharp edges and boundary features, which helps preserve geometric fidelity in those regions. However, this quality comes at a cost-Netgen is computationally expensive and struggles with complex topologies. It fails entirely on intricate models such as the Glass Artwork, and produces degenerate or collapsed elements on tubular or narrow features, as observed in the Wheel Set example. Gmsh, on the other hand, is significantly faster. However, its aggressive meshing strategy often leads to non-watertight meshes, particularly around surface boundaries. It also suffers from

## 250 | Robust tessellation of CAD models

![Figure 16](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-16-p012.png)

*Figure 16: Close-up comparison of watertightness in two local regions across four meshing methods: Gmsh, Netgen, OCC, and Ours. Each row shows a magnified view of a distinct surface junction. Non-watertight regions are enclosed in red boxes. While Netgen and our method maintain consistent watertight connections, Gmsh and OCC exhibit visible gaps or misalignments at patch boundaries.*

Table 1: Comparison of critical region construction for case turbine using different bounding volume strategies.

Table 2: Comparison of critical region construction for case mobius ring using different bounding volume strategies.

allowing higher-quality tessellation with fewer self-intersection constraints.

## 252 | Robust tessellation of CAD models

self-intersections on thin structures. Gmsh demonstrates limitations in handling narrow and slender features: it frequently exhibits element collapse, loss of face connectivity, and degraded topological integrity in such cases.

OCC generates meshes rapidly and robustly across all test cases and maintains good patch coverage. Nevertheless, its approach lacks sufficient interior refinement in some surface regions, leading to lower overall mesh quality and uneven distribution of triangle density. Moreover, OCC occasionally produces non-watertight meshes at surface patch junctions, where gaps or overlaps remain between adjacent surfaces.

Overall, our method demonstrates superior robustness and generality, as evidenced by the comprehensive experimental results. By incorporating critical regions and adaptive sampling, our approach produces high-quality, watertight, and intersection-free tessellations across a diverse range of CAD inputs. Notably, it is the only method that consistently succeeds in generating nonself-intersecting meshes for all benchmark cases, including those with sharp features, narrow passages, and complex patch topologies.

## 6 Conclusion and Future Work

We have presented a robust and general framework for the selfintersection-free tessellation of B-rep models, integrating critical points and critical regions, adaptive bounding volumes, and high-quality constrained Delaunay triangulation. Our method guarantees watertightness, topological consistency, and high mesh quality, even in the presence of narrow surface features and complex trimming configurations. By establishing theoretical guarantees in both \(R_{2}\) and \(R_{3}\) settings, and validating against industrial-strength geometric kernels, we demonstrate that the proposed framework offers a reliable solution for downstream CAD, CAE, and CAM applications.

Despite these advances, challenges remain. A primary limitation is that our current framework assumes a geometrically valid B-rep input; consequently, it does not handle models with pre-existing geometric errors, such as overlapping surfaces, intersecting components, or complex assemblies with inter-part collisions. Additionally, while our method significantly reduces distortion through parallel hexahedron-guided bounding volumes, anisotropic subdivision, and local mesh optimization, it can still struggle to produce high-quality elements on severely distorted or degenerate surfaces. In future work, we plan to investigate techniques for robust preprocessing to repair such invalid geometries and regularize pathological surface patches. Additionally, we aim to explore alternative partitioning schemes, such as nonmidpoint or non-rectangular subdivision, to compute a minimal set of critical regions, thereby further optimizing computational efficiency.

Conflicts of Interest The authors declare no competing interests.

Author Contributions Gangyi Li: Conceptualization, Methodology, Software, Writing. Zhongxuan Luo: Writing-Review and Editing, Supervision. Yuhao Feng: Methodology, Software. Lingfeng Zhang: Methodology, Software. Yuqiao Gai: Visualization, Software. Na Lei: Conceptualization, Writing-Review and Editing.

This work is supported by the National Natural Science Foundation of China T2225012, 12494550, and 12494554.

The data underlying this article are available in the public domain. The ABC Dataset can be accessed at https://deep-geometry.gith ub.io/abc-dataset/ . Additional CAD models were derived from the GrabCAD community library at https://grabcad.com/library.

## 254 | Robust tessellation of CAD models

$$
S ′ is L ′ 1 = n − 1 i = 0 p i − 1 k = 0
$$

By the convex hull property of NURBS curves (Piegl & Tiller, 2012), for any subinterval [s i, k, s i, k + 1] ⊆ [s i, s i + 1] , the convex hull of the subsegment \(C_{1}\) | [s i, k, s i, k + 1] satisfies conv (\(C_{1}\) | [s i, k, s i, k + 1] ) ⊆ conv (\(C_{1}\) | [s i, s i + 1] ) = \(B_{1}\), i. Since \(C_{1}\) (s i, k) \(C_{1}\) (s i, k + 1) ⊆ conv (\(C_{1}\) | [s i, k, s i, k + 1] ), all refined segments of L ′ 1 within [s i, s i + 1] are contained in \(B_{1}\), i. Similarly, let T ′ be an arbitrary refinement of T : every original interval [t j, t j + 1] (with t j, t j + 1 ∈ T) is partitioned into q j − 1 l = 0 [t j, l, t j, l + 1] (q j ≥ 1, t j, 0 = t j, t j, q j = t j + 1) in T ′ , and the refined polyline L ′ 2 = m − 1 j = 0 q j − 1 l = 0 \(C_{2}\) (t j, l) \(C_{2}\) (t j, l + 1) has all segments contained in \(B_{2}\), j. From the definition of critical points, \(B_{1}\), i ∩ \(B_{2}\), j = ∅ for all i ∈ { 0, 1, . . . , n − 1 \(\wp\) and j ∈ { 0, 1, . . . , m − 1. Thus, all refined segments of L ′ 1 and L ′ 2 lie in disjoint convex hulls, so L ′ 1 ∩ L ′ 2 = ∅ . □ Appendix B. Proof of Lemma 2 Proof. Step 1: Vertices of 3D triangles lie in subpatch convex hulls take any ˆ △ 1 ∈ ˆ \(M_{1}\) with 2D preimage △ (P, Q, R) ∈ \(M_{1}\) ⊆ \(R_{1}\), k ∗ . By definition of critical regions, P, Q, R ∈ \(R_{1}\), k ∗ implies their images satisfy \(S_{1}\) (P), \(S_{1}\) (Q), \(S_{1}\) (R) ∈ \(S_{1}\), k ∗ (where \(S_{1}\), k ∗ = \(S_{1}\) | \(R_{1}\), k ∗ ). By the convex hull property of NURBS surfaces (Piegl & Tiller, 2012), \(S_{1}\), k ∗ ⊆ \(B_{1}\), k ∗ (where \(B_{1}\), k ∗ = conv (\(S_{1}\), k ∗ ) ), so all vertices of ˆ △ 1 lie in \(B_{1}\), k ∗ .

Step 2: Entire 3D triangles are contained in convex hulls. A 3D triangle ˆ △ 1 = △ (A, B, C) (with A, B, C ∈ \(B_{1}\), k ∗ ) consists of all convex combinations of its vertices: ˆ △ 1 = { λ 1 A + λ 2 B + λ 3 C | λ 1, λ 2, λ 3 ≥ 0, λ 1 + λ 2 + λ 3 = 1. Since convex hulls are convex sets (closed under convex combinations), ˆ △ 1 ⊆ \(B_{1}\), k ∗ . By the same logic, any ˆ △ 2 ∈ ˆ \(M_{2}\) is contained in some \(B_{2}\), p ∗ (where \(B_{2}\), p ∗ = conv (\(S_{2}\), p ∗ ) ). Step 3: Non-intersection of 3D triangles. By definition of critical regions, \(B_{1}\), k ∩ \(B_{2}\), p = ∅ for all k ∈ { 1, . . . , n \(\wp\) and p ∈ { 1, . . . , m. For any ˆ △ 1 ⊆ \(B_{1}\), k ∗ and ˆ △ 2 ⊆ \(B_{2}\), p ∗ , their containment in disjoint convex hulls implies:

Conclusion All 3D triangles in ˆ M 1 are disjoint from all 3D triangles in ˆ M 2. □ Appendix C. Additional Evaluation on CAD Models This appendix presents evaluation results for 75 additional complex CAD B-rep models. Figures C1 and C2 display the visual tessellation results for all 75 models, along with statistical distributions of total computation time (Figure C3) and mesh quality metrics (Figures C4 and C5).

Journal of computational Design and engineering, 2026, 13(1), 239–258 | 255

![Figure C1](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-c1-p017.png)

*Figure C1: Visualization of tessellation results for the additional dataset (Part I).*

## 256 | Robust tessellation of CAD models

![Figure C2](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-c2-p018.png)

*Figure C2: Visualization of tessellation results for the additional dataset (Part II).*

Journal of computational Design and engineering, 2026, 13(1), 239–258 | 257

![Figure C3](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-c3-p019.png)

*Figure C3: Distribution of running times for test cases.*

![Figure C4](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-c4-p019.png)

*Figure C4: Distribution of scaled Jacobian values for test cases.*

## 258 | Robust tessellation of CAD models

![Figure C5](/Users/evanthayer/Projects/paperx/docs/2026_robust_tessellation_without_self_intersections/figures/figure-c5-p020.png)

*Figure C5: Distribution of skewness for test cases.*

Received: July 19, 2025. Revised: December 10, 2025. Accepted: December 11, 2025 © The Author(s) 2025. Published by Oxford University Press on behalf of the Society for computational Design and engineering. This is an Open Access article distributed under the terms of the Creative Commons Attribution-NonCommercial License (https://creativecommons.org/licenses/by-nc/4.0/ ), which permits non-commercial re-use, distribution, and reproduction in any medium, provided the original work is properly cited. For commercial re-use, please contact reprints@oup.com for reprints and translation rights for reprints. All other permissions can be obtained through our RightsLink service via the Permissions link on the article page on our site-for further information please contact journals.permissions@oup.com

## References

- Attene, M. (2010). A lightweight approach to repairing digitized polygon meshes. The Visual Computer, 26, 1393–1406. https://doi.org/ 10.1007/s00371-010-0416-3 Attene, M., Campen, M., & Kobbelt, L. (2013). Polygon mesh repairing: An application perspective. ACM Computing Surveys (CSUR), 45, 1– 33. https://doi.org/10.1145/2431211.2431214 Bajaj, C. L., Hoffmann, C. M., Lynch, R. E., & Hopcroft, J. (1988). Tracing surface intersections. Computer Aided Geometric Design, 5, 285–307. https://doi.org/10.1016/0167-8396(88)90010-6 Barto ˇn, M. (2011). Solving polynomial systems using no-root elimination blending schemes. Computer-Aided Design, 43, 1870–1878. https://doi.org/10.1016/j.cad.2011.09.011 Bommes, D., Lévy, B., Pietroni, N., Puppo, E., Silva, C., Tarini, M., & Zorin, D. (2013). Quad-mesh generation and processing: A survey. In Computer Graphics Forum, Vol. 32, pp. 51–76, Wiley Online Library. https://doi.org/10.1111/cgf.12014 Borouchaki, H., Hecht, F., & Frey, P. J. (1998). Mesh gradation control. International Journal for Numerical Methods in engineering, 43, 1143–1165. https://doi.org/10.1002/(SICI)1097-0207(19981130)43: 61143::AID-NME470 ⟩ 3.0.CO;2-I Cha, J., Ryu, J., Choi, J.-H., & Kim, D.-S. (2020). Medial-abc: an algorithm for the correspondence between myocardium and coronary artery mesh models based on the medial axis of coronary artery. Journal of computational Design and engineering, 7, 736– 760. https://doi.org/10.1093/jcde/qwaa054. https://doi.org/10.1093/jcde/qwaa054 Charton, J., Baek, S., & Kim, Y. (2020). Mesh repairing using topology graphs. Journal of computational Design and engineering, 8, 251– 267. https://doi.org/10.1093/jcde/qwaa076. https://doi.org/10.1093/jcde/qwaa076 Cheng, S.-W., Dey, T. K., Shewchuk, J., & Sahni, S. (2013). Delaunay Mesh Generation. CRC Press Boca Raton. Cignoni, P., Rocchini, C., & Scopigno, R. (1998). Metro: measuring error on simplified surfaces. In Computer Graphics Forum, Vol. 17, pp. 167–174, Wiley Online Library. https://doi.org/10.1111/1467-8659. 00236 Cripps, R. J., & Parwana, S. (2011). A robust efficient tracing scheme for triangulating trimmed parametric surfaces. Computer-Aided Design, 43, 12–20. https://doi.org/10.1016/j.cad.2010.08.009 Cuillière, J.-C. (1998). An adaptive method for the automatic triangulation of 3d parametric surfaces. Computer-Aided Design, 30, 139– 149. https://doi.org/10.1016/S0010-4485(97)00085-7 De Goes, F., Desbrun, M., & Tong, Y. (2016). Vector field processing on triangle meshes. In ACM SIGGRAPH 2016 Courses, pp. 1–49. Endo, Y., Tada, M., & Mochimaru, M. (2014). Reconstructing individual hand models from motion capture data. Journal of computational Design and engineering, 1, 1–12. https://doi.org/10.7315/JCDE.2014. 001. Downloaded from https://academic.oup.com/jcde/article/13/1/239/8383411 by guest on 08 April 2026 Journal of computational Design and engineering, 2026, 13(1), 239–258 | 253

- Filip, D., Magedson, R., & Markot, R. (1986). Surface algorithms using

- bounds on derivatives. Computer Aided Geometric Design, 3, 295– 311. https://doi.org/10.1016/0167-8396(86)90005-1 Geuzaine, C., & Remacle, J.-F. (2009). Gmsh: A 3-d finite element mesh

- generator with built-in pre-and post-processing facilities. International Journal for Numerical Methods in engineering, 79, 1309–1331. https://doi.org/10.1002/nme.2579 Gong, X., & Feng, H.-Y. (2015). Cutter-workpiece engagement determi-

- nation for general milling using triangle mesh modeling. Journal of computational Design and engineering, 3, 151–160. https://doi.or g/10.1016/j.jcde.2015.12.001. GrabCAD (2025). Grabcad library. https://grabcad.com/library. Ac-

- cessed: 2025-10-09. Gu, H., Chase, T. R., Cheney, D. C., Bailey, T. T., & Johnson, D. (2001).

- Identifying, correcting, and avoiding errors in computer-aided design models which affect interoperability. Journal of Computing and Information Science in engineering, 1, 156–166. https://doi.org/10.1115/1.1384887 Guo, J., Ding, F., Jia, X., & Yan, D.-M. (2019). Automatic and high-quality

- surface mesh generation for cad models. Computer-Aided Design, 109, 49–59. https://doi.org/10.1016/j.cad.2018.12.005 Ju, T. (2009). Fixing geometric errors on polygonal models: a survey.

- Journal of Computer Science and Technology, 24, 19–29. https://doi.or g/10.1007/s11390-009-9206-7 Koch, S., Matveev, A., Jiang, Z., Williams, F., Artemov, A., Burnaev,

- E., Alexa, M., Zorin, D., & Panozzo, D. (2019). Abc: A big cad model dataset for geometric deep learning. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 9601–9611. Li, K., Jia, X., & Chen, F. (2025). Fast determination and computation of

- self-intersections for nurbs surfaces. ACM Transactions on Graphics, 44, 1–16. Lien, S.-L., Shantz, M., & Pratt, V. (1987). Adaptive forward differencing

- for rendering curves and surfaces. ACM Siggraph Computer Graphics, 21, 111–118. https://doi.org/10.1145/37402.37416 Lin, H., Qin, Y., Liao, H., & Xiong, Y. (2013). Affine arithmetic-based

- b-spline surface intersection with gpu acceleration. IEEE Transactions on Visualization and Computer Graphics, 20, 172–181. Lu, W., Liang, J., Ren, M., Wu, H., Zhang, J., & Liu, J. (2022). Robust and

- fast cad model tessellation for inspection. IEEE Transactions on Instrumentation and Measurement, 71, 1–14. https://doi.org/10.1109/ TIM.2022.3214285 Marussig, B., & Hughes, T. J. (2018). A review of trimming in isoge-

- ometric analysis: challenges, data exchange and simulation aspects. Archives of computational Methods in engineering, 25, 1059– 1127. https://doi.org/10.1007/s11831-017-9220-9 Open CASCADE Technology (2025). Open CASCADE Technology

- (OCCT). https://www.opencascade.com/. Accessed: 2025-05-08. Owen, S. J. (1998). A survey of unstructured mesh generation tech-

- nology. IMR, 239, 15. Park, J., & Kang, N. (2024). BMO-GNN: Bayesian mesh optimization

- for graph neural networks to enhance engineering performance prediction. Journal of computational Design and engineering, 11, 260– 271. https://doi.org/10.1093/jcde/qwae102. Park, Y., Son, S.-H., Kim, M.-S., & Elber, G. (2020). Surface–surface-

- intersection computation using a bounding volume hierarchy with osculating toroidal patches in the leaf nodes. Computer-Aided Design, 127, 102866. https://doi.org/10.1016/j.cad.2020.102866 Patrikalakis, N. M. (1993). Surface-to-surface intersections. IEEE Com-

- puter Graphics and Applications, 13, 89–95. https://doi.org/10.1109/ 38.180122 Pekerman, D., Elber, G., & Kim, M.-S. (2008). Self-intersection detec-

- tion and elimination in freeform curves and surfaces. ComputerAided Design, 40, 150–159. https://doi.org/10.1016/j.cad.2007.10. 004 Piegl, L., & Tiller, W. (2012). The NURBS Book. Springer Science & Business Media. Rossignac, J. R., & Requicha, A. A. (1987). Piecewise-circular curves for geometric modeling. IBM Journal of Research and Development, 31, 296–313. https://doi.org/10.1147/rd.313.0296 Ruppert, J. (1995). A delaunay refinement algorithm for quality 2-dimensional mesh generation. Journal of algorithms, 18, 548–585. https://doi.org/10.1006/jagm.1995.1021 Samareh, J. A. (2005). Geometry and grid/mesh generation issues for cfd and csm shape optimization. Optimization and engineering, 6, 21–32. https://doi.org/10.1023/B:OPTE.0000048535.08259.a8 Schöberl, J. (1997). Netgen an advancing front 2d/3d-mesh generator based on abstract rules. Computing and Visualization in Science, 1, 41–52. https://doi.org/10.1007/s007910050004 Schroeder, W. J., Avila, L. S., & Hoffman, W. (2000). Visualizing with vtk: a tutorial. IEEE Computer Graphics and Applications, 20, 20–27. https://doi.org/10.1109/38.865875 Sederberg, T. W. (1983). Implicit and Parametric curves and Surfaces for Computer Aided Geometric Design. Purdue University. Sheng, X., & Hirsch, B. E. (1992). Triangulation of trimmed surfaces in parametric space. Computer-Aided Design, 24, 437–444. https://do i.org/10.1016/0010-4485(92)90011-X Shostko, A. A., Löhner, R., & Sandberg, W. C. (1999). Surface triangulation over intersecting geometries. International Journal for Numerical Methods in engineering, 44, 1359–1376. https://doi.org/10.1002/ (SICI)1097-0207(19990330)44:91359::AID-NME552 ⟩ 3.0.CO;2-B Yerry, M. A., & Shephard, M. S. (1984). Automatic three-dimensional mesh generation by the modified-octree technique. International Journal for Numerical Methods in engineering, 20, 1965–1990. https: //doi.org/10.1002/nme.1620201103 Zhang, R., Hu, P., & Tang, K. (2015). Five-axis finishing tool path generation for a mesh blade based on linear morphing cone. Journal of computational Design and engineering, 2, 268–275 https://doi.org/ 10.1016/j.jcde.2015.06.013. Appendix A. Proof of Lemma 1 Proof. Conclusion 1: Initial non-intersection of L 1 and L 2 By the convex hull property of C 2-continuous NURBS curves (Piegl & Tiller, 2012), any line segment connecting two points on a NURBS curve segment is contained within the convex hull of that curve segment. For L 1: each segment C 1 (s i) C 1 (s i + 1) lies on the subsegment C 1, i = C 1 | [s i, s i + 1], so C 1 (s i) C 1 (s i + 1) ⊆ conv (C 1, i) = B 1, i. Similarly, for L 2: each segment C 2 (t j) C 2 (t j + 1) ⊆ conv (C 2, j) = B 2, j. From the definition of critical points, B 1, i ∩ B 2, j = ∅ for all i ∈-0, 1,..., n − 1 } and j ∈-0, 1,..., m − 1. Since every segment of L 1 is contained in some B 1, i, and every segment of L 2 is contained in some B 2, j, no segment of L 1 can intersect any segment of L 2. Thus, the unions L 1 and L 2 are disjoint, i.e., L 1 ∩ L 2 = ∅. Conclusion 2: Non-intersection of refined polylines L ′ 1 and L ′ 2 Let S ′ be an arbitrary refinement of S: by definition of refinement, S ′ ⊇ S, and for every original interval [s i, s i + 1] ⊆ [0, 1] (with s i, s i + 1 ∈ S), S ′ partitions [s i, s i + 1] into a finite sequence of consecutive subintervals: [s i, s i + 1] = p i − 1 k = 0 [s i, k, s i, k + 1], where p i ≥ 1 (number of inserted subintervals, p i = 1 means no insertion), s i, 0 = s i, s i, p i = s i + 1, and s i, 1,..., s i, p i − 1 ∈ S ′ \ S are intermediate insertion points. The refined polyline L ′ 1 corresponding to Downloaded from https://academic.oup.com/jcde/article/13/1/239/8383411 by guest on 08 April 2026
