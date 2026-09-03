# LUNARIS-X (SIH26166)
### Multi-Modal, Sun Angle & Scale-Invariant Lunar Image Registration Platform
**Indian Space Research Organisation (ISRO) | Smart India Hackathon 2026**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Java](https://img.shields.io/badge/Java-21-orange.svg?logo=openjdk)](https://openjdk.org)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.3+-6DB33F.svg?logo=springboot)](https://spring.io/projects/spring-boot)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg?logo=vite)](https://vitejs.dev)
[![Tests](https://img.shields.io/badge/Tests-65%20Passing-brightgreen.svg)]()

---

## Overview

**LUNARIS-X** is an end-to-end, multi-tier distributed platform engineered for high-precision autonomous co-registration and landmark correspondence of Chandrayaan-2 lunar orbiter observations across diverse optical sensors (**OHRC**, **TMC-2**, and **IIRS**).

Co-registering multi-temporal lunar surface imagery poses extreme physical and geometric challenges:
1. **Extreme Sun Angle & Illumination Invariance**: Solar incidence variations ($\Delta\phi_\odot \approx 180^\circ$) cause crater shadow inversions where intensity and gradient-based detectors fail.
2. **Severe Scale Disparities**: Scale jumps ranging from $1:16$ to $1:20$ between TMC-2 (~5 m) and OHRC (~0.28 m), and up to $1:300$ between IIRS (~80 m) and OHRC.
3. **Multi-Modal Radiometry**: Panchromatic visible imagery vs. hyperspectral SWIR absorption bands with non-linear radiometric inversions.
4. **Sub-Pixel Geometric Accuracy**: Robust outlier filtering and transformation modeling producing $\text{RMSE} < 1.0\text{ px}$.

---

## Implementation Truth Matrix (Strict Scientific Audit)

In compliance with SIH26166 strict operational integrity:

| Capability / Algorithm | Status | Details |
| :--- | :--- | :--- |
| **PDS4 / PDS3 Metadata Parser** | **IMPLEMENTED & TESTED** | `pds4_parser.py`: extracts observational geometry, GSD, footprints, and field-level provenance (`FOUND`, `DERIVED`, `ESTIMATED`, `MISSING`). |
| **PRADAN Product Catalog** | **IMPLEMENTED & TESTED** | `pradan_catalog.py`: local directory scanning, independent querying for OHRC, TMC-2, and IIRS. |
| **Autonomous Overlap Detection** | **IMPLEMENTED & TESTED** | `overlap_detector.py`: mathematical 2D/spherical footprint intersection, scale disparity ratio, returns `CONFIRMED_OVERLAP`, `CONFIRMED_DISJOINT`, or `INDETERMINATE_MISSING_FOOTPRINT`. |
| **Scientific Reference Selector** | **IMPLEMENTED & TESTED** | `reference_selector.py`: 4-tier decision priority (Mission &rarr; User &rarr; Objective &rarr; Multi-factor Heuristic). |
| **Multi-Modal Preprocessor** | **IMPLEMENTED & TESTED** | `normalizer.py`: non-destructive NaN/Inf sanitization, 16-bit radiometric percentile stretch, instrument-specific conditioning (Bilateral, CLAHE, SWIR median). |
| **SIFT Baseline Pipeline** | **IMPLEMENTED & TESTED** | `sift_detector.py`: OpenCV SIFT feature extraction and nearest-neighbor ratio matching. |
| **RIFT Baseline Pipeline** | **IMPLEMENTED & TESTED** | `rift_detector.py`: Log-Gabor Phase Congruency + Maximum Index Map (MIM) descriptors. |
| **Proposed Method (AMSR)** | **IMPLEMENTED & TESTED** | `proposed_pipeline.py`: Structural Phase Congruency, shadow-boundary edge suppression, multi-scale pyramid, MAGSAC++ outlier rejection. |
| **Geometric Verification** | **IMPLEMENTED & TESTED** | `verifier.py`: MAGSAC++ with RANSAC fallback, reporting inlier ratio, candidate counts, and reprojection residuals. |
| **Spatial Distribution Filter** | **IMPLEMENTED & TESTED** | `spatial_filter.py`: 4&times;4 spatial grid binning, inlier cap, Gini coefficient $G_k$, objective quality status (`GOOD`, `ACCEPTABLE`, `POOR`). |
| **Sub-Pixel Refiner** | **IMPLEMENTED & TESTED** | `subpixel.py`: 2D quadratic Taylor expansion on local NCC patch: $\delta = -H^{-1} g$, strictly verifying concave Hessian. |
| **Dynamic Model Selector** | **IMPLEMENTED & TESTED** | `model_selector.py`: condition number stability check, dynamic model switching (Homography &rarr; Affine &rarr; Similarity &rarr; Translation). |
| **LoFTR Deep Transformer** | **PROPOSED / UNIMPLEMENTED** | Documented as proposed future deep learning enhancement; not fabricated as active classical engine. |
| **Real PRADAN Validation** | **INGESTION READY** | Infrastructure fully tested and ready for user-provided flight data. Not pre-claimed without real flight products. |

---

## Real ISRO/ISSDC PRADAN Data Workflow

LUNARIS-X does **not** scrape or automate PRADAN logins. Users download authentic Chandrayaan-2 products from ISSDC and process them locally:

```
[ISSDC PRADAN Web Portal]
         │ (Manual Search & Download)
         ▼
[Local Directory: data/pradan/]
         │
         ├── PDS4 XML Label (*.xml)
         └── Raster Payload (*.tif, *.img)
         │
         ▼
[1. Local Directory Scan & Parsing]
         │ (src/dataset/pds4_parser.py & pradan_catalog.py)
         ▼
[2. Catalog Registry & Querying]
         │ (OHRC, TMC-2, IIRS indexed independently)
         ▼
[3. Autonomous Overlap Detection]
         │ (src/dataset/overlap_detector.py)
         ▼
[4. 4-Tier Reference / Moving Selection]
         │ (src/proposed/reference_selector.py)
         ▼
[5. Non-Destructive Multi-Modal Preprocessing]
         │ (src/preprocessing/normalizer.py)
         ▼
[6. Feature Matching & MAGSAC++ Geometric Verification]
         │ (SIFT, RIFT, or Structural AMSR)
         ▼
[7. Sub-Pixel Refinement & Transformation Re-estimation]
         │ (src/refinement/subpixel.py)
         ▼
[8. Residual Evaluation & Provenance Output]
```

### Step 1: Download PRADAN Products
1. Visit the official ISSDC PRADAN portal: [https://pradan.issdc.gov.in/ch2/](https://pradan.issdc.gov.in/ch2/).
2. Log in with your ISRO/ISSDC credentials.
3. Search for overlapping observations:
   - **OHRC (Orbiter High Resolution Camera)**: Calibrated observations (GSD ~0.28 m).
   - **TMC-2 (Terrain Mapping Camera-2)**: Stereo triplet or calibrated nadir strip (GSD ~5 m).
   - **IIRS (Imaging Infra-Red Spectrometer)**: Hyperspectral SWIR cube (GSD ~80 m, 256 bands).
4. Download the product bundles (XML label file and corresponding `.tif` / `.img` raster).
5. Place downloaded files into `data/pradan/` (or any local directory):
   ```
   data/pradan/
   ├── ch2_ohr_ncp_20200815t041012_d_img.xml
   ├── ch2_ohr_ncp_20200815t041012_d_img.tif
   ├── ch2_tmc_ncn_20200815t041015_d_img.xml
   └── ch2_tmc_ncn_20200815t041015_d_img.tif
   ```

### Step 2: Index Products via REST API or UI
Scan local directory to register products into catalog:
```bash
# Direct API call to FastAPI (Port 8000)
curl -X POST "http://localhost:8000/api/v1/catalog/scan" -F "directory_path=data/pradan" -F "data_category=AUTHENTIC_CH2_PRADAN"

# Or through Spring Boot (Port 8080)
curl -X POST "http://localhost:8080/api/v1/pradan/scan?directoryPath=data/pradan"
```

### Step 3: Check Geographic Overlap
Validate that two products observe the same lunar surface region:
```bash
curl -X POST "http://localhost:8000/api/v1/overlap/check" \
  -F "reference_id=ch2_tmc_ncn_20200815t041015_d_img" \
  -F "moving_id=ch2_ohr_ncp_20200815t041012_d_img"
```
**Example Response**:
```json
{
  "is_valid_pair": true,
  "has_overlap": true,
  "overlap_status": "CONFIRMED_OVERLAP",
  "overlap_percentage_ref": 8.42,
  "overlap_percentage_mov": 100.0,
  "scale_disparity_ratio": 17.86,
  "reason": "Geographic footprints intersect: 8.42% of Reference and 100.0% of Moving frame intersect. Extreme scale disparity (17.86x) detected; will invoke multi-scale pyramid.",
  "reference_product_id": "ch2_tmc_ncn_20200815t041015_d_img",
  "moving_product_id": "ch2_ohr_ncp_20200815t041012_d_img"
}
```

### Step 4: Run Multi-Modal Registration
Execute registration via the interactive UI at `http://localhost:3000` or via REST API:
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "source_file=@data/pradan/ch2_ohr_ncp_20200815t041012_d_img.tif" \
  -F "reference_file=@data/pradan/ch2_tmc_ncn_20200815t041015_d_img.tif" \
  -F "algorithm=Proposed_Method" \
  -F "transformation_model=HOMOGRAPHY" \
  -F "enable_subpixel=true" \
  -F "enable_spatial_filter=true" \
  -F "data_category=AUTHENTIC_CH2_PRADAN"
```

---

## Supported Sensor Combinations (3-Phase Architecture)

1. **Phase 1: OHRC &harr; TMC-2** *(Operational Priority)*
   - Scale disparity: $1:16$ to $1:20$
   - Strategy: Multi-scale Gaussian-Laplacian pyramid bridge, structural phase congruency, stereo angle equalization.
2. **Phase 2: OHRC &harr; IIRS**
   - Scale disparity: Up to $1:300$
   - Strategy: Hyperspectral SWIR continuum band reduction, dead-pixel median filtering, phase congruency.
3. **Phase 3: TMC-2 &harr; IIRS**
   - Scale disparity: $1:16$
   - Strategy: Spectral alignment, local contrast enhancement (CLAHE), structural matching.

---

## Ground Truth vs. Residual Error Reporting

LUNARIS-X strictly separates **inlier reprojection residuals** from **analytical ground-truth errors**:
- When testing on synthetic benchmark pairs with known homographies:
  - `rmse_ground_truth`: Evaluated against analytical ground truth matrix.
  - `ground_truth_status`: `AVAILABLE`.
- When processing real PRADAN flight observations:
  - External analytical ground truth is unavailable.
  - `rmse_ground_truth`: `null`.
  - `ground_truth_status`: `NOT_AVAILABLE`.
  - System reports measured internal consistency metrics: inlier count, consensus ratio, inlier reprojection RMSE, sub-pixel residual distribution, and spatial Gini dispersion.

---

## Quickstart & Service Launch

### 1. Launch All Distributed Microservices
```cmd
start_all_services.bat
```
This automatically:
- Checks and frees ports `8000`, `8080`, and `3000`.
- Starts the Python 3.13 FastAPI engine (`http://localhost:8000`).
- Starts the Java 21 Spring Boot backend (`http://localhost:8080`).
- Starts the React 18 + Vite frontend (`http://localhost:3000`).
- Runs `scripts/wait_for_services.py` with real-time health-check polling.

### 2. Verify Complete Test Suites
```bash
# Python CV/ML Test Suite (38 tests)
py -3.13 -m pytest tests/

# Java Spring Boot Test Suite (18 tests)
cd backend && mvn test

# React Frontend Test Suite (9 tests)
cd frontend && npm test
```
**All 65 automated tests pass with 0 failures.**

### 3. Graceful Shutdown
```cmd
stop_all_services.bat
```

---

## System Endpoints

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **Spring Boot API & Swagger**: [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Health Check**: `GET http://localhost:8000/api/v1/health`
- **PRADAN Catalog Scan**: `POST http://localhost:8000/api/v1/catalog/scan`
- **Geographic Overlap Check**: `POST http://localhost:8000/api/v1/overlap/check`
- **Reference Selection**: `POST http://localhost:8000/api/v1/reference/select`

---

## License & Attribution

Developed for **Smart India Hackathon (SIH 2026)** &mdash; Problem Statement **SIH26166**.  
Indian Space Research Organisation (ISRO) &bull; Space Applications Centre (SAC).
