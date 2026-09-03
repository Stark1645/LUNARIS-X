"""
Unit Tests for Multi-scale, Spatial Distribution Filter, and Sub-pixel Refiner.
"""

import numpy as np
import pytest
from src.multiscale.scale_bridge import MultiScaleBridge
from src.distribution.spatial_filter import SpatialDistributionFilter
from src.refinement.subpixel import SubPixelRefiner
from src.dataset.synthetic_generator import LunarSurfaceGenerator


def test_multiscale_bridge():
    bridge = MultiScaleBridge(max_octaves=3, scale_step=2.0)
    img = np.ones((256, 256), dtype=np.uint8) * 100
    pyramid = bridge.build_pyramid(img, target_scale_ratio=4.0)

    assert len(pyramid) >= 2
    assert pyramid[0][0].shape == (256, 256)
    assert pyramid[0][1] == 1.0


def test_spatial_distribution_gini_filter():
    # Clustered points in top-left corner
    clustered_pts = np.random.uniform(5, 40, size=(100, 2)).astype(np.float32)
    gini_clustered = SpatialDistributionFilter.compute_gini_coefficient(clustered_pts, image_shape=(256, 256), grid_size=4)

    # Uniform points across canvas
    uniform_pts = np.random.uniform(5, 250, size=(100, 2)).astype(np.float32)
    gini_uniform = SpatialDistributionFilter.compute_gini_coefficient(uniform_pts, image_shape=(256, 256), grid_size=4)

    assert gini_clustered > gini_uniform, "Clustered points must have higher Gini coefficient than uniform points"

    # Test filtering
    filter_mod = SpatialDistributionFilter(grid_size=4, max_points_per_bin=10)
    filt_src, filt_ref, stats = filter_mod.filter_inliers(clustered_pts, clustered_pts, image_shape=(256, 256))
    assert len(filt_src) <= 100
    assert "filtered_gini" in stats


def test_subpixel_refiner():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=10, seed=42)
    img = LunarSurfaceGenerator.render_photometric_shading(dem, 45.0, 50.0)

    # Simulated integer match points
    src_pts = np.array([[100.0, 100.0], [150.0, 150.0], [80.0, 120.0]], dtype=np.float32)
    ref_pts = src_pts.copy()

    refiner = SubPixelRefiner(patch_radius=7, search_radius=3)
    refined_ref, disps, stats = refiner.refine_points(img, img, src_pts, ref_pts)

    assert refined_ref.shape == ref_pts.shape
    assert stats["total_points"] == 3
