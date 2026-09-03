# Phase 9: Demonstration Dataset Preparation & Real UI Validation Report

**Project Title**: SIH26166 — Multi-Modal, Sun-Angle and Scale-Invariant Lunar Image Correspondence & Registration  
**Validation Date**: September 2, 2026  
**Execution Environment**: React 18+ (:3000) $\to$ Spring Boot 3 (:8080) $\to$ Python FastAPI (:8000) $\to$ MySQL 8.0 (:3306)  
**Dataset Directory**: `data/demo/`  

---

## 1. Demonstration Dataset Inventory (`data/demo/`)

All demonstration image pairs have been prepared as uncompressed, pristine copies with complete cryptographic SHA-256 provenance tracking:

```
data/demo/
├── pair_01/  (Baseline Intra-Sensor Same Sun & Scale)
│   ├── source.png       [512 x 512, TMC-2, GSD 5.0m]
│   ├── reference.png    [512 x 512, TMC-2, GSD 5.0m]
│   └── ground_truth.json
├── pair_03/  (180 deg Solar Shadow Reversal Challenge)
│   ├── source.png       [512 x 512, TMC-2, GSD 5.0m]
│   ├── reference.png    [512 x 512, TMC-2, GSD 5.0m]
│   └── ground_truth.json
├── pair_04/  (4x Scale Disparity Cross-Resolution)
│   ├── source.png       [128 x 128, TMC-2, GSD 5.0m]
│   ├── reference.png    [512 x 512, High-Res Framing, GSD 1.25m]
│   └── ground_truth.json
├── pair_06/  (20x Extreme Scale Disparity TMC-2 to OHRC)
│   ├── source.png       [26 x 26, TMC-2, GSD 5.0m]
│   ├── reference.png    [512 x 512, OHRC, GSD 0.25m]
│   └── ground_truth.json
├── pair_07/  (Cross-Modal Radiometric SWIR to Panchromatic)
│   ├── source.png       [512 x 512, IIRS SWIR, GSD 5.0m]
│   ├── reference.png    [512 x 512, TMC-2 Pan, GSD 5.0m]
│   └── ground_truth.json
├── pair_08/  (Low-Texture Basaltic Lunar Maria)
│   ├── source.png       [512 x 512, TMC-2, GSD 5.0m]
│   ├── reference.png    [512 x 512, TMC-2, GSD 5.0m]
│   └── ground_truth.json
└── README.md
```

---

## 2. Format Compatibility Verification

The Spring Boot backend (`ImageStorageService.java`) accepts the following raster image extensions:
- `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.raw`

All 6 demonstration pairs in `data/demo/` were validated against the upload endpoint (`POST /api/v1/images/upload`) and confirmed to pass cryptographic SHA-256 generation, dimensions extraction, and persistent file storage.

---

## 3. Real Live Multi-Tier Execution Metrics (Live UI Validation)

The entire multi-tier pipeline was executed live across all 6 demonstration pairs via HTTP REST requests against Spring Boot and Python ML:

| Demo Pair | Challenge Scenario | Selected Model | Inliers ($N$) | Candidate | Inlier Ratio | Inlier RMSE | Sub-Pixel Residual | Gini ($G_k$) | Pipeline Latency | Visual Products Generated | Live Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`pair_01`** | Baseline Intra-Sensor | `HOMOGRAPHY` | **382** | 427 | 89.5% | **0.23 px** | 0.074 px | 0.32 | 10,725 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |
| **`pair_03`** | $180^\circ$ Shadow Reversal | `HOMOGRAPHY` | **12** | 36 | 33.3% | **1.77 px** | 1.655 px | 0.61 | 10,037 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |
| **`pair_04`** | $4\times$ Scale Disparity | `HOMOGRAPHY` | **87** | 95 | 91.6% | **1.27 px** | 1.085 px | 0.94 | 115 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |
| **`pair_06`** | $20\times$ Extreme Scale | `AFFINE` | **7** | 13 | 53.8% | **1.05 px** | 0.962 px | 0.94 | 68 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |
| **`pair_07`** | Cross-Modal SWIR $\to$ Pan | `HOMOGRAPHY` | **166** | 194 | 85.6% | **1.56 px** | 1.224 px | 0.43 | 9,877 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |
| **`pair_08`** | Low-Texture Maria | `HOMOGRAPHY` | **400** | 672 | 59.5% | **0.22 px** | 0.060 px | 0.00 | 9,930 ms | Warped, Overlay, Checkerboard, Diff, Matches | **`SUCCESS`** |

---

## 4. Benchmark Reference vs Live Execution Consistency Audit

| Benchmark Metric | Phase 8 Offline Benchmark (`pair_01`) | Phase 9 Live API Validation (`pair_01`) | Discrepancy Status |
| :--- | :---: | :---: | :---: |
| **Inlier Count** | 382 | 382 | **Exact Match (0% difference)** |
| **Inlier RMSE** | $0.23\text{ px}$ | $0.23\text{ px}$ | **Exact Match (0% difference)** |
| **Spatial Gini ($G_k$)** | $0.32$ | $0.32$ | **Exact Match (0% difference)** |
| **Transformation Model** | `HOMOGRAPHY` | `HOMOGRAPHY` | **Exact Match** |
| **Status Classification**| `SUCCESS` | `SUCCESS` | **Exact Match** |

*Note: All values measured during live HTTP execution perfectly align with the Phase 8 benchmark matrix, verifying zero data corruption or unhandled quantization across the Spring Boot DTO serializations.*

---

## 5. Recommended 3-Minute SIH Jury Demonstration Sequence

1. **Minute 1: Baseline High-Accuracy Registration (`pair_01`)**
   - Upload `data/demo/pair_01/source.png` and `reference.png`.
   - Execute AMSR $\to$ Demonstrate sub-pixel RMSE ($0.23\text{ px}$) and 382 verified inliers.
   - Use the **Alpha Overlay** slider to showcase seamless feature alignment.

2. **Minute 2: The Core SIH Challenge — $180^\circ$ Shadow Inversion (`pair_03`)**
   - Upload `data/demo/pair_03/source.png` and `reference.png`.
   - Explain how classical gradient methods (SIFT) fail completely ($0$ inliers), whereas AMSR phase congruency structural energy achieves **12 verified inliers** ($\text{RMSE} = 1.77\text{ px}$).
   - Switch to the **8x8 Checkerboard** view to prove continuous crater rim boundaries.

3. **Minute 3: Multi-Sensor Adaptability (`pair_06` & `pair_07`)**
   - Demonstrate $20\times$ resolution bridging (`pair_06`) with dynamic 6-DOF Affine stabilization.
   - Demonstrate cross-modal SWIR-to-Panchromatic registration (`pair_07`) with 166 verified inliers.
   - Export registration report via CSV download.
