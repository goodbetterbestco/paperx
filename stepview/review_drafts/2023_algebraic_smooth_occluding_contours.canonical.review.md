# Algebraic Smooth Occluding Contours

Aaron Hertzmann, Ryan Capouellez, Piecewise-Quadratic Surface

New York University USA
USA
New York University Jiacheng Dai New York University USA Denis Zorin New York University USA

## Abstract

Computing occluding contours is a key step in 3D non-photorealistic rendering, but producing smooth contours with consistent visi- bility has been a notoriously-challenging open problem. This pa- per describes the first general-purpose smooth surface construc- tion for which the occluding contours can be computed in closed form. Given an input mesh and camera viewpoint, we show how to approximate the mesh with a \(G^{1}\) piecewise-quadratic surface, for which the occluding contours are piecewise-rational curves in image-space. We show that this method produces smooth contours with consistent visibility much more efficiently than the state-of- the-art. · Computingmethodologies → Non-photorealistic rendering ; Visibility ; Parametric curve and surface models . © 2023 Copyright held by the owner author(s). Publication rights licensed to ACM. ACM ISBN 979-8-4007-0159-7 23 08...$15.00 KEYWORDS contours, non-photorealistic rendering, piecewise-quadratic surface, visibility Figure 1: Our method takes a triangle mesh, and renders smooth occluding contours for a given camera viewpoint. For each view,

## 1 INTRODUCTION

Computing occluding contour lines of 3D objects is a common step in 3D non-photorealistic rendering algorithms, whether for architectural drawings, cartoon stylization, or pen-and-ink illustration. Conceptually, the problem is deceptively simple: find the points of the surface where the dot product \(\mathbf{n} \cdot \tau\) of the view direction \(\tau\) and the normal vector \(\mathbf{n}\) changes sign, and determine which of these points are visible [Bénard and Hertzmann 2019].

For triangle meshes, the exact occluding contours can easily be defined: they are a subset of the edges of the original mesh. However, when the mesh represents a smooth object, these contours usually have many spurious singularities, and do not produce the clean contour topology of a smooth surface (Figure 2). This makes them unsuitable for curve stylization, and noisy during animation, e.g., [Bénard et al. 2014]. This mismatch between mesh contours and smooth surface contours can be attributed to the fact that the normal \(\mathbf{n}\) is discontinuous on the mesh, and sign-change sets of discontinuous functions fundamentally differ in structure from the zero sets of smooth functions.

Unfortunately, robustly computing the occluding contours for smooth surfaces is difficult. For common representations, the occluding contours are projective-transformed piecewise higher-order algebraic implicit curves. Existing methods approximate these curves with polylines, but visibility for these polylines is unreliable, as they are not the contours of the smooth surface [Bénard et al. 2014; Eisemann et al. 2008]. Recent methods construct a new triangle mesh with the extracted polylines as contours [Bénard et al. 2014; Liu et al. 2023], but require very costly heuristic search. These difficulties raise the question: is there a practical smooth representation for which visible occluding contours can be computed exactly?

In this paper, we describe a method for computing occluding contours in closed form. For a given input mesh and camera viewpoint, we show how to approximate the mesh with a \(C^{1}\) (excluding a small set of points) surface so that the occluding contours are piecewise-rational curves in image space. This algebraic representation allows for reliable visibility by solving low-order polynomial equations, and for direct, efficient computations without heuristics or search.

Our approach operates as follows. We first apply a projective transformation to the input mesh, reducing the problem to orthographic occluding contours. We use a Powell-Sabin construction to produce a \(C^{1}\) quadratic patch surface, which, we observe, is the only algebraic representation with rational contours. To support perspective views, our surface construction is view-dependent but can be evaluated very efficiently with a precomputed matrix factorization. All possible piecewise rational quadratic contour lines in the parametric domain are easily enumerated, and correspond to piecewise rational quartic curves in the image domain. visibility for the contours is also resolved precisely by a straightforward computation (up to numerical errors in solving low-order polynomial equations).

In proposing the first algebraic smooth occluding contour procedure, our main contribution is a careful integration and adaptation of a number of recent and classical techniques in a highlyconstrained setting. This includes recent methods for robust surface parameteriztion, a view-dependent almost-everywhere \(C^{1}\) surface approximation, supporting efficient per-view updates with precomputation, quantitative invisibility for piecewise quadratic surfaces, and efficient cusp computation.

In comparison to state-of-the-art methods for accurate contours [Bénard et al. 2014; Liu et al. 2023], our method does not involve expensive search and unpredictable refinement heuristics; we find order-of-magnitude faster performance on larger meshes, while avoiding the visibility errors that older methods are prone to.

## 2 RELATED WORK

It has long been known that the occluding contours for a smooth surface cannot be computed analytically, except for simple primitives like spheres and quadrics [Cipolla and Giblin 2000]. Hence, all previous methods employ numerical approximations of the smooth contour; see [Bénard and Hertzmann 2019] for a survey. Past methods either often produce artifacts, or else require expensive computations to achieve topologically-accurate curves.

Raster methods, based on edge detection of an image buffer are the simplest way to approximate the contour, e.g., [Decaudin 1996; Saito and Takahashi 1990]; however, these methods do not produce a vector representation of the contours.

Representing a smooth surface as a triangle mesh yields accurate image-space contours but with erroneous topology (Figure 2). Heuristics may be used to smooth the topology for stylization [Eisemann et al. 2008; Isenberg et al. 2002; Kirsanov et al. 2003; Northrup and Markosian 2000], but these too may be very inaccurate and often produce artifacts.

A third approach is to directly compute a polyline contour approximation, e.g., by root-finding on the smooth surface representation [Elber and Cohen 1990; Stroila et al. 2008; Weiss 1966; Winkenbach and Salesin 1996]. However, visibility of these sampled contours are inconsistent with the smooth surface [Bénard et al. 2014]. Defining a piecewise-smooth contour function on a triangle mesh [Hertzmann and Zorin 2000] has the same problem. Bénard et al. [2014] generate a new triangle mesh from sampled contours that produces consistent visibility. However, this method has a high computational cost and is not guaranteed to find a valid mesh. planar-maps can produce consistent visibility [Stroila et al. 2008; Winkenbach and Salesin 1996], but may also include incorrect topology from polyline contour approximations.

Liu et al. [2023] recently explained why this problem has been so difficult: sampling smooth contours produces 2D polylines that cannot be the contours of any valid surface. Liu et al. do guarantee valid polylines, but their method uses expensive numerical sampling operations, involving costly iterative refinements and heuristics to find a consistent mesh.

In contrast to these works, we present a method using a \(C^{1}\) approximation of an arbitrary input mesh for which we can compute exact (up to numerical precision) contours algebraically, with precise visibility, without any of the heuristics or expensive refinement procedures of previous methods.

Linear-normal (LN) surfaces [Jüttler 1998; Jüttler and Sampoli 2000] produce \(G^{1}\) surfaces with normals depending linearly on the parametric coordinates, which, in turn, yields piecewise-linear contour lines in the parametric domain, but they are limited in the type of surfaces that these can represent, e.g., they have singularities at parabolic points.

## 3 OVERVIEW

Given an input mesh \(M\) and camera position \(\mathbf{c}\), we seek a tangent plane-continuous surface representation that approximates the mesh and yields high-quality contours that are continuous and have explicit algebraic form, allowing exact and efficient computation. Our key observation is that the problem of finding this representation is extremely constrained-yet it does have a solution. We start with defining the problem more precisely.

We use \(\mathbf{p}(u, v): \Omega \subset \mathbb{R}^{2} \rightarrow \mathbb{R}^{3}\) to denote a surface patch parameterized over a domain \(\Omega\) in the plane. The parameterization is assumed to be at least \(C^{1}\). The normal \(\mathbf{n}(u, v)=\mathbf{p}_{u} \times \mathbf{p}_{v}\) is not necessarily unit length. The camera position is \(\mathbf{c}\), and the image plane is \(P\), with unit normal \(\tau\).

The occluding contour of the image of the surface patch \(\mathbf{p}\) in \(P\) is the projection to the image plane of the set of points \(\mathbf{p}(C)\), with the curve \(C\) in the parametric domain defined by

The curve \(\mathbf{p}(C)\) is the occluding contour generator, and the apparent contour is the visible projection of that curve. For brevity, we refer to each of these 2D and 3D curves as "contours." These elements are illustrated in Figure 3. Existing methods for solving these equations employ numerical approximations, as no closed-form solution is known for these equations for general-purpose smooth surfaces.

Algebraic Contour Existence. Under what conditions does Equation 1 yield curves in closed-form? For algebraic functions, the following is known, e.g., [Ferrer et al. 2008]:

Proposition 1. An irreducible algebraic curve 𝑐 ( 𝑢, 𝑣 ) = 0 admits a rational parameterization for an arbitrary choice of coefficients if and only if it is linear or quadratic.

The linear case corresponds to using a triangle mesh, which has been heavily used in previous methods, with the problems discussed in Section 2. Juttler et al. [Jüttler 1998; Jüttler and Sampoli 2000] describe a higher-order algebraic surface with constraints that make \(C\) reducible into a linear factor and another factor independent of the view direction, but the construction is degenerate at parabolic points. Instead, we consider surfaces where \(\mathbf{p}(u, v)\) is quadratic, which has not been explored in depth. When \(\mathbf{p}(u, v)\) is quadratic, \(\mathbf{n}(u, v)\) is also quadratic. Then, for orthographic projection, Equation 1 is quadratic, and thus the solution curves are rational functions. It is also clear from Equation 1 that contour continuity requires that the surface is at least \(G^{1}\).

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2023_algebraic_smooth_occluding_contours/figures/figure-3-p003.png)

*Figure 3: Left: The occluding contours of a smooth patch are the points p ( 𝑢, 𝑣 ) where the normal and view direction are orthogonal (n ( 𝑢, 𝑣 ) · 𝜏 = 0). In this paper, we show that the contour for a quadratic patch can be described by an algebraic curve r ( 𝑡 ) in the parameter domain, so the 3D contour is p (r ( 𝑡 )). Right: 3D perspective transformation converting perspective projection frustum to a cube. (Public domain Spot model by Keenan Crane.)*

Hence, if we can approximate an input mesh with a \(G^{1}\), piecewisequadratic surface, then its contours are piecewise rational functions for orthographic projections.

Next, we summarize the key features of our method, determined by this observation.

Handling Perspective. Many applications require perspective projection, which we handle by applying a projective transformation to the input mesh. That is, an input vertex with camera coordinates [ \(x, y, z\) ] becomes [ \(x / z, y / z,-1 / z\) ], with orthographic view vector \(\tau=[0,0,1]\), yielding a view equivalent to perspective projection of the original input. A key insight is that, for algebraic contours, we must apply the transformation to the mesh before constructing a smooth representation, which makes the surface approximation view-dependent, but does not lead to visible artifacts.

Quadratic Surface Construction. After the projective transformation, we seek to approximate the mesh with a surface composed of quadratic patches. In order for the contours to be continuous across patch boundaries, the surface must be \(G^{1}\) everywhere, except a small number of isolated points. The existing surface choices are quite constrained. A classical solution to this problem for surfaces parameterized over arbitrary triangulations of the plane is the Powell-Sabin interpolant, which was in part motivated by a need for continuous isolines for height fields. Applying these to arbitrary meshes requires several additional components: mesh parametrization, a method for dealing with singular vertices of the parametrization, a way to generate high-quality surfaces without extraneous oscillations, and fast update to handle view-dependence. Our solution is based on the overall idea of He et al [2005], but with several important differences. In particular, their method does not produce quadratic patches for one-ring of triangles near singular vertices of the parametrization (cones) and it is interpolating, rather than approximating, the input mesh.

visibility. To compute visibility of occluding contours, we adapt the Quantitative Invisibility (QI) algorithm [Appel 1967; Bénard and Hertzmann 2019]. QI is normally applied to mesh contours; we show how to apply it to rational occluding contours, which requires computing curve intersections and solving equations for cusps efficiently.

### 3.1 Method summary

For a given mesh \(M\), our method begins with preprocessing steps. first, we scale \(M\) to fit within a unit box. We then compute a global \((u, v)\) parameterization for \(M\). We split each triangle into 12 triangles, each of which will be a quadratic patch in the final surface. Finally, we precompute a factorized matrix that will allow us to efficiently produce patch coefficients for each new viewpoint, minimizing thin-plate surface energy.

```text
At run-time, given a new camera view \(\mathbf{c}\), we perform the follow- ing steps: (1) we apply a projective transformation to the mesh \(M\), producing transformed mesh vertices;
(2) we use the precomputed matrices to produce Bézier coefficients defining our piecewise qua- dratic Powell-Sabin surface from the updated vertex position;
(3) we then find all contours contained within all patches;
(4) we compute their intersections and cusp points, split them at these points and (5) compute visibility using QI. The output rational image space curves may be then rendered in 2D.
```

Our algorithm allows to perform these steps at a relatively low cost: specifically, (2) requires a single backsubstitution solve for a factorized matrix (3) requires solving a quadratic equation and small linear transformations for patches that may contain contours (4) requires solving a system of two quadratic equations for cusps for each contour segment, and intersecting fourth-degree rational curves for a small number of curve pairs, and (5) tracing a small number of rays intersecting them with quadratic patches (also a system of two quadratic equations).

## 4 EXTRACTING VISIBLE CONTOURS

Given a \(C^{1}\) (excluding isolated points) piecewise quadratic surface viewed under orthographic projection, we now show exact procedures for extracting the occluding contour generator and determining which portions are visible. We do assume a general-position view direction, assuming it is perturbed to avoid exact alignment with tangents to flat parts of the surface, and that the surface does not self-intersect. We do not assume that the surface itself is in a fully general position: we do require that the surface normal does not vanish, except at cones.

### 4.1 The contours of a single quadratic patch

We first enumerate parametric expressions for the contours of a quadratic surface, ignoring the triangular domain bounds.

$$
For a quadratic surface parameterized by coordinates \(\mathbf{r}=[u, v]\),
$$

$$
\tau \cdot \mathbf{n}(\mathbf{r})=\frac{1}{2} \mathbf{r}^{T} A \mathbf{r}+\mathbf{b}^{T} \mathbf{r}+c=0
$$

i.e., the contours are conic sections in the parametric domain (Figure 3). For completeness, we now enumerate all stable cases, i.e., the ones that are not always eliminated by a perturbation of the view direction.

We diagonalize the contour equation using \(A=U^{T} \operatorname{diag}\left(\sigma_{1}, \sigma_{2}\right) U\). If \(A\) is not singular, then we can reparameterize in terms of unknown

$$
\sigma_{1} z_{1}^{2}+\sigma_{2} z_{2}^{2}+\hat{c}=0
$$

where \(\hat{c}=c-\mathbf{b}^{T} A^{-1} \mathbf{b} / 2\). We ensure \(\hat{c} \geq 0\) by negating \(\sigma_{1}, \sigma_{2}, \hat{c}\) if necessary. We then seek a solution curve of the form \(\mathbf{z}(t)\). When \(\hat{c}>0\), the solution curve \(\mathbf{z}(t)\) may be an ellipse or hyperbola with scales \(k_{1}=\sqrt{\hat{c} /\left|\sigma_{1}\right|}, k_{2}=\sqrt{\hat{c} /\left|\sigma_{2}\right|}\). In cone patches (Section 5), \(\hat{c}=0\) occurs stably, in which case the solution \(\mathbf{z}(t)\) is a pair of intersecting lines. The first three columns of Table 1 provide the solution curves \(\mathbf{z}(t)\) for these cases. Then, the solution curves are converted to parameter domain by \(\mathbf{r}(t)=U^{T} \mathbf{z}(t)+A^{-1} \mathbf{b}\).

If \(A\) is singular ( \(\sigma_{2}=0\) ), we reparameterize with \(\mathbf{z}=U \mathbf{r}\), and the contour equation becomes

$$
\sigma_{1} z_{1}^{2}+\hat{\mathbf{b}}^{T} \mathbf{z}+c=0
$$

where \(\hat{\mathbf{b}}=U \mathbf{b}\). We negate terms if \(\sigma_{1}<0\). Then, the solution curve \(\mathbf{z}(t)\) may be either a parabola or two parallel lines in parameter space, depending on whether \(\hat{b}_{2}=0\). Solution curves \(\mathbf{z}(t)\) are provided in the fourth and fifth columns of Table 1. The parameterdomain curve is then \(\mathbf{r}(t)=U^{T} \mathbf{z}(t)\). We note that \(A\) being nearsingular can be stable with respect to the viewpoint change for a cylindrical surface; the contours along a cylinder are always straight lines; see supplemental material for details).

All tests of a quantity \(x\) equal to zero are implemented by checking \(|x|<\epsilon\), where we use \(\epsilon=10^{-10}\).

Trimming. In general, only a subset of the occluding contour for a quadratic may lie within a patch. We compute the bounds \(t \in\left[t_{0}, t_{1}\right]\) as follows. The above procedure yields a small number of parametric curves of the form \(\mathbf{r}(t)\) that we intersect with each of the lines bounding the domain triangle \((u=0, v=0, u+v=1)\). If there are intersections, then the curve is broken into any subintervals \(\left[t_{\min }, t_{\max }\right]\) contained within the triangle, up to three per curve.

Image-space curve. The above steps identify the occluding contour generators within a patch. Each of these are rational curves in 3D, given by \(\mathbf{p}(\mathbf{r}(t))\), within bounds \(t \in\left[t_{0}, t_{1}\right]\). Under orthographic projection with the appropriate rotation, projection to image-space curves amounts to removing the third coordinate from a curve, yielding the final result of the computation, a quartic rational curve.

### 4.2 Visibility of contours on a p.w. quadratic 𝐶 1 surface.

To compute curve visibility, we adapt the Quantitative Invisibility (QI) algorithm [Appel 1967]. The QI of a surface point is the number of occluders of that point; a point is visible if and only if it has a QI of zero. visibility along a curve can only change at cusps, imagespace intersections, and contour-boundary intersections. Hence, if we split a curve into segments at each of these cases, then QI for an entire segment can be computed by a single ray-test for the curve. Moreover, the number of ray-tests is minimized by propagating QI through these cases, e.g., using the fact that the QI increases by

$$
\mathbf{z}(t)=\left[\frac{-\hat{\mathbf{b}}_{1} \pm \sqrt{\hat{\mathbf{b}}_{1}^{2}-4 \sigma_{1}^{2} c}}{2 \sigma_{1}^{2}}, t\right]
$$

$$
\mathbf{z}(t)=\left[\frac{k_{1}\left(1-t^{2}\right)}{1+t^{2}}, \frac{2 k_{2} t}{1+t^{2}}\right]
$$

$$
\mathbf{z}(t)=\left[\frac{k_{1}\left(1+t^{2}\right)}{t^{2}-1}, \frac{2 k_{2} t}{t^{2}-1}\right]
$$

$$
\mathbf{z}(t)=\left[t, \pm t \sqrt{-\frac{\sigma_{1}}{\sigma_{2}}}\right]
$$

$$
\mathbf{z}(t)=\left[t, \frac{-\sigma_{1} t^{2}-\hat{b}_{1} t-c}{\hat{b}_{2}}\right]
$$

one from the near side to the far side of a cusp. See [Bénard and Hertzmann 2019] for a full description of the QI algorithm.

Previous work applied QI to triangle mesh contours. In order to compute QI for piecewise-quadratic surfaces, we need new algorithms for computing ray tests, detecting cusps, detecting imagespace intersections, and propagating QI.

View graph construction. We first connect contour generator curves across patch boundaries. Since the surface is \(C^{1}\) by design, the occluding contours will be continuous at patch boundaries, and form disjoint loops, with the exception of cone points, where multiple loops can share a point. We disallow visibility propagation through cone points.

After we compute cusps and image-space contour intersections as explained below, we split the countour curves at these points, constructing a graph of non-intersecting rational quadratic segments with nodes labeled as cusp, intersection, contour-boundary intersection or interior. . vectors 11 and the cusp as the Detecting interior cusps. To determine cusp positions in the interior of a quadratic patch, we need to find points where \(\tau\) is parallel to the tangent to the contour curve. One can use this definition directly, solving the univariate equation \(\tau \cdot \frac{d}{d_{t}} \mathbf{p}(\mathbf{r}(t))=0\); however, this equation is a degree 10 polynomial. Instead we opt for a different approach. We introduce two orthogonal vectors \(\tau_{1}\) and \(\tau_{2}\) perpendicular to the view direction, and define the cusp as the point on the contour for which the tangent is orthogonal to both of these vectors. An important observation is that the unnormalized tangent to all isolines of \(\mathbf{n} \cdot \tau\) in the parametric domain is given by \(\left[-\mathbf{n}_{v} \cdot \tau, \mathbf{n}_{u} \cdot \tau\right]\), which is a linear function on the whole patch. Mapped to 3D this yields a quadratic equation:

i.e., the components of the tangent are also quadratic, and the condition for a cusp is a system of two quadratic equations in ( 𝑢, 𝑣 ) :

$$
\mathbf{t}(u, v) \cdot \tau_{1}=0, \text { and } \mathbf{t}(u, v) \cdot \tau_{2}=0,
$$

Note that the contour equation itself is redundant, because if the view direction is aligned with a surface tangent, it is perpendicular to the normal. We solve this equation using the pencil method which reduces it to a cubic equation in one variable, and a pair of quadratic equations, which we also use for ray-patch intersections [Ogaki and Tokuyoshi 2011]; the cubic equation is solved by finding the companion matrix eigenvalues with QR decomposition.

QI increases by 1 along the contour in the direction of \(\mathbf{t}\).

Patch-boundary cusps. At a patch boundary, a contour may have two distinct tangents \(\mathbf{t}\) and \(\mathbf{t}^{\prime}\) corresponding to the common endpoint of the contour segments in two patches; a cusp occurs if \(\tau \cdot(\mathbf{n} \times \mathbf{t})\) and \(\tau \cdot\left(\mathbf{n} \times \mathbf{t}^{\prime}\right)\) have different signs. While in this case there is no need to split either of the curves at the cusp, the visibility may change at the common endpoint, which we refer to as a boundary cusp. We opt not to propagate visibility through such cusps.

Image-space contour intersections. The intersections of contours in the image domain are computed using the standard Bézier clipping algorithm [Sederberg and Nishita 1990], which typically converges in a few iterations. The QI on the top contour is a constant \(q\), the segment of the lower contour not occluded by the near surface also has QI \(q\), and the lower contour segment occluded by the Ray tests and QI propagation. Once the contours have been split at cusps and intersections, the visibility can be determined by performing a ray test at a contour segment and then propagating QI. We do not propagate QI through cone points, since multiple contours may meet there, and we do not propagate QI though patchboundary cusps. If any segments do not have QI values assigned after propagation, the process repeats with a new ray test. We use a highly efficient ray-quadratic patch intersection test [Ogaki and Tokuyoshi 2011]; however, a substantial speed up is obtained using the standard bounding-box tests and spatial grid for acceleration.

$$
\mathbf{t}(u, v)=-\mathbf{p}_{u}\left(\mathbf{n}_{v} \cdot \tau\right)+\mathbf{p}_{v}\left(\mathbf{n}_{u} \cdot \tau\right)
$$

## 5 SURFACE CONSTRUCTION

```text
We now describe our smooth surface construction;
producing a high-quality surface is essential to generating well-behaved con- tours. The input is an arbitrary manifold mesh \(M=(V, E, F)\) pos- sibly with boundary, along with vertex positions. The output is a surface composed of quadratic patches joined with \(G^{1}\) continuity,
```

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2023_algebraic_smooth_occluding_contours/figures/figure-5-p006.png)

*Figure 5: Surface definition. (a) An input mesh with vertex positions p 𝑖 . (b) 3D mesh is mapped to the plane with cuts with texture coordinates r = ( 𝑢, 𝑣 ), consistent edge length and sum of angles at most vertices equal to 2 𝜋 (c) Vertex 𝑎 (red vertex) occurs at three places on the cut, but a chart can be constructed where the sum of the angles around 𝑎 is 2 𝜋 . For a cone vertex 𝑏 (green vertex), the sum is less than 2 𝜋 . (d) The chart for each vertex with respect to which gradient DOF are defined.*

everywhere except at a small number of isolated vertices. Our approach is based on He et al. [2005], with several important changes.

### 5.1 Conformal parameterization

We first compute a locally bijective global surface parameterization, to produce \(u_{v}\) coordinates for the mesh, as required for the Powell-Sabin interpolant. More specifically, the parameterization is a flattening into the \(u_{v}\) plane of the input mesh \(M\) (Figure 5). The mesh is cut to a disk \(M^{c}\) along mesh edges, such that, for two images of a cut edge in the \(u_{v}\) domain, their lengths match. The

$$
q=\left[\mathbf{p}_{1}, \mathrm{~g}_{1}^{u}, \mathrm{~g}_{1}^{v} \ldots \mathrm{p}_{n}, \mathrm{~g}_{n}^{u}, \mathrm{~g}_{n}^{v}, \mathrm{~g}_{1}^{m} \ldots \mathrm{~g}_{m}^{m}\right]
$$

```text
The first step is to select a small number of cone vertices, consis- tent with genus;
we use \(4(g-1)\) cones for \(g>1\) and 8 for genus zero. We uniformly distribute them over the surface, by partitioning it into clusters of close size, and, for each cluster, picking the vertex of smallest discrete curvature, as this minimizes visual artifacts of the surface. We do not fix angles at the cones;
instead, we fix the conformal scale factors at cones to 1 , as in [Springborn et al. 2008], to minimize parametrization distortion at these points. Additionally, we perform one step of Loop subdivision on the incident triangles, to further reduce artifacts.
```

$$
p^{\ell}=B_{\ell} q^{\text {loc }}, \ell=1 \ldots 12
$$

Then, we apply an efficient implementation of discrete conformal maps [Campen et al. 2021; Gillespie et al. 2021] mathematically guaranteed [Gu et al. 2018] to satisfy these requirements, possibly with a moderate amount of mesh refinement. These methods compute an edge length assignment, which we convert to a 𝑢𝑣 parametrization using a greedy layout algorithm, as in [Springborn et al. 2008].

While conformal parameterization can have extreme scale variation, uniformly scaling the parametric domain of a polynomial patch does not affect its shape, and so this scaling does not significantly impact our output surface construction. This stage of our algorithm differs from the parameterization step of He et al. [2005], which does not guarantee injectivity, fixes cone angles to multiples of 𝜋 , and does not provide control over their position, leading to higher distortion.

### 5.2 Powell-Sabin construction

The Powell-Sabin interpolant transforms a set of input degrees-offreedom (DOFs) \(q\) associated with a mesh \(M\) into a set of quadratic patches \(\mathbf{p}(u, v)\). Each patch is defined by six Bézier points on a triangle in the \(u_{v}\) plane. Each of these triangles is obtained by splitting the parametric images of the triangles in the original mesh (Figure 6(right)). We use the more-expensive 12-split Powell-Sabin construction as it yields higher surface quality, but a 6-split can also be used with acceptable results. All quadratic patches associated with an input triangle form a \(C^{1}\) piecewise-quadratic macropatch \(\mathbf{P}(u, v)\). The input coefficients include, for every vertex, the position \(\mathbf{p}\) The input coefficients include, for every vertex, the position \(\mathbf{p}\) and two tangents \(\mathbf{g}^{u}, \mathbf{g}^{v}\), and for every edge midpoint, a single tangent \(\mathbf{g}^{m}\) (Figure 6(left)). If the parametrization has no cuts, then \(\mathbf{g}^{u}\), \(\mathbf{g}^{v}\) are prescribed values of \(\partial_{u} \mathbf{P}\left(u_{i}, v_{i}\right)\) and \(\partial_{v} \mathbf{P}\left(u_{i}, v_{i}\right)\) at a vertex \(i\) respectively, and \(\mathbf{g}^{m}\) is \(\partial_{\mathbf{e}_{i_{j}}^{\perp}} \mathbf{P}(u, v)\), where \(\mathbf{e}_{i_{j}}^{\perp}\) is the vector perpendicular to the edge \(\mathbf{e}_{i_{j}}\). All macropatches \(\mathbf{P}\) sharing a vertex share these coefficients at the vertex, and similarly, when two patches sharing a midpoint, they share a coordinate derivative in the direction \(\mathbf{e}_{i_{j}}^{\perp}\). Powell and Sabin [1977] show that sharing these degrees of freedom is sufficient for their construction to yield a \(C^{1}\) surface.

Wewrite the complete set of free DOFs for the surface as a vector of coefficients:

where \(n\) is the number of vertices, \(m\) the number of edges, and \(\mathbf{g}_{\ell}^{m}=\mathbf{g}_{i_{j}}^{m}\) if the edge ( \(i_{j}\) ) has index \(\ell\); the 3 components of each vector are flattened.

```text
Local parameters. To construct a single macropatch for a triangle ( \(i j k\) ) we extract the relevant 12 DOFs from this vector to obtain a local DOF vector, \(q^{\text {loc }}=\left[\mathbf{p}_{i}, \mathbf{g}_{i}^{u}, \ldots \mathbf{g}_{k}^{m}\right]\), with 12 vector DOFs;
the coefficients of the 12 quadratic subpatches are obtained by the stan- dard Powell-Sabin linear transformation of this vector, described in supplementary: this yields six Bezier points for each quadratic patch as shown in Figure 6.
```

where each \(B_{\ell}\) is a \(6 \times 12\) matrix applied coordinatewise, mapping twelve local degrees of freedom to six quadratic patch coefficients.

Cut vertices. To determine local DOFs \(q^{\text {loc }}\) from global \(q\) at a vertex \(i\) or edge ( \(i_{j}\) ) on the cut, we need to define the local gradients \(\mathbf{g}\) consistently across the cut. We do so by constructing a chart comprising all incident triangles of the vertex or edge. One of the edges of the chart is arbitrarily chosen to be the \(u^{\prime}\) coordinate direction, defining a local coordinate system ( \(u^{\prime}, v^{\prime}\) ). All triangles are mapped to the chart by a rigid transformation \(T_{i j_{k}}\) from global \(\mathbf{r}=(u, v)\) Then we can obtain the gradient DOFs \(\mathbf{g}\) in coordinates \(\left(u^{\prime}, v^{\prime}\right)\) on the chart. To obtain the vertex DOFs for each triangle ( \(i j_{k}\) ), we

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2023_algebraic_smooth_occluding_contours/figures/figure-6-p007.png)

*Figure 6: Left: The smooth surface is parameterized by the following coefficients: for each vertex, a position p and gradients g 𝑢 and g 𝑣 , and, for each edge, a midpoint gradient g 𝑚 . Right: Each input triangle is split into 12 triangles, with Bézier controls named as shown here. These control points are computed from the smooth surface coefficients 𝑞 loc = [p 𝑖 , g 𝑢*

$$
\begin{aligned} E(q) & =\frac{1}{2}\left(q^{T} H^{s} q+w\left(q-q_{0}\right)^{T} H^{f}\left(q-q_{0}\right)\right) \\ & =\frac{1}{2} q^{T} H q-w q^{T} H^{f} q_{0}+\mathrm{const} \end{aligned}
$$

apply 𝑇 𝑖 𝑗𝑘 and apply the corresponding transform to ∇ r ′ \(P(r′)\) = [ 𝜕 𝑢 ′ P, 𝜕 𝑣 ′ P] , to obtain the local DOF vector ∇ r P = 𝑇 𝑖 𝑗𝑘 ∇ r ′ P for the macropatch. This construction retains 𝐶 1 continuity across cut edges and at non-cone vertices [He et al. 2005].

Cone vertices. At cone vertices, we create degenerate patches, e.g., [Neamtu and Pfluger 1994]. In order to achieve consistent gradients across the cut, we set gradients \(\mathbf{g}_{u}, \mathbf{g}_{v}\) to zero at cone vertices, making the patch map \(\mathbf{p}(u, v)\) singular at these points. The conditions for \(C^{1}\) continuity are still satisfied, although the surface has a cone point at the vertex (Supplemental Material). While one could apply spline surface construction methods that force a common tangent plane at a singular vertex, we found our approach to have negligible impact on contour quality. Typical surface behavior near a cone is shown in Figure 7.

### 5.3 Thin-plate optimization

We now describe how to optimize the global parameters \(q\) to produce a smooth surface shape that approximates the input mesh vertices. One nice property of a Powell-Sabin spline surface is that it is \(C^{1}\), and, at the same time, minimal degree. \(C^{1}\) is a requirement for conforming finite-element discretization of optimization objectives containing second derivatives, in particular, the thin-plate functional:

where \(\mathbf{p}_{i}^{0}\) are the input mesh vertices and \(\Omega_{\ell}\) is the \(\ell\)-th triangle domain. We discretize the functional by simply substituting the expressions for quadratic patches in terms of the degrees of freedom \(q^{\text {loc }}\), yielding constant expressions for the integrands for each quadratic patch. These expressions are quadratic in the degrees of freedom, so the energy can be written as a quadratic form for each patch with a constant local matrix, which are then assembled into a global system. We pre-compute matrices \(H^{s}\) and \(H^{f}\), combined into a matrix \(H=H^{s}+w H^{f}\), corresponding to the fitting and smoothing terms of the quadratic objective (8) respectively. Then the energy can be written in the form

The constant term \(q_{0}\) is the vector of degrees of freedom with the original mesh vertex positions for \(\mathbf{p}_{i}\) and zeros for all other components. This objective is minimized by solving \(H_{q}=w H^{f} q_{0}\) for \(q\), i.e. a single sparse linear solve.

One can also show by direct computation that our optimization objective minimum, expressed as Bézier control points of patches, is independent of the choice of the chart coordinates \(\left(u^{\prime}, v^{\prime}\right)\).

However, the matrix \(H\) depends on parametric coordinates and not on the vertex positions. Hence, all of the computations in this section, including mesh parameterization and defining local and global coordinates, can be computed in a preprocess. We precompute the Cholesky decomposition of the sparse matrix \(H\), which makes the cost of solving the system \(H_{q}=w H^{f} q_{0}\) negligible at run-time.

## 6 EVALUATION

We show results of our method in Figures 1 and 8. Our method produces clean, smooth rational output curves without gaps or other topological errors.

Timings and scaling. We tested our algorithm on the same small test set that was used in [Liu et al. 2023]. We preprocessed the meshes by performing boolean unions of parts to eliminate all intersections, and cleaning up the resulting mesh to eliminate very short edges. Figure 11 shows the timings for the view-dependent and view-independent parts of our algorithm. We use 29 models and 26 randomized views per model. We see relatively very little per-frame timing variation (standard deviation less than 150 ms for the largest models), and both precomputation and per-view performance scales approximately linearly with the input size. Our implementation is serial and not heavily optimized, and we expect that performance can be significantly improved.

Comparison with previous work. Precise comparison with ConTesse [Liu et al. 2023], the state-of-the-art method for accurate contours, is difficult for various reasons, e.g., that paper reports timing only for mesh generation. Nonetheless, it is clear that our approach operates an order of magnitude faster during run-time, and scales much better as well. Our entire per-view processing

$$
E(q)=\sum_{\ell} \int_{\Omega_{\ell}} \mathbf{p}_{u u}^{2}+\mathbf{p}_{v v}^{2}+2 \mathbf{p}_{u v}^{2} d u d v+w \sum_{i} A_{i}\left(\mathbf{p}_{i}-\mathbf{p}_{i}^{0}\right)^{2}
$$

time, for smaller meshes, is comparable to ConTesse's mesh generation step alone. However, for larger meshes, our method becomes orders-of-magnitude faster, e.g., for 'Fertility,' ConTesse averages 16 seconds per view for mesh generation, whereas we require 0.4 seconds per view for the entire visibility pipeline, after a 4.4 seconds of preprocessing time. For "Killeroo," ConTesse requires 33 seconds per view for mesh generation, whereas we require 0.5 seconds per view, after 3 seconds preprocessing. We evaluated timing on an MacBook Pro 2.7 GHz, an older machine than the ConTesse results are reported on.

This is to be expected, since our method requires only a linear solve to compute patch coefficients for each new view, whereas ConTesse employs many iterative heuristic search steps to find a valid mesh for each new view.

View-dependent effects. Because we construct a view-dependent surface approximation, in principle, the object could appear nonrigid during rotation. Figure 10 and the accompanying video show that the projective transformation does not alter the geometric appearance or produce non-rigid effects.

Smoothness vs. approximation. All examples in this paper were generated using a constant weight 𝑤 = 1 for the fitting term in (10); Figure 9 shows how the surface changes as this weight varies.

## 7 CONCLUSIONS

We have presented a method for efficient computation of highquality occluding contours on \(C^{1}\) surfaces approximating arbitrary input meshes. As contours are computed in closed algebraic form and are the exact (modulo numerical errors) contours of the surface, visibility computation is a straightforward extension of the QI algorithm for meshes, and, at the same time, are close to the contours on the smooth surface that the mesh is approximating. The resulting contour lines cannot violate topological conditions from [Liu et al. 2023], except due to numerical error for non-generalposition choices of the view direction. Hence, the output contours have valid, well-defined visibility, without the artifacts that have plagued previous methods.

There are many extensions that are easy to add to our framework: it is straightforward to add sharp features, and handle non-manifold surfaces, e.g., resulting from intersections or self-intersections. Other curves, like suggestive contours, apparent ridges [DeCarlo 2012], and can be added as polylines, as well as stylized shading effects. The per-view computational cost of our approach is proportional to the number of contour segments and is embarrassingly parallel: an optimized implementation is likely to improve performance by a large factor. Another potentially important direction is to explore higher-order constructions with constraints with reducible parametric contour equations, as these may eliminate the need for a global parametrization.

## References

- Arthur Appel. 1967. The Notion of Quantitative Invisibility and the Machine Rendering of Solids. In Proceedings of the 196722nd National Conference (ACM '67). ACM, 387393. https: doi.org 10.1145800196.806007

- Pierre Bénard and Aaron Hertzmann. 2019. Line Drawings from 3D Models. Foundations and Trends in Computer Graphics and Vision 11, 1-2 (2019), 1-159. https: doi.org 10.15610600000075

- Pierre Bénard, Aaron Hertzmann, and Michael Kass. 2014. Computing Smooth Surface Contours with Accurate Topology. ACM Trans. Graph. 33, 2, Article 19 (2014), 21 pages. https: doi.org 10.11452558307

- Marcel Campen, Ryan Capouellez, Hanxiao Shen, Leyi Zhu, Daniele Panozzo, and Denis Zorin. 2021. efficient and robust discrete conformal equivalence with boundary. ACM Transactions on Graphics (TOG) 40, 6 (2021), 1-16.

- Roberto Cipolla and Peter Giblin. 2000. Visual Motion of curves and Surfaces. Cambridge University Press.

- Wolfgang Dahmen. 1989. Smooth piecewise quadric surfaces. In Mathematical methods in computer aided geometric design. Elsevier, 181-193.

- Doug DeCarlo. 2012. Depicting 3D shape using lines. In Proc. SPIE, Vol. 8291. 82918291-16. https: doi.org 10.111712.916463

- Philippe Decaudin. 1996. Cartoon Looking Rendering of 3D Scenes. Research Report 2919. INRIA. http: phildec.users.sf.net Research RR-2919.php

- Elmar Eisemann, Holger Winnemöller, John C. Hart, and David Salesin. 2008. Stylized Vector Art from 3D Models with Region Support. In Proceedings of the Nineteenth Eurographics Conference on Rendering (EGSR '08). Eurographics Association, 11991207. https: doi.org 10.1111 j.1467-8659.2008.01258.x

- Gershon Elber and Elaine Cohen. 1990. Hidden curve removal for Free Form Surfaces. In Proceedings of the 17th Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH '90). ACM, 95-104. https: doi.org 10.114597879.97890

- Rafael Sendra Ferrer, Sonia Pérez Díaz, and F Winkler. 2008. Rational algebraic curves: a computer algebra approach. Springer Berlin.

- Mark Gillespie, Boris Springborn, and Keenan Crane. 2021. Discrete conformal equivalence of polyhedral surfaces. ACM Transactions on Graphics 40, 4 (2021).

- Xianfeng David Gu, Feng Luo, Jian Sun, and Tianqi Wu. 2018. A discrete uniformization theorem for polyhedral surfaces. Journal of Differential Geometry 109, 2 (2018), 223-256.

- Ying He, Miao Jin, Xianfeng Gu, and Hong Qin. 2005. A 𝐶 1 globally interpolatory spline of arbitrary topology. In International Workshop on Variational, Geometric, and Level Set Methods in Computer Vision. Springer, 295-306.

- Aaron Hertzmann and Denis Zorin. 2000. Illustrating Smooth Surfaces. In Proceedings of the 27th Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH '00). ACM Press Addison-Wesley Publishing Co., 517-526. https: doi.org 10.1145344779.345074

- Tobias Isenberg, Nick Halper, and Thomas Strothotte. 2002. Stylizing silhouettes at interactive rates: From silhouette edges to silhouette strokes. In Computer Graphics Forum, Vol. 21. 249-258. https: doi.org 10.11111467-8659.00584

- Jüttler. 1998. Triangular Bézier surface patches with a linear normal vector field. In The mathematics of surfaces, VIII (R. Cripps, ed.). Info. Geom., Winchester, 431-446.

- Jüttler and M.L. Sampoli. 2000. Hermite interpolation by piecewise polynomial surfaces with rational offsets. Computer Aided Geometric Design 17, 4 (2000), 361385.

- Kirsanov, P. V. Sander, and S. J. Gortler. 2003. Simple silhouettes for Complex Surfaces. In Proceedings of the 2003 Eurographics ACM SIGGRAPH Symposium on Geometry Processing (SGP '03). Eurographics Association, 102-106.

- Chenxi Liu, Pierre Bénard, Aaron Hertzmann, and Shayan Hoshyari. 2023. ConTesse: Accurate Occluding Contours for Subdivision Surfaces. ACM Trans. Graph. 42, 1, Article 5 (Feb. 2023), 16 pages. https: doi.org 10.11453544778

- Marian Neamtu and Pia R Pfluger. 1994. Degenerate polynomial patches of degree 4 and 5 used for geometrically smooth interpolation in 3. Computer Aided Geometric Design 11, 4 (1994), 451-474.

- D. Northrup and Lee Markosian. 2000. Artistic silhouettes: A Hybrid Approach. In Proceedings of the 1st International Symposium on Non-photorealistic Animation and Rendering (NPAR '00). ACM, 31-37. https: doi.org 10.1145340916.340920

- Shinji Ogaki and Yusuke Tokuyoshi. 2011. Direct Ray Tracing of Phong Tessellation. Computer Graphics Forum 30, 4 (2011), 1337-1344. https: doi.org 10.1111 j.14678659.2011.01993.x

- Michael JD Powell and Malcolm A Sabin. 1977. Piecewise quadratic approximations on triangles. ACMTransactions on Mathematical Software (TOMS) 3, 4 (1977), 316-325.

- Takafumi Saito and Tokiichiro Takahashi. 1990. Comprehensible Rendering of 3-D Shapes. In Proceedings of the 17th Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH '90). ACM, 197-206. https: doi.org 10.114597879.97901

- Thomas W Sederberg and Tomoyuki Nishita. 1990. curve intersection using Bézier clipping. Computer-Aided Design 22, 9 (1990), 538-549.

- Boris Springborn, Peter Schröder, and Ulrich Pinkall. 2008. Conformal equivalence of triangle meshes. ACM Transactions on Graphics (TOG) 27, 3 (2008), 1-11.

- Matei Stroila, Elmar Eisemann, and John Hart. 2008. Clip Art Rendering of Smooth Isosurfaces. IEEE Transactions on Visualization and Computer Graphics 14, 1 (2008), 135-145. https: doi.org 10.1109 TVCG.2007.1058

- Ruth A. Weiss. 1966. BE VISION, A Package of IBM 7090 FORTRAN Programs to Draw Orthographic Views of Combinations of Plane and Quadric Surfaces. J. ACM 13, 2 (1966), 194-204. https: doi.org 10.1145321328.321330

- Georges Winkenbach and David H. Salesin. 1996. Rendering Parametric Surfaces in Pen and Ink. In Proceedings of the 23rd Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH '96). ACM, 469-476. https: doi.org 10.1145237170.237287

- Figure 8: Examples of of contour line sets obtained using our method on models from the modified dataset of [Liu et al. 2023]. (Bigguy and Monster Frog ©Bay Raitt. Fertility courtesy UU from AIM@SHAPE-VISIONAIR Shape Repository. Public domain Blub, Bob, and Ogre models by Keenan Crane. Killeroo ©headus.com.au. Open source Pawn model from OpenSubdiv.)

- perspective perspective Orthographic Orthographic

- Figure 9: Given a triangle mesh, we need a representation of the underlying smooth surface. Here we visualize the dependence of our smooth surface shape fitting on the weight 𝑤, without a projective transformation step. We use 𝑤 = 1 for all experiments in this paper. (Public domain Ogre model by Keenan Crane.) perspective perspective Orthographic Orthographic Low FOV High FOV

- Figure 10: perspective projection of a mesh, vs. orthographic projection of the projective-transformed mesh. In each pair, the two renderings are geometrically equivalent. (The shading differs, but is not used in contour detection and shown here only for visualization. Killeroo ©headus.com.au.) Input faces Time (s) blub bob car fertility killeroo spot_quad blub bob car fertility killeroo spot_quad Per frame Preprocessing Step Computation time

- Figure 11: Timing for our method, on meshes from the ConTesse [Liu et al. 2023] dataset. Orange circles show preprocessing computation time, and blue circles show per-frame time, averaged over 26 frames. While preprocessing can take several seconds, per-frame computation is very efficient, growing very slowly as a function of mesh size. Computation times were measured on a MacBook Pro 2.7Ghz Intel Core i7, 16Gb memory. The "car" mesh is more intensive at run-time due a very high shape complexity, requiring over a million ray-patch intersection tests per frame.
