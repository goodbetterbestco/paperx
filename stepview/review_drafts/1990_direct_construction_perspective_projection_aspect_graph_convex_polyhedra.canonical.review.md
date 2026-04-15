# Direct Construction of the Perspective Projection Aspect Graph of Convex Polyhedra

Graphof Convex Polyhedra*

Department of Computer Science and Engineering, University of South Florida, Tampa, Florida 33620
The aspect graph concept was first described by Koenderink and van Doorn as a possible mechanism in human vision and has subsequently become an active research topic in computer vision. This paper describes an algorithm for constructing the perspective projection aspect graph of convex polyhedra. In the perspective projection aspect graph, viewpoint space is modeled as all of 3D space surrounding the object. This makes the perspective projection aspect graph a more realistic representation than the orthographic projection aspect graph, in which viewpoint space is modeled by the Gaussian sphere. The algorithm uses an intermediate data structure which represents a complete parcellation of 3D space derived from the geometric definition of the object. All information necessary for identifying object aspects and corresponding viewing cells is obtained as a result of this parcellation. The resulting aspect graph structure has a node for each distinct aspect viewing cell. The upper bounds on the time complexity of the algorithm and the space complexity of the resulting data structure are O(N4), where N is the number of faces of the polyhedron. The algorithm has been implemented in C, runs on a SUN workstation, and can use PADL-2 files for its input description of objects. © 1990 Academic Press, Inc.
Department of Computer Science and Engineering, University of South Florida

## Abstract

[missing from original]

## Introduction

Koenderink and van Doorn first described a graph structure which they called the visual potential of an object [1]. Each node in this graph structure represents a different aspect of the object. An aspect is generally defined as the qualitative structure of the line drawing of an object, as seen from any point in some defined maximal, connected region of viewpoint space. For a given object, all of viewpoint space can be parcellated into such cells, so that there is a node in the aspect graph for each qualitatively different view of the object. Each arc between nodes of the graph represents a possible transition across the boundary between two cells of the parcellation. The change in aspect which occurs in crossing the boundary is termed a visual event. "Thus the visual potential represents in a concise way any visual experience an observer can obtain by looking at the object when traversing any orbit through space" [1]. Figure 1 shows the visual potential (aspect graph) of a tetrahedron. The term aspect graph has come to be used generically in the field of computer vision to refer to any graph based representation inspired by Koenderink and van Doorn's visual potential concept.

tion is assumed, then the cell of viewpoint space associated with each node of the aspect graph is just a locus of points on the Gaussian sphere. If perspective projection is assumed, then the cell of viewing space associated with each node is some volume of 3D space. In general, the perspective projection aspect graph has a greater node complexity than the orthographic projection aspect graph, because of the higher dimension of the viewpoint space. Some of the views of an object represented in a perspective projection aspect graph are not represented in an orthographic projection aspect graph. algorithms to construct the perspective projection aspect graph naturally have greater time and space complexity than algorithms to construct the orthographic projection aspect graph.

algorithms to directly calculate the object-specific partition of viewpoint space under the assumption of perspective projection have also been developed. Werman et al. [14] described a solution for the 2D convex case (essentially a convex polygon in the plane). Stewman and Bowyer first described an algorithm for convex, trihedral polyhedra [16] and then for general convex polyhedra [17]. Watts [18] and Plantinga and Dyer [15] described different approaches to the problem for convex

Within the class of orthographic projection aspect graphs, another important distinction is whether the viewing sphere is initially partitioned in a quasi-uniform manner independent of object geometry, or whether an object-specific partition is calculated directly from the geometry of the object. The approach of using an initial quasi-uniform partition has the advantage that it can be applied to objects of any geometry, but has the disadvantage that the accuracy of the representation is limited by the fineness of the tessellation. This approach has been employed by a large number of researchers, and incorporated into experimental vision systems [3-5, 8-13]. The approach of directly calculating an object specific partition of the viewing sphere has the advantage of greater accuracy, but has the disadvantage that algorithms are not (yet) known for general curved objects (but see (24, 25]). algorithms to directly calculate the object-specific partition of the viewing sphere have been described for 2.5D "prismatic" objects [2], for convex polyhedra [6-9, 14], for general polyhedra [6-7] and for solids of revolution [24]. To our knowledge, none of these algorithms has yet been implemented and incorporated into an object recognition system.

polyhedra. More recently, Stewman and Bowyer [19] and Plantinga and Dyer [15] outlined approaches for nonconvex polyhedra based on Edelsbrunner et al's [20] algorithm for constructing the geometric incidence lattice for an arrangement of planes. This paper gives an updated description of the first algorithm developed to construct the aspect graph of convex polyhedral objects [17]. To our knowledge, this is the only algorithm for the perspective projection aspect graph which has been implemented and used in object recognition experiments (21].

We follow the convention that an arc between nodes of the graph represents a visual event involving a change in visibility of a single face of the object. The reasoning behind this convention is as follows. Two viewing cells have either (1) no common boundary element, (2) a single point as the only common boundary element, (3) a single line segment or half-line as the only common boundary element, or (4) a single 2D area as the only common boundary element. With the convention we follow, only viewing cells which share a 2D boundary segment are connected by arcs in the aspect graph. This is appropriate if it is considered that it is impossible for a finite size viewer to transition exactly across a point or a line. Our convention is also consistent with Koenderink and van Doorn's original depiction of the aspect graph of a tetrahedron, but it is not the only reasonable interpretation of what an are should represent (2, 5, 6].

The algorithm directly calculates the perspective projection aspect graph of a convex polyhedron from its boundary surface description. Each node of the graph has attributes defining the corresponding aspect of the object and the 3D cell of space from which the aspect is seen. Since we are dealing only with convex polyhedra and no self-occlusions occur for such objects, our definition of an aspect and a viewing cell can be quite simple. Each individual aspect can be completely determined by the set of visible faces of the object. Each individual viewing cell is the set of all viewpoints from which the set of visible faces is the same. For non-convex polyhedra or curved-surface objects, the definitions of aspect and viewing cell would be correspondingly more complex.

Figure 2 depicts the boundary surface description of a truncated wedge and the corresponding aspect graph created by our algorithm. This example object is used to illustrate much of the following discussion.

## 2 ASPECT GRAPH CONSTRUCTION ALGORITHM

The algorithm operates in two major stages. In the first stage, an intermediate data structure is created which completely summarizes the parcellation of the viewing space about the object. This data structure is referred to as the parcellation graph. In the second stage, another intermediate data structure, the evaluation matrix, is processed to construct identification numbers for the viewing cells, which exist for a given object, and to determine which cells are linked by visual events.

### 2.A Assumptions and Constraints

A boundary surface representation is used to introduce each new object into the knowledge base of the recognition system. Figure 3 illustrates the form of the boundary surface representation; each object is specified by a sct of faces and each face is a planar polygon defined by a list of vertices given in counterclockwise order as they would appear from outside of the object.

• - object model-finite cell F== Front R == Right L == Left B == Back T == Top b == bottom

- (a) A truncated wedge and its six faces

The origin of the model coordinate system is assumed to be inside the object and not to lie in any plane in which a face of the object lies. If planar equations are based on outward-directed normals, evaluation of the equations using point coordinates will result in a value greater than 0 if the point lies to the outside of the plane, equal to 0 if the point lies on the plane, and less than 0 if the point lies to the inside of the plane. Note that a viewpoint may lie to the inside of a given plane and still be outside the object. However, a viewpoint must lie to the outside of the plane in which a face of the object lies in order for that face to be visible. (This is true only for convex polyhedra, where exactly one face of the object lies in a given plane and "inside" and "outside" are unambiguous.)

### 2.B Cell Numbering Conventions

For a convex polyhedron with \(N\) faces, there are \(N\) planes involved in the parcellation of viewpoint space. There are \(2^{N}\) possible definitions for a cell of viewpoint space in terms of its inside/outside relation to each of the \(N\) planes. We

![Figure 3. For simplicity, the parcellation graph is shown without auxiliary points.](/Users/evanthayer/Projects/stepview/docs/1990_direct_construction_perspective_projection_aspect_graph_convex_polyhedra/figures/figure-3-2-p008.png)

*Figure 3. For simplicity, the parcellation graph is shown without auxiliary points.: For simplicity, the parcellation graph is shown without auxiliary points.*

assign each possible cell definition an \(N\)-bit identification number, where each bit position corresponds to one of the \(N\) planes. A bit value of 1 means the cell is located outside of the associated plane, and a bit value of 0 means the cell is located inside of the associated plane. The existence of a cell defined by a particular one of the \(2^{N}\) possible identification numbers can be verified by finding a volume of viewpoint space which satisfies all the relationships indicated by the bit values. The cell numbers also permit easy determination of cell adjacencies (arcs between nodes of the graph) following the convention described in Section 1. Two cells are adjacent if they have identification numbers which differ in exactly one bit position, and the boundary shared by the two cells lies in the corresponding plane.

### 2.C Parcellation Graph Creation

As mentioned previously, the first step in creating the aspect graph is to generate the intermediate parcellation graph data structure. The parcellation graph is a three-level bidirected graph which summarizes the parcellation of space by the \(N\) planes in which faces of the object lie. At the graph's top level are \(N\) nodes, one for each plane. These planes will be referred to as the bounding planes of the object. At the second level of the parcellation graph are nodes for all of the lines of intersection between the bounding planes. Each line is linked to its defining planes. At the graph's third level are nodes for all of the points which result from intersections of lines in the second level. Each point is linked to its defining lines. The parcellation graph of an object contains all planes, lines, and points involved in the parcellation of viewpoint space. The lines and points corresponding to edges and vertices which are part of the object boundary generally form only a subset of the lines and points in the parcellation. The parcellation graph will contain additional lines and points whenever there are viewing cells of finite extent (as is the case with our example object). A straightforward approach is taken to construct the parcellation graph. first, nodes are allocated for all the bounding planes of the object. Each of these nodes is attributed with the planar equation. The first step in this process is to calculate the outward-directed surface normal for the plane. This is accomplished by taking the cross product between the direction vectors associated with the first and second line segments along the boundary of each face. Given \(V_{0}=\left[\begin{array}{lll}x_{0} & y_{0} & z_{0}\end{array}\right]\), \(V_{1}=\left[x_{1} y_{1} z_{1}\right]\), and \(V_{2}=\left[\begin{array}{lll}x_{2} & y_{2} & z_{2}\end{array}\right]\) as the first three vertices in the boundary list for a face, the surface normal for the plane containing the face is given by Eq. (1),

$$
a i+b j+c k=\left|\begin{array}{ccc} i & j & k \tag{1}\\ \left(x_{1}-x_{0}\right) & \left(y_{1}-y_{0}\right) & \left(z_{1}-z_{0}\right) \\ \left(x_{2}-x_{1}\right) & \left(y_{2}-y_{1}\right) & \left(z_{2}-z_{1}\right) \end{array}\right| .
$$

The resulting surface normal will always be outward-directed, since the polygon bounding the face is convex and the vertices are assumed to be listed in counterclockwise order as the face appears from outside the object. Each surface normal is stored as a vector of the form [a b c].

where \(a, b\), and \(c\) are the components of the normal vector obtained by using Eq. (1). A more useful form of the equation is

$$
\begin{equation*} a x+b y+c z+d=0 \tag{3} \end{equation*}
$$

$$
\begin{equation*} d=-a x_{0}-b y_{0}-c z_{0} \tag{4} \end{equation*}
$$

Each planar equation is stored as a vector of the form [a b c d]. Table 1 contains a summary of the planar equations for the bounding planes of the truncated wedge in Fig. 3. The lines of intersection resulting from the bounding planes occupy the nodes on the second level of the parcellation graph. Each pair of planes, \(F_{i}\) and \(F_{j}\) such that \(i \neq j\), forms a linear system \(\left[F_{i} F_{j}\right]^{\mathrm{T}}\) that has either a line of intersection as its solution or has no solution. A

The general form of the planar equation is where

$$
\begin{equation*} a\left(x-x_{0}\right)+b\left(y-y_{0}\right)+c\left(z-z_{0}\right)=0 \tag{2} \end{equation*}
$$

Gauss-Jordan reduction is used to solve each linear system. If a solution exists, the coefficients of the parametric form of the line equation are stored in the form [a b c de f], where

$$
\begin{align*} & x=a t+d \\ & y=b t+e, \text { and } \tag{5}\\ & z=c t+f \end{align*}
$$

Table 2 contains the coefficients of the parametric line equations for all lines of intersection in the parcellation graph of the truncated wedge. These are determined from the plane equations listed in Table 1. Points resulting from intersections of three or more of the bounding planes fill the lowest level of the parcellation graph. These points of intersection are found by determining where lines of intersection cross in the parcellation. The point \(P=[x y_{z}]\) is the point of intersection between a pair of lines \(L_{i}\) and \(L_{j}\) for \(i \neq j\) if

$$
\begin{align*} a_{1} t+d_{1} & =a_{2} s+d_{2} \\ b_{1} t+e_{1} & =b_{2} s+e_{2} \tag{7}\\ c_{1} t+f_{1} & =c_{2} s+f_{2} \end{align*}
$$

$$
\left|\begin{array}{cc:c} a_{1} & -a_{2} & \left(d_{2}-d_{1}\right) \tag{8}\\ b_{1} & -b_{2} & \left(e_{2}-e_{1}\right) \\ c_{1} & -c_{2} & \left(f_{2}-f_{1}\right) \end{array}\right|
$$

into the parcellation graph with the original planes as mentioned previously. Fig. 3. For simplicity, the parcellation graph is shown without auxiliary points.

![Figure 3. For simplicity, the parcellation graph is shown without auxiliary points.](/Users/evanthayer/Projects/stepview/docs/1990_direct_construction_perspective_projection_aspect_graph_convex_polyhedra/figures/figure-3-2-p008.png)

*Figure 3. For simplicity, the parcellation graph is shown without auxiliary points.: For simplicity, the parcellation graph is shown without auxiliary points.*

### 2.D Selection of Test Points

The next step aids in the determination of which cell identification numbers are valid for a given object. A cell number is valid if and only if some volume of viewpoint space exists which satisfies the cell number's specified relationships to the N planes. Each valid cell number corresponds to a node in the aspect graph of the object.

As long as the object is of finite size and exists as a closed solid there must be at least one intersection point in the parcellation which lies on the boundary of each cell. This suggests that the points listed in the parcellation graph can be used to identify valid cell numbers. Validating cell numbers by using the boundary points requires that the cell boundary be treated, in essence, as part of its interior. In this can be written as relaxed interpretation of the cell numbers, a bit value of 1 indicates a point to the greater than three, this results in the identification of cells which do not actually exist, because in these cases space cannot be physically divided into 2M volumes sharing a common boundary point. Objects such as the example truncated wedge (Fig. 3) do not encounter this problem, since all the intersection points are defined

![FIG. 4. Parcellation graph for the truncated wedge.](/Users/evanthayer/Projects/stepview/docs/1990_direct_construction_perspective_projection_aspect_graph_convex_polyhedra/figures/figure-4-p010.png)

*FIG. 4. Parcellation graph for the truncated wedge.: Parcellation graph for the truncated wedge.*

by exactly three planes. However, Fig. 5 depicts an object for which the problem does arise. The top point of this four-sided pyramid represents the intersection of four planes. Sixteen cells would be validated by this boundary point, even though only 14 volumes of space are defined by the intersection of the four planes. (The two nonexistent viewing cells that would be validated by the point are ones in which one opposing pair of the four sides is visible but the other pair of sides is not.)

A practical solution is found in the following way. The invalid cells are degenerate in the sense that their boundaries do not enclose a volume of space which satisfies the relationships specified by the cell number. Another way of saying this is that they can be viewed as cells which have boundaries completely comprised of dangling lines and planes. Dangling lines touch a cell boundary at only a single point. Dangling planes touch a cell boundary at a single point or along a single line. The simplest 3D volume of space has a boundary comprised of three planes which meet at one point. It has only one real 3D corner, and thus only one intersection point from the parcellation graph will satisfy the constraints imposed

![FiG. 5. A four-sided pyramid.](/Users/evanthayer/Projects/stepview/docs/1990_direct_construction_perspective_projection_aspect_graph_convex_polyhedra/figures/figure-5-p010.png)

*FiG. 5. A four-sided pyramid.: A four-sided pyramid.*

by the cell's identification number. If auxiliary points are added to the parcellation graph, one along each infinite extension of each line in the parcellation, the simplest region will be the same as that described above except that there will be four test points which satisfy the relaxed relationships in the cell number. All degenerate cells will have fewer than four points which satisfy the same relationships and thus can be easily identified and eliminated. Thus, the lowest level of the parcellation graph is augmented with the auxiliary points in order to obtain a sufficient set of test points for the construction of valid cell numbers. Auxiliary points are found by keeping track of the maximum ( \(t_{\text {max }}\) ) and mini mum ( \(t_{\text {min }}\) ) values of the parameter \(t\) for points of intersection along each line. Once all of the points of intersection have been entered into the parcellation graph, two extra points are found for each line by evaluating Eq. (5) for each line with the parameter \(t\) set at \(t_{\text {max }}+1\) and \(t_{\text {min }}-1\).

### 2.E Creation of the Evaluation Matrix

The evaluation matrix is created to allow more efficient determination of valid cell numbers. During this process, the planar equations for all of the bounding planes of the object must be evaluated with the coordinates of each of the boundary points in the parcellation. Repeated evaluations are avoided by creating a matrix to hold all of the values. This evaluation matrix is \(M\) rows by \(N\) columns, where \(M\) is the total number of points from the bottom of the parcellation graph (intersection points and auxiliary points), and \(N\) is the number of bounding planes for the object. The value of each matrix entry \(E_{i, j}\) is determined by evaluating the planar equation indicated by the column with the point coordinates indicated by the row. See Eq. (9):

$$
\begin{equation*} E_{i, j}=a_{j} x_{i}+b_{j} y_{i}+c_{j} z_{i}+d_{j} \tag{9} \end{equation*}
$$

If the resulting value \(E_{i, j}\) is negative, then the boundary point \(P_{i}\) lies to the inside of the plane \(F_{j}\). If \(E_{i, j}\) is positive, then \(P_{i}\) lies to the outside of \(F_{j}\). If \(E_{i, j}\) is zero, then \(P_{i}\) lies on \(F_{j}\). Table 4 lists values in the evaluation matrix for the truncated wedge in Fig. 3. Rows for both intersection points and auxiliary points appear in the evaluation matrix.

### 2.F Generation of Valid Cell Identification Numbers

Determination of the nodes of the aspect graph is reduced to a process of finding that subset of the \(2^{\mathbf{N}}\) possible cell identification numbers for which each number in the subset has at least four points in the parcellation graph which satisfy the relationships specified by that number. Using the evaluation matrix, an efficient algorithm can be devised to construct, one bit at a time, only those valid cell numbers. This computation is most easily explained as a recursive procedure. At each stage, the recursive procedure takes a partial cell number and a set of rows from the evaluation matrix as its input. It examines the column which corresponds to the depth of the recursive call and splits the input row set into two possibly overlapping subsets. The procedure then appends \(a_{1}\) or \(a_{0}\) to the partial cell number and makes a recursive call for each subset which still has at least four members. The pattern of recursive calls takes the form of a binary tree \(\mathbf{N}\) levels deep. The leaves of the tree represent valid cell numbers. The number of calls cannot become exponential because, at certain nodes in the tree, entire subtrees are left undeveloped. (See the complexity analysis in Section 4.) The specifics of constructing the set of valid cell numbers are as follows. At the first (root) level call to the procedure there is a null partial cell number and the input row set contains all of the rows in the evaluation matrix. The values in the first column of every row are examined. Rows with a non-negative value in the first column are grouped together in a row set that indicates the existence of cell numbers with \(a_{1}\) in the first bit position. All cells whose cell numbers have \(a_{1}\) in the first bit position are located on the side of the first bounding plane away from the origin. If the row set has at least four members, then a partial cell number is created having \(a_{1}\) in the first bit position and a recursive call is made. Rows with a non-positive value in the first column position are grouped together in a row set that indicates the existence of cell numbers with \(a_{0}\) in the first bit position. All cells whose cell numbers have \(a_{0}\) in the first bit position are located on the same side of the first bounding plane as the origin. If this row set has at least four members, then a partial cell number is created having \(a_{0}\) in the first bit position and a recursive call is made. Whenever a row set has less than four members, then it cannot represent the boundary of a valid viewing cell, and so no further development of cell numbers from the current partial cell number is required. Each recursive call at the second level of the tree splits its input row sets based on the values located in the second column of the input rows. If a row set resulting from this second splitting has at least four members, a recursive call is made with one of these partial cell numbers \((00 \ldots 01 \ldots 10 \ldots 11 \ldots)\). The recursive calls continue to a maximum depth of \(N\) calls. When an \(N\) th level call is made, one last split of the row set occurs and a complete cell number is returned for each row set that survives. Each final row set indicates all of the vertices on a cell boundary and can be used to recover that cell's boundary from the parcellation graph. Figure 6 illustrates the pattern of recursive calls required to determine the valid cell numbers for the truncated wedge. It is interesting to note that the pattern would be different if the original set of bounding planes had been listed in a different order. However, the same set of cell numbers would be found.

### 2.G Recovery of Cell Boundary Descriptions

The set of points known to lie on the boundary of a cell can be used in the following manner to determine the boundary of that cell. Each cell boundary is represented by a subgraph of the parcellation graph. If a point exists on the boundary of a cell, every line in the parcellation graph that passes through that point also touches that boundary. These lines are easily identified, since each point is linked to all such lines in the parcellation graph. If a line touches the boundary of the cell at only a single point (it is linked to only one of the points in the row set for the cell) then it dangles and is dropped from the boundary subgraph. Each line is linked to its defining planes so they are easily found. If a plane is linked to only one line in the subgraph, then it dangles and is dropped from the subgraph. The subgraph comprised of points, lines, and planes identified in this manner forms the exact boundary of the cell.

### 2.H Creation of an Explicit Aspect Graph Structure

Creation of an explicit aspect graph structure is a relatively simple task. first, for each cell number generated, a node is allocated and given the cell number and the cell boundary description as attributes. The 1 bits in the cell number indicate the object faces which are visible in the aspect. The cell boundary description was determined explicitly in the preceding process. Establishing links between nodes where a visual event is defined by the appearance or disappearance of a single face can be done in any of several ways. Perhaps the most elegant alternative is to generate the links between nodes at the same time that the cell numbers are generated. first, note that there is a link between nodes of the aspect graph if and only if their cell numbers differ in exactly one bit

![FIG. 6. Depiction of pattern of cell number generation. (Points of intersection in the row sets input](/Users/evanthayer/Projects/stepview/docs/1990_direct_construction_perspective_projection_aspect_graph_convex_polyhedra/figures/figure-6-p014.png)

*FIG. 6. Depiction of pattern of cell number generation. (Points of intersection in the row sets input: Depiction of pattern of cell number generation. (Points of intersection in the row sets input to the first three levels of calls are shown. Auxiliary points in these row sets are not shown).*

Thus, two nodes of the aspect graph are to be connected if and only if the paths through the tree differ at exactly one level. All such connections can be found as follows.

Beginning with the root node, whenever the processing of a node results in both a 1-descendent and a 0-descendent, then these two siblings are connected by a visual event link. After the splitting to generate the 1-and 0-descendents, the 1-descendent is expanded and then the 0-descendent is expanded. When two nodes connected by a visual event link are expanded, the 1-descendents of the two nodes (if both have a 1-descendent) and the 0-descendents of the two nodes (if both have a 0-descendent) each inherit the visual event link. In this way, the visual event links are inherited down similar paths of the tree to all pairs of cells connected by a visual event.

## 3 ANALYSIS OF COMPLEXITY

This section presents an analysis of the complexity of the data structure sizes and the execution time of the algorithm. The analysis is simplified by using one of the results of Edelsbrunner et al. [20]. Edelsbrunner describes an algorithm for constructing the geometric incidence lattice representing the arrangement of a set of hyperplanes. For convex polyhedra, the arrangement of the \(\mathbf{N}\) planes in which the faces of the object lie is similar to the parcellation of space discussed in this paper. The aspect graph differs from the geometric incidence lattice, in the case of convex polyhedra, in that it distinguishes one cell of the parcellation as representing the object and it attributes each other cell with a list of the object faces visible from viewpoints in that cell. (In the case of non-convex polyhedra, the aspect graph further differs due to planes and quadric surfaces which are not part of the object boundary but enter into the parcellation of space, and due to the object itself occupying more than one cell of the parcellation.) The primary result of Edelsbrunner [20] which is of interest here deals with the number of \(k\)-faces which can occur in an arrangement of \(\mathbf{N}\) planes. Following Lemma 2.1 of [20], the maximum number of 3-faces (3D cells in the parcellation) formed by an arrangement of \(\mathbf{N}\) planes is

$$
1 / 6 *\left(\mathbf{N}^{3}+5^{*} \mathbf{N}\right)+1
$$

one of which (in the case of convex polyhedra) would correspond to the object itself. (This result can be found in other ways [22-23], and related questions have long been popular in mathematical games.) This upper bound is achieved when the arrangement is simple; that is, every pair of planes intersects in a distinct line and every triplet of planes intersects in a distinct point. It is easy to see that an object of any number of faces can be constructed to meet this condition. Simply begin with a tetrahedron, and successively shave off corners such that each new face creates three new object vertices and none of the intersection points in the current parcellation lie in the same plane as the new face. (For a highly degenerate class of polyhedra, such as N-sided approximations to a cylinder, the number of cells in the parcellation of space may be \(O(N2)\) [15].)

### 3.A Space Complexity

It is easy to see that the upper bound on the space complexity of the parcellation graph data structure is \(\Theta\left(\mathbf{N}^{3}\right)\), reflecting \(\mathbf{N}\) nodes for planes in which faces of the object lie, \(\Theta\left(\mathbf{N}^{2}\right)\) nodes for lines of intersection defined by pairs of planes, \(\Theta\left(\mathbf{N}^{3}\right)\) nodes for points defined by triplets of planes, and a constant number of arcs touching a node of each type. (The number of arcs touching a node of each type can be increased if the arrangement is not simple, but there will be a correspond ing decrease in the number of nodes.) It is also easy to see that the upper bound on the space complexity of the evaluation matrix is \(\Theta\left(\mathbf{N}^{4}\right)\), reflecting \(\mathbf{N}\) columns for the planes in which faces of the object lie and \(\Theta\left(\mathbf{N}^{3}\right)\) rows for the points of intersection.

Lastly, the upper bound on the node complexity of the aspect graph itself, with one node for each cell of the parcellation, is clearly \(\Theta\left(\mathbf{N}^{3}\right)\). If each node is

The tree structure created in generating the viewing cell numbers is also \(\Theta\left(\mathbf{N}^{4}\right)\), the tree being \(\mathbf{N}\) levels deep and having a maximum of \(\Theta\left(\mathbf{N}^{3}\right)\) nodes in a level.

### 3.B Time Complexity

The time complexity can be determined by analyzing the serial stages of the matrix, processing of the evaluation matrix to obtain the cell numbers, and

The upper bound on the time complexity of creating the parcellation graph is \(\Theta\left(\mathbf{N}^{4}\right)\), representing the solution of \(\Theta\left(\mathbf{N}^{2}\right)\) pairs of plane equations to find lines of intersection, followed by the solution of \(\Theta\left(\mathbf{N}^{4}\right)\) pairs of line equations to find the coordinates of points of intersection. The links between plane nodes and line nodes and between line nodes and point nodes can be done directly as the solutions are found. (The points of intersection could be found in \(\Theta\left(\mathbf{N}^{3}\right)\) time by considering triplets of planes, but by finding the points through line intersections we can easily keep track of the outermost intersection point on each line and generate auxiliary points outside these points. This does not affect the overall complexity of the algorithm, since there are other \(\Theta\left(\mathbf{N}^{4}\right)\) stages which cannot be reduced.)

The time complexity can be determined by analyzing the serial stages of the algorithm: construction of the parcellation graph, construction of the evaluation matrix, processing of the evaluation matrix to obtain the cell numbers, and

The upper bound on the time complexity of creating the evaluation matrix is \(\Theta\left(\mathbf{N}^{4}\right)\), representing the solution of each of \(\mathbf{N}\) plane equations for each of \(\Theta\left(\mathbf{N}^{3}\right)\) points. The upper bound on the time complexity of processing the evaluation matrix to obtain the valid cell numbers is also \(\Theta\left(\mathbf{N}^{4}\right)\). To see this, note that the evaluation matrix is processed in \(\mathbf{N}\) stages, one for each plane equation. Also note that the first stage involves \(\Theta\left(\mathbf{N}^{3}\right)\) examinations of evaluation matrix entries in order to split them into two (overlapping) groups. Successive stages examine each entry in each group for splitting into new subgroups. The number of groups will grow to \(\Theta\left(\mathbf{N}^{3}\right)\) by the end of the processing, one for each node of the aspect graph. However, since each intersection point is on the boundary of eight cells in the parcellation, it can never appear in more than eight groups in any stage of the splitting, and so the total number of entries examined at each stage is always \(\Theta\left(\mathbf{N}^{3}\right)\). (This is for a simple arrangement; if the arrangement is not simple, then a vertex can be on the boundary of more than eight cells, but there will be fewer than the maximum possible number of cells.) Creation of the explicit aspect graph structure is also an \(\Theta\left(\mathbf{N}^{4}\right)\) step. Finding the exact cell boundary by following each of the points used to validate the cell back through the parcellation graph to find the lines and planes to which it is linked is \(\Theta\left(\mathbf{N}^{3}\right)\), reflecting \(\Theta\left(\mathbf{N}^{3}\right)\) total points used in validating the cells, and each point having links to three lines and each of the lines having links to two planes. However, establishing links between nodes separated by a visual event takes \(\Theta\left(\mathbf{N}^{4}\right)\) time. Again using Lemma 2.1 of [20], the total number of 2-faces (2D faces on the boundary of a 3D cell) in the parcellation is \(\Theta\left(\mathbf{N}^{3}\right)\). Since each 2D face on the boundary of a cell corresponds to a visual event, there are clearly \(\Theta\left(\mathbf{N}^{3}\right)\) visual event links between leaves of the tree (arcs between nodes of the aspect graph), and these links are propagated down \(\mathbf{N}\) levels of the tree from the root to the leaves.

## 4 CONCLUSIONS

An algorithm for directly calculating the exact perspective projection aspect graph of convex polyhedra from their boundary surface description has been presented The algorithm has an upper bound of \(\Theta\left(\mathbf{N}^{4}\right)\) for time complexity of execution and space complexity of the resulting data structure, where \(\mathbf{N}\) is the number of faces of the convex polyhedron. The algorithm has been implemented in C and runs on a SUN workstation. It has been used to generate object representations for use in a prototype object recognition system developed in our lab [21]. There is evidence that many of the concepts used in the algorithm are also applicable to non-convex polyhedra [19]. Our plans for continued research in this area include (1) development and implementation of algorithms for determining the "equivalent" nodes of an aspect graph, (2) development of a method of attaching relative probabilities to the nodes of an aspect graph, (3) development and implementation of algorithms to handle non-convex polyhedra and curved-surface objects, and (4) further exploration of the use of aspect graphs in object recognition.

## Acknowledgments

The authors thank Louise Stark and David Eggert for many valuable discussions.

## References

- J. J. Koenderink and A. J. van Doorn, The internal representation of solid shape with respect to vision, Biol. Cybern. 32, 1979, 211-216.

- C. Goad, Automatic construction of special purpose programs for hidden surface elimination, Comput. Graphics 16, No. 3, 1982, 167-178.

- G. M. Castore, Solid modeling, aspect graphs, and robot vision, in Solid Modeling by Computers: From Theory to Applications (Pickett and Boyse, Eds.) pp. 277-292, 1984, Plenum, New York.

- C. Goad, Special purpose automatic programming for 3-D model based vision, in 1983 DARPA Image Understanding Workshop, pp. 94-104.

- H. Plantinga and C. R. Dyer, An algorithm for constructing the aspect graph, in 27th IEEE Symposium on Foundations of Computer Science, 1986, pp. 123-131.

- M. R. Korn and C. R. Dyer, 3-D multiview object representations for model-based object recognition, Pattern Recognit. 20, No. 1, 1987, 91-103.

- Z. Gigus and J. Malik, Computing the aspect graph for line drawings of polyhedral objects, in IEEE 1988 Conference on Robotics and Automation, pp. 1560-1566; also see IEEE 1988 Conference on Computer Vision and Pattern Recognition, pp. 654-661.

- K. Ikeuchi, Precompiling a geometrical model into an interpretation tree for object recognition in bin-picking tasks, in 1987 DARPA Image Understanding Workshop, pp. 321-339.

- K. Ikeuchi, Generating an interpretation tree from a CAD model for 3D-object recognition in bin-picking tasks, Int. J. Comput. Vision, 1987, 145-165.

- J. B. Burns and L. J. Kitchen, Recognition in 2D images of 3D objects from large model bases using prediction hierarchies, in 1987 Int. Joint Conf. Artif. Intell., pp. 763-766.

- M. Hebert and T. Kanade, The 3-D profile method for object recognition, in IEEE 1985 Conference on Computer Vision and Pattern Recognition, pp. 458-463.

- L. Shapiro, A CAD-model-based system for object localization, SPIE No. 938: Digital and Optical Shape representation and Pattern Recognition, 1988, pp. 408-418.

- T. Henderson and C. Hansen, CAGD-based computer vision, SPIE No. 938: Digital and Optical Shape representation and Pattern Recognition, 1988, pp. 428-435.

- J. A. Gualtieri, S. Baugher, and M. Werman, The visual potential: One convex polygon, Comput. Vision Graphics Image Process. 46, No. 1, 1989, 96-130; also see CS-TR-1690, Center for Automation Research, University of Maryland, 1986.

- H. Plantinga and C. Dyer, visibility, Occlusion and the Aspect Graph, CS-TR-736, University of Wisconsin-Madison, 1987.

- J. Stewman and K. Bowyer, Implementing viewing spheres: Automatic construction of aspect graphs for planar-faced, convex objects, SPIE No. 786: Applications of Artificial Intelligence V, 1987, pp. 526-532.

- J. Stewman and K. Bowyer, Aspect graphs for convex, planar-face objects, IEEE 1987 Workshop on Computer Vision, pp. 123-130.

- N. Watts, Calculating the principal views of a polyhedron, in 1988 International Conference on Pattern Recognition, pp. 316-322; also see CS-TR-234, University of Rochester, 1987.

- J. Stewman and K. Bowyer, Constructing the perspective projection aspect graph of non-convex polyhedra, in IEEE 1988 International Conference on Computer Vision, pp. 494-500.

- H. Edelsbrunner, J. O'Rourke, and R. Seidel, Constructing arrangements of lines and hyperplanes with applications, in IEEE 1983 Symposium on Foundations of Computer Science, pp. 83-91.

- K. Miller, An Introduction to the Calculus of Finite Differences and Difference Equations, Holt, New York, 1960.

- L. Stark, D. Eggert, and K. Bowyer, Aspect graphs and nonlinear optimization in 3-D object recognition, in IEEE 1988 International Conference on Computer Vision, pp. 501-507.

- L. Milne-Thompson, The Calculus of Finite Differences, MacMillan, New York, 1951.

- J. Ponce and D. J. Kriegman, On recognizing and positioning curved 3D objects from image contours, in 1989 DARPA Image Understanding Workshop, pp. 461-470.

- K. W. Bowyer, D. Eggert, J. Stewman, and L. Stark, Developing the aspect graph representation for use in image understanding, in 1989 DARPA Image Understanding Workshop, pp. 831-849.
