# SIH 2026 (SIH26166) — Frontend Architecture & UI Specification

**Frontend Technology Stack**: React 18.3.1, TypeScript 5.5, Vite 5.4, Lucide React, Axios, Vitest.  
**Target Environment**: Desktop-First Scientific Lunar Analysis Dashboard (Port 3000).  
**Communication Pipeline**: React (`:3000`) $\to$ Spring Boot 3 (`:8080`) $\to$ Python FastAPI (`:8000`) $\to$ MySQL 8.0 (`:3306`).

---

## 1. Component Hierarchy & Layout Tree

```
App (Root Orchestrator & Multi-Tier Health Poller)
├── Navbar (Branding, Live Engine Status Pill, Tab Navigation)
│
├── WorkspacePage (Tab 1: End-to-End Image Registration)
│   ├── ImageUploader [SOURCE / MOVING IMAGE] (TMC-2, GSD, Dropzone, Metadata, SHA-256)
│   ├── ImageUploader [REFERENCE / FIXED IMAGE] (OHRC / Basemap, Dropzone, Metadata, SHA-256)
│   ├── ConfigPanel (Algorithm Backend, Geometry Model, Lowe's Ratio, RANSAC Reprojection, Toggles)
│   ├── PipelineStepper (14-Stage Visual Execution Pipeline with Live Status)
│   ├── ComparisonViewer (Alpha Overlay Slider, 8x8 Checkerboard, Difference Heatmap, Side-by-Side)
│   └── ScientificMetricsPanel (Inlier Count, IR, Inlier RMSE, GT RMSE, Sub-Pixel Residual, Gini G_k, Matrix)
│
├── BenchmarksPage (Tab 2: Ch-2-MatchBench Registry)
│   └── BenchmarkExplorer (Suites A-E Filter, Algorithm Filter, Search, CSV Export, Status Badges)
│
└── SystemHealthPage (Tab 3: Microservices Diagnostic Dashboard)
    ├── Spring Boot 3 REST Tier Status Card (Port 8080)
    ├── Python ML Microservice Status Card (Port 8000)
    ├── MySQL 8.0 Persistence Tier Status Card (Port 3306)
    └── Supported Algorithm Backends Reference Card
```

---

## 2. Directory Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── src/
│   ├── App.tsx                         -> Main layout with persistent header & navigation
│   ├── main.tsx                        -> Application mount
│   ├── index.css                       -> Space-slate theme tokens, typography, badges, cards
│   ├── vite-env.d.ts                   -> Vite client type declarations
│   ├── types/
│   │   └── index.ts                    -> DTO interfaces matching Spring Boot and Python ML contracts
│   ├── services/
│   │   └── api.ts                      -> Axios REST client connecting to Spring Boot /api/v1/
│   ├── components/
│   │   ├── layout/
│   │   │   └── Navbar.tsx              -> Top navigation header with health pill
│   │   ├── upload/
│   │   │   └── ImageUploader.tsx       -> Drag-and-drop upload for Moving/Fixed frames
│   │   ├── registration/
│   │   │   └── ConfigPanel.tsx         -> Algorithm & transformation configuration
│   │   ├── pipeline/
│   │   │   └── PipelineStepper.tsx     -> 14-stage logical pipeline visualizer
│   │   ├── comparison/
│   │   │   └── ComparisonViewer.tsx    -> Alpha slider, Checkerboard, Difference, Side-by-Side
│   │   ├── metrics/
│   │   │   └── ScientificMetricsPanel.tsx -> Measured metrics grid & 3x3 matrix formatter
│   │   └── experiments/
│   │       └── BenchmarkExplorer.tsx   -> Ch-2-MatchBench multi-suite table & CSV exporter
│   ├── pages/
│   │   ├── WorkspacePage.tsx           -> Main interactive registration workspace
│   │   ├── BenchmarksPage.tsx          -> Benchmark registry page
│   │   └── SystemHealthPage.tsx        -> Microservices diagnostic dashboard
│   └── test/
│       ├── setup.ts                    -> Testing Library / Vitest setup
│       ├── App.test.tsx                -> Root UI rendering tests
│       ├── ImageUploader.test.tsx      -> Moving vs Fixed role tests
│       ├── ConfigPanel.test.tsx        -> Algorithm selection & submit tests
│       └── ScientificMetricsPanel.test.tsx -> Metric precision and N/A fallback tests
```

---

## 3. Coordinate System & Image Transformation Conventions

To maintain mathematical consistency across Python, Java, and React:
1. **Origin**: $(0,0)$ top-left corner of the image canvas.
2. **Horizontal Axis ($x$)**: Increases rightwards ($0 \le x < W$).
3. **Vertical Axis ($y$)**: Increases downwards ($0 \le y < H$).
4. **Moving vs Fixed Definition**:
   - **SOURCE = MOVING IMAGE**: The raw acquired frame (e.g. TMC-2 optical track).
   - **REFERENCE = FIXED IMAGE**: The stationary coordinate reference (e.g. OHRC / Lunar Basemap).
   - **WARPED SOURCE = REGISTERED PRODUCT**: The Source image resampled into the Reference coordinate frame using the estimated homography matrix $\mathbf{H}$.
