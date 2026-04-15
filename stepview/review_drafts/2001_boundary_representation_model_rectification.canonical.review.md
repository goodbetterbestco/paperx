# 2001 boundary representation model rectification

G. Shen, T. Sakkalis, N. M. Patrikalakis

Massachusetts Institute of Technology, Cambridge, Massachusetts 02139-4307
Massachusetts Institute of Technology, Cambridge, Massachusetts 02139-4307

## Abstract

Defects in boundary representation models often lead to system errors in modeling software and associated applications. This paper analyzes the model rectification problem of manifold boundary models, and argues that a rectify-by-reconstruction approach is needed in order to reach the global optimal solution. The restricted face boundary reconstruction problem is shown to be NP-hard. Based on this, the solid boundary reconstruction problem is also shown to be NP-hard. © 2001 Academic Press Key Words: boundary reconstruction; NP-hardness; CAD model defects; robustness; data exchange. A-

## Introduction

Model representations of products enable man-machine and machine-machine communication. With rules set by representation schemes, models can be realized as physical biguities arise. This is especially true for manifold boundary representation (B-rep) as conditions for validity of manifold B-rep models [5]. Defects in B-rep models are those defects are topological and geometric errors, and visually appear as gaps, dangling faces, artifacts. However, such realization often fails whenever models contradict rules and amits validity is not self-guaranteed [1-4]. In an earlier paper, we have identified sufficient representational features that do not conform to constraints set by modeling schemes. Such internal walls, and inconsistent orientations. Defects may cause failures of modeling systems and applications because operations are typically designed with the assumption of model validity. Model rectification, a process that repairs defects, is essential to the success of design and manufacturing defect-free products in an integrated CAD CAM environment. Research on model rectification has been done mainly on triangulated models, specifically, STL models for rapid prototyping. STL models represent solids using oriented triangles [6]. Defects in STL models are gaps due to missing triangles, inconsistently oriented triangles, and inappropriate intersections in the interiors of triangles. Most algorithms [7, 8] identify erroneous triangle edges, string such edges to form hole boundaries, and then fill holes with triangles. As pointed out in [7], topological ambiguities are resolved by intuitive heuristics. These algorithms [7, 8] use local topology (incidence and adjacency) to rectify defects and are successful in the majority of candidate models, but may create undesirable global topological and geometric changes. See also [9] for a critique of these methods.

Barequet and Sharir [9] developed a global gap-closing algorithm for polyhedral models, using a partial curve-matching technique. In their method, gap boundaries are discretized. Each match between any two parts of gap boundaries is given a score based on the closeness of their discrete points. They have shown that finding a consistent set of partial curve matches with maximum score, a subproblem of their repairing process, is NP-hard. Barquet and Kumar [10] developed a model repairing system using the algorithm in [9], but with a modified score that is the normalized gap area between two matched parts of gap boundaries. Visualization tools were also provided to enable the user to override unwanted modifications. The system was improved by Barequet et al. [11] in terms of efficiency, and extended to models with regular arrangement of entire NURBS surface patches. However, this extension does not handle trimmed patches with intersection curve boundaries and general B-rep models involving nonregular arrangement of surface patches.

A different type of global algorithm is based on spatial subdivision. Murali and Funkhouser [12] developed an algorithm that handles defects such as intersecting and overlapping polygons and misoriented polygons. The algorithm follows three steps: spatial subdivision, solid region identification, and model output. It first subdivides \(\mathbf{R}^{3}\) into con vex cells using planes on which polygons sit. A cell adjacency graph is then constructed. Each node is a convex cell, and each arc is a link between two cells sharing a polygon. Whether a cell is a part of the intended solid is determined by its solidity value, ranging from-1 to 1. The solidity value of a cell is computed based on how much area of the cell boundary is covered by original polygons as well as solidity values of neighboring cells. Boundary polygons of cells with positive solidity values are then output as the resulting solid boundary. A major advantage of this algorithm is that it always outputs a valid solid. One limitation is that it may mishandle missing polygons and add cells that do not belong to the model.

Hamann and Jean [13] proposed a user-assisted gap-closing method for curved boundaries using bivariate scattered data approximation techniques to approximate missing data in gap areas.

Another approach currently investigated by many researchers is the development of new geometric representations that are free of defects caused by the precision limitation of the computer [3, 14]. Two typical examples are precise representation and error-bounded representation (see [15-17]). The common characteristic of these two representations is that both use new arithmetic systems for computer representation of numbers, and the algebraic operations necessary for modeling are closed B-rep models contain topological and geometric specification of boundaries. Although rarely, topological errors could happen. Often a model has a geometric specification inconsistent with its topological specification. In such cases, it is unclear which one gives correct information about the boundary. The task of model rectification is to create a valid boundary model that is also intended by the designer. Sakkalis et al. [5] derived sufficient conditions for representational validity of ideal models. Such conditions are useful in developing defect identification and rectification methods. Krause et al. [18] proposed a methodology, which views representational validity as an application-dependent concept, for processing (verifying and repairing) CAD data, especially those received from data exchange, and developed an experimental data processor for grid generation for aerodynamic simulation. Jackson [19] developed the concept of tolerant modeling implemented in the Parasolid modeler, where each face, edge, and vertex of a B-rep model is associated with a local tolerance and these tolerances are taken into account in subsequent operations. Commercial software such as [20, 21] now repairs erroneous B-rep models interactively and or semiautomatically. Such repairing tools usually succeed in fixing local defects but leave global consistency to the users or process in an iterative manner. This paper analyzes the nature of the manifold B-rep model rectification problem, as well as the complexity of the problem. It approaches the problem as a reconstruction problem—reconstruct a valid boundary model, which is also most likely to be the intended one, using only the information in the erroneous model.

The paper is organized as follows: Section 2 discusses the nature of the rectification problem, and argues that the problem should be approached as a reconstruction problem in order to reach the global optimal solution. Section 3 first studies and formulates a lowerdimensional problem, the face reconstruction problem, and proves that it is NP-hard. Then it extends this result to the boundary reconstruction problem. Section 4 concludes the paper. The paper also includes an Appendix that provides a brief review of NP-completeness, needed in explaining this work.

## 2 PROBLEM STATEMENT

Defects must be identified before being rectified. Based on this principle, two approaches, local and global, may be explored for the development of rectification methods.

A local rectification method traverses through a representation of a model, identifies defects using the sufficient conditions derived in Sakkalis et al. [5], and rectifies defects using the same sufficient conditions, or some heuristic rules and or user assistance if ambiguities arise. Such an approach is the same as other rectification methods [7, 8, 20] except that conditions for identifying and rectifying defects may have some differences. However, a local method does not guarantee a global optimal solution. In addition, rectification of local defects may have unpredictable cascading effects on other topological and geometric entities in the model, and some defects may not be rectified without searching further. A global rectification method, on the other hand, identifies all defects once and for all. It then rectifies defects such that the resulting model is not only valid but also optimal based on some user-defined criteria. The main obstacle for developing such a method lies in the fact that a priori identification of all defects, done independently of rectification, is impossible in general. As the definition of a boundary is bottom-up in a model representation, the validity verification should proceed in the same manner. Higher dimensional entities cannot be verified if lower dimensional entities have not been rectified. Part of the reason it is so difficult to implement an identify-and-rectify approach is the necessity to maintain the consistency between topological and geometric information. It is not difficult to identify a defect, but it is hard to decide what is right or wrong, whenever there is inconsistency between topological and geometric information.

The ultimate goal of model rectification is to find the model intended by the designer but misrepresented. However, without user assistance, any solution resulting from the erroneous model is only an educated guess. It comes down to the question "What do we trust about a model that contains defects?" This is the most fundamental question we must answer before we can move any further. For example, if a B-rep model has correct topological information, while there is no appropriate geometry embedded in the underlying surfaces, what is the intended boundary? Should the topological information be modified to accommodate the geometry, or should the geometry (surfaces) be perturbed to have a boundary consistent with the topological information?

To answer such questions, we need to classify the information in a boundary representation: those initialized or selected by the designer and those induced by the system. In a solid modeling system, the only entities the designer can directly manipulate are the underlying surfaces. All others, topological information and individual topological and geometric entities, are computed by the system. For this reason, we opt to believe that surfaces are the basic information to be used in a rectification method. Another reason for such a hypothesis is that surfaces are specifically designed to fulfill certain performance requirements and functionalities, and therefore, should not be subjected to any modification without the designer's permission. In addition to the above, another piece of information that can be used in the rectification process is the genus of the intended solid boundary. Genus captures the designer's intent and can be computed using the well-known Euler's formula [22].

In this context, model rectification becomes a model reconstruction problem. An algorithm for model rectification searches for the intended boundary in the union of all the surfaces, and rebuilds all necessary topological and geometric entities. However, there may exist many potential solid boundaries, or none at all, resulting from the surfaces. Without additional information, it would be difficult to make a choice. Since an erroneous model in a neutral format (e.g., STEP [23]) is computed with reasonable precision in its native system, the information in the model could help clarify such ambiguities, although it should be used with caution. Roughly speaking, a desirable solution is a model that describes a boundary somewhere "near" the object described by the original model, both topologically and geometrically.

A typical data structure for B-rep models consists of a topological structure and a geometric representation. For a simplified version, see Fig. 1. The topological structure, shaded

![FIG. 1. Data structure for B-rep models.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-1-p004.png)

*FIG. 1. Data structure for B-rep models.: Data structure for B-rep models.*

Loop Edge in Fig. 1, is a graph that describes adjacency and incidence relations \({ }^{1}\) (represented by arcs) between topological entities (represented by nodes). In typical implementations topological relations more detailed than those implied in Fig. 1 (e.g., adjacency relations between a face and all its neighboring faces) are explicitly stored. The geometric representation includes points, curve, and surface equations, which are associated with appropriate topological en tities. A model, thus, is an instance of the data structure, and is valid if it describes a solid boundary. In addition, a face is valid if it describes a set homeomorphic to a closed disk minus \(k\) mutually disjoint open disks, and has no handles. Also, see [5] for validity of other topological nodes. Let \(m_{o}\) be a model with topological structure \(G\left(m_{o}\right).^{2} G\left(m_{o}\right)\) is valid if it is possible to assign each topological entity (face, edge, vertex) a set of the corresponding dimension (surface, curve, point) whose interior is a manifold, such that the union of these manifolds bounds a solid. That is, if \(G\left(m_{o}\right)\) is valid, there exists a nonempty set

$$
\begin{equation*} \mathcal{M}=\left\{m \mid m \text { is a valid model and has topological structure } G\left(m_{o}\right)\right\} . \tag{1} \end{equation*}
$$

For simplicity, in the following analysis, we assume that models have only one shell. It will be clear at the end of this paper that the same result applies to models with multiple shells. With this assumption, for any \(m_{1}, m_{2} \in \mathcal{M}, M_{1}\) is homeomorphic to \(M_{2}\). Therefore, in case that the geometric representation of \(m_{o}\) is inconsistent with \(G\left(m_{o}\right)\), if a reconstructed model \(m_{n}\) has topological structure \(G\left(m_{o}\right), m_{n}\) is topologically equivalent to the model incorporating the design intent. If \(G\left(m_{n}\right)\) is different from \(G\left(m_{o}\right)\), the topological equivalence between \(m_{n}\) and \(m_{o}\) can be imposed by requiring that the genus of \(\partial M_{n}\) is equal to that of \(\partial M\), where model \(m \in \mathcal{M}\). We simply denote this by \(g\left(m_{n}\right)=g\left(m_{0}\right)\), because both genuses can be computed by applying Euler's formula to \(G\left(m_{n}\right)\) and \(G\left(m_{o}\right)\), respectively.

Geometrically, two objects are close to each other if each one is in a neighborhood of the other. Some form of distance function could be used as a measure for this purpose, either the maximum distance or a well-defined average distance. An alternative, arguably more suitable for boundary rectification, is the boundary area change before and after rectification, because both the rectified and the original models use the same set of underlying surfaces. A correspondence can be established between a rectified face and an old face if they both have the same underlying surface, and the area difference between them measures the geometric change. No matter what measure is used, it should approach zero as the erroneous model becomes the exact model.

Since \(M_{o}\) and \(\partial M_{o}\) are not defined for a nonvalid model, we first define another set, called \(\partial M_{o}^{\prime}\) as follows. We project the loops of edges \(e_{i}\) of \(m_{o}\) onto each of the corresponding surfaces to obtain new loops of edges \(e_{i}^{\prime}\) that bound new faces \(F_{i}^{\prime}\), and let \(\partial M_{o}^{\prime}=\cup_{I} F_{i}^{\prime}\). Note that \(\partial M_{0}^{\prime}\) may not bound a solid. The details of this construction are in Sections 3.1.1, 3.1.2, and 3.2. In these sections we define a function \(\phi\) that evaluates the geometric difference between \(\partial M_{o}^{\prime}\) and \(\partial M_{n}\). We will denote this by \(\phi\left(\partial M_{o}^{\prime}, \partial M_{n}\right)\). Let \(\varepsilon\) be a user-specified tolerance for the geometric change and let \(m_{o}, G\left(m_{o}\right)\) be as above. An ideal boundary reconstruction algorithm should follow the following procedure (see Fig. 2):

' Two topological entities of different dimensionalities have an incidence relation if one is a proper subset of the other. Two topological entities of same dimensionality have an adjacency relation if their intersection is a lower dimensional entity that has an incidence relation with each of them. 2 We denote models and face nodes by lowercase letters, and the point sets they represent by uppercase letters. For example, model m, represents solid Mo. The topological structure of a node is denoted by \(G(node)\).

![FIG. 2. Flow chart of an ideal global reconstruction algorithm.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-2-p006.png)

*FIG. 2. Flow chart of an ideal global reconstruction algorithm.: Flow chart of an ideal global reconstruction algorithm.*

return the one with

$$
minimal geometric change N construct in s.t. g (Mn.) = g (mo)
$$

$$
and ¢ (Mó, aMn) ≤E Mn exist?
$$

return the one with minimal topological structure change

return the one with minimal genus change

- Find a new model mn, such that mn has topological structure \(G(mo)\), i.e., \(G(Mn)\) ~ \(G(mo)\) and $ (aM,, a Mn) ≤ E.

- If there exists a number of such new models, select the one with the minimal value.

- Otherwise, find a new model mn, such that \(G(m)\) is different from \(G(mo)\) but g(mn) = g(mo), and (aM, a Mn) ≤ 8.

- If there exists a number of such new models, select the one with the minimal topological structure change; e.g., the difference of the total numbers of arcs and nodes in \(G(mn)\) and \(G(mo)\) is minimal.

- Otherwise, find a new model mn with (aM', a Mn) ≤&. If there exist more than one such new boundaries, select the one with the minimal topological change (i.e., minimal genus change; otherwise, no new model is reconstructed.

3 Two graphs are homeomorphic if both can be obtained from the same graph by a sequence of subdivisions of arcs.

## 3 PROBLEM COMPLEXITY

### 3.1 Face Reconstruction Problem

![FIG. 3. Two homeomorphic graphs with different geometric embeddings.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-3-p007.png)

*FIG. 3. Two homeomorphic graphs with different geometric embeddings.: Two homeomorphic graphs with different geometric embeddings.*

![FIG. 4. Curve segments from surface intersections.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-4-p008.png)

*FIG. 4. Curve segments from surface intersections.: curve segments from surface intersections.*

#### 3.1.1 Face Boundary Reconstruction

Let \(R\) be the underlying surface of face node \(f_{o}\), and \(\left\{R_{i}\right\}_{1 \leq i \leq N}\) be surfaces in \(m_{o}\) such that \(C_{i}=R \cap R_{i} \neq \emptyset\). Surface intersections could be very complex. Here, for simplicity, we assume that surfaces do not overlap. In addition, we also exclude isolated intersection points, since such a point does not bound a finite region on \(R\), and therefore, is not used to form the face boundary. However, if an intersection point between two surfaces is on an intersection curve, it may be used as a vertex in the face boundary. See Fig. 4a, where the intersection point of \(R\) and \(R_{4}\) is on \(C_{1}\). Furthermore, \(C_{i}\) 's may intersect each other. Each \(C_{i}\) is subdivided by intersection points into curve segments, each of which is either an open curve bounded by two intersection points or a simple closed curve. Those intersection points, indeed, are intersections of three or more surfaces. Denote the collection of curve segments on all \(C_{i}\) 's by \(\left\{S_{i_{j}}\right\}\). See Fig. 4b, where broken lines are curve segments and solid dots are intersection points. In the figure, because the underlying surface is finite, its boundary curves are also used in creating curve segments. Note that \(\left\{S_{i_{j}}\right\}\) subdivide \(R\) into patches whose interiors are disjoint and intersection-free. The face geometry must be either one of these patches or the union of some patches. Therefore, the face boundary consists of curve segments from \(\left\{S_{i_{j}}\right\}\).

In the following description, for simplicity, we use a lowercase symbol to denote an edge or a vertex as a point set. Whenever the corresponding representational node is referred, the word node is used before the notation. For example, node \(e\) represents edge \(e\). For models and faces, the same notation scheme as in the previous section is used, i.e., lowercase symbols for nodes and uppercase symbols for point-sets. Let node \(e_{i_{k}}\) be an edge node in \(f_{o}\), also shared by face node \(f_{i}\) having \(R_{i}\) as its underlying surface. Then, to maintain geometric consistency of the adjacency relation between these two faces, \(e_{i_{k}}\) must be a subset of \(C_{i}\). This is rarely true as the underlying curve given in node \(e_{i_{k}}\) is often an approximation of the exact intersection curve \(C_{i}\). As a matter of fact, as illustrated in Fig. 5, \(e_{i_{k}}\) may be pathologically defined by a space curve (the broken line) and two points (the two circles) that may not be on the curve as they are supposed to be. Because the adjacency relation is symbolic and thus exact, the initial rectification of node \(e_{i_{k}}\) can be done by using \(C_{i}\) as the underlying curve and discarding the one given in the original model. Consequently, the vertices must be on \(C_{i}\). They also need to be

![FIG. 5. Initial rectification of an edge on a face.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-5-p009.png)

*FIG. 5. Initial rectification of an edge on a face.: Initial rectification of an edge on a face.*

curve of node eik

close to their original erroneous positions in order to reflect the design intent. Reasonable replacements of the original vertices \(v_{i_{1}}, v_{i_{2}}\), for instance, could be the projections \(v_{i_{1}}^{\prime}, v_{i_{2}}^{\prime}\) of \(v_{i_{1}}, v_{i_{2}}\) onto \(C_{i}\). See Fig. 5, where the new vertices are solid dots. Therefore, such a rectified edge, denoted by \(e_{i_{k}}^{\prime}\), is a subset of \(C_{i}\), bounded by \(v_{i_{1}}^{\prime}, v_{i_{2}}^{\prime}\) and oriented in the same way as \(e_{i_{k}}\) provided that the given underlying curve in node \(e_{i_{k}}\) and \(C_{i}\) are not far apart.

However, as a face should be bounded by curve segments from \(\left\{S_{i_{j}}\right\}\), a rectified edge should consist of such curve segments. Edge \(e_{i_{k}}^{\prime}\) is not guaranteed to be so. See Fig. 6a. Further rectification of \(e_{i_{k}}\) selects some curve segments on \(C_{i}\) such that their union is a simple open or closed curve and an optimal approximation of \(e_{i_{k}}^{\prime}\). The union defines a new edge \(e_{i_{k}}^{\prime \prime}\), whose corresponding node has the same symbolic information as node \(e_{i_{k}}\), i.e., the same embedding surfaces, the same parent faces, and the same orientation, but has a consistent geometric representation while node \(e_{i_{k}}\) does not. Edge \(e_{i_{k}}^{\prime \prime}\) can be obtained by perturbing vertices \(v_{i_{1}}^{\prime}, v_{i_{2}}^{\prime}\) of \(e_{i_{k}}^{\prime}\) to the closest intersection points on \(C_{i}\). This vertex per turbation is also necessary in order to achieve geometric consistency at a vertex. A vertex is involved in various incidence and adjacency relations between its incident faces and edges, and therefore, needs to be positioned at the intersection point of those underlying surfaces.

![FIG. 6. Creation of e, by vertex perturbation.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-6-p009.png)

*FIG. 6. Creation of e, by vertex perturbation.: Creation of e, by vertex perturbation.*

![FIG. 7. Trimming of dangling curve segments (a) and gap filling (b).](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-7-p010.png)

*FIG. 7. Trimming of dangling curve segments (a) and gap filling (b).: Trimming of dangling curve segments (a) and gap filling (b).*

The collection of such rectified edges, however, may not form a valid face boundary, as there may exist open loops and/or dangling curve segments. For example, in Fig. 7a (where the rectified edges are thick lines), a dangling curve segment \(S_{12}\) and a gap between \(e_{5}^{\prime \prime}\) and \(e_{9}^{\prime \prime}\) exist. The final act of face reconstruction is to trim away dangling curve segments and fill gaps with curve segments from \(\left\{S_{i_{j}}\right\}\), so that the selected curve segments form a valid face boundary. See Fig. 7b. This trimming and gap-filling process should create a face boundary that satisfies the topological and geometric requirements stated in the problem statement. Assume that, in the final reconstructed face boundary, the selected curve segments from \(C_{i}\) are \(\mathcal{S}_{i}=\left\{S_{i j_{l}}\right\}_{1 \leq l \leq L_{i}}\). A new edge \(e_{i_{k}}^{n}\) is created by stringing curve segments in \(\mathcal{S}_{i}\). The process starts with an arbitrary curve segment \(S_{i j_{1}} \in \mathcal{S}_{i}\), and searches for its adjacent curve segments in \(\mathcal{S}_{i}\). If, at one endpoint, exactly one adjacent curve segment \(S_{i j_{2}}\) is found, then \(S_{i j_{2}}\) is selected and the search marches on at the other endpoint of \(S_{i j_{2}}\); otherwise, the process terminates and resumes at the other endpoint of \(S_{i j_{1}}\). Note that there may be more than one new edge created from \(\mathcal{S}_{i}\). For example, in Fig. 7, curve segments \(S_{72}, S_{74}\) on \(C_{7}\) are selected in the final face boundary, creating two new edges \(e_{7}^{n}\) and \(e_{11}^{n}\).

In summary, an edge \(e_{i_{k}}\) in the original model, shared by faces \(f_{o}\) and \(f_{i}\), is first rectified by projecting its vertices onto \(C_{i}=R \cap R_{i}\), which is the exact underlying curve of node \(e_{i_{k}}\). This produces \(e_{i_{k}}^{\prime}\), and achieves a consistent adjacency relation between \(f_{o}\) and \(f_{i}\) but may not do so at the vertices. Edge \(e_{i_{k}}^{\prime}\) is then rectified by perturbing its vertices to their closest intersection points on \(C_{i}\), such that the resulting edge \(e_{i_{k}}^{\prime \prime}\) consists of curve segments in \(\left\{S_{i_{j}}\right\}\). Note that node \(e_{i_{k}}^{\prime \prime}\) has the same symbolic information as node \(e_{i_{k}}\) and could be geometrically consistent with all adjacency and incidence relations in which it is involved, if other topological entities are appropriately constructed. Typically, the geometric change between \(e_{i_{k}}^{\prime \prime}\) and \(e_{i_{k}}\) is minimal. Since such edges may not form a valid face boundary, additional curve segments from \(\left\{S_{i_{j}}\right\}\) are added to fill gaps and dangling curve segments are trimmed away. In the rectified face boundary, a new edge \(e_{i_{k}}^{n}\) consists of curve segments

#### 3.1.2 Problem Formulation and Proof of NP-Hardness

To mathematically formulate the FR problem, especially to quantify face geometric change, we classify new edges into two categories:

1. A new edge \(e_{i_{k}}^{n}\) belongs to the first category if it has a corresponding edge \(e_{i_{k}}\) in the original model; i.e., \(e_{i_{k}}^{n}\) is considered to be the rectified \(e_{i_{k}}\). Such a new edge node has the same symbolic information as node \(e_{i_{k}}\) and a geometry that is an optimal approximation of that of node \(e_{i_{k}}\). Because \(e_{i_{k}}\) is not well defined, the geometric change between \(e_{i_{k}}^{n}\) and \(e_{i_{k}}\) is measured by comparing \(e_{i_{k}}^{n}\) and \(e_{i_{k}}^{\prime}\), which is not only well defined but also symbolically the same as and geometrically close to \(e_{i_{k}}\). We define \(\phi_{e}:\left(C_{i} \times C_{i}\right) \rightarrow \mathbf{R}\), where

$$
\begin{equation*} \phi_{e}\left(e_{i_{k}}^{n}, e_{i_{k}}^{\prime}\right)=\operatorname{length}\left(\left(e_{i_{k}}^{n} \cup e_{i_{k}}^{\prime}\right)-\left(e_{i_{k}}^{n} \cap e_{i_{k}}^{\prime}\right)\right), \quad e_{i_{k}}^{n}, e_{i_{k}}^{\prime} \subseteq C_{i} . \tag{2} \end{equation*}
$$

For example, in Fig. 6, if \(e_{i_{k}}^{n}=e_{i_{k}}^{\prime \prime}\), meaning that during the trimming-and-filling stage the edge is unchanged, then

$$
\begin{equation*} \phi_{e}\left(e_{i_{k}}^{n}, e_{i_{k}}^{\prime}\right)=\left|v_{i 1}^{\prime} v_{i 1}^{\prime \prime}\right|+\left|v_{i 2}^{\prime} v_{i 2}^{\prime \prime}\right|, \tag{3} \end{equation*}
$$

where || denotes the length of a curve segment. If there exist more than one new edges on \(C_{i}\) that could belong to the first category, the one with the minimal \(\phi_{e}\) value is designated as the new edge in the first category; i.e., there is at most one corresponding new edge in the new boundary for each edge in the original model. In addition, \(e_{i_{k}}^{n} \cap e_{i_{k}}^{\prime} \neq \emptyset\), so that a new edge whose geometry is far away from \(e_{i_{k}}^{\prime}\) will not be taken as the corresponding new edge of \(e_{i_{k}}\). This could happen, for example, when two new edges \(e_{i_{k}, 1}^{n}, e_{i_{k}, 2}^{n}\) have the same symbolic information as \(e_{i_{k}}\) but

$$
\begin{aligned} e_{i_{k}, 1}^{n} \cap e_{i_{k}}^{\prime} & \neq \emptyset, \\ e_{i_{k}, 2}^{n} \cap e_{i_{k}}^{\prime} & =\emptyset, \\ \phi_{e}\left(e_{i_{k}, 1}^{n}, e_{i_{k}}^{\prime}\right) & >\phi_{e}\left(e_{i_{k}, 2}^{n}, e_{i_{k}}^{\prime}\right) . \end{aligned}
$$

In Fig. 7b, all the new edges, except \(e_{11}^{n}\), belong to the first category.

- All other new edges belong to the second category. These edges are generally added to close gaps. Let a new edge be on curve Cj = Rn Rj. It is possible that the face on R; is not adjacent to fo in the original model, and therefore, the new edge on C; does not have a corresponding old edge.

Because the edges in the original face node carry the design intent, geometric changes to them should be minimized, i.e., \(\sum \phi_{e}\) for the new edges of the first category should be minimal. If there exist more than one choices of new face boundary having the minimum, that with the shortest total length of the edges of the second category should be chosen, because any drastic change is not trustworthy. Figure 8a shows the curve segments and initially rectified edges. Note that the original face node has an inconsistent geometric representation. It can be seen in Fig. 8b that if all four edges represented by thick lines are

![FIG. 8. Minimization of edge geometric change.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-8-p012.png)

*FIG. 8. Minimization of edge geometric change.: Minimization of edge geometric change.*

selected in the final boundary, \(\sum \phi_{e}\) is the minimum. There exist five such loops. Figure 8 c shows the final face boundary that has the shortest gap-closing edge \(e_{5}^{n}\), and Fig. 8d shows the other four.

We now formulate the face reconstruction problem as a search problem: Face reconstruction \((F R)\) problem. Let \(f_{o}\) be a face node, whose geometric representation is inconsistent with its topological structure, in a B-rep model, and \(\left\{S_{i_{j}}\right\}\) be as above. Search for a subcollection

$$
\begin{equation*} \left\{S_{i j_{l}}\right\}_{1 \leq i \leq N, 1 \leq l \leq L_{i}} \tag{4} \end{equation*}
$$

of \(\left\{S_{i_{j}}\right\}\), where \(L_{i}\) is the number of curve segments selected on \(C_{i}\), such that

- {Siji) bounds a face En.

- \(G(fn)\) is homeomorphic to \(G(fo)\) in the strong sense.

- Le(e!,, ci) is minimal for the new edges of the first category.

- If condition (3) is satisfied, then the total length of the edges of the second category is also minimal.

Intuitively, this problem can be converted to a graph problem as \(\left\{S_{i_{j}}\right\}\) forms a geometric embedding on \(R\) of a graph. This graph, \(G_{f}=\left(V_{f}, E_{f}\right)\), has curve segments in \(\left\{S_{i_{j}}\right\}\) as \(\operatorname{arcs}\) in \(E_{f}\) and intersection points as nodes in \(V_{f}\). The solution to the FR problem is then a subgraph satisfying the properties in the problem statement. The face reconstruction process is a process of searching for such a subgraph. A straightforward implementation of this process is to search all possible subgraphs and find the one satisfying conditions 1 to 4 above. Such an exhaustive search, however, may need exponential time in terms of the number of arcs in \(E_{f}\). In the following, we prove that the FR problem is NP-hard by proving a restricted problem is NP-hard. See also the Appendix for some further comments on NP-hard problems, but first, we introduce a known NP-hard problem [25]:

Rural postman problem \({ }^{4}\) : Let graph \(G=(V, E)\). Each \(e \in E\) has length \(l(e) \in Z_{0}^{+}\). Let \(E^{\prime} \subseteq E\). Find the circuit in \(G\) that includes each \(\operatorname{arc}\) in \(E^{\prime}\) and that has the shortest total length.

THEOREM 3.1. FR problem is NP-hard.

Proof. The basic idea of the proof is to consider the following instance of the restricted FR problem: The topological structure of \(f_{o}\) represents a closed disk, and there is only one curve segment on each \(C_{i}\) (see Fig. 9). The boundary of \(F_{o}\) is then a simple closed curve. The solution to the problem must be a circuit in graph \(G_{f}\) if condition (2) is to be satisfied. For each edge \(e_{i_{k}}\) of \(F_{o}\), we construct \(e_{i_{k}}^{\prime}, e_{i_{k}}^{\prime \prime}\) as above. Because there is only one

$$
\begin{equation*} \mathcal{S}_{1}=\left\{S_{i 1} \mid \text { there exists } e_{i_{k}}^{\prime \prime}=S_{i 1}, 0 \leq i \leq N\right\} . \tag{5} \end{equation*}
$$

" Here we give the rural postman search problem because the FR problem is also a search problem. In [25], the rural postman decision problem is given.

![FIG. 9. An instance of the restricted FR problem.](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-9-p014.png)

*FIG. 9. An instance of the restricted FR problem.: An instance of the restricted FR problem.*

Then, if all the curve segments in \(\mathcal{S}_{1}\) are selected, \(\sum \phi_{e}\) for the edges of the first category reaches its minimum. This means that a valid face boundary that includes all the curve segments in \(\mathcal{S}_{1}\) will be selected over any choice that does not.

The corresponding instance of the rural postman problem is as follows: Graph \(G_{f}\) with \(l(e)=\operatorname{length}\left(S_{i_{1}}\right)\) for each \(i\), and \(E^{\prime}=\mathcal{S}_{1}\). We prove that it can be reduced to the restricted FR problem at least in the abstract setting of graph theory. \({ }^{5}\) It can be observed that the solution to the restricted FR problem answers the rural post man problem; if the solution exists for the restricted FR problem and contains all the curve segments in \(\mathcal{S}_{1}\), it is the circuit with the shortest length and includes all the \(\operatorname{arcs}\) in \(E^{\prime}\), and therefore, is the solution to the rural postman problem; if the solution does not exist or it exists but does not contain all the edges in \(\mathcal{S}_{1}\), no solution exists for the rural postman problem.

### 3.2 Boundary Reconstruction Problem

Now we formulate the BR problem and prove that it is also NP-hard. Let \(m_{o}\) be the given B-rep model. The underlying surfaces, \(\left\{R_{i}\right\}_{1 \leq i \leq N}\), are subdivided by surface intersections into a collection of patches

$$
\begin{equation*} \left\{P_{i j}\right\}_{1 \leq i \leq N, 1 \leq j \leq N_{i}}, \tag{6} \end{equation*}
$$

where \(N_{i}\) is the number of patches on surface \(R_{i}\). For a face node \(f_{i}, F_{i}\) may not be well defined. Because the embedding information is symbolic and thus exact, the initial rectification of \(F_{i}\) can be done by trimming the underlying surface \(R_{i}\) of \(f_{i}\) using projections of the loops in \(f_{i}\) onto \(R_{i}\). Denote such a face by \(F_{i}^{\prime}\). As in face reconstruction, \(F_{i}^{\prime}\) is further rectified by selecting patches from \(\left\{P_{i_{j}}\right\}_{1 \leq j \leq N_{i}}\) to form a new geometry that is an optimal approximation of \(F_{i}^{\prime}\). Denote this new face by \(F_{i}^{\prime \prime}\). The difference between \(F_{i}^{\prime}\) and \(F_{i}^{\prime \prime}\) can be measured by function \(\phi_{f}:\left(R_{i} \times R_{i}\right) \rightarrow \mathbf{R}\), where

5 Theoretically, it is possible to develop a linear algorithm to draw a planar graph on the plane. See [26, 27]. This establishes the argument that an abstract graph search problem could be converted to an instance of the geometric problem (FR problem).

$$
\begin{equation*} \phi_{f}\left(F_{i}^{\prime}, F_{i}^{\prime \prime}\right)=\operatorname{area}\left(\left(F_{i}^{\prime} \cup F_{i}^{\prime \prime}\right)-\left(F_{i}^{\prime} \cap F_{i}^{\prime \prime}\right)\right), \quad F_{i}^{\prime}, F_{i}^{\prime \prime} \subseteq R_{i} . \tag{7} \end{equation*}
$$

Such rectified faces may not form a valid solid boundary due to the possible existence of dangling patches and holes. Therefore, a trimming-and-filling process follows. Similar to face reconstruction, in the new solid boundary, a new face \(F_{i}^{n}\) belongs to the first category if it has a corresponding old face, and to the second category if it does not. For the faces of the first category, \(\sum \phi_{f}\left(F_{i}^{n}, F_{i}^{\prime}\right)\) should be minimized. If there exist more than one valid boundaries having the minimum \(\sum \phi_{f}\), that with the minimal total area of the faces of the second category should be chosen.

The boundary reconstruction problem can also be formulated as a search problem: Boundary reconstruction ( \(B R\) ) problem. Let \(m_{O}\) be a B-rep model whose geometric representation is inconsistent with its topological structure, and \(\left\{P_{i_{j}}\right\}\) be as above. Search for a subcollection

$$
\begin{equation*} \left\{P_{i j_{k}}\right\}_{1 \leq i \leq N, 1 \leq k \leq K_{i}} \tag{8} \end{equation*}
$$

of \(\left\{P_{i_{j}}\right\}\), where \(K_{i}\) is the number of patches selected on surface \(R_{i}\), such that

- { Pijk) bounds a solid Mn.

- g(mn) = g(mo), where m, is the new model representing Mn.

- 2ф+ (F", F) is minimal for the faces of the first category.

- If condition (3) is satisfied, then the total area of the faces of the second category is also minimal.

We now prove that the BR problem is NP-hard:

THEOREM 3.2. BR problem is NP-hard. Proof. We prove the theorem by converting the restricted FR problem to the BR problem. Assume that in an instance of the restricted FR problem, the face node \(f_{o}\) has a plane as its underlying surface. Sweep the face along the normal direction to a parallel plane. The sweeping solid of \(F_{o}\) should be homeomorphic to a closed ball. The instance of the BR problem is a patch collection

$$
\begin{align*} \left\{P_{i j}\right\}= & \{\text { patches generated from curve segments }\} \\ & \cup\{\text { patches from the two planes }\} \tag{9} \end{align*}
$$

and a model \(m_{o}\) with its topological structure representing a sphere and \(\left\{F_{i}^{\prime}\right\}\) generated from \(\left\{e_{i_{k}}^{\prime}\right\}\). See Fig. 10 for an example. This conversion can be executed in polynomial time. If a subcollection of \(\left\{S_{i_{j}}\right\}\) is the solution to the restricted FR problem, then the patches generated from the curve segments in the subcollection, with additional patches from the two planes, is the solution to the BR problem. Conversely, if a subcollection of the patches is the solution to the BR problem, it must be bounded by two patches from the two planes and patches whose generating curve segments indeed form the solution to the restricted FR problem.

For models with multiple shells, the same result holds, because the boundary reconstruction problem of models with one shell is a special case of that of models with multiple shells.

![FIG. 10. Illustration of the proof of Theorem 3.2.(](/Users/evanthayer/Projects/stepview/docs/2001_boundary_representation_model_rectification/figures/figure-10-p016.png)

*FIG. 10. Illustration of the proof of Theorem 3.2.(: Illustration of the proof of Theorem 3.2.(*

sweeping

FR problem

## 4 CONCLUSIONS

The BR problem is, in certain ways, similar to the gap boundary matching problem studied by Barequet and Sharir [9], which is also shown to be an NP-hard (global search) problem. However, they are quite different in nature as the former reconstructs a boundary from a set of surfaces and involves complex topological constraints, whereas the latter matches boundaries of a set of surface patches. Theoretically, of course, all NP-complete problems are equivalent, but their specifics can vary significantly.

The understanding of the NP-hardness of a problem helps design algorithms to efficiently and properly solve the problem. In a recent paper [29], we propose model rectification algorithms that approximate the process of finding the optimal solutions described here. To achieve numerical robustness in a floating point environment, interval model representation proves to be a powerful tool [16, 17]. We further study some key topological issues of interval solid models in [28], and develop interval geometric and numerical methods useful in model rectification in [30]. All these are summarized in a review paper [31].

APPENDIX: SHORT REVIEW OF NP-COMPLETENESS

This Appendix provides a brief introduction to the theory of NP-completeness. For details, see [25]. A decision problem is a problem whose answer is yes or no. A problem is said to belong to the class P if it can be solved by a polynomial time DTM program. DTM is the abbreviation for deterministic one-tape Turing machine, a simplified computing model. If the problem can be solved by a polynomial time NDTM program, it belongs to the class NP. NDTM, nondeterministic one-tape Turing machine, has the exact same structure as that of DTM, except that it has a guessing module. A NDTM program has two distinct stages: guessing and checking. For example, the traveling salesman problem is given as:

Traveling salesman problem. Given a finite set of cities, a distance between each pair of cities, and a bound \(B\), is there a tour of all the cities such that the total distance of the tour is no larger than \(B\) ?

A NDTM program first guesses a tour of all the cities, and then verifies in polynomial time if the length of this guessed tour is less than the given threshold. If at least one guessed tour is accepted, the answer to the problem is yes. Therefore, the traveling salesman problem is in class NP.

It is observed that class \((\mathrm{P}) \subseteq\) class \((\mathrm{NP})\). It is also an unproven conjecture that \(\mathrm{P} \neq \mathrm{NP}\). For a problem in NP, there exists a polynomial \(p\) such that the problem can be solved by a deterministic algorithm having time complexity \(O\left(2^{p(n)}\right)\), where \(n\) is the length of the input string. A decision problem \(\Pi\) is NP-complete if \(\Pi \in \mathrm{NP}\) and, for all other decision problems \(\Pi^{\prime} \in \mathrm{NP}\), there is a polynomial transformation from \(\Pi^{\prime}\) to \(\Pi\). A polynomial transformation is a mapping \(f\) such that

- There exists a polynomial DTM program that computes f.

- For any instance x of the problem, x is accepted if and only if f(x) is accepted.

Therefore, NP-complete problems are the "hardest" problems in NP. The NP-completeness proof of a decision problem consists of the following four steps:

- Show that П є NP, i.e., I can be solved by a NDTM program.

- Select a known NP-complete problem '.

- Construct a transformation f from ' to.

- Prove that f is a polynomial transformation.

The NP-completeness can also be proven by restriction; that is, a problem is NP-complete if it contains a known NP-complete problem as a special case.

The concept of NP-hardness applies to problems outside class NP, e.g., search problems. Informally, a search problem is NP-hard if it is at least as hard as some NP-complete problem. For example, the search for the shortest tour of all the cites is as hard as the traveling salesman decision problem, because the solution to the search problem certainly answers the decision problem.

## Acknowledgments

Funding for this work was obtained in part from NSF Grant DMI-9215411, ONR Grant N00014-96-1-0857, and the Kawasaki chair endowment at MIT. The authors thank W. Cho and G. Yu for their assistance in the early phases of the CAD model rectification project. We also thank T. J. Peters and A. C. Russell, the referees and the area editor of the Graphical Models journal for their comments on this work.

Note. This paper was also presented at the 6th ACM Symposium on Solid Modeling and Applications, Ann Arbor, MI, June 2001.

## References

- A. A. G. Requicha, representations for rigid solids: Theory, methods, and systems, ACM Comput. Surveys 12, 1980, 437-464.

- D. E. LaCourse, Handbook of Solid Modeling, McGraw-Hill, New York, 1995.

- C. M. Hoffmann, Geometric and Solid Modeling—An Introduction, Morgan Kaufmann, San Mateo, CA, 1989.

- M. Mäntylä, An Introduction to Solid Modeling, Computer Science Press, Rockville, MD, 1988.

- T. Sakkalis, G. Shen, and N. M. Patrikalakis, Representational validity of boundary representation models, Computer Aided Design 32, 2000, 719-726.

- 3D Systems, Inc., Stereolithography Interface Specification, June 1988.

- J. H. Bohn and M. J. Wozny, A topology-based approach for shell-closure, in Geometric Modeling for Product Realization (P. R. Wilson, M. J. Wozny, and M. J. Pratt, Eds.), pp. 297-318, Elsevier, Amsterdam, 1993.

- I. Makela and A. Dolenc, Some efficient procedures for correcting triangulated models, in Proceedings of Solid Freeform Fabrication Symposium, University of Texas at Austin, 1993, pp. 126-134.

- G. Barequet and M. Sharir, Filling gaps in the boundary of a polyhedron, Computer Aided Geom. Design, 12, 1995, 207-229.

- G. Barequet and S. Kumar, Repairing CAD Models, in Proc. IEEE Visualization, Phoenix, AZ, 1997, pp. 363-370.

- G. Barequet, C. A. Duncan, and S.Kumar, RSVP: A Geometric Toolkit for Controlled Repair of Solid Models, IEEE Trans. Visualiz. Comput. Graphics, 4, 1998, 162-177.

- T. M. Murali and T. A. Funkhouser, Consistent solid and boundary representations from arbitrary polygonal data, in Proceedings of 1997 Symposium on Interactive 3D Graphics, Providence, Rhode Island (A. Van Dam, Ed.), pp. 155-162, Assoc. Comput. Mach. Press, New York, 1997.

- B. Hamann and B. A. Jean, Interactive surface correction based on a local approximation scheme, Comput. Aided Geom. Design 13, 1996, 351-368.

- C. M. Hoffmann, The problems of accuracy and robustness in geometric computation, Computer 22, 1989, 31-41.

- S. Fortune, Polyhedral modeling with multiprecision integer arithmetic, Comput. Aided Design 29, 1997, 123-133.

- C.-Y. Hu, N. M. Patrikalakis, and X. Ye, Robust interval solid modeling: Part I, representations, Comput. Aided Design 28, 1996, 807-817.

- C.-Y. Hu, N. M. Patrikalakis, and X. Ye, Robust interval solid modeling: Part II, boundary evaluation, Comput. Aided Design 28, 1996, 819-830.

- F.-L. Krause, C. Stiel, and J. Lüddemann, Processing of CAD-data-Conversion, verification and repair, in Proceedings of 4th Symposium on Solid Modeling and Applications, Atlanta, GA, May 1997 (C. Hoffmann and W. Bronsvoort, Eds.), pp. 248-254, Assoc. Comput. Mach., New York, 1997.

- D. J. Jackson, Boundary representation modelling with local tolerances, in Proceedings of the 3rd Symposium on Solid Modeling and Applications, Salt Lake City, UT, May 1995 (C. Hoffmann and J. Rossignac, Eds.), pp. 247-253, Assoc. Comput. Mach., New York, 1995.

- International TechneGroup Incorporated, Introduction-CAD fix Makes Geometry Data Exchange Work. Available at http: www.iti-oh.com.

- Theorem Solutions Inc, Product Information. Available at http: www.theorem.co.uk productmain.htm.

- I. C. Braid, Notes on a Geometric Modeller, C.A.D. Group Document 101, University of Cambridge, Cambridge, UK, 1979.

- U.S. Product Data Association, ANS US US Part Part Integrated Geometric Resources: Geometric and Topological representation, 1994.

- F. Harary, Graph Theory, Addison-Wesley, Reading, MA, 1969.

- M. R. Garey and D. S. Johnson, Computer and Intractability: A Guide to the Theory of NP-completeness, W. H. Freeman, San Francisco, 1979.

- N. L. Biggs and A. T. White, Permutation Groups and Combinatorial Structures, Cambridge Univ. Press, Cambridge, UK, 1979.

- N. Chiba, T. Yamanouchi, and T. Nishizeki, Linear algorithms for convex drawings of planar graphs, in Progress in Graph Theory (J. A. Bondy and U. S. R. Murty, Eds.), pp. 153-173, Academic Press, New York,

- T. Sakkalis, G. Shen, and N. M. Patrikalakis, Topological and geometric properties of interval solid models, Graphical Models 63, 2001, 163-175.

- G. Shen, T. Sakkalis, and N. M. Patrikalakis, Manifold boundary representation model rectification ("La rectification des modèles des varietés B-rep"), in Proceedings of the 3rd International Conference on Integrated

- Design and Manufacturing in Mechanical engineering (C. Mascle, C. Fortin, and J. Pegna, Eds.), p. 199 and CDROM, Presses internationales Polytechnique, Montreal, Canada, 2000.

- G. Shen, T. Sakkalis, and N. M. Patrikalakis, Interval methods for B-rep model verification and rectification, in Proceedings of the ASME 26th Design Automation Conference, Baltimore, MD, September 2000, p. 140 and CDROM. ASME, NY, 2000.

- N. M. Patrikalakis, T. Sakkalis, and G. Shen, Boundary representation models: Validity and rectification, Invited paper in Proceedings of the 9th IMA Conference on the Mathematics of Surfaces, University of Cambridge, Cambridge, UK, September 2000 (R. Cipolla and R. Martin, Eds.), pp. 389-409, Springer-Verlag, London, 2000.
