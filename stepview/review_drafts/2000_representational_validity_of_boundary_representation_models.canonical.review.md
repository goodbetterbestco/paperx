# 2000 representational validity of boundary representation models

T. Sakkalis, G. Shen, N.M. Patrikalakis*

[missing from original]

## Abstract

Validity is an important property of solid modeling representations. It ensures that representations always describe physically realizable solids, instead of nonsense objects. This paper surveys and supplements the mathematical theory of ideal boundary representation (B-rep) of solids. In particular, it presents a complete set of conditions on representational nodes of a typical B-rep data structure and proves their sufficiency for model validity. Such conditions are useful in invalid model rectification procedures.

## Introduction

Model validity has long been recognized as an important problem in solid modeling theory and CAD CAM CAE practice [1-3]. An invalid model describes a nonsense object which cannot be properly interpreted and thus cannot be realized as a physical artifact. Although validity is a highly desired property of model representations, not all modelers have it. As is well known, validity of boundary representation (B-rep) models is not self-guaranteed. In spite of effort and progress in developing modeling theory and techniques for creating valid B-rep models, models created using today's CAD systems often contain defects —representational features which violate semantics rules of B-rep modelers. In a manifold B-rep model, defects visually appear as gaps, inappropriate intersections, dangling patches, internal walls and inconsistent orientations. Causes of defects exist throughout the entire life cycle of a model, just to name a few, such as pathological behaviors of solid modeling operations, improperly implemented algorithms, precision limitation of the computer, and data exchange. Consequences of defects could be severe. Invalid models may make certain modeling operations fail, create useless analysis results, produce defective products, and cost enormous resources in fixing at the other end of data exchange, and delay the overall design process considerably.

In the early years of solid modeling, validity verification was mostly done by the user, and was error-prone [1]. As the complexity of models grows enormously, it becomes nearly impossible for the human being to visualize defects, and thus automated, or semi-automated (with limited user assistance), validity verification methods are needed in the solid modeling community.

In this paper, we study representational validity of ideal Brep models. In particular, we compile and prove a complete set of sufficient conditions for representational nodes of a typical B-rep data structure. Most of these conditions have appeared in various forms in extant literature, but often in a less complete manner and without a detailed mathematical proof that these conditions lead to a valid solid.

The paper is organized as follows: Section 2 briefly reviews prior research on model validity. Sections 3 and 4 present the mathematical theory of ideal B-rep of solid models. Section 5 first deals with representational validity of ideal B-rep models; next we present sufficient conditions for validity of manifold B-reps and prove that these conditions lead to a valid solid using methods of Geometric Algebraic Topology. Section 6 concludes this paper with comments on the usefulness of these conditions in invalid model rectification procedures.

2. Brief literature review

Fundamental concepts and definitions of solid modeling can be found in Requicha [1], Mäntyla [2], Hoffmann [3], Braid [4], and the literature cited therein. A historical

![Figure 1. Two valid solids.](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-1-p002.png)

*Figure 1. Two valid solids.: Two valid solids.*

overview of solid modeling developments can be found in Braid [5] and Voelcker and Requicha [6]. This section provides a brief summary of prior research work on model validity, especially of manifold B-rep models.

A solid modeler is designed to model a set of mathema tical solids, which form the modeling space \(\mathscr{M}\) of the mode ler. Each element in \(\mathscr{M}\) is an abstraction of a real solid. A modeler consists of representations and a representation scheme. A representation is a finite symbol structure constructed from an alphabet according to syntactical rules. All syntactically correct representations form the representation space \(\mathscr{R}\). A representation scheme is defined as a relation \(s: \mathscr{M} \rightarrow \mathscr{R}\), whose domain \(\mathscr{D} \subset \mathscr{M}\) and whose range \(\mathscr{V} \subset \mathscr{R}\). A valid representation is a representation in \(\mathscr{V}\), see Requicha [1] and Mäntylä [2]. Manifold B-rep models real solids whose mathematical abstractions are \(r\)-sets with 2-manifold boundary [1,2]. An \(r\)-set is a bounded, regular and semianalytic subset in \(\mathbb{R}^{3}\). Almost all man-made solids can be represented by such mathematical descriptions. B-rep uses a collection of two dimensional entities, called faces, properly connected and consistently oriented, to define solid boundaries. Each face is bounded by loops and is embedded on a surface. Each loop is a string of edges, properly connected and consis tently oriented to form a simple closed curve with orienta tion. Each edge is a simple open or closed curve, and embedded on a curve and bounded by two vertices. In addi tion, a shell is defined as a collection of faces whose union is a connected 2-manifold without boundary. See Fig. 5 for the diagram of such a hierarchical structure. Adjacency and incidence relations of these topological entities are referred

![Figure 3. Three valid faces.](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-3-p002.png)

*Figure 3. Three valid faces.: Three valid faces.*

- Faces may intersect only at common edges or vertices.

- Faces around each vertex can be arranged in a cyclical sequence such that each consecutive pair share an edge incident to the vertex.

- Each edge is shared by exactly two faces.

![Figure 2. Two invalid solids.](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-2-p002.png)

*Figure 2. Two invalid solids.: Two invalid solids.*

![Figure 4. Two invalid faces.](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-4-p003.png)

*Figure 4. Two invalid faces.: Two invalid faces.*

are developed along with geometric specification computation algorithms.

In Braid et al. [8], a topological structure is called admis sible if certain conditions are satisfied, mainly the Euler Poincaré formula. Admissibility does not imply validity because the Euler-Poincaré formula is necessary but not sufficient, meaning that a polyhedral model satisfying this formula may not be a 2-manifold [ \(3,4,8\) ]. Mäntylä [7] further proved that any topological polyhedron constructed using Euler operators is topologically valid. For models created using a modeling kernel whose operations are not based on Euler operators, topological structures could be invalid even if the Euler-Poincaré formula is satisfied.

Geometric integrity can be verified by two tests [8]. Local test verifies if underlying curves of edges and coordinates of vertices are consistent with surfaces. Global test checks if there are any surface intersections in the interiors of faces.

1. if \(\sigma_{T} \in K\) then \(\sigma_{U} \in K, \forall U \subset T\), and

## 3 Mathematical preliminaries

A real solid is a material object that occupies a region in 3-space. An abstract solid, therefore, must unambiguously describe the region occupied by the solid, so that it is possible to classify whether a point is inside the region of the solid [13]. Another important characteristic of a real solid is its physical realizability, which refers to the possibility of rebuilding it [14]. On the other hand, this realizability should not be limited by current manufacturing technology.

In the following we state some definitions pertinent for this discussion. For a reference see Refs. [15-17].

A widely accepted definition of solid was given by Requicha [1]: "a solid, denoted as \(r\)-set, is a subset of \(\mathbb{R}^{3}\) that is bounded, closed, regular and semianalytic". This definition captures mathematical characteristics of most real solids of interest, such as mechanical parts. However, this definition allows non-manifold features, such as the contacting edge between two cubes, a feature which is non-manufacturable (see Fig. 2(b)). It is for that reason that many prefer a solid to be a topological manifold [2].

Let \(p \in \mathbb{R}^{n}\) and let \(r>0\). The open ball \(B(p, r)\) of radius \(r\) centered at \(p\) is defined as the set of points \(x \in \mathbb{R}^{n}\) whose distance from \(p\) is less than \(r\). Such an open ball is also called a neighborhood of \(p\). An open halfspace \(\mathbb{R}^{n+}\) is defined as \(\mathbb{R}^{n+}=\left\{\left(x_{1}, x_{2}, \ldots, x_{n}\right) \in \mathbb{R}^{n} \mid x_{i} \geq 0\right\}\) for some \(i\), \(1 \leq i \leq n\). A subset \(A\) of \(\mathbb{R}^{n}\) is open if for every point \(a \in A\)

![Figure 5. Graph representation of the data structure.](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-5-p003.png)

*Figure 5. Graph representation of the data structure.: Graph representation of the data structure.*

there exists an \(r>0\) so that \(B(a, r) \subset A\). A subset \(A\) of \(\mathbb{R}^{n}\) is called closed if its complement \(\urcorner A\) is open. denotes the number of elements of \(T. k\) is called the dimen sion of the simplex \(\sigma_{T}\). A simplicial complex \(K\) is a finite collection of simplices that satisfy the following:

The underlying space of \(K\) is \([K]=\cup_{\sigma \in K} \sigma\), with the induced topology from \(\mathbb{R}^{n}\). A subcomplex of \(K\) is a simpli cial complex \(L \subset K\).

Definition 3.1. Let AC R". The interior Int(A) of A consists of all points a E A such that A contains a neighborhood of a. The closure A is defined as A = \(int(A)\). The boundary of A is Bd(A) = A-Int(A). A shall be called compact if it is bounded and closed.

Definition 3.2. Let \(A_{1}, A_{2}\) be subsets of \(\mathbb{R}^{n}, \mathbb{R}^{m}\), respec tively, and let \(g: A_{1} \rightarrow A_{2}\) be a map. We say that \(g\) is continuous, if for every point \(b \in A_{2}\) and \(r>0\), the inverse image of \(B(b, r) \cap A_{2}\) is equal to \(C \cap A_{1}\), where \(C\) is an open set in \(\mathbb{R}^{n}\). In addition, we say that \(g\) is a homeomorphism if \(g\) is \(1-1\), onto and \(g\) and \(g^{-1}\) are both continuous. In that case we say that \(A_{1}\) and \(A_{2}\) are homeomorphic.

On the other hand, we say that \(N\) is a \(n\)-manifold with boundary if every \(q \in N\) has a neighborhood homeomorphic to

In view of the above, we define an open disk 4 = Int(M),

$$
s= CC, (1)
$$

## 4 Solids and their boundary

Figs. 1 and 2 illustrate several valid and invalid solids. Obviously, for a solid \(S\) we have \(\partial S=S-\operatorname{int}(S)\). In addi tion, thanks to a result from geometric topology, we note that a solid is a triangulable manifold with boundary, and thus it is orientable [17]. Roughly speaking, the latter means that we know precisely its interior as well as its exterior. Notice, also, that the boundary of a solid may not be connected if the solid has cavities.

Definition 4.2. Let \(S\) be a solid. A shell \(C\) of \(S\) is a connected component of \(\partial S\) [7]. For such a \(C\), we define the inner (outer) part of \(C, C^{\mathrm{I}}\left(C^{\mathrm{O}}\right)\), as the interior of the

Notice that since \(C\) is \(a_{2}\)-manifold without boundary sitting in \(\mathbb{R}^{3}\), it is orientable, and thus \(\mathbb{R}^{3}-C\) has precisely two connected components, one bounded and one unbounded.

Remark 4.1. Let \(S\) be a solid. Then, there exists a unique shell \(C_{\mathrm{e}}\), called external shell, so that every other shell of \(S\) is contained in its inner part \(C_{\mathrm{e}}^{\mathrm{I}}\).

Proof. Let \(U\) be the unique unbounded connected compo nent of \(\mathbb{R}^{3}-S\). Let now \(C_{\mathrm{e}}\) be a shell of \(S\) with the property that some point \(p \in C_{\mathrm{e}}\) has a neighborhood that does not meet any other shell of \(S\) and intersects \(U\). Since \(C_{\mathrm{e}}\) is orientable, we see that every point of \(C_{\mathrm{e}}\) has the above property. We now claim that this shell of \(S\) is the only one with this property; for otherwise, \(S\) would not be connected. Finally, if \(C\) is another shell of \(S\) it obviously lies in the inner part of \(C_{\mathrm{e}}\), since the outer part of \(C_{\mathrm{e}}\) is precisely \(U\).

All shells of \(S\), except \(C_{\mathrm{e}}\) shall be called internal. Note from the above remark that Ф(u, v) = (xu, v), y(u, v), zu, v)).

where \(C_{i}\) are the internal shells of \(S\). We next define the so-called faces of a solid, in order to achieve a boundary representation of solids. Face can be defined in an analogous way to a solid, see Mäntylä [7]. The following definition gives a clear description of face topology.

Definition 4.3. A face \(f\) of a solid \(S\) is a non-void subset of \(\partial S\) having the following properties:

- fis a subset of one, and only one, AS surface.

![Figure s](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-s-2-p005.png)

*Figure s: Figs. 3 and 4 illustrate several valid and invalid faces.*

- The interior Int f) in dS is a connected 2-manifold, and

- fis homeomorphic to a (topological sphere 2 minus a finite number of mutually disjoint (nondegenerate) open disks 4, \(C_{2}\), i= 0,1,..,k,k ≥ 0, so that for i‡ j, д4, 0 a4, is either empty or a single point.

The requirement that a face is embedded in one surface is representational rather than mathematical. This also makes an abstract face close to a natural face, which in general is bounded by natural edges manifested by tangential discontinuities. It is also accepted in solid modeling practice that a face has no handles. Indeed, this is the case as definition 4.3(3) shows. Notice that a face is path-connected, and the connectedness of its interior excludes two neighboring faces to be taken as one face. See also Mäntylä [2]. The following remark comes directly from definition 4.3 and is useful for face representation.

Remark 4.2. Let \(f\) be a face of a solid \(S\), and \(k \geq 0\) be as in definition 4.3(3). Then,

- fis homeomorphic to F, where F is the closed unit disk D = Do minus k mutually disjoint (nondegenerate) open disks Di, so that D, C D, for all 1 ≤ i ≤ k, and aD, n aD; is either empty or a single point, for i ‡ j, 0 ≤ i,j = k, and

- The interior of any simple closed curve c E UKo aD, in F, is a subset of Uk, Di

Proof. Indeed, a sphere \(\Sigma\) minus the open disk \(\Delta_{0}\) is (homeomorphic to) the disk \(D\). Further exclusion of the remaining open disks \(\Delta_{i}, 1 \leq i \leq k\) results in the descrip tion of \(F\) in the first bullet. To prove the second assertion let us suppose that \(C_{1}, C_{2}\) are two different connected compo nents of \(F\). Then, we may pick a simple closed curve \(c \in \operatorname{Bd}\left(C_{1}\right)\) so that its interior is just \(C_{1}\). This, however, is a contradiction to definition 4.3(2).

Once a homeomorphism between \(f\) and \(F\) has been established, it is easy to see what the boundary of \(f\) is. Indeed, let \(g: f \rightarrow F\) be a homeomorphism of \(f\) and \(F\). Then

The following remark describes the topology of Bd(f).

```text
Remark 4.3. Let \( x \in \operatorname{Bd}(f) \), and let \( \Delta_{i} \) be an open disk so that \( x \in \partial \Delta_{i} \). Then, we may choose \( r>0 \) so that F1. \( c_{i}=\overline{B(x, r)} \cap \partial \Delta_{i} \) is a simple curve. Moreover, if \( x \in \partial \Delta_{j}, j \neq i \), then \( c_{i} \cap c_{j}=\{X\} \). F2. \( f \cap B(x, r) \) is equal to precisely \( m \) half open disks \( D_{X}^{i}(f) \) if and only if \( x \in \cap_{i=1}^{m} \partial \Delta_{i} \). In addition, \( \Delta_{X}^{i}=\overline{\Delta_{i}} \cap B(x, r) \) is a half open disk, for each \( i \). Moreover,
```

![Figure s](/Users/evanthayer/Projects/paperx/docs/2000_representational_validity_of_boundary_representation_models/figures/figure-s-2-p005.png)

*Figure s: Figs. 3 and 4 illustrate several valid and invalid faces.*

Since that boundary is an 1-manifold without boundary, i.e. a simple closed curve, we may pick an \(r>0\) so that \(c_{i}=\overline{B(x, r)} \cap \partial \Delta_{i}\) is a simple curve. Now, if \(x \in \partial \Delta_{j}, j \neq i\), definition 4.3(3) says that \(\partial \Delta_{j} \cap \partial \Delta_{i}=\{X\}\). Thus, \(c_{i} \cap c_{j}=\{X\}\). we observe that the \(c_{i}\) 's divide the disk \(\sum_{x}(r)\) into precisely \(2 m\) connected regions \(R_{i}^{1}, R_{i}^{2}\), each one of them being a closed disk, whose boundary contain the points \(a_{i}^{1}, a_{i}^{2}\), and \(a_{i}^{1}, a_{i+1}^{1}\), respectively. The proof is now complete.

Notice the similarity of the above formula, with formula (1). Figs. 3 and 4 illustrate several valid and invalid faces. We may now expand the above discussion of the notion of the 'region bounded by loops' so that we can use it in the next section. Let \(\Sigma: \Phi:[0,1] \times[0,1] \rightarrow \mathbb{R}^{3}\) be an \(A S\) surface and let \(c_{j}, j=1, \ldots, m\) be simple closed curves The given orientation(s) on \(\Sigma\) and \(c_{j}\) induce-via \(\Phi^{-1}\) an orientation on \([0,1] \times[0,1]\) and each \(1_{j}\). We can then agree that each of the above oriented closed curves define a region in \([0,1] \times[0,1]\). For each \(1_{j}\) we define the region bounded by \(l_{j}, R\left(l_{j}\right)\) as the subset of \([0,1] \times[0,1]\) that lies to the left of \(l_{j}\) as one is walking on the positive side of \([0,1] \times[0,1]\), along \(l_{j}\) with respect to its orientation. Finally, we define

Now, a loop can be decomposed into edges.

Definition 4.5. An edge \(e\) of a face \(f\) is a subset of \(\operatorname{Bd}(f)\) such that

- It is also a subset of a loop, and

- It is homeomorphic to either a simple closed curve or to an open simple curve.

On the other hand, edges are bounded by vertices:

Definition 4.6. A vertex \(v\) of an edge \(e\) is

- A component of Bd(e), if Bd(e) ‡Ø.

- An arbitrary point in Bd(e) if Bd(e) = Ø.

In general, the underlying geometry of an edge is the intersection curve of the two underlying surfaces of the two faces sharing this edge, and a vertex is the intersection of three or more surfaces.

We next give the definition of boundary representation: definition 4.7. A boundary representation of a solid \(S\) is a collection of faces \(f_{i}, 1 \leq i \leq n\), such that

- Uff = aS, and

- For any if j, tint; = Bd(ti) N Bd(ti.

## 5 Representational validity conditions

### 5.1 Data structure

A typical data structure for B-rep model has a graph structure as shown in Fig. 5. B-rep data structures can be found in Baumgart [10], Mäntylä [2], Weiler [19] and others. Description of the nodes is given below:

- A vertex node is the representation of a vertex. It has a pointer to a node containing Cartesian coordinates.

- An edge node is the representation of an edge. It has two ordered pointers to two vertex nodes, and a pointer to a node containing the geometric representation of a curve, including a binary field specifying the orientation of the edge with respect to the orientation of the curve.

- A loop node is the representation of a loop. It has a collection of pointers, each of which points to an edge node and has a binary field specifying the orientation of the edge in the loop with respect to the orientation of the edge.

- A face node is the representation of a face. It has a collection of pointers, each of which points to a loop node and has a binary field specifying the orientation of the loop in the face with respect to the orientation of the loop. It also has a pointer to a node containing the geometric representation of an AS surface, including a binary field specifying the orientation of the face with respect to the orientation of the AS surface.

- A shell node is the representation of a shell. It has a collection of pointers to face nodes.

The data structure is an adaptation of the STEP file structure [20], and is able to hold non-manifold features, as we assume a given representation could be topologically incorrect.

### 5.2 Sufficient conditions for node validity

Representational validity verification, for a certain data structure like the one in Section 5.1, is a process of verifying that each node in an instance of the data structure is a valid representation of the corresponding topological entity. The following sufficient conditions are compiled from priory work such as [2,3,7,8,9,20], and the discussion in Section 3 and 4.

- \(C_{5}\).1 Vertex node validity. A vertex node is a valid representation of a vertex if it is assigned with the coordinates specifying the position of the vertex in R.

- \(C_{5}\).2 Edge node validity. An edge node is a valid representation of an edge if

- Its two vertex nodes represent points on the curve.

- There exists a path on the curve, connecting these two points in the given orientation.

- The curve does not self-intersect in the interior of the path.

\(C^{5}\).3 Loop node validity. A loop node represents a valid loop if

- The directed graph constructed by taking vertices as nodes and oriented edges as directed arcs, is a simple directed cycle.

- Any two adjacent edges intersect only at their common vertices. Any two non-adjacent edges do not intersect.

- \(C_{5}\).4 Face node validity. A face node represents a valid face if

- All its loop nodes represent loops on the surface.

- The surface does not self-intersect in the interior of the region bounded by the loops, see Eq. (3).

- The region bounded by the loops satisfies Remark 4.2.

\(C^{5}\).5 Shell node validity. A shell node represents a valid shell Cif

- Each face of C has exactly one adjacent face, which also belongs to C, through each of its edges.

- Each vertex vE C has a finite number of incident faces f, E C and (nondegenerate) edges e; E C, 1 ≤ i ≤ m. These incident faces and edges can be arranged in the form of f, - e, - f2 - ... - fmem-fm+1 = f, and e; is a common edge of f, and f+1, for i = 1, ...,m.

- Any two adjacent faces only intersect at their common vertices and or edges. Any two non-adjacent faces do not intersect.

- Faces are consistently oriented.

\(C^{5}\).6 Model node validity. A model node represents a valid B-rep model if

- There exists exactly one external shell.

- Each of the inner shells is properly oriented such that the region it bounds is in the region bounded by the external shell.

- None of the inner shells is in the region bounded by another inner shell.

- Shells do not intersect.

### 5.3 Proof of validity

In this section we will show that whenever the conditions of Section 5.2 are satisfied, then we indeed get a valid solid More precisely, we will prove that when conditions C5.1 to C5.5 are satisfied the result will be a shell. In addition, we will also prove that once we have shells and C5.6 is satisfied, then we will get a solid.

Our approach is primarily based on the fact that a face f that comes from a face node can be given a triangulation Tr This is easily seen from Remark 4.2. Furthermore, using C5.5.1, given any two faces fi and fz, we can always pick triangulations Tr and Ik of 4, f2 such that TiNIk is a triangulation off f2 = Bd(f) N Bd(f2). Now let \(C\) be a shell that comes from a shell node. To this end, we will show that \(C\) is a compact oriented triangulable 2-manifold without boundary. To achieve that, let a be a point of C. Then, there exists a face fso that a € f. If a E Int(f), then a has a neighborhood Na homeomorphic to R?. Since any two faces do not intersect at their interiors, Na is also a neighborhood of a in C Now let a belong to fj, i = 1,2, ...,m, m ≥ 2. In that case we see that a E NBd(fi, for all i. For simplicity, we may always take a to be a vertex of C. Let e1, ez, ..., em be edges of C so that along with the faces f1, .... fm satisfy C5.5.2 in the said order. Since we have a finite number of distinct edges e, coming through the common vertex a, and each e, satisfies C5.5.2, we may pick \(a_{8}>0\) small enough so that if B = \(B(a,8)\)

- F2 of Remark 4.3 is true for r = 8 and for each fi.

- The c; = B N e, are mutually distinct non-closed simple curves, and each c; is a subset of Bd(fi) N Bd(fi+1), and

- c,N c= {a), for it j.

Since f is incident to ej-1 and ej Ci-1 and c, belong to one, and only one, of the above disks, say Da (fi). Call the unique simple oriented curve that is part of the boundary of Da(f) and connects aj-1 and a, without going through a, V-1. Now let = U™t {y-\(\wp\), where am+1 = ay. Then, since the disks Da(f) and the interior of faces are mutually disjoint, respectively, we see that T is a simple curve that belongs to dB, and thus it is unknotted.

We claim that the union of all the above collections N; N= U# {UN;\(\wp\) is an open disk. Indeed, we first note that the boundary of each half open disk Di(f is simply the (simple) closed curve c-1 U Yi-1 U c;. Now, the set Da (fi) U Da(f2) is a closed disk since is the result of gluing together the two disks Di(f) and Da (f2) along their common boundary q. Simple induction shows that is a closed disk with boundary \(\Gamma\). Obviously, \(\operatorname{Int}(\mathscr{D})=N\). This proves the claim.

Since \(C\) consists of a finite number of faces, each of them being a bounded subset of \(\mathbb{R}^{3}, C\) is also compact. In

Theorem 5.1. Let \(C\) be a shell that comes from a shell node satisfying conditions \(\mathbf{C_{5}. 1}\) to \(\mathbf{C_{5}. 5}\). Then \(C\) is a compact oriented triangulable 2-manifold without boundary.

Corollary 5.2. Let \(S\) be a solid that comes from a model node satisfying C5.6. Then \(S\) is a valid solid.

Using the above theorem we see that \(C_{\mathrm{e}}\) is orientable. We give \(C_{\mathrm{e}}\) an orientation so that the region it bounds is its inner part \(C_{\mathrm{e}}^{\mathrm{I}}\). Notice that each of the inner shells of \(S\) is given the proper orientation according to C5.6.2. Since the various shells of \(S\) do not intersect and each one of them is a compact manifold without boundary, then \(S\) is \(a_{3}\)-manifold with boundary its different shells. To finish the proof, it remains to show that \(S\) is connected. Let \(C_{i}\) be the inner shells of \(S, i=1, \ldots, k\). Notice from C5.6.3 and (1) that

$$
S= Ce U C, (5)
$$

Since the internal shells \(C_{i}\) of \(S\) are disjoint and the interior of one does not contain any other, then \(S\) must be connected.

## 6 Conclusion

It is a natural expectation that these conditions would lead to a computational method for model validity verification. B-rep models are defined in a bottom-up manner. If one representational entity is invalid, very little can be said about the validity of a higher level representational entity which uses this entity, except that the latter is invalid, i.e. we could not know how wrong it is. Nevertheless, such conditions are useful in B-rep model defect rectification, because they tell us what is a correct model. This aspect is developed extensively in our continuing work on model rectification [21,22].

## Acknowledgements

Funding for this work was obtained in part from NSF grant DMI-9215411, ONR grant N00014-96-1-0857 and from the Kawasaki chair endowment at MIT. We would like to thank the referees for their comments which improved the paper.

$$
9 = D: (f)
$$

## References

- Requicha AAG. representations of solid objects-theory, methods and systems. ACM Computing Surveys 1980;12(4):437-64.

- Mäntylä M. An introduction to solid modeling. Computer Science Press, 1988.

- Hoffmann CM. Geometric and solid modeling: an introduction. San Mateo, CA: Morgan Kaufmann, 1989.

- Braid IC. Notes on a Geometric Modeller. CAD Group Document 101, Computer Laboratory, University of Cambridge, England, June

- Braid C. Boundary modeling. In: Piegl L, editor. Fundamental development of computer-aided geometric modeling, San Diego, CA: Academic Press, 1993. p. 165-84.

- Volcker HB, Requicha AG. Research in solid modeling at the University of Rochester: 1972-1987. In: Piegl L, editor. Fundamental development of computer-aided geometric modeling, San Diego, CA: Academic Press, 1993. p. 203-54.

- Mäntylä M. A note on the modeling space of Euler operators. Computer Vision, Graphics and Image Processing 1984;26(1):45-60.

- Braid IC, Hillyard RC, Stroud IA. Stepwise construction of polyhedra in geometric modeling. In: Brodlie KW, editor. Mathematical methods in computer graphics and design, London: Academic Press, 1980. p. 123-41.

- Eastman C, Weiler K. Geometric modeling using Euler operators. In: Proceedings of the first Annual Conference on Computer Graphics in CAD CAM Systems, May 1979:248-59.

- Baumgart B. A polyhedron representation for computer vision. In: Proceedings of National Computer Conference, Montvale, NJ, AFIPS Press, 1975:589-96.

- Eastman C, Lividini J, Stoker D. A database for designing large physical systems. In: Proceedings of National Computer Conference, Montvale, NJ, AFIPS Press, 1975:603-11.

- Mäntylä M, Sulonen R. GWB—A solid modeller with Euler operators. IEEE Computer Graphics and Applications 1982;2(7):17-32.

- Requicha AAG, Voelcker HB. Constructive solid geometry. Technical Report TM 25, Production Automation Project, University of Rochester, Rochester, NY, November 1977.

- Requicha AAG. Mathematical models of rigid solid objects. Technical Report 28, University of Rochester, November 1977.

- Croom F. Basic concepts of algebraic topology. New York: Springer, 1978.

- do Carmo PM. Differential geometry of curves and surfaces. Englewood Cliffs, NJ: Prentice-Hall, 1976.

- Moise EE. Geometric topology in dimensions 2 and 3. New York: Springer, 1977.

- Guillemin V, Pollack A. Differential topology. Englewood Cliffs, NJ: Prentice-Hall, 1974.

- Weiler K. Edge-based data structures for solid modeling in curved surface environments. IEEE Computer Graphics and Applications 1985;5(1):21-40.

- U.S. Product Data Association. ANS US PRO IPO-200-042-1994: Part 42—integrated geometric resources: geometric and topological representation, 1994. Shen G. analysis of boundary representation model rectification. PhD thesis, Massachusetts Institute of Technology, Cambridge, MA, February 2000. Shen G, Sakkalis T, Patrikalakis NM. Manifold boundary representation model rectification. In: Proceedings of the 3rd International Conference on Integrated Design and Manufacturing in Mechanical engineering, Montreal, Canada, May 2000. Dr. Sakkalis is an Associate Professor of Mathematics at the Agricultural University of Athens, Greece and a Research Affiliate at MIT (http: deslab.mit.edu DesignLab people takis1.html). He received a Diploma in Mathematics in 1979 from the University of Athens, Greece, and a PhD in Mathematics in 1986 from the University of Rochester, NY. His research interests include computer aided geometric design, computer algebra, geometric modeling and computational geometry. Dr Sakkalis has been a Visiting Scientist at the IBM Thomas J. Watson Research Center, where he worked with the Design Automation Science Project in Manufacturing Research and at the Design Laboratory at MIT. From 1986 to 1990 he was an Assistant Professor of Mathematics at New Mexico State University, while from 1990 to 1994 was an Assistant Professor of Mathematics at Oakland University in Rochester, Michigan. Guoling Shen's research interests include CAD CAM, and computational geometry. He received a BEng degree in Marine engineering in 1988 from Huazhong University of Science and Technology, China, MS degrees in Naval Architecture and Marine engineering and in Mechanical engineering in 1997, and a PhD degree in Computer Aided Design and Fabrication in 2000, all from MIT (http: deslab.mit.edu). Dr. Patrikalakis is the Kawasaki Professor of engineering and Professor of Ocean and Mechanical engineering at MIT (http: oe.mit.edu). He received a Diploma in Naval Architecture and Mechanical engineering in 1977 from the National Technical University of Athens, Greece, and a PhD in Ocean engineering in 1983 from MIT. His research interests include computer aided design and manufacturing, geometric modeling and computational geometry, and distributed information systems (http: deslab.mit.edu, http: fablab.mit.edu).
