# Entity-Based Aspect Graphs: Making Viewer Centered Representations More Efficient

[missing from original]

[missing from original]

## Abstract

The aspect graph, a graphical representation of an object's characteristic views has been widely developed by several researchers. However, researchers have stated that aspect graphs are limited due to their high complexity and computational cost. A simple non-convex object, such as a step, has 71 distinct characteristic views (nodes in the aspect graph); more complicated objects could have thousands of characteristic views (nodes). Many characteristic views of an aspect graph are not necessary for many applications. In this paper, a new entity-based aspect graph, EAG, is proposed based on the observation that, for most applications, the visibility of only some of the entities on the object is important. The objects of interest are polyhedral solids. We present algorithms for constructing new entity-based aspect graphs based on the faces, edges and vertices of the object, and for combining and contracting previously constructed EAGs in a database to generate EAGs for new objects. The computation time for construction is reduced, yet sufficient information is provided to the application. © 1998 Elsevier Science B.V. All rights reserved

## Introduction

The aspect graph, AG, is a viewer-centered representation of an object based on concepts generally attributed to Koenderink and van Doorn (1979). Each node of an AG corresponds to a distinct characteristic view domain, and each arc between a pair of nodes represents the adjacency between the corresponding characteristic view domains. Each characteristic view domain has a "topologically distinct" view of the object. algorithms have been derived to create AGs for three-dimensional objects by following specific rules to partition the three-dimensional space. Detail literature reviews of aspect graph can be found in (Bowyer and Dyer, 1990). The problem with the AG is its complexity and its limited practical utility. A simple object may have more than a hundred nodes in its aspect graph. The worst-case node complexity is \(O(Nº)\) for an N-faced polyhedron. In the 1991 IEEE Workshop on Directions in Automated CAD-Based Vision (Bowyer, 1991), researchers have discussed why aspect graphs are not (yet) practical for computer vision in a panel. Therefore, an efficient viewer-centered representation of objects, which satisfies the requirements of its intended application, is desired. In most applications of the aspect graph, only a small fraction of the characteristic views are necessary. Most applications focus on a small fraction of the object of interest. For visual inspection, only the entities that are important for the function of the part are inspected or dimensioned. For example, the length, width and height of a pocket on an object are the entities that are important for computing the volume (function) of the pocket. The observability of other entities on the object is not necessary in this situation. For object recognition, many objects are given, some of which may have common features. However, only the observability of the entities that are related to the unique features on the objects is important for identifying them. In these applications, a reduced aspect graph, which focuses on only the important portion of an object would be of much better practical importance.

### 1.1 Related aspect graph work

Several researchers have modified aspect graphs in order to reduce their complexity. These modified aspect graphs are based on the properties that are observed in their applications. For example, some characteristic view domains may be so small that they are hardly useful and some characteristic views for which the observable edges correspond to the same line drawings are considered redundant for object recognition. Weinshall and Werman (1997) define view likelihood and view stability, which are used to identify characteristic views and generic views, respectively. View likelihood measures the probability that a certain view of a given 3D object is observed and view stability measures how little the image changes as the viewpoint is slightly perturbed. Eggert et al. (1993) introduces the scale space aspect graph, which incorporates a quantitative measure of scale into the qualitative representation of the AG used. The method based on scale assumes that some characteristic views will never be useful because of the size of the domains or the limited visibility of the entities in the object. Using this approach reduces the large set of theoretical aspects to a smaller set of the more significant aspects.

Shimshoni and Ponce (1997) introduce the finiteresolution aspect graphs for polyhedral objects. The finite-resolution aspect graphs are developed based on the ideas that (i) an edge is observable when its visible portion projects onto a segment of length greater than a threshold, (ii) two vertices are distinct when the distance between their projections in the image is greater than a threshold. The threshold is determined based on the resolution of camera. As a result, adjacent regions in classical aspect graph with identical finite-resolution views aspects are merged to produce the finite-resolution aspect graph. However, orthographic camera is used in the finite-resolution aspect graphs. Orthographic model is more limited than the full-perspective model used in the scale-space aspect graph developed by Eggert et al. (1993).

Laurentini (1995) introduced the reduced aspect graph. For topological identification of polyhedral objects from multiple views, nodes in the aspect graph, which represent the same line drawing are redundant. Therefore, any pair of nodes in the aspect graph is merged if their aspects are given the same labels and they are topologically equivalent. The scale space aspect graph, the finite-resolution aspect graph, and the reduced aspect graph approaches reduce the size of the aspect graph. However, for the application of sensor placement (Yang et al., 1994; Yang and Marefat, 1995; Tarabanis et al., 1995a,b; Trucco et al., 1997) in visual inspection and for object recognition, some unnecessary information is retained and some useful information is lost. A new entity-based aspect graph, which shows only the characteristic views of the entities of interests, is desired. The scale space aspect graph (Eggert et al., 1993) has eliminated characteristic views in which the visibility of the entities is low or the size of the characteristic domains is too small. The finite-resolution aspect graph (Shimshoni and Ponce, 1997) has merged adjacent regions that have identical finite-resolution view aspects. However, the scale space aspect graph and the finite-resolution aspect graph still include many characteristic views representing unnecessary entities in the graph. Thus for application purposes, they can still be further reduced to a smaller size. The reduced aspect graph (Laurentini, 1995) merges the characteristic views (nodes) that have the same line drawings, however, the lines in the line drawings could represent different entities (edge segments) on the object. This results in the identities of the entities in the characteristic views being lost. Consequently, this reduced aspect graph is not appropriate for determining the sensor parameters for inspecting a desired geometric entity. In order to provide sufficient information and reduce the complexity, an aspect graph, which provides all the distinct characteristic views of the object for a set of geometric entities of interests is desired.

### 1.2 Our contributions

In this paper, we propose the entity-based aspect graph, EAG, in each of which the nodes show only the distinct characteristic views for a set of desired entities. AGs are used for recognizing objects and determining the sensor placement for observing object's entities. Only the observability for the entities of interest is important for these applications, so any characteristic views, which do not differ in their views of the desired entities will not be necessary. In this paper, the entities of interest are selected by the users instead of automatically computed. EAGs reduce the complexity of creating the aspect graph, yet provide enough information for applications.

The contributions of this paper can be summarized as:

- Introducing a new entity-based aspect graph based on the assumption that only the observability of some entities of interest is useful for applications.

- algorithm for creating an EAG from the faces, edges and vertices of an object is presented algorithms are also provided for reusing previously constructed EAGs by contraction and combination. Constructing an aspect graph by using previously built aspect graphs has not previously been proposed. Such a technique allows aspect graphs to be formed more efficiently while allowing the earlier-built aspect graphs to be reused.

- An analysis of the complexity of computing the EAG is presented. It is shown that complexity is decreased, especially significantly when the enti-

ties of interest in the EAG is small compared to all the entities of the original AG.

## 2 Aspect graph and entity-based aspect graph

The AG is used in application to recognize objects and determine sensor placements that allow observation of certain entities of an object without occlusion. For example, given the model of an object, Yang et al. (1994) and Yang and Marefat (1995) utilized the AG for determining the sensor location and orientation that can observe a set of desired entities of the object. In most applications, given the entities of interest, only some of the characteristic views in the complete aspect graph are important. Hence, one can construct the characteristic view domains for these entities of interest and form an aspect graph such that each node of the graph is concerned with only the visibility of these entities. Using this approach, fewer characteristic view domains are formed and less computation time is needed, yet sufficient information is provided for the purpose of the application. The proposed entitybased aspect graph is based on the assumption that only some entities or features of the object are used in an application. The AG is a pair ( \(C, A\) ) where \(C\) is the set of the characteristic view domains represented as nodes, \(\left\{C_{1}, C_{2}, C_{3}, \ldots\right\}\), and \(A\) is the set of the adjacent pairs of characteristic view domains represented as arcs, \(\left\{\ldots,\left(C_{i}, C_{j}\right), \ldots\right\}\). The EAG is a quadruple \((E, V, O, A). E\) is a set of entities of interest for the object, \(\left\{\ldots, e_{i}, \ldots, e_{j}, \ldots\right\}\), such that the EAG only provides the observability of these entities. \(V\) is a set of viewing domains, \(\left\{V_{1}, V_{2}, V_{3}, \ldots\right\}\), in the three-di mensional space. \(O\) is the set of observable lists of entities for each element in \(V,\left\{O_{v_{1}}, O_{v_{2}}, O_{v_{3}}, \ldots\right\}\), where \(O_{v_{i}}\) is the list of observable entities of entity viewing domain \(V_{i}\). An entity is observable in an entity viewing domain only if no portion of this entity is occluded. Similar to the AG, \(A\) is the set of adjacent pairs of entity viewing domain, \(\left\{\ldots,\left(V_{i}, V_{j}\right), \ldots\right\}\). In this paper, the domain of con sidered objects are restricted to planar-faced solids.

Freeman (1990) and Bowyer et al. (1988, 1993) developed algorithms to construct AG for planarfaced solids. Basically, there are three types of partitioning rules for determining the characteristic view domains. Bowyer has described two visual events, the edge-vertex (EV) event and the edge-edge-edge (EEE) event. These visual events are similar to the partitioning types (type A, type B, type C), developed by Freeman. The EV events contain two categories. One involves edge-vertex pairs on the same face and the other involves pairs on separate faces. The first and second category of the EV event corresponds to the type-A partition surfaces and type-B partition barriers of Freeman's method, respectively. The EEE event is the general case where three edges share no common vertex and it corresponds to the type-C quadric surfaces.

The partition rules introduced by Freeman and Bowyer divided the three-dimensional space into regions such that each region (characteristic view domain) has a distinct view of the object. Each partition plane or surface is constructed based on the edges and or vertices of the object to divide the space into two regions. The vantage points from one region are able to observe the corresponding edges or vertices but the vantage points from the other region are unable to do so. To view a face of a convex planar-faced solid, the vantage point is located at the positive side of the face. The positive side of the face is defined as the half space exterior to the object. Type-A partition surface developed by Freeman (1990) is obtained by expanding the object faces. This partitioning rule is the only rule required for convex planar-faced solids. For non-convex solids, two additional partitioning rules, type-B partition barriers and type-C partition quadric surfaces are needed. Type-B partition barriers are used to separate the vantage points, which have the same visible set of faces but different visible set of vertices. The barrier is a bounded planar region formed by the vertices and edges of the non-convex part of the object. The visibility status of the vertices and the edges are determined by which side of the bounded barrier the vantage point is located. Type-C partition quadric surfaces are used to separate the vantage points, which have the same visible set of faces and vertices but different structural features. For planar-faced solids, a T-junction on the image is a virtual junction that is not a real vertex of the object. The visibility of a T-junction formed by two non-adjacent edges is determined by type-C partition quadric surfaces. Given three edge lines of the model, ey, ez and ez, a straight line may pass through all the edges with points Pi, P2 and P3 as the intersection points of the straight line with the edges ey, ez and ez, respectively. The partitioning surfaces are composed of infinite number of these straight lines that intersect with the edges e,, ez and ez. The T-junction is visible from one half space and invisible from the other half space.

Given a set of entities of interest (EOI), one can use all the partition planes and surfaces of the object and eliminate those that are not necessary for constructing the EAG of the object. These partition planes or surfaces formed by the vertices and edges, which are not elements of the set of EOI are eliminated, because the formed planes and surfaces partition only the regions having different observability with respect to the entities that are not in the EOI The domain formed is possibly the combination of several characteristic-view domains of the AG. Although each domain may contain more than one characteristic view of the object; each of these characteristic views will observe the same entities in the set E of the EAG.

```text
Algorithm for constructing EAG with EOI = E Input: The boundary representation of the object (vertices, edges and faces). Output: An EAG with set of viewing domains, \( V \), set of lists of observable entities, \( O \), one list for each element of \( V \), and set of adjacent pairs of viewing domain, \( A, \mathrm{EAG}(E, V, O, A) \).
```

- Find all the partition planes and surfaces (using type-A, type-B and type-C partition planes and surfaces described by Freeman (1990)) and eliminate those generated by entities that are not elements of E, i PI, P2,..., Pni.

- Construct all possible n-tuples, Pz,..., Pr, where pi, Pi are inequalities denoting the different half spaces of the partition plane pr

3. For each \(n\)-tuple, determine the feasibility of the three-dimen sional region described by the \(n\)-tuple. (If a point cannot belong to the corresponding set of \(n\) inequalities, the region is infeasible.) If such an \(n\)-tuple is feasible,

## 4 For each pair of elements in V,

![Figure 1. (a) An object with a blind step. (b) AG of object in (a). (c)EAG with E=(e.ez.ez.e,. eg. eg. eg.0j."2."g."g."g.46.07) as labeled in](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-1-p005.png)

*Figure 1. (a) An object with a blind step. (b) AG of object in (a). (c)EAG with E=(e.ez.ez.e,. eg. eg. eg.0j."2."g."g."g.46.07) as labeled in: (a) An object with a blind step. (b) AG of object in (a). (c)EAG with E=(e.ez.ez.e,. eg. eg. eg.0j."2."g."g."Fig. 46.07) as labeled in Table 1 The list of observable entities in each of the viewing domains of the entity-based aspect graph shown in Fig. 1(c) withE=(e,e2,e3, eg, eg, es, e7.01,02,03,04.05,06,01) as labeled in (a).*

![Figure 2. (a) An object with a pocket on the top face. (b) The](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-2-p006.png)

*Figure 2. (a) An object with a pocket on the top face. (b) The: (a) An object with a pocket on the top face. (b) The entity-based aspect graph of the object in (a) with the set of entities of interest as {Ly, Lz, Lz, Lq, W,, W2, W, W4, H,, Hz, Hz, H,).*

## 3 Construction of entity-based aspect graph by contraction and combination of previously computed EAGs

![Figure 3. The characteristic views of four nodes in the aspect graph in Figure I(b). (a) Characteristic view of node 9. (b) Characteristic view of](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-3-p006.png)

*Figure 3. The characteristic views of four nodes in the aspect graph in Figure I(b). (a) Characteristic view of node 9. (b) Characteristic view of: The characteristic views of four nodes in the aspect graph in Fig. I(b). (a) Characteristic view of node 9. (b) Characteristic view of Table 2 The sets of observable entities in each viewing domain of the entity-based aspect graph of the object in Fig. 2(a) 1(b). (a) Characteristic view of node 9. (b) Characteristic view of node 14. (c) Characteristic view of node 33. (d) Characteristic view of node 39.*

![Figure 4. (a) An object with two pockets, Pocket 1 and Pocket 2, (b) the labels for the entities of Pocket 1 and entities of Pocket 2, (c) EAG](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-4-p007.png)

*Figure 4. (a) An object with two pockets, Pocket 1 and Pocket 2, (b) the labels for the entities of Pocket 1 and entities of Pocket 2, (c) EAG: (a) An object with two pockets, Pocket 1 and Pocket 2, (b) the labels for the entities of Pocket 1 and entities of Pocket 2, (c) EAG with E= (en, ez, 0з, eyes,,, 8, 00, 00, 0½·02›93,01¼·50607018,019, ez0, 021·022; €23, €24}.*

tions of the entity viewing domains from different EAGs, constructing new partition planes or surfaces as necessary, and creating new nodes and arcs.

### 3.1 Contraction

Using the contraction technique, the process of determining the characteristic viewing domains from the parti tioning planes or surfaces is no longer necessary. The new EAG is constructed by manipulating the EAG in the database.

The contraction of a graph, G\ a, is obtained by removing an arc a and identifying the nodes, n, and n2, which are incident to the arc a. The resulting node, nz, is then incident to those arcs, which were originally incident to n, and n2. Assume E'= (eeek...) and E= lee, ex), and E is a subset of \(E(EcE')\), therefore, EAG' can be constructed by contracting EAG'. Let us assume that EAG' = {E', V',0' , Al and EAG? = (E,V2,02,A) V=1010z0j..0j..,0n 0 = 10,, 00г...,0,...,OA = and (ul,o)) is an element of A, ul and of are contracted to produce a new node u?, O? is equal to (O,,nE). (ul,o)) is deleted from the set of adjacencies. u, is substituted for uf and of if any elements of the set of adjacencies contain v, or 0j. For example, the EAG in Fig. 1(c) is a contraction of the AG in Fig. 1(b)

```text
Algorithm for contraction of entity-based as pect graph \( \mathrm{EAG}^{1} \) to construct \( \mathrm{EAG}^{2} \) (where \( \left.E^{2} \subseteq E^{1}\right) \) CONTRACT_EAG(EAG \( { }^{1} \) )
```

- Initialize EAG Set V2 = V', 0'= 0', A = A'

```text
Input: \( \mathrm{EAG}^{1}\left(E^{1}, V^{1}, O^{1}, A^{1}\right), E^{2} \) Output: \( \operatorname{EAG}^{2}\left(E^{2}, V^{2}, O^{2}, A^{2}\right) \) 1. Initialize \( \mathrm{EAG}^{2} \)
```

### 3.2 Combination

If the EAGs of higher level generic shape features, such as slots, pockets, steps, etc. are stored in a database, one can easily construct the EAG of an object with an aggregation of such geometric features by combining the appropriate EAGs available in the database. Using the combination techniques, the EAGs of the more complicated objects with multiple features can be generated more efficiently. Let us assume that EAG' = {E,V', ',O', 4') and EAG' = (E, V2,0', A2) are available. One can form EAG3 = {E?,V3,03, 4'), such that the entities of interest for this new EAG, E = EUE, by combining EAG' and EAG? . Given V = 101,02, v},...,u},...,Um), if the intersection of the entity viewing domains, uf and j, is not an empty space (v) nu} +Ø), new viewing domains are formed based on their intersection in three-dimensional space. New viewing domains can also be formed by new partition planes or surfaces created by the entities in E' and E. The new partition planes or surfaces intersect with the existing partition planes and surfaces to create new viewing domains. V is the union of all v, and v, that do not intersect with the new viewing domains, and the newly formed viewing domains. The adjacencies in A3 are reconstructed based on the common surfaces shared with the new viewing domains. The algorithm to determine the intersection of two three-dimensional regions is described by Mäntyla (1988) in detail.

algorithm for combination of entity-based aspect graphs EAG' and EAG' to construct EAG

```text
Input: \( \mathrm{EAG}^{1}\left(E^{1}, V^{1}, O^{1}, A^{1}\right) \), \( \mathrm{EAG}^{2}\left(E^{2}, V^{2}, O^{2}, A^{2}\right), E^{3}=E^{1} \cup E^{2} \) COMBINE_EAG(EAG \( { }^{1} \), EAG \( ^{2} \) )
```

\(\mathrm{EAG}^{2}\left(E^{2}, V^{2}, O^{2}, A^{2}\right), E^{3}=E^{1} \cup E^{2}\)

- Initialize EAG Set V3 = (), 03= (), 43 = ().

```text
Output: \( \mathrm{EAG}^{3}\left(E^{3}, V^{3}, O^{3}, A^{3}\right) \) 1. Initialize \( \mathrm{EAG}^{3} \)
```

- Combine EAG' and EAG For every element in V', Vi, and every element in V2, V2,

![Figure 5. (a) An object with two steps and a pocket. (b) The](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-5-p009.png)

*Figure 5. (a) An object with two steps and a pocket. (b) The: (a) An object with two steps and a pocket. (b) The entity-based aspect graph with E=(ee2, e3, eg. es. e6), in (a).*

$$
Add Va= Vin V and V" = V2 - (Vin v3) to V3
$$

Add \(V_{k}=V_{i}^{1} \cap V_{j}^{2} \quad\) and \(\quad V_{k}^{\prime}=V_{i}^{1}-V_{i}^{1} \cap V_{j}^{2}\) from to \(V^{3}\).

```text
The viewing domain formed by \( V_{k}^{\prime}=V_{i}^{1}-V_{i}^{1} \cap V_{j}^{2} \) has a list of observable entities \( O_{V_{k}^{\prime}}=
```

```text
The viewing domain formed by \( V_{k}=V_{i}^{1} \cap V_{j}^{2} \) has a list of observable entities \( O_{V_{k}}=O_{V_{i}}^{1} \cap
```

```text
The viewing domain formed by \( V_{k}^{\prime \prime}=V_{j}^{2}-V_{i}^{1} \cap V_{j}^{2} \) has a list of observable entities \( O_{V_{k}^{\prime \prime}}=
```

- If the entities of E' and E? form any new partition planes,

```text
Construct the new partition planes. Find and add to \( V^{3} \) the new viewing domains generated by these partitions. (The new viewing domains are formed by the new partition planes and the existing partition planes using the technique described in Section 2.)
```

- For every pair of viewing domains in V3, (V' V, ) If V; and V share a common surface on the boundaries, add (V,,V,) to A.

Fig. 4 shows an object with two pockets. Pocket 1 is on the top face and Pocket 2 is on one of the side faces. Each of the EAGs, EAG \({ }^{\text {Pocket1 }}\) and EAG \({ }^{\text {Pocket2 }}\), based on the entities of Pocket1, \(\left\{L_{1}, L_{2}, L_{3}, L_{4}, W_{1}, W_{2}, W_{3}, W_{4}, H_{1}, H_{2}, H_{3}, H_{4}\right\}\), and the entities of Pocket2, \(\left\{L_{5}, L_{6}, L_{7}, L_{8}, W_{5}, W_{6}, W_{7}, W_{8}, H_{5}, H_{6}, H_{7}, H_{8}\right\}\), is iso morphic to the EAG which is shown in Fig. 2(b). Each, EAG \({ }^{\text {Pocket1 }}\) and EAG \({ }^{\text {Pocket2 }}\), provides a viewer-centered representation in which the only en tities of interest are those of one of these pockets along with the viewing domains for an object having one such pocket. However, the description of the viewing domains and the visibility of entities for an object having both of such pocket features, both Pocket1 and Pocket2, is not provided in EAG \({ }^{\text {Pocket1 }}\) or EAG \({ }^{\text {Pocket2 }}\). In order to obtain the viewing domain for an object having both such pockets, a new EAG, EAG \({ }^{\text {Pocket1 } \cup \text { Pocket2 }}\), is necessary. EAG \({ }^{\text {Pocket1 } \cup \text { Pocket2 }}\) can be constructed by combining EAG \({ }^{\text {Pocket1 }}\) and EAG \({ }^{\text {Pocket2 }}\). Fig. 4(c) shows the resulting EAG \({ }^{\text {Pocket1 } \cup \text { Pocket2 }}\), which is obtained from applica tion of the combination algorithm described. The visibility of the entities for the nodes (viewing do mains) in Fig. 4(c) is given in Table 3. The combination algorithm is restricted to combine EAGs where the higher level features such as pockets, or steps, are not interacting with each other on the new object. For example, if the EAG for a step is available and a new object has two steps intersecting with one another, combining two EAGs the available step does not create the EAG for the new object. The reason for this is because new edge segments (new entities) are generated when two steps intersect one another. The presented algorithm should be used only to combines EAGs when the higher level features do not intersect on the new object.

## 2 Determine the visibility of the entities in E for each element in V2

```text
For every element of \( O^{2} \), Update the list of observable entities to be the intersection of the original list of observ able entities and \( E^{2} .\left(O_{v_{i}}^{2}=O_{v_{i}}^{1} \cap E^{2}\right) \)
```

3. Contract the adjacent viewing domains if their observable entities are the same

If the updated lists of observable entities for the two adjacent entity viewing domains, \(V_{i}^{2}\) and \(V_{j}^{2}\), are the same, \(\left(O_{v_{i}}^{2}=O_{v_{j}}^{2}\right)\) Remove \(O_{v_{i}}^{2}\) and \(O_{v_{j}}^{2}\) from \(O^{2}\) Remove the current arc of \(\mathrm{EAG}^{2},\left(V_{i}^{2}, V_{j}^{2}\right)\), from \(A^{2}\) For every element of \(A^{2}\), substitute \(V_{i}^{2}\) and

Fig. 3 shows four characteristic views from the aspect graph in Fig. 1(b) which are contracted into one characteristic view for the EAG in Fig. 1(c). The intersection of the observable entities in these char acteristic views and the set of entities of interest of the EAG are the same. The entities of interest as shown in Fig. 1(a) are \(E=\left\{e_{1}, e_{2}, e_{3}, e_{5}\right.\), \(\left.v_{1}, v_{2}, v_{3}, v_{5}, v_{6}\right\}\). Since their corresponding nodes are

## 4 Experimental results and discussion

In this section, two experiments are described to illustrate the space and time savings.

### 4.1 Reducing characteristic views

The number of characteristic views using an EAG for the object, as shown in Fig. 5(a) with two steps on two opposite sides and a pocket on the top face, is greatly reduced. Recall that in the aspect graph for a step as shown in Fig. 1, there are 71 characteristic views. Because of larger number of faces, edges, vertices and higher complexity, the aspect graph of the object in Fig. 5(a) could have hundreds of nodes (or more). Constructing such an aspect graph is both complicated and time consuming. If the entities of interest are only \(e_{1}, e_{2}, e_{3}, e_{4}, e_{5}\) and \(e_{6}\) as labeled in Fig. 5(a), using the described techniques, an entity-based aspect graph with \(E=\left\{e_{1}, e_{2}, e_{3}, e_{4}, e_{5}, e_{6}\right\}\) can be constructed as shown in Fig. 5(b) (see also Table 4). There are only 10 nodes in this entity-based

### 4.2 Reducing computation

The computation time for generating EAGs diminishes as the number of entities of interest decreases. In this experiment, three objects were investigated. The experiments were run on a Sun SPARCstation IPC using SmallTalk (an object oriented programming language from Xerox PARC). Object 1, Object 2 and Object 3 are shown in Fig. 7. Complete aspect graphs were built and the EAGs with different number of entities of interest were also generated. Object 1 and Object 2 each has 20 entities, and generating the AGs for these objects took from 22 to 29 seconds. However, when the number of entities of interest was reduced to 13, it took only one third of that time to generate the corresponding EAGs. When the number of entities of interest was reduced to five (one fourth of all the entities on the objects) the computation time was decreased to 0.133 seconds. A significant amount of time was saved using entitybased aspect graph. A third object with 13 entities, Object 3, was also tested. Similar results were obtained. A significant portion of computation time was saved when the EAGs were generated. The computation times for generating AGs and EAGs for Object 1, Object 2 and Object 3 are shown in Tables 5 and 6 and Fig. 6.

## 5 Complexity analysis

The construction procedures are very tedious and time consuming, and some aspect graph generation algorithms, only find the different characteristic views of the object and not the spatial boundaries of each viewing region. Therefore, each characteristic

![Figure 6. The experimental computation time for generating the](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-6-p011.png)

*Figure 6. The experimental computation time for generating the: The experimental computation time for generating the aspect graph and the entity-based aspect graphs for Object 1, Object 2 and Object 3.*

view is represented as one of the potential vantage points that represent such view. However, for many applications such as sensor planning, it is desirable to have the exact boundaries of the spatial region from which all the vantage points with such a view are obtained. The cost of obtaining such additional information is high, so an effective and efficient algorithm is necessary. Given that n partition planes or surfaces are to be used in constructing an aspect graph, the time complexity of determining a characteristic view for the aspect graph is \(O(2"n')\). Let us assume that the n partition planes or surfaces are (P1, P2,..., Pa). Considering the different half spaces of each of these partitions (denoted pt, Pi), an n-tuple, such as (Pt. P=,...,Pt), can be constructed. There are in total 2" of such n-tuples. If the corresponding partition boundaries of the n-tuple provide a feasible region in the three-dimensional space, each such n-tuple represents a characteristic viewing domain. Given an n-tuple, which represents a feasible characteristic viewing domain, the exact boundaries of the corresponding region are obtained by eliminating those partition planes or surfaces that do not lie on the boundaries of the region. To determine the feasibility and to obtain the exact boundaries for an n-tuple, the time complexity is \(O(n)\). Hence, the total time complexity of generating the aspect graph is \(O(2"n)\).

![Figure 7. (a) Object 1, (b) Object 2 and (c) Object 3.](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-7-p011.png)

*Figure 7. (a) Object 1, (b) Object 2 and (c) Object 3.: (a) Object 1, (b) Object 2 and (c) Object 3.*

![Figure 8. (a) An object with a blind step. (b) The entity-based aspect](/Users/evanthayer/Projects/stepview/docs/1998_entity_based_aspect_graphs_making_viewer_centered_representations_more_efficient/figures/figure-8-p012.png)

*Figure 8. (a) An object with a blind step. (b) The entity-based aspect: (a) An object with a blind step. (b) The entity-based aspect graph of the object in Fig. 3(a) with the set of entities of interests as (Ly, Lz, Lz, W1, Wz, Wz, HI, H2, Hzs.*

entity-based aspect graph will significantly decrease when \(N_{E^{\mathrm{c}}}\) is large.

## 6 Conclusion

The aspect graph, a viewer-centered representation of an object, is useful tool for object recognition, for sensor planning, and several other applications, but it has an important limitation: its complexity. Many research works (Bowyer, 1991, Eggert et al., 1993, Laurentini, 1995) have discussed its practical utility and some have recently proposed aspect graphs having lower complexity based on particular assumptions. In this work, we have described entitybased aspect graphs, which include only the viewing domains that embody distinct visibility characteristics for a particular set of entities of interest belonging to an object. Usually the number of entities of interest is fewer than the total number of entities on the object, and the total number of nodes on the graph is greatly reduced. Using the entity-based aspect graph approach, we still have enough information to plan sensor settings or to recognize the object.

The contributions of this paper can be summarized as follows:

- A new entity-based aspect graph is introduced, based on the assumption that only the observability of some entities of interests are useful for applications such as object recognition and sensor placement.

- algorithms for creating an EAG from the faces, edges and vertices of an object are presented

Also algorithms for contracting and combining previously constructed EAGs are presented. By employing the presented algorithms, the burden of determining the characteristic views from the partition planes or surfaces can be reduced and the previously built EAGs can be reused.

- The complexity of computing an EAG is analyzed. This analysis shows that complexity is decreased significantly. The computational savings are produced by reducing the number of partition planes or surfaces formed by the involved geometric entities.

Fig. 8 and Table 7 show an object with a blind step. For further reading, see (Charkravarty and Freeman, 1982; Edelman and Weinshall, 1991; Kriegman and Ponce, 1990; Petitjean et al., 1992; Ponce et al., 1992; Stark et al., 1988; Wang and Freeman, 1990; Watts, 1988; Yang, 1997).

## References

- Bowyer, K., 1991. Why aspect graphs are not (yet) practical for computer vision. In: IEEE Workshop on Directions in Automated CAD-based Vision, Maui, HI, 2-3 June, pp. 97-104. Bowyer, K.W., Dyer, C.R., 1990. Aspect graphs: An introduction and survey of recent results. Internat. J. Imaging Systems and Technology 2, 315-328.

- Bowyer, K., Stewman, J., Stark, L., Eggert, D., 1988. A 3-D object recognition system using aspect graph. In: 9th Internat. Conf. on Pattern Recognition, Rome, Italy.

- Bowyer, K., Sallam, M.Y., Eggert, D.W., Stewman, J.S., 1993 Computing the generalized aspect graph for objects with moving parts. IEEE Trans. Pattern Anal. Machine Intell. 15 (6),

- Charkravarty, I., Freeman, H., 1982. Characteristic views as a basis for three-dimensional object recognition. SPIE Robot Vision 336. 37-45.

- Edelman, S., Weinshall, D., 1991. A self-organizing multiple-view representation of 3D objects. Biological Cybernet. 64 (3),

- Eggert, D.W., Bowyer, K.W., Dyer, C.R., Christensen, H.I., Goldgof, D.B., 1993. The scale space aspect graph. IEEE Trans Pattern Anal. Machine Intell. 15 (11), 1114-1130.

- Freeman, H., 1990. The Use of Characteristic-View Classes for 3D Object Recognition. Machine Vision for Three-Dimensional Scenes. Academic Press, New York, pp. 109-163.

- Koenderink, J.J., van Doorn, A.J., 1979. The internal representation of solid shape with respect to vision. Biological Cybernet. 32.

- Kriegman, D.J., Ponce, J., 1990. Computing exact aspect graphs of curved objects: solids of revolution. Internat. J. Comput. Vision 5(2), 119-135.

- Laurentini, A., 1995. Introducing the reduced aspect graph. Pattern Recognition Letters 16, 43-48

- Mäntyla, M., 1988. An Introduction to Solid Modeling. Computer Science Press, Rockville, MD

- Petitjean, S., Ponce, J., Kriegman, D.J., 1992. Computing exact aspect graphs of curved objects: algebraic surfaces. Internat. J Comput. Vision 9 (3), 231-255.

- Ponce, J., Petitjean, S., Kriegman, D.J., 1992. Computing exact aspect graph of curved objects: Algebraic surfaces. In: Proc 2nd European Conf. on Computer Vision, Santa Margherita Ligure, Italy, 18-23 May, pp. 599-614. Shimshoni, I., Ponce, J., 1997. Finite-resolution aspect graphs of polyhedral objects. IEEE Trans. Pattern Anal. Machine Intell. 19(4), 315-327. Stark, L., Eggert, D., Bowyer, K., 1988. Aspect graphs and nonlinear optimization in 3-D object recognition. In: Proc. IEEE 2nd Internat. Conf. on Computer Vision, Tampa, FL, pp Tarabanis, K.A., Tsai, R.Y., Allen, P.K., 1995a. The MVP sensor planning system for robotic vision tasks. IEEE Trans. Robotics Automation 11 (1), 72-85. Tarabanis, K.A., Allen, P.K., Tsai, R.Y., 1995b. A survey of sensor planning in computer vision. IEEE Trans. Robotics Automation 11 (1), 86-104. Trucco, E., Umasuthan, M., Wallace, A.M., Roberto, V., 1997. Model-based planning of optimal sensor placements for inspection. IEEE Trans. Robotics Automation 13 (2), 182-194 Wang, R., Freeman, H., 1990. Object recognition based on characteristic view classes. In; Proc. 10th Internat. Conf. on Pattern Recognition, pp. 8-12. Watts, N.A., 1988. Calculating the principal views of a polyhedron. In: Proc. 9th Internat. Conf. on Pattern Recognition, Weinshall, D., Werman, M., 1997. On view likelihood and stability. IEEE Trans. Pattern Anal. Machine Intell. 19 (2), 97-108 Yang, C.C., 1997. Active vision inspection: Planning, error analysis, and tolerance design. Chapter 2: Entity-based aspect graphs. Ph.D Dissertation, Dept. of Electrical Computer engineering, The University of Arizona. Yang, C.C., Marefat, M.M., 1995. Object oriented concepts and mechanisms for feature-based computer integrated inspection. Adv. in engineering Software 20(2-3), 157-179. Yang, C.C., Marefat, M.M., Kashyap, R.L., 1994. Active visual inspection based on CAD models. In: Proc. IEEE Internat. Conf. on Robotics and Automation, San Diego, CA, Pp.
