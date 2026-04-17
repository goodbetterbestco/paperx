# Computing Exact Aspect Graphs of Curved Objects: Algebraic Surfaces

Jean Ponce x, Sylvain Petitjean, David J. Kriegman ~, Algebraic Surfaces*

Dept. of Computer Science, University of Illinois, Urbana, IL 61801, USA
Dept. of Electrical Engineering, Yale University, New Haven, CT 06520, USA

## Abstract

This paper presents an algorithm for computing the exact aspect graph of an opaque solid bounded by a smooth algebraic surface and observed under orthographic projection. The algorithm uses curve tracing, cell decomposition, and ray tracing to construct the regions of the view sphere delineated by visual events. It has been fully implemented, and examples are presented.

## 1 Introduction

The aspect graph [25] is a qualitative, viewer-centered representation that enumerates all possible appearances of an object: The range of all possible viewpoints is partitioned into maximal regions such that the structure of the image contours, also called the aspect, is the same from every viewpoint in a region. The change in the aspect at the boundary between regions is named a visual event. The maximal regions and their boundaries are organized into a graph, whose nodes represent the regions with their associated aspects and whose ares correspond to the visual event boundaries between adjacent regions.

Since their introduction by Koenderink and Van Doom [25] more than ten years ago, aspect graphs have been the object of very active research. The main focus has been on polyhedra, whose contour generators are viewpoint-independent. Indeed, approximate aspect graphs of polyhedra have been successfully used in recognition tasks [7, 18, 20], and several algorithms have been proposed for computing the exact aspect graph of these objects [6, 15, 16, 31, 36, 38, 39, 41, 42].

Recently, algorithms for constructing the exact aspect graph of simple curved objects such as solids bounded by quadric surfaces [8] and solids of revolution [11, 12, 26] have also been introduced. For more complex objects, it was recognized from the start that the necessary theoretical tools could be found in catastrophe theory [1, 5, 25]. However, algorithms based on these tools have, until very recently, remained elusive: Koenderink [24] and Kergosien [23] show the view sphere curves corresponding to the visual events of some surfaces, but, unfortunately, neither author details the algorithm used to compute these curves. Rieger [35] uses cylindrical algebraic decomposition to compute the aspect graph of a quartic surface of the form z = f(z, y).

This paper is the third in a series on the construction of exact aspect graphs of smooth objects, based on the catalogue of possible visual events established by Kergosien [22] (see [33, 40] for the case of piecewise-smooth objects). Previously, we presented a fully implemented algorithm for solids of revolution whose generating curve is polynomial [26] (see [11, 12] for a different approach to the same problem), and reported preliminary results for polynomial parametric surfaces [32]. Here, we present a fully implemented algorithm for computing the aspect graph of an opaque solid bounded by parametric or

* This work was supported by the National Science Foundation under Grant IRI-9015749.

implicit smooth algebraic surfaces, observed under orthographic projection (see [23, 24, 35, 37] for related approaches).

This algorithm is described in Sect. 3. It relies on a combination of symbolic and numerical techniques, including curve tracing and cell decomposition [29], homotopy continuation [30], and "symbolic" ray tracing [21, 28]. An implementation is described in Sect. 4, and examples are presented (Figs. 4,5). Finally, future research directions are briefly discussed in Sect. 5. While the main ideas of our approach are presented in the body of the paper, detailed equations and algorithms are relegated to four appendices.

## 2 Visual Events

Let us start by reviewing some results from catastrophe theory [1]: From most viewpoints, the image contours of smooth surfaces are piecewise-smooth curves whose only singularities are cusps and t-junctions. The contour structure is in general stable with respect to viewpoint, i.e., it does not change when the camera position is submitted to a small perturbation. From some viewpoints, however, almost any perturbation of the viewpoint will alter the contour topology. A catalogue of these "visual events" has been established by Kergosien [22] for transparent generic smooth surfaces observed under orthographic projection (Fig. 1).

![Figure 1. Visual events, a. Local events. From top to bottom](/Users/evanthayer/Projects/paperx/docs/1992_computing_exact_aspect_graphs_of_curved_objects_algebraic_surfaces/figures/figure-1-p002.png)

*Figure 1. Visual events, a. Local events. From top to bottom: swallowtail, beak-to-beak, lip. b. Multilocal events. From top to bottom: triple point, tangent crossing, and cusp crossing.*

Each visual event in this catalogue occurs when the viewing direction has high order contact with the observed surface along certain characteristic curves [1, 24]. When contact occurs at a single point on the surface, the event is said to be local; when it occurs at multiple points, it is said to be multilocal. A catalogue of visual events is also available for piecewise-smooth surfaces [33, 40], but we will restrict our discussion to smooth surfaces in the rest of this paper.

### 2.1 Local Events

As shown in [22], smooth surfaces may exhibit three types of local events: swallowtail, beak-to-beak, and lip transitions (Fig. 1.a). During a swallowtail transition, a smooth image contour forms a singularity and then breaks off into two cusps and a t-junction. In a beak-to-beak transition, two distinct portions of the occluding contour meet at a point in the image. After meeting, the contour splits and forms two cusps; the connectivity of the contour changes. Finally, a lip transition occurs when, out of nowhere, a closed contour is formed with the introduction of two cusps.

Swallowtails occur on flecnodal curves, and both beak-to-beak and lip transitions occur on parabolic curves [1, 24]. Flecnodal points are inflections of asymptotic curves, while parabolic points are zeros of the Gaussian curvature. Equations for the parabolic and flecnodal curves of parametric and implicit surfaces are given in Appendices A.1 and B.1 respectively. The corresponding viewing directions are asymptotic directions along these curves.

### 2.2 Multilocal Events

These events occur when two or more surface points project onto the same contour point. As shown in [22], there are three types of multilocal events: triple points, tangent crossings, and cusp crossings (Fig. 1.b). A triple point is formed by the intersection of three contour segments. For an opaque object, only two branches are visible on one side of the transition while three branches are visible on the other side. A tangent crossing occurs when two contours meet at a point and share a common tangent. Finally, a cusp crossing occurs when the projection of a contour cusp meets another contour.

A multilocal event is characterized by a curve defined in a high dimension space, or equivalently by a family of surface curves. For example, a triple point is formed when three surface points are aligned and, in addition, the surface normals at the three points are all orthogonal to the common line supporting these points. By sweeping this line while maintaining three-point contact, a family of three curves is drawn on the surface. Equations for the families of surface curves corresponding to multilocal events are given in Appendices A.2 and B.2 for parametric and implicit surfaces respectively. The corresponding viewing directions are parallel to the lines supporting the points forming the events.

## 3 The Algorithm

We propose the following algorithm for constructing the aspect graph of an opaque solid bounded by an algebraic surface:

- Trace the visual event curves.

- Eliminate the occluded events.

- Construct the regions delineated on the view sphere by the remaining events.

- Construct the corresponding aspects.

We now detail each step of the algorithm. Note that the aspect graph of a transparent solid can be constructed by using the same procedure but omitting step 2.

### 3.1 Step 1: Tracing Visual Events

As shown in Sect. 2, a visual event corresponds in fact to two curves: a curve (or family of curves) \(\Gamma\) drawn on the object surface and a curve \(\Delta\) drawn on the view sphere.

For algebraic surfaces, the curve \(\Gamma\) is defined implicitly in \(\mathbb{R}^{n+1}\) by a system of \(n\) polynomial equations in \(n+1\) unknowns, with \(1 \leq n \leq 8\) (see Appendices A and B):

$$
\left\{\begin{array}{l} P_{1}\left(X_{0}, X_{1}, \ldots, X_{n}\right)=0, \\ \ldots \\ P_{n}\left(X_{0}, X_{1}, \ldots, X_{n}\right)=0 . \end{array}\right.
$$

To trace a visual event, we first trace \(\Gamma\) in \(\mathbb{R}^{n+1}\). We then trace \(\Delta\) by mapping points of \(\Gamma\) onto points of \(\Delta\) : given a point on \(\Gamma\), the corresponding point on \(\Delta\) is an asymptotic direction for local events, or the direction of the line joining two surface points for multilocal events.

The curve tracing algorithm is decomposed into the following steps (Fig. 2): 1.1. Compute all extremal points of \(\Gamma\) in some direction, say \(X_{0}\) (this includes all singular points). 1.2. Compute all intersections of \(\Gamma\) with the hyperplanes orthogonal to the \(X_{0}\) axis at the extremal points. 1.3. For each interval of the \(X_{0}\) axis delimited by these hyperplanes, intersect \(\Gamma\) and the hyperplane passing through the mid-point of the interval to obtain one sample for each real branch. 1.4. March numerically from the sample points found in step 1.3 to the intersection points found in step 1.2 by predicting new points through Taylor expansion and correcting them through Newton iterations.

![Figure 2. An example of curve tracing in ~2. This curve has two extremal points El, E~, and four regular branches with sample points $1 to $4; note that E2 is singular.](/Users/evanthayer/Projects/paperx/docs/1992_computing_exact_aspect_graphs_of_curved_objects_algebraic_surfaces/figures/figure-2-p004.png)

*Figure 2. An example of curve tracing in ~2. This curve has two extremal points El, E~, and four regular branches with sample points $1 to $4; note that E2 is singular.: An example of curve tracing in ~2. This curve has two extremal points El, E~, and four regular branches with sample points $1 to $4; note that E2 is singular.*

This algorithm overcomes the main difficulties of curve tracing, namely finding a sample point on every real branch and marching through singularities. Its output is a graph whose nodes are extremal or singular points on \(\Gamma\) and whose arcs are discrete approximations of the smooth curve branches between these points. This graph is similar to the s-graph representation of plane curves constructed through cylindrical algebraic decomposition [2]. Using the mapping from \(\Gamma\) onto \(\Delta\), a discrete approximation of the curve \(\Delta\) is readily constructed.

Technical Details. We now detail the computations involved in the curve tracing algorithm. The casual reader may want to skip the rest of this section, at least on first reading, and jump ahead to Sect. 3.2.

Step 1.1 requires the computation of the extrema of \(\Gamma\) in the \(X_{0}\) direction. As shown in Appendix C, these points are the solutions of the system of \(n+1\) polynomial equations in \(n+1\) unknowns obtained by adding the equation \(|J|=0\) to system (1). Here, \(J\) is the Jacobian matrix ( \(\partial P_{i} / \partial X_{j}\) ), with \(i, j=1, . ., n\). Steps 1.2 and 1.3 require computing the intersections of a curve with a hyperplane, and these points are once again the solutions of a system of polynomial equations. We use the homotopy continuation method, as described in Appendix D, to solve these equations.

The curve is actually traced in step 1.4, using a classical prediction/correction approach based on a Taylor expansion of the \(P_{i}\) 's [4, 13]. As shown in Appendix C, this involves inverting the matrix J which is guaranteed to be nonsingular on extrema-free intervals. Note that all real branches can be traced in parallel. As shown in Appendix D, finding the extrema of the curve and its intersections with a family of hyperplanes is a parallel process too.

There is no conceptual difficulty in applying this algorithm to aspect graph construction, but there is a very practical problem: the visual events are defined by very high degree algebraic urves, and tracing them requires solving systems of equations that may have millions of roots. We will come back to this problem in Sect. 4.

### 3.2 Step 2: Eliminating Occluded Events

All visual events of the transparent object are found in step 1 of the algorithm. For an opaque object, some of these events will he occluded, and they should be eliminated. The visibility of an event curve F can be determined through ray tracing at its sample point found in step 1.3 [21, 44].

### 3.3 Step 3: Constructing the Regions

To construct the aspect graph regions delineated by the curves A on the view sphere, we refine the curve tracing algorithm into a cell decomposition algorithm whose output is a description of the regions, their boundary curves, and their adjacency relationships. Note that this refinement is only possible for curves drawn in two-dimensional spaces such as the sphere.

The algorithm is divided into the following steps (Fig. 3): 3.1. Compute all extremal points of the curves in the \(X_{0}\) direction. 3.2. Compute all the intersection points between the curves. 3.3. Compute all intersections of the curves with the "vertical" lines orthogonal to the \(X_{0}\) axis at the extremal and intersection points. 3.4. For each interval of the \(X_{0}\) axis delimited by these lines, do the following: 3.4.1. Intersect the curves and the line passing through the mid-point of the interval to obtain a sample point on each real branch of each curve. 3.4.2. Sort the sample points in increasing \(X_{1}\) order. 3.4.3. March from the sample points to the intersection points found in step 3.3. 3.4.4. Two consecutive branches within an interval of \(X_{0}\) and the vertical segments joining their extremities bound a region.

A sample point can be found for each region as the mid-point of the sample points of the bounding curve branches. This point is used to construct a representative aspect in Sect. 3.4. Maximal regions are found by merging all regions adjacent along a vertical line segment (two regions are adjacent if they share a common boundary, i.e., a vertical line segment or a curve branch).

Technical Details. We now detail the computations involved in the cell decomposition algorithm. Again, the casual reader may want to skip the rest of this section, and jump ahead to Sect. 3.4.

In our application, the coordinates \(X_{0}, X_{1}\) define a parameterization of the view sphere, such as spherical angles. Also, the curve \(\Delta\) corresponding to a visual event is not explicitly defined by polynomial equations. As shown in Appendices A and B, it is actually possible to augment the polynomial equations defining \(\Gamma\) to construct a new algebraic curve \(\Omega\) defined in \(\mathbb{R}^{m+1}\), with \(m>n\), such that \(\Delta\) is the projection of \(\Omega\) onto

![Figure 3. An example of cell decomposition. Two curves are shown, with their extremal points Ei and their intersection points Is; the shaded rectangle delimited by I1 and I2 is divided into five regions with sample points $1 to $5; the region corresponding to $3 is shown in a darker shade.](/Users/evanthayer/Projects/paperx/docs/1992_computing_exact_aspect_graphs_of_curved_objects_algebraic_surfaces/figures/figure-3-p006.png)

*Figure 3. An example of cell decomposition. Two curves are shown, with their extremal points Ei and their intersection points Is; the shaded rectangle delimited by I1 and I2 is divided into five regions with sample points $1 to $5; the region corresponding to $3 is shown in a darker shade.: An example of cell decomposition. Two curves are shown, with their extremal points Ei and their intersection points Is; the shaded rectangle delimited by I1 and I2 is divided into five regions with sample points $1 to $5; the region corresponding to $3 is shown in a darker shade.*

The extrema of \(\Delta\) in the \(X_{0}\) direction are the projections of the extrema of \(\Omega\) in this direction, and they can be found by solving a system of \(m+1\) equations in \(m+1\) unknowns through continuation. Similarly, the intersections of two curves \(\Delta_{1}\) and \(\Delta_{2}\) can be found by writing that \(\Omega_{1}\) and \(\Omega_{2}\) must project onto the same point in \(\mathbb{R}^{2}\) and by solving the corresponding system of \(2 m\) equations in \(2 m\) unknowns. Marching along \(\Delta\) is achieved by marching along \(\Omega\) and projection onto the \(\mathbb{R}^{2}\) plane.

An alternative is to first localize candidate regions of the view sphere where extrema and intersections may occur (using, for example, an adaptive subdivision of the sphere) and to converge to the actual points through local numerical optimization using the equations defining the visual events. This method does not involve the costly resolution of large sets of polynomial equations. A simpler version of this method is to directly work with the discrete approximations of the curves A obtained in step 1. This is the method we have actually used in the implementation described in Sect. 4.

### 3.4 Step 4: Constructing the Aspects

This step involves determining the contour structure of a single view for each region, first for the transparent object, then for the opaque object. This can be done through "symbolic" ray tracing of the object contour [28] as seen from the sample point of the region. Briefly, the contour structure is found using the curve tracing algorithm described earlier. Since contour visibility only changes at the contour singularities found by the algorithm, it is determined through ray tracing [21, 44] at one sample point per regular branch.

## 4 Implementation and Results

The algorithm described in Sect. 3 has been fully implemented. Tracing the visual event curves (step 1) is by far the most expensive part of the algorithm. curve tracing and continuation are parallel processes that can be mapped onto medium-grained MIMD architectures. We have implemented continuation on networks of Sun SPARC Stations communicating via Ethernet, networks of INMOS Transputers, and Intel Hypercubes. In practice, this allows us to routinely solve systems with a few thousands of roots, a task

![Figure 4. A few objects and their aspect graphs](/Users/evanthayer/Projects/paperx/docs/1992_computing_exact_aspect_graphs_of_curved_objects_algebraic_surfaces/figures/figure-4-2-p008.png)

*Figure 4. A few objects and their aspect graphs: a. A parametric surface, b. A bean-shaped implicit surface, c. A squash-shaped implicit surface, d. A "dimpled" implicit surface.*

The objects considered in the next three examples are described by smooth compact implicit surfaces of degree 4. The full aspect graph has been computed. Note that it has the structure predicted in [5, 24] for similarly shaped surfaces.

What do these results indicate? first, it seems that computing exact aspect graphs of surfaces of high degree is impractical. It can be shown that triple points occur only for surfaces of degree 6 or more, and that computing the extremal points of the corresponding curves requires solving a polynomial system of degree 4,315,680-a very high degree indeed! Even if this extraordinary computation were feasible (or another method than ours proved simpler), it is not clear how useful a data structure as complicated as the aspect graph of Fig. 4.a would be for vision applications.

On the other hand, aspect graphs of low-degree surfaces do not require tracing triple points, and the necessary amount of computation remains reasonable (for example, a mere few thousands of roots had to be computed for the tangent crossings of the beanshaped object). In addition, as demonstrated by Fig. 4.b-d, the aspect graphs of these objects are quite simple and should prove useful in recognition tasks.

## 5 Discussion and Future Research

We have presented a new algorithm for computing the exact aspect graph of curved objects and described its implementation. This algorithm is quite general: as noted in [27],

![Figure 4. A few objects and their aspect graphs](/Users/evanthayer/Projects/paperx/docs/1992_computing_exact_aspect_graphs_of_curved_objects_algebraic_surfaces/figures/figure-4-2-p008.png)

*Figure 4. A few objects and their aspect graphs: a. A parametric surface, b. A bean-shaped implicit surface, c. A squash-shaped implicit surface, d. A "dimpled" implicit surface.*

algebraic surfaces subsume most representations u ed in computer aided design and computer vision. Unlike alternative approaches based on cylindrical algebraic decomposition [3, 9], our algorithm is also practical, as demonstrated by our implementation.

We are investigating the case of perspective projection: the (families of) surface curves that delineate the visual events under orthographic projection also delineate perspective projection visual events by defining ruled surfaces that partition the three-dimensional view space into volumetric cells.

Future research will be dedicated to actually using the aspect graph representation in recognition tasks. In [27], we have demonstrated the recovery of the position and orientation of curved three-dimensional objects from monocular contours by using a purely quantitative process that fits an object-centered representation to image contours. What is missing is a control structure for guiding this process. We believe that the qualitative, viewer-centered aspect graph representation can be used to guide the search for matching image and model features and yield efficient control structures analogous to the interpretation trees used in the polyhedral world [14, 17, 19].

Acknowledgments: We thank Seth Hutchinson, Alison Noble and Brigitte Ponce for useful discussions and comments.

Appendix A: The Visual Events of Parametric Surfaces

## A parametric algebraic surface is represented by:

$$
\mathbf{X}(u, v)=(X(u, v), Y(u, v), Z(u, v))^{T}, \quad(u, v) \in I \times J \subset \mathbb{R}^{2},
$$

where \(X, Y, Z\) are (rational) polynomials in \(u, v\). These surfaces include Bézier patches and non-uniform rational B-splines (NURBS) for example.

In this appendix and the following one, we assume that the viewing direction \(\mathbf{V}\) is parameterized in \(\mathbb{R}^{2}\), by spherical angles for example. Note that all equations involving \(\mathbf{V}\) can be made polynomial by using the rational parameterization of the trigonometric functions.

### A.1 Local Events

We recall the equations defining the surface curves (parabolic and flecnodal curves) associated to the visual events (beaks, lips, swallowtails) of parametric surfaces. There is nothing new here, but equations for flecnodal curves are not so easy to find in the literature.

Note: in this appendix, a \(u\) (resp. v) subscript is used to denote a partial derivative with respect to \(u\) (resp. v).

Consider a parametric surface \(\mathbf{X}(u, v)\) and define:

$$
\mathbf{N}=\mathbf{X}_{u} \times \mathbf{X}_{v}, \quad e=\left(\mathbf{X}_{u u} \cdot \mathbf{N}\right) /|\mathbf{N}|, \quad f=\left(\mathbf{X}_{u v} \cdot \mathbf{N}\right) /|\mathbf{N}|, \quad g=\left(\mathbf{X}_{v v} \cdot \mathbf{N}\right) /|\mathbf{N}|,
$$

i.e., \(\mathbf{N}\) is the surface normal, and \(e, f, g\), are the coefficients of the second fundamental form in the coordinate system \(\left(\mathbf{X}_{u}, \mathbf{X}_{v}\right)\) [10].

#### A.1.2 Parabolic Curves.

The parabolic curves of a parametric surface \(X(u,v)\) are given by:

$$
e g-f^{2}=0 .
$$

```text
For each point \(\mathbf{X}(u, v)\) along a parabolic curve, there is only one asymptotic direction, which is given by (4). In the language of Sect. 3, (4) defines the mapping from \(\Gamma\) (the parabolic curve) onto \(\Delta\) (the view sphere curve corresponding to beak-to-beak and lip events). Equivalently, \(\Delta\) is the projection of the curve \(\Omega\) obtained by adding to (5) the equations \(\mathbf{V} \times\left(u^{\prime} \mathbf{X}_{u}+v^{\prime} \mathbf{X}_{v}\right)=0\) and (4).
```

A.1.3 Flecnodal curves. As shown in [43, p.85], the flecnodal points are inflections of the asymptotic curves A, given by:

$$
\left(\mathbf{A}^{\prime} \times \mathbf{A}^{\prime \prime}\right) \cdot \mathbf{N}=0,
$$

which can be seen as an equation in \(u, v, t\), or, equivalently, as an equation in \(u, v, u^{\prime}, v^{\prime}\), \(u^{\prime \prime}, v^{\prime \prime}\).

An equation for the flecnodal curves is obtained by eliminating \(u^{\prime}, v^{\prime}, u^{\prime \prime}, v^{\prime \prime}\) among eqs. (4), (6), and the equation obtained by differentiating (4) with respect to \(t\). Note that since all three equations are homogeneous in \(u^{\prime}, v^{\prime}\) and in \(u^{\prime \prime}, v^{\prime \prime}\), this can be done by arbitrarily setting \(u^{\prime}=1, u^{\prime \prime}=1\), say, and eliminating \(v^{\prime}, v^{\prime \prime}\) among these three equations. The resulting equation in \(u, v\) characterizes the flecnodal curves.

Note that although it is possible to construct the general equation of flecnodal curves for arbitrary parametric surfaces, this equation is very complicated, and it is better to derive it for each particular surface using a computer algebra system. As before, explicit equations for ~2 can be constructed.

### A.2 Multiloeal Events

Multilocal events occur when the viewing direction \(\mathbf{V}\) has high order contact with the surface in at least two distinct points \(\mathbf{X}_{1}\) and \(\mathbf{X}_{2}\). In that case, \(\mathbf{V}=\mathbf{X}_{1}-\mathbf{X}_{2}\).

#### A.2.1 Triple Points.

The triple point is conceptually the simplest of the multilocal events. It occurs when three contour fragments intersect at a single point. Let Xi = \(X(ui,vi)\), for i = 1, 2, 3, be the three corresponding surface points, and let Ni be the corresponding surface normals, we obtain the following equations:

$$
\left\{\begin{array}{l} \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \times\left(\mathbf{X}_{2}-\mathbf{X}_{3}\right)=0 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{3}=0 \\ \left(\mathbf{X}_{2}-\mathbf{X}_{3}\right) \cdot \mathbf{N}_{1}=0 \\ \left(\mathbf{X}_{3}-\mathbf{X}_{1}\right) \cdot \mathbf{N}_{2}=0 \end{array}\right.
$$

The first equation is a vector equation (or equivalently a set of two independent scalar equations) that expresses the fact that the three points are aligned with the viewing direction. The next three equations simply express the fact that the three points belong to the occluding contour. It follows that triple points are characterized by five equations in the six variables \(u_{i}, v_{i}, i=1,2,3\).

An explicit equation for the curve \(\Omega\) corresponding to a triple point can be obtained by replacing ( \(\mathbf{X}_{2}-\mathbf{X}_{3}\) ) by \(\mathbf{V}\) in (7). Similar comments apply to the other multilocal events.

- A.2.2 Tangent Crossings. A tangent crossing occurs when two occluding contour points Xl = \(X(ul,vl)\) and X2 = \(X(u2,v2)\) project to the same image point and have collinear surface normals N1 and N2. This can be rewritten as:

$$
\left\{\begin{array}{l} \mathbf{N}_{1} \times \mathbf{N}_{2}=\mathbf{0} \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{1}=0 \end{array}\right.
$$

Again, remark that the first equation is a vector equation (or equivalently a set of two independent scalar equations). It follows that tangent crossings are characterized by three equations in the four variables \(u_{i}, v_{i}, i=1,2\).

- A.2.3 Cusp Crossings. A cusp crossing occurs when two occluding contour points XI and X~ project to the same image point and one of the points, say X1, is a cusp. This can be rewritten as:

$$
\left\{\begin{array}{l} \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{1}=0 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{2}=0 \\ e_{1} a^{2}+2 f_{1} a b+g_{1} b^{2}=0 \end{array}\right.
$$

where \(e_{1}, f_{1}, g_{1}\) are the values of the coefficients of the second fundamental form at \(\mathbf{X}_{1}\), and ( \(a, b\) ) are the coordinates of the viewing direction \(\mathbf{X}_{\mathbf{1}}-\mathbf{X}_{\mathbf{2}}\) in the basis \(\mathbf{X}_{\mathbf{u}}\left(u_{1}, v_{1}\right)\), \(\mathbf{X}_{v}\left(u_{1}, v_{1}\right)\) of the tangent plane. Note that \(a, b\) can be computed from the dot products of \(\mathbf{X}_{1}-\mathbf{X}_{2}\) with \(\mathbf{X}_{u}\left(u_{1}, v_{1}\right)\) and \(\mathbf{X}_{v}\left(u_{1}, v_{1}\right)\). It follows that cusp crossings are characterized by three equations in the four variables \(u_{i}, v_{i}, i=1,2\).

Appendix B: The Visual Events of Implicit Surfaces An implicit algebraic surface is represented by:

$$
F(X, Y, Z)=F(\mathbf{X})=0
$$

where \(F\) is a polynomial in \(X, Y, Z\).

#### A.I.1 Asymptotic Directions.

$$
The asymptotic curves are the surface curves A(t) = X(u(t), v(t)) defined by the differential equation:
$$

$$
e u^{\prime 2}+2 f u^{\prime} v^{\prime}+g v^{\prime 2}=0
$$

The asymptotic directions are given by \(u^{\prime} \mathbf{X}_{u}+v^{\prime} \mathbf{X}_{v}\), where \(u^{\prime}\) and \(v^{\prime}\) are solutions of the above equation. A contour cusp occurs when the viewing direction is an asymptotic direction.

### B.1 Local Events

For implicit surfaces, even the equations of parabolic curves are buried in the literature. Equations for both parabolic and flecnodal curves are derived in this appendix.

Note: in this appendix, X, Y, Z subscripts denote partial derivatives with respect to these variables.

- B.I.1 Asymptotic Directions. An asymptotic direction V at a point X lies in the tangent plane and has second order contact with the surface. It is characterized by:

$$
\left\{\begin{array}{l} \nabla F(\mathbf{X}) \cdot \mathbf{V}=0 \\ \mathbf{V}^{T} H(\mathbf{X}) \mathbf{V}=0 \end{array}\right.
$$

where \(H(\mathbf{X})\) is the Hessian of \(F\) at \(\mathbf{X}\). Asymptotic directions are determined by solving this homogeneous system in \(\mathbf{V}\).

- B.1.2 Parabolic curves. The parabolic curves of an implicit surface \(F(X)=0\) are given by:

$$
\begin{aligned} & F_{X}^{2}\left(F_{Y Y} F_{Z Z}-F_{Y Z}^{2}\right)+F_{Y}^{2}\left(F_{X X} F_{Z Z}-F_{X Z}^{2}\right) \\ & \quad+F_{Z}^{2}\left(F_{X X} F_{Y Y}-F_{X Y}^{2}\right)+2 F_{X} F_{Y}\left(F_{X Z} F_{Y Z}-F_{Z Z} F_{X Y}\right) \\ & \quad+2 F_{Y} F_{Z}\left(F_{X Y} F_{X Z}-F_{X X} F_{Y Z}\right)+2 F_{X} F_{Z}\left(F_{X Y} F_{Y Z}-F_{Y Y} F_{X Z}\right)=0 \end{aligned}
$$

```text
plus the equation \(F(\mathbf{X})=0\) itself. For each point \(\mathbf{X}\) along a parabolic curve, there is only one asymptotic direction, which is given by (11). It should be noted that one can directly characterize the beak-to-beak and lip events by adding to (12) the equations \(F(\mathbf{X})=0\) and (11), and tracing the resulting curve \(\Omega\) in \(\mathbb{R}^{5}\);
the projection of this curve onto \(\mathbb{R}^{2}\) defines the beak-to-beak and lip curves on the view sphere.
```

- B.1.3 Flecnodal curves. A surface point X = (X, Y, Z) T on a flecnodal curve has third order contact with a line along an asymptotic direction V = (V1, Vu, V3) T [1]. This is characterized by:

$$
\left\{\begin{array}{l} \nabla F(\mathbf{X}) \cdot \mathbf{V}=0 \\ \mathbf{V}^{T} H(\mathbf{X}) \mathbf{V}=0 \\ \mathbf{V}^{T}\left(H_{X}(\mathbf{X}) V_{1}+H_{Y}(\mathbf{X}) V_{2}+H_{Z}(\mathbf{X}) V_{3}\right) \mathbf{V}=0 \end{array}\right.
$$

Since these three equations are homogeneous in the coordinates of \(\mathbf{V}\), these coordinates can easily be eliminated to obtain a single equation in \(\mathbf{X}\). Along with \(F(\mathbf{X})=0\), this system defines the flecnodal curves. As before, explicit equations for \(\Omega\) can be con-

### B.2 Multilocal Events

- B.2.1 Triple Points. Let Xi, i = 1, 2, 3, be three points forming a triple point event. The corresponding equations are similar to the equations defining triple points of parametric surfaces:

$$
\left\{\begin{array}{l} F\left(\mathbf{X}_{i}\right)=0, \quad i=1,2,3 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \times\left(\mathbf{X}_{2}-\mathbf{X}_{3}\right)=0 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{3}=0 \\ \left(\mathbf{X}_{2}-\mathbf{X}_{3}\right) \cdot \mathbf{N}_{1}=0 \\ \left(\mathbf{X}_{3}-\mathbf{X}_{1}\right) \cdot \mathbf{N}_{2}=0 \end{array}\right.
$$

where \(\mathbf{N}_{i}=\nabla F\left(\mathbf{X}_{i}\right)\). It follows that triple points are characterized by eight equations in the nine variables \(X_{i}, Y_{i}, Z_{i}, i=1,2,3\).

- B.2.2 Tangent Crossings. Again, the equations defining tangent crossings of implicit surfaces are similar to the corresponding equations for parametric surfaces:

$$
\left\{\begin{array}{l} F\left(\mathbf{X}_{i}\right)=0, \quad i=1,2 \\ \mathbf{N}_{1} \times \mathbf{N}_{2}=\mathbf{0} \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{1}=0 \end{array}\right.
$$

This is a system of five equations in the six variables \(X_{i}, Y_{i}, Z_{i}, i=1,2\).

- B.2.3 Cusp Crossings. Cusp crossings are characterized by:

$$
\left\{\begin{array}{l} F\left(\mathbf{X}_{i}\right)=0, \quad i=1,2 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{1}=0 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right) \cdot \mathbf{N}_{2}=0 \\ \left(\mathbf{X}_{1}-\mathbf{X}_{2}\right)^{T} H\left(\mathbf{X}_{1}\right)\left(\mathbf{X}_{1}-\mathbf{X}_{2}\right)=0 \end{array}\right.
$$

where the last equation simply expresses the fact that the viewing direction is an asymptotic direction of the surface at \(\mathbf{X}_{1}\). This is again a system of five equations in the six

Appendix C: Details of the curve Tracing algorithm c.1 Step 1.1: Finding the Extremal Points The extrema of \(\Gamma\) in the \(X_{0}\) direction are given by differentiating (1) and setting \(d X_{0}=0\) :

$$
\left\{\begin{array}{l} \left(\partial P_{1} / \partial X_{1}\right) d X_{1}+\ldots+\left(\partial P_{1} / \partial X_{n}\right) d X_{n}=0 \\ \ldots \\ \left(\partial P_{n} / \partial X_{1}\right) d X_{1}+\ldots+\left(\partial P_{n} / \partial X_{n}\right) d X_{n}=0 \end{array} \Longleftrightarrow J\left(\begin{array}{l} d X_{1} \\ \ldots \\ d X_{n} \end{array}\right)=0\right.
$$

where \(J=\left(\partial P_{i} / \partial X_{j}\right)\), with \(i, j=1, . ., n\), is the Jacobian matrix. This system has nontrivial solutions if and only if the determinant \(D\left(X_{0}, X_{1}, \ldots, X_{n}\right)=|J|\) of the Jacobian matrix vanishes. The extrema of \(\Gamma\) are therefore the solutions of:

$$
\left\{\begin{array}{l} P_{1}\left(X_{0}, X_{1}, \ldots, X_{n}\right)=0 \\ \ldots \\ P_{n}\left(X_{0}, X_{1}, \ldots, X_{n}\right)=0 \\ D\left(X_{0}, X_{1}, \ldots, X_{n}\right)=0 \end{array}\right.
$$

### C.2 Steps 1.2 and 1.3: Intersecting the Curve with Hyperplanes

These steps correspond to finding all the intersections of \(\Gamma\) with some hyperplane \(X_{0}=\) \(\hat{X}_{0}\). These intersections are given by:

$$
\left\{\begin{array}{l} P_{1}\left(\hat{X}_{0}, X_{1}, \ldots, X_{n}\right)=0 \\ \ldots \\ P_{n}\left(\hat{X}_{0}, X_{1}, \ldots, X_{n}\right)=0 \end{array}\right.
$$

### C.3 Step 1.4: Marching on Extrema-Free Intervals

To trace a curve on an extrema-free interval, we use a classical prediction/correction approach based on a first order Taylor expansion of the \(P_{i}\) 's (higher order expansions could also be used [4, 13]). By differentiating (1), we obtain:

$$
J\left(\begin{array}{c} d X_{1} \\ \ldots \\ d X_{n} \end{array}\right)=-d X_{0}\left(\begin{array}{c} \partial P_{1} / \partial X_{0} \\ \ldots \\ \partial P_{n} / \partial X_{0} \end{array}\right)
$$

Given a step \(d X_{0}\) in the \(X_{0}\) direction, one can predict the remaining \(d X_{i}\) 's by solving this system of linear equations. This is only possible when the determinant of the Jacobian matrix \(J\) is non-zero, which is exactly equivalent to saying that the point \(\left(X_{0}, \ldots, X_{n}\right)^{T}\) is not an extremum in the \(X_{0}\) direction.

The correction step uses Newton iterations to converge back to the curve from the predicted point. We write once more a first order Taylor approximation of the \(P_{i}\) 's to compute the necessary correction \(\left(d X_{1}, \ldots, d X_{n}\right)^{T}\) for a fixed value of \(X_{0}\) :

$$
\left\{\begin{array}{l} P_{1}+\left(\partial P_{1} / \partial X_{1}\right) d X_{1}+\ldots+\left(\partial P_{1} / \partial X_{n}\right) d X_{n}=0 \\ \ldots \\ P_{n}+\left(\partial P_{n} / \partial X_{1}\right) d X_{1}+\ldots+\left(\partial P_{n} / \partial X_{n}\right) d X_{n}=0 \end{array} \Longleftrightarrow\left(\begin{array}{c} d X_{1} \\ d X_{2} \\ \ldots \\ d X_{n} \end{array}\right)=-J^{-1}\left(\begin{array}{c} P_{1} \\ \ldots \\ P_{n} \end{array}\right)\right.
$$

Appendix D: Homotopy Continuation Consider a system of n polynomial equations Pi in n unknowns Xj, denoted by \(P(X)=0\), with P = (P1,...,Pn) T and X = (X1,...,Xn) T. To solve this system, we use the homotopy continuation method [30], itself a simple form of curve tracing. The principle of the method is as follows. Let \(Q(X)=0\) be another system of polynomial equations with the same total degree as \(P(X)=0\), but known solutions. A homotopy, parameterized by t E [0, 1], can be defined between the two systems by:

$$
(1-t) \mathbf{Q}(\mathbf{X})+t \mathbf{P}(\mathbf{X})=0
$$

The solutions of the target system are found by tracing the curve defined in ~n+l by these equations from t = 0 to t -- 1 according to step 1.4 of our curve tracing algorithm. In this case, however, the sample points are the known solutions of \(Q(X)=0\) at t = 0, which allows us to bypass step 1.3 of the algorithm. It can also be shown [30] that with an appropriate choice of Q, the curve has no extrema or singularities, which allows us to also bypass steps 1.1-1.2.

## References

- V.I. Arnol'd. Singularities ofsystems of rays. Russian Math. Surveys, 38(2):87-176, 1983.

- D.S. Arnon. Topologically reliable display of algebraic curves. Computer Graphics, 17(3):219-227, July 1983.

- D.S. Arnon, G. Collins, and S. McCallum. Cylindrical algebraic decomposition I and II. SIAM J. Comput., 13(4):865-889, November 1984.

- C.L. Bajaj, C.M. Hoffmann, R.E. Lynch, and J.E.H. Hopcroft. Tracing surface intersections. Computer Aided Geometric Design, 5:285-307, 1988.

- J. Callalaan and R. Weiss. A model for describing surface shape. In Proc. IEEE Conf. Comp. Vision Part. Recog., pages 240-245, San Francisco, CA, June 1985.

- G. Castore. Solid modeling, aspect graphs, and robot vision. In Pickett and Boyse, editors, Solid modeling by computer, pages 277-292. Plenum Press, NY, 1984.

- I. Chakravarty. The use of characteristic views as a basis for recognition of threedimensional objects. Image Processing Laboratory IPL-TR-034, Rensselaer Polytechnic Institute, October 1982.

- S. Chen and H. Freeman. On the characteristic views of quadric-surfaced solids. In 1EEE Workshop on Directions in Automated CAD-Based Vision, pages 34-43, June 1991.

- G.E. Collins. Quantifier Elimination for Real Closed Fields by Cylindrical Algebraic decomposition, volume 33 of Lecture Notes in Computer Science. Springer-Verlag, New York, 1975.

- M.P. do Carmo. Differential Geometry of curves and Surfaces. Prentice-Ha l, Englewood Cliffs, N J, 1976.

- D. Eggert and K. Bowyer. Computing the orthographic projection aspect graph of solids of revolution. In Proc. IEEE Workshop on Interpretation of 3D Scenes, pages 102-108, Austin, TX, November 1989.

- D. Eggert and K. Bowyer. perspective projection aspect graphs of solids of revolution: An implementation. In IEEE Workshop on Directions in Automated CAD-Based Vision, pages 44-53, June 1991.

- R.T. Farouki. The characterization of parametric surface sections. Comp. Vis. Graph. Ira. Proc., 33:209-236, 1986.

- O.D. Faugeras and M. Hebert. The representation, recognition, and locating of 3-D objects. International Journal of Robotics Research, 5(3):27-52, Fall 1986.

- Z. Gigus, J. Canny, and R. Seidel. efficiently computing and representing aspect graphs of polyhedral objects. IEEE Trans. Part. Anal. Mach. lntell., 13(6), June 1991.

- Z. Gigus and J. Malik. Computing the aspect graph for line drawings of polyhedral objects. IEEE Trans. Part. Anal. Mach. Intell., 12(2):113-122, February 1990.

- W.E.L. Grimson and T. Lozano-P~rez. Localizing overlapping parts by searching the interpretation tree. IEEE Trans. Patt. Anal. Mach. Intell., 9(4):469-482, 1987.

- M. Hebert and T. Kanade. The 3D profile method for object recognition. In Proc. IEEE Conf. Comp. Vision Patt. Recog., pages 458-463, San Francisco, CA, June 1985.

- D.P. Huttenlocher and S. Uilman. Object recognition using alignment. In Proc. Int. Conf. Comp. Vision, pages 102-111, London, U.K., June 1987.

- K. Ikeuchi and T. Kanaxie. Automatic generation of object recognition programs. Proceedings of the IEEE, 76(8):1016-35, August 1988.

- J.T. Kajiya. Ray tracing parametric patches. Computer Graphics, 16:245-254, July 1982.

- Y.L. Kergosien. La famille des projections orthogonales d'une surface et ses singularit~s. C.R. Acad. Sc. Paris, 292:929-932, 1981.

- Y.L. Kergosien. Generic sign systems in medical imaging. IEEE Computer Graphics and Applications, 11(5):46-65, 1991.

- J.J. Koenderink. Solid Shape. MIT Press, Cambridge, MA, 1990.

- J.J. Koenderink and A.J. Van Doom. The internal representation of solid shape with respect to vision. Biological Cybernetics, 32:211-216, 1979.

- D.J. Kriegman and J. Ponce. Computing exact aspect graphs of curved objects: solids of revolution, lnt. J. of Comp. Vision., 5(2):119-135, 1990.

- D.J. Kriegman and J. Ponce. On recognizing and positioning curved 3D objects from image contours. 1EEE Trans. Patt. Anal. Mach. lntell., 12(12):1127-1137, December 1990.

- D.J. Kriegman and J. Ponce. Geometric modelling for computer vision. In SPIE Conference on curves and Surfaces in Computer Vision and Graphics 1I, Boston, MA, November 1991.

- D.J. Kriegman and J. Ponce. A new curve tracing algorithm and some applications. In P.J. Laurent, A. Le Mdhautd, and L.L. Schumaker, editors, curves and Surfaces, pages 267-270. Academic Press, New York, 1991.

- A.P. Morgan. Solving Polynomial Systems using Continuation for engineering and Scientific Problems. Prentice Hall, Englewood Cliffs, N J, 1987.

- H. Plantinga and C. Dyer. visibility, occlusion, and the aspect graph. Int. J. of Comp. Vision., 5(2):137-160, 1990.

- J. Ponce and D.J. Kriegman. Computing exact aspect graphs of curved objects: parametric patches. In Proc. A A A I Nat. Conf. Artif. lntell., pages 1074-1079, Boston, MA, July 1990.

- J.H. Rieger. On the classification of views of piecewise-smooth objects, linage and Vision Computing, 5:91-97, 1987.

- J.H. Rieger. The geometry of view space of opaque objects bounded by smooth surfaces. Artificial Intelligence, 44(1-2):1-40, July 1990.

- J.H. Rieger. Global bifurcations sets and stable projections of non-singular algebraic surfaces. Int. J. of Comp. Vision., 1991. To appear.

- W.B. Seales and C.R. Dyer. Constrained viewpoint from occluding contour. In IEEE Workshop on Directions in Automated "CAD-Based" Vision, pages 54-63, Maui, Hawaii, June 1991.

- T. Sripradisvarakul and R. Jain. Generating aspect graphs of curved objects. In Proc. IEEE Workshop on Interpretation of 3D Scenes, pages 109-115, Austin, TX, December 1989.

- J. Stewman and K.W. Bowyer. Aspect graphs for planar-fax:e convex objects. In Proc. 1EEE Workshop on Computer Vision, pages 123-130, Miami, FL, 1987.

- J. Stewman and K.W. Bowyer. Creating the perspective projection aspect graph of polyhedral objects. In Proc. Int. Conf. Comp. Vision, pages 495-500, Tampa, FL, 1988.

- C.T.C. Wall. Geometric properties of generic differentiable manifolds. In A. Dold and B. Eckmann, editors, Geometry and Topology, pages 707-774, Rio de Janeiro, 1976. Springer-Verlag.

- R. Wang and H. Freeman. Object recognition based on characteristic views. In International Conference on Pattern Recognition, pages 8-12, Atlantic City, N J, June 1990.

- N. Watts. Calculating the principal views of a polyhedron. CS Tech. Report 234, Rochester University, 1987.

- C.E. Weatherburn. Differentialgeometry. Cambridge University Press, 1927.

- T. Whitted. An improved illumination model for shaded display. Comm. of the ACM, 23(6):343-349, June 1980.
