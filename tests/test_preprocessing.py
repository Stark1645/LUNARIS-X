"""
Unit Tests for Phase 1 Lunar Preprocessor.
"""

import numpy as np
import pytest
from src.preprocessing.normalizer import LunarPreprocessor


def test_radiometric_normalization():
    # 16-bit simulated data
    raw_16bit = np.random.randint(500, 35000, size=(128, 128), dtype=np.uint16)
    norm, stats = LunarPreprocessor.normalize_radiometry(raw_16bit)

    assert norm.shape == (128, 128)
    assert norm.dtype == np.uint8
    assert norm.max() <= 255
    assert norm.min() >= 0
    assert stats["original_dtype"] == "uint16"
    assert stats["p_high"] > stats["p_low"]


def test_valid_mask_creation():
    img = np.ones((100, 100), dtype=np.uint8) * 128
    img[0:10, 0:10] = 0  # Nodata block
    img[20:30, 20:30] = 5  # Shadow block

    mask = LunarPreprocessor.create_valid_mask(img, nodata_value=0, shadow_threshold=10)
    assert mask.shape == (100, 100)
    assert mask[5, 5] == 0  # Nodata masked
    assert mask[25, 25] == 0  # Shadow masked
    assert mask[50, 50] == 255  # Valid


def test_denoise_image():
    noisy = (np.random.rand(64, 64) * 255).astype(np.uint8)
    denoised = LunarPreprocessor.denoise_image(noisy, method="gaussian")
    assert denoised.shape == (64, 64)
    assert denoised.dtype == np.uint8
