"""
Unit and Integration Tests for Proposed Method (AMSR).
"""

import numpy as np
import pytest
from src.proposed.condition_analyzer import ImagePairConditionAnalyzer
from src.proposed.structural_detector import StructuralFeatureDetector
from src.proposed.scale_pyramid_matcher import HierarchicalScalePyramidMatcher
from src.proposed.model_selector import DynamicModelSelector
from src.proposed.proposed_pipeline import ProposedRegistrationPipeline
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator


@pytest.fixture
def test_pair_illumination():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=15, seed=123)
    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=30.0, sun_azimuth_2=210.0, incidence_1=50.0, incidence_2=50.0,  # 180 deg illumination flip
        rotation_deg=3.0, translation_px=(5.0, -3.0)
    )
    return img1, img2, H_gt


@pytest.fixture
def test_pair_scale():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=15, seed=456)
    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=45.0, sun_azimuth_2=45.0, incidence_1=40.0, incidence_2=40.0,
        scale_ratio=4.0  # 4x scale disparity
    )
    return img1, img2, H_gt


def test_condition_analyzer(test_pair_illumination):
    img1, img2, H_gt = test_pair_illumination
    chars = ImagePairConditionAnalyzer.analyze(img1, img2)
    assert chars.is_illumination_inverted is True
    assert chars.recommended_feature_backend in ["STRUCTURAL_PHASE", "HYBRID_AMSR"]


def test_structural_detector(test_pair_illumination):
    img1, img2, H_gt = test_pair_illumination
    detector = StructuralFeatureDetector(nfeatures=300, suppress_shadow_edges=True)
    kps, desc = detector.detect_and_compute(img1)
    assert len(kps) > 10
    assert desc.shape[0] == len(kps)
    assert desc.shape[1] == 216


def test_scale_pyramid_matcher(test_pair_scale):
    img1, img2, H_gt = test_pair_scale
    detector = StructuralFeatureDetector(nfeatures=300)
    matcher = HierarchicalScalePyramidMatcher(detector=detector)
    res = matcher.match_scale_disparate_pair(img1, img2, estimated_scale_ratio=4.0)
    assert res.filtered_matches_count > 0


def test_proposed_pipeline_end_to_end(test_pair_illumination):
    img1, img2, H_gt = test_pair_illumination
    pipeline = ProposedRegistrationPipeline()
    out = pipeline.register(img1, img2, ground_truth_homography=H_gt)
    assert out.status == "SUCCESS"
    assert out.inlier_matches_count >= 4
    assert out.transformation_matrix.shape == (3, 3)
    assert out.metrics.rmse_inliers < 5.0
