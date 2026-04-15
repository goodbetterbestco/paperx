# Recognizing Weakly Simple Polygons

Hugo A. Akitaya, Greg Aloupis, Jeff Erickson, Csaba D. Tóth, Jeff Erickson , and

Department of Computer Science, Tufts University, Medford, MA, USA
Department of Computer Science, University of Illinois, Urbana-Champaign, IL, USA
Department of Mathematics, California State University Northridge, Los Angeles, CA, USA Department of Computer Science, University of Illinois, Urbana-Champaign

## Abstract

We present an O ( n log n )-time algorithm that determines whether a given planar n -gon is weakly simple. This improves upon an O ( n 2 log n )-time algorithm by Chang, Erickson, and Xu [4]. Weakly simple polygons are required as input for several geometric algorithms. As such, how to recognize simple or weakly simple polygons is a fundamental question. 1998 ACM Subject Classification I.3.5 Computational Geometry and Object Modeling Keywords and phrases weakly simple polygon, crossing Digital Object Identifier 10.4230 LIPIcs.SoCG.2016.8

## Introduction

A polygon is simple if it has distinct vertices and interior-disjoint edges that do not pass through vertices. Geometric algorithms are often designed for simple polygons, but many also work for degenerate polygons that do not 'self-cross.' A polygon with at least three vertices is weakly simple if for every ε > 0, the vertices can be perturbed by at most ε to obtain a simple polygon. Such polygons arise naturally in numerous applications, e.g., for modeling planar networks or as the geodesic hull of points within a simple polygon (Fig. 1).

Several definitions have been proposed for weakly simple polygons, each formalizing the intuition that a weakly simple polygon does not cross itself. Some of these definitions were unnecessarily restrictive or incorrect; see [4] for a detailed discussion. Ribó Mor [7] proved that a weakly simple polygon with at least three vertices can be perturbed into a simple polygon continuously while preserving the lengths of its edges, and maintaining that no two edges properly cross. Chang et al. [4] gave an equivalent definition for simple polygons in terms of the Fréchet distance (see Section 2), in which a polygon is perturbed into a simple closed curve. The latter definition is particularly useful for recognizing weakly simple polygons. Apart from perturbing vertices, it allows transforming edges into polylines (by subdividing the edges with Steiner points which may be perturbed). The perturbation of a vertex incurs only local changes, and need not affect the neighborhood of adjacent vertices.

It is easy to decide whether an n-gon is simple in \(O(nlogn)\) time by a sweepline algorithm [8]. Chazelle's triangulation algorithm recognizes simple polygons in \(O(n)\) time, because it only produces a triangulation if the input is simple [5]. Recognizing weakly simple polygons is more subtle. Cortese et al. [6] achieved this in \(O(n3)\)-time. Chang et al. [4] improved this to \(O(n2logn)\) in general; and to \(O(nlogn)\) for several special cases. They

∗ This work was partially supported by the NSF grants CCF-1408763, CCF-1422311, and CCF-1423615.

Editors: Sándor Fekete and Anna Lubiw; Article No. 8; pp. 8:1-8:16

![Figure 1 (a) A simple polygon P . (b) Eight points in the interior of P (solid dots); their geodesic hull is a weakly simple polygon P ′ with 14 vertices. (c) A perturbation of P ′ into a simple polygon.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-1-p002.png)

*Figure 1 (a) A simple polygon P . (b) Eight points in the interior of P (solid dots); their geodesic hull is a weakly simple polygon P ′ with 14 vertices. (c) A perturbation of P ′ into a simple polygon.: Figure 1 (a) A simple polygon P. (b) Eight points in the interior of P (solid dots); their geodesic hull is a weakly simple polygon P ′ with 14 vertices. (c) A perturbation of P ′ into a simple polygon.*

identified two features that are difficult to handle: A spur is a vertex whose incident edges overlap, and a fork is a vertex that lies in the interior of an edge (a vertex may be both a fork and a spur). For polygons with no forks or no spurs, Chang et al. [4] gave an \(O(n \log n)\)-time algorithm. In the presence of both forks and spurs, their solution is to eliminate forks by subdividing all edges that contain vertices in their interiors, potentially creating a quadratic number of vertices. We show how to manage this situation efficiently, while building on ideas from [4, 6] and from Arkin et al. [2], and obtain the following main result. - Theorem 1. Deciding whether a given \(n\)-gon is weakly simple takes \(O(n \log n)\) time.

Our algorithm is detailed in Sections 3-5. It consists of three phases, simplifying the input polygon by a sequence of reduction steps. first, the preprocessing phase applies known methods such as crimp reductions and node expansions (Section 3). Second, the bar simplification phase successively eliminates all forks (Section 4). Third, the spur elimination phase eliminates all spurs (Section 5). We can also perturb any weakly simple polygon into a simple polygon, in \(O(n \log n)\) time, by reversing the sequence of operations.

## 2 Preliminaries

Here, we review definitions from [4] and [6]. We adopt terminology from [4].

Polygons and weak simplicity. An arc in \(\mathbb{R}^{2}\) is a continuous function \(\gamma:[0,1] \rightarrow \mathbb{R}^{2}\). A closed curve is a continuous function \(\gamma: \mathbb{S}^{1} \rightarrow \mathbb{R}^{2}\). A closed curve \(\gamma\) is simple (also known as a Jordan curve) if it is injective. \(A(simple)\) polygon is the image of a piecewise linear (simple) closed curve. Thus a polygon \(P\) can be represented by a cyclic sequence of points \(\left(p_{0}, \ldots, p_{n-1}\right)\), called vertices, where the image of \(\gamma\) consists of line segments \(p_{0} p_{1}, \ldots, p_{n-2} p_{n-1}\), and \(p_{n-1} p_{0}\) in this cyclic order. Similarly, a polygonal chain (alternatively, path) is the image of a piecewise linear arc, and can be represented by a sequence of points \(\left[p_{0}, \ldots, p_{n-1}\right]\). A polygon \(P=\left(p_{0}, \ldots, p_{n-1}\right)\) is weakly simple if \(n=2\), or if \(n>2\) and for every \(\varepsilon>0\) there is a simple polygon \(\left(p_{0}^{\prime}, \ldots, p_{n-1}^{\prime}\right)\) such that \(\left|p_{i} p_{i}^{\prime}\right|<\varepsilon\) for all \(i=0, \ldots, n-1\).

![Figure 2 (a) The bar decomposition for a weakly simple polygon P with 16 vertices ( P is perturbed into a simple polygon for clarity). (b) Image graph of P . (c) A combinatorial representation of P .](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-2-p003.png)

*Figure 2 (a) The bar decomposition for a weakly simple polygon P with 16 vertices ( P is perturbed into a simple polygon for clarity). (b) Image graph of P . (c) A combinatorial representation of P .: Figure 2 (a) The bar decomposition for a weakly simple polygon P with 16 vertices (P is perturbed into a simple polygon for clarity). (b) Image graph of P. (c) A combinatorial representation of P.*

Bar decomposition and image graph. Two edges of a polygon \(P\) cross if their interiors intersect at precisely one point. The edges of a weakly simple polygon cannot cross. In the following, we assume that such crossings have been ruled out. Two edges of \(P\) overlap if their intersection is a nondegenerate line segment. The transitive closure of the overlap relation is an equivalence relation on the edges of \(P\); see Fig. 2(a) where equivalence classes are shaded. The union of all edges in an equivalence class is called a bar. All bars of a polygon can be computed in \(O(n \log n)\) time [4]. The bars are line segments that are pairwise noncrossing and nonoverlapping, and the number of bars is \(O(n)\).

The vertices and bars of \(P\) define a planar straight-line graph \(G\), called the image graph of \(P\). We call the vertices and edges of \(G\) nodes and segments to distinguish them from the vertices and edges of \(P\). Every node that is not in the interior of a bar is called sober. The set of nodes in \(G\) is \(\left\{p_{0}, \ldots, p_{n-1}\right\}\) (note that \(P\) may have repeated vertices that correspond to the same node); two nodes are connected by an edge in \(G\) if they are consecutive nodes along a bar; see Fig. 2(b). Hence \(G\) has \(O(n)\) vertices and edges, and it can be computed in \(O(n \log n)\) time [4]. Note, however, that up to \(O(n)\) edges of \(P\) may pass through a node of \(G\), and there may be \(O\left(n^{2}\right)\) edge-node pairs such that an edge of \(P\) passes through a node of \(G\). An \(O(n \log n)\)-time algorithm cannot afford to compute these pairs explicitly.

Operations. We use certain elementary operations that modify a polygon and ultimately eliminate forks and spurs. An operation that produces a weakly simple polygon iff it is performed on a weakly simple polygon is called ws-equivalent. We shall use some known wsequivalent operations, and introduce several new ws-equivalent operations in Sections 3.3-5.

Combinatorial characterization of weak simplicity. To show that an operation is ws equivalent, it suffices to show the existence of \(\varepsilon\)-perturbations. We will use perfect matchings to combinatorially represent \(\varepsilon\)-perturbations (independent of \(\varepsilon\) or any specific embedding). This representation is a variation of the "strip system" introduced in [4].

Let \(P\) be a polygon and \(G\) its image graph. We construct a family of simple polygons as follows. Let \(\varepsilon=\varepsilon(P) \in(0,1)\), to be specified shortly. For every node \(u\) of \(G\), draw a disk \(D_{u}\) of radius \(\varepsilon\) centered at \(u\). Choose \(\varepsilon\) sufficiently small so that the disks are pairwise disjoint, and no disk intersects a nonincident segment of \(G\). Let the corridor \(N_{u_{v}}\) of segment \(u_{v}\) be the set of points at distance at most \(\varepsilon^{2}\) from \(u_{v}\), outside of the disks \(D_{u}\) and \(D_{v}\), that is, \(N_{u_{v}}=\left\{p \in \mathbb{R}^{2}: \operatorname{dist}(p, u_{v}) \leq \varepsilon^{2}, p \notin D_{u} \cup D_{v}\right\}\). Reduce \(\varepsilon\) further, so that all corridors are pairwise disjoint, and also disjoint from any disk \(D_{w}, w \notin\{u, v\}\). For every segment \(u_{v}\) of \(G\), let the volume \(\operatorname{vol}(u_{v})\) be the number of edges of \(P\) between \(u\) and \(v\). For every segment \(u_{v}\), draw \(\operatorname{vol}(u_{v})\) parallel line segments between \(\partial D_{u}\) and \(\partial D_{v}\) within \(N_{u_{v}}\). Finally, for every disk \(D_{u}\), construct a plane straight-line perfect matching between the segment endpoints

![Figure 3 Two perturbations of a weakly simple polygon on 6 vertices (all of them spurs) that alternate between two distinct points in the plane.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-3-p004.png)

*Figure 3 Two perturbations of a weakly simple polygon on 6 vertices (all of them spurs) that alternate between two distinct points in the plane.: Figure 3 Two perturbations of a weakly simple polygon on 6 vertices (all of them spurs) that alternate between two distinct points in the plane.*

![Figure 4 A crimp reduction replaces [ a, b, c, d ] with [ a, d ]. Top](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-4-p004.png)

*Figure 4 A crimp reduction replaces [ a, b, c, d ] with [ a, d ]. Top: image graph. Bottom: polygon.*

Note that the above combinatorial representation, which will be used in our proofs, may have \(\Theta\left(n^{2}\right)\) size, since each edge passing through a node \(u\) contributes one edge to a matching in \(D_{u}\). We use this simple combinatorial representation in our proofs of correctness, but our algorithm will not maintain it explicitly.

In the absence of spurs, a weakly simple polygon \(P\) defines a unique crossing-free perfect matching in each disk \(D_{u}\) [4] which defines a 2-regular graph \(Q\). Consequently, to decide whether \(P\) is weakly simple it is enough to check whether \(Q \in \Phi(P)\). This is no longer the case in the presence of spurs. In fact, it is not difficult to construct weakly simple \(n\)-gons that admit \(2^{\Theta(n)}\) combinatorially different perturbations into simple polygons; see Fig. 3.

Preprocessing

By a standard line sweep [8], we detect any edge crossing. We then simplify the polygon, using some known steps from [2,4], and some new. All of this takes \(O(n \log n)\) time.

### 3.1 Crimp reduction

Arkin et al. [2] gave an \(O(n)\)-time algorithm for recognizing weakly simple \(n\)-gons where all edges are collinear. They define the ws-equivalent crimp-reduction operation (see the full paper [1] for details). A crimp is a chain of three consecutive edges \([a, b, c, d]\) such that both the first edge \([a, b]\) and the last edge \([c, d]\) contain the middle edge \([b, c]\) (the containment need not be strict). The crimp-reduction replaces the crimp with edge \([a, d]\); see Fig. 4.

Given a chain of two edges \([a, b, c]\) such that \([a, b]\) and \([b, c]\) are collinear but do not overlap, the merge operation replaces \([a, b, c]\) with a single edge \([a, c]\). The merge operation (as well as its inverse, subdivision) is ws-equivalent by the definition of weak simplicity in terms of Fréchet distance [4]. If we greedily apply crimp-reductions and merge operations (cf. Section 2), in linear time we obtain a polygon with the following two properties:

- (A1) Every two consecutive collinear edges overlap (i.e., form a spur).

- (A2) No three consecutive collinear edges form a crimp.

![Figure 5 Node expansion. (Left) Changes in the image graph. (Right) Changes in P (the vertices are perturbed for clarity); new nodes are shown as squares.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-5-p005.png)

*Figure 5 Node expansion. (Left) Changes in the image graph. (Right) Changes in P (the vertices are perturbed for clarity); new nodes are shown as squares.: Figure 5 Node expansion. (Left) Changes in the image graph. (Right) Changes in P (the vertices are perturbed for clarity); new nodes are shown as squares.*

![Figure 6 The old-bar-expansion converts a non-weakly simple polygon to a weakly simple one.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-6-p005.png)

*Figure 6 The old-bar-expansion converts a non-weakly simple polygon to a weakly simple one.: Figure 6 The old-bar-expansion converts a non-weakly simple polygon to a weakly simple one.*

- Lemma 2. Let \(C=\left[e_{i}, \ldots, e_{k}\right]\) be a chain of collinear edges in a polygon with properties (A1) and (A2). Then the sequence of edge lengths \(\left(\left|e_{i}\right|, \ldots,\left|e_{k}\right|\right)\) is unimodal (all local maxima are consecutive); and no two consecutive edges have the same length, except possibly the maximal edge length that can occur at most twice.

However, this contradicts (A2). This proves unimodality, and that no three consecutive edges can have the same length. In fact if \(\left|e_{j}\right|\) is not maximal, one neighbor must be strictly smaller, to avoid the same contradiction.

### 3.2 Node expansion

Compute the bar decomposition of \(P\) and its image graph \(G\) (defined in Section 2, see Fig. 2). For every sober node of the image graph, we perform the ws-equivalent node-expansion operation, described by Chang et al. [4][Section 3] (Cortese et al. [6] call this a cluster expansion). Let \(u\) be a sober node of the image graph and \(D_{u}\) be the disk centered at \(u\) with radius sufficiently small so that \(D_{u}\) intersects only the segments incident to \(u\). For each segment \(u_{x}\) incident to \(u\), create a new node \(u^{x}\) at the intersection point \(u x \cap \partial D_{u}\). Then modify \(P\) by replacing each subpath \([x, u, y]\) passing through \(u\) by \(\left[x, u^{x}, u^{y}, y\right]\); see Fig. 5. If a node expansion produces an edge crossing, report that \(P\) is not weakly simple.

### 3.3 Bar expansion

Chang et al. [4][Section 4] define a bar expansion operation, referred in this paper as old-bar expansion. For a bar \(b\) of the image graph, draw a long and narrow ellipse \(D_{b}\) around the interior nodes of \(b\), and replace each maximal path that intersects with \(D_{b}\) by a straight-line edge. If \(b\) contains no spurs, old-bar-expansion is known to be ws-equivalent [4]. Otherwise, it can produce false positives, hence it is not ws-equivalent; see Fig. 6 for an example.

New bar expansion operation. Let \(b\) be a bar in the image graph with at least one interior node; see Fig. 7. Let \(D_{b}\) be an ellipse whose major axis is in \(b\) such that \(D_{b}\) contains all interior nodes of \(b\) (all nodes in \(b\) except its endpoints), but does not contain any other node of the image graph and does not intersect any segment that is not incident to some node inside \(D_{b}\). Similar to old-bar-expansion, the operation new-bar-expansion introduces subdivision vertices on \(\partial D_{b}\), but all interior vertices of \(b\) remain at their original positions.

![Figure 7 The changes in the image graph caused by new-bar-expansion .](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-7-p006.png)

*Figure 7 The changes in the image graph caused by new-bar-expansion .: Figure 7 The changes in the image graph caused by new-bar-expansion.*

![Figure 8 Formation of new clusters around (left) a sober node and (right) a node on the boundary of an elliptical disk. The roots of the induced trees are colored blue.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-8-p006.png)

*Figure 8 Formation of new clusters around (left) a sober node and (right) a node on the boundary of an elliptical disk. The roots of the induced trees are colored blue.: Figure 8 Formation of new clusters around (left) a sober node and (right) a node on the boundary of an elliptical disk. The roots of the induced trees are colored blue.*

For each segment \(u_{x}\) between a node \(u \in b \cap D_{b}\) and a node \(x \notin b\), create a new node \(u^{x}\) at the intersection point \(u x \cap \partial D_{b}\) and subdivide every edge \([u, x]\) to a path \(\left[u, u^{x}, x\right]\). For each endpoint \(v\) of \(b\), create two new nodes, \(v^{\prime}\) and \(v^{\prime \prime}\), as follows. Node \(v\) is adjacent to a unique segment \(v w \subset b\), where \(w \in b \cap D_{b}\). Create a new node \(v^{\prime} \in \partial D_{b}\) sufficiently close to the intersection point \(v w \cap \partial D_{b}\), but strictly above \(b\); and create a new node \(v^{\prime \prime}\) in the interior of segment \(v w \cap D_{b}\). Subdivide every edge \([v, y]\), where \(y \in b\), into a path \(\left[v, v^{\prime}, v^{\prime \prime}, y\right]\). Since the new-bar-expansion operation consists of only subdivisions (and slight perturbations of the edges passing through the end-segments of the bars), it is ws-equivalent.

Terminology. Here, we classify each path in \(D_{b}\). All nodes \(u \in \partial D_{b}\) lie either above or below \(b\). We call them top and bottom nodes, respectively. Let \(\mathcal{P}\) denote the set of maximal

- cross chain if u x 1 and u y k are top and bottom nodes respectively;

- top chain (resp., bottom chain) if both u x 1 and u y k are top nodes (resp., bottom nodes);

- pin if p = [u x 1, \(u_{1}\), u x 1] (note that every pin is a top or a bottom chain);

- V-chain if p = [u x 1, \(u_{1}\), u y 1], where x = y and p is a top or a bottom chain.

Let \(\mathcal{P}\) in \(\subset \mathcal{P}\) be the set of pins, and \(\mathcal{V} \subset \mathcal{P}\) the set of V-chains. Let \(M_{c_{r}}\) be the set of longest edges of cross chains in \(\mathcal{P}\) (by Lemma 2, each cross chain contributes one or two edges). Every weakly simple polygon has the following property.

- (A3) No edge in M cr lies in the interior of any other edge of P.

We can test property (A3) in \(O(n \log n)\) time at preprocessing (for each bar, sort all edges by their endpoints, and compute \(M_{c_{r}}\) ). If property (A3) fails, we report that \(P\) is not weakly simple. The operations introduced in Section 2 maintain properties (A1)-(A3) in bars.

### 3.4 Clusters

As a preprocessing for spur elimination (Section 5), we group all nodes that do not lie inside a bar into clusters. After node-expansion and new-bar-expansion, all such nodes lie on a boundary of a disk (circular or elliptical). For every sober node \(u\), we create \(\operatorname{deg}(u)\) clusters as follows. Refer to Fig. 8. The node expansion has replaced \(u\) with new nodes on \(\partial D_{u}\). Subdivide each segment in \(D_{u}\) with two new nodes. For each node \(v \in \partial D_{u}\), form a cluster \(C(v)\) that consists of \(v\) and all adjacent (subdivision) nodes inside \(D_{u}\). For each node \(u\) on the boundary of an elliptical disk \(D_{b}\), subdivide the unique edge outside \(D_{b}\) incident to \(u\) with a node \(u^{*}\). Form a cluster \(C\left(u^{*}\right)\) containing \(u\) and \(u^{*}\).

![Figure 9 The changes in the image graph caused by a bar simpliﬁcation.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-9-p007.png)

*Figure 9 The changes in the image graph caused by a bar simpliﬁcation.: Figure 9 The changes in the image graph caused by a bar simpliﬁcation. simplification.*

- (I1) \(C(u)\) induces a tree T [u] in the image graph rooted at u.

- (I2) Every maximal path of P in \(C(u)\) is of one of the following two types:

- (a) both endpoints are at the root of T [u] and the path contains a single spur;

- (b) one endpoint is at the root, the other is at a leaf, and the path contains no spurs. Additionally, each leaf node lscript satisfies the following:

- (I3) lscript has degree one or two in the image graph of P ;

- (I4) there is no spur at lscript ;

- (I5) no edge passes through lscript (i.e., there is no edge [a, b] such that lscript ∈ ab but lscript negationslash∈ { a, b } ).

Initially, every cluster trivially satisfies (I1) and (I2.b) and every leaf node satisfies (I3)-(I5) since it was created by a subdivision. The operations in Section 4 maintain these invariants.

Dummy vertices. Although the operations described in Sections 4 and 5 introduce nodes in clusters, the image graph will always have \(O(n)\) nodes and segments. A vertex at a cluster node is called a benchmark if it is a spur or if it is at a leaf node; otherwise it is called a dummy vertex. Paths traversing clusters may contain \(\Theta\left(n^{2}\right)\) dummy vertices in the worst case, however we do not store these explicitly. By (I1), (I2) and (I4) a maximal path in a cluster can be uniquely encoded by one benchmark vertex: if it goes from a root to a spur at an interior node \(s\) and back, we record only \([s]\); and if it traverses \(T[u]\) from the root to a leaf \(\ell\), we record only [ \(\ell\) ].

Bar simplification

In this section we introduce three new ws-equivalent operations and show that they can eliminate all vertices from each bar independently (thus eliminating all forks). The bar decomposition is pre-computed, and the bars remain fixed during this phase (even though all edges along each bar are eliminated). We give an overview of the effect of the operations (Section 4.1), define them and show that they are ws-equivalent (Sections 4.2 and 4.3), and then show how to use these operations to eliminate all vertices from a bar (Section 4.4).

### 4.1 Overview

After preprocessing in Section 3, we may assume that P has no edge crossings and satisfies (A1)-(A3). We summarize the overall effect of the bar simplification subroutine for a given expanded bar.

Changes in the image graph \(\boldsymbol{G}\). Refer to Fig. 9. All nodes in the interior of the ellipse \(D_{b}\) are eliminated. Some spurs on \(b\) are moved to new nodes in the clusters along \(\partial D_{b}\). Segments inside \(D_{b}\) connect two leaves of trees induced by clusters.

![Figure 10 The changes in the polygon caused by a bar simpliﬁcation.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-10-p008.png)

*Figure 10 The changes in the polygon caused by a bar simpliﬁcation.: Figure 10 The changes in the polygon caused by a bar simpliﬁcation. simplification.*

![Figure 11 Left](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-11-p008.png)

*Figure 11 Left: Spur-reduction(u, v). Right: Node-split(u, v, w).*

Changes in the polygon P. Refer to Fig. 10. Consider a maximal path p in P that lies in D b. The bar simplification will replace p = [u, . . . , v] with a new path p ′ . By (I3)-(I4), only nodes u and v in p lie on ∂D b. If p is the concatenation of \(p_{1}\) and \(p_{2}\) (= p-11), then p ′ will be a spur in the cluster containing u (Fig. 10(a)). If p has no such decomposition, but its two endpoints are at the same node, u = v, then p ′ will be a single edge connecting two leaves in the cluster containing u (Fig. 10(b)). If the endpoints of p are at two different nodes, p ′ is an edge between two leaves of the clusters containing u and v respectively (Fig. 10(c)).

### 4.2 Primitives

The operations in Section 4.3 rely on two basic steps, spur-reductions and node splits (see Fig. 11). The proof of their ws-equivalence is available in the full paper [1]. Together with merge and subdivision, these operations are called primitives.

- spur-reduction (u, v). Assume that every vertex at node u has at least one incident edge [u, v]. Replace any path [u, v, u], with a single-vertex path [u].

- node-split (u, v, w). Assume segments uv and vw are consecutive in radial order around v, and not collinear with an adjacent segment; and P contains no spurs of the form [u, v, u] or [w,v, w]. Create node v ∗ in the interior of the wedge ∠ (u, v, w) sufficiently close to v ; and replace every path [u, v, w] with [u, v ∗ , w].

### 4.3 Operations

We describe three operations: pin-extraction, V-shortcut, and L-shortcut. The first two eliminate pins and V-chains, respectively, and the third simplifies chains in \(\mathcal{P}\) with two or more vertices in the interior of \(D_{b}\), removing one vertex at a time.

![Figure 13 V-shortcut . Changes in the image graph (top), changes in the polygon (bottom).](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-13-p009.png)

*Figure 13 V-shortcut . Changes in the image graph (top), changes in the polygon (bottom).: Figure 13 V-shortcut. Changes in the image graph (top), changes in the polygon (bottom). Figure 12 pin-extraction. Changes in the image graph (top), changes in the polygon (bottom).*

Pin-extraction and V-shortcut operations. These operations are combinations of primitives and, therefore, they are ws-equivalent. (I1)-(I5) are maintained by construction, and (A1)(A3) are also maintained within each bar. Proofs are available in the full paper [1].

- pin-extraction (u, v). Assume that P satisfies (I1)-(I5) and contains a pin [v, u, v] ∈ P in. By (I3), node v is adjacent to a unique node w outside of D b. Perform the following three primitives: (1) subdivision of every path [v, w] into [v, w ∗ , w]; (2) spur-reduction (v, u). (3) spur-reduction (w ∗ , v). See Fig. 12 for an example.

- V-shortcut (\(v_{1}\), u, \(v_{2}\)). Assume that P satisfies (I1)-(I5) and [\(v_{1}\), u, \(v_{2}\)] ∈ V. Furthermore, P contains no pin of the form [\(v_{1}\), u, \(v_{1}\)] or [\(v_{2}\), u, \(v_{2}\)], and no edge [u, q] such that segment uq is in the interior of the wedge ∠ (\(v_{1}\), u, \(v_{2}\)). By (I3), nodes \(v_{1}\) and \(v_{2}\) are each adjacent to unique nodes \(w_{1}\) and \(w_{2}\) outside of D b, respectively. The operation executes the following primitives sequentially: (1) nodesplit (\(v_{1}\), u, \(v_{2}\)), which creates u ∗ ; (2) node-split (u ∗ , \(v_{1}\), \(w_{1}\)) and node-split (u ∗ , \(v_{2}\), \(w_{2}\)); which create v ∗ 1, v ∗ 2 ∈ ∂D b ; (3) merge every path [v ∗ 1, u ∗ , v ∗ 2] to [v ∗ 1, v ∗ 2]. See Fig. 13 for an example.

L-shortcut operation. The purpose of this operation is to eliminate a vertex of a path that has an edge along a given bar. Before describing the operation, we introduce some notation. For a node \(v \in \partial D_{b}\), let \(L_{v}\) be the set of paths \(\left[v, u_{1}, u_{2}\right]\) in \(P\) such that \(u_{1}, u_{2} \in \operatorname{int}\left(D_{b}\right)\). Each path in \(\mathcal{P}\) is either in \(\mathcal{P} i_{n}\), in \(\mathcal{V}\) or has two subpaths in some \(L_{v}\). Recall that \(M_{c_{r}}\) is the set of longest edges of cross chains in \(\mathcal{P}\). Denote by \(\widehat{L_{v}} \subset L_{v}\) the set of paths \(\left[v, u_{1}, u_{2}\right]\), where \(\left[u_{1}, u_{2}\right]\) is not in \(M_{c_{r}}\). We partition \(L_{v}\) into four subsets: a path \(\left[v, u_{1}, u_{2}\right] \in L_{v}\) is in 1. \(L_{v}^{T R}\) (top-right) if \(v\) is a top vertex and \(x\left(u_{1}\right)<x\left(u_{2}\right)\);

- L TL v (top-left) if v is a top vertex and x (\(u_{1}\)) > x (\(u_{2}\));

![Figure 14 L-shortcut . Changes in the image graph (top), changes in the polygon (bottom).](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-14-p010.png)

*Figure 14 L-shortcut . Changes in the image graph (top), changes in the polygon (bottom).: Figure 14 L-shortcut. Changes in the image graph (top), changes in the polygon (bottom).*

- L BR v (bottom-right) if v is a bottom vertex and x (\(u_{1}\)) < x (\(u_{2}\));

- L BL v (bottom-left) if v is a bottom vertex and x (\(u_{1}\)) < x (\(u_{2}\)).

We partition \(\widehat{L_{v}}\) into four subsets analogously. We define the operation L-shortcut for paths in \(L_{v}^{T R}\); the definition for the other subsets can be obtained by suitable reflections.

- L-shortcut (v, T R). Assume that P satisfies (I1)-(I5), v ∈ ∂D b and L TR v = ∅ . By (I3), v is adjacent to a unique node \(u_{1}\) ∈ b and to a unique node w ∈ D b. Let U denote the set of all nodes \(u_{2}\) for which [v, \(u_{1}\), \(u_{2}\)] ∈ L TR v. Let u min ∈ U and u max ∈ U be the leftmost and rightmost node in U, respectively. Further assume that P satisfies:

- (B1) no pins of the form [v, \(u_{1}\), v];

- (B2) no edge [p, \(u_{1}\)] such that segment pu 1 is in the interior of the wedge ∠ (v, \(u_{1}\), \(u_{2}\));

- (B3) no edge [p, q] such that p ∈ ∂D b is a top vertex and q ∈ b, x (\(u_{1}\)) < x (q) < x (u max).

(See the full paper [1] for an justification of these assumptions.) Do the following.

- Create a new node v ∗ ∈ ∂D b to the right of v sufficiently close to v.

- For every path [v, \(u_{1}\), \(u_{2}\)] ∈ L TR v where \(u_{1}\) \(u_{2}\) is the only longest edge of a cross chain, create a crimp by replacing [\(u_{1}\), \(u_{2}\)] with [\(u_{1}\), \(u_{2}\), \(u_{1}\), \(u_{2}\)].

- Replace every path [w,v, \(u_{1}\), u min] by [w,v ∗ , u min].

- Replace every path [w,v, \(u_{1}\), \(u_{2}\)], where \(u_{2}\) ∈ U, by [w,v ∗ , u min, \(u_{2}\)]. See Fig. 14.

glyph[trianglerightsld] Lemma 3. L-shortcut is ws-equivalent and maintains (I1) -(I5).

Proof Sketch (see [1] for a full proof). W.l.o.g., assume L-shortcut (v, T R) is executed. Phase (1) is ws-equivalent by [2]. The rest of the operation is equivalent to subdividing every path in L TR v where \(u_{2}\) = u min into [v, \(u_{1}\), u min, \(u_{2}\)], node-split (v, \(u_{1}\), u min) (which creates u ∗ 1), node-split (w,v, u ∗ 1) (which creates v ∗ ) and merging every path [v ∗ , u ∗ 1, u min] to [v ∗ , u min]. Except for node-split (v, \(u_{1}\), u min), all primitives satisfy their constraints and therefore are ws-equivalent. It remains to show that (B1)-(B3) ensure that this primitive is ws-equivalent. Let P ′ be obtained from P after node-split (v, \(u_{1}\), u min). If P ′ is weakly simple, by changing its embedding we can move u ∗ 1 arbitrarily close to \(u_{1}\) without affecting weak simplicity, hence P is weakly simple. It remains to show that if P is weakly simple, there exists Q ∈ Φ(P) such that the paths in L TR v are the topmost paths in the linear order induced by Q. Indeed, if there is one edge [p, q] above one path in L TR v, by (B1)-(B3), it must be part of a path [p, q, r] such that q is a spur and x (u max) < x (p) and x (u max) < x (r). Then, it can always be moved below the lowest edge [\(u_{2}\), \(u_{3}\)] adjacent to a path in L TR v without introducing any crossing (similar to crimp reduction; see Fig. 15). Phase (1) ensures that this is always possible, since after that phase every path in L TR v has an adjacent edge

![Figure 16 Life cycle of a cross chain in the while loop of bar-simpliﬁcation . The steps applied, from left to right, are](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-16-p011.png)

*Figure 16 Life cycle of a cross chain in the while loop of bar-simpliﬁcation . The steps applied, from left to right, are: (4), (3), (4), (6).*

![Figure 15 If P 1 is weakly simple, we can change the linear order of the edges as shown.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-15-p011.png)

*Figure 15 If P 1 is weakly simple, we can change the linear order of the edges as shown.: Figure 15 If P 1 is weakly simple, we can change the linear order of the edges as shown.*

- Figure 15 If \(P_{1}\) is weakly simple, we can change the linear order of the edges as shown.

Therefore we can "shorten" the lengths of paths in \(L_{v}^{T R}\) to create a simple polygon \(Q^{\prime} \in \Phi\left(P^{\prime}\right)\), hence \(P^{\prime}\) is weakly

### 4.4 Bar simplification algorithm

In this section, we show that the three operations (pin-extraction, V-shortcut, and L-shortcut) can successively remove all spurs of the polygon \(P\) from a bar \(b\).

```text
Algorithm bar-simplification ( P, b ).
```

While \(P\) has an edge along \(b\), perform one operation as follows.

- (i) If P in = ∅ , pick an arbitrary pin [v, u, v] and perform pin-extraction (u, v).

- (ii) Else if V negationslash = ∅ , then let [\(v_{1}\), u, \(v_{2}\)] ∈ V be a path where | x (\(v_{1}\)) -x (\(v_{2}\)) | is minimal, and perform V-shortcut (\(v_{1}\), u, \(v_{2}\)).

- (iii) Else if there exists v ∈ ∂D b such that ̂ L v TR = ∅ , do:

- (a) Let v be the rightmost node where L TR v = ∅ .

- (b) If L TL v ′ = ∅ for all v ′ ∈ ∂D b, x (v) < x (v ′ ) and x (u ′ 1) < x (u max), where u ′ 1 is the unique neighbor of v ′ on b, do L-shortcut (v, T R).

- (c) Else let v ′ be the leftmost node such that x (v) < x (v ′ ) and L TL v ′ = ∅ . If L TL v ′ satisfies (B3) do L-shortcut (v ′ , T L), otherwise halt and report that P is not weakly simple.

- (iv) Else if there exists v ∈ ∂D b such that L TL v = ∅ , repeat steps (iiia-c) with left-right and TR-TL interchanged. (Note the use of L v instead of ̂ L v. The same applies to (vi)).

- (v) Else if there exists v ∈ ∂D b such that ̂ L v BL = ∅ , repeat steps (iiia-c) using BL and BR in place of TR and TL, respectively, and left-right interchanged.

- (vi) Else if there exist v ∈ ∂D b such that L BR v = ∅ , repeat steps (iiia-c) using BR and BL in place of TR and TL respectively.

After the loop ends, perform old-bar-expansion (cf. Section 3.3) in the ellipse D b ; Return \(P(endofalgorithm)\).

Informally, bar-simplification "unwinds" each polygonal chain in the bar, while extracting pins and V-chains as they appear, by alternating between steps (3) to (6) (see Fig. 16). Step (3) uses \({\widehat{L_{v}}}^{T R}\) (instead of \(L_{v}{ }^{T R}\) ) to avoid an infinite loop.

- Lemma 4. The operations performed by bar-simplification \((P, b)\) are ws-equivalent, and maintain properties (A1)-(A3) and (I1)-(I5) inside \(D_{b}\). The algorithm either removes all nodes from the ellipse \(D_{b}\), or reports that \(P\) is not weakly simple. The \(L\)-shortcut operations performed by the algorithm create at most two crimps in each cross-chain in \(\mathcal{P}\).

Proof. We show that the algorithm only uses operations that satisfy their preconditions, and reports that \(P\) is not weakly simple only when \(P\) contains a forbidden configuration.

Since every pin can be extracted from a polygon satisfying (I1)-(I5), we may assume that \(\mathcal{P}\) in \(=\emptyset\). Suppose that \(\mathcal{V} \neq \emptyset\). Let \(\left[v_{1}, u, v_{2}\right] \in \mathcal{V}\) be a V-chain such that \(\left|x\left(v_{1}\right)-x\left(v_{2}\right)\right|\) is minimal. Since \(\mathcal{P} i_{n}=\emptyset\), the only obstacle for condition (B1) is an edge \([u, q]\) such that segment \(u_{q}\) is in the interior of the wedge \(\angle\left(v_{1}, u, v_{2}\right)\) (or else the image graph would have a crossing). This edge is part of a path \([p, u, q]\). Node \(q\) must be on \(\partial D_{b}\) between \(v_{1}\) and \(v_{2}\), otherwise paths \([p, u, q]\) and \(\left[v_{1}, u, v_{2}\right]\) cross. However, \(p \neq q\), otherwise \([p, u, q]\)

Step (3)-(4). By symmetry, we consider only step (3). We distinguish between two cases.

Since \(\mathcal{P} i_{n}=\emptyset\), condition (B1) is met. Suppose there is an edge \(\left[p, u_{1}\right]\) such that segment \(p u_{1}\) is in the interior of the wedge \(\angle\left(v, u_{1}, u_{\text {min }}\right)\). Clearly, \(p \in \partial D_{b}\) is a top node. Then edge \(\left[p, u_{1}\right]\) is part of a path \(\left[p, u_{1}, q\right]\). However, \(q\) must be in the closed wedge \(\angle\left(v, u_{1}, u_{\min }\right)\) otherwise there would be a node-crossing at \(u_{1}\). Also, \(q\) cannot be a top vertex on \(\partial D_{b}\) since \(\mathcal{P i_{n}}=\mathcal{V}=\emptyset\), and \(q\) cannot be on \(b\) by the choice of node \(v\). This confirms

- Case 2: the conditions of (2) are not satisfied. Let the path [v ′ , u ′ 1, u ′ min] ∈ L TL v ′ be selected in L-shortcut (v ′ , T L) by the algorithm. Condition (B2) is satisfied similar to Case 1. If (B3) fails, there is an edge [p, q] such that p ∈ ∂D b is a top vertex and q ∈ b, x (u ′ max) < x (q) < x (u max) (Recall that left and right are interchanged in L TL). Edge [p, q] is part of a path [p, q, r], where r ∈ b, similar to Case 1. This implies [p, q, r] ∈ L TR p ∪ L TL p. If x (v) < x (p) < x (v ′ ), then either L TR p = ∅ , which contradicts the choice of v, or L TL p = ∅ , which contradicts the choice of v ′ . Consequently, x (p) ≤ x (v). This implies x (u ′ max) < x (p) ≤ x (v), so the paths [v, \(u_{1}\), u max] and [v ′ , u ′ 1, u ′ max] cross. Therefore the algorithm correctly finds that P is not weakly simple.

- Steps (5)-(6). If steps (1)-(4) do not apply, then ̂ L v TR ∪ L TL v = ∅ . That is, for every path [v, \(u_{1}\), \(u_{2}\)] ∈ L TR, we have [\(u_{1}\), \(u_{2}\)] ∈ M cr. In particular, there are no top chains. The operations in (5)-(6) do not change these properties. Consequently, once steps (5)-(6) are executed for the first time, steps (3)-(4) are never executed again. By a symmetric argument steps (5)-(6) eliminate all paths in ̂ L v BL ∪ L BR v. If the while loop terminates, every edge in

\(b\) is also in \(M_{c_{r}}\) and \(L_{v}^{T L} \cup L_{v}^{B R}=\emptyset\). Consequently, by Lemma 2, \(b\) contains no spurs and

Termination. Each pin-extraction and V-shortcut operation reduces the number of vertices of \(P\) within \(D_{b}\). Operation L-shortcut \((v, X), X \in\{T R, T L, B R, B L\}\), either reduces the number of interior vertices, or produces a crimp if edge \(\left[u_{1}, u_{2}\right]\) is a longest edge of a cross chain. For termination, it is enough to show that, for each cross-chain \(c \in \mathcal{P}\), the algorithm introduces a crimp at most once in steps (3)-(4), and at most once in steps (5)-(6). W.l.o.g., consider step (3). We apply an L-shortcut in two possible cases. We show that it does not introduce crimps in Case 2. In step (3), we only perform L-shortcut \(\left(v^{\prime}, T L\right)\) if (B3) is satisfied and \(x\left(u_{1}^{\prime}\right)<x\left(u_{\text {max }}\right)\). So for all \(\left[v^{\prime}, u_{1}^{\prime}, u_{2}^{\prime}\right] \in L_{v^{\prime}}^{T L}\), we have \(x\left(u_{1}\right)<x\left(u_{2}^{\prime}\right)\). Suppose, for contradiction, that \(\left[u_{1}^{\prime}, u_{2}^{\prime}\right]\) is the only longest edge of some cross chain (and hence L-shortcut would introduce a crimp). Then, \(\left[u_{1}^{\prime}, u_{2}^{\prime}\right] \in M_{c_{r}}\) is inside \(\left[u_{1}, u_{\max }\right]\), contradicting (A3).

Consider Case 1. Notice that L-shortcut \((v, T R)\) is executed only if there exists a top node \(p\) with \(x(p)<x\left(u_{1}\right)\) such that \({\widehat{L_{p}}}^{T R} \neq \emptyset\). Suppose that L-shortcut \((v, T R)\) introduces a crimp in the path \(\left[v, u_{1}, u_{2}\right] \in L_{v}^{T R}\). This operation removes this subpath of a cross chain from \(L_{v}^{T R}\), but introduces \(\left[v^{*}, u_{2}, u_{1}\right]\) into \(L_{v^{*}}^{T L}\). By the time the algorithm executes L-shortcut \(\left(v^{*}, T L\right)\), we know that for every top vertex \(p\) with \(x(p)<x\left(u_{1}\right),{\widehat{L_{p}}}^{T R}=L_{p}^{T L}=\emptyset\). This implies-Lemma 5. algorithm bar-simplification \((P, b)\) takes \(O(m \log m)\) time, where \(m\) is the number of vertices in \(b\).

Proof. pin-extraction, V-shortcut, and L-shortcut each make \(O(1)\) changes in the image graph. pin-extraction and V-shortcut decrease the number of vertices inside D b. Each L-shortcut does as well, but they may jointly create 2 |P| = \(O(m)\) crimps, by Lemma 3. So the total number of operations is \(O(m)\). When [v, \(u_{1}\), \(u_{2}\)] ∈ L TR v and \(u_{2}\) = u min, L-shortcut replaces [v, \(u_{1}\), \(u_{2}\)] by [v ∗ , u min, \(u_{2}\)]: [\(u_{1}\)] shifts to [\(u_{2}\)], but no vertex is eliminated. In the worst case, one L-shortcut modifies Θ(m) paths, so in Θ(m) operations the total number of vertex shifts is Θ(\(m_{2}\)). Our implementation does not maintain the paths in P explicitly. Instead, we use set operations. We maintain the sets P in, V, and L \(X^{v}\), with v ∈ ∂D b and X ∈ { TR,TL,BR,BL, in sorted lists. The pins [v, u, v] ∈ P in are sorted by x (v); the wedges [\(v_{1}\), u, \(v_{2}\)] ∈ V are sorted by | x (\(v_{1}\)) -x (\(v_{2}\)) | . In every set L \(X^{v}\), the first two nodes in the paths [v, \(u_{1}\), \(u_{2}\)] ∈ L \(X^{v}\) are the same by (I3), and so it is enough to store vertex [\(u_{2}\)]; these vertices are stored in a list sorted by x (\(u_{2}\)). We also maintain binary variables to indicate for each path [v, \(u_{1}\), \(u_{2}\)] ∈ L \(X^{v}\) whether it is part of a cross chain, and whether [\(u_{1}\), \(u_{2}\)] is the only longest edge of that chain.

Steps (1)-(2) remove pins and V-chains, taking linear time in the number of removed vertices, without introducing any path in any set. Consider L-shortcut \((v, T R)\), executed in one of steps (3)-(4) which can be generalized to other occurrences of the L-shortcut operation. The elements \(\left[v, u_{1}, u_{\text {min }}\right] \in L_{v}^{T R}\) are simplified to \(\left[v^{*}, u_{\text {min }}\right]\). For each of these paths, say that the next edge along \(P\) is \(\left[u_{\min }, u_{3}\right]\). Then, the paths \(\left[v^{*}, u_{\min }, u_{3}\right]\) are inserted into either \(\mathcal{P} i n \cup \mathcal{V}\) if \(u_{3} \in \partial D_{b}\) is a top vertex, or \(L_{v^{*}}^{T L}\) if \(u_{3} \in b\). We can find each chain \(\left[v, u_{1}, u_{\min }\right] \in L_{v}^{T R}\) in \(O(1)\) time since \(L_{v}^{T R}\) is sorted by \(x\left(u_{2}\right)\). Finally, all other paths \(\left[v, u_{1}, u_{2}\right] \in L_{v}^{T R}\), where \(u_{2} \neq u_{\text {min }}\), become \(\left[v^{*}, u_{\text {min }}, u_{2}\right]\) and they form the new set \(L_{v^{*}}^{T R}\).

This representation allows the manipulation of \(O(m)\) vertices with one set operation. The number of insert and delete operations in the sorted lists is proportional to the number of vertices that are removed from the interior of \(D_{b}\), which is \(O(m)\). Each insertion and deletion takes \(O(\log m)\) time, and the overall time complexity is \(O(m \log m)\).

## 5 Spur-elimination

When there are no forks in the polygon, we can decide weak simplicity using [4][Theorem 5.1], but a naïve implementation runs in \(O\left(n^{2} \log n\right)\) time: successive applications of spur-reduction would perform an operation at each dummy vertex. Here, we show how to eliminate spurs in \(O(n \log n)\) time. After the bar simplification phase, each vertex of \(P\) belongs to a cluster.

Formation of Groups. Recall that by (I1) each cluster induces a tree. We first modify the image graph, transforming each tree into a binary tree by adding children to nodes with degree higher than 3. This does not affect the benchmark representation and is ws-equivalent (it can be reversed by node-split s and merge s). By construction, if a segment uv connects nodes in different clusters, both u and v are leaves or both are root nodes. We define a group G uv as the set of two clusters \(C(u)\) and \(C(v)\) if their roots are connected by the segment uv.

Recall that we only store benchmark vertices in each cluster. We denote by \(\left[u_{1} ; \ldots ; u_{k}\right]\) (using semicolons) a path inside a group defined by the benchmark vertices \(u_{1}, \ldots, u_{k}\). Let \(\mathcal{B}\) be the set of paths between two consecutive benchmark vertices in \(G_{u_{v}}\). By invariants (I1), (I2) and (I4), every path in \(\mathcal{B}\) has one endpoint in \(T[u]\) and one in \(T[v]\) and every spur in \(G_{u_{v}}\) is incident to two paths in \(\mathcal{B}\).

Overview. Assume that G is a partition of the nodes of the image graph into groups satisfying (I1)-(I5). We consider one group at a time, and eliminate all spurs from one cluster of that group. When we process one group, we may split it into two groups, create a new group, or create a new spur in an adjacent group (similar to pin-extraction in Section 4). The latter operation implies that we may need to process a group several times. Termination is established by showing that each operation reduces the total number of benchmark vertices.

```text
Algorithm spur-elimination ( P, G ).
```

While P contains a spur, do:

- Choose a group G uv ∈ G that contains a spur, w.l.o.g. contained in T [u].

- While T [u] contains an interior node, do:

- If u contains no spurs and is incident to only two edges uv and uw, eliminate u with a merge operation. The node w is the new root of the tree.

- If u contains spurs, eliminate them as described below.

- If u contains no spurs, split G uv into two groups along a chain of segments starting with uv as described below. Rename a largest resulting group to G uv.

The detailed description of steps 2b and 2c, as well as the analysis of the algorithm and the supporting data structures are in the full paper [1]. Here we give a brief summary. Step 2b first replaces every path of the form \(\left[t_{1} ; u ; t_{2}\right]\) by a path \(\left[t_{1} ; t_{2}\right]\) (Fig. 17(a)-(b)). The resulting new path \(\left[t_{1} ; t_{2}\right]\) passes through the lowest common ancestor of \(t_{1}\) and \(t_{2}\), denoted \(\operatorname{lca}\left(t_{1}, t_{2}\right)\). Notice that \(t_{1}\) and \(t_{2}\) belong to \(T[v]\), therefore \(\left[t_{1} ; t_{2}\right]\) does not satisfy (I2). We complete Step 2b by a sequence of "repair" operations that restore (I2). One is analogous to pin-extraction, moving a spur from a leaf of \(T[v]\) into an adjacent group (Fig. 17(b)-(c)). The other is analogous to V-shortcut: it creates a new group for each node \(\ell\) where \(\ell=\operatorname{lca}\left(t_{1}, t_{2}\right)\) for some path \(\left[t_{1} ; t_{2}\right]\) that violates (I2). The set of all \(\left[t_{1} ; t_{2}\right]\) for which \(\operatorname{lca}\left(t_{1}, t_{2}\right)=\ell\) induces

![Figure 17 (a) u contains spurs. (b) After eliminating spurs, T [ v ] does not satisfy (I2). (c) The analogues of pin-extraction and V-shortcut . Leaf nodes are shown black.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-17-p015.png)

*Figure 17 (a) u contains spurs. (b) After eliminating spurs, T [ v ] does not satisfy (I2). (c) The analogues of pin-extraction and V-shortcut . Leaf nodes are shown black.: Figure 17 (a) u contains spurs. (b) After eliminating spurs, T [v] does not satisfy (I2). (c) The analogues of pin-extraction and V-shortcut. Leaf nodes are shown black.*

![Figure 18 Splitting group G uv . (a) Changes in the image graph. (b) Changes in the polygon.](/Users/evanthayer/Projects/stepview/docs/2016_recognizing_weakly_simple_polygons/figures/figure-18-p015.png)

*Figure 18 Splitting group G uv . (a) Changes in the image graph. (b) Changes in the polygon.: Figure 18 Splitting group G uv. (a) Changes in the image graph. (b) Changes in the polygon.*

a tree \(T[\ell]\), in which \(t_{1}\) and \(t_{2}\) are in the left and right subtree of \(\ell\), respectively. We then remove all such paths from \(T[v]\) and create a new group that satisfies (I1)-(I5).

Step 2c splits \(G_{u_{v}}\) into two groups along a chain of segments \(C_{0}\) (Fig. 18(a)-(b)). The tree \(T[u]\) naturally splits into the left and right subtrees, \(T\left[u^{-}\right]\)and \(T\left[u^{+}\right]\), but splitting \(T[v]\) is a nontrivial task. \(\mathcal{B}\) is partitioned into \(\mathcal{B}^{-}\)and \(\mathcal{B}^{+}\), paths with one endpoint in \(T\left[u^{-}\right]\) and \(T\left[u^{+}\right]\), respectively. \(C_{0}\) represents the shared boundary between \(\mathcal{B}^{-}\)and \(\mathcal{B}^{+}\)and can be found in \(O(\log |\mathcal{B}|)\) time. W.l.o.g., \(\left|\mathcal{B}^{-}\right|<\left|\mathcal{B}^{+}\right|\). We build a tree \(T\left[v^{-}\right]\)induced by \(\mathcal{B}^{-}\)and adjust \(T[v]\) so that it is induced by \(\mathcal{B}^{+}\). This is accomplished in \(O\left(\left|\mathcal{B}^{-}\right|\right)\)time by deleting from \(T[v]\) nodes unique to \(T\left[v^{-}\right]\). The spurs connected to one path in \(\mathcal{B}^{-}\)and one in \(\mathcal{B}^{+}\) are replaced by a pair of benchmarks on the boundary of the two groups. By a heavy path decomposition argument, the overall time spent in this step is \(O(n \log n)\).

## 6 Conclusion

We presented an \(O(n \log n)\)-time algorithm for deciding whether a polygon with \(n\) vertices is weakly simple. The problem has a natural generalization for planar graphs [4]. It is an open problem to decide efficiently whether a drawing of a graph \(H\) is weakly simple, i.e., whether a drawing \(P\) of \(H\) is within \(\varepsilon\) Fréchet distance from an embedding \(Q\) of \(H\), for all \(\varepsilon>0\).

We can also generalize the problem to higher dimensions. A polyhedron can be described as a map \(\gamma: \mathbb{S}^{2} \rightarrow \mathbb{R}^{3}\). A simple polyhedron is an injective function. A polyhedron \(P\) is weakly simple if there exists a simple polyhedron within \(\varepsilon\) Fréchet distance from \(P\) for all \(\varepsilon>0\). This problem can be reduced to origami flat foldability. The results of [3] imply that, given a convex polygon \(P\) and a piecewise isometric function \(f: P \rightarrow \mathbb{R}^{2}\) (called crease pattern), it is NP-hard to decide if there exists an injective embedding of \(P\) in three dimensions \(\lambda: P \rightarrow \mathbb{R}^{3}\) within \(\varepsilon\) Fréchet distance from \(f\) for all \(\varepsilon>0\), i.e., if \(f\) is flat foldable. Given \(P\) and \(f\), we can construct a continuous function \(g: \mathbb{S}^{2} \rightarrow P\) mapping each hemisphere of \(\mathbb{S}^{2}\) to \(P\left(g^{-1}(x)\right.\), for a point \(x \in P\), maps to two points in different hemispheres of \(\mathbb{S}^{2}\) ). Then, the polyhedron \(\gamma=g \circ f\) is weakly simple if and only if \(f\) is flat foldable. Therefore, it is also NP-hard to decide whether a polyhedron is weakly simple.

## References

- 1 Hugo A. Akitaya, Greg Aloupis, Jeff Erickson, and Csaba D. Tóth. Recognizing weakly simple polygons. Preprint, 2016. arXiv:1603.07401. 2 Esther M. Arkin, Michael A. Bender, Erik D. Demaine, Martin L. Demaine, Joseph S.B. Mitchell, Saurabh Sethia, and Steven S. Skiena. When can you fold a map? computational Geometry, 29(1):23-46, 2004. 3 Marshall Bern and Barry Hayes. The complexity of flat origami. In Proc. 7th ACM-SIAM Sympos. on Discrete algorithms, pages 175-183, 1996. 4 Hsien-Chih Chang, Jeff Erickson, and Chao Xu. Detecting weakly simple polygons. In Proc. 26th ACM-SIAM Sympos. on Discrete algorithms, pages 1655-1670, 2015. 5 Bernard Chazelle. Triangulating a simple polygon in linear time. Discrete Comput. Geom., 6(3):485-524, 1991. 6 Pier Francesco Cortese, Giuseppe Di Battista, Maurizio Patrignani, and Maurizio Pizzonia. On embedding a cycle in a plane graph. Discrete Math., 309(7):1856-1869, 2009. 7 Ares Ribó Mor. Realization and counting problems for planar structures. PhD thesis, Freie Universität Berlin, Department of Mathematics and Computer Science, 2006. 8 Michael Ian Shamos and Dan Hoey. Geometric intersection problems. In Proc. 17th IEEE Sympos. Foundations of Computer Science, pages 208-215, 1976.
