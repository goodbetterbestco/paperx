# Arbitrarily Precise Computation of Gauss Maps and Visibility Sets for Freeform Surfaces

Total Downloads, Open Access Support provided by, Symposium on Solid Modeling \&amp, Conference Sponsors

GERSHON ELBER , Technion - Israel Institute of Technology, Haifa, Israel ELAINE COHEN , The University of Utah, Salt Lake City, UT, United States
The University of Utah
Technion - Israel Institute of Technology Utah, Salt Lake City, USA May 17 - 19, 1995 Utah, Salt Lake City, USA

## Abstract

The need to compute visibility and accessibility of surfaces occurs in a broad range of applications from computer aided design and manufacturing to computer graphics and vision. Surface-surface intersection is an essential task in modeling systems that support boolean operations. Recently, Gauss maps and visibility sets were shown [3, 4, 20, 21] to be helpful in robustly solving the above problems. This paper presents a symbolic based method to both compute and exploit the Gauss map of a freeform surface or a model consisting of several, possibly trimmed, freeform surfaces. Unlike other approaches to the computation of the Gauss map, the method presented here can be made arbitrarily precise for piecewise polynomial and rational surfaces. The Gauss map is then employed to compute the set of views from which a freeform surface is completely locally visible.

## 1 Introduction

The directions from which a surface is completely visible are of fundamental interest for many applications. In graphics, this problem is closely related to the hidden surface removal problem [8, 9]. In manufacturing, a surface can be machined only when it can be reached or 'seen' by a tool. In [21], the directions from which a feature can be approached for machining purposes without interference is investigated.

The Gauss map of surface \(S[2,17], \mathcal{G}_{2}\), and the visibility set of surface \(S[3,4,20], \mathcal{V}_{3}\), can be used for both shape recognition and matching since they provide a unique characterization of a surface. Throughout this paper, a sub script will denote the surface for which the map or the set is computed.

We first review some intuitive elementary aspects of visibility. For a point \(p\) on a surface \(S\) to be visible to an observer's eye located at a point \(E\) two tests must be satis fied. first, \(p\) must be "forward facing" and not on the "back side" of \(S\), which can be determined by locally examining the surface. Second, \(p\) cannot be occluded by another part of \(S\) or by a different surface in the scene, that is, another surface lies along the ray from the eye to \(p\) but is closer to the eye than \(p\). This last property can only be determined by examining global properties. We will more rigorously define the first requirement, and consider collections of such eye points.

Definition 1 We define \(\mathcal{G}_{3}\), the Gauss map of a surface \(S\), to be a map from the surface \(S\) to the unit sphere, \(S^{2}\), which takes each point \(p \in S\) to its unit normal vector, \(\overrightarrow{n_{p}}\). That is, \(\overrightarrow{n_{p}}=\mathcal{G},(p)\).

Definition 2 Given a unit direction vector \(\vec{v}\), we say that a point \(p \in S\), is locally visible from direction \(\vec{v}\) iff \(\left(\vec{v}, \overrightarrow{n_{p}}\right) \geq 0\).

Denote by \(\operatorname{Int}(S)\) the interior of \(S\). Then, definition 3 Given a unit direction vector \(\vec{v}\), we say that a point \(p \in \operatorname{Int}(S)\) has local neighborhood visibility from

![Figure 1](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-1-p003.png)

*Figure 1: A surface can be locally visible, yet can hide itself globally by looping around itself.*

direction \(\vec{v}\) iff there exist a small open disk \(\mathcal{D} \subset \operatorname{In} t(S)\) such that each \(q \in \mathcal{D}\) is locally visible from \(\vec{v}\).

Definition 4 The visibility set of surface \(S\), \(\mathcal{V}_{\text {, }}\), is the set of points on \(S^{2}\) that correspond to directions from which every point \(p \in I\) nt \((S)\) has local neighborhood visibility. That is, \(\vec{v} \in S^{2}\) is also in \(\mathcal{V}_{s}\) if for all \(p \in \operatorname{Int}(S), p\) has local neigh borhood visibility from \(\vec{v}\). We say that \(S\) is locally visible from each element of \(\mathcal{V}\), definition 4 prescribes the set of directions from which the entire surface is locally visible. Those points are only globally visible if the surface does not loop around itself, as that in Figure 1, or if another surface is not closer to the eye.

$$
\mathcal{V}_{s}=\left\{\vec{\alpha} \mid\left\langle\vec{\alpha}, \mathcal{N}_{s}(u, v)\right\rangle \geq 0, \forall u, v,\|\vec{\alpha}\|=1\right\} .
$$

A common and simple method to determine a bound on the normal directions of a given surface \(S\) is based upon the computation of a bounding cone [16, 19] of all possible normal directions of \(S\). The normal cone is derived from the cross product relation between the two cones representing all the possible partial derivative directions. The normal cone bound of the image of the Gauss map of \(S\) is fairly loose and can provide insufficient information in many applications.

In this paper, a method is presented to compute an arbi trarily precise bound on the directions from which a surface is completely locally visible. That is, we present an approach to the computation of \(\mathcal{G}_{s}\) and \(\mathcal{V}_{s}\) that prescribes an arbitrary precise representation of the boundaries of \(\mathcal{G}_{s}\) and \(\mathcal{V}_{s}\), not a conical upper bound. Unlike existing schemes that exercise bounding cones [16, 19] or convex hull bounds using a mesh of the normal surface [15], the method presented herein can be easily extended to provide \(\mathcal{G}_{s}\) and \(\mathcal{V}_{s}\) of a trimmed surface or even of a set of several trimmed surfaces with arbritrary precision.

$$
\begin{equation*} \hat{\mathcal{N}}_{s}(u, v)=\frac{\partial S(u, v)}{\partial u} \times \frac{\partial S(u, v)}{\partial v}, \tag{2} \end{equation*}
$$

Section 2 discusses the necessary background. In sec tion 3, we develop a method to compute the image of the Gauss map, \(\mathcal{G}_{s}\), of a given surface \(S. \mathcal{G}_{s}\), as a unit vector field [2], is represented and bounded by its boundary curves on the unit sphere, \(S^{2}\).

One application that demonstrates the importance of the Gauss map is the computation of the visibility set of a sur face. We follow the approach proposed in [3,4] and gen eralize it to support freeform surfaces. Using the methods presented herein, the image of \(\mathcal{G}_{s}\) is used to compute the

All figures in this paper were created from an implementation of the algorithms using the Alpha.1 solid modeler developed at the University of Utah.

## 2 Background

Given a regular \(C^{1}\) surface \(S(u, v)\), let \(\mathcal{N}_{S}(u, v)=n_{S(u, v)}\) be the unit normal surface to \(S(u, v)\). We use this new notation to emphasize that \(n_{p}\), defined in definition 1, is dependent on the parametrization. Thus,

$$
\begin{equation*} \mathcal{N}_{s}(u, v)=\frac{\frac{\partial S(u, v)}{\partial u} \times \frac{\partial S(u, v)}{\partial v}}{\left\|\frac{\partial S(u, v)}{\partial u} \times \frac{\partial S(u, v)}{\partial v}\right\|} . \tag{1} \end{equation*}
$$

A surface is considered completely locally visible from direction d if the following holds.

Definition 5 Given a \(C^{1}\) surface \(S(u, v)\), and a vector \(\vec{\alpha}\), \(S(u, v)\) is completely locally visible from direction \(\vec{\alpha}\) iff each point in \(S\) is locally visible from \(\vec{\alpha}\).

A surface \(S\) is partially locally visible from \(\vec{\alpha}\) if only some of the points in \(S\) are locally visible from \(\vec{\alpha}\). As defined, surface normals must point to the "inside" of the surface (object).

Using definition 5, one can immediately see from definition 4 that Corollary 1

\(S(u, v)\). We assume that the surface is completely locally visible from at least one direction, i.e. \(\mathcal{V}_{\text {g }}\) is not empty. This is obviously not always the case. \(S^{2}\) itself, consid ered as a single surface, has no direction from which it is completely locally visible. However, a surface can always be subdivided and tested using loose bounding techniques, such as the bounding cones [16, 19], until this criterion holds.

Whenever possible, the unnormalized normal surface will be used instead of \(\mathcal{N}_{s}(u, v)\). The unnormalized normal, re ferred to as \(\hat{\mathcal{N}}_{\text {s }}\), is defined as, which has a parametrization dependent magnitude. In the ensuing discussion, we symbolically compute the unnormal ized normal surface of \(\hat{\mathcal{N}}_{s}\), and refer to it as \(\hat{\mathcal{N}}_{s}^{2} . S(u, v)\) is assumed to be regular, that is \(\left\|\hat{\mathcal{N}}_{s}(u, v)\right\| \neq 0\), for all \(u, v\), and sufficiently differentiable so that \(\hat{\mathcal{N}}_{s}(u, v)\) and \(\hat{\mathcal{N}}_{s}^{2}(u, v)\) are continuous. algorithms to symbolically compute the sum, difference, and product of B-spline or Bézier surfaces are well known [6, 7, 10, 18]. This paper will exercise symbolic computation and representation of surfaces, computed as scalar and vec tor fields that represent properties such as curvature [11], normals [8], offset error [13], or surface slopes and speed bounds [12]. For example, the Bézier or NURBs representations of \(\hat{\mathcal{N}}_{s}(u, v)\) is a normal vector field that can be symbol ically computed as the (cross) product of the partial deriva tives of \(S(u, v)\) (equation (2)).

let \(q \in \mathcal{R}^{3} .\|q\| \neq 0\). Let \(L\) be a ray from the origin \(\mathcal{O}\) to \(q\), and let \(q_{*^{2}}\) be the point where \(L\) intersects \(S^{2}\). definition \(6 q\) is said to be centrally projected from \(\mathcal{O}\) onto \(s^{2}\) using \(L\). and that \(q_{s^{2}}\) is its projected point. This mapping is called a central or gnomonic [5] projection.

In the ensuing discussion and unless stated otherwise, \(\mathcal{O}\) is assumed to be the center of the central projection. Let \(P\) be an arbitrary plane that does not contain \(\mathcal{O}\), and \(q_{p}\) be the intersection point of \(L\) with \(P\). definition \(7 q\) is said to be centrally projected onto a plane \(P\) using \(L\). and that \(q_{p}\) is its projected point. [n definition 7, we notice that the perspective projection, (Ised in computer graphics, is a special case of a central projection onto a plane.

![Figure 2](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-2-p004.png)

*Figure 2: This simple bicubic surface is used throughout Figure ~: This simple bicnbic surface is used throughc)ut this paper as an example.*

Definition 8 A closed curve, \(C(t) \subset \mathcal{R}^{3}\), is said to be cen trally convex, if there exist a plane \(P\) that does not contain \(\mathcal{O}\) such that the central projection of \(C(t)\) onto \(P\) is a closed conver curve. That is, the line segment connecting two ar bitrary points on the central projection of \(C(t)\) onto \(P\) is totally within the closed region of \(P\) bounded by the central projection of \((i_{t})\).

## 3 Computation of the Image of the Gauss Map

Given an unnormalized normal surface \(\hat{\mathcal{N}}_{s}(u, v)\) our goal is to compute the image of the Gauss map and represent the boundary of this image, \(\partial \mathcal{G}\). on \(S^{2}\). One can compute a loose bound on the image of the Gauss map using cones bounding the partials derivatives of \(S\) and then compute the bounding cone for the normal field as their cross prod uct [16, 19]. Alternatively, one could compute \(\hat{\mathcal{N}}_{s}(u, v)\) sym bolically, centrally project it onto \(S^{2}\) and compute a bound on the projected image. In [15], the control mesh of \(\hat{\mathcal{N}}_{s}(u, v)\), represented as a Bézier surface, was centrally projected onto \(s^{2}\) and used as a bound for the directions of the normals of A surface displayed in an orthographic view can assume extreme values only along its boundary or its silhouette locations. Similarly, a surface centrally projected onto a plane can assume extreme values on the plane only along its boundary or its central silhouette. In a central projec tion, the viewing direction is a line through both the ori gin. \(\mathcal{O}\), and the viewed point \(S(u, v)\). Therefore, the cen tral projection viewing direction of \(S(u, v)\) is collinear with \(S(u, v)-\mathcal{O}=S(u, v)\).

Definition 9 The central silhouette set of \(S, \mathcal{S}_{s}\), is the set of parameter values for which \(\hat{\mathcal{N}}\), is perpendicular to the central projection viewing direction,

To find the extreme values that \(\hat{\mathcal{N}}_{s}\), can assume in a central projection, one needs to compute the boundaries and the central silhouette of \(\hat{\mathcal{N}}_{s}\). At a silhouette point \(\dot{\mathcal{V}}_{s}\left(u_{0}, v_{0}\right)\) (see Figure 3) the vector \(\dot{\mathcal{N}}_{s}\left(u_{0}, v_{0}\right)\) is perpen dicular to \(\hat{\mathcal{N}}_{s}^{2}\left(u_{0}, v_{0}\right)\). In order to compute the silhouette curves of \(\dot{\mathcal{N}}_{s}(u, v)\), one can compute the unnormalized nor mal vector field of \(\dot{\mathcal{N}}_{s}(u, v), \dot{\mathcal{N}}_{s}^{2}(u, v)\), and find the zero set of their inner product,

$$
\begin{equation*} \mathcal{S}=\left\{(u, v) \mid\left\langle\dot{\mathcal{N}}_{s}(u, v), \dot{\mathcal{N}}_{s}^{2}(u, v)\right\rangle=0\right\} \tag{4} \end{equation*}
$$

to yield the set of all central silhouette points.

Once a representation is found, subdi vision based techniques can be used to find an arbitrarily precise approximation to its zero set [10], as a set of piece wise linear curves.

It is necessary to compute square roots to find the pro jection of the boundary and central silhouette curves of \(\mathcal{N}_{\text {s }}\). onto \(S^{2}\). The square root operation is not representable. in general, as (piecewise) polynomial or rational curves. As a result, an arbitrarily dense set of points can be determined using the central projection, a set that defines a piecewise linear approximation of the boundary and central silhouette The smallest locally simply connected set that contains the boundary and the central silhouette curves of \(\mathcal{N}\), is the exact boundary of \(\mathcal{G}\). Thus, \(\mathcal{G}\), can be computed using a two-dimensional boolean union operation on all the regions bounded by the extracted boundary and silhouette curves on \(S^{2}\).

The set of boundary and silhouette curves of.(. (u. u) may be topologically complex (see Figure 4). making the computation of this two-dimensional boolean union difficult. Fortunately, for the application demonstrated herein. namely the computation of the visibility set [3. 4], V,, it is unnecessary to compute the exact boundaries of ~, in order to find the exact houndaries of V..

The approach to the computation of \(\mathcal{V}\), from \(\mathcal{G}\), gener alizes the approach taken in [3,4] to encompass freeform surface representations.

$$
\begin{equation*} \mathcal{S}_{s}=\left\{(u, v) \mid\left\langle S(u, v), \dot{\mathcal{N}}_{s}(u, v)\right\rangle=0\right\} . \tag{3} \end{equation*}
$$

Lemma 1 The directional domain from which a surface is completely visible, \(\mathcal{V}_{s}\), is centrally convex.

Proof: For a vector \(\vec{\alpha} \in S^{2}\) there exists a hemisphere \(\mathcal{H} \subset S^{2}\) from which a surface point with normal \(\vec{\alpha}\) is locally visible (see Figure 5).

$$
\mathcal{H}=\{\vec{\beta} \mid\|\vec{\beta}\|=1,\langle\vec{\beta}, \vec{\alpha}\rangle \geq 0\} .
$$

\(\mathcal{H}\) holds all vectors in \(S^{2}\) that have a nonnegative inner product with \(\vec{\alpha}\) (definition 5). For \(S(u, v)\) to be visible from

![Figure 3](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-3-p005.png)

*Figure 3: Central view extrema occur along boundaries and central silhouettes. Two-dimensional (a) and three-dimensional (b) cases are considered. The central silhouette set of fi.(u, v) (for the surface S(u, v) in Figure 2, in (b)) is equal to the zero set of (~,(u, v), fi(u, v)). At (UO,VO)we find such a central silhouette point.*

![Figure 4](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-4-p005.png)

*Figure 4: The silhouette set in the central projection of Af~(u, v) can be extremely complex. On the left, is a bicubic surface, with its complex normal surface, ~., in the middle. The boundaries and central silhouette set of ~~ are projected on S2, on the right.*

![Figure 5](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-5-p006.png)

*Figure 5: Each vector, ~ is associated with a hemisphere H={3 I 11311=1)(P!+ 20}.*

a given direction \(\vec{\alpha}, \vec{\alpha} \in \mathcal{H}, \forall \mathcal{H}\) of all vectors in \(\mathcal{N}_{s}(u, v)\).

Centrally mapped onto a plane, a hemisphere is a halfplane. Because an intersection of convex regions is convex, the domain of directions from which a surface is completely visible, V,, is centrally convex as well. ■

Lemma 2 Let \(R\) be a region of a cylinder. Then, \(\mathcal{N}_{r}\) (and \(\mathcal{G}_{r}\) ) is a great circle segment in \(S^{2}\) and \(\mathcal{V}_{r}\) is equal to the intersection of the two hemispheres associated with the two end vectors of \(\mathcal{G}_{\mathrm{r}}\) (Figure 7).

Proof: Without loss of generality, one can assume \(R\) is a region of a cylinder around the \(z\) axis. That is, \(R(u, v)=(a \cos (u), a \sin (u), v)\). The unit normal of region \(R\) is equal to \(\mathcal{N}_{T}(u, v)=(-\cos (u),-\sin (u), 0)\) and is obviously a great circle segment on \(S^{2}\) that is also in the \(x_{y}\) plane. Call the great circle segment \(\mathcal{C}\).

Let \(\mathcal{H}\) be a hemisphere associated with a vector in \(\mathcal{C}\). Let \(\overrightarrow{\alpha_{1}}\) and \(\overrightarrow{\alpha_{2}}\) be the two vectors of the end points of the arc of \(\mathcal{C}\) and let \(\mathcal{H}_{1}\) and \(\mathcal{H}_{2}\) be the two hemispheres associated with \(\overrightarrow{\alpha_{1}}\) and \(\overrightarrow{\alpha_{2}}\), respectively. \(\partial \mathcal{H}\), the great circle boundary of \(\mathcal{H}\), is in a plane that always contains the \(z\) axis. Therefore, by moving the vector \(\vec{\alpha}\) along \(\mathcal{C}\) in the \(x_{y}\) plane, the great circle \(\partial \mathcal{H}\) rotates around the \(z\) axis. This transformation is continuous and monotone, when \(R\) is regular. Since \(\overrightarrow{\alpha_{1}}\) and \(\overrightarrow{\alpha_{2}}\) provide the two extreme locations and \(\mathcal{H}_{1}\) and \(\mathcal{H}_{2}\)

Corollary 2 Suppose the Gauss map of \(S\) is two isolated points on \(S^{2}\). Then, \(\mathcal{V}_{s}\), is the same as if \(\mathcal{G}\), was the great circle segment connecting the two vectors on \(S^{2}\).

Given \(\mathcal{G}_{\text {, }}\), for any two vectors \(\overrightarrow{\alpha_{1}}, \overrightarrow{\alpha_{2}} \in \mathcal{G}_{\text {s }}\), one can in clude a great circle segment between them, selecting the smaller one ( \(\overrightarrow{\alpha_{1}}\) and \(\overrightarrow{\alpha_{1}}\) have at least two such segments, one that is greater then or equal to 180 degrees and one that is less than or equal to that), without affecting \(\mathcal{V}_{s}\). Much like a planar convex hull, in which for each two points in the convex hull, the line segment between the two points is also in the convex hull, for each two points in a central convex hull on \(S^{2}\), the great circle segment between them is also contained in the central convex hull:

![Figure 6](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-6-p006.png)

*Figure 6: Central convex hull (dashed) of the silhouette and boundary curves of Af, in Figure 4.*

Deflnition 10 The central convex hull, \(\mathrm{CH} \subset S^{2}\), of some set \(S \subset S^{2}\), is the smallest subset of \(S^{2}\) containing \(S\) bounded by a centrally convex curve (definition 8).

The edges of \(\mathcal{C} \mathcal{H}\) are great circle segments, seen as straight lines from the origin. For any two points in \(\mathcal{C} \mathcal{H}\), the great circle segment on \(S^{2}\) between them is completely in \(\mathcal{C H}\). Specifically, for any two points in \(\mathcal{G}_{s}\), one can add the great circle segment between them having no affect on the visibility set. Applying Corollary 2 allows one to employ the The convex hull must be computed centrally. That is, edges of the convex hull are great circle segments on \(S^{2}\) (see Figures 6 and 8). Optimal planar convex hull algorithms have been known for sometime [1,14]. We cannot use planar convex hull algorithms directly, since we are interested in the central convex hull. A central projection from \(S^{2}\) onto a plane (definition 7) that maps great circles to straight lines is first employed. Then, we apply the planar convex hull algorithm to the two dimensional planar set only to centrally project the edges of the convex hull back onto \(S^{2}\) as great circles. \(\mathcal{G}\), and \(\mathcal{V}\), are required to strictly fit into a hemisphere so that the mapping to a plane is homeomorphic, a require ment equivalent to the constraint for the surface to be visible in the local from at least one direction. Satisfying this re quirement always allows one to uniquely project great circle

![Figure 7](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-7-p007.png)

*Figure 7: Let G, be a great circle segment. Then, the boundary of V, (dotted) is the boundary of the intersection of the two Fijrure 7: Let G, be a meat circle segment. Then, the boundary of V. (dotted) is the boundary of the intersection of the two he~ispheres ~sociate~ with the en~vectors of ~s.*

segments ss line segments on the Z = 1 plane. It is necessary for neither ~, nor V. to be in the Z > 0 hemisphere. Instead, a rotation, 72., could map ~s or V, into the upper hemisphere. Further, if P is the plane through the origin that dichotomizes S2 into two hemispheres, one strictly containing ~, (or V.), then 72 is the mapping that transforms the normal of P to the z axis. One can find P by using loose bounds such as bounding cones [16, 19] or by computing the three dimensional convex hull of g, (or Vs). Alternatively, an \(O(n)\) algorithm to rotate points on a unit sphere as far away from the equator as possible, is described in [3].

Therefore, an algorithm to compute the central convex hull of \(\mathcal{G}\), for surface \(S(u, v)\) follows, algorithm 1

$$
\( \overline{\mathcal{G}} \), , central convex hull Gauss map of \( S(u, v) \);
$$

$$
\( \hat{\mathcal{N}}_{s}(u, v) \Leftarrow \) unnormalized normal surface of
$$

$$
\begin{equation*} \mathcal{V}_{s}=\bigcap_{f_{1} \in \mathcal{F}} \mathcal{H}_{i} \tag{5} \end{equation*}
$$

\(S(u,v)\); B < Boundaries of ~.(u, v), projected onto S2 ; S e Central silhouettes of fi,(a,v), as the zero set of (~~,~), projected onto S2; 'R e Flotation to map B andS to the Z>O hemisphere; ~~ + Central convex hull of \(R(BuS)\);

In section \(4, \overline{\mathcal{G}}\), is used to compute the visibility set of \(S(u, v), \mathcal{V}_{s}\).

## 4 Computing the Vkibility Set

\(\overline{\mathcal{G}}_{s}\) is now used to compute a tight bound on \(\mathcal{V}_{s}\).

Lemma 3 The visibility set derived from~, i~the~ame thevisibility setderivedjrom the boundoryof g,, 8GS. as Proof: Recall that \(\overline{\mathcal{G}}\), is centrally convex. For each interior vector \(\vec{\alpha} \in \overline{\mathcal{G}}_{\text {, }}\), there exists a great circle segment \(\mathcal{C} \subset \overline{\mathcal{G}}_{\text {, }}\), such that \(\vec{\alpha} \in \mathcal{C}\) and the two end vectors of \(\mathcal{C}\) are in \(\partial \overline{\mathcal{G}}\). Since the visibility set of \(\mathcal{C}\) can be determined from its two end vectors in \(\partial \overline{\mathcal{G}}\), by Lemma 2, we conclude that it is enough to examine only (the vectors in) \(\partial \overline{\mathcal{G}}\), in order to determine visibility set from \(\overline{\mathcal{G}}\), m The approximated boundary of \(\overline{\mathcal{G}}\), is a set of great cir cle segments. By Lemma 2, it follows immediately that it is enough to examine the end vectors of these great circle segments in order to determine the visibility of \(\overline{\mathcal{G}}\), (and \(\mathcal{G}_{s}\) ).

Lemma 3 suggests an efficient way to compute \(\mathcal{V}_{3}\) from \(\overline{\mathcal{G}}_{g}\). Given the set of vertices of \(\partial \overline{\mathcal{G}}, \mathcal{F}\), we associate a hemisphere \(\mathcal{H}_{i}\) (Figure 5) with each vertex \(f_{i} \in \mathcal{F}\). The intersections of all these hemispheres is \(\mathcal{V}_{s}\) :

Asin section 3, one can use the central projection and project these hemisphere boundaries (great circles) onto the plane Z= lfromthe ori in. These great circles are mapped P tolines intheplane(?f, , theprojection of 'Hi, is now a half plane defined by a fine). Furthermore, since ~, is centrally convex, the intersection problem is reduced to intersecting each line in the plane only with its two neighbors, the previous fine and the next line. Therefore, the complexity of thk stage is linear (see algorithm 1 for R):

$$
\overline{\mathcal{G}}_{s} \Leftarrow \mathcal{R}^{-1}\left(\overline{\mathcal{G}}_{\cdot}^{P}\right) ;
$$

algorithm 2

![Figure 8](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-8-p008.png)

*Figure 8: Convex hull (dashed) is computed for the projected great circles as lines in the plane Z = 1, using central (of surface in figure 2) projection*

~,, central convex hull of the image of ~,; : V,, tightly bounded visibility set of S; tit + hemispheres associated with vertices of 7?(F.); ?i~ ~ ~H, centrally projected on plane z=]; V: e intersection set of 13?i, half planes; V, * 'R-l (V~) mapped back to S2;

## 5 Extensions

Bounding cones based methods [16, 19] usually examine the entire parametric domain of the surface. Adopting these methods to support trimmed surfaces can be difficult. In contrast, the method presented herein can be easily ex tended to support trimmed surfaces. The boundary of the Gauss map will be computed for the trimmed boundary curves of \(\dot{\mathcal{N}}_{s}(u, v)\), and its trimmed central silhouette curves. No other part of the algorithms developed herein need to be changed. Figure \(10(a)\) shows a trimmed surface constructed from the surface in Figure 2. In Figure 10(b), the extracted silhouette and boundary curves of its Gauss map, its convex hull, and the visibility set (in dotted lines), are all shown mapped onto \(S^{2}\). Figure 11(a) shows a trimmed region out of \(S^{2}\). Obviously, the Gauss map of this surface is identical to the surface itself. In Figure 11(b) the Gauss map with its convex hull and the resulting visibility set are shown.

Given a model \(\mathcal{M}\) consisting of several, possibly trimmed, surfaces one can now answer the query, whether or not there exists a direction from which all surfaces are visible. By computing \(\mathcal{V}_{s}\) for each surface, such a direction exists iff \(\bigcap_{i, \in \mathcal{M}} \mathcal{V}_{i,} \neq \phi\). Furthermore, any vector from the centrally convex set of \(\bigcap_{s, \in \mathcal{M}} \mathcal{V}_{s,}\) can be exploited as a direction from which all surfaces of \(\mathcal{M}\) are visible in the local.

## 6 Conclusion

An algorithm to provide a tight bound on the visibility di rections of a given surface \(S(u, v)\) is described, combined with an algorithm to compute bounds on the Gauss map of \(S\). This bound is tight since it provides the (centrally con vex) visibility set \(\mathcal{V}\), of \(S(u, v)\). The algorithm can be easily extended to provide a tight visibility bound for a trimmed surface, and/or a set of surfaces.

The symbolic computation has a fixed complexity, given the order and continuity of the surface. The complexity of the convex hull computation of the image of the Gauss map is \(n \log (n)\), where \(n\) is the number of vertices, which is the optimal time. The visibility set is computed in linear time from the Gauss map. The silhouette extraction (zero set of \(\left\langle\hat{\mathcal{N}}_{s}(u, v), \hat{\mathcal{N}}_{s}^{2}(u, v)\right\rangle\) ) is the only numeric computation in this algorithm. Subdivision based techniques [10] were used to compute its zero set.

## 7 Acknowledgment

The authors are grateful to Rich Riesenfeld for his valuable remarks on the various drafts of this paper.

## References

- K. R. Andreson. A Reevaluation of an efficient algorithm for Determining the Convex Hull of a Finite planar Set. Information Processing letters 7 (1978).5355. M. P. DoCarmo. Differential Geometry of curves and Surfaces. Prentice-Hall 1976. L. L. Chen and T. C. Woo. computational Geometry on the Sphere With applications to Automated Machining, Technical Report No. 89-30, Department of Industrial and Operations engineering, University of Michigan, August 1989. L. L. Chen, Shuo-Yan Chou, and T. C. Woo. Separating and Intersecting Spherical Polygons: Computing Machinability on Three-, Fourand Five-Axis Numerically Controlled Machines. ACM Transaction on Graphics, Vol. 12, No. 4, pp 305-326, october 1993.

- Figure 9: V. (dotted) is computed as intersection of hemisphere boundaries (great circles) of ~, vertices (dashed) as lines onto the plane Z = 1 and mapped back (of surface in Figure 2). projected r. F

- Figure 10: A trimmed region from the surface in Figure 2 is shown in (a). In (b), shown are its ~, (dashed), the and boundary curves of its Af..(u, v), and its V, (dotted). silhouette

- (a) (a) Figure I1: In (a). is a trimmed region from S°. In (b). is its G.. G. (dashed). and V. (dotted). Figure I 1: In (a), is a trimmmj region from.5'2 (b)

- S. lyanaga. }'. Kawarla and K O. hlay. Encyclopedic I)ic[iouary of Afatbernatics. The M1'1'Press ~'ambricfge, ilassachusetts. and London, England.

- [(i] (;. l~arin ('Ilrves and Surfaces for (''ornputer Aided (;comctric. Iksign \cademic Prc>s, Inc. Third Edition 199:1.

- [~1 R. '1'.Farouki and \'. 'I'. Rajan. algorithms For F'olynomials In Bernstein IJorm Computer Aided Geometric [)esign 5. pp 1-26, 1!)88.

- ('~. Elbcr and E. ('ohell. Hidden C'urve removal for LInt rimmed and 'lrimmed N(JRf3 Surfaces. Technical Report No. 89-019. c'omputer Science, University of ('lab.

- [!1] (;. Elber and E. ~'ohen. Hidden (''urve removal for Free Form Surfaces SIGGR.\PH 90, pp 9.5-104.

- (;. Kltxr. Free Form Surface analysis using a Hybrid of Symbolic and Numeric Computation Ph.D. thesis. l'ui~ersily of (It Al, ('ompnt(r %icnce I)epart ment, 1992.

- (; l;lber an(l E. C'ohcn. Second order Surface analysis-lsing tf~t,ri(i Synlbolic and Numeric Operators. ACM '1'ransart ion on ('; raphics, Vol. 12, No. 2, pp 160-178,:\pril 19$1:!.

- (;. Elbcr and E. Coheli. Hybrid Symbolic and Numeric operators as Tools for analysis of Freeform Surfaces. h!odeliug in ('omputer Graphics, B. Falcidieno and 1'. l,. Kunii (Eds.), \Vorking C'onferencc on Geometric Modeling in Conlputer Graphics (IFIP TC 5 WC 5.10), (: f,llm'a 199.1.

- [1:]] (;. f;ltwr and E. ('oheu. Error Bounded Variable Dist ante CMfs-,t Operator for Free Form curves and Surfaces. luternationat Journal of ~ornputational Geornetry and Applications. Vol. 1., No. 1. pp 67-78, March 199[.

- R 1,. Graham. An Efficirnt algorithm for Determining the ('OUVCXHull of a Finite planar Set. Information Processing letters 1 (1972) 13?-133. ill. E. Hohmeyer. A SUrfa(c lntcrsectiorr algorithm Based on loop t)etettiou Symposium in Solid Mod(ling Foundations and C'AI)-' A\l Applications. Austin, 'rexas, June 5-7, 1991. I), S. Kim. ('ones on Bfzier ('urves and Surfaces. Ph.]). dissertation, T'nivcrsity of Nlichigan. 19!)1). R. S. hfillman and (;. 1). Parker. Elements of I)iffer~ntial Geometry. Prentice-Hall Inc. 1977. K. Morken, Some ldentitir+ for Products and Degree Raising of Splines. ('onstructivc:ipproximation 7, pp 195-209, 1991. T. W_. Se&rberg and Ray J. Meyers. Loop Detection in Surface Patr-h Intersmtions. ('omputer Aided ~;eometric Design.5, pp 161-171, 198A', S. H. Suh and 1. K. fiang. Process Planning for \lultiAxis NC \lachining of Free Surfaces. To Appear in IJPR. 'I'. J. '1'seng and S. Joshi. Determining F,a+ible 'l'ooapproach Directions for Machining Bezier ('urves and Surfaces. Computer Aided Design. Vol. ~:;, No, 5. pl~ 367-378, June 1991.
