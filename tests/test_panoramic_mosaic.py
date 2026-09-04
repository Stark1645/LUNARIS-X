"""
Tests for Expanded Panoramic Mosaic Stitcher.
Verifies that full spatial extents of Source and Reference images are preserved.
"""

import numpy as np
import pytest
import cv2

from src.visualization.renderer import RegistrationVisualizer
from src.registration.pipeline import LunarRegistrationPipeline, RegistrationOutput
from src.proposed.proposed_pipeline import ProposedRegistrationPipeline
from src.geometry.models import TransformationType
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator


def test_draw_panoramic_mosaic_identity():
    ref = np.full((100, 100), 100, dtype=np.uint8)
    src = np.full((100, 100), 200, dtype=np.uint8)
    H = np.eye(3, dtype=np.float64)

    mosaic = RegistrationVisualizer.draw_panoramic_mosaic(ref, src, H)
    assert mosaic is not None
    assert mosaic.ndim == 3
    assert mosaic.shape[0] >= 100
    assert mosaic.shape[1] >= 100


def test_draw_panoramic_mosaic_translation():
    # Source shifted right by 50px
    ref = np.zeros((100, 100), dtype=np.uint8)
    src = np.zeros((100, 100), dtype=np.uint8)
    
    # H maps src to ref, so translation [1 0 50; 0 1 0; 0 0 1]
    H = np.array([
        [1.0, 0.0, 50.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    mosaic = RegistrationVisualizer.draw_panoramic_mosaic(ref, src, H)
    assert mosaic is not None
    # Union width should be at least 150px
    assert mosaic.shape[1] >= 150
    assert mosaic.shape[0] >= 100


def test_panoramic_mosaic_in_pipeline():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=15, seed=123)
    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=45.0, sun_azimuth_2=47.0, incidence_1=35.0, incidence_2=35.0,
        rotation_deg=2.0, translation_px=(10.0, -5.0)
    )

    pipeline = LunarRegistrationPipeline(
        algorithm="SIFT_Baseline",
        transformation_model=TransformationType.HOMOGRAPHY,
        enable_subpixel=True,
        enable_spatial_filter=False
    )

    output = pipeline.register(
        source_image=img1,
        reference_image=img2,
        ground_truth_homography=H_gt,
        is_synthetic=True,
        dataset_category="SYNTHETIC_BENCHMARK"
    )

    assert output.status == "SUCCESS"
    assert output.panoramic_mosaic is not None
    assert output.panoramic_mosaic.ndim == 3
    # Verify standard outputs are completely unaffected
    assert output.warped_source_image is not None
    assert output.warped_source_image.shape == img2.shape
    assert output.alpha_overlay is not None
    assert output.checkerboard is not None
    assert output.difference_map is not None
