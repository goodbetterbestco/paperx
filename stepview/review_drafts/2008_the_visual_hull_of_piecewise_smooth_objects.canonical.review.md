# The Visual Hull of Piecewise Smooth Objects

Andrea Bottino, Aldo Laurentini, Dipartimento di Automatica ed Informatica, Politecnico di Torino, Corso Duca degli Abruzzi , Torino, Italy

© 2006 Elsevier Inc. All rights reserved.

## Abstract

Keywords: Computer vision; Shape-from-silhouettes; Visual hull; Piecewise smooth objects; CAD objects URL: www.polito.it cgvg (A. Bottino). ScienceDirect Computer Vision and Image Understanding www.elsevier.com locate cviu

## Introduction

Reconstructing 3D shapes is a fundamental research topic. Many techniques have been proposed for this purpose, depending first on the sensors used. Active 3D scanning is currently a leading technology. However, 3D scanners are expensive and affected by several limitations. In a number of practical applications, as those involving motion analysis, traditional computer vision techniques based on 2D images captured by inexpensive cameras are preferable or required Many computer vision algorithms for reconstructing or recognizing 3D objects are based on the object silhouette, which is the image area bounded by the contours that occlude the background. silhouettes are often easy to extract from 2D images. In addition, the main silhouettebased reconstruction approach, volume intersection (VI), does not require solving the difficult and time-consuming problem of finding correspondences between various images. Since the introduction of the idea by Baumgart [4], many shape-from-silhouettes algorithms have been proposed, such as [2,10,15,33-35,50]. Some of these algorithms (for instance [35]) produce a textured object. silhouettes have been also used for extracting shape and orientation of rotating objects ([36,51,52]). Recent algorithms refine the reconstruction combining silhouettes and other shape cues ([11,14,19,27), as the photometric constraints introduced by Seitz and Dyer [46]. Generating silhouettes is also relevant to computer graphics: a survey of techniques for producing them can be found in [26]. The visual hull VH(O) [30] of an object O summarizes all the properties of O concerning its silhouettes (or shadows produced by point light sources). It is the largest object that produces the same silhouettes as O observed from viewpoints outside the convex hull of O. It is also the closest approximation of O that can be determined from its silhouettes using viewpoints outside the convex hull. Details can be found in [30] The visual hull also allows making inferences about the true shape of an object [31], constructing next-best-view VI algorithms [8], and understanding the capabilities of tactile robotic probes [6]. In the current shape-from-silhouette literature, the term visual hull (sometimes inferred visual hull) is used for the object reconstructed from silhouettes. algorithms for computing the VH of a given object can be found in [5,30,32,38] for polygons, polyhedra, solids of revolution and smooth curved objects. However, most of the objects to be dealt with in vision problems do not fall in these simple categories. A much more general category, enclosing polyhedra, solid of revolutions and smooth surface objects as particular cases, is that of piecewise smooth objects. These are also the objects produced by CAD volume or surface modeling packages.

In this paper we present the theory of the visual hull of general objects with piecewise smooth surfaces. The paper makes use of some of the results presented in our previous paper [5], concerning the case of smooth curved objects. However, the case of piecewise smooth objects requires a more complex analysis. In fact, for generic objects it can be shown that the surfaces relevant to the visual hull are those produced by particular lines making two or three contact with the object. The types of surfaces are two for smooth objects, but we will see that they are nine for piecewise smooth objects. Since constructing the visual hull requires to construct an arrangement with these surfaces, to reduce their number and extension is of paramount importance. Therefore, a part of the paper is devoted to finding rules for pruning and trimming these surfaces. For this purpose, the techniques used in [5] for smooth surfaces, based on the principal curvatures, are not sufficient, and new more general techniques have been used. Finally, a new output-sensitive algorithm for computing the visual hull will be presented and its complexity analyzed. The algorithm only determines the part of the visual hull connected to the object, but it will be shown that only very unlikely objects have visual hulls with unconnected parts. We will also establish a relation between the visual hull and the aspect graph (AG) of piecewise smooth objects. The aspect graph, a user-centered object representation first proposed by Koenderink and van Doorn [28], collects in a graph all the topologically different line drawings of an object or aspects. The line drawings are the projections of the occluding contours and creases of an object. The vertices of the graph, representing aspects, are connected by edges representing topological changes (visual events, VE), which occur when the viewpoint crosses particular surfaces called the bifurcation set. Even if many papers have been written on this subject, especially in the past decade, the aspect graph should be considered a conceptual tool, mainly because of its huge dimension even for relatively simple objects. The interested reader can find details on the aspect graphs of several categories of objects in [9,12,17,18,22,39,40,42-45,48]. As far as this paper is concerned, we will refer to the catalogue of visual events for piecewise smooth objects presented by Rieger in [44,45]. The content of the paper is as follows. In Section 2, we show that the surface of the visual hull not coincident with the surface of the object consists of patches of nine types of ruled surfaces, which can be determined from the object's surface. These ruled surfaces are a subset of the bifurcation set of the aspect graph of the object. In Section 3, we show that a great deal of pruning and trimming of these surfaces can be done for a given object and provide the rules for pruning each type of surface. An output-sensitive algorithm for computing the visual hull is presented in Section 4, together with its complexity analysis. In Section 5, several examples of construction of the VH by means of a commercial CAD package are presented. The parametric equations of the boundary ruled surfaces are reported in the Appendix.

## 2 Determining the VH's boundary surfaces

![Figure 1. The object O, the convex hull CH(O) where the concavity is filled](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-1-p002.png)

*Figure 1. The object O, the convex hull CH(O) where the concavity is filled: The object O, the convex hull CH(O) where the concavity is filled with soft material, VH(O) obtained scraping off the filling with a ruler grazing the object.*

### 2.1 Lines making three contacts

### 2.2 Lines making two contacts

![Figure II. VC or VF with concave vertices.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-2-2-p007.png)

*Figure II. VC or VF with concave vertices.: Fig. II. VC or VF with concave vertices.*

![Figure 3. The VE triple point.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-3-p003.png)

*Figure 3. The VE triple point.: The VE triple point.*

![Figure 5. Vertex crossing.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-5-p003.png)

*Figure 5. Vertex crossing.: Vertex crossing.*

![Figure 4. The VE tangent crossing.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-4-p003.png)

*Figure 4. The VE tangent crossing.: The VE tangent crossing.*

Finally, we consider the cases VF and VC involving a vertex and a fold or crease, respectively. These cases correspond directly to the surfaces generated by the two cases of the VE vertex crossing (Fig. 5), VEs 17 and 18 of Rieger's catalogue. The equations that characterize these five ruled surfaces can also be found in the Appendix for parametric patches. Adding up, we have shown that a necessary condition for a point to lie on \(\mathrm{S}^{\prime \prime}{ }_{\text {VH }}\) is to belong to one of nine types of ruled surfaces, corresponding to nine particular visual events of the AG.

## 3 Pruning and trimming the boundary surfaces

Computing the VH of a piecewise smooth object does not appear much different from computing its perspective aspect graph: both require constructing a partition of the 3D space with ruled VE surfaces (actually, only nine types of surfaces are required by the VH, when the surfaces corresponding to Rieger's catalogue are 19). Each cell of the partition on one hand corresponds to an aspect if we consider the AG, on the other hand belongs entirely or does not belong at all to the VH. However, this kind of approach to constructing the VH appears prohibitively expensive, since the number of aspects, or cells of the partition for the AG is \(\mathrm{O}\left(n^{18} d^{18}\right)\) according to Petitjean, where \(n\) is the number of patches and \(d\) their degree [40]. Fortunately, the construction of the VH does not involve such an overwhelming computation, since, for a specific object, a great deal of pruning and trimming of the relevant surfaces can be done before constructing the partition. Many surfaces and patches can be discarded or trimmed by investigating whether free lines, compatible with the geometry of the surface near the contact points, pass through points of the VE surface. A free line is a straight line not intersecting \(\mathbf{O}\). No point of a free line can belong to VH [30]. This analysis, which will be presented in the next sub-sections, extends the analysis presented in [5] for smooth objects only. The segments of lines and surfaces surviving these pruning and trimming operations, related to the shape of the object near the contact points, will be called locally active or simply active. Two other pruning and trimming operations must be performed. All the surfaces where the generating line

### 3.1 Active surfaces making three contacts

### 3.2 Active surfaces making two contacts

#### 3.2.1 Active surfaces FF, CC, CF

The case FF has been already analyzed in [5]. Unfortunately, this analysis does not apply to the other cases, since it is based on the Gaussian curvature at the tangency points, which is not defined for creases. Therefore, here we will present new general arguments, related to the curvature of the contour generators, which apply to all cases.

Consider the line L, making two contacts with S at \(\mathbf{p}_{1}\) and \(\mathbf{p}_{2}\), a point \(\mathbf{p}\) of this line, and an infinitesimal rotation of L about \(\mathbf{p}\). If such rotation is possible without intersect ing the object near \(\mathbf{p}_{1}\) and \(\mathbf{p}_{2}\), the rotated line \(\mathrm{L}^{\prime}\) is a free line and the point does not belong to an active surface. A rotation of this kind will also be said compatible (with the surface at the contact points). Let \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\) be infinitesi mal segments of the contour generators near \(\mathbf{p}_{1}\) and \(\mathbf{p}_{2}\), which can be approximated with a segment of the osculat ing circles. Also let \(\mathrm{P}_{\mathrm{C} 1}\) and \(\mathrm{P}_{\mathrm{C} 2}\) be the osculating planes, and \(\mathbf{p}_{1}^{\prime \prime}\) and \(\mathbf{p}_{2}^{\prime \prime}\) the intersections of the rotated line \(\mathrm{L}^{\prime}\) with these planes (Fig. 7). It is clear that \(\mathrm{L}^{\prime}\) is a free line if both \(\mathbf{p}_{1}^{\prime \prime}\) and \(\mathbf{p}_{2}^{\prime \prime}\) lie on the external sides of the corresponding con tour generators \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\), as in the case shown in the fig ure. In most cases, it is convenient to perform this analysis in a plane P normal to L, where we project orthographical ly all the relevant entities, as shown in Fig. 7. Various cases occur, according to the curvatures of the contour generators and the relative positions of the external sides. In the following, if not otherwise explicitly stated, we will refer to the projections onto P of the various entities with the same names of their 3D counterparts.

Consider first the cases, shown in Fig. 8, where the internal sides of the contour generators lie on the same side of the common tangent T. The internal sides (projections of the surface of the object near the contour generators) are

![Figure 6. Active segments of lines making three contacts.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-6-p004.png)

*Figure 6. Active segments of lines making three contacts.: Active segments of lines making three contacts.*

![Figure 7. The line to be analyzed and a compatible rotation.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-7-p005.png)

*Figure 7. The line to be analyzed and a compatible rotation.: The line to be analyzed and a compatible rotation.*

![Figure 8. Cases of tangent crossing where the external sides of the contour generators lie on the same side of T.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-8-p005.png)

*Figure 8. Cases of tangent crossing where the external sides of the contour generators lie on the same side of T.: Cases of tangent crossing where the external sides of the contour generators lie on the same side of T.*

light and dark gray. The dark gray surface containing \(\mathbf{p}_{1}\) is closer to plane P.

Observe first that in all these cases only the internal patch is candidate to be active, since it is easy to see that a small rotation of L about any point of the external infinite segments in the plane normal to T produces a free line. Case (a), where both the centers of curvature lie on the internal side, is not active, and the corresponding surface can be totally discarded. This is easily seen, since the line L can be rotated about any point of the interior segment in the plane containing L and T without intersecting the object. In Fig. 8(a) both \(\mathbf{p}_{1}^{\prime \prime}\) and \(\mathbf{p}_{2}^{\prime \prime}\) lie on the external sides of \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\). Similar arguments show that also case (b) is not active. On the contrary, the figure shows that no rotation such that both \(\mathbf{p}_{1}^{\prime \prime}\) and \(\mathbf{p}_{2}^{\prime \prime}\) lie on the external sides of \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\) is possible in cases (c) and (d), and therefore the internal patches are active.

Case (e) is more complex, and its analysis requires the values of the radii of curvature \(r_{1}\) and \(r_{2}\) of (the projections) of \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\). It has been shown in [5] for the case FF that the internal segment of the 3D line L consists of an inactive segment \(\mathbf{p}_{1} \mathbf{p}_{\mathrm{M}}\) starting at the point \(\mathbf{p}_{1}\) of the contour gen erator where the center of curvature lies on the external side, and an active segment \(\mathbf{p}_{\mathrm{M}} \mathbf{p}_{2}\) ending at the other point, such that:

The proof reported in [5] is only based on the osculating circles of the contour generators, and then also holds for CC and CF.

In the Appendix it is shown how the parametric equation of the contour generator at a fold point can be obtained as shown in the Appendix. For creases, the contour generator is known a priori. The computation of the radii of curvature of the projections of the osculating circles requires the radii of curvatures of the 3D contour generators and the angles between the osculating planes and P. For brevity we omit the details, which can be found in books on differential geometry (see for instance [20], pp. 173-176)). Consider now the cases where the external sides of the contour generators lie on opposite sides of \(T(Fig.9)\).

In all these cases, only the external segments are candidate to be active (free lines are obtained with small rotations about any point of the internal segment in the plane normal to T). It is easy to see that cases (a) and (b) are not active. The compatible rotations shown in the figure are assumed about a point of the external segment crossing P. Similar arguments hold for the other external segment, not shown in the figure. The analysis of the figure (we omit the details) also shows that cases (c) and (d) generate two active external infinite patches. The case (e) requires a more complex analysis [5], whose results are as follows. Consider the external segment start ing at \(\mathbf{p}_{1}\), which is the point of the contour generator \(\mathrm{C}_{1}\) with the center of curvature on the internal side, and

$$
\left|\mathbf{p}_{1} \mathbf{p}_{\mathrm{M}}\right| /\left|\mathbf{p}_{\mathrm{M}} \mathbf{p}_{2}\right|=r_{1} / r_{2}
$$

![Figure 9. Cases of tangent crossing where the external sides of the contour generators lie on opposite side of T.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-9-p006.png)

*Figure 9. Cases of tangent crossing where the external sides of the contour generators lie on opposite side of T.: Cases of tangent crossing where the external sides of the contour generators lie on opposite side of T.*

#### 3.2.2 Active surfaces VF and VC

![Figure 10. VC or VF sub-cases (convex vertex projection). The figure shows](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-10-p006.png)

*Figure 10. VC or VF sub-cases (convex vertex projection). The figure shows: VC or VF sub-cases (convex vertex projection). The figure shows that the interior segment is not active.*

place about any point of the external segments, but not about the interior segment. In any other plane as \(\mathrm{P}_{2}\), no compatible rotation at all is possible. Then the internal seg ment is active. For the sake of clarity, figures \(\left(\mathrm{d}_{1}\right)\) and \(\left(\mathrm{d}_{2}\right)\) also shows the sections made with planes \(\mathrm{P}_{1}\) and \(\mathrm{P}_{2}\). The sections refer to the case VC, but the results also hold for VF. Observe that case (d) can be seen as a limit situation of case (d) in Fig. 8, for a vanishing radius of curvature of one contour generator. Also for cases (e) and (f) there are two possible types of intersection with \(\mathbf{O}\) of a plane rotating about L, as shown in the figure. The analysis of the rotations in these planes, whose details we omit, show that case (e) is inactive, and that in case (f) the external segments are active. Also observe that case (f) can be seen as a limit situation of sub-case (d) in Fig. 9 for a vanishing radius of curvature of one contour generator.

### 3.3 Dealing with non generic objects

Usual CAD objects are not generic. Let us briefly discuss how to deal with these objects. Essentially, we can have objects such that: at the vertices more than three creases can meet, there can be coplanar creases, and lines making multiple contacts.

Vertices where more than three creases meet do not affect the previous analysis of the cases VF and VC. Contact at two coplanar creases, often rectilinear, can be considered a limit situation of case (d) in Fig. 8, or of case (d) in Fig. 9, for vanishing curvatures of both contours. In the first case it produces a planar internal active patch, in the second two active planar external patches. Coplanar edges often generate overlapping planar active surfaces, as shown in the examples of Section 5.

Mostly, CAD objects produce multiple contacts at coplanar edges. These cases can be decomposed into multiple cases of two contacts. Each case supplies active segments: the overall active segments can be obtained by OR-ing the active segments of each case. The example in Fig. 12 refers to a case of three coplanar edges, and shows a section made with a plane passing trough L and skew with respect to the plane containing the edges. Thicker lines mark active segments. Concluding, in this section we have studied the nine types of surfaces in relation with the shape of \(\mathbf{O}\) at the

![Figure 11. Observe that, as soon as the line passing through](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-11-p009.png)

*Figure 11. Observe that, as soon as the line passing through: Observe that, as soon as the line passing through*

![Figure II. VC or VF with concave vertices.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-2-2-p007.png)

*Figure II. VC or VF with concave vertices.: Fig. II. VC or VF with concave vertices.*

contact point, shown that in several cases they are not active, and found the active patches in the remaining cases.

## 4 Constructing the VH

```text
In this section we will discuss an output-sensitive algo rithm for constructing VH(O), and its computational com plexity. For this purpose, we assume that the surface of \( \mathbf{O} \) consists of \( n \) algebraic patches of bounded degree. In addi tion, we assume a model of computation in which primitive operations involving a constant number of surfaces of bounded degree can be performed in constant time [24]. The algorithm proposed finds the part of \( \mathbf{V H}(\mathbf{O}) \) connected with \( \mathbf{O} \). As it will be explained in the following, parts of VH not connected to the object require rather uncommon objects. The algorithm consists of the following steps:
```

- Computing the locally active patches,

- Computing the VH-active patches,

- Constructing a partition of CH(O)-O formed by the VH-active patches and the surface patches of O such that each of the partition belongs entirely or not to he visual hull,

- Selecting the cells of the partition which belong to VH.

![Figure 12. Decomposing multiple contacts.](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-12-p007.png)

*Figure 12. Decomposing multiple contacts.: Decomposing multiple contacts. VC or VF with concave vertices.*

patches in order to reduce the computations of the following steps, could be approximated intersecting in \(O(2)\) time the locally active patches with the surface of some simple boundary solid. Step 3, requires constructing the arrangement of the VH-active surfaces. Computing arrangements of curves and surfaces is an active area of research, with several applications to problems such as robot motion planning, visualization and molecular modeling. Overviews of the subject can be found in [1,24]. A well-known result about arrangements is that, under rather general assumptions, the combinatorial complexity (overall number of cells of all dimensions) of an arrangement of \(\lambda+n\) algebraic surfaces in \(\mathrm{R}^{3}\) is \(\mathrm{O}\left((\lambda+n)^{3}\right)\) [24]. Even if software pack ages, as CGAL [21], exist for constructing arrangements of curves in 2D, so far no algorithm has been implemented for 3D general surfaces. Some algorithms have been presented for arrangements of quadrics ([3,49]), and for constructing a particular data structure able to answer point-location queries in an arrangement of algebraic surfaces [13]. As for a simpler structure conve nient to our algorithm, such as an incidence graph, no detailed algorithm has been presented, but, according to Halperin [24], it is plausible that it could be construct ed in time and space close to \(\mathrm{O}\left((\lambda+n)^{3}\right)\) for both. So we assume that this is the complexity of constructing the arrangement. Step 4, the incidence graph constructed in Step 3 pre sumably in \(\mathrm{O}\left((\lambda+n)^{3}\right)\) time allows to traverse the arrange ment for selecting and merging the cells belonging to VH(O). Several cells can be discarded in constant time [5]. In fact, define positive side of an active patch the side where free lines, compatible with the contact points, pass. Clearly, a cell belonging to the visual hull must lie on the negative side of all its boundary patches. This can be veri fied in constant time for each cell, and then in overall \(\mathrm{O}\left((\lambda+n)^{3}\right)\) time.

Another important pruning of the cells candidate to belong to \(\mathbf{V H}(\mathbf{O})\) can be performed for most objects. In general, the visual hull of an object, even if connected, could also contain parts not connected to the object. How ever, objects able to produce such visual hulls are very unlikely to be found in practice. The example of Fig. 13 shows that constructing objects of this kind takes some ingenuity. The object is connected, made of one external hollow cylinder, with a smaller connected cylinder inside, yellow in the Fig. 13. An horizontal slit allows free lines inside the hollow cylinder, which separate VH(O)-\(O(orange)\) from the object. If we deal with objects whose VH contains only parts connected to \(\mathbf{O}\), as it is for most objects in practice, another simple rule holds for pruning cells of the partition which cannot belong to VH:

Theorem. Only the cells of the partition of \(\operatorname{CH}(O)-O\) that are contiguous to \(\boldsymbol{O}\) are candidate to belong to the portion of VH connected with \(\boldsymbol{O}\).

![Figure 13. A connected object that generates an unconnected VH. (a) A side](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-13-p008.png)

*Figure 13. A connected object that generates an unconnected VH. (a) A side: A connected object that generates an unconnected VH. (a) A side view, (b) top view and (c) an axonometric view of the object. (d) The visual*

Proof. By contradiction, suppose that there is a cell that belongs to a portion of VH connected to \(\mathbf{O}\), and that the cell is not contiguous to \(\mathbf{O}\). In this case all the boundaries of the cell are patches of active surfaces. If the cell belongs to VH, all the positive side must lie on the exterior of the cell. But this also means that the cell is not connected to other cells of the VH, against the hypothesis.

Also this check can be done in constant time for each cell. Actually, also the construction of the partition can be simplified. Assuming an incremental construction tech nique, if one cell not contiguous to \(\mathbf{O}\) is obtained, it can be immediately discarded without any further subdivision.

Adding up, the whole output sensitive algorithm is \(\mathrm{O}\left(n^{6}+(\lambda+n)^{3}+\mu n\right)\).

At the end of this pruning operations, only \(\mu\) candidate cell are left, contiguous to \(\mathbf{O}\). A cell belongs to VH if no free lines pass trough one of its points. To check if one cell must be selected and merged with \(\mathbf{O}\), chose at random a point P lying on a boundary patch belonging to \(\mathbf{O}\), and ver ify whether free lines pass through P. To this purpose, com pute in constant time the tangent plane. Should the patch be planar, a plane parallel and very near to the face could be chosen. Then, intersect in \(\mathrm{O}(n)\) time the plane with the surface of \(\mathbf{O}\), and obtain \(\mathrm{O}(n)\) planar curves. Find in \(\mathrm{O}(n)\) time the \(\mathrm{O}(n)\) lines passing through P and tangent to these curves. If all these line intersect elsewhere one of these curves, the cell belongs to VH, since no free line pass es through P. The computation is \(\mathrm{O}(n)\) for each cell, and then the step is \(\mathrm{O}(\mu n)\). Adding up, the whole output sensitive algorithm is

## 5 Examples

The examples presented in this section, concerning rela tively simple objects and active surfaces, are produced by lines making two contacts with the objects and have been constructed using the commercial modeler CATIA \({ }^{\text {™ }}\). In

![Figure 14. Example 1. The object (a), the VH-active patches (b) and (c), the two cells formed by these patches (d) and (e), the VH (f).](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-14-p009.png)

*Figure 14. Example 1. The object (a), the VH-active patches (b) and (c), the two cells formed by these patches (d) and (e), the VH (f).: Example 1. The object (a), the VH-active patches (b) and (c), the two cells formed by these patches (d) and (e), the VH (f).*

Example 1. Consider the object in Fig. 14(a). In all, there are five VH-active patches. Patches due to overlapping surfaces are counted once. Two planar patches, \(\mathrm{P}_{1}\) and \(\mathrm{P}_{2}\) are shown in Fig. 14(b). \(\mathrm{P}_{1}\) is due to three patches overlapping, due to lines making contact at \(\mathrm{L}_{1}\) and \(\mathrm{L}_{3}, \mathrm{~L}_{1}\) and \(\mathrm{L}_{2}, \mathrm{~L}_{2}\) and \(\mathrm{L}_{3}\). Also, \(\mathrm{P}_{2}\) is generated by various overlapping patches. Fig. 14(c) we show three other VH active patches, \(\mathrm{P}_{3}, \mathrm{P}_{4}\), and \(\mathrm{P}_{5} . \mathrm{P}_{3}\) is generated by the lines passing through vertex \(\mathrm{V}_{1}\) and making contact at crease C between \(\mathrm{V}_{3}\) and \(\mathrm{V}_{5}\). This is an instance of sub-case (d) in Fig. 11. Observe that, as soon as the line passing through \(\mathrm{V}_{1}\) and grazing C becomes \(\mathrm{V}_{1} \mathrm{~V}_{5}\), where \(\mathrm{V}_{5}\) is the middle point of C, the case turns into the inactive sub-case (e) in Fig. 11. Then, all the lines passing through \(\mathrm{V}_{1}\) and making contact with C between \(\mathrm{V}_{5}\) and \(\mathrm{V}_{4}\) are not active. Patch \(\mathrm{P}_{4}\) is planar and is generated by the lines making contact at \(\mathrm{V}_{5}\) and \(\mathrm{L}_{2}\) (case (c) of Fig. 8). Patch \(\mathrm{P}_{5}\) is symmetric to \(\mathrm{P}_{3}\). The five patches produce a partition with two cells, shown in Fig. 14(d) and (e). Only the second cell is contiguous to the object, and belongs to the VH, shown in Fig. 14(f).

Example 2. The object is shown in Fig. 15(a). The VH-ac tive patches are six. Three planar patches, \(\mathrm{P}_{1}, \mathrm{P}_{2}\) and \(\mathrm{P}_{3}\) are shown in Fig. 15(b). The vertical edges also produce active surfaces (not shown in the figure) that lie outside the con vex hull and are not VH-active.

![Figure 11. Observe that, as soon as the line passing through](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-11-p009.png)

*Figure 11. Observe that, as soon as the line passing through: Observe that, as soon as the line passing through*

Lines making contact at the semi-circles \(\mathrm{C}_{1}\) and \(\mathrm{C}_{2}\) produce a conical surface whose internal part is divided into an active patch \(\mathrm{P}_{4}\) and an inactive patch \(\mathrm{P}_{5}\). This is an instance of case (e) in Fig. 8. Two other relevant patches exist, \(\mathrm{P}_{6}\) and \(\mathrm{P}_{7}\) in Fig. 15(d) and (e), generated by the lines

## 6 Summary

![Figure 15. Example 2. The object (a). Three planar VH-active surfaces (b).](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-15-p009.png)

*Figure 15. Example 2. The object (a). Three planar VH-active surfaces (b).: Example 2. The object (a). Three planar VH-active surfaces (b). P4 is VH-active, but not Ps (c). Two other curved symmetrical VHACTIVE patches (d) and (e). The resulting VH (f).*

![Figure 16. Example 3. The object (a), three types of VH-active surfaces (b-d), the visual hull (e).](/Users/evanthayer/Projects/stepview/docs/2008_the_visual_hull_of_piecewise_smooth_objects/figures/figure-16-p010.png)

*Figure 16. Example 3. The object (a), three types of VH-active surfaces (b-d), the visual hull (e).: Example 3. The object (a), three types of VH-active surfaces (b-d), the visual hull (e).*

CAD packages, has been presented. This theory subsumes the previous approaches dealing with specific categories of these objects, like polyhedra, solid of revolutions and smooth surface objects. We have shown that the surface of the VH not coincident with the surface of the object con sists of patches of nine types of ruled surfaces. These sur faces also belong to the bifurcation set of the aspect graph of \(\mathbf{O}\). We have also shown that the set of potentially active surfaces can be radically pruned and trimmed, and we have given rules to perform these operations. The reduction of the relevant patches makes computationally feasible to compute the VH of many practical objects. Finally, we have outlined an algorithm for evaluating the VH, using rules to determine the complete visual hull for most practical objects. The implementation of the different steps of the algorithm can exploit several algorithms already available.

Appendix A

$$
\left(\left(\mathbf{c}_{1}\left(u_{1}\right)-\mathbf{c}_{2}\left(u_{2}\right)\right) \times \mathbf{t}_{1}\left(u_{1}\right)\right) \cdot \mathbf{t}_{2}\left(u_{2}\right)=0
$$

In this appendix we write the equations that determine the nine ruled surfaces whose patches can form \(\mathrm{S}^{\prime \prime}{ }_{\text {vh }}\). We assume the surface patches of the object are given in para In most cases the surface equation cannot be directly written, but the contact conditions allow writing an algebraic multivariate system. In principle, determining the equations of the contour generators, and then the points that determine the generating line can be done using elimination theory techniques [16]. In practice, depending on the degree of the system, numerical methods could be required

Vertex crossing In the case VC, the equation of the surface is immediate ly written ( \(\mathbf{v}\) is the vertex):

$$
\begin{equation*} \mathbf{s}(u, v)=(\mathbf{v}-\mathbf{c}(u)) v \tag{A.1} \end{equation*}
$$

In the case VF, the generating line must be orthogonal to the surface normal at the tangency point:

$$
(\mathbf{v}-\mathbf{p}(u, v)) \cdot \mathbf{n}(u, v)=0 ; \quad \mathbf{n}(u, v)=\mathbf{p}_{u}(u, v) \times \mathbf{p}_{v}(u, v)
$$

where • is the dot product, and \(\times\) the vector product. Elim inating \(v\) between this scalar equation and \(\mathbf{p}(u, v)\) supplies the parametric equation \(\mathbf{c}(u)\) of the contour generator, which allows writing the surface equation (A.1).

The tangents at the two contour generators must be coplanar. In the case CC, let \(\mathbf{c}_{1}\left(u_{1}\right)\) and \(\mathbf{c}_{2}\left(u_{2}\right)\) be the equations of the creases. The co-planarity condition can be written as

$$
\begin{equation*} \mathbf{s}\left(u_{1}, v\right)=\left(\mathbf{c}_{1}\left(u_{1}\right)-\mathbf{c}_{2}\left(u_{1}\right)\right) v \tag{A.2} \end{equation*}
$$

In the case CF, the condition becomes:

$$
\left(\left(\mathbf{c}_{1}\left(u_{1}\right)-\mathbf{p}_{2}\left(u_{2}, v_{2}\right)\right) \times \mathbf{t}\left(u_{1}\right)\right) \times \mathbf{n}_{2}\left(u_{2}, v_{2}\right)=0
$$

This makes two scalar independent equations in \(u_{1}, u_{2}, v_{2}\). By eliminating \(u_{2}, v_{2}\) between these equations and \(\mathbf{p}_{2}\left(u_{2}, v_{2}\right)\) we obtain the parametric equation \(\mathbf{c}_{2}\left(u_{1}\right)\) of the second con tour generator, which allows writing the Eq. (A.2) of the surface.

In the case FF, the equations are

This makes three scalar equations in \(u_{1}, v_{1}, u_{2}\) and \(v_{2}\). Elim inating \(v_{1}, u_{2}\) and \(v_{2}\) between these equations and \(\mathbf{p}_{1}\left(u_{1}, v_{1}\right)\) supplies the parametric equation \(\mathbf{c}_{1}\left(u_{1}\right)\) of the first contour generator. A similar technique leads to \(\mathbf{c}_{2}\left(u_{1}\right)\), which allows to write the Eq. (A.2) of the surface. Triple point

The equations state that: (a) the three points lie on the same line; (b) for fold points the surface normal at the contact point must be orthogonal to the line. For instance, the equations for the case FFC can be written as:

In this case, we have four scalar equations and five param eters \(u_{1}, v_{1}, u_{2}, v_{2}, u_{3}\). Several other equivalent systems can be written. By elimination we can find \(\mathbf{c}_{1}\left(u_{3}\right)\) (or \(\mathbf{c}_{2}\left(u_{3}\right)\) ), which allows to write the surface equation (A.2). For brev ity, we omit the equations for the other three cases.

## References

- P.K. Agarwal, M. Sharir, Arrangements and their applications, in: J. Sack, J. Urrutia (Eds.), Handbook of computational Geometry, Elsevier, Amsterdam, 2000.

- 2] N. Ahuja, J. Veenstra, Generating octrees from object silhouettes in orthographic views, IEEE Trans. PAMI 11 (1989) 137-149.

- E. Berberich, M. Hemmer, L. Kettner, E. Schömer, N. Wolpert, An exact, complete and efficient implementation for computing planar maps of quadric intersection curves, 21st Annual Symposium on computational Geometry (SCG'05), Pisa, Italy, ACM, 2005, pp. 99106.

- B. G. Baumgart, Geometric modeling for computer vision, Technical Report Artificial Intelligence Laboratory Memo AIM-249, Stanford University, 1974.

- A. Bottino, A. Laurentini, The visual hull of smooth curved objects, IEEE Trans. PAMI 26 (12) (2004) 1622-1632.

- A. Bottino, A. Laurentini, Relating visual hull and tactile probing capabilities, in: Proceedings of SCI 2004, 18-21 July 2004, Orlando, Florida (USA), 2004.

- A. Bottino, A. Laurentini, The visual hull of piecewise smooth objects, in: BMVC 2004, 7-9 September 2004, Kingston, 2004.

- A. Bottino, A. Laurentini, What's NEXT? An interactive next best view approach, Pattern Recog. 30 (1) (2006) 126-132.

- K. Bowyer, M. Sallam, D. Eggert, J. Stewman, Computing the generalized aspect graph for objects with moving parts, Trans. PAMI 15 (6) (1993) 605-610.

- M. Brand, K. Kang, D.B. Cooper, Algebraic solution for the visual hull, in: Proc. CVPR'04, 2004, pp. 1063-1069.

- A. Broadhurst, T. Drummond, R. Cipolla, A probabilistic framework for the space carving algorithm, IEEE Proc. ICCV (2001) 388-393.

- J. Callahan, R. Weiss, A model for describing surface shape, in: Proc. CVPR, 1985, pp. 240-245.

- B. Chazelle, H. Edelsbrunner, L.J. Guibas, M. Sharir, A singlyexponential stratification scheme for rea semi-algebraic varieties and its applications, Theoret. Comput. Sci. 84 (1991) 77-105.

- G. Cheung, S. Baker, Takeo Kanade, Visual hull alignment and refinement across time: a 3D reconstruction algorithm combining shape-from-silhouette with stereo, IEEE Proc. CVPR 03 (2003) 1063-C.H. Chian, J.K. Aggarwal, Model reconstruction and shape recognition from occluding contours, Trans. PAMI 11 (1989) 372-389. D. Cox, J. Little, D. O'Shea, Ideals, Varieties and algorithms. An Introduction to computational Algebraic Geometry and Commutative Algebra, second ed., Springer, Berlin, 1996. D.W. Eggert, K.W. Bowyer, C.R. Dyer, H.I. Christensen, D.B Goldof, The scale space aspect graph, Trans. PAMI 15 (11) (1993) D. Eggert, K. Bowyer, Computing the perspective aspect graph of solids of revolution, Trans. PAMI 15 (2) (1993) 109-128 C.H. Esteban, F. Schmitt, silhouette and stereo fusion for 3D object modeling, Comput. Vis. Image Und. (2004) 367-392. and surfaces for CADG: a pratical guide, Academic Press, New York, 1997. E. Flato, D. Halperin, I. Hanniel, O. Nechushtan, E. Ezra, The design and implementation of planar maps in CGAL, ACM J. Exp. Algorithmics 5 (2000) 1-23. Z. Gigus, J. Canny, R. Seidel, efficiently computing and repreaspect graphs of polyhedral objects, Trans. PAMI 13 R.N. Goldman, T.W. Sederberg, Some applications of resultants to problems in computational geometry, The Visual Computer 1 (1985) D. Halperin, Arrangements, in: J. Goodman, J. O'Rourke (Eds.), Handbook of Discrete and computational Geometry, CRC Press R.J. Holt, T.S. Huang, A.N. Netrevali, Algebraic methods for image processing and computer vision, IEEE Trans. Image Process. 5 (6) (1996) 976-986. T. Isenberg et al., A developer's guide to silhouette algorithms for polygonal models, IEEE Comput. Graph. (2003) 28-37. J. Isidoro, S. Sclaroff, Stochastic refinement of the visual hull to satisfy photometric and silhouette consistency constraints, IEEE Proc. ICCV (2003) 1335-1342 J.J. Koenderink, A.J. van Doorn, The internal representation of solid shapes with respect to vision, Biol. Cybern. 32 (1979) 211-216. A. Laurentini, The visual hull concept for silhouette-based image understanding, IEEE Trans. PAMI vol. 16 (1994) 150-162. A. Laurentini, How far 3D shapes can be understood from 2D silhouettes, IEEE Trans. Pattern Anal. Machine Intell. 17 (2) (1995) 188-195. A. Laurentini, Computing the visual hull of solids of revolution, Pattern Recog. 32 (1999) 377-388. E. Lazebnik, E. Boyer, J. Ponce, On how to compute exact visual hulls of object bounded by smooth surfaces, IEEE Proc. CVPR 1 (2001) 156-161. W.N. Martin, J.K. Aggarwal, Volumetric description of objects from multiple views, Trans. PAMI 5 (1983) 150-158. W. Matusik, C. Buehler, L. McMillian, Polyhedral visual hulls for real-time rendering, in: Proc. Eurographics Workshop on Rendering, 2001. P. Mendonca, K. Wong, R. Cipolla, Epipolar geometry from profiles under circular motion, IEEE Trans. PAMI 23 (2001) 604616. N.M. Patrikalakis, T. Maekawa, Shape interrogation for computer aided design and manufacturing, Springer Verlag, Berlin, 2002. S. Petitjean, A computational geometric approach to visual hull, Int. J. Comput. Geometry Appl. 8 (4) (1998) 407-436. S. Petitjean, J. Ponce, D.J. Kriegman, Computing exact aspect graphs of curved objects: algebraic surfaces, Int. J. Comput. Vis. 9 (3) (1992) S. Petitjean, Algebraic geometry and computer vision: polynomial systems, real and complex roots, J. Math. Imaging Vis. 10 (1999) 132.

- J. Ponce, J. Kriegman, Computing exact aspect graph of curved objects: parametric patches, in: Proc. AAAI Conf., July 1990, Boston, 1990, pp. 1074-1079.

- J. Rieger, On the classification of views of piecewise smooth objects, Image Vis. Comput. 5 (1987) 91-97.

- mout. Geom. (1998) 205-229.

- 1. Rege moth complesty acd, Colos Trans Roy. e Loid of

- S. Seitz, C. Dyer, Photorealistic scene reconstruction by voxel coloring, Int. J. Comp. Vis. 35 (1999) 151-173.

- J.-K. Seong, G. Elber, J.K. Jhonston, M.-S. Kim, The convex hull of freeform surfaces, Computing 72 (2004) 171-183. I. Shimshoni, J. Ponce, Finite resolution aspect graphs of polyhedral objects, IEEE Trans. Pattern Anal. Machine Intell. 19 (4) (1997) 315- (49 E Shine a Ci an pera meno quadre Compact for S. Sullivan, J. Ponce, Automatic construction and estimation from photographs using triangular splines, IEEE Trans. Y. Zheng, Acquiring 3D models from sequences of contours, IEEE Trans. PAMI 16 (2) (1994) 163-178.
