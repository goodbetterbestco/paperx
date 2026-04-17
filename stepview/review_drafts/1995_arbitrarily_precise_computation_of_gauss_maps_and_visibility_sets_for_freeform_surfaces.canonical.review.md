# Arbitrarily Precise Computation of Gauss Maps and Visibility Sets for Freeform Surfaces

Gershon Elber3, Elaine Cohen, Open Access Support provided by

Department of Computer Science Department of Computer Science
Technion, Israel Institute of Technology University of Utah
Haifa 32000, Israel Salt Lake City, UT 84112 USA GERSHON ELBER , Technion - Israel Institute of Technology, Haifa, Israel The University of Utah, Salt Lake City, UT, United States The University of Utah Technion - Israel Institute of Technology 3SOLID95: Third ACM SIGGRAPH Symposium on Solid Modeling &amp; Applications May 17 - 19, 1995 Utah, Salt Lake City, USA

## Abstract

PDF Download 218013.218073.pdf 07 April 2026 Total Citations: 22 Total Downloads: 497

## 1 Introduction

The directions from which a surface is completely visible are of fundamental interest for many applications. In graphics, this problem is closely related to the hidden surface removal problem [8, 9]. In manufacturing, a surface can be machined only when it can be reached or “seen” by a tool. In [21], the directions from which a feature can be approached for machining purposes without interference is investigated. The Gauss map of surface S [2, 17], G,, and the visibility set of surface S [3, 4, 20], V,, can be used for both shape recognition and matching since they provide a unique characterization of a surface. Throughout this paper, a srrbscript will denote the surface for which the map or the set is computed. We first review some intuitive elementary aspects of visibility. For a point p on a surface S to be visible to an observer’s eye located at a point E two tests must be satisfied. first, p must be “forward facing” and not on the ‘back side” of S, which can be determined by locally examining the surface. Second, p cannot be occluded by another part of S or by a different surface in the scene, that is, another surface lies along the ray from the eye to p but is closer to the eye than p. This Iwt property can only be determined by examining global properties. We will more rigorously define the first requirement, and consider collections of such eye points.

Definition 1 We define g,, the Gauss map o~ a surface S, to be a map from the surface S to the unit sphere, S2, which takes each point p G S to its unit normal vector, n>. That definition 2 Given a unit direction vector r7, we say that a point \(p_{6}\) S, is locally visible from direction C iff (r7, n;) >0.

Denote by ltzt(S) the interior of S. Then, definition 3 Given a unit direction vector ii, we say that a point p E Int(S) has local neighborhood visibility from

271 visibility set, V,, of \(S(u,o)\) in section 4. V, bounds all the directions from which \(S(u,v)\) is completely locally visible

![Figure 1](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-1-p003.png)

*Figure 1: A surface can be locally visible, yet can hide itself globally by looping around itself.*

direction Z ifl there exist a small open disk ‘D C In$(S) such that each q E D :s locally visible from 0.

Definition 4 The uisibilityset of surface S, V., is the set of points on S2 that correspond to directions from which every ~omt ~ ~ Int(S) has, local neighborhood visibility. That is, v E S M also m V, ~ffor all p G Int(S), p has local neighborhood visibility from ii. We say that S is locally visible from each element of V, definition 4 prescribes the set of directions from which the entire surface is locally visible. Those points are only globally visible if the surface does not loop around itself, as that in Figure 1, or if another surface is not closer to the eye. A common and simple method to determine a bound on the normal directions of a given surface S is based upon the computation of a bounding cone [16, 19] of all possible normal directions of S. The normal cone is derived from the cross product relation between the two cones representing all the possible partial derivative directions. The normal cone bound of the image of the Gauss map of S is fairly loose and can provide insufficient information in many applications. In this paper, a method is presented to compute an arbitrarily precise bound on the directions from which a surface is completely locally visible. That is, we present an approach to the computation of ~, and Vs that prescribes an arbitrary precise representation of the boundaries of ~, and V., not a conical upper bound. Unlike existing schemes that exercise bounding cones [16, 19] or convex hull bounds using a mesh of the normal surface [15], the method presented herein can be easily extended to provide ~. and V, of a trimmed surface or even of a set of several trimmed surfaces with arbitrary precision. Section 2 discusses the necessary background. In section 3, we develop a method to compute the image of the Gauss map, g., of a given surface S. ~,, aa a unit vector field [2], is represented and bounded by its boundary curves on the unit sphere, S2. One application that demonstrates the importance of the Gauss map is the computation of the visibility set of a surface. We follow the approach proposed in [3, 4] and generalize it to support freeform surfaces. Using the methods presented herein, the image of ~. is used to compute the and is also represented by determining its boundary curves on S2. All figures in this paper were created from an implementation of the algorithms using the Alpha.1 solid modeler developed at the University of Utah.

## 2 Background

Thus,

A surface is considered completely locally visible from direction d if the following holds.

Definition 5 Giuen a Cl surface \(S(W,v)\), and a vector d, \(S(u,v)\) is completely locally visible from direction G iff each point in S is locally visible from il.

A surface S is partially locally visible from G if only some of the points in S are locally visible from d. As defined, surface normals must point to the “inside” of the surface (object). Using definition 5, one can immediately see from definition 4 that Corollary 1 v. = {d \(I(f5,Jvs(%w)\)) 2 O,vrl, w, Ipll = 1}.

V, C S2 since it contains only unit vectors. In this paper, we compute ~V,, the boundary of V., for a given surface \(S(u,v)\). We assume that the surface is completely locally visible from at least one direction, i.e. V, is not empty. This is obviously not always the case. S2 itself, considered as a single surface, has no direction from which it is completely locally visible. However, a surface can always be subdivided and tested using loose bounding techniques, such as the bounding cones [16, 19], until this criterion holds. Whenever possible, the unnormalized normal surface will be used instead of N, (u, o). The unnormalized normal, referred to as ~s, is defined as,

JQ-s(u, v) = - x -, (2) which has a parametrization dependent magnitude. In the ensuing discussion, we symbolically compute the unnormalized normal surface of N5, and refer to it FM~. \(S(u,v)\) is assumed to be regular, that is ll~,(u, v)II # O, for all u, v, and sufficiently differentiable so that ~, (u, v) and \(M(u,o)\) are continuous. algorithms to symbolically compute the sum, difference, and product of B-spline or B6zier surfaces are well known [6, 7, 10, 18]. This paper will exercise symbolic computation and representation of surfaces, computed as scalar and vector fields that represent properties such as curvature [1I], normals [8], offset error [13], or surface slopes and speed bounds [12]. For example, the BLzier or NURBS representations of ~, (u, v) is a normal vector field that can be symbolically computed aa the (cross) product of the partial derivatives of \(S(u,0)\) (equation (2)).

272 Let q E “R’. Ilqll # o Let, L be a ray from the origin 0 to q. and let q,, he the point where L intersects S2.

Definition 6 q t~ said to fxcentraliy pro~ected@\(n_{0}\) onto,S) t~s~~lg[,, and that g,.J is tts projected point. This mapp2ng I.$callrff a central or gnomonic /,5] pro]ectton. in the ensuing discussion and unless stated otherwise, @ is assumed to be t he center of the central projection. Let P he an arbitrary plane t hat does not contain 0, and qf, be the intersection point of L with P, definition 7 q IS sotd to ht. wntrdly projected onto a plane 1’ ?~s~rlg I,, and that qP is lts projected point. [n definition 7, we notice that the perspective projection, (Ised in computer graphics, is a special case of a central

![Figure 2](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-2-p004.png)

*Figure 2: This simple bicubic surface is used throughout*

Definition 8.4 closed curt~e, \(C(t)\) \(C_{723,is}\) said to be centrally convex, tf there ez2,9t a plane P that cioes not contain c’J ~uc/t that thr cc ntra{ projection of \(C(t)\) onto P is a closed conw. r curt,, 7%rIf !s, thr l:nc segment ronnechng two arbtlro~y potnt.s on th(central projection 0} C’(t) onto P is /O(fI//V u,lthirl th(closrd rtg~on of P bounded by the r-erz.tral l)rl)]t (l(orr of (“(i]

## 3 Computation of the Image of the Gauss Map

(;ivcn an unnormalized normal surface,~’r,(u, u) our goal is to compute the image of the C,auss map and represent the boundary of this image. OG.., on S2. One can compute a loose bound on the image of the Gauss map using cones bounding the pa,rtia]s derivatives of S and then compute the bounding cone for the normal field as t heir cross product [16, 19]. Alternatively, one could cnmpute,~(. (u, u) symbolically, centrally project it onto S2 and compute a bound on the projected image. In [15]. the control mesh of fi, (u, u), represented as a IWier surface. was centrally projected onto,>”2and used a.s a bound for the directions of the normafs of the surface. In this sect ion, we provide an arbitrarily precise computation of f?~, by detecting the exact extreme points of.i:.(u, u). A surface ciisplayecf in an orthographic view can assume extreme values only along its boundary or its silhouette locations, Similarly, a surface centrally projected onto a plane can assume extreme values on the plane only along its boundary or its central silhouette. In a centraf projec-t Ion, t be viewing direction is a line through both the origin, (!!, and the viewed point.\(S(u,v)\). Therefore, the central projection viewing direction of \(S(rt,v)\) is collinear with,\(S(u,v]–(9==,$(U,71)\).

Definition 9 The central silhouette set o] S, S,, is the set of Pnratneter uahes for uJIzch N, is perpendicular to the cfntr-frl projection t,ierotng direction, s, = {(u, t!)l(.s(i,, f,),.ti, (u, t)) =0} (3)

To find the extreme values that.ti, can assume in a (entral projection. one needs to compute the boundaries and the central silhouette of.~,. At a silhouette point.~~.(uo, w) (see Figure 3) the vector.1. (wO, w) is perpendicular to.~_$(u“, 110). In order to compute the silhouette curves of.V, (u, v), one can compute the unnorrnalized normal vector field of,%(u, I)). ,~?(u, t), and find the zero set of their inner product, s= {(u,?) \(I(Jo,(u,r)\),.i(?(rf, ?,)\(\wp=0\)} , (’t] to yield the set of all central silhouette points. For a surface,$, (.~,, ~~) can be symbolically computed and represented as a piecewise polynomial or rational scalar field [6, 7, I[), 18]. Once a representation is found, subdivision based techniques can be used to find an arbitrarily precise approximation to its zero set [10], as a set of piecewise linear curves. It is necessary to compute square roots to find the projection of the boundary and central silhouette curvw of :{: onto S2. The square root operation is not representable. in general, as (piecewise) polynomial or rational curves. As a result, an arbitrarily dense set of points can be determined using the central projection. a set that defines a piecewise linear approximation of the boundary and central silhouette curves projected onto.$2. The smallest locally simply connected set that contains the boundary and the r-entral silhouette curves of h’, is the exact boundary of G,. Thus, ~, can be computed using a two-dimensional boolean union operation on all the regions bounded by the extracted boundary and silhouette curves on S2. The set of boundary and silhouette curves of.(. (u. u) may be topologically complex (see Figure 4). making the computation of this two-dimensional boolean union difficult. Fortunately, for the application demonstrated herein. namely the computation of the visibility set [3. 4], V,, it is unnecessary to compute the exact boundaries of ~, in order to find the exact houndaries of V.. The approach to the computation of V, from ~, generalizes the approach taken in [3, 4] to encompass freeform surface representations.

Lemma 1 The dzrectlonal domain from whlrh a.surjacc i.q completely uiszble, V,, i.s centrally convex, Proofi For a vector & E.S2 there exists a hemisphere ‘H c S2 from which a surface point with normal & is locally visible (see Figure 5),

?-l holds all vectors in S2 that have a nonnegative inner product with & (I)efinition 5). For.$(u, r) to be visible from

273

![Figure 3](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-3-p005.png)

*Figure 3: Central view extrema occur along boundaries and central silhouettes. Two-dimensional (a) and three-dimensional (b) cases are considered. The central silhouette set of fi.(u, v) (for the surface S(u, v) in Figure 2, in (b)) is equal to the zero set of (~,(u, v), fi(u, v)). At (UO,VO)we find such a central silhouette point.*

![Figure 4](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-4-p005.png)

*Figure 4: The silhouette set in the central projection of Af~(u, v) can be extremely complex. On the left, is a bicubic surface, with its complex normal surface, ~., in the middle. The boundaries and central silhouette set of ~~ are projected on S2, on the right.*

274

![Figure 5](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-5-p006.png)

*Figure 5: Each vector, ~ is associated with a hemisphere*

a given direction d, & E R’, V?f of all vectors in Af, (ri, v). That is, only a direction d contained in (the intersection of) all hemispheres of all unit vectors in N’, (u, u) is in V.. Centrally mapped onto a plane, a hemisphere is a halfplane. Because an intersection of convex regions is convex, the domain of directions from which a surface is completely visible, V,, is centrally convex as well. I Lemma 2 Let R be a region O) a cylinder. Then, Jf, (and ~.) is a great circle s-egment in S2 and V, is equal to the intersection of the two hemispheres associated with the two end vectors of G, {Figure 7).

Proofi Without loss of generality, one can assume R is a region of a cylinder around the z axis. That is, \(R(rI,v)\) == (aces(u), asin(u), v). The unit normal of region R is equal to N,(u, u) = (–cos(u), –sin(u), O) and is obviously a great circle segment on S2 that is also in the zy plane. Call the great circle segment C. Let ?i be a hemisphere associated with a vector in C. Let a“] and ri”zbe the two vectors of the end points of the arc of C and let ‘HI and ?ip be the two hemispheres associated with a-l and ci-z, respectively. &H, the great circle boundary of H, is in a plane that always contains the z axis. Therefore, by moving the vector & along C in the zy plane, the great circle Wi rotates around the z axis. This transformation is continuous and monotone, when R is regular. Since a-l and a-z provide the two extreme locations and HI and ‘Hz form the hemispheres for the two extrema locations, the intersection of all hemispheres associated with a vector in ~, is equal to H, (1 Hz. U Corollary 2 Suppose the Gauss map of S is two isolated points on S2. Then, V,, is the same as if ~, was the great ctrclr segment connecting the two vectors on S2.

```text
Given ~., for any two vectors ci-l, a-z ~ g,, one can in- clude a great circle segment between them, selecting the smaller one (a-l and a-l have at least two such segments, one that is greater then or equal to 180 degrees and one that is less than or equal to that), without affecting V,. Much like a planar convex hull, in which for each two points in the convex hull, the line segment between the two points is also in the convex hull, for each two points in a central convex hull on S2, the great circle segment between them is also contained in the central convex hull:
```

![Figure 6](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-6-p006.png)

*Figure 6: Central convex hull (dashed) of the silhouette and boundary curves of Af, in Figure 4.*

Definition 10 The central convex hull, CM C S2, of some set S C__S2, is the smaliest subset of S2 containing bounded by a centrally convez curve (definition 8).

The edges of CM are great circle segments, seen as straight fines from the origin. For any two points in C?f, the great circle segment on S2 between them is completely in C7f, Specifically, for any two points in ~,, one can add the great circle segment between them having no affect on the visibility set. Applying Coro~ary 2 aflows one to employ the central convex hull of g,, G,, instead of the exact and POSSIBLY topologically complex boundary of ~~ (see Figures 4 and 6), while obtaining the same tight bound on the visibility set, V.. The convex hull must be computed centrally. That is, edges of the convex hull are great circle segments on S2 (see Figures 6 and 8). Optimal planar convex hull algorithms have been known for sometime [1, 14]. We cannot use planar convex hull algorithms directly, since we are interested in the central convex hull. A central projection from S2 onto a plane (definition 7) that maps great circles to straight lines is first employed. Then, we apply the planar convex hrdf algorithm to the two dimensional planar set only to centrally project the edges of the convex hull back onto S2 as great circles. ~, and V, are required to strictly fit into a hemisphere so that the mapping to a plane is homomorphic, a requirement equivalent to the constraint for the surface to be visible in the local from at le~t one direction. Satisfying this requirement always allows one to uniquely project great circle

275

![Figure 7](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-7-p007.png)

*Figure 7: Let G, be a great circle segment. Then, the boundary of V, (dotted) is the boundary of the intersection of the two*

Fijrure 7: Let G, be a meat circle segment. Then, the boundary of V. (dotted) is the boundary of the intersection of the two he~ispheres ~sociate~ with the en~vectors of ~s.

segments ss line segments on the Z = 1 plane. It is necessary for neither ~, nor V. to be in the Z > 0 hemisphere. Instead, a rotation, 72., could map ~s or V, into the upper hemisphere. Further, if P is the plane through the origin that dichotomizes S2 into two hemispheres, one strictly containing ~, (or V.), then 72 is the mapping that transforms the normal of P to the z axis. One can find P by using loose bounds such as bounding cones [16, 19] or by computing the three dimensional convex hull of g, (or Vs). Alternatively, an \(O(n)\) algorithm to rotate points on a unit sphere as far away from the equator as possible, is described in [3]. Therefore, an algorithm to compute the central convex hull of g. for surface \(S(U,v)\) follows,

```text
Input: S(u, v), input surface;
output : ~s, central convex hull Gauss map of S(M, v);
Algorithm: ~.(u,v) + uzmormalized normal surface of S(u, v);
B < Boundaries of ~.(u, v), projected onto S2 ;
S e Central silhouettes of fi,(a,v), as the zero set of (~~,~), projected onto S2;
‘R e Flotation to map B andS to the Z>O hemisphere;
~~ + Central convex hull of R(BuS);
```

In section 4, ~, is used to compute the visibility set of \(S(ri,v)\), vs.

## 4 Computing the Vkibility Set

~~isnow usedto compute atight bound onV,.

Lemma 3 The visibility set derived from~, i~the~ame thevisibility setderivedjrom the boundoryof g,, 8GS. as Proof: Recall t~at ~, is centrally convex. For each interi~r vector & c ~,, there exists a great circle segment C C_~,, such that & G C and the two end vectors of C are in i3~~. Since the visibility set of C can be determined from its two end vectors in d~~ by Lemma 2, weco~clude that it is enough to examine only (the vectors in) ~~, in order to determine visibility setfrom~~m The approximated boundary of ~, is a set of great circle segments. By Lemma 2, it follows immediately that it is enough to examine the end vectors of these~reat circle segmentsin order to determine the visibility of~, (and g.). These end vectors arethevertices oft?~,. Lemma 3 suggests an efficient wa~ to compute V. from ~=. Given the set of vertices of L%s, Y, we azsociate a hemisphere 7-f, (Figure 5) with each vertex ~, \(E_{3}\). The intersections of all these hemispheres is Vs:

Asin section 3, one can use the central projection and project these hemisphere boundaries (great circles) onto the plane Z= lfromthe ori in. These great circles are mapped P tolines intheplane(?f, , theprojection of ’Hi, is now a half plane defined by a fine). Furthermore, since ~, is centrally convex, the intersection problem is reduced to intersecting each line in the plane only with its two neighbors, the previous fine and the next line. Therefore, the complexity of thk stage is linear (see algorithm 1 for R):

276

![Figure 8](/Users/evanthayer/Projects/paperx/docs/1995_arbitrarily_precise_computation_of_gauss_maps_and_visibility_sets_for_freeform_surfaces/figures/figure-8-p008.png)

*Figure 8: Convex hull (dashed) is computed for the projected great circles as lines in the plane Z = 1, using central (of surface in figure 2)*

```text
~,, central convex hull of the image of ~,;
output : V,, tightly bounded visibility set of S;
Algorithm: tit + hemispheres associated with vertices of 7?(F.);
?i~ ~ ~H, centrally projected on plane z=];
V: e intersection set of 13?i, half planes;
V, * ‘R-l (V~) mapped back to S2;
```

## 5 Extensions

Bounding cones based methods [16, 19] usually examine the entire parametric domain of the surface. Adopting these methods to support trimmed surfaces can be difficult. In contrast, the method presented herein can be easily extended to support trimmed surfaces. The boundary of the Gauss map will be computed for the trimmed boundary curves of ~,(u, u), and its trimmed central silhouette curves. No other part of the algorithms developed herein need to be changed. Figure lo(a) shows a trimmed surface constructed from the surface in Figure 2. In Figure 10(b), the extracted silhouette and boundary curves of its Gauss map, its convex hull, and the visibility set (in dotted lines), are all shown mapped onto S2. Figure 11(a) shows a trimmed region out of S2. Obviously, the Gauss map of this surface is identical to the surface itself. In Figure n(b) the Gauss map with its convex hull and the resulting visibility set are shown. Given a model A-4consisting of several, possibly trimmed, surfaces one can now answer the query, whether or not there exists a direction from which all surfaces are visible. By computing V, for each surface, such a direction exists iff fl,,~~ V,, # 4. Furthermore, any vector from the centrally convex set of fl,, e~ Vs, can be exploited.ss a direction from which all surfaces of &l are visible in the local.

## 6 Conclusion

An algorithm to provide a tight bound on the visibility directions of a given surface \(S(u,v)\) is described, combined with an algorithm to compute bounds on the Gauss mapof S. This bound is tight since it provides the (centrally convex) visibility set V, of \(S(U)\) u). The algorithm can be easily extended to provide a tight visibility bound for a trimmed surface, and/or a set of surfaces. The symbolic computation has a fixed complexity, given the order and continuity of the surface. The complexity of the convex hull computation of the image of the Gauss map is rdog(n), where n is the number of vertices, which is the optimal time. The visibility set is computed in linear time from the Gauss map. The silhouette extraction (zero set of (A/~(u, t)), \(M(u,u)\))) is the only numeric computation in this algorithm. Subdivision based techniques [10] were used to compute its zero set.

## 7 Acknowledgment

The authors are grateful to Rich Riesenfeld for his valuable remarks on the various drafts of this paper.

## References

- K. R. Andreson. A Reevaluation of an efficient algorithm for Determining the Convex Hull of a Finite planar Set. Information Processing letters 7 (1978).53-55. M. P. DoCarmo. Differential Geometry of curves and Surfaces. Prentice-Hall 1976. L. L. Chen and T. C. Woo. computational Geometry on the Sphere With applications to Automated Machining, Technical Report No. 89-30, Department of Industrial and Operations engineering, University of Michigan, August 1989. L. L. Chen, Shuo-Yan Chou, and T. C. Woo. Separating and Intersecting Spherical Polygons: Computing Machinability on Three-, Fourand Five-Axis Numerically Controlled Machines. ACM Transaction on Graphics, Vol. 12, No. 4, pp 305-326, october 1993. r. \ /. F

- Figure 9: V. (dotted) is computed as intersection of hemisphere boundaries (great circles) of ~, vertices (dashed) as lines onto the plane Z = 1 and mapped back (of surface in Figure 2). projected

- Figure 10: A trimmed region from the surface in Figure 2 is shown in (a). In (b), shown are its ~, (dashed), the and boundary curves of its Af..(u, v), and its V, (dotted). silhouette (a) Figure I1: In (a). is a trimmed region from S°. In (b). is its G.. G. (dashed). and V. (dotted).

- [(i] Figure I 1: In (a), is a trimmmj region from.5’2

- S. lyanaga. }’. Kawarla and K O. hlay. Encyclopedic I)ic[iouary of Afatbernatics. The M1’1’Press ~’ambricfge, ilassachusetts. and London, England.

- (;. l~arin (‘Ilrves and Surfaces for (“’ornputer Aided (;comctric. Iksign \cademic Prc>s, Inc. Third Edition 199:1.

- R. ‘1’.Farouki and \’. ‘I’. Rajan. algorithms For F’olynomials In Bernstein IJorm Computer Aided Geometric [)esign 5. pp 1-26, 1!)88.

- (“~. Elbcr and E. (’ohell. Hidden C’urve removal for LInt rimmed and “lrimmed N (J Rf3 Surfaces. Technical Report No. 89-019. c‘omputer Science, University of (“lab.

- (;. Elber and E. ~’ohen. Hidden (“’urve removal for Free Form Surfaces SIGGR.\PH 90, pp 9.5-104.

- (;. Kltxr. Free Form Surface analysis using a Hybrid of Symbolic and Numeric Computation Ph.D. thesis. l’ui~ersily of (It Al, (’ompnt(r %icnce I)epart ment, 1992.

- (; l;lber an(l E. C‘ohcn. Second order Surface analysis-lsing tf~t,ri(i Synlbolic and Numeric Operators. ACM ‘1’ransart ion on (“;raphics, Vol. 12, No. 2, pp 160-178,:\pril 19$1:!.

- (;. Elbcr and E. Coheli. Hybrid Symbolic and Numeric operators as Tools for analysis of Freeform Surfaces. h!odeliug in (’omputer Graphics, B. Falcidieno and 1’. l,. Kunii (Eds.), \Vorking C’onferencc on Geometric Modeling in Conlputer Graphics (IFIP TC 5/WC 5.10), (: f,llm’a 199.1.

- (;. f;ltwr and E. (‘oheu. Error Bounded Variable Dis-t ante CMfs-,t Operator for Free Form curves and Surfaces. luternationat Journal of ~ornputational Geornetry and Applications. Vol. 1., No. 1. pp 67-78, March 199[.

- R 1,. Graham. An Efficirnt algorithm for Determining the (’OUVCXHull of a Finite planar Set. Information Processing letters 1 (1972) 13?-133. ill. E. Hohmeyer. A SUrfa(c lntcrsectiorr algorithm Based on loop t)etettiou Symposium in Solid Mod(l-ing Foundations and C’AI)/-” A\l Applications. Austin, ‘rexas, June 5-7, 1991. I), S. Kim. (’ones on Bfzier (‘urves and Surfaces. Ph.]). dissertation, T’nivcrsity of Nlichigan. 19!)1). R. S. hfillman and (;. 1). Parker. Elements of I)iffer~n-tial Geometry. Prentice-Hall Inc. 1977. K. Morken, Some ldentitir+ for Products and Degree Raising of Splines. (’onstructivc:ipproximation 7, pp 195-209, 1991. T. W_. Se&rberg and Ray J. Meyers. Loop Detection in Surface Patr-h Intersmtions. (’omputer Aided ~;eometric Design.5, pp 161-171, 198A’, S. H. Suh and 1. K. fiang. Process Planning for \lultiAxis NC \lachining of Free Surfaces. To Appear in IJPR. ‘I’. J. ‘1’seng and S. Joshi. Determining F,a+ible ‘l’ooapproach Directions for Machining Bezier (“urves and Surfaces. Computer Aided Design. Vol. ~:;, No, 5. pl~ 367-378, June 1991.
