# Global Bifurcation Sets and Stable Projections of Nonsingular Algebraic Surfaces

J.H. RIEGER, Fachbereich fiir Informatik, Universit& Karlsruhe, Hamburg, Bodenstedt str. , Hamburg, Germany, Nonsingular Algebraic Surfaces

[missing from original]

## Abstract

The view graph of a surface is a planar graph whose nodes are the stable views (projections) of the surface and whose edges represent ransitional views of codimension one. The space of all directions of orthogonal projection can be identified with the projective plane. The set of "bad" projection directions, associated with the degenerate views of positive codimension, forms a graph in the projective plane (the view bifurcation set). This graph is dual to the view graph and divides the projective plane into a certain number of connected regions whose representatives are the nodes of the view graph. We assume that the projected surface is nonsingular and parameterized by polynomials of degree d. We present an estimate for the number of nodes in the view graph in terms of d and describe symbolic algorithms for computing the bifurcation set and the view graph of a surface from a parametrization.

## Introduction

In the present article we consider the following problem in computational geometry. Let S be a nonsingular surface in \(R_{3}\) defined by some polynomial, and let e ~ p2 denote a direction of projection. For "most" directions f (that is for all directions in p2 except for a set of positive codimension) the orthogonal projection of S onto a plane perpendicular to f will give rise to a smooth apparent contour with isolated cusps and transverse crossing (this follows from classical results of Whitney [1955] and Mather [1973]). The apparent contour of S will, in general, have degenerate singularities for certain "bad" directions f, and the set 23 of such bad directions consists of (in general, singular) curves in p2. This set is called the bifurcation set of the family of orthogonal projections of S. The connected components of p2 \ 23 correspond to directions of projection e which will give rise to equivalent views of the surface S (strictly speaking, this is only true for compact surfaces S--see section 1.2). In the past 10 years a substantial number of investigations of the local behavior of apparent contours in the neighborhood of some point on a surface S have been carried out within the framework of the theory of singularities of smooth mappings. In particular, extensive classifications of degenerate singularities of apparent contours and the bifurcation sets associated with these singularities have been obtained [Arnol'\(d_{1983}\); Gaffney & Ruas 1977; Kergosien 1981; Rieger 1987a, 1990b]. Here we want to consider certain global and algorithmic aspects of this problem, such as: given an algebraic surface S the view bifurcation set ~3 is a semialgebraic curve in p2, are there bounds for the topology of 23 (for the Betti numbers and the number of connected components of p2 \ 23) in terms of the degree of S? Are there algorithms for computing representatives for all the connected components of p2 \ ~, which represent the nodes in the view graph (or aspect graph) of S (in the sense of Koenderink and van Doom [1986; 1986])? These questions will be studied in this article.

In the area of model-based vision one can distinguish between two types of approaches to object recognition: the first aproach uses (partial) 3D data, such as scene edge fragments, vertexes, or surface normals, which can be matched with \(a_{3}\)-D model (the work of, for example, Grimson and Lozano-P~rez [1984] belongs to this class of approaches); whereas in the second approach one tries to match topological descriptions of line drawings that consist of apparent contours and or of the projections of 3D edges with precomputed "characteristic views" associated to the nodes of the view graphs of a set of object models (see, for example, Chakravarty and Freeman [1982], and Goad [1983]. Note that a "characteristic view" represents an equivalence class consisting of views for which the labeling scheme of Malik [1987] would yield the same result. Of course, we do not claim that all approaches to object recognition fit into one of these two categories nor that a combination of the two approaches is not possible! For extensive surveys of model-based vision we refer to Besl & Jain [1985], Chin & Dyer [1986], and Murray [1988]. The construction of view graphs is a subproblem of the second approach. Whereas the other ingredients of an algorithm for recognizing 3D models in a 2D image based on characteristic views, namely the extraction of topologically correct line drawings from images and the matching of (in general, only partially correct) line drawings with characteristic views, have to deal with typical problems in computer vision like noisy measurements, the construction of view graphs from exact surface models (given by parametrizations or by zero sets of functions) is purely a problem of computational geometry.

Matching line drawings with "characteristic v ews" is theoretically possible if the number of "characteristic views" is finite (for practical application one could argue that the number of such views should also be small). If one defines a view of a polyhedral surface to be the line drawing consisting of its visible projected edges then there exists a finite number of "characteristic views" of this surface (in fact at most \(O(n6)\), where n is the number of faces of the polyhedral surface)-- algorithms for computing characteristic views of polyhedral surfaces are described, for example, by Gigus and Malik [1988] and Gigus et al. [1988]. Likewise, for smooth surfaces there exists a finite number of open regions in "view space" [Rieger 1990a] (i.e., the space of all possible centers of projection or the space of all directions of projection) from which equivalent stable views of a given surface are seen (here we can think of a view as the apparent contour or the visible part of the apparent contour of a smooth surface, see below). These open regions in "view space" are separated by some "bad" set corresponding to unstable views of the surface. In section 1.2 we give a somewhat informal introduction to these concepts, where we restrict the discussion to parallel projections of semi-transparent, parameterized surfaces.

### 1.2 Projections of Smooth Surfaces and View Graphs

In this section we recall some basic defmitions and facts about view graphs of smooth surfaces (more details can be found in Callahan and Weiss [1985] and Rieger [1990a], for example). first, we need to distinguish globally stable projections ("views") of smooth surfaces from unstable (or degenerate) ones. To simplify the exposition we suppose that a smooth surface is globally given as a graph of a function Z, so that

$$
S(x, y)=(x, y, Z(x, y)) .
$$

The parallel project projection of \(S\) along the direc tion \(\ell_{0}=(0: 1: 0) \in \mathbf{P}^{2}\) is given by \(f_{\ell_{0}}(x, y)=(x\), \(Z(x, y))\). The critical \(\Sigma\left(f_{\ell_{0}}\right)\) of the projection consists of points \((x, y)\) for which

$$
d f_{\ell_{0}}(x, y)=\left[\begin{array}{cc} 1 & 0 \\ Z_{x}(x, y) & Z_{y}(x, y) \end{array}\right]
$$

merely has rank one, that is, \(\Sigma\left(f_{\ell_{0}}\right)=\left\{(x, y) \in \mathbf{R}^{2}\right.\) : \(\left.Z_{y}(x, y)=0\right\}\). It is easy to see that \(\Sigma\left(f_{\ell_{0}}\right)\) consists of points on the surface \(S\) whose tangent planes contain the direction of projection \(\ell_{0}\) : just consider where the inner product of the vectors \(\left(-Z_{x}(x, y),-Z_{y}(x, y), 1\right)\) along the normal direction to \(S\) and \((0,1,0)\) along \(\ell_{0}\) vanishes. The apparent contour of \(S\) is given by the critical values \(\Delta\left(f_{\ell_{0}}\right):=f_{\ell_{0}}\left(\Sigma\left(f_{\ell_{0}}\right)\right)\) of the projection.

Example: Consider the quartic surface \(Z(x, y)=x y+y^{4}-y^{2}\) projected along \(\ell_{0}=(0: 1: 0)\). The critical set is the zero set of \(Z_{y}(x, y)=x+4 y^{3}- 2 y\), and the apparent contour is given by

![Figure 1. The critical set (to the left) and the apparent contour (to the right).](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-1-p003.png)

*Figure 1. The critical set (to the left) and the apparent contour (to the right).: The critical set (to the left) and the apparent contour (to the right).*

The apparent contour has ordinary cusps (or Whitney cusps) at y = +1. 6 and a transverse double point at y = _+ 1. 2 (see fig. 1). Here we use the following terminology. Recall that an ordinary cusp of a parameterized plane curve at t = 0 is given by c~(t) = (\(t_{2}\), t3), whereas the Whitney cusp is equivalent o a map f(x, y) = (x, xy + y3) whose curve of critical values \(A(f)\) has an ordinary cusp at the origin (see section 2.2). We can in fact use the two terms interchangeably without risk of confusion as f : \(R_{2}\) ~ \(R_{2}\) has a Whitney cusp if and only if \(A(f)\) has an ordinary cusp. We call a double point transverse if the two branches of the curve have distinct tangent lines at the point of intersection.

We can now give a preliminary definition of a stable view of a smooth surface (see section 3 for technical details). definition: A projection \(f_{\ell}\) of a smooth surface along \(\ell \in \mathbf{P}^{2}\) is globally stable if the apparent contour \(\Delta\left(f_{\ell}\right)\) has only Whitney cusps and transverse double points as its singular points and has no singular points "at infinity".

(The apparent contour of a compact surface is always the union of closed curves automatically satisfying the second requirement of this definition.)

We say that a projection direction \(\ell \in \mathbf{P}^{2}\) is "bad" if \(f_{\ell}\) is not globally stable. Let \(\Delta \subset \mathbf{P}^{2}\) denote the set of such "bad" directions. (In the later sections of this article we will distinguish between the following com ponents of \(\Delta\) : the so-called bifurcation set \(\mathfrak{B}\) consisting of projection directions for which the apparent contour has singular points different from cusps and transverse double points and the set © corresponding to singular points "at infinity." Hence \(\Delta=\mathfrak{B} \cup \mathfrak{C}\), where \(\mathbb{C}\) may be nonvoid for projections of noncompact surfaces, see above remark.) It follows from (a minor modification of) a result of Mather [1973] that for any smooth sur face \(S\) the set \(\Delta\) has positive codimension in \(\mathbf{P}^{2}\) (i.e., is at most 1-dimensional). Assuming that the surface \(S\) is generic (we will not give a precise definition of

We can now define the view graph of a smooth sur face to be the graph in \(\mathbf{P}^{2}\) which is dual to the "bad" set \(\Delta\). This means the following: let \(\left\{\Gamma_{1}, \ldots, \Gamma_{k}\right\}\) denote the connected components of \(\mathbf{P}^{2} \backslash \Delta\) and let \(\left\{\ell_{1}, \ldots, \ell_{k}\right\}\) be a set of "sample points" \(\ell_{l} \in \Gamma_{l}\). Then the view graph \(G=V \times E\) is a graph in the projective plane having \(V=\left\{\ell_{1}, \ldots, \ell_{k}\right\}\) as its set of nodes and

1-dimensional branch of A} as its set of edges. The set of stable projections \(\left\{f_{\ell_{1}}\right.\), \(\left.\ldots, f_{\ell_{k}}\right\}\) contains all "characteristic views" of the sur face \(S\) (the concept of "characteristic views" is due to Chakravarty and Freeman [1982]).

Example: the view graph in \(\mathbf{P}^{2}\) of a torus. Follow ing Callahan and Weiss [1985], we can consider the view graph of the torus on the "viewing sphere." Each point on the sphere represents a direction of parallel projection onto the tangent plane to the sphere at this point. Figure 2 shows the viewing sphere for the torus together with the curves of bad projection directions. The sphere contains six connected regions, and each region consists of projection directions for which the projection of the torus has neither cusps nor crossings (A), four cusps and two crossings (B), or four cusps and no crossing (C). The regions are separated by the curves of the view bifurcation set \(\mathfrak{B}\) which correspond to degenerate projections of the torus: the degeneracies in this case are double swallowtail transitions, tangen tial crossings of the apparent contour, and contour lines being two to one (side view of torus). The set C is empty because of the compactness of the torus.

Each direction of projection is represented by two points on the sphere, because projecting along the direc tions \(\ell\) and \(-\ell\) gives identical views of semitransparent

![Figure 2. The view sphere of the toms.](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-2-p004.png)

*Figure 2. The view sphere of the toms.: The view sphere of the toms.*

$$
(x, y) \mapsto(X(x, y), Y(x, y), Z(x, y)),
$$

surfaces (for opaque surfaces such pairs of antipodal points can be used to represent front and back views of the surface). Hence we can identify pairs of antipodal points on the sphere so that the parameter space of the projection directions becomes the projective plane \(\mathbf{P}^{2}\). We describe \(\mathbf{P}^{2}\) by a closed disk in the plane: imagine that the boundary of the disk corresponds to the equator of the sphere and that the interior of the disk corresponds to points in the northern hemisphere. Alternatively, we can select any great circle and one of the half spheres in the complement of the circle to correspond to the boundary and interior points of the disk, respectively. Figure 3 shows two such choices: the disk boundaries to the left and to the right correspond to the equator and to some line of longitude, respectively. Recall that antipodal points on the boundary of the disk are iden tified, so that the number of connected regions is three in both cases. For each connected region we can select one point as representative-the view associated with the projection direction represented by this point has been called a "characteristic view" by Chakravarty and Freeman [1982]. The representatives of the connected regions are the nodes in the view graph, and the nodes are connected by edges that indicate the view transitions (these edges are given by the dotted lines in figure 3).

### 1.3 Computing View Graphs

```text
Here we consider the following problem. Let S be a nonsingular algebraic surface given by a parametrization where X, Y, Z are polynomials of degree less than or equal to d. We show that the view graph G = V × E of S in p2 has at most O(d 48) nodes. For surfaces parametrized by polynomials X, Y, Z with rational coefficients we describe a symbolic algorithm for computing the view graph. Representing the space of projection directions p2 by a closed disk in the plane, the algorithm produces exactly one sample point with rational coordinates for each connected region of p2 \ A.
```

Roughly speaking, the algorithm consists of three steps. Let

$$
F: \mathbf{P}^{2} \times \mathbf{R}^{2} \rightarrow \mathbf{P}^{2} \times \mathbf{R}^{2}, \quad(\ell ; x, y) \mapsto\left(\ell, f_{\ell}(x, y)\right)
$$

be the family of all parallel projections \(f_{\ell}\) of a given surface \(S\). From singularity theory we have systems of "recognition equations,"

$$
p_{j}\left(\ell, x_{1}, y_{1}, \ldots, x_{t}, y_{t}\right)=0, \quad j=1, \ldots, m
$$

which vanish if and only if \(f_{\ell}\) is an unstable projection of \(S\) with critical value \(f_{\ell}\left(x_{1}, y_{1}\right)=\ldots=f_{\ell}\left(x_{t}, y_{t}\right)\). The \(p_{j}\) define a closed algebraic set \(\tilde{\Delta} \subset \mathbf{P}^{2} \times \mathbf{R}^{2 t}\) whose projection onto the first factor gives the set of "bad" projection directions \(\Delta \subset \mathbf{P}^{2}\). The steps of our algorithm are then as follows:

- Eliminate the "surface parameters" xa, Ya. . . . . Yt between the pj. The resulting equations define, in general, singular algebraic curves A in p2.

- Compute the connected components of p2 \ A using a modified version of Collins' cylindrical a gebraic decomposition.

- The projection of an algebraic set A \(C^{p2}\) × R2t is, in general, merely semialgebraic (by the TarskiSeidenberg theorem--recall that a semialgebraic set is defined by polynomial equalities and inequalities). Hence A C A may be semialgebraic, so we have to delete branches of A that do not extend to real solutions of the pj and merge regions of pZ \

$$
\begin{aligned} \left\{(X, Y, Z) \in \mathbf{R}^{3}: g_{i}(X, Y, Z)=\right. & 0\} \\ & i=1, \ldots, n \end{aligned}
$$

separated by such branches. This gives us the com ponents \(\mathbf{P}^{2} \backslash \Delta\) of the view graph of \(S\). We now indicate some modifications of the algorithm which become necessary if one allows certain other classes of surfaces, central projections, or opaque objects.

1.3.1 Other Classes of Surfaces. The "recogmtion equations" pj are valid also for nonsingular surfaces parametrized by C=-functions (C ~ = infinitely differentiable), but the pj will then be merely C = in the surface parameters. However, already the first step of our algorithm, the elimination of the surface parameters, requires that the pj be polynomials. It might be possible to obtain an approximate view graph algorithm for infinitely differentiable or for analytic surfaces by studying the zero-sets of the pj by numerical methods.

Examples of approximate view graph algorithms are the brute force method of tesselating the view sphere (as in the work of Goad [1983] and of Fekete and Davis [1984]) and the work of Koenderink (personal communication, see also Koenderink [1986]), on numerical computations of the asymptotic ray map. If the resolution of the view sphere tesselation r the distance between points on the projected surface at which the asymptotic directions are computed are not increased as a function of the degree of the surface, that is, according to an increase of the topological complexity of the problem, many characteristic views of the surface will be missed. However, this author is not aware of any results that would indicate how the probability of missing characteristic views in the approximate view graph algorithms is related to what one knows a priori about the projected surface. Our exact algorithm avoids this difficulty at the expense of high computational cost (this is typical for symbolic algorithms). We will restrict the following discussion to (exact) symbolic view graph algorithms for algebraic surfaces.

An algebraic surface can be defined, as above, by a parametrization or as a zero set of a polynomial. We also assume that the polynomials defining a surface have rational coefficients so that the input of the view graph algorithm consists of a finite number of nonzero rational numbers.

The algebraic surfaces for which symbolic view graph algorithms could be designed belong to the following classes.

- Piecewise smooth zero-sets: here S is the union of n nonsingular zero-sets

intersecting along certain "crease" curves.

- Piecewise smooth parametrized patches: here S is the union of n nonsingular parametrized patches

$$
\begin{aligned} (x, y) \mapsto\left(X_{i}(x, y), Y_{i}(x, y), Z_{i}(x, y)\right) & \\ i & =1, \ldots, n \end{aligned}
$$

intersecting along certain crease curves.

- Piecewise linear, i.e., polyhedral, surfaces.

- Nonsingular zero-sets: case n -- 1, of I.

- Nonsingular parametrized surfaces: case n = 1 of II.

- Nonsingular surface of revolution with algebraic generating curve.

Classes II to VI are special cases of I. In fact, if "~" denotes "specializes to," we have the following:

Note that we can define a parametrized surface ( \(X(x\), \(y), Y(x, y), Z(x, y))\) as a zero set by eliminating \(x, y\) between

$$
\begin{aligned} X(x, y)-X & =Y(x, y)-Y \\ & =Z(x, y)-Z=0 \end{aligned}
$$

while it is not possible to globally parametrize com pact zero-sets, like \(X^{2}+Y^{2}+Z^{2}-1=0\), by poly nomials. Likewise, a surface of revolution

$$
(x, y) \mapsto(\cos x f(y), \sin x f(y), g(y))
$$

whose generating curve \(y \mapsto(f(y), g(y))\) is algebraic (and where \(f(y)>0, f^{\prime}(y)^{2}+g^{\prime}(y)^{2}>0\) ) can be defined as zero-set by eliminating \(y\) between

$$
f(y)^{2}-X^{2}-Y^{2}=g(y)-Z=0
$$

For surfaces of Type III and VI there exist exact view graph algorithms. We have already mentioned the work on piecewise linear (polyhedral) surfaces [Gigus \& Malik 1988; Gigus et al. 1988] in 1.1. algorithms for surfaces of revolution have been described in [Eggert \& Bowyer 1989; Kriegman \& Ponce 1990]. Here the set of "bad" projection directions \(\Delta\) is very simple, it consists of concentric circles on the viewing sphere (recall the example of the torus). The reason for this is that the angle (modulo \(\pi\) ) between the projection direction and the axis of revolution determines a view of a surface of revolution-hence one can restrict the parameter space of relevant projection directions from \(\mathbf{P}^{2}\) to \(\mathbf{P}^{1}\). The bad projection directions are then points in \(\mathbf{P}^{1}\) (and no longer curves in \(\mathbf{P}^{2}\) ), and the connected line intervals in \(\mathbf{P}^{1}\) in the complement of these points, which correspond to the nodes in the view graph, can be easily determined.

The nonsingular parametrized surfaces (i.e., type V) considered here typically have more complicated view graphs. Here the set of "bad" projection direc tions is, in general, the union of singular curves in \(\mathbf{P}^{2}\)-this is also a typical feature of the more-general surface classes I, II, and IV. In fact, several steps of our algorithm remain unchanged if one considers the classes I, II, IV. In an extension of the present algorithm one has to face the following problems.

However, the additional singularities that can arise in such projections were classified by Rieger [1987b], Callahan (personal communication), and Tari [1990] (the latter classification being the most com plete). In these classifications one has to impose cer tain restrictions on how the surfaces can intersect; for example, one might assume that a pair of surfaces inter sects transversely along the "crease" curve and that no more than three surfaces meet in a point. For such piecewise smooth surfaces one can add certain systems of recognition equations which "detect" the degenerate projections of a neighborhood of a "crease" curve us ing the results of the classifications. For the additional recognition equations \(p_{j}\) we then just follow the steps 1 to 3 of our algorithm.

The projection of a nonsingular zero-set \(S\) (i.e., type IV) is, in general, not given by a globally defined map \(f_{\ell}: \mathbf{R}^{2} \rightarrow \mathbf{R}^{2}\). One can, of course, find local param etrizations \(f_{\ell}: U_{i} \rightarrow \mathbf{R}^{2}\) for some open neighborood \(U_{i}\) of each point on \(S\), and the recognition equations \(p_{j}\) would then define subsets \(\tilde{\Delta}_{l}\) of some open neighbor hood of \(\mathbf{P}^{2} \times \mathbf{R}^{2 t}\). However, combining the \(\tilde{\Delta}_{i}\) to ob tain global information about \(\tilde{\Delta}\) may be computationally intractable. Another approach is based on the fact that each degenerate projection corresponds to some line grazing the projected surface in some special way: for example, two branches of the apparent contour meet tangentially if and only if the projection direction \(\ell\) is parallel to a line grazing the surface in two distinct points whose normals are parallel. For a zero-set

Now replace in step 1 of our algorithm the \(p_{j}\) by the equations above (and by systems of equations that "detect" other degenerate projections) and eliminate \(\lambda\) and \(p\)-the other steps remain unchanged.

A view graph algorithm for piecewise smooth zero sets (i.e., type I) requires a combination of the mod ifications of our algorithm just described for surfaces of type II and IV. Here is a conjecture concerning the complexity of the view graph of type I surfaces. If a piecewise smooth zero-set is the union of \(n\) smooth zero-sets of degree at most \(d\), then there are at most \(O(\rho(d, n))\) nodes in the view graph, where \(\rho\) is a polynomial in \(d, n\). (Note that for \(d=1\) one has at

1.3.2 Central Projections. The set \(\Delta\) of "bad" centers of projection of a given surface is, in general, a hyper surface in \(\mathbf{R}^{3}\). Taking sample points of the connected components of \(\mathbf{R}^{3} \backslash \Delta\) as the set of nodes and pairs of sample points of components of \(\mathbf{R}^{3} \backslash \Delta\) that are separated by a 2-dimensional cell of \(\Delta\) as the set of edges we again obtain a view graph that can be em bedded in the plane. Stewman and Bowyer [1988] have described a view graph algorithm for polyhedral sur faces under central projection. We have recently ex tended our algorithm for non-singular, parametrized algebraic surfaces to central projection. The recognition equations \(p_{j}\) in step 1 for central projection are now rational functions, and the determination of the con nected components in the complement of a hypersur face in \(\mathbf{R}^{3}\) (step 2) is more difficult than in the plane curve case. So far we have no estimate for the number of nodes in the view graph for central projection.

1.3.3 Opaque objects. In this article we assume that the occluded parts of the apparent contour are visible. Most real-world surfaces, however, are the boundaries of opaque objects. But the transition from the view graph of a semitransparent surface to that of an opaque surface does not present a major problem. In the opaque case we have to consider the entire view sphere (because projection directions corresponding to antipodal points will, in general, give rise to different views) and we compute a subgraph of the view bifurcation set by deleting edges that correspond to hidden transitional views (see Rieger [1990a]). Whether a transitional view singularity ishidden or not can be decided by symbolic computations.

### 1.4 Contents of the Remaining Sections

In section 2 we introduce a convenient global param etrization for the totality of views of a smooth algebraic surface, which is given by a multiparameter family of polynomial mappings from the plane into the plane. In section 3 we define certain real algebraic varieties \(\tilde{\mathfrak{B}}\) which project into the various components of the view bifurcation set \(\mathfrak{B}\), and we present some upper bounds on the topological complexity of \(\mathfrak{B}\) in terms of the degree of the projected surface \(S\). In section 4 we describe symbolic algorithms for computing the defin ing equations of \(\mathfrak{B}\) from a parametrization of \(S\), and in section 5 we describe a way of computing the curves \(\mathfrak{C} \subset \mathbf{P}^{2}\) which correspond to singularities of the ap parent contour "at infinity." In section 6 we present a symbolic algorithm for finding representatives of the connected components of \(\mathbf{P}^{2} \backslash(\mathfrak{B} \cup \mathfrak{C})\) and the cor responding "characteristic views" of \(S\). The algorithms of sections 4,5, and 6 run in polynomial time (where the degree of the polynomial depends on the degree of the projected surface). Finally, in section 7, we apply the algorithm to a simple example surface and men tion some connections between certain geometric fea tures of a surface and its view bifurcation set. An in dex of frequently used symbols is contained in section 8.

$$
\begin{array}{ll} A=\cos \alpha \sin \frac{\omega}{2} & B=\cos \beta \sin \frac{\omega}{2} \\ C=\cos \gamma \sin \frac{\omega}{2} & D=\cos \frac{\omega}{2} \end{array}
$$

## 2 A Global Parametrization of the Set of All Orthogonal Projections of a Surface

$$
\begin{aligned} & R=\left(\begin{array}{cc} D^{2}+A^{2}-B^{2}-C^{2} \\ 2(A B+C D) \\ 2(A C-B D) \end{array}\right. \\ & \left.\begin{array}{cc} 2(A B-C D) & 2(A C-B D) \\ D^{2}+B^{2}-C^{2}-A^{2} & 2(B C-A D) \\ 2(B C+A D) & D^{2}+C^{2}-A^{2}-B^{2} \end{array}\right) \end{aligned}
$$

Let \(S: \mathbf{R}^{2} \rightarrow \mathbf{R}^{3}\) be a polynomial parametrization of a smooth surface, which, in some convenient choice of coordinates, is given as a graph of a function

$$
S(x, y)=(x, y, Z(x, y))
$$

Except for one minor change concerning the definition of \(\tilde{B}_{5}\) (see section 3), everything below will also work without modifications for parametrized surfaces where \(X, Y, Z \in \mathbf{R}[x, y]\), which are smooth and do not have self-intersections. Next, we need a param etrization of the family of orthogonal projections of \(S\) onto a bundle of (projection) planes

$$
\begin{aligned} & F: S^{2} \times \mathbf{R}^{2} \rightarrow T S^{2} \\ & (\ell ; x, y) \mapsto[\ell ; S(x, y)-(S(x, y) \cdot \ell) \ell] \end{aligned}
$$

where the projection directions \(\ell\) are represented by points on the 2-sphere (note, however, that the projec tions along \(\ell\) and \(-\ell\) are identical; we hence obtain the projective plane as parameter space by identifying anti podal points on the 2-sphere). For computational rea sons we want a parametrization of \(F\) by algebraic equa tions. Rather than projecting onto a bundle of planes, we keep the direction of projection (and hence the pro jection plane) fixed and instead change the orientation of the surface \(S\) relative to the projection direction. So let the \(Y\)-direction be the direction of projection ( \(X, Y\), \(Z\) being the coordinates in \(\mathbf{R}^{3}\) ). We parametrize an ele ment of \(S O(3)\) by its Euler parameters [Klein 1922]. Let \(\alpha, \beta\), and \(\gamma\) denote the angles between the axis of rotation and the coordinate axes \(O X, O Y\), and \(O Z\), and let \(\omega\) denote the magnitude of rotation. The Euler parameters are then given by

which are not independent, because clearly A 2 + \(B_{2}\) + \(C^{2}\) + \(D_{2}=1\). A rigid rotation of the surface \(S(x,y)\) = (x, y, \(Z(x,y)\)) is then given by

$$
\left[\begin{array}{c} \bar{X} \\ \bar{Y} \\ \bar{Z} \end{array}\right]:=R \cdot\left(\begin{array}{c} x \\ y \\ Z(x, y) \end{array}\right)
$$

where

Note that the rotation of \(S\) about the projection direc tion, \(Y\), doesn't change the apparent contour of \(S\), hence we may choose \(B=0\).

The orthogonal projection of a point \((\bar{X}, \bar{Y}, \bar{Z})\) on \(S\) along \(Y\) is given by \(\pi(\bar{X}, \bar{Y}, \bar{Z})=(\bar{X}, \bar{Z})\) Hence,

$$
S(x, y)=(X(x, y), Y(x, y), Z(x, y))
$$

relation \(A^{2}+C^{2}+D^{2}=1\), we obtain an algebraic 2-parameter family of projections of \(S\), where

$$
\begin{aligned} & f(A, C, D, x, y)=\binom{u}{v} \\ & \quad:=\binom{\left(D^{2}+A^{2}-C^{2}\right) x-2 C D y+2 A C Z(x, y)}{2 A C x+2 A D y+\left(D^{2}+C^{2}-A^{2}\right) Z(x, y)} \end{aligned}
$$

The set {f(A, C, D, x, y) : (x,y) ~ \(R_{2}\),\(A_{2}\) + \(C_{2}\) + \(D_{2}=1\)} corresponds to the totality of views of the surface S. There is, however, some redundancy in this representation of views. Note that the rotations of S by an angle 0~+ iTr, i ~ Z, give rise to identical apparent contours (for odd i the contours are identical modulo a reflection in the projection plane about the line spanned by the axis of ratoation). Hence we identify points on the sphere \(S_{2}\) = {\(A_{2}\) + \(C_{2}\) + \(D_{2}=1\)} by putting

The quotient space \(S^{2} / \sim=\mathbf{P}^{2}\) is given by the restric tion of \(S^{2}\) to the closed disk

$$
\begin{aligned} \mathfrak{D}= & \left\{(A, C, D) \in S^{2}:\right. \\ & \left.0 \leq A^{2}+C^{2} \leq 1 / 2 \leq D^{2} \leq 1, D>0\right\} \end{aligned}
$$

Also, note that, under the identification above, the northpole on \(S^{2}\) is equivalent to the equator and to the southpole, whereas any other point \(p\) is equivalent to exactly three other points, which lie on a great circle through the northand southpole (see figure 4). Restric tion to the disk \(\mathfrak{D}\) removes this redundancy, so that each line of projection \(\ell \in \mathbf{P}^{2}\) is represented by exactly one point in \(\mathfrak{D}\). Note that the view sphere of figure 2 cor responds to a half sphere of the sphere of Euler param eters shown in figure 4 (where the bounding great cir cle of the half sphere has to be contracted to a point).

## 3 The View Bifurcation Set and Its Topological Complexity

![Figure 4. Identification of points on the unit sphere of Euler parameters.](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-4-p008.png)

*Figure 4. Identification of points on the unit sphere of Euler parameters.: Identification of points on the unit sphere of Euler parameters.*

$$
\begin{aligned} & F: S^{2} \times \mathbf{R}^{2} \rightarrow S^{2} \times \mathbf{R}^{2} \\ &(A, C, D ; x, y) \mapsto(A, C, D, f(A, C, D, x, y)) \end{aligned}
$$

of section 2). Now, setting \(\ell=(A, C, D)\), we define the set \(\tilde{\mathfrak{B}}\) to be the algebraic closure of

$$
\begin{aligned} & (A(\alpha, \omega), C(\gamma, \omega), D(\omega)) \\ & \quad \sim(A(\alpha, \omega+i \pi), C(\gamma, \omega+i \pi), D(\omega+i \pi)) \end{aligned}
$$

$$
\left\{(\ell, T) \in S^{2} \times \mathbf{R}^{2 t}: f(\ell, T)\right.
$$

Let \(\pi: S^{2} \times \mathbf{R}^{2 t} \rightarrow S^{2}\) denote the projection onto the first factor, then the "view bifurcation set" of a sur face \(S\) is given by \(\mathfrak{B}=\pi(\tilde{\mathfrak{B}})\). From the local classifica tion of monogerms (i.e., \(t=1\) ) and multigerms of maps first, we need some basic facts about singularities of maps from the plane to the plane. As above, let \(f(\ell\), \(p)=(u(\ell, p), v(\ell, p))\) be a map of the plane at \(p=(x, y)\) that depends on the parameters \(\ell=(A, C, D)\).

$$
\Sigma\left(f_{\ell}\right)=\left\{p \in \mathbf{R}^{2}: \operatorname{rank} d f_{\ell}(p)<2\right\}
$$

where the rank of \(d f_{\ell}(p)\) is less than two if and only if \(J(\ell, p):=u_{x}(\ell, p) v_{y}(\ell, p)-u_{y}(\ell, p) v_{x}(\ell, p)=0\). Geometrically the critical set corresponds to points \(p\) on the surface \(S\) whose tangent planes contain the direction of projection \(\ell\) (also note that rank \(d f_{\ell}(p)\) is always one or two for projections of smooth surfaces). The image of the critical set under \(f_{\ell}(p)\) is called the apparent contour of \(S\). The critical set \(\Sigma\left(f_{\ell}\right)\) is smooth at ( \(\ell, p\) ) if \(\nabla J(\ell, p) \neq 0\). Let \(\phi(\ell, p)\) be a family of plane curves giving a local parametrization of the critical sets \(J(\ell, p)=0\) such that \(\phi(\ell, 0)=(\ell, p)\). The tangent vectors \(d \phi(\ell, t) / d_{t}=V(\phi(\ell, t))\) at \(t=0\) are given by

Now consider the family of apparent contours of \(S\) (the critical values of \(f_{\ell}\) ), which are, locally near \(p\), given by \(f_{\ell} \circ \phi_{\ell}(t)\). The apparent contour is smooth at \(p\) if and only if

The apparent contour has an ordinary cusp at ( \(\ell, p\) ) iff \(J(\ell, p)=\nabla_{V_{\ell}} f_{\ell}(p)=0\) and \(\nabla_{V_{\ell}} \nabla_{V_{\ell}} f_{\ell}(p) \neq 0\) (clearly, \(\nabla_{V_{\ell}} f_{\ell}(p)=\nabla_{V_{\ell}} \nabla_{V_{\ell}} f_{\ell}(p)=0\) corresponds to points on the apparent contour where \(\left.d\left(f_{\ell} \circ \phi_{\ell t}\right)\right) / d_{t}=d^{2}\left(f_{\ell} \circ \phi_{\ell}(t)\right) / d t^{2}=0\), that is, to higher-order cusps).

A map-germ \(f_{\ell}\) at \(p\) is stable if, roughly speaking, there is an open neighborhood \(U\) of \(\ell\) in \(\mathbf{P}^{2}\) such that for all \(u \in U\) there exists some point \(q\) near \(p\) such that \(f_{u}(q)=h \circ f_{\ell} \circ k^{-1}(p)\) (where \(h\) and \(k\) are germs of diffeomorphisms of the plane). It was one of the earliest results in singularity theory that a stable map of the plane is locally either a regular point, a fold (where the apparent contour is smooth), or an ordinary cusp (see Whitney [1955]). To these local singularities, the fold and the cusp, we have to add one stable multilocal singularity, namely the transverse fold crossing, to ob tain a complete list of stable singularities of mappings from the plane to the plane. To get a transverse fold crossing of the apparent contour, the following condi tions have to be satisifed for two distinct points \(p_{1}\) and \(p_{2}\) on a surface \(S(p)=(p, Z(p))\) :

$$
N\left(p_{1}\right) \neq \lambda N\left(p_{2}\right), \quad \lambda \in \mathbf{R} \backslash\{0\}
$$

where \(N(p)\) denotes the surface normal at \(p\).

There are six (resp. five) types of degenerate singularities of codimension one of real (resp. complex) mappings from the plane to the plane (see, for example, Kergosien [1981]). The critical values (or apparent

$$
V(\ell, p)=\left(-J_{y}(\ell, p), J_{x}(\ell, p)\right)^{T}
$$

contours) of these codimension one singularties and of their deformations are shown in figure 5. The projec tion directions \(\ell\) that correspond to these singularities generically consist of (semialgebraic) curves in \(\mathbf{P}^{2}\), and the more degenerate singularities (of codimension greater than one) are contained in the closure of these semialgebraic sets. This closed semialgebraic set in \(\mathbf{P}^{2}\) is the bifurcation set \(\mathfrak{B}\), which we view as a spherical curve in \(\mathbf{R}^{3}\) (that is \(\mathfrak{B} \subset S^{2} \subset \mathbf{R}^{3}\) ). (Note that we don't consider the affine cone over \(\mathfrak{B}\) via the standard embedding of \(\mathbf{P}^{2}\) in \(\mathbf{R}^{3}\); our parametrization of projec tions \(f_{\ell}\) does not, in general, lead to homogeneous defining equations of \(\mathfrak{B} \subset \mathbf{R}^{3}\).) Then there are varieties \(\tilde{\mathfrak{B}}_{l} \subset \mathbf{R}^{3} \times \mathbf{R}^{2 t}, i=1, \ldots, 5\), whose pro jections onto \(\mathbf{R}^{3}\) yield the components of \(\mathfrak{B}\). The \(\tilde{\mathfrak{B}}_{i}\) are given by the defining equations of the various codimension-one singularities of the projection map \(f(\ell\), \(p\) ), which are local, bilocal, or trilocal ( \(t=1,2\), or 3). In the following we use the notation introduced above, where \(\ell=(A, C, D)\) are the "orientation param

$$
\begin{aligned} \frac{d}{d t}\left(f_{\ell} \circ \phi_{\ell}(0)\right) & =(d f)_{\phi_{\ell}(0)} \circ \frac{d \phi_{\ell}(0)}{d t} \\ & =\nabla_{V_{\ell}} f_{\ell}(p) \neq 0 \end{aligned}
$$

The first set \(\tilde{\mathfrak{B}}_{1}\) corresponds to degenerate singularities where the projection map \(f(\ell, p)\) has a singular critical set \(\Sigma\) at \(p\). The corresponding codimension-one singularities of \(f(\ell, p)\) are known as the beakto-beak and the lip-singularity (which are equivalent as complex maps but distinguished as real maps). We have

$$
f\left(\ell, p_{1}\right)=f\left(\ell, p_{2}\right), \quad J\left(\ell, p_{\imath}\right)=0, \quad i=1,2
$$

$$
\begin{aligned} \tilde{\mathfrak{B}}_{1}:= & \left\{(\ell, p) \in \mathbf{R}^{3} \times \mathbf{R}^{2}: J(\ell, p)\right. \\ & \left.\quad=J_{x}(\ell, p)=J_{y}(\ell, p)=|\ell|^{2}-1=0\right\} \end{aligned}
$$

where (as one easily calculates from the definition of f(f, P)) where \(\operatorname{deg} J=d+1\), which is the highest degree among the defining equations of \(\tilde{\mathfrak{B}}_{1}\).

The set \(\tilde{\mathfrak{B}}_{2}\) corresponds to swallowtail singularities or worse (where worse means of codimension greater than one) at \(p\), and is defined as follows:

$$
\begin{array}{r} \tilde{\mathfrak{B}}_{2}:=\left\{(\ell, p) \in \mathbf{R}^{3} \times \mathbf{R}^{2}: J(\ell, p)=|\ell|^{2}-1=0,\right. \\ \left.\nabla_{V_{\ell}} f(\ell, p)=\nabla_{V_{\ell}} \nabla_{V_{\ell}} f(\ell, p)=(0,0)^{T}\right\} \end{array}
$$

$$
\begin{array}{r} \tilde{\mathfrak{B}}_{4}:=\overline{\left\{\left(\ell, p_{1}, p_{2}\right) \in \mathbf{R}^{3} \times \mathbf{R}^{4}: f\left(\ell, p_{1}\right)-f\left(\ell, p_{2}\right)\right.} \\ \frac{=\nabla_{V_{\ell}} f\left(\ell, p_{1}\right)=(0,0)^{T}}{\left.J\left(\ell, p_{i}\right)=|\ell|^{2}-1=0, \quad i=1,2 ; p_{1} \neq p_{2}\right\}} \end{array}
$$

where \(\operatorname{deg} \nabla_{V_{\ell}} \nabla_{V_{\ell}} f(\ell, p)=3 d+1\) is the highest degree of these defining equations. Note that there are 6 defining equations, but the codimension of \(\tilde{\mathfrak{B}}_{2}\) is generically 4. Hence these equations fail to define \(\tilde{\mathfrak{B}}_{2}\) as a complete intersection. (Recall that a variety of codimension \(m\) is said to be a complete intersection if it can be defined by \(m\) polynomials).

The remaining sets \(\widetilde{\mathfrak{B}}_{i} \subset \mathbf{R}^{3} \times \mathbf{R}^{2 t}, i=3,4,5\), correspond to multilocal singularities of the projection map \(f\). These sets are defined in the following way:

$$
\begin{aligned} \tilde{\mathfrak{B}}_{l}:=\overline{\left\{\left(\ell, p_{1}, \ldots, p_{t}\right) \in \mathbf{R}^{3} \times \mathbf{R}^{2 t}: \overline{f_{1}^{i}}=\right.} & \\ & \left.\cdots=\tilde{f_{l}^{i}}=0 ; p_{k} \neq p_{l}\right\} \end{aligned}
$$

where the overbar denotes the algebraic closure and where the \(\hat{f_{j}}\) are defined below. If we omit the condi tions \(p_{k} \neq p_{l}\) we will obtain reducible closed sets which contain, apart from the (generically 1-dimen sional) sets \(\tilde{\mathfrak{B}}_{l}\) that correspond to "genuine" multiple points of the projection map \(f\), components \(\Delta_{t}^{m}\), where The set \(\tilde{\mathfrak{B}}_{3}\) corresponds to trilocal singularities, where a ray of projection is contained in the tangent planes at three distinct points \(p_{1}, p_{2}, p_{3}\) on a surface. The corresponding apparent contour contains three folds that intersect in a point. This set is given by

$$
\begin{array}{r} \tilde{\mathfrak{B}}_{3}:=\overline{\left\{\left(\ell, p_{1}, p_{2}, p_{3}\right) \in \mathbf{R}^{3} \times \mathbf{R}^{6}: f\left(\ell, p_{t}\right)-\left(\ell, p_{t}\right)\right.} \\ \frac{=(0,0)^{T}, \quad i=2,3}{\left.J\left(\ell, p_{j}\right)=|\ell|^{2}-1=0, \quad j=1,2,3 ; p_{k} \neq p_{\ell}\right\}} \end{array}
$$

\begin{aligned} \tilde{\mathfrak{B}}_{5}:= & \overline{\left\{\left(\ell, p_{1}, p_{2}\right) \in \mathbf{R}^{3} \times \mathbf{R}^{4}: f\left(\ell, p_{1}\right)-f\left(\ell, p_{2}\right)\right.} \\ & \overline{=0,0)^{T}} \\ & \overline{Z_{x}\left(p_{1}\right)-Z_{x}\left(p_{2}\right)=Z_{y}\left(p_{1}\right)-Z_{y}\left(p_{2}\right)} \\ & \left.=J\left(\ell, p_{1}\right)=|\ell|^{2}-1=0 ; p_{1} \neq p_{2}\right\} \end{aligned}

The degrees of the defining equations of \(\tilde{\mathfrak{B}}_{3}\) are less than or equal to \(d+2\). Dropping the conditions \(p_{k} \neq p_{\ell}\) will create additional components \(\Delta_{3}^{1}\) and \(\Delta_{3}^{2}\) whose dimensions are (as one easily checks) two and three, respectively.

Next, we have the set \(\tilde{\mathfrak{B}}_{4}\) corresponding to bilocal singularities where a cusp of the apparent contour meets a fold line (geometrically, this implies that the ray of projection both coincides with an asymptotic ray of the where \(\operatorname{deg} \nabla_{V_{\ell}} f\left(\ell, p_{1}\right)=2 d+1\), which is the highest degree among the defining equations of \(\tilde{\mathfrak{B}}_{4}\) (which also fail to define \(\tilde{\mathscr{B}}_{4}\) as a complete intersection: \(\operatorname{codim}\left(\tilde{\mathfrak{B}}_{4}\right)=6\), generically, but there are 7 equations). The set \(\Delta_{4}^{1}\) corresponding to \(p_{1}=p_{2}\) is easily seen to be 2-dimensional.

Finally, the set \(\tilde{\mathfrak{B}}_{5}\) corresponds to bilocal singularities where a pair of folds of the apparent con tour meets nontransversely in some point (if the folds have exactly 2-point contact then the codimension of this singularity is one). Geometrically, this situation arises when a ray of projection is contained in the tangent planes of a surface at two distinct points \(p_{1}\) and \(p_{2}\) whose normals \(N\left(p_{1}\right)\) and \(N\left(p_{2}\right)\) are parallel. For a surface \(S(p)=(p, Z(p))\) we have \(N\left(p_{1}\right) \| N\left(p_{2}\right) \Leftrightarrow N\left(p_{1}\right) \wedge N\left(p_{2}\right)=(0,0,0)^{T} \Leftrightarrow Z_{x}\left(p_{1}\right)-Z_{x}\left(p_{2}\right)=Z_{y}\left(p_{1}\right)-Z_{y}\left(p_{2}\right)=0\). (Remark: when \(S\) is given by \((X(x, y), Y(x, y), Z(x, y))\) we cannot globally replace the condition \(N\left(p_{1}\right) \wedge N\left(p_{2}\right)=(0,0,0)^{T}\) by \(Z_{x}\left(p_{1}\right)\) - \(Z_{x}\left(p_{2}\right)=Z_{y}\left(p_{1}\right)-Z_{y}\left(p_{2}\right)=0\), but everything else remains the same.) Also note that \(N\left(p_{1}\right) \| N\left(p_{2}\right)\) and \(J\left(\ell, p_{1}\right)=0\) implies that \(J\left(\ell, p_{2}\right)=0\), so that this latter condition is redundant. We hence obtain the following equations, which define \(\tilde{\mathfrak{B}}_{5}\) as a complete intersection:

The degrees of the defining equations are less than or equal to \(d+2\), and the set \(\Delta_{5}^{1}\), corresponding to solu tions where \(p_{1}=p_{2}\), is 3-dimensional.

The varieties 8, C \(R_{3}\) × R 2t, t = 1, 2, 3, are related to the view bifurcation set by the projection r : \(R_{3}\) x R 2t -~ \(R_{3}\), such that ~ := U~ ~r (~,) (in the following we will use the notation ~i := r(~i) for the various components of 2~). The computation of 2~ hence boils down to the elimination of the "surface parameters" (xl, Yl. . . . . xt, Yt) from the defining equations of the 23i. algorithms for this elimination will be described in section 4. In the remainder of this section, we want to study the topological complexity of the view bifurcation set as a function of the degree \(d\) of the projected surface \(S(x, y)\).

The sets \(\tilde{\mathfrak{B}}_{i}\) are real algebraic varieties, but the bi furcation set \(\mathfrak{B}\), which is the projection of the \(\tilde{\mathfrak{B}}_{l}\), will, in general, be merely semialgebraic. Furthermore, it is known that \(\mathfrak{B}\) and the \(\tilde{\mathfrak{B}}_{l}\) are, generically, 1-dimen sional sets. In the following it will be convenient to work over an algebraically closed field, so that in particular the projection of the variety is again a variety. It is also convenient to introduce an additional variable \(\mu\) to make the defining equations of the \(\tilde{\mathfrak{B}}_{i}\) homogeneous (clear ly, no information is thereby lost, because we can recover the original equations by setting \(\mu=1\) ). So let \(f_{j}^{i}\left(\mu, A, C, D, x_{1}, y_{1}, \ldots, x_{t}, y_{t}\right)\) denote the \(j\) th homogeneized and complexified defining equation of \(\tilde{\mathfrak{B}}_{\imath}\), and denote by \(\tilde{V}_{i} \subset \mathbf{C}^{4} \times \mathbf{C}^{2 t}\) the variety defined by \(\left(f_{1}^{i}, \ldots, f_{s_{i}}^{i}\right)\). Note that we omit the conditions \(\left(x_{k}\right.\), \(\left.y_{k}\right) \neq\left(x_{\ell}, y_{\ell}\right)\) for the multilocal cases, so that the \(V_{i}\), for \(i=3,4,5\), are projective varieties corresponding to the affine varieties \(\tilde{\mathfrak{B}}_{i} \cup \Delta_{i}\), where \(\Delta_{i}:=\cup_{m \geq 1} \Delta_{i}^{m}\). Next, let \(b_{i}(X)\) denote the \(i\) th Betti number of the variety \(X\), that is \(b_{i}(X):=\operatorname{rank} H_{l}(X ; k)\), where \(H_{l}(X ; k)\) denotes, as usual, the \(i\) th homology group with respect to some field \(k\) of coefficients. Also, for Theorem 3.1 Let \(f_{1}, \ldots, f_{s}\) be polynomials in \(n\) variables of degree less than or equal to \(d\), and let

$$
\begin{array}{r} X:=\left\{\left(x_{1}, \ldots, x_{n}\right) \in k^{n}: f_{l}\left(x_{1}, \ldots, x_{n}\right)=0,\right. \\ i=1, \ldots, s\} \end{array}
$$

Then (i) for \(k=\mathbf{R}, \Sigma_{l} b_{l}(X) \leq d(2 d-1)^{n-1}\), and (ii) for \(k=\mathbf{C}, \Sigma_{i} b_{i}(X) \leq d(2 d-1)^{2 n-1}\). where \(\pi: \mathbf{C}^{3} \times \mathbf{C}^{2 t} \rightarrow \mathbf{C}^{3}\) is again the projection onto the first factor. We then have the following complexity estimates for the complex and for the real bifurcation set, which will be improved below (see proposition Proposition 3.1 Let \(\mathfrak{B}(\mathbf{C})\) and \(\mathfrak{B}\) denote the complex and the real view bifurcation set of a nonsingular alge braic surface \(S(x, y)=(x, y, Z(x, y))\) of degree \(d\), then

(i) for \(k=\mathbf{C}\) : the sum of the Betti numbers of \(\mathfrak{B}(\mathbf{C})\) is less than or equal to \(O\left(d^{320}\right)\), and (ii) for \(k=\mathbf{R}\) : \(S^{2} \backslash \mathfrak{B}\) has at most \(O\left(d^{192}\right)\) connected components.

Proof' The varieties V, C \(C^{4}\) X C 2t are defined by homogeneous polynomials f(x, A, C, D, x 1.... , Yt), j = 1..... si; let ~7 i denote the highest degree of these polynomials. If 7r : C a x C 2t~ \(C^{4}\) is the projection onto the first factor and Vi := 7r(l~,), then we claim that V, is defined by homogeneous polynomials gj(~, ~ 2t A, C, D) of degree less than or equal to vi := v7 · The claim follows from an elementary result about resultants (see, for example, theorem 10.9 of Walker [1950]).

Lemma 3.1 The resultant \(R\) of the homogeneous poly nomials \(f\left(x_{1}, \ldots x_{n+1}\right)\) and \(g\left(x_{1}, \ldots, x_{n+1}\right)\) of degree \(r\) and \(s\), respectively, with respect to any one of the variables is a homogeneous polynomial in the remain ing variables of degree rs or vanishes if \(f\) and \(g\) have a common (nonconstant) factor.

It is clear that we can obtain the defining equations gj(x, A, C, D) of V i = 7r(~) by eliminating the "surface parameters" (xl, )'1.... , xt, Yt) from the defining equations fji of V be forming a sequence of resultants. So let RI denote the set of resultants with respect to xl of polynomials ft. The elements of R] are homogeneous polynomials of degree at most ~ (by lemma 3.1), because degfj _ _ _ a 7 i. Next, we denote by R~ the set of resultants with respect to Yl of elements of R~, and so on. The defining equations gj of V, C C a are contained in the set R~t, which, by lemma 3.1, consists of homogeneous polynomials of degree less 2t than or equal to ~ . For i = 3, 4, and 5 we remove the greatest (nonconstant) common divisors of the elements of Rj, j < 2t, which correspond to the solution sets 2~ m of dimension greater than one. This doesn't, of course, affect the upper bounds for the degrees of elements of R~t.

It is now clear that 23 (C) is defined by inhomogeous polynomials of the form II~= 1 g~(1, A, C, D), whose 5 zt. degree is less than or equal to v := 1~i=1 ~ · Looking at the defining equations of the ~, we see that v -(d + 1) 4 + (3d + 1) 4 + (d + 2) 64 + (2d + 1) 16 + (d + 2) 16. It follows from theorem 3.1(ii) that the sum of the Betti numbers of ~3(C) is less than or equal to v(2v 1) 5, which is of order d 320 in terms of the degree d of the projected surface S. This proves proposition 3.1(i).

Next, we want to estimate the number of connected components of \(S^{2} \backslash \mathfrak{B}\). Let \(\mathfrak{B}\) denote the real variety defined by considering the defining equations \(\Pi_{i=1}^{5} g_{j}^{i}(1, A, C, D)\) of \(\mathfrak{B}(\mathbf{C})\) as real polynomials. The real bifurcation set \(\mathfrak{B}\) is a (semialgebraic) subset of the real variety \(\mathscr{B}\), which is defined by the defining equations of \(\mathfrak{B}\) and some inequalities of the form \(h(A, C, D) \geq\) 0, which arise from the sets of resultants \(R_{j}^{l}, j<2 t\). From the classification of view bifurcation sets (see for example Rieger [1990b]) it is clear that, for a generic surface \(S\), the sets \(\mathfrak{B}\) and \(\mathfrak{B}\) are graphs in \(S^{2}\). For degenerate smooth surfaces basically the same is true, because, as Mather [1973] has shown, the set of "bad" projection directions has measure zero in \(S^{2}\) for any smooth surface. Now consider the following exact se quence of homology of the pair ( \(S^{2}, \breve{B}\) ) (see theorem 14.1 of Greenberg \& Harper [1981]:

Using the standard fact that the alternating sum of the ranks of an exact sequence vanishes, we get \(\operatorname{rank} H_{2}\left(S^{2}, \breve{\mathfrak{B}} ; \mathbf{Z}_{2}\right)\) where the estimate for \(b_{1}(\breve{B})\) comes from theorem 3.1(i) and is of the order \(d^{192}\) in terms of the degree of the projected surface \(S\). Meanwhile, we get from the subadditivity of the Betti numbers the following inequal ity \(b_{2}\left(S^{2}, \mathfrak{B} ; k\right) \leq b_{2}\left(S^{2}, \mathfrak{B} ; k\right)+b_{2}(\mathfrak{B}, \mathfrak{B} ; k)\) for the triple \(\mathfrak{B} \subset \mathfrak{B} \subset S^{2}\) (recall the following definition: a function \(f\) from certain pairs of spaces to the integers in subadditive if for \(X \subset Y \subset Z\) we have \(f(Z, X) \leq f(Z, Y) \pm f(Y, X))\). Clearly, \(b_{2}(\mathfrak{B}, \mathfrak{B} ; k)=0\) because \(\operatorname{dim} \breve{\mathfrak{B}} \leq 1\). It is a consequence of the Lefschetz duality theorem (see, for example, Giblin's theorem 9.17 [1977, ch. 9]) that the number of connected components of \(S^{2} \backslash \mathfrak{B}\) is equal to \(b_{2}\left(S^{2}, \mathfrak{B} ; \mathbf{Z}_{2}\right)\), which proves the second part of proposition 3.1.

Remarks. (i) The estimate of proposition 3.1 is also valid for the number of connected components of \(\mathbf{P}^{2} \backslash \mathfrak{B}\), because \(\mathbf{P}^{2}\) can be identified with the closed disk \(\mathfrak{D} \subset S^{2}\) (see section 2). The order of the estimate will be the same in this case.

- (ii) Rieger [1990a] showed that the view bifurcation set of an opaque surface is a subgraph of 23, hence the estimate is also valid in this case.

- (iii) For generic surfaces of low degree some of the sets ~, will be empty--genuine triple crossings of the

apparent contour cannot occur for d < 6; a cusp meeting a fold requires d > 5; and tangential contact between folds requires d _> 4). Hence we get lower estimates for surfaces of degree less than six.

- (iv) For smooth algebraic surfaces given by \(S(x,y)\) = (\(X(x,y)\), \(Y(x,y)\), \(Z(x,y)\)) the (order of the) estimate remains valid if we set d := \(max(degX,degY,degZ)\).

- (v) The estimates of proposition 3.1 should not be taken too seriously: there is room for improvement. Perhaps a sharper estimate could be obtained by finding "good" defining equations for the variety 23(C) \(C^{p2}\)(C), whose degree is (as one easily calculates) of order \(d_{7}\). If one could show that 23 (C) is a complete intersection, it would follow from Bezout's theorem that there exist defining equations of degree less than or equal to \(O(d7)\)--in contrast to the equations gj, whose degrees are less than or equal to \(O(d~4)\)! In fact, if 23(C) were a complete intersetion, then the \(O(d7)\) estimated would be exact (i.e., it would also be a lower bound for the degree of g3, where g3(A, C, D) = A 2 + \(C^{2}\) + D 2-1 = 0 are the defining equations of 233(C)).

$$
\begin{aligned} {\left[H_{2}\left(\mathfrak{B} ; \mathbf{Z}_{2}\right)=0\right] } & \rightarrow\left[H_{2}\left(S^{2} ; \mathbf{Z}_{2}\right) \cong \mathbf{Z}_{2}\right] \rightarrow \\ & H_{2}\left(S^{2}, \breve{B} ; \mathbf{Z}_{2}\right) \rightarrow H_{1}\left(\breve{B} ; \mathbf{Z}_{2}\right) \rightarrow\left[H_{1}\left(S^{2} ; \mathbf{Z}_{2}\right)=0\right] \end{aligned}
$$

The following sharper result, which says that the degrees of the \(g_{j}^{l}\) are not greater than \(O\left(d^{16}\right)\), is there fore probably not the best possible.

$$
=b_{1}(\breve{\mathfrak{B}})+1 \leq v(2 v-1)^{2}+1
$$

Proposition 3.2 The degrees of the defining equations of \(\mathfrak{B}_{3}(\mathbf{C}) \cup \mathfrak{B}_{4}(\mathbf{C})\) are less than or equal to \((d+2)^{16}\). (This improves the estimates for \(\Sigma_{i} b_{i}(\mathfrak{B}(\mathbf{C}))\) and for the number of connected components of \(S^{2} \backslash \mathfrak{B}\) to \(O\left(d^{80}\right)\) and \(O\left(d^{48}\right)\), respectively.

Proof: Let \(f_{\ell}(x, y)=\left(u_{\ell}(x, y), v_{\ell}(x, y)\right)\) be a projec tion map depending on the parameters \(\ell=(A, C, D)\) which, as elements of \(k[A, C, D, U, V, x, y]\), have degree at most \(d+2\). Here we take \(U\) and \(V\) as coor dinates in the projection plane. Let \(\Delta_{\ell}(U, V)=0\) denote the defining equations of the apparent contour; by lemma 3.1, \(\operatorname{deg} \Delta_{\ell}(U, V) \leq(d+2)^{4}\). Recall that a point \(P\) on a plane algebraic curve defined by \(\phi(x\), \(y\) ) is an \(r\)-fold point if all derivatives of \(\phi\) of the order less than \(r\) vanish at \(P\) but at least one \(r\) th derivative doesn't. Note that triple points of the apparent contour and points where a cusp meets a fold line are both 3-fold points of \(\Delta_{\ell}(U, V)\). Hence we get the following defin ing equations:

Eliminating \(U\) and \(V\) between these equations gives the defining equations of \(\mathfrak{B}_{3}(\mathbf{C}) \cup \mathfrak{B}_{4}(\mathbf{C}) \subset S^{2}\), which, by lemma 3.1 have degree at most \((d+2)^{16}\).

## 4 Computing the Defining Equations of the View Bifurcation Set

The computation of the view bifurcation set \(\mathfrak{B}\) consists of two steps: (i) the elimination of the surface param eters \(\left(x_{1}, y_{1}, \ldots, x_{t}, y_{t}\right)\) from the defining equations of the varieties \(\tilde{\mathfrak{B}}_{i}\), which gives the defining equations of the variety \(\mathfrak{B} \subset S^{2}\); and (ii) the removal of certain branches of \(\mathfrak{B}\), which correspond to points \((A, C, D) \in S^{2}\) that do not extend to solutions in \(S^{2} \times \mathbf{R}^{2 t}\). The classical method of elimination uses resultants (see, van der Waerden [1939], for example). Alternatively, one can eliminate the surface parameters by computing cer tain standard bases (Gröbner bases) of the ideals defin ing the \(\tilde{\mathfrak{B}}_{l}\) with the Buchberger algorithm [Buchberger 1969, 1985]. first, we need some definitions. For \(\alpha=\left(\alpha_{1}, \ldots\right.\), \(\alpha_{n}\) ) and \(\beta=\left(\beta_{1}, \ldots, \beta_{n}\right) \in \mathbf{N}^{n}\), we define the follow ing lexicographical ordering \(>\) :

$$
\alpha \succ \beta \Leftrightarrow \exists_{m}, \quad 1 \leq m \leq n
$$

$$
\begin{aligned} \alpha_{n} & =\beta_{n} \\ \alpha_{n-1} & =\beta_{n-1} \\ \vdots & \\ \alpha_{m+1} & =\beta_{m+1}, \text { and } \\ \alpha_{m} & >\beta_{m} \end{aligned}
$$

Let \(x=\left(x_{1}, \ldots, x_{n}\right)\), and define the leading monomial \(L(f)\) of a polynomial \(f(x)=\Sigma_{\alpha \in \mathbf{N}^{n}} a_{\alpha} x^{\alpha} \in k\left[x_{1}, \ldots, x_{n}\right]\), with respect to \(\zeta\), to be the \(x^{\alpha}, a_{\alpha} \neq\) 0, for which \(\alpha\) is maximal (w.r.t. \(\zeta\) ). Then we have the following [Mishra \& Yap 1989].

Proposition/definition 4.1 \(G\) is a standard basis (Gröbner basis) for an ideal \(I=\left(f_{1}, \ldots, f_{s}\right)\) in \(k\left[x_{1}\right.\), \(\left.\ldots, x_{n}\right] \Leftrightarrow\{L(g): g \in G\}\) is a basis for the ideal

Let \(F\) denote a set of polynomials, a polynomial \(h\) reduces to \(k\) modulo \(F\) if \(h=k+b \cdot f\), for \(f \in F\) and \(b \in k\left[x_{1}, \ldots, x_{n}\right]\), and \(\alpha \succ \beta\), where \(a_{\alpha} x^{\alpha}=L(h)\) and \(b_{\beta} x^{\beta}=L(k)\) (this reduction of \(h\) is hence some kind of division). A polynomial \(h\) is a normal form modulo \(F\) if such a reduction is not possible. A stan dard basis \(G\) is said to be reduced if every \(g \in G\) is a normal form modulo \(G \backslash\{g\}\) and if the coefficient of \(L(g)\) is equal to one. It can be shown that a reduced standard basis is unique in the following sense: if \(G_{1}\) and \(G_{2}\) are reduced standard bases for the ideals \(I_{1}\) and \(I_{2}\), respectively, then \(I_{1}=I_{2}\) implies that \(G_{1}=G_{2}\).

$$
\partial^{i+j} \Delta_{\ell}(U, V) / \partial U^{i} \partial V^{j}=|\ell|^{2}-1=0
$$

The nice property of any standard basis \(G\), as far as elimination is concerned, is that, up to some reor dering of its generators, \(G\) is 'triangulated" with respect to the \(x_{l}\). To be more precise, we state the following result of Trinks [1978].

Proposition 4.2 Let \(G\) be a standard basis, and assume the ordering of monomials \(x^{\alpha}\) in \(k\left[x_{1}, \ldots, x_{n}\right]\) induced from the above lexicographical ordering \(\zeta\) on \(\alpha \in \mathbf{N}^{n}\), then we have the following:

Now let \(I\left(\tilde{\mathfrak{B}}_{i}\right)=\left(f_{1}^{i}, \ldots, f_{s_{i}}^{i}\right)\) denote the ideal in \(k\left[A, C, D, x_{1}, y_{1}, \ldots, x_{t}, y_{t}\right]\) defining the variety \(\tilde{\mathfrak{B}}_{l}\), and let \(G\left(\tilde{\mathfrak{B}}_{j}\right)\) denote a standard basis of \(I\). The com ponents of \(\mathfrak{B} \subset S^{2}\) are then defined by \(\mathbf{G}\left(\tilde{\mathfrak{B}}_{i}\right) \cap k[A\), \(C, D]\). The computation of a standard basis of an ideal in a polynomial ring is an algorithmic procedure (in vented by Buchberger [1969, 1985] in 1965), and is available in several computer algebra systems (see sec tion 6). We have seen in section 2 that the projective plane We have seen in section 2 that the projective plane of projection directions (where \(\ell\) and \(-\ell\) are identified) corresponds to the closed disk

$$
\begin{aligned} \mathfrak{D}=\left\{(A, C, D) \in S^{2}: 0\right. & \leq A^{2}+C^{2} \leq \frac{1}{2} \\ & \left.\leq D^{2} \leq 1, D>0\right\} \subset S^{2} \end{aligned}
$$

The orthogonal projection of ~ to the plane D = 0 is a diffeomorphism. Let ~ * and 23' denote the images of ~ and 23 C ~ under this projection. The curve 23" is a plane curve (intersected with the closed disk {(A, C) ~ \(R_{2}\) : 0 -< \(A_{2}\) h-\(C_{2}\) ~ 1 2}) defined by the polynomial 1I 5 ~=1 g,(A, C) = 0, where gi C \(G(~i)\) M k[A, C]. There is always such a unique gi(A, C) (i.e., \(\left.\left\{g_{i}\right\}=G\left(\tilde{\mathfrak{B}}_{i}\right) \cap k[A, C]\right)\) provided that (the com plexification of) \(\mathfrak{B}_{i}^{*}\) is 1-dimensional and the \(G\left(\tilde{\mathfrak{B}}_{l}\right)\) are reduced standard bases. (Note that a 1-dimensional set \(\mathfrak{B}_{l}^{*}\) in the plane is always a complete intersection. It can be easily shown that the bifurcation set of a map \(\mathbf{C}^{2} \rightarrow \mathbf{C}^{2}\) is always a hypersurface; the complexified sets \(\mathfrak{B}_{i}^{*}\) are therefore always 1-dimensional or empty).

There is an alternative method of computing the part of the view bifurcation set \(\mathfrak{B}_{1}^{*} \cup \mathfrak{B}_{2}^{*}\), which cor responds to degenerate local singularities. In Rieger [1987a] it was shown that any local singularity of a complex-analytic map of the plane of codimension greater than zero disintegrates into more than one cusp under a generic deformation. Hence it is clear that the ideal \(I_{c}:=\left(J(\ell, p), \nabla_{V_{\ell}} f(\ell, p),|\ell|^{2}-1\right) \subset \mathbf{R}[\ell\), \(p\) ] has solutions of multiplicity greater than one (in an algebraic extension of \(\mathbf{R}\) ) if and only if \(\ell \in \mathfrak{B}_{1} \cup \mathfrak{B}_{2} \subset \mathbf{P}^{2}\). Such "bad" projection directions can be deter mined by first eliminating \(x\), say, between the elements of \(I_{c}\) and then calculating the discriminants with respect to \(y\), and vice versa. Again, this computation can be done using either resultants or standard bases.

The sets \(\tilde{\mathfrak{B}}_{l}\), where \(i=3,4\), and 5, correspond to multilocal singularities, but not all components of \(\tilde{\mathfrak{B}}_{i}\) come from "genuine" multiple points of the projection map \(f(\ell, p)\). A primary decomposition of \(I\left(\tilde{\mathfrak{B}}_{i}\right)\) shows that some solutions correspond to points \(\left(x_{k}, y_{k}\right)=\left(x_{l}\right.\), \(y_{l}\) ), where \(k \neq l\). Such solution branches can be removed by dividing certain elements of \(G\left(\tilde{\mathfrak{B}_{i}}\right)\) by powers of \(x_{k}-x_{l}\) or \(y_{k}-y_{l}\).

Not every point \((A, C) \in \mathfrak{B}^{*}\) extends to a real solu tion of \(I\left(\tilde{\mathfrak{B}}_{i}\right)\) for some \(i\). Hence there are, in general, more connected components in \(\mathfrak{D}^{*} \backslash \mathfrak{B}^{*}\) than there are in \(\mathfrak{D} \backslash \mathfrak{B}\). In section \(\mathbf{6}\) we describe a method for finding representatives for the connected components of \(\mathfrak{D}^{*} \backslash \mathfrak{B}^{*}\), which is based on a cylindrical algebraic decomposition (CAD) of \(\mathfrak{D}^{*}\). The CAD of \(\mathfrak{D}^{*}\) is finer than the decomposition of \(\mathfrak{D}^{*}\) into connected com ponents of \(\mathfrak{D}^{*} \backslash \mathfrak{B}^{*}\). Hence we get superfluous representatives (i.e., nodes in the aspect graph) due both to the fact that branches of \(\mathfrak{B}^{*}\) do not extend to real solutions of \(I\left(\tilde{\mathfrak{B}}_{i}\right)\) and to additional cells introduced by the CAD of \(\mathfrak{D}^{*}\). At the end of section 6 we describe a way of removing such superfluous representatives by computing certain invariants of stable projections of

## 5 Noncompact Surfaces and Singularities of the Apparent Contour at Infinity

The curve C can be computed as follows. Let \(\Delta_{\ell}(U\), \(V)\) be the defining equation of the apparent contour, which can be computed using resultants, as described in the proof of proposition 3.2, or standard bases. The set \(\left\{\Delta_{\ell}(U, V)=0:|\ell|^{2}=1\right\} \subset S^{2} \times \mathbf{R}^{2}\) consists of \(a_{2}\)-parameter family of plane affine curves. Let \(\tilde{\Delta}_{\ell}(\lambda, U, V)=0\) define a projective plane curve where \(\tilde{\Delta}_{\ell}(1, U, V)=\Delta_{\ell}(U, V)\). We want to find the param eter values \(\ell\) such that the projective curve \(\tilde{\Delta}_{\ell}\) has a singular point at \(\lambda=0\). To find such singular points in the hyperplane at infinity, given by \(\lambda=0\), we con sider two sets of affine equations

$$
\begin{aligned} \tilde{\Delta}_{\ell}(\lambda, 1, V) & =\partial \tilde{\Delta}_{\ell}(\lambda, 1, V) / \partial \lambda \\ & =\partial \tilde{\Delta}_{\ell}(\lambda, 1, V) / \partial V=\lambda \\ & =|\ell|^{2}-1=0 \end{aligned}
$$

$$
\begin{aligned} \tilde{\Delta}_{\ell}(\lambda, U, 1) & =\partial \tilde{\Delta}_{\ell}(\lambda, U, 1) / \partial \lambda \\ & =\partial \tilde{\Delta}_{\ell}(\lambda, U, 1) / \partial U=\lambda \\ & =|\ell|^{2}-1=0 \end{aligned}
$$

which define varieties in \(S_{2}\) x \(R_{2}\) (note that we miss the point U = V = 0 but (0 : 0 : 0) ~ p2, anyway). Projecting these varieties onto \(S_{2}\), by computing standard bases G with respect to the orderings k ~- V ~-D ~-A ~ C andk ~-U ~ D ~ A ~ C, respectively, taking the intersections (G) N k[A, C], and restricting to the closed disk ~ * gives the defining equations of G* Using the same arguments as in section 3, one can show that the order of the estimate for the number of connected components of \(\mathbf{P}^{2} \backslash(\mathfrak{B} \cup \mathfrak{C})\) is the same as the estimate in proposition 3.2 for \(\mathbf{P}^{2} \backslash \mathfrak{B}\).

In actual calculations it turns out that it is more efficient to compute the cusps at infinity and the fold crossings at infinity separately (see section 4 for an ex ample). The ideals \(I_{c}:=\left(J(\ell, p), \nabla_{v_{\ell}} f(\ell, p)|\ell|^{2}-\right.\) 1) and \(I_{d}:=\left(u\left(\ell, p_{1}\right)-u\left(\ell, p_{2}\right), v\left(\ell, p_{1}\right)-v\left(\ell, p_{2}\right)\right.\), homogenous with respect to the surface parameters \(p_{\imath}=\left(x_{i}, \mathrm{y}_{1}\right)\) by introducing a new variable \(\lambda\) one obtains corresponding surfaces in \(S^{2} \times \mathbf{P}^{2 t}\). These surfaces in tersect the hyperplane at infinity, \(\lambda=0\), along certain curves that correspond to cusps and fold crossings, re spectively, at infinity. The projections of these curves onto \(S^{2}\) give the branches of \(\mathscr{C}\) that correspond to cusps and fold crossings at infinity. In the example of section 7 we use standard bases to compute these projections.

## 6 Computing Representatives of the Components in the Complement of the Bifurcation Set

first, we need the following definition. Let \(F\) denote a set of polynomials in \(\mathbf{R}\left[x_{1}, \ldots, x_{n}\right]\) and let \(S \subset \mathbf{R}^{m}\), \(m \leq n\), be any subset. Then \(S\) is said to be \(F\)-invariant if any \(f \in F\) is either strictly positive, strictly negative, or vanishes on \(S\). The following result is due to Lojasie wicz (see, for example, [Bochnak et al. 1987 ch 2]).

Theorem 6.1 For any subset \(F \subset \mathbf{R}\left[x_{1}, \ldots, x_{n}\right]\) there exists a subset \(G \subset \mathbf{R}\left[x_{1}, \ldots, x_{n-1}\right]\) such that for any connected \(G\)-invariant subset \(S \subset \mathbf{R}^{n-1}\) there are continuous functions \(\rho_{1}<\cdots<\rho_{r}: S \rightarrow \mathbf{R}\) which give, for all \(s \in S\) and \(f \in F\), the real roots of \(f\left(s, x_{n}\right)\). Furthermore, if \(S\) is semialgebraic then so are the graphs of the \(\rho_{i}\) and the slices of the cylinder \(S \times \mathbf{R}\) cut out by these graphs.

So given a set \(F \subset \mathbf{R}\left[x_{1}, \ldots, x_{n}\right]\) we get by in duction on \(n\) a stratification of \(\mathbf{R}^{n}\) into \(F\)-invariant cells (strata) \(C_{i}\) which are homeomorphic to open sets \(] 0\), \(1\left[{ }^{d_{t}}\right.\) (where \(d_{i}:=\operatorname{dim} C_{i}\) ). The resulting stratification of \(\mathbf{R}^{n}\) is called a cylindrical algebraic decomposition (or CAD) after Collins who invented an algorithm for computing CADs (see Collins [1975] and Arnon et al. [1984]). In the following, \(F\) is assumed to be a set of polynomials with integer coefficients (rational coeffi cients would be o.k., too). Let \(F_{0}:=F\) and define \(F_{j+1} \subset \mathbf{Z}\left[x_{1}, \ldots, x_{n-j-1}\right], 0 \leq j \leq n-1\), to be the union of \(\left\{\operatorname{psc}_{k}(f, g): f, g \in F_{j} ; 0 \leq k<\min (\operatorname{deg} f, \operatorname{deg} g)\right\}\) and where \(\operatorname{psc}_{k}(f, g)\) is the \(k\) th principal subresultant of \(f\), \(g \in \mathbf{Z}\left[x_{1}, \ldots, x_{n-J-1}\right]\left[x_{n-J}\right]\) (recall that \(\operatorname{psc}_{0}(f, g)\) is the usual resultant of \(f\) and \(g\) with respect to \(x_{n-j}\), and that the \(\operatorname{psc}_{k}(f, g), k>0\), are determinants of certain minors of the Sylvester matrix-see Collins [1975]). If the leading coefficients of the \(f \in F_{j}\), where the \(f\) are viewed as polynomials in \(x_{n-j}\), are nonzero constants (which can always be achieved by a linear change of coordinates [van der Waerden 1939]), then \(F_{j}\) and \(F_{j+1}\) correspond to \(F\) and \(G\), respectively, in the statement of theorem 6.1. To construct the CAD of \(\mathbf{R}^{n}\), one first determines the \(F_{n-1}\)-invariant subsets of the real line, which consist of 0-cells, given by the roots of the elements of \(F_{n-1}\), and 1-cells, which are the connected components of \(\mathbf{R}\) in the complement of the 0-cells. Ar non, Collins, and McCallum [1984] call the construc tion of the sequence \(F_{0}, F_{1}, \ldots, F_{n-1}\) the projection phase, and the determination of the \(F_{n-1}\)-invariant 0 and 1-cells of \(\mathbf{R}\) the base phase. The final stage in their algorithm is the extension phase: over each 0-cell or 1-cell of \(\mathbf{R}\), one constructs the \(F_{n-2}\)-invariant 0-and 1-cells or 1-and 2-cells, respectively, of \(\mathbf{R}^{2}\), and then one proceeds inductively on \(n\) until one arrives at a \(F_{0}\)-invariant CAD of \(\mathbf{R}^{n}\) consisting of open \(i\)-cells \((0 \leq i \leq n)\). The details of this algorithm and examples are described by Arnon et al. [1984].

(where \(n=2\) ). The elements of \(F_{n-1}\) are univariate polynomials \(f_{l}\left(x_{1}\right)\) with integer coefficients, and it is possible to find intervals with rational endpoints \(q_{j}^{1}, q_{j}^{2}\) such that each root \(\alpha_{j}\) of some \(f_{i}\) is contained in exactly one of these intervals (using the Uspensky algorithm described in Collins and Loos [1982]. Suppose that \(q_{j}^{1}<q_{j}^{2}<q_{j+1}^{1}\) and \(1 \leq j \leq s\), then the follow ing rational numbers are representatives for each \(F_{n-1^{-}}\) invariant 1-cell of \(\mathbf{R}\) : \(\left(q_{j}^{2}+q_{j+1}^{1}\right) / 2,1 \leq j \leq s-1\); and any pair \(q_{-\infty}, q_{\infty} \in \mathbf{Q}\) such that \(q_{-\infty}<q_{1}^{1}\) and \(q_{\infty}>q_{s}^{2}\) (and if there exist no real roots we may take the origin as representatives of \(\mathbf{R}\) ). For each of these representatives \(P\) we then consider the roots of the polynomials \(f_{i}\left(P, x_{2}\right) \in F_{n-2}\) and apply the same pro cedure as above to obtain representatives \(P^{\prime} \in \mathbf{Q}^{2}\) of the \(F_{n-2}\)-invariant 2-cells of \(\mathbf{R}^{2}\). By induction on \(n\) we get representatives with rational coordinates for each \(F_{0}\)-invariant \(n\)-cell in \(\mathbf{R}^{n}\).

In our case the set \(F_{0} \in \mathbf{Z}[A, C]\) consists of the defining equations of \(\mathfrak{B}^{*} \cup \mathfrak{C}^{*} \cup \partial \mathfrak{D}^{*}\). From among the resulting representatives \(P\) of the 2-cells of the

$$
\left.0 \leq k<\operatorname{deg} \partial f / \partial x_{n-\jmath}\right\}
$$

CAD of \(\mathbf{R}^{2}\) we are only interested in those that are con tained in \(\mathfrak{D}^{*}\), that is, \(|P|^{2} \leq 1 / 2\). The stable views of a surface \(S\) associated with these representatives are not, in general, all inequivalent. The superfluous repre sentatives can be removed by merging pairs of neighbor ing 2-cells of the CAD of \(\mathfrak{D}^{*}\) which are both adjacent to some 1-cell \(C\) of one of the following types: (i) \(C \subset \mathfrak{B}^{*} \cup \mathfrak{C}^{*}\) does not correspond to real singularities of the apparent contour either of positive codimension or contained in the line at infinity; (ii) \(C \not \subset \mathfrak{B}^{*} \cup \mathfrak{C}^{*}\); or (iii) \(C \subset \partial \mathfrak{D}^{*}\) is not the projection of \(\mathfrak{B}\) or \(\mathbb{C}\) (recall that \(P \sim-P\) for a point \(P \in \partial \mathfrak{D}^{*}\), so that a pair of nonneighboring 2-cells of \(\mathbf{R}^{2}\) can be adjacent to the To find neighboring pairs of 2-cells, one has to decide whether a pair of 2-cells is adjacent to the same 1-cell. algorithms for computing adjacencies and inci dence of cells of the CAD are described by Arnon et al. [1984] and Prill [1986], in the following we will briefly sketch what we need for our purposes. There are two types of 1-cell in the CAD of \(\mathbf{R}^{2}\)-"horizontal 1-cells" over the \(F_{1}\)-invariant 1-cells of \(\mathbf{R}\) (i.e., the graphs of the functions \(\rho_{1}\) of theorem 6.1), and "ver tical 1-cells" over the \(F_{1}\)-invariant 0-cells \(\alpha_{j}\) of \(\mathbf{R}\). The vertical 1-cells are the open sets in \(\left\{\alpha_{j}\right\} \times \mathbf{R}\) in the complement of the roots of \(f\left(\alpha_{j}, C\right)\), where \(f \in F_{0}\). The adjacencies in \(\mathbf{R}^{2}\) between 2-cells and horizontal 1-cells are simply given by the ordering of the roots of the \(f(P, C)\), where \(f \in F_{0}\) and \(P\) is a fixed rational representative of some \(F_{1}\)-invariant 1-cell of \(\mathbf{R}\). Com puting the adjacencies between 2-cells and vertical 1-cells, on the other hand, is nontrivial; polynomial time algorithms for this adjaceny computation are described by Arnon et al. [1984] and Prill [1986]. Note that in the case of horizontal 1-cells one merely has to compute the roots of \(f(P, C) \in \mathbf{Q}[C]\), whereas the case of vertical 1-cells involves computing in algebraic ex tensions because \(f\left(\alpha_{j}, C\right) \in \mathbf{Q}\left(\alpha_{j}\right)[C]\). In our exam ple of section 7, we use an implementation of an adja cency algorithm for 0-, 1-, and 2-cells in the plane (see Stiefvater [1989]), which can be easily extended to curves in the projective plane.

Recall from section 2 that pairs of antipodal points P, -P ~ 0~* are identified, so that pairs of 2-cells which are adjacent to some 1-cell in a ~ * might be neighboring cells of the CAD in ~ * and not in \(R_{2}\). Let Co. . . . . Cm denote the Fm-invariant 1-cells conrained in the closed interval [-1.j2, 1L J2], and let Cj. x, ·.., Cj,nj denote the F0-invariant 2-cells over Cj which are contained in ~ * (we assume that Cj is to the left of Cj+I and that Cj, k is below C,k+i). Let %, 1 < j < m, be a real root of some f ~ F1 C Z[A] such that % < %+1 and-1Lj2 < _ _ % _< 1 ~2. Now set R := {~1. . . . . O~m} and L ~ := R U {-%\(\wp\)__~1¢RJ. The vertical lines {-% \(\wp\) x R, where -% ~ k \ R, subdivide certain 2-cells of the CAD into smaller open 2-cells. Now consider the set I" of 2-cells consisting of cells of the CAD that have not been subdivided by such vertical lines and of these open cells contained in 2-cells of the CAD in the complement of the vertical lines. Each 2-cell in 1" that is adjacent to some 1-cell in 0 ~ * has exactly one 2-cell which is adjacent to the antipodal points in O~* of this 1-cell. Such a pair of 2-cells is a neighboring pair in the disk ~* because of the identification of antipodal points in the boundary of this disk. And a pair of 2-cells C,,1, Cj,nj of the CAD of ~* is a neighboring pair if it contains (or is equal to) a pair of neighboring 2-cells of I'.

Next, we define two integer invariants \(c\) and \(d\) of a stable projection of a smooth surface- \(c\) and \(d\) are the numbers of cusps and transverse fold crossings, respectively. Let \(P_{1}\) and \(P_{2}\) denote representatives of a pair of neighboring 2-cells of \(\mathfrak{D}^{*}\), if \(c\left(P_{1}\right) \neq c\left(P_{2}\right)\) or \(d\left(P_{1}\right) \neq d\left(P_{2}\right)\) then the 1-cell that separates the pair of 2-cells is a genuine part of the bifurcation set or of the set that corresponds to singular points of the ap parent contour at infinity. The converse is, in general, not true: if the 1-cell corresponds to a branch of real solutions of \(I\left(\tilde{\mathfrak{B}}_{3}\right)\), that is to triple-fold crossings (see section 3), or to certain multiple components of the bifurcation set (this does not arise for projections of generic surfaces), then \(c\left(P_{1}\right)=c\left(P_{2}\right)\) and \(d\left(P_{1}\right)=d\left(P_{2}\right)\). The numbers \(c\) and \(d\) are the numbers of real roots of the ideals \(I_{c} \subset \mathbf{Q}[D, x, y]\) and \(I_{d} \subset \mathbf{Q}\left[D, x_{1}\right.\), \(\left.y_{1}, x_{2}, y_{2}\right]\) such that \(D \geq 1 / \sqrt{ } 2\). The defining equations of these ideals (in the notation of sections 2 and 3) are

$$
\begin{aligned} f\left(\ell, p_{1}\right)-f\left(\ell, p_{2}\right) & =J\left(\ell, p_{i}\right) \\ & =|\ell|^{2}-1=0, \quad i=1,2 \end{aligned}
$$

where \(\ell=(P, D)\), for some \(P \in \mathbf{Q}^{2}\), and \(p_{i}=\left(x_{i}, y_{i}\right)\). The apparent contour \(\Delta_{P}\) of the surface \(S\) associated to \(P \in \mathbf{Q}^{2}\) can be obtained by eliminating \(D, x\), and \(y\) between

$$
\begin{aligned} u(\ell, p)-U & =v(\ell, p)-V \\ & =J(\ell, p)=|\ell|^{2}-1=0 \end{aligned}
$$

where \(f(\ell, p)=(u(\ell, p) v(\ell, p))\) and \(D \geq 1 / \sqrt{2}\). The singularities of the apparent contour \(\Delta_{p}(U, V)=0\) are given by

If \(P\) is a representative of a 2-cell of the CAD (and hence corresponds to a stable view), then \(\left|S_{P}\right|=c(P) +d(P)\). If \(I\left(\tilde{\mathfrak{B}}_{3}\right)\) has no 1-dimensional branches of real solu

$$
A\left\{C \left\{\xi _ { 1 } \left\{\ldots \left\{\xi_{7}\right.\right.\right.\right.
$$

If \(I\left(\tilde{\mathfrak{B}}_{3}\right)\) has no 1-dimensional branches of real solu tions (which, for example, is always the case if the degree of the projected surface is less than six) and if the bifurcation set has no multiple components (which can be checked by inspecting the standard bases \(G\left(\tilde{\mathfrak{B}}_{i}\right)\) ), then we can find a single representative for each stable view by computing \(c\) and \(d\). If, for a pair of representatives \(P_{1}, P_{2}\) of neighboring 2-cells, \(c\) and \(d\) are equal, we can remove one of them. To be more precise: consider the ordered set

$$
S:=\left\{C_{0,1}, C_{0,2}, \ldots, C_{0, n_{0}}, C_{1,1}, \ldots, C_{m, n_{m}}\right\}
$$

of 2-cells of the CAD of \(\mathfrak{D}\) *. Initially, we represent each cell \(C_{i, j}\) by a rational representative \(P_{i, j}\) and its position \(v_{i, J}:=j+\Sigma_{k=0}^{i-1} n_{k}\) in \(S\). Now we visit each cell \(C_{i, j}\) in the order defined by \(S\) and compare the numbers \(c\left(P_{i, J}\right)\) and \(d\left(P_{i, J}\right)\) with the corresponding numbers of the neighboring cells above and to the right of \(C_{\imath, j}\). Each cell \(C_{i, j}\) has exactly one neighboring cell above if \(j<n_{i}\) and has at least one neighboring cell above if If the set of triple-fold crossing is nonempty, the situation becomes more complicated. One possible ap proach in this case would be the following: let \((\hat{A}, \hat{C})\) be a point on \(a_{1}\)-cell separating a pair of neighboring 2-cells. Note that we can always choose such a point with one rational coordinate, but the other coordinate will in general be an algebraic number. Now set

\(\mathbf{Q}\left[A, C, \xi_{1}, \ldots, \xi_{7}\right]:=\mathbf{Q}\left[A, C, D, x_{1}, y_{1}, \ldots, y_{3}\right]\) and consider elements

$$
\begin{aligned} S_{P}:= & \left\{(U, V) \in \mathbf{R}^{2}: \Delta_{P}(U, V)\right. \\ & \left.=\partial \Delta_{P}(U, V) / \partial U=\partial \Delta_{P}(U, V) / \partial V=0\right\} \end{aligned}
$$

$$
f_{i} \in G\left(\tilde{\mathfrak{B}}_{3}\right) \cap \mathbf{Q}\left[A, C, \xi_{1}, \ldots, \xi_{t}\right]
$$

for \(i=1, \ldots, 7\). Here \(G\left(\tilde{\mathfrak{B}}_{3}\right)\) denotes, as in section 4, the standard basis of \(I\left(\tilde{\mathfrak{B}}_{3}\right)\) w.r.t. the lexicographical ordering

The l-cell containing ( \(\hat{A}, \hat{C}\) ) corresponds to real triple fold crossing if and only if \((\hat{A}, \hat{C})\) is the projection of some point \(\left(\hat{A}, \hat{C}, \hat{\xi}_{1}, \ldots, \hat{\xi}_{7}\right) \in \tilde{\mathcal{B}}_{3}\). This can be checked by induction on \(i\) : the elements \(f_{1}\left(\hat{A}, \hat{C}, \xi_{1}\right) \in G\left(\tilde{\mathfrak{B}}_{3}\right)\) are univariate polynomials in \(\xi_{1}\) with coeffi cients in some algebraic extension of \(\mathbf{Q}\). The common real roots \(\hat{\xi}_{1}\) of the \(f_{1}\) (if they exist) can be determined using a modified version of the Uspensky algorithm (which is based on Descartes' rule of sign, see Collins \& Loos [1982]). Likewise, if \(\hat{p}:=\left(\hat{A}, \hat{C}, \hat{\xi}_{1}, \ldots, \hat{\xi}_{i}\right)\) is a real root of the \(f_{i} \in G\left(\tilde{\mathfrak{B}}_{3}\right)\), one can check whether the univariate polynomials \(f_{l+1}\left(\hat{p}, \xi_{t+1}\right)\) have real roots \(\hat{\xi}_{i+1}\). If, at some stage of the induction, there are no real roots we can remove the 1-cell containing ( \(\hat{A}, \hat{C}\) ) and merge the pair of neighboring 2-cells.

Remarks: Note that one could apply this procedure to the other components \(\mathfrak{B}_{i}\) of the bifurcation set, but the method based on the invariants of the apparent con tour is more efficient in this case. One referee of this article pointed out that one could also use the fact that the apparent contours become nonisomorphic as graphs in the plane as one passes through a triple fold crossing-this would require computing a more detailed description of a stable apparent contour rather than just computing its singular points (cusps and double folds).

## 7 An Example

Before giving an example we would like to mention a relation between the geometry of the projected surface \(S(x, y)=(x, y, Z(x, y))\) and the structure of the view bifurcation set in \(\mathbf{P}^{2}\). The relation between surface geometry and projections has been studied by several authors (see, for example, [Arnol'd 1983; Gaffney \& Ruas 1977; Koenderink 1986]), and the results below are well explained in the book of Banchoff, Gaffney, and McCrory [1982], from which we also take the ex ample surface below as input for our algorithm. Put \(p:=Z_{x}(x, y), q:=Z_{y}(x, y), r:=Z_{x_{x}}(x, y), s:=Z_{x_{y}}(x, y)\), and \(t:=Z_{y_{y}}(x, y)\). A point \(P=(x, y, Z(x\), the parabolic points of a generic surface \(S\) form smooth curves without selfintersections (see [Kergosien \& Thom 1980]). The asymptotic directions at a point \(P\) on \(S\) are directions in \(T_{P} S\) along which the normal curva ture vanishes. They can be computed from the second fundamental form \(r d x^{2}+2 s d x \cdot d y+t d y^{2}=0\), giving

$$
a_{1,2}:=(d x: d y: p d x+q d y) \in \mathbf{P}^{2}
$$

where

$$
\frac{d x}{d y}=-s \pm \frac{\sqrt{s^{2}-r t}}{r}
$$

Hence there are 0,1, or 2 asymptotic directions at an elliptic \(\left(r t-s^{2}>0\right)\), parabolic, or hyperbolic point \(\left(r t-s^{2}<0\right)\) of \(S\). The integral curves of the asymp totic lines form a pair of 1-parameter families of curves in the hyperbolic regions of \(S\). The points of inflection \(P\) of this family of curves form the so-called "flec nodal" curve. The asymptotic lines at \(P\) have 4-point contact with \(S\) and are characterized by the condition \(d^{2} x / d y^{2}=0\). The flecnodal curve of a generic surface \(S\) is a smooth curve that can have transverse self-intersections-if both asymptotic lines have 4-point contact with \(S\) at some special point \(P\) (see [Arnol'\(d_{1983}\)])-and which can touch the parabolic curve at cer tain points (which points correspond to cusps of the Gauss map of \(S\); see [Banchoff et al. 1982]).

Let \(\mathfrak{F}\) and \(\mathfrak{P}\) denote the sets of flecnodal and para bolic points of \(S\), and put

$$
\begin{aligned} & \overline{\mathfrak{B}}_{1}:=\left\{(x, y) \in \mathbf{R}^{2}: S(x, y) \in \mathfrak{P}\right\} \\ & \overline{\mathfrak{B}}_{2}:=\left\{(x, y) \in \mathbf{R}^{2}: S(x, y) \in \mathfrak{F}\right\} . \end{aligned}
$$

\(A(x, y)=(d x: d y: p d x+q d_{y})\), where \(d x / d_{y}=(-s \left.\pm \sqrt{s^{2}-r_{t}}\right) / r\). The "asymptotic ray map" \(A\) is not really a map (as the broken arrow indicates) because it is not defined at elliptic points and has two values at each hyperbolic point of \(S\). The restriction of \(A\) to the set \(\mathfrak{B}_{1}\), which we denote by \(A_{1}\), and the map \(A_{2}\) that assigns to points in \(\bar{B}_{2}\) the asymptotic lines that satisfy the condition \(d^{2} x / d y^{2}=0\) above are, however, well defined. Now we have, for \(i=1,2\), the following relation between the sets \(\overline{\mathfrak{B}}_{i}\) and the sets \(\tilde{\mathfrak{B}}_{t}\) and \(\mathfrak{B}_{t}\) which corres pond to local singularities of positive codimension of orthogonal projections of \(S\) (for definitions see section 3):

$$
\frac{d x}{d y}=y \mp \sqrt{7 y^{2}+x} \quad \text { and }
$$

$$
\frac{d^{2} x}{d y^{2}}=1 \mp \frac{14 y+d x / d y}{2 \sqrt{7 y^{2}+x}}=0
$$

where \(\pi_{j}\) denotes the projection onto the \(j\) th factor.

![Figure 6 Menn's surface--parabolic curve (solid line) and flecnodal curve (dotted line).](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-6-p018.png)

*Figure 6 Menn's surface--parabolic curve (solid line) and flecnodal curve (dotted line).: Menn's surface--parabolic curve (solid line) and flecnodal curve (dotted line).*

Here is an example: Menn's surface is given by the graph of the function \(Z(x, y)=y^{4}+x y^{2}-x^{2}\) (see figure 6). The geometry of this surface has been studied in detail in the book of Banchoff et al. [1982]. In the case of Menn's surface it is possible to find parametriza tions of the flecnodal and parabolic curves by simple calculations, which allow us to compute \(\mathfrak{B}_{i}=A_{i}\left(\mathfrak{B}_{1}\right) \subset \mathbf{P}^{2}, i=1,2\), via the asymptotic ray map. The fact that the above diagram commutes makes it possible to giving \(x=18 y^{2}\). Applying the asymptotic ray map to ( \(18 y^{2}, y\) ) gives two projective curves \(\left(-4 y: 1: 180 y^{3}\right)\) and \(\left(6 y: 1:-170 y^{3}\right)\), where the former corresponds to \(A_{2}\left(18 y^{2}, y\right)\). Next, we have to find a relation between the coordinates \((X: Y: Z) \subset \mathbf{P}^{2}\) and the coordinates \((A, C)\) in the closed disk \(\mathfrak{D}^{*}\) that represents \(\mathbf{P}^{2}\). Recall the matrix \(R\) of Euler parameters (see section 2) where \(B=0\) :

$$
R=\left(\begin{array}{ccc} D^{2}+A^{2}-C^{2} & -2 C D & 2 A C \\ 2 C D & D^{2}-C^{2}-A^{2} & -2 A D \\ 2 A C & 2 A D & D^{2}+C^{2}-A^{2} \end{array}\right)
$$

$$
\begin{aligned} & {\left[-x-7 y^{2},\left(5 C y^{2}-4 A^{5}+20 A^{2} C^{3}-8 A^{3} C^{2}\right.\right.} \\ & +20 C^{5}-4 A C^{4}-20 C^{3}+4 A C^{2} \\ & \left.+4 A^{3}\right),\left(10 A^{2} y-5 y+4 A^{3} D+4 A C^{2} D\right. \\ & \left.-2 A D-20 C^{3} D+10 C D\right),\left(A^{2}+C^{2}\right. \\ & \left.+D^{2}-1\right), D g_{1}(A, C), \\ & \left.\left(A^{2}+C^{2}-1\right) g_{1}(A, C)\right] \end{aligned}
$$

where \(A^{2}+C^{2}+D^{2}=1\). An asymptotic line \(A_{i}(x(y), y)\), for \(i=1,2\) and some fixed \(y\), is related to the line of projection \(e_{Y}:=(0: \lambda: 0), \lambda \neq 0\), by the projective transformation \(R \cdot\left[A_{l}(x(y), y)\right]^{T}=\left(e_{Y}\right)^{T}\). Hence, for any given \(y\), we can solve the system of 4 quadratic equations for ~, A, C, and D. Ify varies we obtain solution curves 23~, 232 (or, strictly speaking, ~1, ~z in the notation of section 3) on the sphere \(A_{2}\) + \(C_{2}\) + \(D_{2}=1\) and corresponding curves 23~, 23~ in ~* C \(R_{2}\). Let I~ C Z[A, C, D, y, X], i = 1, 2, denote the ideals defined by (*) and let gi(A, C) denote the polynomial in the reduced standard basis of Ii (with respect to the lexicographical ordering given by A -~ C -~ D ~ y ~ X) that depends only on A and C, then 23~ = {(A, C) E ~* : gl(A, C) = 0} and 23~ = {(A, C) ~ ~ : g2(A, C) = 0}. Using the Buchberger algorithm of the MAPLE [1988] system, we get for the projective curves Al(x(y), y) = (y : 1 : 5y 3) and A2(x(y), y) = (-4y : 1 : 180y 3) the following defining equations for the view bifurcation sets 23~, 23~ of Menn's surface (note that here and in the following, the leading coefficients of elements of the standard bases might be different from one to avoid rational coefficients):

$$
\begin{aligned} g_{1}=A-4 & A^{3}-4 A C^{2}+20 C^{3}+4 A^{5} \\ + & 8 A^{3} C^{2}-20 A^{2} C^{3}+4 A C^{4}-20 C^{5} \end{aligned}
$$

\begin{array}{r} H=\left[\left(2 C^{2} D^{2}-2 C D\left(2 D^{2}-1\right) y+\right.\right. \\ \left.3\left(2 D^{2}-1\right) y^{2}+\left(2 D^{2}-1\right) x\right) \\ D\left(A^{5}+2 A^{3} C^{2}-2 A^{3} D^{2}+A C^{4}-2 A C^{2} D^{2}\right. \\ \left.+A D^{4}-8 C^{3} D^{2}\right)+12 C^{2} D^{2}\left(2 D^{2}-1\right) y \\ \left.\left.+9 C D\left(2 D^{2}-1\right)^{2} y^{2}-4\left(2 D^{2}-1\right)^{3} y^{3}\right)\right] \end{array}

$$
\begin{aligned} g_{2}=4 A & -16 A^{3}-16 A C^{2}-45 C^{3}+16 A^{5} \\ & +32 A^{3} C^{2}+45 A^{2} C^{3}+16 A C^{4}+45 C^{5} \end{aligned}
$$

$$
\begin{aligned} A^{2}+C^{2}+D^{2}-1 & =h_{2}(A, C, y) \\ & =\frac{\partial h_{2}(A, C, y)}{\partial y}=0 \end{aligned}
$$

Now we want to compare these results with the results obtained by the methods described in section 4. The following is a standard basis \(G(~x)\) of the ideal \(I(~31)\) C Z[A, C, D, x, y], whose defining equations were given in section 2, for \(Z(x,y)\) = y4 + xy2 _ x 2 and the lexicographical ordering defined in section 4:

This is consistent with the result above: \(G\left(\tilde{\mathfrak{B}}_{1}\right) \cap \mathbf{Z}[A, C]\) gives the bivariate polynomial \(\left(A^{2}+C^{2}-\right.\) 1) \(g_{1}(A, C)\), where the equator \(A^{2}+C^{2}=1\) is not

$$
\begin{align*} R \cdot\left[A_{l}(x(y), y)\right]^{T}-\left(e_{Y}\right)^{T} & =A^{2}+C^{2}+D^{2}-1 \tag{*}\\ & =0 \end{align*}
$$

Now there are two possible ways of computing \(\mathfrak{B}_{2}^{*}\) : first, one could calculate a standard basis \(G\left(\tilde{\mathfrak{B}}_{2}\right)\) and take the intersection of \(\mathfrak{D}^{*}\) with the element \(G\left(\mathfrak{B}_{2}\right) \cap \mathbf{Z}[A, C]\) of \(G\left(\tilde{\mathfrak{B}}_{2}\right)\). The second possibility, which in the case of Menn's surface turns out to be more efficient, is to calculate the set of parameters \((A, C) \in \mathscr{D}^{*}\) such that \(I_{c} \subset \mathbf{Z}[A, C, D, x, y]\) has solutions of multi plicity greater than one (recall that this gives us \(\mathfrak{B}_{1}^{*} \cup \mathfrak{B}_{2}^{*}\), where we already know \(\mathfrak{B}_{1}^{*}\) ). first, we calculate a standard basis \(H\) for \(J_{\ell}(x, y)=\nabla_{V_{\ell}} f_{\ell}(x, y)=0\) with respect to the lexicographical ordering \(x>y\) of the independent variables (here we regard \(\ell=(A, C, D)\)

The first element of \(H\) is linear in \(x\); to obtain the multi ple solutions of \(I_{c}\) it is hence enough to calculate the discriminant of the second element \(h_{2}\) of \(H\). A stan dard basis \(K\) of with respect to the ordering A -{ C ~ D -{ y is given by the following:

Recall that \(g_{1}\) and \(g_{2}\) define the view bifurcation sets \(\mathfrak{B}_{1}^{*}\) and \(\mathfrak{B}_{2}^{*}\) that we have obtained from the asymptotic ray map. The set \(\partial \mathscr{D}^{*}=\left\{2 A^{2}+2 C^{2}=1\right\}\) does not correspond to multiple solutions of \(h_{2}\), unless \(2 A^{2}=The degree of Menn's surface is four, the set \( \mathfrak{B}_{5}^{*}\) (corresponding to multilocal singularities of the appar ent contour, namely to pairs of folds in 2-point contact) may therefore be nonempty. Note that the multilocal singularities are not related to the asymptotic ray map. A standard basis of \(I\left(\tilde{\mathfrak{B}}_{5}\right) \subset \mathbf{Z}\left[A, C, D, x_{1}, y_{1}, x_{2}, y_{2}\right]\) with respect to the ordering given in section 4 can be computed using MAPLE, the result is, however, several pages long and is not listed here. Some elements of this standard basis, for example, \(\left(A^{2}+C^{2}-1\right)\left(y_{2}-\right. \left.y_{1}\right) g_{1}(A, C)\), factorize. An inspection of \(G\left(\tilde{\mathfrak{B}}_{5}\right)\) shows that \(I\left(\tilde{\mathfrak{B}}_{5}\right)\) consists of the 3-dimensional component

$$
\begin{aligned} I\left(\Delta_{5}^{1}\right)=\left(x_{2}\right. & -x_{1}, y_{2}-y_{1}, A+2 x_{2} y_{2} \\ & \left.+3 C y_{2}^{2}+4 y_{2}^{3}, A^{2}+C^{2}+D^{2}-1\right) \end{aligned}
$$

which does not correspond to genuine double points of the apparent contour, and certain 0-dimensional com ponents. The set \(\mathfrak{B}_{5}^{*} \subset \mathfrak{D}^{*}\) consists of a single point \((A, C)=(0,0)\) and the corresponding view of Menn's surface \(S\) contains a singularity of infinite codimension: the projection of \(S\) along the \(Y\)-axis, \(f(x, y)=\left(x, y^{4}+\right. x y^{2}-x^{2}\) ), gives rise to an apparent contour consisting of the plane curves \(t \mapsto(t, 0)\) and \(s \mapsto\left(-2 s^{2},-5 s^{4}\right)\), where the second branch is \(2: 1\).

$$
\begin{aligned} & P_{0,1}=(-11585 / 32768,-3523 / 8192) \\ & P_{0,2}=(-11585 / 32768,-2029 / 16384) \\ & P_{0,3}=(-11585 / 32768,1723 / 16384) \\ & P_{0,4}=(-11585 / 32768,1685 / 4096) \\ & P_{1,1}=(11585 / 32768,-1685 / 4096) \\ & P_{1,2}=(11585 / 32768,-1723 / 16384) \\ & P_{1,3}=(11585 / 32768,2029 / 16384) \\ & P_{1,4}=(11585 / 32768,3523 / 8192) \end{aligned}
$$

Using the methods described in section 5 we find that \(\mathbb{C}\) consists of two components. The projection to \(S^{2}\) of the intersection of the "cusp surface," defined by the homogeneized ideal \(I_{c}\), with the hyperplane at infinity gives the curve \(A^{2}+C^{2}+D^{2}-1=2 A^{2}+2 C^{2}

Next, we want to compute the stable views of Menn's surface using the methods described in section 5. first, we compute a CAD of \(\mathfrak{D}^{*}\) : let \(F_{0}=\left\{g_{1}(A, C), g_{2}(A\right.\), where res denotes the usual resultant with respect to \(C\) (note that, by a remark of Collins [1975], we can replace the \(k\) th principal subresultants \(\mathrm{psc}_{k}\) in the definition of \(F_{1}\) of section 5 by the usual resultants res if \(F_{0}\) consists of bivariate polynomials). A computation using MAPLE yields the set of polynomials shown in table 1. Each distinct real root of one of the elements of \(F_{1}\) is contained in one of the intervals shown in table 2. Among the real roots described by these intervals three are contained in the closed interval \([-1 / \sqrt{ } 2,1 / \sqrt{ } 2]\), namely the ones contained in [ \(-5793 / 8192,-11585 /\) Discarding the roots \(\alpha_{j}\) such that \(\left(P_{\imath}, \alpha_{j}\right) \notin \mathfrak{D}^{*}\), for

Next we want to eliminate representatives of neighbor ing 2-cells that do not correspond to topologically dis tinct views of Menn's surface. To do this we have to calculate the invariants \(c\left(P_{i, j}\right)\) and \(d\left(P_{i, j}\right)\) for each representative-this is sufficient because, firstly, the degree of Menn's surface is four so that no triple-fold crossings Table 1. The set F~ C Z[A].

$$
\begin{aligned} & F_{1}= \\ & \left\{4 A-16 A^{3}+16 A^{5}, A-4 A^{3}+4 A^{5},\right. \\ & -657794050200000 A^{15}+3946764301200000 A^{13}-10365503565582000 A^{11} \\ & +14486898288798000 A^{9}-11748635409924000 A^{7} \\ & +5601886831404000 A^{5}-1462711636350000 A^{3}+161425203750000 A \text {, } \\ & 32 A^{2}-16 \text {, } \\ & 556236800000 A^{15}-3337420800000 A^{13}+8572018688000 A^{11} \\ & -11956191232000 A^{9}+9797577216000 A^{7}-4730753536000 A^{5} \\ & +1246838400000 A^{3}-138240000000 A \text {, } \\ & 1953125000000 A^{17}-5859375000000 A^{15}+7324218750000 A^{13} \\ & -4882812500000 A^{11}+1831054687500 A^{9}-366210937500 A^{7} \\ & +30517578125 A^{5} \text {, } \\ & 16200 A^{6}-24300 A^{4}+12150 A^{2}-2025 \text {, } \\ & \left.3200 A^{6}-4800 A^{4}+2400 A^{2}-400\right\} \end{aligned}
$$

- -657794050200000A15 + 3946764301200000A 13-10365503565582000Atl

- 14486898288798000,49 11748635409924OOOA 7

- 5601886831404000A 5-1462711636350000A 3 + 161425203750000A,

- 11956191232000A 9 + 9797577216000A 7-4730753536000A 5

- 1246838400000A 3-138240000000A,

- -4882812500000AJI + 1831054687500A 9-366210937500A 7

- 30517578125A 5,

Table 2. Intervals containing real roots of elements of \(F_{1}\).

$$
\begin{aligned} &\left\{[0,0],\left[\frac{11585}{16384}, \frac{5793}{8192}\right],\left[-\frac{5793}{8192},-\frac{11585}{16384}\right]\right. \\ & {\left[-\frac{12587}{16384},-\frac{6293}{8192}\right],\left[\frac{13043}{16384}, \frac{3261}{4096}\right],\left[\frac{6293}{8192}, \frac{12587}{16384}\right] } \\ & {\left.\left[-\frac{3261}{4096},-\frac{13043}{16384}\right]\right\} } \end{aligned}
$$

Table 3. Intervals containing real roots "over" \(P_{0}\).

$$
\begin{aligned} & \hline\{[0,0], {\left[\frac{10033}{16384}, \frac{5017}{8192}\right],\left[-\frac{5017}{8192},-\frac{10033}{16384}\right] } \\ & {\left[\frac{1723}{8192}, \frac{3447}{16384}\right],\left[\frac{1893}{2048}, \frac{15145}{16384}\right],\left[-\frac{3881}{4096},-\frac{15523}{16384}\right], } \\ & {\left.\left[\frac{15689}{16384}, \frac{7845}{8192}\right],\left[-\frac{4059}{16384},-\frac{2029}{8192}\right],\left[-\frac{7507}{8192},-\frac{15013}{16384}\right]\right\} } \\ & \hline \end{aligned}
$$

Table 4. Intervals containing real roots "over" \(P_{1}\).

$$
\begin{aligned} &\left\{[0,0] \cdot\left[\frac{10033}{16384}, \frac{5017}{8192}\right],\left[-\frac{5017}{8192},-\frac{10033}{16384}\right]\right. \\ & {\left[\frac{15523}{16384}, \frac{3881}{4096}\right],\left[-\frac{3447}{16384},-\frac{1723}{8192}\right],\left[-\frac{15145}{16384},-\frac{1893}{2048}\right], } \\ & {\left.\left[\frac{2029}{8192}, \frac{4059}{16384}\right],\left[\frac{15013}{16384}, \frac{7507}{8192}\right],\left[-\frac{7845}{8192},-\frac{15689}{16384}\right]\right\} } \\ & \hline \end{aligned}
$$

can occur and, secondly, there are no multiple compo nents of \(\mathfrak{B}^{*}\) in \(\mathfrak{D}^{*}\). Computing standard bases of the ideals \(I_{c}\) and \(I_{d}\) (defined in section 5) for \(P=P_{t, j}\), and counting the respective numbers of real solutions such that \(D \geq 1 / \sqrt{ } 2\) gives

```text
Now consult figure 7: for each C j we consider the neighboring cell above (recalling that antipodal points of a~* are identified and that R = R) and to the right and eliminate all cells in this neighborhood with c and d equal to c(Pij) and d(Pi,j) with the exception of the cell Ck for which v k is maximal (v k being the position of Ck in the ordered set S of all 2-cells of the CAD-see section 5). Clearly, this reduces the set of representatives to the quintuple {P0,2, P0,3, PI,2, el,3, Pl,4}, giving the following view graph of Menn's surface:
```

$$
\begin{aligned} & c\left(P_{0,1}\right)=c\left(P_{0,4}\right)=c\left(P_{1,1}\right)=c\left(P_{1,4}\right)=3 \\ & c\left(P_{0,2}\right)=c\left(P_{0,3}\right)=c\left(P_{1,2}\right)=c\left(P_{1,3}\right)=1 \end{aligned}
$$

$$
\begin{aligned} d\left(P_{0,1}\right) & =d\left(P_{0,3}\right) \\ & =d\left(P_{0,4}\right)=d\left(P_{1,1}\right) \\ & =d\left(P_{1,2}\right)=d\left(P_{1,4}\right)=1 \\ d\left(P_{0,2}\right) & =d\left(P_{1,3}\right)=0 \end{aligned}
$$

## 8 Conclusions

We have described a symbolic algorithm for computing view graphs of nonsingular algebraic surfaces given by a parametrization in the case of orthogonal projection and have derived an upper bound for the number of topologically distinct, stable projections of such surfaces (i.e., for the number of nodes in the view graph). Apart from the generalizations of this algorithm, already mentioned in section 1, to piecewise algebraic surfaces and to the case of central projections there is the improvement of the efficiency of the present algorithm as an important goal of future work. The standard

![Figure 7. The 2-cells of the CAD in p2.](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-7-p022.png)

*Figure 7. The 2-cells of the CAD in p2.: The 2-cells of the CAD in p2. The views of Menn's surface corresponding to the P,a are shown in figure 8.*

![Figure & The aparens consours corresponding to the connected components of PF \ (8 U $).](/Users/evanthayer/Projects/stepview/docs/1992_global_bifurcation_sets_stable_projections_nonsingular_algebraic_surfaces/figures/figure-8-p023.png)

*Figure & The aparens consours corresponding to the connected components of PF \ (8 U $).: Fig. & The aparens consours corresponding to the connected components of PF \ (8 U $). Fig, 8. The aparent contours corresponding to the connected components ofp2 \ (~ U ~).*

basis computations for the ideal defining the varieties \(\tilde{\mathfrak{B}}_{i}\) are the main computational bottleneck of the pre sent method, and these computations could be speeded up by working modulo some sufficiently large prime number rather than over the integers (of course, an upper bound for the size of the integer coefficients of polynomials arising in the intermediate steps of the stan dard basis computation is required in order to guarantee the correctness of the resulting standard basis). Finally, we would like to mention a more theoretical question.

## 9 Index of Frequently Used Symbols

- ~1 set of projection directions giving rise to lip beakto-beak singularities (or worse); see section 3

- 22... swallowtail

$$
\( \mathfrak{B}_{2} \ldots \) swallowtail singularities ...; see section 3
$$

- 23... triple-fold crossings...; see section 3

- ~4... cusp fold intersections...;

- 235... nontransverse fold crossings... ; see section 3

- projection directions giving rise to singularities "at infinity"; see section 5

- ~ algebraic set in p2 x R 2t such that ~i ----7f(~z), where 7r is the projection on 1st factor; see section 3

- ~ algebraic set in p2 containing the semialgebraic set ~i; see section 4

- 23~ set obtained by projecting ~i onto a closed disk ~* C R2; see section 4

## Acknowledgements

I am grateful to Thomas Stiefvater for stimulating conversations and for his help in implementing certain parts of the algorithm. A first version of the present algorithm was developed during a visit to the Mathematics Institute at the University of Warwick, England, in 1988, during which the author was supported by a Royal Society fellowship.

## References

- Arnol'd, V.I. 1983. Singularities ofsystems of rays. Russian Math. Surveys 38: 87-176.

- Arnon, D.S., Collins, G.E., and McCallum, S. 1984. Cylindrical algebraic decomposition I: the basic algorithm and II: an adjacency algorithm for the plane. SIAMJ. Comput. 13:865-877 and 878-889.

- Banchoff, T., Gaffney, T., and McCrory, C. 1982. Cusps of Gauss Mappings. Pitman Publishing: Boston-London-Melbourne.

- Besl, P.J., and Jain, R.C. 1985. Three-dimensional object recognition. ACM Comput, Surveys 17: 75-145.

- Bochnak, J., Coste, M., and Roy, M.-E 1987. G~omdtrie algdbrique r~ele. Springer Verlag: Berlin-Heidelberg.

- Buchberger, B. 1969. Ein algorithnusches Kfiterium liir die Lrsbarkeit eines algebraischen Glelchungssystems. Aequationes Math. 4: 374-383.

- Buchberger, B. 1985. Groebner bases: an algorithmic method in polynomial ideal theory. In Multidimensional Systems Theory, N.K. Bose (ed.). Reidel: Dordrecht-Boston-Lancaster, pp. 184-232.

- Callahan, J., and Weiss, R. 1985. A model for descrthmg surface shape. Proc. IEEE Conf. Comput. Vision Part. Recogn., San Francisco, pp. 240-245.

- Chakravarty, I., and Freeman, H. 1982. Characteristic views as a basis for three-dimensional object recogniton. Proc. SPIE 336: 37-45.

- Chin, R.T., and Dyer, C.R. 1986. Model-based recognition in robot vismn. ACM Comput. Surveys 18: 67-108.

- Collins, G.E. 1975. Quantifier elimination for real closed fields by cylindrical algebraic decomposition. Proc. 2nd GI Conf. Automata Theory and Formal Languages. Springer LNCS 33, Springer Verlag: Berlin-Heidelberg-New York, pp. 134-183.

- Collins, G.E., and Loos, R. 1982, Real zeros of polynomials. In Computing, Supplementum 4 Springer-Verlag: Wien-New York.

- Eggert, D., and Bowyer, K. 1989. Computing the orthogonal projection aspect graph of solids of revolution. Proc. 1EEE Workshop on Interpretation of 3-D Scenes. New York, pp. 102-108.

- Fekete, G., and Davis, L.S. 1984. Properly spheres: a new representation for 3-D recognition. Proc. IEEE Workshop on Computer Vision: representation and Control. New York, pp. 192-201.

- Gaffney, T., and Ruas, M. 1977. Unpublished work. See also T. Gaffney, The structure of TA(f), classification, a d an application to differential geometry. Proc. Symposia in Pure Math. 40:1. American Mathematical Society, Providence, RI, 1983, pp. 409-427.

- Giblin, P.J. 1977. Graphs, surfaces, and homology. Chapman and Hall: London.

- Gigus, Z., and Malik, J. 1988. Computing the aspect graph for line drawings of polyhedral objects. Proc. (1EEE) Intern. Conf. Robotics and Automation, Philadelphm, pp. 1560-1566.

- Gigus, Z., Canny, J., and Seldel, R. 1988. efficiently computing and representing aspect graphs of polyhedral objects. Proc. 2nd Internat. Conf. Computer Vision, Florida, pp. 30-39.

- Goad, C. 1983, Special purpose automatic programming for 3-D model-based vision. Proc. DARPA Image Understanding Workshop, Arlington, VA, pp. 94-104. Greenberg, M.J., and Harper, J.R. 1981. Algebraic topology: afirst course. Benjamin-Cummings Publishing: Reading, MA. Grimson, W.E.L., and Lozano-P~rez, T. 1984. Model-based recogmtion and localization from sparse range or tactile data. Intern. J. Robotics Res. 3: 3-35. Kergosien, Y.L. 1981. La famille des projections orthogonales d'une surface et ses smgularit~s. C.R. Acad. Sci. Paris 292: 929-932. Kergosieu, Y.L., and Thom, R. 1980. Sur les points parabohques des surfaces. C.R. Acad. Sci. Paris 290: 705-710. Klein, E 1922. The mathematical theory of the top. In Gesammelte mathemansche Abhandlungen, Zweiter Band. Springer Verlag: Berlin, pp. 618-654. Koenderink, J.J. 1986. The mternal representataon of sohd shape based on topological properties of the apparent contour. Image Understanding 198586, W. Richards and S. Ullman (eds.). Ablex Publishing: Norwood, NJ, pp. 257-286. Koenderink, J.J., and van Doorn, A.J. 1976. The singularities of the visual mapping. Biological Cybernetics 24: 51-59. Kriegman, D.J., and Ponce, J. 1990. Computing exact aspect graphs of curved objects: sohds of revolution. Intern. J. Comput. Vision 5: 119-135. Malik, J. 1987. Interpreting hne drawings of curved objects. Intern. J. Comput. Vision 1: 73-103. MAPLE Reference Manual, 5th ed., 1988, Symbolic computation group, Dept. of Computer Science, Umversity of Waterloo, Waterloo, Ontario N2L 3G1, Canada. Mather, J.N. 1973. Generic projections. Ann of Mathematics 98: 226-245. Mdnor, J. 1964. On the Betti numbers of real varieties. Proc. Amer. Math. Soc. 15: 275-280. Mishra, B., and Yap, C.K. 1989. Notes on Grrbner bases. Information Sciences 48: 219-252. Murray, D.W. 1988. Strategies in object recognition. Preprint. Prill, D. 1986. On approximations and incidence m cylindrical algebraic decompositon. SlAM J. Comput. 15: 972-993. Rieger, J.H. 1987a. Families of maps from the plane to the plane. J. London Math. Soc. 36: 351-369. Rieger, J.H. 1987b. On the classification of views of piecewise smooth objects. Image Vision Comput. 5: 91-97. Rieger, J.H. 1990a. The geometry of view space of opaque objects bounded by smooth surfaces. Artificial Intelligence 44:1-40 Rieger, J.H. 1990b. Versal topological stratification and the bifurcation geometry of map-germs of the plane. Math. Proc. Cambridge Philos. Soc. 107: 127-147. Stewman, J., and Bowyer, K. 1988. Creating the perspective projection aspect graph of polyhedral objects. Proe. 2nd Intern. Conf. Comput. Vision, Tampa, FL, pp. 494-500. Stiefvater, T. 1989. Ein symbolischer Algorithmus zur Berechnung von semialgebraxschen Zellen in der Ebene. Studienarbeit, Fakult~t ftir lnformatlk: Universitiit Karlsruhe, ER.G. Tari, F. 1990. Projections of piecewise-smooth surfaces. Preprint. University of Liverpool, England. Trinks, W. 1978. 0ber B. Buchbergers Verfahren, Systeme algebraischer Gleichungen zu losen. J. Number Theory 10: 475-488. van der Waerden, B.L. 1939. Einf~hrung in die algebraische Geometrie. Springer Verlag: Berlin. Walker, R.J. 1950. Algebraic curves. Princeton University Press. Princeton, NJ; Springer Verlag: Berhn, 1978. Whitney H 1955. On singularities of mappings of Euchdean spaces. I. Mappings of the plane into the plane. Ann. of Mathematics 62: 374-410.
