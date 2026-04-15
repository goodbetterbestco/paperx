# Ray Tracing Trimmed Rational Surface Patches

Tomoyuki Nishita*, Thomas W. Sederberg, Masanori Kakimoto, tional Geometry, Object Modeling; I. . [Computer Graphics]

\( { }^{\dagger} \) Brigham Young University
\( { }^{\ddagger} \) Fujitsu Laboratories LTD

## Abstract

Numerical solutions to the ray patch intersection problem include those developed by Toth [18], Sweeney and Bartels [17), and This paper presents a new algorithm for computing the points at which a ray intersects Joy and Bhetanabhotla [4]. Toth's algorithm is based on interval , rational Bezier surface patch, and also an algorithm for determining it an interser ion point lies within a region trimmed by piecewise Bézier curves. Both algorithm cial preprocessing. Categories and Subject Descriptors: I.3.3 [ Computer Graphics): Picture Image Generation; I.3.5 [Computer Graphics): Computational Geometry and Object Modeling; 1.3.7 [Computer Graphics]: Three-Dimensional Graphics and Realism. General Terms: Algorithms Additional Key Words and Phrases: Computer graphics, ray trac- ing, visible surface algorithms, parametric surfaces. 1 INTRODUCTION The history, theory and capabilities of ray tracing are well docu- surface patches. Specifically, we present an algorithm for computing all points at which a ray intersects a rational Bézier surface patch of any degree. We also describe an algorithm for determining if a mented [3], [5]. This paper deals with the ray tracing of parametric point lies within a trimmed region of the patch. We define a trimmed curves in the parameter plane of the patch. region to be an area bounded by piecewise (possibly rational) Bézier 1.1 Ray-Patch Algorithms Solutions to the ray patch intersection problem can be categorized roughly as being based on subdivision, algebraic or numerical techniques. Subdivision approaches are described by Whitted [19], Rogers [10] and Woodward (20]. These algorithms harness the convex hull hull of the control points, it does not intersect the patch. Through property of Bézier surfaces: if the ray does not intersect the convex recursively subdividing the patch and checking convex hulls, the intersection points can be computed at a linear convergence rate, amounting to a binary search. Whitted's algorithm operates in three dimensions, whereas Rogers and Woodward map the problem to two dimensions. which bounds on the surface and its first derivatives can be obtained. Newton iteration. It works robustly on any parametric surface for Sweeney and Bartels ray trace B-spline surfaces by refining the con- mates the surface. The ray intersection is then computed by intersecting the control mesh with the ray, and using that intersection point as a starting point for Newton iteration. Joy and Bhetanabhotla's algorithm uses quasi-Newton optimization to compute the points) on the patch nearest the ray, including intersection points. Kajiya[6] devised an intersection algorithm based on algebraic techniques (ie., resultants). Kajiya's algorithm reduces the problem of intersecting a bicubic patch with a ray into one of finding the real roots of a degree 18 univariate polynomial. Our ray patch intersection algorithm is based on the convex hull property of Bézier curves and surfaces using a technique we refer to as Bézier clipping. Traditionally, intersection algorithms (such as curve curve [13], surface surface [7], or ray surface [19]) trol mesh using the Oslo algorithm until the mesh closely approxi- based on the convex hull property (that is, subdivision based algorithms) perform a linearly converging binary search. Bézier clipping uses the convex hull property in a more powerful manner, by determining parameter ranges which are guaranteed to not include models, rendering can be performed using conventional construc- points of intersection. Variations of this concept have proven profitable in algorithms for algebraic curve intersection( 12] and planar parametric curve intersection[15]. Bézier clipping has the flavor of a geometrically based interval Newton method, and thus might be categorized as partly a subdivision based algorithm and partly a numerical method. 1.2 Trimmed Patch Algorithms Previous approaches to the rendering of trimmed patches include adaptive forward differencing [16] and polygonization [9]. Neither of these approaches adapts directly to ray tracing (unless one were to polygonize the patch[9] and then ray trace the polygons). If trimming is caused by a boolean operation involving solid geometric tive solid geometry methods[11]. Our algorithm renders trimmed patches defined in a boundary representation, by determining if a point on the patch lies inside or outside a trimmed region. One contribution of this paper is a fast, robust algorithm (based on Bézier clipping) for determining if a ray intersects a collection of trimming curves an even or odd number of times. 1.3 Paper Overview Section 2 introduces Bézier clipping and applies it to the problem of point classification for trimmed patches. Section 3 describes our ray patch intersection algorithm, and performance comparisons are presented in section 4.

## Introduction

This paper assumes the reader is familiar with rational Bézier curves and surfaces[2]. The ray patch intersection algorithm requires patches to be expressed in Bezier form. The point classification algorithm requires trimming curves to be in Bézier form. Conversion from NURBS to Bézier representation is discussed in reference 9.

## 2 POINT CLASSIFICATION

Figure 1 shows a trimmed Bézier surface patch. Its parameter domain (see Figure 2) contains several trimming curves, expressed in Bézier (or rational Bézier) form. Regions enclosed by trimming curves are excluded from the patch. point classification, in the context of trimmed patch ray tracing, is the problem of determining if a given point \(\mathbf{S}\) in \(s, t\) patch param eter space lies IN the patch, OUT of the patch (in a region enclosed by trimming curves), or ON a trimming curve. If \(\mathbf{S}\) is a point at which a ray intersects the patch, then \(S\) qualifies as a hit if it is IN, and as a miss if it is OUT. If \(\mathbf{S}\) is ON a trimming curve, it is reported as a hit, but is flagged for possible anti-alias supersampling.

$$
\begin{equation*} a s+b t+c=0, \quad a^{2}+b^{2}=1 \tag{2} \end{equation*}
$$

Trimming curves completely enclose an OUT region. This may require linear Bézier curve segments along portions of the patch boundary (as in Figure 2). Recall a corollary of the Jordan curve theorem: If any ray \(\mathbf{R}\) in \(s, t\) patch parameter space (not to be confused with a "tracing ray" in \(R^{3}\) ) emanating from \(\mathbf{S}\) intersects the collection of trimming curves an even (odd) number of times, then \(\mathbf{S}\) is IN (OUT of) the patch. Our point classification algorithm amounts to an efficient method of determining that even/odd intersection parity. For this discussion, \(\mathbf{R}\) points in the positive \(s\) direction. In practice, choose the ray in the \(\pm s\) or \(\pm t\) direction which exits the parameter square in the shortest distance. It might appear that ray/curve tangencies can cause a problem. As discussed in CASE \(B\) below, this is not a concern.

The algorithm begins by splitting the patch parameter plane into quadrants which meet at \(\mathbf{S}\) as shown in Figure 3. To determine if \(\mathbf{R}\) intersects a given Bézier trimming curve an even or odd number of times, we categorize the curve based on which quadrants its control points occupy. For now, assume that no end control point lies on a quadrant boundary (a situation addressed in section 2.2.1).

- CASE A: All control points lie on the same side of the line containing R (in quadrants I, II, III, IV, I&II, or III&IV) or "behind" \(R(inquadrantsII&III)\). The convex hull property of Bézier curves guarantees zero intersections with R.

- CASE B: All control points lie in quadrants I&IV, but not case A. Since the curve is continuous and obeys the convex hull property, if the curve endpoints lie in the same quadrant, the curve crosses R an even number of times. Otherwise, the curve intersects R an odd number of times. Note that tangencies between the ray and trimming-curve tangencies, even those of high order, do not pose a problem. The only question is whether the curve endpoints straddle the ray.

CASE C: All other curves.

If a curve is case \(\mathcal{A}\) or \(\mathcal{B}\) no further processing is needed to de termine its intersection parity with a ray. For a case \(\mathcal{C}\) curve, we subdivide it using the de Casteljau algorithm[2] into three Bézier segments in such a way that the two end segments are guaranteed a priori to be case \(\mathcal{A}\) or \(\mathcal{B}\). The points at which to subdivide are determined using a technique we call Bézier clipping, described

$$
d(u)=\sum_{i=0}^{n} d_{i} B_{i}^{n}(u)=0, \quad d_{i}=w_{i}\left(a s_{i}+b t_{i}+c\right)
$$

### 2.1 Bézier Clipping

$$
\begin{equation*} \mathbf{C}(u)=\sum_{i=0}^{n} \mathbf{C}_{i} B_{i}^{n}(u) \tag{1} \end{equation*}
$$

\(\mathbf{C}_{i}=\left(s_{i}, t_{i}\right)\) are the Bézier control points and \(B_{i}^{n}(u)=\binom{n}{i}(1-u)^{n-i} u^{i}\) denote the Bernstein basis functions. \(\mathbf{L}\) is defined by its normalized implicit equation

The intersection of \(\mathbf{L}\) and \(\mathbf{C}\) can be found by substituting equation 1 into equation 2 :

$$
\begin{equation*} d(u)=\sum_{i=0}^{n} d_{i} B_{i}^{n}(u)=0, \quad d_{i}=a s_{i}+b t_{i}+c \tag{3} \end{equation*}
$$

Note that \(d(u)=0\) for all values of \(u\) at which \(\mathbf{C}\) intersects \(\mathbf{L}\). Also, \(d_{i}\) is the distance from \(\mathbf{C}_{i}\) to \(\mathbf{L}\) (as shown in Figure 4). The function d(u) in equation 3 is a polynomial in Bemstein form, and can be represented as an "explicit" (or so-called "nonparametric") Bézier curve[1] as follows:

$$
\begin{equation*} \mathbf{D}(u)=(u, d(u))=\sum_{i=0}^{n} \mathbf{D}_{i} B_{i}^{n}(u) \tag{4} \end{equation*}
$$

Since \(\sum_{i=0}^{n} \frac{i}{n} B_{i}^{n}(u) \equiv u[(1-u)+u]^{n} \equiv u\), the horizontal coordinate of any point \(\mathbf{D}(u)\) is in fact equal to the pa rameter value \(u\). Figure 5 shows the curve \(\mathbf{D}(u)\) which corresponds to the intersection in Figure 4. Since \(\mathbf{D}(u)\) crosses the \(u\)-axis at the same \(u\) values at which \(\mathbf{C}(u)\) intersects \(\mathbf{L}\), we can apply the convex hull property of Bézier curves to identify ranges of \(u\) for which \(\mathbf{C}\) does not intersect \(\mathbf{L}\). Referring again to Figure 5, the convex hull of the \(\mathbf{D}_{i}\) intersects the \(u\) axis at points \(u=u_{\min }=\frac{1}{6}\) and \(u=u_{\max }=\frac{4}{7}\). Since \(\mathbf{D}(u)\)

#### 2.1.1 Rational Curves

For rational Bézier trimming curves

$$
\begin{equation*} \mathbf{C}(u)=\frac{\sum_{i=0}^{n} w_{i} \mathbf{C}_{i} B_{i}^{n}(u)}{\sum_{i=0}^{n} w_{i} B_{i}^{n}(u)} \tag{5} \end{equation*}
$$

![Figure 1. Inminico raica](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-1-p003.png)

*Figure 1. Inminico raica: Figure 1. Inminico raica Trimmed Patch*

![Figure 2](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-2-p003.png)

*Figure 2: Trimming curves*

![Figure 3](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-3-p003.png)

*Figure 3: Quadrants*

![Figure 4](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-4-p003.png)

*Figure 4: Bézier curve/line intersection*

![Figure 5](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-5-p003.png)

*Figure 5: Explicit Bézier curve*

![Figure 6](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-6-p003.png)

*Figure 6: Bézier clips per classification*

![Figure 7](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-7-p003.png)

*Figure 7: Sample trimmed patch*

### 2.2 Point Classification Algorithm

Returning to the problem of point classification, our goal is to subdi vide a case \(\mathcal{C}\) curve into three segments, such that segments 1 and 3 are assured to be case \(\mathcal{A}\) or \(\mathcal{B}\). This can be accomplished by applying Bézier clipping against either the \(s\) quadrant axis ( \(\mathbf{L}=t-t_{\mathrm{r}}=0\) ) We should clip against the axis which will result in the smallest segment 2. A good heuristic for this is to measure the distance from the curve endpoints to each of the axes. Generally, the larger the distance from an axis, the larger the clip tends to be. Denote \(d_{s}=\left|d_{0}\right|+\left|d_{n}\right|\) for the case when \(\mathbf{L}\) is the \(s\) quadrant axis, and \(d_{t}=\left|d_{0}\right|+\left|d_{n}\right|\) when \(\mathbf{L}\) is the \(t\) quadrant axis. Thus, if \(d_{s}>d_{t}\), it is The complete point classification algorithm appears as follows. For clarity, we assume that the point is nearest the edge s = 1 in the parameter square, so we count intersections of the trimming curves with the ray in the positive s direction. If the distance from the point to one of the trimming curves is less than a tolerance value ON TOL, the point is declared to be ON a trimming curve ON_TOL= 10-4 is conservative, and was used in producing Figure 7. BEGIN CLASSIFY

```text
INPUT: Trimming curves, Point, ON_TOL OUTPUT: IN, OUT, or ON Push all trimming curves onto a stack;
```

$$
SIZE = largest dimension of the bounding box;
$$

$$
\begin{equation*} \hat{\mathbf{P}}(s, t)=\frac{\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) w_{i j} \hat{\mathbf{P}}_{i j}}{\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) w_{i j}} \tag{6} \end{equation*}
$$

#### 2.2.1 Implementation

$$
\begin{equation*} d^{k}(s, t)=\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) d_{i j}^{k}=0 \tag{8} \end{equation*}
$$

A problem can arise when \(\mathbf{R}\) happens to pass through an end control point shared by two trimming curves, because two intersections will be reported when one is often the correct answer. The solution we use is to perturb \(S\) away from \(R\) a sub-pixel distance \(<\) ON_TOL. For the same reason, it is important that \(d\left(u_{\min }\right) \neq 0\) and \(d\left(u_{\max }\right) \neq\) 0 (in equation 4 and Figure 5) to within floating point precision. Therefore, make the adjustment \(u_{\min }=0.99 * u_{\min }\) and \(u_{\max }=0.99 * u_{\max }+0.01\). Another reason for this adjustment is to avoid infinite loops. Bézier clipping a curve whose endpoint happens to lie on \(\mathbf{R}\) (ie., \(d_{0}=0\) ) results in segments 1 and 2 having zero length, and segment 3 is simply the original curve.

### 2.3 Performance

ON is the classification which is most expensive to compute. Our algorithm can typically compute an ON classification to seven decimal digits accuracy in four Bézier clips. Figure 6 shows the trimmed patch in Figure 1, using color to indicate how many total Bézier clips were used in classifying each ray intersection. The average number of Bézier clips per point to be classified was 1.04 in this example involving ten trimming curves. Figure 7 shows a patch trimmed with precision by eight Bézier curves.

## A No action needed.

- B If the curve endpoints Co and C, are in different quadrants, increment inter.

- C If SIZE < ON TOL, report ON and RETURN.

Else if \(d_{s} \geq d_{t}\), perform Bézier clipping against \( \mathbf{L}=

$$
\begin{equation*} a_{k} \hat{x}+b_{k} \hat{y}+c_{k} \hat{z}+e_{k}=0, \quad k=1,2 \tag{7} \end{equation*}
$$

$$
Else, perform Bézier clipping against \( \mathbf{L}=t-t_{\tau}=0 \).
$$

If inter is odd, report OUT; else report IN

## 3 RAY-PATCH INTERSECTION

Our algorithm for computing the intersection of a patch with a ray uses the Bézier clipping concept to iteratively clip away regions of the patch which don't intersect the ray.

Section 3.2 then shows how to apply Bézier clipping to iteratively clip away regions of the projected patch which don't intersect the ray.

The most costly single operation in a subdivision-based ray patch intersection algorithm is de Casteljau subdivision. Typically, subdivision is performed in \(R^{3}\) for non-rational patches, and in \(R^{4}\) for rational patches. Woodward[20] (also alluded to by Rogers[10]) shows how the problem can be projected to \(R^{2}\). This means that the number of arithmetic operations to subdivide a non-rational patch is reduced by \(33 \%\) (since subdivision is applied only to \(x, y\) com ponents, rather than \(x, y, z\) ) and for a rational patch is reduced by \(\mathbf{2 5 \%}\) (subdivision in \(x, y, w\) rather than in \(x, y, z, w\) ). Section 3.1 re views that projection, and further shows how the rational case can be handled by subdividing only two components.

### 3.1 Projection to R'

A rational Bézier surface patch in Cartesian three space (î, 9, Ê) is defined parametrically by where \(\hat{\mathbf{P}}_{i_{j}}=\left(\hat{x}_{i_{j}}, \hat{y}_{i_{j}}, \hat{z}_{i_{j}}\right)\) are the Bézier control points with corre sponding weights \(w_{i_{j}}\). (The symbols are hatted to later distinguish them from the projected ( \(x, y\) ) coordinate system). As does Kajiya[6], we define the ray to be the intersection of two planes given by implicit equations

We assume that the plane equations are normalized: \(a_{k}^{2}+b_{k}^{2}+c_{k}^{2}=1\). In practice, it is best if the two planes are orthogonal. For primary rays, we use the scan plane and the plane containing the ray, parallel The intersection of plane k and the patch can be represented by substituting equation 6 into equation 7 and clearing the denominator:

Note that \(d_{i_{j}}^{k}\) is related to the distance from control point \(\hat{\mathbf{P}}_{i_{j}}\) to plane \(k\) :

$$
\begin{equation*} d_{i j}^{k}=w_{i j} \times D I S T A N C E\left(\hat{\mathbf{P}}_{i j}, \text { Plane } k\right) \tag{10} \end{equation*}
$$

where

$$
\begin{equation*} d_{i j}^{k}=w_{i j}\left(a_{k} \hat{x}_{i j}+b_{k} \hat{y}_{i j}+c_{k} \hat{z}_{i j}+e_{k}\right) \tag{9} \end{equation*}
$$

$$
\( \hat{\mathbf{P}}(\hat{s}, \hat{t}) \) lies on plane \( k \) iff \( d^{k}(\hat{s}, \hat{t})=0 \).
$$

$$
\begin{equation*} \mathbf{P}_{i j}=\left(x_{i j}, y_{i j}\right)=\left(d_{i j}^{1}, d_{i j}^{2}\right) \tag{11} \end{equation*}
$$

![Figure 8](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-8-p005.png)

*Figure 8: Projected patch P*

The ray-patch intersection problem now becomes one of finding

$$
\begin{equation*} \{(s, t) \mid \mathbf{P}(s, t)=\mathbf{0} ; 0 \leq s, t \leq 1\} . \tag{13} \end{equation*}
$$

For a non-rational patch (that is, all \(w_{i_{j}}=1\) ), \(\mathbf{P}\) is a simple or thographic projection of \(\hat{\mathbf{P}}\) along the ray. \(\mathbf{P}(s, t)\) is always non rational (all its weights are equal), even if \(\hat{\mathbf{P}}(s, t)\) is rational.

### 3.2 BÉZIER CLIPPING P

Solt scion applies Bezier clipping to the problem of inding all

$$
\begin{equation*} \mathbf{P}(s, t)=0 . \tag{14} \end{equation*}
$$

Begin by defining a line \(\mathbf{L}_{s}\) through \(\mathbf{0}\) parallel to the vector \(\mathbf{V}_{\mathbf{0}}+ \mathbf{V}_{1}\) as shown in Figure 9. Bézier clipping will be used to identify ranges of the \(s\) parameter in which \(\mathbf{P}(s, t)\) does not map to \(\mathbf{0}\).

$$
\begin{equation*} a x+b y+c=0, \quad a^{2}+b^{2}=1 \tag{15} \end{equation*}
$$

then the distance \(D_{i_{j}}\) from each control point \(\mathbf{P}_{i_{j}}=\left(x_{i_{j}}, y_{i_{j}}\right)\) to \(\mathbf{L}_{i}\)

$$
\begin{equation*} D_{i j}=a x_{i j}+b y_{i j}+c . \tag{16} \end{equation*}
$$

The \(D_{i_{j}}\) are shown in Figure 10. Likewise, the distance \(D(s, t)\) from \(\mathbf{L}_{s}\) to any point \(\mathbf{P}(s, t)\) on the projected patch is

The function \(d(s, t)\) can be represented, in an ( \(s, t, d\) ) coor dinate system, as an explicit (or so-called non-parametric) surface

![Figure 9](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-9-p005.png)

*Figure 9: Line L,*

$$
\begin{equation*} \mathbf{P}(s, t)=\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) \mathbf{P}_{i j} \tag{12} \end{equation*}
$$

![Figure 10.](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-10-2-p006.png)

*Figure 10.: Figure 10.*

$$
\begin{equation*} D(s, t)=\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) D_{i j} \tag{17} \end{equation*}
$$

$$
\begin{equation*} \mathbf{D}(s, t)=\sum_{i=0}^{n} \sum_{j=0}^{m} B_{i}^{n}(s) B_{j}^{m}(t) \mathbf{D}_{i j}=(s, t, D(s, t)) . \tag{18} \end{equation*}
$$

Dopie i ca. Compare in eure it, in onton poin Figure 10.

![Figure 10.](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-10-2-p006.png)

*Figure 10.: Figure 10.*

![Figure I1](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-i1-p006.png)

*Figure I1: Top view of D (s,t) parch.*

![Figure 12](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-12-p006.png)

*Figure 12: Side view of D(s. t) patch. Top view of D(s, t) patch.*

bounds the projection of the \(\mathbf{D}(s, t)\) patch. In this example, that convex hull intersects the \(s\) axis at points \(s_{\min }=2 / 5\) and \(s_{\max }=2 / 3\). We conclude that \(d(s, t) \neq 0\), and therefore \(\mathbf{P}(s, t) \neq \mathbf{0}\), for \(s<2 / 5\) and \(s>2 / 3\). The de Casteljau subdivision algorithm is applied to clip away those regions, leaving the two dimensional patch in Figure 13. This process of identifying values \(s_{\text {min }}\) and \(s_{\text {max }}\) which bound the solution set, and then subdividing off the regions \(s<s_{\text {min }}\) and \(s>s_{\max }\) will be referred to as Bézier clipping in \(s\). In an obviously similar manner, we define the process of Bézier clipping in \(t\).

![Figure 13](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-13-p006.png)

*Figure 13: first clip in s.*

![Figure 14](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-14-p006.png)

*Figure 14: Iterating to the solution.*

(In this case, let's assume the tolerance value is \(10^{-4}\). In practice, one should pick a tolerance value which assures sub-pixel accuracy. This is done by finding a bound on the largest first derivative of screen space \(x\) or \(y\) with respect to parameter space \(s\) or \(t\).) How ever, in computing \(t_{\text {min }}, t_{\text {max }}\) for the next \(t\) clip, it turns out that \(t_{\text {max }}-t_{\text {min }}<10^{-4}\). Without subdividing in \(t\), we then compute \(s_{\min }, s_{\max }\) for an \(s\) clip, and discover that \(s_{\max }-s_{\min }<10^{-4}\) also. Thus, in the final step, we compute the intersection to within tolerance without actually subdividing to the clip values. The to tal number of operations in this typical example is: \(s_{\min }, s_{\max }\) or \(t_{\text {min }}, t_{\text {max }}\) is computed five times, and three pairs of de Casteljau subdivisions are performed.

### 3.3 No intersection

If a Bézier trim calculation determines \(s_{\text {min }}>1, s_{\text {max }}<0, t_{\text {min }}>\) 1, or \(t_{\text {max }}<0\), the ray does not intersect the patch. can only occur if \(s_{\text {min }}=0, s_{\text {max }}=1, t_{\text {min }}=0\), or \(t_{\text {max }}=1\). Whenever the subpatch lies on the boundary of the original patch,

### 3.4 Multiple intersections

![Figure 15](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-15-p007.png)

*Figure 15: Patch domain-two intersections*

Therefore, the remaining domain is subdivided in half at \(t=0.5\). A stack data structure is used to store subpatches. We push one of the two sub patches onto the stack, and proceed to process the other subpatch by Bézier clipping in \(s\) to eliminate regions 2 and clipping in \(t\) to remove regions 3. As in the example in Figure 14, without further subdivision we can compute the intersection which lies between re gions 3 to within tolerance. There remains one subpatch on the stack, which we now pop and begin to process by clipping regions 4. The second intersection is refined in two more Bézier clips, as shown.

### 3.5 Primary Ray Preprocessing

Bézier clipping can be used to advantage in a preprocessing step applied at the initialization of each scan line. By Bézier clipping \(\mathbf{P}\) against the scan line in both \(s\) and \(t\) directions, regions of \(\mathbf{P}\) can be discarded which do not intersect any primary ray along the scan line. Figure 16 shows the patch in Figure 8 after Bézier clipping against the scan line ( \(x\) axis). By performing this preprocess, a savings of up to two subdivisions per primary ray/surface intersection can be realized, and also non-intersecting rays can be detected more often. For example, in applying this preprocessing to rendering the teapot in Figure 17, 86\% of the calls to the intersection routine resulted in a hit.

### 3.6 Implementation

To avoid potential infinite loops due to numerical roundoff, make the adjustment \(s_{\min }=0.99 * s_{\min }\) and \(s_{\max }=0.99 * s_{\max }+0.01\) and similarly for t in computing values at which to Bézier clip. Other than the ray patch intersection algorithm, all of the other implementation details are standard. Antialiasing was performed using adaptive supersampling [5], and Murakami's voxel partitioning [8] was implemented. Shadows, reflection and refraction are dealt with in the conventional manner, using our ray-patch intersection algorithm.

![Figure 16](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-16-p007.png)

*Figure 16: Trimming to the Scan Line.*

## 4 DISCUSSION

### 4.1 Examples and Timings

We tested the algorithm on an Iris-4D 70GT workstation and created Figures 17-20 at 500X500 resolution. Each figure caption lists the number of patches in the scene, total CPU time for rendering, (CPU time for rendering a similar scene, not antialiased, with primary rays only), percentage of background pixels, and average number of patch subdivisions per foreground pixel for primary rays. All patches are non-rational bicubics. The chains in Figure 19 were oriented using Free-Form Deformation[14].

### 4.2 Performance Comparisons

It is difficult to derive precise quantitative comparisons between various ray/patch intersection algorithms. The predominant single expense in most ray-patch intersection algorithms is de Casteljau subdivision. Our intersector spends \(45 \%\) of its time computing sub divisions. To split a projected two-dimensional bicubic patch in ei ther parameter direction requires 144 floating point operations. All previous subdivision-based algorithms can take advantage of this projection to \(R^{2}\) (which, as mentioned, saves \(33 \%\) of subdivision costs for non-rational and \(50 \%\) for rational patches). We compared the number of subdivisions per non-background pixel required by our algorithm with the algorithms of Toth[18] and Woodward[20]. To attain three digits accuracy in \(s, t\), Toth reported an average of 19.66 subdivisions for each non-background pixel in his Figure 6 (an example of a single patch in which roughly \(30 \%\) of non-background pixels involve two ray-patch intersections). We duplicated the patch and viewing parameters for Toth's Figure 6 as nearly as possible, and tested our and Woodward's algorithms. The average number of subdivisions per non-background pixel is listed in Table 1. SUN SPARCstation I CPU times for 120X120 image are shown in parenthesis.

It is difficult to make quantitative comparisons with the other published algorithms. Newton [17] and quasi-Newton [4] itera-

![Figure 2U](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-2u-p008.png)

*Figure 2U: leapot encased in deformed glass cube: 39 patches, 21.3*

![Figure 19](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-19-p008.png)

*Figure 19: Chain on patch-work quilt: 4024 patches. 18 back Modified teapot: 2304 patches, 64% background, 4.0 subdivisions ray, 12.5 cpu min. (8.6 min. primary rays only) background, 5.6 subdivisions ray, 29.0 cpu min. (17.6 min. primary rays only)*

![Figure 1X](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-1x-p008.png)

*Figure 1X: Modihed teapor: 2504 parches, 64% backeround. 4.0 Newell's teapot: 33 patches, 65% background, 5.2 subdivisions ray, 6.7 cpu min. (3.9 min. primary rays only)*

![Figure 21](/Users/evanthayer/Projects/stepview/docs/1990_ray_tracing_trimmed_rational_surface_patches/figures/figure-21-p008.png)

*Figure 21: House of mirrors Teapot encased in deformed glass cube: 39 patches, 21.3 cpu min on SUN SPAR Cstation I*

tion appear to converge quickly, but without actually implementing those algorithms, we cannot estimate the computational expense required to assure robustness.

### 4.3 Higher Degree Patches

This algorithm works on patches of arbitrary degree. However, since de Casteljau subdivision is an \(O\left(n^{3}\right)\) operation for surface patches, execution speed suffers as patch degree increases. A sam ple bicubic patch containing a silhouette curve took 50 cpu seconds to render with 11.4 subdivisions per pixel. After elevating that same patch to degree four, the rendering took 94 cpu seconds with 11.2 subdivisions per pixel. The subdivisions per pixel tends to decrease with degree because the control polygon approximates the patch more closely as degree elevation is applied. Table 2 tallies the exe cution speed for patches elevated up to degree eight.

Acknowledgements: The authors gratefully acknowledge the support of Professor Nakamae of Hiroshima University in providing access to his computer graphics lab. The second author was supported in part by the National Science Foundation under grant number DMC-8657057. This work originated while the first author was visiting Brigham Young University, on leave from Fukuyama University.

## References

- Böhm, Wolfgang, Farin, Gerald and Kahmann, Jurgen. A survey of curve and surface methods in CAGD. Computer Aided Geometric Design, 1, 1 (1984), 1-60.

- Farin, Gerald. Curves and Surfaces for Computer Aided Geometric Design, Academic Press, 1988.

- Glassner, Andrew ed., Introduction to Ray Tracing. Academic Press, 1989.

- Joy, Keneth and Bhetanabhotla, Murthy. Ray Tracing Para279-285.

- Joy, Kenneth, Grant, Charles Max, Nelson and Hatfield, Lansing. Computer Graphics: Image Synthesis. Computer Society Press, 1988.

- Kajiya, Jim. Ray tracing parametric patches. Proceedings of puter Graphics,16,3 (July 1982), 245-254.

- nomial Surfaces. IEEE Trans. RAMI,2 (1980), 35-46. Rockwood, Alyn, Heaton, Kurt and Davis, Tom. Real-Time Rendering of Trimmed Surfaces. Proceedings of SIGGRAPH '89 (Boston, MA, July 31-August 4, 1989). In Computer Graphics, 23, 3 (July 1989), 107-117. Rogers, Dave. Procedural Elements for Computer Graphics. McGraw-Hill, New York, 1985, 296-305. Roth, Scott. Ray Casting for Modeling Solids. Computer Graphics and Image Processing, 18, 1982, 109-144. Sederberg, Tom. An algorithm for Algebraic curve intersection. Computer-Aided Design, 21, 9 (1989), 547-554. Sederberg, Tom and Parry, Scott. A Comparison of Three curve intersection algorithms. Computer-Aided Design, 18, 1 (1986), 58-63. Sederberg, Tom and Parry, Scott. Free-Form Deformation of Solid Geometric Models. Proceedings of SIGGRAPH '86 (Dallas, TX, August 18-22, 1986). In Computer Graphics, 20, 4 (August 1986), 151-160. Sederberg, Tom, White, Scott and Zundel, Alan. Fat Arcs: A Bounding Region with Cubic Convergence. Computer Aidea Geometric Design, 6 (1989), 205-218. Shantz, Mike and Chang, Sheue-Ling. Rendering Trimmed NURBS with adaptive Forward Differencing. Proceedings of SIGGRAPH '88 (Atlanta, GA, August 1-5, 1988). In Computer Graphics, 22, 4 (August 1988), 189-198. Sweeney, Michael and Bartels, Richard. Ray Tracing FreeForm B-Spline Surfaces. IEEE CG&A, 6, 2, 1986, 41-49. Toth, Dan. On Ray Tracing Parametric Surfaces. Proceedings of SIGGRAPH '85 (San Francisco, CA, July 22-26, 1985). In Computer Graphics 19, 3 (July 1985), 171-179. Whitted, Turner. An Improved Illumination Model for Shaded Display. CACM, 23, 6, 1980, 96-102. Woodward, Charles. Ray Tracing Parametric Surfaces by Subdivision in Viewing Plane. in W. Strasser and H.-P. Seidel, editors, Theory and Practice of Geometric Modeling, Springer-Verlag, 1989, 273-290.
