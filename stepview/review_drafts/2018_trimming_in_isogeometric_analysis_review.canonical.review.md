# A Review of Trimming in Isogeometric Analysis

Benjamin Marussig, Thomas J. R. Hughes

[missing from original]

## Abstract

We review the treatment of trimmed geometries in the context of design, data exchange, and computational simulation. Such models are omnipresent in current engineering modeling and play a key role for the integration of design and analysis. The problems induced by trimming are often underestimated due to the conceptional simplicity of the procedure. In this work, several challenges and pitfalls are described.

## 1 Introduction

Trimming is much more complicated than most people think. It is one of the most fundamental procedures in Computer Aided Geometric Design (CAGD) that allows the construction of complex geometries. Unfortunately, it is also the source of one of the most serious impediments to interoperability between Computer Aided Design (CAD) systems and downstream applications like numerical simulation [268]. This work aims to increase awareness of this issue by providing a broad overview of trimmed geometries, addressing design, data exchange, and analysis aspects.

Once upon a time, the original vision of CAD was the holistic treatment of the engineering design process [247]. However, it has emerged as an autonomous discipline which seeks to optimize the modeling and visualization of geometric objects. On the other hand, computational analysis has focused on the problem-solving part of engineering. Thus, the main attention has been drawn to the development of mathematical models governing physical phenomena as well as the reliability and efficiency of their numerical treatment. Still, design models are usually the starting point of the analysis process in order to define the domain of interest. In current engineering design, however, they are subsequently approximated by finite element meshes for computation. Since this is a fundamental step in conventional simulations, there is a substantial body of literature on meshing, see e.g., [28, 94, 98, 281, 322] and the references cited therein. Finite element analysis (FEA) was a widely used commercially available procedure in engineering prior to the advent of commercial CAD. Nevertheless, FEA finds itself separated from design by its own representation of geometrical objects, which is different from CAD. The given situation has contributed to a loss of communication between these fields, both of which are essential in the process of addressing practical engineering problems.

Isogeometric analysis [66, 140] provides an alternative to the conventional analysis methodology that converts CAD models for use in FEA. The key idea is to perform numerical simulations based on CAGD technologies. Besides the fact that this synthesis offers several computational benefits, such as high continuity [67, 68, 187], the long term goal of isogeometric analysis is to enhance the overall engineering product development process by closing the gap between design and analysis. An invaluable byproduct of this effort is the initiation of a dialog between these two communities which had drifted apart.

![Figure 1 Model of a half of a torus](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-1-p002.png)

*Figure 1 Model of a half of a torus: an initial non-trimmed torus and surface defined in the xy-plane, b resulting trimmed object, c closeup showing the deviation from the visualization mesh (blue background) and the computed intersection curve C Trimmed (yellow) of the objects, and d closeup illustrating the difference of the original inner circle of the torus C Torus (red) to the intersection curve computed. The images c and d are captured in top view. (Color figure online)*

and limitations. Due to the capability of current CAD systems it may seem that design models are ideal creations, but this notion is simply not true. There are several open issues that need to be solved. Compact overviews are given in the independent compilations of Kasik et al. [151] and Piegl [228]. In these papers, robustness and interoperability issues are identified as crucial CAD problems. Although trimmed geometries are not explicitly mentioned in these papers, they play a central role in both cases.

The most common description of CAGD models is the boundary representation (B-Rep) where an object is represented by its boundary surfaces rather than a volume discretization. These surfaces are usually constructed independently from each other and often only certain regions of a surface are supposed to be part of the actual object. Trimming allows a modeler to cut away the superfluous surface areas. To be precise, the visualization of the surfaces is adapted while their parameterization and mathematical description remain unchanged. This procedure is very convenient and inevitable in many operations such as surface-to-surface intersection. However, the main problem is that trimming cannot practically be performed exactly within CAGD applications. Thus, the final object possesses small gaps and overlaps between its surfaces. Figure 1 illustrates some inaccuracies of a model defined by a torus inter sected by a plane. Note that the discrepancy between the computed intersection \(\boldsymbol{C}_{\text {Trimmed }}\) and the related exact solu tion \(\boldsymbol{C}_{\text {Torus }}\) is scarcely visible. The imperfections of trimmed geometries are usually very well hidden from the user, but they surface as soon as a design model is applied to down stream applications. To use the words of Piegl [228]:

While one can cheat the eye in computer graphics and animation, the milling machine is not as forgiving. Numerical simulation of practical trimmed models is more than the analysis of a specific type of a CAGD representation. It rather addresses the core issue of the interoperability between design and analysis, namely the appropriate treatment of the deficiencies of design models. To be clear, this problem is not restricted to isogeometric analysis, but manifests itself as complications during the meshing process in the case of conventional analysis methodology. In fact, geometry repair and corrections of design models are mandatory tasks, before actual mesh generation can be applied [86, 114]. Isogeometric analysis of trimmed geometries tackles these issues directly at the source, i.e., the design model. Thus, many pitfalls that may occur in a meshing process can be circumvented [61].

It is important to note that the CAD community is also influenced by the ongoing dialog. An increasing number of researchers propose new modeling concepts that take the needs of downstream applications into account, see e.g. [61, 203, 247]. We believe that the aligned efforts of both communities are the keys to unite design and analysis, resulting in a holistic treatment of the engineering design process.

This paper intends to encourage the interaction of these fields by providing an overview of various aspects related to trimmed geometries. Section 2 begins by reviewing some basic concepts frequently used in CAGD. It is focused on non-uniform rational B-spline (NURBS) based B-Rep models since they are the most popular representation in engineering design. Based on this, Sect. 3 addresses the role of trimming in the context of design. A critical assessment of exchanging data between different software packages is provided in Sect. 4. Finally, various strategies to deal with trimmed geometries in an isogeometric analysis process are outlined in Sect. 5. Each of these three review sections closes with a brief summary of the main points and their discussion. Section 6 moves on to focus on a particular aspect, namely the stabilization of a trimmed basis. In the concluding section, the main findings are summarized and some open research questions are listed.

## 2 CAGD Fundamentals

B-splines and their rational counterpart NURBS provide the basis for the geometric modeling of most engineering models. This section gives a brief overview of this CAGD technology focusing on aspects which are crucial for the subsequent discussion. For further information related to spline theory the interested reader is referred to [34, 62, 83]. Detailed descriptions of efficient algorithms can be found in [230]. In the present paper, the terms B-spline and NURBS are used to refer to basis functions. The geometric objects described using these functions, i.e., curves and surfaces, may be generally denoted as patches.

### 2.1 Basis Functions

B-splines \(B_{i, p}\) consist of piecewise polynomial segments which are connected by a certain smoothness. They are defined recursively for a fixed polynomial degree \(p\) by a strictly convex combination of B-splines of the previous degree, \(p-1\), given by

$$
\begin{align*} B_{i, p}(u)= & \frac{u-u_{i}}{u_{i+p}-u_{i}} B_{i, p-1}(u) \\ & +\frac{u_{i+p+1}-u}{u_{i+p+1}-u_{i+1}} B_{i+1, p-1}(u) \tag{1} \end{align*}
$$

![Figure 2 Non-vanishing B-splines B i , p of knot span s for different degrees p = { 0, 1, 2 } which are based on a knot vector with equally spaced knots](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-2-p003.png)

*Figure 2 Non-vanishing B-splines B i , p of knot span s for different degrees p = { 0, 1, 2 } which are based on a knot vector with equally spaced knots: Non-vanishing B-splines B i, p of knot span s for different degrees p = { 0, 1, 2 } which are based on a knot vector with equally spaced knots*

![Figure 3 Polynomial segments  s of a quadratic B-spline due to differ- ent knot vectors 훯 . Note the different continuity C between the seg- ments based on the knot multiplicity](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-3-p003.png)

*Figure 3 Polynomial segments  s of a quadratic B-spline due to differ- ent knot vectors 훯 . Note the different continuity C between the seg- ments based on the knot multiplicity: Polynomial segments  s of a quadratic B-spline due to different knot vectors 훯 . Note the different continuity C between the segments based on the knot multiplicity*

The essential element for this construction is the knot vec tor \(\Xi\) characterized as a non-decreasing sequence of coor dinates \(u_{i} \leqslant u_{i+1}\). The parameters \(u_{i}\) are termed knots and the half-open interval \(\left[u_{i}, u_{i+1}\right)\) is called \(i\) th knot span. Each knot span has \(p+1\) non-vanishing B-splines as illustrated in Fig. 2. Each basis function is entirely defined by \(p+2\) knots and its support, \(\operatorname{supp}\left\{B_{i, p}\right\}=\left\{u_{i}, \ldots, u_{i+p+1}\right\}\), is local. Within each non-zero knot span \(s, u_{s}<u_{s+1}\), of its support, \(B_{i, p}\) is described by a polynomial segment \(B_{i}^{s}\). Each knot value indicates a location within the parameter space which is not \(C^{\infty}\)-continuous, i.e., where two adjacent \(\mathcal{B}_{i}^{s}\) join. Suc cessive knots may share the same value, which is indicated by the knot multiplicity \(m\), i.e., \(u_{i}=u_{i+1}=\cdots=u_{i+m-1}\). In general, the continuity between adjacent segments is \(C^{p-m}\).

is a special form of such a knot vector since it yields the classical p th-degree Bernstein polynomials. To be precise, Bernstein polynomials are usually defined over the interval

$$
\begin{aligned} a_{0,0} & =1 \\ a_{k, 0} & =\frac{a_{k-1,0}}{u_{i+p-k+1}-u_{i}}, \\ a_{k, \ell} & =\frac{a_{k-1, \ell}-a_{k-1, \ell-1}}{u_{i+p+\ell-k+1}-u_{i+\ell}} \quad \ell=1, \ldots, k-1, \\ a_{k, k} & =\frac{-a_{k-1, k-1}}{u_{i+p+1}-u_{i+k}} . \end{aligned}
$$

![Figure 4 B-spline basis specified by an open knot vector, i.e., 훯 = { 0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4 }](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-4-p004.png)

*Figure 4 B-spline basis specified by an open knot vector, i.e., 훯 = { 0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4 }: B-spline basis specified by an open knot vector, i.e., 훯 = { 0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4 }*

[0, 1] . If necessary, the restriction to this interval can be easily accomplished by a coordinate transformation.

As a whole, B-splines based on a common knot vector 𝛯 form a partition of unity, i.e.,

and they are linearly independent, i.e.,

$$
\begin{equation*} \sum_{i=0}^{I-1} B_{i, p}(u) c_{i}=0 \tag{5} \end{equation*}
$$

$$
\begin{equation*} \mathcal{X}(u):=\boldsymbol{C}(u)=\sum_{i=0}^{I-1} B_{i, p}(u) \boldsymbol{c}_{i}, \tag{9} \end{equation*}
$$

is satisfied if and only if \(c_{i}=0, i=0, \ldots, I-1\). Due to the latter property, every piecewise polynomial \(f_{p, \Xi}\) of degree \(p\) over a knot sequence \(\Xi\) can be uniquely described by a linear combination of the corresponding \(B_{i, p}\). Hence, they form a basis of the space \(\mathbb{S}_{p, \Xi}\) collecting all such functions

An example of a cubic B-spline basis defined by an open knot vector is shown in Fig. 4.

The first derivative of B-splines are computed by a linear combination of B-splines of the previous degree

$$
\begin{align*} B_{i, p}^{\prime}(u)= & \frac{p}{u_{i+p}-u_{i}} B_{i, p-1}(u) \\ & -\frac{p}{u_{i+p+1}-u_{i+1}} B_{i+1, p-1}(u) \tag{7} \end{align*}
$$

For the computation of the k th derivative, this is generalized to

$$
\begin{equation*} B_{i, p}^{(k)}(u)=\frac{p!}{(p-k)!} \sum_{\ell=0}^{k} a_{k, \ell} B_{i+\ell, p-k}(u), \tag{8} \end{equation*}
$$

Remark 1 The knot differences of the denominators involved in the recursive formulae (1), (7) and (8) can become zero. In such a case the quotient is defined to be zero.

### 2.2 Curves

B-spline curves of degree \(p\) are defined by basis functions \(B_{i, p}\) due to a knot vector \(\Xi\) with corresponding coefficients in model space \({ }^{1} \boldsymbol{c}_{i}\) which denote control points. The geo metrical mapping \(\mathcal{X}\) from parameter space to model space is given by

$$
\begin{equation*} \sum_{i=0}^{I-1} B_{i, p}(u)=1, \quad u \in\left[u_{0}, u_{I+p}\right], \tag{4} \end{equation*}
$$

with I representing the total number of basis functions. The derivative is

$$
\begin{equation*} \mathbb{S}_{p, \Xi}=\sum_{i=0}^{I-1} B_{i, p} c_{i}, \quad c_{i} \in \mathbb{R} \tag{6} \end{equation*}
$$

$$
\begin{equation*} \mathbf{J}_{\mathcal{X}}(u):=\sum_{i=0}^{I-1} B_{i, p}^{\prime}(u) \boldsymbol{c}_{i} . \tag{10} \end{equation*}
$$

In general, control points \(\boldsymbol{c}_{i}\) are not interpolatory, i.e., they do not lie on the curve. The connection of \(\boldsymbol{c}_{i}\) by straight lines is called the control polygon and it provides an approximation of the actual curve. An important property of a B-spline curve is that it is contained within the convex hull of its control polygon. In particular, a polynomial seg ment related to a non-zero knot span \(s\), i.e., \(u \in\left[u_{s}, u_{s+1}\right)\), is in the convex hull of the control points \(\boldsymbol{c}_{s-p}, \ldots, \boldsymbol{c}_{s}\). The continuity of the whole piecewise polynomial curve \(\boldsymbol{C}(u)\) is inherited from its underlying basis functions, i.e., the continuity at knots is determined by the knot multiplicity, and the position of its control points. These relationships are illustrated in Fig. 5. Note that the interpolatory B-spline \(B_{4,2}\) of Fig. 5a corresponds to the kink at \(\boldsymbol{c}_{4}\) in Fig. 5b and that the second polynomial segment lies within the con vex hull of \(\boldsymbol{c}_{1}\) to \(\boldsymbol{c}_{3}\). If the curve consists of a single poly nomial segment, i.e., the associated \(\Xi\) is of form (3), the curve is referred to as Bézier curve. A polynomial segment of a B-spline curve is termed a Bézier segment, if it can be

The model space is also referred to as physical space.

![Figure 5 Example of a B-spline curve](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-5-p005.png)

*Figure 5 Example of a B-spline curve: a B-splines based on 훯 = { 0, 0, 0, 1, 2, 3, 3, 4, 4, 4 } and b a corresponding piecewise polynomial curve. In b, circles denote control points and the dotted lines indicate the convex hull of the dashed curve segment u ∈[1, 2)*

represented by a Bézier curve. In Fig. 5b, this is the case for the segment \(u \in[3,4]\) defined by the control points \(\boldsymbol{c}_{4}\) to \(\boldsymbol{c}_{6}\). B-spline curves can be generalized to represent rational functions such as conic sections. For this purpose, weights \(w_{i}\) are associated with the control points such that where \(d\) denotes the spatial dimension of the model space. The homogeneous coordinates \(\boldsymbol{c}_{i}^{h}\) specify a B-spline curve \(\boldsymbol{C}^{h}(u)\) in a projective space \(\mathbb{R}^{d+1}\). In order to obtain a curve in \(\mathbb{R}^{d}\), the geometrical mapping (9) is extended by a per spective mapping \(\mathcal{P}\) with the center at the origin of \(\mathbb{R}^{d+1}\). This projection is given by

$$
\begin{equation*} \boldsymbol{C}(u)=\mathcal{P}\left(\boldsymbol{C}^{h}(u)\right)=\frac{\boldsymbol{C}^{w}(u)}{w(u)}, \tag{12} \end{equation*}
$$

$$
\begin{equation*} \frac{\partial C^{w}(u)}{\partial u}=\sum_{i=0}^{I-1} B_{i, p}^{\prime}(u) c_{i}^{w} . \tag{16} \end{equation*}
$$

where \(\boldsymbol{C}^{w}=\left(\boldsymbol{C}_{1}^{h}, \ldots, \boldsymbol{C}_{d}^{h}\right)^{\top}\) are the homogeneous vector components of the curve and the weighting function is determined by

The application of Eq. (12) is illustrated in Fig. 6. The pro jection \(\boldsymbol{C}(u)\) is denoted as a non-uniform rational B-spline (NURBS) curve. The term rational indicates that the result ing curves are piecewise rational polynomials, whereas the term non-uniform emphasizes that the knot values can be distributed arbitrarily.

![Figure 6 Perspective mapping  of a quadratic B-spline curve C h ( u ) in homogeneous form ℝ 3 to a circular arc C ( u ) in model space ℝ 2 . The mapping is indicated by dashed lines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-6-p005.png)

*Figure 6 Perspective mapping  of a quadratic B-spline curve C h ( u ) in homogeneous form ℝ 3 to a circular arc C ( u ) in model space ℝ 2 . The mapping is indicated by dashed lines: Perspective mapping  of a quadratic B-spline curve C h (u) in homogeneous form ℝ 3 to a circular arc C (u) in model space ℝ 2. The mapping is indicated by dashed lines*

The derivative of the NURBS geometrical mapping is defined by

$$
\begin{equation*} \mathbf{J}_{\mathcal{X}}(u):=\frac{w(u) \frac{\partial C^{w}(u)}{\partial u}-\frac{\partial w(u)}{\partial u} C^{w}(u)}{(w(u))^{2}}, \tag{14} \end{equation*}
$$

$$
\begin{equation*} \boldsymbol{c}_{i}^{h}=\left(w_{i} \boldsymbol{c}_{i}, w_{i}\right)^{\top}=\left(\boldsymbol{c}_{i}^{w}, w_{i}\right)^{\top} \in \mathbb{R}^{d+1}, \tag{11} \end{equation*}
$$

$$
\begin{equation*} \frac{\partial w(u)}{\partial u}=\sum_{i=0}^{I-1} B_{i, p}^{\prime}(u) w_{i}, \tag{15} \end{equation*}
$$

Another way to represent NURBS curves is

$$
\begin{equation*} C(u)=\sum_{i=0}^{I-1} R_{i, p}(u) c_{i}, \tag{17} \end{equation*}
$$

$$
\begin{equation*} w(u)=\sum_{i=0}^{I-1} B_{i, p}(u) w_{i} . \tag{13} \end{equation*}
$$

$$
\begin{equation*} R_{i, p}(u)=\frac{w_{i} B_{i, p}(u)}{w(u)} . \tag{18} \end{equation*}
$$

Since the weights \(w_{i}\) are now associated with B-splines \(B_{i, p}\) the mapping (17) employs control points \(\boldsymbol{c}_{i}\) of the model space. In gen eral, NURBS curves degenerate to B-spline curves, if all weights are equal. Hence, they are a generalization of them.

### 2.3 Spline Interpolation

Since condition (21) guarantees that \(\mathbf{A}_{u}\) does not become singular, it is expected that the corresponding condition number gets large if \(\bar{u}\) approaches the limits of its allowed range. Non-uniformity of \(\bar{u}\) is another reason for an increas ing condition number. In fact, it gets arbitrary large if two interpolation sites approach each other, while the others are fixed. Several authors [11, 34, 184] recommend to interpo late at the Greville abscissae \(u^{g}\) which are obtained by the following knot average

These abscissae are well known in CAGD and used for different purposes, e.g., to generate a linear geometrical mapping [83]. The most important feature of this approach is that it induces a stable interpolation scheme for moderate degrees p.

### 2.4 Tensor Product Surfaces

Tensor product surfaces allow an extremely efficient evalu ation of patches. They play an important role in CAGD. In particular, B-spline and NURBS patches are very common. Bivariate basis functions for B-spline patches are obtained by the tensor product of univariate B-splines which are defined by separate knot vectors \(\Xi_{I}\) and \(\Xi_{J}\). These knot vec tors determine the parameterization in the directions \(u\) and \(v\), respectively. Moreover, they span the bivariate basis of a

$$
\begin{equation*} \frac{\partial^{k+l}}{\partial^{k} u \partial^{l} v} \boldsymbol{S}(u, v)=\sum_{i=0}^{I-1} \sum_{j=0}^{J-1} B_{i, p}^{(k)}(u) B_{j, q}^{(l)}(v) \boldsymbol{c}_{i, j} . \tag{24} \end{equation*}
$$

![Figure 7 A bivariate basis determined by 훯 I = { 1, 1, 1, 2, 3, 4, 4, 4 } and 훯 J = { 1, 1, 1, 2.5, 2.5, 4, 4, 4 } for u and v , respectively](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-7-p006.png)

*Figure 7 A bivariate basis determined by 훯 I = { 1, 1, 1, 2, 3, 4, 4, 4 } and 훯 J = { 1, 1, 1, 2.5, 2.5, 4, 4, 4 } for u and v , respectively: a shows the bivariate basis spanned by 훯 I and 훯 J, whereas b illustrates the construction of a corresponding bivariate B-spline*

$$
\begin{equation*} f\left(\bar{u}_{j}\right)=\sum_{i=0}^{I-1} B_{i, p}\left(\bar{u}_{j}\right) c_{i}, \quad j=0, \ldots, I-1 \tag{19} \end{equation*}
$$

$$
\begin{equation*} B_{i, p}\left(\bar{u}_{i}\right) \neq 0, \quad i=0, \ldots, I-1 . \tag{21} \end{equation*}
$$

$$
\begin{equation*} \mathbf{A}_{u}[j, i]=B_{i, p}\left(\bar{u}_{j}\right), \quad i, j=0, \ldots, I-1 \tag{20} \end{equation*}
$$

patch. Combined with a bidirectional grid of control points \(\boldsymbol{c}_{i, j}\) the geometrical mapping \(\mathcal{X}\) is determined by

$$
\begin{equation*} u_{i}^{g}=\frac{u_{i+1}+u_{i+2}+\cdots+u_{i+p}}{p} . \tag{22} \end{equation*}
$$

$$
\begin{equation*} \mathcal{X}(u, v):=\boldsymbol{S}(u, v)=\sum_{i=0}^{I-1} \sum_{j=0}^{J-1} B_{i, p}(u) B_{j, q}(v) \boldsymbol{c}_{i, j} . \tag{23} \end{equation*}
$$

The polynomial degrees are denoted by \(p\) and \(q\), respec tively for each parametric direction. The Jacobian of the mapping (23) is computed by substituting the occurring univariate B-splines by their first derivatives, alternately for each direction. In general, derivatives of B-spline patches are specified by

The efficiency of tensor product surfaces stems from the fact that their evaluation can be performed by a successive evaluation of curves [62]. Suppose the parametric value \(v^{\text {iso }}\) is fixed, the surface equation yields

$$
\begin{align*} \boldsymbol{S}\left(u, v^{i s o}\right) & =\sum_{i=0}^{I-1} \sum_{j=0}^{J-1} B_{i, p}(u) B_{j, q}\left(v^{i s o}\right) \boldsymbol{c}_{i, j} \\ & =\sum_{i=0}^{I-1} B_{i, p}(u)\left(\sum_{j=0}^{J-1} B_{j, q}\left(v^{i s o}\right) \boldsymbol{c}_{i, j}\right) \tag{25}\\ & =\sum_{i=0}^{I-1} B_{i, p}(u) \tilde{\boldsymbol{c}}_{i}=\boldsymbol{C}^{i s o}(u) \end{align*}
$$

with \(\boldsymbol{C}^{\text {iso }}(u)\) denoting an isocurve of the surface defined by new control points \(\tilde{\boldsymbol{c}}_{i}\). Hence, a surface can be evaluated by \(I+1\) or \(J+1\) curve evaluations, depending which paramet ric direction is evaluated first.

The tensor product nature of the patches is illustrated in Fig. 7 by means of a bivariate basis. Note that the univariate knot values propagate through the whole parameter space. If both knot vectors of the resulting patch are of form (3), it is referred to as Bézier surface. NURBS surfaces are derived analogous to curves by the introduction of weights.

### 2.5 Constructing Patches by Boundary Curves

The most basic surface construction scheme is to connect two curves \(\boldsymbol{C}_{i}\) with \(i=1,2\) by a linear interpolation. The resulting surfaces are termed ruled surfaces and they are defined as where \(u, v \in[0,1]\). If \(\boldsymbol{C}_{i}\) have the same degree and knot vector, it is straightforward to represent \(\boldsymbol{S}^{r}\) as a single ten sor product surface. In this case the connection lines on \(\boldsymbol{S}^{r}\) associate points of equal parameter value. Alternatively, the ruling (26) could also be performed according to relative arc length. This yields a different geometry which cannot be converted to a NURBS patch [230].

The construction of Coons patches is another very com mon procedure. Thereby, a surface \(\boldsymbol{S}^{c}\) is sought to fit four boundary curves \(\boldsymbol{C}_{i}(u)\) and \(\boldsymbol{C}_{j}(v)\) with \(i=1,2\) and \(j=3,4\).

$$
\begin{align*} & \boldsymbol{S}^{c}(0,0)=\boldsymbol{C}_{1}(u=0)=\boldsymbol{C}_{3}(v=0) \tag{27}\\ & \boldsymbol{S}^{c}(1,0)=\boldsymbol{C}_{1}(u=1)=\boldsymbol{C}_{4}(v=0) \tag{28}\\ & \boldsymbol{S}^{c}(0,1)=\boldsymbol{C}_{2}(u=0)=\boldsymbol{C}_{3}(v=1) \tag{29}\\ & \boldsymbol{S}^{c}(1,1)=\boldsymbol{C}_{2}(u=1)=\boldsymbol{C}_{4}(v=1) \tag{30} \end{align*}
$$

$$
\begin{align*} \boldsymbol{S}^{r}(u, v) & =(1-v) \boldsymbol{C}_{1}(u)+v \boldsymbol{C}_{2}(u) \\ & =(1-v) \boldsymbol{S}^{r}(u, 0)+v \boldsymbol{S}^{r}(u, 1) \tag{26} \end{align*}
$$

![Figure 8 Components of a bilinear Coons patch due to the boundary curves C i ( u ) and C j ( v ) highlighted by thick lines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-8-p007.png)

*Figure 8 Components of a bilinear Coons patch due to the boundary curves C i ( u ) and C j ( v ) highlighted by thick lines: Components of a bilinear Coons patch due to the boundary curves C i (u) and C j (v) highlighted by thick lines*

![Figure 9 Tensor product representation of triangular patches](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-9-p008.png)

*Figure 9 Tensor product representation of triangular patches: a an angle between adjacent edges has 180 ◦ and b a side shrinks to a point. Circles mark the corner points of the resulting patch*

Using a bilinear interpolation a Coons patch is given by

$$
\begin{equation*} \boldsymbol{S}^{c}(u, v)=\boldsymbol{S}_{u}^{r}(u, v)+\boldsymbol{S}_{v}^{r}(u, v)-\boldsymbol{S}_{c}^{r}(u, v), \tag{31} \end{equation*}
$$

where \(\boldsymbol{S}_{u}^{r}\) and \(\boldsymbol{S}_{v}^{r}\) are ruled surfaces based on \(\boldsymbol{C}_{i}(u)\) and \(\boldsymbol{C}_{j}(v)\), respectively, and \(\boldsymbol{S}_{c}^{r}\) is the bilinear interpolant to the four corner points

These various parts of a Coons patch are visualized in Fig. 8. Equation (31) can be generalized by using two arbitrary smooth interpolation functions \(f_{0}(s)\) and \(f_{1}(s)\) fulfilling

$$
\begin{equation*} f_{k}(\ell)=\delta_{k \ell}, \quad k, \ell=0,1, \tag{33} \end{equation*}
$$

The corresponding Coons patch can be expressed in matrix form as

$$
\begin{gather*} \boldsymbol{S}^{c}(u, v)= \\ -\left[\begin{array}{c} -1 \\ f_{0}(u) \\ f_{1}(u) \end{array}\right]^{\top}\left[\begin{array}{ccc} \mathbf{0} & \boldsymbol{S}^{c}(u, 0) & \boldsymbol{S}^{c}(u, 1) \\ \boldsymbol{S}^{c}(0, v) & \boldsymbol{S}^{c}(0,0) & \boldsymbol{S}^{c}(0,1) \\ \boldsymbol{S}^{c}(1, v) & \boldsymbol{S}^{c}(1,0) & \boldsymbol{S}^{c}(1,1) \end{array}\right]\left[\begin{array}{c} -1 \\ f_{0}(v) \\ f_{1}(v) \end{array}\right], \tag{35} \end{gather*}
$$

$$
\boldsymbol{S}^{\triangle(r, s, t)}=\sum_{\substack{i+j+k=p \\ i, j, k \geqslant 0}} B_{i, j, k, p}(r, s, t) \boldsymbol{c}_{i, j, k},
$$

with \(\mathbf{0} \in \mathbb{R}^{d}\) denoting the zero vector. Various functions may be used to specify \(f_{k}\) such as Hermite polynomials or trigonometric functions. In case of Bernstein polynomials, the surfaces \(\boldsymbol{S}_{u}^{r}, \boldsymbol{S}_{v}^{r}\), and \(\boldsymbol{S}_{c}^{r}\) are in Bézier or B-spline form and the resulting Coons patch can be represented as a sin gle NURBS surface.

$$
\begin{equation*} B_{i, j, k, p}(r, s, t)=\frac{p!}{i!j!k!} r^{i} s^{j} t^{k}, \tag{37} \end{equation*}
$$

Finally, Gordon surfaces are a further generalization of Coons patches, where the surface \(\boldsymbol{S}_{u}^{r}\) and \(\boldsymbol{S}_{v}^{r}\) interpolate sets of isocurves rather than boundary curves. Gordon surfaces are also referred to as transfinite interpolation [103]. The term indicates that these surfaces interpolate an infinite number of points, i.e., the boundary curves and isocurves.

![Figure 10 Triangular Bézier patch of degree p = 3](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-10-p008.png)

*Figure 10 Triangular Bézier patch of degree p = 3: a the general structure of the control grid and b a corresponding surface*

Based on this definition, ruled surfaces, Coons patches, and Gordon surfaces may be generally referred to as transfinite interpolations.

### 2.6 Representation of Triangles

$$
\boldsymbol{S}_{c}^{r}(u, v)=\left[\begin{array}{l} 1 \tag{32}\\ u \end{array}\right]^{\top}\left[\begin{array}{lll} \boldsymbol{S}^{c}(0,0) & \boldsymbol{S}^{c}(0,1) \\ \boldsymbol{S}^{c}(1,0) & \boldsymbol{S}^{c}(1,1) \end{array}\right]\left[\begin{array}{l} 1 \\ v \end{array}\right] .
$$

Triangular patches may be represented by tensor product surfaces despite their four-sided nature. Therefore, either a side or a point is degenerated as shown in Fig. 9. Such degenerated patches are often used since it is convenient to use only one surface representation. However, it is apparent that this can lead to a distorted parameterization. In addition, the enforcement of continuity between adjacent surfaces is difficult in this case.

An alternative is to use triangular patches. A point on such surfaces is defined by barycentric coordinates, i.e., \((r, s, t)\) with \(r+s+t=1\). We will focus on triangular Bézier patches \(\boldsymbol{S}^{\triangle}\) which are specified as

$$
\begin{equation*} f_{0}(s)+f_{1}(s)=1, \quad s \in[0,1], \quad s=u, v . \tag{34} \end{equation*}
$$

representing linearly independent bivariate Bernstein polynomials of degree \(p\). The related control points \(\boldsymbol{c}_{i, j, k}\) form a triangular array as shown in Fig. 10 for the cubic case. The resulting patch fulfills the convex hull property and its boundaries are Bézier curves. Rational triangular Bézier patches may be defined again by the introduction of weights. Despite the potential of triangular patches, there are currently no commercial CAD applications that admit the use of splines on triangulations.

### 2.7 Trimmed Surfaces

In order to represent arbitrary surface boundaries when using tensor product surfaces, patches can be modified by trimming procedures. For this purpose, curves are defined within the parameter space of a surface \(\boldsymbol{S}(u, v)\). These trim ming curves \(\boldsymbol{C}^{t}(\tilde{u})\) are usually B-spline or NURBS curves. They are given by

$$
\boldsymbol{C}^{t}(\tilde{u})=\left[\begin{array}{c} u(\tilde{u}) \tag{38}\\ v(\tilde{u}) \end{array}\right]=\sum_{i=0}^{I-1} R_{i, p}(\tilde{u}) \boldsymbol{c}_{i}^{t},
$$

where \(\boldsymbol{c}_{i}^{t} \in \mathbb{R}^{2}\) are the control points of the trimming curve given in the parameter space of the trimmed surface. Con nected trimming curves are ordered such that they form a closed directed loop. Loops also include the boundary of the original patch if it is intersected by trimming curves. These loops divide the resulting trimmed patch into distinct parts where the curves' directions determine which parts are visible. In other words, trimming procedures are used to define visible areas \(\mathcal{A}^{\mathrm{v}}\) over surfaces independent of the underlying parameter space.

As a result, surfaces with non-rectangular topologies can be represented in a very simple way. An example of a trimmed patch is shown in Fig. 11. It is emphasized that the mathematical description, i.e., the tensor product basis and the related control grid, of the original patch does not change and is never updated to reflect the trimmed boundary represented by the independent trimming curves. Trimmed surfaces should be considered as an 'engineering' extension of tensor product patches [83]. On the one hand, they permit a convenient way to define arbitrary surface topologies and provide a means for visually displaying them in graphics systems. On the other hand, they do not offer a canonical solution to related problems such as a smooth connection of two adjacent patches along a trimming curve, although the graphics system leads the user to incorrectly believe so. In fact, enormous effort has been and is still devoted to resolve the shortcomings of trimming procedures as discussed later on in Sect. 3.

### 2.8 Solid Models

Most CAGD objects are geometrically represented by their boundary only. In other words, these models consist of several boundary patches 𝛾 where \(\Gamma\) denotes the entire boundary of the object. If \(\Gamma\) is a curve, several patches may be needed to represent

$$
\begin{equation*} \Gamma=\bigcup_{i=1}^{I} \gamma_{i}, \tag{39} \end{equation*}
$$

- (a) Regular B-spline patch

distinct sections with different polynomial degrees. This is not a critical issue since curves can be joined rather easily, even with a certain continuity. However, a problem arises as soon as surfaces are considered, because tensor

- (a) Visualization and topological entities

- (b) Components

![Figure 12 Different perspectives of a CAGD solid model](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-12-p010.png)

*Figure 12 Different perspectives of a CAGD solid model: a visible part of the object and its topological entities (to be precise, the related geometric objects, i.e., points, curves, and surfaces, are displayed), b the geometric segments of the B-Rep and c the underlying mathematical parameterization of each surface. In c, dashed lines mark the boundary of the visible area and gray lines indicate the underlying tensor product basis. Note that the parameterization along common edges does not match*

- (c) Parameterization

product surfaces are four-sided by definition. A single regular NURBS surface may be closed equivalently to a cylinder or a torus. Spherical objects may be represented as well, if degenerated edges are introduced. Yet, more complicated objects such as a double torus require a partition into multiple NURBS patches. The connection of two adjacent surfaces is complicated, especially if a certain continuity is desired. In general, non-conforming parameterizations along surface boundaries need to be expected.

In addition to the geometric representation of the boundary patches, the topology of the object has to be described. It addresses the connectivity of the various components, and the corresponding entities are termed

- -vertices relating to points,

- -edges relating to curves,

## 3 Trimming in Computer Aided Geometric Design

There is a large body of literature on trimmed B-spline and NURBS geometries in CAGD. Trimming is addressed in the context of surface intersection, the development for appropriate data structures for solid modeling, the visualization of objects which is referred to as rendering, and remodeling approaches. The following outline of these topics is meant to be comprehensive, but it is by no means complete. Further, some auxiliary techniques are presented.

The motivation for this section is twofold: First of all, it provides an overview of the historical development of trimming approaches in the field of CAGD. Apart from being interesting in its own right, this insight exposes a number of general challenges, techniques, and ideas regarding trimmed geometries. Hence, it is hoped that the subsequent sections also give insight to further strategies dealing with trimming in the context of isogeometric analysis.

### 3.1 Surface Intersection

Trimming is closely related to the problem of surface-tosurface intersection. In general, the intersection of two parametric surfaces

![Figure 13 Cubic curves with different genus. Note the double point in case of the genus 0 curve](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-13-p011.png)

*Figure 13 Cubic curves with different genus. Note the double point in case of the genus 0 curve: Cubic curves with different genus. Note the double point in case of the genus 0 curve*

$$
\begin{align*} & \boldsymbol{S}_{1}(u, v)=\left(x_{1}(u, v), y_{1}(u, v), z_{1}(u, v)\right), \tag{40}\\ & \boldsymbol{S}_{2}(s, t)=\left(x_{2}(s, t), y_{2}(s, t), z_{2}(s, t)\right), \tag{41} \end{align*}
$$

leads to a system of three nonlinear equations, i.e., the three coordinate differences of \(\boldsymbol{S}_{1}\) and \(\boldsymbol{S}_{2}\), with four unknowns \(u, v, s, t\) [62]. If surfaces intersect, the solution usually yields curves, but also subsurfaces or points may occur. The computation of intersections is one of many "geomet ric interrogation" techniques, or processes, employed in all types of modeling. The development of a good surface intersection scheme is far from trivial since the method has to balance three contradictory goals: accuracy, efficiency, and robustness. The surveys [219, 220] and the text books [4, 130, 221] provide detailed information on various approaches. Surface intersection algorithms can be broadly classified into four main categories: (i) analytic methods, (ii) lattice evaluation, (iii) subdivision methods, and (iv) marching methods.

#### 3.1.1 Analytic Methods

The intersection of two surfaces may be solved analytically, i.e., an explicit representation of the intersection curve is obtained. Early solid modeling systems used analytic methods to obtain exact parametric representations of the intersection of quadratic surfaces [40]. The intersection problem always has a simple solution when both surfaces are given as functions in implicit form [130]. The good news is that parametric surfaces can always be represented implicitly [265], but the main problem is that the algebraic complexity of the intersection increases rapidly with the degree of the surfaces. This is often illustrated by a popular example of the intersection of two bicubic patches which has an algebraic degree of 324 as shown by Sederberg [265, 266]. In addition, the intersection of two bicubic patches has a

![Figure 14 Intersection points based on line-to-surface computations](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-14-p011.png)

*Figure 14 Intersection points based on line-to-surface computations: intersection points based on line-to-surface computations*

genus \({ }^{2}\) of 433 and only curves of genus 0, i.e., all degree two curves, cubic curves with one double point, quartic curves with three double points or one triple point, etc., can be expressed parametrically using rational polynomi als [152]. Figure 13 illustrates two examples of implicit cubic curves with different genus. The complexity of sur face intersection curves has also been discussed in the study of Farouki and Hinds [88]. It is argued that the deri vation of an implicit representation is not practical and an approximation scheme may be preferred. In general, ana lytic methods have been restricted to low degree intersections, which yield exact results very fast.

#### 3.1.2 Lattice Evaluation

The basic idea of this technique is to reduce the dimensionality of surface intersections by computing intersections of a number of isoparametric curves [186, 250] (see Fig. 14). Once the discrete intersection points are obtained, they are sorted and connected by an interpolation scheme. In order to define an intersection curve, lattice evaluation involves an initial choice of a proper grid resolution. This is crucial for both the robustness and efficiency of the method. Unfortunately, determination of an appropriate discrete step size is not straightforward and, if too coarse, may lead to a failure in identifying critical features [170]. curve intersection schemes are also useful in the context of ray tracing for visualization and point classification in solid modeling [220]. In these applications a patch is intersected by a straight line, as discussed later on in Sects. 3.3.2 and 3.5.2.

2 The genus g of a plane algebraic curve is specified by the degree p of the curve and the number I and multiplicity m of its singular points: g = 1 2 (\(p_{2}\)-3 p + 2 -∑ \(I_{i}=1\) mi (mi-1) ).

![Figure 15 Determination of an intersection region of two curves by means of a divide-and-conquer scheme that uses axis-aligned bound- ing boxes](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-15-p012.png)

*Figure 15 Determination of an intersection region of two curves by means of a divide-and-conquer scheme that uses axis-aligned bound- ing boxes: Determination of an intersection region of two curves by means of a divide-and-conquer scheme that uses axis-aligned bounding boxes*

#### 3.1.3 Subdivision Methods

The key idea of subdivision approaches is to compute an intersection using approximations of the patches involved, rather than the actual objects themselves. These approximations are often defined by piecewise linear elements. Consequently, the intersection problem is subdivided into many, but significantly simpler, problems. The final intersection curve is obtained by merging the individual intersection results.

A good approximation of the original objects is of course essential for the accuracy of such techniques. However, subdivision algorithms become inefficient for high-precision evaluation, especially if the decomposition is performed uniformly. A considerable improvement can be achieved if the region of the intersection, i.e., the affected elements, is estimated in a preprocessing step. This can be carried out by bounding boxes that completely enclose the corresponding element. Various construction schemes of such bounding boxes are outlined in Sect. 3.5.1. Their common aim is to allow an efficient determination if two objects are clearly separated or not. In particular, elements are recursively refined if their bounding boxes overlap, which leads to a non-uniform, adaptive subdivision algorithm as shown in Fig. 15. This process of successive refinement and removing of separable boxes is referred to as a divide-and-conquer principle [130].

An important advantage of subdivision methods is that they do not require starting points. On the other hand, the drawbacks can be summarized according to Patrikalakis and Maekawa [221] as follows: (i) they are only able to isolate zero-dimensional solutions, (ii) there is no certainty that each root has been extracted, (iii) the number of roots in the remaining subdomains is typically not provided, and (iv) there is no explicit information about root multiplicities without additional computations. Last but not least, (v) the method is not efficient in case of high-precision or higher order evaluations [181, 219].

#### 3.1.4 Marching Methods

Marching methods \({ }^{3}\) derive an intersection curve by step ping piecewise along the curve, e.g., [14, 20, 84]. Such methods usually consist of a search, a marching, and a sorting phase. The first phase detects an appropriate start ing point on the intersecting curve. Often, this is performed by a subdivision or lattice approach. In the marching phase, a point sequence along the intersection curve is developed starting from the points determined in the previous phase. The direction and the length of the next step are defined by the local differential geometry. Finally, the individual points and segments of the intersection curve are sorted and merged to disjoint pieces and curve loops.

According to Hoschek and Lasser [130], all marching methods share some common problems: (i) determination of good starting points, (ii) detection of all branches of the intersecting curve, (iii) avoiding of multiple detections of a intersection segment, (iv) correct behavior at self-intersections and singularities, (v) proper choice of the direction and length of the subsequent step, and (vi) a robust automatic stopping criterion.

Despite all these issues, marching methods are by far the most widely used approaches due to their generality and ease of implementation [170]. In addition, accuracy improvement can be easily achieved by decreasing the step size, and they are also very efficient, especially in combination with subdivision methods.

At this point, it should be emphasized that the problems related to topology detection of the intersection curve, i.e., finding all its branches and singular points, apply to all intersection methods and several authors have addressed them, e.g., [6, 105, 168, 222, 267, 283].

#### 3.1.5 Hybrid Methods

Every intersection method type has its benefits and drawbacks, hence a number of authors have established hybrid methods that combine features of the different categories.

One of the elementary surface intersection schemes has been proposed by Houghton et al. [133]. The algorithm combines a divide-and-conquer approach with a Newton-Raphson procedure: firstly, the surface is subdivided into flat sub-pieces. Then, each sub-piece is approximated by two triangles and the intersection of these triangles is computed. In the next step, the resulting linear segments are sorted and connected using the information provided by the subdivision tree. Finally, the intersection points are refined by the Newton-Raphson scheme. The main advantage of this method is that it is very general and can be

3 Marching methods are also referred to as tracing methods.

applied to any surface representation, in contrast to earlier techniques that utilize properties of certain surface types, e.g., [46, 111, 165, 180, 224, 256].

Barnhill et al. [19] presented another general procedure to compute the intersection of two rectangular \(C^{1}\) patches. It relies on a combination of subdivision and a marching scheme. It does not assume a special structure of the inter secting surfaces and special cases are considered, e.g., infi finite plane intersections, creases, and self-intersection. The algorithm has been enhanced in [20], including the uti lization of the divide-and-conquer concept presented by Houghton et al. [133].

Another combination of a divide-and-conquer subdivision with an iterative marching approach has been developed by Kriezis et al. [169]. The method enables intersecting algebraic surfaces of any degree with rational biquadratic and bicubic patches.

Krishnan and Manocha [170] developed an approach for NURBS surfaces that combines marching methods with the algebraic formulation. The starting points on the intersection curve are computed by Bézier curve-surface intersections that are obtained by eigenvalue computations. Moreover, they introduced a technique that allows detection of singularities during the tracing process.

#### 3.1.6 Representation of the Intersection Curve

Various techniques for the computation of approximate solutions to the surface-to-surface intersection problem have been outlined so far. It remains to discuss the actual representation of the result.

In general, three distinct representations of an intersection are obtained. On the one hand, the intersection curve in model space is computed. This may seem to be the main objective of the whole procedure at first glance, yet it is just a part of the overall solution process. The intersection curve has to be represented in each parameter space of the trimmed patches. These curves are referred to as trimming curves in the following and are needed to determine which surface points are visible. intersection and trimming curves can be defined by any kind of representation, but usually low-degree B-splines are used. They are constructed based on a set of sampling points that result from the surface-to-surface intersection algorithm applied [207]. Subsequently, an interpola tion scheme or another curve-fitting technique is used to generate a continuous approximation of the intersection in model space \(\hat{\boldsymbol{C}}\). In general, this curve does not lie on either of the intersecting surfaces. A trimming curve \(\boldsymbol{C}^{t}\) is obtained based on the sampling points given in the corre sponding parameter space [240]. The related curve \(\tilde{\boldsymbol{C}}^{t}\) in the model space is obtained by evaluating the equation of the surface \(\boldsymbol{S}\) along its \(\boldsymbol{C}^{t}\). Alternatively, \(\tilde{\boldsymbol{C}}^{t}\) may be represented

It is emphasized that \(\tilde{\boldsymbol{C}}^{t}\) does not coincide with the intersection curve in model space \(\hat{\boldsymbol{C}}\), regardless of its representation. In addition, all procedures related to trimming curves are performed for each patch separately. Hence, the images of these curves \(\tilde{\boldsymbol{C}}_{i}^{t}\) do not coincide, neither with each other, nor with \(\hat{\boldsymbol{C}}\). As a consequence, gaps and overlaps may occur between intersecting patches. There is no connec tion between these three representations of the intersection; although the sample points provide some information dur ing the construction, this data is only stored temporarily during the approximation procedure and never retained in memory for further use. These various approximations of a surface-to-surface intersection are summarized in Fig. 16.

Currently, the most common geometric modeling kernels are ACIS, C3D, and Parasolid. They provide software components for the representation and manipulation of objects, and form the geometric core of many CAD applications. All of them use splines for the description of trimming curves [43, 65, 282]. Yet, the representation of the intersection curve in model space varies: ACIS defines it by a three-dimensional B-spline curve, Parasolid uses a set of sorted intersection points that can be interpreted as a linear approximation, and in C3D the intersection curve is not stored at all. In C3D, trimming curves are computed such that they have the same radius and derivatives at the same parametric values. However, this is only satisfied at the intersection point used for the construction, for more details see [102].

4 A multi-affine and totally symmetric mapping is called a blossom (or polar form). Blossoms can be used to define spline algorithms in an elegant way. For details see [236].

![Figure 16 Independent curve interpolation of an ordered point set to obtain approximations of the intersection of two patches S 1 ( u , v ) and S 2 ( s , t ) . The set of sampling points depends on the surface-to-surface intersection algorithm applied. The subsequent interpolation of these points is performed in a the model space and the parameter space of b S 1 ( u , v ) and c S 2 ( s , t ) leading to the curves ̂ C , C t 1 , and C t 2 , respectively. The point data is usually discarded once the curves are constructed](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-16-p014.png)

*Figure 16 Independent curve interpolation of an ordered point set to obtain approximations of the intersection of two patches S 1 ( u , v ) and S 2 ( s , t ) . The set of sampling points depends on the surface-to-surface intersection algorithm applied. The subsequent interpolation of these points is performed in a the model space and the parameter space of b S 1 ( u , v ) and c S 2 ( s , t ) leading to the curves ̂ C , C t 1 , and C t 2 , respectively. The point data is usually discarded once the curves are constructed: Independent curve interpolation of an ordered point set to obtain approximations of the intersection of two patches S 1 (u, v) and S 2 (s, t). The set of sampling points depends on the surface-to-surface intersection algorithm applied. The subsequent interpolation of these points is performed in a the model space and the parameter space of b S 1 (u, v) and c S 2 (s, t) leading to the curves ̂ C, C t 1, and C t 2, respectively. The point data is usually discarded once the curves are constructed*

### 3.2 Solid Modeling

Solid modeling is concerned with the use of unambiguous representations of three-dimensional objects. It is based on

#### 3.2.1 Formulation of Trimmed Solid Models

It took some time to develop a rigorous way to represent trimmed free-form models. There are three broad catego ries for representing geometric objects: (i) decomposition, (ii) boundary, and (iii) constructive representations. Popu lar examples of decomposition representations are voxel models where a solid is approximated by identical cubic cells. Advantages and limitations of this approach are dis cussed in [153]. A B-Rep \({ }^{5}\) (B-Rep) defines an object by its bounded geometry, along with an associated topologi cal structure of corresponding entities, such as faces, edges, and vertices. The benefits of storing an object's shape by means of its boundary were already elaborated in the seminal work of Braid [36]. Most B-Reps consist of sev eral surface patches and additional information is stored to efficiently identify the various components and their rela tion to each other [241]. Various data structures for B-Reps have been used, e.g., [21, 73, 106], to find a compromise between storage requirements and response to topological questions. The best known constructive representation is so-called constructive solid geometry (CSG) [241]. Simple

5 B-Rep models with free-form surfaces are also referred to as sculptured models.

![Figure 18 Representation of the object shown in Figure 12 a by means of a CSG tree](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-18-p015.png)

*Figure 18 Representation of the object shown in Figure 12 a by means of a CSG tree: the object is specified by a composition of simple solids using Boolean operations, i.e., union (U) and difference (−)*

![Figure 17 An early sketch of a trimmed surface (reprinted from [ 29 ], with permission from Elsevier)](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-17-p015.png)

*Figure 17 An early sketch of a trimmed surface (reprinted from [ 29 ], with permission from Elsevier): An early sketch of a trimmed surface (reprinted from [29], with permission from Elsevier)*

primitives are combined by means of rigid motions and regularized Boolean operations-union, intersection, and difference. The resulting object is represented by a binary tree where the internal nodes correspond to the Boolean operations and the primitive solids (or half spaces) are given in the leaves. An example of such a tree is given in Fig. 18.

Remark 2 The developments of isogeometric analysis and additive manufacturing using heterogeneous materials yield to a growing interest in another representation of threedimensional geometric models, namely volumetric representations (V-Reps). As a matter of fact, several researchers in the CAGD community have started addressing this issue, see e.g., [31, 197, 321], including the definition of trimmed V-Reps [203].

Trimmed solid models combine concepts of B-Rep and constructive representation, i.e., they consist of free-form

- (i) Determination of the topological descriptions,

- (ii) Determination of the geometric surface descriptions,

- (iii) Guarantee that the geometry corresponds unambiguously to the topology.

Setting up a topology requires the classification of the neighborhood of various entities (faces, edges, and vertices) involved in the intersections [120]. The correlation of topology and geometry becomes particularly complicated if intersection curves have singularities or self-intersections. In addition, various forms of set membership classification, i.e., the determination if parts are inside, outside, or on the boundary of a domain, are used to compute B-Reps through Boolean operations. In order to determine if a surface point is inside or outside of the surface, the trimming curve must be defined in the parameter space as noted before. If the trimming curve would only be defined in the model space, the problem would be in fact ill-defined [205].

The first formulation of a trimmed patch representation that supports Boolean operations and free-form geometry was presented in the late 1980s by Casale and Bobrow [47, 49]. The domain of trimmed patches is specified by the two-dimensional equivalent of a CSG tree. Hence, a B-Rep is obtained that contains topology information of its trimmed components. Patches are intersected similar to the divide-and-conquer procedure of [133], but the trimming curve is then also transformed into the parameter space in order to perform Boolean operations and set membership classifications. At the same time, a rigorous trimmed surface definition has been formulated by Farouki [85]. The formulation is based on Boolean operation definitions. In particular, a trimmed patch is given by its parametric and implicit surface equations together with a trimming boundary that is defined as a tree structure of non-intersecting and nested piecewise-algebraic loops. These loops consist of monotonic branches. The integral over the trimmed surface is determined by a proper tessellation of the patch. It should, however, be pointed out that all these approaches fail to guarantee exact topological consistency since the images of the trimming curves do not match in general, as noted by Farouki et al. [87]. This leads to gaps and overlaps of the solid model, which can introduce failure of downstream applications such as numerical simulations.

#### 3.2.2 Robustness Issues

Several robustness issues arise in case of imprecise geometric operations. As a matter of fact, the numerical output from simple geometric operations can already be quite inaccurate. Complications may occur even for linear elements as discussed by Hoffmann [120-123] or the computation of the convex hull of a set of points [16], for instance. These problems are induced by propagation of numerical conversion, roundoff, and digit-cancellation errors of floating point representation. The issue of rounding errors of numerical computations is known for a long time, at least since an early study by Forsythe [92]. Investigating the effects of floating point arithmetic on intersection algorithms is an important area of research [220]. Since intersection problems can be expressed as a nonlinear polynomial system of equations, the robustness issue maybe addressed from a computational point of view. Troubles arise if the problem is ill-conditioned which is for example the case for tangential intersections and surface overlaps [135, 195].

The key issue is that numerical errors may cause misjudgment as pointed out in [291]. Since the geometrical decisions are based on approximate data and arithmetic operations of limited precision, there is an interval of uncertainty in which the numerical data cannot yield further information [122]. Of course, the situation gets even

![Figure 19 Example of an incorrect topology](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-19-p016.png)

*Figure 19 Example of an incorrect topology: a two intersection points x i are close together which may lead to b an incorrect topological placement along the vertical line due to numerical approximation errors (re-execution of the original example [204])*

more delicate if trimmed free-form surfaces are involved where approximation errors are quite apparent due to the gaps and overlaps between intersecting patches. In case of topological decisions, the accumulation of approximation errors is especially crucial since inaccuracy leads to inconsistency of the output as indicated in Fig. 19.

There is a large amount of research that addresses the issue of accurate and robust solid modeling. The various concepts are outlined in the following subsections. The approaches are based on tolerances, interval arithmetic, and exact arithmetic.

3.2.2.1 Tolerances Often, tolerances are used to assess the quality of operations like the computation of an intersection [19, 130]. Several authors have suggested to use adaptive tolerances where each element of the model is associated with its own tolerance, e.g., [143, 271]. In addi tion, tolerances may be dynamically updated [82]. Robust ness of topology decisions may be improved by choosing the related precision higher than the one for the input data [291]. Another strategy is to adjust the data in order to obtain topologically consistent functions [204]. There are various other approaches that improve the application of tolerance and the interested reader is referred to the review of Hong and Chang [128] for a comprehensive discussion. In fact, all common CAD software tools are based on a user-defined tolerance that determines the accuracy of the geometrical operations performed. For example, the default tolerance values of ACIS are \(10^{-6}\) for the comparison of points and \(10^{-3}\) for the difference of an approximate curve or surface to its exact counterpart [65]. Unfortunately, tolerances cannot guarantee robust algorithms since they do not deal with the inherent problem of limited-precision arithmetic.

![Figure 20 Four splines representing a quadrilateral](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-20-p017.png)

*Figure 20 Four splines representing a quadrilateral: a ideal mathematical object, b floating point model with approximation errors, and c interval arithmetic based representation*

##### 3.2.2.2 Interval Arithmetic

In case of interval arithmetic, e.g., [76, 208], numerical errors are taken into account by associating an interval of possible values to a variable. This approach is correct in the sense that result intervals are guaranteed to contain the real number that is the value of the expression. The interval size indicates the reliability of floating point computations. In particular, a narrow interval is obtained in case of a successful operation whereas a wide interval reveals a risk [117]. This concept may be modified to rounded intervals to assure that the computed endpoints always contain the exact interval, see e.g., [3, 57, 193]. Interval arithmetic may also be combined with backward error analysis [255].

In the context of solid modeling, Hu et al. [134-136] suggested to use interval NURBS, i.e., NURBS patches with interval arithmetic. The control points are described by interval numbers rather than real numbers. Consequently, they are replaced by control boxes and thus, curves and surfaces are represented by slender tubes and thin shells, respectively. A conceptional sketch is illustrated in Fig. 20. The object is defined by a graph with nodes representing the topological entities. Each node has two lists: one for higher dimensional nodes and another for lower dimensional nodes that are arranged in counterclockwise order. This data structure has been applied to Boolean operations [136] and various intersection problems including ill-conditioned cases [134]. Gaps between actual intersecting objects are avoided and no intersection point is missed. However, objects that do not intersect each other originally, may do after several geometric processing steps using rounded interval arithmetic. Furthermore, interval arithmetic approaches cannot achieve very high precision in reasonable computation time [220].

##### 3.2.2.3 Exact Arithmetic

In order to achieve robustness, algorithms have been developed that are based on exact arithmetic, which is the standard in symbolic computation [318]. Most of these approaches focus on polyhedral objects, see e.g., [26, 93, 291]. For linear geometries like planes and their intersections, exact rational arithmetic is enough to handle all necessary numbers. However, more involved objects rely on real algebraic numbers and therefore, they require more complicated data structures and algorithms. Keyser et al. [157-159] presented such a scheme for curveto-curve intersection in a plane and the theoretical framework for exact computation based on algebraic numbers has been discussed by Yap [318]. A combination of exact approach and floating point calculation may also be used as suggested by Hoffmann et al. [123]. In their paper, symbolic reasoning is used when floating point calculation yields ambiguous results. Krishnan et al. [171] demonstrated that exact arithmetic can be applied to large industrial models. They presented a B-Rep modeling system dealing with models using over 50,000 trimmed Bézier patches.

Still, the main drawback of such approaches is their efficiency. Exact computation can be several orders of magnitude slower than a corresponding floating point implementation [156]. According to Patrikalakis and Maekawa [220], much research remains to be done in bringing such methods to practice. In particular, more efficient algorithms should be explored that are generally applicable in low and high degree problems.

3.2.2.4 Concluding Remarks Overall, the formulation of robust solid models with trimmed patches is still an open issue. Tolerance based approaches are usually preferred since they are faster than the more precise ones. Hence, there is again a tradeoff between efficiency, accuracy, and robustness as discussed in the context of intersection schemes. Of course, the importance of these properties to the object representation strategy depends on the application context [45].

In fact, the problem of topologically correct merging of trimmed surfaces is such a challenge that more recent research in CAGD tries to circumvent this issue by employing other surface descriptions like T-splines and subdivision surfaces. These representations inherently possess a consistent topology and corresponding models are watertight, i.e., they do not have unwanted gaps or holes. However, they also have some drawbacks and the transformation of the original object usually leads to approximations, at least in the vicinity of the intersection curve as discussed later on in Sect. 3.4.

### 3.3 Rendering

In computer graphics rendering refers to the process of generating images of a CAGD model. There are two different ways to approach this goal. On the one hand, indirect schemes first tessellate the surfaces of the object and the actual visualization is based on this render-mesh. On the other hand, rendering may be performed directly on freeform surfaces by ray tracing. For a general introduction to the creation of realistic images, the interested reader is referred to the textbook of Glassner [99].

#### 3.3.1 Tessellation

All commercial rendering systems tessellate free-form surfaces before rendering, because it is more efficient to optimize the code for a single type of primitive [27].

Early on, trimmed surfaces had been rendered using the de Boor [33], Oslo [60], or Boehm's knot insertion [32] algorithm. In addition to the subdivision, the regions must be sorted to find out which ones are hidden and have to be removed for rendering, see e.g., [52, 179, 292]. In general, subdivision approaches are expensive if they are performed to pixel level.

The rendering of trimmed NURBS surfaces can also be carried out using a combination of subdivision and adaptive forward differencing [185, 275]. This method allows fast sampling of a large number of points, but suffers from error propagation. The main drawback in rendering transparent objects is the redundant pixel painting in adaptive forward differencing. Furthermore, the overall performance of the algorithm obtained is rather slow [191].

$$
\begin{equation*} \sup _{(u, v) \in T}\|\boldsymbol{S}(u, v)-\boldsymbol{T}(u, v)\| \leq \frac{2}{9} \lambda^{2}\left(M_{1}+2 M_{2}+M_{3}\right) \tag{42} \end{equation*}
$$

Rockwood et al. [249] presented a scheme enabling rendering of trimmed surfaces in real-time. Firstly, the surface is tessellated, i.e., approximated by linear triangles or other polygons. Therefore, all surfaces are subdivided into individual Bézier patches. A trimmed Bézier patch may be subdivided further to obtain monotone regions that have convex boundaries in the parameter space [165]. Each patch is tessellated into a grid of rectangles which are connected to the region boundaries by triangles. The actual rendering is performed on the approximate mesh. This idea has been adapted and enhanced by several other authors, e.g., [2, 176, 191].

176, 191]. The triangulation of trimmed surfaces by a restricted Delaunay triangulation has been proposed by Sheng and Hirsch [279]. The basic idea of this technique is to compute the approximation mesh in the parameter space. Although it has been developed for stereolithography \({ }^{6}\) applications, the suitability for rendering is emphasized. Stereolithography was also the motivation in [74] where trimmed surfaces are triangulated by an adaptive subdivision scheme. In contrast to the approach by Rockwood et al. [249], both algorithms contain strategies to avoid cracks between patches. A gen eral discussion on how to avoid edge gaps in case of an adaptive subdivision is given by Dehaemer and Zyda [69].

According to Vigo and Brunet [300], the main drawback of the approaches previously mentioned [249, 279] is that

6 Stereolithography is an early and widely used 3D printing technique.

the resulting elements may be odd-shaped, especially near the boundary. They suggested to overcome this issues by a piecewise linear approximation of trimmed surfaces using a triangular mesh that is based on a max-min angle criterion. The algorithm is designed so that the resulting mesh can be used for stereolithography, FEA, and rendering. The mesh obtained consists of shape-regular elements and has no cracks between patches.

The determination of a proper step size of a tessellation is of course an important issue. The elements should not be too small in order to avoid oversampling of the surface, nor too big, since this would decrease the quality of the ren dering [1]. Lane and Carpenter [178] presented a formula for calculating the upper bound of the distance between a right triangle interpolating a surface. Later, the bound was improved by Filip et al. [89]. Based on this work, Sheng and Hirsch [279] derived the following formula for arbi trary triangles: the approximation error can be estimated by the difference of a parametric surface \(\boldsymbol{S}(u, v)\) to a linear triangle \(\boldsymbol{T}(u, v)\) where \(T\) is the correspond region in the parameter space, \(\lambda\) denotes the maximal edge length of \(\boldsymbol{T}(u, v)\), and \(M_{i}\) are specified by

$$
\begin{equation*} M_{1}=\sup _{(u, v) \in T}\left\|\frac{\partial^{2} \boldsymbol{S}(u, v)}{\partial^{2} u}\right\|, \tag{43} \end{equation*}
$$

$$
\begin{equation*} M_{2}=\sup _{(u, v) \in T}\left\|\frac{\partial^{2} \boldsymbol{S}(u, v)}{\partial u \partial v}\right\|, \tag{44} \end{equation*}
$$

$$
\begin{equation*} M_{3}=\sup _{(u, v) \in T}\left\|\frac{\partial^{2} \boldsymbol{S}(u, v)}{\partial^{2} v}\right\| \tag{45} \end{equation*}
$$

Hence, the upper bounds of second derivatives of the sur face are required. Once these bounds are determined, \(\lambda\) can be computed for a given tolerance \(\varepsilon\) by

$$
\begin{equation*} \lambda=3\left(\frac{\varepsilon}{2\left(M_{1}+2 M_{2}+M_{3}\right)}\right)^{1 / 2} \tag{46} \end{equation*}
$$

The bounds on the second derivatives for a B-spline surface (43)-(45) can be computed by constrained optimization [89] or conversion to a Chebyshev basis [279]. Piegl and Richard [229] use the fact that the derivative of a B-spline is again a B-spline to define the upper approximation bounds by computing the maxima of the control points of the differentiated surfaces. They address the treatment

![Figure 21 Rays spawned from an eye-point in order to get a pixel-wise image of an object](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-21-p019.png)

*Figure 21 Rays spawned from an eye-point in order to get a pixel-wise image of an object: Rays spawned from an eye-point in order to get a pixel-wise image of an object*

of rational surfaces by means of homogeneous coordinates and adjustment of the tolerance due to the perspective mapping (12).

A few years later, Piegl and Tiller [231] proposed a tri angulation scheme which is geometry-based, i.e., the pro cedure is based on the geometry rather than the param eterization. The trimming curves are polygonized in the model space by cubic Bézier curves and the surface itself is subdivided by its control net. The main advantage of this approach is that the trimmed NURBS surface is not required to have more than \(C^{0}\)-continuity, in contrast to the previous methods that assumed that the surfaces are \(C^{2}\)-continuous in order to estimate a step length in the parameter space [89]. Elber [79] proposed two alternative approaches that are also independent of the parameteriza tion: one based on an intermediate linear surface fit and another based on global normal curvature. In general, tes sellations do not require an element connectivity or shape regular elements. However, several authors have presented the construction of conforming meshes for trimmed patches that yield triangles with good aspect ratios [55,57,58].

Irregular meshes are also an issue regarding hardware implementation on the graphical processing unit (GPU). Moreton [206] presented tessellation of polynomial surfaces for hardware rendering using forward differences and dividing the work of tessellation between CPU and GPU. To avoid gaps along shared boundaries of patches due to the different floating point engines, all boundary curves of the patches are calculated on the GPU. In order to enable GPU based tessellation, Guthe et al. [108] presented a trim texture scheme which can be parallelized. In this approach, the visible domain is specified based on a texture-map of black and white pixels, hence the trimming task is performed on pixel-level.

#### 3.3.2 Ray Tracing

In contrast to tessellation, ray tracing tries to compute an image one pixel at a time [76]. Every object in a scene is tested if it intersects with rays spawned from an eye-point as indicated in Fig. 21. The result must return at least the closest intersection point and the corresponding normal of the surface for each ray. Hence, the heart of any ray tracing package is the set of ray intersection routines [99].

Ray tracing is a powerful, yet simple approach to image generation [144]. Already early attempts of this technique have been successfully applied for automatic shading of objects [8], modeling of global lightning effects [311], and the visualization of fuzzy reflections and blurred phenomena [64]. In the context of parametric surfaces, the pioneering works focus on different ray-surface intersection methods [144, 146, 297]. Various intersection algorithms have been developed. One of the first algorithms used a lattice approach where the problem is reduced to finding the root of univariate polynomials [146]. Several numerical methods based on Newton schemes have been employed, e.g., [198, 293, 297]. Nishita et al. [214] introduced a ray tracing technique for trimmed patches based on Bézier clipping. This concept has been adapted and enhanced by a large number of researchers, e.g., [44, 78, 97, 217, 303]. Bézier clipping is discussed in more detail in Sect. 3.5.2.

Ray tracing of trimmed patches has also been addressed. Usually, the untrimmed surface is intersected first and the determination if the intersection point lies inside or outside of the trimmed domain is performed in a subsequent step. This point classification task can be employed by raytests, e.g., [198, 214, 261]. The regions that require trimming may be identified in a preprocessing step in order to improve the performance [97]. Section 3.5.2 provides more information on the ray-test concept. An alternative way of point classification is to generate a trim texture that returns whether a point is inside or not [108]. This approach is very efficient since it requires only a single texture look-up to classify a domain point. However, the trim texture has to be updated every time the view changes [313].

One of the greatest challenges of ray tracing is efficient execution [99]. Hence, many researchers have focused on this issue. Early attempts improved the performance by means of bounding box trees, e.g., [198, 316]. Havran [116] compared a number of such schemes and concluded that the kd-tree is the best general-purpose acceleration structures for CPU. Kd-trees define a binary space partition that always employs axis-aligned splitting planes. Pharr et al. [226] have shown that coherence can be exploited to improve ray tracing. Their rendering algorithms improve locality of data storage and data reference. Further improvement can be obtained by simplifying and streamlining the basic algorithms in order to exploit performance features of

### 3.4 Remodeling of Trimmed Models

Solid models with trimmed surfaces suffer from robustness issues that may lead to inconsistencies as previously discussed in Sect. 3.2.2. In order to obtain an unambiguous and watertight description of a solid model, several authors considered replacing trimmed objects by other surface representations. In particular, it has been suggested to remodel trimmed surfaces by means of a set of regular patches, subdivision surfaces, or T-splines.

#### 3.4.1 Regular Patches

The treatment of trimmed surfaces in the early automotive industry was discussed by Sarraga and Waters [257], in which a repatching method is proposed. To be precise, the intersection curves are used as edges of new regular patches approximating the original surface. As pointed out by Sarraga and Waters, repatching has several distinct disadvantages for modeling, but it is applied as a compromise between the complexity of free-form surfaces and the requirements of solid modeling. The common aim of the subsequent approaches is to improve this compromise. Besides the desire for an unambiguous and robust solid model, exchange of geometric data between dissimilar CAD software has been a motivation for this remodeling concept. Various constructions for the repatching procedure have been proposed. Hoschek and Schneider [131] convert trimmed rational Bézier patches into a set of bicubic and biquintic Bézier patches. The segmentation is based on arguments related to the curvature of the surface and conditions on the geometrical continuity. The procedure combines some of Hoschek's previous works, i.e., [129, 132], and consists of four steps: (i) determination of new geometrically oriented boundary curves, (ii) approximation of these curves, (iii) fitting of the interior of each patch using geometric continuity conditions for the boundary and corner points, and (iv) approximation of the intersection curves of trimmed surfaces. The use of ruled surfaces [110], Coons patches [41, 301], and Clough-Tocher

![Figure 22 Generalized Voronoi diagram for five trimming curves (re- execution of the original figure of [ 110 ])](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-22-p020.png)

*Figure 22 Generalized Voronoi diagram for five trimming curves (re- execution of the original figure of [ 110 ]): Generalized Voronoi diagram for five trimming curves (reexecution of the original figure of [110])*

splines \({ }^{7}\) [167] have also been suggested to remodel trimmed surfaces. Another concept is based on clipping isoparamet ric curves of a B-spline surface [9]. Later, this approach has been adapted for the design of aircraft fuselages and wings Generalized Voronoi diagrams may be used to obtain a proper decomposition of the trimmed domain with multiple trimming curves [110, 142]. Thereby, the parameter space is partitioned into convex polygons such that each polygon contains exactly one trimming curve as illustrated in Fig. 22. Details on Voronoi diagrams can be found in the survey of Aurenhammer [10].

Another strategy to remodel trimmed models is local perturbation. In contrast to repatching, the control points of the original surfaces are modified in order to obtain an unambiguous configurations along the intersection curves. Hu and Sun [137] proposed to close gaps between trimmed B-spline surface by an algorithm that moves one of the patches towards the trimming curve defined by the other one. This approach modifies the control point of the patch near the trimming curve using singular value decomposition. It can be used to improve the accuracy of small gaps, but yields bad-shaped surfaces if the gaps are too large. Moreover, this approach does not produce an exact topological consistency. Song et al. [285] defines the differences of corresponding trimming curves by means of a so-called error curve in model space. It is specified so that its coefficients depend linearly upon the control points of the intersecting surfaces. The perturbation is carried out by setting all coefficients of this curve to zero. This is found by solving a linear system of equations and results in an adaptation of the control points. A complement to this work was presented by Farouki et al. [87]. They propose

7 Clough-Tocher is a splitting scheme to construct \(C^{1}\)-continuous splines over triangulations.

![Figure 23 Chaikin’s corner-cutting algorithm](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-23-p021.png)

*Figure 23 Chaikin’s corner-cutting algorithm: construction of a quadratic B-spline curve by a subdivision of the control polygon*

to remodel trimmed surface by a hybrid collection of tensor product patches and triangular patches. In particular, they demonstrated the approximation of trimmed bicubic patches by quintic triangular patches such that the intersection curves are explicitly defined by one side of a triangular Bézier patch. The approach considers pairs of rectangular patches that intersect along a single diagonal arc. This can be achieved by a preprocessing step as described in the follow-up paper [115].

#### 3.4.2 Subdivision Surfaces

The basic concept of subdivision approaches goes back to the 1970s. Chaikin developed an elegant algorithm to draw a curve by cutting the corners of a linear polygon [54]. The basic steps of the procedure are shown in Fig. 23. Later, it was shown that this cutting algorithm converges to a quadratic B-spline curve and the initial polygon is equivalent to its control polygon [246]. This idea of sequential subdivision of a control polygon was generalized by Doo and Sabin [75] as well as Catmull and Clark [53] to compute bi-quadratic and bi-cubic B-spline surfaces, respectively. Since then, a vast number of different subdivision schemes emerged for various surface types, such as triangular splines [190] and NURBS patches [51], for instance. The final objects of subdivision schemes are referred to as limit curves or surfaces. The distinguishing feature of these approaches is that they can be applied to arbitrary control polygons which are not restricted to a regular grid structure. The smoothness between the resulting surfaces is controlled by the subdivision scheme.

![Figure 24 An example of a parameter space with T-junctions which are highlighted by circles](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-24-p021.png)

*Figure 24 An example of a parameter space with T-junctions which are highlighted by circles: An example of a parameter space with T-junctions which are highlighted by circles*

In 2001, the issue of Boolean operation for subdivision surfaces was addressed. Litke et al. [188] presented a trim operator, but do not address surface-to-surface intersections. An algorithm for approximate intersections was developed by Biermann et al. [30]. High accurate results can be achieved at additional computational expense. Both approaches employ subdivision based on triangular splines. Shen et al. [278] convert trimmed NURBS surfaces to untrimmed subdivision surfaces using Bézier edge conditions. The limit surface fits the original object to a specified tolerance. The resulting Catmull-Clark models are watertight and smooth along the intersection. Recently, Shen et al. [277] presented a generalization of the approach that converts B-Rep models of regular and trimmed bicubic NURBS patches to a single NURBS-compatible subdivision surface. During this process, a quadrilateral mesh topology is constructed in the parameter space of each patch and the corresponding control points are computed by solving a fitting problem. Finally, the individual parts are merged into a single subdivision mesh. In order to obtain gap-free joints, the preserved boundary curves in model space are used as target curves of the subdivision surface.

Subdivision models possess a greater flexibility due to their inherent topological consistence while conventional NURBS models have greater control of an objects shape. This attribute of subdivision attracted considerable attention, especially in the field of computer animation [70]. For a detailed discussion on subdivision schemes the interested reader is referred to the textbook [308].

#### 3.4.3 T-splines

T-splines were introduced by Sederberg et al. [270] in 2003. They are generalizations of B-splines that allow T-junctions in the parameter space and the control net of

![Figure 25 Various types of bounding boxes for the same curve. The orientation of the enclosing region is indicated by arrows](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-25-p022.png)

*Figure 25 Various types of bounding boxes for the same curve. The orientation of the enclosing region is indicated by arrows: Various types of bounding boxes for the same curve. The orientation of the enclosing region is indicated by arrows*

a surface as illustrated in Fig. 24. In a subsequent paper [268], the related ability of local refinement is used to close gaps between trimmed surfaces by converting them to a single watertight T-spline model. The resulting T-spline representation can be converted to a collection of NURBS surfaces again, without introducing an approximation error. On the other hand, conversion to the T-spline representation includes some perturbation in the vicinity of the intersection. It is argued that the approximation error can be made arbitrarily small, and the perturbation can be con fined to an arbitrarily narrow neighborhood of the trimming curve. The conversion is performed such that \(C^{2}\)-continuity is obtained between the intersecting surfaces. These papers are focused on cubic splines since they are the most impor tant ones in CAGD. However, the T-spline concept is not restricted to the cubic case.

### 3.5 Auxiliary Techniques

Techniques and strategies frequently used in the context of trimming are outlined in this section. They may be useful for researchers dealing with trimmed models in isogeometric analysis.

#### 3.5.1 Bounding Boxes

$$
\begin{equation*} d_{\min }=\min \left\{0, \frac{d_{1}}{2}\right\} \quad \text { and } \quad d_{\max }=\max \left\{0, \frac{d_{1}}{2}\right\}, \tag{47} \end{equation*}
$$

Bounding boxes are often applied to significantly accelerate geometrical computations. The basic idea is to use rough approximations of objects in order to get a fast indicator if two regions are well separated or not. Hence, involved operations have to be carried out only if necessary. These approximations may be refined adaptively as in divide-and-conquer based surface intersection approaches introduced in Sect. 3.1.3.

The simplest and perhaps most common approach is to embed objects into min-max boxes where the corner points of the object define an axis-parallel box. The axis aligned setting is not mandatory but allows the most efficient evaluation of the distance between two boxes [116]. Some authors suggest to use oriented bounding boxes to

![Figure 26 Construction of axis-parallel bounding boxes by a the end- points and b the control points of a spline](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-26-p022.png)

*Figure 26 Construction of axis-parallel bounding boxes by a the end- points and b the control points of a spline: Construction of axis-parallel bounding boxes by a the endpoints and b the control points of a spline*

improve the geometry approximation, e.g., [15, 20, 133]. In this case, the bounding box is rotated such that it is aligned with the connection of the corner points of the surface it encloses. An object can also be bounded by a combination of slaps, also known as fat lines, with different orientations [154]. Slaps denote regions between two parallel planes which are specified by their normal vector. This concept includes conventional bounding boxes, simply by using two orthogonal slaps. Figure 25 summarizes these various bounding box types.

Bounding boxes constructed by corner points do not guarantee the enclosing of the whole spline, especially if a spline is highly curved. The convex hull property of the control points can be used in order to get a proper approximation. Consequently, the area of the bounding box increases since it is computed based on the control polygon rather than the actual geometry, as illustrated in Fig. 26. Sederberg and Nishita [269] proposed an optimized bound for planar quadratic and cubic Bézier curves. They sug gested defining the bounding region by lines parallel to the connection \(\ell\) of the first and last control point. They are determined by the minimal and maximal distance \(d_{i}\) of the other control points \(\boldsymbol{c}_{i}\) perpendicular to \(\ell\). The tighter bound is determined in the quadratic case by while for the cubic splines it is with the scaling factor 𝛼 given by (49) d max = 𝛼 ⋅ max { 0, d 1, d 2,

$$
\begin{equation*} d_{\min }=\alpha \cdot \min \left\{0, d_{1}, d_{2}\right\}, \tag{48} \end{equation*}
$$

$$
\begin{equation*} d_{\max }=\alpha \cdot \max \left\{0, d_{1}, d_{2}\right\}, \tag{49} \end{equation*}
$$

$$
\alpha=\left\{\begin{array}{l} \frac{3}{4} \text { if } d_{1} d_{2}>0, \tag{50}\\ \frac{4}{9} \text { otherwise } . \end{array}\right.
$$

![Figure 27 Tighter bounds for bounding boxes for quadratic and cubic B-spline curves. The original bounding boxes are shown by dotted lines whereas dashed lines mark the improved ones](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-27-p023.png)

*Figure 27 Tighter bounds for bounding boxes for quadratic and cubic B-spline curves. The original bounding boxes are shown by dotted lines whereas dashed lines mark the improved ones: Tighter bounds for bounding boxes for quadratic and cubic B-spline curves. The original bounding boxes are shown by dotted lines whereas dashed lines mark the improved ones*

![Figure 28 Definition of axis-parallel bounding boxes based on mono- tonic regions. The white points mark the characteristic points consid- ered](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-28-p023.png)

*Figure 28 Definition of axis-parallel bounding boxes based on mono- tonic regions. The white points mark the characteristic points consid- ered: definition of axis-parallel bounding boxes based on monotonic regions. The white points mark the characteristic points considered*

are oriented according to the locations of the first and last control point.

Another way to assure that a curve lies within its bounding box is to subdivide it into monotonic regions. The essential idea is that if a domain of any continuously differentiable function \(f\) is subdivided at its characteris tic values, the range of \(f\) on each of the subintervals can be simply found by evaluating \(f\) at the endpoints of that subinterval [165, 208]. The set of characteristic points may include zeros of the first or second derivatives of \(f\), start and end points of open curves, and singular points such as cusps or self-intersections. Figure 28 shows an example of a B-spline curve that has been divided into monotonic regions and the corresponding bounding boxes. In order to detect these points, a preprocessing step is required. Despite this additional effort, monotonic regions have

![Figure 29 Classification of interior and exterior points by counting intersections of the trimming curve with a ray](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-29-p023.png)

*Figure 29 Classification of interior and exterior points by counting intersections of the trimming curve with a ray: Classification of interior and exterior points by counting intersections of the trimming curve with a ray*

been used in several application like intersecting planer curves [156, 157] and surfaces [84], tessellation of trimmed NURBS [249], and ray tracing [261].

#### 3.5.2 Point Classification

One of the most fundamental operations in the context of trimmed surfaces is the determination if a point \(\boldsymbol{x}\) of a patch is inside or outside the visible domain. This can be done by counting the number of intersections of a ray emanat ing from \(\boldsymbol{x}\) with the trimming curves and the boundary of the patch. If the number is odd \(\boldsymbol{x}\) is inside and otherwise it is outside of the visible area. The direction of the ray can be chosen arbitrary. This rule is based on the Jordan curve theorem, that is, every simple closed planar curve sepa rates the plane into a bounded interior and an unbounded exterior region [109]. Hence, the intersection is determined in the parameter space of the patch, in contrast to the ray tracing approach for rendering outlined in Sect. 3.3.2. Fur thermore, if a trimming curve is not closed, it is associated to the visible part of the patch boundary to obtain a closed loop as illustrated in Fig. 29. Another possibility is to con nect open trimming curves with the non-visible boundary of the patch and intersect only with the trimming curves. It should be noted that in the latter case, the even-odd rule turns upside down, i.e., \(\boldsymbol{x}\) is inside the visible domain if the number of intersections is even.

Despite its conceptional simplicity, the implementation of the corresponding algorithm is not trivial [77]. For example, ambiguous cases may occur like tangency between the ray and the curve. Nishita et al. [214] proposed the following procedure: the ray is chosen such that it intersects perpendicularly with the closest boundary of the patch. As a consequence, the parameter space is divided into four quadrants which meet at the origin of the ray as

![Figure 30 Specification of quadrants for the point classification proce- dure of Nishita et al. [ 214 ]](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-30-p024.png)

*Figure 30 Specification of quadrants for the point classification proce- dure of Nishita et al. [ 214 ]: Specification of quadrants for the point classification procedure of Nishita et al. [214]*

- (i) There are no intersections with the ray if all control points of the trimming curve are within the quadrants I and II, or II and III, or III and IV.

- (ii) All control points of a trimming curve are within the quadrants I and IV. The number of intersections is even if the endpoints of curve are in the same quadrant; otherwise it is odd.

Tangency between the ray and the trimming curve do not pose any problem for these exclusion criteria. However, it should be pointed out that an intersection may be counted twice if the ray goes through an endpoint which is shared by two trimming curves. For the other cases where the intersection has to be computed, Nishita et al. [214] suggested to employ Bézier clipping. This concept has been introduced by Sederberg and Nishita [269] in the context of curve-to-curve intersection and locating points of tangency between two planar Bézier curves. The basic idea is to use the convex hull property of Bézier curves to identify regions of the curves which do not include the solution. The bounding regions are defined by fat lines parallel and perpendicular to the line through the endpoints of the Bézier curve. By iteratively clipping away such regions, the algorithm converges to the solution at a quadratic rate and with a guarantee of robustness.

In particular, the ray is defined implicitly by

$$
\begin{equation*} a x+b y+c=0 \quad \text { with } \quad a^{2}+b^{2}=1 . \tag{51} \end{equation*}
$$

The coordinates are denoted by \(x\) and \(y\) in order to emphasize that this approach is applicable for any plane

![Figure 31 Bézier clipping](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-31-p024.png)

*Figure 31 Bézier clipping: a intersection of a ray 퓁 with a Bézier curve C (u) and b the corresponding non-parametric Bézier curve which is used to determine the parameter range [u max, u min] that contains the intersection of C (u) and 퓁*

coordinate system. The distance \(d(u)\) of a point on the Bézier curve \(\boldsymbol{C}(u)\) to the ray \(\ell\) is given by

$$
\begin{equation*} d(u)=\sum_{i=0}^{p} d_{i} B_{i, p} \quad \text { with } \quad d_{i}=a x_{i}+b y_{i}+c . \tag{52} \end{equation*}
$$

The coefficients \(d_{i}\) are the distances of the control points \(\boldsymbol{c}_{i}\) of the Bézier curve to the ray and \(B_{i, p}\) are Bernstein polyno mials of degree \(p\). Equation (52) can be represented as a non-parametric Bézier curve \(\tilde{\boldsymbol{C}}(u, d(u))\) where the values \(d_{i}\) are related to their corresponding Greville abscissae, The roots of \(\tilde{\boldsymbol{C}}(u, d(u))\) are equivalent to the paramet ric values \(u\) at which \(\ell\) intersects \(\boldsymbol{C}(u)\). Hence, the convex hull of \(\tilde{\boldsymbol{C}}(u, d(u))\) can be used to identify regions where the objects do not intersect. To be precise, the minimal and maximal parametric values, i.e., \(u_{\text {min }}\) and \(u_{\text {max }}\), of the intersections of the convex hull with the \(u\)-axis splits the parameter space into three regions of which only one, i.e., \(u_{\text {min }} \leqslant u \leqslant u_{\text {max }}\), has to be considered for the intersection with the ray. This region is extracted as a Bézier curve by means of knot insertion and the procedure is repeated until a certain tolerance is reached.

This technique can also be utilized to determine the intersection of two Bézier curves by iteratively clipping both objects [269]. Sherbrooke and Patrikalakis [280] developed a generalization of Bézier clipping that allows computing the roots of an n-dimensional system. The socalled Projected-Polyhedron method subdivides an object into Bézier segments and generates each side of its bounding boxes by projecting the control points onto different planes. Thus, only the convex hull of two-dimensional point sets has to be computed.

### 3.6 Summary and Discussion

The previous parts of this section shed light on various aspects of trimmed NURBS in the context of CAD. On the basis of the discussion of surface intersection in Sect. 3.1, it can be concluded that there is no canonical way to derive trimming curves, but a wide range of different techniques to address this problem. Further, an exact representation of an intersection of two patches is not feasible in most cases. In fact, several distinct curves are usually used to specify a single intersection: a curve in model space and trimming curves in the parameter spaces of all patches involved. These curves are independent approximations of the actual intersection and there is no connection between them. This missing link makes it very difficult to transfer information from a trimmed patch to an adjacent one.

The necessity of approximation yields gaps and overlaps between intersecting patches. As a result, robustness problems arise for solid modeling as outlined in Sect. 3.2. Considerable effort has been devoted to derive consistent trimmed models. Still, the problem is unresolved and the absence of truly robust representations poses a demanding challenge, especially for downstream applications. Even within the field of CAGD, the replacement of trimmed surfaces by other representations may be needed. Tessellations are used in the context of rendering, for instance. In this particular case, the main reason is efficiency as discussed in Sect. 3.3. However, all other remodeling approaches presented in Sect. 3.4 are motivated by the flaws of trimmed models and the limitation of tensor product patches due to their four-sided nature. It should be emphasized that these schemes may yield watertight models, but there are certain tradeoffs. First of all, approximations are introduced at least in the vicinity of trimming curves. The number of control variables increases particularly if regular tensor product patches are used for the remodeling. Subdivision surfaces and T-splines are promising techniques, but may induce new problems like extraordinary vertices 8 and linear dependence of the basis functions. In addition, they are designed for a specific surface type which may be an issue if a model consists of parts with different polynomial degree. Overall, it is apparent that there is no simple solution to the trimming problem.

Despite their difficulties, trimmed NURBS are the standard in engineering design and for the exchange of geometrical information in general. On the one hand, trimmed tensor product surfaces persist for historical reasons since they are a well-established technology, integrated in current CAD software. On the other hand, this representation distinguishes itself by its efficiency, precision, and simplicity. Trimming problems are hidden from the user who usually designs a model with the help of black box algorithms. Isogeometric analysis and adaptive manufacturing may lead to new developments in CAGD, but trimmed models are the state of the art and changes will certainly take time. It is not clear to the authors whether trimmed NURBS or other techniques like T-splines and subdivision surfaces will triumph in the future, but it is good to see the competition. At this juncture, however, trimmed NURBS seem to be the dominant technology of engineering design.

## 4 Exchange Standards

At the beginning of this section, general considerations for exchanging data between different computer software systems is discussed. Next, the most popular neutral exchange standards, i.e., the Initial Graphics Exchange Specification (IGES) and the Standard for the Exchange of Product Model Data (STEP), are briefly introduced and compared. Finally, this section closes with some concluding remarks.

### 4.1 General Considerations

In modern CAD systems, parameters and constraints govern the design of a model, rather than the definition of specific control points. Further essential components are local features and the construction history. All these various factors are referred to as design intent [162]. Each software has its own native data structure to keep track of the geometry, the topology, and the design intent of its models. Thus, a translation process is required when information is exchanged between systems with different native structures. The conversion of formats may seem like an easy task, but it is in fact very complicated. Usually, there is no

8 Regular internal vertices have four incident edges, also referred to as valency k = 4. All other settings, i.e., k ≠ 4, are denoted as extraordinary vertices.

direct mapping from one format to another. This holds true in particular for information related to the design intent since there are no canonical guidelines for its representation. Consequently, the exchange of the complete data of a CAD model between different systems is scarcely possible, especially when the systems are designed for different purposes. In most cases, only the geometric information of the final object is transferred.

This interoperability issue has been investigated in a study focusing on the US automotive supply chain [294]. The following possible solutions have been discussed: (i) standardization on a single system, (ii) point-to-point translation, and (iii) neutral format translation.

In case of a single system standardization the same native format is used for all processes, e.g., design and analysis. The main advantage is that the compatibility of the model data is assured since no translation is required. However, this approach implies the restriction to a single system. Consequently, every part has to be adjusted to the developments of the dominant application of the software. Most importantly, translation problems can arise even within one system due to different software versions-just imagine you would like to open a PowerPoint presentation created 10 years ago.

The basic idea of point-to-point translation is to convert a native format of a system directly to a native format of another one. This concept works reasonably well for unambiguous data exchange tasks. Unfortunately, it is not always clear how a given information should be translated so that it is properly interpreted in another native format. In addition, a high degree of vendor cooperation is necessary in order to develop a direct translator. Similar to the previous strategy, direct translators have to be rewritten for each new system or perhaps even for new versions of the same software.

Neutral format translation is based on a common neutral format for the exchange of (geometric) data. This approach enables an independent development of various tools work ing on the same model. The minimization of dependencies simplifies the maintenance of each software and eventu ally leads to robust implementations since a clean code is designed to do one thing well, as noted by Stroustrup \({ }^{9}\) [196]. Further, vendors are more willing to develop transla tors for neutral formats since it does not require the disclo sure of proprietary code. This is beneficial since interpreta tion errors of the native format are most likely minimized when the conversion is provided by vendors themselves. An additional advantage of neutral formats is that they are ideally suited for long term storage of data. However, there

9 Bjarne Stroustrup is the inventor of the programming language C++.

are also a number of weaknesses. First of all, it is not possible to capture the design intent and thus, translation to a neutral format provides only a snapshot of the current geometric model. In general, every translation leads to loss of information and the quality of an exchanged model depends on the capability of the neutral format used.

In the context of isogeometric analysis, the minimal requirement is the accurate exchange of geometrical information of the final model. Topology is also essential to assess the connectivity between patches. The reconstruction of topological data based on edge comparison or related strategies is very cumbersome and extremely error-prone, especially in cases of trimmed geometries where edges only coincide within a certain tolerance as elaborated on in Sect. 3. The following two approaches are suggested: (i) direct extraction of topological data from CAD software by a point-to-point translation or (ii) using a neutral format that is able to cope with topological data. The former may be preferred if there is a cooperation with a CAD vendor and the developments focus on the specific product. However, neutral exchange formats will be discussed in the following because they are the most general and independent approaches. Despite their deficiencies, native formats seem to be the most sustainable solution.

### 4.2 Neutral Format Translators

Concepts for a common data exchange format emerged in the 1970s. These attempts were borne by a variety of partners from industry, academia, and government [101]. Based on the initiative of the CAD user community, in particular General Electric and Boeing, vendors agreed to create an American national standard for CAD data exchange. The final result was the first version of IGES [209]. IGES provided the technical groundwork to a more involved exchange format, namely STEP.

#### 4.2.1 IGES

The name of this neutral exchange format already reveals its original purpose [101]:

- -Initial 10 to suggest that it would not replace the work of the American National Standards Institute.

- -Graphics not geometry, to acknowledge that academics may come up with superior mathematical descriptions.

- -Exchange to suggest that it would not dictate how vendors must implement their native database.

- -Specification to indicate that it is not imposed to be a standard.

10 The word 'interim' was used in the first draft.

Implementation specification

IGES provided an important and very practical first solution to the exchange problem, resulting in a file format that is implemented in almost every CAD system. Regarding current literature on isogeometric analysis, it seems that IGES is still the preferred choice when it comes to the extraction of geometric information. Here, we will try to disprove this notion.

According to Goldstein et al. [101] and the studies cited within, the shortcomings of IGES can by summarized as follows: (i) it contains several ways to capture the same information leading to ambiguous interpretation, (ii) loss of information during exchange, (iii) development without rigorous technical discipline, (iv) restriction of exchange capabilities due to the compliance with earlier IGES versions, (v) it was developed as a method to exchange engineering drawings, but not designed for more sophisticated product data, (vi) vendors implemented only portions of IGES, and (vii) there is no mechanism for testing the translators. In addition, IGES is a national standard which may lead to translation problems if other than US software is used. Most importantly, IGES is a stagnant exchange format. The last official version of IGES, i.e., version 5.3 [155], was published more than 20 years ago in 1996.

Although IGES continues to be deployed in industry, its main legacy is the disclosure of several weaknesses of the neutral exchange concept, thereby enhancing new emerging standards. The most notable one is STEP, which provides a broader, more robust standard for the exchange of data [101].

final draft international standard Proof of new international standard

#### 4.2.2 STEP

Since 1984 the International Organization for Standardization (ISO) has been working on a standard for the exchange of product data and its first parts were published in 1994 [232]. The objective of this development effort-one of the largest ever undertaken by ISO-is the complete and unambiguous definition of a product throughout its entire life cycle, which is independent of any computer system [264]. Hence, the corresponding standard includes the exchange of CAD data, yet its scope is much broader.

STEP is the informal term for the standard officially denoted as ISO 10303. It is organized by an accumulation of various parts unified by a set of fundamental principals. These parts are referred to as ISO 10303-xxx, where xxx is determined by the part number. Each of them is separately published and has to pass several development phases summarized in Table 1. Each part is associated with one of the following series : (i) description methods, (ii) implementation specifications, (iii) conformance testing, (iv) generic integrated resources, (v) application integrated resources, (vi) application protocols. Figure 32 gives an overview of these various components of STEP. The description is given by the common formal specification language EXPRESS (Series 10) defining data types, entities, rules, functions, and so on [274]. It is not a programming language, but has an object-oriented flavor. The transfer of data is defined by the implementation specifications (Series 20). The exchange by a neutral ACSII file is addressed in Part 21, 'clear text encoding the exchange structure.' This STEP-file transfer is the most widely used data exchange form of STEP [264]. However, other approaches, like shared memory access, are covered by the series as well, see e.g., Part 22, 'standard data access interface.' Conformance tests provide the verification requirements (Series 30).

The most fundamental components of STEP are the integrated resources. They contain generic information such

![Figure 33 Design model with the same geometry but different topol- ogy](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-33-p028.png)

*Figure 33 Design model with the same geometry but different topol- ogy: a two independent trimmed surfaces and b connected surfaces by a Boolean operation. In a, the isocurves of the separated surfaces are displayed in black and red, respectively. (Color figure online) Table 2 Entity types of the IGES example*

as geometric data and display attributes (Series 40) as well as further elementary units that are specialized for certain application areas (Series 100). For example, Part 42, 'geometric and topological representations,' focuses on the definition of geometric models in general, while Part 104, 'finite element analysis,' is devoted to applications in the context of FEA. These parts provide the entities needed to build application protocols denoted as APs (Series 200). They are the link to the needs of industry and other users. Their purpose is to interpret the STEP data in the context of a specific application which may be part of one or more stages of a life cycle of a particular product. Part 209, 'multidisciplinary analysis and design,' addresses engineering analysis. Each STEP application protocol is further subdivided into a set of conformation classes (CCs). These subsets must be completely implemented if a translator claims to be conform with the standard [233]. Hence, it is important to know what conformance classes are supported by a software system. This modular structure, with several APs and their CCs, may seem complex and daunting, but it gives users the necessary transparency of what can be expected of the data exchanged. Moreover, the complexity of the overall concept of STEP does not imply that it is difficult to use.

The downside of the broad scope of STEP is the large amount of detailed information which may seem overwhelming at first glance. In addition, ISO documents are

One of the advantages of STEP is that it is more than just a specification for exchanging geometric information. It provides a complete product data format allowing the integration of business and technical data of an object, from design to analysis, manufacturing, sales, and service [294]. STEP is perfectly aligned with the spirit of isogeometric analysis, i.e., unifying fields. The most important feature of STEP is its extensibility. Efforts have been made to include the design intent into STEP [162, 233, 234]. Particularly interesting for isogeometric analysis is the specification of volumetric NURBS and local refinement in the next versions of Part 42 and other parts [284].

#### 4.2.3 Comparative Example

In order to demonstrate the representation of trimmed geometries in IGES and STEP, an example of two inter secting planes is considered. A square \([0,5]^{2}\) within the \(x_{y}\) plane is perpendicularly intersected along its diagonal by another plane surface as illustrated in Fig. 33. Thereby, the perpendicular patch is also trimmed into two halves by the square.

The model investigated has been constructed using the software Rhinoceros and the intersection has been computed in two different ways: using (i) the trim-command and (ii) the Boolean-command, respectively. Both schemes lead to the same geometry, yet the topology varies as indicated by the different highlighting of Fig. 33a and b. To be precise, the trim-command produces a surface model that consists of two independent trimmed surfaces, while the Boolean-command results in a solid model where the patches are connected. Both models have been exported to neutral exchange formats. The corresponding IGES and STEP files are provided in the Appendix. In the following, certain aspects of the exported files are discussed.

11 http: www.iso.org, September 2016.

12 https: www.pdesinc.org ResourceIndex.html, September 2016.

13 http: www.steptools.com library standard, September 2016 14 http: www.steptools.com sc4 archive, September 2016.

![Figure 34 Entity connection of the exchange formats. Pointers are indicated by arrows . The examples have been extracted from Files 1 and 3 of the Appendix, respectively](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-34-p029.png)

*Figure 34 Entity connection of the exchange formats. Pointers are indicated by arrows . The examples have been extracted from Files 1 and 3 of the Appendix, respectively: Entity connection of the exchange formats. Pointers are indicated by arrows. The examples have been extracted from Files 1 and 3 of the Appendix, respectively*

![Figure 35 Descriptions of the surface model’s regular square patch. The B-spline surface data has been extracted from Files 1 and 3 of the Appen- dix, respectively](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-35-p029.png)

*Figure 35 Descriptions of the surface model’s regular square patch. The B-spline surface data has been extracted from Files 1 and 3 of the Appen- dix, respectively: Descriptions of the surface model’s regular square patch. The B-spline surface data has been extracted from Files 1 and 3 of the Appendix, respectively*

Remark 3 The default setting of the Rhinoceros export has been chosen, i.e., AP213AutomotiveDesign, for the STEP examples. However, the elements discussed in this section are not affected by this choice.

##### 4.2.3.1 File Structure

The fixed ASCII file format 15 of IGES is structured by the subsequent sections: Start (S), Global (G), Directory Entry (D), Parameter Data (P), and Termination (T). The letters in the brackets label these distinct parts and they are shown in column 73 of every file. The Directory Entry and the Parameter Data is specified by entities which are associated with a unique type number. Table 2 lists the entities used in this example. The Directory Entries provide attribute information for each entity in an IGES file. Each entry is fixed in size and is specified by 20 fields. The first field contains the entity type and the second one points to the first line of the related Parameter Data record. This connection is shown for a rational B-spline surface in Fig. 34a. The Parameter Data, on the other hand, is

15 There exist also a compressed format for details see [155].

free-formatted and it consists of a sequence of integer and real numbers starting with the entity type number.

STEP files are easy to read since the language used is based on an English-like syntax [274]. In general, an accumulation of entities pointing to each other shapes the structure of the exchange data. Lines specifying entities begin with the symbol #, followed by the unique identifier of the corresponding object. This identifier is used to connect various entities with each other as shown in Fig. 34b. Besides pointers, an entity may consists of integers, real numbers, Booleans (.F..T.), and enumeration flags (e.g., . UNSPECIFIED.).

4.2.3.2 Surfaces representation Both exchange formats provide the fundamental informations of B-spline patches, i.e., degree, knot vectors, and control points, together with auxiliary information. In case of IGES, a sequence of numbers separated by commas is used, while STEP additionally groups associated components using brackets. In Fig. 35, the representations of the regular square patch are compared. Note that knot vectors are specified by knot values with their multiplicity and that coordinates of control points are stored

![Figure 36 Graph related to a trimmed surface in STEP. Entities that provide geometrical information are highlighted in gray . Intermediate nodes may be skipped which is indicated by dashed lines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-36-p030.png)

*Figure 36 Graph related to a trimmed surface in STEP. Entities that provide geometrical information are highlighted in gray . Intermediate nodes may be skipped which is indicated by dashed lines: Graph related to a trimmed surface in STEP. Entities that provide geometrical information are highlighted in gray. Intermediate nodes may be skipped which is indicated by dashed lines*

within its own entity in case of STEP. Hence, error-prone comparisons of floating point numbers are avoided.

Regarding trimmed surfaces, the following information is provided in both exchange formats: (i) the regular surface, (ii) the related loops of trimming curves, and (iii) their counterparts in model space. All this information can be found in a single IGES entity, i.e., 141. In particular, the fourth and fifth number within the sequence of this entity define the reference to the regular surface and the number of related curves, respectively. These numbers are followed by arrays of the size 4. The first value of an array refers to model space curves while the last value points to trimming curves. The total number of arrays is determined by the number of related curves.

In case of STEP, the trimmed surface data is not coalesced in a single object, but it is embedded in a graph structure. Hence, the information is represented by various different entities which are linked together. The ADVANCED_FACE entity may be viewed as the starting point of the graph structure that specifies the trimmed patch. Figure 36 illustrates such a collection of entities. For the sake of clarity, some intermediate entities have been neglected as indicated by the dashed lines.

4.2.3.3 Topology So far, the specification of certain parts of a model has been addressed. Here, the differences between the exchange formats regarding an object's topological information is examined by comparing the output for the surface model and solid model shown in Fig. 33. The former is defined by two independent surfaces, while the latter is a single coherent manifold.

In the following the square patch in the \(x_{y}\)-plane is denoted by \(\boldsymbol{S}\) □ and the perpendicular patch is referred to as \(\boldsymbol{S}^{\perp}\). The corresponding edges of the model are labeled \(\boldsymbol{e}_{i}^{\square}\) with \(i=\{1, \ldots, 3\}\) and \(\boldsymbol{e}_{j}^{\perp}\) with \(j=\{1, \ldots, 4\}\), respectively.

The topology due to the STEP and IGES formats is compared in Fig. 37. To be precise, the provided edge loop data is shown. Further details are neglected for the sake of brevity, but the entire files can be found in the Appendix.

Comparing Fig. 37a and b shows that IGES yields the same output for both models. In other words, the different topologies of them are not recognized. Note that the only values that differ are the sequence numbers of the entities which are completely independent from the actual object. In fact, the topological connection of \(\boldsymbol{S}^{\square}\) and \(\boldsymbol{S}^{\perp}\) is lost in case of the solid model, despite the simplicity of the exam ple. That the solid model has been properly constructed is proven by the STEP output shown in Fig. 37d where the edges \(\boldsymbol{e}_{1}^{\perp}\) and \(\boldsymbol{e}_{3}^{\square}\) are joined in a single reference, i.e., \#48.

The STEP data related to the surface model is illustrated in Fig. 37c.

### 4.3 Summary and Discussion

In Sect. 4.1, the problem of exchanging data between different systems is outlined from a general point of view. It is argued that the use of neutral exchange standards is the most comprehensive way for this task. Nevertheless, every mapping from one system to another may cause problems, especially with respect to the design intent of a model where no canonical representation exists. There is often no one-to-one translation from one format to another, which leaves room for (mis)interpretation. As a result, exchange is usually restricted to snapshots of an object's geometry. The transfer of topology data is also possible if (i) the design model is properly constructed as a coherent solid model and (ii) the neutral format is able to capture this information. It is apparent that the capability of the neutral standard applied is essential for the quality and success of the exchange. This has been demonstrated by a simple example given in Sect. 4.2.3 where IGES does not export the topology correctly.

STEP should generally be preferred as a neutral exchange format. According to Tassey et al. [294], STEP is superior to other translators because it

- -addresses many types of data,

- -incorporates a superset of elements common to all systems,

- -supports special application needs, and

- -provides for international exchanges.

In their paper, several studies are discussed in which STEP excels with respect to the quality of exchanging data of industrial examples. In addition, this standard is constantly developed and improved, e.g., by its enhancements for isogeometric analysis [284].

Theoretically, the broad scope and modular structure of STEP provides coverage of various application domains which are indicated by the application protocols and their conformance classes. However, this functionality has to be supported by the CAD vendors. Most vendors have chosen to implement only certain parts of STEP, i.e., some conformance classes of AP 203 and AP 214 [264]. It is not surprising that vendors seem to show little interest in neutral exchange formats, since their implementation slows down the development of the actual software and users become more independent from their products. Hence, it is likely that neutral file formats will always provide less information than the original model. Translation errors may be avoided if the needed data is extracted directly from the native format, but this requires vendor interaction and the restriction to a single software. This alternative is not very sustainable since a native format may become obsolete after a new software version is released.

## 5 Isogeometric Analysis of Trimmed Geometries

Isogeometric analysis of trimmed NURBS is an important research area, simply due to the omnipresence of such geometry representations. Integration of design and analysis can only be achieved if the simulation is able to cope with CAGD models that are actually used in the design process. Moreover, sound treatment of trimmed solid models is also an essential step for the derivation of volumetric representations.

Current attempts to integrate trimmed geometries into isogeometric analysis may be classified as global and local approaches. The latter uses the parameter space of the trimmed patch as background parameterization and the trimming curves determine the domain of interest, i.e., \(\mathcal{A}^{\mathrm{v}}\), for the analysis. Knot spans that are cut by trimming curves require special attention during the simulation. In that sense, local approaches are closely related to fictitious domain methods, \({ }^{16}\) see e.g., [124, 239, 252, 259]. Conse quently, similar tasks have to be undertaken: (i) detection of trimmed elements, (ii) application of special integra tion schemes in these elements, and (iii) stabilization of the trimmed basis. CAGD models are not modified but the analysis has to deal with all the related robustness issues pointed out in Sect. 3.2.2. Global reconstruction, on the other hand, substitutes a trimmed surface by one or sev eral regular patches which can be analyzed with regular integration rules. In other words, it is endeavored to fix the design model, before it is used in the downstream applica tion, e.g., the simulation. These approaches are similar to remodeling schemes in CAGD presented in Sect. 3.4.1. Isogeometric analysis of subdivision surfaces, e.g., [59, 248, 309], and T-splines, e.g., [22, 262, 263, 321], may be included into the class of global reconstruction techniques. However, the discussion of the analysis of these representations is beyond the scope of this review.

Coupling of multiple patches is another issue that has to be addressed. Adjacent patches usually have nonmatching parameterizations and a robust treatment of tolerances is required to link the degrees of freedom along an intersection due to the gaps between trimmed surfaces and the missing link between their trimming curves. Local

16 There are various names for fictitious domain methods such as embedded domain methods, finite cell methods, WEB-spline methods, and immersed boundary methods. The principle idea, however, is the same.

approach have to deal with the issue directly during the analysis, while global approach apply this crucial step beforehand during the remodeling phase. The coupling itself is usually performed by a weak coupling technique. Alternatively, some global schemes try to establish matching parameterizations during the reconstruction procedure. This allows an explicit coupling of patches and a better control of the continuity between adjacent patches [149]. It is also noteworthy that the coupling procedure may be neglected in certain simulation methods. For example, the boundary element method and the Nyström method do not require certain continuity between elements or patches, see e.g., [218, 223, 225, 319].

The following approaches for analyzing trimmed geometries have been applied to finite element and boundary element methods. The former focuses on shell analysis while the latter is used for volumetric B-Rep models. However, the basic concepts are not restricted to a specific simulation type since in both cases the treatment of trimmed surfaces is in the focus. It will be highlighted if a certain part explicitly applies for a specific simulation method.

The overview begins with a short historical note, which, to the best of the authors' knowledge is the first direct simulation with trimmed patches. Afterwards, the current state of research is reviewed in the Sects. 5.2 and 5.3 addressing global and local approaches, respectively.

### 5.1 The First Analysis of Trimmed Models

It is fascinating that the analysis of trimmed patches goes back to the genesis of trimmed patch formulations. In fact, Casale et al. [48, 50] presented an analysis of such geometries a few years after they had suggested one of the first trimmed solid model formulations [47, 49]. In particular, trimmed patch boundary elements had been proposed.

The basic idea of their approach is to employ the trimmed patch for the geometrical representation and to define an independent Lagrange interpolation over the tensor product surface for the description of the physical variables. This additional basis does not take the trimming curves into account. Thus, the nodes of the Lagrange inter polation may lie inside or outside the trimmed domain. This is emphasized by using the term virtual nodes. The analysis is performed by means of a collocated boundary ele ment formulation, see e.g., [96], where all Lagrange nodes contribute to the system matrix. If a node is outside of the trimmed domain, the jump term coefficient \({ }^{17}\) of the bound ary integral equation is set to 1 since the node is not part of the object's boundary. Numerical integration is performed

17 Usually, the jump term coefficient depends on the geometric angle of the boundary at the point considered, see e.g., [96].

over a triangulation of the trimmed domain. These triangles are used to define integration regions only and do not contribute any degrees of freedom.

This concept has various deficiencies, but it consists of features that can be found in current approaches as well. For example, defining the geometrical mapping by the trimmed parameter space, but the physical fields by a different (spline) basis is employed in some global techniques presented later. There are also similarities to local schemes since the trimmed domain is treated like a background parameterization leading to special considerations regarding numerical integration and points that are not within the domain. Furthermore, the motivation for the application of the boundary element method was the same as today in isogeometric analysis, i.e., the potential of a direct analysis of B-Rep models without the need of generating a volumetric discretization.

### 5.2 Global Approaches

Global reconstruction schemes decompose trimmed surfaces into regular patches. The general concept is the same as presented in Sect. 3.4.1 in the context of CAGD. The distinguishing aspect is that the following strategies are aimed to provide analysis-suitable models.

#### 5.2.1 Reconstruction by Ruled Surfaces

Trimming curves \(\boldsymbol{C}^{t}\) may be used to define a mapping \(\mathcal{X}_{t}\) such that a regular tensor product basis specifies the valid area \(\mathcal{A}^{\mathrm{v}}\) of the corresponding trimmed patch, as proposed by Beer et al. [25]. To be precise, \(\mathcal{X}_{t}\) is given by a linear interpolation between two opposing \(\boldsymbol{C}_{i}^{t}, i=\{1,2\}\). The geometrical mapping to the model space is performed by the original trimmed patch, hence the approach is also referred to as double mapping method.

The following assumptions are made for the sake of notational simplicity. Firstly, the regular basis functions are defined over a unit square, i.e., \(s, t \in[0,1]\). In addition, it is assumed that both trimming curves are specified within the same parameter range \(\tilde{u} \in[a, b]\). Based on that, the intrinsic coordinate \(\tilde{u}\) can be linked to the boundaries of the

These equations traverse the interval of \(\tilde{u}\) in opposite direc tions, e.g., \(f(0)=g(1)=a\), since one of the trimming curves has to be evaluated in reverse order. Finally, \(\mathcal{X}_{t}\) is determined by

![Figure 38 Double mapping scheme to fit a regular tensor product sur- face to a trimmed patch. The first mapping  t specifies the transfor- mation to the valid area  v of the trimmed parameter space, while the geometric mapping is denoted by  . The trimming curves C t i ( ̃ u ) , i = { 1, 2 } , are illustrated by thick lines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-38-p033.png)

*Figure 38 Double mapping scheme to fit a regular tensor product sur- face to a trimmed patch. The first mapping  t specifies the transfor- mation to the valid area  v of the trimmed parameter space, while the geometric mapping is denoted by  . The trimming curves C t i ( ̃ u ) , i = { 1, 2 } , are illustrated by thick lines: Double mapping scheme to fit a regular tensor product surface to a trimmed patch. The first mapping  t specifies the transformation to the valid area  v of the trimmed parameter space, while the geometric mapping is denoted by  . The trimming curves C t i ( ̃ u), i = { 1, 2, are illustrated by thick lines*

From a CAGD point of view, the mapping (55) is equivalent to the one of a ruled surface (26). The main difference is that the ruled surface is defined in the parameter space in this case. The geometric mapping  , however, is still performed by the trimmed patch. Figure 38 summarizes the concept of the double mapping approach.

The main advantage of this approach is its simplicity and ease of implementation. However, there are various restric tions: First of all, the assumption that \(\mathcal{A}^{\mathrm{v}}\) is governed by two opposing trimming curves limits the application to very specific trimming situations. Furthermore, the four-sided nature of \(\mathcal{A}^{\mathrm{v}}\) is implied. Consequently, trimmed patches with more complex topology have to be decomposed by an additional preprocessing step. There is no control over the quality of the parameterization due to the mapping \(\mathcal{X}_{t}\). Ele ments may become very distorted depending on the posi tion of the trimming curves \(\boldsymbol{C}_{i}^{t}\). Such a situation occurs for a triangular-shaped \(\mathcal{A}^{\mathrm{v}}\), see Fig. 9. Since the parameteri zation is completely independent of the basis functions of the trimmed parameter space, the double mapping method works well for Bézier patches. An integration issue arises as soon as B-spline patches are considered. The problem is depicted in Fig. 39. Note that the parameter lines of the geom etry representation propagate through the elements defined by the mapped regular parameterization. Thus, integration

![Figure 39 Double mapping method for a B-spline patch. The dotted lines indicate parameter curves that are not C ∞ -continuity within  v](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-39-p033.png)

*Figure 39 Double mapping method for a B-spline patch. The dotted lines indicate parameter curves that are not C ∞ -continuity within  v: Double mapping method for a B-spline patch. The dotted lines indicate parameter curves that are not C ∞ -continuity within  v*

of the regular elements is not performed over a \(C^{\infty}\)-continu ous region. In order to get a proper distribution of quad rature points, the elements must be subdivided along the non-smooth edges. The specification of such regions is not straightforward. To conclude, the double mapping method is a simple solution for (Bézier) patches which had been trimmed during the design process, at least for ones that can be represented by a regular patch.

#### 5.2.2 Reconstruction by Coons Patches

$$
\begin{equation*} \boldsymbol{S}^{\mathcal{A}^{v}}(s, t)=(1-t) \boldsymbol{C}_{1}^{t}(f(s))+t \boldsymbol{C}_{2}^{t}(g(s)) . \tag{55} \end{equation*}
$$

A natural extension of the previous method is to define the mapping \(\mathcal{X}_{t}\) to a trimmed parameter space by means of Coons patches. In contrast to the ruled surface interpola tion (55), \(\mathcal{X}_{t}\) takes four boundary curves into account. Ran drianarivony [237, 238] developed such an approach, which has been applied to wavelet Galerkin BEM in collabora tion with Harbrecht [113]. Although they do not focus on isogeometric analysis per se, most of their techniques can be directly utilized: (i) decomposition of \(\mathcal{A}^{\mathrm{v}}\) into several four-sided patches, (ii) identification if \(\mathcal{X}_{t}\) is a diffeomor phism, \({ }^{18}\) and (iii) construction of matching parameteriza tions of adjacent patches.

The first step of the decomposition procedure is to sub stitute the trimming curves \(\boldsymbol{C}^{t}\) of each patch by a linear approximation \(\boldsymbol{C}^{l}\). The vertices \(\boldsymbol{x}\) of \(\boldsymbol{C}^{l}\) are located along \(\boldsymbol{C}^{t}\) as illustrated in Fig. 40a. \(\boldsymbol{C}^{l}\) should be as coarse as pos sible since the number of vertices determines the number of patches that decompose \(\mathcal{A}^{\mathrm{v}}\). As initial approximation, the endpoints of the trimming curves may be used. How ever, \(\boldsymbol{C}^{l}\) has to be fine enough to resolve the topology of the trimmed patch, e.g., lines of exterior loops may not inter sect ones of interior loops. In order to get a single polygon representing \(\mathcal{A}^{\mathrm{v}}\), interior loops are connected to exterior

18 A diffeomorphism is a C ∞ mapping with a C ∞ inverse.

![Figure 40 Decomposing of a trimmed domain  v into b regular four- sided patches  i . In a , the trimming curves are continuous whereas the linear approximation is illustrated by dashed lines . Further, vertex x 0 and x 4 are connected by a double edge](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-40-p034.png)

*Figure 40 Decomposing of a trimmed domain  v into b regular four- sided patches  i . In a , the trimming curves are continuous whereas the linear approximation is illustrated by dashed lines . Further, vertex x 0 and x 4 are connected by a double edge: Decomposing of a trimmed domain  v into b regular foursided patches  i. In a, the trimming curves are continuous whereas the linear approximation is illustrated by dashed lines. Further, vertex x 0 and x 4 are connected by a double edge*

$$
\begin{equation*} \boldsymbol{C}_{j}(v)=\sum_{k=0}^{p} B_{k, p}(v) \boldsymbol{c}_{k}^{j}, \quad j=3,4, \quad v \in[0,1] . \tag{57} \end{equation*}
$$

Therefore, it is important that the total number of vertices \(\boldsymbol{x}\) is even. In the next step, the straight boundary curves of \(\boldsymbol{C}^{l}\) are replaced by the complementary portions of \(\boldsymbol{C}^{t}\). An example of a decomposition is shown in Fig. 40b. Due to this procedure, the following problems may arise. The most obvious one is that the curved bound ary may intersect an internal edge. In addition, sharp cor ners become degenerated points if the corresponding \(\boldsymbol{x}\) is smoother than \(C^{0}\). As a result, no diffeomorphism for this region can be found [237]. Finally, it is not assured that a Coons patch interpolation is regular. Such problems arise particularly in case of non-convex domains. An example of a non-regular Coons patch where the parametric lines of the surface overspill is shown in Fig. 41. A remedy to the men tioned issues is local refinement of \(\boldsymbol{C}^{l}\) or the affected \(\mathcal{R}_{i}\). The detection of the first two problems is straightforward, but determination of a Coons patch's regularity requires a more detailed discussion.

The following identification procedure assumes that the Coons patch interpolation (35) is planar and described by boundary curves given in Bézier form, i.e.,

![Figure 41 Example of a planar non-regular Coons patch where iso- curves overlap](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-41-p034.png)

*Figure 41 Example of a planar non-regular Coons patch where iso- curves overlap: Example of a planar non-regular Coons patch where isocurves overlap (a) Approximation of the trimmed domain*

The interpolation function \(f_{1}\) is also described as a Bézier polynomial

$$
\begin{equation*} f_{1}(s)=\sum_{k=0}^{p} B_{k, p}(s) \psi_{k}=1-f_{0}(s), \quad s \in[0,1] \tag{58} \end{equation*}
$$

$$
For the determination of the regularity, the factors \( \mu, \tau \), and \( \alpha \) are specified by
$$

$$
\begin{align*} \mu & :=\max \left\{\left|f_{1}^{\prime}(s)\right|: s \in[0,1]\right\}, \tag{59}\\ \tau & :=\min \left\{\tau_{k \ell}^{i j}\right\}, \quad k, \ell=0, \ldots, p \tag{60}\\ \alpha & :=\max \left\{\alpha_{1}, \alpha_{2}\right\} . \tag{61} \end{align*}
$$

The indices \(i\) and \(j\) are defined as above and the factors in Eqs. (60) and (61) are determined by

$$
\begin{align*} & \tau_{k \ell}^{i j}:=p^{2} \operatorname{det}\left[\boldsymbol{c}_{k+1}^{i}-\boldsymbol{c}_{k}^{i}, \boldsymbol{c}_{\ell+1}^{j}-\boldsymbol{c}_{\ell}^{j}\right] \tag{62}\\ & \alpha_{1}:=\max _{k=0, \ldots, p}\left\{\mu\left\|\left(\boldsymbol{c}_{k}^{4}-\boldsymbol{c}_{k}^{3}\right)+\psi_{k} \hat{c}+\left(\boldsymbol{c}_{0}^{1}-\boldsymbol{c}_{p}^{1}\right)\right\|\right\}, \tag{63}\\ & \alpha_{2}:=\max _{k=0, \ldots, p}\left\{\mu\left\|\left(\boldsymbol{c}_{k}^{2}-\boldsymbol{c}_{k}^{1}\right)+\psi_{k} \hat{c}+\left(\boldsymbol{c}_{0}^{1}-\boldsymbol{c}_{0}^{2}\right)\right\|\right\}, \tag{64} \end{align*}
$$

with \(\hat{c}=\left(c_{0}^{2}-c_{p}^{2}+c_{p}^{1}-c_{0}^{1}\right)\). Finally, the constant \(\beta\) is defined such that

$$
\begin{equation*} \boldsymbol{C}_{i}(u)=\sum_{k=0}^{p} B_{k, p}(u) \boldsymbol{c}_{k}^{i}, \quad i=1,2, \quad u \in[0,1], \tag{56} \end{equation*}
$$

$$
\begin{equation*} p\left\|\psi_{k}\left(\boldsymbol{c}_{\ell+1}^{2}-\boldsymbol{c}_{\ell}^{2}+\boldsymbol{c}_{\ell}^{1}-\boldsymbol{c}_{\ell+1}^{1}\right)+\left(\boldsymbol{c}_{\ell+1}^{1}-\boldsymbol{c}_{\ell}^{1}\right)\right\| \leq \beta, \tag{65} \end{equation*}
$$

![Figure 42 Converting a pair of odd faces to even ones. Circles indicate the initial vertices of the faces and crosses mark those vertices that had been added to obtain faces with an even number of vertices](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-42-p035.png)

*Figure 42 Converting a pair of odd faces to even ones. Circles indicate the initial vertices of the faces and crosses mark those vertices that had been added to obtain faces with an even number of vertices: Converting a pair of odd faces to even ones. Circles indicate the initial vertices of the faces and crosses mark those vertices that had been added to obtain faces with an even number of vertices*

$$
\begin{equation*} p\left\|\psi_{k}\left(c_{\ell+1}^{4}-c_{\ell}^{4}+c_{\ell}^{3}-c_{\ell+1}^{3}\right)+\left(c_{\ell+1}^{3}-c_{\ell}^{3}\right)\right\| \leq \beta, \tag{66} \end{equation*}
$$

$$
\begin{equation*} \mathcal{X}_{i}\left(\boldsymbol{x}_{k}^{i}\right)=\mathcal{X}_{j}\left(\boldsymbol{x}_{\ell}^{j}\right), \tag{71} \end{equation*}
$$

for all \(\ell=0, \ldots, p-1\) and \(k=0, \ldots, p\). Based on these definitions, the Coons patch mapping is regular if

These are only sufficient conditions. If they are not ful filled a subdivision procedure is employed. Therefore, another sufficient condition is derived. Assuming that a Coons patch is represented as Bézier surface with control points \(\boldsymbol{c}_{i, j}^{C}\), the Jacobian can also be described as a Bézier function of degree \(2 p\) with the control points

$$
\begin{equation*} c_{m, n}^{J}=\sum_{\substack{i+k=m \\ j+\ell=n}} C(i, j, k, \ell) \frac{\binom{p}{i}\binom{p}{k}}{\binom{2 p}{i+k}} \frac{\binom{p}{j}\binom{p}{\ell}}{\binom{2 p}{j+\ell}}, \tag{68} \end{equation*}
$$

$$
\begin{equation*} \hat{\boldsymbol{C}}_{i}^{t}:=\overline{\boldsymbol{C}}_{i}^{t} \circ \phi_{i}, \quad \phi_{i}=\left(\lambda_{i}\right)^{-1}, \tag{72} \end{equation*}
$$

$$
with m , n = 0, … , 2 p and the coefficients
$$

where

$$
\begin{equation*} D(i, j, k, \ell):=p^{2} \operatorname{det}\left[\boldsymbol{c}_{i+1, j}^{C}-\boldsymbol{c}_{i, j}^{C}, \boldsymbol{c}_{k, \ell+1}^{C}-\boldsymbol{c}_{k, \ell}^{C}\right] . \tag{70} \end{equation*}
$$

If the coefficients \(\boldsymbol{c}_{m, n}^{J}\) have the same sign the Coons patch mapping is a diffeomorphism. In case of unequal signs, the patch is adaptively subdivided and for each sub-patch the coefficients \(\boldsymbol{c}_{m, n}^{J_{\text {sub }}}\) are computed. The procedure stops as soon as the signs of \(\boldsymbol{c}_{m, n}^{J_{\text {sub }}}\) do not change within every sub-patch.

The overall Coons patch is not regular, if it consists of subpatches with different signs. It is emphasized that the subdivision is only performed to determine the regularity of the mapping. The corresponding proofs and more information can be found in [113, 237].

In case of multiple patches, a matching parameterization between adjacent surfaces is sought. The connectivity is described by a graph. During the decomposition procedure, the polygon vertices of the adjacent patches \(\boldsymbol{S}_{i}\) and \(\boldsymbol{S}_{j}\) are computed so that where \(\boldsymbol{x}_{k}^{i}\) and \(\boldsymbol{x}_{\ell}^{j}\) are the vertices along the common edge and \(\mathcal{X}\) denotes the geometrical mapping (23). If a vertex \(\boldsymbol{x}_{k}^{i}\) is added to obtain an even-numbered approximation \(\boldsymbol{C}^{l}\), a corresponding \(\boldsymbol{x}_{\ell}^{j}\) needs to be added in the adjacent patch. Thus, odd faces can be converted to even ones only in pairs as illustrated in Fig. 42. It should be noted that the inserted vertices propagate through faces which are even already. In order to minimize the affected faces, the shortest path connecting two faces is computed by the application of Dijkstra's algorithm [72] to the connectivity graph. In addi tion to matching vertices, trimming curves \(\boldsymbol{C}^{t} \in[a, b]\) are parameterized by means of the chord length of the corre sponding intersection curve in model space. The trimming curve segment of quadrilaterals \(\mathcal{R}_{i}\) is initially defined by \(\overline{\boldsymbol{C}}_{i}^{t}\left(t \cdot a_{i}+(1-t) b_{i}\right) \in\left[a_{i}, b_{i}\right] \subset[a, b]\). The new representation \(\hat{\boldsymbol{C}}_{i}^{t}\) is given by

$$
\begin{equation*} 2 \alpha \beta+\alpha^{2}<\tau \quad \text { and } \quad \tau>0 . \tag{67} \end{equation*}
$$

$$
with \( \phi_{i} \) denoting the inverse of the length function
$$

$$
\begin{align*} C(i, j, k, \ell):= & \frac{\ell}{p}\left[\frac{i}{p} D(i-1, j, k, \ell-1)\right. \\ & \left.+\left(1-\frac{i}{p}\right) D(i, j, k, \ell-1)\right] \\ & +\left(1-\frac{\ell}{p}\right)\left[\frac{i}{p} D(i-1, j, k, \ell)\right. \tag{69}\\ & \left.+\left(1-\frac{i}{p}\right) D(i, j, k, \ell)\right] \end{align*}
$$

$$
\begin{equation*} \lambda_{i}(t):=\int_{a}^{t}\left\|\frac{d\left(\mathcal{X} \circ \overline{\boldsymbol{C}}_{i}^{t}\right)}{d t}(\theta)\right\| \mathrm{d} \theta . \tag{73} \end{equation*}
$$

Hence, the images of the trimming curve \(\hat{\boldsymbol{C}}^{t}\) of adjacent patches match at the same parametric values, i.e., the same chord length. This procedure is applied before the Coons patch construction. For details on the computation of the reparameterization the interested reader is referred to [238].

In contrast to the approach described in the previous subsection, this reconstruction scheme addresses the partitioning of trimmed domains into several four-sided regions, the regularity of these regions, and the connection of adjacent patches. Yet, some aspects are unresolved. For instance, the compatibility condition (71) implies that trimming curves coincide which is usually not the case as discussed in Sect. 3. Since the trimming curves do not describe the same curve in model space, the chord length parameterization may lead to diverse results. Thus, a robust implementation is required that treats the tolerances involved. As

#### 5.2.3 Reconstruction by Isocurves

Recently, Urick [298] presented a reconstruction approach based on isocurves (25). In contrast to the previous schemes, the trimmed patch is replaced by a new parameterization and a new set of control points. The overall procedure consists of several steps including (i) topology detection, (ii) parameter space analysis and determination of knot vector superset, (iii) reparameterization of trimmed parameter spaces, (iv) computation of corresponding control points, and (v) the treatment of multiple trimming curves. In order to identify the topology of the trimmed domain \(\mathcal{A}^{\mathrm{v}}\), characteristic points \(\boldsymbol{x}\) of the trimming curves \(\boldsymbol{C}^{t}\) are determined. The points considered are summarized in Table 3. They represent characteristic points commonly used in surface-to-surface intersection schemes (i.e., types 0,2, and 3) [221], along with an additional point previously not utilized (type 1). The main purpose of this classification is to detect portions \(\gamma\) of a trimming curve that are asso ciated to either the \(u\)-direction, i.e., \(\gamma^{u}\), or the \(v\)-direction, i.e., \(\gamma^{v}\), of the parameter space. With this in mind, the most significant points are those of types 0 and 1, because they indicate a possible transition from \(\gamma^{u}\) to \(\gamma^{v}\). Each \(\gamma\) together with its opposing edge of the parameter space specifies a four-sided regions \(\mathcal{R}\). An example of a segmentation of \(\mathcal{A}^{\mathrm{v}}\) is illustrated in Fig. 43. Note that not every characteristic point of type 1, i.e., \(\boldsymbol{x}^{1}\), yields a new portion. Hence, the sequence of characteristic points has to be examined rather than the classification of individual points. Once all reconstruction regions \(\mathcal{R}\) are detected, the parameterization of adjacent patches is aligned. The fol lowing knot cross-seeding procedure establishes a oneto-one relation of points along the intersection curve \(\hat{\boldsymbol{C}}(s)\) in model space and the related trimming curves of the

![Figure 43 Determination of the trimming curve portions 훾 u and 훾 v which are associated to the parametric direction u and v , respectively. The boundary of the related regions  i within the trimmed domain are indicated by dashed lines . Characteristic points x are marked by crosses which correspond to the sloped of the curve. The point type is denoted by the related superscript](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-43-p036.png)

*Figure 43 Determination of the trimming curve portions 훾 u and 훾 v which are associated to the parametric direction u and v , respectively. The boundary of the related regions  i within the trimmed domain are indicated by dashed lines . Characteristic points x are marked by crosses which correspond to the sloped of the curve. The point type is denoted by the related superscript: Determination of the trimming curve portions 훾 u and 훾 v which are associated to the parametric direction u and v, respectively. The boundary of the related regions  i within the trimmed domain are indicated by dashed lines. Characteristic points x are marked by crosses which correspond to the sloped of the curve. The point type is denoted by the related superscript*

surfaces \(\boldsymbol{S}_{i}(u, v)\). Firstly, \(\hat{\boldsymbol{C}}(s)\) is refined so that it is defined by Bézier segments, i.e., the multiplicity of all knots is equal to the curve's degree. Furthermore, each \(\boldsymbol{S}_{i}(u, v)\) is subjected to knot insertion in the \(u\)-direction and \(v\)-direction at their characteristic points \(\boldsymbol{x}\) of \(\gamma^{u}\) and \(\gamma^{v}\) portions, respec tively. Thus, the knot vectors of the surfaces incorporate the locations of all \(\boldsymbol{x}\). In the next step, the knot information is exchanged across the different objects involved in order to define a knot vector superset. During this process, new Bézier segments are introduced to \(\hat{\boldsymbol{C}}(s)\). In particular, knots are added at the parametric values \(\hat{s}\) that correspond to the knots of \(S_{i}(u, v)\). The values \(\hat{s}\) are determined by minimiz ing the distance of \(\hat{\boldsymbol{C}}(s)\) to isocurves \(\boldsymbol{C}^{\text {iso }}(u)\) and \(\boldsymbol{C}^{\text {iso }}(v)\) of each \(\boldsymbol{S}_{i}(u, v)\) and the fixed parameters of these isocurves are determined by the knot values of the surfaces. As a result, the refined intersection curve and its superset knot vector reflect the knots and topological characteristics of itself, the related surfaces, and their trimming curves. Finally, this information is passed on to the surfaces, i.e., all \(\boldsymbol{S}_{i}(u, v)\) are refined at the interior knots of \(\hat{\boldsymbol{C}}(s)\) including the knots of the adjacent \(\boldsymbol{S}_{j}(u, v), j \neq i\). This is done by minimizing the distance between the points of \(\hat{\boldsymbol{C}}(s)\) and \(\boldsymbol{S}_{i}(u, v)\). The exchange of knot data is necessary in order to guarantee that patches are connected along their intersection after the reconstruction. Reparameterization is required to obtain a conforming basis for each four-sided region \(\mathcal{R}\). Suppose \(\mathcal{R}\) is related to a \(\gamma^{\nu}\)-portion \({ }^{19}\) of a trimming curve, then it is described by a set of isocurves \(\left\{\boldsymbol{C}_{k}^{\text {iso }}(u)\right\}_{k=1}^{K}\) along fixed parameter values

19 Regions related to a 𝛾 u-portion are treated in an analogous manner.

Thus, the reparameterized region \(\tilde{\mathcal{R}}\) will be conformal with \(\hat{\boldsymbol{C}}(s)\) and the reparameter ized counterpart of an adjacent surface will be conformal as well. Due to the cross-seeding process, \(\gamma^{v}\) is linked to at least one Bézier segment of \(\hat{\boldsymbol{C}}(s)\). The positions \(s_{k}^{\text {iso }}\) of the isocurves \(\boldsymbol{C}_{k}^{i s o}(u)\) are determined by the endpoints and Greville abscissae of these Bézier segments. The corre sponding parametric values in the \(u\)-direction are labeled \(\hat{u}_{k}\) and represent the locations where the distance of \(\boldsymbol{C}_{k}^{i s o}(u)\) is minimal to \(\hat{\boldsymbol{C}}(s)\). Knot insertion at \(\hat{u}_{k}\) is applied to extract the part of \(\boldsymbol{C}_{k}^{i s o}(u)\) that is within the domain of interest, i.e., the current four-sided region \(\mathcal{R}\). The values \(\hat{u}_{k}\) vary for each \(\boldsymbol{C}_{k}^{i s o}(u)\) since they are distributed close to the trimming curves. In other words, parameter intervals of the isocurves within \(\mathcal{R}\) do not match in general. To overcome this issue, all \(\boldsymbol{C}_{k}^{i s o}(u)\) are reparameterized to be specified by the same basis.

The simplest way to establish the reparameterization is to use a linear coordinate transformation so that all isocurves are defined over a common range, combined with a subsequent accumulation of the shifted interior knots of each knot vector. However, this technique yields a large number of basis function since interior knots of isocurves with different initial intervals do not coincide after the transformation. Furthermore, the size of the resulting knot spans may vary excessively because the alteration of shifted interior knots can be arbitrarily small.

Hence, a nonlinear reparameterization is preferred. A set of functions \(\left\{f_{k}(\tilde{u})\right\}_{k=1}^{K}\) is sought that maps the correspond

Note that the linear coordinate transformation is a special case of this formulation where the degree of the function is set to q = 1. The composite of an isocurve \(C^{iso}\) k (u) and its f k ( ̃ u) determines the reparameterization

$$
\begin{equation*} f(\tilde{u}, s)=\sum_{i=0}^{I-1} \sum_{j=0}^{J-1} B_{i, \tilde{p}}(\tilde{u}) B_{j, p_{s}}(s) c_{i, j}, \tag{76} \end{equation*}
$$

The degree of the resulting curve is given by ̃ p = pq where p refers to the original degree of the isocurve. If the longest isocurve is taken as target parameterization, it can be adjusted by using conventional degree elevation to ̃ p. The other curves are subjected to a nonlinear reparameterization based on their f k ( ̃ u). For technical details on nonlinear reparameterization of curves the interested reader is referred to the textbook [230].

![Figure 44 Reparameterization of a trimmed parameter space of a bicu- bic Bézier patch](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-44-p037.png)

*Figure 44 Reparameterization of a trimmed parameter space of a bicu- bic Bézier patch: a surface f ( ̃ u, s) that reparameterizes the trimmed parameter space u to a regular one ̃ u indicated by the vertical and plane grid, respectively. Lines on the surface mark the associated isocurve along s iso k. b Profile of the isocurves f k ( ̃ u)*

$$
\begin{equation*} f_{k}(\tilde{u})=\sum_{i=0}^{I-1} B_{i, q}(\tilde{u}) c_{i}^{k}, \quad q>1, \quad k=1, \ldots, K . \tag{74} \end{equation*}
$$

It remains to find a way to coordinate the individual \(f_{k}(\tilde{u})\) to obtain a global reparameterization for the whole reconstruction domain \(\mathcal{R}\) that yields a new valid tensor product parameter space \(\tilde{\mathcal{R}}\). The key idea is to represent the global transformation as a spline surface \(f(\tilde{u}, s)\). This sur face includes all \(f_{k}(\tilde{u})\) as isocurves, i.e., \(f\left(\tilde{u}, s_{k}^{i s o}\right)=f_{k}(\tilde{u})\). The bivariate reparameterization is given by with the degree \(p_{s}\) of the intersection curve segment and a grid of scalar control coefficients \(c_{i, j}\). If the degree in the \(v\) -direction of the trimmed surface varies from \(p_{s}\), the degree of the segment may be adjusted by means of degree eleva tion. Equation (76) can be represented as a non-parametric

- (c) Further reconstruction regions after basis update

surface by linking the coefficients \(c_{i, j}\) to their Greville abscissae (22).

The corresponding control points are defined as

$$
c_{i, j}=\left[\begin{array}{c} \left(\tilde{u}_{i+1}+\tilde{u}_{i+2}+\cdots+\tilde{u}_{i+\tilde{p}}\right) / \tilde{p} \tag{77}\\ \left(s_{j+1}+s_{j+2}+\cdots+s_{j+p_{s}}\right) / p_{s} \\ c_{i, j} \end{array}\right] .
$$

The coefficients \(c_{i, j}\) can be defined by the user as long as the following restrictions are met:

- (i) The function f ( ̃ u, s) must be strictly monotonic in the ̃ u-direction so that intervals do not overlap.

- (ii) The spline surface must employ the same target knot vector ̃ 𝛯 in the ̃ u-direction.

- (iii) Each knot value \(u_{i}\) of the initial knot vectors must be mapped to a distinct ̃ \(u_{i}\) ∈ ̃ 𝛯 for all isocurves, i.e., \(u_{i}\) = f ( ̃ \(u_{i}\), s iso k), k = 1, … , K.

An illustration of such a bivariate reparameterization func tion \(f(\tilde{u}, s)\) is provided in Fig. 44a and the corresponding isocurves are shown in Fig. 44b. It should be noted that the parameter space spanned by the \(\tilde{u}\)-axis and \(s\)-axis is defined by straight parameter lines only, in contrast to the original basis spanned by the \(u\)-axis and \(s\)-axis. It is emphasized that

$$
\begin{equation*} \tilde{\boldsymbol{c}}_{i}^{k}=\sum_{j=0}^{J-1} B_{j, q}\left(s_{k}^{i s o}\right) \boldsymbol{c}_{i, j}, \quad k=1, \ldots, K . \tag{78} \end{equation*}
$$

- (a) Topology detection and characteristic points

- (b) first two reconstruction regions

the graphs in Fig. 44b intersect at the common interior knots ̃ \(u_{i}\) = \(u_{i}\) = { 1 3, 2 3. The final step of the reconstruction scheme is to determine the control points of the reparameterized regions \(\tilde{\mathcal{R}}\). Therefore, we recall the specification of the control points \(\tilde{\boldsymbol{c}}_{i}^{k}\) of isocurves \(\boldsymbol{C}_{k}^{i s o}(u)\) as a weighted combination of surface control points \(\boldsymbol{c}_{i, j}\)

Isocurves have been introduced at the Greville abscissae of the Bézier segments along the reconstruction boundary \(\gamma^{\nu}\). Hence, the number of isocurves is equal to the number of unknowns, i.e., \(J=K\), and the control points \(\boldsymbol{c}_{i, j}\) can be It is quite astonishing that the procedure described remains the same when multiple trimming curves are involved. Instead of assessing the topology of all trimming curves at once, the trimming curve or more precisely each \(\gamma\) is processed successively and independently of each other. In fact, it does not matter if the portions \(\gamma\) originate from one or several trimming curves. After each reparameteri zation the parameter space is updated and the next region is addressed. The iterative evolution of the reconstructed regions \(\tilde{\mathcal{R}}\) is displayed in Fig. 45. To be clear, the regions \(\mathcal{R}_{0}\) and \(\mathcal{R}_{1}\) shown in Fig. 45b and the regions \(\mathcal{R}_{2}\) and \(\mathcal{R}_{3}\) displayed in Fig. 45c are not constructed at the same time.

The final outcome of the reconstruction is a new set of patches with aligned parameter spaces that share the control point of their intersection curves. Thus, the reconstructed object is watertight. It is emphasized that this holds true even for non-manifolds. These benefits come at the price of an alteration of the initial geometry and an increase of the degrees of freedom. Since the concept has been pre sented just recently, there are several open research topics to explore. For instance, an estimation of the geometrical error introduced with respect to the degree of the reparam eterization function and the number of isocurves would be of great interest. This could be the basis for an optimization procedure for the definition of the reparameterization func tion. Another topic might be the quality of the resulting ele ments in model space, especially at the transitions from \(\gamma^{u}\) to \(\gamma^{v}\) regions.

We close the discussion of the isocurve reconstruction approach with some application remarks. Firstly, the concept can also be applied locally. In this paper it is focused on the tensor product case where refinement propagates Lu through the whole domain for the sake of simplicity. A locally reconstructed parameter space may be represented by any local basis like T-splines, hierarchical B-splines, or LR-splines. Secondly, the degree of the resulting patches may become large, depending on the degree of the reparameterization function. It might be beneficial to apply a degree reduction technique after the reconstruction, but this introduces additional approximation errors. Finally, the intersection curves should have a good parameterization since they play an essential role during the reconstruction. Therefore, it might be advisable to reparameterize the intersection curve, e.g., by its chord length, at the beginning of the overall procedure.

#### 5.2.4 Reconstruction by Triangular Bézier Splines

Another recent attempt has been proposed by Xia and Qian [314]. They employ triangular Bézier patches (36) to convert trimmed models to watertight representations. The convergence behavior of these splines has been assessed by these authors and co-workers in [315]. The conversion involves the following steps: (i) subdivision of all surfaces into tensor product Bézier patches, (ii) exact representation of non-trimmed patches by two Bézier triangles, (iii) knot cross-seeding between adjacent patches, (iv) approximation of the region along the trimming curve using Bézier triangles, and (v) substitution of the resulting control points of the approximate trimming curve by corresponding control points of the intersection curve in model space.

The first step can be easily accomplished by means of knot insertion. The second one is performed following Goldman and Filip [100]. In particular, a non-trimmed ten sor product patch with control points \(\boldsymbol{c}_{m, n}^{\square}\) can be converted to two triangular Bézier patches by where \(i+j+k=p+q\) and \(\binom{\alpha}{\beta}\) are binomial coefficients defined as

Equation (79) yields the control points \(\boldsymbol{c}_{i, j, k}^{\Delta}\) of one triangu lar patch using \(c_{m, n}^{\square}: 0 \leqslant m \leqslant p ; 0 \leqslant n \leqslant q\). The control points of the other triangular patch are obtained by revers ing the order of the original control points,

![Figure 46 Generation of conforming triangulations along the intersec- tion of two patches](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-46-p039.png)

*Figure 46 Generation of conforming triangulations along the intersec- tion of two patches: a definition of Bézier segments of the intersection curve ̂ C ( ̃ x) and the trimming curves C t 1 ( ̃ u) and C t 2 ( ̃ s). b Closest point projection to find corresponding points on the other curves. c Addition of Bézier segments due to the exchanged points and specification of associated triangular regions. Segments are marked by crosses, black points, and white points based on their origin. The offset between ̂ C ( ̃ x) and the images  ◦ C t 1 ( ̃ u) and  ◦ C t 2 ( ̃ s) shall emphasize that they do not coincide in model space. In b, arrows indicate the projections performed (a) Initial setting (b) Knot cross-seeding*

$$
\begin{align*} \boldsymbol{c}_{i, j, k}^{\triangle}= & \frac{1}{\binom{p+q}{q}} \sum_{m=0}^{i} \sum_{n=\max \{0, j-p+m\}}^{\min \{j, q-i+m\}} \boldsymbol{c}_{m, n}^{\square}\binom{i}{m}\binom{j}{n} \tag{79}\\ & \times\binom{ p+q-i-j}{p+n-m-j} \end{align*}
$$

i.e., \(c_{p-m, q-n}^{\square}: 0 \leqslant m \leqslant p ; 0 \leqslant n \leqslant q\). The degree of the resulting patches is determined by \(p+q\). It is emphasized that this transformation does not introduce an approxima tion error.

$$
\begin{equation*} \binom{\alpha}{\beta}:=\frac{\alpha!}{(\alpha-\beta)!\beta!} . \tag{80} \end{equation*}
$$

Next, the relationship of adjacent patches along the intersection is established. This is done similar to the knot cross-seeding procedure described in the previous subsec tion. Hence, we adopt this term here as well. Figure 46 summarizes the basic procedure. Firstly, the intersection curve \(\hat{\boldsymbol{C}}(\tilde{x})\) in model space and the trimming curves \(\boldsymbol{C}_{1}^{t}(\tilde{u})\) and \(\boldsymbol{C}_{2}^{t}(\tilde{s})\) are subdivided into Bézier segments at their knot values and intersections with the trimmed parameter space. Then, the endpoints of these segments are projected to the other curves and the corresponding parametric values are computed. In other words, the trimming curve are refined based on the knot information of the other trimming curve and the intersection curve in model space. Consequently, the resulting Bézier segments of a curve have correspond ing counterparts in the other curves. However, the distinct segments do not coincide in model space. At this point, the purpose of the knot cross-seeding is to obtain an aligned triangulation along the intersection. Triangular patches are specified within each trimmed surface so that one of their boundaries represents a Bézier segment.

The construction of these triangular Bézier patches which are arbitrarily located within the trimmed surface is performed accordingly to Lasser [182]. In general, a Bézier triangle \(T\) of degree \(\tilde{p}\) in a tensor product basis of a sur face \(\boldsymbol{R}(u, v)\) of degrees \(p\) and \(q\) yields a triangular patch \(\boldsymbol{S}^{\triangle}(r, s, t)\) of degree \(\tilde{p}(p+q)\). Xia and Qian [314] focus on the linear case, i.e., \(\tilde{p}=1\), meaning that the trimming curve where the control points of the surface \(\boldsymbol{R}(u, v)\) are used as initial values \(\boldsymbol{R}_{i, j}^{0,0}\). The construction in the \(v\)-direction is performed in an analogous manner. The superscripts \(a\) and \(b\) denote distinct steps of the recurrence relation in the \(u\) -direction and \(v\)-direction, respectively. Note that Eq. (82) is an adaptation of the de Casteljau algorithm that allows employing new parameter values \(u_{\mathbf{I}_{a}^{u}}\) in every iteration.

Likewise, the index tuples are given by \(\mathbf{I}^{v}=\mathbf{I}_{1}^{v}+\cdots+\mathbf{I}_{b}^{v}\) and \(\mathbf{I}^{u}=\mathbf{I}_{1}^{u}+\cdots+\mathbf{I}_{\alpha}^{u}\) with \(\alpha\) referring to the related super

![Figure 47 Illustration of the most common valid cutting patterns of a single knot span. The actual element type is determined by the direc- tion of the trimming curve. The crosses highlight the intersection points of the trimming curve with the element](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-47-p040.png)

*Figure 47 Illustration of the most common valid cutting patterns of a single knot span. The actual element type is determined by the direc- tion of the trimming curve. The crosses highlight the intersection points of the trimming curve with the element: Illustration of the most common valid cutting patterns of a single knot span. The actual element type is determined by the direction of the trimming curve. The crosses highlight the intersection points of the trimming curve with the element*

where each of these index triples consists of

$$
\begin{equation*} \boldsymbol{S}^{\triangle}(r, s, t)=\sum_{|\mathbf{I}|=p+q} B_{\mathbf{I}, p+q}(r, s, t) c_{\mathbf{I}}^{\triangle} \tag{81} \end{equation*}
$$

$$
\begin{align*} \boldsymbol{R}_{i, j}^{a, b}\left(u_{\mathbf{I}^{u}}^{a}, v_{\mathbf{I}^{v}}^{b}\right)= & \left(1-u_{\mathbf{I}_{a}^{u}}\right) \boldsymbol{R}_{i, j}^{a-1, b}\left(u_{\mathbf{I}^{u}}^{a-1}, v_{\mathbf{I}^{v}}^{b}\right) \tag{82}\\ & +u_{\mathbf{I}^{a} a} \boldsymbol{R}_{i+1, j}^{a-1, b}\left(u_{\mathbf{I}^{u}}^{a-1}, v_{\mathbf{I}^{v}}^{b}\right) \end{align*}
$$

This procedure is applied to cover the valid area of every trimmed Bézier surface by a set of triangular Bézier patches. Each Bézier segment of a trimming curve is represented by an edge of such a triangular patch. Finally, those edges are replaced by the corresponding Bézier segment of the intersection curve in model space. Since this substitution is carried out for all patches, a seamless join between adjacent surfaces is obtained. The approximation error introduced may be controlled by refining the patches along the trimming curves. | | | | | | It is worth noting that Xia and Qian [314] use their reconstruction procedure as an intermediate step in order to set up a volumetric parameterization of B-Rep models. The watertight triangular Bézier surface representation provides the starting point for a construction of volumetric Bézier tetrahedra.

$$
\begin{equation*} \boldsymbol{c}_{\mathbf{I}}^{\Delta}=\sum_{\mathbf{I}^{u}+\mathbf{I}^{v}=\mathbf{I}} \frac{1}{\binom{p+q}{\mathbf{I}}} \boldsymbol{R}_{0,0}^{p, q}\left(u_{\mathbf{I}^{u}}^{p}, v_{\mathbf{I}^{v}}^{q}\right) \tag{83} \end{equation*}
$$

![Figure 48 Trimmed parameter space and corresponding element types](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-48-p041.png)

*Figure 48 Trimmed parameter space and corresponding element types: 1 labels untrimmed knot spans whereas − 1 denotes knot spans which are outside of the computational domain. In case of trimmed knot spans the element type indicates the number of interior edges, i.e., 3, 4, or 5. The question mark indicates a special case. The intersections of the trimming curve with the parameter lines are highlighted by crosses*

### 5.3 Local Approaches

Local techniques employ a completely different philosophy than their global counterparts, that is, the geometry model is not modified but the analysis has to deal with all deficiencies of trimmed solid models. Thereby, the trimmed parameter space is used as background parameterization for the simulation while the trimming curves determine the domain of interest. Hence, the analyzed area is embedded in a regular grid of knot spans which consists of interior, exterior, and cut elements. The following subsections discuss (i) the detection of theses distinct element sets, (ii) the integration of cut elements, (iii) the treatment of multipatch geometries, and (iv) the stability of a trimmed basis.

#### 5.3.1 Element Detection

Before the actual analysis can be performed, the various element types and their position within the trimmed basis need to be identified. Interior elements are defined by nonzero knot spans that are completely within the valid domain and can be treated as in regular isogeometric analysis. Exterior ones, on the other hand, can be ignored since their entire support is outside of the domain of interest. Cut elements require special attention. One of the advantages of local approaches is that the cutting patterns of these elements are relatively simple compared to the complexity of the overall trimming curve. Figure 47 depicts topological cases of cut elements that are usually considered, e.g., [160, 161, 199, 202, 260]. It should be pointed out that other cases may exits as well, e.g., an element containing more than one trimming curve. These situations occur especially

![Figure 49 Detection of cut elements according to Kim et al. [ 160 , 161 ]](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-49-p041.png)

*Figure 49 Detection of cut elements according to Kim et al. [ 160 , 161 ]: a first assessment based on the inscribed and circumscribed circles of the element and if necessary, b further comparison of the signed distance of the element corners*

when the basis is very coarse. In general, the complexity of a trimming curve's topology within an element decreases as the fineness of the parameter space increases. Hence, (local) refinement is a common way to resolve invalid cutting patterns. This refinement may be performed for integration purpose only. Thus, no new knots are introduced, but the invalid element is subdivided in several valid integration regions. An alternative is to extend the valid cutting patterns as suggested by Wang et al. [307] or the construction of tailored integration rules for each cut element as proposed by Nagy and Benson [211]. However, the benefit of a restricted number of trimming cases facilitates the subsequent integration process.

Considering the situations shown in Fig. 47, cut elements have either 3, 4, or 5 edges, where one of them is a portion of the trimming curve. In this paper, we adapt the notation of Schmidt et al. [260] and label the type of cut elements by their number of edges. Interior and exterior elements are referred to as elements of type 1 and-1, respectively. Figure 48 illustrates a trimmed parameter space and the related element types. Note that the knot span in the upper right corner is an example of an invalid case since smooth element edges are usually assumed for the numerical integration. Possible strategies to deal with this element include subdivision into several integration regions, treatment as a type 4 element with two curved edges, or knot refinement through the kink of the curve. In general, kinks and straight trimming curves that are aligned with parameter lines are usual suspects for introducing special cases.

The portions of the trimming curve which are within each element have to be determined in order to get a proper description of cut knot spans. In particular, the intersections of the parameter grid with the trimming curve \(\boldsymbol{C}^{t}(\tilde{u})\) are required, together with the corresponding parametric values \(\tilde{u}^{+}\). The overall element detection task consists of the classification of knot span with respect to the trimming

![Figure 50 Starting point for the separation of interior and exterior ele- ments following the procedure of Schmidt et al. [ 260 ]. White knot spans are not classified yet. The arrow indicates the direction of the trimming curve](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-50-p042.png)

*Figure 50 Starting point for the separation of interior and exterior ele- ments following the procedure of Schmidt et al. [ 260 ]. White knot spans are not classified yet. The arrow indicates the direction of the trimming curve: Starting point for the separation of interior and exterior elements following the procedure of Schmidt et al. [260]. White knot spans are not classified yet. The arrow indicates the direction of the trimming curve*

curves and the determination of trimming curve portions related to cut elements.

Kim et al. [160, 161] and Schmidt et al. [260] presented two different algorithmic solutions for the element detection problem. The procedure suggested by the former can be summarized by:

- (i) Compute the minimal signed distance d i, j of the center of each non-zero knot span to all trimming curves to separate interior and exterior elements.

- (ii) Identify cut elements by comparing | | | d i, j | | | with the radii r in i, j and r out i, j of the inscribed and circumscribed circles of the element. If r in i, j ⩽ | | | d i, j | | | < r out i, j, the signed distance of the element corner nodes to the trimming curve are computed and compared as well.

- (iii) Compute intersection points for each element cut by the trimming curve.

Both cases of the second step which specify cut elements are illustrated in Fig. 49. In Fig. 49a, the distance of the element's center to the trimming curve is smaller than the radius of the inscribed circle, whereas in Fig. 49b, the cut element is identified since the signed distances of its corner nodes are positive and negative.

On the other hand, Schmidt et al. [260] recommend to label all non-zero knot spans as interior elements as starting point for the following procedure:

- (i) determine all intersection points of the trimming curve and the grid produced by the tensor product of the knot vectors and sort them in a nondecreasing order with respect to the related values ̃ u + .

- (ii) Assign the element type of cut elements based on the position of successive intersection points.

- (iii) Detect exterior elements based on their position relative to the cut elements.

On this basis, it may be concluded that the present approaches tackle the problem from two different directions. The former puts the element type in the focus with a subsequent calculation of the intersections of cut elements with the trimming curve, whereas the latter computes all intersections and derives the type of the elements afterwards. In general, the most important property of an element detection algorithm is its robustness since it hardly affects the overall efficiency of the simulation. Both approaches require a robust implementation of the curve-to-grid intersection computation. The Bézier clipping technique described in Sect. 3.5.2 could be used. The treatment of invalid cutting patterns applies also to both algorithms and depends on the subsequent integration procedure. The main difference between the approaches is that the former relies on a robust implementation of a point projection algorithm in order to determine the signed distance of a point to the trimming curve, while the latter requires a robust technique for detecting exterior elements based on the intersection information. There is perhaps no objective way to prefer one scheme to the other, but we would like to share our experiences with both schemes by mentioning some possible pitfalls in the following paragraphs.

The first point addresses the detection of exterior elements based on their relative position to cut elements. The starting point is illustrated in Fig. 50. Elements of type 1 are changed to type-1 if they are adjacent to the exterior nodes of cut and exterior elements. The search for adjacent elements can be performed in an incremental manner as it is done in 'flood fill' algorithms, which are commonly used in graphics software [286]. It should, however, be emphasized that intersected grid nodes need special attention since the search for adjacent elements might propagate at these points to the valid domain. Furthermore, a proper treatment of zero knot spans is required.

The other note is concerned with the calculation of the signed distance to trimming curves. The shortest distance \(d_{t}\) of a test point \(\boldsymbol{x}_{t}\) to a trimming curve \(\boldsymbol{C}^{t}(\tilde{u})\) is defined as

![Figure 51 Determination of the correct sign in case of multiple trim- ming curves C t i ( ̃ u ) which describe an acute angle. The area which returns ambiguous signs is indicated in gray . (Courtesy of Jakob W. Steidl)](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-51-p043.png)

*Figure 51 Determination of the correct sign in case of multiple trim- ming curves C t i ( ̃ u ) which describe an acute angle. The area which returns ambiguous signs is indicated in gray . (Courtesy of Jakob W. Steidl): Determination of the correct sign in case of multiple trimming curves C t i ( ̃ u) which describe an acute angle. The area which returns ambiguous signs is indicated in gray. (Courtesy of Jakob W. Steidl)*

A Newton-Raphson iteration scheme is employed to determine the parametric values \(\tilde{u}^{*}\) [192, 230]. The correspond ing sign \(s\) indicates on which side of \(\boldsymbol{C}^{t}(\tilde{u})\) the point \(\boldsymbol{x}_{t}\) is located. It can be computed by the cross product of the tan gent vector \(\boldsymbol{t}=\left(t_{u}, t_{v}\right)^{\top}\) at the projected point \(\boldsymbol{x}_{p}=\boldsymbol{C}^{t}\left(\tilde{u}^{*}\right)\)

In case of non-smooth trimming curves, more than one minimum might exist as pointed out in [287]. From a practical point of view this is only relevant if these minima have different signs. Such cases appear in the vicinity of sharp corners as shown in Fig. 51. The correct sign can be determined by the projected distance calculated by the dot product

$$
s=\left\{\begin{array}{r} 1 \text { if } \kappa_{1}>\kappa_{2}, \tag{93}\\ -1 \text { otherwise, } \end{array}\right.
$$

$$
\begin{equation*} G(u, v):=\sqrt{\operatorname{det}\left(\mathbf{J}_{\mathcal{X}}^{\mathrm{T}}(u, v) \mathbf{J}_{\mathcal{X}}(u, v)\right)}, \tag{96} \end{equation*}
$$

where \(\kappa_{1}\) denotes the curvature of the curve that ends at the corner.

$$
\begin{equation*} J_{\hat{\tau}}\left(\xi_{g}, \eta_{g}\right)=\operatorname{det}\left(\mathbf{J}\left(\xi_{g}, \eta_{g}\right)\right), \tag{97} \end{equation*}
$$

#### 5.3.2 Integration

Various strategies to integrate cut elements \(\tilde{\tau} \in \mathcal{A}^{\mathrm{v}}\) are out lined in this subsection. In general, numerical integration is performed using conventional Gauss-Legendre quadrature. The integral over each \(\tilde{\tau}\)

$$
\begin{equation*} d_{t}=\min \left\{\left\|\boldsymbol{C}^{t}(\tilde{u})-\boldsymbol{x}_{t}\right\|\right\}=\left\|\boldsymbol{C}^{t}\left(\tilde{u}^{*}\right)-\boldsymbol{x}_{t}\right\| . \tag{89} \end{equation*}
$$

![Figure 52 Distribution of quadrature points indicated by black points over a regular patch](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-52-p043.png)

*Figure 52 Distribution of quadrature points indicated by black points over a regular patch: Distribution of quadrature points indicated by black points over a regular patch*

$$
\begin{equation*} I_{\tilde{\tau}}=\int_{\Omega_{\tilde{v}}} f(\boldsymbol{x}) \mathrm{d} \Omega_{\tilde{\tau}} \tag{94} \end{equation*}
$$

is substituted by a weighted sum of point evaluations

$$
\begin{equation*} s=t_{u} d_{v}-t_{v} d_{u} . \tag{90} \end{equation*}
$$

$$
\begin{equation*} I_{\tilde{\tau}} \approx \sum_{g=1}^{n} f\left(\boldsymbol{y}_{g}\right) G\left(u_{g}, v_{g}\right) J_{\hat{\tau}}\left(\xi_{g}, \eta_{g}\right) w_{g} . \tag{95} \end{equation*}
$$

The related quadrature points \(\boldsymbol{y}\) and the correspond ing weights \(w\) are specified in the reference element \(\grave{\tau}=[-1,1]^{2}\). The coordinates for the pointwise evalu ation of the integrand \(f\) are determined by the inte gral transformation \(\mathcal{X}_{r}(\xi, \eta): \mathbb{R}^{2} \mapsto \mathbb{R}^{2}\) from \(\grave{\tau}\) to \(\tilde{\tau}\) and the geometrical mapping \(\mathcal{X}(u, v): \mathbb{R}^{2} \mapsto \mathbb{R}^{3}\), i.e., \(\boldsymbol{y}_{g}=\mathcal{X}\left(u_{g}, v_{g}\right)=\mathcal{X}\left(\mathcal{X}_{r}\left(\xi_{g}, \eta_{g}\right)\right)\) as illustrated in

$$
\begin{align*} & e_{i}=v \cdot \boldsymbol{t}_{i}, \quad i=1,2 \tag{91}\\ & s=\operatorname{sign}\left\{\min \left\{e_{1}, e_{2}\right\}\right\} \tag{92} \end{align*}
$$

is evaluated with respect to the reference coordinates \(\xi_{g}\) and \(\eta_{g}\) of the integration point \(\boldsymbol{y}_{g}\). The definition of the inte gral transformation \(\mathcal{X}_{r}\) and the related \(J_{\tilde{\tau}}\) is straightforward in case of regular elements. However, the domain of cut elements is more complex and thus, the definition of \(\mathcal{X}_{r}\) is more involved.

Numerical integration of cut elements is required in various simulation schemes. Besides the analysis of trimmed geometries, it is also needed in the context of fictitious domain methods and the extended finite element method. There are numerous approaches and a vast body of literature proposing strategies to specify a proper integration of 𝜏 ̃ . It may be performed so that the trimming curve is taken into account in an exact or approximate manner. In this paper, the main focus is on techniques presented in the context of trimmed NURBS objects. They can be broadly classified into the following categories: (i) local reconstruction, (ii) approximate treatment, and (iii) exact treatment. The former is performed in model space, while the others operate in the parameter space in general.

5.3.2.1 Local Reconstruction Schmidt et al. [260] sug gested to perform the adjustment of the integration region by a local reconstruction of the trimmed patch. Therefore, each cut element in the model space \(\tau\) is remodeled as a single reconstruction patch \(\hat{\tau}\). In particular, \(\hat{\tau}\) is specified as a Bézier patch with degrees \(\hat{p} \geqslant p\) and \(\hat{q} \geqslant q\), where \(p\) and \(q\) refer to the degrees of the origin surface. The key idea is to represent \(\hat{\tau}\) in terms of the original control points of \(\tau\). A transformation matrix \(\mathbf{T}\) provides the relationship between the control points of the original and reconstructed patch. It can be computed by means of a least squares approximation where the system of equations is given by

This equation consists of representing the (unknown) control points of \(\hat{\tau}\), the (known) control points of \(\tau\), and a set of sampling points \(\boldsymbol{x}^{s}\) interpo lated by both patches. The total number of control points involved is determined by the number of non-zero basis

![Figure 53 Approximation of the cut element by a polytope ̃𝜌 . The con- trol points of the trimming curve are marked by circles](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-53-p044.png)

*Figure 53 Approximation of the cut element by a polytope ̃𝜌 . The con- trol points of the trimming curve are marked by circles: Approximation of the cut element by a polytope ̃𝜌 . The control points of the trimming curve are marked by circles*

$$
\mathbf{B}=\left[\begin{array}{ccc} B_{0, p}\left(u_{0}^{s}\right) B_{0, q}\left(v_{0}^{s}\right) & \cdots & B_{p, p}\left(u_{0}^{s}\right) B_{q, q}\left(v_{0}^{s}\right) \tag{101}\\ \vdots & \ddots & \vdots \\ B_{0, p}\left(u_{l}^{s}\right) B_{0, q}\left(v_{l}^{s}\right) & \cdots & B_{p, p}\left(u_{l}^{s}\right) B_{q, q}\left(v_{l}^{s}\right) \end{array}\right],
$$

Note that a correlation between the parametric values has to be established so that \(\boldsymbol{x}_{i}^{s}=\tau\left(u_{i}^{s}, v_{i}^{s}\right)=\hat{\tau}\left(\hat{u}_{i}^{s}, \hat{v}_{i}^{s}\right), i=0, \ldots, l\).

$$
\begin{equation*} \hat{\mathbf{B}}^{\top} \hat{\mathbf{B}} \hat{\mathbf{P}}=\hat{\mathbf{B}}^{\top} \mathbf{S}=\hat{\mathbf{B}}^{\top} \mathbf{B P} \tag{102} \end{equation*}
$$

which yields the definition of the transformation matrix

$$
\begin{equation*} \hat{\mathbf{B}} \hat{\mathbf{P}}=\mathbf{S}=\mathbf{B P} \tag{98} \end{equation*}
$$

$$
\begin{equation*} \mathbf{T}=\left(\hat{\mathbf{B}}^{\mathrm{T}} \hat{\mathbf{B}}\right)^{-1} \hat{\mathbf{B}}^{\mathrm{T}} \mathbf{B} \tag{103} \end{equation*}
$$

and the relation between the control points

$$
\hat{\mathbf{P}}=\left[\begin{array}{c} \hat{c}_{0} \tag{99}\\ \vdots \\ \hat{c}_{\hat{n}-1} \end{array}\right], \quad \mathbf{P}=\left[\begin{array}{c} \boldsymbol{c}_{0} \\ \vdots \\ \boldsymbol{c}_{n-1} \end{array}\right], \quad \text { and } \quad \mathbf{S}=\left[\begin{array}{c} \boldsymbol{x}_{0}^{s} \\ \vdots \\ \boldsymbol{x}_{l}^{s} \end{array}\right]
$$

$$
\begin{equation*} \hat{\mathbf{P}}=\mathbf{T P} . \tag{104} \end{equation*}
$$

As a result, numerical integration can be performed based on the regular reconstruction patch \(\hat{\tau}\) and the sim ple mapping of the regular integration can be applied. The values obtained are distributed to the control points of the original patch using the transformation matrix \(\mathbf{T}\). For more details, the interested reader is referred to [260].

This procedure can be directly applied to cut elements of types 3 and 4 as specified in Sect. 5.3.1. Type 5 elements may be subdivided into two four-sided regions. A drawback of the local reconstruction scheme is that it introduces an additional approximation error since the system of equations (102) cannot be solved exactly. Moreover, the stability of the computation of the transformation matrix might be affected if only a very small region of a cut element needs to be reconstructed.

$$
\hat{\mathbf{B}}=\left[\begin{array}{ccc} \hat{B}_{0, \hat{p}}\left(\hat{u}_{0}^{s}\right) \hat{B}_{0, \hat{q}}\left(\hat{v}_{0}^{s}\right) & \cdots & \hat{B}_{\hat{p}, \hat{p}}\left(\hat{u}_{0}^{s}\right) \hat{B}_{\hat{q}, \hat{q}}\left(\hat{v}_{0}^{s}\right) \tag{100}\\ \vdots & \ddots & \vdots \\ \hat{B}_{0, \hat{p}}\left(\hat{u}_{l}^{s}\right) \hat{B}_{0, \hat{q}}\left(\hat{v}_{l}^{s}\right) & \cdots & \hat{B}_{\hat{p}, \hat{p}}\left(\hat{u}_{l}^{s}\right) \hat{B}_{\hat{q}, \hat{q}}\left(\hat{v}_{l}^{s}\right) \end{array}\right]
$$

5.3.2.2 Approximated Trimming curve The following two schemes approximate the trimming curve \(\boldsymbol{C}^{t}\) in order to define proper integration points within the parameter space.

$$
\begin{equation*} \sum_{i=1}^{m} f_{j}\left(u_{i}, v_{i}\right) w_{i}=\int_{\Omega_{\tilde{p}}} f_{j}(u, v) \mathrm{d} \Omega_{\tilde{\rho}}, \quad j=1, \ldots, n \tag{105} \end{equation*}
$$

![Figure 54 Sub-cell structure of a single cut element](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-54-p045.png)

*Figure 54 Sub-cell structure of a single cut element: a conventional approach with quadrature points distributed within the valid (black points) and exterior (green points) domain and b reduced approach integrating over the whole element (orange points) and the valid domain (black points). The sub-cells are indicated by dashed lines. (Color figure online)*

One uses a linear approximation of \(\boldsymbol{C}^{t}\) to set up a tailored integration rule, whereas the other applies an adaptive sub division to approximate the domain of the cut element.

A tailored integration rule can be established for each cut element \(\tilde{\tau}\) as proposed in [211, 305, 306]. The control polygon \({ }^{20}\) of \(\boldsymbol{C}^{t}\) is used to represent \(\tilde{\tau}\) by a polytope \(\tilde{\rho}\) as shown in Fig. 53. The integral over \(\tilde{\rho}\) can be reduced to a sum of line integrals over the edges of \(\tilde{\rho}\) using Lasserre's theorems [183]. Therefore, the integration domain \(\Omega_{\tilde{\rho}}\) has to be convex. Thus, a preprocessing step is applied to rep resent non-convex regions by a combination of convex ones. The line integrals provide reference solutions for the

$$
\begin{equation*} I^{c}=\sum_{i=1}^{I} I_{\tilde{\tau}_{i}^{\mathrm{V}}}^{\mathrm{V}}\left(\alpha^{\mathrm{v}}\right)+\sum_{j=1}^{J} I_{\tilde{\tau}_{j}^{\boxplus}}^{-}\left(\alpha^{-}\right) . \tag{106} \end{equation*}
$$

20 To be precise, it is suggested to use the control points of the intersection curves in the model space and to apply point inversion to determine their location in the parameter space. However, there is no particular reason why the control polygon of the trimming curve cannot be used directly.

A completely different strategy for the integration of cut elements in based on adaptive subdivision. Researchers who developed the finite cell method applied this technique to trimmed geometries [107, 239, 253, 254]. The basic idea is to use a composed Gauss quadrature that aggregates inte gration points along the trimming curve. A cut element \(\tilde{\tau}\) is decomposed into axis-aligned sub-cells \(\tilde{\tau}^{\boxplus}\) based on a tree structure, i.e., a quadtree in two dimensions. Starting from the initial cut element, each sub-cell is further subdivided into equally spaced sub-cells if it contains the trimming curve as displayed in Fig. 54a. This recursive procedure is performed up to a user-defined maximal depth. Following the spirit of fictitious domain methods the integral \(I^{c}\) over the complete element is defined as

The factors \(I_{\tilde{\tau}_{i}^{\boxplus}}^{\mathrm{V}}\) and \(I_{\tilde{\tau}_{j}^{\boxplus}}^{-}\)are the integrals over the valid domain \(\mathcal{A}^{\mathrm{v}}\) and the complementary exterior domain \(\mathcal{A}^{-}\), respectively. Integration points in the interior of \(\mathcal{A}^{\mathrm{v}}\) are multiplied by \(\alpha^{\mathrm{v}}=1\), whereas exterior integration points are multiplied by a value that is almost zero, e.g., \(\alpha^{-}=10^{-14}\) as suggested in [253]. The integration pro cedure can be improved with respect to the number of quadrature points by where \(I_{\tilde{\tilde{\tau}}}^{-}\left(\alpha^{-}\right)\)represents the integral over the whole cut ele ment without taken the trimming curve into account. The integration over the valid domain is performed as before by the composite quadrature, yet with another weighting fac tor, i.e., \(\left(\alpha^{\mathrm{v}}-\alpha^{-}\right)\). Such an improved sub-cell integration is illustrated in Fig. 54b. The key features of this approach are its simplicity and generality. The definition of integral transformation \(\mathcal{X}_{r}\) and its Jacobian is straightforward, due to the axis-aligned shape of the sub-cells. Again, all cutting patterns (includ ing invalid ones) can be addressed with a single algorithm. Moreover, the algorithm can be easily extended to higher dimensions. The downside is that the trimming curve is only approximated. Consequently, the integration region is not represented exactly and an additional approxima tion error is introduced. In fact, the accuracy of the integral ceases at a certain threshold [173,175]. This threshold may be improved by the subdivision depth, but a fine resolution of sub-cells results in a vast number of quadrature points. Further, refined sub-cells do not converge to the trimming curve in contrast to the previous approach. One of the great successes of the finite cell method was the demonstrated ability to achieve higher rates of convergence for higher order elements and splines, and even exponential rates in the context of the \(p\)-method.

##### 5.3.2.3 Exact Trimming Curve

The following techniques focus on defining a proper mapping  r from the reference element ̀ 𝜏 to the cut element 𝜏 ̃ ∈  v so that the trimming curve is exactly represented. Depending on the cutting pattern, 𝜏 ̃ may be represented by a disjointed set of integration regions ̃ 𝜏 ⊡ such that

In contrast to the sub-cells of the previous scheme, the regions \(\tilde{\tau}^{\square}\) are not aligned with the axes of the parameter space and at least one \(\tilde{\tau}^{\square}\) has an edge which is described by the portion of the trimming curve \(\boldsymbol{C}^{t}\) within \(\tilde{\tau}\). the portion of the trimming curve \(\boldsymbol{C}^{t}\) within \(\tilde{\tau}\). There are various ways to specify \(\mathcal{X}_{r}\). Ruled surface (26) and Coons patch (35) interpolation may be applied, where the portion of the trimming curve within \(\tilde{\tau}\) is considered

$$
\begin{align*} \phi(\tilde{u}) & =\mathcal{X}_{s, t}^{-1} \cdot \boldsymbol{C}^{t}(\tilde{u}) \\ & =\left[\begin{array}{ll} x_{3}^{\Delta}-x_{2}^{\Delta} & x_{1}^{\Delta}-x_{2}^{\Delta} \end{array}\right]^{-1}\left(C^{t}(\tilde{u})-x_{2}^{\Delta}\right) \tag{111} \end{align*}
$$

for the construction [199, 307]. An example of local ruled surface mappings for various element types are shown in Fig. 55a. These methods may be interpreted as local coun terparts of the global reconstruction schemes presented in Sects. 5.2.1 and 5.2.2. It is worth noting that approaches based on the blending function method [95, 173, 174] can be included into this category, because this method also employs a transfinite mapping [103]. In the nested Jaco bian approach, integral transformation is also defined by a local NURBS surface combined with a nested subdivision [38, 227]. Thus, \(\mathcal{X}_{r}\) consists of the local surface mapping and an additional transformation to the subregion. A cor responding distribution of quadrature points is shown in Fig. 55b. In contrast to both previous references, i.e., [199, 307], type 5 elements are not decomposed into three trian gular ones, but a bisection of the knot span is performed. Recently, an adaptive Gaussian integration procedure has been proposed [37]. This variation of the nested Jacobian approach defines the local surface parameterization within the reference space instead of the trimmed parameter space as illustrated in Fig. 55c. Therefore, the trimming curve is transformed to the reference space by scaling and rota tion. The integration points and their weights are adapted by scaling the \(\eta\)-direction such that the points are located within the region described by the transformed trimming curve. The motivation for the adaptive Gaussian integration procedure is to treat the various cutting patterns by a single approach.

Another very common strategy is to adopt the integration scheme developed in the context of the NURBS-enhanced finite element method [147, 148, 160, 161, 272, 273]. Using this scheme, every cut element is subdivided into a set of triangles. Those triangles that only consist of straight edges are subjected to conventional integration rules for linear triangles. The other triangles are treated by a series of mappings that take the curved edge into account

Figure 55d displays the components of this series. Suppose the corner nodes of the triangle in the trimmed parameter space are labeled \(\boldsymbol{x}_{1}^{\Delta}\) to \(\boldsymbol{x}_{3}^{\Delta}\), where the beginning and the end of the trimming curve portion within the considered trian gle are denoted by \(\boldsymbol{x}_{2}^{\Delta}\) and \(\boldsymbol{x}_{3}^{\Delta}\), respectively. The transforma tion \(\mathcal{X}_{s, t}: \boldsymbol{x}(s, t) \mapsto \boldsymbol{x}(u, v)\) describes the mapping of a linear three node element

$$
\begin{equation*} \tilde{\tau}=\bigcup_{i=1}^{I} \tilde{\tau}_{i}^{\square} \tag{108} \end{equation*}
$$

In order to address the curved edge, the trimming curve is transformed into the s, t-coordinate system by

![Figure 55 Distribution of quadrature points due to various approaches which represent the trimming curve exactly. Dashed lines indicate a subdi- vision of a cut element into integration regions](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-55-p047.png)

*Figure 55 Distribution of quadrature points due to various approaches which represent the trimming curve exactly. Dashed lines indicate a subdi- vision of a cut element into integration regions: Distribution of quadrature points due to various approaches which represent the trimming curve exactly. Dashed lines indicate a subdivision of a cut element into integration regions*

- (c) Adaptive Gaussian integration procedure

- (a) Local ruled surface mapping

- (b) Nested Jacobian approach

The next mapping \(\mathcal{X}_{\tilde{u}, \zeta}: \boldsymbol{x}(\tilde{u}, \zeta) \mapsto \boldsymbol{x}(s, t)\) converts the tri angular domain into a rectangular one which possesses straight edges only. It is given by

Finally, the transformation \(\mathcal{X}_{\xi, \eta}: \boldsymbol{x}(\xi, \eta) \mapsto \boldsymbol{x}(\tilde{u}, \zeta)\) of the reference space \([-1,1]^{2}\) to the rectangular region is per formed by

$$
\mathcal{X}_{\xi, \eta}:=\left\{\begin{array}{l} \tilde{u}=\frac{\xi}{2}\left(\tilde{u}_{e}-\tilde{u}_{b}\right)+\frac{1}{2}\left(\tilde{u}_{e}+\tilde{u}_{b}\right) \tag{113}\\ \zeta=\frac{\eta}{2}+\frac{1}{2} \end{array}\right.
$$

$$
\mathbf{J}_{s, t}=\left[\begin{array}{cc} u_{3}^{\Delta}-u_{2}^{\Delta} & u_{3}^{\Delta}-v_{2}^{\Delta} \tag{115}\\ u_{1}^{\Delta}-u_{2}^{\Delta} & v_{1}^{\Delta}-v_{2}^{\Delta} \end{array}\right],
$$

$$
\mathbf{J}_{\tilde{u}, \zeta}=\left[\begin{array}{cc} \frac{\partial \phi_{s}(\tilde{u})}{\partial \tilde{u}}(1-\varsigma) & \frac{\partial \phi_{t}(\tilde{u})}{\partial \tilde{u}}(1-\varsigma) \tag{116}\\ -\phi_{s}(\tilde{u}) & 1-\phi_{t}(\tilde{u}) \end{array}\right],
$$

where \(\tilde{u}_{b}\) and \(\tilde{u}_{e}\) are the parametric values of the beginning and the end of the trimming curve portion within the trian gle, i.e., \(\boldsymbol{C}^{t}\left(\tilde{u}_{b}\right)=\boldsymbol{x}_{2}^{\Delta}\) and \(\boldsymbol{C}^{t}\left(\tilde{u}_{e}\right)=\boldsymbol{x}_{3}^{\Delta}\). The Jacobian deter minant of the overall mapping \(\mathcal{X}_{r}\) is determined by

$$
\mathcal{X}_{\tilde{u}, \zeta}:=\left\{\begin{align*} s & =\phi_{s}(\tilde{u})(1-\zeta) \tag{112}\\ t & =\phi_{t}(\tilde{u})(1-\zeta)+\zeta . \end{align*}\right.
$$

$$
\begin{equation*} J_{\tilde{t}}=\operatorname{det}\left(\mathbf{J}_{s, t}\right) \operatorname{det}\left(\mathbf{J}_{\tilde{u}, \zeta}\right) \operatorname{det}\left(\mathbf{J}_{\xi, \eta}\right), \tag{114} \end{equation*}
$$

![Figure 56 Comparison of the distribution of Gauss points within a cut element of type 3 based on the NURBS enhanced FEM mapping ( circles ) and ruled surface parameterization ( crosses ). The trimming curve is described by either a a B-spline curve or b a NURBS curve](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-56-p048.png)

*Figure 56 Comparison of the distribution of Gauss points within a cut element of type 3 based on the NURBS enhanced FEM mapping ( circles ) and ruled surface parameterization ( crosses ). The trimming curve is described by either a a B-spline curve or b a NURBS curve: Comparison of the distribution of Gauss points within a cut element of type 3 based on the NURBS enhanced FEM mapping (circles) and ruled surface parameterization (crosses). The trimming curve is described by either a a B-spline curve or b a NURBS curve*

$$
\mathbf{J}_{\xi, \eta}=\left[\begin{array}{cc} \frac{1}{2}\left(\tilde{u}_{e}-\tilde{u}_{b}\right) & 0 \tag{117}\\ 0 & \frac{1}{2} \end{array}\right] .
$$

The coefficients \(u_{i}^{\Delta}\) and \(v_{i}^{\Delta}\) refer to the coordinates of the corner nodes \(\boldsymbol{x}_{i}^{\Delta}\) and the derivative of the transformed trim ming curve is calculated by

$$
\frac{\partial \phi(\tilde{u})}{\partial \tilde{u}}=\left[\begin{array}{ll} \boldsymbol{x}_{3}^{\Delta}-\boldsymbol{x}_{2}^{\Delta} & \boldsymbol{x}_{1}^{\Delta}-\boldsymbol{x}_{2}^{\Delta} \tag{118} \end{array}\right]^{-1}\left(\frac{\partial \boldsymbol{C}^{t}(\tilde{u})}{\partial \tilde{u}}\right) .
$$

The various integration schemes are summarized in Fig.55. Their common and most essential feature is that the integration region is exactly represented. The main dif ference between the strategies is the partitioning of a cut element \(\tilde{\tau}\) into integration regions \(\tilde{\tau}^{\square}\). In fact, the series of mappings (109) shown in Fig. 55d yields the same distri bution of quadrature points over a triangular element as a ruled surface interpolation (26) illustrated in Fig. 55a, if the trimming curve is a B-spline curve. In case of NURBS curves, on the other hand, different distributions are obtained. These two cases are compared in Fig. 56.

In general, it seems that good results can be obtained with either of these concepts, especially for moderate degrees. However, it has been demonstrated that the properties of coordinate mappings and the corresponding placement of interior nodes is crucial for the convergence behavior of conventional higher degree (p > 3) finite elements [216]. With this in mind, additional research might be useful to assess the quality of the mapping schemes presented with respect to their performance for higher degree.

#### 5.3.3 Multipatch Geometries

A robust treatment of multiple patches is the most challenging part of analyzing trimmed geometries. While single patch analysis can exploit the benefits of trimmed

5.3.3.1 Weak Coupling Weak enforcement of constraints is a common problem in computational mechanics, see e.g., [138, 166, 312] and the references cited therein. Such techniques are required in several contexts like mesh-independent imposing of essential boundary conditions and domain decomposition methods. The latter covers a versatile field of applications including contact problems, parallelization, and coupling of subdomains described by different physics or non-conforming discretizations. Numerous approaches have been developed and each one possesses different benefits and disadvantages. The most popular schemes are based on Lagrange multipliers [12], the penalty method [13, 139], or Nitsche's method [112, 215]. These methods are separated by a fine line: the penalty method may be viewed as an approximation of the Lagrange multiplier method [139]. Furthermore, the Nitsche method may be referred to as a consistent penalty method [252]. In addition, the close relationship of the Nitsche method to the stabilized Lagrange multiplier method [17, 18] has been outlined in [288].

The use of Lagrange multipliers is a very general way to enforce constraints to a system of equations which is applicable to all kinds of problems. Following Huerta et al. [138] the main disadvantages are: (i) the system of equations increases due to the Lagrange multipliers which are incorporated as additional degrees of freedom, (ii) the resulting system is not positive definite, and (iii) the introduction of a separate field for the Lagrange multipliers yields a saddle-point problem which must satisfy a stability condition known as the inf-sup or Babuška-Brezzi condition. In order to fulfill the last point, the interpolation fields of the unknowns and the Lagrange multipliers must be coordinated, which is not a trivial task, examples of choices for the interpolation functions can be found in [139].

The penalty method is easy to implement and avoids the problems mentioned above. However, uniform convergence to the solution can only be guaranteed if the applied penalty parameter increases as the mesh is refined [7]. This is crucial since the system matrix becomes ill-conditioned when the penalty parameter gets large. Usually, a fixed parameter value is chosen and as a result, the quality of the approximation cannot be improved below a certain error.

Nitsche's method introduces a penalty term too, but it is considerably smaller than in the penalty method [80,

![Figure 57 Closest point projections of a slave patch to a master patch. The lines on the surfaces represent the grid of the underlying param- eter space. The intersections of these lines with the trimming curves are illustrated by white and black dots for the slave and master patch, respectively. The projections themselves are indicated by arrows](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-57-p049.png)

*Figure 57 Closest point projections of a slave patch to a master patch. The lines on the surfaces represent the grid of the underlying param- eter space. The intersections of these lines with the trimming curves are illustrated by white and black dots for the slave and master patch, respectively. The projections themselves are indicated by arrows: Closest point projections of a slave patch to a master patch. The lines on the surfaces represent the grid of the underlying parameter space. The intersections of these lines with the trimming curves are illustrated by white and black dots for the slave and master patch, respectively. The projections themselves are indicated by arrows*

254]. According to Huerta et al. [138] the only problem of Nitsche's method is that it is not as general as the other procedure. Thus, it is not straightforward to provide an implementation for some problem types.

These techniques have been successfully applied to various isogeometric analysis applications, e.g. [23, 24, 39, 80, 81, 163, 213]. A comparison of the three schemes can be found in [7]. Also in the context of coupling trimmed patches, the Lagrange multiplier method [307], the penalty method [37, 38], and the Nitsche method [107, 164, 254] have been successfully applied already. In none of these publications, the surface type motivated the choice of the weak coupling strategy. In other words, trimmed patches do not introduce additional arguments to prefer one approach to the other. Nevertheless, it is important to emphasize again that trimming curves of adjacent patches do not describe the same curve in model space. Thus, adjacent patches have non-conforming parameterizations as well as gaps and overlaps along their intersection.

5.3.3.2 Linking of Degrees of Freedom Breitenberger et al. [38] presented a procedure that is able to deal with complex design models and it has been discussed in more detail in the related thesis [37]. In addition to a weak coupling formulation, trimming curves of adjacent patches are connected by so-called edge elements that contain the required topological information. To be precise, the trimming curves are treated by a master-slave concept where points of the slave curve are mapped to the master curve. These points are the intersections of the slave trimming curve with the grid lines of its own parameter space. The mapping to the master curve is performed in model space by means of a point inversion algorithm [192, 230]. The algorithm is usually carried out by a Newton-Raphson scheme and provides the closest projection of a point to a curve as shown in Fig. 57. In addition, the related parametric values of the master curve are provided by the point inversion scheme. The accumulation of these values and the original grid intersections of the master curve define a set of integration regions. Within each region, quadrature points are specified and the corresponding points of the slave curve can again be computed by the point inversion algorithm. To sum up, the relation of two related trimming curves is established by an iterative procedure in model space which computes the shortest distance of a point defined by one curve to the other curve. This is indeed the same concept as for the knot cross-seeding procedures presented in Sect. 5.2 in the context of global approaches. In theory, this is a straightforward task, but its robust implementation is challenging and crucial for the overall performance of an analysis.

$$
\begin{equation*} d_{1}=\left|u_{T i p}(f)-u_{r e f}\right|, \tag{119} \end{equation*}
$$

In the following we would like to highlight the impor tance of a robust association of adjacent patches by show ing an example presented in [37, 38]. The basic setting of the problem is shown in Fig. 58a. This benchmark for geo metric nonlinear shell analysis describes a cantilever that is subjected to an end moment. If the maximal moment \(M_{\text {max }}\) is applied, the cantilever deforms to a closed circular ring. Figure 58b illustrates the numerical solution of this problem for various parameterizations. Note the different level of complexity along the edges of adjacent patches. It clearly demonstrates the vast diversity of situations that my occur in case of multipatch geometries even if they repre sent the same geometry.

Another important aspect studied by this example is the influence of the gap and overlap size between patches. Con sider the geometrical discretization illustrated in Fig. 59. A gap-overlap function \(f\) is introduced to specify a user defined inaccuracy along the curved intersection. Posi tive and negative values of \(f\) represent gaps and overlaps, respectively. The trimming curves are linked by the point inversion algorithm as described before. The resulting ver tical displacements at the cantilever's end \(u_{\text {Tip }}\) of representations with different \(f\) are related to a reference solution \(u_{\text {ref }}\) obtained with \(f=0\). The difference is calculated by and the related results are summarized in Fig. 60. Based on the corresponding graph, it can be concluded that small gaps which are within CAD tolerance, i.e., 0.001 units, barely influence the quality of the simulation. The different behavior of gaps and overlaps can be explained by the minimal distance computation: in contrast to gaps, the assignment of points of the slave curve to the master curve is not unique in case of overlaps. | |

$$
M = 0.7Mmax = Mmax M = 0.35Mmax
$$

![Figure 58 Different geometry models for analyzing a cantilever sub- jected to an end moment](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-58-p050.png)

*Figure 58 Different geometry models for analyzing a cantilever sub- jected to an end moment: a definition of the problem and b resulting solutions. In b, different gray scales indicate the distinct patches.*

##### 5.3.3.3 Continuity Considerations

The continuity along the intersection of two trimmed patches is usually not higher than \(C_{0}\). The construction of corresponding \(C_{0}\) isogeometric spaces with optimal approximation properties is well understood for conforming parameterizations [299]. Brivadis et al. [39] showed this also for weakly imposed \(C_{0}\) conditions. However, their isogeometric mortar method focuses on regular patches and a modification of the basis functions at the boundary is required to obtain stability, if the same degree is used for the primal and dual spaces. Although the influence of non-matching interfaces is discussed as well,

Note the various complexities of the connection of adjacent patches. (Courtesy of Breitenberger [37, 38]) the application in the context of trimmed surfaces has yet to be investigated in more detail.

The construction of smooth isogeometric spaces for trimmed models is an even more complicated open topic. In fact, smooth isogeometric spaces on unstructured geometries are a challenging and open problem in general [141, 296]. Locking effects may occur even for regular planar multipatch configurations [63, 150]. At this point, it should be noted that T-splines or subdivision surfaces provide geometric models which are globally smooth almost everywhere. Nevertheless, these representations seem to lack

![Figure 59 Geometry representation and definition of the gap–overlap parameter f for the investigation of the effect of non-watertight geom- etries on numerical results. (Courtesy of Michael Breitenberger [ 37 , 38 ])](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-59-p051.png)

*Figure 59 Geometry representation and definition of the gap–overlap parameter f for the investigation of the effect of non-watertight geom- etries on numerical results. (Courtesy of Michael Breitenberger [ 37 , 38 ]): Geometry representation and definition of the gap–overlap parameter f for the investigation of the effect of non-watertight geometries on numerical results. (Courtesy of Michael Breitenberger [37, 38])*

$$
\begin{equation*} \mathbf{A}[i+j \cdot J, m+n \cdot J]=B_{i, p}\left(\bar{u}_{m}\right) B_{j, q}\left(\bar{v}_{n}\right), \tag{121} \end{equation*}
$$

![Figure 60 Comparison of the relative vertical displacement d 1 related to the gap–overlap parameter f . Gaps and overlaps are indicated by posi- tive and negative values, respectively. The gray area of the diagram indicates the default tolerance of the CAD software used. (Courtesy of Breitenberger [ 37 , 38 ])](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-60-p051.png)

*Figure 60 Comparison of the relative vertical displacement d 1 related to the gap–overlap parameter f . Gaps and overlaps are indicated by posi- tive and negative values, respectively. The gray area of the diagram indicates the default tolerance of the CAD software used. (Courtesy of Breitenberger [ 37 , 38 ]): Comparison of the relative vertical displacement d 1 related to the gap–overlap parameter f. Gaps and overlaps are indicated by positive and negative values, respectively. The gray area of the diagram indicates the default tolerance of the CAD software used. (Courtesy of Breitenberger [37, 38])*

optimal approximation properties due to the existence of extraordinary vertices [145, 212].

#### 5.3.4 Stabilization

A trimmed basis contains basis functions which are cut by the trimming curve and exist only partially within the valid area \(\mathcal{A}^{\mathrm{v}}\). In order to clarify the problem statement, Fig. 61 illustrates a trimmed univariate basis. It should be noted that the Greville abscissae of cut basis functions may be located outside of \(\mathcal{A}^{\mathrm{v}}\). In the example given, this is the case for \(B_{4,2}\). These points cannot be used for collocation or spline interpolation problems, despite the fact that they are the preferred choice for setting up a stable system of equations (see Sect. 2.3). Furthermore, the support of cut basis functions may be arbitrary small, e.g., this would be the case for \(B_{4,2}\) as the trimming location \(t\) approaches the knot value 2. Thus, the condition number of the resulting system matrices can become very large. In other words, a trimmed basis is not guaranteed to be stable.

In order to emphasize this stability issue an interpolation problem is examined: a given function

$$
\begin{equation*} f(u, v)=\frac{1}{\sqrt{(-1.2-u)^{2}+(-1.2-v)^{2}}}, \tag{120} \end{equation*}
$$

the total number of bivariate basis functions involved. The further components of the corresponding system of equa tions are the unknown coefficients \(c_{i, j}\) and the bivariate spline collocation matrix \(\mathbf{A}\). The matrix is defined by

![Figure 61 Univariate basis trimmed at a parameter t . There are basis functions which are fully inside ( green ), partially inside ( blue ), and completely outside ( dotted ) of  v . The Greville abscissae of the con- sidered basis functions are marked by circles . (Color figure online)](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-61-p051.png)

*Figure 61 Univariate basis trimmed at a parameter t . There are basis functions which are fully inside ( green ), partially inside ( blue ), and completely outside ( dotted ) of  v . The Greville abscissae of the con- sidered basis functions are marked by circles . (Color figure online): Univariate basis trimmed at a parameter t. There are basis functions which are fully inside (green), partially inside (blue), and completely outside (dotted) of  v. The Greville abscissae of the considered basis functions are marked by circles. (Color figure online)*

with \(i, m=0, \ldots, I\) and \(j, n=0, \ldots, J\), where \(I\) and \(J\) are the number of basis functions in each parametric directions. The initial parameter space is given by an open knot vector with a uniform discretization from-1 to 1 in both direc tions, i.e., \(u, v \in[-1,1]\), and the knot span size is specified by \(h=0.125\). A trimming parameter \(t \in[0.5,1)\) deter mines the square domain \(\mathcal{A}^{\mathrm{v}} \in[-1, t]^{2}\) considered for the interpolation problem. The interpolation points \(\overline{\boldsymbol{x}}\) of cut basis functions may have to be shifted into \(\mathcal{A}^{\mathrm{v}}\). Exterior basis functions that are completely outside of \(\mathcal{A}^{\mathrm{v}}\) are not involved in the interpolation process. The quality and sta bility of the approximation \(\boldsymbol{S}_{h}\) are specified by the relative interpolation error measured in the \(L_{2}\)-norm \(\left\|\epsilon_{\text {rel }}\right\|_{L_{2}}\) as well as the condition number of the spline collocation matrix \(\kappa(\mathbf{A})\). The results are summarized in Fig. 62 for vari ous degree with \(p=q\).

![Figure 62 Condition number 휅 ( 퐀 ) and relative interpolation error ‖‖ 휖 rel ‖‖ L 2 of the bivariate basis for several degrees p in both parametric directions related to the trimming parameter t . The subdivision of the horizontal axis corresponds to the knot values of the trimmed basis](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-62-p052.png)

*Figure 62 Condition number 휅 ( 퐀 ) and relative interpolation error ‖‖ 휖 rel ‖‖ L 2 of the bivariate basis for several degrees p in both parametric directions related to the trimming parameter t . The subdivision of the horizontal axis corresponds to the knot values of the trimmed basis: Condition number 휅 ( 퐀 ) and relative interpolation error ‖‖ 휖 rel ‖‖ L 2 of the bivariate basis for several degrees p in both parametric directions related to the trimming parameter t. The subdivision of the horizontal axis corresponds to the knot values of the trimmed basis*

It can be observed that the condition number of \(\mathbf{A}\) is considerably influenced by the trimming parameter \(t\). In particular, a peak is reached as soon as \(t\) approaches a knot value, i.e., a support of cut basis functions becomes very small. Furthermore, the approximation quality is affected. The peaks of the relative error \(\left\|\epsilon_{\text {rel }}\right\|_{L_{2}}\) near knot values are in fact disastrous. Hence, it is evident that the straightfor ward application of a trimmed basis negatively affects the condition number and subsequently the quality of the approximation.

The stability aspect of local approaches for the analysis of trimmed geometries has scarcely been considered in previous works. It is worth noting that Nitsche formulations may incorporate parameters which take cut elements into account, see e.g., [42, 80, 289]. A method-independent alternative that exploit the properties of B-splines is outlined in Sect. 6.

### 5.4 Summary and Discussion

Various approaches to incorporate trimmed geometries into an analysis have been described in this review. While Sect. 5.1 addresses an early attempt which combines trimmed patches with Lagrange interpolation, recent research is the focus of the subsequent Sects. (5.2) and (5.3). To recapitulate the findings of the current approaches: there are two fundamentally different philosophies to deal with trimmed models. One seeks to resolve the deficiencies of trimmed models by a reconstruction of the geometric representation. This is performed as a preprocessing step before the actual analysis. Since these procedures affect entire patches and their connection, they are referred to as global approaches in this work. The other philosophy is to accept the flaws of trimmed models, implying that the analysis has to be adaptable enough to cope with them. This capability is accomplished by treating the occurring trimming situations on the knot span level. Hence, we classify such techniques as local approaches.

Global approaches address the core of the problem and aim to solve it at its origin. In fact, they are similar to the remodeling schemes of CAGD outlined in Sect. 3.4. They share the same shortcomings such as an increased number of control points and the dependence on a four-sided domain if regular tensor product surfaces are used for the reconstruction. It can be argued that global approaches are more related to CAGD than analysis. Consequently, their success is also determined by the acceptance in the design community. However, a compelling global scheme could eventually lead to design models which can be directly applied not only to analysis but all downstream applications, which is the holy grail of the trimming problem.

Local approaches focus on enhancing the analysis and thus, may seem more feasible for researchers in the field of computational mechanics. In fact, the majority of the publications on isogeometric analysis of trimmed geometries employ such concepts. There is a close relation to fictitious domain, or immersed, methods since the trimmed parameter space is used as a background parameterization. Hence, similar challenges have to be addressed: (i) detection of elements cut be the trimming curve, (ii) special integration schemes for these elements, (iii) weak coupling of adjacent patches, and (iv) the stability issue induced by the trimmed basis. The main difference is that additional effort has to be made to associate the degrees of freedom of adjacent patches, keeping in mind that their intersections possess non-matching parameterizations, gaps, and overlaps. These distinct tasks are clearly separated from each other. For example, weak coupling is mandatory for finite element methods but may be neglected if a boundary element method is applied. Most researchers have drawn their attention to the integration of cut elements. The application of weak formulations has also been addressed by several authors. On the other hand, the stability of a trimmed basis and the robust association of adjacent patches are barely discussed in the literature, despite the fact that the latter task is crucial for the analysis of practical design models. Another issue of using a trimmed basis for the analysis is that the Greville abscissae of cut basis functions are not guaranteed to be located inside of the domain of interest. Consequently, an application to interpolation and collocation methods requires further considerations. However, the modular structure of local approaches is indeed a benefit compared to global approaches which require a self-contained concept which becomes more and more sophisticated with its capabilities.

## 6 Stabilization of a Trimmed Basis

There are two reasons for presenting a distinct section on the stabilization of trimmed parameter spaces: first and foremost, we want to draw attention to this issue which has

![Figure 63 Polynomial segments  s of a B-spline. The extensions of the segments are indicated by dashed lines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-63-p053.png)

*Figure 63 Polynomial segments  s of a B-spline. The extensions of the segments are indicated by dashed lines: Polynomial segments  s of a B-spline. The extensions of the segments are indicated by dashed lines*

been scarcely discussed so far, and, in addition, some of our recent research is focused on this topic allowing a more detailed observation of it. The general problem statement has already been given in Sect. 5.3.4, where it has been demonstrated that basis functions cut by a trimming curve can yield ill-conditioned system matrices. Further, Greville abscissae of such basis functions may be outside of the valid domain and thus, they cannot be applied to methods which employ these points like isogeometric collocation [11, 258]. In order to identify the troublesome components, we classify the basis functions of a trimmed parameter space as stable, degenerate, or exterior. The support of the latter is completely outside of the valid domain \(\mathcal{A}^{\mathrm{v}}\) and hence, it can be neglected for the analysis. The distinguish ing feature of the other types is that the Greville abscis sae of stable B-splines are within \(\mathcal{A}^{\mathrm{v}}\) whereas the Greville abscissae of degenerate ones are outside of \(\mathcal{A}^{\mathrm{v}}\).

The following stabilization scheme resolves the issues induced by degenerate basis functions in a simple and flexible manner. The concept is referred to as extended B-splines. Originally, these splines have been developed by Höllig and co-workers in the context of a B-spline based fictitious domain method [124-127]. Here, the main aspects of extended B-splines are outlined based on the findings provided in [199, 202].

### 6.1 Definition of Extended B-splines

We start the description of extended B-splines by recalling two fundamental properties of conventional B-spline: (i) B-splines \(B_{i, p}\) are represented by a set of polynomial seg ments \(\mathcal{B}_{i}^{s}\) and (ii) B-splines form a basis of a space \(\mathbb{S}_{p, \Xi}\) which contains every piecewise polynomial \(f_{p, \Xi}\) of degree \(p\) over a knot sequence \(\Xi\). The former property is illustrated in Fig. 63. It should be noted that each polynomial seg ment \(\mathcal{B}^{s}\) may be extended beyond its associated knot span \(s\). With this in mind, it is straightforward to grasp the essen tial idea of extended B-splines, namely to re-established the stability of a trimmed basis by substituting degenerate, and therefore potentially unstable, B-splines by extensions of stable ones. These extensions can be exactly represented by the basis since they are within \(\mathbb{S}_{p, \Xi}\) by definition. The overall construction procedure of extended B-splines is summarized in Fig. 64. Firstly, it is deter mined if the Greville abscissae of non-exterior B-splines are located inside or outside of \(\mathcal{A}^{\mathrm{v}}\). In the latter case the basis function is labeled as degenerate and the corre sponding index is stored in the index-set J. Secondly, the polynomial segments of trimmed knot spans are replaced by the extensions of the polynomial segments of the clos est non-trimmed knot span that contains stable B-splines only. These extensions together with the polynomial seg ments of the non-trimmed knot spans form the extended

![Figure 64 Basic procedure to get from a conventional to d extended B-splines](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-64-p054.png)

*Figure 64 Basic procedure to get from a conventional to d extended B-splines: b determination of degenerate B-splines and substitution of trimmed polynomial segments by c extensions of non-trimmed ones*

$$
\begin{equation*} f=\sum_{j=0}^{J-1} \lambda_{j, p}(f) B_{j, p}, \tag{123} \end{equation*}
$$

- (b)

- (c)

B-spline basis. The final step is to represent the extended B-splines by a linear combination of the original B-splines. An extended B-spline is defined by

![Figure 65 The construction of bivariate extrapolation weights e i , j for a biquadratic basis. Stable B-splines are marked by black and green circles . The shown values of e i , j are related to the degenerate basis function marked by the blue circle in the upper right corner of the parameter space. B-splines of the closest non-trimmed knot span are indicated by green circles . (Color figure online)](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-65-p054.png)

*Figure 65 The construction of bivariate extrapolation weights e i , j for a biquadratic basis. Stable B-splines are marked by black and green circles . The shown values of e i , j are related to the degenerate basis function marked by the blue circle in the upper right corner of the parameter space. B-splines of the closest non-trimmed knot span are indicated by green circles . (Color figure online): The construction of bivariate extrapolation weights e i, j for a biquadratic basis. Stable B-splines are marked by black and green circles. The shown values of e i, j are related to the degenerate basis function marked by the blue circle in the upper right corner of the parameter space. B-splines of the closest non-trimmed knot span are indicated by green circles. (Color figure online)*

Spline interpolation as described in Sect. 2.3 is not opti mal to compute \(e_{i, j}\) because the Greville abscissae of \(B_{j, p}\) are not located within the trimmed knot span in general. Hence, a quasi interpolation scheme is preferred which allows an explicit computation of B-spline coefficients. In particular, the so-called de Boor-Fix or dual functional \(\lambda_{j, p}\)

$$
\begin{equation*} B_{i, p}^{e}=B_{i, p}+\sum_{j \in J_{i}} e_{i, j} B_{j, p}, \tag{122} \end{equation*}
$$

$$
\begin{equation*} \lambda_{j, p}(f)=\frac{1}{p!} \sum_{k=0}^{p}(-1)^{k} \psi_{j, p}^{(p-k)}\left(\mu_{j}\right) f^{(k)}\left(\mu_{j}\right), \tag{124} \end{equation*}
$$

![Figure 66 Bivariate extended B-splines B e i , p with various cardinali- ties of the index-set 핁 i which indicates the number of related degen- erate B-splines. Note that a is in fact a conventional B-spline, i.e., B e i , p ≡ B i , p , since 핁 i is empty](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-66-p055.png)

*Figure 66 Bivariate extended B-splines B e i , p with various cardinali- ties of the index-set 핁 i which indicates the number of related degen- erate B-splines. Note that a is in fact a conventional B-spline, i.e., B e i , p ≡ B i , p , since 핁 i is empty: Bivariate extended B-splines B e i, p with various cardinalities of the index-set 핁 i which indicates the number of related degenerate B-splines. Note that a is in fact a conventional B-spline, i.e., B e i, p ≡ B i, p, since 핁 i is empty*

$$
\begin{equation*} \psi_{j, p}(u)=\prod_{m=1}^{p}\left(u-u_{j+m}\right) . \tag{125} \end{equation*}
$$

$$
\begin{equation*} e_{i, j}=\frac{1}{p!} \sum_{k=0}^{p}(-1)^{k}(p-k)!\beta_{p-k} k!\alpha_{k} \tag{128} \end{equation*}
$$

The evaluation point \(\mu_{j}\) can be chosen arbitrarily within \(\left[u_{j}, u_{j+p+1}\right]\). Substituting \(f\) of Eq. (124) by \(\mathcal{B}_{i}^{s}\) yields the extrapolation weights

$$
\begin{equation*} \psi_{j, p}(u)=\sum_{k=0}^{p} \beta_{k} u^{k} \quad \text { and } \quad \mathcal{B}_{i}^{s}(u)=\sum_{k=0}^{p} \alpha_{k} u^{k}, \tag{127} \end{equation*}
$$

expression (126) simplifies to

The interested reader is referred to [202] for details on the conversion to power basis form and further details regarding the evaluation of the dual functional. In case of a uniform knot vector, a simplified formula can be derived which solely relies on the indices of the B-splines involved, see e.g., [124].

Bivariate extrapolation weights are simply obtained by the tensor product of their univariate counterparts calculated for each parametric direction as illustrated in Fig. 65. Note that the degenerate B-spline is distributed to (p + 1)(q + 1) stable ones.

### 6.2 Properties of Extended B-splines

Extended B-splines inherit most essential properties of conventional B-splines [124, 125, 127]. They are linearly independent and polynomial precision is guaranteed. Thus, they form a basis for a spline space. Each knot span has exactly \(p+1\) non-vanishing basis functions which span the space of all polynomials of degree \(\leqslant p\) over \(\mathcal{A}^{\mathrm{v}}\). Further more, approximation estimates have the same convergence order as conventional B-splines. Extended B-splines have local support in the sense that only B-splines near the trim ming curve are subjected to the extension procedure. The actual size of the affected region depends on the fineness of the parameter space, the degree of its basis functions, and the number of degenerate \(B_{j, p}\) related to the stable \(B_{i, p}\). The latter is given by the cardinality of the corresponding index-set \(\# \mathbb{J}_{i}\). Figure 66 illustrates various examples of extended B-splines. The basis function shown in Fig. 66a is in fact a conventional B-spline since it is far away from the trimming curve.

However, there are also some differences. It is important to note that the extrapolation weights may be negative, hence the evaluation of extended B-splines may lead to negative values. conventional B-splines, on the other hand, are strictly non-negative. This property is exploited in some contact formulations [295] and structural optimization [210], for instance. In such cases, the application

$$
\begin{equation*} e_{i, j}=\frac{1}{p!} \sum_{k=0}^{p}(-1)^{k} \psi_{j, p}^{(p-k)}\left(\mu_{j}\right) \mathcal{B}_{i}^{s^{(k)}}\left(\mu_{j}\right) . \tag{126} \end{equation*}
$$

of extended B-splines requires further considerations. The main difference in favor of extended B-splines is the stabil ity of the corresponding basis. The condition number of a system is independent of the location of the trimming curve due to the substitution of B-splines with small support. Another benefit is that all Greville abscissae are located within \(\mathcal{A}^{\mathrm{v}}\) by construction.

### 6.3 Assembling

Extended B-splines can be applied to an analysis in a very convenient manner. Suppose we have a linear system of n equations, one for each stable B-spline, set up by all basis functions m which are at least partially inside  v. This yields with m > n. Upon this point, only conventional B-splines have been used to compute the system matrix 𝐊 . In other words, 𝐊 is set up as usual but equations related to degenerate B-splines are neglected. In order to obtain a square matrix an extension matrix 𝐄 ∈ \(\mathbb{R}^{m}\) × n is introduced [124]. This sparse matrix 𝐄 contains all extrapolation weights e i, j including the trivial ones, i.e., e i, i = 1. The transformation of the original to the stable extended B-spline basis is performed by multiplying the extension matrix to the system matrix. The resulting stable system (129) 𝐊 𝐮 = 𝐟 where 𝐮 , 𝐟 ∈ \(\mathbb{R}^{n}\) and 𝐊 ∈ \(\mathbb{R}^{n}\) × m,

### 6.4 Application to NURBS

for the representation of the geometry and the approximations of the physical fields. Hence, conventional B-splines can be used for the discretization of the field variables over NURBS patches. This allows the straightforward application of extended B-splines. In addition, the combination of NURBS for the geometry description and B-splines for the approximations has been shown to be more efficient [199] and does not lead to a loss of accuracy [184, 201, 299]. There is one caveat: independent fields are inconsistent with the isoparametric concept in mechanics and can upset the precise representation of constant strain states and rigid body motions [139].

### 6.5 Assessment of Stability

In order to assess the approximation quality and stability of extended B-splines the same interpolation problem as in Sect. 5.3.4 is considered. Again, the relative interpolation

![Figure 67 Spline interpolation problem with extended B-splines for several degrees p . The condition number 휅 ( 퐀 ) and the relative inter- polation error ‖ ‖ 휖 rel ‖ ‖ L 2 are related to the trimming parameter t . The labels of the horizontal axis indicate knots of the trimmed basis](/Users/evanthayer/Projects/stepview/docs/2018_trimming_in_isogeometric_analysis_review/figures/figure-67-p056.png)

*Figure 67 Spline interpolation problem with extended B-splines for several degrees p . The condition number 휅 ( 퐀 ) and the relative inter- polation error ‖ ‖ 휖 rel ‖ ‖ L 2 are related to the trimming parameter t . The labels of the horizontal axis indicate knots of the trimmed basis: Spline interpolation problem with extended B-splines for several degrees p. The condition number 휅 ( 퐀 ) and the relative interpolation error ‖ ‖ 휖 rel ‖ ‖ L 2 are related to the trimming parameter t. The labels of the horizontal axis indicate knots of the trimmed basis*

error measured in the \(L_{2}\)-norm \(\left\|\epsilon_{\text {rel }}\right\|_{L_{2}}\) and the condition number of the spline collocation matrix \(\kappa(\mathbf{A})\) are examined. The results are summarized in Fig. 67.

Comparing Figs. 62 and 67 shows the significant improvement of extended B-splines. If extended B-splines are used, 𝜅 ( 𝐀 ) hardly changes and is independent of the trimming parameter t. In other words, the extended B-spline basis is stable. Consequently, the approximation quality is significantly improved. In Fig. 67, the reduction of the approximation accuracy occurs only due to the reduction of the degrees of freedom n, i.e., number of extended B-spline, as the trimming parameter t → 0.5.

### 6.6 Summary and Discussion

The concept of extended B-splines substitutes unstable basis functions by extensions of stable ones. It is estab lished in a very flexible manner and requires only the pres ence of a sufficient number of stable basis functions. In general, this requirement is non-restrictive and can be ful filled by refinement of the basis. Still, it may be an issue if the design object contains very small fillets. Only B-splines close to the trimming curve are affected by the stabiliza tion procedure. The number of B-splines depends on the distance of the trimming curve to the knot span which pro vides the stable B-splines. This correlates with the degree \(p\) of the basis function since the size of its support extends over \(p+1\) knot spans.

## 7 Final Remarks and Conclusions

The present work accumulates several topics related to the treatment of trimmed models and the interoperability problem between CAD and downstream applications in general.

It is apparent that trimming is a fundamental technique for geometric design. Most importantly, it enables the computation of intersections between free-form surfaces. However, intersection curves cannot be determined exactly, which leads to various problems. As a result, an intersection is usually approximated by several independent curves, one in model space and one in the parameter space of each surface involved. Their images in model space do not coincide and there is no link between these curves. The resulting gaps and overlaps between the surfaces yield robustness issues due to a lack of exact topological consistency. These problems are still unresolved, despite the fact that they have been the focus of an enormous amount of research.

Since the robustness issues of trimmed models are particularly crucial for downstream applications, the exchange of CAD data is examined as well. Neutral exchange standards seem to be the most comprehensive strategy, but it is important to note that all translations lead to loss of information. Moreover, the capabilities of the various exchange formats are not equivalent. It is demonstrated that STEP is superior to IGES. STEP should be preferred in general and especially if the topology of a model needs to be extracted.

In the context of analysis, the current approaches can be divided into two different philosophies. On the one hand, global approaches aim to fix the problems of trimmed models before the simulation by a reconstruction of the geometric representation. Using local approaches, on the other hand, trimmed models are directly employed, but the analysis has to be enhanced in order to deal with all the flaws of the geometric representation. It may be argued that the former addresses the issue from a CAD point of view, whereas the latter utilizes an analysis perspective. The fact that the problem can be tackled by these diverse directions emphasizes the central role of trimmed models for the integration of design and analysis.

The main conclusions of the present review can be summarized as follows:

- -Trimming seems to be a simple and benign procedure at first glance, but its consequences are profound.

- -Robustness issues are the price for the flexibility of trimmed models.

- -Flaws of trimmed models are usually hidden from the user, but surface as soon as they are applied to a downstream application.

- -To overcome these issues is a crucial aspect regarding the integration of design and analysis.

- -The success of CAD data exchange depends on the quality of the design model and the capability of the exchange format.

- -There is no canonical way to deal with trimmed models, neither in analysis nor in design, at least so far.

It is hoped that this review provides a helpful introduction to the topic and an impetus for further research activities. There are indeed several open issues worth exploring: optimization of the reparameterization of the global approach based on isocurves, assessment of the affect of gaps on the analysis in case of local schemes, and application to isogeometric collocation, just to name a few. In general, the step from academic examples to practical multipatch models is perhaps the most challenging task. Robust algorithms should be able to take the tolerances of a design model into account. On the other hand, it may be an unrealistic aim to find a solution that can deal with every possible trimmed geometry. Similar to the quality of conventional meshes, an isogeometric simulation is effected by the quality of the design model. Hence, the specification of distinct properties that classify a design model to be analysis-suitable are needed so that a designer can get a direct feedback if a model requires an improvement-providing the right information to the right person at the right time. We close this review by emphasizing that a holistic treatment of the engineering design process requires the aligned efforts of both the design and the analysis communities.

Acknowledgements Open access funding provided by Austrian Science Fund (FWF). We thank Michael Breitenberger and Ben Urick for their useful advise and fruitful discussions. This research was supported by the Austrian Science Fund (FWF): \(J_{3884}\)-N32, and the Office of Naval Research (ONR): N00014-17-1-2039. This support is gratefully acknowledged.

Compliance with Ethical Standards Conflict of interest The authors declare that they have no conflict of interest.

Open Access This article is distributed under the terms of the Creative Commons Attribution 4.0 International License (http: creativecommons.org licenses by 4.0), which permits unrestricted use, distribution, and reproduction in any medium, provided you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons license, and indicate if changes were made.

Appendix: Exchange Data File Examples The source files of the neutral exchange format example presented in Sect. 4.2.3 are given in this section. The models have been constructed with the commercial CAD software Rhinoceros 5.

It should be pointed out that the IGES examples, i.e., Files 1 and 2, provide the same information although the topological data of the two models was different before the extraction procedure. In particular, these files differ only in the representation of some floating point values, e.g., 0.0D0 and 8.881D-16, and the sequence of the numbering of a few parametric data entities, e.g., 0000029P of File 1 is equal to 0000037P of File 2. The corresponding STEP examples with the correct topology data are given in Files 3 and 4.

The interested reader is referred to the homepage of STEP Tools, Inc. \({ }^{21}\) for further examples of STEP files covering various application protocols.

21 http: www.steptools.com, 8 2016.

126,1,1,1,0,1,0,-7.071067811865475D0,-7.071067811865475D0, 0000029P 51-0.0D0,-0.0D0,1.0D0,1.0D0,0.0D0,5.0D0,0.0D0,5.0D0,0.0D0,0.0D0, 0000029P 52 53 0000029P-7.071067811865475D0,-0.0D0,0.0D0,0.0D0,1.0D0; 126,3,3,1,0,1,0,-7.071067811865475D0,-7.071067811865475D0, 0000031P 54-7.071067811865475D0,-7.071067811865475D0,-0.0D0,-0.0D0,-0.0D0, 0000031P 55-0.0D0,1.0D0,1.0D0,1.0D0,1.0D0,5.0D0,0.0D0,0.0D0, 0000031P 56 57 0000031P 3.333333333333334D0,1.666666666666666D0,0.0D0, 1.666666666666666D0,3.333333333333334D0,0.0D0,0.0D0,5.0D0,0.0D0, 0000031P 58 59 0000031P D0,0.0D0,0.0D0,1.0D0; -7.071067811865475D0,-0.0 126,1,1,1,0,1,0,-5.0D0,-5.0D0,-0.0D0,-0.0D0,1.0D0,1.0D0,5.0D0, 0000033P 60 0.0D0,0.0D0,0.0D0,0.0D0,0.0D0,-5.0D0,-0.0D0,0.0D0,0.0D0,1.0D0; 0000033P 61 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,5.0D0, 0000035P 62 0.0D0,0.0D0,0.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000035P 63 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,0.0D0, 0000037P 64 0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000037P 65 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,0.0D0, 0000039P 66 0.0D0,5.0D0,0.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000039P 67 68 0000041P 3,29,1,1,31,33,1,1,35,37,1,1,39; 141,1,3,27, 69 0000043P 143,1,27,1,41; 1 T S0000001G0000011D0000044P0000069 File 2: IGES trimming example-solid model \(S_{1}\) 1H,,1H;,, G 1 72HC:\Users\Marussig\Desktop\LinuxSync\simpleTrimmingExampleBooleanIGES.G 2 igs, G 3 26HRhinoceros (Sep 27 2012),31HTrout Lake IGES 012 Sep 27 2012, G 4 32,38,6,308,15, G 5, G 6 7 G 1.0D0,2,2HMM,1,0.254D0,13H160826.214018, 0.001D0, G 8 5D0, G 9, G 10, G 11 12 G 160826.214018; 10,0,13H 314 1 0 0 0 0 0 000000200D 1 314 0 1 1 0 0 0 COLOR 0D 2 406 2 0 0 1 0 0 000000300D 3 406 0-1 1 3 0 0LEVELDEF 0D 4 128 3 0 0 1 0 0 000010000D 5 128 0-1 7 8 0 0 Shell 0D 6 126 10 0 0 1 0 0 000010000D 7 126 0-1 3 1 0 0 Shell 1D 8 126 13 0 0 1 0 0 000010500D 9 126 0-1 4 1 0 0 Shell 1D 10 126 17 0 0 1 0 0 000010000D 11 126 0-1 5 1 0 0 Shell 2D 12 126 22 0 0 1 0 0 000010500D 13 126 0-1 5 1 0 0 Shell 2D 14 126 27 0 0 1 0 0 000010000D 15 126 0-1 5 1 0 0 Shell 3D 16 126 32 0 0 1 0 0 000010500D 17 126 0-1 4 1 0 0 Shell 3D 18 126 36 0 0 1 0 0 000010000D 19 126 0-1 3 1 0 0 Shell 4D 20 126 39 0 0 1 0 0 000010500D 21 126 0-1 3 1 0 0 Shell 4D 22 141 42 0 0 1 0 0 000010000D 23 141 0-1 1 0 0 0 Shell 1D 24 143 43 0 0 1 0 0 000000000D 25 143 0-1 1 0 0 0 Shell 1D 26 128 44 0 0 1 0 0 000010000D 27 128 0-1 4 8 0 0 Shell 0D 28 126 48 0 0 1 0 0 000010000D 29 126 0-1 2 1 0 0 Shell 1D 30 126 50 0 0 1 0 0 000010500D 31 126 0-1 2 1 0 0 Shell 1D 32 126 52 0 0 1 0 0 000010000D 33 126 0-1 2 1 0 0 Shell 2D 34 126 54 0 0 1 0 0 000010500D 35 126 0-1 2 1 0 0 Shell 2D 36 126 56 0 0 1 0 0 000010000D 37 126 0-1 3 1 0 0 Shell 3D 38 126 59 0 0 1 0 0 000010500D 39 126 0-1 6 1 0 0 Shell 3D 40 141 65 0 0 1 0 0 000010000D 41 141 0-1 1 0 0 0 Shell 1D 42 143 66 0 0 1 0 0 000000000D 43 143 0-1 1 0 0 0 Shell 2D 44 1 0000001P); 0 0, 0, 314,0.0,0.0,0.0,20HRGB(2 0000003P 406,2,1,7HDefault; 128,1,1,1,1,0,0,1,0,0,0.0D0,0.0D0,7.071067811865475D0, 0000005P 3 7.071067811865475D0,0.0D0,0.0D0,9.999999999999998D0, 0000005P 4 9.999999999999998D0,1.0D0,1.0D0,1.0D0,1.0D0,5.0D0,0.0D0,-5.0D0, 0000005P 5 8.881784197001252D-16,4.999999999999999D0,-5.0D0,5.0D0,0.0D0, 0000005P 6 4.999999999999998D0,8.881784197001252D-16,4.999999999999999D0, 0000005P 7 4.999999999999998D0,0.0D0,7.071067811865475D0,0.0D0, 0000005P 8 9 0000005P 9.999999999999998D0; 10 0000007P 126,1,1,1,0,1,0,0.0D0,0.0D0,7.071067811865475D0, 7.071067811865475D0,1.0D0,1.0D0,5.0D0,0.0D0,0.0D0,0.0D0,5.0D0, 0000007P 11 0.0D0,0.0D0,7.071067811865475D0,0.0D0,0.0D0,1.0D0; 0000007P 12 13 0000009P 126,1,1,1,0,1,0,0.0D0,0.0D0,7.071067811865475D0, 7.071067811865475D0,1.0D0,1.0D0,0.0D0,5.0D0,0.0D0, 0000009P 14 7.071067811865475D0,5.000000000000001D0,0.0D0,0.0D0, 0000009P 15 16 0000009P 7.071067811865475D0,0.0D0,0.0D0,1.0D0; 126,1,1,1,0,1,0,5.000000000000001D0,5.000000000000001D0, 0000011P 17 9.999999999999998D0,9.999999999999998D0,1.0D0,1.0D0,0.0D0,5.0D0, 0000011P 18 19 0000011P 0.0D0,8.881784197001252D-16,4.999999999999999D0, 4.999999999999998D0,5.000000000000001D0,9.999999999999998D0, 0000011P 20 21 0000011P 1.0D0,0.0D0,0.0D0; 126,1,1,1,0,1,0,5.000000000000001D0,5.000000000000001D0, 0000013P 22 9.999999999999998D0,9.999999999999998D0,1.0D0,1.0D0, 0000013P 23 24 0000013P 7.071067811865475D0,5.000000000000001D0,0.0D0, 25 0000013P 7.071067811865475D0,9.999999999999998D0,0.0D0, 5.000000000000001D0,9.999999999999998D0,0.0D0,0.0D0,1.0D0; 0000013P 26 126,1,1,1,0,1,0,-7.071067811865475D0,-7.071067811865475D0, 0000015P 27 28 0000015P-0.0D0,-0.0D0,1.0D0,1.0D0,8.881784197001252D-16, 4.999999999999999D0,4.999999999999998D0,5.0D0,0.0D0, 0000015P 29

4.999999999999998D0,-7.071067811865475D0,-0.0D0,0.0D0,0.0D0, 0000015P 30 1.0D0; 0000015P 31 32 0000017P 126,1,1,1,0,1,0,0.0D0,0.0D0,7.071067811865475D0, 7.071067811865475D0,1.0D0,1.0D0,7.071067811865475D0, 0000017P 33 9.999999999999998D0,0.0D0,0.0D0,9.999999999999998D0,0.0D0,0.0D0, 0000017P 34 35 0000017P 7.071067811865475D0,0.0D0,0.0D0,1.0D0; 126,1,1,1,0,1,0,-9.999999999999998D0,-9.999999999999998D0, 0000019P 36-5.0D0,-5.0D0,1.0D0,1.0D0,5.0D0,0.0D0,4.999999999999998D0,5.0D0, 0000019P 37 0.0D0,0.0D0,-9.999999999999998D0,-5.0D0,1.0D0,0.0D0,0.0D0; 0000019P 38 39 0000021P 126,1,1,1,0,1,0,0.0D0,0.0D0,4.999999999999998D0, 4.999999999999998D0,1.0D0,1.0D0,0.0D0,9.999999999999998D0,0.0D0, 0000021P 40 0.0D0,5.0D0,0.0D0,0.0D0,4.999999999999998D0,0.0D0,0.0D0,1.0D0; 0000021P 41 141,1,3,5,4,7,1,1,9,11,1,1,13,15,1,1,17,19,1,1,21; 0000023P 42 43 0000025P 143,1,5,1,23; 128,1,1,1,1,0,0,1,0,0,0.0D0,0.0D0,5.0D0,5.0D0,0.0D0,0.0D0,5.0D0, 0000027P 44 5.0D0,1.0D0,1.0D0,1.0D0,1.0D0,0.0D0,0.0D0,0.0D0,0.0D0,5.0D0, 0000027P 45 0.0D0,5.0D0,0.0D0,0.0D0,5.0D0,5.0D0,0.0D0,0.0D0,5.0D0,0.0D0, 0000027P 46 5.0D0; 0000027P 47 126,1,1,1,0,1,0,-5.0D0,-5.0D0,-0.0D0,-0.0D0,1.0D0,1.0D0,5.0D0, 0000029P 48 0.0D0,0.0D0,0.0D0,0.0D0,0.0D0,-5.0D0,-0.0D0,0.0D0,0.0D0,1.0D0; 0000029P 49 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,5.0D0, 0000031P 50 0.0D0,0.0D0,0.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000031P 51 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,0.0D0, 0000033P 52 0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000033P 53 126,1,1,1,0,1,0,0.0D0,0.0D0,5.0D0,5.0D0,1.0D0,1.0D0,0.0D0,0.0D0, 0000035P 54 0.0D0,5.0D0,0.0D0,0.0D0,0.0D0,5.0D0,0.0D0,0.0D0,1.0D0; 0000035P 55 126,1,1,1,0,1,0,-7.071067811865475D0,-7.071067811865475D0, 0000037P 56-0.0D0,-0.0D0,1.0D0,1.0D0,0.0D0,5.0D0,0.0D0,5.0D0,0.0D0,0.0D0, 0000037P 57 58 0000037P-7.071067811865475D0,-0.0D0,0.0D0,0.0D0,1.0D0; 126,3,3,1,0,1,0,-7.071067811865475D0,-7.071067811865475D0, 0000039P 59-7.071067811865475D0,-7.071067811865475D0,-0.0D0,-0.0D0,-0.0D0, 0000039P 60-0.0D0,1.0D0,1.0D0,1.0D0,1.0D0,5.0D0,0.0D0,0.0D0, 0000039P 61 62 0000039P 3.333333333333334D0,1.666666666666666D0,0.0D0, 1.666666666666666D0,3.333333333333334D0,0.0D0,0.0D0,5.0D0,0.0D0, 0000039P 63 64 0000039P 5475D0,-0.0D0,0.0D0,0.0D0,1.0D0; -7.07106781186 65 0000041P 141,1,3,27,3,29,1,1,31,33,1,1,35,37,1,1,39; 66 0000043P 143,1,27,1,41; 1 T S0000001G0000012D0000044P0000066 File 3: STEP trimming example-surface model

```text
ISO -10303-21; HEADER; * Generated by software containing ST-Developer * from STEP Tools, Inc. (www.steptools.com) * * OPTION: using custom schema -name function * FILE_DESCRIPTION( * description * (''), * implementation_level * '2;1'); FILE_NAME( * name * 'Trim', * time_stamp * '2016-09-06T17:08:41+02:00', * author * (''), * organization * (''), * preprocessor_version * 'ST-DEVELOPER visiblespace v15 ', * originating_system * '', * authorisation * ''); FILE_SCHEMA (('AUTOMOTIVE_DESIGN')); ENDSEC; DATA; #10=SHAPE_REPRESENTATION_RELATIONSHIP('','',#100,#15); #11=PRESENTATION_LAYER_ASSIGNMENT('Default','',(#13)); #12=PRESENTATION_LAYER_ASSIGNMENT('Default','',(#14)); #13=SHELL_BASED_SURFACE_MODEL('shell_1',(#16)); #14=SHELL_BASED_SURFACE_MODEL('shell_2',(#17)); #15=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('shell_rep_0',(#13,#14,#102), #99); #16=OPEN_SHELL('',(#18)); #17=OPEN_SHELL('',(#19)); #18=ADVANCED_FACE('',(#20),#80,.T.); #19=ADVANCED_FACE('',(#21),#81,.T.); #20=FACE_OUTER_BOUND('',#22,.T.); #21=FACE_OUTER_BOUND('',#23,.T.); #22=EDGE_LOOP('',(#24,#25,#26,#27)); #23=EDGE_LOOP('',(#28,#29,#30)); #24=ORIENTED_EDGE('',*,*,#52,.T.); #25=ORIENTED_EDGE('',*,*,#53,.T.); #26=ORIENTED_EDGE('',*,*,#54,.T.); #27=ORIENTED_EDGE('',*,*,#55,.T.); #28=ORIENTED_EDGE('',*,*,#56,.T.); #29=ORIENTED_EDGE('',*,*,#57,.T.); #30=ORIENTED_EDGE('',*,*,#58,.T.); #31=PCURVE('',#80,#38); #32=PCURVE('',#80,#39); #33=PCURVE('',#80,#40); #34=PCURVE('',#80,#41); #35=PCURVE('',#81,#42); #36=PCURVE('',#81,#43); #37=PCURVE('',#81,#44); #38=DEFINITIONAL_REPRESENTATION('',(#60),#152); #39=DEFINITIONAL_REPRESENTATION('',(#62),#152); #40=DEFINITIONAL_REPRESENTATION('',(#64),#152); #41=DEFINITIONAL_REPRESENTATION('',(#66),#152); #42=DEFINITIONAL_REPRESENTATION('',(#68),#152); #43=DEFINITIONAL_REPRESENTATION('',(#70),#152); #44=DEFINITIONAL_REPRESENTATION('',(#72),#152); #45=SURFACE_CURVE('',#59,(#31),.PCURVE_S1.); #46=SURFACE_CURVE('',#61,(#32),.PCURVE_S1.); #47=SURFACE_CURVE('',#63,(#33),.PCURVE_S1.); #48=SURFACE_CURVE('',#65,(#34),.PCURVE_S1.); #49=SURFACE_CURVE('',#67,(#35),.PCURVE_S1.); #50=SURFACE_CURVE('',#69,(#36),.PCURVE_S1.); #51=SURFACE_CURVE('',#71,(#37),.PCURVE_S1.); #52=EDGE_CURVE('',#75,#76,#45,.T.);
```

```text
#53=EDGE_CURVE('',#76,#73,#46,.T.); #54=EDGE_CURVE('',#73,#74,#47,.T.); #55=EDGE_CURVE('',#74,#75,#48,.T.); #56=EDGE_CURVE('',#78,#79,#49,.T.); #57=EDGE_CURVE('',#79,#77,#50,.T.); #58=EDGE_CURVE('',#77,#78,#51,.T.); #59=B_SPLINE_CURVE_WITH_KNOTS('',1,(#116,#117),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,7.07106781186547),.UNSPECIFIED.); #60=B_SPLINE_CURVE_WITH_KNOTS('',1,(#118,#119),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,7.07106781186547),.UNSPECIFIED.); #61=B_SPLINE_CURVE_WITH_KNOTS('',1,(#120,#121),.UNSPECIFIED.,.F.,.F.,(2, 2),(5.,10.),.UNSPECIFIED.); #62=B_SPLINE_CURVE_WITH_KNOTS('',1,(#122,#123),.UNSPECIFIED.,.F.,.F.,(2, 2),(5.,10.),.UNSPECIFIED.); #63=B_SPLINE_CURVE_WITH_KNOTS('',1,(#124,#125),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #64=B_SPLINE_CURVE_WITH_KNOTS('',1,(#126,#127),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #65=B_SPLINE_CURVE_WITH_KNOTS('',1,(#128,#129),.UNSPECIFIED.,.F.,.F.,(2, 2),(-10.,-5.),.UNSPECIFIED.); #66=B_SPLINE_CURVE_WITH_KNOTS('',1,(#130,#131),.UNSPECIFIED.,.F.,.F.,(2, 2),(-10.,-5.),.UNSPECIFIED.); #67=B_SPLINE_CURVE_WITH_KNOTS('',1,(#139,#140),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #68=B_SPLINE_CURVE_WITH_KNOTS('',1,(#141,#142),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #69=B_SPLINE_CURVE_WITH_KNOTS('',1,(#143,#144),.UNSPECIFIED.,.F.,.F.,(2, 2),(-5.,0.),.UNSPECIFIED.); #70=B_SPLINE_CURVE_WITH_KNOTS('',1,(#145,#146),.UNSPECIFIED.,.F.,.F.,(2, 2),(-5.,0.),.UNSPECIFIED.); #71=B_SPLINE_CURVE_WITH_KNOTS('',1,(#147,#148),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,5.),.UNSPECIFIED.); #72=B_SPLINE_CURVE_WITH_KNOTS('',1,(#149,#150),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,5.),.UNSPECIFIED.); #73=VERTEX_POINT('',#112); #74=VERTEX_POINT('',#113); #75=VERTEX_POINT('',#114); #76=VERTEX_POINT('',#115); #77=VERTEX_POINT('',#136); #78=VERTEX_POINT('',#137); #79=VERTEX_POINT('',#138); #80=B_SPLINE_SURFACE_WITH_KNOTS('',1,1,((#108,#109),(#110,#111)), .UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.,7.07106781186547),(0.,10.), .UNSPECIFIED.); #81=B_SPLINE_SURFACE_WITH_KNOTS('',1,1,((#132,#133),(#134,#135)), .UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.,5.),(0.,5.),.UNSPECIFIED.); #82=SHAPE_DEFINITION_REPRESENTATION(#83,#100); #83=PRODUCT_DEFINITION_SHAPE('Document','',#85); #84=PRODUCT_DEFINITION_CONTEXT('3D visiblespaceMechanical visiblespaceParts ' ,#89,'design '); #85=PRODUCT_DEFINITION('A','First visiblespaceversion' ,#86,#84); #86=PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('A', 'First visiblespace v e r s i o n ' ,#91 ,. MADE .); #87=PRODUCT_RELATED_PRODUCT_CATEGORY('tool','tool',(#91)); #88=APPLICATION_PROTOCOL_DEFINITION('Draft visiblespaceInternational visiblespaceStandard ', 'automotive_design',1999,#89); #89=APPLICATION_CONTEXT( 'data visiblespace f o r visiblespace a u t o m o t i v e visiblespace m e c h a n i c a l visiblespace d e s i g n visiblespace p r o c e s s e s ' ); #90=PRODUCT_CONTEXT('3D visiblespace Mechanical visiblespace Parts ' ,#89,'mechanical '); #91=PRODUCT('Document','Document','Rhino visiblespaceconverted visiblespaceto visiblespace STEP ' ,(#90)); #92=( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) ); #93=( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) ); #94=DIMENSIONAL_EXPONENTS(0.,0.,0.,0.,0.,0.,0.); #96=( CONVERSION_BASED_UNIT('DEGREES',#95) NAMED_UNIT(#94) PLANE_ANGLE_UNIT() ); #97=( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() ); #98=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#92, 'DISTANCE_ACCURACY_VALUE', 'Maximum visiblespace model visiblespace s p a c e visiblespace d i s t a n c e visiblespace b e t w e e n visiblespace g e o m e t r i c visiblespace e n t i t i e s visiblespace a t visiblespace a s s e r t e d visiblespace c onnectivities'); #99=( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#98)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#97,#96,#92)) REPRESENTATION_CONTEXT('ID1','3D') ); #100=SHAPE_REPRESENTATION('Document',(#101,#102),#99); #101=AXIS2_PLACEMENT_3D('',#107,#103,#104); #102=AXIS2_PLACEMENT_3D('',#151,#105,#106); #103=DIRECTION('',(0.,0.,1.)); #104=DIRECTION('',(1.,0.,0.)); #105=DIRECTION('',(0.,0.,1.)); #106=DIRECTION('',(1.,0.,0.)); #107=CARTESIAN_POINT('',(0.,0.,0.)); #108=CARTESIAN_POINT('',(5.,0.,-5.)); #109=CARTESIAN_POINT('',(5.,0.,5.)); #110=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,-5.)); #111=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #112=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #113=CARTESIAN_POINT('',(5.,0.,5.)); #114=CARTESIAN_POINT('',(5.,0.,8.88178419700125E-16)); #116=CARTESIAN_POINT('',(5.,0.,8.88178419700125E-16));
```

```text
#118=CARTESIAN_POINT('',(0.,5.)); #119=CARTESIAN_POINT('' ,(7.07106781186547,5.)); #120=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,8.88178419700125E-16)); #121=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #122=CARTESIAN_POINT('' ,(7.07106781186547,5.)); #123=CARTESIAN_POINT('' ,(7.07106781186547,10.)); #124=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #125=CARTESIAN_POINT('',(5.,0.,5.)); #126=CARTESIAN_POINT('' ,(7.07106781186547,10.)); #127=CARTESIAN_POINT('',(0.,10.)); #128=CARTESIAN_POINT('',(5.,0.,5.)); #129=CARTESIAN_POINT('',(5.,0.,8.88178419700125E-16)); #130=CARTESIAN_POINT('',(0.,10.)); #131=CARTESIAN_POINT('',(0.,5.)); #132=CARTESIAN_POINT('',(0.,0.,0.)); #133=CARTESIAN_POINT('',(5.,0.,0.)); #134=CARTESIAN_POINT('',(0.,5.,0.)); #135=CARTESIAN_POINT('',(5.,5.,0.)); #136=CARTESIAN_POINT('',(0.,0.,0.)); #137=CARTESIAN_POINT('',(0.,5.,0.)); #138=CARTESIAN_POINT('',(5.,0.,0.)); #139=CARTESIAN_POINT('',(0.,5.,0.)); #140=CARTESIAN_POINT('',(5.,0.,0.)); #141=CARTESIAN_POINT('',(5.,0.)); #142=CARTESIAN_POINT('',(0.,5.)); #143=CARTESIAN_POINT('',(5.,0.,0.)); #144=CARTESIAN_POINT('',(0.,0.,0.)); #145=CARTESIAN_POINT('',(0.,5.)); #146=CARTESIAN_POINT('',(0.,0.)); #147=CARTESIAN_POINT('',(0.,0.,0.)); #148=CARTESIAN_POINT('',(0.,5.,0.)); #149=CARTESIAN_POINT('',(0.,0.)); #150=CARTESIAN_POINT('',(5.,0.)); #151=CARTESIAN_POINT('',(0.,0.,0.)); #152=( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('pspace','') ); ENDSEC; END-ISO -10303-21;
```

```text
#95=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.01745329252),#93); #115=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,8.88178419700125E-16)); #117=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,8.88178419700125E-16)); File 4: STEP trimming example - solid model ISO -10303-21; HEADER; * Generated by software containing ST-Developer * from STEP Tools , Inc. (www.steptools.com) * * OPTION: using custom schema -name function * FILE_DESCRIPTION( * description * (''), * implementation_level * '2;1'); FILE_NAME( * name * 'Boolean', * time_stamp * '2016-09-06T17:07:00+02:00', * author * (''), * organization * (''), * preprocessor_version * 'ST-DEVELOPER visiblespace v15 ', * originating_system * '', * authorisation * ''); FILE_SCHEMA (('AUTOMOTIVE_DESIGN')); ENDSEC; DATA; #10=SHAPE_REPRESENTATION_RELATIONSHIP('','',#92,#13); #11=PRESENTATION_LAYER_ASSIGNMENT('Default','',(#12)); #12=SHELL_BASED_SURFACE_MODEL('shell_1',(#14)); #13=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('shell_rep_0',(#12,#94),#91); #14=OPEN_SHELL('',(#15,#16)); #15=ADVANCED_FACE('',(#17),#72,.T.); #16=ADVANCED_FACE('',(#18),#73,.T.); #17=FACE_OUTER_BOUND('',#19,.T.); #18=FACE_OUTER_BOUND('',#20,.T.); #19=EDGE_LOOP('',(#21,#22,#23,#24)); #20=EDGE_LOOP('',(#25,#26,#27)); #21=ORIENTED_EDGE('',*,*,#48,.T.); #22=ORIENTED_EDGE('',*,*,#49,.T.); #23=ORIENTED_EDGE('',*,*,#50,.T.); #24=ORIENTED_EDGE('',*,*,#51,.T.); #25=ORIENTED_EDGE('',*,*,#52,.T.); #26=ORIENTED_EDGE('',*,*,#53,.T.); #27=ORIENTED_EDGE('',*,*,#48,.F.); #28=PCURVE('',#72,#35); #29=PCURVE('',#72,#36); #30=PCURVE('',#72,#37); #31=PCURVE('',#72,#38); #32=PCURVE('',#73,#39); #33=PCURVE('',#73,#40); #34=PCURVE('',#73,#41); #35=DEFINITIONAL_REPRESENTATION('',(#55),#140); #36=DEFINITIONAL_REPRESENTATION('',(#57),#140); #37=DEFINITIONAL_REPRESENTATION('',(#59),#140); #38=DEFINITIONAL_REPRESENTATION('',(#61),#140); #39=DEFINITIONAL_REPRESENTATION('',(#63),#140); #40=DEFINITIONAL_REPRESENTATION('',(#65),#140); #41=DEFINITIONAL_REPRESENTATION('',(#66),#140); #42=SURFACE_CURVE('',#54,(#28,#34),.PCURVE_S1.); #43=SURFACE_CURVE('',#56,(#29),.PCURVE_S1.); #44=SURFACE_CURVE('',#58,(#30),.PCURVE_S1.); #45=SURFACE_CURVE('',#60,(#31),.PCURVE_S1.); #46=SURFACE_CURVE('',#62,(#32),.PCURVE_S1.); #47=SURFACE_CURVE('',#64,(#33),.PCURVE_S1.); #48=EDGE_CURVE('',#69,#68,#42,.T.); #49=EDGE_CURVE('',#68,#70,#43,.T.);
```

```text
#50=EDGE_CURVE('',#70,#71,#44,.T.); #51=EDGE_CURVE('',#71,#69,#45,.T.); #52=EDGE_CURVE('',#69,#67,#46,.T.); #53=EDGE_CURVE('',#67,#68,#47,.T.); #54=B_SPLINE_CURVE_WITH_KNOTS('',1,(#113,#114),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,7.07106781186547),.UNSPECIFIED.); #55=B_SPLINE_CURVE_WITH_KNOTS('',1,(#115,#116),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,7.07106781186547),.UNSPECIFIED.); #56=B_SPLINE_CURVE_WITH_KNOTS('',1,(#117,#118),.UNSPECIFIED.,.F.,.F.,(2, 2),(5.,10.),.UNSPECIFIED.); #57=B_SPLINE_CURVE_WITH_KNOTS('',1,(#119,#120),.UNSPECIFIED.,.F.,.F.,(2, 2),(5.,10.),.UNSPECIFIED.); #58=B_SPLINE_CURVE_WITH_KNOTS('',1,(#121,#122),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #59=B_SPLINE_CURVE_WITH_KNOTS('',1,(#123,#124),.UNSPECIFIED.,.F.,.F.,(2, 2),(-7.07106781186547,0.),.UNSPECIFIED.); #60=B_SPLINE_CURVE_WITH_KNOTS('',1,(#125,#126),.UNSPECIFIED.,.F.,.F.,(2, 2),(-10.,-5.),.UNSPECIFIED.); #61=B_SPLINE_CURVE_WITH_KNOTS('',1,(#127,#128),.UNSPECIFIED.,.F.,.F.,(2, 2),(-10.,-5.),.UNSPECIFIED.); #62=B_SPLINE_CURVE_WITH_KNOTS('',1,(#129,#130),.UNSPECIFIED.,.F.,.F.,(2, 2),(-5.,0.),.UNSPECIFIED.); #63=B_SPLINE_CURVE_WITH_KNOTS('',1,(#131,#132),.UNSPECIFIED.,.F.,.F.,(2, 2),(-5.,0.),.UNSPECIFIED.); #64=B_SPLINE_CURVE_WITH_KNOTS('',1,(#133,#134),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,5.),.UNSPECIFIED.); #65=B_SPLINE_CURVE_WITH_KNOTS('',1,(#135,#136),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,5.),.UNSPECIFIED.); #66=B_SPLINE_CURVE_WITH_KNOTS('',1,(#137,#138),.UNSPECIFIED.,.F.,.F.,(2, 2),(0.,7.07106781186547),.UNSPECIFIED.); #67=VERTEX_POINT('',#108); #68=VERTEX_POINT('',#109); #69=VERTEX_POINT('',#110); #70=VERTEX_POINT('',#111); #71=VERTEX_POINT('',#112); #72=B_SPLINE_SURFACE_WITH_KNOTS('',1,1,((#100,#101),(#102,#103)), .UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.,7.07106781186547),(0.,10.), .UNSPECIFIED.); #73=B_SPLINE_SURFACE_WITH_KNOTS('',1,1,((#104,#105),(#106,#107)), .UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.,5.),(0.,5.),.UNSPECIFIED.); #74=SHAPE_DEFINITION_REPRESENTATION(#75,#92); #75=PRODUCT_DEFINITION_SHAPE('Document','',#77); #76=PRODUCT_DEFINITION_CONTEXT('3D visiblespaceMechanical visiblespaceParts ' ,#81,'design '); #77=PRODUCT_DEFINITION('A','First visiblespaceversion' ,#78,#76); #78=PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('A', 'First visiblespace v e r s i o n ' ,#83 ,. MADE .); #79=PRODUCT_RELATED_PRODUCT_CATEGORY('tool','tool',(#83)); #80=APPLICATION_PROTOCOL_DEFINITION('Draft visiblespaceInternational visiblespaceStandard ', 'automotive_design',1999,#81); #81=APPLICATION_CONTEXT( 'data visiblespace f o r visiblespace a u t o m o t i v e visiblespace m e c h a n i c a l visiblespace d e s i g n visiblespace p r o c e s s e s ' ); #82=PRODUCT_CONTEXT('3D visiblespace Mechanical visiblespace Parts ' ,#81,'mechanical '); #83=PRODUCT('Document','Document','Rhino visiblespaceconverted visiblespaceto visiblespace STEP ' ,(#82)); #84=( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) ); #85=( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) ); #86=DIMENSIONAL_EXPONENTS(0.,0.,0.,0.,0.,0.,0.); #87=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.01745329252),#85); #88=( CONVERSION_BASED_UNIT('DEGREES',#87) NAMED_UNIT(#86) PLANE_ANGLE_UNIT() ); #89=( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() ); #90=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#84, 'DISTANCE_ACCURACY_VALUE', 'Maximum visiblespace model visiblespace s p a c e visiblespace d i s t a n c e visiblespace b e t w e e n visiblespace g e o m e t r i c visiblespace e n t i t i e s visiblespace a t visiblespace a s s e r t e d visiblespace c onnectivities'); #91=( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#90)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#89,#88,#84)) REPRESENTATION_CONTEXT('ID1','3D') ); #92=SHAPE_REPRESENTATION('Document',(#93,#94),#91); #93=AXIS2_PLACEMENT_3D('',#99,#95,#96); #94=AXIS2_PLACEMENT_3D('',#139,#97,#98); #95=DIRECTION('',(0.,0.,1.)); #96=DIRECTION('',(1.,0.,0.)); #97=DIRECTION('',(0.,0.,1.)); #98=DIRECTION('',(1.,0.,0.)); #99=CARTESIAN_POINT('',(0.,0.,0.)); #100=CARTESIAN_POINT('',(5.,0.,-5.)); #101=CARTESIAN_POINT('',(5.,0.,5.)); #102=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,-5.)); #103=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #104=CARTESIAN_POINT('',(0.,0.,0.)); #105=CARTESIAN_POINT('',(5.,0.,0.)); #106=CARTESIAN_POINT('',(0.,5.,0.)); #107=CARTESIAN_POINT('',(5.,5.,0.)); #108=CARTESIAN_POINT('',(0.,0.,0.)); #109=CARTESIAN_POINT('',(0.,5.,0.)); #110=CARTESIAN_POINT('',(5.,0.,0.)); #111=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #112=CARTESIAN_POINT('',(5.,0.,5.)); #113=CARTESIAN_POINT('',(5.,0.,0.)); #114=CARTESIAN_POINT('',(0.,5.,0.)); #115=CARTESIAN_POINT('',(0.,5.)); #116=CARTESIAN_POINT('' ,(7.07106781186547,5.)); #117=CARTESIAN_POINT('',(0.,5.,0.));
```

```text
#118=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #119=CARTESIAN_POINT('' ,(7.07106781186547,5.)); #120=CARTESIAN_POINT('' ,(7.07106781186547,10.)); #121=CARTESIAN_POINT('' ,(8.88178419700125E-16,5.,5.)); #122=CARTESIAN_POINT('',(5.,0.,5.)); #123=CARTESIAN_POINT('' ,(7.07106781186547,10.)); #124=CARTESIAN_POINT('',(0.,10.)); #125=CARTESIAN_POINT('',(5.,0.,5.)); #126=CARTESIAN_POINT('',(5.,0.,0.)); #127=CARTESIAN_POINT('',(0.,10.)); #128=CARTESIAN_POINT('',(0.,5.)); #129=CARTESIAN_POINT('',(5.,0.,0.)); #130=CARTESIAN_POINT('',(0.,0.,0.)); #131=CARTESIAN_POINT('',(0.,5.)); #132=CARTESIAN_POINT('',(0.,0.)); #133=CARTESIAN_POINT('',(0.,0.,0.)); #134=CARTESIAN_POINT('',(0.,5.,0.)); #135=CARTESIAN_POINT('',(0.,0.)); #136=CARTESIAN_POINT('',(5.,0.)); #137=CARTESIAN_POINT('',(0.,5.)); #138=CARTESIAN_POINT('',(5.,0.)); #139=CARTESIAN_POINT('',(0.,0.,0.)); #140=( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('pspace','') ); ENDSEC; END-ISO -10303-21;
```

## References

- Abi-Ezzi SS, Shirman LA (1991) Tessellation of curved surfaces under highly varying transformations. In: Proceedings of EUROGRAPHICS, vol 91, p 385-397

- Abi-Ezzi SS, Subramaniam S (1994) Fast dynamic tessellation of trimmed NURBS surfaced. In: Computer Graphics Forum, vol 13, p 107-126

- Abrams SL, Cho W, Hu CY, Maekawa T, Patrikalakis NM, Sherbrooke EC, Ye X (1998) efficient and reliable methods for rounded-interval arithmetic. Comput Aided Des 30(8):657-665

- Agoston MK (2005) Computer graphics and geometric modeling. Springer, London

- Alavala CR (2013) CAD CAM: concepts and applications. PHI, New Delhi

- Aomura S, Uehara T (1990) Self-intersection of an offset surface. Comput Aided Des 22(7):417-421

- Apostolatos A, Schmidt R, Wüchner R, Bletzinger KU (2014) A Nitsche-type formulation and comparison of the most common domain decomposition methods in isogeometric analysis. Int J Numer Methods Eng 97(7):473-504

- Appel A (1968) Some techniques for shading machine renderings of solids. In: Proceedings of the spring joint computer conference. ACM, New York, p 37-45

- Applegarth I, Catley D, Bradley I (1989) Clipping of B-spline patches at surface curves. In: Handscomb DC (ed) The mathematics of surfaces III. Clarendon Press, Oxford, pp 229-242

- Aurenhammer F (1991) Voronoi diagrams-a survey of a fundamental geometric data structure. ACM Comput Surv 23(3):345-405

- Auricchio F, Beirão Da Veiga L, Hughes TJR, Reali A, Sangalli G (2010) Isogeometric collocation methods. Math Models Methods Appl Sci 20(11):2075-2107

- Babuška I (1973) The finite element method with Lagrangian multipliers. Numer Math 20(3):179-192

- Babuška I (1973) Finite-element method with penalty. Math Comput 27(122):221-228

- Bajaj CL, Hoffmann CM, Lynch RE, Hopcroft JEH (1988) Tracing surface intersections. Comput Aided Geom Des 5(4):285-307

- Ballard DH (1981) Strip trees: a hierarchical representation for curves. Commun ACM 24(5):310-321

- Barber CB, Dobkin DP, Huhdanpaa H (1996) The quickhull algorithm for convex hulls. ACM Trans Math Softw 22(4):469-483

- Barbosa HJC, Hughes TJR (1991) The finite element method with Lagrange multipliers on the boundary: circumventing the Babuška-Brezzi condition. Comput Methods Appl Mech Eng 85(1):109-128

- Barbosa HJC, Hughes TJR (1992) Boundary Lagrange multipliers in finite element methods: error analysis in natural norms. Numer Math 62:1-15

- Barnhill RE, Farin G, Jordan M, Piper BR (1987) Surface surface intersection. Comput Aided Geom Des 4(1):3-16

- Barnhill RE, Kersey S (1990) A marching method for parametric surface surface intersection. Comput Aided Geom Des 7(1-4):257-280

- Baumgart BG (1972) Winged edge polyhedron representation. Technical report, DTIC Document

- Bazilevs Y, Calo VM, Cottrell JA, Evans JA, Hughes TJR, Lipton S, Scott MA, Sederberg TW (2010) Isogeometric analysis using T-splines. Comput Methods Appl Mech Eng 199(5-8):229-263 Bazilevs Y, Hughes TJR (2007) Weak imposition of Dirichlet boundary conditions in fluid mechanics. Comput Fluids 36(1):12-26 Bazilevs Y, Michler C, Calo VM, Hughes TJR (2007) Weak Dirichlet boundary conditions for wall-bounded turbulent flows. Comput Methods Appl Mech Eng 196(49-52):4853-4862 Beer G, Marussig B, Zechner J (2015) A simple approach to the numerical simulation with trimmed CAD surfaces. Comput Methods Appl Mech Eng 285:776-790 Benouamer MO, Michelucci D, Peroche B (1994) Error-free boundary evaluation based on a lazy rational arithmetic-a detailed implementation. Comput Aided Des 26(6):403-416 Benthin C, Wald I, Slusallek P (2004) Interactive ray tracing of free-form surfaces. In: Proceedings of the 3rd international conference on computer graphics, virtual reality, visualisation and interaction in Africa. ACM, p 99-106 Bern M, Eppstein D, Gilbert J (1994) Provably good mesh generation. J Comput Syst Sci 48(3):384-409 Bézier P (1974) Mathematical and practical possibilities of UNISURF. In: Barnhill RE, Riesenfeld RF (eds) Computer aided geometric design. Academic, New York, pp 127-152 Biermann H, Kristjansson D, Zorin D (2001) Approximate Boolean operations on free-form solids. In: Proceedings of the 28th annual conference on computer graphics and interactive techniques, SIGGRAPH '01. ACM, p 185-194 Biswas A, Fenves SJ, Shapiro V, Sriram R (2008) representation of heterogeneous material properties in the Core Product Model. Eng Comput 24(1):43-58 Boehm W (1980) Inserting new knots into B-spline curves. Comput Aided Des 12(4):199-201 de Boor C (1972) On calculating with B-splines. J Approx Theory 6(1):50-62 de Boor C (2001) A practical guide to splines. In: Applied mathematical sciences, vol 27. Springer, New York 35. de Boor C, Fix GJ (1973) Spline approximation by quasiinterpolants. J Approx Theory 8(1):19-45 Braid IC (1974) Designing with volumes, 2nd edn. Cantab Press, Cambridge University, Cambridge Breitenberger M (2016) CAD-integrated design and analysis of shell structures. PhD Thesis, Technische Universität München Breitenberger M, Apostolatos A, Philipp B, Wüchner R, Bletzinger KU (2015) analysis in computer aided design: nonlinear isogeometric B-Rep analysis of shell structures. Comput Methods Appl Mech Eng 284:401-457 Brivadis E, Buffa A, Wohlmuth B, Wunderlich L (2015) Isogeometric mortar methods. Comput Methods Appl Mech Eng 284:292-319 Brown CM (1982) PADL-2: a technical summary. IEEE Comput Graph Appl 2(2):69-84 Brunnett G (1995) Geometric design with trimmed surfaces. In: Hagen H, Farin G, Noltemeierm H (eds) Geometric modelling: Dagstuhl 1993, computing Supplement 10. Springer, Berlin, pp 101-115 Burman E, Hansbo P (2012) Fictitious domain finite element methods using cut elements: II. A stabilized Nitsche method. Appl Numer Math 62(4):328-341 C3D Labs. C3D kernel documentation. http: c3d.ascon.net doc math class_mb_surface_intersection_curve.html#details. Accessed 19 Aug 2016 Campagna S, Slusallek P, Seidel HP (1997) Ray tracing of spline surfaces: Bézier clipping, Chebyshev boxing, and bounding volume hierarchy-a critical comparison with new results. Vis Comput 13(6):265-282

- Campbell RJ, Flynn PJ (2001) A survey of free-form object representation and recognition techniques. Comput Vis Image Underst 81(2):166-210

- Carlson WE (1982) An algorithm and data structure for 3D object synthesis using surface patch intersections. SIGGRAPH Comput Graph 16(3):255-263

- Casale MS (1987) Free-form solid modeling with trimmed surface patches. IEEE Comput Graph Appl 7(1):33-43

- Casale MS, Bobrow JE (1989) The analysis of solids without mesh generation using trimmed patch boundary elements. Eng Comput 5(3-4):249-257

- Casale MS, Bobrow JE (1989) A set operation algorithm for sculptured solids modeled with trimmed patches. Comput Aided Geom Des 6(3):235-247

- Casale MS, Bobrow JE, Underwood R (1992) Trimmed-patch boundary elements: bridging the gap between solid modeling and engineering analysis. Comput Aided Des 24(4):193-199

- Cashman TJ, Augsdörfer UH, Dodgson NA, Sabin MA (2009) NURBS with extraordinary points: high-degree, nonuniform, rational subdivision schemes. ACM Trans Graph 28(3):46:1-46:9

- Catmull E (1974) A subdivision algorithm for computer display of curved surfaces. Technical report. Computer Science Department, University of Utah

- Catmull E, Clark J (1978) Recursively generated B-spline surfaces on arbitrary topological meshes. Comput Aided Des 10(6):350-355

- Chaikin GM (1974) An algorithm for high-speed curve generation. Comput Graph Image Process 3(4):346-349

- Chew LP (1993) Guaranteed-quality mesh generation for curved surfaces. In: Proceedings of the ninth annual symposium on computational geometry. ACM, New York, p 274-280

- Chiyokura H, Kimura F (1983) Design of solids with free-form surfaces. SIGGRAPH Comput Graph 17(3):289-298

- Cho W, Maekawa T, Patrikalakis NM, Peraire J (1999) Topologically reliable approximation of trimmed polynomial surface patches. Graph Models Image Process 61(2):84-109

- Cho W, Patrikalakis NM, Peraire J (1998) Approximate development of trimmed patches for surface tessellation. Comput Aided Des 30(14):1077-1087

- Cirak F, Long Q (2011) Subdivision shells with exact boundary control and non-manifold geometry. Int J Numer Methods Eng 88(9):897-923

- Cohen E, Lyche T, Riesenfeld R (1980) Discrete B-splines and subdivision techniques in computer-aided geometric design and computer graphics. Comput Graph Image Process 14(2):87-111

- Cohen E, Martin T, Kirby RM, Lyche T, Riesenfeld RF (2010) analysis-aware modeling: understanding quality considerations in modeling for isogeometric analysis. Comput Methods Appl Mech Eng 199(5-8):334-356

- Cohen E, Riesenfeld RF, Elber G (2001) Geometric modeling with splines: an introduction. A K Peters, Natick

- Collin A, Sangalli G, Takacs T (2016) analysis-suitable G 1 multi-patch parametrizations for C 1 isogeometric spaces. Comput Aided Geom Des 47:93-113 (SI: New Developments Geometry)

- Cook RL, Porter T, Carpenter L (1984) Distributed ray tracing. SIGGRAPH Comput Graph 18(3):137-145

- Corney J, Lim T (2001) 3D modeling with ACIS. Saxe-Coburg, Stirling

- Cottrell JA, Hughes TJR, Bazilevs Y (2009) Isogeometric analysis: toward integration of CAD and FEA. Wiley, Chichester

- Cottrell JA, Hughes TJR, Reali A (2007) Studies of refinement and continuity in isogeometric structural analysis. Comput Methods Appl Mech Eng 196(41-44):4160-4183 Cottrell JA, Reali A, Bazilevs Y, Hughes TJR (2006) Isogeometric analysis of structural vibrations. Comput Methods Appl Mech Eng 195(41-43):5257-5296 Dehaemer MJ Jr, Zyda MJ (1991) Simplification of objects rendered by polygonal approximations. Comput Graph 15(2):175-184 DeRose T, Kass M, Truong T (1998) Subdivision surfaces in character animation. In: Proceedings of the 25th annual conference on computer graphics and interactive techniques. ACM, p 85-94 DeRose TD, Goldman RN, Hagen H, Mann S (1993) Functional composition algorithms via blossoming. ACM Trans Graph 12(2):113-135 Dijkstra EW (1959) A note on two problems m connexion with graphs. Numer Math 1:269-271 Dobkin DP, Laszlo MJ (1987) Primitives for the manipulation of three-dimensional subdivisions. In: Proceedings of the third annual symposium on computational geometry. ACM, New York, p 86-99 Dolenc A, Mäkelä I (1994) Optimized triangulation of parametric surfaces. In: Bowyer A (ed) Computer-aided surface geometry and design: the mathematics of surfaces IV, vol 48. Oxford University Press, Institute of Mathematics and Its Applications, p 169-183 Doo D, Sabin M (1978) Behaviour of recursive division surfaces near extraordinary points. Comput Aided Des 10(6):356-360 Duff T (1992) Interval arithmetic recursive subdivision for implicit functions and constructive solid geometry. SIGGRAPH Comput Graph 26(2):131-138 Edelsbrunner H, Mücke EP (1990) Simulation of simplicity: a technique to cope with degenerate cases in geometric algorithms. ACM Trans Graph 9(1):66-104 Efremov A, Havran V, Seidel HP (2005) Robust and numerically stable Bézier clipping method for ray tracing NURBS surfaces. In: Proceedings of the 21st spring conference on computer graphics. ACM, New York, p 127-135 Elber G (1996) Error bounded piecewise linear approximation of freeform surfaces. Comput Aided Des 28(1):51-57 Embar A, Dolbow J, Harari I (2010) Imposing Dirichlet boundary conditions with Nitsche's method and spline-based finite elements. Int J Numer Methods Eng 83(7):877-898 Evans JA, Hughes TJR (2013) Isogeometric divergence-conforming B-splines for the steady Navier-Stokes equations. Math Models Methods Appl Sci 23(8):1421-1478 Fang SF, Bruderlin B, Zhu XH (1993) Robustness in solid modeling: a tolerance-based intuitionistic approach. Comput Aided Des 25(9):567-576 Farin G (2002) curves and surfaces for CAGD: a practical guide, 5th edn. Morgan Kaufmann, San Francisco Farouki RT (1986) The characterization of parametric surface sections. Comput Vis Graph Image Process 33(2):209-236 Farouki RT (1987) Trimmed-surface algorithms for the evaluation and interrogation of solid boundary representations. IBM J Res Dev 31(3):314-334 Farouki RT (1999) Closing the gap between CAD model and downstream application. SIAM News 32(5):303-319 Farouki RT, Han CY, Hass J, Sederberg TW (2004) Topologically consistent trimmed surface approximations based on triangular patches. Comput Aided Geom Des 21(5):459-478 Farouki RT, Hinds JK (1985) A hierarchy of geometric forms. IEEE Comput Graph Appl 5(5):51-78 Filip D, Magedson R, Markot R (1986) Surface algorithms using bounds on derivatives. Comput Aided Geom Des 3(4):295-311 Flöry S, Hofer M (2008) Constrained curve fitting on manifolds. Comput Aided Des 40(1):25-34

- Foley T, Sugerman J (2005) KD-tree acceleration structures for a GPU raytracer. In: Proceedings of the conference on graphics hardware. ACM, New York, p 15-22

- Forsythe GE (1970) Pitfalls in computation, or why a math book isn't enough. Am Math Mon 77(9):931-956

- Fortune S (1995) Polyhedral modelling with exact arithmetic. In: Proceedings of the third ACM symposium on solid modeling and applications. ACM, p 225-234

- Frey PJ, George PL (2010) Mesh generation: application to finite elements, 2nd edn. Wiley, New York

- Fries TP, Omerović S (2016) Higher-order accurate integration of implicit geometries. Int J Numer Methods Eng 106(5):323-371

- Gaul L, Kögl M, Wagner M (2003) Boundary element methods for engineers and scientists: an introductory course with advanced topics. Springer, Berlin

- Geimer M, Abert O (2005) Interactive ray tracing of trimmed bicubic Bézier surfaces without triangulation. In: Proceedings of WSCG, p 71-78

- George PL, Borouchaki H, Frey PJ, Laug P, Saltel E (2004) Chapter 17: mesh generation and mesh adaptivity: theory and techniques. In: Stein E, de Borst R, Hughes TJR (eds) Encyclopedia of computational mechanics. Fundamentals, vol 1. Wiley, Chichester, pp 502-532

- Glassner AS (1989) An introduction to ray tracing. Academic, London

- Goldman RN, Filip DJ (1987) Conversion from Bézier rectangles to Bézier triangles. Comput Aided Des 19(1):25-27

- Goldstein BLM, Kemmerer SJ, Parks CH (1998) A brief history of early product data exchange standards. NISTIR 6221. US Department of Commerce, Technology Administration, Electronics and Electrical engineering Laboratory, National Institute of Standards and Technology

- Golovanov N (2014) Geometric modeling. Academia Publishing House, Praha

- Gordon WJ, Hall CA (1973) Transfinite element methodsblending-function interpolation over arbitrary curved element domains. Numer Math 21(2):109-129

- Gossard DC, Zuffante RP, Sakurai H (1988) Representing dimensions, tolerances, and features in MCAE systems. IEEE Comput Graph Appl 8(2):51-59

- Grandine TA, Klein FW (1997) A new approach to the surface intersection problem. Comput Aided Geom Des 14(2):111-134

- Guibas L, Stolfi J (1985) Primitives for the manipulation of general subdivisions and the computation of Voronoi diagrams. ACM Trans Graph 4(2):74-123

- Guo Y, Ruess M, Schillinger D (2016) A parameter-free variational coupling approach for trimmed isogeometric thin shells. Comput Mech 59(4):693-715

- Guthe M, Balázs A, Klein R (2005) GPU-based trimming and tessellation of NURBS and T-spline surfaces. ACM Trans Graph 24(3):1016-1023

- Hales TC (2007) The Jordan curve theorem, formally and informally. Am Math Mon 114(10):882-894

- Hamann B, Tsai PY (1996) A tessellation algorithm for the representation of trimmed NURBS surfaces with arbitrary trimming curves. Comput Aided Des 28(6-7):461-472

- Hanna SL, Abel JF, Greenberg DP (1983) intersection of parametric surfaces by means of look-up tables. IEEE Comput Graph Appl 3(7):39-48

- Hansbo P (2005) Nitsche's method for interface problems in computational mechanics. GAMM-Mitt 28(2):183-206

- Harbrecht H, Randrianarivony M (2010) From computer aided design to wavelet BEM. Comput Vis Sci 13(2):69-82 Hardwick MF, Clay RL, Boggs PT, Walsh EJ, Larzelere AR, Altshuler A (2005) DART system analysis. Technical report SAND2005-4647. Sandia National Laboratories Hass J, Farouki RT, Han CY, Song X, Sederberg TW (2007) Guaranteed consistency of surface intersections and trimmed surfaces using a coupled topology resolution and domain decomposition scheme. Adv Comput Math 27(1):1-26 Havran V (2000) Heuristic ray shooting algorithms. PhD Thesis, Czech Technical University, Prague Hickey T, Ju Q, Van Emden MH (2001) Interval arithmetic: from principles to implementation. J ACM 48(5):1038-1068 Hiemstra RR, Calabrò F, Schillinger D, Hughes TJR (2016) Optimal and reduced quadrature rules for tensor product and hierarchically refined splines in isogeometric analysis. Comput Methods Appl Mech Eng. doi:10.1016 j.cma.2016.10.049 Hofer M, Pottmann H (2004) Energy-minimizing splines in manifolds. ACM Trans Graph 23(3):284-293 Hoffmann CM (1989) Geometric and solid modeling. Morgan Kaufmann, San Mateo Hoffmann CM (1989) The problems of accuracy and robustness in geometric computation. Computer 22(3):31-39 Hoffmann CM, Hopcroft JE, Karasick MS (1988) Towards implementing robust geometric computations. In: Proceedings of the symposium on computational geometry. ACM, p 106-117 Hoffmann CM, Hopcroft JE, Karasick MS (1989) Robust set operations on polyhedral solids. IEEE Comput Graph Appl 9(6):50-59 Höllig K (2003) Finite element methods with B-splines. In: Frontiers in applied mathematics, vol 26. SIAM, Philadelphia Höllig K, Reif U (2003) Nonuniform web-splines. Comput Aided Geom Des 20(5):277-294 Höllig K, Reif U, Wipper J (2001) B-spline approximation of Neumann problems. Mathematisches Institut A, University of Stuttgart Höllig K, Reif U, Wipper J (2002) Weighted extended B-spline approximation of Dirichlet problems. SIAM J Numer Anal 39(2):442-462 Hong YS, Chang TC (2002) A comprehensive review of tolerancing research. Int J Prod Res 40(11):2425-2459 Hoschek J (1987) Approximate conversion of spline curves. Comput Aided Geom Des 4(1-2):59-66 Hoschek J, Lasser D (1992) Grundlagen der geometrischen Datenverarbeitung. Vieweg+Teubner. English version 'Fundamentals of Computer Aided Geometric Design' translated by Schumaker LL Hoschek J, Schneider FJ (1990) Spline conversion for trimmed rational Bézier-and B-spline surfaces. Comput Aided Des 22(9):580-590 Hoschek J, Schneider FJ, Wassum P (1989) Optimal approximate conversion of spline surfaces. Comput Aided Geom Des 6(4):293-306 Houghton EG, Emnett RF, Factor JD, Sabharwal CL (1985) Implementation of a divide-and-conquer method for intersection of parametric surfaces. Comput Aided Geom Des 2(1):173-183 Hu CY, Maekawa T, Patrikalakis NM, Ye X (1997) Robust interval algorithm for surface intersections. Comput Aided Des 29(9):617-627 Hu CY, Patrikalakis NM, Ye X (1996) Robust interval solid modelling part I: representations. Comput Aided Des 28(10):807-817 Hu CY, Patrikalakis NM, Ye X (1996) Robust interval solid modelling part II: boundary evaluation. Comput Aided Des 28(10):819-830

- Hu YP, Sun TC (1997) Moving a B-spline surface to a curvea trimmed surface matching algorithm. Comput Aided Des 29(6):449-455

- Huerta A, Belytschko T, Fernández-Méndez S, Rabczuk T (2004) Chapter 10: meshfree methods. In: Stein E, de Borst R, Hughes TJR (eds) Encyclopedia of computational mechanics. Fundamentals, vol 1. Wiley, Chichester, pp 279-309

- Hughes TJR (2000) The finite element method: linear static and dynamic finite element analysis. Courier Corporation, Chicago

- Hughes TJR, Cottrell JA, Bazilevs Y (2005) Isogeometric analysis: CAD, finite elements, NURBS, exact geometry and mesh refinement. Comput Methods Appl Mech Eng 194(39-41):4135-4195

- Hughes TJR, Sangalli G (2016) Mathematics of isogeometric analysis: a conspectus. In: Stein E, de Borst R, Hughes TJR (eds) Encyclopedia of computational mechanics. Volume set, 2nd edn, vol 3. Wiley, Chichester

- Hui KC, Wu YB (2005) Feature-based decomposition of trimmed surface. Comput Aided Des 37(8):859-867

- Jackson DJ (1995) Boundary representation modelling with local tolerances. In: Proceedings of the symposium on solid modeling and applications. ACM, p 247-254

- Joy KI, Bhetanabhotla MN (1986) Ray tracing parametric surface patches utilizing numerical techniques and ray coherence. SIGGRAPH Comput Graph 20(4):279-285

- Jüttler B, Mantzaflaris A, Perl R, Rumpf M (2016) On numerical integration in isogeometric subdivision methods for PDEs on surfaces. Comput Methods Appl Mech Eng 302:131-146

- Kajiya JT (1982) Ray tracing parametric patches. SIGGRAPH Comput Graph 16(3):245-254

- Kang P, Youn SK (2015) Isogeometric analysis of topologically complex shell structures. Finite Elem Anal Des 99:68-81

- Kang P, Youn SK (2016) Isogeometric shape optimization of trimmed shell structures. Struct Multidiscip Optim 53(4):825-845

- Kapl M, Buchegger F, Bercovier M, Jüttler B (2016) Isogeometric analysis with geometrically continuous functions on planar multi-patch geometries. Comput Methods Appl Mech Eng. doi:10.1016 j.cma.2016.06.002

- Kapl M, Vitrih V, Jüttler B, Birner K (2015) Isogeometric analysis with geometrically continuous functions on two-patch geometries. Comput Math Appl 70(7):1518-1538

- Kasik DJ, Buxton W, Ferguson DR (2005) Ten CAD challenges. IEEE Comput Graph Appl 25(2):81-92

- Katz S, Sederberg TW (1988) Genus of the intersection curve of two rational surface patches. Comput Aided Geom Des 5(3):253-258

- Kaufman A, Cohen D, Yagel R (1993) Volume graphics. Computer 26(7):51-64

- Kay TL, Kajiya JT (1986) Ray tracing complex scenes. SIGGRAPH Comput Graph 20(4):269-278

- Kennicott PR, Morea G, Reid E, Parks C, Rinaudot G, Harrod Jr DA, Gruttke WB (1996) Initial graphics exchange specification IGES 5.3. ANS US PRO IPO-100-1996. US Product Data Association

- Keyser J, Culver T, Manocha D, Krishnan S (1999) MAPC: a library for efficient and exact manipulation of algebraic points and curves. In: Proceedings of the fifteenth annual symposium on computational geometry. ACM, p 360-369

- Keyser J, Culver T, Manocha D, Krishnan S (2000) efficient and exact manipulation of algebraic points and curves. Comput Aided Des 32(11):649-662

- Keyser J, Krishnan S, Manocha D (1999) efficient and accurate B-rep generation of low degree sculptured solids using exact arithmetic: I. representations. Comput Aided Geom Des 16(9):841-859 Keyser J, Krishnan S, Manocha D (1999) efficient and accurate B-rep generation of low degree sculptured solids using exact arithmetic: II. Computation. Comput Aided Geom Des 16(9):861-882 Kim HJ, Seo YD, Youn SK (2009) Isogeometric analysis for trimmed CAD surfaces. Comput Methods Appl Mech Eng 198(37-40):2982-2995 Kim HJ, Seo YD, Youn SK (2010) Isogeometric analysis with trimming technique for problems of arbitrary complex topology. Comput Methods Appl Mech Eng 199(45-48):2796-2812 Kim J, Pratt MJ, Iyer RG, Sriram RD (2008) Standardized data exchange of CAD models with design intent. Comput Aided Des 40(7):760-777 Kleiss SK, Pechstein C, Jüttler B, Tomar S (2012) IETI-isogeometric tearing and interconnecting. Comput Methods Appl Mech Eng 247-248:201-215 Kollmannsberger S, Özcan A, Baiges J, Ruess M, Rank E, Reali A (2015) Parameter-free, weak imposition of Dirichlet boundary conditions and coupling of trimmed and non-conforming patches. Int J Numer Methods Eng 101(9):670-699 Koparkar PA, Mudur SP (1983) A new class of algorithms for the processing of parametric curves. Comput Aided Des 15(1):41-45 Korneev VG, Langer U (2004) Chapter 22: domain decomposition methods and preconditioning. In: Stein E, de Borst R, Hughes TJR (eds) Encyclopedia of computational mechanics. Fundamentals, vol 1. Wiley, Chichester, pp 617-647 Kosinka J, Cashman TJ (2015) Watertight conversion of trimmed CAD surfaces to Clough-Tocher splines. Comput Aided Geom 37:25-41 Kriezis GA, Patrikalakis NM, Wolter FE (1992) Topological and differential-equation methods for surface intersections. Comput Aided Des 24(1):41-55 Kriezis GA, Prakash PV, Patrikalakis NM (1990) Method for intersecting algebraic surfaces with rational polynomial patches. Comput Aided Des 22(10):645-654 Krishnan S, Manocha D (1997) An efficient surface intersection algorithm based on lower-dimensional formulation. ACM Trans Graph 16(1):74-106 Krishnan S, Manocha D, Gopi M, Culver T, Keyser J (2001) BOOLE: a boundary evaluation system for Boolean combinations of sculptured solids. Int J Comput Geom Appl 11(1):105-144 Krüger J, Westermann R (2003) Acceleration techniques for GPU-based volume rendering. In: Proceedings of the IEEE visualization. IEEE Computer Society, p 287-292 Kudela L (2013) Highly accurate subcell integration in the context of the finite cell method. Master's Thesis, Technical University Munich Kudela L, Zander N, Bog T, Kollmannsberger S, Rank E (2015) efficient and accurate numerical quadrature for immersed boundary methods. Adv Model Simul Eng Sci 2(1):1-22 Kudela L, Zander N, Kollmannsberger S, Rank E (2016) Smart octrees: accurately integrating discontinuous functions in 3D. Comput Methods Appl Mech Eng 306:406-426 Kumar S, Manocha D (1995) efficient rendering of trimmed NURBS surfaces. Comput Aided Des 27(7):509-521 LaCourse DE (1995) Handbook of solid modeling. McGrawHill, Inc., New York Lane JM, Carpenter L (1979) A generalized scan line algorithm for the computer display of parametrically defined surfaces. Comput Graph Image Process 11(3):290-297 Lane JM, Carpenter LC, Whitted T, Blinn JF (1980) Scan line methods for displaying parametrically defined surfaces. Commun ACM 23(1):23-34

- Lane JM, Riesenfeld RF (1980) A theoretical development for the computer generation and display of piecewise polynomial surfaces. IEEE Trans Pattern Anal Mach Intell PAMI-2(1):35-46

- Lasser D (1986) intersection of parametric surfaces in the Bernstein-Bézier representation. Comput Aided Des 18(4):186-192

- Lasser D (2008) Triangular subpatches of rectangular Bézier surfaces. Comput Math Appl 55(8):1706-1719

- Lasserre J (1998) Integration on a convex polytope. Proc Am Math Soc 126(8):2433-2441

- Li K, Qian X (2011) Isogeometric analysis and shape optimization via boundary integral. Comput Aided Des 43(11):1427-1437

- Lien SL, Shantz M, Pratt V (1987) Adaptive forward differencing for rendering curves and surfaces. SIGGRAPH Comput Graph 21(4):111-118

- Limaiem A, Trochu F (1995) Geometric algorithms for the intersection of curves and surfaces. Comput Graph 19(3):391-403

- Lipton S, Evans JA, Bazilevs Y, Elguedj T, Hughes TJR (2010) Robustness of isogeometric structural discretizations under severe mesh distortion. Comput Methods Appl Mech Eng 199(5-8):357-373

- Litke N, Levin A, Schröder P (2001) Trimming for subdivision surfaces. Comput Aided Geom Des 18(5):463-481

- Liu W, Mann S (1997) An optimal algorithm for expanding the composition of polynomials. ACM Trans Graph 16(2):155-178

- Loop C (1987) Smooth subdivision surfaces based on triangles. Master's Thesis, University of Utah

- Luken WL (1996) Tessellation of trimmed NURBS surfaces. Comput Aided Geom Des 13(2):163-177

- Ma YL, Hewitt WT (2003) point inversion and projection for NURBS curve and surface: control polygon approach. Comput Aided Geom Des 20(2):79-99

- Maekawa T, Patrikalakis NM (1993) Computation of singularities and intersections of offsets of planar curves. Comput Aided Geom Des 10(5):407-429

- Mäntylä M (1988) An introduction to solid modeling. Computer Science Press, Rockville, Md

- Markot RP, Magedson RL (1989) Solutions of tangential surface and curve intersections. Comput Aided Des 21(7):421-427

- Martin RC (2009) Clean code: a handbook of Agile software craftsmanship, 1st edn. Pearson Education, Inc., Upper Saddle River

- Martin T, Cohen E, Kirby M (2008) Volumetric parameterization and trivariate B-spline fitting using harmonic functions. In: ACM symposium on solid and physical modeling, New York, NY, USA, p 269-280

- Martin W, Cohen E, Fish R, Shirley P (2000) Practical ray tracing of trimmed NURBS surfaces. J Graph Tools 5(1):27-52

- Marussig B (2016) Seamless integration of design and analysis through boundary integral equations. Monographic Series TU Graz: structural analysis. Verlag der Technischen Universität Graz

- Marussig B, Zechner J, Beer G, Fries T (2016) Integration of design and analysis through boundary integral equations. In: VII European congress on computational methods in applied sciences and engineering, ECCOMAS. https: eccomas2016. org proceedings pdf 5812.pdf

- Marussig B, Zechner J, Beer G, Fries TP (2015) Fast isogeometric boundary element method based on independent field approximation. Comput Methods Appl Mech Eng 284:458-488

- Marussig B, Zechner J, Beer G, Fries TP (2016) Stable isogeometric analysis of trimmed geometries. Comput Methods Appl Mech Eng. doi:10.1016 j.cma.2016.07.040 Massarwi F, Elber G (2016) A B-spline based framework for volumetric object modeling. Comput Aided Des 78:36-47 Milenkovic VJ (1988) Verifiable implementations of geometric algorithms using finite precision arithmetic. Artif Intell 37(1):377-401 Miller JR (1986) Sculptured surfaces in solid models: issues and alternative approaches. IEEE Comput Graph Appl 6(12):37-48 Moreton H (2001) Watertight tessellation using forward differencing. In: Proceedings of the workshop on graphics hardware. ACM, p 25-32 Mortenson ME (1997) Geometric modeling, 2nd edn. Wiley, New York Mudur SP, Koparkar PA (1984) Interval methods for processing geometric objects. IEEE Comput Graph Appl 4(2):7-17 Nagel RN, Braithwaite WW, Kennicott PR (1980) Initial graphics exchange specification (IGES) version 1.0. NBSIR 80-1978 (R). National Bureau of Standards Nagy AP, Abdalla MM, Gurdal Z (2010) On the variational formulation of stress constraints in isogeometric design. Comput Methods Appl Mech Eng 199(41-44):2687-2696 Nagy AP, Benson DJ (2015) On the numerical integration of trimmed isogeometric elements. Comput Methods Appl Mech Eng 284:165-185 Nguyen T, Karčiauskas K, Peters J (2014) A comparative study of several classical, discrete differential and isogeometric methods for solving Poisson's equation on the disk. Axioms 3(2):280-299 Nguyen VP, Kerfriden P, Brino M, Bordas SPA, Bonisoli E (2014) Nitsche's method for two and three dimensional NURBS patch coupling. Comput Mech 53(6):1163-1182 Nishita T, Sederberg TW, Kakimoto M (1990) Ray tracing trimmed rational surface patches. SIGGRAPH Comput Graph 24(4):337-345 Nitsche J (1971) Über ein Variationsprinzip zur Lösung von Dirichlet-Problemen bei Verwendung von Teilräumen, die keinen Randbedingungen unterworfen sind. Abh Math Semin Univ Hambg 36(1):9-15 Omerović S, Fries TP (2016) Conformal higher-order remeshing schemes for implicitly defined interface problems. Int J Numer Methods Eng. doi:10.1002 nme.5301 Pabst HF, Springer JP, Schollmeyer A, Lenhardt R, Lessig C, Froehlich B (2006) Ray casting of trimmed NURBS surfaces on the GPU. In: IEEE symposium on interactive ray tracing, p 151-160 Parreira P (1988) On the accuracy of continuous and discontinuous boundary elements. Eng Anal 5(4):205-211 Patrikalakis NM (1993) Surface-to-surface intersections. IEEE Comput Graph Appl 13(1):89-95 Patrikalakis NM, Maekawa T (2002) Chapter 25: intersection problems. In: Handbook of computer aided geometric design. Elsevier, Amsterdam, p 623-650 Patrikalakis NM, Maekawa T (2009) Shape interrogation for computer aided design and manufacturing. Springer, Berlin Patrikalakis NM, Prakash PV (1990) Surface intersections for geometric modeling. J Mech Des 112(1):100-107 Patterson C, Sheikh M (1984) Interelement continuity in the boundary element method. In: Brebbia C (ed) Topics in boundary element research. Springer, New York, pp 123-141 Peng QS (1984) An algorithm for finding the intersection lines between two B-spline surfaces. Comput Aided Des 16(4):191-196 Peterson AF, Bibby MM (2009) An introduction to the locallycorrected Nyström method. Synth Lect Comput Electromagn 4(1):1-115 Pharr M, Kolb C, Gershbein R, Hanrahan P (1997) Rendering complex scenes with memory-coherent ray tracing. In:

- Proceedings of the conference on computer graphics and interactive techniques. ACM, p 101-108

- Philipp B, Breitenberger M, D'Auria I, Wüchner R, Bletzinger KU (2016) Integrated design and analysis of structural membranes using the isogeometric B-Rep analysis. Comput Methods Appl Mech Eng 303:312-340

- Piegl LA (2005) Ten challenges in computer-aided design. Comput Aided Des 37(4):461-470

- Piegl LA, Richard AM (1995) Tessellating trimmed NURBS surfaces. Comput Aided Des 27(1):16-26

- Piegl LA, Tiller W (1997) The NURBS book, 2nd edn. Springer, New York

- Piegl LA, Tiller W (1998) Geometry-based triangulation of trimmed NURBS surfaces. Comput Aided Des 30(1):11-18

- Pratt MJ (2001) Introduction to ISO 10303-the STEP standard for product data exchange. Technical report. National Institute of Standards and Technology, Manufacturing Systems Integration Division, Gaithersburg

- Pratt MJ, Anderson BD, Ranger T (2005) Towards the standardized exchange of parameterized feature-based CAD models. Comput Aided Des 37(12):1251-1265

- Pratt MJ, Kim J (2006) Experience in the exchange of procedural shape models using ISO 10303 (STEP). In: Symposium on solid and physical modeling. ACM, p 229-238

- Purcell TJ, Buck I, Mark WR, Hanrahan P (2002) Ray tracing on programmable graphics hardware. ACM Trans Graph 21(3):703-712

- Ramshaw L (1987) Blossoming: a connect-the-dots approach to splines. Digital Equipment Corporation, Palo Alto

- Randrianarivony M (2006) Geometric processing of CAD data and meshes as input of integral equation solvers. PhD Thesis, Computer Science Faculty Technische Universität Chemnitz

- Randrianarivony M (2009) On global continuity of Coons mappings in patching CAD surfaces. Comput Aided Des 41(11):782-791

- Rank E, Ruess M, Kollmannsberger S, Schillinger D, Düster A (2012) Geometric modeling, isogeometric analysis and the finite cell method. Comput Methods Appl Mech Eng 249-252:104-115

- Renner G, Weiß V (2004) Exact and approximate computation of B-spline curves on surfaces. Comput Aided Des 36(4):351-362

- Requicha AA, Rossignac JR (1992) Solid modeling and beyond. IEEE Comput Graph Appl 12(5):31-44

- Requicha AAG (1980) representations for rigid solids: theory, methods, and systems. ACM Comput Surv 12(4):437-464

- Requicha AAG, Voelcker HB (1982) Solid modeling: a historical summary and contemporary assessment. IEEE Comput Graph Appl 2(2):9-24

- Requicha AAG, Voelcker HB (1983) Solid modeling: current status and research directions. IEEE Comput Graph Appl 3(7):25-37

- Requicha AAG, Voelcker HB (1985) Boolean operations in solid modeling: boundary evaluation and merging algorithms. Proc IEEE 73(1):30-44

- Riesenfeld RF (1975) On Chaikin's algorithm. Comput Graph Image Process 4(3):304-310

- Riesenfeld RF, Haimes R, Cohen E (2015) Initiating a CAD renaissance: multidisciplinary analysis driven design: framework for a new generation of advanced computational design, engineering and manufacturing environments. Comput Methods Appl Mech Eng 284:1054-1072

- Riffnaller-Schiefer A, Augsdörfer UH, Fellner DW (2016) Isogeometric shell analysis with NURBS compatible subdivision surfaces. Appl Math Comput 272, Part 1:139-147 Rockwood A, Heaton K, Davis T (1989) Real-time rendering of trimmed surfaces. In: ACM SIGGRAPH computer graphics, vol 23. ACM, p 107-116 Rossignac JR, Requicha AAG (1987) Piecewise-circular curves for geometric modeling. IBM J Res Dev 31(3):296-313 Rossignac JR, Requicha AAG (1999) Solid modeling. Technical report Rüberg T, Cirak F (2012) Subdivision-stabilised immersed B-spline finite elements for moving boundary flows. Comput Methods Appl Mech Eng 209-212:266-283 Ruess M, Schillinger D, Bazilevs Y, Varduhn V, Rank E (2013) Weakly enforced essential boundary conditions for NURBSembedded and trimmed NURBS geometries on the basis of the finite cell method. Int J Numer Methods Eng 95(10):811-846 Ruess M, Schillinger D, Özcan AI, Rank E (2014) Weak coupling for isogeometric analysis of non-matching and trimmed multi-patch geometries. Comput Methods Appl Mech Eng 269:46-71 Salesin D, Stolfi J, Guibas L (1989) Epsilon geometry: building robust algorithms from imprecise computations. In: Proceedings of the symposium on computational geometry. ACM, p 208-217 Sarraga RF (1983) Algebraic methods for intersections of quadric surfaces in GMSOLID. Comput Vis Graph Image Process 22(2):222-238 Sarraga RF, Waters WC (1984) Free-form surfaces in GMSOLID: goals and issues. In: Pickett MS, Boyse 'JW (eds) Solid modeling by computers. Springer, New York, pp 187-209 Schillinger D, Evans JA, Reali A, Scott MA, Hughes TJR (2013) Isogeometric collocation: cost comparison with Galerkin methods and extension to adaptive hierarchical NURBS discretizations. Comput Methods Appl Mech Eng 267:170-232 Schillinger D, Ruess M (2015) The finite cell method: a review in the context of higher-order structural analysis of CAD and image-based geometric models. Arch Comput Methods Eng 22(3):391-455 Schmidt R, Wüchner R, Bletzinger KU (2012) Isogeometric analysis of trimmed NURBS geometries. Comput Methods Appl Mech Eng 241-244:93-111 Schollmeyer A, Fröhlich B (2009) Direct trimming of NURBS surfaces on the GPU. ACM Trans Graph 28(3):47:1-47:9 Scott MA (2011) T-splines as a design-through-analysis technology. PhD Thesis, University of Texas computational Science, engineering, and Mathematics Scott MA, Simpson RN, Evans JA, Lipton S, Bordas SPA, Hughes TJR, Sederberg TW (2013) Isogeometric boundary element analysis using unstructured T-splines. Comput Methods Appl Mech Eng 254:197-221 SCRA (2006) STEP application handbook ISO 10303 version 3 Sederberg TW (1983) Implicit and parametric curves and surfaces for computer aided geometric design. PhD Thesis, Purdue University Sederberg TW, Anderson DC, Goldman RN (1984) Implicit representation of parametric curves and surfaces. Comput Vis Graph Image Process 28(1):72-84 Sederberg TW, Christiansen HN, Katz S (1989) Improved test for closed loops in surface intersections. Comput Aided Des 21(8):505-508 Sederberg TW, Li X, Lin HW, Ipson H, Finnigan GT (2008) Watertight trimmed NURBS. ACM Trans Graph 27(3):79:1-79:8 Sederberg TW, Nishita T (1990) curve intersection using Bézier clipping. Comput Aided Des 22(9):538-549 Sederberg TW, Zheng J, Bakenov A, Nasri A (2003) T-splines and T-NURCCs. ACM Trans Graph 22(3):477-484

- Segal M (1990) Using tolerances to guarantee valid polyhedral modeling results. SIGGRAPH Comput Graph 24(4):105-114

- Seo YD, Kim HJ, Youn SK (2010) Isogeometric topology optimization using trimmed spline surfaces. Comput Methods Appl Mech Eng 199(49-52):3270-3296

- Seo YD, Kim HJ, Youn SK (2010) Shape optimization and its extension to topological design based on isogeometric analysis. Int J Solids Struct 47(11-12):1618-1640

- Shah JJ, Mäntylä M (1995) Parametric and feature based CAD CAM. Wiley, New York

- Shantz M, Chang SL (1988) Rendering trimmed NURBS with adaptive forward differencing. SIGGRAPH Comput Graph 22(4):189-198

- Shapiro V (2002) Solid modeling. Handb Comput Aided Geom Des 20:473-518

- Shen J, Kosinka J, Sabin M, Dodgson N (2016) Converting a CAD model into a non-uniform subdivision surface. Comput Aided Geom Des. doi:10.1016 j.cagd.2016.07.003

- Shen J, Kosinka J, Sabin MA, Dodgson NA (2014) Conversion of trimmed NURBS surfaces to Catmull-Clark subdivision surfaces. Comput Aided Geom Des 31(7-8):486-498

- Sheng X, Hirsch BE (1992) Triangulation of trimmed surfaces in parametric space. Comput Aided Des 24(8):437-444

- Sherbrooke EC, Patrikalakis NM (1993) Computation of the solutions of nonlinear polynomial systems. Comput Aided Geom Des 10(5):379-405

- Shewchuk JR (2002) Delaunay refinement algorithms for triangular mesh generation. Comput Geom Theory Appl 22(1-3):21-74

- Siemens Product Lifecycle Management Software, Inc. (2008) Parasolid XT format reference. Siemens Product Lifecycle Management Software, Inc., Cambridge

- Sinha P, Klassen E, Wang KK (1985) Exploiting topological and geometric properties for selective subdivision. In: Proceedings of the first annual symposium on computational geometry. ACM, p 39-45

- Skytt V, Haenisch J (2013) Extension of ISO 10303 with isogeometric model capabilities. ISO TC 184 SC 4 WG 12. ISO

- Song XW, Sederberg TW, Zheng JM, Farouki RT, Hass J (2004) Linear perturbation methods for topologically consistent representations of free-form surface intersections. Comput Aided Geom Des 21(3):303-319

- Steidl JW (2013) Trimmed NURBS: implementation of an element type discrimination algorithm. Master Project, Institute for Structural analysis at Graz University of Technology

- Steidl JW, Fries TP (2016) Automatic conformal decomposition of elements cut by NURBS. In: Papadrakakis M, Papadopoulos V, Stefanou G, Plevris V (eds) ECCOMAS congress

- Stenberg R (1995) On some techniques for approximating boundary conditions in the finite element method. J Comput Appl Math 63(1):139-148

- Sticko S, Kreiss G (2016) A stabilized Nitsche cut element method for the wave equation. Comput Methods Appl Mech Eng 309:364-387

- Stroud I (2006) Boundary representation modelling techniques. Springer, London

- Sugihara K, Iri M (1989) A solid modelling system free from topological inconsistency. J Inf Process 12(4):380-393

- Sutherland IE, Sproull RF, Schumacker RA (1974) A characterization of ten hidden-surface algorithms. ACM Comput Surv 6(1):1-55

- Sweeney MAJ, Bartels RH (1986) Ray tracing free-form B-spline surfaces. IEEE Comput Graph Appl 6(2):41-49

- Tassey G, Brunnermeier SB, Martin SA (1999) Interoperability cost analysis of the U.S. automotive supply chain. Technical report. Research Triangle Institute Temizer I, Wriggers P, Hughes TJR (2011) Contact treatment in isogeometric analysis with NURBS. Comput Methods Appl Mech Eng 200(9-12):1100-1112 Toshniwal D, Speleers H, Hughes TJR (2017) Smooth cubic spline spaces on unstructured quadrilateral meshes with particular emphasis on extraordinary points: design and analysis considerations. Technical report. ICES Reports Toth DL (1985) On ray tracing parametric surfaces. SIGGRAPH Comput Graph 19(3):171-179 Urick B (2016) Reconstruction of tensor product spline surfaces to integrate surface-surface intersection geometry and topology while maintaining inter-surface continuity. PhD Thesis, The University of Texas at Austin da Veiga LB, Buffa A, Sangalli G, Vázquez R (2014) Mathematical analysis of variational isogeometric methods. Acta Numer 23:157-287 Vigo M, Brunet P (1995) Piecewise linear approximation of trimmed surfaces. In: Hagen H, Farin G, Noltemeierm H (eds) Geometric modelling: Dagstuhl 1993, computing supplement 10. Springer, New York, pp 341-356 Vries-Baayens AE, Seebregts CH (1992) Chapter 7: exact conversion of a trimmed nonrational Bézier surface into composite or basic nonrational Bézier surfaces. In: Topics in surface modeling. SIAM, Philadelphia, p 115-144 Wald I, Slusallek P, Benthin C, Wagner M (2001) Interactive rendering with coherent ray tracing. Comput Graph Forum 20(3):153-165 Wang SW, Shih ZC, Chang RC (2000) An improved rendering technique for ray tracing Bézier and B-spline surfaces. J Vis Comput Animat 11(4):209-219 Wang X (2001) Geometric trimming and curvature continuous surface blending for aircraft fuselage and wing shapes. Master's Thesis, Virginia Polytechnic Institute and State University Wang Y, Benson DJ (2016) Geometrically constrained isogeometric parameterized level-set based topology optimization via trimmed elements. Front Mech Eng 1-16 Wang Y, Benson DJ, Nagy AP (2015) A multi-patch nonsingular isogeometric boundary element method using trimmed elements. Comput Mech 56(1):173-191 Wang YW, Huang ZD, Zheng Y, Zhang SG (2013) Isogeometric analysis for compound B-spline surfaces. Comput Methods Appl Mech Eng 261-262:1-15 Warren J, Weimer H (2001) Subdivision methods for geometric design: a constructive approach, 1st edn. Morgan Kaufmann Publishers, Inc., San Francisco Wei X, Zhang Y, Hughes TJR, Scott MA (2015) Truncated hierarchical Catmull-Clark subdivision with local refinement. Comput Methods Appl Mech Eng 291:1-20 Weiler KJ (1986) Topological structures for geometric modeling. PhD Thesis, Rensselaer Polytechnic Institute Whitted T (1980) An improved illumination model for shaded display. Commun ACM 23(6):343-349 Wriggers P, Zavarise G (2004) Chapter 6: computational contact mechanics. In: Stein E, de Borst R, Hughes TJR (eds) Encyclopedia of computational mechanics. Fundamentals, vol 2. Wiley, p 195-226 Wu R, Peters J (2015) Correct resolution rendering of trimmed spline surfaces. Comput Aided Des 58:123-131 Xia S, Qian X (2016) Isogeometric analysis with Bézier tetrahedra. Comput Methods Appl Mech Eng. doi:10.1016 j. cma.2016.09.045 Xia S, Wang X, Qian X (2015) Continuity and convergence in rational triangular Bézier spline based isogeometric analysis. Comput Methods Appl Mech Eng 297:292-324 Yang CG (1987) On speeding up ray tracing of B-spline surfaces. Comput Aided Des 19(3):122-130

- Yang YJ, Cao S, Yong JH, Zhang H, Paul JC, Sun JG, Gu Hj (2008) Approximate computation of curves on B-spline surfaces. Comput Aided Des 40(2):223-234

- Yap CK (1997) Towards exact geometric computation. Comput Geom 7(1):3-23

- Zechner J, Marussig B, Beer G, Fries TP (2015) The isogeometric Nyström method. Comput Methods Appl Mech Eng 306:212-237

- Zhang X (2005) Optimal geometric trimming of B-spline surfaces for aircraft design. PhD Thesis, Virginia Polytechnic Institute and State University Zhang YJ (2016) Geometric modeling and mesh generation from scanned images. CRC Press Zienkiewicz OC, Taylor RL, Zhu JZ (2013) Chapter 17: the finite element method: its basis and fundamentals. In: Automatic mesh generation, 7th edn. Butterworth-Heinemann, Oxford, p 573-640
