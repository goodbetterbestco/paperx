# 1993 robustness in solid modelling a tolerance based intuitionistic approach

Robustness In, Solid Modeling, - A Tolerance Based, Intuitionistic Approach, Shiaofen Fang, Xiaohong Zhu, Beat Bruderlin

Department of Computer Science
University of Utah
Salt Lake City, UT 84112 USA

## Abstract

This paper presents a new robustness method for geometric modeling operations. It com- This paper presents a new robustness method for geometric modeling operations. It com- putes geometric relations from the tolerances defined for geometric objects and dynamically putes geometric relations from the tolerances defined for geometric objects and dynamically updates the tolerances to preserve the properties of the relations, using an intuitionistic self-validation approach. Geometric algorithms using this approach are proved to be ro- bust. A robust Boolean set operation algorithm using this robustness approach has been

#### 4.2.1 Geometric Intersections

For Boolean operations on solids, we must determine the relation between two surfaces using our robustness method, and find intersections of the two surfaces if they are detected intersecting. Algebraic solutions are available for relation detections of planes and natural quadric surfaces.

An approach of finding all the conic section intersections of two natural quadrics is used based on Goldman and Miller's work[8]. The paper gives a complete set of all the special cases occurring when two natural quadric surfaces intersect in one or more conic sections, using a case by case geometric analysis approach. An example is shown in figure 8 in which three quadric surfaces intersect in a single ellipse.

Levin's parametric approach[18], which uses piecewise linear segments to approximate the intersection curves, is used to find other general intersections of two quadric surfaces. However, a piecewise linear approximation requires much larger tolerances to be used in the algorithm which in turn creates more ambiguous relations between objects. Therefore, using algebraic methods as we do for the special cases, is more efficient and more robust.

For geometric intersections, if the intersection computation involves approximation errors, these errors should be considered in the tolerance updating process. For example in Figure 9, two curves intersect at a point with their linear approximations. In building the tolerance

![Figure 8](/Users/evanthayer/Projects/paperx/docs/1993_robustness_in_solid_modelling_a_tolerance_based_intuitionistic_approach/figures/figure-8-p017.png)

*Figure 8: Three quadric surfaces intersect a single ellipse*

![Figure 9](/Users/evanthayer/Projects/paperx/docs/1993_robustness_in_solid_modelling_a_tolerance_based_intuitionistic_approach/figures/figure-9-p018.png)

*Figure 9: intersecting two curves with tolerances*

of the intersection point, the approximation error must be subtracted from \(\varepsilon\) and \(\Delta\) to guarantee that the point is incident on the two curves.

#### 4.2.2 Inside O utside O n Tests

Definition 1 (inside outside a regularized solid) A point \(P\) is inside a solid iff \(P\) is inside one of the GCBs of the solid or \(P\) is on the boundary of more than one GCB and the two implicit surfaces in the two different GCBs on which \(P\) is incident are coincident with opposite surface normals at \(P\).

A point \(P\) is outside a solid iff \(P\) is outside all the GCBs of the solid.

A point \(P\) is on the boundary of a solid iff \(P\) is neither inside nor outside the solid.

A point \(P\) is inside a \(G C B\) iff \(P\) is inside all the half spaces of the \(G C B\).

A point \(P\) is outside a \(G C B\) iff \(P\) is outside one of the half spaces of the \(G C B\).

A point \(P\) is on the boundary of a \(G C B\) iff \(P\) is neither inside nor outside the \(G C B\). A point \(P\) is inside a half space \(F^{+}\)iff \(P\) and \(F\) are apart and \(P\) is on the positive side of \(F\).

A point \(P\) is outside a half space \(F^{+}\)iff \(P\) and \(F\) are apart and \(P\) is on the negative side of \(F\).

Ambiguous relations that might occur during the computation are solved automatically as described in 3.3.

4.3 T e s t s

Two identical cubes of dimensions \(100 \times 100 \times 100\), one rotated about all three axis with an angle \(\alpha\), are tested for Boolean union operation. The initial tolerance \(\tau=1 E-3\), secondary error \(\nu=1 E-4\). Following cases are tested:

- When a > l.ShE 6, the two cubes intersect.

- When a = l.SE 6, ambiguities are created, after r is increased to AE-3, they are detected coincident.

- When a = 1.5E 6, ambiguities are created, after r is increased to 3E 3, they are detected coincident.

- When a-IE 6, ambiguities are created, after r is increased to 2E 3, they axe detected coincident.

Ambiguities in this example only occur in a very small range, namely for angles \(1.8 E-6>\) \([2,7]\) \(A>1 E-6\) (about a factor of two). In a previous approachrthis range was about \(10 E_{4}\), roughly 5000 times bigger. The main difference is that we are not using an analytical model, but an approximated model now, which is more forgiving, but still maintains the desired properties.

In another test example, we use two identical cylinders with radius 50 and height 400, one rotated about X axis with an angle \(\beta\), and then do a Boolean union of them. \(\tau\) and \(\nu\) are defined the same as the last example. Five pictures from this test example are shown at the end of this paper. When angle \(\beta \leq 0.000001\), ambiguities are created. Increasing tolerance \(\tau\) will solve all the ambiguities, and result in two coincident cylinders.

When we position the two cylinders parallel to each other, they intersect in two straight line. The second intersection which occurred previously no longer exists.

5 C o n \(c_{l}\) \(u_{s}\) i o n s

A new tolerance-based robustness method is introduced and applied to Boolean set opera­ tions on 3D objects bounded by planes and natural quadric surfaces. The algebraic methods for detecting conic section intersections for natural quadric surfaces, together with our toler­ ance based, intuitionistic robustness approach generate very reliable and efficient geometric algorithms.

The robustness method used in this paper is very general and can be applied to other geometric algorithms without any changes. In our implementation we completely abstracted away the low level geometric operations (computing intersections an geometric relations) from the high level application specific algorithms. This advantage makes the approach bet­ ter suitable as an underlying abstract data type for CAD systems (where different algorithms

- When a < 0.9 E 6, The two cubes are detected coincident

access the same model data) than previously published special reasoning solutions.

6 A \(c_{k}\) n o \(w_{l}\) e d g m e n t s

This work has been supported, in part, by NSF grants DDM-89 10229 and ASC-89 20219, and a grant from the Hewlett-Packard Laboratories. All opinions, findings, conclusions, or recommendations expressed in this document are those of the authors and do not necessarily reflect the view of the sponsoring agencies.

R e f e r e n c e s

- [6] FANG, S., AND \(B^{r}\) u d e r l i n, B. Robustness in geometric modeling-tolerance based methods. In computational Geometry-Methods, algorithms and Applications, Inter­

## References

- The inside/outside/on test for a solid, which is a key operation for a volume-based representation, can be done entirely with the half space representation and is redefined for our representation, based on tolerance regions \(\varepsilon, \delta\) and \(\Delta\).

- BRUDERLIN, B. Detecting ambiguities: An optimistic approach to robustness problems in computational geometry. Tech. Rep. UUCS 90-003 (submitted), Computer Science Department, University of Utah, April 1990.

- BRUDERLIN, B. Robust regularized set operations on polyhedra. In Proc. of Hawaii International Conference on System Science (January 1991).

- CHOU, S. C. Mechanical Geometry Theorem Proving. D. Reidel Publ., Doordrecht, Holland, 1988.

- EDELSBRUNNER, H., AND M u c k e, E. Simulation of simlicity: A technique to cope with degenerate cases in geometric algorithms. In Proc. of 4th A C M Symposium on Comp. Geometry (June 1988), pp. 118-133.

- FANG, S. Robustness in geometric modeling-an intuitionistic and toleranced-based approach. Ph.D dissertation, University of Utah, Computer Science Department, 1992.

- national Workshop on computational Geometry C G '91 (March 1991), Springer Lecture Notes in Computer Science 553, Bern, Switzerland.

- FANG, S., AND BRUDERLIN, B. Robust geometric modeling with implicit surfaces. In Proc. of International Conference on Manufacturing Automation, Hong Kong (August 1992).

- [ 8 ] GOLDMAN, R. N., AND M il l e r, J. R. Combining algebraic rigor with geometric robustness for the detection and calculation of conic sections in the intersection of two natural quadric surfaces. In Proc. of the A C M S IG G R A P H Symposium on Solid Modeling Foundations and C A D C A M Applications (June 1991), Austin Texas.

- GREENE, D., AND Y a o, F. Finite resolution computational geometry. In Proc. 27th IEEE Symp. Fundations of Computer Science (1986), pp. 143-152.

- GUIBAS, L., Sa l ESIN, D., AND STOLFI, J. Epsilon geometry: Building robust algo­ rithms from imprecise computations. In Proc. of 5th A C M Symposium on computational Geometry (1989).

- HOFFMANN, C. M. Geometric and Solid Modeling: An Introduction. Morgan Kaufmann Publishers, 1989, ch. 4.

- HOFFMANN, C. M. The problems of accuracy and robustness in geometric computation. IEEE Computer 22, 3 (March 1989), 31-41.

- H o f f m a n n, C. M., H o p c r o f t, J. E., AND K a r a s i c k, M. S. Towards implementating robust geometric computations. In Proc. of 4th A C M Symposium on computational Geometry (June 1988), pp. 106-117.

- H o f f m a n n, C. M., H o p c r o f t, J. E., a n d K a r a s i c k, M. S. Robust set operations on polyhedral solids. IEEE Computer Graphics and Application 9 (November 1989).

- KAPUR, D. Using grobner bases to reason about geometry. J. Symbolic Comp. 2 (1986), 399-408.

- KARASICK, M. On the representation and manipulations of rigid solids. Ph.D thesis, McGill University, 1989.

- KUTZLER, B. Algebraic approaches to automated geometry proving. Ph.D Diss., Re­ port 88-74.0, Research Institute for Symbolic Comp., Kepler University, Linz, Austria, 1988.

- LEVIN, J. A parametric algorithm for drawing pictures of solid objects composed of quadric surfaces. Communications of A C M 19, 10 (October 1976), 555-563.

- MlLENKOVIC, V. Verifiable implementations of geometric algorithm using finite preci­ sion arithmetic. Artificial Intelligence 37 (1988), 377-401.

- MlLENKOVIC, V. Verifiable implementations of geometric algorithm using finite preci­ sion arithmetic. Ph.D thesis, Carnegie Mellon University, 1988.

- MlLENKOVIC, V. Calculating approximate curve arrangement using rounded arith­ metic. In ACM Annual Symposium on computational Geometry (1989), pp. 197-207.

- MlLENKOVIC, V., AND Nackman, L. R. Finding compact coordinate representations for polygons and polyhedra. In ACM Annual Symposium on computational Geometry (1990), pp. 244-252.

- MUDUR, S. P., AND KOPARKAR, P. A. Interval methods for processing geometric objects. IEEE Computer Graphics and Application 4, 2 (February 1984), 7-17.

- OTTMANN, T., TlIIEMT, G., AND ULLRICH, C. Numerical stability of geometric algorithms. In ACM Annual Symposium on computational Geometry (June 1987), pp. 119-125.

- ReqUICHA, A. A. G. representation for rigid solids: Theory, methods and systems. Computing Surveys 12, 4 (December 1980).

- SALESIN, D. Epsilon geometry: Building robust algorithms from imprecise computa­ tions. Ph.D thesis, Stanford University, 1991. ·

- SALESIN, D., STOLFI, J., AND GuIBAS, L. Epsilon geometry: Building robust al­ gorithms from imprecise calculations. In A C M A n n u a l S ym posiu m on computational G eom etry (1989), pp. 208-217.

- SEGAL, M. Using tolerances to guarantee valid polyhedral modeling results. Computer Graphics 24, 4 (1990), 105-114.

- STEWART, A. J. Robust point location in approximate polygons. In 1991 Canadian Conference on Compxitational G eom etry (August 1991), pp. 179-182.

- STEWART, A. J. The theory and practice of robust geometric computation, or, how to build robust solid modelers. Ph.D Thesis 91-1229, Department of Computer Science, Cornell University, 1991.

- SUGIIIARA, K., AND IRI, M. Geometric algorithms in finite precision arithmetic. Res. Mem. 88-14, Math. Eng. and Information Physicas, University of Tokyo, 1988.

- SUGIHARA, K., AND IRI, M. A solid modeling system free from topological inconsis­ tency. Journal o f Inform ation P rocessing 12, 4 (1989), 380-393.

- TROELSTRA, A. S. Constructivism in M athem atics: A n Introduction. Elsevier Science Pub. Co., 1988.

- Yap, C. K. A geometric consistency theorem for a symbolic perturbation theorem. In Proc. o f 4th A C M S ym posium on C om p. G eom etry (June 1988), pp. 134-142.
