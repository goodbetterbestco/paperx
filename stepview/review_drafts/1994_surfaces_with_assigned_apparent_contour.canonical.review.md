# Surfaces with Assigned Apparent Contour

[missing from original]

[missing from original]

## Abstract

[Generated abstract from introduction.] This paper studies when a curve with cusps and normal crossings on a surface can be realized as the apparent contour of a smooth surface under a generic map. The author reduces the problem to constructing local excellent extensions near the critical set together with immersive extensions of the resulting boundary curves, extending Blank's word method to curves with cusps and crossings. A combinatorial algorithm based on minimal assemblages is then used to classify excellent extensions up to right equivalence and to derive necessary and sufficient conditions for realizing prescribed contours as apparent contours of embedded generic surfaces in line bundles.

## Introduction

In all the paper we will denote by \(\mathbf{S}^{1}\) the unit circle in Euclidean plane \(\mathbb{R}^{2}\), and by \(\amalg_{h=1}^{k} \mathbf{S}^{1}\) the disjoint union of \(k\) identical copies of the circle; all surfaces and maps will be supposed smooth (i.e. of class \(C^{\infty}\) ). Furthermore we will often use "cut and paste" techniques which work fine in \(C^{0}\) or PL category. Since in low dimension these categories are the same as the \(C^{\infty}\) one, we shall not care to give technical details.

Let \(S\) and \(\mathbf{N}\) be smooth, compact surfaces, \(p \in S\).

definition. A map \(F: S \rightarrow \mathbf{N}\) is said excellent at \(p\) if its germ at \(p\) is equivalent (left-right) to one of the following three normal forms:

Clearly, if \(F\) is excellent at every \(p\) then the set \(\Sigma_{F}\) of its critical points is a smooth curve in \(S\) (i.e. \(\Sigma_{F}\) is a finite union of disjoint circles).

definition. F is said excellent if the following two properties hold:

- (1) F is excellent at every p e 5';

- the apparent contour of F, i.e. the set rF = \(F(IF)\) c N, is a smooth curve except for a finite number of singularities of the following two local kinds:

A classical theorem of Whitney [22], asserts that excellent maps are stable and constitute an open, dense subset of the set of \(C^{\infty}\) maps between two surfaces. This theorem shows the reason why excellent maps are sometimes called generic.

~*~ This work was partially supported by M.U.R.S.T.

Pervenuto alla Redazione 1' 8 Giugno 1992.

Surfaces with Assigned Apparent Contour

DOMENICO LUMINATI(*) Given a curve r C N satisfying condition (2) of the previous definition, we ask whether there exist a surface S and a map F : S ~ N such that r F = r. Moreover we should like to know how many such maps exist up to right equivalence. This problem can obviously be restated as follows: given a curve, f : S' N, with only cusps and normal crossings (definition 1.1) find out all surfaces,S D \(S_{1}\) and maps F : S-N such that IF \(S_{1}\) II The basic idea we will use to solve this problem, is not dissimilar from the one used by Francis and Troyer [8], [9] to solve the problem for plane curves, and arise from a very simple remark by Haefliger [11]: let \(F\) be an excellent extension of \(f\) and \(U\) a tubular neighborhood of \(\Sigma\) : then \(F\) restricted to \(S-U\) is an immersion. Furthermore, one can suppose thet \(F\) restricted to \(\partial U\) is a curve with only normal crossings. Hence the problem reduces to the following two sub-problems: \(i\) ) find out local, excellent extensions of \(f\) to a union of cylinders and Mœbious bands, ii) find out immersive extensions of the curves resulting as "boundary of the local extensions". The last problem can be solved using Blank's methods [1], [19].

In § 1 we define an extension of Blank's word for curves with cusps and normal crossings, from which, by a purely combinatorical algorithm, we construct a set (the set of minimal assemblages) which is in one-to-one correspondence with the set of excellent extensions of the curve, up to right equivalence (Theorem 1.34).

In §0 we will sketch, without any proof, the methods, firstly introduced by Blank [1], [19] and subsequently developed by other authors ([14], [4], [5], [10], [3], [2]), to find all (up to right equivalence) the immersive extensions of a curve with normal crossings only. We include this section because our notations and statements differ a little from those of the original papers. For a complete survey on this matter see also the first chapter of [13].

Finally, given a line bundle \(\pi: \mathbf{E} \rightarrow \mathbf{N}\), and a curve with cusps and normal crossings \(\Gamma \subset \mathbf{N}\), we ask whether there exists a generic surface (i.e. \(\left.\pi\right|_{S}\) is excellent) \(S \subset \mathbf{E}\) haveing \(\Gamma\) as apparent contour. Since we can construct all excellent extensions of the given curve, the problem reduces to find a factorization \(F=\pi \circ F_{1}\), with \(F_{1}: S \rightarrow \mathbf{E}\) an embedding, of a given excellent map \(F\). In §2 we will use the methods developed in §1 to find combinatorical, necessary and sufficient conditions in order that \(F\) possesses such a factorization

0. - Immersions with assigned boundary

Definition 0.1. Let \(k\) be a positive integer; we call generic \(k\)-curve an immersion \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) whose image \(\Gamma=\coprod_{h=1}^{k} \Gamma_{h}\) is smooth up to a finite number of normal crossings.

Definition 0.2. Let \(S\) be a surface (not necessarily connected) with boundary and \(f\) a generic \(k\)-curve, we say that \(F: S \rightarrow \mathbf{N}\) extends \(f\) if and only if \(F\) is an immersion, \(\partial S=\coprod_{h=1}^{k} \mathbf{S}^{1}\) and \(\left.F\right|_{\partial S}=f\). We denote by \(E(f)\) the set of all extensions of \(f\). Given a point \(\infty \in \mathbf{N}-\Gamma\), we denote by \(E_{\infty}^{\beta}(f)\)

- If f is a generic k-curve, then the bundle f *TN --+ Sl 1 has a canonical trivial sub-bundle, T f, spanned by the never zero cross section f'. Let v f = These two sub-bundles are called the tangent and normal bundles to f.

Definition 0.3. We say \(f\) is sided if \(\nu_{f}\) is the trivial bundle. A side for \(f\) is a never zero cross section of \(\nu_{f}\), up to multiplication by a positive function.

Remark 0.4. Since \(\nu f\) can be realized as a sub-bundle of \(f^{*} T \mathbf{N}\), in such a way that \(f^{*} T \mathbf{N}=\tau f \oplus \nu f, f\) is sided if and only if there exists a vector field along \(f\) which is transversal to \(f\).

A notion of rotation number can be given for a sided curve in a surface, with respect to a fixed vector field \(X\) on \(\mathbf{N}\), not vanishing on \(\Gamma\). We denote by \(R_{X}(f)\) the rotation number of the sided curve \(f\) with respect to the vector field \(X\). We do not give its definition here (for a definition see [20], [4], [13]), we only remark that this number essentially counts how many times a vector specifyng the side turns with respect to \(X\) and that it coincides with the usual rotation number for plane curves, endowing such a curve with the side induced by the orientations of \(\mathbb{R}^{2}\), and taking \(X\) to be a constant (never zero) vector field.

Let \(S\) be a compact surface with boundary, and \(F: S \rightarrow \mathbf{N}\) be a generic immersion (i.e. \(\left.F\right|_{\partial S}\) is a generic curve), then \(\left.F\right|_{\partial S}\) has a canonical side defined by the image of an inward-pointing vector field on \(\partial S\). The following fact holds (see [4], [13]):

Proposition 0.5. Let \(F: S \rightarrow \mathbf{N}\) be a generic immersion, and let \(X\) be a vector field which has at most one isolated zero, at the point \(\infty \notin \Gamma\). Then:

$$
\begin{equation*} R_{X}\left(\left.F\right|_{\partial S}\right)=\chi(S)-\beta \chi(\mathbf{N}) . \tag{0.1} \end{equation*}
$$

$$
Here \( \chi \) denotes the Euler characteristic and \( \beta=\# F^{-1}(\infty) \).
$$

Let \(f: \amalg_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a sided curve and \(\infty \notin \Gamma\) a fixed point. definition 0.6. A set of segments for the curve \(f\) is a set \(R=\left\{r_{i}\right\}=A \cup \Omega\),

- each cxi is an oriented, smooth arc, diffeomorphic to a segment of the real line, starting at a point in some component of N-r and ending at oo;

- the wj's are smooth (diffeomorphic to representatives of a minimal system of generators of

- each ri is in general position with respect to r (i.e. misses all crossings and is transversal to r);

- for all r; n rj = oo.

We say that R is a system of segments if the following holds as well:

- if C a component of N-r and 00 f:. C, then some ai starts from C.

```text
Given a set of segments for the \( k \)-curve \( f \), fix a neighborhood \( U_{\infty} \) of the point \( \infty \) such that \( U_{\infty} \cap \Gamma=\varnothing \). For each \( r \in R \) fix an orientable neighborhood
```

![Figure I](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-1-p005.png)

*Figure I: Fig. I*

- E ri;

- e = 1 if the segment ri crosses r from left to right (positive point), with respect to the side of f ; e = -1 otherwise (negative point);

- IL = 1 if r crosses ri from left to right, with respect to the orientation of = -1 otherwise;

- for any two points we have j j' if and only if with respect to the ordering induced by the orientation on ri. ~ Хі, ,н

```text
Finally, define a set of words \( w=\left\{w_{1}, \ldots, w_{k}\right\} \) by the following construction: fix points \( p_{h} \in \Gamma_{h} \), which are neither crossings of \( \Gamma \) nor points in \( R \cap \Gamma \);
for each \( h \), walk along \( \Gamma_{h} \), starting from \( p_{h} \) and following its orientation, and write down all the labels you meet, until you come back to \( p_{h} \). Call \( w_{h} \) the word obtained in this way.
```

Definition 0.7. The set \(w=\left\{w_{1}, \ldots, w_{k}\right\}\) is called the \(k\)-word of the generic \(k\)-curve \(f\), with respect to the set of segments \(R\).

REMARK 0.8. Clearly, \(w\) depends on the choice of the base points \(p_{h}\). In fact, if we change the base point \(p_{h}\), the word \(w_{h}\) changes by the action of a cyclic permutation. We will always consider words up to cyclic permutations.

Definition 0.9. We call 0-assemblage for the \(k\)-word \(w\) a set a, whose elements are unordered pairs \(\left\{x_{i, j, \mu}^{-1}, x_{i, j^{\prime}, \mu^{\prime}}\right\}\) of letters in \(w\), such that:

- then

- each letter corresponding to a point in Q n r appears in some pair of ~;

- each negative letter (i.e. with e = -1) appears in some pair of~;

- each letter appears in at most one pair of A.

Given \(f\) and \(R\) as above, fix a neighborhood \(V_{\infty}\) of \(\infty\) and a diffeomorphism \(\Phi_{\infty}: V_{\infty} \rightarrow \mathbf{B}^{2}\) ( \(\mathbf{B}^{2}\) denotes the unit ball in \(\mathbb{R}^{2}\) ), such that:

- InVo=Ø;

- n \(v_{00}\)) is a set of rays starting at the origin;

```text
and for each integer 1 &#x3E;
1 define gi : S 1 -~ N as gl (t) ( ( 3 + 3l ~ ezt ~ , endowed with the side pointing outside Voo.
```

Definition 0.10. We call \(\beta\)-expansion of the \(k\)-curve \(f\), the \((k+\beta)\)-curve \(f^{\beta}\), obtained by adding \(g_{1}, \ldots, g_{\beta}\) to \(f\). If \(w\) is a word for \(f\), we call \(\beta\)-expansion of the \(k\)-word \(w\) the \((k+\beta)\)-word \(w^{\beta}\) for \(f^{\beta}\) defined by the same set of segments as \(w\). Finally, we call \(\beta\)-assemblage for the word \(w\) a 0-assemblage for \(w^{\beta}\).

REMARK 0.11. \(w^{\beta}=w \cup\left\{u_{1}, \ldots, u_{\beta}\right\}, u_{l}\) being the word for \(g_{l}\). Observe that the words \(u_{1}, \ldots, u_{\beta}\) are equal up to the shift of the index \(j\) of all letters. We define an action of the symmetric group \({ }_{\beta}\) on the set \(A^{\beta}(w)\) of \(\beta\)-assemblages of \(w \sigma \mathrm{a}\) being the set obtained from a by replacing each letter in \(u_{l}\) with the corresponding one in \(u_{\sigma l}\). Clearly \(\sigma\) A fulfills conditions (1)-(4) in definition 0.9, hence it is actually a \(\beta\)-assemblage for \(w\).

## A 0-assemblage

A defines a graph \(G(~)\) as follows: take k + ~3 disjoint, oriented circles Cl, ... , Ck and on each circle Ch, h = 1, ... , l~ [resp. choose points corresponding to the letters of the word Wh [resp. ul], ordered as in Wh [resp. ul], and join by an extra edge (we call such an edge a proper edge) all pairs of points corresponding to pairs of letters in A. Finally weight each proper edge by-1 or 1 according as the It signs of its vertices agree or not.

A graph as just described (i.e. with all vertices standing on \(k\) disjoint, oriented circles and all proper edges weighted by \(\pm 1\) ) will be called a weighted \(k\)-circular graph. We denoted by \(l(G)\) the number of connected components of \(G\).

Definition 0.12. Let \(G\) be a connected weighted \(k\)-circular graph, and \(S\) a surface with \(k\) boundary component. We say that \(G\) is embeddable in \(S\) if there exists a map \(\varphi: G \rightarrow S\) such that the following three properties hold:

- (1) p is a homeomorphisms onto its image;

for each proper edge \(\ell\) of \(G\), let \(U_{\ell}\) be a neighborhood of \(\varphi(\ell)\) homeomorphic to \(\ell \times[-1,1]\). Two semiorientations are naturally defined on \(\partial S \cap U_{\ell}\) : the one induced as boundary of \(U_{\ell}\) and the one induced from the orientation of the circles \(C_{h}\). (3) the just described semiorientations on \(\partial S \cap U_{\ell}\) agree if and only if the

- the just described semiorientations on as n Ul agree if and only if the weight of the edge t is equal to 1.

Obviously, every weighted k-circular graph is embeddable in some surface.

Definition 0.13. If \(G\) is a connected, weighted \(k\)-circular graph we call genus of \(G\) the number \(g(G)=\min \{g(S) \mid G\) is embeddable in \(S\}\).

The following is easily proved (see [13]):

Proposition 0.14. Let \(G^{\prime}\) be obtained from \(G\) by reversing the orientation of a circle and changing the weight of all proper edges having just one vertex on that circle. Then \(g\left(G^{\prime}\right)=g(G)\). If \(G\) is embeddable in \(S\) and \(g(G)=g(S)\) then \(S\) is orientable if and only if there exists a finite sequence \(G=G_{0}, \ldots, G_{n}\) of The second part of the previous statement allows us to define another noteworthy number associated to the graph:

Definition 0.15. We call weighted genus of the connected \(k\)-circular graph \(G\) the number \(h(G)=2 g(G)\) or \(g(G)\) according as \(G\) is positive or not. If \(G\) is not connected and \(G_{i}\) are its connected components, we call weighted genus of \(G\) the number \(h(G)=\sum_{i} h\left(G_{i}\right)\).

We call weighted genus of a \(\beta\)-assemblage the weighted genus of its associated graph, and we denote it by \(h(\mathrm{q})\).

The following proposition holds: Proposition 0.16. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a generic curve, and \(w\) a

$$
\begin{equation*} R_{X}(f) \geq 2 l(\mathbf{q})-k-h(\mathbf{q})-\beta \chi(\mathbf{N}) . \tag{0.2} \end{equation*}
$$

Definition 0.17. Let \(w\) be defined by a system of segments. A \(\beta\)-assemblage \(\mathrm{A} \in \mathcal{A}^{\beta}(w)\) is said minimal if (0.2) is an equality. We denote by \(\mathcal{A}_{m}^{\beta}(w)\) the set of minimal \(\beta\)-assemblages of \(w\).

It is not hard to see that if a E E E A,8 (w), hence (lif3 acts on Denote right equivalence by ~, the following theorem holds: Theorem 0.18. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a generic \(k\)-curve and \(w\) a \(k\)-word for \(f\) defined by a system of segments. Then there exists a bijection between \(E_{\infty}^{\beta}(f) / \underset{\sim}{z}\) and \(A_{m}^{\beta}(w) / \xi_{\beta}\).

SKETCH OF PROOF. We only show how to define such a bijection. first suppose ~3 = 0. Let F E E~(w), then R = F-1 (R) is a set of smooth arcs in S, oriented by the immersion. Label each point of ji n 8S by the same label as the corresponding point in r, and observe that each positive labeled point (i.e. e = 1) is the ending point of some arc, while each negative labeled point (i.e. e = -1) is the starting point of some arc. Furthermore, since 0, every arc must end on as. Pairing the letters corresponding to the vertices of those arcs in R which have both vertices on as, we actually get a minimal 0-assemblage,

\(\mathrm{a}(F)\), and the mapping \(F \mapsto \mathrm{a}(F)\) is a bijection \(E_{\infty}^{0}(f) / \underset{\sim}{r} \rightarrow \mathcal{A}_{m}^{0}(w)\).

Let \(F \in E_{\infty}^{\beta}(f)\) and let \(D_{1}, \ldots, D_{\beta} \subset \mathbf{N}\) be the disks bounded by the curves \(g_{l}\) defining the \(\beta\)-expansion of \(f\) (see definition 0.10), call \(\left\{p_{1}, \ldots, p_{\beta}\right\}=F^{-1}(\infty)\) and \(U_{i}^{j}\) the interior of the connected component of \(F^{-1}\left(D_{i}\right)\) containing \(p_{j}\). For each \(\sigma \in \boldsymbol{S}_{\beta}\), let \(S_{\sigma}=S-\bigcup_{i} U_{i}^{\sigma i}\). Clearly \(F_{\sigma}=\left.F\right|_{S_{\sigma}} \in E_{\infty}^{0}\left(f^{\beta}\right)\), hence, by the case \(\beta=0\), we get an assemblage \(\mathrm{A}\left(F_{\sigma}\right) \in \mathcal{A}_{m}^{0}\left(w^{\beta}\right)=\mathcal{A}_{m}^{\beta}(w)\). Such a construction actually defines a bijection between \(E_{\infty}^{\beta}(f) / \underset{\sim}{z}\) and \(A_{m}^{\beta}(w) / \xi_{\beta}\).

The statement of the previous theorem can be slightly improved. definition 0.19. A connected component \(C\) of \(\mathbf{N}-\Gamma\) is said to be positive [resp. negative] if the side of the curve points inward [resp. outward] \(C\) at every point in \(\partial C\). We say that a set of segments is a reduced system of segments if:

- (5') at least one ai starts from each negative component.

REMARK 0.20. Proposition 0.16, definition 0.17 and finally Theorem 0.18 can be restated, and proved (see [13]), replacing the words "system of segments" by "reduced system of segments", and in this improved form they will be used in § 1.

Now we prove a lemma, we will use in § 1. Let us give one more definition:

Definition 0.21. We say that a generic \(k\)-curve has a curl if there exist \(t_{0}, t_{1} \in \mathbf{S}^{1}\) such that \(f\left(t_{0}\right)=f\left(t_{1}\right)\) and \(\left.f\right|_{\left[t_{0}, t_{1}\right]}\) bounds a disk \(D \subset \mathbf{N}\) such that

![Figure 4](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-4-p009.png)

*Figure 4: *

![Figure 2](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-2-p009.png)

*Figure 2: LEMMA 0.22. Suppose the k-curve f has a positive curl, then for every word w defined by a reduced system of segments.~m(w) _ 0.*

![Figure 3](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-3-p009.png)

*Figure 3: *

PROOF. It is enough to prove that A§\(k(w)=0\) for the word defined by some reduced system of segments. Let D be the disk bounded by the curl and observe that we can construct a reduced system of segment R such that R \(n_{D}=0\). In fact, fix 00 f:. D. Since the curl is positive, there is no need to draw segments starting from D, and all other segments can be drawn far from D. Let f * be the curve obtained by removing the curl as suggested in Fig. 2 and let w and w* be the words defined by R for f and f *. Clearly, R is a reduced system of segments for f * too, and since R \(n_{D}=0\) we have w = w*. Applying (0.2) to f * and using + 1, we get: Rx(f) &#x3E; 2l(~.) - 1~ - h(jk) for all ~ E A'(w). D

## 1 - Extending curves with cusps and normal crossings

Let \(I\) be an interval of the real line \(\mathbb{R}\), and \(f: I \rightarrow \mathbf{N}\) be a curve. definition 1.1. A point \(t_{0} \in I\) is called a cusp point if there exist germs of diffeomorphism \(\gamma:\left(I, t_{0}\right) \rightarrow(\mathbb{R}, 0)\) and \(\varphi:\left(\mathbf{N}, f\left(t_{0}\right)\right) \rightarrow\left(\mathbb{R}^{2}, 0\right)\) such that \(\varphi \circ f \circ \gamma^{-1}(s)=\left(s^{2}, s^{3}\right)\). We say that \(f: \amalg_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) is a \(k\)-curve with cusp and normal crossing (briefly a CN \(k\)-curve) if \(f^{\prime}(t) \neq 0\), except for a finite number of cusp points, and \(f\) is injective except for a finite number of normal crossings.

Let \(\mathcal{C}\) be the set of cusp points of the \(\mathrm{CN} k\)-curve \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\). definition 1.2. A side for \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) is a side for \(\left.f\right|_{\coprod_{h=1}^{k}} \mathbf{S}^{1}-c\) which is directed, in the neighborhood of each cusp, either to the inside or to the outside of the cusp on both branches of the cusp itself. We say that a cusp is positive or negative according as the side is outward or inward pointing (see Fig. 3). Finally, we say that a side for f is coherent if all cusps are negative.

Let \(F: S \rightarrow \mathbf{N}\) be an excellent mapping, by definition \(\left.F\right|_{\Sigma_{F}}\) is a CN curve.

Proposition 1.3. The curve \(\left.F\right|_{\Sigma_{F}}\) has a coherent side.

PROOF. Take the folding side of the map (see Fig. 4 and [18]). D Local extensions. Let \(f: \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a sided CN curve and let \(D \subseteq \mathcal{C}\).

Definition 1.4. We call D-deformation of the first kind of f the generic 2-curve D = fn II fD,2 obtained by doubling f and deforming its cusps as suggested in Fig. 5. Fix a point per which is neither a crossing nor a cusp, and call D-deformation of the second kind the generic 1-curve f ** obtained by modifying In in a neighborhood of p as suggested in Fig. 6.

![Figure 5](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-5-p010.png)

*Figure 5: *

![Figure 6](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-6-p010.png)

*Figure 6: *

REMARK 1.5. It is obvious that \(f_{D}^{*}=f_{\mathcal{C}-D}^{*}\) and \(f_{D}^{* *}=f_{\mathcal{C}-D}^{* *}\). By local arguments, it is easily seen that if \(F: \mathbf{S}^{1} \times[-1,1] \rightarrow \mathbf{N}\) is an excellent mapping such that \(\Sigma_{F}=\mathbf{S}^{1}=\mathbf{S}^{1} \times\{0\}\) and \(\left.F\right|_{\Sigma_{F}}=f\), then there exists a Let \(f: \amalg_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a sided \(\mathrm{CN} k\)-curve, let \(D\) be as above and let \(H \subseteq\{1, \ldots, k\}\); we call such a pair ( \(D, H\) ) a deformation pair. Denote by \(\bar{H}\) the complement of \(H\). \(f_{(D, H)}=\left\{\left(f_{h}\right)_{D}^{*} \mid h \in H\right\} \amalg\left\{\left(f_{h}\right)_{D}^{* *} \mid h \in \bar{H},\right\}\), where \(k_{H}=2 \# H+\# \bar{H}\).

REMARK 1.7. Let \(C_{h}\) be the set of cusp points in the \(h^{\text {th }}\) circle and \(D_{h}=D \cap C_{h}\); if \(D^{\prime}\) is such that either \(D_{h}^{\prime}=D_{h}\) or \(D_{h}^{\prime}=C_{h}-D_{h}\) for all \(h\), then \(f_{(D, H)}=f_{\left(D^{\prime}, H\right)}\). If \(F: \coprod_{h=1}^{k} M_{h} \rightarrow \mathbf{N}\) is a local excellent extension of \(f\) (i.e. \(M_{h}\) is either a cylinder or a Möbius band and \(\left.F\right|_{M_{h}}\) is as in Remark 1.5) then

REMARK 1.8. Let \(M\) be either a cylinder or a Möbius band. Suppose \(F: M \rightarrow \mathbf{N}\) is a local generic extension of \(f: \mathbf{S}^{1} \rightarrow \mathbf{N}\), and let \(t_{0}\) be a cusp point; if \(v \in T_{t_{0}} M-\operatorname{ker}\left(d F\left(t_{0}\right)\right)\) then \(d F\left(t_{0}\right)[v]\) is a vector tangent to the cusp. Identify \(M\) with the quotient space of \(\mathbb{R} \times[-1,1]\) by either the relation \((x, t)=(x+1, t)\) (if \(S\) is a cylinder) or the relation \((x, t)=(x+1,-t)\) (if \(S\) is a Mœbious band) in such a way that \(\pi^{-1}(p)=\mathbb{Z}\), where \(p\) is the fixed point in \(\Gamma\) and \(\pi\) denotes the quotient map. Let \(\widetilde{F}=F \circ \pi\). It can be easily seen that the deformation set induced by \(F\) is given, up to complementation, by \(D=\{t \in(0,1) \mid(t, 0)\) is a cusp point vand \(d F(t, 0)[(0,1)]\) points inward the

Using this characterization, it is not hard to prove the following:

Proposition 1.9. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a \(C N_{k}\)-curve endowed with a coherent side; then for all \((D, H)\) as above, there exists a local excellent extension of \(f\) inducing \((D, H)\) as deformation pair.

Let \(F, G:\left(\mathbb{R}^{2}, 0\right) \rightarrow\left(\mathbb{R}^{2}, 0\right)\) be two generic, singular germs having the same apparent contour (i.e. \(F\left(\Sigma_{F}\right)=G\left(\Sigma_{G}\right)=\Gamma\) ); then they have the same normal form with respect to left-right equivalence, say ii) or iii) in Introduction. Standard arguments in singularity theory prove the following:

Lemma 1.10. Let \(F, G\) be as above and suppose they induce the same side; then there exists a germ of diffeomorphism \(\Phi\) such that \(F=G \circ \Phi\).

Proposition 1.11. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a \(C N_{k}\)-curve, and \(F, G\) two local, excellent extensions of \(f\). Then \(F\) and \(G\) are locally (around \(\amalg_{h=1}^{k} \mathbf{S}^{1}\) ) right equivalent if and only if they induce the same deformation pair.

Proof. If \(F \stackrel{r}{\sim} G\) they obviously induce the same deformation pair. Suppose \(F\) and \(G\) induce the same pair. Clearly it is enough to prove the thesis for a CN 1-curve. Let \(S\) be the domain of \(F\) and \(G\). By the previous lemma we can take finite open covers, \(\left\{U_{i}\right\}_{i=1, \ldots, n},\left\{V_{i}\right\}_{i=1, \ldots, n}\) of \(\mathbf{S}^{1}\) and diffeomorphisms \(\Phi_{i}: U_{i} \rightarrow V_{i}\) such that \(\left.F\right|_{U_{i}}=\left.G\right|_{V_{i}} \circ \Phi_{i}\). Lifting all maps to the universal covering of \(S\), we see that the condition that \(F\) and \(G\) induce the same deformation set, implies that all uniquely determined diffeomorphisms are orientation-preserving [resp. reversing]. To conclude the proof it is enough to choose all the other ones to be orientation-preserving [resp. reversing] and paste them together. Q Rotation number. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a sided \(\mathrm{CN} k\)-curve, and let \(X\) be a vector field on \(\mathbf{N}\) with no zeros on \(\Gamma\). Denote by \(f^{*}\) the generic \(k\)-curve obtained by deforming all cusps in the way suggested in Fig. 7. With the just introduced notations, \(f^{*}=\coprod_{h=1}^{k}\left(f_{h}\right)_{c, 1}^{*}\). Since a deformation of \(f\) has a side, canonically induced by the side of \(f\) (Fig. 8), we can give the following: number \(R_{X}(f)=R_{X}\left(f^{*}\right)\), where \(f^{*}\) is endowed with the side induced by \(f\).

![Figure 7](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-7-p012.png)

*Figure 7: *

![Figure 8](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-8-p012.png)

*Figure 8: *

![Figure 9](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-9-p012.png)

*Figure 9: *

then \(R_{X}\left(f_{D}^{* *}\right)=R_{X}\left(f_{D}^{*}\right)=2 R_{X}(f)-c^{-}+c^{+}\); where \(c^{+}, c^{-}\)denote respectively the number of positive and negative cusps.

Proof. Since rotation number does not change when modifying a curve as suggested in Fig. 9, the left-hand side equality holds. Denote by \(c_{D}^{ \pm}\)the number of positive [resp. negative] cusps in \(D\). Then \(f_{D, 1}^{*}\) [resp. \(f_{D, 2}^{*}\) ] is obtained by adding \(c_{c-D}^{+}\)[resp. \(c_{D}^{+}\)] positive curls and \(c_{\bar{c}-D}^{-}\)[resp. \(c_{D}^{-}\)] negative curls to \(f^{*}\), hence \(R_{X}\left(f_{D, 1}^{*}\right)=R_{X}\left(f^{*}\right)+c_{c-D}^{+}-c_{\bar{c}-D}^{-}\), and \(R_{X}\left(f_{D, 2}^{*}\right)=R_{X}\left(f^{*}\right)+c_{D}^{+}-c_{D}^{-}\). Sum up the two equalities to get the thesis.

LEMMA 1.14. Let f : S~ - N be a CN k-curve and (D, H) a deformation pair; then = 2Rx(f) - c- + c+.

PROOF. This follows immediately from the previous Lemma. D From now on, we will suppose to have fixed a vector field \(X\) vanishing at most at a point \(\infty \notin \Gamma\).

Proposition 1.15. Let \(F: S \rightarrow \mathbf{N}\) be an excellent map; then:

$$
\begin{equation*} 2 R_{X}\left(\left.F\right|_{\Sigma}\right)-c=\chi(S)-\beta \chi(\mathbf{N}) ; \tag{1.1} \end{equation*}
$$

$$
here \( c \) denotes the number of cusps, and \( \beta=\# F^{-1}(\infty) \).
$$

Proof. Let \(f=\left.F\right|_{\Sigma_{F}}\). By Proposition 1.3 all cusps are negative and hence, by the previous Lemma, \(R_{X}\left(f_{(D, H)}\right)=2 R(f)-c\) for all deformation pairs \((D, H)\). Let \(U\) be a tubular neighborhood of \(\Sigma_{F}\) such that \(\left.F\right|_{\partial U}=f_{(D, H)}\). The sides on \(f_{(D, H)}\) induced respectively by the immersion \(\left.F\right|_{S-U}\) and the side of \(f\) clearly coincide, and hence, by \((0.1), R_{X}\left(f_{(D, H)}\right)=\chi(S-U)-\beta \chi(\mathbf{N})\). To conclude the proof, observe that \(\chi(S)=\chi(S-U)\), since \(S\) is obtained pasting a finite number of cylinders and Möbius bands to \(S-U\).

REMARK 1.16. The previous Proposition gives one more condition in order that a curve may be the apparent contour of an excellent map. Nevertheless it is not hard to construct examples of curves fulfilling (1.1), but being the apparent contour of no excellent map \(S \rightarrow \mathbf{N}\). We remark also that (1.1) implies a generalization of a classical theorem of Thom [21], claiming that \(\chi(S) \equiv c(\bmod 2)\) for all excellent maps \(f: S \rightarrow \mathbb{R}^{2}\). More precisely, denoting by \(\operatorname{deg}_{2}\) the modulo two degree:

Theorem 1.17. Let \(F: S \rightarrow \mathbf{N}\) be an excellent map; then \(\chi(S) \equiv c(\bmod 2)\) if and only if either \(\chi(\mathbf{N})\) is even or \(\operatorname{deg}_{2}(F)=0\).

Words. Let \(f: \coprod_{h=1}^{k} \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a CN \(k\)-curve and \(\infty \in \mathbf{N}-\Gamma\) a fixed point.

Definition 1.18. A set of segments for \(f\) is a set \(R=A \cup B \cup \Omega\) of smooth, oriented arcs in \(\mathbf{N}\), such that:

- each r e A U B is diffeomorphic to a closed interval of the real line. The ending point of these arcs is oo and the starting point is either a point in a connected component of N-r, if r E A, or a cusp, if r E B;

- Q is a set of smooth (diffeomorphic to \(S_{1}\)) representatives of a minimal set of generators of 7r,(N, oo);

- for all r, r' E R,

- each r E R is in general position with respect to r, i.e. r contains neither crossings nor cusps (except at most the starting point), is transversal to r and if it starts from a cusp, it points to the outside of the cusp.

We say that \(R\) is a system of segments for \(f\) if the following holds as well:

- at least one segment starts from each component of N-r not containing 0o and from each cusp.

Definition 1.19. Suppose \(f\) is sided, and let \(r \in R\). We say \(p \in R \cap \Gamma\) is positive if and only if either \(p\) is not a cusp and \(r\) crosses \(\Gamma\) from the left to the right or \(p\) is a positive cusp; otherwise we say \(p\) is negative.

![Figure 10](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-10-p014.png)

*Figure 10: *

As in §0, we fix a neighborhood \(U_{\infty}\) of \(\infty\) not intersecting \(\Gamma\) and oriented neighborhoods \(V_{r}\) of \(r-U_{\infty}\) for all \(r \in R\). Next we label \(x_{i, j, \mu}^{e}\) each point in \(R \cap \Gamma\) by the same rules used in §0, except for cusp points in which the index \(\mu\) is +1 or-1 according as the curve crosses the segment from left to right or from right to left (see Fig. 10). Associate a set of \(k\) words to the CN \(k\)-curve \(f\) by the same construction described in §0.

Definition 1.20. We call the set \(w=\left\{w_{1}, \ldots, w_{k}\right\}\) obtained in this way the \(k\)-word of \(f\) with respect to the set of segments \(R\).

REMARK 1.21. As for generic curves (Remark 0.8), the word of a CN curve will be considered up to cyclic permutations.

Let \(f: \mathbf{S}^{1} \rightarrow \mathbf{N}\) be a CN curve, and \(w\) be a word for \(f\). Let \(D \subseteq \mathcal{C}\).

is obtained by erasing all letters in \(w\) corresponding to cusps in \(D\) and \(w_{D, 1}^{*}\) by erasing all letters corresponding to cusps in \(C-D\).

Let \(f\) be a CN \(k\)-curve, \(w\) a \(k\)-word for \(f\) and \((D, H)\) a deformation pair. \(w_{(D, H)}\) given by \(\left\{\left(w_{h}\right)_{D}^{*} \mid h \in H\right\} \amalg\left\{\left(w_{h}\right)_{D}^{* *} \mid h \in \bar{H}\right\}\), where \(\bar{H}\) and \(k_{H}\) are as in definition 1.6. \((D, H)\) is a deformation pair and a is a \(\beta\)-assemblage for the word \(w_{(D, H)}\), as defined in definition 0.10. We denote by \(A^{\beta}(w)\) the set of \(\beta\)-assemblages REMARK 1.25. All letters, except those corresponding to cusps, appear twice in the deformed word \(w_{(D, H)}\). In the previous definition the two copies of the same letter must be considered as different letters.

Proposition 1.26. Let \(R\) be a system of segments for \(f ;\) then \(R\) is a reduced system of segments for \(f_{(D, H)}\).

Proof. Clearly, \(R\) is a set of segment for \(f_{(D, H)}\) (the deformation can be done in such a way that \(R\) is a set of segments for \(f_{(D, H)}\) ). Each connected components of \(\mathbf{N}-\Gamma_{(D, H)}\) either is essentially a component of \(\mathbf{N}-\Gamma\) or is generated by the deformation. At least one segment starts from each component of the first kind. The new ones are bounded by either the curl around some cusp or by parallel branches of \(\Gamma_{(D, H)}\). In the first case the segment which starts from the corresponding cusp, starts from the new component, in the second case, it is easily seen that the new component is not negative (see Fig. 11), hence condition (5') holds.

![Figure 11](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-11-p015.png)

*Figure 11: *

REMARK 1.27. Let \(\tilde{w}_{(D, H)}\) the word for \(f_{(D, H)}\) defined by \(R\); clearly \(\tilde{w}_{(D, H)}\) is obtained by renumbering the second index of all letters in \(w_{(D, H)}\) in such a way to preserve the previous ordering of letters belonging to the same segment; hence, a \(\beta\)-assemblage \(\mathbf{A}=((D, H), \mathrm{q})\) for the word \(w\) obviously defines a Proposition 1.28. The mapping \(\mathbf{A} \mapsto \tilde{\mathfrak{I}}_{\mathbf{A}}\) is a bijection between the set of \(\beta\)-assemblages of \(w\) having ( \(D, H\) ) as deformation pair and \(\mathcal{A}^{\beta}\left(\tilde{w}_{(D, H)}\right)\). Fur thermore \(\mathbf{A}\) and \(\tilde{\mathbf{z}}_{\mathbf{A}}\) have the same number of components and weighted genus.

Proposition 1.29. Let \(f\) be a \(C N_{k}\)-curve and \(w\) be a word defined by a system of segments. Then, for all \(\mathbf{A} \in \boldsymbol{A}^{\beta}(w)\),

$$
\begin{equation*} 2 R_{X}(f)-c_{-}+c_{+} \geq 2 l(\mathbf{A})-k_{H}-h(\mathbf{A})-\beta \chi(\mathbf{N}) . \tag{1.2} \end{equation*}
$$

PROOF. Use Proposition 1.28, (0.2) and Lemma 1.14. D definition 1.30. Let \(w\) be a word for the CN \(k\)-curve \(f\), defined by a system of segments. A \(\beta\)-assemblage \(\mathbf{A}\) of \(w\) will be called minimal if in (1.2) equality holds. We denote by \(\mathcal{A}_{m}^{\beta}(w)\) the set of minimal \(\beta\)-assemblages of \(w\).

Remark 1.31. The mapping \(\mathbf{A} \mapsto \tilde{\mathfrak{z}}_{\mathbf{A}}\) is a bijection between the set of minimal \(\beta\)-assemblages of \(w\), having ( \(D, H\) ) as deformation pair, and \(\mathcal{A}_{m}^{\beta}\left(\tilde{w}_{(D, H)}\right)\).

Let \(f\) be a CN \(k\)-curve, and suppose that the \(h^{\text {th }}\) component of \(f\) has no cusps. Let \((D, H)\) be a deformation pair; then \(\left(w_{h}\right)_{D, 1}^{*}=\left(w_{h}\right)_{D, 2}^{*}=w_{h}\). We definition 1.32. We say \(\mathbf{A}\) is \(\iota\)-equivalent to \(\mathbf{A}^{\prime}\) (briefly \(\mathbf{A} \stackrel{\iota}{\sim} \mathbf{A}^{\prime}\) ) if there exist involutions \(\iota_{h_{1}}, \ldots, \iota_{h_{n}}\) such that \(\mathbf{A}^{\prime}=\iota_{h_{n}} \ldots \iota_{h_{1}} \mathbf{A}\). We say that As in §0, we have an action of the symmetric group \({ }_{\beta}\), on the set \(\mathcal{A}^{\beta}(w)\), given by \(\sigma \mathbf{A}=((D, H), \sigma \mathrm{q})\). We denote by \(\sim\) the equivalence relation on \(\mathcal{A}^{\beta}(w)\) Remark 1.33. If \(\mathbf{A} \sim \mathbf{A}^{\prime}\) then \(\mathbf{A}\) and \(\mathbf{A}^{\prime}\) have the same number of components and the same weighted genus. Hence \(\sim\) can be restricted to the set

Let \(E_{\infty}^{\beta}(f)\) denote the set of all excellent mappings \(F\) defined on some THEOREM 1.34. Let \(w\) a word for \(f\), defined by a system of segments. The Before proving the Theorem, we give some elementary remarks.

Lemma 1.35. Let \(\mathbf{A}, \mathbf{A}^{\prime} \in \mathcal{A}^{\beta}(w), \sigma \in \sigma_{\beta}\). If \(\mathbf{A} \stackrel{\iota}{\sim} \mathbf{A}^{\prime}\), then \(\sigma \mathbf{A} \stackrel{\iota}{\sim} \sigma \mathbf{A}^{\prime}\). If REMARK 1.36. Denote by \(\stackrel{\iota \delta}{\sim}\) the equivalence relation generated by \(\stackrel{\iota}{\sim}\) and \(\stackrel{\delta}{\sim}\). We can consider the quotient relation over \(\mathcal{A}^{\beta}(w) / \xi_{\beta}\); we denote it by \(\stackrel{\iota \delta}{\sim}\) again. Denote by \([\mathbf{A}]\) the class of \(\mathbf{A}\) in \(\mathcal{A}^{\beta}(w) / 5_{\beta}\); by Lemma 1.35 we have that [AI'6 [A'] \(c_{3}\) u A'; furthermore.~m(w),~ _ (.~~(w) ~a) a.

REMARK 1.37. Let \((D, H)\) be a deformation pair and \(\tilde{w}_{(D, H)}\) be the word for \(f_{(D, H)}\) defined by the same segments as \(w\). Let \(\mathbf{A}=((D, H), \hat{\mathrm{A}}) \in \mathcal{A}^{\beta}(w)\) and Proof of Theorem 1.34. We start trying to define a map \(\mathbf{A}_{1}^{\beta}: E_{\infty}^{\beta}(f) \rightarrow \mathcal{A}_{m}^{\beta}(w) / \Phi_{\beta}\). Let \(F \in E_{\infty}^{\beta}(f)\), choose a tubular neighborhood \(U\) of the set of critical points of \(F\), in such a way that \(\left.F\right|_{\partial(S-U)}=f_{(D, H)}\) for some choice of \((D, H)\). Clearly \(\left.F\right|_{S-U}\) is an immersion which estends \(f_{(D, H)}\) and attains exactly \(\beta\) times the value \(\infty\). Let \(\mathrm{A}^{\beta}(F) \in \mathcal{A}_{m}^{\beta}\left(\tilde{w}_{(D, H)}\right) / \xi_{\beta}\) be the class of minimal assemblages associated to \(\left.F\right|_{S-U}\) by Theorem 0.18. define \(\mathbf{A}_{1}^{\beta}(F) \in \mathcal{A}_{m}^{\beta}(w) / \wp_{\beta}\) as the unique class such that \(\left[\tilde{\mathrm{A}}_{\mathbf{A}_{1}^{\beta}(F)}=\mathrm{a}^{\beta}(F)\right.\) (Remark 1.37). Observe that such a construction is not univocal, in fact it depends on:

- (a) the choice of the tubular neighborhood;

$$
and, if \( f_{h} \) is a component with no cusps and \( U_{h} \) is the correspondent component
$$

- (b) the choice of the deformation set; of U, on:

- (c) the choice of the branch of aU, used as domain of fD,l.

As we will see soon, different choices lead to \(\stackrel{\iota \delta}{\sim}\)-equivalent classes, so that a map \(\mathbf{A}_{2}^{\beta}: E_{\infty}^{\beta}(f) \rightarrow \mathcal{A}_{m}^{\beta}(w) / \sim\) is defined. Let us describe more explicitly the above construction.

Let \(\left\{p_{1}, \ldots, p_{\beta}\right\}=F^{-1}(\infty)\) and let \(D_{1}, \ldots, D_{\beta} \subset S\) be disks such that \(p_{i} \in D_{i}\) and \(F\left(\partial D_{i}\right)=g_{i}\left(\mathbf{S}_{1}\right)\), where \(g_{1}, \ldots, g_{\beta}\) are the curves giving the \(\beta\)-expansion (see definition 0.10). Denote by \(\Sigma^{\beta}\) the set \(\Sigma_{F} \cup \bigcup_{i=1}^{\beta} \partial D_{i}\). Since

Let \(U\) be the tubular neighborhood of \(\Sigma\), and let \(\gamma\) be an arc of \(\left(\left.F\right|_{\left(s-\bigcup D_{i}\right)}\right)^{-1}(R)\). Clearly, \(\gamma\) intersects \(\partial U\) in as many points as \(\gamma \cap \Sigma\). Label these points as the corresponding ending point of \(\gamma\). If we read the letters on \(\partial U\) we get the word \(w_{(D, H)}\), while if we read the letters on \(\partial D_{i}\) we get the words \(u_{i}\) (for all \(i=1, \ldots, k\) ) of the \(\beta\)-expansion (see \(\S 0\) ). Pairing together letters corresponding to ending points of the same arc, we get a \(\beta\)-assemblage for \(w_{(D, H)}\), hence a \(\beta\)-assemblage for \(w\), whose class in \(\mathcal{A}^{\beta}(w) / \xi_{\beta}\) is equal to \(\mathbf{A}_{1}(F)\) (compare with the sketch of proof of Theorem 0.18).

From the last construction, it is clear that leaving \(U\) and the deformation set \(D\) fixed, but exchanging the role of the two branches of \(\partial U_{h}\), the assemblage changes by the action of the involution \(\iota_{h}\). It is also clear that choosing a different deformation set the assemblage changes by a \(\delta\)-equivalence. Finally if \(U, U^{\prime}\) are two different tubular neighborhoods, we may define a map from the set of letters in \(w_{(D, H)}\) into itself, simply by mapping each letter represented by an intersection of the arc \(\gamma\) with \(\partial U\) to the letter represented by the corresponding intersection of \(\gamma\) with \(\partial U^{\prime}\). It is easily seen that the assemblages defined by the two choices differ up to the action of this map and that this map is a composition of \(\iota\)-involutions, hence the two assemblages are \(\iota\)-equivalent.

By the very definition, the following is easily proved: Proposition 1.38. If \(F, F^{\prime} \in E_{\infty}^{\beta}(f)\) are right equivalent extensions of \(f\), By this Proposition \(\mathbf{A}_{2}^{\beta}\) defines a map: \(\mathbf{A}^{\beta}: E_{\infty}^{\beta}(f) / \tilde{\sim} \rightarrow \mathcal{A}_{m}^{\beta}(w) / \sim\). To conclude the proof of Theorem 1.34, it is enough to prove the following:

Proposition 1.39. The just defined map \(\mathbf{A}^{\beta}\) is a bijection. Proof. \(\mathbf{A}^{\beta}\) is injective. Let \(F: S \rightarrow \mathbf{N}\) and \(F^{\prime}: S^{\prime} \rightarrow \mathbf{N}\) be such that \(\mathbf{A}^{\beta}(F)=\mathbf{A}^{\beta}\left(F^{\prime}\right)\), then they induce the same deformation pair. By Proposition 1.11 there exist neighborhoods \(U\) and \(U^{\prime}\) of \(\coprod_{h=1}^{k} \mathbf{S}^{1}\) respectively in \(S\) and \(S^{\prime}\) and a diffeomorphism \(\varphi_{1}: U^{\prime} \rightarrow U\) such that \(\left.F^{\prime}\right|_{U^{\prime}}=\left(\left.F\right|_{U}\right) \circ \varphi_{1}\). On the other hand, \(\left.F\right|_{(S-U)}\) and \(\left.F^{\prime}\right|_{\left(S^{\prime}-U^{\prime}\right)}\) are two extension of \(f_{(D, H)}\) inducing the same class of assemblages in \(\mathcal{A}_{m}^{\beta}\left(\tilde{w}_{(D, H)}\right) / \boldsymbol{\xi}_{\beta}\); hence, by Theorem 0.18, there exists a diffeomorphism \(\varphi_{2}: S^{\prime}-U^{\prime} \rightarrow S-U\) such that \(\left.\left.F^{\prime}\right|_{\left(S^{\prime}-U^{\prime}\right)}=\left.F\right|_{( } S-U\right) \circ \varphi_{2}\). A local analysis shows that the two diffeomorphisms \(\varphi_{1}\) and \(\varphi_{2}\) paste together, defining a diffeomorphism \(\varphi: S^{\prime} \rightarrow S\) such that \(F^{\prime}=F \circ \varphi\).

To prove that \(\mathbf{A}^{\beta}\) is surjective we need the following: Lemma 1.40. If \(w\) has minimal assemblages then all cusps of \(f\) are negative.

Proof. By contradiction, suppose that \(f\) has a positive cusp; then every deformation of \(f\) has a positive curl, and then, by Lemma 0.22, \(\mathcal{A}_{m}^{\beta}\left(\tilde{w}_{(D, H)}\right)=\varnothing\) for all deformation pairs ( \(D, H\) ); by Remark 1.31, \(A_{m}^{\beta}(w)=\varnothing\).

Back to the proof of Theorem 1.34, let A = ((D, H), ,~) be a minimal B-assemblage for w. By the previous Lemma f has a coherent side; hence, by Proposition 1.11, there exists a local, excellent extension F1 of f, defined on a disjoint union of cylinders and Mobius bands M, such that F11aM = f(D,H)By Proposition 1.28,~A is a minimal 0-assemblages hence, by Theorem 0.18, there exist a surface S and an immersion F2 : \(S_{2013}\)~ N such that 8§ = and = Once again a local analysis shows that f(D,H).

\(M\) and \(\tilde{S}\) can be pasted along the boundary, so that the map \(F\) obtained past ing \(F_{1}\) and \(F_{2}\) is an excellent map extending \(f\) and, by construction, \(\mathbf{A}^{\beta}(F)=\mathbf{A}\).

2. - Factorization of excellent mappings

Classically, the problem to find out a factorization F = 7r o F1 for an excellent map F : 6' -~ N into a given line bundle E -~ N, was posed with the requirement that F1 should be an immersion; this problem was firstly solved by Haefliger [11], in the case N = JR.2 and E = II~3 ; successively Millet [15] remarked that Hafliger's proof also worked in the case of an arbitrary surface N and the trivial bundle (E = N x R). Finally in [12] the author generalized Hafliger's methods to the general case: let C denote a component of IF, and put cC - #{cusp points in C}, according as C has a trivial normal bundle or not and finally ec = ::i: 1 according as the trivial bundle or not. With these notations the following holds:

Theorem. \(F\) is factorizable into \(\mathbf{E}\) by means of an immersion if and only if, for all components \(C\) of \(\Sigma_{F},(-1)^{c_{C}} \nu_{C} \varepsilon_{C}=1\).

As announced in the introduction, in this section we deal with the problem of finding a factorization \(F=\pi \circ F_{1}\), with \(F_{1}\) an embedding. Let us begin with some lemmas and propositions wich we will use later.

From now on the set of critical points and the apparent contour of an excellent map will be denoted by \(\Sigma\) and \(\Gamma\).

Lemma 2.1. Let \(F: S \rightarrow \mathbf{N}\) be an excellent map. Let \(D \subset \mathbf{N}\) be an embedded disk such that: \(\partial D\) is in general position with respect to \(\Gamma ; D\) contains no cusp; \(D \cap \Gamma\) is a union of simple arcs. Then \(F\) restricted to any component of \(F^{-1}(D)-\Sigma\) is 1-1.

Proof. Fix a point \(\infty \notin D\) and a vector field \(X\) on \(\mathbf{N}\), vanishing at most at \(\infty\). Let \(C\) be a connected component of \(F^{-1}(D)-\Sigma\) and let \(C_{\varepsilon}\) be obtained by removing a small neighborhood of \(\Sigma\). The following facts hold: \(\left.F\right|_{C_{\varepsilon}}\) is an immersion; \(\partial C_{\varepsilon}\) consists of branches of \(F^{-1}(\partial D)\) and arcs parallel to \(\Sigma\); if \(k\) is the number of boundary components of \(\partial C_{\varepsilon}\), then \(F\left(\partial C_{\varepsilon}\right)\) consists of \(k\) loops obtained by arcs of \(\partial D\) and branches of \(\Gamma\). Endowing these loops with the side induced by the immersion, it is easy to see that each of these loops has rotation number greater than or equal to 1, hence \(R_{X}\left(\left.F\right|_{\partial C_{\varepsilon}}\right) \geq k\). On the other hand, by (0.1) of §0, we have \(R_{X}\left(\left.F\right|_{\partial C_{\varepsilon}}\right)=\chi\left(C_{\varepsilon}\right) \leq 1\); hence \(k=1, C_{\varepsilon}\) is a disk and \(\left.F\right|_{\partial C_{\varepsilon}}\) cannot have any crossing; hence \(\left.F\right|_{C_{\varepsilon}}\) is 1-1. The Thesis follows by an exhaustion argument.

Let \(R\) be a system of segments for \(\left.F\right|_{\Sigma}\), the set \(F^{-1}(R)\) consists of oriented arcs having at least the ending point on \(\Sigma \cup F^{-1}(\infty)\). Denote by \(H(F)\) the set of all such arcs starting from \(\Sigma \cup F^{-1}(\infty)\).

Remark 2.2. Since \(\omega \in \Omega\) is a closed loop based at \(\infty\), then \(F^{-1}(\Omega) \subseteq H(F)\).

Lemma 2.3. \(F\) restricted to each component of \(S-H(F)\) is injective. Proof. Let \(p, q \in S-H(F)\) be such that \(F(p)=F(q)\) and let \(\gamma:[0,1] \rightarrow S-H(F)\) be a path joining \(p\) and \(q\). It is not hard to see that we can suppose that \(p, q \in S-F^{-1}(R), \gamma([0,1]) \subset S-F^{-1}(R)\) and \(F \circ \gamma\) is a simple curve in general position with respect to \(\Gamma\) (see [10]). Let \(D \subset \mathbf{N}\) be the disk bounded by \(F \circ \gamma\). Since \(\partial D \cap R=\varnothing\), then \(D \cap R=\varnothing\), and since \(R\) is a system of segments We now state two topological lemmas, whose proof is an easy exercise. Lemma 2.4. Let \(X\) be an arcwise connected topological space, and let \(U, V\) be two open subsets such that \(X=U \cup V\) and \(U \cap V\) is not arcwise Lemma 2.5. Let \(U_{1}, \ldots, U_{n}, n \geq 3\), be open subsets of a topological space \(X\). If \(U_{i} \cap U_{j} \neq \emptyset \Leftrightarrow|i-j| \equiv 0,1(\bmod n)\), then either \(\bigcap_{i=1}^{n} U_{i} \neq \emptyset\), and in this

From the above two lemmas, we have the following: Proposition 2.6. Let \(U_{1}, \ldots, U_{n}(n \geq 3)\) arcwise connected, open subsets of the topological space \(X\), satisfying the hypothesis of Lemma 2.5; then either \(n=3\) and \(\bigcap_{i} U_{i} \neq \varnothing\), or \(H_{1}\left(\bigcup_{i} U_{i}\right) \neq 0\).

From now on, we will denote by \(C\) the set of connected components of \(S-H(F)\).

Since \(\mathbf{\Omega}\) is a minimal system of generators of \(\pi_{1}(\mathbf{N}, \infty), \mathbf{N}-\mathbf{\Omega}\) is diffeomorphic to an open disk; hence, by Lemma 2.3, we can say that \(C\) is a planar surface, that is to say it is an open disk with some holes. By contradiction, assume \(F(C)\) is not an open disk, hence \(F(C)\) has at least two boundary components, furthermore the boundary of \(F(C)\) consists of branches of \(\Gamma\) and branches of segments of \(R\). Let \(\gamma\) be an interior component of \(\partial F(C)\). If \(\gamma\) contains a branch of the segment \(r\), since the segment ends at \(\infty\), the segment itself cuts \(F(C)\) from boundary to boundary. Since \(C\) does not contain \(\operatorname{arcs}\) in \(F^{-1}(R)\) starting and ending at the boundary, this is a contradiction. If \(\gamma\) consists of branches of \(\Gamma\) only, then it bounds a connected component of \(\mathbf{N}-\Gamma\). The segment starting from this connected component leads to a contradiction as in the previous case.

proposition 2.8. Let \(C_{1}, C_{2} \in C\), then \(F\left(C_{1}\right) \cap F\left(C_{2}\right)\) is connected.

Proof. By contradiction, suppose \(F\left(C_{1}\right) \cap F\left(C_{2}\right)\) is disconnected. By Lemma 2.4, \(F\left(C_{1}\right) \cup F\left(C_{2}\right)\) has at least two boundary components. Contradiction follows as in the previous proposition.

Factorization. Let \(S\) and \(\mathbf{N}\) be surfaces and \(\mathbf{E} \xrightarrow{\boldsymbol{\pi}} \mathbf{N}\) a line bundle.

Definition 2.9. We say that a map \(F: S \rightarrow \mathbf{N}\) is factorizable into \(\mathbf{E}\) if there exists an embedding \(F_{1}: S \rightarrow \mathbf{E}\) such that \(F=\pi \circ F_{1}\).

REMARK 2.10. Finding a map F1 such that F = 7r o F1 is the same as finding a section u, of the line bundle F*E induced by \(F(seethediagrambelow)\), hence F is factorizable into E if and only if there exists a section u : S --+ F*E of the induced bundle, such that 7r*F o a is an embedding. If E = N x R is the trivial bundle, this condition reduce to the existence of a function h : S -~ R such that (F, h) : ,S -~ N x R is an embedding. We will call such a function a height for F.

Remark 2.11. Suppose \(F: S \rightarrow \mathbf{N}\) and \(F^{\prime}: S^{\prime} \rightarrow \mathbf{N}\) are right equivalent maps; it is easily seen that \(F\) is factorizable into \(\mathbf{E}\) if and only if \(F^{\prime}\) is. For excellent maps this means that, in some sense, factorizability conditions "must" be contained in the assemblage associated to the map.

We now fix our attention on finding factorizability conditions for excellent mappings. Let \(F^{-1}(\infty)=\left\{p_{1}, \ldots, p_{\beta}\right\}\) and let \(D_{1}, \ldots, D_{\beta}\) be disks in \(S\) such that \(p_{i} \in D_{i}\) and \(\left.F\right|_{\partial D_{1}}=g_{i}\) ( \(g_{i}\) as in definition 0.10), and let \(\tilde{S}=S-\bigcup_{i=1}^{\beta} \dot{D}_{i}\),

Proposition 2.12. \(F\) is factorizable into \(\mathbf{E}\) if and only if \(\tilde{F}\) is.

Proof. Let \(\tilde{F}_{1}: \tilde{S} \rightarrow \mathbf{E}\) be an embedding such that \(\pi \circ \tilde{F}_{1}=\tilde{F}\), and \(U_{\infty}\) an open ball around \(\infty\) such that \(U_{\infty} \cap \Gamma=\varnothing\), and \(U_{\infty}\) contains all curves \(g_{i}\). Let \(U_{i}\) we may suppose that \(h\) assumes constant value \(c_{i}\) on \(U_{i}-D_{i}\), such that \(c_{i} \neq c_{j}\) for all \(i \neq j\). Extend \(\tilde{F}_{1}\) to the required embedding \(F_{1}\), defining \(F_{1}(p)=\Phi^{-1}\left(F(p), c_{i}\right)\) The trivial bundle. Let us first consider the case \(\mathbf{E}=\mathbf{N} \times \mathbb{R}\). In Remark 2.10 Proposition 2.13. Let \(h\) be an height function for \(F\); then for all \(C_{1}\), \(C_{2} \in C\) such that \(F\left(C_{1}\right) \cap F\left(C_{2}\right) \neq \varnothing\), one (and only one) of the following two holds:

PROOF. Clearly at most one of the two holds. By contradiction, suppose both are false, then there exist XI, \(X \in C\) Cl, yl, \(y \in E\) C2 such that \(F(x1)\) = \(F(Y1)\) = zi, \(F(X2)\) = \(F(y2)\) = Z2 and h(yi), h(X2) &#x3E; h(y2). By Proposition 2.8 \(F(C1)\) n \(F(C2)\) is connected, let 1 : [0,1] -~ \(F(Ci)\) n \(F(C2)\) be a path joining zi and z2, and let 11 and 12 be its liftings to 01 and C2 respectively (these liftings exist by Lemma 2.3). Let hi = h o Ii, then hl(O) = h(xl) h2(0), and = h(X2) &#x3E; h(y2) - h2(1), therefore there exists to \(E(0,1)\) such that = h2(to). Call pl E Ci, P2 = - 2(tO) E C2, then pi fp2 and \(F(pi)\) = \(F(p2)\), = h(p2), that is a contradiction. p Suppose \(h\) is a height for \(F\). We define a structure of oriented graph on the set \(\mathcal{C}\), as follows: say that \(C_{1}, C_{2} \in \mathcal{C}\) are joined by an edge pointing to \(C_{2}\) ( \(C_{1} \rightarrow C_{2}\) ) if and only if \(C_{1}\) and \(C_{2}\) verify (1) in Proposition 2.13. We denote by \(L(h)\) this oriented graph.

PROPOSITION 2.14. The graph \(L(h)\) has no loops. Proof. By contradiction, let \(C_{1} \rightarrow C_{2} \rightarrow \ldots \rightarrow C_{n} \rightarrow C_{1}\) be a loop of minimal length. Observe that \(F\left(C_{i}\right) \cap F\left(C_{j}\right) \neq \emptyset \Rightarrow|i-j| \equiv 0,1(\bmod n)\), on the contrary we could use Proposition 2.13 to find a shorter loop. By Proposition 2.6, As in the definition of the word of a curve, for all \(r \in R\), fix an orientation of a small tubular neighborhood of \(r-\infty\).

Proposition 2.15. Let \(C_{1}, C_{2}, C_{3}, C_{4} \in C\) and \(\ell, \ell_{1}, \ell_{2}\), be edges of the graph \(H(F)\). The following two hold:

- (A) suppose that Ci, C2 paste along (i.e. 01.~) and then either C3 and C2-C3 or C3-C1 and C3-C2;

- (B) suppose that Ci, C2 paste along that C3, C4 paste along t2 and Let r E R be the segment containing \(F(ti)\), and suppose \(F(Ci)\), \(F(C3)\) be on the left of r and \(F(C2)\), \(F(C4)\) on its right, then: either Ci-C3 and C2-C4 or C3-C1 and C4-C2.

Proof. Let \(C_{1}, C_{2}, C_{3}\) be as in (A); then \(F\left(C_{1}\right) \cap F\left(C_{3}\right)\) and \(F\left(C_{2}\right) \cap F\left(C_{3}\right)\) are both not empty, hence some edge of \(L(h)\) joins \(C_{1}, C_{3}\) and \(C_{2}, C_{3}\). By contradiction, suppose (A) is false, say \(C_{1} \rightarrow C_{3}\) and \(C_{3} \rightarrow C_{2}\). Let \(z \in F\left(C_{3}\right) \cap F(\ell)\) and let \(p \in \ell\) such that \(F(p)=z\). Take a small neighborhood \(U\) of \(p\), such that \(U \cap C_{3}=\varnothing\) and \(F(U) \subset F\left(C_{3}\right)\), and a path \(\gamma\) in \(U\) joining two points \(p_{1} \in C_{1}, p_{2} \in C_{2}\). Let \(\gamma_{3}\) be the lifting of \(F \circ \gamma\) to \(C_{3}\). Clearly \(F \circ \gamma_{3}=F \circ \gamma\), but \(C_{1} \rightarrow C_{3} \Rightarrow h(\gamma(0))<h\left(\gamma_{3}(0)\right)\) and \(C_{3} \rightarrow C_{2} \Rightarrow h(\gamma(1))>h\left(\gamma_{3}(1)\right)\). As in the previous proposition this fact leads to a contradiction. A completely analogous argument proves (B).

Proposition 2.14 and Proposition 2.15 give necessary conditions in order that an excellent map F may be factorizable. We will prove that these conditions are also sufficient, that is to say the following theorem holds:

THEOREM 2.16. Let \(F: S \rightarrow \mathbf{N}\) be an excellent map; then \(F\) is factorizable into \(\mathbf{N} \times \mathbb{R}\) if and only if the set \(C\) can be given a structure of oriented graph with no loops, satisfying conditions (A) and (B) of Proposition 2.15.

Proof. Let \(\tilde{S}\) be as in Proposition 2.12. We proceed in two steps: Step 1: definition of a height on \(\tilde{S}\) minus a tubular neighborhood of \(\Sigma\); Step 2: extension of such a height to the tubular neighborhood. The thesis will follow by Proposition 2.12.

Let \(L\) be the graph in the assumption; since it has no loops, than → extends to an ordering on \(C\), say \(\prec\), and clearly such an ordering fulfills (A)

- Step 1. Let U be a tubular neighborhood of E such that is a generic curve and denote S' = S-U, r' = \(F(aS')\) and if C E C denote C' = C n S'. Let be a ball around oo, contained in the interior side of all curves gi (see definition 0.10), that is to say \(F(S)\) c (N-Y~ ). For all r E R fix an oriented neighborhood Yr and a diffeomorphism Vr ---+ [0, tr] x [-1, 1], such that:

- Blr f=r';

- Vr E R, Yr contains no crossings of F';

- Vr Ei R, (p,(r) 9 10, trl X f 01;

- Vr E R, (r U r') n Yr is connected (this fact and (2) say that Vr contains only branches of T' intersecting r);

- if rr,j is the component of r' n v, which intersects r at the jth point, counting according to the orientation of r, then Ij I x [-1,1];

- br E R, pr and pr r : r R are orientation-preserving.

Let \(V=\bigcup_{r \in R} V_{r}\), for any proper edge \(\ell\) of \(H(F)\), denote by \(U_{\ell}\) the connected component of \(F^{-1}(V) \cap S^{\prime}\) containing \(\ell \cap S^{\prime}\), and by \(r(\ell)\) the segment containing \(F(\ell)\); denote by \(s(\ell)\) and \(t(\ell)\) the two indexes such that \(C_{s(\ell)}, C_{t(\ell)} \in C\) are the two components pasting along \(\ell\), the former on the left of \(\ell\), the latter on the right (left and right with respect to the orientations induced by \(F\) ). For all \(C \in C\) denote \(C^{*}=\left(C \cap S^{\prime}\right)-\bigcup_{\ell} U_{\ell}\). Finally let \(\psi: \mathbb{R} \times[-1,1] \rightarrow \mathbb{R}\) be a \(C^{\infty}\) function such that: \(\psi(x, y)=0, \forall y \in[-1,-2 / 3] ; \psi(x, y)=1, \forall y \in[2 / 3,1]\) and function such that: \(\psi(x, y)=0, \forall y \in[-1,-2 / 3] ; \psi(x, y)=1, \forall y \in[2 / 3,1]\) and \(\psi(x, y) \in[0,1], \forall x, y\). We define the function \(h_{1}: S^{\prime} \rightarrow \mathbb{R}\),

$$
h_{1}: x \longmapsto \begin{cases}s & \text { if } x \in C_{s}^{*} \tag{2.1}\\ s(\ell)+(t(\ell)-s(\ell)) \psi\left(\varphi_{r(\ell)}(F(x))\right) & \text { if } x \in U_{\ell}\end{cases}
$$

Clearly such a function is of class \(C^{\infty}\). We now prove that \(\left(\left.F\right|_{S^{\prime}}, h_{1}\right): S^{\prime} \rightarrow \mathbf{N} \times \mathbb{R}\) is injective. Let \(x \neq y \in S^{\prime}\), three cases appear:

- (I) z e CJ and

(III) \(x \in U_{\ell}\) and \(y \in U_{\ell^{\prime}}\). Case (I). If \(s=s^{\prime}\), by Lemma 2.3, \(F(x) \neq F(y)\); if \(s \neq s^{\prime}\), clearly \(h_{1}(x) \neq h_{1}(y)\).

Case (I). If \(s=s^{\prime}\), by Lemma 2.3, \(F(x) \neq F(y)\); if \(s \neq s^{\prime}\), clearly \(h_{1}(x) \neq h_{1}(y)\). by (A), this means either \(C_{s} \prec C_{s(\ell)}\) and \(C_{s} \prec C_{t(\ell)}\) or \(C_{s(\ell)} \prec C_{s}\) and \(C_{t(\ell)} \prec C_{s}\), that is to say either \(s<s(\ell)\) and \(s<t(\ell)\) or \(s(\ell)<s\) and \(t(\ell)<s\). By definition of \(h_{1}, \min \{s(\ell), t(\ell)\}<h_{1}(y)<\max \{s(\ell), t(\ell)\}\), hence \(s=h_{1}(x) \neq h_{1}(y)\). Case (III). Suppose \(F(x)=F(y)=p\); the \(V_{r}\) 's are pairwise disjoint, hence Case (III). Suppose \(F(x)\) - \(F(y)\) = p; the Vr's are pairwise disjoint, hence r(.~) - T-(~), and since \(F(.~)\) n \(F(.~')\) ~ ~. By (B), either C~,(t) and Ct(t) or \(C_{s}(l')\) -. and-Ct(~~, that is to say either s(£) s(~') and t(£') or \(S(l')\) s(£) and t(t') Using the definition of hl, an easy computation shows that either h2(y) or h2(y) h, (x). This ends the first step.

Step 2. For the sake of simplicity, we suppose \(\Sigma\) is connected, it will be clear that the same proof also works in the general case. Let \(U\) as above and put

$$
M= \begin{cases}\mathbb{R} \times[-1,1] /{ }_{(x, y)=(x+1, y)} & \text { if } U \text { is orientable } \\ \mathbb{R} \times[-1,1] /{ }_{(x, y)=(x+1,-y)} & \text { if } U \text { is non-orientable }\end{cases}
$$

Let \(\varphi: M \rightarrow U\) be a diffeomorphism such that \(\varphi(\{y=0\})=\Sigma\) and the Denote by \(D_{j}\) both the generic component of \(M-\varphi^{-1}(H(F))\) and the corresponding component of \(U-H(F)\); and by \(C_{i(j)} \in C\) the component of \(S-H(F)\) containing \(D_{j}\). The following two lemmas are an immediate consequence of (A) and (B) respectively.

LEMMA 2.17. Let t E [0, 1) be a cusp point (with the just said notations, either t = ti or t = BJ) and let Dj¡(t), Dj3(t) be the three components having (t, 0) in their closure. Let Dj¡(t) be the one opposed to the edge starting at (t, 0) (see Fig. 12); then: either Ci(j2(f)) or -

![Figure 12](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-12-p025.png)

*Figure 12: *

![Figure 13](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-13-p025.png)

*Figure 13: *

Lemma 2.18. Let \(D_{j_{1}\left(z_{l}\right)}, D_{j_{2}\left(z_{l}\right)}, D_{j_{3}\left(z_{l}\right)}, D_{j_{4}\left(z_{l}\right)}\) the four connected components having \(\left(z_{l}, 0\right)\) in their closure, numbered as in Fig. 13; then either \(C_{i\left(j_{1}\left(z_{l}\right)\right)} \prec Denote \(h_{1,-1}(t)=h_{1} \circ p(t,-1), h_{1,1}(t)=h_{1} \circ p(t, 1)\). By the previous two lemmas, and the way we constructed \(h_{1}\) in Step 1, we can suppose \(h_{1,1}\) and \(h_{1,-1}\) have the following properties:

- h1,1(t + 1) = h1,1(t) and h1,-1(t + 1) = h1,-1(t) if U is orientable, otherwise hI, 1 (t + 1) = h1,-1 (t) and h1,-1 (t + 1) =

- there exists 6 &#x3E; 0 such that:

- i is strictly monotonic on [ti - ê, ti + ~] and [zl + c];

- h1,-1 is strictly monotonic on [sj + 61 and [zl-6, z, + 61;

- 1 e 1 assume constant values on the other intervals;

- b't E [0, 1), h 1,1 (t) = ~ either t = ti or t = sj for some i or j.

These conditions imply that we can extend h, in a neighborhood [t-S, t + S] x [-1,1] of each cusp point (t, 0), as suggested in Fig. 14, in such a way that (F, \(h_{1}\)) : [t-6, f + 6] x [ -1,1] - N x R is an embedding. Moreover, let as in Lemma 2.17, be the three components having (I, 0) in their closure and we can suppose that

$$
\begin{equation*} m(\bar{t}) \leq h_{1}(t, y) \leq M(\bar{t}) \quad \forall(t, y) \in[\bar{t}-\delta, \bar{t}+\delta] \times[-1,1] ; \tag{2.2} \end{equation*}
$$

and, up to taking \(U\) and \(\delta\) small enough, that:

$$
\begin{equation*} F\left(\left[\bar{t}_{1}-\delta, \bar{t}_{1}+\delta\right] \times[-1,1]\right) \cap F\left(\left[\bar{t}_{2}-\delta, \bar{t}_{2}+\delta\right] \times[-1,1]\right)=\varnothing . \tag{2.3} \end{equation*}
$$

for all pairs of cusp points \(\left(\bar{t}_{1}, 0\right),\left(\bar{t}_{2}, 0\right)\).

Lemma 2.19. The mapping \(\left(F, h_{1}\right): S^{\prime} \cup \bigcup_{\bar{t}}([\bar{t}-\delta, \bar{t}+\delta] \times[-1,1]) \rightarrow \mathbf{N} \times \mathbb{R}\) is an embedding.

Proof. By the way we extended \(h_{1}\), the map is clearly an immersion. By contradiction, let \(x_{1}, x_{2} \in S^{\prime} \cup \bigcup_{\tilde{t}}[\bar{t}-\delta, \bar{t}+\delta] \times[-1,1]\) be such that \(F\left(x_{1}\right)=F\left(x_{2}\right)\) \([\bar{t}-\delta, \bar{t}+\delta] \times[-1,1]\) is injective and (2.3), we have that \(x_{1} \in[\bar{t}-\delta, \bar{t}+\delta] \times[-1,1]\) and \(x_{2} \in S^{\prime}\). Furthermore \(h_{1}\) assumes constant value in a neighborhood of \(x_{1}\); let \(C_{i}\) be the component of \(S^{\prime}-H(F)\) containing it, this means that \(F\left(C_{i}\right)\) contains the cusp corresponding to \((\bar{t}, 0)\), hence \(F\left(C_{i}\right) \cap F\left(D_{j_{l}(\bar{t})}\right) \neq \varnothing\) for all \(l=1,2,3\). Use twice (A) and get either \(i<m(\bar{t})=\min _{l} i\left(j_{l}(\bar{t})\right)\) or \(i>M(\bar{t})=\max _{l} i\left(j_{l}(\bar{t})\right)\). Using (2.2) and the fact that \(h_{1}\left(x_{2}\right)=i\), we get a contradiction.

![Figure 14](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-14-p026.png)

*Figure 14: *

![Figure 15](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-15-p026.png)

*Figure 15: *

![Figure 16](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-16-p026.png)

*Figure 16: *

We are only left to extend h 1 over U-\(U([t-6,I+6]x[-1,1])\). Where both hi,i and h1,-1 assume constant values, an extension is easily found as suggested in Fig. 15. Furthermore, conditions (2) and (3) ensure that we can define local extensions of h I over the sets [zl - ê, Zl + e] x [-1,1], in such a way that the value of such an extension at the point (t, y) is between hl,i(t) and (see Fig. 16). Clearly all such extensions can be pasted to give a function h : \(S_{2013}\)~ R. An argument very much like the one used to prove the f previous lemma, proves the following too:

Lemma 2.20. The map \((F, h): S \rightarrow \mathbf{N} \times \mathbb{R}\) is injective.

Since (F, h) is an immersion, this concludes the proof of Theorem 2.16. 0 Now, we give a description of line bundles over surfaces, fitting in with our purpose to find factorability conditions for excellent mappings.

Line bundles. Let \(\mathbf{N}_{1}\) be a connected, compact surface with one boundary component and \(\pi_{1}: \mathbf{E}_{1} \rightarrow \mathbf{N}_{1}\) a line bundle. Suppose \(\left.\mathbf{E}_{1}\right|_{\partial \mathbf{N}_{1}}\) is the trivial bundle definition 2.21. We call closure of \(\mathbf{E}_{1}\) the bundle constructed this way, and we denote it by \(\widehat{\mathbf{E}}_{1}\).

Since \(\left.\mathbf{E}\right|_{D}\) is the trivial bundle, we have the following:

Proposition 2.22. Every line bundle over \(\mathbf{N}\) is the closure of some bundle over a compact, connected surface with one boundary component.

Since the only line bundle over the sphere is the trivial one, from now on we will suppose that \(g(\mathbf{N})>0\). Call weighted genus of a compact, connected surface \(\mathbf{N}\), the number \(h(\mathbf{N})=2 g(\mathbf{N})\) if \(\mathbf{N}\) is orientable, \(h(\mathbf{N})=g(\mathbf{N})\) otherwise. It is a classical fact in topology that a surface \(\mathbf{N}\) is the quotient of a \(2 h(\mathbf{N})\)-gon, by pairwise identification of its edges, and such a polygon can be found by cutting \(\mathbf{N}\) along a minimal system of generators of its fundamental group. Fix the following data: a point \(\infty \in \mathbf{N}\); a set \(\Omega=\left\{\omega_{i}\right\}\) of smooth curves, as in (2) Proposition 2.23. The line bundle \(\left.\mathbf{E}_{\rho}\right|_{\partial \mathbf{N}_{1}}\) is trivial.

Proof. Such a bundle is obtained by successively pasting \(2 h\) copies of \([0,1] \times \mathbb{R}\), by means of mappings of the following two kinds: \((1, t) \mapsto(0, t)\), \((1, t) \mapsto(0,-t)\), and both kinds of such identifications are even in number.

By the previous proposition and Proposition 2.22 we see that every distribution of weights \(\rho\) over \(\Omega\) generates a line bundle over \(\mathbf{N}\), simply by taking the closure \(\widehat{\mathbf{E}}_{\rho}\) of the just-constructed bundle \(\mathbf{E}_{\rho}\). Simple technical arguments prove the following:

Proposition 2.24. If \(\mathbf{E}\) is a line bundle over \(\mathbf{N}\) then there exists a distribution of weights \(\rho\) over \(\Omega\) such that \(\mathbf{E}\) is isomorphic to \(\widehat{\mathbf{E}}_{\rho}\).

The general case. Turn back to our problem. Let F : S-N be an excellent-map and E -&#x3E; N a line bundle. Let R be a system of segments, S and N1 = N be as before. By Proposition 2.24 we can suppose that E = i%bp for some distribution of weights p; hence, by Proposition 2.12 and Remark 2.10, our problem is the same as finding a section u of S, such that 1r;F o o, is an embedding. First of all, let us try to understand the meaning of finding a section of the line bundle F*Ep. Let S' be the surface obtained from,S by cutting along P-\(I(K2)\), and let ~ : S' -~ ,S be the quotient map given by the cut. Let ~p : PN1 --&#x3E; N1 be the mapping generated by the cut of N1 along Q; then there exists a unique map F' : S' PN1 such that p o F' = F o ~. By this fact, the way Ep was defined and thanks to the following commutative diagram

we see that finding a section of \(\tilde{F}^{*} \mathbf{E}_{\rho}\) is the same as finding a function \(h: S^{\prime} \rightarrow \mathbb{R}\), such that:

$$
\begin{equation*} h\left(x_{1}\right)=\rho_{i} h\left(x_{2}\right) \text { if } F\left(\xi\left(x_{1}\right)\right)=F\left(\xi\left(x_{2}\right)\right) \in \omega_{i} \quad \forall x_{1}, x_{2} \text { s.t. } \xi\left(x_{1}\right)=\xi\left(x_{2}\right) \tag{2.4} \end{equation*}
$$

and satisfying the anologous conditions on the differentials. We will denote by \(\sigma_{h}\) the section of \(\tilde{F}^{*} \mathbf{E}_{\rho}\) defined by \(h\). Clearly the following holds:

Proposition 2.25. The mapping \(\pi^{*} \tilde{F} \circ \sigma_{h}: \tilde{S} \rightarrow \mathbf{E}_{\rho}\) is an embedding if and only if \(\left(F^{\prime}, h\right): S^{\prime} \rightarrow P_{\mathbf{N}_{1}} \times \mathbb{R}\) is.

We will call such a function \(h\) a strange height for the mapping \(F_{\tilde{c}}\). Let us introduce some more notation. Let \(\tilde{H}(F)=(H(F) \cap \tilde{S}) \cup \partial \tilde{S}\), and \(H^{\prime}(F) \subset S^{\prime}\) be the set \(H^{\prime}(F)=\xi^{-1}(\tilde{H}(F))\). Denote by \(C\) the set of connected components of \(S-H(F)\), by \(\tilde{C}\) the set of components of \(\tilde{S}-\tilde{H}(F)\) and finally by \(C^{\prime}\) the set of components of \(S^{\prime}-H^{\prime}(F)\). It is immediate that inclusion \(\tilde{S} \hookrightarrow S\) gives a bijection between \(\widetilde{C}\) and \(\mathcal{C}\); while \(\underset{\sim}{\xi}: S^{\prime} \rightarrow \widetilde{S}\) gives a bijection between \(\mathcal{C}^{\prime}\) and \(\tilde{\mathcal{C}}\). For all \(C \in \mathcal{C}\) denote by \(\tilde{C} \in \tilde{\mathcal{C}}\) and by \(C^{\prime} \in \mathcal{C}^{\prime}\) the corresponding components (i.e. \(\tilde{C}\) is the interior of \(C \cap \tilde{S}\) and \(C^{\prime}\) is the component such that Proposition 2.26. Let \(C_{1}, C_{2} \in \mathcal{C}\); then \(F\left(C_{1}\right) \cap F\left(C_{2}\right) \neq \varnothing\) if and only if Proof. The second equivalence is immediate, the first follows from the fact that if \(F\left(C_{1}\right) \cap F\left(C_{2}\right) \neq \emptyset\) and \(F\left(\tilde{C}_{1}\right) \cap F\left(\tilde{C}_{2}\right)=\emptyset\) then \(F\left(C_{1}\right) \cap F\left(C_{2}\right) \subset U_{\infty}\) and the fact that \(\partial\left(F\left(C_{1}\right) \cap F\left(C_{2}\right)\right)\) contains branches of \(\Gamma\), while \(U_{\infty} \cap \Gamma=\varnothing\).

PROPOSITION 2.27. Let Cl, C2 Ei C; then and are connected.

Let \(h\) be a strange height for the excellent map \(F\); by the same arguments used in the proof of Proposition 2.13, the following can be shown:

Proposition 2.28. Let \(C_{1}^{\prime}, C_{2}^{\prime} \in \mathcal{C}^{\prime}\) be such that \(F^{\prime}\left(C_{1}^{\prime}\right) \cap F^{\prime}\left(C_{2}^{\prime}\right) \neq \varnothing\). One of the following two holds:

- y Ei C2 if \(F(x)\) = \(F(y)\) then

- \(F(x)\) = \(F(y)\) then

As in the case of the trivial bundle we give a structure of oriented graph to the set \(C\), saying \(C_{1} \rightarrow C_{2}\) if and only if the corresponding components \(C_{1}^{\prime}\), \(C_{2}^{\prime} \in C^{\prime}\) satisfy condition (1). We call such a graph the graph of \(h\) and denote it by \(L(h)\).

REMARK 2.29. By Proposition 2.26 we see that two components \(C_{1}, C_{2} \in \mathcal{C}\) are joined by an edge if and only if \(F\left(C_{1}\right) \cap F\left(C_{2}\right) \neq \varnothing\), hence the situation is in all similar to the one we had dealing with the trivial bundle.

As in the case of the trivial bundle, the following is proved:

PROPOSITION 2.30. The graph \(L(h)\) has no loop. Denote \(\Omega^{-}=\{\omega \in \Omega \mid \rho(\omega)=-1\}\), an analogue of Proposition 2.15 holds in this case too.

Proposition 2.31. Let \(h\) be a strange height for \(F\), and let \(C_{1}, C_{2}\), \(C_{3}, C_{4} \in C, \ell, \ell_{1}, \ell_{2}\) be proper edges of \(H(F)\); the followings hold:

- (A 1) suppose that Cl, C2 paste (i.e. 0, and then either Ci-C3 and C2 ~ C3 or C3 --+ C1 and C3 ~ C2;

- (Bl) suppose that Cl, C2 paste along fl, C3, ~4 paste along t2 and Let r Ei R be the segment containing and suppose that \(F(CI)\), \(F(C3)\) are on the left of rand \(F(C2)\), \(F(C4)\) on its right; then:

if r c R-Q' either C3 and C2 -~ C4 or C3-C1 and C4-C2; if r E S~- either C3 and C4 --+ C2 or C3-C1 and C2-C4.

Proof. Observe that a situation as in (A1) occurs only if \(F(\ell)\) is contained either in \(\Gamma\) or in \(R-\Omega\); hence the same argument used to prove (A) of Proposition 2.15 proves (A1) too. We now prove (B1). If \(F\left(\ell_{1}\right)\) and \(F\left(\ell_{2}\right)\) are contained in some segment \(r \in R-\Omega\), as in the previous case, the proof is the same as for Proposition 2.15; hence suppose \(F\left(\ell_{1}\right), F\left(\ell_{2}\right) \subset \omega \in \Omega\), and let \(x_{1} \in \ell_{1}, x_{2} \in \ell_{2}\) be such that \(F\left(x_{1}\right)=F\left(x_{2}\right)\). It is easily seen that we can suppose \(x_{1}, x_{2} \in \tilde{S}\). Let \(\ell_{1}^{\prime}, \ell_{1}^{\prime \prime}\) be the edges of \(H^{\prime}(F)\) such that \(\xi\left(\ell_{1}^{\prime}\right)=\xi\left(\ell_{1}^{\prime \prime}\right)=\ell_{1}\) and let \(\ell_{2}^{\prime}, \ell_{2}^{\prime \prime}\) be those such that \(\xi\left(\ell_{2}^{\prime}\right)=\xi\left(\ell_{2}^{\prime \prime}\right)=\ell_{2}\). The assumption in (B1) on the components \(C_{1}, C_{2}, C_{3}\) and \(C_{4}\) ensures that \(C_{1}^{\prime}, C_{2}^{\prime}, C_{3}^{\prime}\) and \(C_{4}^{\prime}\) verify the following:

$$
\begin{aligned} & \partial C_{1}^{\prime} \supset \ell_{1}^{\prime}, \partial C_{2}^{\prime} \supset \ell_{1}^{\prime \prime}, \partial C_{3}^{\prime} \supset \ell_{2}^{\prime}, \partial C_{4}^{\prime} \supset \ell_{2}^{\prime \prime} ; \\ & F^{\prime}\left(C_{1}^{\prime}\right) \cap F^{\prime}\left(C_{3}^{\prime}\right) \neq \emptyset, F^{\prime}\left(C_{2}^{\prime}\right) \cap F^{\prime}\left(C_{4}^{\prime}\right) \neq \emptyset . \end{aligned}
$$

Let \(x_{1}^{\prime} \in \ell_{1}^{\prime}, x_{1}^{\prime \prime} \in \ell_{1}^{\prime \prime}, x_{2}^{\prime} \in \ell_{2}^{\prime}, x_{2}^{\prime \prime} \in \ell_{2}^{\prime \prime}\) be such that \(\xi\left(x_{i}^{\prime}\right)=\xi\left(x_{i}^{\prime \prime}\right)=x_{i}\). It is not

$$
\begin{equation*} \gamma_{i}^{\prime}(1)=x_{i}^{\prime} \text { and } \gamma_{i}^{\prime \prime}(1)=x_{i}^{\prime \prime} \quad i=1,2 ; \tag{1} \end{equation*}
$$

$$
\forall t \neq 1 \quad \begin{cases}\gamma_{1}^{\prime}(t) \in C_{1}^{\prime}, & \gamma_{1}^{\prime \prime}(t) \in C_{2}^{\prime}, \tag{2}\\ \gamma_{2}^{\prime}(t) \in C_{3}^{\prime}, & \gamma_{2}^{\prime \prime}(t) \in C_{4}^{\prime} ;\end{cases}
$$

![Figure 17](/Users/evanthayer/Projects/paperx/docs/1994_surfaces_with_assigned_apparent_contour/figures/figure-17-p030.png)

*Figure 17: *

$$
g_{i}(t)=\left\{\begin{array}{ll} h\left(\gamma_{i}^{\prime}(t)\right) & \text { if } t \in[0,1] \\ \rho(\omega) h\left(\gamma_{i}^{\prime \prime}(t)\right) & \text { if } t \in[1,2] \end{array} \quad i=1,2 .\right.
$$

By definition of a strange height and (1), we see that \(g_{1}\) and \(g_{2}\) are continuous functions. Consider the two cases \(\omega \in \Omega^{+}=\Omega-\Omega^{-}\)and \(\omega \in \Omega^{-}\). In the first case, suppose by contradiction that \(C_{1}^{\prime} \rightarrow C_{3}^{\prime}\) and \(C_{4}^{\prime} \rightarrow C_{3}^{\prime}\). By definition of → and (2), (3), \(g_{1}(t)<g_{2}(t)\) for all \(t<1\) and \(g_{1}(t)>g_{2}(t)\) for all \(t>1\). This implies that \(g_{1}(1)=g_{2}(1)\), hence \(F^{\prime}\left(x_{1}^{\prime}\right)=F^{\prime}\left(x_{2}^{\prime}\right)\) and \(h\left(x_{1}^{\prime}\right)=h\left(x_{2}^{\prime}\right)\), contradicting the fact that \(\left(F^{\prime}, h\right)\) is injective. A similar argument concludes the proof in the second case too.

As in the case of the trivial bundle, Proposition 2.30 and Proposition 2.31 give necessary and sufficient conditions for the existence of a strange height for an excellent map F.

THEOREM 2.32. Let F : S-N be an excellent map, R a system of segments for and E = Ep a line bundle over N. Then F is factorizable into E if and only if C can be given a structure of oriented graph with no loops verifying (A 1) and (\(B_{l}\)) of Proposition 2.31.

PROOF. The proof is completely similar to that of Theorem 2.16. D REMARK 2.33. Repeating almost word by word the statements and proofs in this section, a factorizability theorem for generic immersions can be proved. More precisely, let \(S\) be a compact surfece with boundary, \(F: S \rightarrow \mathbf{N}\) a generic immersion and \(R\) a system of segments for \(\left.F\right|_{\partial S}\); denote \(G(F) \subset S\) the graph which consists of \(\partial S\) and of those arcs in \(F^{-1}(R)\) which have both vertices in \(\partial S \cup F^{-1}(\infty). G(F)\) is the 1-skeleton of a cell decomposition of \(S\) such that \(F\) restricted to the interior of each cell is one to one. Denote by \(C\) the set of 2-cells of such a decomposition.

Theorem 2.34. A generic immersion \(F\) is factorizable into \(\mathbf{E}=\widehat{\mathbf{E}}_{\rho}\) if and

## References

- S.J. BLANK, Extending immersions of the circle. Dissertation, Brandeis University, Waltam, Mass., 1967.

- V.L. CARRARA ZANETIC, Extensions of immersions in dimension two. Trabalhos do Departamento de Matemática 92 (1986), Universidade de S0103o Paulo, Instituto de Matemática e Estatitistica, S0103o Paulo.

- C. CURLEY-D. WOLITZER, Branched immersions of surfaces. Michigan Math. J. 33 (1986), 131-144.

- C.L. EZELL, Branched extensions of curves in compact manifold. Trans. Amer. Math. Soc. 259 (1980), 533-546.

- C.L. EZELL-M.L. MARX, Branched extensions of curves in oriented surfaces. Trans. Amer. Math. Soc. 259 (1980), 515-532.

- G.K. FRANCIS, Assembling compact riemann surfaces with given boundary curves and branch points on the sphere, Illinois J. Math. 20 (1976), 198-217.

- G.K. FRANCIS, Polymersions with nontrivial target. Illinois J. Math. 22 (1978), 161-170.

- G.K. FRANCIS-S.F. TROYER, Excellent Maps with Given Folds and Cusps. Houston J. Math. 3 (1977), 165-194.

- G.K. FRANCIS-S.F. TROYER, Continuation: Excellent Maps with Given Folds and Cusps. Houston J. Math. 8 (1982), 53-59.

- R.Z. GOLDSTEIN-E.C. TURNER, Extending immersions of the circle. Preprint, State University of New York at Albany, Department of Mathematics.

- A. HAEFLIGER, Quelques remarques sur les applications differentiables d'une surface dans le plan. Ann. Inst. Fourier 10 (1960), 47-60.

- D. LUMINATI, Factorizations of generic mappings between surfaces. Proc. Amer. Math. Soc. 118 (1993), 247-253.

- D. LUMINATI, Immersioni di superficie e contorni apparenti. Tesi di Dottorato. Dottorato di Ricerca in Matematica, Università di Pisa (1992).

- M.L. MARX, Extensions of normal immersions of S1 into R2. Trans. Amer. Math. Soc. 187 (1974), 309-326.

- K.C. MILLET, Generic smooth maps of surfaces. Topology Appl. 18 (1984), 197-215.

- R. PIGNONI, curves and Surfaces in Real Projective Space: an Approach to Generic Projections. Singularities, Banach Center Publication 20 (1988), 335-351.

- R. PIGNONI, Projections of Surfaces with a Connected Fold curve. Preprint, Università di Milano (1990).

- R. PIGNONI, On surfaces and they contours. Manuscripta Math. 72 (1991), 223-249.

- V. POENARU, Extension des immersions en codimension 1 (d'aprés Samuel Blank). Exposition 342, Séminaire Bourbaki 20 (196768).

- J.R. QUINE, A global theorem for singularities of maps between oriented 2-manifolds. Trans. Amer. Math. Soc. 236 (1978), 307-314.

- R. THOM, Les Singularités des Application Diffèrentiables. Ann. Inst. Fourier 6 (1955-1956), 43-87.

- H. WHITNEY, On singularities of mappings of Euclidean space. I. Ann. of Math. 62 (1955), 374-410. Dipartimento di Matematica Universita di Trento Via Sommarive, 1428050 Povo Trento, Italy
