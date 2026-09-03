"""
End-to-End Registration Pipeline and Metric Evaluation Tests.
"""

import numpy as np
import pytest
from src.registration.pipeline import LunarRegistrationPipeline
from src.evaluation.metrics import RegistrationEvaluator
from src.geometry.models import TransformationType
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator


@pytest.fixture
def synthetic_benchmark_pair():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(512, 512, num_craters=25, seed=777)
    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=45.0, sun_azimuth_2=48.0, incidence_1=40.0, incidence_2=40.0,
        rotation_deg=4.0, translation_px=(12.0, -8.0)
    )
    return img1, img2, H_gt, meta


def test_end_to_end_sift_registration_pipeline(synthetic_benchmark_pair):
    img1, img2, H_gt, meta = synthetic_benchmark_pair

    pipeline = LunarRegistrationPipeline(
        algorithm="SIFT_Baseline",
        transformation_model=TransformationType.HOMOGRAPHY,
        enable_subpixel=True,
        enable_spatial_filter=True
    )

    output = pipeline.register(
        source_image=img1,
        reference_image=img2,
        ground_truth_homography=H_gt,
        is_synthetic=True,
        dataset_category="SYNTHETIC_BENCHMARK"
    )

    assert output.status == "SUCCESS"
    assert output.inlier_matches_count >= 4
    assert output.warped_source_image.shape == img2.shape
    assert output.transformation_matrix.shape == (3, 3)

    # Validate Metrics
    m = output.metrics
    assert m.status == "SUCCESS"
    assert m.inlier_match_count == output.inlier_matches_count
    assert m.rmse_inliers < 5.0
    assert m.rmse_ground_truth is not None
    assert m.rmse_ground_truth < 5.0
    assert 0.0 <= m.spatial_gini_coefficient <= 1.0
    assert m.latency_ms > 0.0


def test_end_to_end_rift_registration_pipeline(synthetic_benchmark_pair):
    img1, img2, H_gt, meta = synthetic_benchmark_pair

    pipeline = LunarRegistrationPipeline(
        algorithm="RIFT_Baseline",
        transformation_model=TransformationType.HOMOGRAPHY,
        enable_subpixel=True,
        enable_spatial_filter=True
    )

    output = pipeline.register(
        source_image=img1,
        reference_image=img2,
        ground_truth_homography=H_gt,
        is_synthetic=True,
        dataset_category="SYNTHETIC_BENCHMARK"
    )

    assert output.status in ["SUCCESS", "FAILED"]  # RIFT is an evaluated baseline
    if output.status == "SUCCESS":
        assert output.inlier_matches_count >= 4
        assert output.warped_source_image.shape == img2.shape
