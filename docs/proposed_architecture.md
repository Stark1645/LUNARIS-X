# Proposed Architecture Specification: Adaptive Multi-Scale Structural Registration (AMSR)

**Status**: Verified System Architecture  
**Modules Location**: `src/proposed/`  
**API Endpoint**: `POST /api/v1/register` (Algorithm: `Proposed_Method` / `AMSR`)  

---

## 1. System Block Diagram & Data Flow

```
                                      +------------------------------------+
                                      |       SOURCE / MOVING IMAGE        |
                                      | (Chandrayaan-2 Acquired Optical)   |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |     RADIOMETRIC NORMALIZATION      |
                                      | • Dynamic 2%-98% Percentile Clip   |
                                      | • Shadow & Nodata Masking          |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |    CONDITION & QUALITY ANALYZER    |
                                      | • Scale Disparity Estimation (S)   |
                                      | • Photometric Correlation (r_I)    |
                                      | • Gradient Correlation (r_grad)    |
                                      +-----------------+------------------+
                                                        |
                        +-------------------------------+-------------------------------+
                        |                                                               |
              [Scale Disparate S > 1.5]                                     [Scale 1:1 / Illum Inverted]
                        |                                                               |
                        v                                                               v
         +-----------------------------+                                 +-----------------------------+
         |  HIERARCHICAL SCALE BRIDGE  |                                 | STRUCTURAL PHASE DETECTOR   |
         | • Gaussian Scale Pyramid    |                                 | • Log-Gabor Phase Congruency|
         | • Coarse Octave Matching    |                                 | • Shadow Edge Suppression   |
         | • Coordinate Up-Propagation |                                 | • MIM Orientation Histograms|
         +--------------+--------------+                                 +--------------+--------------+
                        |                                                               |
                        +-------------------------------+-------------------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |          FEATURE MATCHING          |
                                      | • Nearest-Neighbor L2 Norm         |
                                      | • Lowe's Ratio Test (0.80)         |
                                      | • Mutual Cross-Check Consistency   |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |    SPATIAL COVERAGE-AWARE RANSAC   |
                                      | • Spatial Gini Check on Samples    |
                                      | • Strict Inlier / Outlier Split    |
                                      +-----------------+------------------+
                                                        |
                                                        v (Verified Inliers)
                                      +------------------------------------+
                                      |     UNIFORM SPATIAL DISPERSION     |
                                      | • 4x4 Grid Quad-Tree Binning       |
                                      | • Max 25 Points / Spatial Bin      |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |    DYNAMIC MODEL SELECTION         |
                                      | • If N < 8 or G_k > 0.65 -> AFFINE |
                                      | • If N >= 8 & G_k <= 0.65 -> HOMOG |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |    2D PARABOLIC HESSIAN SUBPIXEL   |
                                      | • delta* = - H_C^-1 * grad(C)      |
                                      | • Continuous Taylor Refinement     |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |        BACKWARD IMAGE WARPER       |
                                      | • High-Precision Warped Source     |
                                      | • Alpha Blended Overlay            |
                                      | • 8x8 Checkerboard Composite       |
                                      | • Absolute Difference Map          |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |     SCIENTIFIC QUALITY METRICS     |
                                      | • RMSE, Inliers, IR, SPA, G_k      |
                                      +------------------------------------+
```

---

## 2. Component Class Diagram

```
src/proposed/
├── condition_analyzer.py      -> ImagePairConditionAnalyzer, ImagePairCharacteristics
├── structural_detector.py     -> StructuralFeatureDetector (LogGaborFilterBank + ShadowSuppression)
├── scale_pyramid_matcher.py   -> HierarchicalScalePyramidMatcher (Gaussian Octaves + Coordinate Projection)
├── spatial_ransac.py          -> SpatialCoverageAwareVerifier (Gini Validation + Inlier/Outlier Separation)
├── model_selector.py          -> DynamicModelSelector (Affine vs Homography vs Similarity)
├── proposed_pipeline.py       -> ProposedRegistrationPipeline (AMSR Master Pipeline Orchestrator)
└── __init__.py
```
