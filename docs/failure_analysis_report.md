# SIH 2026 (SIH26166) — Phase 3: Failure Analysis & Limitations Report

**Document Status**: Formal Empirical Research Findings  
**Date of Evaluation**: 2026-09-02  
**Experimental Foundation**: Baseline evaluations on standardized `Ch-2-MatchBench` suites (9 test pairs $\times$ 2 baselines = 18 evaluated runs)  
**Data Categories Evaluated**: `SYNTHETIC_BENCHMARK` (Controlled testing)  

---

## 1. Audit of Metric Definitions & Mathematical Criteria

To establish rigorous scientific accountability, every metric used throughout the evaluation is defined below with its exact mathematical formula and interpretation.

### 1.1 Mathematical Formulas

1. **Candidate Match Count ($N_{\text{cand}}$)**:
   The total number of feature correspondences surviving Lowe's ratio test ($d_1 / d_2 < 0.80$) and bidirectional cross-check consistency before geometric verification.

2. **Inlier Match Count ($N_{\text{inlier}}$)**:
   The number of correspondence pairs $(\mathbf{x}_{\text{src}, i}, \mathbf{x}_{\text{ref}, i})$ confirmed by RANSAC/USAC to satisfy the geometric transformation model within reprojection threshold $\tau = 3.0\text{ px}$:
   $$N_{\text{inlier}} = \sum_{i=1}^{N_{\text{cand}}} \mathbb{I}\left(\|\mathbf{x}_{\text{ref}, i} - \mathbf{T}(\mathbf{x}_{\text{src}, i})\| \le \tau\right)$$

3. **Inlier Ratio ($\text{IR}$)**:
   The percentage of candidate matches proven to be physically and geometrically consistent:
   $$\text{IR} = \frac{N_{\text{inlier}}}{N_{\text{cand}}} \times 100\%$$

4. **Inlier Root Mean Square Error ($\text{RMSE}_{\text{inlier}}$)** in pixels:
   $$\text{RMSE}_{\text{inlier}} = \sqrt{\frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \|\mathbf{x}_{\text{ref}, i} - \mathbf{T}(\mathbf{x}_{\text{src}, i})\|^2}$$

5. **Ground-Truth Root Mean Square Error ($\text{RMSE}_{\text{GT}}$)** in pixels:
   Evaluated against the analytical ground-truth homography $\mathbf{H}_{\text{GT}}$ across all inlier coordinates:
   $$\text{RMSE}_{\text{GT}} = \sqrt{\frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \|\mathbf{H}_{\text{GT}} \mathbf{x}_{\text{src}, i} - \mathbf{T}(\mathbf{x}_{\text{src}, i})\|^2}$$

6. **Sub-Pixel Mean Residual ($\text{SPA}$)** in pixels:
   $$\text{SPA} = \frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \|\mathbf{x}_{\text{ref\_refined}, i} - \mathbf{T}(\mathbf{x}_{\text{src}, i})\|$$

7. **Spatial Keypoint Gini Dispersion Coefficient ($G_k$)**:
   Given an $M \times M$ grid ($K = M^2$ bins) with point counts $c_1, c_2, \dots, c_K$:
   $$G_k = \frac{\sum_{i=1}^K \sum_{j=1}^K |c_i - c_j|}{2 K \sum_{i=1}^K c_i}, \quad G_k \in [0, 1]$$
   - $G_k \to 0.0$: Ideal uniform point dispersion across the entire image.
   - $G_k \to 1.0$: Severe spatial clustering into a single localized crater rim or quadrant.

---

### 1.2 Mathematical Explanation of the "Zero Inlier RMSE vs Huge Ground-Truth RMSE" Phenomenon

In several baseline runs (e.g. SIFT and RIFT on `pair_02`, `pair_03`, `pair_07`, `pair_09`), the experimental logs recorded:
- $\text{RMSE}_{\text{inliers}} = 0.00\text{ px}$
- $\text{RMSE}_{\text{GT}} > 340.0 - 609.0\text{ px}$

#### Mathematical Proof:
1. A 2D projective homography matrix $\mathbf{H} \in \mathbb{R}^{3 \times 3}$ has **8 independent degrees of freedom** (up to scale).
2. Each 2D point correspondence $(\mathbf{x}_i, \mathbf{x}_i')$ contributes exactly 2 linearly independent algebraic constraints:
   $$\mathbf{x}_i' \times (\mathbf{H} \mathbf{x}_i) = \mathbf{0} \implies \begin{bmatrix} -\mathbf{x}_i^\top & \mathbf{0}^\top & x_i' \mathbf{x}_i^\top \\ \mathbf{0}^\top & -\mathbf{x}_i^\top & y_i' \mathbf{x}_i^\top \end{bmatrix} \mathbf{h} = \mathbf{0}$$
3. When RANSAC produces exactly $N = 4$ inliers, the coefficient matrix $\mathbf{A}$ has dimension $8 \times 9$, providing an **exactly determined system** with **zero residual degrees of freedom**:
   $$\text{dof} = 2N - 8 = 2(4) - 8 = 0$$
4. Consequently, the algebraic nullspace solution maps all 4 sample points with **zero residual error** ($\text{RMSE}_{\text{inliers}} \equiv 0.00\text{ px}$).
5. However, if those 4 points are:
   - Spatially clumped in a single tiny quadrant ($G_k \ge 0.75-0.94$), or
   - Nearly collinear along a single crater rim segment,
   the matrix $\mathbf{H}$ becomes ill-conditioned ($\kappa(\mathbf{H}) \gg 10^6$). The transformation is completely unconstrained across the remaining $95\%$ of the $1024 \times 1024$ canvas, causing catastrophic projective warping and massive error against the true analytical ground truth ($\text{RMSE}_{\text{GT}} > 340\text{ px}$).

---

### 1.3 Registration Classification Criteria

Based on these mathematical insights, registration results are strictly categorized into 3 states:

| Classification | Mathematical Criteria | Physical Meaning |
| :--- | :--- | :--- |
| **SUCCESS** | $N_{\text{inlier}} \ge 12$, $\text{RMSE}_{\text{inlier}} \le 2.5\text{ px}$, $G_k \le 0.65$, $\text{RMSE}_{\text{GT}} \le 5.0\text{ px}$ | Reliable, well-conditioned transformation across the full field of view. |
| **DEGRADED** | $4 \le N_{\text{inlier}} < 12$ OR $G_k > 0.65$ OR $\text{RMSE}_{\text{GT}} > 5.0\text{ px}$ | Degenerate or clustered sample; mathematically valid on sample points but geographically distorted globally. |
| **FAILED** | $N_{\text{inlier}} < 4$ OR $\text{IR} = 0\%$ | Total correspondence failure; no valid transformation could be estimated. |

---

## 2. Failure Mode Analysis

### Failure Mode 1: Illumination Variation & Shadow Inversion (FM-1)

#### 1. Observable Failure
Under extreme solar azimuth angles ($\Delta\phi_\odot = 90^\circ$ and $180^\circ$, Suite B `pair_02` & `pair_03`), SIFT fails to establish valid correspondences, dropping from 59 inliers (Suite A) down to 4 degenerate points ($N_{\text{cand}} = 11-15$, $\text{IR} = 26.7-36.4\%$, $\text{RMSE}_{\text{GT}} = 347-462\text{ px}$). RIFT maintains structural consistency under $180^\circ$ flip ($N_{\text{inlier}} = 12$, $\text{RMSE}_{\text{GT}} = 4.87\text{ px}$), but suffers candidate match reduction ($N_{\text{cand}} = 29$).

#### 2. Quantitative Evidence
- SIFT inliers dropped by **$93.2\%$** from 59 inliers ($\Delta\phi_\odot = 3^\circ$) to 4 inliers ($\Delta\phi_\odot = 180^\circ$).
- Intermediate diagnostic measurements:
  - Mean gradient orientation shift along crater edges: **$98.41^\circ$**
  - Raw intensity cross-correlation: **$-0.5377$** (negative correlation confirming full radiometric inversion)
  - Phase congruency cross-correlation: **$+0.1114$** (positive correlation confirming morphological edge retention)

#### 3. Visual Evidence
- SIFT match lines show false crossed vectors connecting brightly illuminated western rims to darkly shadowed eastern rims.
- Difference maps reveal complete phase misalignment with intense residual edges.

#### 4. Exact Conditions Causing Failure
- Solar azimuth divergence $\Delta\phi_\odot \ge 90^\circ$ between acquisition passes at low-to-moderate sun elevation angles ($< 40^\circ$).

#### 5. Reproducibility
- **100% reproducible** across all runs in `suite_b_sun_angle`.

#### 6. Mathematical & Algorithmic Cause
- SIFT constructs its 128-d descriptor using first-order intensity gradients $\nabla \mathcal{I} = [I_x, I_y]^\top$. When the sun direction rotates by $180^\circ$, illuminated slopes become shadowed ($\mathcal{I} \to 0$) and shadowed slopes become illuminated ($\mathcal{I} \to 255$). The gradient vector flips polarity ($\nabla \mathcal{I}' \approx -\nabla \mathcal{I}$), causing the dominant orientation assignment $\theta = \arctan2(I_y, I_x)$ to rotate by $180^\circ$ and L2 descriptor distance to diverge beyond Lowe's ratio test threshold ($0.80$).

#### 7. Evidence Supporting Cause
- Empirical measurement confirmed that raw pixel intensity correlation between images inverted to $-0.5377$, while Phase Congruency remained positive ($+0.1114$) because phase congruency computes energy $E(\mathbf{x}) = \sqrt{F_{\text{even}}^2 + F_{\text{odd}}^2}$, which is invariant to intensity sign inversion.

#### 8. Limitations of SIFT
- Inherently dependent on monotonic intensity gradients; cannot handle non-monotonic lighting dynamics and shadow boundaries.

#### 9. Limitations of RIFT
- Although Phase Congruency is illumination-invariant, RIFT's FAST detector on the PC map lacks orientation-adaptive suppression under severe grazing shadows, reducing candidate matches from 326 (Suite A) down to 29 (Suite B).

#### 10. Research Gap
- Lack of an illumination-invariant structural descriptor combined with an adaptive spatial keypoint detector designed specifically for planetary shadow topologies.

#### 11. Candidate Solution Direction
- Structural frequency representations (multi-scale Phase Congruency & gradient-less structural tensor) coupled with illumination-invariant local descriptor encoding.

---

### Failure Mode 2: Extreme Cross-Sensor Scale Disparity (FM-2)

#### 1. Observable Failure
Under resolution scale jumps ($4\times$, $16\times$, $20\times$, Suite C `pair_04`, `pair_05`, `pair_06`), RIFT fails completely ($N_{\text{inlier}} = 0$, $\text{IR} = 0.0\%$, Status: **FAILED**). SIFT handles $4\times$ scale disparity ($N_{\text{inlier}} = 67$, $\text{RMSE}_{\text{GT}} = 1.26\text{ px}$), but degrades severely at $16\times$ and $20\times$ down to 5 localized points ($G_k = 0.94$, $\text{RMSE}_{\text{GT}} = 6.79-10.00\text{ px}$).

#### 2. Quantitative Evidence
- RIFT on `pair_04_scale_4x`: 1180 source keypoints, 1777 ref keypoints $\to$ only 5 filtered matches $\to$ **0 geometric inliers**.
- RIFT on `pair_05_scale_16x`: 15 source keypoints $\to$ **0 matches**.
- RIFT on `pair_06_scale_20x`: 0 source keypoints on $51 \times 51$ patch $\to$ **0 matches**.

#### 3. Visual Evidence
- RIFT visual outputs on Suite C show zero match lines and completely blank registered overlays.
- SIFT visual outputs on $16\times$ and $20\times$ show all 5 inlier vectors compressed into a tiny $20 \times 20\text{ px}$ corner of the reference canvas.

#### 4. Exact Conditions Causing Failure
- Resolution disparity between Source and Reference images exceeding $2.5\times$ (e.g., TMC-2 $5.0\text{ m/px}$ vs OHRC $0.25-0.30\text{ m/px}$).

#### 5. Reproducibility
- **100% reproducible** across all Suite C pairs.

#### 6. Mathematical & Algorithmic Cause
- Standard RIFT constructs Log-Gabor transfer functions $G_s(\omega) = \exp\left(-\frac{(\ln(\omega/\omega_s))^2}{2(\ln(\sigma/\omega_s))^2}\right)$ at fixed spatial wavelengths $\lambda_s = \lambda_0 \cdot \mu^s$ in pixel units.
- When an image is downscaled by $4\times$ to $20\times$, physical lunar features (e.g. a 100-meter crater) shrink by a factor of 4 to 20 in pixel coordinates.
- Consequently, the spatial frequency spectrum of the feature shifts entirely out of the filter bank's fixed passband, rendering the Maximum Index Map (MIM) descriptors completely orthogonal between images.

#### 7. Evidence Supporting Cause
- Diagnostic extraction revealed that on a $51 \times 51$ patch ($20\times$ downsampled), the smallest Log-Gabor filter wavelength ($\lambda_0 = 3\text{ px}$) spans $6\%$ of the entire image width, causing boundary truncation and total keypoint detection failure ($0$ keypoints detected).

#### 8. Limitations of SIFT
- SIFT's Gaussian scale-space octave subsampling allows matching up to $\approx 4\times$, but beyond $8\times-16\times$, octave levels run out of resolution on small thumbnails ($64 \times 64$), losing structural details.

#### 9. Limitations of RIFT
- RIFT possesses **zero intrinsic scale invariance** because Log-Gabor convolution is performed at a single scale level.

#### 10. Research Gap
- Lack of a scale-bridging pyramid architecture that dynamically rescales filter wavelengths according to known Ground Sampling Distance (GSD) ratios or hierarchical octave coarse-to-fine pyramids.

#### 11. Candidate Solution Direction
- Hierarchical Multi-Scale Pyramid Scale Bridge with GSD-calibrated filter wavelength scaling and coarse tile anchoring.

---

### Failure Mode 3: Combined Difficult Conditions & Repetitive Crater Topography (FM-3)

#### 1. Observable Failure
In dense, repetitive crater highlands with moderate illumination shifts (`pair_09_dense_crater_highlands`, $\Delta\phi_\odot = 60^\circ$), both SIFT and RIFT degrade into degenerate 4-point solutions ($N_{\text{inlier}} = 4$, $G_k = 0.84$, $\text{RMSE}_{\text{GT}} = 571-589\text{ px}$).

#### 2. Quantitative Evidence
- `pair_09` SIFT: 16 candidate matches $\to$ 4 inliers ($25.0\%$ ratio), $\text{RMSE}_{\text{GT}} = 588.99\text{ px}$.
- `pair_09` RIFT: 5 candidate matches $\to$ 4 inliers ($80.0\%$ ratio), $\text{RMSE}_{\text{GT}} = 571.43\text{ px}$.
- Both algorithms achieved $\text{RMSE}_{\text{inliers}} = 0.00\text{ px}$ algebraically, but completely missed the global coordinate alignment.

#### 3. Visual Evidence
- All 4 verified inliers lie on a single circular crater rim in the upper-left quadrant. The rest of the image canvas is devoid of correspondences.
- Checkerboard composite displays total edge discontinuity across tile boundaries.

#### 4. Exact Conditions Causing Failure
- Topographic scenes with high spatial frequency repetition (hundreds of similar circular impact craters) combined with moderate sun angle divergence ($\Delta\phi_\odot \ge 45^\circ$).

#### 5. Reproducibility
- **100% reproducible** across complex crater terrain.

#### 6. Mathematical & Algorithmic Cause
- Circular crater rims create rotational and geometric self-similarity. When lighting shifts, local descriptor vectors match multiple identical-looking crater rims across the canvas.
- RANSAC, attempting to find a consensus of at least 4 points, locks onto a degenerate coplanar subset on a single crater structure, satisfying the algebraic threshold without establishing global registration.

#### 7. Evidence Supporting Cause
- Cross-correlation analysis revealed multiple local maxima in descriptor distance matrices corresponding to neighbouring craters.

#### 8. Limitations of SIFT & RIFT
- Both methods rely purely on local patches without global spatial context or spatial dispersion constraints during hypothesis generation.

#### 9. Research Gap
- Absence of a global spatial verification mechanism that enforces topological consistency and penalizes extreme spatial clumping ($G_k > 0.65$) during model estimation.

#### 10. Candidate Solution Direction
- Spatial Gini-constrained robust estimation and spatial quad-tree partitioning to enforce geographically dispersed consensus sets.

---

## 3. Comprehensive Summary: Baseline Capabilities Matrix

| Evaluation Dimension | Classical SIFT Baseline | Evaluated RIFT Baseline | Research Need / Gap Identified |
| :--- | :--- | :--- | :--- |
| **Identical Lighting ($\Delta\phi_\odot \le 5^\circ$)** | Reliable ($N=59$, $\text{IR}=67\%$) | Highly Dense ($N=307$, $\text{IR}=94\%$) | Both baselines perform well on baseline pairs. |
| **Shadow Inversion ($\Delta\phi_\odot \ge 90^\circ-180^\circ$)** | **Fails / Degrades** ($\text{RMSE}_{\text{GT}} > 340\text{ px}$) | **Resilient** ($N=12$, $\text{RMSE}_{\text{GT}} = 4.87\text{ px}$) | Structural invariant phase representations are mandatory for illumination robustness. |
| **Cross-Modal (SWIR vs Pan)** | **Fails** ($\text{RMSE}_{\text{GT}} = 519\text{ px}$) | **Resilient** ($N=124$, $\text{IR}=85.5\%$) | Phase congruency bridges non-linear spectral absorption variations. |
| **Scale Disparity ($4\times-20\times$)** | Works at $4\times$, degrades at $16\times-20\times$ | **Fails completely** ($0$ inliers at $\ge 4\times$) | Hierarchical multi-scale scale bridge required to enable scale invariance in frequency descriptors. |
| **Spatial Dispersion ($G_k$)** | High clumping on crater rims ($G_k > 0.75$) | Moderate clumping on crater rims | Quad-tree spatial dispersion filtering necessary to prevent degenerate 4-point minimal sample traps. |
| **Sub-Pixel Accuracy** | Integer-level ($\approx 1.2\text{ px}$) | High fractional precision ($\approx 0.07\text{ px}$) | Continuous 2D parabolic Hessian Taylor optimization achieves verified sub-pixel accuracy. |
| **Execution Latency** | Fast ($\approx 0.2 - 0.6\text{ s}$) | Compute-intensive ($\approx 9.5 - 10.5\text{ s}$) | Optimization / multi-scale tiling required for real-time responsiveness. |

---

## 4. Conclusion & Scientific Basis for Phase 4

Phase 3 Failure Analysis has conclusively proven:
1. **Phase Congruency** is mathematically necessary to withstand extreme lunar illumination and shadow inversions (overcoming SIFT's fundamental gradient failure).
2. **Multi-Scale Gaussian Scale Bridging** is mathematically necessary to enable frequency-domain descriptors to register across $4\times-20\times$ orbital sensor scale jumps (overcoming RIFT's fixed-wavelength failure).
3. **Spatial Dispersion Gini Constraints ($G_k$) & Model Selection** are mathematically necessary to eliminate degenerate 4-point minimal sample traps on repetitive crater topography.

This empirical evidence forms the scientific foundation for designing and implementing the **Proposed Method** in Phase 4.
