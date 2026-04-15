# Curve Evaluation and Interrogation on Surfaces

Gershon Elber

Computer Science Department
Technion
Haifa 32000, Israel

## Abstract

This paper presents a coherent computational framework to efficiently, and more so robustly, evaluate, interrogate, and compute a whole variety of characteristic curves on freeform parametric rational surfaces represented as (piecewise) polynomial or rational functions. These characteristic curves are expressed as zero sets of bivariate rational functions and include silhouette curves and isoclines from a prescribed viewing direction and or point, reflection lines and reflection ovals, and highlight lines. This zero set formulation allows for a better treatment of singular cases while these characteristic curves are crucial for various applications, from visualization through interrogation to design and manufacturing. c 2001 Academic Press Key Words: silhouettes; isoclines; isophotes; highlight lines; reflection lines.

## Introduction

Freeform surface design is a common tool nowadays in a whole spectrum of geometric applications. Proper design has many aspects and throughout the years, quite a few techniques have been proposed to evaluate the quality of the created surfaces. In this work, we consider one such class of surface quality evaluation scheme, a class that evaluates characteristic curves on the surfaces.

Many techniques that employ curves for surface interrogation were developed, most noticeably reflection lines. Reflection lines have a tradition in the car industry where the quality of the car has been examined in a room with parallel band lights. Simulating this technique with software was the aim of quite a few researchers looking for the simulation of the physical band lighting room [8] or via an approximation that uses a fixed set of curves on the surface [7], perhaps with the aid of intersecting \(S(u;v)\) with a set of parallel planes. Another recent example is [6], where a preprocessing of the surface \(S(u;v)\) into a triangular mesh and the careful enumeration of the expected reflection of each triangular node are employed toward a more efficient process.

This research was supported in part by the Fund for the Promotion of Research at The Technion, Haifa, Israel.

In [12], the problem of detecting steep regions in the design of injection molds is por trayed. A solution that is based on the detection of seed points on the isocline curves, followed by a numerical surface marching process, is also suggested. Clearly, such an approach might suffer from difficulties in guaranteeing the detection of seed points on all isocline curves, on \(S(u, v)\). Furthermore, in general, it is difficult to guarantee the robustness of numerical marching techniques, as, for example, one faces in the general surface-surface intersection (SSI) problem.

When considering curves used in surface interrogation, one can classify the variety of the interrogating curves into their different differential orders. Examples of zero differential order curves on surfaces include isoparametric curves and contour lines. These two types of curves reflect on the general shape of the surface but give no hint of any differential imperfections in the surface.

Second differential order interrogation curves and surfaces are quite common as well, and examples include focal surfaces [4] and obviously lines of curvature and curvature plots [3]. The latter includes the mean, Gaussian, or other variants of the principal curvatures.

In this work, we examine only first differential order curves. The normal of surface \(S(u, v)\) is a function of the two first order partial derivatives of \(S(u, v)\) and hence any imperfections in the first order partials will be immediately reflected in the normal of the surface. The latter immediately affects the way the surface is illuminated. Due to the extensive sensitivity that is given to surface illumination in many industries, such as the car industry, first order differential characteristic curves are quite often exploited in geometric design.

We explore several first order differential characteristic curves. In Section 2, highlight lines [1] are investigated. In Section 3, the computation of silhouette and isocline curves is discussed. Section 4 considers a paradigm for the computation of reflection lines and then introduces a new characteristic curve, the reflection oval, that is similarly expressed as a zero set bivariate function. Finally, we draw our conclusions in Section 5.

Finding the zero set of a rational function is, in general, a simpler and more robust problem to solve compared to general surface-surface intersections or the extraction of general curves on surfaces, in three dimensions. We are required to find the solution to the intersection between an explicit scalar function, \(\mathcal{F}(u, v)\), and a plane, \(Z=0\). Exploiting the subdivision and convex hull containment properties of the NURBS representation, one can easily derive a robust divide and conquer scheme to converge to this desired zero set, with an arbitrary precision [10,11]. An explicit NURBS surface is above (below) the \(Z=0\) level if all its coefficients are positive (negative). Alternatively, the NURBS surface can be subdivided, recursively testing the subdivided elements. By stopping at sufficiently small and/or almost coplanar patches, we end up with a highly robust and quite efficient algorithm.

All the case studies considered in Sections 2 to 4 were computed using a single computational framework in which the characteristic curves are expressed as a zero set of a bivariate rational function. All the presented examples were created with the aid of an implementation that was based on the IRIT [5] solid modeling system that has been developed at the Computer Science Department, Technion, Israel. The zero set solver of the IRIT [5] system was used to extract the actual curves.

## 2 HIGHLIGHT LINES

One simple example that belongs to the class of characteristic curves is the highlight line defined in [1]. Consider a \(C^{1}\) continuous regular parametric surface \(S(u, v)\) and let

$$
\begin{equation*} n(u, v)=\frac{\partial S}{\partial u} \times \frac{\partial S}{\partial v} \tag{1} \end{equation*}
$$

be the unnormalized normal field of \(S\). The regularity requirement on \(S(u, v)\) is equivalent to the constraint of \(\|n(u, v)\| \neq 0\). The highlight curve, \(\mathcal{H}\), on \(S(u, v)\) with respect to some 3 space line \(\mathcal{L}\) in general position, in \(\mathbb{R}^{3}\), is the locus of points on \(S\) such that \(p_{0}=\left(u_{0}, v_{0}\right) \in \mathcal{H}\) if and only if,

$$
\left(S\left(u_{0}, v_{0}\right)+\lambda_{0} n\left(u_{0}, v_{0}\right)\right) \cap \mathcal{L} \neq \emptyset,
$$

for some \(\lambda_{0} \in \mathbb{R}^{+}\). That is, \(\mathcal{H}\) holds for all points on \(S(u, v)\) such that the surface normals at these points intersect \(\mathcal{L}\). Let \(L_{0}\) and \(L_{1}\) be two points on line \(\mathcal{L}, L_{0} \neq L_{1}\). Then, following [1], the condition for a point on \(S(u, v)\) to be a highlight point with respect to \(\mathcal{L}\), reduces to

$$
\begin{equation*} \mathcal{H}=\left\{\left(u_{0}, v_{0}\right) \mid\left\langle\left(L_{0}-L_{1}\right) \times n\left(u_{0}, v_{0}\right), L_{0}-S\left(u_{0}, v_{0}\right)\right\rangle=0\right\}, \tag{2} \end{equation*}
$$

coercing the three vectors of \(\left(L_{0}-L_{1}\right), n\left(u_{0}, v_{0}\right)\), and \(L_{0}-S\left(u_{0}, v_{0}\right)\) to be coplanar. While simple, the locus of points of \(\mathcal{H}\) can clearly reflect on the \(C^{2}\) and \(C^{1}\) disconti nuities in \(S(u, v)\). The derivation of the normal field, \(n(u, v)\), reduces the continuity by one and hence \(C^{2}\) discontinuities in \(S(u, v)\) would be reflected as \(C^{1}\) discontinuities in the highlight lines whereas \(C^{1}\) discontinuities in \(S(u, v)\) would appear as discontinuities in \(\mathcal{H}\). Figure 1 shows one such example of highlight lines computed for a bicubic surface with discontinuities.

## 3 SILHOUETTES AND ISOCLINES

Injection molds are essential manufacturing tools that can be found in numerous industries. Yet, the design of injection molds not only continues to be a difficult procedure but is also, in many cases, a manual and error prone process. One major requirement in mold design attempts to detect and eliminate side slopes that are too steep. These lines are typically near the separation line, the line that subdivides the geometry of the mold into two (or more) parts, but need not be. Such side slopes could make the injected piece inextractable from the mold. Similarly, by employing layered manufacturing (LM) technologies [9], the areas that are in need of support during the manufacturing process are typically defined by the regions on the surface that present tangent plane angles smaller than a certain threshold, with respect to the XY-plane.

Geometrically speaking, during the process of the injection mold design, regions in the geometric model that present slopes larger than a certain tolerance from the injection mold's major axes or direction, \(\mathbf{V}\), should be detected and specially treated. Similarly, in the LM process, if the slope at some surface location is smaller than some tolerance, with respect to the \(X Y\)-plane (having the vertical direction be the \(Z\)-axis), that location requires support.

![FIG. 1. Highlight curves (in gray) can help in the detection of surface discontinuities. The given surface is bicubic, and hence C 2 continuous, in general. A C 2 discontinuity about a third (from the left) along the surface is detected as a C 1 discontinuity in the highlight curves. A C 1 discontinuity about a two thirds along the surface is detected as an actual discontinuity in the highlight curves.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-1-p004.png)

*FIG. 1. Highlight curves (in gray) can help in the detection of surface discontinuities. The given surface is bicubic, and hence C 2 continuous, in general. A C 2 discontinuity about a third (from the left) along the surface is detected as a C 1 discontinuity in the highlight curves. A C 1 discontinuity about a two thirds along the surface is detected as an actual discontinuity in the highlight curves.: Highlight curves (in gray) can help in the detection of surface discontinuities. The given surface is bicubic, and hence C 2 continuous, in general. A C 2 discontinuity about a third (from the left) along the surface is detected as a C 1 discontinuity in the highlight curves. A C 1 discontinuity about a two thirds along the surface is detected as an actual discontinuity in the highlight curves.*

Given surface \(S(u, v)\), the set of points on \(S(u, v)\) that presents a certain, fixed, angle between the normal of \(S(u, v)\) and some viewing direction, \(\mathbf{V}\), is denoted the isoclines [12] of \(S(u, v)\) from \(\mathbf{V}\). Typically, the isoclines are univariate functions or curves, \(C(t)=S(u(t), v(t))\).

If the normal of the surface, \(n(u, v)\), and the viewing direction, \(\mathbf{V}\), are orthogonal, one ends up computing the conventional silhouette curves that are crucial, for example, for hidden curve removal [2]. The isocline curves on the surface are also closely associated with isophotes or lines of equal brightness [4]. Here, the isophotes present curves of constant illumination that could amount to a fixed angle between the normal and the illumination sources (light sources).

We seek all the points on a given regular parametric surface, \(S(u, v)\), that the unnormalized normal field of the surface, \(n(u, v)=\frac{\partial S}{\partial u} \times \frac{\partial S}{\partial v}\), forms a fixed angle with some prescribed direction, \(\mathbf{V}\). This set of points is typically formed out of univariate functions or curves on the surface. In singular cases, such as in planar regions, this assumption might not hold. Nonetheless, hereafter we assume a general freeform surface shape, in a general position, seeking the univariate form that satisfies the fixed angle constraint.

Consider this set of isocline curves on a \(C^{1}\) continuous parametric surface, \(S(u, v)\), that represents curve(s) of constant angle, \(\theta\), with respect to \(\mathbf{V}\). All locations in \(S(u, v)\) that present an angular deviation that is larger than \(\theta\) between \(n(u, v)\) and \(\mathbf{V}\) are delineated from the regions of \(S(u, v)\) of angular deviation that is smaller than \(\theta\), via these isoclines. This delineation holds due to the continuity of the normal field. In other words, for a \(C^{1}\) continuous, nonplanar, parametric surface, the isoclines either form closed regions in the Herein, we present a robust method to compute the set of isocline curves, given a para metric surface \(S(u, v)\) and a prescribed direction \(\mathbf{V}\). Section 3.1 presented the proposed approach, while in Section 3.2, some examples are portrayed.

### 3.1 Proposed Approach

Let the desired fixed angle between the view direction, \(\mathbf{V}\), and the surface normal, \(n(u, v)\), be \(\theta\). Then,

$$
\begin{equation*} \cos (\theta)=\frac{\langle\mathbf{V}, n(u, v)\rangle}{\|n(u, v)\|} \tag{3} \end{equation*}
$$

expresses this angular constraint. We seek to express Constraint (3) as a rational form. Hence, by squaring Constraint (3), one gets

$$
\begin{equation*} \cos ^{2}(\theta)\langle n(u, v), n(u, v)\rangle=\langle\mathbf{V}, n(u, v)\rangle^{2} \tag{4} \end{equation*}
$$

While rational, Constraint (4) includes both positive and negative solutions. That is, if \(\cos (\theta)\) is a solution to Eq. (4), so is \(-\cos (\theta)\). Geometrically, Constraint (4) considers the angle of \(\theta\) from \(\mathbf{V}\) as well as from \(-\mathbf{V}\). Interestingly enough, both the original solution that is viewed from \(\mathbf{V}\) and the reciprocal solution that is viewed from \(-\mathbf{V}\) provide isocline curves that are required by the application of the injection mold design as regions with steep angles in both parts of the injection mold must be detected and eliminated.

Writing Constraint (4) differently, as a zero set constraint, yields

$$
\begin{equation*} \mathcal{F}_{i}(u, v)=\cos ^{2}(\theta)\langle n(u, v), n(u, v)\rangle-\langle\mathbf{V}, n(u, v)\rangle^{2}=0 . \tag{5} \end{equation*}
$$

Differently put, the set of points on surface \(S(u, v)\) that satisfies Constraint (5) equals the set of isoclines or points on \(S(u, v)\) that have a surface normal in a direction that deviates by \(\theta\) degrees from either \(\mathbf{V}\) or \(-\mathbf{V}\). Given a rational surface \(S(u, v)\), the function \(\mathcal{F}_{i}(u, v)\) is clearly rational as well.

### 3.2 Examples

In this section, we present several examples of computed isoclines for freeform surfaces using \(\mathcal{F}_{i}(u, v)\) (Eq. (5)). Figure 2 shows the Utah teapot on its side, with isoclines, in gray, presenting surface normals that are at \(40,50,60,70,80,85\), and \(89^{\circ}\) from \(\mathbf{V}\).

Figure 3 shows a freeform surface in the shape of a wine glass. In Fig. 3a, \(\mathcal{F}_{i}(u, v)\), the function whose zero set is the desired set of isoclines at \(70^{\circ}\) is shown (see Eq. (5)) along with its zero set in thick gray lines. These gray curves, in the parametric space, are mapped onto the original wine glass in Fig. 3b. In Fig. 3c, these gray curves in the parametric space are used to trim and isolate the regions on the wine glass surface that present slopes smaller than \(70^{\circ}\) with respect to the orthographic prescribed (layered manufacturing) view, \(\mathbf{V}\).

Figure 4 shows a freeform surface in the shape of a horn. In Fig. 4a, \(\mathcal{F}_{i}(u, v)\), the function whose zero set is the desired set of isoclines at \(45^{\circ}\), is shown (see Eq. (5)) along with its zero set in thick gray lines. These gray curves, in the parametric space, are mapped onto the original 3-space horn surface in Fig. 4b. In Fig. 4c, these gray curves in the parametric space are again used to trim and isolate the regions on the wine glass surface that present

![FIG. 2. The Utah teapot as four bicubic surfaces on the side with isoclines (in thick gray) presenting surface normals at 40, 50, 60, 70, 80, 85, and 89 ◦ from the V direction.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-2-p006.png)

*FIG. 2. The Utah teapot as four bicubic surfaces on the side with isoclines (in thick gray) presenting surface normals at 40, 50, 60, 70, 80, 85, and 89 ◦ from the V direction.: The Utah teapot as four bicubic surfaces on the side with isoclines (in thick gray) presenting surface normals at 40, 50, 60, 70, 80, 85, and 89 ◦ from the V direction.*

slopes less than \(45^{\circ}\) with respect to the orthographic prescribed (manufacturing) view, \(\mathbf{V}\). Note that the presented approach detects and isolates all such regions, including interior bottom areas.

While a tensor product surface, the horn surface in Fig. 4 and the cap of the teapot in Fig. 2 are both nonregular at singular points. The horn is nonregular at the tip of the surface while the cap of the teapot is nonregular at its center. Hence, the variations in the

![FIG. 3. Isoclines at 70 ◦ of a wine glass laying on its side. The function F i ( u , v ), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the glass while (c) shows (in thin lines) the regions of the glass of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 70 ◦ or less, regions that, for example, might require support in a layered manufacturing process.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-3-p006.png)

*FIG. 3. Isoclines at 70 ◦ of a wine glass laying on its side. The function F i ( u , v ), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the glass while (c) shows (in thin lines) the regions of the glass of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 70 ◦ or less, regions that, for example, might require support in a layered manufacturing process.: Isoclines at 70 ◦ of a wine glass laying on its side. The function F i (u, v), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the glass while (c) shows (in thin lines) the regions of the glass of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 70 ◦ or less, regions that, for example, might require support in a layered manufacturing process.*

![FIG. 4. Isoclines at 45 ◦ of a horn surface laying on its side. The function F i ( u , v ), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set, in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the horn while (c) shows the regions of the horn of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 45 ◦ or less, regions that, for example, might require support in a layered manufacturing process.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-4-p007.png)

*FIG. 4. Isoclines at 45 ◦ of a horn surface laying on its side. The function F i ( u , v ), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set, in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the horn while (c) shows the regions of the horn of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 45 ◦ or less, regions that, for example, might require support in a layered manufacturing process.: Isoclines at 45 ◦ of a horn surface laying on its side. The function F i (u, v), whose zero set is the desired set of isoclines, is presented in (a) along with its zero set, in thick gray lines. Part (b) shows the isoclines (in thick gray) on the surface of the horn while (c) shows the regions of the horn of the surface that are trimmed away, leaving only regions (in thick gray lines) with slopes of 45 ◦ or less, regions that, for example, might require support in a layered manufacturing process.*

magnitudes of the first order derivatives of the surface that hint on the variation in speed of curves on these two surfaces as well as in the glass surface of Fig. 3 are significant. Across the parametric domain of the surfaces, the magnitude of \(\mathcal{F}_{i}(u, v)\) is largely undulating as is evident, for example, from the large variations in the magnitude of \(\mathcal{F}_{i}(u, v)\) in Figs. 3a and 4a. Yet all the isoclines are robustly extracted due to the fact that the zero set contouring problem is simpler and more stable to solve than the general numerical methods of surface marching.

All the examples presented in this section were derived using the zero set finding of Eq. (5) and were computed in a few seconds to a minute on an SGI Indy system equipped with \(a_{150}\) MHz R5000. For a given specific characteristic curve, the computation of \(\mathcal{F}_{i}(u, v)\) has a known time complexity and in all cases the computation of \(\mathcal{F}_{i}(u, v)\) took a negligible time compared to the zero set finding process.

## 4 REFLECTION LINES AND OVALS

Reflection lines have been mostly employed in the automobile industry to examine con tinuity in freeform surfaces. The reflection off a surface depends on the deviation in the normal field of the surface, which, in turn, depends on the first order partial derivatives of the surface. Hence, if surface \(S(u, v)\) is only \(C^{1}\) continuous along some curve \(C\) on \(S(u, v)\), the normal field of \(S(u, v)\) will follow curve \(C\) at \(C^{0}\) continuity. Therefore, and being nor mal field dependent, a reflection of a line in 3-space off surface \(S(u, v)\) will also be \(C^{0}\) continuous along curve \(C\). Once again, because \(C^{0}\) continuity is visually simple to detect, designers have found reflection lines to be a useful tool in interrogating discontinuities, imperfections, and abnormalities in freeform surfaces.

The rest of this section is organized as follows. In Section 4.1, we present our coherent proposed approach for computing reflection lines. In Section 4.2, we extend the proposed approach and examine a different, nonlinear, reflected primitive, a shape that we introduce

![FIG. 5. We question when an incoming ray in the V direction is reﬂected in the r ( u , v ) direction through line L .](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-5-p008.png)

*FIG. 5. We question when an incoming ray in the V direction is reﬂected in the r ( u , v ) direction through line L .: We question when an incoming ray in the V direction is reﬂected in the r (u, v) direction through line L. reflected in the r (u ; v) direction through line L.*

as part of the presented coherent computation framework, the reflection oval. In Section 4.3, some examples are presented.

### 4.1 Reflection Lines

Let \(S(u, v)\) be a \(C^{1}\) continuous regular surface (see Fig. 5) and let \(n(u, v)=\frac{\partial S}{\partial u} \times \frac{\partial S}{\partial v}\) be the unnormalized normal field of surface \(S(u, v)\) as before. Denote by \(\mathbf{V}\) the unit vector along the viewing direction. A ray along \(\mathbf{V}\) that hits surface \(S(u, v)\) will be reflected in the direction of

$$
\begin{equation*} r(u, v)=2 n(u, v)-\mathbf{V} \frac{\langle n(u, v), n(u, v)\rangle}{\langle n(u, v), \mathbf{V}\rangle} . \tag{6} \end{equation*}
$$

examine Eq. (6). If \(n(u, v)\) and \(\mathbf{V}\) are orthogonal, \(\langle n(u, v), \mathbf{V}\rangle\) vanish and \(\|r(u, v)\| \rightarrow \infty\). This degeneracy will make it difficult to derive the reflection lines near the silhouette areas of the surface \(S(u, v)\) from the viewing direction \(\mathbf{V}\). Hence, by rewriting \(r(u, v)\) as

$$
\begin{equation*} \mathbf{r}(u, v)=2 n(u, v)\langle n(u, v), \mathbf{V}\rangle-\mathbf{V}\langle n(u, v), n(u, v)\rangle, \tag{7} \end{equation*}
$$

we resolve the problem.

$$
\mathcal{L}=P_{l}+\mathbf{v}_{l} t, \quad t \in \mathbb{R} .
$$

Then, the locations on surface \(S(u, v)\) that reflect ray \(\mathbf{V}\) through some point on \(\mathcal{L}\) are the locations that satisfy (see Fig. 5)

$$
\begin{equation*} \left\langle S(u, v)-P_{l}, \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle=0, \tag{8} \end{equation*}
$$

coercing the three vectors of \(S(u, v)-P_{l}, \mathbf{v}_{l}\), and \(\mathbf{r}(u, v)\) to be coplanar, much like the highlight lines in Eq. (2).

$$
\begin{equation*} \mathcal{F}_{r_{l}}(u, v)=\left\langle S(u, v), \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle-\left\langle P_{l}, \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle=0 . \tag{10} \end{equation*}
$$

Rewriting (8), we have

$$
\begin{equation*} \left\langle S(u, v), \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle=\left\langle P_{l}, \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle \tag{9} \end{equation*}
$$

The left hand side of Eq. (9) is independent of \(P_{l}\). Given a family of parallel lines in 3-space, typically on some wall of the room, to be reflected off the surfaces, the lines (band lights) differ from each other only in \(P_{l}\). Hence, given the surface \(S(u, v)\), and the direction of this family of lines, \(\mathbf{v}_{l}\), the scalar field of \(\left\langle S(u, v), \mathbf{v}_{l} \times \mathbf{r}(u, v)\right\rangle\) as well as the vector field of \(\mathbf{v}_{l} \times \mathbf{r}(u, v)\) can be precomputed. With these precomputed fields, given a prescription of \(P_{l}\), Eq. (10) could be efficiently derived in full and its zero set computed to yield the shape of the reflection lines on \(S(u, v)\).

### 4.2 Reflection Ovals

The idea of rays reflected off surfaces to examine the continuity of the surface and or imperfections in the surface need not be limited to lines. One can, with similar ease, attempt and consider reflections of other, more complex, primitive shapes, possibly with some additional computational overhead. Herein, we would like to introduce and consider the reflections of ovalic curves.

Let \(S(u, v)\) be a \(C^{1}\) continuous regular surface and let \(\mathbf{r}(u, v)\) be the reflection field as in Eq. (7). Consider \(a_{3}\)-space point \(P_{\mathcal{S}}\) (see Fig. 6). We seek all points on \(S(u, v)\) that reflect the incoming rays \(\mathbf{V}\) in directions \(\mathbf{r}(u, v)\) that form a prescribed angle \(\alpha\) with line

![FIG. 6. We question when an incoming ray in the V direction is reﬂected in the r ( u , v ) direction that forms an angle α with line P S − S ( u , v ).](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-6-p009.png)

*FIG. 6. We question when an incoming ray in the V direction is reﬂected in the r ( u , v ) direction that forms an angle α with line P S − S ( u , v ).: We question when an incoming ray in the V direction is reﬂected in the r (u, v) direction that forms an angle α with line P S − S (u, v). reflected in the r (u ; v) direction that forms an angle fi with line P S ¡ S (u ; v).*

$$
P_{\mathcal{S}}-S(u, v),
$$

$$
\begin{equation*} \cos (\alpha)=\frac{\left\langle P_{\mathcal{S}}-S(u, v), \mathbf{r}(u, v)\right\rangle}{\left\|P_{\mathcal{S}}-S(u, v)\right\|\|\mathbf{r}(u, v)\|} \tag{11} \end{equation*}
$$

With Eq. (13), all that is required in order to compute these ovalic reflection curves on surface \(S(u, v)\) is to prescribe some desired angle \(\alpha=\alpha_{0}\) and solve for that specific zero set.

The reflection ovals of \(\alpha\) degrees are closely related to isoclines of \(\alpha\) degrees. Here, the reflection field \(\mathbf{r}(u, v)\) takes the place of the normal field and a prescribed point \(P_{\mathcal{S}}\) replaces the viewing direction, \(\mathbf{V}\).

Finally, one should note that the shape that is formed by the reflected ovals, \(\mathcal{F}_{r_{o}}(u, v)=0\), is neither circular nor elliptic, in general. Only for the simplest case where \(S(u, v)\) is a plane and point \(P_{\mathcal{S}}\) is above that plane, is the reflected shape a conic section that reduces to a circular shape only if \(\mathbf{V}\) is orthogonal to the plane.

### 4.3 Examples

In this section, we present several examples of computed reflection lines and ovals off freeform surfaces using \(\mathcal{F}_{r_{i}}(u, v)\) and \(\mathcal{F}_{r_{o}}(u, v)\). In Fig. 7, reflection lines off a single bi quadratic surface patch are shown along with the view direction \(\mathbf{V}\).

![FIG. 7. Reﬂection lines (thick gray lines) off a single, C ∞ , biquadratic patch. The view direction is shown by the arrow.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-7-p010.png)

*FIG. 7. Reﬂection lines (thick gray lines) off a single, C ∞ , biquadratic patch. The view direction is shown by the arrow.: Reﬂection lines (thick gray lines) off a single, C ∞ , biquadratic patch. The view direction is shown by the arrow. Reflection lines (thick gray lines) off a single, C 1, biquadratic patch. The view direction is shown by*

While Eq. (11) is not rational, the square of Eq. (11) is

$$
\begin{equation*} \cos ^{2}(\alpha)=\frac{\left\langle P_{\mathcal{S}}-S(u, v), \mathbf{r}(u, v)\right\rangle^{2}}{\left\langle P_{\mathcal{S}}-S(u, v), P_{\mathcal{S}}-S(u, v)\right\rangle\langle\mathbf{r}(u, v), \mathbf{r}(u, v)\rangle} \tag{12} \end{equation*}
$$

$$
\begin{equation*} \mathcal{F}_{r_{o}}(u, v)=\cos ^{2}(\alpha)-\frac{\left\langle P_{\mathcal{S}}-S(u, v), \mathbf{r}(u, v)\right\rangle^{2}}{\left\langle P_{\mathcal{S}}-S(u, v), P_{\mathcal{S}}-S(u, v)\right\rangle\langle\mathbf{r}(u, v), \mathbf{r}(u, v)\rangle}=0 . \tag{13} \end{equation*}
$$

![FIG. 8. Reﬂection lines (thick gray lines) off a biquadratic B-spline surface with two interior knots that introduces two C 2 discontinuous lines. The view direction is shown by the arrow.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-8-p011.png)

*FIG. 8. Reﬂection lines (thick gray lines) off a biquadratic B-spline surface with two interior knots that introduces two C 2 discontinuous lines. The view direction is shown by the arrow.: Reﬂection lines (thick gray lines) off a biquadratic B-spline surface with two interior knots that introduces two C 2 discontinuous lines. The view direction is shown by the arrow. Reflection lines (thick gray lines) off a biquadratic B-spline surface with two interior knots that introduces two C 2 discontinuous lines. The view direction is shown by the arrow.*

In Fig. 8, a biquadratic surface with two \(C^{2}\) discontinuities is shown along with its reflection lines and view direction, \(\mathbf{V}\). The mesh and the knot sequences of this surface are presented in Appendix A. As can be seen in Fig. 8, this surface has two \(C^{2}\) discontinuities that are quite visible due to the \(C^{1}\) discontinuities in the reflection lines. One such \(C^{2}\) surface discontinuity is clearly visible at a highly concentrated region of \(C^{1}\) discontinuous reflection lines, about a third from the right. A second \(C^{2}\) surface discontinuity can be seen a third from the left side, by detecting one \(C^{1}\) discontinuous reflection line. Finally, in Fig. 9, the reflection lines off a sphere are presented.

![FIG. 9. Reﬂection lines (thick gray lines) off a bicubic sphere. The view direction is shown by the arrow.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-9-p011.png)

*FIG. 9. Reﬂection lines (thick gray lines) off a bicubic sphere. The view direction is shown by the arrow.: Reﬂection lines (thick gray lines) off a bicubic sphere. The view direction is shown by the arrow. Reflection lines (thick gray lines) off a bicubic sphere. The view direction is shown by the arrow.*

![FIG. 10. Reﬂection ovals (thick gray lines) off a biquadratic B-spline surface with C 2 discontinuities (compare with Figure 8). The view direction is shown by the arrow.](/Users/evanthayer/Projects/stepview/docs/2001_curve_evaluation_and_interrogation_on_surfaces/figures/figure-10-p012.png)

*FIG. 10. Reﬂection ovals (thick gray lines) off a biquadratic B-spline surface with C 2 discontinuities (compare with Figure 8). The view direction is shown by the arrow.: Reﬂection ovals (thick gray lines) off a biquadratic B-spline surface with C 2 discontinuities (compare with Fig. 8). The view direction is shown by the arrow. Reflection ovals (thick gray lines) off a biquadratic B-spline surface with C 2 discontinuities (compare with Fig. 8). The view direction is shown by the arrow.*

in \(C^{1}\) discontinuities in the reflected ovals on the surface. From this view, the \(C^{2}\) surface discontinuity that is a third from the left is clearly visible, and several \(C^{1}\) discontinuous reflected ovals can be seen.

The computation of the presented reflection lines and ovals varies from an almost interactive speed of several frames per second for Fig. 7 to about a minute for the reflected ovals of Fig. 10 on an SGI Indy system equipped with a 150 MHz R5000.

## 5 CONCLUSION

We have presented a coherent, highly robust, and quite efficient scheme to extract silhouette and isocline curves as well as reflection lines and ovals off freeform surfaces. The proposed approach employs two phases. The first, symbolic phase derives a function \(\mathcal{F}(u, v)\) such that \(\mathcal{F}(u, v)=0\) equates with the desired locus of points on \(S(u, v)\). A second, nu meric process computes this zero set. Being symbolic, the first stage is highly robust. The substitution of the numeric coefficients of \(S(u, v)\) into the different \(\mathcal{F}(u, v)\) equations yields a process that can handle singularities with relative ease. In this work, we have selected to ignore such singular cases mainly due to the need to support a zero set finder that handles such cases, which is beyond the scope of this work. Nevertheless, handling singularities in \(\mathcal{F}(u, v)\) is typically a simpler task compared to the detection of whole faces that are silhouette or isocline regions in \(\mathbb{R}^{3}\).

In this work, the viewing direction was fixed as \(\mathbf{V}\). Adding support for a perspective transformation, or a viewing point \(V_{p}\), one should replace any instance of \(\mathbf{V}\) with \(S(u, v)- V_{p}\). Hence, the rational formulation of the different \(\mathcal{F}(u, v)=0\) constraints remains rational, following this substitution.

Weare certain that the presented coherent approach can better serve in surface evaluation and interrogation and in the derivation of other, similar, characteristic curves, including second differential order characteristic curves or even higher.

## A COEFFICIENTS OF B-SPLINE SURFACE IN FIGS. 8 AND

The surface in Figs. 8 and 10 is a biquadratic (degree 2 in U and V) B-spline surface with:

## U Knot Sequence:

$$
\begin{array}{llllll} 0 & 0 & 0 & 1 & 1 & 1 \end{array}
$$

## V Knot Sequence:

Control Mesh: 0.699477 0.071974 ¡ 0.381915 0.013501 0.46333 ¡ 1.01136 0.410664 ¡ 0.462427 ¡ 0.939545

0.49953 0.557109 0.21478 0.210717 0.022708 ¡ 0.34285 ¡ 0.201925 1.15706 ¡ 0.345263 0.392455 ¡ 0.20932 0.395063 ¡ 0.293521 0.182036 ¡ 0.234382 0.103642 ¡ 0.743721 ¡ 0.162567

0.192508 0.275815 0.991758 ¡ 0.096305 ¡ 0.258586 0.434128 ¡ 0.508947 0.875765 0.431715 0.085433 ¡ 0.490614 1.17204 ¡ 0.600543 ¡ 0.099258 0.542596 ¡ 0.20338 ¡ 1.02502 0.614411

## Acknowledgments

The author is in debt to the reviewers of this paper that have vastly improved the quality of this final result with their comments.

## References

- K. P. Beier and Y. Chen, Highlight-line algorithm for realtime surface-quality assessment, Comput. Aided Design 26, 1994, 268-277.

- G. Elber and E. Cohen, Hidden curve removal for free form surfaces, Comput. Graphics 24, 1990, 95-104 (Siggraph 1990).

- G. Elber and E. Cohen, Second order surface analysis using hybrid symbolic and numeric operators, Trans. Graphics 12, 1993, 160-178.

- J. Hoschek and D. Lasser, Fundamentals of Computer Aided Geometric Design, A K Peters, Wellesley, MA, 1993.

- IRIT 8.0 User's Manual, February 2001, Technion. Available at http: www.cs.technion.ac.il » irit.

- J. Kang, K. W. Lee, and I. Cho, efficient algorithm for real-time generation of reflection lines, in KoreaIsrael Bi-National Conference on Geometric Modeling and Computer Graphics in the World Wide Web Era, September-October 1999, Seoul, Korea, pp. 19-28.

- E. Kaufmann and R. Klass, Smoothing surfaces using reflection lines for families of splines, Comput. Aided Design 20, 1988, 312-316.

- R. Klass, Correction of local surface irregularities using reflection lines, Comput. Aided Design 12, 1980, 73-77.

- A. L. Marsan and D. Dutta, A survey of Process planning techniques for layered manufacturing, in Proceedings of the 1997 ASME Design engineering Technical Conferences, Sacramento, CA, Sept. 1997.

- M. J. Pratt and A. D. Geisow, Surface surface intersection problems, in The Mathematics of Surfaces (J. A. Gregory, Ed.), pp. 117-142, Clarendon Press, Oxford, 1986.

- T. W. Sederberg and S. R. Parry, Comparison of three curve intersection algorithms, Comput. Aided Design 18, 1986, 58-63.

- Y. Tokuyama and S. Bae, An approximation method for generating draft on a freeform surface, Visual Comput. 15, 1999, 1-8.
