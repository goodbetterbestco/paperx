# Curve Intersection Using Bezier Clipping

T W Sederberg, T Nishita*, CURVE CURVE INTERSECTION, Fukuyama, Japan

Engineering Computer Graphics Lab
Brigham Young University
Provo, UT 84602, USA

*Department of Electrical Engineering
Fukuyama University
Fukuyama, Japan

Engineering Computer Graphics Lab, Brigham Young University

Provo
UT 84602
USA

* Department of Electrical Engineering, Fukuyama University

## Abstract

Define a fat line as the region between two parallel lines. The curve intersection algorithm described here begins by computing a fat line which bounds one of the two Bezier curves. Similar bounds have been suggested in References 5, 6 and 7. Denote by I the line Po- Pr. A fat line is chosen parallel to L, as shown in Figure 1. If I is defined in its normalized implicit equation \begin{equation*} a x+b y+c=0 \quad\left(a^{2}+b^{2}=1\right) \tag{1} \end{equation*} then, the distance d(x, y) from any point (x, y) to E is Denote by d; = d (X;, Yi) the signed distance from control point P, = (X;, Yi) to L. By the convex hull property, a fat line bounding a given rational Bézier curve with non-negative weights can be defined as the fat line parallel to E which most tightly encloses the Bezier control points: \begin{equation*} \left\{(x, y) \mid d_{\min } \leqslant d(x, y) \leqslant d_{\max }\right\} \tag{3} \end{equation*} where dmax dmin L A technique referred to as Bézier clipping is presented. This technique forms the basis of an algorithm for computing the points at which two curves intersect, and also an algorithm for robustly and quickly computing points of tangency between two curves. Bézier clipping behaves like an intelligent interval Newton method, in which geometric insight is used to identity regions of the parameter domain which exclude the solution set. Implementation tests suggest that the curve intersection algorithm is marginally slower than an algorithm based on implicitization (though faster than other algorithms) for curves of degree four and less, and is faster than the implicitization algorithm for higher degrees. Bézier clipping, curve intersection, tangency, focus, polynomial, collinear normal algorithm \begin{equation*} d(x, y)=a x+b y+c \tag{2} \end{equation*} This paper presents algorithms to solve the problems of curve curve intersection and of locating points of tangency between two planar Bézier curves, based on a new technique which will be referred to as Bézier clipping. The basic strategy is to use the convex hull property of Bezier curves to identify regions of the curves which do not include part of the solution. By iteratively clipping away such regions, the solution is converged to at a quadratic rate and with a guarantee of robustness. Several papers have addressed the problem of planar Bézier curve curve intersection. Predominant approaches are the convex hull de Casteljau subdivisional algorithm', the interval subdivision method adapted by Koparkar and Mudur, and implicitization? Implementations of those algorithms have suggested that implicitization is easily the fastest of those algorithms for curves of degree less than five? For higher degrees, the interval algorithm is generally fastest. \begin{align*} & d_{\min }=\min \left\{d_{0}, \ldots, d_{n}\right\} \\ & d_{\max }=\max \left\{d_{0}, \ldots, d_{n}\right\} \tag{4} \end{align*} An algorithm for computing points of tangency between two parametric curves has recently been proposed, based on vector fields. In the next section the curve intersection algorithm based on Bézier clipping is discussed; then Bézier clipping is applied to the problem of computing points of tangency; this is followed by some timing comparisons; the final section is devoted to some concluding observations.

## Introduction

$$
\begin{equation*} d(t)=2 t(1-t) d_{1} \tag{5} \end{equation*}
$$

$$
\begin{equation*} \min \left\{0, d_{1}, d_{2}\right\} 3 t(1-t) \leqslant d(t) \leqslant \max \left\{0, d_{1}, d_{2}\right\} 3 t(1-t) \tag{12} \end{equation*}
$$

$$
\begin{align*} & d_{\min }=\min \left\{0, \frac{d_{1}}{2}\right\} \\ & d_{\max }=\max \left\{0, \frac{d_{1}}{2}\right\} \tag{6} \end{align*}
$$

$$
\begin{align*} & d_{\min }=\min \left\{0, d\left(t_{1}\right)\right\} \\ & d_{\max }=\max \left\{0, d\left(t_{1}\right)\right\} \tag{9} \end{align*}
$$

![Figure 2. Fat line for a polynomial quadratic curve](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-2-p002.png)

*Figure 2. Fat line for a polynomial quadratic curve: Figure 2. Fat line for a polynomial quadratic curve*

$$
\begin{align*} & d_{\min }=\min \left\{d\left(t_{1}\right), d\left(t_{2}\right)\right\} \\ & d_{\max }=\max \left\{d\left(t_{1}\right), d\left(t_{2}\right)\right\} \tag{11} \end{align*}
$$

$$
\begin{align*} & d_{\min }=\frac{3}{4} \min \left\{0, d_{1}, d_{2}\right\} \\ & d_{\max }=\frac{3}{4} \max \left\{0, d_{1}, d_{2}\right\} \tag{13} \end{align*}
$$

$$
\begin{equation*} d(t)=3 t(1-t)\left[(1-t) d_{1}+t d_{2}\right] \tag{7} \end{equation*}
$$

$$
\begin{equation*} 3 t(1-t)^{2} d_{1} \leqslant d(t) \leqslant 3 t^{2}(1-t) d_{2} \tag{14} \end{equation*}
$$

$$
\begin{equation*} t_{1}=\frac{d_{1}}{2 d_{1}-d_{2}+\sqrt{d_{1}^{2}-d_{1} d_{2}+d_{2}^{2}}} \tag{8} \end{equation*}
$$

$$
\begin{align*} d_{\min } & =\frac{4}{9} \min \left\{0, d_{1}, d_{2}\right\} \\ d_{\max } & =\frac{4}{9} \max \left\{0, d_{1}, d_{2}\right\} \tag{15} \end{align*}
$$

$$
\begin{align*} & t_{1}=\frac{2 d_{1}-d_{2}+\sqrt{d_{1}^{2}+d_{2}^{2}-d_{1} d_{2}}}{3\left(d_{1}-d_{2}\right)} \\ & t_{2}=\frac{2 d_{1}-d_{2}-\sqrt{d_{1}^{2}+d_{2}^{2}-d_{1} d_{2}}}{3\left(d_{1}-d_{2}\right)} \tag{10} \end{align*}
$$

![Figure 3. Fat lines for polynomial cubic curves](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-3-p002.png)

*Figure 3. Fat lines for polynomial cubic curves: Figure 3. Fat lines for polynomial cubic curves*

![Figure 4. Bézier curve/tat line intersection](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-4-p003.png)

*Figure 4. Bézier curve/tat line intersection: Figure 4. Bézier curve/tat line intersection Figure 4. Bézier curve fat line intersection*

of \(t\) for which \(\mathbf{P}(t)\) lies outside of \(\mathbf{L}\), and hence for which \(\mathbf{P}(t)\) does not intersect \(\mathbf{Q}(u)\).

## P is defined by its parametric equation

$$
\begin{equation*} \mathbf{P}(t)=\sum_{i=0}^{n} \mathbf{P}_{i} B_{i}^{n}(t) \tag{16} \end{equation*}
$$

where \(\mathbf{P}_{i}=\left(x_{i}, y_{i}\right)\) are the Bézier control points, and \(B_{i}^{n}(t)=\binom{n}{i}(1-t)^{n-i} t^{i}\) denote the Bernstein basis functions. If the line \(\bar{L}\) through \(\mathbf{P}_{0}-\mathbf{P}_{n}\) is defined by then the distance \(d(t)\) from any point \(\mathbf{P}(t)\) to \(\bar{L}\) can be found by substituting equation (16) into equation (17):

Note that \(d(t)=0\) for all values of \(t\) at which \(\mathbf{P}\) intersects \(\bar{L}\). Also, \(d_{i}\) is the distance from \(\mathbf{P}_{i}\) to \(\bar{L}\) (as shown in Figure 4). The function \(d(t)\) is a polynomial in Bernstein form, and can be represented as a so-called 'non-parametric' Bézier curve \({ }^{8}\) as follows:

$$
\begin{equation*} \mathbf{D}(t)=(t, d(t))=\sum_{i=0}^{n} \mathbf{D}_{i} B_{i}^{n}(t) \tag{19} \end{equation*}
$$

Since \(\sum_{i=0}^{n}(i / n) B_{i}^{n}(t) \equiv t[(1-t)+t]^{n} \equiv t\), Values of t for which \(P(t)\) lies outside of L correspond to values of t for which \(D(t)\) lies above d = dmax or below d = dmin. Parameter ranges of t can be identified for which \(P(t)\) is guaranteed to lie outside of L by identifying ranges of t for which the convex hull of Dit) lies above d = dmax or below d = dminIn this example, it is certain that \(P(t)\) lies outside of L for parameter values t < 0.25 and for t > 0.75. Bézier clipping is completed by subdividing \(\mathbf{P}\) twice using the de Casteljau algorithm \({ }^{8}\), such that portions of \(\mathbf{P}\) over parameter values \(t<0.25\) and \(t>0.75\) are removed.

![Figure 5. Non-parametric Bézier curve](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-5-p003.png)

*Figure 5. Non-parametric Bézier curve: Figure 5. Non-parametric Bézier curve*

$$
\begin{equation*} a x+b y+c=0 \quad\left(a^{2}+b^{2}=1\right), \tag{17} \end{equation*}
$$

![Figure 71. From Figure 6, it is concluded that it is safe](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-71-p003.png)

*Figure 71. From Figure 6, it is concluded that it is safe: Figure 71. From Figure 6, it is concluded that it is safe*

$$
\begin{equation*} d(t)=\sum_{i=0}^{n} d_{i} B_{i}^{n}(t), \quad d_{i}=a x_{i}+b y_{i}+c \tag{18} \end{equation*}
$$

After three Bézier clips on each curve, the intersection is computed to within six digits of accuracy (see Table

Clipping to other fat lines The fat line defined above provides a nearly optimal Bézier clip in many cases. However, it is clear that any pair of parallel lines which bound the curve can serve as a fat line. In many cases, a fat line perpendicular to the line \(\mathbf{P}_{0}-\mathbf{P}_{n}\) provides a larger Bézier clip than does the fat line parallel to the line \(\mathbf{P}_{0}-\mathbf{P}_{n}\). Figure 8 shows

![Figure 6. After the first Bézier clip](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-6-p004.png)

*Figure 6. After the first Bézier clip: Figure 6. After the first Bézier clip*

![Figure 7. Distance from Q(u) to I](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-7-p004.png)

*Figure 7. Distance from Q(u) to I: Figure 7. Distance from Q(u) to I L*

such a case. It is suggested that in general it works best to examine both fat lines to determine which one provides the largest clip. This extra overhead results in a slightly lower average execution time.

![Figure 8. Alternative fat lines](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-8-p004.png)

*Figure 8. Alternative fat lines: Figure 8. Alternative fat lines Table 1. Parameter ranges for P(t) and Q (u)*

![Figure 9. Two intersections](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-9-p004.png)

*Figure 9. Two intersections: Figure 9. Two intersections*

![Figure 10. Two intersections after a split](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-10-p005.png)

*Figure 10. Two intersections after a split: Figure 10. Two intersections after a split*

curve by at least 20%, subdivide the 'longest' curve (largest remaining parameter interval) and intersect the shorter curve, respectively, with the two halves of the longer curve. This heuristic, applied recursively if needed, allows computation of arbitrary numbers of intersections. Rational curves

If \(\mathbf{P}\) is a rational Bézier curve

$$
\begin{equation*} \mathbf{P}(t)=\frac{\sum_{i=0}^{n} w_{i} \mathbf{P}_{i} B_{i}^{n}(t)}{\sum_{i=0}^{n} w_{i} B_{i}^{n}(t)} \tag{20} \end{equation*}
$$

with control point coordinates \(\mathbf{P}_{i}=\left(x_{i}, y_{i}\right)\) and corresponding non-negative weights \(w_{i}\), the Bézier clip computation is modified as follows. Substituting equation (20) into equation (17) and clearing the denominator yields:

However, unlike the non rational case, the intersection of \(\mathbf{P}(t)\) with a fat line cannot be represented as \(\left\{(x, y)=\mathbf{P}(t) \mid d_{\text {min }} \leqslant d(t) \leqslant\right. d_{\text {max }}\) \}. Instead, \(\mathbf{P}\) must be clipped independently against each of the two lines bounding the fat line. Thus, ranges of \(t\) are identified for which

$$
\sum_{i=0}^{n} w_{i}\left(a x_{i}+b y_{i}+c-d_{\max }\right) B_{i}^{n}(t)>0
$$

$$
\sum_{i=0}^{n} w_{i}\left(a x_{i}+b y_{i}+c+d_{\min }\right) B_{i}^{n}(t)<0
$$

These ranges are identified using the Bézier clipping technique as previously outlined.

$$
\begin{aligned} & d(t)=\sum_{i=0}^{n} d_{i} B_{i}^{n}(t) \\ & d_{i}=w_{i}\left(a x_{i}+b y_{i}+c\right) \end{aligned}
$$

![Figure 11. Collinear normal line](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-11-p005.png)

*Figure 11. Collinear normal line: Figure 11. Collinear normal line*

![Figure 12. Tangent intersection](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-12-p006.png)

*Figure 12. Tangent intersection: Figure 12. Tangent intersection*

$$
\left[\begin{array}{ll} x_{1}-x_{0} & x_{n-1}-x_{n} \tag{21}\\ y_{0}-y_{1} & y_{n}-y_{n-1} \end{array}\right]\left\{\begin{array}{l} c_{0} \\ c_{1} \end{array}\right\}=\left\{\begin{array}{l} y_{n}-y_{0} \\ x_{n}-x_{0} \end{array}\right\}
$$

The focus construction proceeds as follows. If \(\mathbf{N}(t)\) defines any vector function (not necessarily of unit length) which is perpendicular to \(\mathbf{P}(t)\) for all values of \(t\), then the curve \(\mathbf{F}(t)=\mathbf{P}(t)+c(t) \mathbf{N}(t)\) (where \(c(t)\) is any function of \(t\) ) can serve as a focus curve. is itself a Bézier curve of degree \(n-1\), whose control points \(\mathbf{H}_{i}\) are \(n\left(\mathbf{P}_{i+1}-\mathbf{P}_{i}\right)\) (see Figure 16). This discussion deals only with hodographs and foci of polynomial curves. Hodographs of rational Bézier curves are discussed in Reference 12, following which the construction of a focus parallels the present discussion. Graphically, the tangent vector \(\mathbf{P}^{\prime}(t)\) is expressed as a vector from the hodograph origin to the point \(\mathbf{H}(t)\) on the hodograph (see Figure 17). By rotating the hodograph through \(90^{\circ}\) about its origin, a vector function \(\mathbf{N}(t)\) is obtained which defines vectors perpendicular to \(\mathbf{P}(t)\) (see Figure 18). In creating the focus \(\mathbf{F}(t)=\mathbf{P}(t)+c(t) \mathbf{N}(t), c(t)\) is chosen to be a degree-one polynomial \(c_{0}(1-t)+c_{1} t\) which satisfies the condition \(\mathbf{F}(0)=\mathbf{F}(1)\). This is a heuristic decision, motivated by the observation that if \(\mathbf{F}(t)\) begins and ends at the same point, it will tend to cover a relatively small area. The examples in Figures 13-15 illustrate that this choice generally works well. The coefficients \(c_{0}\) and \(c_{1}\) are solved from the linear equation

![Figure 13. Focus example 1](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-13-p006.png)

*Figure 13. Focus example 1: Figure 13. Focus example 1*

![Figure 14. Focus example 2](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-14-p007.png)

*Figure 14. Focus example 2: Figure 14. Focus example 2*

![Figure 15. Focus example 3](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-15-p007.png)

*Figure 15. Focus example 3: Figure 15. Focus example 3*

Thus, even curves with inflection points (as in Figure 14) can have a reasonable focus. This focus construction behaves well when the curve is subdivided into smaller segments, quickly converging to the centre of curvature of their respective curve segments. Thus, even though a curve may initially have an impracticably large focus, the size of the focus will shrink quickly as the curve is subdivided. Figures 19 and 20 show the curve in Figure 15 after it has been split into two and four segments. The resulting foci appear nearly optimally small.

Other focus heuristics After some experimentation, the authors are confident that the focus heuristic is competitive. A few other choices present themselves. first, one could simply compute a line segment through which all lines normal to a given curve pass. This has the virtue that the focus

![Figure 16. Curve and hodograph](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-16-p007.png)

*Figure 16. Curve and hodograph: Figure 16. curve and hodograph*

![Figure 17. Tangent vector](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-17-p007.png)

*Figure 17. Tangent vector: Figure 17. Tangent vector*

is a simpler entity than our degree \(n\) focus, but more computation must go into computing the focus. A second choice is to use the evolute \({ }^{13}\) of the given curve as its focus. The evolute is the locus of the centres

![Figure 18. Rotated hodograph, N(t)](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-18-p008.png)

*Figure 18. Rotated hodograph, N(t): Figure 18. Rotated hodograph, N(t)*

![Figure 19. Curve of Figure 15 (left) split into two segments](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-19-p008.png)

*Figure 19. Curve of Figure 15 (left) split into two segments: Figure 19. curve of Figure 15 (left) split into two segments*

$$
\begin{equation*} d_{i}=\sum_{\substack{i+k=i \\ j \in\{0, \ldots, n\} \\ k \in\{0, \ldots, n-1\}}} \frac{\binom{n}{j}\binom{n-1}{k}}{\binom{2 n-1}{i}} n\left(\mathbf{P}_{k+1}-\mathbf{P}_{k}\right) \cdot\left(\mathbf{P}_{j}-\mathbf{F}\right) \tag{23} \end{equation*}
$$

$$
\begin{equation*} d(t)=\mathbf{P}^{\prime}(t) \cdot(\mathbf{P}(t)-\mathbf{F})=0 \tag{22} \end{equation*}
$$

![Figure 20. Curve of Figure 15 split into four segments](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-20-p008.png)

*Figure 20. Curve of Figure 15 split into four segments: Figure 20. curve of Figure 15 split into four segments*

![Figure 23. P. Q and Fa](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-23-p009.png)

*Figure 23. P. Q and Fa: Figure 23. P. Q and Fa*

![Figure 21. Normal to P(t) passing through F](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-21-p009.png)

*Figure 21. Normal to P(t) passing through F: Figure 21. Normal to P(t) passing through F*

$$
\begin{equation*} d_{i j}=\sum_{\substack{k+1=i \\ 1 \in\{0, \ldots, n\} \\ k \in\{0, \ldots, n-1\}}} \frac{\binom{n}{j}\binom{n-1}{k}}{\binom{2 n-1}{j}} n\left(\mathbf{P}_{k+1}-\mathbf{P}_{k}\right) \cdot\left(\mathbf{P}_{l}-\mathbf{F}_{j}\right) \tag{26} \end{equation*}
$$

$$
\begin{equation*} d(t, \dot{u})=\sum_{i=0}^{2 n-1} \sum_{j=0}^{m} B_{i}^{2 n-1}(t) B_{j}^{m}(u) d_{i j} \tag{25} \end{equation*}
$$

![Figure 24. Top view of D(t, u) patch](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-24-p009.png)

*Figure 24. Top view of D(t, u) patch: Figure 24. Top view of D(t, u) patch*

![Figure 22. Non-parametric Bézier curve](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-22-p009.png)

*Figure 22. Non-parametric Bézier curve: Figure 22. Non-parametric Bézier curve*

$$
\begin{equation*} D(t, u)=\left(\mathbf{P}(t)-\mathbf{F}_{\mathbf{Q}}(u)\right) \cdot \frac{\mathbf{P}^{\prime}(t)}{n} \neq 0,0 \leqslant u \leqslant 1 \tag{24} \end{equation*}
$$

\(D(t, u)\) can be expressed as a tensor product polynomial in Bernstein form in \(t\) and \(u\) :

![Figure 27. Q after first clipping, and its focus](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-27-p010.png)

*Figure 27. Q after first clipping, and its focus: Figure 27. Q after first clipping, and its focus*

$$
\begin{align*} \mathbf{D}(t, u) & =\sum_{i=0}^{2 n-1} \sum_{i=0}^{m} B_{i}^{2 n-1}(t) B_{j}^{m}(u) \mathrm{D}_{i j} \\ & =(t, u, d(t, u)) \tag{27} \end{align*}
$$

![Figure 25. Side view of D(t, u) patch](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-25-p010.png)

*Figure 25. Side view of D(t, u) patch: Figure 25. Side view of D(t, u) patch*

![Figure 26. P after first clipping, and its focus](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-26-p010.png)

*Figure 26. P after first clipping, and its focus: Figure 26. P after first clipping, and its focus*

$$
\( u_{i j}=j / m \). A point on such a patch has coordinates
$$

The top view of the patch \(\mathbf{D}(t, u)\) corresponding to Figure 23 is shown in Figure 24. A side view of the \(\mathbf{D}(t, u)\) patch, looking down the \(u\) axis, is shown in Figure 25. In this side view, portions of \(\mathbf{D}(t, u)\) which are completely above or beneath the \(t\)-axis correspond to portions of \(\mathbf{P}(t)\) for which no normal line intersects any point on \(\mathbf{F}_{\mathbf{Q}}(u)\). In Figure 25, the convex hull of the projected control points bounds the projection of the \(\mathbf{D}(t, u)\) patch. Therefore, it is certain that regions of the \(t\)-axis which lie completely outside the convex hull of the projected \(\mathbf{D}(t, u)\) control points represent portions of \(\mathbf{P}(t)\) for which no normal line intersects any point on \(\mathbf{F}_{\mathbf{Q}}(u)\). In this example, that convex hull intersects the \(t\)-axis at points \(t_{\text {min }}=0.3020\) and \(t_{\text {max }}=0.7712\). It is concluded that \(d(t, u) \neq 0\), and therefore lines normal to \(\mathbf{P}(t)\) do not intersect any point on \(\mathbf{F}_{\mathbf{Q}}(u)\), for \(t<0.3020\) and \(t>0.7712\).

Collinear normal algorithm All the tools have now been gathered to create an algorithm for computing all lines which are simultaneously perpendicular to two curves. Continuing the example in the previous subsection, we clip away portions of \(\mathbf{P}\) which do not have normals through \(\mathbf{F}_{\mathbf{Q}}\). Those portions are shown in fine pen width in Figure 26. Next, compute a focus for the remaining segment of \(\mathbf{P}\), as shown in Figure 26, and clip away regions of \(\mathbf{P}\) whose normal lines do not pass through \(\mathbf{Q}^{\prime}\) 's focus. The remaining portion of \(\mathbf{P}\) is shown in heavy pen width in Figure 27, and also its focus \(\mathbf{F}_{\mathbf{p}}\). This iteration continues as recorded in Table 2. After four iterations, the point of tangency is actually determined to eight digits of accuracy. If an iteration fails to reduce the parameter range of either curve by at least, say, 20%, there may be more than one collinear normal. The remedy is to split one f the curves in half and to compute the colline ormals of each half with the other curve, using a stac data structure to store pairs of curve segments. TIMING COMPARISONS The Bézier trim curve intersection algorithm has been implemented and some timing comparisons have been

![Figure 28. Degree-three example](/Users/evanthayer/Projects/stepview/docs/1990_curve_intersection_using_bezier_clipping/figures/figure-28-p011.png)

*Figure 28. Degree-three example: Figure 28. Degree-three example Table 3. Relative computation times*

Our experience is that, for curves of degree less than five, the implicitization algorithm is typically between one and three times faster than the Bézier clip algorithm, which in turn is typically between two and ten times faster than the other two algorithms. For curves of degree higher than four, the Bézier clipping algorithm generally wins. The algorithm for computing tangent intersections can typically compute a tangent intersection faster than the Bézier clip curve intersector can compute two well-spaced simple intersections. The algorithm for computing tangent intersections is designed for firstorder tangencies, and its performance degrades for higher-order tangencies.

## Acknowledgements

The first-named author was supported in part by the National Science Foundation under grant DMC-8657057.

## References

- 1 Lane, | M and Riesenfeld, R 'A theoretical development for the computer generation ana display of piecewise polynomial surfaces' IEEE Trans. RAMI Vol 2 (1980) pp 35-46

- 2 Koparkar, P A and Mudur, S P 'A new class of algorithms for the processing of parametric curves' Comput.-Aided Des. Vol 15 (1983) pp 41-45

- 3 Sederberg, T W and Parry, S R 'Comparison of three curve intersection algorithms' Comput.-Aided Des. Vol 18 (1986) pp 58-634 Markot, R P and Magedson, R L 'Solutions of tangential surface and curve intersections' Comput.Aided Des. Vol 21 (1989) pp 421-4275 Ballard, D H 'Strip trees: a hierarchical representation for curves' Comm. ACM Vol 24 (1981) pp 310-3216 Carlson, W E 'An algorithm and data structure for 3-D object synthesis using surface patch intersections' Computer Graphics Vol 16 No 3 (1982) pp 255-2637 Sederberg, T W, White, S C and Zundel, A K 'Fat arcs: A bounding region with cubic convergence' Comput. Aided Geometric Des. Vol 6 (1989) pp 205-2188 Farin, G curves and Surfaces for Computer Aided Geometric Design, Academic Press 1988) 9 Böhm, W, Farin, G and Kahmann, J 'A survey of curve and surface methods in CAGD' Comput. Aided Geometric Des. Vol 1 (1984) pp 1-6010 Sederberg, T W, Christiansen, H N and Katz, S 'Improved test for closed loops in surface intersections' Comput.-Aided Des. Vol 21 (1989) pp 11 Bézier, P The Mathematical Basis of the UNISURF CAD System Butterworths, UK (1986) 12 Sederberg, T W and Wang, X 'Rational hodographs' Comput. Aided Geometric Des. Vol 4(1987) pp 333-33513 Salmon, G Higher Plane curves, G E Stechert & Co (1934)
