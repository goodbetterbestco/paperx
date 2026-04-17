# Practical Ray Tracing of Trimmed NURBS Surfaces

William Martin, Elaine Cohen, Russell Fish, William Martin Elaine Cohen, Russell Fish Peter Shirley, Peter Shirley

Computer Science Department
S. Central Campus Drive
Computer Science Department 50 S. Central Campus Drive University of Utah Salt Lake City, UT 84112 [ wmartin | cohen | fish | shirley ] University of Utah

## Abstract

A system is presented for ray tracing trimmed NURBS surfaces. While approaches to components are drawn largely from existing literature, their combination within a single framework is novel. This paper also differs from prior work in that the details of an efficient implementation are fleshed out. Throughout, emphasis is placed on practical methods suitable to implementation in general ray tracing programs.

## 1 Introduction

The modeling community has embraced trimmed NURBS as a primitive of choice. The result has been a rapid proliferation in the number of models utilizing this representation. At the same time, ray tracing has become a popular method for generating computer graphics images of geometric models. Surprisingly, most ray tracing programs do not support the direct use of untessellated trimmed NURBS surfaces. The direct use of untessellated NURBS is desirable because tessellated models increase memory use which can be detrimental to runtime efficiency on modern architectures. In addition, tessellating models can result in visual artifacts, particularly in models with transparent components.

Although several methods of generating ray-NURBS intersections have appeared in the literature [3, 5, 8, 14, 17, 25, 27, 28], widespread adoption into ray tracing programs has not occurred. We believe this lack of acceptance stems from both the intrinsic algebraic complexity of these methods, and from the lack of emphasis in the literature on clean and efficient implementation. Wepresent a new algorithm for ray-NURBS intersection that addresses these issues. The algorithm modifies approaches already in the literature to attain efficiency and ease of implementation.

Our approach is outlined in Figure 1. We create a set of boxes that bound the underlying surface over a given parametric range. The ray is tested for intersection with these boxes, and for a particular box that is hit, a parametric value within the box is used to initiate root finding. The key issues are determining which boxes to use, how to efficiently manage computing intersections with them, how to do the root finding, and how to efficiently evaluate the geometry for a given parametric value.

We use refinement to generate the bounding volume hierarchy, which results in a shallower tree depth than other subdivisionbased methods. We also use an efficient refinement-based point evaluation method to speed root-finding. These choices turn out to be both reasonable to implement and efficient.

![Figure 1](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-1-p001.png)

*Figure 1: The basic method we use to ﬁnd the intersection of a ray and a parametric object shown in a 2D example. Left: The ray is tested against a series of axis-aligned bounding boxes. Right: For each box hit an initial guess is generated in the parametric interval the box bounds. Root ﬁnding is then iteratively applied until a convergence or a divergence criterion is met. find the intersection of a ray and a parametric object shown in a 2D example. Left: The ray is tested against a series of axis-aligned bounding boxes. Right: For each box hit an initial guess is generated in the parametric interval the box bounds. Root finding is then iteratively applied until a convergence or a divergence criterion is met.*

In Section 2 we present the bulk of our method, in particular how to create a hierarchy of bounding boxes and how to perform root finding within a single box to compute an intersection with an untrimmed NURBS surface. In Section 3 we describe how to extend the method to trimmed NURBS surfaces. Finally in Section 4 we show some results from our implementation of the algorithm.

## 2 Ray Tracing NURBS

In ray tracing a surface, we pose the question 'At what points does a ray intersect the surface?' We define a ray as having an origin and a unit direction

$$
\mathbf{r}(t)=\mathbf{o}+\hat{\mathbf{d}} * t
$$

A non-uniform rational B-spline (NURBS) surface can be formulated as

$$
\mathbf{S}^{w}(u, v)=\sum_{i=0}^{M-1} \sum_{j=0}^{N-1} \mathbf{P}_{i, j}^{w} B_{j, k_{u}}(u) B_{i, k_{v}}(v)
$$

where the superscript \(w\) denotes that our formulation produces a point in rational four space, which must be normalized by the homogeneous coordinate prior to display. The \(\left\{\mathbf{P}_{i, j}^{w}\right\}_{i=0, j=0}^{M-1, N-1}\) are the control points ( \(w_{i, j} x_{i, j}, w_{i, j} y_{i, j}, w_{i, j} z_{i, j}, w_{i, j}\) ) of the

$$
\begin{aligned} \tau_{u} & =\left\{u_{j}\right\}_{j=0}^{N-1+k_{u}} \\ \tau_{v} & =\left\{v_{i}\right\}_{i=0}^{M-1+k_{v}} \end{aligned}
$$

$$
\begin{aligned} B_{j, k_{u}}(u) & \equiv\left\{\begin{array}{cl} 1 & \text { if } k_{u}=1 \text { and } u \in\left[u_{j}, u_{j+1}\right) \\ 0 & \text { if } k_{u}=1 \text { and } u \notin\left[u_{j}, u_{j+1}\right) \\ \frac{u-u_{j}}{u_{j+k_{u}-1}-u_{j}} B_{j, k_{u}-1}(u)+\frac{u_{j+k_{u}}-u}{u_{j+k_{u}}-u_{j+1}} B_{j+1, k_{u}-1}(u) & \text { otherwise } \\ 1 & \text { if } k_{v}=1 \text { and } v \in\left[v_{i}, v_{i+1}\right) \\ 0 & \text { if } k_{v}=1 \text { and } v \notin\left[v_{i}, v_{i+1}\right) \end{array}\right. \\ B_{i, k_{v}}(v) & \text { otherwise. } \end{aligned}
$$

Such a surface \(\mathbf{S}\) is defined over the domain \(\left[u_{k_{u}-1}, u_{N}\right) \times\left[v_{k_{v}-1}, v_{M}\right)\). Each non-empty subinterval \(\left[u_{j}, u_{j+1}\right) \times\left[v_{i}, v_{i+1}\right)\) corresponds to a surface patch.

In this discussion, we assume that the reader has a basic familiarity with B-Splines. For further introduction, please refer to [2, 7, 10, 20]. [2, 7, 10, 20]. Following the development by Kajiya [12], we rewrite the ray \(\mathbf{r}\) as the intersection of two planes, \(\left\{\mathbf{p} \mid \mathbf{P}_{\mathbf{1}} \cdot(\mathbf{p}, 1)=0\right\}\) and

$$
\mathbf{N}_{\mathbf{1}}= \begin{cases}\left(\hat{\mathbf{d}}_{y},-\hat{\mathbf{d}}_{x}, 0\right) & \text { if }\left|\hat{\mathbf{d}}_{x}\right|>\left|\hat{\mathbf{d}}_{y}\right| \text { and }\left|\hat{\mathbf{d}}_{x}\right|>\left|\hat{\mathbf{d}}_{z}\right| \\ \left(0, \hat{\mathbf{d}}_{z},-\hat{\mathbf{d}}_{y}\right) & \text { otherwise } .\end{cases}
$$

Thus, \(\mathbf{N}_{\mathbf{1}}\) is always perpendicular to the ray direction \(\hat{\mathbf{d}}\), as desired. \(\mathbf{N}_{\mathbf{2}}\) is simply

$$
\mathbf{N}_{\mathbf{2}}=\mathbf{N}_{\mathbf{1}} \times \hat{\mathbf{d}}
$$

Since both planes contain the origin \(\mathbf{o}\), it must be the case that \(\mathbf{P}_{\mathbf{1}} \cdot(\mathbf{o}, 1)=\mathbf{P}_{\mathbf{2}} \cdot(\mathbf{o}, 1)=0\). Thus,

$$
\begin{aligned} d_{1} & =-\mathbf{N}_{\mathbf{1}} \cdot \mathbf{o} \\ d_{2} & =-\mathbf{N}_{\mathbf{2}} \cdot \mathbf{o} . \end{aligned}
$$

$$
An intersection point on the surface \(\mathbf{S}\) must satisfy the conditions
$$

$$
\begin{aligned} & \mathbf{P}_{\mathbf{1}} \cdot(\mathbf{S}(u, v), 1)=0 \\ & \mathbf{P}_{\mathbf{2}} \cdot(\mathbf{S}(u, v), 1)=0 \end{aligned}
$$

The resulting implicit equations can be solved for \(u\) and \(v\) using numerical methods.

Ray tracing a NURBS surface proceeds in a series of steps. As a preprocess, the control mesh is flattened using refinement. There are several reasons for this. For Newton to converge quadratically, our initial guess for the root ( \(u_{*}, v_{*}\) ) must be close. By refining the mesh, we can bound the various sub-patches, and use the bounding volume hierarchy (BVH) both to cull the rays, and also to narrow the prospective parametric domain and so yield a good initial root estimate. It is important to note that the refined mesh does not persist in memory. It is used to generate the BVH and then is discarded.

During the intersection process, if we reach a leaf of the BVH, we apply traditional numerical root finding to the implicit equations above. The result will determine either a single ( \(u_{*}, v_{*}\) ) value or that no root exists. In the sections that follow, we discuss the details of flattening, generating the BVH, root finding, evaluation, and partial refinement. Together these are all that is needed for computing ray-NURBS intersections.

### 2.1 Flattening

For Newton to converge both swiftly and reliably, the initial guess must be suitably close to the actual root. We employ a flattening procedure-i.e., refining subdividing the control mesh so that each span meets some flatness criteria-both to ensure that the initial guess is a good one, and for the purpose of generating a bounding volume hierarchy for ray culling.

A wealth of research exists on polygonization of spline surfaces, e.g. [1, 13, 19, 22], and for the most part, these approaches can be readily applied to the problem of spline flattening. Some differences merit discussion. first, in the case of finding the numerical ray-spline intersection, we are not so much interested in flatness as in guaranteeing that there are not multiple roots within a leaf node of the bounding volume hierarchy. We note that this guarantee cannot always be made, particularly for nodes which contain silhouettes according to the ray source. Fortunately, the convergence problems which these boundary cases entail can also be improved with the mesh flattening we prescribe. We would also like to avoid any local maxima and minima that would serve to delay or worse yet prevent the convergence of our scheme. The flatness testing utilized by tessellation routines can be used to prevent these situations.

As ray tracing splines is at the outset a complicated task, we recommend the application of as simple a flattening procedure as possible. We have examined two flattening techniques in detail. The first of these is an adaptive subdivision scheme given by Peterson in [19]. As the source for the Graphics Gems is publicly available we will not discuss that method here, but instead refer the reader to the source.

The second approach we have considered is curvature-based refinement of the knot vectors. The number of knots to add to a knot interval is based on a simple heuristic which we now describe.

Suppose we have a B-spline curve \(\mathbf{c}(t)\). An oracle for determining the extent to which the span \(\left[t_{i}, t_{i+1}\right)\) should be refined is given by the product of its maximum curvature and its length over that span. Long curve segments should be divided in order to ensure that the initial guess for the numerical solver is reasonably close to the actual root. High curvature regions should be split to avoid multiple roots. As we are utilizing maximum curvature as a measure of flatness, our heuristic will be overly conservative for curves other than circles. The heuristic value for the number of knots to add to the current span is given by

$$
n_{1}=C_{1} * \max _{\left[t_{i}, t_{i+1}\right)}\{\operatorname{curvature}(\mathbf{c}(t))\} * \operatorname{arclen}(\mathbf{c}(t))_{\left[t_{i}, t_{i+1}\right)}
$$

We also choose to bound the deviation of the curve from its linear approximation. This notion will imbue our heuristic with scale dependence. Thus, for example, large circles will be broken into more pieces than small circles. Erring again on the conservative side, suppose our curve span is a circle with radius \(r\), which we are approximating with linear segments. A measure of the accuracy of the approximation can be phrased in terms of a chord height \(h\) which gives the maximum deviation of the facets from the circle. Observing Figure 2, it can be seen that

$$
\begin{aligned} h & =r-d \\ & =r-r \cos \frac{\theta}{2} \\ & \approx r\left(1-\left(1-\frac{\theta^{2}}{8}\right)\right) \\ & =\frac{r \theta^{2}}{8} . \end{aligned}
$$

Thus, we have

$$
n_{2}=\frac{2 \pi}{\sqrt{\frac{8 h}{r}}}
$$

$$
\begin{aligned} \operatorname{curvature}(\mathbf{c}(t)) & =\frac{\left|\mathbf{c}^{\prime \prime}(t) \times \mathbf{c}^{\prime}(t)\right|}{\left|\mathbf{c}^{\prime}(t)\right|^{3}} \\ & =\frac{\left|\mathbf{c}^{\prime \prime}(t)\right|\left|\mathbf{c}^{\prime}(t)\right||\sin \theta|}{\left|\mathbf{c}^{\prime}(t)\right|^{3}} \\ & =\frac{\left|\mathbf{c}^{\prime \prime}(t)\right||\sin \theta|}{\left|\mathbf{c}^{\prime}(t)\right|^{2}} \\ & \leq \frac{\left|\mathbf{c}^{\prime \prime}(t)\right|}{\left|\mathbf{c}^{\prime}(t)\right|^{2}} \end{aligned}
$$

![Figure 2](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-2-p004.png)

*Figure 2: Illustration of the chord height tolerance heuristic.*

$$
\begin{aligned} & =\frac{2 \pi \sqrt{r}}{\sqrt{8 h}} \\ & \approx C_{2} * \sqrt{\operatorname{arclen}(\mathbf{c}(t))_{\left[t_{i}, t_{i+1}\right)}} . \end{aligned}
$$

Combining the preceding oracles for curve behavior, our heuristic for the number of knots \(n\) to add to an interval will be \(n_{1} * n_{2}\) :

$$
n=C * \max _{\left[t_{i}, t_{i+1}\right)}\{\operatorname{curvature}(\mathbf{c}(t))\} * \operatorname{arclen}(\mathbf{c}(t))_{\left[t_{i}, t_{i+1}\right)}^{3 / 2}
$$

Since the maximum curvature and the arc length are in general hard to come by, we will estimate their values. The arc length of \(\mathbf{c}\) over the interval is given by

$$
\int_{t_{i}}^{t_{i+1}}\left|\mathbf{c}^{\prime}(t)\right| d t=\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\} *\left(t_{i+1}-t_{i}\right)
$$

We make the simplification curvature \((\mathbf{c}(t)) \approx \frac{\left|\mathbf{c}^{\prime \prime}(t)\right|}{\left|\mathbf{c}^{\prime}(t)\right|^{2}}\). In general, this estimate of the curvature will be overstated. The error will be on the side of refining too finely rather than not finely enough, so it is an acceptable trade-off to get the speed of computing second derivatives instead of curvature.

\max _{\left[t_{i}, t_{i+1}\right)}\left\{\text { curvature }(\mathbf{c}(t)\} \approx \frac{\max _{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime \prime}(t)\right|\right\}}{\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\}^{2}} .\right.

If we assume the curve is polynomial, then the first derivative restricted to the interval \(\left[t_{i}, t_{i+1}\right)\) is given by

$$
\mathbf{c}^{\prime}(t)=\sum_{j=i-k+2}^{i} \frac{(k-1)\left(\mathbf{P}_{\mathbf{j}}-\mathbf{P}_{\mathbf{j}-\mathbf{1}}\right)}{t_{j+k-1}-t_{j}} B_{j, k-1}(t)
$$

where \(\left\{\mathbf{P}_{\mathbf{j}}\right\}\) are the control points of the curve. The derivative of a rational curve is considerably more complicated. While the polynomial formulation of the derivative is in general a poor approximation to the rational derivative, in the case of flattening

$$
\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\mathbf{c}^{\prime}(t)\right\} \approx \frac{1}{k-1} \sum_{j=i-k+2}^{i}(k-1) \frac{\left(\mathbf{P}_{\mathbf{j}}-\mathbf{P}_{\mathbf{j}-\mathbf{1}}\right)}{t_{j+k-1}-t_{j}}=\frac{1}{k-1} \sum_{j=i-k+2}^{i} \mathbf{V}_{\mathbf{j}}
$$

Since \(\sum B_{j, k-1}(t)=1\), we can approximate the average velocity by averaging the control points \(\mathbf{V}_{\mathbf{j}}\) of the derivative curve:

where \(\mathbf{V}_{\mathbf{j}}=(k-1) \frac{\left(\mathbf{P}_{\mathbf{j}}-\mathbf{P}_{\mathbf{j}-\mathbf{1}}\right)}{t_{j+k-1}-t_{j}}\). The average speed is therefore

$$
\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\} \approx \frac{1}{k-1} \sum_{j=i-k+2}^{i}\left|\mathbf{V}_{\mathbf{j}}\right|
$$

$$
The second derivative over \(\left[t_{i}, t_{i+1}\right)\) is given by
$$

$$
\mathbf{c}^{\prime \prime}(t)=\sum_{j=i-k+3}^{i}(k-2) \frac{\left[\mathbf{V}_{\mathbf{j}}-\mathbf{V}_{\mathbf{j}-\mathbf{1}}\right]}{t_{j+k-2}-t_{j}} B_{j, k-2}(t)=\sum_{j=i-k+3}^{i} \mathbf{A}_{\mathbf{j}} B_{j, k-2}(t)
$$

Using the convex hull property again, the maximum magnitude of the second derivative is approximated by the maximum magnitude of the second derivative curve control points \(\mathbf{A}_{\mathbf{j}}\) :

$$
\max _{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime \prime}(t)\right|\right\} \approx \max _{i-k+3 \leq j \leq i}\left\{\left|\mathbf{A}_{\mathbf{j}}\right|\right\}
$$

\begin{aligned} n & =C * \frac{\max _{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime \prime}(t)\right|\right\} *\left[\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\} *\left(t_{i+1}-t_{i}\right)\right]^{3 / 2}}{\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\}^{2}} \\ & =C * \frac{\left.\max _{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime \prime}(t)\right|\right\} *\left(t_{i+1}-t_{i}\right)\right]^{3 / 2}}{\operatorname{avg}_{\left[t_{i}, t_{i+1}\right)}\left\{\left|\mathbf{c}^{\prime}(t)\right|\right\}^{1 / 2}} \\ & =C * \frac{\max _{i-k+3 \leq j \leq i}\left\{\left|\mathbf{A}_{\mathbf{j}}\right|\right\}\left(t_{i+1}-t_{i}\right)^{3 / 2}}{\left(\frac{1}{k-1} \sum_{j=i-k+2}^{i}\left|\mathbf{V}_{\mathbf{j}}\right|\right)^{1 / 2}} \end{aligned}

For each row of the mesh, we apply the above heuristic to calculate how many knots need to be added to each \(u\) knot interval, the final number being the maximum across all rows. This process is repeated for each column in order to refine the \(v\) knot vector. The inserted knots are spaced uniformly within the existing knot intervals.

As a final step in the flattening routine, we "close" all of the knot intervals in the refined knot vectors \(\mathbf{t}_{\mathbf{u}}\) and \(\mathbf{t}_{\mathbf{v}}\). By this, we mean that we give multiplicity \(k_{u}-1\) to each internal knot of \(\mathbf{t}_{\mathbf{u}}\) and multiplicity \(k_{u}\) to each end knot. Similarly, we give multiplicities of \(k_{v}-1\) and \(k_{v}\) to the internal and external knots, respectively, of \(\mathbf{t}_{\mathbf{v}}\). The result is a Bézier surface patch corresponding to each non-empty interval \(\left[u_{i}, u_{i+1}\right) \times\left[v_{j}, v_{j+1}\right)\) of \(\mathbf{t}_{\mathbf{u}} \times \mathbf{t}_{\mathbf{v}}\), which we can bound using the convex hull of the corresponding refined surface mesh points. This becomes critical in the next section.

The refined knot vectors determine the refinement matrix used to transform the existing mesh into the refined mesh. There are many techniques for generating this 'alpha matrix.' As it is not critical that this be fast, we refer the reader to several sources [4, 6, 7, 16].

Both adaptive subdivision and curvature-based refinement should yield acceptable results. Both allow the user to adjust the resulting flatness via a simple intuitive parameter. We have preferred the latter mainly because it produces its result in a single pass, without the creation of unnecessary intermediate points. Adaptive subdivision does have the advantage of inserting one knot value at a time, so one does not necessarily need to implement the full machinery of the Oslo algorithm [6]. Instead, one can opt for a simpler approach, such as that of Boehm [4]. It is not clear which method produces more optimal meshes in general. On the one hand, adaptive subdivision computes intermediate results which it then inspects to determine where additional subdivision is required. On the other hand, our method utilizes refinement (we only subdivide in the last step), and this converges more swiftly to the underlying surface than does subdivision.

Neither technique is entirely satisfactory. Each considers the various parametric directions independently, while subdivision and refinement clearly impact both directions. The curvature-based refinement method refines a knot interval without considering the impact of that refinement on neighboring intervals. This can lead to unnecessary refinement. Neither makes any attempt to find optimal placement of inserted knots.

The adaptive subdivision and curvature-based refinement methods are the products of the inevitable compromise between refinement speed and quality. Both satisfy the efficiency and accuracy demands of the problem at hand.

A point which we do not wish to sweep under the carpet is that the selection of the flatness parameter is empirical and left to the user. As this parameter directly impacts the convergence of the root finding process, it should be carefully chosen. Choosing a value too small may cause the numerical solver to fail to converge or to converge to one of several roots in the given parametric interval. This effect will probably be most noticeable along silhouette edges and patch boundaries. On the other hand, choosing a value too large will result in over-refinement of the surface leading to a deeper bounding volume hierarchy, and therefore, potentially more time per ray. We have found that after some experimentation, one develops an intuition for the sorts of parameters which work for a surface. For an example of a system which guarantees convergence without user intervention, see Toth [27]. This guarantee is made at the price of linear convergence in the root finding procedure.

### 2.2 Bounding Volume Hierarchy

We build a bounding volume hierarchy using the points of the refined control mesh we found in the previous section. The root and internal nodes of the tree will contain simple primitives which bound portions of the underlying surface. The leaves of the tree are special objects, which we call interval objects, are used to provide an initial guess (in our case, the midpoint of the bracketing parametric interval) to the Newton iteration. We will now examine the specifics in more detail.

The convex hull property of B-spline surfaces guarantees that the surface is contained in the convex hull of its control mesh. As a result, any convex objects which bound the mesh will bound the underlying surface. We can actually make a stronger claim; because we closed the knot intervals in the last section [made the multiplicity of the internal knots \(k-1\) ], each nonempty interval \(\left[u_{i}, u_{i+1}\right) \times\left[v_{j}, v_{j+1}\right)\) corresponds to a surface patch which is completely contained in the convex hull of its corresponding mesh points. Thus, if we produce bounding volumes for each of these intervals, we will have completely enclosed the surface. We form the tree by sorting the volumes according to the axis direction which has greatest extent across the bounding volumes, splitting the data in half, and repeating the process.

There remains the dilemma of which primitive to use as a bounding volume. Many different objects have been tried including spheres [8], axis-aligned boxes [8, 25, 28], oriented boxes [8], and parallelepipeds [3]. There is generally a tradeoff between speed of intersection and tightness of fit. The analysis is further complicated by the fact that bounding volume performance depends on the type of scene being rendered.

We have preferred simplicity, narrowing our choice to spheres and axis-aligned boxes. Spheres have a very fast intersection test. However, spheres, by definition, can never be flat. Since our intersection routines require surfaces which are locally 'flat,' spheres did not seem to be a natural choice.

Axis-aligned boxes have many advantages. first, they can become flat [at least along axis directions], so they can provide a tighter fit than spheres. The union of two axis-aligned boxes is easily computed. This computation is necessary when building the BVH from the leaves. With many other bounding volumes, the leaves of the subtree must be examined individually to produce reasonable bounding volumes. Finally, many scenes are axis-aligned, especially in the case of architectural walkthroughs. Axis-aligned boxes are nearly ideal in this circumstance.

A simple ray-box intersection routine is intuitive, and so we omit its discussion. An optimized version can be found in the paper by Smits [24].

### 2.3 Root Finding

Given a ray as the intersection of planes \(\mathbf{P}_{\mathbf{1}}=\left(\mathbf{N}_{\mathbf{1}}, d_{1}\right)\) and \(\mathbf{P}_{\mathbf{2}}=\left(\mathbf{N}_{\mathbf{2}}, d_{2}\right)\), our task is to solve for the roots ( \(u_{*}, v_{*}\) ) of

$$
\mathbf{F}(u, v)=\binom{\mathbf{N}_{\mathbf{1}} \cdot \mathbf{S}(u, v)+d_{1}}{\mathbf{N}_{\mathbf{2}} \cdot \mathbf{S}(u, v)+d_{2}}
$$

A variety of numerical methods can be applied to the problem. An excellent reference for these techniques is [21, pp 347393]. We use Newton's method for several reasons. first, it converges quadratically if the initial guess is close, which we ensure by constructing a bounding volume hierarchy. Furthermore, the surface derivatives exist and are calculated at cost comparable to that of surface evaluation. This means that there is likely little computational advantage to utilizing approximate derivative methods such as Broyden.

Newton's method is built from a truncated Taylor's series. Our iteration takes the form

$$
\binom{u_{n+1}}{v_{n+1}}=\binom{u_{n}}{v_{n}}-\mathbf{J}^{-1}\left(u_{n}, v_{n}\right) * \mathbf{F}\left(u_{n}, v_{n}\right)
$$

where \(\mathbf{J}\) is the Jacobian matrix of \(\mathbf{F}\), defined as

$$
\mathbf{J}=\left(\mathbf{F}_{\mathbf{u}}, \mathbf{F}_{\mathbf{v}}\right)
$$

### 2.4 Evaluation

The Newton iteration requires us to perform surface and derivative evaluation at a point (u, v) on the surface. In this section we examine how this can be accomplished efficiently. Prior work on efficient evaluation can be found in [15, 16].

We begin by examining the problem in the context of B-spline curves. We then generalize the result to surfaces. The development parallels that found in [26].

We evaluate a curve \(\mathbf{c}(t)\) by using refinement to stack \(k-1\) knots (where \(k\) is the order of the curve) at the desired parameter value \(t_{*}\). The refined curve is defined over a new knot vector \(\mathbf{t}\) with basis functions \(N_{i, k}(t)\) and new control points \(\omega_{i} \mathbf{D}_{i}\). value \(t_{*}\). The refined curve is defined over a new knot vector \(\mathbf{t}\) with basis functions \(N_{i, k}(t)\) and new control points \(\omega_{i} \mathbf{D}_{i}\). Recall the recurrence for the B-Spline basis functions:

$$
N_{i, k}(t)=\left\{\begin{array}{cl} 1 & \text { if } k=1 \text { and } t \in\left[t_{i}, t_{i+1}\right) \\ 0 & \text { if } k=1 \text { and } t \notin\left[t_{i}, t_{i+1}\right) \\ \frac{t-t_{i}}{t_{i+k-1}-t_{i}} N_{i, k-1}(t)+\frac{t_{i+k}-t}{t_{i+k}-t_{i+1}} N_{i+1, k-1}(t) & \text { otherwise. } \end{array}\right.
$$

Let \(t_{*} \in\left[t_{\mu}, t_{\mu+1}\right)\). As a result of refinement, \(t_{*}=t_{\mu}=\ldots=t_{\mu-k+2}\). According to the definition of the basis functions,

$$
\begin{aligned} N_{\mu, 2}\left(t_{*}\right) & =\frac{t_{*}-t_{\mu}}{t_{\mu+k-1}-t_{\mu}} N_{\mu, 1}\left(t_{*}\right)+\frac{t_{i+k}-t_{*}}{t_{\mu+k}-t_{\mu+1}} N_{\mu+1,1}\left(t_{*}\right) \\ & =0 * 1+\frac{t_{i+k}-t_{*}}{t_{\mu+k}-t_{\mu+1}} * 0 \\ & =0 \end{aligned}
$$

Likewise, the only non-zero order \(k=3\) terms will be those dependent on \(N_{\mu-1,2}: N_{\mu-1,3}\) and \(N_{\mu-2,3}\).

$$
\begin{aligned} N_{\mu-1,3}\left(t_{*}\right) & =\frac{t_{*}-t_{\mu-1}}{(\cdots)} * 1+(\cdots) * 0 \\ & =0 \\ N_{\mu-2,3}\left(t_{*}\right) & =(\cdots) * 0+\frac{t_{\mu-2+k}-t_{*}}{t_{\mu-2+k}-t_{\mu-1}} * 1 \\ & =1 \end{aligned}
$$

The pattern that emerges is that \(N_{\mu-k+1, k}\left(t_{*}\right)=1\). A straightforward consequence of this result is

$$
\mathbf{c}\left(t_{*}\right)=\frac{\sum_{i} N_{i, k}\left(t_{*}\right) \omega_{i} \mathbf{D}_{\mathbf{i}}}{\sum_{i} N_{i, k}\left(t_{*}\right) \omega_{i}}=\frac{\omega_{\mu-k+1} \mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}}{\omega_{\mu-k+1}}=\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}
$$

The point with index µ -k +1 in the refined control polygon yields the point on the curve. A further analysis can be used to yield the derivative. Given a rational curve where D ω i = ω i D i, the derivative is given by the quotient rule

$$
\mathbf{c}(t)=\frac{\sum_{i} N_{i, k}(t) \omega_{i} \mathbf{D}_{\mathbf{i}}}{\sum_{i} N_{i, k}(t) \omega_{i}}=\frac{\sum_{i} N_{i, k}(t) \mathbf{D}_{\mathbf{i}}^{\omega}}{\sum_{i} N_{i, k}(t) \omega_{i}}=\frac{\mathbf{D}(t)}{\omega(t)},
$$

$$
\mathbf{c}^{\prime}(t)=\frac{\omega(t)\left(\mathbf{D}^{\omega}\right)^{\prime}(t)-\mathbf{D}^{\omega}(t) \omega^{\prime}(t)}{\omega(t)^{2}} .
$$

By the preceding analysis \(\mathbf{D}^{\omega}\left(t_{*}\right)=\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega}\). Likewise, \(\omega\left(t_{*}\right)=\omega_{\mu-k+1}\). The derivative of the B-Spline basis function is given by

$$
N_{i, k}^{\prime}(t)=(k-1)\left[\frac{N_{i, k-1}(t)}{t_{i+k-1}-t_{i}}-\frac{N_{i+1, k-1}(t)}{t_{i+k}-t_{i+1}}\right]
$$

Evaluating the derivative at \(t_{*}\), we have

$$
\begin{aligned} \left(\mathbf{D}^{\omega}\right)^{\prime}\left(t_{*}\right) & =\sum_{i} N_{i, k}^{\prime}\left(t_{*}\right) \mathbf{D}_{\mathbf{i}}^{\omega} \\ & =(k-1) \sum_{i} \mathbf{D}_{\mathbf{i}}^{\omega}\left(\frac{N_{i, k-1}\left(t_{*}\right)}{t_{i+k-1}-t_{i}}-\frac{N_{i+1, k-1}\left(t_{*}\right)}{t_{i+k}-t_{i+1}}\right) \\ & =(k-1)\left[\sum_{i} \mathbf{D}_{\mathbf{i}}^{\omega} \frac{N_{i, k-1}\left(t_{*}\right)}{t_{i+k-1}-t_{i}}-\sum_{i} \mathbf{D}_{\mathbf{i}}^{\omega} \frac{N_{i+1, k-1}\left(t_{*}\right)}{t_{i+k}-t_{i+1}}\right] . \end{aligned}
$$

Therefore,

$$
\left(\mathbf{D}^{\omega}\right)^{\prime}\left(t_{*}\right)=(k-1)\left[\frac{\mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}^{\omega}}{t_{\mu+1}-t_{\mu-k+2}}-\frac{\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega}}{t_{\mu+1}-t_{\mu-k+2}}\right]
$$

$$
\omega^{\prime}\left(t_{*}\right)=(k-1)\left[\frac{\omega_{\mu-k+2}}{t_{\mu+1}-t_{\mu-k+2}}-\frac{\omega_{\mu-k+1}}{t_{\mu+1}-t_{\mu-k+2}}\right]
$$

$$
Plugging in for \(\mathbf{c}^{\prime}(t)\)
$$

$$
\begin{aligned} \mathbf{c}^{\prime}\left(t_{*}\right) & =(k-1)\left[\frac{\frac{\mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}^{\omega}-\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega}}{t_{\mu+1}-t_{\mu-k+2}} \omega_{\mu-k+1}-\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega} \frac{\omega_{\mu-k+2}-\omega_{\mu-k+1}}{t_{\mu+1}-t_{\mu-k+2}}}{\omega_{\mu-k+1}^{2}}\right] \\ & =\frac{k-1}{\left(t_{\mu+1}-t_{\mu-k+2}\right) \omega_{\mu-k+1}}\left[\mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}^{\omega}-\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega} \frac{\omega_{\mu-k+2}}{\omega_{\mu-k+1}}\right] \\ & =\frac{k-1}{\left(t_{\mu+1}-t_{\mu-k+2}\right) \omega_{\mu-k+1}}\left[\omega_{\mu-k+2} \mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}-\omega_{\mu-k+1} \mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}} \frac{\omega_{\mu-k+2}}{\omega_{\mu-k+1}}\right] \\ & =\frac{(k-1) \omega_{\mu-k+2}}{\left(t_{\mu+1}-t_{*}\right) \omega_{\mu-k+1}}\left[\mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}-\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}\right] \end{aligned}
$$

The result for surface evaluation follows directly from the curve derivation, due to the independence of the parameters in the tensor product, so we shall simply state the results:

$$
\begin{aligned} \mathbf{S}\left(u_{*}, v_{*}\right) & =\mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1}} \\ \mathbf{S}_{\mathbf{u}}\left(u_{*}, v_{*}\right) & =\frac{\left(k_{u}-1\right) \omega_{\mu_{u}-k_{u}+2, \mu_{v}-k_{v}+1}}{\left(u_{\mu_{u}+1}-u_{*}\right) \omega_{\mu_{u}-k_{u}+1, \mu_{v}-k_{v}+1}}\left[\mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{2}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1}}-\mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1}}\right] \\ \mathbf{S}_{\mathbf{v}}\left(u_{*}, v_{*}\right) & =\frac{\left(k_{v}-1\right) \omega_{\mu_{u}}-k_{u}+1, \mu_{v}-k_{v}+2}{\left(v_{\mu_{v}+1}-v_{*}\right) \omega_{\mu_{u}-k_{u}+1, \mu_{v}-k_{v}+1}}\left[\mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{2}}-\mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1}}\right] \end{aligned}
$$

The normal \(\mathbf{n}(u, v)\) is given by the cross product of the first order partials:

$$
\mathbf{n}\left(u_{*}, v_{*}\right)=\mathbf{S}_{\mathbf{u}}\left(u_{*}, v_{*}\right) \times \mathbf{S}_{\mathbf{v}}\left(u_{*}, v_{*}\right) .
$$

If the surface is not regular (i.e., \(\mathbf{S}_{\mathbf{u}} \times \mathbf{S}_{\mathbf{v}}=0\) ), then our computation may erroneously generate a zero surface normal. We

### 2.5 Partial Refinement

We still need to explain how to calculate the points in the refined mesh so that we can evaluate surface points and derivatives. What follows is drawn directly from Lyche et al. [16], tailored to our specialized needs. We again formulate our solution in the context of curves, and then generalize the result to surfaces.

Earlier we proposed to evaluate the curve \(\mathbf{c}\) at \(t_{*}\) by stacking \(k-1 t_{*}\)-valued knots in its knot vector \(\tau\) to generate the refined knot vector \(\mathbf{t}\). The B-Spline basis transformation defined by this refinement yields a matrix \(\mathbf{A}\) which can be used to calculate the refined control polygon \(\mathbf{D}^{\omega}\) from the original polygon \(\mathbf{P}^{\mathbf{w}}\) :

$$
\mathbf{D}^{\omega}=\mathbf{A} \mathbf{P}^{\mathbf{w}} .
$$

We are not interested in calculating the full alpha matrix \(\mathbf{A}\), but merely rows \(\mu-k+2\) and \(\mu-k+1\), as these are used to generate the points \(\mathbf{D}_{\mu-\mathbf{k}+\mathbf{2}}^{\omega}\) and \(\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega}\) which are required for point and derivative evaluation. Suppose \(t_{*} \in\left[\tau_{\mu^{\prime}}, \tau_{\mu^{\prime}+1}\right)\). We can generate the refinement for row \(\mu+k-1\) using a triangular scheme

$$
\begin{array}{lcc} & & \alpha_{\mu^{\prime}, 0}^{\prime} \\ & \alpha_{\mu^{\prime}-1,1}^{\prime} & \alpha_{\mu^{\prime}, 1}^{\prime} \\ & \vdots & \vdots \\ \alpha_{\mu^{\prime}-\nu, \nu}^{\prime} & \cdots & \alpha_{\mu^{\prime}, \nu}^{\prime} \end{array}
$$

where ν is the number of knots we are inserting and

$$
\begin{aligned} \alpha_{j, 1}^{\prime} & =\delta_{j, \mu^{\prime}} \\ \alpha_{j, p+1}^{\prime} & =\gamma_{j, p} \alpha_{j, p}^{\prime}+\left(1-\gamma_{j+1, p}\right) \alpha_{j+1, p}^{\prime} \\ \gamma_{j, p} & = \begin{cases}\left(t_{*}-\tau_{\mu^{\prime}-p+j-(k-1-\nu)}\right) / d, & \text { if } d=\tau_{\mu^{\prime}+1+j}-\tau_{\mu^{\prime}-p+j-(k-1-\nu)}>0 \\ \text { arbitrary } & \text { otherwise. }\end{cases} \end{aligned}
$$

\(\mathbf{A}_{\mu-k+1, j}=\alpha_{j, \nu}^{\prime}\) for \(j=\mu^{\prime}-\nu, \cdots, \mu^{\prime}\) and \(\mathbf{A}_{i, j}=0\) otherwise. If \(n\) knots exist in the original knot vector \(\tau\) with value \(t_{*}\), then \(\nu=\max \{k-1-n, 1\}-\) that is to say, we always insert at least 1 knot. The quantity \(\nu\) is used in the triangular scheme above to allow one to skip those basis functions which are trivially 0 or 1 due to repeated knots. As a result of this triangular scheme, we generate basis functions in place and avoid redundant computation of \(\alpha^{\prime}\) values for subsequent levels.

The procedure of knot insertion we propose is analogous to B´ ezier subdivision. In Figure 4 a B´ ezier curve has been subdivided at t = . 5, generating a refined polygon { p i } from the original polygon { P i. Recall that a B´ ezier curve is simply a B-Spline curve with open end conditions, in this case, with knot vector τ = { 0, 0, 0, 0, 1, 1, 1, 1. The refined knot vector is then t = { 0, 0, 0, 0, . 5, . 5, . 5, 1, 1, 1, 1. According to our definitions, µ = 6, µ ′ = 3. Thus, the point on the surface should be indexed µ -k +1 = 6-4 + 1 = 3, which agrees with the figure. We observe that \(p_{3}\) is a convex blend of \(p_{2}\) and \(p_{4}\). Likewise, in the refinement scheme we propose, the point on the curve \(\mathbf{D}_{\mu-\mathbf{k}+\mathbf{1}}^{\omega}\) will be a convex blend of the points \(\mathbf{D}_{\mu-\mathbf{k}}^{\omega}\) and \(\mathbf{D}_{\mu-\mathbf{k + 2}}^{\omega}\). The blend factor will be \(\gamma_{\mu^{\prime}, 0}\). The dependency graph shown in Figure 5 will help to clarify. The factor \(\gamma_{\mu^{\prime}, 0}\) is introduced at the first level of the recurrence. The leaf terms can be written as

![Figure 4](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-4-p011.png)

*Figure 4: Original mesh and reﬁned mesh which results from B´ezier subdivision. Original mesh and refined mesh which results from B´ ezier subdivision.*

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-5-p011.png)

*Figure 5: Graph showing how the factor γ µ ′ , 0 propagates through the recurrence.*

$$
\alpha_{j, \nu}^{\prime}=\left(1-\gamma_{\mu^{\prime}, 0}\right) l_{j, \nu}+\gamma_{\mu^{\prime}, 0} r_{j, \nu}
$$

with \(j=\mu^{\prime}-\nu, \cdots, \mu^{\prime} .\left\{l_{j, \nu}\right\}\) and \(\left\{r_{j, \nu}\right\}\) are those terms dependent on \(\alpha_{\mu-1,1}^{\prime}\) and \(\alpha_{\mu, 1}^{\prime}\) respectively. They are the elements of the alpha matrix rows \(\mu-k\) and \(\mu-k+2\) with \(\mathbf{A}_{\mu-k, j}=l_{j, \nu}\) and \(\mathbf{A}_{\mu-k+2, j}=r_{j, \nu}\) for \(j=\mu^{\prime}-\nu, \cdots, \mu^{\prime}\). We can generate the \(\left\{l_{j, \nu}\right\}\) by setting \(\alpha_{\mu^{\prime}-1,1}^{\prime}=1\) and \(\alpha_{\mu^{\prime}, 1}^{\prime}=0\) and likewise, generate \(\left\{r_{j, \nu}\right\}\) by setting \(\alpha_{\mu^{\prime}-1,1}^{\prime}=0\) and \(\alpha_{\mu^{\prime}, 1}^{\prime}=1\). Thus, \(\mathbf{A}_{\mu-k, j}\) and \(\mathbf{A}_{\mu-k+2, j}\) can be generated in the course of generating \(\mathbf{A}_{\mu-k+1, j}\) at little additional expense. The procedure above generalizes easily to surfaces, allowing us to generate the desired rows of the refinement matrices \(\mathbf{A}_{\mathbf{u}}\) and \(\mathbf{A}_{\mathbf{v}}\). The refined mesh \(\mathbf{D}^{\omega}\) is derived from the existing mesh \(\mathbf{P}^{\mathbf{w}}\) by:

$$
\mathbf{D}^{\omega}=\mathbf{A}_{\mathbf{u}} \mathbf{P}^{\mathbf{w}} \mathbf{A}_{\mathbf{v}}^{\mathbf{T}} .
$$

To produce the desired points we only need to evaluate

$$
\begin{aligned} & \left(\begin{array}{ll} \mathbf{D}_{\mu_{\mathbf{u}}}^{\omega}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1} & \mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{1}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{2}}^{\omega} \\ \mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{2}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{1}}^{\omega} & \mathbf{D}_{\mu_{\mathbf{u}}-\mathbf{k}_{\mathbf{u}}+\mathbf{2}, \mu_{\mathbf{v}}-\mathbf{k}_{\mathbf{v}}+\mathbf{2}}^{\omega} \end{array}\right)= \\ & \binom{\left(\mathbf{A}_{\mathbf{u}}\right)_{\mu_{u}+k_{u}+1,\left[\mu_{u}^{\prime}-\nu_{u} \ldots \mu_{u}^{\prime}\right]}^{\omega}}{\left(\mathbf{A}_{\mathbf{u}}\right)_{\mu_{u}+k_{u}+2,\left[\mu_{u}^{\prime}-\nu_{u} \ldots \mu_{u}^{\prime}\right]}^{\omega}} \mathbf{P}_{\left[\mu_{\mathbf{u}}^{\prime}-\nu_{\mathbf{u}} \ldots \mu_{\mathbf{u}}^{\prime}\right]\left[\mu_{\mathbf{v}}^{\prime}-\nu_{\mathbf{v}} \ldots \mu_{\mathbf{v}}^{\prime}\right]}\binom{\left(\mathbf{A}_{\mathbf{v}}\right)_{\mu_{v}+k_{v}+1,\left[\mu_{v}^{\prime}-\nu_{v} \ldots \mu_{v}^{\prime}\right]}}{\left(\mathbf{A}_{\mathbf{v}}\right)_{\mu_{v}+k_{v}+2,\left[\mu_{v}^{\prime}-\nu_{v} \ldots \mu_{v}^{\prime}\right]}}^{T} \end{aligned}
$$

This can be made quite efficient. We have been able to calculate approximately 150K surface evaluations (with derivative) per second on a 300MHz MIPS R12K using this approach.

## F u and Fvarethe vectors

$$
\begin{aligned} & \mathbf{F}_{\mathbf{u}}=\binom{\mathbf{N}_{\mathbf{1}} \cdot \mathbf{S}_{\mathbf{u}}(u, v)}{\mathbf{N}_{\mathbf{2}} \cdot \mathbf{S}_{\mathbf{u}}(u, v)} \\ & \mathbf{F}_{\mathbf{v}}=\binom{\mathbf{N}_{\mathbf{1}} \cdot \mathbf{S}_{\mathbf{v}}(u, v)}{\mathbf{N}_{\mathbf{2}} \cdot \mathbf{S}_{\mathbf{v}}(u, v)} . \end{aligned}
$$

The inverse of the Jacobian is calculated using a result from linear algebra:

$$
\mathbf{J}^{-1}=\frac{\operatorname{adj}(\mathbf{J})}{\operatorname{det}(\mathbf{J})}
$$

$$
The adjoint \(\operatorname{adj}(\mathbf{J})\) is equal to the transpose of the cofactor matrix
$$

$$
\mathbf{C}=\left(\begin{array}{ll} C_{11} & C_{12} \\ C_{21} & C_{22} \end{array}\right)
$$

where \(\mathbf{C}_{i_{j}}=(-1)^{i+j} \operatorname{det}\left(\mathbf{J}_{i_{j}}\right)\) and \(\mathbf{J}_{i_{j}}\) is the submatrix of \(\mathbf{J}\) which remains when the \(i\) th row and \(j\) th column are removed. We find that

$$
\operatorname{adj}(\mathbf{J})=\left(\begin{array}{cc} \mathbf{J}_{22} & -\mathbf{J}_{12} \\ -\mathbf{J}_{21} & \mathbf{J}_{11} \end{array}\right)
$$

We use four criteria, drawn from Yang [28], to decide when to terminate the Newton iteration. The first condition is our success criterion: if we are closer to the root than some predetermined glyph[epsilon1]

$$
\left\|\mathbf{F}\left(u_{n}, v_{n}\right)\right\|<\epsilon
$$

then we report a hit. Otherwise, we continue the iteration. The other three criteria are failure criteria, meaning that if they are met, we terminate the iteration and report a miss. We do not allow the new ( \(u_{*}, v_{*}\) ) estimate to take us farther from the root than the previous one:

$$
\left\|\mathbf{F}\left(u_{n+1}, v_{n+1}\right)\right\|>\left\|\mathbf{F}\left(u_{n}, v_{n}\right)\right\| .
$$

We also do not allow the iteration to take us outside the parametric domain of the surface:

$$
u \notin\left[u_{k_{u}-1}, u_{N}\right), v \notin\left[v_{k_{v}-1}, v_{M}\right)
$$

We limit the number of iterations allowed for convergence:

$$
\text { iter }>\text { MAXITER. }
$$

We set MAXITER around 7, but the average number of iterations needed to produce convergence is 2 or 3 in practice.

A final check is made to assure that the Jacobian \(\mathbf{J}\) is not singular. While this would seem to be a rare occurrence in theory, we have encountered this problem in practice. In the situation where \(\mathbf{J}\left(u_{k}, v_{k}\right)\) is singular, either the surface is not regular

$$
|\operatorname{det}(\mathbf{J})|<\epsilon
$$

If the Jacobian is singular we perform a jittered perturbation of the parametric evaluation point,

$$
\binom{u_{k+1}}{v_{k+1}}=\binom{u_{k}}{v_{k}}+.1 *\binom{\operatorname{drand} 48() *\left(u_{0}-u_{k}\right)}{\operatorname{drand} 48() *\left(v_{0}-v_{k}\right)}
$$

and initiate the next iteration. This operation tends to push the iteration away from problem regions without leaving the basin of convergence.

$$
\begin{aligned} N_{\mu-1,2}\left(t_{*}\right) & =\frac{t_{*}-t_{\mu-1}}{t_{\mu+k-2}-t_{\mu-1}} N_{\mu-1,1}\left(t_{*}\right)+\frac{t_{\mu+k-1}-t_{*}}{t_{\mu+k-1}-t_{\mu}} N_{\mu, 1}\left(t_{*}\right) \\ & =0 * 0+1 * 1 \\ & =1 \end{aligned}
$$

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-3-p008.png)

*Figure 3: Failure to adjust tolerances may result in surface acne.*

$$
t=(\mathbf{P}-\mathbf{o}) \cdot \hat{\mathbf{d}} .
$$

The approximate nature of the convergence also impacts other parts of the ray tracing system. Often, a tolerance glyph[epsilon1] is defined to determine the minimum distance a ray can travel before reporting an intersection. This prevents self-intersections due to errors in numerical calculation. The potential for error is larger in the case of numerical spline intersection than, say, raypolygon intersection. Thus, the tolerances will need to be adjusted accordingly. Failure to make this adjustment will result in 'surface acne' [9] (see Figure 3).

An enhanced method for abating acne would test the normal at points less than \(\epsilon\) along the ray to determine whether these points were on the originating surface. Unfortunately, we have found that we cannot rely on modeling programs to produce consistently oriented surfaces. Therefore, our system utilizes the coarser \(\epsilon\) condition above.

## 3 Trimming Curves

Trimming curves are a common method for overcoming the topologically rectangular limitations of NURBS surfaces. They result typically when designers wish to remove sections from models which are not aligned with the underlying parameterization. In this section, we will define what we mean by trimming curves.

A trimming curve is a closed, oriented curve which lies on a NURBS surface. For our purposes, the curve will consist of piecewise linear segments in parametric space \(\left\{\mathbf{p}_{\mathbf{i}}=\left(u_{i}, v_{i}\right)\right\}\). (In principle, there is no reason one could not extend our

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-6-p012.png)

*Figure 6: Invalid trimming curves: a curve which is not closed, curves which cross, and curves with conﬂicting orientation. conflicting orientation.*

We calculate the orientation of the curve using the method of Rokne [23] for computing the area of a polygon. Given parametric points { p i = (\(u_{i}\), \(v_{i}\)), i = 0. . . n, the signed area can be computed by

$$
A=\frac{1}{2} \sum_{i=0}^{n} u_{i} v_{(i+1) \bmod n}-u_{(i+1) \bmod n} v_{i} .
$$

If A is negative, the curve has a clockwise orientation. Otherwise, the orientation is counter-clockwise.

The orientation of a trimming curve determines which region of the surface is to be kept. We use the convention that the part of the surface to be kept is on the right side of the curve [as you walk in the direction of its orientation]. Inconsistencies in orientation that would result in an ambiguous determination of whether to trim are not allowed (see Figure 6).

An important characteristic of the trimming curves we use is that they are not allowed to cross. Trimming curves can contain trimming curves, and can share vertices and edges. Areas inscribed by counter-clockwise curves are often termed 'holes', while those inscribed by clockwise curves are termed 'regions.'

### 3.1 Building a Hierarchy

Since the curves are not allowed to cross, there are only three possible relationships between two curves \(\mathbf{c}_{\boldsymbol{1}}\) and \(\mathbf{c}_{\boldsymbol{2}}\). \(\mathbf{c}_{\boldsymbol{1}}\) can contain \(\mathbf{c}_{\mathbf{2}}\), be contained in \(\mathbf{c}_{\mathbf{2}}\), or share no regions in common with \(\mathbf{c}_{\mathbf{2}}\). Each node in our hierarchy is a list of trims, and each trim can refer to yet another list of trims which fall inside of it. Building the hierarchy proceeds as:

Insert (Trim newtrim, TrimList tl) for each Trim t in TrimList tl do if t contains newtrim then Insert (newtrim, t.trimlist) return else if newtrim contains t then Insert(t,newtrim.trimlist) Remove(t,tl) end if end if end for tl.Add(newtrim) The contains function for trims needs a bit of clarification. Since trims can share edges and vertices, proper containment tests-those that test only the vertices-will not always work. Instead we perform inside/outside tests on the midpoints of each trim segment. In comparing \(\mathbf{c}_{\mathbf{1}}\) and \(\mathbf{c}_{\mathbf{2}}, \mathbf{c}_{\mathbf{1}}\) is judged to be contained in \(\mathbf{c}_{\mathbf{2}}\) if and only if the midpoint of some segment of \(\mathbf{c}_{\mathbf{1}}\) falls inside \(\mathbf{c}_{\mathbf{2}}\). Since curves cannot cross, any such midpoint will do. The inside/outside test is performed with regard to some \(\epsilon\) so as to counteract round-off error.

For each trim curve, and for each trim list, we store a bounding box which we will use to speed culling in the following ray tracing step.

Once the trim hierarchy is created, we perform a quick pass through the surface patches, removing those patches which are completely trimmed away. This is an optimization step which reduces the size of the BVH and the number of patches which must be examined by the intersection routines. The procedure below can be used by encoding the parametric boundary of the patch to be tested as the trimming curve crv.

![Figure 7](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-7-p013.png)

*Figure 7: A set of trimming curves and the resulting hierarchy.*

IsTrimmed(TrimList tl, Trim crv) for each Trim t in TrimList tl do if t contains crv then return IsTrimmed(t.tl, crv) else if t crosses crv then return false end if end if end for return !tl.is clockwise

### 3.2 Ray Tracing Trimmed NURBS

We ray trace trimmed NURBS by first performing ray intersection with the untrimmed surface. If an intersection point ( \(u_{*}, v_{*}\) ) is found, we then look to the trim hierarchy to determine whether it is to be culled or returned as a hit.

Inside(point p, TrimList tl, boolean& keep)

```text
keep = !tl.is clockwise if tl.boundingbox contains p then for each Trim t in TrimList tl do if t.boundingbox contains p then if t contains p then Inside(p,t.tl,keep) return end if end if end for end if
```

Because ambiguous orientations are not allowed, trims at the same level of the hierarchy will have the same orientation. This orientation is referenced above as tl.is clockwise. The variable keep determines whether the point should be culled.

## 4 Results

We have generated some images (see Figures 9 and 10) and timings for data sets rendered using our technique. All timings are for a single 300MHz R12K MIPS processor with an image resolution of 512x512. All models were Phong shaded and timings include shadow rays.

Wehave implemented our method in a parallel ray tracing system, and have obtained interactive rates with scenes of moderate geometric complexity. For a discussion of that system, we refer the reader to Parker et al. [18].

Source code and other material related to the system which we have described can be found online at http: www.acm.org jgt papers MartinEtAl00.

## Acknowledgments

Thanks to Michael Stark for substantial help analyzing the numerical properties of the algorithm. Thanks also to Brian Smits for helpful discussions, feedback, and encouragement, to Steve Parker for invaluable aid with parallelization and some of the nastier debugging, and to Amy Gooch for comments on the final draft. This work was supported in part by NSF grant 9720192 (CISE New Technologies), DARPA grant F33615-96-C-5621, and the NSF Science and Technology Center for Computer Graphics and Scientific Visualization (ASC-89-20219). All opinions, findings, conclusions or recommendations expressed in this document are those of the authors and do not necessarily reflect the views of the sponsoring agencies.

![Figure 8](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-8-p015.png)

*Figure 8: Statistics for our technique. “Light BV intersections” are generated by casting shadow rays and are treated (and measured) separately from ordinary BV intersections. “NURBS tests” gives the number of numerical NURBS surface intersections performed. “Total NURBS time”and “Avg time per NURBS” give the total and mean time spent on numerical surface intersections, respectively. “NURBS hits” denotes the number of numerical intersections which yielded a hit. “Reported hits” gives the number of successful numerical hits which were not eliminated by trimming curves or by comparison with the previous closest hit along the ray.*

![Figure 9](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-9-p016.png)

*Figure 9: A scene containing NURBS primitives. All of the objects on the table are spline models which have been ray traced using the method presented in this paper.*

![Figure 10](/Users/evanthayer/Projects/paperx/docs/2000_practical_ray_tracing_trimmed_nurbs_surfaces/figures/figure-10-p016.png)

*Figure 10: Mechanical parts produced by the Alpha 1 [11] modeling system (crank, Crank1A, and allblade).*

## References

- Salim S. Abi-Ezzi and Srikanth Subramaniam. Fast dynamic tessellation of trimmed NURBS surfaces. In Eurographics '94, 1994.

- Richard H. Bartels, John C. Beatty, and Brian A. Barsky. An introduction to splines for use in computer graphics and geometric modeling. Morgan Kauffman Publishers, Inc., Los Altos, CA, 1987.

- W. Barth and W. St¨ urzlinger. efficient ray tracing for B´ ezier and B-spline surfaces. Computers and Graphics, 17(4), 1993.

- W. Boehm. Inserting new knots into B-spline curves. Computer-Aided Design, 12:199-201, July 1980.

- Swen Campagna, Philipp Slusallek, and Hans-Peter Seidel. Ray tracing of spline surfaces: B´ ezier clipping, Chebyshev boxing, and bounding volume hierarchy-a critical comparison with new results. Technical report, University of Erlangen, IMMD IX, Computer Graphics Group, Am Weichselgarten 9, D-91058 Erlangen, Germany, October 1996.

- E. Cohen, T. Lyche, and R. Riesenfeld. Discrete B-splines and subdivision techniques in computer-aided geometric design and computer graphics. Comput. Gr. Image Process., 14:87-111, October 1980.

- Gerald E. Farin. curves and surfaces for computer aided geometric design: a practical guide, 4th ed. Academic Press, Inc., San Diego, CA, 1996.

- Alain Fournier and John Buchanan. Chebyshev polynomials for boxing and intersections of parametric curves and surfaces. In Eurographics '94, 1994.

- Andrew Glassner, ed. An introduction to ray tracing. 1989.

- Josef Hoschek and Dieter Lasser. Fundamentals of computer aided geometric design. A.K. Peters, Wellesley, MA, 1993.

- Integrated Graphics Modeling Design and Manufacturing Research Group. Alpha1 geometric modeling system, user's manual. Department of Computer Science, University of Utah.

- James T. Kajiya. Ray tracing parametric patches. Computer Graphics (SIGGRAPH '82 Proceedings), 16(3):245-254, July 1982.

- Subodh Kumar, Dinesh Manocha, and Anselmo Lastra. Interactive display of large NURBS models. IEEE Transactions on Visualization and Computer Graphics, 2(4), December 1996.

- Daniel Lischinski and Jakob Gonczarowski. Improved techniques for ray tracing parametric surfaces. The Visual Computer, 6(3):134-152, June 1990. ISSN 0178-2789.

- William L. Luken and Fuhua (Frank) Cheng. Comparison of surface and derivative evaluation methods for the rendering of NURB surfaces. ACM Transactions on Graphics, 15(2):153-178, April 1996. ISSN 0730-0301.

- T. Lyche, E. Cohen, and K. Morken. Knot line refinement algorithms for tensor product B-spline surfaces. Computer Aided Geometric Design, 2(1-3):133-139, 1985.

- Tomoyuki Nishita, Thomas W. Sederberg, and Masanori Kakimoto. Ray tracing trimmed rational surface patches. In SIGGRAPH '90, 1990.

- Steven Parker, William Martin, Peter-Pike J. Sloan, Peter Shirley, Brian Smits, and Charles Hansen. Interactive ray tracing. 1999 ACM Symposium on Interactive 3D Graphics, pages 119-126, April 1999. ISBN 1-58113-082-1.

- John W. Peterson. Tessellation of NURBS surfaces. In Paul Heckbert, editor, Graphics Gems IV, pages 286-320. Academic Press, Boston, 1994.

- Les A. Piegl and W. Tiller. The NURBS Book. Springer Verlag, New York, NY, 1997.

- William H. Press, Saul A. Teukolsky, William T. Vetterling, and Brian P. Flannery. Numerical recipes in C: The art of scientific computing (2nd ed.). 1992. ISBN 0-521-43108-5. Held in Cambridge.

- Alyn Rockwood, Kurt Heaton, and Tom Davis. Real-time rendering of trimmed surfaces. In SIGGRAPH '89, 1989.

- Jon Rokne. The area of a simple polygon. In James R. Arvo, editor, Graphics Gems II. Academic Press, 1991.

- Brian Smits. Efficiency issues for ray tracing. Journal of Graphics Tools, 3(2):1-14, 1998. ISSN 1086-7651.

- Michael A.J. Sweeney and Richard H. Bartels. Ray tracing free-form B-spline surfaces. IEEE Computer Graphics & Applications, 6(2), February 1986.

- Thomas V. Thompson II and Elaine Cohen. Direct haptic rendering of complex NURBS models. In Proceedings of Symposium on Haptic Interfaces, 1999.

- Daniel L. Toth. On ray tracing parametric surfaces. Computer Graphics (Proceedings of SIGGRAPH 85), 19(3):171-179, July 1985. Held in San Francisco, California.

- Chang-Gui Yang. On speeding up ray tracing of B-spline surfaces. Computer Aided Design, 19(3), April 1987.
