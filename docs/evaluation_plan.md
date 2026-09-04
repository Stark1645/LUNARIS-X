# LUNARIS-X (SIH26166): Scientific Evaluation Plan & Benchmark Metrics

## 1. Quantitative Evaluation Protocol

To prevent subjective bias, all evaluation must be grounded in mathematical metrics computed across the standardized **Ch-2-MatchBench** dataset.

### 1.1 Metrics Defined:

1. **Inlier Count ($N_{\text{inlier}}$)**: Number of geometrically verified correspondence points.
2. **Inlier Ratio ($\text{IR}$)**:
   $$\text{IR} = \frac{N_{\text{inlier}}}{N_{\text{total}}} \times 100\%$$
3. **Root Mean Square Error (RMSE)** in pixels:
   $$\text{RMSE} = \sqrt{\frac{1}{N_{\text{inlier}}} \sum_{i=1}^{N_{\text{inlier}}} \|\mathbf{x}_i' - \mathbf{H} \mathbf{x}_i\|^2}$$
4. **Sub-Pixel Accuracy Rate (SPA@0.5px)**: Percentage of inliers with reprojection residual $< 0.5\text{ px}$.
5. **Spatial Uniformity / Gini Coefficient ($G_k$)**:
   Given an $M \times M$ grid of spatial bins with point counts $c_1, c_2, \dots, c_K$:
   $$G_k = \frac{\sum_{i=1}^K \sum_{j=1}^K |c_i - c_j|}{2 K \sum_{i=1}^K c_i}$$
   Where $G_k \to 0$ represents perfectly uniform point dispersion, and $G_k \to 1$ represents severe clumping.
6. **Registration Success Rate ($\text{SR}$)**: Percentage of pairs registered with $\text{RMSE} \le 1.5\text{ px}$ and $N_{\text{inlier}} \ge 20$.
7. **Processing Latency**: Milliseconds per megapixel.

---

## 2. Controlled Test Suites

| Suite | Description | Primary Challenge Tested | Target Baseline Failure |
| :--- | :--- | :--- | :--- |
| **Suite A** | Intra-sensor, identical illumination | Baseline validity check | None (all should pass) |
| **Suite B** | Sun azimuth shift $\Delta\phi_\odot > 90^\circ$ | Shadow inversion & illumination dynamics | SIFT / AKAZE / LoFTR fail |
| **Suite C** | Cross-scale TMC-2 ($5\text{m}$) vs OHRC ($0.3\text{m}$) | $16\times - 20\times$ scale disparity | SIFT / RIFT2 fail |
| **Suite D** | Cross-modal IIRS SWIR vs Panchromatic | Non-linear spectral absorption | SIFT / AKAZE fail |
| **Suite E** | Low-texture flat lunar maria | Feature scarcity & false matches | SIFT / AKAZE / ORB fail |

---

## 3. Ablation Study Matrix

To evaluate which components contribute to registration performance under extreme conditions, ablation configurations will be executed:
- **Ablation 1 (No Scale Bridge)**: Disables hierarchical scale pyramid; feeds raw downsampled image directly into matcher.
- **Ablation 2 (No Phase Congruency)**: Replaces structural phase congruency with standard gradients.
- **Ablation 3 (No Spatial Dispersion Filter)**: Uses vanilla RANSAC without spatial uniformity constraints.
- **Ablation 4 (No Sub-Pixel Parabolic Refinement)**: Disables Taylor expansion; keeps integer grid coordinates.
