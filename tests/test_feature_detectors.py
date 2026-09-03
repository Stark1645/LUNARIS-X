"""
Unit Tests for SIFT and RIFT Feature Detectors.
"""

import cv2
import numpy as np
import pytest
from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.log_gabor import LogGaborFilterBank
from src.features.rift.rift_detector import RIFTDetector
from src.dataset.synthetic_generator import LunarSurfaceGenerator


@pytest.fixture
def synthetic_lunar_image():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(256, 256, num_craters=15, seed=42)
    img = LunarSurfaceGenerator.render_photometric_shading(dem, sun_azimuth_deg=45.0, incidence_angle_deg=50.0)
    return img


def test_sift_detector(synthetic_lunar_image):
    detector = SIFTDetector(nfeatures=500)
    kps, descs = detector.detect_and_compute(synthetic_lunar_image)

    assert len(kps) > 10, "SIFT should detect features on cratered lunar terrain"
    assert descs.shape[0] == len(kps)
    assert descs.shape[1] == 128
    assert descs.dtype == np.float32


def test_log_gabor_filter_bank(synthetic_lunar_image):
    filter_bank = LogGaborFilterBank(n_scales=3, n_orientations=4)
    pc, mim, energy = filter_bank.compute_phase_congruency(synthetic_lunar_image)

    assert pc.shape == synthetic_lunar_image.shape
    assert mim.shape == synthetic_lunar_image.shape
    assert pc.min() >= 0.0 and pc.max() <= 1.0
    assert mim.max() < 4  # 4 orientations -> indices 0..3


def test_rift_detector(synthetic_lunar_image):
    detector = RIFTDetector(nfeatures=300, patch_size=36, n_scales=3, n_orientations=4, n_spatial_bins=4)
    kps, descs = detector.detect_and_compute(synthetic_lunar_image)

    assert len(kps) > 5, "RIFT should extract keypoints from Phase Congruency maps"
    assert descs.shape[0] == len(kps)
    # 4 bins x 4 bins x 4 orientations = 64
    assert descs.shape[1] == 64
    assert descs.dtype == np.float32
