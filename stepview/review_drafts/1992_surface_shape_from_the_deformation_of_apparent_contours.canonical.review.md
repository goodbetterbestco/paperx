# Surface Shape from the Deformation of Apparent Contours

ROBERTO CIPOLLA, ANDREW BLAKE

Department of Engineering, University of Cambridge, Cambridge CB2 IPZ, England
Department of Engineering Science, University of Oxford, Oxford OXI 3PJ, England
Department of Engineering, University of Cambridge, Cambridge CB2 1PZ, England

## Abstract

One immediate facility afforded by the analysis is that surface patches can be reconstructed in the vicinity of contour generators. Once surface curvature is known, it is possible to discriminate extremal contours from other fixed curves in space. Furthermore, the known robustness of parallax as a cue to depth extends to the case of surface curvature. Its derivative-rate of parallax-is shown theoretically to be a curvature cue that is robust to uncertainties in the known viewer motion. This robustness has been confirmed in experiments. The spatitemporal analysis of deforming silhouettes (apparent contours) is here extended using the mathematics of perspective projections and tools from differential geometry. Analysis of the image motion of a silhouette or apparent contour enables computation of local surface curvature along the corresponding contour generator on the surface, assuming viewer motion is known. To perform the analysis, a spatiotemporal parameterization of imagecurve motion is needed, but is underconstrained (a manifestation of the well-known aperture problem). It is shown that an epipolar parameterization is most naturally matched to the recovery of surface curvature. Finally, the power of the new analysis for robotics applications is demonstrated. Illustrations are given of an Adept robot, equipped with a CCD camera, circumnavigating curved obstacles. When further equipped with a suction gripper the robot manipulator can pick up an object by its curved surface, under visual guidance.

## Introduction

For a smooth arbitrarily curved surface-especially in man-made environments where surface texture may be sparse-the dominant image feature is the apparent contour or silhouette. The apparent contour is the projection of the locus of points on the object-the contour generator or extremal boundary-which separates the visible from the occluded parts of a smooth, opaque, curved surface. The apparent contour and its deformation under information for navigation, object manipulation, motion baum [41 pointed out that surface orientation along the apparent contour can be computed directly from image data. Koenderink [29] related the curvature of an appar-

(Gaussian curvature); the sign of Gaussian curvature is equal to the sign of the curvature of the image contour. Convexities, concavities, and inflections of an apparent contour indicate, respectively, convex, hyperbolic, and parabolic surface points. Giblin and Weiss [23] extended this by adding viewer motions to obtain quantitative estimates of surface curvature. A surface (excluding concavities in opaque objects) can be reconstructed from the envelope of all its tangent planes, which in turn are computed directly from the family of apparent contours silhouettes of the surface, obtained under motion of the viewer. By assuming that the viewer follows a great circle of viewer directions around the object, they restricted the problem of analyzing the envelope of tangent planes to the less general problen of computing the envelope of a family of lines in a plane. Their algorithm was tested on noise-free, synthetic data (on the assumption that apparent contours had been distinguished from other image contours) demonstrating the reconstruction of a planar curve under orthographic projection.

In the first part of this article this will be extended to the general case or arbitrary nonplanar, curvilinear viewer motion under perspective projection. The geom etry of apparent contours and their deformation under viewer-motion are related to the differential geometry of the observed object's surface. In particular it is shown how to recover the position, orientation and 3D shape of visible surfaces in the vicinity of their contour gen erators from the deformation of apparent contours and known viewer motion. The theory for small, local viewer motions is developed to detect extremal bound aries and distinguish them from occluding edges (dis continuities in depth or orientation), surface markings or shadow boundaries. \({ }^{1}\) A consequence of the theory concerns the robustness of relative measurements of surface curvature based on the relative image motion of nearby points in the image-parallax-based measurements. Intuitively it is relatively difficult to judge, moving around a smooth, featureless object, whether its silhouette is extremal or not-that is, whether curvature along the ray is bounded or not. This judgement is much easier to make for objects which have at least a few surface features. Under small viewer motions, features are "sucked" over the extremal boundary, at a rate that depends on surface curvature. Our theoretical findings exactly reflect the intuition that the "sucking" effect is a reliable indicator of relative curvature, regardless of the exact details of the viewer's motion. Relative measurements of curvature across two adjacent points are shown to be entirely immune to uncertainties in the viewer's rotational velocity. The dependency on the viewer's translational velocity is also greatly reduced. The second part of this article describes the implementation of these theories and results of experiments performed with a CCD camera mounted on the wrist joint of \(a_{5}\)-axis Adept 1 SCARA robot arm. A computationally efficient method for extracting and tracking image contours based on B-spline snakes is presented. Measurement of image velocities and accelerations at image contours is used to recover surface position and 3D shape of surfaces in the vicinity of their apparent contours. Error and sensitivity analysis substantiate the claims that parallax methods are orders of magnitude less sensitive to the details of the viewer's motion than single-point measurements. The techniques are also used to detect apparent contours and discriminate them from other fixed image features. We describe the realtime implementaions of these algorithms for use in tasks involving the active exploration of visible surface geometry. The visually derived shape information is successfully used in modeling, navigation, and the manipulation of piecewise smooth curved objects.

## 2 Theoretical Framework

In this section the theoretical framework for the subsequent analysis of apparent contours and their deformation under viewer motion is presented. We begin with the properties of apparent contours and their contour generators and then relate these first to the descriptions of local 3D shape developed from the differential geometry of surfaces, and then to the analysis of visual motion of apparent contours.

### 2.1 The Apparent Contour and Its Contour Generator

Consider a smooth object. For each vantage point, all the rays through the vantage point that are tangent to the surface can be constructed. They touch the object along a smooth curve on its surface which we call the contour generator [38] or alternatively the extremal boundary [3], the rim [29], the fold [6] or the critical set of the visual mapping [12, 23] (figure I). For generic situations (situations that do not change qualitatively under arbitrarily small excursions of the vantage point) the contour generator is part of a smooth space curve (not a planar curve) whose direction is not in general perpendicular to the ray direction. The contour generator is dependent on the local surface geometry and on the vantage point in a simple way which will be elucidated below. Moreover, each vantage point will, in general, generate a different contour generator. Movement of the viewer causes the contour generator to "slip" over the visible surface. The image of the contour generator-here called the apparent contour but elsewhere also known as the occluding contour, profile, outline, silhouette, or limbwill usually be smooth (figure 1). However, as a consequence of the contour generator being a space curve, there may exist a finite number of rays that are tangent not only to the surface but also to the contour generator. At these points, the apparent contour of a transparent object will cusp. For opaque surfaces, however, only one branch of the cusp is visible and the contour ends abruptly [34, 29].

$$
r (so, t) apparens contour Q (5,10) contour generator r(s,to)
$$

### 2.2 Surface Geometry

In the following, descriptions of local 3D shape are developed directly from the differential geometry of surfaces [18, 20, 31]. Consider a point P on the contour generator of a smooth, curved surface in R' and parameterized locally by a vector-valued function r(s, t). The parametric representation can be considered as covering the surface with two families of curves [35]: r(s, to) and r(so, t) where so or to are fixed for a given curve in the family. For the analysis of apparent contours and their deformation with viewer motion it is necessary to choose the one-parameter family of views to be indexed by a time arameter t, which will also parameterize viewer posi ion for a moving observer. The s and t parameters ar defined so that the s-parameter curve, r(s, to), is the contour generator from a particular view to (figure 1). A t-parameter curve r(so, t) can be thought of as the 3D locus of points grazed by a light ray from the viewer, under viewer motion. Such a locus is not uniquely lefined. Given a starting point s = so, t = to, the cor respondence, as the viewer moves, between "succes sive" (in an infinitesimal sense) contour generators is not unique. Hence there is considerable freedom to choose a spatiotemporal parameterization of the surface, r(s, t).

$$
\begin{align*} & \mathbf{r}_{s} \cdot \mathbf{n}=0 \tag{1}\\ & \mathbf{r}_{t} \cdot \mathbf{n}=0 \tag{2} \end{align*}
$$

The local surface geometry at \(P\) is determined by the tangent plane (surface normal) and a description of how the tangent plane turns as we move in arbitrary directions over the surface (figure 2). This can be spec ified in terms of the basis \(\left\{\mathbf{r}_{s}, \mathbf{r}_{t}\right\}\) for the tangent plane (where for convenience \(\mathbf{r}_{s}\) and \(\mathbf{r}_{t}\) denote \(\partial \mathbf{r} / \partial s\) and \(\partial \mathbf{r} / \partial t\), the tangents to the \(s\) - and \(t\)-parameter curves respectively), \({ }^{2}\) the surface normal (a unit vector, \(\mathbf{n}\) ) defined so that and the derivatives of these quantities with respect to movement over the surface. These are conveniently packaged in the first and second fundamental forms as follows. For a tangent-plane vector at \(P, \mathbf{w}\), the first fun damental form, \(I(\mathbf{w}, \mathbf{w})\), is used to express the length of any infinitesimal element in the tangent plane ([18], p. 92):

$$
\begin{equation*} I(\mathbf{w}, \mathbf{w})=\mathbf{w} \cdot \mathbf{w} \tag{3} \end{equation*}
$$

$$
\begin{equation*} \kappa^{n}=\frac{I I(\mathbf{w}, \mathbf{w})}{I(\mathbf{w}, \mathbf{w})} \tag{9} \end{equation*}
$$

![Figure II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-2-2-p020.png)

*Figure II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by: Fig. II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by views. Points are selected on image contours in the first view (to), indicated by crosses A and B for points on an extremal boundary and surface marking respectively. For epipolar parameterization of the surface, corresponding features lie on epipolar lines in the second and third view (t, and tz). Measurement of the three rays lying in an epipolar plane can be used to estimate surface curvatures (figure 12).*

It can be represented by a matrix of coefficients, \(\mathbf{G}\), with respect to the basis \(\left\{\mathbf{r}_{s}, \mathbf{r}_{t}\right\}\) where

$$
\mathbf{G}=\left[\begin{array}{ll} \mathbf{r}_{s} \cdot \mathbf{r}_{s} & \mathbf{r}_{s} \cdot \mathbf{r}_{t} \tag{4}\\ \mathbf{r}_{t} \cdot \mathbf{r}_{s} & \mathbf{r}_{t} \cdot \mathbf{r}_{t} \end{array}\right]
$$

The second fundamental form \(I I(\mathbf{w}, \mathbf{w})\), quantifies the "bending away" of the surface from the tangent plane. It is defined by ([18], p. 141):

$$
\begin{equation*} I I(\mathbf{w}, \mathbf{w})=-\mathbf{w} \cdot \mathbf{L}(\mathbf{w}) \tag{5} \end{equation*}
$$

where \(\mathbf{L}(\mathbf{w})\) is the derivative of the surface normal, \(\mathbf{n}\), in the direction \(\mathbf{w} . \mathbf{L}\) is in fact a linear transformation on the tangent plane. It is also called the shape operator [43] or the Weingarten map [42]. In particular for the basis vectors \(\left\{\mathbf{r}_{s}, \mathbf{r}_{t}\right\}\) :

$$
and the coefficients of the second fundamental are given by matrix \( \mathbf{D} \), where
$$

$$
\mathbf{D}=\left[\begin{array}{ll} \mathbf{r}_{s s} \cdot \mathbf{n} & \mathbf{r}_{s t} \cdot \mathbf{n} \tag{8}\\ \mathbf{r}_{t s} \cdot \mathbf{n} & \mathbf{r}_{t t} \cdot \mathbf{n} \end{array}\right]
$$

$$
\begin{equation*} \mathbf{Q} \cdot \mathbf{n}=0 \tag{11} \end{equation*}
$$

The geometry of the surface is completely deter mined locally up to a rigid motion in \(R^{3}\) by these two quadratic forms. It is, however, sometimes more con venient to characterize the surface by normal curvatures

The maximum and minimum normal curvatures are called the principal curvatures. The corresponding directions are called the principal directions. \({ }^{4}\) It will now be shown how to make these quadratic forms explicit from image measurable quantities. This requires relating the differential geometry of the surface to the analysis of visual motion.

### 2.3 Imaging Model

A monocular observer can determine the orientation of any ray projected onto its imaging surface. The observer cannot, however, determine the distance along the ray of the object feature that generated it. A general model for the imaging device is therefore to consider it as determining the direction of an incoming ray, which we can choose to represent as a unit vector. This is equivalent to considering the imaging device as a spherical pin-hole camera of unit radius (figure 1). The use of spherical projection (rather than planar), which has previously proven to be a powerful tool in structurefrom-motion [32, 39], makes it feasible to extend the theory of Giblin and Weiss [23] to allow for perspective. Its simplicity arises from the fact that there are no special points on the image surface, whereas the origin of the perspective plane is special and the consequent loss of symmetry tends to complicate mathematical arguments. For perspective projection the direction of a ray to a world point, \(P\), with position vector \(\mathbf{r}(s, t)\), is a unit vector on the image sphere \(\mathbf{Q}(s, t)\) defined at time \(t\) by

$$
\begin{align*} & \mathbf{L}\left(\mathbf{r}_{s}\right)=\mathbf{n}_{s} \tag{6}\\ & \mathbf{L}\left(\mathbf{r}_{t}\right)=\mathbf{n}_{t} \tag{7} \end{align*}
$$

$$
\begin{equation*} \mathbf{r}(s, t)=\mathbf{v}(t)+\lambda(s, t) \mathbf{Q}(s, t) \tag{10} \end{equation*}
$$

where \(\lambda(s, t)\) is the distance along the ray to the viewed point \(P\) and \(\mathbf{v}(t)\) is the viewer's position (figure 1). For a given vantage position \(t_{0}\), the apparent con tour determines a continuous family of rays \(\mathbf{Q}\left(s, t_{0}\right)\) emanating from the camera's optical center, which touch the surface so that where \(\mathbf{n}\) is the surface normal. Equation (11) defines both the contour generator and the apparent contour. The moving monocular observer at position \(\mathbf{v}(t)\) sees a family of apparent contours swept over the image sphere. These determine a two-parameter family of rays in \(R^{3}, \mathbf{Q}(s, t)\). As before with \(\mathbf{r}(s, t)\), the parameteri zation is underdetermined but that will be fixed later.

### 2.4 Viewer and Reference Coordinate Systems

$$
\begin{equation*} \mathbf{r}_{s}=\lambda_{s} \mathbf{Q}+\lambda \mathbf{Q}_{s} \tag{17} \end{equation*}
$$

Note that \(\mathbf{Q}\) is the direction of the light ray in the fixed reference/world frame for \(R^{3}\). It is determined by a spherical image position vector \(\tilde{\mathbf{Q}}\) (the direction of the ray in the camera/viewer coordinate system) and the orientation of the camera coordinate system relative to the reference frame. For a moving observer the viewer coordinate system is continuously moving with respect to the reference frame. The relationship between \(\mathbf{Q}\) and \(\tilde{\mathbf{Q}}\) can be conveniently expressed in terms of a rotation operation \(R(t)\) [27]:

The frames are defined so that instantaneously, at time * = O, they coincide,

$$
\begin{equation*} \mathbf{Q}(s, 0)=\tilde{\mathbf{Q}}(s, 0) \tag{13} \end{equation*}
$$

$$
\begin{equation*} \mathbf{n}=\frac{\mathbf{Q} \wedge \mathbf{Q}_{s}}{\left|\mathbf{Q} \wedge \mathbf{Q}_{s}\right|} \tag{19} \end{equation*}
$$

and have relative translational and rotational velocities of \(\mathbf{U}(t)\) and \(\boldsymbol{\Omega}(t)\) respectively:

The relationship between temporal derivatives of measurements made in the camera coordinate system and those made in the reference frame is then given instantaneously at time t = 0 by (differentiating (12)):

where (as before) the subscripts denote differentiation with respect to time and 1 denotes a vector product.

## 3 The Static Analysis of Apparent Contours

### 3.1 Geometric Properties of the Contour Generator and Its Projection

We now establish why the contour generator is a rich source of information about surface geometry. The ›hysical constraints of tangency (all rays at a contou generator are in the surface's tangent plane) and con jugacy (the special relationship between the direction of the contour generator and the ray direction) provide powerful constraints on the local geometry of the surface being viewed and allow the recovery of surface orientation and the sign of Gaussian curvature directly from a single image of the contour generator.

3.1.1 Tangency. Both the tangent to the contour generator, \(\mathbf{r}_{s}\), (obtained by differentiating (10)), and the ray, \(\mathbf{Q}\), must (by definition) lie in the tangent plane of the surface. From the tangency conditions

$$
\begin{aligned} & \mathbf{r}_{s} \cdot \mathbf{n}=0 \\ & \mathbf{Q} \cdot \mathbf{n}=0 \end{aligned}
$$

and (17), we see that the tangent to the apparent contour also lies in the tangent plane of the surface

$$
\begin{equation*} \mathbf{Q}=R(t) \tilde{\mathbf{Q}} \tag{12} \end{equation*}
$$

$$
\begin{equation*} \mathbf{Q}_{s} \cdot \mathbf{n}=0 \tag{18} \end{equation*}
$$

This allows the recovery of the surface orientation \(\mathbf{n}\) (defined up to a sign) directly from a single view \(\mathbf{Q}\left(s, t_{0}\right)\) using the direction of the ray and the tangent to the apparent (image) contour

This result is also valid for projection onto the plane. It is a trivial generalization to perspective projection of the well-known observation of Barrow and Tenenbaum [3, 4].

$$
\begin{gather*} \mathbf{U}=\mathbf{v}_{t} \tag{14}\\ \mathbf{\Omega} \wedge \tilde{\mathbf{Q}}=R_{t} \tilde{\mathbf{Q}} \tag{15} \end{gather*}
$$

3.1.2 Conjugate Direction Relationship of Ray and Contour Generator. The tangency conditions con strain the contour generator to the tangent plane of the surface. In which direction does the contour generator run? The direction is determined by the second funda mental form and the direction of the ray. In particular, the ray direction, \(\mathbf{Q}\), and the tangent to the contour gen erator, \(\mathbf{r}_{s}\), are in conjugate directions with respect to

$$
\begin{equation*} \mathbf{Q}_{t}=\tilde{\mathbf{Q}}_{t}+\mathbf{\Omega} \wedge \tilde{\mathbf{Q}} \tag{16} \end{equation*}
$$

$$
\begin{align*} I\left(\mathbf{Q}, \mathbf{r}_{s}\right) & =-\mathbf{Q} \cdot \mathbf{L}\left(\mathbf{r}_{s}\right) \\ & =-\mathbf{Q} \cdot \mathbf{n}_{s} \tag{20} \end{align*}
$$

which, by differentiating (11) and substituting (18), is zero:

$$
\begin{equation*} \mathbf{Q} \cdot \mathbf{n}_{s}=0 \tag{21} \end{equation*}
$$

The ray direction, \(\mathbf{Q}\), and the contour generator are not in general perpendicular but in conjugate directions. Let \(\theta\) be the angle between the ray direction \(\mathbf{Q}\) and the tangent \(\mathbf{r}_{s}\) to the extremal contour. In general \(-\pi / 2 \leq \theta \leq \pi / 2\). For example, for any point on a sphere, the contour generator will be perpendicular to the ray. However for any point on a cylinder, the conjugate direction of any ray is in the asymptotic direction, (i.e., parallel to the axis of a cylinder), and the contour gen erator will then run along this direction. The special

### 3.2 Static Properties of Apparent Contours

It is now well established that static views of extremal boundaries are rich sources of surface geometry [4, 29, 11, 23]. The main results are summarized below. Simple derivations can be found in [14].

3.2.1 Surface Normal. Computation of orientation on a textured surface patch would usually require (known) viewer motion to obtain depth, followed by spatial dif ferentiation. In the case of a contour generator however, the tangency condition (11), (18) means that surface orientation \(\mathbf{n}\left(s, t_{0}\right)\) can be recovered directly from a single view of an apparent contour \(\mathbf{Q}\left(s, t_{0}\right)\) from the ray ( \(\mathbf{Q}\) ) and image tangent directions ( \(\mathbf{Q}_{s}\) ):

The temporal and spatial differentiation that, for the textured patch, would have to be computed with attendant problems of numerical conditioning, is done, for extremal boundaries, by the physical constraint of tangency.

$$
\begin{equation*} K=\frac{\kappa^{p} \kappa^{t}}{\lambda} \tag{24} \end{equation*}
$$

Note that the sign of the orientation can only be determined if it is known on which side of the apparent contour the surface lies. This information may not be reliably available in a single view. It is shown below, however, that the "sidedness" of the contour generator can be unambiguously determined from the deformation of the apparent contour under known viewer motion. In the following, we choose the convention that the surface normal is defined to point away from the solid surface. This arbitrarily fixes the direction of increasing s-parameter of the apparent contours so that {les, n} form a right-handed orthogonal frame.

3.2.2 Sign of Normal Curvature Along the Contour Generator. The curvature of the apparent (image) contour has the same sign as the normal curvature along the contour generator. The curvature of the apparent contour, \(\kappa^{p}\), com puted as the geodesic curvature of the curve, \(\mathbf{Q}\left(s, t_{0}\right)\), on the image sphere: \({ }^{5,6}\)

$$
\begin{equation*} \kappa^{p}=\frac{\mathbf{Q}_{s s} \cdot \mathbf{n}}{\left|\mathbf{Q}_{s}\right|^{2}} \tag{22} \end{equation*}
$$

is simply related to the normal curvature of the contour generator, \(\kappa^{s}\), by [14]:

$$
\begin{equation*} \kappa^{p}=\frac{\lambda \kappa^{s}}{\sin ^{2} \theta} \tag{23} \end{equation*}
$$

Since surface depth \(\lambda\) must be positive, the sign of \(\kappa^{s}\) must, in fact, be the same as the sign of \(\kappa^{p}\). In the case of viewing a parabolic point, \(k^{s}=0\), and an inflection is generated in the apparent contour. A similar result was derived for orthographic projec tion by Brady et al. [11]. In the special case of a cusp, \(\theta=0\) and the apparent contour has infinite curvature while the contour generator has zero normal curvature. This can be considered in the limit.

3.2.3 Sign of Gaussian Curvature. For opaque sur faces the sign of the Gaussian curvature, \(K\), can be in ferred from a single view of an extremal boundary from the sign of the curvature of the apparent contour. This follows from a simple relationship between the Gaus sian curvature, \(K\); the curvature \(\kappa^{t}\) of the normal sec tion at \(P\) containing the ray direction; the curvature \(\kappa^{p}\) of the apparent contour (perspective projection) and the depth \(\lambda\) [29, 31] (derived in section 4.3.4):

$$
\mathbf{n}\left(s, t_{0}\right)=\frac{\mathbf{Q} \wedge \mathbf{Q}_{s}}{\left|\mathbf{Q} \wedge \mathbf{Q}_{s}\right|}
$$

## 4 The Dynamic Analysis of Apparent Contours

### 4.1 Spatiotemporal Parametrization

local surface shape. The viewer must however have discriminated apparent contours from the images of other surface curves (such as surface markings or discontinuities in surface orientation) and have determined on which side of the image contour the surface lies. When the viewer executes a known motion, then surface depth can, of course, be computed from image velocities [10, 26]. This is correct for static space curves but it will be shown that it also holds for extremal contour generators even though they are not fixed in space. Furthermore, if image accelerations are also computed, then full surface curvature (local 3D shape) can be computed along a contour generator. Giblin and Weiss demonstrated this for orthographic projection and planar motion [23]. We now generalize these results to arbitrary nonplanar, curvilinear viewer motion and on the surface \(\mathbf{r}(s, t)\). The choice is arbitrary since the image contours are projections of different 3D space curves.

![Figure 3. Epipola](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-3-p007.png)

*Figure 3. Epipola: parameterization. A moving observer at positioa v(l) sees a! Fig. 3. Epipolar parameterization. A moving observer at position vt) sees a family of contour generators r(s, f) indexed by the time parame Their spherical perspective projections are represented by a two-parameter family of apparent contours Q(s, +). For the epipolar parameterizati parameter curves (r(so, t) and Q(so, i)) are defined by choosing the correspondence between successive contours to be in an epipolar pla lat is determined by the translational velocity, U and the direction of the ray,*

### 4.2 Epipolar Parameterization

A natural choice of parameterization (for both the spatiotemporal image and the surface), is the epipolar parameterization defined by

$$
\begin{equation*} \mathbf{r}_{t} \wedge \mathbf{Q}=0 \tag{25} \end{equation*}
$$

$$
\begin{equation*} \mathbf{r}_{t}=\left(\frac{\mathbf{Q}_{t} \cdot \mathbf{n}}{\kappa^{t}}\right) \mathbf{Q} \tag{28} \end{equation*}
$$

The tangent to the \(t\)-parameter curve is chosen to be in the direction of the ray, \(\mathbf{Q}\). The physical interpreta tion is that the grazing/contact point is chosen to "slip" along the ray. The tangent-plane basis vectors, \(\mathbf{r}_{s}\) and \(\mathbf{r}_{t}\), are therefore in conjugate directions. The advantage of the parameterization is clear later, when it leads to a simplified treatment of surface curvature and a unified treatment of the projection of rigid space curves and apparent contours. A natural correspondence between points on successive snapshots of an apparent contour can now be set up. These are the lines of constant s on the image sphere. Differentiating (10) with respect to time and enforcing (25) leads to a "matching" condition

The corresponding ray in the next viewpoint (in an in finitesimal sense), \(\mathbf{Q}\left(s_{0}, t+\delta t\right)\), is chosen so that it lies in the plane defined by ( \(\mathbf{U} \wedge \mathbf{Q}\) )-the epipolar plane. This is also the osculating plane of the \(t\)-parameter curve on the surface, \(\mathbf{r}\left(s_{0}, t\right)\) (figure 3). This is the in finitesimal analogue to epipolar-plane matching in stereo [2,10]. For a general motion, however, the epi polar plane structure rotates continuously as the direc tion of translation, U, changes and the space curve, \(\mathbf{r}\left(s_{0}, t\right)\), generated by the movement of a contact point will be nonplanar. Substituting (16) into (26), the tangents to the t parameter curves on the spatiotemporal image, (so. t), are defined at t = 0 bs

Note that \(\tilde{\mathbf{Q}}_{t}\) is equal to the image velocity of a point on the projection of a static space curve at depth \(\lambda\) [39]. This is not surprising since instantaneously image velocities are dependent only on depth and not surface curvature. Points on successive apparent contours are

"matched" by searching along epipolar great circles on the image sphere (or epipolar lines for planar image geometry) defined by the viewer motion, \(\mathbf{U}, \boldsymbol{\Omega}\) and the image position \(\tilde{\mathbf{Q}}\). This induces a natural correspon dence between the contour generators from successive viewpoints on the surface. The contact point on a contour generator moves/slips along the line of sight \(\mathbf{Q}\) with a speed, \(\mathbf{r}_{t}\) determined by the distance and surface curvature.

where \(\kappa^{t}\) is the normal curvature of the space curve,

$$
\begin{equation*} \kappa^{t}=\frac{\mathbf{r}_{t t} \cdot \mathbf{n}}{\mathbf{r}_{t} \cdot \mathbf{r}_{t}} \tag{29} \end{equation*}
$$

Derivation 1. Substituting the matching constraint of (26) into the time derivative of (10) we obtain:

$$
\begin{equation*} \mathbf{r}_{t}=\left(\lambda_{t}+\mathbf{Q} \cdot \mathbf{U}\right) \mathbf{Q} \tag{30} \end{equation*}
$$

Differentiating (30) with respect to time and substituting this into (29) we obtain the relationship between surface curvature and viewer motion.

$$
\begin{equation*} \mathbf{Q}_{t}=\frac{(\mathbf{U} \wedge \mathbf{Q}) \wedge \mathbf{Q}}{\lambda} \tag{26} \end{equation*}
$$

$$
\begin{equation*} \boldsymbol{\kappa}^{t}=\frac{\mathbf{Q}_{t} \cdot \mathbf{n}}{\left(\lambda_{t}+\mathbf{Q} \cdot \mathbf{U}\right)} \tag{31} \end{equation*}
$$

Combining (31) and (30) gives the required result.

The numerator, \(\mathbf{Q}_{t} \cdot \mathbf{n}\), of (28) is analogous to stereo disparity (as appears below in the denominator of the depth formula (32)). It depends only on the dis tance of the contact point and the "stereo baseline." The denominator is the curvature (normal) of the space curve generated as the viewer moves in time. The speed of the contact point is therefore inversely proportional to the surface curvature. The contour generator "clings" to points with high curvature and speeds up as the curva ture is reduced. This property will be used later to dis tinguish surface markings or creases from the contour generators of curved surfaces (extremal boundaries).

### 4.3 Dynamic Properties of Apparent Contours

$$
\begin{equation*} \tilde{\mathbf{Q}}_{t}=\frac{(\mathbf{U} \wedge \tilde{\mathbf{Q}}) \wedge \tilde{\mathbf{Q}}}{\lambda}-\mathbf{\Omega} \wedge \tilde{\mathbf{Q}} \tag{27} \end{equation*}
$$

The choice of a suitable (although arbitrary) spatiotem poral parameterization permits us to make measure ments on the spatiotemporal image, \(\tilde{\mathbf{Q}}(s, t)\), and to recover an exact specification of the visible surface. This includes position, orientation and 3D shape as well as qualitative cues such as to which side of the image contour the occluding surface lies.

4.3.1 Recovery of Depth from Image Velocities. Depth \(\lambda\) (distance along the ray Q-see figure 1) can be com puted from the deformation ( \(\mathbf{Q}_{t}\) ) of the apparent con tour under known viewer motion (translational velocity U) [10]: From (26),

$$
\begin{equation*} \lambda=-\frac{\mathbf{U} \cdot \mathbf{n}}{\mathbf{Q}_{t} \cdot \mathbf{n}} \tag{32} \end{equation*}
$$

$$
\begin{equation*} \tan \theta=\frac{\lambda\left|\mathbf{Q}_{s}\right|}{\lambda_{s}} \tag{36} \end{equation*}
$$

This formula is an infinitesimal analogue of triangulatesimal limit, stereo will, in principle, correctly determine the depth of the contour generator. Equation (32) can also be reexpressed in terms of spherical image position \(\tilde{\mathbf{Q}}\) and the normal component

$$
\begin{equation*} \lambda=-\frac{\mathbf{U} \cdot \mathbf{n}}{\tilde{\mathbf{Q}}_{t} \cdot \mathbf{n}+(\mathbf{\Omega} \wedge \tilde{\mathbf{Q}}) \cdot \mathbf{n}} \tag{33} \end{equation*}
$$

$$
\begin{equation*} \kappa^{s}=\frac{\kappa^{p} \sin ^{2} \theta}{\lambda} \tag{37} \end{equation*}
$$

Clearly, absolute depth can only be recovered if rotational velocity & is known.

4.3.2 Surface Curvature from Deformation of the Ap parent Contour. Surface curvature (3D shape) is to be expressed in terms of the first and second fundamen tal forms, \(\mathbf{G}\) and \(\mathbf{D}\) ((4) and (8)), which in the epipolar parameterization and for unit basis vectors can be sim

$$
\begin{align*} \mathbf{G} & =\left[\begin{array}{cc} 1 & \cos \theta \\ \cos \theta & 1 \end{array}\right] \tag{34}\\ \mathbf{D} & =\left[\begin{array}{cc} \kappa^{s} & 0 \\ 0 & \kappa^{t} \end{array}\right] \tag{35} \end{align*}
$$

$$
\begin{equation*} \boldsymbol{\kappa}^{t}=-\frac{\mathbf{U} \cdot \mathbf{n}}{\lambda\left(\lambda_{t}+\tilde{\mathbf{Q}} \cdot \mathbf{U}\right)} \tag{38} \end{equation*}
$$

where \(\kappa^{t}\) is the normal curvature of the \(t\)-parameter curve \(\mathbf{r}\left(s_{0}, t\right)\) and \(\kappa^{s}\) is the normal curvature of the contour generator \(\mathbf{r}\left(s, t_{0}\right)\) at \(P\). Equivalently \(\kappa^{t}\) is the curvature of the normal section at \(P\) in the direction

$$
\begin{align*} \tilde{\mathbf{Q}}_{t t} \cdot \mathbf{n}= & -\frac{(\mathbf{U} \cdot \mathbf{n})^{2}}{(\lambda)^{3}}\left[\frac{1}{\kappa^{t}}\right]-2 \frac{(\tilde{\mathbf{Q}} \cdot \mathbf{U})(\mathbf{U} \cdot \mathbf{n})}{(\lambda)^{2}} \\ & -\frac{\mathbf{U}_{t} \cdot \mathbf{n}}{\lambda}-\left(\mathbf{Q}_{t} \wedge \tilde{\mathbf{Q}}\right) \cdot \mathbf{n} \\ & -\frac{2(\tilde{\mathbf{Q}} \cdot \mathbf{U})(\mathbf{\Omega} \wedge \tilde{\mathbf{Q}}) \cdot \mathbf{n}}{\lambda} \\ & +\frac{(\mathbf{\Omega} \wedge U) \cdot \mathbf{n}}{\lambda}+(\mathbf{\Omega} \cdot \tilde{\mathbf{Q}})(\mathbf{\Omega} \cdot \mathbf{n}) \tag{39} \end{align*}
$$

Note that \(\mathbf{D}\) is diagonal. This is a result of choosing, in the epipolar parameterization, basis directions, \(\left\{\mathbf{r}_{s}\right.\), \(\mathbf{r}_{t}\) \} that are conjugate. From (21) it is easy to show that the off-diagonal components are both equal to zero:

$$
\mathbf{r}_{t s} \cdot \mathbf{n}=-\mathbf{r}_{t} \cdot \mathbf{n}_{s}=-\left|\mathbf{r}_{t}\right| \mathbf{Q} \cdot \mathbf{n}_{s}=0
$$

How, in summary, can the components of \(\mathbf{G}\) and \(\mathbf{D}\) be computed from the deformation of apparent contours under viewer motion?

4.3.2.1 Angle Between Ray and Contour Generator, \(\theta\left(s, t_{0}\right)\). first \(\theta\left(s, t_{0}\right)\) can be recovered from the con tour generator \(\mathbf{r}\left(s, t_{0}\right)\) which is itself obtained from image velocities along the apparent contour via (33). This requires the numerical differentiation of depths along the contour generator. From (17) and simple trigonometry,

4.3.2.2 Normal Curvature Along the Contour Gener ator, \(\kappa^{s}\). Then normal curvature along the contour generator, \(\kappa^{s}\), is computed from the curvature \(\kappa^{p}\) of the apparent contour. Rearranging (23),

4.3.2.3 Normal Curvature Along the Line of Sight, \(\kappa^{t}\). Finally the normal curvature \(\kappa^{t}\), along the line of sight, can be recovered from image accelerations, as explained below: The normal curvature at \(P\) in the direction of the ray \(\mathbf{Q}, \kappa^{t}\) can be computed from the rate of deforma tion of the apparent contour under viewer motion. From (31) and (32), Since \(\kappa^{t}\) depends on \(\lambda_{t}\), it is clear from (33) that \(\kappa^{t}\) is a function of viewer acceleration ( \(\mathbf{U}_{t}\) and \(\mathbf{\Omega}_{t}\) ) and the second derivative of image position, \(\tilde{\mathbf{Q}}_{t_{t}}\), that is, image acceleration. By differentiating (33) and substituting (38) we find that the normal component of image accel eration at an apparent contour is determined by viewer motion (including translational and rotational accelera tions) in addition to a dependency on depth and surface curvature:

The details of equation (39) are not important. It merely demonstrates that the recovery of \(\kappa^{t}\) requires knowl edge of viewer motion (including translational and rota tional accelerations) together with measurement of image accelerations. In section 5 it will be shown how to cancel the undesirable dependency on viewer accel erations and rotations.

$$
K=\frac{\kappa^{p} \kappa^{t}}{\lambda}
$$

Note two important points:

- — As a result of the conjugacy relationship between the direction of the contour generator and the ray, surface curvature at a contour generator is completely determined by the normal curvatures in these two directions and the angle between them, 0. Compare this to a general surface point which requires the normal curvatures in three directions.

- Determining surface curvature usually requires the computation of second-order spatial derivatives of depth, 1. At extremal boundaries, however, only first-order spatial derivatives, As, and temporal derivatives, 4,, need be computed. One derivative is performed, effectively, by the physical system. This is also the case with specularities [8].

#### 4.3.3 Sidedness of Apparent Contour and Contour Generator.

In the static analysis of the apparent contour it was assumed that the "sidedness" of the contour generator-on which side of the image contour the obscuring surface lies—was known. Up to now in the dynamic analysis of apparent contours an arbitrary direction has been chosen for the s-parameter curve (and hence the image tangent Os) and the surface orientation, n, has been recovered up to an unknown sign from (19). The actual sign can now be determined from the deformation of the apparent contour. Equation (38) determines both a sign and magnitude for normal curvature along the ray, k'. This must, however, be convex and so its sign given by equation (38) allows us to infer the correct orientation of the tangent plane. This is an important qualitative geometric cue. The distinction between free space and solid surface is extremely useful in visual navigation and manipulation.

4.3.4 Gaussian and Mean Curvature. Although the first and second fundamental forms completely characterize the local 3D shape of the surface, it is sometimes more convenient to express the geometry of the surface by its principal curvatures and their geometric and arithmetic means: the Gaussian and mean curvature.

The Gaussian curvature, \(K\), at a point is given by the product of the two principal curvatures [18]. With the epipolar parameterization, Gaussian curvature can be expressed as a product of two curvatures: the normal curvature \(\kappa^{t}\) and the curvature of the apparent contour, \(\kappa^{p}\) scaled by inverse-depth. \({ }^{8}\)

This is the well-known result of Koenderink [29, 31] extended here to recover the magnitude as well as the sign of Gaussian curvature. The mean curvature, \(H\), and the principal curvatures \(\kappa_{1}, \kappa_{2}\) can similarly be ex pressed by

$$
\begin{align*} H & =\frac{1}{2}\left[\frac{\kappa^{p}}{\lambda}+\kappa^{t} \operatorname{cosec}^{2} \theta\right] \tag{40}\\ \kappa_{1,2} & =H \pm \sqrt{H^{2}-K} \tag{41} \end{align*}
$$

### 4.4 Degenerate Cases of the Epipolar Parameterization

In the previous section we introduced the epipolar parameterization and showed how to recover the 3D local shape of surfaces from the deformation of apparent contours.

There are two possible cases where degeneracy of the parameterization arises. These occur when \(\left\{\mathbf{r}_{s}, \mathbf{r}_{t}\right\}\) fails to form a basis for the tangent plane.

The contour generator does not slip over the surface with viewer motion but is fixed. It is therefore not an extremal boundary but a 3D rigid space curve (surface marking or discontinuity in depth or orientation).: An important advantage of the epipolar parameterization is its unified treatment of the image motion of curves. The projections of surface markings and creases can be simply treated as the limiting cases of apparent con tours of surfaces with infinite curvature, \(\kappa^{t}\) (from (28)). In fact the magnitude of the cur vature, \(\kappa^{t}\), can be used to discriminate these image curves from apparent contours. The parameterization degrades gracefully and hence this condition does not pose any spe cial problems. Although the space curve \(\mathbf{r}\left(s, t_{0}\right)\) can still be recovered from image velocities via (33) the surface orientation is no longer completely defined. The tangency conditions ((11) and (18) are no longer valid and the surface normal is only constrained by (17) to be perpendicular to the tangent to the space curve, leaving one degree of freedom unknown. Case 2. \(\mathbf{r}_{s} \wedge \mathbf{r}_{t}=0\) and \(\mathbf{r}_{t} \neq 0\) Not surprisingly, the parameterization degen erates at the singularity of the surface-to image mapping where \(\mathbf{r}_{s}\) and \(\mathbf{r}_{t}\) are parallel on the surface. A cusp \(\left(\left|\mathbf{Q}_{s}\right|=0\right)\) is gener ated in the projection of the contour gener ator. For generic cases the image contour appears to come to a halt at isolated points. Although the epipolar parameterization and equations (19) and (32) can no longer be used to recover depth and surface orientation at the isolated cusp point, this in general poses no problems. By tracking the contourending it is still possible in principle to recover the distance to the surface at a cusp point and the surface orientation [22].

## 5 Motion Parallax and the Robust Estimation of Surface Curvature

It has been shown that although it is feasible to compute surface curvature from the observed deformation of an apparent contour, this requires knowledge of the viewer's translational and rotational velocities and accelerations. Moreover the computation of surface curvature from the deformation of apparent contours is highly sensitive to errors in assumed ego-motion. This may be acceptable for a moving camera mounted on a precision robot arm or when a grid is in view so that accurate visual calibration of the camera position and orientation can be performed [47]. In such cases it is feasible to determine motion to the required accuracy of around 1 part in 1000 (see later). However, when only crude estimates of motion are available another strategy is called for. In such a case, it is sometimes possible to use the crude estimate to bootstrap a more precise visual ego-motion computation [24]. However this requires an adequate number of identifiable corner features, which may not be available in an unstructured environment. Moreover, if the estimate is too crude the go-motion computation may fail; it is notoriously ill onditioned 1481. The alternative approach is to seek geometric cues that are much less sensitive to error in the motion estimate. In this section, it is shown that estimates of surface curvature based on the relative image motion of nearby points in the image-parallax-based measurements—have just this property. Such estimates are stable to perturbations of assumed ego-motion. Intuitively it is relatively difficult to judge, moving around a smooth, featureless object, whether its silhouette is extremal or not-whether curvature along the contour is bounded or not. This judgement is much easier to make for objects which have at least a few surface features. Under small viewer motions, features are "sucked" over the extremal boundary, at a rate which depends on surface curvature.

The theoretical findings of this section exactly reflect the intuition that the "sucking" effect is a reliable indipoints are entirely immune to uncertainties in the viewer's rotational velocity. This is somewhat related to earlier results showing that relative measurements of this kind are important for depth measurement from image velocities [32, 36, 30, 14], or stereoscopic disparities [52] and for curvature measurements from stereoscopically viewed highlights [8]. Furthermore, it will be shown that, unlike the interpretation of single-point measurements, differences of measurements at two points are insensitive to errors in rotation and in translational acceleration. Only dependence on translational velocity remains. Typically, the two feaures might be one point on an extremal boundary and one fixed surface point. The surface point has infinite curvature and therefore acts simply as a stable reference point for the measurement of curvature at the extremal boundary. The reason for the insensitivity of relative curvature measurements is that global additive errors in motion measurement are canceled out.

### 5.1 Motion Parallax

Consider two visual features whose projections on the image sphere (figure 4) are \(\tilde{\mathbf{Q}}\left(s_{i}, t\right), i=1,2\) (which

$$
\begin{equation*} \tilde{\mathbf{Q}}_{t}^{(i)}=\left[\left(\mathbf{U} \wedge \tilde{\mathbf{Q}}^{(i)}\right) \wedge \tilde{\mathbf{Q}}^{(i)}\right] \quad \frac{1}{\lambda^{(i)}} \quad-\mathbf{\Omega} \wedge \tilde{\mathbf{Q}}^{(i)} \tag{42} \end{equation*}
$$

point image velocities consist of two components. The first is due to viewer translation and it is this component

![Figure 4. Motion parallax. Coenider che relative displacement bereeen a poine on an appartet coetour and the imago of a nearty surface frataro](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-4-p012.png)

*Figure 4. Motion parallax. Coenider che relative displacement bereeen a poine on an appartet coetour and the imago of a nearty surface frataro: Motion parallax. Coenider che relative displacement bereeen a poine on an appartet coetour and the imago of a nearty surface frataro 8 = Q(2) - Q". The rate of change of relative image position—-parallax, 8, has been shown to be a robust indicator of relative depth. In this section we show that its temporal derivative-the rate of parallax 6nis a robust geometric cue for the recovery of surface curvature at extremal boundaries.*

$$
\begin{equation*} \delta_{t}=[(\mathbf{U} \wedge \tilde{\mathbf{Q}}) \wedge \tilde{\mathbf{Q}}]\left[\frac{1}{\lambda^{(2)}}-\frac{1}{\lambda^{(1)}}\right] \tag{44} \end{equation*}
$$

that encodes scene structure (depth). The other com ponent is due to the rotational part of the viewer's motion and is independent of scene strucure. Clearly depth can only be recovered accurately if rotational velocity \(\Omega\) is known. The dependence on rotational velocity is removed if, instead of using raw image motion \(\tilde{\mathbf{Q}}_{t}\), the difference of the image motions of a pair of points, \(\tilde{\mathbf{Q}}^{(1)}, \tilde{\mathbf{Q}}^{(2)}\), is used. This is called paral lax [25]. (See figure 4.) The relative image position & of the two points is

Parallax is the temporal derivative of \(\boldsymbol{\delta}, \boldsymbol{\delta}_{t}\). If instan taneously the two points project to the same point on the image sphere, so that

$$
\tilde{\mathbf{Q}}^{(1)}(0)=\tilde{\mathbf{Q}}^{(2)}(0)=\tilde{\mathbf{Q}}
$$

then, from (42), the parallax \(\delta_{t}\) depends only on their relative inverse-depths and on viewer translational velocity. It is independent of (and hence insensitive to errors in) angular rotation \(\boldsymbol{\Omega}\) :

The use of "motion parallax" for robust determination of the direction of translation \(\mathbf{U}\) and relative depths from image velocities was described by Longuet-Higgins and Prazdny [36] and Rieger and Lawton [45].

### 5.2 Rate of Parallax

$$
\begin{equation*} \delta(t)=\tilde{\mathbf{Q}}^{(2)}-\tilde{\mathbf{Q}}^{(1)} \tag{43} \end{equation*}
$$

Following from the well-known results about motion parallax, we derive the central result of this section that the rate of parallax is a robust cue for surface cur vature. The direct formula (39) for normal curvature \(\kappa^{t}\) in terms of image acceleration was sensitive to viewer translational acceleration and rotational velocity and acceleration. If, instead, differences of image accel erations are used, the undesirable sensitivity vanishes. The relationship between image acceleration and nor mal curvature for points \(\tilde{\mathbf{Q}}^{(1)}, \tilde{\mathbf{Q}}^{(2)}\) can be expressed as:

\begin{align*} \tilde{\mathbf{Q}}_{t t}^{(i)} \cdot \mathbf{n}^{(i)}= & -\frac{\left(\mathbf{U} \cdot \mathbf{n}^{(i)}\right)^{2}}{\left(\lambda^{(i)}\right)^{3}}\left[\frac{1}{\kappa^{i t}}\right] \\ & -2 \frac{\left(\mathbf{U} \cdot \tilde{\mathbf{Q}}^{(i)}\right)\left(\mathbf{U} \cdot \mathbf{n}^{(i)}\right)}{\left(\lambda^{(i)}\right)^{2}} \\ & -\frac{\mathbf{U}_{t} \cdot \mathbf{n}^{(i)}}{\lambda^{(i)}}-\left(\boldsymbol{\Omega}_{t} \wedge \tilde{\mathbf{Q}}^{(i)}\right) \cdot \mathbf{n}^{(i)} \\ & -\frac{2\left(\mathbf{U} \cdot \tilde{\mathbf{Q}}^{(i)}\left(\boldsymbol{\Omega} \wedge \tilde{\mathbf{Q}}^{(i)}\right) \cdot \mathbf{n}^{(i)}\right.}{\lambda^{(i)}} \\ & +\frac{(\boldsymbol{\Omega} \wedge \mathbf{U}) \cdot \mathbf{n}^{(i)}}{\lambda^{(i)}} \\ & +\left(\boldsymbol{\Omega} \cdot \tilde{\mathbf{Q}}^{(i)}\right)\left(\boldsymbol{\Omega} \cdot \mathbf{n}^{(i)}\right) \tag{45} \end{align*} where \(\mathbf{n}^{(i)}\) is now taken to be a vector perpendicular to \(\tilde{\mathbf{Q}}^{(i)}\) and will only be a surface normal if the point belongs to an apparent contour. The important point is that the two copies of this equation for the two posi tions \(i=1,2\) can be subtracted, canceling the unde sirable dependency on \(\mathbf{\Omega}, \mathbf{\Omega}_{t}\) and on \(\mathbf{U}_{t}\) if the images of the two points are instantaneously coincident. Think of the two points as being the projection of extremal contour generators, which trace out curves with (normal) curvatures \(\kappa^{t_{1}}\) and \(\kappa^{t_{2}}\) as the viewer moves. Let us define the relative inverse curvature, \(\Delta R\), of the feature pair by

Note that it is simply the difference of the radii of curvature of the normal sections. Consider the two features to be instantaneously spa tially coincident, that is, initially, \(\tilde{\mathbf{Q}}\left(s_{1}, 0\right)=\tilde{\mathbf{Q}}\left(s_{2}, 0\right)\). Moreover assume they lie at a common depth \(\lambda\), and hence, instantaneously, \(\tilde{\mathbf{Q}}_{t}^{(1)}=\tilde{\mathbf{Q}}_{t}^{(2)}\). In practice, of course, the feature pair will only coincide exactly if one of the points is a surface marking which is instantane ously on the extremal boundary (figure 4). The effect of a small separation is analyzed below. Now, taking the

$$
\begin{equation*} \Delta R=\Delta \hat{R}+R^{\mathrm{error}} \tag{48} \end{equation*}
$$

where n is a vector perpendicular to the direction of he ray (Q · n = O), for example, the surface norma of one of the two points. The two points will not neces sarily have the same surface normal. From this equation we can obtain relative inverse curvature, AR, as a function of depth 1, viewer velocity U, and the second temporal derivative of 8. Dependence on viewer motion is now limited to the velocity U. There is no dependence on viewer acceleration or rotational velocity. Hence the relative measurement should be much more robust. (Computationally higher derivatives are generally far more sensitive to noise.)

Note that the use of the epipolar parameterization is not important in the above analysis. It can be shown that the normal component of the relative image accel eration \(\boldsymbol{\delta}_{t_{t}} \cdot \mathbf{n}\) between a distinct feature and an appar ent contour is independent of viewer motion and can be determined completely from spatiotemporal meas urements on the image (appendix A).

In the case that \(\tilde{\mathbf{Q}}^{(1)}\) is known to be a fixed surface reference point, with \(1 / \kappa^{t_{1}}=0\), then \(\Delta R=1 / \kappa^{t_{2}}\) so that the relative inverse curvature \(\Delta R\) constitutes an esti mate, now much more robust, of the normal curvature \(\kappa^{t_{2}}\) at the extremal boundary point \(\tilde{\mathbf{Q}}^{(2)}\). Of course this can now be used in equations (24), (34), and (35) to obtain robust estimates of surface curvature. This is confirmed by the experiments in the next section.

### 5.3 Degradation of Sensitivity with Separation of Points

$$
\begin{equation*} \Delta R=\frac{1}{\kappa^{t 2}}-\frac{1}{\kappa^{t 1}} \tag{46} \end{equation*}
$$

The theory above relating relative curvature to the rate of parallax assumed that the two points \(\tilde{\mathbf{Q}}^{(1)}\) and \(\tilde{\mathbf{Q}}^{(2)}\) were instantaneously coincident in the image and at the same depth, \(\lambda^{(1)}=\lambda^{(2)}\). In practice, point pairs used as features will not coincide exactly and an error limit on curvature (or, more conveniently, its inverse) must be computed to allow for this. The relative curvature can still be computed from the rate of parallax by taking into account an error, where AŘ is the estimate of the relative inverse curvature computed from the rate of parallax.

$$
\begin{equation*} \delta_{t t} \cdot \mathbf{n}=-\frac{(\mathbf{U} \cdot \mathbf{n})^{2}}{\lambda^{3}} \Delta R \tag{47} \end{equation*}
$$

$$
\begin{equation*} \Delta \hat{R}=-\frac{\lambda^{3}}{(\mathbf{U} \cdot \mathbf{n})^{2}} \delta_{t t} \cdot \mathbf{n} \tag{49} \end{equation*}
$$

The error in the radii of curvature, \(R^{\text {error }}\), consists of errors due to the difference in depths of the two fea tures, \(\delta \lambda\); the finite separation in the image, \(\delta=\Delta \tilde{\mathbf{Q}}\) and the differences in tangent planes of the two features, \(\Delta \mathbf{n}\). The magnitude of these effects can be easily com puted from the difference of equation (45) for the two points (appendix B). For nearby points that are on the same surface and for fixation \((\mathbf{U}=\lambda \boldsymbol{\Omega} \wedge \tilde{\mathbf{Q}})\) the domi nant error can be conveniently expressed as:

Parallax-based measurements of curvature will usually be accurate and insensitive to errors in viewer motion if the separation between points on nearby contours satisfies

$$
\begin{equation*} |\delta| \ll \frac{\Delta R}{9 \lambda} \tag{51} \end{equation*}
$$

Equation (50) can also be used to predict the residual sensitivity to translational and rotational accelerations. The important point to notice is that sensitivity to viewer motion is still reduced. As an example consider the sensitivity of absolute measurements of surface cur vature along the ray to error in viewer position. Think of this as adding an unknown translational acceleration, \(\mathbf{U}_{t}\). For absolute measurements (45) the effect of this unknown error is amplified by a factor of \(\lambda^{2} /(\mathbf{U} \cdot \mathbf{n})^{2}\) when estimating surface curvature. From appendix B and (50) we see that for parallax-based measurements the sensitivity is reduced to a factor of \(2 \Delta \lambda / \lambda\) of the original sensitivity. This sensitivity vanishes, of course, when the features are at the same depth. A similar ef fect is observed for rotational velocities and accelerations.

### 5.4 Qualitative Shape

Further robustness can be obtained by considering the ratio of relative curvatures. More precisely this is the ratio of differences in radii of curvature. Ratios of pairs of parallax-based measurements can, in theory, be completely insensitive to viewer motion. This is because

In particular, if we consider the ratio of relative cur vature measurements for two different point-pairs at similar depths, terms depending on absolute depth \(\lambda\) and velocity \(\mathbf{U}\) are canceled out in equation (47). This result corresponds to the following intuitive idea. The rate at which surface features rush toward or away from an extremal boundary is inversely proportional to the (normal) curvature there. The constant of proportional ity is some function of viewer motion and depth; it can be eliminated by considering only ratios of curvatures.

## 6 Implementation of Theory

In the previous sections a computational theory for the recovery of 3D shape from the deformation of apparent contours was presented. The implementation of this theory and the results of experiments performed with a camera mounted on a moving robot arm are now described. In particular this requires the accurate extraction of image curves from real images and tracking their temporal evolution to measure image velocities and accelerations. Uncertainty and sensitivity analysis is used to compute bounds on the estimates of surface curvature. This is critical in discriminating fixed features from extremal boundaries-deciding whether curvature along the ray is bounded or not—since with noisy measurements and poorly calibrated viewer motions, we must test by error analysis the hypothesis that the curvature is unbounded at a fixed feature. Sensitivity analysis is also used to substantiate the claim that parallax methods—using the relative image motion of nearby contours-allow the robust recovery of surface curvature.

### 6.1 Tracking Image Contours with B-Spline Snakes

Image contours can be localized and tracked using a variant of the well-known "snake" of Kass, Witkin, and Terzopoulos [28]. The snake is a computational construct, a dynamic curve able to track moving, deforming image features. Since many snakes can be active at once, each tracking its feature contour as a background process, they constitute a versatile mechanism for direction and focus of attention. 6.1.1 Active Contours-Snakes. Energy-minimizing active-countour models (snakes) were proposed by Kass et al. [28] as a top-down mechanism for locating features of interest in images and tracking their image motion, provided the feature does not move too fast.

The behavior of a snake is controlled by internal and external "forces." \({ }^{9}\) The internal forces enforce smooth ness and the external forces guide the active contour toward the image feature. In their implementation for image curve localization and tracking, these forces are derived by differentiating internal and external energies respectively.

- Internal energy

The internal energy (per unit length), \(E_{\text {internal }}\), at a point on the snake, \(\mathbf{x}(s)\) :

is composed of first and second-order terms, forcing the active contour to act like a string/membrane (avoiding gaps) or a thin rod/plate (avoiding high curvatures) respectively. These effects are controlled by the relative values of \(\alpha\) and \(\beta\). The internal energy serves to maintain smoothness of the curve under changing external influences.

$$
\begin{equation*} \mathbf{x}(s)=\sum_{i} f_{i}(s) \mathbf{q}_{i} \tag{54} \end{equation*}
$$

- External energy

$$
\begin{equation*} \mathbf{F}\left(s_{j}\right)=\nabla\left|\nabla G(\sigma) * I\left(\mathbf{x}\left(s_{j}\right)\right)\right| \tag{55} \end{equation*}
$$

The external force is computed from the image in tensity data \(I(\mathbf{x}(s))\), where the position of the snake is represented by \(\mathbf{x}(s)\), by differentiating an external energy (per unit length) \(E_{\text {external }}\) :

which is computed after convolution of the image with the derivative of a Gaussian kernel, \(\nabla G(\sigma)\), of size (scale) \(\sigma\). Gaussian smoothing extends the search range of the snake by smearing out image edge features. The goal is to find the snake (contour that minimizes the total energy. This is achieved by the numerical solution of the elastic problem using techniques from variational calculus. The main step is the solution of a linear equation involving a banded matrix, typically in several hundred variables [28].

#### 6.1.2 The B-Spline Snake.

A more economical realization can be obtained by using far fewer state variables [46]. In [15] we proposed the use of cubic B-splines [20]. These are deformable curves represented by four or more state variables (control points). The curves may be open or closed as required. The flexibility of the curve increases as more control points are added; each additional control point allows either one more inflection in the curve or, when multiple knots are used [5], reduced continuity at one point.

B-spline snakes are ideally suited for representing, detecting, and tracking image curves. Their main ad vantages include:

- Local control-modifying the position of a data point or control point causes only a small part of the curve to change.

- Compact representation-the number of variables to be estimated is reduced to the number of control points [40].

$$
\begin{equation*} E_{\text {internal }}=\frac{\alpha\left|\mathbf{x}_{s}\right|^{2}+\beta\left|\mathbf{x}_{s s}\right|^{2}}{2} \tag{52} \end{equation*}
$$

- — Continuity control—B-splines are defined with continuity properties at each point.

The B-spline is a curve in the image plane (figure 5) where \(f_{i}\) are the spline basis functions and \(\mathbf{q}_{i}\) are the coefficients or control points. These are positioned so that the curve locates the desired image contour. In the original implementation the "external force" on a point \(\mathbf{x}\left(s_{j}\right)\) was chosen to be so that, at equilibrium (when image forces vanish), the B-spline, \(\mathbf{x}(s)\), stabilized close to a high-contrast

$$
\begin{equation*} E_{\text {external }}=-|\nabla G(\sigma) * I(\mathbf{x}(s))|^{2} \tag{53} \end{equation*}
$$

In this section two major simplifications are introduced. The first concerns the control of spatial scale

$$
\begin{equation*} \sum_{j}\left[\mathbf{y}\left(s_{j}\right)-\sum_{i} f_{i}\left(s_{j}\right) \mathbf{q}_{i}\right]^{2} \tag{56} \end{equation*}
$$

for tracking. The other simplification is that there is no need for internal forces since the B-spline representation maintains smoothness via hard constraints implicit in the representation.

6.1.2.1 Exernal Forces and Control of Scale. The "force" is chosen to depend on the distance between the feature of interest (an edge) and the approximation by the B-spline. For each sample point the "force" on the snake is found by a coarse-to-fine strategy. This is done by inspecting intensity gradients on either side of the snake (either along the normal or along a direction determined by hard constraints, for example, scanlines). Control of scale is achieved by inspecting gradients nearer to or further from the snake itself. Each point chooses to move in the direction of the largest intensity gradient (hence toward a contrast edge). If the intensity gradients either side of the contour have opposite signs the scale is halved. This is repeated until the edge has been localized to the nearest pixel.

$$
\begin{equation*} \sum_{i} \mathbf{q}_{i} \sum_{j} f_{i} f_{k}=\sum_{j} f_{k} \mathbf{y}\left(s_{j}\right) \tag{57} \end{equation*}
$$

The gradient is estimated by finite differences. Gaus sian smoothing is not used. \({ }^{10}\) Image noise is not, as might be thought, a major problem in the unblurred image since CCD cameras have relatively low signalto-noise. Moreover, gradients are sampled at several places along the spline, and those samples combined to compute motions for the spline control points (described below, (57)). The combination of those samples itself has an adequate averaging, noise-defeating effect.

6.1.2.2 Positioning the Control Points. External forces are sampled at N points,

$$
\mathbf{x}\left(s_{j}\right), \quad j=1, \ldots, N
$$

along the curve-typically N > 20 has been adequate in our experiments. External forces are applied to the curve itself; but, for iterative adjustment of displacement, it is necessary to compute the force transmitted to each control point. This can be done by positioning the B-spline so that it minimizes the sum of the square of the distances between the discrete data points of the feature and the approximation by the B-spline. Effectively, each snake point is attached to a feature by an elastic membrane so that its potential energy is proportional to the distance squared. This technique has been used to represent image curves [41].

Derivation 2. If the desired feature position is given by \(\mathbf{y}\left(s_{j}\right)\) for a point on the B-spline, \(\mathbf{x}\left(s_{j}\right)\), we wish to minimize the potential energy:

The new positions of the control points, \(\mathbf{q}_{i}\), are chosen by solving (the least-squares solution):

where \(k\) has the same range of values as the control points, \(i\).

on" and the scale is reduced to enable accurate contour localization. Since accurate measurements are required o compute image accelerations, care has been taker over subpixel resolution. At earlier stages of tracking when coarse blurring (large scale) is used, the capture the snake may lag behind the contour. Once the snake has converged onto the contour, standard edge-detection techniques such as smoothing for subpixel resolution [13] are used to obtain accurate localization.

The snakes were either initialized by hand in the first frame near image contours of interest, which they then track automatically or wait in the image until they are swept by the motion of the camera over a feature for which they have an affinity have also been successful (figure 6). Tracking is maintained provided the contour does not move too quickly. The contour tracker can run at 15 Hz on a SUN4 260 [7]. By using a parallel MIMD architecture (based on 9 Transputers) and interframe constraints (simulating inertia and damping) to enhance tracking capability, the real-time tracking of 10 snakes has been achieved [17). The adaptive choice of the number of control points; the control of the length of the contour, and the scale of the feature search are current topics of research.

### 6.2 The Epipolar Parameterization

In the epipolar parameterization of the spatiotemporal image and surface, a point on an apparent contour in the first image is "matched" to a point in successive images (in an infinitesimal sense) by searching along the corresponding epipolar lines. This allows us to ex tract a \(t\)-parameter curve from the spatiotemporal image. As shown in the previous sections, depth and surface curvature are then computed from firstand second order temporal derivatives of this \(t\)-parameter image

![Figure 6. Tracking image contours with B-spline snakes. A single span B-spline snake "hangs" in the image until it is swepe by the motion of](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-6-p017.png)

*Figure 6. Tracking image contours with B-spline snakes. A single span B-spline snake "hangs" in the image until it is swepe by the motion of: Tracking image contours with B-spline snakes. A single span B-spline snake "hangs" in the image until it is swepe by the motion of swept by the motion of the camera into the vicinity of a high-contrast edge (top left). The snake then tracks the deforming image contour as the camera is moved vertically upward by the robot. Four samples of an image sequence are shown in which the robot moves with a speed of 20 mm s. Tracking speeds of 15 Hz have been achieved without special-purpose hardware by windowing and avoiding Gaussian smoothing.*

curve by equations (32) and (39). This is a nontrivial practical problem since the epipolar structure is continuously changing for arbitrary viewer motions. It requires a dense image sequence and knowledge of the geometrical and optical characteristics of the camera (the intrinsic parameters, for example, image center, pixel size, and focal length [19, 21, 50]) as well as the camera motion.

Estimates of the camera motion are either determined directly from the position and orientation of the gripper and its relationship with the camera center [49] or are obtained by visual calibration techniques [47]. Extraction of the t-parameter curve can be done in a number of ways. We have implemented two simple methods. The first is an extension of epipolar plane image analysis [10, 53] and allows the recovery of depth and surface curvature at a point. The second method analyses the case of extended displacements and arbitrary rotations of the viewer to recover constraints (bounds) on surface curvature. The epipolar parameterization of the image is greatly simplified for simple motions. In particular, if we consider linear viewer motion perpendicular to the optical axis, epipolar lines are simply corresponding raster lines of subsequent images. Figure 7 shows the spatio. temporal image formed by taking a sequence of images in rapid succession and stacking these sequentially in time. For linear motions of the viewer, the t-parameter image curves are trajectories lying in horizontal slices of the spatiotemporal image. Each horizontal slice corresponds to a different epipolar plane. The trajectories of the image positions of points on an apparent contour (A) and a nearby surface marking (B) are shown as a function of time in the spatiotemporal cross-section of figure 7 and plotted in figure 8. Note that this is a simple extension of epipolar plane image analysis in which the trajectories of fixed, rigid features appear as straight lines in the spatiotemporal cross-section image with a gradient that is proportional to inverse depth [10]. For apparent contours however, the trajectories are no longer straight. It is shown below that the gradient of the trajectory still encodes depth. The curvature determines the curvature of the surface in the epipolar plane.

$$
\begin{align*} X_{t}(0) & =-\frac{f U}{\lambda} \tag{58}\\ X_{t t}(0) & =-\frac{f U^{2} R}{\lambda^{3}} \tag{59} \end{align*}
$$

6.2.1 Estimation of Depth and Surface Curvature. For motion perpendicular to the optical axis and for an apparent contour which at time \(t\) is instantaneously aligned with the optical axis (image position in \( \mathrm{mm} \(X(0)\) last image

![Figure Z. 3D spatiotemporal image. (a) The first and last image](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-z-p018.png)

*Figure Z. 3D spatiotemporal image. (a) The first and last image: Fig. Z. 3D spatiotemporal image. (a) The first and last image from an image sequence taken from a camera mounted on a robot arm and moving horizontally from left to right without rotation. (b) The 3D spatiotemporal image formed from the image sequence piled up sequentially with time. The top of the first image and the bottom of the last image are shown along with the spatiotemporal cross-section corresponding to the same epipolar plane. For simple viewer motions consisting of camera translations perpendicular to the optical axis the spatiotemporal cross-section image is formed by storing the scan-lines (epipolar lines) for a given epipolar plane sequentially in order of time [16].*

where \(U\) is the component of viewer translational veloc ity perpendicular to the optical axis and parallel to the scan line; \(f\) is the focal length of the CCD camera lens, and \(R\) is the radius of curvature of the \(t\)-parameter curve lying in the epipolar plane. The radius of curvature is related to the curvature of the normal section by Meusnier's formula [18]. The normal curvature along the ray is given by where cos o is the angle between the surface normal and the epipolar plane. In this case, it is simply equal to the angle between the image curve normal and the horizontal scan line.

The estimate of depth and surface curvature follow directly from the first and second temporal derivatives of the \(t\)-parameter curve, \(X(t)\) and equations \((58,59)\). Due to measurement noise and vibrations of the robot arm, the trajectory may not be smooth (figures 8, 9, 10) and so these derivatives are computed from the coef ficients of a parabola fitted locally to the data by least squares estimation. The uncertainty due to random im age localization and ego-motion errors can be derived from analysis of the residual errors [44, 14].

$$
\begin{equation*} \kappa^{t}=\frac{1}{R} \cos \phi \tag{60} \end{equation*}
$$

In practice, the viewer will not execute simple translational motions perpendicular to the optical axis

![Figure & Spatictemporal cross-section image trajoctories. For linear](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-8-p019.png)

*Figure & Spatictemporal cross-section image trajoctories. For linear: Fig. & Spatictemporal cross-section image trajoctories. For linear Fig. & Spatiotemporal cross-section image trajectories. For linear motion and epipolar parameterization the 1-parameter surface curves lie in the epipolar plane. The i-parameter spatiotemporal image trajectory is also planar. The gradient and curvature of this trajectory encode depth to the contour generator and curvature in the epipolar plane respectively.*

but will rotate to fixate on an object of interest. For linear translational viewer motions with known camera rotations, the analysis of epipolar plane images is still appropriate if we rectify the detected image curves. Rectification can be performed by a 3X3 rotation matrix relating measurements in the rotated coordinate frame to the standard parallel geometry frame. For arbitrary curvilinear motions the \(t\)-parameter curves are no longer constrained to a single cross section of the spatiotemporal image. Each time instant requires a different epipolar structure and so extracting the \(t\)-parameter curve from the spatiotemporal image poses a more difficult practical problem. From at least three discrete views, it is possible to determine whether or not a contour is extremal. For a surface marking or crease (discontinuity in surface orientation), the three rays should intersect at a point in space for a static scene. For an extremal boundary, however, the contact point slips along a curve, \(\mathbf{r}\left(s_{0}, t\right)\) and the three rays will not intersect (figures 11 and 12). In [14, 51] a sim ple numerical method for estimating depth and surface curvatures from a minimum of three discrete views, by determining the osculating circle in each epipolar plane, is described. 6.2.2 Experimental Results-Curvature from the Spatiotemporal Image. Figure 7 shows the t-parameter (a) and in for st a ce marting (B., The ricorics are both approximately linear with a gradient that deter-

![Figure 22 Relative image positions. The eflect of robot vibrations is](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-22-p019.png)

*Figure 22 Relative image positions. The eflect of robot vibrations is: Relative image positions. The eflect of robot vibrations is Deviation from the straight line trajectory. The curvature of the spatiotemporal trajectories is used to estimate the curvature of the epipolar section. The trajectories are not smooth due to vibrations of the robot manipulator (amplitude 0.2 mm). Their effect on the estimation of curvature is reduced by a least-squares fit to the data. The surface curvatures (expressed as radii of curvature) at A and B are estimated as 51.4 † 8.2 mm and 11.8 ‡ 7.3 mm respectively B is not on an extremal boundary but is on a fixed curve. This is a degenerate case of the parameterization and should ideally have zero "radius of curvature," that is, the spatiotemporal trajectory should Relative image positions. The effect of robot vibrations is greatly reduced if the rate of parallax (relative image positions) is used instead.*

mines the distance for the feature. Depth can be estimated to an accuracy of 1 part in 1000 (table 1). The effect due to surface curvature is very difficult to discern. This is easily seen, however, if we look at the deviation of image position away from the straightline trajectory of a feature at a fixed depth (figure 9). Notice that the image position is noisy due to perturbations in the robot position. Typically the robot vibrations

![Figure II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-2-2-p020.png)

*Figure II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by: Fig. II. Estimating surface curvatures from three discrete vices. Points are selected on image contours in the fine view (6), indicated by views. Points are selected on image contours in the first view (to), indicated by crosses A and B for points on an extremal boundary and surface marking respectively. For epipolar parameterization of the surface, corresponding features lie on epipolar lines in the second and third view (t, and tz). Measurement of the three rays lying in an epipolar plane can be used to estimate surface curvatures (figure 12).*

![Figure 12 Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-12-p025.png)

*Figure 12 Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local: Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local*

![Figure I2. The epipolar plane. Each view defines a cangent to ria. 2).](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-i2-p020.png)

*Figure I2. The epipolar plane. Each view defines a cangent to ria. 2).: Fig. I2. The epipolar plane. Each view defines a cangent to ria. 2). tangent to r(so, t). For linear camera motion and epipolar parameterization the rays and I (So, 1) lie in a plane. Ifr (so, t) can be approximated locally as a circle, it can be uniquely determined from measurements in three views. Table 1. Radius of curvature of the epipolar section estimated from the spatiotemporal trajectory for a point on an extremal boundary (A) and on a surface marking (B).*

have amplitudes between 0.1 mm and 0.2 mm. From (39) we see that these vibrations are amplified by a factor depending on the square of the distance to the feature, and that this results in a large uncertainty in the estimate of surface curvature. Equations (58) and (59) are used to estimate the depth and curvature for a point on the extremal boundary of the vase (A) by fitting a parabola to the spatiotemporal trajectory. The method is repeated for a point that is not on an extremal boundary but is on a nearby surface marking (B). This is a degenerate case of the parameterization. A surface marking can be considered as the limiting case of a point with infinite curvature and hence ideally will have zero "radius or curvature." The estimates of depth and curvature are shown in table 1. The veridical values of curvature were measured using calipers. Note that there is a systematic error, not explained by the random errors in the data. This is possibly due to an error in the assumed ego-motion of the robot or focal length.

### 6.3 Error and Sensitivity Analysis

The previous section showed that the visual motion of apparent contours can be used to estimate surface curvatures of a useful accuracy if the viewer ego-motion is known. However, the estimate of curvature is very sensitive to perturbations in the motion parameters and errors in image contour localization. The effect of small errors and uncertainties can be computed by first-order perturbation analysis [14]. The effects of small errors in the assumed egomotion-position and orientation of the camera-are plotted in figures 13a and 13b (curves labeled I). Accuracies of 1 part in 1000 in the measurement of egomotion are essential for surface curvature estimation.

Parallax based methods measuring surface curvature are in principle based on measuring the relative image motion of nearby points on different contours (47). In practice, this is equivalent (46) to computing the dif ference of radii of curvature at the two points, say A and \(\mathbf{B}\) (figure 7). The radius of curvature measured at a surface marking is determined by errors in image measurement and ego-motion. (For a precisely known viewer motion and for exact contour localization the radius of curvature would be zero at a fixed feature.) It can be used as a reference point to subtract the global additive errors due to imprecise mótion when estimat ing the curvature at the point on the extremal boundary. Figures 13a and 13b (curves labeled II) show how the sensitivity of the relative inverse curvature, \(\Delta R\), to error in position and rotation computed between points A and \(B(twonearbypointsatsimilardepths)\) is reduced by an order of magnitude. This is a striking decrease in sensitivity even though the features do not coincide exactly as the theory required. Note that the sensitivity to image localization errors remains (figure 14). This sensitivity is not reduced by parallax and requires subpixel localization of image contours.

## 7 Applications

| Discriminating Between fixed Features ai tremal Boundari The magnitude of the estimate of the radius of curvature, R, can be used to determine whether a point on an image contour lies on an apparent contour or on the projection of a fixed surface feature such as a crease. shadow, or surface marking.

Fig. 13. Sensitivity of curvature estimated from absolute measurements and parallax to errors in motion. (a) The radius of curvature (R = 1 k') for a point on the extremal boundary (A) is plotted as a function of errors in the camera position (a) and orientation (b). Curvature estimation is highly sensitive to errors in ego-motion. curve I shows that a perturbation of 1 mm in position (in a translation of 100 mm) produces an error of 155% in the estimated radius of curvature. A perturbation of 1 mrad in rotation about an axis defined by the epipolar plane (in a total rotation of 200 mrad) produces an error of 100%. (b) However, if parallax-based measurements are used the estimation of curvature is much more robust to errors in ego-motion. curve II shows the difference in radii of curvature between a point on the extremal boundary (A) and the nearby surface marking (B) plotted against error in the position (a) and orientation (b). The sensitivity is reduced by an order of magnitude, to 19% per mm error and 12% per mrad error respectively. With noisy image measurements or poorly calibrated motion we must test by error analysis the hypothesis that \(R\) is not equal to zero for an extremal boundary. We have seen how to compute the effects of small errors in image measurement, and ego-motion. These are con veniently represented by the covariance of the estimated curvature, \(\sigma_{R}\). The estimate of the radius of curvature and its uncertainty is then used to test the hypothesis of an extremal boundary. In particular if we assume that the error in the estimate of the radius has a nor mal distribution (as an approximation to the student- \(t\)

$$
\begin{equation*} -1.96 \sigma_{R}<R<1.96 \sigma_{R} \tag{61} \end{equation*}
$$

![Figure M. Sensitivity of curvature estimate so errors in image contour](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-1000-p022.png)

*Figure M. Sensitivity of curvature estimate so errors in image contour: Fig. M. Sensitivity of curvature estimate so errors in image contour*

By using parallax-based (relative) measurements the discrimination is greatly improved and is limited by the finite separation between the points as predicted by (50). For the example of figure 11 this limit corresponds to a relative curvature of approximately 3 mm. This, however, requires that we have available a fixed nearby reference point. Suppose now that no known surface feature has been identified in advance. Can the robust relative measurements be made to bootstrap themselves without an independent surface reference? It is possible by relative (two-point) curvature measurements obtained for a small set of nearby points to determine pairs which are fixed features. They will have zero relative radii of curvature. Once a fixed feature is detected it can act as stable reference for estimating the curvature at extremal boundaries.

In detecting an apparent contour we have also determined on which side the surface lies and so can compute the sign of Gaussian curvature from the curvature of the image contour. Figure 15 shows a selected number of contours which have been automatically tracked and are correctly labeled by testing for the sign and magnitude of R.

![Figure 1S. Detecting and labeling extremal boundaries. The magnitade of the](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-1s-p022.png)

*Figure 1S. Detecting and labeling extremal boundaries. The magnitade of the: S. Detecting and labeling extremal boundaries. The magnitade of the Sensitivity of curvature estimate to errors in image contour localization. a X label indicates a fixed feature. A > label indicates an apparent contour. The surface lies to the right as one moves in the direction of the twin arrows [37]. The sign of Gaussian curvature can then be inferred directly from the sign of the curvature of the apparent contour.*

### 7.2 Reconstruction of Surfaces

In the vicinity of the extremal boundary we can recover the two families of parametric curves. These constitute a conjugate grid of surface curves: \(s\)-parameter curves (the extremal contour generators from the different viewpoints) and \(t\)-parameter curves (the intersection of a pencil of epipolar planes defined by the first two view points and the surface). The recovered strip of surface is shown in figure 16 projected into the image from a fourth viewpoint. The reconstructed surface obtained by extrapolation of the computed surface curvatures at the extremal boundary A of the vase is shown from a new viewpoint in figure 17.

### 7.3 Visual Navigation Around Curved Surfaces

In this section results are presented showing how a moving robot manipulator can exploit the visually derived 3D shape information in real time to plan a smooth, safe path around an obstacle placed in its path. The scenario of this work is that the start position and goal position for a mobile camera are fixed and the robot is instructed to reach the goal from the start position, skirting around any curved obstacles that would be encountered on a straight line path from the current position to the goal. The camera first localizes an apparent contour and makes a small sideways motion to generate visual motion. This allows it to compute the distance to the contour generator, the "sidedness" of the contour, and more importantly the curvature of the visible surface in the epipolar plane. A safe path around the curved object is then planned by extrapolating the computed curvatures with a correction to allow for the

### 7.4 Manipulation of Curved Objects

Surface curvature recovered directly from the deformation of the apparent contour (instead of dense depth maps) yields useful information for path planning. This information is also important for grasping curved objects.

![Figure 18 Visually guided navigation around curved obstacles. Th](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-18-p024.png)

*Figure 18 Visually guided navigation around curved obstacles. Th: Visually guided navigation around curved obstacles. Th The visual motion of an apparent contour under known viewer motion is used to estimate the position, orientation, and surface curvature of the visible surface. In addition to this quantitative information the visual motion of the apparent contour can also determine which side of the contour is free space. This qualitative and quantitative information is used to map out a safe path around the unmodeled obstacle. The sequence of images shows the robot manipulator's safe execution of the planned path, seen from two viewpoints.*

![Figure 12 Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-12-p025.png)

*Figure 12 Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local: Visually guided navigation over undulsing surface. After defecting a borisoetal image contour, the image motion due to a small local*

![Figure 20. Visually guided manipulation of piecewise curved objects. The manipulacion of curved objects roquires precise 3D shape (curvature)](/Users/evanthayer/Projects/stepview/docs/1992_surface_shape_from_the_deformation_of_apparent_contours/figures/figure-20-p025.png)

*Figure 20. Visually guided manipulation of piecewise curved objects. The manipulacion of curved objects roquires precise 3D shape (curvature): Visually guided manipulation of piecewise curved objects. The manipulacion of curved objects roquires precise 3D shape (curvature) Visually guided navigation over undulating surface. After detecting a horizontal image contour, the image motion due to a small local vertical viewer motion is used to estimate the distance to the contour generator. A larger extended motion is then used to estimate the surface curvature at the contour generator. This is used to map out and execute a safe path over the obstacle, shown in this sequence of images. manipulation of curved objects requires precise 3D shape (curvature) information. The accuracy of measurements of surface curvature based on the deformation of a single apparent contour is limited by uncertainty in the viewer motion. The effect of errors in viewer motion is greatly reduced and the accuracy of surface curvature estimates consequently greatly improved, by using the rate of parallax. In the example shown the relative motion between the image of the projection of the crease of the box (B) and the apparent contour of the vase (A) is used to estimate surface curvature to an accuracy of 15 mm (in a measurement of 40 mm) and the contour generator position to the nearest 1 mm (at a distance of 1 m). This information is used to guide the manipulator*

Reliable estimates of surface curvature can be used to determine grasping points. Figure 20 shows an example of a scene with a vase placed approximately 1 m away from a robot manipulator equipped with a suction gripper. Estimates of surface curvature at the extremal boundary are used to position a suction gripper for manipulation. The robot initializes a snake which localizes a nearby high-contrast edge. In the example shown the snake initially finds the edge of the cardboard box (B). The robot then makes a small local motion of a few centimeters to estimate the depth of the feature. It uses this informtion so that it can then track the contrast edge over a larger baseline while fixating (keeping the edge in the center of the image). Before executing the larger motion of 15 cm the first snake (parent) spawns a child snake which finds a second nearby edge (A). The two edges are then tracked together, allowing the accurate estimation of surface curvature by reducing the sensitivity to robot "wobble" and systematic errors in the robot motion (see figures 9 and 10). The estimates of curvature are accurate to a few millimeters. This is in contrast to estimates of curvature based on the absolute motion of an apparent contour which deliver curvature estimates which are only correct to the nearest centimeter. The extrapolation of these surface curvatures allows the robot to plan a grasping position which is then successfully executed (figure 20).

## 8 Summary and Conclusions

This paper has

- — related the geometry of apparent contours to the differential geometry of the visible surface and to the analysis of visual motion.

- — shown how a moving monocular observer can recover an exact and complete description of the visible surface in the vicinity of a contour generator from the deformation of apparent contours. This requires the computation of spatiotemporal derivatives (up to second order) of the image and known viewer motion. The epipolar parameterization of the spatiotemporal image and surface was introduced. Its advantages include that it allows all image contours to be analyzed in the same framework. Image velocities allow the recovery of the contour generator while image accelerations allow the computation of surface curvature. A consequence of this is that the visual motion of curves can be used to detect extremal boundaries and distinguish them from rigid contour generators such as surface markings, shadows, or creases.

- — shown how the relative motion of image curves (parallax-based measurements) can be used to provide robust estimates of surface curvature which are

- independent of (and hence insensitive to) the exact details of the viewer's motion.

- presented a simple, computationally efficient method for accurately extracting image curves from real images and tracking their temporal evolution. This was an extension of tracking with snakes— energy minimizing splines guided by "image forces" —which avoids computing the internal energies by representing sections of curves as cubic B-splines. Moreover real-time processing (15 frames per second) is achieved by windowing and avoiding Gaussian smoothing.

- analyzed the effect of errors in the knowledge of assumed viewer motion (camera positon and orientation) and in the localization of image contours on the estimates of depth and curvature. Uncertainty and sensitivity analysis was important for two reasons. first, it is useful to compute bounds on the estimates of surface curvature. This is critical in discriminating fixed features from extremal boundaries-deciding whether curvature along the ray is bounded or not-since with noisy measurements and poorly calibrated viewer motions, we must test by error analysis the hypothesis that the curvature is unbounded at a fixed feature. Second, sensitivity analysis was used to substantiate the claim that parallax methods—using the relative image motion of nearby contours-allow the robust recovery of surface curvature. It was shown that estimates of curvature based on absolute measurements of image position are extremely sensitive to motion calibration, requiring accuracies of the order of 1 part in 1000. Estimates of curvature based on relative measurements prove to be orders of magnitude less sensitive to errors in robot position and orientation. The sensitivity to image localization remains, however, but is reduced by integrating measurements from a large number of viewpoints.

- — as an illustration of their power, these motion analysis techniques have been used to achieve something which has so far eluded analysis based on photometric measurements alone: namely reliable discrimination between fixed surface features and points on extremal boundaries. On which side of the image contour the obscuring surface lies can also be determined. As well as using these methods to detect and label extremal boundaries it was shown how they can recover strips of surfaces in the vicinity of extremal boundaries.

- presented results of the real-time implementation of these algorithms for use in tasks involving the active

motion planning and object manipulation. Examples exploiting the visually derived shape for navigation round and the manipulation of piecewise smoot urved objects were presented

$$
K=\frac{\kappa^{s} \kappa^{t}}{\sin ^{2} \theta}
$$

## Acknowledgments

The authors acknowledge discussions with Professor Mike Brady, Dr. David Forsyth, Dr. Steve Maybank, and Dr. Andrew Zisserman and the contribution of Zhiyan Xie in programming the Adept Robot. This work was partially funded by Esprit BRA 3274 (first) and the SERC. Roberto Cipolla gratefully acknowledges the support of the IBM UK Scientific Centre, St. Hugh's College, Oxford, and the Toshiba Corporation Research and Development Centre, Japan.

Notes

- A summary of this theory was first presented by us in [9]. A similar approach was followed by [51, 1].

- Subscripts denote differentiation with respect to the subscript parameter. Superscripts will be used as labels.

- The normal curvature is the curvature of the planar section of the surface through the normal and tangent vector.

- These are in fact the eigenvalues and respective eigenvectors of the matrix G-'D. The determinant of this matrix (product of the two principal curvatures) is called the Gaussian curvature, K. It determines qualitatively a surface's shape. A surface patch that is locally hyperbolic (saddle-like) has principal curvatures of opposite sign and hence negative Gaussian curvature. Elliptic surface patches (concave or convex) have principal curvatures with the same sign and hence positive Gaussian curvature. A locally flat surface patch will have zero Gaussian curvature.

- If we define the surface normal as being outwards from the solid surface, the normal curvature will be negative in any direction for a convex surface patch.

- In general the Gaussian curvature can be determined from the determinant of G-'D or equivalently the ratio of the determinants of the matrixes of coefficients of the second and first fundamental forms. From (34) and (35) it is trivial to show that Gaussian curvature can be expressed by

Substituting (23) for \(\kappa^{s}\) allows us to derive the result.

- The forces are derived from an arbitrary field. They are not natural forces.

- Small amounts of smoothing can be achieved economically b defocusing the image until the desired degree of blur is achieved. Whilst this worked satisfactorily, it was found that the tracker continued to operate just as well when the lens was sharply focused.

## 112 Cipolla and Blake

\begin{aligned} R^{\Delta \mathbf{Q}}= & {\left[\frac{-2 \lambda(\mathbf{U} \cdot \delta)}{\mathbf{U} \cdot \mathbf{n}}-\frac{\lambda^{3}\left(\Omega_{t} \wedge \delta\right) \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right.} \\ & -\frac{2 \lambda^{2}(\mathbf{U} \cdot \delta)(\Omega \wedge \mathbf{Q}) \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}} \\ & -\frac{2 \lambda^{2}(\mathbf{U} \cdot \mathbf{Q})(\Omega \wedge \delta) \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}} \\ & \left.+\frac{\lambda^{3}(\mathbf{\Omega} \cdot \delta)(\mathbf{\Omega} \cdot \mathbf{n})}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right] \\ R^{\mathbf{n}}= & \delta \cdot \mathbf{n}\left[\frac{\lambda^{2} \mathbf{U}_{t} \cdot \mathbf{Q}}{(\mathbf{U} \cdot \mathbf{n})^{2}}-\frac{\lambda|\mathbf{U}|^{2}}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right. \\ & +\frac{(\mathbf{U} \cdot \mathbf{Q})}{\mathbf{U} \cdot \mathbf{n}} \frac{1}{\kappa^{t 2}}+\frac{2 \lambda\left(\mathbf{U} \cdot \mathbf{Q}^{2}\right.}{(\mathbf{U} \cdot \mathbf{n})^{2}} \\ & \left.-\frac{\lambda^{2}(\Omega \wedge \mathbf{Q}) \cdot \mathbf{U}}{(\mathbf{U} \cdot \mathbf{n})^{2}}-\frac{\lambda^{3}|\Omega|^{2}}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right] \end{aligned} an error is introduced into the estimate of surface curvature due to the fact that the features are not instantaneously aligned nor at the same depth nor in the same tangent plane:

$$
\begin{equation*} \Delta R=\Delta \hat{R}+R^{\text {error }} \tag{72} \end{equation*}
$$

where \(R^{\text {error }}\) consists of errors due to the 3 effects mentioned above.

$$
\begin{equation*} R^{\text {error }}=R^{\Delta \lambda}+R^{\Delta \mathbf{Q}}+R^{\mathbf{n}} \tag{73} \end{equation*}
$$

These are easily computed by looking at the differences of equation (45) for the two points. Only first-order errors are listed.

$$
\begin{aligned} R^{\Delta \lambda}= & \Delta \lambda\left[\frac{3}{\lambda \kappa^{t 2}}+\frac{4 \mathbf{U} \cdot \mathbf{Q}}{\mathbf{U} \cdot \mathbf{n}}+\frac{\lambda \mathbf{U}_{t} \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right. \\ & \left.+\frac{2 \lambda(\mathbf{U} \cdot \mathbf{Q})(\mathbf{\Omega} \wedge \mathbf{Q}) \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}}+\frac{\lambda(\mathbf{U} \wedge \mathbf{\Omega}) \cdot \mathbf{n}}{(\mathbf{U} \cdot \mathbf{n})^{2}}\right] \end{aligned}
$$

## References

- E. Arbogast, Modélisation automatique d'objets non polyédriques par observation monoculaire, Ph.D. thesis, Institut National Polytechnique de Grenoble, 1991. S.T. Barnard and M.A. Fischler, computational stereo, ACM Computing Surveys 14(4):553-572, 1982. H.G. Barrow and J.M. Tenenbaum, Recovering intrinisic scene characteristics from images. In A. Hanson and E. Riseman, eds., Computer Vision Systems. Academic Press: New York, 1978. H.G. Barrow and J.M. Tenenbaum, Interpreting line drawings as three-dimensional surfaces, Artificial Intelligence 17:75-116, 1981. R.H. Bartels, J.C. Beatty, and B.A. Barsky, An Introduction to Splines for Use in Computer Graphics and Geometric Modeling. Morgan Kaufmann: Los Altos, CA, 1987. L.M.H. Beusmans, D.D. Hoffman, and B.M. Bennett, Description of solid shape and its inference from occluding contours, J. Opt. Soc. Amer. A 4:1155-1167, 1987. A. Blake, J.M. Brady, R. Cipolla, Z. Xie, and A. Zisserman, Visual navigation around curved obstacles, Proc. IEEE Intern. Conf. Robotics Automat. 3:2490-2495, 1991. A. Blake and H. Bulthoff, Shape from specularities: Computation and psychophysics, Phil. Trans. Roy. Soc. London 331:237-252, A. Blake and R. Cipolla, Robust estimation of surface curvature from deformation of apparent contours. O. Faugeras, ed., Proc. Ist Europ. Conf. Comput. Vis., Antibes, Fr., pp. 465-474, Springer-Verlag: New York, 1990. R.C. Bolles, H.H. Baker, and D.H. Marimont, Epipolar-plane image analysis: An approach to determining structure, Intern. J. Comput. Vis. 1:7-55, 1987. M. Brady, J. Ponce, A. Yuille, and H. Asada, Describing surfaces, Comput. Vis. Graph. Image Process. 32:1-28, 1985. J. Callahan and R. Weiss, A model for describing surface shape, Proc. Conf. Comput. Vis. Patt. Recog., San Francisco, pp. 240-245, 1985. J.F. Canny, A computational approach to edge detection; JEEE Trans. Patt. Anal. Mach. INtell. 8:679-698, 1986.

- R. Cipolla, Active visual inference of surface shape, Ph.D. thesis, University of Oxford, 1991.

- R. Cipolla and A. Blake, The dynamic analysis of apparent contours, Proc. 3rd Intern. Conf. Comput. Vis., pp. 616-623, 1990.

- R. Cipolla and M. Yamamoto, Stereoscopic tracking of bodies in motion, Image Vis. Comput. 8(1):85-90, 1990.

- R.M. Curwen, A. Blake, and R. Cipolla, Parallel implementation of lagrangian dynamics for real-time snakes, Proc. 2nd British Mach. Vis. Conf., 1991.

- M.P. DoCarmo, Differential Geometry of curves and Surfaces, Prentice-Hall: Englewood Cliffs, NJ, 1976.

- O.D Faugeras and G. Toscani, The calibration problem for stereo, Proc. Conf. Comput. Vis. Patt. Recogn., Miami Beach, pp. 15-20, 1986.

- I.D. Faux and M.J. Pratt, computational Geometry for Design and Manufacture, Ellis-Horwood, 1979.

- S. Ganapathy, decomposition of transformation matrices for robot vision, Proc. IEEE Conf. Robotics, pp. 130-139, 1984.

- P.J. Giblin and R. Weiss, Reconstruction of surfaces from profiles, Proc. Ist. Intern. Conf. Comput. Vis., London, pp. 136-144, 1987.

- P.J. Giblin and M.G. Soares, On the geometry of a surface and its singular profiles, Image Vis. Comput. 6(4):225-234, 1988.

- C.G. Harris, Determination of ego-motion from matched points,

- 3rd Alvey Vis. Conf., pp. 189-192, 1987.

- H. von Helmholtz, Treatise on Physiological Optics, Dover: New York, 1925.

- B.K.P. Horn, Robot Vision. McGraw-Hill, NY, 1986.

- B.K.P. Horn, Closed-form solution of absolute orientation using unit quaternions. J. Opt. Soc. Amer. A4(4):629-642, 1987.

- M. Kass, A. Witkin, and D. Terzopoulos, Snakes: active contour models, Proc. Ist Intern. Conf. Comput. Vis., London, pp. 259-268. 1987.

- J.J. Koenderink, What does the occluding contour tell us about solid shape? Perception 13:321-330, 1984.

- J.J. Koenderink, Optic flow, Vision Research 26(1):161-179, 1986.

- J.J. Koenderink, Solid Shape, MIT Press: Cambridge, MA, 1990.

- J.J. Koenderink and A.J. Van Doorn, Invariant properties of the motion parallax field due to the movement of rigid bodies relative to an observer, Optica Acta 22(9):773-791, 1975.

- J.J. Koenderink and A.J. Van Doorn, The singularities of the visual mapping, Biological Cybernetics 24:51-59, 1976.

- J.J. Koenderink and A.J. Van Doorn, The shape of smooth objects and the way contours end, Perception 11:129-137, 1982.

- M.M. Lipschutz, Differential Geometry, McGraw-Hill: New York, 1969.

- H.C. Longuet-Higgins and K. Pradzny, The interpretation of a moving retinal image, Proc. Roy. Soc. London B208:385-397,

- J. Malik, Interpreting line drawings of curved objects, Intern. J. Comput. Vis. 1:73-103, 1987.

- D. Marr, analysis of occluding contour, Proc. Roy. Soc. London 197:441-475, 1977.

- G. Medioni and Y. Yasumoto, Corner detection and curve representation using curve b-splines, Proc. Conf. Comput. Vis. Patt. Recog., Miami Beach, pp. 764-769, 1986.

- S.J. Maybank, The angular velocity associated with the optical flow field arising from motion through a rigid environment, Proc. Roy. Soc. London A401:317-326, 1985.

- S. Menet, P. Saint-Marc, and G. Medioni, B-snakes: implementation and application to stereo, Proc. DARPA, pp. 720-726, 1990. R.S. Millman and G.D. Parker, Elements of Differential Geometry, Prentice-Hall: Englewood Cliffs, NJ, 1977. B. O'Neill, Elementary Differential Geometry, Academic Press: San Diego, CA, 1966. C.R Rao, Linear Statistical Inference and Its Applications, Wiley: New York, 1973. J.H. Rieger and D.L. Lawton, Processing differential image motion, J. Opt. Soc. Amer. A2(2):354-360, 1985. G. Scott, The alternative snake-and other animals, Proc. 3rd Alvey Vis. Conf., pp. 341-347, 1987. R.Y. Tsai, A versatile camera calibration technique for highaccuracy 3D machine vision metrology using off-the-shelf tv cameras and lenses. IEEE J. Robot. Automat. RA-3(4):323-344, 1987. R.Y. Tsai and T.S. Huang, Uniqueness and estimation of threedimensional motion parameters of a rigid object with curved surfaces, IEEE Trans. Patt. Anal. Mach. Intell. 6(1):13-26, 1984. R.Y. Tsai and R.K. Lenz, A new technique for fully autonomous and efficient 3D robotics hand-eye calibration, 4th Intern. Symp. Robotics Res., Santa Cruz, CA, pp. 287-297, 1987. R.Y. Tsai and R.K. Lenz, Techniques for calibration of the scale factor and image center for high accuracy 3D machine vision metrology, IEEE Trans. Patt. Anal. Mach. Intell. 10(5):713-720, R. Vaillant and O.D. Faugeras, Using occluding contours for recovering shape properties of objects. (Submitted to Trans. D. Weinshall, Qualitative depth from stereo, with applications, Comput. Vis. Graph. Image Process. 49:222-241, 1990. M. Yamamoto, Motion analysis using the visualized locus method, Trans. Inform. Process. Soc. Japan 22(5):442-449, 1981 Appendix A. Determining Su · n from the Spatiotemporal Image Q(s, t) If the surface marking is a discrete point (image position \(\mathbf-Q}^-*} \)) it is possible in principle to measure the image velocity, \(\mathbf-Q}_-t}^-*} \) and acceleration, \(\mathbf-Q}_-t t}^-*} \) directly from the image without any assumption about viewer motion. This is impossible for a point on an image curve. Measuring the (real) image velocity \(\mathbf-Q}_-t} \) (and acclera tion \(\mathbf-Q}_-t t} \)) for a point on an image curve requires knowledge of the viewer motion-equation (27). Only the normal component of image velocity can be obtained from local measurements at a curve. It is shown below however that for a discrete point-curve pair, \(\boldsymbol-\delta}_-t t} \cdot \mathbf-n}- \) the normal component of the relative image acceleration-is completely determined from measurements on the spatiotemporal image. This result is important be cause it demonstrates the possibility of obtaining robust inferences of surface geometry that are independent of any assumption of viewer motion. The proof depends on reparameterizing the spatiotemporal image so that it is independent of knowledge

- of viewer motion. In the epipolar parameterization of the spatiotemporal image, \(\mathbf-Q}(s, t) \), the \(s \)-parameter curves were defned to be the image contours while the \(t \)-parameter curves were defined by equation (27) so that at any instant the magnitude and direction of the tangent to a \(t \)-parameter curve is equal to the (real) image velocity, \(\tilde-\mathbf-Q}}_-t} \)-more precisely, \(\left.(\partial \tilde-\mathbf-Q}} / \partial t)\right|_-s} \).

- A parameterization which is completely independent of knowledge of viewer motion, \(\tilde-\mathbf-Q}}(\bar-s}, t) \), where \(s \) is a function of \(s \) and \(t, \bar-s}(s, t) \) can be chosen. Consider, for example, a parameterization where the \(t \)-parameter curves (with tangent \(\left.(\partial \tilde-\mathbf-Q}} / \partial t)\right|_-\bar-s}} \)) are chosen to be or thogonal to the \(\bar-s} \)-parameter curves (with tangent \(\left.(\partial \tilde-\mathbf-Q}} / \partial \bar-s})\right|_-t} \))-the image contours. Equivalently the \(t \) parameter curves are defined to be parallel to the curve normal \(\mathbf-n} \), \begin-align*} \tilde-\mathbf-Q}} & =\tilde-\mathbf-Q}}^-*} \tag-68}\\ \tilde-\mathbf-Q}}_-t} & =\tilde-\mathbf-Q}}_-t}^-*} \tag-69} \end-align*}

- where ß is the magnitude of the normal component of the (real) image velocity. Such a parameterization can always be set up in the image. It is now possible to express the (real) image velocities and acclerations in terms of the new parameterization.

- From (64) we see that \(\left.(\partial \bar-s} / \partial t)\right|_-s} \) determines the magni tude of the tangential component of image-curve veloc ity and is not directly available from the spatiotemporal image. The other quantities in the right-hand side of the (67) are directly measurable from the spatiotemporal image. They are determined by the curvature of the However the discrete point (with image position \(\tilde-\mathbf-Q}}^-*} \)) which is instantaneously aligned with the extremal boundary has the same image velocity, \(\tilde-\mathbf-Q}}_-t}^-*} \), as the point on the apparent contour. From (27), Since \(\tilde-\mathbf-Q}}_-t}^-*} \) is measurable it allow us to determine the tangential component of the image velocity

- \begin-equation*} \left.\frac-\partial \tilde-\mathbf-Q}}}-\partial t}\right|_-\bar-s}}=\beta \mathbf-n} \tag-62} \end-equation*} \begin-equation*} \left.\frac-\partial \bar-s}}-\partial t}\right|_-s}=\frac-\left.\tilde-\mathbf-Q}}_-t} \cdot-}^-\partial \tilde-\mathbf-Q}}}\right|_-\partial \bar-s}}}-\left.\left|\frac-\partial \tilde-\mathbf-Q}}}-\partial \bar-s}}\right|_-t}\right|^-2}} \tag-70} \end-equation*} and hence \(\tilde-\mathbf-Q}}_-t t} \cdot \mathbf-n} \) and \(\boldsymbol-\delta}_-t t} \cdot \mathbf-n} \) from spatiotemporal im age measurements. Appendix B. Correction for Parallax-Based Measurements when Image Points are not Coincident

- \begin-align*} \tilde-\mathbf-Q}}_-t}= & \left.\frac-\partial \tilde-\mathbf-Q}}}-\partial t}\right|_-\bar-s}} \tag-63}\\ = & \left.\left.\frac-\partial \bar-s}}-\partial t}\right|_-s} \frac-\partial \tilde-\mathbf-Q}}}-\partial \bar-s}}\right|_-t}+\left.\frac-\partial \tilde-\mathbf-Q}}}-\partial t}\right|_-\bar-s}} \tag-64}\\ \tilde-\mathbf-Q}}_-t t}= & \left.\frac-\partial^-2} \tilde-\mathbf-Q}}}-\partial t^-2}}\right|_-s} \tag-65}\\ = & \left.\left.\left.\frac-\partial^-2} \bar-s}}-\partial t^-2}}\right|_-s} \frac-\partial \tilde-\mathbf-Q}}}-\partial \bar-s}}\right|_-t}+\left(\left.\frac-\partial \bar-s}}-\partial t}\right|_-s}\right)^-2} \frac-\partial^-2} \tilde-\mathbf-Q}}}-\partial \bar-s}^-2}} \right\rvert\, \\ & +\left.\left.2 \frac-\partial \bar-s}}-\partial t}\right|_-s} \frac-\partial}-\partial \bar-s}}\left(\left.\frac-\partial \tilde-\mathbf-Q}}}-\partial t}\right|_-\bar-s}}\right)\right|_-t}+\left.\frac-\partial^-2} \tilde-\mathbf-Q}}}-\partial t^-2}}\right|_-\bar-s}} \tag-66}\\ \tilde-\mathbf-Q}}_-t} \cdot \mathbf-n}= & \left.\left(\left.\frac-\partial \bar-s}}-\partial t}\right|_-s}\right)^-2} \frac-\partial^-2} \tilde-\mathbf-Q}}}-\partial \bar-s}^-2}}\right|_-t} \cdot \mathbf-n} \\ & +\left.\left.2 \frac-\partial \bar-s}}-\partial t}\right|_-s} \frac-\partial}-\partial \bar-s}}\left(\left.\frac-\partial \tilde-\mathbf-Q}}}-\partial t}\right|_-\bar-s}}\right)\right|_-t} \cdot \mathbf-n}+\left.\frac-\partial^-2} \tilde-\mathbf-Q}}}-\partial t^-2}}\right|_-\bar-s}} \cdot \mathbf-n} \tag-67} \end-align*} The theory relating relative inverse curvatures to the rate of parallax assumed that the two points \(\mathbf-Q}^-(1)} \) and \(\mathbf-Q}^-(2)} \) were actually coincident in the image, and that the underlying surface points were also coincident and hence at the same dept \(\lambda^-(1)}=\lambda^-(2)} \). In practice, point pairs used as features will not coincide exactly. We ana lyze below the effects of a finite separation in image positions \(\Delta \mathbf-Q}=\delta \), and a difference in depths of the 2 features, \(\Delta \lambda. \mathbf-n} \) is the surface normal at the second point, \(\mathbf-Q}^-(2)} \). \begin-aligned} \mathbf-Q}^-(2)} & =\mathbf-Q} \\ \mathbf-Q}^-(1)} & =\mathbf-Q}+\Delta \mathbf-Q} \\ \lambda^-(2)} & =\lambda \\ \lambda^-(1)} & =\lambda+\Delta \lambda \\ \mathbf-Q}^-(2)} \cdot \mathbf-n} & =0 \\ \mathbf-Q}^-(1)} \cdot \mathbf-n} & =\Delta \mathbf-Q} \cdot \mathbf-n} \end-aligned} If the relative inverse curvature is computed from (47), \begin-equation*} \Delta \hat-R}=\frac-(\mathbf-U} \cdot \mathbf-n})^-2}}-\lambda^-3}} \frac-1}-\delta_-t t} \cdot \mathbf-n}} \tag-71} \end-equation*}
