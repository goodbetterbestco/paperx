# The Geometry of View Space of Opaque Objects Bounded by Smooth Surfaces

J.H. Rieger*

Department of Computer Science and Statistics
Queen Mary College
University of London, Mile End Road, London El 4NS, UK; and GEC Hirst Research Centre, East Lane, Wembley, Middlesex HA9 7PP, UK

## Abstract

A view of a smooth, opaque object is a line drawing consisting of contour fragments which form closed loops, terminate, or form T-junctions. Given a compact object we have a global decomposition of the space of camera positions into cells from which topologically equivalent views are obtained. To apply certain image-based object recognition techniques based on characteristic views of an object one needs to know this cellular decomposition of view space. The boundaries of such cells of stable views are formed by the view bifurcation set from which transitional (degenerate) views are seen. We derive a finite list of geometrical models of the view bifurcation set—the view bifurcation set of any particular object is a combination of such model surfaces from this list. To match a characteristic view with an image one has to find the visible fragments of the apparent contour in the image, and we briefly describe an observation which might lead to an algorithm for finding such contour fragments.

### J.H Rieger*

Department of Computer Science and Statistics, Queen Mary College, University of London, Mile End Road, London El 4NS, UK; and GEC Hirst Research Centre, East Lane, Wembley, Middlesex HA9 7PP, UK

## Abstract

A view of a smooth, opaque object is a line drawing consisting of contour fragments which form closed loops, terminate, or form T-junctions. Given a compact object we have a global decomposition of the space of camera positions into cells from which topologically equivalent views are obtained. To apply certain image-based object recognition techniques based on characteristic views of an object one needs to know this cellular decomposition of view space. The boundaries of such cells of stable views are formed by the view bifurcation set from which transitional (degenerate) views are seen. We derive a finite list of geometrical models of the view bifurcation set—the view bifurcation set of any particular object is a combination of such model surfaces from this list. To match a characteristic view with an image one has to find the visible fragments of the apparent contour in the image, and we briefly describe an observation which might lead to an algorithm for finding such contour fragments.

## 1 Introduction

A view of a semitransparent object \(O\) with smooth boundary \(M\) is a line drawing consisting of the intersection of all rays of projection tangent to \(M\) with the image plane. The view space \(V\) of an object is the space \(\mathbb{R}^{3}-O\) of all possible centres of projection. If, instead of central projection, we consider orthogonal projections of \(M\) onto planes we identify \(V\) with the sphere \(S^{2}\) representing all possible directions of projection, the "view sphere" [4]. In either case, \(V\) consists of a finite number of cells giving rise to topologically equivalent views. These cells are separated by the view bifurcation set \(B\). Views of \(M\) as seen from \(V-B\) consist of closed curves which are smooth everywhere except at isolated points corresponding to transverse intersections or cusps [21], whereas views seen from a point on \(B\) contain some degenerate singularity.

To enumerate all possible stable views ("characteristic views" [5]) of \(M\) by picking one representative view for each connected component of \(V-B\), it is necessary to first compute \(B\). The idea of representing an object by its stable views and a graph indicating possible transitions between stable views, the "view graph," is due to Jan Koenderink and Andrea van Doorn [10-12], as is the idea of using techniques from singularity theory to classify transitions between stable views. In 1976, actually before some of the necessary mathematical tools had been developed, they write: "For any given case we can construct the bifurcation set, but we cannot make general statements about its structure." [11, p. 57]. In this paper we describe a solution to this problem in the following sense: We give an exhaustive list of local geometrical models of the view bifurcation set. Any particular view bifurcation set of some generic surface is locally diffeomorphic to one of these models. We actually give a somewhat more general result allowing degenerate smooth surfaces occurring in a one-parameter family, which applies to scale-space descriptions of surfaces [13] or to families of models used in model matching [7]. In everyday vision, views of opaque objects arise more often than views of semitransparent objects (views of transparent objects aren't a problem at all!). Hence we will concentrate on opaque objects in this paper. The stable views of opaque objects consist of line fragments which are either closed or form T-junctions or terminate (these are the analogues of crossings and cusps in the semitransparent case). The view bifurcation set \(\tilde{B}\) of the boundary of an opaque object is a subset of the bifurcation set \(B\) in the semitransparent case. The division of view space into cells \(V-\tilde{B}\) is hence coarser in the opaque case.

Most of the work in computer vision related to the above ideas has concentrated on polyhedral surfaces. Chakravarty used the decomposition of \(V\) in the case of polyhedral surfaces for model matching [5], as well as additional metrical constraints provided by matches between image edges and model edges (such constraints are, of course, not available for smooth surfaces, which lack 3-D edges). Kender and Freudenstein [8] have critisized the singularity theoretic definition of a "degenerate" (i.e., transitional) view on the following grounds: (i) it applies to smooth surfaces only; (ii) only semitransparent objects can be dealt with; and (iii) due to uncertainty in measurements the transitional views become a set of positive measure in \(V\), and hence cannot be discarded. In our opinion, the point made in (i) doesn't seem fair, because it is in the case of smooth objects where the current representations used in computer vision seem hopelessly inadequate. In any case, techniques of singularity theory can be adapted to classify views of piecewise smooth surfaces as well (see [17] for the beginnings of such a unified theory). The price one has to pay is that the classifications become much more complicated. In connection with (ii) it is interesting to point out that our results on opaque objects are derived from results on semitransparent objects. And, point (iii), one can, of course, adapt the view graph to include transitional views as well (not merely the transitions), but this information is redundant. The idea of characteristic views is also related to the problem of interpreting line drawings of objects—a problem, which has attracted much interest in computer vision from the early research on the interpretation of polyhedral scenes up to the recent work of Malik on the interpretation of views of piecewise smooth surfaces [14]. A crucial part in this work is to find a catalogue of all possible junction types in a line drawing—in the language of the present paper this corresponds to a classification of all isolated singularities of codimension 0 (like, for example, cusps and transverse fold crossings). The degenerate singularities of positive codimension are not relevant in the interpretation of single line drawings (they occur with zero probability), but they do occur in families of views and they explain how the stable views fit together globally. The plan of this paper is as follows: Section 2 contains some basic definitions and summarizes the (mathematical) results in [18, 20] from which the results of this paper are derived (using fairly elementary geometrical arguments). Section 3 describes some ideas on (topological model matching, which is a possible area of application. In Section 4 we derive the main result of this paper: a list of local models of the view bifurcation set, and in Section 5 we describe an observation on finding apparent contours in images.

## 2 Preliminaries

In this section we introduce some basic concepts and results from the theory of singularities of smooth maps, which justify the claims and pictures in the remainder of this paper. Complete proofs of these claims would, of course, be out of place in a nonmathematical paper, but we outline the main line of reasoning and give references, which contain the proofs of the various steps in the argument. In Section 2.1 we give an informal description of some basic concepts, which are then defined algebraically in Sections 2.2 and 2.3. Section 2.4 contains a summary of the mathematical results in [18, 20] on which the present paper is based. One of the key ideas in applications of singularity theory to geometry is that a given problem is reduced (modulo some equivalence relation) to some normal form, which still contains the relevant geometrical information but can be studied more easily than the original situation. The geometrical problems of interest here are the following ones:

- (i) two-parameter families of orthogonal projections of rigid, smooth surfaces;

- (ii) two-parameter families of orthogonal projections of one-parameter families of deforming, smooth surfaces; and

- (iii) three-parameter families of central projections of rigid, smooth surfaces.

### 2.1 Informal geometrical description of basic concepts

![Figure 1. (a) The projection of a bean-shaped surface (after J. Callahan). At the critical points of the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-1-p004.png)

*Figure 1. (a) The projection of a bean-shaped surface (after J. Callahan). At the critical points of the: (a) The projection of a bean-shaped surface (after J. Callahan). At the critical points of the projection of M the tangent planes are mapped onto a line; when the line of sight coincides with the tangent line of the curve of critical points on M the projection has a cusp, and when the line of sight touches M at two distinct points the projection has a crossing; (b) for opaque objects the cusps are seen as endings and the crossings are seen as T-junctions.*

![Figure 2. (a) The bifurcation set on the viewing sphere for a semitransparent bean (after J. Callahan](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-2-p005.png)

*Figure 2. (a) The bifurcation set on the viewing sphere for a semitransparent bean (after J. Callahan: (a) The bifurcation set on the viewing sphere for a semitransparent bean (after J. Callahan and J. Koenderink); (b) the case of an opaque bean.*

tions of \(M\), then the view bifurcation sets \(B\) and \(\tilde{B}\) consist of, in general, singular surfaces in the three-dimensional space of centres of projection. Likewise, if we consider the evolution over time \(t\) of the bifurcation sets on the viewing sphere \(S^{2}\) of a one-parameter family of surfaces we again obtain singular surfaces \(B_{t}\) and \(\tilde{B}_{t}\) in \(\mathbb{R} \times S^{2}\). The bifurcation sets \(B\) and \(B\) of Fig. 2 are smooth at most points, and from the smooth points of the bifurcation set one obtains views of \(M\) of codimension 1. From a practical point of view, the knowledge of the possible types of codimension-1 singularities that can arise in a view seems sufficient: to obtain the subdivision of the viewing sphere \(S^{2}\) into regions corresponding to stable views of \(M\), it is enough to find the locus on \(S^{2}\) corresponding to transitional views of codimension 1. However, the more degenerate singularities (of higher codimension) and in particular the most degenerate singularities that can arise in a given situation are of great theoretical importance, because they tell us how the pieces of the bifurcation set fit together. In a \(d\)-parameter family of views the singularities of codimension \(d\) are called the "organising centres," because they determine the semiglobal structure in some neighborhood of a point in \(\mathbb{R}^{d}\). In the two-parameter family of orthogonal views of \(M\) (shown in Fig. 2) the codimension-2 singularities are seen from the vertices of the bifurcation set where the smooth strata of codimension-1 singularities meet. There is a finite list of such vertex types on the viewing sphere of any generic surface, both in the opaque and in the semitransparent case, and any particular bifurcation set is composed of such local "building blocks." Basically the same is true for the bifurcation set in the three-dimensional space of centres of projection of a generic surface, all the smooth strata of the bifurcation set meet at the vertices of some singular surface, and there is a finite list of possible vertex types. Here is an example: Fig. 3(a) shows a "swallowtail surface" in the space of centres of projection. Projecting the surface, whose views are shown in Fig. 3(b), from the vertex of the swallowtail surface gives rise to a view that contains a codimension-3 singularity. From centres of projection located on the cuspidal edges (of Fig. 3(a)) one obtains views containing codimension-2 singularities, and from centres of projection on the selfintersection curve one obtains views with two simultaneous codimension-1 singularities at different locations on the retina. From the remaining smooth parts of the swallowtail surface one sees views containing codimension-1 singularities, and from points in the complement of the swallowtail one obtains the stable views shown in Fig. 3(b).

### 2.2 The visual mapping, apparent contours, Whitney's normal forms for the cusp and the fold

In this section we give algebraic definitions of some of the terms introduced in Section 2.1; in particular, we explain a little bit what we mean by "equivalence

![Figure 3. (a) A vertex of a swallowtail-shaped bifurcation set in the space of centres of projection;](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-3-p007.png)

*Figure 3. (a) A vertex of a swallowtail-shaped bifurcation set in the space of centres of projection;: (a) A vertex of a swallowtail-shaped bifurcation set in the space of centres of projection; (b) the stable views in the complement of the bifurcation set.*

class of views" (full details are given in the technical papers [18,20]). We assume that \(M\) is a smooth surface given by a map \(\varphi: M \rightarrow \mathbb{R}^{3}\) which has maximal rank everywhere (that is \(\varphi\) is an immersion), and we choose local coordinates \(x, y\) on \(M\) and \(X, Y, Z\) in \(\mathbb{R}^{3}\). Locally (at the origin, say) we can replace \(M\) by \(\mathbb{R}^{2}\), and since the rank of \(\mathrm{d} \varphi\) (throughout this paper d denotes the differential) is 2 we can write (in Monge form)

$$
\begin{aligned} & \varphi: \mathbb{R}^{2}, \mathbf{0} \rightarrow \mathbb{R}^{3}, \mathbf{0} \\ & \varphi(x, y)=(x, y, Z(x, y))=(X, Y, Z) . \end{aligned}
$$

Projecting \(M\) orthogonally onto a plane perpendicular to the \(Y\)-direction gives a composed map (the "visual mapping")

$$
\begin{aligned} & f=\pi_{Y} \circ \varphi: \mathbb{R}^{2}, \mathbf{0} \rightarrow \mathbb{R}^{3}, \mathbf{0} \rightarrow \mathbb{R}^{2}, \mathbf{0} \\ & f(x, y)=(x, Z(x, y)) \end{aligned}
$$

The critical set of f

$$
\begin{aligned} \Sigma f & =\{(x, y): \operatorname{rank}[\mathrm{d} f(x, y)]=1\} \\ & =\{(x, y): \partial Z(x, y) / \partial y=0\}, \end{aligned}
$$

is, in the computer vision literature, sometimes called the "contour generator." The set of critical values \(f(\Sigma f)\) is the apparent contour of \(M\), which corresponds to the intersection of the visual rays tangent to \(M\) with the image plane.

Example 2.1. Consider the surface given by \(\varphi(x, y)=\left(x, y, \frac{1}{3} y^{3}+x^{2} y-y\right)\) and its projection along the \(Y\)-direction (see Fig. 4)

$$
f(x, y)=\left(x, \frac{1}{3} y^{3}+x^{2} y-y\right) .
$$

The critical set \(\Sigma f\) is given by \(x^{2}+y^{2}-1=0\), which has the parametrization \(t \mapsto(\sin t, \cos t)\). The contour generator on \(M\) viewed as a space curve is given by

$$
\varphi(\sin t, \cos t)=\left(\sin t, \cos t,-\frac{2}{3} \cos ^{3} t\right) .
$$

The line of sight, the \(Y\)-direction, is tangent to this space curve at \(t=\frac{1}{2} \pi, \frac{3}{2} \pi\), It is a classical result of Whitney [21] that a stable map \(f\) from the plane to the plane has only folds and cusps as local singularities. As a consequence we can transform any stable singularity of \(f(x, y)=(X, Z)\) into one of the normal forms \(\left(x, y^{2}\right)\), the fold, or \(\left(x, x y+y^{3}\right)\), the cusp, by local diffeomorphisms of the \((x, y)\) - and \((X, Z)\)-space (both the normal forms and these diffeomorphisms being defined in a neighborhood of \((x, y)=(X, Z)=(0,0))\). To illustrate how this works, let's transform the cusp of \(f(x, y)=\left(x, \frac{1}{3} y^{3}+\right.\)

![Figure 4. A view along the Y-direction of the surface defined in Example 2.1. The contour generator](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-4-p009.png)

*Figure 4. A view along the Y-direction of the surface defined in Example 2.1. The contour generator: A view along the Y-direction of the surface defined in Example 2.1. The contour generator central projection looks nicer!).*

\(\left.x^{2} y-y\right)\) at \((x, y)=(1,0)\) of our example into the above normal form. first, note that the cusp is three-determined, which means that terms of degree four and higher, denoted below by \(\mathrm{O}(4)\), in the Taylor expansion of \(f\) are irrelevant and can be discarded. Translate the origin to \((x, y)=(1,0)\), so we consider

$$
f(x, y)=\left(x, \frac{1}{3} y^{3}+x^{2} y+2 x y\right) \quad \text { at }(x, y)=(0,0)
$$

(here we use the same symbols for our new coordinates). Now apply the following diffeomorphisms to f in the order given

y \mapsto y-\frac{1}{2} x y, \quad Z \mapsto 3 Z, \quad x \mapsto \frac{1}{6} x, \quad X \mapsto 6 X,

giving the following sequence of "right-left" equivalent maps (right-left equivalent because we compose \(f\) with diffeomorphisms on the right and left, i.e., \(h \circ f \circ k(x, y))\) :

$$
\begin{aligned} \left(x, \frac{1}{3} y^{3}+x^{2} y+2 x y\right) & \sim\left(x, \frac{1}{3} y^{3}+2 x y+\mathrm{O}(4)\right) \\ & \sim\left(x, y^{3}+6 x y\right) \\ & \sim\left(\frac{1}{6} x, y^{3}+x y\right) \\ & \sim\left(x, y^{3}+x y\right) \end{aligned}
$$

There are, of course, more efficient ways of checking the equivalence of a pair of maps. Right-left equivalence defines a (pseudo)group ( \(\mathscr{A}_{\mathrm{c}}\), in John Mather's notation) acting on the space of maps (locally at a point), and a pair of maps being equivalent means that they are contained in the same orbit under this group action. A map is stable if it is contained in an orbit which is open and dense in the space of maps. In principle, one could choose any representative of an orbit as its normal form, but for computational reasons one picks "the" simplest possible polynomial map (whatever simplest means!). This technical approach has been used by the author to derive the relevant classifications of singularities on which this paper is based [18]. Here we merely study the necessary modifications to adapt these results to opaque objects based on simple geometric arguments (this implies that the readers have to take these classifications "on trust," proofs and precise statements of the results can be found in the above exact sources [18,20]).

### 2.3 Families of projections and bifurcation sets

first, consider families of orthogonal projections of \(M\) onto planes. We think of the set of all unit vectors \(\mathbf{1}\) in \(\mathbb{R}^{3}\) as points on the view sphere \(S^{2}\), and project \(M\) onto planes perpendicular to \(\mathbf{1}\). This gives rise to a two-parameter family of projections,

$$
\begin{aligned} & F: S^{2} \times M \rightarrow T S^{2} \\ & F(\mathbf{1}, x, y)=(\mathbf{1}, \varphi(x, y)-(\mathbf{1} \cdot \varphi(x, y)) \mathbf{1})=(\mathbf{1}, f(\mathbf{1}, x, y)) \end{aligned}
$$

where \(T S^{2}\) denotes the union of all tangent planes to \(S^{2}\), and the dot denotes the usual scalar product in \(\mathbb{R}^{3}\). We can write this two-parameter family locally as \(F: \mathbb{R}^{2} \times \mathbb{R}^{2}, \mathbf{0} \rightarrow \mathbb{R}^{2} \times \mathbb{R}^{2}, \mathbf{0}\). If, instead of a single surface, we consider a one-parameter family of surfaces, parametrized by \(\varphi_{t}\), evolving over time \(t\), we have the following three-parameter family of projections,

$$
\begin{aligned} & F: \mathbb{R} \times S^{2} \times M \rightarrow \mathbb{R} \times T S^{2} \\ & F(t, \mathbf{1}, x, y)=\left(t, \mathbf{1}, \varphi_{t}(x, y)-\left(\mathbf{1} \cdot \varphi_{t}(x, y)\right) \mathbf{1}\right)=(t, \mathbf{1}, f(t, \mathbf{1}, x, y)), \end{aligned}
$$

which is locally given by \(F: \mathbb{R}^{3} \times \mathbb{R}^{2}, \mathbf{0} \rightarrow \mathbb{R}^{3} \times \mathbb{R}^{2}, \mathbf{0}\). Finally, consider central projections. Here the parameter space is, instead of \(S^{2}\), the space \(V\) of possible centres of projection \(\boldsymbol{c}\) (recall that \(V\) is \(\mathbb{R}^{3}\) minus the object). So we have a three-parameter family of projections onto spheres,

$$
\begin{aligned} & F: V \times M \rightarrow V \times S^{2} \\ & F(c, x, y)=\left(c, \frac{\varphi(x, y)-c}{|\varphi(x, y)-c|}\right)=(c, f(c, x, y)) \end{aligned}
$$

$$
F(a, x, y)=(a, f(a, x, y))=\left(a, x, \frac{1}{3} y^{3}+x^{2} y+a y\right)
$$

$$
B=\left\{a \in \mathbb{R}^{d}: f(a, x, y) \text { has a degenerate singularity near the origin }\right\} .
$$

![Figure s. The birth of a circular conto trilot (op rey and the corest ding lipshaped](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-s-p011.png)

*Figure s. The birth of a circular conto trilot (op rey and the corest ding lipshaped: Fig. s. The birth of a circular conto trilot (op rey and the corest ding lipshaped The birth of a circular contour generator (top row) and the corresponding lip-shaped apparent contour (bottom row). The degeneracy of this family is at a = 0.*

2.4. Classification of families of maps from R' to R' and their bifurcation sets: Summary of results in (18, 20] In [18] we have classified maps from the plane to the plane of right-left codimension less than or equal to four (in fact, all simple maps of corank one are classified in this paper-this, however, is merely of mathematical interest). Here the stable maps (the ones of codimension 0) correspond to the singularities of Whitney, and the other (degenerate) singularities correspond to transitional views of a smooth surface. The results of this classification are then used in a second paper [20] to produce a list of three-parameter families of maps from R' to R', and to calculate the bifurcation sets in the parameter spaces of these families. Normally, one would obtain such lists of d-parameter families by simply taking the versal unfoldings of minimal dimension of all the degenerate maps of (right-left) codimension d. (Intuitively a versal unfolding of a singularity is a family of maps which displays all the different possible geometrical phenomena near (in the space of maps) this singularity—consult [17, 20] for a precise algebraic definition, some explanations are also contained in Appendix A). Unfortunately right-left equivalence of maps is sometimes too restrictive in that a pair of inequivalent maps can have the same geometry. For maps from R' to ' this begins to happen from codimension 3 onwards: for example, the versal family of minimal dimension (a, x, xy + y' + a,y' + asy + açy) is topologically trivial along the a,-direction. There is a (quite technical) way around this problem, which allows one to remove parameters corresponding to topologically trivial deformations. In [20] we follow this route to obtain the following list of d-parameter families of maps from R' to R' (where d = 3), \(F(a,x,y)\) = (a, f(a, x, y)):

(A remark for the experts: the unfoldings (i), (ii) \({ }_{k}\) for \(k=4\), and (iii) are We denote the singularities \(f(\mathbf{0}, x, y)\) at the origin \(\boldsymbol{a}=\mathbf{0}\) of the \(d\)-parameter

![Figure 6. Top row](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-6-p013.png)

*Figure 6. Top row: one, two, and three-point contact between a pair of lines. Bottom row: A point of k-point contact splits into k points of transverse intersection.*

![Figure 7. A fold F in two-point contact with the limiting tangent T of a cusp C.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-7-p013.png)

*Figure 7. A fold F in two-point contact with the limiting tangent T of a cusp C.: A fold F in two-point contact with the limiting tangent T of a cusp C.*

![Figure 8. The (local) projections of codimentions 3 (on the right) and their contour generators](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-8-p014.png)

*Figure 8. The (local) projections of codimentions 3 (on the right) and their contour generators: The (local) projections of codimentions 3 (on the right) and their contour generators (critical sets) seen from the above, i.e., along the normal (on the left): (x, y) denote coordinates on icine oriente are the he cd thie onion enter the surface and (X, Z) denote coordinates in the image plane; lower case letters in the formulas of the right column denote real parameters defining curves.*

codimension-3 singularity is also a (zero-dimensional) stratum.) It is enough to study these bifurcation sets near a codimension-3 singularity, because the less degenerate singularities meet at such points in parameter space. Above we give formulas and pictures of the contour generators (critical sets) and the apparent contours of the (local) codimension-3 singularities (see Fig. 8). Note that these critical sets (and the contour generators for that matter) have singularities, whereas, generically, the contour generators are smooth curves on \(M\) without selfintersections. Of course, these singularities will disintegrate by changing the viewing position slightly or by slightly deforming the surface, and the bifurcation sets in Section 4 will describe all the nearby stable configurations.

### 2.5 Families of projections and versality

To understand the relation between the normal forms of families of maps from \(\mathbb{R}^{2}\) to \(\mathbb{R}^{2}\) of Section 2.4 and the families of projections (1)-(3) of Section 2.3, we consider here two questions. Is it true that for almost all surfaces (in the sense of Lebesgue measure) the families of projections (1) and (3) are always locally equivalent to one of the normal forms of Section 2.4? And for any given normal form: Is there always a surface which has a family of projections equivalent to that normal form? The answer to the first question is affirmative. Roughly speaking, for an open and dense set of smooth surfaces (immersions) any two-parameter family of orthogonal projections is locally versal (that is, equivalent to one of the \(d\)-parameter families of Section 2.4, where \(d \leqslant 2\) ). In the case of threeparameter families of central projections a similar result is true: but we have to replace versal by topologically versal, and \(d \leqslant 2\) by \(d \leqslant 3\) (this result is due to Mond, see [16]). Now consider the second question. Let \(\varphi(x, y)=(x, y, Z(x, y))=(X, Y, Z)\) be a (possibly local) parametrization of a smooth surface. first, we need a parametrization for the three-parameter family (1) of orthogonal projections of \(\varphi\). Rather than changing the projection direction 1 on the viewing sphere, we keep the direction of projection \(\boldsymbol{e}_{2}=(0,1,0)\), say, fixed (i.e., we always project onto the ( \(X, Z\) )-plane) and instead apply a two-parameter family of

$$
R=\left(\begin{array}{ccc} a_{1}^{2}-a_{2}^{2}+a_{3}^{2} & -2 a_{2} a_{3} & 2 a_{1} a_{2} \\ 2 a_{2} a_{3} & -a_{1}^{2}-a_{2}^{2}+a_{3}^{2} & -2 a_{1} a_{3} \\ 2 a_{1} a_{2} & 2 a_{1} a_{3} & -a_{1}^{2}+a_{2}^{2}+a_{3}^{2} \end{array}\right),
$$

where \(a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=1\). The parameters in this two-parameter family of rotations (the parameter space is the unit two-sphere in the \(\left(a_{1}, a_{2}, a_{3}\right)\)-space, which, roughly speaking, corresponds to the viewing sphere-although most points on the viewing sphere are here represented twice) are the usual Euler parameters:

$$
a_{1}=\cos \alpha \sin \frac{1}{2} \omega, \quad a_{2}=\cos \gamma \sin \frac{1}{2} \omega, \quad a_{3}=\cos \frac{1}{2} \omega,
$$

where \(\alpha\) and \(\gamma\) are the angles between the axis of rotation and the \(X\) - and \(Z\)-axes, respectively, and where \(\omega\) is the magnitude of rotation (the irrelevant rotation about the \(Y\)-axis, the line of sight, is assumed to be zero). Letting \(\pi_{Y}\) denote the orthogonal projection \((\bar{X}, \bar{Y}, \bar{Z}) \mapsto(\bar{X}, \bar{Z})\), we obtain a twoparameter family of projections \((\bar{X}, \bar{Z})^{\mathrm{T}}=\pi_{Y} \circ\left(R \cdot \varphi^{\mathrm{T}}\right)\) of the surface \(\varphi\) given

$$
\binom{\bar{X}}{\bar{Z}}=\binom{\left(a_{1}^{2}-a_{2}^{2}+a_{3}^{2}\right) x-2 a_{2} a_{3} y+2 a_{1} a_{2} Z(x, y)}{2 a_{1} a_{2} x+2 a_{1} a_{3} y-\left(a_{1}^{2}-a_{2}^{2}-a_{3}^{2}\right) Z(x, y)}
$$

where \(a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=1\) (here \(v^{\mathrm{T}}\) denotes the transpose of \(v\) ). This parametrization of the family of orthogonal projections of the surface \(\varphi\) is in fact global, it represents the totality of views of \(\varphi\) on the view sphere, not just the views in a neighborhood of the view sphere. However, our concern here is merely local. One can now easily find surfaces \(\varphi(x, y)=(x, y, Z(x, y))\) such that the family (4) near \(a_{1}=a_{2}=x=y=0\) and

$$
Z(x, y)= \begin{cases}y^{3} \pm x^{2} y & \text { for }(\mathrm{i})_{2} \\ x^{2}+y^{3}+x^{3} y & \text { for }(\mathrm{i})_{3} \\ x y+y^{4} & \text { for }(\mathrm{ii})_{4} \\ x y+y^{5} \pm x y^{3} & \text { for }(\mathrm{ii})_{5} \\ x y^{2}+y^{4}+y^{5} & \text { for }(\mathrm{iii})_{2}\end{cases}
$$

The most degenerate member of the family (4) is the projection where \(a_{1}=a_{2}=0\) and \(a_{3}=1\). In some of the above cases this projection differs from the normal forms at \(a_{1}=\cdots=a_{d}=0\) of Section 2.4 (although the corresponding projections are equivalent), these differences are required to make the family (4) versal (see Appendix A). To obtain the three-parameter families \((\mathrm{i})_{4}\), (ii) \({ }_{6}\), (iii) \({ }_{3}\), (iv), and (v) of Section 2.4 we can use the parametrization (4) of orthogonal views together with the following one-parameter families of surfaces,

$$
\varphi(t, x, y)=(t, x, y, Z(t, x, y))
$$

$$
Z(t, x, y)= \begin{cases}x^{2}+y^{3} \pm x^{4} y+t x^{2} y & \text { for }(\mathrm{i})_{4} \\ x y+x y^{2}+y^{6}+t y^{4} & \text { for }(\mathrm{ii})_{6} \\ x y^{2}+y^{4}+x^{3} y+t x^{2} y & \text { for }(\mathrm{iii})_{3} \\ x y^{2}+y^{5}+t y^{4} & \text { for }(\mathrm{iv}) \\ x^{2} y+y^{4}+t y^{2} & \text { for }(\mathrm{v})\end{cases}
$$

## 3 Matching Views of Opaque Objects with Models

![Figure 9. A view of a smooth, opaque object; numbers denote contour fragments and T-junctions are](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-9-p017.png)

*Figure 9. A view of a smooth, opaque object; numbers denote contour fragments and T-junctions are: A view of a smooth, opaque object; numbers denote contour fragments and T-junctions are labelled by a T.*

contour segments: (a) closed loops (like segment 8); (b) isolated segments terminating at cusps (like segment 7); (c) segments with one cusp and one T-junction (like segment 4); and (d) segments joining T-junctions (like segment 1). If we denote the number of cusps of a segment by \(C\), and indicate that a segment joins a T-junction transversely by an s (like "stem"), we can describe Fig. 9 as follows:

segment 1: (C = 0, \(T(1)\)s, \(T(3)\)s), segment 2: (C = 1, \(T(1)\)), segment 3: (C = 0, \(T(1)\), \(T(2)\)s), segment 4: (C = 1, \(T(2)\)), segment 5: (C = 0, \(T(2)\), \(T(3)\)), segment 6: (C = 1, \(T(3)\)), segment 7: (C= 2), segment 8: (C = 0).

This description has some obvious deficiencies. It doesn't reflect inclusion relationships: an entirely different view, where segment 7 is contained in segment 8 (for example), would have the same description. Hence it is useful to keep track of global relationships between loops of contour segments: for example, pairs of such loops might be contained in each other, be disjoint, or might intersect in a pair of T-junctions. Another problem with this description is that it cannot pick up the difference between the views shown in Fig. 10. Clearly, the difference between views (a) and (b) can only be described by taking into account the orientation of the contour loops. With the convention that for a segment, which is (part of) a closed loop, we count its T-junctions in clockwise order, say, the views (a) and (b) have different descriptions:

![Figure 10. Views showing different orientations of a contour loop.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-10-p018.png)

*Figure 10. Views showing different orientations of a contour loop.: Views showing different orientations of a contour loop.*

segment 1: (C = 0, \(T(1)\)s, \(T(1)\)), segment 2: (C = 1, \(T(1)\)) \(T(1)\) \(T(1)\) (a) (b)

$$
\begin{aligned} & \text { segment 1: }(C=0, T(1), T(1) \mathrm{s}), \\ & \text { segment 2: }(C=1, T(1)) . \end{aligned}
$$

Another refinement of this description could be introduced by keeping track of inflexion points on the contour segments. As Koenderink and van Doorn have pointed out, inflexion points on the contour correspond to parabolic points on the surface [9, 11]. With this refinement we could, for example, infer that segment 7 of Fig. 9 corresponds to a dent and not to a bump. However, our classification of view singularities up to right-left equivalence does not preserve inflexion properties of the contour. A refined classification (up to codimension 2) preserving inflexions has been obtained by considering affine duals of the apparent contour (see [3, 15]). This refinement would further partition the cells in view space with an invariant number of cusps and T-junctions into smaller cells in which in addition the number of inflexion points are constant. After a characteristic view with the right number of cusps and T-junctions has been matched with an image one could improve this match by counting the inflexions (a "coarse-to-fine" strategy, currently loved by everyone in vision...).

## 4 View Bifurcation Sets of Opaque, Smooth Objects

There are certain universal local models for the bifurcation sets that generically occur in the parameter spaces of the families of views (1)-(3) of Section 2.3 (namely on the viewing sphere \(S^{2}\), in the product space \(\mathbb{R} \times S^{2}\), and in the space of centres of projection). Due to the algebraic complexity of the problem, a direct study of the bifurcation geometry of these parameter spaces is difficult. The fact, however, that the families of views (1)-(3) are, in general, versal (see Section 2.5) allows us to replace these families by the normal forms of Section 2.4, which can be studied more easily. In [20] we have derived a catalogue of local models for the bifurcation set from such normal forms, and in the present section we adjust this classification to the situation where the viewed surfaces are the boundaries of opaque objects.

It must be stressed that the pictures of bifurcation sets and of views, below,

The pictures in this section show bifurcation sets in \(\mathbb{R}^{3}\) near vertices corresponding to views of codimension 3. The information about less degenerate points on the bifurcation set is completely contained in these pictures, because all the strata of lower codimension meet at such degenerate vertices of the bifurcation set (hence, it is not necessary to show pictures of the bifurcation set near views of codimension 1 and 2). Some of the bifurcation sets can arise both in families of central projections and in families of orthogonal projections of one-parameter families of surfaces, whereas others can only arise in the latter situation (see Section 2.5).

should not be taken too literally: the bifurcation sets in the space of centres of projection, for example, are in reality ruled surfaces; our hand-drawn bifurcation sets, on the other hand, may become ruled surfaces after some bending and twisting (i.e., after applying some diffeomorphism). Likewise, two stable views of the same surface that are related by a rigid rotation of the surface may, in our drawings, not look like pictures of the same surface at all: again, our drawings are only correct up to diffeomorphisms. (Compare Fig. 3(b), where an attempt has been made to indicate how the orientation of the surface changes between different views, and Fig. 13, which, to the differential topologist, is equivalent.) There are three reasons for drawing the bifurcation sets and views in this section in such a way (apart from the artistic incompetence of the author!):

- In one of the applications that we have in mind the surfaces are deforming.

- The quantitative incorrectness of these drawings reflects the loss of information caused by the reduction (modulo diffeomorphisms) of a geometrical problem to a normal form.

- In a distorted picture the singularities can be shown more clearly (in a correct picture a pair of endings, say, might be too close, or a T-junction might look almost non-transverse, etc.).

### 4.1 Local singularities

We define an object locally as O= {(x, y, ≥\(Z(x,y)\))) or {(x, y, =\(Z(x,y)\))), i.e., as the set of points (near the origin) in R' whose heights are not smaller (or not greater) than specified by the function Z. The projections of such objects along the Y-direction fall into one of two categories according to whether the degree of the lowest order term of \(Z(0,y)\) is even or odd, or, in geometrical terms, whether the line of sight has even-point contact or odd-point contact with the surface at (0, 0, 0). (Here we assume that \(Z(0,0)=0\), and we recall the definition of k-point contact in Section 2.4.) When the degree is even the object remains entirely above (or below) the line of sight, whereas when the degree is odd the object is above and below. Let's assume that the degree of the lowest-order term of \(Z(0,y)\) is greater than one so that the line of sight is tangent to the bounding surface of the object at (x, Y, Z) = (0, 0, 0)-otherwise not much is happening visually anyway! define a "front view" ("back view") of (X, Y, Z) = (0, 0, 0) as a view along the Y-direction for increasing (decreasing) Y from a centre of projection c1,2 = (0, 71, 0), say, or c1.2 = (0, 70, 0) for orthogonal projection. Then there are for any given bounding surface two (possibly distinct) types of projection depending on whether the object is above or below its bounding surface and depending on whether it is viewed from the front or the back (and not four types as one might expect, see Fig. 11.

![Figure 11. For any given surface there are two distinct views if that surface is the boundary of an](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-11-p021.png)

*Figure 11. For any given surface there are two distinct views if that surface is the boundary of an: For any given surface there are two distinct views if that surface is the boundary of an situation for even k. Bottom row: situation for odd k.*

Note the difference between the case when the bounding surface remains on one side of the line of sight, where a part of the background is visible, and the case when the bounding surface has inflexional contact (possibly of higher order) with the line of sight. Now consider the surfaces \(M\) corresponding to the codimension-3 projections of Section 2.4, namely \(I_{4}^{ \pm}, I I_{6}, I I I_{3}, I V\), and \(V\). From [20] we know the bifurcation sets in the view space of these projections, and we know the apparent contours of \(M\) seen from points within the cells \(\mathbb{R}^{3}-B\). We noted above that for each apparent contour of \(M\) there are two (possibly distinct) views if \(M\) is the bounding contour of an opaque object. These views are, of course, subsets of the apparent contour with the hidden lines removed. Likewise, the view bifurcation sets \(\tilde{B}\) of opaque objects are obtained from the full bifurcation sets \(B\) by removing two-dimensional boundaries between cells of \(\mathbb{R}^{3}-B\) which correspond to apparent contours that differ by some hidden detail. first, consider the projections 14. Here \(Z(0,y)\) = y has odd degree and hence according to Fig. 11 we have to consider the cases:

$$
\begin{aligned} & O_{1}^{ \pm}=\left\{\left(x, y, \leqslant\left(y^{3} \pm x^{4} y\right)\right)\right\}, c_{1}, \\ & O_{2}^{ \pm}=\left\{\left(x, y, \geqslant\left(y^{3} \pm x^{4} y\right)\right)\right\}, c_{2} . \end{aligned}
$$

However, applying the diffeomorphisms \(y \mapsto-y\) and \(Z \mapsto-Z\), which preserve the visible bifurcations, to the family of projections \(\left(\boldsymbol{a}, x, y^{3} \pm x^{4} y+\right.\) \(\sum_{i=1}^{3} a_{i} x^{k-i-1} y\) ) shows that the front and back views are equivalent. Hence, we choose the pairs ( \(O_{1}^{ \pm}, c_{1}\) ), say, as our "normal forms." Figure 12 shows the bifurcation set (which is the same for \(I_{4}^{+}\)and \(I_{4}^{-}\))-due to the absence of any multi-local singularities, \(\tilde{B}\) is identical to the full bifurcation set \(B\) (this is unusual: the subsequent bifurcation sets will be different from their full

![Figure 12. View bifurcation set near a 1; singularity. The a,-direction points into the plane of the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-12-p022.png)

*Figure 12. View bifurcation set near a 1; singularity. The a,-direction points into the plane of the: View bifurcation set near a 1; singularity. The a,-direction points into the plane of the the paper, the a,-direction points left, and the a-direction points up. Three cells of stable views meet at the origin (which, here and in the subsequent figures, corresponds to the codimension-3 singularity).*

$$
O=\left\{\left(x, y, \geqslant\left(x y+y^{6}\right)\right)\right\}, c_{1,2}
$$

$$
O=\left\{\left(x, y, \geqslant\left(x y^{2}+y^{4}+y^{7}\right)\right)\right\}, c_{1,2} .
$$

![Figure 16 (Figure 18) shows the bifurcation sets B1.2, and Figure 17 (Figure 19) shows](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-16-p022.png)

*Figure 16 (Figure 18) shows the bifurcation sets B1.2, and Figure 17 (Figure 19) shows: Figure 16 (Fig. 18) shows the bifurcation sets B1.2, and Fig. 17 (Fig. 19) shows*

![Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-13-5-p027.png)

*Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.: Sections at a, >0 are identical due to the symmetry about a, = 0.*

![Figure 15. A section through the bifurcation set of Figure 14 at a, < 0. The notation is the same as in](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-15-p024.png)

*Figure 15. A section through the bifurcation set of Figure 14 at a, < 0. The notation is the same as in: A section through the bifurcation set of Fig. 14 at a, < 0. The notation is the same as in Fig. 13*

![Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-13-5-p027.png)

*Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.: Sections at a, >0 are identical due to the symmetry about a, = 0.*

![Figure 16 (Figure 18) shows the bifurcation sets B1.2, and Figure 17 (Figure 19) shows](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-16-p022.png)

*Figure 16 (Figure 18) shows the bifurcation sets B1.2, and Figure 17 (Figure 19) shows: Figure 16 (Fig. 18) shows the bifurcation sets B1.2, and Fig. 17 (Fig. 19) shows*

![Figure 17. A section through the bifurcation set of Figure 16 at a, > 0. The notation is the same as in](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-17-p025.png)

*Figure 17. A section through the bifurcation set of Figure 16 at a, > 0. The notation is the same as in: A section through the bifurcation set of Fig. 16 at a, > 0. The notation is the same as in Fig. 13.*

![Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-13-5-p027.png)

*Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.: Sections at a, >0 are identical due to the symmetry about a, = 0.*

![Figure 18. Second type of view bifurcation set near a Ill, singularity. The coordinate frame is the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-18-p025.png)

*Figure 18. Second type of view bifurcation set near a Ill, singularity. The coordinate frame is the: Second type of view bifurcation set near a Ill, singularity. The coordinate frame is the III, singularity. The coordinate frame is the same as in Fig. 16. Here six cells of stable views meet at the origin.*

![Figure 19. A section through the bifurcation set of Figure 18 at a, >0. The notation is the same as in](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-19-p026.png)

*Figure 19. A section through the bifurcation set of Figure 18 at a, >0. The notation is the same as in: A section through the bifurcation set of Fig. 18 at a, >0. The notation is the same as in Fig. 13.*

![Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-13-5-p027.png)

*Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.: Sections at a, >0 are identical due to the symmetry about a, = 0.*

$$
The degree of \(Z(0, y)=y^{5}\) of \(I V\) is odd, leading to two distinct cases:
$$

$$
O_{1}=\left\{\left(x, y, \leqslant\left(x y^{2}+y^{5}\right)\right)\right\}, c_{1}
$$

$$
O_{2}=\left\{\left(x, y, \geqslant\left(x y^{2}+y^{5}\right)\right)\right\}, \boldsymbol{c}_{2} .
$$

Here the full bifurcation set \(B\) separates \(\mathbb{R}^{3}\) into twenty-three cells, see [20]. In the case ( \(O_{1}, \boldsymbol{c}_{1}\) ) the bifurcation set \(\tilde{B}_{1}\) separates \(\mathbb{R}^{3}\) into nine components, and is symmetric about \(a_{1}=0\) (see Fig. 20). Figure 21 shows a section through \(\tilde{B}_{1}\) at \(a_{1} \neq 0\) indicating strata of transitional views and nearby stable views. In the second case ( \(O_{2}, \boldsymbol{c}_{2}\) ) the bifurcation set is again symmetric about \(a_{1}=0\), and \(\mathbb{R}^{3}-\tilde{B}_{2}\) has five connected components (see Fig. 22). A section through \(\tilde{B}_{2}\) at \(a_{1} \neq 0\) indicating strata of transitional views and the nearby stable views are shown in Fig. 23. Finally, \(Z(0, y)=y^{4}\) of \(V\) has even degree, and again there are two distinct cases:

$$
O=\left\{\left(x, y, \geqslant\left(x^{2} y+y^{4}\right)\right)\right\}, c_{1,2} .
$$

Once again \(B\) and \(\tilde{B}_{1,2}\) are symmetric about \(a_{1}=0, \mathbb{R}^{3}-\tilde{B}_{1}\) has five connected components (see Fig. 24) and \(\mathbb{R}^{3}-\tilde{B}_{2}\) has seven connected components (see

![Figure 20. First type of view bifurcation set near a /V singularity. The coordinate frame is the same](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-20-p027.png)

*Figure 20. First type of view bifurcation set near a /V singularity. The coordinate frame is the same: first type of view bifurcation set near a /V singularity. The coordinate frame is the same as in Fig. 12. Here nine cells of stable views meet at the origin. Note the symmetry of the bifurcation set about a, = 0.*

![Figure 21. A section through the bifurcation set of Figure 20 at a, <O. The notation is the same as in](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-21-p027.png)

*Figure 21. A section through the bifurcation set of Figure 20 at a, <O. The notation is the same as in: A section through the bifurcation set of Fig. 20 at a, <O. The notation is the same as in <0. The notation is the same as in Fig. 13. Sections at a, > 0 are identical due to the symmetry about a, = 0.*

![Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-13-5-p027.png)

*Figure 13. Sections at a, >0 are identical due to the symmetry about a, = 0.: Sections at a, >0 are identical due to the symmetry about a, = 0.*

![Figure 22. Second type of view bifurcation set near a TV singularity. The coordinate frame is the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-22-p028.png)

*Figure 22. Second type of view bifurcation set near a TV singularity. The coordinate frame is the: Second type of view bifurcation set near a TV singularity. The coordinate frame is the V singularity. The coordinate frame is the same as in Fig. 12. Here five cells of stable views meet at the origin. Again the bifurcation set is symmetric about a, = 0*

![Figure 23. A section through the bifurcation set of Figure 22 at a, <0 or at a, > 0. The notation is the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-23-p028.png)

*Figure 23. A section through the bifurcation set of Figure 22 at a, <0 or at a, > 0. The notation is the: A section through the bifurcation set of Fig. 22 at a, <0 or at a, > 0. The notation is the same as in Fig. 13.*

![Figure 24. First type of view bifurcation set near a V singularity. The coordinate frame is the same a](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-24-p029.png)

*Figure 24. First type of view bifurcation set near a V singularity. The coordinate frame is the same a: first type of view bifurcation set near a V singularity. The coordinate frame is the same a as in Fig. 12. Here five cells of stable views meet at the origin. Again the bifurcation set is symmetric about a, = 0.*

![Figure 25. A section through the bifurcation set of Figure 24 at a, <0 or at a, >0. The notation is the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-25-p029.png)

*Figure 25. A section through the bifurcation set of Figure 24 at a, <0 or at a, >0. The notation is the: A section through the bifurcation set of Fig. 24 at a, <0 or at a, >0. The notation is the same as in Fig. 13.*

![Figure 26. Second type of view bifurcation set near a V singularity. The coordinate frame is the same](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-26-p030.png)

*Figure 26. Second type of view bifurcation set near a V singularity. The coordinate frame is the same: Second type of view bifurcation set near a V singularity. The coordinate frame is the same as in Fig. 12. Here seven cells of stable views meet at the origin. Again the bifurcation set is symmetric about a, = 0.*

![Figure 27. A section through the bifurcation set of Figure 26 at a, <0 or at a, >0. The notation is the](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-27-p030.png)

*Figure 27. A section through the bifurcation set of Figure 26 at a, <0 or at a, >0. The notation is the: A section through the bifurcation set of Fig. 26 at a, <0 or at a, >0. The notation is the same as in Fig. 13.*

Fig. 26). Figures 25 and 27 show sections at \(a_{1} \neq 0\) through \(\tilde{B}_{1}\) and \(\tilde{B}_{2}\) indicating strata of transitional views and nearby stable views.

### 4.2 A multi-local singularity of codimension 3: An example

The degenerate local projections arise when we view certain special points on a surface patch from special centres of projection. It is also possible to see unusual multi-local views from special centres of projection when the line of sight is tangent to a surface at several distinct points. Here the intrinsic geometry of the surface patches near such points is not very complicated but their relative locations in space are unusual. Not much is known about the local geometry of the view bifurcation set near centres of projection corresponding to multi-local singularities of codimension 3 (see, for example, [17] for a list of multi-local singularities of codimension less than or equal to 2), except in the case of bi-local singularities which have been studied in [19, Chapter 4]. Let us, however, consider one example: the singularity \(F++++F\) of codimension 3 consisting of a pair of folds having four-point contact. Note that a pair of folds has one-point contact if the line of sight grazes a surface at two points (i.e., is a bitangent ray) whose normals are not parallel (and we see a typical T-junction). We know that T-junctions are stable under slight changes of viewing position, and hence such viewing positions form cells in view space. Jan Koenderink introduced in [10] the concept of the bitangent ray manifold to study bifurcations of T-junctions. The boundaries of the cells of the bitangent ray manifold are formed by special rays which are tangent at two points whose normals are parallel. It follows that these boundaries (which are subsets of the view bifurcation set) form ruled surfaces corresponding to views \(F++F\) containing a pair of folds having tangential contact. This ruled surface, however, is not necessarily smooth: it may have cuspidal edges corresponding to one-dimensional strata of \(F+++F\) views (fold pairs having inflexional contact), and from special centres of projection we might have \(F++++F\) views. Koenderink (personal communication) discovered in numerical computer studies of the bitangent ray manifold that the most degenerate singularities of this manifold, which persist under small deformations of the surface \(M\), are swallowtail points in view space corresponding to \(F++++F\) views. Calculating the bifurcation set in the parameter space of the versal unfolding of \(F++++F\) (of minimal dimension) shows that the most degenerate points of the bitangent ray manifold of any generic surface \(M\) (or in fact of a versal three-parameter family of projections of any smooth surface) are indeed swallowtail points. Figure 28 shows a section through a swallowtail surface at \(a_{1}<0\) indicating the \(F++F\) and \(F+++F\) strata, and nearby stable views (the complete swallowtail surface looks like Fig. 12). The parameters ( \(a_{1}, a_{2}, a_{3}\) ) refer to the parameters of the versal unfolding of \(F++++F\) :

$$
\left\{\begin{array}{l} (\boldsymbol{a}, x, y) \mapsto\left(\boldsymbol{a}, x, y^{2}\right), \\ (\boldsymbol{a}, \bar{x}, \bar{y}) \mapsto\left(\boldsymbol{a}, \bar{x}, \bar{y}^{2}+\bar{x}^{4}+a_{1} \bar{x}^{2}+a_{2} \bar{x}+a_{3}\right) . \end{array}\right.
$$

(Here \((x, y)\) and \((\bar{x}, \bar{y})\) are local coordinates of the two surface patches, which project onto a common point in the image plane-see [17, 19] for details on unfoldings of multi-local singularities.)

## 5 A Remark on Finding Apparent Contours

The simplest conceivable lighting model assumes that the image intensity of a viewed point only depends on the angle between the surface normal at that point and the direction of illumination. This assumes, apart from the surface being a diffuse (Lambertian) reflector, that the imaged surface is convex (i.e., there are no interreflections), that there is a single light source, and that there are no cast shadows or surface markings. Note that most of these complications are, however, determined by some surface characteristics and the mutual disposition of (perhaps several) light sources and a surface, and are not affected by camera position. (The exception is, of course, specular reflection: highlights tend to move on the surface as the camera position changes.) Hence, if we ignore highlights, we can conceptually decouple the projection process and the (complex) processes that light the surface and give rise to a foliation of the surface into curves of equal brightness (so-called isophotes). Consider a piece of surface containing two regions with different reflectance properties, which are therefore separated by a brightness discontinuity (surface marking). On either side of the discontinuity we have (generically) fields of smooth isophotes which (again generically) meet the discontinuity transversely (see Fig. 29). Now project the patch onto the image plane: if the patch is visible and not near a contour generator the foliation by image isophotes will be diffeomorphic to the foliation of the surface patch by its isophotes (so that the projection of the patch looks like the patch itself-modulo some

![Figure 29. Top row](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-29-p033.png)

*Figure 29. Top row: isophotes on a surface patch with discontinuity (bold line) and contour generator (dashed line) on the left. Projection of the patch on the right. Bottom row: isophotes on surface patch without discontinuity (left) and its projection (right) showing the tangency of projected isophotes along the fold locus more clearly.*

distortion). If, however, the patch contains a contour generator crossing the brightness discontinuity, we see a folded version of the surface patch (see Fig. 29): generically the image isophotes will be tangent to the apparent contour (except for some exceptional image isophotes, which form a set of measure 0 and are tangent to the line of sight—see Remark 5.1 below). If the background consists of a projected piece of surface then we have also image isophotes on the opposite side of the apparent contour, which are not related to the foreground and are (generically) transverse to the apparent contour. We conclude that apparent contours are curves in the image of brightness discontinuity along which (almost) all image isophotes on one side of this curve become tangent as they approach the discontinuity. (In other words, the apparent contour is the envelope of these image isophotes.) This observation and the geometry of exceptional isophotes follow from a classification of families of plane curves by Dufour [6]. Figure 30 shows as an example the image isophotes of a torus with two cups and two T-junctions in front of a planar background (there are two lightsources in the scene). As one of the referees of this paper has rightly pointed out, many of the isophotes on the torus actually seem to be transverse to the apparent contour. The reason for this is the high curvature of some image isophotes near the apparent contour. To illustrate this problem, let us consider the geometry near one of the degenerate isophotes mentioned above, which are actually tranverse to the apparent contour. Consider the family of isophotes parametrized by \(t\), where each member of the family (for fixed \(t\) ) is a plane curve parametrized by \(x\) (see Fig. 31). From the classification of families of plane curves (see [6; 19,

![Figure 30. Image isophotes of a scene containing a torus and a planar background.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-30-p034.png)

*Figure 30. Image isophotes of a scene containing a torus and a planar background.: Image isophotes of a scene containing a torus and a planar background.*

$$
\alpha_{t}(x)=\left(t+t x+x^{3}, x^{2}\right),
$$

![Figure 31. Image isophotes near a degenerate isophote, which is transverse to the apparent contour.](/Users/evanthayer/Projects/paperx/docs/1990_geometry_of_view_space_opaque_objects_bounded_by_smooth_surfaces/figures/figure-31-p034.png)

*Figure 31. Image isophotes near a degenerate isophote, which is transverse to the apparent contour.: Image isophotes near a degenerate isophote, which is transverse to the apparent contour.*

\((t, x)=(0,0)\), drops rank if and only if \(x=0\), so that the critical values of \(\alpha\) form the curve \(\alpha_{t}(0)=(t, 0)\).

Remark 5.1. Classically, the envelope of a family of plane curves \(F(t, X, Z)=\) \(0, t\) being the parameter, is defined to be the discriminant of \(F\), obtained by eliminating \(t\) from \(F(t, X, Z)=\partial F(t, X, Z) / \partial t=0\). We can get an implicit equation for the family of curves parametrized by \(\alpha(t, x)\) by calculating the resultant of \(t+t x+x^{3}-X=x^{2}-Z=0\) with respect to \(x\), giving \(F(t, X, Z)=\)

Using the well-known formula for the curvature of a parametrized plane curve (involving the first and second derivatives of \(\alpha_{t}(x)=\left(t+t x+x^{3}, x^{2}\right)\) with respect to \(\left.x\right)\) we get

$$
\kappa_{t}(x)=\frac{2 t-6 x^{2}}{\left(t^{2}+4 x^{2}+6 t x^{2}+9 x^{4}\right)^{3 / 2}}
$$

Along the apparent contour we have k,(0) = 2 f. Also note that the tangent vectors to the isophotes da, (x) dx = (t + 3x' ', 2x) are defined along the apparent contour a,(0) and are tangent to it, except for the exceptional isophote at t = 0 which has a cusp. At the cusp the curvature is infinite, and moving along the apparent contour the curvature away from t = 0 becomes finite: as the cusp unfolds, the curvature along the apparent contour drops according to 2 f. In a digital picture the isophotes have finite resolution so that the isophotes near an exceptional isophote (i.e., in some neighborhood of t= 0) appear to be transverse to the apparent contour, because of their high curvature near the contour. With the techniques of this paper (from differential topology) we can only make qualitative but no quantitative statements: we cannot predict the resolution necessary to detect the tangency of isophotes outside some interval around t=0 to the contour, we merely can guarantee that a fine enough resolution exists. Of course, it will be necessary to develop an algorithm for finding the apparent contour based on this observation and then do some extensive tests on real images to judge the usefulness of this remark. But the above might perhaps give the reader some hope about the purely geometrical results of the previous sections.

## 6 Open Problems and Current Work

In this section we want to discuss briefly two areas of current interest. The first area has to do with the evolution of view bifurcation sets of families of surfaces. Of particular interest are the one-parameter families of surfaces that arise from diffusion processes, because they yield a well-defined way of representing three-dimensional shapes at various levels of detail. One advantage of representations based on diffusion over other hierarchical shape representations, which often use a very limited set of basic shapes (such as cubes, cylinders, cones, spheres, etc.) and boolean operators defined on them, is that they model a wide class of surfaces for which important concepts like genericity and stability can be defined in a precise way. Here we want to mention a couple of diffusion processes. Brakke [2] has studied the diffusion of a surface by motion along its inward normals proportional to the mean curvature, and Koenderink and van Doorn [13] have proposed to diffuse the bounding surface of an object by volume-based Gaussian blurring. Discontinuities will develop on the surface after a short time with both diffusion techniques, even for smooth initial surfaces, so that evolutions of view bifurcation sets different from the ones described in the present paper must be expected. It would be very interesting to classify such diffusion processes and the resulting evolutions of view bifurcation sets over time. (In [19, Chapter 6] we have studied the evolution of bifurcation sets in the plane of maps from \(\mathbb{R}^{2}\) to \(\mathbb{R}^{2}\) by classifying functions on stratified semialgebraic sets in \(\mathbb{R}^{3}\)-however, the relation between this general classification and the special kinds of families arising in multi-scale surface descriptions in computer vision is not well understood at the present time.) Finally, we want to mention an algorithmic problem. One is interested in view bifurcation sets, because they separate the regions in view space that correspond to stable views. The computation of the view bifurcation set is the hardest step in any algorithm that derives from a parametrization of a surface all its topologically distinct views ("characteristic views" [5]). Using some of the results in [18, 20], we have designed an algorithm that derives the defining equations of the bifurcation set on the viewing sphere from a parametrization & of a smooth, algebraic surface (the algorithm performs symbolic rather than numerical computations). This recent work brings up many new theoretical questions of a global kind (note that the present classification merely gives local, or semiglobal, information about the bifurcation set), such as: Is there an upper bound for the number of connected regions on the viewing sphere in terms of the degree of o?

Appendix A. Some Details on the Versality of Families of Projections

In Section 2.5 we made the claim that the families (4) of orthogonal projections of certain surfaces (or families of surfaces) are locally versal (or topologically versal). The fact that these families are versal implies that the bifurcation geometry of these families (i.e., the geometry of the bifurcation set and of the stable apparent contours in the complement of the bifurcation set) is the same as the bifurcation geometry of certain normal forms, which can be studied much more easily than the families (4). Here we want to sketch the proof of this claim.

first, the definition of a versal unfolding. Let f: R",0→ R",0 be a C*-map germ given by X = f(x), and let F: R" × R",0→ R* × R",0 denote a d-parameter unfolding of f, given by Fa, x) = (a, f(a, x)) where f(0, x) = f(x). Two d-parameter unfoldings F and G are isomorphic if there exist germs of diffeomorphisms \(H(a,X)\) = (a, ha, X)) of Rdx xR°,0 and \(K(a,x)\) = (a, \(K(a,x)\)) of R" × R", ,0, such that G = H·FoK ! Now let F: R" × R",O→R° × RP,0 and G: R'×R"0→ R'×R"0 denote unfoldings of f: R",0→R",0, and let $: R°,0 → R",0 denote a C"-map germ given by a = q(b). Let \(F(a,fa,x)\)) be the above unfolding, and define G = 4*F, the pull-back of F by 4, as follows:

$$
\begin{aligned} & G: \mathbb{R}^{s} \times \mathbb{R}^{n}, \mathbf{0} \rightarrow \mathbb{R}^{s} \times \mathbb{R}^{p}, \mathbf{0}, \\ & G(\boldsymbol{b}, \boldsymbol{x})=(\boldsymbol{b}, \bar{f}(\varphi(\boldsymbol{b}), \boldsymbol{x})) . \end{aligned}
$$

We say that two unfoldings \(F\) and \(G\) are equivalent if there exists a \(\varphi\) such that \(G\) is isomorphic to \(\varphi^{*} F\). And an unfolding \(F\) of \(f\) is said to be versal if every unfolding of \(f\) is isomorphic to \(\varphi^{*} F\) for some \(\varphi\).

Next, we want to state a necessary and sufficient condition for the versality of an unfolding. Let \(E_{n, p}\) denote the space of \(C^{\infty}\)-map germs from \(\mathbb{R}^{n}, \mathbf{0}\) to \(\mathbb{R}^{p}, \mathbf{0}\), and let \(\mathscr{A}_{\mathrm{e}}=\operatorname{Diff}\left(\mathbb{R}^{n}, \mathbf{0}\right) \times \operatorname{Diff}\left(\mathbb{R}^{p}, \mathbf{0}\right)\) denote the (pseudo)group of right-left equivalences (see Section 2.2). The action of this group on the space \(E_{n, p}\) is given by \((h, k) \cdot f=h \circ f \circ k^{-1}\), for \((h, k) \in \mathscr{A}_{\mathrm{e}}\) and \(f \in E_{n, p}\). The orbit of \(f\)

$$
\frac{\mathrm{d}}{\mathrm{~d} t}\left(h_{t} \circ f \circ k_{t}^{-1}\right)_{t=0}
$$

Now we can state the following:

Versality Theorem. An unfolding

$$
F: \mathbb{R}^{d} \times \mathbb{R}^{n}, \mathbf{0} \rightarrow \mathbb{R}^{d} \times \mathbb{R}^{p}, \mathbf{0},
$$

$$
F(a, x)=(a, \bar{f}(a, x))
$$

$$
of \(f: \mathbb{R}^{n}, \mathbf{0} \rightarrow \mathbb{R}^{p}, \mathbf{0}\) is versal if and only if
$$

$$
T \mathscr{A}_{\mathrm{c}} \cdot f+\mathbb{R}\left\{\frac{\partial \bar{f}(\boldsymbol{a}, \boldsymbol{x})}{\partial a_{i}}\right\}=E_{n, p}, \quad i=1, \ldots, d .
$$

Remarks. (i) The codimension of a singularity \(f\) is defined to be \(\operatorname{dim}_{\mathbb{R}} E_{n, p} /\) \(T \mathscr{A}_{e} \cdot f\), hence any unfolding of a stable singularity (of codimension 0) is versal-a stable singularity is already unfolded. (ii) The Versality Theorem says that, in order to construct a versal unfolding of a degenerate singularity \(f\), one simply has to add certain monomials \(\varphi_{i}=\Pi_{j=1}^{n} x_{j}^{\alpha_{j}} \cdot \partial / \partial X_{k}\) to \(f\), which form a linearly independent basis for the quotient space \(E_{n, p} / T \mathscr{A}_{\mathrm{e}} \cdot f\). The resulting unfolding \(F(\boldsymbol{a}, \boldsymbol{x})=(\boldsymbol{a}, f(\boldsymbol{x})+\) \(\left.\sum_{i=1}^{d} a_{i} \varphi_{i}\right)\) is versal, and its dimension \(d\) is greater than or equal to the codimension of \(f\).

From the second remark it should be clear that it is very easy to check whether a given unfolding \(F\) of a map germ \(f\) is versal-provided we know \(T \mathscr{A}_{\mathrm{e}} \cdot f!\) Consider the family (4):

$$
\binom{\bar{X}}{\bar{Z}}=\binom{\left(a_{1}^{2}-a_{2}^{2}+a_{3}^{2}\right) x-2 a_{2} a_{3} y+2 a_{1} a_{2} Z(x, y)}{2 a_{1} a_{2} x+2 a_{1} a_{3} y-\left(a_{1}^{2}-a_{2}^{2}-a_{3}^{2}\right) Z(x, y)},
$$

where \(a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=1\). Differentiating with respect to the unfolding parameters \(a_{i}\), and evaluating at \(a_{1}=a_{2}=0, a_{3}=1\) gives:

(0,2 y)^{\mathrm{T}}, \quad(-2 y, 0)^{\mathrm{T}}, \quad(2 x, 2 \(Z(x,y)\))^{\mathrm{T}} .

The last vector cannot be obtained from the family (4), because \(\partial / \partial a_{3}\) is not contained in the tangent space to the two-sphere \(a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=1\) at \(a_{1}=a_{2}=\)

$$
T \mathscr{A}_{\mathrm{e}} \cdot(x, Z(x, y))+\mathbb{R}\left\{\binom{0}{2 y}\binom{-2 y}{0}\right\}=E_{n, p} .
$$

```text
The nontrivial part of this proof is the calculation of the tangent spaces \(T \mathscr{A}_{\mathrm{c}} \cdot(x, Z(x, y))\), for each \(Z(x, y)\) of Section 2.5-but fortunately the results of [18] can be used to do this without much effort. For the list of families of surfaces Z(t, x, y) = Zo(x, y) + tP(x, y), we obtain, after differentiating with respect to the unfolding parameters and evaluating at
```

$$
\(t=a_{1}=a_{2}=0, a_{3}=1\), the following condition from the Versality Theorem:
$$

$$
T \mathscr{A}_{\mathrm{e}} \cdot(x, Z(x, y))+\mathbb{R}\left\{\binom{0}{2 y}\binom{-2 y}{0}\binom{0}{2 P(x, y)}\right\}=E_{n, p} .
$$

Again using the results of [18], it can be shown that this condition is satisfied for \(Z(t, x, y)=x^{2}+y^{3} \pm x^{4} y+t x^{2} y\) and \(x y^{2}+y^{4}+x^{3} y+t x^{2} y\)-hence the cor-

## Acknowledgement

I am grateful to Peter Giblin and Jan Koenderink for helpful conversations, and I thank one of the referees for his critical comments concerning the presentation of results.

## References

- V.I. Arnol'd, Singularities of systems of rays, Russian Math. Surv. 38 (1983) 87-176.

- K.A. Brakke, The Motion of a Surface by its Mean Curvature, Princeton Mathematical Notes 20 (Princeton University Press, Princeton, NJ, 1978).

- J.W. Bruce and P.J. Giblin, Outlines and their duals, Proc. London Math. Soc. (3) 50(1985), 552-570.

- J. Callahan and R. Weiss, A model for describing surface shape, in: Proceedings IEEE Conference on Computer Vision and Pattern Recognition, San Francisco, CA (1985) 240-245.

- J.P. Dufour, Familles de courbes planes differentiables, Topology 22 (1983) 449-474.

- I. Chakravarty and H. Freeman, Characteristic views as a basis for three-dimensional object recognition, Proc. SPIE 336 (1982) 37-45.

- W.E.L. Grimson, Recognition of object families using parameterized models, in: Proceedings first International Conference Computer Vision, London (1987) 93-101.

- J.R. Kender and D.G. Freudenstein, What is a "degenerate" view?, Preprint, Department of Computer Science, Columbia University, New York (1986).

- J.J. Koenderink, What does the occluding contour tell us about shape?, Perception 13(1984) 321-330.

- J.J. Koenderink, The internal representation of solid shape based on the topological properties of the apparent contour, in: W. Richards and S. Ullman, eds., Image Understanding 19851986 (Ablex, Norwood, NJ, 1986) 257-286.

- J.J. Koenderink and A.J. van Doorn, The singularities of the visual mapping, Biol. Cybern. 24 (1976) 51-59

- J.J. Koenderink and A.J. van Doorn, The internal representation of solid shape with respect to vision, Biol. Cybern. 32 (1979) 211-216.

- J.J. Koenderink and A.J. van Doorn, Dynamic shape, Biol. Cybern. 53 (1986) 383-396.

- C. McCrory, Profiles of surfaces, Preprint, Mathematics Institute, University of Warwick, Coventry (1980), corrected (1981).

- J. Malik, Interpreting line drawings of curved objects, Int. J. Comput. Vision 1 (1987) 73-103.

- D. Mond, Singularities of the exponential map of the tangent bundle associated with an immersion, Proc. London Math. Soc. (3) 53 (1986) 357-384.

- J.H. Rieger, On the classification of views of piecewise smooth objects, Image Vision Comput. 5 (1987) 91-97.

- J.H. Rieger, Families of maps from the plane to the plane, J. London Math. Soc. (2) 36 (1987) 351-369.

- J.H. Rieger, Apparent contours and their singularities, Ph.D. Thesis, Queen Mary College. London (1988)

- J.H. Rieger, Versal topological stratification and the bifurcation geometry of map-germs of the plane, Math. Proc. Cambridge Philos. Soc. (to appear).

- H. Whitney, On the singularities of mappings of Euclidean spaces, I: Mappings of the plane into the plane, Ann. of Math. 62(1955) 374-410.

- Received January 1988; revised version received March 1989
