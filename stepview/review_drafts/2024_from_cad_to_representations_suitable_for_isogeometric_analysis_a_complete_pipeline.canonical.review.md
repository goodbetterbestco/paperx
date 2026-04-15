# 2024 from cad to representations suitable for isogeometric analysis a complete pipeline

Michelangelo Marsala, Angelos Mantzaflaris, Bernard Mourrain, Sam Whyman, Mark Gammon

[missing from original]

## Abstract

Next generation CAD CAE systems shall integrate design and analysis procedures as a means to simplify workflows, boost performance, and speed up time to market. In the present paper we demonstrate a proof of concept of such a unification using subdivision surfaces and the enabling technology of isogeometric analysis. In particular, we present a complete pipeline to convert CAD models into smooth G 1 spline representations, which are suitable for isogeometric analysis. Starting from a CAD boundary representation of a mechanical object, we perform an automatic control cage extraction by means of quadrangular faces, such that its limit Catmull-Clark subdivision surface approximates accurately the input model. We then compute a basis of the G 1 spline space over the quad mesh in order to carry out least squares fitting over a point cloud, acquired by sampling the original CAD geometry. The resulting surface is a collection of Bézier patches with G 1 regularity. Finally, we use the basis functions to perform isogeometric analysis simulations of realistic PDEs on the reconstructed G 1 model. The quality of the construction is demonstrated via several numerical examples performed on a collection of CAD objects presenting various challenging realistic shapes. Keywords CAD models · Point cloud fitting · Geometrically smooth surfaces · Spline basis · Isogeometric analysis Shape modeling and analysis are crucial operations which directly impact engineering and industrial processes in many sectors of our society. The last several decades have witnessed the development of many powerful tools for

## Introduction

computer-aided design (CAD), computer-aided engineering (CAE), and computer-aided manufacturing (CAM). These tools assist in handling the complex computations required to convert from the digital model of a shape to its actual production. Such computations can include digital shape description, model reparation, meshing, numerical simulations, and optimization. Currently, they require specific engineering efforts, are time consuming, and prone to errors and approximations [1, 2, Chapter 1]. This explains why alternative approaches are under investigation.

The boundary representation (B-rep) is used widely in solid modeling applications due to its flexibility and precision when representing manufacturable geometry in mechanical CAD (MCAD) processes. B-rep models consist of a set of topological entities with the following hierarchical relationship: vertices; edges bound by vertices; and faces bound by edges. The valence (i.e., number of incident edges) of the vertices can vary, and may not be considered to be regular (i.e., valence of 4). The topological entities are associated with corresponding geometric information. For instance, each topological edge has a spline curve associated with it. Similarly, each topological face has a parametric surface associated with it (herein referred to as the embedding surface). We will assume these to be NURBS surfaces, though analytic representations are also common. Figure 1 shows in (a) an example of a typical MCAD B-rep model and in (b) its separate NURBS surfaces as the embedding geometry for each face.

Whilst a B-rep representation prescribes definitive topological relationships between geometric entities, there is no guarantee of geometric fidelity.

The embedding NURBS surfaces of topologically neighboring faces may be discontinuous to an arbitrary extent at their interface. Similarly, the spline curves associated with the edges might not necessarily conform to the NURBS patches incident on the edge. The combination of these factors is referred to as geometric sloppiness (see schematic in Fig. 2), the severity of which depends on the design process employed within the CAD system. Furthermore, the topology of the B-rep can be arbitrarily complex, often for reasons no other than being an artefact of the design process. The side effect of such complexity is often the emergence of poor quality geometry, in the form of sliver faces.

The combination of geometric sloppiness and complex (or excessive) topology can present serious challenges for CAE applications and are often a major bottleneck to an effective design pipeline [3].

Therefore, there is significant appeal in simplifying both the topology and geometry of the model (or even select parts of the model) into an alternative representation which is more suitable for the specific application. This is a concept known as hybrid modeling, and allows the benefits of multiple different representations to be exploited. In an effective hybrid modeling engine, a direct link between the alternate representation and the original MCAD B-rep should always be maintained. This is especially important during the design of manufacturable parts, where MCAD B-rep is considered the standard format.

![Figure 2 Demonstration of geometric sloppiness inherently present in MCAD representations. The MCAD vertices are represented in red, the edges in blue, and the embedding NURBS surfaces in green and orange. In this example, the edges do not conform to the surfaces](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-2-p002.png)

*Figure 2 Demonstration of geometric sloppiness inherently present in MCAD representations. The MCAD vertices are represented in red, the edges in blue, and the embedding NURBS surfaces in green and orange. In this example, the edges do not conform to the surfaces: Demonstration of geometric sloppiness inherently present in MCAD representations. The MCAD vertices are represented in red, the edges in blue, and the embedding NURBS surfaces in green and orange. In this example, the edges do not conform to the surfaces*

Subdivision surfaces [4, 5] are one example of an alternative geometry type which has benefits over traditional NURBS patches due to their arbitrary topology via the introduction of extraordinary vertices (EVs). This means that a single subdivision surface can be used to represent an entire B-rep body comprised of many contiguous faces, with arbitrary topological complexity. This contrasts with the strictly rectangular nature of NURBS which dictates the need for multiple adjacent patches. Such alternative representation may be of particular interest for design optimization processes [6], wherein subdivisions surfaces may act as a proxy to the MCAD geometry for convenient manipulation. Within a hybrid modeling framework, subdivision surfaces may be treated just as any other embedding geometry for a B-rep face. This is crucial for the hybrid concept as it allows full compatibility with pre-existing operations offered by geometry engine software.

The goal of hybrid modeling is not to replace B-rep, but to complement it. Subdivision surfaces offer an intermediate representation which allows for convenient local modification to the geometry via adjustment of relatively few control points. Other representations may be more suitable when, for example, topological adjustments are desired, such as implicit representations, but an effective hybrid modeling engine should use a combination of different representations, exploiting the strengths of each.

One of the limitations of the widely used Catmull-Clark scheme [7] is in how the limit surface behaves at boundaries. Many implementations, such as the https: graph ics. pixar. com opens ubdiv docs intro. html OpenSubdiv library from Pixar, allow the application of sharp or semi-sharp creases to the boundary (or the interior) of the subdivision surface. These tools allow the creation of features such as fillets and chamfers without the need for introducing additional control cage vertices. However, these schemes do not allow for any limit surface curvature in the direction orthogonal to the boundary (referred to as cross-curvature) [8]. In the fields of computer graphics and animation, this is rarely an obstacle to achieving results. For engineering purposes however, this does not permit accurate modeling of real geometries which exhibit genuine cross-curvature at the boundary. Furthermore, we generally require precise control over the external boundaries of the limit surface so that they behave more similarly to MCAD edges and can be manipulated as such. These requirements for engineering-grade subdivision surfaces can be achieved by the addition of Bézier edge conditions [9].

To analyze the mechanical behavior of an MCAD model, a classical approach consists of meshing the shape from its B-rep description. Then, standard finite element methods (FEM) can be employed to run numerical simulations. Computing meshes from MCAD B-rep, which are suitable for numerical simulation, is not trivial due to the sloppiness of the geometric description, and the trimmed NURBS patchwork nature of the shape. Moreover, the meshing process produces piecewise linear approximations of the shape, which may require expensive mesh refinement to achieve sufficient accuracy in regions of high curvature. This is an obstacle for the development of high order numerical methods [10]. In recent years the alternative approach of isogeometric analysis (IGA) has been proposed to circumvent these difficulties [2]. Rather than involving an expensive meshing approximation step, it directly exploits the piecewise B-spline parametrization of the shape and associated B-spline basis functions in order to apply B-spline based FEM. This approach allows for high order numerical methods, requiring smaller finite element spaces, at the cost of a more expensive step in assembling the mass or stiffness matrices. However, this requires the computation of spline basis functions associated with the given geometry parametrization.

### 1.1 Contributions

We present a new scheme for handling MCAD B-rep models, and for analyzing their mechanical and physical behavior. It can be decomposed into the following steps:

- Computation of a single control cage, guided by a subdivision surface.

- Sampling of points on the MCAD B-rep model, adapted to the control cage partitioning of the domain of arbitrary topology.

- Reconstruction of a geometrically smooth surface from the data points, using the \(G_{1}\) basis functions associated with the control cage mesh.

- Isogeometric analysis of the mechanical behavior, using the G 1 basis associated with the control cage mesh.

![Figure 3 Schematic representation of the different steps composing the proposed pipeline](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-3-p003.png)

*Figure 3 Schematic representation of the different steps composing the proposed pipeline: Schematic representation of the different steps composing the proposed pipeline*

since they are based on the topology of the control cage. Therefore, our procedure demonstrates that high order isogeometric analysis is an enabling technology for next generation CAD CAE systems.

Our approach to generating control cages guided by subdivision surfaces from an initial MCAD B-rep model employs a combination of partitioning and meshing technology [11] to produce a quad mesh control cage of the domain. The full construction process is explained in detail in Sect. 2. Moreover, we also compute a basis of the \(G^{1}\) functions associated with the control cage, and use it for fitting accu rately the MCAD model and running high order numerical simulation via the IGA methodology.

We demonstrate the viability of our approach on real models from the automotive, shipbuilding, and aerospace industries, running the full process from the B-rep shape representation to numerical simulation.

### 1.2 Positioning

The need to run numerical simulation on CAD models is ubiquitous in engineering and industry. A classical approach, which has prevailed in the last few decades, is to mesh the CAD model and run standard FEM on the generated mesh. An entire suite of meshing technologies has been developed over the years, which today is commonly integrated into commercial products, or accessible in open source software, e.g., [12].

Converting a quadrilateral mesh into a spline model is a task that has been studied from multiple points of view over the last decade, especially due to the advent of isogeometric analysis. T-splines were used for this task in [13], due to their support of unstructured meshes, notably implemented in a commercial package [14]. In [15], the authors enhance T-spline construction to be \(C^{1}\) at EVs and apply them to the analysis of Kirchhoff-Love shell problems. In [16], a semi-automatic frame-field guided parametrization approach is developed, which converts trimmed B-rep geometry to conforming, watertight NURBS. In [17, 18], the authors present a method to rebuild (trimmed) CAD models based on surface Ricci flow with metric optimization. In [19], the authors use the history of employing Boolean operations in the construction of CAD models to ensure that trimmed CAD model are watertight. In [20], patch surface meshes serve as a guide to generating volume meshes suitable for use in fluid-structure interaction simulations. Overall, research centered around meshing geometric models is still very active [21-24]. However, the generated mesh remains an approximation of the geometric model and may require tuned refinement operations in regions with high error. This leads to complex and costly optimization computations to obtain accurate solutions in numerical simulations.

Another trend has been to approximate CAD models with higher order and more accurate representations of geometry which are simple to manipulate. Subdivision surfaces [4] and even volumes [25, 26] appeared as possible candidates due to their capacities to reproduce B-spline functions in regular regions, and to represent shapes with complex topologies. Some works have been developed to convert B-spline representations into subdivision schemes [27-29], or trimmed B-spline representation [30] to subdivision surfaces [9]. In general, the limit surface has good global approximation properties but poor geometric quality around the extraordinary vertices. Moreover, FEM based on subdivision schemes are not straightforward to control and require advanced techniques (such as dedicated quadrature rules) to obtain the expected precision [31].

An alternative approach to achieve faithful geometric representation, and perform accurate numerical simulation, is to use high order elements both for the geometry and the FEM. An approximate conversion of a Catmull-Clark subdivision surface into a collection of bicubic B-spline patches is described in [32]. The resulting surface is not necessarily smooth. Several works have addressed the construction of smooth surfaces from (quad) meshes. See e.g., [33-39].

To complete our pipeline, we also need to compute bases of spline functional spaces over the computed geom etry. The analysis of spline spaces over planar domains is well-developed, though many open problems still remain (see e.g., [40-44] and references therein). The analysis of \(G^{1}\) spline spaces is much less investigated [45-51]. We use these recent basis constructions both to construct an accurate representation of the geometry and to obtain functional ele ments of high order in IGA simulations.

## 2 Control cage generation from MCAD geometry

In this section, we detail the construction of the control cage from the boundary representation of a model. The foundation to our approach is to represent each MCAD edge with a cubic B-spline with a multiplicity-4 knot at each end. This allows the end curvature to be controlled by so-called slope control points which are not themselves part of the control cage topology (Fig. 4). These can equally be thought of as tangent vectors stored at the ends of the spline.

The limit surface is then defined to be the tensor product surface of the boundary B-splines. Since the slope control points affect only the first two knot spans, it follows that the first two layers of patches depart from the usual behavior of the regular regions of a Catmull-Clark subdivision surface (i.e., away from the EVs). This modification constitutes the addition of Bézier edge conditions to the standard Catmull-Clark scheme [9], and is illustrated by Fig. 5. The

![Figure 4 Schematic of a cubic B-spline with knot vector [0, 0, 0, 0, 1, 2, 3, 4,...]. The slope control point is shown in red, and all other control points in blue. The location of the red point influences the shape of the spline only within the first two knot spans. (Color figure online)](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-4-p005.png)

*Figure 4 Schematic of a cubic B-spline with knot vector [0, 0, 0, 0, 1, 2, 3, 4,...]. The slope control point is shown in red, and all other control points in blue. The location of the red point influences the shape of the spline only within the first two knot spans. (Color figure online): Schematic of a cubic B-spline with knot vector [0, 0, 0, 0, 1, 2, 3, 4,...]. The slope control point is shown in red, and all other control points in blue. The location of the red point influences the shape of the spline only within the first two knot spans. (Color figure online)*

3D location of the limit surface corresponding to the bound ary of the B-rep faces is influenced only by the control points associated with the MCAD edges. Therefore, neighboring control cages sharing the same boundary control points will maintain at least \(C^{0}\)-continuity between their limit surfaces, regardless of the positions of the interior control points, or the slope control points.

The use of Bézier edge conditions imposes strict topological requirements upon the control cage. Namely, no new EV may be placed on a B-rep face boundary (where one was not already present in the B-rep topology, such as in Fig. 11), nor within the first two layers of control cage faces, due to the tensor product nature of the limit surface within these regions.

These topological constraints, to which engineeringgrade subdivision surfaces must adhere, pose challenges when generating a suitable control cage. Each MCAD vertex must be treated as a corner, i.e., it must be associated with \(a_{2}\)-valent control cage vertex (such as in Fig. 5). The introduction of any new EV, where one was not already present in the B-rep topology, is restricted solely to the interior of the control cage. Meeting these requirements through traditional quad-dominant meshing techniques is challenging, and therefore we present a novel automatic approach referred to as SubD layering, which is tailored to satisfying the prescribed topological constraints.

The process involves partitioning an MCAD face into regions of structured and unstructured mesh. The structured regions form a boundary layer from which new EVs are fully excluded. These are formed by constructing 4-sided blocks around each MCAD vertex (referred to as corner blocks), and then connecting these to form 4-sided edge blocks associated with each MCAD edge. The remaining interior region constitutes a block with topology identical to the original MCAD face, and this is filled with unstructured mesh. This process is illustrated in Fig. 6.

The size and positions of the corner blocks are determined using the two-dimensional medial axis [11] as a guide to ensure that the blocks do not intersect. The construction of the medial axis follows the work in [52]: the algorithm starts with a Delaunay mesh of the domain and discovers triangles that are representative of medial vertices and edges, while it refines triangles which are not isomorphic to the medial circle. The resulting representation is reduced to a topology of minimum size. A snapshot of a computed SubD layering and the medial axis for a face from the Car model is given in Fig. 7.

Once the domain partitioning has been completed, we generate a coarse mesh of the layer faces. The boundary layer (consisting of the corner and edge blocks) is meshed

![Figure 6 Schematic outlining the SubD layering process. a MCAD B-rep face with 5 vertices. b corner blocks are constructed around the MCAD vertices. c corners blocks are connected to form edge blocks. d Domain is partitioned into corner (red) and edge (green) blocks which can receive structured mesh, and one interior (gray) region which receives unstructured mesh. (Color figure online)](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-6-p006.png)

*Figure 6 Schematic outlining the SubD layering process. a MCAD B-rep face with 5 vertices. b corner blocks are constructed around the MCAD vertices. c corners blocks are connected to form edge blocks. d Domain is partitioned into corner (red) and edge (green) blocks which can receive structured mesh, and one interior (gray) region which receives unstructured mesh. (Color figure online): Schematic outlining the SubD layering process. a MCAD B-rep face with 5 vertices. b corner blocks are constructed around the MCAD vertices. c corners blocks are connected to form edge blocks. d domain is partitioned into corner (red) and edge (green) blocks which can receive structured mesh, and one interior (gray) region which receives unstructured mesh. (Color figure online)*

using a transfinite interpolation technique [53] and is specified to be one element thick between the boundary and the interior (see Fig. 6). This does not preclude increasing the mesh density along the length of the edge blocks, thus limiting the aspect ratio of the resulting elements. The interior region is meshed using quad-dominant meshing technology [11]. Owing to the strict placement rules of the edge and corner blocks, the resulting control cage faces can exhibit notable skewness. Furthermore, it should be noted from Fig. 7 that some of the corner blocks have colinear quad edges (i.e., associated with MCAD vertices on flat edges), which may lead to degenerate Jacobians. We acknowledge that this is a current limitation of our approach, and propose the need of future research to address the problem. The entire coarse mesh (including both the boundary and interior regions) is then refined twice using the Catmull-Clark subdivision scheme. This ensures that there are no EVs within the first two layers of control cage faces from the boundary, thus satisfying the topological requirements for the Bézier edge conditions. A simple example of the refinement of a coarse mesh, serving to demonstrate the EV placement criteria, is illustrated in Fig. 8. The refinement for a face from the Car model is shown in Fig. 9.

The SubD layering process is applied to each MCAD face in the model in turn, such that the resulting control cage meets the topological requirements dictated by all MCAD edges, both external and internal (i.e., connectivity 1 and 2, respectively). By stipulating that the common vertices along the edges between contiguous faces are shared, a single limit ment the location of the EVs meet the topological requirements for the Bézier edge conditions

![Figure 9 Mesh refinement for the wheel arch of the Car model. From left to right](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-9-p007.png)

*Figure 9 Mesh refinement for the wheel arch of the Car model. From left to right: initial coarse mesh; one level of refinement; two levels of refinement. The control cage faces corresponding to the corner and an initial coarse mesh for a 5-sided face. b one level of refinement. c two levels of refinement (with Laplacian mesh smoothing applied). The EVs are highlighted in red. After two levels of refine-*

surface is able to represent the entire model while remain ing fully watertight (i.e., \(C^{0}\) continuous). This guarantee is not maintained for MCAD B-rep geometry as a network of (trimmed) NURBS patches. An example of a watertight limit surface is given in Fig. 10. An example of the control cage computation is presented in Fig. 1(c).

Despite the restricted placement of EVs with respect to the B-rep face boundaries, the SubD layering construction is fully compatible with B-rep face networks of any topology. This includes the presence of MCAD vertices with a face valence not equal to four. This is because the limit surface corresponding to each separate face is governed solely by the edges which bound that face, and only that face. This is demonstrated in Fig. 11.

## 3 Control cage adjustment and point cloud sampling

The SubD layering process outlined in Sect. 2 is primarily focused on achieving the correct topology for the control cage. The second step of the process is to adjust the control cage so that its limit surface coincides with the target MCAD geometry. To achieve this, we use the ability of our engineering-grade subdivision surfaces to accurately represent edge blocks are shown in red and green, respectively. The faces corresponding to the interior region is shown in gray. This may be compared with the parametric domain partitioning presented in Fig. 7

![Figure 10 A single subdivision surface representing the wing tip of the SNC Dream Chaser model, which is comprised of multiple MCAD B-rep faces. The control cage is shown in green, and the limit sur- face is shaded in orange. Bézier edge conditions (with slope control vectors shown in gray) are applied such that contiguous regions of the limit surface meet with the same C 1 discontinuity as the original B-rep. However, the limit surface is guaranteed to be exactly C 0 con- tinuous along the join reflecting the MCAD edges (blue). (Color fig- ure online)](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-10-p007.png)

*Figure 10 A single subdivision surface representing the wing tip of the SNC Dream Chaser model, which is comprised of multiple MCAD B-rep faces. The control cage is shown in green, and the limit sur- face is shaded in orange. Bézier edge conditions (with slope control vectors shown in gray) are applied such that contiguous regions of the limit surface meet with the same C 1 discontinuity as the original B-rep. However, the limit surface is guaranteed to be exactly C 0 con- tinuous along the join reflecting the MCAD edges (blue). (Color fig- ure online): A single subdivision surface representing the wing tip of the SNC Dream Chaser model, which is comprised of multiple MCAD B-rep faces. The control cage is shown in green, and the limit surface is shaded in orange. Bézier edge conditions (with slope control vectors shown in gray) are applied such that contiguous regions of the limit surface meet with the same C 1 discontinuity as the original B-rep. However, the limit surface is guaranteed to be exactly C 0 continuous along the join reflecting the MCAD edges (blue). (Color figure online)*

geometry; the behavior of the edges is governed by the B-spline edge conditions, which can be made to respect the MCAD edges via a least squares fitting process.

Once the positions of the edge control points have been determined, they are fixed. Then, to adjust the interior control points, we minimize the error between a grid of

![Figure 11 A schematic of the SubD layering construction centered around an MCAD vertex (yellow) with a face valence equal to five. The MCAD edges are shown in blue. The control cage vertices (black) introduced by the layering process are shared between the topologically connected faces (i.e., those coincident with the blue lines). Each red region corresponds to a section of limit surface which is governed solely by the control points belonging to that face (see Figure 5 ), whilst maintaining C 0 -continuity with the neighboring red regions. This is a departure from the standard Catmull-Clark scheme, wherein each of the control points surrounding the EV has an influ- ence over the limit surface. (Color figure online)](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-11-p008.png)

*Figure 11 A schematic of the SubD layering construction centered around an MCAD vertex (yellow) with a face valence equal to five. The MCAD edges are shown in blue. The control cage vertices (black) introduced by the layering process are shared between the topologically connected faces (i.e., those coincident with the blue lines). Each red region corresponds to a section of limit surface which is governed solely by the control points belonging to that face (see Figure 5 ), whilst maintaining C 0 -continuity with the neighboring red regions. This is a departure from the standard Catmull-Clark scheme, wherein each of the control points surrounding the EV has an influ- ence over the limit surface. (Color figure online): A schematic of the SubD layering construction centered around an MCAD vertex (yellow) with a face valence equal to five. The MCAD edges are shown in blue. The control cage vertices (black) introduced by the layering process are shared between the topologically connected faces (i.e., those coincident with the blue lines). Each red region corresponds to a section of limit surface which is governed solely by the control points belonging to that face (see Fig. 5), whilst maintaining C 0-continuity with the neighboring red regions. This is a departure from the standard Catmull-Clark scheme, wherein each of the control points surrounding the EV has an influence over the limit surface. (Color figure online)*

sample points on the limit surface and the corresponding point grid on the MCAD geometry. This is done by com puting gradients of the error and by iteratively adjusting the control cage until a sufficiently good approximation is attained. Given a set of all control points \(\mathcal{X}\), consider the set of sample points \(\hat{\mathcal{P}}\) over the limit surface, where each sample point \(\mathbf{p}_{i} \in \hat{\mathcal{P}}\) can be expressed as the limit stencil

$$
\begin{equation*} \mathbf{p}_{i}=\sum_{\mathbf{x}_{j} \in \mathcal{C}} w_{j}^{i} \mathbf{x}_{j}, \tag{1} \end{equation*}
$$

where \(\mathcal{C} \subset \mathcal{X}\), is the set of control points supporting \(\mathbf{p}_{i}\). The weights \(w_{j}^{i}\) are functions of the local patch parameter \([s, t]\) corresponding to the limit surface evaluation point \(\mathbf{p}_{i}\), such that where \(\mathbf{s}\) is the column vector \(\left[1, s, s^{2}, s^{3}\right]\), \(\mathbf{t}\) is the column vector \(\left[1, t, t^{2}, t^{3}\right]\), and \(M_{s}\) and \(M_{t}\) are matrices representing the cubic spline evaluation. The functions row(j) and \(\operatorname{col}(j)\) map the control point index \(j \in \mathcal{C}\) to the corresponding row and column of the tensor product grid, respectively. The matrices are determined solely by the control cage topology. For example, for regular patches under the Catmull-Clark scheme the matrices \(M_{s}\) and \(M_{t}\) take the form,

$$
M_{s}=M_{t}=\left[\begin{array}{cccc} 1 & -3 & 3 & -1 \tag{3}\\ 4 & 0 & -6 & 3 \\ 1 & 3 & 3 & -3 \\ 0 & 0 & 0 & 1 \end{array}\right] .
$$

The set \(\hat{\mathcal{P}}\) is constructed by iterating over each control cage face and appending a uniform grid of local patch parameters. Each sample point \(\mathbf{p}_{i}\) on the limit surface is assigned a corresponding target location \(\mathbf{q}_{i}\) on the MCAD geometry. This is achieved via bilinear interpolation over the parametric sub-domain of the MCAD face which is bounded by the control cage face. The MCAD face is evaluated at the interpolated coordinate to find \(\mathbf{q}_{i}\).

For patches influenced by the Bézier edge conditions (see Sect. 2), where \(M_{s} \neq M_{t}\), the matrices are determined using the De Boor algorithm [54]. For patches containing EVs, we employ the evaluation method of [55]. Once the appropri ate matrices have been determined, the weights may subse quently be evaluated conveniently for any given parameter value \([s, t]\) according to (2).

$$
A gradient vector \( \boldsymbol{\delta}_{i} \) for each control point in \( \mathcal{X} \) is defined to be
$$

$$
\begin{equation*} \boldsymbol{\delta}_{\mathrm{i}}=\frac{1}{\left|\mathcal{A}_{\mathrm{i}}\right|} \sum_{\mathbf{p}_{\mathrm{j}} \in \mathcal{A}_{\mathrm{i}}}\left(\mathbf{q}_{\mathrm{j}}-\mathbf{p}_{\mathrm{j}}\right) \mathrm{w}_{\mathrm{i}}^{\mathrm{j}}, \tag{4} \end{equation*}
$$

where denotes the set of sample points which are influenced by control point x i. One round of control point adjustment equates to applying the operation x i = x i + 𝜹 i, ∀ x i ∈ X. This procedure avoids the need to solve a large linear system and instead relies on local updates of the control points at hand. We stress that this fitting is an intermediate result obtained prior to the subsequent least-squares fitting of the \(G_{1}\) spline surfaces. As such, we only require an adequate approximation of the MCAD geometry. We found that applying 1000 rounds of control cage adjustment was sufficient in the majority of cases; nonetheless, we acknowledge that this is an area for future improvement by means of introducing robust convergence criteria. The fitting results are demonstrated in Fig. 12, which shows the front section of the NASA CRM.

The procedure concerning the fitting for our multipatch \(G^{1}\) spline representation combines the generation of points on the geometry with a standard regression between the sample points and the parametric points on the subdivi sion surface. We require a set of samples points which lie exactly on the geometry, including the edges. Each point must be mapped to a corresponding patch of the subdivision surface, together with a local patch parameter

$$
\begin{equation*} w_{j}^{i}(s, t)=\left[M_{t} \mathbf{t}\right]_{\operatorname{row}(j)}\left[M_{s} \mathbf{s}\right]_{\operatorname{col}(j)}, \tag{2} \end{equation*}
$$

![Figure 12 Heat map of the distance from the limit surface to the target MCAD geometry, for the forward section of the NASA CRM. A maximum fitting error of approximately 0.005% of the aircraft length is achieved after 1000 rounds of iterative control cage adjustment](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-12-p009.png)

*Figure 12 Heat map of the distance from the limit surface to the target MCAD geometry, for the forward section of the NASA CRM. A maximum fitting error of approximately 0.005% of the aircraft length is achieved after 1000 rounds of iterative control cage adjustment: Heat map of the distance from the limit surface to the target MCAD geometry, for the forward section of the NASA CRM. A maximum fitting error of approximately 0.005% of the aircraft length is achieved after 1000 rounds of iterative control cage adjustment*

coordinate. This is achieved by sampling each patch of the limit surface at a predetermined set of parameter values, using explicit evaluation [55]. The corresponding 3D positions on the limit surface (which approximates the geometry) are then projected back onto the MCAD geometry. Given that the limit surface samples already lie very close to the target geometry, they may be projected easily onto the embedding NURBS surfaces of the MCAD B-rep faces. We also apply additional heuristics such as mean value interpolation when the displacements are large, which aims at preventing creases and folds appearing in highly curved regions. These measures also serve to reduce the impact of geometric sloppiness and poor quality B-rep, ensuring that the sample grids for neighboring faces meet without gaps or folds. The result is a uniform non-folding structured grid of sample points lying on the target geometry, for each patch of the limit surface. Figure 13 shows an example of the typical distribution of the point cloud sampling.

## 4 G 1 functions on quad meshes

To apply least squares fitting and IGA methods, we need to define a function space of regular functions such as a spline space. In this section, we briefly introduce some basic definitions and the tools required to build spaces of geometrically smooth functions over a quad mesh M.

### 4.1 Definition of G 1 functions

Let \(f=\left(f_{\sigma}\right)_{\sigma \in \mathcal{M}}\) be a collection of functions defined over the faces \(\sigma\) of a quad mesh \(\mathcal{M}\). All faces \(\sigma \in \mathcal{M}\) have parametric domain \([0,1]^{2}\).

We name \(e\) the common edge shared by two adjacent patches \(f^{L}=\left.f\right|_{\sigma_{L}}\) and \(f^{R}=\left.f\right|_{\sigma_{R}}\) of a collection \(f\). With reference to the local systems' orientation in Fig. 14, two functions are said to be \(G^{1}\) (or tangent plane continuous) if they join \(G^{0}\) (or \(C^{0}\) ), i.e.,

$$
\begin{equation*} f^{L}\left(u_{1}, 0\right)=f^{R}\left(0, u_{1}\right), \quad u_{1} \in[0,1], \tag{5} \end{equation*}
$$

![Figure 14 Local coordinate systems between two adjacent patches](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-14-p010.png)

*Figure 14 Local coordinate systems between two adjacent patches: Local coordinate systems between two adjacent patches*

and there exists three function a, b, c ∶ e ⟶ \(\mathbb{R}^{called}\) gluing functions such that where \(u_{1} \in[0,1], f_{u}=\frac{\partial f}{\partial u}\) and \(\langle\cdot \mid \cdot\rangle\) refers to the standard Euclidean scalar product. In detail, (6) means that the tan gent plane across the common edge e of \(f^{L}\) and \(f^{R}\) is the same, (8) signifies that the tangent plane has no vanishing normal, and (7) controls the orientation of the patches in order to avoid cusps. We refer the reader to [56] for further details.

A particular spline space defined over quad meshes and verifying eqs. (5) to (8) is the \(G^{1} \mathrm{ACC}\) derived in [39]; it is obtained from a collection of biquintic Bézier functions by imposing \(G^{1}\) continuity across extraordinary regions making use of the quadratic gluing functions

polynomials and \(a_{i}=2 \cos \left(2 \pi / N_{i}\right), i=0,2\) where \(N_{i}\) repre sent the valence of the two vertices belonging to the com mon edge (i.e., the number of edges attached to them). More generally, \(C^{1}\) continuity of surfaces can be obtained from \(G^{1}\) (geometric) continuity after some regular repara metrization of adjacent pieces (i.e., patches sharing the edge

$$
\begin{align*} & f_{v_{1}}^{L}\left(u_{1}, 0\right) c\left(u_{1}\right)+f_{u_{1}}^{R}\left(0, u_{1}\right) b\left(u_{1}\right)+f_{v_{0}}^{L}\left(0, u_{1}\right) a\left(u_{1}\right)=0, \tag{6}\\ & c\left(u_{1}\right) b\left(u_{1}\right)<0, \tag{7}\\ & \left\langle f_{v_{1}}^{L}\left(u_{1}, 0\right), f_{v_{0}}^{R}\left(0, u_{1}\right)\right\rangle \neq 0, \tag{8} \end{align*}
$$

$$
\begin{aligned} & \phi_{\sigma_{R}, \sigma_{L}}: \mathbb{R}^{2} \longrightarrow \mathbb{R}^{2}, \quad\left(u_{1}, v_{1}\right) \mapsto\left(u_{0}, v_{0}\right) \\ & \quad=\binom{v_{1} \mathfrak{b}\left(u_{1}\right)}{u_{1}+v_{1} \mathfrak{a}\left(u_{1}\right)}, \quad \text { where } \quad \mathfrak{b}(u)=\frac{b(u)}{c(u)}, \mathfrak{a}(u)=\frac{a(u)}{c(u)} \end{aligned}
$$

The relations for the tangent plane continuity constraints between the control points \(\mathbf{b}_{i, j}, i, j=0, \ldots, 5\) of two neigh boring Bézier patches \(f^{L}, f^{R}\) defining the \(G^{1}\) ACC space are the following:

$$
\begin{aligned} \mathrm{b}_{0,1}^{L}+\mathrm{b}_{1,0}^{R} \&=\bar{a}_{0} \mathrm{~b}_{0,0}^{L}+a_{0} \mathrm{~b}_{1,0}^{L}, & \\ 5\left(\mathrm{~b}_{1,1}^{L}+\mathrm{b}_{1,1}^{R}\right)= & a_{0} \mathrm{~b}_{0,0}^{L}+5 \bar{a}_{0} \mathrm{~b}_{1,0}^{L}+4 a_{0} \mathrm{~b}_{2,0}^{L}, \\ 10\left(\mathrm{~b}_{2,1}^{L}+\mathrm{b}_{1,2}^{R}\right)= & -a_{0} \mathrm{~b}_{0,0}^{L}+5 a_{0} \mathrm{~b}_{1,0}^{L}+10 \bar{a}_{0} \mathrm{~b}_{2,0}^{L}+6 a_{0} \mathrm{~b}_{3,0}^{L}, \\ 10\left(\mathrm{~b}_{3,1}^{L}+\mathrm{b}_{1,3}^{R}\right)= & a_{0} \mathrm{~b}_{0,0}^{L}-5 a_{0} \mathrm{~b}_{1,0}^{L}+10 a_{0} \mathrm{~b}_{2,0}^{L}+10 \bar{a}_{0} \mathrm{~b}_{3,0}^{L} \\ & +4 a_{0} \mathrm{~b}_{4,0}^{L}, \mathrm{~b}_{4,1}^{L}+\mathrm{b}_{1,4}^{R} \&=2 \mathrm{~b}_{4,0}^{L}, \\ \mathrm{~b}_{5,1}^{L}+\mathrm{b}_{1,5}^{R}= & 2 \mathrm{~b}_{5,0}^{L}, \\ 10\left(\mathrm{~b}_{3,0}^{L}-\mathrm{b}_{2,0}^{L}\right)= & \mathrm{b}_{0,0}^{L}-5 \mathrm{~b}_{1,0}^{L}+5 \mathrm{~b}_{4,0}^{L}-\mathrm{b}_{5,0}^{L}, \end{aligned}
$$

with \(\bar{a}_{0}=2-a_{0}\). The above system of \(G^{1}\) relations can be solved by following the approach in [39].

$$
\begin{aligned} & a(u)=a_{0} B_{2}^{0}(u)-a_{2} B_{2}^{2}(u), \\ & b(u)=-1, \\ & c(u)=1, \end{aligned}
$$

### 4.2 Construction

The aim of this step of the pipeline is to obtain a representation of an MCAD model in terms of smooth \(G^{1}\) functions. In Sect. 3 it has been shown how to discretize an MCAD model as a dense point cloud preserving its features, while Sect. 2 presents a method for the automatic generation of a control cage (i.e., a quad mesh) approximating the MCAD. Therefore, the idea is to use the construction in [51] to obtain a multipatch \(G^{1}\) spline representation via point

$$
\begin{equation*} \min _{\mathbf{c}} \sum_{i=1}^{n_{P}}\left\|\sum_{j=1}^{n_{b}} c_{j} B_{j}\left(\xi^{i} ; \sigma_{\ell}\right)-\mathbf{P}_{i}\right\|_{2}^{2}+\lambda E_{\text {thin }}(\mathbf{c}), \quad \lambda \geq 0 \tag{9} \end{equation*}
$$

cloud fitting using basis functions defined over the control cage supporting the data points. These bases are obtained by performing an extraction procedure which returns the control points defining the basis function in the Bézier form. More precisely, to get the Bézier coefficient of the bases, we fix the value of a control point appearing in the equations defining the \(G^{1} \mathrm{ACC}\) in Sect. 4.1 to be, for exam ple, 1, and all the remaining free coefficients in the system to be 0. Hence, with these initial values we solve all the equations defining the \(G^{1}\) constraints and as a result of this operation, we obtain the control points for our basis func tions. Repeating for all the Bézier points involved in the system results in the entire set of bases generating the \(G^{1}\) ACC spline space. The resulting bases set can be decom posed as a direct sum of three subsets formed by particular functions attached to the different features of a quad mesh; these sets are the so-called vertex bases set, edge bases set and face bases set. As suggested by the names, the vertex bases set contains basis functions whose support lies on the patches attached to a vertex. In presence of an EV, i.e., a vertex with valence \(N \neq 4\), the resulting set of bases is composed of \(N+3\) elements, while for a regular vertex the corresponding space consists of 4 functions. Belonging to the edge bases set are all those functions whose sup port is contained in the two patches attached to a specific edge of the mesh. We will have 2 basis functions for each extraordinary edge (that is, an edge sharing an EV) and 4 for each regular and boundary edge. Lastly, we find in the face vertex set the basis functions whose support is entirely contained within a single patch. Part of this set are the face and corner basis functions, which appear in groups of 4 each. We refer the reader to [51] for a detailed analysis of the basis functions and their construction.

### 4.3 G 1 spline fitting

Consider a point cloud P, which is a collection of n P points P i ∈ \(\mathbb{R}^{3}\), i = 1, … , n P with associated parameters 𝝃 i = ( 𝜉 \(i_{1}\), 𝜉 \(i_{2}\)) ∈ \(\mathbb{R}^{2}\) on the face 𝜎 𝓁 , and the set of \(G_{1}\) basis functions Bj ∈ B containing n b elements (presented in Sect. 4.2) defined over the control cage M formed by n F faces generated with the strategy described in Sect. 2. The idea of the least squares fitting technique is to find the coefficients c = { \(c_{j}\) } n \(b_{j}=1\), \(c_{j}\) ∈ \(\mathbb{R}^{3}\), defining a spline surface

$$
S(\xi ; \sigma)=\sum_{j=1}^{n_{b}} c_{j} B_{j}(\xi ; \sigma), \quad \sigma \in \mathcal{M}
$$

such that the squared distance from the set of points is minimal, that is, obtained by computing

We also take into account in our minimization problem (9) an energy term given by the standard thin-plate energy ‖ ‖

$$
\begin{aligned} & E_{\text {thin }}(\mathbf{c})=\sum_{\ell=1}^{n_{F}} \iint_{[0,1]^{2}}\left\|S_{\xi_{1} \xi_{1}}\left(\xi ; \sigma_{\ell}\right)\right\|_{2}^{2} \\ & \quad+2\left\|S_{\xi_{1} \xi_{2}}\left(\xi ; \sigma_{\ell}\right)\right\|_{2}^{2}+\left\|S_{\xi_{2} \xi_{2}}\left(\xi ; \sigma_{\ell}\right)\right\|_{2}^{2} d \xi \end{aligned}
$$

where \(S_{\xi_{r} \xi_{s}}=\frac{\partial^{2}}{\partial \xi_{r} \partial \xi_{s}} S(\xi ; \sigma)\). Having such a term is useful to control and avoid possible unpleasant oscillations that might arise from the fitting. Note that the mesh is not modified during the fitting procedure, and the point cloud \(\mathcal{P}\) is the MCAD sampling given in Sect. 3.

We can now compute the fitted surface S by solving the minimization problem given in (9). This is a least squares problem, whose solution is obtained by solving a linear system. In order to investigate the quality of the fitting we compute the following error indicators:

$$
\begin{align*} L^{\infty} & :=\max _{i=1, \ldots, n_{P}}\left\|S\left(\boldsymbol{\xi}^{i}\right)-\mathbf{P}_{i}\right\|_{2} \\ & \text { RMSE }:=\sqrt{\frac{1}{n_{P}} \sum_{i=1}^{n_{P}}\left\|S\left(\boldsymbol{\xi}^{i}\right)-\mathbf{P}_{i}\right\|_{2}^{2}} \tag{10} \end{align*}
$$

which represent, respectively, the maximum \(\ell_{2}\) distance and the so-called root mean squared error (RMSE). Section 6 presents several numerical experiments showing the quality of the surfaces obtained with the use of our multipatch \(G^{1}\) basis functions.

## 5 Isogeometric analysis

Isogeometric analysis (IGA) is a highly efficient technique for solving PDEs numerically. Its basic idea, presented in [2] (which unifies the FEM approach and Computer Aided Geometric Design) is to use the same basis functions for both reproducing exactly the computational domain, and for the numerical approximation of the PDE. Here we focus on solv ing the heat equation and the biharmonic flow equation on a 2-manifold \(\Omega \subset \mathbb{R}^{3}\), which is defined by our MCAD model. Hence, we need to extend the standard Laplace operator to the Laplace-Beltrami operator, which is necessary when dealing with manifolds. To do that, we define the geometry map with \(\widehat{\Omega}=[0,1]^{2}\), which defines our manifold by means of a mapping from the parametric domain \(\widehat{\Omega}\) into the physical space \(\mathbb{R}^{3}\). The Jacobian of the mapping \(J\), i.e.,

$$
\left\{\begin{array}{lc} a_{1}(\widehat{u}(\xi, t), \widehat{w})=b_{1}\left(\partial_{t} \widehat{u}(\xi, t), \widehat{w}\right), & (\xi, t) \in \widehat{\Omega} \times(0, T], \tag{13}\\ u(\xi, 0)=u_{0}(\mathbf{x}), & \xi \in \widehat{\Omega}, \widehat{\mathbf{x}}(\xi) \in \Omega, \\ \widehat{u}(\xi, t)=u_{D}(\mathbf{x}, t), & (\xi, t) \in \partial \widehat{\Omega} \times(0, T], \end{array}\right.
$$

is used to define the first fundamental form of the mapping ̂ G defined as together with its determinant ̂ g, which is

Finally, we have all the tools to define the gradient operator on the manifold Ω in parametric coordinates, as well as the Laplace-Beltrami operator of a sufficiently smooth function \(\varphi\) associated to the manifold \(\Omega\), where \(\hat{\varphi}(\xi)=\varphi(\mathbf{x}(\xi))\) and \(\widehat{\nabla}, \widehat{\nabla}\). identify, respectively, the gradient and the divergence operators in the parametric space.

For a more precise explanation of operators for isogeometric solutions to PDEs on manifolds, we refer the reader to [57].

We can therefore formulate the (strong) Cauchy prob lem for the heat equation. Let \(\Omega\) be a manifold; find \(u \in C^{2}(\Omega) \times C^{1}\left(\mathbb{R}_{+}\right)\)such that

$$
\begin{aligned} & a_{2}(\widehat{v}, \widehat{w})=\int_{\widehat{\Omega}} \frac{1}{\widehat{g}} \widehat{\nabla} \cdot\left(\widehat{g} \widehat{G}^{-1}(\xi) \widehat{\nabla} \widehat{v}\right) \widehat{\nabla} \\ & \quad \cdot\left(\widehat{g} \widehat{G}^{-1} \widehat{\nabla} \widehat{w}\right) \mathrm{d} \xi, \quad b_{2}(\widehat{v}, \widehat{w})=\int_{\widehat{\Omega}} \widehat{v} \widehat{w} \widehat{g} \mathrm{~d} \xi \end{aligned}
$$

with ΔΩ the Laplace-Beltrami operator, c, T > 0 and \(u_{0}(x)\), u \(D(x,t)\) given initial data. The weak formulation of the problem (12) with reference to the parametric space, which will be the target of our IGA simulation, can be obtained with the use of the following form and operator: ⎩ Thus, the weak form of the heat equations can be formu lated as: find \(u \in H^{1}(\Omega)\), where \(u=\left(\hat{u} \circ \mathbf{x}^{-1}\right)(\boldsymbol{\xi})\), such that Thus, the weak form is: find \(u \in H^{2}(\Omega), u=\left(\widehat{u} \circ \mathbf{x}^{-1}\right)(\xi)\) such

$$
and for every \( \widehat{w} \in H^{2}(\widehat{\Omega}) \).
$$

In the experiments that follow, Dirichlet boundary con ditions are enforced strongly on the \(G^{1}\)-spline discretiza tion space, whereas Neumann conditions are applied in the system matrix. Note that our variational forms are semi discrete, and solutions in time are obtained by means of the Crank-Nicolson method.

In the weak formulation of the biharmonic operator, sec ond derivatives appear (see [58,59] for a detailed derivation of the weak form and its solution space). Therefore, having \(C^{1}\) continuity of the basis functions involved in the numeri cal solution of (14) is fundamental for obtaining coherent results.

![Figure 15 Car model. a original MCAD model. b quad mesh extrapo- lated from the MCAD geometry. c point cloud sampling of the origi- nal MCAD model. d surface in solid color. e surface in multipatch](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-15-p013.png)

*Figure 15 Car model. a original MCAD model. b quad mesh extrapo- lated from the MCAD geometry. c point cloud sampling of the origi- nal MCAD model. d surface in solid color. e surface in multipatch: Car model. a original MCAD model. b quad mesh extrapolated from the MCAD geometry. c point cloud sampling of the original MCAD model. d surface in solid color. e surface in multipatch Table 1 Fitting errors, spline space and MCAD model features for the experiments in Figs. 15, 16, 17, 18*

color. \(\mathbf{f}\) error color plot representing the \(\ell_{2}\) distance between the point cloud and the resulting surface. \(\mathbf{g}-\mathbf{h}\) reflection lines around two EVs of different valences pointed out in (e)

## 6 Experimentation

Here we report the numerical experiments to demonstrate the quality of our construction. first we present the least squares fitting procedure to reconstruct a \(G^{1}\) surface from an MCAD point cloud, then we will use the previous result as the geometric domain over which to solve the heat and bihar monic equations using geometrically smooth basis functions in the IGA environment. The proposed functions will lead to optimal convergence rates in isogeometric analysis (equal to 5 for an elliptic problem in the energy norm) when inserting knots uniformly inside each patch. We emphasize that the basis functions are biquintic polynomials on every patch of

![Figure 16 Dream Chaser shuttle model. a input MCAD model. b quad mesh extrapolated from the MCAD geometry. c point cloud sam- pling of the original MCAD model. d surface in solid color. e sur-](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-16-p014.png)

*Figure 16 Dream Chaser shuttle model. a input MCAD model. b quad mesh extrapolated from the MCAD geometry. c point cloud sam- pling of the original MCAD model. d surface in solid color. e sur-: Dream Chaser shuttle model. a input MCAD model. b quad mesh extrapolated from the MCAD geometry. c point cloud sampling of the original MCAD model. d surface in solid color. e sur-*

face in multipatch color. \(\mathbf{f}\) error color plot representing the \(\ell_{2}\) distance between the point cloud and the resulting surface. g, \(\mathbf{h}\) reflection lines around two EVs of different valences pointed out in (e)

![Figure 17 KCS hull model. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-17-p014.png)

*Figure 17 KCS hull model. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface: KCS hull model. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface*

the geometry, but they have a bicubic parametrization on regular patches. However, if each finer model is re-generated from the MCAD (see Sect. 2), the rates of convergence will be bounded by the geometry approximation error made in the process. We refer the reader to [60, Chapter 4] for detailed study and numerical experiments demonstrating this behavior.

![Figure 18 NASA CRM. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-18-p015.png)

*Figure 18 NASA CRM. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface: NASA CRM. a quad mesh extrapolated from the MCAD geometry. b point cloud sampling of the original MCAD model. c surface in solid color. d surface in multipatch color. e error color plot representing the 퓁 2 distance between the point cloud and the resulting surface*

![Figure 19 Solution for the biharmonic equation on the Car model at the instants from T = 0, 0.1, 0.2, 0.3 and T = 0.4 minutes](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-19-p015.png)

*Figure 19 Solution for the biharmonic equation on the Car model at the instants from T = 0, 0.1, 0.2, 0.3 and T = 0.4 minutes: Solution for the biharmonic equation on the Car model at the instants from T = 0, 0.1, 0.2, 0.3 and T = 0.4 minutes*

The CAD models used for the numerical investigation are standard target examples for this type of problem. These are: Car model, \({ }^{1}\) Dream Chaser shuttle model, \({ }^{2}\) KCS hull model \({ }^{3}\) and the NASA CRM. \({ }^{4}\) These are standard open domain mod els that originate from industrial cases.

All of them present special features and sharp edges which are a notable characteristic to be recovered in the 1 https: drexel. edu

2 https: www. sierr aspace. com dreamchaser-space plane 3 http: www. simma n2008. dk kcs conta iner. html 4 https: commo nrese archm odel. larc. nasa. gov fitted surface. The samplings of the original models are obtained following the procedure explained in Sect. 3. In order to obtain a precise result, the target point clouds contain large amounts of data. For the same reason, the control cage obtained from the MCAD (Sect. 2) presents a significant quantity of faces. The models are represented in their original scale, i.e., 1 unit = 1 m. All of the numerical experiments have been performed on three different machines: the first has been devoted to the control cage generation and the MCAD sampling using the software CADfix [61] (C); the second ran the bases computation using Julia language (J) and consequent spline fitting using the G+Smo library

![Figure 20 Solution for the heat equation on the Dream Chaser model at the instants from T = 0 to T = 0.4 min](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-20-p016.png)

*Figure 20 Solution for the heat equation on the Dream Chaser model at the instants from T = 0 to T = 0.4 min: Solution for the heat equation on the Dream Chaser model at the instants from T = 0 to T = 0.4 min*

![Figure 21 Solution for the biharmonic equation on the KCS ship model at the instants from T = 0 to T = 0.4 min](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-21-p016.png)

*Figure 21 Solution for the biharmonic equation on the KCS ship model at the instants from T = 0 to T = 0.4 min: Solution for the biharmonic equation on the KCS ship model at the instants from T = 0 to T = 0.4 min*

![Figure 22 Solution for the heat equation on the NASA CRM at the instants from T = 0 to T = 0.4 min](/Users/evanthayer/Projects/stepview/docs/2024_from_cad_to_representations_suitable_for_isogeometric_analysis_a_complete_pipeline/figures/figure-22-p016.png)

*Figure 22 Solution for the heat equation on the NASA CRM at the instants from T = 0 to T = 0.4 min: Solution for the heat equation on the NASA CRM at the instants from T = 0 to T = 0.4 min*

[62] (G); the third has been used to compute the numerical solution of the heat and biharmonic equations on G+Smo. Respectively, their specifications are: Intel Xeon E3-1240 @ 3.70GHz, 16.0 GB RAM, 4 cores; Intel Core 7-9850 @ \(2.60 \mathrm{GHz}, 16.0 \mathrm{~GB}\) RAM, 6 cores; and Intel Xeon Gold 6230R CPU @ \(2.10 \mathrm{GHz}, 504.0 \mathrm{~GB}\) RAM, 104 cores.

a comparison between the input data and the fitted surface; the fitted surface in solid coloring; the fitted surface in mul tipatch coloring; and a color plot representing the approxi mation error in Euclidean norm. Moreover, Table 1 sum marizes the dimensions of the starting point cloud, control cage and spline space together with the approximation errors evaluated with the formulae in (10). Such errors, for the Car, KCS and NASA CRM models, have been obtained without forcing any smoothing (i.e., \(\lambda=0\) ). For the Dream Chaser model a parameter \(\lambda=0.1\) has been used. From the \(L^{\infty}\) errors represented in Table 1, as well as in the color map of the models' color plot, it can be noticed that the highest errors are located, as expected, around the EVs and near the sharp regions of the MCAD models. This is because we are fitting sharp edges with high smoothness bases which cannot prop erly recreate the actual shape of the model in these regions. In order to increase the quality of the fitting (i.e., decrease the error) and faithfully reproduce the characteristics of the input model, our construction allows us to identify the sharp edges of the MCAD model which are to be preserved. This is automated, owing to the fact that the point cloud sample grid (see Sect. 3) derives directly from the subdivision sur face. Since the control cage maintains an exact topological relationship with the target B-rep, the location of the MCAD edges is known explicitly. Defining on those edges (via, for example, an input list) \(C^{0}\) basis functions only, our output surface will manifest these sharp features. It is important to note that despite the difference in the sizes of the four models, the relative error is always of the same order of magnitude.

```text
Regarding IGA simulations, some experiments with the heat and biharmonic equations have been performed. With reference to (13) and (15), we run the simulations for each of the four MCAD models, considering as the final time the instances T = 0.1, T = 0.2, T = 0.3 and T = 0.4 minutes. These time dependent integrations have been carried out using 20 time steps t step in the Crank-Nicolson method (Tables 1, 2).
```

Figures 19, 20, 21, 22 present the results of the IGA simulations for both the heat (12) and biharmonic (14) equations. These are obtained by setting, as initial conditions, a heat source at the likely location of the engines within the various vehicles represented. This demonstrates a realistic analysis of the thermal behavior of such models. Moreover, Table 2 presents the running times required to compute each fragment of the pipeline.

## 7 Conclusion

This work serves as a proof of concept for unifying isogeometric analysis and subdivision surfaces as enabling technologies for simulation. We presented a complete and efficient pipeline to convert MCAD models into \(G_{1}\) smooth objects which are suitable for isogeometric analysis simulations. Starting from an MCAD object, we first produce a quad mesh whose Catmull-Clark limit surface adequately approximates the input geometry. Guided by this limit surface we compute a point cloud sampling of the MCAD model, which is fitted with the use of basis functions defined over the previously extracted quad mesh, in a least squares approach. The obtained spline surface and the \(G_{1}\) basis are used to run IGA simulations. To demonstrate the quality of the fitting, various numerical experiments derived from real MCAD models are provided with their error measurements. We illustrate the IGA simulations for the heat and biharmonic equations in real-life situations, highlighting the suitability of our approach for analysis.

Our process features the translation of traditional MCAD B-rep to a format more suitable for CAE applications. The technique aims to reproduce the originating B-rep, maintaining all prior topological relationships. This exposes the sensitivity of our method to both the complexity and the quality of the input geometry (in particular, the presence of sliver faces). As an area of future study, we highlight the potential of employing virtual topology [63] for mitigating the impacts of these artefacts by suppressing unnecessary topological features.

The exploitation of alternative geometric representations underpins the notion of a hybrid modeling approach. We anticipate that these alternative representations will become increasingly integrated into the design, analysis, and optimization stages of product development. Con sequently, this will simplify the workflow, boost perfor mance and productivity, and reduce time to market. How ever, a realistic expectation within industry would be to produce an MCAD B-rep representation as the end result, as typically mandated by many manufacturing processes. Therefore, the original MCAD model must be updated to reflect the results of the design optimization process. Our \(G^{1}\) quad mesh spline representation maintains an exact topological associativity with the original B-rep, therefore lending itself to a convenient route back to a traditional MCAD B-rep representation without altering the topology. We propose this as an important topic for further study, as it would complete the tool set for employing a hybrid modeling approach within an industrial setting.

Acknowledgements The authors acknowledge the contribution of the European Union's Horizon 2020 research and innovation program under the Marie Skłodowska-Curie project GRAPES (No. 860843). MM is a member of the INdAM research group GNCS, Italy. MM acknowledges the support of the Italian Ministry of University and Research (MUR) through the PRIN project NOTES (No. P2022NC97R), funded by the European Union-Next Generation EU. SW and MG acknowledge the ATI IUK project COLIBRI (No. 46349).

Funding Open access funding provided by Università degli Studi di Firenze within the CRUI-CARE Agreement.

Data availability The data that support the findings of this study are available on request from the corresponding author, MM. The data are not publicly available due to confidentiality restrictions.

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http: creativecommons.org licenses by 4.0.

## References

- Boggs P, Althsuler A, Larzelere A, Walsh E, Clay R (2005) Hardwick M, DART system analysis., Tech Rep SAND2005-4647 (OSTI)

- Cottrell J, Hughes T, Bazilevs Y (2009) Isogeometric analysis: toward integration of CAD and FEA, John Wiley & Sons, Ltd

- Bianconi F, Conti P, Di Angelo L (2006) Interoperability among CAD CAM CAE systems: a review of current research trends, In: Geometric Modeling and Imaging-New Trends (GMAI'06), pp. 82-89

- Zorin D, Schröder P, Derose A, Kobbelt L, Levin A, Sweldens W (2000) Subdivision for modeling and animation, course Notes of SIGGRAPH

- Peters J, Reif U (2008) Subdivision surfaces. Springer

- Bandara K, Rüberg T, Cirak F (2016) Shape optimisation with multiresolution subdivision surfaces and immersed finite elements. Comput Methods Appl Mech Eng 300:510-539

- Catmull E, Clark J (1978) Recursively generated B-spline surfaces on arbitrary topological meshes. Copmut-Aided Des 10(6):350-355

- Nasri A, Sabin M, Zaki RA, Nassiri N, Santina R (2006) Feature curves with cross curvature control on Catmull-Clark subdivision surfaces. In: Nishita T, Peng Q, Seidel H-P (eds) Advances in computer graphics. Springer, Berlin Heidelberg, Berlin, Heidelberg, pp 761-768

- Shen J, Kosinka J, Sabin M, Dodgson N (2014) Conversion of trimmed NURBS surfaces to Catmull-Clark subdivision surfaces. Comput Aided Geom Design 31(7-8):486-498

- Frey P, George P (2008) Mesh generation. Wiley

- Ali Z, Tyacke J, Tucker P, Shahpar S (2016) Block topology generation for structured multi-block meshing with hierarchical geometry handling. Procedia Eng 26:212-224

- Geuzaine C, Remacle J (2009) Gmsh: A 3-D finite element mesh generator with built-in preand post-processing facilities. Int J Numer Meth Eng 79(11):1309-1331

- Wang W, Zhang Y, Scott MA, Hughes TJR (2011) Converting an unstructured quadrilateral mesh to a standard T-spline surface. Comput Mech 48(4):477-498

- Lai Y, Liu L, Zhang YJ, Chen J, Fang E, Lua J (2016) Rhino 3D to Abaqus: A T-spline based isogeometric analysis Software Framework. Springer International Publishing, Cham, pp 271-281 Casquero H, Wei X, Toshniwal D, Li A, Hughes TJ, Kiendl J, Zhang YJ (2020) Seamless integration of design and KirchhoffLove shell analysis using analysis-suitable unstructured T-splines. Comput Methods Appl Mech Eng 360:112765 Hiemstra RR, Shepherd KM, Johnson MJ, Quan L, Hughes TJ (2020) Towards untrimmed nurbs: CAD embedded reparameterization of trimmed b-rep geometry using frame-field guided global parameterization. Comput Methods Appl Mech Eng 369:113227 Shepherd KM, Gu XD, Hughes TJ (2022) Feature-aware reconstruction of trimmed splines using ricci flow with metric optimization. Comput Methods Appl Mech Eng 402:115555 Shepherd KM, Gu XD, Hughes TJ (2022) Isogeometric model reconstruction of open shells via ricci flow and quadrilateral layout-inducing energies. Eng Struct 252:113602 Urick B, Marussig B, Cohen E, Crawford RH, Hughes TJ, Riesenfeld RF (2019) Watertight boolean operations: a framework for creating CAD-compatible gap-free editable solid models. Comput Aided Des 115:147-160 Wobbes E, Bazilevs Y, Kuraishi T, Otoguro Y, Takizawa K, Tezduyar TE (2023) Advanced IGA mesh generation and application to structural vibrations. Springer International Publishing, Cham, pp 513-531 Bommes D, Lempfer T, Kobbelt L (2011) Global structure optimization of quadrilateral meshes. Comput Graph Forum 30(2):375-384 Tarini M, Puppo E, Panozzo D, Pietroni N, Cignoni P (2011) Simple quad domains for field aligned mesh parametrization. ACM Trans Graph 30(6):1-12 Couplet M, Reberol M, Remacle J (2021) Generation of highorder coarse quad meshes on CAD models via integer linear programming, In: AIAA AVIATION 2021 FORUM, American Institute of Aeronautics and Astronautics Yu Y, Wei X, Li A, Liu JG, He J, Zhang YJ (2022) HexGen and Hex2Spline: Polycube-based hexahedral mesh generation and spline modeling for Isogeometric analysis applications in LSDYNA. In: Manni C, Speleers H (eds) Geometric challenges in isogeometric analysis. Springer International Publishing, Cham, pp 333-363 Wei X, Zhang YJ, Toshniwal D, Speleers H, Li X, Manni C, Evans JA, Hughes TJ (2018) Blended B-spline construction on unstructured quadrilateral and hexahedral meshes with optimal convergence rates in isogeometric analysis. Comput Methods Appl Mech Eng 341:609-639 Xie J, Xu J, Dong Z, Xu G, Deng C, Mourrain B, Zhang YJ (2020) Interpolatory Catmull-Clark volumetric subdivision over unstructured hexahedral meshes for modeling and simulation applications. Comput Aided Geom Design 80:101867 Sederberg T, Zheng J, Sewell D, Sabin M (1998) Non-uniform recursive subdivision surfaces, In: Proceedings of the 25th annual conference on Computer graphics and interactive techniques-SIGGRAPH '98, ACM Press Cashman T, Augsdörfer U, Dodgson N, Sabin M (2009) NURBS with extraordinary points. ACM Trans Graph 28(3):1-9 Cashman T, Dodgson N, Sabin M (2009) A symmetric, nonuniform, refine and smooth subdivision algorithm for general degree B-splines. Comput Aided Geom Design 26(1):94-104 Marussig B, Hughes TJR (2017) A review of trimming in isogeometric analysis: Challenges, data exchange and simulation aspects. Arch Comput Methods Eng 25(4):1059-1127 Ma Y, Ma W (2019) A subdivision scheme for unstructured quadrilateral meshes with improved convergence rate for isogeometric analysis. Graph Models 106:101043 Loop C, Schaefer S (2008) Approximating Catmull-Clark subdivision surfaces with bicubic patches. ACM Trans Graph 27(1):8:1-8:11

- Peters J (2000) Patching Catmull-Clark meshes, in: Proceedings of the 27th Annual Conference on Computer Graphics and Interactive Techniques, SIGGRAPH '00. ACM Press AddisonWesley Publishing Co, NY, USA, pp. 255-258

- Fan J, Peters J (2008) On smooth bicubic surfaces from quad meshes. International symposium on viual computing. Springer, Cham, pp 87-96

- Peters J, Fan J (2010) On the complexity of smooth spline surfaces from quad meshes. Comput Aided Geom Design 27(1):96-105

- Hahmann S, Bonneau G, Caramiaux B (2008) Bicubic G 1 interpolation of irregular quad meshes using a 4-split. International Conference on Geometric Modeling and Processing. Springer, Cham, pp 17-32

- Bonneau G, Hahmann S (2014) Flexible G 1 interpolation of quad meshes. Graph Models 76(6):669-681

- Karčiauskas K, Peters J (2017) Improved shape for refinable surfaces with singularly parameterized irregularities. Comput Aided Des 90:191-198

- Marsala M, Mantzaflaris A, Mourrain B (2022) G 1-smooth biquintic approximation of Catmull-Clark subdivision surfaces. ComputAided Geom Design 99:102158

- Alfeld P, Schumaker L (1987) The dimension of bivariate spline spaces of smoothness r for degree d ≥ 4 r + 1. Constr Approx 3(2):189-197

- Hong D (1991) Spaces of bivariate spline functions over triangulation. Approx Theory Appl 7(1):56-75

- Schumaker L (1984) Bounds on the dimension of spaces of multivariate piecewise polynomials. Rocky Mountain J. Math. 14(1):251-264

- Lai M, Schumaker L (2007) Spline functions on triangulations, vol 110. Cambridge University Press, Cambridge, Encyclopedia of Mathematics and its Applications

- Mourrain B, Villamizar N (2013) Homological techniques for the analysis of the dimension of triangular spline spaces. J Symb Comput 50:564-577

- Mourrain B, Vidunas R, Villamizar N (2016) Geometrically continuous splines for surfaces of arbitrary topology. Comput Aided Geom Design 45:108-133

- Kapl M, Sangalli G, Takacs T (2017) Dimension and basis construction for analysis-suitable G 1 two-patch parameterizations. Comput Aided Geom Design 52-53:75-89

- Kapl M, Sangalli G, Takacs T (2019) Isogeometric analysis with C 1 functions on planar, unstructured quadrilateral meshes. SMAI J Comput Math S 5:67-86

- Kapl M, Sangalli G, Takacs T (2019) An isogeometric C 1 subspace on unstructured multi-patch planar domains. Comput Aided Geom Design 69:55-75 Blidia A, Mourrain B, Villamizar N (2017) G 1-smooth splines on quad meshes with 4-split macro-patch elements. Comput Aided Geom Design 52-53:106-125 Blidia A, Mourrain B, Xu G (2020) Geometrically smooth spline bases for data fitting and simulation. Comput Aided Geom Design 78(101814):15 Marsala M, Mantzaflaris A, Mourrain B (2024) G 1 spline functions for point cloud fitting. Appl Math Comput 460:128279 Sheehy DJ, Armstrong CG, Robinson DJ (1995) Computing the medial surface of a solid from a domain delaunay triangulation, in: Proceedings of the Third ACM Symposium on Solid Modeling and Applications, SMA '95, Association for Computing Machinery, New York, NY, USA, p. 201-212 Gordon W, Hall C (1973) Construction of curvilinear coordinate systems and application to mesh generation. Int J Num Methods Eng 7:461-477 Farin G, Hoschek J, Kim M-S (2002) Handbook to Computed Aided Geometric Design. North Holland Stam J (1998) Exact evaluation of Catmull-Clark subdivision surfaces at arbitrary parameter values, in: Proceedings of the 25th annual conference on Computer graphics and interactive techniques-SIGGRAPH '98, ACM Press Bercovier M, Matskewich T (2017) Smooth Bézier surfaces over unstructured quadrilateral meshes. Springer International Publishing, Lecture Notes of the Unione Matematica Italiana Dedè L, Quarteroni A (2015) Isogeometric analysis for second order partial differential equations on surfaces. Comput Methods Appl Mech Eng 284:807-834 Ciarlet PG (2002) The finite element method for elliptic problems, SIAM Kapl M, Vitrih V, Jüttler B, Birner K (2015) Isogeometric analysis with geometrically continuous functions on two-patch geometries. Comput Math Appl 70(7):1518-1538 Marsala M (2023) Modeling, approximation and simulation using smooth splines on unstructured meshes, PhD thesis, Université Côte d'Azur CADfix, https: www. itiglobal. com cadfix Mantzaflaris A (2020) An overview of geometry plus simulation modules. Math Asp Comput Inform Sci. Springer International Publishing, Cham, pp 453-456 Sheffer A, Bercovier M, Blacker T, Clements J (2000) Virtual topology operators for meshing. Int J Comput Geometry Appl 10(03):309-331 Publisher's Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.
