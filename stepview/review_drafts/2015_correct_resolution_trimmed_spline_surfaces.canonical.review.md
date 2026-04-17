# Correct Resolution Rendering of Trimmed Spline Surfaces

Ruijin Wu, Jorg Peters

[missing from original]

## Abstract

visual artifacts. This paper presents a new approach to rendering trimmed spline surfaces that guarantees visual accuracy efficiently, even under interactive adjustment of trim curves and spline surfaces. The technique achieves robustness and speed by discretizing on the CPU and transfer it to the GPU. This process interrupts the design process and can yield unsatisfactory results as closeups reveal a jagged or otherwise incorrect approximation. Conversely, an overly fine triangulation wastes resources: there is no need to highly resolve a complex trim curve when the corresponding surface measures only a few pixels on the screen.

## 1 Introduction

A standard approach to designing geometry in computer aided design, is to 'overfit', i.e. create spline surfaces that are larger than needed and subsequently trim the surfaces back to match functional constraints or join to other surfaces (see Fig. 1). This approach persists both for historical reasons and for design simplicity: for historical reasons in that overfitting and trimming pre-dates alternative approaches such as subdivision surfaces [1, 2] and finite geometrically-smooth patch complexes (see e.g. [3, 4]); for practical reasons, in that it is often more convenient to control the shape of a signature piece in isolation than when constraints have to be taken into consideration. For example, a car's dashboard can be prepared in one piece without consideration of cut-outs for instrumentation and the steering column.

The prevailing practice in computer aided design environments is to generate and display a fixed-resolution triangulation

Correct resolution rendering of trimmed spline surfaces

$$
Ruijin Wu \({ }^{\mathrm{a}}\), Jorg Peters \({ }^{\mathrm{a}}\)
$$

on the CPU and transfer it to the GPU. This process interrupts the design process and can yield unsatisfactory results as closeups reveal a jagged or otherwise incorrect approximation. Conversely, an overly fine triangulation wastes resources: there is no need to highly resolve a complex trim curve when the corresponding surface measures only a few pixels on the screen.

The computer graphics community has developed a number of clever techniques, reviewed in Section 2, to deliver real-time display of trimmed spline surfaces. The present paper advances the state-of-the-art by carefully predicting how fine an evaluation of the trim curves results in correct trim decisions at screen resolution. This tight prediction makes it possible to construct, as a prelude to each modified view or model rendering pass, a slim and adaptive trim-query acceleration table that supports a light-weight per-fragment trim test. This simple add-on to any rendering pass is efficient enough to allow interactive trimcurve editing.

Overview. Section 2 reviews existing techniques for fast rendering of trimmed spline surfaces. Section 3 reviews basic concepts and establishes notation. Section 4 explains how correct resolution can be determined. Section 5 explains how to build and use the trim-query acceleration table. Section 6 measures the performance of a full implementation.

## 2 Real-time rendering of trimmed surfaces and related techniques

The trim decision is to determine to which side, of a set of trim curves, lies the \(u_{v}\)-pre-image of a pixel. The underlying challenge is the same as when determining the fill region of a planar decal [5] - except that in planar filling, the accuracy of rendering is measured in the \(u_{v}\)-plane, while for trimmed surfaces, the accuracy is measured in screen space, i.e. after applying the non-linear surface map followed by projection onto the screen.

A straightforward approach, used in 2D vector graphics [6, Sec 8.7], is to ray-test : each pixel's uv-pre-image in the domain sends a ray to the domain boundary to determine the number of intersections (and possibly the intersection curve orientation). The intersections decide whether the fragment is to be discarded. For example, Pabst et al. [7] test scan-line curve intersection directly in the Fragment Shader. Direct testing without an acceleration structure is impractical since the number and complexity of intersections can be unpredictably high so that robustness and accuracy are difficult to assure within a fixed time. It pays to pre-process the trim curves and map them into a hierarchical search structure in order to localize testing to a single trim curve segment. For example, Schollmeyer et al. [8] break the segments into monotone pieces and test scanline curve intersection in the Fragment Shader by robust binary search. This pre-processing is view-point independent but becomes expensive for interactive trim-curve manipulation.

Another pre-processing choice is to convert the piecewise rational trim curves into an implicit representation, via resultants (see e.g. [10, 11, 12]). Evaluating the resultant will generate a signed number and the sign can be used to determine whether a pixel is to be trimmed. In principle, this yields unlimited accuracy. However, there are several caveats to this approach. first, the use of resultants increases the degree and number of variables. The coefficients of the implicit representation are typically complicated expressions in terms of the coefficients of the trim curve segments. Therefore the evaluation in the Fragment Shader can be expensive even if the derivation of the implicit expression is done off-line prior to rendering. There are more efficient approaches than full implicitization, e.g. [13]. While useful for ray-tracing, these expressions do not presently yield a signed test as required for trimming. Second, implicitization converts the entire rational curve, not just the required rational piece. Use of resultants therefore requires a careful restriction of the test region, for example by isolating bounding triangles in the domain that contain a single indicator function whose zero level set represents the trim. Determining such restrictions is in general tricky since the implicit can have extraneous branches. For conics, the conversion expressions are sufficiently simple and for fixed shapes, such as fonts, determining bounding triangles can be done offline once and for all [14]. For less static scenarios, also pre-processing of conics and triangulation of the domain is not easily parallelized. Stencil buffers can avoid careful triangulation [5] but the fixed resolution inherits the challenges of texture-based trimming.

Computing the trim curves from CSG operations addresses a related but somewhat different problem than rendering. Here the trim curves (exact intersection pre-images) are not given. For simple CSG primitives such as quadrics the render decision can be based on an implicit in out test. For more complex B-reps, faceted models are compared and proper resolution of the B-rep into facets remains a challenge. Practical implementations use stencil operations, depth and occlusion testing [15, 16].

![Figure 2](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-2-p002.png)

*Figure 2: Correct resolution real-time rendering of trimmed spline surfaces.*

## 3 Definitions and Concepts

Coordinates and Projection. In the OpenGL graphics pipeline [17, Sec 13.6], the non-orthogonal projection P

$$
\left(\begin{array}{l} x \\ y \\ z \\ 1 \end{array}\right) \rightarrow\left(\begin{array}{l} x_{c} \\ y_{c} \\ z_{c} \\ w_{c} \end{array}\right):=\left(\begin{array}{cccc} P_{11} & 0 & 0 & 0 \\ 0 & P_{22} & 0 & 0 \\ 0 & 0 & P_{33} & P_{34} \\ 0 & 0 & -1 & 0 \end{array}\right)\left(\begin{array}{l} x \\ y \\ z \\ 1 \end{array}\right)
$$

maps camera coordinates \((x, y, z, 1)^{T}\) with the camera is at the origin pointing in the negative \(z\)-direction, to clip coordinates \(\left(x_{c}, y_{c}, z_{c}, w_{c}\right)^{T}\). The entries \(P_{33}:=(\bar{z}-\underline{z}) /(\bar{z}+\underline{z})\) and \(P_{34}:=\) \(2 \bar{z} \underline{z} /(\underline{z}-\bar{z})\) define two planes at depth \(\underline{z}\) (near) and \(\bar{z}\) (far) such that any geometry with depth outside the range \([\underline{z}, \bar{z}]\) is clipped. Perspective division converts the clip coordinates into normalized device coordinates \(\left(x_{d}, y_{d}, z_{d}\right):=\left(x_{c}, y_{c}, z_{c}\right) / w_{c}\), and the viewport transformation converts normalized device coordinates to screen coordinates: \((\tilde{\mathrm{x}}, \tilde{\mathrm{y}}):=\left(W x_{d} / 2+O_{x}, H y_{d} / 2+\right.\) \(\left.O_{y}\right)\). Here \(W\) and \(H\) are the width, respectively height of the viewport in pixels and \(O_{x}\) and \(O_{y}\) are the screen space coordinates of the viewport center, typically \(O_{x}=W / 2, O_{y}=H / 2\). Together, the projection from \(\mathbb{R}^{3}\) to the rasterized screen is

Surfaces and trim curves. Models consist of rational parametric surfaces

$$
\mathbf{x}: U \subsetneq \mathbb{R}^{2} \rightarrow \mathbb{R}^{3} \quad(u, v) \rightarrow \mathbf{x}(u, v):=\left(\begin{array}{l} x(u, v) \\ y(u, v) \\ z(u, v) \end{array}\right)
$$

defined on a domain \(U\). Often \(U:=[0. .1]^{2}\), the unit square, and the surface (patch) is in tensor-product form with basis functions \(b_{k}\),

$$
\mathbf{x}(u, v):=\sum_{i} \sum_{j} \mathbf{c}_{i j} b_{i}(u) b_{j}(v) .
$$

To trim a patch means to restrict its domain to one side of a piecewise rational trim curve

There can be multiple trim curves per patch. When trim curves are nested, their orientation can be used to determine which side is trimmed away. A simplified convention applies an alternating count from a domain boundary.

Trim curves are often rational approximations \(\gamma_{1}(t), \gamma_{2}(t)\) to the solutions of the surface-surface intersection (SSI) problem, \(\mathbf{x}_{1}\left(u_{1}, v_{1}\right)=\mathbf{x}_{2}\left(u_{2}, v_{2}\right) \in \mathbb{R}^{3}\). We are not concerned with solving such potentially hard SSI systems of 3 equations in 4 unknowns, whose solution is generically a pair of non-rational algebraic curves. Rather we assume the trim curves are given as rational curves and address the challenge of efficient accurate display of the resulting trimmed surface.

$$
V_{i}:=\left\{(u, v) \in U, \quad \nu_{i} \leq v<\nu_{i+1}\right\} .
$$

Trim curves can also be artist-defined or they can reference planar shapes. Such shapes, for example fonts, are mapped to the surface reshaped by the curvature of the map \(\mathbf{x}\).

Faithful surface tessellation. Ray-casting guarantees that each pixel represents a correctly-placed surface piece and finds each pixel's \(u_{v}\)-pre-image. Remarkably, such pixel-accurate rendering can also be achieved using the highly efficient standard graphics pipeline. In [18], a compute shader determines a nearoptimal (minimal) tessellation factor \(\tau\) for each patch \(\mathbf{x}\), so that evaluating \(\mathbf{x}\) on a \(\tau \times \tau\) partition of its domain \(U\) yields a proxy triangulation \(\hat{\mathbf{x}} \in \mathbb{R}^{3}\) of \(\mathbf{x}\) such that its image under the screen projection \(P\) of (1) agrees with that of the correct image. That is the difference \(\mathrm{Px}(\mathrm{u})-\mathrm{P} \hat{\mathbf{x}}(\mathrm{u})\) is below the visible pixel threshold. We call \(\hat{\mathbf{x}}\) a faithful triangulation of \(\mathbf{x}\) and will use \(\hat{\mathbf{x}}\) to render the trimmed surfaces.

$$
|\tilde{\mathbf{x}}(u, v)-\tilde{\mathbf{x}}(u, v+h)|=h\left|\tilde{\mathbf{x}}_{v}\left(u, v^{*}\right)\right|, \quad \tilde{\mathbf{x}}_{v}:=\frac{\partial \tilde{\mathbf{x}}}{\partial v}
$$

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-3-p003.png)

*Figure 3: Choosing a correct domain partition into uv-cells. i.e. sufﬁciently ﬁne so that no two pixels’ uv-pre-images share one uv-cell. sufficiently fine so that no two pixels' uv-pre-images share one uv-cell.*

$$
\begin{aligned} & \mathrm{P}: \mathbb{R}^{3} \rightarrow \mathbb{R}^{2} \quad w_{x}:=\frac{P_{11} W}{2}, w_{y}:=\frac{P_{22} H}{2} \\ & (x, y, z) \rightarrow(\tilde{\mathrm{x}}, \tilde{\mathrm{y}}):=\left(w_{x} \frac{x}{z}+c_{x}, w_{y} \frac{y}{z}+c_{y}\right) \end{aligned}
$$

## 4 Predicting correct resolution

Since any screen has a fixed discrete resolution, trimmed surfaces can and need only be resolved up to pixel width (subpixel width in the case of subsampling for anti-aliasing). Our approach is to pull back the pixel-grid to the domain \(U\) and partition \(U\) into \(u_{v}\)-cells-in such a way that no two pixels' \(u_{v}\)-pre-images share one \(u_{v}\)-cell (cf. Fig. 3). This guarantees each pixel, in particular of a group straddling the projection of a surface trim, its individual trim test. Next we evaluate the trim curve in the domain \(U\) so that the resulting broken line differs from the exact trim curve by less than one \(u_{v}\)-cell. The two discretizations, of the domain \(U\) and of the curve \(\gamma\), provide a consistent, correct resolution in the sense that testing the \(u_{v}\) - pre-image of a pixel ( \(\tilde{\mathrm{x}}_{i}, \tilde{\mathrm{y}}_{i}\) ) against the broken line yields a correct trim decision up to pixel resolution.

For a non-linear surface \(\mathbf{x}\) followed by a perspective projection P, pulling the pixel-grid back exactly is not practical since the Jacobian of Px can vary strongly. Multi-resolution can accommodate adaptively scaled \(u_{v}\)-cells, but a complex hierarchical lookup slows down each fragment's trim test. We therefore opt for a simple two-level hierarchy. At the first level, we partition the domain \(U\) into \(n_{V} v\)-strips \(V_{i}\) :

$$
\gamma: T \subsetneq \mathbb{R} \rightarrow U \quad t \rightarrow \gamma(t):=(u(t), v(t)) .
$$

Each v-strip is a 'fat scan-line' where the u-coordinate is free while the v-coordinate is sandwiched between an upper and a lower bound. The default choice is to space the \(v_{i}\) uniformly and set n V = τ , where τ is the surface tessellation factor already computed according to [18]. At the second level, each v-strip V i is uniformly partitioned once more in the v-direction into a minimal number µ i of v-scan lines that guarantees correct trim resolution (see Fig. 4). To determine the critical number µ i that guarantees that the distance between the screen images of two v-scan lines is less than one pixel, we proceed as follows. By the mean value theorem, for some v ∗ ∈ [v, v + h] ,

If, for all \(v \in V_{i}\) and the \(v\)-scan line-spacing \(h>0\),

$$
\begin{aligned} h \rho_{i}(v) & <1, \quad v \in\left[\nu_{i} . \nu_{i+1}\right] \\ \rho_{i}(v) & :=\max \left\{\sup _{u}\left|\tilde{\mathrm{x}}_{v}(u, v)\right|, \sup _{u}\left|\tilde{\mathrm{y}}_{v}(u, v)\right|\right\} \end{aligned}
$$

then the \(\tilde{\mathrm{x}}\)-distance between the screen images of the two \(v\)-scan lines \(\tilde{\mathrm{x}}\left(u, v_{j}\right)\) and \(\tilde{\mathrm{x}}\left(u, v_{j}+h\right)\) is less than a pixel and so is the

(a) Trim curve in uv space and v-scan line intersections for two v-strips

![Figure 4](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-4-p004.png)

*Figure 4: Construction and testing of the u-intercept table. (b) Two v-strips V 1 and V 2 partitioned into µ 1 = 4 and µ 2 = 12 v-scan lines respectively. (c) The ← and ↓ indicate the v-scan line and the relative u coordinate of x in the u-intercept table. (d) In the absence of orientation information, the parity of the table entry just smaller than u decides the trim-query. (d) Trimmed region (red) on patch at correct resolution.*

$$
\mu_{i}:=\left\lceil\left(\nu_{i+1}-\nu_{i}\right) \sup _{v \in\left[\nu_{i} . . \nu_{i+1}\right]} \rho_{i}(v)\right\rceil
$$

$$
\left(\nu_{i+1}-\nu_{i}\right) \max _{\triangle} \rho_{\triangle}, \quad \triangle \cap V_{i} \neq \emptyset,
$$

guarantees correct resolution. Fig. 5a shows an artifact when \(\mu_{i}\) is chosen too small. Fig. 5c shows the correct and near-minimal choice. If the projection is orthographic and the surface is a faithful triangulation then \(\mu_{i}\) is simply the maximum size of the \(\tilde{\mathrm{x}}\) and the \(\tilde{\mathrm{y}}\) projection of the strip in pixels.

$$
\rho_{\alpha}:=\max \left\{\left|\tilde{\mathrm{x}}_{v}\left(u_{\alpha}, v_{\alpha}\right)\right|,\left|\tilde{\mathrm{y}}_{v}\left(u_{\alpha}, v_{\alpha}\right)\right|\right\}
$$

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-5-p004.png)

*Figure 5: Render quality affected by scan density (jaggies in (a)) and curve tessellation level (corners (b)). Figures are enlarged. (a) insufficient scan resolution µ i (b) insufficient curve tessellation (c) correct resolution*

Since for any reasonable view the near-plane of the scene is at some minimal distance to the viewer, i.e. \(z \geq\) \(\underline{z}>0\), the expansion

$$
\tilde{\mathrm{x}}_{v}=\tilde{\mathrm{x}}_{x} x_{v}+\tilde{\mathrm{x}}_{y} y_{v}+\tilde{\mathrm{x}}_{z} z_{v}=\frac{w_{x}}{z}\left(x_{v}-\frac{x}{z} z_{v}\right)
$$

is well-defined, although potentially large for small \(z\). For our (faithfully) triangulated surface, \(x\) and \(z\) are piecewise linear maps and \(x_{v}\) and \(z_{v}\) are piecewise constant. Determining an upper bound on \(\rho_{i}(v)\) over the three vertices \(\left(u_{k}, v_{k}\right), k=1,2,3\) of each triangle △,

$$
\rho_{\triangle}:=\max _{k}\left|\frac{1}{z}\right| \max _{k}\left|w_{x}\left(x_{v}-\frac{x}{z} z_{v}\right)\right|,
$$

$$
\operatorname{base}_{i}+j, \quad \operatorname{base}_{i}:=\sum_{k=1}^{i-1} \mu_{k}, \quad j:=\frac{v-\nu_{i}}{\nu_{i+1}-\nu_{i}} \mu_{i},
$$

typically yields a tight estimate. However, the estimate \(\rho_{\triangle}\) can include (parts of) triangles outside the viewing frustum so that, if a user zooms in and a part of a triangle approaches the camera, \(z\) can be arbitrarily small. Instead, using the pixel's \(u_{v}\)-preimage sent down through the graphics pipeline, we compute the analog of (8) for each pixel \(\alpha\) as

$$
\mu_{i}:=\left(\nu_{i+1}-\nu_{i}\right) \max _{\alpha} \rho_{\alpha}, \quad \alpha \in V_{i} .
$$

## 5 Filling and using the acceleration table

The overall algorithm is summarized as follows. Each trim curve writes itself, at the correct resolution (determined by the \(v\)-scan line density \(\mu_{i}\) defined in the previous section) into a slim \(u\)-intercept table. Each fragment then makes its trim decision by testing against the table entries.

Initializing the \(u\)-intercept table. The key data structure is the \(u\)-intercept table. There is one \(u\)-intercept table per sub-surface, e.g. a tensor-product spline patch complex with \(\ell_{u} \times \ell_{v}\) pieces. The \(u\)-intercept table is an array of size \(\mu \times n\) where \(\mu:=\sum_{i} \mu_{i}\) is the total number of \(v\)-scan lines and \(n\) is an upper bound on the number of trim curves that may cross a \(v\)-scan line of the surface piece. The row of the table with index

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-6-p005.png)

*Figure 6: Flowchart of the surface trimming add-on (light green) to pixel-accurate GPU rendering according to [18].*

will contain a sorted list of \(u\)-intercepts: the intersections of the (linear segments of the correctly tessellated) trim curves \(\gamma\) with the \(v\)-scan line \((u, v): v=\nu_{i}+\frac{j}{\mu_{i}}\left(\nu_{i+1}-\nu_{i}\right)\). Each \(v\)-strip The bounds of [19] could be leveraged, but since the Compute Shader already uses slefe-based bounds to generate the faithful triangulation \(\hat{\mathbf{x}}\) according to [18], we use the same estimators to determine the curve tessellation factor for correct resolution (as defined in Section 4). For the correct curve tessellation number, the Compute Shader threads calculate, for each trim curve segment \(k\) in parallel, the end points \(\gamma\left(t_{k-1}\right)\) and \(\gamma\left(t_{k}\right)\). Each thread then inserts the \(u\)-coordinates of all \(v\)-scan lineintersections with the trim curve segment into the \(u\)-intercept table. A second generation of threads subsequently sorts all trim curve intersections of a \(v\)-scan line by their \(u\)-coordinates.

Testing against the \(u\)-intercept table. To determine whether a fragment with pre-image ( \(u, v\) ) should be discarded, the Fragment Shader reads the row of the table determined from \(v\) by (11) and locates \(u\), by binary search in the table (see Fig. 4b). The complexity of the binary search is \(\log _{2} n\), i.e. 4 tests if the number of intercepts is \(n=16\). The Fragment Shader then

### 5.1 Implementation detail and optimization

Fig. 6 shows our mapping of accurate trim display onto the graphics pipeline. The main add-on is the Compute Shader pass, shown as the top row of the flowchart. The trim test is performed in the Fragment Shader. The Geometry Shader can be removed by adding its work to the Fragment Shader. Consistent intersections. Care has to be taken to avoid duplicate or missing intersections where the \(v\)-scan line intersects two consecutive trim curve segments at the common end point. If the \(v\)-scan line does not cross but just touches the two segments, either two or zero intersections should be recorded, not one. We achieve consistency by treating every segment as a bottom-open top-closed interval (see Fig. 7).

![Figure 7](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-7-p005.png)

*Figure 7: (a) Artifacts due to duplicated/missing intersections of curve segments that end at v-scan lines. (b) Choosing segments bottom-open top-closed prevents artifacts.*

Merging u-intercept tables. To minimize overhead in launching a compute shader and memory allocation we can and do

![Figure 8](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-8-p006.png)

*Figure 8: Trimmed B´ezier patches joining at a point. The part to be trimmed away is colored in red.*

Multi-sample anti-aliasing. (m-MSAA) improves silhouettes and (trim) boundaries by testing object coverage at m locations per pixel (compare Fig. 10a to Fig. 10b where m = 4). We add sub-pixel trim testing by decreasing the screen spacing of v-scan lines in (6) so that the trim has sub-pixel accuracy. The Fragment Shader then corrects the coverage mask according to the per sub-pixel trim test result (see Fig. 10c). The main cost of m-MSAA is in creating finer u-intercept tables, not in the Fragment Shader test.

![Figure 9](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-9-p006.png)

*Figure 9: Pixel-gap ﬁlling by drawing the patch trim boundary Pixel-gap filling by drawing the patch trim boundary*

![Figure 10](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-10-p006.png)

*Figure 10: Anti-aliasing for silhouettes and trim boundaries. The screen occupation is 100%. The images are cropped and scaled. In (b, bottom), standard 4xMSAA correctly antialiases the silhouette (corresponding to the green square in the overview image on top), but not the boundary of the circular hole (middle, red square). In (c), our method correctly antialiases both silhouettes and trims.*

Opportunistic optimization. Whenever the view is unchanged, neither the surface tessellation nor the u-intercept table need to be recomputed. Whenever the geometry is unchanged, neither the surface slefe-boxes of the pixel-accurate patch rendering nor the trim curve partition need to be recomputed.

## 6 Results

We implemented the trim-render add-on in the OpenGL 4.3 API and benchmarked the implementation on the CAD models in Fig. 11. To make the benchmark easily replicable, we fixed the number of \(v\)-strips per spline surface to 128 and packed their \(v\)-scan lines into \(u\)-intercept tables of 16384 rows. We allocated space so that each row can hold up to \(n=32\) intersections (but never encountered more than 8 intersections; see Fig. 12).

![Figure 11](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-11-p007.png)

*Figure 11: Two models built from trimmed surfaces.*

Table 1 breaks down the overall work and the work for maintaining the u-intercept table. To measure the maximally interactive case, we did not use opportunistic optimization. The full algorithm displayed by the flowchart of Fig. 6 was executed for each render pass. As observed in [8], a direct performance comparison to earlier implementations is challenging due to their implementation complexity and choice of scenes and textures. Moreover, recent advances in hardware acceleration, notably the introduction of the tessellation engine, have changed the bottlenecks when rendering spline surfaces. To nevertheless give an idea of the magnitude of acceleration, we note that none of the earlier trim-surface rendering algorithms promised interactive trim adjustment. We show the increased flexibility and speed of the trim-rendering add-on in the accompanying video, by demonstrating interactive trim modification.

![Figure 12](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-12-p007.png)

*Figure 12: Number of u-intercept table entries: green=1 to red=6.*

The GPU memory used by the add-on is that of the slim \(u\) - intercept table, set to \(2^{14}\) rows and \(2^{5}\) columns plus, for each surface piece consisting of many patches, \(2^{7} v\)-strip indices and the numbers \(\mu_{i}\). The graph in Fig. 13 compares GPU memory usage for different zoom levels and the Mini data set of the \(u\) - intercept table vs. texture-based trimming. (Identical trimming precision was enforced by setting the texture resolution to \(n_{V}\). \(\max _{i} \mu_{i}\).)

![Figure 13](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-13-p007.png)

*Figure 13: GPU memory usage for different zoom levels. Table 1: Break down of the rendering time for the models in Fig. 11. The timings were collected for an i5-2500 3.3GHz processor and a GTX 780 graphics card, for a screen resolution of 1000 × 1000.*

Performance under zoom and different resolution. Fig. 14 illustrates work distribution when zooming in. As the surface(s) fill more and more of the screen, the surface rendering time (red) dominates, while work for calculating the patch tessellation levels decreases since many patches are recognized to fall outside the viewing frustum by the algorithm of [18] and are discarded. Fig. 15 shows the increase in run time when the render window increases from \(400 \times 400\) to \(1200 \times 1200\). Since the patch-based work, for determining the tessellation factor that guarantees pixel-accuracy [18], stays constant, the proportional increase of work for drawing (pixel fill) and the trim test determine the overall cost.

![Figure 14](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-14-p008.png)

*Figure 14: Performance at different zoom levels.*

![Figure 15](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-15-p008.png)

*Figure 15: Performance at different screen resolution for model Fig. 11a.*

## 7 Discussion

As surveyed in Section 2, existing approaches to rendering trimmed spline surfaces require extensive pre-processing and re-approximation of the data or expensive off-line ray casting that interfere with the designer's work flow. Correct resolution rendering can give immediate and visually accurate feedback by discretizing at just the right level. A direct timing comparison with the implementations of [9], [7] and [8] is not possible since the GPU hardware has evolved; and meaningful comparison requires that all rendering be (sub-)pixel accurate. However timing comparisons are not crucial since a qualitative comparison already brings out the relative strengths. On one hand, the correct resolution approach avoids generating large trim textures that are a bottleneck in [9]. On the other hand, the trim test based on the \(u\)-intercept table is faster and more robust than retrieving and solving equations in [7]. And while approaches such as [8] leverage extensive pre-processing, the \(u\)-intercept table is built on the fly, enabling interactive trim adjustment. Accuracy via the simple \(u\)-intercept table data structure is made possible by tight estimates and the fact that the screen resolution is known at run time.

In terms of GPU usage, an important characteristic of correct resolution rendering is that the Fragment Shader does little extra work. This is important since rendering is typically Fragment Shader bound due to heavy use by expensive pixel shading operations.

![Figure 16](/Users/evanthayer/Projects/paperx/docs/2015_correct_resolution_trimmed_spline_surfaces/figures/figure-16-p008.png)

*Figure 16: Correct resolution real-time rendering of trimmed spline surfaces.*

Acknowledgements. Wethank Michael Guthe, Bernd Froehlich and Andre Schollmeyer for pointers to trimmed NURBS models and helpful comments concerning their algorithms. We thank GrabCad.com for providing models. This work was supported in part by NSF grant CCF-1117695.

## References

- [1] E. Catmull, J. Clark, Recursively generated B-spline surfaces on arbitrary topological meshes, Computer-Aided Design 10 (1978) 350-355.

- J. Peters, U. Reif, Subdivision Surfaces, Vol. 3 of Geometry and Computing, Springer-Verlag, New York, 2008.

- C. Loop, Second order smoothness over extraordinary vertices, in: R. Scopigno, D. Zorin (Eds.), Eurographics Symposium on Geometry Processing, Eurographics Association, Nice, France, 2004, pp. 169-178.

- K. Karˇ ciauskas, J. Peters, Rational bi-cubic G 2 splines for design with basic shapes, Computer Graphics Forum (SGP2011) 30 (5) (2011) 13891395.

- M. J. Kilgard, J. Bolz, GPU-accelerated path rendering, ACM Transactions on Graphics 31 (6) (2012) 1.

- D. Rice, R. J. Simpson, OpenVG specification version 1.1 (Dec. 2008).

- H.-F. Pabst, J. Springer, A. Schollmeyer, R. Lenhardt, C. Lessig, B. Froehlich, Ray casting of trimmed NURBS surfaces on the GPU, in: Interactive Ray Tracing 2006, IEEE Symposium on, 2006, pp. 151-160.

- A. Schollmeyer, B. Fr¨ ohlich, Direct trimming of NURBS surfaces on the GPU, ACM Transactions on Graphics 28 (3) (2009) 1.

- M. Guthe, A. Bal´ azs, R. Klein, GPU-based trimming and tessellation of NURBS and T-spline surfaces, ACM Transactions on Graphics 24 (3) (2005) 1016.

- J. T. Kajiya, Ray tracing parametric patches, in: Computer Graphics (SIGGRAPH '82 Proceedings), Vol. 16 (3), 1982, pp. 245-54, ray tracing bivariate polynomial patches.

- D. Manocha, J. F. Canny, MultiPolynomial resultant algorithms, Journal of Symbolic Computation 15 (2) (1993) 99-122.

- T. W. Sederberg, F. Chen, Implicitization using moving curves and surfaces, in: SIGGRAPH, 1995, pp. 301-308.

- B. Laurent, Implicit matrix representations of rational B´ ezier curves and surfaces, Computer-Aided Design 46 (2014) 14-24.

- C. Loop, J. Blinn, Resolution independent curve rendering using programmable graphics hardware, ACM Transactions on Graphics (TOG) 24 (3) (2005) 1000.

- T. E. F. Wiegand, Interactive Rendering of CSG Models, Computer Graphics Forum 15 (4) (1996) 249-261.

- J. Rossignac, A. Megahed, B. Schneider, Interactive inspection of solids: cross-sections and interferences, ACM SIGGRAPH Computer Graphics 26 (2) (1992) 353-360.

- M. Segal, K. Akeley, The OpenGL graphics system: A specification (Oct. 2013).

- Y. I. Yeo, L. Bin, J. Peters, efficient pixel-accurate rendering of curved surfaces, in: Proc ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games-I3D '12, ACM Press, New York, New York, USA, 2012, p. 165.

- D. Filip, R. Magedson, R. Markot, Surface algorithms using bounds on derivatives, Computer Aided Geometric Design 3 (4) (1986) 295-311.

- A. Bal´ azs, M. Guthe, R. Klein, efficient trimmed NURBS tessellation, Journal of WSCG 12 (2004) 27-33.3.
