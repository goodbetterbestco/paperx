# Detecting Weakly Simple Polygons

Hsien-Chih Chang, Jeff Erickson, Chao Xu, Submitted to SODA - July

Department of Computer Science University of Illinois, Urbana-Champaign

## Abstract

A closed curve in the plane is weakly simple if it is the limit (in the Fréchet metric) of a sequence of simple closed curves. We describe an algorithm to determine whether a closed walk of length \(n\) in a simple plane graph is weakly simple in \(O(n \log n)\) time, improving an earlier \(O\left(n^{3}\right)\)-time algorithm of Cortese et al. [Discrete Math. 2009]. As an immediate corollary, we obtain the first efficient algorithm to determine whether an arbitrary \(n\)-vertex polygon is weakly simple; our algorithm runs in \(O\left(n^{2} \log n\right)\) time. We also describe algorithms that detect weak simplicity in \(O(n \log n)\) time for two interesting classes of polygons. Finally, we discuss subtle errors in several previously published definitions of weak simplicity. 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44

## 1 Introduction

Simple polygons in the plane have been standard objects of study in computational geometry for decades, and in the broader mathematical community for centuries. Many algorithms designed for simple polygons continue to work with little or no modification in degenerate cases, where intuitively the polygon overlaps itself but does not cross itself. We offer the first complete and efficient algorithm to detect such degenerate polygons.

Unfortunately, neither of these definitions imply efficient algorithms to determine whether a given polygon is weakly simple. Several authors have offered alternative characterizations of weakly simple polygons, all building on the intuition that that a weakly simple polygon does not 'cross itself'. Unfortunately, none of these characterizations is entirely consistent with the formal definition, especially when the algorithm contains spurs-vertices whose two incident edges overlap. We discuss these earlier definitions in detail in Section 2.5 and Appendix A.

![Figure 1.1. Top row](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-1-1-p002.png)

*Figure 1.1. Top row: Two weakly simple polygons from Meister’s seminal 1770 treatise on polygons [36]. Bottom row: The polygon (a, x, b, x, c, x) is weakly simple; the polygon (a, x, b, x, c, x, a, x, b, x, c, x) is not.*

We describe an algorithm to determine whether a closed walk of length \(n\) in a planar straight-line graph is weakly simple in \(O(n \log n)\) time. Our algorithm is essentially a more efficient implementation of an earlier \(O\left(n^{3}\right)\)-time algorithm of Cortese et al. [17] for the same problem. Since any \(n\)-vertex polygon can be decomposed into a walk of length \(O\left(n^{2}\right)\) in union of the polygon's vertices and edges, we immediately obtain an algorithm to decide whether a polygon is weakly simple in \(O\left(n^{2} \log n\right)\) time. The quadratic blowup is caused by forks in the polygon: vertices that lie in the interior of many overlapping collinear edges. For polygons without forks, the running time is simply \(O(n \log n)\). We also describe a simpler \(O(n \log n)\)-time algorithm for polygons without spurs (but possibly with forks).

Our paper is organized as follows. We review standard terminology, formally define weak simplicity, and discuss connections to other published definitions in Section 2. In Section 3, as a warm-up to our later results, we describe a simple algorithm to determine whether a polygon without spurs or forks is weakly simple in \(O(n \log n)\) time. Section 4 describes our \(O(n \log n)\)-time algorithm for polygons without spurs, but possibly with forks. We give a complete description of the algorithm of Cortese et al. for closed walks in planar graphs, reformulated using our terminology, in Section 5 and then describe and analyze our faster implementation in Section 6. Due to space constraints, many details and proofs are deferred to the appendix. In particular, we relate weak simplicity to related notions of compound planarity and self-touching linkage configurations in Appendix B; we provide implementation details and proofs of correctness for an important expansion operation in Appendix C; and we describe several extensions and open problems in Appendix D.

$$
d_{\mathcal{F}}(P, Q):=\inf _{\rho: S^{1} \rightarrow S^{1}} \max _{t \in S^{1}} d(P(\rho(t)), Q(t))
$$

$$
d_{V}(P, Q):=\min _{s} \max _{i} d\left(p_{i}, q_{i+s \bmod n}\right)
$$

## 2 Background

### 2.1 Curves and Polygons

A path in the plane is a continuous function \(P:[0,1] \rightarrow \mathbb{R}^{2}\). A closed curve in the plane is a continuous function \(P: S^{1} \rightarrow \mathbb{R}^{2}\). A path or closed curve is simple if it is injective. A polygon is a piecewise-linear closed curve; every polygon is defined by a cyclic sequence of points, called vertices, connected by line segments, called edges. We often describe polygons by listing their vertices in parentheses; for example, \(\left(\boldsymbol{p}_{\mathbf{0}}, \boldsymbol{p}_{\mathbf{1}}, \ldots, \boldsymbol{p}_{\boldsymbol{n}-\mathbf{1}}\right)\) denotes the polygon with vertices \(p_{i}\) and edges \(p_{i} p_{i+1 \bmod n}\) for every index \(i\). A polygon is simple if and only if its vertices are distinct and its edges intersect only at common endpoints. We emphasize that the vertices of a non-simple polygon need not be distinct, and two edges of a non-simple polygon may overlap or even coincide [26,36]. However, we do assume without (significant) loss of generality that every edge of a polygon has positive length.

Similarly, a polygonal chain is a piecewise-linear path, which consists of a linear sequence of points (vertices) connected by line segments (edges). We often describe polygonal paths by listing their vertices in square brackets, like \(\left[\boldsymbol{p}_{\mathbf{0}}, \boldsymbol{p}_{\mathbf{1}}, \ldots, \boldsymbol{p}_{\boldsymbol{n}-\mathbf{1}}\right]\), to distinguish them from polygons. A corner of a polygon or polygonal chain \(P\) is a subpath [ \(p_{i-1}, p_{i}, p_{i+1}\) ] consisting of two consecutive edges of \(P\). Three local features of polygons play important roles in our results. A spur of a polygon \(P\) is a vertex of \(P\) whose two incident edges overlap. A fork of a polygon \(P\) is a vertex of \(P\) that lies in the interior of an edge of \(P\). Finally, a simple crossing between two paths is a point of transverse intersection; if the paths are polygonal chains, this intersection point could be a vertex of one or both paths.

### 2.2 Distances

Let \(\boldsymbol{d}(\boldsymbol{p}, \boldsymbol{q})\) denote the Euclidean distance between two points \(p\) and \(q\) in the plane. The Fréchet distance \(\boldsymbol{d}_{\mathcal{F}}(P, Q)\) between two closed curves \(P\) and \(Q\) is defined as where the infimum is taken over all orientation-preserving homeomorphisms of \(S^{1}\). The function \(\rho\) is often called a reparametrization of \(S^{1}\). Fréchet distance is a complete metric over the space of all (unparametrized) closed curves in the plane. The Fréchet distance between paths is defined similarly. For any two polygons \(P=\left(p_{0}, p_{1}, \ldots, p_{n-1}\right)\) and \(Q=\left(q_{0}, q_{1}, \ldots, q_{n-1}\right)\) with the same number of vertices, the vertex distance between \(P\) and \(Q\) is defined as

For each integer \(n\), vertex distance is a complete metric over the space of all \(n\)-vertex polygons (where two polygons that differ only by a cyclic shift of indices are identified).

### 2.3 Planar Graphs

A planar embedding of a graph represents the vertices by distinct points in the plane, and the edges by interior-disjoint simple paths between their endpoints. A planar straight-line graph is a planar graph embedding in which every edge is represented by a single line segment. We refer to the vertices of a planar straight-line graph as nodes and the edges as segments, to distinguish them from the vertices and edges of polygons. Any planar graph embedding partitions the plane into several regions, call the faces of the embedding. Euler's formula states that any planar embedding of a connected graph with \(V\) vertices and \(E\) edges has exactly \(2-V+E\) faces. Any planar graph embedding can be represented abstractly by a rotation system, which records for each node the cyclic sequence of incident segments [37] . planar straight-line graphs can be represented by several data structures, each of which allows fast access to the abstract graph, the coordinates of its nodes, and the rotation system; one popular example is the doubly-connected edge list [5] .

### 2.4 Weak Simplicity

Intuitively, a closed curve or polygon is weakly simple if it can be made simple by an arbitrarily small perturbation, or equivalently, if it is the limit of a sequence of simple closed curves or polygons. Our two different metrics for curve similarity give us two different formal definitions:

- A closed curve P is weakly simple if, for any " > 0, there is a simple closed curve Q such that d \(F(P,Q)\) < " . In other words, a closed curve is weakly simple if it can be made simple by an arbitrarily small perturbation of the entire curve.

- A polygon P is rigidly weakly simple if, for any " > 0, there is a simple polygon Q with the same number of vertices such that dV (P, Q) <" . In other words, a polygon is rigidly weakly simple if it can be made simple by an arbitrarily small perturbation of its vertices.

For any two polygons \(P\) and \(Q\) with the same number of vertices, we have \(d_{\mathcal{F}}(P, Q) \leq d_{V}(P, Q)\); thus, every rigidly weakly simple polygon is also weakly simple. The following theorem, whose proof we defer to Appendix B, implies that the two definitions are almost equivalent for polygons.

Theorem 2.1. Every weakly simple polygon with more than two vertices is rigidly weakly simple.

Our proof relies on a nontrivial result of Ribó Mor [39, Theorem 3.1] (previously conjectured by Connelly et al. [16, Conjecture 4.1] ) about 'self-touching' linkage configurations. The restriction to polygons with more than two vertices is necessary; every polygon with at most two vertices is weakly simple, because it is a degenerate ellipse, but not rigidly weakly simple, because every simple polygon has at least three vertices.

### 2.5 Earlier Definitions of Weak Simplicity

Several authors have offered combinatorial definitions of weakly simple polygons based on the intuitive notation that a weakly simple polygon cannot cross itself; however, every such definition we have found in the literature is either imprecise, incomplete, or incorrect. For example, a common definition of 'weakly simple', originally due to Toussaint [10, 44, 47, 48] , requires that the rotation number (the sum of signed external angles divided by 2) is either + 1 or 1; however, rotation numbers are not well-defined for polygons with spurs. Every combinatorial definition of '(self-)crossing' we have found in the literature [10,19,22,34,44,47,50] is incorrect for polygons with spurs; many of these definitions are incorrect even for polygons without spurs. Figure 2.1 shows a spur-free polygon with 14 vertices that is not weakly simple but satisfies several published definitions of weak simplicity, including Toussaint's. We offer further details, examples, and discussion in Appendix A.

![Figure 2.1. A polygon that many published deﬁnitions incorrectly classify as weakly simple.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-2-1-p004.png)

*Figure 2.1. A polygon that many published deﬁnitions incorrectly classify as weakly simple.: Figure 2.1. A polygon that many published deﬁnitions incorrectly classify as weakly simple. definitions incorrectly classify as weakly simple.*

We emphasize that the algorithms in all these papers appear to be correct. Given simple polygons as input, these algorithms construct weakly simple polygons as intermediate results, with additional structure that is consistent with the papers' definitions. More importantly, in each case, the perturbations required to make those polygons simple are implicit in their construction. Despite occasional claims to the contrary (based on overly restrictive definitions) [1] , we are unaware of any previous algorithm to determine whether a polygon is weakly simple.

## 3 No Spurs or Forks

In this section, we describe an algorithm to determine whether a polygon without spurs or forks is weakly simple in \(O(n \log n)\) time. Although we have not seen a complete description of this algorithm in the literature, it is essentially folklore. Similar techniques were previously used by Reinhart [38], Zieschang [51], and Chillingworth [14] to determine whether a given closed curve in an arbitrary 2-manifold with boundary is homotopic to a simple closed curve, and more recently by Cortese et al. [17] to determine clustered planarity of closed walks in plane graphs.

Let \(P=\left(p_{0}, \ldots, p_{n-1}\right)\) be an arbitrary polygon without spurs or forks. The algorithm consists of three phases. first, we construct the image of \(P\), to identify all coincident vertices and edges, and to rule out simple crossings between edges of \(P\). Second, we look for simple crossings at the vertices of \(P\). Finally, if there are no simple crossings, we expand \(P\) into a nearby 2-regular plane graph in the only way possible, and then check whether the expansion is consistent with \(P\).

The description and analysis of our algorithm use the following multiplicity functions: \(\boldsymbol{n}(\boldsymbol{u})\) denotes the number of times the point \(u\) occurs as a vertex of \(P ; \boldsymbol{n}(\boldsymbol{u} \boldsymbol{v})\) denotes the number of times the line segment \(u_{v}\) occurs (in either orientation) as an edge of \(P\); and \(\boldsymbol{n}(\boldsymbol{u} \boldsymbol{v} \boldsymbol{w})\) denote the number of times the corner \([u, v, w]\) or its reversal \([w, v, u]\) occurs in \(P\).

### 3.1 Constructing the Image Graph

In the first phase, we determine in \(O(n \log n)\) time whether any two edges of \(P\) cross, using the classical sweep-line algorithm of Shamos and Hoey [43]; if so, we immediately halt and report that \(P\) is not weakly simple. Otherwise, the image of \(P\) is a planar straight-line graph \(G\), whose vertices we call nodes and whose edges we call segments, to distinguish them from the vertices and edges of \(P\). Specifically, the nodes of \(G\) are obtained from the vertices of \(P\) by removing duplicates, and the segments of \(G\) are obtained from the edges of \(P\) by removing duplicates. The image graph \(G\) can be constructed in \(O(n \log n)\) time using, for example, a straightforward modification of Shamos and Hoey's sweep-line algorithm. This is the most time-consuming portion of our algorithm; the other two phases require only \(O(n)\) time. \({ }^{1}\)

### 3.2 Node Expansion

Let \(u\) be an arbitrary node in \(G\). Consider a disk \(D_{u}\) of radius \(\delta\) centered at \(u\), with \(\delta\) chosen sufficiently small that \(D_{u}\) intersects only the segments of \(G\) incident to \(u\). Because edges of \(G\) are straight line segments, the circle \(\partial D_{u}\) intersects each edge at most once. On each segment \(u_{x}\) incident to \(u\), we introduce a new node \([u_{x}]\) at the intersection point \(u x \cap \partial D_{u}\). Then we modify \(P\) by replacing each maximal subwalk in \(D_{u}\) with a straight line segment.

![Figure 3.1. Node expansion. Compare with Figure C.1 .](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-3-1-p005.png)

*Figure 3.1. Node expansion. Compare with Figure C.1 .: Figure 3.1. Node expansion. Compare with Figure C.1.*

We conjecture that the image graph of a weakly simple polygon can actually be constructed in \(O(nlogn)\) or even \(O(n)\) time, by a suitable modification of algorithms for triangulating simple polygons [2,13,15,20,42] .

Thus, if \(P\) contains the subpath \([x, u, y]\), the modified polygon contain the edge \([u_{x}][u_{y}]\). Let \(\tilde{P}\) denote the modified polygon, and let \(\tilde{G}\) denote the image of \(\tilde{P}\) in the plane; see the top row of Figure 3.1. Lemmas C. 1 and C. 2 (in the appendix) imply that the original polygon \(P\) is weakly simple if and only if the expanded polygon \(\tilde{P}\) is weakly simple. If \(P\) has a simple crossing at \(u\), then some pair of edges of \(\tilde{P}\) cross inside \(D_{u}\). We describe how to check for such crossings in Section C.2. expand every node of \(G\) in \(O(n)\) time overall. If any node expansion creates a simple crossing, we halt immediately and report that \(P\) is not weakly simple. Otherwise, let \(\tilde{P}\) denote the polygon after all node expansions, and let \(\tilde{G}\) denote its image graph. By induction, \(\tilde{G}\) is a plane graph, and \(P\) is weakly simple if and only if \(\tilde{P}\) is weakly simple.

### 3.3 Global Inflation

In the final phase of the algorithm, we "inflate" the image graph \(\tilde{G}\) into a 2-regular plane graph \(\tilde{Q}\) by replacing each segment \(s\) of \(\tilde{G}\) with several parallel segments, one for each edge of \(\tilde{P}\) that traverses \(s\); see the right column of Figure 3.1. Then \(\tilde{P}\) (and therefore \(P\) ) is weakly simple if and only if \(\tilde{Q}\) is connected and consistent with \(\tilde{P}\). Fix an arbitrarily small positive real number \(\varepsilon \ll \delta\). To construct \(\tilde{Q}\) from \(\tilde{G}\), we replace each node \([u_{v}]\) with \(n(u_{v})\) closely spaced points on \(\partial D_{u}\), all within \(\varepsilon\) of \([u_{v}]\). Then we replace each segment \([u_{v}][v_{u}]\) of \(\tilde{G}\) outside the disks with \(n(u_{v})\) parallel segments. Finally, within each disk \(D_{u}\), we replace each corner segment [uv][uw] with \(n(u v_{w})\) parallel segments, so that all resulting segments in \(D_{u}\) are disjoint. Crucially, there is exactly one way to perform this final replacement within each disk \(D_{u}\) once the boundary points are fixed; see [6,11,12] for related constructions. The uniqueness of \(\tilde{Q}\) implies \(\tilde{P}\) is weakly simple if and only if (1) the resulting 2-regular graph \(\tilde{Q}\) is connected and thus a simple polygon, and (2) we have \(d_{V}(\tilde{P}, \tilde{Q})<\varepsilon\). We can check whether \(\tilde{Q}\) is connected in \(O(n)\) time by depth-first search. Finally, if \(\tilde{Q}\) is a simple polygon, we can determine whether \(d_{V}(\tilde{P}, \tilde{Q})<\varepsilon\) in \(O(n)\) time using any fast string-matching algorithm.

One final detail remains to complete the proof of Theorem 3.1: How do we choose appropriate parameters \(\delta\) and \(\varepsilon\) in the second and third phases? In fact, there is no need to choose specific values at all! The combinatorial embedding of the expanded image graph \(\tilde{G}\) is identical for all sufficiently small positive \(\delta\); similarly, the combinatorial embedding of the 2-regular graph \(\tilde{Q}\) is identical for all sufficiently small positive \(\varepsilon \ll \delta\). Thus, the entire algorithm can be performed by modifying abstract graphs and their rotation systems, without choosing explicit values of \(\delta\) or \(\varepsilon\) at all! See Section C. 2 for details.

Theorem 3.1. Given an arbitrary n-vertex polygon \(P\) without spurs or forks, we can determine in \(O(n \log n)\) time whether \(P\) is weakly simple.

## 4 Forks But No Spurs

Recall that a fork in a polygon is a vertex that lies in the interior of an edge. With only minor modifications, the algorithm in the previous section can also be applied to polygons with forks, but still without spurs. Specifically, in the preprocessing phase, we locate all forks in \(O((n+k) \log n)\) time using a standard sweep-line algorithm [4], where \(k=O\left(n^{2}\right)\) is the number of forks, and then subdivide each We define a coarser decomposition of the image of \(P\) into points and line segments called a bar decomposition, as follows. A bar of \(P\) is a component of the union of the interiors of all edges of \(P\) that lie on a common line. Every fork lies in exactly one bar; we call any vertex that is not in a bar sober.

We can compute the bar decomposition of \(P\) in \(O(n \log n)\) time as follows. first, cluster the edges of \(P\) into collinear subsets, by sorting them by the slopes and \(y\)-intercepts of their supporting lines. Then for each collinear subset, sort the endpoints by \(x\)-coordinate, breaking ties by sorting all right endpoints before all left endpoints. Finally, a linear-time scan along each sorted collinear subset of edges yields all bars that lie on that line. We also identify all distinct sober vertices, compute (the indices of) all vertices and edges of \(P\) that lie in each bar, and compute the bars incident to each fork in cyclic order. Finally, we verify that no pair of bars crosses, using a standard sweep-line algorithm [43]. Next we perform a node expansion at each sober node, as described in the previous section. We also perform a bar expansion around each bar, defined as follows. For any bar \(b\), let \(b^{\circ}\) denote the subset of \(b\) obtained by removing all points within distance \(2 \delta\) of endpoints of \(b\), and let \(D_{b}\) denote an elliptical disk whose major axis is \(b^{\circ}\) and whose minor axis has length \(2 \delta\), where the parameter \(\delta\) is chosen so that \(D_{b}\) intersects only the edges of \(P\) that also intersect the bar. Then bar expansion is identical to node expansion: we subdivide \(P\) at the intersection points \(\operatorname{im} P \cap \partial D_{b}\), replace each maximal subpath of \(P\) that lies in \(D_{b}\) with a line segment, and finally verify that the new segments do not cross, as described in Section C.2.

![Figure 4.1. A bar decomposition of a weakly simple polygon without spurs, and a nearby simple polygon.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-4-1-p007.png)

*Figure 4.1. A bar decomposition of a weakly simple polygon without spurs, and a nearby simple polygon.: Figure 4.1. A bar decomposition of a weakly simple polygon without spurs, and a nearby simple polygon.*

Since every edge of \(P\) touches at most three bars or sober nodes, we can expand every bar and every sober node in \(O(n)\) time. The resulting polygon \(\tilde{P}\) has no simple crossings, no forks, and no spurs. Lemmas C.1, C.2, and C.3 imply inductively that \(\tilde{P}\) is weakly simple if and only if the original polygon \(P\) is weakly simple. Finally, we can determine whether \(\tilde{P}\) is weakly simple in \(O(n)\) time using the global inflation algorithm described in Section 3.3. We conclude:

Theorem 4.1. Given an arbitrary n-vertex polygon \(P\) without spurs, but possibly with forks, we can determine in \(O(n \log n)\) time whether \(P\) is weakly simple.

## 5 Polygons with Spurs

Neither of the previous algorithms is correct when the input polygon has spurs. To handle these polygons, we apply a recent algorithm of Cortese et al. [17] to determine whether a walk in a plane graph is weakly simple (in their terminology, whether a rigid clustered cycle is c-planar). We include a complete description of the algorithm here, reformulated in our terminology, not only to keep this paper self-contained, but also so that we can improve its running time in Section 6.

At a high level, the algorithm proceeds as follows. In an initial preprocessing phase, we construct the image graph \(G\) of the input polygon \(P\) and then expand \(P\) at every node in \(G\). Then, following Cortese et al. [17], we repeatedly modify the polygon using an operation we call segment expansion, defined in Section 5.1, until either we detect a simple crossing (in which case \(P\) is not weakly simple), the image graph is reduced to a single line segment (in which case \(P\) is weakly simple), or there are no more "useful" segments to expand. If the input polygon has no forks, the image graph \(G\) has complexity \(O(n)\), we construct it in \(O(n \log n)\) time, and we expand every node in \(O(n)\) time, exactly as described in Section 3. A simple potential argument implies that the main loop terminates after at most \(O(n)\) segment expansions. (Cortese et al. [17] prove an upper bound of \(O\left(n^{2}\right)\) expansions using a different potential function.)

A naïve implementation executes each segment expansion in \(O(n)\) time, giving us an overall running time of \(O\left(n^{2}\right)\). The \(O(n \log n)\) time bound follows from a more careful implementation and analysis, which we describe in Section 6. Theorem 5.1.

Theorem 5.1. Given an arbitrary \(n\)-vertex polygon \(P\) without forks but possibly with spurs, we can

Thus, Theorem 5.1 has the following immediate corollary.

Corollary 5.2. Given an arbitrary n-vertex polygon P, we can determine in \(O(n2logn)\) time whether P is weakly simple.

For the remainder of the paper, we assume that the input polygon P has no forks.

### 5.1 Segment Expansion

We now describe the main loop of our algorithm in more detail. The main operation, segment expansion, is nearly identical to our earlier expansion operations. Let \(s\) be an arbitrary segment of the current image graph \(G\). Let \(D_{s}\) be an elliptical disk whose boundary intersects precisely the segments that share one endpoint with \(s\). To expand segment \(s\), we subdivide \(P\) at its intersection with \(\partial D_{s}\), replace each maximal subpath of \(P\) that lies in \(D_{s}\) with a line segment, and verify that the new segments do not cross. Unfortunately, expanding an arbitrary segment could change a polygon that is not weakly simple into a polygon that is weakly simple. Our algorithm expands only segments with the following property. A segment \(u_{v}\) in the image graph is a base of one of its endpoints \(u\) if every occurrence of \(u\) in the polygon \(P\) is immediately preceded or followed by the other endpoint \(v\). A segment is safe if it is a base of both of its endpoints. Cortese et al. prove that a polygon \(P\) is weakly simple if and only if the polygon \(\tilde{P}\) that results from expanding a safe segment is also weakly simple [17, Lemma 3]. We provide a new proof of this key lemma in the appendix (Section C.5). After a node expansion around any node \(u\), each new node \([u_{x}]\) on the boundary of \(D_{u}\) has a base, namely the segment \([u_{x}] x\) [17, Property 5]. Thus, expanding every node in the original image graph guarantees that every node in the image graph has a base. Similarly, after any segment expansion, every newly created node has a base. Thus, our algorithm inductively maintains the invariant that every node in the image graph has a base. It follows that at every iteration of our algorithm, the image graph has at least one safe segment, so our algorithm never gets stuck.

### 5.2 Useful Segments

However, under some circumstances, expanding a safe segment does not actually make progress. Specifically, if both endpoints of the segment have degree 2 in \(G\), and no spur in \(P\) includes that segment, Specifically, if both endpoints of the segment have degree 2 in \(G\), and no spur in \(P\) includes that segment, the segment expansion does not change the combinatorial structure of \(P\) or \(G\) at all. We call any such segment useless. Equivalently, a safe edge is useful if it is the only base of one of its endpoints, and useless otherwise. Our algorithm repeatedly expands only useful segments until either the image graph consists of a single segment (in which case \(P\) is weakly simple) or there are no more useful segments to expand. Lemma 5.3. Let \(G\) be the image graph of a polygon \(P\) without simple crossings. If every node of \(G\) has a base but \(G\) has no useful segments, then \(G\) is a simple polygon and \(P\) has no spurs. Proof: Let \(H\) be the subgraph of all safe segments of \(G\). The degree of any node in \(H\) is at most the number of bases of that node in \(G\). Since no node in \(G\) can have more than two bases, \(H\) is the union of disjoint paths and cycles. If some component of \(H\) is a path, the first (or last) segment in that path is useful. Otherwise, every node in \(G\) has two bases, and therefore has degree 2; because \(G\) is a connected planar straight line graph, it must be a simple polygon. Moreover, because every node in \(G\) has two bases, \(P\) has no spurs.

Lemma 5.3 implies that when our main loop ends, we can invoke our algorithm for spur-free polygons in Section 3. But this is overkill. Because \(P\) has no spurs, \(P\) must traverse every segment of \(G\) the same number of times. It follows that the 2-regular plane graph \(\tilde{Q}\) constructed in the inflation phase of the algorithm in Section 3 will consist of \(n(u_{v})\) parallel copies of \(G\). Thus, when the main loop ends, \(P\) is weakly simple if and only if \(n(u_{v})=1\), for any single segment \(u_{v}\).

### 5.3 Termination and Analysis

Like Cortese et al., we prove that our algorithm halts using a potential argument. Let \(|P|\) and \(|G|\) respectively denote the number of vertices in polygon \(P\) and the number of nodes in its image graph \(G\); our potential function is \(\Phi(P, G):=|P|-|G|\). Clearly \(\Phi(P, G)\) is always non-negative. Our preprocessing phase at most doubles \(|P|\), so at the beginning of the main loop we have \(\Phi(P, G) \leq 2 n\). (Cortese et al. used the potential \(\sum_{e} n(e)^{2}=O\left(n^{2}\right)\), where the sum is over all segments of \(G\); otherwise, our analysis is nearly identical.) Lemma 5.4. Let \(P\) be any polygon whose image graph \(G\) has more than one segment, let \(\tilde{P}\) be the result of expanding a useful segment of \(G\), and let \(\tilde{G}\) be the image graph of \(\tilde{P}\). Then \(\Phi(\tilde{P}, \tilde{G})<\Phi(P, G)\).

Proof: Let \(u_{v}\) be a useful segment of \(G\), where without loss of generality we have \(\operatorname{deg}(u) \leq \operatorname{deg}(v)\). Because \(u_{v}\) is safe, every maximal subpath of \(P\) that lies in the ellipse \(D_{u_{v}}\) contains at least 2 vertices, so \(|\tilde{P}| \leq|P|\). We easily observe that \(|\tilde{G}|=|G|+\operatorname{deg}(u)+\operatorname{deg}(v)-4\), so if \(\operatorname{deg}(u)+\operatorname{deg}(v)>4\), the proof is complete. There are three other cases to consider:

- If deg (u) = deg (v) = 1, then uv is the only segment of G, which is impossible.

- Otherwise, if deg (u) = 1, then P must contain the spur [v, u, v] , which implies ϕ ˜ P ϕ ϕ P ϕ 2 and therefore ( ˜ P, ˜ G) (P, G) (deg (v) 1) (P, G) 1.

- Finally, suppose deg (u) = deg (v) = 2. Because uv is useful, P must contain one of the spurs [v, u, v] or [u, v, u] , which implies ϕ ˜ P ϕ ϕ P ϕ 2 and therefore ( ˜ P, ˜ G) (P, G) 2.

Lemma 5.4 immediately implies the main loop of the algorithm ends after at most \(2 n\) segment expansions. Because the potential \(\Phi\) decreases at every iteration, the polygon never has more than \(2 n\) vertices. We can find a useful segment in the image graph (if one exists) and perform a segment expansion in \(O(n)\) time by brute force. Thus, a naïve implementation of our algorithm runs in \(O\left(n^{2}\right)\) time.

## 6 Fast Implementation

Finally, we describe a more careful implementation of the previous algorithm that runs in \(O(n \log n)\) time. We build the image graph \(G\) and perform the initial node expansions in \(O(n \log n)\) time, just as in the previous sections. After building some necessary data structures, we repeatedly expand useful segments until we either find a local crossing or there are no more useful segments.

### 6.1 Data Structures

Our algorithm uses the following data structures. We maintain the image graph \(G\) in a standard data structure for planar straight-line graphs, such as a doubly-connected edge list [5]. The polygon \(P\) is represented by a circular doubly-linked list that alternates between vertex records and edge records; each vertex in \(P\) points to the corresponding node in \(G\). Call an edge of \(P\) simple if neither endpoint is a spur and complex otherwise. For each segment \(u_{v}\), we separately maintain a doubly-linked list Simple( \(u_{v}\) ) of all simple edges of \(P\) that coincide with \(u_{v}\), and a doubly-linked list Complex( \(u_{v}\) ) of all complex edges of \(P\) that coincide with \(u_{v}\). Every record in these lists has pointers both to and from the corresponding edge record in the circular list representing \(P\). Each of these lists also maintains its size. Each node \(u\) in \(G\) also maintains a pointer to its base (or bases). Finally, we maintain a global queue of all useful segments in \(G\). All of these data structures can be constructed in \(O(n)\) time after the preprocessing phase.

### 6.2 Segment Expansion

Our algorithm divides each segment expansion into the following four phases: (1) remove all spurs at the endpoints \(u\) and \(v\); (2) compute the nodes [ua] and [ \(v_{z}\) ] in cyclic order around the ellipse \(\partial D_{u_{v}}\); (3) straighten the remaining paths through \(u\) and through \(v\); (4) build the graph \(G_{D}\), check for simple crossings, and update the image graph \(G\). Our analysis uses the following functions of \(u\) (and similar functions of \(v\) ), all defined just before the segment expansion begins:

- deg (u) is the number of segments incident to u, including uv.

- n (u) is the number of vertices of P that coincide with u.

- (u) is the number of spurs of P that coincide with u.

- (u) = n (u) (u) is the number of vertices at u that are not spurs.

, . Specifically:

Phase 1: Remove spurs. We remove all spurs at \(u\) and \(v\) by brute force, by traversing \(u_{v}\) 's list of complex edges. Each time we remove a spur \(s\), we check the edges of \(P\) immediately before and after \(s\), and if necessary, move them from Simple(s) to Complex(s) or vice versa. We also update the count \(n(u)\) and \(n(v)\). After this phase, every maximal subpath of \(P\) inside the disk \(D_{u_{v}}\) has length at most 3. The total time for this phase is \(O(\sigma(u)+\sigma(v))\). Phase 2: Compute sequence of new nodes. Next, we compute the intersection points \(G \cap \partial D\) in cyclic order by considering the segments incident to \(u\) in cyclic order, starting just after \(u_{v}\), and then the segments incident to \(v\) in cyclic order, starting just after \(u_{v}\). These two cyclic orders are accessible in the doubly-connected edge list representing \(G\). For each intersection point \([u a]\) or \([v_{z}]\), we initialize a new node record with a pointer to its base \([u a] a\) or \([v_{z}] z\). At this point, we can update the queue of useful segments. Finally, we find a segment \(u a^{*}\) with maximum weight \(n\left(\left[u a^{*}\right]\right)\) and a segment \(v z^{*}\) with maximum weight \(n\left(\left[v z^{*}\right]\right)\), such that \(a^{*} \neq v\) and \(z^{*} \neq u\). To simplify notation, let \(u^{\prime}\) denote the point \(\left[u a^{*}\right]=\) \(u a^{*} \cap \partial D\) and let \(v^{\prime}\) denote the point \(\left[v z^{*}\right]=v z^{*} \cap \partial D\). The total time for this phase is \(O(\operatorname{deg}(u)+\operatorname{deg}(v))\). Phase 3: Expansion. The third phase straightens the remaining constant-length paths through \(u\) and \(v\) except for subpaths \(\left[a^{*}, u, v, z^{*}\right]\) or \(\left[a^{*}, u, a^{*}\right]\) or \(\left[z^{*}, v, z^{*}\right]\). Specifically, for each segment ua with \(a \neq a^{*}\),

- [a, u, v] becomes [a, [ua] , v] · [a, u, a] becomes [a, [ua] , a] ·

- [a, u, b] becomes [a, [ua] , [ub] , b]

$$
O(\sigma(u)+\sigma(v))+O\left(\phi(u)-n\left(u^{\prime}\right)+\phi(v)-n\left(v^{\prime}\right)\right)+O(\operatorname{deg}(u)+\operatorname{deg}(v)) .
$$

$$
\phi(u)=\sum_{x \in C(u)}(n(x)+\sigma(x)) .
$$

$$
\phi(u)-n\left(u^{\prime}\right)=\sum_{x \in C(u) \backslash\left\{u^{\prime}\right\}} n(x)+\sum_{x \in C(u)} \sigma(x),
$$

$$
\sum_{u \in N}\left(\phi(u)-n\left(u^{\prime}\right)\right)=\sum_{x \in N \backslash N^{\prime}} n(x)+O(n) .
$$

Then for each segment \(v_{z}\) with \(z \neq z^{*}\), we similarly replace subpaths of \(P\) that contain \(v_{z}\) with paths At the end of these two loops, the only remaining subpaths through \(u\) and \(v\) have the forms \(\left[a^{*}, u, v, z^{*}\right]\) or \(\left[a^{*}, u, a^{*}\right]\) or \(\left[z^{*}, v, z^{*}\right]\). To update these subpaths, we intuitively move node \(u\) to \(u^{\prime}\) and move node \(v\) to \(v^{\prime}\). But in fact, "moving" these two nodes has no effect on our data structures at all; we only change their names for purposes of analysis. The total time for this phase at most \(O((u)\) n (\(u_{0}\)) + (v) n (\(v_{0}\))), where n (\(u_{0}\)) and n (\(v_{0}\)) denote the number of vertices at \(u_{0}\) and \(v_{0}\) after the segment expansion.

Phase 4: Check planarity and update \(\boldsymbol{G}\). We discover all the segments in the graph \(G_{D}\) in the previous phase. If there are more than \(2(\operatorname{deg}(u)+\operatorname{deg}(v))\) such segments, then \(G_{D}\) cannot be planar, so we immediately halt and report that \(P\) is not weakly simple. Otherwise, we compute the rotation system of \(G_{D}\) and check its planarity in \(O(\operatorname{deg}(u)+\operatorname{deg}(v))\) time, as described in Section C.2. If \(G_{D}\) is a plane graph, we splice it into the image graph \(G\), again in \(O(\operatorname{deg}(u)+\operatorname{deg}(v))\) time.

This completes our implementation of segment expansion.

### 6.3 Time Analysis and Heavy-Path Decomposition

The total running time of a single edge expansion is at most Since each segment incident to \(u\) carries at least one edge, we have \(\operatorname{deg}(u)<\sigma(u)+\phi(u)\), so we can charge the last term to the first two. The total time spent removing spurs is clearly \(O(n)\). We bound the total remaining time as follows.

For purposes of analysis, imagine building a family tree \(\boldsymbol{T}\) of all nodes that our algorithm ever creates. The root of \(T\) is a special node \(r\), whose children are the nodes in the initial image graph (after node expansion). The children in \(T\) of any other node \(u\) are the new nodes [ua] created during the segment expansion that destroys \(u\). (Likewise, the children of \(v\) are the new nodes \([v_{z}]\).) Each node \(u\) in \(T\) has weight \(n(u)\), which is the number of vertices located at \(u\) just before the segment expansion that destroys \(u\), or equivalently, just after the segment expansion that creates \(u\). To simplify analysis, we set \(n(r)=n\), the initial number of vertices in \(P\). Let \(C(u)\) denote the children of node \(u\) in \(T\), and let \(u^{\prime}\) denote the maximum-weight child of \(u\). Finally, let \(N\) denote the set of all nodes, and let \(N^{\prime}\) denote the set of all maximum-weight children. Expanding segment \(u_{v}\) moves every vertex at \(u\) that is not a spur to one of the children of \(u\), and then merges pairs of coincident vertices to form spurs; thus,

The following standard heavy-path decomposition argument [27,46] implies that \(\sum_{x \in N \backslash N^{\prime}} n(x)=\) \(O(n \log n)\). If we remove the vertices in \(N^{\prime}\) from \(T\) by contracting each node in \(N^{\prime}\) to its parent, the resulting tree has height \(O(\log n)\), and the total weight of the nodes at each level is \(O(n)\). We conclude that the total time spent expanding segments is \(O(n \log n)\), which completes the proof of Theorem 5.1.

## Appendix

## A Problems with Previous Definitions

### A.1 Crossing and Self-Crossing

Many authors have offered the intuition that a polygon is weakly simple if and only if it is not "selfcrossing"; indeed, this is the complete definition offered by some authors [1,30]. However, a proper definition of "self-crossing" is quite subtle; we believe the most natural and general definition is the following. Two paths \(P\) and \(Q\) are weakly disjoint if, for all sufficiently small \(\varepsilon>0\), there are disjoint paths \(\tilde{P}\) and \(\tilde{Q}\) such that \(d_{\mathcal{F}}(P, \tilde{P})<\varepsilon\) and \(d_{\mathcal{F}}(Q, \tilde{Q})<\varepsilon\). Two paths cross if they are not weakly disjoint. Finally, a closed curve is self-crossing if it contains two crossing subpaths. However, this is not the definition of 'crossing' that most often appears in the computational geometry literature; variants on the following combinatorial definition are much more common [10,19,34,47] . Two polygonal chains P = [\(p_{0}\), \(p_{1}\), . . . , p ' ] and Q = [\(q_{0}\), \(q_{1}\), . . . , q ' ] with length ' 3 have a forward crossing if they satisfy two conditions:

- pi = qi for all 1 i ' 1, and

- the cyclic order of p 0, q 0, p 2 around p 1 is equal to the cyclic order of p ' , q ' , p ' 2 around p ' 1.

Polygonal chains \(P\) and \(Q\) have a backward crossing if \(P\) and the reversal of \(Q\) have a forward crossing. (See Figure A.1.) Finally, two polygonal chains \(P\) and \(Q\) cross if some subpaths of \(P\) and \(Q\) have a simple crossing, a forward crossing, or a backward crossing.

![Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-a-5-p016.png)

*Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.: Figure A.5. A polygon (a, b, c, a, b, c, a, x, y, z, x, y, z, x) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.*

These two definitions appear to be equivalent for polygonal chains without spurs, but they are not equivalent in general; Figure A.2 shows two simple examples where the definitions differ. In fact, we know of no combinatorial definition of 'crossing' that agrees with our topological definition for arbitrary polygonal chains with spurs.

![Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-a-5-p016.png)

*Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.: Figure A.5. A polygon (a, b, c, a, b, c, a, x, y, z, x, y, z, x) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.*

Several other authors (including the second author of this paper) have proposed the following more intuitive definition [22,44,50]: Two paths \(P\) and \(Q\) "cross" if, for arbitrarily small neighborhoods \(U\) of some common subpath, path \(P\) contains a point in more than one component of \(\partial U \backslash Q\); see Figure A.3(a). This definition is correct when \(P\) and \(Q\) are simple, but it yields both false positives and false negatives for non-simple paths, even without spurs. For example, the paths \([w, x, y, z, x, y]\) and \([z, x, y, z, x, w]\) in

![Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-a-5-p016.png)

*Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.: Figure A.5. A polygon (a, b, c, a, b, c, a, x, y, z, x, y, z, x) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.*

### A.2 Weak Simplicity

Avoiding self-crossings is a necessary condition for a polygon to be weakly simple, but it is not sufficient. For example, a polygon that wraps 3 times around triangle (as considered by Meister [36] ) and the polygon (a, x, b, x, c, x, a, x, b, x, c, x) in Figure 1.1 are neither self-crossing nor weakly simple.

Toussaint [10,44,47,48] defines a polygon to be weakly simple if its rotation number is either +1 or-1 and any pair of points splits the polygon into two paths that cross. Here, the rotation number of a polygon is the sum of the signed external angles at the vertices of the polygon, divided by \(2 \pi\), where each external angle is normalized to the interval ( \(-\pi, \pi\) ). Unfortunately, the rotation number of a polygon with spurs is undefined, since there is no way to determine locally whether the external angle at a spur should be \(\pi\) or \(-\pi\). As a result, Toussaint's definition can only be applied to polygons without spurs.

![Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-a-5-p016.png)

*Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.: Figure A.5. A polygon (a, b, c, a, b, c, a, x, y, z, x, y, z, x) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.*

Even for polygons without spurs, there is a more subtle problem with Toussaint's definition. Consider the 14-vertex polygon \((a, b, c, a, b, c, a, x, y, z, x, y, z, x)\) shown in Figures 2.1 and A.5. This polygon contains exactly two crossings: one between subpaths \([x, a, b, c, a, b]\) and \([c, a, b, c, a, x]\), and the other between subpaths \([a, x, y, z, x, y]\) and \([z, x, y, z, x, a]\). However, both pairs of crossing subpaths overlap not just geometrically, but combinatorially, as substrings of the polygon's vertex sequence. In short, a polygon (or polygonal chain) can cross itself without being divisible into two paths that cross each other! Demaine and O'Rourke's definition of a self-crossing linkage configuration [19] has the same problem. (Their definition also does not consider the possibility of backward crossings.)

![Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-a-5-p016.png)

*Figure A.5. A polygon ( a , b , c , a , b , c , a , x , y , z , x , y , z , x ) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.: Figure A.5. A polygon (a, b, c, a, b, c, a, x, y, z, x, y, z, x) that is not weakly simple, even though its rotation number is 1 and every pair of vertices splits the polygon into two paths that do not cross.*

Finally, it is unclear how we could use the combinatorial definitions of "crossing" and "self-crossing" that correctly handle these subtleties to quickly determine whether a polygon is weakly simple. Given a polygon \(P\) without spurs, there is a natural algorithm to determine whether \(P\) is self-crossing in \(O\left(n^{3}\right)\) time-Find all maximal coincident subpaths via dynamic programming, and check whether each one is a forward or backward crossing-but this is considerably slower than the algorithms we derive from the topological definition of "weakly simple".

Several other papers offer definitions of "weakly simple" that are overly restrictive [ \(7,8,28,35,41\) ]. For example, the LEDA software library [35] defines a polygon to be weakly simple it it has coincident vertices but otherwise disjoint edges; Bose and Morin [7,8] define a polygon to be weakly simple if the graph \(G\) defined by its vertices and edges is plane, the outer face of \(G\) is a cycle, and one bounded face of \(G\) is adjacent to all vertices. It is straightforward to construct weakly simple polygons that contradict these definitions.

Finally, several recent papers define weak simplicity directly in terms of vertex perturbation, what we are calling rigid weak simplicity [18,21,29,32], without mentioning any connection to the more general (and arguably more natural) definition in terms of Fréchet distance. \({ }^{2}\) Again, we emphasize that the algorithms in all the papers we discuss in this section appear to be correct, and the simple polygons they construct are consistent with the corresponding papers' definitions.

## B Proof of Theorem 2.1

In this section, we prove Theorem 2.1: Every weakly simple polygon with more than two vertices is rigidly weakly simple. In fact we will prove a stronger result; as explained in Sections 2.5 and A, most of the definitions of 'weakly simple' in the past are either incorrect or restricted. However, several related notions turn out to be equivalent to our formal definition of weak simplicity. Here is the statement of the full theorem we are about to prove; we defer the definitions of the bold terms to later subsections.

Theorem B.1. Let \(P\) be a polygon with more than two vertices. The following statements are equivalent: (a) \(P\) is weakly simple.

- (b) P is a compound-planar rigid clustered cycle [17].

- (c) P is strip-weakly simple.

- (d) P has a self-touching configuration [16].

- (e) P is rigidly weakly simple.

These terms are roughly ordered from least restrictive to most restrictive. The backward implications \((\mathrm{e}) \Rightarrow(\mathrm{d}) \Rightarrow(\mathrm{c}) \Rightarrow(\mathrm{b})\) and (c) \(\Rightarrow(\mathrm{a})\) all follow immediately from the definitions. Most of the forward implications also follow directly from the definitions and the classical Jordan-Schönflies theorem: Every simple closed curve is isotopic to a circle. The only exceptions are (a) ⇒ (c), which requires a more careful topological argument, and (d) ⇒ (e), which relies on a nontrivial result of Ribó Mor [39, Theorem 3.1].

### B.1 Strip system

Let \(G\) be the graph formed by the image of polygon \(P\) in the plane, whose vertices we call nodes and whose edges we call segments. For any real number \(\varepsilon>0\), the \(\varepsilon\)-strip system of \(P\) is a decomposition of a neighborhood of \(G\) into the following disks and strips.

- For each node u of G, let Du denote the disk of radius " centered at u.

- For each segment uv of G, let Suv denote the strip of points with distance at most " 2 from uv that do not lie in the interior of Du or Dv.

2 As of June 2014, Wikipedia [49] offers two definitions of 'weakly simple polygon', both of which are completely wrong. In particular, every planar straight-line graph is the limit, in the Hausdorff metric, of a sequence of simple polygons with a fixed number of vertices.

$$
A_{p_{0}, p_{1}}, A_{p_{1}, p_{0}}, A_{p_{1}, p_{2}}, A_{p_{2}, p_{1}}, \ldots, A_{p_{n-1}, p_{0}}, A_{p_{0}, p_{n-1}} .
$$

The circular \(\operatorname{arcs} A_{u, v}=S_{u_{v}} \cap D_{u}\) and \(A_{v, u}=S_{u_{v}} \cap D_{v}\) are called the ends of \(S_{u_{v}}\). We assume \(\varepsilon\) is sufficiently small that these disks and strips are pairwise disjoint except that each strip intersects exactly two disks at its ends. Finally, let \(U_{\varepsilon}\) denote the union of all these disks and strips. We say that a polygon \(P\) is strip-weakly simple if, for every sufficiently small \(\varepsilon>0\), there is a simple closed curve \(Q^{\prime}\) inside the neighborhood \(U_{\varepsilon}\) that crosses the disks and strips of the strip system in the same order that \(P\) traverses the nodes and segments of \(G\). Formally, if \(P=\left(p_{0}, p_{1}, \ldots, p_{n-1}\right)\), then the curve \(Q^{\prime}\) intersects ends only transversely, in the cyclic order

In particular, \(Q^{\prime}\) never intersects the same end consecutively more than once. Informally, we say that such a curve respects the strip system of \(P\). Any closed curve \(Q\) that respects the \(\varepsilon\)-strip system of \(P\) satisfies the inequality \(d_{\mathcal{F}}(P, Q)<\varepsilon\). It follows immediately that if \(P\) is strip-weakly simple, then \(P\) is also weakly simple. The converse implication requires a more careful topological argument.

Lemma B.2. A polygon \(P\) is weakly simple if and only if \(P\) strip-weakly simple.

Proof: Let \(P=\left(p_{0}, p_{1}, \ldots, p_{n-1}\right)\) be a weakly simple polygon. By breaking the edges if necessary, we assume that \(P\) has no forks. Fix a sufficiently small real number \(\varepsilon>0\), and let \(Q\) be a simple closed curve such that \(d_{\mathcal{F}}(P, Q)<\varepsilon^{2}\). This closed curve lies within the neighborhood \(U_{\varepsilon}\) but does not necessarily have the correct crossing pattern with the arcs of the strip system. To complete the proof, we show how to locally modify \(Q\) into a simple closed curve \(Q^{\prime}\) that respects the strip system of \(P\).

```text
For each node \(u\), let \(\widehat{D}_{u}\) denote the complement of the unbounded component of the complement the union of \(D_{u}\) with all bad subpaths with endpoints in \(D_{u}\). The subspace \(\widehat{D}_{u}\) is a closed topological disk, and for any two nodes \(u\) and \(v\), the disks \(\widehat{D}_{u}\) and \(\widehat{D}_{v}\) are disjoint. The Jordan-Schönflies theorem implies that there is a homeomorphism \(h_{u}: \widehat{D}_{u} \rightarrow D_{u}\) for each node \(u\);
without loss of generality, this homeomorphism fixes every good point on \(\partial D_{u}\).
```

We call a subpath of \(Q\) good if it lies entirely within a strip and has one endpoint on each end of that strip. If \(\varepsilon\) is sufficiently small, \(Q\) has exactly \(n\) good subpaths. We call the endpoints of the good subpaths good points. Removing the good subpaths of \(Q\) leaves exactly \(n\) bad subpaths; each bad subpath intersects only one disk \(D_{u}\), but may intersect any end on \(\partial D_{u}\) an arbitrary (or even uncountably many!) number of times.

Let \(D_{u}^{-}\)denote the disk of radius \(\varepsilon-\varepsilon^{2}\) centered at \(u\), and let \(h_{u}^{-}: \widehat{D}_{u} \rightarrow D_{u}^{-}\)be the homeomorphism obtained by applying \(h_{u}\) and then scaling around \(u\). Then, we compose the homeomorphism \(h_{u}^{-}\)into a single homeomorphism \(h^{-}: \bigsqcup_{u} \widehat{D}_{u} \rightarrow \bigsqcup_{u} D_{u}^{-}\).

![Figure B.1. Subpaths of Q and Q ′ within the strip system of node u .](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-b-p018.png)

*Figure B.1. Subpaths of Q and Q ′ within the strip system of node u .: Figure B.1. Subpaths of Q and Q ′ within the strip system of node u. 0 within the strip system of node u.*

```text
Finally, let \(Q^{\prime}\) be the closed curve obtained from \(Q\) by replacing each bad subpath with its image under the homeomorphism \(h^{-}\)and then, for each node \(u\), connecting each good point on \(\partial D_{u}\) with the corresponding point on \(\partial D_{u}^{-}\)with a line segment;
see Figure B.1. \(Q^{\prime}\) is a simple closed curve that respects the strip system of \(P\). It follows that \(P\) is strip-weakly simple.
```

### B.2 Compound-Planarity and Self-Touching Configurations

However, both definitions turn out to be almost equivalent to our definition of strip-weakly simple. We describe here only the relevant differences; we refer the reader to the original papers [16,17] for the original definitions.

Following Connelly, Demaine and Rote [16], a polygon \(P\) can be represented as a self-touching configuration if, for any \(\varepsilon>0\), there is a simple closed curve \(Q\) that respects the \(\varepsilon\)-strip system of \(P\), with the additional requirement that for each segment \(u_{v}\), the intersection \(Q \cap S_{u_{v}}\) is a set of disjoint line segments from one end of \(S_{u_{v}}\) to the other. Given any closed curve \(Q^{\prime}\) that respects the \(\varepsilon\)-strip system of \(P\), the Jordan-Schönflies theorem implies there there is a homeomorphism \(h_{u_{v}}: S_{u_{v}} \rightarrow S_{u_{v}}\) that straightens the good subpaths \(Q \cap S_{u_{v}}\). This gives us the implication (c) ⇔(d).

Following Cortese et al. [17,23,24], a polygon \(P\) can be represented as a compound-planar rigid clustered cycle if it respects an arbitrary topological strip system. In a topological strip system, the regions \(D_{u}\) and strips \(S_{u_{v}}\) are arbitrary closed topological disks that contain the corresponding nodes and segments of \(G\), where for any segment \(u_{v}\), the intersection \(S_{u_{v}} \cap D_{u}\) is a simple path, and otherwise all the disks are disjoint. The Jordan-Schönflies theorem implies that there is a homeomorphism of the plane to itself that maps any topological strip system of \(P\) to the \(\varepsilon\)-strip system of \(P\), for any \(\varepsilon>0\). This gives us the equivalent (b) ⇔ (c).

### B.3 Rigidification Lemma

Finally, a self-touching configuration has a \(\delta\)-perturbation if there is a planar configuration of the same linkage such that corresponding joints (vertices of the linkage) in the two configurations have distance at most \(\delta\) [16]. Equivalently, a \(\delta\)-perturbation of \(P\) is a simple polygon at vertex distance at most \(\delta\) from \(P\). Ribó Mor [39, Theorem 3.1] proved that every self-touching configuration of a linkage with at least three vertices has a \(\delta\)-perturbation, for any \(\delta>0\). This theorem provides the final link (d) ⇒ (e), completing the proof of Theorem B.1.

## C Expansion

The node expansion, bar expansion, and segment expansion operations used by the algorithms in Sections 3, 4, and 5 are all special cases of a more general operation, defined as follows. Let P = (\(p_{0}\), \(p_{1}\), . . . , pn 1) be an arbitrary polygon, and let D be an elliptical disk that intersects P transversely ; that is, the boundary ellipse @ D intersects at least one edge of P, is not tangent to any edge of P, and does not contain any vertex of P. To expand P inside D, we subdivide the edges of P that intersect @ D by introducing new vertices at the intersection points, and then replace each maximal subpath of P inside D with a straight line segment between its endpoints on @ D. In the rest of this section, we provide missing proofs and implementation details for the expansion operations in our earlier algorithms.

### C.1 Preserving Weak Simplicity

Lemma C.1. Let \(P\) be a weakly simple polygon, and let \(D\) be an elliptical disk whose boundary intersects \(P\) transversely. The polygon \(\tilde{P}\) obtained by expanding \(P\) inside \(D\) is weakly simple.

Proof: Suppose \(P=\left(p_{0}, p_{1}, \ldots, p_{n-1}\right)\) is a weakly simple polygon. By Theorem 2.1, for any real number \(\varepsilon>0\), there is a simple polygon \(Q=\left(q_{0}, q_{1}, \ldots, q_{n-1}\right)\) such that \(d_{V}(P, Q)<\varepsilon\). If \(\varepsilon\) is sufficiently small, \(\partial D\) also intersects \(Q\) transversely; moreover, \(\partial D\) intersects an edge of \(Q\) if and only if it intersects the corresponding edge of \(P\) in the same number of points. Let \(\tilde{Q}\) be the polygon obtained by expanding \(Q\) inside \(D\). See Figure C.1.

Thus, for any \(\delta>0\), we obtain a simple polygon \(\tilde{Q}\) such that \(d_{\mathcal{F}}(\tilde{P}, \tilde{Q})<\delta\) by setting \(\varepsilon<(\delta / 2) \sin \theta^{*}\). We conclude that \(\tilde{P}\) is weakly simple.

The converse of this lemma is not true in general; Figure C.2 shows a simple counterexample. However, 10 as we argue below, the converse of this lemma is true for the specific expansions performed by our 11 algorithms. 12

![Figure C.3. Bar expansion. Compare with Figure 3.1 .](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-100-3-p021.png)

*Figure C.3. Bar expansion. Compare with Figure 3.1 .: Figure C.3. Bar expansion. Compare with Figure 3.1.*

### C.2 Implementation and Planarity Checking

Given the polygon \(P\) and ellipse \(D\), it is straightforward to compute the polygon \(\tilde{P}\) resulting from expanding \(P\) inside \(D\) in \(O(n)\) time by brute force. For arbitrary expansions, computing and sorting the coordinates of the intersection points with the ellipse \(\partial D\) requires some care. In our algorithms, however, all expansion operations can be performed combinatorially, with no numerical computation whatsoever. The actual size and shape of the disk \(D\) is completely immaterial to our algorithms; our geometric description in terms of ellipses is intended to provide intuition and simplify our proofs. Our algorithms maintain a representation of the polygon \(P\) that allows us to compute the sequence of points where \(P\) crosses \(\partial D\), in cyclic order around \(D\), in constant time per intersection point. Specifically, for the node and segment expansions in Sections 3 and 5, this sequence of points can be extracted from the rotation system of the image graph \(G\). For the bar expansions in Section 4, this sequence can be

![Figure C.3. Bar expansion. Compare with Figure 3.1 .](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-100-3-p021.png)

*Figure C.3. Bar expansion. Compare with Figure 3.1 .: Figure C.3. Bar expansion. Compare with Figure 3.1.*

Because \(Q\) is simple, the intersection \(Q \cap D\) consists of disjoint simple subpaths. For any two such subpaths \(\alpha\) and \(\beta\), the endpoints of \(\alpha\) must lie in one component of \(\partial D \backslash \beta\), and thus the corresponding line segments \(\tilde{\alpha}\) and \(\tilde{\beta}\) of \(\tilde{Q}\) are also disjoint. It follows that \(\tilde{Q}\) is also simple. Consider a vertex \(\tilde{p}\) of \(\tilde{P}\), located at the intersection of an edge \(p_{i} p_{i+1}\) of \(P\) and the ellipse \(\partial D\). Let \(\theta\) denote the angle between \(p_{i} p_{i+1}\) and (the line tangent to) \(\partial D\) at \(\tilde{p}\). If \(\varepsilon\) is sufficiently small, the corresponding edge \(q_{i} q_{i+1}\) of \(Q\) intersects \(\partial D\) at a point \(\tilde{q}\) such that \(d(\tilde{p}, \tilde{q})<2 \varepsilon / \sin \theta\). It follows that \(d_{V}(\tilde{P}, \tilde{Q})<2 \varepsilon / \sin \theta^{*}\), where \(\theta^{*}\) is the minimum angle of intersection between \(P\) and \(\partial D\).

extracted from the order of forks along each bar，and cyclic order of bars ending at each fork；both of these orders are computed as part of the bar decomposition．Given this sequence of points，which of these orders are computed as part of the bar decomposition．Given this sequence of points，which become the new vertices of \(\tilde{P}\) ，we can perform the rest of the expansion in \(O(m)\) time，where \(m\) is the number of edges of \(P\) that intersect \(D\) ． If P is not weakly simple, the expanded polygon ˜ P may include pairs of edges that cross transversely. Let GD denote the graph whose vertices are the intersection points im P ∴ @ D and whose edges are distinct edges of ˜ P inside D and arcs of @ D between vertices in cyclic order. ˜ P contains crossing edges if and only if GD is not a plane graph. We can determine the planarity of \(G_{D}\) as follows．first，add a new＂apex＂vertex \(a\) and connect it by edges to each of the vertices of \(G_{D}\) ．The resulting abstract graph \(G_{D}^{+}\)is 3－connected，and therefore by edges to each of the vertices of \(G_{D}\) ．The resulting abstract graph \(G_{D}^{+}\)is 3－connected，and therefore has at most one planar embedding．Moreover，\(G_{D}^{+}\)is planar if and only if there is a planar embedding 的 of \(G_{D}\) with all vertices on a single face（which we take to be the outer face）in the correct cyclic order． Thus，\(G_{D}\) is a plane graph if and only if \(G_{D}^{+}\)is a planar graph；there are several linear－time algorithms to Thus，\(G_{D}\) is a plane graph if and only if \(G_{D}^{+}\)is a planar graph；there are several linear－time algorithms to determine whether a graph is planar \([9,25,31,45]\) ．Crudely，\(G_{D}\) has at most \(O(m)\) vertices and edges，so determine whether a graph is planar［9，25，31，45］．Crudely，\(G_{D}\) has at most \(O(m)\) vertices and edges，so 别 the planarity check takes at most \(O(m)\) time．

### C.3 Node Expansion

In Section 3，we define node expansion as expansion inside a circular disk \(D_{u}\) of radius \(\delta\) centered at 洞的 some vertex \(u\) of \(P\) ，where the radius \(\delta\) is sufficiently small that \(D_{u}\) intersects only edges incident to \(u\) ． Lemma C． 2 （Cortese et al．［17，Lemma 2］）．Let \(P\) be an arbitrary polygon，and let \(\tilde{P}\) be the result of a single node expansion．\(P\) is weakly simple if and only if \(\tilde{P}\) is weakly simple． Proof：Suppose \(\tilde{P}\) is weakly simple．Fix a sufficiently small positive real number \(\varepsilon<\delta\) ．By Theorem 2．1， there is a simple polygon \(\tilde{Q}\) such that \(d_{\mathcal{F}}(\tilde{P}, \tilde{Q}) \leq d_{V}(\tilde{P}, \tilde{Q})<\varepsilon\) ．We easily observe that \(d_{\mathcal{F}}(P, \tilde{P})<\delta\) ． 的 Thus，the triangle inequality implies \(d_{\mathcal{F}}(P, \tilde{Q})<d_{\mathcal{F}}(P, \tilde{P})+d_{\mathcal{F}}(\tilde{P}, \tilde{Q})<\delta+\varepsilon<2 \delta\) ．Because \(\delta\) is arbitrarily 的 small，we conclude that \(P\) is weakly simple．Finally，Lemma C． 1 completes the proof．

### C.4 Bar Expansion

Recall from Section 4 that a bar of \(P\) is a component of the union of all edges of \(P\) that lie on some line．Bar expansion is defined as expansion inside an ellipse \(D_{b}\) defined by a bar \(b\) as follows．Fix a 的 sufficiently small real number \(\delta>0\) ．Let \(b^{\circ}\) denote the subset of \(b\) containing points at distance at least sufficiently small real number \(\delta>0\) ．Let \(b^{\circ}\) denote the subset of \(b\) containing points at distance at least \(2 \delta\) from the endpoints of \(b\) ．Finally，\(D_{b}\) is the ellipse whose major axis is \(b^{\circ}\) and whose minor axis has 别的 length \(2 \delta\) ．We emphasize that the endpoints of the bar \(b\) are outside \(D_{b}\) ．

![Figure C.3. Bar expansion. Compare with Figure 3.1 .](/Users/evanthayer/Projects/paperx/docs/2015_detecting_weakly_simple_polygons/figures/figure-100-3-p021.png)

*Figure C.3. Bar expansion. Compare with Figure 3.1 .: Figure C.3. Bar expansion. Compare with Figure 3.1.*

Lemma C．3．Let \(P\) be a polygon without spurs，and let \(\tilde{P}\) be the result of a single bar expansion．\(P\) is weakly simple if and only if \(\tilde{P}\) is weakly simple． Proof: Let \(b\) be the bar around which we are expanding, and let \(\theta>0\) denote the minimum positive angle between \(b\) and any edge incident to but not contained in \(b\). Consider a subpath \([u, v, w, x]\) of \(P\) such that \(v_{w}\) lies in the interior of \(D_{b}\) and therefore in the bar \(b\); the vertices \(u\) and \(x\) must lie outside \(D_{b}\).

If \(\tilde{P}\) is weakly simple, there is a simple polygon \(\tilde{Q}\) such that \(d_{\mathcal{F}}(\tilde{P}, \tilde{Q}) \leq d_{V}(\tilde{P}, \tilde{Q})<\delta\), which implies \(d_{\mathcal{F}}(P, \tilde{Q})<d_{\mathcal{F}}(P, \tilde{P})+d_{\mathcal{F}}(\tilde{P}, \tilde{Q})<\delta(1+1 / \sin \theta)\) by the triangle inequality. Since this Fréchet distance can be made arbitrarily small by shrinking \(\delta\), we conclude that \(P\) is weakly simple. Finally, Lemma C. 1 completes the proof.

We easily observe that ( , ˜ ) = sin ⇐ = sin and ( , ˜ ) = sin ⇐ = sin, which implies that d \(F([u,v,w,x],[u,˜v,˜w,x])\) = sin. By similar arguments for edges that share one or both endpoints of b, we conclude that d \(F(P,˜P)\) < = sin.

If \(P\) has spurs, then bar expansions are no longer safe; the resulting polygon \(\tilde{P}\) could be weakly simple even though \(P\) is not.

### C.5 Segment Expansion

Recall from Section 5 that segment expansion means expansion around an ellipse that just contains one segment of the image graph \(G\). For purposes of proving correctness, we specify this ellipse more carefully as follows. Fix a sufficiently small real number \(\delta>0\). For any segment \(u_{v}\) of \(G\), let \(u v^{+}\)denote the subset of all points on the line through \(u_{v}\) that have distance at most \(\delta\) from \(u_{v}\). Let \(D_{u_{v}}\) denote the ellipse whose major axis is \(u v^{+}\)and whose minor axis has length \(2 \delta\). We emphasize that in contrast to bar expansion, the endpoints of segment \(u_{v}\) lie inside \(D_{u_{v}}\).

To simplify the proof, we imagine that each segment expansion is preceded by a spur reduction, which replaces any subpath \([u, v, \ldots, u, v]\) that alternates between \(u\) and \(v\) at least twice with the single edge \([u, v]\). For example, the subpath \([a, u, v, u, v, u, v, b]\) would become a single spur \([a, u, v, u, b]\), and the subpath \([a, u, v, u, v, u, v, u, v, z]\) would become a simple subpath \([a, u, v, z]\).

Lemma C.4. Let \(P\) be any polygon, and let \(\bar{P}\) be the result of a spur reduction on some segment \(u_{v}\) of its image graph. If \(\bar{P}\) is weakly simple, then \(P\) is weakly simple.

Proof: It suffices to consider the case where \(\bar{P}\) is obtained from \(P\) by replacing exactly one subpath \([a, u, v, u, v, z]\) with the simpler subpath \([a, u, v, z]\), for some nodes \(a \neq v\) and \(z \neq u\). The argument for Suppose \(\bar{P}\) is weakly simple. Then by Theorem 2.1 for any \(\varepsilon>0\), there is a polygon \(\bar{Q}\) with \(d_{V}(\bar{P}, \bar{Q})<\varepsilon\). Let \(\left[a^{\prime}, u^{\prime}, v^{\prime}, z^{\prime}\right]\) be the subpath of \(\bar{Q}\) corresponding to the replacement subpath \([a, u, v, z]\) of \(\bar{P}\). If \(\varepsilon\) is sufficiently small, we can find four points \(u_{1}, u_{2}, v_{1}, v_{2}\) with the following properties:

- d (\(u_{1}\), \(u_{0}\) \(v_{0}\)) = d (\(u_{2}\), \(u_{0}\) \(v_{0}\)) = d (\(u_{1}\), \(u_{0}\) \(v_{0}\)) = d (\(u_{2}\), \(u_{0}\) \(v_{0}\)) = " 2, and

- d (\(u_{1}\), \(u_{0}\)) = d (\(u_{2}\), \(u_{0}\)) = d (\(v_{1}\), \(v_{0}\)) = d (\(v_{2}\), \(v_{0}\)) = " ,

- the path [\(u_{0}\), \(u_{1}\), \(v_{1}\), \(u_{2}\), \(v_{2}\), \(v_{0}\)] is simple and intersects ¯ Q only at the edge \(u_{0}\) \(v_{0}\).

Let \(Q\) be the simple polygon obtained by replacing the edge \(\left[u^{\prime}, v^{\prime}\right]\) with \(\left[u^{\prime}, u_{1}, v_{1}, u_{2}, v_{2}, v^{\prime}\right]\). Then we have \(d_{\mathcal{F}}(P, Q)<2 \varepsilon\) by the triangle inequality, which implies that \(P\) is weakly simple.

The following lemma was proved by Cortese et al. [17, Lemma 3] ; we provide an alternative geometric proof here.

Lemma C.5. Let \(P\) be a spur-reduced polygon with more than two distinct vertices, and let \(\tilde{P}\) be the result of a safe segment expansion. \(P\) is weakly simple if and only if \(\tilde{P}\) is weakly simple.

$$
d_{\mathcal{F}}\left([[u a], u, v, u,[u b]],\left[a^{\prime}, a_{i}, z_{i}, a_{i}, b^{\prime}\right]\right)<\delta / \sin \theta+\varepsilon .
$$

Proof: Let \(u_{v}\) be the safe segment around which we are expanding, and let \(\theta\) be the smallest positive angle between \(u_{v}\) and any other segment incident to \(u\) or \(v\). By the previous lemma, we can assume without loss of generality that \(P\) does not contain the subpath [ \(u, v, u, v\) ].

Suppose P has k distinct spurs at uv. For each integer i from 0 to k, let Di be the elliptical disk concentric with Duv but whose axes are shorter by 2 (i + 1) " . For example, the major axis of \(D_{0}\) has length ϕ uv ϕ + 2 2 " and the minor axis has length 2 2 " . Every vertex of ˜ Q lies outside each disk Di, and if " is sufficiently small, every edge of ˜ Q that intersects D also intersects each disk Di.

Suppose ˜ P is weakly simple. Fix a real number " = 2 n, and let ˜ Q be a simple polygon such that dV ( ˜ P, ˜ Q) < " , guaranteed by Theorem 2.1. If P has no spurs at uv, the proof of Lemma C.3 implies that d \(F(P,˜Q)\) < (1 + 1 = sin) and we are done. However, if P has a spur at uv, the Fréchet distance between P and ˜ Q is approximately the length of uv. In this case, we iteratively modify ˜ Q into a new simple polygon Q such that d \(F(P,Q)\) < = sin + " < (1 + 1 = sin).

We iteratively define a sequence of polygons ˜ Q = Q 0, Q 1, . . . , Qk as follows. Fix an index i 0. Let Ui and Vi denote the subsets of @ Di within distance = sin of u and v, respectively. If is sufficiently small, the elliptical arcs Ui and Vi are disjoint. Every segment in ˜ Qi ∴ Di has endpoints in Ui [Vi. We call a segment in ˜ Qi ∴ Di a left segment if both endpoints are in Ui, or a right segment if both endpoints are in Vi. Every left segment corresponds to a subpath of P of the form [a, u, v, u, b] , and every right segment corresponds to a subpath of P of the form [y, v, u, v, z] .

Arguments in the proof of Lemma C. 3 imply that \(d\left(u, a^{\prime}\right)<\delta / \sin \theta+\varepsilon\) and \(d\left(u, b^{\prime}\right)<\delta / \sin \theta+\varepsilon\), which in turn imply that \(d\left(u, a_{i}\right)<\delta / \sin \theta+\varepsilon\) and \(d\left(u, b_{i}\right)<\delta / \sin \theta+\varepsilon\). It now follows that

Suppose \(\tilde{Q}_{i} \cap D_{i}\) includes at least one left segment; right segments are handled symmetrically. Then some component \(R_{i}\) of \(D_{i} \backslash \tilde{Q}_{i}\) has both a left segment and an arc of \(V_{i}\) on its boundary. Suppose the left segment corresponds to the subpath \([a, u, v, u, b]\) of \(P\). Then \(\tilde{P}\) contains the subpath \([a,[u a],[u b], b]\), where \([u a]=u a \cap \partial D_{u_{v}}\) and \([u b]=u b \cap \partial D_{u_{v}}\), polygon \(\tilde{Q}\) contains an edge \(a^{\prime} b^{\prime}\) such that \(d\left(a^{\prime},[u a]\right)<\varepsilon\) and \(d\left(b^{\prime},[u b]\right)<\varepsilon\), and finally \(a_{i} b_{i}=a^{\prime} b^{\prime} \cap D_{i}\) is the left segment in question. Fix a point \(z_{i} \in R \cap V_{i}\),

The final polygon \(Q_{k}\) has no left or right segments in \(D_{k}\); thus, every spur in \(P\) is within Fréchet distance \(\delta / \sin \theta+\varepsilon\) of the corresponding path \(Q_{k}\). We conclude that \(d_{\mathcal{F}}\left(P, Q_{k}\right)<\delta / \sin \theta+\varepsilon\), and Lemma C. 1 completes the proof.

## D Generalizations and Open Problems

### D.1 Polygonal Chains

A straightforward generalization of our algorithm can determine whether a given polygonal chain is weakly simple in \(O\left(n^{2} \log n\right)\) time, by checking a polygon that traverses the chain twice.

Lemma D.1. The polygonal chain \(P=\left[p_{0}, p_{1}, \ldots, p_{n-1}, p_{n}\right]\) is weakly simple if and only if the polygon Proof: Suppose \(P\) is weakly simple. Then for any \(\delta>0\), there is a simple curve \(Q\) with \(d_{\mathcal{F}}(P, Q)<\delta\). In fact, we can assume \(Q\) is a simple polygonal chain, as Ribó Mor's results [39] extend to polygonal chains. Fix a positive real number \(\varepsilon \ll \delta\) such that the intersection of \(Q\) with any closed disk of radius \(\varepsilon\) centered on a point of \(Q\) is connected; it suffices for \(\varepsilon\) be less than the minimum local feature size of \(Q\) [40]. Let \(\hat{Q}\) denote the boundary of the \(\varepsilon\)-neighborhood of \(Q\). Then \(\hat{Q}\) is a simple closed curve where \(d_{\mathcal{F}}(\hat{P}, \hat{Q})<\delta+2 \varepsilon\), which implies that \(\hat{P}\) is weakly simple.

$$
d_{\mathcal{F}}(P, Q)=\inf _{\phi: H \rightarrow H} \max _{x \in H} d(P(\phi(x)), Q(x))
$$

On the other hand, suppose the polygon \(\hat{P}\) is a weakly simple. Then for any \(\delta>0\) there is a simple polygon \(\hat{Q}\) such that \(d_{V}(\hat{P}, \hat{Q})<\delta\). Let \(Q\) be either subpath of \(\hat{Q}\) between the vertex corresponding to \(p_{0}\) to the vertex corresponding to \(p_{n}\). Then \(Q\) is a simple polygonal chain with \(d_{V}(P, Q)<\delta\), which implies that \(P\) is weakly simple.

### D.2 Graph Drawings

There is a natural generalization of weak simplicity to arbitrary graph drawings. Any graph can be regarded as a topological space, specifically, a branched 1-manifold. A planar drawing of a graph \(H\) is just a continuous map from \(H\) to the plane; a drawing is simple or an embedding if it is injective. The Fréchet distance between two planar drawings \(P\) and \(Q\) of the same graph \(H\) is naturally defined as where the infimum is taken over all automorphisms of \(H\) (homeomorphisms from \(H\) to itself). We can define a planar drawing \(P\) to be weakly simple (or a weak embedding) if, for any \(\varepsilon>0\), there is a planar embedding \(Q\) of \(H\) with \(d_{\mathcal{F}}(P, Q)<\varepsilon\). This definition is consistent with our existing definitions of weakly simple closed curves in the plane. It is a natural open question whether one can decide in polynomial time whether a given straight-line drawing of a planar graph is a weak embedding; Cortese et al. [17] observe that it is not sufficient to check whether every cycle in the drawing is weakly simple. However, a generalization of our algorithm actually solves this problem when the graph \(H\) being drawn is a disjoint union of cycles. In fact, the algorithm is unchanged except for the termination condition; when the main loop terminates, the image graph is the union of disjoint cycles and single segments, and \(P\) is weakly simple if and only if each component of \(P\) either traverses some component of the image graph exactly once or maps to an isolated segment. Moreover, using the doubling trick described above in Section D.1, our algorithm can also be applied to disjoint unions of cycles and paths. Details will appear in the full version of the paper.

Any algorithm to determine whether a graph drawing is a weak embedding must handle the special case where the image of the drawing is a simple path. This special case is equivalent to the strip planarity problem recently introduced by Angelini et al. [3] as a variant of clustered planarity [17,23] and level planarity [33] . The strip planarity problem is open even when the graph H is a tree.

### D.3 Surface Graphs

Our algorithm can also be generalized to surfaces of higher genus. A closed curve \(P\) in an arbitrary surface \(\Sigma\) is weakly simple if for any \(\varepsilon>0\) there is a simple (injective) closed curve \(Q\) in the same surface, such that \(d_{\mathcal{F}}(P, Q)<\varepsilon\), where Fréchet distance is defined with respect to an arbitrary metric Theorem D.2. Given a closed walk \(P\) of length \(n\) in an arbitrary surface-embedded graph, we can determine whether \(P\) is weakly simple in \(O(n \log n)\) time.

Our algorithms for detecting weakly simple polygons use the geometry of the plane only in the preprocessing phase, where we apply a sweep-line algorithm to remove forks and to construct the image graph. Cortese et al. already describe topological versions of our expansion operations, which use topological disks instead of ellipses, as well as their proofs of correctness [17]. The only minor subtlety is the termination condition when the underlying surface is non-orientable. For any integer \(k>0\), let \(\gamma^{k}\) be the cycle that wraps around some simple cycle \(\gamma\) exactly \(k\) times. Then \(\gamma^{k}\) is weakly simple if and only if \(k=1\), or \(k=2\) and \(\gamma\) is orientation-reversing [14,38,51]. Again, details will appear in the full version of the paper.

### D.4 Faster?

Finally, perhaps the most immediate open question is how to improve the \(O\left(n^{2} \log n\right)\) running time of our algorithm for arbitrary polygons with both spurs and forks. A direct generalization of bar expansion seems unlikely; Lemma C. 3 does not generalize to polygons with spurs. Nevertheless, we conjecture that the quadratic blowup from subdividing edges at forks can be avoided, and that the running time can be improved to \(O(n \log n)\).

## References

- [ 1 ] Manuel Abellanas, Alfredo García, Ferran Hurtado, Javier Tejel, and Jorge Urrutia. Augmenting

- the connectivity of geometric graphs. Comput. Geom. Theory Appl. 40(3):220-230, 2008. [2] Nancy M. Amato, Michael T. Goodrich, and Edgar Ramos. A randomized algorithm for triangulating a simple polygon in linear time. Discrete Comput. Geom. 26:245-265, 2001. [3] Patrizio Angelini, Giordano Da Lozzo, Giuseppe Di Battista, and Fabrizio Frati. Strip planarity testing. Proc. 21st International Symposium on Graph Drawing, 37-48, 2013. arXiv:1309.0683. [4] Jon Louis Bentley and Thomas A. Ottmann. Algorithms for reporting and counting geometric intersections. IEEE Trans. Comput. C-28(9):643-647, 1979. [5] Mark de Berg, Otfried Cheong, Marc van Kreveld, and Mark Overmars. computational Geometry: algorithms and Applications, 3rd edition. Springer-Verlag, 2008. [6] Joan S. Birman and Caroline Series. Geodesics with bounded intersection number on surfaces are sparsely distributed. Topology 24(2):217-225, 1985. [7] Prosenjit Bose, Jean-Lou De Carufel, Stephane Durocher, and Perouz Taslakian. Competitive online routing on Delaunay graphs. Proc. 14th Scand. Workshop algorithm Theory, 98-104, 2014. Lecture Notes Comput. Sci. 8503, Springer. [8] Prosenjit Bose and Pat Morin. Competitive online routing in geometric graphs. Theoretical Computer Science 324(2-3):273-288, 2004. [9] John M. Boyer and Wendy J. Wyrvold. On the cutting edge: Simplified O (n) planarity by edge addition. J. Graph algorithms Appl. 8(3):241-273, 2004. [10] David Dylan Bremner. point visibility graphs and restricted-orientation polygon covering. Master's thesis, Simon Fraser University, 1993. [11] Erin W. Chambers, Éric Colin de Verdière, Jeff Erickson, Francis Lazarus, and Kim Whittlesey. Splitting (complicated) surfaces is hard. Comput. Geom. Theory Appl. 41(1-2):94-110, 2008. [12] Erin W. Chambers, Jeff Erickson, and Amir Nayyeri. Minimum cuts and shortest homologous cycles. Proc. 25th Ann. Symp. Comput. Geom., 377-385, 2009. [13] Bernard Chazelle. Triangulating a simple polygon in linear time. Discrete Comput. Geom. 6(5):485524, 1991. [14] David R. J. Chillingworth. Winding numbers on surfaces, II. Math. Ann. 199:131-152, 1972. [15] Kenneth L. Clarkson, Robert E. Tarjan, and Christopher J. Van Wyk. A fast Las Vegas algorithm for triangulating a simple polygon. Discrete Comput. Geom. 4:423-432, 1989. [16] Robert Connelly, Erik D. Demaine, and Günter Rote. Infinitesimally locked self-touching linkages with applications to locked trees. Physical Knots: Knotting, Linking, and Folding of Geometric Objects in Ρ 3, 287-311, 2002. American Mathematical Society.

- [ 17 ] Pier Francesco Cortese, Giuseppe Di Battista, Maurizio Patrignani, and Maurizio Pizzonia. On embedding a cycle in a plane graph. Discrete Mathematics 309(7):1856-1869, 2009.

- [ 18 ] Mirela Damian, Robin Flatland, Joseph O'Rourke, and Suneeta Ramaswami. Connecting polygonizations via stretches and twangs. Theory of Computing Systems 47(3):674-695, 2010.

- [ 19 ] Erik D. Demaine and Joseph O'Rourke. Geometric Folding algorithms: Linkages, Origami, Polyhedra. Cambridge Univ. Press, 2007.

- [ 20 ] Olivier Devillers. Randomization yields simple O (n log n) algorithms for difficult (n) problems. Int. J. Comput. Geom. Appl. 2(1):621-635, 1992.

- [ 21 ] Adrian Dumitrescu and Csaba D. Tóth. Light orthogonal networks with constant geometric dilation. Journal of Discrete algorithms 7(1):112-129, 2009.

- [ 22 ] Jeff Erickson and Amir Nayyeri. Shortest noncrossing walks in the plane. Proc. 22nd Ann. ACM-SIAM Symp. Discrete algorithms, 297-308, 2011.

- [ 23 ] Qing-Wen Feng, Robert F. Cohen, and Peter Eades. Planarity for clustered graphs. Proc. 3rd Europ. Symp. algorithms, 1995. Lecture Notes Comput. Sci. 979, Springer.

- [ 24 ] Qingwen Feng. Recognizing compound planarity of graphs. Proc. 7th Australasian Workshop Combin. algorithms, 101-107, 1996. Technical Report 508, Basser Dept. Comput. Sci., Univ. Sydney. η http: www.it.usyd.edu.au research tr tr508.pdf ι.

- [ 25 ] Hubert de Fraysseix and Patrice Ossona de Mendez. Trémaux trees and planarity. Europ. J.Combin. 33(3):279-293, 2012.

- [ 26 ] Branko Grünbaum. Polygons: Meister was right and Poinsot was wrong but prevailed. Beitr. Algebra Geom. 53(1):57-71, 2012.

- [ 27 ] Dov Harel and Robert Endre Tarjan. Fast algorithms for finding nearest common ancestors. SIAM J. Comput. 13(2):338-355, 1984.

- [ 28 ] Michael Hoffmann, Bettina Speckmann, and Csaba D. Tóth. Pointed binary encompassing trees. Proc. 9th Scand. Workshop algorithm Theory, 442-454, 2004. Lecture Notes in Computer Science 3111, Springer. Preliminary version of [29].

- [ 29 ] Michael Hoffmann, Bettina Speckmann, and Csaba D. Tóth. Pointed binary encompassing trees: Simple and optimal. Comput. Geom. Theory Appl. 43(1):35-41, 2010. Full version of [28].

- [ 30 ] Michael Hoffmann and Csaba D. Tóth. Pointed and colored binary encompassing trees. Proc. 21st Ann. Symp. Comput. Geom., 81-90, 2005.

- [ 31 ] John Hopcroft and Robert E. Tarjan. efficient planarity testing. J. Assoc. Comput. Mach. 21(4):549569, 1974.

- [ 32 ] Mashhood Ishaque, Diane L. Souvaine, and Csaba D. Tóth. Disjoint compatible geometric matchings. Discrete and computational Geometry 49(1):89-131, 2013.

- [ 33 ] Michael Jünger, Sebastian Leipert, and Petra Mutzel. Level planarity testing in linear time. Proc. 6th Int. Symp. Graw Drawing, 224-237, 1998. Lecture Notes Comput. Sci. 1547, Springer.

- [ 34 ] Yoshiyuki Kusakari, Hitoshi Suzuki, and Takao Nishizeki. A shortest pair of paths on the plane with obstacles and crossing areas. Int. J. Comput. Geom. Appl. 9(2):151-170, 1999.

- [ 35 ] Kurt Mehlhorn and Stefan Näher. LEDA: A Platform for Combinatorial and Geometric Computing. Cambridge Univ. Press, 1999. [36] Albrecht Ludwig Friedrich Meister. Generalia de genesi figurarum planarum, et inde pendentibus earum affectionibus. Novi Commentarii Soc. Reg. Scient. Gott. 1:144-180 + 9 plates, 17691770. Presented January 6, 1770. [37] Bojan Mohar and Carsten Thomassen. Graphs on Surfaces. Johns Hopkins Univ. Press, 2001. [38] Bruce L. Reinhart. Algorithms for Jordan curves on compact surfaces. Ann. Math. 75:271-283, 1962. [39] Ares Ribó Mor. Realization and Counting Problems for planar Structures: Trees and Linkages, Polytopes and Polyominoes. Ph.D. thesis, Freie Universität Berlin, 2006. [40] Jim Ruppert. A new and simple algorithm for quality 2-dimensional mesh generation. J. algorithms 18(3):548-585, 1995. [41] Ignaz Rutter and Alexander Wolff. Augmenting the connectivity of planar and geometric graphs. J. Graph algorithms Appl. 16(2):599-628, 2012. [42] Raimund Seidel. A simple and fast incremental randomized algorithm for computing trapezoidal decompositions and for triangulating polygons. Comput. Geom. Theory Appl. 1(1):51-64, 1991. [43] Michael I. Shamos and Dan Hoey. Geometric intersection problems. Proc. 17th Annu. IEEE Sympos. Found. Comput. Sci., 208-215, 1976. [44] Thomas Shermer and Godfried Toussaint. Characterizations of star-shaped polygons. Tech. Rep. 92-11, School of Computing Science, Simon Fraser University, December 1992. η ftp: fas.sfu.ca pub cs TR 1992 CMPT92-11.ps.gz ι. [45] Wei-Kuan Shih and Wen-Lian Hsu. A new planarity test. Theoret. Comput. Sci. 223(1-2):179-191, 1999. [46] Daniel D. Sleator and Robert Endre Tarjan. A data structure for dynamic trees. J. Comput. Syst. Sci. 26(3):362-391, 1983. [47] Godfried T. Toussaint. Computing geodesic properties inside a simple polygon. Revue d'Intelligence Artificielle 3(2):9-42, 1989. [48] Godfried T. Toussaint. On separating two simple polygons by a single translation. Discrete Comput. Geom. 4(1):265-278, 1989. [49] Wikipedia contributors. Simple polygon. Wikipedia, The Free Encyclopedia. η http: en.wikipedia. org wiki Simple_polygon ι. Last accessed June 26, 2014. [50] Chung-Do Yang, Der-Tsai Lee, and Chak-Kuen Wong. The smallest pair of noncrossing paths in a rectilinear polygon. IEEE Trans. Comput. 46(8):930-941, 1997.

- [ 51 ] Heiner Zieschang. Algorithmen für einfache Kurven auf Flächen. Math. Scand. 17:17-40, 1965.
