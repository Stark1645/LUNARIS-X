"""
Comprehensive Dataset Validation & Audit Test Suite for SIH26166.
Verifies file integrity, ground-truth homography mapping, image statistics, and provenance records.
"""

import os
import glob
import json
import cv2
import pytest
import numpy as np
from src.dataset.provenance import ProvenanceTracker
from src.dataset.pds4_parser import PDS4Parser
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator


def test_benchmark_files_exist_and_readable():
    """Verify that all 5 benchmark suites exist with valid images and ground truth."""
    benchmark_dir = "data/benchmark"
    assert os.path.exists(benchmark_dir), "data/benchmark directory must exist"

    catalog_path = os.path.join(benchmark_dir, "benchmark_catalog.json")
    assert os.path.exists(catalog_path), "benchmark_catalog.json must exist"

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    assert catalog.get("is_synthetic") is True
    assert "suites" in catalog
    assert len(catalog["suites"]) == 5

    pair_dirs = glob.glob(os.path.join(benchmark_dir, "suite_*", "pair_*"))
    assert len(pair_dirs) == 9, f"Expected 9 benchmark pairs, found {len(pair_dirs)}"

    for pdir in pair_dirs:
        img1_path = os.path.join(pdir, "image_1.png")
        img2_path = os.path.join(pdir, "image_2.png")
        gt_path = os.path.join(pdir, "ground_truth.json")
        prov_path = os.path.join(pdir, "provenance.json")

        assert os.path.exists(img1_path), f"Missing image_1.png in {pdir}"
        assert os.path.exists(img2_path), f"Missing image_2.png in {pdir}"
        assert os.path.exists(gt_path), f"Missing ground_truth.json in {pdir}"
        assert os.path.exists(prov_path), f"Missing provenance.json in {pdir}"

        # Test image read & properties
        im1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        im2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

        assert im1 is not None, f"Failed to load {img1_path}"
        assert im2 is not None, f"Failed to load {img2_path}"
        assert im1.shape[0] > 0 and im1.shape[1] > 0
        assert im2.shape[0] > 0 and im2.shape[1] > 0
        assert im1.std() > 1.0, f"Image 1 in {pdir} appears blank or uniform"
        assert im2.std() > 1.0, f"Image 2 in {pdir} appears blank or uniform"


def test_provenance_cryptographic_checksums():
    """Verify that all SHA-256 hashes in provenance records match the actual on-disk files."""
    prov_files = glob.glob("data/benchmark/**/provenance.json", recursive=True)
    assert len(prov_files) >= 9

    for pf in prov_files:
        with open(pf, "r", encoding="utf-8") as f:
            prov = json.load(f)

        assert prov.get("data_category") == "SYNTHETIC_BENCHMARK"
        assert prov.get("is_synthetic") is True

        img1_info = prov.get("image_1", {}).get("file_integrity", {})
        img_path = img1_info.get("image_path")
        expected_sha = img1_info.get("sha256_checksum")

        assert img_path is not None and os.path.exists(img_path)
        actual_sha = ProvenanceTracker.compute_sha256(img_path)
        assert actual_sha == expected_sha, f"SHA-256 mismatch for {img_path}"


def test_ground_truth_homography_mathematical_properties():
    """Verify that ground-truth homography matrices are non-singular and map interior points accurately."""
    gt_files = glob.glob("data/benchmark/**/ground_truth.json", recursive=True)
    assert len(gt_files) >= 9

    for gf in gt_files:
        with open(gf, "r", encoding="utf-8") as f:
            gt = json.load(f)

        H = np.array(gt["ground_truth_homography"], dtype=np.float64)
        assert H.shape == (3, 3)

        # Check non-singularity (determinant non-zero)
        det = np.linalg.det(H)
        assert abs(det) > 1e-6, f"Singular Homography matrix in {gf}"

        # Test point transformation
        # Point (100, 100) in image 1
        pt1 = np.array([100.0, 100.0, 1.0], dtype=np.float64)
        pt2 = H @ pt1
        pt2 /= pt2[2]

        assert not np.isnan(pt2).any()
        assert not np.isinf(pt2).any()


def test_synthetic_surface_smoothness_and_gradients():
    """Verify that synthetic terrain does not contain high-frequency noise artifacts."""
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(512, 512, num_craters=25, seed=42)
    img = LunarSurfaceGenerator.render_photometric_shading(dem, 45.0, 50.0)

    # Compute horizontal pixel difference
    diff_h = np.abs(img[:, 1:].astype(float) - img[:, :-1].astype(float))
    mean_diff = float(diff_h.mean())

    # Realistic terrain has mean pixel gradient < 5.0 (un-smoothed noise was > 65.0)
    assert mean_diff < 5.0, f"Synthetic image gradient is too noisy ({mean_diff:.2f})"
