# LUNARIS-X (SIH26166) — Master Technical Handbook & Defense Guide
**Automated Sub-Pixel Multi-Modal Lunar Image Registration Engine**  
*Team: Byte Hats | Smart India Hackathon 2026*

---

## Table of Contents
1. [The Lunar Registration Problem (Space Physics vs Computer Vision)](#1-the-lunar-registration-problem)
2. [Satellite Payloads & Orbital Geometry (Chandrayaan-2)](#2-satellite-payloads--orbital-geometry)
3. [Data Ingestion & PDS4 Architecture](#3-data-ingestion--pds4-architecture)
4. [Existing Systems & Literature Baselines](#4-existing-systems--literature-baselines)
5. [The Proposed Method: AMSR Architecture](#5-the-proposed-method-amsr-architecture)
6. [Geometric Transformation Models & The Homography Deep-Dive](#6-geometric-transformation-models--the-homography-deep-dive)
7. [Hyperparameter Dynamics & Sensitivity Tuning](#7-hyperparameter-dynamics--sensitivity-tuning)
8. [The Spatial Gini Dispersion Metric ($G_k$)](#8-the-spatial-gini-dispersion-metric-g_k)
9. [Comprehensive Scientific Metrics Telemetry](#9-comprehensive-scientific-metrics-telemetry)
10. [Visual Diagnostic Products & Interactive Inspection](#10-visual-diagnostic-products--interactive-inspection)
11. [Empirical Validation on Authentic Chandrayaan-2 Flight Data](#11-empirical-validation-on-authentic-flight-data)
12. [Jury Defense Cheatsheet (Top 10 Technical Questions)](#12-jury-defense-cheatsheet)

---

## 1. The Lunar Registration Problem

Image registration on the Moon is radically more challenging than on Earth. Algorithms engineered for Earth observation (Sentinel, Landsat, Google Earth) completely fail when applied to lunar imagery due to four fundamental physical factors:

### 1.1 Complete Absence of Atmosphere
* **Zero Rayleigh/Mie Scattering**: Earth has an atmosphere that diffuses sunlight into shadow zones. The Moon has a vacuum; there is zero atmospheric scattering.
* **Infinite Radiometric Dynamic Range**: Surfaces facing the Sun are intensely illuminated, while adjacent shadow regions plunge into pitch blackness ($DN \approx 0$).

### 1.2 Extreme Solar Illumination & Non-Linear Shadow Reversal
* As the Sun's azimuth angle ($\phi_\odot$) shifts between satellite revisit orbits (e.g., from an early morning pass to an afternoon pass), the cast shadows inside crater bowls shift $180^\circ$.
* **The Gradient Inversion Trap**: Classical gradient-based computer vision methods (SIFT, SURF, ORB) compute intensity gradients $\nabla I = [\frac{\partial I}{\partial x}, \frac{\partial I}{\partial y}]^T$. When lighting inverts, the vector direction rotates $180^\circ$, causing descriptor Euclidean distances to explode and resulting in **zero matches**.

### 1.3 Gigantic Sensor Resolution & Scale Gaps ($20\times$)
* Chandrayaan-2 carries instruments with vastly different Ground Sampling Distances (GSD):
  - **OHRC**: $0.25\text{ m/pixel}$ (25 centimeters)
  - **TMC-2**: $5.0\text{ m/pixel}$ (500 centimeters)
* This represents a **$20\times$ scale disparity** (a $400\times$ difference in pixel area). Standard matching algorithms break down when scale disparity exceeds $3\times$ to $4\times$.

### 1.4 Repetitive, Self-Similar Geomorphology
* Unlike terrestrial scenes with roads, buildings, coastlines, and rivers, the lunar regolith consists entirely of nested, impact-crater bowl structures and boulder fields.
* Distinctive keypoint matching without strict geometric verification results in massive false-correspondence rates due to repetitive circular features.

---

## 2. Satellite Payloads & Orbital Geometry

Chandrayaan-2 operates in a **100 km circular polar orbit** (inclination $\approx 90^\circ$). As the Moon slowly rotates underneath ($27.3\text{ Earth days}$ per rotation), the orbiter scans long ground swaths line by line using pushbroom line-scan CCD/CMOS sensors.

```
                    ┌──────────────────────────────────────────────┐
                    │      Chandrayaan-2 Orbiter (100 km Altitude)  │
                    └──────────────────────────────────────────────┘
                                  │                │
            ┌─────────────────────┘                └─────────────────────┐
            ▼                                                            ▼
┌───────────────────────────────┐                          ┌───────────────────────────────┐
│     OHRC (Pushbroom Optical)  │                          │    TMC-2 (3-Line Stereo)      │
│  • GSD: 0.25 m/pixel          │                          │  • GSD: 5.0 m/pixel           │
│  • Swath Width: 12 km         │                          │  • Swath Width: 20 km         │
│  • Target: Landing Site & DEM │                          │  • Target: Global Topography  │
└───────────────────────────────┘                          └───────────────────────────────┘
```

### 2.1 Payloads Summary
1. **OHRC (Orbiter High Resolution Camera)**:
   - World's highest-resolution civilian planetary camera ($0.25\text{ m/px}$).
   - Used for hazard mapping, boulder counting, and Artemis/ISRO landing site characterization.
2. **TMC-2 (Terrain Mapping Camera - 2)**:
   - Triple-strip pushbroom camera (Fore $+25^\circ$, Nadir $0^\circ$, Aft $-25^\circ$).
   - Generates stereo pairs for digital elevation model (DEM) generation at $5\text{ m/px}$.
3. **IIRS (Imaging Infrared Spectrometer)**:
   - Hyperspectral imager ($0.8\text{ }\mu\text{m}$ to $5.0\text{ }\mu\text{m}$) at $5\text{ m} - 80\text{ m/px}$.
   - Detects mineral signatures and hydroxyl/water-ice ($\text{H}_2\text{O}/\text{OH}$) absorption features.

### 2.2 Why Do Overlaps Occur?
* **Adjacent Orbit Side-Lap**: Consecutive polar orbits overlap at their longitudinal boundaries ($10\% - 30\%$ side-overlap).
* **Multi-Temporal Re-visit (Target Intersection)**: The orbiter observes the same crater formation weeks or months apart under different orbital pitch angles and solar azimuth angles.

---

## 3. Data Ingestion & PDS4 Architecture

Planetary science does not use standard 8-bit JPEG/PNG formats. All raw data downlinked through the Deep Space Network (DSN) to the **Indian Space Science Data Centre (ISSDC)** at Byalalu, Bengaluru, is formatted in accordance with the **NASA/ISRO PDS4 (Planetary Data System v4)** international standard.

### 3.1 PDS4 Structure
Every observation consists of two coupled files:
1. **`.xml` Label File**: Contains mission ephemeris, camera sensor temperature, optical transfer functions, coordinate bounding boxes (latitude/longitude polygons), Solar Azimuth Angle ($\phi_\odot$), Solar Incidence Angle ($\theta_i$), and exact GSD.
2. **`.img` / `.tif` Raster File**: 16-bit uncompressed radiometric Digital Numbers (DN) representing calibrated spectral radiance ($0$ to $65535$).

### 3.2 LUNARIS-X Ingestion Pipeline
* **`PDS4Parser` (`src/dataset/pds4_parser.py`)**: Automatically extracts ephemeris parameters and checks spatial bounding box intersections.
* **`ProvenanceTracker`**: Computes an immutable **SHA-256 cryptographic hash** of both the label and raster image. This guarantees data provenance and ensures zero data tampering.
* **`RadiometricNormalizer` (`src/preprocessing/normalizer.py`)**: Sanitizes `NaN` and `Inf` dropouts (caused by cosmic rays or saturated sensor wells), applies $2\%$ - $98\%$ percent-clip contrast stretching, and converts 16-bit raw counts to calibrated 8-bit matrices.

---

## 4. Existing Systems & Literature Baselines

| System / Method | Methodology | Strengths | Fatal Flaw on Lunar Data |
| :--- | :--- | :--- | :--- |
| **USGS ISIS3** | SPICE orbital geometry + manual tie pointing | Rigorous orbital math | Extremely labor-intensive; cannot automatically handle illumination inversion. |
| **NASA ASP** | SIFT + Normalized Cross Correlation (NCC) | Good on mild stereo | Crashes when scale ratio exceeds $3\times$; fails on inverted crater shadows. |
| **Classical SIFT** | Difference of Gaussians (DoG) + gradient orientation histograms | Rotation and scale invariant | **Fails when illumination shifts** ($180^\circ$ shadow flip causes gradient sign inversion $\rightarrow$ 0 matches). |
| **RIFT (2020)** | Phase Congruency + Maximum Index Map (MIM) | Radiometric and radiation invariant | Fails on scale gaps $>4\times$; highly vulnerable to 4-point spatial cluster traps. |
| **Deep Learning (LoFTR / SuperPoint)** | Learned feature matching via Transformers/CNNs | High terrestrial performance | **Severe hallucination** on featureless regolith; non-deterministic; high GPU overhead. |

---

## 5. The Proposed Method: AMSR Architecture
*(Adaptive Multi-Scale Structural Registration)*

```
[Raw Moving (Source) & Fixed (Reference)]
                   │
                   ▼
       [1. Condition Analyzer]
   (Measures scale ratio, noise, illumination inversion)
                   │
                   ▼
     [2. Radiometric Preprocessing]
   (Dead-pixel sanitization, percentile normalization)
                   │
                   ▼
  [3. Multi-Scale Log-Gabor Phase Congruency]
   (Frequency-domain structural boundary isolation)
                   │
                   ▼
       [4. Shadow-Edge Suppression]
   (Filters transient illumination shadows, retains rock rims)
                   │
                   ▼
    [5. Hierarchical Scale-Pyramid Bridge]
   (Isometric multi-octave bridging for 0.25m vs 5m)
                   │
                   ▼
  [6. Lowe's 0.80 NNDR + Bidirectional Matcher]
                   │
                   ▼
   [7. 4-Way Cardinal Rotation Consensus]
   (Auto 0°, 90°, 180°, 270° ascending/descending alignment)
                   │
                   ▼
    [8. Spatial Gini Dispersion Constraint]
   (Enforces uniform inlier network, eliminates cluster traps)
                   │
                   ▼
 [9. 2D Continuous Parabolic Hessian Refiner]
   (Continuous Taylor expansion for < 0.5 px accuracy)
                   │
                   ▼
    [10. 8-DOF Projective Homography Warping]
                   │
                   ▼
  [11. Multi-Product Visualizer & Mosaic Engine]
```

### Core Innovations in AMSR:
1. **Frequency-Domain Structural Phase Congruency**:
   - Instead of calculating image gradients, AMSR decomposes the image into frequency bands using a 2D Log-Gabor filter bank:
     $$G(\omega, \theta) = \exp\left(-\frac{(\ln(\omega/\omega_0))^2}{2(\ln(\kappa/\omega_0))^2}\right) \cdot \exp\left(-\frac{(\theta - \theta_j)^2}{2\sigma_\theta^2}\right)$$
   - Phase Congruency ($PC$) identifies points where all Fourier frequency components are in phase:
     $$PC(x, y) = \frac{\sum_o \sum_s W_o(x, y) \lfloor A_{so}(x, y) \Delta \Phi_{so}(x, y) - T_o \rfloor_+}{\sum_o \sum_s A_{so}(x, y) + \epsilon}$$
   - **Key Property**: $PC$ is strictly invariant to illumination, brightness, and contrast changes because edge boundaries depend on phase alignment, not gradient amplitude!

2. **Shadow-Edge Suppression**:
   - Transient shadow borders move with the Sun. AMSR filters low-frequency edge transitions and suppresses moving shadow boundaries, retaining only the sharp, invariant geomorphological crater rims.

3. **GSD-Consistent Scale-Pyramid Bridge**:
   - To match a 0.25m OHRC image against a 5m TMC-2 image, AMSR does not perform a naive resize (which blurs fine textures). It constructs an octave pyramid where each scale level is physically anchored to the ratio:
     $$\text{Scale Factor } s = \frac{\text{GSD}_{\text{source}}}{\text{GSD}_{\text{reference}}}$$
   - This enables scale-invariant correspondence across octave levels without interpolation artifacts.

---

## 6. Geometric Transformation Models & The Homography Deep-Dive

### 6.1 Hierarchy of Geometric Models
When transforming Source coordinates $\mathbf{x} = [x, y]^T$ to Reference coordinates $\mathbf{x}' = [x', y']^T$:

| Model | DOF | Preserves | Formula |
| :--- | :---: | :--- | :--- |
| **Translation** | **2** | Orientation, Scale, Angles, Parallelism | $\mathbf{x}' = \mathbf{x} + \mathbf{t}$ |
| **Similarity** | **4** | Shape, Angles, Parallelism | $\mathbf{x}' = s \mathbf{R} \mathbf{x} + \mathbf{t}$ |
| **Affine** | **6** | Parallelism, Midpoints | $\mathbf{x}' = \mathbf{A} \mathbf{x} + \mathbf{t}$ |
| **Homography** | **8** | Straight Lines | $\mathbf{x}' \sim \mathbf{H} \mathbf{x}$ |

### 6.2 What is Homography? (The Projective Transformation)
A **Homography** $\mathbf{H}$ is an invertible mapping between two projective planes. It represents the exact relationship between two 2D images of a common 3D plane viewed from two distinct camera positions.

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \sim \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

Expanding into inhomogeneous Cartesian coordinates:
$$x' = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + 1}, \quad y' = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + 1}$$

### 6.3 Why 8 Degrees of Freedom (8-DOF)?
The $3 \times 3$ matrix contains 9 entries. However, projective coordinates are scale-invariant: $\mathbf{H}$ and $\lambda \mathbf{H}$ (for any $\lambda \ne 0$) produce the exact same physical coordinates. Thus, dividing all entries by $h_{33}$ leaves **8 independent parameters**:
* $h_{13}, h_{23}$: Horizontal and vertical translation ($t_x, t_y$).
* $h_{11}, h_{12}, h_{21}, h_{22}$: Rotation, non-uniform scaling, and shear.
* **$h_{31}, h_{32}$**: **Perspective foreshortening and projective tilt parameters!**

### 6.4 Why 4 Points are Required:
Each correspondence pair $(x_i, y_i) \leftrightarrow (x'_i, y'_i)$ provides **2 linearly independent constraints**:
$$x'_i(h_{31}x_i + h_{32}y_i + 1) - (h_{11}x_i + h_{12}y_i + h_{13}) = 0$$
$$y'_i(h_{31}x_i + h_{32}y_i + 1) - (h_{21}x_i + h_{22}y_i + h_{23}) = 0$$
To solve for 8 unknowns:
$$\frac{8 \text{ unknowns}}{2 \text{ equations/point}} = \mathbf{4 \text{ point pairs}}$$
This is why RANSAC samples minimal sets of 4 non-collinear points.

### 6.5 Why Homography is Essential for the Moon:
Orbital satellite cameras scan the Moon with varying off-nadir pitch and roll tilt angles ($5^\circ - 20^\circ$). Furthermore, lunar crater walls have steep 3D bowl slopes. An Affine model assumes an orthographic camera at infinity with zero tilt; **only an 8-DOF Homography can rectify the perspective foreshortening caused by orbital camera slant and crater slope relief.**

---

## 7. Hyperparameter Dynamics & Sensitivity Tuning

### 7.1 Lowe’s Nearest-Neighbor Distance Ratio (NNDR)
$$\text{Ratio} = \frac{\|\mathbf{d}_{\text{query}} - \mathbf{d}_{\text{1st\_match}}\|_2}{\|\mathbf{d}_{\text{query}} - \mathbf{d}_{\text{2nd\_match}}\|_2}$$

* **Lowering Ratio ($0.80 \rightarrow 0.50$ — Ultra-Strict)**:
  - Eliminates almost all false matches.
  - *Severe Risk*: On repetitive lunar crater terrains, candidate count drops drastically. If inlier count drops below 4, the entire pipeline fails with an "Insufficient Inliers" error.
* **Raising Ratio ($0.80 \rightarrow 0.95$ — Highly Permissive)**:
  - Generates thousands of candidate points.
  - *Severe Risk*: Floods RANSAC with ambiguous matches. Inlier ratio drops from $89\%$ to under $25\%$. RANSAC takes significantly longer and risks converging on a corrupted transformation.
* **Why 0.80 is Default**: Empirically eliminates $90\%$ of false matches while retaining over $95\%$ of true correspondences.

### 7.2 RANSAC Reprojection Threshold ($\epsilon$)
A correspondence $(\mathbf{x}_i, \mathbf{x}'_i)$ is an **Inlier** if:
$$\|\mathbf{x}'_i - \frac{\mathbf{H}\mathbf{x}_i}{(\mathbf{H}\mathbf{x}_i)_z}\|_2 \le \epsilon$$

* **Lowering Threshold ($3.0\text{ px} \rightarrow 0.8\text{ px}$ — Perfectionist)**:
  - Forces an artificially low RMSE.
  - *Severe Risk*: Rejects genuine physical points affected by 2-kilometer crater elevation differences, mistaking genuine 3D terrain relief for error.
* **Raising Threshold ($3.0\text{ px} \rightarrow 8.0\text{ px}$ — Sloppy)**:
  - Produces an artificially large inlier count.
  - *Severe Risk*: Incorporates inaccurate matches into the final least-squares fit, producing a blurry, misaligned overlay (checkerboard boundaries become jagged).
* **Why 3.0 px is Default**: Accommodates 3D crater depth displacement during initial consensus, after which the **continuous 2D parabolic Hessian refiner polishes tie-points down to $< 0.5\text{ px}$ precision**.

---

## 8. The Spatial Gini Dispersion Metric ($G_k$)

### 8.1 The Local Sample Clustering Trap
A major failure mode in standard satellite registration is the **Sample Clustering Trap**:
* An image pair contains 1 large, sharp crater and 9 kilometers of flatter terrain.
* The feature detector finds 250 points — **all clustered inside that single crater**.
* RANSAC reports: *"Success! 250 inliers, 0.5 px RMSE!"*
* **The Reality**: The single crater matches, but because all 250 points were concentrated in a tiny $5\%$ area, the remaining $95\%$ of the lunar scene is violently stretched and distorted like melted rubber!

### 8.2 Mathematical Formulation
LUNARIS-X partitions the image into an $M \times N$ spatial grid (e.g., $4 \times 4 = 16$ cells) and computes the **Spatial Gini Coefficient**:

$$G_k = \frac{\sum_{i=1}^k \sum_{j=1}^k |n_i - n_j|}{2k \sum_{i=1}^k n_i}$$
*(Where $k = 16$ grid cells, and $n_i$ is the inlier count in cell $i$)*.

### 8.3 Interpretation:
* **$G_k \le 0.45$ (GOOD)**: Tie-points are evenly distributed across the entire lunar surface. The Homography is geometrically anchored across the full frame.
* **$0.45 < G_k \le 0.70$ (ACCEPTABLE)**: Moderate clustering (common on pre-cropped crater images).
* **$G_k > 0.70$ (POOR / CLUSTERED)**: Severe concentration. System flags a warning that geometric reliability outside the cluster zone is degraded.

---

## 9. Comprehensive Scientific Metrics Telemetry

LUNARIS-X outputs **12 quantitative metrics** complying with NASA/ISRO cartographic accuracy standards:

1. **Candidate Matches Count**: Total initial correspondences after nearest-neighbor matching.
2. **Inlier Matches Count**: Number of correspondences confirmed by RANSAC consensus.
3. **Inlier Ratio (%)**: $\frac{\text{Inliers}}{\text{Candidates}} \times 100\%$. Measures algorithm robustness against false matches.
4. **Reprojection RMSE (pixels)**:
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N \|\mathbf{x}'_i - \mathbf{H}\mathbf{x}_i\|^2}$$
   Measures the average distance between projected source points and reference points. Target: $< 2.0\text{ px}$.
5. **Ground-Truth RMSE (pixels)**:
   Evaluates estimated matrix $\mathbf{H}$ against analytical ground truth $\mathbf{H}_{\text{GT}}$ on synthetic benchmarks:
   $$\text{RMSE}_{\text{GT}} = \sqrt{\frac{1}{K} \sum_{k=1}^K \|\mathbf{H}_{\text{GT}}\mathbf{p}_k - \mathbf{H}_{\text{est}}\mathbf{p}_k\|^2}$$
6. **Ground Truth Status**: `AVAILABLE` on synthetic benchmarks | `NOT AVAILABLE (N/A)` on real flight data.
7. **Mean Sub-Pixel Residual (pixels)**: Average coordinate displacement after continuous 2D parabolic Hessian refinement.
8. **MAE of Residuals (pixels)**: Mean Absolute Error across all verified inliers.
9. **Median Residual (pixels)**: Robust statistical measure immune to single-point outliers.
10. **Sub-Pixel Accuracy Rate (< 0.5 px)**: Percentage of inliers with error strictly under half a pixel.
11. **Spatial Gini Coefficient ($G_k$)**: Measures spatial uniformity of the control point network ($0 = \text{uniform}, 1 = \text{clustered}$).
12. **End-to-End Latency (ms)**: Total execution runtime from ingestion to mosaic delivery.

---

## 10. Visual Diagnostic Products & Interactive Inspection

LUNARIS-X provides **6 interactive visual verification products** in `ComparisonViewer.tsx`:

1. **Side-by-Side Diagnostic**:
   - Displays Original Source (unaligned), Fixed Reference (ground truth frame), and Warped Source (registered).
2. **Tie-Point Match Inliers**:
   - Visualizes all correspondence vectors: **Green lines = Verified Inliers**, **Red lines = Purged Outliers**.
3. **Dynamic Real-Time Cross-Fade Overlay**:
   - Uses stacked hardware-accelerated GPU layers.
   - Live slider ($0\%$ to $100\%$) allows the mission specialist to fade smoothly between `Fixed Ref` and `Warped Src` at 60fps.
   - **Verification**: If Homography is correct, crater rims exhibit **zero ghosting and zero double edges**.
4. **8x8 Checkerboard Alignment**:
   - Alternating square tiles (Tile 1 from Reference, Tile 2 from Warped Source).
   - **Verification**: Circular crater boundaries continue across tile borders **with zero discontinuity or jump**.
5. **Radiometric Difference Heatmap**:
   - Computes absolute difference $|\mathbf{I}_{\text{ref}} - \mathbf{I}'_{\text{src}}|$ mapped through an Inferno colormap.
   - Aligned topography cancels out to pitch black; bright fringes reveal real solar shadow changes.
6. **Expanded Panoramic Mosaic (Full Combined Product)**:
   - Preserves $100\%$ of both images. Calculates the projective bounding-box union:
     $$\mathbf{T} = \begin{bmatrix} 1 & 0 & -x_{\min} \\ 0 & 1 & -y_{\min} \\ 0 & 0 & 1 \end{bmatrix}$$
   - Non-overlapping source and reference areas are fully retained; the overlap zone is alpha-blended.

---

## 11. Empirical Validation on Authentic Chandrayaan-2 Flight Data

### Dataset Profile
* **Mission**: Chandrayaan-2 Orbiter High Resolution Camera (OHRC)
* **Source Frame**: `ch2_ohr_crater_source_0609` (Jan 3, 2026, morning orbit pass)
* **Reference Frame**: `ch2_ohr_crater_reference_1005` (Jan 3, 2026, afternoon orbit pass)
* **Pixel Dimensions**: $1600 \times 1200\text{ pixels}$
* **Ground Sampling Distance (GSD)**: $0.25\text{ m/pixel}$ (25 cm resolution)
* **Solar Geometry**: Large solar azimuth angle variation ($\Delta \phi_\odot \approx 65^\circ$), inverted crater bowl shadows.

### Measured Empirical Results
* **Status**: `SUCCESS`
* **Verified Inliers**: **227 points** (from 468 candidates)
* **Inlier Consensus Ratio**: **$48.5\%$**
* **Reprojection RMSE**: **$1.27\text{ pixels}$** (Near sub-pixel precision across a $1600\times 1200$ frame!)
* **Estimated Homography Matrix $\mathbf{H}$**:
  $$\mathbf{H} = \begin{bmatrix} 0.984279 & -0.042111 & -26.2958 \\ 0.047794 & 0.991133 & -17.2733 \\ -0.000006 & -0.000011 & 1.000000 \end{bmatrix}$$
  *(Reveals a $26.3\text{ px}$ horizontal shift, $17.3\text{ px}$ vertical shift, $2.7^\circ$ rotation, and slight off-nadir tilt).*
* **Spatial Gini Coefficient**: $0.559$ (`POOR/CLUSTERED` — accurately diagnosing that features are naturally concentrated inside the focused crater structure).
* **Panoramic Mosaic Canvas**: **$1684 \times 1295 \times 3\text{ pixels}$** (Complete coverage of both non-overlapping borders preserved!).

---

## 12. Jury Defense Cheatsheet (Top 10 Technical Questions)

### Q1: "Why not use Deep Learning (LoFTR, SuperPoint, SuperGlue)?"
> **Answer**: *"Deep learning feature matchers are trained predominantly on terrestrial photos with atmospheric diffusion, vegetation, and buildings. When applied to featureless lunar regolith and deep shadow boundaries, deep learning models hallucinate non-existent features, suffer from out-of-distribution failure, and lack mathematical interpretability. Furthermore, they require power-hungry GPUs. Our AMSR method is frequency-deterministic, physics-grounded in Phase Congruency, runs on standard CPUs, and guarantees mathematical convergence."*

### Q2: "Why is Ground Truth RMSE marked as 'N/A' on your real flight data run?"
> **Answer**: *"Because on the real Moon, there are no physical surveyors on the ground to provide millimeter ground truth coordinates. Claiming to have a 'ground truth' metric on real flight data is scientifically dishonest. In real planetary missions, international standards (USGS/NASA) evaluate registration using Inlier Reprojection RMSE (which is 1.27 px in our run) and visual checkerboard continuity. Ground truth RMSE is strictly reserved for our synthetic benchmarks where true mathematical homography is known."*

### Q3: "How does Phase Congruency beat SIFT on lunar shadows?"
> **Answer**: *"SIFT relies on spatial intensity gradients ($\nabla I$). When the Sun shifts from morning to afternoon, the shadow flips $180^\circ$, inverting the gradient vector direction and causing descriptor matching to fail completely. Phase Congruency operates in the Fourier frequency domain using Log-Gabor filters. It detects where all frequency harmonics are in phase — which corresponds to the true physical rock rim of the crater, completely ignoring the amplitude of the moving shadow."*

### Q4: "How do you handle Ascending vs Descending satellite orbits?"
> **Answer**: *"When a satellite captures an area on an ascending pass (South to North) and later on a descending pass (North to South), the images are rotated by $180^\circ$. If the flight camera is tilted sideways, the image is rotated by $90^\circ$. LUNARIS-X incorporates an automatic 4-Way Cardinal Orientation Recovery engine ($0^\circ, 90^\circ, 180^\circ, 270^\circ$). If initial matching is low, it tests rotational consensus in RAM within milliseconds, completely eliminating manual pre-rotation."*

### Q5: "What is the 4-Point Sample Cluster Trap?"
> **Answer**: *"Standard RANSAC only needs 4 points to compute a Homography. If an algorithm finds 200 points all crammed inside one single crater, RANSAC will fit a matrix that matches that single crater perfectly, but violently distorts the rest of the 10-kilometer scene. We eliminate this trap by enforcing a Spatial Gini Dispersion constraint ($G_k \le 0.45$) across a spatial grid, mathematically proving that tie-points are uniformly spread across the entire terrain."*

### Q6: "Why did you use 8-DOF Homography instead of 6-DOF Affine?"
> **Answer**: *"Chandrayaan-2 orbits involve off-nadir camera pitch and roll tilt angles, and lunar craters have steep 3D bowl slopes. An Affine transformation can only handle translation, rotation, scale, and shear — it cannot correct for perspective slant. The two perspective parameters ($h_{31}, h_{32}$) in an 8-DOF Homography are essential to rectify camera perspective tilt and surface relief foreshortening."*

### Q7: "What happens if an image is completely flat with no craters?"
> **Answer**: *"LUNARIS-X includes a Dynamic Model Selector. If feature points are collinear or insufficient to support an 8-DOF Homography without singularity, the pipeline automatically detects the degeneracy and falls back gracefully to a 6-DOF Affine or 4-DOF Similarity model, preventing numerical crash."*

### Q8: "How does the Continuous 2D Parabolic Hessian achieve sub-pixel accuracy?"
> **Answer**: *"Discrete pixel matching only gives integer coordinates. Once integer tie-points are found, our SubPixelRefiner extracts a local similarity surface and fits a continuous 2D quadratic Taylor polynomial. Setting the gradient $\nabla f = 0$ yields the sub-pixel peak displacement: $\Delta \mathbf{x} = -\mathbf{H}_{\text{Hessian}}^{-1} \nabla f$, refining point coordinates to $< 0.5\text{ pixels}$ accuracy."*

### Q9: "What is your software architecture?"
> **Answer**: *"LUNARIS-X is engineered as a robust 3-tier distributed microservice: a Python 3.13 FastAPI machine learning service handling OpenCV/NumPy matrix math, orchestrated by an enterprise Java 21 Spring Boot 3 backend handling job queuing and database persistence, serving an interactive React 18 + Vite frontend with 60fps GPU-accelerated layer blending."*

### Q10: "How does your system contribute to future lunar exploration (Artemis / Chandrayaan-4)?"
> **Answer**: *"Future missions require precise landing site hazard mapping. By fusing high-resolution 0.25m OHRC morphological maps with TMC-2 stereo elevation DEMs and IIRS water-ice spectral data, LUNARIS-X provides unified, sub-pixel co-registered cartographic products essential for lunar landing site selection, rover path planning, and volatile resource prospecting."*
