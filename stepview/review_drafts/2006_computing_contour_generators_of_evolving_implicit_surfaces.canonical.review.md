# Computing Contour Generators of Evolving Implicit Surfaces

Simon Plantinga, Gert Vegter

Site: University of Groningen

University of Groningen

## Abstract

Generated abstract from paper content. This paper develops a framework and algorithms for computing contour generators and apparent contours of implicit surfaces, including surfaces or viewpoints that evolve over time. For generic static and time-dependent cases, it derives local normal forms and algebraic conditions for regular points, folds, cusps, and the principal topology-changing bifurcations of contours, including lips, beak-to-beak, and swallowtail events. Building on these characterizations, the authors use interval analysis and adaptive tracing to compute an initial contour generator with topological guarantees. The approach is intended as a robust foundation for maintaining correct contour topology during deformation or viewpoint change.

## 1 Introduction

An important visibility feature of a smooth object seen under parallel projection along a certain direction is its contour generator, also known as outline, or profile. The contour generator is the curve on the surface, separating front-facing regions from back-facing regions. This curve may have singularities if the direction of projection is non-generic. The apparent contour is the projection of the contour generator onto a plane perpendicular to the view direction. In many cases, drawing just the visible part of the apparent contour gives a good impression of the shape of the object. In this paper, we will not distinguish between visible and invisible parts of the contour generator. Stated otherwise, we assume the surface is transparent. Generically, the apparent contour is a smooth curve, with some isolated singularities. See Figure 1.

The contour generator and the apparent contour play an important role in computer graphics and computer vision. Rendering a polyhedral model of a smooth surface yields a jaggy outline, unless the triangulation of the surface is finer in a neighbourhood of the contour generator. This observation has led to techniques for view-dependent meshing and view-dependent refinement techniques, cf. [1]. ∗ email: { simon|gert } @cs.rug.nl

![Figure 1](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-1-p003.png)

*Figure 1: A smooth surface (left), its apparent contour under parallel projection along the z direction (middle), and its contour generator, seen from a diﬀerent position (right). For generic surfaces (or, generic parallel projections) the contour generator is a smooth, possibly disconnected curve on the surface, whereas the apparent contour may have isolated cusp points. different position (right). For generic surfaces (or, generic parallel projections) the contour generator is a smooth, possibly disconnected curve on the surface, whereas the apparent contour may have isolated cusp points.*

Also, to render a smooth surface it is sufficient to render only the part of the surface with front-facing normals, so the contour generator, being the boundary of the potentially visible part plays a crucial role here. In non-photorealistic rendering [17] one just visualizes the apparent contour, perhaps enhanced by strokes indicating the main curvature directions of the surface. This is also the underlying idea in silhouette rendering of implicit surfaces [6]. In computer vision, techniques have been developed for partial reconstruction of a surface from a sequence of apparent contours corresponding to a discrete set of nearby projection directions. We refer to the book [9] for an overview, and for a good introduction to the mathematics underlying this paper. Other applications use silhouette interpolation [12] from a precomputed set of silhouettes to obtain the silhouette for an arbitrary projection. In computational geometry, rapid silhouette computation of polyhedral models under perspective projection with moving viewpoints has been achieved by applying suitable preprocessing techniques [4].

This paper presents a method for the robust computation of contour generators and apparent contours of implicit surfaces. For an introduction to the use of implicit surfaces for smooth deformable object modeling we refer to [19] and [5].

We first consider generic static views, where both the surface and the direction of projection are static. Then we pass to time-dependent views, where the direction of projection changes with time. We derive conditions that locate the changes in the topology of the contour generator and the apparent contour. It turns out that generically there are three types of events, or bifurcations, leading to such a change in topology. These bifurcations have been studied from a much more advanced mathematical point of view, where they are known under the names lips, beak-to-beak, and swallowtail bifurcation. See also [8]. For a nice non-mathematical description we refer to the beautiful book by Koenderink [16]. Also see Arnol'd [3] and Bruce [7] for a sketch of some of the mathematical details related to singularity theory. Arnol'd [2] contains some of the results of the paper in a complex analytic setting. Our approach is somewhere inbetween the level of Koenderink's book and the sophisticated mathematical approach. We use only elementary tools, like the Inverse and Implicit Function Theorem, and finite order Taylor expansions. These techniques are used to design algorithms, in the same way as the Implicit Function Theorem gives rise to Newton's method.

Most curve tracing algorithms step along the curve using a fixed step size. See for example [6] or [15]. For a good approximation, the user has to choose a step size that is 'small enough' to follow the details of the curve. Some algorithms predict a dynamic step size, based on the local curvature. Both methods cannot guarantee a correct approximation to the curve. Also, these curve tracing algorithms assume there are no singularities. By examining the singularities before tracing the curve we can avoid them in the tracing process. We developed a condition based on interval analysis, that guarantees topological correctness of the traced curve.

In Section 2 we present the framework, and discuss criteria for a point on the contour generator and apparent contour to be regular. Section 3 examines singularities under some time-dependent view, for example when the viewpoint moves or when the surface deforms. In section 4 we explain the transformation to local models. Section 5 shows in detail how to derive local models near fold and cusp points. In section 6 we examine contours for time-dependent views. For the implementation interval analysis is used. A brief overview can be found in section 7. The algorithm for computing the contour generator is explained in section 8.

## 2 Contour generator and apparent contour

Contour generators of implicit surfaces To understand the nature of regular and singular points of the contour generator, and their projections on the apparent contour, we assume S is given as the zero-set of a smooth function F : \(R_{3}\) → R, so S = F-1 (0). Furthermore, we assume that 0 is a regular value of F, i.e., the gradient ∇ F is non-zero at every point of the surface. The gradient vector ∇ \(F(p)\) is the normal of the surface at p, i.e., it is normal to the tangent plane of S at p. This tangent plane is denoted by T p (S). If v is the direction of parallel projection, then the contour generator Γ is the set of points at which the normal to S is perpendicular to the direction of projection, i.e., p ∈ Γ iff the following conditions hold:

$$
\begin{align*} F(p) & =0 \\ \langle\nabla F(p), v\rangle & =0 \tag{1} \end{align*}
$$

For convenience, we assume throughout the paper that v = (0, 0, 1). Then the preceding equations reduce to

$$
\begin{align*} & F(x, y, z)=0 \\ & F_{z}(x, y, z)=0 \tag{2} \end{align*}
$$

Here, and in the sequel, we shall occasionally write \(F_{z}\) instead of \(\frac{\partial F}{\partial z}(p)\). We also use notation like \(F_{x}\) and \(F_{z_{z}}\), with a similar meaning. We assume that S is a generic surface, i.e. there are no degenerate singular points on its contour generator. Some functions can yield degenerate contour generators. For example, a cylinder has a two-dimensional contour generator for the view direction along its axis. Using a small perturbation, we can remove these degeneracies. In the case of the cylinder, the two-dimensional contour generator collapses to a one-dimensional curve. See for example [21].

We now derive conditions for the contour generator \(\Gamma\) and the apparent contour \(\gamma\) to be regular at a given point. Recall that a curve is regular at a certain point if it has a non-zero tangent vector at that point. The next result gives conditions in terms of the function defining the surface. Proposition 2.1.

1. A point p ∈ Γ is a regular point of the contour generator if and only if

$$
\begin{equation*} F_{z z}(p) \neq 0 \quad \text { or } \quad \Delta(p) \neq 0 \tag{3} \end{equation*}
$$

where ∆(p) is a Jacobian determinant defined by

$$
\Delta(p)=\left.\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{p}=\left|\begin{array}{cc} F_{x}(p) & F_{y}(p) \\ F_{x z}(p) & F_{y z}(p) \end{array}\right|
$$

∣ ∣ ∣ 2. A point p ∈ γ is a regular point of the apparent contour if and only if

$$
\begin{equation*} F_{z z}(p) \neq 0 \tag{4} \end{equation*}
$$

Proof. 1. The condition for p to be regular is

$$
\nabla F(p) \wedge \nabla F_{z}(p) \neq 0
$$

Since \(F_{z}(p)=0\), a straightforward calculation yields

$$
\begin{equation*} \nabla F(p) \wedge \nabla F_{z}(p)=F_{z z} \cdot\left(F_{y},-F_{x}, 0\right)+\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)} \cdot(0,0,1) \tag{5} \end{equation*}
$$

Since \(\nabla F(p)=\left(F_{x}(p), F_{y}(p), 0\right) \neq 0\), we see that \(\left(F_{y},-F_{x}, 0\right)\) and \((0,0,1)\) are linearly independent vectors. Therefore, the linear combination of these vectors in the right-hand side of (5) is zero iff the corresponding scalar coefficients are zero. The necessity and sufficiency of condition (3) is a straightforward consequence of this observation.

2. Since ∇ \(F(p)=0\) ∈ \(R_{3}\), and F \(z(p)=0\), we see that (F x (p), F y (p)) = (0, 0). Assuming F \(y(p)=0\), we get

$$
\left.\frac{\partial\left(F, F_{z}\right)}{\partial(y, z)}\right|_{p}=\left|\begin{array}{cc} F_{y} & F_{z} \tag{6}\\ F_{y z} & F_{z z} \end{array}\right|_{p}=F_{y}(p) F_{z z}(p) \neq 0
$$

Let \(p=\left(x_{0}, y_{0}, z_{0}\right)\). Then, the Implicit Function Theorem yields locally defined functions \(\eta, \zeta: \mathbb{R} \rightarrow \mathbb{R}\), with \(\eta\left(x_{0}\right)=y_{0}\) and \(\zeta\left(x_{0}\right)=z_{0}\), such that (2) holds iff \(y=\eta(x)\) and \(z=\zeta(x)\). The contour generator is a regular curve parametrized as \(x \mapsto(x, \eta(x), \zeta(x))\), locally near \(p\), whereas the apparent contour is a regular curve in the plane parametrized as \(x \mapsto(x, \eta(x))\), locally near Singular points of contour generators We apply the preceding result to detect non-degenerate singularities of contour generators of implicit surfaces. This result will be applied later in this section, when we consider contour generators of time-dependent surfaces. Again, let the regular surface \(S\) be the zero set of a \(C^{3}\)-function \(F: \mathbb{R}^{3} \rightarrow \mathbb{R}\), for which 0 is a regular value. We consider the contour generator \(\Gamma\) of \(S\) under parallel projection along the vector

$$
F=F_{z}=0
$$

We consider the contour generator as the zero-set of the function \(F_{z}\), restricted to \(S\).

Corollary 2.2. point \(p\) is a non-degenerate singular point of \(\Gamma\) iff the following two conditions hold:

$$
\begin{equation*} F(p)=F_{z}(p)=F_{z z}(p)=\left.\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{p}=0 \tag{7} \end{equation*}
$$

$$
and \( \Sigma(p) \neq 0 \), where, for \( F_{x}(p) \neq 0 \),
$$

$$
whereas, for \( F_{y}(p) \neq 0 \), we have
$$

Proof. Condition (7) reflects the fact that \(p\) is a singular point of \(F_{z} \mid S\), cf. (3), whereas (8) expresses non-degeneracy of this singular point. Condition (8) is obtained by a straightforward expansion \({ }^{1}\) of (46) (see appendix A), with \(G=F_{z}\), and \(V=X\) as in (47), where \(\lambda=\frac{F_{x_{z}}^{0}}{F_{x}^{0}}, F_{z}^{0}=F_{z_{z}}^{0}=0\), and Generic projections: fold and cusp points In view of Proposition 2.1, regular points of the apparent contour are projections of points \((x, y, z) \in \mathbb{R}^{3}\) satisfying

$$
F(x, y, z)=F_{z}(x, y, z)=0, \quad \text { and } \quad F_{z z}(x, y, z) \neq 0 .
$$

This being a system of two equations in three unknowns, we expect that the regular points of the

![Figure 2](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-2-p006.png)

*Figure 2: (a) A local model of the surface at a fold point is x + z 2 = 0. Both the contour generator Γ, and the visible contour γ , are regular at the fold point, and its projection onto the image plane, respectively. (b) A local model at a cusp point is x + yz + z 3 = 0. Here the contour generator is regular, but the apparent contour has a regular cusp.*

1 using a computer algebra system

$$
\begin{align*} \Sigma(p)= & -F_{x}^{2} F_{x z z}^{2} F_{y}^{2}+2 F_{x}^{3} F_{x z z} F_{y} F_{y z z}-F_{x}^{4} F_{y z z}^{2} \\ & -2 F_{x}^{3} F_{x y z} F_{y} F_{z z z}+2 F_{x}^{2} F_{x y} F_{x z} F_{y} F_{z z z} \\ & +F_{x}^{2} F_{x x z} F_{y}^{2} F_{z z z}-F_{x} F_{x x} F_{x z} F_{y}^{2} F_{z z z} \tag{8}\\ & -F_{x}^{3} F_{x z} F_{y y} F_{z z z}+F_{x}^{4} F_{y y z} F_{z z z}, \end{align*}
$$

$$
\begin{align*} \Sigma(p)= & -F_{x z z}^{2} F_{y}^{4}+2 F_{x} F_{x z z} F_{y}^{3} F_{y z z}-F_{x}^{2}{F_{y}^{2}}^{2} F_{y z z}^{2} \\ & -2 F_{x} F_{x y z} F_{y}^{3} F_{z z z}+F_{x x z} F_{y}^{4} F_{z z z} \\ & +F_{x}^{2} F_{y}^{2} F_{y y z} F_{z z z}+2 F_{x} F_{x y} F_{y}^{2} F_{y z} F_{z z z} \tag{9}\\ & -F_{x x} F_{y}^{3} F_{y z} F_{z z z}-F_{x}^{2} F_{y} F_{y y} F_{y z} F_{z z z} \end{align*}
$$

apparent contour form a one-dimensional subset of the plane. Furthermore, the singular points of the apparent contour are projections of points satisfying an additional equation, viz. \(F_{z_{z}}(x, y, z)=0\), and are therefore expected to be isolated. This is true for generic surfaces. To make this more precise, we consider the set of functions \(F: \mathbb{R}^{3} \rightarrow \mathbb{R}\), satisfying

$$
\begin{equation*} \left(F(x, y, z), F_{z}(x, y, z), F_{z z}(x, y, z), \Delta(x, y, z)\right) \neq(0,0,0,0) \tag{10} \end{equation*}
$$

If \(F\) satisfies (10), then Proposition 2.1 tells us that the contour generator \(\Gamma\) of \(S=F^{-1}(0)\) under

- F zz (x, y, z) = 0; in this case the point projects to a regular point (x, y) of the apparent contour γ . Such a point is called a fold point of the contour generator. This terminology is justified by the local model of the surface near a fold point, viz.

$$
\begin{equation*} x+z^{2}=0 \tag{12} \end{equation*}
$$

See also Figure 2a. Here the contour generator is the \(y\)-axis in three space, so the apparent contour is the \(y\)-axis in the image plane.

$$
\begin{equation*} G(x, y, z)=x+y z+z^{3}=0 \tag{13} \end{equation*}
$$

- F zz (x, y, z) = 0; in this case the point projects to a singular point (x, y) of γ . Such a point is called a cusp point of the contour generator if, in addition to (10), condition (11) is satisfied, i.e., if both ∆(x, y, z) = 0 and F zzz (x, y, z) = 0. In this case the surface has the following local model near the cusp point:

See also Figure 2b. The local model \(G\) is sufficiently simple to allow for an explicit com putation of its contour generator and apparent contour: the former is parametrized by

Intuitively speaking, a local model of the surface near a point is a 'simple' expression of the defining equation in suitably chosen local coordinates. Usually, as in the cases of fold and cusp points, a local model is a low degree polynomial, which can be easily analyzed in the sense that the contour generator and the apparent contour are easily determined.

So far we have only considered parallel projection. The standard perspective transformation [14], which moves the viewpoint to ∞ , reduces perspective projections to parallel projections. By deforming the surface using this transformation, perspective projections can be computed by using parallel projection on the transformed implicit function.

## 3 Evolving contours

However, evolving surfaces depend on an additional variable, t say. Time dependency is expressed by considering implicitly defined surfaces

$$
S_{t}=\left\{(x, y, z) \in \mathbb{R}^{3} \mid F(x, y, z, t)=0\right\}
$$

$$
\begin{equation*} \left(F(x, y, z), F_{z}(x, y, z), F_{z z}(x, y, z), F_{z z z}(x, y, z)\right) \neq(0,0,0,0) \tag{11} \end{equation*}
$$

where \(F: \mathbb{R}^{3} \times \mathbb{R} \rightarrow \mathbb{R}\) is a smooth function of the space variables ( \(x, y, z\) ) and time \(t\). Generically we expect that exactly one of the conditions (10) and (11) will be violated at isolated values of \((x, y, z, t)\). For definiteness, we assume \((0,0,0,0)\) is such a value.

Violation of (10) corresponds to a singularity of the contour generator. In this case the implicit surfaces, defined by \(F(x, y, z, 0)=0\) and \(F_{z}(x, y, z, 0)=0\), are tangent at \((x, y, z)=(0,0,0)\), but the tangency is non-degenerate. Stated otherwise, the function \(G: \mathbb{R}^{3} \rightarrow \mathbb{R}\), defined by \(G(x, y, z)=F_{z}(x, y, z)\), restricted to the surface \(S_{0}\), has a non-degenerate singularity at \((0,0,0)\). Generically, there are two types of bifurcations, corresponding to different scenarios for changes in topology of the contour generator. The beak-to-beak bifurcation corresponds to the merging or splitting of connected components of the contour generator. Under some additional generic conditions (inequalities), a local model for this phenomenon is the surface, defined by

$$
\begin{equation*} G(x, y, z, t)=x+\left(-y^{2}+t\right) z+z^{3}, \tag{14} \end{equation*}
$$

Here the contour generator is defined by \(x=2 z^{3},-y^{2}+3 z^{2}=-t\). See also Figure 3.

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-3-p008.png)

*Figure 3: The beak-to-beak bifurcation. With respect to the local model (14) the bifurcation corresponds to t < 0 (left), t = 0 (middle), and t > 0 (right).*

Putting G t (x, y, z) = \(G(x,y,z,t)\), we check that \(G_{0}\) satisfies (7) at p = (0, 0, 0), and that | Σ(p) | = -4. (In fact, \(G_{0}\) x = 1, so all higher order derivatives of \(G_{0}\) x vanish identically, so only the last term in the right hand side of (8) is not identically equal to zero.) Therefore, \(G_{0}\) z | S has a non-degenerate singular point of saddle type at p. According to the Morse lemma (see [11] or [18]), the level set of \(G_{0}\) z | S through p consists of two regular curves, intersecting transversally at p, which concurs with Figure 3 (middle).

A second scenario due to the violation of (11) is the lips bifurcation, corresponding to the birth or death of connected components of the contour generator. Again, under some additional generic conditions a local model for this phenomenon is the surface, defined by

$$
\begin{equation*} G(x, y, z, t)=x+\left(y^{2}+t\right) z+z^{3}, \tag{15} \end{equation*}
$$

Here the contour generator is defined by \(x=2 z^{3}, y^{2}+3 z^{2}=-t\). In particular, for \(t>0\) the surface

![Figure 4](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-4-p009.png)

*Figure 4: The lips bifurcation. Left: t < 0. Middle: t = 0. Right: t > 0.*

is isolated on the contour generator, and for \(t<0\) there is a small connected component growing out of this isolated point as \(t\) decreases beyond 0. See also Figure 4. As for the beak-to-beak bifurcation, we show that \(G^{0} \mid S\) has a non-degenerate singular point at \((0,0,0)\), which in this case is an extremum.

Violation of (11) involves the occurrence of a higher order singularity of the apparent contour. Note, however, that in this situation the contour generator is still regular at the point (x, y, z), cf. Proposition 2.1. Imposing some additional generic conditions a local model for this type of bifurcation is

$$
\begin{equation*} G(x, y, z, t)=x+y z+t z^{2}+z^{4}=0 . \tag{16} \end{equation*}
$$

Here the apparent contour is parametrized as \(z \mapsto\left(t z^{2}+z^{4},-2 t z-4 z^{3}\right)\). See also Figure 5.

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-5-p009.png)

*Figure 5: The swallowtail bifurcation. Left: t < 0. Middle: t = 0. Right: t > 0.*

## 4 Transformations and normal forms

In Section 2 we presented local models of various types of regular and singular points on contour generators and apparent contours, both for generic static surfaces, and for surfaces evolving generically in time. These local models are low degree polynomials, which are easy to analyze, and which yet capture the qualitative behavior of the contour generator and the apparent contour in a neighborhood of the point of interest. In this section we explain more precisely what we mean by capturing local behavior.

Consider two regular implicit surfaces \(S=F^{-1}(0)\) and \(T=G^{-1}(0)\). An invertible smooth map \(\Phi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{3}\) for which

$$
\begin{equation*} F \circ \Phi=G \tag{17} \end{equation*}
$$

maps \(T\) to \(S\). In fact, we consider \(\Phi\) to be defined only locally near some point of \(T\), but we will not express this in our notation. The map \(\Phi\) need not map the contour generator of \(T\) onto that of \(S\), however. To enforce this, we require that \(\Phi\) maps vertical lines onto vertical lines, i.e., \(\Phi\) should be of the form

$$
\begin{equation*} \Phi(x, y, z)=(h(x, y), H(x, y, z)) \tag{18} \end{equation*}
$$

where \(h: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) and \(H: \mathbb{R}^{3} \rightarrow \mathbb{R}\) are smooth maps. The map \(h\) is even invertible, since \(\Phi\) is invertible. To allow ourselves even more flexibility in the derivation of local models, we relax condition (17) by requiring the existence of a non-zero function \(\varphi: \mathbb{R}^{3} \rightarrow \mathbb{R}\) such that

$$
\begin{equation*} F(\Phi(x, y, z))=\varphi(x, y, z) G(x, y, z) \tag{19} \end{equation*}
$$

Definition 4.1. Let \(S=F^{-1}(0)\) and \(T=G^{-1}(0)\) be regular surfaces, near \(p=(0,0,0) \in \mathbb{R}^{3}\). An admissible local transformation from \(T\) to \(S\), locally near \(p\), is a pair \((\Phi, \varphi)\), where \(\varphi: \mathbb{R}^{3} \rightarrow \mathbb{R}\) is non-zero at \(p\), and \(\Phi: \mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{3}\) is locally invertible near \(p\), and of the form (18), such that (19) holds. We also say that \(\Phi\) brings \(F\) in the normal form \(G\).

If the surfaces \(S\) and \(T\) depend smoothly on \(k\) parameters, i.e., they are defined by functions \(F: \mathbb{R}^{3} \times \mathbb{R}^{k} \rightarrow \mathbb{R}\) and \(G: \mathbb{R}^{3} \times \mathbb{R}^{k} \rightarrow \mathbb{R}\), respectively, then we require that the parameters are not mixed with the \((x, y, z)\)-coordinates, i.e., we require that (19) is replaced with

$$
F(\Phi(x, y, z, \mu))=\varphi(x, y, z, \mu) G(x, y, z, \mu)
$$

where \(\Phi: \mathbb{R}^{3} \times \mathbb{R}^{k} \rightarrow \mathbb{R}^{3} \times \mathbb{R}^{k}\) is of the form

$$
\Phi(x, y, z, \mu)=(h(x, y, \mu), H(x, y, z, \mu), \psi(\mu)) .
$$

Furthermore, the map \(h^{\mu}: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), defined by \(h^{\mu}(x, y)=h(x, y, \mu)\), maps the apparent contour of \(T^{\mu}\) onto that of \(S^{\psi(\mu)}\).

Proposition 4.2. If \(\Phi\) is an admissible local transformation from \(T\) to \(S\), locally near a point \(p\) on the contour generator of \(T\), where \(\Phi\) is of the form (18), then

- Φ maps T to S, locally near p ∈ S ;

- Φ maps the contour generator of T to the contour generator of S, locally near p ;

- h maps the apparent contour of T onto the apparent contour of S, locally near the projection π (p) ∈ \(R_{2}\).

Proof. From (18) and (19) it is easy to derive

$$
\begin{aligned} F(\Phi(p)) & =\psi(p) G(p) \\ F_{z}(\Phi(p)) H_{z}(p) & =\psi_{z}(p) G(p)+\psi(p) G_{z}(p) \end{aligned}
$$

Since \(\psi(p) \neq 0\), and \(H_{z}(p) \neq 0\), we conclude that \(G(p)=G_{z}(p)=0\) iff \(F(\Phi(p))=F_{z}(\Phi(p))=0\).

Example: local model at a truncated cusp point We now illustrate the use of admissible transformations by deriving a local model for the class of implicit surfaces defined as the zero set of a function of the form:

$$
\begin{equation*} F(x, y, z)=a(x, y)+b(x, y) z+c(x, y) z^{2}+z^{3} \tag{20} \end{equation*}
$$

$$
with \( a(0,0)=b(0,0)=c(0,0)=0 \), and
$$

$$
\begin{equation*} \left.\frac{\partial(a, b)}{\partial(x, y)}\right|_{0} \neq 0 \tag{21} \end{equation*}
$$

Note that the local model \(x+y z+z^{3}=0\), derived in Section 2 for a cusp point, belongs to this

$$
\left.\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{0}=\left.\frac{\partial(a, b)}{\partial(x, y)}\right|_{0} \neq 0
$$

we see that \(0 \in \mathbb{R}^{3}\) is a regular point of the contour generator of \(S\), whereas (0,0) is a singular point of the apparent contour, cf. Proposition 2.1 As a first step towards a normal form of the implicit surface, we apply the Tschirnhausen transformation \(z \mapsto z-\frac{1}{3} c(x, y)\) to transform the quadratic term (in \(z\) ) in \(F\) away. More precisely,

$$
\begin{aligned} F\left(x, y, z-\frac{1}{3} c(x, y)\right)= & a(x, y)-\frac{1}{3} b(x, y) c(x, y)+\frac{2}{27} c(x, y)^{3} \\ & +\left(b(x, y)-\frac{1}{3} c^{2}(x, y)\right) z+z^{3} \\ = & G(\bar{\varphi}(x, y), z) \end{aligned}
$$

$$
\begin{aligned} \bar{\varphi}(x, y)= & \left(a(x, y)-\frac{1}{3} b(x, y) c(x, y)+\frac{2}{27} c(x, y)^{3}\right. \\ & \left.b(x, y)-\frac{1}{3} c(x, y)^{2}\right) . \end{aligned}
$$

$$
It is not hard to check that the Jacobian determinant of \( \bar{\varphi} \) at \( 0 \in \mathbb{R}^{2} \) is equal to
$$

\left.\frac{\partial(a, b)}{\partial(x, y)}\right|_{0}, so \(\bar{\varphi}\) is a local diffeomorphism near \(0 \in \mathbb{R}^{2}\). Let \(\varphi\) be its inverse, then, putting \Phi(x, y, z)=\left(\varphi(x, y), z-\frac{1}{3} c(\varphi(x, y))\right.

$$
F \circ \Phi(x, y, z)=G(x, y, z)
$$

In other words, the admissible transformation Φ brings F into the normal form G. In particular, it maps the surface T = G-1 (0) and its contour generator onto S = F-1 (0), and ϕ maps the apparent contour of T onto the apparent contour of S.

## 5 Deriving local models

In this section, we derive local models of an implicit surface near fold and cusp points of contour generators. The local model for the fold point is as stated in Section 2, the one for the cusp point is slightly weaker in the sense that it includes terms of higher order. To derive these models, we use only elementary means, like the Implicit Function Theorem and Taylor expansion up to finite order. Although these tools are strong enough to derive the essential qualitative features of the contour generator and apparent contour at a fold or a cusp point, they are not strong enough to obtain the simple polynomial form for the cusp as stated earlier. Although the cubic model for the cusp (See Figure 2b) can be obtained by elementary means, the derivation is quite involved, cf. [22]. Even worse, the polynomial models of the contour generator of evolving surfaces (See Figures 3, 4, and 5) can only be obtained using sophisticated methods from Singularity Theory. Therefore, our more modest goal will be to obtain a local model only for the lower order part of the implicit function, which is sufficient for our purposes. See Proposition 5.2 for a more precise statement.

Local model at a fold point Proposition 5.1. Let \(p \in S\) be a regular point of the contour generator of \(S\), and let its image under parallel projection along \(v\) be a regular point of the apparent contour of \(S\). Then there is an admissible transformation, bringing \(S\) into the normal form \(x \pm z^{2}=0\) (See also Figure 2a).

$$
F_{(x, y)}(z)=F(x, y, z)
$$

Proof. Let \(p=0 \in \mathbb{R}^{3}\) be a regular point of the contour generator of \(S=F^{-1}(0)\), and let its projection \((0,0)\) be a regular point of the apparent contour. Then \(F(0)=F_{z}(0)=0\), and \(F_{z_{z}}(0) \neq 0\). Consider \(F\) as a 2-parameter family of real-valued univariate functions depending on the parameters \((x, y)\), i.e., Then \(F(0,0)\) has a non-degenerate singularity at 0 ∈ R, and hence the function \(F(x,y)\) has a nondegenerate singularity z = ζ (x, y), depending smoothly on the parameters (x, y), such that ζ (0, 0) = 0. According to the Morse Lemma with parameters, cf. Appendix B, there is a local diffeomorphism (x, y, z) ↦→ (x, y, \(Z(x,y,z)\)) on a neighborhood of 0 ∈ \(R_{3}\), such that

$$
F(x, y, Z(x, y, z))=\alpha(x, y) \pm z^{2}
$$

In fact, \(\xi(x, y)\) is the solution of the equation \(\alpha(\xi, y)-x=0\), with \(\xi(0,0)=0\). The existence and where the local diffeomorphism \(\Phi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{3}\) is defined by

$$
\Phi(x, y, z)=(\xi(x, y), y, Z(\xi(x, y), y, z)) .
$$

Now \(\Phi\) is an admissible transformation, so it maps the surface \(T\), defined by \(x \pm z^{2}=0\) and its

$$
\alpha(\varphi(x, y))=x .
$$

Local model at a cusp point Proposition 5.2. Let \(p \in S\) be a point of the contour generator of \(S\), satisfying conditions (10) and (11). Then \(p\) projects onto a cusp point of the apparent contour of \(S\) under parallel projection along \(v\). More precisely, there is an admissible transformation, defined on a neighborhood of \(p\), transforming \(S\) into a local model of the form

$$
G(x, y, z)=x+y z+z^{3}+z^{4} R(x, y, z)=0
$$

where R is a smooth function (See also Figure 2b).

Before giving the proof, we observe that this result involves the existence of a map \(h: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), mapping the apparent contour of \(T=G^{-1}(0)\) onto the apparent contour of \(S=F^{-1}(0)\). The

$$
\begin{align*} G(x, y, z) & =x+y z+z^{3}+z^{4} R(x, y, z) \\ G_{z}(x, y, z) & =y+3 z^{2}+z^{3}\left(4 R(x, y, z)+z R_{z}(x, y, z)\right) \tag{22} \end{align*}
$$

Using the Implicit Function Theorem, it is easy to see that we can solve \(x\) and \(y\) from (22), yielding:

$$
\begin{align*} & x(z)=2 z^{3}+O\left(z^{4}\right) \tag{23}\\ & y(z)=-3 z^{2}+O\left(z^{3}\right) \end{align*}
$$

Therefore, the apparent contour of \(S\) has a cusp at \((0,0)\).

Proof. We follow the same strategy as in the example of the truncated cusp in Section 4 by trans forming the quadratic term of \(F\) in \(z\) away. For general (not necessarily polynomial) functions \(F\) the Tschirnhausen transformation is obtained as follows. Since \(F_{z z_{z}}(p) \neq 0\), the Implicit Function Theorem guarantees that

$$
\begin{equation*} F_{z z}(x, y, z)=0 \tag{24} \end{equation*}
$$

has a solution \(z=z(x, y)\), locally near \((0,0)\), with \(z(0,0)=0\). In this situation, Taylor expansion yields:

$$
\begin{equation*} F(x, y, z+z(x, y))=C(x, y)\left(U(x, y)+V(x, y) z+z^{3}+z^{4} R_{4}(x, y, z)\right) \tag{25} \end{equation*}
$$

where \(R_{4}\) is a smooth function, and

$$
\begin{align*} C(x, y) & =\frac{1}{6} F_{z z z}(x, y, z(x, y)) \\ U(x, y) & =F(x, y, z(x, y)) / C(x, y) \tag{26}\\ V(x, y) & =F_{z}(x, y, z(x, y)) / C(x, y) \end{align*}
$$

Note that \(C(0,0) \neq 0\). Furthermore, \(U(0,0)=V(0,0)=0\). Note that there is no quadratic term in (25), because \(F_{z_{z}}(x, y, z(x, y))=0\). The right hand side of (25) is in fact the form of \(F\) after the parameter-dependent change of coordinates \((x, y, z) \mapsto(x, y, z+z(x, y))\). We try to polish (25) further by applying additional admissible transformations of the parameters \((x, y)\) and the variable \(z\). To this end, observe that

$$
\left.\frac{\partial(U, V)}{\partial(x, y)}\right|_{(0,0)}=\left.\frac{6}{F_{z z z}^{0}} \frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{(0,0)} \neq 0
$$

Therefore, there is an invertible smooth local change of \(x, y\)-coordinates \(\varphi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) such that

$$
\begin{equation*} U \circ \varphi(x, y)=x, \quad \text { and } \quad V \circ \varphi(x, y)=y . \tag{27} \end{equation*}
$$

with \(R(x, y, z)=R_{4}(\varphi(x, y), z)\). In other words: \(G\) is a local model of \(F\).

## 6 Time dependent contours

If we allow the direction of projection to change over time, or, equivalently, fix the direction of projection and allow the surface to depend on time, the implicit function, defining the surface, depends on four variables \((x, y, z, t)\), where \(t\) corresponds to time. In this situation, we expect one of the conditions (10) and (11) to be violated at isolated values of \((x, y, z, t)\). See also the description of evolving contours in Section 2. In this section, we derive approximate local models for these degenerate situations, cf Figures 4, 3 and 5. As said before, we consider a smooth function \(F: \mathbb{R}^{3} \times \mathbb{R} \rightarrow \mathbb{R}\), which defines a time-dependent

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-6-p014.png)

*Figure 6: A beak-to-beak bifurcation. Top row: a sequence of views of a smooth surface. Middle row: the corresponding apparent contours. Bottom row: blow up of the apparent contour near the bifurcation event.*

$$
F(\varphi(x, y), z+z(\varphi(x, y)))=C(x, y) G(x, y, z),
$$

$$
G(x, y, z)=x+y z+z^{3}+z^{4} R(x, y, z),
$$

Lips and beak-to-beak bifurcations The occurrence of lips and beak-to-beak bifurcations are associated with a violation of condition (10).

Proposition 6.1. Let \(p\) be a non-degenerate singular point of the contour generator for \(t=t_{0}\), i.e.,

$$
\begin{equation*} F\left(p, t_{0}\right)=F_{z}\left(p, t_{0}\right)=F_{z z}\left(p, t_{0}\right)=\left.\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{\left(p, t_{0}\right)}=0, \text { and } F_{z z z}\left(p, t_{0}\right) \neq 0 \tag{28} \end{equation*}
$$

$$
\left(\begin{array}{ccc} F_{x}^{0} & F_{y}^{0} & F_{t}^{0} \tag{29}\\ F_{x z}^{0} & F_{y z}^{0} & F_{t z}^{0} \end{array}\right) \quad \text { has rank two. }
$$

Then the surface has a local model at \(\left(p, t_{0}\right)\) of the form

$$
G(x, y, z, t)=x+\left(\sigma y^{2}+\alpha(x, t)\right) z+z^{3}+z^{4} R(x, y, z, t)
$$

Remark Before giving the proof, we observe that contour generator is determined by the equations \(G=G_{z}=0\), i.e.,

$$
\begin{array}{r} x+\left(\sigma y^{2}+\alpha(x, y)\right) z+z^{3}=O\left(z^{4}\right) \\ \left(\sigma y^{2}+\alpha(x, y)\right) z+3 z^{2}=O\left(z^{3}\right) \end{array}
$$

Solving this system for \(x\) and \(y\) yields

$$
\begin{aligned} x & =2 z^{3}+O\left(z^{4}\right) \\ \sigma y^{2}+3 z^{2} & =-\alpha(x, t)+O\left(z^{3}\right) \end{aligned}
$$

Since α (0, 0) = 0, it is easy to see that the singularity of the contour generator for t = 0 is of saddle type if σ = -1, and corresponds to an extremum if σ = +1. The former case corresponds to a beak-to-beak bifurcation, the lattor to a lips bifurcation. We have a scenario like depicted in Figure 3 and 4, respectively, where it depends on the sign of ∂α ∂t (0, 0) whether we have to read the Figure from left-to-right or from right-to-left, as t passes zero from negative to positive values.

Proof. For ease of notation we assume that \(p=(0,0,0)\) and \(t_{0}=0\). Our approach is as in the

$$
\begin{equation*} F_{z z}(x, y, z, t)=0 \tag{30} \end{equation*}
$$

cf (24). Since \(F_{z z_{z}}(0,0,0,0) \neq 0\), there is a locally unique solution \(z=\zeta(x, y, t)\) of (30), with

$$
F(x, y, z+z(x, y), t)=C(x, y, t)\left(U(x, y, t)+V(x, y, t) z+z^{3}+z^{4} R_{4}(x, y, z, t)\right)
$$

$$
\Sigma(p) \neq 0
$$

where \(R_{4}\) is a smooth function, and

$$
\begin{aligned} C(x, y, t) & =\frac{1}{6} F_{z z z}(x, y, z(x, y, t)) \\ U(x, y, t) & =F(x, y, z(x, y, t), t) / C(x, y, t) \\ V(x, y, t) & =F_{z}(x, y, z(x, y, t), t) / C(x, y, t) \end{aligned}
$$

Also in this case \(C(0,0,0) \neq 0\), and \(U(0,0,0)=V(0,0,0)=0\). To avoid superscripts, we introduce the functions \(u, v: \mathbb{R}^{2} \rightarrow \mathbb{R}\), defined by \(u(x, y)=U(x, y, 0)\), and \(v(x, y)=V(x, y, 0)\). In this case we have

$$
\begin{equation*} \left.\frac{\partial(U, V)}{\partial(x, y)}\right|_{(0,0)}=\left.\frac{6}{F_{z z z}^{0}} \frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{(0,0)}=0, \tag{31} \end{equation*}
$$

so, unlike the situation at a cusp point, we don't have the normal form \((x, y)\) for the pair \((u, v)\). Yet, we can obtain a normal form as stated in the Proposition. To this end introduce the map \(\Psi: \mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2}\), defined by

$$
\begin{equation*} \Psi(x, y, t)=(U(x, y, t), V(x, y, t)) . \tag{32} \end{equation*}
$$

$$
It follows from (32) that the Jacobian determinant \( J=U_{x} V_{y}-U_{y} V_{x} \) of \( \Psi \) satisfies
$$

$$
\begin{equation*} J(0,0,0)=0 \tag{33} \end{equation*}
$$

the derivative of the map \(\psi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), defined by \(\psi(x, y)=(u(x, y), v(x, y))\) at \((0,0) \in \mathbb{R}^{2}\) has rank one.

This observation brings us to the context of Singularity Theory, in particular the theory of normal forms of generic maps from the plane to the plane. Whitney's paper [22] presents a local normal form for the two types of generic singularities of this type of maps, viz. the fold and the cusp. As said before, although, or perhaps, because, this paper uses elementary tools, the technical details are quite involved. We refer the reader to Appendix C for a rather self-contained derivation of the Whitney fold, fine-tuned to our current context.

$$
U \circ \varphi(x, y, t)=x, \quad \text { and } \quad V \circ \varphi(x, y, t)=\sigma y^{2}+\alpha(x, t) .
$$

Since \(\nabla u(0,0) \neq(0,0)\), cf (34), Proposition C.3, or rather its parametrized version presented in Section C.3, guarantees the existence of a change of parameters \(\varphi(x, y, t)\) of the form \(\varphi(x, y, t)=(\cdot, \cdot, t)\), such that

$$
Here \( \alpha \) is a smooth function with \( \alpha(0,0)=0 \), and
$$

$$
\sigma=\operatorname{sign}\left(\left\langle\nabla u(0,0), \nabla j(0,0)^{\perp}\right\rangle\right)=\operatorname{sign}\left(-u_{x}^{0} j_{y}^{0}+u_{y}^{0} j_{x}^{0}\right)
$$

A straigthforward, but tedious-and hence preferably automated-computation shows that

$$
-u_{x}^{0} j_{y}^{0}+u_{y}^{0} j_{x}^{0}=\Sigma(p)
$$

Therefore,

$$
F(\varphi(x, y, t), z+z(\varphi(x, y, t)))=C(x, y, t) G(x, y, z, t)
$$

$$
G(x, y, z)=x+\left(\sigma y^{2}+\alpha(x, t)\right) z+z^{3}+z^{4} R(x, y, z)
$$

with \(R(x, y, z)=R_{4}(\varphi(x, y, t), z)\). In other words: \(G\) is a local model of \(F\).

$$
\begin{equation*} \left(u_{x}^{0}, u_{y}^{0}\right)=\frac{6}{F_{z z z}^{0}}\left(F_{x}^{0}, F_{y}^{0}\right) \neq(0,0), \tag{34} \end{equation*}
$$

![Figure 7](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-7-p017.png)

*Figure 7: A swallowtail bifurcation. Top row: a sequence of views of a smooth surface. Middle row: the corresponding apparent contours. Bottom row: blow up of the apparent contour near the bifurcation event.*

The swallowtail bifurcation In this section we study the discontinuous change of the apparent contour associated with a violation of (11), whereas (10) still holds. In this case the contour generator is regular.

Proposition 6.2. Let \(F\) : \(\mathbb{R}^{3} \times \mathbb{R} \rightarrow \mathbb{R}\) be such that at \(\left(p, t_{0}\right) \in \mathbb{R}^{3} \times \mathbb{R}\) the following conditions are satisfied:

$$
\begin{equation*} F\left(p, t_{0}\right)=F_{z}\left(p, t_{0}\right)=F_{z z}\left(p, t_{0}\right)=F_{z z z}\left(p, t_{0}\right)=0 . \tag{35} \end{equation*}
$$

If at ( \(p, t_{0}\) ) the generic conditions:

$$
\begin{equation*} F_{z z z z}\left(p, t_{0}\right) \neq 0,\left.\frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{\left(p, t_{0}\right)} \neq 0, \text { and }\left.\frac{\partial\left(F, F_{z}, F_{z z}\right)}{\partial(x, y, t)}\right|_{\left(p, t_{0}\right)} \neq 0 . \tag{36} \end{equation*}
$$

are satisfied, then \(F\) has a local model at \(\left(p, t_{0}\right)\) of the form

$$
\begin{equation*} G(x, y, z, t)=x+y z+w(x, y, t) z^{2}+z^{4}+z^{5} R(x, y, z, t), \tag{37} \end{equation*}
$$

$$
with \( w(0,0, t)=\alpha t+O\left(t^{2}\right) \), where
$$

$$
\begin{equation*} \alpha=\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F, F_{z}, F_{z z}\right)}{\partial(x, y, t)}\right|_{(0,0,0)} \neq 0 . \tag{38} \end{equation*}
$$

In particular, there is a time-dependent change of coordinates \(h^{t}: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), mapping the apparent contour of \(S^{t}\) onto the apparent contour of \(\left(G^{t}\right)^{-1}(0)\), which has a parametrization of the form \(z \mapsto(x(z, t), y(z, t))\), where:

$$
\begin{aligned} & x(z, t)=w^{0}(t) z^{2}-2 w^{0}(t) w_{x}^{0}(t) z^{3}-\left(3+w^{0}(t) W(t)\right) z^{4}+X(z, t) z^{5} \\ & y(z, t)=-2 w^{0}(t) z+4 w^{0}(t) w_{y}^{0}(t) z^{2}-\left(2+w^{0}(t) W(t)\right) z^{3}+Y(z, t) z^{4} \end{aligned}
$$

$$
\begin{aligned} & w^{0}(t)=w(0,0, t)=\alpha t+O\left(t^{2}\right) \\ & w_{x}^{0}(0)=-\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F_{z}, F_{z z}\right)}{\partial(x, y)}\right|_{0} \\ & w_{y}^{0}(0)=\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F, F_{z z}\right)}{\partial(x, y)}\right|_{0} \\ & W(0)=w_{x}^{0}+4\left(w_{y}^{0}\right)^{2} \end{aligned}
$$

Remark The parametrization of the apparent contour is of the form

$$
\begin{aligned} & x(z, t)=\left(\alpha t+O\left(t^{2}\right)\right) z^{2}+O(t) z^{2}-(3+O(t)) z^{4}+O\left(z^{5}\right) \\ & y(z, t)=\left(-2 \alpha t+O\left(t^{2}\right)\right) z+O(t) z^{2}-\left(2+O\left(t^{2}\right)\right) z^{3}+O\left(z^{4}\right) \end{aligned}
$$

For \(\alpha>0\), the evolution of the apparent contour is as the one depicted in Figure 5, whereas for \(\alpha<0\) the evolution corresponds to reading the latter figure from right to left.

Proof. As before, we assume that \(p=(0,0,0)\) and \(t_{0}=0\). As in the Tschirnhausen transformation,

$$
\begin{equation*} F_{z z z}(x, y, z, t)=0 \tag{39} \end{equation*}
$$

Since \(F_{z z z_{z}}(0,0,0,0) \neq 0\), there is a locally unique solution \(z=\zeta(x, y, t)\) of (39), with \(\zeta(0,0,0)=0\).

$$
F(x, y, z+\zeta(x, y, t), t)=C\left(U+V z+W z^{2}+z^{4}+z^{5} R(x, y, z, t)\right)
$$

where R is a smooth function, and

$$
\begin{aligned} C & =C(x, y, t)=\frac{1}{4!} F_{z z z z}(x, y, \zeta(x, y, t), t) \\ U & =U(x, y, t)=F(x, y, \zeta(x, y, t), t) / C(x, y, t) \\ V & =V(x, y, t)=F_{z}(x, y, \zeta(x, y, t), t) / C(x, y, t) \\ W & =W(x, y, t)=\frac{1}{2} F_{z z}(x, y, \zeta(x, y, t), t) / C(x, y, t) \end{aligned}
$$

Since, according to

$$
\left.\frac{\partial(U, V)}{\partial(x, y)}\right|_{(0,0,0)}=\left.\frac{4!}{F_{z z z z}^{0}} \frac{\partial\left(F, F_{z}\right)}{\partial(x, y)}\right|_{(0,0,0,0)}=\frac{4!\Delta_{0}}{F_{z z z z}^{0}} \neq 0
$$

we see that the map \(\psi: \mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2} \times \mathbb{R}\), defined by

$$
\psi(x, y, t)=(U(x, y, t), V(x, y, t), t),
$$

is a local diffeomorphism, which has an inverse of the form

$$
\varphi(x, y, t)=(\xi(x, y, t), \eta(x, y, t), t),
$$

we see that \(\Phi\) is an admissible transformation bringing \(F\) into the normal form \(G=F \circ \Phi\), which is of the form

$$
G(x, y, z, t)=x+y z+w(x, y, t) z^{2}+z^{4}+O\left(|z|^{5}\right),
$$

$$
w(x, y, t)=W(\xi(x, y, t), \eta(x, y, t), t)=F_{z z}(\xi(x, y, t), \eta(x, y, t), t) .
$$

$$
\begin{equation*} U \circ \varphi(x, y, t)=x \text { and } V \circ \varphi(x, y, t)=y . \tag{40} \end{equation*}
$$

$$
\Phi(x, y, z, t)=(\xi(x, y, t), \eta(x, y, t), z, t),
$$

Therefore \(w(0,0,0)=0\). Furthermore,

$$
w_{t}(0,0,0)=\frac{4!}{F_{z z z z}^{0}}\left(F_{x z z}^{0} \xi_{t}^{0}+F_{y z z}^{0} \eta_{t}^{0}+F_{t z z}^{0}\right)
$$

$$
\left(\begin{array}{cc} F_{x}^{0} & F_{y}^{0} \\ F_{x z}^{0} & F_{y z}^{0} \end{array}\right)\binom{\xi_{t}^{0}}{\eta_{t}^{0}}=\binom{-F_{t}^{0}}{-F_{z t}^{0}}
$$

Using Cramer's rule, we obtain

$$
\xi_{t}^{0}=-\frac{1}{\Delta_{0}}\left|\begin{array}{cc} F_{t}^{0} & F_{y}^{0} \\ F_{z t}^{0} & F_{y z}^{0} \end{array}\right|, \quad \text { and } \quad \eta_{t}^{0}=-\frac{1}{\Delta_{0}}\left|\begin{array}{cc} F_{x}^{0} & F_{t}^{0} \\ F_{x z}^{0} & F_{z t}^{0} \end{array}\right| .
$$

$$
\begin{align*} w_{t}^{0} & =-\frac{4!}{\Delta_{0} F_{z z z z}^{0}}\left(F_{x z z}^{0}\left|\begin{array}{cc} F_{t}^{0} & F_{y}^{0} \\ F_{z t}^{0} & F_{y z}^{0} \end{array}\right|+F_{y z z}^{0}\left|\begin{array}{cc} F_{x}^{0} & F_{t}^{0} \\ F_{x z}^{0} & F_{z t}^{0} \end{array}\right|-F_{t z z}^{0}\left|\begin{array}{cc} F_{x}^{0} & F_{y}^{0} \\ F_{x z}^{0} & F_{y z}^{0} \end{array}\right|\right) \\ & =\frac{4!}{\Delta_{0} F_{z z z z}^{0}}\left|\begin{array}{ccc} F_{x}^{0} & F_{y}^{0} & F_{t}^{0} \\ F_{x z}^{0} & F_{y z}^{0} & F_{z t}^{0} \\ F_{x z z}^{0} & F_{y z z}^{0} & F_{z z t}^{0} \end{array}\right| \\ & =\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F, F_{z}, F_{z z}\right)}{\partial(x, y, z)}\right|_{0} . \tag{41} \end{align*}
$$

From (40) we derive

$$
\begin{aligned} & U_{x}^{0} \xi_{t}^{0}+U_{y}^{0} \eta_{t}^{0}+U_{t}^{0}=0 \\ & V_{x}^{0} \xi_{t}^{0}+V_{y}^{0} \eta_{t}^{0}+V_{t}^{0}=0 \end{aligned}
$$

By a similar computation we obtain:

$$
\begin{equation*} w_{x}^{0}=-\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F_{z}, F_{z z}\right)}{\partial(x, y, z)}\right|_{0} . \tag{42} \end{equation*}
$$

$$
\begin{equation*} w_{y}^{0}=\left.\frac{4!}{\Delta_{0} F_{z z z z}^{0}} \frac{\partial\left(F, F_{z z}\right)}{\partial(x, y, z)}\right|_{0} . \tag{43} \end{equation*}
$$

Finally, we can solve \(x\) and \(y\) as functions of ( \(z, t\) ) from the set of equations \(G(x, y, z, t)=G_{z}(x, y, z, t)=0\), with \(G\) as in (37). A straightforward, preferably automated, computation yields:

$$
\begin{aligned} x(0, t)= & 0 \\ y(0, t)= & 0 \\ x_{z}(0, t)= & 0 \\ y_{z}(0, t)= & -2 w(0,0, t) \\ x_{z z}(0, t)= & 2 w(0,0, t) \\ y_{z z}(0, t)= & 8 w(0,0, t) w_{y}(0,0, t) \\ x_{z z z}(0, t)= & -12 w(0,0, t) w_{y}(0,0, t) \\ y_{z z z}(0, t)= & -12\left(2+4 w(0,0, t) w_{y}(0,0, t)^{2}+2 w(0,0, t)^{2} w_{y y}(0,0, t)+\right. \\ & \left.w(0,0, t) w_{x}(0,0, t)\right) \\ x_{z z z z}(0, t)= & 24\left(3+4 w(0,0, t) w_{y}(0,0, t)^{2}+2 w(0,0, t)^{2} w_{y y}(0,0, t)+\right. \\ & \left.w(0,0, t) w_{x}(0,0, t)\right) \end{aligned}
$$

The low order Taylor expansions of \(x(z, t)\) and \(y(z, t)\), as stated in Proposition 6.2 are obtained by combining these expressions with the identities for \(w_{t}^{0}, w_{x}^{0}\), and \(w_{y}^{0}\) in (41), (42), and (43), respectively.

## 7 Interval analysis

One way to prevent rounding errors due to finite precision numbers is to use interval arithmetic. Instead of numbers, intervals containing the exact solution are computed. An inclusion function \(\square f\) for a function \(f: \mathbb{R}^{m} \rightarrow \mathbb{R}^{n}\) computes for each \(m\)-dimensional interval \(I\) (i.e. an \(m\)-box) an \(n\)-dimensional interval \(\square f(I)\) such that

$$
x \in I \Rightarrow f(x) \in \square f(I)
$$

An inclusion function is convergent if

$$
\operatorname{width}(I) \rightarrow 0 \Rightarrow \quad \text { width }(\square f(I)) \rightarrow 0
$$

where the width of an interval is the largest width of I. For example if \(f: \mathbb{R} \rightarrow \mathbb{R}\) is the square function \(f(x)=x^{2}\), then a convergent inclusion function is

$$
\square f([a, b])= \begin{cases}{\left[\min \left(a^{2}, b^{2}\right), \max \left(a^{2}, b^{2}\right)\right],} & a \cdot b \geq 0 \\ {\left[0, \max \left(a^{2}, b^{2}\right)\right],} & a \cdot b<0\end{cases}
$$

Inclusion functions exist for the basic operators and functions. To compute an inclusion function it is often sufficient to replace the standard number type (e.g. double) by an interval type.

We assume there are convergent inclusion functions for our implicit function \(F\) and its deriva tives, and will denote them by \(F\) (and similiar for the derivatives). From the context it will be clear when the inclusion function is meant.

Interval arithmetic can be implemented using demand-driven precision. For the interval bounds, ordinary doubles (with conservative rounding) can be used for fast computation. In the rare case that the interval becomes too small for the precision of a double, a multi-precision number type can be used.

Interval Newton Method For precision small intervals around the required value are used. Another use of interval arithmetic is to compute function values over larger intervals. If for an implicit surface \(F=0\) and a box \(I\) we have \(0 \notin \square F(I)\), we can be certain that \(I\) contains no part of the surface. This observation can be extended to the Interval Newton Method, that finds all roots of a function \(f: \mathbb{R}^{n} \rightarrow \mathbb{R}^{n}\) in a box \(I\). The first part of the algorithm recursively subdivides the box, discarding parts of space containing no roots. If the boxes are small enough a Newton method refines the solutions and guarantees that all roots are found. Solving

$$
f(x)+J(I)(z-x)=0
$$

where \(x\) is the centre of \(I, J\) is the Jacobian matrix of \(f\) and \(J(I)\) is the interval matrix of \(J\) over the interval \(I\), results in an interval \(Y\) containing all roots \(z\) of \(f\). This interval can be used to refine \(I\). Also, if \(Y \subset I\) there is a unique root of \(f\) in \(I\). See [13] for the mathematical details. A more practical introduction can be found in [20] or [21].

## 8 Tracing the contour generator

Our goal is to approximate the contour generator by a piecewise linear curve. This initial approximation can then be maintained under some time-dependent view. To this end the singularities of the contour generator for an evolving view or surface can be precomputed using interval analysis. Since the topology doesn't change between these singularities, the initial contour generator can be updated continuously, until we reach a time where a singularity arises. The local model at this singularity indicates how the topology has to be updated. See Section 4.

Note that for a singularity of the contour generator of a time-dependent surface, we have

$$
\left(\begin{array}{c} F(x, y, z, t) \\ F_{z}(x, y, z, t) \\ F_{z z}(x, y, z, t) \\ \Delta(x, y, z, t) \end{array}\right)=0
$$

Using the Interval Newton Method, we can find all \(t\) for which a singularity occurs.

For the initial contour generator we can assume there are no singularities. The construction consists of two steps.

Firstly, for each component we have to find an initial point to start the tracing process. Interval analysis enables us to find points on all components of the contour generator. See below for details. These (regular) points serve as starting points for the tracing process.

Secondly, we trace the component by stepping along the contour generator. For each starting point we trace the component, by moving from a point \(p^{i}\) to the next point \(p^{i+1}\). We take a small step in the direction of the tangent to the contour generator at \(p^{i}\). Then, we move the resulting point back to the contour generator, giving us \(p^{i+1}\). An interval test guarantees that we stay on the same component, without skipping a part. If the test fails, we decrease the step size and try again, until the interval test succeeds. If we reach the initial point \(p^{0}\), the component is fully traced. See Figure 11 for some results of the algorithm.

Finding initial points Atangent vector to the contour generator at p can be found by computing

$$
w(p)=\nabla F(p) \wedge \nabla F_{z}(p)=\left(\begin{array}{c} F_{y} F_{z z} \\ -F_{x} F_{z z} \\ F_{x} F_{y z}-F_{y} F_{x z} \end{array}\right)
$$

Since the components of the contour generator are bounded, closed curves, there are at least two points on each component where the \(x\)-component of \(w(p)\) disappears, i.e where \(F_{y} F_{z_{z}}=0\). Let \(R, S: \mathbb{R}^{3} \rightarrow \mathbb{R}^{3}\) be the functions

$$
R(p)=\left(\begin{array}{c} F(p) \\ F_{z}(p) \\ F_{y}(p) \end{array}\right) \text { and } S(p)=\left(\begin{array}{c} F(p) \\ F_{z}(p) \\ F_{z z}(p) \end{array}\right)
$$

The Interval Newton Method can find all roots of \(R\) and \(S\). These roots are used to create a list of (regular) initial points.

Tracing step Let \(N(x)\) be the normalized vector field

$$
N(x)=\frac{\nabla F(x) \wedge \nabla F_{z}(x)}{\left\|\nabla F(x) \wedge \nabla F_{z}(x)\right\|}
$$

For \(x\) on the contour generator, \(N(x)\) is a tangent vector at \(x\). From \(p^{i}\) we first move to \(q^{0}=p^{i}+\delta N\left(p^{i}\right)\), where \(\delta\) is the step size. To move back to the contour generator, we alternately move

$$
\begin{cases}q^{i+1}=q^{i}-\frac{F\left(q^{i}\right) \nabla F\left(q^{i}\right)}{\left\|\nabla F\left(q^{i}\right)\right\|^{2}} & \text { towards } F \\ q^{i+1}=q^{i}-\frac{F_{z}\left(q^{i}\right) \nabla F_{z}\left(q^{i}\right)}{\left\|\nabla F_{z}\left(q^{i}\right)\right\|^{2}} & \text { towards } F_{z}\end{cases}
$$

until \(\left\|q^{i+2}-q^{i}\right\|\) is sufficiently small. The resulting point is the next point on the contour generator, \(p^{i+1}\). For this new point we perform the interval test (explained below) to determine whether \(p^{i} p^{i+1}\) is a good approximation of the contour generator. If not, we decrease \(\delta\) (e.g. by setting it to \(\delta / 2\) ), and repeat the tracing step from \(p^{i}\).

Interval test For a fixed step size, there is always a possibility of accidentally jumping to another component of the contour generator, or of skipping a part (figure 8). To assure that \(p^{i} p^{i+1}\) is a good approximation for the contour generator, first we construct a sphere \(S\) with centre \(p^{i}\), that contains \(p^{i+1}\). Then we take the bounding box \(B\) of \(S\) :

$$
B=\left[p_{x}^{i}-\Delta, p_{x}^{i}+\Delta\right] \times\left[p_{y}^{i}-\Delta, p_{y}^{i}+\Delta\right] \times\left[p_{z}^{i}-\Delta, p_{z}^{i}+\Delta\right]
$$

where \(\Delta=\left\|p^{i+1}-p^{i}\right\|\). Over this box we compute the interval

$$
I=\left\langle N\left(p^{i}\right), N(B)\right\rangle
$$

The interval condition \(I>\frac{1}{2} \sqrt{2}\) implies that the angle between \(N\left(p^{i}\right)\) and \(N(x)\) is at most \(\frac{\pi}{4}\). The contour generator lies in a cone \(C\) around \(N(x)\) (fig. 10) with top angle \(\frac{\pi}{2}\), for if it leaves the cone at point \(a\), then \(\left\langle N\left(p^{i}\right), N(a)\right\rangle\) would be smaller than \(\frac{1}{2} \sqrt{2}\). It can only leave the sphere in \(S \cap C\). In this part of the sphere the contour generator can't re-enter \(S\), because that would require an entry point \(b\) where \(\left\langle N\left(p^{i}\right), N(b)\right\rangle<\frac{1}{2} \sqrt{2}\). Therefore, there is only a single connected component of the contour generator within sphere \(S\).

![Figure 8](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-8-p023.png)

*Figure 8: Left: N (p i) is a tangent to the intersection of F = 0 and F z = 0. Right: a ﬁxed step size can miss part of the contour generator. fixed step size can miss part of the contour generator.*

Lemma 8.1. If \(I>\frac{1}{2} \sqrt{2}\), (i.e. \(\forall i \in I: i>\frac{1}{2} \sqrt{2}\) ), then the part of the contour generator within \(S\) consists of a single component (fig. 9).

![Figure 9](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-9-p023.png)

*Figure 9: The sphere containing the line segment, and its bounding box.*

Proof. We define \(G(x)=\left\langle x-p^{i}, N\left(p^{i}\right)\right\rangle\). The level sets of \(G\) are planes perpendicular to \(N\left(p^{i}\right)\). Let \(f: \mathbb{R}^{3} \rightarrow \mathbb{R}^{3}\) be the function

$$
f(x)=\left(\begin{array}{c} F(x) \\ F_{z}(x) \\ G(x) \end{array}\right) .
$$

Suppose there are two points \(x\) and \(y\) of the contour generator in \(B\), lying in a plane perpendicular to \(N\left(p^{i}\right)\), i.e. \(f(x)=f(y)=(0,0, \theta)\) for some \(\theta\). Then there are points \(s\) and \(t\) on \(x_{y}\) where

$$
\left(\begin{array}{c} \nabla F(s) \\ \nabla F_{z}(t) \\ N\left(p^{i}\right) \end{array}\right)(y-x)=\left(\begin{array}{l} 0 \\ 0 \\ 0 \end{array}\right)
$$

Since \(s, t \in B\) this contradicts the interval test. Therefore, within box \(B\) each plane perpendicular to \(N\left(p^{i}\right)\) contains at most one point of the contour generator.

![Figure 10](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-10-p024.png)

*Figure 10: The contour generator lies within a cone.*

If the interval test succeeds, we can use the same sphere \(S\) to remove redundant points from the initial point list. If there are point in the list that lie within \(S\), they must be part of the component we are tracing, so they can be discarded. To test whether the component is fully traced, we test if the initial point \(p^{0}\) is contained in \(S\). If it is, testing

$$
\left\langle p^{i+1}-p^{i}, p^{0}-p^{i}\right\rangle>0
$$

Since \(p^{i}\) is in general close to, but not on the contour generator, in practice we take a slightly larger bound. Also, \(\Delta\) should be slightly larger than \(\left\|p^{i+1}-p^{i}\right\|\), to prevent \(p^{i+1}\) from being too close to other parts of the contour generator outside \(S\).

![Figure 11](/Users/evanthayer/Projects/paperx/docs/2006_computing_contour_generators_of_evolving_implicit_surfaces/figures/figure-11-p024.png)

*Figure 11: Contour generator of a sphere and of 8 metaballs (see appendix D) near the vertices of a cube. The small squares indicate the initial points. The dots on the sphere show the dynamic step size. Note that the metaballs are close to a singularity under motion of the viewpoint. The sizes of the eight components range from 439 to 879 segments.*

```text
Evolving surfaces For a time-dependent surface \( F(x, y, z, t)=0 \) there is no need to compute the initial points on the contour generator for each \( t \). Instead, we trace the initial points as time evolves. Recall that the initial points are zeroes of the functions
```

$$
R(x, y, z, t)=\left(\begin{array}{c} F(x, y, z, t) \\ F_{z}(x, y, z, t) \\ F_{y}(x, y, z, t) \end{array}\right) \text { and } S(x, y, z, t)=\left(\begin{array}{c} F(x, y, z, t) \\ F_{z}(x, y, z, t) \\ F_{z z}(x, y, z, t) \end{array}\right)
$$

The tangent vector to the curve is perpendicular to the gradients of the three components of \(R\) and of \(S\). As time evolves, generically initial points are created and destroyed in pairs. This happens when the tangent vector is perpendicular to the \(t\)-axis. Otherwise, according to the implicit function theorem there exists a unique solution.

For time-dependent surfaces, these are 1-dimensional curves in \(\mathbb{R}^{4}\). These curves can be traced similar to the contour generator itself, i.e. by stepping along the curve using a step size such that the interval inequality \(\left(I>\frac{1}{2} \sqrt{2}\right)\) is satisfied.

For R the tangent vector can be found using

$$
\operatorname{Ker}\left[\begin{array}{cccc} F_{x} & F_{y} & F_{z} & F_{t} \\ F_{x z} & F_{y z} & F_{z z} & F_{z t} \\ F_{x y} & F_{y y} & F_{y z} & F_{y t} \end{array}\right]
$$

A solution \(\left(t_{1}, t_{2}, t_{3}, t_{4}\right)\) in the kernel with \(\sum t_{i}=0\) can be found by adding a row \([1,1,1,1]\) to

$$
\left(\left|\begin{array}{ccc} 0 & 0 & F_{t} \\ F_{y z} & F_{z z} & F_{z t} \\ F_{y y} & F_{y z} & F_{y t} \end{array}\right|,-\left|\begin{array}{ccc} F_{x} & 0 & F_{t} \\ F_{x z} & F_{z z} & F_{z t} \\ F_{x y} & F_{y z} & F_{y t} \end{array}\right|,\left|\begin{array}{ccc} F_{x} & 0 & F_{t} \\ F_{x z} & F_{y z} & F_{z t} \\ F_{x y} & F_{y y} & F_{y t} \end{array}\right|,-\left|\begin{array}{ccc} F_{x} & 0 & 0 \\ F_{x z} & F_{y z} & F_{z z} \\ F_{x y} & F_{y y} & F_{y z} \end{array}\right|\right)
$$

∣ ∣ ∣ ∣ ∣ This tangent vector is perpendicular to the t-axis if

$$
\left(\begin{array}{c} F \\ F_{z} \\ F_{y} \\ F_{x} \end{array}\right)=0 \text { or }\left(\begin{array}{c} F \\ F_{z} \\ F_{y} \\ F_{y z}^{2}-F_{y y} F_{z z} \end{array}\right)=0
$$

The first equality has no solutions, since the surface does not contain singularities.

Similarly, for S we have:

$$
\operatorname{Ker}\left[\begin{array}{cccc} F_{x} & F_{y} & F_{z} & F_{t} \\ F_{x z} & F_{y z} & F_{z z} & F_{t z} \\ F_{x z z} & F_{y z z} & F_{z z z} & F_{t z z} \end{array}\right]
$$

For the tangent vector of S we find:

$$
\left(\left|\begin{array}{ccc} F_{y} & 0 & F_{t} \\ F_{y z} & 0 & F_{t z} \\ F_{t} & F_{t z} & F_{t z z} \end{array}\right|,-\left|\begin{array}{ccc} F_{x} & 0 & F_{t} \\ F_{x z} & 0 & F_{t z} \\ F_{x z z} & F_{z z z} & F_{t z z} \end{array}\right|,\left|\begin{array}{ccc} F_{x} & F_{y} & F_{t} \\ F_{x z} & F_{y z} & F_{t z} \\ F_{x z z} & F_{y z z} & F_{z z z} \end{array}\right|,-\left|\begin{array}{ccc} F_{x} & F_{y} & 0 \\ F_{x z} & F_{y z} & 0 \\ F_{x z z} & F_{y z z} & F_{z z z} \end{array}\right|\right)
$$

$$
\left(\begin{array}{c} F \\ F_{z} \\ F_{z z} \\ F_{z z z} \end{array}\right)=0 \text { or }\left(\begin{array}{c} F \\ F_{z} \\ F_{z z} \\ F_{x} F_{y z}-F_{y} F_{x z} \end{array}\right)=0
$$

The first equality corresponds to swallowtail bifurcations, the second equality corresponds to singularities of the contour generator.

## 9 Conclusion and future research

We presented a framework for the analysis of an implicit surface near regular and singular points of its contour generator and apparent contour, and also derived conditions for detecting changes of topology of these visibility features in generic one-parameter families of implicit surfaces.

We developed an algorithm to compute a topologically correct approximation of the initial contour generator. A dynamic step size, combined with an interval test, guarantees that no part of the contour generator is skipped.

We plan to extend this work by implementing a robust algorithm for maintaining the contour generator under time-dependent directions of projection or surfaces, in such a way that its topology is guaranteed.

## Acknowledgements

Partially supported by the IST Programme of the EU as a Shared-cost RTD (FET Open) Project under Contract No IST-2000-26473 (ECG-Effective computational Geometry for curves and Surfaces)

## A Singularities of functions on surfaces

Non-degenerate singular points Consider an implicit surface \(S=F^{-1}(0)\), where \(F: \mathbb{R}^{3} \rightarrow \mathbb{R}\) is a \(C^{2}\) function. We assume that 0 is a regular value of \(F\), so according to the Implicit Function Theorem \(S\) is a regular \(C^{2}\)-surface. Our goal is to determine conditions which guarantee that the restriction of a \(C^{2}\) function \(G: \mathbb{R}^{3} \rightarrow \mathbb{R}\) to the surface \(S\) has a non-degenerate singular point. As for notation, the gradient of a function \(F: \mathbb{R}^{3} \rightarrow \mathbb{R}\) at \(p \in \mathbb{R}\) will be denoted by \(\nabla F(p)\). Furthermore, the Hessian quadratic form of a function \(F: \mathbb{R}^{3} \rightarrow \mathbb{R}\) at \(p \in \mathbb{R}\) will be denoted by \(H_{F}(p)\). Usually, we suppress the dependence on \(p\) from our notation, and denote this quadratic form by \(H_{F}\). With respect to the standard euclidean inner product its matrix is the usual symmetric matrix whose entries are the second order partial derivatives of \(F\). We denote partial derivatives using subscripts, e.g., \(F_{x}\) denotes \(\frac{\partial F}{\partial x}, F_{x_{y}}\) denotes \(\frac{\partial^{2} F}{\partial x \partial y}\), etc.

Theorem A.1. Let \(F, G: \mathbb{R}^{3} \rightarrow \mathbb{R}\) be \(C^{2}\) functions, and let 0 be a regular value of \(F\). Let \(p\) be a point on the surface \(S=F^{-1}(0)\).

- p is a singular point of G | S iff there is a real number λ such that

$$
\begin{equation*} \nabla G(p)=\lambda \nabla F(p) \tag{44} \end{equation*}
$$

- Furthermore, the singular point p is non-degenerate iff

$$
\begin{equation*} \left(H_{G}-\lambda H_{F}\right) \mid T_{p} S \tag{45} \end{equation*}
$$

is a non-degenerate quadratic form, where λ is as in (44). Remark The scalar λ in (44) is traditionally called a Lagrange multiplier. Corollary A.2. The singularity \(p\) of \(G \mid S\) is non-degenerate iff the \(2 \times 2\)-matrix \(\Delta\), defined by (46), is non-singular:

$$
\Delta=V^{T} \cdot\left(\left(\begin{array}{ccc} G_{x x} & G_{x y} & G_{x z} \tag{46}\\ G_{x y} & G_{y y} & G_{y z} \\ G_{x z} & G_{y z} & G_{z z} \end{array}\right)-\lambda\left(\begin{array}{ccc} F_{x x} & F_{x y} & F_{x z} \\ F_{x y} & F_{y y} & F_{y z} \\ F_{x z} & F_{y z} & F_{z z} \end{array}\right)\right) \cdot V
$$

where \(\lambda\) is the Lagrange multiplier defined by (44), and \(V\) is a \(3 \times 2\)-matrix whose columns span the tangent space \(T_{p} S\). Here all first and second order derivatives are evaluated at \(p\). Furthermore, \(G \mid S\), the singular point \(p\) is a maximum or minimum if \(\operatorname{det}(\Delta)>0\), and a saddle point if \(\operatorname{det}(\Delta)<0\).

In particular, we may take \(V=X, V=Y\), or \(V=Z\) if \(F_{x}(p) \neq 0, F_{y}(p) \neq 0\), or, \(F_{z}(p) \neq 0\), respectively, where

$$
X=\left(\begin{array}{cc} F_{y} & F_{z} \tag{47}\\ -F_{x} & 0 \\ 0 & -F_{x} \end{array}\right), Y=\left(\begin{array}{cc} -F_{y} & 0 \\ F_{x} & F_{z} \\ 0 & -F_{y} \end{array}\right), Z=\left(\begin{array}{cc} -F_{z} & 0 \\ 0 & -F_{z} \\ F_{x} & F_{y} \end{array}\right)
$$

Since \(T_{p} S=\operatorname{ker} d F_{p}\), we see that this is equivalent to the existence of a scalar \(\lambda\) such that \(d G_{p}=\lambda d F_{p}\).

$$
\begin{align*} & F_{x} f_{y}+F_{y}=0 \tag{48}\\ & F_{x} f_{z}+F_{z}=0 \tag{49} \end{align*}
$$

- Since 0 is a regular value of F, we have ∇ \(F(p)=0\). We assume that F \(x(p)=0\), and argue similarly in case F \(y(p)=0\) or F \(z(p)=0\). Furthermore, assume that p = (0, 0, 0). According to the Implicit Function Theorem, there is a unique local solution x = f (y, z), with \(f(0,0)=0\), of the equation \(F(x,y,z)=0\). Implicit differentiation yields

where \(f_{y}\) and \(f_{z}\) are evaluated at \((y, z)\), and \(F_{x}, F_{y}\) and \(F_{z}\) are evaluated at \((f(y, z), y, z)\). Similarly,

$$
\begin{equation*} F_{x x} f_{y}^{2}+2 F_{x y} f_{y}+F_{y y}+F_{x} f_{y y}=0 \tag{50} \end{equation*}
$$

Similar identities are obtained by differentiating (48) with respect to \(y\), and (49) with respect to \(z\).

Using \(y\) and \(z\) as local coordinates on \(S\), we obtain the following expression of \(G \mid S\) with respect to these local coordinates:

$$
g(y, z)=G(f(y, z), y, z)
$$

Differentiating this identity twice with respect to y we obtain

$$
\begin{equation*} g_{y y}=G_{x x} f_{y}^{2}+2 G_{x y} f_{y}+G_{y y}+G_{x} f_{y y} \tag{51} \end{equation*}
$$

Since \(F_{x}(p) \neq 0\), we solve \(f_{y_{y}}\) from (50), and plug the resulting expression into (51), to get where is the Lagrange multiplier, cf. (44). We rewrite (52) as

$$
\lambda=\frac{G_{x}}{F_{x}}
$$

$$
\begin{aligned} g_{y y} & =\left(\begin{array}{lll} f_{y} & 1 & 0 \end{array}\right)\left(H_{G}-\lambda H_{F}\right)\left(\begin{array}{c} f_{y} \\ 1 \\ 0 \end{array}\right) \\ & =\frac{1}{F_{x}^{2}}\left(\begin{array}{lll} F_{y} & -F_{x} & 0 \end{array}\right)\left(H_{G}-\lambda H_{F}\right)\left(\begin{array}{c} F_{y} \\ -F_{x} \\ 0 \end{array}\right) \end{aligned}
$$

$$
g_{y z}=\frac{1}{F_{x}^{2}}\left(\begin{array}{lll} F_{y} & -F_{x} & 0 \end{array}\right)\left(H_{G}-\lambda H_{F}\right)\left(\begin{array}{c} F_{z} \\ 0 \\ -F_{x} \end{array}\right)
$$

$$
g_{z z}=\frac{1}{F_{x}^{2}}\left(\begin{array}{lll} F_{z} & 0 & -F_{x} \end{array}\right)\left(H_{G}-\lambda H_{F}\right)\left(\begin{array}{c} F_{z} \\ 0 \\ -F_{x} \end{array}\right)
$$

Since the vectors \(\left(F_{y},-F_{x}, 0\right)\) and \(\left(F_{z}, 0,-F_{x}\right)\) span the tangent space \(T_{p} S\), we see that

$$
\left(\begin{array}{cc} g_{y y} & g_{y z} \\ g_{y z} & g_{z z} \end{array}\right)=\frac{1}{F_{x}^{2}} \Delta
$$

## B The Morse Lemma with parameters

The Morse Lemma gives a normal form for a smooth function in a neighborhood of a non-degenerate critical point. We discuss an extension of this result to functions depending on parameters. We refer to Arnol'd [2] for a proof. Let \(F: \mathbb{R}^{n} \times \mathbb{R}^{k} \rightarrow \mathbb{R}\) be a smooth map, and let the function \(f: \mathbb{R}^{n} \rightarrow \mathbb{R}\), defined by \(f(x)=F(x, 0)\), have a non-degenerate singularity at \(p \in \mathbb{R}^{n}\). Then the function \(F_{\mu}: \mathbb{R}^{n} \rightarrow \mathbb{R}\) has a non-degenerate singularity \(p_{\mu}\), which depends smoothly on \(\mu \in \mathbb{R}^{k}\), and coincides with \(p\) for \(\mu=0\). In fact, the singular point \(x=p_{\mu}\) is a solution of the system of equations

$$
\frac{\partial F}{\partial x_{1}}(x, \mu)=\cdots=\frac{\partial F}{\partial x_{n}}(x, \mu)=0
$$

Therefore, the Implicit Function Theorem guarantees the existence and uniqueness of the local solution p µ .

Proposition B.1. There is a local diffeomorphism \(\Phi: \mathbb{R}^{n} \times \mathbb{R}^{k} \rightarrow \mathbb{R}^{n} \times \mathbb{R}^{k}\), defined on a neigh borhood of ( \(p, 0\) ), of the form

$$
\Phi(x, \mu)=(\varphi(x, \mu), \mu),
$$

$$
\begin{equation*} g_{y y}=\left(G_{x x}-\lambda F_{x x}\right) f_{y}^{2}+2\left(G_{x y}-\lambda F_{x y}\right) f_{y}+\left(G_{y y}-\lambda F_{y y}\right) \tag{52} \end{equation*}
$$

$$
F \circ \Phi(x, \mu)=\sigma_{1} x_{1}^{2}+\cdots+\sigma_{n} x_{n}^{2}+F\left(p_{\mu}, \mu\right)
$$

where \(\sigma_{i}=\pm 1, i=1, \ldots, n\), defines the signature of the quadratic part of \(f\) at \(p\).

The proof of the Morse Lemma with parameters is completely similar to the proof of the 'regular' Morse Lemma.

## C Normal form of a Whitney fold

### C.1 Fold points of good mappings

A celebrated theorem of Whitney [22] states that generic mappings of the plane into the plane have only two types of singular points, namely folds or cusps. In this note we discuss a normal form for such a mapping in the neighborhood of a fold point, and sketch a method for actually computing such a normal form. Let \(f: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) be a mapping, and let \(J: \mathbb{R}^{2} \rightarrow \mathbb{R}\) be its Jacobian determinant. More precisely, if \(f(x, y)=(u(x, y), v(x, y))\), then

$$
J=u_{x} v_{y}-u_{y} v_{x}
$$

The mapping \(f\) is called good if \(J(p) \neq 0\) or \(\nabla J(p) \neq 0\), at every point \(p \in \mathbb{R}^{2}\). In other words, the system of equations

$$
\begin{equation*} J(x, y)=J_{x}(x, y)=J_{y}(x, y)=0 \tag{53} \end{equation*}
$$

has no solutions in \(\mathbb{R}^{2}\). It can be proven that this condition is independent of the choice of coordinates.

Whitney proves that generically a map from the plane into the plane is good. Intuitively, this may seem to follow from the observation that generic systems of three equations in two unknowns do not have a solution. However, it is not obvious that (53) is a generic system. A proof can be given using Thom's transversality theorem. Consequently, the singular set \(S_{1}(f)=J^{-1}(0)\) of a good map consists of a number of disjoint regular curves in the plane. This is a straightforward consequence of the Implicit Function Theorem, since the gradient of \(J\) is non-zero at every point of \(S_{1}(f)\). Furthermore, at a singular point \(p\) at least one of the partial derivatives of the component functions of \(f\) is non-zero, i.e.

$$
\begin{equation*} \left(u_{x}(p), u_{y}(p), v_{x}(p), v_{y}(p)\right) \neq(0,0,0,0) \tag{54} \end{equation*}
$$

In particular, the rank of the derivative \(d f_{p}\) at a singular point is one, or, equivalently, the kernel of \(d f_{p}\) is one-dimensional. A singular point \(p\) of a good map \(f\) is called a fold point [10] if

$$
\begin{equation*} T_{p} S_{1}(f) \oplus \operatorname{Ker} d f_{p}=\mathbb{R}^{2} \tag{55} \end{equation*}
$$

Note that the tangent space \(T_{p} S_{1}(f)\) is well-defined, since \(S_{1}(f)\) is a regular curve. Whitney's [22] version of (55) is slightly different: if \(w\) is a non-zero tangent vector at \(p\) to \(S_{1}(f)\), then the directional derivative of \(f\) in the direction \(w\) is non-zero, i.e., \(\nabla_{w} f(p) \neq 0\). Obviously, the two versions are equivalent, and, more importantly, neither version depends on a particular choice of coordinates. The latter observation follows from Lemma C.1.

Lemma C.1. Let \(f\) be a good map, \(\varphi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) an invertible non-singular map, and \(g=f \circ \varphi\). Then

- (i) \(S_{1}(g)\) = ϕ -1 (\(S_{1}(f)\)) ;

- (ii) g (\(S_{1}(g)\)) = f (\(S_{1}(f)\)) ;

- (iii) g is a good map;

- (iv) p is a fold point of g iff ϕ (p) is a fold point of f.

Since

$$
\begin{equation*} d g_{p}=d f_{\varphi(p)} \circ d \varphi_{p} \tag{56} \end{equation*}
$$

$$
\begin{equation*} \tilde{J}(p)=J(\varphi(p)) \cdot \operatorname{det} d \varphi_{p} \tag{57} \end{equation*}
$$

Therefore, \(\varphi\left(\tilde{J}^{-1}(0)\right)=J^{-1}(0)\), which is equivalent to first claim. The second claim is an immediate consequence of the first one. To prove the third claim, let \(p \in S_{1}(g)\), i.e., \(\tilde{J}(p)=0\). Then (57) implies \(J(\varphi(p))=0\). Therefore, applying the product rule to (57) yields

$$
\begin{equation*} d \tilde{J}_{p}=\operatorname{det} d \varphi_{p} \cdot d J_{\varphi(p)} \circ d \varphi_{p} \tag{58} \end{equation*}
$$

Since \(d \varphi_{p}\) is invertible, we see that the scalar \(\operatorname{det} d \varphi_{p}\) is non-zero, and hence that

$$
d \tilde{J}_{p} \neq 0 \text { iff } d J_{\varphi(p)} \neq 0
$$

This proves the third claim. Finally, observe that (56) implies

$$
\begin{equation*} d \varphi_{p}\left(\operatorname{Ker} d g_{p}\right)=\operatorname{Ker} d f_{\varphi(p)} \tag{59} \end{equation*}
$$

and that (58) implies

$$
\begin{equation*} d \varphi_{p}\left(\operatorname{Ker} d \tilde{J}_{p}\right)=\operatorname{Ker} d J_{\varphi(p)} \tag{60} \end{equation*}
$$

Since \(\operatorname{Ker} d \tilde{J}_{p}=T_{p} S_{1}(g)\), and \(\operatorname{Ker} d J_{\varphi(p)}=T_{\varphi(p)} S_{1}(f)\), we conclude from (59) and (60) that

$$
T_{p} S_{1}(g) \oplus \operatorname{Ker} d g_{p}=\mathbb{R}^{2} \quad \text { iff } \quad T_{\varphi(p)} S_{1}(f) \oplus \operatorname{Ker} d f_{\varphi(p)}=\mathbb{R}^{2}
$$

in other words: \(p\) is a fold point of \(g\) iff \(\varphi(p)\) is a fold point of \(f\). This concludes the proof of the fourth claim.

For later use, we isolate the following result.

Lemma C.2. Let \(f: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) be a good map, with component functions \(u, v: \mathbb{R}^{2} \rightarrow \mathbb{R}\), and Jacobian determinant \(J: \mathbb{R}^{2} \rightarrow \mathbb{R}\). The following statements are equivalent:

- (i) p is a fold point of f ;

- (ii) W p = (0, 0), where

$$
W_{p}=\left(\left\langle\nabla u(p), \nabla J(p)^{\perp}\right\rangle,\left\langle\nabla v(p), \nabla J(p)^{\perp}\right\rangle\right) .
$$

In either case, \(W_{p}\) is a tangent vector of the regular curve \(f\left(S_{1}(f)\right)\) at \(p\).

Proof. Since \(f\) is good, \(J^{-1}(0)=S_{1}(f)\) is a regular curve, containing \(p\). Its tangent vector at \(p\) is Since \(d f_{p}\) has rank one, we have \(\nabla u(p) \neq(0,0)\) or \(\nabla v(p) \neq(0,0)\). Assume the former inequality holds. Then there is a real constant \(c\) such that

It now follows that (55) is holds iff \(\nabla u(p)^{\perp}\) is not parallel to \(\nabla J(p)^{\perp}\), or, iff \(\left\langle\nabla u(p), \nabla J(p)^{\perp}\right\rangle \neq 0\). Similarly, if \(\nabla v(p) \neq 0\), then (55) is equivalent to \(\left\langle\nabla v(p), \nabla J(p)^{\perp}\right\rangle \neq 0\). In either case, \(W_{p} \neq 0\).

$$
Now for W ∈ R 2 , so df p ( ∇ u ( p ) ⊥ ) = (0 , 0). Hence Ker df p = R ∇ u ( p ) ⊥ .
$$

$$
\begin{equation*} d f_{p}(W)=(\langle\nabla u(p), W\rangle,\langle\nabla v(p), W\rangle) \tag{61} \end{equation*}
$$

To prove that \(W_{p}\) is tangent to \(f\left(S_{1}(f)\right)\) at \(p\), let \(s \mapsto(x(s), y(s))\) be a regular parametrization of \(J^{-1}(0)\), with \((x(0), y(0))=p\), and \(\left(x^{\prime}(0), y^{\prime}(0)\right)=\nabla J(p)^{\perp}\). Then \(\alpha(s)=f(x(s), y(s))\) is a parametrization of \(f\left(J^{-1}(0)\right)\), and, in view of (61 we have

$$
\begin{equation*} \alpha^{\prime}(0)=d f_{p}\left(\nabla J(p)^{\perp}\right)=W_{p} \tag{62} \end{equation*}
$$

### C.2 Normal form of a good map near a fold point

Our goal is to obtain a simple form of a good map near a fold point. Such a normal form can be obtained by applying a change of coordinates on the domain of the map, on its range, or both. We start by applying only changes of coordinates on the domain of the map.

Proposition C.3. Let \(f: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) be a good map with component functions \(u, v: \mathbb{R}^{2} \rightarrow \mathbb{R}\), and Jacobian determinant \(J: \mathbb{R}^{2} \rightarrow \mathbb{R}\). Let \(p=(0,0)\) be a fold point of \(f\), with \(f(p)=(0,0)\). The

- (i) f (J-1 (0)) is transversal to the y-axis at f (p) ;

- (ii) ∇ u (p) = (0, 0) ;

- (iii) There is a local change of coordinates ϕ : \(R_{2}\) → \(R_{2}\), with ϕ (0, 0) = p, such that

$$
\begin{equation*} f \circ \varphi(x, y)=\left(x, \sigma y^{2}+\alpha(x)\right), \tag{63} \end{equation*}
$$

where \(\sigma=\operatorname{sign}\left(\left\langle\nabla u(p), \nabla J(p)^{\perp}\right\rangle\right)=\pm 1\), and \(\alpha: \mathbb{R} \rightarrow \mathbb{R}\) is a smooth function with \(\alpha(0)=0\).

Remark If \(g=f \circ \varphi\), we shall say that \(\varphi\) brings \(f\) into the form \(g\). The right hand side of (63) will be considered as a normal form. The transformations bringing the mapping into normal form should be computationally feasible. Therefore, we shall be very precise about each and every step we take.

Proof. Proposition C.3 Since g (\(S_{1}(g)\)) = { (x, α (x)) | x ∈ \(R_{2}\), the first claim follows.

$$
\nabla v(p)=c \nabla u(p)
$$

So it remains to prove that the (ii) implies (iii). The proof goes in two steps. We assume that p = (0, 0).

Step 1. There is a local change of coordinates bringing \(f\) into one of the forms \(g(x, y)=(x, V(x, y))\).

To see this, we first consider the case and

$$
\begin{equation*} u_{x}^{0} \neq 0 \tag{64} \end{equation*}
$$

If \(u_{x}^{0}=0\), then condition (ii) implies that \(u_{y}^{0} \neq 0\). This case is reduced to (64) by first applying the transformation \((x, y) \mapsto(y, x)\).

$$
\psi(x, y)=(u(x, y), y)
$$

is non-singular. Let \(\varphi\) be the inverse of \(\psi\), then \(\varphi(x, y)=(\xi, \eta)\) iff \(\eta=y\) and

$$
\begin{equation*} u(\xi, y)-x=0 \tag{65} \end{equation*}
$$

Let \(\xi=\xi(x, y)\) be the locally unique solution of (65) with \(\xi(0,0)=0\), then

$$
\varphi(x, y)=(\xi(x, y), y)
$$

$$
f \circ \varphi(x, y)=(x, V(x, y)), \quad \text { with } \quad V(x, y)=v(\xi(x, y), y)
$$

Step 2. If \(f(x, y)=(x, V(x, y))\) is a good map with a fold point at \((0,0)\), then there is a local change of coordinates bringing \(g\) into the form \(g(x, y)=\left(x, \pm y^{2}+\alpha(x)\right)\), where \(\alpha: \mathbb{R} \rightarrow \mathbb{R}\) is a

$$
d f_{(x, y)}=\left(\begin{array}{cc} 1 & 0 \\ V_{x} & V_{y} \end{array}\right)
$$

we see that \((0,0)\) is a singular point of \(f\) iff

$$
\begin{equation*} V_{y}^{0}=0 \tag{66} \end{equation*}
$$

$$
\begin{equation*} V_{y y}^{0} \neq 0 . \tag{67} \end{equation*}
$$

In that case, \(\operatorname{Kerdf}(0,0)\) is the span of the vector \((0,1)\). Furthermore, \(J=V_{y}\), so the fact that \(f\) is a good mapping implies in particular that \(\nabla J(0,0)=\left(V_{x_{y}}^{0}, V_{y_{y}}^{0}\right) \neq(0,0)\). A non-zero tangent vector to \(S_{1}(f)=J^{-1}(0)\) at \((0,0)\) is \(\nabla J(0,0)^{\perp}=\left(-V_{y_{y}}^{0}, V_{x_{y}}^{0}\right)\). It is now easy to see that condition (55) is equivalent to Since also \(V(0,0)=0\), we apply the Morse Lemma with parameters to bring the function \(V\) into normal form. More precisely, there is a local change of parameters \(\varphi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) of the form \(\varphi(x, y)=(x, \Phi(x, y))\), such that

$$
V \circ \varphi(x, y)= \pm y^{2}+\alpha(x)
$$

where \(\alpha\) is a smooth function with \(\alpha(0)=0\). It is now obvious that \(f \circ \varphi\) is the desired normal form.

Concatenating steps 1 and 2 concludes the proof.

Corollary C.4. If \(f: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\) is a good mapping with a fold point at \(p\), then there is a local change of coordinates \(\varphi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), near \((0,0)\), with \(\varphi(0,0)=p\), and a local change of coordinates \(\psi: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), with \(\psi(f(p))=(0,0)\), such that

$$
\psi \circ f \circ \varphi(x, y)=\left(x, y^{2}\right)
$$

Proof. Applying Proposition C.3, we may assume that \(f(x, y)=\left(x, \pm y^{2}+\alpha(x)\right)\) or \(f(x, y)=\left( \pm x^{2}+\alpha(y), y\right)\). In the first case, take \(\psi(x, y)=(x, \pm(y-\alpha(x)))\). Then \(\psi \circ f(x, y)=\left(x, y^{2}\right)\). The second case is treated similarly.

Remark In Step 1 of the proof of Proposition C.3, in case \(u_{x}=0\), near p = (0, 0), we define the function V by \(V(x,y)\) = v ( ξ (x, y), y), where ξ = ξ (x, y) is the solution of u ( ξ, y) -x = 0. The derivatives V y and V yy can be computed from this definition in a straightforward way:

$$
V_{y}=v_{x} \xi_{y}+v_{y}=v_{x}\left(-\frac{u_{y}}{u_{x}}\right)+v_{y}=\frac{J}{u_{x}},
$$

Since \(J(0,0)=0\), we obtain

$$
V_{y y}(0,0)=\frac{\left(J_{x}^{0} \xi_{y}^{0}+J_{y}^{0}\right) u_{x}^{0}}{\left(u_{x}^{0}\right)^{2}}=\frac{-u_{y}^{0} J_{x}^{0}+u_{x}^{0} J_{y}^{0}}{\left(u_{x}^{0}\right)^{2}}
$$

Therefore, \(V_{y_{y}}(0,0) \neq 0\) iff \(\left\langle\nabla u(0,0), \nabla J(0,0)^{\perp}\right\rangle \neq 0\) iff the vectors \(\nabla u(0,0)^{\perp}\) and \(\nabla J(0,0)^{\perp}\) are not parallel. We claim that \(\nabla u(0,0)^{\perp}=\left(-u_{y}^{0}, u_{x}^{0}\right)\) is a non-zero vector in \(\operatorname{Ker} d f_{0}\). Indeed, since \(d f_{0}\) has rank 1, we see that \(\nabla v(0,0)=c \nabla u(0,0)\), for some real constant \(c\). Therefore

$$
\left(\begin{array}{cc} u_{x}^{0} & u_{y}^{0} \\ v_{x}^{0} & v_{y}^{0} \end{array}\right)\binom{-u_{y}^{0}}{u_{x}^{0}}=\binom{0}{0},
$$

### C.3 Introducing parameters

If \(f\) depends on an additional parameter \(t\), we can still obtain a normal form like (63), provided we let both the transformation \(\varphi\) and the function \(\alpha\) depend on this new parameter. More precisely, consider a family of maps \(f_{t}: \mathbb{R}^{2} \rightarrow \mathbb{R}^{2}\), depending smoothly on the parameter \(t \in \mathbb{R}\), such that \(f_{0}\) satisfies any of the conditions (i), (ii) and (iii) of Proposition C.3. With this family we associate the map \(F: \mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2}\), defined by \(F(x, t)=f_{t}(x)\). Then there is a one-parameter family \(\Phi: \mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2} \times \mathbb{R}\) of local coordinate transformations of the form

$$
\Phi(x, y, t)=\left(\varphi_{t}(x, y), t\right)
$$

The latter identity may be rephrased as

$$
f_{t} \circ \varphi_{t}(x, y)=\left(x, \sigma y^{2}+\alpha(x, t)\right) .
$$

$$
\begin{equation*} F \circ \Phi(x, y, t)=\left(x, \sigma y^{2}+\alpha(x, t)\right) . \tag{68} \end{equation*}
$$

The image of the fold curve of \(f_{t}\) is \(f_{t}\left(S_{1}\left(f_{t}\right)\right)=\{(x, \alpha(x, t)) \mid x \in \mathbb{R}\}\). The point of intersection of this curve with the \(y\)-axis, viz \((0, \alpha(0, t))\), passes through the origin with speed \(\alpha_{t}^{0}\) (Here we consider \(t\) as time). To express this velocity in terms of \(f_{t}\), let \(u(x, y, t)\) and \(v(x, y, t)\) be the component functions of \(F(x, y, t)\).

Lemma C.5. If \(u_{x}(p, 0) \neq 0\), then

$$
\alpha_{t}^{0}=\frac{1}{u_{x}(p, 0)} \frac{\partial(u, v)}{\partial(x, t)}(p, 0),
$$

$$
\alpha_{t}^{0}=\frac{1}{u_{y}(p, 0)} \frac{\partial(u, v)}{\partial(y, t)}(p, 0)
$$

Proof. Let Φ(x, y, t) = ( ξ (x, y, t), η (x, y, t)). Then (68) boils down to

$$
\begin{aligned} u(\xi(x, y, t), \eta(x, y, t), t) & =x \\ v(\xi(x, y, t), \eta(x, y, t), t) & =\sigma y^{2}+\alpha(x, t) \end{aligned}
$$

Differentiating the latter identity with respect to \(t\) and evaluating at ( \(p, 0\) ) yields

$$
\begin{align*} u_{x}^{0} \xi_{t}^{0}+u_{y}^{0} \eta_{t}^{0}+u_{t}^{0} & =0 \tag{69}\\ v_{x}^{0} \xi_{t}^{0}+v_{y}^{0} \eta_{t}^{0}+v_{t}^{0} & =\alpha_{t}^{0} \end{align*}
$$

$$
\alpha_{t}^{0}=v_{t}^{0}-c u_{t}^{0}=\frac{1}{u_{x}^{0}}\left(u_{x}^{0} v_{t}^{0}-v_{x}^{0} u_{t}^{0}\right)
$$

Since the second condition of Proposition C. 3 holds, i.e., \(\left(u_{x}^{0}, u_{y}^{0}\right) \neq(0,0)\), there is a scalar constant \(c\) such that \(\left(u_{x}^{0}, u_{y}^{0}\right)=c\left(v_{x}^{0}, v_{y}^{0}\right)\). Therefore, (69) implies:

If \(u_{y}^{0} \neq 0\), the second identity is derived similarly.

$$
Remark Lemma C. 5 implies that \( \alpha_{t}^{0} \neq 0 \) iff the matrix
$$

has rank two. Furthermore, since \(u_{x}^{0} v_{y}^{0}-u_{y}^{0} v_{x}^{0}=0\), it follows that

$$
u_{y}^{0}\left|\begin{array}{cc} u_{x}^{0} & u_{t}^{0} \\ v_{x}^{0} & v_{t}^{0} \end{array}\right|=u_{x}^{0}\left|\begin{array}{cc} u_{y}^{0} & u_{t}^{0} \\ v_{y}^{0} & v_{t}^{0} \end{array}\right|
$$

In view of Lemma C. 5 both sides of this equality are equal to \(u_{x}^{0} u_{y}^{0} \alpha_{t}^{0}\).

## D Metaballs

One approach to modeling using implicit surfaces is to use metaballs. A single metaball consists of a density function around a single point. The function value at the point equals a given weight, and drops to zero at a given distance (the radius) from the centre. By adding individual metaballs and subtracting a threshold value, blobby objects can be joined smoothly.

$$
\left(\begin{array}{ccc} u_{x}^{0} & u_{y}^{0} & u_{t}^{0} \\ v_{x}^{0} & v_{y}^{0} & v_{t}^{0} \end{array}\right)
$$

For a single metaball with weight \(w\) and radius \(R\) we use the density function

$$
D(P)= \begin{cases}w\left(1-\left(\frac{r}{R}\right)^{2}\right)^{2} & r<R \\ 0 & r \geq R\end{cases}
$$

where \(r\) is the distance from \(P\) to the centre of the metaball.

Using threshold T, the implicit function for the metaball object is given by

$$
F(P)=\sum_{i=1}^{n} D_{i}(P)-T
$$

## References

- P. Alliez, N. Laurent, H. Sanson, and F. Schmitt. efficient view-dependent refinement of 3d meshes using sqrt(3)-subdivision, 2001. To appear in the Visual Computer.

- V.I. Arnol'd. Wave front evolution and equivariant Morse lemma. Comm. Pure Appl. Math., 29:557-582, 1976.

- V.I. Arnol'd. Catastrophe Theory. Springer-Verlag, Berlin, 1986.

- G. Barequet, C.A. Duncan, M.T. Goodrich, S. Kumar, and M. Pop. efficient perspectiveaccurate silhouette computation. In Proc. 15th Annu. ACM Sympos. Comput. Geom., pages 417-418, 1999.

- J. Bloomenthal. Introduction to Implicit Surfaces. Morgan-Kaufmann, 1997.

- D.J. Bremer and J.F. Hughes. Rapid approximate silhouette rendering of implicit surfaces. In Proceedings of Implicit Surfaces '98, pages 155-164, 1998.

- J.W. Bruce. Seeing-the mathematical viewpoint. The Mathematical Intelligencer, 6:18-25, 1984.

- J.W. Bruce and P.J. Giblin. Outlines and their duals. Proc. London Math. Soc. (3), 50:552-570, 1985.

- R. Cipolla and P.J. Giblin. Visual Motion of curves and Surfaces. Cambridge University Press, 2000.

- M. Golubitsky and V. Guillemin. Stable Mappings and Their Singularities, volume 14 of Graduate Texts in Mathematics. Springer-Verlag, 1973.

- A.T. Fomenko and T.L. Kunii. Topological Modeling for Visualization. Springer-Verlag, Tokyo, 1997.

- X. Gu, S.J. Gortler, H. Hoppe, L. McMillan, B.J. Brown, and A.D. Stone. silhouette mapping. Computer Science Technical Report TR-1-99, Harvard University, March 1999.

- E.R. Hansen and R.I. Greenberg. An Interval Newton Method. Applied Mathematics and Computation, 12:89-98, 1983.

- D. Hearn, M.P. Baker. Computer Graphics, 2nd edition Prentice-Hall, Englewood Cliffs, NJ, 1994.

- C.M. Hoffman. Geometric and Solid Modeling. Morgan-Kaufman, 1989.

- J.J. Koenderink. Solid Shape. Artificial Intelligence. MIT-Press, Cambridge, Massachusetts, 1990.

- L. Markosian, M.A. Kowalski, S.J. Trychin, L.D. Bourdev, D. Goldstein, and J.F. Hughes. Real-time nonphotorealistic rendering. In SIGGRAPH'97 Proceedings, pages 415-420, 1997.

- J. Milnor. Morse Theory, Vol.51 of Annals of Mathematics Studies, Princeton University Press, Princeton, NJ, 1963.

- A. Opalach and S.C. Maddock. An Overview of Implicit Surfaces. Introduction to Modelling and Animation Using Implicit Surfaces, pages 1.1-1.13, 1995.

- J.M. Snyder. Interval analysis for Computer Graphics. SIGGRAPH'92 Proceedings, pages 121-130, 1992.

- B.T. Stander and J.C. Hart. Guaranteeing the topology of an implicit surface polygonization for interactive modeling. SIGGRAPH'97 Proceedings, pages 279-286, 1997.

- H. Whitney. On singularities of mappings of euclidean spaces I, mappings of the plane into the plane. Ann. of Math., 62:374-410, 1955.
