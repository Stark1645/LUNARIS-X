# LUNARIS-X (SIH26166) — Enterprise Backend Architecture

**Backend Technology Stack**: Java 21 LTS, Spring Boot 3.3.2, Spring Data JPA, Hibernate 6, MySQL 8.0, Springdoc OpenAPI 3.  
**Microservice Integration**: Python 3.13 FastAPI Registration ML Microservice (`http://localhost:8000`).  
**Design Pattern**: Layered Enterprise Architecture (Controller $\to$ Service $\to$ Repository / Persistence $\to$ Python ML Client).

---

## 1. System Context & Layered Architecture

```
+===================================================================================================================+
|                                    ENTERPRISE SYSTEM ARCHITECTURE (SIH26166)                                      |
+===================================================================================================================+

  [ WEB CLIENT / REACT SPA ]                   [ EXTERNAL DATA SOURCES / ISRO PRADAN ]
             |                                                    |
             | HTTP (JSON / Multipart)                            | GeoTIFF / XML Ingest
             v                                                    v
+-------------------------------------------------------------------------------------------------------------------+
| SPRING BOOT 3 REST SERVICE LAYER (PORT 8080)                                                                      |
|                                                                                                                   |
|  +------------------------+  +------------------------+  +------------------------+  +------------------------+   |
|  |    ImageController     |  |RegistrationJobControl'r|  |  ExperimentController  |  |    HealthController    |   |
|  | /api/v1/images/upload  |  | /api/v1/jobs/register  |  | /api/v1/experiments    |  | /api/v1/health         |   |
|  +-----------+------------+  +-----------+------------+  +-----------+------------+  +-----------+------------+   |
|              |                           |                           |                           |                |
|              v                           v                           v                           v                |
|  +------------------------+  +------------------------+  +------------------------+  +------------------------+   |
|  |  ImageStorageService   |  |  RegistrationService   |  |   ExperimentService    |  |  GlobalExceptionHandler|   |
|  | • SHA-256 Checksum     |  | • Job Lifecycle Mgmt   |  | • Benchmark Queries    |  | • Structured Errors    |   |
|  | • Path Traversal Check |  | • Result Marshalling   |  | • Ablation Records     |  | • Status Mapping       |   |
|  +-----------+------------+  +-----------+------------+  +-----------+------------+  +------------------------+   |
|              |                           |                           |                                            |
|              |                           v                           |                                            |
|              |               +------------------------+              |                                            |
|              |               | PythonMlClientService  |              |                                            |
|              |               | • Timeout Management   |              |                                            |
|              |               | • Multipart Streaming  |              |                                            |
|              |               +-----------+------------+              |                                            |
|              |                           |                           |                                            |
|              v                           |                           v                                            |
|  +---------------------------------------+----------------------------------------+                               |
|  | SPRING DATA JPA REPOSITORY LAYER                                               |                               |
|  | • ImageRepository             • RegistrationJobRepository                      |                               |
|  | • RegistrationMetricsRepo     • MatchPointRepository • ExperimentRepository    |                               |
|  +---------------------------------------+----------------------------------------+                               |
+------------------------------------------|----------------------------------------+-------------------------------+
                                           |                                        |
                   [MySQL Database Connection: 3306]             [REST / Multipart HTTP: 8000]
                                           |                                        |
                                           v                                        v
                            +-----------------------------+          +-----------------------------+
                            |      MySQL 8.0 RDBMS        |          |  PYTHON FASTAPI ML ENGINE   |
                            | • lunar_registration_db     |          | • AMSR Master Pipeline      |
                            | • images                    |          | • Multi-Scale Phase Match   |
                            | • registration_jobs         |          | • Spatial Coverage RANSAC   |
                            | • registration_metrics      |          | • Sub-Pixel Refinement      |
                            | • match_points              |          | • Image Warping Composites  |
                            | • experiments               |          +-----------------------------+
                            +-----------------------------+
```

---

## 2. Component Directory Structure

```
backend/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/org/sih/lunar/
    │   │   ├── LunarRegistrationApplication.java
    │   │   ├── config/
    │   │   │   ├── AppConfig.java              -> RestTemplate & Jackson ObjectMapper beans
    │   │   │   ├── CorsConfig.java             -> Cross-Origin Resource Sharing rules
    │   │   │   └── OpenApiConfig.java          -> Swagger OpenAPI 3 configuration
    │   │   ├── controller/
    │   │   │   ├── ImageController.java        -> /api/v1/images (Upload, List, Metadata)
    │   │   │   ├── RegistrationJobController.java -> /api/v1/jobs (Submit, Retrieve, List)
    │   │   │   ├── ExperimentController.java   -> /api/v1/experiments (Benchmark & Ablation records)
    │   │   │   └── HealthController.java       -> /api/v1/health (Multi-tier health status)
    │   │   ├── dto/
    │   │   │   ├── RegistrationRequestDTO.java -> Bean Validation inputs
    │   │   │   ├── RegistrationResponseDTO.java-> Output DTO with metrics and Base64 visuals
    │   │   │   ├── ImageUploadResponseDTO.java -> Image metadata & SHA-256 hash
    │   │   │   ├── MetricsDTO.java             -> Inlier RMSE, GT RMSE, Gini, Subpixel
    │   │   │   ├── MatchPointDTO.java          -> Spatial tie-point coordinates
    │   │   │   ├── JobStatusDTO.java           -> Lightweight status DTO
    │   │   │   ├── ErrorResponseDTO.java       -> RFC 7807 compliant error format
    │   │   │   └── HealthStatusDTO.java        -> Backend + Python + MySQL status
    │   │   ├── entity/
    │   │   │   ├── ImageEntity.java            -> Image metadata table
    │   │   │   ├── RegistrationJobEntity.java  -> Job state & model table
    │   │   │   ├── RegistrationMetricsEntity.java -> Scientific metrics table
    │   │   │   ├── MatchPointEntity.java       -> Correspondence point table
    │   │   │   └── ExperimentEntity.java       -> Benchmark run registry table
    │   │   ├── exception/
    │   │   │   ├── GlobalExceptionHandler.java -> Controller advice
    │   │   │   ├── ResourceNotFoundException.java
    │   │   │   ├── ValidationException.java
    │   │   │   └── PythonServiceUnavailableException.java
    │   │   ├── repository/
    │   │   │   ├── ImageRepository.java
    │   │   │   ├── RegistrationJobRepository.java
    │   │   │   ├── RegistrationMetricsRepository.java
    │   │   │   ├── MatchPointRepository.java
    │   │   │   └── ExperimentRepository.java
    │   │   └── service/
    │   │       ├── ImageStorageService.java    -> Safe file persistence & SHA-256
    │   │       ├── PythonMlClientService.java  -> REST client to Python engine
    │   │       ├── RegistrationService.java    -> Orchestration & transaction logic
    │   │       └── ExperimentService.java      -> Benchmark queries
    │   └── resources/
    │       └── application.yml                 -> Database, storage, and ML service config
    └── test/
        ├── java/org/sih/lunar/
        │   ├── LunarRegistrationApplicationTests.java
        │   ├── controller/
        │   │   ├── ImageControllerTest.java
        │   │   ├── RegistrationJobControllerTest.java
        │   │   └── HealthControllerTest.java
        │   ├── service/
        │   │   ├── ImageStorageServiceTest.java
        │   │   ├── PythonMlClientServiceTest.java
        │   │   ├── RegistrationServiceTest.java
        │   │   └── ExperimentServiceTest.java
        │   └── repository/
        │       └── RepositoryPersistenceTest.java
        └── resources/
            └── application-test.yml
```
