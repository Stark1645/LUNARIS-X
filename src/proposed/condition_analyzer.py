"""
Image Pair Condition & Characteristic Analyzer for Proposed Method (SIH26166).
Analyzes scale disparity, illumination difference, photometric correlation, and texture density
to select the optimal registration strategy dynamically without arbitrary hardcoding.
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ImagePairCharacteristics:
    """Quantitative characteristics of an image pair."""
    scale_ratio: float  # Estimated or metadata-derived scale disparity
    gradient_correlation: float  # Cross-correlation of gradient maps [-1, 1]
    intensity_correlation: float  # Cross-correlation of raw intensities [-1, 1]
    is_scale_disparate: bool  # True if scale ratio > 1.5x
    is_illumination_inverted: bool  # True if gradient or intensity correlation < 0.1
    is_low_texture: bool  # True if spatial standard deviation is low
    texture_entropy_src: float
    texture_entropy_ref: float
    recommended_feature_backend: str  # STRUCTURAL_PHASE | PYRAMID_SIFT | HYBRID_AMSR


class ImagePairConditionAnalyzer:
    """Inspects input pair characteristics to dynamically guide registration strategy."""

    @staticmethod
    def analyze(
        source_image: np.ndarray,
        reference_image: np.ndarray,
        gsd_source_m: Optional[float] = None,
        gsd_reference_m: Optional[float] = None
    ) -> ImagePairCharacteristics:
        """
        Computes scale disparity, photometric correlation, and texture entropy.
        """
        if len(source_image.shape) == 3:
            src_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
        else:
            src_gray = source_image

        if len(reference_image.shape) == 3:
            ref_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
        else:
            ref_gray = reference_image

        h_s, w_s = src_gray.shape
        h_r, w_r = ref_gray.shape

        # 1. Determine Scale Ratio
        if gsd_source_m is not None and gsd_reference_m is not None and gsd_source_m > 0 and gsd_reference_m > 0:
            scale_ratio = max(gsd_source_m / gsd_reference_m, gsd_reference_m / gsd_source_m)
        else:
            # Dimension ratio as proxy
            scale_ratio = max(float(w_r) / max(1.0, float(w_s)), float(w_s) / max(1.0, float(w_r)))

        is_scale_disparate = bool(scale_ratio > 1.5)

        # 2. Rescale to common resolution thumbnail for photometric analysis
        thumb_size = (256, 256)
        src_thumb = cv2.resize(src_gray, thumb_size, interpolation=cv2.INTER_AREA).astype(np.float32)
        ref_thumb = cv2.resize(ref_gray, thumb_size, interpolation=cv2.INTER_AREA).astype(np.float32)

        # Intensity Correlation
        src_flat = src_thumb.flatten() - np.mean(src_thumb)
        ref_flat = ref_thumb.flatten() - np.mean(ref_thumb)
        std_prod = (np.std(src_thumb) * np.std(ref_thumb)) + 1e-6
        intensity_corr = float(np.dot(src_flat, ref_flat) / (len(src_flat) * std_prod))

        # Gradient Correlation (Sobel magnitude cross-correlation)
        gx_s = cv2.Sobel(src_thumb, cv2.CV_32F, 1, 0, ksize=3)
        gy_s = cv2.Sobel(src_thumb, cv2.CV_32F, 0, 1, ksize=3)
        mag_s = np.sqrt(gx_s ** 2 + gy_s ** 2)

        gx_r = cv2.Sobel(ref_thumb, cv2.CV_32F, 1, 0, ksize=3)
        gy_r = cv2.Sobel(ref_thumb, cv2.CV_32F, 0, 1, ksize=3)
        mag_r = np.sqrt(gx_r ** 2 + gy_r ** 2)

        mag_s_flat = mag_s.flatten() - np.mean(mag_s)
        mag_r_flat = mag_r.flatten() - np.mean(mag_r)
        grad_std_prod = (np.std(mag_s) * np.std(mag_r)) + 1e-6
        grad_corr = float(np.dot(mag_s_flat, mag_r_flat) / (len(mag_s_flat) * grad_std_prod))

        is_illum_inverted = bool(intensity_corr < 0.15 or grad_corr < 0.20)

        # 3. Texture Entropy
        def entropy(img: np.ndarray) -> float:
            hist, _ = np.histogram(img.flatten(), bins=32, range=(0, 256), density=True)
            hist = hist[hist > 0]
            return float(-np.sum(hist * np.log2(hist)))

        ent_s = entropy(src_thumb.astype(np.uint8))
        ent_r = entropy(ref_thumb.astype(np.uint8))
        is_low_tex = bool(ent_s < 3.0 or ent_r < 3.0)

        # Strategy selection rule based directly on Phase 3 failure evidence:
        if is_scale_disparate:
            strategy = "HYBRID_AMSR"  # Must use hierarchical scale pyramid bridge
        elif is_illum_inverted:
            strategy = "STRUCTURAL_PHASE"  # Must use Phase Congruency to overcome shadow reversal
        else:
            strategy = "HYBRID_AMSR"  # Standard high-performance multi-scale structural matching

        return ImagePairCharacteristics(
            scale_ratio=scale_ratio,
            gradient_correlation=grad_corr,
            intensity_correlation=intensity_corr,
            is_scale_disparate=is_scale_disparate,
            is_illumination_inverted=is_illum_inverted,
            is_low_texture=is_low_tex,
            texture_entropy_src=ent_s,
            texture_entropy_ref=ent_r,
            recommended_feature_backend=strategy
        )
