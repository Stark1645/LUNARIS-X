# SIH26166: System Requirements Specification

## 1. Functional Requirements (FR)

- **FR-1: Multi-Format Data Ingestion**
  - The system must parse and ingest Chandrayaan-2 PDS4 XML labels, GeoTIFF images, and raw planetary raster data for OHRC, TMC-2 (Nadir, Fore, Aft), and IIRS (hyperspectral cubes).
- **FR-2: Solar & Ephemeris Geometry Extraction**
  - The system must extract solar azimuth ($\phi_\odot$), solar incidence angle ($\theta_i$), emission angle ($\epsilon$), and phase angle ($\alpha$) from image metadata / SPICE kernels.
- **FR-3: Multi-Scale Pyramid Generation**
  - The system must generate intermediate scale representations to bridge resolution ratios between $1:1$ and $1:20+$ (TMC-2 to OHRC).
- **FR-4: Invariant Feature Extraction & Matching**
  - The system must compute illumination- and scale-invariant descriptors and identify matching tie-points between arbitrary image pairs.
- **FR-5: False-Match Rejection & Outlier Filtering**
  - The system must filter out spurious correspondences caused by repetitive crater patterns and shadow edges using robust geometric estimation (RANSAC / USAC-based verification; MAGSAC++ evaluated where appropriate).
- **FR-6: Spatially Distributed Control Network Generation**
  - The system must ensure tie-points are not solely clustered on high-contrast crater rims by enforcing a spatial Gini distribution constraint ($G_k < 0.35$).
- **FR-7: Sub-Pixel Parabolic Refinement**
  - The system must refine tie-point locations to sub-pixel accuracy ($< 0.5\text{ px}$) using local similarity surface Hessian analysis.
- **FR-8: Geometric Image Registration & Blending**
  - The system must compute transformation matrices (Affine, Projective Homography, and Thin-Plate Spline) and produce warped, co-registered overlays and checkerboard composites.
- **FR-9: Scientific Metric Logging & Reporting**
  - The system must output quantitative reports including inlier count, inlier ratio, RMSE, spatial Gini coefficient, and runtime latency.
- **FR-10: Interactive UI & Inspection**
  - The system must provide an interactive web dashboard for uploading, running correspondence, toggling baselines vs proposed method, sliding overlay transparency, and exporting control network files.

---

## 2. Scientific & Mathematical Objectives (Experimental Targets)

> [!NOTE]
> All quantitative metrics listed below represent **Experimental Optimization Targets** and research hypotheses to be measured empirically on standardized benchmarks. They are not presumed or guaranteed minimums prior to execution.

- **Target-1: Illumination Invariance**: Evaluate inlier preservation and geometric consistency under significant solar azimuth shifts ($\Delta \phi_\odot \ge 90^\circ$ and $\Delta \phi_\odot \approx 180^\circ$). Target: maximize inlier ratio relative to classical gradient baselines.
- **Target-2: Scale Invariance**: Measure registration success across multi-octave resolution jumps (e.g. $1:4$ to $1:20+$ scale gaps between TMC-2 and OHRC) using hierarchical scale bridging.
- **Target-3: Registration Precision**: Evaluate geometric reprojection RMSE against analytical ground truth on synthetic benchmarks and calibrated flight pairs. Target: achieve sub-pixel reprojection accuracy on verified inliers.
- **Target-4: Cross-Modal Repeatability**: Quantitatively test point correspondence between IIRS SWIR absorption bands and Panchromatic optical imagery.
- **Target-5: Spatial Dispersion Uniformity**: Minimize the spatial Gini coefficient ($G_k$) across heterogeneous lunar scenes (cratered highlands vs smooth maria), preventing tie-point clustering on individual crater rims.

---

## 3. Data Integrity & Provenance Classification

The system strictly distinguishes between two separate data regimes:
1. **Authentic Chandrayaan-2 Flight Data**: Raw PDS4 XML labels and GeoTIFFs downloaded from the official ISRO ISSDC PRADAN portal, with genuine orbital ephemeris metadata and zero synthetic simulation.
2. **Synthetic / Semi-Synthetic Benchmark Data (`Ch-2-MatchBench`)**: Numerically simulated lunar elevation models with Lommel-Seeliger shading and analytical ground-truth homographies, used for controlled failure analysis and stress-testing.

---

## 4. Technical Constraints (TC)

- **TC-1: Environment**: Python 3.10+, PyTorch 2.x, OpenCV 4.x, FastAPI backend, React 18 frontend.
- **TC-2: Deployment**: Capable of running on standard GPU hardware with CPU-fallback capability.
- **TC-3: Memory Safety**: Processing large OHRC scenes via dynamic tile-based partitioning to prevent Out-Of-Memory (OOM) errors.
