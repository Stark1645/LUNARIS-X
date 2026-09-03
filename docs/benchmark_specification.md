# Ch-2-MatchBench: Benchmark Specification & Design

## 1. Overview & Purpose
`Ch-2-MatchBench` is a standardized benchmark suite created to scientifically evaluate lunar image correspondence and registration algorithms under controlled, reproducible conditions representing the core challenges of ISRO SIH26166.

---

## 2. Test Suites Specification

```
+---------------------------------------------------------------------------------------------------+
| SUITE ID | SUITE NAME            | CHALLENGE / CONDITIONS                | TARGET SENSORS SIMULATED|
+----------+-----------------------+---------------------------------------+-------------------------+
| Suite A  | Intra-Sensor Baseline | Identical sun angle, 1:1 scale, 5° rot| TMC2-TMC2 (5m / 5m)     |
| Suite B  | Sun-Angle Disparity   | 90° & 180° solar azimuth shifts       | OHRC-OHRC (0.3m / 0.3m) |
| Suite C  | Cross-Scale Disparity | 1:4, 1:16, 1:20 resolution scale jumps| TMC2-OHRC (5m / 0.25m)  |
| Suite D  | Cross-Modal SWIR      | Non-linear mineral absorption bands   | IIRS-TMC2 (80m / 5m)    |
| Suite E  | Difficult Terrain     | Low-texture maria & dense highlands   | TMC2 / OHRC             |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Detailed Pair Breakdown

### Suite A: Intra-Sensor Baseline
- **`pair_01_baseline_same_sun`**:
  - Primary Sun Azimuth: $45^\circ$, Secondary: $48^\circ$ ($\Delta\phi = 3^\circ$).
  - Incidence Angle: $40^\circ$.
  - Transform: $\text{Rotation} = 5.0^\circ$, $\text{Translation} = (15.0, -10.0)\text{ px}$.
  - Purpose: Evaluates performance of classical and illumination-robust baseline algorithms (SIFT, AKAZE, RIFT) under benign conditions with minimal illumination delta.

### Suite B: Sun-Angle Invariance
- **`pair_02_sun_angle_90deg`**:
  - Primary Sun Azimuth: $45^\circ$, Secondary: $135^\circ$ ($\Delta\phi = 90^\circ$).
  - Incidence Angle: $60^\circ$ (long shadows).
  - Purpose: Tests resilience to orthogonal illumination where rim shadows shift by $90^\circ$.
- **`pair_03_sun_angle_180deg`**:
  - Primary Sun Azimuth: $30^\circ$, Secondary: $210^\circ$ ($\Delta\phi = 180^\circ$).
  - Incidence Angle: $65^\circ$.
  - Purpose: Tests extreme shadow reversal (East vs West sun) where classical gradient matchers catastrophically fail.

### Suite C: Extreme Scale Disparity
- **`pair_04_scale_4x`**: Scale ratio $4.0\times$ (intermediate pyramid level).
- **`pair_05_scale_16x_tmc2_ohrc`**: Scale ratio $16.0\times$ (TMC-2 $5\text{ m/px}$ to OHRC $0.31\text{ m/px}$).
- **`pair_06_scale_20x_tmc2_ohrc`**: Scale ratio $20.0\times$ (TMC-2 $5\text{ m/px}$ to OHRC $0.25\text{ m/px}$).
- Purpose: Tests whether multi-scale pyramid bridges can resolve features when fine craters disappear in coarse views.

### Suite D: Cross-Modal Registration
- **`pair_07_cross_modal_swir_pan`**:
  - Simulates IIRS SWIR mineral absorption against Panchromatic optical imagery.
  - Purpose: Tests non-linear radiometric transformation invariance (Phase Congruency vs Gradient).

### Suite E: Difficult Lunar Terrain
- **`pair_08_low_texture_maria`**: Smooth volcanic lunar maria with sparse features ($\sigma_{\text{img}} \approx 4.3$).
- **`pair_09_dense_crater_highlands`**: Overlapping multi-generational crater field with intense self-shadowing.

---

## 4. Ground Truth Integrity
Each pair contains `ground_truth.json` specifying the exact $3\times 3$ Homography matrix $\mathbf{H}_{\text{gt}}$ that satisfies:
$$\begin{bmatrix} x_2 \\ y_2 \\ 1 \end{bmatrix} \sim \mathbf{H}_{\text{gt}} \begin{bmatrix} x_1 \\ y_1 \\ 1 \end{bmatrix}$$
This allows calculating exact pixel reprojection error: $\text{Error} = \|\mathbf{x}_2 - \mathbf{H}_{\text{gt}}\mathbf{x}_1\|$.
