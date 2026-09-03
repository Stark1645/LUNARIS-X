# System Architecture: SIH26166 Lunar Image Correspondence & Registration

## 1. Architectural Philosophy
The registration system addresses the core physics of Chandrayaan-2 imagery by decoupling **illumination (shadows)** from **physical surface morphology**, bridging **extreme scale differences (1:1 to 1:20+)** hierarchically, and enforcing **uniform spatial distribution** of geometrically verified inliers prior to sub-pixel refinement.

```
+===================================================================================================================+
|                                  SIH26166 — MASTER REGISTRATION WORKFLOW ARCHITECTURE                             |
+===================================================================================================================+

   +---------------------------------------+                     +---------------------------------------+
   |         SOURCE / MOVING IMAGE         |                     |        REFERENCE / FIXED IMAGE        |
   | (Chandrayaan-2 Acquired Optical Image)|                     |  (Overlapping Lunar Reference Image)  |
   +-------------------+-------------------+                     +-------------------+-------------------+
                       |                                                             |
                       +------------------------------+------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |       IMAGE VALIDATION        |
                                      | • Sensor Format Verification  |
                                      | • PDS4/PDS3 Metadata Parsing  |
                                      | • Coordinate & Extent Check   |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |         PREPROCESSING         |
                                      | • Radiometric Normalization   |
                                      | • Contrast Stretching & Denoise|
                                      | • Invalid Pixel/Shadow Masking|
                                      +---------------+---------------+
                                                      |
                       +------------------------------+------------------------------+
                       | SIH CHALLENGE: SCALE VARIATION                              |
                       | • Altitudes • Resolutions (0.25m-250m) • Scale Ratios (1:20)|
                       +------------------------------+------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |   MULTI-SCALE REPRESENTATION  |
                                      | • Hierarchical Scale Pyramids |
                                      | • Multi-Resolution Processing |
                                      | • Scale-Aware Search Space    |
                                      +---------------+---------------+
                                                      |
                       +------------------------------+------------------------------+
                       | SIH CHALLENGE: ILLUMINATION VARIATION                       |
                       | • Sun Azimuth • Sun Elevation • Surface Lighting • Shadows  |
                       +------------------------------+------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |    FEATURE / CORRESPONDENCE   |
                                      |           DETECTION           |
                                      | • Classical SIFT Baseline     |
                                      | • RIFT / Log-Gabor Phase Map  |
                                      | • Scale-Space Keypoints       |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |       FEATURE MATCHING        |
                                      | • Descriptor Distance Metric  |
                                      | • Nearest-Neighbor Matching   |
                                      | • Cross-Check Consistency     |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |        MATCH FILTERING        |
                                      | • Lowe's Ratio Test (0.75-0.8)|
                                      | • Mutual Match Enforcement    |
                                      | • Ambiguity Rejection        |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     GEOMETRIC VERIFICATION    |
                                      | • RANSAC / USAC-Based Robust  |
                                      |   Geometric Verification      |
                                      | • Geometric Consistency       |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |       INLIER / OUTLIER        |
                                      |          SEPARATION           |
                                      | ┌───────────────────────────┐ |
                                      | │ [Candidate Matches]       │ |
                                      | │             │             │ |
                                      | │   RANSAC / USAC Robust    │ |
                                      | │       /          \        │ |
                                      | │      v            v       │ |
                                      | │ [RELIABLE      [OUTLIERS] │ |
                                      | │  INLIERS]    (Discarded)  │ |
                                      | └───────────────────────────┘ |
                                      +---------------+---------------+
                                                      |
                                                      v (Verified Inliers Only)
                                      +-------------------------------+
                                      |      UNIFORM DISTRIBUTION     |
                                      |      OF RELIABLE INLIERS      |
                                      | • Select reliable inlier      |
                                      |   correspondences with spatial|
                                      |   coverage across the image   |
                                      | • Grid-Based Binning          |
                                      | • Spatial Dispersion Filter   |
                                      | • Prevent Crater Clustering   |
                                      +---------------+---------------+
                                                      |
                       +------------------------------+------------------------------+
                       | SIH CHALLENGE: VIEWPOINT VARIATION                          |
                       | • Position • Orientation • Shift • Rotation • Perspective   |
                       +------------------------------+------------------------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     TRANSFORMATION MODEL      |
                                      |          SELECTION            |
                                      | • Translation                 |
                                      | • Similarity                  |
                                      | • Affine                      |
                                      | • Homography (Projective)     |
                                      | * Note: Select model by       |
                                      |   imaging geometry & evidence |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |   TRANSFORMATION ESTIMATION   |
                                      | • Least-Squares Parameter Fit |
                                      | • Robust Regularization       |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     SUB-PIXEL REFINEMENT      |
                                      | • Initial Correspondence      |
                                      | • Local Correlation Hessian   |
                                      | • 2D Parabolic Taylor Surface |
                                      | • Fractional Displacement Fit |
                                      | • Measured Residual Sub-Pixel |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     REGISTER SOURCE IMAGE     |
                                      |      TO REFERENCE FRAME       |
                                      | • Backward Bilinear/Bicubic   |
                                      | • Dynamic Range Alignment     |
                                      +---------------+---------------+
                                                      |
                                                      v
+===================================================================================================================+
|                                                  SYSTEM OUTPUTS                                                   |
+===================================================================================================================+
|                                                                                                                   |
|   +--------------------------+    +--------------------------+    +-------------------------------------------+   |
|   |    REGISTERED PRODUCT    |    |   CORRESPONDING MATCH    |    |            REGISTRATION QUALITY           |   |
|   |                          |    |          POINTS          |    |               METRICS PANEL               |   |
|   | • Source/Moving Image    |    |                          |    |                                           |   |
|   |   transformed & aligned  |    | • Candidate Matches      |    | • RMSE (Reprojection Error) [px]          |   |
|   |   to Reference/Fixed     |    | • Verified Inliers (Green|    | • Inlier Match Count                      |   |
|   |   coordinate frame       |    | • Outliers (Red/Filtered)|    | • Inlier Ratio (%)                        |   |
|   | • Difference Map         |    | • Correspondence Vectors |    | • Measured Sub-Pixel Error [px]           |   |
|   | • Alpha Slider Overlay   |    | • Spatial Coverage Plot  |    | • Spatial Match Coverage / Gini ($G_k$)   |   |
|   | • Checkerboard Composite |    | • Exportable CSV Points  |    | • Processing Time / Latency [s]           |   |
|   | • GeoTIFF / PNG Export   |    |                          |    | * Note: Values generated from actual      |   |
|   |                          |    |                          |    |   experiments; N/A if not yet evaluated   |   |
|   +--------------------------+    +--------------------------+    +-------------------------------------------+   |
+===================================================================================================================+
```

---

## 2. Component Breakdown

### 2.1 Stage 1: Validation, Preprocessing & Multi-Scale Representation
- Reads PDS4 XML metadata: ground sampling distance (GSD), solar azimuth, solar incidence, latitude/longitude bounds.
- Preprocessing applies radiometric percentile stretching (2%–98%) and shadow mask generation.
- Generates Gaussian scale pyramids $\mathcal{P}^{(k)}$ such that octave scales match within $1.5\times$ resolution increments, enabling stepwise registration across $20\times+$ scale disparities (TMC-2 $5\text{ m/px}$ to OHRC $0.25\text{ m/px}$).

### 2.2 Stage 2: Feature Detection & Phase Congruency
- SIFT baseline: Multi-scale DoG extrema with 128-d gradient histograms.
- RIFT illumination-robust baseline (evaluated method): Multi-scale, multi-orientation Log-Gabor transfer functions:
  $$G(\omega, \theta) = \exp\left(-\frac{(\ln(\omega/\omega_0))^2}{2(\ln(\kappa/\omega_0))^2}\right) \exp\left(-\frac{(\theta - \theta_j)^2}{2\sigma_\theta^2}\right)$$
- Evaluates Maximum Moment of Phase Congruency Covariance (MIMPC) structural maps to test resilience under solar azimuth and illumination variations.

### 2.3 Stage 3: Matching & Match Filtering
- Nearest-neighbor descriptor matching with Lowe's ratio test ($0.75-0.80$) and bidirectional cross-check consistency to eliminate ambiguous candidate matches.

### 2.4 Stage 4: Geometric Verification & Inlier / Outlier Separation
- Robust geometric estimation using RANSAC / USAC (MAGSAC++ evaluated where appropriate) to verify geometric consistency.
- Separates candidate correspondences strictly into verified inliers and discarded outliers.

### 2.5 Stage 5: Uniform Distribution of Reliable Inliers
- Quad-Tree spatial binning selects verified inliers across image quadrants, preventing point clumping on high-contrast crater rims and optimizing the Keypoint Gini Coefficient ($G_k$).
- Never synthesizes artificial points; only selects among geometrically verified inliers.

### 2.6 Stage 6: Transformation Model Selection & Estimation
- Selects the optimal transformation model (Translation, Similarity, Affine, or Projective Homography) based on physical viewing geometry and residual error.
- Estimates transformation parameters via robust least-squares.

### 2.7 Stage 7: Sub-Pixel Surface Refinement
- Performs 2D continuous parabolic surface fitting ($\mathbf{\delta} = - \mathbf{H}_C^{-1} \nabla C$) on the local correlation neighborhood around each tie-point, targeting fractional-pixel localization accuracy.

### 2.8 Stage 8: Output Generation & Quantitative Evaluation
- Produces registered source image, alpha overlays, checkerboard composites, match point plots, and quantitative metric reports (RMSE, Inlier Count, Inlier Ratio, Sub-pixel Error, Gini $G_k$, Latency).
- All reported metrics are strictly derived from executed experimental runs; unrun conditions are reported as `N/A / Not Yet Evaluated`.
- Distinguishes authentic Chandrayaan-2 flight data from synthetic benchmark datasets.
