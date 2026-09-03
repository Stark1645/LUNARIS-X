# SIH 2026 (SIH26166) — Final Comprehensive Benchmark Results

**Evaluation Dataset**: Ch-2-MatchBench (9 Synthetic Benchmark Pairs across Suites A through E)  
**Evaluated Algorithms**: SIFT Baseline, RIFT Baseline, Adaptive Multi-Scale Structural Registration (AMSR) Engine  
**Ablation Configurations**: No Scale Pyramid, No Shadow Suppression, No Dynamic Model, No Sub-Pixel Refinement  

---

## 1. Overall Performance Comparison Matrix

| Suite | Pair Identifier | Evaluation Condition | Method | Inliers ($N$) | Candidate | Inlier Ratio (%) | Inlier RMSE (px) | GT RMSE (px) | Sub-Pixel (px) | Gini ($G_k$) | Latency (ms) | Classification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Suite A** | `pair_01_baseline_same_sun` | Baseline Same Sun ($5\text{m} \leftrightarrow 5\text{m}$) | SIFT | 59 | 75 | 78.7% | 1.47 | 1.82 | 0.450 | 0.41 | 811 | `SUCCESS` |
| | | | RIFT | 59 | 75 | 78.7% | 1.47 | 1.82 | 0.450 | 0.41 | 535 | `SUCCESS` |
| | | | **AMSR (Proposed)** | **382** | **450** | **84.9%** | **0.23** | **0.31** | **0.180** | **0.32** | 10,268 | `SUCCESS` |
| **Suite B** | `pair_02_sun_angle_90deg` | $90^\circ$ Solar Azimuth Shift | SIFT | 4 | 28 | 14.3% | 0.00 | 185.20 | 2.500 | 0.75 | 449 | `DEGRADED` |
| | | | RIFT | 4 | 28 | 14.3% | 0.00 | 185.20 | 2.500 | 0.75 | 448 | `DEGRADED` |
| | | | **AMSR (Proposed)** | 4 | 32 | 12.5% | 229.58 | 229.58 | 2.450 | 0.75 | 9,977 | `DEGRADED` |
| **Suite B** | `pair_03_sun_angle_180deg`| $180^\circ$ Solar Azimuth Inversion | SIFT | 4 | 30 | 13.3% | 0.00 | 210.45 | 3.100 | 0.75 | 488 | `DEGRADED` |
| | | | RIFT | 4 | 30 | 13.3% | 0.00 | 210.45 | 3.100 | 0.75 | 470 | `DEGRADED` |
| | | | **AMSR (Proposed)** | **12** | **36** | **33.3%** | **1.77** | **2.34** | **1.655** | **0.61** | 9,678 | `SUCCESS` |
| **Suite C** | `pair_04_scale_4x` | $4\times$ Scale Disparity ($5\text{m} \leftrightarrow 1.25\text{m}$) | SIFT | 67 | 80 | 83.8% | 1.31 | 0.52 | 0.380 | 0.94 | 255 | `DEGRADED` |
| | | | RIFT | 67 | 80 | 83.8% | 1.31 | 0.52 | 0.380 | 0.94 | 235 | `DEGRADED` |
| | | | **AMSR (Proposed)** | **87** | **95** | **91.6%** | **1.27** | **0.41** | **1.085** | **0.94** | 152 | `DEGRADED`* |
| **Suite C** | `pair_05_scale_16x_tmc2_ohrc`| $16\times$ Scale Disparity ($5\text{m} \leftrightarrow 0.31\text{m}$) | SIFT | 5 | 15 | 33.3% | 0.00 | 312.40 | 4.200 | 0.94 | 224 | `DEGRADED` |
| | | | RIFT | 5 | 15 | 33.3% | 0.00 | 312.40 | 4.200 | 0.94 | 219 | `DEGRADED` |
| | | | **AMSR (Proposed)** | **7** | **15** | **46.7%** | **7.25** | **8.12** | **0.980** | **0.94** | 90 | `DEGRADED` |
| **Suite C** | `pair_06_scale_20x_tmc2_ohrc`| $20\times$ Scale Disparity ($5\text{m} \leftrightarrow 0.25\text{m}$) | SIFT | 5 | 18 | 27.8% | 0.00 | 450.10 | 5.100 | 0.94 | 276 | `DEGRADED` |
| | | | RIFT | 5 | 18 | 27.8% | 0.00 | 450.10 | 5.100 | 0.94 | 271 | `DEGRADED` |
| | | | **AMSR (Proposed)** | **7** | **13** | **53.8%** | **1.05** | **2.85** | **0.962** | **0.94** | 187 | `DEGRADED` |
| **Suite D** | `pair_07_cross_modal_swir_pan`| SWIR vs Panchromatic Transfer | SIFT | 4 | 25 | 16.0% | 0.00 | 175.60 | 2.800 | 0.91 | 412 | `DEGRADED` |
| | | | RIFT | 4 | 25 | 16.0% | 0.00 | 175.60 | 2.800 | 0.91 | 408 | `DEGRADED` |
| | | | **AMSR (Proposed)** | **166** | **210** | **79.0%** | **1.56** | **1.95** | **0.320** | **0.43** | 10,279 | `SUCCESS` |
| **Suite E** | `pair_08_low_texture_maria` | Basaltic Maria Low-Texture | SIFT | 400 | 450 | 88.9% | 0.45 | 0.65 | 0.210 | 0.00 | 644 | `SUCCESS` |
| | | | RIFT | 400 | 450 | 88.9% | 0.45 | 0.65 | 0.210 | 0.00 | 624 | `SUCCESS` |
| | | | **AMSR (Proposed)** | **400** | **450** | **88.9%** | **0.22** | **0.35** | **0.150** | **0.00** | 9,814 | `SUCCESS` |
| **Suite E** | `pair_09_dense_crater_highlands`| High-Density Cratered Highlands | SIFT | 4 | 30 | 13.3% | 0.00 | 145.80 | 3.500 | 0.84 | 506 | `DEGRADED` |
| | | | RIFT | 4 | 30 | 13.3% | 0.00 | 145.80 | 3.500 | 0.84 | 468 | `DEGRADED` |
| | | | **AMSR (Proposed)** | 4 | 30 | 13.3% | 122.81 | 122.81 | 3.200 | 0.84 | 9,713 | `DEGRADED` |

*\*Note on `pair_04`: When verified against ground truth ($\text{RMSE}_{\text{GT}} = 0.41\text{ px}$), it fulfills mathematical alignment success, but is diagnosed as `DEGRADED` in autonomous mode due to localized spatial clustering on the central crater ($G_k = 0.94$).*

---

## 2. Summary of Algorithmic Success Counts

$$\text{AMSR (Proposed Engine): } \mathbf{4\text{ SUCCESS / } 5\text{ DEGRADED / } 0\text{ FAILED}}$$
$$\text{SIFT Baseline: } \mathbf{2\text{ SUCCESS / } 7\text{ DEGRADED / } 0\text{ FAILED}}$$
$$\text{RIFT Baseline: } \mathbf{2\text{ SUCCESS / } 7\text{ DEGRADED / } 0\text{ FAILED}}$$
