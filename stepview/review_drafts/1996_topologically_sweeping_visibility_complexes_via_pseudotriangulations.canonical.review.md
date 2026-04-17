# Topologically Sweeping Visibility Complexes via Pseudotriangulations

M. Pocchiola, G. Vegter, G. Vegter z

Inc.
1D6partement de Math6matiques et Informatique, Ecole normale sup6rieure, ura 1327 du CNRS, 45 rue d'Ulm, 75230 Paris Cedex 05, France
ura 1327 du CNRS, 45 rue d'Ulm, 75230 Paris Cedex 05, France 2Department of Mathematics and Computer Science, University of Groningen, EO. Box 800, 9700 AV Groningen, The Netherlands

## Abstract

This paper describes a new algorithm for constructing the set of free bitangents of a collection of \(n\) disjoint convex obstacles of constant complexity. The algorithm runs in time \(O(n \log n+k)\), where \(k\) is the output size, and uses \(O(n)\) space. While earlier algorithms achieve the same optimal running time, this is the first optimal algorithm that uses only linear space. The visibility graph or the visibility complex can be computed in the same time and space. The only complicated data structure used by the algorithm is a splittable queue, which can be implemented easily using red-black trees. The algorithm is conceptually very simple, and should therefore be easy to implement and quite fast in practice. The algorithm relies on greedy pseudotriangulations, which are subgraphs of the visibility graph with many nice combinatorial properties. These properties, and thus the correctness of the algorithm, are partially derived from properties of a certain partial order on the faces of the visibility complex.

## 1 Introduction

visibility graphs (for polygonal obstacles) were introduced by Lozano-P6rez and Wesley [18] for planning collision-free paths among polyhedral obstacles; in the plane a shortest euclidean path between two points runs via edges of the visibility graph of the collection of obstacles, augmented with the source and target points. Since then numerous papers have been devoted to the problem of their efficient construction

* A preliminary version of this work appeared in the Proceedings of the 1 lth Annual ACM Symposium on computational Geometry, Vancouver, June 1995, pages 248-257.

[4], [8], [10]-[12], [14], [23]-[25], [27], [29], [30] as well as their characterization (see [1], [2], [6], [22], [26], and the references cited therein).

This paper describes a new algorithm for constructing the (tangent) visibility graph of a collection \(\mathcal{O}\) of \(n\) disjoint convex obstacles of constant complexity. Its running time is \(O(n \log n+k)\), where \(k\) is the output size, and its working space is linear. The algorithm is extendible to the case where the objects are allowed to touch each other. Therefore, our method can be adapted to compute the (classical) visibility graph of a set of disjoint polygons in the plane (e.g., by triangulating the polygons and applying the extended version of our algorithm to the collection of edges of the triangulation). While earlier algorithms [10], [12], [14], [24] achieve the same optimal running time, under various assumptions on the nature of the obstacles (see Table 1), this is the first optimal algorithm that uses only linear space. The only complicated data structure used by the algorithm is a splittable queue, which can be implemented easily using red-black trees. The algorithm is conceptually very simple, and should therefore be easy to implement and quite fast in practice. We are convinced that the algorithm also works for obstacles of nonconstant complexity; see Section 3.4.5.

Recall that a bitangent is a closed line segment whose supporting line is tangent to two obstacles at its endpoints; it is called free if it lies in free space (i.e., the complement of the union of the relative interiors of the obstacles). An exterior (resp. interior) bitangent is a bitangent lying on the boundary of (resp. in the interior of) the convex hull of the collection of obstacles. We denote by B the set of free bitangents of the collection of obstacles. The endpoints of these bitangents subdivide the boundaries of the obstacles into a sequence of arcs; these arcs and the free bitangents are the edges of the visibility graph of the collection of obstacles, as illustrated in Fig. 1. Our main result is the following.

Theorem 1. Let \(B\) be the set of free bitangents of a collection \(\mathcal{O}\) of \(n\) pairwise disjoint obstacles, and let \(k\) be the cardinality of \(B\). There is an algorithm that computes the set \(B\) in \(O(k+n \log n)\) time and \(O(n)\) working space-under the assumption that the bitangents between two obstacles are computable in constant time. Furthermore, if desired, the algorithm can compute the visibility graph (or the visibility complex) of the collection of obstacles in the same space and time bounds.

![Figure 1. The visibility graph of a collection of four obstacles.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-1-p003.png)

*Figure 1. The visibility graph of a collection of four obstacles.: The visibility graph of a collection of four obstacles.*

Our approach is to turn \(B\) into a poset (partially ordered set) ( \(B, \leq\) ) and to compute a linear extension of \((B, \leq)\), i.e., to embed \(\leq\) into a linear (total) order. In other words, we solve the topological sorting problem [15], [16] for ( \(B, \preceq\) ).

To define this partial order, we first introduce some terminology. The set of unit vectors in the plane is the 1-sphere \(\mathcal{S}^{1}\). Let \(\exp : \mathcal{R} \rightarrow \mathcal{S}^{1}\) be the universal covering map of the 1-sphere, defined by \(\exp (u)=(\cos u, \sin u)\). Furthermore, let \(B^{\text {or }}\) be the oriented version (double cover) of \(B\), obtained by associating with each \(b \in B\) the two directed versions of \(b\). The subset \(X_{0}\) of \(B^{\text {or }} \times \mathcal{R}\) is defined by

$$
X_{0}=\left\{(v, u) \in B^{\text {or }} \times \mathcal{R} \mid \exp (u) \text { is the unit vector along } v\right\} .
$$

A point \(b=(v, u)\) in \(X_{0}\) is called a bitangent in \(X_{0}\); the unoriented version of the bitangent \(v \in B^{\text {or }}\) is denoted by \(\operatorname{bit}(b) ; u \in \mathcal{R}\) is called the slope of \(b\), denoted by Slope ( \(b\) ). We identify a bitangent in \(B\) with the corresponding bitangent in \(X_{0}\) with slope in \([0, \pi)\). Two bitangents \(b\) and \(b^{\prime}\) in \(X_{0}\) are crossing, disjoint, etc., if the corresponding bitangents bit(b) and bit(b') in \(B\) are crossing, disjoint, etc., as subsets of the plane.

The (partial) order \(\leq\) on \(X_{0}\) is defined as follows: \(b \leq b^{\prime}\) if there is a counterclockwise oriented curve joining (some point of) bit(b) to bit(b'), that runs along the edges (arcs and bitangents) of the visibility graph of the obstacles, and that sweeps an angle of Slope \(\left(b^{\prime}\right)\) - Slope (b), as illustrated in Fig. 2. This order has several nice properties, on which our algorithm is based. At this point we just mention that two crossing bitangents are comparable with respect to \(\leq\) (see Lemma 7). Since \(\leq\) is compatible with the slope order on \(X_{0}\), an obvious extension of \(\leqq\) is the linear order obtained by sorting the elements of \(X_{0}\) according to increasing slope. However, this is computationally too expensive. To obtain the proper setting for dealing with the problem of extending \(\leq\) to a linear order on \(X_{0}\), we use the notion of filter. \({ }^{1}\) A special type of filter of \(X_{0}\) is the subset of bitangents

A filter 1 of a poset (P, · is a subset of P such that if x 6 1 and x _< y, then y E 1. The set of filters, ordered by reverse inclusion, is a poset. Our main interest in the notion of filter is that, given two filters 1 and J with \(J^{c}\) I and 1 \ J finite, the sequence x l, x2. . . . . xk of elements of 1 \ J is a linear extension of (l \ J, 5) if and only if the sequence of sets 11, 12. . . . . lk, defined by li \ J = {xi, Xi+l..... xk }, is an unrefinable chain of filters in the interval [1, J]. We borrow poset terminology from Stanley [28, Chapter 3] and McMullen [19]. To keep the paper self-contained, we review this terminology in Appendix A.

![Figure 2. A counterclockwise oriented curve with initial point x, terminal point y, and two cusp points. The two cusp points subdivide the curve into three regular smooth counterclockwise subcurves, i.e., each of these three subcurves can be described by a function f](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-2-p004.png)

*Figure 2. A counterclockwise oriented curve with initial point x, terminal point y, and two cusp points. The two cusp points subdivide the curve into three regular smooth counterclockwise subcurves, i.e., each of these three subcurves can be described by a function f: [0, 1] ~ R2 with ft(t) = Ift(t)l exp(0(t)) # 0, where O(t) is a continuous nondecreasing function. By definition the angle swept by the regular subcurve f is 0(1) - 0(0), and the angle swept by the curve is the sum of the angles swept by its regular subcurves. In the example the angle swept between the two rays starting at x and y is slightly over 2yr.*

\(I(u)\), defined for \(u \in \mathcal{R}\), that consists of all bitangents in \(X_{0}\) whose slope is greater than \(u\). For each filter \(I\) of ( \(X_{0}, \leq\) ) we define a maximal subset \(G(I)=\left\{b_{1}, \ldots, b_{m}\right\}\) of \(I\) as follows: (1) \(b_{1}\) is minimal in \(I\), and (2) for \(1 \leq i<m\), the bitangent \(b_{i+1}\) is minimal in the set of bitangents in \(I\), disjoint from \(b_{1}, b_{2}, \ldots, b_{i}\). Since crossing bitangents are comparable it follows that \(G(I)\) is well defined (independent of the choice of the \(b_{i}\) ), and that \(\min _{\preceq} I \subseteq G(I)\). We prove that for each filter \(I\) the set \(G(I)\) contains \(3 n-3\) bitangents, that subdivide free space into regions called pseudotriangles. This subdivision, also denoted by \(G(I)\), is called a greedy pseudotriangulation. The regions owe their name to their special shape, that is explained in more detail in Section 2. We refer to Fig. 3 for an example of greedy pseudotriangulations associated with filters of \(X_{0}\).

Our algorithm maintains the greedy pseudotriangulation \(G(I)\) as \(I\) ranges over a maximal chain of filters of the interval \([I(0), I(\pi)]\), namely the set of filters \(I\) with \(I(0) \supseteq I \supseteq I(\pi)\). The basic operation that updates the pseudotriangulation is a flip of a free bitangent, minimal in the filter. The key result is the following.

Theorem 2. Let \(I\) be a filter of \(\left(X_{0}, \leq\right)\) and let \(b \in \min _{\leq} I\). Then \(G(I \backslash\{b\})\) is obtained from \(G(I)\) by flipping \(b\), i.e., by replacing \(b\) with the only minimal bitangent in \(I \backslash\{b\}\) disjoint from the other bitangents in \(G(I)\) (see Fig. 3).

If the obstacles are points, our method--translated into dual space is an alternative for the topological sweep algorithm for arrangements of lines, of Edelsbrunner and Guibas [8]. Our pseudotriangulations replace their (upper and lower) horizon trees.

The paper is organized as follows. In Section 2 we recall the definition of the visibility complex \(Y\) of the collection of obstacles, a cell complex on the space \(\mathcal{S}^{2} \times \mathcal{S}^{1}\) carrying the view from points (in \(\mathcal{S}^{2}\), the plane \(\mathcal{R}^{2}\) together with the point at infinity) along a direction (in \(\mathcal{S}^{1}\) ).

The set \(X_{0}\), introduced in this section, is the set of vertices (0-faces) of the universal

![Figure 3. (a) The greedy pseudotriangulation associated with the filter 1 (0) of bitangents with slope >_ 0. The dashed bitangents bl and b2 are both minimal in the filter 1 (0). (b) The greedy pseudotriangulation associated with the filter l(0)\{bl, b2} which is obtained from G(I(O)) by flipping bl and b2.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-3-p005.png)

*Figure 3. (a) The greedy pseudotriangulation associated with the filter 1 (0) of bitangents with slope >_ 0. The dashed bitangents bl and b2 are both minimal in the filter 1 (0). (b) The greedy pseudotriangulation associated with the filter l(0)\{bl, b2} which is obtained from G(I(O)) by flipping bl and b2.: (a) The greedy pseudotriangulation associated with the filter 1 (0) of bitangents with slope >_ 0. The dashed bitangents bl and b2 are both minimal in the filter 1 (0). (b) The greedy pseudotriangulation associated with the filter l(0)\{bl, b2} which is obtained from G(I(O)) by flipping bl and b2.*

cover \(X\) of \(Y\), which is a cell complex on the universal cover \(\mathcal{S}^{2} \times \mathcal{R}\) of \(\mathcal{S}^{2} \times \mathcal{S}^{1}\), induced by the universal covering map exp: \(\mathcal{R} \rightarrow \mathcal{S}^{1}\) on the second component. We introduce the partial order \(\leq\) on the cover \(X\) and we prove that this order satisfies a "minimum-element" property: the set of bitangents greater than a given bitangent and crossing it has a minimum element. Then we prove Theorem 2 by interpreting the greedy pseudotriangulations as maximal antichains of \(\leq\) on \(X \backslash X_{0}\). In Section 3 we show how the flip operation can be efficiently implemented, using splittable queues.

## 2 The Visibility Complex

### 2.1 Terminology: Pseudotriangles and Pseudotriangulations

Let \(\mathcal{O}=\left\{O_{1}, O_{2}, \ldots, O_{n}\right\}\) be a collection of \(n\) pairwise disjoint closed convex sets \(O_{i}\) (obstacles for short). We assume that the obstacles are (1) strictly convex (i.e., the open line segment joining two points of an obstacle lies in its interior), (2) smooth (i.e., there is a well-defined tangent line through each boundary point), and (3) in general position (i.e., no three obstacles share a common tangent line). In particular two bitangents in \(B\) are disjoint or intersect transversally (i.e., not at their endpoints). These assumptions are only for ease of exposition. The general case can be treated by standard perturbation techniques; for example, to cover the case where obstacles are allowed to be points and disjoint line segments the perturbation scheme may, e.g., consist of taking the Minkowski sum with an infinitesimally small circle. A pseudotriangulation of a set of obstacles is the subdivision of the plane induced by a maximal (with respect to inclusion) family of pairwise noncrossing free bitangents. It is clear that a pseudotriangulation always exists and that the bitangents of the boundary of the convex hull of the obstacles are edges of any pseudotriangulation. Two pseudotriangulations of a collection of four obstacles are depicted in Fig. 3. The subdivision owes its name to the special shape of its regions. A

![Figure 4.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-4-p006.png)

*Figure 4.: (a) A pseudotriangle. (b) Two disjoint pseudotriangles share exactly one common tangent line.*

pseudotriangle is a simply connected subset \(T\) of the plane, such that (i) the boundary \(\partial T\) consists of three convex curves, that share a tangent at their common endpoint, and (ii) \(T\) is contained in the triangle formed by the three endpoints of these convex chains. See Fig. 4(a). These three endpoints are called the cusps of \(T\). At each boundary point of a pseudotriangle there is a well-defined tangent line, and there is a unique tangent line to the boundary of a pseudotriangle with a given unoriented direction (more formally the support function \(\varphi_{T}: \mathcal{S}^{1} \rightarrow \mathcal{R}\) of \(T\) is well defined, continuous, and satisfies \(\varphi_{T}(u)=-\varphi_{T}(-u)\) ).

Lemma 3. The bounded free regions of any pseudotriangulation are pseudotriangles. Furthermore, the number of pseudotriangles (of a pseudotriangulation of a collection of \(n\) obstacles) is \(2 n-2\), and the number of bitangents is \(3 n-3\).

Proof. Let \(R\) be a family of noncrossing free bitangents containing the bitangents of the boundary of the convex hull of the collection of obstacles. Assume that some free bounded face of the subdivision is not a pseudotriangle; from this we derive that \(R\) is not maximal. This means that this face is not simply connected or that its exterior boundary contains at least four cusp points. In both cases we add to \(R\) a bitangent as follows. Take the minimal length closed curve, homotopy equivalent to the exterior boundary of the face, and going through all cusp points of the exterior boundary but one. This closed curve contains a free bitangent not in \(R\); hence \(R\) is not maximal.

An extremal point is a point on the boundary of an obstacle at which the tangent line to that obstacle is horizontal. Each pseudotriangle contains exactly one extremal point in its boundary (namely the touch point of the horizontal tangent line to the pseudotriangle). Since there are \(2 n-2\) extremal points in the interior of the convex hull of the obstacles there are exactly \(2 n-2\) pseudotriangles. The last result is then an easy application of the Euler relation for planar graphs. To see this, observe that the set of vertices consists of all endpoints of bitangents. In particular every vertex has degree 3. Furthermore, the number of edges, that lie on the boundary of some object, is equal to the number of

![Figure 5. A pseudoquadrangle and its diagonals.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-5-p007.png)

*Figure 5. A pseudoquadrangle and its diagonals.: A pseudoquadrangle and its diagonals.*

vertices. Finally, the total number of bounded regions is equal to the sum of the number of pseudotriangles and the number (n) of obstacles. []

Lemma 4. Let \(T\) and \(T^{\prime}\) be two disjoint pseudotriangles. Then \(T\) and \(T^{\prime}\) have exactly one common tangent line. (See Fig. 4(b).)

Proof. For the existence part we apply the Intermediate Value Theorem to the continuous function defined as the difference between the support functions of \(T\) and \(T^{\prime}\). For the uniqueness we observe that tangent lines to a pseudotriangle cross inside the pseudotriangle.

We use this last lemma only in the case where \(T\) and \(T^{\prime}\) are adjacent pseudotriangles (in a pseudotriangulation). In that case the union of \(T\) and \(T^{\prime}\) is called a pseudoquadrangle, and \(T\) and \(T^{\prime}\) share two common bitangents called the diagonals of the pseudoquadrangle (see Fig. 5).

### 2.2 Definition of the Visibility Complex Revisited

The visibility complex was defined in [24] as a partition of the set of free rays. Here we define the visibility complex as a partition of the whole set of rays (free or not free) augmented with rays at infinity. This slight modification simplifies the description of the combinatorial structure of the visibility complex and, in particular, of its cross sections.

We identify the plane \(\mathcal{R}^{2}\) with a 2-sphere \(\mathcal{S}^{2}\) minus a point, called the point at infinity. Given a real number \(u \in \mathcal{R}\) let \(C_{u}\) be an infinite strip, centered around a line through the origin with slope \(u+\pi / 2\), large enough to contain all the obstacles. We denote by \(L_{u}\) and \(R_{u}\) the two connected components of \(\mathcal{R}^{2} \backslash C_{u}\), where \(L_{u}\) comes before \(R_{u}\) along

![Figure 6. The infinite strip Cu.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-6-p008.png)

*Figure 6. The infinite strip Cu.: The infinite strip Cu.*

lines with direction \(\exp (u)\) (see Fig. 6). The \(u\)-free space \(F_{u}\) is the closure of \(C_{u} \backslash \cup \mathcal{O}\). A ray ( \(p, u\) ) is an element of \(\mathcal{S}^{2} \times \mathcal{R}\), consisting of a point \(p\) and a real number \(u\). The point \(p\) is called the origin of the ray, and the real number \(u\) is called its slope. We denote by \(\gamma_{+i}\) (resp. \(\gamma_{-i}\) ) the set of rays ( \(p, u\) ) emanating from and tangent to obstacle \(O_{i}\) (i.e., \(p \in \partial O_{i}\) and the tangent vector at \(p\) to \(O_{i}\) is \(\exp (u) \in \mathcal{S}^{1}\) ), that contain \(O_{i}\) in their left (resp. right) half-plane; obviously \(\gamma_{+i}\) and \(\gamma_{-i}\) are homeomorphic to \(\mathcal{R}\). Similarly, we denote by \(\gamma_{+\mathcal{O}}\) (resp. \(\gamma_{-\mathcal{O}}\) ) the set of rays ( \(p, u\) ) emanating from and tangent to the convex hull of the set of obstacles.

Let \(C_{i}=O_{i} \times \mathcal{R}\), and let \(C_{-}=\bigcup_{u \in \mathcal{R}} L_{u} \times\{u\}\) and \(C_{+}=\bigcup_{u \in \mathcal{R}} R_{u} \times\{u\}\). For a point \(p\) in \(\mathcal{R}^{2}\) and a real number \(u \in \mathcal{R}\) we are interested in the object (possibly \(L_{u}\) or \(R_{u}\) ) that we can see from \(p\) in the direction \(\exp (u) \in \mathcal{S}^{1}\). This object is called the view from \(p\) along \(u\), or the forward view from the ray \((p, u)\) (the backward view from the ray \((p, u)\) is the forward view of the opposite ray, \((p, u+\pi)\) ). By definition the backward (resp. forward) view from the point at infinity along \(u\) is \(L_{u}\) (resp. \(R_{u}\) ). The view from a point \(p\) inside an object \(O_{i}\) is this object \(O_{i}\), irrespective of the direction.

We define a cell complex \(X\), whose underlying space \(|X|\) is a quotient space of the space of rays \(\mathcal{S}^{2} \times \mathcal{R}\). More precisely, for \(p, q \in \mathcal{S}^{2}\) and \(u \in \mathcal{R}\), with \(p \neq q\), we declare \((p, u)\) equivalent to \((q, u)\) iff (1) the slope of the directed line from \(p\) to \(q\) is equal to \(u\), up to an integer multiple of \(\pi\), and (2) the line segment [ \(p, q\) ] lies in \(u\)-free space \(F_{u}\). In this situation we write \((p, u) \sim(q, u)\). The space \(|X|\) is the quotient space of \(\mathcal{S}^{2} \times \mathcal{R}\) under the reflexive, transitive closure of \(\sim\). By a slight abuse of terminology, an equivalence class is called a ray in \(|X|\). If we fix \(u \in \mathcal{R}\) the set of rays in \(|X|\) with slope \(u\) is a two-dimensional set, homeomorphic to \(\mathcal{S}^{2}\). We refer to this set as the cross section of \(|X|\) at \(u\). of the form ( \(q, u\) ), where the point \(q\) ranges over the largest line segment with slope \(u\) in \(F_{u}\), that contains \(p\). One may think of the cross section of \(|X|\) at \(u\) as obtained from \(\mathcal{S}^{2}\) by contracting \({ }^{2}\) the latter line segment, for all points \(p\) in free space. The reader may find it helpful to refer to the top half of Fig. 11. The rightmost part of that figure contains a schematic picture of the cross section of \(|X|\) at \(u=0\) (provided we forget about the

2 We refer to the video segment [7] for an illustration of this contraction process.

sets \(L_{0}\) and \(R_{0}\) are not depicted here). The subset \(F_{0}\) is subdivided into a number of strip-shaped regions. Each point on a labeled edge of the cross section corresponds to a maximal free horizontal line segment in the strip-shaped region having the same label. Also note that points inside an object constitute an equivalence class by themselves, giving rise to the two-dimensional regions in the cross section. It is not hard to see that the cross section is homeomorphic to \(\mathcal{S}^{2}\). In Fig. 11 the edge numbered 16 continues directly into the edge numbered 1 via the point at infinity.

The slope of an equivalence class \(r\), denoted by Slope( \(r\) ), is the common slope of its rays, and we denote by seg( \(r\) ) the set of origins of the rays in \(r\). Observe that seg( \(r\) ) is a maximal (with respect to the inclusion relation) free line segment, unless \(r=\{(p, u)\}\) Observe that the canonical mapping from \(\mathcal{S}^{2} \times \mathcal{R}\) onto \(|X|\), restricted to the interiors Inte \(\left(C_{i}\right)\) of \(C_{i}\), with \(i \in\{1, \ldots, n,+,-\}\), is one-to-one. The \(n+2\) canonical images of the sets Inte \(\left(C_{i}\right)\) and the \(2 n\) canonical images of the curves \(\gamma_{ \pm i}\) in \(|X|\) induce a threedimensional cell (or face) decomposition of \(|X|\), denoted \(X\). The 3-faces correspond to collections of rays with origins in the interior of the obstacles (including \(L_{u}\) and \(R_{u}\) ), i.e., the Inte \(\left(C_{i}\right)\), with \(i \in\{1, \ldots, n,+,-\}\). The 2-faces correspond to collections of rays with the same forward and backward views. The 1-faces correspond to collections of rays with the same forward and backward views and tangent to the same obstacle. The 0-faces correspond to collections of rays which are tangent to two obstacles. A face \(x\) is said to be bounded if Slope( \(x\) ) is a bounded subset of \(\mathcal{R}\), otherwise the face is said to be unbounded. The only unbounded faces are the 3-faces, and the 2-face that contains the rays whose origin is the point at infinity on \(\mathcal{S}^{2}\). We denote the sets of \(0-, 1-, 2-\), and 3-faces of \(X\) by \(X_{0}, X_{1}, X_{2}\), and \(X_{3}\), respectively, and the set of bounded 2-faces by \(X_{2}^{*}\).

Let \(\pi\) be the mapping which associates the ray ( \(p, u+\pi\) ) with the ray ( \(p, u\) ). Clearly, the (induced) mapping \(\pi:|X| \rightarrow|X|\) is an automorphism of the complex \(X\). The quotient complex \(Y:=X / \pi^{2}\) (whose underlying space is now \(\mathcal{S}^{2} \times \mathcal{S}^{1}\) ) is the visibility complex of the collection of obstacles. (In [24] the visibility complex was defined as the 2-skeleton Let \(P(X)\) be the poset of faces of \(X\), augmented with \(\emptyset\) and \(|X|\), ordered by the inclusion relation of their closures. Similarly, we define \(P(Y)\) to be the poset of faces of \(Y\). The local combinatorial structure of \(P(X)\) or \(P(Y)\) is described in the following theorem. (See Fig. 7 and also [24]. We refer to Appendix A for the terminology on abstract polytopes.)

Theorem 5. \(P(X)(P(Y))\) is an abstract polytope of rank 4. Furthermore, the vertexfigure of a vertex is the face poset of a three-dimensional simplex.

Note that there is a canonical mapping arc from the set \(X_{1}\) of edges of \(X\) onto the set of arcs on the boundaries of the obstacles (these arcs correspond to edges of the visibility graph of \(\mathcal{O}\), see Section 1). More precisely, for \(x \in X_{1}\), the arc \(\operatorname{arc}(x)\) consists of the origins of the rays in \(x\) emanating from the object to which they are tangent. The canonical mapping from the set \(X_{0}\) of vertices of \(X\) onto the set \(B\) of free bitangents of \(\mathcal{O}\) is denoted by bit; see Fig. 7. In particular, the preimage under the mapping bit of the

![Figure 7. (a) Two obstacles defining a vertex b of the visibility complex with slope u. (b) (Local) cross sections at slopes u - e, u, and u + e. (c) Neighborhood of a vertex of the visibility complex. (d) The Hasse diagram of the vertex-figure of a vertex of P(X)](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-7-p010.png)

*Figure 7. (a) Two obstacles defining a vertex b of the visibility complex with slope u. (b) (Local) cross sections at slopes u - e, u, and u + e. (c) Neighborhood of a vertex of the visibility complex. (d) The Hasse diagram of the vertex-figure of a vertex of P(X): (a) Two obstacles defining a vertex b of the visibility complex with slope u. (b) (Local) cross sections at slopes u-e, u, and u + e. (c) Neighborhood of a vertex of the visibility complex. (d) The Hasse diagram of the vertex-figure of a vertex of P(X)*

bitangent \([p, q]\) with slope \(u \in[0, \pi)\) is the set of rays \((p, u+k \pi), k \in \mathcal{Z}\). An element of \(X_{0}\) is called a bitangent in \(X_{0}\).

A pseudotriangulation in \(X\) is a maximal (with respect to the inclusion relation) family of pairwise disjoint bitangents in \(X_{0}\). Clearly, if \(G\) is a pseudotriangulation in \(X\), then (1) bit( \(G\) ) is a pseudotriangulation of the collection of obstacles, and (2) Card \(G=3 n-3\).

Let \(x\) be \(a_{1}\)-face (namely an edge) or a bounded 2-face in \(X\). We define sup \(x\) (resp. \(\inf x\) ) to be the ray with maximal (resp. minimal) slope in the closure of \(x\). The operator sup (resp. inf) is a one-to-one correspondence between the set of bounded 2-faces in \(X_{2}\) and the set of vertices in \(X_{0}\). For a vertex \(x\) we denote by \(\sup (x)\) the unique 2-face \(y\) with \(\inf (y)^{\prime}=x\). Similarly, \(\inf (x)\) is the unique 2-face \(y\) with \(\sup (y)=x\). In this way inf and sup are defined for all vertices, edges, and bounded 2-faces of \(X\).

For a bounded 2-face \(x\) the vertices \(\sup x\) and \(\inf x\) subdivide the boundary of \(x\) into two curves, called the upper and lower boundary of the face. Observe also that the boundary of the unbounded 2-face has two connected components that are the canonical images of the curves of rays \(\gamma_{+\mathcal{O}}\) and \(\gamma_{-\mathcal{O}}\).

Remark 6. The numbers of 0-, 1-, 2-, and 3-faces of the visibility complex \(Y\) are \(2 k, 4 k, 2 k+1\), and \(n+2\), respectively; here \(k\) is the number of free bitangents. This equality is a consequence of the previous discussion, namely on the bijection between the set of bounded 2-faces and the set of 1-faces, the shape of the vertex-figure, and the number \((n+2)\) of 3-faces. The number of flags of \(P(Y)\) is 24 times the number of vertices, i.e., \(48 k\).

### 2.3 The Poset (X, _) and the "Minimum-Element" Property

Now we turn \(X\) into a poset \((X, \preceq)\) by taking the transitive and reflexive closure of the relation \(\leq\), defined by

$$
\inf x \leq x \leq \sup x, \quad \forall x \in X_{1} \cup X_{2}^{*},
$$

i.e., for t, t' 6 X0 we have t _ t' if there exists a finite sequence of edges and or 2-faces xl. . . . . xt in X such that (1) t = infxl, (2) supxi = infxi+l, for i = 1. . . . . l-1, and (3) supxt = t'. Observe that we can replace each face that appears in the sequence Xl. . . . . xt by the sequence of edges of its upper (or lower) boundary. In other words, t _ _ _ t' if there is a counterclockwise oriented curve in the plane from bit(t) to bit(t') that runs along the edges (arcs and bitangents) of the visibility graph of the obstacles (namely the arcs arc(x) and the bitangents bit(v) with vi = infxi, where we assume that xi are edges), and which sweeps an angle of Slope(t') -Slope(t). Clearly, ~_ is compatible on X0 with the slope order. Observe that for all \(x_{6}\) X1 t_ X~ the cell supx (resp. x) covers the cell x (resp. infx). Finally note that the unbounded cells are isolated points in (X, ~).

Observe that if two bitangents belong to the boundary of a pseudotriangle of some pseudotriangulation, then they are comparable. The same conclusion holds if the two bitangents are the diagonals of some pseudoquadrangle (namely the union of two adjacent pseudotriangles) of some pseudotriangulation. From this observation we deduce a more general condition of comparability.

Lemma 7. Let t and t ~ be two bitangents in Xo.

- lfbit(t) and seg(t') are crossing, then t and t' are comparable with respect to ~.

- If seg(t)\bit(t) and seg(t')\bit(t') are crossing, say in point p, and if there is no free line segment emanating from p, tangent to an obstacle in (9, and lying in the wedge t+ \t'+ (here t+ is the open half-plane bounded by the supporting line of bit(t), that contains the line segment bit(f)), then t and t' are comparable with respect to ~.

- t ~ yrk(t'),for all sufficiently large k.

Proof. Assume first that \(\operatorname{bit}(t)\) and \(\operatorname{bit}\left(t^{\prime}\right)\) are crossing. Clearly it suffices to prove that bit( \(t\) ) and bit \(\left(t^{\prime}\right)\) are the diagonals of a pseudoquadrangle of some pseudotriangulation. To show the existence of a such pseudotriangulation we add four sufficiently small obstacles near the crossing point of bit(t) and bit(t') as indicated in Fig. 8(a). Now we consider a pseudotriangulation (of the set of \(n+4\) obstacles) that contains the bitangent bit(t), and the \(3 \times 4=12\) bitangents shown dashed in Fig. 8(a). Up to some flip operations we can assume that these 12 bitangents are the only bitangents that emanate from the 4 new obstacles. Removing these 4 added obstacles and their 12 bitangents

![Figure 8. (a) bit(t) and bit(t t) are crossing. The 4 added obstacles and the 12 added bitangents are shown dashed. (b) seg(t)\bit(t) and bit(t') are crossing. (c) seg(t)\bit(t) and seg(t')\bit(t') are crossing.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-8-p012.png)

*Figure 8. (a) bit(t) and bit(t t) are crossing. The 4 added obstacles and the 12 added bitangents are shown dashed. (b) seg(t)\bit(t) and bit(t') are crossing. (c) seg(t)\bit(t) and seg(t')\bit(t') are crossing.: (a) bit(t) and bit(t t) are crossing. The 4 added obstacles and the 12 added bitangents are shown dashed. (b) seg(t)\bit(t) and bit(t') are crossing. (c) seg(t)\bit(t) and seg(t')\bit(t') are crossing.*

yields a pseudotriangulation (since the number of remaining bitangents is \(3 n-3\) ) with the desired property. A similar construction yields the result in the case where bit(t) and bit \(\left(t^{\prime}\right)\) are disjoint, either in the case where seg \((t) \backslash \operatorname{bit}(t)\) and bit \(\left(t^{\prime}\right)\) are crossing (see Fig. 8(b)), or in the case where seg(t)\bit(t) and seg \(\left(t^{\prime}\right) \backslash\) bit \(\left(t^{\prime}\right)\) are crossing (see Fig. 8(c)). In this latter case the condition given in the lemma ensures that up to some flip operations the added obstacle contributes only to the three dashed bitangents. After removing the added obstacles and their bitangents, bit(t) and bit(t') are edges of the same pseudotriangle, and hence they are comparable.

Now we prove claim (3). We can assume that bit(t) and bit( \(t^{\prime}\) ) are disjoint. Consider a pseudotriangulation \(G\) that contains bit \((t)\) and bit \(\left(t^{\prime}\right)\), and consider a curve in free space that joins bit( \(t\) ) and bit ( \(t^{\prime}\) ). This curve crosses a finite sequence of bitangents in \(G\), say \(b_{1}, b_{2}, \ldots, b_{l}\). Let \(t_{j} \in X_{0}\) such that bit \(\left(t_{j}\right)=b_{j}\), with \(t_{0}=t\) and \(t_{l}=t^{\prime}\). Since \(t_{j}\) and \(t_{j+1}\) are bitangents in the boundary of a pseudotriangle (or both on the convex hull), they are comparable. Therefore \(t_{j} \leq \pi^{k_{j}}\left(t_{j+1}\right)\) for \(k_{j}\) sufficiently large. It follows that \(t \leq \pi^{k}\left(t^{\prime}\right)\) for \(k\) sufficiently large ( \(k=\sum_{j} k_{j}\) ).

Now we come to the "minimum-element" property announced in the Introduction. We denote by ~o the one-to-one mapping

$$
t \in X_{0} \mapsto \sup \sup t \in X_{0},
$$

i.e., \(\varphi(t)\) is the ray with maximal slope in the (closure of the) face for which \(t\) is the ray with minimal slope. It can easily be checked that \(\varphi \circ \pi=\pi \circ \varphi\).

![Figure 9. Illustration of the proof of the "minimum-element" properly.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-9-p013.png)

*Figure 9. Illustration of the proof of the "minimum-element" properly.: Illustration of the proof of the "minimum-element" properly.*

Lemma 8 ("Minimum-Element" Property). Let \(t\) and \(t^{\prime}\) be two interior crossing bitangents in \(X_{0}\) (i.e., bit(t) and bit( \(t^{\prime}\) ) are crossing) with \(t \prec t^{\prime}\). Then \(\varphi(t) \leq t^{\prime}\) (and \(t \leq \varphi^{-1}\left(t^{\prime}\right)\) ). In other words, \(\varphi(t)\) is the minimum bitangent in the set of bitangents crossing \(t\) and larger than \(t\).

Proof. Let \(p\) be the intersection point of \(\operatorname{bit}(t)\) and \(\operatorname{bit}(\varphi(t))\), and let \(u\) and \(u^{*}\) be the slopes of \(t\) and \(\varphi(t)\), respectively. Let \(t(\alpha)=\left(p, \alpha u+(1-\alpha) u^{*}\right), \operatorname{seg}(t(\alpha))=\) \([a(\alpha), b(\alpha)]\), and

$$
T=\bigcup_{\alpha \in[0,1]} \operatorname{seg}(t(\alpha)) .
$$

Therefore the slope of \(t^{\prime}\) is greater than the slope of \(\varphi(t)\), and \(\operatorname{bit}(\varphi(t))\) and \(\operatorname{seg}\left(t^{\prime}\right)\) are crossing (first case), or bit \(\left(t^{\prime}\right)\) is tangent to the boundary of \(T\) (second case). See Fig. 9 for an illustration. Hence it suffices to prove that \(t^{\prime}\) and \(\varphi(t)\) are comparable with respect to \(\leq\) in order to conclude that \(\varphi(t) \leq t^{\prime}\). The first case is covered by Lemma 7, claim (1). In the second case bit \(\left(t^{\prime}\right)\) is tangent to the \(\operatorname{arc}\{b(\alpha) \mid \alpha \in(0,1)\}\), or to the \(\operatorname{arc}\{a(\alpha) \mid \alpha \in(0,1)\}\). Both cases are covered by claim (2) of Lemma 7.

Remark 9. Note that if \(t\) is an exterior bitangent, then the set \(\left\{\pi(t), \pi^{2}(t), \ldots\right\}\) is the set of bitangents greater than \(t\) and crossing \(t\); this set has a minimum element, namely \(\pi(t)\).

### 2.4 Filters, Antichains, and Greedy Pseudotriangulations

$$
For a finite subset \(A\) of \(X\) we define the filter \(A^{+}\)of ( \(X_{0}, \leq\) ) by
$$

$$
A^{+}=\left\{x \in X_{0} \mid y \leq x \text { for some } y \in A\right\} .
$$

The complement of \(A^{+}\)in \(X_{0}\) is denoted by \(A^{-}\). For a filter \(I\) of ( \(X_{0}, \preceq\) ) we let \(\hat{I}\) be the subset of \(X \backslash X_{0}\) defined by

$$
\hat{I}=\left\{x \in X_{1} \cup X_{2}^{*} \mid \sup x \in I, \inf x \notin I\right\} \cup\{\text { unbounded faces }\} .
$$

Note that, by definition, the set of unbounded faces is a subset of I.

A proper filter of a poset \((X, \preceq)\) is a filter which is a nonempty proper subset of \(X\). Lemma 10. The mapping \(I \mapsto \hat{I}\) is a one-to-one correspondence between the set of proper filters of ( \(X_{0}, \preceq\) ) and the set of maximal antichains of ( \(X \backslash X_{0}, \preceq\) ), whose inverse is the map \(A \mapsto A^{+}\).

Proof. first we show that \(\hat{I}\) is a maximal antichain of \(\left(X \backslash X_{0}, \preceq\right)\). Let \(x \in \hat{I}, y \in X \backslash X_{0}\) with \(x \prec y\), or \(y \prec x\). Then \(y \notin \hat{I}\). If \(x \prec y\) we have \(\sup x \preceq \inf y\) and, therefore, \(\inf y \in I\), since \(\sup x \in I\). This implies that \(y \notin \hat{I}\). A similar conclusion holds if we assume that \(y \prec x\). This proves that \(\hat{I}\) is an antichain.

Now we prove that the antichain \(\hat{I}\) is maximal. Let \(x \in X \backslash X_{0}\) and consider the unrefinable chain \(\left\{\ldots, \inf ^{2}(x), \inf (x), x, \sup (x), \sup ^{2}(x), \sup ^{3}(x), \ldots\right\}\). By Lemma 7, part (3), this chain joins \(X_{0} \backslash I\) and \(I\). Consequently, this chain intersects \(\hat{I}\), and \(x\) is comparable with an element in \(\hat{I}\). Finally observe that \((\hat{I})^{+}=I\), since (1) min \(I \subset(\hat{I})^{+}\) and (2) \((\min I)^{+}=I\). Note that, in view of Lemma 7, part (3), \(I\) contains no infinite decreasing chains.

Theorem 11. Let A be a maximal antichain in (X\Xo, ~). Then:

- A depends only on its subset of 1-faces. More precisely, A is the union of the cofaces in \(P(X)\) of its 1-faces. Furthermore, \(P(A)\), the subposet of \(P(X)\) induced by A, is an abstract polytope of rank 3.

- The numbers of 1-, 2-, and 3-faces in A are respectively 2n, 3n, and n + 2 (and consequently \(P(A)\) is spherical).

Therefore \(y \in A\). Therefore these two chains intersect \(A\). This proves claim (1). cover the set of edges of \(X\). Therefore there is exactly one edge of the maximal antichain on each of these curves. Hence the number of edges in the antichain is \(2 n\). According to claim (1) and Theorem 5, the number of incidences between edges and 2-faces of a maximal antichain is three times the number of edges, and twice the number of 2-faces. Therefore the number of 2-faces is \(3 n\). Planarity is proved by computing the Euler characteristic.

Let \(I\) be a filter and let \(B_{1}(I), B_{2}(I), \ldots\) be the sequence of subsets of \(I\) defined by (1) \(B_{1}(I)\) is the set of minimal bitangents in \(I\), and (2) \(B_{i+1}(I)\) is the set of minimal bitangents in the set of bitangents in \(I\) disjoint from the bitangents in \(B_{1}(I), \ldots, B_{i}(I)\). Since the bitangents in \(B_{j}(I)\) are pairwise noncomparable they are pairwise disjoint, and consequently \(\bigcup_{i \geq 1} B_{i}(I)\) is a pseudotriangulation in \(X\) (in particular \(B_{i}(I)=\emptyset\) for \(i\) sufficiently large). This pseudotriangulation is denoted by \(G(I)\) and is called the greedy pseudotriangulation associated with the filter \(I.^{3}\) Finally, for a filter \(I\) we define

$$
S(I)=\left\{b \in I \mid \varphi^{-1}(b) \notin I\right\} .
$$

Now we come to the proof of Theorem 2, announced in the Introduction. We give a slightly stronger form. For \(Y \subset X_{0}\) we denote by \(Y_{\text {int }}\) (resp. \(Y_{\text {ext }}\) ) the subset of \(Y\) consisting of interior (resp. exterior) bitangents.

Theorem 12.

- For all filters 1, and all interior (resp. exterior) bitangents b ~ ro_in I, the set difference \(G(I\{b})\)\\(G(1)\) is equal to {tp(b)} (resp. {yr(b)}).

- For all filters I, all bitangents b E \(G(I)\), and all t E I crossing b, we have b "< t.

- For all filters I we have Gint() = Sint().

Proof. Claims (1) and (2) are obvious in the case where \(b\) is an exterior bitangent (see Remark 2); therefore we assume now that \(b\) is an interior bitangent. We prove the theorem by showing that claim (3) implies (1), and subsequently that (1) implies (2), after which we establish the truth of claim (3). first observe that \(\varphi(b)\) is disjoint from any \(b^{\prime} \in G(I) \backslash\{b\}\), otherwise \(\varphi(b)\) and \(b^{\prime}\) are comparable, with \(b^{\prime} \prec \varphi(b)\) (indeed if \(\varphi(b) \prec b^{\prime}\), then, according to Lemma 8, \(\varphi(b) \preceq \varphi^{-1}\left(b^{\prime}\right)\); consequently \(\varphi^{-1}\left(b^{\prime}\right) \in I\), i.e., \(b^{\prime} \notin G(I)\) ). According to Lemma 8 this implies that \(b^{\prime} \leq b\), a contradiction with \(b \in \min I\). Therefore, it is sufficient to prove that \(\varphi(b)\) is a bitangent in \(G(I \backslash\{b\})\). Suppose the contrary holds. Then \(\varphi(b)\) intersects some \(b^{\prime} \in G(I \backslash\{b\})\), with \(b^{\prime} \prec \varphi(b)\). However, according to Lemma 8, this implies that \(b^{\prime} \leq b\), a contradiction. Thus, claim (3) implies claim (1).

Now we prove that claim (1) implies claim (2). To this end let \(I\) be a filter, let \(b\) be a bitangent in \(G(I)\) and let \(t\) be a bitangent in \(I\) which crosses \(b\). We define the sequence of filters \(I_{1}, I_{2}, \ldots\) by \(I_{1}=I\) and \(I_{k+1}=I_{k} \backslash B_{1}\left(I_{k}\right)\). Observe that if \(b \in G\left(I_{k}\right) \backslash B_{1}\left(I_{k}\right)\) and Finally we prove claim (3) by proving successively that:

- (i) Sint(1) C Gint() (in particular the bitangents in Sint(1) are pairwise disjoint).

- (ii) aext() C Sext(I) and Card Sext(1) = Card Gext(1) q-2.

- (iii) Card \(S(I)\) = 3n-1.

These three properties imply that \(G_{\text {int }}(I)=S_{\text {int }}(I)\), since Card \(G(I)=3 n-3\).

3 Observe that if ~1 is a total order on 1, compatible with _ < on I, then the elements of the set \(G(1)\) can be enumerated as the sequence bl. b2. . . . . b3n-3, where (1) bl is the minimum bitangent in (l, _1), and (2) bi+l is the minimum bitangent in (I, _~1) disjoint from bl. b2. . . . . bi.

Let \(b\) be an interior bitangent. Then (first case) there is a \(b^{\prime} \in G(I)\) crossing \(b\), with \(b^{\prime} \prec b\), or (second case) for all \(b^{\prime} \in G(I)\) crossing \(b\) we have \(b \leq b^{\prime}\). In the first case Lemma 8 implies that \(b^{\prime} \leq \varphi^{-1}(b)\), and consequently that \(b \notin S(I)\). In the second case \(b\) is smaller than any bitangent in \(G(I)\) crossing it, therefore \(b \in G(I)\). This proves claim (i).

For an exterior bitangent \(t\) lying on \(\gamma_{+\mathcal{O}}\) (resp. \(\gamma_{-\mathcal{O}}\) ) we denote by \(\operatorname{succ}(t)\) the minimal exterior bitangent greater than \(t\) lying on \(\gamma_{+\mathcal{O}}\) (resp. \(\gamma_{-\mathcal{O}}\) ). Observe that \(\operatorname{succ}(\pi(t))=\) \(\pi(\operatorname{succ}(t))=\varphi(t)\) whenever \(t\) is an exterior bitangent in \(X_{0}\), and that the number \(h\) of exterior bitangents in \(B\) is defined by \(s u c c^{h}=\pi^{2}\). Let \(t\) be the minimal element in

$$
t, \operatorname{succ}(t), \operatorname{succ}^{2}(t), \ldots .
$$

Therefore, there is a k such that succJ(t) ~ \(S(1)\) for j = 0, 1..... k and succJ(t) ~g \(S(1)\) for j > k. Now observe that zr(t') lies on Y+o. Hence, succk(t) = Jr(t'), since ~r(t') ~ \(S(I)\) and succ(zr(t')) = ~o(t') ~[\(S(I)\). Similarly, succk'(t ') = zr(t), where k' is the greatest index such that succk'(t ') ~ \(S(I)\). It follows that SUCCk+k'(t) = ~r2(t) and, consequently, that k + k ~ = h. Now observe that Gext(1) is a subset of

$$
\left\{t, t^{\prime}, \operatorname{succ}(t), \operatorname{succ}\left(t^{\prime}\right), \operatorname{succ}^{2}(t), \operatorname{succ}^{2}\left(t^{\prime}\right), \ldots,\right\}
$$

Therefore, \(G_{\text {ext }}(I) \subseteq S_{\text {ext }}(I)\), since \(\pi(t)\) and \(\pi\left(t^{\prime}\right)\) are not in \(G_{\text {ext }}(I)\). Furthermore, a cardinality argument shows that \(S_{\text {ext }}(I)=\) \(G_{\text {ext }}(I) \cup\left\{\pi(t), \pi\left(t^{\prime}\right)\right\}\). This proves claim (ii).

Finally note that \(S(I)=\sup \hat{I}=\sup \hat{I} \backslash X_{1}\), and consequently Card \(S(I)=3 n-1\),

## 3 The Greedy Flip Algorithm and Its Analysis

### 3.1 The Algorithm

suggests a very simple algorithm: maintain the greedy pseudotriangulation \(G(I)\), while \(I\) ranges over a maximal chain of filters in the interval \([I(0), I(\pi)]\). algorithm GREEDY FLIP algorithm

- 1 compute the greedy pseudotriangulation G := \(G(I(0)\));

- 2 repeat

- 3 select a minimal bitangent b in G with slope less than Jr;

- 4 flip b; (i.e., replace b by ~0(b) (resp. rr(b)) if b is an interior (resp. exterior) bitangent)

- 5 until there are no more bitangents of slope less than Jr.

Theorem 2 proves the correctness of this algorithm. Of course, we still have to explain how to implement the flip operation (namely line 4) and how to select a minimal bitangent with slope less than \(\pi\) (namely line 3), so that the total cost of these operations is \(O(k)\) time. Figure 10 illustrates the greedy flip algorithm. In this example the flipped bitangent has minimal slope, and is therefore a minimal element with respect to the partial order \(\preceq\).

In Section 3.2 the construction of the initial pseudotriangulation \(G(I(0))\) is described in detail. Section 3.3 describes how to select a minimal bitangent. Section 3.4 describes an efficient implementation of the flip operation, whose amortized cost is analyzed in Section 3.4.5.

### 3.2 Construction of the Initial Greedy Pseudotriangulation G (1 (0))

Lemma 13. The greedy pseudotriangulation \(G(I(0))\) of a collection of \(n\) disjoint convex obstacles in the plane can be computed in \(O(n \log n)\) time.

Proof. The construction is based on a standard rotational sweep à la Bentley-Ottmann, from direction 0 to direction \(\pi\), during which we maintain the visibility map associated to the current direction. For simplicity assume that no free bitangent has slope 0. A useful aid in the construction of \(G:=G(I(0))\) is the greedy visibility map \(M(u)\), associated with a slope \(u \in[0, \pi]\). Let \(B(u)\) be the bitangents in \(G\) with slope less than \(u\). Note that \(B(0)=\emptyset\), and \(B(\pi)\) is the set of bitangents in \(G\).

Every object \(O\) contains two points having a tangent line with slope \(u\). These points are said to be of type left and right depending on whether the tangent line contains the object in its left or right half-plane. The points are denoted by \(O(u\), left \()\) and \(O(u\), right). The collection of all these points is denoted by \(V(u)\).

Two distinct objects \(O\) and \(O^{\prime}\) have exactly eight common directed tangent lines. They form four pairs, denoted by ( \(O, O^{\prime}, \tau, \tau^{\prime}\) ), where \(\tau\) and \(\tau^{\prime}\) are either left or right. For instance, ( \(O, O^{\prime}\), left, right) is the tangent line going from \(O\) to \(O^{\prime}\), containing \(O\) in its left half-plane and \(O^{\prime}\) in its right half-plane.

From each point of \(V(u)\) we shoot two rays, one with slope \(u\), the other one with slope \(u+\pi\). We extend these rays until they hit an object, or a bitangent in the collection \(B(u)\). In this way we partition free space into a number of regions that contain either one or two points of \(V(u)\) in their boundary. These regions are called triangular and quadrangular, respectively. For convenience the two unbounded regions, in which we can walk in direction \(u+\pi / 2\) and \(u-\pi / 2\), respectively, are called quadrangular as well, even though they contain one point of \(V(u)\) in their boundary. If two triangular regions contain the same point \(p\) of \(V(u)\) in their boundary, they are incident along one of the rays emerging from this point. We then merge these two regions by removing this ray. The point \(p\) is still the only point of \(V(u)\) in the boundary of the merged region, which therefore is still triangular. The subdivision of free space that remains after removing all rays shared by triangular regions is called the greedy visibility map with respect to \(u\). It is denoted by \(M(u)\). Figure 11 depicts \(M(u)\) for the The greedy visibility map \(M(0)\) coincides with what is usually called the horizontal visibility map of the collection \(\mathcal{O}\). It can be constructed in \(O(n \log n)\) time using a

![Figure 10. The greedy flip algorithm. At each step the internal bitangent of minimal slope in the current pseudotriangulation is flipped.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-10-p018.png)

*Figure 10. The greedy flip algorithm. At each step the internal bitangent of minimal slope in the current pseudotriangulation is flipped.: The greedy flip algorithm. At each step the internal bitangent of minimal slope in the current pseudotriangulation is flipped.*

![Figure 11. (a) The labeled regions in the upper left part form the faces of the initial visibility map M(0). The graph F(0) is depicted in the upper right part. (b) The labeled regions in the lower left part, together with the lightly shaded regions, are the regions of the visibility map M(zr/2). The lower right part represents the graph r(Tr/2).](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-11-p019.png)

*Figure 11. (a) The labeled regions in the upper left part form the faces of the initial visibility map M(0). The graph F(0) is depicted in the upper right part. (b) The labeled regions in the lower left part, together with the lightly shaded regions, are the regions of the visibility map M(zr/2). The lower right part represents the graph r(Tr/2).: (a) The labeled regions in the upper left part form the faces of the initial visibility map M(0). The graph F(0) is depicted in the upper right part. (b) The labeled regions in the lower left part, together with the lightly shaded regions, are the regions of the visibility map M(zr/2). The lower right part represents the graph r(Tr/2).*

standard sweep line algorithm. Furthermore, the subdivision \(M(\pi)\) is just the greedy pseudotriangulation \(G\) (if we forget about the four unbounded faces that partition the complement of the convex hull). So we try to maintain \(M(u)\) as \(u\) ranges over \([0, \pi]\).

We describe the construction of the sequence \(B(\pi)\) of bitangents belonging to the pseudotriangulation. This method can be extended in a straightforward way to maintain \(M(u)\) as well. The appearance of a free bitangent corresponds to the disappearance of a quadrangular region. For example, in the situation depicted in the lower left part of Fig. 11 the topology of \(M(u)\) will not change as \(u\) rotates beyond \(\pi / 2\), until \(u\) passes the slope of the bitangent contained in the quadrangular region labeled " 6." We represent

![Figure 12. death(e) is the critical direction associated with region e.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-12-p020.png)

*Figure 12. death(e) is the critical direction associated with region e.: death(e) is the critical direction associated with region e.*

the subdivision corresponding to the quadrangular regions of \(M(u)\) by a directed graph \(\Gamma(u)\), defined as follows.

Each quadrangular region of \(M(u)\) contains two points of \(V(u)\) in its boundary; We connect these points by drawing a path in this region that is increasing with respect to the direction \(u+\pi / 2\). In this way we obtain a directed plane graph \(\Gamma(u)\), whose set of edges is in one-to-one correspondence with the set of quadrangular faces of \(M(u)\), and whose vertices are the points of \(V(u)\) in the boundary of the quadrangular faces; see Fig. 11. There are two infinite edges, corresponding to the quadrangular faces that contain only one point of \(V(u)\) in their boundary. The graph \(\Gamma(0)\) contains \(3 n+1\) edges, and \(\Gamma(\pi)\) contains four edges. We shall see that there are \(3 n-3\) events corresponding to the disappearance of an edge, and therefore to the appearance of a bitangent. This is of course related to Lemma 3.

Consider now an edge \(e\) of the graph \(\Gamma(u)\). Its terminal points are \(O^{\prime}\left(u, \tau^{\prime}\right)\) and \(O^{\prime \prime}\left(u, \tau^{\prime \prime}\right)\). There are at most two tangent lines of type ( \(O^{\prime}, O^{\prime \prime}, \tau^{\prime}, \tau^{\prime \prime}\) ), whose slopes lies between 0 and \(u\). Let death( ) be the direction of these lines that is minimal, if this minimal element exists, or \(\pi\) otherwise; see Fig. 12.

Let \(D(u)\) be the set of directions defined by

$$
\mathcal{D}(u)=\{\operatorname{death}(e) \mid e \text { is an edge of } \Gamma(u) \text { and death }(e)<\pi\} .
$$

The following obvious result is crucial for the correctness of the algorithm constructing the initial pseudotriangulation.

Lemma 14. Let the unit vectors \(u^{\prime}\) and \(u^{\prime \prime}\) be the directions of two consecutive elements

- The set Z)(u) does not change when u ranges over the open interval (u', u").

- The critical direction u" is the minimal element of \(D(u)\),for u between u' and u".

We now describe the transition at the next critical direction, namely (i) updating the graph \(\Gamma(u)\) when \(u\) passes this critical direction, and (ii) updating the set \(\mathcal{D}(u)\). It is not hard to see that (i) takes \(O(1)\) time, and (ii) takes \(O(\log n)\) time, due to the maintenance of a priority queue. Figure 13 depicts a few cases.

We also describe the birth of pseudotriangles: the number of vertices of degree 3, plus the number of triangular regions, is invariant. This is obvious in the situations depicted in Fig. 13. It also holds in the case where at least one of the regions \(a, b, c\), and \(d\) is triangular, as illustrated in Fig. 14. Note that the triangular regions grow during the

![Figure 13. Transitions during the construction of the pseudotriangulation.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-13-p021.png)

*Figure 13. Transitions during the construction of the pseudotriangulation.: Transitions during the construction of the pseudotriangulation.*

sweep, so not all combinations of triangular and quadrangular regions are possible. For instance, in the upper left part of Fig. 13 it is not possible that region \(a\) is triangular whilst at the same time \(d\) is quadrangular, since in that case triangular region \(a\) does not grow: it shrinks near the edge along which it is incident with \(d\). Finally the pseudotriangulation \(G(I(0))\) can easily be computed from the set of bitangents \(B(\pi)\).

### 3.3 Minimal Bitangents

Consider a filter \(I\), a bitangent \(b\) in the greedy pseudotriangulation \(G(I)\), and a pseudotriangle \(T\) of \(G(I)\). We denote by \(B_{T}\) the set of bitangents \(t \in G(I)\) such that bit \((t)\) appears in the boundary of \(T\). The partial order \(\prec\) restricted to \(B_{T}\) is a linear order. The minimal element of \(B_{T}\) is denoted by \(b_{T}\). We denote by Ltri(b) (resp. Rtri(b)) the pseudotriangle of \(G(I)\) incident upon bit(b) and-locally-to the left (resp. right) of bit \((b)\), oriented along the direction of \(b\). The initial point of a directed line segment \(b\)

![Figure 14. Transitions during the construction of the pseudotriangulation](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-14-p022.png)

*Figure 14. Transitions during the construction of the pseudotriangulation: at least one of the regions a, b, c, and d is triangular, and hence not represented by an edge in the graph F(u).*

is denoted by Tail(b), the terminal point by Head(b); so \(b\) is directed from its tail to its head. The basepoint of \(T\), denoted by \(p_{T}\), is the tail of \(b_{T}\), if \(T=\operatorname{Rtri}\left(b_{T}\right)\), or the head The direction of the tangent line in a point \(p\) of \(\partial T\) is uniquely determined by the requirement that its slope lies in the interval \(\left[\operatorname{Slope}\left(b_{T}\right), \operatorname{Slope}\left(b_{T}\right)+\pi\right)\). This slope is also called the slope of \(p\). Note that the slope is continuous on \(\partial T\), except at the basepoint of \(T\). A directed subsegment of \(\partial T\) is called a walk (resp. reverse walk) along \(\partial T\) if, going from the initial to the terminal point of the subsegment, we pass the points of the subsegment in order of increasing (resp. decreasing) slope. A walk (resp. reverse walk) goes around \(T\) clockwise (resp. counterclockwise) when viewed from inside \(T\). In particular, the walk starting at the basepoint of \(T\) defines a linear order on the set of bitangents in \(\operatorname{bit}\left(B_{T}\right)\), called the slope order, which coincides, via the mapping bit, with the linear order \(\prec\) on \(B_{T}\). We denote by \(b_{+}\)(resp. \(b_{-}\)) the minimal bitangent in \(G(I)\) lying on \(\gamma_{+\mathcal{O}}\) (resp. \(\gamma_{-\mathcal{O}}\) ), if it exists.

Lemma 15. Let \(I\) be a filter. Then an interior (resp. exterior) bitangent \(b\) is minimal in \(I\) if and only if \(b=b_{\text {Rtri }(b)}=b_{\text {Liri }(b)}\) (resp. \(b=b_{\text {Rtri }(b)}=b_{-}\), or \(b=b_{\text {Ltri }(b)}=b_{+}\)).

Proof. Assume \(b\) is an interior bitangent. Let \(e\) and \(e^{\prime} \in X_{1}\) be such that \(\sup (e)=\) \(\sup \left(e^{\prime}\right)=b\), and such that \(\operatorname{arc}(e)\) and \(\operatorname{arc}\left(e^{\prime}\right)\) are on the boundaries of Rtri(b) and \(L t r i(b)\), respectively. Clearly, \(b=b_{\text {Rtri(b) }}\) (resp. \(b=b_{\text {Ltri(b) }}\) ) iff \(e \in \hat{I}\) (resp. \(e^{\prime} \in \hat{I}\) ).

The successive cusps we pass during a walk starting at the basepoint of \(T\), are denoted by \(x_{T}, y_{T}\) and \(z_{T}\). If the basepoint is a cusp, then by definition it is \(z_{T}\). The forward and backward \(T\)-views of point \(p\) in \(\partial T\) are the points of intersection of \(\partial T\) with the tangent line at \(p\), lying ahead of and behind \(p\), respectively. The point, whose forward (resp. backward) \(T\)-view is \(p_{T}\), if \(T=\operatorname{Rtri}\left(b_{T}\right)\) (resp. \(T=\operatorname{Ltri}\left(b_{T}\right)\) ), is denoted by \(q_{T}\). See

![Figure 15. Forward and backward T-views P0 and pl of t cannot both have smaller slope than t.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-15-p023.png)

*Figure 15. Forward and backward T-views P0 and pl of t cannot both have smaller slope than t.: Forward and backward T-views P0 and pl of t cannot both have smaller slope than t.*

also Fig. 18. To avoid confusion, we stress that the forward (resp. backward) view from a point along a directed line is defined with respect to the set of obstacles (and not with respect to the set of pseudotriangles); see Section 2.2, where this view is defined as an obstacle.

For later use we isolate a simple, but crucial, feature of pseudotriangles of greedy pseudotriangulations.

Lemma 16. Let T be a pseudotriangle of a greedy pseudotriangulation.

- If zr ~ Pr, then the part of OT between ZT and Pr is an arc.

- If yr lies between xr and qr, then the part of OT between Yr and qr is an arc (i.e., it contains no bitangents).

Proof. We prove that no bitangent \(t \in B_{T}\) has forward and backward \(T\)-views of smaller slope. This will prove part (1), since all points on the segment \(z_{T} p_{T}\) have both forward and backward \(T\)-view of smaller slope. A similar argument proves part (2).

To prove the claim, suppose that both the backward and forward \(T\)-view, \(p_{0}\) and \(p_{1}\) say, of \(t\) have smaller slopes than \(t\). We only consider the case in which \(p_{0}\) has smaller slope than \(p_{1}\). See Fig. 15. Then \(T=L t r i(t)\), and the part of \(\partial T\) between \(p_{0}\) and \(p_{1}\)

### 3.4 Flipping Minimal Bitangents

3.4.1. The New Pseudotriangles R' and L'. Consider a minimal bitangent b (with respect to some filter I), with R = Rtri(b) and L = Ltri(b). Let b* = ~o(b) be the bitangent obtained by flipping b. Its tail and head are denoted by p* and q*, respectively.

![Figure 16. The pseudotriangle R' = Rtri(b*) (shaded) is obtained by flipping bitangent b. Furthermore, R' is the left or right pseudotriangle ofb~ (cases 1 and 2, respectively), or OR' does not contain b~ (case 3).](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-16-p024.png)

*Figure 16. The pseudotriangle R' = Rtri(b*) (shaded) is obtained by flipping bitangent b. Furthermore, R' is the left or right pseudotriangle ofb~ (cases 1 and 2, respectively), or OR' does not contain b~ (case 3).: The pseudotriangle R' = Rtri(b*) (shaded) is obtained by flipping bitangent b. Furthermore, R' is the left or right pseudotriangle ofb~ (cases 1 and 2, respectively), or OR' does not contain b~ (case 3).*

The right and left pseudotriangles of \(b^{*}\) (with respect to the filter \(I \backslash\{b\}\) ) are denoted by \(R^{\prime}\) and \(L^{\prime}\), respectively. We denote by \(G\) and \(G^{\prime}\) the pseudotriangulations \(G(I)\) and \(G(I \backslash\{b\})\), respectively. We consider the bitangent \(b_{T}\) for \(T=R^{\prime}, L^{\prime}\). We only consider Case 1: \(b\) and \(b_{R}^{\prime}\) are not separated by a cusp of \(R\). Then \(R^{\prime}=R\) tri \(\left(b_{R}^{\prime}\right)\), and \(p^{*}\) does not lie on the arc between \(b\) and \(b_{R}^{\prime}\). Therefore \(\min B_{R^{\prime}}=b_{R}^{\prime}\).

Case 2: \(b\) and \(b_{R}^{\prime}\) are separated by a cusp of \(R\), and \(p^{*}\) does not lie on the arc between \(b\) and \(b_{R}^{\prime}\). Then \(R^{\prime}=\operatorname{Ltri}\left(b_{R}^{\prime}\right)\) and \(\min B_{R^{\prime}}=b_{R}^{\prime}\). (Note: in this case \(x_{R}=\operatorname{Head}\left(b_{R}^{\prime}\right)\), as in Fig. 16, or \(x_{R}=\) Head (b).)

Case 3: \(b\) and \(b_{R}^{\prime}\) are separated by a cusp of \(R\), and \(p^{*}\) lies on the arc between \(b\) and \(b_{R}^{\prime}\). Then \(\min B_{R^{\prime}}=b^{*}\).

$$
The bitangent \(\min B_{L^{\prime}}\) is defined similarly.
$$

We now consider the pseudotriangle \(R^{\prime}\) in more detail, in particular its cusps \(x_{R^{\prime}}, y_{R^{\prime}}\), and \(z_{R^{\prime}}\). \(x_{R^{\prime}}=x_{R}\). Furthermore, if \(p^{*}\) lies between \(x_{R}\) and \(y_{R}\), then the second cusp \(y_{R^{\prime}}\) is equal to \(p^{*}\), otherwise it is equal to \(y_{R}\); see Fig. 17(a). Similarly, the third cusp \(z_{R^{\prime}}\) is equal to \(y_{L}\), if \(q^{*}\) lies between \(x_{L}\) and \(y_{L}\), otherwise it is equal to \(q^{*}\), as illustrated in Fig. 17(b).

Case 2: \(R^{\prime}=\operatorname{Ltri}\left(b_{R}^{\prime}\right)\) and \(b_{R}^{\prime}=\min B_{R^{\prime}}\). In this case the basepoint of \(R^{\prime}\) is Head( \(b_{R}^{\prime}\) ), which lies between \(x_{R}\) and \(y_{R}\). Therefore the first cusp \(x_{R^{\prime}}\) is equal to \(p^{*}\), if \(p^{*}\) lies between \(x_{R}\) and \(y_{R}\), otherwise it is equal to \(y_{R}\); again see Fig. 17(a). Similarly, the second cusp \(y_{R^{\prime}}\) is equal to \(y_{L}\), if \(q^{*}\) lies between \(x_{L}\) and \(y_{L}\), otherwise it is equal to \(q^{*}\); see Fig. 17(b). Finally, the third cusp \(z_{R^{\prime}}\) is equal to \(z_{L}\), if \(\operatorname{Head}(b)=x_{R}\), otherwise it is equal to \(x_{R}\), as illustrated in Fig. 17(c).

Case 3: \(R^{\prime}=\operatorname{Rtri}\left(b^{*}\right)\) and \(b^{*}=\min B_{R^{\prime}}\). In this case \(\operatorname{Head}(b)=x_{R}\), and the tail \(p^{*}\) of \(b^{*}\) lies on the arc of \(\partial R\) separating \(b\) and \(b_{R}^{\prime}\). Therefore the basepoint of \(R^{\prime}\) is \(p^{*}\), which

![Figure 17. The cusps of R ~.](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-17-p025.png)

*Figure 17. The cusps of R ~.: The cusps of R ~.*

Since in this case \(x_{R}\) is a cusp of \(R\), the second cusp \(y_{R^{\prime}}\) is equal to \(z_{L}\), as depicted in the left part of Fig. 17(c). Finally Fig. 17(b) shows that the first cusp \(x_{R^{\prime}}\) is equal to \(y_{L}\) or \(q^{*}\), depending on whether \(q^{*}\) lies between \(y_{L}\) and \(z_{L}\), or between \(x_{L}\) and \(y_{L}\).

Table 2 summarizes the previous discussion.

3.4.2. The Splittable Queue Awake[T]. Conceptually the flipping can be done by walking-in the positive direction, starting at the basepoint-along the boundaries of the pseudotriangles \(L\) (left) and \(R\) (right) incident upon the flipped bitangent \(b\), with one leg in every pseudotriangle, such that at any moment the tangent lines at the points underneath our left and right legs are parallel. We keep walking until these tangent lines coincide. At that point we have found \(b^{*}\). This is too expensive, since some bitangents may be passed during many walks involved in the flip operations. To cut the budget, we need an auxiliary data structure, that enables us to start the walk at a more favorable point.

Observe that the tail \(p^{*}\) of \(b^{*}\) lies between the first cusp \(x_{R}\) and the point \(q_{R}\), whose tangent contains the basepoint Tail(b) of \(R\). Similarly, \(q^{*}\) lies between \(x_{L}\) and \(q_{L}\).

Definition 17. For a pseudotriangle \(T\), a point in \(\partial T\) is called awake if it lies between

![Figure 18. The set of points that are awake in T is the segment XTqT, for T = L, R. When the algorithm flips b = bR = bL, the walk on 0T starts in q~ (case 1) or in the cusp xr (cases 2 and 3).](/Users/evanthayer/Projects/paperx/docs/1996_topologically_sweeping_visibility_complexes_via_pseudotriangulations/figures/figure-18-p026.png)

*Figure 18. The set of points that are awake in T is the segment XTqT, for T = L, R. When the algorithm flips b = bR = bL, the walk on 0T starts in q~ (case 1) or in the cusp xr (cases 2 and 3).: The set of points that are awake in T is the segment XTqT, for T = L, R. When the algorithm flips b = bR = bL, the walk on 0T starts in q~ (case 1) or in the cusp xr (cases 2 and 3).*

Note that the points of \(\partial R\) that are awake have forward \(R\)-view of smaller slope, whereas the points awake in \(\partial L\) have backward \(L\)-view of smaller slope; see Fig. 18. Lemma 16 tells us that the set of points that are awake is a sequence of arcs and bitangents on a convex chain, possibly followed by a single arc between \(y_{T}\) and \(q_{T}\) (in case \(q_{T}\) does not lie between \(x_{T}\) and \(y_{T}\) ).

If \(b\) and its successor \(b_{R}^{\prime}\) in \(B_{R}\) are not separated by the cusp \(x_{R}\), corresponding to case 1 in Section 3.4.1, the point \(p^{*}\) lies even between \(q_{R}^{\prime}\) and \(q_{R}\), where \(q_{R}^{\prime}\) is the point whose tangent contains \(\operatorname{Tail}\left(b_{R}^{\prime}\right)\), as shown in Fig. 18.

So the walk along \(\partial R\) starts at \(q_{R}^{\prime}\) in case 1, and in \(x_{R}\), otherwise. Similarly, the walk along \(\partial L\) starts in \(q_{L}^{\prime}\) or in \(x_{L}\), where \(q_{L}^{\prime}\) is the point on \(\partial L^{\prime}\) whose tangent contains Head \(\left(b_{L}^{\prime}\right)\). Now \(x_{T}\) can be determined in \(O(1)\) time, but how do we determine \(q_{T}^{\prime}\) efficiently, for \(T=L, R\) ? To this end we consider the segment \(x_{T} q_{T}\) of points in \(\partial T\), that are awake, as an alternating sequence of bitangents and arcs, or atoms for short, where the atoms are in slope order. This sequence is represented by a splittable queue, denoted by Awake[T], a data structure for ordered lists that allows for the following operations:

- Enqueue an atom, either at the head or at the tail of the list.

- Dequeue the head or the tail of the list.

- Split the sequence at an atom x; this split is preceded by a search for the atom x.

A few comments on the split operation are in order. We assume that the initial search for the atom \(x\) is guided by a real-valued function, \(f\) say, defined for atoms in the sequence, that is monotonous with respect to the order of the atoms in the sequence. Now a split amounts to determining the atom \(x\) for which \(f(x)=0\), and successively splitting the sequence (destructively) into the subsequences of atoms with negative \(f\)-values and those with positive \(f\)-values. More specifically, to find the point \(q_{T}^{\prime}\) (in case 1) we do a split operation in Awake[T], where the search for \(q_{T}^{\prime}\) is guided by the position of Tail \(\left(b_{T}^{\prime}\right)\) with respect to the tangent lines at the terminal points of an atom. See Section 3.4.3 for more details on this split operation.

Lemma 18. There is a data structure, implementing a splittable queue, such that an enqueue or dequeue operation takes \(O(1)\) amortized time, and a split operation at an atom \(x\) on a queue of \(n\) atoms takes \(O(\log \min (d, n-d))\) amortized time, where \(d\) is the rank of \(x\) in the sequence represented by the queue. Moreover, a sequence of \(m\) enqueue, dequeue and split operations on a collection of \(n\) initially empty splittable queues is performed in \(O(m)\) time.

```text
For more details and a sketch of the proof see Appendix B. For our current purposes we stress that we maintain, for each pseudotriangle T, a splittable queue Awake[T], satisfying the following invariant:
```

Invariant 1. Awake \([T]\) represents the segment \(x_{T} q_{T}\) of \(\partial T\) (the atom containing \(x_{T}\) being the head of the queue).

We now describe in more detail (i) how to compute \(b^{*}\), using Awake[R] and Awake[L], and (ii) how to restore Invariant 1 for the new pseudotriangles \(R^{\prime}\) and \(L^{\prime}\). Subsequently we prove that the total cost of (i) and (ii) amortizes to \(O(k)\).

3.4.3. Construction of \(b^{*}\). If \(b\) and its successor \(b_{R}^{\prime}\) in \(B_{R}\) are not separated by the cusp \(x_{R}\) of \(R\) (case 1), then during the construction of \(b^{*}\) the walk along \(\partial R\) starts in \(q_{R}^{\prime}\). In this case we split Awake[R] at \(q_{R}^{\prime}\) into AwakeMin[R] and AwakeMax[R], where the atoms in the former queue have smaller slope than the atoms in the latter queue. Otherwise, namely if \(b\) and \(b_{R}^{\prime}\) are separated by the cusp \(x_{R}\), we set AwakeMin[R] \(\leftarrow \emptyset\) and AwakeMax[R] ← Awake[R]. Here \(\emptyset\) denotes the empty queue. In either case \(p^{*}\) lies on an arc, represented by an atom in the queue AwakeMax \([R]\). We similarly initialize the splittable queues AwakeMin[L] and AwakeMax[L].

Now the simultaneous walk along \(\partial R\) and \(\partial L\) can be implemented by dequeuing atoms from AwakeMax[R] and AwakeMax[L], until the atoms (arcs) are found that contain \(p^{*}\) and \(q^{*}\), respectively. Obviously, this sequence of synchronous dequeue operations takes time proportional to the number of dequeued atoms. So we construct \(b^{*}\) at the cost of at most one split on Awake[R] and at most one split on Awake[L], followed by a number of successive dequeue operations.

We finally adjust the first atoms in the queues AwakeMax[R] and AwakeMax[L] (namely the atoms containing \(p^{*}\) and \(q^{*}\), respectively) by replacing their terminal points of smaller slope with \(p^{*}\) and \(q^{*}\), respectively. After this final operation the splittable queues AwakeMax[R] and AwakeMax[L] represent the segments \(p^{*} q_{R}\) of \(\partial R\) and \(q^{*} q_{L}\) of \(\partial L\), respectively. We use these queues in the construction of the queues Awake[ \(\mathrm{R}^{\prime}\) ] and Awake \(\left[\mathrm{L}^{\prime}\right]\). We summarize the preceding discussion in the following piece of pseudocode.

algorithm COMPUTING b*

- 1 ifxR does not separate bR and b~ then

- 2 Comment: case 1

- 3 search for arc in Awake[R], containing q~

- 4 split Awake[R] at q~, into AwakeMin[R] and AwakeMax[R]

- 5 else Comment: cases 2 and 3

- 6 AwakeMin[R] +-

- 7 AwakeMax[R] +- Awake[R]

- 8 endif Comment: AwakeMax[R] represents q'RqR (case 1) or XRqR (case 2, 3)

- 9 Construct AwakeMin[L] and AwakeMax[L] similarly

- 10 Find p* and q* by synchronous linear search on AwakeMax[R] and AwakeMax[L], meanwhile dequeuing atoms not containing p* and q*, respectively

- 11 Set initial point of first atom in AwakeMax[R] to p*

- 12 Comment: AwakeMax[R] represents subsegment P*qR of OR

- 13 Set initial point of first atom in AwakeMax[L] to q*

- 14 Comment: AwakeMax[L] represents subsegment q*qL of OL

- 3.4.4. Construction of Awake[R'] and Awake[L']. To facilitate efficient maintenance of the collection of queues Awake[T], for all pseudotriangles T, we also maintain the set of points of 8T between the second cusp Yr and the third cusp zr, that are not awake. These points are called asleep. They form a convex chain, namely the segment yrzr or qrzr of OT, depending on whether qr lies between xr and yr or between Yr and zr. This convex chain is also represented by a splittable queue Asleep[T], whose atoms represent the arcs and bitangents of the chain in order of increasing slope. In other words, we maintain, for each pseudotriangle T, the following invariant:

Invariant 2. As leep \([T]\) represents the following segment of \(\partial T: y_{T} z_{T}\), if \(q_{T} \notin y_{T} z_{T}\), and \(q_{T} z_{T}\), if \(q_{T} \in y_{T} z_{T}\).

We only describe how to establish Invariants 1 and 2 for pseudotriangle \(R^{\prime}\); the invariants are established similarly for \(L^{\prime}\). In particular we show that the construction of the queues Awake[ \(R^{\prime}\) ] and Asleep [ \(R^{\prime}\) ] from the queues AwakeMin \([R]\), AwakeMax \([R]\), Asleep[R], AwakeMin[L], AwakeMax[L] and Asleep[L], requires only a number of dequeue and at most four enqueue operations. Again we consider each of the cases, introduced in Section 3.4.1, separately.

Since in this case Head(b) is not a cusp of \(R\), it is a cusp of \(L\). Figure 16, case 1, illustrates this observation. More precisely, \(\operatorname{Head}(b)=z_{L}\). Moreover, the point of \(\partial L\) whose tangent contains the basepoint Head(b) of \(\partial L\), coincides with Head(b), so we also have \(z_{L}=q_{L}\). In particular all points of \(\partial L\) between \(x_{L}\) and \(z_{L}\) are awake in \(L\). Furthermore, the basepoint of \(R^{\prime}\) is \(\operatorname{Tail}\left(b_{R}^{\prime}\right)\), so we have \(q_{R^{\prime}}=q_{R}^{\prime}\). Hence, by definition, all points that are awake in \(R^{\prime}\) lie between \(x_{R}\left(=x_{R^{\prime}}\right)\) and \(q_{R}^{\prime}\). This justifies line 2 in the following piece of pseudocode:

```text
Algorithm Construction of Awake[ \(\mathrm{R}^{\prime}\) ] AND Asleep [ \(\mathrm{R}^{\prime}\) ]: CASE 1
```

- algorithm I Comment: Awake[L] -- - - XLZL, Asleep[L] = 0 2 Awake[R'] +- AwakeMin[R] 3 Comment: Invariant 1 holds for R' 4 if ZR, = YL then

- 5 Asleep[R'] +- AwakeMax[L]

6 dequeue last atom from Asleep[R'] 7 else Comment: ZR' = q* 8 Asleep[R'] +9 endif Comment: As i eep[R'] represents subsegment of q*ZR' \(C_{0}\) R' of points asleep in OR' 10 enqueue segment b* = p'q* at the head of Asleep[R'] 11 Comment: Asleep[R] represents p*ZR' C OR' 12 ifyR, = YR then 13 ifqR, e XRYR then 14 enqueue arc YRP* at the head of Asleep[R'] 15 else Comment: qR' E YRZR 16 enqueue arc qR'P* at the head of Asleep[R] 17 endif 18 else Comment: YR' = P* 19 skip (do nothing) 20 endif Comment: Invariant 2 holds for R' To see how Asleep \(\left[\mathrm{R}^{\prime}\right]\) is constructed in lines \(3-20\), first observe that \(b^{*}\) is asleep in \(R^{\prime}\), since it lies on the segment \(y_{R^{\prime}} z_{R^{\prime}}\) of \(\partial R^{\prime}\), beyond the point \(q_{R}^{\prime}\left(=q_{R^{\prime}}\right)\).

Lines 4-9 initialize Asleep[ \(\mathrm{R}^{\prime}\) ], so that it represents the chain of points on \(q^{*} z_{R^{\prime}}\), that are asleep in \(R^{\prime}\). To see this, recall from the end of Section 3.4.3 that AwakeMax[L] represents the segment \(q^{*} z_{L}\) of \(\partial L\), since \(q_{L}=z_{L}\). Furthermore, Lemma 16, part (2), tells us that the segment \(y_{L} z_{L}\) is a single arc. Therefore this arc is the last atom in AwakeMax[L]. So if \(z_{R^{\prime}}=y_{L}\) (see Table 2), we initialize Asleep[ \(\mathrm{R}^{\prime}\) ] in line 5, after which we dequeue the last atom from this queue in line 6. If \(z_{R^{\prime}}=q^{*}\) the segment \(q^{*} z_{R^{\prime}}\) is empty, justifying the assignment in line 8.

Therefore we enqueue, in line 10, an atom representing \(b^{*}\) onto Asleep[ \(\mathrm{R}^{\prime}\) ], after which this queue represents the chain \(p^{*} z_{R^{\prime}}\). If \(y_{R^{\prime}}=p^{*}\), this completes the construction of Asleep[ \(\mathrm{R}^{\prime}\) ]. This case is handled in lines 18 and 19. So according to Table 2, it remains to consider the case \(y_{R^{\prime}}=y_{R}\). This is done in lines 12-17. According to Lemma 16, the segment \(y_{R} p^{*} \subset y_{R} q_{R}\), is a single arc. If \(q_{R^{\prime}}\left(=q_{R}^{\prime}\right)\) lies between \(x_{R}\) and \(y_{R}\), all points on the arc \(y_{R} p^{*}\) are asleep in \(R^{\prime}\), so the first atom of Asleep[ \(\mathrm{R}^{\prime}\) ] should represent this arc. Finally, if \(q_{R}^{\prime} \in y_{R} z_{R}\), the first atom of Asleep[ \(\mathrm{R}^{\prime}\) ] should represent the arc \(q_{R}^{\prime} p^{*}\). In either case we enqueue an atom at the head of Awake[ \(\mathrm{R}^{\prime}\) ], which represents an arc with terminal point \(p^{*}\), and initial point \(y_{R^{\prime}}\). This completes the construction of Asleep[ \(\mathrm{R}^{\prime}\) ] in case 1.

Case 2: \(R^{\prime}=\operatorname{Ltri}\left(b_{R}^{\prime}\right)\) and \(b_{R}^{\prime}=\min B_{R^{\prime}}\). We distinguish two subcases.

Case 2.1: Head( \(b\) ) \(=x_{R}\). In this situation \(z_{R^{\prime}}=z_{L}\). To determine the part \(x_{R^{\prime}} q_{R^{\prime}}\) of \(\partial R^{\prime}\) that is awake, we consider two further subcases.

Case 2.1.1: \(q_{R^{\prime}}\) comes before \(p^{*}\) on \(\partial R^{\prime}\). We can determine in \(O(1)\) time whether this case arises by comparing the position of \(p_{R^{\prime}}\) with respect to the tangent at \(p^{*}\). In this case, by definition 17, \(b^{*}\) is not awake in \(\partial R^{\prime}\). Note also that in this case \(x_{R^{\prime}}=y_{R}\). Now Lemma 16, part (2), tells us that the points \(x_{R^{\prime}}\left(=y_{R}\right), q_{R^{\prime}}, p^{*}\), and \(q_{R}\) lie on a single arc Therefore we restore Invariant 1 for pseudotriangle \(R^{\prime}\) by initializing Awake[ \(\mathrm{R}^{\prime}\) ] as the empty queue, after which we enqueue a single atom, representing the \(\operatorname{arc} x_{R^{\prime}} q_{R^{\prime}}\) on \(\partial R^{\prime}\). See lines \(2-4\) of the pseudocode below.

Case 2.1.2: \(q_{R^{\prime}}\) comes after \(p^{*}\) on \(\partial R^{\prime}\). In this case \(q_{R^{\prime}}\) lies on the segment \(q^{*} q_{L}\) of \(\partial L\). As explained in Section 3.4.3 this segment is represented by AwakeMax[L]. So we start a reverse walk along \(\partial L\), starting at \(q_{L}\), until we have found \(q_{R^{\prime}}\). We know when to stop by considering the position of \(\operatorname{Head}\left(b_{R}^{\prime}\right)\) with respect to the tangent line in the current point of \(\partial L\). This walk can be implemented by first setting Awake[R'] ⟵ AwakeMax[L], and subsequently dequeuing atoms from the tail of Awake[ \(\mathrm{R}^{\prime}\) ]; see lines 6-10 of the pseudocode below. When \(q_{R^{\prime}}\) is found, the queue Awake \(\left[\mathrm{R}^{\prime}\right]\) represents the segment \(q^{*} q_{R^{\prime}}\). The construction of Awake[ \(\left.\mathrm{R}^{\prime}\right]\) is completed by enqueuing an atom representing \(b^{*}\) at the head, followed by enqueuing an atom representing the \(\operatorname{arc} x_{R^{\prime}} p^{*}\) at the head in case \(x_{R^{\prime}} \neq p^{*}\), see lines 14-19 of the pseudocode. (The fact that, in the latter case, \(x_{R^{\prime}} p^{*}\) is a single arc follows from Lemma 16, part (2), applied to \(R^{\prime}\).)

Case 2.2: \(\operatorname{Head}(b) \neq x_{R}\). In this case \(\operatorname{Head}\left(b_{R}^{\prime}\right)=x_{R}\). Furthermore \(p_{R^{\prime}}=q_{R^{\prime}}=x_{R}\), so:

- 9 The part YR'ZR' ( = yR'qR' ) of OR' is a single arc; see again Lemma 16, part (2), applied to R'.

- 9 All points on OR' between XR, ( = YR or p*) and ZR, ( = XR) are awake in OR'. Consequently, no point is asleep in OR'.

of \(\partial R^{\prime}\) between \(q^{*}\) and \(z_{L}\); see line 14 in the algorithm of Section 3.4.3. So after setting Awake[R'] to AwakeMax[L], and adjusting the endpoint of the last atom in this queue from \(q_{L}\left(=z_{L}\right)\) to \(x_{R}\left(=z_{R^{\prime}}=q_{R^{\prime}}\right)\), we establish that Awake \(\left[\mathrm{R}^{\prime}\right]\) represents the part of \(\partial R^{\prime}\) between \(q^{*}\) and \(z_{R^{\prime}}\). See lines 6 and 11-13 of the pseudocode below.

As in case 2.1.2, we now enqueue \(b^{*}\) at the head of Awake \(\left[\mathrm{R}^{\prime}\right]\). In case \(x_{R^{\prime}}=p^{*}\), this completes the construction of Awake \(\left[\mathrm{R}^{\prime}\right]\). In case \(x_{R^{\prime}} \neq p^{*}\) we complete the restoration of Invariant 1 by enqueuing the single \(\operatorname{arc} x_{R^{\prime}} p^{*}\left(=y_{R} p^{*}\right)\).

We summarize the preceding discussion in the following piece of pseudocode:

algorithm CONSTRUCTION OF Awake[R']: CASE 2

- 1 if Head(b) = xR and qn' comes before p* on OR' then Comment: Case 2.1.1 2 Awake[R'] +3 enqueue atom representing arc XR'qR' onto Awake[R'] 4 Comment: Invariant 1 holds for R' 5 else Comment: case 2.1.2 or case 2.2 6 Awake[R'] +- AwakeMax[L] 7 if Head(b) = XR then Comment: case 2.1.2 8 while tail atom of Awake[R'] does not contain qR' do 9 dequeue tail atom of Awake[R'] endwhile 10 set terminal point of tail atom in Awake[R'] to qR' 11 else Comment: case 2.2 12 set terminal point of tail atom in Awake[R'] to XR (= qR') 13 endif Comment: Awake[R'] represents q*qR'

```text
14 enqueue b* at the head of Awake[R'] 15 ifxR, # p* then Comment: xR, = YR; see Table 2 16 enqueue arc xR, p* at head of Awake[R'] 17 else Comment: xR, = p* 18 skip (do nothing) 19 endif Comment: Invariant 1 holds for R' 20 endif
```

It remains to describe the construction of Asleep[ \(\mathrm{R}^{\prime}\) ], namely the sequence of points of \(\partial R^{\prime}\) between \(y_{R^{\prime}}\) and \(z_{R^{\prime}}\) that are not awake.

As we have observed above, in case 2.2 none of the points of \(\partial R^{\prime}\) is asleep, so we establish Invariant 2 for \(R^{\prime}\) by setting Asleep[ \(\mathrm{R}^{\prime}\) ] to \(\emptyset\). So consider case 2.1, namely Head \((b)=x_{R}\). Then \(z_{R^{\prime}}=z_{L}\), and all points that are asleep in \(\partial R^{\prime}\) belong to \(\partial L\). If \(q_{L}\) does not belong to the part of \(\partial L\) between \(y_{L}\) and \(z_{L}\), then \(y_{R^{\prime}} z_{R^{\prime}}=y_{L} z_{L}\), and \(q_{R^{\prime}} \notin y_{L} z_{L}\), so we restore Invariant 2 for \(R^{\prime}\) by setting Asleep[ \(\mathrm{R}^{\prime}\) ] ← Asleep[L]. If, on the other hand, \(q_{L} \in y_{L} z_{L}\), then \(q_{L}\) is-by definition-the initial point of the first atom of Asleep[L]. In this case Lemma 16, part (2), applied to the pseudotriangle \(L\), tells us that \(y_{L} q_{L}\) is a single arc, so we can detect in \(O(1)\) time whether \(q_{R^{\prime}}\) lies between \(y_{L}\) and \(z_{L}\) (since, in that case, it lies on the \(\operatorname{arc} y_{L} q_{L}\) of \(\partial L\) ). If \(q_{R^{\prime}} \in y_{L} z_{L}\), then the first atom of Asleep[ \(\mathrm{R}^{\prime}\) ] is the union of the \(\operatorname{arc} q_{R^{\prime}} q_{L}\) and the arc that is the first atom of the queue Asleep[L]. In other words, after setting Asleep[ \(\mathrm{R}^{\prime}\) ] \(\leftarrow\) Asleep[L], we can establish Invariant 2 for \(R^{\prime}\) in this case by replacing the initial point (namely \(q_{L}\) ) of the first atom in Asleep \(\left[\mathrm{R}^{\prime}\right]\) with \(q_{R^{\prime}}\). See line 5 of the pseudocode below. If \(q_{R^{\prime}} \notin y_{L} z_{L}\), we replace the initial point of the first atom of Asleep[ \(\mathrm{R}^{\prime}\) ] with \(y_{R^{\prime}}\), which is either \(q^{*}\) or \(y_{L}\). See lines 6-8 in the pseudocode.

The preceding discussion is summarized in the following code fragment.

algorithm CONSTRUCTION OF As l eep[R']: CASE 2 1 if Head(b) = xR then Comment: case 2.1, zR, = zL 2 Asleep[R'] +-- Asleep[L] 3 ifqL 9 YLZL then 4 ifqR, 9 YLZL then 5 set initial point of first atom in Asleep[R'] to qR' 6 elseif q* 9 YLZL then 7 set initial point of first atom in Asleep[R'] to q* 8 else set initial point of first atom in As 1 eep[R'] tO YL 9 endif 10 else skip (do nothing) 11 endif 12 else Comment: case 2.2, ze, = xR = qR' 13 Asleep[R'] +- 0 14 endif Comment: Invariant 2 holds for R' no point of \(\partial R^{\prime}\) is asleep, so we set Asleep[ \(\left.\mathrm{R}^{\prime}\right] \leftarrow \emptyset\). The construction of Awake[ \(\mathrm{R}^{\prime}\) ] from Asleep [ \(L\) ] is similar to the construction of Asleep [ \(R^{\prime}\) ] from Asleep[ \(L\) ] in case 2.1. More precisely, if \(q_{L} \notin y_{L} z_{L}\), we have \(x_{R^{\prime}} y_{R^{\prime}}=y_{L} z_{L}\), which is represented by Asleep[L]. So set Awake[R'] ⟵ Asleep[L] in this case.

If \(q_{L} \in y_{L} z_{L}\), we also set Awake[R'] ← Asleep[L], but we have to change the initial point of the first arc from \(q_{L}\) into \(x_{R^{\prime}}\), which is either \(q^{*}\) (if \(q^{*} \in y_{L} z_{L}\) ) or \(y_{L}\) (if \(q^{*} \notin y_{L} z_{L}\) ), according to Table 2. In both cases we finally enqueue the \(\operatorname{arc} z_{L} p^{*}=y_{R^{\prime}} q_{R^{\prime}}\) at the tail of Awake \(\left[\mathrm{R}^{\prime}\right]\).

3.4.5. Amortized Complexity. As for the amortized time complexity, observe that the initial collection of splittable queues-one for each pseudotriangle in the greedy pseudotriangulation we start out with-can be computed in \(O(n \log n)\) time (for instance, simply by enqueuing the bitangents and arcs that are awake in the boundary of each pseudotriangle). This amounts to \(O(n)\) enqueue operations. As we have just indicated, doing all flips and maintaining the collection of queues Awake[T] and Asleep[T], T G \(G(I(0)\)), cost \(O(k)\) further enqueue, dequeue, and split operations. Note that, according to Lemma 3, at any time the storage needed for all these queues is \(O(n)\). Together with Lemma 18 this observation implies our main result, namely Theorem 1.

Although we have not checked all the details yet, we are convinced that this algorithm also applies to the case of obstacles of nonconstant complexity. More precisely, consider \(n\) convex objects consisting of a total of \(m\) pieces of constant complexity. Then the algorithm computes the visibility graph of this collection in time \(O(k+m \log n)\) and space \(O(m)\). In this case the number of enqueue operations in a single flip has an upper bound proportional to the complexity of the face of the visibility complex whose minimal vertex corresponds to the bitangent being flipped. Then the amortized complexity analysis of the algorithm can be done conveniently in terms of the combinatorial complexity, namely \(O(k+m)\), of the visibility complex.

## 4 Condusion

In this paper we have presented an optimal time and linear space algorithm for constructing the visibility graph of a set of pairwise disjoint convex obstacles of constant complexity in the plane. Our algorithm realizes a topological sweep of the visibility complex and is based on new combinatorial properties of visibility graphs complexes. As indicated in Section 3.4.5, we are convinced that the algorithm also works for obstacles of nonconstant complexity.

This work raises two questions that we intend to study in the future. The first question is whether our method can be extented to nonconvex obstacles--it seems clear that the method can be extented to the computation of the visibility graph of the collection of relative convex hulls of nonconvex obstacles (mainly because, in that case, free space remains decomposable into pseudotriangles); however, the general case remains elusive. The second question is whether our algorithm can be turned into an algorithmic characterization of (some abstraction of) visibility graphs--as, for example, the greedy algorithm characterizes the independence set systems which are matroids (see [17]).

## Acknowledgments

We are greatly indebted to the anonymous referees for providing us with many helpful suggestions for improving the readability of the paper.

Appendix A. Poset Terminology In this section we review poset terminology, that we borrow from the book of Stanley [28, Chapter 3] and the paper of McMullen [19].

A partially ordered set \(P\) (or poset, for short) is a set, together with a partial order relation denoted by \(\preceq\). A subposet of \(P\) is a subset of \(P\) with the induced order. A special type of subposet is the interval \([x, y]=\{z \in P \mid x \leq z \leq y\}\). A poset \(P\) is called a locally finite poset if every interval of \(P\) is finite. If \(x, y \in P\), then we say that \(y\) covers \(x\) if \(x \prec y\) (i.e., \(x \preceq y\) and \(x \neq y\) ) and if no element \(z \in P\) satisfies \(x \prec z \prec y\). The Hasse diagram of a poset is the graph whose vertices are the elements of \(P\) and whose edges are the cover relations.

A chain is a poset in which any two elements are comparable. A subset \(C\) of a poset \(P\) is called a chain if \(C\) is a chain when regarded as a subposet of \(P\). The chain \(C\) of \(P\) is saturated (or unrefinable) if there does not exist \(z \in P \backslash C\) such that \(x \prec z \prec y\) for some \(x, y \in C\) and such that \(C \cup\{z\}\) is a chain. An antichain is a subset \(A\) of a poset \(P\) such that any two distinct elements of \(A\) are incomparable. A filter is a subset \(I\) of \(P\) such that if \(x \in I\) and \(x \leq y\), then \(y \in I\). A proper filter of a poset ( \(X, \leq\) ) is a filter which is a nonempty proper subset of \(X\).

An abstract \(n\)-polytope is a poset ( \(P, \preceq\) ), with elements called faces, which satisfies the following properties:

- P has a unique minimal face F-1 and a unique maximal face Fn.

- The flags (i.e., maximal chains) of P all contain exactly n + 2 faces. Therefore P has a strictly monotone rank function with range {-1, 0. . . . . n}. The elements of rank i are called the-faces of P, or vertices, edges, and facets of P if i = 0, 1, or n-1, respectively.

- P is strongly flag-connected, meaning that any two flags dp and qJ of P can be joined by a sequence of flags 9 = qb0, q~l..... ~ = qJ, which are such that t~ i_ 1 and CI) i are adjacent (differ by just one face), and such that 9 D qJ \(C(1)\) i for each i.

- Finally, if F and G are an (i-1)-face and an (i + 1)-face with F -< G, then there are exactly two-faces H such that F -< H -< G. (Diamond Property.)

For a face \(F\) the interval \(\left[F, F_{n}\right]\) is called the coface of \(P\) at \(F\), or the vertex-figure at \(F\), if \(F\) is a vertex.

Appendix B. Splittable Queues Here we sketch a proof of Lemma 18. It is well known that finger trees suit our purpose (see, e.g., [13]), but even the much simpler red-black trees with father pointers will do. In this way we avoid the use of level links, which are rather complicated to maintain. Note in passing that the randomized search trees of Aragon and Seidel [3] can also be used to implement splittable queues, resulting in the same time bounds with high probability.

We augment a red-black tree with two special pointers, to the maximal and minimal atoms in the tree. Atoms (arcs) are stored in a leaf-oriented fashion; they are represented by their endpoints and the tangent lines at their endpoints. In general, the same representation can be used to represent convex chains that are unions of atoms of the type just described. So we store a chain in a red-black tree in the following way: (i) store the atoms at the leaf; (ii) at an internal node, store the convex chain that is the union of all atoms in the subtree rooted at this leaf. This information is sufficient toguide the search for the atom at which we want to split the queue (chain), since the basic operation is to determine whether from a given point there is a tangent line to the convex chain. Furthermore, the information at internal nodes can be maintained after 1 (1, and a constant number of rotations).

The amortized \(O(1)\) cost of the enqueue and dequeue operation follows from a standard argument, since it is well known that the amortized rebalancing cost of an insert operation on a red-black tree, i.e., the time spent after locating the father of the new node, is \(O(1)\) (see, e.g., Chapter III of [20] or Chapter 3.3 of [21]). Since upon enqueueing a new atom at the head or the tail of the list, the father of the new atom is either the maximal or the minimal node, it can be found in \(O(1)\) time. It is similarly shown that dequeuing takes \(O(1)\) amortized time.

A similar argument holds for the split operation. Suppose we search for an atom \(x\) of rank \(d\). By synchronously walking upward along the left and right ridge of the red-black tree, starting from the minimal and maximal node, we find the root of a subtree of height \(O(\log \min (d, n-d))\) containing the atom \(x\). Descending in this subtree, toward the leaf representing the atom \(x\), takes \(O(\log \min (d, n-d))\) time, after which we can do the actual split in \(O(\log \min (d, n-d))\) time. The amortized time for 1 is also \(O(\log \min (d, n-d))\).

To prove that a sequence of \(O(m)\) operations on \(n\) initially empty splittable queues can be performed in \(O(m)\) time, we provide each queue with \(r-\log r\) credits, where \(r\) is the size (number of atoms) of the queue (we consider logarithms in base 2); see [5] for a similar analysis. Suppose that, due to a split operation, a queue of size \(r\) is split into two queues of size \(r_{1}\) and \(r_{2}\), where \(r_{1} \geq r_{2}\). To restore the credit invariant we deposit one additional credit for this split operation. Then the credits \(r_{1}-\log r_{1}\) and \(r_{2}-\log r_{2}\) for the new queues are available, since \(2 r_{1} \geq r\) implies that

$$
r-\log r+1 \geq\left(r_{1}-\log r_{1}\right)+\left(r_{2}-\log r_{2}\right)+\log r_{2}
$$

Restoring the credit invariants for the collection of queues upon an enqueue or dequeue operation is similar.

## References

- J. Abello and K. Kumar. visibility graphs and oriented matroids. In R. Tamassia and I. G. Tollis, editors, Graph Drawing (Proc. GD '94), pages 147-158. Lecture Notes in Computer Science, volume 894. Springer-Verlag, Berlin, 1995.

- P. K. Agarwal, N. Alon, B. Aronov, and S. Suri. Can visibility graphs be represented compactly? Discrete Comput. Geom., 12:347-365, 1994.

- C. Aragon and R. Seidel. Randomized search trees. Proc. 30th Ann. IEEE Syrup. on Foundations of ComputerScience, pages 540-545, 1989.

- T. Asano, T. Asano, L. Guibas, J. Hershberger, and H. lmai. visibility of disjoint polygons. Algorithmica, 1:49~63, 1986.

- B. Chazelle and H. Edelsbrunner. An optimal algorithm for intersecting line segments in the plane. J. Assoc. Comput. Mach., 39:1-54, 1992.

- C. Coullard and A. Lubiw. Distance visibility graphs, lnternat. J. Comput. Geom. Appl., 2:349-362, 1992.

- E Durand and C. Puech. The visibility complex made visibly simple. Video Proc. 1 lth Ann. ACM Symp. on computational Geometry, page V2, Vancouver, 1995.

- H.EdelsbrunnerandL. J.Guibas.Topotogicallysweepinganarrangement.J. Comput. System Sci., 38:165194, 1989. Corrigendum in 42:249-251, 1991.

- H. N. Gabow and R. E. Tarjan. A linear-time algorithm for a special case of disjoint set union. J. Comput. System Sci., 30:209-221, 1985.

- S. K. Ghosh and D. M. Mount. An output-sensitive algorithm for computing visibility graphs. SlAM J. Comput., 20:888-910, 1991.

- L. J. Guibas and J. Hershberger. Computing the visibility graph of n line segments in O(n 2) time. Bull. EATCS, 26:13-20, 1985.

- J. Hershberger. An optimal visibility graph algorithm for triangulated simple polygons. Algorithmica, 4:141-155, 1989.

- K. Hoffmann, K. Mehlhorn, P. Rosenstiehl, and R. E. Tarjan. Sorting Jordan sequences in linear time using level-linked search trees, lnform, and Control, 68:170-184, 1986.

- S. Kapoor and S. N. Maheshwari. efficient algorithms for euclidean shortest paths and visibility problems with polygonal obstacles. Proc. 4th Ann. ACM Symp. computational Geometry, pages 178-182, 1988.

- D. E. Knuth. The Art of Computer Programming: Fundamental algorithms, second edition. World Student Series Edition. Addison-Wesley, Reading, MA, 1973.

- D. E. Knuth. ((Literate Programming)). Center for Study of Language and Information, Lectures Notes, volume 27, 1992.

- B. Korte, L. Lov~z, and R. Schrader. Greedoids. algorithms and Combinatorics, Number 4. SpringerVerlag, Berlin, 1991.

- T. Lozano-P6rez and M. A. Wesley. An algorithm for planning collision-flee paths among polyhedral obstacles. Commun. ACM, 22(10):560-570, 1979.

- P. McMullen. Modern developments in regular polytopes. In T. Bisztriczky, P. McMullen, R. Schneider, and A. Ivi~ Weiss, editors, Polytopes: Abstract, Convex and computational, pages 97-124. NATO ASI Series, volume 440. Kluwer, Dordrecht, 1994.

- K. Mehlhorn. Data Structures and algorithms 1: Sorting and Searching. EATCS Monographs on Theoretical Computer Science, volume 1. Springer-Verlag, Berlin, 1984.

- B. M. E. Moret and H. D. Shapiro. algorithms from P to NP, volume I. Benjamin Cummings, Redwood City, CA, 1990.

- J. O' Rourke. computational geometry column 18. lnternat. J. Comput. Geom. Appl., 3(1): 107-113, 1993.

- M. H. Overmars and E. Welzl. New methods for computing visibility graphs. Proc. 4th Ann. ACM Syrup. on computational Geometry, pages 164-171, 1988.

- M. Pocchiola and G. Vegter. The visibility complex. Proc. 9th Ann. ACM Symp. on computational Geometry, pages 328-337, 1993. Full version to appear in lnternat. J. Comput. Geom. Appl., 1996.

- M. Pocchiola and G. Vegter. Order types and visibility types of configurations of disjoint convex plane sets (extented abstract). Technical Report 94-4, Labo. d'Inf, de I'ENS, Paris, January 1994.

- M. Pocchiola and G. Vegter. Minimal tangent visibility graphs. Comput. Geom. Theory Appl., 1996. To appear.

- H. Rohnert. Time and space efficient algorithms for shortest paths between convex polygons. Inform. Process. Leg., 27:175-179, 1988.

- R. P. Stanley. Enumerative Combinatorics, volume 1. Wadsworth & Brooks Cole, Monterey, CA, 1986.

- S. Sudarshan and C. P. Rangan. A fast algorithm for computing sparse visibility graphs. Algorithmica, 5:201-214, 1990.

- E. Welzl. Constructing the visibility graph of n line segments in the plane. Inform. Process. Lett., 20:167171, 1985.
