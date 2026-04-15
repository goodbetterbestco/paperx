# Self-Overlapping Curves Revisited

David Eppstein, Elena Mumford

\( { }^{1} \) Computer Science Department

## Abstract

A surface embedded in space, in such a way that each point has a neighborhood within which the surface is a terrain, projects to an immersed surface in the plane, the boundary of which is a self-intersecting curve. Under what circumstances can we reverse these mappings algorithmically? Shor and van Wyk considered one such problem, determining whether a curve is the boundary of an immersed disk; they showed that the self-overlapping curves defined in this way can be recognized in polynomial time. We show that several related problems are more difficult: it is NP-complete to determine whether an immersed disk is the projection of a surface embedded in space, or whether a curve is the boundary of an immersed surface in the plane that is not constrained to be a disk. However, when a casing is supplied with a self-intersecting curve, describing which component of the curve lies above and which below at each crossing, we may determine in time linear in the number of crossings whether the cased curve forms the projected boundary of a surface in space. As a related result, we show that an immersed surface with a single boundary curve that crosses itself n times has at most 2 n 2 combinatorially distinct spatial embeddings, and we discuss the existence of fixed-parameter tractable algorithms for related problems.

## Introduction

In this paper we consider the algorithmic interplay between three types of topological object: self-crossing curves in the plane, two-dimensional surfaces mapped to the plane in a self-overlapping way, and threedimensional embeddings of surfaces that generalize the terrains familiar in computational geometry.

A surface or two-dimensional manifold with boundary is a compact Hausdorff topological space M such that every point p has a neighborhood homeomorphic to a closed disk. If this homeomorphism maps p to a boundary point of the disk, we call p a boundary point of M ; the set of boundary points is represented by ∂ M. An immersion or local homeomorphism is a continuous function i : M → T that, restricted to some neighborhood of every point, is a homeomorphism. We will here be concerned only with the case that T = \(R_{2}\), in which case we say that the surface M is immersed in the plane. If M is topologically a disk, we call i an immersed disk, but immersions of other types of manifold are also possible.

An embedding of a surface M into some space S is a closed subspace of S that is the image of M under a one-to-one continuous function e : M ↦→ S, the inverse of which is also continuous. A terrain is a surface embedded in space \(R_{3}\) such that every vertical line { (x, y, z) | x = \(c_{1}\), y = \(c_{2}\) \(\wp\) intersects it at most once. We are interested here in a localized version of this property: an generalized terrain is a surface M embedded in space \(R_{3}\) such that every point of M has a neighborhood the image of which is a terrain. Intuitively, such a surface is embedded in such a way that it has no vertical tangent lines, so that it has a consistent up-down orientation at every point. We will also call such a surface a embedded surface, when it does not introduce any confusion-see Figure 2 for an example. Intuitively, every generalized terrain can be constructed by gluing terrains along their boundaries. As with immersions, if M is topologically a disk, we call e (M) an embedded disk. If i is an immersion, i ( ∂ M) is a curve in the plane, which we call the boundary of the immersion ; with a suitable general-position assumption on i, this curve intersects itself only at proper pairwise crossings [7]. And if e is an embedding of a generalized terrain, we may project it into the plane to form an immersion:

![Figure 1.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-1-p002.png)

*Figure 1.: *

let \(\pi_{z}(x, y, z)=(x, y)\), then \(i(p)=\pi_{z}(e(p))\) is a local homeomorphism from \(M\) to \(\mathbb{R}^{2}\). We are interested in this paper in the conditions under which these transformations can be reversed: if we are given an immersed surface, when is it the projection of a generalized terrain? If we are given a curve in the plane, when is it the boundary of an immersed surface, or of the projection of a generalized terrain?

The study of this subject goes back to a paper by Whitney [10]. Shor and Van Wyk [8] first considered problems of this type from the algorithmic point of view. In our terminology, they showed that it is possible in polynomial time to determine whether a given curve (with proper pairwise crossings) is the boundary of an immersed disk. However, the possibilities of non-disk manifolds, of curves with multiple connected components, and of space embeddings as well as of plane immersions left many similar types of problems unsolved.

The cased curves mentioned on the right side of Figure 1 require further explanation. If one computes the projected boundary of a generalized terrain, one can obtain not just a set of curves in the plane, but also a 'casing' describing the above-below relationship of the two components of boundary curve at each crossing point. Casings are generally depicted graphically by interrupting the lower curve segment at a crossing, and allowing the upper curve segment to pass through the crossing uninterrupted, as we have done with the arcs and crossings of the figure. Casings of this type are standard in the two-dimensional description of mathematical knots, and have also been studied from the point of view of graph drawing [5]. By throwing away the casing information, we obtain an uncased curve in the plane, but an uncased curve with n crossings has \(2^{n}\) different casings. As we show, this casing information is crucial: with it we can, in linear time, reconstruct a generalized terrain (if one exists) that has the given cased curve as its projected boundary. In the absence of casing, as we show, it is NP-complete to determine whether a curve is the projected boundary of a generalized terrain, or the boundary of an immersed surface. Additionally, we show using a different reduction that it is NP-complete to determine whether an immersed disk is the projection of a generalized terrain. The question mark indicates the problem that remains open.

The problem of embedding a cased curve as a surface boundary is related to the study of so-called Seifert surfaces in the knot theory; however, we require the surface to be a generalized terrain, which is not generally the case for Seifert surfaces. Two spatial embeddings of a curve are called combinatorially equivalent if they provide it with the same casing. Thus, every curve with \(n\) crossings has at most \(2^{n}\) com binatorially different spatial embeddings. However, we show that an immersed surface has at most \(2^{n / 2}\) combinatorially different spatial embeddings. As we show, the ideas behind this combinatorial result lead to a fixed-parameter-tractable algorithm for testing whether an immersed surface can be lifted to an embedded surface.

Our main reasons for being interested in these problems are, firstly, their mathematical pedigree stretching back to Whitney'\(s_{1937}\) paper and, secondly, to resolve past confusion over how variations in the definition of a self-overlapping curve can change the computational complexity of the problem. We note for instance that the original conference version of the Shor and Van Wyk paper stated incorrectly that their methods solved both the immersion problem and the (still open) problem of testing whether a curve is the boundary of an embedded disk; this error was fortunately corrected in the journal version. Beyond these motivations, however, it also may be possible to use these problems in certain application areas of geometric computation. For instance, VLSI circuits are typically designed in terms of two-dimensional polygonal regions that overlap with each other in functional regions of the circuit; the global vertical ordering of these regions is less critical for the proper operation of the circuit than the vertical adjacencies between overlapping regions. Thus, our results may shed light on the difficulty of testing whether certain two-dimensional circuit designs have a valid three-dimensional representation. In architectural and landscape design, also, one often has surfaces with no vertical tangent (because people must walk on them!) with levels that overlap in complex patterns. More generally, we feel that the concept of a generalized terrain may be relevant in many of the computational geometry applications in which terrains arise.

## 2 Additional definitions and examples

Let \(i: M \rightarrow \mathbb{R}^{2}\) be a surface immersion in the plane. For every point \(p \in i(M)\) the thickness of \(i(M)\) at \(p\) is the number of points in the set \(i^{-1}(p)\). The boundary of an immersed surface splits \(\mathbb{R}^{2}\) into faces, where the thickness at all points belonging to the same face is the same. In fact, the thickness at \(p\) can be obtained from the boundary curve of the surface and is equal to the winding number of the curve around \(p\), defined as the number of times the curve goes around \(p\) in clockwise direction; see, e.g. [3] for a more detailed explanation of this concept.

A lifting of an immersion \(i\) is an embedding \(e: M \rightarrow \mathbb{R}^{3}\) that projects to \(i\) : that is, for all \(p \in M, i(p)=\pi_{z}(e(M))\), where \(\pi_{z}((x, y, z))=(x, y)\). Necessarily, \(e\) must describe a generalized terrain, for otherwise its projection would not be a local homeomorphism.

A hole in a surface \(M\) with an immersion \(i\) is a component \(C\) of the boundary of \(M\) such that \(i(C)\) is a simple curve and such that \(i\) maps a neighborhood of \(C\) to the outside of \(i(C)\). It is tempting to imagine that every immersed surface, and therefore every generalized terrain, must be topologically equivalent to a disk with holes, and that every immersed surface with a single boundary component must be topologically equivalent to a disk, but this is not true. For instance, Figure 3 shows a single curve that bounds an immersed surface topologically equivalent to a punctured torus.

![Figure 2. A generalized terrain, as viewed from above. Figure 3. This curve is the boundary of a unique immersed surface, topologically equivalent to a punctured torus.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-2-p004.png)

*Figure 2. A generalized terrain, as viewed from above. Figure 3. This curve is the boundary of a unique immersed surface, topologically equivalent to a punctured torus.: A generalized terrain, as viewed from above. Fig. 3. This curve is the boundary of a unique immersed surface, topologically equivalent to a punctured torus.*

In dealing with surfaces that have multiple boundary components, it is important to have the concept of an orientation of a curve, an assignment of a consistent cyclic ordering to the points of the curve. We orient the boundary components of a surface M so that (as viewed according to the orientation) the surface itself is to the right of the boundary curve. An immersion or embedding of a surface, having a given set of curves in the plane as boundary, is consistent with an orientation of those curves if this rightwards orientation intrinsic to the surface matches the orientation in the embedding. Thus, a simple closed curve bounding a disk in the plane is oriented clockwise, while the boundary of a hole is oriented counterclockwise.

Although every generalized terrain projects to an immersed surface and every immersed surface has a self-intersecting curve as a boundary, this correspondence does not always work in the opposite direction. Some immersed surfaces cannot be be lifted into space; Figure 4 shows an example of an immersed disk with a hole. Any embedding of this disk into \(\mathbb{R}^{3}\) would intersect itself at some curve connecting the self intersection points of its boundary curve. Some curves, such as the curve defined by the \(\infty\) symbol, cannot be embedded as boundaries of any immersed surfaces. Even more problematically, some curves can be a boundary of more than one immersed surface. Bennequin in [2] has given an example of a curve (see Figure 5) that can be viewed as a boundary of an immersed disk in five different ways. Two of these ways involve a single central component with three lobes hanging off it symmetrically, while the other three have a shape that is more like a single spiral strip. The three spiral disks can be embedded into space but the two three-lobed disks cannot.

![Figure 4. These two curves form the boundary of an immersed surface in two different ways, neither of which can be lifted to R 3 .](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-4-p004.png)

*Figure 4. These two curves form the boundary of an immersed surface in two different ways, neither of which can be lifted to R 3 .: These two curves form the boundary of an immersed surface in two different ways, neither of which can be lifted to R 3.*

![Figure 5. Bennequin’s curve bounding ﬁve different immersed disks.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-5-p004.png)

*Figure 5. Bennequin’s curve bounding ﬁve different immersed disks.: Bennequin’s curve bounding ﬁve different immersed disks. Bennequin's curve bounding five different immersed disks.*

## 3 Lifting a cased curve

Theorem 1. Given a single component curve with a given casing, we can determine whether the cased curve represents the boundary of a generalized terrain, and find a terrain having it as boundary, in time linear in the number of crossings of the curve.

Proof. We represent the curve using a modified form of Dowker notation [4] as follows:

- Label the n crossings of the curve by the numbers from 1 to n, arbitrarily.

- Choose a starting point on a part of the curve that lies on the exterior face of the drawing, and orient the curve consistently so that at this starting point the exterior face lies to the left of the oriented curve.

- At crossing i, draw two arrows, one on each of the two strands of the curve, outward from the crossing in the direction given by the orientation. Assign the arrow that is to the clockwise of the other arrow the number + i and the other the number-i.

- List the marks constructed in this way, in the order that they would be found by traversing the curve as oriented from the given starting point.

Additionally, we specify the casing as an \(n\)-bit binary number. It has a nonzero bit in position \(i-1\) if the strand labeled \(+i\) crosses above the strand labeled \(-i\), and a zero bit otherwise.

From these heights of the boundary curve, we can define a full surface, by stacking sheets of surface above each face of the drawing, the number of sheets equalling the winding number of the curve around the face. The height of the boundary curve tells us which sheets continue from one face to an adjacent face, and which sheet has its boundary there. This describes a valid surface if the following conditions are met:

We use the sequence of above-below relationships to compute an array Height \([i]\), that indicates the number of layers of surface that are supposed to lie below the curve as it heads outwards from the crossing labeled \(i\). Note that here, \(i\) may be either positive or negative. At the start of the labeling sequence, the height is zero: as it is on the outside face, the surface must be only one layer thick at that point. Subsequent heights can be computed in constant time per value, by traversing the curve: at an undercrossing, the height remains the same as at the previous arrow in the traversal order, while at an overcrossing, the height differs either by +1 or-1. For an overcrossing with label \(+i\), the new height is one larger than the previous height, but for an overcrossing with label \(-i\), the new height is one smaller than the previous height.

- The height of each strand of the curve lies between zero and the winding number of the face adjacent to the strand in the exterior direction. (These winding numbers may be determined from the curve itself in linear time, based on a similar traversal of the crossing sequence.)

- The casing determined by the heights matches the input casing.

Both conditions may easily be checked in linear time.

For a curve with multiple components we have a similar result but the complexity of the algorithm is higher.

Theorem 2. Given a cased oriented curve, we can determine whether the cased curve represents the bound ary of a generalized terrain and find a terrain having it as a boundary, in \(O\left(\min \left(n_{k}, n+k^{3}\right)\right)\) time, where \(n\) is the number of self-crossings of the curve and \(k\) is the number of its components.

Proof. We first calculate the winding numbers of the faces our curve \(C\) splits the plane into. For that we construct a dual graph \(D(C)\) of the curve defined as follows. \(D(C)\) has a vertex for each face. Two vertices \(v_{1}\) and \(v_{2}\) of \(D(C)\) are connected by a directed edge ( \(v_{1} \rightarrow v_{2}\) ) if the corresponding faces \(f_{1}\) and \(f_{2}\) are separated by a directed strand of \(C\) in such a way that \(f_{1}\) lies to the left as we move along the strand in the given direction. Let \(v\) have a winding number \(w\). Then every neighbor \(u\) of \(v\) has a winding number \(w-1\) if the corresponding edge is oriented from \(u\) to \(v\) or has the winding number \(w+1\) otherwise. (If we encounter a vertex with a negative winding number, the curve cannot be embedded as a generalized terrain boundary.) The winding number at the vertex representing the outer face is zero and \(D(C)\) is connected, so we can find winding numbers for all vertices of \(D(C)\) in time linear in \(n\). Next, as in the single-curve algorithm, we pick a starting point for every curve component \(c_{i}\) with as low thickness (the winding number of a face adjacent to the left of \(c_{i}\) ) as possible; let \(b_{i}\) denote the height of the curve \(c_{i}\) at that starting point. By tracing around the curve, as before, we can determine the height of the curve at each of its other strands \(s\), as an integer offset \(\gamma_{s}\) from \(b_{i}\). To ensure correctness of the casing, we have four types of constraints on these heights:

- bi + γ s values are non-negative for all strands s of ci, for all 0 ≤ i ≤ k. This will follow automatically from our choice of start point as long as bi itself is non-negative.

- Each bi + γ s ≤ w, where w is the winding number adjacent to s (on its left). We put all constraints of this type for a single component together to find the smallest integer Bi such that bi must be at most Bi in order to satisfy the given constraints.

- Each crossing between two strands s 1 and s 2 of the same component ci is cased correctly. This can be tested by comparing their offsets γ s 1 and γ s 2, and does not depend on the choice of bi.

- Each crossing between two different components ci and cj is cased correctly. This translates to the inequality bi ≥ bj -δ i j, for some value δ i j that can be calculated from the two offsets γ s i and γ s j at the two crossing strands s i ∈ ci and s j ∈ cj.

To handle constraints of types (1), (2), and (3), make a graph \(G\), with one vertex \(v_{i}\) per component \(c_{i}\), and a special starting vertex \(s\). Draw an edge with length zero from \(s\) to each \(v_{i}\), and an edge of length \(\delta_{i_{j}}\) from \(v_{j}\) to \(v_{i}\). If there exists a negative cycle in this graph, it corresponds to a set of constraints of type (4) that cannot be simultaneously satisfied, and no embedding exists. Otherwise, let \(b_{i}\) be \(-d\left(s, v_{i}\right)\) where \(d\) is the distance computed by a single source shortest path algorithm (note the minus sign). The edge from \(s\) to \(v_{i}\) forces \(d\left(s, v_{i}\right)\) to be non-positive, so \(b_{i} \geq 0\). The edge from \(v_{j}\) to \(v_{i}\) forces \(d\left(s, v_{i}\right) \leq d\left(s, v_{j}\right)+\delta_{i_{j}}\), the negation of a constraint of type (4), so all such constraints are satisfied. We can test whether this assignment of \(b_{i}\) values satisfies the constraints of type (2) by testing each such inequality; if one of the constraints of this type is violated then it together with the constraints on the shortest path to \(v_{i}\) cannot be simultaneously satisfied and no embedding exists. Therefore, the casing corresponds to an embedding if and only if setting \(b_{i}=-d\left(s, v_{i}\right)\) results in a height assignment that satisfies all constraints. If there are k curve components, the graph has \(O\left(\min \left(n, k^{2}\right)\right)\) edges, the negative cycle detection and single source shortest path in graph with negative edge weights can be done in \(O\left(\min \left(n_{k}, k^{3}\right)\right)\) time (e.g. by Bellman-Ford \(\left.[1,6]\right)\) so the total time would be \(O\left(\min \left(n_{k}, n+k^{3}\right)\right)\).

This result immediately leads to an \(O\left(n_{2}^{n}\right)\)-time algorithm, which we have implemented, for testing whether an uncased curve is the boundary of a generalized terrain: simply apply this linear time test to all possible casings of the curve. However, we believe that dynamic programming based on a separator decomposition of the curve arrangement will lead to improved running times. In such a technique, similarly to dynamic programs for other planar graph algorithms described by Smith and Wormald [9], one would partition the planar graph representing the input curve arrangement along a separator, and maintain a system of dynamic program states describing the heights of points on the input curve at each position at which the separator intersects the input curve. As the heights are at most \(n\), and each dynamic programming state would need to combine the heights of \(O(\sqrt{n})\) points, the time for such an approach would be exponential in \(O(\sqrt{n} \log n)\), improving the simple algorithm described above which is exponential in \(n\). However, such an algorithm would be significantly more complicated than the one we implemented.

![Figure 6. Reduction from P LANAR 3- COLORABILITY to immersibility or embeddability of a curve.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-6-p007.png)

*Figure 6. Reduction from P LANAR 3- COLORABILITY to immersibility or embeddability of a curve.: Reduction from planar 3-COLORABILITY to immersibility or embeddability of a curve.*

## 4 Hardness of immersion and embedding for uncased curves

As we now show, the absence of a casing makes it much more difficult to determine whether a given curve or set of curves is the boundary of an immersion or of a generalized terrain. The overall reduction is depicted in Figure 6. We start with a simplified version of the proof that applies to multiple oriented curves.

### 4.1 Oriented curves

We show that finding a surface immersion for an oriented curve is NP-complete using a reduction from planar 3-COLORABILITY. A planar 3-COLORABILITY instance tests whether a planar graph has a vertex-coloring with three colors, such that adjacent vertices have different colors.

We transform a planar graph \(G=(V, E)\) into a family \(C_{G}\) of \(|V|+3\) simple closed curves. \(|V|\) of these curves, which we call vertex-curves, are oriented counterclockwise and represent the vertices of \(G\). In any immersion or embedding having \(C_{G}\) as boundary, vertex-curves must be hole boundaries due to their orien tation. We place these curves in such a way that every pair of vertex-curves are either disjoint or have two points in common, and such that a pair of vertex-curves intersect if and only if the corresponding vertices of the graph are adjacent. The remaining three curves in \(C_{G}\), denoted \(c_{1}, c_{2}\) and \(c_{3}\), are oriented clockwise and surround all the vertex-curves. These three curves are disk-boundaries. See Figure 6(a),(b) for an example.

Lemma 1. If \(G\) has a three-coloring then there exists an immersed surface in the plane of which \(C_{G}\) is a boundary, having the topology of three disks with holes.

Proof. Form a disk in the plane for each of \(c_{1}, c_{2}\), and \(c_{3}\). For each vertex-curve \(c_{v}\), corresponding to a vertex \(v\) with color \(i\), form a hole with boundary \(c_{v}\) in the disk bounded by \(c_{i}\). Due to the coloring of \(G\), no two holes in the same disk overlap, so this forms a valid immersion of three punctured disks with boundaries \(c_{1}\), \(c_{2}\) and \(c_{3}\), together with the holes formed as above.

Corollary 1. If \(G\) has a three-coloring then \(C_{G}\) can be embedded in space as the boundary of a generalized terrain.

Proof. Lift the three punctured disks of Lemma 1 to distinct heights in \(\mathbb{R}^{3}\).

Next we prove that given a collection of surfaces \(S\) immersed in the plane so that the boundaries of \(S\) match the reduction \(C_{G}\) of a graph \(G\) we can define a 3-coloring of \(G\) from \(S\).

To do so, define a relation \(\sim\) between hole-boundaries of \(S: b_{1} \sim b_{2}\) if and only if there exists a curve in \(S\) that starts on \(b_{1}\), ends on \(b_{2}\), and does not pass through any points where two holes overlap.

Lemma 2. ∼ is an equivalence relation. Proof. Reflexivity and symmetry are clear. To prove transitivity, suppose \(b_{1} \sim b_{2}\) and \(b_{2} \sim b_{3}\), and find a curve from \(b_{1}\) to \(b_{3}\) by concatenating the curves \(b_{1} \sim b_{2}, b_{2} \sim b_{3}\), and a curve around the boundary of \(b_{2}\). Lemma 3. ∼ has at most three equivalence classes.

Proof. We pick a point \(p\) of the plane that is not in any of the holes: the immersed surface has three points \(p_{1}, p_{2}, p_{3}\) that map to \(p\). Then every point of the surface can be connected by a path to one of the three points \(p_{i}\). The path is constructed by first following a straight line segment to \(p\) and then detouring around any hole crossed by the line segment. Any two hole boundaries that connect to the same \(p_{i}\) must be equivalent to each other by concatenation of curves. Lemma 4. If hole-boundaries \(b_{i}\) and \(b_{j}\) cross each other, then \(b_{i}\) is not related by \(\sim\) to \(b_{j}\). Proof. Suppose for a contradiction that \(b_{i} \sim b_{j}\), let \(c\) be a curve connecting \(b_{i}\) and \(b_{j}\), and let \(s\) be a short line segment connecting \(b_{i}\) to \(b_{j}\) near their crossing. We can assume that \(c\) and \(s\) have the same endpoints, so together they define a (possibly self-intersecting) polygon, containing some other set of boundary holes. We choose \(c\) in such a way that this polygon contains as few boundary holes as possible, and then (among curves passing around the other holes in the same pattern) so that it is as short as possible. If \(c\) is not equal to \(s\), then it must be stretched tight against some other hole, and we can reduce the number of holes in the polygon by replacing \(c\) by a curve that goes the other way around the same hole. Thus \(c\) must be equal to \(s\). But then near the crossing \(b_{i}\) and \(b_{j}\) would be on the same layer of the surface, not possible. Thus \(\sim\) corresponds to a partition of \(V\) into three subsets, with no adjacent pair of vertices in the same subset; that is, \(a_{3}\)-coloring. \(G\) may be transformed into \(C_{G}\) in polynomial time, providing a polynomial-time many-one reduction from the known NP-complete problem of planar 3-COLORABILITY to immersing or embedding a set of oriented curves. These immersion and embedding problems may be solved in NP, in the case of embedding by considering heights of curves as used in the proof of Theorem 1, or in the case of immersions by a system of disks and gluings as used by Shor and Van Wyk [8]. We have proven Theorem 3. The problem of determining whether a set of oriented curves can be seen as a boundary of some immersed surface is NP-complete.

Corollary 2. The problem of determining whether a set of oriented curves can be seen as a boundary of an embedded surface is NP-complete.

Proof. Consider a planar graph \(G\) and the set of curves \(C_{G}\) described above. Assume we have a generalized terrain \(M\) that has \(C_{G}\) as a boundary. \(M\) projects to an immersed surface with \(C_{G}\) as a boundary which, as we have shown earlier, defines a three coloring of \(G\). In the other direction, by Corollary 1, given a 3-coloring of \(G\), we can embed \(C_{G}\) as a generalized terrain boundary.

### 4.2 Non-oriented curves

To prove a similar hardness result for unoriented curves, we simply replace each vertex-curve in the reduc tion by a curve that can only be embedded with one orientation, namely a curve with two self-intersections as depicted in Figure 7. If the self-crossing parts of these curves do not cross the other curves, they can only be oriented in such a way that the two outer lobes \(c_{1}\) and \(c_{2}\) of the curve act like hole boundaries in whatever surface they bound, i.e. for any immersed surface \(i\) the neighborhoods of \(c_{1}\) and \(c_{2}\) are mapped outside of \(i\left(c_{1}\right)\) and \(i\left(c_{2}\right)\) correspondingly. Hence, Corollary 3. It is NP-complete to determine whether a curve can be seen as a boundary of an immersed surface in the plane or an embedded surface in space.

![Figure 7. A curve that can only be embedded with one orientation.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-7-p009.png)

*Figure 7. A curve that can only be embedded with one orientation.: A curve that can only be embedded with one orientation.*

### 4.3 Finding a surface embedding for a single component curve

We finish this section by showing that it is NP-complete to determine the existence of an immersed or embedded surface for a curve even when it consist of a single component. As before, we reduce the problem from planar 3-colorability. Our reduction is as before, forming a system \(C_{G}\) of oriented curves that can be the boundary of an immersion or embedding if and only if the given graph \(G\) is 3-colorable; by adding an additional step to the reduction we transform \(C_{G}\) into a single curve without changing the existence of an immersion or embedding. The following lemmas make this extra step possible.

Lemma 5. Let \(C\) be a curve or set of oriented curves, and let \(C^{\prime}\) be a curve or set of curves formed by breaking \(C\) in two points along the boundary of a region of thickness one, and connecting these two breaks by a pair of parallel curves. Then the embedded or immersed surfaces for \(C\) are in 1-1 correspondence with Proof. In terms of the embedded or immersed surface, going from \(C\) to \(C^{\prime}\) corresponds to cutting the surface by removing a thin strip between the parallel curves, and going from \(C^{\prime}\) to \(C\) corresponds to gluing the cut back together. Cutting and gluing in this way are inverse operations, so both are one-to-one.

Lemma 6. Let \(C\) be a curve or set of oriented curves, and let \(R\) be a region bounded by two segments of curves and two crossing points, such that at least one of the two neighboring regions of \(R\) has smaller thickness than \(R\), and such that \(R\) contains no crossing of \(C\). Let \(C^{\prime}\) be the curve or set of oriented curves formed by uncrossing the two crossings bounding \(R\). Then \(C\) is the boundary of an embedded or immersed surface if and only if \(C^{\prime}\) is.

Proof. In terms of the embedded or immersed surface, the two curves bounding \(R\) must be boundaries of two different layers of the surface, so one can go from \(C\) to \(C^{\prime}\) by pulling these layers apart without changing the existence of an immersion or embedding (Figure 8). In the other direction, we can push the two layers together without any interaction between them; note however that for embeddings these two operations may not be one-to-one as we may have a choice whether to put one layer above or below the other.

Given an instance \(G\) of planar 3-colorability we construct the curve family \(C_{G}\) as in Section 4.1. We then transform \(C_{G}\) into a single curve by attaching the three outer curves together, and the holes to the outer curve, via thin strips that pass across the curve without covering any crossings, go outside the outer

![Figure 8. Uncrossing the dashed region bounded by two thick segments of curves and two indicated crossing points.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-8-p009.png)

*Figure 8. Uncrossing the dashed region bounded by two thick segments of curves and two indicated crossing points.: Uncrossing the dashed region bounded by two thick segments of curves and two indicated crossing points.*

![Figure 9. Reduction from A CYCLIC P ARTITION to liftability of an immersed surface.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-9-p010.png)

*Figure 9. Reduction from A CYCLIC P ARTITION to liftability of an immersed surface.: Reduction from A CYCLIC P ARTITION to liftability of an immersed surface.*

boundary, and then connect back to it, as shown in Figure 6(c). Each strip connecting two boundary curves can be removed by cutting it and performing a sequence of pulling-apart operations, so by Lemmas 5 and 6 the single curve is the boundary of an immersed or embedded surface if and only if \(C_{G}\) was. Hence we have the following theorem:

Theorem 4. The problem of determining the existence of an immersed or embedded surface that has a single component curve as a boundary is NP-complete.

## 5 Finding an embedding from a surface immersion

As we now show, it is NP-complete to lift an immersion to an embedding. Our reduction is via a graph theoretic problem, Acyclic Partition, which we also show to be NP-complete. define Acyclic Par TITION to be the decision problem that takes a directed graph \(G\) as input and outputs yes if and only if the vertices of \(G\) can be partitioned into two acyclic subsets. We first reduce Acyclic Partition to our problem by constructing an immersed disk that can be lifted into space if and only the input graph is a yes-instance of Acyclic Partition. Then we show that Acyclic Partition is NP-complete.

Lemma 7. ACYCLIC PARTITION can be reduced in polynomial time to disk immersion lifting.

Proof. Given a directed graph \(G\), we create an immersed disk, in the form of a single central area (a large rectangle) connected to a rectangle for each vertex of \(G\) that covers approximately the same region of the plane as the central area (perturbed slightly so the boundaries do not overlap). For each \(v\), the rectangle for \(v\) is connected to the central rectangle by a semicircular bridge that extends out from the central rectangle and back in to the rectangle for \(v\), as shown in Figure 9; no two of these bridges overlap. Additionally, whenever \(G\) has an edge \(v \rightarrow w\), we extend a rectangular tab out from the rectangle for \(v\) so that it covers the bridge for \(w\). See Figure 9 showing the complete reduction for a very simple graph.

How can the resulting immersed disk be embedded? Each vertex's rectangle must go either above or below the central rectangle, clearly, and as the rectangles all have a common intersection they can be totally ordered by height in any embedding. If \(v\) and \(w\) are both above the central rectangle, and there is an edge \(v \rightarrow w\), then the corresponding tab forces \(v\) to be above \(w\). Thus, the total order of the rectangles above the central rectangle is consistent with the edges. This is only possible if the edges connecting pairs of points corresponding to the rectangles above the central rectangle form a directed acyclic graph. Similarly the rectangles below the central rectangle can be embedded in such a way that their tabs do not block their bridges only if the corresponding vertices form a directed acyclic graph.

In the example in Figure 9, for instance, we can embed the rectangles in top-to-bottom order \(w, u\), central, \(v\). The two rectangles above the central rectangle, \(w\) and \(u\), define an acyclic graph as does the rectangle \(v\) by itself below the rectangle. However it would not work to try to put the rectangles for \(u\) and \(v\) on the same side of the central rectangle as each other, as the two of them form a cycle in the graph.

Next, as promised, we prove that ACYCLIC PARTITION is NP-complete.

Lemma 8. ACYCLIC PARTITION is NP-complete.

Proof. NOT-ALL-EQUAL-3SAT is a known-NP-complete variation of 3-SAT. A NOT-ALL-EQUAL-3SAT instance consists of a set of clauses, each having three terms (variables or negations of variables). It is satisfied by a truth assignment such that in every clause not all three terms have the same values.

We transform NOT-ALL-EQUAL-3SAT into ACYCLIC PARTITION as follows. Create a pair of graph vertices for each variable and its negation, with edges forming \(a_{2}\)-cycle (Figure 10, left); the two vertices must be in different parts of any acyclic bipartition. Create another triple of vertices for each clause, with edges forming \(a_{3}\)-cycle; not all three may be on the same side of any acyclic bipartition. Finally, add 2-cycles connecting the term vertices with corresponding clause vertices (Figure 10, right). The resulting graph has an acyclic bipartition if and only if the input NOT-ALL-EQUAL-3SAT instance is satisfiable. intersectionsq unionsq Combining these two reductions gives us our result: Theorem 5. It is NP-complete to determine whether an immersed surface can lift to a generalized terrain.

## 6 The number of embeddings of an immersion

Theorem 6. An immersed surface \(M\) has at most \(2^{n / 2}\) combinatorially different spatial embeddings.

Proof. We construct an undirected multigraph \(G\) on a set of self-intersections of the boundary curve, as follows. From each self-intersection \(v\), formed by the crossing of the boundaries of two layers \(\ell_{i}\) and \(\ell_{j}\), trace a curve in \(\ell_{j}\) along the path formed in the plane by the boundary of \(\ell_{i}\), until reaching another crossing point \(w\) that involves a boundary of the layer in which the curve is being traced; add an edge in \(G\) connecting \(v\) and \(w\). Figure 12 depicts this construction for a curve that is the boundary of a unique immersed surface.

The obtained graph \(G\) is 2-regular: there is one edge for each layer involved in each crossing. If \(M\) is obtained from a generalized terrain, both crossings connected by any edge \(e\) of \(G\) must be cased the same way: for, the path traced out by \(e\) has at all points of the path one surface consistently above or below the boundary curve of the other, so there is no way for the two surfaces to swap heights. Therefore, for a casing coming from an embedding of \(M\), the edges around any cycle of \(G\) must alternate between upper and lower, so each cycle must have even length at least equal to two. Choosing one of two casings for each of at most \(n / 2\) cycles in \(G\), the total number of valid casings is at most \(2^{n / 2}\).

One consequence of this result is a simple \(O\left(n_{2}^{n / 2}\right)\)-time algorithm for finding a lifting of an immersed surface with a single boundary component, by testing all casings consistent with the graph \(G\). However, in many cases we can do better than this.

![Figure 10. Gadgets for the reduction from N OT - ALL - EQUAL -3 SAT to A CYCLIC P ARTITION .](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-10-p011.png)

*Figure 10. Gadgets for the reduction from N OT - ALL - EQUAL -3 SAT to A CYCLIC P ARTITION .: Gadgets for the reduction from N OT-ALL-EQUAL-3 SAT to A CYCLIC P ARTITION.*

![Figure 11. An immersed surface with 2 n / 2 combinatorially differ- ent spatial embeddings.](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-11-p012.png)

*Figure 11. An immersed surface with 2 n / 2 combinatorially differ- ent spatial embeddings.: An immersed surface with 2 n / 2 combinatorially different spatial embeddings.*

![Figure 12. The graph G formed from the crossings of an immersed surface. The curve shown in black is the boundary of a unique immersed surface; the corresponding graph consists of two 4-cycles and one 6-cycle (colored red, green, and blue).](/Users/evanthayer/Projects/stepview/docs/2009_self_overlapping_curves_revisited/figures/figure-12-p012.png)

*Figure 12. The graph G formed from the crossings of an immersed surface. The curve shown in black is the boundary of a unique immersed surface; the corresponding graph consists of two 4-cycles and one 6-cycle (colored red, green, and blue).: The graph G formed from the crossings of an immersed surface. The curve shown in black is the boundary of a unique immersed surface; the corresponding graph consists of two 4-cycles and one 6-cycle (colored red, green, and blue).*

Observe that, in Figure 12, the green cycle on the left consists of vertices and boundary paths that all lie on points contained in only two levels of the immersed surface. We call such a cycle an irrelevant cycle, because the existence of a three-dimensional embedding does not depend on how it is cased: if a three dimensional embedding with one of the two possible casings exists, then changing the casing of that cycle while keeping the casing of the rest of the drawing fixed will result in another valid embedding. The red and blue cycles in the figure are relevant cycles, because they are not irrelevant: they both include vertices that are contained within three layers of the immersion. It is possible for a cycle to have all its vertices contained in only two layers, but to have points on the curves forming its edges that are contained in three or more layers; in this case, also, we call it a relevant cycle. Then clearly, we can find a lifting of an immersed surface in time \(O\left(n_{2}^{k}\right)\), where \(k\) is the number of relevant cycles: try all casings of the relevant cycles, and pick a single fixed casing for each irrelevant one. Thus, the problem of lifting an immersion to an embedding is fixed-parameter tractable, with \(k\) as the fixed parameter.

Alternatively, we may use as a parameter the number \(c\) of crossings of the input curve that lie within three or more layers of the immersion. It is not difficult to show that \(k=O(c)\); for, each relevant cycle either It would be of interest to determine whether there is a fixed parameter tractable algorithm for the problem of finding a three-dimensional embedding for a given plane curve, without being given the corresponding immersion. In this case the multigraph \(G\) cannot be defined, since it depends on having a fixed immersion, but we may still use \(c\) as the parameter for testing fixed parameter tractability.

## References

- R. Bellman. On a routing problem. Quarterly of Applied Mathematics, 16(1):87-90, 1958.

- D. Bennequin. Exemples d'immersions du disque dans le plan qui ne sont pas projections de plongements dans l'espace. C. R. Acad. Sci. Paris Se'r., A-B 281(2-3, AII):A81-A84, 1975.

- W. G. Chinn and N. E. Steenrod. first Concepts of Topology. New Mathematical Library, MAA, 1966.

- C. H. Dowker and M. B. Thistlethwaite. Classification of knot projections. Topology Appl., 16:19-31, 1983.

- D. Eppstein, M. J. van Kreveld, E. Mumford, and B. Speckmann. Edges and switches, tunnels and bridges. In Proc. 10th Worksh. algorithms and Data Structures, volume 4619 of Lecture Notes in Computer Science, pages 77-88. Springer-Verlag, 2007.

- J. L. R. Ford and D. R. Fulkerson. Flows in Networks. Princeton University Press, Princeton, 1962.

- M. L. Marx. Extensions of normal immersions of S 1 into R 2. Trans. Amer. Math. Soc., 187:309-326, 1974.

- P. W. Shor and C. J. V. Wyk. Detecting and decomposing self-overlapping curves. Comput. Geom. Theory Appl., 2(1):31-50, 1992.

- W. D. Smith and N. C. Wormald. Geometric separator theorems and applications. In FOCS '98: Proceedings of the 39th Annual Symposium on Foundations of Computer Science, page 232, Washington, DC, USA, 1998. IEEE Computer Society.

- H. Whitney. On regular closed curves in the plane. Composition Math., 4:276-284, 1937.
