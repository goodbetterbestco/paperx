# Visibility, Occlusion, and the Aspect Graph

W. Harry Plantinga - Charles R. Dyer

Department of Computer Sciences University of Wisconsin - Madison

## Abstract

In this paper we study the ways in which the topology of the image of a polyhedron changes with changing viewpoint. We catalog the ways that the "topological appearance" or aspect can change. This enables us to find maximal regions of viewpoints of the same aspect. We use these techniques to construct the viewpoint space partition (VSP), a partition of viewpoint space into maximal regions of constant aspect, and its dual, the aspect graph. In this paper we present tight bounds on the maximum size of the VSP and the aspect graph and give algorithms for their construction, first in the convex case and then in the general case. In particular, we give tight bounds on the maximum size of O(n2) and O(n°) under orthographic projection with a 2-D viewpoint space and of O(1°) and (n°) under perspective projection with a 3-D viewpoint space. We also present properties of the VSP and aspect graph and give algorithms for their construction. * This work was supported in part by the NSF under grant DCR-8520870.

## 2 Visibility and Occlusion

Visual perception involves acquiring information about the surrounding world from an image of the world. The image is a representation of the array of ambient light available at a viewpoint. When the viewer is a camera, the viewpoint is the center of the lens. The ambient light available to the viewer is a solid angle of light arriving at the viewpoint.

In general, an object in the world is said to be visible in an image whenever light arrives at the viewpoint from the object, so that the object is represented by a region of light intensity values in the image. However, in some cases it is desirable to define a more restrictive model of visibility, in order to focus attention on a particular aspect of the problem of visual perception.

In this paper we study the change in the topological structure of images of polyhedra, and we use two models of visibility that enable us to study the problem in two slightly different ways. In both models the world contains solid, opaque polyhedra and the edges of the polyhedra are visible in the image. Thus, in the models the image plane is an unbounded plane containing line segments corresponding to the projections of the visible edges of the polyhedra in the world. We assume that the resolution of the image is infinite; nothing is too small to resolve. Note that under these models the image of a polyhedron is more than a silhouette; it is a line drawing with hidden lines removed. Equivalently, the image can be thought of as a set of polygonal regions corresponding to visible faces or parts of faces of the polyhedron.

Since the image plane can only capture light incident upon the viewing plane from some directions (half of them), and since some part of the image plane may be preferred for objects of interest (e.g. the fovea), we also speak of a viewing direction. The viewing direction or line of sight is the direction in which the camera is pointed, so that objects in the viewing direction appear at the preferred point of the image. We also assume that the camera has a fixed orientation with respect to the viewing direction, so that objects generally appear upright.

For some problems it is sufficient to assume that the viewpoint is a large distance away from the object of interest and that the whole object is visible in the image. For example, in object recognition it may be reasonable to assume that the whole object to be recognized appears in the image. It would not do for the viewpoint to be inside the object to be recognized or for the viewpoint to be so close to the object that only one face is visible. For other problems the space of possible viewpoints must range over the whole world. For example, in motion planning the visible surfaces represent the boundaries of free space in any direction. In useful motion planning problems, obstacles may be on all sides of the object to be moved. The object may even be inside a workspace.

Therefore we use two viewing models. The first model is designed to handle the first case, in which the whole object is in front of the viewer in any image. In order to model this case, we restrict viewpoints to an infinite sphere containing the object and use orthographic projection in forming the image. Thus the whole object is in front of the viewer from any viewpoint. We call this the orthographic model. It is a useful model because it represents a restriction on visibility that makes some representations smaller. In the second model we allow the viewpoint to be any point in the world. In this case it is natural to use perspective projection in forming the image from a viewpoint. This model is intended to resemble natural vision, in which objects can be all around the viewer, and the viewer can even be inside objects, such as houses.

The directions of incident ambient light represented in the image plane are those directions more than 90° away from the viewing direction (since the viewing direction is away from the viewer but the visible light is toward the viewer). In problems such as motion planning, visibility information from all directions is of interest, since the visible surfaces represent the boundaries of free space in any direction. visibility from all directions can be represented by two image planes from opposite viewing directions along with points at infinity in one of the planes or by an image sphere representing all viewing directions. For the problem of looking at an object and recognizing it or perceiving its shape, however, a section of a single image plane is sufficient. We assume that the viewer is interested in a particular object or small part of the world and "looks at" the object.

In the perspective model, viewpoint space is R3 and the viewing direction is the direction from the viewpoint to the origin. Thus, the image formation process can be modelled mathematically as a perspective projection of the visible edges of the object onto the image plane, in such a way that the origin of the world projects onto the origin of the image plane. The object of interest will project onto a region of pixels near the origin of the image.

In the orthographic model, we need only represent the direction of the viewpoint, rather than its location in the world. In this model viewpoint space is the 2-D space of directions from the origin. We can represent these directions as points on a unit sphere, with a point corresponding to the direction from that point to the origin. We will speak of points on the unit sphere and viewing directions interchangeably. We will denote viewing directions by (0,$) (see Figure 1). That is, if the point (0,0,1) corresponds to the viewing direction "straight ahead" (i.e. some reference viewing direction) then that point rotated by 0 counterclockwise about the y-axis and then by d counterclockwise about the x-axis corresponds to the viewing direction (0,¢). (In Figure 1, we show a negative $ and positive 0 rotation).

![Figure 1. The point (8,¢) on the unit sphere.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-1-p012.png)

*Figure 1. The point (8,¢) on the unit sphere.: Figure 1. The point (8,¢) on the unit sphere.*

Occlusion is the general term for the hiding of some feature in the world from some viewpoint. That is, when the view of something is blocked from a particular viewpoint, we say that it is occluded. Occlusion can also be used as a verb, referring to the change from visible to invisible of some feature. These notions of occlusion are object-centered in the sense that they concern whether a feature of an object is visible. There is also an image-centered notion of occlusion, concerning the change in the image resulting from occlusion. For example, from some viewpoint, a part of a face may be visible in a region of the image. As the viewpoint changes, the region may shrink and disappear as that part of the face becomes occluded.

In this paper we are concerned with the changes in occlusion that bring about a topological change in the image. A topological change in the image results when a region appears or disappears, or when regions split or merge. For example, the merging of two regions of the image results in a topologically-distinct image (see Figure 2).

![Figure 2. The merging of two regions in the image is a topological change.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-2-p012.png)

*Figure 2. The merging of two regions in the image is a topological change.: Figure 2. The merging of two regions in the image is a topological change. Figure 6. The aspect graph is the dual of the VSP. Figure 7. The aspect graph for a tetrahedron.*

However, the change in a region of the image from \(a_{4}\)-sided polygon to \(a_{5}\)-sided polygon does not by itself result in a topologically distinct image (see Figure 3).

![Figure 3. A change in the number of sides of a polygon in the image is not a](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-3-p013.png)

*Figure 3. A change in the number of sides of a polygon in the image is not a: Figure 3. A change in the number of sides of a polygon in the image is not a*

The changes in occlusion that result in a topological change in the image we call events. These events are the sort of occlusion we deal with in this paper. That is, we are interested in the ways in which the topological structure of the image of polyhedra changes with changing viewpoint, through the accretion, deletion, splitting, and merging of regions in the image. We characterize the way that the structure of the image changes by studying the viewpoints at which such changes occurs. These viewpoints are interesting because they are the boundaries in viewpoint space of volumes of viewpoints from which the world has the same topological appearance.

Figure 3 shows an event that does not result in two images that are topologically distinct. However, the images are "linearly distinct," in the sense that not every edge of the second can be obtained by a linear transformation of an edge of the first. By also considering events such as that shown in Figure 3, we could modify our work below from the study of topologically-distinct images to the study of linearly-distinct images.

## 3 The Viewpoint Space Partition and the Aspect Graph

From any viewpoint a polyhedron has a particular appearance, and varying the viewpoint slightly does not generally change the topology of the image. Thus, there are "stable views" or aspects for a polyhedron-views of the polyhedron with the same topological image structure over a region of viewpoints. We call a maximal connected region of viewpoints from which the views of the object are topologically equivalent a maximal viewing region of constant aspect or viewing region for short. Some changes in viewpoint result in a change in the topology of the image, however. These changes pass from one viewing region to another.

We can define a viewing region more formally as a set of viewpoints that are equivalent under an equivalence relation defined as follows. For two viewpoints v1 and v2, we say that V1 = v2 whenever there is a path of viewpoints from v1 to v2 such that from every viewpoint along the path (including v1 and v2) the aspect is constant, ie. the image has the same topological structure. = is an equivalence relation since it is reflexive, symmetric, and transitive. Therefore it partitions viewpoint space into equivalence classes consisting of regions or volumes of constant aspect, i.e. viewing regions.

We call this partition of viewpoint space the viewpoint space partition or VSP. In the orthographic case it consists of a partition of the sphere, and in the perspective case it consists of a partition of R3. The boundary points of the VSP are points from which an arbitrarily small change in viewpoint causes a change in the topology of the image. Figure 4 shows a tetrahedron and Figure 5 shows the structure of the viewpoint space partition generated by the tetrahedron under orthographic projection. The viewpoint space partition is flattened out onto a plane, and the shapes of the regions are not preserved, but the topological structure is preserved

![Figure 4. A tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-4-p014.png)

*Figure 4. A tetrahedron.: Figure 4. A tetrahedron. Figure 9. An image of a cube under our viewing model and that of Koenderink and van Doorn.*

![Figure 5. The viewpoint space partition for a tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-5-p015.png)

*Figure 5. The viewpoint space partition for a tetrahedron.: Figure 5. The viewpoint space partition for a tetrahedron.*

The shaded side of a boundary represents the inside of a region. Each region is labelled by the faces visible from viewing directions in that region. Since a face is not visible edge-on, the regions are open and their complements are closed.

By definition, the regions of viewpoints of the VSP contain viewpoints in which the topology of the image is constant. Some differences in the image at different viewpoints are still possible, however. No image regions can appear, disappear, split, or merge, but they can change in shape. In fact, polygonal regions of the image can change in the number of edges bounding the region without changing the topology of the image, and the structure of image features such as T-junctions can change without changing the topology of the image. Characterizing images as "topologically equivalent" is not as strong as characterizing them as, say, "linearly equivalent," where images are related by a linear transformation.

The definition of the VSP does not include labels for the regions. They are included in Figure 5 to aid understanding the figure. If one wishes to label the regions with the corresponding aspects, labeling the regions with the names of the visible faces is sufficient in the convex case, as we have done in Figure 5. It is not sufficient in the general case, however, since images with the same sets of visible faces can have different topological structure. In that case we can label a region by adding a pointer to an image of the object from a viewpoint in that region. Alternatively, we could label the boundaries with a description of the change that occurs in the image.

We define the dual of the region-boundary structure of the VSP to be the aspect graph. That is, for every region of the VSP there is a vertex in the aspect graph, and vertices of the aspect graph are connected by edges whenever the corresponding regions of the VSP are adjacent. Thus, the aspect graph has a vertex for every aspect, and vertices for adjacent aspects are connected. Figure 6 shows the aspect graph for the tetrahedron of Figure 4 overlaid on the VSP, and Figure 7 shows the aspect graph by itself. In this case the aspect graph is the same under the orthographic and perspective models.

![Figure 6.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-6-p016.png)

*Figure 6.: Figure 6. Figure 10. A band of m sides.*

![Figure 1. The point (8,¢) on the unit sphere.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-1-p012.png)

*Figure 1. The point (8,¢) on the unit sphere.: Figure 1. The point (8,¢) on the unit sphere.*

![Figure 7. The aspect graph for a tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-7-p016.png)

*Figure 7. The aspect graph for a tetrahedron.: Figure 7. The aspect graph for a tetrahedron. Figure 11. A convex polyhedron with two orthogonal bands.*

Note that under our definition of the VSP and the aspect graph two different vertices of the aspect graph can correspond to aspects that are topologically equal. This happens when the appearance of the object is the same from two different, unconnected maximal regions of viewpoint space. Furthermore, the appearance from the two aspects can be the same in two different senses. In the more restrictive

![Figure 2. The merging of two regions in the image is a topological change.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-2-p012.png)

*Figure 2. The merging of two regions in the image is a topological change.: Figure 2. The merging of two regions in the image is a topological change. Figure 6. The aspect graph is the dual of the VSP. Figure 7. The aspect graph for a tetrahedron.*

![Figure 3. A change in the number of sides of a polygon in the image is not a](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-3-p013.png)

*Figure 3. A change in the number of sides of a polygon in the image is not a: Figure 3. A change in the number of sides of a polygon in the image is not a*

The observant reader may have wondered why in Figure 7 vertices A and ABC are connected, whereas vertices AB and AC are not. After all, the corresponding regions of viewpoint space seem to have the same relationship to each other in both cases: paths of viewpoints connecting a viewpoint in one region with a viewpoint in the other all pass through a single point \(P(seeFigure8)\).

![Figure 8. The boundary between four regions of viewpoint space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-8-p017.png)

*Figure 8. The boundary between four regions of viewpoint space.: Figure 8. The boundary between four regions of viewpoint space.*

шишишии * в visible CATA visible l

The answer is a result of the fact that faces are not visible edge-on. The regions of viewpoint space in Figure 8 are shown with shading on open boundaries. Thus, the point P is in region A but not in regions AB, AC, or ABC. Therefore it is possible to find a path of viewpoints from a point in region A to a point in region ABC which doesn't go through AB and AC, but it is not possible to find such a path between AB and AC.

- Koenderink and A. van Doorn [1976] first introduced the notion of a stable view or aspect, but their definition differs slightly from ours. They assume that

equivalent a maximal viewing region of constant aspect or viewing region for short. Some changes in viewpoint result in a change in the topology of the image, however. These changes pass from one viewing region to another. We can define a viewing region more formally as a set of viewpoints that are equivalent under an equivalence relation defined as follows. For two viewpoints \(\mathbf{v}_{1}\) and \(\mathbf{v}_{2}\), we say that \(\mathbf{v}_{1} \approx \mathbf{v}_{2}\) whenever there is a path of viewpoints from \(\mathbf{v}_{1}\) to \(\mathbf{v}_{2}\) such that from every viewpoint along the path (including \(\mathbf{v}_{1}\) and \(\mathbf{v}_{2}\) ) the aspect is constant, i.e. the image has the same topological structure. \(\approx\) is an equivalence relation since it is reflexive, symmetric, and transitive. Therefore it partitions viewpoint space into equivalence classes consisting of regions or volumes of constant aspect, i.e. viewing regions.

![Figure 9. An image of a eube under our viewing model and that of Koenderink and](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-9-p018.png)

*Figure 9. An image of a eube under our viewing model and that of Koenderink and: Figure 9. An image of a eube under our viewing model and that of Koenderink and*

In our model all of the visible edges of the polyhedra appear as line segments in the image. In Koenderink and van Doorn's model, sharp edges are not allowed, so they are considered to have been smoothed. Only occluding contours and local minima and maxima of distance appear in an image. Koenderink and van Doorn define a change in aspect to be a change in the topological structure of these singularities. We define a change in aspect to be a change in the topological structure of the regions in the image formed by the projection of the edges of the object.

Koenderink and van Doorn [1979] first introduced the aspect graph (which they call the visual potential graph) in order to formalize the ideas of the topologically-distinct views of an object. Their definition of the aspect graph differs from ours in the same way that their definition of aspect differs.

![Figure 4. A tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-4-p014.png)

*Figure 4. A tetrahedron.: Figure 4. A tetrahedron. Figure 9. An image of a cube under our viewing model and that of Koenderink and van Doorn.*

## 4 Convex Polyhedra

In this section we consider the VSP and aspect graph for a single convex polyhedron. The restriction to convex polyhedra greatly simplifies the problem because a face is always visible from viewpoints "in front of" it; no face ever occludes another face. The only way that a face may become invisible with changing viewpoint is by "turning away from" the viewer or "going below the horizon." That is, when the viewpoint passes through the plane containing the face, the face becomes invisible (or visible) due to occlusion of the face by the rest of the object. Also, there cannot be two vertices in the aspect graph for the same set of faces since if the same set of faces is visible from two viewpoints, that set is also visible from all viewpoints along the shortest path (geodesic) in viewpoint space connecting them. Thus, in the convex case a change in aspect and a change in the visibility of some face of the polyhedron are equivalent events.

![Figure 5. The viewpoint space partition for a tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-5-p015.png)

*Figure 5. The viewpoint space partition for a tetrahedron.: Figure 5. The viewpoint space partition for a tetrahedron.*

### 4.1 Orthographic Case

Under the orthographic viewing model, viewpoint space is \(a_{2}\)-D spherical space of directions. A face of a convex polyhedron is visible in any viewing direction "pointing toward" the front of that face. That is, if d is a viewing direction and n is the outward normal of the face, that face is visible whenever n. d ‹ 0, i.e. the angle between n and d is greater than 180°. Therefore the boundary between the regions of the sphere of viewing directions where the face is visible and where it is invisible is the great circle defined by (d : n. d = 0). This is the intersection of the sphere with a plane containing the origin and having normal n.

#### 4.1.1 An Upper Bound

The great circle corresponding to a face is the boundary on the sphere of viewpoints between the region (hemisphere) where the face is visible and the region where it is invisible. For a polyhedron with n faces, the corresponding n great circles therefore partition viewpoint space into a subdivision in which the same set of faces is visible from all of the viewpoints in each region. That is, the n great circles partition viewpoint space into the VSP.

Assuming that no two faces have antiparallel normals, each pair of great circles intersects in exactly two points. In that case the total number of intersection points is at most 2 n (n-1) = \(O(n2)\). (The number can be less than 2 n (n-1) if several great circles intersect in the same point.) If two faces of the polyhedron are parallel, the corresponding great circles coincide, and the number of vertices in the VSP is reduced. Thus the VSP has \(O(n?)\) vertices. Since a subdivision of \(a_{2}\)-D space is by definition planar and a planar graph has a linear number of edges and regions, the size of the VSP is therefore \(O(n?)\). The aspect graph is the dual of the VSP, so it is also planar and also has size \(O(n2)\).

#### 4.1.2 A Lower Bound

The lower bound on the maximum size of the VSP and the aspect graph for a convex polyhedron of size n under orthographic projection is 2(n2). We prove this by exhibiting a class of such polyhedra. Consider a band of m square faces arranged around a circle (see Figure 10). In Figure 11 we show two such bands arranged orthogonally around a sphere, with additional faces added to form a convex polyhedron.

![Figure 10. A band of m sides.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-10-p020.png)

*Figure 10. A band of m sides.: Figure 10. A band of m sides.*

![Figure 6.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-6-p016.png)

*Figure 6.: Figure 6. Figure 10. A band of m sides.*

![Figure 7. The aspect graph for a tetrahedron.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-7-p016.png)

*Figure 7. The aspect graph for a tetrahedron.: Figure 7. The aspect graph for a tetrahedron. Figure 11. A convex polyhedron with two orthogonal bands.*

![Figure 11. A convex polyhedron with two orthogonal bands.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-11-p020.png)

*Figure 11. A convex polyhedron with two orthogonal bands.: Figure 11. A convex polyhedron with two orthogonal bands.*

Select one of the faces visible in Figure 11 from each band, excluding the face that is common to both bands. The great circles bounding the visibility regions on the sphere of the two selected faces have two intersection points, and these points are vertices of the VSP. Each pair of faces thus selected has a unique pair of intersection points, so there are \(S(m?)\) vertices in the VSP. The faces added to the bands to form a polyhedron have total size \(O(m)\), so if the polyhedron has size n, its VSP has size 2(n2). Since the aspect graph is the dual of the VSP, it also has size 2(n2).

In fact, a polyhedron would have to be highly degenerate to have a VSP of size less than \(O(n2)\). For example, any class of polyhedra that has bounded vertex degree and bounded face degree has a VSP of size \(S(n2)\). This is because the only way to reduce the size of the VSP is to have the intersection points of the great circles coincide, and if the number of edges around each face and the number of faces around each vertex is bounded, then the number of great circles that can intersect in a single point is bounded. An example of a highly degenerate class of polyhedra is the class of n-sided approximations to a cylinder; for polyhedra in this class the VSP has size \(O(n)\).

#### 4.1.3 An Algorithm

the same information with the addition of the actual boundaries in viewpoint space of the viewing regions, and the space it requires is only a constant factor larger. Since the VSP represents viewing regions and their boundaries, it is a more appropriate tool for most applications that are concerned with the particular viewpoints associated with each aspect. The observant reader may have wondered why in Figure 7 vertices A and \(A B C\) are connected, whereas vertices \(A B\) and \(A C\) are not. After all, the corresponding regions of viewpoint space seem to have the same relationship to each other in both cases: paths of viewpoints connecting a viewpoint in one region with a viewpoint in the other all pass through a single point \(P\) (see Figure 8).

The algorithm for constructing the arrangement works by starting with an empty subdivision and adding one line at a time. Adding a line 1 to the subdivision involves finding an intersection point of 1 with a line already in the subdivision. Both lines are split at the intersection point: the nodes in the subdivision for the edges that intersect are duplicated, and one endpoint of each of the four edges is set to the intersection point. 1 crosses a region of the subdivision in both directions from that point. The edges of one of the regions are tested for intersection with 1, and the intersection point thus found is added to the subdivision. The region just crossed by 1 is split into two regions, one on either side of the new edge on 1. This process is continued in both directions from the first intersection point of 1 with an edge of the subdivision, until all of 1 has been inserted into the subdivision. possible to find a path of viewpoints from a point in region \(A\) to a point in region \(A B C\) which doesn't go through AB and AC, but it is not possible to find such a path between AB and AC. J. Koenderink and A. van Doorn [1976] first introduced the notion of a stable

![Figure 8. The boundary between four regions of viewpoint space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-8-p017.png)

*Figure 8. The boundary between four regions of viewpoint space.: Figure 8. The boundary between four regions of viewpoint space.*

### 4.2 Perspective Case

The only kind of occlusion that occurs in this case is a face turning away from the viewer, as in the orthographic case. However, under the perspective model a face is visible from all points in front of the plane spanned by that face (rather than from all viewing directions pointing toward that face). Therefore viewpoint space is cut by n planes for a polyhedron with n faces, and the resulting subdivision is the VSP. The aspect graph is the dual of the cell-face structure of the VSP.

![Figure 9. An image of a eube under our viewing model and that of Koenderink and](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-9-p018.png)

*Figure 9. An image of a eube under our viewing model and that of Koenderink and: Figure 9. An image of a eube under our viewing model and that of Koenderink and*

In fact, the aspect graph for a polyhedron under perspective projection contains as a subgraph the aspect graph for that polyhedron under orthographic projection. This is true because in the limit of increasingly large spheres centered on the polyhedron, the planes spanned by the faces of the polyhedron cut the sphere in the same great circles as in the orthographic case.

#### 4.2.1 An Upper Bound

The VSP is the subdivision of viewpoint space generated by the n planes corresponding to the n faces of the polyhedron. Since the intersection of three general planes is a point, there can be at most \(O(n3)\) intersection points of n planes. In order to get the largest possible VSP, we can assume that every set of three planes intersects in a distinct point. These intersection points are vertices of the VSP, so the VSP has \(O(n3)\) vertices.

Thus each plane is cut into a subdivision of \(O(n2)\) vertices, edges, and regions. Therefore among all n planes there are \(O(n3)\) vertices, edges, and faces. A cell of the VSP is bounded by only four faces in the worst case, so the VSP has at most \(O(n3)\) vertices, edges, faces, and cells. The aspect graph is the dual of the cell-face structure of the VSP, so its size is also \(O(n3)\).

#### 4.2.2 A Lower Bound

4.1. Orthographic Case Under the orthographic viewing model, viewpoint space is \(a_{2}\)-D spherical space of directions. A face of a convex polyhedron is visible in any viewing direction "pointing toward" the front of that face. That is, if \(\mathbf{d}\) is a viewing direction and \(\mathbf{n}\) is

![Figure 12. Two quarter-bands.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-12-p023.png)

*Figure 12. Two quarter-bands.: Figure 12. Two quarter-bands. Figures 17a and 17b. Edge-edge-edge occlusion type 1.*

viewpoints between the region (hemisphere) where the face is visible and the region where it is invisible. For a polyhedron with \(\mathbf{n}\) faces, the corresponding \(\mathbf{n}\) great circles therefore partition viewpoint space into a subdivision in which the same set of faces is visible from all of the viewpoints in each region. That is, the \(\mathbf{n}\) great circles partition viewpoint space into the VSP.

#### 4.2.3 An Algorithm

the size of the VSP is therefore \(\mathrm{O}\left(\mathbf{n}^{2}\right)\). The aspect graph is the dual of the VSP, so it is also planar and also has size \(\mathrm{O}\left(\mathbf{n}^{2}\right)\).

4.1.2. A Lower Bound The lower bound on the maximum size of the VSP and the aspect graph for a convex polyhedron of size \(\mathbf{n}\) under orthographic projection is \(\Omega\left(\mathbf{n}^{2}\right)\). We prove this by exhibiting a class of such polyhedra. Consider a band of \(\mathbf{m}\) square faces arranged around a circle (see Figure 10). In Figure 11 we show two such bands arranged orthogonally around a sphere, with additional faces added to form a convex polyhedron.

The aspect graph is the dual of the cell-face graph of the VSP. It can be constructed from the data structure for the VSP by copying the VSP, changing cells to vertices and faces between cells to edges joining them, and deleting everything else. This algorithm requires linear time in the size of the VSP, so the aspect graph can be constructed in \(O(n3)\) time.

![Figure 10. A band of m sides.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-10-p020.png)

*Figure 10. A band of m sides.: Figure 10. A band of m sides.*

## 5 Non-Convex Polyhedra

In the convex case, the only sort of event that can change the aspect is the horizon effect. In the non-convex case, faces can occlude other faces, causing several other types of events. Thus, in order to construct the VSP and the aspect graph in the non-convex case we must characterize all the ways in which aspect can change. Since there are more modes of changing aspect, the size of the VSP and the aspect graph for non-convex polyhedra can be much larger. In the following sections we list the kinds of events that can occur and the corresponding boundaries of regions of constant aspect that result in viewpoint space.

![Figure 11. A convex polyhedron with two orthogonal bands.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-11-p020.png)

*Figure 11. A convex polyhedron with two orthogonal bands.: Figure 11. A convex polyhedron with two orthogonal bands.*

### 5.1 Orthographic Case

In the orthographic case, the VSP is a subdivision of the sphere of viewpoints, and the aspect graph is its dual. We first list the ways that the aspect can change in the non-convex case and the kinds of boundaries in viewpoint space that these changes generate. We then present upper and lower bounds on the maximum size of the VSP and aspect graph in this case and present an algorithm for their construction.

#### 5.1.1 Occlusion under Orthographic Projection

around each vertex is bounded, then the number of great circles that can intersect in a single point is bounded. An example of a highly degenerate class of polyhedra is the class of \(\mathbf{n}\)-sided approximations to a cylinder; for polyhedra in this class the VSP has size \(O(n)\). 4.1.3. An algorithm The great circles defined by the face normals subdivide the sphere of viewing directions into the VSP. Therefore to give an algorithm for constructing the VSP it is only necessary to show how to merge these great circles into one subdivision data

##### 5.1.1.1 Edge-Vertex Occlusion Boundaries

gorithm for constructing an arrangement (subdivision) formed by \(\mathbf{n}\) lines in the plane in \(\mathrm{O}\left(\mathbf{n}^{2}\right)\) time. The algorithm for constructing the arrangement can be used for constructing a subdivision formed by great circles on the sphere since they behave very much like lines on a plane. In fact, the great circles can be projected onto lines on two parallel planes and the arrangements constructed in the planes. This approach is similar to that of McKenna and Seidel [1985], in which they construct minimal or The algorithm for constructing the arrangement works by starting with an empty subdivision and adding one line at a time. Adding a line \(\mathbf{1}\) to the subdivision involves finding an intersection point of \(\mathbf{1}\) with a line already in the subdivision. Both lines are split at the intersection point: the nodes in the subdivision for the edges that intersect are duplicated, and one endpoint of each of the four edges is set to the intersection point. 1 crosses a region of the subdivision in both directions from that point. The edges of one of the regions are tested for intersection with \(\mathbf{l}\), and the

which is worst-case optimal. In fact, the algorithm is optimal for all but highly degenerate polyhedra, since only in that case does the VSP have size smaller than \(\Theta\left(n^{2}\right)\).

constructing the aspect graph can be done in \(\mathrm{O}\left(\mathbf{n}^{2}\right)\) time. 4.2. Perspective Case Under the perspective model the viewpoint is not restricted, so the viewpoint space is \(R^{3}\). Also, objects are not restricted to being in front of the viewpoint; they

Regions can merge in another way, illustrated in Figure 16. If a concave corner lies on an edge in an image (Figure 16a), an arbitrarily small change in viewpoint can cause the regions on either side of the corner to merge (Figure 16b).

projection. This is true because in the limit of increasingly large spheres centered on the polyhedron, the planes spanned by the faces of the polyhedron cut the sphere in the same great circles as in the orthographic case. 4.2.1. An Upper Bound The VSP is the subdivision of viewpoint space generated by the \(\mathbf{n}\) planes corresponding to the \(\mathbf{n}\) faces of the polyhedron. Since the intersection of three general planes is a point, there can be at most \(O\left(n^{3}\right)\) intersection points of \(n\) planes. In order to get the largest possible VSP, we can assume that every set of three planes intersects in a distinct point. These intersection points are vertices of the VSP, so the VSP has \(O\left(n^{3}\right)\) vertices. At worst, each plane is intersected by all the others, resulting in \(O(n)\) lines subdividing each plane. Thus each plane is cut into a subdivision of \(O\left(n^{2}\right)\) vertices,

##### 5.1.1.2 Edge-Edge-Edge Occlusion

of the cell-face structure of the VSP, so its size is also \(\mathrm{O}\left(\mathbf{n}^{3}\right)\). 4.2.2. A Lower Bound The lower bound example of the orthographic case (see Figure 11) is also a lower bound in the perspective case. Consider the faces of the two bands in any octant, i.e. one quarter of each band in the same octant (see Figure 12).

Any three distinct faces from these band-quarters (two from one band and one from the other) determine a distinct vertex in the VSP since they have a distinct intersection point. There are \(\Omega(\mathbf{n})\) faces in each band quarter, so the VSP has \(\Omega\left(\mathbf{n}^{3}\right)\) vertices. The VSP must also have \(\Omega\left(\mathbf{n}^{3}\right)\) cells, so the aspect graph also has size

![Figure 12. Two quarter-bands.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-12-p023.png)

*Figure 12. Two quarter-bands.: Figure 12. Two quarter-bands. Figures 17a and 17b. Edge-edge-edge occlusion type 1.*

The \(\mathbf{n}\) planes corresponding to the \(\mathbf{n}\) faces of a polyhedron partition space into the VSP. In order to construct the VSP, we must find all of the intersections of the The algorithm builds the subdivision one plane at a time, as in the orthographic case. A plane \(\mathbf{p}\) can be added to the subdivision by finding the line of intersection of \(\mathbf{p}\) and each plane already in the subdivision. The line of intersection of \(\mathbf{p}\) and another The boundaries in viewpoint space generated by edge-edge-edge occlusion occur at viewpoints where three unconnected edges appear to intersect in a single point. In order to find the viewing directions in which three edges appear to intersect in a single point, let the endpoints of the three edges be p11, P12, P21, P22, P31, and p32 respectively, and pick a point on one of the edges, say

$$
p = p11+t(p12-P11), 0≤t≤1 (1)
$$

to vertices and faces between cells to edges joining them, and deleting everything else. This algorithm requires linear time in the size of the VSP, so the aspect graph can be constructed in \(O\left(\mathbf{n}^{3}\right)\) time. 5. Non-Convex Polyhedra

$$
(p-p21) × (P21-P22) (p-p31) × (P31-P32)
$$

and the intersection of these two planes has the direction

$$
d = [(p-p21)x (P21-P22)]×[(p-p31)×(P31-P32)] (2)
$$

Therefore d is a viewing direction in which the three edges appear to intersect at p. Note that d is a quadratic function of the parameter t. Thus viewing directions do not form an arc of a great circle in viewpoint space—rather, they form a quadratic curve. In Eq. (2) d is given in Cartesian coordinates. In order to transform it to the (0,ф) notation, we can use a Cartesian-to-spherical coordinate transformation:

$$
0 = tan-1 (dx dz) (3)
$$

$$
*=-sin-1(dy Nd,?+dy?+dz?) (4)
$$

There are \(O(n3)\) sets of three edges in a polyhedron, so there are \(O(n3)\) such curves in viewpoint space.

Note that horizon and vertex-edge occlusion boundaries can be considered a special case of edge-edge-edge occlusion. When two of the edges of edge-edge-edge occlusion meet at a vertex of the object, the result is vertex-edge occlusion. When all three of the edges lie on the same face of the object, the result is that the viewing direction lies in the plane containing the face. In that case the viewing direction is on the boundary of occlusion caused by the face turning away from the viewer.

We claim that the occlusion boundaries listed above represent a complete catalog of events that change the topology of an image. If the topology of the image is to change with a small change in viewpoint, then some region must appear or disappear, or regions must split or merge. If one of those things happens, it must start at some point in the image. The only way that such a change can happen is if at least three edges (or two parallel edges) meet at that point in the image, and we have listed all the unique ways in which three edges can meet in such a way that the topology of the image changes. If more than three edges meet at the point, then either they are degenerate and some subset of three generates the same event, or they are general and hence do not generate an event with viewpoint space extent; i.e., the lines appear to intersect at only a single viewpoint. Parallel edges that overlap in an image can be treated as two vertex-edge pairs.

#### 5.1.2 An Upper Bound

We have seen that the boundary points of occlusion are viewing directions where three object edges appear to intersect in a single point and there are \(O(n3)\) curves of such points. \(O(n?)\) quadratic curves on the sphere intersect in \(O(n6)\) points. The resulting subdivision of viewpoint space is planar, so it also has \(O(n°)\) edges and regions. Therefore the VSP and the aspect graph both have maximum size

#### 5.1.3 A Lower Bound

We have argued that there are \(O(n3)\) curves in viewpoint space potentially bounding regions of visibility and that there are \(O(n6)\) intersection points of these curves, so the VSP has size \(O(n6)\). In fact, these bounds are tight. We show this by presenting an example family of polyhedra with n faces that has an aspect graph (and hence a VSP) of size 2(n6).* Consider two grids of m strips each, with the strips close together. In front of these grids are two screens, each with m slits. The two screens and grids are

* This example is due to John Canny [1987].

arranged as in Figure 19. Note that the grid edges are not quite parallel to the screen edges.

![Figure 19. Two grids behind two screens.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-19-p030.png)

*Figure 19. Two grids behind two screens.: Figure 19. Two grids behind two screens.*

In a typical view of the grids behind the screens, parts of the grids are visible through only one slit of each screen. Furthermore, only a small part of the grid is visible through the slit (see Figure 20).

![Figure 20. A typical view of the two grids (seen simultaneously).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-20-p030.png)

*Figure 20. A typical view of the two grids (seen simultaneously).: Figure 20. A typical view of the two grids (seen simultaneously).*

the great circle with the normal \(\left(\mathbf{p}_{1}-\mathbf{p}\right) \times\left(\mathbf{p}_{2}-\mathbf{p}_{1}\right)\). The boundaries of the arc are the points of intersection with the lines ( \(\mathbf{p}, \mathbf{p}_{1}\) ) and ( \(\mathbf{p}, \mathbf{p}_{2}\) ).

![Figure 21. Close-up views through the slits.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-21-p031.png)

*Figure 21. Close-up views through the slits.: Figure 21. Close-up views through the slits. Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.*

Note that changing the viewing direction along the horizontal arrow causes the m nearly horizontal faces to disappear from view in the vertical slit and reappear one by one, generating a new boundary of occlusion in viewpoint space each time. This disappearing and reappearing of the horizontal faces in back occurs m times, so that the view through this slit requires Sm?) vertices in the aspect graph. There are m vertical slits, requiring 2(m2) boundaries each, for a total of 2(m3) boundaries. Note also that the view through a vertical slit doesn't change when the viewing direction is changed parallel to the vertical arrow. These boundaries are parallel straight lines (arcs of great circles) in viewpoint space.

However, the boundaries are orthogonal to the other 2(m3) boundaries, so there are 2(m6) intersection points of these boundaries. Therefore the VSP and the aspect graph have size 2(m6).

#### 5.1.4 An Algorithm

The algorithm for constructing the VSP in the case of convex polyhedra is relatively straightforward. The VSP is the partition of the sphere generated by great circles corresponding to the faces of the polyhedron. In the case of non-convex polyhedra this approach does not work. A face may not be visible from all viewpoints in front of it because it is partially occluded from some viewpoints by other faces.

However, the types of boundaries of regions of the VSP (events) have listed above, and the VSP can be computed from them. overlap in the image. The latter case is handled as two instances of vertex-edge occlusion. The boundaries in viewpoint space generated by edge-edge-edge occlusion occur at viewpoints where three unconnected edges appear to intersect in a single point. In order to find the viewing directions in which three edges appear to intersect in a single point, let the endpoints of the three edges be \(\mathbf{p}_{11}, \mathbf{p}_{12}, \mathbf{p}_{21}, \mathbf{p}_{22}\), \(\mathbf{p}_{31}\), and \(\mathbf{p}_{32}\) respectively, and pick a point on one of the edges, say The other two edges appear to intersect in some viewing direction \(\mathbf{d}\) at \(\mathbf{p}\) whenever the planes defined by \(\mathbf{p}\) and each of the other two edges intersect in a line with direction \(\mathbf{d}\). That is, the other two edges appear to intersect at \(\mathbf{p}\) from a viewing direction given by the intersection of the planes defined by \(\mathbf{p}, \mathbf{p}_{21}, \mathbf{p}_{22}\), and \(\mathbf{p}, \mathbf{p}_{31}\), \(\mathbf{p}_{32}\). Normals to these planes are given by and the intersection of these two planes has the direction Therefore \(\mathbf{d}\) is a viewing direction in which the three edges appear to intersect at \(\mathbf{p}\). Note that \(\mathbf{d}\) is a quadratic function of the parameter \(t\). Thus viewing directions do not form an arc of a great circle in viewpoint space-rather, they form a quadratic do not form an arc of a great circle in viewpoint space-rather, they form a quadratic curve. In Eq. (2) \(\mathbf{d}\) is given in Cartesian coordinates. In order to transform it to the \((\theta, \phi)\) notation, we can use a Cartesian-to-spherical coordinate transformation:

There are \(O\left(n^{3}\right)\) sets of three edges in a polyhedron, so there are \(O\left(n^{3}\right)\) such curves in viewpoint space. Note that horizon and vertex-edge occlusion boundaries can be considered a polyhedral scene, so it is simple to find the aspect boundaries from the asp. The asp is introduced in the next section. For a more detailed description of properties of the asp and algorithms for the asp see [Plantinga and Dyer, 1987a] and [Plantinga and Dyer, 1987b].

##### 5.1.4.1 The Aspect Representation

Three edges of a polyhedron may generate an event that bounds a region of constant aspect in viewpoint space, but in order to determine whether the three edges actually generate an event, we must determine several things. first, we must determine the viewpoints from which the edges appear to intersect in a single point in the image. Then, we must determine whether the edges are arranged in a way that represents a potential event. Finally, we must determine from which of the viewpoints the event is actually visible, and not occluded by other faces. i.e., the lines appear to intersect at only a single viewpoint. Parallel edges that overlap in an image can be treated as two vertex-edge pairs. 5.1.2. An Upper Bound We have seen that the boundary points of occlusion are viewing directions where three object edges appear to intersect in a single point and there are \(\mathrm{O}\left(\mathbf{n}^{3}\right)\) curves of such points. \(O\left(\mathbf{n}^{3}\right)\) quadratic curves on the sphere intersect in \(O\left(\mathbf{n}^{6}\right)\) points. The resulting subdivision of viewpoint space is planar, so it also has \(O\left(\mathbf{n}^{6}\right)\) 5.1.3. A Lower Bound We have argued that there are \(\mathrm{O}\left(\mathbf{n}^{3}\right)\) curves in viewpoint space potentially bounding regions of visibility and that there are \(\mathrm{O}\left(\mathbf{n}^{6}\right)\) intersection points of these curves, so the VSP has size \(\mathrm{O}\left(\mathbf{n}^{6}\right)\). In fact, these bounds are tight. We show this by curves, so the VSP has size \(\mathrm{O}\left(\mathbf{n}^{6}\right)\). In fact, these bounds are tight. We show this by presenting an example family of polyhedra with \(\mathbf{n}\) faces that has an aspect graph (and hence a VSP) of size \(\Omega\left(\mathbf{n}^{6}\right)\).* Consider two grids of \(\mathbf{m}\) strips each, with the strips close together. In front of these grids are two screens, each with \(\mathbf{m}\) slits. The two screens and grids are We can construct the asp for a point at location (*0,y0,z0) in a fixed coordinate system by considering what happens to the image of the point as the viewpoint changes. The projection onto the image plane can be separated into two parts, a rotation so that the viewing direction is along the z-axis and an orthographic projection into the z=0 plane. The rotation is given by

$$
cos e 0 sin e 7r1 0
$$

*o sin 0 sin $ + yo cos $ + zo cos 0 sin q, xo sin 0 cos $ - yo sin $ + z0 cos 9 cos $l

After orthographic projection into the image plane (u,v), this yields

![Figure 19. Two grids behind two screens.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-19-p030.png)

*Figure 19. Two grids behind two screens.: Figure 19. Two grids behind two screens.*

$$
u= x0 cos A - zo sin A (6)
$$

$$
v = x0 sin 0 sin $ + yo cos $ + zo cos 0 sin d (7)
$$

These equations have two degrees of freedom, 0 and $. Thus a point in 3-space has as its aspect representation \(a_{2}\)-D surface in aspect space.

The asp for a line segment is \(a_{3}\)-surface in aspect space bounded by 2surfaces. It can be written down directly by substituting parametric equations for a line segment into the point equations. We use a parametric representation for the line segment from (*0,70, 20) to (x1,71,21), with parameter s varying from 0 to 1. Letting a1 = x1-x0, b1 = Y1-y0, and c1 = z1-70 we have

$$
y(s) = y1 + b1 s Z(S) = Z1 + C1 S (8)
$$

![Figure 20. A typical view of the two grids (seen simultaneously).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-20-p030.png)

*Figure 20. A typical view of the two grids (seen simultaneously).: Figure 20. A typical view of the two grids (seen simultaneously).*

$$
U = (X1 + a1 S) cos 0 - (z1 + C1 S) sin e V = (*1 + a1 S) sin 0 sin ф + (V1 + b1 s) cos Ø + (Z1 + C1 S) cos 0 sin ¢ (10)
$$

The part of each grid that is visible behind the vertical screen is a portion of a nearlyvertical grid element and between 0 and \(\mathbf{m}\) nearly-horizontal grid elements. The The asp for a triangle consists of the asps for the bounding sides and vertices as described above plus connectivity information, namely, links from the asps for bounding sides to the asps for the adjacent vertices, and so on. Figure 22 shows the asp for the triangle (1,1,0), (2,1,0), (1,2,0) in object space. Since it is difficult to represent \(a_{4}\)-D volume in \(a_{2}\)-D figure, the figure shows two 3-D cross-sections of the asp at different fixed values of $. The 2-D cross-sections of the asp within each 3-D cross-section are the images of the triangle for the corresponding values of 0 and $. The asp represents all of these cross-sections continuously by representing the equations of the bounding surfaces.

![Figure 21. Close-up views through the slits.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-21-p031.png)

*Figure 21. Close-up views through the slits.: Figure 21. Close-up views through the slits. Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.*

![Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22a-p035.png)

*Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.: Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.*

![Figure 22b. A cross-section of the asp for the triangle for 0 = 0°.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22b-p035.png)

*Figure 22b. A cross-section of the asp for the triangle for 0 = 0°.: Figure 22b. A cross-section of the asp for the triangle for 0 = 0°. apparent intersection of four edges Tante 3. Viscalevffs ared corresponding asp features.*

![Figure 22c. A cross-section of the asp for the triangle for ф = 30°.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22c-p036.png)

*Figure 22c. A cross-section of the asp for the triangle for ф = 30°.: Figure 22c. A cross-section of the asp for the triangle for ф = 30°.*

###### 5.1.4.1.1 Representing Asps

We can represent an asp by representing the volume of aspect space that it occupies; specifically, by representing the 3-surfaces that bound the 4-D cells of aspect space. These 3-surfaces are bounded by 2-surfaces, the 2-surfaces by 1surfaces, and the 1-surfaces by points. Unfortunately, the surfaces are not in general planar, so the object is not a polytope (i.e. the generalization of a polygon, polyhedron, etc.). However, the surfaces are well-behaved: the trigonometric functions in the equations for the surfaces can be eliminated by a spherical-toCartesian coordinate transformation of the representation for viewpoints, from (0,¢) to V = (Vx, Vy, Vz). As a result, the surfaces are algebraic, and each can be represented with a few constants.

This algorithm can be executed in \(O\left(\mathbf{n}^{7}\right)\) time, which is somewhat worse than the worst case size of the aspect graph, \(O\left(\mathbf{n}^{6}\right)\). A more serious problem with this algorithm is that its best case time is \(\Omega\left(\mathbf{n}^{7}\right)\). For example, the VSP for a convex polyhedron has size \(\mathrm{O}\left(\mathbf{n}^{2}\right)\) but this algorithm would still take time \(\Omega\left(\mathbf{n}^{7}\right)\). Since the worst case is very large and most aspect graphs are not as large as the worst case, an algorithm with better behavior for simple polyhedra would be much preferable. The size of the subdivision generated by \(\mathbf{m}\) curves is \(\mathrm{O}\left(\mathbf{m}^{2}\right)\), so in order to construct the aspect graph more efficiently we compute the actual boundaries of than \(\Theta\left(\mathbf{n}^{6} \log \mathbf{n}\right)\). In order to do that, we make use of the aspect representation or asp for the object. The asp represents all of the visual events for a polyhedron or use for the 3-D faces bounding \(a_{4}\)-polytope. We refer to the 2-surfaces that bound the facets as ridges, and the 1-surfaces or curves as edges. \(A_{4}\)-D volume of aspect space bounded by facets is referred to as a cell. In general, the asp is \(a_{4}\)-manifold in aspect space, i.e. a region or regions of aspect space partitioned into cells, which we refer to as a subdivision. The cells correspond to polygons in the image of the object and the facets bounding the cells correspond to edges.

Thus, the asp is very much like a set of 4-polytopes in aspect space except that the "faces" are curved, and we must store the constants of the equation for each face. We represent the asp with a data structure similar to that of a polyhedron, except that the asp is 4-D rather than 3-D and the volume of the asp is partitioned into 4-D cells. A cell of aspect space is represented as a node with pointers to the bounding facets. The facets are represented by the constants of the equation for the 3-surface and pointers to the bounding ridges, and so on. We can also work with asps much as we would with polyhedra. For example, we can determine whether two asps intersect by determining whether some face of one intersects some face of the other, and if not, whether one is completely inside the other.

###### 5.1.4.1.2 Asps and Visibility

the asp. The asp is a representation of the volume of aspect space that a polyhedron occupies, where aspect space is defined as viewpoint space cross the image plane, i.e. the tangent bundle of planes on the sphere. If we denote a viewpoint by ( \(\theta, \phi\) ) and a point in the image plane by ( \(u, v\) ), then we can denote a point of aspect space ( \(\theta, \phi, u, v)\). The orientation of the image plane with respect to the line of sight is fixed so that In fact, a fundamental property of aspect space is that occlusion in object space corresponds to set subtraction in aspect space. That is, if one polygon partially occludes another, we can characterize that occlusion in aspect space by subtracting the asp of the first from the second. For example, in Figure 23a we show two triangles in object space, one in the z=0 plane (left) and one in the z=1 plane; in Figure 23b we show the asps for the triangles (with $ = 0).

![Figure 23b. The asps for two triangles.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-23b-p038.png)

*Figure 23b. The asps for two triangles.: Figure 23b. The asps for two triangles.*

![Figure 23a. Two triangles in object space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-23a-p038.png)

*Figure 23a. Two triangles in object space.: Figure 23a. Two triangles in object space.*

In Figure 24 we show the set subtraction of the second triangle from the first. Since set subtraction in aspect space corresponds to occlusion in object space, any cross section of Figure 24 for a particular viewpoint corresponds to the part of the first triangle visible from that viewpoint (i e. not occluded by the second).

![Figure 24. Occlusion in image space corresponds to subtraction in aspect space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-24-p038.png)

*Figure 24. Occlusion in image space corresponds to subtraction in aspect space.: Figure 24. Occlusion in image space corresponds to subtraction in aspect space. Figure 27. A viewing direction along which four object edges appear to intersect in a single point in an image.*

Since it is difficult to represent a 4-D volume in a 2-D figure, the figure shows two 3-D cross-sections of the asp at different fixed values of \(\phi\). The 2-D cross-sections of the asp within each 3-D cross-section are the images of the triangle for the corresponding values of \(\theta\) and \(\phi\). The asp represents all of these cross-sections continuously by representing the

![Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22a-p035.png)

*Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.: Figure 22a. The triangle (1,1,0), (2,1,0), (1,2,0) in object space.*

###### 5.1.4.1.3 Aspect Surfaces

The aspect representation for a non-convex polygon is a cell of aspect space, bounded by 3-surfaces or facets. The facets correspond to the edges of the polygon. Ridges bound the visibility of facets, and there are ridges corresponding to the vertices bounding the edges of the polygon. There is also another sort of ridge, corresponding to the case where the visibility of a polygon edge is bounded by another, occluding edge. In that case the ridge corresponds to the apparent intersection of the two object edges. This type of ridge results from the subtraction of the asp for the occluding polygon from the asp for the given polygon. The surface on which the ridge lies results from the intersection of the surfaces on which the two facets lie. This is the general sort of 2-surface.

![Figure 22b. A cross-section of the asp for the triangle for 0 = 0°.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22b-p035.png)

*Figure 22b. A cross-section of the asp for the triangle for 0 = 0°.: Figure 22b. A cross-section of the asp for the triangle for 0 = 0°. apparent intersection of four edges Tante 3. Viscalevffs ared corresponding asp features.*

The boundaries of an asp ridge are a result of the horizon effect or the more general sort of event bounding the visibility of a ridge: the apparent intersection of three object edges in a single image point. Asp vertices correspond to visual events that are visible from a single viewpoint and that occupy a single point of the image plane: the apparent intersection of four object edges in a single image point.

In order to find the intersection of cells of aspect space, we must be able to find the intersection of pairs of asp surfaces of various sorts. Note that all of the asp surfaces—3-surfaces, 2-surfaces, 1-surfaces, and vertices—result from the intersection of a set of asp 3-surfacesone, two, three, and four respectively. Thus, finding the intersection of an asp 3-surface and an asp 2-surfaces is equivalent to finding the intersection of the three "parent" asp 3-surfaces involved. Also, since two asp 1-surfaces that lie on the same 2-surface have two common 3-surface "parents," finding the intersection of two 1-surfaces is equivalent to finding the intersection of the four unique 3-surfaces involved in the problem. In general, finding the intersection of two asp surfaces is equivalent to finding the intersection of the unique "parents" of those surfaces.

![Figure 22c. A cross-section of the asp for the triangle for ф = 30°.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-22c-p036.png)

*Figure 22c. A cross-section of the asp for the triangle for ф = 30°.: Figure 22c. A cross-section of the asp for the triangle for ф = 30°.*

\(A_{3}\)-surface of aspect space corresponds to the visibility of a line in object space. The equations for such a surface for a line passing through the points p1 = (x1,y1,21) and p1 + a1 = (x1+a1,y1+b1,21+C1) were derived earlier and are repeated here:

$$
u= (x1 + S a1) cos 0 - (z1 + S C1) sin e (11)
$$

$$
v = (x1 + S a1) sin 0 sin $ + (y1 + s b1) cos $ + (21 + S C1) cos 0 sin $ (12)
$$

Therefore we can work with the surfaces in much the same manner as we would work with lines and planes in a polyhedron. For example, we can calculate the intersection of any two of these surfaces in closed form, so that calculating the intersection for two particular surfaces is a matter of plugging constants into an equation. The intersection of two 3-surfaces is \(a_{2}\)-surface and, with the viewpoint Using V = (Vx, vy, Vz) for the viewpoint, we get

![Figure 25. The viewing direction along which two lines appear to intersect.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-25-p040.png)

*Figure 25. The viewing direction along which two lines appear to intersect.: Figure 25. The viewing direction along which two lines appear to intersect.*

$$
(x2 + 52 a2) - (x1 +S a1) V: = (22 + S2 C2) - (z1 + 8 C1) (13)
$$

From these equations we can find u and v as a function of 0 and $. The surface can be represented by twelve constants: a1, a2, b1, b2, c1, c2, x1, X2, Y1, Y2, 21, z2. These are related to the coordinates of the four endpoints of the two lines involved in the visual event.

5.1.4.1.2. Asps and visibility Consider again the asp for a point. Eqs. (6) and (7) for the asp for that point are defined for all values of \(\theta\) and \(\phi\). This is as one would expect, since a point is visible from any viewing direction. We can represent a point which is not visible from every viewing direction, say a point which is occluded in some directions by a We could find the 1-surface by finding the intersection of three pairs of equations of the form of Eqs. (11) (12) for three 3-surfaces. However, there is a simpler way to find the form. Consider three edges in space, P1 to p1+ a1, P2 to p2 + a2, and p3 to p3 + a3. Pick a point p1 + sal on one line (see Figure 26) and find a line through that point that intersects both of the other lines.

![Figure 26. A viewing direction along which three object edges appear to intersect](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-26-p041.png)

*Figure 26. A viewing direction along which three object edges appear to intersect: Figure 26. A viewing direction along which three object edges appear to intersect*

Pital PItsa, 9-P3 PI P2 and (14) Solving for s yields s = V. [P2-P1) xa2! V. (a1 xa2) (15) Note the viewing direction must be along the intersection of the planes defined by the point pi + s al and each of the other two lines. Normals to these planes are given by

$$
(P1 + 881 - P2) X 82
$$

so a vector parallel to the viewing direction in question is given by

![Figure 23a. Two triangles in object space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-23a-p038.png)

*Figure 23a. Two triangles in object space.: Figure 23a. Two triangles in object space.*

A vertex of aspect space results from the intersection of four asp 3-surfaces, two general 2-surfaces, two 1-surfaces on \(a_{2}\)-surface, or any other combination of surfaces with four unique 3-surface "parents." The visual even that gives rise to an asp vertex is the apparent intersection of four object edges in a single point. This occurs from only one viewpoint, so the corresponding asp surface is a vertex.

In order to find the viewing direction at which this visual event occurs, consider four lines in space, through p1 & PI+ 81, P2 & P2 + a2, P3 & P3 + a3, and P4 & P4 + a4. Pick a point p1 + s a1 on one line (see Figure 27) and suppose a line through that point intersects all three of the other lines.

![Figure 27. A viewing direction along which four object edges appear to intersect ir](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-27-p042.png)

*Figure 27. A viewing direction along which four object edges appear to intersect ir: Figure 27. A viewing direction along which four object edges appear to intersect ir*

![Figure 23b. The asps for two triangles.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-23b-p038.png)

*Figure 23b. The asps for two triangles.: Figure 23b. The asps for two triangles.*

![Figure 24. Occlusion in image space corresponds to subtraction in aspect space.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-24-p038.png)

*Figure 24. Occlusion in image space corresponds to subtraction in aspect space.: Figure 24. Occlusion in image space corresponds to subtraction in aspect space. Figure 27. A viewing direction along which four object edges appear to intersect in a single point in an image.*

$$
(P1 +S 21 - P3) Xa3
$$

If the three planes intersect in a single line, then the normals have a triple cross product of zero, yielding a cubic equation in s. Thus, we can find the vertex by solving the cubic equation for s.

###### 5.1.4.1.4 Size of Asps

In the case of a convex polyhedron, the asp has size \(O(n)\) for an object with n faces since there is a face in the polyhedron for every facet in the asp and the sizes of the facets in the asp correspond directly to the size of the faces in the polyhedron. However, in the non-convex case the asp is much larger since the cross section of an asp at any value of (0,4) is a view of the corresponding object with hidden lines removed. In [Plantinga and Dyer, 1987] it is shown that the maximum size of the asp for a general polyhedron with n faces is \(O(n4)\). However, the worst case occurs only for objects or scenes that are visually very complex, that is, that have a large amount of occlusion; Figure 28 is an example of such a scene.

![Figure 28. An example of a scene for which the asp has size O(n*).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-28-p043.png)

*Figure 28. An example of a scene for which the asp has size O(n*).: Figure 28. An example of a scene for which the asp has size O(n*).*

It is perhaps surprising that the asp, which represents the appearance of an object from every viewpoint, has smaller size than the VSP, which only represents the regions of constant aspect in viewpoint space. The asp has size \(O(n4)\) while the VSP has size \(O(n6)\). The asp is smaller for a reason analogous to the reason that a polyhedron of size n can have an image of size \(O(n?)\). Forming the image of the polyhedron requires projecting lines in R3 into R?, and lines that did not intersect in R3 may intersect in R2. A set of n lines can have \(O(n2)\) intersection points. Similarly, projecting the \(O(n3)\) 1-surfaces of the asp into viewpoint space causes them to intersect where they did not intersect before, resulting in \(O(n6)\) intersection points.

###### 5.1.4.1.5 Constructing the Asp

![Figure 25. The viewing direction along which two lines appear to intersect.](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-25-p040.png)

*Figure 25. The viewing direction along which two lines appear to intersect.: Figure 25. The viewing direction along which two lines appear to intersect.*

##### 5.1.4.2 Using the Asp to Construct the VSP

![Figure 26. A viewing direction along which three object edges appear to intersect](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-26-p041.png)

*Figure 26. A viewing direction along which three object edges appear to intersect: Figure 26. A viewing direction along which three object edges appear to intersect*

![Figure 27. A viewing direction along which four object edges appear to intersect ir](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-27-p042.png)

*Figure 27. A viewing direction along which four object edges appear to intersect ir: Figure 27. A viewing direction along which four object edges appear to intersect ir*

### 5.2 Perspective Case

The viewing direction must intersect the three planes define by the point \(\mathbf{p}_{1}+s \mathbf{a}_{1}\) and each of the other lines. Normals to these planes are given by If the three planes intersect in a single line, then the normals have a triple cross product of zero, yielding a cubic equation in \(s\). Thus, we can find the vertex by solving the cubic equation for \(s\). 5.1.4.1.4. Size of Asps

#### 5.2.1 Occlusion under Perspective Projection

However, since viewpoint space is R3, the boundary generated in viewpoint space in each case is a surface in R3 rather than a curve on the sphere. In the orthographic model, a face turning away from the viewer generates a visibility boundary that is an arc of a great circle on the sphere. In the perspective model, the boundary of visibility is a part of a plane in viewpoint space, specifically, the plane containing the face. This is true because a face "turns away from the viewer" whenever the viewpoint drops below the plane containing the face.

Edge-vertex occlusion boundaries (see Figures 15 and 16) are also parts of a plane. The plane is defined by the vertex and the edge involved in the visual event. The lines bounding the section of the plane corresponding to the occlusion boundary are the lines defined by the vertex and each of the endpoints of the edge.

It is perhaps surprising that the asp, which represents the appearance of an object from every viewpoint, has smaller size than the VSP, which only represents the regions of constant aspect in viewpoint space. The asp has size \(O\left(\mathbf{n}^{4}\right)\) while the VSP has size \(\mathrm{O}\left(\mathbf{n}^{6}\right)\). The asp is smaller for a reason analogous to the reason that a

![Figure 28. An example of a scene for which the asp has size O(n*).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-28-p043.png)

*Figure 28. An example of a scene for which the asp has size O(n*).: Figure 28. An example of a scene for which the asp has size O(n*).*

#### 5.2.2 Upper Bound

Since the surfaces are algebraic, any pair has a constant number of curves of intersection and any three have a constant number of points of intersection. Thus the \(O(n3)\) surfaces have \(O(n9)\) intersection points.

On any one of the surfaces there can be at most \(O(no)\) edges and faces, because the intersection of that surface with the other surfaces results in \(a_{2}\)-D subdivision of that surface by \(O(n3)\) curves. Summing for all surfaces, a total of \(O(n9)\) vertices, edges, and faces bound cells of viewpoint space. Since a cell must have bounding faces and a face can bound at most two cells, there are \(O(n9)\) cells. Thus, the VSP has size \(O(n9)\).

#### 5.2.3 Lower Bound

In this section we show that \(O(n9)\) is a tight bound on the maximum size of the VSP and aspect graph. We present a polyhedral scene that has a VSP of size 2(n9). The example is similar to the lower bound example in the orthographic case (Section 5.1.3) except that changing the viewpoint in any of three orthogonal directions changes the aspect (see Figure 29).

![Figure 29. Polyhedra with VSP of size 2(n°).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-29-p048.png)

*Figure 29. Polyhedra with VSP of size 2(n°).: Figure 29. Polyhedra with VSP of size 2(n°).*

1987b]. In the former paper it is also shown that subtraction of a cell from an asp can be constructed in \(O(\mathbf{n_{m}})\) time for asps of size \(\mathbf{n}\) and \(\mathbf{m}\) using the brute-force intersection algorithm, and the asp for a polyhedral scene of size \(\mathbf{n}\) can be From any viewpoint inside the cube, some subset of faces of each grid is visible through one of the slits. In a manner similar to the orthographic example of Section 5.1.3, changing the viewpoint parallel to one of the edges of the cube changes the faces of one grid through one screen, but it does not affect the view of the other two grids. Each grid generates \(S(n2)\) boundaries of visibility through each slit, or 2(n3) boundaries of visibility through the whole screen. All of the boundaries are parallel planes, so the 2(n3) planes corresponding to each screen grid pair intersect in 2(n°) points. Therefore the VSP and the aspect graph have size 2(n°).

Note that we could just as well have used orthographic projection in constructing this example. However, in our orthographic model we define viewpoint space to be the sphere. This example would suffice as a \(S(n9)\) lower bound under orthographic projection as well if viewpoint space is R3.

#### 5.2.4 An Algorithm

Since the VSP is a partition of R3 under the perspective model, in order to construct it we must be able to calculate the surfaces in viewpoint space that bound the aspects. These surfaces are given by Eq. (11) for sets of three object edges in all orders. As in the orthographic case, we can calculate the VSP using a naive algorithm: construct all possible boundaries of visibility using Eq. (11) for all sets of three object edges in all orders. Find the subdivision of viewpoint space that these boundaries generate; the result is the VSP.

It remains to construct the subdivision of viewpoint space generated by these events. We call the cells of the subdivision regions, the boundaries of the regions edges, and the intersection points of the edges vertices. We will use as a data structure for the subdivision nodes for regions, edges, and vertices, with links between nodes corresponding to adjacent regions and edges or edges and vertices. At each edge node we store the constants of the curve on which the edge lies. The edge-vertex structure of the subdivision generated by \(\mathbf{m}\) curves on the sphere is constructed incrementally, starting with an empty subdivision and adding curves one by one. Adding a curve \(\mathbf{c}\) to the subdivision involves finding the intersection points of \(\mathbf{c}\) with every curve already in the subdivision and inserting them into the subdivision. \(\mathbf{c}\) will intersect each curve already in the subdivision at Unfortunately, as in the orthographic case, the best-case and worst-case times are the same for this algorithm: it requires time 2(n10) even for simple objects. An algorithm will perform better on the average if it finds the the exact set boundaries in viewpoint space before finding the subdivision that they generate. It is important to keep the number of boundaries in viewpoint space as small as possible before finding the subdivision that they generate because m boundaries that are not highly degenerate form a subdivision of size \(O(m3)\). In order to compute the exact visibility boundaries for each face of the polyhedron, we again use the aspect representation, this time constructed using perspective projection. We first describe the asp under perspective projection and then show how to use it to construct the VSP.

##### 5.2.4.1 The Asp under Perspective Projection

Since in the perspective case we take viewpoint space to be R3 rather than the sphere, aspect space is \(a_{5}\)-D space: R3 cross the image plane. To represent viewpoint space we use spherical coordinates (0,$,r), similar to the orthographic case but with the addition of distance r from the origin. Thus a point of aspect space is represented (0,¢,r,u,v), where (0,ф,r) is the viewpoint and (u,v) is the point on the image plane. The viewing direction is the direction from (0,ø,r) to the origin. A point (0,ф,r,u, v) of aspect space is in the asp for a polyhedron when (u,v) is in the image of the polyhedron from the viewpoint (0,ф,r). In some cases we will also use Cartesian coordinates for viewpoints, (Vx, Vy, Vz) = V. case. For example, constructing the asp for a convex object takes \(\mathrm{O}\left(n^{2}\right)\) time using the algorithm given, and finding the VSP generated by the \(O(n)\) events takes \(O(n\({}^{2}\)\) \(\log n)\) time. The brute-force algorithm requires \(\Theta\left(n^{7}\right)\) time even in this case. The aspect graph is the dual of the region-boundary structure of the VSP. We find it by finding the dual of the VSP, as in the convex case. The aspect graph has the same maximum size as the VSP, \(\Theta\left(\mathbf{n}^{6}\right)\). The aspect graph has a vertex for every distinct aspect of the polyhedron, but as we have defined it the vertices of the aspect graph contain no information about the particular aspect that they represent. In order to characterize the aspect one can store an image of the object from one of the

and can be computed in \(\mathrm{O}\left(\mathbf{n}^{2}\right)\) time with a hidden-line removal algorithm, so the aspect graph with images at each vertex requires space and time \(O\left(\mathbf{n}^{8}\right)\) to construct. 5.2. Perspective Case

$$
u = f (x0 cos 9 - zo sin e) r - (xo sin 0 cos $ - yo sin $ + Zo cos 0 cos 4) (18)
$$

$$
f (*0 sin 0 sin $ + yo cos $ + Z0 cos 0 sin $) V = r - (x0 sin e cos $ - yo sin $ + Zo cos A cos $) (19)
$$

the orthographic model. For example, in modelling a house under the orthographic model, the only viewpoints allowed are a sphere of viewpoints outside of the house. However, in the perspective model viewpoint space is \(R^{3}\), so the viewpoint can be outside of the house, in the living room, or inside a closet.

The asp for a polyhedron under the perspective model is much like the asp under the orthographic model. The difference is that the asp is \(a_{5}\)-manifold in \(a_{5}\)-D aspect space rather than \(a_{4}\)-manifold in 4-space. It can be constructed in the same way as in the orthographic case, if the algorithms for intersection and union are generalized to 5-D. edge-vertex, edge-edge-edge, etc.) also occur in the perspective model. However, since viewpoint space is \(\mathrm{R}^{3}\), the boundary generated in viewpoint space in each case is a surface in \(\mathrm{R}^{3}\) rather than a curve on the sphere. In the orthographic model, a face turning away from the viewer generates a visibility boundary that is an arc of a great circle on the sphere. In the perspective model, the boundary of visibility is a part of a plane in viewpoint space, specifically, the plane containing the face. This is true because a face "turns away from the viewer" whenever the viewpoint drops below the plane containing the face. Edge-vertex occlusion boundaries (see Figures 15 and 16) are also parts of a

The surfaces corresponding to these events are closely related to those in the orthographic case. There are two differences, resulting from the use of perspective rather than orthographic projection and from taking viewpoint space to be R3 rather than the sphere. The viewing directions from which an event occurs in the perspective case are the same as those from which the event occurs in the orthographic case. However, all of the viewpoints along a line parallel to the viewing direction and intersecting an object point at which the event occurs must be taken as the set of viewpoints at which the event occurs. Thus the surface is of one dimension higher in the perspective case.

Under the perspective model the asp faces correspond to the same visual events as they do under the orthographic model, except that the surfaces are in R3 rather than on the sphere. Some visual events that were not visible in the orthographic case because they were behind other faces may be visible in the perspective case from some viewpoints in R3. However, the asymptotic worst-case size of the asp and time to construct the asp is the same as the orthographic case since the same events are visible in the worst case.

##### 5.2.4.2 Using the Asp to Construct the VSP

In this section we show that \(O\left(\mathbf{n}^{9}\right)\) is a tight bound on the maximum size of the VSP and aspect graph. We present a polyhedral scene that has a VSP of size \(\Omega\left(\mathbf{n}^{9}\right)\). The example is similar to the lower bound example in the orthographic case (Section 5.1.3) except that changing the viewpoint in any of three orthogonal directions changes the aspect (see Figure 29).

Projecting the 2-faces into viewpoint space is done by solving the equation for \(a_{2}\)-surface for viewpoint as a function of two parameters. The equation for the 2-surface is already expressed in this form in Eq. 17. The form of Eq. 17 is

$$
V= a1+ sa2+r[s? az+sa4+as]
$$

$$
a1 + 81a2 + r1[ s12 a3 + 8124+ a5] = a6 + s2a7+r2[s2? a8 + 52 ag + a10] (20)
$$

This equation is satisfied for some values of r1 and r2 whenever three vectors are coplanar: the two viewing directions [s12 a3 + s1 a4 + a5] and [sz? ag + s2 ag + a10] and the vector between the two object points at which the event occurs, al + s1 a2 a6-s2 a7. Therefore Eq. (20) is satisfied when the triple cross product of these three vectors is zero. This yields a cubic equation in s1 and s2, which can be solved for s2 in terms of s1 with the cubic equation. The intersection of three surfaces of the form of Eq. 17 yields two algebraic equations for s2 in terms of s1; finding intersection points involves setting the equations equal and finding zeros using numerical methods.

![Figure 29. Polyhedra with VSP of size 2(n°).](/Users/evanthayer/Projects/paperx/docs/1990_visibility_occlusion_and_the_aspect_graph/figures/figure-29-p048.png)

*Figure 29. Polyhedra with VSP of size 2(n°).: Figure 29. Polyhedra with VSP of size 2(n°).*

From any viewpoint inside the cube, some subset of faces of each grid is visible through one of the slits. In a manner similar to the orthographic example of Section 5.1.3, changing the viewpoint parallel to one of the edges of the cube changes the faces of one grid through one screen, but it does not affect the view of the other two grids. Each grid generates \(\Omega\left(\mathbf{n}^{2}\right)\) boundaries of visibility through each slit, or \(\Omega\left(\mathbf{n}^{3}\right)\) boundaries of visibility through the whole screen. All of the boundaries are parallel planes, so the \(\Omega\left(\mathbf{n}^{3}\right)\) planes corresponding to each screen/grid pair intersect in \(\Omega\left(\mathbf{n}^{9}\right)\) points. Therefore the VSP and the aspect graph have size \(\Omega\left(\mathbf{n}^{9}\right)\). Note that we could just as well have used orthographic projection in constructing this example. However, in our orthographic model we define viewpoint space to be the sphere. This example would suffice as a \(\Omega\left(\mathbf{n}^{9}\right)\) lower bound under orthographic projection as well if viewpoint space is \(R^{3}\). 5.2.4. An algorithm Since the VSP is a partition of \(R^{3}\) under the perspective model, in order to the aspects. These surfaces are given by Eq. (11) for sets of three object edges in all orders. As in the orthographic case, we can calculate the VSP using a naive algorithm: construct all possible boundaries of visibility using Eq. (11) for all sets of three object edges in all orders. Find the subdivision of viewpoint space that these boundaries generate; the result is the VSP. A subdivision of \(R^{3}\) by \(\mathbf{m}\) algebraic surfaces has size \(O\left(\mathbf{m}^{3}\right)\), so the \(O\left(\mathbf{n}^{3}\right)\) boundaries in viewpoint space generate a subdivision of size \(\mathrm{O}\left(\mathbf{n}^{9}\right)\) with a 3-D viewpoint space. The subdivision can be constructed in \(\mathrm{O}\left(n^{9} \log n\right)\) time using the algorithm given in Section 5.2.4.2. It remains to test each face \(\mathbf{f}\) that separates two cells of the subdivision to determine whether the aspect actually changes at \(\mathbf{f}\). We can test whether the aspect actually changes by finding the appearance of the image immediately around the image point where the event occurs that gave rise \(\mathbf{f}\). If section of the image near the event are the same from viewpoints immediately to either side of \(\mathbf{f}\), then that face should be removed from the VSP and the cells on either side merged. This test can be performed in \(O(n)\) time for each face of the VSP, so using this algorithm the VSP can be constructed in \(\mathrm{O}\left(\mathbf{n}^{10}\right)\) time. Unfortunately, as in the orthographic case, the best-case and worst-case times are the same for this algorithm: it requires time \(\Omega\left(\mathbf{n}^{10}\right)\) even for simple objects. An

## 6 Related work

to keep the number of boundaries in viewpoint space as small as possible before finding the subdivision that they generate because \(\mathbf{m}\) boundaries that are not highly degenerate form a subdivision of size \(\Theta\left(\mathbf{m}^{3}\right)\). In order to compute the exact visibility boundaries for each face of the polyhedron, we again use the aspect representation, this time constructed using perspective projection. We first describe the asp under perspective projection and then show how to use it to construct the VSP. 5.2.4.1. The Asp under Perspective Projection Since in the perspective case we take viewpoint space to be \(\mathrm{R}^{3}\) rather than the sphere, aspect space is a 5-D space: \(R^{3}\) cross the image plane. To represent sphere, aspect space is a 5-D space: \(R^{3}\) cross the image plane. To represent viewpoint space we use spherical coordinates \((\theta, \phi, r)\), similar to the orthographic case but with the addition of distance \(r\) from the origin. Thus a point of aspect space is represented \((\theta, \phi, r, u, v)\), where \((\theta, \phi, r)\) is the viewpoint and \((u, v)\) is the point on the image plane. The viewing direction is the direction from \((\theta, \phi, r)\) to the origin. A point \((\theta, \phi, r, u, v)\) of aspect space is in the asp for a polyhedron when ( \(u, v\) ) is in the image of viewpoints, it has as its asp one point in the image plane for each viewpoint \(\mathbf{V}\). That is, the asp for a point is \(a_{3}\)-surface in aspect space. We can determine the point in the image plane in the same manner that we found the point in the orthographic case, except that we now use perspective rather than orthographic projection. In that case, after a rotation to make the viewpoint lie on the \(\mathbf{z}\)-axis, the point \(\mathbf{p}\) was given by Eq. (5) in Section 5.1.4.1. Under perspective projection, a point ( \(\mathrm{p}_{\mathrm{x}}, \mathrm{p}_{\mathrm{y}}, \mathrm{p}_{\mathrm{z}}\) ) projects to where \(f\) is the focal length and \(d\) is the distance along the \(z\)-axis from the viewpoint to where \(f\) is the focal length and \(d\) is the distance along the \(z\)-axis from the viewpoint to the object point, i.e. the difference in z-coordinates. Thus, the asp for the point \(\left(\mathrm{x}_{0}, \mathrm{y}_{0}, \mathrm{z}_{0}\right)\) from the viewpoint \((\theta, \phi, \mathrm{r})\) is given by the asp can be had by substituting Eq. (8) (the parametric equations for a line) for \(\mathrm{x}_{0}\), \(y_{0}\), and \(z_{0}\) into Eqs. (18) and (19). The asp for a polygon is a cell of aspect space bounded by the 4-surfaces corresponding to the edges bounding the cell.

The asp for a polyhedron under the perspective model is much like the asp under the orthographic model. The difference is that the asp is \(a_{5}\)-manifold in \(a_{5}\)-D aspect space rather than \(a_{4}\)-manifold in 4-space. It can be constructed in the same way as in the orthographic case, if the algorithms for intersection and union are generalized to 5-D. The asp faces corresponding to visual events are of one dimension higher in the perspective case. In Table 4 we show visual events and corresponding asp features for the perspective case. Note that there are no true 0-D visual events. A \(0-\mathrm{D}\) visual event would be a visual event visible at a particular point in the image, from only one viewpoint. However, for any visual event there is some line in viewpoint space along which the same visual event is visible, at points a little closer or further from the object. The only way that \(a_{1}\)-D visual event ends is when the Researchers have uses different numbers of characteristic views, ranging from a small or moderate constant (up to about 300) [Chakravarty and Freeman, 1982; Fekete and Davis, 1984; Korn and Dyer; Scott, 1984; Thorpe and Shafer, 1983] to every "topologically distinct" view of the object [Castore, 1983; Castore and Crawford, 1984; Crawford, 1985]. Ikeuchi [1987] constructs and uses an "interpretation tree" in \(a_{3}\)-D object recognition algorithm for bin-picking. This interpretation tree bears some resemblance to the aspect graph. Rosenfeld [1986] suggests that fast object recognition will require representing an object as a series of "characteristic views" or "aspects." Other researchers propose that the aspect graph be used as part of a general representation for computer vision [Schneier, Lumia, & Kent, 1986].

The surfaces corresponding to these events are closely related to those in the orthographic case. There are two differences, resulting from the use of perspective rather than orthographic projection and from taking viewpoint space to be \(R^{3}\) rather than the sphere. The viewing directions from which an event occurs in the perspective case are the same as those from which the event occurs in the Avis and Toussaint [1981] compute visibility from many viewpoints simultaneously when they discuss the visibility of a polygon in the plane from viewpoints along an edge in the plane. However, their algorithm computes the parts of a polygon that are visible from some point along a line in the plane, rather than visibility from every point along the line. Consequently, their work does not really compute visibility from a continuous region of viewpoints. Other work on the visibility polygon from an edge includes [El Gindy, 1984; Chazelle and Guibas, 1985; Guibas et al., 1986; Suri and O'Rourke, 1986]. orthographic case because they were behind other faces may be visible in the perspective case from some viewpoints in \(R^{3}\). However, the asymptotic worst-case size of the asp and time to construct the asp is the same as the orthographic case since the same events are visible in the worst case. 5.2.4.2. Using the Asp to Construct the VSP As in the orthographic case, all boundaries of VSP regions are represented as a function of viewpoint by faces in the asp. In the perspective case, events are the

## 7 Conclusion

In this paper we analyzed the visibility and occlusion of faces of a polyhedron over all viewpoints. We showed how to calculate boundaries of visibility and regions of constant aspect in viewpoint space. We did this by listing the ways in which aspect can change. The aspect changes when a region in the image appears or disappears, or when regions merge or split. subdivision of viewpoint space they generate. Projecting the 2-faces into viewpoint space is done by solving the equation for \(a_{2}\)-surface for viewpoint as a function of two parameters. The equation for the 2-surface is already expressed in this form in Eq. 17. The form of Eq. 17 is The intersection of two such surfaces is a curve of the form This equation is satisfied for some values of \(r_{1}\) and \(r_{2}\) whenever three vectors are coplanar: the two viewing directions \(\left[s_{1}{ }^{2} \mathbf{a}_{3}+s_{1} \mathbf{a}_{4}+\mathbf{a}_{5}\right]\) and \(\left[s_{2}{ }^{2} \mathbf{a}_{8}+s_{2} \mathbf{a}_{9}+\mathbf{a}_{10}\right]\) and the vector between the two object points at which the event occurs, \(\mathbf{a}_{1}+s_{1} \mathbf{a}_{2}-\) and the vector between the two object points at which the event occurs, \(\mathbf{a}_{1}+s_{1} \mathbf{a}_{2}-\) \(\mathbf{a}_{6}-s_{2} \mathbf{a}_{7}\). Therefore Eq. (20) is satisfied when the triple cross product of these three vectors is zero. This yields a cubic equation in \(s_{1}\) and \(s_{2}\), which can be solved for \(s_{2}\) in terms of \(s_{1}\) with the cubic equation. The intersection of three surfaces of the form of Eq. 17 yields two algebraic equations for \(s_{2}\) in terms of \(s_{1}\); finding intersection points involves setting the equations equal and finding zeros using numerical subdivision of viewpoint space that they generate. The algorithms for convex polyhedra run in time that is worst-case optimal and in fact optimal for all polyhedra that are not highly degenerate. The algorithms for the non-convex polyhedra run in nearly optimal time in the sense that the runtime is within a log factor of output size for any polyhedron that is not highly degenerate. constants defining the surface on which it lies. We construct the subdivision generated by \(\mathbf{m}\) surfaces in \(R^{3}\) by adding surfaces to the partial subdivision, one by one. We add a surface to the subdivision by finding the intersections of that surface with every other surface. The intersection curves are added to the 2-D subdivisions on each surface in the same way that the 2-D subdivision was constructed in the orthographic case. After the The asp is constructed in \(\mathrm{O}\left(\mathbf{n}^{5}\right)\) time and results in \(\mathrm{O}\left(\mathbf{n}^{3}\right)\) boundaries in viewpoint space. Therefore the subdivision can be constructed in \(O\left(n^{9} \log n\right)\) time, so the time to construct the VSP is \(\mathrm{O}\left(\mathbf{n}^{9} \log \mathbf{n}\right)\). The time complexity of constructing the

## References

- Avis, Dold C. To aide noirls Coith. Go, de, pi. i the visibility of a

- Can eport EC 008 (R), M Walchecal pare in, pastion Rosearch

- Canny, J., personal communication, 1987.

- Castore, G "Solid modeling, aspect graphs, and robot vision," General Motors Conf. on Solid Modeling, 1983.

- Castore, G. and C. Crawford, "From solid model to robot vision," Proc. IEEE first Int. Conf. on Robotics, pp. 90-92, 1984.

- Chakravarty, dimensional object recognit, arac Sit 336S bot Visis, pp. 37-481982.

- Chazelle, B. and L. Guibas, "visibility and intersection problems in plane geometry," Proc. ACM Symp. on computational Geometry, 1985, pp. 135-146.

- Chazelle, B, D. Guibas, and D. T. Lee, "The power of geometric duality," BIT 25.

- Crawford Patternet grantian p. 382-384, 1985. » Proc. IEEE Conf. on Computer Vision

- "delsbrunner, H., J. O'Rourke, and R. Seidel, "Constructing arrangements of lines and hyperplanes with applications," SIAM J. Comput. 15 (2), 1986, pp. 341.

- El Gindy, a polD; AN A time 2, 1g1, pm. for computing the visibility polygon

- El Gindy, El, An simple algoith, fee coral epot, Sea of Comp poly So ence, an edge in simple polygons, McGill University, 1984.

- Fekete, G. and L. Davis, "Property spheres: a new representation for 3D object recognition," in Proc. Workshop on Computer Vision: representation and Control, pp. 192-201, 1984.

- Ikeuchi, K., "Precompiling a geometric model into an interpretation tree for object recognition in bin-picking tasks," Proc. IEEE Conf. on Robotics and Automation, 1986, pp. 321-339.

- Kender, J. and D. Freudenstein, "What is a 'degenerate' view," Proc. IEEE Conf. on Robotics and Automation, 1986, pp. 589-598.

- Koenderink, J. and A. van Doorn, "The singularities of the visual mapping," Biol. Cybernet. 24, pp. 51-59, 1976. Koendrespect and in Bio Cere 2i1 21-216, tation of solid shape with

- Korn, M. and C. Dyer, "3D multiview object representations for model-based object recognition,"Pattern Recognition 20, pp. 91-103, 1987.

- Lee, D.T., "visibility of a simple polygon," Comput. Vision, Graphics, and Image Proc. 22, 1983, pp. 207-221 Plantinga, W. H. and C. Dyer,

- Plantinga, W. H. and C. Dyer, "The aspect representation," TR 683, Computer Sciences Dept., University of Wisconsin, Madison, 1987.

- Plantinga, W. H. and C. Dyer, "Construction and display algorithms for the asp," TF 135, Computer Sciences Dept., University of Wisconsin, Madison, 1987.

- Rosenfeld, A., "Recognizing unexpected objects: a proposed approach," Int. J. Pattern Recognition and Artif. Intell. 1(1), 1987, pp. 71-84. Schneier, on; Romput: iand E rept, and hage states, p. or bigs, el robot

- Scott, R., "Graphics and prediction from models," in Proc. Image Understanding Workshop, pp. 98-106, 1984.

- Suri, S. and J. O'Rourke, "Worst-case optimal algorithms for constructing visibility polygons with holes," Proc. Second ACM Symp. on computational Geometry, 1986, pp. 14-23.

- Sutherlandac. ag Sprol, ANd Compumacku, ey chapp. 1056, 1974. "A characterization of ten hidden-

- Thorpe, C. and S. Shafer, "Correspondence in line drawings of multiple views of objects," Proc. 8th Int. Joint Conf. on Artif. Intell., pp. 959-965, 1983.

- Werman, M., S. Baugher, and A. Gualtieri, "The visual potential: one convex polygon," Tech. Rept. CAR-TR-212, Center for Automation Research, Univ. o1 Maryland, 1986
