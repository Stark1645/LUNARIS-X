# LUNARIS-X (SIH26166)
### Multi-Modal, Sun Angle & Scale-Invariant Lunar Image Registration Platform
**Indian Space Research Organisation (ISRO) | Smart India Hackathon 2026**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Java](https://img.shields.io/badge/Java-21-orange.svg?logo=openjdk)](https://openjdk.org)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.3+-6DB33F.svg?logo=springboot)](https://spring.io/projects/spring-boot)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg?logo=vite)](https://vitejs.dev)

---

## Overview

**LUNARIS-X** is an end-to-end, multi-tier distributed platform engineered for high-precision autonomous co-registration and landmark correspondence of Chandrayaan-2 lunar orbiter observations across diverse optical sensors (**OHRC**, **TMC-2**, and **IIRS**).

Co-registering multi-temporal lunar surface imagery poses extreme computer vision challenges:
1. **Extreme Sun Angle & Illumination Invariance**: Solar incidence variations ($\Delta\phi_\odot \approx 180^\circ$) cause crater shadow inversions where gradient-based detectors fail.
2. **Severe Scale Disparities**: Massive scale jumps ($1:16$ to $1:20$ between TMC-2 and OHRC; up to $1:800$ between IIRS and OHRC).
3. **Multi-Modal Radiometry**: Panchromatic visible imagery vs. hyperspectral SWIR absorption bands with non-linear radiometric inversions.
4. **Sub-Pixel Geometric Accuracy**: Outlier filtering and transformation modeling producing $\text{RMSE} < 1.0\text{ px}$.

---

## System Architecture

```
                       +-----------------------------------+
                       |         React 18 + Vite UI        |
                       |    (Port 3000 | TypeScript)       |
                       +-----------------+-----------------+
                                         |
                                         | REST / Multipart
                                         v
                       +-----------------------------------+
                       |    Java 21 Spring Boot 3 Core     |
                       |    (Port 8080 | Enterprise API)   |
                       +-----------------+-----------------+
                                         |
                                         | HTTP / JSON IPC
                                         v
                       +-----------------------------------+
                       |     Python 3.13 FastAPI ML        |
                       |   (Port 8000 | CV Algorithms)     |
                       +-----------------------------------+
```

### 1. Python ML Service (`/src`) &mdash; Port 8000
- **Proposed Method**: Multi-scale Phase Congruency, RIFT (Radiation-Invariant Feature Transform), LoFTR deep correspondence, adaptive Harris corners.
- **Outlier Filtering**: MAGSAC++ / RANSAC with spatial bucketing to guarantee uniform landmark coverage across maria and highlands.
- **Transformation Estimation**: Sub-pixel Affine, Homography, and Thin-Plate Spline (TPS) with residual verification.

### 2. Spring Boot 3 Backend (`/backend`) &mdash; Port 8080
- **Orchestration**: Asynchronous registration job workflows, task persistence, storage abstraction, and system health status.
- **Documentation**: Interactive OpenAPI 3 / Swagger documentation at `/swagger-ui.html`.

### 3. React Frontend (`/frontend`) &mdash; Port 3000
- **Visualization**: Dual-canvas interactive correspondence visualizer, inlier/outlier vector plots, error heatmap overlays, and performance benchmark dashboard.

---

## Repository Structure

```
.
├── backend/                  # Java 21 Spring Boot 3 Backend Service
│   ├── pom.xml               # Maven configuration
│   └── src/                  # Controllers, services, models, repositories
├── data/                     # Benchmark and evaluation datasets
│   ├── benchmark/            # 5 synthetic & real test suites (A through E)
│   └── demo/                 # Curated demo pairs for live presentations
├── docs/                     # 37+ technical specifications & research papers
│   ├── architecture.md       # Full architectural breakdown
│   ├── problem_statement.md  # Scientific objectives & lunar optics physics
│   ├── proposed_method.md    # Mathematical derivation of proposed method
│   └── ...
├── frontend/                 # React 18 + TypeScript + Vite UI
│   ├── package.json          # Node dependencies
│   └── src/                  # Components, hooks, services, state management
├── results/                  # Validation logs, benchmark metrics & visual outputs
├── scripts/                  # Automation & orchestration utilities
│   └── wait_for_services.py  # Health-check polling script for all microservices
├── src/                      # Python 3.13 CV / ML Microservice
│   ├── api/                  # FastAPI routes & DTOs
│   ├── features/             # SIFT, RIFT, Phase Congruency detectors
│   ├── geometry/             # Homography, Affine, residual estimators
│   ├── matching/             # Keypoint matchers & ratio tests
│   └── registration/         # End-to-end registration pipeline
├── tests/                    # Python unit and integration test suite
├── start_all_services.bat    # One-click multi-tier Windows launcher
└── stop_all_services.bat     # Clean termination script for all background ports
```

---

## Quickstart

### Prerequisites
- **Python**: 3.13+ (`py -3.13` launcher recommended)
- **Java**: JDK 21+ with Maven 3.9+
- **Node.js**: 18+ with `npm`

### One-Click Launch (Windows)
```cmd
start_all_services.bat
```
This script frees ports (8000, 8080, 3000), starts the three services in dedicated consoles, monitors startup health, and launches your browser to `http://localhost:3000`.

### Manual Launch

1. **Start Python ML Service (Port 8000)**:
   ```bash
   py -3.13 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
   ```
2. **Start Spring Boot Backend (Port 8080)**:
   ```bash
   cd backend
   mvn spring-boot:run
   ```
3. **Start React Frontend (Port 3000)**:
   ```bash
   cd frontend
   npm run dev
   ```

### Stopping Services
```cmd
stop_all_services.bat
```

---

## Endpoints & API Docs

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend UI** | `http://localhost:3000` | Interactive Lunar Registration Dashboard |
| **Spring Boot API** | `http://localhost:8080/api/v1/health` | Backend Health & Microservice Status |
| **Swagger UI** | `http://localhost:8080/swagger-ui.html` | Interactive REST API Documentation |
| **Python ML Docs** | `http://localhost:8000/docs` | FastAPI Swagger Interface |

---

## License & Attribution

Developed for **Smart India Hackathon 2026** (Problem Statement: **SIH26166**) in collaboration with the **Indian Space Research Organisation (ISRO)**.
