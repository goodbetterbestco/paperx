# 2019 integrating cad and numerical analysis dirty geometry handling using the finite cell method

Benjamin Wassermann, Stefan Kollmannsberger, Shuohui Yin, László Kudela, Ernst Rank

\({ }^{\mathrm{a}}\) Chair for Computation in Engineering, Technical University of Munich, Arcisstr. 21, 80333 München, Germany
\({ }^{\mathrm{b}}\) School of Mechanical Engineering, Xiangtan University, Hunan 411105, PR China
\({ }^{\mathrm{c}}\) Institute for Advanced Study, Technical University of Munich, Lichtenbergstr. 2a, 85748 Garching, Germany

## Abstract

This paper proposes a computational methodology for the integration of Computer Aided Design (CAD) and the Finite Cell Method (FCM) for models with "dirty geometries". FCM, being a fictitious domain approach based on higher order finite Cell Method (FCM) for models with "dirty geometries". FCM, being a fictitious domain approach based on higher order finite elements, embeds the physical model into a fictitious domain, which can be discretized without having to take into account the boundary of the physical domain. The true geometry is captured by a precise numerical integration of elements cut by the boundary. Thus, an effective Point Membership Classification algorithm that determines the inside-outside state of an integration point with respect to the physical domain is a core operation in FCM. To treat also "dirty geometries", i.e. imprecise or flawed

## 1 Introduction

Product development in the scope of Computer Aided engineering (CAE) typically involves Computer Aided Design (CAD) and numerical analyses. The life cycle of almost every complex mechanical product starts with the Design (CAD) and numerical analyses. The life cycle of almost every complex mechanical product starts with the creation of a CAD model which is then converted into a suitable format for downstream CAE applications such as Finite Element analysis, Rapid Prototyping, or automated manufacturing. However, a truly smooth transition from a geometric to a computational model is still challenging. This is especially the case for numerical simulations like the Finite Element Method. Very often, complex and time-consuming model preparation and pre-processing steps

![Figure 1. Cad model of a screw with flaws. Free edges are highlighted in blue . (For interpretation of the references to color in this figure](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-1-p002.png)

*Figure 1. Cad model of a screw with flaws. Free edges are highlighted in blue . (For interpretation of the references to color in this figure: Cad model of a screw with flaws. Free edges are highlighted in blue. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)*

are necessary to obtain a decent numerical model that is suitable for analysis purposes. For complex CAD models, this transition process can take up to 80% of the overall analysis time [1]. For this reason, various alternative numerical approaches have been developed which seek to avoid or shorten this costly transition process (e.g., meshing). Isogeometric analysis (IGA) as the most prominent example aims at easing the transition from CAD to computational analysis by using the same spline basis functions for geometric modeling and numerical simulation [1,2]. In a related earlier approach Cirak and Scott [3] presented an integrated design process based on Subdivision Surfaces. Kagan and Fischer [4] used B-spline finite elements in an effort to join design and analysis. However, independent of the respective numerical approach, flaws may appear in the CAD model during the design-analysis cycle-such as double entities, gaps, overlaps, intersections, and slivers-as shown in Fig. 1. They are mainly due to data loss while the model is exchanged between different CAD and or CAE systems, to inappropriate operations by the designer, or to approximation steps resulting in incompatible geometries. These model flaws, also called dirty topologies or dirty geometries, may be extremely small or even unapparent. While they are of no particular importance to a CAD engineer they may, however, cause serious problems for structural analyses. In the best case, they merely generate excessively fine meshes in some regions which are not relevant to structural analysis (e.g., at fillets, etc.) but drive up computational time unnecessarily. In the worst case, computations fail completely because no finite element mesh can be created. This is due to the fact that neither classical finite element approaches nor the newly developed methods mentioned above are designed to handle dirty topologies and geometries. Thus, extra effort is necessary to repair, heal, or reconstruct the model into an analysis-suitable geometry [5], even if the affected region is not of special interest to the structural analyst. This is also a major obstacle for IGA, which heavily relies on flawless geometries.

Solid CAD modeling systems mainly rely on two different representation techniques: Boundary representation (B-Rep) and Constructive Solid Geometry (CSG) [6] which is often extended to a so-called procedural modeling. In CSG, a volume is described by volumetric primitives, whereas in B-Rep it is described via its surfaces. Consequently, B-Rep models provide direct and easy access to the explicit boundaries. However, B-Rep models are not necessarily valid, meaning that it might in some cases not be possible to determine whether a point lies inside or outside (point Membership Classification). In contrast, CSG models are inherently watertight. Problems such as non-manifolds, dangling faces, or lines, or Boolean operations on disjoint objects need to be handled accordingly by the respective CAD system. A novel representation technique-V-Rep (volumetric representation) - was recently proposed by Elber et al. [7] and implemented into the IRIT solid modeler. \({ }^{1}\) V-Reps are constructed of volumetric, non-singular B-Spline primitives, thus, providing both an explicit volume and explicit surface description. As the V-Rep models follow the CSG idea of combining valid primitives, this approach can help to overcome several pitfalls in solid modeling. Within this paper, we focus on flawed or 'dirty' B-Rep models. The most direct way to address CAD model flaws is to heal or repair the model before meshing. The healing process involves identifying the type of model errors and fixing them individually. Butlin and Stops [8] listed topological and geometrical inconsistencies. The geometrical inconsistencies relate to their positions in space, while the topological inconsistencies relate to the connections or relationships among entities. Gu et al. [9] presented a visual catalog of potential flaws. Petersson and Chand [10] developed a suite of tools for the preparation of CAD geometries that are imported from IGES files and stored in the boundary representation for mesh generation; the algorithm can identify gross flaws and remove them automatically. Yang et al. [11] classified topological and geometrical flaws in CAD models and proposed a procedural method to verify 19 flaw types in STEP format and 12 types in the IGES format. Yang and Han [5] conducted a case study to investigate the typical nature of CAD model flaws. They reported the classification and frequency of each of the six most common error types that significantly increase the lead times, and they proposed a repair method based on the design history. Healing methods act either on the CAD model or on the mesh [5]. According to their approach, these methods can be classified into surface [12], volumetric [13] and hybrid [14] types. Surface-based geometry repair methods perform local modifications merging and fixing incorrect surface patches. Volumetric techniques are used to reconstruct a new global shape without flaws. However, this approach typically leads to information loss, especially at sharp features such as kinks. Hybrid methods combine the advantages of local surface healing and global volumetric healing. To this end, flaws are detected and a volumetric reconstruction is performed only in their vicinity. These methods have been used for CAD models that are represented in typical B-Rep formats (e.g., STEP and IGES) as well as for polygonal meshes [15]. Although healing and repair methods have been applied successfully in recent years, healing can still be very labor intensive and time consuming in the scope of product development. As a remedy, mesh generation techniques have been developed which have the potential to generate meshes from flawed geometric models. In this line of research, Wang and Srinivasan [16] proposed an adaptive Cartesian mesh generation method. Herein, the computational grid is created inside the domain, which then connects to the boundary. Another technique-the Cartesian shrink-wrapping technique-was presented in [17] to generate triangular surface meshes automatically for 3D flawed geometries without healing. However, to generate a mesh, an initial watertight shell (called wrapper surface) needs to be constructed. Another line of research proposed by Gasparini et al. [18] is an approach to analyze geometrically imperfect models based on a geometrically adaptive integration technique that uses different model representations, i.e. space decomposition, B-Rep, and distance fields. This approach relies on a method that was first introduced by Kantorovich [19] and that has recently been commercialized [20]. Furthermore, this approach requires computation of a well-defined distance function to the boundaries — which is non-trivial for dirty geometries, as the orientation of boundary surfaces might be incorrect or the location of the boundaries is anticipated incorrectly, e.g., due to spurious entities, or intersections. However, two main issues arise applying geometry healing: (i) In the case that the geometry is healed locally, i.e. each flaw on its own, it is almost impossible to heal all flaws. Hence, a subsequent volumetric meshing is likely to fail. (ii) If the model is healed in a volumetric sense, i.e. the model is entirely reconstructed, a valid model can be obtained. However, typically sharp features, such as edges, corners or small details are lost. The automatic assumptions which are made during the volumetric healing lead to a changed model which is likely to be not in the designer's intent.

In this work, we present an alternative computational methodology which aims at dealing robustly with dirty topologies and geometries. At its core, it utilizes the Finite Cell Method (FCM) [21,22], a fictitious domain method which uses classical linear, or higher-order finite elements. The FCM embeds the physical model into a fictitious domain which is then discretized by a simple, often axis-aligned grid. This grid does not have to conform to the boundary of the physical domain. Instead, the physical domain is recovered on the level of integration of element matrices and load vectors. A point Membership Classification (PMC) test is carried out at each integration point to determine whether it lies inside or outside the physical domain. Hence, the only information needed from the CAD model is a reliable and robust MC, which strongly reduces the geometrical and topological requirements on the validity of the geometric model. This observation allows for a new paradigm in the computational analysis: http: www.cs.technion.ac.il gershon GuIrit.

not to create an analysis-suitable model and or to derive a mesh or distance field, but rather to directly compute on geometrically and or topologically flawed models by a flaw-insensitive computational method. Thus, it is neither required to heal the flawed geometry nor to construct conforming meshes or distance fields. Instead, a PMC is constructed which is robust w.r.t. to a large number of model flaws. The point Membership Classification test can then be evaluated with a certainty at least up to a geometric magnitude of the defect itself (as, e.g., in the case of gaps). This is important because a subsequent computational analysis can then directly be carried out without healing. Moreover, the computational analysis may still deliver the necessary accuracy on those flawed models as their effect on the results of the computation remains local to the flaw itself. Only, if the local flaw lies directly in the region of interest it must be fixed. This is, however, only necessary to achieve higher accuracy — an analysis can be carried out either way.

The Finite Cell Method is a widely applicable method itself. While the original publications concerning the FCM treated linear elasticity in 2D and 3D [22], the scope of application was extended to various fields, such as elastoplasticity [23], constructive solid geometric models [24], topology optimization [25,26], local enrichment for material interfaces [27], elastodynamics and wave propagation [28-30], and contact problems [31,32]. Further developments include weakly enforced essential boundary conditions [33], local refinement schemes [34], and efficient integration techniques [35-38]. Furthermore, the concept of the FCM is independent of the underlying approximation method. It does not have to be based on hierarchical Legendre shape functions but can also be built on a spline-based approximation like in Isogeometric analysis, or spectral shape functions [39]. In this case, the fictitious domain approach is an adequate method for trimming Isogeometric analysis, as presented and analyzed, e.g., in [40-42]. In [43], an efficient method to overcome the inherent problem of bad condition numbers based on precondition is presented. Approaches very similar to the FCM have been presented more recently, like the cutFEM method [44], which builds on earlier publications of Hansbo et al. [45]. Therein, small elements are explicitly stabilized by controlling the gradients across embedded boundaries connected neighboring cells in the fictitious domain. This is different to FCM where a stabilization is achieved to a certain extent by a small but non-zero stiffness in the fictitious domain.

In this contribution, the FCM is extended in order to directly simulate a CAD model with flaws. The paper is structured as follows: Section 2 provides a brief overview over geometrical and topological flaws. The basic formulation of the FCM and the requirements of a numerical simulation on flawed geometric CAD models are given in Section 3. A robust algorithm for point Membership Classification on dirty geometries is presented in Section 4. Several numerical examples for the proposed methodology are presented and discussed in Section 5. Finally, conclusions are drawn in Section 6.

## 2 Dirty topology geometry

In this section, we provide a very short general overview of Boundary representation (B-Rep) models (Section 2.1) and necessary conditions for their validity (Section 2.2). By implication, "dirty' geometries, or topologies are models which do not meet these requirements and are therefore mathematically invalid. To describe the wide variety of different flaws (Section 2.3), we define mathematical operators (Section 2.4) and apply them to a valid B-Rep model, thereby transforming a 'valid' into a 'dirty' B-Rep model (Section 2.5). Several of these flaw operators allow introducing a control parameter &, indicating a geometric size of the respective flaws. Applying a sequence of flaw operators maps a flawless model to exactly one resulting flawed model. It is obvious that, given some flawed model, it is not possible to determine on which flawless model it could be based meaning that a class of equivalent flawless models can be associated to one 'dirty' model. Our conceptual approach therefore only assumes the existence of a flawless model that is expected to be 'close' to the 'dirty' one. This is used as the geometric basis for analysis. Further, it is to be noted that no explicit knowledge of this flawless model is required.

### 2.1 Boundary representation models

B-Rep objects are described by their boundaries. A model \(\Omega\) can consist of several sub-domains, which all describe a separate closed volumetric body \(B_{i}\).

$$
\Omega=\left\{B_{i} \quad \mid i \in\{1, \ldots, n\}\right\}
$$

![Figure 2. Example topology with n = 5 vertices, m = 7 edges, and o = 3 faces.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-2-p005.png)

*Figure 2. Example topology with n = 5 vertices, m = 7 edges, and o = 3 faces.: Example topology with n = 5 vertices, m = 7 edges, and o = 3 faces.*

with \(n\) being the number of volumetric bodies. For simplicity of presentation, we assume that a B-Rep model consists only of domain \(\Omega=B\). A B-Rep body consists of topology \(T\) and geometry \(G\) [6]:

$$
B(T, G)
$$

The topology \(T\) describes the relations or logical location of all entities (2.1.1), whereas the geometry \(G\) provides the physical location of points, consequently defining the actual shape of the model (2.1.2).

#### 2.1.1 Topology

The topology \(T\left(t, r^{\text {int }}, r^{\text {ext }}\right)\) provides the logical internal \(r^{\text {int }}=\left\{r_{i}^{\text {int }}\right\}\) and external relations \(r^{\text {ext }}=\left\{r_{i}^{\text {ext }}\right\}\)

$$
\begin{aligned} V & =\left\{v_{i}\right. \\ \mid & i \in\{1, \ldots, n\}\} \\ E & =\left\{e_{i}\right. \\ \mid & \left.i \in\{1, \ldots, m\}, e_{i}=\left(v_{\alpha}, v_{\beta}\right), v_{\alpha}, v_{\beta} \in V\right\} \\ F & =\left\{f_{i} \mid i \in\{1, \ldots, o\}, f_{i}=\left(e_{\kappa}\right)_{\kappa \in\{\alpha, \ldots, \psi\}}, \boldsymbol{n}_{i}, e_{\kappa} \in E\right\} \end{aligned}
$$

with \(n, m, o\) being the number of vertices, edges, and faces, respectively. The ordered pair of vertices \(\left(v_{\alpha}, v_{\beta}\right)\) contains the bounding vertices of an edge. A face \(f_{i}\) is described by an ordered pair containing: (i) the boundary edges, denoted by an ordered \(n\)-tuple ( \(e_{\kappa}\) ), with \(n\) being the number of boundary edges, and (ii) the respective normal vector \(\boldsymbol{n}_{i}\). In some cases, the normal vector is provided implicitly by the order of the boundary edges ( \(e_{\kappa}\) ). The external relations \(r^{\text {ext }}\) describe the global adjacency relations between the particular entities (e.g., which faces are neighbors to each other). There are various possible methods to represent the internal and external adjacency relations, or a combination of both, such as the winged edge model or the double connected edge list [6]. Thereby, the adjacency relations can be represented by graphs. Fig. 2 shows an exemplary detail of a topology consisting of three triangles. The pure external relations can, for example, be represented by the adjacency matrix \(r_{F F}^{e x_{t}}\) (see Eq. (6)). The adjacency matrices for faces and edges \(r_{F E}\) (see Eq. (7)) and for edges and vertices \(r_{V E}\) (see Eq. (8)) represent a combination of internal and external relations. \({ }^{2}\)

#### 2.1.2 Geometry

The geometry \(G\left(\left\{g_{i}\right\}\right)\) contains the geometric entities \(g_{i}\), i.e the points \(\boldsymbol{P}_{i}\), curves \(\boldsymbol{C}_{j}(\xi)\), and surfaces \(\boldsymbol{S}_{k}(\xi, \eta)\), which describe the actual physical location of the boundary and, thus, the shape of the geometry. curves and surfaces are often expressed in parametric representation:

\begin{aligned} & \boldsymbol{P}_{i}=\left(x_{i}\binom{y_{i}, z_{i}}{x(\xi)}^{\mathrm{T}}\right. \\ & \boldsymbol{C}_{i}(\xi)=\underset{z(\xi)}{y(\xi)} \end{aligned} \quad \text { e.g., } \quad \boldsymbol{C}_{i}(\xi)=N_{j}^{n \boldsymbol{z}} N_{j}(\xi) \cdot \boldsymbol{Q}_{j}

2 Please note: An entry 1 in the adjacency matrix shows which entity (row) is connected to which other entity (column). An entry 0 indicates that no direct adjacency exists.

![Figure 3. At each edge e; two boundary curves Cs, and C5, meet.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-3-p006.png)

*Figure 3. At each edge e; two boundary curves Cs, and C5, meet.: At each edge e; two boundary curves Cs, and C5, meet. At each edge ej two boundary curves C's; and CSt meet.*

\boldsymbol{S}_{i}(\boldsymbol{\xi})=\left(\begin{array}{c} x(\boldsymbol{\xi}) \\ y(\boldsymbol{\xi}) \\ z(\boldsymbol{\xi}) \end{array} \quad \text { e.g., } \quad \boldsymbol{S}_{i}(\boldsymbol{\xi})={ }_{j}^{n \boldsymbol{\eta}} N_{k} N_{j}(\xi) \cdot N_{k}(\eta) \cdot \boldsymbol{Q}_{j, k}\right.

with \(\xi \in \mathbb{R}\) and \(\boldsymbol{\xi}=(\xi, \eta) \in \mathbb{R}^{2} . N_{i}(\xi)\) denote shape functions (such as Lagrange or Legendre polynomials, B-Splines, NURBS, etc.) and \(\boldsymbol{Q}_{i}\) the associated (control-)points, which can, depending on the curve description, coincide with the geometrical points \(\boldsymbol{P}_{i}\).

Analogous to the topology, the geometry G can be represented by sets:

$$
\begin{aligned} & P=\left\{\boldsymbol{P}_{i} \mid i=\{1, \ldots, n\}\right\} \\ & C=\left\{\boldsymbol{C}_{i} \mid i=\{1, \ldots, 2 \cdot m\}\right\} \\ & S=\left\{\boldsymbol{S}_{i} \mid i=\{1, \ldots, o\}\right\} \end{aligned}
$$

where the number of points and surfaces equals the number of vertices \(n\) and faces \(o\), respectively. A special case are curves, where at each edge two adjoined faces meet, whose underlying surfaces have each their own boundary curves. Consequently, the number of curves is \(2 \cdot m\) (see Fig. 3).

#### 2.1.3 Minimal B-Rep and the STL format

The most commonly used B-Rep exchange format between CAD and analysis is STL (STereoLithography, or more expressive Standard Tessellation Language). STL can be interpreted as a minimal B-Rep format, as it Silen of est penden in dinal are of expliy separatice beer poops a geometric information in form of point coordinates is provided explicitly only for vertices, curves and surfaces are linearly interpolated. No adjacency, or 'consistency' information is provided, which makes STL quite flexible — but also particularly prone to a variety of potential flaws. The relation between faces and vertices reads:

$$
F^{S T L}=\left\{f_{i}\left|i \in\{1, \ldots, o\}, f_{i}=\left(v_{\alpha}, v_{\beta}, v_{\gamma}\right), \boldsymbol{t}_{i}, v_{\kappa} \in V,|V|=3 \cdot o\right\}\right.
$$

Note that-due to the multiple definition of vertices-STL models are, strictly speaking, topologically not valid. Furthermore, the redundancy of point definitions and normal vectors, which could be derived from the orientation of the face has an eminent impact on the required memory for storage.

### 2.2 Conditions for valid B-Rep models

Although intuitively quite apparent, it is not straightforward to define a valid B-Rep model. Patrikalakis et al. [46] provided a definition: "A B-Rep model is valid if its faces form an orientable 2-manifold without boundary". From this, several requirements can be derived, some of which are also mentioned by Mäntylä [6] and Hoffmann [47]. Topology:

- different vertices do have different coordinates (see Fig. 6a).

- One edge is shared by exactly two faces (see Fig. 4).

- Faces at one vertex belong to one surface, i.e. at a vertex it is possible to cycle through all adjacent faces such that all of the vertex edges are crossed exactly once (see Fig. 4).

![Figure 4. Vertex with adjoined edges and faces](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-4-p007.png)

*Figure 4. Vertex with adjoined edges and faces: (a) It is possible to cycle through the faces, passing each adjoined edge once. Hence, all faces belong to the same surface. (b) Not all faces belong to the same surface.*

![Figure 5. Gaps between trimmed NURBS patches of the Utah teapot.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-5-p007.png)

*Figure 5. Gaps between trimmed NURBS patches of the Utah teapot.: Gaps between trimmed NURBS patches of the Utah teapot. Picture taken from [48].*

- The orientation of faces must follow Moebius' Rule, i.e. inside and outside must be distinguishable from each other (see Fig. 6d).

Geometry:

- A curve must lie on the respective surface whose partial boundary it forms.

- Both boundary curves at one edge must coincide (see Fig. 7a).

- Surfaces must not self-intersect. From this-and from 5-it follows that curves do not self-intersect either (see Fig. 7b).

- Surfaces must not touch or intersect with other surfaces except at common edges (see Fig. 7c).

### 2.3 CAD model flaws

Model flaws can originate from different sources, such as mathematical inaccuracies, data conversion problems between different software systems, mistakes by designers, different design goals, etc. The probably most famous example of mathematical inaccuracies is the 'leaking teapot' model, as depicted in Fig. 5. The gap between spout and body of the teapot could only be avoided by more complex spline types (see, e.g., T-splines [49]), or unreasonably high polynomial degrees. The simplification results in a non-watertight geometry, a major obstacle for the interoperability between CAD and CAE. Figs. 6-8 provide an overview over the most common topological and geometrical modeling flaws.

### 2.4 Flaw operators

In the following, we will introduce several operators that perform transformations on a valid B-Rep model, allowing for a controlled imposition of different flaws. To measure the size of the flaws, we introduce an error parameter e, indicating the 'dirtiness' or inaccuracy of the model.

![Figure 6. Topological flaws.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-6-p008.png)

*Figure 6. Topological flaws.: Topological flaws.*

e1 V2 e2 f2. (a) Double vertices (b) Double edges (c) Double faces fitF (d) Wrong orientations (e) Missing faces

![Figure 7. Geometrical flaws.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-7-p008.png)

*Figure 7. Geometrical flaws.: Geometrical flaws.*

- (a) curves at common edge do not coincide

$$
(b) Surface and boundary curve self- intersect (c) Surface intersects with another surface
$$

To provide an easily understandable formulation of the operators, we consider an object-oriented B-Rep data structure. Thereby, the implementation must allow a distinction between internal and external/adjacency relations. Fig. 9 provides a UML diagram of a possible hierarchical implementation. For an introduction to the notation of the UML (Unified Modeling Language) see, e.g., [50]. Here, the external adjacency relations \(r^{\text {ext }}\) are realized at the faces, where the adjacent faces are stored in the field: adjacentFaces. All other external adjacency relations Let \(\omega^{t_{i}}\) be the B-Rep sub-part, or segment, which corresponds to a topological entity \(t_{i}\), e.g., a face, an edge, or a vertex. The segment \(\omega^{t_{i}}\) consists of all information that is needed to visualize \(t_{i}\). Hence, it must contain \(t_{i}\) and, recursively, all underlying sub-topologies and geometries that are related by respective internal adjacency relations \(r^{\text {int }}\) (see Fig. 10).

$$
\omega^{t_{i}}\left(T^{t_{i}}, G^{t_{i}}\right) \subset B
$$

![Figure 8. Hybrid flaws which consist of topological and geometrical components.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-8-p009.png)

*Figure 8. Hybrid flaws which consist of topological and geometrical components.: Hybrid flaws which consist of topological and geometrical components.*

![Figure 9. UML-diagram of a possible object-oriented B-Rep implementation.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-9-p009.png)

*Figure 9. UML-diagram of a possible object-oriented B-Rep implementation.: UML-diagram of a possible object-oriented B-Rep implementation.*

Face 0..* id: int boundaryEdges : list<Edge> normal: vector<double> adjacentFaces : list<Face> geometry: Surface Surface 0.* Edge 0.* id: int vertice : list< Vertex> geometry: curve curve 2 2 Vertex id: int geometry: point point 1

![Figure 10. B-Rep sub-part wi, which corresponds to face fi and consists of the topology Tfi and the corresponding geometry Gfi.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-10-p010.png)

*Figure 10. B-Rep sub-part wi, which corresponds to face fi and consists of the topology Tfi and the corresponding geometry Gfi.: B-Rep sub-part wi, which corresponds to face fi and consists of the topology Tfi and the corresponding geometry Gfi. B-Rep sub-part wf, which corresponds to face fi and consists of the topology Tfi and the corresponding geometry Gfi.*

) with Ti T, pint and G'i(y) being the respective topology and geometry, where = (ti) and y = (vil denote the sets of those topological and geometrical entities which are recursively related by the internal relations pint = (pi"'). Consequently, three different segments are possible: (1) vertex segments, (b) edge segments, and (c) face segments. As topological entities {Ti), a face segment, for example, contains the face itself and all associated edges and vertices. As geometric entities (j), it holds the corresponding surface with its boundary curves and corner points. Additionally, all internal relations (pin) are contained, i.e. the relations among face, boundary edges, and vertices, as well as the relations to the geometric entities. Not contained are external adjacency relations, i.e. those to neighboring faces or edges. In the following, \(\tilde{a}\) denotes the object \(a\) after the transformation and let dist \((a, b)=\inf \left\{\|a, b\|_{2}\right\}\) be the minimum Euclidean distance between two objects, e.g., the distance between the closest points on two different surfaces.

- Let Oselect be an extraction operator, which selects for a topological entity t; the corresponding segment coi from the body B.

$$
O^{\text {select }}\left(B, t_{i}\right) \mapsto \omega^{t_{i}}
$$

Note that the external relations are not extracted. Hence, the segment forgets about its logical location in the body.

- Let Ojoin beja join pperator that adds a segment co" to the body B.

2. Let \(O^{\text {join }}\) be (a join pperator that adds a segment \(\omega^{t_{i}}\) to the body \(B\).

- Let OshallowCopy be a shallow copy operator that copies an arbitrary entity a;. For a more detailed description of the object-oriented concept of 'shallow' and 'deep' copying see, e.g., [51]. a; can be a topological entity ti, a geometrical entity gi, or an internal ri" or external relation rext

$$
O^{\text {shallowCopy }}\left(a_{i}\right) \mapsto \tilde{a}_{i}, \text { where } \tilde{a}_{i}:=a_{i}
$$

The ':=' in (19) is to be understood as the shallow copy assignment, according to [51]. Note that the new object is distinguishable from the old object, e.g., by an updated id, or, in the context of object-oriented programming, by a different memory address. Yet, it still uses the same references to other objects as the original segment.

- Let OdeepCopy be an internal deep copy operator [51] that performs a deep copy operation on a segment cli. To this end, a shallow copy operation is carried out on all corresponding topological and geometrical entities, as well as the internal adjacency relations.

\begin{aligned} & \text { ll as the internal adjacency relations. } \\ & \left.O^{\text {deepCopy }} \underset{\omega^{t_{i}}}{\omega^{t_{i}}} \mapsto \tilde{\omega}^{t_{i}}\left(\tilde{T}^{t_{i}}, \tilde{G}^{t_{i}}\right), \text { with } \tilde{T}^{t_{i}} \tilde{\tau}, \tilde{\rho}^{\text {int }}\right), \tilde{\tau}_{i}:=O^{\text {shallowCopy }}\left(\tau_{i}\right), \\ & \tilde{\rho}_{i}^{\text {int }}:=O^{\text {shallowCopy }}\left(\rho_{i}^{\text {int }}\right) \forall \tau_{i}, \rho_{i}^{\text {int }} \in T^{t_{i}}, \end{aligned}

$$
\tilde{G}^{t_{i}}(\tilde{\gamma}), \tilde{\gamma}_{i}:=O^{\text {shallowCopy }}\left(\gamma_{i}\right) \forall \gamma_{i} \in G^{t_{i}}
$$

Note that the deep copied segment \(\omega^{t_{i}}\) has no information about its logical location in \(B\), i.e. it has no external adjacency relations, and that all internal relations are updated to reference the new topological and geometrical entities.

- Let Odelete be a deletion operator that deletes a face fi and its related geometry gli C G consisting of the underlying surface S; and the corresponding boundary curves {Ci). Thereby, the characteristic size of the resulting opening must not exceed a given, e.g., user-defined minimal accuracy &. Let 8 be the diameter of the largest possible inscribed sphere of the surface S; to be deleted.

$$
O^{\text {delete }}\left(B, f_{i}, g^{f_{i}}\right) \mapsto \tilde{B}(\tilde{T}, \tilde{G}) \text {, where } \tilde{F}=F \backslash f_{i} ; \tilde{G}=G \backslash g^{f_{i}}, \delta<\varepsilon
$$

Note that, as a deletion of an edge, or vertex would lead to an uncontrollable cascade of deletions of superior entities, only a face deletion is allowed in this context. A B-Rep model with a deleted edge or node without deletion of referencing faces would not even be readable and is not considered in our investigation.

- Let explode be an operator that removes all external relations rext from a body B. This can be achieved by extracting (17), copying (20), and joining (18) all face segments @ fi Vfi e F. The resulting body B is then described by independent topological sup-parts segments cy)

$$
O^{\text {explode }}(B)=O^{\text {join }} B^{\circ}, O^{\text {deepCopy }} O^{\text {extract }}(B, F) \mapsto \tilde{B}, \text { where } \tilde{r}^{\text {ext }}=\emptyset
$$

where \(B^{\circ}\) is an empty body.

O^{f l i p}\left(\begin{array}{l} ( \\ f_{i} \end{array} \mapsto \tilde{f}_{i}, \text { where } \tilde{f}_{i}=\left(\left(e_{\kappa}\right), \tilde{\boldsymbol{n}}_{i}=-1 \cdot \boldsymbol{n}_{i}\right)\right.

- Let Omove be a geometric move operation that moves the point Pi within the range e. Additionally, all adjoined surfaces and curves are adapted consistently such that they form \(a_{2}\)-manifold without boundaries ce El operation. This involves the following adaptions to the adjoined surfaces SPi = (S!' ) and curves

- The resulting point P; must again lie on the altered surfaces SPi and curves CPi.

- All pairs of the resulting adjoined surfaces (SA, 5g) must again meet at their common edge curve exConsequently, the two respective boundary curves (CA, C%) must coincide.

The latter condition is omitted in the case of an already broken topology, where an edge no longer has two adjoined faces surfaces. ()

$$
\left(\begin{array}{l} \\ \sim \end{array}\right)
$$

$$
O^{\text {move }}\left(\boldsymbol{P}_{i}, G\right) \mapsto \tilde{G}, \text { where } 0<\operatorname{dist} \quad \boldsymbol{P}_{i}, \tilde{\boldsymbol{P}}_{i}<\varepsilon,
$$

\begin{aligned} & \quad \exists \boldsymbol{\xi}: \tilde{\boldsymbol{S}}_{i}^{\tilde{\boldsymbol{P}}_{i}}(\boldsymbol{\xi})=\tilde{\boldsymbol{P}}_{i} \forall \tilde{\boldsymbol{S}}_{i}^{\tilde{\boldsymbol{P}}_{i}}, \exists \zeta: \tilde{\boldsymbol{C}}_{i}(\zeta)=\tilde{\boldsymbol{P}}_{i} \forall \tilde{\boldsymbol{C}}_{i}^{\tilde{\boldsymbol{P}}_{i}}, \\ & \text { and }( \\ & \quad \text { dist } \tilde{\boldsymbol{C}}_{A}^{e_{k}}, \tilde{\boldsymbol{C}}_{B}^{e_{k}}=0 \forall\left(\tilde{\boldsymbol{S}}_{A}^{e_{k}}, \tilde{\boldsymbol{S}}_{B}^{e_{k}}\right) \text { at } v_{i} \end{aligned}

- Let Odetach be a geometrical operator that detaches two adjacent surfaces, S; and Sj, which meet at the edge ek (see Fig. 7a). To this end, one surface S; and its respective boundary curve Cek at ek are changed. Again, the characteristic size of the potentially resulting opening must not exceed 8.

$$
\begin{gathered} O^{\text {detach }}\left(G, e_{k}\right) \mapsto \tilde{G}, \text { wheye dist } \tilde{\boldsymbol{S}}_{i}, \tilde{\boldsymbol{C}}_{\boldsymbol{S}_{i}}^{e_{k}}(\xi)=0, \\ 0 \leq \operatorname{dist} \boldsymbol{C}_{\boldsymbol{S}_{i}}^{e_{k}}, \tilde{\boldsymbol{C}}_{\boldsymbol{S}_{i}}^{e_{k}}(\xi)<\varepsilon \forall \xi \in\left[\xi_{a}, \xi_{b}\right] \end{gathered}
$$

$$
with \(\left[\xi_{a}, \xi_{b}\right]\) being the respective interval on which the boundary curve is defined.
$$

- Let Ointersect be a geometric operator that alters a surface S;(E) such that it touches or intersects with another surface S;(n) apart from common edges. Note that we assume that there is no intersection in the original

model, according to the definition of a valid B-Rep model. \begin{aligned} & O^{\text {intersect }}\left(\boldsymbol{S}_{i}(\boldsymbol{\xi})\right)\left(\tilde{\boldsymbol{S}}_{i}(\boldsymbol{\xi}),\right. \text { where } \\ & \quad \exists(\boldsymbol{\xi}, \boldsymbol{\eta}): \operatorname{dist} \tilde{\boldsymbol{S}}_{i}(\boldsymbol{\xi}), \boldsymbol{S}_{j}(\boldsymbol{\eta})=0 \wedge \operatorname{dist} \tilde{\boldsymbol{S}}_{i}(\boldsymbol{\xi}), \tilde{\boldsymbol{C}}_{k}^{\tilde{\boldsymbol{S}}_{i}}>0 \\ & \quad \forall \tilde{\boldsymbol{C}}_{k}^{\tilde{\boldsymbol{S}}_{i}} \in \Gamma^{\tilde{\boldsymbol{S}}_{i}}, i \neq j \end{aligned} with \(\Gamma^{\tilde{\boldsymbol{S}}}{ }_{i}\) being the set of boundary curves of \(\tilde{\boldsymbol{S}}_{i}\).

A special case of intersections are self-intersections:

$$
O^{\text {self Intersect }}\left(\boldsymbol{S}_{i}(\boldsymbol{\xi})\right) \mapsto \tilde{\boldsymbol{S}}_{i}(\boldsymbol{\xi}), \text { where } \exists(\boldsymbol{\xi}, \boldsymbol{\eta}): \text { dist } \tilde{\boldsymbol{S}}_{i}(\boldsymbol{\xi}), \boldsymbol{S}_{i}(\boldsymbol{\eta})=0, \boldsymbol{\xi} \neq \boldsymbol{\eta}
$$

### 2.5 Application of flaw operators

We now continue with the definition of a flawed model. To this end, we apply the flaw operators defined in Section 2.4 onto a valid B-Rep model. The 'dirtiness' of the model is then defined by &. It should be mentioned that, for models that are drafted by a real-life CAD system, flaws do not necessarily originate from these operators, yet most flawed models can equivalently be created by a sequence of these operators.

Let \(B(T, G)\) be a valid flawless B-Rep body. Note that operators acting on the body is to be understood as acting on a segment \(\omega^{t_{i}}\), or single topological, or geometrical entity, or relation.

- Single topological entities t; and their corresponding segments c,; can be copied and added to B with a combination of the extraction (17), the deep copying (20), and the joging (18) operator:

$$
\tilde{B}(\tilde{T}, \tilde{G}):=O^{\text {join }} \quad B(T, G), O^{\text {deepCopy }} O^{\text {extract }}\left(B(T, G), t_{i}\right)
$$

The resulting B-Rep model is invalid as it has multiple entities (refer to Figs. 6a, 6b, and 6c), which violates condition 1. As an example, consider the STL format where each triangle (re-)defines its corner points. Also, multiply defined faces surfaces appear frequently in free form CAD models, which leads to a touching intersection of the surfaces (refer to Fig. 8c).

- Application of the deletion operator (21) on a face fi:

$$
\tilde{B}(\tilde{T}, \tilde{G}):=O^{\text {delete }} B, f_{i}, g_{f_{i}}
$$

The deletion of a face violates condition 2 (see Fig. 6e). Thereby, the size of the resulting opening restricted to be smaller than &.

- Application of the explosion operator (22):

$$
\tilde{B}(\tilde{T}, \tilde{G}):=O^{\text {explode }}(B(T, G))
$$

Most B-Rep models are constructed from independent surfaces, which are later joined into a (hopefully) valid B-Rep model. This join operation corresponds to the inverse of the explosion operation. It is yet well known that a strict "join'-operation is not necessarily possible (or maybe not feasible) e.g., in case of an intersection of two NURBS surfaces [48]. Also, STL models are constructed by independent triangles. Such models violate the topological conditions 1, 2, and 3. Geometrically, they can still form a closed 2-manifold without boundaries. However, these models are very prone to a variety of different flaws, as no external adjacency relations are provided explicitly.

- Application of the flip operator (23):

$$
\tilde{B}(\tilde{T}, G):=O^{f l i p}(B(T, G))
$$

However, this error also appears quite frequently if the normal is given explicitly, e.g., in the case of STL.

- Application of the move operator (24):

$$
\tilde{B}(T, \tilde{G}):=O^{\text {move }}(B(T, G))
$$

However, the orientability can be lost (see condition: 4). As an example, consider a point \(\boldsymbol{P}_{i}\) on surface \(\boldsymbol{S}_{j}\), which is close to surface \(\boldsymbol{S}_{k}\) with distance \(\operatorname{dist}\left(\boldsymbol{P}_{i}, \boldsymbol{S}_{k}\right)<\varepsilon\). A movement then can lead to an intersection of the two surfaces. This violates condition 8 (see Fig. 7c).

- Application of the detach operator (25):

$$
\tilde{B}(T, \tilde{G}):=O^{\text {detach }}(B(T, G))
$$

The resulting model violates condition 6. This is likely to happen at the intersection of free-form surfaces. The boundary curves would require unreasonably high polynomial degrees to perfectly coincide. Possible flaws can e.g., be openings or intersections (see Figs. 7a and 7c). As an example, consider the leaking Utah teapot.

- Application of the intersection operator (26):

$$
\tilde{B}(T, \tilde{G}):=O^{\text {intersect }}(B(T, G))
$$

The resulting model may violate conditions 7 or 8. Apart from gaps, intersections frequently appear at patch boundaries as well (see Fig. Ta). intersections can also occur if two surfaces are too close to each other. In this case, they additionally violate Moebius' Rule 4 (see Figs. 7c and 7b). A special case are overlaps, where two surfaces touch each other (see Fig. 8b).

- Application of the copy (20) and the move operators (24) to a single face fi:

\begin{aligned} & \tilde{\omega}^{f_{i}}:=O^{\text {deepCopy }} O^{\text {extract }}\left(B, f_{i}\right) \\ & \breve{\omega}^{f_{i}}:=O^{\text {move }}\left(\boldsymbol{P}_{j} \in\left(\tilde{\omega}^{f_{i}}, \tilde{G}^{t_{i}}\right)\right. \\ & \tilde{B}(\tilde{T}, \tilde{G}):=O^{\text {join }} B, \breve{\omega}^{f_{i}} \end{aligned}

This chain of operations allows to create offsets and artifacts, i.e. entities which do not belong to the outer hull and lead to a violation of the conditions 3 and 2 (see Figs. 8d and 8e).

- Application of the explosion (22) and move operators (24):

$$
\begin{aligned} \tilde{B}(\tilde{T}, \tilde{G}) & :=O^{\text {explode }}(B) \\ \breve{B}(\tilde{T}, \breve{G}) & :=O^{\text {move }}\left(\tilde{\boldsymbol{P}}_{i} \in \tilde{G}, \tilde{G}\right) \end{aligned}
$$

Starting from an exploded model, moving one or more points can lead to various common flaws-such as gaps, intersections, or overlaps (see Figs. 8a, 8c, 8b). As many B-Rep modeling tools work with exploded models, i.e. with independent surfaces, these flaws appear very commonly, particularly at patch boundaries. Also, the STL format stores a body with independent triangles.

Note that, independent of the performed operations, it is imperative for the presented method that the size of all openings and gaps is restricted to be smaller than a pre-defined &. This is required not only for each individual flaw operation but also for the resulting model after a sequence of flaw operations, e.g., a sequence of individual moves of a segment. a simulation model either impossible or invalid. The necessity to heal the flaws can neither be circumvented by meshing, as in the classical FEM, nor by a direct simulation as in IGA. It is, however, possible to compute 'dirty' a sing, in made asical mersible or invalid. Theisal to he The resulting flawed models are invalid in a mathematical sense, which renders a subsequent conversion into models directly with an embedded domain method such as the Finite Cell Method (Section 3). To this end, we construct a specially adapted point Membership Classification test (Section 4) which is blind to flaws up to a characteristic size 8.

## 3 Finite cell method

The Finite Cell Method is a higher order fictitious domain method. However, the approach presented within this paper does not rely on higher-order elements. Hence, it can be also applicable for linear fictitious domain methods. FCM offers simple meshing of potentially complex domains into a structured grid of, e.g., cuboid cells without compromising the accuracy of the underlying numerical method. For completeness of this paper, the basic concepts are briefly introduced in this section. We restrict ourselves to linear elasticity — emphasizing however, that the FCM has been extended to more general partial differential equations [52-55].

![Figure 11. The concept of the Finite Cell Method [56].](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-11-p014.png)

*Figure 11. The concept of the Finite Cell Method [56].: The concept of the Finite Cell Method [56].*

$$
t = 0on anu a = 0.0 Sfict IN + Su=Sphy UNfict → Siphy = 1.0
$$

### 3.1 Basic formulation

In the Finite Cell Method, an n-dimensional open and bounded physical domain \(\Omega_{\text {phy }}\) is embedded in a fictitious domain \(\Omega_{\text {fict }}\) to form an extended domain \(\Omega_{\cup}\), as illustrated in Fig. 11 in two dimensions. The resulting domain \(\Omega\) has a simple shape which can be meshed easily, without conforming to the boundary of \(\Omega_{p h_{y}}\). The weak form of the equilibrium equation for the extended domain Su is defined as

$$
\int_{\Omega \cup}[\mathbf{L v}]^{T} \alpha \mathbf{C}[\mathbf{L u}] \mathrm{d} \Omega=\int_{\Omega \cup} \mathbf{v}^{T} \alpha \mathbf{f} \mathrm{~d} \Omega+\int_{\Gamma_{N}} \mathbf{v}^{T} \overline{\mathbf{t}} \mathrm{~d} \Gamma
$$

where \(\mathbf{u}\) is a displacement function, \(\mathbf{v}\) a test function, \(\mathbf{L}\) is the linear strain operator, and \(\mathbf{C}\) denotes the elasticity matrix of the physical domain \(\Omega_{\text {phy }}\), yet extended to \(\Omega_{\cup}\). \(\mathbf{f}\) and \(\overline{\mathbf{t}}\) denote the body load and the prescribed tractions on the Neumann boundary, respectively. The indicator function \(\alpha\) is defined as

$$
\alpha(\mathbf{x})=\left\{\begin{array}{ll} 1 & \forall \mathbf{x} \in \Omega_{p h y} \\ 10^{-q} & \forall \mathbf{x} \in \Omega_{f i c t} \end{array},\right.
$$

In the limiting case of q → ∞, the standard weak form for an elasticity problem on Sphys is obtained. In practical applications, a sufficiently large q = 6..10 (see [21,22]) is chosen, introducing a modeling error to the formulation [57], which yet stabilizes the numerical scheme and controls the conditioning number of the discrete equation system — see [43] for a detailed analysis. Sfict is then discretized in 'finite cells' of simple shape (rectangles or cuboids). In the context of this paper, we assume for simplicity a uniform grid of finite cells, yet note that generalizations to locally refined grids [58,59] and unstructured meshes [60-62] have been studied extensively.

### 3.2 Geometry treatment

In FCM, the physical domain \(\Omega_{\text {phys }}\) (i.e. the geometry) is recovered by the discontinuous scalar field \(\alpha\). Consequently, the complexity of the geometry is shifted from the finite elements to the integration of the element matrices and load vectors, which imposes less geometrical requirements on the model. It is in fact sufficient to provide a robust point Membership Classification (PMC), i.e. for every point \(x \in \mathbb{R}^{n}\), it must be possible to decide whether it is inside or outside of \(\Omega_{\text {phys }}\). This implies that \(\Omega_{\text {phys }}\) must have a mathematically valid description. Due to the discontinuity of \(\alpha\), the integrands in cut cells need to be computed by specially constructed quadrature rules, see, e.g., [35,38,63] for a recent overview of possible schemes. To perform a suitable integration, the domain is approximated by a space-tree \(T R_{\text {int }}\). The leaves of \(T R_{\text {int }}\) are called integration leaves \(c_{\text {int }}\). Additional information, such as explicit surface descriptions are only needed for the application of boundary conditions as well as for post-processing (see Section 3.3).

### 3.3 Boundary conditions

Neumann boundary conditions are applied according to Eq. (37) in an integral sense on the boundary \(\Gamma_{N}\). Homogeneous Neumann conditions (i.e. zero traction) require no treatment, as they are automatically satisfied by setting \(\alpha=0\) or, in an approximate sense, to a small value in \(\Omega_{\text {fict }}\). As the boundary of the physical model typically does not coincide with the edges/faces of the finite cell mesh, Dirichlet boundary conditions need to be enforced also in a weak sense. To this end, several methods have been adopted, such as the penalty method, Nitsche's method, or Lagrange Multipliers [33,64-66]. For the integration of Dirichlet and inhomogeneous Neumann boundary conditions, an explicit surface description is needed. This can be of poor quality. For the enforcement of Neumann boundary conditions, however, a surface without multiple faces surfaces or large overlaps is required, as these flaws would introduce physically modified boundary conditions (i.e. additional loads, heat sources, etc.). To this end, we propose the following automatable method to convert a 'dirty' surface into a surface without multiple entities or overlaps:

- Triangulate the respective surface (if not already provided, e.g., with STL).

- Get the intersection points between the surface mesh and the element boundaries.

- Create an element-wise point cloud from the intersection points and respective triangle corner points.

- Perform an element-wise Delaunay triangulation on the respective point cloud.

The resulting element-wise triangular meshes are used only for integration and can consequently be independent of each other. Note that the requirements to these local surface meshes are by far less restrictive than they would be for a surface mesh as a starting point for volume mesh generation. Note that a potential triangulation of the surface will cause an approximation error.

## 4 Robust point membership classification for flawed CAD models

As explained in Section 3, the only geometric information required to setup the system matrices for the Finite Cell Method is an unambiguous statement about the location of a point, i.e whether it lies inside or outside of the domain of computation. Considering flawed CAD models (e.g., with undesired openings), the concept of 'inside' or 'outside' is fuzzy — at least up to the characteristic size of the flaw e. In this section, we present a robust point Membership Classification method for 'dirty' STL B-Rep models. The presented approach is, however, not restricted to STL models, and it can easily be extended to other boundary representations.

### 4.1 Point membership classification for valid CAD models

PMC algorithms are fundamental and extensively used operations, e.g., in computer graphics, computer games, and in geoinformatics [67]. For different geometric representations, various PM algorithms exist. For CSG models, a point is classified against all the underlying primitives and the resulting Boolean expressions (see [24]). Ray casting [67] is often used for boundary representation models. Further variants are approximation-tree-based algorithms [68], point cloud methods [69], sign of offset [70], and the swath method [71]. As the space-tree based approximation and the ray-casting are needed in the following, these aspects will be explained in more detail:

- Ray casting: The ray casting method is an efficient and suitable algorithm for general polytopes, and it is extensively used in computational graphics, e.g., for depth maps. To classify a given point with respect to a geometric model, a ray is shot in an arbitrary direction and the intersections with the boundary are counted The parity (even, or odd) of intersections then provides information on whether the point lies inside or outside. For flawless models, ray-casting is accurate. For flawed CAD models, however, ray casting delivers no reliable statement about the point's domain membership, as almost all flaws influence the parity of intersections

- Space-tree based PMC: For the tree-based PMC, the domain is discretized by a space-tree TRint, with leaves Coeo. Leaves intersected by the surface are marked as cut. Subsequently, a flood-fill algorithm is applied to the leaves Ceo. Starting from a seed point, whose domain membership is known, all connected leaves are marked as inside or outside, respectively. A challenge in this methodology is posed only by undesired openings or unintentional gaps. In these cases, a too fine approximation with leaves smaller than the size of the flaws would cause the flood-fill algorithm to mark the entire domain as inside or outside. Furthermore, despite its robustness against most flaws, the octree TRint gives only a coarse step-wise approximation of the geometry.

### 4.2 General approach for flawed models

The presented PM method combines the robustness of space-tree approximation with the accuracy of ray-casting. The general approach works as follows:

- The CAD model is approximated by a watertight space-tree TReo. Watertightness is imperative to ensure that the subsequent flood-fill can distinguish between inside and outside.

- A flood fill algorithm is applied on TReo to mark all connected points as inside and outside, respectively. This yields a filled space tree TRgeo. Remark: For all points that are not on cut leaves, the approximation tree TReo can be used as fast, efficient, and accurate PMC.

- An additional ray-casting is only carried out for points lying inside the cut boundary leaves — in order to approximate the structure more precisely.

Step 1 and Step 3 will now be described in more detail. For a description of the well-known flood fill algorithm in step 2 we refer to, e.g., [72].

### 4.3 Watertight space tree approximation

To ensure that the approximation space-tree \(\widehat{T R}_{\text {geo }}\) is watertight, the size of the smallest leafs \(d_{\text {cgeo }}\) must not undercut the characteristic size of the largest gap/opening \(\varepsilon_{\text {gap }}\).

$$
d_{c_{\text {geo }}}>\varepsilon_{\text {gap }}
$$

\(\varepsilon_{\text {gap }}\) is typically not known apriori and is determined by an iterative decrease of the cell size, until the subsequent fill algorithm fills the entire domain. From this, it follows that the maximal partitioning depth \(n_{\text {max }}\) of \(\widehat{T R}\) geo is bounded by the ratio of domain size \(d_{\text {domain }}\) of the tree \(\widehat{T R}_{\text {geo }}\) to the dimension of the gaps/openings \(\varepsilon_{\text {gap }}\) :

$$
n_{\max }<\log _{2} \frac{d_{\text {domain }}}{\varepsilon_{\text {gap }}}
$$

This limitation might allow, depending on the size of the gaps/openings only a very coarse approximation of the true geometry (see Fig. 25). Concerning all other types of considered flaws, a test using the space tree \(\widehat{T R}_{\text {geo }}\) is robust. Note that the reconstruction tree can be set up for an arbitrary flaw size \(\varepsilon_{\text {gap }}\), as long as at least one inner cell can be detected. The quality of the result will then only be dependent on the secondary PMC test (see Section 4.4). Note that, generally, the space-trees \(T R_{i n_{t}}\) and \(\widehat{T R}_{\text {geo }}\) are distinct. While \(T R_{i n_{t}}\) is constructed in order to numerically integrate the discontinuous element matrices for finite cells (see Section 3), the purpose of \(\widehat{T R}_{\text {geo }}\) is merely to support the point Membership Classification of the integration points. After the surface is approximated by the space tree, the flood fill algorithm [72] can be applied to mark connected regions. Fig. 13 shows the octree approximation of a simple example (Fig. 12), which has several typical flaws. The size of the opening \(\varepsilon_{\text {gap }}\) allows a maximum subdivision level of \(n_{\text {max }}=7\). Hence, the ratio of the largest gap to overall size is in the range of:

$$
\frac{1}{256}<\frac{\varepsilon_{\text {gap }}}{d_{\text {domain }}}<\frac{1}{128} .
$$

### 4.4 Point membership classification on cut leaves

The space-tree \(\widehat{T R}_{\text {geo }}\) represents the surface only very roughly and, thus, cannot be used for a precise numerical analysis. Hence, in order to improve the representation of the boundary, an additional PMC using ray casting is carried out on cut leaves. Let us first assume that the model is flawless (see Fig. 14a). Then, the ray test for any integration point in an integration leaf \(c_{\text {int }}\) yields a unique result without ambiguity, independent of the direction of the ray. In case of a flawed surface, the result may be ambiguous, depending on the selected direction of the ray (Fig. 14b-f). To handle this problem, we test rays in different directions, more precisely to the midpoints of all neighboring non-cut cells, which restricts the intersection tests to be carried out in the vicinity of the integration point and guarantees that various directions are queried. Hence, the probability for a correct result is increased. The PMC is then decided 'following the vote of the majority'. Clearly, this 'vote' can be wrong w.r.t. the (in general unknown) flawless model. This wrong decision results in an integration error for the computation of element matrices. In a mathematical sense, we are performing a 'variational crime' (see, e.g., [73]). For geometrically small flaws, the smallness of this integration error can be readily assumed-as, by construction of the two-stage PMC, it can only occur in the smallest leaf \(c_{\text {geo }}\) cut by the surface.

![Figure 12. Example of an STL model with typical flaws.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-12-p017.png)

*Figure 12. Example of an STL model with typical flaws.: Example of an STL model with typical flaws.*

wrongly oriented facet

![Figure 13. Octree approximation of the embedded tetrahedral domain. The outer domain (blue) is separated by the cut leaves (red) from the](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-13-p017.png)

*Figure 13. Octree approximation of the embedded tetrahedral domain. The outer domain (blue) is separated by the cut leaves (red) from the: Octree approximation of the embedded tetrahedral domain. The outer domain (blue) is separated by the cut leaves (red) from the inner domain (gray). The subdivision level is nmax = 7. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)*

We can even bound this error by bracketing, i.e. by solving the elasticity problem (23) - once under the assumption that all ambiguous integration points are inside, and once assuming them outside of the domain of computation (see Section 4.5 and Example 5.1), thus ensuring that the approximation quality of the method is not corrupted.

Note that also other possibilities for the secondary PM test can be applied, such as ray-casting in only a few, or just one direction, which will lead to a significant speedup but increases the probability of wrong results. Another possibility lies in the combination with a MC test based on point clouds, as this test is sensitive to other types of flaws, such as wrongly oriented normals, or intersections.

![Figure 14. Multiple ray casting for different flaws (red](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-14-p018.png)

*Figure 14. Multiple ray casting for different flaws (red: cut leafs, gray: inside, blue: outside). In these examples (d) and (f) would lead to indifferent results. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)*

### 4.5 Parameter study on the influence of the gap size

As stated in Section 2.5 a flawed model has, in general, no mathematically valid solution. Therefore it is not possible to define an 'error' of the computed approximation w.r.t. an exact solution. Yet, in order to judge the quality we compare for a simple example energies of approximate and reference solution in dependence of the size of a flaw in the B-Rep model. In particular, we investigate the influence of the largest gap size \(\varepsilon_{\text {gap }}\) on the internal strain energy for a cube with the dimensions \(1 \times 1 \times 1\) loaded under self-weight. The cube is clamped at the bottom. It is embedded in \(9 \times 9 \times 9\) elements employing integrated Legendre polynomials of degree \(p=3\). The B-Rep model of the cube consists of twelve triangles. One triangle is not properly connected to two of its neighbors resulting in a flawed model with a gap of characteristic size \(\varepsilon_{\text {gap }}^{i}\) (see Fig. 15). The size of the gap limits the maximum subdivision depth of the reconstruction tree, meaning that more refined trees would lead to a non-watertight boundary of the tree (see Section 4.3). The embedding domain used for the reconstruction tree has the dimension \(1.6 \times 1.6 \times 1.6\). The quality of The embedding domain used for the reconstruction tree has the dimension \(1.6 \times 1.6 \times 1.6\). The quality of reconstruction not only depends on the depth of the tree but also on the relative position of the domain of computation (the cube) and the tree. This influence is studied by gradually 'shifting' the origin \(x_{0, \text { beta }}\) of the cube along a diagohal in space:

with B = 0...3. Fig. 16 shows two different reconstruction trees for different origin positions. Fig. 17 shows the influence of the characteristic size of the gap \(\varepsilon_{\text {gap }}\) on the error in the internal energy. The abscissa depicts the characteristic size of the gap compared to the unit length of the cube in percent. The values correspond to the respective maximum subdivision depths \(n_{\text {max }}^{i}=9 \ldots 3\) resulting from gap sizes \(\varepsilon_{\text {gap }}^{i}=\frac{1.6}{2^{n_{\text {max }}^{i}}}\) from left to right. The ordinate shows the deviation of the internal strain energy \(U\) to the reference energy \(U_{r e f}\) in percent. The reference energy \(U_{\text {ref }}\) is computed on a flawless model. Accurate results in energy are obtained even for large

![Figure 15. Parameter study on a unit cube](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-15-p019.png)

*Figure 15. Parameter study on a unit cube: (a) Characteristic gap size §gap- (b) Reconstruction tree on the flawed geometry. (a) Characteristic gap size Egap· (b) Reconstruction tree on the flawed geometry.*

![Figure 16. Cut through two reconstruction trees for different gap sizes, consequently maximum subdivision depths and for different origin](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-16-p019.png)

*Figure 16. Cut through two reconstruction trees for different gap sizes, consequently maximum subdivision depths and for different origin: Cut through two reconstruction trees for different gap sizes, consequently maximum subdivision depths and for different origin (a)Egap=0.2, max=3, shift byB=0.(b) Egap=0.0031, nmax=9, shift by B= 3.*

gap sizes of up to 20% of the domain length. The quality of the solution is confirmed by Fig. 18, showing a plot of principle stresses of the reference solutions and approximate solutions for two gap sizes.

Although this study supports the quality of the presented approach, it cannot guarantee limitation of an error in energy of even of local solution quantities in general situations. They strongly depend on the complexity of the model and the amount and type of flaws. A crucial factor is also the location of the flaw. If it is located in highly stressed regions, the influence will be bigger than if it were located in regions of low stress. It remains to an engineer to judge the feasibility of the solution.

## 5 Numerical examples

To demonstrate the accuracy and robustness of the proposed approach, three examples are presented. The first simple example serves to verify the proposed method. To this end, a plate with a hole is simulated and compared to a flawless reference solution. The complex screw in the second example proves the applicability for sophisticated defective CAD models. Again, a flawless reference model was available. The last example is an engine bracket taken

![Figure 17. Relative deviation of energies depending on the gap size for different positions of the cube.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-17-p020.png)

*Figure 17. Relative deviation of energies depending on the gap size for different positions of the cube.: Relative deviation of energies depending on the gap size for different positions of the cube.*

![Figure 18. Principal stresses for the flawless model (a) and gap sizes of Egap = 2.5% (b) and Egap = 20% (c).](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-18-p020.png)

*Figure 18. Principal stresses for the flawless model (a) and gap sizes of Egap = 2.5% (b) and Egap = 20% (c).: Principal stresses for the flawless model (a) and gap sizes of Egap = 2.5% (b) and Egap = 20% (c).*

directly from engineering practice. This model is a perfect example of a flawed geometry, as many NURBS-patches do not fit together. An attempt to mesh the model showed that 337.544 triangles had a free edge, i.e. are flawed.

### 5.1 Example 1: Thick-walled plate with circular hole

As a classical benchmark for 3D problems, we choose the thick-walled plate with four circular holes [21]. The Young's modulus is set to \(E=10000.0 \mathrm{~N} / \mathrm{mm}^{2}\) and the Poisson's ratio to \(v=0.30\). The plate is loaded with a The domain is discretized into \(10 \times 10 \times 1\) finite cells employing integrated Legendre polynomials as basis functions. The background grid and the qualitative displacement are depicted in Fig. 22. A convergence study was carried out for \(p\)-refinement using \(p=1 \ldots 6\). To measure the accuracy of the approach, the strain energy is computed and passed on to the reference solution \(u_{e_{x}}\), which was computed with an extensive boundary-conforming Fig. 24 plots the strain energy for the different polynomial degrees. Note that the relative error in the strain energy can only be computed for the valid model, as this is the only possible basis to compute a reference solution.

* 4.0 mm in = 100.0 N mm' t = 1.0mm r = 1.0 mm 4.0 mm O O O O

![Figure 19. Thick-walled plate with circular hole under surface load.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-19-p021.png)

*Figure 19. Thick-walled plate with circular hole under surface load.: Thick-walled plate with circular hole under surface load.*

![Figure 20. Flawed B-Rep model containing several gaps, intersections, offsets, and multiple entities.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-20-p021.png)

*Figure 20. Flawed B-Rep model containing several gaps, intersections, offsets, and multiple entities.: Flawed B-Rep model containing several gaps, intersections, offsets, and multiple entities.*

![Figure 21. Flaw details](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-21-p021.png)

*Figure 21. Flaw details: (a) gap (b) intersection (c) offset of the top surface.*

$$
(a) Gap (b) Intersection (c) Offset
$$

In Fig. 24, it can be seen, that both models converge to a slightly different value. This is, of course, to be expected — as both models have a slightly different shape and volume. The good convergence of the flawed model is attributed to the fact that errors due to flaws are very localized. This is an inherent property of the proposed methodology.

A detailed investigation of the flawed geometry can be carried out based on the ray-casting tests, which are applied on the integration cells (see Section 4.4). As an example, we consider a polynomial degree of p = 3. For

![Figure 22. Approximation tree TRaco with subdivision depth max = 5.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-22-p022.png)

*Figure 22. Approximation tree TRaco with subdivision depth max = 5.: Approximation tree TRaco with subdivision depth max = 5. Approximation tree TRgeo with subdivision depth max = 5.*

![Figure 23. Displacement and finite cell discretization.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-23-p022.png)

*Figure 23. Displacement and finite cell discretization.: Displacement and finite cell discretization.*

![Figure 24. Strain energy norm for polynomial degrees p = 1...6.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-24-p022.png)

*Figure 24. Strain energy norm for polynomial degrees p = 1...6.: Strain energy norm for polynomial degrees p = 1...6.*

Polynomial degree

the integration of the system matrices, 6406920 points need to be evaluated. From these, a total number of 2225 641 points ( \(\sim 35 \%\) ) are lying on cut cells. Typically, 12 to 18 ray-castings are carried out on each of these points. 1503636 points ( \(\sim 23 \%\) ) are ambiguous, i.e. at least one ray delivers a different result compared to the majority. In 656009 cases ( \(\sim 10 \%\) ), a 'vote for the majority' is not possible, as the number of rays voting for inside and outside is equal. This large amount is mainly due to the many double entities. To compute the upper and lower boundaries of the energy norm, two additional simulations were carried out-once with all ambiguous integration

![Figure 25. Cut through an octree approximation TRgeo, with (a) too small cut leaves (geo (black), so that all (non cut) leaves are marked as](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-25-p023.png)

*Figure 25. Cut through an octree approximation TRgeo, with (a) too small cut leaves (geo (black), so that all (non cut) leaves are marked as: Cut through an octree approximation TRgeo, with (a) too small cut leaves (geo (black), so that all (non cut) leaves are marked as Ceo (black), so that all (non cut leaves are marked as outside (light gray). (b) with one subdivision level less leaves inside (dark gray) can be detected.*

![Figure 26. Finite cell mesh and displacement of the flawed and the valid model.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-26-p023.png)

*Figure 26. Finite cell mesh and displacement of the flawed and the valid model.: Finite cell mesh and displacement of the flawed and the valid model.*

$$
(a) FCM mesh (b) Flawed (c) Valid, including FCM mesh
$$

points counting as inside and once counting as outside. The energy norm for lower boundary was \(\sim 0.4 \%\) lower, and for the upper boundary \(\sim 2.9 \%\) larger compared to the simulation with 'vote for the majority'. Due to the fact that the error is restricted to the smallest geometrical leaves and the ray-casting errors occur only in the vicinity of the flaws, the deviation in the strain energy norm is rather small.

### 5.2 Example 2: Screw

This example demonstrates how the algorithm performs for a more complex geometry. To this end, we consider the potentially flawed CAD model of a screw, depicted in Fig. 1. The simulation was carried out on \(10 \times 30 \times 10\) finite cells using trivariate B-Splines of polynomial degree \(p=3\) and the open knot vector Fig. 25 shows the effect of a too fine resolution of \(\widehat{T R}_{\text {geo }}\). For a subdivision depth \(n_{\text {max }}=5\), the flood fill algorithm marks the entire domain as outside.

A visual inspection of the displacements of the flawed and the valid model shows no difference (see Fig. 26), whereas differences around the flaws can be detected for the von Mises stresses (see Fig. 27). The stresses at the flawed model are more noisy compared to the valid model.

![Figure 27. Von Mises stresses around the flawed region.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-27-p024.png)

*Figure 27. Von Mises stresses around the flawed region.: Von Mises stresses around the flawed region.*

(b) Valid

![Figure 28. General electric design challenge for the optimal shape of a jet engine brake.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-28-p024.png)

*Figure 28. General electric design challenge for the optimal shape of a jet engine brake.: General electric design challenge for the optimal shape of a jet engine brake.*

(b) Optimized design

### 5.3 Example 3: Engine brake

In 2013, a collaboration of Grab Cad and General Electric arranged a competition to find the optimal design of an engine bracket for a General Electric turbofan [74]. The submitted designs were then evaluated, and the top ten were produced using additive manufacturing. The model depicted in Fig. 28 was designed by Sean Morrissey. \({ }^{3}\) In an attempt to perform a heat diffusion simulation motivated by a local heat source induced by a laser beam during additive manufacturing it turns out that 337.544 triangles have a free edge, indicating a gap opening between the patches. 2324 triangles were oriented in the wrong direction and innumerable intersections occurred. Due to the immense amount of flaws, geometry healing-and, thus, also the meshing-is not applicable on this raw model. However, using the approach presented in this paper, we were able to immediately run a simulation without any further treatment of flaws.

We choose \(18 \times 11 \times 6\) elements for the simulation. A partitioning depth for the geometry approximation tree \(\widehat{T R}_{\text {geo }}\) of \(n_{\text {max }}=3\) on each finite cell was applicable. A laser beam is modeled by a small heat source where a local refinement of the finite cell grid was applied. Fig. 30 shows the resulting temperatures in the specimen.

## 6 Conclusions

This work presents a methodology to address challenges flawed CAD models pose to computational mechanics. Unlike other methods that rely on model reconstruction or geometry healing, the proposed approach herein allows 3 https: grabcad.com sean.morrissey-1.

![Figure 29. Blue lines denote open edges](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-29-p025.png)

*Figure 29. Blue lines denote open edges: In many cases the free edges are fairly close. As can be seen in the detailed views, however, some of the gaps and openings are quite large. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)*

![Figure 30. Temperature distribution in the bracket due to a point heat source.](/Users/evanthayer/Projects/paperx/docs/2019_integrating_cad_and_numerical_analysis_dirty_geometry_handling_using_the_finite_cell_method/figures/figure-30-p025.png)

*Figure 30. Temperature distribution in the bracket due to a point heat source.: Temperature distribution in the bracket due to a point heat source.*

for a numerical analysis directly on the corrupted 'dirty' geometry. Certainly, a simulation on broken geometries will inevitably lead to errors, which are yet of a similar nature to modeling errors due to a representation of a NURBS-based geometry by faceted surfaces. The size of this modeling error depends on the geometric size of the flaws, e.g., the width of a gap between patches. The influence of these errors remains local to the flaw itself. Moreover, the error can be bounded by performing bracketing simulations. Therein, the upper bound is delivered by a computation considering all ambiguous integration points to lie inside the physical domain and the lower bound is generated by considering the inverse situation. Several examples demonstrate the capability of the proposed method, showing that results of high accuracy can be obtained.

## Acknowledgments

We gratefully acknowledge the support of the German Research Foundation under the Grant No. Ra624 22-2. Shuohui Yin from Hohai University, China as a visiting student at Technische Universität München, Germany, thanks Prof. Ernst Rank and Dr. Stefan Kollmannsberger at Technische Universität München for one-year academic guidance and discussion. He also thankfully acknowledges the support of the scholarship from China Scholarship Council (CSC).

## References

- J.A. Cottrell, T.J.R. Hughes, Y. Bazilevs, Isogeometric analysis: Toward Integration of CAD and FEA, John Wiley & Sons, ISBN: 978-0-470-74909-8, 2009.

- T.J.R. Hughes, J.A. Cottrell, Y. Bazilevs, Isogeometric analysis: CAD, finite elements, NURBS, exact geometry and mesh refinement,

- F. Cirak, M.J. Scott, E.K. Antonsson, M. Ortiz, P. Schröder, Integrated modeling, finite-element analysis, and engineering design for thin-shell structures using subdivision, Comput. Aided Des. 34(2) (2002) 137-148, http: dx.doi.org 10.1016 S0010-4485(01)00061-6.

- P. Kagan, A. Fischer, Integrated mechanically based CAE system using B-Spline finite elements, Comput. Aided Des. 32(8) (2000)

- 539-552, http: dx.doi.org 10.1016 S0010-4485(00)00041-5.

- J. Yang, S. Han, Repairing CAD model errors based on the design history, Comput. Aided Des. 38(6) (2006) 627-640, http: dx.doi.org 10.1016 j.cad.2006.02.007.

- M. Mäntylä, An Introduction to Solid Modeling, in: Principles of computer science series., Rockville: Computer Science Press, ISBN: 978-0-88175-108-6, 1988, 13.

- F. Massarwi, G. Elber, A B-spline based framework for volumetric object modeling, Comput. Aided Des. 78(2016) 36-47, http: dx.doi.org 10.1016 j.cad.2016.05.003.

- G. Butlin, C. Stops, Cad data repair, in: Proceedings of the 5th International Meshing Roundtable, 1996, pp. 7-12.

- H. Gu, T.R. Chase, D.C. Cheney, T.T. Bailey, D. Johnson, Identifying, correcting, and avoiding errors in computer-aided design models which affect interoperability, J. Comput. Inf. Sci. Eng. 1(2) (2001) 156-166, http: dx.doi.org 10.11151.1384887.

- N.A. Petersson, K.K. Chand, Detecting Translation Errors in CAD Surfaces and Preparing Geometries for Mesh Generation, Lawrence Livermore National Lab., CA (US), Newport Beach, CA, 2001.

- J. Yang, S. Han, S. Park, A method for verification of computer-aided design model errors, J. Eng. Des. 16 (3) (2005) 337-352, http: dx.doi.org 10.108009544820500126565.

- C.S. Chong, A. Senthil Kumar, H.P. Lee, Automatic mesh-healing technique for model repair and finite element model generation, Finite Elem. Anal. Des. 43(15) (2007) 1109-1119, 1109-1119,http: dx.doi.org 10.1016 j.finel.2007.06.009.

- F.S. Nooruddin, G. Turk, Simplification and repair of polygonal models using volumetric techniques, IEEE Trans. Vis. Comput. Graphics 9 (2) (2003) 191-205, http: dx.doi.org 10.1109 TVCG.2003.1196006.

- S. Bischoff, L. Kobbelt, Structure preserving CAD model repair, Comput. Graph. Forum 24(3) (2005) 527-536, http: dx.doi.org 10. 1111 j.1467-8659.2005.00878.x.

- O. Busaryev, T.K. Dey, J.A. Levine, Repairing and meshing imperfect shapes with delaunay refinement, in: 2009 SIAM ACM Joint

- (2002) 703-717, http: dx.doi.org 10.1002 fld.344.

- Y.K. Lee, C.K. Lim, H. Ghazialam, H. Vardhan, E. Eklund, Surface mesh generation for dirty geometries by the cartesian shrink-wrapping technique, Eng. Comput. 26(4) (2010) 377-390, http: dx.doi.org 10.1007 s00366-009-0171-0.

- R. Gasparini, T. Kosta, I. Tsukanov, engineering analysis in imprecise geometric models, in: Finite Elements in analysis and Design, Vol. 66, 2013, pp. 96-109, http: dx.doi.org 10.1016 j.finel.2012.10.011.

- L.V. Kantorovich, V.I. Krylov, Approximate Methods of Higher analysis, Interscience Publishers, ISBN: 978-0-486-82160-3, 1958.

- IntactSolutions, ScanAndSolve, http: www.scan-and-solve.com, 2013.

- J. Parvizian, A. Düster, E. Rank, Finite cell method, Comput. Mech. 41(1) (2007) 121-133, http: dx.doi.org 10.1007 s00466-0070173-y.

- A. Düster, J. Parvizian, Z. Yang, E. Rank, The finite cell method for three-dimensional problems of solid mechanics, Comput. Methods Appl. Mech. Engrg. 197(4548) (2008) 3768-3782, http: dx.doi.org 10.1016 j.cma.2008.02.036.

- A. Abedian, J. Parvizian, A. Düster, E. Rank, Finite cell method compared to h-version finite element method for elasto-plastic problems, Appl. Math. Mech. 35(10) (2014) 1239-1248, http: dx.doi.org 10.1007 s10483-014-1861-9.

- B. Wassermann, S. Kollmannsberger, T. Bog, E. Rank, From geometric design to numerical analysis: A direct approach using the finite cell method on constructive solid geometry, Comput. Math. Appl. (2017) http: dx.doi.org 10.1016 j.camwa.2017.01.027.

- S. Cai, W. Zhang, J. Zhu, T. Gao, Stress constrained shape and topology optimization with fixed mesh: A B-spline finite cell method combined with level set function, Comput. Methods Appl. Mech. Engrg. 278(2014) 361-387, http: dx.doi.org 10.1016 j.cma.2014.06. 007.

- J.P. Groen, M. Langelaar, O. Sigmund, M. Ruess, Higher-order multi-resolution topology optimization using the finite cell method, Internat. J. Numer. Methods Engrg. (2016) http: dx.doi.org 10.1002 nme.5432.

- M. Joulaian, A. Düster, Local enrichment of the finite cell method for problems with material interfaces, Comput. Mech. 52(4) (2013) 741-762, http: dx.doi.org 10.1007 s00466-013-0853-8.

- M. Joulaian, S. Duczek, U. Gabbert, A. Düster, Finite and spectral cell method for wave propagation in heterogeneous materials, Comput. Mech. 54(3) (2014) 661-675, http: dx.doi.org 10.1007 s00466-014-1019-z.

- S. Duczek, M. Joulaian, A. Düster, U. Gabbert, Numerical analysis of lamb waves using the finite and spectral cell methods, Internat. J. Numer. Methods Engrg. 99(1) (2014) 26-53, http: dx.doi.org 10.1002 nme.4663.

- M. Elhaddad, N. Zander, S. Kollmannsberger, A. Shadavakhsh, V. Nübel, E. Rank, Finite cell method: High-order structural dynamics for complex geometries, Int. J. Struct. Stab. Dyn. 15(7) (2015) 1540018, http: dx.doi.org 10.1142 S0219455415400180.

- T. Bog, N. Zander, S. Kollmannsberger, E. Rank, Weak imposition of frictionless contact constraints on automatically recovered high-order, embedded interfaces using the finite cell method, Comput. Mech. (2017).

- A. Mongeau, Large deformation twoand threedimensional contact on embedded interfaces using the Finite Cell Method, (Master's thesis), Technische Universität München, 2015.

- S. Kollmannsberger, A. Ozcan, J. Baiges, M. Ruess, E. Rank, A. Reali, Parameterfree, weak imposition of Dirichlet boundary conditions and coupling of trimmed and non-conforming patches, Internat. J. Numer. Methods Engrg. 101 (9) (2015) 670-699, http: dx.doi.org 10.1002 nme.4817.

- N. Zander, T. Bog, S. Kollmannsberger, D. Schillinger, E. Rank, Multi-level hp-adaptivity: high-order mesh adaptivity without the difficulties of constraining hanging nodes, Comput. Mech. 55 (3) (2015) 499-517, http: dx.doi.org 10.1007 s00466-014-1118-x.

- L. Kudela, N. Zander, S. Kollmannsberger, E. Rank, Smart octrees: accurately integrating discontinuous functions, in: 3D, Computer Methods in Applied Mechanics and engineering, Vol. 306, 2016, pp. 406-426, http: dx.doi.org 10.1016 j.cma.2016.04.006.

- T.-P. Fries, S. Omerovic, Higher-order accurate integration of implicit geometries, Internat. J. Numer. Methods Engrg. 106(5)(2015) 323-371, http: dx.doi.org 10.1002 nme.5121.

- M. Joulaian, S. Hubrich, A. Düster, Numerical integration of discontinuities on arbitrary domains based on moment fitting, Comput. Mech. 57(6) (2016) 979-999, http: dx.doi.org 10.1007 s00466-016-1273-3.

- S. Hubrich, P.D. Stolfo, L. Kudela, S. Kollmannsberger, E. Rank, A. Schröder, A. Düster, Numerical integration of discontinuous functions: Moment fitting and smart octree, Comput. Mech. (2017) 1-19, http: dx.doi.org 10.1007 s00466-017-1441-0.

- D. Giraldo, D. Restrepo, The spectral cell method in nonlinear earthquake modeling, Comput. Mech. (2017) 1-21, http: dx.doi.org 10.1007 s00466-017-1454-8.

- D. Schillinger, M. Ruess, N. Zander, Y. Bazilevs, A. Düster, E. Rank, Small and large deformation analysis with the p-and B-spline versions of the finite cell method, Comput. Mech. 50(4) (2012) 445-478, http: dx.doi.org 10.1007 s00466-012-0684-z.

- E. Rank, M. Ruess, S. Kollmannsberger, D. Schillinger, A. Düster, Geometric. modeling, Geometric modeling isogeometric analysis and the finite cell method, Comput. Methods Appl. Mech. Engrg. 249-252 (2012) 104-115, http: dx.doi.org 10.1016 j.cma.2012.05.022.

- M. Ruess, D. Schillinger, A.I. Özcan, E. Rank, Weak coupling for isogeometric analysis of non-matching and trimmed multi-patch geometries, Comput. Methods Appl. Mech. Engrg. 269(2014) 46-71, http: dx.doi.org 10.1016 j.cma.2013.10.009.

- F. de Prenter, C.V. Verhoosel, G.J. van Zwieten, E.H. van Brummelen, Condition number analysis and preconditioning of the finite cell method, Comput. Methods Appl. Mech. Engrg. 316 (Supplement C) (2017) 297-327, http: dx.doi.org 10.1016 j.cma.2016.07.006.

- E. Burman, P. Hansbo, M.G. Larson, A stabilized cut finite element method for partial differential equations on surfaces: The laplace operator, Comput. Methods Appl. Mech. Engrg. 285(2015) 188-207, http: dx.doi.org 10.1016 j.cma.2014.10.044.

- E. Burman, P. Hansbo, Fictitious domain finite element methods using cut elements: I. A stabilized lagrange multiplier method, Comput. Methods Appl. Mech. Engrg. 199(2680) (2010) 41-44-2686, http: dx.doi.org 10.1016 j.cma.2010.05.011.

- N.M. Patrikalakis, T. Sakkalis, G. Shen, Boundary representation models: Validity and rectification, in: The Mathematics of Surfaces IX, Springer, London, ISBN: 978-1-4471-1153-5, 2000, pp. 389-409, 978-1-4471-0495-7.

- C.M. Hoffmann, Geometric and Solid Modeling: An Introduction, in: The Morgan Kaufmann series in computer graphics and geometric modeling, Morgan Kaufmann, San Mateo, Calif, ISBN: 978-1-55860-067-6, 1989.

- T.W. Sederberg, G.T. Finnigan, X. Li, H. Lin, H. Ipson, Watertight Trimmed NURBS in ACM SIGGRAPH 2008 Papers, ACM, New York, NY, USA, 2008, http: dx.doi.org 10.11451399504.1360678.

- 19] Y. Bazilevs, V.M. Calo, J.A. Cottrell, J.A. Evans, T.J.R. Hughes, S. Lipton, M.A. Scott, T.W. Sederberg, Isogeometric analysis usin splines. Comput. Methods Appl. Mech. Engrg. 199 (58) (2010) 229-263, http: dx.doi.org 10.1016 j.cma.2009.02.03(

- A. Goldberg, D. Robson, Modeling with UML: Language, Concepts, Methods, Springer International Publishing, ISBN:

- [501 B. Rumpe, Modeling with UML: Language, Concepts, Methods, Springer International Publishing, ISBN: 978-3-319-33932-0, 2016.

- D. Schillinger, A. Düster, E. Rank, The hp-d-adaptive finite cell method for geometrically nonlinear problems of solid mechanics, Internat. J. Numer. Methods Engrg. 89(9) (2012) 1171-1202, http: dx.doi.org 10.1002 nme.3289.

- N. Zander, S. Kollmannsberger, M. Ruess, Z. Yosibash, E. Rank, The finite cell method for linear thermoelasticity, Comput. Math. Appl. 64(11) (2012) 3527-3541, http: dx.doi.org 10.1016 j.camwa.2012.09.002.

- M. Elhaddad, N. Zander, T. Bog, L. Kudela, S. Kollmannsberger, J.S. Kirschke, T. Baum, M. Ruess, E. Rank, Multi-level hp-finite cell method for embedded interface problems with application in biomechanics, Int. J. Numer. Methods Biomed. Eng. 34(4) (2018) e2951, http: dx.doi.org 10.1002 cnm.2951.

- S. Kollmannsberger, A. Özcan, M. Carraturo, N. Zander, E. Rank, A hierarchical computational model for moving thermal loads and phase changes with applications to selective laser melting, Comput. Math. Appl. 75(5) (2018) 1483-1497, http: dx.doi.org 10.1016 j. camwa.2017.11.014.

- 30 Ads), Encyclopedia of computational Mechanics, Vol. 2, Chichester, West Sussex: John Wiley e Sons, ISB: 978-1-19-00379-5 Eds.), Encyclopedia of computational Mechanics, 2017, pp. 1-35.

- M. Dauge, A. Düster, E. Rank, Theoretical and numerical investigation of the finite cell method, J. Sci. Comput. 65(3) (2015) 1039-1064, http: dx.doi.org 10.1007 s10915-015-9997-3.

- D. Schillinger, E. Rank, An unfitted hp-adaptive finite element method based on hierarchical B-splines for interface problems of complex geometry, Comput. Methods Appl. Mech. Engrg. 200(3358) (2011) 47-48-3380, http: dx.doi.org 10.1016 j.cma.2011.08.002.

- N. Zander, T. Bog, M. Elhaddad, F. Frischmann, S. Kollmannsberger, E. Rank, The multi-level hp-method for three-dimensional problems: Dynamically changing high-order mesh refinement with arbitrary hanging nodes, Comput. Methods Appl. Mech. Engrg. 310 (2016) 252-277, http: dx.doi.org 10.1016 j.cma.2016.07.007.

- V. Varduhn, M.-C. Hsu, M. Ruess, D. Schillinger, The tetrahedral finite cell method: higher-order immersogeometric analysis on adaptive non-boundary-fitted meshes, Internat. J. Numer. Methods Engrg. 107(12) (2016) 1054-1079, http: dx.doi.org 10.1002 nme.5207.

- D. Kamensky, M.-C. Hsu, D. Schillinger, J.A. Evans, A. Aggarwal, Y. Bazilevs, M.S. Sacks, T.J.R. Hughes, An immersogeometric variational framework for fluidstructure interaction: Application to bioprosthetic heart valves, Comput. Methods Appl. Mech. Engrg. 284(2015) 1005-1053, http: dx.doi.org 10.1016 j.cma.2014.10.04000015.

- S. Duczek, U. Gabbert, The finite cell method for polygonal meshes: Poly-FCM, Comput. Mech. (2016) 1-32, http: dx.doi.org 10.

- A. Abedian, J. Parvizian, A. Düster, H. Khademyzadeh, E. Rank, Performance of different integration schemes in facing discontinuities in the finite cell method, Int. J. Comput. Methods 10(03) (2013) 1350002, http: dx.doi.org 10.1142 S0219876213500023.

- M. Ruess, Y. Bazilevs, D. Schillinger, N. Zander, E. Rank, Weakly enforced boundary conditions for the NURBS-based finite cell method, in: European Congress on computational Methods in Applied Sciences and engineering (ECCOMAS), Vienna, Austria, ISBN: 978-3-9502481-9-7, 2012.

- M. Ruess, D. Schillinger, Y. Bazilevs, V. Varduhn, E. Rank, Weakly enforced essential boundary conditions for nurbs-embedded and trimmed nurbs geometries on the basis of the finite cell method, Internat. J. Numer. Methods Engrg. 95(10) (2013) 811-846, http: dx.doi.org 10.1002 nme.4522

- Y. Guo, M. Ruess, Nitsche's method for a coupling of isogeometric thin shells and blended shell structures, Comput. Methods Appl. Mech. Engrg. 284(2015) 881-905, http: dx.doi.org 10.1016 j.cma.2014.11.014.

- F.P. Preparata, M.I. Shamos, computational Geometry: An Introduction, Springer-Verlag New York, Inc, New York, NY, USA, ISBN:

- B. Zalik, I. Kolingerova, A cell-based point-in-polygon algorithm suitable for large sets of points, Comput. Geosci. 27(10) (2001) 1135-1145, http: dx.doi.org 10.1016 S0098-3004(01)00037-1.

- A. Sitek, R.H. Huesman, G.T. Gullberg, Tomographic reconstruction using an adaptive tetrahedral mesh defined by a point cloud, IEEE Trans. Med. Imaging 25(9) (2006) 1172-1179, http: dx.doi.org 10.1109 TMI.2006.879319.

- G. Taylor, point in polygon test, Surv. Rev. 32 (254) (1994) 479-484, http: dx.doi.org 10.1179 sre.1994.32.254.479.

- K.B. Salomon, An efficient point-in-polygon algorithm, Comput. Geosci. 4(2) (1978) 173-178, http: dx.doi.org 10.10160098-

- J.D. Foley, A.V. Dam, S.K. Feiner, J.F. Hughes, R.L. Phillips, Introduction to Computer Graphics, Addison-Wesley, ISBN: 978-0-201-60921-9, 1997.

- G. Strang, An analysis of the Finite Element Method, Englewood Cliffs, NJ: Prentice-Hall, ISBN: 0-13-032946-0, 1973.

- GrabCad, General Electric jet engine bracket challenge-GrabCAD, https: grabcad.com challenges ge-jet-engine-bracket-challenge,
