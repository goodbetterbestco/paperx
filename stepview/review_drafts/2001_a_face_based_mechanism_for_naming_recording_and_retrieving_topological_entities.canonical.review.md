# 2001 a face based mechanism for naming recording and retrieving topological entities

Computer-Aided Design ( ) -, Junjun Wu*, Tianbing Zhang, Xinfang Zhang, Ji Zhou

Nowadays, new generation of feature based parametric modeling systems makes it easy to define part model, which can generate various similar parts. This function is realized through flexible editing tools, by which dimension values, constraint relations and feature definitions can be modified. Parametric function makes it possible to change the dimension values of part at any time and drive the part to get a completely new variant through the various information stored in part model. This is one of the main purposes of parametric models [1]. In these systems, designers usually define a part model through dimensions, constraints and features which make it possible to generate variants. When designers want to get a variant of the designed part, they can edit the designed model using editing tools. However, some times designers may not be able to get the satisfying results through this way. The typical reasons are
CAD Center, Huazhong University of Science and Technology, Wuhan, Hubei 430074, People's Republic of China
precisely, has been implemented in InteSolid, a history and feature based modeling system. © 2001 Elsevier Science Ltd. All rights reserved. the dimension values of part at any time and drive the part to

## Abstract

Keywords: Topological name; Design history; Feature and history based design www.elsevier.com locate cad

## Introduction

the ability of solving constraints is not strong enough to handle some odd cases; the newly set dimension values are not reasonable or engineering oriented; and some related entities cannot be retrieved or identified from the information in the part model.

The first two of the above can be solved by applying Dimensional Constraint Manager (DCM), a software component module that manipulates geometric designs to satisfy given dimensions [2,3], to feature based modeling systems. However, the third is relevant to referencing topological entities. The history of designing part model is a sequential one in feature based parametric system. Usually a base feature is designed first then the other features are attached to it. Every modeling step is a design history stage in which one feature is generated. Every feature contains its specific information, such as parameters, attributes, feature operations and the records of referenced topological entities. These topological entities, that is, faces, edges and vertices, are used mainly for the following three purposes:

as operation object of a feature, i.e. the removed face of a shelling feature; as datum object of a feature, i.e. the datum plane of the sketch of a protrusion feature; and as medial object between a feature and its technical information, i.e. the entities in a feature referenced by dimensions.

When some of the dimension values, constraint relations or feature definitions of features in a part are modified, if all the referenced topological entities can be retrieved or identified from the records, it should be reconstructed automatically

![Figure 1. CSG Tree-like structure of the design history of a part.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-1-p002.png)

*Figure 1. CSG Tree-like structure of the design history of a part.: CSG Tree-like structure of the design history of a part.*

and unambiguously according to the specific information in every feature. However, in traditional modeling systems the referenced topological entities cannot be retrieved correctly from their records. To solve this problem, a robust mechanism for naming, recording and retrieving topological entities should be applied to feature based modeling systems. The basic functions of this mechanism are how to name the topological entities, how to record the topological entities through names and how to unambiguously retrieve the entities from the topological names when regenerating the part model.

This mechanism is not only what the 3D parametric modeling systems need, but also one of the notable characteristics that differ from traditional modeling systems. Moreover, it can be used to establish feature associations among various applications, such as, the mapping from design features to assembly or manufacturing features. Hence, the development of a mechanism for naming, recording and retrieving topological entities is necessary. This paper is organized as follows. In Section 2, the related research is reviewed. Section 3 gives an exploration of the design history of parts. How to name topological entities is described in Section 4. Section 5 illustrates how to record and retrieve topological entities. Eliminating ambiguity is discussed in Section 6. Finally a brief summary is given in Section 7.

## 2 Review of related research

Among the previous related research on mechanism for naming topological entities, the work of Kripac [4,5] and Capoyleas [1] is representative. However, the research related in this area is not enough Kripac presents a topological ID system, which systematically assigns IDs (names or labels) to topological entities in solid models. The IDs of topological entities in the old version of the solid model are mapped to the IDs of the corresponding topological entities in the new version of the solid model automatically when reevaluating the solid model. This topological ID system is implemented through the names of steps, faces, edges and vertices, a graph recording the history of face deleting, living, creating, merging and splitting and mapping algorithms. The algorithms he adopted are perplexing because he omitted many details, which should be clarified when mapping topological IDs.

Capoyleas from Purdue University also has conducted a lot of researches in this area. The method he used is to give a unique identification to every topological entity. He mainly focused on how to solve ambiguity when naming topological entities. He presented two methods to solve ambiguity. One uses local orientation information, which is based on the direction in which an adjacent face uses an edge, and on the face orientation in the solid model. The other uses feature orientation information, which is defined based on the direction of extrusion or the spin of revolution. The second method is mainly applied to entities in features, which must rely on profiles. In order to improve the editability of feature based design, Chen [6] presents the matching algorithms for vertex, edge and face, which are based on the naming mechanism provided by Capoyleas.

However, they did not consider many phenomena that happen to topological entities after Boolean operations. These phenomena can help us to find an easier way to setup a mechanism for naming, recording and retrieving topological entities. Firstly, it is unnecessary to give names to all the topological entities. Thus the space is greatly saved and some maintenance problems are avoided. Secondly, although the algorithms they provided are effective enough to solve ambiguity some times, it is not an easy task to implement these algorithms. Research on a number of commercial CAD systems, such as Pro Engineer, SolidWorks and SolidEdge, indicates that they should have done much work on the mechanism for naming, recording and retrieving topological entities. Flexible naming mechanism is one of the prerequisites of these systems. Due to severe competence in commerce, they are not willing to make it public on how to implement their mechanisms for naming, recording and retrieving topological entities, respectively.

## 3 Explore the design history of parts

Exploring the design history of parts is helpful to under stand the idea of setting up the mechanism for naming, recording and retrieving topological entities. In a feature based modeling system it's usual to design a base feature first, and then attach the other features to the previously designed features. There are a part body and an original feature body at every design stage. Generally, with the current feature defined, a design stage, \(S_{i}\), is defined. \(\operatorname{PB}\left(S_{i}\right)\) specifies the part body in stage \(S_{i}\), and \(\operatorname{PFB}\left(S_{i}\right)\) the body of the original feature in stage \(S_{i}\). If the Boolean opera tor between \(\mathrm{PB}\left(S_{i}\right)\) and \(\mathrm{PFB}\left(S_{i}\right),\left\langle\mathrm{OP}_{i}\right\rangle\), is regular, the part

![Figure 2. The adjacent faces of an edge.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-2-p003.png)

*Figure 2. The adjacent faces of an edge.: The adjacent faces of an edge.*

### 3.1 Adjacent face and Adjacent face set

### 3.2 Feature face set

![Figure 3. The feature face set of feature.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-3-p003.png)

*Figure 3. The feature face set of feature.: The feature face set of feature.*

cutting an Extrusion Feature from the block. \(F_{1}, F_{2}\) and \(F_{3}\) are the FFS of the cut Extrude feature.

### 3.3 Entity in feature

If any of the faces in \(\mathrm{AFS}(\mathrm{TE})\), where TE is a topological entity in the part body PB, can be found in \(\operatorname{FFS}(F E A T)\), where FEAT is a feature in the part, TE is an Entity in Feature (EIF). \(E_{1}\) and \(E_{4}\) in Fig. 3 are EIFs.

### 3.4 Entity between features

If a face \(f_{1}\), in feature \(F E A T_{1}\) and a face \(f_{2}\), in feature \(F E A T_{2}\) can all be found in \(\operatorname{AFS}(\mathrm{TE})\), where TE is an entity in PB which contains \(F E A T_{1}\) and \(F E A T_{2}\), Then TE is an Entity Between Features (EBF). \(E_{2}\) and \(E_{3}\) in Fig. 3 are EBF's.

### 3.5 Entity with source and entity without source

The expression, Geom(TE), is used to represent the geometry of a topological entity TE. Part body PB is gener ated after the Boolean operation between body \(B_{1}\) and \(B_{2}\). If there exists another topological entity \(\mathrm{TE}^{\prime}\) which is in \(B_{1}\) or \(B_{2}\) and makes Geom(TE') equal to Geom(TE), then TE' is the source of TE and TE is an Entity With Source (EWS). If TE' does not exist, TE is an Entity Without Source (EWOS). For instance, \(F_{1}, F_{2}\) and \(F_{3}\) in Fig. 3 are EWS' es, but \(E_{2}\) and \(E_{3}\) are EWOS'es.

The design history illustrated in Fig. 1 has the following intrinsic characteristics.

- EIF is an EWS and EBF is an EWOS.

- Any topological face in body PB(S;) is an EWS. This is not true to topological edges and topological vertices.

- In the dynamical evolution of part body, EIF's and EBF's in it are created and deleted from time to time.

- After Boolean operations, there may leave some hints of PFB(S;) in body PB(Si+1). It means that some or all of the faces in PFB(S;) may emerge in body PB(S:+1)

- Some or all of the faces in body PBS;) and PFB(S,) constitute the boundary of part body PB(Si+1) after the Boolean operation.

- After the Boolean operation between body PB(S;) and body PFB(S;), some EWOS'es will be created.

It can be concluded from these characteristics that no topological face without source will be created, but some topological edges and vertices without source will be generated after Boolean operation. This conclusion is the basis of the face based mechanism for naming, recording and retrieving topological entities. The brief diagram of our mechanism is shown in Fig. 4. As the body of an original feature is created, every face of this feature is attached with a name (called original name). Then a Boolean operation is conducted between the part body and the original feature body with names. If it is needed to reference an entity (face, edge or vertex) in the

- Attach names to faces in original feature body.

- Boolean Operation.

- Propagation of original name.

- Record topological entity with real name.

- Retrieve topological entity from real name.

![Figure 4. Brief diagram of mechanism for naming, recording and retrieving](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-4-p004.png)

*Figure 4. Brief diagram of mechanism for naming, recording and retrieving: Brief diagram of mechanism for naming, recording and retrieving topological entities.*

## 4 Name topological face

### 4.1 Attach original name to face

- the topological edges and topological vertices in part body may be EWOS'es;

- any topological face in part body has a corresponding source in one of the original features. Thus, attaching

![Figure 5. Dependency between original names and feature faces.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-5-p004.png)

*Figure 5. Dependency between original names and feature faces.: Dependency between original names and feature faces.*

![Figure 6. Typical sweep feature.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-6-p004.png)

*Figure 6. Typical sweep feature.: Typical sweep feature.*

names to the faces in part body can be implemented by attaching names to faces in original features; and

- during the process of Boolean operations, the topological edges and topological vertices in part body are changed dynamically, whereas the faces in original features are relatively stable.

A feature face and its original name have a one-to-one relationship, as illustrated in Fig. 5. One original name is attached to only one topological face, and one topological face has only one original name attached to it. There are several important methods, such as DELETE, ADD, QUERY, EMPTY and REPLACE, etc. in the mechanism that establishes the relationship between original names and feature faces. It is clear that the most important methods are the ones corresponding to deleting, keeping, merging and splitting topological faces. The essential of naming topological face is to treat original names as attributes, which are attached to the feature faces. The context of original name is closely related to the generating modes of concrete features and will not change in its life cycle once created. With the generation of a topological face, an original name attached to it is generated, and with the disappearance of a topological face, the topological name on it will also be removed.

### 4.2 Context of original name

The contexts of original names for the faces in a feature are decided by the feature's generating mode and the locations of the face in the feature. For example, Extrude is a feature whose shape is decided by a profile. The contexts of original names for the faces in a protrusion are related to the identities of the elements in the profile. Every instance of a feature has a globally unique identity in a part. In InteSolid, a feature based modeling system, features are classified into the following three catalogues [7]:

- profile based feature, whose shape is mainly decided by one or more profiles, i.e. Extrude, Revolve and Sweep;

![Figure 7. Name chamfer feature.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-7-p005.png)

*Figure 7. Name chamfer feature.: Name chamfer feature.*

$$
\mathrm{ON}(F)=\left\{\begin{array}{l} {[\text { FeatID, } 0,-1,0,0], \quad \text { if } F \text { is the starting face. }} \\ \mathrm{ON}_{\text {side }}, \text { if } F \text { is a side face. } \\ {[\text { FeatID, } 0,-2,0,0], \quad \text { if } F \text { is the ending face. }} \end{array}\right.
$$

- entity based feature, which references some topological entities in the part body to do some special operations on them, i.e. Chamfer, Round, Shell; and

\mathrm{ON}(F)= \begin{cases}{[\text { FeatID, } 0,-1,0,0],} & \text { if } F \text { is the starting face. } \\ {\left[\text { FeatID, } \text { FeatID }_{\mathrm{p}}, \text { ID }_{\text {element }}, \text { FeatID }_{\mathrm{p}}, \text { ID }_{\text {axis }}\right],} \\ & \text { if } F \text { is a side face. } \\ {[\text { FeatID, } 0,-2,0,0],} & \text { if } F \text { is the ending face. }\end{cases}

- feature based feature, whose generation depends on other features, i.e. Linear Pattern, Circular Pattern and Mirror.

#### 4.2.1 Name profile based feature

Extrude and Revolve are the two specific cases of Sweep, which is generated by sweeping a profile along a path. The profile is a 2D closed one and the path can be 2D or 3D connected segments. Fig. 6 shows a typical Sweep feature. There are three types of feature faces, that is, starting face, side face and ending face. Set element \(E\) as one of the edges of the profile, trajectory \(T\) one of the segments of the path. The context of the original name for the face decided by \(E\) and \(T\) can be decided by FeatID \({ }_{\mathrm{P}}, \mathrm{ID}_{\text {element }}, \mathrm{FeatID}_{\text {Path }}\) and \(\mathrm{ID}_{\text {trajectory }}\) where FeatID \(\mathrm{ID}_{\mathrm{P}}\) and FeatID \({ }_{\text {Path }}\) are the identities of the profile and path, \(\mathrm{ID}_{\text {element }}\) and \(\mathrm{ID}_{\text {trajectory }}\) are the identities of \(E\) and \(T\), respectively. It's obvious that a given element \(E\) and a given trajectory \(T\) are related to a side face. Hence, the context of the original name for the side face which is in the profile based feature can be expressed by where FeatID is the feature identity of Sweep Since almost all the Sweep features have starting faces and ending faces, the contexts of the original names for these two faces have general meaning. Here the expression for the side face is applied to the expressions for the starting face and the ending face. Set the value of \(\mathrm{ID}_{\text {element }}\) for start ing face as-1 and that of \(\mathrm{ID}_{\text {element }}\) for ending face as-2. Thereby the contexts of original names for the faces in the

Sweep feature are expressed by

As to an Extrude feature, which is formed by sweeping a profile along the normal of the profile, since the values of FeatID \({ }_{\text {Path }}\) and \(\mathrm{ID}_{\text {trajectory }}\) can be set as zero, the contexts of the original names for the faces in the Extrude feature are

$$
\mathrm{ON}(F)= \begin{cases}{[\text { FeatID, } 0,-1,0,0],} & \text { if } F \text { is the starting face. } \\ {\left[\text { FeatID, } \mathrm{FeatID}_{\mathrm{p}}, \mathrm{Id}_{\text {element }}, 0,0\right],, \text { if } F \text { is a side face. }} \\ {[\text { FeatID, } 0,-2,0,0],} & \text { if } F \text { is the ending face. }\end{cases}
$$

A Revolve feature is formed by sweeping a profile around a central axis for a certain angle. The values for FeatID \({ }_{\text {Path }}\) and \(\mathrm{ID}_{\text {trajectory }}\) are \(\mathrm{Feat}_{\mathrm{ID}}\) and \(\mathrm{ID}_{\text {axis }}\), respectively. When the angle is \(360^{\circ}\), the starting face and the ending face do not exist any more. Thus, the contexts of the original names for the faces in the Revolve feature are

#### 4.2.2 Name entity based feature

If all the original names can be depicted by a uniform expression, it is possible to handle the names in a uniform manner. It is an ideal method beyond all doubt. When naming an entity based feature, exploiting the contexts of the original names for profile based features should be considered. This can be illustrated by naming a Chamfer feature.

The chamfered faces are achieved by replacing some of the edges in part with planes. The context of the original name for a chamfered face can exploit the contexts of the original names of the faces adjacent to the chamfered edge. Therefore, the context of the original name of any face of a chamfered feature is

$$
\mathrm{ON}_{\text {Side }}=\left[\text { FeatID, FeatID }{ }_{\mathrm{p}}, \text { ID }_{\text {element }}, \text { FeatID } \text { Path }, \text { ID }_{\text {trajectory }}\right],
$$

$$
\mathrm{ON}(F)=\left[\text { FeatID, FeatID }{ }_{\mathrm{FF1}}, \mathrm{ID}_{\text {element }}, \text { FeatID }_{\mathrm{FF2}}, \mathrm{ID}_{\text {element2 }}\right],
$$

where FeatID \({ }_{\text {FF1 }}\) is the identity of the feature which has a feature face \(F_{1}\), one of the adjacent faces of the chamfered edge, and FeatID \({ }_{\mathrm{FF} 2}\) is the identity of the feature which has a feature face \(F_{2}\), another adjacent face of the chamfered edge. If there is only one adjacent face of the chamfered edge, the values of FeatID \({ }_{\text {FF2 }}\) and FeatID \({ }_{\text {FF1 }}\) are the same. The value of \(\mathrm{ID}_{\text {element } 1}\) is the same as the value of the corresponding part in the context of the original name for face \(F_{1}\), and the value of \(\mathrm{ID}_{\text {element } 2}\) is the same as the value of the corresponding part in the context of the original name for face \(F_{2}\).

\begin{aligned} \mathrm{ON}(F)= & {\left[\text { FeatID, } \text { FeatID }{ }_{\mathrm{P}}, \text { ID }_{\text {element }}, \text { FeatID }_{\text {path }},\right.} \\ & \text { ID } \left._{\text {trajectory }}, \text { InsNum }\right], \end{aligned}

![Figure 8. Name linear patter feature.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-8-p006.png)

*Figure 8. Name linear patter feature.: Name linear patter feature. Name linear pattern feature.*

$$
\begin{aligned} & \mathrm{ON}\left(F_{1}\right)=[6,5,-2,0,0] \\ & \mathrm{ON}\left(F_{2}\right)=[6,5,-1,0,0] \end{aligned}
$$

The part illustrated in Fig. 7 is made by subtracting one block from the other and chamfering edge \(e_{1}\) and edge \(e_{2}\). Although the original feature body contains eight faces, actually only face (a, b, e, f) and face (b, c, d, e) are the feature faces. It is sufficient only to name the two feature faces. \(F_{1}, F_{2}\) and \(F_{3}\) are the feature faces in the cut Extrude feature, whose identity value is assumed to be 6. This Extrude feature has a profile, which consists of four elements, \(I_{1}, I_{2}, I_{3}\) and \(I_{4}\). If the identity of the profile is 5, the contexts of the original names for \(F_{1}, F_{2}\) and \(F_{3}\) are

$$
\mathrm{ON}\left(F_{3}\right)=[6,5,-2,0,0] .
$$

According to the idea above, the contexts of the original names for face(a, b, e, f) and face (b, c, d, e) are

$$
\mathrm{ON}(\mathrm{face}(\mathrm{a}, \mathrm{~b}, \mathrm{e}, \mathrm{f}))=\left[7,6,-2,6, \mathrm{ID}_{\mathrm{I} 1}\right]
$$

$$
\mathrm{ON}\left(F_{3^{\prime \prime}}\right)=\left[7,5, \mathrm{ID}_{\mathrm{e}}, 0,2\right] .
$$

$$
\mathrm{ON}(\text { face }(\mathrm{b}, \mathrm{c}, \mathrm{~d}, \mathrm{e}))=\left[7,6,-2,6, \mathrm{ID}_{\mathrm{I} 2}\right]
$$

$$
\mathrm{ON}(F)=\left[\mathrm{FeatID}, \mathrm{id}_{1}, \mathrm{id}_{2}, \mathrm{id}_{3}, \mathrm{id}_{4}, \mathrm{id}_{5}, \text { option }\right],
$$

#### 4.2.3 Name feature based feature

Naming an entity based feature embodies the idea of exploiting the context of the original name for a profile based feature. However, naming a feature based feature can be achieved by extending the context of the original name for a profile based feature. This will be explained through naming a Linear Pattern feature. Linear Pattern feature is formed by copying one or more features in the part and posing them along a given direction with proportional spacing. The shape of any instance in a linear pattern feature is the same as that of the feature(s) copied. Usually the instance number of a linear pattern feature is greater than one. Therefore, it is necessary to extend the context of the original name for the face of a profile based feature so that it can be used for the face of a feature based feature. The context of the original name after being extended is where symbol InsNum is the sequential number of the instance to which face F belongs.

The part depicted in Fig. 8 is made by uniting a block and a cylinder, both of which are Extrude features and doing a linear pattern (the instance number is 2) to the cylinder. If assuming that the value of the identity for the cylinder feature is 6 and that of the profile for the cylinder is 5, the contexts of the original names for the faces in the original feature body of the cylinder are

$$
\mathrm{ON}\left(F_{3}\right)=\left[6,5, \mathrm{ID}_{\mathrm{e}}, 0,0\right] .
$$

The contexts of the original names for the faces in the linear pattern feature are

$$
\mathrm{ON}\left(F_{1}\right)=\left[6,5, \mathrm{ID}_{\mathrm{I} 2}, 0,0\right],
$$

$$
\mathrm{ON}\left(F_{2}\right)=\left[6,5, \mathrm{ID}_{\mathrm{II}}, 0,0\right],
$$

$$
\begin{aligned} & \mathrm{ON}\left(F_{1^{\prime}}\right)=[7,5,-2,0,1] \\ & \mathrm{ON}\left(F_{2^{\prime}}\right)=[7,5,-1,0,1] \\ & \mathrm{ON}\left(F_{3^{\prime}}\right)=\left[7,5, \mathrm{ID}_{\mathrm{e}}, 0,1\right] \\ & \mathrm{ON}\left(F_{1^{\prime \prime}}\right)=[7,5,-2,0,2] \\ & \mathrm{ON}\left(F_{2^{\prime \prime}}\right)=[7,5,-1,0,2] \end{aligned}
$$

Summarizing the above naming ideas and the research on the generations of form features in feature based parametric modeling systems, the context of the original name for the face of a general feature can be expressed by where the values of \(\mathrm{id}_{1}, \mathrm{id}_{2}, \mathrm{id}_{3}, \mathrm{id}_{4}\) and \(\mathrm{id}_{5}\) have their own specific meanings decided by the type of the feature and the location of the given face \(F\).

### 4.3 Propagation of original name

After naming topological faces is finished, a Boolean operation will be executed between the body of the original feature and the part body. Because of the Boolean operation, the topological faces in the two bodies will be deleted, merged, split or still kept. Therefore, there should be some specific methods to handle the topological names

![Figure 9. Propagation of splitting topological name.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-9-p007.png)

*Figure 9. Propagation of splitting topological name.: Propagation of splitting topological name.*

#### 4.3.1 Propagation of deleting topological name

#### 4.3.2 Propagation of keeping topological name

#### 4.3.3 Propagation of splitting topological name

$$
\mathrm{RN}(F)=[\mathrm{ON}(F), \mathrm{PSI}],
$$

![Figure 10. Propagation of merging topological name.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-10-p007.png)

*Figure 10. Propagation of merging topological name.: Propagation of merging topological name.*

$$
\mathrm{RN}(E)=\left[\mathrm{RN}\left(F_{1}\right), \mathrm{RN}\left(F_{2}\right), \mathrm{PSI}\right],
$$

from it. This is called propagation of splitting topological name and illustrated in Fig. 9.

#### 4.3.4 Merging propagation of topological name

As depicted in Fig. 10, when face \(F_{1}\) and face \(F_{2}\) are merged into one face \(F\), the topological name of face \(F_{2}\) in the part body will be used to name the new face \(F\), i.e. \(\mathrm{ON}_{3}\) is the same as \(\mathrm{ON}_{2}\). This is called propagation of merging topological name.

## 5 Record and retrieve topological entity

As discussed above, if a feature in designing references some topological entities as its operation objects, datum objects or medial objects, these referenced topological entities should be recorded as topological names (real names). And while rebuilding the whole part or editing a feature, those referenced topological entities should be retrieved from the real names recorded in the feature. Actually recording and retrieving topological entities are the two aspects of the same problem.

### 5.1 Record topological entity

In our mechanism, the real name recording a topological entity is derived from the original name of a topological face. Thus referencing a topological entity is implemented indirectly. This is important for history and constraint based solid modeling system in which directly referencing topological entities may cause serious inconsistency problems.

#### 5.1.1 Record topological face

Generally speaking, it's enough to record a topological face with the real name attached to it. Nevertheless, because of the split of topological face, things get a little complicated In order to distinguish those faces originated from the same face from each other, it is necessary to record a topological face with the combination of the real name attached to it and some specific information that can tell this face from the other. Therefore the real name for a topological face is where \(\mathrm{ON}(F)\) is the original name of the face \(F\) and symbol SI is the parametric space information that can eliminate ambi

#### 5.1.2 Record topological edge

Geometrically two intersected faces can express an edge in 3D space. We can take this into the consideration of record ing a topological edge. It is natural to record a topological edge through recording its adjacent topological faces. If face \(F_{1}\) and face \(F_{2}\) are the adjacent faces of an edge E, the real name for this topological edge is expressed by

![Figure 11. Hierarchical structure of names.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-11-p008.png)

*Figure 11. Hierarchical structure of names.: Hierarchical structure of names.*

#### 5.1.3 Record topological vertex

![Figure 12. Symmetric topological face.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-12-p008.png)

*Figure 12. Symmetric topological face.: Symmetric topological face.*

![Figure 13. Symmetric edges.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-13-p008.png)

*Figure 13. Symmetric edges.: Symmetric edges.*

every entity in the part body can have a corresponding real name if necessary.

### 5.2 Retrieve topological entity

Retrieving a topological entity is the reverse process of recording the topological entity, whose goal is to calculate the real name of a given entity. The task of retrieving a topological entity is to find a proper entity in the part body from a given real name.

## 6 Eliminate ambiguity

In the process of recording and retrieving topological entities, ambiguity will show up from time to time. The usage of component PSI in the expression of a real name is no other than eliminating ambiguity.

### 6.1 Topological symmetry

The main cause of ambiguity is the topological symmetric situation, which is brought out by the split of topological faces. If a face is split into two or more faces after a Boolean operation, each face in the split faces is a symmetric topological face to the other one. The part depicted in Fig. 12 is made by cutting two through slots on the top surface of a block. After cutting the two through slots, the top face of the block is split into three faces, \(F_{1}, F_{2}\) and \(F_{3}\). Face \(F_{1}\) is a symmetric topological face to the other two faces, \(F_{2}\) and \(F_{3}\). This is same to \(F_{2}\) and \(F_{3}\) too. Set \(\partial_{1}\) and \(\partial_{2}\) as two topological face sets, which cannot be empty and any one of the faces in set \(\partial_{1} \cup \partial_{2}\) belongs to the same part body.

- If d, \(C^{22}\) and d2 \(C^{21}\), di and zare strongly symmetric to each other.

- If to any face F2 of the faces in d1, there exists a face F, in дz that is symmetric to F2 and this is true to any face in 21, 2, and dz are weakly symmetric to each other.

- If there exist four sets 1j, 12, 13 and 14 that make

- 13 0 14 = Д

- 1, and 13 are strongly symmetric to each other and

- 12 and 14 are weekly symmetric to each other,

![Figure 14. Symmetric vertices.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-14-p009.png)

*Figure 14. Symmetric vertices.: Symmetric vertices.*

### 6.2 Parametric space information

Ambiguity will happen during recording and retrieving a topological entity when the number of entities obtained through a topological name is greater than two. Sometimes in the actual part design process, ambiguity is acceptable. For example, ambiguity is acceptable for the sketching plane because all the ambiguous faces are coplanar. This is also true for selecting the axis when creating a Revolve feature, because all the ambiguous edges are collinear. However, retrieving the unambiguous entity is the usual case. Therefore a mechanism that can solve ambiguity should be supplied. A topological face on a solid may be split into two or more faces during the process of a Boolean operation. The parametric space expressions of the faces before and after splitting are the same only with some changes to the valid definition space area. It can be illustrated by the trimming operation between two surfaces, \(\mathrm{P}(u, v)\) and \(\mathrm{Q}(u, v)\) in Fig. 16. Suppose that the two side parts of surface \(\mathrm{P}(u, v)\) and the middle part of surface \(\mathrm{Q}(s, t)\) are kept after trimming, the valid definition areas of surface \(\mathrm{P}(u, v)\) are covered by the two outer loops, and that of \(\mathrm{Q}(s, t)\) the middle loop. Before merging operation, their valid definition areas are the corresponding rectangles, which are defined by \(0 \leq u \leq 1,0 \leq v \leq 1\) and \(0 \leq s \leq 1,0 \leq t \leq 1\), respectively. In addition, the shapes of curves and surface will not be changed when scaling, rotating and displacing them [8].

![Figure 16. The variation of parametric space.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-16-p010.png)

*Figure 16. The variation of parametric space.: The variation of parametric space.*

- first select a different feature point on the topological entities that have the same topological name;

- then get the u and v values of the parametric space on any one of the adjacent faces of the entities; and

- at last sort all the entities according to the u and v values.

![Figure 17. Select feature point.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-17-p010.png)

*Figure 17. Select feature point.: Select feature point.*

![Figure 18. Obtain parametric space information.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-18-p010.png)

*Figure 18. Obtain parametric space information.: Obtain parametric space information.*

s1 goes through the highest point of area A and is parallel to line v = 0. Line s2 goes through the lowest point of area A and is parallel to line v = 0. Line t1 is through the right point of area A and parallel to line u = 0. Line t2 is through the left point of area A and is parallel to line u = 0. The modalities of area B have the following three possibilities.

- Area B is in one of the four districts a, c, g and i. There are no intersecting points between area B and lines s1, s2, tl and t2.

- Area B intersects with lines sl, s2, tl and t2. Area B encompasses or is encompassed by area A

- Area B is in one of the four districts: b, d, f and h. There are no intersecting points between area B and lines sl, s2, tl and t2

In fact case 3 and case 2 are the same because if Area A and Area B are exchanged, case 3 now becomes case 2.

As to case 1, any two points in area A and area B can be treated as feature points. In order to regularize the algorithm, the left points of area A and Area B are selected as feature points. As to case 2, it is more complicated. As depicted in Fig. 17(b), line s1 intersects with area B and the intersecting points are point \(\mathrm{p} 1_{\mathrm{B}}\) and point \(\mathrm{p} 2_{\mathrm{B}}\). The top point of area A is point \(\mathrm{p}_{\mathrm{A}}\). point \(\mathrm{p}_{\mathrm{A}}\) can be selected as the feature point of area A and point \(\mathrm{P}_{\mathrm{B}}\) the feature point of area B. If there are intersected points in both \(u\) and \(v\) direc tions, select the point in \(u\) direction as the feature point. If there are more intersected points in \(u\) or \(v\) direction, select the point whose \(u\) or \(v\) value is smallest as the feature point. The most important of all, the feature points of two topolo gical entities that may generate ambiguity must be different. The principle of selecting feature points is valid not only to topological faces, but also to topological edge and topological vertices. As to a vertex, the feature point is the corresponding point in the parametric space. It can be concluded that the parametric space information of a topological entity is related to one of the adjacent faces

![Figure 19. Distinguish ambiguous faces.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-19-p011.png)

*Figure 19. Distinguish ambiguous faces.: Distinguish ambiguous faces.*

$$
\operatorname{PSI}(\mathrm{TE})=[\mathrm{ON}(F), \text { Seq }, \text { Totle }],
$$

### 6.3 Distinguish ambiguous faces

![Figure 20. Distinguish weakly symmetric edges.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-20-p011.png)

*Figure 20. Distinguish weakly symmetric edges.: Distinguish weakly symmetric edges.*

![Figure 21. Distinguish strongly symmetric edges.](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-21-p011.png)

*Figure 21. Distinguish strongly symmetric edges.: Distinguish strongly symmetric edges.*

\(\mathrm{ON}\left(F_{1}\right)\) is equal to \(\mathrm{ON}\left(F_{2}\right)\). PSI1 is different from PSI2, because according to the above method of selecting feature points, the feature point of PSI1 is the point in parametric space corresponding to vertex \(V_{1}\) and that of PSI2 \(V_{2}\).

### 6.4 Distinguish ambiguous edges

As discussed previously, ambiguous edges may be weakly, moderately or strongly symmetric to each other. Actually the ambiguities caused by weak and moderate symmetry have been solved through the real name of a topological edge. This is because there must exist weakly symmetric faces in the adjacent faces of topological edges and the real names of faces in a weakly symmetric face set are different from each other. In Fig. 19, \(E_{1}\) and \(E_{2}\) are moderately symmetric to each other. They can be distin guished from each other through the real names of their adjacent faces. Because \(\mathrm{RN}\left(F_{1}\right)\) is not equal to \(\mathrm{RN}\left(F_{2}\right)\), \(\mathrm{RN}\left(E_{1}\right)\) is different from \(\mathrm{RN}\left(E_{2}\right)\). This is true to \(E_{1}\) and \(E_{2}\) in Fig. 20, where \(E_{1}\) and \(E_{2}\) are weakly symmetric to each other. The part in Fig. 20 is made by uniting two intersecting cylinders. As to strongly symmetric edges, it is necessary to calculate their parametric space information through which one edge can be distinguished from the others. The part in Fig. 21 is formed by cutting a \(1 / 4\) torus from a sphere. \(E_{1}\) and \(E_{2}\) are strongly symmetric to each other. Because the para metric space information of \(E_{1}\) is different from that of \(E_{2}\), \(E_{1}\) and \(E_{2}\) can be distinguished form each other.

### 6.5 Distinguish ambiguous vertices

Similar to distinguishing ambiguous edges, moderately and faintly symmetric vertices can be distinguished directly through the real names of their adjacent faces. For exam ples, \(V_{1}\) and \(V_{2}\) in Fig. 19 (moderately symmetric vertices) and \(V_{5}\) and \(V_{6}\) in Fig. 14 (weakly symmetric vertices) can be distinguished directly through their real names. As to strongly vertices, it is also needed to calculate their para metric space information to distinguish them. \(V_{2}\) and \(V_{3}\) in Fig. 19 are strongly symmetric to each other. It is the para metric space information of them that can tell \(V_{2}\) from \(V_{3}\).

## 21 and dare moderately symmetric to each other.

- If ay and d2 are strongly symmetric to each other, e and ez are strongly symmetric to each other.

- If dy and zare weakly symmetric to each other, ej and e2 are weakly symmetric to each other.

- If d, and are moderately symmetric to each other, e1 and ez are moderately symmetric to each other.

![Figure 15. Shape, size, location and gesture of the original feature body have](/Users/evanthayer/Projects/stepview/docs/2001_a_face_based_mechanism_for_naming_recording_and_retrieving_topological_entities/figures/figure-15-p009.png)

*Figure 15. Shape, size, location and gesture of the original feature body have: Shape, size, location and gesture of the original feature body have effect on topological symmetry.*

The part in Fig. 13(a) is made by cutting a blind slot on the top face of a block. Edge \(e_{1}\) and \(e_{2}\) are strongly symmetric to each other. The part in Fig. 13(b) is made by cutting two intersected through slots on a block. Edge \(e_{1}\) and \(e_{2}\) are weakly symmetric to each other. The part in Fig. 13(c) is made by cutting a through slot on a block. Edge \(e_{1}\) and \(e_{2}\) are moderately symmetric to each other. The part in Fig. 14 is made by cutting two blind semi circle slots and a through semi-circle slot on the same face of a block. \(V_{1}\) and \(V_{2}\) are strongly symmetric to each other, \(V_{3}\) and \(V_{4}\) are moderately symmetric to each other and \(V_{5}\) and \(V_{6}\) are weakly symmetric to each other. As illustrated in Fig. 15, the shape, size, location and gesture of the original feature body are the main factors that affect topological symmetry. In Fig. 15, the finished parts are on the right. On the left are the parts and the original features. In (a), the original feature is a cylinder. The edge \(e_{1}\) and edge \(e_{2}\) in it are moderately symmetric to each other. In (b), the shape of the origi final feature is changed from a cylinder to a block. In (c), the size of the cylinder is getting larger than that in (a). In (d), the location of the cylinder is transferred from the middle to the side of the base block. In (e), the gesture of the cylinder is changed. It can be learnt that the edge \(e_{1}\) and edge \(e_{2}\) in (b), (c), (d), (e) are not symmetric to each other any more.

## 7 Summary

The face based mechanism for naming, recording and retrieving topological entities has been implemented and applied to InteSolid 1.0, a history and feature based product modeling system developed by state key laboratory of CAD in Huazhong University of Science and Technology. The result makes it clear that the mechanism enables the modeling system to correctly and unambiguously replay the design history possible and the editablity of parts is enhanced greatly.

## Acknowledgements

This paper is based on the work of developing a feature based product modeling and design system, which is supported by National Subject Fund of People's Republic China.

## References

- Capoyleas V, Chen X, Hoffmann CM. Generic naming in generative, constraint-based design. CAD 1996;28(1): 17-26.

- The dimensional constraint manager, 2D DCM Manual, Version 3.4, D-Cubed Ltd, 1998.

- The dimensional constraint manager, 2D DCM Part Positioning Product Manual, Version 1.8.0, D-Cubed Ltd, 1998

- Kripac J. A mechanism for persistently naming topological entities in history-based parametric solid models. CAD 1997;29(3):113-22.

- Kripac J. Topological ID system-A mechanism for persistently naming topological entities in history-based parametric solid models, PhD dissertation, Czech Technical University, Prague, 1993.

- Chen Xiangping, Hoffmann CM. On editability of feature-based design. CAD 1995;27(12):905-14.

- Wu Junjun. Theory research and practice for history-based form feature modeling, PhD disserattion, Huazhong University of Science and Technology, Wuhan, 1998.

- Choi BK. Surface Modelling for CAD CAM. Amsterdam: Elsevier, 1991. Wu Junjun is a research fellow at State Key Laboratory of CAD of Huazhong University of Science and Technology (HUST), His research interests lie in feature-based mechanical modeling, design for manufacturing and design for assembly. Wu received his BS, MS and PhD degrees in mechanical engineering from HUST. Zhang Tianbing is a PhD candidate in mechanical engineering of HUST. His research interests include CAD CAM and solid modeling. Zhang received his BS and MS degrees in mechanical engineering from Xi'an Jiaotong University. Zhang Xinfang is a professor of mechanical engineering and chairman of state key laboratory of CAD. His research interests include Concurrent engineering, CAD CAM and engineering Database. Zhang received his BS, MS and PhD degrees in mechanical engineering from HUST. Zhou Ji is a professor of mechanical engineering and president of HUST. His research interests include optimal design, Intelligent CAD and computer integrated manufacturing system. Zhou received his BS degree in mechanical engineering from TsingHua University and MS degree in mechanical engineering from HUST. He received his PhD degree in mechanical engineering of New York State University at Buffalo.
