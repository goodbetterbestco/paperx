# Partitioning Trimmed Spline Surfaces into NonSelf-Occluding Regions for Visibility Computation

Shankar Krishnan, NonSelf-Occluding Regions for, Dinesh Manocha, Visibility Computation

AT&T Research Labs
180 Park Avenue
Room E-201, Florham Park, New Jersey 07932

Department of Computer Science
University of North Carolina
Chapel Hill, North Carolina 27599-3175

AT\&T Research Labs
180 Park Avenue
Room E-201, Florham Park, New Jersey 07932

Department of Computer Science
University of North Carolina
Chapel Hill, North Carolina 27599-3175

## Abstract

Computing the visible portions of curved surfaces from a given viewpoint is of great interest in many applications. It is closely related to the hidden surface removal problem in computer graphics, and machining applications in manufacturing. Most of the early work has focused on discrete methods based on polygonization or ray-tracing and hidden curve removal. In this paper we present an algorithm for decomposing a given surface into regions so that each region is either completely visible or hidden from a given viewpoint. Initially, it decomposes the domain of each surface based on silhouettes and boundary curves. To compute the exact visibility, we introduce a notion of visibility curves obtained by projection of silhouette and boundary curves and decomposition of the surface into nonoverlapping regions. These curves are computed using marching methods and we present techniques to compute all the components. The nonoverlapping and visible portions of the surface are represented as trimmed surfaces and we present a representation based on polygon trapezoidation algorithms. The algorithms presented use some recently developed algorithms from computational geometry like triangulation of simple polygons and point location. Given the nonoverlapping regions, we use an existing randomized algorithm for visibility computation. We also present results from a preliminary implementation of our algorithm. © 2000 Academic Press

## Funding Note

' Supported in part by an Alfred P. Sloan Foundation Fellowship, ARO Contract P-34982-MA, NSF Grant CCR-9625217, ONR Young Investigator Award, and Intel.

## 1 INTRODUCTION

The problems of visibility and accessibility computations are fundamental for computer graphics, computer-aided design, and manufacturing applications. In particular, hidden line and surface removal algorithms in computer graphics are related to visibility computations [FDHF90, Hor84, SSS74, HG77]. Similarly, accessibility computations in manufacturing applications are based on Gauss maps and visibility sets [Woo94, CCW93, GWT94]. These problems have been extensively studied in computer graphics, computer-aided design, computational geometry, and manufacturing literature. In this paper, we are dealing with algebraic surfaces and surfaces defined using rational splines [Far93] that are differentiable.

Given a viewpoint, the hidden surface removal problem deals with computation of the surface boundary visible from that viewpoint. Most of the earlier algorithms in the literature are for planar and polygonal primitives and hidden line removal [FDHF90, Mul89, SSS74]. In the computational geometry literature, many of the hidden surface algorithms simply calculate the entire arrangement of lines (projections of edges and vertices of the objects on the viewing plane). Output-sensitive hidden surface algorithms were developed for special input cases like c-oriented solids [GO87], axis-parallel rectangles [PVY92], and polyhedral terrains [RS88]. Very few algorithms are able to cope with cycles (impossible to obtain an ordering among the faces without splitting some of them) efficiently. A randomized algorithm to generate the visibility map was given by Mulmuley [Mul90] for the general case. The algorithm maintains the trapezoidation of the visibility map and updates it by randomly adding one face at a time. The algorithm is (almost) output-sensitive. Extensions of the hidden surface algorithm from planar to curved faces are described in [Mul90]. A survey of most of the recent results in computational geometry regarding object-space hidden surface removal is presented in [Dor94].

When dealing with curved surfaces, most hidden surface removal algorithms must be capable of manipulating semialgebraic sets [Mul89]. Results from elimination theory and algebraic decision procedures like Gröbner bases are usually used for this purpose [Can88]. Unfortunately, algorithms based entirely on symbolic manipulation require infinite precision to represent algebraic numbers. Bounds based on gap theorems [Can88] have been used to compute their bit-complexity. However, implementations of these algorithms are very nontrivial and applicability of these bounds in practical situations are still not clear. Given a model composed of algebraic or parametric surfaces, it can be polygonized and algorithms developed for polygonal models can then be applied. However, the accuracy of the overall algorithm is limited by the accuracy of the polygonal approximation. Other algorithms for visibility computations are based on ray-tracing or scan-line conversion [FDHF90]. These algorithms are slow (may take a few seconds for each patch) and lead to data proliferation. Furthermore, their accuracy is limited by the image or device precision. These techniques are device resolution dependent and many applications in modeling and rendering demand a device-independent representation [TW93]. For example, many data standards for 2D and 3D models (e.g., the PostScript language) use higher order or deviceindependent representations.

![FIG. 1. Local visibility computations based on silhouettes.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-1-p003.png)

*FIG. 1. Local visibility computations based on silhouettes.: Local visibility computations based on silhouettes.*

At this point there are two Z values for the same front facing surface piece. These points are shown as "x*es in the parameter space

Patch Coordinates 261.747 102.9-57.4605 199.883 95.7857 28.4751 82.1126 93.3985 120.048-56.2504 112.366 87.0828

173.737-97.1096 20.224 6.4257 41.7767 113.64

2. 209 3 18 1647497

57.5666 84 3559 194.299-74.642 105.59 142.717

More recently, a hidden curve removal algorithm has been presented for parametric surfaces by Elber and Cohen [EC90] based on silhouette curves. A silhouette curve is defined as the locus of points on the surface where the normal vector is orthogonal to the viewing direction. In this paper [EC90], they extract the curves of interest by considering boundary curves, silhouette curves, isoparametric curves and curves along \(C^{1}\) discontinuity based on 2D curve-curve intersections. Given a curved surface model and a viewpoint, the silhouettes on the model partition it into front facing and back facing regions (as shown in Fig. 1). The surfaces obtained after partitioning based on the silhouette computation need not be completely visible, as shown in Fig. 1.

We present an algorithm for decomposing a spline surface into nonoverlapping regions from a given viewpoint. Given a model, we represent it as a series of Bézier surfaces using knot-insertion algorithms. Each Bézier surface is partitioned into nonoverlapping regions (these regions can overlap with each other but not with themselves) based on silhouette and visibility curves (refer to Section 5). Each computed region has the property that it is either entirely visible or invisible in the absence of other surfaces. The visibility curves are computed based on the silhouette and boundary curves. Each nonoverlapping region is represented as a trimmed Bézier surface bounded by silhouettes, visibility, and boundary curves. Since the trimming curves are algebraic in nature, it is not possible to provide a representation (like parametric curves) that is truly resolution independent. Instead, we provide a piecewise linear approximation of the algebraic curve and an analytic representation which can be refined on demand using well-known minimization methods. Given a collection of these trimmed surfaces, we then use a slight variation of an existing randomized algorithm [Mul89] to compute the visible portions for hidden surface removal.

In this paper we assume that the input model is composed of nonintersecting surfaces. Given any arbitrary model, we initially decompose it into noninteresecting surfaces using our surface intersection algorithm [KM97]. This algorithm uses a combination of symbolic techniques and results from numerical linear algebra. We have implemented the algorithm for decomposing each surface into nonoverlapping regions in finite precision (using 64-bit double precision floating-point arithmetic). The actual performance of the algorithm varies with the viewpoint and surface geometry. On an average it takes about 40-70 ms to decompose one bicubic patch into nonoverlapping regions. The main goal of this paper is to present an algorithm for reducing the hidden surface removal problem for spline surfaces to that of polygonal models. Coupled with such an algorithm for polygonal models, we obtain a complete visible surface extraction algorithm for spline surfaces. A preliminary version of this paper appeared in [KM98].

The rest of the paper is organized in the following manner. Section 2 presents background material and reviews algorithms from computational geometry and numerical linear algebra used in the rest of the paper. Section 3 briefly describes an overview of our algorithm. We outline an efficient algorithm for computing the silhouettes based on marching methods in Section 4. We introduce the notion of visibility curves in Section 5 and show that silhouettes and visibility curves partition a general surface into nonoverlapping regions. We present algorithms and implementations for computation of visibility curves in Section 6. In Section 7 we talk about how to apply our decomposition algorithm to accomplish hidden surface removal and give some details about our implementation. For the sake of completeness, we also present a variation of an existing algorithm [Mul89] for hidden surface removal of our decomposed faces in the Appendix.

## 2 BACKGROUND

The overall algorithm for visibility computation uses algorithms from computational geometry and linear algebra. Some of them include trapezoidation of polygons, partitioning a simple polygon using nonintersecting chains, curve surface intersections, and local methods of tracing based on power iterations. We review some of these techniques in this section. Some of the algorithms presented here might not be optimal in terms of worst-case asymptotic complexity; we compromised it in favor of simplicity and ease of implementation.

### 2.1 Triangulating Simple Polygons

We represent trimmed surfaces as well as portions of surfaces obtained after visibility decomposition using nonconvex simple polygons in the domain. These nonconvex polygonal domains are decomposed into triangles for many geometric operations like intersections and partitioning.

To decompose a simple polygon into an optimal number of triangles we use Seidel's algorithm [Sei91]. It is an incremental randomized algorithm whose expected complexity is \(O\left(N \log ^{*} N\right)\), where \(N\) is the number of vertices (in our application, \(N\) is typically

![FIG. 2. Three stages of Seidel's algorithm.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-2-p005.png)

*FIG. 2. Three stages of Seidel's algorithm.: Three stages of Seidel's algorithm.*

between 100 and 200). In practice, it is almost linear time. The algorithm proceeds in three steps as shown in Fig. 2. They are:

- Decompose the polygon into trapezoids in \(O(log*N)\) time (Fig. 2a),

- Generate monotone polygons from the trapezoids in linear time (Fig. 2b), and

- Triangulate the monotone polygons in linear time (Fig. 2c).

The trapezoidation of the polygon is useful in two ways. We can find whether a given point is inside the polygon in \(O(logN)\) time by doing binary search on the trapezoids. Moreover, we can obtain a point inside the polygon in constant time. For the purposes of the visibility computation algorithm, trapezoidation is sufficient. However, the triangulation is eventually used for rendering the visible portions. While there are linear time algorithms to triangulate simple polygons, we chose Seidel's algorithm because there was an efficient inhouse implementation of the algorithm available to us [NM95].

### 2.2 Partitioning a Simple Polygon

We use algorithms for partitioning a simple polygon into connected components based on a set of nonintersecting chains. Given a simple polygon \(P\) and a number of nonin tersecting polygonal chains \(C\), our task is to partition \(P\). We make no assumptions on \(C\) except that each chain \(c_{i} \in C\) in itself should partition \(P\). This algorithm is an impor tant component of our overall algorithm. We use it to partition the domain of parametric patches using silhouette and visibility curves. The goal of this algorithm is to subdivide the original domain of a patch into components each of which have a simple boundary (no interior loops). We make use of this fact later in the paper. The problem at hand has been studied extensively in the computational geometry literature and has been solved efficiently (namely, Bentley-Ottmann [BO79] \(O((n+k) \log n)\) or Chazelle-Edelsbrunner [CE88] \(O(n \log n+k)\) ). Typically, these algorithms compute the arrangement of the line segments and then generate the partitions by walking the faces of the arrangement. We have implemented a slightly modified version. A feature of our implementation is that along with the partitions, we also obtain the connectivity between them. This is used to verify the correctness of our results.

Let us assume for the sake of simplicity that the chains do not form a loop inside the polygon. This is because partitions surrounding the loop will not have a simple boundary anymore. We treat this case separately in our algorithm. Details are provided at the end of the algorithm description. The main idea in this algorithm is the fact that since the chains are nonintersecting, each of the partitioned regions starts and ends at intersection

![FIG. 3. Partitioning a polygon with polygonal chains.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-3-p006.png)

*FIG. 3. Partitioning a polygon with polygonal chains.: Partitioning a polygon with polygonal chains.*

Since the vertices of each chain are given in a specific order, we shall assume that to be the direction of the chain. The algorithm works in two steps.

- Find all the intersection points of each chain with the polygon and number them according to the order in which they occur. We associate three fields with each intersection point-the chain corresponding to each intersection point (type), the number of the intersection point within the chain (rank), and whether the chain was coming in or going out of the polygon at this point (in_or_out). For example, the intersection point aj in the figure has type = a, rank = 1, and in_or-out = out as its three fields. The in or out field is actually unnecessary because rank has that information. However, we use it for ease of description.

- Given all the intersections, we traverse the polygon starting from an arbitrary vertex. We use a stack as a data structure to compute the partitions. Let us assume that we start traversing the polygon from vertex vo in an anticlockwise order for the example given in the figure. Given this traversal, we can order the intersection points around the polygon. In the example, the order would be ao, b3, br, bi, co, ci, bo, a3, az, ai. As we proceed from vertex v; to vj+1 in the polygon, we retrieve all the intersection points of the various chains with the edge (V;, Vi+1) in order. If q is an intersection point, let p be the point on the top of the stack. To determine if q is pushed or p is popped, the following condition is checked.

```text
if (q.type ‡ p.type) push(q); else if ((q.rank - p.rank == 1) && (q.in_or_out == out) && (p.in_or_out == in)) pop (p); else if ((p.rank - q.rank == 1) && (p.in_or_out == out) && (q.in_or_out == in)) pop(p); else push (q);
```

If \(p\) is popped, then \(p\) and \(q\) form a partition of the polygon. The corresponding partition is read out and the chain of vertices between \(p\) and \(q\) is appended to the vertex (this chain will be a part of the partition that involves this vertex) currently on top of the stack (the one that was below \(p\) ). After traversing the polygon completely once, we would have obtained all the partitions.

At this point, we have partitioned the domain using chains that end at the boundary of the domain. However, any loop that is present inside the domain must lie inside one of the partitioned regions. Each of the loops (starting from the innermost if the loops are nested) themselves form a partition. The remaining part of the region (they have boundaries with multiple components) are broken into simple regions by introducing a simple horizontal cut from the loop to the boundary of the partition or the next outer loop. The horizontal cut is made by choosing a point whose \(y\)-coordinate lies between the \(y\) extents of the loop and drawing a horizontal through the point.

### 2.3 Curve Surface Intersection

Computing the intersection of curves and surfaces is needed to find whether a given surface is occluded. Given a surface patch that is guaranteed to have the same visibility for all its points, we shoot a ray from a point on the surface to the viewpoint and determine if the ray intersects any other surface (between the chosen point on the surface and the viewpoint). If the number of intersections is O, the surface is visible; otherwise it is not. We use some recent algorithms for these intersections based on eigenvalue computations [MD94]. The algorithm we describe here can be used for any degree curve and its complexity is cubic in the degree of the curve. Therefore, even though the problem of ray-surface intersection is much simpler, our algorithm does not suffer because of its generality.

Given a parametric representation of a surface \(\mathbf{F}(s, t)\left(\mathbf{F}: \mathcal{R}^{2} \rightarrow \mathcal{R}^{3}\right)\) of degree \(m \times n\), we compute its implicit representation using resultant methods [Dix08] and obtain a matrix formulation \(\mathbf{M}(x, y, z, w)\). The entries of this matrix are linear polynomials in \(x, y, z, w\) (of the form \(a x+b y+c z+d_{w}\) ) so that the set

$$
\begin{equation*} \{(x, y, z, w): \operatorname{Det}(\mathbf{M}(x, y, z, w))=0\} \tag{1} \end{equation*}
$$

is exactly the surface in homogeneous coordinates. One main advantage of this method is that we do not have to compute the large determinant which is highly unstable numerically. We substitute the parameterization of the curve, say \(\mathbf{G}(u)=(\bar{X}(u), \bar{Y}(u), \bar{Z}(u), \bar{W}(u))\) of degree \(d\), into \(\mathbf{M}(x, y, z, w)\) and obtain a univariate matrix polynomial \(\mathbf{M}(u)\). The problem of intersection computation is thus reduced to computing the roots of the nonlinear matrix polynomial \(\mathbf{M}(u)\). The algorithms that are used to compute the roots of a matrix polynomial require a power basis representation. However, our polynomial which is in the Bernstein basis is easily converted to power basis by the transformation \(\bar{u}=\frac{u}{1-u}\). The resulting matrix \(\mathbf{M}(\bar{u})\) can be represented as

$$
\begin{equation*} \mathbf{M}(\bar{u})=\bar{u}^{d} M_{d}+\bar{u}^{d-1} M_{d-1}+\cdots+\bar{u} M_{1}+M_{0}, \tag{2} \end{equation*}
$$

where \(M_{i}\) 's are matrices of order \(2 m_{n}\) with numeric entries. Furthermore, the roots of the matrix polynomial, \(\mathbf{M}(u)\), are identical with the eigenvalues of

$$
C=\left[\begin{array}{ccccc} 0 & I_{2 m n} & 0 & \cdots & 0 \tag{3}\\ \vdots & \vdots & \vdots & \vdots & \vdots \\ 0 & 0 & 0 & \cdots & I_{2 m n} \\ -\overline{\mathbf{M}}_{0} & -\overline{\mathbf{M}}_{1} & -\overline{\mathbf{M}}_{2} & \cdots & -\overline{\mathbf{M}}_{d-1} \end{array}\right],
$$

where \(\overline{\mathbf{M}}_{i}=\mathbf{M}_{d}^{-1} \mathbf{M}_{i}\) [GLR82]. In case \(\mathbf{M}_{d}\) is singular or ill-conditioned, the intersection problem is reduced to a generalized eigenvalue problem [MD94]. Algorithms to compute all the eigenvalues are based on QR orthogonal transformations [GL89].

### 2.4 Power Iterations

We use marching methods to trace the visibility curves (see Section 5). At each iter ation, we pose the problem as an eigenvalue problem and use local methods to compute points on the curve. Power iteration is a fundamental local technique used to compute eigenvalues and eigenvectors of a matrix. Given a diagonalizable matrix, \(\mathbf{A}\), there exists

$$
\mathbf{z}_{k}=\mathbf{A} \mathbf{q}_{k-1} ; \quad \mathbf{q}_{k}=\mathbf{z}_{k} /\left\|\mathbf{z}_{k}\right\|_{\infty} ; \quad s_{k}=\mathbf{q}_{k}^{T} \mathbf{A} \mathbf{q}_{k},
$$

where \(\left\|\mathbf{z}_{k}\right\|_{\infty}\) refers to the \(L_{\infty}\) norm of the vector \(\mathbf{z}_{k} . s_{k}\) converges to the largest eigenvalue \(\lambda_{1}\), and \(\mathbf{q}_{k}\) converges to the corresponding eigenvector \(\mathbf{x}_{1}\).

The basic idea of power iterations can be used and modified to obtain the eigenvalue of a matrix \(\mathbf{A}\) that is closest to a given guess \(s\). It actually corresponds to the largest eigenvalue of the matrix \((\mathbf{A}-s \mathbf{I})^{-1}\). Instead of computing the inverse explicitly (which can be numerically unstable), we use inverse power iterations. Given an initial unit vector \(\mathbf{q}_{0}\), we generate a sequence of vectors \(\mathbf{q}_{k}\) as

$$
\text { Solve }(\mathbf{A}-s \mathbf{I}) \mathbf{z}_{k}=\mathbf{q}_{k-1} ; \quad \mathbf{q}_{k}=\mathbf{z}_{k} /\left\|\mathbf{z}_{k}\right\|_{\infty} ; \quad s_{k}=\mathbf{q}_{k}^{T} \mathbf{A} \mathbf{q}_{k} .
$$

We use inverse power iterations to trace curves. We formulate the curve as the singular set of a matrix polynomial and reduce it to an eigenvalue problem. Given a point on the curve, we approximate the next point on the curve by taking a small step size in a direction determined by the local geometry of the curve. We use this point as our guess and use inverse power iterations to converge back to the curve. The reader is requested to refer to [KM97] to get more details on how we perform curve tracing using inverse power iterations.

## 3 OVERVIEW OF THE ALGORITHM

```text
In this section, we briefly describe the algorithm. The details of individual steps of the algorithm are described in later sections. For the purposes of this paper, we assume that the viewpoint is situated at z= - oo so that the projection on the viewing plane is orthographic. Given a scene composed of nonintersecting Bézier patches and a viewpoint, we perform the following steps for each patch.
```

- Compute the silhouette curves on the patch for the given viewpoint.

- Partition the domain of the Bézier patch as determined by the silhouette curves. The boundary of each partition is made up of the original boundary curves or the computed silhouette curves.

- For each partition so generated,

- —Trace out visibility curves (curves in the interior of the partition that have the same projection on the image plane as that of the boundary curves) by following the boundary curves.

- —Partition the domain according to the visibility curves

The set of partitions obtained after this algorithm is executed satisfy the property that each partition is nonself-occluding. This fact is proved later in Theorem 2. The main complexity of the algorithm lies in the computation of the silhouette and visibility curves. We use a combination of symbolic and numeric techniques to evaluate these curves explicitly.

## 4 SILHOUETTES

Silhouette computation forms an important part of visibility algorithms for curved surfaces. Intuitively speaking, a silhouette curve is the locus of all points on the surface where the normal vector to the surface at that point is perpendicular to the line of sight. We shall restrict our discussion to surfaces whose silhouette (from a given viewpoint) is a curve on the surface. The property of the silhouette curve is that it subdivides the surface into front and back facing regions. However, as shown in Fig. 1, silhouettes alone are not sufficient to determine all visible regions. In this section, we describe an algorithm to compute the silhouette curve on a parametric (represented as Bézier [Far93]) patch efficiently. Some assumptions are in order about the kind of surfaces we deal with. We assume that the surfaces are not self-intersecting purely for exposition. In the most general case, we can compute the intersection curve using the algorithm described in [KM95] and partition the surface into nonintersecting pieces.

We assume for the sake of simplicity that the viewpoint is located at \((0,0,-\infty)\) and that the view direction is toward the positive \(z\)-axis. It is easy to see that even if this is not the case, we can always achieve it by applying an appropriate perspective transformation to the control points of the parametric surface \(\mathbf{F}(s, t)\). We also require that all the surfaces are differentiable everywhere. We formulate the silhouette curve as an algebraic plane curve in the domain of \(\mathbf{F}(s, t)\).

### 4.1 Formulation of the Silhouette Curve

Let \(\mathbf{F}(s, t)\) denote the parametric (differentiable) surface and let \(\phi_{1}(s, t), \phi_{2}(s, t)\) and \(\phi_{3}(s, t)\) denote the mappings from the parametric space to \((x, y, z)\) space.

$$
\begin{gathered} \mathbf{F}(s, t)=\langle X(s, t), Y(s, t), Z(s, t), W(s, t)\rangle \\ \phi_{1}(s, t)=\frac{X(s, t)}{W(s, t)}, \quad \phi_{2}(s, t)=\frac{Y(s, t)}{W(s, t)}, \quad \phi_{3}(s, t)=\frac{Z(s, t)}{W(s, t)} . \end{gathered}
$$

In the rest of the paper, we shall drop the \((s, t)\) suffixes from all the functions for more concise notation. The \(z\)-component of the normal at an arbitrary point on the surface is given by the determinant

$$
N_{z}=\left|\begin{array}{ll} \phi_{1_{s}} & \phi_{1_{t}} \tag{4}\\ \phi_{2_{s}} & \phi_{2_{t}} \end{array}\right|,
$$

where \(\phi_{i_{s}}\) and \(\phi_{i_{t}}\) denote the partial derivatives of the appropriate function \(\phi_{i}\) with respect to \(s\) and \(t\).

$$
\begin{aligned} \phi_{1_{s}} & =\frac{\left(W X_{s}-W_{s} X\right)}{W^{2}} \\ \phi_{1_{t}} & =\frac{\left(W X_{t}-W_{t} X\right)}{W^{2}} \\ \phi_{2_{s}} & =\frac{\left(W Y_{s}-W_{s} Y\right)}{W^{2}} \\ \phi_{2_{t}} & =\frac{\left(W Y_{t}-W_{t} Y\right)}{W^{2}} \end{aligned}
$$

On the silhouette curve, \(N_{z}=0\). Since \(W(s, t)>0\), we can express the plane curve rep resenting the silhouette as the determinant

$$
N_{z}=\left|\begin{array}{cc} \left(W X_{s}-W_{s} X\right) & \left(W X_{t}-W_{t} X\right) \tag{5}\\ \left(W Y_{s}-W_{s} Y\right) & \left(W Y_{t}-W_{t} Y\right) \end{array}\right|=0 .
$$

Expanding the determinant and rearranging the terms, we can express it as the singular set of the matrix \(\mathbf{M}(s, t)\)

$$
\mathbf{M}(s, t)=\left(\begin{array}{lll} X(s, t) & Y(s, t) & W(s, t) \tag{6}\\ X_{s}(s, t) & Y_{s}(s, t) & W_{s}(s, t) \\ X_{t}(s, t) & Y_{t}(s, t) & W_{t}(s, t) \end{array}\right)=0 .
$$

The singular set of \(\mathbf{M}(s, t)\) is the values of \(s\) and \(t\) which make it singular.

However, there could be cases when \(N_{z}\) starts positive, touches zero, and then becomes positive again. Saddle-shaped regions (oriented appropriately) are examples of these cases. These are not the generic case and small perturbations of the view direction are enough to remove these cases [RE93]. Further, the algebraic formulation of the silhouette curve above does not preclude the possibility of singularities (self-intersections). We believe that singularities of silhouettes (in object space) are also nongeneric and a similar perturbation of the view direction should remove them. However, we are not able to prove it or provide a good reference for it. For the rest of this paper, we will assume that the silhouette curve does not contain singular points.

### 4.2 Silhouette Computation

Let us denote the projected silhouette curve corresponding to \(\operatorname{Det}(\mathbf{M}(s, t))\) by \(D(s, t)\). If the Bézier patch \(\mathbf{F}(s, t)\) is of degree \(m\) in \(s\) and \(n\) in \(t\), the curve \(D(s, t)\) has degree at most \(3(m+n)\). This is a high degree algebraic curve. Our task is to evaluate this curve (i.e., its topological type) completely and efficiently inside our domain of interest.

Our approach is based on marching along the curve using local geometric properties of the curve. All marching methods require at least one point on every component of the curve inside the domain of interest. We adopt different methods to compute starting points on open (intersect the boundary of the domain) and closed components (or loops).

To determine starting points on open components we substitute one of the variables \(s\) or \(t\) with the value 0 or 1. This reduces the silhouette equation to a polynomial equation in one variable and this has only a discrete set of solutions. We find all the boundary silhouette points by determining the roots of four univariate matrix polynomials, \(\mathbf{M}(0, t), \mathbf{M}(1, t)\), \(\mathbf{M}(s, 0)\), and \(\mathbf{M}(s, 1)\). This problem can be reduced to finding the eigenvalues of an associated companion matrix (see Eq. (3)) [MD94]. We retain only the real solutions that lie within the domain.

A much harder problem is to determine if the silhouette curve has loops inside the domain of the surface, and if so to compute at least one point on each of them. We use the fact that the silhouette curve is an algebraic plane curve that is continuous in the complex domain. Since the coefficients of the curve are real, all complex portions of the curve must occur in conjugate pairs. We characterize certain special points on loops (turning points) as places where two complex conjugate paths merge to form a real component. Our idea of loop detection is captured by the following lemma which we state without proof

LEMMA 1 [KM97]. If the curve in the real domain [0, 1] × [O, 1] consists of a closed component, then two arbitrary complex conjugate paths meet at one of the real points (corresponding to a turning point) on the loop.

By following all the complex paths inside the domain we can locate at least a single point on each loop. Figure 4 shows the presence of loops in silhouette curves.

![Figure 4](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-4-2-p021.png)

*Figure 4: TABLE 1 Performance of Our algorithm*

Given a point on each component of the silhouette curve, marching methods obtain approximations of the next point by taking a small step size in a direction determined by the local geometry of the curve. Based on the approximate value, these algorithms use local iterative methods to trace back on to the curve to evaluate the silhouette curve. We have developed an algorithm based on inverse power iterations (Section 2.4) to trace the curve. The details of the complete algorithm are presented in [KM97]. Our algorithm evaluates the silhouette curve at discrete steps to create a piecewise linear approximation. The tracing algorithm has been implemented and tested on a variety of examples and has proved to be fairly robust. Consider a patch \(F(s,t)\) of degree m in s and n in t, and let N= \(max(m,n)\). Then the companion matrix (Eq. (3)), whose eigenvalues correspond to the roots of the matrix polynomial) is of order 3N. We use the QR method [GL89] to compute all the eigenvalues. The number of floating point operations performed is 8NS. In inverse power iterations, the two main operations are the LU decomposition of the matrix and solving the resulting triangular systems. Usually the LU decomposition is computed using Gaussian elimination and it takes about § N° operations (without pivoting). Solving each triangular system costs about {Nº operations. As a result, the inverse power iteration takes about } N3 + { N° operations, where k is the number of iterations. It turns out that the structure of the companion matrix can be used to reduce the number of operations for LU decomposition (9 N operations) as well as to solve the triangular systems (12kN operations, where k is the number of iterations).

### 4.3 Surface Partitioning Based on Silhouettes

Lemma 2. Let \(\mathbf{C} \subset \Re^{3}\) be the set of silhouette curves on a given surface \(\mathbf{S} \subseteq \Re^{3}\) from a given viewpoint. Then \(\mathbf{S}\) can be decomposed into \(\mathbf{C}\) and disjoint regions whose boundaries are surface boundaries and/or parts of \(\mathbf{C}\).

Proof. Let \(p\) be a point on \(\mathbf{S}-\mathbf{C}\) (i.e., \(N_{z}(p) \neq 0\) ). define the (open) region \(\mathbf{R}_{p}\) as follows:

\(\mathbf{R}_{p}=\{s \in \mathbf{S}-\mathbf{C} \mid \exists\) a continuous path from \(p\) to \(s\) without crossing \(\mathbf{C}\}\).

\(\mathbf{R}_{q}\) is defined similarly for a point \(q \notin \mathbf{R}_{p}\), if such a \(q\) exists. Now we have to show that \(\mathbf{R}_{p} \cap \mathbf{R}_{q} \neq \emptyset\). Let us assume the contrary. Then there exists a point \(r \in \mathbf{R}_{p} \cap \mathbf{R}_{q}\). This implies

![FIG. 5. Silhouette curve on the patch and the domain.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-5-p012.png)

*FIG. 5. Silhouette curve on the patch and the domain.: silhouette curve on the patch and the domain.*

silhouette curve that there is a continuous path (without crossing \(\mathbf{C}\) ) from \(p\) to \(r\) and \(r\) to \(q\), and hence from \(p\) to \(q\). This is a contradiction.

From the above lemma we can conclude that \(\mathbf{S}\) can be partitioned into a set of regions \(\mathbf{R}\) so that the boundaries of each region \(\wp \in \mathbf{R}\) consists of original surface boundaries and silhouette curves. The domain of each patch is represented as a simple polygon in counterclockwise order. For example, a complete tensor product Bézier patch has its domain polygon as \(\{(0,0),(1,0),(1,1),(0,1),(0,0)\}\). We then use our partition_polygon (Section 2.2) routine to subdivide the domain into disjoint regions.

We now state without proof a fundamental theorem from vector calculus called the global inverse theorem, which provides the basis for our method [Ful78].

THEOREM 1 [Ful78]. Let \(\mathbf{F}\) be a continuously differentiable mapping defined on an open region \(D \in \Re^{2}\), with range \(R \in \Re^{2}\), and let its Jacobian be never zero in \(D\). Suppose further that \(C\) is a simple closed curve that, together with its interior, lies in \(D\), and that \(\mathbf{F}\) is one-to-one on \(C\). Then the image \(\Gamma\) of \(C\) is a simple closed curve that, together with its interior, lies in \(R\). Furthermore, \(\mathbf{F}\) is one-to-one on the closed region consisting of \(C\) and its interior, so that the inverse transformation can be defined on the closed region consisting of \(\Gamma\) and its interior.

The importance of this theorem lies in the fact that properties of the entire region can be argued by looking at the properties of its boundary.

Consider the vector field \(\mathbf{M}: \Re^{2} \rightarrow \Re^{2}\) so that

$$
\mathbf{M}(s, t)=\left(\phi_{1}(s, t), \phi_{2}(s, t)\right),
$$

where the \(\phi_{i}^{\prime} s\) were defined in the previous section. Intuitively, the vector field \(\mathbf{M}\) projects a point on the surface \(\mathbf{F}(s, t)\) on to the \(x_{y}\) plane. We now relate the silhouette curve and the Jacobian of the function \(\mathbf{M}\).

Lemma 3. Let \(\mathbf{M}\) be a mapping from \(\Re^{2} \rightarrow \Re^{2}\) such that \(\mathbf{M}(s, t)=\left(\frac{X(s, t)}{W(s, t)}, \frac{Y(s, t)}{W(s, t)}\right)\). Then the locus of all points on the surface that have vanishing Jacobians corresponds exactly to the silhouette curve.

Proof. The Jacobian \(J(s, t)\) of \(\mathbf{M}\) is given by

$$
J(s, t)=\left|\begin{array}{ll} \frac{\left(W X_{s}-W_{s} X\right)}{W^{2}} & \frac{\left(W X_{t}-W_{t} X\right)}{W^{2}} \tag{7}\\ \frac{\left(W Y_{s}-W_{s} Y\right)}{W^{2}} & \frac{\left(W Y_{t}-W_{t} Y\right)}{W^{2}} \end{array}\right|
$$

However when \(J=0\), we get the same equation as Eq. (5). That is precisely the equation of the silhouette curve in the domain of the surface. Therefore, the silhouette curves are the only places on the surface where the Jacobian of \(\mathbf{M}\) vanishes.

We denote the set of regions obtained after partitioning by \(R\). Henceforth, we shall be considering a single element of this set \(\wp \in R\). Because of the previous lemma, we can conclude that the interior of each \(\wp \in R\) has no vanishing Jacobian. Therefore, the global inverse theorem applies on each of the regions in \(R\).

## 5 VISIBILITY CURVES

In the previous section, we described a method to compute silhouettes. We shall now introduce the notion of visibility curves and elucidate their role in determining visibility.

Consider a region \(\wp \in R\). Let us denote the boundary of \(\wp\) by \(\partial\) ø and the interior of \(\wp\), the open set \(\wp-\partial\) „ , by \(\operatorname{int}(\wp)\).

Definition 1. Given a region \(\wp \in R\), the visibility curves on \(\wp, V(\wp)\), is defined as the locus of points,

$$
V(\wp)=\left\{p_{i} \mid p_{i} \in \operatorname{int}(\wp), \exists p_{b} \in \partial \wp, \mathbf{M}\left(p_{i}\right)=\mathbf{M}\left(p_{b}\right)\right\} .
$$

Intuitively speaking, visibility curves are the loci of all points which lie in the interior of such a partition that have the same projection on the viewing plane as the boundary curves of that partition. It is precisely at these points that the visibility of a patch changes.

Lemma 4. The visibility curves on \(\wp, V(\wp)\) as defined above, indeed, form a set of curves.

Proof. We shall prove this part by contradiction. Let us assume that there exists an iso lated point \(p_{i} \in V(\wp)\). But by definition, there must be a point \(p_{b} \in \partial \wp\) such that \(\mathbf{M}\left(p_{i}\right)=\mathbf{M}\left(p_{b}\right)\). We know that \(\partial \wp\) is a continuous closed curve. Consider a small displacement, \(\delta \in \Re^{2}\), of \(p_{b}\) along \(\partial \wp\). Since \(\mathbf{M}\) is a smooth map, there exists an \(\epsilon \in \Re^{2}\) such that \(\mathbf{M}\left(p_{i}+\epsilon\right)=\mathbf{M}\left(p_{b}+\delta\right)\) [Mun75]. In fact, in the limit \(\delta\) going to zero, \(\epsilon \approx J^{-1}\left(p_{i}\right) J\left(p_{b}\right) \delta\), where \(J\) and \(J^{-1}\) are the Jacobian and the Jacobian inverse of \(\mathbf{M}\) respectively. Further, we know that \(J^{-1}\left(p_{i}\right)\) exists because \(p_{i} \in \operatorname{int}(\wp)\). Therefore, \(p_{i}\) cannot be an isolated point, and the visibility curves indeed form a curve.

COROLLARY 1. The set of visibility curves \(V(\wp)\) induces a partition on the region \(\wp\).

![FIG. 6.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-6-p014.png)

*FIG. 6.: A helical patch with no silhouettes.*

![FIG. 7. Visibility curves on the helical patch.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-7-p015.png)

*FIG. 7. Visibility curves on the helical patch.: visibility curves on the helical patch.*

![FIG. 8. (a) Partitioning based on visibility curves (b) Image of region K2 under M.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-8-p015.png)

*FIG. 8. (a) Partitioning based on visibility curves (b) Image of region K2 under M.: (a) Partitioning based on visibility curves (b) Image of region K2 under M.*

map, there must be a corresponding path (path) from \(p_{2}\). Let us assume that path \({ }_{1}\) reaches the boundary point \(p_{b_{1}}\) first, and that the point on path \({ }_{2}\) that has the same projection as \(p_{b_{1}}\) is \(p_{2}^{\prime}\). Since \(\mathbf{M}\left(p_{b_{1}}\right)=\mathbf{M}\left(p_{2}^{\prime}\right), p_{2}^{\prime}\) cannot be an interior point (otherwise, it is part of the visibility curve). So \(p_{2}^{\prime}\) is also a boundary point. However, since \(p_{b_{1}}\) was an arbitrarily chosen point, all its choices must lead to \(p_{2}^{\prime} \mathrm{s}\) on the boundary. But this contradicts our assumption about boundary curves being in general position. Hence any curve \(C\) must be one-to-one under \(\mathbf{M}\).

Using C and the global inverse theorem, we conclude that the interior of every region \(k \in K_{\wp}\) is one-to-one under the projection mapping \(\mathbf{M}\).

## 6 COMPUTATION OF VISIBILITY CURVES

In this section, we will describe our method to compute visibility curves. The whole algorithm is split into two parts—(i) finding all the intersections on the projected boundary curves and (ii) tracing each visibility curve.

### 6.1 Boundary Intersections

After partitioning based on silhouettes, we obtain regions whose boundaries consist of parts of the original boundary curves of the patch and the silhouette. Let us consider a single region whose boundary is made up of a set of original boundary curves, \(B\), and another set of silhouette curves, \(L\). Each element of \(B\) is represented by the corresponding Bézier curve and the interval of parameter values in which it is valid. We also maintain the projection of the boundary curves as a polygonal chain in order to obtain its intersections with silhouette curves. Each element of \(L\) and its projection under \(\mathbf{M}\) is maintained just as a polygonal chain. In order to compute all the intersection points on the projection, we must detect all self-intersections in each element of \(B\) and \(L\) and intersections between elements. Overall, there are only four basic categories in which all of them fall. We shall discuss each one in detail.

1. intersection between two boundary curves: Basically, this case reduces to finding the intersection points between two Bézier plane curves. Let \(\mathbf{f}\) and \(\mathbf{g}\) be two plane curves parametrized by \(u\) and \(v\) respectively. The two equations that give rise to the solution are

$$
\begin{aligned} \frac{X_{f}(u)}{W_{f}(u)} & =\frac{X_{g}(v)}{W_{g}(v)} \\ \frac{Y_{f}(u)}{W_{f}(u)} & =\frac{Y_{g}(v)}{W_{g}(v)}, \end{aligned}
$$

where \(X_{f}, Y_{f}, W_{f}\), and \(X_{g}, Y_{g}, W_{g}\) are the componentwise functions of \(\mathbf{f}\) and \(\mathbf{g}\) respectively. By eliminating \(u\) from these two equations using Sylvester's resultant [Sed83], we obtain a matrix polynomial in \(v\). We can reduce it to an eigenvalue problem of an associated companion matrix [MD94]. After all the eigenvalues (using LAPACK routines) are obtained only the solutions that lie within the intervals are taken. Using this method, all the intersection points are determined accurately and efficiently.

2. Self-intersections on boundary curves: Consider a plane Bézier curve \(\mathbf{f}=\langle X(s)\), v, uv, so that

$$
\begin{aligned} \frac{X(u)}{W(u)} & =\frac{X(v)}{W(v)} \\ \frac{Y(u)}{W(u)} & =\frac{Y(v)}{W(v)} . \end{aligned}
$$

Since \(u=v\) is a trivial solution to the above pair of equations, we eliminate it by dividing each of the equations by the factor \((u-v)\). Thus the equations become

$$
\begin{aligned} \frac{(X(u) W(v)-X(v) W(u))}{(u-v)} & =0 \\ \frac{(Y(u) W(v)-Y(v) W(u))}{(u-v)} & =0 . \end{aligned}
$$

equations using Sylvester's resultant, we get a \((2 n-2) \times(2 n-2)\) matrix polynomial of degree \(n-1\). We reduce this problem to one of finding eigenvalues of an associated matrix of size \(2(n-1)^{2}\). This gives all the self-intersections on the boundary curve.

- intersection between two silhouette curves: The equations governing the solution set are

$$
\begin{aligned} D(s, t) & =0 \\ D(u, v) & =0 \\ \frac{X(s, t)}{W(s, t)} & =\frac{X(u, v)}{W(u, v)} \\ \frac{Y(s, t)}{W(s, t)} & =\frac{Y(u, v)}{W(u, v)} \end{aligned}
$$

where \(D(s, t)=0\) is the equation of the silhouette curve defined in Section 4.2 and \(X, Y, Z\) and \(W\) are the componentwise functions of the patch. These four equations in four variables, typically, give rise to a zero dimensional solution set. However, it is not feasible to solve these four equations directly because of the high degree of the silhouette curve and the algebraic complexity of the resulting system. Therefore, we use piecewise linear approximation of all silhouette curves as the first iteration in our intersection computation. We treat the chain as a set of line segments. Each intersection point obtained is then refined using local minimization methods (we use Powell's method) using the energy equation \(E(u, v, s, t)\) given by

$$
\begin{aligned} E(u, v, s, t)= & D^{2}(s, t)+D^{2}(u, v)+(X(s, t) W(u, v)-X(u, v) W(s, t))^{2} \\ & +(Y(s, t) W(u, v)-Y(u, v) W(s, t))^{2} \end{aligned}
$$

Self-intersections are also found using the same method. We found that in practice this method of finding intersections works well and gives accurate results.

- intersection between boundary curve and silhouette: Consider a boundary curve f parametrized by u. Xr, Ye, Zi, and We are the scalar functions of F. Xr, for example, could represent any one of the four functions, \(X(s,0)\), \(X(s,1)\), \(X(0,t)\), and \(X(1,t)\). The set

![FIG. 9. Generation of visibility curves near the boundaries.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-9-p018.png)

*FIG. 9. Generation of visibility curves near the boundaries.: Generation of visibility curves near the boundaries.*

of intersection points of this curve with the silhouette satisfy

$$
\begin{aligned} D(s, t) & =0 \\ \frac{X(s, t)}{W(s, t)} & =\frac{X_{f}(u)}{W_{f}(u)} \\ \frac{Y(s, t)}{W(s, t)} & =\frac{Y_{f}(u)}{W_{f}(u)} \end{aligned}
$$

In this case, we use the approximated version of the boundary curves (as a piecewise linear chain) and apply a similar procedure as in the previous case. The minimization equation in this case is

$$
E(u, s, t)=D^{2}(s, t)+\left(X(s, t) W_{f}(u)-X_{f}(u) W(s, t)\right)^{2}+\left(Y(s, t) W_{f}(u)-Y_{f}(u) W(s, t)\right)^{2} .
$$

Accuracy of silhouette curve. The use of a piecewise linear approximation for the silhouette curves may seem limiting considering that points on this curve are used as starting points for tracing visibility curves. However, the points are not chosen from the linear approximation. We maintain the linear chain only to compute a starting guess to the actual point on the silhouette curve quickly. Given this approximation, we refine it using the analytic form of the silhouette curve and the boundary curve (if given in analytic form). The refinement is carried out until the point is within a user specified tolerance to the actual silhouette curve. (The generation of visibility curves near the boundaries is shown in Fig. 9.)

Once all the intersection points are computed, we are ready to trace all the visibility curves.

### 6.2 Tracing Visibility Curves

Given the starting point of each visibility curve, we are ready to trace it.

![FIG. 10. Tracing of visibility curves.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-10-p019.png)

*FIG. 10. Tracing of visibility curves.: Tracing of visibility curves.*

move to a neighboring point, h, on the visibility curve. If (gu, gu) are the domain coordinates of g, let X = \(W(gus&o)\) \(Y(gu-gu)\) *(sus and y = Wus) X, Y, and W are the componentwise functions of the original patch. We would like to find (hi, hu) in the local neighborhood of (fi, fu) such that

$$
\begin{aligned} & \frac{X\left(h_{u}, h_{v}\right)}{W\left(h_{u}, h_{v}\right)}-x=0 \\ & \frac{Y\left(h_{u}, h_{v}\right)}{W\left(h_{u}, h_{v}\right)}-y=0 . \end{aligned}
$$

Eliminating \(h_{v}\) from these two equations results in a matrix polynomial in \(h_{u}\). The singular set of this polynomial determines \(h_{u}\), and from the corresponding eigenvector, we can find \(h_{v}\). However, a lot of unnecessary work can be avoided by observing that ( \(h_{u}, h_{v}\) ) is in the neighborhood of ( \(f_{u}, f_{v}\) ). Using \(f_{u}\) as a guess to \(h_{u}\) and building a corresponding eigenvector out of \(f_{v}\), we perform inverse power iterations (described in Section 2.4) to It is possible to use Newton's method to solve the above set of equations. However, as we will see, this method has some problems. Let us assume that point b on the boundary is on a silhouette. We proved that a silhouette point is one where the Jacobian vanishes. Therefore, Newton's method does not perform well close to silhouette points. Inverse power iteration suffers from no such problem.

Tracing terminates when one of the following two cases occur.

- (hul, hu) goes out of the region, or

- (hu, hu) = (gu, gu).

The first case occurs more often. For example, if we trace further from point \(c, d\) goes out of the region. Therefore, after each step of the tracing process we have to check for containment of a point inside an arbitrary (simple, but not necessarily convex) polygon. This could be very expensive unless some processing is done on the polygon. We use Seidel's trapezoidation algorithm (created during triangulation) to create trapezoids by horizontal decomposition in \(O(N)\) time. Any point can then be determined inside or outside in \(O(\log N)\) time.

The second case occurs when the visibility curve hits the boundary curve and then continues along it. This will not be detected in the previous case and, hence, has to be checked explicitly.

![FIG. 11. (a) Partitioning of patch in Figure 1 based on visibility curves and (b) visibility curves in the domain.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-11-p020.png)

*FIG. 11. (a) Partitioning of patch in Figure 1 based on visibility curves and (b) visibility curves in the domain.: (a) Partitioning of patch in Fig. 1 based on visibility curves and (b) visibility curves in the domain.*

After computing all the visibility curves, we calculate all the partitions induced by the visibility curves in each region using the partition_polygon routine. Figures 11 and 12 show the partitioning of the patches in Fig. 1 and Fig. 6 using the visibility curves. Each partition thus obtained is one-to-one under projection. It transforms the original visibility problem into one of n polygon-like surfaces in space. The analysis given so far partitions all parts of a given surface, while only the far regions need to be partitioned. A simple check before tracing visibility can reduce the time and space complexity of the algorithm.

### 6.3 Device Independence

In this paper, we have shown that the silhouette and visibility curves, which form the trimming boundaries of the surface patches, are algebraic curves. Most of these curves do not have a rational parameterization. Therefore, we use tracing based algorithms to evaluate these curves. There has been significant work done in the symbolic and algebraic computation literature on evaluating these curves to any desired precision [AB88, Abh90, BHHL88, FS90, BR90, KM95]. In many ways, that is the best we can do to provide an explicit representation of these curves. As compared to earlier approaches, we provide the device with both the piecewise linear approximation and the analytic representation of this

![FIG. 12. Partitioning of patch in Figure 6 based on visibility curves.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-12-p020.png)

*FIG. 12. Partitioning of patch in Figure 6 based on visibility curves.: Partitioning of patch in Fig. 6 based on visibility curves.*

curve. If the resolution provided by the approximation generated by the tracing algorithm is not sufficient, the device has to evaluate intermediate points using the analytic form and simple minimization strategies [KKMN95]. Our approach is certainly not very efficient, but the complexity of the problem precludes us from using any other simpler method.

## 7 APPLICATION TO HIDDEN SURFACE REMOVAL

In the previous sections, we looked at the visibility problem for a single patch. After we partition each patch based on silhouettes and visibility curves, each region is one-to-one under the projection operation and can now be treated as a polygon. We shall, therefore, refer to each such region as a face. Recently fast randomized algorithms have been developed that can handle this problem for polygonal models [Mul89]. We present a slight variation of Mulmuley's algorithm for the sake of completeness in the Appendix. Our final goal is to output trimmed patches of the scene that are visible from the given viewpoint. We shall assume for simplicity that the faces input to this algorithm are nonintersecting. If they are intersecting, we may have to compute all the pairwise surface intersection [KM97] and split them into nonintersecting faces. It is possible that in many curved surface models (generated using constructive solid geometry or surface fitting algorithms), adjacent patches almost always share sections of boundary curves. This can cause problems when one such curve is projected into the domain of the other and curve-curve intersections are computed. However, if any extra information about the adjacency between the various patches in the model is known, we can avoid the computation of such degenerate intersections. Many of the current modelers are capable of producing the adjacency information of such models.

### 7.1 Implementation and Performance

The algorithm to compute nonoverlapping regions using silhouette and algebraic curves has been implemented. The algorithm uses existing EISPACK and LAPACK routines for some of the matrix computations. At each stage of the algorithm, we can compute bounds on the accuracy of the results obtained based on the accuracy and convergence of numerical methods adopted like eigenvalue computation, power iteration, and Gaussian elimination. Our implementation uses EISPACK [GBDM77] routines (in Fortran) to compute the eigenvalues of matrices. The algorithm was run on a SGI Onyx workstation with a R4400 CPU with 128 Mbytes of main memory.

We have not implemented the randomized algorithm for performing the general hidden surface removal. Currently, our system takes a set of parametric patches and computes its decomposition into nonoverlapping regions. Table 1 shows the performance of our algorithm on certain parametric patches. The time shown for curve computation is the total time for silhouette and visibility curve generation, and the column for running time gives the total time taken by the algorithm for curve generation and producing the nonoverlapping partitions.

![Figure 4](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-4-2-p021.png)

*Figure 4: TABLE 1 Performance of Our algorithm*

## 8 CONCLUSION

We have presented an algorithm for computing the visible portions of a scene composed of curved (parametric) surfaces from a given viewpoint. We have also given a method to compute the silhouette curve efficiently and correctly. We introduced the notion of visibility curves, which are used to partition each patch into nonoverlapping regions. The algorithm has been implemented in floating point arithmetic and performs well in practice.

## 9 APPENDIX

We now present a slight variation of the hidden surface removal algorithm of Mulmuley [Mul89]. The input to the algorithm is a set of n faces with their boundaries represented as a collection of Bézier curves and piecewise linear chains. We also have the entire face boundary as a closed simple polygon. It will be used during the tracing step. We provide an overview of the algorithm first. Let us represent the set of faces by H= (h1, h2,...,hni. Let Vi denote the collection of visible regions after i faces are added in random. The i faces already added are kept in the set Q. We want to compute V". After i steps of the algorithm, we maintain V'. At the (i + 1)st step, we pick a random face hit1 from the set HQ. For each face in V', we find all the boundary intersections with the face hitt using the method described in the previous section. Let us consider a specific intersection point (p, q) such that p lies on the boundary of one of the faces in Vi and q lies on the boundary of hi+1. If the z coordinate of p is less than that of q (p lies in front of q, then project the boundary curve on which p lies on hit, or else project the other way around. Tracing is accomplished by inverse power iteration, which was described in both Sections 2.4 and 6. The equations used to trace these curves are exactly the same as those used in Section 6. Tracing is done for all the intersection points. We partition appropriate faces by their projection curves and locate a point r inside each of the partitioned faces. Since all points inside one region are now entirely visible or not, we check only on one point. We shoot a ray from the point r to-o in the z direction and find the number of intersections with faces of V' U{hi+1). The curve surface intersection method used is described in Section 2.3. If the number of intersections is 0, this face is added; otherwise it is discarded. All the faces that were not partitioned in step (i + 1) are retained in VitI. After all the n faces are added, we obtain V". We shall now provide the pseudocode for this algorithm. For case of writing the pseudo-code, we shall assume that we have a routine project_boundary_curves that takes two faces as parameters and computes all the projected boundary curves as described above. It returns O if there are no boundary curves between the two faces; otherwise, it returns 1. We also have another routine called partition _face that computes the partition of the face using the projected boundary curve.

```text
Q=D; H= (hi, h2,..., hn); V =Ø; for (i = 1; i ≤ n; i + +){ hi = random face from set HQ; Q = QUh
V' =Ø; T =Ø; * stores faces that are partitioned in this iteration * for each face f € VI- do { j= project_boundary_curves( f, hi, &c); if (j == 0) Vi = VU{f); else i T = TU partition face (f, c); T= TU partition face(hi, C); -for each face t e T do { (Sx, Sy, Sz) = some point inside t; r = semi-infinite ray from (Sx, Sy, Sz) to (Sx, Sy, - 00); if (ray intersection_count(r) == 0) V' = V' U{t); output V";
```

![FIG. 13. Visibility computation on a set of faces.](/Users/evanthayer/Projects/stepview/docs/2000_partitioning_trimmed_spline_surfaces_visibility/figures/figure-13-p023.png)

*FIG. 13. Visibility computation on a set of faces.: visibility computation on a set of faces.*

curves drawn on the objects behind. Figure 13b shows the result of the algorithm on the set of faces. The complexity of this algorithm varies according to the order in which the faces are added. Therefore, by adding the faces randomly we reduce the expected running time of the algorithm. The output of the algorithm is a set of visible portions of patches represented as trimmed surfaces. The accuracy of the trimming curve can be adjusted according to the preferences of the user by changing the step size in the tracing method.

## Acknowledgments

We thank David Banks, David Eberly, Brice Tebbs, and Turner Whitted for all the productive discussions and helpful insights. We also thank Brice Tebbs for providing the patch in Figs. 1 and 5

## References

- [AB88] S. S. Abhyankar and C. Bajaj, Computations with algebraic curves, in Lecture Notes in Computer Science, Vol. 358, pp. 279-284, Springer-Verlag, Berlin New York, 1988.

- [Abh90] S. S. Abhyankar, Algebraic, Geometry for Scientists and Engineers, Am. Math. Soc. Providence, 1990.

- [BHHL88] C. L. Bajaj, C. M. Hoffmann, J. E. Hopcroft, and R. E. Lynch, Tracing surface intersections, Comput. Aided Geom. Design 5, 1988, 285-307.

- [BO79] J. L. Bently and T. A. Ottmann, algorithms for reporting and counting geometric intersections, IEEE Trans. Comput. C-28, 1979, 643-647.

- [BR90] C. Bajaj and A. Royappa, The ganith algebraic geometry toolkit, in Lecture Notes in Computer Science, Vol. 429, pp. 268-269, Springer-Verlag, Berlin New York, 1990.

- [Can88] J. F. Canny, The Complexity of Robot Motion Planning, ACM doctoral dissertation award, MIT Press, Cambridge, MA, 1988.

- [CCW93] L. Chen, S. Chou, and T. C. Woo, Separating and intersecting spehrical polygons: Computing machinability on three, four and five axis numerically controlled machines, ACM Trans. Graph. 12 (4), 1993, 305-326.

- [CE88] B. Chazelle and H. Edelsbrunner, An optimal algorithm for intersecting line segments in the plane, in Proc. 29th Annual TEEE Sympos. Found. Comput. Sci., 1988, pp. 590-600

- [Dix08] A. L. Dixon, The eliminant of three quantics in two independent variables, in Proceedings of London Mathematical Society, 1908, Vol. 6, pp. 49-69, 209-236.

- [Dor94] S. E Dorward, A survey of object-space hidden surface removal, Internat. J. Comput. Geom. Appl. 4, 1994, 325-362.

- [EC90] G. Elber and E. Cohen, Hidden curve removal for free form surfaces, Comput. Graph. 24(4), 1990, 95-104.

- [EC93] G. Elber and E. Cohen, Second order surface analysis using hybrid symbolic and numeric operators, ACM Trans. Graph. 12(2), 1993, 160-178.

- [EC94] G. Elber and E. Cohen, Exact Computation of Gauss Maps and visibility Sets for Freeform Surfaces, Technical report CIS 9414, Computer Science Department, Technion University, 1994.

- [Far93] G. Farin, curves and Surfaces for Computer Aided Geometric Design: A Practical Guide, Academic Press, San Diego, 1993.

- [FDHF90] J. Foley, A. Van Dam. J. Hughes, and S. Feiner, Computer Graphics: Principles and Practice, Addison-Wesley, Reading, MA, 1990.

- [FS90] R. T. Farouki and T. Sakkalis, Singular points of algebraic curves, J. Symb. Comput. 9(4), 1990, 457-483.

- [Ful78] W. Fulks, Advanced, Calculus: An Introduction to analysis, Wiley, New York, 1978.

- [GBDM77] B. S. Garbow, J. M. Boyle, J. Dongarra, and C. B. Moler, Matrix Eigensystem Routines—EISPACK Guide Extension, Vol. 51. Springer-Verlag, Berlin, 1977.

- [GL89] G. H. Golub and G. F. Van Loan, Matrix Computations, Johns Hopkins Press, Baltimore, 1989.

- [GLR82] I. Gohberg, P. Lancaster, and L. Rodman, Matrix Polynomials, Academic Press, San Diego, 1982.

- [G87] R. H. Güting and T. Ottmann, New algorithms for special cases of the hidden line elimination problem, Comput. Vision Graph. Image Process. 40, 1987, 188-204.

- [GWT94] J. G. Gan, T. C. Woo, and K. Tang, Spherical maps: Their construction, properties, and approximation, ASME Trans. J. Mech. Design 116(2), 1994.

- [HG77] G. Hamlin and C. W. Gear, Raster-scan hidden surface algorithm techniques, Comput. Graph. 11, 1977, 206-213.

- [Hor84] C. Hornung, A method for solving the visibility problem, IEEE Comput. Graph. Appl. 4(7), 1984, 26-33.

- [KKMN95] S. Kumar, S. Krishnan, D. Manocha, and A. Narkhede, High speed and high fidelity visualization of complex csg models, in BCS International Conference on Visualization and Modeling, Leeds, UK 1995, pp. 228-249.

- [KM95] S. Krishnan and D. Manocha, Numeric-symbolic algorithms for evaluating one-dimensional algebraic sets, in Proceedings of International Symporium on Symbolic and Algebraic Computation, 1995, pp. 59-67.

- [KM97] S. Krishnan and D. Manocha, An efficient surface intersection algorithm based on the lower dimensional formulation, ACM Trans. Graph. 16(1), 1997, 74-106.

- [KM98] S. Krishnan and D. Manocha, Decomposing spline surfaces into non-overlapping regions for visible surface computation, in Proc. of Indian Conference on Computer Vision, Graphics and Image Processing (Santanu Chaudhury and Shree Nayar, Eds.), pp. 207-215, 1998

- [Li81] L. Li, Hidden-line algorithm for curved surfaces, Comput. Aided Design 20(8), 1981, 466-470.

- [MD94] D Manocha and J. Demmel, algorithms for intersecting parametric and algebric curves I: Simple intersections, ACM Trans. Graph. 13(1), 1994, 73-100.

- [Mul89] K. Mulmuley, An efficient algorithm for hidden surface removal, Comput. Graph. 23(3), 1989, 379388.

- [Mul90] K. Mulmuley, An efficient algorithm for hidden surface removal, II. Report TR-90-31, University of Chicago, Chicago, Illinois, 1990.

- [Mun75] J. R. Munkers, Topology: A first Course, Prentice Hall, New York, 1975.

- [NM95] A. Narkhede and D. Manocha, Fast polygon triangulation based on seidel's algorithm, in Graphics Gems V (A. Paeth, Ed.), pp. 394-397, Academic Press, San Diego, 1995.

- [PVY92] F. P. Preparata, J. S. Vitter, and M. Yvinec. Output sensitive generation of the perspective view of isothetic parallelepipeds, Algorithmica 8, 1992, 257-283.

- [RE93] M. F. Roy and T. Van Effeleterre, Aspect graphs of algebraic surfaces, in Proceedings of International Symposium on Symbolic and Algebraic Computation, Kiev, Ukraine, 1993.

- [RS88] J. H. Reif and S. Sen, An efficient output-sensitive hidden-surface removal algorithms and its parallelization, in Proc. 4th Annu. ACM Sympos. Comput. Geom., 1998, pp. 193-200.

- [Sed83] T. W. Sederberg, Implicit and Parametric curves and Surfaces, Ph.D. thesis, Purdue University, 1983.

- [Sei91] R. Seidel, A simple and fast randomized algorithm for computing trapezoidal decompositions and for triangulating polygons, Comput. Geom. Theory Appl. 1(1), 1991, 51-64.

- [SSS74] I. Sutherland, R. Sproull, and R. Schumaker, A characterization of ten hidden-surface algorithms, Comput. Surveys 6(1), 1974, 1-55.

- [TW93] B. Tebbs and T. Whitted, Numerical design limited, personal communication, 1993.

- [Woo94] T. Woo, visibility maps and spherical algorithms, Comput. Aided Design 26(1), 1994, 6-16.
