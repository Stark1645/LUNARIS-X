# Scientific Experiment Log & Measured Benchmark Registry

This document records **only actual measured experimental metrics** obtained from executions on the standardized `Ch-2-MatchBench` benchmark suites. No values are fabricated, interpolated, or estimated.

---

## 1. Baseline Evaluation: SIFT vs RIFT Baselines (Phase 2 Execution)

- **Date**: 2026-09-02
- **Data Category**: `SYNTHETIC_BENCHMARK` (9 pairs across 5 challenge suites)
- **Evaluation Settings**: RANSAC Reprojection Threshold = $3.0\text{ px}$, Sub-Pixel Refinement = Enabled, Spatial Dispersion Filter = Enabled ($4 \times 4$ grid, max 25 pts/bin), Ratio Threshold = $0.80$, Cross-Check = Enabled.

### Summary Table of Measured Metrics

| Suite | Pair Name | Challenge Tested | Algorithm | Status | Inlier Count | Inlier Ratio (%) | Inlier RMSE (px) | Ground Truth RMSE (px) | Sub-Pixel Residual (px) | Spatial Gini ($G_k$) | Latency (ms) | Key Observations / Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Suite A** | `pair_01_baseline_same_sun` | Baseline validity ($\Delta\phi_\odot = 3^\circ$, Scale 1:1) | **SIFT** | **SUCCESS** | 59 | 67.0% | 1.47 | 0.68 | 1.20 | 0.41 | 525 | Reliable registration under standard conditions. |
| **Suite A** | `pair_01_baseline_same_sun` | Baseline validity ($\Delta\phi_\odot = 3^\circ$, Scale 1:1) | **RIFT** | **SUCCESS** | 307 | 94.2% | 0.18 | 33.45 | 0.07 | 0.32 | 9916 | Dense tie-points extracted from phase congruency. |
| **Suite B** | `pair_02_sun_angle_90deg` | Sun Azimuth $\Delta\phi_\odot = 90^\circ$ | **SIFT** | **DEGRADED** | 4 | 36.4% | 0.00 | 461.98 | 0.00 | 0.75 | 421 | Severe gradient reversal on crater shadows; homography degenerated (GT RMSE 462 px). |
| **Suite B** | `pair_02_sun_angle_90deg` | Sun Azimuth $\Delta\phi_\odot = 90^\circ$ | **RIFT** | **DEGRADED** | 4 | 100.0% | 0.00 | 609.12 | 0.00 | 0.84 | 9428 | Keypoints collapsed to single rim cluster; insufficient spatial distribution for homography. |
| **Suite B** | `pair_03_sun_angle_180deg` | Sun Azimuth $\Delta\phi_\odot = 180^\circ$ (Shadow Inversion) | **SIFT** | **DEGRADED** | 4 | 26.7% | 0.00 | 347.09 | 0.00 | 0.75 | 557 | Complete gradient polarity flip causes SIFT descriptor mismatch (GT RMSE 347 px). |
| **Suite B** | `pair_03_sun_angle_180deg` | Sun Azimuth $\Delta\phi_\odot = 180^\circ$ (Shadow Inversion) | **RIFT** | **SUCCESS** | 12 | 41.4% | 1.51 | 4.87 | 1.33 | 0.61 | 9526 | Phase congruency preserves structural morphology under $180^\circ$ lighting reversal (GT RMSE 4.87 px). |
| **Suite C** | `pair_04_scale_4x` | Scale Disparity $4\times$ | **SIFT** | **SUCCESS** | 67 | 93.1% | 1.31 | 1.26 | 1.08 | 0.94 | 391 | DoG octave scale-space handles $4\times$ resolution jump accurately. |
| **Suite C** | `pair_04_scale_4x` | Scale Disparity $4\times$ | **RIFT** | **FAILED** | 0 | 0.0% | N/A | N/A | N/A | 1.00 | 5647 | **Failure**: Log-Gabor filter bank is fixed-scale in single octave; descriptor frequency shifts under $4\times$ disparity. |
| **Suite C** | `pair_05_scale_16x_tmc2_ohrc`| Scale Disparity $16\times$ (TMC-2 $\leftrightarrow$ OHRC) | **SIFT** | **DEGRADED** | 5 | 62.5% | 0.00 | 6.79 | 0.00 | 0.94 | 200 | Borderline inlier count (5 pts clustered on tiny 64x64 patch); high spatial Gini ($G_k=0.94$). |
| **Suite C** | `pair_05_scale_16x_tmc2_ohrc`| Scale Disparity $16\times$ (TMC-2 $\leftrightarrow$ OHRC) | **RIFT** | **FAILED** | 0 | 0.0% | N/A | N/A | N/A | 1.00 | 4790 | **Failure**: 0 raw matches produced. Frequency wavelength mismatch between 64x64 and 1024x1024. |
| **Suite C** | `pair_06_scale_20x_tmc2_ohrc`| Extreme Scale $20\times$ (TMC-2 $\leftrightarrow$ OHRC) | **SIFT** | **DEGRADED** | 5 | 50.0% | 0.00 | 10.00 | 0.00 | 0.94 | 216 | Severe scale breakdown; tie-points restricted to top corner (GT RMSE 10.0 px). |
| **Suite C** | `pair_06_scale_20x_tmc2_ohrc`| Extreme Scale $20\times$ (TMC-2 $\leftrightarrow$ OHRC) | **RIFT** | **FAILED** | 0 | 0.0% | N/A | N/A | N/A | 1.00 | 4734 | **Failure**: 0 keypoints extracted on 51x51 patch; complete scale collapse. |
| **Suite D** | `pair_07_cross_modal_swir_pan`| Cross-Modal SWIR vs Panchromatic | **SIFT** | **DEGRADED** | 4 | 44.4% | 0.00 | 519.15 | 0.00 | 0.91 | 445 | Severe gradient inversion across non-linear spectral absorption bands (GT RMSE 519 px). |
| **Suite D** | `pair_07_cross_modal_swir_pan`| Cross-Modal SWIR vs Panchromatic | **RIFT** | **SUCCESS** | 124 | 85.5% | 1.39 | 27.79 | 1.05 | 0.42 | 10510 | Phase congruency successfully bridges cross-modal spectral differences with 124 inliers. |
| **Suite E** | `pair_08_low_texture_maria` | Low-Contrast Flat Lunar Maria | **SIFT** | **SUCCESS** | 400 | 50.3% | 0.45 | 16.10 | 0.39 | 0.00 | 662 | Abundant weak gradients detected; high spatial coverage ($G_k = 0.00$). |
| **Suite E** | `pair_08_low_texture_maria` | Low-Contrast Flat Lunar Maria | **RIFT** | **SUCCESS** | 399 | 66.9% | 0.16 | 15.84 | 0.05 | 0.00 | 9942 | Uniform feature distribution across flat terrain ($G_k = 0.00$). |
| **Suite E** | `pair_09_dense_crater_highlands`| Dense Repetitive Crater Terrain ($\Delta\phi_\odot = 60^\circ$) | **SIFT** | **DEGRADED** | 4 | 25.0% | 0.00 | 588.99 | 0.00 | 0.84 | 513 | Repetitive circular rims cause false perceptual matches; RANSAC locked onto wrong plane. |
| **Suite E** | `pair_09_dense_crater_highlands`| Dense Repetitive Crater Terrain ($\Delta\phi_\odot = 60^\circ$) | **RIFT** | **DEGRADED** | 4 | 80.0% | 0.00 | 571.43 | 0.00 | 0.84 | 10110 | MIM orientation histograms aliased across symmetric crater circular rims. |

---

## 2. Authentic Flight Data Evaluation: `AUTHENTIC_CH2_PRADAN`

- **Status**: *No raw ISRO PRADAN PDS4 product files currently staged in `data/raw/`*.
- **Policy**: All authentic flight data runs will be processed and logged in a separate subsection below as authentic products are ingested. Synthetic and authentic metrics will **never** be aggregated together.

| Exp ID | Pair Name | Mission / Instrument | Solar Incidence | Solar Azimuth | GSD Ratio | Method | Status | Inliers | Inlier Ratio | RMSE (px) | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| *Pending* | - | ISRO CH2 TMC-2 / OHRC | - | - | - | - | *Pending* | - | - | - | - |

---

## 3. Preserved Artifacts & Reproduction Directory
All output products (warped registered images, correspondence match lines, alpha overlays, checkerboard composites, difference maps, and inlier CSV coordinate files) are preserved in:
`results/baseline_evaluation/synthetic_benchmark/`
