"""
Image Preprocessing & Normalization Module for Lunar Imagery (SIH26166).
Handles 8-bit/16-bit radiometric stretching, percentile clipping, denoising, and valid pixel masking.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any


class LunarPreprocessor:
    """Preprocesses optical and lunar raster imagery for robust feature extraction."""

    @staticmethod
    def normalize_radiometry(
        image: np.ndarray,
        lower_percentile: float = 2.0,
        upper_percentile: float = 98.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Normalizes dynamic range via percentile stretching.
        Handles both native 16-bit (PDS4 raw) and 8-bit images.
        Returns normalized 8-bit [0, 255] grayscale image and stretch metadata.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or invalid.")

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        img_float = gray.astype(np.float32)

        # Ignore zero/nodata values when computing percentiles if valid pixels exist
        valid_mask = img_float > 0
        if np.sum(valid_mask) > 100:
            valid_pixels = img_float[valid_mask]
        else:
            valid_pixels = img_float.flatten()

        p_low = float(np.percentile(valid_pixels, lower_percentile))
        p_high = float(np.percentile(valid_pixels, upper_percentile))

        if p_high - p_low < 1e-5:
            # Flat image fallback
            norm = np.zeros_like(img_float, dtype=np.uint8)
        else:
            clipped = np.clip(img_float, p_low, p_high)
            norm = ((clipped - p_low) / (p_high - p_low) * 255.0).astype(np.uint8)

        stats = {
            "original_dtype": str(image.dtype),
            "original_min": float(gray.min()),
            "original_max": float(gray.max()),
            "original_mean": float(gray.mean()),
            "original_std": float(gray.std()),
            "p_low": p_low,
            "p_high": p_high,
            "width": int(gray.shape[1]),
            "height": int(gray.shape[0])
        }

        return norm, stats

    @staticmethod
    def create_valid_mask(
        image: np.ndarray,
        nodata_value: float = 0.0,
        shadow_threshold: Optional[int] = None
    ) -> np.ndarray:
        """
        Creates a binary mask (255 = valid, 0 = invalid/shadow) to exclude non-informative regions.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        mask = np.ones_like(gray, dtype=np.uint8) * 255

        # Nodata mask
        mask[gray == nodata_value] = 0

        # Optional harsh shadow threshold mask (for permanently shadowed lunar regions)
        if shadow_threshold is not None:
            mask[gray <= shadow_threshold] = 0

        return mask

    @staticmethod
    def denoise_image(
        image: np.ndarray,
        method: str = "gaussian",
        kernel_size: int = 3
    ) -> np.ndarray:
        """
        Applies gentle denoising while preserving morphological edges (crater rims).
        """
        if method == "gaussian":
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0.8)
        elif method == "median":
            return cv2.medianBlur(image, kernel_size)
        elif method == "bilateral":
            return cv2.bilateralFilter(image, d=5, sigmaColor=25, sigmaSpace=25)
        else:
            return image
