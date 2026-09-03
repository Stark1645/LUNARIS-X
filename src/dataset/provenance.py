"""
Provenance Tracking & Metadata Integrity Verification for SIH26166 Datasets.
Generates SHA-256 hashes, records acquisition parameters, and logs source traceability.
"""

import os
import hashlib
import json
import time
from typing import Dict, Any, Optional
from src.dataset.pds4_parser import PlanetaryMetadata


class ProvenanceTracker:
    """Manages immutable dataset provenance records and checksum validation."""

    @staticmethod
    def compute_sha256(file_path: str, block_size: int = 65536) -> str:
        """Computes SHA-256 hash of a file for integrity tracking."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha256.update(block)
        return sha256.hexdigest()

    @staticmethod
    def create_provenance_record(
        metadata: PlanetaryMetadata,
        image_path: str,
        source_url: str,
        data_category: str = "SYNTHETIC_BENCHMARK",
        is_synthetic: bool = True,
        license_type: str = "Open Research Dataset",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Creates a standardized provenance record dictionary."""
        file_hash = ProvenanceTracker.compute_sha256(image_path) if os.path.exists(image_path) else "N/A"
        file_size_bytes = os.path.getsize(image_path) if os.path.exists(image_path) else 0

        # Normalize path to forward slashes for cross-platform consistency
        norm_img_path = image_path.replace("\\", "/")
        norm_label_path = metadata.raw_label_path.replace("\\", "/")

        record = {
            "provenance_schema_version": "1.1",
            "timestamp_created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data_category": data_category,  # SYNTHETIC_BENCHMARK | AUTHENTIC_CH2_PRADAN | AUTHENTIC_EXTERNAL_PDS | TEST_FIXTURE
            "is_synthetic": is_synthetic,
            "product_id": metadata.product_id,
            "instrument_id": metadata.instrument_id,
            "target_name": metadata.target_name,
            "acquisition_time_utc": metadata.acquisition_time_utc,
            "solar_geometry": {
                "sun_azimuth_deg": metadata.solar_geometry.sun_azimuth_deg,
                "incidence_angle_deg": metadata.solar_geometry.incidence_angle_deg,
                "emission_angle_deg": metadata.solar_geometry.emission_angle_deg,
                "phase_angle_deg": metadata.solar_geometry.phase_angle_deg,
            },
            "spatial_bounds": {
                "min_lat": metadata.spatial_bounds.min_lat,
                "max_lat": metadata.spatial_bounds.max_lat,
                "min_lon": metadata.spatial_bounds.min_lon,
                "max_lon": metadata.spatial_bounds.max_lon,
                "gsd_m": metadata.spatial_bounds.gsd_m,
            },
            "projection": metadata.projection,
            "file_integrity": {
                "image_filename": os.path.basename(image_path),
                "image_path": norm_img_path,
                "sha256_checksum": file_hash,
                "file_size_bytes": file_size_bytes,
                "raw_label_path": norm_label_path,
            },
            "source_provenance": {
                "source_portal": source_url,
                "license_type": license_type,
                "notes": notes,
            }
        }
        return record

    @staticmethod
    def save_provenance_manifest(record: Dict[str, Any], output_json_path: str) -> None:
        """Saves provenance record to JSON manifest."""
        os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

    @staticmethod
    def verify_provenance_manifest(manifest_path: str) -> bool:
        """Verifies integrity of a dataset file against its stored manifest."""
        if not os.path.exists(manifest_path):
            return False

        with open(manifest_path, "r", encoding="utf-8") as f:
            record = json.load(f)

        img_path = record.get("file_integrity", {}).get("image_path")
        expected_hash = record.get("file_integrity", {}).get("sha256_checksum")

        if not img_path or not os.path.exists(img_path) or expected_hash == "N/A":
            return False

        actual_hash = ProvenanceTracker.compute_sha256(img_path)
        return actual_hash == expected_hash
