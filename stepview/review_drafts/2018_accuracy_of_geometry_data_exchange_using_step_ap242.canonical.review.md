# 2018 accuracy of geometry data exchange using step ap242

John Bijnens, Karel Kellens, David Cheshire, KU Leuven, Dept. of Mechanical Engineering, Agoralaan Gebouw B bus , Diepenbeek, Belgium, 6th CIRP Global Web Conference

\( { }^{b} \) Staffordshire University
College Rd
Stoke-on-Trent ST4 2DE, The UK

## Abstract

A new methodology, Model Based Definition (MBD), is gaining popularity. MBD is all about adding the necessary manufacturing information directly onto the 3D model by means of 3D annotations, so-called PMI (Product and Manufacturing Information) data. Two kinds of PMI exist, presentation and representation. PMI representation provides the data in a format that is readable by machines. This allows reuse of the CAD data by other stakeholders. Reuse means it is possible to interrogate the model. One stakeholder that benefits from this is quality control. Others, like manufacturing people who need to change the geometry to adhere to the tolerances specified by the PMI data, are left out in the cold. This paper researches the accuracy that can be achieved by exchanging geometry between different systems by using STEP AP242 and is a preliminary research for a new project to automatically adjust the STEP file driven by PMI data.

## Introduction

Boundary changed to respectively 40.1 and 65.05 as defined by the specified asymmetric dimensional tolerance, 20 needs to be changed to 20.0065 as defined by the specified ISO fitting. As currently most CAM systems can't apply the information contained within the PMI data to the CAD model automatically these adjustments need to be applied manually. This must be repeated with every modification to the original CAD model.

![Figure 1](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-1-p002.png)

*Figure 1: Nominal values influenced by applied tolerances (units mm)*

Not all the stakeholders use the same CAD package. As a result, STEP AP242 is very often used to exchange MBD based CAD models between the different packages[8]. This means that the above-mentioned adjustments that are needed to optimise a CAD model to generate the proper CNC tool paths must be applied frequently to imported STEP files. As can be seen in the example given in Fig. 1 the size of these adjustments can be as small as a few microns. To successfully develop a solution that can automatically implement these adjustments, it is necessary that the transfer of CAD data via STEP AP242 is more accurate than the smallest necessary adjustment.

The goal of the research that is documented in this article is to verify whether the accuracy of exchanging CAD geometry using STEP files is below micron level. If this accuracy cannot be guaranteed modifying the CAD model exchanged using STEP makes no sense. first the methodology used to determine the accuracy of CAD data exchange through STEP AP242 is discussed, then the results are listed and finally a conclusion is given.

## 2 Methodology

Four things can have an impact on the resulting accuracy when exchanging 3D models between CAD systems using STEP:

- the nature of the exchanged geometry

- the model accuracy of the original CAD model

- the model accuracy used within the STEP file

- the model accuracy applied within the receiving system.

The nature of the exchanged geometry refers to the mathematical description of the geometry. CAD models are defined as boundary representation models often abbreviated as B-rep or BREP models[9]. This means the volume of the model is defined by surfaces that form the boundaries of the volume combined with the use of vectors defining the material side. These boundary surfaces can be defined using an analytical representation (ruled surface, surface of revolution, etc. based on analytical elements such as lines, arc, circles) or by using a spline-based (NURBS) representation[10]. To verify whether the accuracy depends on the type of boundary surfaces used four different CAD models were created. The first one contains an analytical surface (a sphere created by revolving an arc around a centre axis), the three others contain a NURBS surface (convex, concave, convex and concave combined) (see Fig. 2).

![Figure 2](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-2-p002.png)

*Figure 2: analytical, convex, concave, convex and concave model*

The model accuracy of the original CAD model can also have an impact on the accuracy of the data exchange. CAD systems can have different ways to define the model accuracy[11]. In the most common definition the model accuracy defines the minimum distance between two points which allows the CAD system to still distinguish the two points as two individual non-coinciding points. To check the influence of applied model accuracy two versions of these four test models have been created. One version has a model accuracy of 0.01 mm and the other has a model accuracy of 0.001 mm.

The model accuracy applied within the STEP file also effects the accuracy of the data exchange. In principle, it should be the same as the model accuracy of the original CAD model. As not all CAD systems do this automatically but allow the designer to specify an arbitrary accuracy or tolerance value for the export this is not always the case. The designer should take care the export accuracy is the same as the accuracy of the originating CAD model. The impact of this possible accuracy discrepancy is not investigated in this research.

The model accuracy applied within the receiving system should be the same as the one used within the STEP file. Where possible this has been configured manually within the receiving CAD package.

The test models have been created in PTC Creo 4 and exported to STEP AP203is and STEP AP242e1. These STEP files have then been imported into several other CAD systems. The CAD systems that were used to perform the tests with are PTC Creo 4, Inventor 2018, Siemens NX 11, ZW3D 2018, CATIA v5, FreeCAD 0.17, OnShape and SpaceClaim19. The importing has been done using the default settings of each CAD package except for PTC Creo. Here some default settings which can have a big impact on the accuracy of the imported files

![Figure 3](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-3-p002.png)

*Figure 3: PTC Creo import settings*

STL file because they change the parametrisation of the spline curves and spline surfaces have been disabled (see Fig. 3).

Comparable settings were not found in the configuration dialog windows of the other CAD packages. PTC Creo uses relative accuracy by default to create a CAD model. Consequently, the real model accuracy that is used for the imported CAD geometry depends on the overall size of the CAD model. CAD part templates with a model accuracy of 0.01 mm and 0.001 mm were used in the tests. To show the impact this has on the accuracy of the import the values of the deviations from the original geometry are listed for the default PTC import settings and for the optimised settings in the tables and graphs further on in this article. Within each CAD package an STL file with a triangular tessellation has been generated with a chord height of 0.01 mm. For CAD packages where setting the chord height was not possible, the most accurate setting available has been used. The chord height is the maximum distance allowed from the triangle to the surface and determines the distance between the vertices of the triangles (see Fig. 4).

![Figure 4](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-4-p003.png)

*Figure 4: Chord height*

The unique vertices are filtered out of the STL file and the deviation of these vertices with the original CAD geometry is determined using the Assembly Verify module of PTC Creo. The vertices and the CAD geometry are not assembled based on a so-called 'best fit' but by mapping two coordinate systems, namely the one used to create the STL file and an identical one in the original CAD model. Theoretically the vertices should be located exactly on the CAD geometry, so the deviation is considered a measure of the accuracy with which the STEP file has transferred the original geometry to another CAD system. A schematic overview of the workflow is given in Fig. 5.

![Figure 5](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-5-p003.png)

*Figure 5: applied workflow*

## 3 Results

The results for STEP AP203 and STEP AP242 are the same. As STEP AP242 is an ISO standard that encapsulates other standards as STEP AP203, STEP 214 these results were expected. Because of this and because STEP AP242 is the de facto standard to exchange MBD data only the results of the STEP AP242 files are given.

3.1. STEP AP242e1-Analytical model (model accuracy is 0.01 mm)

3.2. STEP AP242e1-Convex NURBS surface (model accuracy is 0.01 mm) 3.3. STEP AP242e1-Concave NURBS surface (model accuracy is 0.01 mm)

3.4. STEP AP242e1-Concave convex NURBS surface (model accuracy is 0.01 mm)

3.5. STEP AP242e1-Analytical model (model accuracy is 0.001 mm)

3.6. STEP AP242e1-Convex NURBS surface (model accuracy is 0.001 mm) 3.7. STEP AP242e1-Concave NURBS surface (model accuracy is 0.001 mm) 3.9. STEP AP242e1-Comparative overview of the exchange of a 3D model (model accuracy is 0.01 mm) Fig. 6 gives a comparative overview of the exchange of four different types of 3D models (analytical, convex, concave, concave and convex) with a model accuracy of 0.01 mm using STEP AP242

![Figure 6](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-6-p005.png)

*Figure 6: STEP AP242 Comparative overview (model accuracy is 0.01 mm) Table 7: Deviation of STL vertices generated from an imported STEP AP242e1 file on a concave NURBS surface Table 8: Deviation of STL vertices generated from an imported STEP AP242e1 file on a concave convex NURBS surface*

3.10. STEP AP242e1-Comparative overview of the exchange of a 3D model (model accuracy is 0.001 mm) Fig. 7 gives a comparative overview of the exchange of four different types of 3D models (analytical, convex, concave, concave and convex) with a model accuracy of 0.001 mm using STEP AP242

![Figure 7](/Users/evanthayer/Projects/paperx/docs/2018_accuracy_of_geometry_data_exchange_using_step_ap242/figures/figure-7-p005.png)

*Figure 7: STEP AP242 Comparative overview (model accuracy is 0.001 mm)*

## 4 Conclusion

Within the MBD philosophy a CAD model is created using nominal values and the required tolerances are added as 3D annotations, the so-called PMI data. For typical mechanical parts these tolerances have a range of a few µm to a few hundredths of a mm. In case of an asymmetric tolerance the nominal value needs to be changed to the middle of the tolerance field to be able to generate the optimal tool path. This change of the nominal value can only be done when a CAD model can be transferred from a CAD to a CAM system with an adequate accuracy. In this context an adequate accuracy is an accuracy that is better than the smallest applied tolerance.

The goal of this research is to test whether 3D CAD models can be exchanged between different CAD CAM systems using STEP AP242 which supports exchange of MBD based models with an error of less than 1 µm.

The research focuses on the exchange of naked geometry without added intelligence. An example of geometry with added intelligence is a threaded hole. Each CAD system has its own unique way to add this intelligence (hole diameter and drilling depth, thread tapping information), e.g. in PTC Creo only the geometry of the drilled hole is created and the information for the tapping operation is added to additional geometry like a cylindrical surface.

The results of this research show that whether the accuracy achieved is sufficient or not depends very much on three things: the nature of the geometry (analytical or spline-based description) transferred, the accuracy used in the conversion and the settings of the STEP interface of the sending and receiving CAD CAM system.

Geometry that is described analytically can be exchanged with the highest accuracy. When a spline-based description is used the achieved accuracy is lower but still below 1 µm.

Two model accuracies were applied in the tests, 0.01 mm and 0.001 mm. The best accuracy was obtained using 0.001 mm.

To guarantee a good and usable transfer, the exchange between two systems must be tested and optimised. If this is the case, the tests show that almost all the CAD CAM systems tested are compliant. Two systems (Inventor and Siemens NX) give less good results for double curved surfaces. This may be due to settings that are not known and therefore not used in these tests. Further investigation is needed in this respect.

## References

- Quintana V, Rivest L, Pellerin R, et al. Will Modelbased definition replace engineering drawings throughout the product lifecycle? A global perspective from aerospace industry. Comput Ind 2010; 61(5):497-508.

- Alemanni M, Destefanis F, Vezzetti E. Model-based definition design in the product lifecycle management scenario. Int J Adv Manuf Technol 2011; 52(1-4):114.

- Cheney D, Fischer B. Measuring the PMI Modeling Capability in CAD Systems: Report 1-Combined Test Case Verification. Natl Inst Stand Technol NISTGCR 2015; 15-997. Boy J, Rosché P. Recommended Practices for PMI Polyline Presentation (AP203 AP214). 2014[Online] CAx Implementor Forum 2014. Fischer B. The changing face of CAD annotation. Mach Des Media 2011; 83(5):46-49. Maggiano BYL. Model-Based Measurement. Qual Mag 2015; (March):20-24. Brunsmann J, Wilkes W, Schlageter G, et al. State-ofthe-art of long-term preservation in product lifecycle management. Int J Digit Libr 2012; 12(1):27-39. Hedberg T, Lubell J, Fischer L, et al. Testing the Digital Thread in Support of Model-Based Manufacturing and Inspection. J Comput Inf Sci Eng 2016; 16(2):021001. Chang K-H, Chang K-H. Solid Modeling. In: eDesign Elsevier 2015; pp. 125-67. Bianconi F, Conti P, Angelo L Di. Interoperability among CAD CAM CAE systems: a review of current research trends. Geom Model Imaging--New Trends 1993; (January):82-89. Kim J, Pratt MJ, Iyer RG, et al. Standardized data exchange of CAD models with design intent. CAD Comput Aided Des 2008; 40(7):760-77.
