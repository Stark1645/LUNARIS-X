# SIH 2026 (SIH26166) — REST API Specification

**Base URL**: `http://localhost:8080`  
**OpenAPI / Swagger UI**: `http://localhost:8080/swagger-ui.html`  
**OpenAPI JSON Docs**: `http://localhost:8080/v3/api-docs`  
**Content-Type**: `application/json` (unless specified as `multipart/form-data`)

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Request Body / Params | Response Codes |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/images/upload` | Uploads a lunar optical/reference image and computes SHA-256 hash | `multipart/form-data` (`file`, `sensor_name`, `mission_name`, `gsd_meters`, `data_category`) | `201 CREATED`, `400 BAD_REQUEST`, `413 PAYLOAD_TOO_LARGE` |
| `GET` | `/api/v1/images` | Lists all uploaded images with metadata | None | `200 OK` |
| `GET` | `/api/v1/images/{id}` | Retrieves metadata and cryptographic checksum for a specific image | Path variable: `id` (Long) | `200 OK`, `404 NOT_FOUND` |
| `POST` | `/api/v1/jobs/register` | Submits and executes a registration job between source and reference image IDs | JSON `RegistrationRequestDTO` | `200 OK`, `400 BAD_REQUEST`, `404 NOT_FOUND`, `503 SERVICE_UNAVAILABLE` |
| `GET` | `/api/v1/jobs` | Lists all registration jobs and status | None | `200 OK` |
| `GET` | `/api/v1/jobs/{id}` | Retrieves full metrics, transformation matrix, and visual products for a specific job | Path variable: `id` (Long) | `200 OK`, `404 NOT_FOUND` |
| `GET` | `/api/v1/experiments` | Lists all baseline and ablation experiment evaluation records | None | `200 OK` |
| `GET` | `/api/v1/experiments/suite/{suiteName}` | Filters experiment logs by benchmark suite name | Path variable: `suiteName` (String) | `200 OK` |
| `GET` | `/api/v1/health` | Multi-tier health check for Backend, MySQL, and Python ML service | None | `200 OK` |

---

## 2. Request & Response Payload Examples

### 2.1 Submit Registration Job (`POST /api/v1/jobs/register`)
**Request Body**:
```json
{
  "sourceImageId": 1,
  "referenceImageId": 2,
  "algorithm": "Proposed_Method",
  "transformationModel": "HOMOGRAPHY",
  "ratioThreshold": 0.80,
  "ransacThreshold": 3.0,
  "enableSubpixel": true,
  "enableSpatialFilter": true
}
```

**Response Body (200 OK)**:
```json
{
  "jobId": 101,
  "status": "SUCCESS",
  "algorithm": "Proposed_Method",
  "selectedTransformationModel": "HOMOGRAPHY",
  "transformationMatrixJson": "[[1.002, -0.001, 5.23], [0.001, 0.998, -3.11], [0.0, 0.0, 1.0]]",
  "sourceImageId": 1,
  "referenceImageId": 2,
  "sourceFilename": "ch2_tmc2_orbit100.png",
  "referenceFilename": "ch2_ohrc_ref_tile.png",
  "metrics": {
    "candidateMatchesCount": 95,
    "inlierMatchesCount": 87,
    "inlierRatioPercent": 91.58,
    "rmseInliersPx": 1.27,
    "rmseGroundTruthPx": 0.41,
    "meanSubpixelResidualPx": 0.22,
    "subpixelAccuracyRate05px": 0.88,
    "spatialGiniCoefficient": 0.32,
    "latencyMs": 390.0,
    "dataCategory": "SYNTHETIC_BENCHMARK"
  },
  "warpedImageBase64": "data:image/png;base64,...",
  "matchVisBase64": "data:image/png;base64,...",
  "alphaOverlayBase64": "data:image/png;base64,...",
  "checkerboardBase64": "data:image/png;base64,...",
  "differenceMapBase64": "data:image/png;base64,...",
  "createdAt": "2026-09-02T20:25:00",
  "completedAt": "2026-09-02T20:25:01"
}
```

---

## 3. Standardized Error Response Model (RFC 7807)

```json
{
  "timestamp": "2026-09-02T20:25:30",
  "status": 400,
  "error": "Validation Failed",
  "message": "Input argument validation failed",
  "path": "/api/v1/jobs/register",
  "validationErrors": [
    "sourceImageId: Source image ID must not be null"
  ]
}
```
