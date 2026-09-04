# LUNARIS-X (SIH26166) — Demonstration Readiness Guide & Evaluation Checklist

**Project Title**: LUNARIS-X — Multi-Modal, Sun-Angle and Scale-Invariant Lunar Image Correspondence & Registration Engine  
**Readiness Status**: $\mathbf{READY\ FOR\ SIH\ DEMONSTRATION}$  
**Target Jury / Stakeholders**: ISRO / Smart India Hackathon Evaluators  

---

## 1. Executive Demonstration Checklist

| System Component | Verification Status | Live Demonstration Feature |
| :--- | :---: | :--- |
| **Python ML Service** | `VERIFIED (Port 8000)` | AMSR Phase Congruency, Scale Pyramid Bridge, Spatial RANSAC, Sub-Pixel Refinement. |
| **Spring Boot Backend** | `VERIFIED (Port 8080)` | Multipart Uploads, SHA-256 Hashes, Job Lifecycle, Metric Marshalling, JPA Repositories. |
| **MySQL Database** | `VERIFIED (Port 3306)` | `lunar_registration_db` tables (`images`, `registration_jobs`, `registration_metrics`, `match_points`). |
| **React 18+ Frontend** | `VERIFIED (Port 3000)` | Drag-and-drop workspace, Alpha Slider, 8x8 Checkerboard, Difference Heatmap, CSV Exporter. |
| **Automated Tests** | `54/54 PASSED (100%)` | Pytest (27 tests), JUnit 5 (18 tests), Vitest (9 tests), Vite Production Build (0 errors). |

---

## 2. Recommended Live Demonstration Flow (5-Minute Walkthrough)

### Step 1: System Overview & Health (`Tab 3: System Health`)
1. Open `http://localhost:3000` and switch to the **System Health** tab.
2. Highlight the multi-tier microservices architecture:
   - Spring Boot 3 on Java 21 LTS (Port 8080)
   - Python 3.13 FastAPI Registration Engine (Port 8000)
   - MySQL 8.0 Persistence Layer (Port 3306)
   - Point to Swagger UI (`http://localhost:8080/swagger-ui.html`) for interactive OpenAPI documentation.

### Step 2: Challenge 1 — $180^\circ$ Solar Azimuth & Shadow Reversal (`pair_03`)
1. Switch to **Registration Workspace** (`Tab 1`).
2. Upload `data/benchmark/suite_b_sun_angle/pair_03_sun_angle_180deg/image_1.png` as **Source (Moving Image)**.
3. Upload `image_2.png` from the same folder as **Reference (Fixed Image)**.
4. Note the cryptographic SHA-256 display and explicit role badges.
5. Select **Proposed Method (AMSR)** $\to$ Click **Execute Registration**.
6. Show results:
   - Explain how Log-Gabor structural energy and shadow-boundary suppression recovered **12 verified inliers** ($\text{RMSE} = 1.77\text{ px}$) where classical SIFT produced 0 inliers.
   - Switch between **Alpha Overlay** (slide opacity from 0% to 100%), **8x8 Checkerboard** (inspect crater rim alignment), and **Difference Heatmap**.

### Step 3: Challenge 2 — Cross-Modal SWIR to Panchromatic Transfer (`pair_07`)
1. Upload `data/benchmark/suite_d_cross_modal/pair_07_cross_modal_swir_pan/image_1.png` and `image_2.png`.
2. Click **Execute Registration**.
3. Point out **166 verified inliers** ($\text{IR} = 79.0\%$, $\text{RMSE} = 1.56\text{ px}, G_k = 0.43$) demonstrating invariance to non-linear intensity mappings.

### Step 4: Challenge 3 — $20\times$ Extreme Scale Disparity (`pair_06`)
1. Upload `data/benchmark/suite_c_scale_disparity/pair_06_scale_20x_tmc2_ohrc/image_1.png` and `image_2.png`.
2. Execute registration and demonstrate how the **Dynamic Model Selector** automatically stabilized on a 6-DOF Affine transformation ($\text{RMSE} = 1.05\text{ px}$) to prevent planar overfitting on sparse samples.

### Step 5: Benchmark & Scientific Integrity (`Tab 2: Benchmark Registry`)
1. Switch to **Benchmark Registry**.
2. Filter across Suites A through E.
3. Highlight that experimental diagnostic criteria ($G_k \le 0.65$) are separated from specification targets ($G_k < 0.35$).
4. Export the complete experiment catalog to CSV.

---

## 3. Known Limitations & Research Boundaries

1. **Orthogonal Illumination Disparity ($90^\circ$)**: When solar illumination is shifted by exactly $90^\circ$ (`pair_02`), shadow boundaries deform orthogonally to surface gradient edges. AMSR detects the difficulty and degrades gracefully rather than outputting false correspondences.
2. **Dense Crater Repetitive Highlands (`pair_09`)**: High density of self-similar craters can create ambiguity in descriptor matching.
3. **Execution Latency**: Phase congruency filter bank convolution (4 scales $\times$ 6 orientations 2D FFT) requires $\sim 5-10\text{ seconds}$ per $512\times 512$ tile on CPU without dedicated GPU acceleration.
4. **Authentic Flight Data**: Native PDS4 orbital archives (`AUTHENTIC_CH2_PRADAN`) are not bundled locally; all benchmarks are evaluated on the controlled `SYNTHETIC_BENCHMARK` suite.

---

## 4. Exact Launch Commands

```bash
# 1. Start Python FastAPI ML Engine
py -3.13 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 2. Start Spring Boot 3 Backend
cd backend && mvn spring-boot:run

# 3. Start React 18+ Frontend
cd frontend && npm run dev
```
Access UI at `http://localhost:3000`.
