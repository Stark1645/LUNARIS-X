# Data Provenance, Traceability & Ingestion Architecture

## 1. Provenance Philosophy
To prevent data contamination, accidental misrepresentation of synthetic data, or loss of scientific ephemeris metadata, every image processed by our system generates an immutable JSON provenance record adhering to Schema v1.1.

---

## 2. Provenance Schema v1.1 Specification

```json
{
  "provenance_schema_version": "1.1",
  "timestamp_created_utc": "2026-09-01T00:00:00Z",
  "data_category": "SYNTHETIC_BENCHMARK | AUTHENTIC_CH2_PRADAN | AUTHENTIC_EXTERNAL_PDS | TEST_FIXTURE",
  "is_synthetic": true,
  "product_id": "PRODUCT_IDENTIFIER_STRING",
  "instrument_id": "CH2_OHRC | CH2_TMC2 | CH2_IIRS | LRO_NAC | SELENE_TC",
  "target_name": "Moon",
  "acquisition_time_utc": "ISO-8601 Timestamp",
  "solar_geometry": {
    "sun_azimuth_deg": 45.0,
    "incidence_angle_deg": 60.0,
    "emission_angle_deg": 0.0,
    "phase_angle_deg": 60.0
  },
  "spatial_bounds": {
    "min_lat": -85.0,
    "max_lat": -84.0,
    "min_lon": 20.0,
    "max_lon": 22.0,
    "gsd_m": 0.28
  },
  "projection": "Moon 2000 IAU / Simple Cylindrical",
  "file_integrity": {
    "image_filename": "image_1.png",
    "image_path": "data/benchmark/suite_b_sun_angle/pair_02_sun_angle_90deg/image_1.png",
    "sha256_checksum": "HEX_SHA256_64_CHARS",
    "file_size_bytes": 1048576,
    "raw_label_path": "data/benchmark/suite_b_sun_angle/pair_02_sun_angle_90deg/ground_truth.json"
  },
  "source_provenance": {
    "source_portal": "URL or internal generator identifier",
    "license_type": "ISRO Open Science Data Policy / Open Research",
    "notes": "Detailed description of product origin"
  }
}
```

---

## 3. Incorporation of Authentic Chandrayaan-2 Flight Data
When authentic Chandrayaan-2 datasets are downloaded from the ISSDC PRADAN portal via the manual Standard Operating Procedure:
1. User places downloaded `.xml` and `.tif` files into `data/raw/ohrc/`, `data/raw/tmc2/`, or `data/raw/iirs/`.
2. The ingestion pipeline `src.dataset.ingest_pipeline` runs:
   ```bash
   py -3.13 -m src.dataset.ingest_pipeline --input data/raw/ --catalog data/raw_catalog.json
   ```
3. The parser extracts PDS4 observational geometry, computes SHA-256 checksums, marks `data_category = "AUTHENTIC_CH2_PRADAN"` and `is_synthetic = false`, and records them in `data/raw_catalog.json`.
