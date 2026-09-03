# Phase 4 Experiment Log: Proposed Method & Ablation Study Registry

**Date**: 2026-09-02  
**Dataset Classification**: `SYNTHETIC_BENCHMARK`  
**Execution Environment**: Python 3.13.5 (OpenCV 5.0, NumPy, SciPy)  
**Total Evaluated Runs**: 63 runs (9 benchmark pairs $\times$ 7 configurations)  

---

## 1. Complete Run Log

| Run ID | Pair Name | Configuration Evaluated | Inliers | Candidates | Inlier Ratio | Inlier RMSE (px) | Ground-Truth RMSE (px) | Model Selected | Gini ($G_k$) | Latency (ms) | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P4-01** | `pair_01_baseline_same_sun` | SIFT Baseline | 59 | 88 | 67.0% | 1.47 | 0.68 | HOMOGRAPHY | 0.41 | 578 | SUCCESS |
| **P4-02** | `pair_01_baseline_same_sun` | RIFT Baseline | 307 | 326 | 94.2% | 0.18 | 33.45 | HOMOGRAPHY | 0.32 | 9860 | SUCCESS |
| **P4-03** | `pair_01_baseline_same_sun` | Proposed Full | 382 | 427 | 89.5% | 0.23 | 33.65 | HOMOGRAPHY | 0.32 | 10103 | SUCCESS |
| **P4-04** | `pair_01_baseline_same_sun` | Ablation No Scale Pyramid | 382 | 427 | 89.5% | 0.23 | 33.65 | HOMOGRAPHY | 0.32 | 9896 | SUCCESS |
| **P4-05** | `pair_01_baseline_same_sun` | Ablation No Shadow Suppress | 309 | 430 | 71.9% | 0.25 | 35.96 | HOMOGRAPHY | 0.20 | 9761 | SUCCESS |
| **P4-06** | `pair_01_baseline_same_sun` | Ablation No Dynamic Model | 382 | 427 | 89.5% | 0.23 | 33.65 | HOMOGRAPHY | 0.32 | 9809 | SUCCESS |
| **P4-07** | `pair_01_baseline_same_sun` | Ablation No Subpixel | 382 | 427 | 89.5% | 0.90 | 33.71 | HOMOGRAPHY | 0.32 | 9648 | SUCCESS |
| **P4-08** | `pair_02_sun_angle_90deg` | SIFT Baseline | 4 | 11 | 36.4% | 0.00 | 461.98 | HOMOGRAPHY | 0.75 | 447 | DEGRADED |
| **P4-09** | `pair_02_sun_angle_90deg` | RIFT Baseline | 4 | 4 | 100.0% | 0.00 | 609.12 | HOMOGRAPHY | 0.84 | 9338 | DEGRADED |
| **P4-10** | `pair_02_sun_angle_90deg` | Proposed Full | 4 | 4 | 100.0% | 0.00 | 609.12 | HOMOGRAPHY | 0.84 | 9279 | DEGRADED |
| **P4-11** | `pair_03_sun_angle_180deg` | SIFT Baseline | 4 | 15 | 26.7% | 0.00 | 347.09 | HOMOGRAPHY | 0.75 | 557 | DEGRADED |
| **P4-12** | `pair_03_sun_angle_180deg` | RIFT Baseline | 12 | 29 | 41.4% | 1.51 | 4.87 | HOMOGRAPHY | 0.61 | 9526 | SUCCESS |
| **P4-13** | `pair_03_sun_angle_180deg` | Proposed Full | 12 | 36 | 33.3% | 1.77 | 5.42 | HOMOGRAPHY | 0.61 | 9508 | SUCCESS |
| **P4-14** | `pair_03_sun_angle_180deg` | Ablation No Shadow Suppress | 10 | 33 | 30.3% | 6.67 | 8.76 | AFFINE | 0.71 | 9574 | DEGRADED |
| **P4-15** | `pair_04_scale_4x` | SIFT Baseline | 67 | 72 | 93.1% | 1.31 | 1.26 | HOMOGRAPHY | 0.94 | 391 | SUCCESS |
| **P4-16** | `pair_04_scale_4x` | RIFT Baseline | 0 | 5 | 0.0% | N/A | N/A | HOMOGRAPHY | 1.00 | 5647 | FAILED |
| **P4-17** | `pair_04_scale_4x` | Proposed Full | 87 | 95 | 91.6% | 1.27 | 0.41 | HOMOGRAPHY | 0.94 | 390 | SUCCESS |
| **P4-18** | `pair_04_scale_4x` | Ablation No Scale Pyramid | 5 | 10 | 50.0% | 170.67 | 426.13 | AFFINE | 0.94 | 5509 | DEGRADED |
| **P4-19** | `pair_05_scale_16x_tmc2_ohrc`| SIFT Baseline | 5 | 8 | 62.5% | 0.00 | 6.79 | HOMOGRAPHY | 0.94 | 200 | DEGRADED |
| **P4-20** | `pair_05_scale_16x_tmc2_ohrc`| RIFT Baseline | 0 | 0 | 0.0% | N/A | N/A | HOMOGRAPHY | 1.00 | 4790 | FAILED |
| **P4-21** | `pair_05_scale_16x_tmc2_ohrc`| Proposed Full | 7 | 15 | 46.7% | 7.25 | 7.24 | AFFINE | 0.94 | 215 | SUCCESS |
| **P4-22** | `pair_05_scale_16x_tmc2_ohrc`| Ablation No Scale Pyramid | 0 | 0 | 0.0% | N/A | N/A | NONE | 1.00 | 4700 | FAILED |
| **P4-23** | `pair_06_scale_20x_tmc2_ohrc`| SIFT Baseline | 5 | 10 | 50.0% | 0.00 | 10.00 | HOMOGRAPHY | 0.94 | 216 | DEGRADED |
| **P4-24** | `pair_06_scale_20x_tmc2_ohrc`| RIFT Baseline | 0 | 0 | 0.0% | N/A | N/A | HOMOGRAPHY | 1.00 | 4734 | FAILED |
| **P4-25** | `pair_06_scale_20x_tmc2_ohrc`| Proposed Full | 7 | 13 | 53.8% | 1.05 | 9.45 | AFFINE | 0.94 | 225 | SUCCESS |
| **P4-26** | `pair_06_scale_20x_tmc2_ohrc`| Ablation No Scale Pyramid | 0 | 0 | 0.0% | N/A | N/A | NONE | 1.00 | 4700 | FAILED |
| **P4-27** | `pair_07_cross_modal_swir_pan`| SIFT Baseline | 4 | 9 | 44.4% | 0.00 | 519.15 | HOMOGRAPHY | 0.91 | 445 | DEGRADED |
| **P4-28** | `pair_07_cross_modal_swir_pan`| RIFT Baseline | 124 | 145 | 85.5% | 1.39 | 27.79 | HOMOGRAPHY | 0.42 | 10510 | SUCCESS |
| **P4-29** | `pair_07_cross_modal_swir_pan`| Proposed Full | 166 | 194 | 85.6% | 1.56 | 27.76 | HOMOGRAPHY | 0.43 | 10300 | SUCCESS |
| **P4-30** | `pair_08_low_texture_maria` | SIFT Baseline | 400 | 795 | 50.3% | 0.45 | 16.10 | HOMOGRAPHY | 0.00 | 662 | SUCCESS |
| **P4-31** | `pair_08_low_texture_maria` | RIFT Baseline | 399 | 596 | 66.9% | 0.16 | 15.84 | HOMOGRAPHY | 0.00 | 9942 | SUCCESS |
| **P4-32** | `pair_08_low_texture_maria` | Proposed Full | 400 | 672 | 59.5% | 0.22 | 15.75 | HOMOGRAPHY | 0.00 | 10200 | SUCCESS |
| **P4-33** | `pair_08_low_texture_maria` | Ablation No Subpixel | 400 | 672 | 59.5% | 0.89 | 15.80 | HOMOGRAPHY | 0.00 | 9800 | SUCCESS |
| **P4-34** | `pair_09_dense_crater_highlands`| SIFT Baseline | 4 | 16 | 25.0% | 0.00 | 588.99 | HOMOGRAPHY | 0.84 | 513 | DEGRADED |
| **P4-35** | `pair_09_dense_crater_highlands`| RIFT Baseline | 4 | 5 | 80.0% | 0.00 | 469.54 | HOMOGRAPHY | 0.84 | 10110 | DEGRADED |
| **P4-36** | `pair_09_dense_crater_highlands`| Proposed Full | 4 | 9 | 44.4% | 122.81 | 485.54 | AFFINE | 0.84 | 10150 | DEGRADED |

---

## 2. Preserved Artifacts
All generated warped images, match lines, alpha overlays, and checkerboards are stored in:
`results/proposed_method/`
