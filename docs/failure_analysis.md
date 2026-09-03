# Failure Analysis Methodology & Diagnostic Framework

## 1. Objectives of Phase 3 Failure Analysis
Before designing and locking our innovative contributions, we perform a structured failure diagnosis by deliberately subjecting all baselines (SIFT, AKAZE, RIFT2, LoFTR) to extreme lunar conditions and isolating the exact mathematical failure mechanism.

---

## 2. Failure Mode Taxonomy

```
+---------------------------------------------------------------------------------------------------+
| CODE | FAILURE MODE             | ROOT CAUSE                               | TEST SCENARIO        |
+------+--------------------------+------------------------------------------+----------------------+
| FM-1 | Shadow Edge Inversion    | Solar azimuth shift > 90° flips gradient | High sun angle delta |
|      |                          | vectors; DoG / FAST keypoints drop.      | (Suite B)            |
+------+--------------------------+------------------------------------------+----------------------+
| FM-2 | Scale Collapse           | Feature descriptors cannot span > 4x     | TMC-2 to OHRC (1:20) |
|      |                          | resolution gap; octave levels decouple. | (Suite C)            |
+------+--------------------------+------------------------------------------+----------------------+
| FM-3 | Spectral Inversion       | IIRS SWIR absorption bands reverse       | IIRS vs Panchromatic |
|      |                          | local contrast vs panchromatic radiance. | (Suite D)            |
+------+--------------------------+------------------------------------------+----------------------+
| FM-4 | Spatial Clumping Defect  | RANSAC fits a local planar model on a    | Mixed Crater/Mare    |
|      |                          | single high-contrast crater rim; rest fails. (Suite E)         |
+------+--------------------------+------------------------------------------+----------------------+
| FM-5 | Sub-Pixel Jitter         | Integer correlation peaks drift due to   | Stereo Triplet       |
|      |                          | foreshortening and terrain parallax.     | (TMC-2 Fore/Aft)     |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Diagnostic Logging Protocol
For every test pair processed during benchmarking, the diagnostic engine records:
1. `pair_id`: Unique identifier.
2. `sun_angle_delta`: Angle difference between primary and secondary image solar azimuths.
3. `scale_ratio`: Resolution ratio $S_A / S_B$.
4. `sensor_pair`: e.g. `OHRC-TMC2`, `TMC2-IIRS`.
5. `inlier_count`: Number of verified geometric inliers.
6. `inlier_ratio`: Percentage of candidate matches that are true inliers.
7. `rmse`: Geometric registration root mean square error.
8. `gini_coefficient`: Spatial dispersion measure ($0.0 = \text{uniform}, 1.0 = \text{clustered}$).
9. `failure_classification`: Categorized as `SUCCESS`, `FM-1`, `FM-2`, `FM-3`, `FM-4`, or `FM-5`.
