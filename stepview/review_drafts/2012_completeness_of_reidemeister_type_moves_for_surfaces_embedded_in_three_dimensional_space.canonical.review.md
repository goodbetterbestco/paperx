# Completeness of Reidemeister-Type Moves for Surfaces Embedded in Three-Dimensional Space

[missing from original]

[missing from original]

## Abstract

In this paper we are concerned with labelled apparent contours, namely with appar- ent contours of generic orthogonal projections of embedded surfaces in \(\mathbb{R}^{3}\), endowed with a suitable information on the relative depth. We give a proof of the following theorem: there exists a finite set of elementary moves (i.e. local topological changes) on labelled apparent contours such that two generic embeddings in \(\mathbb{R}^{3}\) of a closed surface are isotopic if and only if their apparent contours can be connected using only smooth planar isotopies and a finite sequence of moves. This result, that can be obtained as a by-product of general results on knotted surfaces and singularity theory, is obtained here with a direct and rather elementary proof. Key words: Isotopic embedded surfaces, apparent contours, completeness, Reidemeister moves.

## 2010 Mathematics Subject Classification:

Primary 57R45; Secondary 57R52, 57R40.

## 1 Introduction

In knot theory it is well known that two link diagrams represent ambient isotopic knots or links, if and only if they are related by a finite number of local Reidemeister moves or their inverses. The diagram of a link is simply the orthogonal projection of the image of the link onto some plane, together with the knowledge of which strand goes over at each crossing. Up to a small perturbation of the link, transversal crossings are the only possible singularities of the diagram.

A similar question can be formulated for two-dimensional smooth closed (i.e. compact without boundary) manifolds \(M\) embedded in \(\mathbb{R}^{3}\), that is, understanding when two embedded surfaces can be deformed into each other by a smooth path of embeddings.

In analogy with the link diagram, we can rely on the apparent contour \(\operatorname{AppCon}(\varphi)\) of \(\varphi:=\pi \circ e: M \rightarrow \mathbb{R}^{2}\), i.e. the image of the singular points of a generic orthogonal projection \(\pi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{2}\) of an embedding \(e: M \rightarrow \mathbb{R}^{3}\). The apparent contour carries a natural orientation and leads to a graph similar to a link diagram, with possibly the addition of cusps (see e.g. [25]). If we also add a so-called Huffman labelling (see [15], [26], [7], [3]) which is a nonnegative integer attached to each arc, giving information about the relative depth of the corresponding fold with respect to the remaining preimages of the arc, an apparent contour provides complete information on the 3D embedding (up to compactly supported deformations of \(\mathbb{R}^{3}\) in the projection direction) [3]. In Section 3 we recall the main properties of the apparent contours needed in our paper.

It turns out that there are six basic moves (local change of topology) on the apparent contour that correspond to a general deformation of the embedded surface; they can be used in exactly the same way as the Reidemeister moves on link diagrams. Our aim is to show that this set of moves, namely \(K(fromtherussianwordkasanie\(=\)\) tangency \(), \mathrm{L}(\) lips \(), \mathrm{B}\) (beak-to-beak), \(C(cusp-fold)\), \(S(swallowtail)\) and \(T(triplepoint)\), is complete. This means that two embedded surfaces in generic position with respect to the projection, that can be deformed into each other, have apparent contours that can be connected using only smooth planar isotopies and a finite sequence of such moves.

This list of moves (see Figure 2 for a graphical representation) is essentially the same found in the literature for the related subject of maps from twomanifolds into \(\mathbb{R}^{2}\) (see e.g. [18]), even if the presence of the Huffman labelling entails a different classification of the list of moves belonging to each of the six aforementioned types: see Section 4. We also recall that the problem of finding a complete set of Reidemeister-type moves relating two equivalent knotted surfaces in \(\mathbb{R}^{4}\) has been solved. We refer in particular to the set of moves found by Roseman [21], to the papers of Carter and Saito [5], [6] where generic embedded surfaces in \(\mathbb{R}^{4}\) are projected in \(\mathbb{R}^{3}\) (diagram) and projected further in \(\mathbb{R}^{2}\) to construct a chart, and to the paper [13] of Goryunov. It must also be remembered that similar classifications appear in various contexts, in particular in Thom's catastrophe theory [22] and in Cerf's theory [9], in the paper of Wassermann [23], in the papers of Mancini and Ruas [16], and of Rieger [20]. We refer to the books [7], [8], [1] and [2] for further information.

The main result of the present paper (Corollary 6.1) can be obtained as a byproduct of general results present in the literature on the theory of knotted surfaces in \(\mathbb{R}^{4}\), for instance it can be deduced from [4]. However, also because we are concerned with embedded surfaces rather than immersed ones, we believe to be worthwhile to provide a more specific and direct proof. See also Remark 6.3 for more on this point.

Our proof has some similarities with the one described in [7] for the embedding of surfaces in \(\mathbb{R}^{4}\), and relies on the classification (reported very quickly in Section 2) of the singularities of stable maps between 3-manifolds: see [11] and references therein. Roughly, the idea of the proof is the following. Given an orthogonal projection \(\pi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{2}\) and a smooth closed surface \(M\), we consider an isotopy \(\gamma \in C^{\infty}\left(M \times[0,1] ; \mathbb{R}^{3}\right)\) between an initial embedding ( \(t=0\) ) and a final embedding \((t=1)\) of \(M\) in \(\mathbb{R}^{3}\), in generic positions with respect to \(\pi\). Since it is convenient to deal with closed source manifolds, we extend in a smooth periodic way \(\gamma\) to a map (still denoted by \(\gamma\) ) defined on \(\mathscr{X}:=M \times \mathbb{S}^{1}\). Let us interpret as time the last coordinate \(t \in \mathbb{S}^{1}\), and denote by ( \(x, t\) ) the points of \(\mathscr{X}\). Let us now consider the level preserving map \(F_{\gamma}: \mathscr{X} \rightarrow \mathscr{Y}:=\mathbb{R}^{2} \times \mathbb{S}^{1}\) obtained as the composition of the track \((x, t) \in M \times \mathbb{S}^{1} \rightarrow(\gamma(x, t), t) \in \mathbb{R}^{3} \times \mathbb{S}^{1}\) of \(\gamma\) with the projection map \((y, z, t) \in \mathbb{R}^{3} \times \mathbb{S}^{1} \rightarrow(y, t) \in \mathbb{R}^{2} \times \mathbb{S}^{1}\), i.e.,

$$
F_{\gamma}(x, t)=\left(\gamma_{1}(x, t), \gamma_{2}(x, t), t\right) .
$$

Provided \(F_{\gamma}\) is stable, its singular locus gives a stratification of \(\mathscr{X}\) into smooth submanifolds and, in a natural way, also a stratification \(\left\{Y_{0}, Y_{1}, Y_{2}, Y_{3}\right\}\) of \(\mathscr{Y}\). The family of apparent contours relating the two embeddings then satisfies

$$
\bigcup_{t \in \mathbb{S}^{1}}\left(\operatorname{AppCon}\left(\varphi_{t}\right) \times\{t\}\right)=Y_{1} \cup Y_{2} \cup Y_{3},
$$

where \(\varphi_{t}(x):=\left(\gamma_{1}(x, t), \gamma_{2}(x, t)\right), Y_{1}\) is the stratum of fold surfaces, \(Y_{2}\) is the stratum of cusp curves and double curves, and \(Y_{3}\) is the discrete stratum of cuspfold points, swallow tails and triple points. Let us now consider the projection \(p: \mathscr{Y} \rightarrow \mathbb{S}^{1}, p(y, t)=t\). It turns out that, provided \(p\) is a stratified Morse function, the union of \(Y_{3}\) and the critical points of the restriction \(p_{\mid Y_{2}}\) determine the complete list of moves on the apparent contours (see Corollary 6.1 and Figure 3). A technical part of our proof, based on the standard definition of stability, is contained in Lemmata 5.6, 5.8 and Corollary 5.7. The point is to show that the original map \(F_{\gamma}\) can be slightly deformed and made stable, and then perturbed once more in order to make \(p\) stratified: this is the content of Theorem 5.5.

We conclude this introduction by observing that in [10, definition 2] a different notion of equivalence between maps is introduced. Such a definition can be suitable when the target space \(\mathscr{Y}\) is the cartesian product of a two-dimensional manifold with \(\mathbb{R}\).

## 2 Stable maps and their singularities

In this section we briefly recall a few well known facts about singularity theory (see for instance [11], [2], [1] and references therein).

### 2.1 Density of stable maps

Let \(\mathscr{X}\) denote a closed smooth manifold of dimension \(m\), and let \(\mathscr{Y}\) be a smooth manifold of dimension \(n\) without boundary. We denote by \(C^{\infty}(\mathscr{X}, \mathscr{Y})\) the set of smooth maps from \(\mathscr{X}\) to \(\mathscr{Y}\) endowed with the Whitney topology; \(C^{\infty}(\mathscr{X}, \mathscr{Y})\) turns out to be a Baire space.

Definition 2.1. Two maps \(F, G \in C^{\infty}(\mathscr{X}, \mathscr{Y})\) are smoothly left-right equivalent (briefly, equivalent) if there exist two diffeomorphisms \(\phi: \mathscr{X} \rightarrow \mathscr{X}\) and \(\psi: \mathscr{Y} \rightarrow \mathscr{Y}\) such that \(G \circ \phi=\psi \circ F\).

Definition 2.2. A map \(F \in C^{\infty}(\mathscr{X}, \mathscr{Y})\) is smoothly stable (briefly, stable) if there exists a neighbourhood \(U_{F} \subset C^{\infty}(\mathscr{X}, \mathscr{Y})\) of \(F\) such that any map in \(U_{F}\) is equivalent to \(F\).

$$
\operatorname{Stab}(\mathscr{X}, \mathscr{Y}):=\left\{F \in C^{\infty}(\mathscr{X}, \mathscr{Y}): F \text { is stable }\right\},
$$

which is an open subset of \(C^{\infty}(\mathscr{X}, \mathscr{Y})\). We recall that if \(F\) is stable, then any map equivalent to \(F\) is stable. We also recall that the set \(\operatorname{Emb}(\mathscr{X} ; \mathscr{Y})\) of embeddings of \(\mathscr{X}\) into \(\mathscr{Y}\) is open in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\), and \(\operatorname{Emb}(\mathscr{X} ; \mathscr{Y}) \subseteq \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\).

### 2.2 Nonremovable singularities of maps for m ¼ n ¼

Assume in this section that \(m=n=3\). These dimensions are nice, so that \(\operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) is dense in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\).

- 2.2.1. Stratification of X associated with a stable map. We recall (see [11, Chap. 7, Sec. 6]) that a map F a Stab ð X ; Y Þ has a singular locus in the source manifold X of the following types:

- folds, denoted by \(S_{1}\) ð F Þ . It is a smooth submanifold of X of codimension 1, consisting of the points where the di¤erential dF x of F at x a X has corank 1;

- swallow-tails in X, denoted by \(S_{13}\) ð F Þ H \(S_{12}\) ð F Þ . It is a smooth submanifold of X of codimension 3, and therefore it is a finite set of points.

- pleats, denoted by \(S_{12}\) ð F Þ H \(S_{1}\) ð F Þ . It is a smooth submanifold of X of codimension 2 in X ;

define \(X_{0}\) as the set of the regular points of \(F\) and

$$
X_{1}:=S_{1}(F) \backslash S_{1_{2}}(F), \quad X_{2}:=S_{1_{2}}(F) \backslash S_{1_{3}}(F), \quad X_{3}:=S_{1_{3}}(F),
$$

where the index denotes the codimension in \(\mathscr{X}\). Then \(\left\{X_{0}, X_{1}, X_{2}, X_{3}\right\}\) forms a stratification of \(\mathscr{X}\), in the sense that \(\mathscr{X}\) is the union of the mutually disjoint smooth submanifolds \(X_{j}\) (the strata), such that \(\bar{X}_{j}=\bigcup_{j \leq h \leq 3} X_{h}\) for any \(j=0,1,2,3\). We call such a stratification the stratification of \(\mathscr{X}\) associated with the stable map \(F\).

2.2.2. Stratification of \(\mathscr{Y}\) induced by a stable map. By [11, Chap. 7, Th. 6.3], if \(F \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) the images of the strata \(X_{i}\) must intersect transversally. On \(F\left(X_{0}\right)\) there are no conditions. The set \(F\left(X_{1}\right)\) must selfintersect transversally: the resulting intersection is a set of double curves of codimension 2 in \(\mathscr{Y}\) (points having two singular preimages, i.e. two preimages in \(S_{1}(F)\) ) and a set of triple points (codimension 3, points with three singular preimages) in \(\mathscr{Y}\); moreover \(F\left(X_{1}\right)\) must intersect \(F\left(X_{2}\right)\) transversally, giving a finite set of cusp-fold points in \(\mathscr{Y}\). The remaining cases have dimension that is too low to give rise to any intersection set. Therefore, we define the following subsets of the target manifold \(\mathscr{Y}\) (the index denoting the codimension in \(\mathscr{Y}\) and the superscript denoting the number of singular preimages):

- Y 0 is the set of all h a Y such that no element in F 1 ð h Þ belongs to \(X_{1}\) A \(X_{2}\) A \(X_{3}\); hence Y 0 B F ð X Þ J F ð \(X_{0}\) Þ , namely Y 0 is contained in the set of regular values of F ;

- \(Y_{1}\) is the set of all h a Y such that \(F_{1}\) ð h Þ has one element in \(X_{1}\) and the other elements in \(X_{0}\). Hence \(Y_{1}\) is contained in F ð \(X_{1}\) Þ ; we call \(Y_{1}\) the set of fold surfaces. It carries a natural orientation since it separates points where the number of preimages of F jumps of two units;

- \(Y_{1}\) 2 is the set of all h a Y such that \(F_{1}\) ð h Þ has one element in \(X_{2}\), and the other elements in \(X_{0}\). We call \(Y_{1}\) 2 the set of cusp curves ;

- Y 1 3 is the set of all h a Y such that F 1 ð h Þ has one element in \(X_{3}\), and the other elements in \(X_{0}\). We call Y 1 3 the set of swallow tails ;

- \(Y_{2}\) 2 is the set of all h a Y such that \(F_{1}\) ð h Þ has two elements in \(X_{1}\) and the other elements in \(X_{0}\). We call \(Y_{2}\) 2 the set of double curves ;

- \(Y_{2}\) 3 is the set of all h a Y such that \(F_{1}\) ð h Þ has one element in \(X_{2}\), one element in \(X_{1}\) and the other elements in \(X_{0}\). We call \(Y_{2}\) 3 the set of cusp-fold points ;

- \(Y_{3}\) 3 is the set of all h a Y such that \(F_{1}\) ð h Þ has three elements in \(X_{1}\) and the other elements in \(X_{0}\). We call \(Y_{3}\) 3 the set of triple points.

Such a description allows to define a natural stratification of the target manifold \(\mathscr{Y}\) in the smooth submanifolds \(Y_{0}, Y_{1}, Y_{2}, Y_{3}\) (the strata), where

$$
Y_{2}:=Y_{2}^{1} \cup Y_{2}^{2}, \quad Y_{3}:=Y_{3}^{1} \cup Y_{3}^{2} \cup Y_{3}^{3} .
$$

This stratification will be denoted by \(\left\{Y_{j}\right\}_{F}\), and will be called the stratification of \(\mathscr{Y}\) induced by the stable map \(F\). For simplicity of notation, unless otherwise specified we drop the dependence on \(F\) of each strata \(Y_{j}\). We conclude this section by recalling the definition of a stratified Morse function defined on the stratified space \(\left(\mathscr{Y},\left\{Y_{j}\right\}_{F}\right)\) induced by the stable map \(F\) (see definition 2.3. Let \(F \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) and let \(u: \mathscr{Y} \rightarrow \mathbb{S}^{1}\) be a smooth function. We say that \(u\) is a stratified Morse function on \(\left(\mathscr{Y},\left\{Y_{j}\right\}_{F}\right)\) if the following three conditions hold:

- -for any j a \(f_{0}\) ; 1 ; 2 g the restriction \(u_{j}\) Yj of u to stratum Yj is a Morse function, and the set crit ð \(u_{j}\) Yj Þ of its critical points is finite; S

- -the critical values j A \(f_{0}\) ; 1 ; 2 g \(u_{j}\) Yj ð crit ð \(u_{j}\) Yj ÞÞ A u ð \(Y_{3}\) Þ are distinct, where points of \(Y_{3}\) are considered as critical points;

- -if j a f 1 ; 2 ; 3 g and h a Yj, then ker ð du h Þ does not contain any limit of a sequence of tangent spaces to Yh at h k a Yh, where 0 a h < j and lim k !þ l h k ¼ h.

## 3 Apparent contours

In this section we briefly recall the notions of apparent contour and labelling of an apparent contour. In the sequel \(M\) is a two-dimensional smooth closed orientable manifold, and \(\varphi: M \rightarrow \mathbb{R}^{2}\) is a smooth stable map. The apparent contour \(\operatorname{AppCon}(\varphi) \subset \mathbb{R}^{2}\) of \(\varphi\) is the image through \(\varphi\) of the singular locus of \(\varphi\) in \(M\). We set

$$
f(y):=\#\left\{\varphi^{-1}(y)\right\}, \quad y=\left(y_{1}, y_{2}\right) \in \mathbb{R}^{2} .
$$

The function \(f\) is constant on each connected component (called region) of \(\mathbb{R}^{2} \backslash \operatorname{AppCon}(\varphi)\), and it jumps of two units along an arc of \(\operatorname{AppCon}(\varphi)\). The apparent contour carries a natural orientation, so that the highest value of \(f\) lies locally on the left, in this way \(f\) can also be recovered as twice the winding number of the apparent contour.

It is well known (see for instance [27] and references therein) that the stability of \(\varphi\) implies that \(\operatorname{AppCon}(\varphi)\) consists of a finite family of smooth immersions of the circle \(\mathbb{S}^{1}\) in \(\mathbb{R}^{2}\) up to a finite number of points corresponding to canonical cusps, denoted by Cusps( \(\varphi\) ); self-intersections (called crossings) of the immersions are in a finite number, transverse and double, and will be denoted by \(\operatorname{Crossings}(\varphi)\). Denoting by \(\operatorname{Arcs}(\varphi)\) the \(\operatorname{arcs}\) of \(\operatorname{AppCon}(\varphi)\), we have \(\operatorname{AppCon}(\varphi)=\operatorname{Arcs}(\varphi) \cup \operatorname{Cusps}(\varphi) \cup \operatorname{Crossings}(\varphi)\). Therefore, \(\operatorname{AppCon}(\varphi)\) has the following structure: any point of \(\operatorname{AppCon}(\varphi)\) has a neighbourhood in \(\mathbb{R}^{2}\) which is diffeomorphic to one of the pictures in Figure 1, with matching orientations and appropriate choice of the values of \(f\) and \(d\) (see below for the meaning of the function \(d\) ). Because of the depth information coming from the embedding (see the next sections) we distinguish cusps where \(d\) is decreasing from cusps where \(d\) is increasing; a similar distinction is made for crossings. The gap shown in the pictures for arcs at a crossing is just added for visual convenience to help distinguish the arc with larger values of \(d\) (where \(d\) jumps by two, broken arc) from the arc with smaller value of \(d\) (unbroken).

### 3.1 Labelling of an apparent contour

A Huffman labelling (labelling for short) of \(\operatorname{AppCon}(\varphi)\) (see [15], [26], [7, p.19], [8, pp. 19, 20], [3]) is a pair \((f, d)\), where the function \(d: \operatorname{Arcs}(\varphi) \rightarrow \mathbb{N}\) has the following properties:

- -d is locally constant on Arcs ð j Þ ;

- -0 a d ð y Þ a lim inf y ! y f ð y Þ , for all y a Arcs ð j Þ ;

- -the compatibility conditions betweeen f and d depicted in Figure 1 must be satisfied.

### 3.2 Factorization of j through an embedding and a projection

Definition 3.1. Let \(\pi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{2}\) be an orthogonal projection and let \(\Sigma\) be a smooth closed surface embedded in \(\mathbb{R}^{3}\). We say that \(\Sigma\) is in generic position with respect to \(\pi\) if \(\pi_{\mid \Sigma}: \Sigma \rightarrow \mathbb{R}^{2}\) is stable.

![Figure 1. (b), (c)](/Users/evanthayer/Projects/paperx/docs/2012_completeness_of_reidemeister_type_moves_for_surfaces_embedded_in_three_dimensional_space/figures/figure-1-p006.png)

*Figure 1. (b), (c): the canonical cusp of AppCon ð j Þ , i.e. the semicubic curve ð y 2 1 ; y 3 1 Þ . (d), (e): the canonical crossings of AppCon ð j Þ . (a)–(e): compatibility conditions between f (deﬁned in (3.1)) and d (deﬁned in Section 3.1). (defined in (3.1)) and d (defined in Section 3.1).*

Remark 3.2. As shown in [3], the existence of a labelling on a planar graph with crossings and cusps, is a necessary and sufficient condition for the existence of a smooth closed two-manifold \(S\) and of a smooth map \(\varphi: S \rightarrow \mathbb{R}^{2}\) factorizing as

$$
\varphi=\pi \circ e
$$

where \(e: S \rightarrow \mathbb{R}^{3}\) is a smooth embedding, \(\pi: \mathbb{R}^{3} \rightarrow \mathbb{R}^{2}\) is an orthogonal projection such that \(\Sigma:=e(S)\) is in generic position with respect to \(\pi\), and such that the planar graph is \(\operatorname{AppCon}(\varphi)\). Moreover such an embedding is unique up to The meanings of \(f\) and \(d\) then become the following:

- -f ð y Þ is the number of points of S that project on y a \(R_{2}\) ;

- -d ð y Þ counts the number of layers of S in front of the point of the singular locus of j that projects on y.

The following simple observation is concerned with the stability of \(\pi \circ e\) (see [17] for general stability theorems for composite mappings), and shows that, in the statement of Theorem 5.5, there is no loss of generality in assuming the initial and final surfaces \(\Sigma_{0}\) and \(\Sigma_{1}\) to be in generic position with respect to \(\pi\).

Remark 3.3. Given \(e \in \operatorname{Emb}\left(M, \mathbb{R}^{3}\right)\) and a neighbourhood \(U_{e} \subset C^{\infty}\left(M, \mathbb{R}^{3}\right)\) of \(e\), there exists \(\hat{e} \in \operatorname{Emb}\left(M, \mathbb{R}^{3}\right) \cap U_{e}\) such that \(\hat{\Sigma}:=\hat{e}(M)\) is in generic position with respect to \(\pi\). Indeed, by identifying \(M\) with \(\Sigma:=e(M)\) we can suppose that \(e: \Sigma \rightarrow \mathbb{R}^{3}\) is the identity. Then \(\kappa:=\pi \circ e \in C^{\infty}\left(\Sigma, \mathbb{R}^{2}\right)\) is a map between two 2-manifolds, with \(\Sigma\) closed. From the density of \(\operatorname{Stab}\left(\Sigma, \mathbb{R}^{2}\right)\) in \(C^{\infty}\left(\Sigma, \mathbb{R}^{2}\right)\) it follows that, given any neighboourhood \(U_{\kappa} \subset C^{\infty}\left(\Sigma, \mathbb{R}^{2}\right)\) of \(\kappa\) there exists a \(\operatorname{map} \varphi \in \operatorname{Stab}\left(\Sigma, \mathbb{R}^{2}\right) \cap U_{\kappa}\). define \(\hat{\Sigma}:=\{(\varphi(y, z), z):(y, z) \in \Sigma\}\). Taking \(U_{\kappa}\) small enough and recalling that \(\operatorname{Emb}\left(\Sigma, \mathbb{R}^{3}\right)\) is open in \(C^{\infty}\left(\Sigma, \mathbb{R}^{3}\right)\), we obtain that there exists \(\hat{e} \in \operatorname{Emb}\left(M, \mathbb{R}^{3}\right) \cap U_{e}\) such that \(\hat{e}(M)=\hat{\Sigma}\). Moreover \(\pi_{\mid \hat{\Sigma}}=\varphi\), so that the stability of \(\varphi\) implies that \(\hat{\Sigma}\) is in generic position with respect to \(\pi\).

## 4 Moves on apparent contours

In this section we list the moves on the apparent contour; in view of Theorem 5.5, and as explained in the introduction, this list turns out to be complete (see Corollary 6.1).

Definition 4.1. With reference to Figure 2, the moves on an apparent contour are given as \(K, L, B, C, S, T\), by identifying a box in \(\mathbb{R}^{2}\) diffeomorphic to the box on the left side of the picture and replacing it with a box diffeomorphic to the box on the right side.

Remark 4.2. We require that the moves leave unchanged a (small) neighbourhood of the boundary of the box. The same definition as definition 4.1 can be given, except for the move T, by switching the role of the two boxes: this is equivalent to reverse the orientation of the \(t\)-axis, and to consider the inverse moves as temporal inverse moves. The corresponding moves will be denoted by \(\mathrm{K}^{-1}, \mathrm{~L}^{-1}\), \(\mathrm{B}^{-1}, \mathrm{C}^{-1}, \mathrm{~S}^{-1}\). The (direct) moves \(\mathrm{K}, \mathrm{L}, \mathrm{B}, \mathrm{C}, \mathrm{S}, \mathrm{T}\) are chosen in such a way that they simplify the local topology of the apparent contour (i.e., they decrease the number of crossings/cusps). There is no distinction between direct and inverse moves of type T, as explained in the sequel.

We recall that all apparent contours that we consider in the present paper are oriented, and therefore different orientations determine different moves. For simplicity of notation, in most of the pictures of Figure 2 we do not specify the orientation; moreover, we do not indicate the values of \(f\) before and after the moves, since the values of \(f\) can be inferred from the orientation of the apparent contour.

- -The four moves of type K. We divide the moves of type K into four di¤erent moves as follows. Up to a rotation of 180 degrees, we can assume that the arc with the two extremal points on the left is in front of the other arc. The four moves therefore are classified on the basis of the four possible orientations of the two arcs. In addition they are parameterized by two nonnegative integers d and k, as explained in Section 4.3 below.

- -The moves L and B. Up to a rotation of 180 degrees, we can assume that the highest value of d is on the upper arc. Then there is one move L and one move B, as depicted in Figure 2.

- -The eight moves of type C. We divide the moves of type C into two groups of four di¤erent types. first we distinguish the case when the cusp is in front of the (vertical) arc. The first of the figures for C is in turn divided into four cases, depending on whether the value of d decreases of increases when parameterizing the cusp, and on the orientation of the vertical arc. In the second figure the cusp is behind the vertical arc: similarly as before, we have four cases. The set of values taken by d along the cusped arc are f d þ k ; d þ k þ 1 ; d þ k þ 2 ; d þ k þ 3 g. Again the meaning of the two parameters d and k is explained in Section 4.3.

- -The two moves of type S. We divide the moves of type S into two groups: in the first picture the value of d jumps up by two at the crossing and is decreasing at (both) cusps (the arcs are traversed according to their natural orientation), whereas in the second picture d is increasing at the cusps.

- -The sixteen moves of type T. The three arcs carry a natural ordering according to their relative depth (increasing values of d); we can always rotate the picture so that the nearest arc (lowest d), is the vertical one. We then have two di¤erent possibilities for the position of the itermediate and of the furthest arcs. Each of the three arcs can be oriented in two ways: the internal triangular region can lie on the left or on the right. In the end we have sixteen di¤erent possibilities which however also account for the corresponding time reversed moves, in the sense that the inverse of a T move is still a T move. This is in contrast to what happens for all the other moves. If \(d_{1}\), \(k_{1}\) and \(k_{2}\) denote respectively the number of layers in front of the first fold (nearest arc), the

![Figure 2. List of moves on the apparent contour](/Users/evanthayer/Projects/paperx/docs/2012_completeness_of_reidemeister_type_moves_for_surfaces_embedded_in_three_dimensional_space/figures/figure-2-p009.png)

*Figure 2. List of moves on the apparent contour: Figure 2. List of moves on the apparent contour*

number of layers interposed between the first and second fold and the number of layers interposed between the second and the third fold, then \(d_{1}\) is the value of \(d\) on the first arc, \(d_{1}+k_{1}\) and \(d_{1}+k_{1}+2\) are the two values taken by \(d\) on the second arc, and the values of \(d\) on the third arc are contained in the set \(\left\{d_{1}+k_{1}+k_{2}+i: i=0,2,4\right\}\), the precise values depending on the orientation of the first and second arc. Remark 4.3. In order to make a complete classification of the moves, the number of layers, at different depths, of the corresponding three dimensional embedded surface must be taken into account: this introduces further degrees of freedom in the list of different moves, as follows. Moves \(\mathrm{L}, \mathrm{B}\) and S have one nonnegative integer parameter \(d\), counting the number of layers in front of the fold. Moves of type K and C have two nonnegative integer parameters \(d\) and \(k\), counting the number of layers in front of the first fold, and the number of layers in between the two folds. Moves of type T have three nonnegative integer parameters, given respectively by the number of layers in front of the first fold surface, by the number of layers between the first and the second fold surface, an by the number of layers between the second and the third fold surface.

## 5 Stability of F g and stratifiability of p

In order to state the main result (Theorem 5.5) we need some preparation. In this section M denotes a smooth two-dimensional closed manifold.

Recall [14] that an isotopy from \(M\) to \(\mathbb{R}^{3}\) is a map \(\gamma \in C^{\infty}\left(M \times[0,1], \mathbb{R}^{3}\right)\) such that for any \(t \in[0,1]\) the map \(\gamma(\cdot, t): M \rightarrow \mathbb{R}^{3}\) is an embedding.

Definition 5.1. Let \(\Sigma_{0}\) and \(\Sigma_{1}\) be the images in \(\mathbb{R}^{3}\) of two smooth embeddings of \(M\). We say that \(\Sigma_{0}\) and \(\Sigma_{1}\) are isotopic if there exists an isotopy \(\gamma\) such that \(\gamma(M, 0)=\Sigma_{0}\) and \(\gamma(M, 1)=\Sigma_{1}\).

Therefore, we perform the following operations. We first reparametrize the map \(\gamma(x, \cdot)\) by composing it with a strictly increasing \(C^{\infty}([0,1],[0,1])\) function having vanishing derivatives of all order at 0 and 1. We still denote by \(t\) the new variable, so that

$$
{\frac{\partial^{k} \gamma(x, t)}{\partial t^{k}}}_{\mid t=0}=\left.\frac{\partial^{k} \gamma(x, t)}{\partial t^{k}}\right|_{\mid t=1}=0, \quad k \in \mathbb{N}, k \geq 1 .
$$

We next extend \(\gamma\) on the whole of \(M \times \mathbb{R}\) by reflecting it about 0 and 1, resulting in a smooth periodic function of period 2 in the variable \(t\). If we identify \(\mathbb{R} /[0,2]\) with \(\mathbb{S}^{1}\) we obtain a smooth function, still denoted by \(\gamma\), defined on the closed smooth manifold \(M \times \mathbb{S}^{1}\) with values in \(\mathbb{R}^{3}\). In this way 0 and 1 are two distinct points in the oriented circle \(\mathbb{S}^{1}\).

From now on we set

$$
\mathscr{X}:=M \times \mathbb{S}^{1} .
$$

Variables in \(\mathscr{X}\) will be denoted by ( \(x, t\) ) with \(x \in M, x=\left(x_{1}, x_{2}\right)\) (locally) and \(t \in \mathbb{S}^{1}\). Moreover, we shall denote as usual by ( \(y, z\) ) a point of \(\mathbb{R}^{3}=\mathbb{R}^{2} \times \mathbb{R}\) where \(y=\left(y_{1}, y_{2}\right) \in \mathbb{R}^{2}\) and \(z \in \mathbb{R}\).

### 5.1 The map F g

From now on we set

$$
\mathscr{Y}:=\mathbb{R}^{2} \times \mathbb{S}^{1} .
$$

Variables in \(\mathscr{Y}\) will be denoted by \((y, t)\) with \(y=\left(y_{1}, y_{2}\right) \in \mathbb{R}^{2}\) and \(t \in \mathbb{S}^{1}\). We let \(\pi: \mathbb{R}^{3}=\mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2}\) denote the orthogonal projection defined by \(\pi(y, z):=y\).

Definition 5.2. Let \(\gamma \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\). We define \(F_{\gamma} \in C^{\infty}(\mathscr{X}, \mathscr{Y})\) as

$$
F_{\gamma}(x, t):=(\pi(\gamma(x, t)), t), \quad(x, t) \in \mathscr{X} .
$$

The map \(\gamma \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right) \rightarrow F_{\gamma} \in C^{\infty}(\mathscr{X}, \mathscr{Y})\) is continuous. It is immediately seen that the differential of \(F_{\gamma}\) has rank 2 at \((\bar{x}, \bar{t}) \in \mathscr{X}\) if and only if the map

$$
\varphi_{\bar{t}}:=\pi(\gamma(\cdot, \bar{t})): x \in M \rightarrow \varphi_{\bar{t}}(x):=\left(\gamma_{1}(x, \bar{t}), \gamma_{2}(x, \bar{t})\right) \in \mathbb{R}^{2}
$$

has differential with rank one at \(\bar{x} \in M\). This in particular implies (1.1). Note that, defining \(f_{t}(y)\) as in (3.1) with \(\varphi_{t}\) in place of \(\varphi\), we have \(f_{t}(y)=\#\left\{F_{\gamma}^{-1}(y, t)\right\}\) for any \((y, t) \in \mathscr{Y}\).

5.2. Statement of the main theorem

$$
We denote by \(p: \mathscr{Y} \rightarrow \mathbb{S}^{1}\) the projection
$$

$$
p(y, t):=t, \quad y \in \mathbb{R}^{2}, t \in \mathbb{S}^{1},
$$

defined on the target manifold Y. Let \(\Sigma_{0}\) and \(\Sigma_{1}\) be two isotopic embedded surfaces in \(\mathbb{R}^{3}\), and let \(\gamma\) be the isotopy. In order to prove the completeness of the set of moves (Section 6) we need to have that \(F_{\gamma} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) and, at the same time, that \(p: \mathscr{Y} \rightarrow \mathbb{S}^{1}\) is a stratified Morse function on the stratification ( \(\mathscr{Y},\left\{Y_{j}\right\}_{F_{y}}\) ). Corollary 5.7 below shows that \(F_{\gamma}\) can be approximated by stable maps of the form \(F_{\bar{\gamma}}\), for a suitable \(\bar{\gamma}\). The stability of \(F_{\bar{\gamma}}\) implies that \(p_{\mid Y_{0}}\) and \(p_{\mid Y_{1}}\) have no critical points (Remark 5.3) but does not imply, in general, that \(p\) is a stratified Morse function (Remark 5.4): it may happen that a curve in \(Y_{2}\) having an endpoint in \(Y_{3}\) has there a tangent line contained in the plane \(\{t=\) const \(\}\).

Remark 5.3. Let \(\alpha \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) be such that \(F_{\alpha} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\), and let \(\left(\mathscr{Y},\left\{Y_{j}\right\}_{F_{\alpha}}\right)\) be the stratification induced by \(F_{\alpha}\). Recalling definition (5.6) of \(p\) it is immediate to check that \(p_{\mid Y_{0}}\) does not have any critical point. Moreover:

- -p j \(Y_{1}\) does not have any critical point, or equivalently the tangent plane to \(Y_{1}\) at a point is never orthogonal to ð 0 ; 0 ; 1 Þ . Indeed, if the rank of the di¤erential of F a at ð x ; t Þ a X is two and F a ð x ; t Þ a \(Y_{1}\), necessarily the tangent space at F a ð x ; t Þ contains a vector of the form ð \(c_{1}\) ; \(c_{2}\) ; 1 Þ for some \(c_{1}\) ; \(c_{2}\) a R. In particular the tangent plane to \(Y_{1}\) at F a ð x ; t Þ is transversal to f t ¼ t g, and this holds uniformly with respect to the points in \(Y_{1}\).

- -Let ð y ; t Þ a \(Y_{2}\) A \(Y_{3}\) be a point which is limit of points ð yk ; tk Þ belonging to \(Y_{1}\). Assume that the limit of the sequence of tangent planes to \(Y_{1}\) at ð yk ; tk Þ a \(Y_{1}\) exists, and denote by T such a limit. Then, by the previous item and by continuity, still ð \(c_{1}\) ; \(c_{2}\) ; 1 Þ is one of the two vectors spanning T. Therefore T is transverse to f t ¼ t g at ð y ; t Þ .

Remark 5.4. Let as adopt the notation of Remark 5.3. Then the function \(p\) could not be a stratified Morse function on \(\left(\mathscr{Y},\left\{Y_{j}\right\}_{F_{\tilde{y}}}\right)\), since the third condition of definition 2.3 may fail, when \(u=p\) and \(j=3\). For instance:

- -It is not di‰cult to find an example of a map a a \(C^{l}\) ð X ; \(R_{3}\) Þ with F a a Stab ð X ; Y Þ , having a triple point at ð y ; t Þ ¼ ð 0 ; 0 Þ a \(Y_{3}\) 3 with one of the double curves in \(Y_{2}\) 2 parallel to f t ¼ 0 g. This is the case for instance of a map F a a Stab ð X ; Y Þ having, locally around ð 0 ; 0 Þ , the fold surfaces of the form f \(y_{1}\) ¼ e t g and f \(y_{2}\) ¼ 0 g. These folds are obviously mutually transverse, f \(y_{1}\) ¼ t ¼ 0 g is locally one of the double curves and it is parallel to the plane f t ¼ 0 g.

- -Up to a change of variables in X and Y, a swallow tail singularity at ð 0 ; 0 Þ has the local description \(h_{1}\) ¼ \(x_{1}\) \(x_{2}\) þ \(x_{2}\) 1 \(x_{3}\) þ \(x_{4}\) 1, \(h_{2}\) ¼ \(x_{2}\), \(h_{3}\) ¼ \(x_{3}\). There are two cusp curves and one double curve originating at the singularity with a common tangent vector ð 0 ; 0 ; 1 Þ ; moreover all the fold surfaces are locally tangent at the singularity to the plane f \(h_{1}\) ¼ 0 g. We can provide two simple realizations in our context of the canonical representation above. The choice x ¼ ð \(x_{1}\) ; \(x_{2}\) Þ , y ¼ ð \(h_{1}\) ; \(h_{2}\) Þ , t ¼ \(x_{3}\) ¼ \(h_{3}\) corresponds to the move S, whereas the choice x ¼ ð \(x_{1}\) ; \(x_{3}\) Þ , y ¼ ð \(h_{1}\) ; \(h_{3}\) Þ , t ¼ \(x_{2}\) ¼ \(h_{2}\) (whence p ð a ð x ; t ÞÞ ¼ ð tx 1 þ \(x_{2}\) \(x_{2}\) 1 þ \(x_{4}\) 1 ; \(x_{2}\) Þ ) corresponds to an evolution that is degenerate at t ¼ 0: indeed the corresponding apparent contour has a cusp with one of the two departing arcs that is (locally) completely contained in another arc of the contour.

In Lemma 5.8 we perform a further perturbation of a stable map \(F_{\beta}\) in order to get a new map making the function \(p\) stratified. Eventually, stability of \(F_{\gamma}\) and stratifiability of \(p\) can be achieved at the same time, and this is one of the byproducts of the following theorem.

Theorem 5.5. Let \(\pi: \mathbb{R}^{3}=\mathbb{R}^{2} \times \mathbb{R} \rightarrow \mathbb{R}^{2}\) be the orthogonal projection, and for \(j=0,1\) let \(e_{j} \in \operatorname{Emb}\left(M, \mathbb{R}^{3}\right)\) be such that \(\Sigma_{0}:=e_{0}(M)\) and \(\Sigma_{1}:=e_{1}(M)\) are in generic position with respect to \(\pi\). Assume that \(\gamma \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) is an isotopy between \(\Sigma_{0}\) and \(\Sigma_{1}\). Then for any neighbourhood \(U_{e_{j}} \subset C^{\infty}\left(M, \mathbb{R}^{3}\right)\) of \(e_{j}, j=0,1\), and for any neighbourhood \(U_{\gamma} \subset C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) of \(\gamma\) there exists a map \(\tilde{\gamma} \in U_{\gamma}\) such that

- (i) ~ \(S_{0}\) : ¼ ~ g ð M ; 0 Þ and ~ \(S_{1}\) : ¼ ~ g ð M ; 1 Þ are in generic position with respect to p, ~ g ð ; 0 Þ a Ue 0, ~ g ð ; 1 Þ a Ue 1, and ~ g is an isotopy betweeen ~ \(S_{0}\) and ~ \(S_{1}\) ;

- (ii) F ~ g a Stab ð X ; Y Þ , where F ~ g ð x ; t Þ : ¼ ð p ~ g ð x ; t Þ ; t Þ for any ð x ; t Þ a X ;

- (iii) p : Y ! \(S_{1}\) is a stratified Morse function on the stratification ð Y ; f Yj g F ~ g Þ of Y induced by F ~ g.

### 5.3 Proof of Theorem 5.5

We split the proof into various steps.

Lemma 5.6. Let \(\alpha \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\). For any neighbourhood \(N_{\alpha}\) of \(\alpha\) in \(C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) we can find a neighbourhood \(V_{F_{\alpha}}\) of \(F_{\alpha}\) in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\) such that for any \(G \in V_{F_{\alpha}}\) there exists \(\bar{\alpha} \in N_{\alpha}\) so that

$$
\(F_{\bar{\alpha}}\) is equivalent to \(G\).
$$

Proof. Let \(N_{\alpha}\) be a neighbourhood of \(\alpha\). Let also \(V_{F_{\alpha}}\) be a neighbourhood of \(F_{\alpha}\) in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\). We want to show that, reducing \(V_{F_{\alpha}}\), any \(G \in V_{F_{\alpha}}\) is equivalent to a map having the third component equal to \(t\). Write \(G\) in components as \(G=\left(G_{1}, G_{2}, G_{3}\right): \mathscr{X} \rightarrow \mathbb{R}^{2} \times \mathbb{S}^{1}\). Then, provided \(V_{F_{\alpha}}\) is sufficiently small, for any \(x \in M\) the function \(t \in \mathbb{S}^{1} \rightarrow G_{3}^{x}(t):=G_{3}(x, t) \in \mathbb{S}^{1}\) is close to the identity in \(\mathcal{C}^{\infty}\left(\mathbb{S}^{1}, \mathbb{S}^{1}\right)\), and therefore it is invertible. Let \(g^{x}(\cdot): \mathbb{S}^{1} \rightarrow \mathbb{S}^{1}\) be its inverse; note that the map \((x, t) \in \mathscr{X} \rightarrow g^{x}(t) \in \mathbb{S}^{1}\) is smooth. Moreover \(g^{x}\left(G_{3}^{x}(t)\right)=t\) and \(G_{3}^{x}\left(g^{x}(s)\right)=s\). Setting \(\alpha=\left(\alpha_{x}, \alpha_{z}\right) \in \mathbb{R}^{2} \times \mathbb{R}\), we define \(\bar{\alpha}: \mathscr{X} \rightarrow \mathbb{R}^{3}\) (writing \(t\) in place of \(s\) ) as

$$
\bar{\alpha}(x, t):=\left(G_{1}\left(x, g^{x}(t)\right), G_{2}\left(x, g^{x}(t)\right), \alpha_{z}(x, t)\right), \quad(x, t) \in \mathscr{X} .
$$

Since \(\bar{\alpha}\) depends continuously on \(G\), possibly restricting the neighbourhood \(V_{F_{\alpha}}\) we can ensure that \(\bar{\alpha} \in N_{\alpha}\). Then the map \((x, t) \in \mathscr{X} \rightarrow F_{\bar{\alpha}}(x, t):=(\pi \circ \bar{\alpha}(x, t), t) \in \mathscr{Y}\) satisfies

$$
F_{\bar{\alpha}}(x, t)=\left(G_{1}\left(x, g^{x}(t)\right), G_{2}\left(x, g^{x}(t)\right), t\right), \quad(x, t) \in \mathscr{X} .
$$

Since \(G \circ \phi=F_{\bar{\alpha}}=\mathrm{id}_{\mathscr{y}} \circ F_{\bar{\alpha}}\), it follows that \(F_{\bar{\alpha}}\) is equivalent to \(G\).

Corollary 5.7. Let \(\alpha \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\). For any neighbourhood \(N_{\alpha}\) of \(\alpha\) in \(C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) there exists \(\bar{\alpha} \in N_{\alpha}\) such that

$$
F_{\bar{\alpha}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y}) .
$$

Since \(\operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) is dense in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\), there exists \(H \in V_{F_{\alpha}} \cap \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). Therefore, choosing \(G=H\) in Lemma 5.6 we deduce that \(F_{\bar{\alpha}}\) is equivalent to \(H \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). As a consequence, also \(F_{\bar{\alpha}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\).

Lemma 5.8. Let \(\beta \in C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) be such that \(F_{\beta} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). For any neighbourhood \(W_{\beta}\) of \(\beta\) in \(C^{\infty}\left(\mathscr{X}, \mathbb{R}^{3}\right)\) there exists a map \(\hat{\beta} \in W_{\beta}\) such that \(F_{\hat{\beta}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) and p: \mathscr{Y} \rightarrow \mathbb{S}^{1} \text { is a stratified Morse function on }\left(\mathscr{Y},\left\{Y_{j}\right\}_{F_{\hat{\beta}}}\right).

Proof. Since \(F_{\beta} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\), from Remark 5.3 it follows that \(p_{\mid Y_{0}}\) and \(p_{\mid Y_{1}}\) have no critical points. The examples in Remark 5.4 show however that \(F_{\beta}\) must be slightly perturbed in order the function \(p\) to be a stratified Morse function. Let \(W_{\beta}\) be a neighbourhood of \(\beta\) in \(C^{\infty}(\mathscr{X}, \mathscr{Y})\). Recalling definition 2.3, in order to prove (5.8) it remains to show that there exists \(\hat{\beta} \in W_{\beta}\) such that the function \(p:\left(\mathscr{Y},\left\{Y_{j}\right\}_{F_{\hat{\beta}}}\right) \rightarrow \mathbb{S}^{1}\) satisfies the following three properties:

- if ð y ; t Þ a \(Y_{3}\) then all curves in \(Y_{2}\) having ð y ; t Þ as an end point cannot have a limit tangent line at ð y ; t Þ contained in f t ¼ t g ;

- all critical values of p j \(Y_{2}\) are distinct, and distinct from p ð \(Y_{3}\) Þ , in turn consisting of distinct points of \(S_{1}\) ;

- the critical points of p j \(Y_{2}\) are nondegenerate.

Let us consider the stratification \(\left\{Y_{j}\right\}_{F_{\beta}}\) induced by \(F_{\beta}\), and let \((\bar{y}, \bar{t}) \in Y_{3}\). Note that if \((\bar{y}, \bar{t}) \in Y_{3}^{3}\) then only one of the three double curves concurring at \((\bar{y}, \bar{t})\) may have the property of having a limit tangent line contained in \(\{t=\bar{t}\}\) : indeed, if two of them share this property, then there is a fold surface in \(Y_{1}\) having the tangent plane at ( \(\bar{y}, \bar{t}\) ) parallel to \(\{t=\bar{t}\}\), which is in contradiction with Remark 5.3. Recall also that, if \((\bar{y}, \bar{t}) \in Y_{3}^{1}\) is a swallow tail, then the two cusp curves and the double curve concurring at \((\bar{y}, \bar{t})\) have the same tangent vector there. Assume now that there is a curve \(c\) in \(Y_{2} \cup\{(\bar{y}, \bar{t})\}\) having \((\bar{y}, \bar{t})\) as an end point with a limit tangent line at \((\bar{y}, \bar{t})\) contained in \(\{t=\bar{t}\}\). Let \(\lambda=\left(\lambda_{1}, \lambda_{2}, \lambda_{3}\right) \in\) \(C^{\infty}([0,1], \mathscr{Y})\) be a regular parameterization of \(c\) having \((\bar{y}, \bar{t})\) as an end point, so that \(\lambda(0)=(\bar{y}, \bar{t})\) and \(\lambda_{3}^{\prime}(0)=0\). Pick a smooth function \(a: \mathscr{Y} \rightarrow \mathbb{R}\) satisfying

$$
a(\bar{y}, \bar{t})=0, \quad \frac{d}{d \sigma} a(\lambda(\sigma))_{\mid \sigma=0} \neq 0 .
$$

Let \(\Omega \subset \mathscr{Y}\) be a neighbourhood of ( \(\bar{y}, \bar{t}\) ) small enough so that all points in \(Y_{3} \backslash\{(\bar{y}, \bar{t})\}\) are not contained in \(\bar{\Omega}\); let also \(\chi\) be a smooth nonnegative function on \(\mathscr{Y}\) supported in \(\Omega\) which is constantly equal to one in a small neighbourhood of \((\bar{y}, \bar{t})\) and let \(\varepsilon \in \mathbb{R}\). define the function \(j: \mathscr{Y} \rightarrow \mathbb{R}\) as

$$
j(y, t):=t+\epsilon \chi(y, t) a(y, t), \quad(y, t) \in \mathscr{Y} .
$$

Therefore, the map \(\psi: \mathscr{Y} \rightarrow \mathscr{Y}\) defined as \(\psi(y, t):=(y, j(y, t))\) is a diffeomorphism of \(\mathscr{Y}\). define \(G: \mathscr{X} \rightarrow \mathscr{Y}\) as

$$
G:=\psi \circ F_{\beta}
$$

Then \(G\) is equivalent to \(F_{\beta}\), and therefore since by assumption \(F_{\beta} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\), it follows that also \(G \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). Moreover

$$
G(x, t)=\left(\pi \circ \beta(x, t), i^{x}(t)\right), \quad(x, t) \in \mathscr{X},
$$

Let \(V_{F_{\beta}}\) be the neighbourhood of \(F_{\beta}\) given by Lemma 5.6 (take \(\beta=\alpha\) and \(W_{\beta}=N_{\alpha}\) ). If \(|\epsilon| \ll 1\) we have \(G \in V_{F_{\beta}}\). Let us now consider the stratification \(\left\{Y_{0}^{G}, Y_{1}^{G}, Y_{2}^{G}, Y_{3}^{G}\right\}\) induced on \(\mathscr{Y}\) by \(G\) : by equality (5.10) it follows that such a stratification is the image through \(\psi\) of the stratification induced by \(F_{\beta}\). The first relation in (5.9) implies that \((\bar{y}, \bar{t}) \in Y_{3}^{G}\); moreover \(\psi(c) \subset Y_{2}^{G} \cup\{(\bar{y}, \bar{t})\}\) is regularly parameterized in a neighbourhood of ( \(\bar{y}, \bar{t}\) ) by \(\sigma \in[0,1] \rightarrow \psi(\lambda(\sigma))=\) \(\left(\lambda_{1}(\sigma), \lambda_{2}(\sigma), j(\lambda(\sigma))\right)\). Since

$$
\frac{d}{d \sigma} j(\lambda(\sigma))_{\mid \sigma=0}=\lambda_{3}^{\prime}(0)+\varepsilon \frac{d}{d \sigma} a(\lambda(\sigma))_{\mid \sigma=0}=\varepsilon \frac{d}{d \sigma} a(\lambda(\sigma))_{\mid \sigma=0},
$$

the second relation in (5.9) guarantees that the right hand side of (5.11) is nonzero. It follows that assertion (1) is satisfied for the stratification induced by G.

where

$$
i^{x}(t):=t+\epsilon \chi\left(F_{\beta}(x, t)\right) a\left(F_{\beta}(x, t)\right), \quad(x, t) \in \mathscr{X} .
$$

Denote by \(\phi: \mathscr{X} \rightarrow \mathscr{X}\) the diffeomorphism of \(\mathscr{X}\) defined by \(\phi(x, t):=\) \(\left(x,\left(i^{x}\right)^{-1}(t)\right)\). From the proof of Lemma 5.6, it follows that there exists \(\hat{\beta} \in W_{\beta}\) such that

$$
G \circ \phi=F_{\hat{\beta}}
$$

Since \(G \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\) it follows that \(F_{\hat{\beta}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). Moreover, (5.12) implies that the stratification of \(\mathscr{X}\) associated with \(G\) is the image through \(\phi\) of the stratification associated with \(F_{\beta}\), and that the stratification of \(\mathscr{Y}\) induced by \(G\) coincides with the stratification induced by \(F_{\hat{\beta}}\). We conclude therefore that the stratification induced by \(F_{\hat{\beta}}\) satisfies condition (1). If we now replace the function \(a\) in the previous argument with the function \(a+b\), where \(b: \mathscr{Y} \rightarrow \mathbb{R}\) is a smooth function satisfying \(b(\bar{y}, \bar{t}) \neq 0\) and \(d b_{(\bar{y}, \bar{t})}=0\), we obtain that \(p\left(Y_{3}\right)\) consists of distinct points of \(\mathbb{S}^{1}\). Considering the stratification of \(\mathscr{Y}\) induced by \(F_{\hat{\beta}}\), from condition (1) we deduce that \(p_{\mid Y_{2}}\) has no critical points on the boundary points of \(Y_{2}\). Therefore, being all critical points of \(p_{\mid Y_{2}}\) interior to any arc of \(Y_{2}\) we can argue using one dimensional Morse theory, and obtain assertion (3). Also assertion (2) follows in a standard way.

We are now in the position to conclude the proof of the theorem.

We apply Corollary 5.7 to \(\alpha=\gamma\) and to \(N_{\alpha} \subseteq U_{\gamma}\), and we obtain a corresponding map \(\bar{\gamma} \in N_{\alpha}\) satisfying \(F_{\bar{\gamma}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\). Possibly reducing \(N_{\alpha}\), we can assume that \(\bar{\gamma}(\cdot, 0) \in U_{e_{0}}\) and \(\bar{\gamma}(\cdot, 1) \in U_{e_{1}}\). Since \(F_{\bar{\gamma}} \in \operatorname{Stab}(\mathscr{X}, \mathscr{Y})\), we can now apply Lemma 5.8 to \(\beta=\bar{\gamma}\) and to \(W_{\beta}\) a neighbourhood of \(\bar{\gamma}\) satisfying \(W_{\beta} \subseteq N_{\alpha}\) : if we set

$$
\tilde{\gamma}:=\hat{\beta},
$$

it follows that \(\tilde{\gamma} \in W_{\beta} \subseteq N_{\alpha} \subseteq U_{\gamma}\), and \(\tilde{\gamma}\) satisfies assertions (ii) and (iii). MoreSince \(\gamma(\cdot, t) \in \operatorname{Emb}\left(M, \mathbb{R}^{3}\right)\) and \(\operatorname{Emb}\left(M, \mathbb{R}^{3}\right)\) is open in \(C^{\infty}\left(M, \mathbb{R}^{3}\right)\) it follows (possibly reducing \(W_{\beta}\) ) that \(\tilde{\gamma}(M, 0)\) and \(\tilde{\gamma}(M, 1)\) are isotopic. Since by assumption \(\pi_{\mid \Sigma_{j}} \in \operatorname{Stab}\left(\Sigma_{j}, \mathbb{R}^{2}\right)\), possibly reducing \(W_{\beta}\) and recalling that \(\operatorname{Stab}\left(\Sigma_{j}, \mathbb{R}^{2}\right)\) is open in \(C^{\infty}\left(\Sigma_{j}, \mathbb{R}^{2}\right)\) it follows that \(\pi_{\mid \tilde{\gamma}(M, 0)} \in \operatorname{Stab}\left(\Sigma_{0}, \mathbb{R}^{2}\right)\) and \(\pi_{\mid \tilde{\gamma}(M, 1)} \in \operatorname{Stab}\left(\Sigma_{1}, \mathbb{R}^{2}\right)\). This proves (i) and concludes the proof of Theorem 5.5.

## 6 Completeness of moves

Let \(\pi, e_{0}, e_{1}, \tilde{\gamma},\left(\mathscr{Y},\left\{Y_{j}\right\}_{F_{\tilde{\gamma}}}\right)\) and \(p\) be as in Theorem 5.5. By compactness, the set \(\operatorname{crit}\left(p_{\mid Y_{2}}\right)\) of critical points of \(p_{\mid Y_{2}}\) is finite. Since also \(Y_{3}\) consists of isolated points, it follows that \(p_{Y_{2}}\left(\operatorname{crit}\left(p_{\mid Y_{2}}\right)\right) \cup p\left(Y_{3}\right)\) is a finite set of points of \(\mathbb{S}^{1}\), that we call the set of critical times. If \(t_{0}\) is not a critical time, the apparent contour (given by a normal slice, i.e. the transversal intersection of \(Y_{1} \cup Y_{2} \cup Y_{3}\) with \(\left\{t=t_{0}\right\}\) ) varies smoothly, and its topology does not change. Hence we can find a smooth path of diffeomorphisms of \(\mathbb{R}^{2}\) connecting the apparent contours at times \(t_{1}\) and \(t_{2}\) whenever the interval \(\left[t_{1}, t_{2}\right]\) does not contain any critical time. Moreover, in view of the classification results on singularities of stable mappings between 3-manifolds (Section 2), we obtain the following corollary (compare with Figure 3).

Corollary 6.1. A point \((y, t) \in \operatorname{crit}\left(p_{\mid Y_{2}}\right) \cup Y_{3}\) lies in one of the following classes, each determining a move in the list of Section 4:

- -ð y ; t Þ a \(Y_{2}\) 2 is a local maximum (resp. a local minimum) of a double curve: moves of type \(K(resp.oftypeK1)\).

- -ð y ; t Þ a \(Y_{1}\) 2 is a local maximum (resp. local minimum) of a cusp curve that bounds folds going downwards (resp. upwards) : move \(L(resp.moveL1)\).

- -ð y ; t Þ a \(Y_{1}\) 2 is a local maximum (resp. local minimum) of a cusp curve that bounds folds going upwards (resp. downwards) : move \(B(resp.moveB1)\).

- -ð y ; t Þ a Y 1 3 : moves of type S.

- -ð y ; t Þ a Y 3 3 : moves of type T.

- -ð y ; t Þ a Y 2 3 : moves of type C.

Remark 6.2. A more precise classification of each move can be obtained by looking at the orientation of the various folds involved and at the relative depth of the preimages in the singular set \(\bar{X}_{1}=S_{1}\left(F_{\tilde{\gamma}}\right)\) with respect to the regular preimages. For example, a points in \(Y_{3}^{3}\) has three distinct preimages in \(X_{1}\) which can be ordered according to the \(z\) coordinate (dropped by the projection \(\pi\) ). Each of the three involved folds, which are transversal with respect to "time" \(t\), carries a natural orientation and hence contributes with a sign. The relative depth of the three singular preimages with respect to the remaining regular preimages provides for the three nonnegative integers parameters as explained in Remark 4.3. Note that a cusp curve forces the orientation of the two adjacent folds. In this way we have a precise one-to-one correspondence between the list of moves of Section 4 and the list in Corollary 6.1.

Remark 6.3. Corollary 6.1 can be obtained as a special case of [4, Theorem 3.5.5] in which Carter, Rieger and Saito consider isotopies of immersed surfaces \(F\) in \(\mathbb{R}^{3}\), realized as projections of embedded surfaces in \(\mathbb{R}^{4}\), possibly with pinch points. They seek all codimension one singularities of maps \(\mathbb{R}^{3} \supset F \rightarrow\) \(\mathbb{R} \times \mathbb{R} \rightarrow \mathbb{R}\). The majority of these singularities are related to self-intersections and pinch points of \(F\), which are excluded in our setting. Moreover, they also consider singularities that arise from the presence of a height function \(\mathbb{R} \times \mathbb{R} \rightarrow \mathbb{R}\) which we do not need here. The remaining codimension one singularities correspond to those listed in Corollary 6.1. To be more specific, [4, Figure 9(row 1, column 1)] corresponds to move L; [4, Figure 9(2,1)] corresponds to B; [4, Figure \(9(3,1)\) ] corresponds to S; [4, Figure \(10(1,1)\) ] corresponds to K; [4, Figure 10(1,2)] corresponds to C ; [4, Figure 10(2,1)] corresponds to T. Theorem [4, 3.2.3] is a simpler version of [4, Theorem 3.5.5], in which the height function is not considered, and hence it is more close to Corollary 6.1; it follows by combining the classifications given by [13], [20] and [24].

![Figure 3. Each row represents the fold surfaces Y 1 near di¤erent types of critical points for p](/Users/evanthayer/Projects/paperx/docs/2012_completeness_of_reidemeister_type_moves_for_surfaces_embedded_in_three_dimensional_space/figures/figure-3-p017.png)

*Figure 3. Each row represents the fold surfaces Y 1 near di¤erent types of critical points for p: K, L, inverse of B, inverse of S, C, T. The second and third pictures on each row show the cutting with t ¼ const (apparent contour) before and after the critical value.*

## References

- V. I. Arnold-V. V. Goryunov-O. V. Lyashko-V. A. Vasilev. Dynamical Systems VIII, Springer-Verlag, Berlin 1993.

- V. I. Arnold-S. M. Gusein-Zade-A. N. Varchenko. Singularities of Di¤erentiable Maps, Volume I, Birkha ¨user, Boston 1985.

- G. Bellettini-V. Beorchia-M. Paolini. Topological and variational properties of a model for the reconstruction of three-dimensional transparent images with selfocclusions, J. Math. Imaging Vision, 32 (2008), 265-291.

- J. S. Carter-J. H. Rieger-M. Saito. A combinatorial description of knotted surfaces and their isotopies, Adv. Math. 127 (1997), 1-51.

- J. S. Carter-M. Saito. Syzigies among elementary string interactions in 2 þ 1 dimensions, Lett. Math. Phys. 23 (1991) 4, 287-300.

- J. S. Carter-M. Saito. Reidemeister moves for surfaces isotopies and their interpretation as moves to movies, J. Knot Theory Ramifications 2 (1993) 3, 251-284.

- J. S. Carter-M. Saito. Knotted Surfaces and Their Diagrams, Mathematical Surveys Monographs 55, Amer. Math. Soc., Providence, RI, 1998.

- J. S. Carter-S. Kamada-M. Saito. Surfaces in 4-Space, Encyclopaedia of Mathematical Sciences, 142, Springer-Verlag, 2004.

- J. Cerf. La stratification naturelle des espace de fonctions di¤e ´rentiables re ´elles et le the ´ore `me de la pseudo-isotopie, Publ. Math. Inst. Hautes E ´ tudes Sci. (1970), 5-170.

- L. A. Favaro-C. M. Mendes. Global stability for diagrams of di¤erentiable applications, Ann. Inst. Fourier (Grenoble) 36 (1986), 133-153.

- M. Golubitsky-V. Guillemin. Stable Mappings and Their Singularities, SpringerVerlag, New York 1974.

- M. Goresky-R. MacPherson. Stratified Morse Theory, Springer-Verlag, Berlin 1988.

- V. V. Goryunov. Monodromy of the image of a mapping, Funct. Anal. Appl. 25 (1991), 174-180.

- M. W. Hirsch. Di¤erential Topology, Springer-Verlag, New-York 1976.

- D. A. Huffman. Impossible objects as nonsense sentences, in Machine Intelligence 6, B. Meltzer and D. Michie Eds., American Elsevier Publishing Co., New York 1971.

- S. Mancini-M. A. S. Ruas. Bifurcations of generic parameter families of functions on foliated manifolds, Math. Scand. 72, (1993), 5-19.

- I. Nakai. Topological stability theorem for composite mappings, Ann. Inst. Fourier, 39 (1989), 459-500.

- T. Ohmoto-F. Aicardi. first order local invariants of apparent contours, Topology, 45 (2007), 27-45.

- R. Pignoni. Density and stability of Morse functions on a stratified space, Ann. Scuola Norm. Sup. Pisa Cl. Sci., 6 (1979), 593-608.

- J. H. Rieger. On the complexity and computation of view graph of piecewise smooth algebraic surfaces, Phil. Trans. R. Soc. London A (1996), 354, 1899-1940.

- D. Roseman. Reidemeister-type moves for surfaces in four dimensional space, [A] Jones, Vaughan F. R. (ed) et al, Knot theory. Proceedings of the mini-semester, Warsaw, Poland 1995. Banach Cent. Publ. 42, 347-380 (1998).

- R. Thom. Stabilite ´ Structurelle et Morphoge ´ne `se, W.A. Benjamin, Inc., Reading, Massachussetts, 1972.

- G. Wassermann. Stability of unfoldings in space and time, Acta Math. 135 (1975), 57-128.

- J. M. West. The di¤erential geometry of the crosscap, Ph.D. thesis, Univ. of Liverpool, England 1995.

- H. Whitney. On singularities of mappings of euclidean spaces. I. Mappings of the plane into the plane, Ann. of Math., 62 (1955), 374-410.

- L. R. Williams. Topological reconstruction of a smooth manifold-solid from its occluding contour, Int. J. Computer Vision, 23 (1997), 93-108.

- L. C. Wilson. Equivalence of stable mappings between two-dimensional manifolds, J. Di¤erential Geom., 11 (1976), 1-14.

- Received 4 April 2011, and in revised form 26 June 2011. Dipartimento di Matematica Universita ` di Roma Tor Vergata via della Ricerca Scientifica 1, 00133 Roma, Italy Giovanni Bellettini and INFN Laboratori Nazionali di Frascati, Frascati, Italy E-mail: Giovanni.Bellettini@lnf.infn.it Dipartimento di Matematica e Informatica Valentina Beorchia Universita ` di Trieste via Valerio 12 b, 34127 Trieste, Italy E-mail: beorchia@units.it Maurizio Paolini Dipartimento di Matematica Universita ` Cattolica ''Sacro Cuore'' via Trieste 17, 25121 Brescia, Italy E-mail: paolini@dmf.unicatt.it
