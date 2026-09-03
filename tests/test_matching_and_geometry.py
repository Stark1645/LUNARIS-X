"""
Unit Tests for Matching and Geometric Verification Modules.
"""

import numpy as np
import pytest
from src.features.sift.sift_detector import SIFTDetector
from src.matching.matcher import FeatureMatcher
from src.geometry.models import TransformationType, TransformationEstimator
from src.geometry.verifier import RobustGeometricVerifier
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator


@pytest.fixture
def synthetic_pair():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=15, seed=101)
    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=45.0, sun_azimuth_2=48.0, incidence_1=40.0, incidence_2=40.0,
        rotation_deg=5.0, translation_px=(10.0, -5.0)
    )
    return img1, img2, H_gt


def test_feature_matching_and_ratio_test(synthetic_pair):
    img1, img2, H_gt = synthetic_pair
    sift = SIFTDetector(nfeatures=500)
    kps1, desc1 = sift.detect_and_compute(img1)
    kps2, desc2 = sift.detect_and_compute(img2)

    matcher = FeatureMatcher(ratio_threshold=0.80, cross_check=True)
    res = matcher.match(kps1, desc1, kps2, desc2)

    assert res.filtered_matches_count > 0
    assert len(res.source_points) == res.filtered_matches_count
    assert len(res.reference_points) == res.filtered_matches_count


def test_robust_geometric_verification_inlier_separation(synthetic_pair):
    img1, img2, H_gt = synthetic_pair
    sift = SIFTDetector(nfeatures=500)
    kps1, desc1 = sift.detect_and_compute(img1)
    kps2, desc2 = sift.detect_and_compute(img2)

    matcher = FeatureMatcher(ratio_threshold=0.80, cross_check=True)
    match_res = matcher.match(kps1, desc1, kps2, desc2)

    verifier = RobustGeometricVerifier(ransac_threshold=3.0)
    geom_res = verifier.verify(match_res.source_points, match_res.reference_points, preferred_model=TransformationType.HOMOGRAPHY)

    assert geom_res.is_valid is True
    assert geom_res.inlier_count >= 4
    assert len(geom_res.inlier_src_points) == geom_res.inlier_count
    assert len(geom_res.outlier_src_points) == geom_res.outlier_count
    assert geom_res.inlier_ratio > 0.0
    assert geom_res.mean_rmse < 3.0  # Reprojection error within RANSAC threshold


def test_transformation_models_estimation():
    # True affine transform: Rotation 30 deg + Translation (20, 15)
    theta = np.deg2rad(30.0)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    H_true = np.array([
        [cos_t, -sin_t, 20.0],
        [sin_t,  cos_t, 15.0],
        [0.0,    0.0,   1.0]
    ], dtype=np.float64)

    src_pts = np.array([
        [50.0, 50.0],
        [150.0, 50.0],
        [150.0, 150.0],
        [50.0, 150.0]
    ], dtype=np.float32)

    ref_pts = TransformationEstimator.transform_points(src_pts, H_true)

    # Test Homography fit
    H_est, stats = TransformationEstimator.estimate_model(src_pts, ref_pts, TransformationType.HOMOGRAPHY)
    assert H_est is not None
    pred_ref = TransformationEstimator.transform_points(src_pts, H_est)
    err = np.max(np.abs(ref_pts - pred_ref))
    assert err < 1e-3, f"Transformation estimation error {err} too high"
