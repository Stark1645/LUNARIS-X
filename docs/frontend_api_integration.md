# SIH 2026 (SIH26166) — Frontend-to-Backend API Integration Specification

This document defines the REST communication contract between the React 18 frontend and the Spring Boot 3 backend on `http://localhost:8080/api/v1`.

---

## 1. Endpoints & Integration Methods

```
+----------------------------------------------------------------------------------------------------+
| REACT FRONTEND (:3000)       | SPRING BOOT 3 REST BACKEND (:8080)     | PYTHON FASTAPI ML ENGINE   |
+------------------------------+----------------------------------------+----------------------------+
| apiService.getHealth()       | GET /api/v1/health                     | GET /api/v1/health         |
|                              | -> Returns health of DB + Python ML    | -> Liveness & Backends     |
|                              |                                        |                            |
| apiService.uploadImage()     | POST /api/v1/images/upload             | (None - Stored in backend  |
|                              | -> Multipart upload with SHA-256       |  disk storage)             |
|                              |                                        |                            |
| apiService.submitRegistration| POST /api/v1/jobs/register             | POST /api/v1/register      |
|                              | -> Submits Source + Ref IDs, algorithm | -> Multi-Scale Registration|
|                              |    and threshold configuration         |    Engine execution        |
|                              |                                        |                            |
| apiService.getAllExperiments | GET /api/v1/experiments                | (None - Read from MySQL    |
|                              | -> Retrieves Ch-2-MatchBench records   |  experiments table)        |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. API Error Handling & Resilience

The frontend parses RFC 7807 error responses using `parseApiError(err)` in `src/services/api.ts`:
- **400 Bad Request**: Displays specific validation error strings (e.g. unsupported file format, missing source image ID).
- **413 Payload Too Large**: Displays `"Uploaded file size exceeds the configured maximum limit (100MB)"`.
- **404 Not Found**: Displays entity missing message.
- **503 Service Unavailable**: Displays `"Failed to communicate with Python ML Service"`.
- **Network Disconnection**: Displays informative fallback state without crashing the UI.
